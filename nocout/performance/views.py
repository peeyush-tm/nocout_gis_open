# -*- coding: utf-8 -*-
import csv
#import json
import ujson as json
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

from performance.models import PerformanceService, PerformanceNetwork, \
    EventService, NetworkStatus, \
    ServiceStatus, InventoryStatus, \
    PerformanceStatus, PerformanceInventory, \
    Status, NetworkAvailabilityDaily, Topology, Utilization, UtilizationStatus

from django.utils.dateformat import format

from operator import itemgetter

from nocout.utils import util as nocout_utils

#utilities inventory
from inventory.utils import util as inventory_utils

from performance.utils import util as perf_utils

from service.utils.util import service_data_sources

from nocout.settings import DATE_TIME_FORMAT

##execute this globally
SERVICE_DATA_SOURCE = service_data_sources()
##execute this globally

import logging

log = logging.getLogger(__name__)

# def uptime_to_days(uptime=0):
#     if uptime:
#         ret_val = int(float(uptime)/(60 * 60 * 2``))
#         return ret_val if ret_val > 0 else int(float(uptime)/(60 * 60))


def rta_null(rta=0):
    """

    :param rta:
    :return:
    """
    try:
        if float(rta) == 0:
            return None
    except Exception as e:
        return None

    return rta


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

        hidden_headers = [
            {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
        ]

        common_headers = [
            {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'bs_name', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'city', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'state', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},

        ]

        polled_headers = [
            {'mData': 'packet_loss', 'sTitle': 'Packet Loss', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'latency', 'sTitle': 'Latency', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'last_updated', 'sTitle': 'Last Updated Time', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'age', 'sTitle': 'Status Since', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        ]

        action_headers = [
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False}
        ]

        if page_type in ["customer", "network"]:
            specific_headers = [
                {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
                {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
                {'mData': 'customer_name', 'sTitle': 'Customer', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
            ]

        # elif page_type in ["network"]:
        #     specific_headers = [
        #         {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'sClass': 'hidden-xs',
        #          'bSortable': True},
        #     ]

        else:
            specific_headers = [
                {'mData': 'device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
            ]

        datatable_headers = hidden_headers
        datatable_headers += specific_headers
        datatable_headers += common_headers
        datatable_headers += polled_headers
        datatable_headers += action_headers

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

    columns = [
        'id',
        'circuit_id',
        'sector_id',
        'customer_name',
        'ip_address',
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

        required_value_list = ['id', 'machine__name', 'device_name', 'ip_address']

        device_tab_technology = self.request.GET.get('data_tab')

        devices = inventory_utils.filter_devices(organizations=kwargs['organizations'],
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
            columns = [
                'id',
                'circuit_id',
                'sector_id',
                'customer_name',
                'ip_address',
                'device_type',
                'bs_name',
                'city',
                'state',
                'packet_loss',
                'latency',
                'last_updated',
                'age'
            ]
        elif page_type == 'network':
            columns = [
                'id',
                'circuit_id',
                'sector_id',
                'customer_name',
                'ip_address',
                'device_type',
                'bs_name',
                'city',
                'state',
                'packet_loss',
                'latency',
                'last_updated',
                'age'
            ]
        else:
            columns = [
                'id',
                'device_technology',
                'ip_address',
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

    def prepare_devices(self, qs):
        """

        :param device_list:
        :return:
        """
        page_type = self.request.GET['page_type']
        return perf_utils.prepare_gis_devices(qs, page_type)

    def prepare_machines(self, qs):
        """
        """
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

        return inventory_utils.prepare_machines(device_list)

    def prepare_polled_results(self, qs, multi_proc=False, machine_dict={}):
        """
        preparing polled results
        after creating static inventory first
        """
        result_qs = perf_utils.polled_results(qs=qs,
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
        page_type = self.request.GET['page_type']
        if qs:
            for dct in qs:
                # device = Device.objects.get(id=dct['id'])
                try:
                    if int(dct['packet_loss']) == 100:
                        dct['latency'] = "DOWN"
                except Exception as e:
                    if str((dct['packet_loss'])) in ["100", "100.0", "100.00"]:
                        dct['latency'] = "DOWN"

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


class Get_Perfomance(View):
    """
    The Class based View to get performance page for the single device.

    """

    def get(self, request, page_type="no_page", device_id=0):

        device = Device.objects.get(id=device_id)
        device_technology = DeviceTechnology.objects.get(id=device.device_technology).name
        realdevice = device

        page_data = {
            'page_title': page_type.capitalize(),
            'device_technology': device_technology,
            'device': device,
            'realdevice': realdevice,
            'get_devices_url': 'performance/get_inventory_devices/' + page_type,
            'get_status_url': 'performance/get_inventory_device_status/' + page_type + '/device/' + str(device_id),
            'get_services_url': 'performance/get_inventory_service_data_sources/device/' + str(
                device_id),
            'page_type': page_type
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
        return HttpResponse(json.dumps(result), mimetype="application/json")

    def get_result(self, page_type, organizations):
        """
        Generic function to return the result w.r.t the page_type and organization of the current logged in user.

        :param page_type:
        :param organization:
        return result
        """
        device_list = []

        if page_type == "customer":
            device_list = inventory_utils.organization_customer_devices(organizations)

        elif page_type == "network":
            device_list = inventory_utils.organization_network_devices(organizations)

        elif page_type == 'other':
            device_list = inventory_utils.organization_backhaul_devices(organizations)

        result = list()
        for device in device_list:
            result.append({'id': device.id,
                           'alias': device.device_alias,
                           'technology': DeviceTechnology.objects.get(id=device.device_technology).name}
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
            if technology.name in ['P2P', 'PTP', 'ptp', 'p2p']:
                result['data']['objects']['headers'] = ['BS Name',
                                                        'Customer Name',
                                                        'Technology',
                                                        'Type',
                                                        'City',
                                                        'State',
                                                        'IP Address',
                                                        # 'MAC Address',
                                                        'Planned Frequency',
                                                        'Frequency'
                ]
            elif technology.name.lower() in ['wimax']:
                result['data']['objects']['headers'] = ['BS Name',
                                                        'Sector ID',
                                                        'PMP Port',
                                                        'Technology',
                                                        'Type',
                                                        'City',
                                                        'State',
                                                        'IP Address',
                                                        # 'MAC Address',
                                                        'Planned Frequency',
                                                        'Frequency'
                ]
            else:
                result['data']['objects']['headers'] = ['BS Name',
                                                        'Sector ID',
                                                        'Technology',
                                                        'Type',
                                                        'City',
                                                        'State',
                                                        'IP Address',
                                                        # 'MAC Address',
                                                        'Planned Frequency',
                                                        'Frequency'
                ]
            result['data']['objects']['values'] = []
            sector_objects = Sector.objects.filter(sector_configured_on=device.id)

            for sector in sector_objects:

                sector_id = 'N/A'
                pmp_port = 'N/A'
                dr_ip = None

                base_station = sector.base_station
                planned_frequency = [sector.planned_frequency] if sector.planned_frequency else ["N/A"]
                frequency = [sector.frequency.value] if sector.frequency else ["N/A"]
                planned_frequency = ",".join(planned_frequency)
                frequency = ",".join(frequency)
                if technology.name.lower() in ['ptp', 'p2p']:
                    try:
                        circuits = sector.circuit_set.get()
                        customer_name = circuits.customer.alias
                    except Exception as no_circuit:
                        log.exception(no_circuit)

                else:
                    sector_id = sector.sector_id
                    if technology.name.lower() in ['wimax']:
                        try:
                            pmp_port = sector.sector_configured_on_port.alias
                            pmp_port = pmp_port.upper()
                        except Exception as no_port:
                            log.exception(no_port)
                        try:
                            dr_ip = sector.dr_configured_on.ip_address
                        except Exception as no_dr:
                            dr_ip = None
                            log.exception(no_dr.message)

                try:
                    city_name = City.objects.get(id=base_station.city).city_name \
                        if base_station.city \
                        else "N/A"
                except Exception as no_city:
                    city_name = "N/A"
                try:
                    state_name = State.objects.get(id=base_station.state).state_name \
                        if base_station.state \
                        else "N/A"
                except Exception as no_state:
                    state_name = "N/A"

                display_bs_name = base_station.alias
                if display_bs_name:
                    display_bs_name = display_bs_name.upper()

                if technology.name.lower() in ['ptp', 'p2p']:
                    result['data']['objects']['values'].append([display_bs_name,
                                                                customer_name,
                                                                technology.alias,
                                                                type.alias,
                                                                city_name,
                                                                state_name,
                                                                device.ip_address,
                                                                # device.mac_address,
                                                                planned_frequency,
                                                                frequency
                    ])

                elif technology.name.lower() in ['wimax']:
                    result['data']['objects']['values'].append([display_bs_name,
                                                                sector_id,
                                                                pmp_port,
                                                                technology.alias,
                                                                type.alias,
                                                                city_name,
                                                                state_name,
                                                                device.ip_address,
                                                                # device.mac_address,
                                                                planned_frequency,
                                                                frequency
                    ])
                    if dr_ip:
                        dr_ip += " (DR) "
                        result['data']['objects']['values'].append([display_bs_name,
                                                                sector_id,
                                                                pmp_port,
                                                                technology.alias,
                                                                type.alias,
                                                                city_name,
                                                                state_name,
                                                                dr_ip,
                                                                # device.mac_address,
                                                                planned_frequency,
                                                                frequency
                    ])

                else:
                    result['data']['objects']['values'].append([display_bs_name,
                                                                sector_id,
                                                                # pmp_port,
                                                                technology.alias,
                                                                type.alias,
                                                                city_name,
                                                                state_name,
                                                                device.ip_address,
                                                                # device.mac_address,
                                                                planned_frequency,
                                                                frequency
                    ])

        elif device.substation_set.exists():
            result['data']['objects']['headers'] = ['BS Name',
                                                    'SS Name',
                                                    'Circuit ID',
                                                    'Customer Name',
                                                    'Technology',
                                                    # 'Building Height',
                                                    # 'Tower Height',
                                                    'City',
                                                    'State',
                                                    'IP Address',
                                                    'MAC Address',
                                                    # 'Planned Frequency',
                                                    'Frequency'
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

                    planned_frequency = [sector.planned_frequency] if sector.planned_frequency else ["N/A"]
                    frequency = [sector.frequency.value] if sector.frequency else ["N/A"]
                    planned_frequency = ",".join(planned_frequency)
                    frequency = ",".join(frequency)

                    try:
                        city_name = City.objects.get(id=base_station.city).city_name \
                            if base_station.city \
                            else "N/A"
                    except Exception as no_city:
                        city_name = "N/A"
                    try:
                        state_name = State.objects.get(id=base_station.state).state_name \
                            if base_station.state \
                            else "N/A"
                    except Exception as no_state:
                        state_name = "N/A"

                    display_mac_address = device.mac_address
                    if display_mac_address:
                        display_mac_address = display_mac_address.upper()

                    display_bs_name = base_station.alias
                    if display_bs_name:
                        display_bs_name = display_bs_name.upper()

                    result['data']['objects']['values'].append([display_bs_name,
                                                                substation.alias,
                                                                circuit.circuit_id,
                                                                customer_name[0].alias,
                                                                technology.alias,
                                                                # substation.building_height,
                                                                # substation.tower_height,
                                                                city_name,
                                                                state_name,
                                                                device.ip_address,
                                                                display_mac_address,
                                                                # planned_frequency,
                                                                frequency
                    ])

        result['success'] = 1
        result['message'] = 'Inventory Device Status Fetched Successfully.'
        return HttpResponse(json.dumps(result), mimetype="application/json")


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
                        "info": [],
                        "isActive": 1
                    },
                    'service_status_tab': {
                        "info": [],
                        "isActive": 0
                    },
                    'inventory_status_tab': {
                        "info": [],
                        "isActive": 0
                    },
                    'service_perf_tab': {
                        "info": [],
                        "isActive": 0
                    },
                    'availability_tab': {
                        "info": [],
                        "isActive": 0
                    },
                    'topology_tab': {
                        "info": [],
                        "isActive": 0
                    },
                    'utilization_top_tab': {
                        "info": [],
                        "isActive": 0
                    },
                    'rssi_top_tab': {
                        "info": [],
                        "isActive": 0
                    }
                }
            }
        }
        device = Device.objects.get(id=device_id)
        device_type = DeviceType.objects.get(id=device.device_type)

        #if there is no service present in the configuration (BULK SYNC)
        # inventory_device_service_name = device_type.service.filter().values_list('name', 'service_data_sources__name')

        #
        # #Fetch the Service names that are configured w.r.t to a device.
        # inventory_device_service_name = DeviceServiceConfiguration.objects.filter(
        #     device_name= device.device_name)\
        #     .values_list('service_name', 'data_source')

        # configured_services = DeviceServiceConfiguration.objects.filter(
        #     device_name=device.device_name) \
        #     .values_list('service_name', 'data_source')
        #
        # if len(configured_services):
        #     inventory_device_service_name = configured_services

        # TODO:to remove this code as the services are getting multi added with their port.
        # inventory_device_service_name = list(set(inventory_device_service_name))

        result['data']['objects']['network_perf_tab']["info"].append(
            {
                'name': "pl",
                'title': "Packet Drop",
                'url': 'performance/service/ping/service_data_source/pl/device/' + str(device_id),
                'active': 0,
                'service_type_tab': 'network_perf_tab'
            })

        result['data']['objects']['network_perf_tab']["info"].append(
            {
                'name': "rta",
                'title': "Latency",
                'url': 'performance/service/ping/service_data_source/rta/device/' + str(device_id),
                'active': 0,
                'service_type_tab': 'network_perf_tab'
            })

        if device.substation_set.exists():
            result['data']['objects']['network_perf_tab']["info"].append(
            {
                'name': "rf",
                'title': "RF Latency",
                'url': 'performance/service/rf/service_data_source/rf/device/' + str(device_id),
                'active': 0,
                'service_type_tab': 'network_perf_tab'
            })

        device_type_services = device_type.service.filter().prefetch_related('servicespecificdatasource_set')

        for service in device_type_services:
            service_name = service.name.strip().lower()
            service_data_sources = service.service_data_sources.filter()
            for service_data_source in service_data_sources:
                sds_name = service_data_source.name.strip().lower()

                sds_info = {
                            'name': service_data_source.name,
                            'title': service.alias.strip().upper() +
                                    "<br> [ " +
                                    service_data_source.alias.strip().title() +
                                    " ] <br>",
                            'url': 'performance/service/' + service_name +
                                   '/service_data_source/' + sds_name +
                                   '/device/' + str(device_id),
                            'active': 0,
                        }

                if '_status' in service_name:
                    result['data']['objects']['service_status_tab']["info"].append(sds_info)

                elif '_invent' in service_name:
                    result['data']['objects']['inventory_status_tab']["info"].append(sds_info)
                elif 'topology' in service_name:
                    continue
                else:
                    result['data']['objects']['service_perf_tab']["info"].append(sds_info)

                
        result['data']['objects']['availability_tab']["info"].append(
            {
                'name': 'availability',
                'title': 'Availability',
                'url': 'performance/service/availability/service_data_source/availability/device/' +
                       str(device_id),
                'active': 0,
            })

        result['data']['objects']['topology_tab']["info"].append({
            'name': 'topology',
            'title': 'Topology',
            'url': 'performance/service/topology/service_data_source/topology/device/' +
                   str(device_id),
            'active': 0,
        })

        result['data']['objects']['utilization_top_tab']["info"].append({
            'name': 'utilization_top',
            'title': 'Utilization',
            'url': 'performance/servicedetail/util/device/'+str(device_id),
            'active': 0,
        })

        # result['data']['objects']['rssi_top_tab']["info"].append({
        #     'name': 'rssi_top',
        #     'title': 'RSSI',
        #     'url': 'performance/servicedetail/rssi/device/'+str(device_id),
        #     'active': 0,
        # })

        result['success'] = 1
        result['message'] = 'Substation Devices Services Data Source Fetched Successfully.'
        return HttpResponse(json.dumps(result), mimetype="application/json")


class Get_Service_Status(View):
    """
    Class to get the latest Performance Value for a device, device data source and service
    """

    def get(self, request, service_name, service_data_source_type, device_id):
        """

        :param request:
        :param service_name:
        :param service_data_source_type:
        :param device_id:
        """
        self.result = {
            'success': 0,
            'message': 'No Data.',
            'data': {
                'meta': {},
                'objects': {
                    'perf': None,
                    'last_updated': None,
                    'status': None,
                    'age': None
                }
            }
        }

        date_format = "%d-%m-%Y %H:%M:%S"

        device = Device.objects.get(id=int(device_id))
        inventory_device_name = device.device_name
        inventory_device_machine_name = device.machine.name  # Device Machine Name required in Query to fetch data.

        device_nms_uptime_query_set = NetworkStatus.objects.filter(
            device_name=inventory_device_name,
            data_source='pl',
        ).values('age', 'severity')
        # using(
        #     alias=inventory_device_machine_name
        # ).
        device_nms_uptime = nocout_utils.nocout_query_results(query_set=device_nms_uptime_query_set,
                                                              using=inventory_device_machine_name)
        if device_nms_uptime and len(device_nms_uptime):
            data = device_nms_uptime[0]

            age = datetime.datetime.fromtimestamp(float(data['age'])
            ).strftime(DATE_TIME_FORMAT)
            severity = data['severity']

            self.result = {
                'success': 1,
                'message': 'Service Status Fetched Successfully',
                'data': {
                    'meta': {},
                    'objects': {
                        'perf': None,
                        'last_updated': None,
                        'status': severity.lower().strip() if severity else None,
                        'age': age
                    }
                }
            }

        if service_data_source_type in ['pl', 'rta']:
            performance_data_query_set = NetworkStatus.objects.filter(device_name=inventory_device_name,
                                                            service_name=service_name,
                                                            data_source=service_data_source_type,
            )

        elif "rf" == service_name and "rf" == service_data_source_type:
            performance_data_query_set = None

        elif service_name in ['util', 'topology', 'availability'] or service_data_source_type in ['util', 'availability', 'topology']:
            performance_data_query_set = None

        elif '_status' in service_name:
            performance_data_query_set = Status.objects.filter(device_name=inventory_device_name,
                                                     service_name=service_name,
                                                     data_source=service_data_source_type,
            )

        elif '_invent' in service_name:
            performance_data_query_set = InventoryStatus.objects.filter(device_name=inventory_device_name,
                                                              service_name=service_name,
                                                              data_source=service_data_source_type
            )

        elif '_kpi' in service_name:
            performance_data_query_set = UtilizationStatus.objects.filter(device_name=inventory_device_name,
                                                              service_name=service_name,
                                                              data_source=service_data_source_type
            )

        else:
            performance_data_query_set = ServiceStatus.objects.filter(device_name=inventory_device_name,
                                                            service_name=service_name,
                                                            data_source=service_data_source_type,
            )

        if performance_data_query_set:
            performance_data = nocout_utils.nocout_query_results(query_set=performance_data_query_set,
                                                                 using=inventory_device_machine_name)
            try:
                current_value = self.formulate_data(performance_data[0].current_value,
                                                    service_data_source_type)
                last_updated = datetime.datetime.fromtimestamp(
                    float(performance_data[0].sys_timestamp)
                ).strftime(DATE_TIME_FORMAT)
                self.result['data']['objects']['perf'] = current_value
                self.result['data']['objects']['last_updated'] = last_updated
            except Exception as e:
                log.exception(e.message)

        return HttpResponse(json.dumps(self.result), mimetype="application/json")

    def formulate_data(self, current_value, service_data_source_type):
        """

        :param current_value: current value for the service
        :param service_data_source_type: current value to be transformed
        """
        if service_data_source_type == 'uptime':
            if current_value:
                tt_sec = float(current_value) / 100
                return self.display_time(tt_sec)
        else:
            return current_value

    def display_time(self, seconds, granularity=4):
        """

        :param seconds: seconds on float
        :param granularity:
        :return:
        """
        intervals = (
            ('weeks', 604800),
            ('days', 86400),
            ('hours', 3600),
            ('minutes', 60),
            ('seconds', 1),
        )
        result = []
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return ', '.join(result[:granularity])


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

        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        isSet = False

        isSet, start_date, end_date = perf_utils.get_time(start_date, end_date, date_format)

        if service_data_source_type in ['pl', 'rta']:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(minutes=-180), 'U')
            technology = DeviceTechnology.objects.get(id=device.device_technology)
            dr_device = None
            if technology and technology.name.lower() in ['wimax'] and device.sector_configured_on.exists():
                dr_devices = device.sector_configured_on.filter()
                for dr_d in dr_devices:
                    dr_device = dr_d.dr_configured_on
            if dr_device:
                performance_data = PerformanceNetwork.objects.filter(device_name__in=[inventory_device_name, dr_device.device_name],
                                                                     service_name=service_name,
                                                                     data_source=service_data_source_type,
                                                                     sys_timestamp__gte=start_date,
                                                                     sys_timestamp__lte=end_date).using(
                    alias=inventory_device_machine_name).order_by('sys_timestamp')
                result = self.dr_performance_data_result(performance_data=performance_data,
                                                         sector_device=device,
                                                         dr_device=dr_device
                                                         )
            else:

                performance_data = PerformanceNetwork.objects.filter(device_name=inventory_device_name,
                                                                     service_name=service_name,
                                                                     data_source=service_data_source_type,
                                                                     sys_timestamp__gte=start_date,
                                                                     sys_timestamp__lte=end_date).using(
                    alias=inventory_device_machine_name).order_by('sys_timestamp')

                result = self.get_performance_data_result(performance_data)

        elif service_data_source_type == 'rf':
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(minutes=-180), 'U')
            sector_device = None
            if device.substation_set.exists():
                try:
                    ss = device.substation_set.get()
                    circuit = ss.circuit_set.get()
                    sector_device = circuit.sector.sector_configured_on
                except Exception as e:
                    log.exception(e.message)
            if sector_device:
                performance_data_ss = PerformanceNetwork.objects.filter(device_name=inventory_device_name,
                                                                     service_name='ping',
                                                                     data_source='rta',
                                                                     sys_timestamp__gte=start_date,
                                                                     sys_timestamp__lte=end_date).using(
                    alias=inventory_device_machine_name).order_by('sys_timestamp')

                performance_data_bs = PerformanceNetwork.objects.filter(device_name=sector_device.device_name,
                                                                     service_name='ping',
                                                                     data_source='rta',
                                                                     sys_timestamp__gte=start_date,
                                                                     sys_timestamp__lte=end_date).using(
                    alias=sector_device.machine.name).order_by('sys_timestamp')

                result = self.rf_performance_data_result(performance_data_bs=performance_data_bs,
                                                         performance_data_ss=performance_data_ss
                )

            else:
                performance_data = PerformanceNetwork.objects.filter(device_name=inventory_device_name,
                                                                     service_name='ping',
                                                                     data_source='rta',
                                                                     sys_timestamp__gte=start_date,
                                                                     sys_timestamp__lte=end_date).using(
                    alias=inventory_device_machine_name).order_by('sys_timestamp')

                result = self.get_performance_data_result(performance_data)

        elif "availability" in service_name or service_data_source_type in ['availability']:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(weeks=-1), 'U')
            technology = DeviceTechnology.objects.get(id=device.device_technology)
            dr_device = None
            if technology and technology.name.lower() in ['wimax'] and device.sector_configured_on.exists():
                dr_devices = device.sector_configured_on.filter()
                for dr_d in dr_devices:
                    dr_device = dr_d.dr_configured_on
            if dr_device:
                performance_data = NetworkAvailabilityDaily.objects.filter(device_name__in=[inventory_device_name, dr_device.device_name],
                                                                     service_name=service_name,
                                                                     data_source=service_data_source_type,
                                                                     sys_timestamp__gte=start_date,
                                                                     sys_timestamp__lte=end_date).using(
                    alias=inventory_device_machine_name).order_by('sys_timestamp')
                result = self.dr_performance_data_result(performance_data=performance_data,
                                                         sector_device=device,
                                                         dr_device=dr_device
                                                         )
            else:
                performance_data = NetworkAvailabilityDaily.objects.filter(device_name=inventory_device_name,
                                                                       service_name=service_name,
                                                                       data_source=service_data_source_type,
                                                                       sys_timestamp__gte=start_date,
                                                                       sys_timestamp__lte=end_date).using(
                alias=inventory_device_machine_name).order_by('sys_timestamp')

                result = self.get_performance_data_result(performance_data, data_source="availability")

        elif "topology" in service_name or service_data_source_type in ['topology']:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(weeks=-1), 'U')
            #for wimax devices there can be a case of DR
            #we need to incorporate the DR devices as well
            technology = DeviceTechnology.objects.get(id=device.device_technology)
            dr_device = None
            if technology and technology.name.lower() in ['wimax'] and device.sector_configured_on.exists():
                dr_devices = device.sector_configured_on.filter()
                for dr_d in dr_devices:
                    dr_device = dr_d.dr_configured_on

            if dr_device:
                dr_device_name = dr_device.device_name
                performance_data = Topology.objects.filter(device_name__in=[inventory_device_name, dr_device_name],
                                                           # service_name=service_name,
                                                           data_source='topology',  #service_data_source_type,
                                                           sys_timestamp__gte=start_date,
                                                           sys_timestamp__lte=end_date).using(
                    alias=inventory_device_machine_name)
                result = self.get_topology_result(performance_data, dr_ip=dr_device.ip_address)
            else:
                performance_data = Topology.objects.filter(device_name=inventory_device_name,
                                                           # service_name=service_name,
                                                           data_source='topology',  #service_data_source_type,
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
                                                                   sys_timestamp__gte=start_date,
                                                                   sys_timestamp__lte=end_date).using(
                alias=inventory_device_machine_name)

            result = self.get_perf_table_result(performance_data)

        elif '_kpi' in service_name:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(minutes=-180), 'U')
            #kpi services depends on the refer fields
            #and not directly on the "device_name"
            #the refer filed indicates the sector
            technology = DeviceTechnology.objects.get(id=device.device_technology)
            dr_device = None
            if technology and technology.name.lower() in ['wimax'] and device.sector_configured_on.exists():
                dr_devices = device.sector_configured_on.filter()
                for dr_d in dr_devices:
                    dr_device = dr_d.dr_configured_on
            if dr_device:
                performance_data = Utilization.objects.filter(device_name__in=[inventory_device_name, dr_device.device_name],
                                                                     service_name=service_name,
                                                                     data_source=service_data_source_type,
                                                                     sys_timestamp__gte=start_date,
                                                                     sys_timestamp__lte=end_date).using(
                    alias=inventory_device_machine_name).order_by('sys_timestamp')
                result = self.dr_performance_data_result(performance_data=performance_data,
                                                         sector_device=device,
                                                         dr_device=dr_device
                                                         )
            else:
                performance_data = Utilization.objects.filter(device_name=inventory_device_name,
                                                                   service_name=service_name,
                                                                   data_source=service_data_source_type,
                                                                   sys_timestamp__gte=start_date,
                                                                   sys_timestamp__lte=end_date).using(
                alias=inventory_device_machine_name).order_by('sys_timestamp')

                result = self.get_performance_data_result(performance_data)

        else:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(minutes=-180), 'U')
            technology = DeviceTechnology.objects.get(id=device.device_technology)
            dr_device = None
            if technology and technology.name.lower() in ['wimax'] and device.sector_configured_on.exists():
                dr_devices = device.sector_configured_on.filter()
                for dr_d in dr_devices:
                    dr_device = dr_d.dr_configured_on
            if dr_device:
                performance_data = PerformanceService.objects.filter(device_name__in=[inventory_device_name, dr_device.device_name],
                                                                     service_name=service_name,
                                                                     data_source=service_data_source_type,
                                                                     sys_timestamp__gte=start_date,
                                                                     sys_timestamp__lte=end_date).using(
                    alias=inventory_device_machine_name).order_by('sys_timestamp')

                #to check of string based dashboards
                #need to return a table
                if service_data_source_type.lower() in SERVICE_DATA_SOURCE \
                        and SERVICE_DATA_SOURCE[service_data_source_type.lower()]['type'] == 'table':
                    result = self.get_perf_table_result(performance_data)

                else:
                    result = self.dr_performance_data_result(performance_data=performance_data,
                                                         sector_device=device,
                                                         dr_device=dr_device
                                                         )

            else:
                performance_data = PerformanceService.objects.filter(device_name=inventory_device_name,
                                                                 service_name=service_name,
                                                                 data_source=service_data_source_type,
                                                                 sys_timestamp__gte=start_date,
                                                                 sys_timestamp__lte=end_date).using(
                alias=inventory_device_machine_name).order_by('sys_timestamp')
                #to check of string based dashboards
                #need to return a table
                if service_data_source_type.lower() in SERVICE_DATA_SOURCE \
                        and SERVICE_DATA_SOURCE[service_data_source_type.lower()]['type'] == 'table':
                    result = self.get_perf_table_result(performance_data)

                else:
                    result = self.get_performance_data_result(performance_data)

        download_excel = self.request.GET.get('download_excel', '')
        download_csv = self.request.GET.get('download_csv', '')

        if download_excel:

            table_data, table_header = self.return_table_header_and_table_data(service_name, result)
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('report')
            style = xlwt.XFStyle()

            borders = xlwt.Borders()
            borders.bottom = xlwt.Borders.DASHED
            style.borders = borders

            column_length = len(table_header)
            row_length = len(table_data) + 1
            #Writing headers first for the excel file.
            for column in range(column_length):
                worksheet.write(0, column, table_header[column], style=style)
            #Writing rest of the rows.
            for row in range(1, row_length):
                for column in range(column_length):
                    worksheet.write(row, column, table_data[row - 1][table_header[column].lower()], style=style)

            response = HttpResponse(mimetype='application/vnd.ms-excel', content_type='text/plain')
            start_date_string = start_date
            end_date_string = end_date
            response['Content-Disposition'] = 'attachment; filename=performance_report_{0}_{1}_to_{2}.xls' \
                .format(inventory_device_name, start_date_string, end_date_string)
            workbook.save(response)
            return response

        elif download_csv:

            table_data, table_header = self.return_table_header_and_table_data(service_name, result)
            response = HttpResponse(content_type='text/csv')
            start_date_string = start_date
            end_date_string = end_date
            response['Content-Disposition'] = 'attachment; filename="performance_report_{0}_{1}_to_{2}.xls"' \
                .format(inventory_device_name, start_date_string, end_date_string)

            writer = csv.writer(response)
            writer.writerow(table_header)
            column_length = len(table_header)
            row_length = len(table_data) + 1

            for row in range(1, row_length):
                row_list = list()
                for column in range(0, column_length):
                    row_list.append(table_data[row - 1][table_header[column].lower()])
                writer.writerow(row_list)
            return response

        else:
            return HttpResponse(json.dumps(result), mimetype="application/json")

    def return_table_header_and_table_data(self, service_name, result):

        if '_invent' in service_name or '_status' in service_name:
            table_data = result['data']['objects']['table_data']
            table_header = result['data']['objects']['table_data_header']

        else:
            table_data = result['data']['objects']['chart_data'][0]['data']
            table_header = ['Value', 'Date', 'Time']
            data_list = []
            for data in table_data:
                data_list += [{
                                  'date': datetime.datetime.fromtimestamp(float(data['x'] / 1000)).strftime("%d/%B/%Y"),
                                  'time': datetime.datetime.fromtimestamp(float(data['x'] / 1000)).strftime("%I:%M %p"),
                                  'value': data['y'],
                              }]
            table_data = data_list
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
                    # 'date': datetime.datetime.fromtimestamp(float(data.sys_timestamp)).strftime("%d/%B/%Y"),
                    'time': datetime.datetime.fromtimestamp(float(data.sys_timestamp)).strftime(DATE_TIME_FORMAT),
                    'ip_address': data.ip_address,
                    'value': data.current_value,
                })
        self.result['success'] = 1
        self.result[
            'message'] = 'Device Performance Data Fetched Successfully To Plot Table.' if result_data else 'No Record Found.'
        self.result['data']['objects']['table_data'] = result_data
        self.result['data']['objects']['table_data_header'] = ['time', 'ip_address', 'value']
        return self.result

    def get_topology_result(self, performance_data, dr_ip=None):
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
                connected_ip = data.connected_device_ip
                #check if the devices connected exists in the database
                #we will loop through the set of connected device
                #TODO : make a single call to DB
                connected_devices = Device.objects.filter(ip_address=connected_ip)
                #since connected devices are all SS
                #they may exist or not
                #we will assume them to be no present in db
                circuit_id = 'NA'
                customer_name = 'NA'
                packet_loss = 'NA'
                latency = 'NA'
                status_since = 'NA'
                machine = 'default'
                #now lets check if SS exists for a device
                #and that the customer and circuit are present for that SS

                if connected_devices:
                    connected_device = connected_devices[0]
                    try:
                        ss = connected_device.substation_set.get()
                        ckt = ss.circuit_set.get()
                        circuit_id = ckt.circuit_id
                        customer_name = ckt.customer.alias
                    except Exception as e:
                        pass

                    #now lets see what the performance data it holds
                    if connected_device.is_added_to_nms:
                        machine = connected_device.machine.name
                        #is it added?
                        #only then query the performance network database
                        #for getting latest status
                        perf_data = NetworkStatus.objects.filter(device_name=connected_device.device_name
                        ).annotate(dcount=Count('data_source')
                        ).values('data_source', 'current_value', 'age', 'sys_timestamp').using(alias=machine)
                        processed = []
                        for pdata in perf_data:
                            if pdata['data_source'] not in processed:
                                if pdata['data_source'] == 'pl':
                                    packet_loss = pdata['current_value']
                                elif pdata['data_source'] == 'rta':

                                    try:
                                        latency = float(pdata['current_value'])
                                        if int(latency) == 0:
                                            latency = "DOWN"
                                    except:
                                        latency = pdata['current_value']
                                else:
                                    continue
                                status_since = pdata['age']
                                status_since = datetime.datetime.fromtimestamp(float(status_since)
                                ).strftime(DATE_TIME_FORMAT)
                            else:
                                continue

                show_ip_address = data.ip_address
                if dr_ip and dr_ip == show_ip_address:
                    show_ip_address += " (DR)"
                result_data.append({
                    #'device_name': data.device_name,
                    'ip_address': show_ip_address,
                    'mac_address': data.mac_address,
                    'sector_id': data.sector_id,
                    'connected_device_ip': data.connected_device_ip,
                    'connected_device_mac': data.connected_device_mac,
                    'circuit_id': circuit_id,
                    'customer_name': customer_name,
                    'packet_loss': packet_loss,
                    'latency': latency,
                    'status_since': status_since,
                    'last_updated': datetime.datetime.fromtimestamp(float(data.sys_timestamp)
                    ).strftime(DATE_TIME_FORMAT),
                })

        self.result['success'] = 1
        self.result['message'] = 'Device Data Fetched Successfully.' if result_data else 'No Record Found.'
        self.result['data']['objects']['table_data'] = result_data
        self.result['data']['objects']['table_data_header'] = [#'device_name',
                                                               'ip_address',
                                                               'mac_address',
                                                               'sector_id',
                                                               'connected_device_ip',
                                                               'connected_device_mac',
                                                               'circuit_id',
                                                               'customer_name',
                                                               'packet_loss',
                                                               'latency',
                                                               'status_since',
                                                               'last_updated'
        ]
        return self.result

    def rf_performance_data_result(self, performance_data_ss, performance_data_bs):
        """
        """
        chart_data = list()
        if performance_data_ss and performance_data_bs:
            data_list, warn_data_list, crit_data_list, aggregate_data = list(), list(), list(), dict()
            min_data_list = list()
            max_data_list = list()

            for data in performance_data_ss:
                js_time = data.sys_timestamp*1000
                if data.avg_value:
                    try:
                        ##in between 5 minutes the bs result will come before ss result
                        valid_end_time = data.sys_timestamp
                        valid_start_time = data.sys_timestamp - 300
                        ##in between 5 minutes the bs result will come before ss result
                        bs_lat = performance_data_bs.filter(sys_timestamp__gte=valid_start_time,
                                                            sys_timestamp__lte=valid_end_time
                        )[0].avg_value

                        ss_lat = data.avg_value
                        rf_lat = float(ss_lat) - float(bs_lat)
                        data_list.append([js_time, float(rf_lat)])
                    except Exception as e:
                        rf_lat = data.avg_value
                        data_list.append([js_time, float(rf_lat)])
                        log.exception(e.message)

            chart_data = [{'name': "RF Latency",
                            'data': data_list,
                            'type': 'area',
                            'valuesuffix': ' ms ',
                            'valuetext': ' ms '
                          }
                        ]

        self.result['success'] = 1
        self.result['message'] = 'Device Performance Data Fetched Successfully To Plot Graphs.'
        self.result['data']['objects']['chart_data'] = chart_data

        return self.result

    def dr_performance_data_result(self, performance_data, sector_device, dr_device):
        """
        specially for dr devices
        """


        sector_performance_data = performance_data.filter(device_name=sector_device.device_name)
        dr_performance_data = performance_data.filter(device_name=dr_device.device_name)

        sector_result = self.performance_data_result(performance_data=sector_performance_data)
        dr_result = self.performance_data_result(performance_data=dr_performance_data)
        try:
            sector_result['data']['objects']['chart_data'][0]['name'] += " ( {0} )".format(sector_device.ip_address)
            dr_result['data']['objects']['chart_data'][0]['name'] += " DR: ( {0} )".format(dr_device.ip_address)

            chart_data = sector_result['data']['objects']['chart_data']
            chart_data.append(dr_result['data']['objects']['chart_data'][0])
        except:
            chart_data = sector_result['data']['objects']['chart_data']

        self.result['success'] = 1
        self.result['message'] = 'Device Performance Data Fetched Successfully To Plot Graphs.'
        self.result['data']['objects']['chart_data'] = chart_data

        return self.result

    def performance_data_result(self, performance_data, data_source=None):
        chart_data = list()
        result = {
            'success': 0,
            'message': 'Device Utilization Data not found',
            'data': {
                'meta': {},
                'objects': {
                    'plot_type': '',
                    'display_name': '',
                    'valuesuffix': '',
                    'type': '',
                    'chart_data': [],
                    'valuetext': ''
                }
            }
        }
        if performance_data:
            data_list, warn_data_list, crit_data_list, aggregate_data = list(), list(), list(), dict()
            min_data_list = list()
            max_data_list = list()
            for data in performance_data:
                temp_time = data.sys_timestamp

                if temp_time in aggregate_data:
                    continue
                else:
                    aggregate_data[temp_time] = data.sys_timestamp

                    #time in javascript format
                    js_time = data.sys_timestamp * 1000
                    #time in javascript format

                    sds_name = str(data.data_source).strip().lower()
                    sds_display_name = \
                        SERVICE_DATA_SOURCE[sds_name]["display_name"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else str(data.data_source).upper()

                    result['data']['objects']['display_name'] = sds_display_name

                    result['data']['objects']['type'] = \
                        SERVICE_DATA_SOURCE[sds_name]["type"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else "area"

                    result['data']['objects']['valuesuffix'] = \
                        SERVICE_DATA_SOURCE[sds_name]["valuesuffix"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else ""

                    result['data']['objects']['valuetext'] = \
                        SERVICE_DATA_SOURCE[sds_name]["valuetext"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else str(data.data_source).upper()

                    result['data']['objects']['plot_type'] = 'charts'

                    chart_color = \
                        SERVICE_DATA_SOURCE[sds_name]["chart_color"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else '#70AFC4'

                    if sds_name not in ["availability"]:
                        #only display warning if there exists a warning
                        if data.warning_threshold:
                            warn_data_list.append([js_time, float(data.warning_threshold)])

                        #only display critical if there exists a critical
                        if data.critical_threshold:
                            crit_data_list.append([js_time, float(data.critical_threshold)])

                        ###to draw each data point w.r.t threshold we would need to use the following
                        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["show_min"]:
                            min_data_list.append([js_time, float(data.min_value)
                            if data.min_value else None])

                        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["show_max"]:
                            max_data_list.append([js_time, float(data.max_value)
                            if data.max_value else None])

                        compare_point = lambda p1, p2, p3: chart_color \
                            if abs(p1) < abs(p2) \
                            else ('#FFE90D'
                                  if abs(p2) < abs(p1) < abs(p3)
                                  else ('#FF193B' if abs(p3) < abs(p1)
                                        else chart_color
                        )
                        )

                        formula = SERVICE_DATA_SOURCE[sds_name]["formula"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else None

                        if data.current_value:
                            val = float(data.current_value) if data.current_value else 0
                            warn_val = float(data.warning_threshold) if data.warning_threshold else val
                            crit_val = float(data.critical_threshold) if data.critical_threshold else val

                            formatter_data_point = {
                                "name": sds_display_name,
                                "color": compare_point(val, warn_val, crit_val),
                                "y": eval(str(formula) + "(" + str(data.current_value) + ")")
                                if formula
                                else float(data.current_value),
                                "x": js_time
                            }
                        else:
                            formatter_data_point = {
                                "name": sds_display_name,
                                "color": chart_color,
                                "y": None,
                                "x": js_time
                            }

                        data_list.append(formatter_data_point)
                        chart_data = [{'name': result['data']['objects']['display_name'],
                                       'data': data_list,
                                       'type': result['data']['objects']['type'],
                                       'valuesuffix': result['data']['objects']['valuesuffix'],
                                       'valuetext': result['data']['objects']['valuetext']
                                      }
                        ]
                        if len(min_data_list):
                            chart_data.append(
                                {'name': str("min value").title(),
                                 'color': '#01CC14',
                                 'data': min_data_list,
                                 'type': 'line',
                                 'marker': {
                                     'enabled': False
                                 }
                                }
                            )

                        if len(max_data_list):
                            chart_data.append(
                                {'name': str("max value").title(),
                                 'color': '#FF8716',
                                 'data': max_data_list,
                                 'type': 'line',
                                 'marker': {
                                     'enabled': False
                                 }
                                }
                            )

                        if len(crit_data_list):
                            chart_data.append(
                                {'name': str("warning threshold").title(),
                                 'color': '#FFE90D',
                                 'data': warn_data_list,
                                 'type': 'line',
                                 'marker': {
                                     'enabled': False
                                 }
                                }
                            )

                        if len(warn_data_list):
                            chart_data.append(
                                {'name': str("critical threshold").title(),
                                 'color': '#FF193B',
                                 'data': crit_data_list,
                                 'type': 'line',
                                 'marker': {
                                     'enabled': False
                                 }
                                }
                            )
                    else:
                        if data.current_value:
                            formatter_data_point = {
                                "name": "Availability",
                                "color": '#70AFC4',
                                "y": float(data.current_value),
                                "x": js_time
                            }
                            formatter_data_point_down = {
                                "name": "UnAvailability",
                                "color": '#FF193B',
                                "y": 100.00 - float(data.current_value),
                                "x": js_time
                            }
                        else:
                            formatter_data_point = {
                                "name": str(data.data_source).upper(),
                                "color": '#70AFC4',
                                "y": None,
                                "x": js_time
                            }
                            formatter_data_point_down = {
                                "name": "UnAvailability",
                                "color": '#FF193B',
                                "y": None,
                                "x": js_time
                            }

                        data_list.append(formatter_data_point)
                        warn_data_list.append(formatter_data_point_down)

                        chart_data = [{'name': 'Availability',
                                       'data': data_list,
                                       'type': result['data']['objects']['type'],
                                       'valuesuffix': result['data']['objects']['valuesuffix'],
                                       'valuetext': result['data']['objects']['valuetext']
                                      },
                                      {'name': 'UnAvailability',
                                       'color': '#FF193B',
                                       'data': warn_data_list,
                                       'type': 'column',
                                       'marker': {
                                           'enabled': False
                                       }}
                        ]


            #this ensures a further good presentation of data w.r.t thresholds

            result['success'] = 1
            result['message'] = 'Device Performance Data Fetched Successfully To Plot Graphs.'
            result['data']['objects']['chart_data'] = chart_data

        return result

    def get_performance_data_result(self, performance_data, data_source=None):
        chart_data = list()
        if performance_data:
            data_list, warn_data_list, crit_data_list, aggregate_data = list(), list(), list(), dict()
            min_data_list = list()
            max_data_list = list()
            for data in performance_data:
                temp_time = data.sys_timestamp

                if temp_time in aggregate_data:
                    continue
                else:
                    aggregate_data[temp_time] = data.sys_timestamp

                    #time in javascript format
                    js_time = data.sys_timestamp * 1000
                    #time in javascript format

                    sds_name = str(data.data_source).strip().lower()

                    sds_display_name = \
                        SERVICE_DATA_SOURCE[sds_name]["display_name"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else str(data.data_source).upper()

                    self.result['data']['objects']['display_name'] = sds_display_name

                    self.result['data']['objects']['type'] = \
                        SERVICE_DATA_SOURCE[sds_name]["type"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else "area"

                    self.result['data']['objects']['valuesuffix'] = \
                        SERVICE_DATA_SOURCE[sds_name]["valuesuffix"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else ""

                    self.result['data']['objects']['valuetext'] = \
                        SERVICE_DATA_SOURCE[sds_name]["valuetext"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else str(data.data_source).upper()

                    self.result['data']['objects']['plot_type'] = 'charts'

                    chart_color = \
                        SERVICE_DATA_SOURCE[sds_name]["chart_color"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else '#70AFC4'

                    if sds_name not in ["availability"]:
                        #only display warning if there exists a warning
                        if data.warning_threshold:
                            warn_data_list.append([js_time, float(data.warning_threshold)])

                        #only display critical if there exists a critical
                        if data.critical_threshold:
                            crit_data_list.append([js_time, float(data.critical_threshold)])

                        ###to draw each data point w.r.t threshold we would need to use the following
                        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["show_min"]:
                            min_data_list.append([js_time, float(data.min_value)
                            if data.min_value else None])

                        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["show_max"]:
                            max_data_list.append([js_time, float(data.max_value)
                            if data.max_value else None])

                        compare_point = lambda p1, p2, p3: chart_color \
                            if abs(p1) < abs(p2) \
                            else ('#FFE90D'
                                  if abs(p2) < abs(p1) < abs(p3)
                                  else ('#FF193B' if abs(p3) < abs(p1)
                                        else chart_color
                        )
                        )

                        formula = SERVICE_DATA_SOURCE[sds_name]["formula"] \
                            if sds_name in SERVICE_DATA_SOURCE \
                            else None

                        if data.current_value:
                            val = float(data.current_value) if data.current_value else 0
                            warn_val = float(data.warning_threshold) if data.warning_threshold else val
                            crit_val = float(data.critical_threshold) if data.critical_threshold else val

                            formatter_data_point = {
                                "name": sds_display_name,
                                "color": compare_point(val, warn_val, crit_val),
                                "y": eval(str(formula) + "(" + str(data.current_value) + ")")
                                if formula
                                else float(data.current_value),
                                "x": js_time
                            }
                        else:
                            formatter_data_point = {
                                "name": sds_display_name,
                                "color": '#70AFC4',
                                "y": None,
                                "x": js_time
                            }

                        data_list.append(formatter_data_point)
                        chart_data = [{'name': self.result['data']['objects']['display_name'],
                                       'data': data_list,
                                       'type': self.result['data']['objects']['type'],
                                       'valuesuffix': self.result['data']['objects']['valuesuffix'],
                                       'valuetext': self.result['data']['objects']['valuetext']
                                      }
                        ]
                        if len(min_data_list):
                            chart_data.append(
                                {'name': str("min value").title(),
                                 'color': '#01CC14',
                                 'data': min_data_list,
                                 'type': 'line',
                                 'marker': {
                                     'enabled': False
                                 }
                                }
                            )

                        if len(max_data_list):
                            chart_data.append(
                                {'name': str("max value").title(),
                                 'color': '#FF8716',
                                 'data': max_data_list,
                                 'type': 'line',
                                 'marker': {
                                     'enabled': False
                                 }
                                }
                            )

                        if len(crit_data_list):
                            chart_data.append(
                                {'name': str("warning threshold").title(),
                                 'color': '#FFE90D',
                                 'data': warn_data_list,
                                 'type': 'line',
                                 'marker': {
                                     'enabled': False
                                 }
                                }
                            )

                        if len(warn_data_list):
                            chart_data.append(
                                {'name': str("critical threshold").title(),
                                 'color': '#FF193B',
                                 'data': crit_data_list,
                                 'type': 'line',
                                 'marker': {
                                     'enabled': False
                                 }
                                }
                            )
                    else:
                        if data.current_value:
                            formatter_data_point = {
                                "name": "Availability",
                                "color": '#70AFC4',
                                "y": float(data.current_value),
                                "x": js_time
                            }
                            formatter_data_point_down = {
                                "name": "UnAvailability",
                                "color": '#FF193B',
                                "y": 100.00 - float(data.current_value),
                                "x": js_time
                            }
                        else:
                            formatter_data_point = {
                                "name": str(data.data_source).upper(),
                                "color": '#70AFC4',
                                "y": None,
                                "x": js_time
                            }
                            formatter_data_point_down = {
                                "name": "UnAvailability",
                                "color": '#FF193B',
                                "y": None,
                                "x": js_time
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
                                       'marker': {
                                           'enabled': False
                                       }}
                        ]


            #this ensures a further good presentation of data w.r.t thresholds

            self.result['success'] = 1
            self.result['message'] = 'Device Performance Data Fetched Successfully To Plot Graphs.'
            self.result['data']['objects']['chart_data'] = chart_data

        return self.result


class DeviceServiceDetail(View):
    """
    Utilization Stitching Per Technology Wise
    url : utilization/device/<device_id>
    get the device id and check the services associated to the device
    stitch together the device utilization
    """
    def get(self, request, service_name, device_id):
        """

        :param request: request body
        :param device_id: id of the device
        :return: chart data for utilisation services
        """
        result = {
            'success': 0,
            'message': 'Device Utilization Data not found',
            'data': {
                'meta': {},
                'objects': {
                    'plot_type': 'charts',
                    'display_name': service_name.strip().title(),
                    'valuesuffix': '  ',
                    'type': 'area',
                    'chart_data': [],
                    'valuetext': '  '
                }
            }
        }
        date_format = "%d-%m-%Y %H:%M:%S"
        #get the time
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        isSet = False
        isSet, start_date, end_date = perf_utils.get_time(start_date, end_date, date_format)
        if not isSet:
            end_date = format(datetime.datetime.now(), 'U')
            start_date = format(datetime.datetime.now() + datetime.timedelta(minutes=-180), 'U')

        device = Device.objects.get(id=device_id)

        #specially for DR devices
        technology = DeviceTechnology.objects.get(id=device.device_technology)
        dr_device = None
        if technology and technology.name.lower() in ['wimax'] and device.sector_configured_on.exists():
            dr_devices = device.sector_configured_on.filter()
            for dr_d in dr_devices:
                dr_device = dr_d.dr_configured_on
        #specially for DR devices

        device_type = DeviceType.objects.get(id=device.device_type)
        device_type_services = device_type.service.filter(name__icontains=service_name
        ).prefetch_related('servicespecificdatasource_set')

        services = device_type_services.values('name',
                                               'alias',
                                               'servicespecificdatasource__service_data_sources__name',
                                               'servicespecificdatasource__service_data_sources__alias'
        )

        service_names = list()
        sds_names = list()
        service_data_sources = {}

        for s in services:
            service_names.append(s['name'])
            temp_sds_name = s['servicespecificdatasource__service_data_sources__name']
            temp_s_name = s['name']
            sds_names.append(temp_sds_name)
            service_data_sources[temp_s_name, temp_sds_name] = \
                s['alias'] + "[ " + s['servicespecificdatasource__service_data_sources__alias'] + " ]"

        if dr_device:
            performance = PerformanceService.objects.filter(
                device_name__in=[device.device_name, dr_device.device_name],
                service_name__in=service_names,
                data_source__in=sds_names,
                sys_timestamp__gte=start_date,
                sys_timestamp__lte=end_date).using(
                    alias=device.machine.name).order_by('sys_timestamp')
        else:
            performance = PerformanceService.objects.filter(
                device_name=device.device_name,
                service_name__in=service_names,
                data_source__in=sds_names,
                sys_timestamp__gte=start_date,
                sys_timestamp__lte=end_date).using(
                    alias=device.machine.name).order_by('sys_timestamp')

        chart_data = []
        #format for chart data
        # {'name': str("min value").title(),
        #  'color': '#01CC14',
        #  'data': [js_time, value],
        #  'type': 'line',
        #  'marker': {
        #      'enabled': False
        #  }
        # }
        color = {}
        temp_chart_data = {}
        for data in performance:
            try:
                append_ip_address = ""
                if dr_device and dr_device.ip_address == data.ip_address:
                    append_ip_address += " DR: {0} ".format(data.ip_address)
                elif dr_device and dr_device.ip_address != data.ip_address:
                    append_ip_address += " {0} ".format(data.ip_address)
                else:
                    append_ip_address = ""

                if dr_device and dr_device.ip_address == data.ip_address:
                    if (data.ip_address, data.service_name, data.data_source) not in temp_chart_data:

                        temp_chart_data[data.ip_address, data.service_name, data.data_source] = {
                            'name': service_data_sources[data.service_name, data.data_source] + append_ip_address,
                            'data': [],
                            'color': SERVICE_DATA_SOURCE[
                                        data.data_source.strip().lower()
                                    ]['chart_color'],
                        }
                    js_time = data.sys_timestamp*1000
                    value = float(data.current_value)
                    temp_chart_data[data.ip_address, data.service_name, data.data_source]['data'].append([
                        js_time, value,
                    ])
                else:
                    if (data.service_name, data.data_source) not in temp_chart_data:
                        color[data.service_name, data.data_source] = perf_utils.color_picker()
                        temp_chart_data[data.service_name, data.data_source] = {
                            'name': service_data_sources[data.service_name, data.data_source],
                            'data': [],
                            'color': SERVICE_DATA_SOURCE[
                                        data.data_source.strip().lower()
                                    ]['chart_color'],
                        }
                    js_time = data.sys_timestamp*1000
                    value = float(data.current_value)
                    temp_chart_data[data.service_name, data.data_source]['data'].append([
                        js_time, value,
                    ])
            except Exception as e:
                log.exception(e.message)
                continue

        for cd in temp_chart_data:
            chart_data.append(temp_chart_data[cd])

        result = {
            'success': 1,
            'message': 'Device Utilization Data',
            'data': {
                'meta': {},
                'objects': {
                    'plot_type': 'charts',
                    'display_name': service_name.strip().title(),
                    'valuesuffix': '  ',
                    'type': 'area',
                    'chart_data': chart_data,
                    'valuetext': '  '
                }
            }
        }

        return HttpResponse(json.dumps(result), mimetype="application/json")