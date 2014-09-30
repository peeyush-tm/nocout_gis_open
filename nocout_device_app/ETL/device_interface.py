from MySQLdb import connect
import requests
from ast import literal_eval
import pprint
from datetime import datetime
import time


g_services = ('radwin_rssi', 'radwin_uptime', 'radwin_uas', 'radwin_service_throughput',
		'radwin_dl_utilization', 'radwin_ul_utilization', 'radwin_link_ethernet_status',
		'radwin_port_mode_status', 'radwin_port_speed_status', 'radwin_autonegotiation_status',
		'radwin_frequency_invent', 'radwin_producttype_invent', 'radwin_odu_sn_invent',
		'radwin_idu_sn_invent', 'radwin_cbw_invent', 'radwin_mimo_diversity_invent',
		'radwin_link_distance_invent', 'radwin_ssid_invent')

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
		t.name != '' and dt.name != '' and dt.name != 'Default' and s.name != '';
	"""

        db = mysql_conn()
	cur = db.cursor()
	cur.execute(p2p_query)
	data = cur.fetchall()
	cur.close()

	return data


def mysql_conn():
	db = connect(user='root', host='localhost', passwd='root', db='nocout_dev_27_08_14')

	return db


def add_hosts(data):
	# Devices which are successfully added
	added_devices = []
	keys = ['device_name', 'device_alias', 'ip_address', 'site', 'device_type']
	payload = {}
	url = 'http://omdadmin:omd@localhost/master_UA/check_mk/nocout.py'
	for i, p in enumerate(data):
		payload = dict(zip(keys, p))
		payload.update({
			"site": "pardeep_slave_1",
			"agent_tag": "snmp-v1|snmp",
			"mode": "addhost",
			"ping_levels": "{'rta': (800, 1300), 'loss': (70, 100), 'timeout': 10, 'packets': 6}"
			})
		try:
		        response = literal_eval(send_to_deviceapp(payload, url=url))
		except Exception, e:
			print 'Bad response from DA: Host - ' + pprint.pformat(payload)
		if response.get('success') == 1:
			added_devices.append(payload.get('device_name'))
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
		serv_param.retry_check_interval, serv_param.max_check_attempts
		FROM
		service_serviceparameters serv_param
		WHERE
		serv_param.id IN
	"""
	serv_param_query += " %s" % pprint.pformat(serv_param_ids)
	cur.execute(serv_param_query)
	serv_params = cur.fetchall()

	service_datasource_mapping = dict(zip(map(lambda t: t[1], service_info), map(lambda t: t[1], ds_data)))

	serv_servparam_mapping = {}
	for s in service_info:
		serv_servparam_mapping[s[1]] = filter(lambda t: t[0] == int(s[2]), serv_params)
	
	cur.close()

	return service_datasource_mapping, serv_servparam_mapping


def insert_data(config):
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
		cur.executemany(insert_query, config)
	except Exception, e:
		print 'Config insertion error: ' + pprint.pformat(e)
	db.commit()
	cur.close()


if __name__ == '__main__':
	#global g_services
	t1 = time.time()
	added_devices = []
	device_service_conf = []
	data = main()
	added_devices = add_hosts(data)
	service_data_sources, service_parameters = get_service_data_sources(g_services)
	print '\nservice_data_sources'
	print service_data_sources
	print '\nservice_parameters'
	print service_parameters
	# Insert the device's config info into db
	for d in added_devices:
		for s in g_services:
			data_sources = service_data_sources.get(s).split(',')
			s_param = service_parameters.get(s)[0]
			for ds in data_sources:
				splitted_ds = ds.split('|')
				this_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
				entry = (d, s, 'snmp', 161, splitted_ds[0], 'v1', 'public',
						s_param[1], s_param[2], s_param[3], s_param[4],
						splitted_ds[1], splitted_ds[2], this_time, this_time, 1)
				device_service_conf.append(entry)
	
	print '\nNo of entries'
	print len(device_service_conf)
	time.sleep(1)
	insert_data(device_service_conf)
	print '\nTotal time taken'
	print time.time() - t1 


