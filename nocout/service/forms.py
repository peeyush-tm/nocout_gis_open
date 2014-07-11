from django import forms
from models import Service, ServiceParameters, ServiceDataSource, Protocol


#************************************* Service ******************************************
class ServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # removing help text for service_data_sources 'select' field
        self.base_fields['service_data_sources'].help_text = ''

        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['parameters'].empty_label = 'Select'
        self.fields['command'].empty_label = 'Select'
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
        model = Service


#************************************** Service Data Source ****************************************
class ServiceDataSourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceDataSourceForm, self).__init__(*args, **kwargs)
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
        model = ServiceDataSource


#************************************** Service Parameters *****************************************
class ServiceParametersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceParametersForm, self).__init__(*args, **kwargs)
        self.fields['protocol'].empty_label = 'Select'
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
        model = ServiceParameters


#************************************** Protocol *****************************************
class ProtocolForm(forms.ModelForm):

    AUTH_PROTOCOL = (
        ('', 'Select'),
        ('MD5', 'MD5'),
        ('SHA', 'SHA'),
    )

    SECURITY_LEVEL = (
        ('', 'Select'),
        ('NoAuthNoPriv', 'NoAuthNoPriv'),
        ('authNoPriv', 'authNoPriv'),
        ('authpriv', 'authpriv')
    )

    PRIVATE_PHASE = (
        ('', 'Select'),
        ('AES', 'AES'),
        ('DES', 'DES')
    )

    security_level = forms.TypedChoiceField(choices=SECURITY_LEVEL, required=False)
    auth_protocol = forms.TypedChoiceField(choices=AUTH_PROTOCOL, required=False)
    private_phase = forms.TypedChoiceField(choices=PRIVATE_PHASE, required=False)

    def __init__(self, *args, **kwargs):
        super(ProtocolForm, self).__init__(*args, **kwargs)
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
        model = Protocol
