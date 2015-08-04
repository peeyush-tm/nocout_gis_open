"""
redis-enqueue-broker-module
============================

Store host check results received from broker
into a redis backed queue
"""

from redis import StrictRedis

from shinken.basemodule import BaseModule
from shinken.log import logger

info, warning, error = logger.info, logger.warning, logger.error


properties = {
              'daemons': ['broker'],
              'type': 'redis-enqueue-broker',
              'external': False
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
		
		# store only host and service check results
		self.host_valid_broks = ['host_check_result']
		self.service_valid_broks = ['service_check_result']
		# need only these keys out of complete check result
		self.host_valid_attrs = ['address', 'state', 'last_chk', 
				'last_state_change', 'host_name', 'perf_data']
		self.service_valid_attrs = self.host_valid_attrs + ['service_description']
		# need to save plugin output for these services as well
		self.need_plugin_out = ['wimax_topology', 'cambium_topology']
		self.redis_conf = {
				'host': getattr(mod_conf, 'host', 'localhost'),
				'port': getattr(mod_conf, 'port', 6379),
				'db': int(getattr(mod_conf, 'database', 0))
				}
		# redis queue
		self.queue = RedisQueue(**self.redis_conf)


	def main(self):
		info('[%s] Start main function.' % self.name)
		while not self.interrupted:
			broks = self.to_q.get()
			for brok in broks:
				brok = brok.prepare()
				info('brok: %s' % brok)
				if brok and brok.type in self.valid_broks:
					try:
						msg = dict([(k, v) for  k, v in brok.data.iteritems() if 
							k in self.valid_attrs])
						self.queue.put(msg)
					except Exception as exc:
						error('[%s] Problem with brok: '
						     	 	 '%s' % (self.name, exc))

	# called by base module
	def manage_host_check_result_brok(self, brok):
		info('[%s] Start manage_host_check_result_brok' % self.name)
		# get broks from queue broks
		#broks = self.broks
		if brok.type in self.host_valid_broks:
			try:
				#info('[%s] brok: %s' % (self.name, brok.data.items()))
				msg = dict([(k, v) for  k, v in brok.data.iteritems() if 
					k in self.host_valid_attrs])
				self.queue.put('host', msg)
			except Exception as exc:
				error('[%s] Problem with brok: '
						     '%s' % (self.name, exc))

	# called by base module
	def manage_service_check_result_brok(self, brok):
		service_valid_attrs = self.service_valid_attrs
		info('[%s] Start manage_service_check_result_brok' % self.name)
		if brok.type in self.service_valid_broks:
			info('[%s] brok: %s' % (self.name, brok))
			service = str(brok.data['service_description'])
			if service == 'Check_MK':
				return
			if service in self.need_plugin_out:
				service_valid_attrs += ['output']
			try:
				msg = dict([(k, v) for  k, v in brok.data.iteritems() if 
					k in service_valid_attrs])
				self.queue.put('service', msg)
			except Exception as exc:
				error('[%s] Problem with brok: '
						     '%s' % (self.name, exc))


class RedisQueue:
	""" Queue with redis backend"""

	def __init__(self, **redis_conf):
		self.prefix = 'queue'
		self.db = StrictRedis(**redis_conf)
		self.key = '%s:%s' % (self.prefix, '%s')

	def put(self, suffix, *items):
		self.db.rpush(self.key % suffix, *items)
		# save on disk
		#self.db.save()
