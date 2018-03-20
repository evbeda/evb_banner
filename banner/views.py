# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from eventbrite import Eventbrite
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class EventsView(TemplateView, LoginRequiredMixin):

    template_name = "events/events.html"

    def get_context_data(self, **kwargs):
        context = super(EventsView, self).get_context_data(**kwargs)
        access_token = self.request.user.social_auth.all()[0].access_token
        eventbrite = Eventbrite(access_token)
        context['events'] = [
            event['name']['html']
            for event in eventbrite.get('/users/me/events/')['events']
        ]
        return context

