import logging
from inventory.models import BaseStation, Customer, Antenna
from device.models import DeviceType, DeviceVendor, DeviceTechnology, City
from random import randint, uniform
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


def prepare_result(base_station_object):

    base_station = base_station_object
    #BaseStation.objects.get(id=base_station_id).prefetch_all()
    sectors = base_station.sector.filter(sector_configured_on__is_deleted = 0)
    backhaul = base_station.backhaul

    bs_city_name = "N/A"
    bs_state_name = "N/A"
    try:
        if base_station.city:
            bs_city =  City.objects.prefetch_related('state').filter(id=base_station.city)[0]
            bs_city_name = bs_city.city_name
            bs_state_name =  bs_city.state.state_name
    except:
        pass

    base_station_info = {
        'id': base_station.id,
        'name': base_station.name,
        'alias': base_station.name,
        'data': {
            'lat': base_station.latitude,
            'lon': base_station.longitude,
            "markerUrl": 'static/img/marker/slave01.png',
            'antenna_height': 0,
            'vendor':','.join(sectors[0].bs_technology.device_vendors.values_list('name', flat=True)),
            'city': bs_city_name,
            'state': bs_state_name,
            'param': {
                'base_station': prepare_basestation(base_station, bs_city_name, bs_state_name),
                'backhual': prepare_backhaul(backhaul)
            }
        },
    }

    base_station_info['data']['param']['sector'] = []
    base_station_info['sector_ss_vendor']=''
    base_station_info['sector_ss_technology']=''
    base_station_info['sector_configured_on_devices']=''
    base_station_info['circuit_ids']=''
    for sector in sectors:
        # if Sector.objects.get(id=sector.id).sector_configured_on.is_deleted == 1:
        #     continue

        circuits = sector.circuit_set.all()

        # for bsname in base_station_info['data']:
        #     if 'technology' not in bsname:
        #         base_station_info['data']["technology"] = sector.bs_technology.name if sector.bs_technology else 'N/A'
        #     if 'vendor' not in bsname:
        #         base_station_info['data']["vendor"] = ','.join(sector.bs_technology.device_vendors.values_list('name', flat=True))
        #         'vendor':','.join(base_station.bs_technology.device_vendors.values_list('name', flat=True)),

        base_station_info['data']['param']['sector'] += [
        {
            "color": sector.frequency.color_hex_value
                    if (sector.frequency and sector.frequency.color_hex_value)
                    else 'rgba(74,72,94,0.58)',
            'radius': sector.frequency.frequency_radius
                if (sector.frequency and sector.frequency.frequency_radius)
                else uniform(0,3),
            #sector.cell_radius if sector.cell_radius else 0,
            'azimuth_angle': sector.antenna.azimuth_angle if sector.antenna else 0,
            'beam_width': sector.antenna.beam_width if sector.antenna else 0,
            # "markerUrl": tech_marker_url_master(sector.bs_technology.name) if sector.bs_technology else "static/img/marker/icon2_small.png",
            'orientation': sector.antenna.polarization if sector.antenna else "vertical",
            'technology':sector.bs_technology.name if sector.bs_technology else 'N/A',
            'vendor': DeviceVendor.objects.get(id=sector.sector_configured_on.device_vendor).name,
            'sector_configured_on':sector.sector_configured_on.device_name,
            'circuit_id':None,
            'antenna_height': sector.antenna.height if sector.antenna else randint(40,70),
            "markerUrl": tech_marker_url(sector.sector_configured_on.device_type, sector.bs_technology.name, ms=True),
            'device_info':[

             {
                 "name": "device_name",
                 "title": "Device Name",
                 "show": 1,
                 "value": sector.sector_configured_on.device_name
             },
             {
                 "name": "device_id",
                 "title": "Device ID",
                 "show": 0,
                 "value": sector.sector_configured_on.id
             },
             {
                 "name": "device_mac",
                 "title": "Device MAC",
                 "show": 0,
                 "value": sector.sector_configured_on.mac_address
             }

            ],
            'info': [
                {
                  'name': 'sector_name',
                  'title': 'Sector Name',
                  'show': 1,
                  'value': sector.name
                },
                {
                    'name': 'planned_frequency',
                    'title': 'Planned Frequency',
                    'show': 1,
                    'value':sector.frequency.value
                        if (sector.frequency and sector.frequency.value)
                        else 'N/A',
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
                }
            ] + prepare_basestation(base_station, bs_city_name, bs_state_name),
            'sub_station': []
        }]
        base_station_info['sector_ss_vendor']+= DeviceVendor.objects.get(id=sector.sector_configured_on.device_vendor).name +', '
        base_station_info['sector_ss_technology']+= DeviceTechnology.objects.get(id=sector.sector_configured_on.device_technology).name +', '
        base_station_info['sector_configured_on_devices']+= sector.sector_configured_on.device_name + ', '


        for circuit in circuits:
            substation = circuit.sub_station #SubStation.objects.get(id=circuit.sub_station.id)
            substation_device = substation.device #Device.objects.get(id=substation.device.id)
            if substation_device.is_deleted == 1:
                continue
            substation_list= [
            {
                'id': substation.id,
                'name': substation.name,
                'device_name': substation.device.device_name,
                'data': {
                    "lat": substation.latitude if substation.latitude else substation_device.latitude,
                    "lon": substation.longitude if substation.longitude else substation_device.longitude,
                    "antenna_height": substation.antenna.height if substation.antenna else randint(40,70),
                    "substation_device_ip_address": substation_device.ip_address if substation_device.ip_address else 'N/A',
                    "technology":sector.bs_technology.name,
                    "markerUrl": tech_marker_url(substation_device.device_type, sector.bs_technology.name, ms=False), #tech_marker_url_slave(sector.bs_technology.name),
                    "show_link": 1,
                    "link_color": sector.frequency.color_hex_value if hasattr(
                        sector,
                        'frequency') and sector.frequency else 'rgba(74,72,94,0.58)',
                    'param': {
                        'sub_station': [
                            {
                                'name': 'ss_ip',
                                'title': 'SS IP',
                                'show': 1,
                                'value': substation_device.ip_address if substation_device.ip_address else 'N/A'
                            },
                            {
                                'name': 'ss_mac',
                                'title': 'SS MAC',
                                'show': 0,
                                'value': substation_device.mac_address if substation_device.mac_address else 'N/A'
                            },
                            {
                                'name': 'name',
                                'title': 'SS Name',
                                'show': 0,
                                'value': substation.name if substation.name else 'N/A'
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
                                'name': 'latitude',
                                'title': 'Latitude',
                                'show': 1,
                                'value': substation.latitude if substation.latitude else substation_device.latitude
                            },
                            {
                                'name': 'longitude',
                                'title': 'Longitude',
                                'show': 1,
                                'value': substation.longitude if substation.longitude else substation_device.longitude
                            },
                            {
                                'name': 'antenna_height',
                                'title': 'Antenna Height',
                                'show': 1,
                                'value': substation.antenna.height if substation.antenna else randint(40,70)
                            },
                            {
                                'name': 'polarisation',
                                'title': 'Polarisation',
                                'show': 1,
                                'value': sector.antenna.polarization \
                                    if sector.antenna else 'N/A'
                            },
                            {
                                'name': 'ss_technology',
                                'title': 'Technology',
                                'show': 1,
                                'value': sector.bs_technology.name if sector.bs_technology else 'N/A'
                            },
                            {
                                'name': 'building_height',
                                'title': 'Building Height',
                                'show': 1,
                                'value': substation.building_height \
                                    if substation.building_height else 0
                            },
                            {
                                'name': 'tower_height',
                                'title': 'tower_height',
                                'show': 1,
                                'value': substation.tower_height \
                                    if substation.tower_height else 0
                            },
                            {
                                'name': 'mount_type',
                                'title': 'SS MountType',
                                'show': 1,
                                'value': sector.antenna.mount_type if sector.antenna else 'N/A'
                            },
                            {
                                'name': 'alias',
                                'title': 'Alias',
                                'show': 1,
                                'value': substation_device.device_alias if substation_device.device_alias else 'N/A'
                            },
                            {
                                'name': 'ss_device_id',
                                'title': 'SS Device ID',
                                'show': 0,
                                'value': substation_device.id if substation_device.id else 'N/A'
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
                            },
                            {
                                'name': 'planned_frequency',
                                'title': 'Planned Frequency',
                                'show': 1,
                                'value':sector.frequency.value
                                    if (sector.frequency and sector.frequency.value)
                                    else 'N/A',
                            }
                        ]}
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
                        'value': Customer.objects.get(id= substation.circuit_set.values_list('customer_id', flat=True)[0]).alias \
                            if substation.circuit_set.values_list('customer_id', flat=True)[0] else 'N/A'
                    },
                    {
                        'name': 'antenna_mount_type',
                        'title': 'Antenna Mount Type',
                        'show': 1,
                        'value': Antenna.objects.get(id=substation.antenna.id).mount_type \
                            if substation.antenna else 'N/A'
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
            base_station_info['data']['param']['sector'][-1]['circuit_id']= circuit.circuit_id
            base_station_info['sector_ss_vendor']+= DeviceVendor.objects.get(id=substation.device.device_vendor).name +', '
            base_station_info['sector_ss_technology']+= DeviceTechnology.objects.get(id=substation.device.device_technology).name +', '
            base_station_info['sector_configured_on_devices']+= substation_device.ip_address + ', '
            base_station_info['circuit_ids']+= circuit.circuit_id +', '

    # Additional Information required to filter the data in the gis maps
    base_station_sector_ss_vendor= base_station_info['sector_ss_vendor'].split(', ')
    base_station_sector_ss_technology= base_station_info['sector_ss_technology'].split(', ')
    base_station_sector_configured_on= base_station_info['sector_configured_on_devices'].split(', ')
    base_station_circuit_ids= base_station_info['circuit_ids'].split(', ')

    base_station_info['sector_ss_vendor']= "|".join(sorted(set(base_station_sector_ss_vendor), key=base_station_sector_ss_vendor.index))
    base_station_info['sector_ss_technology']= "|".join(sorted(set(base_station_sector_ss_technology), key=base_station_sector_ss_technology.index))
    base_station_info['sector_configured_on_devices']= "|".join(sorted(set(base_station_sector_configured_on), key=base_station_sector_configured_on.index))
    base_station_info['circuit_ids']= "|".join(sorted(set(base_station_circuit_ids), key=base_station_circuit_ids.index))

    return base_station_info