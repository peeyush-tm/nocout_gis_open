import logging
import operator
import copy
import ast
import json
# from device.api import DeviceStats
import re
from django.db.models import Q, Count
from django.views.generic.base import View
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from device.api import logged_in_user_organizations, prepare_result
from device.models import Device, DeviceType, DeviceVendor,\
    DeviceTechnology, City, State
from itertools import chain
from device_group.models import DeviceGroup

logger=logging.getLogger(__name__)
# class DeviceGetFilters(View):
#     """
#     Getting all the info for all the devices,
#     to be populated into search filters drop downs
#
#     """
#
#     def get(self, request):
#         """
#         Getting all the devices
#
#         Args:
#
#         Returns:
#
#         """
#
#         device_dict = {}
#         self.result = {
#             "success": 1,
#             "message": "Device Data",
#             "data": {
#                 "meta": None,
#                 "objects": []
#             }
#         }
#         device_dict = self.get_device_objects()
#         self.result.get('data').get('objects').extend(device_dict)
#         device_dict = self.get_objects_by_id(
#             DeviceGroup,
#             key='device_group',
#             title='Device Group'
#         )
#         self.result.get('data').get('objects').append(device_dict)
#         device_dict = self.get_objects_by_id(
#             DeviceType,
#             key='device_type',
#             title='Device Type'
#         )
#         self.result.get('data').get('objects').append(device_dict)
#         device_dict = self.get_objects_by_id(
#             DeviceTechnology,
#             key='device_technology',
#             title='Device Technology'
#         )
#         self.result.get('data').get('objects').append(device_dict)
#         device_dict = self.get_objects_by_id(
#             DeviceVendor,
#             key='device_vendor',
#             title='Device Vendor'
#         )
#         self.result.get('data').get('objects').append(device_dict)
#         return HttpResponse(json.dumps(self.result))
#
#
#     def get_device_objects(self, **kwargs):
#         result_list = []
#         device_attribute_dict = {
#             "device_name": [],
#             "device_alias": [],
#             "ip_address": [],
#             "mac_address": [],
#             "host_state": [],
#             "city": [],
#             "state": []
#         }
#         base_dict = {
#             "key": None,
#             "title": None,
#             "field_type": None,
#             "element_type": None,
#             "values": []
#         }
#         attr_list = [
#             {"device_name": "Device Name"},
#             {"device_alias": "Device Alias"},
#             {"ip_address": "IP Address"},
#             {"mac_address": "Mac Address"},
#             {"host_state": "Host State"},
#             {"city": "City"},
#             {"state": "State"}
#         ]
#         obj_list = Device.objects.all().order_by('id').values()
#         for obj in obj_list:
#             device_attribute_dict.get('device_name').append({
#                 "id": obj.get('id'),
#                 "value": obj.get('device_name')
#             })
#             device_attribute_dict.get('device_alias').append({
#                 "id": obj.get('id'),
#                 "value": obj.get('device_alias')
#             })
#             device_attribute_dict.get('ip_address').append({
#                 "id": obj.get('id'),
#                 "value": obj.get('ip_address')
#             })
#             device_attribute_dict.get('mac_address').append({
#                 "id": obj.get('id'),
#                 "value": obj.get('mac_address')
#             })
#             device_attribute_dict.get('host_state').append({
#                 "id": obj.get('id'),
#                 "value": obj.get('host_state')
#             })
#             device_attribute_dict.get('city').append({
#                 "id": obj.get('id'),
#                 "value": obj.get('city')
#             })
#             device_attribute_dict.get('state').append({
#                 "id": obj.get('id'),
#                 "value": obj.get('state')
#             })
#
#         for attr in attr_list:
#             base_dict = dict(
#                 key=attr.keys()[0],
#                 title=attr.values()[0],
#                 field_type="string",
#                 element_type="multiselect",
#                 values=device_attribute_dict.get(attr.keys()[0])
#             )
#             result_list.append(base_dict)
#
#         return result_list
#
#     def get_objects_by_id(self, model_class, **kwargs):
#         base_dict = {
#             "key": kwargs.get('key'),
#             "title": kwargs.get('title'),
#             "field_type": "string",
#             "element_type": "multiselect",
#             "values": []
#         }
#
#         obj_list = model_class.objects.all().order_by('id')
#         for obj in obj_list:
#             value_dict = dict(
#                 id=obj.id,
#                 value=obj.name
#             )
#             base_dict.get('values').append(value_dict)
#
#         return base_dict
#
#
# class DeviceSetFilters(View):
#     """
#     Returning values matched to search filters
#     criterion
#     """
#
#     def get(self, request):
#         """
#         Get the values for filters
#
#         Args:
#
#         Returns:
#
#         """
#
#         req_params = request.GET
#         #Get the host-ip
#         host_ip = request.META['SERVER_NAME']
#         host_port = request.META['SERVER_PORT']
#         filters = {}
#         device_attribs = {}
#         device_object_list = []
#         #Result dict prototype
#         self.result = {
#             "success": 0,
#             "message": "No Device Data",
#             "data": {
#                 "meta": None,
#                 "objects": None
#             }
#         }
#         cls = DeviceStats()
#
#         if req_params.get('filters') is not None:
#             filters = ast.literal_eval(req_params.get('filters'))
#
#         #storing all filter, name/value, pairs in one big dict
#         filters = {attr.get('field'): attr.get('value') for attr in filters}
#
#         if 'device_group' in filters.iterkeys():
#             device_gp_list = DeviceStats.get_model_queryset(
#                 cls,
#                 DeviceGroup,
#                 'id',
#                 field_list=filters.get('device_group')
#             )
#
#             device_id_list = self.inventory_model_queryset(
#                 Inventory,
#                 'device_id',
#                 field_list=device_gp_list
#             )
#             device_attribs.update({
#                 "device_id_list": device_id_list
#             })
#
#         if 'device_technology' in filters.iterkeys():
#             device_attribs = self.add_filters(
#                 filters,
#                 device_attribs,
#                 'device_technology'
#             )
#
#         if 'device_vendor' in filters.iterkeys():
#             device_attribs = self.add_filters(
#                 filters,
#                 device_attribs,
#                 'device_vendor'
#             )
#
#         if 'device_model' in filters.iterkeys():
#             device_attribs = self.add_filters(
#                 filters,
#                 device_attribs,
#                 'device_model'
#             )
#
#         if 'device_name' in filters.iterkeys():
#             device_attribs = self.add_filters(
#                 filters,
#                 device_attribs,
#                 'device_name'
#             )
#
#         if 'device_alias' in filters.iterkeys():
#             device_attribs = self.add_filters(
#                 filters,
#                 device_attribs,
#                 'device_alias'
#             )
#
#         if 'mac_address' in filters.iterkeys():
#             device_attribs = self.add_filters(
#                 filters,
#                 device_attribs,
#                 'mac_address'
#             )
#
#         if 'ip_address' in filters.iterkeys():
#             device_attribs = self.add_filters(
#                 filters,
#                 device_attribs,
#                 'ip_address'
#             )
#
#         if 'city' in filters.iterkeys():
#             device_attribs = self.add_filters(
#                 filters,
#                 device_attribs,
#                 'city'
#             )
#
#         if 'state' in filters.iterkeys():
#             device_attribs = self.add_filters(
#                 filters,
#                 device_attribs,
#                 'state'
#             )
#
#         device_object_list = self.device_model_queryset(
#             Device,
#             'device_name',
#             field_attribs=device_attribs
#         )
#
#         device_object_list = self.get_master(device_object_list)
#
#         device_m_s_info = DeviceStats.get_master_slave_pairs(
#             cls,
#             device_object_list,
#             show_link=1,
#             host_ip=host_ip,
#             host_port=host_port
#         )
#
#         if len(device_m_s_info.get('children')):
#             self.result.update({
#                 "success": 1,
#                 "message": "Device Data",
#                 "data": {
#                     "meta": device_m_s_info.pop('meta'),
#                     "objects": device_m_s_info
#                 }
#             })
#             return HttpResponse(json.dumps(self.result))
#         else:
#             return HttpResponse(json.dumps(self.result))
#
#     def add_filters(self, filters, filter_dict, filter_key):
#         filter_dict.update({
#             filter_key: filters.get(filter_key)
#         })
#
#         return filter_dict
#
#     def inventory_model_queryset(self, model_class, field_name, **kwargs):
#         q_list = []
#         obj_attr_list = []
#         f = operator.attrgetter(field_name)
#         for attr in kwargs.get('field_list'):
#             q_list.append(Q(device_group_id=attr))
#
#         obj_list = model_class.objects.filter(reduce(operator.or_, q_list))
#         for o in obj_list:
#             obj_attr_list.append(f(o))
#
#         return obj_attr_list
#
#     def device_model_queryset(self, model_class, field_name, **kwargs):
#         q_list = []
#         reduce_q_list = []
#         final_predicate_list = []
#         obj_attr_list = []
#         obj_list = []
#
#         f = operator.attrgetter(field_name)
#
#         device_id_list = kwargs.get('field_attribs').get('device_id_list', [])
#         device_technology = kwargs.get('field_attribs').get('device_technology', [])
#         device_vendor = kwargs.get('field_attribs').get('device_vendor', [])
#         device_model = kwargs.get('field_attribs').get('device_model', [])
#         device_name = kwargs.get('field_attribs').get('device_name', [])
#         device_alias = kwargs.get('field_attribs').get('device_alias', [])
#         mac_address = kwargs.get('field_attribs').get('mac_address', [])
#         ip_address = kwargs.get('field_attribs').get('ip_address', [])
#         city_list = kwargs.get('field_attribs').get('city', [])
#         state_list = kwargs.get('field_attribs').get('state', [])
#
#         if len(device_id_list):
#             for _id in device_id_list:
#                 q_list.append(Q(pk=_id))
#         if len(device_technology):
#             for _id in device_technology:
#                 q_list.append(Q(device_technology=_id))
#         if len(device_vendor):
#             for _id in device_vendor:
#                 q_list.append(Q(device_vendor=_id))
#         if len(device_model):
#             for _id in device_model:
#                 q_list.append(Q(device_model=_id))
#         if len(device_name):
#             for _name in device_name:
#                 q_list.append(Q(device_name=_name))
#         if len(device_alias):
#             for _alias in device_alias:
#                 q_list.append(Q(device_alias=_alias))
#         if len(ip_address):
#             for _ip in ip_address:
#                 q_list.append(Q(ip_address=_ip))
#         if len(mac_address):
#             for _mac in mac_address:
#                 q_list.append(Q(mac_address=_mac))
#         if len(city_list):
#             for city in city_list:
#                 q_list.append(Q(city=city.strip()))
#         if len(state_list):
#             for state in state_list:
#                 q_list.append(Q(state=state.strip()))
#         if len(q_list):
#             reduce_q_list = reduce(operator.or_, q_list)
#
#         if len(reduce_q_list):
#             obj_list = model_class.objects.filter(reduce_q_list)
#
#         return obj_list
#
#     def get_master(self, device_object_list):
#         master_object = None
#         master_object_list = []
#         device_object_list = list(device_object_list)
#         if len(device_object_list) == 0:
#             return device_object_list
#
#         for s in device_object_list:
#             if not [p.id for p in device_object_list if s.parent_id == p.id]:
#                 try:
#                     master_object = Device.objects.get(
#                         id=s.parent_id
#                     )
#                     master_object_list.append(master_object)
#                 except ObjectDoesNotExist, error:
#                     print error
#         if len(master_object_list):
#             device_object_list = device_object_list + master_object_list
#
#         return device_object_list
from inventory.models import Sector, BaseStation, Circuit
#reving duplicate entries in the dictionaries in a list
removing_duplicate_entries = lambda lst: [dict(t) for t in set( [ tuple(sorted(d.items())) for d in lst ] )]

class DeviceGetFilters(View):
    """
        Getting all the info for all the devices,
        to be populated into search filters drop downs

    """
    def get(self, request):
        """
        Getting all the devices

        Args: self , request

        Returns: self.result

        """
        self.result = {
            "success": 1,
            "message": "Device Data",
            "data": {
                "meta": None,
                "objects": []
            }
        }

        bs_name={
                "field_type": "string",
                "element_type": "multiselect",
                "values": [],
                "key": "name",
                "title": "B S Name"
                }

        bs_alias={
                "field_type": "string",
                "element_type": "multiselect",
                "values": [],
                "key": "alias",
                "title": "B S Alias"
                }

        bs_city={
                "field_type": "string",
                "element_type": "multiselect",
                "values": [],
                "key": "city",
                "title": "BS City"
                }

        bs_state={
                "field_type": "string",
                "element_type": "multiselect",
                "values": [],
                "key": "state",
                "title": "BS State"
                }

        bs_technology={
                "field_type": "string",
                "element_type": "multiselect",
                "values": [],
                "key": "bs_technology",
                "title": "BS Technology"
                }

        bs_latitude={
                "field_type": "string",
                "element_type": "multiselect",
                "values": [],
                "key": "latitude",
                "title": "BS Latitude"
                }

        bs_longitude={
                "field_type": "string",
                "element_type": "multiselect",
                "values": [],
                "key": "longitude",
                "title": "BS Longitude"
                }


        sector_configured_on_dict={
                "field_type": "string",
                "element_type": "multiselect",
                "values": [],
                "key": "sector_configured_on",
                "title": "Sector Configured On Device"
                }

        circuit_dict={
                "field_type": "string",
                "element_type": "multiselect",
                "values": [],
                "key": "circuit_name",
                "title": "Circuit"
            }

        organizations= logged_in_user_organizations(self)

        for organization in organizations:
            base_stations= Sector.objects.filter( sector_configured_on__id__in= \
            organization.device_set.values_list('id', flat=True )).values_list('base_station', flat=True).distinct()


            for base_station_id in base_stations:
                try:
                    base_station_object= BaseStation.objects.get(id= base_station_id)
                    bs_name['values'].append({'id':base_station_object.id, 'value':base_station_object.name })
                    bs_alias['values'].append({'id':base_station_object.id, 'value':base_station_object.alias })
                    bs_city['values'].append({'id':base_station_object.city, 'value':City.objects.get(id=base_station_object.city).city_name })
                    bs_state['values'].append({'id':base_station_object.state, 'value':State.objects.get(id=base_station_object.state).state_name })
                    bs_technology['values'].append({'id':base_station_object.bs_technology.id, 'value':base_station_object.bs_technology.name })
                    bs_latitude['values'].append({'id':base_station_object.id, 'value':base_station_object.latitude })
                    bs_longitude['values'].append({'id':base_station_object.id, 'value':base_station_object.longitude })


                    sectors= Sector.objects.filter( base_station= base_station_id )
                    for sector in sectors:
                        sector_configured_on_dict['values'].append({'id':sector.sector_configured_on.id,\
                               'value': sector.sector_configured_on.device_name + ' ('+sector.sector_configured_on.ip_address+')' })

                        if sector.circuit_set.values_list('id', flat=True):
                            circuit_dict['values'].append({'id':sector.circuit_set.values_list('id', flat=True)[0],\
                                                           'value':sector.circuit_set.values_list('name', flat=True)[0] })


                except Exception as e:
                    logger.info( e.message+'for base station id: %s'%(str(base_station_id)) )

        #removing duplicate values for the bs_city, bs_state and bs_technology
        bs_state['values']=removing_duplicate_entries(bs_state['values'])
        bs_city['values']=removing_duplicate_entries(bs_city['values'])
        bs_technology['values']=removing_duplicate_entries(bs_technology['values'])

        self.result['data']['objects'].extend((bs_name, bs_alias, bs_technology, bs_city, bs_state, bs_latitude,\
                                              bs_longitude, sector_configured_on_dict, circuit_dict))

        return HttpResponse(json.dumps(self.result))



class DeviceSetFilters(View):
    """
    Parses the request
    """
    def get(self, request):

        self.result = {
            "success": 0,
            "message": "Device Data",
            "data": {
                "meta": None,
                "objects": []
            }
        }

        request_query= self.request.GET.get('filters','')
        if request_query:
            request_query=eval(request_query)
            base_station_ids, circuit_ids= list(), list()
            exec_query_base_station = "base_station_ids = BaseStation.objects.filter("
            exec_query_circuit = "circuit_ids = Circuit.objects.filter("

            query_circuit, query_base_station =list(), list()
            for filter in request_query:
                if filter['field']=='circuit_name':
                    query_circuit.append("Q(name__in=%s)"%(filter['value']))
                elif filter['field']=='city':

                    city_ids=City.objects.filter(city_name__in=filter['value']).values_list('id', flat=True)
                    query_base_station.append("Q(%s__in=%s)"%(filter['field'],str(city_ids)))

                elif filter['field']=='state':

                    state_ids=State.objects.filter(state_name__in= filter['value']).values_list('id', flat=True)
                    query_base_station.append("Q(%s__in=%s)"%(filter['field'],str(state_ids)))

                elif filter['field']=='bs_technology':

                    dt_ids=DeviceTechnology.objects.filter(name__in= filter['value']).values_list('id', flat=True)
                    query_base_station.append("Q(%s__in=%s)"%(filter['field'],str(dt_ids)))

                elif filter['field']=='sector_configured_on':
                    #removing the () brackets and anything between it and then strip it to remove any space left.
                    value_list= [ re.sub("\([^]]*\)", lambda x:'', value ).strip() for value in filter['value'] ]

                    devices= Device.objects.filter(device_name__in = value_list).values_list('id', flat=True)
                    # sector_configured_on_ids=list()
                    # for device in devices:
                    #     sector_configured_on_ids+= device.sector_configured_on.values_list('id', flat=True)

                    bs_ids= Sector.objects.filter(sector_configured_on__in= devices)\
                                .values_list('base_station__id', flat=True)

                    base_station_ids+=bs_ids

                else:
                    query_base_station.append("Q(%s__in=%s)"%(filter['field'], filter['value']))

            exec_query_base_station+=" | ".join(query_base_station) +").values_list('id', flat=True)"
            exec_query_circuit+=" | ".join(query_circuit) +").values_list('id', flat=True)"

            if query_base_station: exec exec_query_base_station
            if query_circuit: exec exec_query_circuit

            if base_station_ids:
                self.result['data']['objects']= {"id" : "mainNode", "name" : "mainNodeName", "data" :
                                                { "unspiderfy_icon" : "static/img/marker/slave01.png" }
                                                }
                self.result['data']['objects']['children']=list()
                for base_station_id in base_station_ids:
                    try:
                        base_station_info=prepare_result(base_station_id)
                        self.result['data']['objects']['children'].append(base_station_info)
                    except Exception as e:
                        logger.error("API Error Message: %s"%(e.message))
                        pass

            if circuit_ids:
                for circuit_id in circuit_ids:
                    circuit=Circuit.objects.get(id=circuit_id)
                    base_station_id=circuit.sector.base_station.id
                    try:
                        base_station_info=prepare_result(base_station_id)
                        self.result['data']['objects']['children'].append(base_station_info)
                    except Exception as e:
                        logger.error("API Error Message: %s"%(e.message))
                        pass

            self.result['message']='Data Fetched Successfully.'
            self.result['success']=1

        return HttpResponse(json.dumps(self.result))

































