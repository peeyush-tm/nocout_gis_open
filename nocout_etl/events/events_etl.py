"""
events_etl.py
================

This module manages log events for both hosts and services
"""

import re

from celery import chord, Task

from handlers.db_ops import (mysql_insert_handler, 
		RedisInterface, get_task_logger)
from start.start import app

logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error

# redis db with device inventory info
INVENTORY_DB = getattr(app.conf, 'INVENTORY_DB', 3)

event_output_pattern = re.compile(\
		'([^ ]*) - ([^:]*): rta ([^ms,]*)(?:ms)?, lost ([^%]*)%'
		)


class EventTaskBase(Task):
	""" Base events class for one Redis connection per 
	worker and sending tasks in batches"""

	ignore_result = True

	def __call__(self, *args, **kwargs):
		self.q_name = kwargs.get('queue')
		self.site_name = kwargs.get('site_name')
		# type of event, host or service
		self.event_type = 'host' if 'host' in self.q_name else 'service' 
		self.rds_cnx = RedisInterface(perf_q=self.q_name)
		return self.run()

	def run(self):
		# get data from redis queue
		data = self.rds_cnx.get(0, -1)
		info('Queue: {0} len: {1}'.format(self.name, len(data)))
		if data:
			name_ip_mapping = self.map_name_ip()
			batches = self.get_batches(data)
			do_work(None, self.event_type, name_ip_mapping, 
					batches, self.site_name)

	def get_batches(self, data):
		""" prepares batches of data"""
		batches = []
		while data:
			t = min(len(data), 5000)
			batches.append(data[:t])
			data = data[t:]
		return batches

	def map_name_ip(self):
		""" Loads device inventory info from Redis with name --> ip mapping, 
		makes a new redis connection"""
		conn = RedisInterface(custom_conf={'db': INVENTORY_DB}).redis_cnx
		p = conn.pipeline()
		keys = conn.keys(pattern='device_inventory:*')
		[p.get(k) for k in keys]

		return dict([t for t in zip(keys, p.execute())])



@app.task(name='events_export_caller', ignore_result=True)
def do_work(results, event_type, name_ip_mapping, batches, site_name):
	batch = batches.pop(0)
	batch_task = build_export_events.s(event_type, name_ip_mapping, 
			batch, site_name) 
	if batches:
		callback = do_work.s(name_ip_mapping, batches)
		return chord(batch_task)(callback)
	else:
		batch_task.apply_async()


@app.task(name='events_export', ignore_result=True)
def build_export_events(event_type, name_ip_mapping, events, site_name):
	table_names = {
			'host': {
				'live': 'performance_eventnetwork',
				'status': 'performance_eventnetworkstatus'
				},
			'service': {
				'live': 'performance_eventservice',
				'status': 'performance_eventservicestatus'
				},
			}
	columns = ('device_name', 'service_name', 'machine_name',
			'site_name', 'ip_address', 'data_source', 'severity',
			'current_value', 'min_value', 'max_value', 'avg_value',
			'warning_threshold', 'critical_threshold', 'sys_timestamp',
			'check_timestamp', 'description')
	final_events = []

	for event in events:
		for_host = False
		# ignore events related to counter reset
		if 'wrapped' in event:
			continue
		event['ip_address'] = name_ip_mapping.get(event['hostname'])
		patch_event_keys(event)
		if event['alert_type'] == 'HOST':
			for_host = True
		event.pop('alert_type', '')
		# split the event pckt for host events, based on pl and rta
		if for_host:
			data_source_states = parse_event_output(event['description'])
			for ds, val in data_source_states.iteritems():
				tmp = {}
				tmp.update(event)
				tmp['data_source'] = ds
				tmp['current_value'] = val
				final_events.append(tmp)
		else:
			final_events.append(event)

    # args: (data, live_db, status_db, mongo_live_db, site)
	mysql_insert_handler.s(
			final_events,
			table_names[event_type]['live'],
			table_names[event_type]['status'],
			table_names[event_type]['live'], 
			'pub_slave_1', 
			columns=columns
			).apply_async()


def parse_event_output(output):
	ds_states = {}
	matched = event_output_pattern.match(output)
	if matched:
		ds_states.update(
				{
					'rta': matched.group(3), 
					'pl': matched.group(4)
					}
				)
	return ds_states


def patch_event_keys(event):
	""" function to rename/add/remove keys from a event dict 
	to match mysql table structure"""
	# these event properties not needed for mysql insertion
	pop_entries = ['event_type', 'attempts', 'state_type']
	# setting default values for these event properties
	default_vals = [
			'current_value', 'max_value', 'min_value', 
			'avg_value', 'age', 'refer',  
			'data_source', 'warning_threshold', 'critical_threshold']
	old_to_new_keys = {
			'hostname': 'device_name',
			'service_desc': 'service_name',
			'state': 'severity',
			'output': 'description'
			}
	[event.pop(e, '') for e in pop_entries]
 	event['check_timestamp'] = event['sys_timestamp'] = event.pop('time', '')
 	for old, new in old_to_new_keys.iteritems():
 		event[new] = event.pop(old, '')
 	event['site_name']  = event['machine_name'] = None
 	for x in default_vals:
 		event[x] = None


@app.task(name='service-main')
def main(**opts):
	opts = {'site_name': 'pub_slave_1',
			'queue': 'q:event:host'}
	event_task = EventTaskBase()
	event_task(**opts)


if __name__ == '__main__':
	main()
