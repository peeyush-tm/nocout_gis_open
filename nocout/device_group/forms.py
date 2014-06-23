from django import forms
from device.models import Device
from device_group.models import DeviceGroup
from organization.models import Organization


class DeviceGroupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        initial = kwargs.setdefault('initial',{})
        if kwargs['instance']:
            initial['organization']= kwargs['instance'].organization.id
        elif Organization.objects.all():
            initial['organization']=Organization.objects.all()[0].id
        else:
            initial['organization']=None

        super(DeviceGroupForm, self).__init__(*args, **kwargs)

        organization_id=None
        if kwargs['instance']:
            self.fields['name'].widget.attrs['readonly'] = True
            organization_id=initial['organization']
        elif Organization.objects.all():
            organization_id=Organization.objects.all()[0].id
        if organization_id:
            organization_descendants_ids= Organization.objects.get(id= organization_id).get_descendants(include_self=True).values_list('id', flat=True)
            self.fields['devices'].queryset= Device.objects.filter( organization__in = organization_descendants_ids, is_deleted=0)

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
        fields = ('name', 'alias', 'parent', 'location', 'address','organization','devices')