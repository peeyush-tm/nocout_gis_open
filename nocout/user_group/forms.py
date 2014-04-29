from django import forms
from user_profile.models import UserGroup

class UserGroupForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = ('name', 'alias', 'parent', 'device_group', 'location', 'address')
        