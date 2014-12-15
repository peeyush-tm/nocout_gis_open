# -*- encoding: utf-8; py-indent-offset: 4 -*-

import datetime

#utilities core
from nocout.utils import util as nocout_utils

from performance.utils import util as perf_utils

# misc utility functions

def prepare_query(table_name=None,
                  devices=None,
                  data_sources=["pl", "rta"],
                  columns=None, condition=None,
                  offset=None,
                  limit=None):
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
        query = "SELECT {0} FROM {1} as original_table " \
                "LEFT OUTER JOIN ({1} as derived_table) " \
                "ON ( " \
                "        original_table.data_source = derived_table.data_source " \
                "    AND original_table.device_name = derived_table.device_name " \
                "    AND original_table.id < derived_table.id" \
                ") " \
                "WHERE ( " \
                "        derived_table.id is null " \
                "    AND original_table.device_name in ( {2} ) " \
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

    :return:
    """
    severity_check = ['DOWN', 'CRITICAL', 'WARNING', "WARN", "CRIT"]
    for item in list_to_check:
        for severity in severity_check:
            if severity.lower() in item.lower():
                return True


@nocout_utils.cache_for(300)
def raw_prepare_result(performance_data,
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

    count = 0

    # while count <= math.ceil(len(devices) / limit):

    query = prepare_query(table_name=table_name,
                          devices=devices, #[limit * count:limit * (count + 1)],# spilicing the devices here
                          data_sources=data_sources,
                          columns=columns,
                          condition=condition,
                          offset=offset,
                          limit=None
    )
    # print(query)
    if query:
        performance_data += nocout_utils.fetch_raw_result(query, machine)
    else:
        return []

        # count += 1

    return performance_data


@nocout_utils.cache_for(300)
def indexed_alert_results(performance_data):
    """

    :param performance_data:
    :return:
    """

    indexed_raw_results = {}

    for data in performance_data:
        #this would be a unique combination
        if data['data_source'] is not None and data['device_name'] is not None:
            defined_index = data['device_name'], data['data_source']
            if defined_index not in indexed_raw_results:
                indexed_raw_results[defined_index] = None
            indexed_raw_results[defined_index] = data

    return indexed_raw_results

@nocout_utils.cache_for(300)
def prepare_raw_alert_results(performance_data=None):
    """
    prepare GIS result using raw query

    :param device_list:
    :param performance_data:
    :return:
    """

    indexed_alert_data = indexed_alert_results(performance_data)

    device_list = list()

    for device_alert in indexed_alert_data:
        # the data would be a tuple of ("device_name"."data_source")
        #sample index data
        #{(u'511', u'pl'): {
        # 'data_source': u'pl',
        # 'severity': u'down',
        # 'max_value': u'0',
        # 'age': 1416309593L,
        # 'device_name': u'511',
        # 'sys_timestamp': 0L,
        # 'current_value': u'49',
        # 'ip_address': u'10.157.66.9',
        # 'id': 59440L}
        # }

        device_name, data_source = device_alert

        data = indexed_alert_data[device_alert]

        if severity_level_check(list_to_check=[data['severity']]):
            device_events = {}
            device_events.update({
                'device_name': device_name,
                'severity': data['severity'],
                'ip_address': data["ip_address"],
                'data_source_name': " ".join(map(lambda a: a.title(), data_source.split("_"))),
                'current_value': data["current_value"],
                'max_value': data["max_value"],
                'min_value': data["min_value"],
                'sys_timestamp': datetime.datetime.fromtimestamp(
                    float(data["sys_timestamp"])).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)"),
                'age': datetime.datetime.fromtimestamp(
                    float(data["age"])).strftime("%m/%d/%y (%b) %H:%M:%S")
                    if data["age"]
                    else "",
                'description': ''#data['description']
            })

            device_list.append(device_events)

    return device_list


@nocout_utils.cache_for(300)
def map_results(perf_result, qs):
    """

    :param perf_result:
    :param qs:
    :return:
    """
    result_qs = []

    indexed_qs = perf_utils.pre_map_indexing(index_dict=qs)
    indexed_perf = perf_utils.pre_map_indexing(index_dict=perf_result)

    for device in indexed_qs:
        try:
            device_info = indexed_qs[device][0].items()
            map_perf = indexed_perf[device]
            for data_source in map_perf:
                result_qs.append(dict(device_info + data_source.items()))
        except Exception as e:
            continue

    return result_qs


def ping_service_query(device_name, start_date, end_date):
    """

    :return:
    """
    query = " "\
                    " SELECT " \
                    " original_table.`device_name`," \
                    " original_table.`ip_address`," \
                    " original_table.`service_name`," \
                    " original_table.`severity`," \
                    " original_table.`current_value` as latency," \
                    " `derived_table`.`current_value` as packet_loss, " \
                    " `original_table`.`sys_timestamp`," \
                    " original_table.`description` " \
                    " FROM `performance_eventnetwork` as original_table "\
                    " INNER JOIN (`performance_eventnetwork` as derived_table) "\
                    " ON( "\
                    "    original_table.`data_source` <> derived_table.`data_source` "\
                    "    AND "\
                    "   original_table.`sys_timestamp` = derived_table.`sys_timestamp` "\
                    "    AND "\
                    "    original_table.`device_name` = derived_table.`device_name` "\
                    " ) "\
                    " WHERE( "\
                    "    original_table.`device_name`= '{0}' "\
                    "    AND "\
                    "    original_table.`sys_timestamp` BETWEEN {1} AND {2} "\
                    " ) "\
                    " GROUP BY original_table.`sys_timestamp` "\
                    " ORDER BY original_table.`sys_timestamp` DESC ".format(
                    # (',').join(["original_table.`" + col_name + "`" for col_name in required_columns]),
                    device_name,
                    start_date,
                    end_date
                    )
    return query


def common_prepare_results(dct):
    """
    Common function to prepare result on query set

    :params qs:
    :return qs:
    """

    current_value = dct['current_value']
    try:
        current_value = float(current_value)
    except:
        pass
    if dct['severity'].upper() == 'DOWN' \
            or "CRITICAL" in dct['description'].upper() \
            or dct['severity'].upper() == 'CRITICAL':
        dct['severity'] = '<i class="fa fa-circle red-dot" value="1" title="Critical"><span style="display:none">1</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-danger">%s</span>' % (dct['description'])

    elif dct['severity'].upper() == 'WARNING' \
            or "WARNING" in dct['description'].upper() \
            or "WARN" in dct['description'].upper():
        dct['severity'] = '<i class="fa fa-circle orange-dot" value="2" title="Warning"><span style="display:none">2</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-warning">%s</span>' % (dct['description'])

    elif dct['severity'].upper() == 'UP' \
            or "OK" in dct['description'].upper():
        dct['severity'] = '<i class="fa fa-circle green-dot" value="3" title="Ok"><span style="display:none">3</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-success">%s</span>' % (dct['description'])

    else:
        dct['severity'] = '<i class="fa fa-circle grey-dot" value="4" title="Ok"><span style="display:none">4</span></i>'
        dct['current_value'] = current_value
        dct['description'] = '<span class="text-muted">%s</span>' % (dct['description'])

    return dct