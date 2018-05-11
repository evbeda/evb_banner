""" This are the methods that supports the behaviour of the views """
import calendar
import json
import requests
import threading
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Event,
    EventDesign,
    UserWebhook,
)
from social_django.models import UserSocialAuth
from eventbrite import Eventbrite
import pyrebase


DEFAULT_EVENT_DESIGN = 1


def get_events_data(events, banner):

    """
    This method is where the data of the banner display will be created
    """

    for event in events:
        event = replace_data(event)
        yield {
            'data_x': event.sort * banner.design.data_x,
            'data_y': event.sort * banner.design.data_y,
            'data_z': event.sort * banner.design.data_z,
            'data_rotate': banner.design.data_rotate,
            'data_scale': banner.design.data_scale,
            'event': event,
        }


def replace_data(event):

    """
    Here we replace the pseudovariables of the design of the
    event passed as argument for the real values of those variables
    """

    if event.custom_title:
        event.design.html = unicode(event.design.html).replace(
            '|| title ||', unicode(event.custom_title)
        )
    else:
        event.design.html = unicode(event.design.html).replace(
            '|| title ||', unicode(event.title)
        )

    if event.custom_description:
        event.design.html = unicode(event.design.html).replace(
            '|| description ||', unicode(event.custom_description)
        )
    else:
        event.design.html = unicode(event.design.html).replace(
            '|| description ||', unicode(event.description)
        )

    if event.custom_logo:
        event.design.html = unicode(event.design.html).replace(
            '|| logo ||', unicode(event.custom_logo)
        )
    else:
        event.design.html = unicode(event.design.html).replace(
            '|| logo ||', unicode(event.logo)
        )

    event.design.html = unicode(event.design.html).replace(
        '|| startdate_month ||',
        calendar.month_name[event.start.month][:3].upper() + '.'
    )

    event.design.html = unicode(event.design.html).replace(
        '|| startdate_day ||', unicode(event.start.day)
    )

    event.design.html = unicode(event.design.html).replace(
        '|| evb_url ||', unicode(event.evb_url)
    )

    event.design.html = unicode(event.design.html).replace(
        '|| id ||', unicode(event.id)
    )

    return event


def img_upload(logo, banner, event):

    """
    Here is the upload of an image
    (or any file really) to the firebase service
    """

    firebase = pyrebase.initialize_app(settings.FIREBASECONFIG)
    storage = firebase.storage()
    storage.child(
        'custom_logos/' + str(banner) + '/' + str(event) + '-' + logo.name
    ).put(logo)
    return storage.child(
        'custom_logos/' + str(banner) + '/' + str(event) + '-' + logo.name
    ).get_url(1)


def get_auth_token(user):

    """
    This method will receive an user and
    return its repesctive social_auth token
    """

    try:
        token = user.social_auth.get(
            provider='eventbrite'
        ).access_token
    except UserSocialAuth.DoesNotExist:
        print 'UserSocialAuth does not exists!'
    return token


def get_api_events(token):

    """
    Get events from the user of the token from the api
    """

    eventbrite = Eventbrite(token)
    return eventbrite.get('/users/me/events/')['events']


def create_webhook(user):

    """
    Method to create a webhook that listens to
    the publications of events of an user
    """

    has_webhook = UserWebhook.objects.filter(user=user).exists()
    if has_webhook:
        webhook = UserWebhook.objects.get(user=user)
        response = webhook.webhook_id
    else:
        token = get_auth_token(user)

        data = {
            'endpoint_url': 'https://evbbanner.herokuapp.com/banner/event/add',
            'actions': 'event.published',
        }
        try:
            response = Eventbrite(token).post('/webhooks/', data)[u'id']
            UserWebhook.objects.create(webhook_id=response, user=user)
        except Exception as ex:
            print ex.message
    return response


@csrf_exempt
def accept_webhook(request):
    threading.Thread(target=process_webhook, args=(request.body,)).start()
    return HttpResponse()


def process_webhook(body):
    config_data = json.loads(body)
    user_id = config_data['config']['user_id']
    social_user = UserSocialAuth.objects.get(
        uid=user_id
    )
    access_token = social_user.extra_data['access_token']
    data = requests.get(
        json.loads(
            body
        )['api_url'] +
        '?token=' +
        access_token
    )
    save_event(data.json())


def save_event(data):
    start = data['start']['local'].replace('T', ' ')
    end = data['end']['local'].replace('T', ' ')
    if data['logo'] is not None:
        logo = data['logo']['url']
    else:
        logo = 'none'
    edesign = EventDesign.objects.get(id=DEFAULT_EVENT_DESIGN)
    event = Event(
        evb_id=data['id'],
        evb_url=data['url'],
        title=data['name']['text'],
        description=data['description']['text'],
        start=start,
        end=end,
        logo=logo,
        organizer=data['organizer_id'],
        design=edesign,
    )
    event.save()
