"""
network_etl.py
================

This script collects and stores data for host checks
running on all configured devices for this poller.

"""


from ast import literal_eval
from ConfigParser import ConfigParser
from datetime import datetime, timedelta
from itertools import izip_longest
import re
import socket,time
from sys import path

from celery import group

#path.append('/omd/nocout_etl')

from handlers.db_ops import *
from start.start import app

DB_CONF = getattr(app.conf, 'CNX_FROM_CONF', None)

logger = get_task_logger(__name__)
info , warning, error = logger.info, logger.warning, logger.error


def calculate_refer_field_for_host(device_first_down, host_name, ds_values, 
	check_timestamp):
	refer = ''
	try:
		if (device_first_down is None and ds_values['cur'] == '100'):
			device_first_down = {}
			device_first_down['device_name'] = host_name
			device_first_down['severity'] = "down"
			device_first_down['check_timestamp'] = check_timestamp
			#device_first_down_list.append(device_first_down)
		elif (device_first_down and ds_values['cur'] != '100'):
			device_first_down['severity'] = "up"
		elif (device_first_down and device_first_down['severity'] == "up" and 
				ds_values['cur'] == '100'):
			device_first_down['severity'] = "down"
			device_first_down['check_timestamp'] = check_timestamp
		if device_first_down and device_first_down.get('time'):
			refer = device_first_down['check_timestamp']
	except Exception as exc:
		# printing the exc for now
		error('Exc in host refer field: {}'.format(exc))

	return  refer, device_first_down

def calculate_host_severity_for_pl(ds_values,host_severity):
	ds_values['cur'] = ds_values['cur'].strip('%')
	try:
		pl_war = ds_values['war']
		pl_crit = ds_values['cric']
		pl_cur = ds_values['cur']
	except:
		pl_war=None
		pl_crit=None
		pl_cur=None
	if pl_cur and pl_war and pl_crit:
		pl_cur = float(pl_cur)
		pl_war = float(pl_war)
		pl_crit = float(pl_crit)
		if pl_cur < pl_war:
			host_severity = "up"
		elif pl_cur >= pl_war and pl_cur <= pl_crit:
			host_severity = "warning"
		else:
			host_severity = "down"

	return host_severity

def calculate_host_severity_for_letency(ds_values,host_severity):	
	try:
		rta_war =  ds_values['war']
		rta_crit = ds_values['cric']
		rta_cur =  ds_values['cur']
	except:
		rta_war = None
		rta_cur =  None
		rta_crit= None
	if  rta_cur and rta_war and rta_crit:
		rta_cur = float(rta_cur)
		rta_war = float(rta_war)
		rta_crit = float(rta_crit)
		if rta_cur < rta_war:
			host_severity = "up"
		elif (rta_cur >= rta_war) and (rta_cur <= rta_crit):
			host_severity = "warning"
		else:
			host_severity = "down"
	return host_severity


@app.task(base=DatabaseTask, name='build-export-host')
def build_export(site, network_perf_data):
	""" processes and prepares data for db insert"""

	# contains one dict value for each service data source
	data_array = []
	# last down time for devices
	rds_cli = RedisInterface()
	last_down_all = rds_cli.multi_get(key_prefix='last_down')
	p = rds_cli.redis_cnx.pipeline(transaction=True)
	# values updated during current execution, only these
	# values should be updated into redis
	last_down_updated_all = []
	for h_chk_val in network_perf_data:
		if not h_chk_val:
			continue
		#try:
		#	h_chk_val = literal_eval(h_chk_val)
		#except Exception as exc:
		#	error('Error in json loading: %s' % exc)
		#	continue
		data_dict = {}
		threshold_values = {}
		host_severity = host_state = h_chk_val['state'] if h_chk_val.get('state') \
				else 'unknown'
		refer = ''
		device_name = str(h_chk_val['host_name'])
		device_down_entry = None
		# Process network perf data
		try:
			threshold_values = get_threshold(h_chk_val.get('perf_data'))
			# TODO: include rt_min, rt_max values if needed
			c_min, c_max = None, None
			# rt_min and rt_max are not needed for perf calculations
			threshold_values.pop('rtmin', '')
			threshold_values.pop('rtmax', '')
			# Age of last service state change
			age = h_chk_val['last_state_change']
		except:
			# TODO :: should not return empty values
			pass

		for ds, ds_values in threshold_values.items():
			check_time = datetime.fromtimestamp(float(h_chk_val['last_chk']))
			# since we are processing data every minute,
			# so pivot the time stamp to next minute time frame
			local_timestamp = pivot_timestamp_fwd(check_time)
			host_severity = host_state
			if ds == 'pl':
				host_severity = calculate_host_severity_for_pl(ds_values, host_severity)
				for i, entry in enumerate(last_down_all):
					if str(entry['device_name']) == device_name:
						device_down_entry = entry
						last_down_all.pop(i)
						break
				refer, device_down_entry = calculate_refer_field_for_host(device_down_entry, 
						device_name, ds_values, local_timestamp)
				if device_down_entry:
					last_down_updated_all.append(device_down_entry)
				key = 'availibility' + ':' + site + ':' + device_name + ':' + str(h_chk_val['address'])
				p.rpush(key,ds_values.get('cur'))
			if ds == 'rta':
				host_severity = calculate_host_severity_for_letency(ds_values, host_severity)	
			data_dict.update({
				# since we are usig 'pyformat' style for string formatting 
				# with executemany, for mysql insert, dict key names should 
				# not be altered or else mysql insert will fail
				'device_name': device_name,
				'service_name': 'ping',
				'machine_name': site, 
				'site_name': site,
				'ip_address': str(h_chk_val['address']),
				'data_source': ds,
				'severity': host_severity,
				'current_value': ds_values.get('cur'),
				'min_value': c_min,
				'max_value': c_max,
				'avg_value': ds_values.get('cur'),
				'warning_threshold': ds_values.get('war'),
				'critical_threshold': ds_values.get('cric'),
				'sys_timestamp': local_timestamp ,
				'check_timestamp': check_time,
				'age': age,
				'refer':refer,
				})
			data_array.append(data_dict)
			data_dict = {}
		
	# send aggregator task
	aggregator.s(data_array, last_down_updated_all, site).apply_async()
	try:
		p.execute()
	except Exception,e:
		warning('Network-Error: {0}'.format(e))
		pass

@app.task(name='device_availibility', ignore_result=True)
def device_availibility(site_name=None):
	service = "availability"
	DB_CONF = getattr(app.conf, 'CNX_FROM_CONF', None)
	conf = ConfigParser()
	conf.read(DB_CONF)
	site = conf.get('machine','machine_name')
	redis_cli =RedisInterface()
	p = redis_cli.redis_cnx.pipeline()
	host_keys = redis_cli.redis_cnx.keys(pattern="availibility:%s:*" % site)
	[p.lrange(k, 0,-1) for k  in host_keys]
	host_availibility_info = p.execute()
	ds="availability"
	host_state = "ok"
	availability_list = []
	for key,value in zip(host_keys,host_availibility_info):
		#warning('key: {0}{1}'.format(key,value))
		key_names = key.split(':')
		try:
			ip_address = key_names[3]
		except:
			ip_address = ""
		host_name = key_names[2]
		#value = eval(value)
		down_count = value.count('100')
		total_down = ((down_count * 5)/(24*60.0) *100)
		if total_down >=100:
			total_down = 100.0
		total_up = "%.2f" % (100 -total_down )
		current_time = int(time.time())
		availability_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,device_name=host_name,
						service_name=service,current_value=total_up,min_value=0,max_value=0,avg_value=0,
						data_source=ds,severity=host_state,site_name=site,warning_threshold=0,
						machine_name=site,
						critical_threshold=0,ip_address=ip_address)
		availability_list.append(availability_dict)	
		availability_dict = {}
	availibility_mysql_insert.s( 'performance_networkavailabilitydaily',availability_list,site).apply_async()
	#warning('host availibility: {0}'.format(availability_list))


@app.task(name='get-host-checks', ignore_result=True)
def get_host_checks_output(site_name=None):
	# initialize redis connection
	queue = RedisInterface(perf_q='q:perf:host')
	# get host check results from redis backed queue
	# pulling 1000 values from queue, at a time
	host_check_results = queue.get(0, -1)
	if host_check_results:
		build_export.s(site_name, host_check_results).apply_async()


#@app.task(name='get-host-checks', ignore_result=True)
def get_host_checks_output_old(site_name=None):
	"""Live query on `hosts` check_mk table"""

	start_time = (datetime.now() - timedelta(minutes=1)
		).replace(second=0, microsecond=0)
	end_time = start_time + timedelta(minutes=1)
	start_time, end_time = start_time.strftime('%s'), end_time.strftime('%s')
	network_live_query = "GET hosts\n"+\
			"Columns: host_name host_address host_state last_check "+\
			"host_last_state_change host_perf_data\n"+\
			"Filter: last_check >= %s\n" % start_time+\
			"Filter: last_check < %s\n" % end_time+\
			"OutputFormat: python\n"

	try:
		nw_qry_output = eval(get_from_socket(site_name, network_live_query))
	except Exception as exc:
		error('Exc in get socket: {}'.format(exc))
		nw_qry_output = []
	if nw_qry_output:
		# send build_export with 1000 hosts data [configurable]
		for club_data in izip_longest(*[iter(nw_qry_output)] * 1000):
			build_export.s(site_name, club_data).apply_async()


@app.task(base=DatabaseTask, name='aggregator-host')
def aggregator(data_values, last_down_devices, site):
	""" sends task messages"""

	if data_values:
		# redis/mysql inserts/updates
		#group(
		#		[rds_cli.redis_update.s(data_values, perf_type='status'),
		#			rds_cli.redis_insert.s(data_values, perf_type='live'),
		#			mysql_insert_handler.s(data_values, site)]
		#		).apply_async()

		# mongo/mysql inserts/updates
		rds_cli = RedisInterface()
		warning('site name in network etl: {0}'.format(site))
		group([
			rds_cli.redis_update.s(last_down_devices, perf_type='last_down'),
			#mongo_update.s(data_values, 
			#	('device_name', 'service_name', 'data_source'), 'network_status', site), 
			#mongo_insert.s(data_values, 'network_perf', site),
			mysql_insert_handler.s(data_values, 'performance_performancenetwork', 
				'performance_networkstatus', 'network_perf', site)
			]
			).apply_async()


def get_from_socket(site_name, query):
	"""collect query data from the live unix socket"""

	socket_path = "/omd/sites/%s/tmp/run/live" % site_name
	#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(socket_path)
	s.settimeout(60.0)
	s.send(query)
	s.shutdown(socket.SHUT_WR)
	output = ''
	while True:
		try:
	 		out = s.recv(100000000)
		except socket.timeout:
			error('socket timeout ..Exiting')
			break
		out.strip()
		if not len(out):
			break
		output += out

	return output


def get_threshold(perf_data):
	"""
	function for parsing the performance data output
	collected from LQL
	"""

	threshold_values = {}
	if not len(perf_data):
		return threshold_values
	for param in perf_data.split(" "):
		param = param.strip("['\n', ' ']")
		if param.partition('=')[2]:
				if ';' in param.split("=")[1]:
						threshold_values[param.split("=")[0]] = {
						"war": re.sub('ms', '', param.split("=")[1].split(";")[1]),
						"cric": re.sub('ms', '', param.split("=")[1].split(";")[2]),
						"cur": re.sub('ms', '', param.split("=")[1].split(";")[0])
						}
				else:
						threshold_values[param.split("=")[0]] = {
						"war": None,
						"cric": None,
						"cur": re.sub('ms', '', param.split("=")[1].strip("\n"))
						}
		else:
			threshold_values[param.split("=")[0]] = {
				"war": None,
				"cric": None,
				"cur": None
							}

	return threshold_values


def pivot_timestamp_fwd(timestamp):
	""" pivot the time to at start of next minute"""

	return ((timestamp + timedelta(minutes=1)
		).replace(second=0, microsecond=0))


@app.task(name='network-main')
def main(**opts):
	#opts = {'site_name': 'pub_subordinate_1'}
	DB_CONF = getattr(app.conf, 'CNX_FROM_CONF', None)
	conf = ConfigParser()
	conf.read(DB_CONF)
	opts = {'site_name': conf.get('machine','machine_name')}

	get_host_checks_output.s(**opts).apply_async()


if __name__ == '__main__':
	main()
