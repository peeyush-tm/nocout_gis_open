from django import forms
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType, \
    Country, State, City, StateGeoInfo, DevicePort
from nocout.widgets import MultipleToSingleSelectionWidget, IntReturnModelChoiceField
from device.models import DeviceTypeFields
import pyproj
from shapely.geometry import Polygon, Point
from shapely.ops import transform
from functools import partial
from django.forms.util import ErrorList


# *************************************** Device Form ***********************************************
class DeviceForm(forms.ModelForm):
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
        self.base_fields['device_technology'].label = 'Device Technology'
        self.base_fields['device_vendor'].label = 'Device Vendor'
        self.base_fields['device_model'].label = 'Device Model'
        self.base_fields['device_type'].label = 'Device Type'
        # self.base_fields['service'].label = 'Services'

        initial = kwargs.setdefault('initial', {})

        super(DeviceForm, self).__init__(*args, **kwargs)

        # setting select menus default values which is by default '---------'
        self.fields['organization'].widget.choices = self.fields['organization'].choices
        self.fields['organization'].empty_label = "Select"
        self.fields['parent'].empty_label = "Select"
        self.fields['parent'].widget.choices = self.fields['parent'].choices
        self.fields['site_instance'].empty_label = "Select"
        self.fields['site_instance'].widget.choices = self.fields['site_instance'].choices
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
        except:
            pass
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
        model = Device
        exclude = ['is_deleted', 'is_added_to_nms', 'is_monitored_on_nms']
        widgets = {
            'device_group': MultipleToSingleSelectionWidget,
        }

    def clean_latitude(self):
        latitude = self.data['latitude']
        if latitude!='' and len(latitude)>2 and latitude[2] != '.':
            raise forms.ValidationError("Please enter correct value for latitude.")
        return self.cleaned_data.get('latitude')

    def clean_longitude(self):
        longitude = self.data['longitude']
        if longitude!='' and len(longitude)>2 and longitude[2] != '.':
            raise forms.ValidationError("Please enter correct value for longitude.")
        return self.cleaned_data.get('longitude')

    def clean(self):
        latitude = self.cleaned_data.get('latitude')
        longitude = self.cleaned_data.get('longitude')
        state = self.cleaned_data.get('state')

        if latitude and longitude and state:
            project = partial(
            pyproj.transform,
            pyproj.Proj(init='epsg:4326'),
            pyproj.Proj('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs'))

            state_geo_info = StateGeoInfo.objects.filter(state_id=state)
            state_lat_longs = []
            for geo_info in state_geo_info:
                temp_lat_longs = []
                temp_lat_longs.append(geo_info.longitude)
                temp_lat_longs.append(geo_info.latitude)
                state_lat_longs.append(temp_lat_longs)

            poly = Polygon(tuple(state_lat_longs))
            point = Point(longitude, latitude)

            # Translate to spherical Mercator or Google projection
            poly_g = transform(project, poly)
            p1_g = transform(project, point)
            if not poly_g.contains(p1_g):
                self._errors["latitude"] = ErrorList([u"Latitude, longitude specified doesn't exist within selected state."])
        print self.cleaned_data
        return self.cleaned_data


# ********************************** Device Extra Fields Form ***************************************
class DeviceTypeFieldsForm(forms.ModelForm):
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
        model = DeviceTypeFields
        fields = ('field_name', 'field_display_name', 'device_type')


class DeviceTypeFieldsUpdateForm(forms.ModelForm):
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
        model = DeviceTypeFields
        fields = ('field_name', 'field_display_name', 'device_type')


# **************************************** Device Technology ****************************************
class DeviceTechnologyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceTechnologyForm, self).__init__(*args, **kwargs)
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
        model = DeviceTechnology
        fields = ('name', 'alias', 'device_vendors')


# ****************************************** Device Vendor ******************************************
class DeviceVendorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceVendorForm, self).__init__(*args, **kwargs)
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
        model = DeviceVendor
        fields = ('name', 'alias', 'device_models')


# ******************************************* Device Model ******************************************
class DeviceModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceModelForm, self).__init__(*args, **kwargs)
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
        model = DeviceModel
        fields = ('name', 'alias', 'device_types')


# ******************************************* Device Type *******************************************
class DeviceTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
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
        model = DeviceType


# ******************************************* Device Type *******************************************
class DevicePortForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DevicePortForm, self).__init__(*args, **kwargs)
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
        model = DevicePort
