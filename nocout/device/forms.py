from django import forms
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType, \
    Country, State, City, StateGeoInfo, DevicePort, DeviceFrequency
from django.core.exceptions import ValidationError
from nocout.widgets import MultipleToSingleSelectionWidget, IntReturnModelChoiceField
from device.models import DeviceTypeFields
# import pyproj
# commented because of goes package is not supported for python 2.7 on centos 6.5
# from shapely.geometry import Polygon, Point
# from shapely.ops import transform
# commented because of goes package is not supported for python 2.7 on centos 6.5
from functools import partial
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
    country = IntReturnModelChoiceField(queryset=Country.objects.all(),
                                        required=False)
    state = IntReturnModelChoiceField(queryset=State.objects.all(),
                                      required=False)
    city = IntReturnModelChoiceField(queryset=City.objects.all(),
                                     required=False)
    #latitude = forms.CharField( widget=forms.TextInput(attrs={'type':'text'}))
    #longitude = forms.CharField( widget=forms.TextInput(attrs={'type':'text'}))

    def __init__(self, *args, **kwargs):
        # setting foreign keys field label
        self.base_fields['site_instance'].label = 'Site Instance'
        self.base_fields['machine'].label = 'Machine'
        self.base_fields['device_technology'].label = 'Device Technology'
        self.base_fields['device_vendor'].label = 'Device Vendor'
        self.base_fields['device_model'].label = 'Device Model'
        self.base_fields['device_type'].label = 'Device Type'
        # self.base_fields['service'].label = 'Services'
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)
        initial = kwargs.setdefault('initial', {})

        super(DeviceForm, self).__init__(*args, **kwargs)

        # setting select menus default values which is by default '---------'
        self.fields['organization'].widget.choices = self.fields['organization'].choices
        self.fields['organization'].empty_label = "Select"
        self.fields['parent'].empty_label = "Select"
        self.fields['parent'].widget.choices = self.fields['parent'].choices
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
        self.fields['country'].empty_label = "Select"
        self.fields['country'].widget.choices = self.fields['country'].choices
        self.fields['state'].empty_label = "Select"
        self.fields['state'].widget.choices = self.fields['state'].choices
        self.fields['city'].empty_label = "Select"
        self.fields['city'].widget.choices = self.fields['city'].choices
        self.fields['site_instance'].required = True
        self.fields['machine'].required = True
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['country'].required = True
        self.fields['state'].required = True
        self.fields['city'].required = True

        #self.fields['latitude'].widget.attrs['data-mask'] = '99.99999999999999999999'
        #self.fields['longitude'].widget.attrs['data-mask'] = '99.99999999999999999999'

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
        model = Device
        exclude = ['is_deleted', 'is_added_to_nms', 'is_monitored_on_nms']
        widgets = {
            'device_group': MultipleToSingleSelectionWidget,
        }

    def clean_latitude(self):
        """
        Latitude field validations
        """
        latitude = self.data['latitude']
        if latitude != '' and len(latitude) > 2 and latitude[2] != '.':
            raise forms.ValidationError("Please enter correct value for latitude.")
        return self.cleaned_data.get('latitude')

    def clean_longitude(self):
        """
        Longitude field validation
        """
        longitude = self.data['longitude']
        if longitude != '' and len(longitude) > 2 and longitude[2] != '.':
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
        latitude = self.cleaned_data.get('latitude')
        longitude = self.cleaned_data.get('longitude')
        state = self.cleaned_data.get('state')

        # check that device name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            device_name = self.cleaned_data['device_name']
            if not re.match(r'^[A-Za-z0-9\._-]+$', device_name):
                self._errors["device_name"] = ErrorList(
                    [u"Device name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)

        #commented because of goes package is not supported for python 2.7 on centos 6.5
        # check whether lat log lies in state co-ordinates or not
        # if latitude and longitude and state:
        #     project = partial(
        #         pyproj.transform,
        #         pyproj.Proj(init='epsg:4326'),
        #         pyproj.Proj(
        #             '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs'))
        #
        #     state_geo_info = StateGeoInfo.objects.filter(state_id=state)
        #     state_lat_longs = list()
        #     for geo_info in state_geo_info:
        #         temp_lat_longs = list()
        #         temp_lat_longs.append(geo_info.longitude)
        #         temp_lat_longs.append(geo_info.latitude)
        #         state_lat_longs.append(temp_lat_longs)
        #
        #     poly = Polygon(tuple(state_lat_longs))
        #     point = Point(longitude, latitude)
        #
        #     # Translate to spherical Mercator or Google projection
        #     poly_g = transform(project, poly)
        #     p1_g = transform(project, point)
        #     if not poly_g.contains(p1_g):
        #         self._errors["latitude"] = ErrorList(
        #             [u"Latitude, longitude specified doesn't exist within selected state."])
        #commented because of goes package is not supported for python 2.7 on centos 6.5 @TODO: check another package
        # print self.cleaned_data
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
class DeviceTypeForm(forms.ModelForm):
    """
    Rendering form for device type
    """
    AGENT_TAG = (
        ('', 'Select'),
        ('snmp', 'SNMP'),
        ('ping', 'Ping')
    )
    agent_tag = forms.TypedChoiceField(choices=AGENT_TAG, required=True)

    def __init__(self, *args, **kwargs):
        # removing help text for device_port 'select' field
        self.base_fields['device_port'].help_text = ''
        # removing help text for service 'select' field
        self.base_fields['service'].help_text = ''

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
        self.fields['color_hex_value'].widget.attrs.update({'value':"rgb(45,14,255,0.58)",'class':'colorpicker',\
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
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['value'] = ErrorList(
                    [u"Value must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data
