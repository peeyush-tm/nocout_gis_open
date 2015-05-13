import datetime
from dateutil import tz

from random import randint

from HTMLParser import HTMLParser
import htmlentitydefs

from django.db import connections
from nocout.settings import DATE_TIME_FORMAT

from nocout.settings import DATE_TIME_FORMAT, USE_TZ

date_handler = lambda obj: obj.strftime(DATE_TIME_FORMAT) if isinstance(obj, datetime.datetime) else None

#for managing the slave-master connections
from django.conf import settings
import socket
#http://stackoverflow.com/questions/26608906/django-multiple-databases-fallback-to-master-if-slave-is-down

#https://github.com/benjamin-croker/loggy/blob/master/loggy.py
import inspect
from functools import wraps
# import functools
# def log(fn):
#     @functools.wraps(fn)
#     def decorated(*args, **kwargs):
#         # get the names of all the args
#         arguments = inspect.getcallargs(fn, *args, **kwargs)
#
#         logging.debug("function '{}' called by '{}' with arguments:\n{}".format(
#                       fn.__name__,
#                       inspect.stack()[1][3],
#                       arguments))
#         result = fn(*args, **kwargs)
#         logging.debug("result: {}\n".format(result))
#
#     return decorated
#https://github.com/benjamin-croker/loggy/blob/master/loggy.py

#logging the performance of function
import logging
log = logging.getLogger(__name__)
#logging the performance of function

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


project_group_role_dict_mapper={
    'admin':'group_admin',
    'operator':'group_operator',
    'viewer':'group_viewer',
}


if getattr(settings, 'PROFILE'):
    from line_profiler import LineProfiler as LLP
    from memory_profiler import LineProfiler as MLP
    from memory_profiler import show_results


# #profiler
def time_it(debug=getattr(settings, 'PROFILE')):
        def decorator(fn):
            def wrapper(*args, **kwargs):
                st = datetime.datetime.now()
                if debug:
                    log.debug("+++"*40)
                    log.debug("START     \t\t\t: { " + fn.__name__ + " } : ")
                    try:
                        #check the module calling the function
                        log.debug("          \t\t\t: function '{}' called by '{}' : '{}'".format(
                                      fn.__name__,
                                      inspect.stack()[1][3],
                                      inspect.stack()[1][1],
                                      )
                        )
                    except:
                        pass
                    #check the module calling the function
                    profile_type = getattr(settings, 'PROFILE_TYPE')
                    if profile_type == 'line':
                        profiler = LLP()
                        profiled_func = profiler(fn)
                    else:
                        profiler = MLP()
                        profiled_func = profiler(fn)
                    try:
                        result = profiled_func(*args, **kwargs)
                    finally:
                        if profile_type == 'line':
                            profiler.print_stats()
                        else:
                            show_results(profiler)
                else:
                    result = fn(*args, **kwargs)
                end = datetime.datetime.now()
                if debug:
                    elapsed = end - st
                    log.debug("TIME TAKEN\t\t\t: [{}".format(divmod(elapsed.total_seconds(), 60)))
                    log.debug("END       \t\t\t: { " + fn.__name__ + " } : ")
                    log.debug("+++"*40)

                return result
            return wrapper
        return decorator


#http://stackoverflow.com/questions/26608906/django-multiple-databases-fallback-to-master-if-slave-is-down
#defining utility to exatly choose a database to query from
#django routers are of no use
#we will pass in the machine name
#we will test the connection
#and we will return the results of the database to be used

import random


@time_it()
def nocout_db_router(db='default', levels=0):
    """

    :param db: pass the name for the database
    :param levels: number of slaves available
    :return:the database to be queried on
    """
    db_slave_up = list()
    #can choose from master db as well
    db_slave_up.append(db)
    db_slave = db + "_slave"
    if levels and levels != -1:
        for x in range(1, levels):
            db_slave = db + "_slave_" + str(x)
            if test_connection_to_db(db_slave):
                db_slave_up.append(db_slave)
    elif levels == -1:
        return db
    else:
        if test_connection_to_db(db_slave):
                db_slave_up.append(db_slave)

    return random.choice(db_slave_up)


@time_it()
def nocout_query_results(query_set=None, using='default', levels=0):
    """

    :param query_set: query set to be executed
    :param using: the db alias
    :param levels: levels of slaves default = 0, that is one slave is present, -1 means no slave
    :return:
    """
    if query_set:
        #choose a random database : slave // master
        if levels == -1:
            return query_set.using(alias=using)
        else:
            db = nocout_db_router(db=using, levels=levels)
            return query_set.using(alias=db)
    return None


#http://stackoverflow.com/questions/26608906/django-multiple-databases-fallback-to-master-if-slave-is-down
def test_connection_to_db(database_name):
    """

    :param database_name:
    :return:
    """
    try:
        db_definition = getattr(settings, 'DATABASES')[database_name]
        #if it gets a socket connection in 2 seconds
        s = socket.create_connection((db_definition['HOST'], db_definition['PORT']), 5)
        #if it gets a socket connection in 2 seconds
        s.close()
        return True
    except Exception as e:
        #general exception handelling
        #because connection might not exists in settings file
        return False


@time_it()
def fetch_raw_result(query, machine='default'):
    """
    django raw query does not get result in a single call, it iterates and calls the same query a lot of time
    which can be optmised if we pre fetch the results

    :param query: query to execute
    :param machine: machine name
    :return:the data fetched in form of a dictionary
    """
    db = machine
    db_slave = db + "_slave"
    if test_connection_to_db(database_name=db_slave):
        db = db_slave

    cursor = connections[db].cursor()
    cursor.execute(query)

    return dict_fetchall(cursor)


def dict_fetchall(cursor):
    """
    https://docs.djangoproject.com/en/1.6/topics/db/sql/
    return the cursor in dictionary format

    :param cursor: data base cursor
    :return: dictioanry of the rows
    """

    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def format_value(format_this, type_of=None):
    """

    :param format_this:
    :return:
    """
    if format_this:
        try:
            if not type_of:
                return format_this if format_this else 'NA'
            elif type_of == 'frequency_color':
                return format_this if format_this else 'rgba(74,72,94,0.58)'
            elif type_of == 'frequency_radius':
                return format_this if format_this else 0.5
            elif type_of == 'integer':
                return format_this if format_this else 0
            elif type_of == 'antenna':
                return format_this if format_this else 'vertical'
            elif type_of == 'random':
                return format_this if format_this else randint(40,70)
            elif type_of == 'icon':
                if len(str(format_this)) > 5:
                    img_url = str("media/"+ str(format_this)) \
                        if "uploaded" in str(format_this) \
                        else "static/img/" + str(format_this)
                    return img_url
                else:
                    return "static/img/icons/mobilephonetower10.png"
            elif type_of == 'mac':
                return format_this.upper() if format_this else 'NA'
            elif type_of == 'date':
                return str(format_this)
            elif type_of == 'epoch':
                return date_handler(format_this)
        except:
            return 'NA'
    else:
        return 'NA'

    return 'NA'


###caching
from django.core.cache import cache


# get the cache key for storage
def cache_get_key(*args, **kwargs):
    import hashlib

    serialise = []
    for arg in args:
        serialise.append(str(arg))
    for key, arg in kwargs.items():
        serialise.append(str(key))
        serialise.append(str(arg))
    key = hashlib.md5("".join(serialise)).hexdigest()
    return key


#decorator for caching functions
def cache_for(time):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            debug=getattr(settings, 'PROFILE')
            st = datetime.datetime.now()
            if debug:
                log.debug("---"*40)
                log.debug("FROM CACHE       \t: START : { " + fn.__name__ + " } : ")
            key = cache_get_key(fn.__name__, *args, **kwargs)
            result = cache.get(key)
            if not result:
                if debug:
                    log.debug("FUNCTION CALL\t: START : { " + fn.__name__ + " } : ")
                    #check the module calling the function
                    try:
                        #check the module calling the function
                        log.debug("          \t\t\t: function '{}' called by '{}' : '{}'".format(
                                      fn.__name__,
                                      inspect.stack()[1][3],
                                      inspect.stack()[1][1],
                                      )
                        )
                    except:
                        pass
                    #check the module calling the function
                    profile_type = getattr(settings, 'PROFILE_TYPE')
                    if profile_type == 'line':
                        profiler = LLP()
                        profiled_func = profiler(fn)
                    else:
                        profiler = MLP()
                        profiled_func = profiler(fn)
                    try:
                        result = profiled_func(*args, **kwargs)
                    finally:
                        if profile_type == 'line':
                            profiler.print_stats()
                        else:
                            show_results(profiler)
                    cache.set(key, result, time)
                else:
                    result = fn(*args, **kwargs)
                    cache.set(key, result, time)

                if debug:
                    end = datetime.datetime.now()
                    elapsed = end - st
                    log.debug("TIME TAKEN   \t:       : [{}".format(divmod(elapsed.total_seconds(), 60)))
                    log.debug("FUNCTION CALL\t: END   : { " + fn.__name__ + " } : ")
            if debug:
                end = datetime.datetime.now()
                elapsed = end - st
                log.debug("TIME TAKEN       \t:       : [{}".format(divmod(elapsed.total_seconds(), 60)))
                log.debug("FROM CACHE       \t: END   : { " + fn.__name__ + " } : ")
                log.debug("---"*40)
            return result

        return wrapper

    return decorator


def non_cached_all_gis_inventory(monitored_only=False, technology=None, type_rf=None, bs_id=None):
    """

    :param monitored_only: true false
    :param technology: technology name
    :param type_rf: sector, ss, bh
    :param bs_id: id of the base station
    :return: live cached result for the bs or for complete inventory
    """
    query = query_all_gis_inventory(monitored_only, technology, type_rf, bs_id=bs_id)
    return fetch_raw_result(query)


@cache_for(300)  #caching GIS inventory
def cached_all_gis_inventory(monitored_only=False, technology=None, type_rf=None, bs_id=None, device_list=None):
    """


    :param monitored_only: true false
    :param technology: technology name
    :param type_rf: sector, ss, bh
    :param bs_id: id of the base station
    :param device_list: list of device names
    :return: cached result for the bs or for complete inventory
    """
    query = query_all_gis_inventory(monitored_only, technology, type_rf, bs_id=bs_id, device_list=device_list)
    return fetch_raw_result(query)


## Function with imporved GIS API query
def query_all_gis_inventory(monitored_only=False, technology=None, type_rf=None, bs_id=None, device_list=None):
    """

    :param monitored_only: True or False
    :param technology: Technology Name
    :param type_rf: sector or ss or backhaul
    :param bs_id: base station ID
    :param device_list: list of device names
    :return: query for gis
    """
    added_device = " "

    tech = " "

    rf_tech = " "

    if monitored_only:
        added_device = "where device.is_added_to_nms = 1 "

        if technology:
            tech = " and technology.name = '{0}'".format(technology)
            if type_rf != 'bh':
                rf_tech = " where SECTOR_TECH = '{0}' and SS_TECH = '{0}' ".format(technology)

    elif not monitored_only:
        if technology:
            tech = " where technology.name = '{0}'".format(technology)
            if type_rf != 'bh':
                rf_tech = " where SECTOR_TECH = '{0}' ".format(technology)

    else:
        added_device = ""
        tech = ""
        rf_tech = " "

    added_device += tech

    if type_rf == 'sector':
        rf_tech = " where SECTOR_TECH = '{0}' ".format(technology)
    elif type_rf == 'ss':
        rf_tech = " where SECTOR_TECH = '{0}' and SS_TECH = '{0}' ".format(technology)
    elif type_rf == 'bh':
        rf_tech = " where BHTECH = '{0}' ".format(technology)
    else:
        pass

    where_bs = ''
    if bs_id:
        where_bs = ' where basestation.id  = {0} '.format(bs_id)

    gis = '''
        select * from (
                select  basestation.id as BSID,
                        basestation.name as BSNAME,
                        basestation.alias as BSALIAS,
                        basestation.bs_site_id as BSSITEID,
                        basestation.bs_site_type as BSSITETYPE,

                        device.ip_address as BSSWITCH,

                        basestation.bs_type as BSTYPE,
                        basestation.bh_bso as BSBHBSO,
                        basestation.hssu_used as BSHSSUUSED,
                        basestation.hssu_port as BSHSSUPORT,
                        basestation.latitude as BSLAT,
                        basestation.longitude as BSLONG,

                        basestation.infra_provider as BSINFRAPROVIDER,
                        basestation.gps_type as BSGPSTYPE,
                        basestation.building_height as BSBUILDINGHGT,
                        basestation.tower_height as BSTOWERHEIGHT,
                        basestation.tag1 as BSTAG1,
			            basestation.tag2 as BSTAG2,
                        basestation.maintenance_status as BSMAINTENANCESTATUS,

                        city.city_name as BSCITY,
                        state.state_name as BSSTATE,
                        country.country_name as BSCOUNTRY,

                        basestation.address as BSADDRESS,

                        backhaul.id as BHID,
                        sector.id as SID
                        
                from inventory_basestation as basestation
                left join inventory_sector as sector
                on sector.base_station_id = basestation.id
                left join inventory_backhaul as backhaul
                on backhaul.id = basestation.backhaul_id 
                left join device_country as country
                on country.id = basestation.country_id
                left join device_city as city
                on city.id = basestation.city_id
                left join device_state as state
                on state.id = basestation.state_id
                left join device_device as device
                on device.id = basestation.bs_switch_id
{2}
            )as bs_info
left join (
    select * from (select

        sector.id as SECTOR_ID,
        sector.name as SECTOR_NAME,
        sector.alias as SECTOR_ALIAS,
        sector.sector_id as SECTOR_SECTOR_ID,
        sector.base_station_id as SECTOR_BS_ID,
        sector.mrc as SECTOR_MRC,
        sector.dr_site as SECTOR_DR,
        sector.tx_power as SECTOR_TX,
        sector.rx_power as SECTOR_RX,
        sector.rf_bandwidth as SECTOR_RFBW,
        sector.frame_length as SECTOR_FRAME_LENGTH,
        sector.cell_radius as SECTOR_CELL_RADIUS,
        sector.modulation as SECTOR_MODULATION,
        sector.planned_frequency as SECTOR_PLANNED_FREQUENCY,

        technology.name as SECTOR_TECH,
        vendor.name as SECTOR_VENDOR,
        devicetype.name as SECTOR_TYPE,
        devicetype.device_icon as SECTOR_ICON,
        devicetype.device_gmap_icon as SECTOR_GMAP_ICON,

        device.id as SECTOR_CONF_ON_ID,
        device.device_name as SECTOR_CONF_ON,
        device.device_name as SECTOR_CONF_ON_NAME,
        device.device_alias as SECTOR_CONF_ON_ALIAS,
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
        frequency.value as SECTOR_FREQUENCY,

        dport.name as SECTOR_PORT,

        drd.id as DR_CONF_ON_ID,
        drd.device_name as DR_CONF_ON,
        drd.ip_address as DR_CONF_ON_IP

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
        ) left join ( device_deviceport as dport )
        on (
            dport.id = sector.sector_configured_on_port_id
        ) left join (
			inventory_sector as dr,
            device_device as drd
        )
        on (
			dr.id = sector.id
            and
            drd.id = dr.dr_configured_on_id
        )
{0}
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
            devicetype.name as SS_TYPE,
            devicetype.name as SSDEVICETYPE,
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
{0}
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

                bh_info.BH_DEVICE_ID as BH_DEVICE_ID,
                bh_info.BHCONF as BHCONF,
                bh_info.BHCONF_IP as BHCONF_IP,
                bh_info.BHTECH as BHTECH,
                bh_info.BHTYPE as BHTYPE,
                bh_info.BH_AGGR_PORT as BH_AGGR_PORT,
                bh_info.BH_DEVICE_PORT as BH_DEVICE_PORT,

				POP,
                POP_IP,
				POP_TECH,
				POP_TYPE,
				AGGR,
                AGGR_IP,
				AGGR_TECH,
                AGGR_TYPE,
				BSCONV,
                BSCONV_IP,
				BSCONV_TECH,
                BSCONV_TYPE

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
                backhaul.aggregator_port as BH_AGGR_PORT,
                backhaul.switch_port as BH_DEVICE_PORT,

                device.id as BH_DEVICE_ID,
                device.device_name as BHCONF,
                device.ip_address as BHCONF_IP,
                tech.name as BHTECH,
                devicetype.name as BHTYPE

        from inventory_backhaul as backhaul
        join (
            device_device as device,
            device_devicetype as devicetype,
            device_devicetechnology as tech
        )
        on (
            device.id = backhaul.bh_configured_on_id
            and
            tech.id = device.device_technology
            and
            devicetype.id = device.device_type
        )

        ) as bh_info left join (
                select backhaul.id as BHID,
						device.device_name as POP,
						device.ip_address as POP_IP,
						devicetype.name as POP_TYPE,
						tech.name as POP_TECH
				from inventory_backhaul
				as backhaul
                left join (
                    device_device as device,
					device_devicetype as devicetype,
					device_devicetechnology as tech
                )
                on (
                    device.id = backhaul.pop_id
					and
					tech.id = device.device_technology
					and
					devicetype.id = device.device_type
                )
        ) as pop_info
        on (bh_info.BHID = pop_info.BHID)
        left join ((
                select backhaul.id as BHID,
						device.device_name as BSCONV,
						device.ip_address as BSCONV_IP,
						devicetype.name as BSCONV_TYPE,
						tech.name as BSCONV_TECH
				from inventory_backhaul as backhaul
                left join (
                    device_device as device,
					device_devicetype as devicetype,
					device_devicetechnology as tech
                )
                on (
                    device.id = backhaul.bh_switch_id
					and
					tech.id = device.device_technology
					and
					devicetype.id = device.device_type
                )
        ) as bscon_info
        ) on (bh_info.BHID = bscon_info.BHID)
        left join ((
                select backhaul.id as BHID,
					device.device_name as AGGR,
					device.ip_address as AGGR_IP,
					devicetype.name as AGGR_TYPE,
					tech.name as AGGR_TECH
				from inventory_backhaul as backhaul
                left join (
                    device_device as device,
					device_devicetype as devicetype,
					device_devicetechnology as tech
                )
                on (
                    device.id = backhaul.aggregator_id
					and
					tech.id = device.device_technology
					and
					devicetype.id = device.device_type
                )
        ) as aggr_info
        ) on (bh_info.BHID = aggr_info.BHID)

    ) as bh
on
    (bh.BHID = bs_info.BHID)

{1}
 group by BSID,SECTOR_ID,CID 

        ;
        '''.format(added_device, rf_tech, where_bs)
    return gis


def convert_utc_to_local_timezone(datetime_obj=None):
    """ Convert datetime object timezone from 'utc' to 'local'

        Parameters:
            - datetime_obj ('datetime.datetime') - timestamp as datetime object for e.g. 2014-12-25 12:26:00+00:00

        Returns:
           - output (str) - output as a timestamp string for e.g. 12/25/14 (Dec) 17:56:03 (05:56 PM)

    """
    if USE_TZ:
        # get 'utc' timezone
        from_zone = tz.tzutc()

        # get 'local' timezone
        to_zone = tz.tzlocal()

        # output timestamp
        output = datetime_obj

        if output:
            try:
                # modify timezone info in datetime object to 'utc'
                output = output.replace(tzinfo=from_zone)

                # convert timezone from 'utc' to 'local'
                output = output.astimezone(to_zone)

                # format datetime string
                output = output.strftime(DATE_TIME_FORMAT)
            except Exception as e:
                log.error("Timezone conversion not possible. Exception: {0}".format(e.message))
    else:
        return datetime_obj.strftime(DATE_TIME_FORMAT)

    return output


def indexed_query_set(query_set, indexes, values, is_raw=False):
    """
    # since query sets are not evaluated by default, we will evaluate the query set
    # index the query set on a few attributes
    # and return a disctionary if indexes
    :param query_set: the original query set and subclasses : Query set must be complete and must be having a db
    :param indexes: required indexes for indexing the query set
    :param values: required values of the query set
    :return: indexed results
    """
    if set(indexes).issubset(values):
        indexed_result = dict()
        if not is_raw:
            if query_set.exists():
                if query_set.values(*indexes).exists():  # check if the desired indexes exists
                    for qs in query_set.values(*values):  # check if the desired values exists
                        index = tuple(qs[x] for x in indexes)
                        if index not in indexed_result:
                            indexed_result[index] = list()
                        indexed_result[index].append(qs)
            else:
                return False

        else:
            # we have raw query results which are
            # list of dictionatry
            if len(query_set):
                for qs in query_set:
                    index = tuple(qs[x] for x in indexes)
                    if index not in indexed_result:
                        indexed_result[index] = list()
                    indexed_result[index].append(qs)
            else:
                return False
        return indexed_result
    else:
        return False


def check_item_is_list(items):
    """

    :param items: any item to check
    :return: list of items
    """
    if type(items) == type(list()):
        return items
    elif type(items) == type(set()):
        return list(items)
    else:
        return [items]


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = [ ]

    def handle_data(self, d):
        self.result.append(d)

    def handle_charref(self, number):
        codepoint = int(number[1:], 16) if number[0] in (u'x', u'X') else int(number)
        self.result.append(unichr(codepoint))

    def handle_entityref(self, name):
        codepoint = htmlentitydefs.name2codepoint[name]
        self.result.append(unichr(codepoint))

    def get_text(self):
        return u''.join(self.result)


def html_to_text(html):
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()

# Disable Signals for loaddata command Django
# http://stackoverflow.com/questions/15624817/have-loaddata-ignore-or-disable-post-save-signals


def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs['raw']:
            return
        signal_handler(*args, **kwargs)
    return wrapper