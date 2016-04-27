"""
service_etl.py
================
This script collects and stores data for host checks
running on all configured devices for this poller.
"""


from ast import literal_eval
from ConfigParser import ConfigParser
from datetime import datetime, timedelta
import re
from sys import path
import sys

from celery import group

from handlers.db_ops import *
from start.start import app

logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error

path.append('/omd/nocout_etl')

INVENTORY_DB = getattr(app.conf, 'INVENTORY_DB', 3)



def splitter(perf, delimiters, indexes):
	out = []
	for p in perf:
		for t in zip(delimiters, indexes):
			temp = p.split(t[0])[t[1]]
			p = temp
		out.append(p)

	return out


# TODO: don't process data for down BS devices
def update_topology(li, data_values, name_ip_mapping, delete_old_topology, site):
	""" processes and updates bs-ss connections topology"""
	# splitter = lambda x, sep, i: x.split(sep)[i]
	perf_out = data_values.get('output')
	ss_ips = []
	if perf_out:
		d = {}
		device_name = str(data_values.get('host_name'))
		service_name = str(data_values.get('service_description'))
		now = datetime.now()
		key = 'device_inventory:' + device_name
		ip_address = str(name_ip_mapping.get(key))
		delete_old_topology[0].add(device_name)

		try:
			plugin_output = perf_out.split('- ')[1]
			ss_sec_ids, ss_ports = [], []
			if service_name.startswith('cambium'):
				bs_mac, ss_sec_id, perf = plugin_output.split(' ', 2)
				ss_wise_values = perf.split()
				ss_macs = splitter(ss_wise_values, ('/',), (1,))
				[ss_sec_ids.append(ss_sec_id) for i, _ in enumerate(ss_macs)]
				ss_ips = splitter(ss_wise_values, ('/',), (0,))
				[ss_ports.append(None) for i, _ in enumerate(ss_macs)]
			elif service_name.startswith('wimax'):
				perf = plugin_output
				ss_wise_values = perf.split()
				ss_macs = splitter(ss_wise_values, ('=',), (0,))
				ss_sec_ids = splitter(ss_wise_values, ('=', ','), (1, 8))
				ss_ips = splitter(ss_wise_values, ('=', ','), (1, 9))
				ss_ports = splitter(ss_wise_values, ('=', ','), (1, -1))
		except Exception as exc:
			#error('Error in topology output: {0}, {1}'.format(exc,ss_wise_values))
			pass
		else:
			machine_name = site[:-8]
			for i, ss_ip in enumerate(ss_ips):
				delete_old_topology[1].add(ss_ip)
				d.update({
					'device_name': device_name,
					'ip_address': ip_address,
					'service_name': service_name,
					'data_source': 'topology',
					'sys_timestamp': now,
					'check_timestamp': now,
					'sector_id': ss_sec_ids[i],
					'connected_device_ip': ss_ip,
					'connected_device_mac': ss_macs[i],
					'refer': ss_ports[i],
					'site_name': site,
					'machine_name': site,
					'mac_address': None,
				})
				li.append(d)
				d = {}


@app.task(name='build-export-service')
def build_export(site, perf_data):
	""" processes and prepares data for db insert"""

	# contains one dict value for each service data source
	serv_data = []
	warning('build_export site {0}'.format(site))
	# topology perf data
	topology_serv_data = []
	# util services data
	util_serv_data = []
	kpi_serv_data = []
	interface_serv_data = []
	invent_serv_data = []
	kpi_helper_serv_data = []
	ss_provis_helper_serv_data = []
	# delete topology entries from db, for these bs and ss
	# delete bs based on names and ss on ips
	old_topology = [set(), set()]

	# needed for mrc and dr manipulations
	util_services = ['wimax_pmp1_dl_util_bgp', 'wimax_pmp2_dl_util_bgp', 
					'wimax_pmp1_ul_util_bgp', 'wimax_pmp2_ul_util_bgp']
	# keep last 2 values for severity these services in Redis, kpi checks
	# need their values as input
	kpi_helper_services = ['wimax_ul_cinr', 'wimax_ul_intrf', 'cambium_ul_jitter',
	                'cambium_rereg_count']
	# helper services for ss provisioning - keep last two values of field current_value
	ss_provis_helper_service = ['cambium_ul_rssi', 'cambium_dl_rssi',
					'cambium_dl_jitter', 'cambium_ul_jitter',
					'cambium_rereg_count', 'wimax_ul_rssi',
					'wimax_dl_rssi', 'wimax_dl_cinr', 'wimax_ss_ptx_invent']

	# get device_name --> ip mappings from redis
	rds_cli = RedisInterface(custom_conf={'db': INVENTORY_DB})
	p = rds_cli.redis_cnx.pipeline()
	keys = rds_cli.redis_cnx.keys(pattern='device_inventory:*')
	[p.get(k) for k in keys]
	name_ip_mapping = dict([t for t in zip(keys, p.execute())])

	for chk_val in perf_data:
		dict_perf = {}
		if not chk_val:
			continue
		#if not isinstance(chk_val, dict):
		#	try:
		#		chk_val = literal_eval(chk_val)
		#	except Exception as exc:
		#		error('Error in json loading: %s' % exc)
		#		continue
		service_name = str(chk_val['service_description'])
		device_name = str(chk_val['host_name'])
		# TODO: deliver to appropriate modules, using message queues [producer/consumer]
		# topology services
		if service_name.endswith(('_topology', '_topology_discover')):
			update_topology(topology_serv_data, chk_val, 
					name_ip_mapping, old_topology, site)
		# dr and mrc dependent services
		elif service_name in util_services:
			dict_perf = make_dicts_from_perf(util_serv_data, chk_val,
				name_ip_mapping, site)
		# kpi services
		elif service_name.endswith('_kpi'):
			dict_perf = make_dicts_from_perf(kpi_serv_data, chk_val, 
				name_ip_mapping, site)
		# status services
		elif service_name.endswith('_status'):
			dict_perf = make_dicts_from_perf(interface_serv_data, chk_val, 
				name_ip_mapping, site)
		# invent services
		elif service_name.endswith('_invent'):
			dict_perf = make_dicts_from_perf(invent_serv_data, chk_val, 
				name_ip_mapping, site)
		else:
			dict_perf = make_dicts_from_perf(serv_data, chk_val, 
				name_ip_mapping, site)

		# load values into redis
		if service_name in kpi_helper_services:
			kpi_helper_serv_data.append({
				'severity': dict_perf.get('severity'),
				'device_name': device_name,
				'service_name': service_name
			})
		# load values into redis
		if service_name in ss_provis_helper_service:
			ss_provis_helper_serv_data.append({
				'device_name': device_name,
				'service_name': service_name,
				'current_value': dict_perf.get('current_value')
			})

	# send insert/update tasks
	send_db_tasks.s(serv_data=serv_data,
	                interface_serv_data=interface_serv_data,
	                invent_serv_data=invent_serv_data,
	                kpi_serv_data=kpi_serv_data,
	                topology_serv_data=topology_serv_data,
	                old_topology=old_topology,
	                util_serv_data=util_serv_data,
	                kpi_helper_serv_data=kpi_helper_serv_data,
	                ss_provis_helper_serv_data=ss_provis_helper_serv_data,
	                site=site
	                ).apply_async()


@app.task(name='make-dicts-from-perf')
def make_dicts_from_perf(outs, ins, name_ip_mapping,site, multi=False):
	li = []
	retval = {}
	rici_services = ['wimax_bs_ul_issue_kpi','rici_dl_util_kpi','rici_ul_util_kpi','juniper_switch_dl_util_kpi',
                        'juniper_switch_ul_util_kpi', 'cisco_switch_dl_util_kpi','cisco_switch_ul_util_kpi','huawei_switch_dl_util_kpi','huawei_switch_ul_util_kpi']
	#info('name_ip_mapping: {0}'.format(name_ip_mapping))
	if not multi:
		li.append(ins)
		ins = li
	for chk_val in ins:
		device_name = str(chk_val.get('host_name'))
		service_name = str(chk_val.get('service_description'))
		key = 'device_inventory:' + device_name
		ip_address = name_ip_mapping.get(key)
		data_dict = {}
		threshold_values = {}
		severity = chk_val['state'] if chk_val.get('state') else 'unknown'
		refer = ''
		try:
			refer = str(chk_val.get('refer'))
		except Exception as e:
			pass
			
		# Age of last service state change
		age = chk_val['last_state_change']
		try:
			threshold_values = get_threshold(chk_val.get('perf_data').strip())
		except Exception as exc:
			error('Error in threshold_values: {0}'.format(exc))

		for ds, ds_values in threshold_values.items():
			check_time = datetime.fromtimestamp(float(chk_val['last_chk']))
			try:
				if service_name in rici_services:
					if float(ds_values.get('cur')) < float(ds_values.get('war')):
						severity = 'ok'
					elif float(ds_values.get('cur')) >= float(ds_values.get('cric')):
						severity = 'critical'
					else:
						severity = 'warning' 	
			except Exception as exc:
				#error('Error in Rici kpi services {0}'.format(exc))
				pass
			# since we are processing data every minute,
			# so pivot the time stamp to next minute time frame
			local_timestamp = pivot_timestamp_fwd(check_time)
			data_dict.update({
				# since we are usig 'pyformat' style for string formatting 
				# with executemany, for mysql insert, dict key names should 
				# not be altered or else mysql insert will fail
				'device_name': device_name,
				'service_name': service_name,
				'machine_name': site.split('_')[0],
				'site_name': site,
				'ip_address': ip_address,
				'data_source': ds,
				'severity': severity,
				'current_value': ds_values.get('cur'),
				'min_value': ds_values.get('cur'),
				'max_value': ds_values.get('cur'),
				'avg_value': ds_values.get('cur'),
				'warning_threshold': ds_values.get('war'),
				'critical_threshold': ds_values.get('cric'),
				'sys_timestamp': local_timestamp,
				'check_timestamp': check_time,
				'age': age,
				'refer': refer,
			})
			outs.append(data_dict)
			data_dict = {}
			severity = None

	if outs:
		retval.update({
			'current_value': outs[-1].get('current_value'),
			'severity': outs[-1].get('severity'),
		})

	return retval



@app.task(name='get-service-checks', ignore_result=True)
def get_service_checks_output(site_name=None):
	# get check results from redis backed queue
	# pulling 2000 values from queue, at a time
	queue = RedisInterface(perf_q='q:perf:service')
	check_results = queue.get(0, -1)
	warning('Queue len, size of obj: {0}, {1}'.format(
		len(check_results), sys.getsizeof(check_results)))
	if check_results:
		build_export.s(site_name, check_results).apply_async()

@app.task(name='get-ul-issue-service-checks', ignore_result=True)
def get_ul_issue_service_checks_output(**opt):
	# get check results from redis backed queue
	# pulling 2000 values from queue, at a time
	#DB_CONF = getattr(app.conf, 'CNX_FROM_CONF', None)
	#conf = ConfigParser()
	#conf.read(DB_CONF)
	site_name = opt.get('site_name')
	queue = RedisInterface(perf_q='queue:ul_issue:%s' % site_name)
	check_results = queue.get(0, -1)
	warning('ul_issue Queue len: {0}'.format(len(check_results)))
	if check_results:
		build_export.s(site_name, check_results).apply_async()


@app.task(name='send-db-tasks-service', ignore_result=True)
def send_db_tasks(**kw):
	""" sends task messages into celery task broker"""

	topology_data_fields = ('device_name', 'service_name', 'machine_name',
	                        'site_name', 'sys_timestamp', 'check_timestamp', 
	                        'ip_address', 'sector_id', 'connected_device_ip', 
	                        'connected_device_mac', 'mac_address','data_source')
	#warning('send-db-send**********')
	site = kw.get('site')
	#warning('site name: {0}'.format(site))
	# tasks to be sent
	tasks = []
	rds_cli = RedisInterface()

	if kw.get('kpi_serv_data'):
		kpi_serv_data = kw.get('kpi_serv_data')
		# mongo/mysql inserts/updates for regular services
		mysql_site = site.split('_')[0]
		tasks.extend([
			# mongo_update.s(kpi_serv_data,
			#               ('device_name', 'service_name', 'data_source'),
			#               'kpi_status', site),
			# mongo_insert.s(kpi_serv_data, 'kpi_perf', site),
			mysql_insert_handler.s(kpi_serv_data, 'performance_utilization',
			                       'performance_utilizationstatus', 'kpi_perf', mysql_site)])

	if kw.get('topology_serv_data'):
		topology_serv_data = kw.get('topology_serv_data')
		old_topology = kw.get('old_topology')
		# topology specific tasks --> needs only update
		tasks.extend([
			mysql_insert_handler.s(topology_serv_data, 'performance_topology', None,
			                       None, 'historical', columns=topology_data_fields,
			                       old_topology=old_topology)])
	
	# need to keep the data in redis for kpi checks
	if kw.get('kpi_helper_serv_data'):
		kpi_helper_serv_data = kw.get('kpi_helper_serv_data')
		tasks.extend([
			rds_cli.redis_update.s(kpi_helper_serv_data, update_queue=True,
			                       perf_type='ul_issue')
		])
	# need to keep the data in redis for provis checks
	if kw.get('ss_provis_helper_serv_data'):
		ss_provis_helper_serv_data = kw.get('ss_provis_helper_serv_data')
		tasks.extend([
			rds_cli.multi_set.s(ss_provis_helper_serv_data, perf_type='provis')
		])

	if tasks:
		group(tasks).apply_async()


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


@app.task(name='service-main')
def main(**opts):
	# srv_etl = ServiceEtl()
	#DB_CONF = getattr(app.conf, 'CNX_FROM_CONF', None)
	#conf = ConfigParser()
	#conf.read(DB_CONF)
	opt = {'site_name': opts.get('site__name')}

	get_service_checks_output.s(**opt).apply_async()


if __name__ == '__main__':
	main()

