from mysql_connection import mysql_conn
from pprint import pformat
from operator import itemgetter
from nocout_logger import nocout_log

logger = nocout_log()

pmp_ss_bs_checks = ['cambium_ul_jitter', 'cambium_reg_count', 'cambium_rereg_count', 'cambium_ul_rssi']

bulkwalk_hosts = [(['snmp-v2'], ['@all'])]

# ping_levels = [({'loss': (80, 100), 'packets': 10, 'rta': (1500, 3000), 'timeout': 20}, [u'Radwin2KSS'], ['@all'], {})]

ping_levels_db = list()


default_snmp_ports = [
    (161, ['Radwin2KBS'], ['@all']),
    (161, ['Radwin2KSS'], ['@all']),
    (161, ['CanopyPM100AP'], ['@all']),
    (161, ['CanopyPM100SS'], ['@all']),
    (161, ['CanopySM100AP'], ['@all']),
    (161, ['CanopySM100SS'], ['@all']),
]

snmp_ports_db = list()

# # will calculate the commnities

default_snmp_communities = [
    ('public', ['Radwin2KBS'], ['@all']),
    ('public', ['Radwin2KSS'], ['@all']),
    ('Canopy', ['CanopyPM100AP'], ['@all']),
    ('Canopy', ['CanopyPM100SS'], ['@all']),
    ('Canopy', ['CanopySM100AP'], ['@all']),
    ('Canopy', ['CanopySM100SS'], ['@all']),
]

snmp_communities_db = list()

## will calculate the commnities

extra_service_conf = {}

extra_service_conf['retry_check_interval'] = []

extra_service_conf['max_check_attempts'] = []

extra_service_conf['normal_check_interval'] = [
    (5, [], ['@all'], 'Check_MK'),
]

wimax_mod_services = ['wimax_modulation_dl_fec', 'wimax_modulation_ul_fec']


def prepare_hosts_file():
    all_hosts, ipaddresses, host_attributes = [], {}, {}
    wimax_bs_devices, cambium_bs_devices = [], []
    # This file contains device names, to be updated in configuration db
    open('/omd/sites/master_UA/etc/check_mk/conf.d/wato/hosts.txt', 'w').close()
    #try:
    all_hosts, ipaddresses, host_attributes, wimax_bs_devices, \
            cambium_bs_devices = make_BS_data()
    #except Exception, exp:
    #   logger.error('Exception in make_BS_data: ' + pformat(exp))
    #try:
    make_SS_data(all_hosts, ipaddresses, host_attributes)
    #except Exception, exp:
    #   logger.error('Exception in make_SS_data: ' + pformat(exp))
    write_hosts_file(all_hosts, ipaddresses, host_attributes)

    return (wimax_bs_devices, cambium_bs_devices)


def make_BS_data(all_hosts=[], ipaddresses={}, host_attributes={}):
    db = mysql_conn()
    query = """
    select 
    DISTINCT(device_device.ip_address),
    device_device.device_name,
    device_devicetype.name,
    device_device.mac_address,
    device_device.ip_address,
    device_devicetype.agent_tag,
    inventory_sector.name,
    site_instance_siteinstance.name,
    device_device.device_alias,
    inventory_sector.dr_site,
    inventory_sector.dr_configured_on_id,
    device_devicetechnology.name
    from device_device inner join (device_devicetechnology, device_devicemodel, device_devicetype, machine_machine, site_instance_siteinstance, inventory_sector)
    on (
    device_devicetype.id = device_device.device_type and
    device_devicetechnology.id = device_device.device_technology and
    device_devicemodel.id = device_device.device_model and
    machine_machine.id = device_device.machine_id and
    site_instance_siteinstance.id = device_device.site_instance_id and
    inventory_sector.sector_configured_on_id = device_device.id
    )
    where device_device.is_deleted=0 and device_devicetechnology.name in ('WiMAX', 'P2P', 'PMP') and device_devicetype.name in ('Radwin2KBS', 'CanopyPM100AP', 'CanopySM100AP', 'StarmaxIDU');
    """
    # host row for devices
        #host name | device type | mac | parent _ name | wan | prod | agent tags | site | wato
    # host row for dr-enabled wimax devices
    #host name | device type | mac | parent _ name | dr: dr_host_name | wan | prod | agent tags | site | wato
    cur = db.cursor() 
    cur.execute(query) 
    data = cur.fetchall() 
    # Removing duplicate entries for devices having more than one Ckt-ids
    unq_device_data = []
    device_ips = set(map(lambda e: e[0], data))
    for i, e in enumerate(data):
        if e[0] in device_ips:
            unq_device_data.append(e)
            device_ips.remove(e[0])
    data = unq_device_data
    cur.close() 
    db.close()
    processed = []
    dr_en_devices = sorted(filter(lambda e: e[9] and e[9].lower() == 'yes' and e[10], data), key=itemgetter(10))
    #print 'dr_en_devices --'
    #print len(dr_en_devices)
    data = filter(lambda e: e[9] == '' or (e[9] and e[9].lower() == 'no'), data)
    # dr_enabled devices ids
    # dr_configured_on_devices would be treated as master device
    dr_configured_on_ids = map(lambda e: e[10], dr_en_devices)
    #print '--dr_configured_on_ids----'
    #print len(dr_configured_on_ids)
    # Find dr_configured on devices from device_device table
    dr_configured_on_devices = get_dr_configured_on_devices(device_ids=dr_configured_on_ids)
    final_dr_devices = zip(dr_en_devices, dr_configured_on_devices)
    #print '-- final_dr_devices --'
    #print len(final_dr_devices)
    hosts_only = open('/omd/sites/master_UA/etc/check_mk/conf.d/wato/hosts.txt', 'a')

    for entry in final_dr_devices:
        if (str(entry[0][1]) in processed) or (str(entry[1][0]) in processed):
            continue
        hosts_only.write(str(entry[0][1] + '\n'))
        hosts_only.write(str(entry[1][0] + '\n'))
        processed.append(str(entry[0][1]))
        processed.append(str(entry[1][0]))
        # Append the `site_name` for slave dr device, we need them in active checks
        # We believe that dr master/slave pair is being monitored on same site
        # Entries for master dr device
        dr_device_entry = str(entry[0][1]) + '|' + str(entry[0][2]) + '|' + str(entry[0][3]) + \
                '| dr: ' + str(entry[1][0]) + '|dr_master|wan|prod|' + str(entry[0][5]) + '|site:' + str(entry[0][7]) + '|wato|//'
        all_hosts.append(dr_device_entry)
        ipaddresses.update({str(entry[0][1]): str(entry[0][0])})
        host_attributes.update({str(entry[0][1]):
            {
                'alias': entry[0][8],
                    'contactgroups': (True, ['all']),
                'site': str(entry[0][7]),
                'tag_agent': str(entry[0][5])
                }
            })
        # Entries for slave dr device
        # slave dr device stands for device which got its entry as `dr_configured_on_id` in
        # inventory_sector table
        dr_device_entry = str(entry[1][0]) + '|' + str(entry[0][2]) + '|' + str(entry[1][2]) + \
                '| dr: ' + str(entry[0][1]) + '|dr_slave|wan|prod|' + str(entry[0][5]) + '|site:' + str(entry[0][7]) + '|wato|//'
        all_hosts.append(dr_device_entry)
        ipaddresses.update({str(entry[1][0]): str(entry[1][1])})
        host_attributes.update({str(entry[1][0]):
            {
                'alias': entry[1][3],
                    'contactgroups': (True, ['all']),
                'site': str(entry[0][7]),
                'tag_agent': str(entry[0][5])
                }
            })


    for device in data:
        if  str(device[1]) in processed:
            continue
        hosts_only.write(str(device[1]) + '\n')
        processed.append(str(device[1]))
        entry = str(device[1]) + '|' + str(device[2]) + '|' + str(device[3]).lower() + \
            '|wan|prod|' + str(device[5]) + '|site:' + str(device[7]) + '|wato|//' 
        all_hosts.append(entry) 
        ipaddresses.update({str(device[1]): str(device[0])})
        host_attributes.update({ str(device[1]): { 
            'alias': str(device[8]), 
            'contactgroups': (True, ['all']),
            'site': str(device[7]),
            'tag_agent': str(device[5])
            }})
    hosts_only.close()


    # Get the wimax BS devices (we need them for active checks)
    L0 = map(lambda e: (e[1], e[7]), filter(lambda e: e[11].lower() == 'wimax', data))
    L1 = map(lambda e: (e[1], e[7]), dr_en_devices)
    #L2 = zip(map(lambda e: e[0], dr_configured_on_devices), map(lambda e: e[1], L1))
    wimax_bs_devices = L0 + L1
    # Get the Cambium BS devices (we need them for active checks)
    # Since, as of now, we have only Cambium devices in pmp technology
    cambium_bs_devices = map(lambda e: (e[1], e[7]), filter(lambda e: e[11].lower() == 'pmp', data))

    return (all_hosts, ipaddresses, host_attributes, wimax_bs_devices, cambium_bs_devices)


def get_dr_configured_on_devices(device_ids=[]):
    """
    dr_configured_on_devices would be treaed as
    master device in this case
    """
    dr_configured_on_devices = []
    if device_ids:
        query = "SELECT device_name, ip_address, mac_address, device_alias, id \
                FROM device_device WHERE id IN %s" % pformat(tuple(device_ids))
        db = mysql_conn()
        cur = db.cursor()
        cur.execute(query)
        dr_configured_on_devices = cur.fetchall()
        cur.close()
        db.close()
    return dr_configured_on_devices


def write_hosts_file(all_hosts, ipaddresses, host_attributes):
    with open('/omd/sites/master_UA/etc/check_mk/conf.d/wato/hosts.mk', 'w') as f:
        f.write("# encoding: utf-8\n\n")
        f.write("\nhost_contactgroups += []\n\n\n")
        f.write("all_hosts += %s\n" % pformat(all_hosts))
        f.write("\n\n# Explicit IP Addresses\n")
        f.write("ipaddresses.update(%s)\n\n" % pformat(ipaddresses))
        f.write("host_attributes.update(\n%s)\n" % pformat(host_attributes))

    
    ## Write DR enabled devices to seperate .mk file
    #with open('/omd/sites/master_UA/etc/check_mk/conf.d/wato/wimax_dr_en.mk', 'w') as f:
    #   f.write("# encoding: utf-8\n\n")
    #   f.write("\nhost_contactgroups += []\n\n\n")
    #   f.write("all_hosts += %s\n" % pformat(dr_all_hosts))
    #   f.write("\n\n# Explicit IP Addresses\n")
    #   f.write("ipaddresses.update(%s)\n\n" % pformat(dr_ipaddresses))
    #   f.write("host_attributes.update(\n%s)\n" % pformat(dr_host_attributes))


def make_SS_data(all_hosts, ipaddresses, host_attributes):
    db = mysql_conn()
    query = """
        select 
    distinct(SSIP),
    original.device_name as BSNAME, 
    original.mac_address as BSMAC,
    original.ip_address as BSIP, 
    SSNAME, 
    SSMAC, 
    DEVICETYPE, 
    TAG, 
    SITE,
    SUBSTATION, 
    CIRCUIT,
    SECTOR,
        original.device_alias as BSALIAS,
        SSALIAS
    from device_device as original
    inner join (
    (select 
    device_device.device_name SSNAME,
        device_device.device_alias as SSALIAS,
    device_devicetype.name as DEVICETYPE,
    device_device.mac_address as SSMAC,
    device_device.ip_address as SSIP,
    device_devicetype.agent_tag as TAG,
    inventory_substation.name as SUBSTATION,
    site_instance_siteinstance.name as SITE,
    inventory_circuit.circuit_id as CIRCUIT,
    inventory_sector.name SECTOR,
    inventory_sector.sector_configured_on_id as matcher
    from device_device 
    inner join (device_devicetechnology, device_devicemodel, device_devicetype, machine_machine, site_instance_siteinstance, inventory_substation, inventory_circuit, inventory_sector)
    on (
    device_devicetype.id = device_device.device_type and
    device_devicetechnology.id = device_device.device_technology and
    device_devicemodel.id = device_device.device_model and
    machine_machine.id = device_device.machine_id and
    site_instance_siteinstance.id = device_device.site_instance_id and
    inventory_substation.device_id = device_device.id and
    inventory_circuit.sub_station_id = inventory_substation.id and
    !isnull(inventory_circuit.sector_id) and
    inventory_sector.id = inventory_circuit.sector_id
    )
    where device_device.is_deleted=0 and device_devicetechnology.name in ('WiMAX', 'P2P', 'PMP') and device_devicetype.name in ('Radwin2KSS', 'CanopyPM100SS', 'CanopySM100SS', 'StarmaxSS')) as dupli
    )
    on (original.id = dupli.matcher)
        """
        #host name | device type | mac | parent _ name | wan | prod | agent tags | site | wato
    cur = db.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    db.close()
    processed = []
    hosts_only = open('/omd/sites/master_UA/etc/check_mk/conf.d/wato/hosts.txt', 'a')
    for device in data:
        if str(device[4]) in processed:
            continue
        hosts_only.write(str(device[4]) + '\n')
        processed.append(str(device[4]))
        entry = str(device[4]) + '|' + str(device[6]) + '|' + str(device[5]).lower() + '|' + str(device[1]) + '|wan|prod|' + str(device[7]) + '|site:' + str(device[8]) + '|wato|//'
        all_hosts.append(entry)
        ipaddresses.update({str(device[4]): str(device[0])})
        host_attributes.update({
            str(device[4]): {
            'alias': str(device[13]),
            'contactgroups': (True, ['all']),
            'site': str(device[8]),
            'tag_agent': str(device[7])
            }})
    #all_hosts = list(set(all_hosts))
    hosts_only.close()


def update_configuration_db():
    hosts = []
    with open('/omd/sites/master_UA/etc/check_mk/conf.d/wato/hosts.txt', 'r') as f:
        hosts = map(lambda t: t.strip(), list(f))
    query = "UPDATE device_device set is_added_to_nms = 1, is_monitored_on_nms = 1"
    query += " WHERE device_name IN %s" % pformat(tuple(hosts))
    db = mysql_conn()
    cur = db.cursor()
    cur.execute(query)
    db.commit()
    cur.close()


##############################
# Prepare the rules.mk file
##############################


def prepare_rules(**kwargs):
    ping_levels_db, default_checks, snmp_ports_db, \
            snmp_communities_db, active_checks_thresholds, \
            active_checks_thresholds_per_device = get_settings()
    wimax_pmp1_ul_active_checks, wimax_pmp1_dl_active_checks, wimax_pmp2_ul_active_checks, \
            wimax_pmp2_dl_active_checks, cambium_ul_active_checks, cambium_dl_active_checks= active_checks(
            kwargs.get('wimax_bs_devices'), kwargs.get('cambium_bs_devices'),
            active_checks_thresholds, active_checks_thresholds_per_device)
    write_rules_file(ping_levels_db, default_checks, \
            snmp_ports_db, snmp_communities_db, wimax_pmp1_ul_active_checks, \
            wimax_pmp1_dl_active_checks, wimax_pmp2_ul_active_checks, wimax_pmp2_dl_active_checks, \
            cambium_ul_active_checks, cambium_dl_active_checks)


def get_settings():
    data = []
    # Device specific actve check thresholds, collected from service_deviceserviceconfiguration
    default_checks, active_checks_thresholds_per_device = prepare_priority_checks()
    active_checks_thresholds = []
    query = prepare_query()
    db = mysql_conn()
    try:
        cur = db.cursor()
        cur.execute(query)
        data = dict_rows(cur)
        cur.close()
        #logger.debug('data in get_settings: ' + pformat(data))
    except Exception, exp:
        logger.error('Exception in get_settings: ' + pformat(exp))
        db.close()
    finally:
        db.close()

    processed = []
    # Following active checks should not be included in list of passive checks
    exclude_services = ['wimax_pmp1_ul_util_kpi', 'wimax_pmp1_dl_util_kpi'
            'wimax_pmp2_ul_util_kpi', 'wimax_pmp2_dl_util_kpi',
            'cambium_ul_util_kpi', 'cambium_dl_util_kpi']
    for service in data:
        """
        from pprint import pprint
        pprint(service)
        {
            u'agent_tag': u'snmp-v2|snmp',
            u'check_interval': 5,
            u'critical': u'150',
            u'datasource': u'rereg_count',
            u'devicetype': u'CanopySM100SS',
            u'max_check_attempts': 2,
            u'ping_interval': 5,
            u'ping_packets': 6,
            u'ping_pl_critical': 100,
            u'ping_pl_warning': 80,
            u'ping_rta_critical': 3000,
            u'ping_rta_warning': 1500,
            u'ping_timeout': 20,
            u'retry_check_interval': 1,
            u'service': u'cambium_rereg_count',
            u'warning': u'20'
        }
        """
        if service['devicetype'] not in processed:
            ping_config = {'loss': (service['ping_pl_warning'], service['ping_pl_critical']),
                           'packets': service['ping_packets'],
                           'rta': (service['ping_rta_warning'], service['ping_rta_critical']),
                           'timeout': service['ping_timeout']}, [service['devicetype']], ['@all'], {}
            ping_levels_db.append(ping_config)
            processed.append(service['devicetype'])
        service_config = None
        if service['service']:
            threshold = ()
            try:
                threshold = get_threshold(service)
                if str(service['service']) in exclude_services:
                    active_checks_thresholds.append(str(service['service']), threshold[0], threshold[1])
                    continue
            except Exception, exp:
                logger.error('Exception in get_threshold: ' + pformat(exp))
            service_config = [service['devicetype']], ['@all'], service['service'], None, threshold
        if service_config and (service_config not in default_checks):
                default_checks.append(service_config)
        if service['port'] and service['community']:
            d_ports = service['port'], [service['devicetype']], ['@all']
            if d_ports not in snmp_ports_db:
                snmp_ports_db.append(d_ports)

            d_community = str(service['community']), [str(service['devicetype'])], ['@all']
            if d_community not in snmp_communities_db:
                snmp_communities_db.append(d_community)
    return ping_levels_db, default_checks, snmp_ports_db, snmp_communities_db,\
            active_checks_thresholds, active_checks_thresholds_per_device



def prepare_query():
    query = """
    select
    devicetype.name as devicetype,
    service.name as service,
    datasource.name as datasource,
    devicetype_svc_ds.warning as dtype_ds_warning,
    devicetype_svc_ds.critical as dtype_ds_critical,
    svcds.warning as service_warning,
    svcds.critical as service_critical,
    datasource.warning as warning,
    datasource.critical as critical,
    params.normal_check_interval as check_interval,
    params.retry_check_interval as retry_check_interval,
    params.max_check_attempts as max_check_attempts,
    devicetype.agent_tag as agent_tag,
    devicetype.normal_check_interval as ping_interval,
    devicetype.packets as ping_packets,
    devicetype.pl_critical as ping_pl_critical,
    devicetype.pl_warning as ping_pl_warning,
    devicetype.rta_critical as ping_rta_critical,
    devicetype.rta_warning as ping_rta_warning,
    devicetype.timeout as ping_timeout,
    protocol.port as port,
    protocol.version as version,
    protocol.read_community as community
    from device_devicetype as devicetype
    left join (
        service_service as service,
        device_devicetypeservice as devicetype_svc,

        service_servicespecificdatasource as svcds,
        service_servicedatasource as datasource,
        service_serviceparameters as params,
        service_protocol as protocol
    )
    on (
        svcds.service_id = service.id
        and
        protocol.id = params.protocol_id
        and
        svcds.service_data_sources_id = datasource.id
        and
        params.id = service.parameters_id
        and
        devicetype_svc.service_id = service.id
        and
        devicetype.id = devicetype_svc.device_type_id
    )
    left join
    device_devicetypeservicedatasource as devicetype_svc_ds
    on
    (
    devicetype_svc_ds.device_type_service_id = devicetype_svc.id
    and
    devicetype_svc_ds.service_data_sources_id = datasource.id
    )
    where devicetype.name <> 'Default';
    """
    return query


def get_threshold(service):
    result = ()
    serv = service.get('service')
    warn = None
    crit = None
    try:
        if service.get('dtype_ds_warning') or service.get('dtype_ds_critical'):
            warn = service.get('dtype_ds_warning')
            crit = service.get('dtype_ds_critical')

        elif service.get('service_warning') or service.get('service_critical'):
            warn = service.get('service_warning')
            crit = service.get('service_critical')

        elif service.get('warning') or service.get('critical'):
            warn = service.get('warning')
            crit = service.get('critical')
    except Exception:
        return result

    result = format_threshold(warn, crit, serv)

    return result


def format_threshold(warn, crit, service):
    """

    :param warn:
    :param crit:
    :return:
    """
    if warn and crit:
        try:
            return float(warn), float(crit)
        except:
            if service in wimax_mod_services:
                return map(lambda x: x.strip(), warn.split(',')), \
                       (map(lambda x: x.strip(), crit.split(',')))
            return str(warn), str(crit)
    else:
        return ()


def prepare_priority_checks():
    db = mysql_conn()
    data_values = []
    query = """
    SELECT DISTINCT service_name, device_name, warning, critical
    FROM service_deviceserviceconfiguration
    """
    active_checks_thresholds_per_device = []
    exclude_services = ['wimax_pmp1_ul_util_kpi', 'wimax_pmp1_dl_util_kpi',
            'wimax_pmp2_ul_util_kpi', 'wimax_pmp2_dl_util_kpi',
            'cambium_dl_util_kpi', 'cambium_ul_util_kpi']
    try:
        cur = db.cursor()
        cur.execute(query)
        data_values = dict_rows(cur)
    except Exception, exp:
        logger.error('Exception in priority_checks: ' + pformat(exp))
    finally:
        cur.close()
        db.close()

    data_values = filter(lambda d: d['warning'] or d['critical'], data_values)
    processed_values = []
    for entry in data_values:
        # We need to store war/crit to be used for active checks,
        # Since these would be added as normal services by user
        if str(entry.get('service_name')) in exclude_services:
            active_checks_thresholds_per_device.append((str(entry['device_name']), str(entry['service_name']), \
                    entry['warning'], entry['critical']))
            continue
        if entry.get('service_name') in wimax_mod_services:
            processed_values.append(([str(entry.get('device_name'))], entry.get('service_name'), None, (
            map(str, entry['warning'].replace(' ', '').split(',')),
            map(str, entry['critical'].replace(' ', '').split(',')))))
        else:
            processed_values.append(([str(entry.get('device_name'))], entry.get('service_name'), None,
                                     (float(entry.get('warning')), float(entry.get('critical')))))

    return processed_values, active_checks_thresholds_per_device


def active_checks(wimax_list, cambium_list, active_checks_thresholds, 
        active_checks_thresholds_per_device, wimax_pmp1_ul_check_list=[],
        wimax_pmp1_dl_check_list=[],wimax_pmp2_ul_check_list=[],
        wimax_pmp2_dl_check_list=[], cambium_ul_check_list=[], cambium_dl_check_list=[]):
    # These values would be used if we dont find device specific entry
    S1 = filter(lambda x: 'wimax_pmp1_ul_util_kpi' in x[0], active_checks_thresholds)
    S2 = filter(lambda x: 'wimax_pmp1_dl_util_kpi' in x[0], active_checks_thresholds)
    S3 = filter(lambda x: 'wimax_pmp2_ul_util_kpi' in x[0], active_checks_thresholds)
    S4 = filter(lambda x: 'wimax_pmp2_dl_util_kpi' in x[0], active_checks_thresholds)
    S5 = filter(lambda x: 'cambium_ul_util_kpi' in x[0], active_checks_thresholds)
    S6 = filter(lambda x: 'cambium_dl_util_kpi' in x[0], active_checks_thresholds)
    for entry in wimax_list:
        # Find device specific entry
        wimax_pmp1_ul_util = filter(lambda x: entry[0] == x[0] and 'wimax_pmp1_ul_util_kpi' == x[1], active_checks_thresholds_per_device)
        wimax_pmp1_dl_util = filter(lambda x: entry[0] == x[0] and 'wimax_pmp1_dl_util_kpi' == x[1], active_checks_thresholds_per_device)
        wimax_pmp2_ul_util = filter(lambda x: entry[0] == x[0] and 'wimax_pmp2_ul_util_kpi' == x[1], active_checks_thresholds_per_device)
        wimax_pmp2_dl_util = filter(lambda x: entry[0] == x[0] and 'wimax_pmp2_dl_util_kpi' == x[1], active_checks_thresholds_per_device)
        if wimax_pmp1_ul_util:
            wimax_pmp1_ul_util_war, wimax_pmp1_ul_util_crit = wimax_pmp1_ul_util[0][2], wimax_pmp1_ul_util[0][3]
        elif S1:
            wimax_pmp1_ul_util_war, wimax_pmp1_ul_util_crit = S1[0][2], S1[0][3]
        else:
            wimax_pmp1_ul_util_war, wimax_pmp1_ul_util_crit = 80, 90

        if wimax_pmp1_dl_util:
            wimax_pmp1_dl_util_war, wimax_pmp1_dl_util_crit = wimax_pmp1_dl_util[0][2], wimax_pmp1_dl_util[0][3]
        elif S2:
            wimax_pmp1_dl_util_war, wimax_pmp1_dl_util_crit = S2[0][2], S2[0][3]
        else:
            wimax_pmp1_dl_util_war, wimax_pmp1_dl_util_crit = 80, 90

        if wimax_pmp2_ul_util:
            wimax_pmp2_ul_util_war, wimax_pmp2_ul_util_crit = wimax_pmp2_ul_util[0][2], wimax_pmp2_ul_util[0][3]
        elif S3:
            wimax_pmp2_ul_util_war, wimax_pmp2_ul_util_crit = S3[0][2], S3[0][3]
        else:
            wimax_pmp2_ul_util_war, wimax_pmp2_ul_util_crit = 80, 90

        if wimax_pmp2_dl_util:
            wimax_pmp2_dl_util_war, wimax_pmp2_dl_util_crit = wimax_pmp2_dl_util[0][2], wimax_pmp2_dl_util[0][3]
        elif S4:
            wimax_pmp2_dl_util_war, wimax_pmp2_dl_util_crit = S4[0][2], S4[0][3]
        else:
            wimax_pmp2_dl_util_war, wimax_pmp2_dl_util_crit = 80, 90

        wimax_pmp1_ul_check_list.append((('wimax_pmp1_ul_util_kpi', str(entry[0]), \
                {'site': str(entry[1]), 'war': wimax_pmp1_ul_util_war, 'crit': wimax_pmp1_ul_util_crit}), [], [str(entry[0])]))
        wimax_pmp1_dl_check_list.append((('wimax_pmp1_dl_util_kpi', str(entry[0]), \
                {'site': str(entry[1]), 'war': wimax_pmp1_dl_util_war, 'crit': wimax_pmp1_dl_util_crit}), [], [str(entry[0])]))

        wimax_pmp2_ul_check_list.append((('wimax_pmp2_ul_util_kpi', str(entry[0]), \
                {'site': str(entry[1]), 'war': wimax_pmp2_ul_util_war, 'crit': wimax_pmp2_ul_util_crit}), [], [str(entry[0])]))
        wimax_pmp2_dl_check_list.append((('wimax_pmp2_dl_util_kpi', str(entry[0]), \
                {'site': str(entry[1]), 'war': wimax_pmp2_dl_util_war, 'crit': wimax_pmp2_dl_util_crit}), [], [str(entry[0])]))
    for entry in cambium_list:
        # Find device specific entry
        camb_ul_util = filter(lambda x: entry[0] == x[0] and 'cambium_ul_util_kpi' == x[1], active_checks_thresholds_per_device)
        camb_dl_util = filter(lambda x: entry[0] == x[0] and 'cambium_dl_util_kpi' == x[1], active_checks_thresholds_per_device)
        if camb_ul_util:
            camb_ul_util_war, camb_ul_util_crit = camb_ul_util[0][2], camb_ul_util[0][3]
        elif S5:
            camb_ul_util_war, camb_ul_util_crit = S5[0][1], S5[0][2]
        else:
            camb_ul_util_war, camb_ul_util_crit = 80, 90

        if camb_dl_util:
            camb_dl_util_war, camb_dl_util_crit = camb_dl_util[0][2], camb_dl_util[0][3]
        elif S6:
            camb_dl_util_war, camb_dl_util_crit = S6[0][1], S6[0][2]
        else:
            camb_dl_util_war, camb_dl_util_crit = 80, 90

        cambium_ul_check_list.append((('cambium_ul_util_kpi', str(entry[0]), \
                {'site': str(entry[1]), 'war': camb_ul_util_war, 'crit': camb_ul_util_crit}), [], [str(entry[0])]))
        cambium_dl_check_list.append((('cambium_dl_util_kpi', str(entry[0]), \
                {'site': str(entry[1]), 'war': camb_dl_util_war, 'crit': camb_dl_util_crit}), [], [str(entry[0])]))
    
    return wimax_pmp1_ul_check_list, wimax_pmp1_dl_check_list,wimax_pmp2_ul_check_list, \
            wimax_pmp2_dl_check_list, cambium_ul_check_list, cambium_dl_check_list


def dict_rows(cur):
    desc = cur.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cur.fetchall()
    ]


def write_rules_file(ping_levels_db, default_checks, snmp_ports_db, 
        snmp_communities_db, wimax_pmp1_ul_active_checks, wimax_pmp1_dl_active_checks ,
        wimax_pmp2_ul_active_checks, wimax_pmp2_dl_active_checks, cambium_ul_active_checks, cambium_dl_active_checks):
    global default_snmp_ports
    global default_snmp_communities
    if len(snmp_communities_db):
        default_snmp_communities = snmp_communities_db
    if len(snmp_ports_db):
        default_snmp_ports = snmp_ports_db
    with open('/omd/sites/master_UA/etc/check_mk/conf.d/wato/rules.mk', 'w') as f:
        f.write("# encoding: utf-8")
        f.write("\n\n\n")
        f.write("bulkwalk_hosts += %s" % pformat(bulkwalk_hosts))
        f.write("\n\n\n")
        f.write("ping_levels += %s" % pformat(ping_levels_db))
        f.write("\n\n\n")
        f.write("active_checks.setdefault('wimax_pmp1_ul_util_kpi', [])\n")
        f.write("active_checks.setdefault('wimax_pmp1_dl_util_kpi', [])\n")
        f.write("active_checks.setdefault('wimax_pmp2_ul_util_kpi', [])\n")
        f.write("active_checks.setdefault('wimax_pmp2_dl_util_kpi', [])\n")
        f.write("active_checks.setdefault('cambium_ul_util_kpi', [])\n\n")
        f.write("active_checks.setdefault('cambium_dl_util_kpi', [])\n\n")
        f.write("active_checks['wimax_pmp1_ul_util_kpi'] += %s\n\n" % pformat(wimax_pmp1_ul_active_checks))
        f.write("active_checks['wimax_pmp1_dl_util_kpi'] += %s\n\n" % pformat(wimax_pmp1_dl_active_checks))
        f.write("active_checks['wimax_pmp2_ul_util_kpi'] += %s\n\n" % pformat(wimax_pmp2_ul_active_checks))
        f.write("active_checks['wimax_pmp2_dl_util_kpi'] += %s\n\n" % pformat(wimax_pmp2_dl_active_checks))
        f.write("active_checks['cambium_ul_util_kpi'] += %s\n\n" % pformat(cambium_ul_active_checks))
        f.write("active_checks['cambium_dl_util_kpi'] += %s\n\n" % pformat(cambium_dl_active_checks))
        f.write("checks += %s" % pformat(default_checks))
        f.write("\n\n\n")
        f.write("snmp_ports += %s" % pformat(default_snmp_ports))
        f.write("\n\n\n")
        f.write("snmp_communities += %s" % pformat(default_snmp_communities))
        f.write("\n\n\n")
        f.write(
            "extra_service_conf['normal_check_interval'] = %s" % pformat(extra_service_conf['normal_check_interval']))
        f.write("\n\n\n")
        f.write("extra_service_conf['max_check_attempts'] = %s" % pformat(extra_service_conf['max_check_attempts']))
        f.write("\n\n\n")
        f.write("extra_service_conf['retry_check_interval'] = %s" % pformat(extra_service_conf['retry_check_interval']))


def main():
    wimax_bs_devices, cambium_bs_devices = prepare_hosts_file()
    print "wimax_bs_devices, cambium_bs_devices"
    print len(wimax_bs_devices), len(cambium_bs_devices)
    prepare_rules(wimax_bs_devices=wimax_bs_devices, cambium_bs_devices=cambium_bs_devices)


if __name__ == '__main__':
    main()
