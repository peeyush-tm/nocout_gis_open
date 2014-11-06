"""
Dashboard Utilities.
"""
from multiprocessing import Process, Queue

from django.conf import settings


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
    service_status_data = model.objects.filter(
        device_name__in=machine_device_list,
        service_name__icontains = service_name,
        data_source = data_source,
    ).using(machine).values('id', 'device_name', 'service_name', 'ip_address', 'data_source', 'severity', 'current_value', 'warning_threshold', 'critical_threshold', 'sys_timestamp', 'check_timestamp')

    if queue:
        try:
            queue.put(service_status_data)
        except Exception as e:
            log.exception(e.message)
    else:
        return service_status_data


def get_service_status_results(user_devices, model, service_name, data_source):

    unique_device_machine_list = {device.machine.name: True for device in user_devices}.keys()

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
                service_status_results += queue.get()
            else:
                break
    else:
        for machine, machine_device_list in machine_dict.items():
            service_status_results += get_service_status_data(False, machine_device_list, machine=machine, model=model, service_name=service_name, data_source=data_source)

    return service_status_results


def get_dashboard_status_range_counter(dashboard_setting, service_status_results):
    range_counter = dict()
    for i in range(1, 11):
        range_counter.update({'range%d' %i: 0})

    for result in service_status_results:
        for i in range(1, 11):
            start_range = getattr(dashboard_setting, 'range%d_start' %i)
            end_range = getattr(dashboard_setting, 'range%d_end' %i)

            # dashboard type is numeric and start_range and end_range exists to compare result.
            if dashboard_setting.dashboard_type == 'INT' and start_range and end_range:
                if float(start_range) <= float(result['current_value']) <= float(end_range):
                    range_counter['range%d' %i] += 1

            # dashboard type is string and start_range exists to compare result.
            elif dashboard_setting.dashboard_type == 'STR' and start_range:
                if result['current_value'].lower() in start_range.lower():
                    range_counter['range%d' %i] += 1

    return range_counter


def get_pie_chart_json_response_dict(dashboard_setting, data_source, range_counter):

    display_name = data_source.replace('_', ' ')

    chart_data = []
    colors = []
    for count in range(1, 11):
        start_range = getattr(dashboard_setting, 'range%d_start' %count)
        end_range = getattr(dashboard_setting, 'range%d_end' %count)
        color = getattr(dashboard_setting, 'range%d_color_hex_value' %count)

        chart_data.append(['range%d (%s - %s)' % (count, start_range, end_range), range_counter['range%d' %count]])
        if color:
            colors.append(color)
        else:
            colors.append("#000000")

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
