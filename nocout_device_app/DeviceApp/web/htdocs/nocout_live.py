"""
nocout_live.py
==============

Script to handle on-demand live polling for a particular service data source
"""

from wato import *
from pprint import pformat
import subprocess
import re
from ast import literal_eval


def main():
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
    device = html.var('device')
    service = html.var('service')
    try:
        data_source_list = literal_eval(html.var('ds'))
    except Exception:
        data_source_list = ['']
    if not data_source_list:
        data_source_list = ['']
    for ds in data_source_list:
        current_values.extend(get_current_value(device, service, ds))

    return current_values


def get_current_value(device, service=None, ds=None):
    response = []
    site_name = get_site_name()
    cmd = '/opt/omd/sites/%s/bin/cmk -nvp %s' % (site_name, device)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    check_output, error = p.communicate()
    if check_output:
        reg_exp1 = re.compile(r'(?<=\()[^)]*(?=\)$)', re.MULTILINE)
        reg_exp2 = re.compile(r'^\S+', re.MULTILINE)
        # Parse perfdata for all services running on that device
        ds_current_states = re.findall(reg_exp1, check_output)
        # Get all the service names, currently running
        current_services = re.findall(reg_exp2, check_output)[:-1]

        service_ds_pairs = zip(current_services, ds_current_states)
        desired_service_ds_pair = filter(lambda x: service in x[0], service_ds_pairs)
        if desired_service_ds_pair:
            ds_values = desired_service_ds_pair[0][1].split(' ')
            desired_ds = filter(lambda x: ds in x, ds_values)
            response = map(lambda x: x.split('=')[1].split(';')[0], desired_ds)

    return response


def get_site_name(site=None):
    site = defaults.omd_site

    return site