from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from alarm_escalation.models import EscalationLevel
import logging
logger = logging.getLogger(__name__)


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
        self.fields['alarm_age'].widget.attrs['placeholder'] = 'Enter Age in Seconds.'
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

    def clean_emails(self):
        if self.cleaned_data['emails'] != '':
            emails = self.cleaned_data['emails'].replace(' ','')
            emails = emails.split(',')
            try:
                for email in emails:
                    print email
                    validate_email(email)
            except ValidationError as e:
                raise ValidationError('Invalid emails.')
        return self.cleaned_data['emails']
