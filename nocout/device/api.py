"""
===============================================
Module contains api's specific to 'device' app.
===============================================

Location:
* /nocout_gis/nocout/device/api.py

List of constructs:
=======
Classes
=======
* DeviceStatsApi
* DeviceFilterApi
* LPServicesApi
* FetchLPDataApi
* FetchLPSettingsApi
* FetchThresholdConfigurationApi
* FetchThematicSettingsApi
* BulkFetchLPDataApi

=======
Methods
=======
* prepare_raw_result
* nocout_live_polling
"""

import ast
import json
import ujson
import urllib
import requests
import logging
from copy import deepcopy
from pprint import pformat
from multiprocessing import Process, Queue
from django.db.models import Count
from django.views.generic.base import View
from django.http import HttpResponse
from device.models import Device, DeviceType, DeviceVendor, DeviceTechnology, State, City
from nocout.utils import logged_in_user_organizations
from nocout.utils.util import time_it, cached_all_gis_inventory, cache_for
from service.models import DeviceServiceConfiguration, Service, ServiceDataSource
from django.contrib.staticfiles.templatetags.staticfiles import static
from site_instance.models import SiteInstance
from performance.models import Topology
import performance.utils as perf_util
from service.utils.util import service_data_sources
from sitesearch.views import prepare_raw_bs_result
from nocout.settings import GIS_MAP_MAX_DEVICE_LIMIT, CACHE_TIME
from user_profile.models import UserProfile
from inventory.models import (BaseStation, LivePollingSettings,
                              ThresholdConfiguration, ThematicSettings,
                              PingThematicSettings, UserThematicSettings,
                              UserPingThematicSettings)

logger = logging.getLogger(__name__)


@cache_for(CACHE_TIME.get('INVENTORY', 300))
def prepare_raw_result(bs_dict=None):
    """
    To fetch dictionary of base station objects.

    Args:
        bs_dict (list): List of dictionaries containing inventory wrt the base stations.
                        For e.g.,
                        [
                            {
                                'SS_LONGITUDE': None,
                                'THROUHPUT': None,
                                'BSCITYID': 842L,
                                'SECTOR_FRAME_LENGTH': None,
                                'BSTYPE': u'',
                                'SECTOR_FREQUENCY_ID': None,
                                'BH_PORT': u'Fa0/24',
                                'SECTOR_BS_ID': None,
                                'POP': None,
                                'SID': None,
                                'BSLAT': 18.5288,
                                'BSSITETYPE': u'RTT',
                                'SS_NAME': None,
                                'BH_AGGR_PORT': None,
                                'POP_TYPE': None,
                                'BHID': 1L,
                                'SSANTENNAMOUNTTYPE': None,
                                'CCID': None,
                                'SECTOR_TX': None,
                                'SS_ETH_EXT': None,
                                'BH_CONNECTIVITY': u'Onnet',
                                'SS_VERSION': None,
                                'SECTOR_PLANNED_FREQUENCY': None,
                                'SS_DEVICE_ID': None,
                                'SSDEVICENAME': None,
                                'SECTOR_SECTOR_ID': None,
                                'SS_MAC': None,
                                'SECTOR_FREQUENCY': None,
                                'BH_TYPE': u'',
                                'SS_TYPE': None,
                                'BSADDRESS': u'TTMLOfficeSiteID: 1301Address: ,
                                TTMLOffice,
                                NearSanchetiHosp,
                                Shivajinagar,
                                Mahaarashtr/Pune//Pincode-411005',
                                'BSMAINTENANCESTATUS': u'Yes',
                                'CINR': None,
                                'POP_IP': None,
                                'SS_ANTENNA_MAKE': None,
                                'SECTOR_TECH': None,
                                'SECTOR_ID': None,
                                'CIRCUIT_TYPE': None,
                                'SECTOR_ALIAS': None,
                                'SECTOR_MRC': None,
                                'DR_CONF_ON_ID': None,
                                'SECTOR_TYPE_ID': None,
                                'SECTOR_VENDOR': None,
                                'SS_GMAP_ICON': None,
                                'DR_CONF_ON_IP': None,
                                'BSSITEID': u'1301.0',
                                'BSTAG2': u'',
                                'BSTAG1': u'',
                                'SECTOR_ANTENNA_GAIN': None,
                                'QOS': None,
                                'SECTOR_CONF_ON_MAC': None,
                                'BH_CAPACITY': 100L,
                                'SECTOR_GMAP_ICON': None,
                                'AGGR': u'10002',
                                'RSSI': None,
                                'AGGR_TYPE': u'Switch',
                                'SS_ANTENNA_GAIN': None,
                                'SECTOR_ANTENNA_HEIGHT': None,
                                'SS_ANTENNA_REFLECTOR': None,
                                'BSINFRAPROVIDER': u'TTML',
                                'SECTOR_RX': None,
                                'SS_CUST_ADDR': None,
                                'SS_ANTENNA_TILT': None,
                                'BSALIAS': u'TTMLOffice',
                                'BSGPSTYPE': u'UGPS',
                                'BSCOUNTRY': u'India',
                                'BSBUILDINGHGT': 18.0,
                                'SSID': None,
                                'BSSTATEID': 16L,
                                'SECTOR_CONF_ON_ALIAS': None,
                                'BH_PE_IP': u'192.168.224.80',
                                'SSIP': None,
                                'SECTOR_TECH_ID': None,
                                'SECTOR_FREQUENCY_COLOR': None,
                                'BH_DEVICE_PORT': None,
                                'SECTOR_FREQUENCY_RADIUS': None,
                                'SECTOR_ANTENNA_SYNC_SPLITTER': None,
                                'SSDEVICEALIAS': None,
                                'BSHSSUUSED': u'',
                                'SECTOR_CONF_ON_NAME': None,
                                'AGGR_TECH': u'Switch',
                                'BSCONV_TYPE': None,
                                'BSSTATE': u'Maharashtra',
                                'BHTYPEID': 12L,
                                'AGGR_IP': u'172.21.254.235',
                                'BH_CIRCUIT_ID': u'IOR_163134',
                                'DATE_OF_ACCEPT': None,
                                'CID': None,
                                'SS_ANTENNA_AZMINUTH_ANGLE': None,
                                'SS_BUILDING_HGT': None,
                                'SS_TOWER_HGT': None,
                                'SECTOR_ANTENNA_MAKE': None,
                                'BHCONF': u'10001',
                                'JITTER': None,
                                'BSHSSUPORT': u'',
                                'BH_PE_HOSTNAME': u'pu-shi-shi-mi12-rt01',
                                'SECTOR_BEAM_WIDTH': None,
                                'SS_ANTENNA_POLARIZATION': None,
                                'BH_TTSL_CIRCUIT_ID': u'NA',
                                'SECTOR_CONF_ON': None,
                                'SS_ICON': None,
                                'BSID': 1L,
                                'SECTOR_ANTENNA_AZMINUTH_ANGLE': None,
                                'SS_TECH': None,
                                'BSNAME': u'ttml_office_pun_mah',
                                'SECTOR_ANTENNA_TILT': None,
                                'BHTECH': u'Switch',
                                'BHCONF_IP': u'10.171.137.4',
                                'SS_CABLE_LENGTH': None,
                                'DR_CONF_ON': None,
                                'BH_DEVICE_ID': 10001L,
                                'SS_ANTENNA_HEIGHT': None,
                                'SECTOR_RFBW': None,
                                'BSTOWERHEIGHT': 21.0,
                                'BSCONV': None,
                                'SECTORANTENNAMOUNTTYPE': None,
                                'SS_VENDOR': None,
                                'SECTOR_CELL_RADIUS': None,
                                'SECTOR_PORT': None,
                                'CUSTID': None,
                                'SECTOR_NAME': None,
                                'SECTOR_ANTENNA_REFLECTOR': None,
                                'SS_ANTENNA_SYNC_SPLITTER': None,
                                'SECTOR_DR': None,
                                'BSCITY': u'Pune',
                                'SS_ALIAS': None,
                                'SECTOR_MODULATION': None,
                                'BSBHBSO': u'',
                                'SSDEVICETYPE': None,
                                'CUST': None,
                                'SECTOR_ANTENNA_SPLITTER': None,
                                'SECTOR_CONF_ON_ID': None,
                                'SS_BEAM_WIDTH': None,
                                'CALIAS': None,
                                'POP_TECH': None,
                                'BHTECHID': 7L,
                                'SS_ANTENNA_SPLITTER': None,
                                'SS_ANTENNA_TYPE': None,
                                'SS_TECH_ID': None,
                                'SS_LATITUDE': None,
                                'SECTOR_CONF_ON_IP': None,
                                'BSCONV_IP': None,
                                'SS_TYPE_ID': None,
                                'SECTOR_ANTENNA_POLARIZATION': None,
                                'BSLONG': 73.8533,
                                'SECTOR_ANTENNA_TYPE': None,
                                'BHTYPE': u'Switch',
                                'BSCONV_TECH': None,
                                'BSSWITCH': u'10.171.137.4',
                                'SS_SERIAL_NO': None,
                                'SSHGT': None,
                                'SECTOR_ICON': None,
                                'SECTOR_TYPE': None
                            }
                        ]

    Returns:
        bs_result(dict): Dictionary with base station id's as key and corresponding base station inventory as value.
                         For e.g.,
                            {
                            1L: [
                                    {
                                        'SS_LONGITUDE': None,
                                        'THROUHPUT': None,
                                        'BSCITYID': 842L,
                                        'SECTOR_FRAME_LENGTH': None,
                                        'BSTYPE': u'',
                                        'SECTOR_FREQUENCY_ID': None,
                                        'BH_PORT': u'Fa0/24',
                                        'SECTOR_BS_ID': None,
                                        'POP': None,
                                        'SID': None,
                                        'BSLAT': 18.5288,
                                        'BSSITETYPE': u'RTT',
                                        'SS_NAME': None,
                                        'BH_AGGR_PORT': None,
                                        'POP_TYPE': None,
                                        'BHID': 1L,
                                        'SSANTENNAMOUNTTYPE': None,
                                        'CCID': None,
                                        'SECTOR_TX': None,
                                        'SS_ETH_EXT': None,
                                        'BH_CONNECTIVITY': u'Onnet',
                                        'SS_VERSION': None,
                                        'SECTOR_PLANNED_FREQUENCY': None,
                                        'SS_DEVICE_ID': None,
                                        'SSDEVICENAME': None,
                                        'SECTOR_SECTOR_ID': None,
                                        'SS_MAC': None,
                                        'SECTOR_FREQUENCY': None,
                                        'BH_TYPE': u'',
                                        'SS_TYPE': None,
                                        'BSADDRESS': u'TTMLOfficeSiteID: 1301Address: ,
                                        TTMLOffice,
                                        NearSanchetiHosp,
                                        Shivajinagar,
                                        Mahaarashtr/Pune//Pincode-411005',
                                        'BSMAINTENANCESTATUS': u'Yes',
                                        'CINR': None,
                                        'POP_IP': None,
                                        'SS_ANTENNA_MAKE': None,
                                        'SECTOR_TECH': None,
                                        'SECTOR_ID': None,
                                        'CIRCUIT_TYPE': None,
                                        'SECTOR_ALIAS': None,
                                        'SECTOR_MRC': None,
                                        'DR_CONF_ON_ID': None,
                                        'SECTOR_TYPE_ID': None,
                                        'SECTOR_VENDOR': None,
                                        'SS_GMAP_ICON': None,
                                        'DR_CONF_ON_IP': None,
                                        'BSSITEID': u'1301.0',
                                        'BSTAG2': u'',
                                        'BSTAG1': u'',
                                        'SECTOR_ANTENNA_GAIN': None,
                                        'QOS': None,
                                        'SECTOR_CONF_ON_MAC': None,
                                        'BH_CAPACITY': 100L,
                                        'SECTOR_GMAP_ICON': None,
                                        'AGGR': u'10002',
                                        'RSSI': None,
                                        'AGGR_TYPE': u'Switch',
                                        'SS_ANTENNA_GAIN': None,
                                        'SECTOR_ANTENNA_HEIGHT': None,
                                        'SS_ANTENNA_REFLECTOR': None,
                                        'BSINFRAPROVIDER': u'TTML',
                                        'SECTOR_RX': None,
                                        'SS_CUST_ADDR': None,
                                        'SS_ANTENNA_TILT': None,
                                        'BSALIAS': u'TTMLOffice',
                                        'BSGPSTYPE': u'UGPS',
                                        'BSCOUNTRY': u'India',
                                        'BSBUILDINGHGT': 18.0,
                                        'SSID': None,
                                        'BSSTATEID': 16L,
                                        'SECTOR_CONF_ON_ALIAS': None,
                                        'BH_PE_IP': u'192.168.224.80',
                                        'SSIP': None,
                                        'SECTOR_TECH_ID': None,
                                        'SECTOR_FREQUENCY_COLOR': None,
                                        'BH_DEVICE_PORT': None,
                                        'SECTOR_FREQUENCY_RADIUS': None,
                                        'SECTOR_ANTENNA_SYNC_SPLITTER': None,
                                        'SSDEVICEALIAS': None,
                                        'BSHSSUUSED': u'',
                                        'SECTOR_CONF_ON_NAME': None,
                                        'AGGR_TECH': u'Switch',
                                        'BSCONV_TYPE': None,
                                        'BSSTATE': u'Maharashtra',
                                        'BHTYPEID': 12L,
                                        'AGGR_IP': u'172.21.254.235',
                                        'BH_CIRCUIT_ID': u'IOR_163134',
                                        'DATE_OF_ACCEPT': None,
                                        'CID': None,
                                        'SS_ANTENNA_AZMINUTH_ANGLE': None,
                                        'SS_BUILDING_HGT': None,
                                        'SS_TOWER_HGT': None,
                                        'SECTOR_ANTENNA_MAKE': None,
                                        'BHCONF': u'10001',
                                        'JITTER': None,
                                        'BSHSSUPORT': u'',
                                        'BH_PE_HOSTNAME': u'pu-shi-shi-mi12-rt01',
                                        'SECTOR_BEAM_WIDTH': None,
                                        'SS_ANTENNA_POLARIZATION': None,
                                        'BH_TTSL_CIRCUIT_ID': u'NA',
                                        'SECTOR_CONF_ON': None,
                                        'SS_ICON': None,
                                        'BSID': 1L,
                                        'SECTOR_ANTENNA_AZMINUTH_ANGLE': None,
                                        'SS_TECH': None,
                                        'BSNAME': u'ttml_office_pun_mah',
                                        'SECTOR_ANTENNA_TILT': None,
                                        'BHTECH': u'Switch',
                                        'BHCONF_IP': u'10.171.137.4',
                                        'SS_CABLE_LENGTH': None,
                                        'DR_CONF_ON': None,
                                        'BH_DEVICE_ID': 10001L,
                                        'SS_ANTENNA_HEIGHT': None,
                                        'SECTOR_RFBW': None,
                                        'BSTOWERHEIGHT': 21.0,
                                        'BSCONV': None,
                                        'SECTORANTENNAMOUNTTYPE': None,
                                        'SS_VENDOR': None,
                                        'SECTOR_CELL_RADIUS': None,
                                        'SECTOR_PORT': None,
                                        'CUSTID': None,
                                        'SECTOR_NAME': None,
                                        'SECTOR_ANTENNA_REFLECTOR': None,
                                        'SS_ANTENNA_SYNC_SPLITTER': None,
                                        'SECTOR_DR': None,
                                        'BSCITY': u'Pune',
                                        'SS_ALIAS': None,
                                        'SECTOR_MODULATION': None,
                                        'BSBHBSO': u'',
                                        'SSDEVICETYPE': None,
                                        'CUST': None,
                                        'SECTOR_ANTENNA_SPLITTER': None,
                                        'SECTOR_CONF_ON_ID': None,
                                        'SS_BEAM_WIDTH': None,
                                        'CALIAS': None,
                                        'POP_TECH': None,
                                        'BHTECHID': 7L,
                                        'SS_ANTENNA_SPLITTER': None,
                                        'SS_ANTENNA_TYPE': None,
                                        'SS_TECH_ID': None,
                                        'SS_LATITUDE': None,
                                        'SECTOR_CONF_ON_IP': None,
                                        'BSCONV_IP': None,
                                        'SS_TYPE_ID': None,
                                        'SECTOR_ANTENNA_POLARIZATION': None,
                                        'BSLONG': 73.8533,
                                        'SECTOR_ANTENNA_TYPE': None,
                                        'BHTYPE': u'Switch',
                                        'BSCONV_TECH': None,
                                        'BSSWITCH': u'10.171.137.4',
                                        'SS_SERIAL_NO': None,
                                        'SSHGT': None,
                                        'SECTOR_ICON': None,
                                        'SECTOR_TYPE': None
                                    }
                                ]
                            }
    """
    bs_list = []
    bs_result = {}

    # Preparing result by pivoting via basestation id.
    if len(bs_dict):
        for bs in bs_dict:
            BSID = bs['BSID']
            if BSID not in bs_list:
                bs_list.append(BSID)
                bs_result[BSID] = []
            bs_result[BSID].append(bs)

    return bs_result


class DeviceStatsApi(View):
    """
    Get base stations inventory with specified limit. If there is no limit parameter
    in request then it will fetch complete inventory.

    Usage: Shows inventory data on GIS maps.

    URL: /device/stats/?total_count=0&page_number=1

    Args:
        page_number (unicode): Page number or offset for inventory data.
        total_count (unicode): Number of the devices needs to be shown.

    Returns:
        result (dict): Response send in json format.
                       For e.g.,
                             {
                                "success": 0,
                                "message": "Device Loading Completed",
                                "data": {
                                    "meta": {

                                    },
                                    "objects": None
                                }
                            }
    """
    # Formatted inventory wrt the base stations.
    raw_result = prepare_raw_result(cached_all_gis_inventory(monitored_only=True))

    # @time_it()
    def get(self, request):

        self.result = {
            "success": 0,
            "message": "Device Loading Completed",
            "data": {
                "meta": {},
                "objects": None
            }
        }

        # page_number= request.GET['page_number']
        # limit= request.GET['limit']

        organizations = logged_in_user_organizations(self)

        if organizations:
            page_number = self.request.GET.get('page_number', None)
            start, offset = None, None
            if page_number:
                # Setting the Start and Offset limit for the Query.
                offset = int(page_number) * GIS_MAP_MAX_DEVICE_LIMIT
                start = offset - GIS_MAP_MAX_DEVICE_LIMIT

            bs_id = BaseStation.objects.prefetch_related('sector', 'backhaul').filter(
                organization__in=organizations)[start:offset].annotate(
                dcount=Count('name')).values_list('id', flat=True)

            # If the total count key is not in the meta objects then run the query.
            total_count = self.request.GET.get('total_count')

            if not int(total_count):
                total_count = BaseStation.objects.filter(organization__in=organizations).annotate(
                    dcount=Count('name')).count()

                self.result['data']['meta']['total_count'] = total_count
            else:
                # Other than first request the total_count will be echoed back
                # and then can be placed in the result.
                total_count = self.request.GET.get('total_count')
                self.result['data']['meta']['total_count'] = total_count

            self.result['data']['meta']['limit'] = GIS_MAP_MAX_DEVICE_LIMIT
            self.result['data']['meta']['offset'] = offset
            self.result['data']['objects'] = {
                "id": "mainNode",
                "name": "mainNodeName",
                "data": {"unspiderfy_icon": "static/img/icons/bs.png"}
            }
            self.result['data']['objects']['children'] = list()

            for bs in bs_id:
                if bs in self.raw_result:
                    base_station_info = prepare_raw_bs_result(self.raw_result[bs])
                    self.result['data']['objects']['children'].append(base_station_info)

            self.result['data']['meta']['device_count'] = len(self.result['data']['objects']['children'])
            self.result['message'] = 'Data Fetched Successfully.'
            self.result['success'] = 1

        return HttpResponse(ujson.dumps(self.result), content_type="application/json")


class DeviceFilterApi(View):
    """
    Get detailed data for technologies, vendors, models, state, city etc. in a dictionary.

    Usage: Used in device tree structure and filtering technologies in live poll view.

    URL: /device/filter/0/

    Args:
        for_map (unicode): Specify that data is for map or other functionaliy.

    Returns:
        result (dict): Response send in json format.
                       For e.g.,
                             {
                                'message': 'DataFetchedSuccessfully.',
                                'data': {
                                    'meta': {

                                    },
                                    'objects': {
                                        'vendor': {
                                            'data': [
                                                {
                                                    'tech_name': u'Default',
                                                    'id': 1L,
                                                    'value': u'Default',
                                                    'tech_id': 1L
                                                },
                                                {
                                                    'tech_name': u'P2P',
                                                    'id': 2L,
                                                    'value': u'Radwin',
                                                    'tech_id': 2L
                                                },
                                                {
                                                    'tech_name': u'WiMAX',
                                                    'id': 3L,
                                                    'value': u'Telisma',
                                                    'tech_id': 3L
                                                },
                                                {
                                                    'tech_name': u'WiMAX',
                                                    'id': 7L,
                                                    'value': u'RAD',
                                                    'tech_id': 3L
                                                },
                                                {
                                                    'tech_name': u'WiMAX',
                                                    'id': 8L,
                                                    'value': u'MROtek',
                                                    'tech_id': 3L
                                                },
                                                {
                                                    'tech_name': u'PMP',
                                                    'id': 4L,
                                                    'value': u'Cambium',
                                                    'tech_id': 4L
                                                },
                                                {
                                                    'tech_name': u'PMP',
                                                    'id': 7L,
                                                    'value': u'RAD',
                                                    'tech_id': 4L
                                                },
                                                {
                                                    'tech_name': u'PMP',
                                                    'id': 8L,
                                                    'value': u'MROtek',
                                                    'tech_id': 4L
                                                },
                                                {
                                                    'tech_name': u'Switch',
                                                    'id': 9L,
                                                    'value': u'Switch',
                                                    'tech_id': 7L
                                                },
                                                {
                                                    'tech_name': u'TCLPOP',
                                                    'id': 7L,
                                                    'value': u'RAD',
                                                    'tech_id': 8L
                                                },
                                                {
                                                    'tech_name': u'TCLPOP',
                                                    'id': 8L,
                                                    'value': u'MROtek',
                                                    'tech_id': 8L
                                                },
                                                {
                                                    'tech_name': u'TCLPTPPOP',
                                                    'id': 2L,
                                                    'value': u'Radwin',
                                                    'tech_id': 9L
                                                },
                                                {
                                                    'tech_name': u'PTP-BH',
                                                    'id': 2L,
                                                    'value': u'Radwin',
                                                    'tech_id': 10L
                                                },
                                                {
                                                    'id': 1L,
                                                    'value': u'Default'
                                                },
                                                {
                                                    'id': 2L,
                                                    'value': u'Radwin'
                                                },
                                                {
                                                    'id': 3L,
                                                    'value': u'Telisma'
                                                },
                                                {
                                                    'id': 4L,
                                                    'value': u'Cambium'
                                                },
                                                {
                                                    'id': 7L,
                                                    'value': u'RAD'
                                                },
                                                {
                                                    'id': 8L,
                                                    'value': u'MROtek'
                                                },
                                                {
                                                    'id': 9L,
                                                    'value': u'Switch'
                                                }
                                            ]
                                        },
                                        'state': {
                                            'data': [
                                                {
                                                    'id': 1L,
                                                    'value': u'AndhraPradesh'
                                                },
                                                {
                                                    'id': 2L,
                                                    'value': u'ArunachalPradesh'
                                                }
                                            ]
                                        },
                                        'technology': {
                                            'data': [
                                                {
                                                    'id': 1L,
                                                    'value': u'Default'
                                                },
                                                {
                                                    'id': 2L,
                                                    'value': u'P2P'
                                                },
                                                {
                                                    'id': 3L,
                                                    'value': u'WiMAX'
                                                },
                                                {
                                                    'id': 4L,
                                                    'value': u'PMP'
                                                },
                                                {
                                                    'id': 7L,
                                                    'value': u'Switch'
                                                },
                                                {
                                                    'id': 8L,
                                                    'value': u'TCLPOP'
                                                },
                                                {
                                                    'id': 9L,
                                                    'value': u'TCLPTPPOP'
                                                },
                                                {
                                                    'id': 10L,
                                                    'value': u'PTP-BH'
                                                }
                                            ]
                                        },
                                        'city': {
                                            'data': [
                                                {
                                                    'state_id': 1L,
                                                    'id': 1L,
                                                    'value': u'Adilabad',
                                                    'state_name': u'AndhraPradesh'
                                                },
                                                {
                                                    'state_id': 1L,
                                                    'id': 2L,
                                                    'value': u'Adoni',
                                                    'state_name': u'AndhraPradesh'
                                                },
                                                {
                                                    'state_id': 1L,
                                                    'id': 3L,
                                                    'value': u'Amadalavalasa',
                                                    'state_name': u'AndhraPradesh'
                                                }
                                            ]
                                        }
                                    }
                                },
                                'success': 1
                            }
    """

    def get(self, request, *args, **kwargs):
        # Response to be returned.
        self.result = {
            "success": 0,
            "message": "Device Loading Completed",
            "data": {
                "meta": {},
                "objects": {}
            }
        }

        technology_data = []
        vendor_list, vendor_data, state_data, city_data = [], [], [], []

        for device_technology in DeviceTechnology.objects.all():
            # Creating technologies data.
            technology_data.append({'id': device_technology.id,
                                    'value': device_technology.name})
            if int(self.kwargs['for_map']) == 0:
                vendors = device_technology.device_vendors.all()
                for vendor in vendors:
                    if vendor not in vendor_list:
                        vendor_list.append(vendor.id)
                        # Creating vendor data.
                        vendor_data.append(
                            {
                                'id': vendor.id,
                                'value': vendor.name,
                                'tech_id': device_technology.id,
                                'tech_name': device_technology.name
                            }
                        )

        if int(self.kwargs['for_map']) == 0:
            for vendor in DeviceVendor.objects.all():
                vendor_data.append({'id': vendor.id,
                                    'value': vendor.name})

            for state in State.objects.all():
                # Creating state data.
                state_data.append({'id': state.id,
                                   'value': state.state_name})
                
            state_list = []
            
            for city in City.objects.all():
                # Creating city data.
                city_data.append({'id': city.id,
                                  'value': city.city_name,
                                  'state_id': city.state.id,
                                  'state_name': city.state.state_name})
                if city.state.id not in state_list:
                    state_list.append(city.state.id)
                    state_data.append({'id': city.state.id, 'value': city.state.state_name})

        self.result['data']['objects']['technology'] = {'data': technology_data}

        # Specify whether data is for 'map' or other functionality.
        if int(self.kwargs['for_map']) == 0:
            self.result['data']['objects']['vendor'] = {'data': vendor_data}
            self.result['data']['objects']['state'] = {'data': state_data}
            self.result['data']['objects']['city'] = {'data': city_data}

        self.result['message'] = 'Data Fetched Successfully.'
        self.result['success'] = 1

        return HttpResponse(ujson.dumps(self.result), content_type="application/json")


class LPServicesApi(View):
    """
        API for fetching the services and data sources for list of devices.

        Args:
            devices (list): List of devices.

        Returns:
            result (dict): Dictionary of devices with associates services and data sources.
                           For e.g.,
                               {
                                    "success" : 1,
                                    "message" : "Services Fetched Successfully",
                                    "data" : {
                                        "device1" : {
                                            "services" : [
                                                {
                                                    "name" : "any_service_name2",
                                                    "value" : "65",
                                                    "datasource" : [
                                                        {
                                                            "name" : "any_service_datasource_name1",
                                                            "value" : "651"
                                                        },
                                                        {
                                                            "name" : "any_service_datasource_name2",
                                                            "value" : "652"
                                                        },
                                                        {
                                                            "name" : "any_service_datasource_name3",
                                                            "value" : "653"
                                                        }
                                                    ]
                                                },
                                                {
                                                    "name" : "any_service_name3",
                                                    "value" : "66",
                                                    "datasource" : [
                                                        {
                                                            "name" : "any_service_datasource_name4",
                                                            "value" : "654"
                                                        },
                                                        {
                                                            "name" : "any_service_datasource_name5",
                                                            "value" : "655"
                                                        },
                                                        {
                                                            "name" : "any_service_datasource_name6",
                                                            "value" : "656"
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        "device2" : {
                                            "services" : [
                                                {
                                                    "name" : "any_service_name4",
                                                    "value" : "6545",
                                                    "datasource" : [
                                                        {
                                                            "name" : "any_service_datasource_name7",
                                                            "value" : "657"
                                                        },
                                                        {
                                                            "name" : "any_service_datasource_name8",
                                                            "value" : "658"
                                                        },
                                                        {
                                                            "name" : "any_service_datasource_name9",
                                                            "value" : "659"
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    }
                                }
    """
    def get(self, request):
        """
        Returns json containing devices, services and data sources.
        """
        result = {
            "success": 0,
            "message": "No Service Data",
            "data": {
            }
        }

        # List of devices for which service and data sources needs to be fetched,
        # i.e. ['device1', 'device2'].
        try:
            devices = eval(str(self.request.GET.get('devices',None)))
            if devices:
                for dv in devices:
                    device = Device.objects.get(device_name=dv)

                    # Fetching all rows form 'service_deviceserviceconfiguration' where device_name is
                    # is name of device currently in loop; to get all associated services.
                    device_sdc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name)

                    # Initializing dict for current device.
                    result['data'][str(dv)] = {}

                    # Initializing list for services associated to current device(dv).
                    result['data'][str(dv)]['services'] = []

                    # Loop through all services of current device(dv).
                    for dsc in device_sdc:
                        svc_dict = dict()
                        svc_dict['name'] = str(dsc.service_name)
                        svc_dict['value'] = Service.objects.get(name=dsc.service_name).id

                        # Initializing list of data sources.
                        svc_dict['datasource'] = []

                        # Fetching all rows form 'service_deviceserviceconfiguration'
                        # where device_name and service_name are names of current device
                        # and service in loop; to get all associated data sources.
                        service_data_sources = DeviceServiceConfiguration.objects.filter(device_name=dv,
                                                                                         service_name=dsc.service_name)

                        # Loop through all the data sources associated with current service(dsc).
                        for sds in service_data_sources:
                            sds_dict = dict()
                            sds_dict['name'] = sds.data_source
                            sds_dict['value'] = ServiceDataSource.objects.get(name=sds.data_source).id
                            # Appending data source dict to data sources list for current service(dsc) data source list.
                            svc_dict['datasource'].append(sds_dict)

                        # Appending service dict to services list of current device(dv).
                        result['data'][str(dv)]['services'].append(svc_dict)
                        result['success'] = 1
                        result['message'] = "Successfully fetched services and data sources."
        except Exception as e:
            result['message'] = e.message
            logger.info(e)

        return HttpResponse(json.dumps(result))


class FetchLPDataApi(View):
    """
        API for fetching the service live polled value.

        Args:
            device (list): List of devices.
            service (list): List of services.
            datasource (list): List of data sources.

        Returns:
            result (dict): Dictionary containing list of live polled values and icon urls.
                           For e.g.,
                                {
                                    "success" : 1,
                                    "message" : "Live Polling Data Fetched Successfully",
                                    "data" : {
                                        "value" : ["50"],
                                        "icon" : ["static/img/marker/icon1_small.png"]
                                    }
                                }
    """
    def get(self, request):
        """
        Returns json containing live polling value and icon url.
        """
        # Converting 'json' into python object.
        devices = eval(str(self.request.GET.get('device', None)))
        services = eval(str(self.request.GET.get('service', None)))
        datasources = eval(str(self.request.GET.get('datasource', None)))

        result = {
            "success": 0,
            "message": "",
            "data": {
            }
        }

        result['data']['value'] = []
        result['data']['icon'] = []

        try:
            for dv, svc, ds in zip(devices, services, datasources):
                lp_data = dict()
                lp_data['mode'] = "live"
                lp_data['device'] = dv
                lp_data['service'] = svc
                lp_data['ds'] = []
                lp_data['ds'].append(ds)

                device = Device.objects.get(device_name=dv)
                service = Service.objects.get(name=svc)
                data_source = ServiceDataSource.objects.get(name=ds)

                url = "http://{}:{}@{}:{}/{}/check_mk/nocout_live.py".format(device.site_instance.username,
                                                                             device.site_instance.password,
                                                                             device.machine.machine_ip,
                                                                             device.site_instance.web_service_port,
                                                                             device.site_instance.name)

                # Encoding 'lp_data'.
                encoded_data = urllib.urlencode(lp_data)

                # Sending post request to nocout device app to fetch service live polling value.
                r = requests.post(url , data=encoded_data)

                # Converting post response data into python dict expression.
                response_dict = ast.literal_eval(r.text)

                # If response(r) is given by post request than process it further to get success/failure messages.
                if r:
                    result['data']['value'].append(response_dict.get('value')[0])
                    tech = DeviceTechnology.objects.get(pk=device.device_technology)

                    # Live polling settings for getting associates service and data sources.
                    lps = LivePollingSettings.objects.get(technology=tech, service=service, data_source=data_source)

                    # Threshold configuration for getting warning, critical comparison values.
                    tc = ThresholdConfiguration.objects.get(live_polling_template=lps)

                    # Thematic settings for getting icon url.
                    ts = ThematicSettings.objects.get(threshold_template=tc)

                    # Comparing threshold values to get icon.
                    try:
                        value = int(response_dict.get('value')[0])
                        image_partial = "img/icons/wifi7.png"
                        if abs(int(value)) > abs(int(tc.warning)):
                            image_partial = ts.gt_warning.upload_image
                        elif abs(int(tc.warning)) >= abs(int(value)) >= abs(int(tc.critical)):
                            image_partial = ts.bt_w_c.upload_image
                        elif abs(int(value)) > abs(int(tc.critical)):
                            image_partial = ts.gt_critical.upload_image
                        else:
                            icon = static('img/icons/wifi7.png')
                        img_url = "media/" + str(image_partial) if "uploaded" in str(image_partial) else static(
                            "img/" + image_partial)
                        icon = str(img_url)
                    except Exception as e:
                        icon = static('img/icons/wifi7.png')
                        logger.info(e.message)

                    result['data']['icon'].append(icon)
                    # If response_dict doesn't have key 'success'.
                    if not response_dict.get('success'):
                        logger.info(response_dict.get('error_message'))
                        result['message'] += "Failed to fetch data for '%s'." % (svc)
                    else:
                        result['message'] += "Successfully fetch data for '%s'." % (svc)
            result['success'] = 1
        except Exception as e:
            result['message'] = e.message
            logger.info(e)

        return HttpResponse(json.dumps(result))


class FetchLPSettingsApi(View):
    """
        API for fetching the service live polled value.

        Args:
            technology (unicode): ID of technology.

        Returns:
            result (dict): Dictionary containing list of live polling settings.
                           For e.g.,
                                {
                                    "message": "Successfully fetched live polling settings.",
                                    "data": {
                                        "lp_templates": [
                                            {
                                                "id": 1,
                                                "value": "RadwinUAS"
                                            },
                                            {
                                                "id": 2,
                                                "value": "Radwin RSSI"
                                            },
                                            {
                                                "id": 3,
                                                "value": "Estimated Throughput"
                                            },
                                            {
                                                "id": 4,
                                                "value": "Radwin Uptime"
                                            }
                                        ]
                                    },
                                    "success": 1
                                }
    """
    def get(self, request):
        """
        Returns json containing live polling values and icon urls for bulk devices.
        """
        # Result dictionary to be returned as output of api.
        result = {
            "success": 0,
            "message": "Failed to fetch live polling settings.",
            "data": {
            }
        }

        # Initializing 'lp_templates' list containing live setting templates.
        result['data']['lp_templates'] = list()

        # Converting 'json' into python object.
        technology_id = int(self.request.GET.get('technology', None))

        # Technology object.
        technology = DeviceTechnology.objects.get(pk=technology_id)

        # Get live polling settings corresponding to the technology.
        lps = ""
        try:
            lps = LivePollingSettings.objects.filter(technology=technology)
        except Exception as e:
            logger.info(e.message)

        if lps:
            for lp in lps:
                lp_temp = dict()
                lp_temp['id'] = lp.id
                lp_temp['value'] = lp.alias
                result['data']['lp_templates'].append(lp_temp)

            result['message'] = "Successfully fetched live polling settings."
            result['success'] = 1

        return HttpResponse(json.dumps(result))


class FetchThresholdConfigurationApi(View):
    """
        API for fetching the service live polled value.

        Args:
            technology (unicode): ID of technology.

        Returns:
            result (dict): Dictionary containing list of threshold configurations.
                           For e.g.,
                                {
                                    "message": "Successfully fetched threshold configurations.",
                                    "data": {
                                        "threshold_templates": [
                                            {
                                                "id": 6,
                                                "value": "Radwin UAS"
                                            },
                                            {
                                                "id": 7,
                                                "value": "Radwin RSSI Critical"
                                            },
                                            {
                                                "id": 11,
                                                "value": "Radwin RSSI Warning"
                                            },
                                            {
                                                "id": 8,
                                                "value": "Estimated Throughput"
                                            },
                                            {
                                                "id": 9,
                                                "value": "Radwin Uptime"
                                            }
                                        ]
                                    },
                                    "success": 1
                                }
    """
    def get(self, request):
        """
        Returns json containing live polling values and icon urls for bulk devices.
        """
        # Result dictionary to be returned as output of api.
        result = {
            "success": 0,
            "message": "Failed to fetch live polling settings.",
            "data": {
            }
        }

        # Initializing 'lp_templates' list containing live setting templates.
        result['data']['threshold_templates'] = list()

        # Converting 'json' into python object.
        technology_id = int(self.request.GET.get('technology', None))

        # Technology object.
        technology = DeviceTechnology.objects.get(pk=technology_id)

        # Get live polling settings corresponding to the technology.
        lps = ""
        try:
            lps = LivePollingSettings.objects.filter(technology=technology)
        except Exception as e:
            logger.info(e.message)

        if lps:
            for lp in lps:
                threshold_configurations = ThresholdConfiguration.objects.filter(live_polling_template=lp)
                if threshold_configurations:
                    for tc in threshold_configurations:
                        tc_temp = dict()
                        tc_temp['id'] = tc.id
                        tc_temp['value'] = tc.alias
                        result['data']['threshold_templates'].append(tc_temp)
            result['message'] = "Successfully fetched threshold configurations."
            result['success'] = 1
        return HttpResponse(json.dumps(result))


class FetchThematicSettingsApi(View):
    """
        API for fetching the service live polled value.

        Args:
            technology (unicode): ID of technology.

        Returns:
            result (dict): Dictionary containing list of threshold configurations.
                           For e.g.,
                                {
                                    "message": "Successfully fetched threshold configurations.",
                                    "data": {
                                        "threshold_templates": [
                                            {
                                                "id": 6,
                                                "value": "Radwin UAS"
                                            },
                                            {
                                                "id": 7,
                                                "value": "Radwin RSSI Critical"
                                            },
                                            {
                                                "id": 11,
                                                "value": "Radwin RSSI Warning"
                                            },
                                            {
                                                "id": 8,
                                                "value": "Estimated Throughput"
                                            },
                                            {
                                                "id": 9,
                                                "value": "Radwin Uptime"
                                            }
                                        ]
                                    },
                                    "success": 1
                                }
    """
    def get(self, request):
        """
        Returns json containing live polling values and icon urls for bulk devices.
        """
        # Result dictionary to be returned as output of api.
        result = {
            "success": 0,
            "message": "Failed to fetch thematic settings.",
            "data": {
            }
        }

        # Initializing 'lp_templates' list containing live setting templates.
        result['data']['thematic_settings'] = list()

        # Service type.
        service_type = self.request.GET.get('service_type', None)

        # Converting 'json' into python object.
        technology_id = int(self.request.GET.get('technology', None))

        # Technology object.
        technology = DeviceTechnology.objects.get(pk=technology_id)

        # Get live polling settings corresponding to the technology.
        lps = ""
        try:
            lps = LivePollingSettings.objects.filter(technology=technology)
        except Exception as e:
            logger.info(e.message)
        if service_type == 'ping':
            thematic_settings = PingThematicSettings.objects.filter(technology=technology)
            for ts in thematic_settings:
                ts_temp = dict()
                ts_temp['id'] = ts.id
                ts_temp['value'] = ts.alias
                result['data']['thematic_settings'].append(ts_temp)
            result['message'] = "Successfully fetched thematic settings."
            result['success'] = 1
        else:
            if lps:
                for lp in lps:
                    threshold_configurations = ThresholdConfiguration.objects.filter(live_polling_template=lp)
                    if threshold_configurations:
                        for tc in threshold_configurations:
                            thematic_settings = ThematicSettings.objects.filter(threshold_template=tc)
                            if thematic_settings:
                                for ts in thematic_settings:
                                    ts_temp = dict()
                                    ts_temp['id'] = ts.id
                                    ts_temp['value'] = ts.alias
                                    result['data']['thematic_settings'].append(ts_temp)
            result['message'] = "Successfully fetched thematic settings."
            result['success'] = 1

        return HttpResponse(json.dumps(result))


class BulkFetchLPDataApi(View):
    """
        API for fetching the service live polled values.

        Args:
            ts_template (unicode): Threshold configuration template id. For e.g. 23.
            devices (list): List of devices. For e.g. ["3335","1714","2624","2622"].
            service_type (unicode): Type of service, i.e 'ping' or 'normal'.

        Returns:
            result (dict): Dictionary containing list of live polled values and icon urls.
                           For e.g.,
                                {
                                    "message": "Successfully fetched.",
                                    "data": {
                                        "devices": {
                                            "2622": {
                                                "message": "Successfully fetch data for '2622'.",
                                                "value": [
                                                    "-57"
                                                ],
                                                "icon": "media/uploaded/icons/2014-09-25/demo1.png"
                                            },
                                            "2624": {
                                                "message": "Successfully fetch data for '2624'.",
                                                "value": "NA",
                                                "icon": "media/uploaded/icons/2014/09/18/wifi3.png"
                                            },
                                            "3335": {
                                                "message": "Successfully fetch data for '3335'.",
                                                "value": "NA",
                                                "icon": "media/uploaded/icons/2014/09/18/wifi3.png"
                                            },
                                            "1714": {
                                                "message": "Successfully fetch data for '1714'.",
                                                "value": [
                                                    "-66"
                                                ],
                                                "icon": "media/uploaded/icons/2014-10-26/demo2.png"
                                            }
                                        }
                                    },
                                    "success": 1
                                }
    """
    def get(self, request):
        """
        Returns json containing live polling values and icon urls for bulk devices.
        """
        # Get service type, i.e. 'ping' or 'normal'.
        try:
            service_type = self.request.GET.get('service_type')
        except Exception as e:
            service_type = ""

        # Devices list.
        devices = eval(str(self.request.GET.get('devices', None)))

        # Thematic settings template ID.
        try:
            ts_template_id = int(self.request.GET.get('ts_template'))
        except Exception as e:
            ts_template_id = ""

        # Service name.
        try:
            service_name = self.request.GET.get('service_name')
        except Exception as e:
            service_name = ""

        # Data source.
        try:
            ds_name = self.request.GET.get('ds_name')
        except Exception as e:
            ds_name = ""

        # Thematic settings.
        try:
            ts_type = self.request.GET.get('ts_type', None)
        except Exception as e:
            ts_type = ""

        # Exceptional services, i.e. 'ss' services which get service data from 'bs' instead from 'ss'.
        exceptional_services = ['wimax_dl_cinr', 'wimax_ul_cinr', 'wimax_dl_rssi',
                                'wimax_ul_rssi', 'wimax_ul_intrf', 'wimax_dl_intrf',
                                'wimax_modulation_dl_fec', 'wimax_modulation_ul_fec',
                                'cambium_ul_rssi', 'cambium_ul_jitter', 'cambium_reg_count',
                                'cambium_rereg_count']

        # Service for which live polling runs.
        service = ""

        # Data source for which live polling runs.
        data_source = ""

        # Live polling template ID.
        lp_template_id = ""

        # Result dictionary which needs to be returned as an output of api.
        result = {
            "success": 0,
            "message": "Failed to fetch the data.",
            "data": {}
        }

        # Fetch device technology if ts_type present.
        ts_technology = None

        if ts_type:
            try:
                ts_technology = DeviceTechnology.objects.get(id=Device.objects.get(
                    device_name=devices[0]).device_technology)
            except Exception as e:
                pass

        if not all([service_name, ds_name]):
            # Get thematic settings corresponding to the 'service_type'.
            if service_type == 'ping' or ts_type == 'ping':
                # Thematic settings (ping).
                if ts_type:
                    ts = self.get_thematic_settings(ts_type, ts_technology).thematic_template
                else:
                    ts = PingThematicSettings.objects.get(pk=ts_template_id)
                service = ts.service
                data_source = ts.data_source

                # Result dictionary which needs to be returned as an output of api.
                result = {
                    "success": 0,
                    "message": "Failed to fetch thematic settings.",
                    "data": {}
                }
            else:
                # Thematic settings (normal).
                if ts_type:
                    ts = self.get_thematic_settings(ts_type, ts_technology).thematic_template
                else:
                    ts = ThematicSettings.objects.get(pk=ts_template_id)

                # Live polling template ID.
                lp_template_id = ThresholdConfiguration.objects.get(
                    pk=ts.threshold_template.id).live_polling_template.id

                # Getting service and data source from live polling settings.
                try:
                    service = LivePollingSettings.objects.get(pk=lp_template_id).service
                    data_source = LivePollingSettings.objects.get(pk=lp_template_id).data_source
                except Exception as e:
                    pass

                # Result dictionary which needs to be returned as an output of api.
                result = {
                    "success": 0,
                    "message": "Failed to fetch live polling data.",
                    "data": {}
                }
        else:
            service = service_name
            data_source = ds_name

        # Fetch values specific to data source.
        # Formula corresponding to 'data_source'
        ds_formula = ""

        # Data source object.
        ds_obj = None
        try:
            ds_obj = ServiceDataSource.objects.get(name=data_source)
            ds_formula = ds_obj.formula
        except Exception as e:
            pass

        if ds_obj:
            result['data']['data_source'] = dict()
            result['data']['data_source']['chart_type'] = ds_obj.chart_type
            result['data']['data_source']['chart_color'] = ds_obj.chart_color
            result['data']['data_source']['data_source_type'] = ds_obj.ds_type_name()

        # In case of 'rta' and 'pl', fetch data from 'service_data_sources' function.
        if ds_name in ['pl', 'rta']:
            ds_dict = service_data_sources()
            result['data']['data_source'] = dict()
            result['data']['data_source']['chart_type'] = ds_dict[ds_name]['type'] if 'type' in ds_dict[ds_name] else ""
            result['data']['data_source']['chart_color'] = ds_dict[ds_name]['chart_color'] if 'chart_color' in ds_dict[
                ds_name] else ""
            result['data']['data_source']['data_source_type'] = ds_dict[ds_name][
                'data_source_type'] if 'data_source_type' in ds_dict[ds_name] else ""

            if ds_name in ['pl', 'rta']:
                ds_formula = ds_dict[ds_name]['formula'] if 'formula' in ds_dict[ds_name] else ""

        # BS device to with 'ss' is connected (applied only if 'service' is from 'exceptional_services').
        bs_device, site_name = None, None

        result['data']['devices'] = dict()

        # Get machines associated with the current devices.
        machine_list = []
        for device in devices:
            try:
                machine = Device.objects.get(device_name=device).machine.id
                machine_list.append(machine)
            except Exception as e:
                pass

        # Remove redundant machine id's from 'machine_list'.
        machines = set(machine_list)

        try:
            responses = []
            for machine_id in machines:
                response_dict = {
                    'value': []
                }

                # Live polling setting.
                if not all([service_name, ds_name]):
                    if service_type and service_type != "ping":
                        lp_template = LivePollingSettings.objects.get(pk=lp_template_id)
                    if ts_type and ts_type != "ping":
                        lp_template = ts.threshold_template.live_polling_template

                # Current machine devices.
                current_devices_list = []

                # Fetch devices associated with current machine.
                for device_name in devices:
                    try:
                        device = Device.objects.get(device_name=device_name)
                        if device.machine.id == machine_id:
                            current_devices_list.append(str(device.device_name))
                    except Exception as e:
                        pass

                # Get site instances associated with the current devices.
                site_instances_list = []

                # Fetch all site instances associated with the devices in 'current_devices_list'.
                for device_name in current_devices_list:
                    try:
                        device = Device.objects.get(device_name=device_name)
                        # If service is from 'exceptional_services' than get base station
                        # and it's device to which 'ss' device is connected from 'Topology'.
                        if str(service) in exceptional_services:
                            # MAC address of device.
                            mac_address = device.mac_address
                            mac = mac_address.lower()

                            # Base station device name to which 'ss' is connected.
                            bs_device = Topology.objects.get(connected_device_mac=mac)

                            # Get base station device.
                            device = Device.objects.get(device_name=bs_device.device_name)

                        # Append device site instance id in 'site_instances_list' list.
                        site_instances_list.append(device.site_instance.id)
                    except Exception as e:
                        pass

                # Remove redundant site instance id's from 'site_instances_list'.
                sites = set(site_instances_list)
                site_list = []
                for site_id in sites:
                    # BS and SS macs mapping dictionary
                    # For e.g. 'bs_name_ss_mac_mapping': {
                    #                                     u'1527': [
                    #                                         u'00: 02: 73: 93: 05: 4f',
                    #                                         u'00: 02: 73: 90: 80: 98'
                    #                                    ]}
                    bs_name_ss_mac_mapping = {}

                    # SS name and MAC mapping dictionary
                    # For e.g. 'ss_name_mac_mapping': {
                    #                                     u'3597': u'00: 02: 73: 91: 2a: 24',
                    #                                     u'3769': u'00: 02: 73: 93: 06: d3',
                    #                                     u'3594': u'00: 02: 73: 90: 24: 88',
                    #                                     u'3047': u'00: 02: 73: 93: 05: 4f'
                    #                                 }
                    ss_name_mac_mapping = {}

                    # List of devices associated with current site instance.
                    devices_in_current_site = []

                    for device_name in current_devices_list:
                        try:
                            device = Device.objects.get(device_name=device_name)
                            if str(service) in exceptional_services:
                                # SS device MAC address.
                                device_ss_mac = device.mac_address

                                # Insert data in 'ss_name_mac_mapping' dictionary.
                                ss_name_mac_mapping[device.device_name] = device_ss_mac

                                # Get base station device name from 'Topology'.
                                bs_device = Topology.objects.get(connected_device_mac=device_ss_mac.lower())

                                # Get base station device.
                                device = Device.objects.get(device_name=bs_device.device_name)

                                if device.device_name in bs_name_ss_mac_mapping.keys():
                                    bs_name_ss_mac_mapping[device.device_name].append(device_ss_mac)
                                else:
                                    bs_name_ss_mac_mapping[device.device_name] = [device_ss_mac]

                                # Base station device site instance ID.
                                bs_site_id = device.site_instance.id

                                if bs_site_id == site_id and device.device_name not in devices_in_current_site:
                                    devices_in_current_site.append(device.device_name)
                            elif device.site_instance.id == site_id:
                                devices_in_current_site.append(device.device_name)
                        except Exception as e:
                            pass

                    # Live polling data dictionary (payload for nocout.py api call).
                    # For e.g.
                    # lp_data -
                    # {
                    #   'device_list': [u'1598'],
                    #   'bs_name_ss_mac_mapping': {u'1598': [u'00:02:73:90:1f:6e']},
                    #   'service_list': ['wimax_dl_rssi'],
                    #   'ss_name_mac_mapping': {
                    #                              u'2622': u'00:02:73:90:1f:6e',
                    #                              u'2624': u'00:02:73:92:9c:12',
                    #                              u'3335': u'00:02:73:91:99:1d'
                    #                          },
                    #   'mode': 'live',
                    #   'dr_master_slave': {},
                    #   'ds': ['dl_rssi']
                    # }
                    lp_data = dict()
                    lp_data['mode'] = "live"
                    lp_data['bs_name_ss_mac_mapping'] = bs_name_ss_mac_mapping
                    lp_data['ss_name_mac_mapping'] = ss_name_mac_mapping
                    lp_data['device_list'] = devices_in_current_site

                    if not all([service_name, ds_name]):
                        if service_type == 'ping' or ts_type == "ping":
                            lp_data['service_list'] = [str(service)]
                            lp_data['ds'] = [str(data_source)]
                        else:
                            lp_data['service_list'] = [str(lp_template.service.name)]
                            lp_data['ds'] = [str(lp_template.data_source.name)]
                    else:
                        lp_data['service_list'] = [str(service)]
                        lp_data['ds'] = [str(data_source)]

                    site = SiteInstance.objects.get(pk=int(site_id))
                    site_list.append({
                        'username': site.username,
                        'password': site.password,
                        'port': site.web_service_port,
                        'machine': site.machine.machine_ip,
                        'site_name': site.name,
                        'lp_data': lp_data
                    })

                # Multiprocessing.
                q = Queue()
                jobs = [
                    Process(
                        target=nocout_live_polling,
                        args=(q, site,)
                    ) for site in site_list
                ]

                for j in jobs:
                    j.start()
                for k in jobs:
                    k.join()
                pformat(q)
                while True:
                    if not q.empty():
                        responses.append(q.get())
                    else:
                        break
                for entry in responses:
                    response_dict['value'].extend(entry.get('value'))

                # If response(r) is given by post request than process it further to get success/failure messages.
                if len(response_dict):
                    # Get devices from 'response_dict'.
                    devices_in_response = response_dict.get('value')

                    for device_name in devices:
                        device_obj = ""
                        try:
                            device_obj = Device.objects.get(device_name=device_name)
                        except Exception as e:
                            pass

                        device_value = "NA"

                        # Check whether device present in 'devices_in_response'
                        # if present then fetch it's live polled value.
                        for device_dict in devices_in_response:
                            for device, val in device_dict.items():
                                if device_name == device:
                                    device_value = val
                                    continue

                        result['data']['devices'][device_name] = dict()

                        # Evaluate value if formula is available for data source.
                        if ds_formula:
                            try:
                                result['data']['devices'][device_name]['value'] = eval(
                                    "perf_util.ds_formula(device_value)")
                            except Exception as e:
                                pass
                        else:
                            result['data']['devices'][device_name]['value'] = device_value

                        if not all([service_name, ds_name]):
                            # Default icon.
                            icon = ""
                            try:
                                icon = DeviceType.objects.get(pk=device_obj.device_type).device_icon
                            except Exception as e:
                                pass

                            icon = str(icon)

                            # Fetch icon settings for thematics as per thematic type selected i.e. 'ping' or 'normal'.
                            th_icon_settings = ""
                            try:
                                th_icon_settings = ts.icon_settings
                            except Exception as e:
                                pass

                            # Fetch thematic ranges as per service type selected i.e. 'ping' or 'normal'.
                            th_ranges = ""
                            try:
                                if service_type == "ping" or ts_type == "ping":
                                    th_ranges = ts
                                else:
                                    th_ranges = ts.threshold_template
                            except Exception as e:
                                pass

                            # Fetch service type if 'ts_type' is "normal".
                            svc_type = ""
                            try:
                                if service_type != "ping" or ts_type != "ping":
                                    svc_type = ts.threshold_template.service_type
                            except Exception as e:
                                pass

                            # Comparing threshold values to get icon.
                            try:
                                if len(device_value) and (device_value != "NA"):

                                    value = device_value

                                    # Get appropriate icon.
                                    if service_type == "normal" or ts_type == "normal":
                                        if svc_type == "INT":
                                            icon = self.get_icon_for_numeric_service(th_ranges,
                                                                                     th_icon_settings,
                                                                                     value,
                                                                                     icon)
                                        elif svc_type == "STR":
                                            icon = self.get_icon_for_string_service(th_ranges,
                                                                                    th_icon_settings,
                                                                                    value,
                                                                                    icon)
                                        else:
                                            pass
                                    elif service_type == "ping" or ts_type == "ping":
                                        icon = self.get_icon_for_numeric_service(th_ranges,
                                                                                 th_icon_settings,
                                                                                 value,
                                                                                 icon)
                                    else:
                                        pass
                                else:
                                    icon = "media/" + str(icon) if "uploaded" in str(
                                        icon) else "static/img/" + str(icon)

                            except Exception as e:
                                pass

                            result['data']['devices'][device_name]['icon'] = icon

                        # If response_dict doesn't have key 'success'.
                        if device_value and (device_value != "NA"):
                            result['data']['devices'][device_name]['message'] = "Successfully fetch data for '%s'." % \
                                                                                device_name
                        else:
                            result['data']['devices'][device_name]['message'] = "Failed to fetch data for '%s'." % \
                                                                                device_name
            result['success'] = 1
            result['message'] = "Successfully fetched."
        except Exception as e:
            result['message'] = e.message

        return HttpResponse(json.dumps(result))

    def get_thematic_settings(self, ts_type, device_technology):
        """
            Get user thematic settings.

            Args:
                ts_type (unicode): Thematic settings type i.e 'ping' or 'normal'.
                device_technology (<class 'device.models.DeviceTechnology'>): Device technology object.

            Returns:
                user_thematics (<class 'inventory.models.UserPingThematicSettings'>): Thematic settings object.
        """
        user_thematics = None

        # Current user.
        try:
            current_user = UserProfile.objects.get(id=self.request.user.id)
        except Exception as e:
            return None

        device_technology = device_technology

        # Fetch thematic settings for current user.
        if ts_type == "normal":
            try:
                user_thematics = UserThematicSettings.objects.get(user_profile=current_user,
                                                                  thematic_technology=device_technology)
            except Exception as e:
                return user_thematics

        elif ts_type == "ping":
            try:
                user_thematics = UserPingThematicSettings.objects.get(user_profile=current_user,
                                                                      thematic_technology=device_technology)
            except Exception as e:
                return user_thematics

        return user_thematics

    def get_icon_for_numeric_service(self, th_ranges=None, th_icon_settings="", value="", icon=""):
        """
            Get device icon corresponding to fetched performance value.
            Args:
                th_ranges (<class 'inventory.models.ThresholdConfiguration'>): Threshold configuration object.
                                                                               For e.g. Wimax DL RSSI.
                th_icon_settings (unicode): icon settings in json format.
                                            For e.g.,
                            [
                                {
                                    'icon_settings1': u'uploaded/icons/2014-09-26/2014-09-26-11-56-11_SM-GIF.gif'
                                },
                                {
                                    'icon_settings2': u'uploaded/icons/2014-10-26/2014-10-26-14-59-40_SM-Red.png'
                                },
                                {
                                    'icon_settings3': u'uploaded/icons/2014-09-25/2014-09-25-13-59-00_P2P-Green.png'
                                }
                            ]
                value (str): Performance value. For e.g. "-57".
                icon (str): Icon location. For e.g. "media/uploaded/icons/2014/09/18/wifi3.png".

            Returns:
                icon (str): Icon location. For e.g. "media/uploaded/icons/2014/09/18/wifi3.png".
        """

        # Default image to be loaded.
        image_partial = icon

        # Fetch value from list.
        if type(value) is list:
            value = value[0]
        elif type(value) is str:
            value = value
        else:
            pass

        # Just to be safe of % unit in value for PL polling.
        value = "".join(str(value).split('%'))

        if th_ranges and th_icon_settings and len(str(value)):
            compare_this = float(value)
            for i in range(1, 11):
                try:
                    compare_to_start = float(eval("th_ranges.range%d_start" % i))
                    compare_to_end = float(eval("th_ranges.range%d_end" % i))
                    icon_settings = eval(th_icon_settings)
                    if compare_to_start <= compare_this <= compare_to_end:
                        icon_key = "icon_settings{0}".format(i)
                        for icon_setting in icon_settings:
                            if icon_key in icon_setting.keys():
                                image_partial = str(icon_setting[icon_key])
                                break
                except Exception as e:
                    continue

        # Image URL.
        img_url = "media/" + str(image_partial) if "uploaded" in str(
            image_partial) else "static/img/" + str(image_partial)

        # Icon to be send in response.
        icon = str(img_url)

        return icon

    def get_icon_for_string_service(self, th_ranges=None, th_icon_settings="", value="", icon=""):
        """
            Get device icon corresponding to fetched performance value.
            Args:
                th_ranges (<class 'inventory.models.ThresholdConfiguration'>): Threshold configuration object.
                                                                               For e.g. Wimax DL RSSI.
                th_icon_settings (unicode): Icon settings in json format.
                                            For e.g.,
                        [
                            {
                                'icon_settings1': u'uploaded/icons/2014-09-26/2014-09-26-11-56-11_SM-GIF.gif'
                            },
                            {
                                'icon_settings2': u'uploaded/icons/2014-10-26/2014-10-26-14-59-40_SM-Red.png'
                            },
                            {
                                'icon_settings3': u'uploaded/icons/2014-09-25/2014-09-25-13-59-00_P2P-Green.png'
                            }
                        ]
                value (str): Performance value. For e.g. "-57".
                icon (str): Icon location. For e.g. "media/uploaded/icons/2014/09/18/wifi3.png".

            Returns:
                icon (str): Icon location. For e.g. "media/uploaded/icons/2014/09/18/wifi3.png".
        """

        # Default image to be loaded.
        image_partial = icon

        # Fetch value from list.
        if type(value) is list:
            value = value[0]
        elif type(value) is str:
            value = value
        else:
            pass

        if th_ranges and th_icon_settings and value:
            compare_this = ''.join(e for e in value if e.isalnum())
            for i in range(1, 11):
                try:
                    eval_this = eval("th_ranges.range%d_start" % i)
                    compare_to = ''.join(e for e in eval_this if e.isalnum())
                    icon_settings = eval(th_icon_settings)
                    if compare_this.strip().lower() == compare_to.strip().lower():
                        icon_key = "icon_settings{0}".format(i)
                        for icon_setting in icon_settings:
                            if icon_key in icon_setting.keys():
                                image_partial = str(icon_setting[icon_key])
                                break
                except Exception as e:
                    continue

        # Image URL.
        img_url = "media/" + str(image_partial) if "uploaded" in str(
            image_partial) else "static/img/" + str(image_partial)

        # Icon to be send in response.
        icon = str(img_url)

        return icon


def nocout_live_polling(q, site):
    # URL for nocout.py.
    url = "http://{}:{}@{}:{}/{}/check_mk/nocout_live.py".format(site.get('username'),
                                                                 site.get('password'),
                                                                 site.get('machine'),
                                                                 site.get('port'),
                                                                 site.get('site_name'))
    # Encoding 'lp_data'.
    encoded_data = urllib.urlencode(site.get('lp_data'))

    # Sending post request to nocout device app to fetch service live polling value.
    try:
        r = requests.post(url, data=encoded_data)
        response_dict = ast.literal_eval(r.text)
        if len(response_dict):
            temp_dict = deepcopy(response_dict)
            q.put(temp_dict)
    except Exception as e:
        pass
