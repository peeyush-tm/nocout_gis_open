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
from operator import itemgetter
from redis import StrictRedis
from redis.sentinel import Sentinel
from time import sleep
from configobj import ConfigObj
import ujson
import zlib
import memcache
from nocout_site_name import *

#logger = get_task_logger(__name__)
#info , warning, error = logger.info, logger.warning, logger.error

#DB_CONF = getattr(app.conf, 'CNX_FROM_CONF', None)
#SENTINELS = getattr(app.conf, 'SENTINELS', None)



config =ConfigObj('/omd/sites/%s/lib/python/handlers/redis_config.ini' % nocout_site_name)
class RedisInterface(object):
	""" Implements various redis operations"""

	#__slots__ = ['custom_conf', 'redis_conn', 'perf_q']


	def __init__(self, **kw):
		self.custom_conf = kw.get('custom_conf')
		self.redis_conn = None
		# queue name to get check results data from 
		#self.perf_q = kw.get('service_q')

	def conn_from_conf(self, custom_conf=None):
		""" Method used to get redis connection without binding 
		with any queue"""
		self.custom_conf = custom_conf
		return self.redis_cnx

	@property
	def redis_cnx(self):
		#conf = ConfigParser()
		#conf.read(DB_CONF)
		# redis connection config
		re_conf = {
			'port': int(config.get('redis').get('port')),
			'db': int(config.get('redis').get('db'))
		}
		#re_conf.update(self.custom_conf) if self.custom_conf else re_conf
		service_name = config.get('redis').get('service_name')
		try:
			#self.redis_conn = StrictRedis(**re_conf)
			SENTINELS = []
			sentinel_info = config.get('sentinel')
			SENTINELS.append((sentinel_info.get('ospf1_host'),int(sentinel_info.get('ospf1_port'))))		
			SENTINELS.append((sentinel_info.get('ospf2_host'),int(sentinel_info.get('ospf2_port'))))		
			SENTINELS.append((sentinel_info.get('ospf3_host'),int(sentinel_info.get('ospf3_port'))))		
			SENTINELS.append((sentinel_info.get('ospf4_host'),int(sentinel_info.get('ospf4_port'))))		
			SENTINELS.append((sentinel_info.get('ospf5_host'),int(sentinel_info.get('ospf5_port'))))		
			SENTINELS.append((sentinel_info.get('vrfprv_host'),int(sentinel_info.get('vrfprv_port'))))		
			SENTINELS.append((sentinel_info.get('pub_host'),int(sentinel_info.get('pub_port'))))		
			sentinel = Sentinel(SENTINELS, **re_conf)
			self.redis_conn = sentinel.main_for(service_name) 
		except Exception as exc:
			print exc

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
			#error('Redis pipe error in update... {0}, retrying...'.format(exc))
			print exc
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
			print exc
			#error('Redis pipe error in multi get... {0}'.format(exc))

		return out

	def multi_set(self, data_values, perf_type='',time=None):
		""" Sets multiple key values through pipeline"""
		KEY = '%s:%s:%s' % (perf_type, '%s', '%s')
		p = self.redis_cnx.pipeline(transaction=True)
		# keep the provis data keys with a timeout of 5 mins
		if not time:
			time = 300
		[p.setex(KEY %
		         (d.get('device_name'), d.get('service_name')),
		         time, d.get('current_value')) for d in data_values
		 ]
		try:
		    p.execute()
		except Exception as exc:
		    print exc
		    #error('Redis pipe error in multi_set: {0}'.format(exc))
	def zadd_compress(self,set_name,time,data_value):
		""" adds data to redis on sorted set """
		try:
			cnx = self.redis_cnx
			serialized_value = ujson.dumps(data_value)
			compressed_value =zlib.compress(serialized_value)
			cnx.zadd(set_name,time,compressed_value)
		except Exception,e:
			print e
		    	#error('Redis error in adding in set{0}'.format(exc))
	def zrangebyscore_dcompress(self,set_name,start_time,end_time):
		""" retrieving the latest doc between start_time and end_time"""
		serialized_value = []
		try:
			cnx = self.redis_cnx
			value = cnx.zrangebyscore(set_name,start_time,end_time)
			dcomp_value=[zlib.decompress(value[index]) for index in xrange(len(value))]
			#decompressed_value =zlib.decompress(value)
			serialized_value=[item for index in xrange(len(dcomp_value)) for item in ujson.loads(dcomp_value[index])]
			#serialized_value = ujson.loads(decompressed_value)
		except Exception,e:
			pass				
		return serialized_value
	def zremrangebyscore_remove(self,set_name,start_time,end_time):
		try:
			cnx = self.redis_cnx
			ret =cnx.zremrangebyscore(set_name,start_time,end_time)
		except Exception,e:
			pass 
		return ret	
class MemcacheInterface(object):
	""" Memcache implementation """

	def __init__(self, **kw):
		self.memc = None
	@property
	def memc_conn(self):
		try:
			memcache_info = config.get('memcache')
			memcache_port=memcache_info.get('port')
			memc_string =[]
			ospf1_con_string= memcache_info.get('ospf1_host') + ":" + str(memcache_port)
			ospf2_con_string= memcache_info.get('ospf2_host') + ":" + str(memcache_port)
			ospf3_con_string= memcache_info.get('ospf3_host') + ":" + str(memcache_port)
			ospf4_con_string= memcache_info.get('ospf4_host') + ":" + str(memcache_port)
			ospf5_con_string= memcache_info.get('ospf5_host') + ":" + str(memcache_port)
			memc_string.extend([ospf1_con_string,ospf2_con_string,ospf3_con_string,ospf4_con_string,ospf5_con_string])
			self.memc = memcache.Client(memc_string, debug=1)
		except Exception,e:
			print e
		return self.memc
		 
		
	def store(self,key,value, doc_len_key,time,chunksize=1000):
	   #serialized = pickle.dumps(value, 2)
	   values = {}
	   memc = self.memc_conn
	   for i in xrange(0, len(value), chunksize):
		#print i
		values['%s.%s' % (key, i/chunksize)] = value[i : i+chunksize]
	   doc_len = i/chunksize
	   #print len(values)

	   if 1000*doc_len < len(value):
		doc_len =doc_len +1
		values['%s.%s' % (key, doc_len)] = value[i : len(value)]
	   memc.set_multi(values,time)
	   memc.set(doc_len_key,doc_len,time) 
	   #memc.set("service_doc_len",doc_len,time=240)
	def retrieve(self,key,doc_len_key):
	    memc=self.memc_conn
	    my_list = []
	    if memc:
		y=memc.get(doc_len_key)
		result = memc.get_multi(['%s.%s' % (key, i) for i in xrange(y)])
		serv_list=[v for v in result.values() if v is not None]
		my_list = [item for sublist in serv_list for item in sublist]	
		#print len(my_list)
	    return my_list
	
@app.task(base=DatabaseTask, name='threshold-kpi-services', bind=True)
def store_threshold_for_kpi_services(self):
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
	"where devicetype.name <> 'Default' and service.name like '%_kpi'; "
	)
	#info('sample {0}'.format('Testing'))
	cur = store_threshold_for_kpi_services.mysql_cnx('historical').cursor()
	cur.execute(query)
	out = cur.fetchall()
	#info('out: {0}'.format(out))
	rds_cli = RedisInterface(custom_conf={'db': 3})
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
		"device_devicetechnology.name IN ('WiMAX', 'P2P', 'PMP')"
	)
	dr_query = (
		"SELECT "
		"inner_device.Sector_IP AS primary_ip, "
		"outer_device.ip_address AS dr_ip "
		"FROM ( "
			"SELECT "
				"ds.ip_address AS Sector_IP, "
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
    	"device_devicetype.name in ('Switch', 'RiCi', 'PINE') "
    	"group by device_device.ip_address;" )


	ping_threshold_query = ("select name,rta_warning,rta_critical,pl_warning,pl_critical from device_devicetype; ")

	cur.execute(backhaul_query)
	backhaul_out = cur.fetchall()
	
	ping_threshold_dict = {}
	# Calculate warning and critical for device type to be used in Event 
	cur.execute(ping_threshold_query)
	ping_threshold_out = cur.fetchall()
	for d1 in ping_threshold_out:
		ping_threshold_dict[d1[0]] = []
		ping_threshold_dict[d1[0]].extend([d1[1],d1[2],d1[3],d1[4]])

	warning('out: {0}'.format(ping_threshold_dict))
	
	# e.g. keeping invent data in database number 3
	rds_cli = RedisInterface(custom_conf={'db': 3})
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

@app.task(name='load-backhaul-data')
def load_backhaul_data(data_values, p, extra=None):
	t = data_values[0]
	processed = []
	#info('PORT-Data: {0}'.format(data_values))
	# key:: <device-tech>:<device-type>:<site-name>:<ip>
	key = '%s:%s:%s:%s' % (str(t[3]).lower(),
					'ss' if t[3].endswith('SS') else 'bs',
					'%s',
					'%s')
	invent_key = 'device_inventory:%s'
	for device in data_values:
		device_attr = []
		if str(device[3].lower()) == 'Cisco' or str(device[3].lower()) == 'Juniper':
			port_wise_capacities = [0]*26
		else:
			port_wise_capacities = [0]*8
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
			#info('ERR-Data: {0}'.format(err))
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
				if inner[0] == outer[2]:
					matched_dr = inner[1]
					break
			if matched_dr:
				outer.append(matched_dr)
				matched_dr = None
	#[p.rpush(key % data[2], data[:last_index]) for data in data_values]
	for data in data_values:
		p.set(invent_key % data[0], data[2])
		p.rpush(key % (data[1], data[2]), data[:last_index])

		
