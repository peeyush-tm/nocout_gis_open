"""
db_ops.py
==========

Maintains per process database connections and handles 
data manipulations, used in site-wide ETL operations.
[for celery]
"""


from ast import literal_eval
from ConfigParser import ConfigParser
from itertools import groupby, izip_longest
import memcache
from mysql.connector import connect
from mysql.connector.errors import (OperationalError, InterfaceError)
from operator import itemgetter
from pymongo import MongoClient
from redis import StrictRedis
from time import sleep

from celery import Task
from celery.contrib.methods import task_method
from celery.utils.log import get_task_logger

from start.start import app

logger = get_task_logger(__name__)
info , warning, error = logger.info, logger.warning, logger.error

db_conf = app.conf.CNX_FROM_CONF
INVENTORY_DB = getattr(app.conf, 'INVENTORY_DB', 3)

class DatabaseTask(Task):
	abstract = True
	# maintains database connections based on sites
	# mysql connections
	my_conn_pool = {}
	# mongo connections
	mo_conn_pool = {}
	# redis connection object
	memc_conn_pool = {}
	# memc connection object
	redis_conn = None

	conf = ConfigParser()
	conf.read(db_conf)

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
	def memc_cnx(self,key):
		if not self.memc_conn_pool.get(key):
			try:
				#memc_conf = []
				self.memc_conn_pool[key] = memcache.Client(['10.133.19.165:11211','10.133.12.163:11211'], debug=1)
			except Exception as e:
				error('Memc connection problem, retrying... {0}'.format(e))
    				#self.memc_conn_pool[key] =None
		return self.memc_conn_pool.get(key)	

class RedisInterface:
	""" Implements various redis operations"""

	def __init__(self, **kw):
		self.custom_conf = kw.get('custom_conf')
		self.redis_conn = None
		# queue name to get check results data from 
		self.perf_q = kw.get('perf_q')

	@property
	def redis_cnx(self):
		conf = ConfigParser()
		conf.read(db_conf)
		# redis connection config
		re_conf = {
			'port': int(conf.get('redis', 'port')),
			'db': int(conf.get('redis', 'db'))
		}
		re_conf.update(self.custom_conf) if self.custom_conf else re_conf
		try:
			self.redis_conn = StrictRedis(**re_conf)
		except Exception as exc:
			error('Redis connection error... {0}'.format(exc))

		return self.redis_conn

	def get(self, start, end):
		""" Get and remove values from redis list based on a range"""
		output = self.redis_cnx.lrange(self.perf_q, start, end)
		output = [literal_eval(x) for x in output]
		# keep only unread values in list
		self.redis_cnx.ltrim(self.perf_q, end+1, -1)

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
				p.execute()

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


@app.task(base=DatabaseTask, name='load-inventory', bind=True)
def load_inventory(self):
	"""
	Loads inventory data into redis
	"""
	query = (
		"SELECT DISTINCT D.device_name, site_instance_siteinstance.name, "
		"D.ip_address, device_devicetype.name AS dev_type, "
		"device_devicetechnology.name AS dev_tech "
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
		"WHERE "
		"D.is_deleted = 0 AND "
		"D.host_state <> 'Disable' AND "
		"device_devicetechnology.name IN ('WiMAX', 'P2P', 'PMP', 'Mrotek', 'RiCi')"
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
	# info('out: {0}'.format(out))

	# keeping invent data in database number 3
	rds_cli = RedisInterface(custom_conf={'db': INVENTORY_DB})
	rds_cli.redis_cnx.flushdb()
	rds_pipe = rds_cli.redis_cnx.pipeline(transaction=True)
	wimax_bs_list = []
	# group based on device technologies and load the devices info to redis
	out = sorted(out, key=itemgetter(3))
	for grp, grp_vals in groupby(out, key=itemgetter(3)):
		grouped_devices = list(grp_vals)
		if grouped_devices[0][3] == 'StarmaxIDU':
			[wimax_bs_list.append(list(x)) for x in grouped_devices]
			# push wimax bs with its dr site info
			cur.execute(dr_query)
			dr_info = cur.fetchall()
			cur.close()
			#warning('dr hosts: {0}'.format(dr_info))
			load_devicetechno_wise(wimax_bs_list, rds_pipe, extra=dr_info)
		else:
			load_devicetechno_wise(grouped_devices, rds_pipe)
	try:
		rds_pipe.execute()
	except Exception as exc:
		error('Error in redis inventory loading... {0}'.format(exc))
	else:
		warning('Inventory loading done.')


@app.task(name='load-devicetechno-wise')
def load_devicetechno_wise(data_values, p, extra=None):
	"""
	Loads specific device technology data into redis
	"""
	t = data_values[0]
	# key:: <device-tech>:<device-type>:<site-name>:<ip>
	key = '%s:%s:%s:%s' % (str(t[4]).lower(),
					'ss' if t[3].endswith('SS') else 'bs',
					'%s',
					'%s')
	# keeping basic inventory info of a device, name --> ip mapping
	invent_key = 'device_inventory:%s'
	# entries needed from index 0 to last_index-1
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
	for entry in data_values:
		entry.pop('_id', '')
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
	
	#warning('Called with table: {0}'.format(table))
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
	except Exception as exc:
		# rollback transaction
		lcl_cnx.rollback()
		# attempt task retry
		raise self.retry(exc=exc)

	warning('Len for status upserts {0}\n'.format(len(data_values)))


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
