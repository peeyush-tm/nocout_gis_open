from django import forms
from django.forms import ModelForm

from activity_stream.models import UserAction

class UserActionForm(ModelForm):
    action = forms.CharField(max_length=128, required=True)
    module = forms.CharField(widget=forms.TextInput, required=True)
    class Meta:
        model = UserAction
        fields = ['action', 'module']
