"""
client.py
==========
Sends aggregation tasks into celery queues for
asynchronous execution
"""


from datetime import datetime, timedelta

from celery import chord, chain, group
from celery.utils.log import get_task_logger

import db_tasks
import entry
import tasks

logger = get_task_logger(__name__)
info, warning, critical = (logger.info, logger.warning,
        logger.critical)

app = entry.app


@app.task(name='prepare-main', ignore_result=True)
def prepare_data(**extra_opts):
    """
    Breaks hosts into batches and sends tasks for each batch
    """
     
    data_values = []
    end_time = datetime.now()
    # adding buffer window for 5 minutes live data [for edge cases]
    #end_time = datetime(2015, 9, 4, 16, 30)
    end_time = end_time - timedelta(minutes=4)
    start_time = end_time - timedelta(hours=extra_opts.get('hours'))
    #start_time = start_time - timedelta(minutes=1)
    print start_time, end_time
    start_time, end_time = int(start_time.strftime('%s')), int(end_time.strftime('%s'))
    extra_opts.update({'start_time': start_time,
	    'end_time': end_time})
#    result = group(
#		chain(
#			db_tasks.read_data.s(
#				map(str, list(device_gen_obj)), 
#				extra_opts.get('source_perf_table'), 
#				start_time, 
#				end_time,
#				machine=str(extra_opts.get('machine'))
#				),
#			tasks.quantify_perf_data.s(
#				time_frame=extra_opts.get('time_frame'),
#				destination_perf_table=extra_opts.get('destination_perf_table')
#				)
#			)
#		for device_gen_obj in db_tasks.get_active_inventory_devices(
#				machine=str(extra_opts.get('machine')),
#				all=extra_opts.get('all'))
#	).apply_async()
    devices = list(db_tasks.get_active_inventory_devices(
	    machine=str(extra_opts.get('machine')), 
	    all=extra_opts.get('all')))
    # prepare batches, a list of list of devices
    #devices = ['11473']
    devices_in_batches = get_batches(devices)
    #devices_in_batches = devices
    if devices_in_batches:
	    dispatch_batches.delay(None, devices_in_batches, **extra_opts)


@app.task(name='task-caller')
def task_caller(device_set, **extra_opts):
	""" Calls the actual aggregation tasks using chain"""
	return chain(
			db_tasks.read_data.s(
				map(str, device_set),
				extra_opts.get('source_perf_table'),
				extra_opts.get('start_time'),
				extra_opts.get('end_time'),
				machine=str(extra_opts.get('machine'))
				),
			tasks.quantify_perf_data.s(
				time_frame=extra_opts.get('time_frame'),
				destination_perf_table=extra_opts.get(
					'destination_perf_table')
				)
			).apply()


@app.task(name='dispatch-batches')
def dispatch_batches(results, batches, **extra_opts):
	""" Process the tasks into one batch at a time.
	Uses chord to defer remaing task batches"""
	#warning('dispatch-batches called')
	# Batch contains list of devices to be processed at one time
	batch = batches.pop(0)
	tasks = [task_caller.s(device_set, **extra_opts) for device_set in batch]

	if batches:
		# delay the execution of remaining batches using chord
		callback = dispatch_batches.s(batches, **extra_opts)
		return chord(tasks)(callback)
	else:
		return group(tasks).apply_async()


@app.task(name='get-batches')
def get_batches(devices):
	""" Prepares a list of list of devices"""
	t_size = getattr(app.conf, 'BATCH_SIZE', 10)
	batches = []
	while devices:
		t = min(t_size, len(devices))
		batches.append(devices[:t])
		devices = devices[t:]
	return batches


@app.task(name='aggregation-main', ignore_result=True)
def main(**extra_opts):
        prepare_data.s(**extra_opts).apply_async()


if __name__ == '__main__':
	defaults = {
			'source_perf_table': 'performance_utilization',
			'destination_perf_table': 'performance_utilizationbihourly',
			'read_from': 'mysql',
			'time_frame': 'half_hourly',
			'hours': 0.5,
			'machine': 'pub',
			'all': False
		}
	main(**defaults)
