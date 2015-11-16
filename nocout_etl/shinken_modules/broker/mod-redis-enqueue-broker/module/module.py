"""
redis-enqueue-broker-module
============================

Shinken broker module to brok information of 
services/hosts and events into redis backed queue
"""

from ast import literal_eval
from redis import StrictRedis
from redis.sentinel import Sentinel
from threading import Thread
from shinken.basemodule import BaseModule
from shinken.log import logger
import Queue
from logevent import LogEvent
from multiprocessing import Process,Queue
info, warning, error = logger.info, logger.warning, logger.error


properties = {
              'daemons': ['broker'],
              'type': 'redis-enqueue-broker',
              'external': True,
	      'phases': ['running'],
              }


# called by the plugin manager to get a module instance
def get_instance(mod_conf):
    info('[%s] Get a Broker module %s' 
    		% (mod_conf.get_name(), mod_conf.get_name()))
    instance = RedisEnqueueBroker(mod_conf)
    return instance


class RedisEnqueueBroker(BaseModule):
	""" Enqueue broks into a redis backed queue"""

	def __init__(self, mod_conf):
		BaseModule.__init__(self, mod_conf)
		# create shared queues
		#manager = Manager()
		#self.create_queues(manager=manager)
		self.queue=Queue(200000)	
		# store only host and service check results
		self.host_valid_broks = ['host_check_result']
		self.service_valid_broks = ['service_check_result']
		self.valid_broks = ['host_check_result','service_check_result','log']
		# need only these keys out of complete check result
		self.host_valid_attrs = ['address', 'state', 'last_chk', 
				'last_state_change', 'host_name', 'perf_data']
		self.service_valid_attrs = self.host_valid_attrs + ['service_description']
		# need to save plugin output for these services as well
		self.need_plugin_out = ['wimax_topology', 'cambium_topology']
		self.redis_conf = {
				'host': getattr(mod_conf, 'host', 'localhost'),
				'port': getattr(mod_conf, 'port', 6379),
				'db': int(getattr(mod_conf, 'db', 0))
				}
		sentinels = []
		sentinels_conf = getattr(mod_conf, 'sentinels', None)
		if sentinels_conf:
			sentinels_conf = sentinels_conf.split(',')
			while sentinels_conf:
				sentinels.append(tuple(sentinels_conf[:2]))
				sentinels_conf = sentinels_conf[2:]
		sentinels_service_name = getattr(mod_conf, 'service_name', 'mymaster')
		min_other_sentinels = getattr(mod_conf, 'min_other_sentinels', 0)

		self.redis_conf.update({
			'sentinels': sentinels, 
			'sentinels_service_name': sentinels_service_name,
			'min_other_sentinels': min_other_sentinels
			})

		# redis conn
		self.rds_cnx = RedisQueue(**self.redis_conf)


	def main(self):
		self.set_proctitle(self.name)
		self.set_exit_handler()
		info('[%s] Start main function.' % self.name)
		#worker=Process(target=self.process_brok,args=(self.queue,))
		#worker = Thread(target=self.process_brok)
		#worker.daemon=True
		#worker.start()
		#info('[%s] Process id.' % worker.pid)
		self.start_loop()

	def start_loop(self):
		valid_event_type = ['ALERT']
		while not self.interrupted:
			broks = self.to_q.get()
			brok_list = []
			error('Queue size %s' % self.to_q.qsize() )
			for brok in broks:
				#info('brok: %s' % brok)
				try:
					#msg = dict([(k, v) for  k, v in brok.data.iteritems() if 
					#	k in self.valid_attrs])
					#self.rds_cnx.put(msg)
					if brok and brok.type in self.valid_broks:
						brok.prepare()
						if brok.type == 'log':
							log = brok.data['log']
							event = LogEvent(log)
							data = event.data
							if data and data['event_type'] in valid_event_type:
								alrt_type = data['alert_type']
								if alrt_type in ['HOST','SERVICE']:
									if alrt_type == 'HOST':
										data.update({'service_desc': 'ping'})
									brok_list.append(data)
									#error('log %s' % data)
									
						else:
							brok_list.append(brok)
					#self.manage_brok(brok)
				except Exception as exc:
					error('[%s] Problem with brok: '
				     	 	 '%s' % (self.name, exc))
			self.manage_brok(brok_list)
			#self.process_brok(brok_list)

	def manage_brok(self,brok_list):
		try:
			#if brok and brok.type in self.valid_broks:
			self.rds_cnx.put('brok:data', *brok_list)
			#self.queue.put_nowait(brok_list)
			#error('Q:len:M %s' % self.queue.qsize())
		except Exception,e:
			error('Error in inserting redis queue %s' % e)
		

	# called by base module
	def manage_log_brok(self, brok):
		# we need only alerts
		valid_event_type = ['ALERT']
		log = brok.data['log']
		event = LogEvent(log)
		data = event.data
		if data and data['event_type'] in valid_event_type:
			#info('[%s] Data: %s' % (self.name, data))
			alrt_type = data['alert_type']
			try:
				if alrt_type == 'HOST':
					data.update({'service_desc': 'ping'})
					self.rds_cnx.put('event:host', data)
				elif alrt_type == 'SERVICE':
					self.rds_cnx.put('event:service', data)
			except:
				error('Exception in log ')
			

	# called by base module
	def manage_host_check_result_brok(self, brok):
		# get broks from queue broks
		#broks = self.broks
		if brok.type in self.host_valid_broks:
			try:
				# don't process the host data more than once in 5 mins window
				host_name = brok.data['host_name']
				host_key = ':'.join(['volatile', host_name])
				if self.rds_cnx.get(host_key):
					return
				else:
					self.rds_cnx.setex(host_key, 300, 1)

				msg = dict([(k, v) for  k, v in brok.data.iteritems() if 
					k in self.host_valid_attrs])
				self.rds_cnx.put('perf:host', msg)
				#info('[%s] brok: %s' % (self.name, msg))

			except Exception as exc:
				error('[%s] Problem with brok: '
						     '%s' % (self.name, exc))

	# called by base module
	def manage_service_check_result_brok(self, brok):
		service_valid_attrs = self.service_valid_attrs
		#info('[%s] Start manage_service_check_result_brok' % self.name)
		if brok.type in self.service_valid_broks:
			#info('[%s] brok: %s' % (self.name, brok.data))
			service = str(brok.data['service_description'])
			if service == 'Check_MK':
				return
			if service in self.need_plugin_out:
				service_valid_attrs += ['output']
			try:
				msg = dict([(k, v) for  k, v in brok.data.iteritems() if 
					k in service_valid_attrs])
				# for load testing purposes
				li = []
				[li.append(msg.copy()) for _ in range(1)]
				self.rds_cnx.put('perf:service', *li)
			except Exception as exc:
				error('[%s] Problem with brok: '
						     '%s' % (self.name, exc))


	def process_brok(self,q):
		while True:
			error('Process brok %s',q.qsize())
			result_list= []
			try:
				for items in range(0,q.qsize()):
					#error('item: %s',items)
					result_list.append(q.get_nowait())
			except Exception,e:
				error('Error %s', e)
				continue	
			#except:
			#	error('error in process brok'  )
			#error('Q:len:B %s' % q.qsize())
			for brok_entry in result_list:
				for brok in brok_entry:
					if brok.type == 'host_check_result':
						self.manage_host_check_result_brok(brok)
					elif brok.type =='service_check_result':
						self.manage_service_check_result_brok(brok)
					elif brok.type =='log':
						self.manage_log_brok(brok)
class RedisQueue:
	""" Queue with redis backend"""

	def __init__(self, **redis_conf):
		self.prefix = 'q'
		sentinels = redis_conf.pop('sentinels', '()')
		sentinels_service_name = redis_conf.pop('sentinels_service_name', 
				'mymaster')
		min_other_sentinels = redis_conf.pop('min_other_sentinels', 0)
		s = Sentinel(sentinels, **redis_conf)
		self.db = s.master_for(sentinels_service_name)
		#self.db = StrictRedis(**redis_conf)

	def put(self, suffix, *items):
		key = '%s:%s' % (self.prefix, '%s')
		self.db.rpush(key % suffix, *items)
		# save on disk
		#self.db.save()

	def get(self, key):
		return self.db.get(key)

	def setex(self, key, time, value):
		return self.db.setex(key, time, value)
