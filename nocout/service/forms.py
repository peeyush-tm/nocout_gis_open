from django import forms
from models import Service, ServiceParameters


class ServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = Service
        fields = ('service_name', 'alias', 'parameters', 'command', 'description')


class ServiceParametersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceParametersForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = ServiceParameters
        fields = ('parameter_description', 'max_check_attempts', 'check_interval',
                  'retry_interval', 'check_period', 'notification_interval',
                  'notification_period'
        )
