from django import forms
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType, Country, State, City
from nocout.widgets import MultipleToSingleSelectionWidget, IntReturnModelChoiceField
from device.models import DeviceTypeFields


# *************************************** Device Form ***********************************************


class DeviceForm(forms.ModelForm):
    device_technology = IntReturnModelChoiceField(queryset=DeviceTechnology.objects.all(),
                                                  required=False)
    device_vendor = IntReturnModelChoiceField(queryset=DeviceVendor.objects.all(),
                                              required=False)
    device_model = IntReturnModelChoiceField(queryset=DeviceModel.objects.all(),
                                             required=False)
    device_type = IntReturnModelChoiceField(queryset=DeviceType.objects.all(),
                                            required=False)
    country = IntReturnModelChoiceField(queryset=Country.objects.all(),
                                        required=False)
    state = IntReturnModelChoiceField(queryset=State.objects.all(),
                                      required=False)
    city = IntReturnModelChoiceField(queryset=City.objects.all(),
                                     required=False)

    def __init__(self, *args, **kwargs):
        # setting foreign keys field label
        self.base_fields['device_group'].label = 'Device Group'
        self.base_fields['site_instance'].label = 'Site Instance'
        self.base_fields['device_technology'].label = 'Device Technology'
        self.base_fields['device_vendor'].label = 'Device Vendor'
        self.base_fields['device_model'].label = 'Device Model'
        self.base_fields['device_type'].label = 'Device Type'

        initial = kwargs.setdefault('initial', {})
        initial['device_group'] = kwargs['instance'].device_group.values_list('pk', flat=True)[0] if kwargs[
            'instance'] else []

        super(DeviceForm, self).__init__(*args, **kwargs)

        # setting select menus default values which is by default '---------'
        self.fields['site_instance'].empty_label = "Select Site Instance...."
        self.fields['site_instance'].widget.choices = self.fields['site_instance'].choices
        self.fields['device_technology'].empty_label = "Select Device Technology...."
        self.fields['device_technology'].widget.choices = self.fields['device_technology'].choices
        self.fields['device_vendor'].empty_label = "Select Device Vendor...."
        self.fields['device_vendor'].widget.choices = self.fields['device_vendor'].choices
        self.fields['device_model'].empty_label = "Select Device Model...."
        self.fields['device_model'].widget.choices = self.fields['device_model'].choices
        self.fields['device_type'].empty_label = "Select Device Type...."
        self.fields['device_type'].widget.choices = self.fields['device_type'].choices
        self.fields['country'].empty_label = "Select Country...."
        self.fields['country'].widget.choices = self.fields['country'].choices
        self.fields['state'].empty_label = "Select State...."
        self.fields['state'].widget.choices = self.fields['state'].choices
        self.fields['city'].empty_label = "Select City...."
        self.fields['city'].widget.choices = self.fields['city'].choices

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
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Device
        exclude = ['is_deleted']
        widgets = {
            'device_group': MultipleToSingleSelectionWidget,
        }


# ********************************** Device Extra Fields Form ***************************************


class DeviceTypeFieldsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceTypeFieldsForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
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
                field.widget.attrs['class'] += ' form-control'
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
                field.widget.attrs['class'] += ' form-control'
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
                field.widget.attrs['class'] += ' form-control'
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
                field.widget.attrs['class'] += ' form-control'
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
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = DeviceType
        fields = ('name', 'alias')
