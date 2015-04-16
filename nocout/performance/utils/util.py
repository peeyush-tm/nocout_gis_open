# -*- encoding: utf-8; py-indent-offset: 4 -*-

# python utilities
import datetime
#python utilities

from django.utils.dateformat import format

from multiprocessing import Process, Queue

#nocout utilities
from nocout.utils.util import fetch_raw_result, \
    format_value, cache_for, \
    cached_all_gis_inventory
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
                " WHERE `{1}`.`device_name` IN ( {2} ) " \
                " AND `{1}`.`data_source` IN ( {3} ) {4} " \
                " ORDER BY `{1}`.sys_timestamp DESC) AS `derived_table` " \
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
        SELECT table_1.id AS id,
            table_1.service_name AS service_name,
            table_1.device_name AS device_name,
            table_1.current_value AS pl,
            table_2.current_value AS rta,
            table_1.sys_timestamp AS sys_timestamp,
            table_1.age AS age
        FROM (
        SELECT `id`,`service_name`,`device_name`,`data_source`,`current_value`,`sys_timestamp`, `age`
        FROM
            (
                SELECT `id`,
                `service_name`,
                `device_name`,
                `data_source`,
                `current_value`,
                `sys_timestamp`,
                `age`
                FROM `performance_networkstatus`
                WHERE
                    `performance_networkstatus`.`device_name` IN ({0})
                    AND `performance_networkstatus`.`data_source` IN ( 'pl' )
            ) AS `derived_table`
        ) AS table_1
        JOIN (
            SELECT `id`,`service_name`,`device_name`,`data_source`,`current_value`,`sys_timestamp`
            FROM
                (
                    SELECT `id`,
                    `service_name`,
                    `device_name`,
                    `data_source`,
                    `current_value`,
                    `sys_timestamp`
                    FROM `performance_networkstatus`
                    WHERE
                        `performance_networkstatus`.`device_name` IN ({0})
                        AND `performance_networkstatus`.`data_source` IN ( 'rta' )
              ) AS `derived_table`
        ) AS table_2
        ON (table_1.device_name = table_2.device_name
            AND table_1.data_source != table_2.data_source
            AND table_1.sys_timestamp = table_2.sys_timestamp
            )
        GROUP BY (table_1.device_name);
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
                args=(q, machine_device_list, machine, model)
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

    result_qs = map_results(perf_result, devices)
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
        for perf in performance:  #may run 7 times : per machine once
            try:
                device_info = indexed_qs[device][0].items()
                data_source = perf[device]
                result_qs.append(dict(device_info + data_source.items()))
            except Exception as e:
                continue

    return result_qs


@cache_for(300)
def combined_indexed_gis_devices(indexes, monitored_only=True, technology=None, type_rf=None):
    """
    indexes={
            'sector': 'SECTOR_CONF_ON_NAME',
            'ss': 'SSDEVICENAME',
            'bh': 'BHCONF',
            'pop': 'POP',
            'aggr': 'AGGR',
            'bsconv': 'BSCONV',
            'dr': 'DR_CONF_ON'
        }
    :return:
    """

    indexed_sector = {}
    indexed_ss = {}
    indexed_bh = {}

    # dr case
    indexed_dr = {}

    #pop, aggrigation, bs conveter
    indexed_bh_pop = {}
    indexed_bh_aggr = {}
    indexed_bh_conv = {}

    if indexes:
        raw_results = cached_all_gis_inventory(monitored_only=monitored_only, technology=technology, type_rf=type_rf)

        for result in raw_results:
            defined_sector_index = result[indexes['sector']]
            defined_ss_index = result[indexes['ss']]
            defined_bh_index = result[indexes['bh']]

            defined_bh_pop_index = result[indexes['pop']]
            defined_bh_aggr_index = result[indexes['aggr']]
            defined_bh_conv_index = result[indexes['bsconv']]

            # adding for DR
            defined_dr_conv_index = result[indexes['dr']]

            # indexing sector
            if defined_sector_index not in indexed_sector:
                indexed_sector[defined_sector_index] = []
            try:
                indexed_sector[defined_sector_index].append(result)
            except:
                pass

            # indexing DR
            if defined_dr_conv_index and defined_dr_conv_index not in indexed_dr:
                indexed_dr[defined_dr_conv_index] = list()
            try:
                indexed_dr[defined_dr_conv_index].append(result)
            except:
                pass

            # indexing ss
            if defined_ss_index not in indexed_ss:
                indexed_ss[defined_ss_index] = []
            try:
                indexed_ss[defined_ss_index].append(result)
            except:
                pass

            # indexing bh
            if defined_bh_index and defined_bh_index not in indexed_bh:
                indexed_bh[defined_bh_index] = []
            try:
                indexed_bh[defined_bh_index].append(result)
            except:
                pass

            # pop, aggrigation, bs conveter
            # indexing pop
            if defined_bh_pop_index and defined_bh_pop_index not in indexed_bh_pop:
                indexed_bh_pop[defined_bh_pop_index] = []
            try:
                indexed_bh_pop[defined_bh_pop_index].append(result)
            except:
                pass

            # indexing bsconv
            if defined_bh_conv_index and defined_bh_conv_index not in indexed_bh_conv:
                indexed_bh_conv[defined_bh_conv_index] = []
            try:
                indexed_bh_conv[defined_bh_conv_index].append(result)
            except:
                pass
            # indexing aggregation
            if defined_bh_aggr_index and defined_bh_aggr_index not in indexed_bh_aggr:
                indexed_bh_aggr[defined_bh_aggr_index] = []
            try:
                indexed_bh_aggr[defined_bh_aggr_index].append(result)
            except:
                pass

    return indexed_sector, indexed_ss, indexed_bh, indexed_bh_pop, indexed_bh_aggr, indexed_bh_conv, indexed_dr


@cache_for(300)
def prepare_gis_devices(devices, page_type, monitored_only=True, technology=None, type_rf=None):
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

    indexed_sector, indexed_ss, indexed_bh, indexed_bh_pop, indexed_bh_aggr, indexed_bh_conv, indexed_dr = \
        combined_indexed_gis_devices(
            indexes={
                'sector': 'SECTOR_CONF_ON_NAME',
                'ss': 'SSDEVICENAME',
                'bh': 'BHCONF',
                'pop': 'POP',
                'aggr': 'AGGR',
                'bsconv': 'BSCONV',
                'dr': 'DR_CONF_ON'
            },
            monitored_only=monitored_only, technology=technology, type_rf=type_rf
        )


    # gis_result = indexed_gis_devices(page_type=page_type)

    processed_device = {}

    for device in devices:

        device.update({
            "near_end_ip": "",
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
        is_pop = False
        is_aggr = False
        is_conv = False

        # M7: 15th April 2014 #1308
        is_dr = False

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
        #pop, aggr, conv
        elif device_name in indexed_bh_pop:
            is_pop = True
            raw_result = indexed_bh_pop[device_name]
        #aggr
        elif device_name in indexed_bh_aggr:
            is_aggr = True
            raw_result = indexed_bh_aggr[device_name]
        #conv
        elif device_name in indexed_bh_conv:
            is_conv = True
            raw_result = indexed_bh_conv[device_name]
        # DR # M7: 15th April 2014 #1308
        elif device_name in indexed_dr:
            is_dr = True
            raw_result = indexed_dr[device_name]
        else:
            continue

        sector_details = []
        apnd = ""

        if is_sector or is_dr:
            for bs_row in raw_result:
                if bs_row['SECTOR_SECTOR_ID'] and bs_row['SECTOR_SECTOR_ID'] not in sector_id:
                    sector_id.append(bs_row['SECTOR_SECTOR_ID'])

                    mrc = bs_row['SECTOR_MRC']

                    if mrc and mrc.strip().lower() == 'yes':
                        apnd = "MRC:</br>(PMP 1, PMP 2) "
                    else:
                        port = bs_row['SECTOR_PORT']
                        if port:
                            apnd = "(" + port + ")</br> "

                    sector_details.append(apnd.upper() + bs_row['SECTOR_SECTOR_ID'])

        for bs_row in raw_result:
            if device_name is not None:
                processed_device[device_name] = []
                device.update({
                    "near_end_ip": format_value(bs_row['SECTOR_CONF_ON_IP']),
                    "sector_id": " ".join(sector_details),
                    "circuit_id": format_value(bs_row['CCID']),
                    "customer_name": format_value(bs_row['CUST']),
                    "bs_name": format_value(bs_row['BSALIAS']).upper(),
                    "city": format_value(bs_row['BSCITY']),
                    "state": format_value(bs_row['BSSTATE']),
                    "device_type": format_value(bs_row['SECTOR_TYPE']),
                    "device_technology": format_value(bs_row['SECTOR_TECH'])
                })
                if is_ss:
                    mrc = bs_row['SECTOR_MRC']
                    port = bs_row['SECTOR_PORT']
                    if mrc and mrc.strip().lower() == 'yes':
                        apnd = "MRC:</br>(PMP 1, PMP 2) "
                    else:
                        if port:
                            apnd = "(" + port + ")</br>"

                    if bs_row['CIRCUIT_TYPE']:
                        if bs_row['CIRCUIT_TYPE'].lower().strip() in ['bh', 'backhaul']:
                            device.update({
                                "bs_name": format_value(bs_row['CUST']).upper(),
                            })

                    device.update({
                        "sector_id": apnd.upper() + format_value(bs_row['SECTOR_SECTOR_ID']),
                        "device_type": format_value(bs_row['SS_TYPE']),
                        "device_technology": format_value(bs_row['SECTOR_TECH'])
                    })
                elif is_bh:
                    device.update({
                        "device_type": format_value(bs_row['BHTYPE']),
                        "device_technology": format_value(bs_row['BHTECH'])
                    })
                elif is_pop:
                    device.update({
                        "device_type": format_value(bs_row['POP_TYPE']),
                        "device_technology": format_value(bs_row['POP_TECH'])
                    })
                elif is_aggr:
                    device.update({
                        "device_type": format_value(bs_row['AGGR_TYPE']),
                        "device_technology": format_value(bs_row['AGGR_TECH'])
                    })
                elif is_conv:
                    device.update({
                        "device_type": format_value(bs_row['BSCONV_TYPE']),
                        "device_technology": format_value(bs_row['BSCONV_TECH'])
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
def get_multiprocessing_performance_data(q, device_list, machine, model):
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
    performance_data = fetch_raw_result(query=query, machine=machine)  #model.objects.raw(query).using(alias=machine)

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

    performance_data = fetch_raw_result(query=query, machine=machine)  #model.objects.raw(query).using(alias=machine)

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
    #  device_result

    return device_result


def get_time(start_date, end_date, date_format, data_for):

    isSet = False

    if len(start_date) and len(end_date) and 'undefined' not in [start_date, end_date]:
        isSet = True
        try:
            start_date = float(start_date)
            end_date = float(end_date)
        except Exception, e:
            start_date_object = datetime.datetime.strptime(start_date, date_format)
            end_date_object = datetime.datetime.strptime(end_date, date_format)
            start_date = format(start_date_object, 'U')
            end_date = format(end_date_object, 'U')

    else:
        now_datetime = datetime.datetime.now()
        end_date = format(now_datetime, 'U')
        # In case of 'bihourly' & 'hourly' start date will be start of today(i.e '%Y-%m-%d 00:00:00')
        if data_for in ['bihourly']:
            last_4_days = now_datetime - datetime.timedelta(days=4)
            start_date = format(last_4_days.replace(hour=0, minute=0, second=0, microsecond=0), 'U')
        elif data_for in ['hourly']:
            last_7_days = now_datetime - datetime.timedelta(days=7)
            start_date = format(last_7_days.replace(hour=0, minute=0, second=0, microsecond=0), 'U')
        elif data_for in ['daily', 'weekly', 'monthly', 'yearly']:
            end_date = 0
        else:
            # The end date is the end limit we need to make query till.
            end_date_object = now_datetime
            # The start date is the last monday of the week we need to calculate from.
            start_date_object = end_date_object - datetime.timedelta(days=end_date_object.weekday())
            # Replacing the time, to start with the 00:00:00 of the last monday obtained.
            start_date_object = start_date_object.replace(hour=00, minute=00, second=00, microsecond=00)
            # Converting the date to epoch time or Unix Timestamp
            start_date = format(start_date_object, 'U')

    if end_date:
        end_date = float(end_date)

    if start_date:
        start_date = float(start_date)

    return isSet, start_date, end_date


def color_picker():
    import random
    color = "#"
    color += "%06x" % random.randint(0,0xFFFFFF)
    return color.upper()
