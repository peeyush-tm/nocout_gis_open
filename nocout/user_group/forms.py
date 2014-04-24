from django import forms
from user_profile.models import UserGroup
from nocout.widgets import MultipleToSingleSelectionWidget

class UserGroupForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = ('name', 'alias', 'parent', 'device_group', 'location', 'address')
        
        widgets = {
                'device_group': MultipleToSingleSelectionWidget,
        }