"""
network_etl.py
================

This script collects and stores data for all services 
running on all configured devices for this poller.

"""

import re
from datetime import datetime, timedelta
import socket
from itertools import izip_longest
from celery import group

from start import app
from db_ops import *


def calculate_refer_field_for_host(device_first_down_list, host_name, ds_values, 
		local_timestamp):
	device_first_down = {}
	device_first_down_entry = []
	refer = ''
	try:
		device_first_down_entry = filter(lambda x: host_name == x['host'], 
				device_first_down_list)
		if device_first_down_entry:
			device_first_down = device_first_down_entry[0]
		else:
			return refer
		if (device_first_down == {} and ds_values['cur'] == '100'):
			device_first_down['host'] = host_name
			device_first_down['severity'] = "down"
			device_first_down['time'] = local_timestamp
			device_first_down_list.append(device_first_down)
		elif (device_first_down and host_name ==  device_first_down['host'] and 
		    ds_values['cur'] != '100'):
			device_first_down['severity'] = "up"
		elif (device_first_down and host_name == device_first_down['host'] and 
				device_first_down['severity'] == "up" and 
				ds_values['cur'] == '100'):
			device_first_down['severity'] = "down"
			device_first_down['time'] = local_timestamp
		if device_first_down['time']:
			refer = device_first_down['time']
	except Exception as exc:
		# printing the exc for now
		print 'Exc in host refer field: ', exc
	return  refer	

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


@app.task(base=DatabaseTask, name='build-export')
def build_export(site, network_perf_data):
	""" processes and prepares data for db insert"""
	
    # contains one dict value for each service data source
	data_array = []
	for h_chk_val in network_perf_data:
		if not h_chk_val:
			continue
		data_dict = {}
		threshold_values = {}
		host_severity = host_state = 'unknown'
		refer = ''
		# Process network perf data
		device_first_down_list = list(build_export.mongo_cnx(site).device_first_down.find())
		try:
			threshold_values = get_threshold(h_chk_val[-1])
			rt_min = threshold_values.get('rtmin').get('cur')
			rt_max = threshold_values.get('rtmax').get('cur')
			# rtmin, rtmax values are not used in perf calc
			threshold_values.pop('rtmin', '')
			threshold_values.pop('rtmax', '')
			# TODO :: use `assert` to check for entry sanity
			if h_chk_val[2] == 0:
				host_state = 'up'
			elif h_chk_val[2] == 1:
				host_state = 'down'
			# Age of last service state change
			age = h_chk_val[-2]
		except:
			# TODO :: should not return empty values
			pass

		for ds, ds_values in threshold_values.items():
			check_time = datetime.fromtimestamp(float(h_chk_val[3]))
			# since we are processing data every minute,
			# so pivot the time stamp to next minute time frame
			local_timestamp = pivot_timestamp_fwd(check_time)
			host_severity = host_state
			if ds == 'pl':
				host_severity = calculate_host_severity_for_pl(ds_values, host_severity)	
				refer = calculate_refer_field_for_host(device_first_down_list, 
						str(h_chk_val[0]), ds_values, local_timestamp)
				c_min, c_max = None, None
			if ds == 'rta':
				host_severity = calculate_host_severity_for_letency(ds_values, host_severity)	
				c_min, c_max = rt_min, rt_max
			data_dict.update({
				# since we are usig 'pyformat' style for string formatting 
				# with executemany, for mysql insert, dict key names should 
				# not be altered or else mysql insert will fail
				'device_name': str(h_chk_val[0]),
				'service_name': 'ping',
				'machine_name': site[:-8], 
				'site_name': site,
				'ip_address': str(h_chk_val[1]),
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
	aggregator.s(data_array, site).apply_async()


@app.task(name='get-host-checks', ignore_result=True)
def get_host_checks_output(site_name=None):
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
		print 'Exc in get socket: ', exc
		nw_qry_output = []
	if nw_qry_output:
		# send build_export with 1000 hosts data [configurable]
		for club_data in izip_longest(*[iter(nw_qry_output)] * 1000):
			build_export.s(site_name, club_data).apply_async()


@app.task(base=DatabaseTask, name='aggregator')
def aggregator(data_values, site):
	""" sends task messages"""

	if data_values:
		# mongo/mysql inserts/updates
		group(
				[mongo_update.s(data_values, ('device_name', 'service_name', 'data_source'), 
					'network_status', site), 
					mongo_insert.s(data_values, 'network_perf', site),
					mysql_insert_handler.s(data_values, site)]
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
			print 'socket timeout ..Exiting'
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


@app.task(name='network-main-pub')
def main(**opts):
	opts = {'site_name': 'pardeep_subordinate_1'}
	get_host_checks_output.s(**opts).apply_async()


if __name__ == '__main__':
	main()
