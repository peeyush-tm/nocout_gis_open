import operator
import copy
import ast
import json
from django.db.models import Q
from django.views.generic.base import View
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from device.models import Device, DeviceType, DeviceVendor,\
    DeviceTechnology, DeviceModel, Inventory
from device_group.models import DeviceGroup

class DeviceGetFilters(View):
    """
    Getting all the info for all the devices,
    to be populated into search filters drop downs

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
            "element_type": "radio",
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


class DeviceSetFilters(View):
    """
    Returning values matched to search filters
    criterion
    """

    def get(self, request):
        """
        Get the values for filters

        Args:

        Returns:

        """

        req_params = request.GET
        #Get the host-ip
        host_ip = request.META['SERVER_NAME']
        filters = {}
        device_attribs = {}
        device_object_list = []
        #Result dict prototype
        self.result = {
            "success": 0,
            "message": "No Device Data",
            "data": {
                "meta": None,
                "objects": None
            }
        }
        if req_params.get('filters') is not None:
            filters = ast.literal_eval(req_params.get('filters'))

        #storing all filter, name/value, pairs in one big dict
        filters = {attr.get('field'): attr.get('value') for attr in filters}

        if 'device_group' in filters.iterkeys():
            device_gp_list = self.get_model_queryset(
                DeviceGroup,
                'id',
                field_list=filters.get('device_group')
            )

            device_id_list = self.inventory_model_queryset(
                Inventory,
                'device_id',
                field_list=device_gp_list
            )
            device_attribs.update({
                "device_id_list": device_id_list
            })

        if 'device_technology' in filters.iterkeys():
            device_attribs.update({
            "device_technology": filters.get('device_technology')
        })

        if 'device_vendor' in filters.iterkeys():
            device_attribs.update({
            "device_vendor": filters.get('device_vendor')
        })

        if 'device_model' in filters.iterkeys():
            device_attribs.update({
            "device_model": filters.get('device_model')
        })

        if 'city' in filters.iterkeys():
            device_attribs.update({
            "city_list": filters.get('city')
        })

        if 'state' in filters.iterkeys():
            device_attribs.update({
            "state_list": filters.get('state')
        })

        device_object_list = self.device_model_queryset(
            Device,
            'device_name',
            field_attribs=device_attribs
        )

        device_object_list = self.get_master(device_object_list)

        device_m_s_info = self.get_master_slave_pairs(
            device_object_list,
            show_link=1,
            host_ip=host_ip
        )

        if len(device_m_s_info.get('children')):
            self.result.update({
                "success": 1,
                "message": "Device Data",
                "data": {
                    "meta": device_m_s_info.pop('meta'),
                    "objects": device_m_s_info
                }
            })
            return HttpResponse(json.dumps(self.result))
        else:
            return HttpResponse(json.dumps(self.result))

    def get_model_queryset(self, model_class, field_name, **kwargs):
        q_list = []
        obj_attr_list = []
        f = operator.attrgetter(field_name)
        if kwargs.get('field_list') is not None:
            for attr in kwargs.get('field_list'):
                q_list.append(Q(pk=attr))
            obj_list = model_class.objects.filter(reduce(operator.or_, q_list))
            for o in obj_list:
                obj_attr_list.append(f(o))
        else:
            obj_attr_list = model_class.objects.all().values('id', 'name')

        return obj_attr_list

    def inventory_model_queryset(self, model_class, field_name, **kwargs):
        q_list = []
        obj_attr_list = []
        f = operator.attrgetter(field_name)
        for attr in kwargs.get('field_list'):
            q_list.append(Q(device_group_id=attr))

        obj_list = model_class.objects.filter(reduce(operator.or_, q_list))
        for o in obj_list:
            obj_attr_list.append(f(o))

        return obj_attr_list

    def device_model_queryset(self, model_class, field_name, **kwargs):
        q_list = []
        reduce_q_list = []
        final_predicate_list = []
        obj_attr_list = []
        obj_list = []
        f = operator.attrgetter(field_name)
        device_id_list = kwargs.get('field_attribs').get('device_id_list', [])
        device_technology = kwargs.get('field_attribs').get('device_technology', [])
        device_vendor = kwargs.get('field_attribs').get('device_vendor', [])
        device_model = kwargs.get('field_attribs').get('device_model', [])
        city_list = kwargs.get('field_attribs').get('city_list', [])
        state_list = kwargs.get('field_attribs').get('state_list', [])

        if len(device_id_list):
            for _id in device_id_list:
                q_list.append(Q(pk=_id))
        if len(device_technology):
            for _id in device_technology:
                q_list.append(Q(device_technology=_id))
        if len(device_vendor):
            for _id in device_vendor:
                q_list.append(Q(device_vendor=_id))
        if len(device_model):
            for _id in device_model:
                q_list.append(Q(device_model=_id))
        if len(city_list):
            for city in city_list:
                q_list.append(Q(city=city.strip()))
        if len(state_list):
            for state in state_list:
                q_list.append(Q(state=state.strip()))
        if len(q_list):
            reduce_q_list = reduce(operator.or_, q_list)

        if len(reduce_q_list):
            obj_list = Device.objects.filter(reduce_q_list)

        return obj_list

    def get_master_slave_pairs(self, device_object_list, **kwargs):
        device_technology_info = {}
        device_vendor_info = {}
        device_model_info = {}
        device_type_info = {}
        device_info = {}
        device_info_list = []
        device_technology_info = self.get_model_queryset(
            DeviceTechnology,
            'name'
        )
        device_technology_info = {x.get('id'): x.get('name') \
                                for x in device_technology_info}

        device_vendor_info = self.get_model_queryset(
            DeviceVendor,
            'name'
        )
        device_vendor_info = {x.get('id'): x.get('name') \
                                for x in device_vendor_info}

        device_model_info = self.get_model_queryset(
            DeviceModel,
            'name'
        )
        device_model_info = {x.get('id'): x.get('name') \
                                for x in device_model_info}

        device_type_info = self.get_model_queryset(
            DeviceType,
            'name'
        )
        device_type_info = {x.get('id'): x.get('name') \
                                for x in device_type_info}
        try:
            for obj in device_object_list:
                device_info = {
                        "id": obj.id,
                        "name": obj.device_name,
                        "alias": obj.device_alias,
                        "device_type": device_type_info.get(obj.device_type),
                        "mac": obj.mac_address,
                        "current_state": obj.host_state,
                        "vendor": device_vendor_info.get(obj.device_vendor),
                        "model": device_model_info.get(obj.device_model),
                        "technology": device_technology_info.get(obj.device_technology),
                        "parent_id": obj.parent_id,
                        "lat": obj.latitude,
                        "lon": obj.longitude,
                        "markerUrl": "http://192.168.0.19:8000/static/img/marker/slave03.png",
                        "perf": "75%",
                        "ip": obj.ip_address,
                        "otherDetail": "No Detail",
                        "city": obj.city,
                        "state": obj.state
                    }
                device_info_list.append(device_info)
        except AttributeError, error:
            print "Device Info Key Error"
            print error.message
            raise
        #Prototype for device dict
        device_stats_dict = {
            "id": "root node",
            "name": "Root Site Instance",
            "data": {
                "$type": "none"
            },
            "children": []
        }
        #Master-slave pairs based on `parent_id` and `device_id`
        for outer in device_info_list:
            master = copy.deepcopy(outer)
            master.update(
                {
                "showLink": kwargs.get('show_link'),
                "children": []
                }
            )
            #dict to store master device info
            master = {
                "id": master.pop('id'),
                "parent_id": master.pop('parent_id'),
                "name": master.pop('name'),
                "children": master.pop('children'),
                "data": master
            }
            for inner in device_info_list:
                if inner.get('parent_id') == outer.get('id'):
                    slave = copy.deepcopy(inner)
                    slave.update(
                        {
                        "linkColor": "green",
                        "children": []
                        }
                    )
                    #dict to store slave device info
                    slave = {
                        "id": slave.pop('id'),
                        "name": slave.pop('name'),
                        "parent_id": slave.pop('parent_id'),
                        "children": slave.pop('children'),
                        "data": slave
                    }
                    master.pop('parent_id', None)
                    slave.pop('parent_id', None)
                    master.get('children').append(slave)
                    device_stats_dict.get('children').append(master)
        device_stats_dict.update({
            "meta": {
                "total_count": None,
                "limit": None
            }
        })
        return device_stats_dict

    def get_master(self, device_object_list):
        master_object = None
        master_object_list = []
        device_object_list = list(device_object_list)
        if len(device_object_list) == 0:
            return device_object_list

        for s in device_object_list:
            if not [p.id for p in device_object_list if s.parent_id == p.id]:
                try:
                    master_object = Device.objects.get(
                        id=s.parent_id
                    )
                    master_object_list.append(master_object)
                except ObjectDoesNotExist, error:
                    print error
        if len(master_object_list):
            device_object_list = device_object_list + master_object_list

        return device_object_list
