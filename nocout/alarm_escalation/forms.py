from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList

from organization.models import Organization
from alarm_escalation.models import EscalationLevel
import logging
logger = logging.getLogger(__name__)


class EscalationLevelForm(forms.ModelForm):
    """
    Class Based Escalation Level Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
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
        self.fields['service_data_source'].widget.attrs['id'] = 'id_data_source'
        if not self.request.user.is_superuser:
            self.fields['organization'].queryset = Organization.objects.filter(id=self.request.user.userprofile.organization.id)
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

    def clean(self):
        level_list = list()
        if 'organization' in self.cleaned_data and 'device_type' in self.cleaned_data and 'service' in self.cleaned_data and 'service_data_source' in self.cleaned_data:
            level_list = EscalationLevel.objects.filter(organization=self.cleaned_data['organization'],
                                               name=self.cleaned_data['name'],
                                               service=self.cleaned_data['service'],
                                               device_type=self.cleaned_data['device_type'],
                                               service_data_source=self.cleaned_data['service_data_source'])
            try:
                if self.id:
                    level_list = level_list.exclude(pk=self.id)
            except Exception as e:
                logger.info(e.message)

        if level_list:
            self._errors['name'] = ErrorList([u'This level, device type, service, data source is already exists in this organization.'])
        return self.cleaned_data
