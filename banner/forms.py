from django import forms


class EventSelected(forms.Form):

    title = forms.CharField(required=False)
    description = forms.CharField(required=False)
    start = forms.CharField(required=False)
    end = forms.CharField(required=False)
    organizer = forms.HiddenInput()
    logo = forms.CharField(initial='logo', required=False)
    selection = forms.BooleanField(required=False)
    event_id = forms.CharField(required=False)

    # def add_event(self, event):
    #     self.fields[event['id']] = forms.BooleanField(required=False)

        #self.fields[event['name']['text']] = forms.BooleanField(required=False)
