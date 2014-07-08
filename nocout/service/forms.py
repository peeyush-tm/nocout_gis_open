from django import forms
from models import Service, ServiceParameters, ServiceDataSource, Protocol


#************************************* Service ******************************************
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


#************************************** Service Data Source ****************************************
class ServiceDataSourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceDataSourceForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = ServiceDataSource


#************************************** Service Parameters *****************************************
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


#************************************** Protocol *****************************************
class ProtocolForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProtocolForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = Protocol
