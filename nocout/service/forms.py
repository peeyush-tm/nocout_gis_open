from django import forms
from models import Service, ServiceParameters


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('service_name', 'alias', 'parameters', 'command', 'description')


class ServiceParametersForm(forms.ModelForm):
    class Meta:
        model = ServiceParameters
        fields = ('parameter_description', 'max_check_attempts', 'check_interval',
                  'retry_interval', 'check_period', 'notification_interval',
                  'notification_period'
        )
