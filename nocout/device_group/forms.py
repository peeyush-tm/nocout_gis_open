from django import forms
from device_group.models import DeviceGroup


class DeviceGroupForm(forms.ModelForm):
    class Meta:
        model = DeviceGroup
        fields = ('name', 'alias', 'parent', 'location', 'address')