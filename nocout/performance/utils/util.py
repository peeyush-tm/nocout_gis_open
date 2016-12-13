# -*- encoding: utf-8; py-indent-offset: 4 -*-e
import ujson as json
import os
import datetime
import time
from operator import itemgetter
from multiprocessing import Process, Queue

from django.utils.dateformat import format

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

# Queue implementation using REDIS
from nocout.utils.nqueue import NQueue

# python logging
import logging

import requests

log = logging.getLogger(__name__)
# python logging

from nocout.settings import PHANTOM_PROTOCOL, PHANTOM_HOST, PHANTOM_PORT, \
    MEDIA_ROOT, CHART_WIDTH, CHART_HEIGHT, CHART_IMG_TYPE, HIGHCHARTS_CONVERT_JS, \
    CACHE_TIME, DATE_TIME_FORMAT, TRAPS_DATABASE

from django.http import HttpRequest

from device.models import Device
from inventory.models import Sector, Circuit
from performance.models import NetworkStatus
from alert_center.models import CurrentAlarms

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


class PerformanceUtilsGateway:
    """
    This class works as gateway between performance utils & other apps
    """
    def prepare_query(
        self,
        table_name=None, 
        devices=None, 
        data_sources=["pl", "rta"], 
        columns=None, 
        condition=None
    ):
        """

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
            condition=condition
        )

        return param1

    def prepare_row_query(
        self, 
        table_name=None, 
        devices=None, 
        data_sources=["pl", "rta"], 
        columns=None, 
        condition=None
    ):
        """

        :param condition:
        :param columns:
        :param data_sources:
        :param devices:
        :param table_name:
        """
        param1 = prepare_row_query(
            table_name=table_name, 
            devices=devices, 
            data_sources=data_sources, 
            columns=columns, 
            condition=condition
        )

        return param1

    def polled_results(self, qs, multi_proc=False, machine_dict={}, model_is=None):
        """

        :param model_is:
        :param machine_dict:
        :param multi_proc:
        :param qs:
        """
        param1 = polled_results(
            qs, 
            multi_proc=multi_proc, 
            machine_dict=machine_dict, 
            model_is=model_is
        )

        return param1

    def pre_map_indexing(self, index_dict, index_on='device_name'):
        """

        :param index_on:
        :param index_dict:
        """
        param1 = pre_map_indexing(index_dict, index_on=index_on)

        return param1

    def map_results(self, perf_result, qs):
        """

        :param qs:
        :param perf_result:
        """
        param1 = map_results(perf_result, qs)

        return param1

    def combined_indexed_gis_devices(self, indexes, monitored_only=True, technology=None, type_rf=None):
        """

        :param type_rf:
        :param technology:
        :param monitored_only:
        :param indexes:
        """
        param1, param2, param3, param4, param5, param6, param7 = combined_indexed_gis_devices(
            indexes, 
            monitored_only=monitored_only, 
            technology=technology, 
            type_rf=type_rf
        )

        return param1, param2, param3, param4, param5, param6, param7

    def prepare_gis_devices(self, devices, page_type, monitored_only=True, technology=None, type_rf=None):
        """

        :param type_rf:
        :param technology:
        :param monitored_only:
        :param page_type:
        :param devices:
        """
        param1 = prepare_gis_devices(
            devices, 
            page_type, 
            monitored_only=monitored_only, 
            technology=technology, 
            type_rf=type_rf
        )

        return param1

    def indexed_polled_results(self, performance_data):
        """

        :param performance_data:
        """
        param1 = indexed_polled_results(performance_data)

        return param1

    def get_time(self, start_date, end_date, date_format, data_for):
        """

        :param data_for:
        :param date_format:
        :param end_date:
        :param start_date:
        """
        param1, param2, param3 = get_time(start_date, end_date, date_format, data_for)

        return param1, param2, param3

    def color_picker(self):
        param1 = color_picker()

        return param1

    def create_perf_chart_img(self, device_name, service, data_source):
        """

        :param data_source:
        :param service:
        :param device_name:
        """
        param1 = create_perf_chart_img(device_name, service, data_source)

        return param1

    def dataTableOrdering(self, self_instance, qs, order_columns):
        """

        :param order_columns:
        :param qs:
        :param self_instance:
        """
        param1 = dataTableOrdering(self_instance, qs, order_columns)

        return param1

    def get_performance_data(self, device_list, machine, model=None):
        """

        :param device_list:
        :param machine:
        :param model:
        """

        param1 = get_performance_data(device_list, machine, model)

        return param1

    def prepare_gis_devices_optimized(
        self,
        qs,
        page_type='network',
        monitored_only=True,
        technology='',
        type_rf='',
        device_name_list=None,
        is_single_call=False,
        device_ip_list=None,
        ticket_required=False
    ):

        param1 = prepare_gis_devices_optimized(
            qs,
            page_type=page_type,
            monitored_only=monitored_only,
            technology=technology,
            type_rf=type_rf,
            device_name_list=device_name_list,
            is_single_call=is_single_call,
            device_ip_list=device_ip_list,
            ticket_required=ticket_required
        )

        return param1

    def get_se_to_pe_min_latency(self, device_id=0, page_type='network'):
        """

        :param device_id
        :param page_type
        """
        param1 = get_se_to_pe_min_latency(device_id, page_type)

        return param1


# misc utility functions
def prepare_query(table_name=None, devices=None, data_sources=["pl", "rta"], columns=None, condition=None):
    """
    The raw query preparation.

    :param condition:
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

    :param condition:
    :param columns:
    :param data_sources:
    :param devices:
    :param table_name:
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


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_PERFORMANCE', 300))
def polled_results(qs, multi_proc=False, machine_dict={}, model_is=None):
    """
    ##since the perfomance status data would be refreshed per 5 minutes## we will cache it
    :param model_is:
    :param machine_dict:
    :param multi_proc:
    :param qs:
    """
    # Fetching the data for the device w.r.t to their machine.
    # # multi processing module here
    # # to fetch the deice results from corrosponding machines
    model = model_is
    devices = qs
    processed = []
    perf_result = []
    q = NQueue()
    if multi_proc and q.ping():
          # using Nocout Queue instead of Python Queue
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
        q.clear()  # removing the queue after its emptied

    else:
        for machine, machine_device_list in machine_dict.items():
            perf_result.append(get_performance_data(machine_device_list, machine, model))

    result_qs = map_results(perf_result, devices)
    return result_qs

@nocout_utils.time_it()
@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_PERFORMANCE', 300))
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


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_PERFORMANCE', 300))
def map_results(perf_result, qs):
    """


    :param qs:
    :param perf_result:
    """
    result_qs = []
    performance = perf_result
    processed = []

    indexed_qs = pre_map_indexing(index_dict=qs)

    for device in indexed_qs:
        for perf in performance:  # may run 7 times : per machine once
            try:
                device_info = indexed_qs[device][0].items()
                data_source = perf[device]
                result_qs.append(dict(device_info + data_source.items()))
            except Exception as e:
                continue

    return result_qs


@nocout_utils.cache_for(CACHE_TIME.get('INVENTORY', 300))
def combined_indexed_gis_devices(indexes, monitored_only=True, technology=None, type_rf=None):
    """
    indexes={
    :param type_rf:
    :param technology:
    :param monitored_only:
    :param indexes:
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

    # pop, aggrigation, bs conveter
    indexed_bh_pop = {}
    indexed_bh_aggr = {}
    indexed_bh_conv = {}

    if indexes:
        raw_results = nocout_utils.cached_all_gis_inventory(monitored_only=monitored_only, technology=technology, type_rf=type_rf)

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
            except Exception as e:
                pass

            # indexing DR
            if defined_dr_conv_index and defined_dr_conv_index not in indexed_dr:
                indexed_dr[defined_dr_conv_index] = list()
            try:
                indexed_dr[defined_dr_conv_index].append(result)
            except Exception as e:
                pass

            # indexing ss
            if defined_ss_index not in indexed_ss:
                indexed_ss[defined_ss_index] = []
            try:
                indexed_ss[defined_ss_index].append(result)
            except Exception as e:
                pass

            # indexing bh
            if defined_bh_index and defined_bh_index not in indexed_bh:
                indexed_bh[defined_bh_index] = []
            try:
                indexed_bh[defined_bh_index].append(result)
            except Exception as e:
                pass

            # pop, aggrigation, bs conveter
            # indexing pop
            if defined_bh_pop_index and defined_bh_pop_index not in indexed_bh_pop:
                indexed_bh_pop[defined_bh_pop_index] = []
            try:
                indexed_bh_pop[defined_bh_pop_index].append(result)
            except Exception as e:
                pass

            # indexing bsconv
            if defined_bh_conv_index and defined_bh_conv_index not in indexed_bh_conv:
                indexed_bh_conv[defined_bh_conv_index] = []
            try:
                indexed_bh_conv[defined_bh_conv_index].append(result)
            except Exception as e:
                pass
            # indexing aggregation
            if defined_bh_aggr_index and defined_bh_aggr_index not in indexed_bh_aggr:
                indexed_bh_aggr[defined_bh_aggr_index] = []
            try:
                indexed_bh_aggr[defined_bh_aggr_index].append(result)
            except Exception as e:
                pass

    return indexed_sector, indexed_ss, indexed_bh, indexed_bh_pop, indexed_bh_aggr, indexed_bh_conv, indexed_dr


@nocout_utils.cache_for(CACHE_TIME.get('INVENTORY', 300))
def prepare_gis_devices(devices, page_type, monitored_only=True, technology=None, type_rf=None):
    """
    map the devices with gis data
    :param type_rf:
    :param technology:
    :param monitored_only:
    :param page_type:
    :param devices:
    :return:
    """

    def put_na(bsdict, key):
        """
        put NA for keys of a dictionary
        :param bsdict:
        :param key : key in the dictionary
        """
        if key in bsdict:
            return bsdict.get(key, 'NA')
        else:
            return 'NA'

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

    result_devices = list() # all the devices which can properly map to their inventory

    for device in devices:

        device_name = device.get('device_name')
        # if not device_name:
        #     continue

        device.update({
            "id": 0,
            "near_end_ip": "",
            "sector_id": "",
            "circuit_id": "",
            "customer_name": "",
            "bs_name": "",
            "city": "",
            "state": "",
            "device_type": "",
            "device_technology": "",
            # Newly added keys for inventory status headers: 15-May-15
            "device_type_id": "",
            "device_technology_id": "",
            "ss_technology": "",
            "ss_technology_id": "",
            "ss_type": "",
            "ss_type_id": "",
            "bh_technology": "",
            "bh_technology_id": "",
            "bh_type": "",
            "bh_type_id": "",
            "planned_freq": "",
            "polled_freq": "",
            "qos_bw": "",
            "ss_name": "",
            "sector_id_str": "",
            "pmp_port_str": "",
            "bh_capacity": "",
            "bh_port": "",
            "bh_id": "",
            "bs_id": "",
            "ss_id": "",
            "sector_pk": "",
            "sector_pk_str": "",
            "ckt_id": "",
            "cust_id": "",
            "city_id": "",
            "state_id": "",
            "near_end_id": "",
            "freq_id": "",
            # Newly added keys for Network Alert Details Bakhaul Tab: 20-May-15
            "bh_connectivity": "",
            # BS names & ids in case of BH & other devices
            "bs_names_list": "",
            "bs_ids_list": "",
            "bs_bh_ports_list": "",
            "bs_bh_capacity_list": ""
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
            # is sector
            is_sector = True
            raw_result = indexed_sector[device_name]
        elif device_name in indexed_ss:
            # is ss
            is_ss = True
            raw_result = indexed_ss[device_name]
        elif device_name in indexed_bh:
            # is bh
            is_bh = True
            raw_result = indexed_bh[device_name]
        # pop, aggr, conv
        elif device_name in indexed_bh_pop:
            is_pop = True
            raw_result = indexed_bh_pop[device_name]
        # aggr
        elif device_name in indexed_bh_aggr:
            is_aggr = True
            raw_result = indexed_bh_aggr[device_name]
        # conv
        elif device_name in indexed_bh_conv:
            is_conv = True
            raw_result = indexed_bh_conv[device_name]
        # DR # M7: 15th April 2014 #1308
        elif device_name in indexed_dr:
            is_dr = True
            raw_result = indexed_dr[device_name]
        else:
            continue

        # Init variables
        apnd = ""
        sector_details = list()
        sector_id_str = list()
        pmp_port_str = list()
        sector_pk_str = list()
        bs_names_list = list()
        bs_ids_list = list()
        bs_bh_ports_list = list()
        bs_bh_capacity_list = list()

        if is_sector or is_dr:
            for bs_row in raw_result:
                if bs_row.get('SECTOR_SECTOR_ID') and bs_row.get('SECTOR_SECTOR_ID') not in sector_id:
                    sector_id.append(bs_row.get('SECTOR_SECTOR_ID'))
                    mrc = bs_row.get('SECTOR_MRC')

                    if mrc and mrc.strip().lower() == 'yes':
                        apnd = "MRC:</br>(PMP 1, PMP 2) "
                    else:
                        port = bs_row.get('SECTOR_PORT')
                        if port:
                            apnd = "(" + port + ")</br> "
                            pmp_port_str.append(port)
                    # append formatted sector id with port in list
                    sector_details.append(apnd.upper() + bs_row.get('SECTOR_SECTOR_ID'))
                    if bs_row.get('SECTOR_SECTOR_ID', False):
                        # append sector id in list
                        sector_id_str.append(bs_row.get('SECTOR_SECTOR_ID'))

                    # append sector primary key in list
                    if bs_row.get('SECTOR_ID', False):
                        sector_pk_str.append(str(bs_row.get('SECTOR_ID')))

        elif is_bh or is_pop or is_aggr or is_conv:  # In case of BH & Other devices

            for bs_row in raw_result:
                if bs_row.get('BSID') and str(bs_row.get('BSID')) not in bs_ids_list:
                    bs_ids_list.append(str(bs_row.get('BSID')))
                    bs_names_list.append(bs_row.get('BSALIAS').upper())
                    bs_bh_ports_list.append(str(bs_row.get('BS_BH_PORT')))
                    bs_bh_capacity_list.append(str(bs_row.get('BS_BH_CAPACITY')))
        else:
            pass

        for bs_row in raw_result:
            device.update({
                "near_end_ip": put_na(bs_row, 'SECTOR_CONF_ON_IP'),
                "sector_id": " ".join(sector_details),
                "circuit_id": put_na(bs_row, 'CCID'),
                "customer_name": put_na(bs_row, 'CUST'),
                "bs_name": put_na(bs_row, 'BSALIAS'),
                "city": put_na(bs_row, 'BSCITY'),
                "state": put_na(bs_row, 'BSSTATE'),
                "device_type": put_na(bs_row, 'SECTOR_TYPE'),
                "device_technology": put_na(bs_row, 'SECTOR_TECH'),
                # Newly added keys for inventory status headers: 15-May-15
                "device_type_id": put_na(bs_row, 'SECTOR_TYPE_ID'),
                "device_technology_id": put_na(bs_row, 'SECTOR_TECH_ID'),
                "ss_technology": put_na(bs_row, 'SS_TECH'),
                "ss_technology_id": put_na(bs_row, 'SS_TECH_ID'),
                "ss_type": put_na(bs_row, 'SS_TYPE'),
                "ss_type_id": put_na(bs_row, 'SS_TYPE_ID'),
                "bh_technology": put_na(bs_row, 'BHTECH'),
                "bh_technology_id": put_na(bs_row, 'BHTECHID'),
                "bh_type": put_na(bs_row, 'BHTYPE'),
                "bh_type_id": put_na(bs_row, 'BHTYPEID'),
                "planned_freq": put_na(bs_row, 'SECTOR_PLANNED_FREQUENCY'),
                "polled_freq": put_na(bs_row, 'SECTOR_FREQUENCY'),
                "qos_bw": put_na(bs_row, 'QOS'),
                "ss_name": put_na(bs_row, 'SS_ALIAS'),
                "sector_id_str": ",".join(sector_id_str),
                "pmp_port_str": ",".join(pmp_port_str),
                "bh_capacity": put_na(bs_row, 'BH_CAPACITY'),
                "bh_port": put_na(bs_row, 'BH_PORT'),
                "bh_id": put_na(bs_row, 'BHID'),
                "bs_id": put_na(bs_row, 'BSID'),
                "ss_id": put_na(bs_row, 'SSID'),
                "sector_pk": put_na(bs_row, 'SECTOR_ID'),
                "sector_pk_str": ",".join(sector_pk_str),
                "ckt_id": put_na(bs_row, 'CID'),
                "cust_id": put_na(bs_row, 'CUSTID'),
                "city_id": put_na(bs_row, 'BSCITYID'),
                "state_id": put_na(bs_row, 'BSSTATEID'),
                "near_end_id": put_na(bs_row, 'SECTOR_CONF_ON_ID'),
                "freq_id": put_na(bs_row, 'SECTOR_FREQUENCY_ID'),
                # Newly added keys for Network Alert Details Bakhaul Tab: 20-May-15
                "bh_connectivity": put_na(bs_row, 'BH_CONNECTIVITY'),
                # BS names & ids in case of BH & other devices
                "bs_names_list": ",".join(bs_names_list),
                "bs_ids_list": ",".join(bs_ids_list),
                "bs_bh_ports_list": ",".join(bs_bh_ports_list),
                "bs_bh_capacity_list": ",".join(bs_bh_capacity_list)
            })

            if is_sector:
                device.update({
                    "id": bs_row.get('SECTOR_CONF_ON_ID', 0)
                })
            elif is_dr:
                device.update({
                    "id": bs_row.get('DR_CONF_ON_ID', 0),
                    "sector_id": "DR:</br>" + " ".join(sector_details),
                })
            elif is_ss:
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
                            "bs_name": nocout_utils.format_value(bs_row['CUST']).upper(),
                        })

                device.update({
                    "id": bs_row.get('SS_DEVICE_ID', 0),
                    "sector_id": apnd.upper() + nocout_utils.format_value(bs_row['SECTOR_SECTOR_ID']),
                    "device_type": nocout_utils.format_value(bs_row['SS_TYPE']),
                    "device_technology": nocout_utils.format_value(bs_row['SECTOR_TECH'])
                })
            elif is_bh:
                device.update({
                    "id": bs_row.get('BH_DEVICE_ID', 0),
                    "device_type": nocout_utils.format_value(bs_row['BHTYPE']),
                    "device_technology": nocout_utils.format_value(bs_row['BHTECH'])
                })
            elif is_pop:
                device.update({
                    "id": bs_row.get('POP_DEVICE_ID', 0),
                    "device_type": nocout_utils.format_value(bs_row['POP_TYPE']),
                    "device_technology": nocout_utils.format_value(bs_row['POP_TECH'])
                })
            elif is_aggr:
                device.update({
                    "id": bs_row.get('AGGR_DEVICE_ID', 0),
                    "device_type": nocout_utils.format_value(bs_row['AGGR_TYPE']),
                    "device_technology": nocout_utils.format_value(bs_row['AGGR_TECH'])
                })
            elif is_conv:
                device.update({
                    "id": bs_row.get('BSCONV_DEVICE_ID', 0),
                    "device_type": nocout_utils.format_value(bs_row['BSCONV_TYPE']),
                    "device_technology": nocout_utils.format_value(bs_row['BSCONV_TECH'])
                })
            else:
                continue

        result_devices.append(device)

    return result_devices


@nocout_utils.cache_for(CACHE_TIME.get('INVENTORY', 300))
def prepare_gis_devices_optimized(
    qs,
    page_type='network',
    monitored_only=True,
    technology='',
    type_rf='',
    device_name_list=None,
    is_single_call=False,
    device_ip_list=None,
    ticket_required=False
):
    """
    This function first fetch inventory data as per the params & then 
    map the inventory data with given qs
    """
    if not qs:
        return qs

    resultant_dataset = list()

    if page_type in ['customer']:

        if technology.upper() in ['P2P', 'PTP', 'PTP-BH']:
            inventory_resultset = nocout_utils.fetch_ss_inventory(
                technology=technology,
                device_name_list=device_name_list
            )

            sector_inventory_resultset = nocout_utils.fetch_ptp_sector_inventory(
                device_name_list=device_name_list
            )

            if len(inventory_resultset):
                inventory_resultset.update(sector_inventory_resultset)
            else:
                inventory_resultset = sector_inventory_resultset

            for data in qs:
                data.update({
                    "near_end_ip": "NA",
                    "sector_id": "NA",
                    "circuit_id": "NA",
                    "customer_name": "NA",
                    "bs_name": "NA",
                    "ss_name": "NA",
                    "ss_id": 0,
                    "city": "NA",
                    "region": "NA",
                    "state": "NA",
                    "device_type": "NA",
                    "device_technology": "NA",
                    "site_id": "NA",
                    "bs_id": 0,
                    "city_id": 0,
                    "state_id": 0,
                    "tech_id": 0,
                    "type_id": 0,
                    "near_device_id" : 0,
                    "ckt_pk": 0,
                    "sect_pk": 0,
                    "cust_id": 0,
                    "qos_bw": "NA",
                    "polled_frequency": "NA",
                    "freq_id": 0,
                })

                device_name = data.get('device_name')
                if not device_name or not len(inventory_resultset):
                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
                    continue

                inventory_dataset = inventory_resultset.get(device_name)

                if not inventory_dataset or not len(inventory_dataset):
                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
                    continue

                for inventory_row in inventory_dataset:
                    data.update({
                        "id" : inventory_row.get('DEVICE_ID', 0),
                        "near_end_ip": inventory_row.get('SECTOR_CONF_ON_IP', 'NA'),
                        "sector_id": inventory_row.get('SECTOR_PORT_SECTOR_ID', 'NA'),
                        "circuit_id": inventory_row.get('CCID', 'NA'),
                        "customer_name": inventory_row.get('CUST', 'NA'),
                        "bs_name": inventory_row.get('BSALIAS', 'NA'),
                        "ss_name": inventory_row.get('SSALIAS', 'NA'),
                        "ss_id": inventory_row.get('SSID', 0),
                        "region": inventory_row.get('org_alias', 'NA'),
                        "city": inventory_row.get('BSCITY', 'NA'),
                        "state": inventory_row.get('BSSTATE', 'NA'),
                        "site_id": inventory_row.get('SITEID', 'NA'),
                        "device_type": inventory_row.get('DEVICE_TYPE', 'NA'),
                        "device_technology": inventory_row.get('DEVICE_TECH', 'NA'),
                        "bs_id": inventory_row.get('BSID', 0),
                        "city_id": inventory_row.get('BSCITYID', 0),
                        "state_id": inventory_row.get('BSSTATEID', 0),
                        "tech_id": inventory_row.get('TECHID', 0),
                        "type_id": inventory_row.get('TYPEID', 0),
                        "near_device_id" : inventory_row.get('NEAR_DEVICE_ID', 0),
                        "ckt_pk" : inventory_row.get('CID', 0),
                        "sect_pk" : inventory_row.get('SECT_ID', 0),
                        "cust_id" : inventory_row.get('CUSTID', 0),
                        "qos_bw" : inventory_row.get('CKT_QOS', "NA"),
                        "polled_frequency" : inventory_row.get('FREQUENCY', "NA"),
                        "freq_id" : inventory_row.get('FREQ_ID', 0),
                    })

                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
        else:
            inventory_resultset = nocout_utils.fetch_ss_inventory(
                technology=technology,
                device_name_list=device_name_list
            )

            for data in qs:
                data.update({
                    "near_end_ip": "NA",
                    "sector_id": "NA",
                    "circuit_id": "NA",
                    "customer_name": "NA",
                    "bs_name": "NA",
                    "ss_name": "NA",
                    "ss_id": 0,
                    "site_id": "NA",
                    "region": "NA",
                    "city": "NA",
                    "state": "NA",
                    "device_type": "NA",
                    "device_technology": "NA",
                    "bs_id": 0,
                    "city_id": 0,
                    "state_id": 0,
                    "tech_id": 0,
                    "type_id": 0,
                    "near_device_id" : 0,
                    "ckt_pk" : 0,
                    "sect_pk" : 0,
                    "cust_id" : 0,
                    "qos_bw" : "NA",
                    "polled_frequency": "NA",
                    "freq_id": 0
                })


                device_name = data.get('device_name')
                if not device_name or not len(inventory_resultset):
                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
                    continue

                inventory_dataset = inventory_resultset.get(device_name)

                if not inventory_dataset or not len(inventory_dataset):
                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
                    continue

                for inventory_row in inventory_dataset:

                    data.update({
                        "id" : inventory_row.get('DEVICE_ID', 0),
                        "near_end_ip": inventory_row.get('SECTOR_CONF_ON_IP', 'NA'),
                        "sector_id": inventory_row.get('SECTOR_PORT_SECTOR_ID', 'NA'),
                        "circuit_id": inventory_row.get('CCID', 'NA'),
                        "customer_name": inventory_row.get('CUST', 'NA'),
                        "bs_name": inventory_row.get('BSALIAS', 'NA'),
                        "ss_name": inventory_row.get('SSALIAS', 'NA'),
                        "site_id": inventory_row.get('SITEID', 'NA'),
                        "ss_id": inventory_row.get('SSID', 'NA'),
                        "city": inventory_row.get('BSCITY', 'NA'),
                        "state": inventory_row.get('BSSTATE', 'NA'),
                        "device_type": inventory_row.get('DEVICE_TYPE', 'NA'),
                        "device_technology": inventory_row.get('DEVICE_TECH', 'NA'),
                        "bs_id": inventory_row.get('BSID', 0),
                        "region": inventory_row.get('org_alias', 'NA'),
                        "city_id": inventory_row.get('BSCITYID', 0),
                        "state_id": inventory_row.get('BSSTATEID', 0),
                        "tech_id": inventory_row.get('TECHID', 0),
                        "type_id": inventory_row.get('TYPEID', 0),
                        "near_device_id" : inventory_row.get('NEAR_DEVICE_ID', 0),
                        "ckt_pk" : inventory_row.get('CID', 0),
                        "sect_pk" : inventory_row.get('SECT_ID', 0),
                        "cust_id" : inventory_row.get('CUSTID', 0),
                        "qos_bw" : inventory_row.get('CKT_QOS', 0),
                        "polled_frequency" : inventory_row.get('FREQUENCY', "NA"),
                        "freq_id" : inventory_row.get('FREQ_ID', 0),
                    })

                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
    elif page_type in ['network']:
        if technology.upper() in ['P2P', 'PTP', 'PTP-BH']:
            ptpbh_ss_inventory_resultset = nocout_utils.fetch_ptpbh_ss_inventory(
                technology=technology,
                device_name_list=device_name_list
            )
            

            ptpbh_sector_inventory_resultset = nocout_utils.fetch_ptpbh_sector_inventory(
                device_name_list=device_name_list
            )
            
            if len(ptpbh_ss_inventory_resultset):
                # Merge 'ptpbh_sector_inventory_resultset' dict with 'ptpbh_ss_inventory_resultset'
                ptpbh_ss_inventory_resultset.update(ptpbh_sector_inventory_resultset)
            else:
                ptpbh_ss_inventory_resultset = ptpbh_sector_inventory_resultset

            for data in qs:
                data.update({
                    "near_end_ip": "NA",
                    "sector_id": "NA",
                    "circuit_id": "NA",
                    "customer_name": "NA",
                    "customer_count": "NA",
                    "bs_name": "NA",
                    "ss_name": "NA",
                    "ss_id": "NA",
                    "site_id": "NA",
                    "city": "NA",
                    "state": "NA",
                    "region": "NA",
                    "device_type": "NA",
                    "device_technology": "NA",
                    "qos_bw" : "NA",
                    "bs_id": 0,
                    "city_id": 0,
                    "state_id": 0,
                    "tech_id": 0,
                    "type_id": 0,
                    "near_device_id" : 0,
                    "ckt_pk" : 0,
                    "sect_pk" : 0,
                    "cust_id" : 0,
                    "polled_frequency" : "NA",
                    "freq_id" : 0,
                    "planned_frequency": "NA"
                })


                device_name = data.get('device_name')
                if not device_name or not len(ptpbh_ss_inventory_resultset):
                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
                    continue

                inventory_dataset = ptpbh_ss_inventory_resultset.get(device_name)

                if not inventory_dataset or not len(inventory_dataset):
                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
                    continue

                for inventory_row in inventory_dataset:

                    data.update({
                        "id" : inventory_row.get('DEVICE_ID', 0),
                        "near_end_ip": inventory_row.get('SECTOR_CONF_ON_IP', 'NA'),
                        "sector_id": inventory_row.get('SECTOR_PORT_SECTOR_ID', 'NA'),
                        "circuit_id": inventory_row.get('CCID', 'NA'),
                        "customer_name": inventory_row.get('CUST', 'NA'),
                        "bs_name": inventory_row.get('BSALIAS', 'NA'),
                        "ss_name": inventory_row.get('SSALIAS', 'NA'),
                        "ss_id": inventory_row.get('SSID', 'NA'),
                        "site_id": inventory_row.get('SITEID', 'NA'),
                        "region": inventory_row.get('org_alias', 'NA'),
                        "city": inventory_row.get('BSCITY', 'NA'),
                        "state": inventory_row.get('BSSTATE', 'NA'),
                        "device_type": inventory_row.get('DEVICE_TYPE', 'NA'),
                        "device_technology": inventory_row.get('DEVICE_TECH', 'NA'),
                        "qos_bw" : inventory_row.get('CKT_QOS', "NA"),
                        "bs_id": inventory_row.get('BSID', 0),
                        "city_id": inventory_row.get('BSCITYID', 0),
                        "state_id": inventory_row.get('BSSTATEID', 0),
                        "tech_id": inventory_row.get('TECHID', 0),
                        "type_id": inventory_row.get('TYPEID', 0),
                        "near_device_id" : inventory_row.get('NEAR_DEVICE_ID', 0),
                        "ckt_pk" : inventory_row.get('CID', 0),
                        "sect_pk" : inventory_row.get('SECT_ID', 0),
                        "cust_id" : inventory_row.get('CUSTID', 0),
                        "polled_frequency" : inventory_row.get('FREQUENCY', "NA"),
                        "freq_id" : inventory_row.get('FREQ_ID', 0),
                        "planned_frequency": inventory_row.get('SECTOR_PLANNED_FREQUENCY', 'NA'),
                    })

                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
        else:
            if is_single_call and technology in ['WiMAX']:
                grouped_query = False
            else:
                grouped_query = True

            ticket_dict = {}
            if ticket_required and device_ip_list:
                # call fucntion for getting indexed dict
                # where key = ip_address and value = ticket number
                ticket_dict = get_ticket_numbers(device_ip_list)

            sector_inventory_resultset = nocout_utils.fetch_sector_inventory(
                technology=technology,
                device_name_list=device_name_list,
                grouped_query=grouped_query
            )

            if technology in ['WiMAX']:

                # Fetch DR devices
                dr_inventory_resultset = nocout_utils.fetch_dr_sector_inventory(
                    device_name_list=device_name_list,
                    grouped_query=grouped_query
                )

                if len(sector_inventory_resultset):
                    # Merge 'dr_inventory_resultset' dict with sector_inventory_resultset
                    sector_inventory_resultset.update(dr_inventory_resultset)
                else:
                    # Merge 'dr_inventory_resultset' dict with sector_inventory_resultset
                    sector_inventory_resultset = dr_inventory_resultset

                # Fetch MRC devices
                mrc_inventory_resultset = nocout_utils.fetch_mrc_sector_inventory(
                    device_name_list=device_name_list,
                    grouped_query=grouped_query
                )

                if len(sector_inventory_resultset):
                    # Merge 'mrc_inventory_resultset' dict with sector_inventory_resultset
                    sector_inventory_resultset.update(mrc_inventory_resultset)
                else:
                    # Merge 'mrc_inventory_resultset' dict with sector_inventory_resultset
                    sector_inventory_resultset = mrc_inventory_resultset

            for data in qs:
                data.update({
                    "near_end_ip": "NA",
                    "sector_id": "NA",
                    "circuit_id": "NA",
                    "customer_name": "NA",
                    "bs_name": "NA",
                    "city": "NA",
                    "state": "NA",
                    "device_type": "NA",
                    "region": "NA",
                    "site_id": "NA",
                    "device_technology": "NA",
                    "bs_id": 0,
                    "city_id": 0,
                    "state_id": 0,
                    "tech_id": 0,
                    "type_id": 0,
                    "near_device_id" : 0,
                    "ckt_pk" : 0,
                    "sect_pk" : 0,
                    "cust_id" : 0,
                    "polled_frequency" : "NA",
                    "freq_id" : 0,
                    "planned_frequency": "NA",
                    "customer_count": 0,
                    "ticket_no": "NA"
                })


                device_name = data.get('device_name')
                device_ip = data.get('ip_address')
                # Update ticket_number 
                data.update({"ticket_no": ticket_dict.get(device_ip, 'NA')})

                if not device_name or not len(sector_inventory_resultset):
                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
                    continue

                inventory_dataset = sector_inventory_resultset.get(device_name)

                if not inventory_dataset or not len(inventory_dataset):
                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
                    continue

                for inventory_row in inventory_dataset:
                    
                    data.update({
                        "id" : inventory_row.get('DEVICE_ID', 0),
                        "near_end_ip": inventory_row.get('SECTOR_CONF_ON_IP', 'NA'),
                        "sector_id": inventory_row.get('SECTOR_PORT_SECTOR_ID', 'NA'),
                        "sector_sector_id": inventory_row.get('SECTOR_PORT_SECTOR_ID', 'NA'),
                        "pmp_port": inventory_row.get('SECTOR_PORT', 'NA'),
                        "circuit_id": inventory_row.get('CCID', 'NA'),
                        "customer_name": inventory_row.get('CUST', 'NA'),
                        "bs_name": inventory_row.get('BSALIAS', 'NA'),
                        "city": inventory_row.get('BSCITY', 'NA'),
                        "site_id": inventory_row.get('SITEID', 'NA'),
                        "state": inventory_row.get('BSSTATE', 'NA'),
                        "device_type": inventory_row.get('DEVICE_TYPE', 'NA'),
                        "device_technology": inventory_row.get('DEVICE_TECH', 'NA'),
                        "region": inventory_row.get('org_alias', 'NA'),
                        "bs_id": inventory_row.get('BSID', 0),
                        "city_id": inventory_row.get('BSCITYID', 0),
                        "state_id": inventory_row.get('BSSTATEID', 0),
                        "tech_id": inventory_row.get('TECHID', 0),
                        "type_id": inventory_row.get('TYPEID', 0),
                        "near_device_id" : inventory_row.get('NEAR_DEVICE_ID', 0),
                        "ckt_pk" : inventory_row.get('CID', 0),
                        "sect_pk" : inventory_row.get('SECT_ID', 0),
                        "cust_id" : inventory_row.get('CUSTID', 0),
                        "polled_frequency" : inventory_row.get('FREQUENCY', "NA"),
                        "freq_id" : inventory_row.get('FREQ_ID', 0),
                        "planned_frequency": inventory_row.get('SECTOR_PLANNED_FREQUENCY', 'NA'),
                        "customer_count": inventory_row.get('CUSTOMER_COUNT', 0),
                    })
                    
                    # append the deep copied dict
                    resultant_dataset.append(json.loads(json.dumps(data)))
    else:
        if is_single_call:
            grouped_query = False
        else:
            grouped_query = True
            
        backhaul_inventory_resultset = nocout_utils.fetch_backhaul_inventory(
            device_name_list=device_name_list,
            type_rf=type_rf,
            grouped_query=grouped_query
        )

        for data in qs:
            data.update({
                "bs_name": "NA",
                "city": "NA",
                "state": "NA",
                "device_type": "NA",
                "device_technology": "NA",
                "bh_connectivity" : "NA",
                "customer_count" : "NA",
                "bh_capacity" : "NA",
                "region": "NA",
                "bh_alias" : "NA",
                "bh_port" : 0,
                "bs_id": 0,
                "bh_id": 0,
                "city_id": 0,
                "state_id": 0,
                "tech_id": 0,
                "type_id": 0,
                "pe_hostname": "NA",
                "site_id": "NA",
            })


            device_name = data.get('device_name')
            if not device_name or not len(backhaul_inventory_resultset):
                # append the deep copied dict
                resultant_dataset.append(json.loads(json.dumps(data)))
                continue

            inventory_dataset = backhaul_inventory_resultset.get(device_name)

            if not inventory_dataset or not len(inventory_dataset):
                # append the deep copied dict
                resultant_dataset.append(json.loads(json.dumps(data)))
                continue

            for inventory_row in inventory_dataset:
                data.update({
                    "id" : inventory_row.get('DEVICE_ID', 0),
                    "bs_name": inventory_row.get('BSALIAS', 'NA'),
                    "city": inventory_row.get('BSCITY', 'NA'),
                    "state": inventory_row.get('BSSTATE', 'NA'),
                    "device_type": inventory_row.get('DEVICE_TYPE', 'NA'),
                    "device_technology": inventory_row.get('DEVICE_TECH', 'NA'),
                    "bh_connectivity" : inventory_row.get('BH_CONNECTIVITY', 'NA'),
                    "region": inventory_row.get('org_alias', 'NA'),
                    "bh_capacity" : inventory_row.get('BHCAPACITY', 'NA'),
                    "bh_alias" : inventory_row.get('BH_ALIAS', 'NA'),
                    "bh_port" : inventory_row.get('BHPORT', 'NA'),
                    "bs_id": inventory_row.get('BSID', 0),
                    "bh_id": inventory_row.get('BHID', 0),
                    "site_id": inventory_row.get('SITEID', 'NA'),
                    "city_id": inventory_row.get('BSCITYID', 0),
                    "state_id": inventory_row.get('BSSTATEID', 0),
                    "tech_id": inventory_row.get('TECHID', 0),
                    "type_id": inventory_row.get('TYPEID', 0),
                    "pe_hostname": inventory_row.get('PE_HOSTNAME', "NA")
                })
                
                # append the deep copied dict
                resultant_dataset.append(json.loads(json.dumps(data)))

    return resultant_dataset


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_PERFORMANCE', 300))
def indexed_polled_results(performance_data):
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


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_PERFORMANCE', 300))
def get_performance_data(device_list, machine, model):
    """
    Consolidated Performance Data from the Data base.

    :param model:
    :param machine:
    :param device_list:
    :return:
    """
    st = datetime.datetime.now()

    device_result = {}
    perf_result = {"packet_loss": "N/A",
                   "latency": "N/A",
                   "last_updated": "N/A",
                   "age": "N/A"
                   }

    query = prepare_row_query(table_name="performance_networkstatus",
                              devices=device_list
                              )

    performance_data = nocout_utils.fetch_raw_result(query=query, machine=machine)  # model.objects.raw(query).using(alias=machine)

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


def get_time(start_date, end_date, date_format, data_for):
    """

    :param start_date:
    :param end_date:
    :param date_format:
    :param data_for:
    :return:
    """
    isSet = False

    if len(str(start_date)) and len(str(end_date)) and 'undefined' not in [start_date, end_date]:
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
    """


    :return:
    """
    import random

    color = "#"
    color += "%06x" % random.randint(0, 0xFFFFFF)
    return color.upper()


def create_perf_chart_img(device_name, service, data_source):
    """
    This function create performance chart image for given device, 
    service & data_source and return image url
    :param data_source:
    :param service:
    :param device_name:
    """
    device_id = Device.objects.get(device_name=device_name).id
    kwargs_dict = {
        'service_name': service,
        'service_data_source_type': data_source,
        'device_id': device_id
    }

    # create http request for getting rows data (for accessing list view classes)
    request_object = HttpRequest()

    # import performance views gateway class
    from performance.views import PerformanceViewsGateway

    # Create instance of 'PerformanceViewsGateway' class
    perf_views = PerformanceViewsGateway()

    # call "initGetServiceTypePerformanceData"
    perf_data_class = perf_views.initGetServiceTypePerformanceData()

    # Attach request HTTP object with 'initGetServiceTypePerformanceData' instance
    perf_data_class.request = request_object

    # Attach 'kwargs' with 'initGetServiceTypePerformanceData' instance
    perf_data_class.kwargs = kwargs_dict

    # Make 'GET' request to 'initGetServiceTypePerformanceData' class
    fetched_result = perf_data_class.get(request_object, service, data_source, device_id)

    # convert the fetched content to json format
    perf_data = json.loads(fetched_result.content)

    chart_dataset = []
    valuetext = ''
    if perf_data['success'] and 'chart_data' in perf_data['data']['objects']:
        # Get chart data from fetched content
        chart_dataset = perf_data['data']['objects']['chart_data']
        valuetext = perf_data['data']['objects']['valuetext']

    # JSON data required for phantomJS request inline variable
    data_json = {
        'type': 'json',
        'chart': {
            'width': CHART_WIDTH,
            'height': CHART_HEIGHT
        },
        'credits': {
            'enabled': False
        },
        'legend':{
            'itemDistance' : 15,
            'itemMarginBottom' : 5,
            'borderColor' : '#FFFFFF',
            'borderWidth' : "1",
            'borderRadius' : "8",
            'itemStyle': {
                'color': '#FFFFFF',
                'fontSize' : '12px'
            }
        },
        'title': {
            'text': ''
        },
        'yAxis': {
            'title' : {
                'text' : valuetext
            }
        },
        'xAxis': {
            'title': {
                'text': 'Time'
            },
            'type': 'datetime',
            'minRange': '3600000',
            'dateTimeLabelFormats': {
                'millisecond': '%H:%M:%S.%L',
                'second': '%H:%M:%S',
                'minute': '%H:%M',
                'hour': '%H:%M',
                'day': '%e. %b',
                'week': '%e. %b',
                'month': '%b %y',
                'year': '%Y'
            }
        },
        'series': chart_dataset
    }

    infile_str = {
        'infile': json.dumps(data_json),
        'options': json.dumps(data_json),
        'globaloptions': json.dumps({'global': {'useUTC': False}}),
        'type': CHART_IMG_TYPE,
        'constr': 'Chart',
        'scale': '1'
    }

    # Create PhantomJS url to hit POST request on it
    phantom_url = PHANTOM_PROTOCOL + "://" + PHANTOM_HOST + ":" + PHANTOM_PORT + "/"

    # Start PhantomJS server in background
    # os.system("phantomjs " + HIGHCHARTS_CONVERT_JS + " -host " + PHANTOM_HOST + " -port " + PHANTOM_PORT + "&")

    # Make POST request to phantom js host to create the chart image
    chart_img_request = requests.post(phantom_url, data=json.dumps(infile_str))

    # if directory for perf chart img didn't exist than create it
    chart_img_path = MEDIA_ROOT + 'uploaded/perf_chart'
    if not os.path.exists(chart_img_path):
        os.makedirs(chart_img_path)

    timestamp = time.time()
    full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S')

    # created filename
    filename = "{}_{}_{}".format("chart", full_time, device_id)

    fh = open(chart_img_path + "/" + filename + "." + infile_str['type'], "wb")
    fh.write(chart_img_request.content.decode('base64'))
    fh.close()

    result = {
        "chart_url": chart_img_path + "/" + filename + "." + infile_str['type']
    }

    return result


def dataTableOrdering(self_instance, qs, order_columns):
    """ 
     Get parameters from the request and prepare order by clause
    :param order_columns:
    :param self_instance:
    :param qs:
    """
    request = self_instance.request
    # Number of columns that are used in sorting
    try:
        i_sorting_cols = int(request.REQUEST.get('iSortingCols', 0))
    except Exception:
        i_sorting_cols = 0

    order = []

    for i in range(i_sorting_cols):
        # sorting column
        try:
            i_sort_col = int(request.REQUEST.get('iSortCol_%s' % i))
        except Exception:
            i_sort_col = 0
        # sorting order
        s_sort_dir = request.REQUEST.get('sSortDir_%s' % i)

        sdir = '-' if s_sort_dir == 'desc' else ''

        sortcol = order_columns[i_sort_col]
        if isinstance(sortcol, list):
            for sc in sortcol:
                order.append('%s%s' % (sdir, sc))
        else:
            order.append('%s%s' % (sdir, sortcol))
    if order:
        key_name = order[0][1:] if '-' in order[0] else order[0]
        sorted_device_data = sorted(qs, key=itemgetter(key_name), reverse=True if '-' in order[0] else False)
        return sorted_device_data

    return qs


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_PERFORMANCE', 300))
def get_multiprocessing_performance_data(q, device_list, machine, model):
    """
    Consolidated Performance Data from the Data base.
    - for distributed performance collection
    - function to accept machine wise device list and 
      fetch result from the desired machine
    - max processes = 7 (number of total machines)
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
                   "age": "N/A"
                   }

    query = prepare_row_query(table_name="performance_networkstatus",
                              devices=device_list,
                              )
    # (query)
    performance_data = nocout_utils.fetch_raw_result(query=query, machine=machine)  # model.objects.raw(query).using(alias=machine)

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
            # ).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)")

            perf_result["age"] = datetime.datetime.fromtimestamp(
                float(data["age"])
            ).strftime(DATE_TIME_FORMAT) if data["age"] else ""
            # ).strftime("%m/%d/%y (%b) %H:%M:%S") if data["age"] else ""

            device_result[device] = perf_result
    # (device_result)
    try:
        q.put(device_result)

    except Exception as e:
        log.exception(e.message)

def get_se_to_pe_min_latency(device_id=0, page_type='network'):
    """
    This method is for getting device's SE to PE min latency
    :param device_id: id of device
    :param page_type: Type of page i.e. 'Network', 'Customer'
    :return: min_latency(SE TO PE Min. latency of device)
    """
    if not device_id:
        return 'NA'

    if page_type == 'network':
        try:
            pe_device = Sector.objects.get(
                    sector_configured_on_id=device_id
                ).base_station.backhaul.pe_ip
        except Exception, e:
            return 'NA'
    elif page_type == 'customer':
        try:
            pe_device = Circuit.objects.get(
                    sub_station__device_id=device_id
                ).sector.base_station.backhaul.pe_ip
        except Exception, e:
            return 'NA'
    else:
        pass

    try:
        # Reason of using 'filter' instead of 'get' : 
        # Using(db_name) method doesn't work on model object
        # it only works on querysets
        min_latency = NetworkStatus.objects.filter(
            ip_address=pe_device.ip_address,
            data_source='rta',
            service_name='ping'
        ).using(
            pe_device.machine.name
        ).values_list(
            'min_value', flat=True
        )[0]
    except Exception, err:
        return 'NA'

    return min_latency

def get_ticket_numbers(device_ip_list=[], required_events=['Device_not_reachable']):
    """
    Function for getting ticket numbers for corresponding IP Address
    :param device_ip_list
    :return result_dict = {
        'IP Address': 'Ticket Number'
    }
    """
    # Result to be returned
    result_dict = {}

    if device_ip_list and required_events:
        alarms_qs = CurrentAlarms.objects.filter(
            eventname__in=required_events,
            ip_address__in=device_ip_list,
            is_active=1,
        ).using(
            TRAPS_DATABASE
        ).values(
            'ip_address',
            'ticket_number'
        )

        # Looping on alarms queryset to format resultant dict
        for alarm in alarms_qs:
            ip = alarm['ip_address']
            tkt_num = alarm['ticket_number']

            result_dict.update({ip: tkt_num})

    return result_dict


