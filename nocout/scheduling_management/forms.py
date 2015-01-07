from django import forms

from scheduling_management.models import Event, Weekdays
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
    repeat_on = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(),
                queryset=Weekdays.objects.filter().order_by('id'), required=False)
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
                else:
                    field.widget.attrs['class'] += ' form-control'
            else:
                if (name =='repeat_by') or (name == 'repeat_on'): # prevent these field from assigning of th select2 class.
                    field.widget.attrs.update({'class': 'col-md'})
                elif name == 'device':
                   field.widget.attrs.update({'class': 'col-md-12'})
                elif isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        """
        Meta Information
        """
        model = Event
        exclude = ('created_by', 'organization')
