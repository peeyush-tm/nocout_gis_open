import inspect
import re

from django import forms
from django.forms.models import inlineformset_factory,  BaseInlineFormSet
from django.forms.util import ErrorList
from django.core.exceptions import ValidationError

from service.models import Service, ServiceParameters, ServiceDataSource, Protocol, ServiceSpecificDataSource, \
    DeviceServiceConfiguration
from device.forms import BaseDeviceTypeServiceFormset

from performance import formulae

import logging
logger = logging.getLogger(__name__)


#************************************* Service ******************************************
class BaseServiceDataSourceFormset(BaseInlineFormSet):
    """
    Custome Inline formest.
    """
    def __init__(self, *args, **kwargs):

        super(BaseServiceDataSourceFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['service_data_sources'].empty_label = 'Select'

    def clean(self):
        for form in self.forms:
            if not len(form.cleaned_data.keys()):
                raise forms.ValidationError('This field is required.')

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
    'critical': forms.TextInput(attrs={'class': 'form-control'}),
    'warning': forms.TextInput(attrs={'class': 'form-control'}),
    'service_data_sources': forms.Select(attrs={'class': 'form-control'})
}
ServiceDataSourceCreateFormSet = inlineformset_factory(Service, ServiceSpecificDataSource,
                                                       formset=BaseServiceDataSourceFormset,
                                                       extra=1, widgets=widgets, can_delete=True, fields="__all__")
ServiceDataSourceUpdateFormSet = inlineformset_factory(Service, ServiceSpecificDataSource,
                                                       formset=BaseServiceDataSourceFormset,
                                                       extra=0, widgets=widgets, can_delete=True, fields="__all__")
DTServiceDataSourceUpdateFormSet = inlineformset_factory(Service, ServiceSpecificDataSource,
                                                         formset=BaseDeviceTypeServiceFormset,
                                                         extra=0, widgets=widgets, can_delete=False, fields="__all__")

# ************************************** Service Data Source ****************************************
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

        FORMULA_CHOICES = [('', 'No Formula')]
        FORMULA_CHOICES += [(function_tuple[0], function_tuple[0]) for function_tuple in inspect.getmembers(formulae, inspect.isfunction)]
        self.fields['formula'] = forms.ChoiceField(choices=FORMULA_CHOICES, required=False)

        for name, field in self.fields.items():
            self.fields['chart_color'].widget.attrs.update({'class':'colorpicker',\
                                                            'data-color-format':'rgba' })
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
        fields = "__all__"

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


# ************************************** Service Parameters *****************************************
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
        fields = "__all__"

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
        fields = "__all__"

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


# ************************************** Device Service Configuration Update *****************************************
class DeviceServiceConfigurationForm(forms.ModelForm):
    """
    Class Based Protocol Model Form.
    """
    def __init__(self, *args, **kwargs):

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(DeviceServiceConfigurationForm, self).__init__(*args, **kwargs)

        self.fields['device_name'].widget.attrs['readonly'] = True
        self.fields['service_name'].widget.attrs['readonly'] = True
        self.fields['agent_tag'].widget.attrs['readonly'] = True
        self.fields['port'].widget.attrs['readonly'] = True
        self.fields['data_source'].widget.attrs['readonly'] = True
        self.fields['version'].widget.attrs['readonly'] = True
        self.fields['read_community'].widget.attrs['readonly'] = True
        self.fields['svc_template'].widget.attrs['readonly'] = True
        self.fields['normal_check_interval'].widget.attrs['readonly'] = True
        self.fields['retry_check_interval'].widget.attrs['readonly'] = True
        self.fields['max_check_attempts'].widget.attrs['readonly'] = True

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
        model = DeviceServiceConfiguration
        exclude = ['operation', 'added_on', 'modified_on', 'is_added']



