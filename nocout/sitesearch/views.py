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
from inventory.models import Sector, BaseStation, Circuit, SubStation, Customer, Antenna
from device.models import Device, DeviceType, DeviceVendor, \
    DeviceTechnology, City, State
from nocout.settings import GIS_MAP_MAX_DEVICE_LIMIT
from nocout.utils import logged_in_user_organizations
logger = logging.getLogger(__name__)

# removing duplicate entries in the dictionaries in a list
removing_duplicate_entries = lambda lst: [dict(t) for t in set([tuple(sorted(d.items())) for d in lst])]


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

        bs_name = {
            "field_type": "string",
            "element_type": "multiselect",
            "values": [],
            "key": "name",
            "title": "B S Name"
        }

        bs_alias = {
            "field_type": "string",
            "element_type": "multiselect",
            "values": [],
            "key": "alias",
            "title": "B S Alias"
        }

        bs_city = {
            "field_type": "string",
            "element_type": "multiselect",
            "values": [],
            "key": "city",
            "title": "BS City"
        }

        bs_state = {
            "field_type": "string",
            "element_type": "multiselect",
            "values": [],
            "key": "state",
            "title": "BS State"
        }

        # bs_technology={
        #         "field_type": "string",
        #         "element_type": "multiselect",
        #         "values": [],
        #         "key": "bs_technology",
        #         "title": "BS Technology"
        #         }

        bs_latitude = {
            "field_type": "string",
            "element_type": "multiselect",
            "values": [],
            "key": "latitude",
            "title": "BS Latitude"
        }

        bs_longitude = {
            "field_type": "string",
            "element_type": "multiselect",
            "values": [],
            "key": "longitude",
            "title": "BS Longitude"
        }

        sector_configured_on_dict = {
            "field_type": "string",
            "element_type": "multiselect",
            "values": [],
            "key": "sector_configured_on",
            "title": "Sector Configured On Device"
        }

        circuit_dict = {
            "field_type": "string",
            "element_type": "multiselect",
            "values": [],
            "key": "circuit_name",
            "title": "Circuit"
        }

        organizations = logged_in_user_organizations(self)

        for organization in organizations:
            base_stations = Sector.objects.filter(sector_configured_on__id__in= \
                                                      organization.device_set.values_list('id', flat=True)).values_list(
                'base_station', flat=True).distinct()

            for base_station_id in base_stations:
                try:
                    base_station_object = BaseStation.objects.get(id=base_station_id)
                    bs_name['values'].append({'id': base_station_object.id, 'value': base_station_object.name})
                    bs_alias['values'].append({'id': base_station_object.id, 'value': base_station_object.alias})
                    bs_city['values'].append({'id': base_station_object.city,
                                              'value': City.objects.get(id=base_station_object.city).city_name})
                    bs_state['values'].append({'id': base_station_object.state,
                                               'value': State.objects.get(id=base_station_object.state).state_name})
                    # bs_technology['values'].append({'id':base_station_object.bs_technology.id, 'value':base_station_object.bs_technology.name })
                    bs_latitude['values'].append({'id': base_station_object.id, 'value': base_station_object.latitude})
                    bs_longitude['values'].append(
                        {'id': base_station_object.id, 'value': base_station_object.longitude})

                    sectors = Sector.objects.filter(base_station=base_station_id)
                    for sector in sectors:
                        sector_configured_on_dict['values'].append({'id': sector.sector_configured_on.id, \
                                                                    'value': sector.sector_configured_on.device_name + ' (' + sector.sector_configured_on.ip_address + ')'})

                        if sector.circuit_set.values_list('id', flat=True):
                            circuit_dict['values'].append({'id': sector.circuit_set.values_list('id', flat=True)[0], \
                                                           'value': sector.circuit_set.values_list('name', flat=True)[
                                                               0]})


                except Exception as e:
                    logger.info(e.message + 'for base station id: %s' % (str(base_station_id)), exc_info=True)

        #removing duplicate values for the bs_city, bs_state and bs_technology
        bs_state['values'] = removing_duplicate_entries(bs_state['values'])
        bs_city['values'] = removing_duplicate_entries(bs_city['values'])
        # bs_technology['values']=removing_duplicate_entries(bs_technology['values'])

        self.result['data']['objects'].extend((bs_name, bs_alias,
                                               # bs_technology,
                                               bs_city, bs_state, bs_latitude, \
                                               bs_longitude, sector_configured_on_dict, circuit_dict))

        return HttpResponse(json.dumps(self.result))


class DeviceSetFilters(View):
    """
    Parses the get request from the filter form.
    """
    def get(self, request, total_count=None):
        """
        Handles the get request. Parse the get parameters and fetch the data as required in the request.

        :params self object
        :params request
        :return result
        """
        self.result = {
            "success": 0,
            "message": "Device Data",
            "data": {
                "meta": {},
                "objects": []
            }
        }

        result_data=list()
        request_query= self.request.GET.get('filters','')
        result_data= filter_gis_map(request_query)
        self.result['data']['objects']= {"id" : "mainNode", "name" : "mainNodeName", "data" :
                                        { "unspiderfy_icon" : "static/img/marker/slave01.png" }
                                        }

        self.result['data']['meta']['total_count']= total_count if total_count else len(result_data)
        self.result['data']['meta']['limit']= GIS_MAP_MAX_DEVICE_LIMIT
        self.result['data']['objects']['children']= result_data
        self.result['message']= 'Data Fetched Successfully.' if self.result['data']['objects']['children'] else 'No record found.'
        self.result['success']= 1 if self.result['data']['objects']['children'] else 0
        return HttpResponse(json.dumps(self.result))


def filter_gis_map(request_query):
    result_list = list()
    if request_query:
        request_query = eval(request_query)
        base_station_ids, circuit_ids = list(), list()
        exec_query_base_station = "base_station_ids = BaseStation.objects.filter("
        exec_query_circuit = "circuit_ids = Circuit.objects.filter("

        query_circuit, query_base_station = list(), list()
        for filter in request_query:

            if filter['field'] == 'circuit_name':
                query_circuit.append("Q(name__in=%s)" % (filter['value']))
            elif filter['field'] == 'city':

                city_ids = City.objects.filter(city_name__in=filter['value']).values_list('id', flat=True)
                query_base_station.append("Q(%s__in=%s)" % (filter['field'], str(city_ids)))

            elif filter['field'] == 'state':

                state_ids = State.objects.filter(state_name__in=filter['value']).values_list('id', flat=True)
                query_base_station.append("Q(%s__in=%s)" % (filter['field'], str(state_ids)))

            # elif filter['field']=='bs_technology':
            #
            #     dt_ids= DeviceTechnology.objects.filter(name__in= filter['value']).values_list('id', flat=True)
            #     query_base_station.append("Q(%s__in=%s)"%(filter['field'],str(dt_ids)))

            elif filter['field'] == 'sector_configured_on':
                #removing the () brackets and anything between it and then strip it to remove any space left.
                value_list = [re.sub("\([^]]*\)", lambda x: '', value).strip() for value in filter['value']]
                devices = Device.objects.filter(device_name__in=value_list).values_list('id', flat=True)
                bs_ids = Sector.objects.filter(sector_configured_on__in=devices).values_list('base_station__id',
                                                                                             flat=True)
                base_station_ids += bs_ids

            else:
                query_base_station.append("Q(%s__in=%s)" % (filter['field'], filter['value']))

        exec_query_base_station += " | ".join(query_base_station) + ").values_list('id', flat=True)"
        exec_query_circuit += " | ".join(query_circuit) + ").values_list('id', flat=True)"

        if query_base_station: exec exec_query_base_station
        if query_circuit: exec exec_query_circuit

        if base_station_ids:
            for base_station_id in base_station_ids:
                try:
                    base_station_info = prepare_result(base_station_id)
                    result_list.append(base_station_info)
                except Exception as e:
                    logger.error("SetFilters API Error Message: %s" % (e.message), exc_info=True)
                    pass

        if circuit_ids:
            for circuit_id in circuit_ids:
                circuit = Circuit.objects.get(id=circuit_id)
                base_station_id = circuit.sector.base_station.id
                try:
                    base_station_info = prepare_result(base_station_id)
                    result_list.append(base_station_info)
                except Exception as e:
                    logger.error("SetFilters API Error Message: %s" % (e.message), exc_info=True)
                    pass

    return result_list

def tech_marker_url(techno):
    """

    :param techno: technology P2P,
    :return: technology markers
    """
    if techno == "P2P":
        return "static/img/icons/mobilephonetower1.png"
    elif techno == "PMP":
        return "static/img/icons/mobilephonetower2.png"
    elif techno == "WiMAX":
        return "static/img/icons/mobilephonetower3.png"
    else:
        return "static/img/marker/icon2_small.png"

def prepare_result(base_station_id):
    base_station = BaseStation.objects.get(id=base_station_id)

    sectors = Sector.objects.filter(base_station=base_station.id)
    base_station_info = {
        'id': base_station.id,
        'name': base_station.name,
        'data': {
            'lat': base_station.latitude,
            'lon': base_station.longitude,
            "markerUrl": 'static/img/marker/slave01.png',
            'antena_height': 0,
            'vendor':','.join(sectors[0].bs_technology.device_vendors.values_list('name', flat=True)),
            'city': City.objects.get(id=base_station.city).city_name if base_station.city else 'N/A',
            'state': State.objects.get(id=base_station.state).state_name if base_station.state else 'N/A',
            'param': {
                'base_station': [
                    {
                        'name': 'name',
                        'title': 'Name',
                        'show': 1,
                        'value': base_station.name if base_station.name else 'N/A'
                    },
                    {
                        'name': 'alias',
                        'title': 'Alias',
                        'show': 1,
                        'value': base_station.alias if base_station.name else 'N/A'
                    },
                    {
                        'name': 'bs_site_id',
                        'title': 'Site Name',
                        'show': 1,
                        'value': base_station.bs_site_id if base_station.bs_site_id else 'N/A'
                    },
                    {
                        'name': 'bs_site_type',
                        'title': 'Site Type',
                        'show': 1,
                        'value': base_station.bs_site_type if base_station.bs_site_type else 'N/A'
                    },
                    {
                        'name': 'building_height',
                        'title': 'Building Height',
                        'show': 1,
                        'value': base_station.building_height if base_station.building_height else 'N/A'
                    },
                    {
                        'name': 'tower_height',
                        'title': 'Tower Height',
                        'show': 1,
                        'value': base_station.tower_height if base_station.tower_height else 'N/A'
                    },
                    {
                        'name': 'bs_city',
                        'title': 'City',
                        'show': 1,
                        'value': City.objects.get(id=base_station.city).city_name \
                                 if base_station.city else 'N/A'
                    },
                    {
                        'name': 'bs_state',
                        'title': 'State',
                        'show': 1,
                        'value': State.objects.get(id=base_station.state).state_name \
                                 if base_station.state else 'N/A'
                    },
                    {
                        'name': 'tower_height',
                        'title': 'Tower Height',
                        'show': 1,
                        'value': base_station.tower_height if base_station.tower_height else 'N/A'
                    },
                    {
                        'name': 'bs_address',
                        'title': 'Address',
                        'show': 1,
                        'value': base_station.address if base_station.address else 'N/A'
                    },
                    {
                        'name': 'bs_gps_type',
                        'title': 'GPS Type',
                        'show': 1,
                        'value': base_station.gps_type if base_station.gps_type else 'N/A'
                    },
                    {
                        'name':'bs_type',
                        'title':'BS Type',
                        'show':1,
                        'value': base_station.bs_type if base_station.bs_type else 'N/A'
                    }
                ],
                'backhual': [
                    {
                        'name': 'bh_configured_on',
                        'title': 'BH Configured On',
                        'show': 1,
                        'value': base_station.backhaul.bh_configured_on.device_name if base_station.backhaul.bh_configured_on.device_name else 'N/A'
                    },
                    {
                        'name': 'bh_capacity',
                        'title': 'BH Capacity',
                        'show': 1,
                        'value': base_station.backhaul.bh_capacity if base_station.backhaul.bh_capacity else 'N/A'
                    },
                    {
                        'name': 'bh_type',
                        'title': 'BH Type',
                        'show': 1,
                        'value': base_station.backhaul.bh_type if base_station.backhaul.bh_type else 'N/A'
                    },
                    {
                        'name': 'pe_ip',
                        'title': 'PE IP',
                        'show': 1,
                        'value': base_station.backhaul.pe_ip if base_station.backhaul.pe_ip else 'N/A'
                    },
                    {
                        'name': 'bh_connectivity',
                        'title': 'BH Connectivity',
                        'show': 1,
                        'value': base_station.backhaul.bh_connectivity if base_station.backhaul.bh_connectivity else 'N/A'
                    },
                    ]}

        },
        }

    base_station_info['data']['param']['sector'] = []

    for sector in sectors:
        if Sector.objects.get(id=sector.id).sector_configured_on.is_deleted == 1:
            continue

        # for bsname in base_station_info['data']:
        #     if 'technology' not in bsname:
        #         base_station_info['data']["technology"] = sector.bs_technology.name if sector.bs_technology else 'N/A'
        #     if 'vendor' not in bsname:
        #         base_station_info['data']["vendor"] = ','.join(sector.bs_technology.device_vendors.values_list('name', flat=True))
        #         'vendor':','.join(base_station.bs_technology.device_vendors.values_list('name', flat=True)),

        base_station_info['data']['param']['sector'] += [{
                                                             "color": sector.frequency.color_hex_value if hasattr(
                                                                 sector,
                                                                 'frequency') and sector.frequency else 'rgba(74,72,94,0.58)',
                                                             'radius': sector.cell_radius if sector.cell_radius else 0,
                                                             'azimuth_angle': sector.antenna.azimuth_angle if sector.antenna else 0,
                                                             'beam_width': sector.antenna.beam_width if sector.antenna else 0,
                                                             'orientation': sector.antenna.polarization if sector.antenna else "vertical",
                                                             'technology':sector.bs_technology.name if sector.bs_technology else 'N/A',
                                                             'info': [{
                                                                          'name': 'sector_name',
                                                                          'title': 'Sector Name',
                                                                          'show': 1,
                                                                          'value': sector.name
                                                                      },
                                                                      {
                                                                          'name': 'type_of_bs',
                                                                          'title': 'Type of BS',
                                                                          'show': 1,
                                                                          'value': sector.base_station.bs_type \
                                                                              if sector.base_station.bs_type else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'building_height',
                                                                          'title': 'Building Height',
                                                                          'show': 1,
                                                                          'value': base_station.building_height \
                                                                              if base_station.building_height else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'site_name',
                                                                          'title': 'Site Name',
                                                                          'show': 1,
                                                                          'value': base_station.bs_site_id  if base_station.bs_site_id else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'site_type',
                                                                          'title': 'Site Type',
                                                                          'show': 1,
                                                                          'value': base_station.bs_site_type \
                                                                              if base_station.bs_site_type else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'address',
                                                                          'title': 'Address',
                                                                          'show': 1,
                                                                          'value': base_station.address \
                                                                              if base_station.address else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'type_of_gps',
                                                                          'title': 'Type of GPS',
                                                                          'show': 1,
                                                                          'value': base_station.gps_type \
                                                                              if base_station.gps_type else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'tower_height',
                                                                          'title': 'Tower Height',
                                                                          'show': 1,
                                                                          'value': base_station.tower_height if base_station.tower_height else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'type_of_antenna',
                                                                          'title': 'Antenna Type',
                                                                          'show': 1,
                                                                          'value': sector.antenna.mount_type if sector.antenna else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'antenna_tilt',
                                                                          'title': 'Antenna Tilt',
                                                                          'show': 1,
                                                                          'value': sector.antenna.tilt if sector.antenna else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'antenna_height',
                                                                          'title': 'Antenna Height',
                                                                          'show': 1,
                                                                          'value': sector.antenna.height if sector.antenna else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'antenna_bw',
                                                                          'title': 'Antenna Beam Width',
                                                                          'show': 1,
                                                                          'value': sector.antenna.beam_width if sector.antenna else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'antenna_azimuth',
                                                                          'title': 'Antenna Azimuth Angle',
                                                                          'show': 1,
                                                                          'value': sector.antenna.azimuth_angle if sector.antenna else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'antenna_splitter_installed',
                                                                          'title': 'Installation of Splitter',
                                                                          'show': 1,
                                                                          'value': sector.antenna.splitter_installed if sector.antenna else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'city',
                                                                          'title': 'City',
                                                                          'show': 1,
                                                                          'value': City.objects.get(
                                                                              id=base_station.city).city_name \
                                                                              if sector.base_station.city else 'N/A'
                                                                      },
                                                                      {
                                                                          'name': 'state',
                                                                          'title': 'State',
                                                                          'show': 1,
                                                                          'value': State.objects.get(
                                                                              id=base_station.state).state_name \
                                                                              if base_station.state else 'N/A'
                                                                      },
                                                                      ],
                                                             'sub_station': []

                                                         }]

        circuits = Circuit.objects.filter(sector=sector.id)
        for circuit in circuits:
            substation = SubStation.objects.get(id=circuit.sub_station.id)
            substation_device = Device.objects.get(id=substation.device.id)
            if substation_device.is_deleted == 1:
                continue
            substation_list= [{
                                'id': substation.id,
                                'name': substation.name,
                                'device_name': substation.device.device_name,
                                'data': {
                                    "lat": substation_device.latitude,
                                    "lon": substation_device.longitude,
                                    "antenna_height": substation.antenna.height if substation.antenna else 0,
                                    "technology":sector.bs_technology.name,
                                    "markerUrl": "static/img/marker/icon4_small.png",
                                    "show_link": 1,
                                    "link_color": sector.frequency.color_hex_value if hasattr(
                                        sector,
                                        'frequency') and sector.frequency else 'rgba(74,72,94,0.58)',
                                    'param': {
                                        'sub_station': [
                                            {
                                                'name': 'name',
                                                'title': 'SS Name',
                                                'show': 1,
                                                'value': substation.name if substation.name else 'N/A'
                                            },
                                            {
                                                'name': 'alias',
                                                'title': 'Alias',
                                                'show': 1,
                                                'value': substation_device.device_alias if substation_device.device_alias else 'N/A'
                                            },
                                            {
                                                'name': 'ss_ip',
                                                'title': 'SS IP',
                                                'show': 1,
                                                'value': substation_device.ip_address if substation_device.ip_address else 'N/A'

                                            },
                                            {
                                                'name': 'cktid',
                                                'title': 'Circuit ID',
                                                'show': 1,
                                                'value': circuit.circuit_id if circuit.circuit_id else 'N/A'
                                            },
                                            {
                                                'name': 'qos_bandwidth',
                                                'title': 'QOS(BW)',
                                                'show': 1,
                                                'value': circuit.qos_bandwidth if circuit.qos_bandwidth else 'N/A'
                                            },
                                            {
                                                'name': 'ss_technology',
                                                'title': 'Technology',
                                                'show': 1,
                                                'value': sector.bs_technology.name if sector.bs_technology else 'N/A'
                                            },
                                            {
                                                'name': 'antenna_height',
                                                'title': 'Antenna Height',
                                                'show': 1,
                                                'value': sector.antenna.height if sector.antenna else 'N/A'
                                            },
                                            {
                                                'name': 'building_height',
                                                'title': 'Building Height',
                                                'show': 1,
                                                'value': substation.building_height \
                                                    if substation.building_height else 'N/A'
                                            },
                                            {
                                                'name': 'tower_height',
                                                'title': 'tower_height',
                                                'show': 1,
                                                'value': substation.tower_height \
                                                    if substation.tower_height else 'N/A'
                                            },
                                            {
                                                'name': 'polarisation',
                                                'title': 'Polarisation',
                                                'show': 1,
                                                'value': sector.antenna.polarization \
                                                    if sector.antenna else 'N/A'
                                            },
                                            {
                                                'name': 'mount_type',
                                                'title': 'SS MountType',
                                                'show': 1,
                                                'value': sector.antenna.mount_type if sector.antenna else 'N/A'
                                            },
                                            {


                                                'name': 'antenna_type',
                                                'title': 'Antenna Type',
                                                'show': 1,
                                                'value': sector.antenna.antenna_type if sector.antenna else 'N/A'
                                            },
                                            {
                                                'name': 'ethernet_extender',
                                                'title': 'Ethernet Extender',
                                                'show': 1,
                                                'value': sector.antenna.ethernet_extender \
                                                    if hasattr(
                                                    sector.antenna,
                                                    'ethernet_extender') and sector.antenna  else 'N/A'
                                            },
                                            {
                                                'name': 'cable_length',
                                                'title': 'Cable Length',
                                                'show': 1,
                                                'value': sector.antenna.cable_length \
                                                    if hasattr(
                                                    sector.antenna,
                                                    'cable_length') and sector.antenna else 'N/A'
                                            },
                                            {
                                                'name': 'customer_address',
                                                'title': 'Customer Address',
                                                'show': 1,
                                                'value': Customer.objects.get(
                                                    id=sector.circuit_set.values(
                                                        'customer')).address \
                                                    if 'customer' in sector.circuit_set.values() else 'N/A'
                                            },
                                            {
                                                'name': 'date_of_acceptance',
                                                'title': 'Date of Acceptance',
                                                'show': 1,
                                                'value': Customer.objects.get(
                                                    id=sector.circuit_set.values(
                                                        'customer')).date_of_acceptance \
                                                    if 'date_of_acceptance' in sector.circuit_set.values(
                                                    'date_of_acceptance') else 'N/A'
                                            },
                                            {
                                                'name': 'dl_rssi_during_acceptance',
                                                'title': 'RSSI During Acceptance' if substation_device.device_technology == \
                                                          DeviceTechnology.objects.get(name='P2P').id else 'DL RSSI During Acceptance',
                                                'show': 1,
                                                 'value': substation.circuit_set.values_list('dl_rssi_during_acceptance', flat=True)[0] \
                                                    if substation.circuit_set.values_list('dl_rssi_during_acceptance', flat=True)[0] else 'N/A'
                                            }
                                        ],
                                        }
                                }
                            }]

            if substation_device.device_technology == DeviceTechnology.objects.get(name='WiMAX').id:
                substation_list[0]['data']['param']['sub_station']+=[
                    {
                        'name': 'dl_cinr_during_acceptance',
                        'title': 'DL CINR RSSI During Acceptance',
                        'show': 1,
                        'value': substation.circuit_set.values_list('dl_cinr_during_acceptance', flat=True)[0] \
                            if substation.circuit_set.values_list('dl_cinr_during_acceptance', flat=True)[0] else 'N/A'
                    }]

            elif substation_device.device_technology == DeviceTechnology.objects.get(name='PMP').id:
                substation_list[0]['data']['param']['sub_station']+=[
                    {
                        'name': 'jitter_value_during_acceptance',
                        'title': 'Jitter Value During Acceptance',
                        'show': 1,
                        'value': substation.circuit_set.values_list('jitter_value_during_acceptance', flat=True)[0] \
                            if substation.circuit_set.values_list('jitter_value_during_acceptance', flat=True)[0] else 'N/A'
                    }]

            elif substation_device.device_technology == DeviceTechnology.objects.get(name='P2P').id:
                substation_list[0]['data']['param']['sub_station']+=[
                    {
                        'name': 'customer_name',
                        'title': 'Customer Name',
                        'show': 1,
                        'value': Customer.objects.get(id= substation.circuit_set.values_list('customer_id', flat=True)[0]).name \
                            if substation.circuit_set.values_list('customer_id', flat=True)[0] else 'N/A'
                    },
                    {
                        'name': 'antenna_mount_type',
                        'title': 'Antenna Mount Type',
                        'show': 1,
                        'value': Antenna.objects.get(id=substation.antenna.id).mount_type \
                            if substation.antenna.id else 'N/A'
                    },
                    {
                        'name': 'throughput_during_acceptance',
                        'title': 'Throughput During Acceptance',
                        'show': 1,
                        'value': substation.circuit_set.values_list('throughput_during_acceptance', flat=True)[0] \
                            if substation.circuit_set.values_list('throughput_during_acceptance', flat=True)[0] else 'N/A'
                    },
                    {
                        'name': 'bh_bso',
                        'title': 'BH BSO',
                        'show': 1,
                        'value': base_station.bh_bso if base_station.bh_bso else 'N/A'
                    }]

            base_station_info['data']['param']['sector'][-1]['sub_station']+= substation_list

    return base_station_info