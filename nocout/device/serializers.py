from device.models import Device
from rest_framework import serializers


class DeviceParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'device_name', 'device_alias', 'ip_address')


class DeviceInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
