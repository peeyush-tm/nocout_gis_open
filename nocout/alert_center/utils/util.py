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


# misc utility functions
def prepare_query(
    table_name=None, 
    devices=None, 
    data_sources=["pl", "rta"], 
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
        query = "SELECT {0} FROM {1} AS original_table " \
                "LEFT OUTER JOIN ({1} AS derived_table) " \
                "ON ( " \
                "        original_table.data_source = derived_table.data_source " \
                "    AND original_table.device_name = derived_table.device_name " \
                "    AND original_table.id < derived_table.id" \
                ") " \
                "WHERE ( " \
                "        derived_table.id IS NULL " \
                "    AND original_table.device_name IN ( {2} ) " \
                "    {3}" \
                "    {4}" \
                ")" \
                "ORDER BY original_table.id DESC " \
                "".format(
            (',').join(["original_table.`" + col_name + "`" for col_name in columns]),
            table_name,
            (",".join(map(in_string, devices))),
            "AND original_table.data_source in ( {0} )".format(
                (',').join(map(in_string, data_sources))
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
                sds_name = service_name.strip() + "_" + data_source.strip()

            try:
                sds_name = SERVICE_DATA_SOURCE[sds_name]['display_name']
            except:
                sds_name = " ".join(map(lambda a: a.title(), data_source.split("_")))

            device_events = {}
            device_events.update({
                'device_name': device_name,
                'severity': data['severity'],
                'ip_address': data["ip_address"],
                'data_source_name': sds_name,
                'current_value': data["current_value"],
                'max_value': data["max_value"],
                'min_value': data["min_value"],
                'sys_timestamp': datetime.datetime.fromtimestamp(
                    float(data["sys_timestamp"])).strftime(DATE_TIME_FORMAT),
                'age': datetime.datetime.fromtimestamp(
                    float(data["age"])
                ).strftime(DATE_TIME_FORMAT) if data["age"] else "",
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

    if dct['severity'].upper() == 'DOWN' \
            or "CRITICAL" in dct['description'].upper() \
            or dct['severity'].upper() == 'CRITICAL':
        dct[
            'severity'
        ] = '<i class="fa fa-circle red-dot" value="1" title="Critical"><span style="display:none">DOWN</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-danger">%s</span>' % (dct['description'])

    elif dct['severity'].upper() == 'WARNING' \
            or "WARNING" in dct['description'].upper() \
            or "WARN" in dct['description'].upper():
        dct[
            'severity'
        ] = '<i class="fa fa-circle orange-dot" value="2" title="Warning"><span style="display:none">WARNING</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-warning">%s</span>' % (dct['description'])

    elif dct['severity'].upper() == 'UP' \
            or "OK" in dct['description'].upper():
        dct[
            'severity'
        ] = '<i class="fa fa-circle green-dot" value="3" title="Ok"><span style="display:none">UP</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-success">%s</span>' % (dct['description'])

    else:
        dct[
            'severity'
        ] = '<i class="fa fa-circle grey-dot" value="4" title="Unknown"><span style="display:none">Unknown</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-muted">%s</span>' % (dct['description'])

    return dct
