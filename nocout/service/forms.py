from django import forms
from django.core.exceptions import ValidationError
from models import Service, ServiceParameters, ServiceDataSource, Protocol, ServiceSpecificDataSource
import re
from django.forms.util import ErrorList
from django.forms.models import inlineformset_factory,BaseInlineFormSet
import logging
logger = logging.getLogger(__name__)


#************************************* Service ******************************************
class BaseServiceDataSourceFormset(BaseInlineFormSet):
    """
    """
    def __init__(self, *args, **kwargs):

        super(BaseServiceDataSourceFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['service_data_sources'].empty_label = 'Select'

    def clean(self):
        for form in self.forms:
            if not 'service_data_sources' in form.cleaned_data:
                raise forms.ValidationError("This field is required.")

class ServiceForm(forms.ModelForm):
    """
    Class Based Service Model Form.
    """
    def __init__(self, *args, **kwargs):
        # removing help text for service_data_sources 'select' field
        #self.base_fields['service_data_sources'].help_text = ''

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        """
        Meta Information
        """
        model = Service
        fields = ('name', 'alias', 'parameters', 'command', 'description')

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = Service.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for service form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data
widgets = {
           'critical': forms.TextInput(attrs= {'class' : 'form-control'}),
           'warning': forms.TextInput(attrs= {'class' : 'form-control'}),
           'service_data_sources': forms.Select(attrs= {'class' : 'form-control'})
    }
ServiceDataSourceCreateFormSet = inlineformset_factory(Service, ServiceSpecificDataSource, formset=BaseServiceDataSourceFormset,
    extra=1, widgets=widgets, can_delete=True)
ServiceDataSourceUpdateFormSet = inlineformset_factory(Service, ServiceSpecificDataSource, formset=BaseServiceDataSourceFormset,
    extra=0, widgets=widgets, can_delete=True)


#************************************** Service Data Source ****************************************
class ServiceDataSourceForm(forms.ModelForm):
    """
    Class Based ServiceDataSource Model Form .
    """
    def __init__(self, *args, **kwargs):

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        """
        Meta Information.
        """
        model = ServiceDataSource

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = ServiceDataSource.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for service data source form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


#************************************** Service Parameters *****************************************
class ServiceParametersForm(forms.ModelForm):
    """
    Class Based Service Parameters Model Form .
    """
    def __init__(self, *args, **kwargs):

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        """
        Meta information.
        """
        model = ServiceParameters

    def clean_parameter_description(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['parameter_description']
        names = ServiceParameters.objects.filter(parameter_description=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for service data source form
        """
        name = self.cleaned_data.get('parameter_description')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['parameter_description'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


#************************************** Protocol *****************************************
class ProtocolForm(forms.ModelForm):
    """
    Class Based Protocol Model Form.
    """
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

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        """
        Meta Information.
        """
        model = Protocol

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = Protocol.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for service data source form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


