import logging
from inventory.models import BaseStation, Customer, Antenna
from device.models import DeviceType, DeviceVendor, DeviceTechnology, City
from random import randint, uniform
import datetime
from nocout.settings import DEBUG
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
from django.core.urlresolvers import reverse

logger = logging.getLogger(__name__)

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()

def tech_marker_url(device_type, techno, ms=True):
    """

    :param techno: technology P2P,
    :return: technology markers
    """
    try:
        dt = DeviceType.objects.get(id = device_type)
        if len(str(dt.device_gmap_icon)) > 5:
            img_url = str("media/"+ str(dt.device_gmap_icon)) \
                if "uploaded" in str(dt.device_gmap_icon) \
                else "static/img/" + str(dt.device_gmap_icon)
            return img_url
        else:
            return "static/img/icons/mobilephonetower10.png"

    except:
        return tech_marker_url_main(techno, ms)


def tech_marker_url_main(techno, main=True):
    """

    :param techno: technology P2P,
    :return: technology markers
    """
    if main:
        if techno == "P2P":
            return "static/img/icons/mobilephonetower1.png"
        elif techno == "PMP":
            return "static/img/icons/mobilephonetower2.png"
        elif techno == "WiMAX":
            return "static/img/icons/mobilephonetower3.png"
        else:
            return "static/img/marker/icon2_small.png"
    else:
        return tech_marker_url_subordinate(techno)


def tech_marker_url_subordinate(techno):
    """

    :param techno: technology P2P,
    :return: technology markers
    """
    if techno == "P2P":
        return "static/img/icons/wifi1.png"
    elif techno == "PMP":
        return "static/img/icons/wifi2.png"
    elif techno == "WiMAX":
        return "static/img/icons/wifi3.png"
    else:
        return "static/img/marker/icon4_small.png"


def prepare_raw_basestation(base_station=None):
    """

    :param base_station: base-station dictionary object
    :return: base-station information
    """
    if base_station:
        base_station_info = [
            {
                'name': 'base_station_alias',
                'title': 'Base-Station Name',
                'show': 1,
                'value': unicode(nocout_utils.format_value(base_station['BSALIAS']))+"|"
            },
            {
                'name': 'bs_site_id',
                'title': 'BS Site Name',
                'show': 1,
                'value': unicode(nocout_utils.format_value(base_station['BSSITEID']))+"|"
            },
            {
                'name': 'building_height',
                'title': 'Building Height',
                'show': 1,
                'value': unicode(nocout_utils.format_value(base_station['BSBUILDINGHGT']))+"|"
                
            },
            {
                'name': 'tower_height',
                'title': 'Tower Height',
                'show': 1,
                'value': unicode(nocout_utils.format_value(base_station['BSTOWERHEIGHT']))+"|"
            },
            {
                'name':'bs_type',
                'title':'BS Type',
                'show':1,
                'value': unicode(nocout_utils.format_value(base_station['BSSITETYPE']))+"|"
            },
            {
                'name': 'bs_gps_type',
                'title': 'GPS Type',
                'show': 1,
                'value': unicode(nocout_utils.format_value(base_station['BSGPSTYPE']))+"|"
            },
            {
                'name': 'bs_address',
                'title': 'Address',
                'show': 1,
                'value': unicode(nocout_utils.format_value(base_station['BSADDRESS']))+"|"
            },
            {
                'name': 'bs_city',
                'title': 'City',
                'show': 1,
                'value': unicode(nocout_utils.format_value(base_station['BSCITY']))+"|"
            },
            {
                'name': 'bs_state',
                'title': 'State',
                'show': 1,
                'value': unicode(nocout_utils.format_value(base_station['BSSTATE']))+"|"
            },
            {
                'name': 'lat_lon',
                'title': 'Lat, Long',
                'show':1,
                'value': unicode(nocout_utils.format_value(base_station['BSLAT']))+","+unicode(nocout_utils.format_value(base_station['BSLONG']))+"|"
            },
            {
                'name': 'bs_infra_provider',
                'title': 'Infra Provider',
                'show': 1,
                'value': unicode(nocout_utils.format_value(base_station['BSINFRAPROVIDER']))+"|"
            },
            {
                'name':'tag1',
                'title':'Tag1',
                'show':1,
                'value': unicode(nocout_utils.format_value(base_station['BSTAG1']))+"|"
            },
            {
                'name':'tag2',
                'title':'Tag2',
                'show':1,
                'value': unicode(nocout_utils.format_value(base_station['BSTAG2']))+"|"
            }
        ]
        return base_station_info
    return []


def prepare_raw_backhaul(backhaul):
    """

    :param backhaul:
    :return:
    """

    backhaul_info = []
    backhaul_list = []

    if backhaul:
        # for backhaul in backhaul:
        if backhaul['BHID']:
            backhaul_info = [
                {
                    'name': 'bh_capacity',
                    'title': 'BH Capacity',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BH_CAPACITY']))+"|"
                },
                {
                    'name': 'bh_connectivity',
                    'title': 'BH Connectivity',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BH_CONNECTIVITY']))+"|"
                },
                {
                    'name': 'bh_type',
                    'title': 'BH Type',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BH_TYPE']))+"|"
                },
                {
                    'name': 'bh_circuit_id',
                    'title': 'BH Circuit ID',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BH_CIRCUIT_ID']))+"|"
                },
                {
                    'name': 'bh_ttsl_circuit_id',
                    'title': 'BSO Circuit ID',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BH_TTSL_CIRCUIT_ID']))+"|"
                },
                {
                    'name': 'bh_pe_hostname',
                    'title': 'PE Hostname',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BH_PE_HOSTNAME']))+"|"
                },
                {
                    'name': 'pe_ip',
                    'title': 'PE IP',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BH_PE_IP']))+"|"
                },
                {
                    'name':'bs_switch_ip',
                    'title':'BS Switch IP',
                    'show':1,
                    'value': unicode(nocout_utils.format_value(backhaul['BSSWITCH']))+"|"
                },
                {
                    'name': 'aggregation_switch',
                    'title': 'Aggregation Switch',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['AGGR_IP']))+"|"
                },
                {
                    'name': 'aggregation_switch_port',
                    'title': 'Aggregation Switch Port',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BH_AGGR_PORT']))+"|"
                },
                {
                    'name': 'bs_converter_ip',
                    'title': 'BS Converter IP',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BSCONV_IP']))+"|"
                },
                {
                    'name': 'pop',
                    'title': 'POP IP',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['POP_IP']))+"|"
                },
                {
                    'name':'bh_device_type',
                    'title':'Converter Type',
                    'show':1,
                    'value': unicode(nocout_utils.format_value(backhaul['BHTYPE']))+"|"
                },
                {
                    'name': 'bh_configured_on',
                    'title': 'BH Configured On',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BHCONF_IP']))+"|"
                },
                {
                    'name': 'bh_device_port',
                    'title': 'SW/Con Port',
                    'show': 1,
                    'value': unicode(nocout_utils.format_value(backhaul['BH_DEVICE_PORT']))+"|"
                }
            ]

    return backhaul_info

def pivot_element(bs_result, pivot_key):
    """

    :param bs_result:
    :return:
    """

    sector_dict = dict()
    if bs_result:
        #preparing result by pivoting via basestation id
        for sector in bs_result:
            if sector[pivot_key]:
                sid = sector[pivot_key]
                if sid not in sector_dict:
                    sector_dict[sid] = []
                sector_dict[sid].append(sector)
    return sector_dict



def prepare_raw_sector(sectors=None,with_data=False):
    """

    :param sector:
    :return:
    """

    sector_info = []
    sector_list = []

    sector_ss_vendor = []
    sector_ss_technology = []
    sector_ss_type = []
    sector_configured_on_devices = []
    sector_planned_frequencies = []
    circuit_ids = []
    sectors_info_list = []

    ##### Sector Tooltip Variables Start
    all_sector_cktid = ""
    all_sector_customer_alias = ""
    all_sector_idu_ip = ""
    all_sector_pe_ip = ""
    all_sector_qos_bandwidth = ""
    all_sector_hssu_used = ""
    all_sector_hssu_port = ""
    all_sector_bh_bso = ""
    all_sector_antenna_height = ""
    all_sector_antenna_polarization = ""
    all_sector_mount_type = ""
    all_sector_cable_length = ""
    all_sector_ethernet_extender = ""
    all_sector_building_height = ""
    all_sector_tower_height = ""
    all_sector_technology = ""
    all_sector_type = ""
    all_sector_lat_lon = ""
    all_sector_customer_address = ""
    all_sector_sector_alias = ""
    all_sector_dl_rssi_during_acceptance = ""
    all_sector_date_of_acceptance = ""
    all_sector_sector_id = ""
    all_sector_frequency = ""
    all_sector_ugps_installed = ""
    all_sector_tx_power_planned = ""
    all_sector_rx_power_planned = ""
    all_sector_antenna_azimuth = ""
    all_sector_antenna_make = ""
    all_sector_sync_splitter = ""
    all_sector_pmp_port = ""
    all_sector_dr_status = ""
    all_sector_mrc_status = ""
    all_sector_antenna_tilt = ""
    all_sector_antenna_splitter_installed = ""
    all_sector_frame_length = ""
    ##### Sector Tooltip Variables End
    counter = 0
    if sectors:
        for sector_id in sectors:
            if sector_id not in sector_list:
                sector_list.append(sector_id)
                sector = sectors[sector_id][0]

                #prepare sector vendor list
                sector_ss_vendor.append(nocout_utils.format_value(format_this=sector['SECTOR_VENDOR']))
                #prepare Sector technology list
                techno_to_append = nocout_utils.format_value(format_this=sector['SECTOR_TECH'])
                #prepare Sector type list
                type_to_append = nocout_utils.format_value(format_this=sector['SECTOR_TYPE'])
                if sector['CIRCUIT_TYPE'] and sector['CIRCUIT_TYPE'].lower() in ['backhaul', 'bh']:
                    techno_to_append = 'PTP BH'
                sector_ss_technology.append(techno_to_append)
                sector_ss_type.append(type_to_append)
                #prepare BH technology list
                # sector_ss_technology.append(nocout_utils.format_value(format_this=sector['BHTECH']))
                #prepare sector configured on device
                sector_configured_on_devices.append(nocout_utils.format_value(format_this=sector['SECTOR_CONF_ON_IP']))
                #prepare BH configured on device
                # sector_configured_on_devices.append(nocout_utils.format_value(format_this=sector['BHCONF_IP']))

                circuit_dict = pivot_element(sectors[sector_id], 'CCID')

                #circuit id prepare ?
                substation, circuit_id, substation_ip, subStationsInfo  = prepare_raw_ss_result(
                    circuits=circuit_dict,
                    sector_id=sector_id,
                    frequency_color=nocout_utils.format_value(format_this=sector['SECTOR_FREQUENCY_COLOR'],type_of='frequency_color'),
                    frequency=nocout_utils.format_value(format_this=sector['SECTOR_FREQUENCY']),
                    with_data=with_data
                )

                near_end_perf_url = ""
                near_end_inventory_url = ""
                page_type = 'customer'
                # Check for technology to make perf page url
                if techno_to_append.lower() in ['pmp', 'wimax', 'ptp bh']:
                    page_type = 'network'

                near_end_perf_url = reverse(
                    'SingleDevicePerf',
                    kwargs={
                        'page_type': page_type, 
                        'device_id': sector['SECTOR_CONF_ON_ID']
                    },
                    current_app='performance'
                )

                # Sector Device Inventory URL
                near_end_inventory_url = reverse(
                    'device_edit',
                    kwargs={
                        'pk': sector['SECTOR_CONF_ON_ID']
                    },
                    current_app='device'
                )

                circuit_ids += circuit_id
                sector_configured_on_devices += substation_ip
                # Polled Frequency
                sector_planned_frequencies.append(nocout_utils.format_value(format_this=sector['SECTOR_FREQUENCY']))
                # Planned Frequency
                # sector_planned_frequencies.append(nocout_utils.format_value(format_this=sector['SECTOR_PLANNED_FREQUENCY']))

                # If with_data flag is true then send tooltip data
                if with_data:
                    ### Append Sector Infowindow Content
                    all_sector_cktid += unicode(nocout_utils.format_value(format_this=sector['CCID']))+"|"
                    all_sector_customer_alias += unicode(nocout_utils.format_value(format_this=sector['CUST']))+"|"
                    all_sector_idu_ip += unicode(nocout_utils.format_value(format_this=sector['SECTOR_CONF_ON_IP']))+"|"
                    all_sector_pe_ip += unicode(nocout_utils.format_value(format_this=sector['BH_PE_IP']))+"|"
                    all_sector_qos_bandwidth += unicode(nocout_utils.format_value(format_this=sector['QOS']))+"|"
                    all_sector_hssu_used += unicode(nocout_utils.format_value(format_this=sector['BSHSSUUSED']))+"|"
                    all_sector_hssu_port += unicode(nocout_utils.format_value(format_this=sector['BSHSSUPORT']))+"|"
                    all_sector_bh_bso += unicode(nocout_utils.format_value(format_this=sector['BSBHBSO']))+"|"
                    all_sector_antenna_height += unicode(nocout_utils.format_value(format_this=sector['SECTOR_ANTENNA_HEIGHT']))+"|"
                    all_sector_antenna_polarization += unicode(nocout_utils.format_value(format_this=sector['SECTOR_ANTENNA_POLARIZATION']))+"|"
                    all_sector_mount_type += unicode(nocout_utils.format_value(format_this=sector['SSANTENNAMOUNTTYPE']))+"|"
                    all_sector_cable_length += unicode(nocout_utils.format_value(format_this=sector['SS_CABLE_LENGTH']))+"|"
                    all_sector_ethernet_extender += unicode(nocout_utils.format_value(format_this=sector['SS_ETH_EXT']))+"|"
                    all_sector_building_height += unicode(nocout_utils.format_value(format_this=sector['BSBUILDINGHGT']))+"|"
                    all_sector_tower_height += unicode(nocout_utils.format_value(format_this=sector['BSTOWERHEIGHT']))+"|"
                    all_sector_technology += unicode(techno_to_append)+"|"
                    all_sector_type+= unicode(type_to_append)+"|"
                    all_sector_lat_lon += unicode(unicode(nocout_utils.format_value(format_this=sector['BSLAT']))+","+unicode(nocout_utils.format_value(sector['BSLONG'])))+"|"
                    all_sector_customer_address += unicode(nocout_utils.format_value(format_this=sector['SS_CUST_ADDR']))+"|"
                    all_sector_sector_alias += unicode(nocout_utils.format_value(format_this=sector['SECTOR_ALIAS']))+"|"
                    all_sector_dl_rssi_during_acceptance += unicode(nocout_utils.format_value(format_this=sector['RSSI']))+"|"
                    all_sector_date_of_acceptance += unicode(nocout_utils.format_value(format_this=sector['DATE_OF_ACCEPT']))+"|"
                    all_sector_sector_id += unicode(nocout_utils.format_value(format_this=sector['SECTOR_SECTOR_ID']))+"|"
                    all_sector_frequency += unicode(nocout_utils.format_value(format_this=sector['SECTOR_PLANNED_FREQUENCY']))+"|"
                    all_sector_ugps_installed += unicode(nocout_utils.format_value(format_this=sector['BSGPSTYPE']))+"|"
                    all_sector_tx_power_planned += unicode(nocout_utils.format_value(format_this=sector['SECTOR_TX']))+"|"
                    all_sector_rx_power_planned += unicode(nocout_utils.format_value(format_this=sector['SECTOR_RX']))+"|"
                    all_sector_antenna_azimuth += unicode(nocout_utils.format_value(format_this=sector['SECTOR_ANTENNA_AZMINUTH_ANGLE']))+"|"
                    all_sector_antenna_make += unicode(nocout_utils.format_value(format_this=sector['SECTOR_ANTENNA_MAKE']))+"|"
                    all_sector_sync_splitter += unicode(nocout_utils.format_value(format_this=sector['SECTOR_ANTENNA_SYNC_SPLITTER']))+"|"
                    all_sector_pmp_port += unicode(sector['SECTOR_PORT'])+"|"
                    all_sector_dr_status += unicode(nocout_utils.format_value(format_this=sector['SECTOR_DR']))+"|"
                    all_sector_mrc_status += unicode(nocout_utils.format_value(format_this=sector['SECTOR_MRC']))+"|"
                    all_sector_antenna_tilt += unicode(nocout_utils.format_value(format_this=sector['SECTOR_ANTENNA_TILT']))+"|"
                    all_sector_antenna_splitter_installed += unicode(nocout_utils.format_value(format_this=sector['SECTOR_ANTENNA_SPLITTER']))+"|"
                    all_sector_frame_length += unicode(nocout_utils.format_value(format_this=sector['SECTOR_FRAME_LENGTH']))+"|"

                sector_info.append({
                    "color": nocout_utils.format_value(format_this=sector['SECTOR_FREQUENCY_COLOR'],type_of='frequency_color'),
                    'radius': nocout_utils.format_value(format_this=sector['SECTOR_FREQUENCY_RADIUS'],type_of='frequency_radius'),
                    #sector.cell_radius if sector.cell_radius else 0,
                    'azimuth_angle': nocout_utils.format_value(format_this=sector['SECTOR_ANTENNA_AZMINUTH_ANGLE'],type_of='integer'),
                    'beam_width': nocout_utils.format_value(format_this=sector['SECTOR_BEAM_WIDTH'],type_of='integer'),
                    'planned_frequency': nocout_utils.format_value(format_this=sector['SECTOR_FREQUENCY']),
                    'frequency': nocout_utils.format_value(format_this=sector['SECTOR_PLANNED_FREQUENCY']),
                    # "markerUrl": tech_marker_url_main(sector.bs_technology.name) if sector.bs_technology else "static/img/marker/icon2_small.png",
                    'orientation': nocout_utils.format_value(format_this=sector['SECTOR_ANTENNA_POLARIZATION'],type_of='antenna'),
                    'technology': techno_to_append,
                    'device_type': type_to_append,
                    'vendor': nocout_utils.format_value(format_this=sector['SECTOR_VENDOR']),
                    'sector_configured_on': nocout_utils.format_value(format_this=sector['SECTOR_CONF_ON_IP']),
                    'sector_configured_on_device': nocout_utils.format_value(format_this=sector['SECTOR_CONF_ON']),
                    # 'sector_device_id' : nocout_utils.format_value(format_this=sector['SECTOR_CONF_ON_ID']),
                    'perf_page_url' : near_end_perf_url,
                    "inventory_url" : near_end_inventory_url,
                    'circuit_id':None,
                    'sector_id' : nocout_utils.format_value(format_this=sector['SECTOR_ID']),
                    'antenna_height': nocout_utils.format_value(format_this=sector['SECTOR_ANTENNA_HEIGHT'], type_of='random'),
                    "markerUrl": nocout_utils.format_value(format_this=sector['SECTOR_GMAP_ICON'], type_of='icon'),
                    'device_info':[
                        {
                            "name": "device_name",
                            "title": "Device Name",
                            "show": 0,
                            "value": nocout_utils.format_value(format_this=sector['SECTOR_CONF_ON_ALIAS'])
                        },
                        {
                            "name": "device_id",
                            "title": "Device ID",
                            "show": 0,
                            "value": nocout_utils.format_value(format_this=sector['SECTOR_CONF_ON_ID'])
                        },
                        {
                            "name": "device_mac",
                            "title": "Device MAC",
                            "show": 0,
                            "value": nocout_utils.format_value(format_this=sector['SECTOR_CONF_ON_MAC'])
                        }

                    ],
                    'info': [],
                    "item_index" : counter,
                    'ss_info_list' : subStationsInfo,
                    'sub_station': substation
                })

                # Increment counter as per the loop
                counter += 1

    # If with_data flag is true then send tooltip data
    if with_data:        
        # Sector Infowindow content
        sectors_info_list = [
            {
              'name': 'cktid',
              'title': 'Circuit ID',
              'show': 1,
              'value': all_sector_cktid
            },
            {
              'name': 'customer_alias',
              'title': 'Customer Name',
              'show': 1,
              'value': all_sector_customer_alias
            },
            {
              'name': 'idu_ip',
              'title': 'IDU IP',
              'show': 1,
              'value': all_sector_idu_ip
            },
            {
                'name': 'pe_ip',
                'title': 'PE IP',
                'show': 1,
                'value': all_sector_pe_ip
            },
            {
                'name': 'qos_bandwidth',
                'title': 'QOS(BW)',
                'show': 1,
                'value': all_sector_qos_bandwidth
            },
            {
              'name': 'hssu_used',
              'title': 'HSSU Used',
              'show': 1,
              'value': all_sector_hssu_used
            },
            {
              'name': 'hssu_port',
              'title': 'HSSU Port',
              'show': 1,
              'value': all_sector_hssu_port
            },
            {
              'name': 'bh_bso',
              'title': 'BH BSO',
              'show': 1,
              'value': all_sector_bh_bso
            },
            {
              'name': 'antenna_height',
              'title': 'Antenna Height',
              'show': 1,
              'value': all_sector_antenna_height
            },
            {
              'name': 'antenna_polarization',
              'title': 'Antenna Polarization',
              'show': 1,
              'value': all_sector_antenna_polarization
            },
            {
                'name': 'mount_type',
                'title': 'SS MountType',
                'show': 1,
                'value': all_sector_mount_type
            },
            {
                'name': 'cable_length',
                'title': 'Cable Length',
                'show': 1,
                'value': all_sector_cable_length
            },
            {
                'name': 'ethernet_extender',
                'title': 'Ethernet Extender',
                'show': 1,
                'value': all_sector_ethernet_extender
            },
            {
              'name': 'building_height',
              'title': 'Building Height',
              'show': 1,
              'value': all_sector_building_height
            },
            {
              'name': 'tower_height',
              'title': 'Tower Height',
              'show': 1,
              'value': all_sector_tower_height
            },
            {
              'name': 'technology',
              'title': 'Technology',
              'show': 1,
              'value': all_sector_technology
            },
            {
              'name': 'devicetype',
              'title': 'Device-Type',
              'show': 1,
              'value': all_sector_technology
            },
            {
                'name': 'lat_lon',
                'title': 'Lat, Long',
                'show':1,
                'value': all_sector_lat_lon
            },
            {
                'name': 'customer_address',
                'title': 'Customer Address',
                'show': 1,
                'value': all_sector_customer_address
            },
            {
              'name': 'sector_alias',
              'title': 'Alias',
              'show': 0,
              'value': all_sector_sector_alias
            },
            {
                'name': 'dl_rssi_during_acceptance',
                'title': 'RSSI During Acceptance',
                'show': 1,
                'value': all_sector_dl_rssi_during_acceptance
            },
            {
                'name': 'date_of_acceptance',
                'title': 'Date of Acceptance',
                'show': 1,
                'value': all_sector_date_of_acceptance
            },
            {
              'name': 'sector_id',
              'title': 'Sector ID',
              'show': 1,
              'value': all_sector_sector_id
            },
            {
                'name': 'frequency',
                'title': 'Planned Frequency',
                'show': 1,
                'value': all_sector_frequency
            },
            {
                'name': 'ugps_installed',
                'title': 'UGPS Installed',
                'show': 1,
                'value': all_sector_ugps_installed
            },
            {
                'name': 'tx_power_planned',
                'title': 'Tx Power Planned',
                'show': 1,
                'value': all_sector_tx_power_planned
            },
            {
                'name': 'rx_power_planned',
                'title': 'Rx Power Planned',
                'show': 1,
                'value': all_sector_rx_power_planned
            },
            {
              'name': 'antenna_azimuth',
              'title': 'Antenna Azimuth Angle',
              'show': 1,
              'value': all_sector_antenna_azimuth
            },
            {
                'name': 'antenna_make',
                'title': 'Antenna Make',
                'show': 1,
                'value': all_sector_antenna_make
            },
            {
              'name': 'sync_splitter',
              'title': 'Sync Splitter Used',
              'show': 1,
              'value': all_sector_sync_splitter
            },
            {
                'name': 'pmp_port',
                'title': 'PMP PORT',
                'show': 1,
                'value': all_sector_pmp_port
            },
            {
                'name': 'dr_status',
                'title': 'DR Status',
                'show': 1,
                'value': all_sector_dr_status
            },
            {
                'name': 'mrc_status',
                'title': 'MRC Status',
                'show': 1,
                'value': all_sector_mrc_status
            },
            {
              'name': 'antenna_tilt',
              'title': 'Antenna Tilt',
              'show': 1,
              'value': all_sector_antenna_tilt
            },
            {
              'name': 'antenna_splitter_installed',
              'title': 'Installation of Splitter',
              'show': 1,
              'value': all_sector_antenna_splitter_installed
            },
            {
              'name': 'frame_length',
              'title': 'Frame Length',
              'show': 1,
              'value': all_sector_frame_length
            }
        ]

    # Return the content
    return (
        sector_info,
        sector_ss_vendor,
        sector_ss_technology,
        sector_ss_type,
        sector_configured_on_devices,
        circuit_ids,
        sector_planned_frequencies,
        sectors_info_list
    )


def prepare_raw_ss_result(circuits, sector_id, frequency_color, frequency, with_data=False):
    """

    :param frequency:
    :param frequency_color:
    :param sector_id:
    :param basestations:
    :return:
    """
    substation_info = []
    circuit_ids = []
    substation_ip = []
    subStationsInfo = []
    
    ##### SS Tooltip Variables Start
    all_ckt_ids = ""
    all_customer_alias = ""
    all_ss_ip = ""
    all_pe_ip = ""
    all_qos_bandwidth = ""
    all_antenna_height = ""
    all_polarisation = ""
    all_mount_type = ""
    all_antenna_type = ""
    all_cable_length = ""
    all_ethernet_extender = ""
    all_building_height = ""
    all_tower_height = ""
    all_ss_technology = ""
    all_ss_type = ""
    all_lat_lon = ""
    all_customer_address = ""
    all_alias = ""
    all_dl_rssi_during_acceptance = ""
    all_date_of_acceptance = ""
    base_station_alias = ""
    ##### SS Tooltip Variables End

    ss_counter = 0

    if circuits and sector_id:
        for circuit_id in circuits:
            if circuit_id:
                circuit = circuits[circuit_id][0]
                if circuit['SID'] and circuit['SID'] == sector_id:
                    far_end_perf_url = ""
                    far_end_inventory_url = ""
                    page_type = 'network'

                    #unique circuit id condition
                    if circuit_id not in circuit_ids:
                        circuit_ids.append(circuit_id)

                    techno_to_append = circuit['SS_TECH']
                    type_to_append = circuit['SS_TYPE']


                    if circuit['CIRCUIT_TYPE'] and circuit['CIRCUIT_TYPE'].lower() in ['backhaul', 'bh']:
                        techno_to_append = 'PTP BH'

                    if circuit['SSIP'] and circuit['SSIP'] not in substation_ip:
                        # Check for technology to make perf page url
                        if techno_to_append.lower() in ['pmp', 'wimax', 'ptp', 'p2p']:
                            page_type = 'customer'

                        try:
                            far_end_perf_url = reverse(
                                'SingleDevicePerf',
                                kwargs={
                                    'page_type': page_type, 
                                    'device_id': circuit['SS_DEVICE_ID']
                                },
                                current_app='performance'
                            )
                        except Exception, e:
                            far_end_perf_url = ''

                        # Sector Device Inventory URL
                        far_end_inventory_url = reverse(
                            'device_edit',
                            kwargs={
                                'pk': circuit['SS_DEVICE_ID']
                            },
                            current_app='device'
                        )

                        substation_ip.append(circuit['SSIP'])

                    # If with_data flag is true then send tooltip data
                    if with_data:
                        # Appending SS Infowindow Content
                        base_station_alias += unicode(nocout_utils.format_value(circuit['BSALIAS']))+"|"
                        all_ckt_ids += unicode(nocout_utils.format_value(circuit['CCID']))+"|"
                        all_customer_alias += unicode(nocout_utils.format_value(circuit['CUST']))+"|"
                        all_ss_ip +=  unicode(nocout_utils.format_value(circuit['SSIP']))+"|"
                        all_pe_ip +=  unicode(nocout_utils.format_value(circuit['BH_PE_IP']))+"|"
                        all_qos_bandwidth +=  unicode(nocout_utils.format_value(circuit['QOS']))+"|"
                        all_antenna_height +=  unicode(nocout_utils.format_value(circuit['SSHGT']))+"|"
                        all_polarisation +=  unicode(nocout_utils.format_value(circuit['SS_ANTENNA_POLARIZATION'],type_of='antenna'))+"|"
                        all_mount_type +=  unicode(nocout_utils.format_value(circuit['SSANTENNAMOUNTTYPE']))+"|"
                        all_antenna_type +=  unicode(nocout_utils.format_value(circuit['SS_ANTENNA_TYPE']))+"|"
                        all_cable_length +=  unicode(nocout_utils.format_value(circuit['SS_CABLE_LENGTH']))+"|"
                        all_ethernet_extender +=  unicode(nocout_utils.format_value(circuit['SS_ETH_EXT']))+"|"
                        all_building_height +=  unicode(nocout_utils.format_value(circuit['SS_BUILDING_HGT']))+"|"
                        all_tower_height +=  unicode(nocout_utils.format_value(circuit['SS_TOWER_HGT']))+"|"
                        all_ss_technology +=  unicode(nocout_utils.format_value(techno_to_append))+"|"
                        all_ss_type +=  unicode(nocout_utils.format_value(type_to_append))+"|"
                        all_lat_lon +=  unicode(unicode(nocout_utils.format_value(circuit['SS_LATITUDE']))+","+unicode(nocout_utils.format_value(circuit['SS_LONGITUDE'])))+"|"
                        all_customer_address +=  unicode(nocout_utils.format_value(circuit['SS_CUST_ADDR']))+"|"
                        all_alias +=  unicode(nocout_utils.format_value(circuit['SS_ALIAS']))+"|"
                        all_dl_rssi_during_acceptance +=  unicode(nocout_utils.format_value(circuit['RSSI']))+"|"
                        all_date_of_acceptance +=  unicode(nocout_utils.format_value(circuit['DATE_OF_ACCEPT']))+"|"

                    substation_info.append(
                        {
                            'id': circuit['SSID'],
                            'name': circuit['SS_NAME'],
                            'device_name': circuit['SSDEVICENAME'],
                            'device_id' : circuit['SS_DEVICE_ID'],
                            'data': {
                                "lat": circuit['SS_LATITUDE'],
                                "lon": circuit['SS_LONGITUDE'],
                                "perf_page_url" : far_end_perf_url,
                                "inventory_url" : far_end_inventory_url,
                                "circuit_id" : nocout_utils.format_value(circuit['CCID']),
                                # "antenna_height": nocout_utils.format_value(circuit['SSHGT'], type_of='random'),
                                "substation_device_ip_address": circuit['SSIP'],
                                "technology": techno_to_append,
                                "device_type" : type_to_append,
                                "markerUrl": nocout_utils.format_value(format_this=circuit['SS_GMAP_ICON'], type_of='icon'),
                                "show_link": 1,
                                "link_color": frequency_color,
                                "item_index" : ss_counter
                            }
                        }
                    )
                    # Increment counter as per SS loop
                    ss_counter += 1

    # If with_data flag is true then send tooltip data
    if with_data:
        # Create Sub Station Info List
        subStationsInfo = [
            {
                'name': 'base_station_alias',
                'title': 'Base Station Name',
                'show': 0,
                'value': base_station_alias
            },
            {
                'name': 'cktid',
                'title': 'Circuit ID',
                'show': 1,
                'value': all_ckt_ids
            },
            {
                'name': 'customer_alias',
                'title': 'Customer Name',
                'show': 1,
                'value': all_customer_alias
            },
            {
                'name': 'ss_ip',
                'title': 'SS IP',
                'show': 1,
                'value': all_ss_ip
            },
            {
                'name': 'pe_ip',
                'title': 'PE IP',
                'show': 1,
                'value': all_pe_ip
            },
            {
                'name': 'qos_bandwidth',
                'title': 'QOS(BW)',
                'show': 1,
                'value': all_qos_bandwidth
            },
            {
                'name': 'antenna_height',
                'title': 'Antenna Height',
                'show': 1,
                'value': all_antenna_height
            },
            {
                'name': 'polarisation',
                'title': 'Polarisation',
                'show': 1,
                'value': all_polarisation
            },
            {
                'name': 'mount_type',
                'title': 'SS MountType',
                'show': 1,
                'value': all_mount_type
            },
            {
                'name': 'antenna_type',
                'title': 'Antenna Type',
                'show': 1,
                'value': all_antenna_type
            },
            {
                'name': 'cable_length',
                'title': 'Cable Length',
                'show': 1,
                'value': all_cable_length
            },
            {
                'name': 'ethernet_extender',
                'title': 'Ethernet Extender',
                'show': 1,
                'value': all_ethernet_extender
            },
            {
                'name': 'building_height',
                'title': 'Building Height',
                'show': 1,
                'value': all_building_height
            },
            {
                'name': 'tower_height',
                'title': 'tower_height',
                'show': 1,
                'value': all_tower_height
            },
            {
                'name': 'ss_technology',
                'title': 'Technology',
                'show': 1,
                'value': all_ss_technology
            },
            {
                'name': 'ss_devicetype',
                'title': 'Device Type',
                'show': 1,
                'value': all_ss_type
            },
            {
                'name': 'lat_lon',
                'title': 'Lat, Long',
                'show': 1,
                'value': all_lat_lon
            },
            {
                'name': 'customer_address',
                'title': 'Customer Address',
                'show': 1,
                'value': all_customer_address
            },
            {
                'name': 'alias',
                'title': 'Alias',
                'show': 1,
                'value': all_alias
            },
            {
                'name': 'dl_rssi_during_acceptance',
                'title': 'RSSI During Acceptance',
                'show': 1,
                'value': all_dl_rssi_during_acceptance
            },
            {
                'name': 'date_of_acceptance',
                'title': 'Date of Acceptance',
                'show': 1,
                'value': all_date_of_acceptance
            }
        ]


    return (substation_info, circuit_ids, substation_ip, subStationsInfo)


def prepare_raw_bs_result(bs_result=None,with_data=False):
    """

    :return:
    """
    bs_vendor_list = []
    sector_ss_vendor = []
    sector_ss_technology = []
    sector_ss_type = []
    sector_configured_on_devices = []
    circuit_ids = []
    sector_planned_frequencies = []

    if bs_result:

        base_station = bs_result[0]

        bs_marker_icon = 'static/img/icons/bs_black.png'

        try:
            if base_station['BSMAINTENANCESTATUS'] and base_station['BSMAINTENANCESTATUS'].strip() == 'Yes':
                bs_marker_icon = 'static/img/icons/bs_red.png'
        except Exception, e:
            # raise e
            pass

        base_station_info = {
            'id': base_station['BSID'],
            'name': base_station['BSNAME'],
            'alias': base_station['BSALIAS'],
            'data': {
                'lat': base_station['BSLAT'],
                'lon': base_station['BSLONG'],
                "markerUrl": bs_marker_icon,
                "maintenance_status" : base_station['BSMAINTENANCESTATUS'],
                'antenna_height': 0,
                'vendor': None,
                'city': base_station['BSCITY'],
                'state': base_station['BSSTATE'],
                'bh_id' : base_station['BHID'],
                'bh_device_id' : base_station['BH_DEVICE_ID'],
                'bh_device_type' : base_station['BHTYPE'],
                'bh_device_tech' : base_station['BHTECH'],
                'param': {
                    'base_station': [],
                    'backhual' : []
                }
            },
        }

        # If with_data flag is true then send tooltip data
        if with_data:
            base_station_info['data']['param']['base_station'] = prepare_raw_basestation(base_station=base_station)
            base_station_info['data']['param']['backhual'] = prepare_raw_backhaul(backhaul=base_station)

        sector_dict = pivot_element(bs_result, 'SECTOR_ID')

        sector_info, \
        sector_ss_vendor, \
        sector_ss_technology, \
        sector_ss_type, \
        sector_configured_on_devices, \
        circuit_ids, \
        sector_planned_frequencies, \
        sectors_info_list = prepare_raw_sector(sectors=sector_dict,with_data=with_data)

        base_station_info['data']['param']['sector'] = sector_info
        base_station_info['data']['param']['sectors_info_list'] = sectors_info_list
        base_station_info['sector_ss_vendor'] = "|".join(sector_ss_vendor)
        base_station_info['sector_ss_technology'] = "|".join(sector_ss_technology)
        base_station_info['sector_ss_type'] = "|".join(sector_ss_type)
        base_station_info['sector_configured_on_devices'] = "|".join(sector_configured_on_devices)
        base_station_info['circuit_ids'] = "|".join(circuit_ids)
        base_station_info['sector_planned_frequencies'] = "|".join(sector_planned_frequencies)

        return base_station_info

    return []
