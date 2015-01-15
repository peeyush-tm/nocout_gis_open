"""
Dashboard Utilities.
"""
import json
from multiprocessing import Process, Queue

from django.conf import settings
from django.db.models import Count
from datetime import datetime, timedelta

import logging
log = logging.getLogger(__name__)

def get_service_status_data(queue, machine_device_list, machine, model, service_name, data_source):
    """
    Consolidated Service Status Data from the Data base.

    :param machine:
    :param model:
    :param service_name:
    :param data_source:
    :param device_list:
    :param queue:
    :return:
    """
    required_severity = ['warning','critical']
    required_values = ['id',
                        'device_name',
                        'service_name',
                        'ip_address',
                        'data_source',
                        'severity',
                        'current_value',
                        'warning_threshold',
                        'critical_threshold',
                        'sys_timestamp',
                        'check_timestamp',
                        'age'
    ]
    service_status_data = model.objects.filter(
        device_name__in=machine_device_list,
        service_name__icontains = service_name,
        data_source = data_source#,
        # severity__in=required_severity
    ).using(machine).values(*required_values)

    if queue:
        try:
            queue.put(service_status_data)
        except Exception as e:
            log.exception(e.message)
    else:
        return service_status_data


def get_service_status_results(user_devices, model, service_name, data_source):

    unique_device_machine_list = {device.machine.name: True for device in user_devices}.keys()

    service_status_results = None

    machine_dict = {}
    #Creating the machine as a key and device_name as a list for that machine.
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device.device_name for device in user_devices if device.machine.name == machine]

    multi_proc = getattr(settings, 'MULTI_PROCESSING_ENABLED', False)

    service_status_results = []
    if multi_proc:
        queue = Queue()
        jobs = [
            Process(
                target=get_service_status_data,
                args=(queue, machine_device_list),
                kwargs=dict(machine=machine, model=model, service_name=service_name, data_source=data_source)
            ) for machine, machine_device_list in machine_dict.items()
        ]

        for job in jobs:
            job.start()
        for job in jobs:
            job.join()

        while True:
            if not queue.empty():
                if service_status_results:
                    service_status_results |= queue.get()
                else:
                    service_status_results = queue.get()
            else:
                break
    else:
        for machine, machine_device_list in machine_dict.items():
            if service_status_results:
                service_status_results |= get_service_status_data(False,
                                                                  machine_device_list,
                                                                  machine=machine,
                                                                  model=model,
                                                                  service_name=service_name,
                                                                  data_source=data_source
                )
            else:
                service_status_results = get_service_status_data(False,
                                                                  machine_device_list,
                                                                  machine=machine,
                                                                  model=model,
                                                                  service_name=service_name,
                                                                  data_source=data_source
                )

    return service_status_results


def get_dashboard_status_range_counter(dashboard_setting, service_status_results):
    range_counter = dict()
    for i in range(1, 11):
        range_counter.update({'range%d' %i: 0})
    range_counter.update({'unknown': 0})

    for result in service_status_results:
        is_unknown_range = True
        for i in range(1, 11):
            start_range = getattr(dashboard_setting, 'range%d_start' %i)
            end_range = getattr(dashboard_setting, 'range%d_end' %i)

            # dashboard type is numeric and start_range and end_range exists to compare result.
            if dashboard_setting.dashboard_type == 'INT' and start_range and end_range:
                try:
                    if float(start_range) <= float(result['current_value']) <= float(end_range):
                        range_counter['range%d' %i] += 1
                        is_unknown_range = False
                except ValueError as value_error:
                    range_counter['unknown'] += 1
                    is_unknown_range = False
                    break

            # dashboard type is string and start_range exists to compare result.
            elif dashboard_setting.dashboard_type == 'STR' and start_range:
                if result['current_value'].lower() in start_range.lower():
                    range_counter['range%d' %i] += 1
                    is_unknown_range = False
        if is_unknown_range:
            range_counter['unknown'] += 1

    return range_counter


def get_pie_chart_json_response_dict(dashboard_setting, data_source, range_counter):

    display_name = data_source.replace('_', ' ')

    chart_data = []
    colors = []
    for count in range(1, 11):
        start_range = getattr(dashboard_setting, 'range%d_start' %count)
        end_range = getattr(dashboard_setting, 'range%d_end' %count)
        color = getattr(dashboard_setting, 'range%d_color_hex_value' %count)
        if start_range or end_range:
            if len(str(start_range).strip()) or len(str(end_range).strip()):
                chart_data.append(['(%s, %s)' % (start_range, end_range), range_counter['range%d' %count]])
                if color:
                    colors.append(color)
                else:
                    colors.append("#000000")
    chart_data.append(['Unknown', range_counter['unknown']])
    colors.append("#d3d3d3")

    response_dict = {
        "message": "Device Performance Data Fetched Successfully To Plot Graphs.",
        "data": {
            "meta": {},
            "objects": {
                "plot_type": "charts",
                "display_name": display_name,
                "valuesuffix": "dB",
                "colors": colors,
                "chart_data": [{
                    "type": 'pie',
                    "name": display_name.upper(),
                    "data": chart_data
                }]
            }
        },
        "success": 1
    }
    return response_dict


#**************************** Sector Capacity *********************#
def get_dashboard_status_sector_range_counter(service_status_results):
    range_counter = {'Needs Augmentation': 0, 'Stop Provisioning': 0, 'Normal':0, 'Unknown':0}
    date_format = '%Y-%m-%d %H:%M:%S'
    # now = datetime.today() - timedelta(minutes=10)

    for result in service_status_results:
        age_str_since_the_epoch = datetime.fromtimestamp(float(result['age'])).strftime(date_format)
        sys_timestamp_str_since_the_epoch = datetime.fromtimestamp(float(result['sys_timestamp'])).strftime(date_format)
        age_time_since_the_epoch = datetime.strptime(age_str_since_the_epoch, date_format)
        sys_timestamp_str_since_the_epoch = datetime.strptime(sys_timestamp_str_since_the_epoch, date_format)
        result_status =  age_time_since_the_epoch - sys_timestamp_str_since_the_epoch
        if result['severity'] == 'warning' and result_status > timedelta(minutes=10):
            range_counter['Needs Augmentation'] += 1
        elif result['severity'] == 'critical' and result_status >= timedelta(minutes=10):
            range_counter['Stop Provisioning'] += 1
        elif result['severity'] == 'ok':
            range_counter['Normal'] += 1
        else:
            range_counter['Unknown'] += 1

    return range_counter


#**************************** Sales Opportunity *********************#
def get_topology_status_data(machine_device_list, machine, model, service_name, data_source):
    """
    Consolidated Topology Status Data from the Data base.

    :param machine:
    :param model:
    :param service_name:
    :param data_source:
    :param device_list:
    :return:
    """
    topology_status_data = model.objects.filter(
        device_name__in=machine_device_list,
        # service_name__icontains = service_name,
        # data_source = data_source,
        data_source = 'topology',
    ).using(machine)

    return topology_status_data


def get_topology_status_results(user_devices, model, service_name, data_source, user_sector):

    unique_device_machine_list = {device.machine.name: True for device in user_devices}.keys()

    machine_dict = {}
    #Creating the machine as a key and device_name as a list for that machine.
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device.device_name for device in user_devices if device.machine.name == machine]

    status_results = []
    topology_status_results = model.objects.none()
    for machine, machine_device_list in machine_dict.items():
        topology_status_results |= get_topology_status_data(machine_device_list, machine=machine, model=model, service_name=service_name, data_source=data_source)

    for sector in user_sector:
        ss_qs = topology_status_results.filter(sector_id=sector.sector_id).\
                        annotate(Count('connected_device_ip'))
        # current value define the total ss connected to the sector
        status_results.append({'sector_id': sector.id, 'current_value': ss_qs.count()})
    return status_results


def get_highchart_response(dictionary={}):
    if 'type' not in dictionary:
        return json.dumps({
            "message": "No Data To Display.",
            "success": 0
        })

    if dictionary['type'] == 'pie':
        chart_data = {
            'type': 'pie',
            'name': dictionary['name'],
            'title': dictionary['title'],
            'data': dictionary['chart_series'],
        }
    elif dictionary['type'] == 'gauge':
        chart_data = {
            "is_inverted": False,
            "name": dictionary['name'],
            "title": '',
            "data": [{
                "color": dictionary['color'],
                "name": dictionary['name'],
                "count": dictionary['count']
            }],
            "valuesuffix": "",
            "type": "gauge",
            "valuetext": ""
        }
    elif dictionary['type'] == 'areaspline':
        chart_data = {
            'type': 'areaspline',
            'title': dictionary['title'],
            'valuesuffix': dictionary['valuesuffix'],
            'data': dictionary['chart_series']
        }

    return json.dumps({
        "message": "Device Performance Data Fetched Successfully To Plot Graphs.",
        "data": {
            "meta": {
            },
            "objects": {
                "chart_data": [chart_data]
            }
        },
        "success": 1
    })
