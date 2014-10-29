from django import forms

class UserActionForm(forms.Form):
    action = forms.CharField(max_length=128, required=True)
    module = forms.CharField(widget=forms.TextInput, required=True)
