"""
Dashboard Utilities.
"""
import copy
import json
from multiprocessing import Process, Queue

from django.conf import settings
from django.db.models import Count
from datetime import datetime, timedelta

from dashboard.models import DashboardSetting
from dashboard.config import dashboards

import logging
log = logging.getLogger(__name__)


def get_unused_dashboards(dashboard_setting_id=None):
    """
    """
    dashboard_settings = DashboardSetting.objects.all()
    if dashboard_setting_id:

        dashboard_settings = dashboard_settings.exclude(id=dashboard_setting_id)

    technologies = {
        'P2P': 2,
        'PMP': 4,
        'WiMAX': 3,
        'All': None,
    }

    types = {
        'numeric': 'INT',
        'string': 'String',
    }

    unused_dashboards = copy.copy(dashboards)

    for dashboard_setting in dashboard_settings:
        setting_technology = dashboard_setting.technology.id if dashboard_setting.technology else None
        for i, dashboard_conf in enumerate(unused_dashboards):
            if dashboard_conf['page_name'] == dashboard_setting.page_name and technologies[dashboard_conf['technology']] == setting_technology and dashboard_conf['is_bh'] == dashboard_setting.is_bh and dashboard_conf['dashboard_name'] == dashboard_setting.name and types[dashboard_conf['dashboard_type']] == dashboard_setting.dashboard_type:
                unused_dashboards.pop(i)
    return json.dumps(unused_dashboards)

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


def get_range_status(dashboard_setting, result):
    '''
    Method return the range name in which the result's current value falls.

    :param:
    dashboard_setting: dashboard_setting object.
    result: dictionary (must contain 'current_value' as key)

    return: dictionary containing 'range_count' as key and range as value.
                    i.e: { 'range_count': 'range_name' }
    '''
    range_count = 'unknown'
    for i in range(1, 11):
        # Get the start_range and end_range attribute of dashboard_setting.
        start_range = getattr(dashboard_setting, 'range%d_start' %i)
        end_range = getattr(dashboard_setting, 'range%d_end' %i)

        # dashboard type is numeric and start_range and end_range exists to compare result.
        if dashboard_setting.dashboard_type == 'INT' and start_range and end_range:
            try:
                if float(start_range) <= float(result['current_value']) <= float(end_range):
                    range_count = 'range%d' %i
            except ValueError as value_error:
                range_count = 'unknown'
                break
            except TypeError as type_error:
                pass

        # dashboard type is string and start_range exists to compare result.
        elif dashboard_setting.dashboard_type == 'STR' and start_range:
            if result['current_value'].lower() in start_range.lower():
                range_count = 'range%d' %i

    return {'range_count': range_count}


def get_dashboard_status_range_counter(dashboard_setting, service_status_results):
    '''
    Method return the count of ranges according to dashboard_setting.

    :param:
    dashboard_setting: dashboard_setting object.
    service_status_results: list of dictionary.

    return: dictionary
                    i.e: { 'unknown': 0, 'range1': 1, 'range2': 2,... }
    '''
    range_counter = dict()
    # initialize the ranges of range_counter to 0(zero)
    for i in range(1, 11):
        range_counter.update({'range%d' %i: 0})
    range_counter.update({'unknown': 0})

    range_status_dct = dict()
    # update the ranges of range_counter.
    for result in service_status_results:
        # Get the name of range in which result's current_value falls.
        range_status_dct = get_range_status(dashboard_setting, result)
        range_counter[range_status_dct['range_count']] += 1

    return range_counter


def get_pie_chart_json_response_dict(dashboard_setting, data_source, range_counter):
    '''
    Method return the chart data used for the dashboard.

    :param:
    dashboard_setting: dashboard_setting object.
    data_source: data source name.
    range_counter: dictionary containing range name as key and value.

    return: dictionary in specific format.
    '''
    display_name = data_source.replace('_', ' ')

    chart_data = []
    colors = []
    for count in range(1, 11):
        # get the start_range, end_range attribute of dashboard_setting.
        start_range = getattr(dashboard_setting, 'range%d_start' %count)
        end_range = getattr(dashboard_setting, 'range%d_end' %count)
        # get the color attribute of dashboard_setting.
        color = getattr(dashboard_setting, 'range%d_color_hex_value' %count)
        # creating list using (start_range, end_range) and range_counter value.
        if start_range or end_range:
            if len(str(start_range).strip()) or len(str(end_range).strip()):
                chart_data.append(['(%s, %s)' % (start_range, end_range), range_counter['range%d' %count]])
                # append color if exists else append default color.
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
    '''
    Method return the dictionay for the severity status.

    :param:
    service_status_results: list of dictionary.

    return: dictionary.
                    i.e: {  'Normal':0,
                            'Unknown':3,
                            'Stop Provisioning': 1,
                            'Needs Augmentation': 0,
                        }
    '''
    range_counter = {'Needs Augmentation': 0, 'Stop Provisioning': 0, 'Normal':0, 'Unknown':0}
    date_format = '%Y-%m-%d %H:%M:%S'
    # now = datetime.today() - timedelta(minutes=10)

    for result in service_status_results:
        # Convert the integer age and sys_timestamp into string as date_format.
        age_str_since_the_epoch = datetime.fromtimestamp(float(result['age'])).strftime(date_format)
        sys_timestamp_str_since_the_epoch = datetime.fromtimestamp(float(result['sys_timestamp'])).strftime(date_format)

        # get the age and sys_timestamp as datetime object.
        age_time_since_the_epoch = datetime.strptime(age_str_since_the_epoch, date_format)
        sys_timestamp_str_since_the_epoch = datetime.strptime(sys_timestamp_str_since_the_epoch, date_format)

        # update the range_counter values.
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
def get_topology_status_results(user_devices, model, service_name, data_source, user_sector):
    '''
    Method return the total ss connected to the sector.

    :param:
    user_devices: device list.
    model: model name.
    service_name: service name.
    data_source: data source name.
    user_sector: sector list.

    return: list of dictionary.
                    i.e: [
                        {'id': sector_id1, 'name': sector_name1, 'device_name':  device_name1, 'current_value': 1},
                        {'id': sector_id2, 'name': sector_name2, 'device_name':  device_name2, 'current_value': 2},
                        {'id': sector_id3, ...},
                        ]
    '''

    status_results = []

    topology_status_results = model.objects.filter(
                                    sector_id__in=user_sector.values_list('sector_id', flat=True),
                                    data_source='topology',
                                )

    # Count the total ss connected to the sector.
    for sector in user_sector:
        ss_qs = topology_status_results.filter(sector_id=sector.sector_id).\
                        annotate(Count('connected_device_ip'))
        # current value define the total ss connected to the sector.
        status_results.append({'id': sector.id, 'name': sector.name, 'device_name':  sector.sector_configured_on.device_name, 'current_value': ss_qs.count()})
    return status_results


#**************************** Highchart Response *********************#
def get_highchart_response(dictionary={}):
    '''
    Method return the chart data used for the dashboard.

    :param:
    dictionary: containing the attributes which vary according to chart type:
        - type: type of chart.
        - name: dashboard name.
        - title: title for chart.
        - chart_series: list of data.
        - color: list of color.
        - count: integer.
        - max: integer.
        - stops: list containing range

    return: dictionay in specific format.
    '''
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
        if 'colors' in dictionary:
            chart_data.update({'color': dictionary['colors']})
    elif dictionary['type'] == 'gauge':
        chart_data = {
            "is_inverted": False,
            "name": dictionary['name'],
            "title": '',
            "data": [{
                "color": dictionary['color'],
                "name": dictionary['name'],
                "count": dictionary['count'],
                "max": dictionary['max'],
                "stops": dictionary['stops'],
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
    elif dictionary['type'] == 'column':

        return json.dumps({
            "message": "Device Performance Data Fetched Successfully To Plot Graphs.",
            "data": {
                "meta": {
                },
                "objects": {
                    'type': 'column',
                    'valuesuffix': dictionary['valuesuffix'],
                    "chart_data": dictionary['chart_series'],
                    'name': dictionary['name'],
                    'valuetext' : dictionary['valuetext']
                }
            },
            "success": 1
        })


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


def get_guege_chart_max_n_stops(dashboard_setting):
    '''
    Method retunrs the max_range value and stops range calculated from the dashboard_setting:

    dashboard_setting: dashboard_setting object.

    return: tuple of (integer, list of list)
                    i.e: (7, [  [2, u'rgb(76, 17, 48)'],
                                [4, u'rgb(0, 255, 255)'],
                                [7, u'rgb(204, 0, 0)'],...
                            ]
                        )
    '''
    max_range = 0
    stops = []
    for count in range(1, 11):
        # Get the end_range and color attribute of dashboard_setting.
        end_range = getattr(dashboard_setting, 'range%d_end' %count)
        color = getattr(dashboard_setting, 'range%d_color_hex_value' %count)

        # update max_range and stops.
        if end_range and color:
            end_range = int(end_range)
            stops.append([end_range, color])
            if end_range > max_range:
                max_range = end_range
    return max_range, stops
