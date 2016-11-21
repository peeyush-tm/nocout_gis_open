from django import forms
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType, \
    Country, State, City, StateGeoInfo, DevicePort, DeviceFrequency, DeviceTypeService, DeviceTypeServiceDataSource, \
    DeviceSyncHistory
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory,  BaseInlineFormSet
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
from nocout.widgets import MultipleToSingleSelectionWidget, IntReturnModelChoiceField
from device.models import DeviceTypeFields
from service.models import Service, ServiceDataSource

from nocout.settings import ENABLE_PARENT_FIELDS
from django.forms.util import ErrorList
import re
import logging
logger = logging.getLogger(__name__)


# *************************************** Device Form ***********************************************


class DeviceForm(forms.ModelForm):
    """
    Rendering form for device
    """
    device_technology = IntReturnModelChoiceField(queryset=DeviceTechnology.objects.all(),
                                                  required=True)
    device_vendor = IntReturnModelChoiceField(queryset=DeviceVendor.objects.all(),
                                              required=True)
    device_model = IntReturnModelChoiceField(queryset=DeviceModel.objects.all(),
                                             required=True)
    device_type = IntReturnModelChoiceField(queryset=DeviceType.objects.all(),
                                            required=True)

    def __init__(self, *args, **kwargs):

        self.request=kwargs.pop('request', None)
        # setting foreign keys field label
        self.base_fields['site_instance'].label = 'Site Instance'
        self.base_fields['machine'].label = 'Machine'
        self.base_fields['device_technology'].label = 'Device Technology'
        self.base_fields['device_vendor'].label = 'Device Vendor'
        self.base_fields['device_model'].label = 'Device Model'
        self.base_fields['device_type'].label = 'Device Type'
        if 'parent' in self.base_fields:
            self.base_fields['parent'].label = 'Parent IP'
        # self.base_fields['service'].label = 'Services'
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)
        initial = kwargs.setdefault('initial', {})

        super(DeviceForm, self).__init__(*args, **kwargs)

        # setting select menus default values which is by default '---------'
        if not self.request is None:
            # Create instance of 'NocoutUtilsGateway' class
            nocout_utils = NocoutUtilsGateway()
            # print "**********self.fields**********"
            # print self.fields
            # print "**********self.fields**********"
            self.fields['organization'].queryset = nocout_utils.logged_in_user_organizations(self)
        else:
            self.fields['organization'].widget.choices = self.fields['organization'].choices
        self.fields['organization'].widget.choices = self.fields['organization'].choices
        self.fields['organization'].empty_label = "Select"
        # self.fields['parent'].empty_label = "Select"
        if 'parent' in self.fields:
            self.fields['parent'].widget = forms.HiddenInput()
        self.fields['site_instance'].empty_label = "Select"
        self.fields['site_instance'].widget.choices = self.fields['site_instance'].choices
        self.fields['machine'].empty_label = "Select"
        self.fields['machine'].widget.choices = self.fields['machine'].choices
        self.fields['device_technology'].empty_label = "Select"
        self.fields['device_technology'].widget.choices = self.fields['device_technology'].choices
        self.fields['device_vendor'].empty_label = "Select"
        self.fields['device_vendor'].widget.choices = self.fields['device_vendor'].choices
        self.fields['device_model'].empty_label = "Select"
        self.fields['device_model'].widget.choices = self.fields['device_model'].choices
        self.fields['device_type'].empty_label = "Select"
        self.fields['device_type'].widget.choices = self.fields['device_type'].choices
        self.fields['ports'].empty_label = "Select"
        self.fields['ports'].widget.choices = self.fields['ports'].choices
        self.fields['site_instance'].required = True
        self.fields['machine'].required = True
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['country'].required = True
        self.fields['state'].required = True
        self.fields['city'].required = True

        # to redisplay the extra fields form with already filled values we follow these steps:
        # 1. check that device type exist in 'kwargs' or not
        # 2. if 'device type' value exist then fetch extra fields associated with that 'device type'
        # 3. then we recreates text fields corresponding to each field we fetched in step 2
        try:
            if kwargs['data']['device_type']:
                extra_fields = DeviceTypeFields.objects.filter(device_type_id=kwargs['data']['device_type'])
                for extra_field in extra_fields:
                    self.fields[extra_field.field_name] = forms.CharField(label=extra_field.field_display_name)
                    self.fields.update({
                        extra_field.field_name: forms.CharField(widget=forms.TextInput(), required=False,
                                                                label=extra_field.field_display_name, ),
                    })
                    self.fields[extra_field.field_name].widget.attrs['class'] = 'extra'
        except Exception as e:
            logger.info(e.message)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                else:
                    field.widget.attrs['class'] += ' tip-focus form-control'
                    field.widget.attrs['data-toggle'] = 'tooltip'
                    field.widget.attrs['data-placement'] = 'right'
                    field.widget.attrs['title'] = field.help_text
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': ' tip-focus form-control'})
                    field.widget.attrs.update({'data-toggle': 'tooltip'})
                    field.widget.attrs.update({'data-placement': 'right'})
                    field.widget.attrs.update({'title': field.help_text})

    class Meta:
        """
        Meta Information
        """
        model = Device
        if ENABLE_PARENT_FIELDS:
            exclude = ['device_name', 'is_deleted', 'is_added_to_nms', 'is_monitored_on_nms']
        else:
            exclude = ['device_name', 'is_deleted', 'is_added_to_nms', 'is_monitored_on_nms', 'parent', 'parent_type', 'parent_port']
        widgets = {
            'device_group': MultipleToSingleSelectionWidget,
        }

    def clean_latitude(self):
        """
        Latitude field validations
        """
        latitude = self.request.POST.get('latitude') #self.data['latitude']

        is_error = False
        try:
            latitude = float(latitude)
        except Exception, e:
            is_error = True

        if latitude == '' or str(latitude).count('.') > 1 or is_error:
            raise forms.ValidationError("Please enter correct value for latitude.")
        return self.cleaned_data.get('latitude')

    def clean_longitude(self):
        """
        Longitude field validation
        """
        longitude = self.request.POST.get('longitude') #self.data['longitude']
        
        is_error = False
        try:
            longitude = float(longitude)
        except Exception, e:
            is_error = True

        if longitude == '' or str(longitude).count('.') > 1 or is_error:
            raise forms.ValidationError("Please enter correct value for longitude.")
        return self.cleaned_data.get('longitude')

    def clean_device_name(self):
        """
        Device name unique validation
        """
        device_name = self.cleaned_data['device_name']
        devices = Device.objects.filter(device_name=device_name)
        try:
            if self.id:
                devices = devices.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if devices.count() > 0:
            raise ValidationError('This device name is already in use.')
        return device_name

    def clean_ip_address(self):
        """
        IP Address unique validation
        """
        ip_address = self.cleaned_data['ip_address']
        devices = Device.objects.filter(ip_address=ip_address)
        try:
            if self.id:
                devices = devices.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if devices.count() > 0:
            raise ValidationError('This IP address is already in use.')
        return ip_address

    def clean(self):
        """
        Validations for device form
        """
        latitude = self.request.POST.get('latitude')
        longitude = self.request.POST.get('longitude')
        state = self.cleaned_data.get('state')

        # check that device name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            device_name = self.cleaned_data['device_name']
            if not re.match(r'^[A-Za-z0-9\._-]+$', device_name):
                self._errors["device_name"] = ErrorList(
                    [u"Device name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)

        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()

        try:
            is_lat_long_valid = nocout_utils.is_lat_long_in_state(float(latitude), float(longitude), state)
        except Exception, e:
            is_lat_long_valid = False

        if not is_lat_long_valid:
            self._errors["latitude"] = ErrorList(
                [u"Latitude, longitude specified doesn't exist within selected state."])

        return self.cleaned_data


# ********************************** Device Extra Fields Form ***************************************
class DeviceTypeFieldsForm(forms.ModelForm):
    """
    Rendering form for device type fields
    """
    def __init__(self, *args, **kwargs):
        super(DeviceTypeFieldsForm, self).__init__(*args, **kwargs)
        self.fields['device_type'].empty_label = 'Select'
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
        model = DeviceTypeFields
        fields = ('field_name', 'field_display_name', 'device_type')

    def clean_field_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['field_name']
        names = DeviceTypeFields.objects.filter(field_name=name)
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
        Validations for device type fields form
        """
        name = self.cleaned_data.get('field_name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['field_name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


class DeviceTypeFieldsUpdateForm(forms.ModelForm):
    """
    Rendering update form for device type fields
    """
    def __init__(self, *args, **kwargs):
        super(DeviceTypeFieldsUpdateForm, self).__init__(*args, **kwargs)
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
        model = DeviceTypeFields
        fields = ('field_name', 'field_display_name', 'device_type')

    def clean(self):
        """
        Validations for command form
        """
        name = self.cleaned_data.get('field_name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['field_name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


# **************************************** Device Technology ****************************************
class DeviceTechnologyForm(forms.ModelForm):
    """
    Rendering form for device technology
    """
    def __init__(self, *args, **kwargs):
        # removing help text for device_vendors 'select' field
        self.base_fields['device_vendors'].help_text = ''

        super(DeviceTechnologyForm, self).__init__(*args, **kwargs)
        self.fields['device_vendors'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        model = DeviceTechnology
        fields = ('name', 'alias', 'device_vendors')

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = DeviceTechnology.objects.filter(name=name)
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
        Validations for technology form
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


# ****************************************** Device Vendor ******************************************
class DeviceVendorForm(forms.ModelForm):
    """
    Rendering form for device vendor
    """
    def __init__(self, *args, **kwargs):
        # removing help text for device_models 'select' field
        self.base_fields['device_models'].help_text = ''
        super(DeviceVendorForm, self).__init__(*args, **kwargs)

        self.fields['device_models'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        model = DeviceVendor
        fields = ('name', 'alias', 'device_models')

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = DeviceVendor.objects.filter(name=name)
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
        Validations for vendor form
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


# ******************************************* Device Model ******************************************
class DeviceModelForm(forms.ModelForm):
    """
    Rendering form for device model
    """
    def __init__(self, *args, **kwargs):

        # removing help text for device_types 'select' field
        self.base_fields['device_types'].help_text = ''

        super(DeviceModelForm, self).__init__(*args, **kwargs)
        self.fields['device_types'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        model = DeviceModel
        fields = ('name', 'alias', 'device_types')

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = DeviceModel.objects.filter(name=name)
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
        Validations for model form
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


# ******************************************* Device Type *******************************************
class BaseDeviceTypeServiceFormset(BaseInlineFormSet):
    """
    Custome Inline formest.
    """
    def __init__(self, *args, **kwargs):
        super(BaseDeviceTypeServiceFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            choices_list = [(service.id, '%s(%s)' % (service.alias, service.name)) for service in Service.objects.all()]
            form.fields['service'].choices = choices_list
            form.fields['parameter'].empty_label = 'Select'

    def clean(self):
        for form in self.forms:
            if not 'service' in form.cleaned_data.keys():
                raise forms.ValidationError('This field is required.')

class DeviceTypeForm(forms.ModelForm):
    """
    Rendering form for device type
    """
    AGENT_TAG = (
        ('', 'Select'),
        ('snmp-v1|snmp', 'SNMP-V1'),
        ('snmp-v2|snmp', 'SNMP-V2'),
        ('snmp-v3|snmp', 'SNMP-V3'),
        ('snmp-v3|priv|snmp', 'SNMP-V3-PRIV'),
        ('ping', 'Ping')
    )
    agent_tag = forms.TypedChoiceField(choices=AGENT_TAG, required=True)

    def __init__(self, *args, **kwargs):
        # removing help text for device_port 'select' field
        self.base_fields['device_port'].help_text = ''
        # removing help text for service 'select' field
        # self.base_fields['service'].help_text = ''

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(DeviceTypeForm, self).__init__(*args, **kwargs)
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
        model = DeviceType
        exclude = ('service',)

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = DeviceType.objects.filter(name=name)
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
        Validations for device type form
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
           'service': forms.Select(attrs= {'class' : 'form-control'}),
           'parameter': forms.Select(attrs= {'class' : 'form-control'}),
           'critical': forms.TextInput(attrs= {'class' : 'form-control'}),
           'warning': forms.TextInput(attrs= {'class' : 'form-control'}),
           'service_data_sources': forms.Select(attrs= {'class' : 'form-control'}),
    }
DeviceTypeServiceCreateFormset = inlineformset_factory(DeviceType, DeviceTypeService, formset=BaseDeviceTypeServiceFormset,
    fields=('service', 'parameter'), extra=1, widgets=widgets, can_delete=True)
DeviceTypeServiceUpdateFormset = inlineformset_factory(DeviceType, DeviceTypeService, formset=BaseDeviceTypeServiceFormset,
    fields=('service', 'parameter'), extra=0, widgets=widgets, can_delete=True)

# ******************************************* Device Type *******************************************
class DevicePortForm(forms.ModelForm):
    """
    Rendering form for device port
    """
    def __init__(self, *args, **kwargs):
        super(DevicePortForm, self).__init__(*args, **kwargs)

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        model = DevicePort
        fields = '__all__'

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = DevicePort.objects.filter(name=name)
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
        Validations for command form
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


class DeviceFrequencyForm(forms.ModelForm):
    """
    Rendering form for device frequencies
    """
    def __init__(self, *args, **kwargs):

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(DeviceFrequencyForm, self).__init__(*args, **kwargs)
        self.fields['color_hex_value'].widget.attrs.update({'value':"rgba(45,14,255,0.58)",'class':'colorpicker',\
                                                            'data-color-format':'rgba' })
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})

    class Meta:
        """
        Meta Information
        """
        model = DeviceFrequency
        fields = '__all__'

    def clean_value(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['value']
        names = DeviceFrequency.objects.filter(value=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This value is already in use.')
        return name

    def clean(self):
        """
        Validations for command form
        """
        name = self.cleaned_data.get('value')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[0-9\.]+$', name):
                self._errors['value'] = ErrorList(
                    [u"Value must be alphanumeric & can only contains .(dot)"])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


# ******************************************* Country *******************************************
class CountryForm(forms.ModelForm):
    """
    Rendering form for country
    """
    def __init__(self, *args, **kwargs):
        # removing help text for device_models 'select' field
        self.base_fields['country_name'].help_text = ''
        super(CountryForm, self).__init__(*args, **kwargs)

        self.fields['country_name'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        model = Country
        fields = ('country_name',)


# ******************************************* Country *******************************************
class StateForm(forms.ModelForm):
    """
    Rendering form for country
    """
    def __init__(self, *args, **kwargs):
        # removing help text for device_models 'select' field
        self.base_fields['state_name'].help_text = ''
        super(StateForm, self).__init__(*args, **kwargs)

        self.fields['state_name'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        model = State
        fields = ('country', 'state_name',)


# ******************************************* Country *******************************************
class CityForm(forms.ModelForm):
    """
    Rendering form for city
    """
    def __init__(self, *args, **kwargs):
        self.base_fields['city_name'].help_text = ''
        super(CityForm, self).__init__(*args, **kwargs)

        self.fields['city_name'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        model = City
        fields = ('state', 'city_name',)


#**************************************** GIS Wizard Forms ****************************************#

class WizardDeviceTypeForm(DeviceTypeForm):
    """
    Class Based View Base Station Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        super(WizardDeviceTypeForm, self).__init__(*args, **kwargs)

        self.fields.pop('service')

    class Meta:
        """
        Meta Information
        """
        model = DeviceType
        fields = ('name', 'alias', 'device_port', 'service', 'packets', 'timeout', 'normal_check_interval',
            'rta_warning', 'rta_critical', 'pl_warning', 'pl_critical', 'agent_tag', 'device_icon', 'device_gmap_icon',
        )


#**************************************** GIS Device Type Service Wizard Forms ****************************************#
class BaseDTSDataSourceFormset(BaseInlineFormSet):
    """
    Custome Inline formest.
    """
    def __init__(self, *args, **kwargs):

        super(BaseDTSDataSourceFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            choices_list = [(sds.id, '%s(%s)' % (sds.alias, sds.name)) for sds in ServiceDataSource.objects.all()]
            form.fields['service_data_sources'].choices = choices_list

    def clean(self):
        for form in self.forms:
            if not 'service_data_sources' in form.cleaned_data.keys():
                raise forms.ValidationError('This field is required.')

class WizardDeviceTypeServiceForm(forms.ModelForm):
    """
    Rendering form for device type service
    """

    def __init__(self, *args, **kwargs):
        # removing help text for service 'select' field
        self.base_fields['service'].help_text = ''
        self.base_fields['service'].empty_label = 'Select'
        # removing help text for service 'select' field
        self.base_fields['parameter'].help_text = ''
        self.base_fields['parameter'].help_text = 'Select'

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(WizardDeviceTypeServiceForm, self).__init__(*args, **kwargs)
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
        model = DeviceTypeService
        exclude = ('device_type', 'service_data_sources',)

widgets = {
           'critical': forms.TextInput(attrs= {'class' : 'form-control'}),
           'warning': forms.TextInput(attrs= {'class' : 'form-control'}),
           'service_data_sources': forms.Select(attrs= {'class' : 'form-control'}),
    }

DeviceTypeServiceDataSourceCreateFormset = inlineformset_factory(DeviceTypeService, DeviceTypeServiceDataSource,
    formset=BaseDTSDataSourceFormset, extra=1, widgets=widgets, can_delete=True, fields="__all__")
DeviceTypeServiceDataSourceUpdateFormset = inlineformset_factory(DeviceTypeService, DeviceTypeServiceDataSource,
    formset=BaseDTSDataSourceFormset, extra=0, widgets=widgets, can_delete=True, fields="__all__")


# **************************** GIS Inventory Excel Download Update ******************************
class DeviceSyncHistoryEditForm(forms.ModelForm):
    """
    Class Based View DeviceSyncHistory Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        super(DeviceSyncHistoryEditForm, self).__init__(*args, **kwargs)
        self.fields['sync_by'].widget.attrs['readonly'] = True
        self.fields['message'].widget.attrs['readonly'] = True
        self.fields['added_on'].widget.attrs['readonly'] = True
        self.fields['completed_on'].widget.attrs['readonly'] = True

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
        model = DeviceSyncHistory
        fields = ['message', 'description', 'sync_by', 'added_on', 'completed_on']

