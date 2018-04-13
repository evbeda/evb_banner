from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import modelformset_factory
from .models import (
    Banner,
    Event,
    EventDesign,
)


class EventForm(forms.ModelForm):

    selection = forms.BooleanField(required=False)
    evb_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    evb_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    custom_title = forms.CharField(required=False)
    custom_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'cols': 50, 'rows': 2}),
    )
    custom_logo = forms.FileField(required=False)
    start = forms.DateTimeField(
        required=False,
        widget=forms.HiddenInput(),
    )
    end = forms.DateTimeField(
        required=False,
        widget=forms.HiddenInput(),
    )
    organizer = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    title = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    description = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    logo = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Event
        exclude = ('design', 'banner',)

    def save(self, commit=True):
        m = super(EventForm, self).save(commit=False)
        cd = self.cleaned_data
        if commit:
            m.save()
        if cd['selection']:
            return m

class BannerForm(forms.ModelForm):

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'cols': 90, 'rows': 4})
    )

    class Meta:
        model = Banner
        exclude = ('user', 'design',)

class EventDesignForm(forms.ModelForm):

    class Meta:
        model = EventDesign
        exclude = ()

'''will be refactor'''
class EventForm(forms.ModelForm):

    selection = forms.BooleanField(required=False)
    evb_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    evb_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    custom_title = forms.CharField(required=False)
    custom_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'cols': 50, 'rows': 2}),
    )
    custom_logo = forms.FileField(required=False)
    start = forms.DateTimeField(
        required=False,
        widget=forms.HiddenInput(),
    )
    end = forms.DateTimeField(
        required=False,
        widget=forms.HiddenInput(),
    )
    organizer = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    title = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    description = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    logo = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    order = forms.CharField(
        required=False,
    )


