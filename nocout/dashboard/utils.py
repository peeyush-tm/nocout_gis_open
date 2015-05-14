"""
Dashboard Utilities.
"""
import copy
import json
from multiprocessing import Process, Queue

from django.conf import settings
from django.db.models import Count
from datetime import datetime, timedelta
from django.utils.dateformat import format

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
    if data_source.strip().lower() in ['availability']:
        required_values = [
            'id',
            'device_name',
            'service_name',
            'ip_address',
            'data_source',
            'severity',
            'current_value',
            'warning_threshold',
            'critical_threshold',
            'sys_timestamp',
            'check_timestamp'
        ]

    service_status_data = model.objects.filter(
        device_name__in=machine_device_list,
        service_name__icontains=service_name,
        data_source=data_source
    ).using(machine).values(*required_values)

    if data_source.strip().lower() in ['availability']:
        # availablity is a daily value
        # inserted once a day
        # as a new row
        # so to calculate this we would require
        now = datetime.now()
        today = datetime(now.year, now.month, now.day, 0, 0)
        yesterday = float(format(today + timedelta(days=-1), 'U'))
        today = float(format(today, 'U'))

        service_status_data = service_status_data.filter(
            sys_timestamp__lte=today,
            sys_timestamp__gte=yesterday,
        )

    if queue:
        try:
            queue.put(service_status_data)
        except Exception as e:
            log.exception(e.message)
    else:
        return service_status_data

# Below class is referenced from Link - https://djangosnippets.org/snippets/1253/
class MultiQuerySet(object):
    def __init__(self, *args, **kwargs):
        self.querysets = args
        self._count = None
    
    def _clone(self):
        querysets = [qs._clone() for qs in self.querysets]
        return MultiQuerySet(*querysets)
    
    def __repr__(self):
        return repr(list(self.querysets))
                
    def count(self):
        if not self._count:
            self._count = sum([qs.count() for qs in self.querysets])
        return self._count
    
    def __len__(self):
        return self.count()
    
    def __iter__(self):
        for qs in self.querysets:
            for item in qs.all():
                yield item
        
    def __getitem__(self, item):
        indices = (offset, stop, step) = item.indices(self.count())
        items = []
        total_len = stop - offset
        for qs in self.querysets:
            if len(qs) < offset:
                offset -= len(qs)
            else:
                items += list(qs[offset:stop])
                if len(items) >= total_len:
                    return items
                else:
                    offset = 0
                    stop = total_len - len(items)
                    continue

def get_service_status_results(user_devices, model, service_name, data_source):

    unique_device_machine_list = {device.machine.name: True for device in user_devices}.keys()

    service_status_results = None

    machine_dict = {}
    #Creating the machine as a key and device_name as a list for that machine.
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device.device_name for device in user_devices if device.machine.name == machine]

    multi_proc = getattr(settings, 'MULTI_PROCESSING_ENABLED', False)

    service_status_results = []
    multi_qyery_list = []
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
            service_status_results_temp = get_service_status_data(False,
                                                              machine_device_list,
                                                              machine=machine,
                                                              model=model,
                                                              service_name=service_name,
                                                              data_source=data_source
                                                            )
            multi_qyery_list.append(service_status_results_temp)
        
        service_status_results = MultiQuerySet(*multi_qyery_list)
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
            string_compare = lambda x: ''.join(e for e in x.lower() if e.isalnum())
            # if result['current_value'].lower() in start_range.lower():
            string_get = string_compare(result['current_value'])
            start_range_alnum = string_compare(start_range)
            if string_get.lower() == start_range_alnum.lower():
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
        ds_name_list = [
            'latency-network',
            'packetloss-network',
            'down-network',
            'temperature',
            'latency-WiMAX',
            'packetloss-WiMAX',
            'down-WiMAX',
            'latency-PMP',
            'packetloss-PMP',
            'down-PMP'
        ]
        if dashboard_setting.name in ds_name_list:
            range_counter[range_status_dct['range_count']] = result['current_value']
        else:     
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


# **************************** Sales Opportunity **********************#

def get_total_circuits_per_sector(model, user_sector):
    '''
    Method return the total Circuits connected to the sector.

    :param:
    model: model name.
    user_sector: sector list.

    return: list of dictionary.
                    i.e: [
                        {'id': sector_id1, 'name': sector_name1, 'device_name':  device_name1, 'organization': organization, 'current_value': 1},
                        {'id': sector_id2, 'name': sector_name2, 'device_name':  device_name2, 'organization': organization,'current_value': 2},
                        {'id': sector_id3, ...},
                        ]
    '''
    status_results = []
    topology_status_results = model.objects.filter(sector__in=user_sector.values_list('id', flat=True))

    for sector in user_sector:
        circuit_qs = topology_status_results.filter(sector=sector.id).count()
        status_results.append({'id': sector.id,
                               'name':sector.name,
                               'device_name': sector.sector_configured_on.device_name,
                               'organization': sector.organization,
                               'current_value': circuit_qs
                            })

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
        if dictionary['title'] != 'MFR Cause Code':
            timestamp = dictionary['processed_for_key']
        chart_data = {
            'type': 'pie',
            'name': dictionary['name'],
            'title': dictionary['title'],
            'data': dictionary['chart_series'],
        }
        if 'colors' in dictionary:
            chart_data.update({'color': dictionary['colors']})
        if dictionary['title'] != 'MFR Cause Code':    
            return json.dumps({
                "message": "Device Performance Data Fetched Successfully To Plot Graphs.",
                "data": {
                    "meta": {
                },
                    "objects": {
                        "timestamp" : timestamp,
                        "chart_data": [chart_data]
                    }
                },
            "success": 1
            })    
    elif dictionary['type'] == 'gauge':
        timestamp = dictionary['processed_for_key']
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
        return json.dumps({
            "message": "Device Performance Data Fetched Successfully To Plot Graphs.",
            "data": {
                "meta": {
            },
                "objects": {
                    "timestamp" : timestamp,
                    "chart_data": [chart_data]
                }
            },
        "success": 1
        })
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
        end_range = getattr(dashboard_setting, 'range%d_end' %count)
        if end_range:
            end_range = float(end_range)
            if end_range >= max_range:
                max_range = end_range
    for count in range(1, 11):
        # Get the end_range and color attribute of dashboard_setting.
        end_range = getattr(dashboard_setting, 'range%d_end' %count)
        color = getattr(dashboard_setting, 'range%d_color_hex_value' %count)

        # update max_range and stops.
        if end_range and color:
            stops.append([float(end_range)/float(max_range), color])

    return max_range, stops
