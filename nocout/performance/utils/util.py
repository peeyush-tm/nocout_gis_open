# -*- encoding: utf-8; py-indent-offset: 4 -*-

#python utilities
import datetime
#python utilities

from multiprocessing import Process, Queue

#nocout utilities
from nocout.utils.util import fetch_raw_result, dict_fetchall, \
    format_value, cache_for, time_it, \
    cached_all_gis_inventory, query_all_gis_inventory, query_all_gis_inventory_improved
#nocout utilities

#python logging
import logging
log = logging.getLogger(__name__)
#python logging

# misc utility functions
def prepare_query(table_name=None, devices=None, data_sources=["pl", "rta"], columns=None, condition=None):
    """
    The raw query preparation.

    :param table_name:
    :param devices:
    :param data_sources:
    :param columns:
    :return query:
    """
    in_string = lambda x: "'" + str(x) + "'"
    col_string = lambda x: "`" + str(x) + "`"
    query = None
    if columns:
        columns = (",".join(map(col_string, columns)))
    else:
        columns = "*"

    extra_where_clause = condition if condition else ""

    if table_name and devices:
        query = " SELECT {0} FROM ( " \
                " SELECT {0} FROM `{1}` " \
                " WHERE `{1}`.`device_name` in ( {2} ) " \
                " AND `{1}`.`data_source` in ( {3} ) {4} " \
                " ORDER BY `{1}`.sys_timestamp DESC) as `derived_table` " \
                " GROUP BY `derived_table`.`device_name`, `derived_table`.`data_source` " \
            .format(columns,
                    table_name,
                    (",".join(map(in_string, devices))),
                    (',').join(map(in_string, data_sources)),
                    extra_where_clause.format(table_name)
        )

    return query


def prepare_row_query(table_name=None, devices=None, data_sources=["pl", "rta"], columns=None, condition=None):
    """

    :return:
    """
    in_string = lambda x: "'" + str(x) + "'"
    query = """
        select table_1.id as id,
            table_1.service_name as service_name,
            table_1.device_name as device_name,
            table_1.current_value as pl,
            table_2.current_value as rta,
            table_1.sys_timestamp as sys_timestamp,
            table_1.age as age
        from (
        select `id`,`service_name`,`device_name`,`data_source`,`current_value`,`sys_timestamp`, `age`
        from
            (
                select `id`,
                `service_name`,
                `device_name`,
                `data_source`,
                `current_value`,
                `sys_timestamp`,
                `age`
                from `performance_networkstatus`
                where
                    `performance_networkstatus`.`device_name` in ({0})
                    and `performance_networkstatus`.`data_source` in ( 'pl' )
            ) as `derived_table`
        ) as table_1
        join (
            select `id`,`service_name`,`device_name`,`data_source`,`current_value`,`sys_timestamp`
            from
                (
                    select `id`,
                    `service_name`,
                    `device_name`,
                    `data_source`,
                    `current_value`,
                    `sys_timestamp`
                    from `performance_networkstatus`
                    where
                        `performance_networkstatus`.`device_name` in ({0})
                        and `performance_networkstatus`.`data_source` in ( 'rta' )
              ) as `derived_table`
        ) as table_2
        on (table_1.device_name = table_2.device_name
            and table_1.data_source != table_2.data_source
            and table_1.sys_timestamp = table_2.sys_timestamp
            )
        group by (table_1.device_name);
    """.format(",".join(map(in_string, devices)))

    return query


@cache_for(300)
def polled_results(qs, multi_proc=False, machine_dict={}, model_is=None):
    """
    ##since the perfomance status data would be refreshed per 5 minutes## we will cache it
    """
    #Fetching the data for the device w.r.t to their machine.
    ## multi processing module here
    ## to fetch the deice results from corrosponding machines
    model = model_is
    devices = qs
    processed = []
    perf_result = []
    if multi_proc:

        q = Queue()
        jobs = [
            Process(
                target=get_multiprocessing_performance_data,
                args=(q,machine_device_list, machine,model)
            ) for machine, machine_device_list in machine_dict.items()
        ]

        for j in jobs:
            j.start()
        for k in jobs:
            k.join()

        while True:
            if not q.empty():
                perf_result.append(q.get())
            else:
                break

    else:
        for machine, machine_device_list in machine_dict.items():
            perf_result.append(get_performance_data(machine_device_list, machine, model))

    result_qs = map_results(perf_result,devices)
    return result_qs


@cache_for(300)
def pre_map_indexing(index_dict, index_on='device_name'):
    """

    :param index_dict:
    :param index_on:
    :return:
    """
    indexed_results = {}
    for data in index_dict:
        defined_index = data['device_name']
        if defined_index not in indexed_results:
            indexed_results[defined_index] = []
        indexed_results[defined_index].append(data)

    return indexed_results


@cache_for(300)
def map_results(perf_result, qs):
    """
    """
    result_qs = []
    performance = perf_result
    processed = []

    indexed_qs = pre_map_indexing(index_dict=qs)

    for device in indexed_qs:
        for perf in performance: #may run 7 times : per machine once
            try:
                device_info = indexed_qs[device][0].items()
                data_source = perf[device]
                result_qs.append(dict(device_info + data_source.items()))
            except Exception as e:
                log.exception(e.message)
                continue

    return result_qs


@cache_for(300)
def combined_indexed_gis_devices(indexes):
    """
    indexes={'sector':'SECTOR_CONF_ON_NAME','ss':'SSDEVICENAME','bh':'BHCONF'}
    :return:
    """

    indexed_sector = {}
    indexed_ss = {}
    indexed_bh = {}

    if indexes:
        raw_results = cached_all_gis_inventory(query_all_gis_inventory(monitored_only=True))

        for result in raw_results:
            defined_sector_index = result[indexes['sector']]
            defined_ss_index = result[indexes['ss']]
            defined_bh_index = result[indexes['bh']]
            #indexing sector
            if defined_sector_index not in indexed_sector:
                indexed_sector[defined_sector_index] = []
            #indexing ss
            if defined_ss_index not in indexed_ss:
                indexed_ss[defined_ss_index] = []
            #indexing bh
            if defined_bh_index not in indexed_bh:
                indexed_bh[defined_bh_index] = []

            indexed_sector[defined_sector_index].append(result)
            indexed_ss[defined_ss_index].append(result)
            indexed_bh[defined_bh_index].append(result)


    return indexed_sector, indexed_ss, indexed_bh


@cache_for(300)
def prepare_gis_devices(devices, page_type):
    """
    map the devices with gis data
    :return:
    """
    # ##binary search instead
    # from bisect import bisect_left
    #
    # def binary_search(a, x, lo=0, hi=None):   # can't use a to specify default for hi
    #     hi = hi if hi is not None else len(a) # hi defaults to len(a)
    #     pos = bisect_left(a,x,lo,hi)          # find insertion position
    #     return (pos if pos != hi and a[pos] == x else -1) # don't walk off the end
    # ##binary search instead

    indexed_sector, indexed_ss, indexed_bh = \
        combined_indexed_gis_devices(indexes={'sector':'SECTOR_CONF_ON_NAME','ss':'SSDEVICENAME','bh':'BHCONF'})

    # gis_result = indexed_gis_devices(page_type=page_type)

    processed_device = {}

    for device in devices:

        device.update({
            "sector_id": "",
            "circuit_id": "",
            "customer_name": "",
            "bs_name": "",
            "city": "",
            "state": "",
            "device_type": "",
            "device_technology": ""
        })

        is_sector = False
        is_ss = False
        is_bh = False

        sector_id = []

        device_name = device['device_name']

        if device_name in indexed_sector:
            #is sector
            is_sector = True
            raw_result = indexed_sector[device_name]
        elif device_name in indexed_ss:
            #is ss
            is_ss = True
            raw_result = indexed_ss[device_name]
        elif device_name in indexed_bh:
            #is bh
            is_bh = True
            raw_result = indexed_bh[device_name]
        else:
            continue

        sector_details = []
        apnd = ""

        if is_sector:
            for bs_row in raw_result:
                port = bs_row['SECTOR_PORT']
                if port:
                    apnd = "( " + port + " )"
                if bs_row['SECTOR_SECTOR_ID'] not in sector_id \
                    and bs_row['SECTOR_SECTOR_ID'] is not None:
                    sector_id.append(bs_row['SECTOR_SECTOR_ID'])
                    sector_details.append(bs_row['SECTOR_SECTOR_ID'] + apnd)

        for bs_row in raw_result:
            if device_name is not None:
                processed_device[device_name] = []
                device.update({
                        "sector_id": ", ".join(sector_details),
                        "circuit_id": format_value(bs_row['CCID']),
                        "customer_name": format_value(bs_row['CUST']),
                        "bs_name": format_value(bs_row['BSALIAS']),
                        "city": format_value(bs_row['BSCITY']),
                        "state": format_value(bs_row['BSSTATE']),
                        "device_type": format_value(bs_row['SECTOR_TYPE']),
                        "device_technology": format_value(bs_row['SECTOR_TECH'])
                    })
                if is_ss:
                    if bs_row['CIRCUIT_TYPE']:
                        if bs_row['CIRCUIT_TYPE'].lower().strip() in ['bh', 'backhaul']:
                            device.update({
                                "bs_name": format_value(bs_row['CUST']),
                            })

                    device.update({
                        "sector_id": format_value(bs_row['SECTOR_SECTOR_ID']) + apnd,
                        "device_type": format_value(bs_row['SS_TYPE']),
                        "device_technology": format_value(bs_row['SECTOR_TECH'])
                    })
                elif is_bh:
                    device.update({
                        "device_type": format_value(bs_row['BHTYPE']),
                        "device_technology": format_value(bs_row['BHTECH'])
                    })

    return devices


@cache_for(300)
def indexed_polled_results(performance_data):
    """

    :return: dictionary for polled results w.r.t to device name
    """
    indexed_raw_results = {}

    for data in performance_data:
        defined_index = data['device_name']
        if defined_index not in indexed_raw_results:
            indexed_raw_results[defined_index] = None
        indexed_raw_results[defined_index] = data

    return indexed_raw_results


## for distributed performance collection
## function to accept machine wise device list
## and fetch result from the desired machine
## max processes = 7 (number of total machines)
@cache_for(300)
def get_multiprocessing_performance_data(q,device_list, machine, model):
    """
    Consolidated Performance Data from the Data base.

    :param q:
    :param machine:
    :param model:
    :param device_list:
    :return:
    """

    device_result = {}
    perf_result = {"packet_loss": "N/A",
                   "latency": "N/A",
                   "last_updated": "N/A",
                   "last_updated_date": "N/A",
                   "last_updated_time": "N/A",
                   "age": "N/A"
                  }

    query = prepare_row_query(table_name="performance_networkstatus",
                          devices=device_list,
    )
    # (query)
    performance_data = fetch_raw_result(query=query,machine=machine)#model.objects.raw(query).using(alias=machine)

    indexed_perf_data = indexed_polled_results(performance_data)

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
                           "last_updated_date": "N/A",
                           "last_updated_time": "N/A",
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
            except:
                # if d_src == "pl":
                perf_result["packet_loss"] = data['pl']
                # if d_src == "rta":
                perf_result["latency"] = data['rta']

            perf_result["last_updated"] = datetime.datetime.fromtimestamp(
                float(data['sys_timestamp'])
            ).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)")

            perf_result["age"] = datetime.datetime.fromtimestamp(
                    float(data["age"])).strftime("%m/%d/%y (%b) %H:%M:%S") if data["age"] else ""

            device_result[device] = perf_result
    # (device_result)
    try:
        q.put(device_result)

    except Exception as e:
        log.exception(e.message)


@cache_for(300)
def get_performance_data(device_list, machine, model):
    """
    Consolidated Performance Data from the Data base.

    :param device_list:
    :return:
    """
    st = datetime.datetime.now()

    device_result = {}
    perf_result = {"packet_loss": "N/A",
                   "latency": "N/A",
                   "last_updated": "N/A",
                   "last_updated_date": "N/A",
                   "last_updated_time": "N/A",
                   "age": "N/A"
                  }

    query = prepare_row_query(table_name="performance_networkstatus",
                          devices=device_list
    )

    performance_data = fetch_raw_result(query=query,machine=machine)#model.objects.raw(query).using(alias=machine)

    indexed_perf_data = indexed_polled_results(performance_data)

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
                           "last_updated_date": "N/A",
                           "last_updated_time": "N/A",
                           "device_name" : "N/A",
                           "age" : "N/A",
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
            except:
                # if d_src == "pl":
                perf_result["packet_loss"] = data['pl']
                # if d_src == "rta":
                perf_result["latency"] = data['rta']

            perf_result["last_updated"] = datetime.datetime.fromtimestamp(
                float(data['sys_timestamp'])
            ).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)")

            perf_result["age"] = datetime.datetime.fromtimestamp(
                    float(data["age"])).strftime("%m/%d/%y (%b) %H:%M:%S") if data["age"] else ""


            device_result[device] = perf_result
    # (device_result)
    #  device_result

    return device_result
