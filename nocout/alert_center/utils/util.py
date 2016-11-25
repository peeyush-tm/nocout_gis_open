# -*- encoding: utf-8; py-indent-offset: 4 -*-

import datetime
# Import nocout utils gateway(NocoutUtilsGateway) class
from nocout.utils.util import NocoutUtilsGateway

# Import performance utils gateway class
from performance.utils.util import PerformanceUtilsGateway

# Import service utils gateway class
from service.utils.util import ServiceUtilsGateway

from nocout.settings import DATE_TIME_FORMAT, CACHE_TIME

# Create instance of 'ServiceUtilsGateway' class
service_utils = ServiceUtilsGateway()

SERVICE_DATA_SOURCE = service_utils.service_data_sources()

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()

import logging
logger = logging.getLogger(__name__)


class AlertCenterUtilsGateway:
    """
    This class works as gateway between alert center utils & other apps
    """
    def prepare_query(
        self, 
        table_name=None, 
        devices=None, 
        data_sources=["pl", "rta"], 
        columns=None, 
        condition=None, 
        offset=None, 
        limit=None
    ):
        """

        :param limit:
        :param offset:
        :param condition:
        :param columns:
        :param data_sources:
        :param devices:
        :param table_name:
        """
        param1 = prepare_query(
            table_name=table_name, 
            devices=devices, 
            data_sources=data_sources, 
            columns=columns, 
            condition=condition, 
            offset=offset, 
            limit=limit
        )

        return param1

    def severity_level_check(self, list_to_check):
        """

        :param list_to_check:
        """
        param1 = severity_level_check(list_to_check)

        return param1

    def raw_prepare_result(
        self, 
        performance_data, 
        machine, 
        table_name=None, 
        devices=None, 
        data_sources=["pl", "rta"], 
        columns=None, 
        condition=None, 
        offset=0, 
        limit=5000
    ):
        """

        :param limit:
        :param offset:
        :param condition:
        :param columns:
        :param data_sources:
        :param devices:
        :param table_name:
        :param machine:
        :param performance_data:
        """
        param1 = raw_prepare_result(
            performance_data, 
            machine, 
            table_name=table_name, 
            devices=devices, 
            data_sources=data_sources, 
            columns=columns, 
            condition=condition, 
            offset=offset, 
            limit=limit
        )

        return param1

    def indexed_alert_results(self, performance_data):
        """

        :param performance_data:
        """
        param1 = indexed_alert_results(performance_data)

        return param1

    def prepare_raw_alert_results(self, performance_data=None):
        """

        :param performance_data:
        """
        param1 = prepare_raw_alert_results(performance_data=performance_data)

        return param1

    def map_results(self, perf_result, qs):
        """

        :param qs:
        :param perf_result:
        """
        param1 = map_results(perf_result, qs)

        return param1

    def ping_service_query(self, device_name, start_date, end_date):
        """

        :param end_date:
        :param start_date:
        :param device_name:
        """
        param1 = ping_service_query(device_name, start_date, end_date)

        return param1

    def common_prepare_results(self, dct):
        """

        :param dct:
        """
        param1 = common_prepare_results(dct)

        return param1

    def common_get_severity_icon(self, severity):

        param1 = common_get_severity_icon(severity)

        return param1

    def polled_results(
        self,
        multi_proc=False,
        machine_dict=None,
        table_name=None,
        data_sources=None,
        columns=None,
        condition=None
    ):
        """
        """
        param1 = polled_results(
            multi_proc=multi_proc,
            machine_dict=machine_dict,
            table_name=table_name,
            data_sources=data_sources,
            columns=columns,
            condition=condition
        )

        return param1

    def get_multiprocessing_performance_data(self, q, machine_device_list, machine, data_sources, columns, condition, table_name):
        """
        """
        param1 = get_multiprocessing_performance_data(
            q,
            machine_device_list,
            machine,
            data_sources,
            columns,
            condition,
            table_name
        )

        return param1

    def get_performance_data(self, machine_device_list, machine, data_sources, columns, condition, table_name):
        """
        """
        param1 = get_performance_data(
            machine_device_list,
            machine,
            data_sources,
            columns,
            condition,
            table_name
        )

        return param1

# misc utility functions
def prepare_query(
    table_name=None, 
    devices=None, 
    data_sources=None,
    columns=None, 
    condition=None, 
    offset=None, 
    limit=None
):
    """

    :param table_name:
    :param devices:
    :param data_sources:
    :param columns:
    :param condition:
    :param offset:
    :param limit:
    :return:
    """
    in_string = lambda x: "'" + str(x) + "'"
    # col_string = lambda x,y: ("%s`" + str(x) + "`") %(y)
    query = None

    if not columns:
        return None

    if table_name and devices:
        query = """
        SELECT {0} FROM {1} AS original_table
        WHERE (
            original_table.device_name IN ( {2} )
            {3}
            {4}
        )
        ORDER BY original_table.id DESC
        """.format(
            ','.join(["original_table.`" + col_name + "`" for col_name in columns]),
            table_name,
            (",".join(map(in_string, devices))),
            "AND original_table.data_source in ( {0} )".format(
                ','.join(map(in_string, data_sources))
            ) if data_sources else "",
            condition.format("original_table") if condition else "",
        )

        if limit is not None and offset is not None:
            query += "LIMIT {0}, {1}".format(offset, limit)

    return query


def severity_level_check(list_to_check):
    """


    :param list_to_check:
    :return:
    """
    severity_check = ['DOWN', 'CRITICAL', 'WARNING', "WARN", "CRIT"]
    for item in list_to_check:
        for severity in severity_check:
            if severity.lower() in item.lower():
                return True


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_ALERT', 300))
def raw_prepare_result(
    performance_data, 
    machine, 
    table_name=None, 
    devices=None, 
    data_sources=["pl", "rta"], 
    columns=None, 
    condition=None, 
    offset=0, 
    limit=5000
):
    """

    :param performance_data:
    :param machine:
    :param table_name:
    :param devices:
    :param data_sources:
    :param columns:
    :param condition:
    :param offset:
    :param limit:
    :return:
    """
    query = prepare_query(
        table_name=table_name,
        devices=devices,
        data_sources=data_sources,
        columns=columns,
        condition=condition,
        offset=offset,
        limit=None
    )

    if query:
        performance_data += nocout_utils.fetch_raw_result(query, machine)
    else:
        return []

    return performance_data


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_ALERT', 300))
def indexed_alert_results(performance_data):
    """

    :param performance_data:
    :return:
    """

    indexed_raw_results = {}

    for data in performance_data:
        # this would be a unique combination
        if data['data_source'] and data['device_name'] and data['service_name']:
            defined_index = data['device_name'], data['service_name'], data['data_source']
            if defined_index not in indexed_raw_results:
                indexed_raw_results[defined_index] = None
            indexed_raw_results[defined_index] = data

    return indexed_raw_results


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_ALERT', 300))
def prepare_raw_alert_results(performance_data=None):
    """
    prepare GIS result using raw query

    :param performance_data:
    :return:
    """

    indexed_alert_data = indexed_alert_results(performance_data)

    device_list = list()

    for device_alert in indexed_alert_data:

        device_name, service_name, data_source = device_alert

        data = indexed_alert_data[device_alert]

        if severity_level_check(list_to_check=[data['severity']]):

            sds_name = data_source.strip().lower()

            if sds_name not in ['pl', 'rta']:
                sds_name = service_name.strip().lower() + "_" + data_source.strip().lower()

            try:
                sds_name = SERVICE_DATA_SOURCE[sds_name]['display_name']
            except:
                sds_name = " ".join(map(lambda a: a.title(), data_source.split("_")))

            device_events = {}
            device_events.update({
                'device_name': device_name,
                'severity': data['severity'],
                'ip_address': data["ip_address"],
                'data_source_key': data_source,
                'data_source_name': sds_name,
                'current_value': data["current_value"],
                'max_value': data["max_value"],
                'min_value': data["min_value"],
                'warning_threshold': data["warning_threshold"],
                'machine_name': data.get('machine_name'),
                # 'sys_timestamp': datetime.datetime.fromtimestamp(
                #     float(data["sys_timestamp"])).strftime(DATE_TIME_FORMAT),
                # 'age': datetime.datetime.fromtimestamp(
                #     float(data["age"])
                # ).strftime(DATE_TIME_FORMAT) if data["age"] else "",
                'sys_timestamp': float(data["sys_timestamp"]) if data["sys_timestamp"] else "",
                'age': float(data["age"]) if data["age"] else "",
                'description': '',
                'refer': data["refer"] if ('refer' in data and data['refer']) else ''
            })

            device_list.append(device_events)

    return device_list


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_ALERT', 300))
def map_results(perf_result, qs):
    """

    :param perf_result:
    :param qs:
    :return:
    """
    result_qs = []

    # Create instance of 'PerformanceUtilsGateway' class
    perf_utils = PerformanceUtilsGateway()

    # Call 'pre_map_indexing' method of 'PerformanceUtilsGateway' class
    # indexed_qs = perf_utils.pre_map_indexing(index_dict=qs)
    indexed_perf = perf_utils.pre_map_indexing(index_dict=perf_result)
    
    for device in indexed_perf:
        for perf_res in indexed_perf[device]:
            result_qs.append(perf_res)
    return result_qs


def ping_service_query(device_name, start_date, end_date):
    """

    :param end_date:
    :param start_date:
    :param device_name:
    :return:
    """
    query = " " \
            " SELECT " \
            " original_table.`device_name`," \
            " original_table.`ip_address`," \
            " original_table.`service_name`," \
            " original_table.`severity`," \
            " original_table.`current_value` AS latency," \
            " `derived_table`.`current_value` AS packet_loss, " \
            " `original_table`.`sys_timestamp`," \
            " original_table.`description` " \
            " FROM `performance_eventnetwork` AS original_table " \
            " INNER JOIN (`performance_eventnetwork` AS derived_table) " \
            " ON( " \
            "    original_table.`data_source` <> derived_table.`data_source` " \
            "    AND " \
            "   original_table.`sys_timestamp` = derived_table.`sys_timestamp` " \
            "    AND " \
            "    original_table.`device_name` = derived_table.`device_name` " \
            " ) " \
            " WHERE( " \
            "    original_table.`device_name`= '{0}' " \
            "    AND " \
            "    original_table.`sys_timestamp` BETWEEN {1} AND {2} " \
            " ) " \
            " GROUP BY original_table.`sys_timestamp` " \
            " ORDER BY original_table.`sys_timestamp` DESC ".format(device_name, start_date, end_date)
    return query


def common_prepare_results(dct):
    """
    Common function to prepare result on query set
    :param dct:
    :params qs:
    :return qs:
    """

    current_value = dct['current_value']
    try:
        current_value = float(current_value)
    except Exception, e:
        pass

    if dct['severity'].strip().upper() == 'DOWN' \
            or "CRITICAL" in dct['description'].strip().upper() \
            or dct['severity'].strip().upper() == 'CRITICAL':
        dct[
            'severity'
        ] = '<i class="fa fa-circle red-dot" value="1" title="Critical"><span style="display:none">DOWN</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-danger">%s</span>' % (dct['description'])

    elif dct['severity'].strip().upper() == 'WARNING' \
            or "WARNING" in dct['description'].strip().upper() \
            or "WARN" in dct['description'].strip().upper():
        dct[
            'severity'
        ] = '<i class="fa fa-circle orange-dot" value="2" title="Warning"><span style="display:none">WARNING</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-warning">%s</span>' % (dct['description'])

    elif dct['severity'].strip().upper() == 'UP' \
            or "OK" in dct['description'].strip().upper():
        dct[
            'severity'
        ] = '<i class="fa fa-circle green-dot" value="3" title="Ok"><span style="display:none">UP</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-success">%s</span>' % (dct['description'])

    elif dct['severity'].strip().upper() == 'INDOWNTIME':
        dct[
            'severity'
        ] = '<i class="fa fa-circle blue-dot" value="4" title="In Downtime"><span style="display:none">In Downtime</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-success">%s</span>' % (dct['description'])

    else:
        dct[
            'severity'
        ] = '<i class="fa fa-circle grey-dot" value="5" title="Unknown"><span style="display:none">Unknown</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-muted">%s</span>' % (dct['description'])

    return dct


def common_get_severity_icon(severity):
    """
    this function return the severity icon as per the given param
    """

    severity_icon = '<i class="fa fa-circle grey-dot" title="Unknown">\
                     <span style="display:none">Unknown</span></i>'

    if not severity:
        return severity_icon

    severity = severity.lower()

    if severity in ['down', 'critical', 'crit']:
        severity_icon = '<i class="fa fa-circle red-dot" title="{0}">\
                         <span style="display:none">{0}</span></i>'.format(severity.title())
    
    elif severity in ['warning', 'warn', 'major']:
        severity_icon = '<i class="fa fa-circle orange-dot" title="{0}">\
                         <span style="display:none">{0}</span></i>'.format(severity.title())

    elif severity in ['up', 'ok', 'informational']:
        severity_icon = '<i class="fa fa-circle green-dot" title="{0}">\
                         <span style="display:none">{0}</span></i>'.format(severity.title())

    elif severity in ['minor']:
        severity_icon = '<i class="fa fa-circle blue-dot" title="{0}">\
                         <span style="display:none">{0}</span></i>'.format(severity.title())

    elif severity in ['normal']:
        severity_icon = '<i class="fa fa-circle purple-dot" title="{0}">\
                         <span style="display:none">{0}</span></i>'.format(severity.title())
    elif severity in ['indowntime']:
        severity_icon = '<i class="fa fa-circle blue-dot" value="4" title="In Downtime"> \
                        <span style="display:none">In Downtime</span></i>'
    else:
        severity_icon = '<i class="fa fa-circle grey-dot" title="{0}">\
                         <span style="display:none">UP</span></i>'.format(severity.title())

    return severity_icon

# Introducing multiprocessing for Alert Center
from nocout.utils.nqueue import NQueue
from multiprocessing import Process

@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_ALERT', 300))
def polled_results(
                   multi_proc=False,
                   machine_dict=None,
                   table_name=None,
                   data_sources=None,
                   columns=None,
                   condition=None
                   ):
    """
    since the perfomance status data would be refreshed per 5 minutes## we will cache it
    :param table_name: name of the table to query from RAW query
    :param machine_dict:
    :param multi_proc:
    """
    # Fetching the data for the device w.r.t to their machine.
    # # multi processing module here
    # # to fetch the deice results from corrosponding machines

    perf_result = list()
    q = NQueue()
    if multi_proc and q.ping():

        jobs = [
            Process(
                target=get_multiprocessing_performance_data,
                args=(q, machine_device_list, machine, data_sources, columns, condition, table_name)
            ) for machine, machine_device_list in machine_dict.items()
        ]

        for j in jobs:
            j.start()
        for k in jobs:
            k.join()

        while True:
            if not q.empty():
                perf_result.extend(q.get())
            else:
                break
        q.clear()  # removing the queue after its emptied

    else:
        for machine, machine_device_list in machine_dict.items():
            perf_result.extend(
                get_performance_data(
                    machine_device_list, machine, data_sources, columns, condition, table_name
                )
            )

    return perf_result


def get_multiprocessing_performance_data(q, machine_device_list, machine, data_sources, columns, condition, table_name):
    """

    :return:
    """

    query = prepare_query(
        table_name=table_name,
        devices=machine_device_list,
        data_sources=data_sources,
        columns=columns,
        condition=condition
    )

    try:
        q.put(prepare_raw_alert_results(nocout_utils.fetch_raw_result(query, machine)))

    except Exception as e:
        logger.exception(e.message)


def get_performance_data(machine_device_list, machine, data_sources, columns, condition, table_name):
    """

    :return:
    """
    query = prepare_query(
        table_name=table_name,
        devices=machine_device_list,
        data_sources=data_sources,
        columns=columns,
        condition=condition
    )
    return prepare_raw_alert_results(nocout_utils.fetch_raw_result(query, machine))

def get_ping_status(device_list, machine, model):
    """
    Consolidated ping status for devices from the Data base.

    :param model:
    :param machine:
    :param device_list:
    :return:
    """
    perf_utils = PerformanceUtilsGateway()
    st = datetime.datetime.now()

    device_result = {}
    perf_result = {"packet_loss": "N/A",
                   "latency": "N/A",
                   "last_updated": "N/A",
                   "age": "N/A"
                   }

    query = perf_utils.prepare_row_query(table_name="performance_networkstatus",
                              devices=device_list
                              )

    performance_data = nocout_utils.fetch_raw_result(query=query, machine=machine)  # model.objects.raw(query).using(alias=machine)

    indexed_perf_data = make_indexed_polled_results(performance_data)

    # (len(performance_data))
    for device in device_list:
        if device not in device_result:
            device_result[device] = perf_result

    processed = []
    for device in indexed_perf_data:
        if device not in processed:
            processed.append(device)
            perf_result = {"packet_loss": "N/A",
                           "latency": "N/A",
                           "last_updated": "N/A",
                           "device_name": "N/A",
                           "age": "N/A",
                           }
            data = indexed_perf_data[device]
            # for data in performance_data:
            #     if str(data['device_name']).strip().lower() == str(device).strip().lower():
            perf_result['device_name'] = data['device_name']

            # d_src = str(data['data_source']).strip().lower()
            # current_val = str(data['current_value'])
            try:
                # if d_src == "pl":
                perf_result["packet_loss"] = float(data['pl'])
                # if d_src == "rta":
                perf_result["latency"] = float(data['rta'])
            except Exception as e:
                # if d_src == "pl":
                perf_result["packet_loss"] = data['pl']
                # if d_src == "rta":
                perf_result["latency"] = data['rta']

            perf_result["last_updated"] = datetime.datetime.fromtimestamp(
                float(data['sys_timestamp'])
            ).strftime(DATE_TIME_FORMAT)

            perf_result["age"] = datetime.datetime.fromtimestamp(
                float(data["age"])
            ).strftime(DATE_TIME_FORMAT) if data["age"] else ""

            device_result[device] = perf_result

    return device_result

def make_indexed_polled_results(performance_data):
    """


    :param performance_data:
    :return: dictionary for polled results w.r.t to device name
    """
    indexed_raw_results = {}

    for data in performance_data:
        defined_index = data['device_name']
        if defined_index not in indexed_raw_results:
            indexed_raw_results[defined_index] = None
        indexed_raw_results[defined_index] = data

    return indexed_raw_results
