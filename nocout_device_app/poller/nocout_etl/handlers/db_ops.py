"""
db_ops.py
==========

Maintains per process database connections and handles 
data manipulations, used in site-wide ETL operations.
[for celery]
"""


from ast import literal_eval
from ConfigParser import ConfigParser
from datetime import datetime
from itertools import groupby, izip_longest
import memcache
from mysql.connector import connect
from mysql.connector.errors import (OperationalError, InterfaceError)
from operator import itemgetter
from pymongo import MongoClient
from redis import StrictRedis
from redis.sentinel import Sentinel
from time import sleep

from celery import Task
from celery.contrib.methods import task_method
from celery.utils.log import get_task_logger

#from start_pub import app
from start.start import app
logger = get_task_logger(__name__)
info , warning, error = logger.info, logger.warning, logger.error

DB_CONF = getattr(app.conf, 'CNX_FROM_CONF', None)
INVENTORY_DB = getattr(app.conf, 'INVENTORY_DB', 3)
SENTINELS = getattr(app.conf, 'SENTINELS', None)
MEMCACHE_CONFIG = getattr(app.conf,'MEMCACHE_CONFIG',None)


class DatabaseTask(Task):
	abstract = True
	# maintains database connections based on sites
	# mysql connections
	my_conn_pool = {}
	# mongo connections
	mo_conn_pool = {}
	# redis connection object
	memc_conn = None
	# memc connection object
	redis_conn = None

	conf = ConfigParser()
	conf.read(DB_CONF)

	def after_return(self, *args, **kwargs):
		if self.name == 'mongo-export-mysql-handler':
			# get values to be deleted from mongo and site name
			site, delete_values = args[3]
			for col_name, col_count in delete_values.iteritems():
				purge_mongo_data(col_name, col_count, site)
		super(DatabaseTask, self).after_return(*args, **kwargs)

	def mongo_cnx(self, key):
		# mongo connection config
		mo_conf = {
				'host': self.conf.get(key, 'mongo_host'),
				'port': int(self.conf.get(key, 'mongo_port')),
				}
		if not self.mo_conn_pool.get(key):
			try:
				self.mo_conn_pool[key] = MongoClient(**mo_conf)[self.conf.get(key, 
					'mongo_database')]
			except Exception as exc:
				error('Mongo connection error... {0}'.format(exc))
				#raise self.retry(max_retries=2, countdown=10, exc=exc)

		return self.mo_conn_pool.get(key)

	def mysql_cnx(self, key):
		# mysql connection config
		my_conf = {
				'host': self.conf.get(key, 'host'),
				'port': int(self.conf.get(key, 'port')),
				'user': self.conf.get(key, 'user'),
				'password': self.conf.get(key, 'password'),
				'database': self.conf.get(key, 'database'),
				}
		try_connect = False
		if not (self.my_conn_pool.get(key) and self.my_conn_pool.get(key).is_connected()):
			try_connect = True
		if try_connect:
			try:
				self.my_conn_pool[key] = connect(**my_conf)
			except Exception as exc:
				error('Mysql connection problem, retrying... {0}'.format(exc))
				#raise self.retry(max_retries=2, countdown=10, exc=exc)

		return self.my_conn_pool.get(key)
	@property
	def memc_cnx(self):
		if not self.memc_conn:
			try:
				#memc_conf = []
				self.memc_conn = memcache.Client(
						MEMCACHE_CONFIG, debug=1
						)
			except Exception as e:
				error('Memc connection problem, retrying... {0}'.format(e))

		return self.memc_conn


class RedisInterface(object):
	""" Implements various redis operations"""

	#__slots__ = ['custom_conf', 'redis_conn', 'perf_q']


	def __init__(self, **kw):
		self.custom_conf = kw.get('custom_conf')
		self.redis_conn = None
		# queue name to get check results data from 
		self.perf_q = kw.get('perf_q')

	def conn_from_conf(self, custom_conf=None):
		""" Method used to get redis connection without binding 
		with any queue"""
		self.custom_conf = custom_conf
		return self.redis_cnx

	@property
	def redis_cnx(self):
		conf = ConfigParser()
		conf.read(DB_CONF)
		# redis connection config
		re_conf = {
			'port': int(conf.get('redis', 'port')),
			'db': int(conf.get('redis', 'db'))
		}
		re_conf.update(self.custom_conf) if self.custom_conf else re_conf
		service_name = conf.get('redis', 'service_name', 'mymaster')
		try:
			#self.redis_conn = StrictRedis(**re_conf)
			sentinel = Sentinel(SENTINELS, **re_conf)
			self.redis_conn = sentinel.master_for(service_name) 
		except Exception as exc:
			error('Redis connection error... {0}'.format(exc))

		return self.redis_conn

	def get(self, start, end):
		""" Get and remove values from redis list based on a range"""
		p = self.redis_cnx.pipeline(transaction=True)

		p.lrange(self.perf_q, start, end)
		# keep only unread values in list
		if end == -1:
			start, end = -1, 0
		else:
			start,  end = end+1, -1

		output = p.execute()
		if output and output[0]:
		    p.ltrim(self.perf_q, start, end)
		    p.execute()
		    output = output[0]
		    output = [literal_eval(x) for x in output]

		return output

	@app.task(filter=task_method, name='redis-update')
	def redis_update(self, data_values, update_queue=False, perf_type=''):
		""" Updates multiple hashes in single operation using pipelining"""
		KEY = '%s:%s:%s:%s' % (perf_type, '%s', '%s', '%s')
		p = self.redis_cnx.pipeline(transaction=True)
		try:
			# update the queue values
			if update_queue:
				KEY = '%s:%s:%s' % (perf_type, '%s', '%s')
				devices = [(d.get('device_name'), d.get('service_name'))for d in data_values]
				# push the values into queues
				[p.rpush(KEY % (d.get('device_name'), d.get('service_name')), d.get('severity'))
				 for d in data_values]
				# perform all operations atomically
				p.execute()
				# calc queue length corresponds to every host entry
				[p.llen(KEY % (x[0], x[1])) for x in devices]
				queues_len = p.execute()
				#host_queuelen_map = zip(devices, queues_len)
				# keep only 2 latest values for each host entry, if any
				#trim_hosts = filter(lambda x: x[1] > 2, host_queuelen_map)
				trim_hosts = []
				for _, x in enumerate(zip(devices, queues_len)):
					if x[1] > 2:
						trim_hosts.append(x[0])
				[p.ltrim(KEY % (x[0], x[1]), -2, -1) for x in trim_hosts]
			# update the hash values
			else:
				[p.hmset(KEY %
					(d.get('device_name'), d.get('service_name'), d.get('data_source')),
					d) for d in data_values]
				# perform all operations atomically
			p.execute()
		except Exception as exc:
			error('Redis pipe error in update... {0}, retrying...'.format(exc))
			# send the task for retry
			#Task.retry(args=(data_values), kwargs={'perf_type': perf_type},
			#		max_retries=2, countdown=10, exc=exc)

	def multi_get(self, key_prefix):
		""" Returns list of values (mappings) having keys matching with key_prefix"""
		out = []
		if not key_prefix:
			return out
		pattern = key_prefix + '*'
		keys = self.redis_cnx.keys(pattern=pattern)
		p = self.redis_cnx.pipeline()
		try:
			[p.hgetall(k) for k in keys]
			out = p.execute()
		except Exception as exc:
			error('Redis pipe error in multi get... {0}'.format(exc))

		return out

	@app.task(filter=task_method, name='redis-insert')
	def multi_set(self, data_values, perf_type=''):
		""" Sets multiple key values through pipeline"""
		KEY = '%s:%s:%s' % (perf_type, '%s', '%s')
		p = self.redis_cnx.pipeline(transaction=True)
		# keep the provis data keys with a timeout of 5 mins
		[p.setex(KEY %
		         (d.get('device_name'), d.get('service_name')),
		         300, d.get('current_value')) for d in data_values
		]
		try:
		    p.execute()
		except Exception as exc:
		    error('Redis pipe error in multi_set: {0}'.format(exc))

@app.task(base=DatabaseTask, name='threshold-kpi-services', bind=True)
def store_threshold_for_kpi_services(self):
        topology_services = ('wimax_dl_rssi','wimax_ul_rssi','wimax_dl_cinr','wimax_ul_cinr','wimax_dl_intrf','wimax_ul_intrf',
	'wimax_modulation_dl_fec','wimax_modulation_ul_fec')
	memc = store_threshold_for_kpi_services.memc_cnx
	query = (
	"select devicetype.name as devicetype, "
	"service.name as service, "
	"datasource.name as datasource, "
	"devicetype_svc_ds.warning as dtype_ds_warning, "
	"devicetype_svc_ds.critical as dtype_ds_critical, "
	"svcds.warning as service_warning, "
	"svcds.critical as service_critical, "
	"datasource.warning as warning, "
	"datasource.critical as critical "
	"from device_devicetype as devicetype "
	"left join ( "
	"service_service as service, "
	"device_devicetypeservice as devicetype_svc, "
	"service_servicespecificdatasource as svcds, "
	"service_servicedatasource as datasource "
	") "
	"on ( "
	"svcds.service_id = service.id "
	"and "
	"svcds.service_data_sources_id = datasource.id "
	"and "
	"devicetype_svc.service_id = service.id "
	"and "
	"devicetype.id = devicetype_svc.device_type_id "
	") "
	"left join "
	"device_devicetypeservicedatasource as devicetype_svc_ds "
	"on "
	"( "
	"devicetype_svc_ds.device_type_service_id = devicetype_svc.id "
	"and "
	"devicetype_svc_ds.service_data_sources_id = datasource.id "
	")"
	"where devicetype.name <> 'Default' and service.name like '%_kpi' or service.name in " + str(topology_services) +";"
	)
	#info('sample {0}'.format('Testing'))
	cur = store_threshold_for_kpi_services.mysql_cnx('historical').cursor()
	cur.execute(query)
	out = cur.fetchall()
	#info('out: {0}'.format(out))
	rds_cli = RedisInterface(custom_conf={'db': INVENTORY_DB})
	rds_cnx = rds_cli.redis_cnx
	processed_service = []
	try:
		for entry in out:
			key = str(entry[1])
			if key not in processed_service:
				war_key = key + ":" + "war"
				crit_key = key + ":" + "crit"
				if entry[3] or entry[4]: 
					rds_cnx.set(war_key,entry[3])	
					rds_cnx.set(crit_key,entry[4])	
				elif entry[5] or entry[6]: 
					rds_cnx.set(war_key,entry[5])	
					rds_cnx.set(crit_key,entry[6])	
				elif entry[7] or entry[8]: 
					rds_cnx.set(war_key,entry[7])	
					rds_cnx.set(crit_key,entry[8])
				processed_service.append(key)
	except:
		error('KPI threshold values loading into redis failed')
	
	else:
		info('KPI threshold values loading into redis success')

		
@app.task(base=DatabaseTask, name='load-inventory', bind=True)
def load_inventory(self):
	"""
	Loads appropriate inventory data into redis and memcache
	"""
	query = (
		"SELECT DISTINCT D.device_name, site_instance_siteinstance.name, "
		"D.ip_address, device_devicetype.name AS dev_type, "
		"device_devicetechnology.name AS dev_tech ,"
		"inventory_circuit.qos_bandwidth as qos_bw "
		"FROM device_device D "
		"INNER JOIN "
		"(device_devicetype, device_devicetechnology, machine_machine, "
		"site_instance_siteinstance) "
		"ON "
		"( "
		"device_devicetype.id = D.device_type AND "
		"device_devicetechnology.id = D.device_technology AND "
		"machine_machine.id = D.machine_id AND "
		"site_instance_siteinstance.id = D.site_instance_id "
		") "
		"LEFT JOIN "
		"(inventory_substation,inventory_circuit) "
		"ON "
		"( "
		"inventory_substation.device_id = D.id  and "
		"inventory_circuit.sub_station_id = inventory_substation.id "
		") "
		"WHERE "
		"D.is_deleted = 0 AND "
		"D.host_state <> 'Disable' AND "
		"device_devicetechnology.name IN ('WiMAX', 'P2P', 'PMP') "
		"and device_devicetype.name in " 
		"('Radwin2KBS', 'CanopyPM100AP', 'CanopySM100AP', 'StarmaxIDU', 'Radwin5KBS','Radwin2KSS', 'CanopyPM100SS', " 
		"'CanopySM100SS', 'StarmaxSS','Radwin5KSS')"
	)
	dr_query = (
		"SELECT "
		"inner_device.Sector_name AS primary_dn, "
		"outer_device.device_name AS dr_dn "
		"FROM ( "
			"SELECT "
				"ds.device_name AS Sector_name, "
				"sector.dr_configured_on_id as dr_id "
		"FROM "
			"inventory_sector AS sector "
		"INNER JOIN "
			"device_device AS ds "
		"ON "
			"NOT ISNULL(sector.sector_configured_on_id) "
		"AND "
			"sector.sector_configured_on_id = ds.id "
		"AND "
			"sector.dr_site = 'yes' "
		"AND "
			"NOT ISNULL(sector.dr_configured_on_id) "
		") AS inner_device "
		"INNER JOIN "
			"device_device as outer_device "
		"ON "
			"outer_device.id = inner_device.dr_id; "
	)

	cur = load_inventory.mysql_cnx('historical').cursor()
	cur.execute(query)
	out = cur.fetchall()
	backhaul_query  = ( 
	"select device_device.device_name, "
    	"site_instance_siteinstance.name, "
	"device_device.ip_address, "
    	"device_devicetype.name, "
    	"device_devicetechnology.name as techno_name, "
    	"group_concat(service_servicedatasource.name separator '$$') as port_name, " 
    	"group_concat(inventory_basestation.bh_port_name separator '$$') as port_alias, "
    	"group_concat(inventory_basestation.bh_capacity separator '$$') as port_wise_capacity "
    	"from device_device "
    	"inner join "
    	"(device_devicetechnology, device_devicetype, "
   	"machine_machine, site_instance_siteinstance) "
    	"on "
    	"( "
    	"device_devicetype.id = device_device.device_type and "
    	"device_devicetechnology.id = device_device.device_technology and "
    	"machine_machine.id = device_device.machine_id and "
    	"site_instance_siteinstance.id = device_device.site_instance_id "
    	") "
    	"inner join "
    	"(inventory_backhaul) "
    	"on "
    	"(device_device.id = inventory_backhaul.bh_configured_on_id OR device_device.id = inventory_backhaul.aggregator_id OR "
     	"device_device.id = inventory_backhaul.pop_id OR "
     	"device_device.id = inventory_backhaul.bh_switch_id) "
    	"left join "
    	"(inventory_basestation) "
    	"on "
    	"(inventory_backhaul.id = inventory_basestation.backhaul_id) "
    	"left join "
    	"(service_servicedatasource) "
    	"on "
    	"(inventory_basestation.bh_port_name = service_servicedatasource.alias) "
    	"where "
    	"device_device.is_deleted=0 and "
    	"device_device.host_state <> 'Disable' "
    	"and "
    	"device_devicetype.name in ('RiCi', 'PINE') "
    	"group by device_device.ip_address;" )


	switch_query = """
	select
		bh_device.device_name,
		site_instance_siteinstance.name,
		bh_device.ip_address,
		dtype.name as device_type,
		GROUP_CONCAT(bs.bh_port_name separator ',') as bh_ports,
		GROUP_CONCAT(sds.name separator ',') as service_alias,
		group_concat(bs.bh_capacity separator ',') as port_wise_capacity 
	from
		inventory_basestation as bs
	left join
		inventory_backhaul as bh
	on
		bs.backhaul_id = bh.id
	left join
		device_device as bh_device
	ON
		bh_device.id = bh.bh_configured_on_id
	left join
		device_devicetype as dtype
	ON
		dtype.id = bh_device.device_type
	left join
		service_servicedatasource as sds
	ON
		lower(sds.name) = lower(bs.bh_port_name)
		OR
		lower(sds.alias) = lower(bs.bh_port_name)
		OR
		lower(sds.name) = lower(replace(bs.bh_port_name, '/', '_'))
		OR
		lower(sds.alias) = lower(replace(bs.bh_port_name, '/', '_'))
	left join 
	(machine_machine,site_instance_siteinstance)
	on
	(
	 machine_machine.id = bh_device.machine_id and site_instance_siteinstance.id = bh_device.site_instance_id
	)
	WHERE
		lower(dtype.name) in ('juniper', 'cisco','huawei')
	group by
		bh_device.id;
	"""

	ping_threshold_query = ("select name,rta_warning,rta_critical,pl_warning,pl_critical from device_devicetype; ")

	cur.execute(backhaul_query)
	backhaul_out = cur.fetchall()
	cur.execute(switch_query)
	switch_output = cur.fetchall()
	
	ping_threshold_dict = {}
	# Calculate warning and critical for device type to be used in Event 
	cur.execute(ping_threshold_query)
	ping_threshold_out = cur.fetchall()
	for d1 in ping_threshold_out:
		ping_threshold_dict[d1[0]] = []
		ping_threshold_dict[d1[0]].extend([d1[1],d1[2],d1[3],d1[4]])

	#warning('out: {0},{1}'.format(ping_threshold_dict,ping_threshold_out))
	
	# e.g. keeping invent data in database number 3
	rds_cli = RedisInterface(custom_conf={'db': INVENTORY_DB})
	rds_cli.redis_cnx.flushdb()
	rds_pipe = rds_cli.redis_cnx.pipeline(transaction=True)

	# memc client
	#memc = memcache.Client(['10.133.19.165:11211'])
        memc =  load_inventory.memc_cnx
	wimax_bs_list = []

	# device_name --> ip mapping (in memc)
	device_name_ip_map = {}

	# keeping extra iteration for name and ip map
	for d in out:
		device_name_ip_map[d[0]] = d[2]
	for d in backhaul_out:
		device_name_ip_map[d[0]] = d[2]

	# group based on device technologies and load the devices info to redis
	out = sorted(out, key=itemgetter(3))
	backhaul_out = sorted(backhaul_out, key=itemgetter(3))
	switch_out = sorted(switch_output, key=itemgetter(2))

	for grp, grp_vals in groupby(out, key=itemgetter(3)):
		grouped_devices = list(grp_vals)
        	#error('Data ... {0}'.format(grouped_devices))
		if grouped_devices[0][3] == 'StarmaxIDU':
			[wimax_bs_list.append(list(x)) for x in grouped_devices]
			# push wimax bs with its dr site info
			cur.execute(dr_query)
			dr_info = cur.fetchall()
			cur.close()
			#warning('wimax bs: {0}'.format(wimax_bs_list))
			store_ping_threshold(wimax_bs_list,rds_pipe,ping_threshold_dict)
			load_devicetechno_wise(wimax_bs_list, rds_pipe,extra=dr_info)
		else:
			store_ping_threshold(grouped_devices,rds_pipe,ping_threshold_dict)
			load_devicetechno_wise(grouped_devices,rds_pipe)
	for bk_grp, bk_grp_vals in groupby(backhaul_out, key=itemgetter(3)):
		bk_grouped_devices = list(bk_grp_vals)
		load_backhaul_data(bk_grouped_devices, rds_pipe)
	for switch_grp, switch_grp_vals in groupby(switch_out, key=itemgetter(2)):
		switch_grouped_devices = list(switch_grp_vals)
		load_switch_data(switch_grouped_devices, rds_pipe)

	try:
		rds_pipe.execute()
		store_threshold_for_kpi_services()
	except Exception as exc:
		error('Error in redis inventory loading... {0}'.format(exc))
	else:
		warning('Inventory loading into redis, done.')
	
	try:
		memc.set_multi(device_name_ip_map)
	except Exception as exc:
		error('Error in memc inventory loading... {0}'.format(exc))
	else:
		warning('Inventory loading into memc, done.')
	

@app.task(name='store-ping-threshold')
def store_ping_threshold(data_values,p,ping_threshold_dict):
        #error('Data ... {0}'.format(data_values))
	host_key = '%s:ping' 	
	t1 = data_values[0]
	threshold_value = ping_threshold_dict.get(t1[3])
	for data in data_values:
		#p.delete(host_key % data[0])
		p.rpush(host_key % data[0],threshold_value)


@app.task(name='load-switch-data')
def load_switch_data(data_values, p, extra=None):
	t = data_values[0]
	processed = []
	#info('PORT-Data: {0}'.format(data_values))
	# key:: <device-tech>:<device-type>:<site-name>:<ip>
	key = '%s:%s:%s:%s' % (str(t[3]).lower(),
					'ss' if t[3].endswith('SS') else 'bs',
					'%s',
					'%s')
	invent_key = 'device_inventory:%s'
        cisco_juniper = ['cisco','juniper']
	for device in data_values:
		device_attr = []
		if str(device[3].lower()) == 'cisco':
			port_wise_capacities = [0]*26
		elif str(device[3].lower()) == 'juniper':
			port_wise_capacities = [0]*52
		elif str(device[3].lower()) == 'huawei':
                        port_wise_capacities = [0]*28



		if  str(device[0]) in processed:
		    continue
		if str(device[3].lower()) == 'cisco':
		    try :
			int_ports = map(lambda x: x.split('/')[-1], device[4].split(','))
			int_ports = map(lambda x: int(x), int_ports)   #convert int type
			int_string = map(lambda x: x.split('/')[0], device[4].split(','))
			for i in xrange(len(int_string)):
			    #if int_string[i]== 'Gi0':
			    if 'gi' in int_string[i].lower():
				int_ports[i]= int_ports[i]+24
			capacities = device[6].split(',') if device[6] else device[6]
			if len(int_string)>1:  # to multiple kpi for ring ports
                            capacities.append(capacities[0])
			for p_n, p_cap in zip(int_ports, capacities):
			    port_wise_capacities[int(p_n)-1] = p_cap

		    except Exception as e:
			port_wise_capacities = [0]*8
		if str(device[3].lower()) == 'juniper':
		   try:
		       int_ports = map(lambda x: x.split('/')[-1], device[4].split(','))
		       int_ports = map(lambda x: int(x), int_ports)   #convert int type
		       int_ports_s = map(lambda x: x.split('/')[-2], device[4].split(','))
		       int_ports_s = map(lambda x: int(x), int_ports_s)
		       for i in xrange(len(int_ports_s)):
			   if int_ports_s[i]== 1:
			       int_ports[i]=int_ports[i]+48
		       capacities = device[6].split(',') if device[6] else device[6]
                       if len(int_ports)>1: # for ring port extra capcity added
                           capacities.append(capacities[0])
                       for p_n, p_cap in zip(int_ports, capacities):
                           port_wise_capacities[int(p_n)] = p_cap
		   except Exception as e:
			port_wise_capacities = [0]*8

		if str(device[3].lower()) == 'huawei':
                        try:
                           capacities = device[6].split(',') if device[6] else device[6]
                           for i in xrange(len(capacities)):
                               port_wise_capacities[i]=capacities[i]
                        except Exception as e:
                            port_wise_capacities = [0]*8


		p.set(invent_key % device[0], device[2])
		device_attr.extend([device[0],device[1],device[2]])
		device_attr.append(port_wise_capacities)
		#info('Output-Data: {0}'.format(device_attr))
		p.rpush(key % (device[1], device[2]), device_attr)
		processed.append(str(device[0]))



@app.task(name='load-backhaul-data')
def load_backhaul_data(data_values, p, extra=None):
	t = data_values[0]
	processed = []
	#error('PORT-Data: {0}'.format(data_values))
	# key:: <device-tech>:<device-type>:<site-name>:<ip>
	key = '%s:%s:%s:%s' % (str(t[3]).lower(),
					'ss' if t[3].endswith('SS') else 'bs',
					'%s',
					'%s')
	invent_key = 'device_inventory:%s'
	for device in data_values:
		device_attr = []
		port_wise_capacities = [0]*9
		if  str(device[0]) in processed:
		    continue
		if '_' in str(device[5]):
		    try:
			int_ports = map(lambda x: x.split('_')[-1], device[5].split('$$'))
			capacities = device[7].split('$$') if device[7] else device[7]
			#info('PORT-Data: {0}'.format(capacities))
			for p_n, p_cap in zip(int_ports, capacities):
			    #port_wise_capacities[int(p_n)-1] = p_cap
			    port_wise_capacities[int(p_n)-1] = p_cap
		    except (IndexError, TypeError, AttributeError) as err:
			error('ERR-Data: normal {0}'.format(err))
			port_wise_capacities = [0]*8
		p.set(invent_key % device[0], device[2])
		device_attr.extend([device[0],device[1],device[2]])
		device_attr.append(port_wise_capacities)
		#info('Output-Data: {0}'.format(device_attr))
		p.rpush(key % (device[1], device[2]), device_attr)
		processed.append(str(device[0]))

@app.task(name='load-devicetechno-wise')
def load_devicetechno_wise(data_values, p, extra=None):
	"""
	Loads specific device technology data into redis
	"""
	t = data_values[0]

	# key for storing rta/pl warning/critial values

	# key:: <device-tech>:<device-type>:<site-name>:<ip>
	key = '%s:%s:%s:%s' % (str(t[4]).lower(),
					'ss' if t[3].endswith('SS') else 'bs',
					'%s',
					'%s')
	# keeping basic inventory info of a device, name --> ip mapping
	invent_key = 'device_inventory:%s'
	# entries needed from index 0 to last_index-1
	if t[3] == 'Radwin2KSS':
		last_index = 6
	else:
		last_index = 3
	matched_dr = None
	# TODO: need to improve the algo here
	if extra:
		# update the `dr_hosts` hash in redis
		dr_mapping = dict([t for t in extra])
		p.hmset('dr_hosts', dr_mapping)
		last_index = 4
		for outer in data_values:
			del outer[3:]
			for inner in extra:
				if inner[0] == outer[0]:
					matched_dr = inner[1]
				elif inner[1] == outer[0]:
					matched_dr = inner[0]
					break
			if matched_dr:
				outer.append(matched_dr)
				matched_dr = None
	#[p.rpush(key % data[2], data[:last_index]) for data in data_values]
	for data in data_values:
		
		try:
			if data[3].startswith('Radwin5K'):
				key = key.replace("pmp","rad5k")
		except Exception as e :
			error('key: normal {0}'.format(e))
				
		p.set(invent_key % data[0], data[2])
		p.rpush(key % (data[1], data[2]), data[:last_index])

@app.task(base=DatabaseTask, name='nw-mongo-update', bind=True)
def mongo_update(self, data_values, indexes, col, site):
	lcl_cnx = mongo_update.mongo_cnx(site)[col]
	if data_values and lcl_cnx:
		try:
			for val in data_values:
				find_query = {}
				[find_query.update({x: val.get(x)}) for x in indexes]
				lcl_cnx.update(find_query, val, upsert=True)
		except Exception as exc:
			error('Mongo update problem, retrying... {0}'.format(exc))
			raise self.retry(args=(data_values, indexes, col), max_retries=1,
					countdown=10, exc=exc)
	else:
		# TODO :: mark the task as failed
		error('Mongo update failed...')


@app.task(base=DatabaseTask, name='nw-mongo-insert', bind=True)
def mongo_insert(self, data_values, col, site):
	if data_values:
		try:
			mongo_insert.mongo_cnx(site)[col].insert(data_values)
		except Exception as exc:
			error('Mongo insert problem, retrying... {0}'.format(exc))
			raise self.retry(args=(data_values, col), max_retries=1,
					exc=exc)
	else:
		error('Mongo insert failed...')


@app.task(base=DatabaseTask, name='nw-mysql-handler', bind=True)
def mysql_insert_handler(self, data_values, insert_table, update_table, mongo_col,
                         site, columns=None, old_topology=None):
	""" mysql insert and also updates last entry into mongodb"""
	
	# TODO: Every task should sub class db_ops and initialize table names, 
	# instead of passing them as function args seperately
	if (data_values and 
			isinstance(data_values[0].get('sys_timestamp'), datetime)):
		for entry in data_values:
			entry['sys_timestamp'] = entry['sys_timestamp'].strftime('%s')
			entry['check_timestamp'] = entry['check_timestamp'].strftime('%s')

	# handle the data deletion for toplogy table
	if old_topology:
		local_cnx = mysql_insert_handler.mysql_cnx(site)
		delete_old_topology(local_cnx, old_topology)

	if insert_table:
		# executing the task asynchronously
		mysql_insert.s(insert_table, data_values, mongo_col, site, columns=columns
		               ).apply_async()

	if update_table:
		# execute asynchronously
		mysql_update.s(update_table, data_values, site, columns=columns
		               ).apply_async()


@app.task(base=DatabaseTask, name='nw-mysql-update', bind=True,
          default_retry_delay=20, max_retries=1)
def mysql_update(self, table, data_values, site, columns=None):
	""" mysql update"""
	
	default_columns = ('device_name', 'service_name', 'machine_name',
	                   'site_name', 'ip_address', 'data_source', 'severity',
	                   'current_value', 'min_value', 'max_value', 'avg_value',
	                   'warning_threshold', 'critical_threshold', 'sys_timestamp',
	                   'check_timestamp', 'age', 'refer')
	columns = columns if columns else default_columns
	p0 = "INSERT INTO %(table)s" % {'table': table}
	p1 = ' (%s)' % ','.join(columns)
	p2 = ' , '.join(map(lambda x: ' %('+ x + ')s', columns))
	p3 = ' , '.join(map(lambda x: x + ' = VALUES(' + x + ')', columns))
	updt_qry = p0 + p1 + ' VALUES (' + p2 + ') ON DUPLICATE KEY UPDATE ' + p3

	try:
		lcl_cnx = mysql_update.mysql_cnx(site)
		cur = lcl_cnx.cursor()
		cur.executemany(updt_qry, data_values)
		lcl_cnx.commit()
		cur.close()
		lcl_cnx.close()
	except Exception as exc:
		# rollback transaction
		lcl_cnx.rollback()
		# attempt task retry
		raise self.retry(exc=exc)

	#warning('Len for status upserts {0}\n'.format(len(data_values)))


@app.task(base=DatabaseTask, name='nw-mysql-insert', bind=True,
		default_retry_delay=40, max_retries=1)
def mysql_insert(self, table, data_values, mongo_col, site, columns=None):
	""" mysql batch insert"""

	#warning('Called with table: {0}'.format(table))
	default_columns = ('device_name', 'service_name', 'machine_name',
			'site_name', 'ip_address', 'data_source', 'severity',
			'current_value', 'min_value', 'max_value', 'avg_value',
			'warning_threshold', 'critical_threshold', 'sys_timestamp',
			'check_timestamp', 'age', 'refer')
	columns = columns if columns else default_columns
	p0 = "INSERT INTO %(table)s " % {'table': table}
	p1 = ' (%s) ' % ','.join(columns)
	p2 = ' , '.join(map(lambda x: ' %('+ x + ')s', columns))
	query = p0 + p1 + ' VALUES (' + p2 + ') '
	try:
		lcl_cnx = mysql_insert.mysql_cnx(site)
		cur = lcl_cnx.cursor()
		# cur.executemany(qry, map(lambda x: fmt_qry(**x), data_values))
		cur.executemany(query, data_values)
		lcl_cnx.commit()
		cur.close()
		lcl_cnx.close()
	except (OperationalError, InterfaceError) as db_exc:
		lcl_cnx.rollback()
		error('Error in mysql_insert task, {0}'.format(db_exc))
		#if self.request.retries >= self.max_retries:
		# store the data into mongo, as a backup
		mongo_insert.s(data_values, mongo_col, site).apply_async()
		# else:
		#	# perform a retry before taking data backup in mongo
		#	raise self.retry(exc=db_exc)
	except Exception as exc:
		# rollback transaction
		lcl_cnx.rollback()
		error('Error in mysql_insert task, {0}'.format(exc))

@app.task(base=DatabaseTask, name='availibility-mysql-insert', bind=True,
		default_retry_delay=40, max_retries=1)
def availibility_mysql_insert(self, table, data_values, site, columns=None):
	""" mysql batch insert"""

	#warning('Called with table: {0}'.format(table))
	default_columns = ('device_name', 'service_name', 'machine_name',
			'site_name', 'ip_address', 'data_source', 'severity',
			'current_value', 'min_value', 'max_value', 'avg_value',
			'warning_threshold', 'critical_threshold', 'sys_timestamp',
			'check_timestamp')
	columns = columns if columns else default_columns
	p0 = "INSERT INTO %(table)s " % {'table': table}
	p1 = ' (%s) ' % ','.join(columns)
	p2 = ' , '.join(map(lambda x: ' %('+ x + ')s', columns))
	query = p0 + p1 + ' VALUES (' + p2 + ') '
	try:
		lcl_cnx = mysql_insert.mysql_cnx(site)
		cur = lcl_cnx.cursor()
		# cur.executemany(qry, map(lambda x: fmt_qry(**x), data_values))
		cur.executemany(query, data_values)
		lcl_cnx.commit()
		cur.close()
	except (OperationalError, InterfaceError) as db_exc:
		lcl_cnx.rollback()
		error('Error in mysql_insert task, {0}'.format(db_exc))
		#if self.request.retries >= self.max_retries:
		# store the data into mongo, as a backup
		#mongo_insert.s(data_values, mongo_col, site).apply_async()
		# else:
		#	# perform a retry before taking data backup in mongo
		#	raise self.retry(exc=db_exc)
	except Exception as exc:
		# rollback transaction
		lcl_cnx.rollback()
		error('Error in mysql_insert task, {0}'.format(exc))

def delete_old_topology(cnx, old_topology):
	query = """
	DELETE FROM %(table)s
	WHERE %(column)s IN %(values)s
	"""
	mapping = {
		'table': 'performance_topology',
		'column': 'device_name',
		'values': "('%s')" % map(lambda x:  str(x) ,old_topology[0])[0]
	}
	cur = cnx.cursor()
	try:
		q = query % mapping
		cur.execute(q)
		if len(old_topology[1]) == 1:
			ip_tuple = "('%s')" % map(lambda x:  str(x) ,old_topology[1])[0]
		else:
			ip_tuple = "%s" % str(tuple(map(lambda x:  str(x) ,old_topology[1])))
		mapping.update({
			'column': 'connected_device_ip',
			'values': ip_tuple
		})
		q = query % mapping
		cur.execute(q)
		cnx.commit()
		cur.close()
		cnx.close()
	except Exception as exc:
		error('Error in removing old topology data: {0}'.format(exc))


@app.task(base=DatabaseTask, name='get-latest-entry', bind=True)
def latest_entry(self, site, op='S', value=None, perf_type=None):
	""" stores timestamp of last successful insert made into mysql"""
	lcl_cnx = latest_entry.mongo_cnx(site)
	stamp = None
	if op == 'S':
		# select operation
		try:
			stamp = list(lcl_cnx['latest_entry'].find(
				{'perf_type': perf_type}))[0].get('time')
		except: pass
	elif op == 'I':
		# insert operation
		lcl_cnx['latest_entry'].update({'perf_type': perf_type},
				{'time': value, 'perf_type': perf_type}, upsert=True)

	return float(stamp) if stamp else stamp


@app.task(base=DatabaseTask, name='mongo-export-mysql-handler')
def mongo_export_mysql_handler(site, delete_values):
	""" acquires a lock and sends a task for mongo_export_mysql
	"""
	rds_cli = RedisInterface().redis_cnx
	# redis lock
	lock = rds_cli.lock('mongo-export-mysql-handler', timeout=60*60)
	have_lock = lock.acquire(blocking=False)
	# ensures only one task is executed at a time
	if have_lock:
		mongo_export_mysql(site, delete_values)


@app.task(base=DatabaseTask, name='mongo-export-mysql', bind=True)
def mongo_export_mysql(site, delete_values):
	""" Export old data which is not in mysql due to its downtime,

	Args:
		site: used to connect to a particular mysql database
		delete_values: collection name --> doc count mapping, for which
		data has successfully been migrated to mysql and could be deleted
		from mongo
	"""

	warning('Mongo export mysql called')
	# sending the mysql insert tasks into batches of 6000 rows at a time
	size_of_chunk = 6000
	data_values = []
	# mongodb collections --> corresponding mysql tables mapping
	collection_table_mapping = {
		'service_perf': 'performance_performanceservice',
		'network_perf': 'performance_performancenetwork',
		'interface_perf': 'performance_performancestatus',
		'kpi_perf': 'performance_utilization',
		'deviceavailability_perf': 'performance_deviceavailibilitydaily',
	}
	# if mysql is down --> no point in reading data from mongo
	if not mongo_export_mysql.mysql_cnx(site).is_connected():
		return
	for mongo_col in collection_table_mapping:
		table = collection_table_mapping.get(mongo_col)
		try:
			data_values = list(mongo_export_mysql.mongo_cnx(site)[mongo_col].find())
		except Exception as exc:
			error('mongo_export_mysql error: {0}'.format(exc))

			# problem with the mongo itself --> no need to raise and
			# send `tasK_failure` signal
			break
		if data_values:
			for t in izip_longest(*[iter(data_values)] * size_of_chunk):
				warning('Importing {0} values to mysql for table: {1}'.format(
					len(t)), table)
				try:
					export_to_mysql.s(table, t, site).apply()
				except Exception as exc:
					error('Problem with the mysql export: {0}'.format(exc))
					# raise the exc, so that  `task_failure` signal is sent because
					# we still want the data in mongo
					raise exc
				else:
					val = delete_values[mongo_col] if delete_values.get(mongo_col) else 0
					delete_values.update({
						mongo_col: val + size_of_chunk
						})
				sleep(5)
		sleep(10)


@app.task(base=DatabaseTask, name='export-to-mysql', bind=True,
		default_retry_delay=60, max_retries=1)
def export_to_mysql(self, table, data_values, site, columns=None):
	""" mysql batch insert, called only for data migration from mongo to mysql"""

	for entry in data_values:
		entry.pop('_id', '')
		entry['sys_timestamp'] = entry['sys_timestamp'].strftime('%s')
		entry['check_timestamp'] = entry['check_timestamp'].strftime('%s')
	default_columns = ('device_name', 'service_name', 'machine_name',
	                   'site_name', 'ip_address', 'data_source', 'severity',
	                   'current_value', 'min_value', 'max_value', 'avg_value',
	                   'warning_threshold', 'critical_threshold', 'sys_timestamp',
	                   'check_timestamp', 'age', 'refer')
	columns = columns if columns else default_columns
	p0 = "INSERT INTO %(table)s " % {'table': table}
	p1 = ' (%s) ' % ','.join(columns)
	p2 = ' , '.join(map(lambda x: ' %('+ x + ')s', columns))
	query = p0 + p1 + ' VALUES (' + p2 + ') '
	lcl_cnx = export_to_mysql.mysql_cnx(site)
	cur = lcl_cnx.cursor()
	cur.executemany(query, data_values)
	lcl_cnx.commit()
	cur.close()


@app.task(base=DatabaseTask, name='purge-mongo-data')
def purge_mongo_data(col_name, col_count, site):
	""" deletes data from mongo, which has been successfully migrated to
	mysql
	"""
	try:
		local_cnx = purge_mongo_data.mongo_cnx(site)[col_name]
		ids = map(lambda x: x.get('_id'), list(local_cnx.find({}, {'_id': 1}).limit(
			col_count)))
		local_cnx.remove({'_id': {'$in': ids}})
	except Exception as exc:
		error('Error in mongo deletion: {0}'.format(exc))
