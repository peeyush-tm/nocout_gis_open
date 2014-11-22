# -*- coding: utf-8 -*-
import csv
import json
import datetime
import time
from django.db.models import Count, Q
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.views.generic import ListView
from django.views.generic.base import View
from django_datatables_view.base_datatable_view import BaseDatatableView
import xlwt
from device.models import Device, City, State, DeviceType, DeviceTechnology
from inventory.models import SubStation, Circuit, Sector, BaseStation, Backhaul, Customer
from nocout.settings import P2P, WiMAX, PMP, DEBUG
from performance.models import PerformanceService, PerformanceNetwork, EventNetwork, EventService, NetworkStatus, ServiceStatus, InventoryStatus, \
    PerformanceStatus, PerformanceInventory, Status, NetworkAvailabilityDaily, Topology
from service.models import ServiceDataSource, Service, DeviceServiceConfiguration
from django.utils.dateformat import format
from operator import itemgetter
from nocout.utils.util import fetch_raw_result, dict_fetchall, \
    format_value, cache_for, \
    cached_all_gis_inventory, query_all_gis_inventory, query_all_gis_inventory_improved

from multiprocessing import Process, Queue

import logging

log = logging.getLogger(__name__)

SERVICE_DATA_SOURCE = {
    "uas": {
        "display_name": "UAS",
        "type": "area",
        "valuesuffix": "seconds",
        "valuetext": "Seconds",
        "formula": None
    },
    "rssi": {
        "display_name": "RSSI",
        "type": "column",
        "valuesuffix": "dB",
        "valuetext": "dB",
        "formula": None
    },
    "uptime": {
        "display_name": "UPTIME",
        "type": "line",
        "valuesuffix": " seconds",
        "valuetext": "up since (timeticks)",
        "formula": None
    },
    "rta": {
        "display_name": "Latency",
        "type": "area", "valuesuffix":
        "ms", "valuetext": "ms",
        "formula": None
    },
    "pl": {
        "display_name": "Packet Drop",
        "type": "column",
        "valuesuffix": "%",
        "valuetext": "Percentage (%)",
        "formula": None
    },
    "service_throughput": {
        "display_name": "Service throughput",
        "type": "area",
        "valuesuffix": " mbps",
        "valuetext": " mbps",
        "formula": None
    },
    "management_port_on_odu": {
        "display_name": "Management Port on ODU",
        "type": "area",
        "valuesuffix": " mbps",
        "valuetext": " mbps",
        "formula": None
    },
    "radio_interface": {
        "display_name": "Radio Interface" ,
        "type": "area",
        "valuesuffix": " mbps",
        "valuetext": " mbps",
        "formula": None
    },
    "availability": {
        "display_name": "Availability",
        "type": "column",
        "valuesuffix": " %",
        "valuetext": " %",
        "formula": None
    },
    ##listing there special performance checks with type string
    #wimax_ss_ip#ss_ip
    #wimax_modulation_dl_fec#modulation_dl_fec
    #wimax_ss_sector_id#ss_sector_id
    #wimax_ss_frequency#frequency
    #wimax_modulation_ul_fec#modulation_ul_fec
    #wimax_ul_intrf#ul_intrf
    #wimax_dl_intrf#dl_intrf
    #wimax_ss_mac#ss_mac
    ##listing there special performance checks with type string

    "ss_ip": {
        "display_name": "ss_ip",
        "type": "table",
        "valuesuffix": " ",
        "valuetext": " ",
        "formula": None
    },

    "modulation_dl_fec": {
        "display_name": "modulation_dl_fec",
        "type": "table",
        "valuesuffix": " ",
        "valuetext": " ",
        "formula": None
    },

    "ss_sector_id": {
        "display_name": "ss_sector_id",
        "type": "table",
        "valuesuffix": " ",
        "valuetext": " ",
        "formula": None
    },

    "frequency": {
        "display_name": "frequency",
        "type": "table",
        "valuesuffix": " MHz",
        "valuetext": " MHz",
        "formula": None
    },

    "modulation_ul_fec": {
        "display_name": "modulation_ul_fec",
        "type": "table",
        "valuesuffix": " ",
        "valuetext": " ",
        "formula": None
    },

    "ul_intrf": {
        "display_name": "ul_intrf",
        "type": "table",
        "valuesuffix": " ",
        "valuetext": " ",
        "formula": None
    },

    "dl_intrf": {
        "display_name": "dl_intrf",
        "type": "table",
        "valuesuffix": " ",
        "valuetext": " ",
        "formula": None
    },

    "ss_mac": {
        "display_name": "ss_mac",
        "type": "table",
        "valuesuffix": " ",
        "valuetext": " ",
        "formula": None
    },


}

SERVICES = {

}

# def uptime_to_days(uptime=0):
#     if uptime:
#         ret_val = int(float(uptime)/(60 * 60 * 2``))
#         return ret_val if ret_val > 0 else int(float(uptime)/(60 * 60))

class Live_Performance(ListView):
    """
    A generic class view for the performance view

    """
    model = NetworkStatus
    template_name = 'performance/live_perf.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """
        context = super(Live_Performance, self).get_context_data(**kwargs)
        page_type = self.kwargs['page_type']
        if page_type in ["customer"]:
            datatable_headers = [
                # {'mData': 'site_instance', 'sTitle': 'Site ID', 'Width': 'null', 'bSortable': False},
                {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
                {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                # {'mData': 'device_name', 'sTitle': 'Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                {'mData': 'device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                # {'mData': 'device_alias', 'sTitle': 'Alias', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                # {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                {'mData': 'bs_name', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'circuit_id', 'sTitle': 'Circuit IDs', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'customer_name', 'sTitle': 'Customer Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                # {'mData': 'sector_id', 'sTitle': 'Sector IDs', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                {'mData': 'city', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'state', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'packet_loss', 'sTitle': 'Packet Loss', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'latency', 'sTitle': 'Latency', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'last_updated', 'sTitle': 'Last Updated Time', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'age', 'sTitle': 'Age', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False}
            ]
        elif page_type in ["network"]:
            datatable_headers = [
                # {'mData': 'site_instance', 'sTitle': 'Site ID', 'Width': 'null', 'bSortable': False},
                {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
                {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                # {'mData': 'device_name', 'sTitle': 'Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                {'mData': 'device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                # {'mData': 'device_alias', 'sTitle': 'Alias', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                # {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                {'mData': 'bs_name', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                # {'mData': 'circuit_id', 'sTitle': 'Circuit IDs', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                {'mData': 'sector_id', 'sTitle': 'Sector IDs', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'city', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'state', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'packet_loss', 'sTitle': 'Packet Loss', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'latency', 'sTitle': 'Latency', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'last_updated', 'sTitle': 'Last Updated Time', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'age', 'sTitle': 'Age', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False}
            ]
        else:
            datatable_headers = [
                # {'mData': 'site_instance', 'sTitle': 'Site ID', 'Width': 'null', 'bSortable': False},
                {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
                {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                # {'mData': 'device_name', 'sTitle': 'Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                {'mData': 'device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                # {'mData': 'device_alias', 'sTitle': 'Alias', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                # {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': False},
                {'mData': 'bs_name', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'city', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'state', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'packet_loss', 'sTitle': 'Packet Loss', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'latency', 'sTitle': 'Latency', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'last_updated', 'sTitle': 'Last Updated Time', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'age', 'sTitle': 'Age', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
                {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False}
            ]

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['page_type'] = page_type
        return context


class LivePerformanceListing(BaseDatatableView):
    """
    A generic class based view for the performance data table rendering.

    """
    model = NetworkStatus
    is_ordered = False
    is_polled = False
    is_searched = False
    is_initialised = True

    columns = ['id',
               'ip_address',
               'device_technology',
               'device_type',
               'bs_name',
               'city',
               'state',
               'packet_loss',
               'latency',
               'last_updated',
               'age'
    ]
    polled_columns = [
        'packet_loss',
       'latency',
       'last_updated',
       'age'
    ]

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        else:
            if self.request.user.userprofile.role.values_list('role_name', flat=True)[0] == 'admin':
                organizations = list(self.request.user.userprofile.organization.get_descendants(include_self=True))
            else:
                organizations = [self.request.user.userprofile.organization]

            return self.get_initial_query_set_data(organizations=organizations)

    def get_initial_query_set_data(self, **kwargs):
        """
        Generic function required to fetch the initial data with respect to the page_type parameter in the get request requested.

        :param device_association:
        :param kwargs:
        :return: list of devices
        """

        page_type = self.request.GET.get('page_type')

        required_value_list = ['id','machine__name','device_name','ip_address']

        device_tab_technology = self.request.GET.get('data_tab')

        devices = filter_devices(organizations=kwargs['organizations'],
                                 data_tab=device_tab_technology,
                                 page_type=page_type,
                                 required_value_list=required_value_list
        )

        return devices

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return result_list:
        """

        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            if len(sSearch) > 3:
                self.is_initialised = False
                self.is_searched = True
                search_data = self.prepare_devices(qs)
                result_list = list()
                for dictionary in search_data:
                    x = json.dumps(dictionary)
                    dictionary = json.loads(x)
                    for dict in dictionary:
                        if dictionary[dict]:
                            if (isinstance(dictionary[dict], unicode) or isinstance(dictionary[dict], str)) and (
                                dictionary not in result_list
                            ):
                                if sSearch.encode('utf-8').lower() in dictionary[dict].encode('utf-8').lower():
                                    result_list.append(dictionary)
                            else:
                                if sSearch == dictionary[dict] and dictionary not in result_list:
                                    result_list.append(dictionary)

                return result_list
            else:
                self.is_searched = False
        return qs

    def ordering(self, qs):
        """
        sorting for the table
        """
        request = self.request

        page_type = request.GET['page_type']
        

        if page_type == 'customer':
            columns = ['id',
               'ip_address',
               'device_technology',
               'device_type',
               'bs_name',
               'circuit_id',
               'customer_name',
               'city',
               'state',
               'packet_loss',
               'latency',
               'last_updated',
               'age'
            ]
        elif page_type == 'network':
            columns = ['id',
               'ip_address',
               'device_technology',
               'device_type',
               'bs_name',
               'sector_id',
               'city',
               'state',
               'packet_loss',
               'latency',
               'last_updated',
               'age'
            ]
        else:
            columns = ['id',
               'ip_address',
               'device_technology',
               'device_type',
               'bs_name',
               'city',
               'state',
               'packet_loss',
               'latency',
               'last_updated',
               'age'
            ]

        i_sort_col = 0

        # Number of columns that are used in sorting
        try:
            i_sorting_cols = int(request.REQUEST.get('iSortingCols', 0))
        except ValueError:
            i_sorting_cols = 0

        reverse = True

        for i in range(i_sorting_cols):
            # sorting column
            try:
                i_sort_col = int(request.REQUEST.get('iSortCol_%s' % i))
            except ValueError:
                i_sort_col = 0
            # sorting order
            s_sort_dir = request.REQUEST.get('sSortDir_%s' % i)

            reverse = True if s_sort_dir == 'desc' else False

        if i_sorting_cols and i_sort_col:
            self.is_initialised = False
            self.is_ordered = True
            sort_data = self.prepare_devices(qs)
            try:
                sort_using = columns[i_sort_col]
                if sort_using in self.polled_columns:
                    self.is_polled = True
                    ##now we need to poll the devices
                    ##here we can limit the number of devices in query
                    ##to get the data from
                    ##that needs to be per machine basis
                    ##once we have the results
                    ##we can quickly call upon prepare_devices
                    machines = self.prepare_machines(sort_data)
                    #preparing the polled results
                    result_qs = self.prepare_polled_results(sort_data, multi_proc=False, machine_dict=machines)
                    sort_data = result_qs
                else:
                    self.is_polled = False
                sorted_qs = sorted(sort_data, key=itemgetter(sort_using), reverse=reverse)
                return sorted_qs

            except Exception as nocolumn:
                self.is_initialised = True
                self.is_ordered = False
                self.is_polled = False

        else:
            self.is_initialised = True
            self.is_ordered = False
            self.is_polled = False
            return qs

    def prepare_devices(self,qs):
        """

        :param device_list:
        :return:
        """
        if DEBUG:
            log.debug("preparing devices")
        page_type = self.request.GET['page_type']
        return prepare_gis_devices(qs, page_type)

    def prepare_machines(self, qs):
        """
        """
        if DEBUG:
            log.debug("preparing machines")
        device_list = []
        for device in qs:
            device_list.append(
                {
                    'device_name': device['device_name'],
                    'device_machine': device['machine_name'],
                    'id': device['id'],
                    'ip_address': device['ip_address']
                }
            )

        return prepare_machines(device_list)

    def prepare_polled_results(self, qs, multi_proc=False, machine_dict={}):
        """
        preparing polled results
        after creating static inventory first
        """
        if DEBUG:
            log.debug("preparing polled results")
        result_qs = polled_results(qs=qs,
                                   multi_proc=multi_proc,
                                   machine_dict=machine_dict,
                                   model_is=self.model
        )
        return result_qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if DEBUG:
            log.debug("preparing final result")
        page_type = self.request.GET['page_type']
        if qs:
            for dct in qs:
                # device = Device.objects.get(id=dct['id'])
                if page_type in ["customer", "network"]:
                    dct.update(
                        actions='<a href="/performance/{0}_live/{1}/" title="Device Performance"><i class="fa fa-bar-chart-o text-info"></i></a>\
                        <a href="/alert_center/{0}/device/{1}/service_tab/{2}/" title="Device Alert"><i class="fa fa-warning text-warning"></i></a> \
                        <a href="/device/{1}" title="Device Inventory"><i class="fa fa-dropbox text-muted" ></i></a>'
                        .format(page_type,
                                dct['id'],
                                'ping')
                    )
                else:
                    dct.update(
                        actions='<a href="/performance/{0}_live/{1}/" title="Device Performance"><i class="fa fa-bar-chart-o text-info"></i></a>\
                        <a href="/device/{1}" title="Device Inventory"><i class="fa fa-dropbox text-muted" ></i></a>'
                        .format(page_type,
                                dct['id']
                        )
                    )

        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request

        page_type = self.request.GET['page_type']

        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        #check if this has just initialised
        #if so : process the results
        qs = self.ordering(qs)
        qs = self.paging(qs)
        ##check if this has been searched
        ## if this has been seached
        ## dont call prepare_devices

        if self.is_initialised and not (self.is_searched or self.is_ordered):
            #prepare devices with GIS information
            qs = self.prepare_devices(qs=qs)
            #end prepare devices with GIS information

        if not self.is_polled:
            #preparing machine list
            machines = self.prepare_machines(qs)
            #preparing the polled results
            qs = self.prepare_polled_results(qs, multi_proc=True, machine_dict=machines)

        # if the qs is empty then JSON is unable to serialize the empty
        # ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


@cache_for(300)
def prepare_machines(device_list):
    """

    :return:
    """
    # Unique machine from the device_list
    unique_device_machine_list = {device['device_machine']: True for device in device_list}.keys()

    machine_dict = {}
    #Creating the machine as a key and device_name as a list for that machine.
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device['device_name'] for device in device_list if
                                 device['device_machine'] == machine]

    return machine_dict


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


def map_results(perf_result, qs):
    """
    """
    st = datetime.datetime.now()
    if DEBUG:
        if DEBUG:
            log.debug("MAP RESULTS : Start")
            log.debug("START %s" %st)

    result_qs = qs
    performance = perf_result
    processed = []
    for dct in result_qs:
        device_name = dct["device_name"]
        if device_name not in processed:
            processed.append(device_name)
            for perf in performance:
                try:
                    result = perf[device_name]
                    try:
                        dct["packet_loss"] = float(result["packet_loss"])
                        dct["latency"] = float(result["latency"])
                    except Exception as e:
                        dct["packet_loss"] = result["packet_loss"]
                        dct["latency"] = result["latency"]
                    dct["last_updated"] = result["last_updated"]
                    dct["age"] = result["age"]
                except:
                    continue

    if DEBUG:
        endtime = datetime.datetime.now()
        elapsed = endtime - st
        log.debug("MAPPING END {}".format(divmod(elapsed.total_seconds(), 60)))
        log.debug("MAP RESULTS  : RETURN")
    return result_qs


class Get_Perfomance(View):
    """
    The Class based View to get performance page for the single device.

    """

    def get(self, request, page_type="no_page", device_id=0):

        device = Device.objects.get(id=device_id)
        device_technology = DeviceTechnology.objects.get(id=device.device_technology).name
        realdevice = device

        """
            TODO START :- Replace below code by calling alert_center's 'SingleDeviceAlertDetails' class
        """
        start_date= self.request.GET.get('start_date','')
        end_date= self.request.GET.get('end_date','')
        isSet = False

        date_format = "%d-%m-%Y %H:%M:%S"

        if len(start_date) and len(end_date) and 'undefined' not in [start_date, end_date]:
            try:
                start_date = float(start_date)
                end_date = float(end_date)
            except Exception, e:
                start_date_object= datetime.datetime.strptime(start_date, date_format)
                end_date_object= datetime.datetime.strptime(end_date, date_format)
                start_date= format( start_date_object, 'U')
                end_date= format( end_date_object, 'U')
        else:
            # The end date is the end limit we need to make query till.
            end_date_object = datetime.datetime.now()
            # The start date is the last monday of the week we need to calculate from.
            start_date_object = end_date_object - datetime.timedelta(days=end_date_object.weekday())
            # Replacing the time, to start with the 00:00:00 of the last monday obtained.
            start_date_object = start_date_object.replace(hour=00, minute=00, second=00, microsecond=00)
            # Converting the date to epoch time or Unix Timestamp
            end_date = format(end_date_object, 'U')
            start_date = format(start_date_object, 'U')
            isSet = True

        sia_data_list = None
        error_data_list = None

        required_columns = ["device_name",
            "ip_address",
            "service_name",
            "data_source",
            "severity",
            "current_value",
            "sys_timestamp",
            "description"
        ]

        sia_data_list = EventService.objects. \
            filter(device_name=device.device_name,
                   sys_timestamp__gte=start_date,
                   sys_timestamp__lte=end_date). \
            order_by("-sys_timestamp"). \
            values(*required_columns).using(alias=device.machine.name)

        for data in sia_data_list:
            # data["alert_date"] = datetime.datetime. \
            #     fromtimestamp(float(data["sys_timestamp"])). \
            #     strftime("%d/%B/%Y")
            # data["alert_time"] = datetime.datetime. \
            #     fromtimestamp(float(data["sys_timestamp"])). \
            #     strftime("%I:%M %p")
            data["alert_date_time"] = datetime.datetime. \
                fromtimestamp(float(data["sys_timestamp"])). \
                strftime("%d/%B/%Y %I:%M %p")
                
            del (data["sys_timestamp"])

        
        in_string = lambda x: "'" + str(x) + "'"
        col_string = lambda x: "`" + str(x) + "`"
        is_ping = True
        # raw query is required here so as to get data
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
                device.device_name,
                start_date,
                end_date
                )
        error_data_list = fetch_raw_result(query, device.machine.name)

        for data in error_data_list:
            # data["alert_date"] = datetime.datetime. \
            #     fromtimestamp(float(data["sys_timestamp"])). \
            #     strftime("%d/%B/%Y")
            # data["alert_time"] = datetime.datetime. \
            #     fromtimestamp(float(data["sys_timestamp"])). \
            #     strftime("%I:%M %p")
            data["alert_date_time"] = datetime.datetime. \
                fromtimestamp(float(data["sys_timestamp"])). \
                strftime("%d/%B/%Y %I:%M %p")
                
            del (data["sys_timestamp"])

        """
            TODO END
        """

        page_data = {
            'page_title': page_type.capitalize(),
            'device_technology' : device_technology,
            'device': device,
            'realdevice': realdevice,
            'get_devices_url': 'performance/get_inventory_devices/' + page_type,
            'get_status_url':  'performance/get_inventory_device_status/' + page_type + '/device/' + str(device_id),
            'get_services_url': 'performance/get_inventory_service_data_sources/device/' + str(
                device_id),
            'page_type':page_type,
            'error_data' : error_data_list,
            'sia_data' : sia_data_list
            }

        return render(request, 'performance/single_device_perf.html', page_data)


class Performance_Dashboard(View):
    """
    The Class based View to get performance dashboard page requested.

    """

    def get(self, request):
        """
        Handles the get request

        :param request:
        :return Http response object:
        """
        return render_to_response('home/home.html')


class Sector_Dashboard(View):
    """
    The Class based view to get sector dashboard page requested.

    """

    def get(self, request):
        """
        Handles the get request

        :param request:
        :return Http response object:
        """

        return render(request, 'home/home.html')


class Fetch_Inventory_Devices(View):
    """
    The Generic Class Based View to fetch the inventory devices with respect to page_type resquested.

    """

    def get(self, request, page_type=None):
        """
        Handles the get request

        :param request:
        :param page_type:
        :return Http response object:
        """

        result = {
            'success': 0,
            'message': 'Substation Devices Not Fetched Successfully.',
            'data': {
                'meta': {},
                'objects': []
            }
        }

        logged_in_user = request.user.userprofile

        if 'admin' in logged_in_user.role.values_list('role_name', flat=True):
            organizations = list(logged_in_user.organization.get_descendants(include_self=True))
        else:
            organizations = [logged_in_user.organization]

        result['data']['objects'] += self.get_result(page_type, organizations)

        result['success'] = 1
        result['message'] = 'Substation Devices Fetched Successfully.'
        return HttpResponse(json.dumps(result))

    def get_result(self, page_type, organizations):
        """
        Generic function to return the result w.r.t the page_type and organization of the current logged in user.

        :param page_type:
        :param organization:
        return result
        """
        device_list = []

        if page_type == "customer":
            device_list = organization_customer_devices(organizations)

        elif page_type == "network":
            device_list = organization_network_devices(organizations)

        elif page_type == 'other':
            device_list = organization_backhaul_devices(organizations)

        result = list()
        for device in device_list:
            result.append({'id': device.id,
                           'alias': device.device_alias,
                           'technology': DeviceTechnology.objects.get(id=device.device_technology).name }
        )
        return result


class Inventory_Device_Status(View):
    """
    Class Based Generic view to return a Single Device Status

    """

    def get(self, request, page_type, device_id):
        """
        Handles the Get Request to return a single device status w.r.t page_type and device id requested.

        """
        result = {
            'success': 0,
            'message': 'Inventory Device Status Not Fetched Successfully.',
            'data': {
                'meta': {},
                'objects': {}
            }
        }
        result['data']['objects']['values'] = list()

        customer_name = ''

        device = Device.objects.get(id=device_id)
        technology = DeviceTechnology.objects.get(id=device.device_technology)
        type = DeviceType.objects.get(id=device.device_type)

        if device.sector_configured_on.exists():
            if technology.name in ['P2P','PTP','ptp','p2p']:
                result['data']['objects']['headers'] = ['BS Name',
                                                    'Customer Name',
                                                    'Technology',
                                                    'Type',
                                                    'City',
                                                    'State',
                                                    'IP Address',
                                                    'MAC Address',
                                                    'Planned Frequency'
                ]
            else:
                result['data']['objects']['headers'] = ['BS Name',
                                                    'Sector ID',
                                                    'PMP Port',
                                                    'Technology',
                                                    'Type',
                                                    'City',
                                                    'State',
                                                    'IP Address',
                                                    'MAC Address',
                                                    'Planned Frequency'
                ]
            result['data']['objects']['values'] = []
            sector_objects = Sector.objects.filter(sector_configured_on=device.id)
            sector_id = 'N/A'
            pmp_port = 'N/A'
            for sector in sector_objects:
                base_station = sector.base_station
                planned_frequency = [sector.frequency.value] if sector.frequency else ["N/A"]
                planned_frequency = ",".join(planned_frequency)
                if technology.name in ['P2P','PTP','ptp','p2p']:
                    try:
                        circuits = sector.circuit_set.get()
                        customer_name = circuits.customer.alias
                    except Exception as no_circuit:
                        log.exception(no_circuit)
                else:
                    sector_id = sector.sector_id
                try:
                    pmp_port = sector.sector_configured_on_port.alias
                except Exception as no_port:
                    log.exception(no_port)
                try:
                    city_name = City.objects.get(id=base_station.city).city_name\
                                                            if base_station.city\
                                                            else "N/A"
                except Exception as no_city:
                    city_name = "N/A"
                try:
                    state_name = State.objects.get(id=base_station.state).state_name\
                                                            if base_station.state\
                                                            else "N/A"
                except Exception as no_state:
                    state_name = "N/A"
                if technology.name in ['P2P','PTP','ptp','p2p']:
                    result['data']['objects']['values'].append([base_station.alias,
                                                        customer_name,
                                                       technology.alias,
                                                       type.alias,
                                                       city_name,
                                                       state_name,
                                                       device.ip_address,
                                                       device.mac_address,
                                                       planned_frequency
                ])
                else:
                    result['data']['objects']['values'].append([base_station.alias,
                                                        sector_id,
                                                        pmp_port,
                                                       technology.alias,
                                                       type.alias,
                                                       city_name,
                                                       state_name,
                                                       device.ip_address,
                                                       device.mac_address,
                                                       planned_frequency
                ])

        elif device.substation_set.exists():
            result['data']['objects']['headers'] = ['BS Name',
                                                    'SS Name',
                                                    'Circuit ID',
                                                    'Customer Name',
                                                    'Technology',
                                                    'Building Height',
                                                    'Tower Height',
                                                    'City',
                                                    'State',
                                                    'IP Address',
                                                    'MAC Address',
                                                    'Planned Frequency'
            ]
            result['data']['objects']['values'] = []
            substation_objects = device.substation_set.filter()
            if len(substation_objects):
                substation = substation_objects[0]
                customer_name = "N/A"
                if substation.circuit_set.exists():
                    customer_id = Circuit.objects.filter(sub_station_id=substation.id).values('customer_id')
                    customer_name = Customer.objects.filter(id=customer_id[0]["customer_id"])
                    circuit = substation.circuit_set.get()
                    # customer_name = Customer.objects.filter(id=circuit.customer_id)
                    sector = circuit.sector
                    base_station = sector.base_station

                    planned_frequency = [sector.frequency.value] if sector.frequency else ["N/A"]
                    planned_frequency = ",".join(planned_frequency)

                    try:
                        city_name = City.objects.get(id=base_station.city).city_name\
                                                            if base_station.city\
                                                            else "N/A"
                    except Exception as no_city:
                        city_name = "N/A"
                    try:
                        state_name = State.objects.get(id=base_station.state).state_name\
                                                            if base_station.state\
                                                            else "N/A"
                    except Exception as no_state:
                        state_name = "N/A"
                    result['data']['objects']['values'].append([base_station.alias,
                                                           substation.alias,
                                                           circuit.circuit_id,
                                                           customer_name[0].alias,
                                                           technology.alias,
                                                           substation.building_height,
                                                           substation.tower_height,
                                                           city_name,
                                                           state_name,
                                                           device.ip_address,
                                                           device.mac_address,
                                                           planned_frequency
                    ])

        result['success'] = 1
        result['message'] = 'Inventory Device Status Fetched Successfully.'
        return HttpResponse(json.dumps(result))


class Inventory_Device_Service_Data_Source(View):
    """
    Generic Class based View for to fetch Inventory Device Service Data Source.

    """

    def get(self, request, device_id):
        """
        Handles the get Request w.r.t to the page type and device id requested

        :params request object:
        :params device_id:
        :return result
        """

        result = {
            'success': 0,
            'message': 'Services Data Source Not Fetched Successfully.',
            'data': {
                'meta': {},
                'objects': {
                    'network_perf_tab': {
                        "info" : [],
                        "isActive" : 1
                    },
                    'service_status_tab': {
                        "info" : [],
                        "isActive" : 0
                    },
                    'inventory_status_tab': {
                        "info" : [],
                        "isActive" : 0
                    },
                    'service_perf_tab': {
                        "info" : [],
                        "isActive" : 0
                    },
                    'availability_tab': {
                        "info" : [],
                        "isActive" : 0
                    },
                    'topology_tab': {
                        "info" : [],
                        "isActive" : 0
                    }
                }
            }
        }
        device= Device.objects.get(id=device_id)
        device_type = DeviceType.objects.get(id=device.device_type)

        #if there is no service present in the configuration (BULK SYNC)
        inventory_device_service_name = device_type.service.filter().values_list('name', 'service_data_sources__name')

        #
        # #Fetch the Service names that are configured w.r.t to a device.
        # inventory_device_service_name = DeviceServiceConfiguration.objects.filter(
        #     device_name= device.device_name)\
        #     .values_list('service_name', 'data_source')

        configured_services = DeviceServiceConfiguration.objects.filter(
                                device_name= device.device_name)\
                                .values_list('service_name', 'data_source')

        if len(configured_services):
            inventory_device_service_name = configured_services

        # TODO:to remove this code as the services are getting multi added with their port.
        inventory_device_service_name = list(set(inventory_device_service_name))

        result['data']['objects']['network_perf_tab']["info"].append(
            {
                'name': "rta",
                'title': "Latency",
                'url': 'performance/service/ping/service_data_source/rta/device/' + str(device_id),
                'active': 0,
                'service_type_tab': 'network_perf_tab'
            })
        result['data']['objects']['network_perf_tab']["info"].append(
            {
                'name': "pl",
                'title': "Packet Drop",
                'url': 'performance/service/ping/service_data_source/pl/device/' + str(device_id),
                'active': 0,
                'service_type_tab': 'network_perf_tab'
            })

        for (service_name, service_data_source) in inventory_device_service_name:
            if '_status' in service_name:
                # service_data_sources = Service.objects.get(name=service_name).service_data_sources.all()
                # for service_data_source in service_data_sources:
                result['data']['objects']['service_status_tab']["info"].append(
                    {
                        'name': service_data_source,
                        'title': Service.objects.get(name=service_name).alias.upper() +
                                 " : " +
                                 ServiceDataSource.objects.filter(name=service_data_source)[0].alias
                                    if len(ServiceDataSource.objects.filter(name=service_data_source)) else service_data_source,
                        'url': 'performance/service/' + service_name + '/service_data_source/' + service_data_source + '/device/' + str(
                            device_id),
                        'active': 0,
                    })

            elif '_invent' in service_name:
                # service_data_sources = Service.objects.get(name=service_name).service_data_sources.all()
                # for service_data_source in service_data_sources:
                result['data']['objects']['inventory_status_tab']["info"].append(
                    {
                        'name': service_data_source,
                        'title': Service.objects.get(name=service_name).alias.upper() +
                                 " : " +
                                 ServiceDataSource.objects.filter(name=service_data_source)[0].alias
                                    if len(ServiceDataSource.objects.filter(name=service_data_source)) else service_data_source,
                        'url': 'performance/service/' + service_name + '/service_data_source/' + service_data_source + '/device/' + str(
                            device_id),
                        'active': 0,
                    })
            else:
                # service_data_sources = Service.objects.get(name=service_name).service_data_sources.all()
                # for service_data_source in service_data_sources:
                result['data']['objects']['service_perf_tab']["info"].append(
                    {
                        'name': service_data_source,
                        'title': Service.objects.get(name=service_name).alias.upper() +
                                 " : " +
                                 ServiceDataSource.objects.filter(name=service_data_source)[0].alias
                                    if len(ServiceDataSource.objects.filter(name=service_data_source)) else service_data_source,
                        'url': 'performance/service/' + service_name + '/service_data_source/' + service_data_source + '/device/' + str(
                            device_id),
                        'active': 0,
                    })

        result['data']['objects']['availability_tab']["info"].append(
        {
            'name': 'availability',
            'title': 'Availability',
            'url': 'performance/service/availability/service_data_source/availability/device/' +
                   str(device_id),
            'active': 0,
        })

        result['data']['objects']['topology_tab']["info"].append(
        {
            'name': 'topology',
            'title': 'Topology',
            'url': 'performance/service/topology/service_data_source/topology/device/' +
                   str(device_id),
            'active': 0,
        })

        result['success'] = 1
        result['message'] = 'Substation Devices Services Data Source Fetched Successfully.'
        return HttpResponse(json.dumps(result))


class Get_Service_Type_Performance_Data(View):
    """
    Generic Class based View to Fetch the Performance Data.

    """

    def get(self, request, service_name, service_data_source_type, device_id):
        """
        Handles the get request to fetch performance data w.r.t to arguments requested.

        :params request object:
        :params service_name:
        :params service_data_source_type:
        :params device_id:
        :return result

        """
        self.result = {
            'success': 0,
            'message': 'No Data.',
            'data': {
                'meta': {},
                'objects': {}
            }
        }

        date_format = "%d-%m-%Y %H:%M:%S"

        device = Device.objects.get(id=int(device_id))
        inventory_device_name = device.device_name
        inventory_device_machine_name = device.machine.name  # Device Machine Name required in Query to fetch data.

        start_date= self.request.GET.get('start_date','')
        end_date= self.request.GET.get('end_date','')
        isSet = False

        if len(start_date) and len(end_date) and 'undefined' not in [start_date, end_date]:
            isSet = True
            try:
                start_date = float(start_date)
                end_date = float(end_date)
            except Exception, e:
                start_date_object= datetime.datetime.strptime(start_date, date_format)
                end_date_object= datetime.datetime.strptime(end_date, date_format)
                start_date= format( start_date_object, 'U')
                end_date= format( end_date_object, 'U')

        else:
            # The end date is the end limit we need to make query till.
            end_date_object = datetime.datetime.now()
            # The start date is the last monday of the week we need to calculate from.
            start_date_object = end_date_object - datetime.timedelta(days=end_date_object.weekday())
            # Replacing the time, to start with the 00:00:00 of the last monday obtained.
            start_date_object = start_date_object.replace(hour=00, minute=00, second=00, microsecond=00)
            # Converting the date to epoch time or Unix Timestamp
            end_date = format(end_date_object, 'U')
            start_date = format(start_date_object, 'U')


        if service_data_source_type in ['pl', 'rta']:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(minutes=-180), 'U')

            performance_data = PerformanceNetwork.objects.filter(device_name=inventory_device_name,
                                                                 service_name=service_name,
                                                                 data_source=service_data_source_type,
                                                                 sys_timestamp__gte=start_date,
                                                                 sys_timestamp__lte=end_date).using(
                                                                 alias=inventory_device_machine_name)

            result = self.get_performance_data_result(performance_data)

        elif "availability" in service_name or service_data_source_type in ['availability']:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(weeks=-1), 'U')
            performance_data = NetworkAvailabilityDaily.objects.filter(device_name=inventory_device_name,
                                                                 service_name=service_name,
                                                                 data_source=service_data_source_type,
                                                                 sys_timestamp__gte=start_date,
                                                                 sys_timestamp__lte=end_date).using(
                                                                 alias=inventory_device_machine_name)

            result = self.get_performance_data_result(performance_data, data_source="availability")

        elif "topology" in service_name or service_data_source_type in ['topology']:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(weeks=-1), 'U')
            performance_data = Topology.objects.filter(device_name=inventory_device_name,
                                                                 # service_name=service_name,
                                                                 data_source='topology',#service_data_source_type,
                                                                 sys_timestamp__gte=start_date,
                                                                 sys_timestamp__lte=end_date).using(
                                                                 alias=inventory_device_machine_name)

            result = self.get_topology_result(performance_data)


        elif '_status' in service_name:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(days=-1), 'U')
            performance_data = PerformanceStatus.objects.filter(device_name=inventory_device_name,
                                                                service_name=service_name,
                                                                data_source=service_data_source_type,
                                                                sys_timestamp__gte=start_date,
                                                                sys_timestamp__lte=end_date).using(
                                                                alias=inventory_device_machine_name)

            result = self.get_perf_table_result(performance_data)

        elif '_invent' in service_name:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(weeks=-1), 'U')
            performance_data = PerformanceInventory.objects.filter(device_name=inventory_device_name,
                                                                   service_name=service_name,
                                                                   data_source=service_data_source_type,
                                                                   sys_timestamp__gte= start_date,
                                                                   sys_timestamp__lte= end_date).using(
                                                                   alias=inventory_device_machine_name)

            result = self.get_perf_table_result(performance_data)
        else:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(minutes=-180), 'U')
            performance_data = PerformanceService.objects.filter(device_name=inventory_device_name,
                                                                 service_name=service_name,
                                                                 data_source=service_data_source_type,
                                                                 sys_timestamp__gte= start_date,
                                                                 sys_timestamp__lte= end_date).using(
                                                                 alias=inventory_device_machine_name)
            #to check of string based dashboards
            #need to return a table
            if service_data_source_type.lower() in SERVICE_DATA_SOURCE\
                and SERVICE_DATA_SOURCE[service_data_source_type.lower()]['type'] == 'table':
                result = self.get_perf_table_result(performance_data)

            else:
                result = self.get_performance_data_result(performance_data)

        download_excel= self.request.GET.get('download_excel', '')
        download_csv= self.request.GET.get('download_csv', '')

        if download_excel:

            table_data, table_header=self.return_table_header_and_table_data(service_name, result)
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('report')
            style = xlwt.XFStyle()

            borders = xlwt.Borders()
            borders.bottom = xlwt.Borders.DASHED
            style.borders = borders

            column_length= len(table_header)
            row_length= len(table_data) +1
            #Writing headers first for the excel file.
            for column in range(column_length):
                worksheet.write(0, column, table_header[column], style=style)
            #Writing rest of the rows.
            for row in range(1,row_length):
                for column in range(column_length):
                    worksheet.write(row, column, table_data[row-1][ table_header[column].lower() ], style=style)

            response= HttpResponse(mimetype= 'application/vnd.ms-excel', content_type='text/plain')
            start_date_string=start_date
            end_date_string=end_date
            response['Content-Disposition'] = 'attachment; filename=performance_report_{0}_{1}_to_{2}.xls'\
                .format( inventory_device_name, start_date_string, end_date_string )
            workbook.save(response)
            return response

        elif download_csv:

            table_data, table_header=self.return_table_header_and_table_data(service_name, result)
            response = HttpResponse(content_type='text/csv')
            start_date_string=start_date
            end_date_string=end_date
            response['Content-Disposition'] = 'attachment; filename="performance_report_{0}_{1}_to_{2}.xls"'\
                .format(inventory_device_name, start_date_string, end_date_string)

            writer = csv.writer(response)
            writer.writerow(table_header)
            column_length= len(table_header)
            row_length= len(table_data) +1

            for row in range(1, row_length):
                row_list= list()
                for column in range(0, column_length):
                    row_list.append(table_data[row-1][ table_header[column].lower() ])
                writer.writerow(row_list)
            return response

        else:
            return HttpResponse(json.dumps(result), mimetype="application/json")

    def return_table_header_and_table_data(self, service_name, result ):

        if '_invent' in service_name or  '_status' in service_name :
            table_data= result['data']['objects']['table_data']
            table_header= result['data']['objects']['table_data_header']

        else:
            table_data= result['data']['objects']['chart_data'][0]['data']
            table_header= ['Value','Date', 'Time' ]
            data_list=[]
            for data in table_data:
                data_list+= [{
                    'date': datetime.datetime.fromtimestamp(float(data['x']/1000)).strftime("%d/%B/%Y"),
                    'time': datetime.datetime.fromtimestamp(float(data['x']/1000)).strftime("%I:%M %p"),
                    'value':data['y'],
                    }]
            table_data=data_list
        return table_data, table_header


    def get_perf_table_result(self, performance_data):

        result_data, aggregate_data = list(), dict()
        for data in performance_data:
            temp_time = data.sys_timestamp

            if temp_time in aggregate_data:
                continue
            else:
                aggregate_data[temp_time] = data.sys_timestamp
                result_data.append({
                    'date': datetime.datetime.fromtimestamp(float(data.sys_timestamp)).strftime("%d/%B/%Y"),
                    'time': datetime.datetime.fromtimestamp(float(data.sys_timestamp)).strftime("%I:%M %p"),
                    'value': data.current_value,
                    })
        self.result['success'] = 1
        self.result[
            'message'] = 'Device Performance Data Fetched Successfully To Plot Table.' if result_data else 'No Record Found.'
        self.result['data']['objects']['table_data'] = result_data
        self.result['data']['objects']['table_data_header'] = ['date', 'time', 'value']
        return self.result

    def get_topology_result(self, performance_data):
        """
        Getting the current topology of any elements of the network
        """

        result_data, aggregate_data = list(), dict()
        for data in performance_data:
            temp_time = data.sys_timestamp
            connected_mac = data.connected_device_mac
            if connected_mac in aggregate_data:
                continue
            else:
                aggregate_data[connected_mac] = data.connected_device_mac
                result_data.append({
                        'device_name': data.device_name,
                        'ip_address': data.ip_address,
                        'mac_address': data.mac_address,
                        'sector_id': data.sector_id,
                        'connected_device_ip': data.connected_device_ip,
                        'connected_device_mac': data.connected_device_mac,
                        'date': datetime.datetime.fromtimestamp(float(data.sys_timestamp)).strftime("%d/%B/%Y"),
                        'time': datetime.datetime.fromtimestamp(float(data.sys_timestamp)).strftime("%I:%M %p")
                    })
        self.result['success'] = 1
        self.result['message'] = 'Device Data Fetched Successfully.' if result_data else 'No Record Found.'
        self.result['data']['objects']['table_data'] = result_data
        self.result['data']['objects']['table_data_header'] = ['device_name',
                                                               'ip_address',
                                                               'mac_address',
                                                               'sector_id',
                                                               'connected_device_ip',
                                                               'connected_device_mac',
                                                               'date',
                                                               'time'
        ]
        return self.result



    def get_performance_data_result(self, performance_data, data_source = None):
        chart_data = list()
        if performance_data:
            data_list, warn_data_list, crit_data_list, aggregate_data = list(), list(), list(), dict()
            for data in performance_data:
                temp_time = data.sys_timestamp

                if temp_time in aggregate_data:
                    continue
                else:
                    aggregate_data[temp_time] = data.sys_timestamp
                    self.result['data']['objects']['display_name'] = \
                        SERVICE_DATA_SOURCE[str(data.data_source).strip().lower()]["display_name"]\
                            if str(data.data_source).strip().lower() in SERVICE_DATA_SOURCE \
                            else str(data.data_source).upper()

                    self.result['data']['objects']['type'] = \
                        SERVICE_DATA_SOURCE[str(data.data_source).strip().lower()]["type"]\
                            if str(data.data_source).strip().lower() in SERVICE_DATA_SOURCE \
                            else "area"

                    self.result['data']['objects']['valuesuffix'] = \
                        SERVICE_DATA_SOURCE[str(data.data_source).strip().lower()]["valuesuffix"]\
                            if str(data.data_source).strip().lower() in SERVICE_DATA_SOURCE \
                            else ""

                    self.result['data']['objects']['valuetext'] = \
                        SERVICE_DATA_SOURCE[str(data.data_source).strip().lower()]["valuetext"]\
                            if str(data.data_source).strip().lower() in SERVICE_DATA_SOURCE \
                            else str(data.data_source).upper()

                    self.result['data']['objects']['plot_type'] = 'charts'
                    # data_list.append([data.sys_timestamp, data.current_value ])

                    # data_list.append([data.sys_timestamp*1000, float(data.current_value) if data.current_value else 0])
                    if data_source not in ["availability"]:
                        warn_data_list.append([data.sys_timestamp * 1000, float(data.warning_threshold)
                        if data.critical_threshold else None])

                        crit_data_list.append([data.sys_timestamp * 1000, float(data.critical_threshold)
                        if data.critical_threshold else None])

                        ###to draw each data point w.r.t threshold we would need to use the following

                        compare_point = lambda p1, p2, p3: '#70AFC4' \
                            if abs(p1) < abs(p2) \
                            else ('#FFE90D'
                                  if abs(p2) < abs(p1) < abs(p3)
                                  else ('#FF193B' if abs(p3) < abs(p1)
                                                else "#70AFC4"
                                        )
                                )

                        formula = SERVICE_DATA_SOURCE[str(data.data_source).lower().strip()]["formula"]\
                                    if str(data.data_source).lower().strip() in SERVICE_DATA_SOURCE \
                                    else None

                        if data.current_value:
                            formatter_data_point = {
                                "name": str(data.data_source).upper(),
                                "color": compare_point(float(data.current_value) if data.current_value else 0,
                                                       float(data.warning_threshold) if data.warning_threshold else 0,
                                                       float(data.critical_threshold) if data.critical_threshold else 0
                                ),
                                "y": eval(str(formula) + "(" +str(data.current_value) + ")")
                                        if formula
                                        else float(data.current_value),
                                "x": data.sys_timestamp * 1000
                            }
                        else:
                            formatter_data_point = {
                                "name": str(data.data_source).upper(),
                                "color": '#70AFC4',
                                "y": None,
                                "x": data.sys_timestamp * 1000
                            }

                        data_list.append(formatter_data_point)
                        chart_data = [{'name': self.result['data']['objects']['display_name'],
                                     'data': data_list,
                                     'type': self.result['data']['objects']['type'],
                                     'valuesuffix': self.result['data']['objects']['valuesuffix'],
                                     'valuetext': self.result['data']['objects']['valuetext']
                                    },
                                    {'name': str("warning threshold").title(),
                                     'color': '#FFE90D',
                                     'data': warn_data_list,
                                     'type': 'line',
                                     'marker' : {
                                         'enabled': False
                                     }
                                    },
                                    {'name': str("critical threshold").title(),
                                     'color': '#FF193B',
                                     'data': crit_data_list,
                                     'type': 'line',
                                     'marker' : {
                                         'enabled': False
                                     }
                        }]
                    else:
                        if data.current_value:
                            formatter_data_point = {
                                "name": "Availability",
                                "color": '#70AFC4',
                                "y": float(data.current_value),
                                "x": data.sys_timestamp * 1000
                            }
                            formatter_data_point_down = {
                                "name": "UnAvailability",
                                "color": '#FF193B',
                                "y": 100.00 - float(data.current_value),
                                "x": data.sys_timestamp * 1000
                            }
                        else:
                            formatter_data_point = {
                                "name": str(data.data_source).upper(),
                                "color": '#70AFC4',
                                "y": None,
                                "x": data.sys_timestamp * 1000
                            }
                            formatter_data_point_down = {
                                "name": "UnAvailability",
                                "color": '#FF193B',
                                "y": None,
                                "x": data.sys_timestamp * 1000
                            }

                        data_list.append(formatter_data_point)
                        warn_data_list.append(formatter_data_point_down)

                        chart_data = [{'name': 'Availability',
                                     'data': data_list,
                                     'type': self.result['data']['objects']['type'],
                                     'valuesuffix': self.result['data']['objects']['valuesuffix'],
                                     'valuetext': self.result['data']['objects']['valuetext']
                        },
                                      {'name': 'UnAvailability',
                                     'color': '#FF193B',
                                     'data': warn_data_list,
                                     'type': 'column',
                                     'marker' : {
                                         'enabled': False
                                     }}
                        ]


            #this ensures a further good presentation of data w.r.t thresholds

            self.result['success'] = 1
            self.result['message'] = 'Device Performance Data Fetched Successfully To Plot Graphs.'
            self.result['data']['objects']['chart_data'] = chart_data

        return self.result


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

#common function to get the devices
@cache_for(300)
def ptp_device_circuit_backhaul(specify_type='all'):
    """
    Special case fot PTP technology devices. Wherein Circuit type backhaul is required
    :return:
    """
    if specify_type == 'all':
        device_list_with_circuit_type_backhaul = Device.objects.filter(
            Q(id__in=Sector.objects.filter(id__in=Circuit.objects.filter(circuit_type__icontains="Backhaul").
                                            values_list('sector', flat=True)).
                                            values_list('sector_configured_on', flat=True))
            |
            Q(id__in=SubStation.objects.filter(id__in=Circuit.objects.filter(circuit_type__icontains="Backhaul").
                                            values_list('sub_station', flat=True)).
                                            values_list('device', flat=True))
        )
    elif specify_type == 'ss':
        device_list_with_circuit_type_backhaul = Device.objects.filter(
            Q(id__in=SubStation.objects.filter(id__in=Circuit.objects.filter(circuit_type__icontains="Backhaul").
                                            values_list('sub_station', flat=True)).
                                            values_list('device', flat=True))
        )
    elif specify_type == 'bs':
        device_list_with_circuit_type_backhaul = Device.objects.filter(
            Q(id__in=Sector.objects.filter(id__in=Circuit.objects.filter(circuit_type__icontains="Backhaul").
                                            values_list('sector', flat=True)).
                                            values_list('sector_configured_on', flat=True))
        )
    else:
        device_list_with_circuit_type_backhaul = []

    return device_list_with_circuit_type_backhaul


@cache_for(300)
def organization_customer_devices(organizations, technology = None, specify_ptp_type='all'):
    """
    To result back the all the customer devices from the respective organization..

    :param organization:
    :return list of customer devices
    """
    if not technology:
        organization_customer_devices= Device.objects.filter(
                                    Q(sector_configured_on__isnull=False) | Q(substation__isnull=False),
                                    is_added_to_nms=1,
                                    is_deleted=0,
                                    organization__in= organizations
        )
    else:
        if int(technology) == int(P2P.ID):
            if specify_ptp_type in ['ss','bs']:
                choose_ss_bs = None
                if specify_ptp_type == 'ss':
                    choose_ss_bs = Q(substation__isnull=False)
                else:
                    choose_ss_bs = Q(sector_configured_on__isnull=False)
                organization_customer_devices = Device.objects.filter(
                    ~Q(id__in=ptp_device_circuit_backhaul(specify_type=specify_ptp_type)),
                    choose_ss_bs,  #calls the specific set of devices
                    is_added_to_nms= 1,
                    is_deleted= 0,
                    organization__in= organizations,
                    device_technology= technology
                )
            else:
                organization_customer_devices = Device.objects.filter(
                    ~Q(id__in=ptp_device_circuit_backhaul()),
                    Q(substation__isnull=False)
                    |
                    Q(sector_configured_on__isnull=False),
                    is_added_to_nms= 1,
                    is_deleted= 0,
                    organization__in= organizations,
                    device_technology= technology
                )
        else:
            organization_customer_devices = Device.objects.filter(
                is_added_to_nms= 1,
                substation__isnull=False,
                is_deleted= 0,
                organization__in= organizations,
                device_technology= technology
            )

    return organization_customer_devices


@cache_for(300)
def organization_network_devices(organizations, technology = None, specify_ptp_bh_type='all'):
    """
    To result back the all the network devices from the respective organization..

    :param organizations:
    :param technology:
    :param organization:
    :return list of network devices
    """


    if not technology:
        organization_network_devices = Device.objects.filter(
                                        Q(id__in= ptp_device_circuit_backhaul())
                                        |
                                        Q(device_technology = int(WiMAX.ID))
                                        |
                                        Q(device_technology = int(PMP.ID)),
                                        is_added_to_nms=1,
                                        is_deleted=0,
                                        organization__in= organizations
        )
    else:
        if int(technology) == int(P2P.ID):
            if specify_ptp_bh_type in ['ss', 'bs']:
                organization_network_devices = Device.objects.filter(
                                            Q(id__in= ptp_device_circuit_backhaul(specify_type=specify_ptp_bh_type)),
                                            is_added_to_nms=1,
                                            is_deleted=0,
                                            organization__in= organizations
                )
            else:
                organization_network_devices = Device.objects.filter(
                                            Q(id__in= ptp_device_circuit_backhaul()),
                                            is_added_to_nms=1,
                                            is_deleted=0,
                                            organization__in= organizations
                )
        else:
            organization_network_devices = Device.objects.filter(
                                            device_technology = int(technology),
                                            is_added_to_nms=1,
                                            sector_configured_on__isnull = False,
                                            is_deleted=0,
                                            organization__in= organizations
            ).annotate(dcount=Count('id'))

    return organization_network_devices


@cache_for(300)
def organization_backhaul_devices(organizations, technology = None):
    """
    To result back the all the network devices from the respective organization..

    :param organizations:
    :param technology:
    :param organization:
    :return list of network devices
    """

    return  Device.objects.filter(
                                    backhaul__isnull=False,
                                    is_added_to_nms=1,
                                    is_deleted=0,
                                    organization__in= organizations
    )


@cache_for(300)
def filter_devices(organizations=[],
                   data_tab=None,
                   page_type="customer",
                   required_value_list=[]
                   ):

    """

    :param logged_in_user: authenticated user
    :param data_tab: the technology user wants to retrive
    :return: the list of devices that user has been assigned via organization
    """
    device_list = list()
    organization_devices = list()

    if len(required_value_list):
        device_value_list = required_value_list
    else:
        device_value_list = ['id','machine__name','device_name','ip_address']

    device_tab_technology = data_tab ##
    device_technology_id = None
    try:
        device_technology_id = DeviceTechnology.objects.get(name=device_tab_technology).id
    except Exception as e:
        log.exception("Backhaul Device Filter %s" %(e.message))

    if page_type == "customer":
        device_list = organization_customer_devices(organizations, device_technology_id
        ).values(*device_value_list)
    elif page_type == "network":
        device_list = organization_network_devices(organizations, device_technology_id
        ).values(*device_value_list)
    elif page_type == "other":
        device_list = organization_backhaul_devices(organizations).values(*device_value_list)
    else:
        device_list = []
    # get the devices in an organisation which are added for monitoring
    organization_devices = [
        {
            'device_name': device['device_name'],
            'machine_name': device['machine__name'],
            'id': device['id'],
            'ip_address': device['ip_address']
        }
        for device in device_list
    ]

    return organization_devices


@cache_for(300)
def indexed_gis_devices(indexed="SECTOR_CONF_ON_ID"):
    """

    :return:
    """

    raw_results = cached_all_gis_inventory(query_all_gis_inventory(monitored_only=True))

    indexed_raw_results = {}

    for result in raw_results:
        defined_index = result[indexed]
        if defined_index not in indexed_raw_results:
            indexed_raw_results[defined_index] = []
        indexed_raw_results[defined_index].append(result)

    return indexed_raw_results


@cache_for(300)
def combined_indexed_gis_devices(indexes):
    """
    indexes={'sector':'SECTOR_CONF_ON_NAME','ss':'SSDEVICENAME','bh':'BHCONF'}
    :return:
    """
    st = datetime.datetime.now()

    if DEBUG:
        log.debug("PERFORMANCE : GIS INDEXED sector ss bh results")
        log.debug("START TIME : %s" %st)

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

    if DEBUG:
        endtime = datetime.datetime.now()
        elapsed = endtime - st
        log.debug("TIME TAKEN : {}".format(divmod(elapsed.total_seconds(), 60)))
        log.debug("PERFORMANCE : GIS INDEXED sector ss bh results : COMPLETED")

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

    st = datetime.datetime.now()

    if DEBUG:
        log.debug("PERFORMANCE : CALL : combined_indexed_gis_devices")
        log.debug("START TIME : %s" %st)

    indexed_sector, indexed_ss, indexed_bh = \
        combined_indexed_gis_devices(indexes={'sector':'SECTOR_CONF_ON_NAME','ss':'SSDEVICENAME','bh':'BHCONF'})

    # gis_result = indexed_gis_devices(page_type=page_type)

    if DEBUG:
        endtime = datetime.datetime.now()
        elapsed = endtime - st
        log.debug("TIME TAKEN : {}".format(divmod(elapsed.total_seconds(), 60)))
        log.debug("PERFORMANCE : CALL : combined_indexed_gis_devices : COMPLETED")

    st = datetime.datetime.now()

    if DEBUG:
        log.debug("FINAL RESULTS : GIS Inventory Mapped")
        log.debug("START TIME : %s" %st)

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

        if is_sector:
            for bs_row in raw_result:
                if bs_row['SECTOR_SECTOR_ID'] not in sector_id \
                    and bs_row['SECTOR_SECTOR_ID'] is not None:
                    sector_id.append(bs_row['SECTOR_SECTOR_ID'])

        for bs_row in raw_result:
            if device_name is not None and device_name not in processed_device:
                processed_device[device_name] = []
                device.update({
                        "sector_id": ", ".join(sector_id),
                        "circuit_id": format_value(bs_row['CCID']),
                        "customer_name": format_value(bs_row['CUST']),
                        "bs_name": format_value(bs_row['BSALIAS']),
                        "city": format_value(bs_row['BSCITY']),
                        "state": format_value(bs_row['BSSTATE']),
                        "device_type": format_value(bs_row['SECTOR_TYPE']),
                        "device_technology": format_value(bs_row['SECTOR_TECH'])
                    })
                if is_ss:
                    device.update({
                        "sector_id": format_value(bs_row['SECTOR_SECTOR_ID']),
                        "device_type": format_value(bs_row['SS_TYPE']),
                        "device_technology": format_value(bs_row['SECTOR_TECH'])
                    })
                elif is_bh:
                    device.update({
                        "device_type": format_value(bs_row['BHTYPE']),
                        "device_technology": format_value(bs_row['BHTECH'])
                    })

    if DEBUG:
        endtime = datetime.datetime.now()
        elapsed = endtime - st
        log.debug("TIME TAKEN : {}".format(divmod(elapsed.total_seconds(), 60)))
        log.debug("FINAL RESULTS : GIS Inventory Mapped : COMPLETED")

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
    st = datetime.datetime.now()

    device_result = {}
    # perf_result = {"packet_loss": "N/A",
    #                "latency": "N/A",
    #                "last_updated": "N/A",
    #                "last_updated_date": "N/A",
    #                "last_updated_time": "N/A",
    #                "age": "N/A"
    #               }

    if DEBUG:
        log.debug("preparing polled results : query")
        log.debug("start time %s" %st)

    query = prepare_row_query(table_name="performance_networkstatus",
                          devices=device_list,
    )
    # (query)
    performance_data = fetch_raw_result(query=query,machine=machine)#model.objects.raw(query).using(alias=machine)

    indexed_perf_data = indexed_polled_results(performance_data)

    # (len(performance_data))
    # for device in device_list:
    #     if device not in device_result:
    #         device_result[device] = perf_result

    if DEBUG:
        endtime = datetime.datetime.now()
        elapsed = endtime - st
        log.debug("preparing polled results : query execution complete")
        log.debug("Ending Query Time {}".format(divmod(elapsed.total_seconds(), 60)))

    st = datetime.datetime.now()

    if DEBUG:
        log.debug("preparing polled results : processing in loop start")
        log.debug("start time %s" %st)

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

            # if d_src == "pl":
            perf_result["packet_loss"] = data['pl']
            # if d_src == "rta":
            perf_result["latency"] = data['rta']

            perf_result["last_updated"] = datetime.datetime.fromtimestamp(
                float(data['sys_timestamp'])
            ).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)")

            perf_result["age"] = datetime.datetime.fromtimestamp(
                float(data['age'])
            ).strftime("%d days %H:%M:%S")

            device_result[device] = perf_result
    # (device_result)
    try:
        q.put(device_result)

        if DEBUG:
            endtime = datetime.datetime.now()
            elapsed = endtime - st
            log.debug("preparing polled results : processing in loop end")
            log.debug("Ending Multiprocessing time {}".format(divmod(elapsed.total_seconds(), 60)))

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
    # perf_result = {"packet_loss": "N/A",
    #                "latency": "N/A",
    #                "last_updated": "N/A",
    #                "last_updated_date": "N/A",
    #                "last_updated_time": "N/A",
    #                "age": "N/A"
    #               }

    if DEBUG:
        log.debug("preparing polled results : query")
        log.debug("start time %s" %st)

    query = prepare_row_query(table_name="performance_networkstatus",
                          devices=device_list
    )

    performance_data = fetch_raw_result(query=query,machine=machine)#model.objects.raw(query).using(alias=machine)

    indexed_perf_data = indexed_polled_results(performance_data)

    # (len(performance_data))
    # for device in device_list:
    #     if device not in device_result:
    #         device_result[device] = perf_result

    if DEBUG:
        endtime = datetime.datetime.now()
        elapsed = endtime - st
        log.debug("preparing polled results : query execution complete")
        log.debug("Ending Query Time {}".format(divmod(elapsed.total_seconds(), 60)))

    st = datetime.datetime.now()

    if DEBUG:
        log.debug("preparing polled results : processing in loop start")
        log.debug("start time %s" %st)


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

            # if d_src == "pl":
            perf_result["packet_loss"] = data['pl']
            # if d_src == "rta":
            perf_result["latency"] = data['rta']

            perf_result["last_updated"] = datetime.datetime.fromtimestamp(
                float(data['sys_timestamp'])
            ).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)")

            perf_result["age"] = datetime.datetime.fromtimestamp(
                float(data['age'])
            ).strftime("%d days %H:%M:%S")

            device_result[device] = perf_result
    # (device_result)
    #  device_result
    if DEBUG:
        endtime = datetime.datetime.now()
        elapsed = endtime - st
        log.debug("preparing polled results : processing in loop end")
        log.debug("Ending single thread processing time {}".format(divmod(elapsed.total_seconds(), 60)))

    return device_result
