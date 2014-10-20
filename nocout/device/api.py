import ast, sys
import json, logging
import urllib
from multiprocessing import Process, Queue
from django.db.models import Q, Count
from django.views.generic.base import View
from django.http import HttpResponse
from inventory.models import BaseStation, Sector, Circuit, SubStation, Customer, LivePollingSettings, \
    ThresholdConfiguration, ThematicSettings
from device.models import Device, DeviceType, DeviceVendor, \
    DeviceTechnology, DeviceModel, State, Country, City
import requests
from nocout.utils import logged_in_user_organizations
from nocout.utils.util import fetch_raw_result, dict_fetchall, format_value
from service.models import DeviceServiceConfiguration, Service, ServiceDataSource
from django.contrib.staticfiles.templatetags.staticfiles import static
from site_instance.models import SiteInstance
from sitesearch.views import prepare_raw_bs_result
from nocout.settings import GIS_MAP_MAX_DEVICE_LIMIT

from django.db import connections

logger=logging.getLogger(__name__)


class DeviceStatsApi(View):

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

        organizations= logged_in_user_organizations(self)

        if organizations:
            # for organization in organizations:
            page_number= self.request.GET.get('page_number', None)
            start, offset= None, None
            if page_number:
                #Setting the Start and Offset limit for the Query.
                offset= int(page_number)*GIS_MAP_MAX_DEVICE_LIMIT
                start= offset - GIS_MAP_MAX_DEVICE_LIMIT

            # base_stations_and_sector_configured_on_devices= \
            #     Sector.objects.filter(sector_configured_on__id__in= \
            #                                   organization.device_set.values_list('id', flat=True))[start:offset]\
            #                                   .values_list('base_station').annotate(dcount=Count('base_station'))
            base_stations_and_sector_configured_on_devices = BaseStation.objects.prefetch_related(
                'sector', 'backhaul').filter(
                    sector__in = Sector.objects.filter(
                        sector_configured_on__organization__in=organizations)
                )[start:offset].annotate(dcount=Count('name'))

            bs_id = BaseStation.objects.prefetch_related(
                'sector', 'backhaul').filter(
                    sector__in = Sector.objects.filter(
                        sector_configured_on__organization__in=organizations)
                )[start:offset].annotate(dcount=Count('name')).values_list('id',flat=True)

            if base_stations_and_sector_configured_on_devices:
                #if the total count key is not in the meta objects then run the query
                total_count=self.request.GET.get('total_count')

                if not int(total_count):
                    total_count= BaseStation.objects.filter(
                    sector__in = Sector.objects.filter(
                        sector_configured_on__organization__in=organizations)
                    ).annotate(dcount=Count('name')).count()
                    self.result['data']['meta']['total_count']= total_count

                else:
                    #Otherthan first request the total_count will be echoed back and then can be placed in the result.
                    total_count= self.request.GET.get('total_count')
                    self.result['data']['meta']['total_count']= total_count

                self.result['data']['meta']['limit']= GIS_MAP_MAX_DEVICE_LIMIT
                self.result['data']['meta']['offset']= offset
                self.result['data']['objects']= {"id" : "mainNode", "name" : "mainNodeName", "data" :
                                                        { "unspiderfy_icon" : "static/img/icons/bs.png" }
                                                }
                self.result['data']['objects']['children']= list()

                query = """
                    select * from (
                        select basestation.id as BSID,
                                basestation.name as BSNAME,
                                basestation.alias as BSALIAS,
                                basestation.bs_site_id as BSSITEID,
                                basestation.bs_site_type as BSSITETYPE,

                                device.ip_address as BSSWITCH,

                                basestation.bs_type as BSTYPE,
                                basestation.bh_bso as BSBHBSO,
                                basestation.hssu_used as BSHSSUUSED,
                                basestation.latitude as BSLAT,
                                basestation.longitude as BSLONG,

                                basestation.infra_provider as BSINFRAPROVIDER,
                                basestation.gps_type as BSGPSTYPE,
                                basestation.building_height as BSBUILDINGHGT,
                                basestation.tower_height as BSTOWERHEIGHT,

                                city.city_name as BSCITY,
                                state.state_name as BSSTATE,
                                country.country_name as BSCOUNTRY,

                                basestation.address as BSADDRESS,

                                backhaul.id as BHID,
                                sector.id as SID

                        from inventory_basestation as basestation
                        left join (
                            inventory_sector as sector,
                            inventory_backhaul as backhaul,
                            device_country as country,
                            device_city as city,
                            device_state as state,
                            device_device as device
                        )
                        on (
                            sector.base_station_id = basestation.id
                        and
                            backhaul.id = basestation.backhaul_id
                        and
                            city.id = basestation.city
                        and
                            state.id = basestation.state
                        and
                            country.id = basestation.country
                        and
                            device.id = basestation.bs_switch_id
                        )
                    )as bs_info
                    left join (
                        select * from (select

                            sector.id as SECTOR_ID,
                            sector.name as SECTOR_NAME,
                            sector.alias as SECTOR_ALIAS,
                            sector.sector_id as SECTOR_SECTOR_ID,
                            sector.base_station_id as SECTOR_BS_ID,
                            sector.mrc as SECTOR_MRC,
                            sector.tx_power as SECTOR_TX,
                            sector.rx_power as SECTOR_RX,
                            sector.rf_bandwidth as SECTOR_RFBW,
                            sector.frame_length as SECTOR_FRAME_LENGTH,
                            sector.cell_radius as SECTOR_CELL_RADIUS,
                            sector.modulation as SECTOR_MODULATION,

                            technology.name as SECTOR_TECH,
                            vendor.name as SECTOR_VENDOR,
                            devicetype.name as SECTOR_TYPE,
                            devicetype.device_icon as SECTOR_ICON,
                            devicetype.device_gmap_icon as SECTOR_GMAP_ICON,

                            device.id as SECTOR_CONF_ON_ID,
                            device.device_name as SECTOR_CONF_ON,
                            device.ip_address as SECTOR_CONF_ON_IP,
                            device.mac_address as SECTOR_CONF_ON_MAC,

                            antenna.antenna_type as SECTOR_ANTENNA_TYPE,
                            antenna.height as SECTOR_ANTENNA_HEIGHT,
                            antenna.polarization as SECTOR_ANTENNA_POLARIZATION,
                            antenna.tilt as SECTOR_ANTENNA_TILT,
                            antenna.gain as SECTOR_ANTENNA_GAIN,
                            antenna.mount_type as SECTORANTENNAMOUNTTYPE,
                            antenna.beam_width as SECTOR_BEAM_WIDTH,
                            antenna.azimuth_angle as SECTOR_ANTENNA_AZMINUTH_ANGLE,
                            antenna.reflector as SECTOR_ANTENNA_REFLECTOR,
                            antenna.splitter_installed as SECTOR_ANTENNA_SPLITTER,
                            antenna.sync_splitter_used as SECTOR_ANTENNA_SYNC_SPLITTER,
                            antenna.make_of_antenna as SECTOR_ANTENNA_MAKE,

                            frequency.color_hex_value as SECTOR_FREQUENCY_COLOR,
                            frequency.frequency_radius as SECTOR_FREQUENCY_RADIUS,
                            frequency.value as SECTOR_FREQUENCY

                            from inventory_sector as sector
                            join (
                                device_device as device,
                                inventory_antenna as antenna,
                                device_devicetechnology as technology,
                                device_devicevendor as vendor,
                                device_devicetype as devicetype
                            )
                            on (
                                device.id = sector.sector_configured_on_id
                            and
                                antenna.id = sector.antenna_id
                            and
                                technology.id = device.device_technology
                            and
                                devicetype.id = device.device_type
                            and
                                vendor.id = device.device_vendor
                            ) left join (device_devicefrequency as frequency)
                            on (
                                frequency.id = sector.frequency_id
                            )
                        ) as sector_info
                        left join (
                            select circuit.id as CID,
                                circuit.alias as CALIAS,
                                circuit.circuit_id as CCID,
                                circuit.sector_id as SID,

                                circuit.circuit_type as CIRCUIT_TYPE,
                                circuit.qos_bandwidth as QOS,
                                circuit.dl_rssi_during_acceptance as RSSI,
                                circuit.dl_cinr_during_acceptance as CINR,
                                circuit.jitter_value_during_acceptance as JITTER,
                                circuit.throughput_during_acceptance as THROUHPUT,
                                circuit.date_of_acceptance as DATE_OF_ACCEPT,

                                customer.alias as CUST,
                                customer.address as SS_CUST_ADDR,

                                substation.id as SSID,
                                substation.name as SS_NAME,
                                substation.alias as SS_ALIAS,
                                substation.version as SS_VERSION,
                                substation.serial_no as SS_SERIAL_NO,
                                substation.building_height as SS_BUILDING_HGT,
                                substation.tower_height as SS_TOWER_HGT,
                                substation.ethernet_extender as SS_ETH_EXT,
                                substation.cable_length as SS_CABLE_LENGTH,
                                substation.latitude as SS_LATITUDE,
                                substation.longitude as SS_LONGITUDE,
                                substation.mac_address as SS_MAC,

                                antenna.height as SSHGT,
                                antenna.antenna_type as SS_ANTENNA_TYPE,
                                antenna.height as SS_ANTENNA_HEIGHT,
                                antenna.polarization as SS_ANTENNA_POLARIZATION,
                                antenna.tilt as SS_ANTENNA_TILT,
                                antenna.gain as SS_ANTENNA_GAIN,
                                antenna.mount_type as SSANTENNAMOUNTTYPE,
                                antenna.beam_width as SS_BEAM_WIDTH,
                                antenna.azimuth_angle as SS_ANTENNA_AZMINUTH_ANGLE,
                                antenna.reflector as SS_ANTENNA_REFLECTOR,
                                antenna.splitter_installed as SS_ANTENNA_SPLITTER,
                                antenna.sync_splitter_used as SS_ANTENNA_SYNC_SPLITTER,
                                antenna.make_of_antenna as SS_ANTENNA_MAKE,

                                device.ip_address as SSIP,
                                device.id as SS_DEVICE_ID,
                                device.device_alias as SSDEVICEALIAS,
                                device.device_name as SSDEVICENAME,

                                technology.name as SS_TECH,
                                vendor.name as SS_VENDOR,

                                devicetype.device_icon as SS_ICON,
                                devicetype.device_gmap_icon as SS_GMAP_ICON

                            from inventory_circuit as circuit
                            join (
                                inventory_substation as substation,
                                inventory_customer as customer,
                                inventory_antenna as antenna,
                                device_device as device,
                                device_devicetechnology as technology,
                                device_devicevendor as vendor,
                                device_devicetype as devicetype
                            )
                            on (
                                customer.id = circuit.customer_id
                            and
                                substation.id = circuit.sub_station_id
                            and
                                antenna.id = substation.antenna_id
                            and
                                device.id = substation.device_id
                            and
                                technology.id = device.device_technology
                            and
                                vendor.id = device.device_vendor
                            and
                                devicetype.id = device.device_type
                            )
                        ) as ckt_info
                        on (
                            ckt_info.SID = sector_info.SECTOR_ID
                        )
                    ) as sect_ckt
                    on (sect_ckt.SECTOR_BS_ID = bs_info.BSID)
                    left join
                        (
                            select bh_info.BHID as BHID,
                                    bh_info.BH_PORT as BH_PORT,
                                    bh_info.BH_TYPE as BH_TYPE,
                                    bh_info.BH_PE_HOSTNAME as BH_PE_HOSTNAME,
                                    bh_info.BH_PE_IP as BH_PE_IP,
                                    bh_info.BH_CONNECTIVITY as BH_CONNECTIVITY,
                                    bh_info.BH_CIRCUIT_ID as BH_CIRCUIT_ID,
                                    bh_info.BH_CAPACITY as BH_CAPACITY,
                                    bh_info.BH_TTSL_CIRCUIT_ID as BH_TTSL_CIRCUIT_ID,
                                    bh_info.BH_DR_SITE as BH_DR_SITE,

                                    bh_info.BHCONF as BHCONF,
                                    bh_info.BHCONF_IP as BHCONF_IP,
                                    POP_IP,
                                    AGGR_IP,
                                    BSCONV_IP

                            from (
                            select backhaul.id as BHID,
                                    backhaul.bh_port_name as BH_PORT,
                                    backhaul.bh_type as BH_TYPE,
                                    backhaul.pe_hostname as BH_PE_HOSTNAME,
                                    backhaul.pe_ip as BH_PE_IP,
                                    backhaul.bh_connectivity as BH_CONNECTIVITY,
                                    backhaul.bh_circuit_id as BH_CIRCUIT_ID,
                                    backhaul.bh_capacity as BH_CAPACITY,
                                    backhaul.ttsl_circuit_id as BH_TTSL_CIRCUIT_ID,
                                    backhaul.dr_site as BH_DR_SITE,

                                    device.device_name as BHCONF,
                                    device.ip_address as BHCONF_IP

                            from inventory_backhaul as backhaul
                            join (
                                device_device as device
                            )
                            on (
                                device.id = backhaul.bh_configured_on_id
                            )
                            ) as bh_info left join (
                                    select backhaul.id as BHID, device.device_name as POP, device.ip_address as POP_IP from inventory_backhaul as backhaul
                                    left join (
                                        device_device as device
                                    )
                                    on (
                                        device.id = backhaul.pop_id
                                    )
                            ) as pop_info
                            on (bh_info.BHID = pop_info.BHID)
                            left join ((
                                    select backhaul.id as BHID, device.device_name as BSCONV, device.ip_address as BSCONV_IP from inventory_backhaul as backhaul
                                    left join (
                                        device_device as device
                                    )
                                    on (
                                        device.id = backhaul.bh_switch_id
                                    )
                            ) as bscon_info
                            ) on (bh_info.BHID = bscon_info.BHID)
                            left join ((
                                    select backhaul.id as BHID, device.device_name as AGGR, device.ip_address as AGGR_IP from inventory_backhaul as backhaul
                                    left join (
                                        device_device as device
                                    )
                                    on (
                                        device.id = backhaul.aggregator_id
                                    )
                            ) as aggr_info
                            ) on (bh_info.BHID = aggr_info.BHID)

                        ) as bh
                    on
                        (bh.BHID = bs_info.BHID)
                where (bs_info.BSID in ({0}))
                Group by BSID,SECTOR_ID,CID
                ;
                """.format(', '.join(str(i) for i in bs_id))
                # print ((fetch_raw_result(query)))

                raw_result = prepare_raw_result(fetch_raw_result(query))
                for basestation in raw_result:
                    base_station_info= prepare_raw_bs_result(raw_result[basestation])
                    self.result['data']['objects']['children'].append(base_station_info)

                self.result['data']['meta']['device_count']= len(self.result['data']['objects']['children'])
            self.result['message']='Data Fetched Successfully.'
            self.result['success']=1
        return HttpResponse(json.dumps(self.result))

def prepare_raw_result(bs_dict = []):
    """

    :param bs_dict: dictionary of base-station objects
    :return: API formatted result
    """

    bs_list = []
    bs_result = {}
    #preparing result by pivoting via basestation id
    if len(bs_dict):
        for bs in bs_dict:
            BSID = bs['BSID']
            if BSID not in bs_list:
                bs_list.append(BSID)
                bs_result[BSID] = []
            bs_result[BSID].append(bs)
    return bs_result


class DeviceFilterApi(View):

    def get(self, request):
        self.result = {
            "success": 0,
            "message": "Device Loading Completed",
            "data": {
                "meta": {},
                "objects": {}
            }
        }

        vendor_list = []
        technology_data,vendor_data,state_data,city_data=[],[],[],[]
        for device_technology in DeviceTechnology.objects.all():
            technology_data.append({ 'id':device_technology.id,
                                     'value':device_technology.name })
            vendors = device_technology.device_vendors.all()
            for vendor in vendors:
                if vendor not in vendor_list:
                    vendor_list.append(vendor.id)
                    vendor_data.append({ 'id':vendor.id,
                                         'value':vendor.name,
                                         'tech_id': device_technology.id,
                                         'tech_name': device_technology.name
                    })
        # for vendor in DeviceVendor.objects.all():
        #     vendor_data.append({ 'id':vendor.id,
        #                              'value':vendor.name })
        # #
        # for state in State.objects.all():
        #     state_data.append({ 'id':state.id,
        #                              'value':state.state_name })
        state_list = []
        for city in City.objects.all():
            city_data.append({'id':city.id,
                             'value':city.city_name,
                             'state_id': city.state.id,
                             'state_name': city.state.state_name }
            )
            if city.state.id not in state_list:
                state_list.append(city.state.id)
                state_data.append({ 'id':city.state.id,'value':city.state.state_name })

        self.result['data']['objects']['technology']={'data':technology_data}
        self.result['data']['objects']['vendor']={'data':vendor_data}
        self.result['data']['objects']['state']={'data':state_data}
        self.result['data']['objects']['city']={'data':city_data}
        self.result['message']='Data Fetched Successfully.'
        self.result['success']=1

        return HttpResponse(json.dumps(self.result))


class LPServicesApi(View):
    """
        API for fetching the services and data sources for list of devices.
        :Parameters:
            - 'devices' (list) - list of devices

        :Returns:
           - 'result' (dict) - dictionary of devices with associates services and data sources
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
        """Returns json containing devices, services and data sources"""

        result = {
            "success": 0,
            "message": "No Service Data",
            "data": {
            }
        }

        # list of devices for which service and data sources needs to be fetched
        # i.e. ['device1', 'device2']
        try:
            devices = eval(str(self.request.GET.get('devices',None)))
            if devices:
                for dv in devices:
                    device = Device.objects.get(device_name=dv)

                    # fetching all rows form 'service_deviceserviceconfiguration' where device_name is
                    # is name of device currently in loop; to get all associated services
                    device_sdc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name)

                    # initializing dict for current device
                    result['data'][str(dv)] = {}

                    # initializing list for services associated to current device(dv)
                    result['data'][str(dv)]['services'] = []

                    # loop through all services of current device(dv)
                    for dsc in device_sdc:
                        svc_dict = dict()
                        svc_dict['name'] = str(dsc.service_name)
                        svc_dict['value'] = Service.objects.get(name=dsc.service_name).id

                        # initializing list of data sources
                        svc_dict['datasource'] = []

                        # fetching all rows form 'service_deviceserviceconfiguration' where device_name and service_name
                        # are names of current device and service in loop; to get all associated data sources
                        service_data_sources = DeviceServiceConfiguration.objects.filter(device_name=dv, service_name=dsc.service_name)

                        # loop through all the data sources associated with current service(dsc)
                        for sds in service_data_sources:
                            sds_dict = dict()
                            sds_dict['name'] = sds.data_source
                            sds_dict['value'] = ServiceDataSource.objects.get(name=sds.data_source).id
                            # appending data source dict to data sources list for current service(dsc) data source list
                            svc_dict['datasource'].append(sds_dict)

                        # appending service dict to services list of current device(dv)
                        result['data'][str(dv)]['services'].append(svc_dict)
                        result['success'] = 1
                        result['message'] = "Successfully fetched services and data sources."
        except Exception as e:
            result['message'] = e.message
            logger.info(e)

        return HttpResponse(json.dumps(result))


class FetchLPDataApi(View):
    """
        API for fetching the service live polled value
        :Parameters:
            - 'device' (list) - list of devices
            - 'service' (list) - list of services
            - 'datasource' (list) - list of data sources

        :Returns:
           - 'result' (dict) - dictionary containing list of live polled values and icon urls
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
        """Returns json containing live polling value and icon url"""

        # converting 'json' into python object
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

                # encoding 'lp_data'
                encoded_data = urllib.urlencode(lp_data)

                # sending post request to nocout device app to fetch service live polling value
                r = requests.post(url , data=encoded_data)

                # converting post response data into python dict expression
                response_dict = ast.literal_eval(r.text)

                # if response(r) is given by post request than process it further to get success/failure messages
                if r:
                    result['data']['value'].append(response_dict.get('value')[0])

                    # device technology
                    tech = DeviceTechnology.objects.get(pk=device.device_technology)

                    # live polling settings for getting associates service and data sources
                    lps = LivePollingSettings.objects.get(technology=tech, service=service, data_source=data_source)

                    # threshold configuration for getting warning, critical comparison values
                    tc = ThresholdConfiguration.objects.get(live_polling_template=lps)

                    # thematic settings for getting icon url
                    ts = ThematicSettings.objects.get(threshold_template=tc)

                    # comparing threshold values to get icon
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
                    # if response_dict doesn't have key 'success'
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
        API for fetching the service live polled value
        :Parameters:
            - 'technology' (unicode) - id of technology

        :Returns:
           - 'result' (dict) - dictionary containing list of live polling settings
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
        """Returns json containing live polling values and icon urls for bulk devices"""
        # result dictionary to be returned as output of ap1
        result = {
            "success": 0,
            "message": "Failed to fetch live polling settings.",
            "data": {
            }
        }

        # initializing 'lp_templates' list containing live setting templates
        result['data']['lp_templates'] = list()

        # converting 'json' into python object
        technology_id = int(self.request.GET.get('technology', None))

        # technology object
        technology = DeviceTechnology.objects.get(pk=technology_id)

        # get live polling settings corresponding to the technology
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
        API for fetching the service live polled value
        :Parameters:
            - 'technology' (unicode) - id of technology

        :Returns:
           - 'result' (dict) - dictionary containing list of threshold configurations
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
        """Returns json containing live polling values and icon urls for bulk devices"""
        # result dictionary to be returned as output of api
        result = {
            "success": 0,
            "message": "Failed to fetch live polling settings.",
            "data": {
            }
        }

        # initializing 'lp_templates' list containing live setting templates
        result['data']['threshold_templates'] = list()

        # converting 'json' into python object
        technology_id = int(self.request.GET.get('technology', None))

        # technology object
        technology = DeviceTechnology.objects.get(pk=technology_id)

        # get live polling settings corresponding to the technology
        lps = ""
        try:
            lps = LivePollingSettings.objects.filter(technology=technology)
        except Exception as e:
            logger.info(e.message)

        if lps:
            tc_temp = dict()
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
        API for fetching the service live polled value
        :Parameters:
            - 'technology' (unicode) - id of technology

        :Returns:
           - 'result' (dict) - dictionary containing list of threshold configurations
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
        """Returns json containing live polling values and icon urls for bulk devices"""
        # result dictionary to be returned as output of api
        result = {
            "success": 0,
            "message": "Failed to fetch live polling settings.",
            "data": {
            }
        }

        # initializing 'lp_templates' list containing live setting templates
        result['data']['thematic_settings'] = list()

        # converting 'json' into python object
        technology_id = int(self.request.GET.get('technology', None))

        # technology object
        technology = DeviceTechnology.objects.get(pk=technology_id)

        # get live polling settings corresponding to the technology
        lps = ""
        try:
            lps = LivePollingSettings.objects.filter(technology=technology)
        except Exception as e:
            logger.info(e.message)

        if lps:
            tc_temp = dict()
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
                                print "********************************* ts_temp - ", ts_temp
            result['message'] = "Successfully fetched thematic settings."
            result['success'] = 1
        return HttpResponse(json.dumps(result))


class BulkFetchLPDataApi(View):
    """
        API for fetching the service live polled value
        :Parameters:
            - 'ts_template' (unicode) - threshold configuration template id
            - 'devices' (list) - list of devices

        :Returns:
           - 'result' (dict) - dictionary containing list of live polled values and icon urls
            {
                "message": "Successfully fetched.",
                "data": {
                    "devices": {
                        "115.114.15.188": {
                            "message": "Successfully fetch data for '115.114.15.188'.",
                            "value": "-62",
                            "icon": "/media/uploaded/icons/2014/08/19/blinking_dot.gif"
                        },
                        "121.244.195.36": {
                            "message": "Successfully fetch data for '121.244.195.36'.",
                            "value": "",
                            "icon": "/static/img/icons/wifi7.png"
                        },
                        "121.240.119.108": {
                            "message": "Successfully fetch data for '121.240.119.108'.",
                            "value": "",
                            "icon": "/static/img/icons/wifi7.png"
                        },
                        "115.112.161.68": {
                            "message": "Successfully fetch data for '115.112.161.68'.",
                            "value": "-61",
                            "icon": "/media/uploaded/icons/2014/08/19/blinking_dot.gif"
                        },
                        "121.240.226.243": {
                            "message": "Successfully fetch data for '121.240.226.243'.",
                            "value": "",
                            "icon": "/static/img/icons/wifi7.png"
                        },
                        "115.111.230.212": {
                            "message": "Successfully fetch data for '115.111.230.212'.",
                            "value": "",
                            "icon": "/static/img/icons/wifi7.png"
                        },
                        "ptp_sectorstation": {
                            "message": "Successfully fetch data for 'ptp_sectorstation'.",
                            "value": "",
                            "icon": "/static/img/icons/wifi7.png"
                        },
                        "14.141.83.236": {
                            "message": "Successfully fetch data for '14.141.83.236'.",
                            "value": "",
                            "icon": "/static/img/icons/wifi7.png"
                        },
                        "14.141.37.190": {
                            "message": "Successfully fetch data for '14.141.37.190'.",
                            "value": "",
                            "icon": "/static/img/icons/wifi7.png"
                        },
                        "14.141.111.132": {
                            "message": "Successfully fetch data for '14.141.111.132'.",
                            "value": "-56",
                            "icon": "/media/uploaded/icons/2014/08/19/blinking_dot.gif"
                        }
                    }
                },
                "success": 1
            }
    """

    def get(self, request):
        """Returns json containing live polling values and icon urls for bulk devices"""

        # converting 'json' into python object
        devices = eval(str(self.request.GET.get('devices', None)))
        ts_template_id = int(self.request.GET.get('ts_template', None))

        service = ""
        data_source = ""
        # Responsed form multiprocessing

        # selected thematic setting
        ts = ThematicSettings.objects.get(pk=ts_template_id)

        # getting live polling template
        lp_template_id = ThresholdConfiguration.objects.get(pk=ts.threshold_template.id).live_polling_template.id

        # getting service and data source form live polling settings
        try:
            service = LivePollingSettings.objects.get(pk=lp_template_id).service
            data_source = LivePollingSettings.objects.get(pk=lp_template_id).data_source

        except Exception as e:
            logger.info("No service and data source corresponding to this live pollig setting template.")

        # result dictionary to be returned as output of ap1
        result = {
            "success": 0,
            "message": "Failed to fetch live polling data.",
            "data": {
            }
        }

        result['data']['devices'] = dict()
        # get machines associated with current devices
        machine_list = []
        for device in devices:
            try:
                machine = Device.objects.get(device_name=device).machine.id
                machine_list.append(machine)
            except Exception as e:
                logger.info(e.message)
        machines = set(machine_list)

        try:
            for machine_id in machines:
                response_dict = {
                    'value': []
                }
                responses = []
                # live polling setting
                lp_template = LivePollingSettings.objects.get(pk=lp_template_id)

                # current machine devices
                current_devices_list = []

                for device_name in devices:
                    try:
                        device = Device.objects.get(device_name=device_name)
                        if device.machine.id == machine_id:
                            current_devices_list.append(str(device.device_name))
                    except Exception as e:
                        logger.info(e.message)

                site_instances_list = []
                for device_name in current_devices_list:
                    try:
                        device = Device.objects.get(device_name=device_name)
                        site_instances_list.append(device.site_instance.id)
                    except Exception as e:
                        logger.info(e.message)

                sites = set(site_instances_list)
                site_list = []
                for site_id in sites:
                    devices_in_current_site = []
                    for device_name in current_devices_list:
                        try:
                            device = Device.objects.get(device_name=device_name)
                            if device.site_instance.id == site_id:
                                devices_in_current_site.append(device.device_name)
                        except Exception as e:
                            logger.info(e.message)

                    # live polling data dictionary (payload for nocout.py api call)
                    lp_data = dict()
                    lp_data['mode'] = "live"
                    lp_data['device_list'] = devices_in_current_site
                    lp_data['service_list'] = [str(lp_template.service.name)]
                    lp_data['ds'] = [str(lp_template.data_source.name)]
                    site = SiteInstance.objects.get(pk=int(site_id))
                    site_list.append({
                        'username': site.username,
                        'password': site.password,
                        'port': site.web_service_port,
                        'machine': site.machine.machine_ip,
                        'site_name': site.name,
                        'lp_data': lp_data
                    })

                # Multiprocessing
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

                while True:
                    if not q.empty():
                        responses.append(q.get())
                    else:
                        break
                for entry in responses:
                    response_dict['value'].extend(entry.get('value'))

                # if response(r) is given by post request than process it further to get success/failure messages
                if len(response_dict):
                    devices_in_response = response_dict.get('value')

                    for device_dict in devices_in_response:
                        device_name = ""
                        device_value = ""

                        for device, val in device_dict.items():
                            device_name = device
                            try:
                                device_value = val[0]
                            except Exception as e:
                                device_value = ""
                                logger.info(e.message)

                        result['data']['devices'][device_name] = dict()

                        result['data']['devices'][device_name]['value'] = device_value

                        # threshold configuration for getting warning, critical comparison values
                        tc = ThresholdConfiguration.objects.get(pk=ts.threshold_template.id)

                        #default image to be loaded
                        image_partial = "icons/mobilephonetower10.png"

                        # comparing threshold values to get icon
                        try:
                            # icon as per thematic setting

                            if len(device_value):
                                # live polled value of device service
                                value = ast.literal_eval(str(device_value))
                                try:
                                    if (float(tc.range1_start)) <= (float(value)) <= (float(tc.range1_end)):
                                        icon_settings = eval(ts.icon_settings)
                                        for icon_setting in icon_settings:
                                            if 'icon_settings1' in icon_setting.keys():
                                                image_partial = str(icon_setting['icon_settings1'])
                                except Exception as e:
                                    logger.info(e.message)

                                try:
                                    if (float(tc.range2_start)) <= (float(value)) <= (float(tc.range2_end)):
                                        icon_settings = eval(ts.icon_settings)
                                        for icon_setting in icon_settings:
                                            if 'icon_settings2' in icon_setting.keys():
                                                image_partial = str(icon_setting['icon_settings2'])
                                except Exception as e:
                                    logger.info(e.message)

                                try:
                                    if (float(tc.range3_start)) <= (float(value)) <= (float(tc.range3_end)):
                                        icon_settings = eval(ts.icon_settings)
                                        for icon_setting in icon_settings:
                                            if 'icon_settings3' in icon_setting.keys():
                                                image_partial = str(icon_setting['icon_settings3'])
                                except Exception as e:
                                    logger.info(e.message)

                                try:
                                    if (float(tc.range4_start)) <= (float(value)) <= (float(tc.range4_end)):
                                        icon_settings = eval(ts.icon_settings)
                                        for icon_setting in icon_settings:
                                            if 'icon_settings4' in icon_setting.keys():
                                                image_partial = str(icon_setting['icon_settings4'])
                                except Exception as e:
                                    logger.info(e.message)

                                try:
                                    if (float(tc.range5_start)) <= (float(value)) <= (float(tc.range5_end)):
                                        icon_settings = eval(ts.icon_settings)
                                        for icon_setting in icon_settings:
                                            if 'icon_settings5' in icon_setting.keys():
                                                image_partial = str(icon_setting['icon_settings5'])
                                except Exception as e:
                                    logger.info(e.message)

                                try:
                                    if (float(tc.range6_start)) <= (float(value)) <= (float(tc.range6_end)):
                                        icon_settings = eval(ts.icon_settings)
                                        for icon_setting in icon_settings:
                                            if 'icon_settings6' in icon_setting.keys():
                                                image_partial = str(icon_setting['icon_settings6'])
                                except Exception as e:
                                    logger.info(e.message)

                                try:
                                    if (float(tc.range7_start)) <= (float(value)) <= (float(tc.range7_end)):
                                        icon_settings = eval(ts.icon_settings)
                                        for icon_setting in icon_settings:
                                            if 'icon_settings7' in icon_setting.keys():
                                                image_partial = str(icon_setting['icon_settings7'])
                                except Exception as e:
                                    logger.info(e.message)

                                try:
                                    if (float(tc.range8_start)) <= (float(value)) <= (float(tc.range8_end)):
                                        icon_settings = eval(ts.icon_settings)
                                        for icon_setting in icon_settings:
                                            if 'icon_settings8' in icon_setting.keys():
                                                image_partial = str(icon_setting['icon_settings8'])
                                except Exception as e:
                                    logger.info(e.message)

                                try:
                                    if (float(tc.range9_start)) <= (float(value)) <= (float(tc.range9_end)):
                                        icon_settings = eval(ts.icon_settings)
                                        for icon_setting in icon_settings:
                                            if 'icon_settings9' in icon_setting.keys():
                                                image_partial = str(icon_setting['icon_settings9'])
                                except Exception as e:
                                    logger.info(e.message)

                                try:
                                    if (float(tc.range10_start)) <= (float(value)) <= (float(tc.range10_end)):
                                        icon_settings = eval(ts.icon_settings)
                                        for icon_setting in icon_settings:
                                            if 'icon_settings10' in icon_setting.keys():
                                                image_partial = str(icon_setting['icon_settings10'])
                                except Exception as e:
                                    logger.info(e.message)
                            # image url
                            img_url = "media/" + str(image_partial) if "uploaded" in str(image_partial) else "static/img/" + str(image_partial)

                            # icon to be send in response
                            icon = str(img_url)
                        except Exception as e:
                            icon = str(image_partial)
                            logger.info(e.message)

                        result['data']['devices'][device_name]['icon'] = icon

                        # if response_dict doesn't have key 'success'
                        if not response_dict.get('success'):
                            logger.info(response_dict.get('error_message'))
                            result['data']['devices'][device_name]['message'] = "Failed to fetch data for '%s'." % \
                                                                                device_name
                        else:
                            result['data']['devices'][device_name]['message'] = "Successfully fetch data for '%s'." % \
                                                                                device_name
            result['success'] = 1
            result['message'] = "Successfully fetched."
        except Exception as e:
            result['message'] = e.message
            logger.info(e)
        return HttpResponse(json.dumps(result))


def nocout_live_polling(q, site):
    response_dict = {}

    # url for nocout.py
    # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
    # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
    url = "http://{}:{}@{}:{}/{}/check_mk/nocout_live.py".format(site.get('username'),
                                                                 site.get('password'),
                                                                 site.get('machine'),
                                                                 site.get('port'),
                                                                 site.get('site_name'))

    # encoding 'lp_data'
    encoded_data = urllib.urlencode(site.get('lp_data'))

    # sending post request to nocout device app to fetch service live polling value
    try:
        r = requests.post(url, data=encoded_data)
        response_dict = ast.literal_eval(r.text)
        if len(response_dict):
            q.put(response_dict)
    except Exception as e:
        logger.info(e.message)




