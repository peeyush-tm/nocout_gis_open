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
from nocout_live import get_current_value
from nocout_logger import nocout_log


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
	try:
		logger.info('[Polling Iteration Start]')
		device_list = literal_eval(html.var('device_list'))
		service_list = literal_eval(html.var('service_list'))
		bs_name_ss_mac_mapping = literal_eval(html.var('bs_name_ss_mac_mapping'))
		ss_name_mac_mapping = literal_eval(html.var('ss_name_mac_mapping'))
	except Exception as e:
		logger.info('excep: ' + pformat(e))
	logger.info('device_list: ' + pformat(device_list))
	logger.info('service_list: ' + pformat(service_list))
	try:
		data_source_list = literal_eval(html.var('ds'))
	except Exception:
		data_source_list = ['']
		#logger.error('No ds provided in request object', exc_info=True)
	if not data_source_list:
		data_source_list = ['']

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
					'data_source_list': data_source_list,
					'bs_name_ss_mac_mapping': bs_name_ss_mac_mapping,
					'ss_name_mac_mapping': ss_name_mac_mapping
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

