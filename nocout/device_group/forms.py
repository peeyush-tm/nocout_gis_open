from django import forms
from device_group.models import DeviceGroup


class DeviceGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceGroupForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.__class__ == forms.widgets.TextInput:
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' form-control'
                else:
                    field.widget.attrs.update({'class':'form-control'})
        for name, field in self.fields.items():
            if field.widget.__class__ == forms.widgets.Select:
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' form-control'
                else:
                    field.widget.attrs.update({'class':'form-control'})

    class Meta:
        model = DeviceGroup
        fields = ('name', 'alias', 'parent', 'location', 'address')