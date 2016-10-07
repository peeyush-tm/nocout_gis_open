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
#from nocout_site_name import *

#logger = get_task_logger(__name__)
#info , warning, error = logger.info, logger.warning, logger.error

#DB_CONF = getattr(app.conf, 'CNX_FROM_CONF', None)
#SENTINELS = getattr(app.conf, 'SENTINELS', None)
import os
p = os.path.dirname(os.path.abspath(__file__))
paths = [path for path in p.split('/')]
nocout_site_name = paths[paths.index('sites') + 1]


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
			self.redis_conn = sentinel.master_for(service_name) 
		except Exception as exc:
			print exc

		return self.redis_conn

        @property
        def redis_cnx_prd4(self):
                #conf = ConfigParser()
                #conf.read(DB_CONF)
                # redis connection config
                re_conf = {
                        'port': int(config.get('redis_prd4').get('port')),
                        'db': int(config.get('redis_prd4').get('db'))
                }
                #re_conf.update(self.custom_conf) if self.custom_conf else re_conf
                service_name = config.get('redis_prd4').get('service_name')
                try:
                        #self.redis_conn = StrictRedis(**re_conf)
                        SENTINELS = []
                        sentinel_info = config.get('sentinel')
                        SENTINELS.append((sentinel_info.get('prd4_host'),int(sentinel_info.get('prd4_port'))))
                        sentinel = Sentinel(SENTINELS, **re_conf)
                        self.redis_conn = sentinel.master_for(service_name)
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

	def multi_set(self, data_values, perf_type='',exp_time=None):
		""" Sets multiple key values through pipeline"""
		KEY = '%s:%s:%s' % (perf_type, '%s', '%s')
		p = self.redis_cnx.pipeline(transaction=True)
		# keep the provis data keys with a timeout of 5 mins
		if not exp_time:
			exp_time = 300
		[p.setex(KEY %
		         (d.get('device_name'), d.get('service_name')),
		         exp_time, d.get('current_value')) for d in data_values
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
	   try: 
	   	doc_len = i/chunksize
	   #print len(values)

	   	if 1000*doc_len < len(value):
			doc_len =doc_len +1
			values['%s.%s' % (key, doc_len)] = value[i : len(value)]
	   	memc.set_multi(values,time)
	   	memc.set(doc_len_key,doc_len,time)
	   except:
		pass 
	   #memc.set("service_doc_len",doc_len,time=240)
	def retrieve(self,key,doc_len_key):
	    memc=self.memc_conn
	    my_list = []
	    try:
	    	if memc:
			y=memc.get(doc_len_key)
			result = memc.get_multi(['%s.%s' % (key, i) for i in xrange(y)])
			serv_list=[v for v in result.values() if v is not None]
			my_list = [item for sublist in serv_list for item in sublist]
	    except:
		pass	
		#print len(my_list)
	    return my_list
