from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from alarm_escalation.models import EscalationLevel
import logging
logger = logging.getLogger(__name__)


# class AlarmEscalationForm(forms.ModelForm):
#     """
#     Class Based View AlarmEscalation Model form to update and create.
#     """
#     def __init__(self, *args, **kwargs):
#         initial = kwargs.setdefault('initial',{})

#         try:
#             if 'instance' in kwargs:
#                 self.id = kwargs['instance'].id
#         except Exception as e:
#             logger.info(e.message)

#         super(AlarmEscalationForm, self).__init__(*args, **kwargs)
#         self.fields['technology'].empty_label = 'Select'
#         self.fields['base_station'].empty_label = 'Select'
#         for name, field in self.fields.items():
#             if field.widget.attrs.has_key('class'):
#                 if isinstance(field.widget, forms.widgets.Select):
#                     field.widget.attrs['class'] += ' col-md-12'
#                     field.widget.attrs['class'] += ' select2select'
#                 else:
#                     field.widget.attrs['class'] += ' form-control'
#             else:
#                 if isinstance(field.widget, forms.widgets.Select):
#                     field.widget.attrs.update({'class': 'col-md-12 select2select'})
#                 else:
#                     field.widget.attrs.update({'class': 'form-control'})


#     class Meta:
#         model = AlarmEscalation


class EscalationLevelForm(forms.ModelForm):
    """
    Class Based View Level Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        initial = kwargs.setdefault('initial',{})

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(EscalationLevelForm, self).__init__(*args, **kwargs)
        self.fields['organization'].empty_label = 'Select'
        self.fields['service'].empty_label = 'Select'
        self.fields['device_type'].empty_label = 'Select'
        self.fields['service_data_source'].empty_label = 'Select'
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
        model = EscalationLevel

