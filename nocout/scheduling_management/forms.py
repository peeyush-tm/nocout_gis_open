from django import forms

from scheduling_management.models import Event, Weekdays
from device.models import Device
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

    end_never = forms.BooleanField(initial=True, required=False)
    # Note take a boolean field in model and replate select_device name with that field.
    select_device = forms.ChoiceField(widget=forms.RadioSelect(),
                    choices=((True, 'Add all device'),(False, 'Select specific devices')))
    device = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(),
                queryset=Device.objects.all(), required=False)


    def __init__(self, *args, **kwargs):
        # # removing help text for device 'select' field
        # self.base_fields['device'].help_text = ''
        self.base_fields['end_never'].widget = forms.HiddenInput()

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(EventForm, self).__init__(*args, **kwargs)
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
                if isinstance(field.widget, forms.widgets.RadioSelect):
                    field.widget.attrs.update({'class': ''})
                elif isinstance(field.widget, forms.widgets.CheckboxSelectMultiple):
                    field.widget.attrs.update({'class': ''})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        """
        Meta Information
        """
        model = Event
        exclude = ('created_by', 'organization', 'device', 'repeat_every', 'repeat_by', 'repeat_on',)
