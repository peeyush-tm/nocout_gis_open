from mysql_connection import mysql_conn, dict_rows
from pprint import pprint, pformat

db = mysql_conn()

pmp_ss_bs_checks = ['cambium_ul_jitter','cambium_reg_count','cambium_rereg_count','cambium_ul_rssi']

bulkwalk_hosts = [(['snmp-v2'],['@all'])]

#ping_levels = [({'loss': (80, 100), 'packets': 10, 'rta': (1500, 3000), 'timeout': 20}, [u'Radwin2KSS'], ['@all'], {})] 

ping_levels_db = list()

default_checks = [
#(['Radwin2KBS'], ['@all'], 'radwin_rssi', None, (-50, -60)),
]

default_snmp_ports = [
                (161, ['Radwin2KBS'], ['@all']),
                (161, ['Radwin2KSS'], ['@all']),
                (161, ['CanopyPM100AP'], ['@all']),
                (161, ['CanopyPM100SS'], ['@all']),
                (161, ['CanopySM100AP'], ['@all']),
                (161, ['CanopySM100SS'], ['@all']),
                ]

snmp_ports_db = list()

## will calculate the commnities

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

def main():
    get_settings()

    #pprint(ping_levels_db)
    #pprint(default_checks)
    #pprint(snmp_communities_db)
    #pprint(snmp_ports_db)
     
    if len(snmp_communities_db):
        default_snmp_communities = snmp_communities_db
    if len(snmp_ports_db):
        default_snmp_ports = snmp_ports_db
    #pprint(default_snmp_ports)
    #pprint(default_snmp_communities)
    with open('/apps/omd/sites/main_UA/etc/check_mk/conf.d/wato/rules.mk', 'w') as f:
        f.write("# encoding: utf-8")
        f.write("\n\n\n")
        f.write("bulkwalk_hosts += %s" % pformat(bulkwalk_hosts))
        f.write("\n\n\n")
        f.write("ping_levels += %s" % pformat(ping_levels_db))
        f.write("\n\n\n")
        f.write("checks += %s" % pformat(default_checks))
        f.write("\n\n\n")
        f.write("snmp_ports += %s" % pformat(default_snmp_ports))
        f.write("\n\n\n")
        f.write("snmp_communities += %s" % pformat(default_snmp_communities))
        f.write("\n\n\n")
        f.write("extra_service_conf['normal_check_interval'] = %s" % pformat(extra_service_conf['normal_check_interval']))
        f.write("\n\n\n")
        f.write("extra_service_conf['max_check_attempts'] = %s" % pformat(extra_service_conf['max_check_attempts']))
        f.write("\n\n\n")
        f.write("extra_service_conf['retry_check_interval'] = %s" % pformat(extra_service_conf['retry_check_interval']))
       	 


def prepare_query():
    query = """
    select
    devicetype.name as devicetype,
    service.name as service,
    datasource.name as datasource,
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
        service_servicespecificdatasource as svcds,
        service_servicedatasource as datasource,
        service_serviceparameters as params,
        service_protocol as protocol,
        device_devicetype_service as devicetypesvc
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
        devicetypesvc.service_id = service.id
        and
        devicetype.id = devicetypesvc.devicetype_id
    )
    where devicetype.name <> 'Default'
    """
    return query

def get_settings():
    global default_checks
    default_checks = prepare_priority_checks()
    query = prepare_query()
    cur = db.cursor()
    cur.execute(query)
    data = dict_rows(cur)
    cur.close()
    processed = []
    for service in data:
        """from pprint import pprint
          pprint(service)
          {u'agent_tag': u'snmp-v2|snmp',
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
 u'warning': u'20'}
        """
        if service['devicetype'] not in processed:
            ping_config = {'loss': (service['ping_pl_warning'], service['ping_pl_critical']), 
                        'packets': service['ping_packets'], 
                        'rta': (service['ping_rta_warning'], service['ping_rta_critical']), 'timeout': service['ping_timeout']}, [service['devicetype']], ['@all'], {}
            ping_levels_db.append(ping_config)
            processed.append(service['devicetype'])
        if service['service']:        
            threshold = get_threshold(service)
            service_config = [service['devicetype']], ['@all'], service['service'], None, threshold
            default_checks.append(service_config)
            if service['port'] and service['community']:
                d_ports = service['port'], [service['devicetype']], ['@all']
                if d_ports not in snmp_ports_db:
                    snmp_ports_db.append(d_ports) 
                
                d_community = str(service['community']), [str(service['devicetype'])], ['@all']
                if d_community not in snmp_communities_db:
                    snmp_communities_db.append(d_community)


def get_threshold(service):
    result = ()
    if service.get('service_warning') or service.get('service_critical'):
        result = (int(service['service_warning']), int('service_critical'))
    else:
        try:
	    if service.get('service') in wimax_mod_services:
		    result = (map(str, service['warning'].replace(' ', '').split(',')), map(str, service['critical'].replace(' ', '').split(',')))
	    else:
		    result = (int(service['warning']), int(service['critical']))
        except:
	    pass
            #result = (service['warning'], service['critical'])
    return result


def prepare_priority_checks():
	query = """
	SELECT DISTINCT service_name, device_name, warning, critical
	FROM service_deviceserviceconfiguration
	"""

	cur = db.cursor()
	cur.execute(query)
	data_values = dict_rows(cur)
	data_values = filter(lambda d: d['warning'] or d['critical'], data_values)
	processed_values = []
	for entry in data_values:
		if entry.get('service_name') in wimax_mod_services:
			processed_values.append(([str(entry.get('device_name'))], entry.get('service_name'), None, (map(str, entry['warning'].replace(' ', '').split(',')), map(str, entry['critical'].replace(' ', '').split(',')))))
		else:
			processed_values.append(([str(entry.get('device_name'))], entry.get('service_name'), None, (entry.get('warning'), entry.get('critical'))))
	#print processed_values

	return processed_values


def ping_settings():
    pass

def check_settings():
    pass

def pmp_ss_settings():
    pass

if __name__ == '__main__':
    main()
