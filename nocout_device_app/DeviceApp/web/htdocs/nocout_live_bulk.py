'''
nocout_live_bulk.py
===================

Script that fetches current data for a list of services running
on a set of devices
'''
from wato import *
from pprint import pformat
import os
from multiprocessing import Process, Queue
from ast import literal_eval
#import Queue
from nocout_live import get_current_value, nocout_log
from itertools import groupby
from operator import itemgetter
from nocout import get_parent

logger = nocout_log()

def main():
    """
    Entry point for all the functions

    Returns:
        {
	 "success": 1,
	 "message": "Data fetched successfully",
	 "error_message": None,
	 "value": [] # The current values for the desired service data sources
	}
    """
    response = {
        "success": 1,
        "message": "Data fetched successfully",
        "error_message": None,
        "value": []
    }
    action = ''
    action = html.var('mode')
    if action == 'live':
        response['value'] = poll_device()
    else:
        response.update({
            "message": "No data",
            "error_message": "No action defined for this case"
        })

    html.write(pformat(response))


def poll_device():
	response = []
	wimax_service_list = ['wimax_dl_cinr','wimax_ul_cinr','wimax_dl_rssi','wimax_ul_rssi','wimax_ul_intrf','wimax_dl_intrf',
	'wimax_modulation_dl_fec','wimax_modulation_ul_fec']
	logger.info('[Polling Iteration Start]')
	device_list = literal_eval(html.var('device_list'))
	service_list = literal_eval(html.var('service_list'))
	logger.info('device_list: ' + pformat(device_list))
	logger.info('service_list: ' + pformat(service_list))
	parent_list = []
	if service_list[0] in wimax_service_list:
		for d in device_list:
			__, parent_device = get_parent(host=d, db=False)
			parent_list.append(parent_device)
		logger.info('parent_list' + pformat(parent_list))
		ss_bs_list = zip(device_list,parent_list)
		ss_bs_list.sort(key = itemgetter(1))
		groups = groupby(ss_bs_list, itemgetter(1))
		device_list =[[item[0] for item in data] for (key, data) in groups]
		logger.info('device_list' + pformat(device_list))
  
	logger.info('device_list : %s and service_list : %s' % (device_list, service_list))
	# If in case no `ds` supplied in req obj, [''] would be supplied as default
	try:
		data_source_list = literal_eval(html.var('ds'))
	except Exception:
		data_source_list = ['']
		#logger.error('No ds provided in request object', exc_info=True)
	if not data_source_list:
		data_source_list = ['']
	#logger.debug('data_source_list : %s' % data_source_list)

	#current_values = get_current_value(device, service, data_source_list)

		#t = threading.Thread(
		#		target=get_current_value,
		#		args=(q,),
		#		kwargs=
		#		{
		#			'device': device,
		#			'service_list': service_list,
		#			'data_source_list': data_source_list
		#			}
		#		)
		###t.daemon =True
		#t.start()

	q = Queue()
	jobs = [
			Process(
				target=get_current_value,
				args=(q,),
				kwargs=
				{
					'device': device,
					'service_list': service_list,
					'data_source_list': data_source_list
					}
				) for device in device_list
			]
	for j in jobs:
	        j.start()
	for k in jobs:
	        k.join()

	##logger.debug('Queue ' + pformat(q.qsize()))
	while True:
		if not q.empty():
			response.append(q.get())
		else:
			break
	logger.info('[Polling Iteration End]')

	return response


def poll_processes():
	logger.debug('Parent Process ID: ' + pformat(os.getppid()))
	logger.debug('Process ID: ' + pformat(os.getpid()))

