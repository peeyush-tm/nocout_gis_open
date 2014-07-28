import ast
import json, logging
import urllib
from django.db.models import Q, Count
from django.views.generic.base import View
from django.http import HttpResponse
from inventory.models import BaseStation, Sector, Circuit, SubStation, Customer, LivePollingSettings, \
    ThresholdConfiguration, ThematicSettings
from device.models import Device, DeviceType, DeviceVendor, \
    DeviceTechnology, DeviceModel, State, Country, City
import requests
from service.models import DeviceServiceConfiguration, Service, ServiceDataSource
from django.contrib.staticfiles.templatetags.staticfiles import static

logger=logging.getLogger(__name__)
# class DeviceStatsApi(View):
#     """
#     Api calls :wq!initiated for device stats
#
#     """
#
#     def get(self, request):
#         """
#         Handling http GET method for device data
#
#         Args:
#             request (WSGIRequest): The request object.
#
#         Returns:
#             {
#                 'success': 1,
#                 'message': 'Device Data',
#                 'data': {
#                     'meta': {
#                         'total_count': <total_count>,
#                         'limit': <limit>
#                     }
#                     'objects': <device_objects_list>
#             }
#
#         """
#
#         #Result dict prototype
#         self.result = {
#             "success": 0,
#             "message": "No Device Data",
#             "data": {
#                 "meta": None,
#                 "objects": None
#             }
#         }
#         req_params = request.GET
#
#         #Retreive username from active session
#         username = request.user.username
#         if username == '':
#             username = req_params.get('username')
#
#         page_number = req_params.get('page_number')
#         limit = req_params.get('limit')
#
#         #Get the host machine IP address
#         host_ip = request.META['SERVER_NAME']
#         host_port = request.META['SERVER_PORT']
#
#         #Show link between master-slave device pairs
#         show_link = 1
#
#         cls = DeviceStats()
#         device_stats_dict = DeviceStats.p2p_device_info(
#             cls,
#             username,
#             host_ip=host_ip,
#             host_port=host_port,
#             show_link=show_link,
#             page_number=page_number,
#             limit=limit
#         )
#
#         if len(device_stats_dict.get('children')):
#             self.result.update({
#                 "success": 1,
#                 "message": "Device Data",
#                 "data": {
#                     "meta": device_stats_dict.pop('meta'),
#                     "objects": device_stats_dict
#                 }
#             })
#             return HttpResponse(json.dumps(self.result))
#         else:
#             return HttpResponse(json.dumps(self.result))
#
#
# class DeviceStats(View):
#     """
#     Base class for Device stats methods
#     """
#
#     def p2p_device_info(self, user, **kwargs):
#         """
#         Serves device stats data for devices associated
#         with a particular user
#
#         Args:
#             user (str): Username passed in the querystring.
#             host_ip (str): IP address of the host machine.
#             show_link (int): Would show the links on GIS,
#                 if value goes to 1.
#
#         Returns:
#             Device stats `dict` object.
#
#         """
#
#         device_stats_dict = {}
#         inventory_list = []
#         page_number = kwargs.get('page_number') if kwargs.get('page_number') else 1
#         limit = kwargs.get('limit') if kwargs.get('limit') else 10
#         device_object_list = []
#         try:
#             self.user_id = User.objects.get(username=user).id
#             # self.user_gp_id = Department.objects.get(
#             #     user_profile_id=self.
#             #     user_id
#             # ).user_group_id
#             # One user_group may have associated with more than one device_group
#             # self.dev_gp_list = Organization.objects.filter(
#             #     user_group_id=self.
#             #     user_gp_id
#             # ).values()
#
#             # for dev_gp in self.dev_gp_list:
#                 # obj_list = Inventory.objects.filter(
#                 #     device_group_id=dev_gp.get('device_group_id')
#                 # ).values()
#                 # inventory_list.extend(obj_list)
#
#             total_count = len(inventory_list)
#         except Exception, error:
#             print "No Data for this user"
#             print error
#             return device_stats_dict
#
#         inventory_list, limit = self.slice_object_list(
#             inventory_list,
#             page_number=page_number,
#             limit=limit
#         )
#
#         for dev in inventory_list:
#             device_info = {}
#             try:
#                 if not [d.id for d in device_object_list if d.id == dev.get('device_id')]:
#                     device_object = Device.objects.get(
#                         id=dev.get('device_id')
#                     )
#                     device_object_list.append(device_object)
#                 if not [d.id for d in device_object_list if d.id == device_object.parent_id]:
#                     master_device_object = Device.objects.get(
#                         id=device_object.parent_id
#                     )
#                     device_object_list.append(master_device_object)
#             except ObjectDoesNotExist as e:
#                 print "No Device found"
#                 print e
#                 continue
#
#         device_stats_dict = self.get_master_slave_pairs(
#             device_object_list,
#             host_ip=kwargs.get('host_ip'),
#             host_port=kwargs.get('host_port')
#         )
#
#         return device_stats_dict
#
#     def get_model_queryset(self, model_class, field_name, **kwargs):
#         q_list = []
#         obj_attr_list = []
#         f = operator.attrgetter(field_name)
#         if kwargs.get('field_list') is not None:
#             for attr in kwargs.get('field_list'):
#                 q_list.append(Q(pk=attr))
#             obj_list = model_class.objects.filter(reduce(operator.or_, q_list))
#             for o in obj_list:
#                 obj_attr_list.append(f(o))
#         else:
#             obj_attr_list = model_class.objects.all().values('id', 'name')
#
#         return obj_attr_list
#
#     def get_master_slave_pairs(self, device_object_list, **kwargs):
#         device_technology_info = {}
#         device_vendor_info = {}
#         device_model_info = {}
#         device_type_info = {}
#         device_info = {}
#         device_info_list = []
#         #Prototype for device dict
#         device_stats_dict = {
#             "id": "root node",
#             "name": "Root Site Instance",
#             "data": {
#                 "$type": "none"
#             },
#             "children": []
#         }
#
#         device_technology_info = self.get_model_queryset(
#             DeviceTechnology,
#             'name'
#         )
#         device_technology_info = {x.get('id'): x.get('name') \
#                                 for x in device_technology_info}
#
#         device_vendor_info = self.get_model_queryset(
#             DeviceVendor,
#             'name'
#         )
#         device_vendor_info = {x.get('id'): x.get('name') \
#                                 for x in device_vendor_info}
#
#         device_model_info = self.get_model_queryset(
#             DeviceModel,
#             'name'
#         )
#         device_model_info = {x.get('id'): x.get('name') \
#                                 for x in device_model_info}
#
#         device_type_info = self.get_model_queryset(
#             DeviceType,
#             'name'
#         )
#         device_type_info = {x.get('id'): x.get('name') \
#                                 for x in device_type_info}
#         try:
#             for obj in device_object_list:
#                 device_info = {
#                         "id": obj.id,
#                         "name": obj.device_name,
#                         "alias": obj.device_alias,
#                         "device_type": device_type_info.get(obj.device_type),
#                         "mac": obj.mac_address,
#                         "current_state": obj.host_state,
#                         "vendor": device_vendor_info.get(obj.device_vendor),
#                         "model": device_model_info.get(obj.device_model),
#                         "technology": device_technology_info.get(obj.device_technology),
#                         "parent_id": obj.parent_id,
#                         "lat": obj.latitude,
#                         "lon": obj.longitude,
#                         "markerUrl": "//%s:%s/static/img/marker/slave03.png"
#                         % (kwargs.get('host_ip'), kwargs.get('host_port')),
#                         "perf": "75%",
#                         "ip": obj.ip_address,
#                         "otherDetail": "No Detail",
#                         "city": obj.city,
#                         "state": obj.state
#                     }
#                 device_info_list.append(device_info)
#         except AttributeError, error:
#             print "Device Info Key Error"
#             print error.message
#             raise
#
#         #Master-slave pairs based on `parent_id` and `device_id`
#         for outer in device_info_list:
#             master = copy.deepcopy(outer)
#             master.update(
#                 {
#                 "showLink": kwargs.get('show_link'),
#                 "children": []
#                 }
#             )
#             #dict to store master device info
#             master = {
#                 "id": master.pop('id'),
#                 "parent_id": master.pop('parent_id'),
#                 "name": master.pop('name'),
#                 "children": master.pop('children'),
#                 "data": master
#             }
#             for inner in device_info_list:
#                 if inner.get('parent_id') == outer.get('id'):
#                     slave = copy.deepcopy(inner)
#                     slave.update(
#                         {
#                         "linkColor": "green",
#                         "children": []
#                         }
#                     )
#                     #dict to store slave device info
#                     slave = {
#                         "id": slave.pop('id'),
#                         "name": slave.pop('name'),
#                         "parent_id": slave.pop('parent_id'),
#                         "children": slave.pop('children'),
#                         "data": slave
#                     }
#                     master.pop('parent_id', None)
#                     slave.pop('parent_id', None)
#                     master.get('children').append(slave)
#                     device_stats_dict.get('children').append(master)
#         device_stats_dict.update({
#             "meta": {
#                 "total_count": None,
#                 "limit": None
#             }
#         })
#         return device_stats_dict
#
#     def slice_object_list(self, inventory_list, **kwargs):
#         if int(kwargs.get('limit')) is not 0:
#             limit = int(kwargs.get('limit'))
#         else:
#             limit = 10
#         if int(kwargs.get('page_number')) is not 0:
#             page_number = int(kwargs.get('page_number'))
#         else:
#             page_number = 1
#         start = limit * (page_number-1)
#         end = limit * (page_number)
#         inventory_list = inventory_list[start:end]
#         return inventory_list, limit



class DeviceStatsApi(View):


    def get(self, request):

        self.result = {
            "success": 0,
            "message": "No Device Data",
            "data": {
                "meta": {},
                "objects": None
            }
        }
        # page_number= request.GET['page_number']
        # limit= request.GET['limit']


        logged_in_user= self.request.user.userprofile

        if logged_in_user.role.values_list('role_name', flat=True)[0] =='admin':
            organizations= logged_in_user.organization.get_descendants(include_self=True)
        else:
            organizations=[logged_in_user.organization]

        if organizations:
            for organization in organizations:

                base_stations_and_sector_configured_on_devices= Sector.objects.filter(sector_configured_on__id__in= organization.device_set.values_list('id', flat=True))\
                    .values_list('base_station').annotate(dcount=Count('base_station'))
                self.result['data']['meta']['total_count']=0

                if base_stations_and_sector_configured_on_devices:
                    self.result['data']['objects']= {"id" : "mainNode", "name" : "mainNodeName", "data" :
                                                            { "unspiderfy_icon" : "static/img/marker/slave01.png" }
                                                    }
                    self.result['data']['objects']['children']=list()
                    for base_station_id, dcount in base_stations_and_sector_configured_on_devices:
                        try:

                            base_station=BaseStation.objects.get(id=base_station_id)
                            # sector_configured_on_device=Device.objects.get(id=sector_configured_on_device)
                            base_station_info={
                                'id':base_station.id,
                                'name':base_station.name,
                                'data':{
                                        'lat':base_station.latitude,
                                        'lon':base_station.longitude,
                                        "markerUrl" : "static/img/marker/icon2_small.png",
                                        'technology':base_station.bs_technology.name,
                                        'antena_height':None,
                                        'vendor':','.join(base_station.bs_technology.device_vendors.values_list('name', flat=True)),
                                        'city':City.objects.get(id=base_station.city).city_name if base_station.city else None ,
                                        'state':State.objects.get(id=base_station.state).state_name if base_station.state else None,
                                        'param':{
                                            'base_station':[
                                                        {
                                                         'name':'alias',
                                                         'title':'Alias',
                                                         'show':1,
                                                         'value':base_station.alias
                                                        },
                                                        {
                                                         'name':'building_height',
                                                         'title':'Building Height',
                                                         'show':1,
                                                         'value':base_station.building_height if base_station.building_height else 'N/A'
                                                        },
                                                        {
                                                         'name':'tower_height',
                                                         'title':'Tower Height',
                                                         'show':1,
                                                         'value':base_station.tower_height if base_station.tower_height else 'N/A'
                                                        },
                                                        {
                                                         'name':'bs_technology',
                                                         'title':'BS Technology',
                                                         'show':1,
                                                         'value':base_station.bs_technology.name if base_station.bs_technology else 'N/A'
                                                        }],
                                              'backhual':[
                                                           {
                                                            'name':'bh_configured_on',
                                                            'title':'BH Configured On',
                                                            'show':1,
                                                            'value':base_station.backhaul.bh_configured_on.device_name if base_station.backhaul.bh_configured_on.device_name else 'N/A'
                                                           },
                                                           {
                                                            'name':'bh_capacity',
                                                            'title':'BH Capacity',
                                                            'show':1,
                                                            'value':base_station.backhaul.bh_capacity if base_station.backhaul.bh_capacity else 'N/A'
                                                           },
                                                           {
                                                            'name':'bh_type',
                                                            'title':'BH Type',
                                                            'show':1,
                                                            'value':base_station.backhaul.bh_type if base_station.backhaul.bh_type else 'N/A'
                                                           },
                                                           {
                                                            'name':'pe_ip',
                                                            'title':'PE IP',
                                                            'show':1,
                                                            'value':base_station.backhaul.pe_ip if base_station.backhaul.pe_ip else 'N/A'
                                                           },
                                                           {
                                                            'name':'bh_connectivity',
                                                            'title':'BH Connectivity',
                                                            'show':1,
                                                            'value':base_station.backhaul.bh_connectivity if base_station.backhaul.bh_connectivity else 'N/A'
                                                           },
                                       ]}

                                       },
                                }

                            base_station_info['data']['param']['sector']=[]
                            sectors= Sector.objects.filter(base_station = base_station.id)
                            for sector in sectors:
                                    base_station_info['data']['param']['sector']+=[{
                                    "color" : sector.frequency.color_hex_value if hasattr(sector, 'frequency')  and sector.frequency else 'rgba(74,72,94,0.58)',
                                    'radius':sector.cell_radius,
                                    'azimuth_angle':sector.antenna.azimuth_angle,
                                    'beam_width' : sector.antenna.beam_width,
                                    'orientation' : sector.antenna.polarization,
                                    'info':[   {
                                                'name':'sector_name',
                                                'title':'Sector Name',
                                                'show':1,
                                                'value':sector.name
                                                },
                                               {
                                                'name':'type_of_bs',
                                                'title':'Type of BS',
                                                'show':1,
                                                'value':sector.base_station.bs_type \
                                                    if sector.base_station.bs_type else 'N/A'
                                                },
                                               {
                                                'name':'building_height',
                                                'title':'Building Height',
                                                'show':1,
                                                'value':base_station.building_height \
                                                    if base_station.building_height else 'N/A'
                                                },
                                               {
                                                'name':'tower_height',
                                                'title':'Tower Height',
                                                'show':1,
                                                'value':base_station.tower_height if base_station.tower_height else 'N/A'
                                                },
                                               {
                                                'name':'type_of_antenna',
                                                'title':'Antenna Type',
                                                'show':1,
                                                'value':sector.antenna.mount_type if sector.antenna.mount_type else 'N/A'
                                                },
                                               {
                                                'name':'antenna_tilt',
                                                'title':'Antenna Tilt',
                                                'show':1,
                                                'value':sector.antenna.tilt if sector.antenna.tilt else 'N/A'
                                                },
                                               {
                                                'name':'antenna_ht',
                                                'title':'Antenna Height',
                                                'show':1,
                                                'value':sector.antenna.height if sector.antenna.height else 'N/A'
                                                },
                                               {
                                                'name':'antenna_bw',
                                                'title':'Antenna Beam Width',
                                                'show':1,
                                                'value':sector.antenna.beam_width if sector.antenna.beam_width else 'N/A'
                                                },
                                               {
                                                'name':'antenna_azimuth',
                                                'title':'Antenna Azimuth Angle',
                                                'show':1,
                                                'value':sector.antenna.azimuth_angle if sector.antenna.azimuth_angle else 'N/A'
                                                },
                                               {
                                                'name':'antenna_splitter_installed',
                                                'title':'Installation of Splitter',
                                                'show':1,
                                                'value':sector.antenna.splitter_installed if sector.antenna.splitter_installed else 'N/A'
                                                },
                                               {
                                                'name':'city',
                                                'title':'City',
                                                'show':1,
                                                'value':City.objects.get(id=base_station.city).city_name  \
                                                    if sector.base_station.city else 'N/A'
                                                },
                                               {
                                                'name':'state',
                                                'title':'State',
                                                'show':1,
                                                'value':State.objects.get(id=base_station.state).state_name \
                                                    if base_station.state else 'N/A'
                                                },
                                    ],
                                    'sub_station':[]

                                    }]

                                    circuits= Circuit.objects.filter(sector = sector.id)
                                    for circuit in circuits:
                                        substation= SubStation.objects.get(id = circuit.sub_station.id)
                                        substation_device= Device.objects.get(id= substation.device.id)
                                        base_station_info['data']['param']['sector'][-1]['sub_station']+=[{
                                                          'id'  : substation.id,
                                                          'name': substation.name,
                                                          'data': {
                                                              "lat":substation_device.latitude,
                                                              "lon":substation_device.longitude,
                                                              "antenmaina_height" : sector.antenna.height,
                                                              "markerUrl" : "static/img/marker/icon4_small.png",
                                                              "show_link" : 1,
                                                              "link_color" : sector.frequency.color_hex_value if hasattr(sector, 'frequency')  and sector.frequency else 'rgba(74,72,94,0.58)',
                                                              'param':{
                                                                      'sub_station':[
                                                                          {
                                                                           'name':'alias',
                                                                           'title':'Alias',
                                                                           'show':1,
                                                                           'value':substation_device.device_alias if substation_device.device_alias else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'cktid',
                                                                           'title':'Circuit ID',
                                                                           'show':1,
                                                                           'value':circuit.id if circuit.id else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'qos_bandwidth',
                                                                           'title':'QOS(BW)',
                                                                           'show':1,
                                                                           'value':circuit.qos_bandwidth if circuit.qos_bandwidth else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'latitude',
                                                                           'title':'Latitude',
                                                                           'show':1,
                                                                           'value':substation_device.latitude if substation_device.latitude else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'longitude',
                                                                           'title':'Longitude',
                                                                           'show':1,
                                                                           'value':substation.device.longitude if substation.device.longitude else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'antenna_height',
                                                                           'title':'Antenna Height',
                                                                           'show':1,
                                                                           'value':sector.antenna.height if sector.antenna.height else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'polarisation',
                                                                           'title':'Polarisation',
                                                                           'show':1,
                                                                           'value':sector.antenna.polarization \
                                                                               if sector.antenna.polarization else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'mount_type',
                                                                           'title':'SS MountType',
                                                                           'show':1,
                                                                           'value':sector.antenna.mount_type if sector.antenna.mount_type else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'antenna_type',
                                                                           'title':'Antenna Type',
                                                                           'show':1,
                                                                           'value':sector.antenna.antenna_type if sector.antenna.antenna_type else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'ethernet_extender',
                                                                           'title':'Ethernet Extender',
                                                                           'show':1,
                                                                           'value':sector.antenna.ethernet_extender \
                                                                               if hasattr(sector.antenna, 'ethernet_extender') and sector.antenna.ethernet_extender  else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'cable_length',
                                                                           'title':'Cable Length',
                                                                           'show':1,
                                                                           'value':sector.antenna.cable_length \
                                                                               if hasattr(sector.antenna, 'cable_length') and sector.antenna.cable_length else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'customer_address',
                                                                           'title':'Customer Address',
                                                                           'show':1,
                                                                           'value': Customer.objects.get(id=sector.circuit_set.values('customer')).address \
                                                                               if 'customer' in sector.circuit_set.values() else 'N/A'
                                                                          },
                                                                          {
                                                                           'name':'date_of_acceptance',
                                                                           'title':'Date of Acceptance',
                                                                           'show':1,
                                                                           'value':Customer.objects.get(id=sector.circuit_set.values('customer')).date_of_acceptance \
                                                                               if 'date_of_acceptance' in sector.circuit_set.values('date_of_acceptance') else 'N/A'
                                                                          }
                                                                      ],
                                                                  }
                                                              }
                                                              }]
                            self.result['data']['objects']['children'].append(base_station_info)
                        except Exception as e:
                            logger.error("API Error Message: %s"%(e.message))
                            pass
                    self.result['message']='Data Fetched Successfully.'
                    self.result['success']=1
        return HttpResponse(json.dumps(self.result))


class DeviceFilterApi(View):

    def get(self, request):
        self.result = {
            "success": 0,
            "message": "No Device Data",
            "data": {
                "meta": {},
                "objects": {}
            }
        }

        technology_data,vendor_data,state_data,city_data=[],[],[],[]
        for device_technology in DeviceTechnology.objects.all():
            technology_data.append({ 'id':device_technology.id,
                                     'value':device_technology.name })
        for vendor in DeviceVendor.objects.all():
            vendor_data.append({ 'id':vendor.id,
                                     'value':vendor.name })

        for state in State.objects.all():
            state_data.append({ 'id':state.id,
                                     'value':state.state_name })

        for city in City.objects.all():
            city_data.append({ 'id':city.id,
                                     'value':city.city_name })

        self.result['data']['objects']['technology']={'data':technology_data}
        self.result['data']['objects']['vendor']={'data':vendor_data}
        self.result['data']['objects']['state']={'data':state_data}
        self.result['data']['objects']['city']={'data':city_data}
        self.result['message']='Data Fetched Successfully.'
        self.result['success']=1

        return HttpResponse(json.dumps(self.result))


class LPServicesApi(View):
    def get(self, request):
        self.result = {
            "success": 0,
            "message": "No Service Data",
            "data": {
            }
        }
        devices = eval(str(self.request.GET.get('devices',None)))
        if devices:
            for dv in devices:
                device = Device.objects.get(device_name=dv)
                device_sdc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name)
                self.result['data'][str(dv)] = {}
                self.result['data'][str(dv)]['services'] = []
                for dsc in device_sdc:
                    svc_dict = {}
                    svc_dict['name'] = str(dsc.service_name)
                    svc_dict['value'] = Service.objects.get(name=dsc.service_name).id
                    svc_dict['datasource'] = []
                    service_data_sources = DeviceServiceConfiguration.objects.filter(device_name=dv, service_name=dsc.service_name)
                    for sds in service_data_sources:
                        sds_dict = {}
                        sds_dict['name'] = sds.data_source
                        sds_dict['value'] = ServiceDataSource.objects.get(name=sds.data_source).id
                        svc_dict['datasource'].append(sds_dict)
                    self.result['data'][str(dv)]['services'].append(svc_dict)
        return HttpResponse(json.dumps(self.result))


class FetchLPDataApi(View):
    def get(self, request):
        devices = eval(str(self.request.GET.get('device',None)))
        services = eval(str(self.request.GET.get('service',None)))
        datasources = eval(str(self.request.GET.get('datasource',None)))

        self.result = {
            "success": 0,
            "message": "",
            "data": {
            }
        }

        self.result['data']['value'] = []
        self.result['data']['icon'] = []

        for dv, svc, ds in zip(devices, services, datasources):
            lp_data = {}
            lp_data['mode'] = "live"
            lp_data['device'] = dv
            lp_data['service'] = svc
            lp_data['ds'] = []
            lp_data['ds'].append(ds)

            device = Device.objects.get(device_name=dv)
            service= Service.objects.get(name=svc)
            data_source = ServiceDataSource.objects.get(name=ds)
            machine_ip = device.machine.machine_ip
            site_name = device.site_instance.name

            url = "http://{}:{}@{}:{}/{}/check_mk/nocout_live.py".format(device.site_instance.username,
                                                                    device.site_instance.password,
                                                                    device.machine.machine_ip,
                                                                    device.site_instance.web_service_port,
                                                                    device.site_instance.name)

            encoded_data = urllib.urlencode(lp_data)
            r = requests.post(url , data=encoded_data)

            # converting post response data into python dict expression
            response_dict = ast.literal_eval(r.text)
            # if response(r) is given by post request than process it further to get success/failure messages
            if r:
                self.result['success'] = 1
                self.result['data']['value'].append(response_dict.get('value')[0])


                tech = DeviceTechnology.objects.get(pk=device.device_technology)
                lps = LivePollingSettings.objects.get(technology=tech, service=service, data_source=data_source)
                tc = ThresholdConfiguration.objects.get(live_polling_template=lps)
                ts = ThematicSettings.objects.get(threshold_template=tc)
                value = int(response_dict.get('value')[0])
                if int(value) > int(tc.warning):
                    icon = static('img/{}'.format(ts.gt_warning.upload_image))
                elif int(tc.warning) >= int(value) >= int(tc.critical):
                    icon = static('img/{}'.format(ts.bt_w_c.upload_image))
                elif int(value) > int(tc.critical):
                    icon = static('img/{}'.format(ts.gt_critical.upload_image))
                else:
                    icon = static('img/icons/wifi7.png')

                self.result['data']['icon'].append(icon)
                # if response_dict doesn't have key 'success'
                if not response_dict.get('success'):
                    logger.info(response_dict.get('error_message'))
                    self.result['message'] += "Failed to fetch data for '%s'. <br />" % (svc)
                else:
                    self.result['message'] += "Successfully fetch data for '%s'. <br />" % (svc)

        return HttpResponse(json.dumps(self.result))




