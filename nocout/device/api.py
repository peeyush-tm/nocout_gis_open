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
* GetDeviceTypeExtraFields
* DeviceSoftDelete
* AddDeviceToNMSDisplayInfo
* DeleteSingleServiceDisplayData
* DeviceServiceStatus
* ServiceAddOldConf
* AddServices
* AddServiceDisplayData
* GetDeviceInventory
* EditSingleServiceDisplayData
* FetchLPSettingsApi
* ModifyDeviceState
* RestoreDevice
* EditSingleService
* DeleteSingleService
* GetEligibleParentDevices
* GetDevicePorts
* ServiceEditOldConf
* FetchThematicSettingsApi
* FetchLPDataApi
* DeleteServices
* ServiceEditPingConf
* SyncDevicesInNMS
* ServiceAddNewConf
* DeleteServiceDisplayData
* DeviceFilterApi
* DeleteDeviceFromNMS
* GetVendorsForTech
* FetchThresholdConfigurationApi
* LPServicesApi
* DeviceRestoreDispalyData
* ResetServiceConfiguration
* ServiceEditNewConf
* GetModelsForVendor
* BulkFetchLPDataApi
* GetServiceParaTableData
* EditServiceDisplayData
* DeviceStatsApi
* GetDevicesForSelectionMenu
* RemoveSyncDeadlock
* GetSitesForMachine
* GetTypesForModel
* EditServices
* EditDeviceInNMS
* AddDeviceToNMS

=======
Methods
=======
* prepare_raw_result
* nocout_live_polling
"""

import ast
import json
import ujson
import time
import urllib
from datetime import datetime
from device.serializers import DeviceParentSerializer, DeviceInventorySerializer
from machine.models import Machine
from nocout import settings
import requests
import logging
from copy import deepcopy
from pprint import pformat
from multiprocessing import Process, Queue
from django.db.models import Count,Q
from django.views.generic.base import View
from django.http import HttpResponse
from device.models import Device, DeviceType, DeviceVendor, DeviceTechnology, State, City, DeviceModel, \
    DeviceSyncHistory
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
from service.models import DeviceServiceConfiguration, Service, ServiceDataSource, DevicePingConfiguration, \
    ServiceParameters
from django.contrib.staticfiles.templatetags.staticfiles import static
from site_instance.models import SiteInstance
from performance.models import Topology
from performance.formulae import display_time, rta_null
# Import service utils gateway class
from service.utils.util import ServiceUtilsGateway
from sitesearch.views import prepare_raw_bs_result
from nocout.settings import GIS_MAP_MAX_DEVICE_LIMIT, CACHE_TIME,\
    PING_RTA_WARNING, PING_RTA_CRITICAL, \
    PING_PL_WARNING, PING_PL_CRITICAL, \
    SERVICE_DATA_SOURCE
from user_profile.models import UserProfile
from inventory.models import (BaseStation, LivePollingSettings,
                              ThresholdConfiguration, ThematicSettings,
                              PingThematicSettings, UserThematicSettings,
                              UserPingThematicSettings)
from device.models import DeviceTechnology
from rest_framework.views import APIView
from rest_framework.response import Response

from inventory.utils.util import getDeviceTypeNamedDict, getFrequencyDict
from django.core.urlresolvers import reverse

logger = logging.getLogger(__name__)

# Create service utils instance
service_utils = ServiceUtilsGateway()

# Create SDS data dict
SERVICE_DATA_SOURCE = service_utils.service_data_sources()

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


def prepare_ss_info_dict(ss_dataset=[], device_type_dict={}, frequency_obj={}, base_urls={}):
    """

    """
    ss_dict = {}

    if not base_urls:
        # Create performance page base url
        try:
            perf_page_base_url = reverse(
                'SingleDevicePerf',
                kwargs={
                    'page_type': 'page_type', 
                    'device_id': 0
                },
                current_app='performance'
            )
        except Exception, e:
            perf_page_base_url = ''

        # Create device inventory page base url
        try:
            inventory_base_url = reverse(
                'device_edit',
                kwargs={
                    'pk': 0
                },
                current_app='device'
            )
        except Exception, e:
            inventory_base_url = ''

    if not ss_dataset:
        return ss_dict

    for data in ss_dataset:

        data_list = data.split('|')
        if len(data_list) > 1:
            if data_list[0] not in ss_dict:
                ss_dict[data_list[0]] = {
                    'ss_list': list(),
                    'ip_list': list(),
                    'circuit_list': list()
                }

            try:
                ss_id = int(data_list[1])
            except Exception, e:
                ss_id = ''

            if ss_id:
                try:
                    device_id = int(data_list[2])
                except Exception, e:
                    device_id = ''

                try:
                    device_name = data_list[3]
                except Exception, e:
                    device_name = ''

                try:
                    ip_address = data_list[4]
                except Exception, e:
                    ip_address = ''

                try:
                    device_type = data_list[5]
                except Exception, e:
                    device_type = ''

                try:
                    latitude = float(data_list[6])
                except Exception, e:
                    latitude = ''

                try:
                    longitude = float(data_list[7])
                except Exception, e:
                    longitude = ''

                try:
                    circuit_id = data_list[8]
                except Exception, e:
                    circuit_id = 'NA'

                try:
                    antenna_height = int(data_list[9])
                except Exception, e:
                    antenna_height = 'NA'

                try:
                    technology = data_list[10]
                except Exception, e:
                    technology = 'NA'

                try:
                    ss_name = data_list[11]
                except Exception, e:
                    ss_name = 'NA'

                icon_url = device_type_dict.get(device_type, '')

                if icon_url:
                    icon_url = icon_url.get('gmap_icon')

                label_str = ''

                page_type = 'customer'
                performance_url = ''
                inventory_url = ''

                if base_urls.get('performance'):
                    performance_url = base_urls.get('performance')
                    performance_url = performance_url.replace('page_type', page_type)
                    performance_url = performance_url.replace('0', str(device_id))

                if base_urls.get('inventory'):
                    inventory_url = base_urls.get('inventory')
                    inventory_url = inventory_url.replace('page_type', page_type)
                    inventory_url = inventory_url.replace('0', str(device_id))

                # Only in case if we have extra info then
                if len(data_list) > 12:

                    try:
                        customer_alias = data_list[12]
                    except Exception, e:
                        customer_alias = 'NA'

                    try:
                        pe_ip = data_list[13]
                    except Exception, e:
                        pe_ip = 'NA'

                    try:
                        qos_bandwidth = data_list[14]
                    except Exception, e:
                        qos_bandwidth = 'NA'

                    try:
                        polarization = data_list[15]
                    except Exception, e:
                        polarization = 'NA'

                    try:
                        mount_type = data_list[16]
                    except Exception, e:
                        mount_type = 'NA'

                    try:
                        mount_type = data_list[16]
                    except Exception, e:
                        mount_type = 'NA'

                    try:
                        antenna_type = data_list[17]
                    except Exception, e:
                        antenna_type = 'NA'

                    try:
                        cable_length = data_list[18]
                    except Exception, e:
                        cable_length = 'NA'

                    try:
                        ethernet_extender = data_list[19]
                    except Exception, e:
                        ethernet_extender = 'NA'

                    try:
                        building_height = data_list[20]
                    except Exception, e:
                        building_height = 'NA'

                    try:
                        tower_height = data_list[21]
                    except Exception, e:
                        tower_height = 'NA'

                    try:
                        customer_address = data_list[22]
                    except Exception, e:
                        customer_address = 'NA'

                    try:
                        ss_alias = data_list[23]
                    except Exception, e:
                        ss_alias = 'NA'

                    try:
                        rssi_during_acceptance = data_list[24]
                    except Exception, e:
                        rssi_during_acceptance = 'NA'

                    try:
                        date_of_acceptance = data_list[25]
                    except Exception, e:
                        date_of_acceptance = 'NA'

                    label_str += unicode(circuit_id) + '|'
                    label_str += unicode(customer_alias) + '|'
                    label_str += unicode(ip_address) + '|'
                    label_str += unicode(pe_ip) + '|'
                    label_str += unicode(qos_bandwidth) + '|'
                    label_str += unicode(antenna_height) + '|'
                    label_str += unicode(polarization) + '|'
                    label_str += unicode(mount_type) + '|'
                    label_str += unicode(antenna_type) + '|'
                    label_str += unicode(cable_length) + '|'
                    label_str += unicode(ethernet_extender) + '|'
                    label_str += unicode(building_height) + '|'
                    label_str += unicode(tower_height) + '|'
                    label_str += unicode(technology) + '|'
                    label_str += unicode(latitude) + ', ' + unicode(longitude) + '|'
                    label_str += unicode(customer_address) + '|'
                    label_str += unicode(ss_alias) + '|'
                    label_str += unicode(rssi_during_acceptance) + '|'
                    label_str += unicode(date_of_acceptance)

                ss_info = {
                    'id': ss_id,
                    'name': ss_name,
                    'device_id': device_id,
                    'device_name': device_name,
                    'ip_address': ip_address,
                    'device_type': device_type,
                    'device_tech': technology,
                    'lat': latitude,
                    'lon': longitude,
                    'inventory_url': inventory_url,
                    'perf_page_url': performance_url,
                    'circuit_id': circuit_id,
                    'markerUrl': icon_url,
                    'antenna_height': antenna_height,
                    'show_link': 1,
                    'link_color': '',
                    'label_str': label_str
                }                

                ss_dict[data_list[0]]['ss_list'].append(ss_info)
                ss_dict[data_list[0]]['ip_list'].append(ip_address)
                ss_dict[data_list[0]]['circuit_list'].append(circuit_id)

    return ss_dict


def prepare_raw_result_v2(resultset=None, bs_ids=[]):

    result = list()

    if not resultset:
        return result

    # Create performance page base url
    try:
        perf_page_base_url = reverse(
            'SingleDevicePerf',
            kwargs={
                'page_type': 'page_type', 
                'device_id': 0
            },
            current_app='performance'
        )
    except Exception, e:
        perf_page_base_url = ''

    # Create device inventory page base url
    try:
        inventory_base_url = reverse(
            'device_edit',
            kwargs={
                'pk': 0
            },
            current_app='device'
        )
    except Exception, e:
        inventory_base_url = ''

    base_urls_dict = {
        'inventory': inventory_base_url,
        'performance': perf_page_base_url
    }

    # Get the device type dict to get the device type gmap icon
    device_type_dict = getDeviceTypeNamedDict()
    # Fetch the device frequency to get the sector color as per freq id
    freq_dict = getFrequencyDict()
    # Device Technology List
    tech_list = list(DeviceTechnology.objects.all().values_list('name', flat=True))
    # Device Vendor List
    vendor_list = list(DeviceVendor.objects.all().values_list('name', flat=True))
    traced_sector_pk = list()
    traced_sector_id = list()
    
    for bs in resultset:
        if not bs.get('BSID'):
            continue

        # If non organization BS then don't plot it on map
        if bs_ids and bs.get('BSID') not in bs_ids:
            continue

        sector_info_str = bs.get('SECT_STR', '')

        temp_dict = {
            'bs_id': bs.get('BSID'),
            'name': bs.get('BSNAME'),
            'alias': bs.get('BSALIAS'),
            'region': bs.get('BSREGION'),
            'city': bs.get('BSCITY'),
            'state': bs.get('BSSTATE'),
            'total_ss': bs.get('TOTALSS'),
            'lat': bs.get('BSLAT'),
            'lon': bs.get('BSLON'),
            'icon_url': 'static/img/icons/bs.png',
            'bh_id': bs.get('BHID'),
            'bh_device_id': bs.get('BHDEVICEID'),
            'bh_device_ip': bs.get('BHDEVICEIP'),
            'bh_device_type': bs.get('BHDEVICETYPE'),
            'bh_device_tech': bs.get('BHDEVICETECH'),
            'maintenance_status': bs.get('BSMAINTENANCESTATUS'),
            'has_pps_alarm' : bs.get('has_pps'),
            'tech_str': '',
            'vendor_str': '',
            'freq_str': '',
            'polarization_str': '',
            'antenna_type_str': '',
            'sector_configured_on_devices': '',
            'circuit_ids': '',
            'sectors': []
        }

        sector_list = list()
        if sector_info_str:
            ss_info_str = bs.get('SS_STR', '')
            sector_info = sector_info_str.split('-|-|-')
            ss_info_dict = {}
            if ss_info_str:
                ss_info_dict = prepare_ss_info_dict(
                    ss_info_str.split('-|-|-'),
                    device_type_dict,
                    freq_dict,
                    base_urls_dict
                )

            for info in sector_info:
                splitted_str = info.split('|')
                try:
                    sector_pk = int(splitted_str[0])
                except Exception, e:
                    continue

                try:
                    sector_id = splitted_str[1]
                except Exception, e:
                    sector_id = ''

                if sector_pk in traced_sector_pk and sector_id in traced_sector_id:
                    continue

                if sector_pk not in traced_sector_pk:
                    traced_sector_pk.append(sector_pk)

                traced_sector_id.append(sector_id)

                try:
                    try:
                        technology = splitted_str[2] if splitted_str[2] in tech_list else 'NA'
                    except Exception, e:
                        technology = 'NA'
                    
                    try:
                        vendor = splitted_str[3] if splitted_str[3] in vendor_list else 'NA'
                    except Exception, e:
                        vendor = 'NA'
                    
                    try:
                        device_type = splitted_str[4]
                    except Exception, e:
                        device_type = 'NA'

                    try:
                        freq_id = str(splitted_str[5])
                    except Exception, e:
                        freq_id = 'NA'

                    try:
                        polarization = splitted_str[6]
                    except Exception, e:
                        polarization = 'NA'

                    try:
                        azimuth_angle = int(splitted_str[7])
                    except Exception, e:
                        azimuth_angle = 'NA'

                    try:
                        beamwidth = int(splitted_str[8])
                    except Exception, e:
                        beamwidth = 'NA'

                    try:
                        antenna_height = int(splitted_str[9])
                    except Exception, e:
                        antenna_height = 'NA'

                    try:
                        sector_ip = splitted_str[10]
                    except Exception, e:
                        sector_ip = ''

                    try:
                        device_name = splitted_str[11]
                    except Exception, e:
                        device_name = ''

                    try:
                        device_id = splitted_str[12]
                    except Exception, e:
                        device_id = ''

                    try:
                        antenna_type = splitted_str[13]
                    except Exception, e:
                        antenna_type = 'NA'

                    gmap_icon = ''
                    freq_val = ''
                    color = ''
                    radius = ''
                    # fetch marker icon from device_type dict
                    if device_type in device_type_dict:
                        device_type_obj = device_type_dict.get(device_type)
                        gmap_icon = device_type_obj.get('gmap_icon')

                    # Fetch freq color & value from freq dict
                    if freq_id in freq_dict:
                        freq_obj = freq_dict.get(freq_id)
                        color = freq_obj.get('color')
                        freq_val = freq_obj.get('value')
                        radius = freq_obj.get('radius', 0.5)

                    ss_data_obj = ss_info_dict.get(str(sector_pk), {})
                    ss_list = ss_data_obj.get('ss_list', [])
                    ip_list = ss_data_obj.get('ip_list', [])
                    circuit_list = ss_data_obj.get('circuit_list', [])

                    # Concat sectors technology
                    temp_dict['tech_str'] += technology + '|'
                    # Concat sectors vendor
                    temp_dict['vendor_str'] += vendor + '|'
                    # Concat sectors freq.
                    temp_dict['freq_str'] += freq_val + '|'
                    # Concat sectors antenna polarization
                    temp_dict['polarization_str'] += polarization + '|'
                    # Concat sectors antenna type
                    temp_dict['antenna_type_str'] += antenna_type + '|'
                    # Concat Sectors IP
                    temp_dict['sector_configured_on_devices'] += sector_ip + '|'
                    # Concat SS IPs
                    temp_dict['sector_configured_on_devices'] += '|'.join(ip_list) + '|'
                    # Concat Circuit ID's
                    temp_dict['circuit_ids'] += '|'.join(circuit_list) + '|'

                    perf_page_url = ''
                    inventory_url = ''
                    page_type = 'customer'
                    # Check for technology to make perf page url
                    if technology.lower() in ['pmp', 'wimax', 'ptp bh']:
                        page_type = 'network'

                    if perf_page_base_url:
                        perf_page_url = perf_page_base_url
                        perf_page_url = perf_page_url.replace('page_type', page_type)
                        perf_page_url = perf_page_url.replace('0', device_id)
                    else:
                        # Create Perf page url
                        try:
                            perf_page_url = reverse(
                                'SingleDevicePerf',
                                kwargs={
                                    'page_type': page_type, 
                                    'device_id': device_id
                                },
                                current_app='performance'
                            )
                        except Exception, e:
                            pass

                    # Sector Device Inventory URL
                    if inventory_base_url:
                        inventory_url = inventory_base_url
                        inventory_url = inventory_url.replace('0', device_id)
                    else:
                        try:
                            inventory_url = reverse(
                                'device_edit',
                                kwargs={
                                    'pk': device_id
                                },
                                current_app='device'
                            )
                        except Exception, e:
                            pass

                    sector = {
                        'id': sector_pk,
                        'device_name': device_name,
                        'sector_id': sector_id,
                        'technology': technology,
                        'vendor': vendor,
                        'device_type': device_type,
                        'azimuth_angle': azimuth_angle,
                        'beam_width': beamwidth,
                        'markerUrl': gmap_icon,
                        'color': color,
                        'radius': radius,
                        'inventory_url': inventory_url,
                        'perf_page_url': perf_page_url,
                        'freq': freq_val,
                        'ip_address': sector_ip,
                        'polarization': polarization,
                        'antenna_height': antenna_height,
                        'sub_stations': ss_list,
                        'device_id': device_id,
                        'antenna_type': antenna_type
                    }
                    sector_list.append(sector)
                except Exception, e:
                    continue
                
                temp_dict.update(sectors=sector_list)
        
        result.append(temp_dict)

    return result

@nocout_utils.cache_for(CACHE_TIME.get('INVENTORY', 300))
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

    def __init__(self):
        # Formatted inventory wrt the base stations.
        self.result = {
            "success": 0,
            "message": "Device Loading Completed",
            "data": {
                "meta": {},
                "objects": None
            }
        }
        self.raw_result = nocout_utils.get_maps_initial_data_cached(bs_id=[])
        super(DeviceStatsApi, self).__init__()

    def get(self, request):
        """
        get http method

        :param request: HTTP request
        """

        organizations = nocout_utils.logged_in_user_organizations(self)

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
            # self.result['data']['objects'] = {
            #     "id": "mainNode",
            #     "name": "mainNodeName",
            #     "data": {"unspiderfy_icon": "static/img/icons/bs.png"}
            # }
            self.result['data']['objects'] = {
                'children' : []
            }

            self.result['data']['objects']['children'] = prepare_raw_result_v2(
                resultset=self.raw_result,
                bs_ids=list(bs_id)
            )

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
            devices = eval(str(self.request.GET.get('devices', None)))
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
                r = requests.post(url, data=encoded_data)

                # Converting post response data into python dict expression.
                response_dict = ast.literal_eval(r.text)

                # If response(r) is given by post request than process it further to get success/failure messages.
                if r:
                    result['data']['value'].append(response_dict.get('value')[0])
                    tech = DeviceTechnology.objects.get(pk=device.device_technology)
                    device_type = DeviceType.objects.get(pk=device.device_type)

                    # Live polling settings for getting associates service and data sources.
                    lps = LivePollingSettings.objects.get(technology=tech,device_type=device_type, service=service, data_source=data_source)

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
            device_type (unicode): ID of type.

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
        device_type_id = int(self.request.GET.get('device_type', None))


        # Technology object.
        technology = DeviceTechnology.objects.get(pk=technology_id)
        # Type object.
        device_type = DeviceType.objects.get(pk=device_type_id)

        # Get live polling settings corresponding to the technology and type.
        lps = ""
        try:
            lps = LivePollingSettings.objects.filter(technology=technology,device_type=device_type)
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
            device_type (unicode): ID of device_type .

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
        device_type_id = int(self.request.GET.get('device_type', None))

        # Technology object.
        technology = DeviceTechnology.objects.get(pk=technology_id)
        # Device Type object.
        device_type = DeviceType.objects.get(pk=device_type_id)


        # Get live polling settings corresponding to the technology.
        lps = ""
        try:
            lps = LivePollingSettings.objects.filter(technology=technology,device_type=device_type)
        except Exception as e:
            logger.info(e.message)
        if service_type == 'ping':
            thematic_settings = PingThematicSettings.objects.filter(technology=technology,type=device_type)
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

        # Is radwin 5k device
        try:
            is_radwin5 = int(self.request.GET.get('is_radwin5', 0))
        except Exception, e:
            is_radwin5 = 0

        # Is first call or not(used in case of utilization for calculation)
        try:
            is_first_call = int(self.request.GET.get('is_first_call', 1))
        except Exception, e:
            is_first_call = 1

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

        # Create SDS key
        try:
            sds_key = service_name + '_' + ds_name
        except Exception, e:
            sds_key = ''


        # Thematic settings.
        try:
            ts_type = self.request.GET.get('ts_type', None)
        except Exception as e:
            ts_type = ""

        try:
            if sds_key in SERVICE_DATA_SOURCE:
                sds_data = SERVICE_DATA_SOURCE.get(sds_key)
                ds_name = sds_data.get('ds_name') if sds_data.get('ds_name') else ds_name
                service_name = sds_data.get('service_name') if sds_data.get('service_name') else service_name
        except Exception, e:
            pass

        # Exceptional services, i.e. 'ss' services which get service data from 'bs' instead from 'ss'.
        exceptional_services = [
            'wimax_dl_cinr', 'wimax_ul_cinr', 'wimax_dl_rssi', 'wimax_ul_rssi', 'wimax_ss_dl_utilization',
            'wimax_ss_ul_utilization', 'wimax_ul_intrf', 'wimax_dl_intrf', 'wimax_modulation_dl_fec', 
            'wimax_modulation_ul_fec', 'cambium_ul_rssi', 'cambium_ul_jitter', 'cambium_reg_count', 'cambium_rereg_count', 
            'rad5k_ul_rssi', 'rad5k_dl_rssi','rad5k_ss_dl_utilization' ,'rad5k_ss_ul_utilization',
            'rad5k_dl_time_slot_alloted_invent','rad5k_ul_time_slot_alloted_invent',  'rad5k_dl_estmd_throughput_invent', 
            'rad5k_ul_estmd_throughput_invent', 'rad5k_ul_uas_invent', 'rad5k_dl_es_invent', 'rad5k_ul_ses_invent', 
            'rad5k_ul_bbe_invent','rad5k_ss_cell_radius_invent', 'rad5k_ss_cmd_rx_pwr_invent', 'rad5k_ss_dl_utilization', 
            'rad5k_ss_ul_utilization', 'wimax_qos_invent', 'wimax_ss_session_uptime', 'rad5k_ss_mir_ul', 'rad5k_ss_mir_dl',
            'rad5k_ss2_ul_rssi', 'rad5k_ss2_dl_rssi', 'rad5k_ss_dl_estmd_throughput', 'rad5k_ss_ul_estmd_throughput',
            'rad5k_ss_data_vlan_invent', 'rad5k_ss_dl_modulation',
        ]

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
        # Fetch device type if ts_type present.
        ts_device_type = None

        if ts_type:
            try:
                ts_technology = DeviceTechnology.objects.get(id=Device.objects.get(
                    device_name=devices[0]).device_technology)
            except Exception as e:
                pass

            try:
                ts_device_type = DeviceType.objects.get(id=Device.objects.get(
                    device_name=devices[0]).device_type)
            except Exception as e:
                pass

        if not all([service_name, ds_name]):
            # Get thematic settings corresponding to the 'service_type'.
            if service_type == 'ping' or ts_type == 'ping':
                # Thematic settings (ping).
                if ts_type:
                    ts = self.get_thematic_settings(ts_type, ts_technology,ts_device_type).thematic_template
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
                    ts = self.get_thematic_settings(ts_type, ts_technology,ts_device_type).thematic_template
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

        # In case of 'rta' and 'pl', fetch data from 'service_data_sources' function.
        if ds_name in ['pl', 'rta']:
            ds_dict = SERVICE_DATA_SOURCE
            result['data']['meta'] = dict()
            result['data']['meta']['chart_type'] = ds_dict[ds_name]['type'] if 'type' in ds_dict[ds_name] else ""
            result['data']['meta']['chart_color'] = ds_dict[ds_name]['chart_color'] if 'chart_color' in ds_dict[
                ds_name] else ""
            result['data']['meta']['data_source_type'] = ds_dict[ds_name]['data_source_type'] if 'data_source_type' in \
                                                                                                 ds_dict[
                                                                                                     ds_name] else "Numeric"
            result['data']['meta']['is_inverted'] = ds_dict[ds_name]['is_inverted'] if 'is_inverted' in ds_dict[
                ds_name] else ""

            result['data']['meta']['valuesuffix'] = ds_dict[ds_name]['valuesuffix'] if 'valuesuffix' in ds_dict[
                ds_name] else ""

            result['data']['meta']['valuetext'] = ds_dict[ds_name]['valuetext'] if 'valuetext' in ds_dict[ds_name] else ""
            # Device Type Parameter of Device Name.
            device_type = Device.objects.filter(device_name__in=devices).values_list('device_type', flat=True)
            # Device Type warn crit params corresponding to Device.
            ds_warn_crit_param = DeviceType.objects.filter(id__in=device_type).values('pl_warning', 'pl_critical',
                                                                                      'rta_warning', 'rta_critical')

            if ds_name in ['pl']:
                result['data']['meta']['warning'] = ds_warn_crit_param[0]['pl_warning']
                result['data']['meta']['critical'] = ds_warn_crit_param[0]['pl_critical']
                result['data']['meta']['valuesuffix'] = ds_dict['pl']['valuesuffix'] if 'valuesuffix' in ds_dict['pl'] else ""
                result['data']['meta']['valuetext'] = ds_dict['pl']['valuetext'] if 'valuetext' in ds_dict['pl'] else ""
            elif ds_name in ['pl'] and not (
                        ds_warn_crit_param[0]['pl_warning'] and ds_warn_crit_param[0]['pl_critical']):
                result['data']['meta']['warning'] = PING_PL_WARNING
                result['data']['meta']['critical'] = PING_PL_CRITICAL
            elif ds_name in ['rta']:
                result['data']['meta']['warning'] = ds_warn_crit_param[0]['rta_warning']
                result['data']['meta']['critical'] = ds_warn_crit_param[0]['rta_critical']
                result['data']['meta']['valuesuffix'] = ds_dict['rta']['valuesuffix'] if 'valuesuffix' in ds_dict['rta'] else ""
                result['data']['meta']['valuetext'] = ds_dict['rta']['valuetext'] if 'valuetext' in ds_dict['rta'] else ""
            elif ds_name in ['rta'] and not (
                        ds_warn_crit_param[0]['rta_warning'] and ds_warn_crit_param[0]['rta_critical']):
                result['data']['meta']['warning'] = PING_RTA_WARNING
                result['data']['meta']['critical'] = PING_RTA_CRITICAL

            ds_formula = ds_dict[ds_name]['formula'] if 'formula' in ds_dict[ds_name] else ""
        else:
            # Data source object.
            ds_formula = ""
            ds_obj = None
            try:
                ds_obj = ServiceDataSource.objects.get(name=data_source)
                ds_formula = ds_obj.formula
            except Exception as e:
                logger.info(e.message)

            if ds_obj:
                result['data']['meta'] = dict()
                result['data']['meta']['chart_type'] = ds_obj.chart_type
                result['data']['meta']['chart_color'] = ds_obj.chart_color
                result['data']['meta']['is_inverted'] = ds_obj.is_inverted
                result['data']['meta']['data_source_type'] = ds_obj.ds_type_name()
                result['data']['meta']['valuetext'] = ''
                result['data']['meta']['valuesuffix'] = ''

                try:
                    result['data']['meta']['valuetext'] = ds_obj.valuetext
                    result['data']['meta']['valuesuffix'] = ds_obj.valuesuffix
                except Exception, e:
                    result['data']['meta']['valuetext'] = ''
                    result['data']['meta']['valuesuffix'] = ''

                try:
                    ds_dtype_obj = DeviceTypeServiceDataSource.objects.get(
                        device_type_service__service__name=service,
                        service_data_sources__name=data_source
                    )
                    result['data']['meta']['warning'] = ds_dtype_obj.warning
                    result['data']['meta']['critical'] = ds_dtype_obj.critical
                except Exception as e:
                    result['data']['meta']['warning'] = ds_obj.warning
                    result['data']['meta']['critical'] = ds_obj.critical

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

                            if is_radwin5:
                                # IP address of device.
                                ip_address = device.ip_address

                                # Base station device name to which 'ss' is connected.
                                bs_device = Topology.objects.get(connected_device_ip=ip_address)
                            else:
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

                                if is_radwin5:
                                    # IP address of device.
                                    device_ss_mac = device.ip_address

                                    # Insert data in 'ss_name_mac_mapping' dictionary.
                                    ss_name_mac_mapping[device.device_name] = device_ss_mac

                                    # Base station device name to which 'ss' is connected.
                                    bs_device = Topology.objects.get(connected_device_ip=device_ss_mac)
                                else:
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
                    lp_data['is_first_call'] = is_first_call

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

                        try:
                            if ds_name in ['pl']:
                                if device_value >= ds_warn_crit_param[0]['pl_critical']:
                                    result['data']['meta']['chart_color'] = '#FF193B'
                                elif device_value < ds_warn_crit_param[0]['pl_critical'] and device_value >= ds_warn_crit_param[0]['pl_warning']:
                                    result['data']['meta']['chart_color'] = '#FFE90D'
                                else:
                                    pass
                        except Exception as e:
                            pass
                        # Evaluate value if formula is available for data source.
                        if ds_formula:
                            device_val = device_value
                            try:
                                if type(device_value) == list:
                                    device_val = device_value[0]

                                result['data']['devices'][device_name]['value'] = eval(
                                    str(ds_formula) + "(" + str(device_val) + ")")
                            except Exception as e:
                                result['data']['devices'][device_name]['value'] = device_val
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

    def get_thematic_settings(self, ts_type, device_technology,device_type):
        """
            Get user thematic settings.

            Args:
                ts_type (unicode): Thematic settings type i.e 'ping' or 'normal'.
                device_technology (<class 'device.models.DeviceTechnology'>): Device technology object.
                device_type (<class 'device.models.DeviceType'>): Device type object.

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
        device_type = device_type

        # Fetch thematic settings for current user.
        if ts_type == "normal":
            try:
                user_thematics = UserThematicSettings.objects.get(user_profile=current_user,
                                                                  thematic_technology=device_technology,
                                                                  thematic_type=device_type)
            except Exception as e:
                return user_thematics

        elif ts_type == "ping":
            try:
                user_thematics = UserPingThematicSettings.objects.get(user_profile=current_user,
                                                                      thematic_technology=device_technology,
                                                                      thematic_type=device_type)
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


class GetVendorsForTech(APIView):
    """
    Fetch vendors corresponding to the selected technology.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_tech_vendors/4/"
    """

    def get(self, request, pk):
        """
        Processing API request.
        Args:
            pk (unicode): Selected option value.

        Returns:
            result (str): JSON formatted response.
                         For e.g.,
                            [
                                {
                                    "alias": "Cambium",
                                    "id": 4,
                                    "name": "Cambium"
                                },
                                {
                                    "alias": "RAD",
                                    "id": 7,
                                    "name": "RAD"
                                },
                                {
                                    "alias": "MROTek",
                                    "id": 8,
                                    "name": "MROtek"
                                }
                            ]
        """
        tech_id = pk

        # Response of api.
        result = list()

        # Technology object.
        tech = None
        if tech_id:
            tech = DeviceTechnology.objects.filter(id=tech_id)

        # Fetch vendors associated with the selected technology.
        if tech:
            vendors = tech[0].device_vendors.all()

            result = [{'id': value.id,
                       'name': value.name,
                       'alias': value.alias} for value in vendors]

        return Response(result)


class GetModelsForVendor(APIView):
    """
    Fetch models corresponding to the selected vendor.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_vendor_models/4/"
    """

    def get(self, request, pk):
        """
        Processing API request.
        Args:
            pk (unicode): Selected option value.

        Returns:
            result (str): JSON formatted response.
                         For e.g.,
                            [
                                {
                                    "alias": "CanopyPM100",
                                    "id": 4,
                                    "name": "CanopyPM100"
                                },
                                {
                                    "alias": "CanopySM100",
                                    "id": 5,
                                    "name": "CanopySM100"
                                }
                            ]
        """
        vendor_id = pk

        # Response of api.
        result = list()

        # Vendor object.
        vendor = None
        if vendor_id:
            vendor = DeviceVendor.objects.filter(id=vendor_id)

        # Fetch models associated with the selected vendor.
        if vendor:
            models = vendor[0].device_models.all()

            result = [{'id': value.id,
                       'name': value.name,
                       'alias': value.alias} for value in models]

        return Response(result)


class GetTypesForModel(APIView):
    """
    Fetch types corresponding to the selected model.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_model_types/4/"
    """

    def get(self, request, pk):
        """
        Processing API request.
        Args:
            pk (unicode): Selected option value.

        Returns:
            result (str): JSON formatted response.
                         For e.g.,
                            [
                                {
                                    "alias": "CanopyPM100",
                                    "id": 4,
                                    "name": "CanopyPM100"
                                },
                                {
                                    "alias": "CanopySM100",
                                    "id": 5,
                                    "name": "CanopySM100"
                                }
                            ]
        """
        model_id = pk

        # Response of api.
        result = list()

        # Model object.
        model = None
        if model_id:
            model = DeviceModel.objects.filter(id=model_id)

        # Fetch types associated with the selected model.
        if model:
            types = model[0].device_types.all()

            result = [{'id': value.id,
                       'name': value.name,
                       'alias': value.alias} for value in types]

        return Response(result)


class GetTypesForTech(APIView):
    """
    Fetch type corresponding to the selected technology.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_tech_types/4/"
    """

    def get(self, request, pk):
        """
        Processing API request.
        Args:
            pk (unicode): Selected option value.

        Returns:
            result (str): JSON formatted response.
                         For e.g.,
                            [
                                {
                                    "alias": "Cambium",
                                    "id": 4,
                                    "name": "Cambium"
                                },
                                {
                                    "alias": "RAD",
                                    "id": 7,
                                    "name": "RAD"
                                },
                                {
                                    "alias": "MROTek",
                                    "id": 8,
                                    "name": "MROtek"
                                }
                            ]
        """
        tech_id = pk

        # Response of api.
        result = list()

        # Technology object.
        tech = None
        if tech_id:
            tech = DeviceTechnology.objects.filter(id=tech_id)

        if tech:
            # Fetch types associated with the selected technology.
            types = DeviceType.objects.filter(
                id__in=DeviceModel.objects.filter(
                    id__in=DeviceVendor.objects.filter(
                        id__in=DeviceTechnology.objects.get(id=tech_id).technologyvendor_set.values_list('vendor_id', flat=True)
                    ).values_list('vendormodel__model_id', flat=True)
                ).values_list('modeltype__type_id', flat=True))

            result = [{'id': value.id,
                       'name': value.name,
                       'alias': value.alias} for value in types]

        return Response(result)


class GetDevicePorts(APIView):
    """
    Fetch device ports corresponding to the selected device type.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_device_ports/4/"
    """

    def get(self, request, pk):
        """
        Processing API request.
        Args:
            pk (unicode): Selected option value.

        Returns:
            result (str): JSON formatted response.
                         For e.g.,
                            [
                                {
                                    "alias": "PMP Port 1",
                                    "id": 1,
                                    "value": 1,
                                    "name": "pmp_port_1"
                                },
                                {
                                    "alias": "PMP Port 2",
                                    "id": 2,
                                    "value": 2,
                                    "name": "pmp_port_2"
                                }
                            ]
        """
        type_id = pk

        # Response of api.
        result = list()

        # Device type object.
        device_types = None
        if type_id:
            device_types = DeviceType.objects.filter(id=type_id)

        # Fetch ports associated with the selected device type.
        if device_types:
            ports = device_types[0].device_port.all()

            result = [{'id': value.id,
                       'name': value.name,
                       'alias': value.alias,
                       'value': value.value} for value in ports]

        return Response(result)


class GetSitesForMachine(APIView):
    """
    Fetch sites corresponding to the selected machine.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_machine_sites/4/"
    """

    def get(self, request, pk):
        """
        Processing API request.
        Args:
            pk (unicode): Selected option value.

        Returns:
            result (str): JSON formatted response.
                         For e.g.,
                            [
                                {
                                    "alias": "CanopyPM100",
                                    "id": 4,
                                    "name": "CanopyPM100"
                                },
                                {
                                    "alias": "CanopySM100",
                                    "id": 5,
                                    "name": "CanopySM100"
                                }
                            ]
        """
        machine_id = pk

        # Response of api.
        result = list()

        # Machine object.
        machine = None
        if machine_id:
            machine = Machine.objects.filter(id=machine_id)

        # Fetch sites associated with the selected machine.
        if machine:
            sites = machine[0].siteinstance_set.all()

            result = [{'id': value.id,
                       'name': value.name,
                       'alias': value.alias} for value in sites]

        return Response(result)


class GetDeviceTypeExtraFields(APIView):
    """
    Fetch device extra fields corresponding to the device type.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_extra_fields/4/"
    """

    def get(self, request, pk):
        """
        Processing API request.
        Args:
            pk (unicode): Selected option value.

        Returns:
            result (str): JSON formatted response.
                         For e.g.,
                            [
                                {
                                    "alias": "CanopyPM100",
                                    "id": 4,
                                    "name": "CanopyPM100"
                                },
                                {
                                    "alias": "CanopySM100",
                                    "id": 5,
                                    "name": "CanopySM100"
                                }
                            ]
        """
        device_type_id = pk

        # Response of api.
        result = list()

        # Device Type object.
        device_types = None
        if device_type_id:
            device_types = DeviceType.objects.filter(id=device_type_id)

        # Fetch device extra fields.
        device_extra_fields = None
        if device_extra_fields:
            device_extra_fields = device_types[0].devicetypefields_set.all()

        # Fetch sites associated with the selected machine.
        if device_extra_fields:
            result = [{'id': value.id,
                       'name': value.field_name,
                       'alias': value.field_display_name} for value in device_extra_fields]

        return Response(result)


class GetDevicesForSelectionMenu(APIView):
    """
    Fetch list of devices for selection menu.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/devices_for_menu/m/"
    """

    def get(self, request, flag):
        """
        Processing API request.
        Args:
            state (unicode): Device state.
                             all: a
                             is_added_to_nms: n
                             is_monitored_on_nms: m
                             enable: e
                             disable: d
                             is_deleted: sd

        Returns:
            result (str): JSON formatted response.
                         For e.g.,
                            [
                                {
                                    "id": 11343,
                                    "device_name": "11343",
                                    "device_alias": "1131208803",
                                    "ip_address": "10.168.40.21"
                                },
                                {
                                    "id": 11345,
                                    "device_name": "11345",
                                    "device_alias": "091NEWD030008192497",
                                    "ip_address": "10.168.28.49"
                                }
                            ]
        """
        # Status flag.
        flag = flag

        # Response of api.
        result = list()

        # Get all devices.
        devices = None
        if flag == 'a':
            devices = Device.objects.all()
        elif flag == 'n':
            devices = Device.objects.filter(is_added_to_nms__in=[1, 2]).values('id',
                                                                               'device_name',
                                                                               'device_alias',
                                                                               'ip_address')
        elif flag == 'm':
            devices = Device.objects.filter(is_monitored_on_nms__in=[1, 2]).values('id',
                                                                                   'device_name',
                                                                                   'device_alias',
                                                                                   'ip_address')
        elif flag == 'e':
            devices = Device.objects.filter(host_state='enable').values('id',
                                                                        'device_name',
                                                                        'device_alias',
                                                                        'ip_address')
        elif flag == 'd':
            devices = Device.objects.filter(host_state='disable').values('id',
                                                                         'device_name',
                                                                         'device_alias',
                                                                         'ip_address')
        elif flag == 'sd':
            devices = Device.objects.filter(is_deleted=1).values('id',
                                                                 'device_name',
                                                                 'device_alias',
                                                                 'ip_address')
        else:
            pass

        serializer = DeviceParentSerializer(devices, many=True)

        return Response(serializer.data)


class GetDeviceInventory(APIView):
    """
    Fetch list of devices corresponding to the passed status.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/device_inventory/m/"
    """

    def get(self, request, flag):
        """
        Processing API request.

        Args:
            state (unicode): Device state.
                             all: a
                             is_added_to_nms: n
                             is_monitored_on_nms: m
                             enable: e
                             disable: d
                             is_deleted: sd

        Returns:
            result (str): JSON formatted response.
                         For e.g.,
                            [
                                {
                                    "id": 11343,
                                    "device_name": "11343",
                                    "device_alias": "1131208803",
                                    "device_technology": 3,
                                    "device_vendor": 3,
                                    "device_model": 3,
                                    "device_type": 5,
                                    "ip_address": "10.168.40.21",
                                    "mac_address": "00:02:73:92:d9:73",
                                    "netmask": null,
                                    "gateway": null,
                                    "dhcp_state": "Disable",
                                    "host_priority": "Normal",
                                    "host_state": "Disable",
                                    "latitude": 28.7174,
                                    "longitude": 77.1235,
                                    "timezone": "Asia/Kolkata",
                                    "address": "PLOT NO.-5 VIKAS SURYA PLAZA COMMUNITYCENTRE DC CHOWK SECTOR-9
                                                ROHININEW DELHI 110085",
                                    "description": "Sub Station created on 25-Feb-2015 at 17:29:16.",
                                    "is_deleted": 0,
                                    "is_added_to_nms": 1,
                                    "is_monitored_on_nms": 1,
                                    "lft": 1340,
                                    "rght": 1341,
                                    "tree_id": 2,
                                    "level": 1,
                                    "machine": 4,
                                    "site_instance": 5,
                                    "organization": 1,
                                    "parent": 10244,
                                    "country": 1,
                                    "state": null,
                                    "city": null,
                                    "ports": []
                                }
                            ]
        """

        # Status flag.
        flag = flag

        # Get all devices.
        devices = None
        if flag == 'a':
            devices = Device.objects.all()
        elif flag == 'n':
            devices = Device.objects.filter(is_added_to_nms__in=[1, 2])
        elif flag == 'm':
            devices = Device.objects.filter(is_monitored_on_nms__in=[1, 2])
        elif flag == 'e':
            devices = Device.objects.filter(host_state='enable')
        elif flag == 'd':
            devices = Device.objects.filter(host_state='disable')
        elif flag == 'sd':
            devices = Device.objects.filter(is_deleted=1)
        else:
            pass

        serializer = DeviceInventorySerializer(devices, many=True)

        return Response(serializer.data)


class GetEligibleParentDevices(APIView):
    """
    Fetch devices which are eligible to be the parent of child devices of device which needs to be soft deleted.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_eligible_parent/10244/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            value (int): Device ID.

        Returns:
            result (dictionary): Dictionary contains device and it's children's values.
                                 For e.g.,
                                    {
                                        "message": "Successfully render form.",
                                        "data": {
                                            "meta": "",
                                            "objects": {
                                                "childs": [
                                                    {
                                                        "value": "11337",
                                                        "key": 11337
                                                    },
                                                    {
                                                        "value": "11339",
                                                        "key": 11339
                                                    },
                                                    {
                                                        "value": "11343",
                                                        "key": 11343
                                                    }
                                                ],
                                                "form_title": "device",
                                                "form_type": "device",
                                                "id": 10244
                                            }
                                        },
                                        "success": 1
                                    }

        Note:
            * Child Devices: These are the devices which are associated with the device,
                             which needs to be deleted in parent-child relationship.
            * Child Device Descendant: Set of all child devices descendants (needs for
                                       filtering new parent devices choice).
            * Eligible Devices: These are the devices which are not associated with the device,
                                (which needs to be deleted) & are eligible to be the
                                parent of devices in child devices.
        """
        device = Device.objects.get(id=pk)

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to render form correctly."
        result['data']['meta'] = ''
        result['data']['objects'] = {}
        result['data']['objects']['form_type'] = 'device'
        result['data']['objects']['form_title'] = 'device'
        result['data']['objects']['id'] = device.id
        result['data']['objects']['name'] = device.device_name
        result['data']['objects']['ip_address'] = device.ip_address

        # These are the devices which are associated with the device,
        # which needs to be deleted in parent-child relationship.
        child_devices = Device.objects.filter(parent_id=pk, is_deleted=0)

        # Set of all child devices descendants (needs for filtering new parent devices choice).
        child_device_descendants = []
        for child_device in child_devices:
            device_descendant = child_device.get_descendants()
            for cd in device_descendant:
                child_device_descendants.append(cd)

        result['data']['objects']['childs'] = []
        result['data']['objects']['eligible'] = []

        # Future device parent is needed to find out only if our device is
        # associated with any other device i.e if child_devices.count() > 0.
        if child_devices.count() > 0:
            # These are the devices which are not associated with the
            # device (which needs to be deleted) & are eligible to be the
            # parent of devices in child_devices.
            remaining_devices = Device.objects.exclude(parent_id=pk)
            selected_devices = set(remaining_devices) - set(child_device_descendants)
            result['data']['objects']['eligible'] = []
            for e_dv in selected_devices:
                e_dict = dict()
                e_dict['key'] = e_dv.id
                e_dict['value'] = e_dv.device_name
                # For excluding 'device' which we are deleting from eligible
                # device choices.
                if e_dv.id == device.id:
                    continue
                if e_dv.is_deleted == 1:
                    continue
                # For excluding devices from eligible device choices those are not from
                # same device_group as the device which we are deleting.
                # if set(e_dv.device_group.all()) != set(device.device_group.all()): continue
                result['data']['objects']['eligible'].append(e_dict)
            for c_dv in child_devices:
                c_dict = dict()
                c_dict['key'] = c_dv.id
                c_dict['value'] = c_dv.device_name
                result['data']['objects']['childs'].append(c_dict)

        result['success'] = 1
        result['message'] = "Successfully render form."

        return Response(result)


class DeviceSoftDelete(APIView):
    """
    Soft delete device i.e. not deleting device from database, it just set
    it's is_deleted field value to 1 & remove it's relationship with any other device
    & make some other device parent of associated device.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/device_soft_delete/10244/1/"
    """

    def get(self, request, device_id, new_parent_id):
        """
        Processing API request.

        Args:
            device_id (unicode): ID of device which needs to be deleted.
            new_parent_id (unicode): ID of device which is new parent of child devices.

        Returns:
            result (dictionary): Dictionary contains device and it's children's values.
                                 For e.g.,
                                    {
                                        "message": "Successfully deleted.",
                                        "data": {
                                            "meta": "",
                                            "objects": {
                                                "device_name": "10244",
                                                "device_id": "10244"
                                            }
                                        },
                                        "success": 1
                                    }
        """
        device = Device.objects.get(id=device_id)

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "No data exists."
        result['data']['meta'] = ''
        result['data']['objects'] = {}
        result['data']['objects']['device_id'] = device_id
        result['data']['objects']['device_name'] = device.device_name

        # New parent device for associated devices.
        new_parent = ""

        try:
            new_parent = Device.objects.get(id=new_parent_id)
        except Exception as e:
            logger.info("No new device parent exist. Exception: ", e.message)

        # Fetching all child devices of device which needs to be deleted.
        child_devices = ""
        try:
            child_devices = Device.objects.filter(parent_id=device_id)
        except Exception as e:
            logger.info("No child device exists. Exception: ", e.message)

        # Assign new parent device to all child devices.
        if new_parent:
            if child_devices.count() > 0:
                child_devices.update(parent=new_parent)

        # Delete device from nms core if it is already added there(nms core).
        if device.host_state != "Disable" and device.is_added_to_nms != 0:
            device.is_added_to_nms = 0
            device.is_monitored_on_nms = 0
            device.save()
            # Remove device services from 'service_deviceserviceconfiguration' table.
            DeviceServiceConfiguration.objects.filter(device_name=device.device_name).delete()
            # Remove device ping service from 'service_devicepingconfiguration' table.
            DevicePingConfiguration.objects.filter(device_name=device.device_name).delete()

        # Setting 'is_deleted' bit of device to 1 which means device is soft deleted.
        if device.is_deleted == 0:
            device.is_deleted = 1
            device.save()
            # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
            try:
                device.site_instance.is_device_change = 1
                device.site_instance.save()
            except Exception as e:
                pass
            result['success'] = 1
            result['message'] = "Successfully deleted."
        else:
            result['success'] = 0
            result['message'] = "Already soft deleted."

        return Response(result)


class DeviceRestoreDispalyData(APIView):
    """
    Get data to show on device restore form.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/device_restore_display_data/1/"
    """

    def get(self, request, value):
        """
        Processing API request.

        Args:
            value (unicode): Device ID.

        Returns:
            result (dictionary): Dictionary contains device and it's children's values.
                                 For e.g.,
                                    {
                                        'message': 'Successfully render form.',
                                        'data': {
                                            'meta': '',
                                            'objects': {
                                                'alias': u'091HYDE030007077237_NE',
                                                'id': 6247L,
                                                'name': u'1'
                                            }
                                        },
                                        'success': 1
                                    }
        """
        device = Device.objects.get(id=value)

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to render form correctly."
        result['data']['meta'] = ''
        result['data']['objects'] = {}

        if device:
            result['data']['objects']['id'] = device.id
            result['data']['objects']['ip_address'] = device.ip_address
            result['data']['objects']['name'] = device.device_name
            result['data']['objects']['alias'] = device.device_alias
            result['success'] = 1
            result['message'] = "Successfully render form."

        return Response(result)


class RestoreDevice(APIView):
    """
    Restoring device to device inventory.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/device_restore/1/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            device_id (unicode): Device ID.

        Returns:
            result (dictionary): Dictionary contains device and it's children's values.
                                 For e.g.,
                                    {
                                        'message': 'Successfully restored device (091HYDE030007077237_NE).',
                                        'data': {
                                            'meta': '',
                                            'objects': {
                                                'device_name': u'1',
                                                'device_id': u'6247'
                                            }
                                        },
                                        'success': 1
                                    }

        """
        device = Device.objects.get(id=pk)

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "No data exists."
        result['data']['meta'] = ''
        result['data']['objects'] = {}
        result['data']['objects']['device_id'] = pk
        result['data']['objects']['device_name'] = device.device_name

        # Setting 'is_deleted' bit of device to 0 which means device is restored.
        if device.is_deleted == 1:
            device.is_deleted = 0
            device.save()
            # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
            try:
                device.site_instance.is_device_change = 1
                device.site_instance.save()
            except Exception as e:
                pass
            result['success'] = 1
            result['message'] = "Successfully restored device ({}).".format(device.device_alias)
        else:
            result['success'] = 0
            result['message'] = "Already restored."

        return Response(result)


class AddDeviceToNMSDisplayInfo(APIView):
    """
    Generate form content for device addition to nms core.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/add_device_to_nms_display_info/10244/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            pk (unicode): Device ID.

        Returns:
            result (dict): Dictionary of ping parameters associated with device type.
                           For e.g.,
                                {
                                    "message": "Successfully fetched ping parameters from database.",
                                    "data": {
                                        "rta_critical": 30,
                                        "packets": 10,
                                        "meta": "",
                                        "timeout": 10,
                                        "pl_critical": 30,
                                        "normal_check_interval": 5,
                                        "pl_warning": 20,
                                        "rta_warning": 20,
                                        "device_id": "10244"
                                    },
                                    "success": 1
                                }

        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to get device ping data."
        result['data']['meta'] = ''

        device = Device.objects.get(pk=pk)

        try:
            device_type = DeviceType.objects.get(pk=device.device_type)
            # Get device ping information which is a ssociated which device type (if exist).
            ping_packets = device_type.packets if device_type.packets else settings.PING_PACKETS
            ping_timeout = device_type.timeout if device_type.timeout else settings.PING_TIMEOUT
            ping_normal_check_interval = device_type.normal_check_interval if device_type.normal_check_interval \
                else settings.PING_NORMAL_CHECK_INTERVAL
            ping_rta_warning = device_type.rta_warning if device_type.rta_warning else settings.PING_RTA_WARNING
            ping_rta_critical = device_type.rta_critical if device_type.rta_critical else settings.PING_RTA_CRITICAL
            ping_pl_warning = device_type.pl_warning if device_type.pl_warning else settings.PING_PL_WARNING
            ping_pl_critical = device_type.pl_critical if device_type.pl_critical else settings.PING_PL_CRITICAL
            result['message'] = "Successfully fetched ping parameters from database."
            result['success'] = 1
        except Exception as e:
            # If device type doesn't have ping parameters associated than use default ones.
            ping_packets = 60
            ping_timeout = 20
            ping_normal_check_interval = 5
            ping_rta_warning = 1500
            ping_rta_critical = 3000
            ping_pl_warning = 80
            ping_pl_critical = 100
            result['message'] = "Successfully get default ping parameters."
            result['success'] = 1
            logger.info(e.message)

        result['data']['device_id'] = pk
        result['data']['packets'] = ping_packets
        result['data']['timeout'] = ping_timeout
        result['data']['normal_check_interval'] = ping_normal_check_interval
        result['data']['rta_warning'] = ping_rta_warning
        result['data']['rta_critical'] = ping_rta_critical
        result['data']['pl_warning'] = ping_pl_warning
        result['data']['pl_critical'] = ping_pl_critical

        return Response(result)


class AddDeviceToNMS(APIView):
    """
    Adding device to nms core.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/add_device_to_nms/10244/?ping_data={}"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            pk (unicode): Device ID.
            ping_data (unicode): String containing device ping data in dictionary format.

        Returns:
            result (dict): Dictionary of device info.
                           For e.g.,
                              {
                                  'message': 'Deviceaddedsuccessfully.',
                                  'data': {
                                      'site': u'nocout_gis_slave',
                                      'agent_tag': u'snmp',
                                      'mode': 'addhost',
                                      'device_name': u'device_116',
                                      'device_alias': u'Device116',
                                      'ip_address': u'115.111.183.116'
                                  },
                                  'success': 1
                              }
        """
        # Ping data.
        ping_data = None
        try:
            ping_data = eval(self.request.GET.get('ping_data'))
        except Exception as e:
            pass

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "<i class=\"fa fa-times red-dot\"></i>Device addition failed."
        result['data']['meta'] = ''

        # Device object.
        device = None
        try:
            device = Device.objects.get(pk=pk)
        except Exception as e:
            pass

        if device:
            ping_levels = {
                "rta": (ping_data['rta_warning'] if ping_data['rta_warning'] else 1500,
                        ping_data['rta_critical'] if ping_data['rta_critical'] else 3000),
                "loss": (ping_data['pl_warning'] if ping_data['pl_warning'] else 80,
                         ping_data['pl_critical'] if ping_data['pl_critical'] else 100),
                "packets": ping_data['packets'] if ping_data['packets'] and ping_data['packets'] <= 20 else 6,
                "timeout": ping_data['timeout'] if ping_data['timeout'] else 20}

            if device.host_state != "Disable":
                # Get 'agent_tag' from DeviceType model.
                agent_tag = ""
                device_type_name = ""
                try:
                    device_type_object = DeviceType.objects.get(id=device.device_type)
                    agent_tag = device_type_object.agent_tag
                    device_type_name = device_type_object.name
                except Exception as e:
                    logger.info(e.message)

                device_data = {
                    'device_name': str(device.device_name),
                    'device_alias': str(device.device_alias),
                    'ip_address': str(device.ip_address),
                    'agent_tag': str(agent_tag),
                    'site': str(device.site_instance.name),
                    'mode': 'addhost',
                    'ping_levels': ping_levels,
                    'parent_device_name': None,
                    'mac': str(device.mac_address),
                    'device_type': device_type_name
                }

                device_tech = DeviceTechnology.objects.filter(id=device.device_technology)
                if len(device_tech) and device_tech[0].name.lower() in ['pmp', 'wimax']:
                    if device.substation_set.exists():
                        try:
                            substation = device.substation_set.get()

                            # Check for the circuit.
                            if substation.circuit_set.exists():
                                circuit = substation.circuit_set.get()
                                sector = circuit.sector
                                parent_device = sector.sector_configured_on
                                device_data.update({
                                    'parent_device_name': parent_device.device_name
                                })
                            else:
                                result['message'] = "<i class=\"fa fa-check red-dot\"></i> \
                                                     Could not find BS for this SS in the topology."
                                return json.dumps({'result': result})

                        except Exception as e:
                            result['message'] = "<i class=\"fa fa-check red-dot\"></i> \
                                                 Could not find BS for this SS in the topology."
                            logger.exception(e.message)
                            return json.dumps({'result': result})

                dpc = DevicePingConfiguration()
                dpc.device_name = device.device_name
                dpc.device_alias = device.device_alias
                dpc.packets = ping_data['packets']
                dpc.timeout = ping_data['timeout']
                dpc.normal_check_interval = ping_data['normal_check_interval']
                dpc.rta_warning = ping_data['rta_warning']
                dpc.rta_critical = ping_data['rta_critical']
                dpc.pl_warning = ping_data['pl_warning']
                dpc.pl_critical = ping_data['pl_critical']
                dpc.save()
                result['message'] = "<i class=\"fa fa-check green-dot\"></i> Device added successfully."
                # Set 'is_added_to_nms' to 1 after device successfully added to nocout nms core.
                device.is_added_to_nms = 1
                result['success'] = 1
                # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
                try:
                    device.site_instance.is_device_change = 1
                    device.site_instance.save()
                except Exception as e:
                    pass
                device.save()
            else:
                result['message'] = "<i class=\"fa fa-check red-dot\"></i> Device state is disabled. \
                                     First enable it than add it to nms core."
        else:
            result['message'] = "Device doesn't exist."

        return Response(result)


class EditDeviceInNMS(APIView):
    """
    Editing device in nms core.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/edit_device_in_nms/10244/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            pk (unicode): Device ID.

        Returns:
            result (dict): Dictionary of device info.
                           For e.g,
                              {
                                  'message': 'Deviceeditedsuccessfully.',
                                  'data': {
                                      'site': u'nocout_gis_slave',
                                      'agent_tag': u'snmp',
                                      'mode': 'edithost',
                                      'device_name': u'device_116',
                                      'device_alias': u'Device116',
                                      'ip_address': u'115.111.183.116'
                                  },
                                  'success': 1
                              }

        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Device edit failed."
        result['data']['meta'] = ''

        # Device object.
        device = None
        try:
            device = Device.objects.get(pk=pk)
        except Exception as e:
            pass

        if device:
            if device.host_state != "Disable":
                # Get 'agent_tag' from DeviceType model.
                agent_tag = ""
                try:
                    agent_tag = DeviceType.objects.get(id=device.device_type).agent_tag
                except Exception as e:
                    logger.info(e.message)
                device_data = {
                    'device_name': device.device_name,
                    'device_alias': device.device_alias,
                    'ip_address': device.ip_address,
                    'agent_tag': agent_tag,
                    'site': device.site_instance.name,
                    'mode': 'edithost',
                    'parent_device_name': None,
                    'mac': device.mac_address
                }
                device_tech = DeviceTechnology.objects.filter(id=device.device_technology)

                if len(device_tech) and device_tech[0].name.lower() in ['pmp', 'wimax']:
                    if device.substation_set.exists():
                        try:
                            substation = device.substation_set.get()
                            # Check for the circuit.
                            if substation.circuit_set.exists():
                                circuit = substation.circuit_set.get()
                                sector = circuit.sector
                                parent_device = sector.sector_configured_on
                                device_data.update({
                                    'parent_device_name': parent_device.device_name
                                })
                            else:
                                result['message'] = "<i class=\"fa fa-check red-dot\"></i> \
                                                     Could not find BS for this SS in the topology."
                                return json.dumps({'result': result})
                        except Exception as e:
                            result['message'] = "<i class=\"fa fa-check red-dot\"></i> \
                                                 Could not find BS for this SS in the topology."
                            logger.exception(e.message)
                            return json.dumps({'result': result})

                result['message'] = "<i class=\"fa fa-check green-dot\"></i> Device edited successfully."
                # Set 'is_added_to_nms' to 1 after device successfully edited in nocout nms core.
                device.is_added_to_nms = 1
                device.save()
                result['success'] = 1

                # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
                try:
                    device.site_instance.is_device_change = 1
                    device.site_instance.save()
                except Exception as e:
                    pass
            else:
                result['message'] = "<i class=\"fa fa-info text-info\"></i> Device state is disabled. \
                                     First enable it than add it to nms core."
        else:
            result['message'] = "Device doesn't exist."

        return Response(result)


class DeleteDeviceFromNMS(APIView):
    """
    Delete device from nms core.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/delete_device_from_nms/10244/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            pk (unicode): Device ID.

        Returns:
            result (dict): Dictionary of device info.
                           For e.g,
                             {
                                 'message': 'Devicedeletedsuccessfully',
                                 'data': {
                                 },
                                 'success': 1
                             }

        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Device deletion failed."
        result['data']['meta'] = ''

        # Device object.
        device = None
        try:
            device = Device.objects.get(id=pk)
        except Exception as e:
            pass

        if device:
            if device.host_state != "Disable":
                result['success'] = 1
                result['message'] = "Device disabled and deleted Successfully."

                # Set 'is_added_to_nms' to 1 after device successfully added to nocout nms core.
                device.is_added_to_nms = 0

                # Set 'is_monitored_on_nms' to 1 if service is added successfully.
                device.is_monitored_on_nms = 0

                # Set device state to 'Disable'.
                device.host_state = "Disable"
                device.save()

                # Remove device services from 'service_deviceserviceconfiguration' table.
                DeviceServiceConfiguration.objects.filter(device_name=device.device_name).delete()

                # Remove device ping service from 'service_devicepingconfiguration' table.
                DevicePingConfiguration.objects.filter(device_name=device.device_name).delete()

                # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
                try:
                    device.site_instance.is_device_change = 1
                    device.site_instance.save()
                except Exception as e:
                    pass
            else:
                result['message'] = "<i class=\"fa fa-times red-dot\"></i> Device state is disabled. \
                                     First enable it than add it to nms core."
        else:
            result['message'] = "Device doesn't exist."

        return Response(result)


class ModifyDeviceState(APIView):
    """
    Enable or disable device state.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/modify_device_state/11341/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            pk (unicode): Device ID.

        Returns:
            result (dict): Dictionary of device info.
                           For e.g.,
                             {
                                 'message': 'Device state modified successfully.',
                                 'success': 1
                             }

        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Device state modifictaion failed."
        result['data']['meta'] = ''

        # Device object.
        device = None
        try:
            device = Device.objects.get(pk=pk)
        except Exception as e:
            pass

        if device:
            result['success'] = 1
            result['message'] = "Device state modified successfully."

            # Revert current device state.
            if device.host_state == "Enable":
                device.host_state = "Disable"
            else:
                device.host_state = "Enable"

            device.save()

            # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
            try:
                device.site_instance.is_device_change = 1
                device.site_instance.save()
            except Exception as e:
                pass
        else:
            result['message'] = "<i class=\"fa fa-times red-dot\"></i> Device state modification failed."

        return Response(result)


class SyncDevicesInNMS(APIView):
    """
    Sync devices configuration with nms core.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/sync_devices_in_nms/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Returns:
            result (dict): Dictionary of device info.
                        For e.g.,
                             {
                                'message': 'Configpushedtomysite,nocout_gis_slave',
                                'data': {
                                    'mode': 'sync'
                                },
                                'success': 1
                             }

        Note:
            Sync status bits are as following:
            0 => Pending
            1 => Success
            2 => Failed
            3 => Deadlock Removal
            4 => Table(device_device_devicesynchistory) has no entry
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Device activation for monitoring failed."
        result['data']['meta'] = ''

        timestamp = time.time()
        fulltime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S')

        # Get last status bit of 'DeviceSyncHistory'.
        try:
            last_sync_obj = DeviceSyncHistory.objects.latest('id')
            # Last sync status.
            last_syn_status = last_sync_obj.status
        except Exception as e:
            last_syn_status = 4
            logger.error("DeviceSyncHistory table has no entry.")

        # Sync status bits are as following:
        #     0 => Pending
        #     1 => Success
        #     2 => Failed
        #     3 => Deadlock Removal
        #     4 => Table(device_device_devicesynchistory) has no entry
        if last_syn_status in [1, 2, 3, 4]:
            # Current user's username.
            username = request.user.username
            # Create entry in 'device_devicesynchistory' table.
            device_sync_history = DeviceSyncHistory()
            device_sync_history.status = 0
            device_sync_history.description = "Sync run at {}.".format(fulltime)
            device_sync_history.sync_by = username
            device_sync_history.save()

            # Get 'device sync history' object.
            sync_obj_id = device_sync_history.id

            device_data = {
                'mode': 'sync',
                'sync_obj_id': sync_obj_id
            }

            # Site to which configuration needs to be pushed.
            master_site = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME'])

            # URL for nocout.py.
            url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                    master_site.password,
                                                                    master_site.machine.machine_ip,
                                                                    master_site.web_service_port,
                                                                    master_site.name)

            # Sending post request to device app for syncing configuration to associated sites.
            r = requests.post(url, data=device_data)

            try:
                # Converting raw string 'r' into dictionary.
                response_dict = ast.literal_eval(r.text)
                if r:
                    result['data'] = device_data
                    result['success'] = 1
                    result['message'] = response_dict['message'].capitalize()
            except Exception as e:
                device_sync_history.status = 2
                device_sync_history.description = "Sync failed to run at {}.".format(fulltime)
                device_sync_history.completed_on = datetime.now()
                device_sync_history.save()
                result['message'] = "Failed to sync device and services."
                logger.info(r.text)
        else:
            result['message'] = "Someone is already running sync."

        return Response(result)


class RemoveSyncDeadlock(APIView):
    """
    Remove deadlock created in sync history table.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/remove_sync_deadlock/"
    """

    def get(self, request):
        """
        Processing API request.

        Returns:
            result (dict): Dictionary of device info.
                           For e.g.,
                                {
                                    "result": {
                                        "message": "Successfully removed sync deadlock.",
                                        "data": {
                                            "meta": ""
                                        },
                                        "success": 1
                                    }
                                }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Deadlock removal for sync failed."
        result['data']['meta'] = ''

        # Get last id of 'DeviceSyncHistory'.
        try:
            # Get a formatted timestamp.
            timestamp = time.time()
            fulltime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S')
            # Updating last device sync history object.
            last_sync_obj = DeviceSyncHistory.objects.latest('id')
            # Modify status of last 'sync' to 3 i.e. 'Deadlock'.
            last_sync_obj.status = 3
            last_sync_obj.description = "Deadlock created during this sync, removed at {}.".format(fulltime)
            last_sync_obj.save()
            result['success'] = 1
            result['message'] = "Successfully removed sync deadlock."
        except Exception as e:
            logger.error("DeviceSyncHistory table has no entry. Exception: ", e.message)

        return Response(result)


class EditSingleServiceDisplayData(APIView):
    """
    Edit single service for a device from nms core.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/edit_single_svc_display_data/"
    """

    def get(self, request, dsc_id):
        """
        Processing API request.

        Args:
            dsc_id (unicode): Device service configuration ID.

        Returns:
            result (dict): Dictionary of device service info.
                           For e.g.,
                                {
                                    'message': '',
                                    'data': {
                                        'meta': {

                                        },
                                        'objects': {
                                            'current_template': u'radwin_snmp_v1_222',
                                            'templates': [
                                                {
                                                    'value': u'radwin_snmp_v1_224',
                                                    'key': 1L
                                                },
                                                {
                                                    'value': u'radwin_snmp_v1_223',
                                                    'key': 2L
                                                }
                                            ],
                                            'data_source': u'rssi',
                                            'agent_tag': u'snmp',
                                            'version': u'v1',
                                            'read_community': u'public',
                                            'service_name': u'radwin_rssi',
                                            'device_alias': u'Device116',
                                            'dsc_id': 68,
                                            'warning': u'-50',
                                            'critical': u'-85',
                                            'retry_check_interval': 1L,
                                            'normal_check_interval': 6L,
                                            'max_check_attempts': 6L,
                                            'device_name': u'device_116',
                                            'port': 163L
                                        }
                                    },
                                    'success': 0
                                }

        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}

        # Device service configuration object.
        dsc = None
        try:
            dsc = DeviceServiceConfiguration.objects.get(id=dsc_id)
        except Exception as e:
            pass

        if dsc:
            try:
                device = Device.objects.get(device_name=dsc.device_name)
                service_data = result['data']['objects']
                service_data['dsc_id'] = dsc_id
                service_data['device_name'] = dsc.device_name
                service_data['device_alias'] = device.device_alias
                service_data['service_name'] = dsc.service_name
                service_data['current_template'] = dsc.svc_template
                service_data['normal_check_interval'] = dsc.normal_check_interval
                service_data['retry_check_interval'] = dsc.retry_check_interval
                service_data['max_check_attempts'] = dsc.max_check_attempts
                service_data['data_source'] = dsc.data_source
                service_data['warning'] = dsc.warning
                service_data['critical'] = dsc.critical
                service_data['agent_tag'] = dsc.agent_tag
                service_data['version'] = dsc.version
                service_data['read_community'] = dsc.read_community
                service_data['port'] = dsc.port
                service_data['templates'] = []
                service_templates = ServiceParameters.objects.all()
                for svc_template in service_templates:
                    temp_dict = dict()
                    temp_dict['key'] = svc_template.id
                    temp_dict['value'] = svc_template.parameter_description
                    service_data['templates'].append(temp_dict)
            except Exception as e:
                logger.info(e)
        else:
            result['message'] = "Device service configuration doesn't exist."

        return Response(result)


class GetServiceParaTableData(APIView):
    """
    Get service parameters and data source tables for service edit form.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_svc_para_table_data/10582/radwin_uas/4/"
    """

    def get(self, request, device_name, service_name, template_id=""):
        """
        Processing API request.

        Args:
            device_name (unicode): Device name.
            service_name (unicode): Service name.

        Kwargs:
            template_id (unicode): Template ID.

        Returns:
            result (str): Result dictionary.
                         For e.g.,
                                {
                                    "message": "",
                                    "data": {
                                        "objects": {},
                                        "data_sources": [],
                                        "retry_check_interval": 1,
                                        "meta": {},
                                        "normal_check_interval": 5,
                                        "max_check_attempts": 1
                                    },
                                    "success": 0
                                }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}

        if template_id:
            svc_template = None
            try:
                svc_template = ServiceParameters.objects.get(id=template_id)
            except Exception as e:
                pass

            result['data']['normal_check_interval'] = svc_template.normal_check_interval
            result['data']['retry_check_interval'] = svc_template.retry_check_interval
            result['data']['max_check_attempts'] = svc_template.max_check_attempts

            result['data']['data_sources'] = list()

            for sds in DeviceServiceConfiguration.objects.filter(device_name=device_name, service_name=service_name):
                ds_dict = dict()
                ds_dict['ds_name'] = sds.data_source
                ds_dict['warning'] = sds.warning
                ds_dict['critical'] = sds.critical

                result['data']['data_sources'].append()
        else:
            result['message'] = "No data to show."

        return Response(result)


class EditSingleService(APIView):
    """
    Edit single service corresponding to a device.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/edit_single_service/1/4/?data_sources={}"
    """

    def get(self, request, dsc_id, svc_temp_id):
        """
        Processing API request.

        Args:
            dsc_id (unicode): Device service configuration ID.
            svc_temp_id (unicode): Service template ID.
            data_sources (list): List of data sources dictionaries.
                                 For e.g.,
                                    [
                                        {
                                            'data_source': u'rssi',
                                            'warning': u'-50',
                                            'critical': u'-85'
                                        }
                                    ]

        Returns:
            result (dict): Dictionary containing service information.
                           For e.g.,
                                {
                                    "snmp_community": {
                                        "read_community": "public",
                                        "version": "v2c"
                                    },
                                    "agent_tag": "snmp",
                                    "service_name": "radwin_rssi",
                                    "snmp_port": 161,
                                    "serv_params": {
                                        "normal_check_interval": 5,
                                        "max_check_attempts": 5,
                                        "retry_check_interval": 5
                                    },
                                    "device_name": "radwin",
                                    "mode": "editservice",
                                    "cmd_params": {
                                        "rssi": {
                                            "warning": "-50",
                                            "critical": "-80"
                                        }
                                    }
                                }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}

        # Data sources.
        data_sources = None
        try:
            data_sources = eval(self.request.GET.get('data_sources'))
        except Exception as e:
            pass

        # Device service configuration object.
        dsc = ""
        try:
            dsc = DeviceServiceConfiguration.objects.get(id=dsc_id)
            try:
                # Payload data for post request.
                service_data = result['data']['objects']
                service_para = ServiceParameters.objects.get(pk=svc_temp_id)
                service_data['mode'] = "editservice"
                service_data['device_name'] = str(dsc.device_name)
                service_data['service_name'] = str(dsc.service_name)
                service_data['serv_params'] = {}
                service_data['serv_params']['normal_check_interval'] = int(service_para.normal_check_interval)
                service_data['serv_params']['retry_check_interval'] = int(service_para.retry_check_interval)
                service_data['serv_params']['max_check_attempts'] = int(service_para.max_check_attempts)
                service_data['snmp_community'] = {}
                service_data['snmp_community']['version'] = str(service_para.protocol.version)
                service_data['snmp_community']['read_community'] = str(service_para.protocol.read_community)
                service_data['cmd_params'] = {}

                # Looping through data sources add them to 'cmd_params' dictionary.
                for sds in data_sources:
                    service_data['cmd_params'][str(sds['data_source'])] = {'warning': str(sds['warning']),
                                                                           'critical': str(sds['critical'])}

                service_data['snmp_port'] = str(dsc.port)
                service_data['agent_tag'] = str(dsc.agent_tag) if eval(dsc.agent_tag) is not None else "snmp"

                # Master site on which service needs to be added.
                master_site = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME'])
                # URL for nocout.py.
                url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                        master_site.password,
                                                                        master_site.machine.machine_ip,
                                                                        master_site.web_service_port,
                                                                        master_site.name)
                # Encode payload data.
                encoded_data = urllib.urlencode(service_data)

                # Sending post request to nocout device app to add service.
                r = requests.post(url, data=encoded_data)

                # Converting post response data into python dictionary.
                response_dict = ast.literal_eval(r.text)

                # If response(r) is given by post request than process it further to get success/failure messages.
                if r:
                    result['data'] = service_data
                    result['success'] = 1

                    # If response_dict doesn't have key 'success'.
                    if not response_dict.get('success'):
                        logger.info(response_dict.get('error_message'))
                        result['message'] += "<i class=\"fa fa-times red-dot\"></i>\
                                              Failed to updated service '%s'. <br />" % dsc.service_name
                    else:
                        result[
                            'message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                           Successfully updated service '%s'. <br />" % dsc.service_name

                        # Saving service to 'service_deviceserviceconfiguration' table.
                        try:
                            # If service exist in 'service_deviceserviceconfiguration' table then update it.
                            for data_source in data_sources:
                                dsc_obj = DeviceServiceConfiguration.objects.get(device_name=dsc.device_name,
                                                                                 service_name=dsc.service_name,
                                                                                 data_source=data_source['data_source'])
                                dsc_obj.agent_tag = str(dsc.agent_tag)
                                dsc_obj.port = str(service_para.protocol.port)
                                dsc_obj.version = str(service_para.protocol.version)
                                dsc_obj.read_community = str(service_para.protocol.read_community)
                                dsc_obj.svc_template = str(service_para.parameter_description)
                                dsc_obj.normal_check_interval = int(service_para.normal_check_interval)
                                dsc_obj.retry_check_interval = int(service_para.retry_check_interval)
                                dsc_obj.max_check_attempts = int(service_para.max_check_attempts)
                                dsc_obj.warning = data_source['warning']
                                dsc_obj.critical = data_source['critical']
                                dsc_obj.save()
                        except Exception as e:
                            logger.info(e)
            except Exception as e:
                logger.info(e)
                result['message'] = "Failed to updated service '%s'. <br />" % dsc.service_name
        except Exception as e:
            logger.info(e)
            result['message'] = "Failed to updated service '%s'. <br />" % dsc.service_name

        return Response(result)


class DeleteSingleServiceDisplayData(APIView):
    """
    Get parameters for single service deletion form.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/delete_single_svc_display_data/1/"
    """

    def get(self, request, dsc_id):
        """
        Processing API request.

        Args:
            dsc_id (unicode): Device service configuration object ID.

        Returns:
            result (dict): Dictionary containing service information.
                           For e.g.,
                                {
                                    'message': '',
                                    'data': {
                                        'meta': {

                                        },
                                        'objects': {
                                            'service_name': u'radwin_rssi',
                                            'data_sources': [
                                                u'rssi'
                                            ],
                                            'device_alias': u'Device116',
                                            'service_alias': u'Receivedsignalstrength',
                                            'device_name': u'device_116'
                                        }
                                    },
                                    'success': 0
                                }
        """
        # Device service configuration object.
        dsc = DeviceServiceConfiguration.objects.get(id=dsc_id)

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}

        try:
            service_data = result['data']['objects']
            service_data['service_name'] = dsc.service_name
            service_data['service_alias'] = Service.objects.get(name=str(dsc.service_name)).alias
            service_data['device_name'] = dsc.device_name
            service_data['device_alias'] = Device.objects.get(device_name=str(dsc.device_name)).device_alias
            service_data['data_sources'] = []
            try:
                # Fetch data sources from 'DeviceServiceConfiguration' model.
                dsc_for_data_sources = DeviceServiceConfiguration.objects.filter(device_name=dsc.device_name,
                                                                                 service_name=dsc.service_name)
                for dsc_for_data_source in dsc_for_data_sources:
                    service_data['data_sources'].append(dsc_for_data_source.data_source)
            except Exception as e:
                logger.info(e)
        except Exception as e:
            logger.info(e)

        return Response(result)


class DeleteSingleService(APIView):
    """
    Delete service corresponding to the device.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/delete_single_svc/1/"n
    """

    def get(self, request, device_name, service_name):
        """
        Processing API request.

        Args:
            device_name (unicode): Device name.
            service_name (unicode): Service name.

        Returns:
            result (dict): Dictionary containing service information.
                           For e.g.,
                                {
                                    'message': '',
                                    'data': {
                                        'meta': {

                                        },
                                        'objects': {
                                            'service_name': u'radwin_rssi',
                                            'data_sources': [
                                                u'rssi'
                                            ],
                                            'device_alias': u'Device116',
                                            'service_alias': u'Receivedsignalstrength',
                                            'device_name': u'device_116'
                                        }
                                    },
                                    'success': 0
                                }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}

        try:
            service_data = {
                'mode': 'deleteservice',
                'device_name': str(device_name),
                'service_name': str(service_name)
            }

            master_site = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME'])
            # URL for nocout.py.
            url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                    master_site.password,
                                                                    master_site.machine.machine_ip,
                                                                    master_site.web_service_port,
                                                                    master_site.name)

            # Encode service payload data.
            encoded_data = urllib.urlencode(service_data)

            # Sending post request to nocout device app to add a service.
            r = requests.post(url, data=encoded_data)

            # Converting post response data into python dictionary.
            response_dict = ast.literal_eval(r.text)

            # If response(r) is given by post request than process it further to get success/failure messages.
            if r:
                result['data'] = service_data
                result['success'] = 1

                # If response dictionary doesn't have key 'success'.
                if not response_dict.get('success'):
                    logger.info(response_dict.get('error_message'))
                    result['message'] += "<i class=\"fa fa-times red-dot\"></i>\
                                          Failed to delete service '%s'. <br />" % service_name
                else:
                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                          Successfully updated service '%s'. <br />" % service_name

                # Delete service rows form 'service_deviceserviceconfiguration' table.
                DeviceServiceConfiguration.objects.filter(device_name=device_name, service_name=service_name).delete()
        except Exception as e:
            result['message'] += e.message

        return Response(result)


class EditServiceDisplayData(APIView):
    """
    Service parameters to display on form.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/edit_svc_display_data/12452/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            value (unicode): Device ID.

        Returns:
            result (dict): Dictionary containing service information.
                           For e.g,
                                {
                                    'message': 'Successfully render form.',
                                    'data': {
                                        'meta': '',
                                        'objects': {
                                            'master_site': u'master_UA',
                                            'device_alias': u'Device116',
                                            'is_added': 1L,
                                            'services': [
                                                {
                                                    'value': u'ODUserialnumber',
                                                    'key': 14L
                                                }
                                            ],
                                            'device_name': u'device_116',
                                            'device_id': 545
                                        }
                                    },
                                    'success': 0
                                }
        """
        # Device object.
        device = Device.objects.get(id=pk)

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to render form correctly."
        result['data']['meta'] = ''
        result['data']['objects'] = {}
        result['data']['objects']['device_id'] = pk
        result['data']['objects']['device_name'] = device.device_name
        result['data']['objects']['device_alias'] = device.device_alias
        result['data']['objects']['services'] = []
        result['data']['objects']['master_site'] = ""
        result['data']['objects']['is_added'] = device.is_added_to_nms

        # Get device type.
        device_type = None
        try:
            device_type = DeviceType.objects.get(id=device.device_type)
        except Exception as e:
            pass

        # Get all services associated with the devic type.
        dt_services = None
        try:
            dt_services = device_type.service.all()
        except Exception as e:
            pass

        # Get deleted services.
        del_svc = list()
        try:
            del_svc = list(set(DeviceServiceConfiguration.objects.filter(
                device_name=device.device_name, operation="d").values_list('service_name', flat=True)))
        except Exception as e:
            pass

        # Get monitored services except in deletion queue.
        editable_svc = dt_services.exclude(name__in=del_svc)

        # Get services associated with device.
        try:
            try:
                master_site_name = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME']).name
                result['data']['objects']['master_site'] = master_site_name
            except Exception as e:
                logger.info("Master site doesn't exist.")

            if device.is_added_to_nms == 1:
                result['data']['objects']['services'] = []
                for svc in editable_svc:
                    service = Service.objects.get(name=svc)
                    svc_dict = dict()
                    svc_dict['key'] = service.id
                    svc_dict['value'] = service.alias
                    result['data']['objects']['services'].append(svc_dict)
            else:
                result['message'] = "First add device in nms core."
        except Exception as e:
            logger.info("No service to monitor.")

        return Response(result)


class ServiceEditOldConf(APIView):
    """
    Show currently present information of service in schema.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/svc_edit_old_conf/4/12/10585/"
    """

    def get(self, request, service_id="", device_id=""):
        """
        Processing API request.

        Args:
            option (unicode): Checkbox value.
            service_id (unicode): Service ID.
            device_id (unicode): Device ID.

        Returns:
            dajax (str): Dictionary containing service old configuration.
                         For e.g.,
                             {
                                "message": "",
                                "data": {
                                    "objects": {},
                                    "retry_check_interval": 1,
                                    "svc_param": [
                                        {
                                            "parameter_description": "radwin_snmp_performance_5_min",
                                            "id": 4
                                        },
                                        {
                                            "parameter_description": "radwin_snmp_performance_10_min",
                                            "id": 5
                                        },
                                        {
                                            "parameter_description": "radwin_snmp_status_60_min",
                                            "id": 6
                                        },
                                        {
                                            "parameter_description": "radwin_snmp_inventory_1_day",
                                            "id": 7
                                        },
                                        {
                                            "parameter_description": "cambium_snmp_inventory_1_day",
                                            "id": 8
                                        },
                                        {
                                            "parameter_description": "cambium_snmp_performance_5_min",
                                            "id": 9
                                        }
                                    ],
                                    "meta": {},
                                    "normal_check_interval": 60,
                                    "max_check_attempts": 1,
                                    "old_conf": [
                                        {
                                            "data_source": "1",
                                            "warning": "",
                                            "critical": ""
                                        }
                                    ]
                                },
                                "success": 0
                            }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data'] = {}

        # Get device.
        device = None
        try:
            device = Device.objects.get(pk=device_id)
        except Exception as e:
            pass

        # Get service.
        service = None
        try:
            service = Service.objects.get(pk=service_id)
        except Exception as e:
            pass

        # Get service template.
        svc_template = None
        try:
            svc_template = service.parameters
        except Exception as e:
            pass

        # Get service data sources.
        svc_data_sources = None
        try:
            svc_data_sources = service.service_data_sources.all()
        except Exception as e:
            pass

        if service_id and service_id != "":
            svc_params = ServiceParameters.objects.all()
            if svc_params:
                try:
                    if svc_params:
                        # Get device service configuration.
                        dsc = DeviceServiceConfiguration.objects.filter(
                            device_name=device.device_name,
                            service_name=service.name).exclude(operation="d")

                        if dsc:
                            svc_template = dsc[0]
                            svc_data_sources = dsc

                        result['data']['normal_check_interval'] = svc_template.normal_check_interval
                        result['data']['retry_check_interval'] = svc_template.retry_check_interval
                        result['data']['max_check_attempts'] = svc_template.max_check_attempts
                        result['data']['old_conf'] = list()

                        # Set show templates or not bit.
                        show_svc_templates = True

                        if svc_data_sources:
                            for sds in svc_data_sources:
                                ds_dict = dict()
                                if dsc:
                                    data_source = sds.data_source
                                else:
                                    data_source = sds.name
                                try:
                                    ds_dict['data_source'] = data_source
                                    ds_dict['warning'] = sds.warning
                                    ds_dict['critical'] = sds.critical
                                    result['data']['old_conf'].append(ds_dict)
                                    result['success'] = 1
                                    result['message'] = "Successfully fetched service old configuration."
                                except Exception as e:
                                    show_svc_templates = False

                            if show_svc_templates:
                                result['data']['svc_param'] = list()
                                for svc_param in svc_params:
                                    svc_param_dict = dict()
                                    svc_param_dict['id'] = svc_param.id
                                    svc_param_dict['parameter_description'] = svc_param.parameter_description
                                    result['data']['svc_param'].append(svc_param_dict)
                                    result['success'] = 1
                                    result['message'] = "Successfully fetched service old configuration."
                            else:
                                result['message'] = "Data source parameters are not editable."
                    else:
                        result['message'] = "No data source associated."
                        result['success'] = 0
                except Exception as e:
                    logger.info("No data source available.")
        else:
            result['message'] = "No data source associated."
            result['success'] = 0

        return Response(result)


class ServiceEditNewConf(APIView):
    """
    Show modified information of the service.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/svc_edit_new_conf/4/12/"
    """

    def get(self, request, service_id="", template_id=""):
        """
        Processing API request.

        Args:
            service_id (unicode): Service ID.
            template_id (unicode): Template ID.

        Returns:
            dajax (str): Dictionary containing modified configuration of service.
                         For e.g.,
                            {
                                "message": "",
                                "data": {
                                    "objects": {},
                                    "data_sources": [
                                        {
                                            "ds_name": "color_code",
                                            "warning": "",
                                            "critical": ""
                                        }
                                    ],
                                    "retry_check_interval": 1,
                                    "meta": {},
                                    "normal_check_interval": 5,
                                    "max_check_attempts": 1
                                },
                                "success": 0
                            }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}

        # Get service.
        service = None
        try:
            service = Service.objects.get(id=service_id)
        except Exception as e:
            pass

        # Get template.
        template = None
        try:
            template = ServiceParameters.objects.get(pk=template_id)
        except Exception as e:
            pass

        # Get data sources.
        data_sources = None
        try:
            data_sources = service.service_data_sources.all()
        except Exception as e:
            pass

        result['data']['normal_check_interval'] = template.normal_check_interval
        result['data']['retry_check_interval'] = template.retry_check_interval
        result['data']['max_check_attempts'] = template.max_check_attempts
        result['data']['data_sources'] = list()

        for sds in data_sources:
            ds_dict = dict()
            ds_dict['ds_name'] = sds.name
            ds_dict['warning'] = sds.warning
            ds_dict['critical'] = sds.critical
            result['data']['data_sources'].append(ds_dict)

        return Response(result)


class ServiceEditPingConf(APIView):
    """
    Show ping information of the service.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/svc_edit_ping_conf/10585/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            device_id (unicode): Device ID.

        Returns:
            dajax (str): Dictionary containing ping service configuration.
                         For e.g.,
                            {
                                "message": "",
                                "data": {
                                    "rta_critical": 3000,
                                    "objects": {},
                                    "packets": 60,
                                    "meta": {},
                                    "timeout": 20,
                                    "pl_critical": 100,
                                    "normal_check_interval": 5,
                                    "pl_warning": 80,
                                    "rta_warning": 1500
                                },
                                "success": 0
                            }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data'] = {}

        # Get device.
        device = Device.objects.get(pk=pk)

        try:
            # Get device ping configuration object.
            dpc = DevicePingConfiguration.objects.get(device_name=device.device_name)
            packets = dpc.packets
            timeout = dpc.timeout
            normal_check_interval = dpc.normal_check_interval
            rta_warning = dpc.rta_warning
            rta_critical = dpc.rta_critical
            pl_warning = dpc.pl_warning
            pl_critical = dpc.pl_critical
        except Exception as e:
            # If there are no ping parmeters for this device in 'service_devicepingconfiguration'
            # then get default ping parameters from 'settings.py".
            packets = settings.PING_PACKETS
            timeout = settings.PING_TIMEOUT
            normal_check_interval = settings.PING_NORMAL_CHECK_INTERVAL
            rta_warning = settings.PING_RTA_WARNING
            rta_critical = settings.PING_RTA_CRITICAL
            pl_warning = settings.PING_PL_WARNING
            pl_critical = settings.PING_PL_CRITICAL
            logger.info(e.message)

        result['success'] = 1
        result['message'] = 'Ping configuration fetched successfully.'
        result['data']['packets'] = packets
        result['data']['timeout'] = timeout
        result['data']['normal_check_interval'] = normal_check_interval
        result['data']['rta_warning'] = rta_warning
        result['data']['rta_critical'] = rta_critical
        result['data']['pl_warning'] = pl_warning
        result['data']['pl_critical'] = pl_critical

        return Response(result)


class EditServices(APIView):
    """
    Edit services corresponding to the device.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/edit_services/11343/?svc_data=[{'service_id': u'54', 'data_source': [{
         'warning': u'15', 'critical': u'19', 'name': u'dl_cinr'}], 'template_id': u'9'}, {'service_id': u'55',
         'data_source': [{'warning': u'15', 'critical': u'19', 'name': u'ul_cinr'}], 'template_id': u'13'}]
         &svc_ping={'rta_critical': 3000, 'packets': 60, 'timeout': 20, 'pl_critical': 100, 'normal_check_interval': 5,
         'pl_warning': 80, 'rta_warning': 1500}"
    """

    def get(self, request, device_id=""):
        """
        Processing API request.

        Args:
            device_id (unicode): Device ID.
            svc_data (list): List of dictionaries containing service data.
                             For e.g.,
                                [
                                    {
                                        'service_id': u'1',
                                        'data_source': [
                                            {
                                                'warning': u'-50',
                                                'critical': u'-85',
                                                'name': u'rssi'
                                            }
                                        ],
                                        'template_id': u'2',
                                        'device_id': u'545'
                                    },
                                    {
                                        'service_id': u'13',
                                        'data_source': [
                                            {
                                                'warning': u'',
                                                'critical': u'',
                                                'name': u'idu_sn'
                                            }
                                        ],
                                        'template_id': u'3',
                                        'device_id': u'545'
                                    }
                                ]

            svc_ping (dict): Dictionary containing ping data.
                             For e.g.,
                                 {
                                    'rta_critical': 3000,
                                    'packets': 60,
                                    'timeout': 20,
                                    'pl_critical': 100,
                                    'normal_check_interval': 5,
                                    'pl_warning': 80,
                                    'rta_warning': 1500
                                }

        Returns:
            result (dict): Dictionary containing service information.
                           For e.g.,
                                {
                                    "message": "<i class=\"fa fa-check green-dot\"></i>Successfully edited service
                                               'ping'. <br /><i class=\"fa fa-check green-dot\"></i>Successfully edited
                                                service 'wimax_dl_cinr'. <br /><i class=\"fa fa-check green-dot\"></i>
                                                Successfully edited service 'wimax_ul_cinr'. <br />",
                                    "data": {
                                        "svc_ping": {
                                            "rta_critical": 3000,
                                            "packets": 60,
                                            "timeout": 20,
                                            "pl_critical": 100,
                                            "normal_check_interval": 5,
                                            "pl_warning": 80,
                                            "rta_warning": 1500
                                        },
                                        "svc_data": [
                                            {
                                                "service_id": "54",
                                                "data_source": [
                                                    {
                                                        "warning": "15",
                                                        "critical": "19",
                                                        "name": "dl_cinr"
                                                    }
                                                ],
                                                "template_id": "9"
                                            },
                                            {
                                                "service_id": "55",
                                                "data_source": [
                                                    {
                                                        "warning": "15",
                                                        "critical": "19",
                                                        "name": "ul_cinr"
                                                    }
                                                ],
                                                "template_id": "13"
                                            }
                                        ]
                                    },
                                    "success": 0
                                }

        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}

        # Service configuration data.
        svc_data = eval(self.request.GET.get('svc_data', None))

        # Service ping configuration.
        svc_ping = eval(self.request.GET.get('svc_ping', None))

        # Collects messages returned from service addition api.
        messages = ""

        # Get device.
        device = None
        try:
            device = Device.objects.get(id=device_id)
        except Exception as e:
            pass

        # Edit 'ping' service.
        try:
            if device and svc_ping:
                device_name = device.device_name

                # Get device ping configuration object.
                dpc = ""
                try:
                    dpc = DevicePingConfiguration.objects.get(device_name=device_name)
                except Exception as e:
                    logger.info(e.message)

                if dpc:
                    try:
                        # Device ping configuration.
                        dpc.device_name = device_name
                        dpc.device_alias = device.device_alias
                        dpc.packets = svc_ping['packets']
                        dpc.timeout = svc_ping['timeout']
                        dpc.normal_check_interval = svc_ping['normal_check_interval']
                        dpc.rta_warning = svc_ping['rta_warning']
                        dpc.rta_critical = svc_ping['rta_critical']
                        dpc.pl_warning = svc_ping['pl_warning']
                        dpc.pl_critical = svc_ping['pl_critical']
                        dpc.operation = "e"
                        dpc.save()

                        # Set site instance bit corresponding to the device.
                        device.site_instance.is_device_change = 1
                        device.site_instance.save()

                        result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                               Successfully edited service 'ping'. <br />"
                        messages += result['message']
                    except Exception as e:
                        result['message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to edit service ping. <br />"
                        messages += result['message']
                else:
                    # Device ping configuration.
                    try:
                        dpc = DevicePingConfiguration()
                        dpc.device_name = device_name
                        dpc.device_alias = device.device_alias
                        dpc.packets = svc_ping['packets']
                        dpc.timeout = svc_ping['timeout']
                        dpc.normal_check_interval = svc_ping['normal_check_interval']
                        dpc.rta_warning = svc_ping['rta_warning']
                        dpc.rta_critical = svc_ping['rta_critical']
                        dpc.pl_warning = svc_ping['pl_warning']
                        dpc.pl_critical = svc_ping['pl_critical']
                        dpc.operation = "c"
                        dpc.save()

                        # Set site instance bit corresponding to the device.
                        device.site_instance.is_device_change = 1
                        device.site_instance.save()

                        result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                               Successfully created service 'ping'. <br />"
                        messages += result['message']
                    except Exception as e:
                        result[
                            'message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to create service ping. <br />"
                        messages += result['message']
        except Exception as e:
            logger.info(e.message)
            result['message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to edit/create service 'ping'. <br />"
            messages += result['message']

        # Edit other services.
        for sd in svc_data:
            result = dict()
            result['data'] = {}
            result['success'] = 0
            result['message'] = ""

            # Get service.
            service = None
            try:
                service = Service.objects.get(pk=int(sd['service_id']))
            except Exception as e:
                pass

            # Get service parameters.
            service_para = service.parameters
            try:
                service_para = ServiceParameters.objects.get(pk=int(sd['template_id']))
            except Exception as e:
                logger.info(e)

            try:
                for sds in sd['data_source']:
                    if sds['warning'] != "":
                        try:
                            # If service exist in 'service_deviceserviceconfiguration' table
                            # then update service, else create it.
                            for data_source in sd['data_source']:
                                dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                                                service_name=service.name,
                                                                                data_source=data_source['name'])
                                if dsc:
                                    dsc = dsc[0]
                                    dsc.agent_tag = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
                                    dsc.port = str(service_para.protocol.port)
                                    dsc.version = str(service_para.protocol.version)
                                    dsc.read_community = str(service_para.protocol.read_community)
                                    dsc.svc_template = str(service_para.parameter_description)
                                    dsc.normal_check_interval = int(service_para.normal_check_interval)
                                    dsc.retry_check_interval = int(service_para.retry_check_interval)
                                    dsc.max_check_attempts = int(service_para.max_check_attempts)
                                    if data_source['warning'] != "":
                                        dsc.warning = int(data_source['warning'])
                                    if data_source['critical'] != "":
                                        dsc.critical = int(data_source['critical'])
                                    dsc.is_added = 0
                                    dsc.operation = "e"
                                    dsc.save()

                                    # Set site instance bit corresponding to the device.
                                    device.site_instance.is_device_change = 1
                                    device.site_instance.save()

                                    # Set 'is_monitored_on_nms' to 1 if service is added successfully.
                                    device.is_monitored_on_nms = 1
                                    device.save()

                                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                                           Successfully edited service '%s'. <br />" % service.name
                                    messages += result['message']
                                else:
                                    dsc = DeviceServiceConfiguration()
                                    dsc.device_name = device.device_name
                                    dsc.service_name = service.name
                                    dsc.data_source = data_source['name']
                                    dsc.agent_tag = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
                                    dsc.port = str(service_para.protocol.port)
                                    dsc.version = str(service_para.protocol.version)
                                    dsc.read_community = str(service_para.protocol.read_community)
                                    dsc.svc_template = str(service_para.parameter_description)
                                    dsc.normal_check_interval = int(service_para.normal_check_interval)
                                    dsc.retry_check_interval = int(service_para.retry_check_interval)
                                    dsc.max_check_attempts = int(service_para.max_check_attempts)
                                    if data_source['warning'] != "":
                                        dsc.warning = int(data_source['warning'])
                                    if data_source['critical'] != "":
                                        dsc.critical = int(data_source['critical'])
                                    dsc.is_added = 0
                                    dsc.operation = "c"
                                    dsc.save()

                                    # Set site instance bit corresponding to the device.
                                    device.site_instance.is_device_change = 1
                                    device.site_instance.save()

                                    # Set 'is_monitored_on_nms' to 1 if service is added successfully.
                                    device.is_monitored_on_nms = 1
                                    device.save()

                                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                                           Successfully created service '%s'. <br />" % service.name
                                    messages += result['message']

                        except Exception as e:
                            logger.exception(e)
                    else:
                        # Save service to 'service_deviceserviceconfiguration' table.
                        try:
                            # If service exist in 'service_deviceserviceconfiguration' table
                            # then update service, else create it.
                            for data_source in sd['data_source']:
                                dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                                                service_name=service.name,
                                                                                data_source=data_source['name'])
                                if dsc:
                                    dsc = dsc[0]
                                    dsc.agent_tag = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
                                    dsc.port = str(service_para.protocol.port)
                                    dsc.version = str(service_para.protocol.version)
                                    dsc.read_community = str(service_para.protocol.read_community)
                                    dsc.svc_template = str(service_para.parameter_description)
                                    dsc.normal_check_interval = int(service_para.normal_check_interval)
                                    dsc.retry_check_interval = int(service_para.retry_check_interval)
                                    dsc.max_check_attempts = int(service_para.max_check_attempts)
                                    dsc.warning = int(data_source['warning']) if data_source['warning'] else ""
                                    dsc.critical = int(data_source['critical']) if data_source['critical'] else ""
                                    dsc.is_added = 1
                                    dsc.operation = "e"
                                    dsc.save()

                                    # Set site instance bit corresponding to the device.
                                    device.site_instance.is_device_change = 1
                                    device.site_instance.save()

                                    # Set 'is_monitored_on_nms' to 1 if service is added successfully.
                                    device.is_monitored_on_nms = 1
                                    device.save()

                                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                                           Successfully edited service '%s'. <br />" % service.name
                                    messages += result['message']
                                else:
                                    dsc = DeviceServiceConfiguration()
                                    dsc.device_name = device.device_name
                                    dsc.service_name = service.name
                                    dsc.data_source = data_source['name']
                                    dsc.agent_tag = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
                                    dsc.port = str(service_para.protocol.port)
                                    dsc.version = str(service_para.protocol.version)
                                    dsc.read_community = str(service_para.protocol.read_community)
                                    dsc.svc_template = str(service_para.parameter_description)
                                    dsc.normal_check_interval = int(service_para.normal_check_interval)
                                    dsc.retry_check_interval = int(service_para.retry_check_interval)
                                    dsc.max_check_attempts = int(service_para.max_check_attempts)
                                    dsc.warning = int(data_source['warning']) if data_source['warning'] else ""
                                    dsc.critical = int(data_source['critical']) if data_source['critical'] else ""
                                    dsc.is_added = 1
                                    dsc.operation = "c"
                                    dsc.save()

                                    # Set 'is_monitored_on_nms' to 1 if service is added successfully.
                                    device.is_monitored_on_nms = 1
                                    device.save()

                                    # Set site instance bit corresponding to the device.
                                    device.site_instance.is_device_change = 1
                                    device.site_instance.save()

                                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                                           Successfully created service '%s'. <br />" % service.name
                                    messages += result['message']
                        except Exception as e:
                            logger.exception(e)
            except Exception as e:
                logger.exception(e)
                result['message'] += "<i class=\"fa fa-times red-dot\"></i>\
                                       Failed to edit service '%s'. <br />" % service.name
                messages += result['message']

        # Assign messages to result dict message key.
        if messages:
            result['message'] = messages
        else:
            result['message'] = "No template is selected for any service"

        result['data']['svc_data'] = svc_data
        result['data']['svc_ping'] = svc_ping

        return Response(result)


class DeleteServiceDisplayData(APIView):
    """
    Get parameters for service deletion form.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/delete_svc_display_data/11343/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            pk (int): Device ID.

        Returns:
            result (dict): Dictionary containing services information.
                           For e.g.,
                                {
                                    "message": "Successfully render data.",
                                    "data": {
                                        "meta": "",
                                        "objects": {
                                            "master_site": "master_UA",
                                            "device_alias": "1131208803",
                                            "is_added": 1,
                                            "services": [
                                                {
                                                    "value": "downlink cinr",
                                                    "key": 54
                                                },
                                                {
                                                    "value": "uplink cinr",
                                                    "key": 55
                                                },
                                                {
                                                    "value": "downlink intrf",
                                                    "key": 56
                                                },
                                                {
                                                    "value": "uplink intrf",
                                                    "key": 57
                                                },
                                                {
                                                    "value": "uplink rssi",
                                                    "key": 59
                                                }
                                            ],
                                            "device_name": "11343",
                                            "device_id": "11343"
                                        }
                                    },
                                    "success": 0
                                }
        """
        # Device to which services are associated.
        device = Device.objects.get(id=pk)

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to render form correctly."
        result['data']['meta'] = ''
        result['data']['objects'] = {}
        result['data']['objects']['device_id'] = pk
        result['data']['objects']['device_name'] = device.device_name
        result['data']['objects']['device_alias'] = device.device_alias
        result['data']['objects']['services'] = []
        result['data']['objects']['master_site'] = ""
        result['data']['objects']['is_added'] = device.is_added_to_nms

        # Get device type.
        device_type = DeviceType.objects.get(id=device.device_type)

        # Get all services associated with the device type.
        dt_services = device_type.service.all()

        # Get services associated with the device.
        try:
            try:
                master_site_name = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME']).name
                result['data']['objects']['master_site'] = master_site_name
            except Exception as e:
                logger.info("Master site doesn't exist.")
            if device.is_added_to_nms == 1:
                # Fetching all services those were already deleted from 'service device configuration' table.
                dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name, operation='d')

                # Services those are already running for this device.
                services = []
                for svc in dsc:
                    services.append(svc.service_name)

                # Extracting unique set of services from 'services' list.
                monitored_services = dt_services.exclude(name__in=list((set(services))))

                result['data']['objects']['services'] = []

                for svc in monitored_services:
                    svc_dict = dict()
                    svc_dict['key'] = svc.id
                    svc_dict['value'] = svc.alias
                    result['data']['objects']['services'].append(svc_dict)
                    result['message'] = "Successfully render data."
            else:
                result['message'] = "First add device in nms core."
        except Exception as e:
            logger.info("No service to monitor.")
            logger.info(e.message)

        return Response(result)


class DeleteServices(APIView):
    """
    Delete services corresponding to the device.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/delete_services/11343/?service_data=["57","59","60"]"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            pk (unicode): Device ID.
            service_data (list): List of dictionaries containing service data.
                                 For e.g.,
                                     [u'54', u'55', u'56']

        Returns:
            result (dict):  Dictionary containing deleted services information.
                            For e.g.,
                                {
                                    "message": "<i class=\"fa fa-check green-dot\"></i>Successfully deleted service
                                               'wimax_ul_intrf'. <br /><i class=\"fa fa-check green-dot\"></i>
                                                Successfully deleted service 'wimax_ul_rssi'. <br />
                                                <i class=\"fa fa-check green-dot\"></i>Successfully deleted service
                                                'wimax_dl_modulation_change_invent'. <br />",
                                    "data": {},
                                    "success": 1
                                }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""

        # Get device.
        device = None
        try:
            device = Device.objects.get(id=pk)
        except Exception as e:
            pass

        # Services list.
        service_data = eval(self.request.GET.get('service_data', None))

        # Get agent tag.
        agent_tag = "snmp"
        try:
            agent_tag = DeviceType.objects.get(id=device.device_type).agent_tag
        except Exception as e:
            pass

        # Collects messages returned from service addition api.
        messages = ""

        for svc_id in service_data:
            result['message'] = ""

            try:
                # Get service.
                service = Service.objects.get(pk=svc_id)

                # Delete services corresponding to the device.
                result['success'] = 1

                # If response dict doesn't have key 'success'.
                if device:
                    # Create entry in 'device service configuration'.
                    dsc = DeviceServiceConfiguration()
                    dsc.device_name = device.device_name
                    dsc.service_name = service.name
                    dsc.agent_tag = agent_tag
                    dsc.operation = "d"
                    dsc.save()

                    # Delete service rows from 'service_deviceserviceconfiguration' table.
                    DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                              service_name=service.name,
                                                              operation__in=["c", "e"]).delete()

                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                          Successfully deleted service '%s'. <br />" % service.name
                    messages += result['message']
                else:
                    result['message'] += "<i class=\"fa fa-times red-dot\"></i>\
                                          Failed to delete service '%s'. <br />" % service.name
                    messages += result['message']
            except Exception as e:
                result['message'] += e.message

        result['message'] = messages

        return Response(result)


class AddServiceDisplayData(APIView):
    """
    Show form for adding services corresponding to the device.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/add_svc_display_data/11343/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            pk (int): Device ID.

        Returns:
            result (dict): Dictionary containing services information.
                           For e.g.,
                                {
                                    "message": "Successfully render form data.",
                                    "data": {
                                        "meta": "",
                                        "objects": {
                                            "master_site": "master_UA",
                                            "device_alias": "1131208803",
                                            "is_added": 1,
                                            "services": [
                                                {
                                                    "value": "downlink cinr",
                                                    "key": 54
                                                },
                                                {
                                                    "value": "uplink cinr",
                                                    "key": 55
                                                },
                                                {
                                                    "value": "downlink intrf",
                                                    "key": 56
                                                },
                                                {
                                                    "value": "uplink intrf",
                                                    "key": 57
                                                },
                                                {
                                                    "value": "uplink rssi",
                                                    "key": 59
                                                },
                                                {
                                                    "value": "dl_modulation_change",
                                                    "key": 60
                                                }
                                            ],
                                            "device_name": "11343",
                                            "device_id": "11343"
                                        }
                                    },
                                    "success": 0
                                }
        """
        # Device to which services are associated.
        device = Device.objects.get(id=pk)

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to render form correctly."
        result['data']['meta'] = ''
        result['data']['objects'] = {}
        result['data']['objects']['device_id'] = pk
        result['data']['objects']['device_name'] = device.device_name
        result['data']['objects']['device_alias'] = device.device_alias
        result['data']['objects']['services'] = []
        result['data']['objects']['master_site'] = ""
        result['data']['objects']['is_added'] = device.is_added_to_nms

        # Get services associated with device.
        try:
            try:
                master_site_name = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME']).name
                result['data']['objects']['master_site'] = master_site_name
            except Exception as e:
                logger.info(e.message)

            if device.is_added_to_nms == 1:
                # Fetching all services from 'service device configuration' table.
                deleted_services = DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                                             operation="d").values_list('service_name',
                                                                                                        flat=True)

                # Filter duplicate service entries from 'deleted_services' list.
                deleted_services = list(set(deleted_services))

                # Get services those can be added (i.e. services already deleted).
                services = Service.objects.filter(name__in=deleted_services)

                result['data']['objects']['services'] = []

                for svc in services:
                    svc_dict = dict()
                    svc_dict['key'] = svc.id
                    svc_dict['value'] = svc.alias
                    result['data']['objects']['services'].append(svc_dict)
                result['message'] = "Successfully render form data."
            else:
                result['message'] = "First add device in nms core."
        except Exception as e:
            logger.info("No service to monitor.")
            logger.info(e.message)

        return Response(result)


class ServiceAddOldConf(APIView):
    """
    Show current information of service present in schema.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/svc_add_old_conf/11343/14/4/"
    """

    def get(self, request, device_id="", service_id="", option=""):
        """
        Processing API request.

        Args:
            device_id (unicode): Device ID.
            service_id (unicode): Service ID.
            option (unicode): Checkbox value.

        Returns:
            result (dict): Dictionary containing service data.
                         For e.g.,
                            {
                                "message": "<h5 class='text-red'>Fetched data successfully.</h5> ",
                                "data": {
                                    "meta": {},
                                    "objects": {
                                        "svc_param": [
                                            {
                                                "parameter_description": "radwin_snmp_performance_5_min",
                                                "id": 4
                                            },
                                            {
                                                "parameter_description": "radwin_snmp_performance_10_min",
                                                "id": 5
                                            },
                                            {
                                                "parameter_description": "radwin_snmp_status_60_min",
                                                "id": 6
                                            },
                                            {
                                                "parameter_description": "radwin_snmp_inventory_1_day",
                                                "id": 7
                                            },
                                            {
                                                "parameter_description": "cambium_snmp_inventory_1_day",
                                                "id": 8
                                            }
                                        ],
                                        "option": "4"
                                    }
                                },
                                "success": 0
                            }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to fetch data."
        result['data']['meta'] = {}
        result['data']['objects'] = {}
        result['data']['objects']['svc_param'] = list()

        if service_id and service_id != "":
            svc_params = ServiceParameters.objects.all()
            if svc_params:
                try:
                    result['data']['objects']['option'] = service_id

                    for svc_param in svc_params:
                        param_dict = dict()
                        param_dict['id'] = svc_param.id
                        param_dict['parameter_description'] = svc_param.parameter_description
                        result['data']['objects']['svc_param'].append(param_dict)
                    result['success'] = 1
                    result['message'] = "<h5 class='text-red'>Fetched data successfully.</h5> "
                except Exception as e:
                    logger.info("No data source available.")
                    logger.info(e.message)
            else:
                result['message'] = "<h5 class='text-red'>No data source associated.</h5>"
        else:
            pass

        return Response(result)


class ServiceAddNewConf(APIView):
    """
    Show modified information of service.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/svc_add_new_conf/14/4/"
    """

    def get(self, request, service_id="", template_id=""):
        """
        Processing API request.

        Args:
            service_id (unicode): Service ID.
            template_id (unicode): Template ID.

        Returns:
            result (dict): Dictionary containing service data.
                         For e.g.,
                            {
                                "message": "Successfully fetched data.",
                                "data": {
                                    "meta": {},
                                    "objects": {
                                        "service_id": "14",
                                        "max_check_attempts": 1,
                                        "normal_check_interval": 5,
                                        "retry_check_interval": 1,
                                        "data_sources": [
                                            {
                                                "state": "Editable.",
                                                "warning": "",
                                                "critical": "",
                                                "name": "odu_sn"
                                            }
                                        ]
                                    }
                                },
                                "success": 0
                            }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to fetch data."
        result['data']['meta'] = {}
        result['data']['objects'] = {}
        result['data']['objects']['data_sources'] = list()
        result['data']['objects']['service_id'] = service_id

        service = Service.objects.get(pk=service_id)
        template = ServiceParameters.objects.get(pk=template_id)

        result['data']['objects']['normal_check_interval'] = template.normal_check_interval
        result['data']['objects']['retry_check_interval'] = template.retry_check_interval
        result['data']['objects']['max_check_attempts'] = template.max_check_attempts

        # Data sources associated with the service.
        data_sources = service.service_data_sources.all()

        for sds in data_sources:
            ds_dict = dict()
            try:
                ds_dict['name'] = sds.name
                ds_dict['title'] = 'Editable.'
                ds_dict['state'] = 'true'
                ds_dict['warning'] = sds.warning
                ds_dict['critical'] = sds.critical
                result['data']['objects']['data_sources'].append(ds_dict)
            except Exception as e:
                ds_dict['name'] = sds.name
                ds_dict['title'] = 'Non editable.'
                ds_dict['state'] = 'false'
                ds_dict['warning'] = sds.warning
                ds_dict['critical'] = sds.critical
                result['data']['objects']['data_sources'].append(ds_dict)

        if result['data']['objects']['data_sources']:
            result['message'] = "Successfully fetched data."

        return Response(result)


class AddServices(APIView):
    """
    Adding services corresponding to the device.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/add_services/11343/?svc_data=[{'service_id': u'54',
         'data_source': [{'warning': u'15', 'critical': u'19', 'name': u'dl_cinr'}], 'template_id': u'9'}]"
    """

    def get(self, request, device_id):
        """
        Processing API request.

        Args:
            device_id (unicode): Device ID.
            svc_data (list): List of dictionaries containing service data.
                             For e.g.,
                                    [
                                        {
                                            'service_id': u'1',
                                            'data_source': [
                                                {
                                                    'warning': u'-50',
                                                    'critical': u'-85',
                                                    'name': u'rssi'
                                                }
                                            ],
                                            'template_id': u'2',
                                            'device_id': u'545'
                                        },
                                        {
                                            'service_id': u'13',
                                            'data_source': [
                                                {
                                                    'warning': u'',
                                                    'critical': u'',
                                                    'name': u'idu_sn'
                                                }
                                            ],
                                            'template_id': u'3',
                                            'device_id': u'545'
                                        }
                                    ]

        Returns:
            result (dict): Dictionary containing services information.
                           For e.g.,
                                {
                                    'message': u"Successfully edited service 'radwin_rssi'. <br />
                                                 Successfully edited service 'radwin_idu_sn_invent'. <br />",
                                    'data': {
                                        'snmp_community': {
                                            'read_community': 'public',
                                            'version': 'v1'
                                        },
                                        'service_name': 'radwin_idu_sn_invent',
                                        'serv_params': {
                                            'normal_check_interval': 5,
                                            'max_check_attempts': 5,
                                            'retry_check_interval': 1
                                        },
                                        'device_name': 'device_116',
                                        'mode': 'editservice',
                                        'cmd_params': {

                                        }
                                    },
                                    'success': 1
                                }

        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}

        svc_data = eval(self.request.GET.get('svc_data', None))

        # Get device.
        device = None
        try:
            device = Device.objects.get(id=device_id)
        except Exception as e:
            pass

        # Get device name.
        device_name = ""
        if device:
            device_name = device.device_name

        # Collects messages returned from service addition api.
        messages = ""

        for sd in svc_data:
            # Reset message value.
            result['message'] = ""

            try:
                service = Service.objects.get(pk=int(sd['service_id']))

                # If service template is not selected than default will be considered.
                try:
                    service_para = ServiceParameters.objects.get(pk=int(sd['template_id']))
                except Exception as e:
                    service_para = service.parameters
                    logger.info(e.message)

                # List of data sources.
                data_sources = []
                try:
                    if 'data_source' in sd:
                        for sds in sd['data_source']:
                            temp_dict = dict()
                            temp_dict['name'] = str(sds['name']) if sds['name'] != "" else ""
                            temp_dict['warning'] = str(sds['warning']) if sds['warning'] != "" else ""
                            temp_dict['critical'] = str(sds['critical']) if sds['critical'] != "" else ""
                            data_sources.append(temp_dict)
                    else:
                        for sds in service.service_data_sources.all():
                            temp_dict = dict()
                            temp_dict['name'] = str(sds.name) if sds.name != "" else ""
                            temp_dict['warning'] = str(sds.warning) if sds.warning != "" else ""
                            temp_dict['critical'] = str(sds.critical) if sds.critical != "" else ""
                            data_sources.append(temp_dict)
                except Exception as e:
                    logger.info(e.message)

                result['success'] = 1

                try:
                    # Delete entry corresponding to this service with operation 'd'.
                    # Because we can only add services those were already deleted
                    # and which has operation bit set to 'd' (for deleted).
                    DeviceServiceConfiguration.objects.filter(device_name=device_name,
                                                              service_name=service.name,
                                                              operation="d").delete()

                    # Add service in 'service_deviceserviceconfiguration' table.
                    for data_source in data_sources:
                        dsc = DeviceServiceConfiguration()
                        dsc.device_name = device.device_name
                        dsc.service_name = service.name
                        dsc.agent_tag = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
                        dsc.port = str(service_para.protocol.port)
                        dsc.version = str(service_para.protocol.version)
                        dsc.read_community = str(service_para.protocol.read_community)
                        dsc.svc_template = str(service_para.parameter_description)
                        dsc.normal_check_interval = int(service_para.normal_check_interval)
                        dsc.retry_check_interval = int(service_para.retry_check_interval)
                        dsc.max_check_attempts = int(service_para.max_check_attempts)
                        dsc.data_source = data_source['name']
                        dsc.warning = data_source['warning']
                        dsc.critical = data_source['critical']
                        dsc.operation = "c"
                        dsc.is_added = 0
                        dsc.save()

                        result['message'] += "<i class=\"fa fa-check green-dot\"></i> \
                                               Successfully added service '%s'. <br />" % service.name

                        messages += result['message']
                except Exception as e:
                    result['message'] += "<i class=\"fa fa-check green-dot\"></i> \
                                           Failed to add service '%s'. <br />" % service.name
                    messages += result['message']

                # Set 'is_monitored_on_nms' to 1 if service is added successfully.
                device.is_monitored_on_nms = 1
                device.save()

                # Set site instance bit corresponding to the device.
                device.site_instance.is_device_change = 1
                device.site_instance.save()
            except Exception as e:
                logger.info(e)
                result['message'] += "<i class=\"fa fa-times red-dot\"></i> Something wrong with the form data. <br />"
                messages += result['message']

        # Assign messages to result dict message key.
        result['message'] = messages

        return Response(result)


class DeviceServiceStatus(APIView):
    """
    Show current configuration/status of services corresponding to the device.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/device_service_status/11343/"
    """

    def get(self, request, pk):
        """
        Processing API request.

        Args:
            pk (unicode): Device ID.

        Returns:
            result (dict): Dictionary of device and associated services information.
                           For e.g.,
                                {
                                    'message': '',
                                    'data': {
                                        'meta': {

                                        },
                                        'objects': {
                                            'site_instance': 'nocout_gis_slave',
                                            'inactive_services': [
                                                {
                                                    'service': u'Receivedsignalstrength',
                                                    'data_sources': 'Receivedsignalstrength,
                                                    '
                                                },
                                                {
                                                    'service': u'totaluplinkutilization',
                                                    'data_sources': 'Management_Port_on_Odu,
                                                    Radio_Interface,
                                                    '
                                                },
                                                {
                                                    'service': u'channelbandwidth',
                                                    'data_sources': 'channelbandwidth,
                                                    '
                                                },
                                                {
                                                    'service': u'portspeedstatus',
                                                    'data_sources': 'ethernet_port_1,
                                                    ethernet_port_2,
                                                    ethernet_port_3,
                                                    ethernet_port_4,
                                                    '
                                                },
                                                {
                                                    'service': u'IDUserialnumber',
                                                    'data_sources': 'IDUserialnumber,
                                                    '
                                                },
                                                {
                                                    'service': u'totaluptime',
                                                    'data_sources': 'totaluptime,
                                                    '
                                                },
                                                {
                                                    'service': u'portautonegotiationstatus',
                                                    'data_sources': 'ethernet_port_1,
                                                    ethernet_port_2,
                                                    ethernet_port_3,
                                                    ethernet_port_4,
                                                    '
                                                }
                                            ],
                                            'active_services': [

                                            ],
                                            'device_name': '115.112.95.187',
                                            'machine': 'default',
                                            'device_type': 'Radwin2KBS',
                                            'ip_address': '115.112.95.187'
                                        }
                                    },
                                    'success': 1
                                }

        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}

        # Get device.
        device = Device.objects.get(pk=pk)

        # Fetching all services from 'service device configuration' table.
        dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name)

        # Get device type.
        device_type = DeviceType.objects.get(id=device.device_type)

        # Get deleted services.
        deleted_services_list = dsc.filter(operation="d").values_list("service_name", flat=True)
        deleted_services = Service.objects.filter(name__in=list(set(deleted_services_list)))

        # Get active services.
        active_services = device_type.service.all().exclude(name__in=deleted_services_list)

        result['data']['objects']['device_name'] = str(device.device_alias)
        result['data']['objects']['machine'] = str(device.machine)
        result['data']['objects']['site_instance'] = str(device.site_instance)
        result['data']['objects']['ip_address'] = str(device.ip_address)
        result['data']['objects']['device_type'] = str(DeviceType.objects.get(pk=device.device_type))
        result['data']['objects']['active_services'] = []
        result['data']['objects']['inactive_services'] = []

        for svc in active_services:
            temp_svc = dict()
            temp_svc['service'] = svc.alias
            temp_svc['data_sources'] = ""
            for ds in svc.service_data_sources.all():
                temp_svc['data_sources'] += "{}, ".format(ds.alias)
            result['data']['objects']['active_services'].append(temp_svc)

        for svc in deleted_services:
            temp_svc = dict()
            temp_svc['service'] = svc.alias
            temp_svc['data_sources'] = ""
            for ds in svc.service_data_sources.all():
                temp_svc['data_sources'] += "{}, ".format(ds.alias)
            result['data']['objects']['inactive_services'].append(temp_svc)

        return Response(result)


class ResetServiceConfiguration(APIView):
    """
    Reset device service configuration.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/reset_service_conf/"
    """

    def get(self, request):
        """
        Processing API request.

        Returns:
            result (dict): Dictionary containing device information.
                           For e.g.,
                                {
                                    "message": "Successfully reset device service configuration.",
                                    "data": {
                                        "meta": ""
                                    },
                                    "success": 1
                                }
        """
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to reset device service configuration."
        result['data']['meta'] = ''

        # Get last id of 'DeviceSyncHistory'.
        try:
            # Get all devices list from 'service_devicepingconfiguration'.
            ping_devices = DevicePingConfiguration.objects.all().values_list('device_name', flat=True)

            # Get list of sites associated with 'ping_devices'.
            ping_sites = Device.objects.filter(device_name__in=list(set(ping_devices))).values_list('site_instance__id',
                                                                                                    flat=True)

            # Get all devices list from 'service_deviceserviceconfiguration'.
            svc_devices = DeviceServiceConfiguration.objects.all().values_list('device_name', flat=True)

            # Get list of sites associated with 'svc_devices'.
            svc_sites = Device.objects.filter(device_name__in=list(set(svc_devices))).values_list('site_instance__id',
                                                                                                  flat=True)

            # Effected sites.
            effected_sites = set(list(ping_sites) + list(svc_sites))

            # Set 'is_device_change' bit of corresponding sites.
            SiteInstance.objects.filter(id__in=effected_sites).update(is_device_change=1)

            # Truncate 'service_deviceserviceconfiguration'.
            DeviceServiceConfiguration.objects.all().delete()

            # Truncate 'service_devicepingconfiguration'.
            DevicePingConfiguration.objects.all().delete()

            result['success'] = 1
            result['message'] = "Successfully reset device service configuration."

        except Exception as e:
            logger.info(e.message)

        return Response(result)


class GetDataSourceforDisplayType(APIView):
    """
    Fetch type corresponding to the selected technology.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_tech_types/4/"
    """

    def get(self, request):
        search = self.request.GET.get('search', None)
        plot_type = self.request.GET.get('display_type', None)

        # Response of api.
        result = list()

        # Fetch data_sources associated with the selected type and search text.
        if search:
            if plot_type == "table":
                data_sources = ServiceDataSource.objects.filter(
                    Q(alias__icontains=search)
                    &
                    Q(chart_type="table")).order_by('alias')
            else:
                data_sources = ServiceDataSource.objects.filter(
                    Q(alias__icontains=search)
                    &
                    (~Q(chart_type="table")&Q(data_source_type=1))).order_by('alias')
        else:
             data_sources = ServiceDataSource.objects.filter( Q(chart_type = "table")if plot_type == "table" else
                                                              (~Q(chart_type="table")&Q(data_source_type=1))).order_by('alias')

        for value in data_sources:
            services= value.service_set.all()
            for service in services:
                if '_invent' not in service.name and '_status' not in service.name:
                    result.append({
                        'id': str(value.id) + '_' + str(service.id),
                        'text': value.alias + " - "+ str(service.alias),
                        'name' : value.name
                    })


        return Response(result)

