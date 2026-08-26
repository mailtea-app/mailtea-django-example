from django import forms


class NotificationForm(forms.Form):
    """Shared by the HTML form and the JSON endpoint, so both validate alike."""

    to = forms.EmailField(label="To")
    subject = forms.CharField(label="Subject", max_length=200)
    message = forms.CharField(label="Message", widget=forms.Textarea)
