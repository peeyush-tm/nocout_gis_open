import json
import copy
from django.views.generic.base import View
from django.http import HttpResponse
from device.models import Device, DeviceType, DeviceVendor,\
    DeviceTechnology, DeviceModel
from device_group.models import DeviceGroup

class DeviceGetFilters(View):
    """
    Getting all the info for all the devices

    """

    def get(self, request):
        """
        Getting all the devices

        Args:

        Returns:

        """

        device_dict = {}
        self.result = {
            "success": 1,
            "message": "Device Data",
            "data": {
                "meta": None,
                "objects": []
            }
        }
        device_dict = self.get_device_objects()
        self.result.get('data').get('objects').extend(device_dict)
        device_dict = self.get_device_group_objects()
        self.result.get('data').get('objects').append(device_dict)
        device_dict = self.get_device_type_objects()
        self.result.get('data').get('objects').append(device_dict)
        device_dict = self.get_device_technology_objects()
        self.result.get('data').get('objects').append(device_dict)
        device_dict = self.get_device_vendor_objects()
        self.result.get('data').get('objects').append(device_dict)
        return HttpResponse(json.dumps(self.result))


    def get_device_objects(self, **kwargs):
        result_list = []
        device_attribute_dict = {
            "device_name": [],
            "device_alias": [],
            "ip_address": [],
            "mac_address": [],
            "host_state": [],
            "city": [],
            "state": []
        }
        base_dict = {
            "key": None,
            "title": None,
            "field_type": None,
            "element_type": None,
            "values": []
        }
        attr_list = [
            {"device_name": "Device Name"},
            {"device_alias": "Device Alias"},
            {"ip_address": "IP Address"},
            {"mac_address": "Mac Address"},
            {"host_state": "Host State"},
            {"city": "City"},
            {"state": "State"}
        ]
        obj_list = Device.objects.all().order_by('id').values()
        for obj in obj_list:
            device_attribute_dict.get('device_name').append({
                "id": obj.get('id'),
                "value": obj.get('device_name')
            })
            device_attribute_dict.get('device_alias').append({
                "id": obj.get('id'),
                "value": obj.get('device_alias')
            })
            device_attribute_dict.get('ip_address').append({
                "id": obj.get('id'),
                "value": obj.get('ip_address')
            })
            device_attribute_dict.get('mac_address').append({
                "id": obj.get('id'),
                "value": obj.get('mac_address')
            })
            device_attribute_dict.get('host_state').append({
                "id": obj.get('id'),
                "value": obj.get('host_state')
            })
            device_attribute_dict.get('city').append({
                "id": obj.get('id'),
                "value": obj.get('city')
            })
            device_attribute_dict.get('state').append({
                "id": obj.get('id'),
                "value": obj.get('state')
            })
            
        for attr in attr_list:
            base_dict = dict(
                key=attr.keys()[0],
                title=attr.values()[0],
                field_type="string",
                element_type="multiselect",
                values=device_attribute_dict.get(attr.keys()[0])
            )
            result_list.append(base_dict)

        return result_list

    def get_device_group_objects(self, **kwargs):
        base_dict = {
            "key": "device_group",
            "title": "Device Group",
            "field_type": "string",
            "element_type": "multiselect",
            "values": []
        }

        obj_list = DeviceGroup.objects.all().order_by('id')
        for obj in obj_list:
            value_dict = dict(
                id=obj.id,
                value=obj.name
            )
            base_dict.get('values').append(value_dict)

        return base_dict

    def get_device_type_objects(self, **kwargs):
        base_dict = {
            "key": "device_type",
            "title": "Device Type",
            "field_type": "string",
            "element_type": "multiselect",
            "values": []
        }

        obj_list = DeviceType.objects.all().order_by('id')
        for obj in obj_list:
            value_dict = dict(
                id=obj.id,
                value=obj.name
            )
            base_dict.get('values').append(value_dict)

        return base_dict


    def get_device_technology_objects(self, **kwargs):
        base_dict = {
            "key": "device_technology",
            "title": "Device Technology",
            "field_type": "string",
            "element_type": "multiselect",
            "values": []
        }

        obj_list = DeviceTechnology.objects.all().order_by('id')
        for obj in obj_list:
            value_dict = dict(
                id=obj.id,
                value=obj.name
            )
            base_dict.get('values').append(value_dict)

        return base_dict


    def get_device_vendor_objects(self, **kwargs):
        base_dict = {
            "key": "device_vendor",
            "title": "Device Vendor",
            "field_type": "string",
            "element_type": "multiselect",
            "values": []
        }

        obj_list = DeviceVendor.objects.all().order_by('id')
        for obj in obj_list:
            value_dict = dict(
                id=obj.id,
                value=obj.name
            )
            base_dict.get('values').append(value_dict)

        return base_dict