from django import forms
from user_profile.models import UserGroup
from nocout.widgets import MultipleToSingleSelectionWidget


class UserGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserGroupForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})

    class Meta:
        model = UserGroup
        fields = ('name', 'alias', 'parent', 'device_group', 'location', 'address')

        widgets = {
            'device_group': MultipleToSingleSelectionWidget,
        }
