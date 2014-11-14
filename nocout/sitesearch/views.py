import logging
from inventory.models import BaseStation, Customer, Antenna
from device.models import DeviceType, DeviceVendor, DeviceTechnology, City
from random import randint, uniform

from nocout.utils.util import format_value

logger = logging.getLogger(__name__)

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
        return tech_marker_url_master(techno, ms)


def tech_marker_url_master(techno, master=True):
    """

    :param techno: technology P2P,
    :return: technology markers
    """
    if master:
        if techno == "P2P":
            return "static/img/icons/mobilephonetower1.png"
        elif techno == "PMP":
            return "static/img/icons/mobilephonetower2.png"
        elif techno == "WiMAX":
            return "static/img/icons/mobilephonetower3.png"
        else:
            return "static/img/marker/icon2_small.png"
    else:
        return tech_marker_url_slave(techno)

def tech_marker_url_slave(techno):
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

def prepare_basestation(base_station, bs_city_name, bs_state_name):
    try:
        base_station_info = [
            {
                'name': 'name',
                'title': 'Base-Station Name',
                'show': 0,
                'value': base_station.name if base_station.name else 'N/A'
            },
            {
                'name': 'alias',
                'title': 'Base-Station Name',
                'show': 1,
                'value': base_station.alias if base_station.name else 'N/A'
            },
            {
                'name': 'bs_site_id',
                'title': 'BS Site Name',
                'show': 1,
                'value': base_station.bs_site_id if base_station.bs_site_id else 'N/A'
            },
            {
                'name': 'bs_site_type',
                'title': 'BS Site Type',
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
                'value': bs_city_name
            },
            {
                'name': 'bs_state',
                'title': 'State',
                'show': 1,
                'value': bs_state_name
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
            },
            {
                'name':'bs_switch',
                'title':'BS Switch',
                'show':1,
                'value': base_station.bs_switch.ip_address
                        if (base_station and base_station.bs_switch and base_station.bs_switch.ip_address)
                        else 'N/A'
            }
        ]
        return base_station_info
    except Exception as no_basestation:
        return []

def prepare_raw_basestation(base_station=None):
    """

    :param base_station: base-station dictionary object
    :return: base-station information
    """
    if base_station:
        base_station_info = [
            {
                'name': 'name',
                'title': 'Base-Station Name',
                'show': 0,
                'value': format_value(base_station['BSNAME'])
            },
            {
                'name': 'alias',
                'title': 'Base-Station Name',
                'show': 1,
                'value': format_value(base_station['BSALIAS'])
            },
            {
                'name': 'bs_site_id',
                'title': 'BS Site Name',
                'show': 1,
                'value': format_value(base_station['BSSITEID'])
            },
            {
                'name': 'bs_site_type',
                'title': 'BS Site Type',
                'show': 1,
                'value': format_value(base_station['BSSITETYPE'])
            },
            {
                'name': 'building_height',
                'title': 'Building Height',
                'show': 1,
                'value': format_value(base_station['BSTOWERHEIGHT'])
            },
            {
                'name': 'tower_height',
                'title': 'Tower Height',
                'show': 1,
                'value': format_value(base_station['BSBUILDINGHGT'])
            },
            {
                'name': 'bs_city',
                'title': 'City',
                'show': 1,
                'value': format_value(base_station['BSCITY'])
            },
            {
                'name': 'bs_state',
                'title': 'State',
                'show': 1,
                'value': format_value(base_station['BSSTATE'])
            },
            {
                'name': 'bs_address',
                'title': 'Address',
                'show': 1,
                'value': format_value(base_station['BSADDRESS'])
            },
            {
                'name': 'bs_gps_type',
                'title': 'GPS Type',
                'show': 1,
                'value': format_value(base_station['BSGPSTYPE'])
            },
            {
                'name':'bs_type',
                'title':'BS Type',
                'show':1,
                'value': format_value(base_station['BSSITETYPE'])
            },
            {
                'name':'bs_switch',
                'title':'BS Switch',
                'show':1,
                'value': format_value(base_station['BSSWITCH'])
            }
        ]
        return base_station_info
    return []

def prepare_backhaul(backhaul):
    try:
        backhaul_info = [
            {
                'name': 'bh_configured_on',
                'title': 'BH Configured On',
                'show': 1,
                'value': backhaul.bh_configured_on.device_name if backhaul else 'N/A'
            },
            {
                'name': 'bh_capacity',
                'title': 'BH Capacity',
                'show': 1,
                'value': backhaul.bh_capacity if backhaul else 'N/A'
            },
            {
                'name': 'bh_type',
                'title': 'BH Type',
                'show': 1,
                'value': backhaul.bh_type if backhaul else 'N/A'
            },
            {
                'name': 'pe_ip',
                'title': 'PE IP',
                'show': 1,
                'value': backhaul.pe_ip if backhaul else 'N/A'
            },
            {
                'name': 'bh_connectivity',
                'title': 'BH Connectivity',
                'show': 1,
                'value': backhaul.bh_connectivity if backhaul else 'N/A'
            },
            {
                'name': 'aggregation_switch',
                'title': 'Aggregation Switch',
                'show': 1,
                'value': backhaul.aggregator.ip_address
                        if (backhaul and  backhaul.aggregator)
                        else 'N/A'
            },
            {
                'name': 'aggregation_port',
                'title': 'Aggregation Port',
                'show': 1,
                'value': str(backhaul.aggregator_port_name) + "/" + str(backhaul.aggregator_port)
                        if (backhaul and  backhaul.aggregator_port_name and backhaul.aggregator_port)
                        else 'N/A'
            },
            {
                'name': 'bs_converter_ip',
                'title': 'BS Converter IP',
                'show': 1,
                'value': str(backhaul.bh_switch.ip_address) if (backhaul and backhaul.bh_switch) else 'N/A'
            }
        ]
        return backhaul_info
    except Exception as no_backhaul:
        return []

def prepare_raw_backhaul(backhaul):
    """

    :param backhaul:
    :return:
    """
    backhaul_info = []
    if backhaul:
        if backhaul['BHID']:
            backhaul_info = [
                {
                    'name': 'bh_configured_on',
                    'title': 'BH Configured On',
                    'show': 1,
                    'value': format_value(backhaul['BHCONF_IP'])
                },
                {
                    'name': 'bh_capacity',
                    'title': 'BH Capacity',
                    'show': 1,
                    'value': format_value(backhaul['BH_CAPACITY'])
                },
                {
                    'name': 'bh_type',
                    'title': 'BH Type',
                    'show': 1,
                    'value': format_value(backhaul['BH_TYPE'])
                },
                {
                    'name': 'pe_ip',
                    'title': 'PE IP',
                    'show': 1,
                    'value': format_value(backhaul['BH_PE_IP'])
                },
                {
                    'name': 'bh_connectivity',
                    'title': 'BH Connectivity',
                    'show': 1,
                    'value': format_value(backhaul['BH_CONNECTIVITY'])
                },
                {
                    'name': 'aggregation_switch',
                    'title': 'Aggregation Switch',
                    'show': 1,
                    'value': format_value(backhaul['AGGR_IP'])
                },
                {
                    'name': 'pop',
                    'title': 'POP IP',
                    'show': 1,
                    'value': format_value(backhaul['POP_IP'])
                },
                {
                    'name': 'bs_converter_ip',
                    'title': 'BS Converter IP',
                    'show': 1,
                    'value': format_value(backhaul['BSCONV_IP'])
                }
            ]
    return backhaul_info

def prepare_raw_sector(basestations):
    """

    :param sector:
    :return:
    """
    sector_info = []
    sector_list = []

    sector_ss_vendor = []
    sector_ss_technology = []
    sector_configured_on_devices = []
    sector_planned_frequencies = []
    circuit_ids = []

    if basestations:
        for sector in basestations:
            if sector['SECTOR_ID']:
                if sector['SECTOR_ID'] not in sector_list:
                    sector_list.append(sector['SECTOR_ID'])
                    #prepare sector vendor list
                    sector_ss_vendor.append(format_value(format_this=sector['SECTOR_VENDOR']))
                    #prepare technology list
                    sector_ss_technology.append(format_value(format_this=sector['SECTOR_TECH']))
                    #prepare sector configured on device
                    sector_configured_on_devices.append(format_value(format_this=sector['SECTOR_CONF_ON_IP']))

                    #circuit id prepare ?
                    substation, circuit_id, substation_ip = prepare_raw_ss_result(basestations=basestations,
                                                                 sector_id=sector['SECTOR_ID'],
                                                                 frequency_color=format_value(
                                                                     format_this=sector['SECTOR_FREQUENCY_COLOR'],
                                                                     type_of='frequency_color'
                                                                 ),
                                                                 frequency=format_value(
                                                                     format_this=sector['SECTOR_FREQUENCY']
                                                                 )
                    )
                    circuit_ids += circuit_id
                    sector_configured_on_devices += substation_ip
                    sector_planned_frequencies.append(format_value(format_this=sector['SECTOR_FREQUENCY']))
                    sector_info.append(
                        {
                            "color": format_value(format_this=sector['SECTOR_FREQUENCY_COLOR'],type_of='frequency_color'),
                            'radius': format_value(format_this=sector['SECTOR_FREQUENCY_RADIUS'],type_of='frequency_radius'),
                            #sector.cell_radius if sector.cell_radius else 0,
                            'azimuth_angle': format_value(format_this=sector['SECTOR_ANTENNA_AZMINUTH_ANGLE'],type_of='integer'),
                            'beam_width': format_value(format_this=sector['SECTOR_BEAM_WIDTH'],type_of='integer'),
                            'planned_frequency': format_value(format_this=sector['SECTOR_FREQUENCY']),
                            # "markerUrl": tech_marker_url_master(sector.bs_technology.name) if sector.bs_technology else "static/img/marker/icon2_small.png",
                            'orientation': format_value(format_this=sector['SECTOR_ANTENNA_POLARIZATION'],type_of='antenna'),
                            'technology':format_value(format_this=sector['SECTOR_TECH']),
                            'vendor': format_value(format_this=sector['SECTOR_VENDOR']),
                            'sector_configured_on': format_value(format_this=sector['SECTOR_CONF_ON_IP']),
                            'sector_configured_on_device': format_value(format_this=sector['SECTOR_CONF_ON']),
                            'circuit_id':None,
                            'antenna_height': format_value(format_this=sector['SECTOR_ANTENNA_HEIGHT'], type_of='random'),
                            "markerUrl": format_value(format_this=sector['SECTOR_GMAP_ICON'], type_of='icon'),
                            'device_info':[

                             {
                                 "name": "device_name",
                                 "title": "Device Name",
                                 "show": 1,
                                 "value": format_value(format_this=sector['SECTOR_CONF_ON'])
                             },
                             {
                                 "name": "device_id",
                                 "title": "Device ID",
                                 "show": 0,
                                 "value": format_value(format_this=sector['SECTOR_CONF_ON_ID'])
                             },
                             {
                                 "name": "device_mac",
                                 "title": "Device MAC",
                                 "show": 0,
                                 "value": format_value(format_this=sector['SECTOR_CONF_ON_MAC'])
                             }

                            ],
                            'info': [
                                {
                                  'name': 'sector_name',
                                  'title': 'Sector Name',
                                  'show': 1,
                                  'value': format_value(format_this=sector['SECTOR_NAME'])
                                },
                                {
                                    'name': 'planned_frequency',
                                    'title': 'Planned Frequency',
                                    'show': 1,
                                    'value': format_value(format_this=sector['SECTOR_FREQUENCY']),
                                },
                                {
                                  'name': 'type_of_antenna',
                                  'title': 'Antenna Type',
                                  'show': 1,
                                  'value': format_value(format_this=sector['SECTOR_ANTENNA_TYPE']),
                                },
                                {
                                  'name': 'antenna_tilt',
                                  'title': 'Antenna Tilt',
                                  'show': 1,
                                  'value': format_value(format_this=sector['SECTOR_ANTENNA_TILT']),
                                },
                                {
                                  'name': 'antenna_height',
                                  'title': 'Antenna Height',
                                  'show': 1,
                                  'value': format_value(format_this=sector['SECTOR_ANTENNA_HEIGHT']),
                                },
                                {
                                  'name': 'antenna_bw',
                                  'title': 'Antenna Beam Width',
                                  'show': 1,
                                  'value': format_value(format_this=sector['SECTOR_BEAM_WIDTH']),
                                },
                                {
                                  'name': 'antenna_azimuth',
                                  'title': 'Antenna Azimuth Angle',
                                  'show': 1,
                                  'value': format_value(format_this=sector['SECTOR_ANTENNA_AZMINUTH_ANGLE']),
                                },
                                {
                                  'name': 'antenna_splitter_installed',
                                  'title': 'Installation of Splitter',
                                  'show': 1,
                                  'value': format_value(format_this=sector['SECTOR_ANTENNA_SPLITTER']),
                                }
                            ],
                            'sub_station': substation
                        }
                    )
    return (sector_info, sector_ss_vendor, sector_ss_technology, sector_configured_on_devices, circuit_ids, sector_planned_frequencies)

def prepare_raw_ss_result(basestations, sector_id, frequency_color, frequency):
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
    if basestations and sector_id:
        for circuit in basestations:
            if circuit['CCID']:
                if circuit['SID'] and circuit['SID'] == sector_id:
                    if circuit['CCID'] not in circuit_ids:
                        circuit_ids.append(circuit['CCID'])
                    if circuit['SSIP'] and circuit['SSIP'] not in substation_ip:
                        substation_ip.append(circuit['SSIP'])
                    substation_info.append(
                        {
                            'id': circuit['SSID'],
                            'name': circuit['SS_NAME'],
                            'device_name': circuit['SSDEVICENAME'],
                            'data': {
                                "lat": circuit['SS_LATITUDE'],
                                "lon": circuit['SS_LONGITUDE'],
                                "antenna_height": format_value(circuit['SSHGT'], type_of='random'),
                                "substation_device_ip_address": circuit['SSIP'],
                                "technology": circuit['SS_TECH'],
                                "markerUrl": format_value(format_this=circuit['SS_GMAP_ICON'], type_of='icon'),
                                "show_link": 1,
                                "link_color": frequency_color,
                                'param': {
                                    'sub_station': [
                                        {
                                            'name': 'ss_ip',
                                            'title': 'SS IP',
                                            'show': 1,
                                            'value': format_value(circuit['SSIP'])
                                        },
                                        {
                                            'name': 'ss_mac',
                                            'title': 'SS MAC',
                                            'show': 0,
                                            'value': format_value(circuit['SS_MAC'])
                                        },
                                        {
                                            'name': 'name',
                                            'title': 'SS Name',
                                            'show': 0,
                                            'value': format_value(circuit['SS_NAME'])
                                        },
                                        {
                                            'name': 'cktid',
                                            'title': 'Circuit ID',
                                            'show': 1,
                                            'value': format_value(circuit['CCID'])
                                        },
                                        {
                                            'name': 'qos_bandwidth',
                                            'title': 'QOS(BW)',
                                            'show': 1,
                                            'value': format_value(circuit['QOS'])
                                        },
                                        {
                                            'name': 'latitude',
                                            'title': 'Latitude',
                                            'show': 1,
                                            'value': format_value(circuit['SS_LATITUDE'])
                                        },
                                        {
                                            'name': 'longitude',
                                            'title': 'Longitude',
                                            'show': 1,
                                            'value': format_value(circuit['SS_LONGITUDE'])
                                        },
                                        {
                                            'name': 'antenna_height',
                                            'title': 'Antenna Height',
                                            'show': 1,
                                            'value': format_value(circuit['SSHGT'])
                                        },
                                        {
                                            'name': 'polarisation',
                                            'title': 'Polarisation',
                                            'show': 1,
                                            'value': format_value(circuit['SS_ANTENNA_POLARIZATION'],type_of='antenna')
                                        },
                                        {
                                            'name': 'ss_technology',
                                            'title': 'Technology',
                                            'show': 1,
                                            'value': format_value(circuit['SS_TECH'])
                                        },
                                        {
                                            'name': 'building_height',
                                            'title': 'Building Height',
                                            'show': 1,
                                            'value': format_value(circuit['SS_BUILDING_HGT'])
                                        },
                                        {
                                            'name': 'tower_height',
                                            'title': 'tower_height',
                                            'show': 1,
                                            'value': format_value(circuit['SS_TOWER_HGT'])
                                        },
                                        {
                                            'name': 'mount_type',
                                            'title': 'SS MountType',
                                            'show': 1,
                                            'value': format_value(circuit['SSANTENNAMOUNTTYPE'])
                                        },
                                        {
                                            'name': 'alias',
                                            'title': 'Alias',
                                            'show': 1,
                                            'value': format_value(circuit['SS_ALIAS'])
                                        },
                                        {
                                            'name': 'ss_device_id',
                                            'title': 'SS Device ID',
                                            'show': 0,
                                            'value': format_value(circuit['SS_DEVICE_ID'])
                                        },
                                        {
                                            'name': 'antenna_type',
                                            'title': 'Antenna Type',
                                            'show': 1,
                                            'value': format_value(circuit['SS_ANTENNA_TYPE'])
                                        },
                                        {
                                            'name': 'ethernet_extender',
                                            'title': 'Ethernet Extender',
                                            'show': 1,
                                            'value': format_value(circuit['SS_ETH_EXT'])
                                        },
                                        {
                                            'name': 'cable_length',
                                            'title': 'Cable Length',
                                            'show': 1,
                                            'value': format_value(circuit['SS_CABLE_LENGTH'])
                                        },
                                        {
                                            'name': 'customer_address',
                                            'title': 'Customer Address',
                                            'show': 1,
                                            'value': format_value(circuit['SS_CUST_ADDR'])
                                        },
                                        {
                                            'name': 'date_of_acceptance',
                                            'title': 'Date of Acceptance',
                                            'show': 1,
                                            'value': str(format_value(circuit['DATE_OF_ACCEPT']))
                                        },
                                        {
                                            'name': 'dl_rssi_during_acceptance',
                                            'title': 'RSSI During Acceptance',
                                            'show': 1,
                                            'value': format_value(circuit['RSSI'])
                                        },
                                        {
                                            'name': 'planned_frequency',
                                            'title': 'Planned Frequency',
                                            'show': 1,
                                            'value': frequency
                                        }
                                    ]
                                }
                            }
                        }
                    )

    return (substation_info, circuit_ids, substation_ip)


def prepare_raw_bs_result(bs_result=None):
    """

    :return:
    """
    bs_vendor_list = []
    sector_ss_vendor = []
    sector_ss_technology = []
    sector_configured_on_devices = []
    circuit_ids = []
    sector_planned_frequencies = []

    if bs_result:

        base_station = bs_result[0]

        base_station_info = {
            'id': base_station['BSID'],
            'name': base_station['BSNAME'],
            'alias': base_station['BSALIAS'],
            'data': {
                'lat': base_station['BSLAT'],
                'lon': base_station['BSLONG'],
                "markerUrl": 'static/img/marker/slave01.png',
                'antenna_height': 0,
                'vendor': None,
                'city': base_station['BSCITY'],
                'state': base_station['BSSTATE'],
                'param': {
                    'base_station': prepare_raw_basestation(base_station=base_station),
                    'backhual': prepare_raw_backhaul(backhaul=base_station)
                }
            },
        }
        sector_info, \
        sector_ss_vendor, \
        sector_ss_technology, \
        sector_configured_on_devices, \
        circuit_ids, \
        sector_planned_frequencies = prepare_raw_sector(basestations=bs_result)

        base_station_info['data']['param']['sector'] = sector_info
        base_station_info['sector_ss_vendor'] = "|".join(sector_ss_vendor)
        base_station_info['sector_ss_technology'] = "|".join(sector_ss_technology)
        base_station_info['sector_configured_on_devices'] = "|".join(sector_configured_on_devices)
        base_station_info['circuit_ids'] = "|".join(circuit_ids)
        base_station_info['sector_planned_frequencies'] = "|".join(sector_planned_frequencies)

        return base_station_info

    return []
