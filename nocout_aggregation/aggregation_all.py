"""
aggregation_all.py
==================
Performance and network data aggregation
"""

import time
import sys
from datetime import datetime, timedelta
from pprint import pprint
import collections
from operator import itemgetter
from itertools import groupby
import optparse
from ConfigParser import ConfigParser

import historical_mysql_export
import host_wise_aggr
from celery import chain, group
import entry
app = entry.app
print app


@app.task(name='add')
def add(x, y):
    return x + y


@app.task(name='prepare-main', ignore_result=True)
def prepare_data(**extra_opts):
    """
    Quantifies (int, float) perf data using `min`, `max` and `sum` funcs
    and frequency based data on number of  occurrences of values
    """
    
    data_values = []
    #end_time = datetime.now()
    end_time = datetime(2015, 6, 1, 6, 0)
    start_time = end_time - timedelta(hours=extra_opts.get('hours'))
    start_time = start_time - timedelta(minutes=1)
    print start_time, end_time
    start_time, end_time = int(start_time.strftime('%s')), int(end_time.strftime('%s'))
    result = group(
		chain(
			historical_mysql_export.read_data.s(
				map(str, list(device_gen_obj)), 
				extra_opts.get('source_perf_table'), 
				start_time, 
				end_time,
				machine=str(extra_opts.get('machine'))
				),
			host_wise_aggr.quantify_perf_data.s(
				time_frame=extra_opts.get('time_frame'),
				destination_perf_table=extra_opts.get('destination_perf_table')
				)
			)
		for device_gen_obj in historical_mysql_export.get_active_inventory_devices(
				machine=str(extra_opts.get('machine')),
				all=extra_opts.get('all'))
	).apply_async()


def usage():
    print "Usage: service_mongo_aggregation_hourly.py [options]"


@app.task(name='aggregation-main', ignore_result=True)
def main(**extra_opts):
        prepare_data.s(**extra_opts).apply_async()


@app.task(name='demo-task', bind=True)
def demo_task(self):
	with open('/data01/nocout/data_aggregation/demo_task.txt', 'a') as fd:
		fd.write('Task with id: %s executed at -- %s\n' % (self.request.id, datetime.now()))


if __name__ == '__main__':
	defaults = {
			'source_perf_table': 'performance_performanceservice',
			'destination_perf_table': 'performance_performanceservicehourly',
			'read_from': 'mysql',
			'time_frame': 'hourly',
			'hours': 1,
			'machine': 'ospf5',
			'all': False
		}
	main(**defaults)
	#print "Can't run the script in stand alone mode."
