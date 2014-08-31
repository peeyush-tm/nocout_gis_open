import threading
from wato import *
from pprint import pformat
from multiprocessing import Process, Queue
from ast import literal_eval
#import Queue
import os
import time
from nocout_live import get_current_value, nocout_log


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
	current_values = []
	ds_value = None
	logger.info('[Polling Iteration Start]')
	device_list = literal_eval(html.var('device_list'))
	service_list = literal_eval(html.var('service_list'))
	logger.info('device_list : %s and service_list : %s' % (device_list, service_list))
	# If in case no `ds` supplied in req obj, [''] would be supplied as default
	try:
		data_source_list = literal_eval(html.var('ds'))
	except Exception:
		data_source_list = ['']
		logger.error('No ds provided in request object', exc_info=True)
	if not data_source_list:
		data_source_list = ['']
	logger.debug('data_source_list : %s' % data_source_list)

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
		#ds_value = current_values
		#current_values = []
	        #logger.debug('Queue ' + pformat(q.qsize()))
	#response.append(q.get())
	#time.sleep(4)
	##logger.debug('Queue ' + pformat(q.qsize()))
	while True:
		if not q.empty():
			response.append(q.get())
		else:
			break
	
	##q.join()
	#for device in device_list:
	#	response = get_current_value(response, device=device, service_list=service_list, data_source_list=data_source_list)


	return response


