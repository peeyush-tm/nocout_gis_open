import mysql.connector
#from MySQLdb import connect
import requests
from ast import literal_eval
import pprint
from datetime import datetime
import urllib
import json
import time


g_services = ('radwin_rssi', 'radwin_uptime', 'radwin_uas', 'radwin_service_throughput',
		'radwin_dl_utilization', 'radwin_ul_utilization', 'radwin_link_ethernet_status',
		'radwin_port_mode_status', 'radwin_port_speed_status', 'radwin_autonegotiation_status',
		'radwin_frequency_invent', 'radwin_producttype_invent', 'radwin_odu_sn_invent',
		'radwin_idu_sn_invent', 'radwin_cbw_invent', 'radwin_mimo_diversity_invent',
		'radwin_link_distance_invent', 'radwin_ssid_invent')
config = {}

def main():
	p2p_query = """
		select 
		d.device_name, d.device_alias, d.ip_address, s.name site, dt.name dtye
		from 
		device_device d 
		left join 
		site_instance_siteinstance s 
		on 
		d.site_instance_id=s.id and d.machine_id = s.machine_id 
		left join 
		device_devicetechnology t
		on 
		t.id = d.device_technology and t.name = 'P2P'
		left join device_devicetype dt
		on
		dt.id = d.device_type
		where
		d.is_added_to_nms = 0 and d.is_deleted = 0 and t.name != '' and dt.name != '' and
		dt.name != 'Default' and s.name != '';
	"""

        db = mysql_conn()
	cur = db.cursor()
	cur.execute(p2p_query)
	data = cur.fetchall()
	cur.close()

	return data


def edit_service_query():
	query =  """
		select 
                d.device_name
                from 
                device_device d 
                left join 
                site_instance_siteinstance s 
                on 
                d.site_instance_id=s.id and d.machine_id = s.machine_id 
                left join 
                device_devicetechnology t
                on 
                t.id = d.device_technology and t.name = 'P2P'
                left join device_devicetype dt
                on
                dt.id = d.device_type
                where
                d.is_monitored_on_nms = 2 and t.name != '' and dt.name != '' and
                dt.name != 'Default' and s.name != '';
        """
 
        db = mysql_conn()
	cur = db.cursor()
	cur.execute(query)
	data = cur.fetchall()
	print "Edit data"
	print data
	cur.close()

	return data
			

def edit_services(hostlist):
	query= """
	select * from service_deviceserviceconfiguration where device_name IN
	"""
	query += " %s " % pprint.pformat(hostlist)
	query += "and is_edited = 2;"
	db = mysql_conn()
        cur = db.cursor()
        cur.execute(query)
        data = cur.fetchall()
	print "edited services"
        print data
        cur.close()
 

def edit_service_template():
	query = """
		select 
		s.name, sd.name, sd.warning,sd.critical 
		from 
		service_service_service_data_sources sds
		left join 
		service_service s 
		on 
		s.id=sds.service_id
		left join 
		service_servicedatasource sd 
		on 
		sd.id = sds.servicedatasource_id
		where sd.warning != "" and sd.critical != "" and sd.is_edited =1;
	"""
	payload = {'mode': 'editservice'}
	db = mysql_conn()
        cur = db.cursor()
        cur.execute(query)
        data = cur.fetchall()
        print "edited service template"
        print data
	url  = 'http://omdadmin:omd@localhost/master_UA/check_mk/nocout.py'
	for e in data:
		payload['service_name'] = e[0]
		payload['cmd_params'] = json.dumps({e[1]: {'warning': int(e[2]), 'critical': int(e[3])}})
		payload['edit_servicetemplate'] = 1
		print 'payload'
		print payload
		try:
		        response = send_to_deviceapp(payload, url=url)
			print 'response'
			print response
			# Update table service_servicedatasource
			query = """
				UPDATE service_servicedatasource
				SET
				is_edited = 0
				WHERE
			"""
			query += " name = '%s'" % e[1]
			print query
			cur.execute(query)
			# Update table service_deviceserviceconfiguration
			query = """
				UPDATE service_deviceserviceconfiguration
				SET"""
			query += " warning = %s, critical = %s" % (e[2], e[3])
			query += " WHERE service_name = '%s'" % e[0]
			print query

			cur.execute(query)
			db.commit()
		except Exception, e:
			print 'Error : ' + pprint.pformat(e)
        cur.close()


def mysql_conn():
	db = mysql.connector.connect(
			user=config.get('user'),
			host=config.get('host'),
			password=config.get('password'),
			database=config.get('database'),
			port=config.get('port'))

	return db


def extract_service_snmp_parameters(device_type):
	snmp_parameter = None
	if device_type:
		query = """
			select agent_tag from device_devicetype where name =
			"""
		query += " '%s' " % (device_type)

		db = mysql_conn()
        	cur = db.cursor()
        	cur.execute(query)
        	snmp_parameter = cur.fetchall()
	
	return snmp_parameter

def add_hosts(data):
	# Devices which are successfully added
	added_devices = []
	keys = ['device_name', 'device_alias', 'ip_address', 'site', 'device_type']
	payload = {}
	response = {}
	url = 'http://omdadmin:omd@localhost/master_UA/check_mk/nocout.py'
	for i, p in enumerate(data):
		snmp_tag = extract_service_snmp_parameters(p[4])
		snmp_tag = snmp_tag[0][0]
		print 'snmp_tag'
		print snmp_tag
		if not snmp_tag:
			snmp_tag = "snmp-v1|snmp"
		payload = dict(zip(keys, p))
		payload.update({
			"agent_tag": snmp_tag,
			"mode": "addhost"
			})
		try:
		        response = literal_eval(send_to_deviceapp(payload, url=url))
		except Exception, e:
			print 'Bad response from DA: Host - ' + pprint.pformat(payload)
		if response.get('success') == 1:
			device = payload.get('device_name')
			device, snmp_tag = str(device), str(snmp_tag)
			added_devices.append({device: snmp_tag})
		response = {}
	return added_devices

def send_to_deviceapp(payload, url=None):
	r = requests.post(url=url, data=payload)

	return r.text


def get_service_data_sources(services):
	service_info = []
	serv_id_query = """
	SELECT serv.id, serv.name, serv.parameters_id from service_service serv WHERE
	serv.name IN
	"""
	serv_id_query += " %s" % pprint.pformat(services)
	db = mysql_conn()
	cur = db.cursor()
	cur.execute(serv_id_query)
        data = cur.fetchall()
	for s_id in data:
		serv_tuple = (s_id[0], s_id[1], s_id[2])
		service_info.append(serv_tuple)
	

        ds_query = """
		SELECT s_ds_table.service_id, GROUP_CONCAT(CONCAT(sds.name, '|', sds.warning, '|', sds.critical)) 
		FROM 
		service_service_service_data_sources s_ds_table
		LEFT JOIN
		service_servicedatasource sds
		ON
		sds.id = s_ds_table.servicedatasource_id
		WHERE
		s_ds_table.service_id IN
	"""
	ds_query += " %s GROUP BY s_ds_table.service_id" % pprint.pformat(tuple(map(lambda x: int(x[0]), service_info)))


	cur.execute(ds_query)
	ds_data = cur.fetchall()

        serv_param_ids = tuple(map(lambda t: int(t[2]), service_info))
	serv_param_query = """
		SELECT serv_param.id, serv_param.parameter_description, serv_param.normal_check_interval,
		serv_param.retry_check_interval, serv_param.max_check_attempts ,sp.port,sp.version ,sp.read_community 
		FROM
		service_serviceparameters serv_param
		LEFT JOIN
		service_protocol sp
		on serv_param.protocol_id = sp.id
		WHERE
		serv_param.id IN
	"""
	serv_param_query += " %s" % pprint.pformat(serv_param_ids)
	cur.execute(serv_param_query)
	serv_params = cur.fetchall()

	#print "serv_params..."
	#print serv_params
	service_datasource_mapping = dict(zip(map(lambda t: t[1], service_info), map(lambda t: t[1], ds_data)))

	serv_servparam_mapping = {}
	for s in service_info:
		serv_servparam_mapping[s[1]] = filter(lambda t: t[0] == int(s[2]), serv_params)

	#print serv_servparam_mapping	
	cur.close()

	return service_datasource_mapping, serv_servparam_mapping


def insert_data(data, table=None, keys= []):
	db = mysql_conn()
	cur = db.cursor()
	table = 'service_deviceserviceconfiguration'
	insert_query = "INSERT INTO `%s`" % table
	insert_query += """
		(device_name, service_name, agent_tag, port,
		data_source, version, read_community, svc_template, normal_check_interval,
		retry_check_interval, max_check_attempts, warning, 
		critical, added_on, modified_on, is_added)
		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
		%s, %s, %s, %s, %s)
	"""
	try:
		cur.executemany(insert_query, data)
	except Exception, e:
		print 'Config insertion error: ' + pprint.pformat(e)
	db.commit()
	cur.close()

def delete_device_template():
	query= 	"""
		select 
		d.device_name
		from 
		device_device d 
		left join 
		site_instance_siteinstance s 
		on 
		d.site_instance_id=s.id and d.machine_id = s.machine_id 
		left join 
		device_devicetechnology t
		on 
		t.id = d.device_technology and t.name = 'P2P'
		left join device_devicetype dt
		on
		dt.id = d.device_type
		where
		d.is_deleted = 1 and t.name != '' and dt.name != '' and
		dt.name != 'Default' and s.name != '';
		"""
	db = mysql_conn()
	cur = db.cursor()
	cur.execute(query)
	device_list = cur.fetchall()
	payload = {}
	payload = {'mode': 'deletehost'}
	url = 'http://omdadmin:omd@localhost/master_UA/check_mk/nocout.py'
	for device in device_list:
		payload.update({
                        "device_name": device[0],
                        })
		try:
                        response = literal_eval(send_to_deviceapp(payload, url=url))
			print 'delete response'
			print response
                except Exception, e:
                        print 'Bulk Host deletion error from DA:' + pprint.pformat(payload)
	cur.close()

	

def delete_service_template():
	query = """
	        select device_name, group_concat(distinct service_name) from service_deviceserviceconfiguration 
		where is_edited = 2
		group by device_name;
		"""

	db = mysql_conn()
	cur = db.cursor()
	cur.execute(query)
	device_list = cur.fetchall()
	payload = {}
	payload = {'mode':'deleteservice'}
	url = 'http://omdadmin:omd@localhost/master_UA/check_mk/nocout.py'
	for entry in device_list:
		for serv in entry[1]:
			payload.update({
				"device_name": entry[0],
				"service_name" : serv,
				})
		try:
                        response = literal_eval(send_to_deviceapp(payload, url=url))
                except Exception, e:
                        print 'Bulk service deletion error from DA:' + pprint.pformat(payload)

	query = """
	Delete from service_deviceserviceconfiguration
	where
	is_edited = 2
	"""
        cur.execute(query)
	db.commit()
	cur.close()
	db.close()

	
def edit_flags_device_device(device_list,flag1=None,flag2=None,flag3=None):

	db = mysql_conn()
        cur = db.cursor()
	if not device_list:
		return 

	try:
		if flag1:
			query = """
				update device_device set is_added_to_nms = 1 where device_name IN
				"""
			query += " %s " % pprint.pformat(tuple(device_list))
        		cur.execute(query)
			db.commit()

		if flag2:
			query = """
				update device_device set is_monitored_on_nms = 1 where device_name IN
				"""
			query += " %s " % pprint.pformat(tuple(device_list))
		
        		cur.execute(query)
			db.commit()
		if flag3:
			query = """
				update device_device set is_deleted = 1 where device_name IN
				"""
			query += " %s " % pprint.pformat(tuple(device_list))
		
        		cur.execute(query)
			db.commit()
		cur.close()
	except Exception, e:
		print 'Flag insertion error: ' + pprint.pformat(e)	


def set_ping_levels():
	query = """
	SELECT dt.name, dt.packets, dt.timeout, dt.rta_warning, dt.rta_critical,
	dt.pl_warning, dt.pl_critical
	FROM device_devicetype dt
	WHERE
	dt.name != 'Default'
	"""
	db = mysql_conn()
	cur = db.cursor()
	cur.execute(query)
	data = cur.fetchall()
	ping_levels_list = []
	payload = {
			'mode': 'set_ping_levels'
			}
	for d in data:
		ping_levels = {
			'device_type': d[0],
			'rta': (int(d[3]), int(d[4])),
			'loss': (int(d[5]), int(d[6])),
			'timeout': int(d[2]),
			'packets': int(d[1])
		}
		#ping_levels = json.dumps(ping_levels)
		ping_levels_list.append(ping_levels)
	#ping_levels_list = json.dumps(ping_levels_list)
	payload.update({'ping_levels_list': ping_levels_list})
	payload = urllib.urlencode(payload)
	url  = 'http://omdadmin:omd@localhost/master_UA/check_mk/nocout.py'
	response = send_to_deviceapp(payload, url)


def entry(**kw):
	global config
	config = {}
	config.update({
		'user': kw.get('user'),
		'password': kw.get('sql_passwd'),
		'host': kw.get('ip'),
		'database': kw.get('sql_db'),
		'port': kw.get('sql_port')
		})
	print 'config'
	print config
	global g_services
	device_config_keys = ['device_name', 'service_name', 'agent_tag', 'port',
			'data_source', 'version', 'read_community', 'svc_template', 'normal_check_interval',
			'retry_check_interval', 'max_check_attempts', 'warning',
			'critical', 'added_on', 'modified_on', 'is_added']
	t1 = time.time()
	added_devices = []
	device_service_conf = []


	# code commented for the single service edit
	"""
	data1 = edit_service_query()
	t=[]
	for device in data1:
		t.append(device[0])
	edit_services_host  = tuple(t)
	edit_services(edit_services_host)
	"""		
	# Add bulk ping levels based on device type tag
	set_ping_levels()
	data = main()
	# Find the fresh devices (with is_added_to_nms is zero)
	added_devices = add_hosts(data)
	service_data_sources, service_parameters = get_service_data_sources(g_services)
	# Update is_added_to_nms and is_monitored_on_nms in the device_device flag
	edit_flags_device_device(sum(map(lambda t: t.keys() ,added_devices), []),flag1 = "is_added_to_nms",flag2= "is_monitored_on_nms",flag3=None)
	print '\n added devices'
	print added_devices
	#print '\nservice_data_sources'
	#print service_data_sources
	#print '\nservice_parameters'
	#print service_parameters


	# Insert the device's config info into db
	for d in added_devices:
		for s in g_services:
			data_sources = service_data_sources.get(s).split(',')
			s_param = service_parameters.get(s)[0]
			for ds in data_sources:
				splitted_ds = ds.split('|')
				this_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
				entry = (d.keys()[0], s, d.values()[0], s_param[5], splitted_ds[0], s_param[6], s_param[7],
						s_param[1], s_param[2], s_param[3], s_param[4],
						splitted_ds[1], splitted_ds[2], this_time, this_time, 1)
				device_service_conf.append(entry)
	
	#print '\ndevice_service_conf'
	#print device_service_conf[23:45]
	time.sleep(1)
	insert_data(device_service_conf, table = 'service_deviceserviceconfiguration',
			keys = device_config_keys)
	# Bulk service edit
	edit_service_template()
	# Bulk device delete	
	delete_device_template()
	#Bulk service delete
	delete_service_template()
	print '\nTotal time taken'
	print time.time() - t1 


if __name__ == '__main__':
	entry()

