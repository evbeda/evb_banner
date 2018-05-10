# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from social_django.models import UserSocialAuth
from unittest import skip
from mock import (
    MagicMock,
    patch,
)
from .factories import (
    BannerDesignFactory,
    BannerFactory,
    EventFactory,
    UserFactory,
)
from .models import (
    Banner,
    BannerDesign,
    Event,
    EventDesign,
)
from .views import (
    BannerView,
    BannerNewEventsSelectedCreateView,
    EditEventDesignView,
)
from .forms import (
    BannerForm,
    EventDesignForm,
    EventForm,
)
from .utils import (
    get_api_events,
    replace_data,
)


class TestBase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username='testuser',
            password='12345',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        self.user.set_password('hello')
        self.user.save()
        self.auth = UserSocialAuth.objects.create(
            user=self.user, provider='eventbrite', uid="249759038146"
        )
        login = self.client.login(username='testuser', password='hello')
        return login


class BannerViewTest(TestBase):

    def setUp(self):
        super(BannerViewTest, self).setUp()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_no_banners(self):
        response = self.client.get('/')
        self.assertContains(response, 'No banners yet!')


class BannerDesignTest(TestBase):

    def test_banner_design_creation(self):
        w = BannerDesignFactory()
        self.assertTrue(isinstance(w, BannerDesign))
        banner_design_list = BannerDesign.objects.all()
        banner_design = banner_design_list[len(banner_design_list) - 1]
        self.assertEqual(banner_design.name, w.name)


class BannerDesignViewTest(TestBase):

    def setUp(self):
        super(BannerDesignViewTest, self).setUp()
        self.get_auth_token_patcher = patch(
            'banner.utils.get_auth_token',
            return_value=123456,
        )
        self.mock_get_auth_token = self.get_auth_token_patcher.start()
        self.eb_post_patcher = patch(
            'banner.utils.Eventbrite.post',
            return_value={
                'id': 123456,
            },
        )
        self.mock_get_auth_token = self.eb_post_patcher.start()
        self.banner = BannerFactory()

    def test_banner_design_view(self):
        response = self.client.get(
            '/banner/' + str(self.banner.id) + '/preview/'
        )
        self.assertEqual(response.status_code, 200)

    def test_events_inside_banner(self):
        event1 = EventFactory.build()
        event1.banner = self.banner
        event1.save()

        event2 = EventFactory.build()
        event2.banner = self.banner
        event2.save()

        response = self.client.get(
            '/banner/' + str(self.banner.id) + '/preview/'
        )
        self.assertContains(response, 'event-' + str(event1.id))
        self.assertContains(response, 'event-' + str(event2.id))

    def tearDown(self):
        self.get_auth_token_patcher.stop()
        self.eb_post_patcher.stop()


@patch(
    'banner.utils.get_auth_token',
    return_value=123456,
)
@patch(
    'banner.utils.Eventbrite.post',
    return_value={
        'id': 123456,
    },
)
class BannerTest(TestBase):

    def test_banner_creation(self, mock_eb_post, mock_get_auth_token):
        w = BannerFactory()
        self.assertTrue(isinstance(w, Banner))
        banner_list = Banner.objects.all()
        banner = banner_list[len(banner_list) - 1]
        self.assertEqual(banner.title, w.title)


class BannerDetailViewTest(TestBase):

    def setUp(self):
        super(BannerDetailViewTest, self).setUp()
        self.get_auth_token_patcher = patch(
            'banner.utils.get_auth_token',
            return_value=123456,
        )
        self.mock_get_auth_token = self.get_auth_token_patcher.start()
        self.eb_post_patcher = patch(
            'banner.utils.Eventbrite.post',
            return_value={
                'id': 123456,
            },
        )
        self.mock_get_auth_token = self.eb_post_patcher.start()
        self.banner = BannerFactory()

    def test_banner_detail_view(self):
        response = self.client.get(self.banner.get_absolute_url)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.get_auth_token_patcher.stop()
        self.eb_post_patcher.stop()


@patch(
    'banner.utils.get_auth_token',
    return_value=123456,
)
@patch(
    'banner.utils.Eventbrite.post',
    return_value={
        'id': 123456,
    },
)
class EventTest(TestBase):

    def test_event_creation(self, mock_eb_post, mock_get_auth_token):
        w = EventFactory()
        self.assertTrue(isinstance(w, Event))
        event_list = Event.objects.all()
        event = event_list[len(event_list) - 1]
        self.assertEqual(event.title, w.title)


class EventViewTest(TestBase):

    def setUp(self):
        super(EventViewTest, self).setUp()

    @patch('banner.views.Eventbrite.get')
    def test_events_page_status_code(self, mock_eventbrite_get):
        response = self.client.get('/banner/new/')
        self.assertEqual(response.status_code, 200)

    @patch('banner.views.Eventbrite.get')
    def test_call_with_correct_parameters(self, mock_eventbrite_get):
        self.client.get('/banner/new/')
        self.assertEquals(
            mock_eventbrite_get.call_args_list[0][0][0],
            '/users/me/events/',
        )

    @patch('banner.views.Eventbrite.get')
    def test_call_once_api(self, mock_eventbrite_get):
        self.client.get('/banner/new/')
        mock_eventbrite_get.assert_called_once()


class EventDesignFormTest(TestBase):

    def setUp(self):
        super(EventDesignFormTest, self).setUp()

    def test_edit_design_form_valid(self):
        form_data = {
            u'Edit': [u'Submit'],
            u'csrfmiddlewaretoken': [u'asd'],
            u'html': [
                u'<div class="panel-event">\r\n<div'
                'class="panel-event-header row">\r\n<div class="col-md-8'
                'event-logo">'
                '<em><strong><img class="img-rounded"'
                'src="|| logo ||" /></strong></em></div>\r\n\r\n<div'
                'class="col-md-4'
                'info-panel" style="padding-left:0!important">\r\n<div'
                'class="event-start-date-month"><em><strong>|| startdate_month'
                '||</strong></em></div>\r\n\r\n<div'
                'class="event-start-date-day"><em><strong>|| startdate_day'
                '||</strong></em></div>\r\n\r\n<div'
                'class="event-title"><em><strong>|| title'
                '||</strong></em></div>\r\n</div>\r\n</div>\r\n\r\n<div'
                'class="panel-event-body">\r\n<div class="box row">\r\n<div'
                'class="col-md-8" style="padding:0 !important">\r\n<div'
                'class="event-description"><em><strong>|| description'
                '||</strong></em></div>\r\n</div>\r\n\r\n<div class="col-md-4"'
                '>\r\n<div class="event-qr" id="qrcode">&nbsp;</div>'
                '\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n'
            ]
        }
        form = EventDesignForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_edit_design_form_invalid(self):
        form_data = {
            u'Edit': [u'Submit'],
            u'csrfmiddlewaretoken': [u'asd'],
            u'html': []
        }
        form = EventDesignForm(data=form_data)
        self.assertFalse(form.is_valid())


class EditEventDesignViewTest(TestBase):

    def setUp(self):
        super(EditEventDesignViewTest, self).setUp()
        self.get_auth_token_patcher = patch(
            'banner.utils.get_auth_token',
            return_value=123456,
        )
        self.mock_get_auth_token = self.get_auth_token_patcher.start()
        self.eb_post_patcher = patch(
            'banner.utils.Eventbrite.post',
            return_value={
                'id': 123456,
            },
        )
        self.mock_get_auth_token = self.eb_post_patcher.start()
        self.banner = BannerFactory()
        self.event = EventFactory()

    def test_event_design_form_post_valid(self):

        form_data = {
            u'Edit': [u'Submit'],
            u'csrfmiddlewaretoken': [u'asd'],
            u'html': [
                u'<div>\r\n<div>\r\n<div>'
                '<em><strong><img '
                'src="|| logo ||" /></strong></em></div>\r\n\r\n<div>\r\n<div>'
                '<em><strong>|| startdate_month'
                '||</strong></em></div>\r\n\r\n<div '
                '><em><strong>|| startdate_day'
                '||</strong></em></div>\r\n\r\n<div>'
                '<em><strong>|| title'
                '||</strong></em></div>\r\n</div>\r\n</div>\r\n\r\n<div>'
                '\r\n<div>\r\n<div '
                'style="padding:0 !important">\r\n<div>'
                '<em><strong>|| description'
                '||</strong></em></div>\r\n</div>\r\n\r\n<div>'
                '\r\n<div id="qrcode">&nbsp;</div>'
                '\r\n</div>\r\n</div>\r\n</div>\r\n</div>'
            ]
        }

        response = self.client.post("/banner/{}/event/{}/".format(
            self.banner.id,
            self.event.id,
        ), form_data, follow=True)

        self.assertEquals(200, response.status_code)

        saved_event = Event.objects.select_related(
            'design',
        ).get(
            pk=self.event.id,
        )
        self.assertEquals(self.event, saved_event)
        self.assertEquals(form_data['html'][0], saved_event.design.html)

    def test_form_post_form_invalid(self):

        form_data = {
            u'Edit': [u'Submit'],
            u'csrfmiddlewaretoken': [u'asd'],
            u'html': []
        }

        response = self.client.post("/banner/{}/event/{}/".format(
            self.banner.id,
            self.event.id,
        ), form_data, follow=True)

        self.assertEquals(200, response.status_code)
        self.assertFormError(response, 'form', None, "Can't submit it empty!")

    def test_context_data(self):

        response = self.client.get("/banner/{}/event/{}/".format(
            self.banner.id,
            self.event.id,
        ), follow=True)

        self.assertTrue(
            isinstance(response.context_data['form'], EventDesignForm)
        )
        self.assertTrue(
            isinstance(response.context_data['view'], EditEventDesignView)
        )
        self.assertEquals(self.event, response.context_data['event'])
        self.assertEquals(200, response.status_code)

    def test_form_initial_data_default(self):

        default_event_design = EventDesign.objects.get(id=1)

        response = self.client.get("/banner/{}/event/{}/".format(
            self.banner.id,
            self.event.id,
        ), follow=True)

        self.assertEquals(
            response.context_data['form'].initial['html'],
            default_event_design.html
        )

    def test_form_initial_data(self):

        self.event.design = EventDesign.objects.create(
            user=self.user,
            html='asd',
        )
        self.event.save()
        response = self.client.get("/banner/{}/event/{}/".format(
            self.banner.id,
            self.event.id,
        ), follow=True)

        self.assertEquals(
            response.context_data['form'].initial['html'],
            self.event.design.html
        )

    def tearDown(self):
        self.get_auth_token_patcher.stop()
        self.eb_post_patcher.stop()


@patch(
    'banner.views.Eventbrite.get',
    return_value={
        'events': [
            {
                "name": {
                    "text": "Evento de prueba",
                    "html": "Evento de prueba"
                },
                "description": {
                    "text": "evento de prueba",
                    "html": "<P>evento de prueba<\/P>"
                },
                "id": "40741881063",
                "url": "https://www.eventbrite.com.ar/e/evento-de-prueba-tickets-40741881063",
                "start": {
                    "timezone": u'America/Argentina/Mendoza',
                    "local": u'2018-04-29T22:00:00',
                    "utc": u'2018-01-04T22:00:00Z'
                },
                "end": {
                    "timezone": 'America/Argentina/Mendoza',
                    "local": u'2018-04-29T23:00:00',
                    "utc": u'2018-01-05T01:00:00Z'
                },
                "organization_id": "236776874706",
                "created": "2017-11-25T19:13:18Z",
                "changed": "2018-01-05T05:23:49Z",
                "capacity": 20,
                "capacity_is_custom": False,
                "status": "completed",
                "currency": "ARS",
                "listed": False,
                "shareable": True,
                "invite_only": False,
                "online_event": False,
                "show_remaining": True,
                "tx_time_limit": 480,
                "hide_start_date": False,
                "hide_end_date": False,
                "locale": "es_AR",
                "is_locked": False,
                "privacy_setting": "unlocked",
                "is_series": False,
                "is_series_parent": False,
                "is_reserved_seating": False,
                "source": "create_2.0",
                "is_free": True,
                "version": "3.0.0",
                "logo_id": "38099252",
                "organizer_id": "15852777053",
                "venue_id": "22336362",
                "category_id": "102",
                "subcategory_id": None,
                "format_id": "100",
                "resource_uri": "https://www.eventbriteapi.com/v3/events/40741881063/",
                "logo": {
                    "crop_mask": {
                        "top_left": {
                            "x": 196,
                            "y": 184
                        },
                        "width": 464,
                        "height": 232
                    },
                    "original": {
                        "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F38099252%2F236776874706%2F1%2Foriginal.jpg?auto=compress&s=109e5624c733ef88316094935138451f",
                        "width": 835,
                        "height": 470
                    },
                    "id": 38099252,
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F38099252%2F236776874706%2F1%2Foriginal.jpg?h=200&w=450&auto=compress&rect=196%2C184%2C464%2C232&s=dd415facae0a66bcd1ce9178aac57f68",
                    "aspect_ratio": "2",
                    "edge_color": "#ffffff",
                    "edge_color_set": True
                }
            }
        ]
    }
)
class BannerNewEventsSelectedCreateViewTest(TestBase):

    def setUp(self):
        super(BannerNewEventsSelectedCreateViewTest, self).setUp()
        self.get_auth_token_patcher = patch(
            'banner.utils.get_auth_token',
            return_value=123456,
        )
        self.mock_get_auth_token = self.get_auth_token_patcher.start()
        self.eb_post_patcher = patch(
            'banner.utils.Eventbrite.post',
            return_value={
                'id': 123456,
            },
        )
        self.mock_get_auth_token = self.eb_post_patcher.start()

    def test_banner_new_form_get(self, mock_get_api_events):

        response = self.client.get("/banner/new/", follow=True)
        self.assertEquals(200, response.status_code)

    def test_banner_new_form_post_valid(self, mock_get_api_events):

        form_data = {
            u'Events Selected': [u''],
            u'csrfmiddlewaretoken': [u'asd'],
            u'description': [u'Description for custom banner'],
            u'form-0-custom_description': [u'A rugby match'],
            u'form-0-custom_title': [u'Wallabies vs pumas'],
            u'form-0-description': [u'descripcion'],
            u'form-0-end': [u'2018-04-29 22:00:00'],
            u'form-0-evb_id': [u'44384359815'],
            u'form-0-evb_url': [u'https://www.eventbrite.com/'],
            u'form-0-logo': [u'none'],
            u'form-0-organizer': [u'15828411681'],
            u'form-0-selection': [u'on'],
            u'form-0-start': [u'2018-04-29 19:00:00'],
            u'form-0-title': [u'New event'],
            u'form-1-custom_description': [u''],
            u'form-1-custom_logo': [u''],
            u'form-1-custom_title': [u''],
            u'form-1-description': [u'This is one event!'],
            u'form-1-end': [u'2021-11-27 11:30:00'],
            u'form-1-evb_id': [u'40188254150'],
            u'form-1-evb_url': [u'https://www.eventbrite.com/'],
            u'form-1-logo': [u'https://img.evbuc.com/'],
            u'form-1-organizer': [u'15828411681'],
            u'form-1-selection': [u'on'],
            u'form-1-start': [u'2019-11-27 21:30:00'],
            u'form-1-title': [u"Fernando's interview"],
            u'form-INITIAL_FORMS': [u'0', u'0'],
            u'form-MAX_NUM_FORMS': [u'1000', u'1000'],
            u'form-MIN_NUM_FORMS': [u'0', u'0'],
            u'form-TOTAL_FORMS': [u'2', u'2'],
            u'title': [u'CUSTOM BANNER'],
        }

        response = self.client.post("/banner/new/".format(
        ), form_data, follow=True)

        self.assertEquals(200, response.status_code)

        saved_banner = Banner.objects.latest('changed',)
        saved_events = Event.objects.filter(banner=saved_banner)

        default_event_design = EventDesign.objects.get(id=1)
        for saved_event in saved_events:
            self.assertTrue(
                isinstance(saved_event, Event)
            )
            self.assertEquals(default_event_design, saved_event.design)

    def test_form_post_form_invalid(self, mock_get_api_events):

        form_data = {
            u'Events Selected': [u''],
            u'csrfmiddlewaretoken': [u'asd'],
            u'description': [u'Description for custom banner'],
            u'form-INITIAL_FORMS': [u'0', u'0'],
            u'form-MAX_NUM_FORMS': [u'1000', u'1000'],
            u'form-MIN_NUM_FORMS': [u'0', u'0'],
            u'form-TOTAL_FORMS': [u'0', u'0'],
            u'title': [u'CUSTOM BANNER'],
        }

        response = self.client.post("/banner/new/".format(
        ), form_data, follow=True)

        self.assertEquals(200, response.status_code)
        self.assertFormError(response, 'form', None, "No events selected")

    def test_edit_banner_deleting_event(self, mock_get_api_events):
        form_data = {
            u'Events Selected': [u''],
            u'csrfmiddlewaretoken': [u'asd'],
            u'description': [u'Description for custom banner'],
            u'form-0-custom_description': [u'A rugby match'],
            u'form-0-custom_title': [u'Wallabies vs pumas'],
            u'form-0-description': [u'descripcion'],
            u'form-0-end': [u'2018-04-29 22:00:00'],
            u'form-0-evb_id': [u'44384359815'],
            u'form-0-evb_url': [u'https://www.eventbrite.com/'],
            u'form-0-logo': [u'none'],
            u'form-0-organizer': [u'15828411681'],
            u'form-0-selection': [u'on'],
            u'form-0-start': [u'2018-04-29 19:00:00'],
            u'form-0-title': [u'New event'],
            u'form-1-custom_description': [u''],
            u'form-1-custom_logo': [u''],
            u'form-1-custom_title': [u''],
            u'form-1-description': [u'This is one event!'],
            u'form-1-end': [u'2021-11-27 11:30:00'],
            u'form-1-evb_id': [u'40188254150'],
            u'form-1-evb_url': [u'https://www.eventbrite.com/'],
            u'form-1-logo': [u'https://img.evbuc.com/'],
            u'form-1-organizer': [u'15828411681'],
            u'form-1-selection': [u'on'],
            u'form-1-start': [u'2019-11-27 21:30:00'],
            u'form-1-title': [u"Fernando's interview"],
            u'form-INITIAL_FORMS': [u'0', u'0'],
            u'form-MAX_NUM_FORMS': [u'1000', u'1000'],
            u'form-MIN_NUM_FORMS': [u'0', u'0'],
            u'form-TOTAL_FORMS': [u'2', u'2'],
            u'title': [u'CUSTOM BANNER'],
        }

        self.client.post("/banner/new/".format(
        ), form_data, follow=True)

        saved_banner = Banner.objects.latest('changed',)
        saved_events = Event.objects.filter(banner=saved_banner)
        self.assertEqual(len(saved_events), 2)

        form_data_edit = {
            u'Events Selected': [u''],
            u'csrfmiddlewaretoken': [u'asd'],
            u'description': [u'Description for custom banner'],
            u'form-0-custom_description': [u'A rugby match edited'],
            u'form-0-custom_title': [u'Wallabies vs pumas edited'],
            u'form-0-description': [u'descripcion'],
            u'form-0-end': [u'2018-04-29 22:00:00'],
            u'form-0-evb_id': [u'44384359815'],
            u'form-0-evb_url': [u'https://www.eventbrite.com/'],
            u'form-0-logo': [u'none'],
            u'form-0-organizer': [u'15828411681'],
            u'form-0-selection': [u'on'],
            u'form-0-start': [u'2018-04-29 19:00:00'],
            u'form-0-title': [u'New event'],
            u'form-INITIAL_FORMS': [u'0', u'0'],
            u'form-MAX_NUM_FORMS': [u'1000', u'1000'],
            u'form-MIN_NUM_FORMS': [u'0', u'0'],
            u'form-TOTAL_FORMS': [u'1', u'1'],
            u'title': [u'CUSTOM BANNER'],
        }
        self.client.post("/banner/{}/banner_update/".format(
            saved_banner.id
        ), form_data_edit, follow=True)
        edited_events = Event.objects.filter(banner=saved_banner)
        self.assertEqual(len(edited_events), 1)
        self.assertEqual(
            edited_events[0].custom_title, 'Wallabies vs pumas edited',
        )
        self.assertEqual(
            edited_events[0].custom_description, 'A rugby match edited',
        )

    def test_edit_banner_adding_event(self, mock_get_api_events):
        form_data = {
            u'Events Selected': [u''],
            u'csrfmiddlewaretoken': [u'asd'],
            u'description': [u'Description for custom banner'],
            u'form-0-custom_description': [u'A rugby match'],
            u'form-0-custom_title': [u'Wallabies vs pumas'],
            u'form-0-description': [u'descripcion'],
            u'form-0-end': [u'2018-04-29 22:00:00'],
            u'form-0-evb_id': [u'44384359815'],
            u'form-0-evb_url': [u'https://www.eventbrite.com/'],
            u'form-0-logo': [u'none'],
            u'form-0-organizer': [u'15828411681'],
            u'form-0-selection': [u'on'],
            u'form-0-start': [u'2018-04-29 19:00:00'],
            u'form-0-title': [u'New event'],
            u'form-INITIAL_FORMS': [u'0', u'0'],
            u'form-MAX_NUM_FORMS': [u'1000', u'1000'],
            u'form-MIN_NUM_FORMS': [u'0', u'0'],
            u'form-TOTAL_FORMS': [u'1', u'1'],
            u'title': [u'CUSTOM BANNER'],
        }
        self.client.post("/banner/new/".format(
        ), form_data, follow=True)
        saved_banner = Banner.objects.latest('changed',)
        saved_events = Event.objects.filter(banner=saved_banner)
        self.assertEqual(len(saved_events), 1)

        form_data_edit = {
            u'Events Selected': [u''],
            u'csrfmiddlewaretoken': [u'asd'],
            u'description': [u'Description for custom banner'],
            u'form-0-custom_description': [u'A rugby match edited'],
            u'form-0-custom_title': [u'Wallabies vs pumas edited'],
            u'form-0-description': [u'descripcion'],
            u'form-0-end': [u'2018-04-29 22:00:00'],
            u'form-0-evb_id': [u'44384359815'],
            u'form-0-evb_url': [u'https://www.eventbrite.com/'],
            u'form-0-logo': [u'none'],
            u'form-0-organizer': [u'15828411681'],
            u'form-0-selection': [u'on'],
            u'form-0-start': [u'2018-04-29 19:00:00'],
            u'form-0-title': [u'New event'],
            u'form-1-custom_description': [u''],
            u'form-1-custom_logo': [u''],
            u'form-1-custom_title': [u''],
            u'form-1-description': [u'This is one event!'],
            u'form-1-end': [u'2021-11-27 11:30:00'],
            u'form-1-evb_id': [u'40188254150'],
            u'form-1-evb_url': [u'https://www.eventbrite.com/'],
            u'form-1-logo': [u'https://img.evbuc.com/'],
            u'form-1-organizer': [u'15828411681'],
            u'form-1-selection': [u'on'],
            u'form-1-start': [u'2019-11-27 21:30:00'],
            u'form-1-title': [u"Fernando's interview"],
            u'form-INITIAL_FORMS': [u'0', u'0'],
            u'form-MAX_NUM_FORMS': [u'1000', u'1000'],
            u'form-MIN_NUM_FORMS': [u'0', u'0'],
            u'form-TOTAL_FORMS': [u'2', u'2'],
            u'title': [u'CUSTOM BANNER'],
        }
        self.client.post("/banner/{}/banner_update/".format(
            saved_banner.id
        ), form_data_edit, follow=True)
        edited_events = Event.objects.filter(banner=saved_banner)
        self.assertEqual(len(edited_events), 2)
        self.assertEqual(
            edited_events[1].custom_title, 'Wallabies vs pumas edited',
        )
        self.assertEqual(
            edited_events[1].custom_description, 'A rugby match edited',
        )

    def test_edit_banner_modifing_event(self, mock_get_api_events):

        form_data = {
            u'Events Selected': [u''],
            u'csrfmiddlewaretoken': [u'asd'],
            u'description': [u'Description for custom banner'],
            u'form-0-custom_description': [u'A rugby match'],
            u'form-0-custom_title': [u'Wallabies vs pumas'],
            u'form-0-description': [u'descripcion'],
            u'form-0-end': [u'2018-04-29 22:00:00'],
            u'form-0-evb_id': [u'44384359815'],
            u'form-0-evb_url': [u'https://www.eventbrite.com/'],
            u'form-0-logo': [u'none'],
            u'form-0-organizer': [u'15828411681'],
            u'form-0-selection': [u'on'],
            u'form-0-start': [u'2018-04-29 19:00:00'],
            u'form-0-title': [u'New event'],
            u'form-INITIAL_FORMS': [u'0', u'0'],
            u'form-MAX_NUM_FORMS': [u'1000', u'1000'],
            u'form-MIN_NUM_FORMS': [u'0', u'0'],
            u'form-TOTAL_FORMS': [u'1', u'1'],
            u'title': [u'CUSTOM BANNER'],
        }
        self.client.post("/banner/new/".format(
        ), form_data, follow=True)
        total_banners = Banner.objects.all()
        total_events = Event.objects.all()
        self.assertEqual(len(total_banners), 1)
        self.assertEqual(len(total_events), 1)

        form_data_edit = {
            u'Events Selected': [u''],
            u'csrfmiddlewaretoken': [u'asd'],
            u'description': [u'Description for custom banner edited'],
            u'form-0-custom_description': [u'A rugby match edited'],
            u'form-0-custom_title': [u'Wallabies vs pumas edited'],
            u'form-0-description': [u'descripcion'],
            u'form-0-end': [u'2018-04-29 22:00:00'],
            u'form-0-evb_id': [u'44384359815'],
            u'form-0-evb_url': [u'https://www.eventbrite.com/'],
            u'form-0-logo': [u'none'],
            u'form-0-organizer': [u'15828411681'],
            u'form-0-selection': [u'on'],
            u'form-0-start': [u'2018-04-29 19:00:00'],
            u'form-0-title': [u'New event'],
            u'form-INITIAL_FORMS': [u'0', u'0'],
            u'form-MAX_NUM_FORMS': [u'1000', u'1000'],
            u'form-MIN_NUM_FORMS': [u'0', u'0'],
            u'form-TOTAL_FORMS': [u'1', u'1'],
            u'title': [u'CUSTOM BANNER edited'],
        }
        self.client.post("/banner/{}/banner_update/".format(
            total_banners[0].id
        ), form_data_edit, follow=True)
        total_banners_after_edition = Banner.objects.all()
        total_events_after_edition = Event.objects.all()
        self.assertEqual(len(total_banners_after_edition), 1)
        self.assertEqual(len(total_events_after_edition), 1)
        self.assertEqual(
            total_events_after_edition[0].custom_title,
            'Wallabies vs pumas edited',
        )
        self.assertEqual(
            total_events_after_edition[0].custom_description,
            'A rugby match edited',
        )
        self.assertEqual(
            total_banners_after_edition[0].title,
            'CUSTOM BANNER edited',
        )
        self.assertEqual(
            total_banners_after_edition[0].description,
            'Description for custom banner edited',
        )

    def tearDown(self):
        self.get_auth_token_patcher.stop()
        self.eb_post_patcher.stop()


class BannerFormTest(TestBase):
    def setUp(self):
        super(BannerFormTest, self).setUp()

    def test_banner_form_valid(self):
        form_data = {
            u'Events Selected': [u''],
            u'csrfmiddlewaretoken': [u'asd'],
            u'description': [u'Description for custom banner'],
            u'form-INITIAL_FORMS': [u'0', u'0'],
            u'form-MAX_NUM_FORMS': [u'1000', u'1000'],
            u'form-MIN_NUM_FORMS': [u'0', u'0'],
            u'form-TOTAL_FORMS': [u'0', u'0'],
            u'title': [u'CUSTOM BANNER'],
        }
        form = BannerForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_banner_form_invalid(self):
        form_data = {
            u'Events Selected': [u''],
            u'csrfmiddlewaretoken': [u'asd'],
            u'description': [u'Description for custom banner'],
            u'form-INITIAL_FORMS': [u'0', u'0'],
            u'form-MAX_NUM_FORMS': [u'1000', u'1000'],
            u'form-MIN_NUM_FORMS': [u'0', u'0'],
            u'form-TOTAL_FORMS': [u'0', u'0'],
        }
        form = BannerForm(data=form_data)
        self.assertFalse(form.is_valid())


class EventFormTest(TestBase):

    def setUp(self):
        super(EventFormTest, self).setUp()

    def test_event_form_valid(self):
        form_data = {
            u'csrfmiddlewaretoken': u'asd',
            u'custom_description': u'A rugby match',
            u'custom_title': u'Wallabies vs pumas',
            u'description': u'',
            u'end': u'2021-11-27 10:30:00',
            u'evb_id': 44384359815,
            u'evb_url': u'https://www.eventbrite.com/',
            u'logo': u'none',
            u'organizer': u'15828411681',
            u'selection': u'on',
            u'start': u'2021-11-27 11:30:00',
            u'title': u'New event',
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_event_form_invalid(self):
        form_data = {
            u'csrfmiddlewaretoken': u'asd',
            u'custom_description': u'A rugby match',
            u'custom_title': u'Wallabies vs pumas',
            u'end': u'2018-04-29 22:00:00',
            u'evb_id': 44384359815,
            u'evb_url': u'https://www.eventbrite.com/',
            u'logo': u'none',
            u'organizer': u'15828411681',
            u'selection': u'on',
            u'start': u'2018-04-29 19:00:00',
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())


class BannerUtilsTest(TestBase):

    def setUp(self):
        super(BannerUtilsTest, self).setUp()
        self.get_auth_token_patcher = patch(
            'banner.utils.get_auth_token',
            return_value=123456,
        )
        self.mock_get_auth_token = self.get_auth_token_patcher.start()
        self.eb_post_patcher = patch(
            'banner.utils.Eventbrite.post',
            return_value={
                'id': 123456,
            },
        )
        self.mock_get_auth_token = self.eb_post_patcher.start()

    def test_replace_data_unicode(self):
        event = EventFactory()
        replaced_data = replace_data(event)
        self.assertTrue(isinstance(replaced_data.design.html, unicode))

    def tearDown(self):
        self.get_auth_token_patcher.stop()
        self.eb_post_patcher.stop()
