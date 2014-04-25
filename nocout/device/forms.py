from django import forms
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType, DeviceTypeFields
from nocout.widgets import MultipleToSingleSelectionWidget, IntReturnModelChoiceField


# *************************************** Device Form *********************************************


class DeviceForm(forms.ModelForm):
        
    device_technology = IntReturnModelChoiceField(queryset=DeviceTechnology.objects.all(), 
                                               required=False
                                               )
    device_vendor = IntReturnModelChoiceField(queryset=DeviceVendor.objects.all(),
                                       required=False
                                       )
    device_model = IntReturnModelChoiceField(queryset=DeviceModel.objects.all(),
                                     required=False
                                     )
    device_type = IntReturnModelChoiceField(queryset=DeviceType.objects.all(),
                                    required=False
                                    )
    
    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.base_fields['device_group'].help_text = ""
        self.base_fields['service'].help_text = ""
        
    class Meta:
        model = Device
        fields = ('device_name', 'device_alias', 'instance', 'device_group', 'parent', 'device_technology', 'device_vendor', 'device_model',
                  'device_type', 'service', 'ip_address', 'mac_address', 'netmask', 'gateway', 'dhcp_state', 'host_priority', 'host_state',
                  'address', 'city', 'state', 'timezone', 'latitude', 'longitude', 'description'
        )
        widgets = {
            'device_group': MultipleToSingleSelectionWidget,
        }
        '''
        widgets = {
                   'device_name': forms.TextInput(attrs={'style': 'width:400px'}),
                   'device_alias': forms.TextInput(attrs={'style': 'width:400px'}),
                   'ip_address': forms.TextInput(attrs={'style': 'width:400px'}),
                   'mac_address': forms.TextInput(attrs={'style': 'width:400px'}),
                   'netmask': forms.TextInput(attrs={'style': 'width:400px'}),
                   'gateway': forms.TextInput(attrs={'style': 'width:400px'}),
                   'city': forms.TextInput(attrs={'style': 'width:400px'}),
                   'state': forms.TextInput(attrs={'style': 'width:400px'}),
                   'timezone': forms.TextInput(attrs={'style': 'width:400px'}),
                   'latitude': forms.TextInput(attrs={'style': 'width:400px'}),
                   'longitude': forms.TextInput(attrs={'style': 'width:400px'}),
                   'address': forms.Textarea(attrs={'style': 'width:400px'}),
                   'description': forms.Textarea(attrs={'style': 'width:400px'}),
                   'parent': forms.Select(attrs={'style': 'width:400px'}),
                   'instance': forms.Select(attrs={'style': 'width:400px'}),
                   'dhcp_state': forms.Select(attrs={'style': 'width:400px'}),
                   'host_priority': forms.Select(attrs={'style': 'width:400px'}),
                   'host_state': forms.Select(attrs={'style': 'width:400px'}),
                   'device_group': MultipleToSingleSelectionWidget(attrs={'style': 'width:400px'}),
                   'service': forms.SelectMultiple(attrs={'style': 'width:400px'})
        }
        '''


# ********************************** Device Extra Fields Form *******************************************        


class DeviceTypeFieldsForm(forms.ModelForm):
    
    class Meta:
        model = DeviceTypeFields
        fields = ('field_name', 'field_display_name', 'device_type')


class DeviceTypeFieldsUpdateForm(forms.ModelForm):
    
    class Meta:
        model = DeviceTypeFields
        fields = ('field_name', 'field_display_name')
        
        
# **************************************** Device Technology *******************************************


class DeviceTechnologyForm(forms.ModelForm):
    
    class Meta:
        model = DeviceTechnology
        fields = ('name', 'alias', 'device_vendors')
        
        
# **************************************** Device Vendor *******************************************


class DeviceVendorForm(forms.ModelForm):
    
    class Meta:
        model = DeviceVendor
        fields = ('name', 'alias', 'device_models')



        
        