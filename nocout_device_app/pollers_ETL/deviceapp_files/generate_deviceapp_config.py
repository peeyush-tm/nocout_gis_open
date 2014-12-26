from mysql_connection import mysql_conn
from pprint import pformat
from operator import itemgetter
from nocout_logger import nocout_log
from collections import namedtuple

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
    T = namedtuple('devices', 
            ['wimax_bs_devices', 'cambium_bs_devices',
                'radwin_bs_devices', 'wimax_ss_devices', 
                'radwin_ss_devices', 'total_radwin_devices'])
    all_hosts, ipaddresses, host_attributes = [], {}, {}
    wimax_bs_devices, cambium_bs_devices = [], []
    # This file contains device names, to be updated in configuration db
    open('/omd/sites/master_UA/etc/check_mk/conf.d/wato/hosts.txt', 'w').close()
    #try:
    bs_devices = make_BS_data()
    #except Exception, exp:
    #   logger.error('Exception in make_BS_data: ' + pformat(exp))
    #try:
    ss_devices = make_SS_data(bs_devices.all_hosts, bs_devices.ipaddresses, bs_devices.host_attributes)
    #except Exception, exp:
    #   logger.error('Exception in make_SS_data: ' + pformat(exp))
    T.wimax_bs_devices, T.cambium_bs_devices = bs_devices.wimax_bs_devices, bs_devices.cambium_bs_devices
    T.radwin_bs_devices, T.radwin_ss_devices = bs_devices.radwin_bs_devices, ss_devices.radwin_ss_devices
    T.total_radwin_devices = bs_devices.radwin_bs_devices + ss_devices.radwin_ss_devices
    T.wimax_ss_devices = ss_devices.wimax_ss_devices

    write_hosts_file(ss_devices.all_hosts, ss_devices.ipaddresses, ss_devices.host_attributes)

    return T


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
    device_devicetechnology.name as techno_name,
    inventory_circuit.qos_bandwidth as QoS_BW
    from device_device inner join (device_devicetechnology, device_devicemodel, device_devicetype, machine_machine, site_instance_siteinstance, inventory_sector, inventory_circuit)
    on (
    device_devicetype.id = device_device.device_type and
    device_devicetechnology.id = device_device.device_technology and
    device_devicemodel.id = device_device.device_model and
    machine_machine.id = device_device.machine_id and
    site_instance_siteinstance.id = device_device.site_instance_id and
    inventory_sector.sector_configured_on_id = device_device.id and
    inventory_sector.id = inventory_circuit.sector_id
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
    T = namedtuple('bs_devices', [
        'all_hosts', 'ipaddresses', 'host_attributes',
        'wimax_bs_devices', 'cambium_bs_devices', 'radwin_bs_devices'])
    processed = []
    dr_en_devices = sorted(filter(lambda e: e[9] and e[9].lower() == 'yes' and e[10], data), key=itemgetter(10))
    #print 'dr_en_devices --'
    #print len(dr_en_devices)
    data = filter(lambda e: e[9] == '' or e[9] == None or (e[9] and e[9].lower() == 'no'), data)
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

    #print data
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

    T.all_hosts, T.ipaddresses, T.host_attributes = all_hosts, ipaddresses, host_attributes

    # Get the wimax BS devices (we need them for active checks)
    # Ex entry : ('device_1', 'ospf4_slave_1')
    L0 = map(lambda e: (e[1], e[7]), filter(lambda e: e[11].lower() == 'wimax', data))
    L1 = map(lambda e: (e[1], e[7]), dr_en_devices)
    #L2 = zip(map(lambda e: e[0], dr_configured_on_devices), map(lambda e: e[1], L1))
    wimax_bs_devices = L0 + L1
    # Get the Cambium BS devices (we need them for active checks)
    # Since, as of now, we have only Cambium devices in pmp technology
    cambium_bs_devices = map(lambda e: (e[1], e[7]), filter(lambda e: e[11].lower() == 'pmp', data))
    T.wimax_bs_devices, T.cambium_bs_devices = wimax_bs_devices, cambium_bs_devices

    # Get the Radwin BS devices (We need them to generate active and static checks)
    # Ex entry : ('device_1', 'ospf4_slave_1', '5120')
    radwin_bs_devices = map(lambda e: (e[1], e[7], e[12]), filter(lambda e: e[11].lower() == 'p2p', data))
    # Calculate the QoS, needed as input to static checks in form of warning/critical values
    qos_values = eval_qos(map(lambda e: e[2], radwin_bs_devices))
    radwin_bs_devices = map(lambda e: (e[0], e[1]), radwin_bs_devices)
    radwin_bs_devices = zip(radwin_bs_devices, qos_values)
    T.radwin_bs_devices = radwin_bs_devices

    return T


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


def eval_qos(vals, out=[]):
    for v in vals:
        if v and int(v) > 10:
            v = float(v) / float(1024)
        elif v and int(v) <= 10:
            v = float(v)
        else:
            v = 1.0
        out.append(v)

    return out


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
    SSALIAS,
    techno_name,
    QoS_BW
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
    inventory_sector.sector_configured_on_id as matcher,
    device_devicetechnology.name as techno_name,
    inventory_circuit.qos_bandwidth as QoS_BW
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
    T = namedtuple('ss_devices', [
        'all_hosts', 'ipaddresses', 'host_attributes',
        'radwin_ss_devices', 'wimax_ss_devices'])
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

    # Get Radwin SS devices, we need them for static n active checks
    radwin_ss_devices = filter(lambda e: e[14].lower() == 'p2p', data)
    radwin_ss_devices = map(lambda e: (e[4], e[8], e[15]), radwin_ss_devices)
    qos_values = eval_qos(map(lambda e: e[2], radwin_ss_devices))
    radwin_ss_devices = map(lambda e: (e[0], e[1]), radwin_ss_devices)
    radwin_ss_devices = zip(radwin_ss_devices, qos_values)
    # Get Wimax SS devices, for active checks
    wimax_ss_devices = filter(lambda e: e[14].lower() == 'wimax', data)
    wimax_ss_devices = map(lambda e: (e[4], e[8]), wimax_ss_devices)
    #print wimax_ss_devices[0:10]

    T.all_hosts, T.ipaddresses, T.host_attributes = all_hosts, ipaddresses, host_attributes
    T.radwin_ss_devices, T.wimax_ss_devices = radwin_ss_devices, wimax_ss_devices

    return T


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


def prepare_rules(devices):
    #ping_levels_db, default_checks, snmp_ports_db, \
    #        snmp_communities_db, active_checks_thresholds, \
    #        active_checks_thresholds_per_device = get_settings()
    settings_out = get_settings()

    #print settings_out.active_checks_thresholds
    ac_chks1 = util_active_checks(
            devices, 
            settings_out.active_checks_thresholds, 
            settings_out.active_checks_thresholds_per_device)
    ac_chks2 = ss_active_checks(
            devices, 
            settings_out.active_checks_thresholds,
            settings_out.active_checks_thresholds_per_device)
    ac_chks1.update(ac_chks2)

    write_rules_file(settings_out, ac_chks1)


def get_settings():
    data = []
    T = namedtuple('host_rules', [
        'ping_levels_db', 'default_checks', 'snmp_ports_db',
        'snmp_communities_db', 'active_checks_thresholds',
        'active_checks_thresholds_per_device'
        ])
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
    # Following utilization active checks should not be included in list of passive checks
    exclude_util_active_services = ['wimax_pmp1_ul_util_kpi', 'wimax_pmp1_dl_util_kpi',
            'wimax_pmp2_ul_util_kpi', 'wimax_pmp2_dl_util_kpi',
            'cambium_ul_util_kpi', 'cambium_dl_util_kpi',
            'radwin_ul_util_kpi', 'radwin_dl_util_kpi', 'radwin_util_static']
    # Following dependent SS checks should not be included in list of passive checks
    # As they are treated as active checks (Dependent in sense they get data from their BS)
    exclude_ss_active_services = ['wimax_ul_rssi', 'wimax_dl_rssi', 'wimax_ul_cinr',
            'wimax_dl_cinr', 'wimax_ul_intrf', 'wimax_dl_intrf',
            'wimax_modulation_ul_fec', 'wimax_modulation_dl_fec']
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
            	if str(service['service']) in exclude_util_active_services:
                	active_checks_thresholds.append((str(service['service']), threshold[0], threshold[1]))
                	continue
            	if str(service['service']) in exclude_ss_active_services:
                	active_checks_thresholds.append((str(service['service']), threshold[0], threshold[1]))
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
    T.ping_levels_db, T.default_checks, T.snmp_ports_db = ping_levels_db, default_checks, snmp_ports_db
    T.snmp_communities_db, T.active_checks_thresholds = snmp_communities_db, active_checks_thresholds
    T.active_checks_thresholds_per_device = active_checks_thresholds_per_device

    return T


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
    #print service
    #try:
    if service.get('dtype_ds_warning') or service.get('dtype_ds_critical'):
        warn = service.get('dtype_ds_warning')
        crit = service.get('dtype_ds_critical')

    elif service.get('service_warning') or service.get('service_critical'):
        warn = service.get('service_warning')
        crit = service.get('service_critical')

    elif service.get('warning') or service.get('critical'):
        warn = service.get('warning')
        crit = service.get('critical')
    #except Exception:
        #return result

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
    # Following utilization active checks should not be included in list of passive checks
    exclude_util_active_services = ['wimax_pmp1_ul_util_kpi', 'wimax_pmp1_dl_util_kpi',
            'wimax_pmp2_ul_util_kpi', 'wimax_pmp2_dl_util_kpi',
            'cambium_ul_util_kpi', 'cambium_dl_util_kpi',
            'radwin_ul_util_kpi', 'radwin_dl_util_kpi', 'radwin_util_static']
    # Following dependent SS checks should not be included in list of passive checks
    # As they are treated as active checks (Dependent in sense they get data from their BS)
    exclude_ss_active_services = ['wimax_ul_rssi', 'wimax_dl_rssi', 'wimax_ul_cinr',
            'wimax_dl_cinr', 'wimax_ul_intrf', 'wimax_dl_intrf',
            'wimax_modulation_ul_fec', 'wimax_modulation_dl_fec']
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
        if str(entry.get('service_name')) in exclude_util_active_services:
            active_checks_thresholds_per_device.append((str(entry['device_name']), str(entry['service_name']), \
                    entry['warning'], entry['critical']))
            continue
        if str(entry.get('service_name')) in exclude_ss_active_services:
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


def ss_active_checks(devices, active_checks_thresholds, active_checks_thresholds_per_device):
    wimax_ss_services = ['wimax_ul_rssi', 'wimax_dl_rssi', 'wimax_ul_cinr',
        'wimax_dl_cinr', 'wimax_ul_intrf', 'wimax_dl_intrf', 
        'wimax_modulation_ul_fec', 'wimax_modulation_dl_fec']
    check_dict = {}
    check_dict = make_active_check_rows(check_dict, devices.wimax_ss_devices, wimax_ss_services, 
            active_checks_thresholds, active_checks_thresholds_per_device)

    return check_dict


def make_active_check_rows(container, devices, services, active_checks_thresholds, 
        active_checks_thresholds_per_device, def_war=None, def_crit=None):

    for service in services:
        container[service] = []
        # These thresholds would be used if we dont find entry in below filter func
        serv_specific_entry = filter(lambda e: service in e[0], active_checks_thresholds)
        for host_tuple in devices:
            #print host_tuple
            host_specific_entry = filter(lambda e: host_tuple[0] == e[0] and service == e[1], active_checks_thresholds_per_device)
            if host_specific_entry:
                war, crit = host_specific_entry[0][2], host_specific_entry[0][3]
            elif serv_specific_entry:
                war, crit = serv_specific_entry[0][1], serv_specific_entry[0][2]
            else:
                war, crit = def_war, def_crit
            container[service].append(((str(service), {'host': str(host_tuple[0]), 'site': str(host_tuple[1]), 'war': war, 'crit': crit}), [], [str(host_tuple[0])]))

    return container


def util_active_checks(devices, active_checks_thresholds, active_checks_thresholds_per_device):
    wimax_util_services = ['wimax_pmp1_ul_util_kpi', 'wimax_pmp1_dl_util_kpi',
            'wimax_pmp2_ul_util_kpi', 'wimax_pmp2_dl_util_kpi']
    cambium_util_services = ['cambium_ul_util_kpi', 'cambium_dl_util_kpi']
    radwin_util_services = ['radwin_ul_util_kpi', 'radwin_dl_util_kpi']
    check_dict = {}
    check_dict = make_active_check_rows(check_dict, devices.wimax_bs_devices,
            wimax_util_services, active_checks_thresholds, active_checks_thresholds_per_device,
            def_war=80, def_crit=90)
    check_dict = make_active_check_rows(check_dict, devices.cambium_bs_devices,
            cambium_util_services, active_checks_thresholds, active_checks_thresholds_per_device,
            def_war=80, def_crit=90)
    check_dict = make_active_check_rows(check_dict, devices.total_radwin_devices,
            radwin_util_services, active_checks_thresholds, active_checks_thresholds_per_device)
    ########################################################################################
    # These values would be used if we dont find device specific entry
    #S1 = filter(lambda x: 'wimax_pmp1_ul_util_kpi' in x[0], active_checks_thresholds)
    #S2 = filter(lambda x: 'wimax_pmp1_dl_util_kpi' in x[0], active_checks_thresholds)
    #S3 = filter(lambda x: 'wimax_pmp2_ul_util_kpi' in x[0], active_checks_thresholds)
    #S4 = filter(lambda x: 'wimax_pmp2_dl_util_kpi' in x[0], active_checks_thresholds)
    #S5 = filter(lambda x: 'cambium_ul_util_kpi' in x[0], active_checks_thresholds)
    #S6 = filter(lambda x: 'cambium_dl_util_kpi' in x[0], active_checks_thresholds)
    #S7 = filter(lambda x: 'radwin_ul_util_kpi' in x[0], active_checks_thresholds)
    #S8 = filter(lambda x: 'radwin_dl_util_kpi' in x[0], active_checks_thresholds)
    #for entry in devices.wimax_bs_devices:
    #    # Find device specific entry
    #    wimax_pmp1_ul_util = filter(lambda x: entry[0] == x[0] and 'wimax_pmp1_ul_util_kpi' == x[1], active_checks_thresholds_per_device)
    #    wimax_pmp1_dl_util = filter(lambda x: entry[0] == x[0] and 'wimax_pmp1_dl_util_kpi' == x[1], active_checks_thresholds_per_device)
    #    wimax_pmp2_ul_util = filter(lambda x: entry[0] == x[0] and 'wimax_pmp2_ul_util_kpi' == x[1], active_checks_thresholds_per_device)
    #    wimax_pmp2_dl_util = filter(lambda x: entry[0] == x[0] and 'wimax_pmp2_dl_util_kpi' == x[1], active_checks_thresholds_per_device)
    #    try:
    #            if wimax_pmp1_ul_util:
    #                    wimax_pmp1_ul_util_war, wimax_pmp1_ul_util_crit = wimax_pmp1_ul_util[0][2], wimax_pmp1_ul_util[0][3]
    #            elif S1:
    #                    wimax_pmp1_ul_util_war, wimax_pmp1_ul_util_crit = S1[0][2], S1[0][3]
    #            else:
    #                    wimax_pmp1_ul_util_war, wimax_pmp1_ul_util_crit = 80, 90
    #    except Exception:
    #        wimax_pmp1_ul_util_war, wimax_pmp1_ul_util_crit = 80, 90

    #    try:
    #            if wimax_pmp1_dl_util:
    #                    wimax_pmp1_dl_util_war, wimax_pmp1_dl_util_crit = wimax_pmp1_dl_util[0][2], wimax_pmp1_dl_util[0][3]
    #            elif S2:
    #                    wimax_pmp1_dl_util_war, wimax_pmp1_dl_util_crit = S2[0][2], S2[0][3]
    #            else:
    #                    wimax_pmp1_dl_util_war, wimax_pmp1_dl_util_crit = 80, 90
    #    except Exception:
    #        wimax_pmp1_dl_util_war, wimax_pmp1_dl_util_crit = 80, 90

    #    try:
    #            if wimax_pmp2_ul_util:
    #                    wimax_pmp2_ul_util_war, wimax_pmp2_ul_util_crit = wimax_pmp2_ul_util[0][2], wimax_pmp2_ul_util[0][3]
    #            elif S3:
    #                    wimax_pmp2_ul_util_war, wimax_pmp2_ul_util_crit = S3[0][2], S3[0][3]
    #            else:
    #                    wimax_pmp2_ul_util_war, wimax_pmp2_ul_util_crit = 80, 90
    #    except Exception:
    #        wimax_pmp2_ul_util_war, wimax_pmp2_ul_util_crit = 80, 90

    #    try:
    #            if wimax_pmp2_dl_util:
    #                    wimax_pmp2_dl_util_war, wimax_pmp2_dl_util_crit = wimax_pmp2_dl_util[0][2], wimax_pmp2_dl_util[0][3]
    #            elif S4:
    #                    wimax_pmp2_dl_util_war, wimax_pmp2_dl_util_crit = S4[0][2], S4[0][3]
    #            else:
    #                    wimax_pmp2_dl_util_war, wimax_pmp2_dl_util_crit = 80, 90
    #    except Exception:
    #        wimax_pmp2_dl_util_war, wimax_pmp2_dl_util_crit = 80, 90

    #    wimax_pmp1_ul_check_list.append((('wimax_pmp1_ul_util_kpi', str(entry[0]), \
    #            {'site': str(entry[1]), 'war': wimax_pmp1_ul_util_war, 'crit': wimax_pmp1_ul_util_crit}), [], [str(entry[0])]))
    #    wimax_pmp1_dl_check_list.append((('wimax_pmp1_dl_util_kpi', str(entry[0]), \
    #            {'site': str(entry[1]), 'war': wimax_pmp1_dl_util_war, 'crit': wimax_pmp1_dl_util_crit}), [], [str(entry[0])]))

    #    wimax_pmp2_ul_check_list.append((('wimax_pmp2_ul_util_kpi', str(entry[0]), \
    #            {'site': str(entry[1]), 'war': wimax_pmp2_ul_util_war, 'crit': wimax_pmp2_ul_util_crit}), [], [str(entry[0])]))
    #    wimax_pmp2_dl_check_list.append((('wimax_pmp2_dl_util_kpi', str(entry[0]), \
    #            {'site': str(entry[1]), 'war': wimax_pmp2_dl_util_war, 'crit': wimax_pmp2_dl_util_crit}), [], [str(entry[0])]))
    #for entry in devices.cambium_bs_devices:
    #    # Find device specific entry
    #    camb_ul_util = filter(lambda x: entry[0] == x[0] and 'cambium_ul_util_kpi' == x[1], active_checks_thresholds_per_device)
    #    camb_dl_util = filter(lambda x: entry[0] == x[0] and 'cambium_dl_util_kpi' == x[1], active_checks_thresholds_per_device)
    #    if camb_ul_util:
    #        camb_ul_util_war, camb_ul_util_crit = camb_ul_util[0][2], camb_ul_util[0][3]
    #    elif S5:
    #        camb_ul_util_war, camb_ul_util_crit = S5[0][1], S5[0][2]
    #    else:
    #        camb_ul_util_war, camb_ul_util_crit = 80, 90

    #    if camb_dl_util:
    #        camb_dl_util_war, camb_dl_util_crit = camb_dl_util[0][2], camb_dl_util[0][3]
    #    elif S6:
    #        camb_dl_util_war, camb_dl_util_crit = S6[0][1], S6[0][2]
    #    else:
    #        camb_dl_util_war, camb_dl_util_crit = 80, 90

    #    cambium_ul_check_list.append((('cambium_ul_util_kpi', str(entry[0]), \
    #            {'site': str(entry[1]), 'war': camb_ul_util_war, 'crit': camb_ul_util_crit}), [], [str(entry[0])]))
    #    cambium_dl_check_list.append((('cambium_dl_util_kpi', str(entry[0]), \
    #            {'site': str(entry[1]), 'war': camb_dl_util_war, 'crit': camb_dl_util_crit}), [], [str(entry[0])]))
    #for entry in devices.total_radwin_devices:
    #    # Find device specific entry
    #    rad_ul_util = filter(lambda x: entry[0][0] == x[0] and 'radwin_ul_util_kpi' == x[1], active_checks_thresholds_per_device)
    #    rad_dl_util = filter(lambda x: entry[0][0] == x[0] and 'radwin_dl_util_kpi' == x[1], active_checks_thresholds_per_device)
    #    if rad_ul_util:
    #        rad_ul_util_war, rad_ul_util_crit = rad_ul_util[0][2], rad_ul_util[0][3]
    #    elif S7:
    #        rad_ul_util_war, rad_ul_util_crit = S7[0][1], S7[0][2]
    #    else:
    #        rad_ul_util_war, rad_ul_util_crit = 80, 90

    #    if rad_dl_util:
    #        rad_dl_util_war, rad_dl_util_crit = rad_dl_util[0][2], rad_dl_util[0][3]
    #    elif S8:
    #        rad_dl_util_war, rad_dl_util_crit = S8[0][1], S8[0][2]
    #    else:
    #        rad_dl_util_war, rad_dl_util_crit = 80, 90

    #    radwin_ul_check_list.append((('radwin_ul_util_kpi', str(entry[0][0]), \
    #            {'site': str(entry[0][1]), 'war': rad_ul_util_war, 'crit': rad_ul_util_crit}), [], [str(entry[0][0])]))

    #    radwin_dl_check_list.append((('radwin_dl_util_kpi', str(entry[0][0]), \
    #            {'site': str(entry[0][1]), 'war': rad_dl_util_war, 'crit': rad_dl_util_crit}), [], [str(entry[0][0])]))

    #    radwin_static_check_list.append((('radwin_util_static', str(entry[0][0]), \
    #            {'site': str(entry[0][1]), 'war': entry[1], 'crit': entry[1]}), [], [str(entry[0][0])]))

    #T.wimax_pmp1_ul_check_list, T.wimax_pmp1_dl_check_list = wimax_pmp1_ul_check_list, wimax_pmp1_dl_check_list
    #T.wimax_pmp2_ul_check_list, T.wimax_pmp2_dl_check_list = wimax_pmp2_ul_check_list, wimax_pmp2_dl_check_list
    #T.cambium_ul_check_list, T.cambium_dl_check_list = cambium_ul_check_list, cambium_dl_check_list
    #T.radwin_ul_check_list, T.radwin_dl_check_list = radwin_ul_check_list, radwin_dl_check_list
    #T.radwin_static_check_list = radwin_static_check_list
    
    return check_dict


def dict_rows(cur):
    desc = cur.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cur.fetchall()
    ]


def write_rules_file(settings_out, final_active_checks):
    global default_snmp_ports
    global default_snmp_communities
    if len(settings_out.snmp_communities_db):
        default_snmp_communities = settings_out.snmp_communities_db
    if len(settings_out.snmp_ports_db):
        default_snmp_ports = settings_out.snmp_ports_db
    with open('/omd/sites/master_UA/etc/check_mk/conf.d/wato/rules.mk', 'w') as f:
        f.write("# encoding: utf-8")
        f.write("\n\n\n")
        f.write("bulkwalk_hosts += %s" % pformat(bulkwalk_hosts))
        f.write("\n\n\n")
        f.write("ping_levels += %s" % pformat(settings_out.ping_levels_db))
        f.write("\n\n\n")

        #f.write("active_checks.setdefault('wimax_pmp1_ul_util_kpi', [])\n")
        #f.write("active_checks.setdefault('wimax_pmp1_dl_util_kpi', [])\n")
        #f.write("active_checks.setdefault('wimax_pmp2_ul_util_kpi', [])\n")
        #f.write("active_checks.setdefault('wimax_pmp2_dl_util_kpi', [])\n")
        #f.write("active_checks.setdefault('cambium_ul_util_kpi', [])\n")
        #f.write("active_checks.setdefault('cambium_dl_util_kpi', [])\n")
        #f.write("active_checks.setdefault('radwin_ul_util_kpi', [])\n")
        #f.write("active_checks.setdefault('radwin_dl_util_kpi', [])\n")
        #f.write("active_checks.setdefault('radwin_util_static', [])\n")

        #f.write("active_checks['wimax_pmp1_ul_util_kpi'] += %s\n\n" % pformat(ac_chks1.wimax_pmp1_ul_check_list))
        #f.write("active_checks['wimax_pmp1_dl_util_kpi'] += %s\n\n" % pformat(ac_chks1.wimax_pmp1_dl_check_list))
        #f.write("active_checks['wimax_pmp2_ul_util_kpi'] += %s\n\n" % pformat(ac_chks1.wimax_pmp2_ul_check_list))
        #f.write("active_checks['wimax_pmp2_dl_util_kpi'] += %s\n\n" % pformat(ac_chks1.wimax_pmp2_dl_check_list))
        #f.write("active_checks['cambium_ul_util_kpi'] += %s\n\n" % pformat(ac_chks1.cambium_ul_check_list))
        #f.write("active_checks['cambium_dl_util_kpi'] += %s\n\n" % pformat(ac_chks1.cambium_dl_check_list))
        #f.write("active_checks['radwin_ul_util_kpi'] += %s\n\n" % pformat(ac_chks1.radwin_ul_check_list))
        #f.write("active_checks['radwin_dl_util_kpi'] += %s\n\n" % pformat(ac_chks1.radwin_dl_check_list))
        #f.write("active_checks['radwin_util_static'] += %s\n\n" % pformat(ac_chks1.radwin_static_check_list))

        #for check_name in ac_chks1._fields:
        #    f.write("active_checks.setdefault('" + check_name + "', [])\n")
        #for check_name in ac_chks1._fields:
        #    if isinstance(getattr(ac_chks1, check_name), list):
        #        f.write("active_checks['" + check_name + "'] += %s\n\n" % pformat(list(getattr(ac_chks1, check_name))))

        f.write("\n")
        #for check_name in ac_chks2._fields:
        #    f.write("active_checks.setdefault('" + check_name + "', [])\n")
        #f.write("\n")
        #for check_name in ac_chks2._fields:
        #    if isinstance(getattr(ac_chks2, check_name), list):
        #        f.write("active_checks['" + check_name + "'] += %s\n\n" % pformat(list(getattr(ac_chks2, check_name))))

        for service in final_active_checks.keys():
            f.write("active_checks.setdefault('" + service + "', [])\n")

        for service, check_list in final_active_checks.iteritems():
            f.write("active_checks['" + service + "'] += %s\n\n" % pformat(check_list))

        f.write("checks += %s" % pformat(settings_out.default_checks))
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
    hosts_out = prepare_hosts_file()
    print "wimax_bs_devices, wimax_ss_devices, cambium_bs_devices", "radwin_bs_devices", "radwin_ss_devices"
    print len(hosts_out.wimax_bs_devices), len(hosts_out.wimax_ss_devices), len(hosts_out.cambium_bs_devices), \
            len(hosts_out.radwin_bs_devices), len(hosts_out.radwin_ss_devices)
    prepare_rules(hosts_out)


if __name__ == '__main__':
    main()
