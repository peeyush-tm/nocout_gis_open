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
import time
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
	#warning('build_export site {0}'.format(site))
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
			#severity = None

	if outs:
		retval.update({
			'current_value': outs[-1].get('current_value'),
			'severity': outs[-1].get('severity'),
		})

	return retval


@app.task(base=DatabaseTask, name='extract_values_from_main_function')
def extract_values_from_main_function(hosts, services, services_thresholds, site_name=None, func=None, batch=500):
    """ Sends messages for given tasks in celery queue"""
    redis_cnx = RedisInterface(custom_conf={'db': INVENTORY_DB}).redis_cnx
    p = redis_cnx.pipeline()
    warning('Sending kpi tasks for: {0} hosts'.format(len(hosts)))
    while  hosts:
        [p.lrange(k, 0 ,-1) for k in hosts[:batch]]
        host_params = p.execute()
	for service in services:
	    args = {}
	    memc = extract_values_from_main_function.memc_cnx
	    try :
	        war = services_thresholds[service + ':war']
                war = war.strip()
	    except Exception,e:
		war = None
            try :
	        crit = services_thresholds[service + ':crit']
	        crit = crit.strip()
	    except Exception,e:
                crit = None
	    local_cnx = RedisInterface()
	    args = {
		    'host_info': host_params,
		    'site_name': site_name,
		    'service': service,
		    'war': war,
		    'crit': crit,
		    'redis': local_cnx,
		    'memc': memc,
		    'my_function': func
	    }
	    calling_func = call_passive_check_output
            calling_func.delay(**args)
        hosts = hosts[batch:]

@app.task(name='call_passive_check_output',ignore_result=True)
def call_passive_check_output(**opt):
	my_function = eval(opt['my_function'])
	my_function(**opt)

def make_service_dict(
        perf, state, hostname, site,
        ip_address, age_of_state, **args):
    service_dict = {}
    service_dict['host_name'] = hostname
    service_dict['address'] = ip_address
    service_dict['site'] = site
    service_dict['perf_data'] = perf
    service_dict['last_state_change'] = age_of_state
    service_dict['state']  = state
    service_dict['last_chk'] = time.time()
    service_dict['service_description']=args['service']
    service_dict['age']= age_of_state
    return service_dict

def make_event_dict(
        perf, state, hostname, site,
        ip_address, age_of_state, **args):

    perf_description = {
    'wimax_dl_rssi' : 'downlink signal strength indication',
    'wimax_ul_rssi' : 'uplink signal strength indication',
    'wimax_dl_cinr' : 'downlink cinr',
    'wimax_ul_cinr' : 'uplink cinr',
    'wimax_dl_intrf' : 'dl intrf',
    'wimax_ul_intrf' : 'ul intrf',
    'wimax_modulation_dl_fec' : 'downlink modulation FEC',
    'wimax_modulation_ul_fec' : 'uplink modulation FEC',
    }

    event_state = {'ok' : 'OK',
    'critical' : 'CRIT',
    'warning' : 'WARN',
    'unknown' : 'UNKNOWN',
    }

    event_dict = {}

    current_value = 'Unknown' if state is 'unknown' else perf.split("=")[1].split(";")[0]

    event_dict['device_name'] = hostname
    event_dict['ip_address'] = ip_address
    event_dict['site_name'] = site
    event_dict['description'] = '%s - Device %s is %s' % (event_state[state],perf_description[args['service']],current_value) ##Make description format
    event_dict['severity']  = state.upper()
    event_dict['sys_timestamp'] = time.time()
    event_dict['check_timestamp'] = time.time()
    event_dict['service_name']= args['service']
    event_dict['data_source']= args['service'].split('_',1)[1]
    #event_dict['age']= age_of_state
    event_dict['machine_name'] = site.split('_')[0]
    event_dict['min_value'] = 0
    event_dict['max_value'] = 0
    event_dict['avg_value'] = 0
    event_dict['current_value'] = 0
    event_dict['warning_threshold'] = 0
    event_dict['critical_threshold'] = 0

    return event_dict

@app.task(name='extract_wimax_topology_fields_value',ignore_result=True)
def extract_wimax_topology_fields_value(**args):
        wimax_services = ['wimax_dl_rssi','wimax_ul_rssi','wimax_dl_cinr','wimax_ul_cinr','wimax_dl_intrf','wimax_ul_intrf','wimax_modulation_dl_fec','wimax_modulation_ul_fec']
        comparison_services = ['wimax_dl_rssi','wimax_ul_rssi','wimax_dl_cinr','wimax_ul_cinr']
        intrf_services = ['wimax_dl_intrf','wimax_ul_intrf']
        mod_services = ['wimax_modulation_dl_fec','wimax_modulation_ul_fec']
	dl_fec_normal =  ["qam1634", "qam6423","qam6434"]
	ul_fec_normal = ["qam1612", "qam1634", "qam6423","qam6434"]
        service_name = args['service']
        host_info = args['host_info']
        memc = args['memc']
	state_string = 'unknown'
        this_time = datetime.now()
	service_list = []
        t_stmp = this_time + timedelta(minutes=-(this_time.minute % 5))
        t_stmp = t_stmp.replace(second=0,microsecond=0)
        current_time =int(time.mktime(t_stmp.timetuple()))
	prefix = service_name.split('_',1)[1]
	event_list = []
	event_columns = ['sys_timestamp','device_name','severity','description','min_value', 'max_value', 'avg_value','current_value',\
                        'data_source','warning_threshold','critical_threshold','check_timestamp','ip_address','service_name',\
                        'site_name','machine_name']

	for entry in host_info:
	    value = ''
	    state = 3
	    state_string = 'unknown'
	    try:
                host_name,site,ip = eval(entry[0])
                key = "%s_mac" % host_name
                mac = memc.get(str(key))
                #error('Wimax mac: {0}'.format(mac))
                value_list = memc.get(mac)
                #error('Wimax output: {0} {1}'.format(value_list,ip))
                value = value_list[wimax_services.index(service_name)+1]

                if service_name in comparison_services :
			value = int(value)
			if value < int(args['crit']):
				state  = 2
				state_string = 'critical'
			elif value >= int(args['crit']) and value <= int(args['war']):
				state = 1
				state_string = 'warning'
			else:
				state = 0
				state_string = 'ok'
			key1 = str(host_name) + "_%s" % prefix + "_" + str(current_time)
			memc.set(key1,value,600)
		elif service_name in intrf_services:
			if value.lower()  == args['crit'].lower():
				state  = 2
				state_string = 'critical'
			elif value.lower()  == args['war'].lower():
				state = 1
				state_string = 'warning'
			elif value.lower() == "Norm".lower():
				state = 0
				state_string = 'ok'
			#perf = '%s' %(prefix) + "=%s" % (value)
		elif service_name in mod_services:
			value1 = "".join(e for e in value if e.isalnum())
			if args['crit']:
				critical_value=map(lambda x: "".join(c for c in x if c.isalnum()) ,args['crit'].split(','))
				crit=map(lambda x: x.replace(' ','-') ,args['crit'].split(','))
				args['crit'] = ",".join(crit)
			if args['war']:
				warning_value=map(lambda x: "".join(c for c in x if c.isalnum()) ,args['war'].split(','))
				warn=map(lambda x: x.replace(' ','-') ,args['war'].split(','))
				args['war'] = ",".join(warn)
			if value1 in critical_value:
				state  = 2
				state_string = 'critical'
			elif value1 in warning_value:
				state  = 1
				state_string = 'warning'
			elif 'dl_fec' in service_name and value1 in dl_fec_normal:
				state  = 0
				state_string = 'ok'
			elif 'ul_fec' in service_name and value1 in ul_fec_normal:
				state  = 0
				state_string = 'ok'
			else:
				state = 3
				state_string = 'unknown'

		#error('perf: {0} {1}'.format(args['war'],args['crit']))
		perf = '%s' %(prefix) + "=%s;%s;%s" % (value,args['war'],args['crit'])
	    except Exception ,e:
		#error('Error in wimax services: {0}, {1} {2}'.format(e,ip,service_name))
		perf = '%s=' %(prefix)
		pass

	    age_of_state,add_to_events = age_since_last_stored_state(host_name, service_name, state_string)
            service_dict = make_service_dict(
	        perf, state_string, host_name, site, ip, age_of_state, **args)
            service_list.append(service_dict)
	#error('len wimax services: {0}'.format(service_list))
	    if add_to_events :
		event_dict = make_event_dict(
                    perf, state_string, host_name, site, ip, age_of_state, **args)
                event_list.append(event_dict)

        if len(service_list) > 0:
            build_export.s(args['site_name'], service_list).apply_async()
        if len(event_list) > 0:
            try :
                mysql_insert_handler.s(event_list,'performance_eventservice','performance_eventservicestatus',None,args['site_name'],
		columns=event_columns).apply_async()
            except Exception ,e :
                print "Event insert error",e

@app.task(base=DatabaseTask, name='age_since_last_stored_state')
def age_since_last_stored_state(host, service, state):
    """ Calculates the age since when service
    was in the given state
    """

    prefix = 'util:'
    key = prefix + host + ':' + service
    # memc connection to get the state
    #memc = memcache.Client(['10.133.19.165:11211'])
    memc = age_since_last_stored_state.memc_cnx
    out = memc.get(str(key))
    set_key = True
    add_to_events = True
    now = datetime.now().strftime('%s')
    age = now
    value = state + ',' + age

    if out:
        out = out.split(',')
        old_state = out[0]
        time_since = out[1]
        # dont update the existing state if not changed
        if old_state == state:
	    add_to_events = False
            set_key = False
            age = time_since
    if set_key:
        memc.set(str(key), value)

    return int(age),add_to_events
@app.task(name='extract_wimax_bs_ss_params_fields_value',ignore_result=True)
def extract_wimax_bs_ss_params_fields_value(**args):
        wimax_services = ['wimax_ss_ul_utilization' , 'wimax_ss_dl_utilization' , 'wimax_qos_invent' , 'wimax_ss_session_uptime' ]
        wimax_utilization_service = ['wimax_ss_ul_utilization','wimax_ss_dl_utilization']
        wimax_qos_service = ['wimax_qos_invent']
        service_name = args['service']
        host_info = args['host_info']
        memc = args['memc']
        state_string = 'unknown'
        this_time = datetime.now()
        service_list = []
        event_list = []

        event_columns = ['sys_timestamp','device_name','severity','description','min_value', 'max_value', 'avg_value','current_value',\
                        'data_source','warning_threshold','critical_threshold','check_timestamp','ip_address','service_name',\
                        'site_name','machine_name']
        t_stmp = this_time + timedelta(minutes=-(this_time.minute % 5))
        t_stmp = t_stmp.replace(second=0,microsecond=0)
        current_time =int(time.mktime(t_stmp.timetuple()))
        prefix = service_name.split('_',2)[-1]
        for entry in host_info:
            value = ''
            state = 3
            state_string = 'unknown'
            perf = None
            try:
                host_name,site,ip = eval(entry[0])
                key = "%s_mac" % host_name
                mac = memc.get(str(key))
                #error('Wimax mac: {0}'.format(mac))
                key1 = str(mac) + '_params'
                value_list = memc.get(key1)
                #error('Wimax output: {0} {1}'.format(value_list,ip))
                #state = 0
                #state_string = 'ok'
                #value = 0
                if service_name in wimax_utilization_service :
                    value = value_list[wimax_utilization_service.index(service_name)]
                    value = float(value)/1024.0
                    value = round(value,2)
                    perf = '%s' %(prefix) + "=%s" % str(value)
		    state_string = 'ok'
		    state = 0

                elif service_name in wimax_qos_service :
                    value = value_list[2:4]
                    dl_qos = float(value[0])/(1000.0*1000)
                    prefix1 = 'dl_qos'
                    ul_qos = float(value[1])/(1000.0*1000)
                    prefix2 = 'ul_qos'
                    perf = '%s' %(prefix1) + "=%s " % str(dl_qos) + '%s' %(prefix2) + "=%s" % str(ul_qos)
		    state_string = 'ok'
		    state = 0
                else :
                    value = value_list[wimax_services.index(service_name) + 1]
                    perf = '%s' %(prefix) + "=%s" % str(value)
                    state_string = 'ok'
		    state = 0

            except Exception,e:

                #error('Error in wimax bs ss param services: {0}, {1} {2}'.format(e,ip,service_name))

		if service_name in wimax_qos_service:
		    perf = 'dl_qos= ul_qos='
		else :
                    perf ='%s=' %(prefix)
                #pass

            age_of_state,create_event = age_since_last_stored_state(host_name, service_name, state_string)
            service_dict = make_service_dict(
                            perf, state_string, host_name, site, ip, age_of_state, **args)

            service_list.append(service_dict)

        if len(service_list) > 0:
            build_export.s(args['site_name'], service_list).apply_async()

@app.task(name='extract_wimax_ss_port_params_value',ignore_result=True)
def extract_wimax_ss_port_params_value(**args):
        wimax_services = ["wimax_ss_speed_status" ,"wimax_ss_autonegotiation_status" ,"wimax_ss_duplex_status" ,\
                                                "wimax_ss_uptime" ,"wimax_dl_modulation_change_invent" ,"wimax_ss_link_status"]

        comparison_services = ['wimax_dl_modulation_change_invent']

        prefix_dict = {'wimax_ss_speed_status'  : 'ss_speed' ,
                       'wimax_ss_autonegotiation_status' : 'autonegotiation' ,
                       'wimax_ss_duplex_status' : 'duplex' ,
                       'wimax_ss_uptime' : 'uptime' ,
                       'wimax_dl_modulation_change_invent' : 'dl_modulation_change' ,
                       'wimax_ss_link_status' : 'link_state'
                      }

        service_name = args['service']
        host_info = args['host_info']
        memc = args['memc']
        state_string = 'unknown'
        this_time = datetime.now()
        service_list = []
        event_list = []
        event_columns = ['sys_timestamp','device_name','severity','description','min_value', 'max_value', 'avg_value','current_value',\
                        'data_source','warning_threshold','critical_threshold','check_timestamp','ip_address','service_name',\
                        'site_name','machine_name']
        t_stmp = this_time + timedelta(minutes=-(this_time.minute % 5))
        t_stmp = t_stmp.replace(second=0,microsecond=0)
        current_time =int(time.mktime(t_stmp.timetuple()))
        prefix = prefix_dict[service_name]
        for entry in host_info:
            value = ''
            state = 3
            state_string = 'unknown'
            try:
                host_name,site,ip = eval(entry[0])
                key = "%s_ss_port_params" %  str(host_name)
                #error('Wimax mac: {0}'.format(mac))
                value_list = memc.get(key)
                #error('Wimax ss_port_params output: {0} {1}'.format(value_list,ip))
                value = str(value_list[wimax_services.index(service_name)])

                if service_name in comparison_services :
                        value = int(value)
                        if value > int(args['crit']):
                                state  = 2
                                state_string = 'critical'
                        elif  value >= int(args['war']):
                                state = 1
                                state_string = 'warning'
                        else:
                                state = 0
                                state_string = 'ok'

                elif service_name in wimax_services :
                        value = value.replace(" ","_")
                        state = 0
                        state_string = 'ok'

                #else:
                #        state = 3
                #        state_string = 'unknown'

                #error('perf: {0} {1}'.format(args['war'],args['crit']))
                if args['war'] is not None :
                    perf = '%s' %(prefix) + "=%s;%s;%s" % (value,args['war'],args['crit'])
                else :
                     perf = '%s' %(prefix) + "=%s" %(value)
            except Exception ,e:
                #error('Error in wimax services: {0}, {1} {2}'.format(e,ip,service_name))
                perf = '%s=' %(prefix)
            age_of_state,add_to_events = age_since_last_stored_state(host_name, service_name, state_string)
            service_dict = make_service_dict(
                perf, state_string, host_name, site, ip, age_of_state, **args)
            service_list.append(service_dict)
        #error('len wimax services: {0}'.format(service_list))
        if len(service_list) > 0:
            build_export.s(args['site_name'], service_list).apply_async()

@app.task(name='get_passive_checks_output',ignore_result=True)
def get_passive_checks_output(**opt):
    INVENTORY_DB = 3
    service_threshold = {}
    ss_port_service_threshold = {}
    opts = {'site_name': opt.get('site_name')}
    try :
        ends_with = opt.get('ends_with')
    except :
        ends_with = None

    topology_related_services = ['wimax_dl_cinr','wimax_dl_rssi','wimax_ul_cinr','wimax_ul_rssi','wimax_dl_intrf','wimax_ul_intrf','wimax_modulation_dl_fec','wimax_modulation_ul_fec']
    bs_ss_params_related_services = ['wimax_ss_ul_utilization' , 'wimax_ss_dl_utilization' , 'wimax_ss_session_uptime' ] #'wimax_qos_invent'

    ss_port_params_services = ["wimax_ss_speed_status" ,"wimax_ss_autonegotiation_status" ,"wimax_ss_duplex_status","wimax_ss_uptime" ,"wimax_ss_link_status"]  #"wimax_dl_modulation_change_invent"

    if ends_with is None :
        topology_related_services = filter(lambda x:x.split('_')[-1] not in ['invent','status'],topology_related_services)
        bs_ss_params_related_services = filter(lambda x:x.split('_')[-1] not in ['invent','status'],bs_ss_params_related_services)
        ss_port_params_services = filter(lambda x:x.split('_')[-1] not in ['invent','status'],ss_port_params_services)

    else :
        topology_related_services = filter(lambda x:x.split('_')[-1] in ends_with,topology_related_services)
        bs_ss_params_related_services = filter(lambda x:x.split('_')[-1] in ends_with,bs_ss_params_related_services)
        ss_port_params_services = filter(lambda x:x.split('_')[-1] in ends_with,ss_port_params_services)

    rds_cli_invent = RedisInterface(custom_conf={'db': INVENTORY_DB})
    redis_cnx = rds_cli_invent.redis_cnx

    # changing site name to machine name as ON UAT enviornment to support shinken we used the machine name in place of site .In prod
    # we need to change it as site_name
    machine= opts['site_name'].split('_')[0]
    wimax_ss_key = redis_cnx.keys(pattern="wimax:ss:%s:*" % opts['site_name'])
    #error('wimax ss key: {0}'.format(wimax_ss_key))
    for service_name in topology_related_services:
        war_key  = service_name + ':war'
        crit_key  = service_name + ':crit'
        service_threshold[war_key]  =  redis_cnx.get(war_key)
        service_threshold[crit_key]  =  redis_cnx.get(crit_key)
    #error('thresholds: {0}'.format(service_threshold))

    for service_name in ss_port_params_services:
        war_key  = service_name + ':war'
        crit_key  = service_name + ':crit'
        try :
            ss_port_service_threshold[war_key]  =  redis_cnx.get(war_key)
        except Exception,e :
            ss_port_service_threshold[war_key]  = None
        try :
            ss_port_service_threshold[crit_key]  =  redis_cnx.get(crit_key)
        except Exception,e :
            ss_port_service_threshold[crit_key]  = None
    #error('ss_port thresholds: {0}'.format(ss_port_service_threshold))

    extract_values_from_main_function(
            wimax_ss_key,
            topology_related_services,
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_wimax_topology_fields_value'
            )
    extract_values_from_main_function(
            wimax_ss_key,
            bs_ss_params_related_services,
            {},
            site_name=opt.get('site_name'),
            func='extract_wimax_bs_ss_params_fields_value'
            )
    extract_values_from_main_function(
            wimax_ss_key,
            ss_port_params_services,
            ss_port_service_threshold,
            site_name=opt.get('site_name'),
            func='extract_wimax_ss_port_params_value'
            )

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
	if kw.get('serv_data'):
		serv_data = kw.get('serv_data')
		#error('site__ name: {0}'.format(site))
		mysql_site = site.split('_')[0]
		#warning(serv_data[:2])
		# mongo/mysql inserts/updates for regular services
		tasks.extend([
			mysql_insert_handler.s(serv_data, 'performance_performanceservice',
			                       'performance_servicestatus', 'service_perf', mysql_site)])

	if kw.get('interface_serv_data'):
		interface_serv_data = kw.get('interface_serv_data')
		# mongo/mysql inserts/updates for regular services
		mysql_site = site.split('_')[0]
		tasks.extend([
			mysql_insert_handler.s(interface_serv_data, 'performance_performancestatus',
			                       'performance_status', 'interface_perf', mysql_site)])

	if kw.get('invent_serv_data'):
		invent_serv_data = kw.get('invent_serv_data')
		# mongo/mysql inserts/updates for regular services
		mysql_site = site.split('_')[0]
		tasks.extend([
			mysql_insert_handler.s(invent_serv_data, 'performance_performanceinventory',
			                       'performance_inventorystatus', 'inventory_perf', mysql_site)])


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
