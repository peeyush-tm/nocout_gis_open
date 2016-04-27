
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
