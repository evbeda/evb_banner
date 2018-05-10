from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import modelformset_factory
from ckeditor.widgets import CKEditorWidget
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
        widget=forms.HiddenInput(),
    )
    end = forms.DateTimeField(
        widget=forms.HiddenInput(),
    )
    organizer = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    title = forms.CharField(
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

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['selection'].initial = True


class BannerForm(forms.ModelForm):

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'cols': 90, 'rows': 4})
    )

    class Meta:
        model = Banner
        exclude = ('user', 'design',)


class EventDesignForm(forms.ModelForm):

    html = forms.CharField(
        required=True,
        widget=CKEditorWidget(),
    )

    class Meta:
        model = EventDesign
        exclude = ('user', 'name',)


class SelectBannerForm(forms.Form):
    banner = forms.ModelChoiceField(queryset=Banner.objects.all())


class EventsSortForm(forms.Form):

    sort = forms.IntegerField(required=True)
    event = forms.IntegerField(
        required=True,
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


class BannerSortForm(forms.Form):
    title = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    description = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    banner = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput(),
    )
