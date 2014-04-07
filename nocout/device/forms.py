from django import forms
from device.models import Device

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ('device_name', 'device_alias', 'instance', 'device_group', 'parent', 'device_technology', 'device_vendor', 'device_model',
                  'device_type', 'service', 'ip_address', 'mac_address', 'netmask', 'gateway', 'dhcp_state', 'host_priority', 'host_state',
                  'address', 'city', 'state', 'timezone', 'latitude', 'longitude', 'description'
                  )