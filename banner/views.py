""" Views module. Here is the definitions
of all the views of the banner app """
# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.urlresolvers import reverse_lazy
from django.db import IntegrityError, transaction
from django.forms import modelformset_factory
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    DeleteView,
    FormView,
)
from django.shortcuts import render
from dateutil.parser import parse as parse_date
from . import forms
from .models import (
    Banner,
    BannerDesign,
    Event,
    EventDesign,
)
from .utils import (
    get_events_data,
    get_auth_token,
    get_api_events,
)
from eventbrite import Eventbrite


DEFAULT_BANNER_DESIGN = 1
DEFAULT_EVENT_DESIGN = 1


@method_decorator(login_required, name='dispatch')
class BannerNewEventsSelectedCreateView(FormView, LoginRequiredMixin):

    """ This is the view of the creation and edit of the banners """

    form_class = forms.BannerForm
    template_name = 'events_list.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):

        context = super(
            BannerNewEventsSelectedCreateView,
            self
        ).get_context_data()

        token = get_auth_token(self.request.user)
        events = get_api_events(token)

        if self.kwargs:
            existing_events = Event.objects.filter(
                banner_id=self.kwargs['pk'],
            )
            list_evb_id = [event.evb_id for event in existing_events]
        else:
            list_evb_id = []

        data_event = []
        for event in events:
            if parse_date(event['start']['local']) >= datetime.today():
                if int(event['id']) not in list_evb_id:
                    if event['logo'] is not None:
                        logo = event['logo']['url']
                    else:
                        logo = 'none'
                    data = {
                        'title': event['name']['text'],
                        'description': event['description']['text'],
                        'start': event['start']['local'].replace('T', ' '),
                        'end': event['end']['local'].replace('T', ' '),
                        'organizer': event['organizer_id'],
                        'evb_id': event['id'],
                        'evb_url': event['url'],
                        'logo': logo,
                    }
                    data_event.append(data)

        messages = []
        if data_event == [] and 'existing_events' not in locals():
            messages.append('You dont have active events')
            context['messages'] = messages
        else:
            event_formset = modelformset_factory(
                Event,
                form=forms.EventForm,
                extra=len(data_event),
            )
            if self.kwargs:
                formset = event_formset(
                    initial=data_event,
                    queryset=Event.objects.filter(
                        banner_id=self.kwargs['pk']
                    ),
                )
            else:
                formset = event_formset(
                    initial=data_event,
                    queryset=Event.objects.none(),
                )
            context['formset'] = formset
        return context

    def get_form_kwargs(self, **kwargs):
        if self.kwargs:
            banner = Banner.objects.get(id=self.kwargs['pk'])
            kwargs = super(
                BannerNewEventsSelectedCreateView, self
            ).get_form_kwargs()
            kwargs['initial']['title'] = banner.title
            kwargs['initial']['description'] = banner.description
        return kwargs

    def edit_banner(self, form, formset, *args, **kwargs):
        form.instance.user = self.request.user
        updating_banner = Banner.objects.get(id=self.kwargs['pk'])
        updating_banner.title = form.cleaned_data['title']
        updating_banner.description = form.cleaned_data['description']
        updating_banner.save()
        updating_events = Event.objects.filter(banner_id=self.kwargs['pk'])
        events_evb_id_list = [event.evb_id for event in updating_events]
        updated_events = formset.cleaned_data
        '''delete events'''
        updated_evb_id_list = [
            event['evb_id'] for event in updated_events
            if event['selection']
        ]
        for updating_event in updating_events:
            if updating_event.evb_id not in updated_evb_id_list:
                Event.objects.get(id=updating_event.id)
                updating_event.delete()
        for event in updated_events:
            if event['selection']:

                '''create evetns'''
                if int(event['evb_id']) not in events_evb_id_list:
                    e_design = EventDesign.objects.get(
                        id=DEFAULT_EVENT_DESIGN,
                    )
                    new_event = Event()
                    new_event.banner = updating_banner
                    new_event.design = e_design
                    new_event.title = event['title']
                    new_event.description = event['description']
                    new_event.start = event['start']
                    new_event.end = event['end']
                    new_event.logo = event['logo']
                    new_event.organizer = event['organizer']
                    new_event.evb_id = event['evb_id']
                    new_event.evb_url = event['evb_url']
                    new_event.custom_title = event['custom_title']
                    new_event.custom_description = event['custom_description']
                    if Event.objects.all().count() == 0:
                        last_event_id = 1
                    else:
                        last_event_id = Event.objects.latest('created').id
                    if event['custom_logo']:
                        new_event.custom_logo = self.img_upload(
                            event['custom_logo'],
                            new_event.banner.id,
                            last_event_id + 1,
                        )
                    new_event.save()
                else:
                    for updating_event in updating_events:
                        '''update events'''
                        if int(event['evb_id']) == updating_event.evb_id:
                            updating_event.custom_title = event['custom_title']
                            updating_event.custom_description \
                                = event['custom_description']
                            try:
                                if event['custom_logo']:
                                    updating_event.custom_logo \
                                        = self.img_upload(
                                            event['custom_logo'],
                                            updating_event.banner.id,
                                            updating_event.id,
                                        )
                            except IntegrityError as e:
                                print e.message
                            updating_event.save()
        return super(
            BannerNewEventsSelectedCreateView,
            self,
        ).form_valid(form)

    def post(self, request, *args, **kwargs):
        form = forms.BannerForm(
            request.POST,
        )

        event_formset = modelformset_factory(
            Event,
            form=forms.EventForm,
        )

        formset = event_formset(
            request.POST,
            request.FILES,
            queryset=Event.objects.none(),
        )
        if form.is_valid() and formset.is_valid():
            if not any([
                    selection_cleaned_data['selection']
                    for selection_cleaned_data in formset.cleaned_data
            ]):
                form.add_error(NON_FIELD_ERRORS, 'No events selected')
                return render(
                    request,
                    'event_list.html',
                    {'form': form, 'formset': formset}
                )
            if 'pk' in self.kwargs:
                return self.edit_banner(form, formset, self.kwargs['pk'])
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form)

    @transaction.atomic
    def form_valid(self, form, formset):
        form.instance.user = self.request.user
        banner = form.save(commit=False)
        events = formset.save(commit=False)
        try:
            with transaction.atomic():
                b_design = BannerDesign.objects.get(
                    id=DEFAULT_BANNER_DESIGN,
                )
                banner.design = b_design
                banner.save()

                e_design = EventDesign.objects.get(
                    id=DEFAULT_EVENT_DESIGN,
                )

                last_banner_id = Banner.objects.latest('created').id
                for event in events:
                    if event is not None:
                        event.banner = banner
                        event.design = e_design
                        if Event.objects.all().count() == 0:
                            last_event_id = 1
                        else:
                            last_event_id = Event.objects.latest('created').id
                        if event.custom_logo:
                            event.custom_logo = self.img_upload(
                                event.custom_logo,
                                last_banner_id + 1,
                                last_event_id + 1,
                            )
                        event.save()
        except IntegrityError as error:
            print error.message

        return super(
            BannerNewEventsSelectedCreateView,
            self,
        ).form_valid(form)


class BannerDeleteView(DeleteView):

    """ This is the delete banner view """

    model = Banner
    template_name = 'delete_banner.html'
    success_url = reverse_lazy('index')


@method_decorator(login_required, name='dispatch')
class BannerView(TemplateView, LoginRequiredMixin):

    """ This is the index view. Here we display all the banners that the user
    has created """

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(BannerView, self).get_context_data(**kwargs)
        banners = Banner.objects.filter(user=self.request.user)
        events = []
        for banner in banners:
            for event in Event.objects.filter(banner=banner):
                events.append(event)
        not_assigned_events = Event.objects.exclude(
            banner__isnull=False
        ).exists()
        context['notassignedevents'] = not_assigned_events
        context['events'] = events
        context['banners'] = banners
        return context


@method_decorator(login_required, name='dispatch')
class BannerDetailView(DetailView, LoginRequiredMixin):

    """ This view where we can see what's inside of a banner """

    model = Banner

    def get_context_data(self, **kwargs):
        context = super(BannerDetailView, self).get_context_data(**kwargs)
        banner = Banner.objects.get(id=self.kwargs['pk'])
        events = Event.objects.filter(banner=banner)

        context['banner'] = banner
        context['events'] = events
        return context


class BannerPreview(TemplateView, LoginRequiredMixin):

    """ This view is the one that enables us to see the banner in action! """

    template_name = 'banner/preview.html'

    def get_context_data(self, **kwargs):
        context = super(BannerPreview, self).get_context_data(**kwargs)
        banner = Banner.objects.select_related(
            'design'
        ) .get(
            id=self.kwargs['pk']
        )

        # Should be refactored when assigning positions
        # to the events in the banner
        events = [
            (idx, event)
            for idx, event in
            enumerate(
                Event.objects.filter(
                    banner=banner
                )
            )
        ]

        events_data = [
            event for event in get_events_data(events, banner)
        ]
        context['banner'] = banner
        context['events_data'] = events_data
        return context


@method_decorator(login_required, name='dispatch')
class EditEventDesignView(FormView, LoginRequiredMixin):

    """ The view to edit the layout of an event (or anything really)
    through an html editor """

    template_name = 'event/edit_design.html'
    form_class = forms.EventDesignForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super(EditEventDesignView, self).get_context_data(**kwargs)
        event = Event.objects.get(pk=self.kwargs['epk'])
        context['event'] = event
        return context

    def get_form_kwargs(self):
        kwargs = super(EditEventDesignView, self).get_form_kwargs()
        event = Event.objects.select_related(
            'design'
        ).get(
            pk=self.kwargs['epk']
        )
        kwargs['initial']['html'] = event.design.html
        return kwargs

    def post(self, request, *args, **kwargs):

        event = Event.objects.select_related(
            'design'
        ).get(
            pk=self.kwargs['epk']
        )

        if event.design.name == 'default':
            form = forms.EventDesignForm(
                request.POST,
            )
        else:
            form = forms.EventDesignForm(
                request.POST,
                instance=event.design,
            )
        if form.is_valid():
            return self.form_valid(form)

        form.add_error(NON_FIELD_ERRORS, "Can't submit it empty!")
        return render(
            request,
            'event/edit_design.html',
            {'form': form}
        )

    def form_valid(self, form, *args, **kwargs):
        form.instance.user = self.request.user
        event_design = form.save()
        if event_design.name != 'default':
            event = Event.objects.select_related(
                'design'
            ).get(
                pk=self.kwargs['epk']
            )
            event.design = event_design
        event_design.save()
        event.save()

        return super(
            EditEventDesignView,
            self,
        ).form_valid(form)


@method_decorator(login_required, name='dispatch')
class AddUnassignedEventsView(FormView, LoginRequiredMixin):

    """ The view to edit the layout of an event (or anything really)
    through an html editor """

    template_name = 'banner/add_unassigned_events.html'
    form_class = forms.SelectBannerForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super(
            AddUnassignedEventsView,
            self,
        ).get_context_data(**kwargs)

        not_assigned_events = Event.objects.exclude(
            banner__isnull=False
        )

        event_formset = modelformset_factory(
            Event,
            form=forms.EventForm,
            extra=0,
        )

        form = forms.SelectBannerForm()

        form.fields['banner'].queryset = Banner.objects.filter(
            user=self.request.user
        )

        formset = event_formset(
            queryset=not_assigned_events,
        )

        context['form'] = form
        context['formset'] = formset
        return context

    def post(self, request, *args, **kwargs):
        form = forms.SelectBannerForm(
            request.POST,
            request.user,
        )

        event_formset = modelformset_factory(
            Event,
            form=forms.EventForm,
        )

        formset = event_formset(
            request.POST,
            request.FILES,
            queryset=Event.objects.none(),
        )

        if form.is_valid() and formset.is_valid():
            if not any([
                    selection_cleaned_data['selection']
                    for selection_cleaned_data in formset.cleaned_data
            ]):
                form.add_error(NON_FIELD_ERRORS, 'No events selected')
                return render(
                    request,
                    self.template_name,
                    {'form': form, 'formset': formset}
                )
            if 'pk' in self.kwargs:
                return self.edit_banner(form, formset, self.kwargs['pk'])
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, formset):
        banner = form.cleaned_data['banner']
        events = [
            event['id'] for event in formset.cleaned_data if event['selection']
        ]

        for event in events:
            event.banner = banner
            event.save()

        not_assigned_events_exists = Event.objects.exclude(
            banner__isnull=False
        ).exists()

        if not_assigned_events_exists:
            self.success_url = reverse_lazy('add_events')

        return super(
            AddUnassignedEventsView,
            self,
        ).form_valid(form)

