import re
from django import forms
from django.core.exceptions import ValidationError
from django.forms.util import ErrorList
from organization.models import Organization

from scheduling_management.models import Event, Weekdays, SNMPTrapSettings
from device.models import Device, DeviceTechnology
import logging
logger = logging.getLogger(__name__)


class EventForm(forms.ModelForm):
    """
    Rendering form for Scheduling event
    """

    repeat_every_list = []  # Create the list from 1 to 30 as (i,i)
    for i in range(1,31):
        repeat_every_list.append((i,i))

    REPEAT_EVERY = tuple(repeat_every_list)

    repeat_every = forms.ChoiceField(initial=1, choices=REPEAT_EVERY, required=False)
    repeat_by = forms.ChoiceField(widget=forms.RadioSelect(), choices=Event.REPEAT_BY, required=False)
    repeat_on = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices = Weekdays.WEEKDAYS, required=False)
    end_never = forms.BooleanField(initial=True, required=False)
    start_on_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), required=True)
    end_on_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), required=True)
    technology = forms.ModelChoiceField(queryset=DeviceTechnology.objects.all(), empty_label='Select', required=False)
    # Note take a boolean field in model and replate select_device name with that field.
    # select_device = forms.ChoiceField(widget=forms.RadioSelect(), initial=False,
    #                 choices=((True, 'Add all device'),(False, 'Select specific devices')), required=False)


    def __init__(self, *args, **kwargs):
        # # removing help text for device 'select' field
        self.base_fields['device'].help_text = ''
        self.base_fields['end_never'].widget = forms.HiddenInput()
        self.base_fields['device'].widget = forms.HiddenInput()
        # removing help text for device type 'select' field
        self.base_fields['device_type'].help_text = ''
        self.base_fields['device_type'].widget = forms.HiddenInput()
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(EventForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if (name =='repeat_by') or (name == 'repeat_on'): # prevent these field from assigning of th select2 class.
                    field.widget.attrs['class'] += ' col-md'
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                elif isinstance(field.widget, forms.widgets.HiddenInput):
                    field.widget.attrs['class'] += ' col-md-12'
                else:
                    field.widget.attrs['class'] += ' form-control'
            else:
                if (name =='repeat_by') or (name == 'repeat_on'): # prevent these field from assigning of th select2 class.
                    field.widget.attrs.update({'class': 'col-md'})
                elif name == 'device':
                   field.widget.attrs.update({'class': 'col-md-12'})
                elif isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                elif isinstance(field.widget, forms.widgets.HiddenInput):
                    field.widget.attrs.update({'class': 'col-md-12'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        """
        Meta Information
        """
        model = Event
        exclude = ('created_by', 'organization')


# *************************************** Antenna **************************************
class SNMPTrapSettingsForm(forms.ModelForm):
    """
    Class Based View SNMPTrapSettings Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SNMPTrapSettingsForm, self).__init__(*args, **kwargs)
        self.fields['device_technology'].empty_label = 'Select'
        self.fields['device_vendor'].empty_label = 'Select'
        self.fields['device_model'].empty_label = 'Select'
        self.fields['device_type'].empty_label = 'Select'

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                else:
                    field.widget.attrs['class'] += ' tip-focus form-control'
                    field.widget.attrs['data-toggle'] = 'tooltip'
                    field.widget.attrs['data-placement'] = 'right'
                    field.widget.attrs['title'] = field.help_text
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': ' tip-focus form-control'})
                    field.widget.attrs.update({'data-toggle': 'tooltip'})
                    field.widget.attrs.update({'data-placement': 'right'})
                    field.widget.attrs.update({'title': field.help_text})

    class Meta:
        """
        Meta Information
        """
        model = SNMPTrapSettings

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = SNMPTrapSettings.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This trap name is already in use.')
        return name

    def clean(self):
        """
        Validations for antenna form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Trap name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data
