from django.core.exceptions import ValidationError
import re
from django import forms
from device.models import Device
from device_group.models import DeviceGroup
from organization.models import Organization
from django.forms.util import ErrorList
import logging
logger = logging.getLogger(__name__)


class DeviceGroupForm(forms.ModelForm):
    """
    Device Group Models Form to create and update.
    """

    def __init__(self, *args, **kwargs):
        initial = kwargs.setdefault('initial',{})
        if kwargs['instance']:
            initial['organization']= kwargs['instance'].organization.id
        elif Organization.objects.all():
            initial['organization']=Organization.objects.all()[0].id
        else:
            initial['organization']=None


        # removing help text for devices 'select' field
        self.base_fields['devices'].help_text = ''

        super(DeviceGroupForm, self).__init__(*args, **kwargs)
        self.fields['parent'].empty_label = 'Select'
        self.fields['organization'].empty_label = 'Select'

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        organization_id = None
        if kwargs['instance']:
            self.fields['name'].widget.attrs['readonly'] = True
            organization_id=initial['organization']
        elif Organization.objects.all():
            organization_id=Organization.objects.all()[0].id
        if organization_id:
            organization_descendants_ids= Organization.objects.get(id= organization_id).get_descendants(include_self=True)\
                .values_list('id', flat=True)
            self.fields['devices'].queryset= Device.objects.filter( organization__in = organization_descendants_ids, is_deleted=0)

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                else:
                    field.widget.attrs['class'] += ' form-control'
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        """
        Meta Information.
        """
        model = DeviceGroup
        fields = ('name', 'alias', 'parent', 'organization', 'devices')

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = DeviceGroup.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for device group form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data