"""
nocout_live.py
==============

Script to handle on-demand live polling for a particular service data source
"""

from wato import *
from pprint import pformat
import subprocess
import re
import os
from ast import literal_eval
import logging


def nocout_log():
    """
    Handles logging functinality for device app

    Args:
        
    Kwargs:

    Returns:
        logger object, which logs the activities to a log file
    """
    logger=logging.getLogger('nocout_da')
    fd = os.open('/opt/omd/sites/%s/nocout/nocout_live.log' % defaults.omd_site, os.O_RDWR | os.O_CREAT)
    if not len(logger.handlers):
        logger.setLevel(logging.DEBUG)
        handler=logging.FileHandler('/opt/omd/sites/%s/nocout/nocout_live.log' % defaults.omd_site)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    os.close(fd)

    return logger


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
    current_values = []
    logger.info('[Polling Iteration Start]')
    device = html.var('device')
    service = html.var('service')
    logger.info('device : %s and service : %s' % (device, service))
    # If in case no `ds` supplied in req obj, [''] would be supplied as default
    try:
        data_source_list = literal_eval(html.var('ds'))
    except Exception:
        data_source_list = ['']
        logger.error('No ds provided in request object', exc_info=True)
    if not data_source_list:
        data_source_list = ['']
    logger.debug('data_source_list : %s' % data_source_list)
    
    current_values = get_current_value(device, service, data_source_list)

    return current_values


def get_current_value(device, service=None, data_source_list=None):
    response = []
    # Teramatrix poller on which this device is being monitored
    site_name = get_site_name()
    cmd = '/opt/omd/sites/%s/bin/cmk -nvp %s' % (site_name, device)
    # Fork a subprocess
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    check_output, error = p.communicate()
    if check_output:
        reg_exp1 = re.compile(r'(?<=\()[^)]*(?=\)$)', re.MULTILINE)
        reg_exp2 = re.compile(r'^ *\S+', re.MULTILINE)
        # Parse perfdata for all services running on that device
        ds_current_states = re.findall(reg_exp1, check_output)
        logger.info('ds_current_states : %s' % ds_current_states)
        # Get all the service names, currently running
	current_services = map(lambda x: x.strip(), re.findall(reg_exp2, check_output)[:-1])
        logger.info('current_services : %s' % current_services)

        service_ds_pairs = zip(current_services, ds_current_states)
        desired_service_ds_pair = filter(lambda x: service in x[0], service_ds_pairs)
        logger.debug('desired_service_ds_pair : %s' % desired_service_ds_pair)
        if desired_service_ds_pair:
            ds_values = desired_service_ds_pair[0][1].split(' ')
            logger.info('ds_values : %s' % ds_values)
            for ds in data_source_list:
		# Parse the output to get current value for that data source
                desired_ds = filter(lambda x: ds in x.split('=')[0], ds_values)
                logger.debug('desired_ds : %s' % desired_ds)
                response.extend(map(lambda x: x.split('=')[1].split(';')[0], desired_ds))
            logger.info('response : %s' % response)
            logger.info('[Polling Iteration End]')

    return response


def get_site_name(site=None):
    site = defaults.omd_site

    return site
