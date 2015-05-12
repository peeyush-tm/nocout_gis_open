"""
=====================================================================
Module contains forms functionlity specific to 'activity_stream' app.
=====================================================================

Location:
* /nocout_gis/nocout/activity_stream/forms.py

List of constructs:
=======
Classes
=======
* UserActionForm
"""

from django import forms


class UserActionForm(forms.Form):
    action = forms.CharField(max_length=128, required=True)
    module = forms.CharField(widget=forms.TextInput, required=True)
