# -*- coding: utf-8 -*-

# import json
import ujson as json
import datetime
import time
from operator import itemgetter
import re
from django.db.models import Count, Q
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.base import View
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.dateformat import format

from device.models import Device, DeviceType, DeviceTechnology, DevicePort
from service.models import ServiceDataSource
from inventory.models import SubStation, Circuit, Sector, BaseStation, Backhaul, Customer
from performance.models import PerformanceService, PerformanceNetwork, \
    NetworkStatus, \
    ServiceStatus, InventoryStatus, \
    PerformanceStatus, PerformanceInventory, \
    Status, NetworkAvailabilityDaily, Topology, Utilization, UtilizationStatus, SpotDashboard, \
    PerformanceServiceBiHourly, PerformanceServiceHourly, PerformanceServiceDaily, PerformanceServiceWeekly, \
    PerformanceServiceMonthly, PerformanceServiceYearly, PerformanceNetworkBiHourly, PerformanceNetworkHourly, \
    PerformanceNetworkDaily, PerformanceNetworkWeekly, PerformanceNetworkMonthly, PerformanceNetworkYearly, \
    PerformanceStatusDaily, PerformanceStatusWeekly, PerformanceStatusMonthly, PerformanceStatusYearly, \
    PerformanceInventoryDaily, PerformanceInventoryWeekly, PerformanceInventoryMonthly, PerformanceInventoryYearly,\
    UtilizationBiHourly, UtilizationHourly, UtilizationDaily, UtilizationWeekly, UtilizationMonthly, UtilizationYearly

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

# Import inventory utils gateway class
from inventory.utils.util import InventoryUtilsGateway

# Import performance utils gateway class
from performance.utils.util import PerformanceUtilsGateway

# Import service utils gateway class
from service.utils.util import ServiceUtilsGateway

# Import advance filtering mixin for BaseDatatableView
from nocout.mixins.datatable import AdvanceFilteringMixin

from nocout.settings import DATE_TIME_FORMAT, LIVE_POLLING_CONFIGURATION, \
    MIN_CHART_TYPE, MAX_CHART_TYPE, AVG_CHART_TYPE, MIN_CHART_COLOR, MAX_CHART_COLOR, \
    AVG_CHART_COLOR, CACHE_TIME, \
    WARN_COLOR, CRIT_COLOR, WARN_TYPE, CRIT_TYPE, MULTI_PROCESSING_ENABLED

from performance.formulae import display_time, rta_null

# Create instance of 'ServiceUtilsGateway' class
service_utils = ServiceUtilsGateway()

##execute this globally
SERVICE_DATA_SOURCE = service_utils.service_data_sources()

import logging

log = logging.getLogger(__name__)

# Create instance of 'PerformanceUtilsGateway' class
perf_utils = PerformanceUtilsGateway()

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


class PerformanceViewsGateway:
    """
    This class works as gateway between performance views & other apps
    """

    def getLastXMonths(self, params):

        response_param1, response_param2 = getLastXMonths(params)

        return response_param1, response_param2


    def get_device_status_headers(self, page_type='network', type_of_device=None, technology=None):
        response_param1 = get_device_status_headers(
            page_type=page_type,
            type_of_device=type_of_device,
            technology=technology
        )

        return response_param1


    def get_higher_severity(self, severity_dict):
        response_param1, response_param2 = get_higher_severity(severity_dict)

        return response_param1, response_param2


    def device_current_status(self, device_object):
        response_param1, response_param2 = device_current_status(device_object)

        return response_param1, response_param2


    def device_last_down_time(self, device_object):
        response_param1 = device_last_down_time(device_object)

        return response_param1

    def initGetServiceTypePerformanceData(self):
        class_instance = GetServiceTypePerformanceData()

        return class_instance


class LivePerformance(ListView):
    """
    A generic class view for the performance view

    """
    model = NetworkStatus
    template_name = 'performance/live_perf.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        :param kwargs:
        """
        context = super(LivePerformance, self).get_context_data(**kwargs)
        page_type = self.kwargs['page_type']

        hidden_headers = [
            {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
        ]

        common_headers = [
            {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'bs_name', 'sTitle': 'BS Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'city', 'sTitle': 'City', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'state', 'sTitle': 'State', 'sWidth': 'auto', 'bSortable': True},

        ]

        polled_headers = [
            {'mData': 'packet_loss', 'sTitle': 'Packet Loss', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'latency', 'sTitle': 'Latency', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'last_updated', 'sTitle': 'Last Updated Time', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'Status Since', 'sWidth': 'auto', 'bSortable': True},
        ]

        action_headers = [
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False}
        ]

        if page_type in ["network"]:
            specific_headers = [
                {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'customer_name', 'sTitle': 'Customer', 'sWidth': 'auto', 'bSortable': True},
            ]

        elif page_type in ["customer"]:
            specific_headers = [
                {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'customer_name', 'sTitle': 'Customer', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'near_end_ip', 'sTitle': 'Near End Ip', 'sWidth': 'auto', 'bSortable': True},
            ]

        else:
            specific_headers = [
                {'mData': 'device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'bSortable': True},
            ]

        datatable_headers = hidden_headers
        datatable_headers += specific_headers
        datatable_headers += common_headers
        datatable_headers += polled_headers
        datatable_headers += action_headers

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['page_type'] = page_type
        return context


class LivePerformanceListing(BaseDatatableView, AdvanceFilteringMixin):
    """
    A generic class based view for the performance data table rendering.

    """
    model = NetworkStatus
    is_ordered = False
    is_polled = False
    is_searched = False
    is_initialised = True
    
    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    columns = [
        'id',
        'circuit_id',
        'sector_id',
        'customer_name',
        'near_end_ip',
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
        Generic function required to fetch the initial data with respect to 
        the page_type parameter in the get request requested.
        :param kwargs:
        :return: list of devices
        """

        page_type = self.request.GET.get('page_type')

        other_type = self.request.GET.get('other_type', None)

        required_value_list = ['id', 'machine__name', 'device_name', 'ip_address']

        device_tab_technology = self.request.GET.get('data_tab')
        
        devices = self.inventory_utils.filter_devices(
            organizations=kwargs['organizations'],
            data_tab=device_tab_technology,
            page_type=page_type,
            other_type=other_type,
            required_value_list=required_value_list
        )

        # preparing machine list
        machines = self.inventory_utils.prepare_machines(
            devices, machine_key='machine_name'
        )

        #preparing the polled results
        qs = self.prepare_polled_results(
            devices,
            multi_proc=MULTI_PROCESSING_ENABLED,
            machine_dict=machines
        )

        return qs

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return result_list:
        """

        # sSearch = self.request.GET.get('sSearch', None)
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            self.is_initialised = False
            self.is_searched = True
            result = self.prepare_devices(qs)
            result_list = list()
            for search_data in result:
                temp_var = json.dumps(search_data)
                search_data = json.loads(temp_var)
                for data in search_data:
                    if search_data[data]:
                        if(
                            (isinstance(search_data[data], unicode) or isinstance(search_data[data], str))
                            and
                            (search_data not in result_list)
                        ):
                            if sSearch.encode('utf-8').lower() in search_data[data].encode('utf-8').lower():
                                result_list.append(search_data)
                        else:
                            if sSearch == unicode(search_data[data]) and search_data not in result_list:
                                result_list.append(search_data)

            return self.advance_filter_queryset(result_list)
        return self.advance_filter_queryset(qs)

    def ordering(self, qs):
        """
        sorting for the table
        :param qs:
        """
        request = self.request

        page_type = request.GET['page_type']

        if page_type == 'customer':
            columns = [
                'id',
                'sector_id',
                'circuit_id',
                'customer_name',
                'near_end_ip',
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
                'sector_id',
                'circuit_id',
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

        # Number of columns that are used in sorting
        sorting_cols = 0
        if self.pre_camel_case_notation:
            try:
                sorting_cols = int(self._querydict.get('iSortingCols', 0))
            except ValueError:
                sorting_cols = 0
        else:
            sort_key = 'order[{0}][column]'.format(sorting_cols)
            while sort_key in self._querydict:
                sorting_cols += 1
                sort_key = 'order[{0}][column]'.format(sorting_cols)

        order = []
        order_columns = columns
        reverse = ''
        sort_using = ''

        for i in range(sorting_cols):
            # sorting column
            sort_dir = 'asc'
            try:
                if self.pre_camel_case_notation:
                    sort_col = int(self._querydict.get('iSortCol_{0}'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('sSortDir_{0}'.format(i))
                else:
                    sort_col = int(self._querydict.get('order[{0}][column]'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('order[{0}][dir]'.format(i))
            except ValueError:
                sort_col = 0

            sdir = '-' if sort_dir == 'desc' else ''
            reverse = True if sort_dir == 'desc' else False
            sortcol = order_columns[sort_col]

            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
                    sort_using = sc
            else:
                order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))
                sort_using = sortcol

        if order:
            self.is_initialised = False
            self.is_ordered = True
            try:
                sort_data = self.prepare_devices(qs)
                if sort_using in ['ip_address', 'near_end_ip']:
                    sorted_qs = sorted(
                        sort_data,
                        key=lambda item: int(re.sub(r'\W+', '', unicode(item[sort_using]).strip().lower())) if item[sort_using] and item[sort_using].lower() != 'na' else item[sort_using],
                        reverse=reverse
                    )
                else:
                    sorted_qs = sorted(
                        sort_data,
                        key=lambda item: unicode(item[sort_using]).strip().lower(),
                        reverse=reverse
                    )
                return sorted_qs
            except Exception, e:
                self.is_initialised = True
                self.is_ordered = False
                return qs
        else:
            return qs

    def prepare_devices(self, qs):
        """

        :param qs:
        :return:
        """
        page_type = self.request.GET.get('page_type')
        device_tab_technology = self.request.GET.get('data_tab')
        other_type = self.request.GET.get('other_type')

        if page_type == 'network':
            type_rf = 'sector'
        elif page_type == 'customer':
            type_rf = 'ss'
        else:
            type_rf = other_type
                

        device_name_list = list()

        # GET all device name list from the list
        try:
            map(lambda x: device_name_list.append(x['device_name']), qs)
        except Exception, e:
            # logger.info(e.message)
            pass

        return perf_utils.prepare_gis_devices_optimized(
            qs,
            page_type=page_type,
            technology=device_tab_technology,
            type_rf=type_rf,
            device_name_list=device_name_list
        )

    def prepare_machines(self, qs):
        """

        :param qs:
        """
        return self.inventory_utils.prepare_machines(qs, machine_key='machine_name')

    def prepare_polled_results(self, qs, multi_proc=MULTI_PROCESSING_ENABLED, machine_dict={}):
        """
        preparing polled results
        after creating static inventory first
        :param machine_dict:
        :param multi_proc:
        :param qs:
        """
        result_qs = perf_utils.polled_results(
            qs=qs,
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
        alert_page_type = page_type

        # In case of other page update page type to 'network' for alert center link
        if page_type not in ["customer", "network"]:
            alert_page_type = 'network'

        if qs:
            for dct in qs:

                try:
                    if int(dct['packet_loss']) == 100:
                        dct['latency'] = "DOWN"
                except Exception as e:
                    if str((dct['packet_loss'])) in ["100", "100.0", "100.00"]:
                        dct['latency'] = "DOWN"

                performance_url = reverse(
                    'SingleDevicePerf',
                    kwargs={
                        'page_type': page_type, 
                        'device_id': dct.get('id', 0)
                    },
                    current_app='performance'
                )

                alert_url = reverse(
                    'SingleDeviceAlertsInit',
                    kwargs={
                        'page_type': alert_page_type, 
                        'data_source' : 'down', 
                        'device_id': dct.get('id', 0)
                    },
                    current_app='alert_center'
                )

                inventory_url = reverse(
                    'device_edit',
                    kwargs={
                        'pk': dct.get('id', 0)
                    },
                    current_app='device'
                )

                dct.update(
                    actions='<a href="' + performance_url + '" title="Device Performance">\
                            <i class="fa fa-bar-chart-o text-info"></i></a>\
                            <a href="' + alert_url + '" title="Device Alert">\
                            <i class="fa fa-warning text-warning"></i></a> \
                            <a href="' + inventory_url + '" title="Device Inventory">\
                            <i class="fa fa-dropbox text-muted" ></i></a>'
                )

        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.
        :param kwargs:
        :param args:
        """

        request = self.request

        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)

        if not (self.is_searched or self.is_ordered):
            # prepare devices with GIS information
            qs = self.prepare_devices(qs=qs)

        # if the qs is empty then JSON is unable to serialize the empty
        # ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        aaData = self.prepare_results(qs)
        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }
        return ret


class GetPerfomance(View):
    """
    The Class based View to get performance page for the single device.

    """

    def get(self, request, page_type="no_page", device_id=0):
        """
        :param request:
        :param page_type:
        :param device_id:
        :return:
        """
        device = Device.objects.get(id=device_id)
        device_technology = DeviceTechnology.objects.get(id=device.device_technology).name
        realdevice = device
        bs_alias = None

        try:
            if device.sector_configured_on.exists():
                bs_alias = device.sector_configured_on.filter()[0].base_station.alias
            elif device.dr_configured_on.exists():
                bs_alias = device.dr_configured_on.filter()[0].base_station.alias
            elif device.substation_set.exists():
                bs_alias = Sector.objects.get(
                    id=Circuit.objects.get(
                        sub_station=device.substation_set.get().id
                    ).sector_id
                ).base_station.alias
            elif device.backhaul.exists() or device.backhaul_switch.exists() or device.backhaul_pop.exists() \
                or device.backhaul_aggregator.exists():
                bh_id = None
                if device.backhaul.exists():
                    bh_id = device.backhaul.get().id
                elif device.backhaul_switch.exists():
                    bh_id = device.backhaul_switch.get().id
                elif device.backhaul_pop.exists():
                    bh_id = device.backhaul_pop.get().id
                elif device.backhaul_aggregator.exists():
                    bh_id = device.backhaul_aggregator.get().id

                bs_alias = ','.join(
                    BaseStation.objects.filter(
                        backhaul= bh_id
                    ).values_list('alias', flat=True)
                )
            else:
                pass
        except Exception, e:
            # log.info(e.message)
            bs_alias = None

        if not bs_alias:
            bs_alias = realdevice.device_alias

        is_util_tab = request.GET.get('is_util', 0)

        is_dr_device = device.dr_configured_on.exists()

        # Device inventory status url
        inventory_status_url = reverse(
            'DeviceStatusUrl',
            kwargs={
                'page_type': page_type,
                'device_id': device_id
            },
            current_app='performance'
        )
        
        link_page_type = page_type
        
        # pass page type as 'network' for other tab devices for single alert page link
        if page_type in ['other'] or device.backhaul_switch.exists() or \
            device.backhaul_pop.exists() or device.backhaul_aggregator.exists():

            link_page_type = 'network'

        # alert page url
        alert_page_url = reverse(
            'SingleDeviceAlertsInit',
            kwargs={
                'page_type': link_page_type,
                'device_id': device_id,
                'data_source': 'down'
            },
            current_app='alert_center'
        )

        # inventory page url
        inventory_page_url = reverse(
            'device_edit',
            kwargs={'pk': device_id},
            current_app='device'
        )

        service_ds_url = ''
        
        try:
            # Service Data-source url
            service_ds_url = reverse(
                'get_service_data_source_url',
                kwargs={'device_id': device_id},
                current_app='performance'
            )
            service_ds_url = service_ds_url+"?is_util="+str(is_util_tab)
        except Exception, e:
            service_ds_url = 'performance/get_inventory_service_data_sources\
                            /device/'+str(device_id)+'/?is_util='+str(is_util_tab)

        page_data = {
            'page_title': page_type.capitalize(),
            'device_technology': device_technology,
            'device': device,
            'realdevice': realdevice,
            'bs_alias' : bs_alias,
            'get_status_url': inventory_status_url,
            'get_services_url': service_ds_url,
            'inventory_page_url': inventory_page_url,
            'alert_page_url': alert_page_url,
            'page_type': page_type,
            'live_poll_config': json.dumps(LIVE_POLLING_CONFIGURATION),
            'is_util_tab': int(is_util_tab),
            'is_dr_device' : is_dr_device
        }

        return render(request, 'performance/single_device_perf.html', page_data)


class SectorDashboard(ListView):
    """
    The Class based view to get sector dashboard page requested.

    """

    model = SpotDashboard
    template_name = 'performance/sector_dashboard.html'

    def get_context_data(self, **kwargs):

        """

        :param kwargs:
        :return:
        """
        context = super(SectorDashboard, self).get_context_data(**kwargs)
        # Sector Info Headers
        sector_headers = [
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto'},
            {'mData': 'sector_sector_configured_on', 'sTitle': 'Sector Configured On', 'sWidth': 'auto'},
            {'mData': 'sector_device_technology', 'sTitle': 'Technology', 'sWidth': 'auto'}
        ]

        ul_last_six_month_headers = list()
        ul_last_six_month_headers_for_report = list()

        sia_last_six_month_headers = list()
        sia_last_six_month_headers_for_report = list()

        augt_last_six_month_headers = list()
        augt_last_six_month_headers_for_report = list()

        months_index_list = list()

        # Get Last Six Month List
        last_six_months_list, months_list = getLastXMonths(6)

        try:
            # pass
            last_six_months_list.reverse()
        except Exception, e:
            # raise e
            pass

        for i in range(6):
            # Get month index from year,month tuple
            month_index = last_six_months_list[i][1] - 1
            month_name = months_list[month_index]['name']
            month_alias = months_list[month_index]['alias']

            # Months index List
            months_index_list.append(month_index)

            # Last Six Month UL Issues Headers
            ul_last_six_month_headers.append(
                {
                    'mData': 'ul_issue_'+str(i+1),
                    'sTitle': month_alias,
                    'sWidth': 'auto',
                    'bSortable': False
                }
            )
            # UL Issue Header for downloaded report
            ul_last_six_month_headers_for_report.append(
                {
                    'mData': 'ul_issue_'+str(i+1),
                    'sTitle': month_alias+"(UL Issue)",
                    'sWidth': 'auto',
                    'bSortable': False
                }
            )

            # Last Six Month SIA Headers
            sia_last_six_month_headers.append(
                {
                    'mData': 'sia_'+str(i+1),
                    'sTitle': month_alias,
                    'sWidth': 'auto',
                    'bSortable': False
                }
            )
            # SIA Header for downloaded report
            sia_last_six_month_headers_for_report.append(
                {
                    'mData': 'sia_'+str(i+1),
                    'sTitle': month_alias+"(SIA)",
                    'sWidth': 'auto',
                    'bSortable': False
                }
            )

            # Last Six Month Augmentation Headers
            augt_last_six_month_headers.append(
                {
                    'mData': 'augment_'+str(i+1),
                    'sTitle': month_alias,
                    'sWidth': 'auto',
                    'bSortable': False
                }
            )
            # Augmentation Header for downloaded report
            augt_last_six_month_headers_for_report.append(
                {
                    'mData': 'augment_'+str(i+1),
                    'sTitle': month_alias+"(Augmentation)",
                    'sWidth': 'auto',
                    'bSortable': False
                }
            )

        table_headers = []
        table_headers += sector_headers
        table_headers += ul_last_six_month_headers
        table_headers += sia_last_six_month_headers
        table_headers += augt_last_six_month_headers

        report_headers = []
        report_headers += sector_headers
        report_headers += ul_last_six_month_headers_for_report
        report_headers += sia_last_six_month_headers_for_report
        report_headers += augt_last_six_month_headers_for_report

        context['table_headers'] = json.dumps(table_headers)
        context['report_headers'] = json.dumps(report_headers)
        context['months_index'] = json.dumps(months_index_list)
        return context


class SectorDashboardListing(BaseDatatableView, AdvanceFilteringMixin):
    """ This class show sector spot dashboard listing """

    model = SpotDashboard

    # default technology
    technology = 'ALL'

    # Static info Colums
    static_columns = [
        "sector_sector_id",
        "sector_sector_configured_on",
        "sector_device_technology"
    ]

    # Calculated or polled info columns
    polled_columns = [
        "ul_issue_1",
        "ul_issue_2",
        "ul_issue_3",
        "ul_issue_4",
        "ul_issue_5",
        "ul_issue_6",
        "augment_1",
        "augment_2",
        "augment_3",
        "augment_4",
        "augment_5",
        "augment_6",
        "sia_1",
        "sia_2",
        "sia_3",
        "sia_4",
        "sia_5",
        "sia_6"
    ]

    columns = static_columns + polled_columns

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        resultset = []
        if self.technology == 'ALL':
            resultset = self.model.objects.values(*self.columns)
        else:
            resultset = self.model.objects.filter(
                sector_device_technology=self.technology
            ).values(*self.columns)

        return resultset

    def prepare_results(self, qs):

        """

        :param qs:
        :return:
        """
        report_resultset = []

        red_dot_html_string = '<i class="fa fa-circle text-danger"><span class="hide">1</span> </i>'
        no_issue_string = '-'

        for data in qs:
            report_object = {}
            report_object['sector_id'] = data['sector_sector_id']
            report_object['sector_sector_configured_on'] = data['sector_sector_configured_on']
            report_object['sector_device_technology'] = data['sector_device_technology']

            #  Last 6 months loop
            for i in range(6):
                columns_concat_counter = str(i+1)
                # Condition for ul Issue
                if data['ul_issue_'+columns_concat_counter]:
                    report_object['ul_issue_'+columns_concat_counter] = red_dot_html_string
                else:
                    report_object['ul_issue_'+columns_concat_counter] = no_issue_string

                # Condition for Augmentation
                if data['augment_'+columns_concat_counter]:
                    report_object['augment_'+columns_concat_counter] = red_dot_html_string
                else:
                    report_object['augment_'+columns_concat_counter] = no_issue_string

                # Condition for SIA
                if data['sia_'+columns_concat_counter]:
                    report_object['sia_'+columns_concat_counter] = red_dot_html_string
                else:
                    report_object['sia_'+columns_concat_counter] = no_issue_string

            #add data to report_resultset list
            report_resultset.append(report_object)

        return report_resultset

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value
        :param qs:
        """

        # sSearch = self.request.GET.get('sSearch', None)
        sSearch = self.request.GET.get('search[value]', None)

        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % self.model.__name__
            for column in self.columns[:-1]:
                # avoid search on 'added_on'
                if column == 'added_on':
                    continue
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return self.advance_filter_queryset(qs)

    def ordering(self, qs):
        """ 
         Get parameters from the request and prepare order by clause
        :param qs:
        """
        return nocout_utils.nocout_datatable_ordering(self, qs, self.static_columns)

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        :param kwargs:
        :param args:
        """

        request = self.request
        self.initialize(*args, **kwargs)

        self.technology = request.GET['technology'] if 'technology' in request.GET else 'ALL'

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        aaData = self.prepare_results(qs)

        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }

        return ret


class InventoryDeviceStatus(View):
    """
    Class Based Generic view to return a Single Device Status

    """

    def get(self, request, page_type, device_id):
        """
        Handles the Get Request to return a single device status w.r.t page_type and device id requested.

        :param device_id:
        :param page_type:
        :param request:
        """
        result = {
            'success': 0,
            'message': 'Inventory Device Status Not Fetched Successfully.',
            'data': {
                'meta': {},
                'objects': {
                    "headers": list(),
                    "values": list(),
                    "is_others_page": 0
                }
            }
        }

        # Inventory Device Type Flags
        is_ss = False
        is_sector = False
        is_bh = False
        is_other = False

        page_type = self.kwargs.get('page_type')
        
        # type of device flag
        type_of_device = ""
        list_devices_invent_info = ''

        # Get Device Object
        device = Device.objects.get(id=device_id)

        try:
            device_tech = DeviceTechnology.objects.get(pk=device.device_technology).name
        except Exception, e:
            device_tech = ''
        
        # check that the device is SS, sector, BH or other and update the flag accordingly
        if device.substation_set.exists():
            is_ss = True
            type_of_device = "sub_station"
            type_rf = 'ss'
        elif device.sector_configured_on.exists() or device.dr_configured_on.exists():
            is_sector = True
            type_of_device = "sector"
            type_rf = 'sector'
        elif device.backhaul.exists():
            is_bh = True
            type_of_device = "backhaul"
            type_rf = 'backhaul'
            page_type = 'other'
        elif device.backhaul_switch.exists() or device.backhaul_pop.exists() or device.backhaul_aggregator.exists():
            is_other = True
            type_of_device = "other"
            type_rf = type_of_device
            page_type = type_of_device
            result['data']['objects']['is_others_page'] = 1

        device_obj = {
            "device_name" : device.device_name,
            "ip_address" : device.ip_address,
            "mac_address" : device.mac_address,
            "machine_name" : device.machine.name,
            "device_id" : device.id
        }
        devices_info_list = [device_obj]
        device_name_list = [device.device_name]

        # If wimax device then append 
        # corresponding DR or Sector device in list.
        if device_tech in ['WiMAX'] and page_type in ['network']:
            if device.sector_configured_on.exists():
                dr_device_name = Sector.objects.filter(
                    sector_configured_on=device.id
                ).values(
                    'dr_configured_on__id',
                    'dr_configured_on__device_name',
                    'dr_configured_on__ip_address',
                    'dr_configured_on__mac_address',
                    'dr_configured_on__machine__name'
                )[:1]

                if dr_device_name and dr_device_name[0]['dr_configured_on__device_name']:
                    devices_info_list.append({
                        "device_name" : dr_device_name[0]['dr_configured_on__device_name'],
                        "ip_address" : dr_device_name[0]['dr_configured_on__ip_address']+"(DR)",
                        "mac_address" : dr_device_name[0]['dr_configured_on__mac_address'],
                        "device_id" : dr_device_name[0]['dr_configured_on__id'],
                        "machine_name" : dr_device_name[0]['dr_configured_on__machine__name']
                    })
                    device_name_list.append(dr_device_name[0]['dr_configured_on__device_name'])

            # Check for DR device
            if device.dr_configured_on.exists():
                devices_info_list[0]['ip_address'] += '(DR)'
                sector_device_name = Sector.objects.filter(
                    dr_configured_on=device.id
                ).values(
                    'sector_configured_on__id',
                    'sector_configured_on__device_name',
                    'sector_configured_on__ip_address',
                    'sector_configured_on__mac_address',
                    'sector_configured_on__machine__name'
                )[:1]

                if sector_device_name and sector_device_name[0]['sector_configured_on__device_name']:
                    devices_info_list.append({
                        "device_name" : sector_device_name[0]['sector_configured_on__device_name'],
                        "ip_address" : sector_device_name[0]['sector_configured_on__ip_address'],
                        "mac_address" : sector_device_name[0]['sector_configured_on__mac_address'],
                        "device_id" : sector_device_name[0]['sector_configured_on__id'],
                        "machine_name" : sector_device_name[0]['sector_configured_on__machine__name']
                    })
                    device_name_list.append(sector_device_name[0]['sector_configured_on__device_name'])

        if devices_info_list:
            if device_tech in ['WiMAX'] or page_type == 'other':
                is_single_call = True
            else:
                is_single_call = False

            list_devices_invent_info = perf_utils.prepare_gis_devices_optimized(
                devices_info_list,
                page_type=page_type,
                technology=device_tech,
                type_rf=type_rf,
                device_name_list=device_name_list,
                is_single_call=is_single_call
            )

            # list_devices_invent_info = perf_utils.prepare_gis_devices(devices_info_list, page_type=None)

            if list_devices_invent_info:
                lowered_device_tech = list_devices_invent_info[0]['device_technology'].lower()
                # If SS device & of PMP or Wimax Technology then fetch the qos_bandwidth from distributed DB
                if page_type == 'customer' and lowered_device_tech in ['pmp', 'wimax']:
                    # get device name from fetched info
                    device_name = list_devices_invent_info[0]['device_name']
                    # get machine name from fetched info
                    machine_name = list_devices_invent_info[0]['machine_name']
                    service_name = ''
                    ds_name = ''
                    
                    # GET Service & DS as per the technology
                    if lowered_device_tech in ['pmp']:
                        service_name = 'cambium_qos_invent'
                        ds_name = 'bw_dl_sus_rate'
                    elif lowered_device_tech in ['wimax']:
                        service_name = 'wimax_qos_invent'
                        ds_name = 'dl_qos'

                    # If we have device_name, machine_name, service & db only then proceed
                    if device_name and machine_name and service_name and ds_name:
                        invent_status_obj = InventoryStatus.objects.filter(
                            device_name=device_name,
                            service_name=service_name,
                            data_source=ds_name
                        ).order_by('-sys_timestamp').using(alias=machine_name)[:1]

                        if invent_status_obj and invent_status_obj[0].current_value:
                            list_devices_invent_info[0]['qos_bw'] = invent_status_obj[0].current_value

        # Format fetched inventory data in desired format
        resultant_data = self.prepareInventoryStatusResult(
            dataset=list_devices_invent_info,
            page_type=page_type,
            type_of_device=type_of_device,
            technology=device_tech
        )

        result['success'] = 1
        result['message'] = 'Inventory Device Status Fetched Successfully.'
        result['data']['objects'] = resultant_data

        return HttpResponse(json.dumps(result), content_type="application/json")

    def prepareInventoryStatusResult(
        self,
        dataset=[],
        page_type='network',
        type_of_device='sector',
        technology_key='device_technology',
        technology=None
    ):

        if not len(dataset):
            return []

        resultant_data = []

        headers_list = get_device_status_headers(
            page_type,
            type_of_device,
            technology
        )
        
        for data in dataset:
            # deep copy headers object
            new_headers = json.loads(json.dumps(headers_list))
            for header in new_headers:
                header_key = header["name"]
                if header_key in data:
                    header["value"] = data[header_key]
                    if header["value"] and header["value"] != 'NA':
                        try:
                            header["url"] = reverse(
                                header["url_name"],
                                kwargs={ header["kwargs_name"] : data[header["pk_key"]] },
                                current_app=header["app_name"]
                            )
                        except Exception, e:
                            header["url"] = ''
                    else:  # If no value then show NA
                        header["value"] = 'NA' 
                       

            resultant_data.append(new_headers)

        return resultant_data


class InventoryDeviceServiceDataSource(View):
    """
    Generic Class based View for to fetch Inventory Device Service Data Source.

    """

    def get(self, request, device_id):
        """
        Handles the get Request w.r.t to the page type and device id requested

        :param device_id:
        :param request:
        :return result
        """
        is_util_tab = request.GET.get('is_util',0)
        service_view_type = request.GET.get('service_view_type','normal')

        result = {
            'success': 0,
            'message': 'Services Data Source Not Fetched Successfully.',
            'data': {
                'meta': {
                    'services_list' : []
                },
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

        # if is_util_tab is 1 then make isActive key of utilization_top_tab to 1
        if int(is_util_tab):
            result['data']['objects']['network_perf_tab']["isActive"] = 0
            result['data']['objects']['utilization_top_tab']["isActive"] = 1

        device = Device.objects.get(id=device_id)
        device_type = DeviceType.objects.get(id=device.device_type)
        services_list = [{
            'id' : 'ping',
            'title' : 'Ping'
        }]

        if service_view_type == 'normal':

            result['data']['objects']['network_perf_tab']["info"].append({
                'name': "pl",
                'title': "Packet Drop",
                'url': 'performance/service/ping/service_data_source/pl/device/' + str(device_id),
                'active': 0,
                'service_type_tab': 'network_perf_tab'
            })

            result['data']['objects']['network_perf_tab']["info"].append({
                'name': "rta",
                'title': "Latency",
                'url': 'performance/service/ping/service_data_source/rta/device/' + str(device_id),
                'active': 0,
                'service_type_tab': 'network_perf_tab'
            })

            if device.substation_set.exists():
                result['data']['objects']['network_perf_tab']["info"].append({
                    'name': "rf",
                    'title': "RF Latency",
                    'url': 'performance/service/rf/service_data_source/rf/device/' + str(device_id),
                    'active': 0,
                    'service_type_tab': 'network_perf_tab'
                })

            is_bh = False
            excluded_bh_data_sources = []
            if device.backhaul.exists():
                # if the backhaul exists, that means we need to check for the PORT
                # if there is a port
                try:
                    those_ports = device.backhaul.get().basestation_set.filter().values_list('bh_port_name', flat=True)

                    bh_data_sources = ServiceDataSource.objects.filter(
                        name__in=DevicePort.objects.filter(alias__in=those_ports).values_list('name', flat=True)
                    ).values_list('name', flat=True)

                    excluded_bh_data_sources = list(ServiceDataSource.objects.filter(
                        name__in=DevicePort.objects.filter().values_list('name', flat=True)
                    ).exclude(
                        name__in=bh_data_sources).values_list('name', flat=True))

                    excluded_bh_data_sources_status = [str(x)+"_state" for x in excluded_bh_data_sources]

                    excluded_bh_data_sources += excluded_bh_data_sources_status

                    is_bh = True
                except Exception as e:
                    log.exception('{0} {1}', filter(type(e), e.message))
                    is_bh = False

            device_type_services = device_type.service.filter().prefetch_related('servicespecificdatasource_set')

            for service in device_type_services:
                service_name = service.name.strip().lower()
                desired_sds = service.service_data_sources.filter()
                services_list.append({
                    'id' : service_name,
                    'title' : service.alias.strip()
                })
                if is_bh:
                    desired_sds = service.service_data_sources.exclude(name__in=excluded_bh_data_sources).filter()

                for service_data_source in desired_sds:
                    sds_name = service_data_source.name.strip().lower()

                    if service_data_source.show_performance_center:
                        sds_info = {
                                    'name': service_data_source.name,
                                    'title': service.alias.strip() +
                                            "<br> [ " +
                                            service_data_source.alias.strip() +
                                            " ] <br>",
                                    'url': 'performance/service/' + service_name +
                                           '/service_data_source/' + sds_name +
                                           '/device/' + str(device_id),
                                    'active': 0,
                                }
                    else:
                        continue

                    if '_status' in service_name:
                        result['data']['objects']['service_status_tab']["info"].append(sds_info)

                    elif '_invent' in service_name:
                        result['data']['objects']['inventory_status_tab']["info"].append(sds_info)
                    elif 'topology' in service_name:
                        continue
                    else:
                        result['data']['objects']['service_perf_tab']["info"].append(sds_info)

        else:
            result['data']['objects']['network_perf_tab']["info"].append({
                'name': "ping-all",
                'title': "Ping",
                'url': 'performance/service/ping/service_data_source/all/device/' + str(device_id) +'?service_view_type=unified',
                'active': 0,
                'service_type_tab': 'network_perf_tab'
            })

            device_type_services = device_type.service.filter().prefetch_related('servicespecificdatasource_set')

            for service in device_type_services:
                service_name = service.name.strip().lower()
                services_list.append({
                    'id' : service_name,
                    'title' : service.alias.strip()
                })
                sds_info = {
                    'name': service_name,
                    'title': service.alias.strip(),
                    'url': 'performance/service/' + service_name +
                           '/service_data_source/all/device/' + str(device_id) +'?service_view_type=unified',
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

        result['success'] = 1
        result['data']['meta']['services_list'] = services_list
        result['message'] = 'Substation Devices Services Data Source Fetched Successfully.'
        return HttpResponse(json.dumps(result), content_type="application/json")


class GetServiceStatus(View):
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
                    'pl_status' : None,
                    'status': None,
                    'age': None,
                    'last_down_time': None,
                    'severity': None
                }
            }
        }

        date_format = "%d-%m-%Y %H:%M:%S"

        device = Device.objects.get(id=int(device_id))
        inventory_device_name = device.device_name
        inventory_device_machine_name = device.machine.name  # Device Machine Name required in Query to fetch data.

        #get the current status
        #if the current status is OK
        #check when was the element last down

        severity, a = device_current_status(device_object=device)
        last_down_time = a['down'] if(a and 'down' in a) else ""
        age = a['age'] if(a and 'age' in a) else ""

        if age:
            try:
                age = datetime.datetime.fromtimestamp(float(age)).strftime(DATE_TIME_FORMAT)
            except Exception, e:
                age = age

        if last_down_time:
            try:
                last_down_time = datetime.datetime.fromtimestamp(float(last_down_time)).strftime(DATE_TIME_FORMAT)
            except Exception, e:
                last_down_time = last_down_time

        severity_status = severity.lower().strip() if severity else None

        self.result = {
            'success': 1,
            'message': 'Service Status Fetched Successfully',
            'data': {
                'meta': {},
                'objects': {
                    'perf': None,
                    'last_updated': None,
                    'pl_status' : severity_status,
                    'status': None,
                    'age': age,
                    'last_down_time': last_down_time
                }
            }
        }

        if service_data_source_type in ['pl', 'rta']:
            performance_data_query_set = NetworkStatus.objects.filter(
                device_name=inventory_device_name,
                service_name=service_name,
                data_source=service_data_source_type
            ).using(alias=inventory_device_machine_name)
        elif "rf" == service_name and "rf" == service_data_source_type:
            performance_data_query_set = None

        elif(
            service_name in ['util', 'topology', 'availability']
            or
            service_data_source_type in ['util', 'availability', 'topology']
        ):
            performance_data_query_set = None

        elif '_status' in service_name:
            performance_data_query_set = Status.objects.filter(
                device_name=inventory_device_name,
                service_name=service_name,
                data_source=service_data_source_type
            ).using(alias=inventory_device_machine_name)

        elif '_invent' in service_name:
            performance_data_query_set = InventoryStatus.objects.filter(
                device_name=inventory_device_name,
                service_name=service_name,
                data_source=service_data_source_type
            ).using(alias=inventory_device_machine_name)

        elif '_kpi' in service_name:
            performance_data_query_set = UtilizationStatus.objects.filter(
                device_name=inventory_device_name,
                service_name=service_name,
                data_source=service_data_source_type
            ).using(alias=inventory_device_machine_name)

        else:
            performance_data_query_set = ServiceStatus.objects.filter(
                device_name=inventory_device_name,
                service_name=service_name,
                data_source=service_data_source_type
            ).using(alias=inventory_device_machine_name)

        # IF device is not down only then fetch the severity count
        if severity_status and severity_status not in ['down', 'critical', 'crit']:
            # Calculate the severity of current device from all the Models
            severity_count = self.get_status_severity(
                device_name=inventory_device_name,
                machine_name=inventory_device_machine_name
            )
        else:
            severity_count = {
                "ok": "X",
                "warn": "X",
                "crit": "X",
                "unknown": "X"
            }

        self.result['data']['objects']['severity'] = severity_count

        if performance_data_query_set:
            performance_data = performance_data_query_set

            try:
                current_value = self.formulate_data(
                    performance_data[0].current_value,
                    service_data_source_type
                )
                last_updated = datetime.datetime.fromtimestamp(
                    float(performance_data[0].sys_timestamp)
                ).strftime(DATE_TIME_FORMAT)
                severity_val = performance_data[0].severity.lower().strip() if performance_data[0].severity else None

                self.result['data']['objects']['perf'] = current_value
                self.result['data']['objects']['last_updated'] = last_updated
                self.result['data']['objects']['status'] = severity_val
            except Exception as e:
                log.exception(e.message)

        return HttpResponse(json.dumps(self.result), content_type="application/json")

    def get_status_severity(
        self,
        device_name=None,
        machine_name=None
    ):
        """
        This function gets the severity count for all services & datasource combination in status tables.
        :param machine_name:
        :param device_name:
        """
        severity_count_dict = {
            "ok": 0,
            "warn": 0,
            "crit": 0,
            "unknown": 0,
        }

        # If any of the params not exists the return
        if not device_name or not machine_name:
            return severity_count_dict

        # Network Status Severity
        # network_severity = NetworkStatus.objects.filter(
        #     device_name=device_name
        # ).values_list('severity', flat=True).using(alias=machine_name)

        # Status Status Severity
        status_severity = Status.objects.filter(
            device_name=device_name
        ).values_list('severity', flat=True).using(alias=machine_name)

        # Inventory Status Severity
        invent_severity = InventoryStatus.objects.filter(
            device_name=device_name
        ).values_list('severity', flat=True).using(alias=machine_name)

        # Utilization Status Severity
        utilization_severity = UtilizationStatus.objects.filter(
            device_name=device_name
        ).values_list('severity', flat=True).using(alias=machine_name)

        # Service Status Severity
        service_severity = ServiceStatus.objects.filter(
            device_name=device_name
        ).values_list('severity', flat=True).using(alias=machine_name)

        total_severity_list = list()

        # Concat all severity list fetched from all Model
        # total_severity_list += list(network_severity)
        total_severity_list += list(status_severity)
        total_severity_list += list(invent_severity)
        total_severity_list += list(utilization_severity)
        total_severity_list += list(service_severity)

        for severity in total_severity_list:
            if severity:
                if severity.lower() in ['ok', 'success', 'up']:
                    severity_count_dict['ok'] += 1
                elif severity.lower() in ['warn', 'warning']:
                    severity_count_dict['warn'] += 1
                elif severity.lower() in ['crit', 'critical', 'down']:
                    severity_count_dict['crit'] += 1
                else:
                    severity_count_dict['unknown'] += 1

        return severity_count_dict

    def formulate_data(self, current_value, service_data_source_type):
        """

        :param current_value: current value for the service
        :param service_data_source_type: current value to be transformed
        """
        if service_data_source_type == 'uptime':
            if current_value:
                tt_sec = float(current_value)
                return display_time(tt_sec)
        else:
            return current_value


class ServiceDataSourceHeaders(ListView):
    """
    A generic class based view for the single device page ServiceDataSourceHeaders.
    """
    model = PerformanceService
    template_name = 'performance/single_device_perf.html'

    def get_context_data(self, **kwargs):

        """

        :param kwargs:
        :return:
        """
        context = super(ServiceDataSourceHeaders, self).get_context_data(**kwargs)

        datatable_headers = [
            {'mData': 'current_value', 'sTitle': 'Current Value', 'sWidth': 'auto'},
            {'mData': 'severity', 'sTitle': 'Severity', 'sWidth': 'auto'},
            {'mData': 'warning_threshold', 'sTitle': 'Warning Threshold', 'sWidth': 'auto'},
            {'mData': 'critical_threshold', 'sTitle': 'Critical Threshold', 'sWidth': 'auto'},
            {'mData': 'sys_timestamp', 'sTitle': 'Time', 'sWidth': 'auto'},
            {'mData': 'data_source', 'sTitle': 'Data Source', 'sWidth': 'auto'},
            {'mData': 'service_name', 'sTitle': 'Service', 'sWidth': 'auto'},
            {'mData': 'min_value', 'sTitle': 'Min. Value', 'sWidth': 'auto'},
            {'mData': 'max_value', 'sTitle': 'Max. Value', 'sWidth': 'auto'},
            {'mData': 'avg_value', 'sTitle': 'Avg. Value', 'sWidth': 'auto'},
            {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'auto'}
        ]

        context['datatable_headers'] = json.dumps(datatable_headers)

        return context


class ServiceDataSourceListing(BaseDatatableView, AdvanceFilteringMixin):
    """
    A generic class based view for the single device page ServiceDataSourceListing rendering.

    """
    model = PerformanceService

    columns = [
        'current_value',
        'severity',
        'warning_threshold',
        'critical_threshold',
        'sys_timestamp',
        'data_source',
        'service_name',
        'min_value',
        'max_value',
        'avg_value',
        'ip_address'
    ]

    order_columns = columns

    isHistorical = False

    formula = None

    data_source = ''

    perf_data_instance = ''

    parameters = {}

    inventory_device_machine_name = ""

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        # If params not initialized the init them by calling initialize_params
        if not self.perf_data_instance or not self.parameters:
            self.initialize_params()

        resultset = self.perf_data_instance.get_performance_data(
            **self.parameters
        ).using(alias=self.inventory_device_machine_name)

        updated_resultset = resultset.values(*self.columns).order_by('-sys_timestamp')

        return updated_resultset

    def initialize_params(self):

        """
        This function initializes public variables of this class
        """

        # REQUIRED GET PARAMS
        device_id = self.kwargs['device_id']
        service = self.kwargs['service_name']
        data_source = self.kwargs['service_data_source_type']
        data_for = self.request.GET.get('data_for', 'live')

        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        
        date_format = DATE_TIME_FORMAT
        device = Device.objects.get(id=int(device_id))
        inventory_device_name = device.device_name

        service_view_type = self.request.GET.get('service_view_type')
        is_unified_view = service_view_type and service_view_type == 'unified'

        self.data_source = self.kwargs['service_data_source_type']

        # Create instance of "GetServiceTypePerformanceData" class
        self.perf_data_instance = GetServiceTypePerformanceData()

        if data_for != 'live':
            self.isHistorical = True
            # Device Machine Name required in Query to fetch data.
            self.inventory_device_machine_name = 'default'
        else:
            # Device Machine Name required in Query to fetch data.
            self.inventory_device_machine_name = device.machine.name


        isSet, start_date, end_date = perf_utils.get_time(start_date, end_date, date_format, data_for)

        if not isSet and data_for == 'live':
            now_datetime = datetime.datetime.now()
            end_date = float(format(now_datetime, 'U'))
            start_date = float(format(now_datetime + datetime.timedelta(minutes=-180), 'U'))

        # Update the DS name when it is not in 'pl','rta' or 'availability' (<SERVICE_NAM>_<DS_NAME>)
        if self.data_source not in ['pl', 'rta', 'availability']:
            self.data_source = str(service)+"_"+str(self.data_source)

        if is_unified_view:
            for sds in SERVICE_DATA_SOURCE:
                if not self.formula:
                    if service.strip() in sds and SERVICE_DATA_SOURCE[sds]['type'] == 'table':
                        self.formula = SERVICE_DATA_SOURCE[sds]['formula']
                else:
                    break

            self.columns.append('min_value')
            self.columns.append('max_value')
        else:
            # check for the formula
            if self.data_source in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[self.data_source]['formula']:
                self.formula = SERVICE_DATA_SOURCE[self.data_source]['formula']

            if self.data_source in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[self.data_source]["show_min"]:
                if 'min_value' not in self.columns:
                    self.columns.append('min_value')

            if self.data_source in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[self.data_source]["show_max"]:
                if 'max_value' not in self.columns:
                    self.columns.append('max_value')


        if data_for == 'bihourly':
            self.model = PerformanceServiceBiHourly
        elif data_for == 'hourly':
            self.model = PerformanceServiceHourly
        elif data_for == 'daily':
            self.model = PerformanceServiceDaily
        elif data_for == 'weekly':
            self.model = PerformanceServiceWeekly
        elif data_for == 'monthly':
            self.model = PerformanceServiceMonthly
        elif data_for == 'yearly':
            self.model = PerformanceServiceYearly

        if (service == 'ping' or data_source in ['pl', 'rta']) and data_source not in ['rf']:
        # if data_source in ['pl', 'rta']:
            if data_for == 'bihourly':
                self.model = PerformanceNetworkBiHourly
            elif data_for == 'hourly':
                self.model = PerformanceNetworkHourly
            elif data_for == 'daily':
                self.model = PerformanceNetworkDaily
            elif data_for == 'weekly':
                self.model = PerformanceNetworkWeekly
            elif data_for == 'monthly':
                self.model = PerformanceNetworkMonthly
            elif data_for == 'yearly':
                self.model = PerformanceNetworkYearly
            else:
                self.model = PerformanceNetwork        

        if "_status" in service:
            if not isSet and data_for == 'live':
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(days=-1), 'U')

            if data_for == 'daily':
                self.model = PerformanceStatusDaily
            elif data_for == 'weekly':
                self.model = PerformanceStatusWeekly
            elif data_for == 'monthly':
                self.model = PerformanceStatusMonthly
            elif data_for == 'yearly':
                self.model = PerformanceStatusYearly
            else:
                self.model = PerformanceStatus

        elif '_invent' in service:

            if not isSet and data_for == 'live':
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(weeks=-1), 'U')

            if data_for == 'daily':
                self.model = PerformanceInventoryDaily
            elif data_for == 'weekly':
                self.model = PerformanceInventoryWeekly
            elif data_for == 'monthly':
                self.model = PerformanceInventoryMonthly
            elif data_for == 'yearly':
                self.model = PerformanceInventoryYearly
            else:
                self.model = PerformanceInventory
        elif '_kpi' in service:
            if data_for == 'bihourly':
                self.model = UtilizationBiHourly
            elif data_for == 'hourly':
                self.model = UtilizationHourly
            elif data_for == 'daily':
                self.model = UtilizationDaily
            elif data_for == 'weekly':
                self.model = UtilizationWeekly
            elif data_for == 'monthly':
                self.model = UtilizationMonthly
            elif data_for == 'yearly':
                self.model = UtilizationYearly
            else:
                self.model = Utilization

        self.parameters = {
            'model': self.model,
            'start_time': start_date,
            'end_time': end_date,
            'devices': [inventory_device_name],
            'services': [service],
            'sds': [data_source]
        }

        return True

    def prepare_results(self, qs):
        """

        :param qs:
        :return:
        """
        data = []
        
        service_view_type = self.request.GET.get('service_view_type')
        is_unified_view = service_view_type and service_view_type == 'unified'

        for item in qs:
            datetime_obj = ''

            if item['sys_timestamp']:
                datetime_obj = datetime.datetime.fromtimestamp(item['sys_timestamp'])

            current_val = eval(str(self.formula) + "(" + str(item['current_value']) + ")") \
                if self.formula else item['current_value']
            
            min_val = eval(str(self.formula) + "(" + str(item['min_value']) + ")") \
                if self.formula else item['min_value']

            max_val = eval(str(self.formula) + "(" + str(item['max_value']) + ")") \
                if self.formula else item['max_value']

            avg_val = eval(str(self.formula) + "(" + str(item['avg_value']) + ")") \
                if self.formula else item['avg_value']

            item.update(
                current_value=current_val,
                sys_timestamp=datetime_obj.strftime(
                    # '%d-%m-%Y %H:%M'
                    DATE_TIME_FORMAT
                ) if item['sys_timestamp'] != "" else ""
            )

            if self.data_source in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[self.data_source]["show_min"]:
                item.update(
                    min_value=min_val
                )

            if self.data_source in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[self.data_source]["show_max"]:
                item.update(
                    max_value=max_val
                )

            if self.isHistorical or is_unified_view:

                item.update(
                    min_value=min_val,
                    max_value=max_val,
                    avg_value=avg_val
                )

            # Add data to list
            data.append(item)

        return data

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value
        :param qs:
        """

        # sSearch = self.request.GET.get('sSearch', None)
        sSearch = self.request.GET.get('search[value]', None)

        if sSearch:

            try:
                main_resultset = self.perf_data_instance.get_performance_data(
                    **self.parameters
                ).using(alias=self.inventory_device_machine_name)

                qs = main_resultset.filter(
                    Q(max_value__icontains=sSearch)
                    |
                    Q(min_value__icontains=sSearch)
                    |
                    Q(current_value__icontains=sSearch)
                    |
                    Q(ip_address__icontains=sSearch)
                    |
                    Q(severity__icontains=sSearch)
                    |
                    Q(warning_threshold__icontains=sSearch)
                    |
                    Q(critical_threshold__icontains=sSearch)
                ).values(*self.columns).order_by('-sys_timestamp')

            except Exception, e:
                pass

        return self.advance_filter_queryset(qs)

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        :param qs:
        """
        return nocout_utils.nocout_datatable_ordering(self, qs, self.columns)

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        :param kwargs:
        :param args:
        """

        request = self.request
        self.initialize(*args, **kwargs)

        # If params not initialized the init them by calling initialize_params
        if not self.perf_data_instance or not self.parameters:
            self.initialize_params()

        try:
            # Create Ordering columns from GET request
            total_columns_count = int(self.request.GET.get('iColumns', len(self.columns)))
            new_ordering_columns = list()
            
            for i in range(total_columns_count):
                if self.request.GET.get('mDataProp_%s' % i) not in new_ordering_columns:
                    new_ordering_columns.append(self.request.GET.get('mDataProp_%s' % i))

            # Update new ordering columns in global variable
            self.order_columns = new_ordering_columns
        except Exception, e:
            pass

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        aaData = self.prepare_results(qs)

        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }
        return ret


class GetServiceTypePerformanceData(View):
    """
    Generic Class based View to Fetch the Performance Data.
    """

    def get(self, request, service_name, service_data_source_type, device_id):
        """
        Handles the get request to fetch performance data w.r.t to arguments requested.

        :param device_id:
        :param service_data_source_type:
        :param service_name:
        :param request:
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

        # GET param to check the the data is requested for live data or historical data
        data_for = self.request.GET.get('data_for', 'live')
        # initialize historical data flag
        is_historical_data = False

        # If call is for historical data then enable "is_historical_data" flag
        if data_for != 'live':
            is_historical_data = True

        # for wimax devices special case
        dr_device = None

        # for topology service these would come in handy
        sector_object = None
        sector_device = None

        date_format = DATE_TIME_FORMAT
        device = Device.objects.get(id=int(device_id))
        inventory_device_name = device.device_name
        inventory_device_machine_name = device.machine.name  # Device Machine Name required in Query to fetch data.

        try:
            technology = DeviceTechnology.objects.get(id=device.device_technology)
        except:
            return HttpResponse(json.dumps(self.result), content_type="application/json")

        # If DR configured device & sector configured deivce flags
        is_dr_device = device.dr_configured_on.exists()
        is_sector_device = device.sector_configured_on.exists()

        # date time settings
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        isSet, start_date, end_date = perf_utils.get_time(start_date, end_date, date_format, data_for)

        if not isSet and data_for == 'live':
            now_datetime = datetime.datetime.now()
            end_date = float(format(now_datetime, 'U'))
            start_date = float(format(now_datetime + datetime.timedelta(minutes=-180), 'U'))

        if service_data_source_type.strip() not in ['topology', 'rta', 'pl', 'availability', 'rf']:
            sds_name = service_name.strip() + "_" + service_data_source_type.strip()
        else:
            sds_name = service_data_source_type.strip()

        # to check if data source would be displayed as a chart or as a table
        show_chart = True

        service_view_type = self.request.GET.get('service_view_type')
        is_unified_view = service_view_type and service_view_type == 'unified'

        # Chart type as per unified view. Show only table if anyone ds has table type.
        if is_unified_view:
            for sds in SERVICE_DATA_SOURCE:
                if show_chart:
                    if service_name.strip() in sds and SERVICE_DATA_SOURCE[sds]['type'] == 'table':
                        show_chart = False
                else:
                    break
        else:
            if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]['type'] == 'table':
                show_chart = False

        # check for the formula
        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]['formula']:
            formula = SERVICE_DATA_SOURCE[sds_name]['formula']
        else:
            formula = None

        # Update 'default' machine name in case of historical data request
        if data_for not in ['live']:
            inventory_device_machine_name = 'default'

        parameters = {
            'model': PerformanceService,
            'start_time': start_date,
            'end_time': end_date,
            'devices': [inventory_device_name],
            'services': [service_name],
            'sds': [service_data_source_type]
        }

        if data_for == 'bihourly':
            parameters.update({
                'model': PerformanceServiceBiHourly
            })
        elif data_for == 'hourly':
            parameters.update({
                'model': PerformanceServiceHourly
            })
        elif data_for == 'daily':
            parameters.update({
                'model': PerformanceServiceDaily
            })
        elif data_for == 'weekly':
            parameters.update({
                'model': PerformanceServiceWeekly
            })
        elif data_for == 'monthly':
            parameters.update({
                'model': PerformanceServiceMonthly
            })
        elif data_for == 'yearly':
            parameters.update({
                'model': PerformanceServiceYearly
            })

        if (service_name == 'ping' or service_data_source_type in ['pl', 'rta']) and service_data_source_type not in ['rf']:
            if data_for == 'bihourly':
                parameters.update({
                    'model': PerformanceNetworkBiHourly
                })
            elif data_for == 'hourly':
                parameters.update({
                    'model': PerformanceNetworkHourly
                })
            elif data_for == 'daily':
                parameters.update({
                    'model': PerformanceNetworkDaily
                })
            elif data_for == 'weekly':
                parameters.update({
                    'model': PerformanceNetworkWeekly
                })
            elif data_for == 'monthly':
                parameters.update({
                    'model': PerformanceNetworkMonthly
                })
            elif data_for == 'yearly':
                parameters.update({
                    'model': PerformanceNetworkYearly
                })
            else:
                parameters.update({
                    'model': PerformanceNetwork
                })

            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name)

            result = self.get_performance_data_result(performance_data, '', is_historical_data)

        elif service_data_source_type == 'rf':
            sector_device = None
            if device.substation_set.exists():
                try:
                    ss = device.substation_set.get()
                    circuit = ss.circuit_set.get()
                    sector_device = circuit.sector.sector_configured_on
                except Exception as e:
                    return HttpResponse(json.dumps(self.result), content_type="application/json")
            else:
                return HttpResponse(json.dumps(self.result), content_type="application/json")

            parameters.update({
                'model': PerformanceNetwork,
                'start_time': start_date,
                'end_time': end_date,
                'devices': [inventory_device_name],
                'services': ['ping'],
                'sds': ['rta']
            })

            if data_for == 'bihourly':
                parameters.update({
                    'model': PerformanceNetworkBiHourly
                })
            elif data_for == 'hourly':
                parameters.update({
                    'model': PerformanceNetworkHourly
                })
            elif data_for == 'daily':
                parameters.update({
                    'model': PerformanceNetworkDaily
                })
            elif data_for == 'weekly':
                parameters.update({
                    'model': PerformanceNetworkWeekly
                })
            elif data_for == 'monthly':
                parameters.update({
                    'model': PerformanceNetworkMonthly
                })
            elif data_for == 'yearly':
                parameters.update({
                    'model': PerformanceNetworkYearly
                })

            # ss data performance
            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name).order_by('sys_timestamp')

            if sector_device:
                # for calculating BS data
                parameters.update({
                    'devices': [sector_device.device_name]
                })
                # bs data performance
                performance_data_bs = self.get_performance_data(
                    **parameters
                ).using(alias=inventory_device_machine_name).order_by('sys_timestamp')

                result = self.rf_performance_data_result(
                    performance_data_bs=performance_data_bs,
                    performance_data_ss=performance_data
                )
            else:
                result = self.get_performance_data_result(performance_data, '', is_historical_data)

        elif "availability" in service_name or service_data_source_type in ['availability']:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(weeks=-1), 'U')

            parameters.update({
                'model': NetworkAvailabilityDaily,
                'start_time': start_date,
                'end_time': end_date
            })

            # gather performance data
            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name).order_by('sys_timestamp')

            result = self.get_performance_data_result(performance_data, data_source="availability")

        elif "topology" in service_name or service_data_source_type in ['topology']:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(weeks=-1), 'U')
            
            dr_devices_ip = None
            # for wimax devices there can be a case of DR
            # we need to incorporate the DR devices as well
            try:
                if technology and technology.name.lower() in ['wimax'] and (is_sector_device or is_dr_device):
                    # In Case of DR Device
                    if is_dr_device:
                        dr_devices = device.dr_configured_on.filter()
                        device_col_name = 'sector_configured_on__device_name'
                        configured_device_qs = device.dr_configured_on.values().distinct().values(
                            'sector_configured_on__device_name',
                            'sector_configured_on__ip_address'
                        )
                        dr_devices_ip = device.ip_address
                    else:
                        dr_devices = device.sector_configured_on.filter()
                        configured_device_qs = device.sector_configured_on.values().distinct().values(
                            'dr_configured_on__device_name',
                            'dr_configured_on__ip_address'
                        )
                        device_col_name = 'dr_configured_on__device_name'
                        dr_devices_ip = configured_device_qs[0]['dr_configured_on__ip_address'] if configured_device_qs.exists() else ''
                        sector_device = device

                    if configured_device_qs:
                        dr_devices_name = configured_device_qs[0][device_col_name] if configured_device_qs.exists() else ''

                    if dr_devices_name:
                        # append dr/sector device
                        parameters['devices'].append(dr_devices_name)
                    # parameters updated with all devices
            except:
                pass  # no dr site

            try:
                if is_dr_device:
                    sector_object = dr_devices if dr_devices else device.dr_configured_on.filter()
                else:
                    sector_object = device.sector_configured_on.filter()
            except:
                return HttpResponse(json.dumps(self.result), content_type="application/json")

            parameters.update({
                'model': Topology,
                'start_time': start_date,
                'end_time': end_date,
                'services': None,
                'sds': ['topology']
            })

            performance_data = self.get_performance_data(
                **parameters
            )

            if dr_devices_ip:
                result = self.get_topology_result(
                    performance_data,
                    dr_ip=dr_devices_ip,
                    technology=technology,
                    sectors=sector_object
                )
            else:
                result = self.get_topology_result(
                    performance_data,
                    technology=technology,
                    sectors=sector_object
                )

        elif '_status' in service_name:
            if not isSet and data_for == 'live':
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(days=-1), 'U')

            parameters.update({
                'model': PerformanceStatus,
                'start_time': start_date,
                'end_time': end_date,
                'devices': [inventory_device_name],
                'services': [service_name],
                'sds': [service_data_source_type]
            })

            if data_for == 'daily':
                parameters.update({
                    'model': PerformanceStatusDaily
                })
            elif data_for == 'weekly':
                parameters.update({
                    'model': PerformanceStatusWeekly
                })
            elif data_for == 'monthly':
                parameters.update({
                    'model': PerformanceStatusMonthly
                })
            elif data_for == 'yearly':
                parameters.update({
                    'model': PerformanceStatusYearly
                })

            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name)
            
            result = self.get_perf_table_result(performance_data, None, is_historical_data)

        elif '_invent' in service_name:
            if not isSet and data_for == 'live':
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(weeks=-1), 'U')

            parameters.update({
                'model': PerformanceInventory,
                'start_time': start_date,
                'end_time': end_date,
                'devices': [inventory_device_name],
                'services': [service_name],
                'sds': [service_data_source_type]
            })

            if data_for == 'daily':
                parameters.update({
                    'model': PerformanceInventoryDaily
                })
            elif data_for == 'weekly':
                parameters.update({
                    'model': PerformanceInventoryWeekly
                })
            elif data_for == 'monthly':
                parameters.update({
                    'model': PerformanceInventoryMonthly
                })
            elif data_for == 'yearly':
                parameters.update({
                    'model': PerformanceInventoryYearly
                })

            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name)

            result = self.get_perf_table_result(performance_data, None, is_historical_data)

        elif '_kpi' in service_name:

            current_device = [inventory_device_name]

            if is_dr_device:
                try:
                    # Get the 'sectors' device name associated with this DR device
                    devices_qs = device.dr_configured_on.values().distinct().values_list(
                        'sector_configured_on__device_name', flat=True
                    )
                    # Convert queryset to list
                    current_device = [item for item in devices_qs]
                except Exception, e:
                    pass

            parameters.update({
                'model': Utilization,
                'start_time': start_date,
                'end_time': end_date,
                'services': [service_name],
                'devices': current_device,
                'sds': [service_data_source_type]
            })

            if data_for == 'bihourly':
                parameters.update({
                    'model': UtilizationBiHourly
                })
            elif data_for == 'hourly':
                parameters.update({
                    'model': UtilizationHourly
                })
            elif data_for == 'daily':
                parameters.update({
                    'model': UtilizationDaily
                })
            elif data_for == 'weekly':
                parameters.update({
                    'model': UtilizationWeekly
                })
            elif data_for == 'monthly':
                parameters.update({
                    'model': UtilizationMonthly
                })
            elif data_for == 'yearly':
                parameters.update({
                    'model': UtilizationYearly
                })

            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name)

            if not show_chart:  # show the table
                result = self.get_perf_table_result(
                    performance_data=performance_data,
                    formula=formula,
                    is_historical_data=is_historical_data
                )
            else:  # show the chart
                result = self.get_performance_data_result(performance_data, '', is_historical_data)

        else:
            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name)

            if not show_chart:  # show the table
                result = self.get_perf_table_result(
                    performance_data=performance_data,
                    formula=formula,
                    is_historical_data=is_historical_data
                )
            else:  # show the chart
                result = self.get_performance_data_result(performance_data, '', is_historical_data)

        return HttpResponse(json.dumps(result), content_type="application/json")

    def get_performance_data(self, model=None, start_time=None, end_time=None, devices=None, services=None, sds=None):
        """

        :param model:
        :param start_time:
        :param end_time:
        :param devices:
        :param services:
        :param sds:
        :return:
        """
        if services:
            where_condition = ''
            if start_time and end_time:
                if 'all' in sds:
                    where_condition = (
                        Q(device_name__in=devices)
                        &
                        Q(service_name__in=services)
                        &
                        Q(sys_timestamp__gte=start_time) & Q(sys_timestamp__lte=end_time)
                    )
                else:
                    where_condition = (
                        Q(device_name__in=devices)
                        &
                        Q(service_name__in=services) & Q(data_source__in=sds)
                        &
                        Q(sys_timestamp__gte=start_time) & Q(sys_timestamp__lte=end_time)
                    )
            else:
                if 'all' in sds:
                    where_condition = (
                        Q(device_name__in=devices)
                        &
                        Q(service_name__in=services)
                    )
                else:
                    where_condition = (
                        Q(device_name__in=devices)
                        &
                        Q(service_name__in=services) & Q(data_source__in=sds)
                    )
            performance_data = model.objects.filter(where_condition).order_by('sys_timestamp')
        else:
            if start_time and end_time:
                if 'all' in sds:
                    where_condition = (
                        Q(device_name__in=devices)
                        &
                        Q(sys_timestamp__gte=start_time) & Q(sys_timestamp__lte=end_time)
                    )
                else:
                    where_condition = (
                        Q(device_name__in=devices)
                        &
                        Q(data_source__in=sds)
                        &
                        Q(sys_timestamp__gte=start_time) & Q(sys_timestamp__lte=end_time)
                    )
            else:
                if 'all' in sds:
                    where_condition = (
                        Q(device_name__in=devices)
                    )
                else:
                    where_condition = (
                        Q(device_name__in=devices)
                        &
                        Q(data_source__in=sds)
                    )
            performance_data = model.objects.filter(where_condition).order_by('sys_timestamp')

        return performance_data

    def return_table_header_and_table_data(self, service_name, result):

        """

        :param service_name:
        :param result:
        :return:
        """
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
                    'value': data['y']
                }]
            table_data = data_list
        return table_data, table_header

    def get_perf_table_result(self, performance_data, formula=None, is_historical_data=False):

        """

        :param performance_data:
        :param formula:
        :param is_historical_data:
        :return:
        """
        grid_headers = list()
        if is_historical_data:
            # Grid Headers List
            grid_headers = [
                {'mData': 'sys_timestamp', 'sTitle': 'Time', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'min_value', 'sTitle': 'Min. Value', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'max_value', 'sTitle': 'Max. Value', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'avg_value', 'sTitle': 'Avg. Value', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'current_value', 'sTitle': 'Value', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'severity', 'sTitle': 'Severity', 'sWidth': 'auto', 'bSortable': True}
            ]
        else:
            # Grid Headers List
            grid_headers = [
                {'mData': 'sys_timestamp', 'sTitle': 'Time', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'current_value', 'sTitle': 'Value', 'sWidth': 'auto', 'bSortable': True},
                {'mData': 'severity', 'sTitle': 'Severity', 'sWidth': 'auto', 'bSortable': True}
            ]

        self.result['success'] = 1
        self.result['message'] = 'Headers fetched successfully.'
        self.result['data']['objects']['table_data_header'] = grid_headers

        return self.result

    def get_topology_result(self, performance_data, dr_ip=None, technology=None, sectors=None):
        """
        Getting the current topology of any elements of the network
        :param sectors:
        :param technology:
        :param dr_ip:
        :param performance_data:
        """

        result_data, aggregate_data, connected_ss_ip = list(), dict(), list()

        #topology last updated
        last_updated = None
        #topology last updated

        #we need to get all the connected
        #sector--> circuits --> SS
        #we need to append those SS here as well
        #to note : the SS might be currently connected one
        #or the SS might be the one disconnected
        #if it is connected, then it will be present in topology
        #else it will be present in the SECTOR --> CIRCUIT --> SS
        for data in performance_data:
            temp_time = data.sys_timestamp
            connected_mac = data.connected_device_mac
            if connected_mac in aggregate_data:
                continue
            else:
                aggregate_data[connected_mac] = data.connected_device_mac

                #check the connected SS
                connected_ss_ip.append(data.connected_device_ip)
                #check the connected SS

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
                last_down = 'NA'
                machine = 'default'
                vlan = 'NA'
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

                        vlan = self.ss_vlan_performance_data_result(
                            technology=technology,
                            ss_device_object=connected_device,
                            machine=machine
                        )

                        packet_loss, latency, status_since, last_down = self.ss_network_performance_data_result(
                            ss_device_object=connected_device,
                            machine=machine
                        )

                last_updated = datetime.datetime.fromtimestamp(
                    float(data.sys_timestamp)
                ).strftime(DATE_TIME_FORMAT)

                show_ip_address = data.ip_address

                # If DR device IP then add " (DR)" string with it.
                if dr_ip and dr_ip == show_ip_address:
                    show_ip_address += " (DR)"

                result_data.append({
                    #'device_name': data.device_name,
                    'ip_address': show_ip_address,
                    'mac_address': data.mac_address,
                    'sector_id': data.sector_id,
                    'vlan': vlan,
                    'connected_device_ip': data.connected_device_ip,
                    'connected_device_mac': data.connected_device_mac,
                    'circuit_id': circuit_id,
                    'customer_name': customer_name,
                    'packet_loss': packet_loss,
                    'latency': latency,
                    # 'up_down_since': status_since,
                    'last_down_time': last_down,
                    'last_updated': last_updated,
                })

        #here we will append the rest of the SS
        #which are not in topology now
        #but are connected to the sector
        if sectors:
            not_connected_ss = SubStation.objects.filter(
                circuit__sector__in=sectors
            ).exclude(
                device__ip_address__in=connected_ss_ip
            ).prefetch_related('circuit_set')

            circuit_id = 'NA'
            customer_name = 'NA'
            sector_ip = 'NA'
            sector_mac = 'NA'
            sector_id = None

            for ss in not_connected_ss:
                vlan = self.ss_vlan_performance_data_result(
                    technology=technology,
                    ss_device_object=ss.device,
                    machine=ss.device.machine.name
                )
                packet_loss, latency, status_since, last_down = self.ss_network_performance_data_result(
                    ss_device_object=ss.device,
                    machine=ss.device.machine.name
                )
                try:
                    circuit_object = ss.circuit_set.filter().prefetch_related('sector').get()
                    circuit_id = circuit_object.circuit_id
                    customer_name = circuit_object.customer.alias
                    device_mac = ss.device.mac_address
                    device_ip = ss.device.ip_address
                    sector_ip = circuit_object.sector.sector_configured_on.ip_address
                    sector_mac = circuit_object.sector.sector_configured_on.mac_address
                    sector_id = circuit_object.sector.sector_id

                except:
                    continue

                if sector_id:
                    result_data.append({
                        #'device_name': data.device_name,
                        'ip_address': sector_ip,
                        'mac_address': sector_mac,
                        'sector_id': sector_id,
                        'vlan': vlan,
                        'connected_device_ip': device_ip,
                        'connected_device_mac': device_mac,
                        'circuit_id': circuit_id,
                        'customer_name': customer_name,
                        'packet_loss': packet_loss,
                        'latency': latency,
                        # 'up_down_since': status_since,
                        'last_down_time': last_down,
                        'last_updated': last_updated,
                    })

        self.result['success'] = 1
        self.result['message'] = 'Device Data Fetched Successfully.' if result_data else 'No Record Found.'
        self.result['data']['objects']['table_data'] = result_data
        self.result['data']['objects']['table_data_header'] = [
            'ip_address',
            'mac_address',
            'sector_id',
            'vlan',
            'connected_device_ip',
            'connected_device_mac',
            'circuit_id',
            'customer_name',
            'packet_loss',
            'latency',
            'last_down_time',
            'last_updated'
        ]

        return self.result

    def ss_vlan_performance_data_result(self, technology, ss_device_object, machine):
        """
        provide the SS vlan data
        :param machine:
        :param ss_device_object:
        :param technology:
        """
        vlan = "NA"

        if technology and technology.name.lower() in ['wimax']:
            service_name = 'wimax_ss_vlan_invent'
            data_source = 'ss_vlan'
        elif technology and technology.name.lower() in ['pmp']:
            service_name = 'cambium_vlan_invent'
            data_source = 'vlan'
        else:
            service_name = None
            data_source = None

        if service_name and data_source:
            try:
                vs = InventoryStatus.objects.filter(
                    device_name=ss_device_object.device_name,
                    service_name=service_name,
                    data_source=data_source
                ).using(alias=machine)
                vlan = vs[0].current_value
            except Exception as e:
                log.exception(e.message)
                vlan = "NA"

        return vlan

    def ss_network_performance_data_result(self, ss_device_object, machine):
        """
        provide the pl and latency
        :param machine:
        :param ss_device_object:
        """
        packet_loss = None
        latency = None
        status_since = None
        last_down = None

        perf_data = NetworkStatus.objects.filter(
            device_name=ss_device_object.device_name
        ).annotate(
            dcount=Count('data_source')
        ).values(
            'data_source', 'current_value', 'age', 'sys_timestamp', 'refer'
        ).using(alias=machine)

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
                if pdata['data_source'] == 'pl' and pdata['current_value'] != 100:
                    status_since = pdata['age']
                else:
                    status_since = pdata['refer']

                try:
                    status_since = datetime.datetime.fromtimestamp(
                        float(status_since)
                    ).strftime(DATE_TIME_FORMAT)
                except Exception, e:
                    status_since = status_since

            else:
                continue

        #last time down results
        severity, a = device_current_status(device_object=ss_device_object)
        age = a['age'] if(a and 'age' in a) else ""
        down = a['down'] if(a and 'down' in a) else ""
        if age:
            status_since = datetime.datetime.fromtimestamp(
                float(age)
            ).strftime(DATE_TIME_FORMAT)

        if down:
            try:
                last_down = datetime.datetime.fromtimestamp(
                    float(down)
                ).strftime(DATE_TIME_FORMAT)
            except Exception, e:
                last_down = down
        # log.info(str(ss_device_object.ip_address) + "----------" + str(last_down))
        if not last_down:
            last_down = 'NA'

        return packet_loss, latency, status_since, last_down

    def rf_performance_data_result(self, performance_data_ss, performance_data_bs):
        """
        :param performance_data_bs:
        :param performance_data_ss:
        """
        chart_data = list()
        if performance_data_ss and performance_data_bs:
            data_list, warn_data_list, crit_data_list, aggregate_data = list(), list(), list(), dict()
            bs_data_list = list()
            ss_data_list = list()

            rf_prop = SERVICE_DATA_SOURCE['rf']

            for data in performance_data_ss:
                js_time = data.sys_timestamp*1000
                if data.avg_value:
                    try:
                        ##in between 5 minutes the bs result will come before ss result
                        valid_end_time = data.sys_timestamp + 30  #30 seconds buffer added
                        valid_start_time = data.sys_timestamp - 330  #30 seconds buffer added
                        ##in between 5 minutes the bs result will come before ss result
                        bs_lat = performance_data_bs.filter(
                            sys_timestamp__gte=valid_start_time,
                            sys_timestamp__lte=valid_end_time
                        )[0].avg_value

                        ss_lat = data.avg_value
                        rf_lat = float(ss_lat) - float(bs_lat)

                        if rf_lat < 0:
                            rf_lat = 0

                        if rf_prop['show_bs']:
                            bs_data_list.append([js_time, float(bs_lat)])
                        if rf_prop['show_ss']:
                            ss_data_list.append([js_time, float(ss_lat)])

                        data_list.append([js_time, float(rf_lat)])
                    except Exception as e:
                        rf_lat = data.avg_value
                        if rf_prop['show_ss']:
                            ss_data_list.append([js_time, float(rf_lat)])
                        data_list.append([js_time, float(rf_lat)])
                        log.exception(e.message)

            chart_data = [{
                'name': "RF Latency",
                'data': data_list,
                'type': 'area',
                'valuesuffix': ' ms ',
                'valuetext': ' ms '
            }]
            if rf_prop['show_ss']:
                chart_data.append({
                    'name': "SS Latency",
                    'data': ss_data_list,
                    'type': 'spline',
                    'valuesuffix': ' ms ',
                    'valuetext': ' ms '
                })
            if rf_prop['show_bs']:
                chart_data.append({
                    'name': "BS Latency",
                    'data': bs_data_list,
                    'type': 'spline',
                    'valuesuffix': ' ms ',
                    'valuetext': ' ms '
                })

        self.result['success'] = 1
        self.result['data']['objects']['chart_data'] = chart_data
        self.result['message'] = 'Device Performance Data Fetched Successfully To Plot Graphs.'

        if not chart_data or len(chart_data) == 0:
            self.result['message'] = 'No Data'

        return self.result

    def dr_performance_data_result(self, performance_data, sector_device, dr_device, availability=False):
        """
        specially for dr devices
        :param availability:
        :param dr_device:
        :param sector_device:
        :param performance_data:
        """

        sector_performance_data = performance_data.filter(device_name=sector_device.device_name)
        dr_performance_data = performance_data.filter(device_name=dr_device.device_name)

        sector_result = self.performance_data_result(performance_data=sector_performance_data)
        dr_result = self.perforxmance_data_result(performance_data=dr_performance_data)
        try:
            sector_result['data']['objects']['chart_data'][0]['name'] += " ( {0} )".format(sector_device.ip_address)
            if availability:
                sector_result['data']['objects']['chart_data'][1]['name'] += " ( {0} )".format(sector_device.ip_address)

            dr_result['data']['objects']['chart_data'][0]['name'] += " DR: ( {0} )".format(dr_device.ip_address)

            chart_data = sector_result['data']['objects']['chart_data']
            chart_data.append(dr_result['data']['objects']['chart_data'][0])
            if availability:
                dr_result['data']['objects']['chart_data'][1]['name'] += " DR: ( {0} )".format(dr_device.ip_address)
                chart_data.append(dr_result['data']['objects']['chart_data'][1])

        except:
            chart_data = sector_result['data']['objects']['chart_data']

        self.result['success'] = 1
        self.result['message'] = 'Device Performance Data Fetched Successfully To Plot Graphs.'
        self.result['data']['objects']['chart_data'] = chart_data

        return self.result

    def performance_data_result(self, performance_data, data_source=None):
        """
        :param performance_data:
        :param data_source:
        :return:
        """
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
                    sds_name = str(data.data_source).strip()
                    if sds_name not in ['availability']:
                        if sds_name not in ['pl', 'rta']:
                            sds_name = str(data.service_name).strip() + "_" + str(data.data_source).strip()

                    sds_display_name = SERVICE_DATA_SOURCE[sds_name]["display_name"] \
                        if sds_name in SERVICE_DATA_SOURCE  else str(data.data_source).upper()

                    result['data']['objects']['display_name'] = sds_display_name

                    result['data']['objects']['type'] = SERVICE_DATA_SOURCE[sds_name]["type"] \
                        if sds_name in SERVICE_DATA_SOURCE else "area"

                    result['data']['objects']['valuesuffix'] = SERVICE_DATA_SOURCE[sds_name]["valuesuffix"] \
                        if sds_name in SERVICE_DATA_SOURCE else ""

                    result['data']['objects']['valuetext'] = SERVICE_DATA_SOURCE[sds_name]["valuetext"] \
                        if sds_name in SERVICE_DATA_SOURCE else str(data.data_source).upper()

                    result['data']['objects']['plot_type'] = 'charts'

                    chart_color = SERVICE_DATA_SOURCE[sds_name]["chart_color"] \
                        if sds_name in SERVICE_DATA_SOURCE else '#70AFC4'

                    if sds_name not in ["availability"]:
                        #only display warning if there exists a warning
                        if data.warning_threshold:
                            warn_data_list.append([js_time, float(data.warning_threshold)])

                        #only display critical if there exists a critical
                        if data.critical_threshold:
                            crit_data_list.append([js_time, float(data.critical_threshold)])

                        ###to draw each data point w.r.t threshold we would need to use the following
                        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["show_min"]:
                            min_data_list.append([
                                js_time,
                                float(data.min_value) if data.min_value else None
                            ])

                        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["show_max"]:
                            max_data_list.append([
                                js_time,
                                float(data.max_value) if data.max_value else None
                            ])

                        sds_inverted = False

                        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["is_inverted"]:
                            sds_inverted = SERVICE_DATA_SOURCE[sds_name]["is_inverted"]

                        if not sds_inverted:
                            compare_point = lambda p1, p2, p3: chart_color \
                                if abs(p1) < abs(p2) \
                                else ('#FFE90D'
                                      if abs(p2) < abs(p1) < abs(p3)
                                      else ('#FF193B' if abs(p3) < abs(p1) else chart_color)
                                )
                        else:
                            compare_point = lambda p1, p2, p3: chart_color \
                                if abs(p1) > abs(p2) \
                                else ('#FFE90D'
                                      if abs(p2) > abs(p1) > abs(p3)
                                      else ('#FF193B' if abs(p3) > abs(p1) else chart_color)
                                )

                        formula = SERVICE_DATA_SOURCE[sds_name]["formula"] \
                            if sds_name in SERVICE_DATA_SOURCE else None

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
                        chart_data = [{
                            'name': result['data']['objects']['display_name'],
                            'data': data_list,
                            'type': result['data']['objects']['type'],
                            'valuesuffix': result['data']['objects']['valuesuffix'],
                            'valuetext': result['data']['objects']['valuetext'],
                            'is_inverted': sds_inverted
                        }]

                        if len(min_data_list):
                            chart_data.append({
                                'name': str("min value").title(),
                                'color': '#01CC14',
                                'data': min_data_list,
                                'type': 'line',
                                'marker': {
                                    'enabled': False
                                }
                            })

                        if len(max_data_list):
                            chart_data.append({
                                'name': str("max value").title(),
                                'color': '#FF8716',
                                'data': max_data_list,
                                'type': 'line',
                                'marker': {
                                    'enabled': False
                                }
                            })
                        # Condition should be of length of warning list
                        if len(warn_data_list):
                            chart_data.append({
                                'name': str("warning threshold").title(),
                                'color': WARN_COLOR,
                                'data': warn_data_list,
                                'type': WARN_TYPE,
                                'marker': {
                                    'enabled': False
                                }
                            })
                        # Condition should be of length of critical list
                        if len(crit_data_list):
                            chart_data.append({
                                'name': str("critical threshold").title(),
                                'color': CRIT_COLOR,
                                'data': crit_data_list,
                                'type': CRIT_TYPE,
                                'marker': {
                                    'enabled': False
                                }
                            })
                    else:
                        y_value = None
                        y_down_value = None
                        y_color = '#70AFC4'
                        y_down_color = '#FF193B'
                        y_title = str(data.data_source).upper()

                        if data.current_value:
                            # title for availability
                            y_title = "Availability"

                            # Value for availability & unavailability
                            y_value = float(data.current_value)
                            y_down_value = 100.00 - float(data.current_value)

                            # Color for availability & unavailability
                            y_color = '#90ee7e'
                            y_down_color = '#FF193B'

                        data_list.append({
                            "name": y_title,
                            "color": y_color,
                            "y": y_value,
                            "x": js_time
                        })

                        warn_data_list.append({
                            "name": "UnAvailability",
                            "color": y_down_color,
                            "y": y_down_value,
                            "x": js_time
                        })

                        chart_data = [
                            {
                                'name': 'Availability',
                                'data': data_list,
                                'type': result['data']['objects']['type'],
                                'valuesuffix': result['data']['objects']['valuesuffix'],
                                'valuetext': result['data']['objects']['valuetext']
                            },
                            {
                                'name': 'UnAvailability',
                                'color': '#FF193B',
                                'data': warn_data_list,
                                'type': 'column',
                                'marker': {
                                    'enabled': False
                                }
                            }
                        ]

            #this ensures a further good presentation of data w.r.t thresholds

            result['success'] = 1
            result['message'] = 'Device Performance Data Fetched Successfully To Plot Graphs.'
            result['data']['objects']['chart_data'] = chart_data

        return result

    # TODO: Mix charts support
    
    def get_performance_data_result(self, performance_data, data_source=None, is_historical_data=False):
        """

        :param performance_data:
        :param data_source:
        :param is_historical_data:
        :return:
        """
        chart_data= list()

        if performance_data:
            ds_list = list(set(performance_data.values_list('data_source', flat=True)))
            service_view_type = self.request.GET.get('service_view_type')
            is_unified_view = service_view_type and service_view_type == 'unified'
            for ds in ds_list:
                # Variables used for HISTORICAL data
                data_list, warn_data_list, crit_data_list, aggregate_data = list(), list(), list(), dict()
                data_list_min, data_list_max, data_list_avg =  list(), list(), list()
                min_data_list = list()
                max_data_list = list()
                x = performance_data.filter(data_source=ds)
                for data in x:
                    temp_time = data.sys_timestamp

                    if temp_time in aggregate_data:
                        continue
                    else:
                        aggregate_data[temp_time] = data.sys_timestamp

                        #time in javascript format
                        js_time = data.sys_timestamp * 1000
                        #time in javascript format

                        sds_name = str(data.data_source).strip()

                        if sds_name not in ['availability']:
                            if sds_name not in ['pl', 'rta']:
                                sds_name = str(data.service_name).strip() + "_" + str(data.data_source).strip()

                        sds_display_name = SERVICE_DATA_SOURCE[sds_name]["display_name"] \
                            if sds_name in SERVICE_DATA_SOURCE else str(data.data_source).upper()

                        self.result['data']['objects']['display_name'] = sds_display_name

                        display_name = self.result['data']['objects']['display_name']

                        self.result['data']['objects']['type'] = SERVICE_DATA_SOURCE[sds_name]["type"] \
                            if sds_name in SERVICE_DATA_SOURCE else "area"

                        self.result['data']['objects']['valuesuffix'] = SERVICE_DATA_SOURCE[sds_name]["valuesuffix"] \
                            if sds_name in SERVICE_DATA_SOURCE else ""

                        self.result['data']['objects']['valuetext'] = SERVICE_DATA_SOURCE[sds_name]["valuetext"] \
                            if sds_name in SERVICE_DATA_SOURCE else str(data.data_source).upper()

                        self.result['data']['objects']['plot_type'] = 'charts'

                        chart_color = SERVICE_DATA_SOURCE[sds_name]["chart_color"] \
                            if sds_name in SERVICE_DATA_SOURCE else '#70AFC4'

                        if sds_name not in ["availability"]:

                            sds_inverted = False
                            self.result['data']['objects']['is_inverted'] = sds_inverted

                            if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["is_inverted"]:
                                sds_inverted = SERVICE_DATA_SOURCE[sds_name]["is_inverted"]
                                self.result['data']['objects']['is_inverted'] = sds_inverted

                            if not sds_inverted:
                                compare_point = lambda p1, p2, p3: chart_color \
                                    if abs(p1) < abs(p2) \
                                    else ('#FFE90D'
                                          if abs(p2) < abs(p1) < abs(p3)
                                          else ('#FF193B' if abs(p3) < abs(p1) else chart_color)
                                    )
                            else:
                                compare_point = lambda p1, p2, p3: chart_color \
                                    if abs(p1) > abs(p2) \
                                    else ('#FFE90D'
                                          if abs(p2) > abs(p1) > abs(p3)
                                          else ('#FF193B' if abs(p3) > abs(p1) else chart_color)
                                    )

                            formula = SERVICE_DATA_SOURCE[sds_name]["formula"] if sds_name in SERVICE_DATA_SOURCE else None

                            #only display warning if there exists a warning
                            if data.warning_threshold:
                                warn_data_list.append([js_time, float(data.warning_threshold)])

                            #only display critical if there exists a critical
                            if data.critical_threshold:
                                crit_data_list.append([js_time, float(data.critical_threshold)])

                            no_val_color = '#70AFC4'
                            # FOR HISTORICAL DATA
                            if is_historical_data:
                                # MIN VAL
                                min_value = None
                                min_color = no_val_color
                                if data.min_value:
                                    val = float(data.min_value) if data.min_value else 0
                                    min_value = eval(str(formula) + "(" + str(val) + ")") if formula else float(data.min_value)
                                    min_color = MIN_CHART_COLOR

                                data_list_min.append({
                                    "name": str(sds_display_name)+"(Min Value)",
                                    "color": min_color,
                                    "y": min_value,
                                    "x": js_time
                                })

                                # MAX VAL
                                max_value = None
                                max_color = no_val_color
                                if data.max_value:
                                    val = float(data.max_value) if data.max_value else 0
                                    max_value = eval(str(formula) + "(" + str(val) + ")") if formula else float(data.max_value)
                                    max_color = MAX_CHART_COLOR

                                data_list_max.append({
                                    "name": str(sds_display_name)+"(Max Value)",
                                    "color": max_color,
                                    "y": max_value,
                                    "x": js_time
                                })
                                
                                # AVG VAL
                                avg_value = None
                                avg_color = no_val_color
                                if data.avg_value:
                                    val = float(data.avg_value) if data.avg_value else 0
                                    avg_value = eval(str(formula) + "(" + str(val) + ")") if formula else float(data.avg_value)
                                    avg_color = AVG_CHART_COLOR
                                
                                data_list_avg.append({
                                    "name": str(sds_display_name)+"(Avg Value)",
                                    "color": avg_color,
                                    "y": avg_value,
                                    "x": js_time
                                })

                                # CURRENT VAL
                                current_value = None
                                current_color = no_val_color
                                if data.current_value:
                                    val = float(data.current_value) if data.current_value else 0
                                    warn_val = float(data.warning_threshold) if data.warning_threshold else val
                                    crit_val = float(data.critical_threshold) if data.critical_threshold else val
                                    current_value = eval(str(formula) + "(" + str(val) + ")") if formula else float(data.current_value)
                                    current_color = compare_point(val, warn_val, crit_val)

                                data_list.append({
                                    "name": str(sds_display_name)+"(Current Value)",
                                    "color": current_color,
                                    "y": current_value,
                                    "x": js_time
                                })

                                chart_data = [
                                    {  # Min Value
                                        'name': self.result['data']['objects']['display_name']+"(Min Value)",
                                        'data': data_list_min,
                                        'type': MIN_CHART_TYPE,
                                        'color': MIN_CHART_COLOR,
                                        'valuesuffix': self.result['data']['objects']['valuesuffix'],
                                        'valuetext': self.result['data']['objects']['valuetext'],
                                        'is_inverted': self.result['data']['objects']['is_inverted'],
                                        'marker': {
                                            'enabled': False
                                        }
                                    },
                                    {  # Max Value
                                        'name': self.result['data']['objects']['display_name']+"(Max Value)",
                                        'data': data_list_max,
                                        'type': MAX_CHART_TYPE,
                                        'color': MAX_CHART_COLOR,
                                        'valuesuffix': self.result['data']['objects']['valuesuffix'],
                                        'valuetext': self.result['data']['objects']['valuetext'],
                                        'is_inverted': self.result['data']['objects']['is_inverted'],
                                        'marker': {
                                            'enabled': False
                                        }
                                    },
                                    {  # Avg Value
                                        'name': self.result['data']['objects']['display_name']+"(Avg Value)",
                                        'data': data_list_avg,
                                        'type': AVG_CHART_TYPE,
                                        'color': AVG_CHART_COLOR,
                                        'valuesuffix': self.result['data']['objects']['valuesuffix'],
                                        'valuetext': self.result['data']['objects']['valuetext'],
                                        'is_inverted': self.result['data']['objects']['is_inverted'],
                                        'marker': {
                                            'enabled': False
                                        }
                                    }#,
                                    # {  # Current Value
                                    #     'name': self.result['data']['objects']['display_name']+"(Current Value)",
                                    #     'data': data_list,
                                    #     'type': self.result['data']['objects']['type'],
                                    #     'valuesuffix': self.result['data']['objects']['valuesuffix'],
                                    #     'valuetext': self.result['data']['objects']['valuetext'],
                                    #     'is_inverted': self.result['data']['objects']['is_inverted']
                                    # }
                                ]

                            else:
                                ###to draw each data point w.r.t threshold we would need to use the following
                                if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["show_min"]:
                                    min_data_list.append([
                                        js_time,
                                        float(data.min_value) if data.min_value else None
                                    ])

                                if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["show_max"]:
                                    max_data_list.append([
                                        js_time,
                                        float(data.max_value) if data.max_value else None
                                    ])

                                current_value = None
                                current_color = no_val_color
                                if data.current_value:
                                    val = float(data.current_value) if data.current_value else 0
                                    warn_val = float(data.warning_threshold) if data.warning_threshold else val
                                    crit_val = float(data.critical_threshold) if data.critical_threshold else val
                                    current_value = eval(str(formula) + "(" + str(val) + ")") if formula else float(data.current_value)
                                    current_color = compare_point(val, warn_val, crit_val)

                                data_list.append({
                                    "name": sds_display_name,
                                    "color": current_color,
                                    "y": current_value,
                                    "x": js_time
                                })

                                # if len(min_data_list):
                                #     chart_data.append({
                                #         'name': str("min value").title(),
                                #         'color': '#01CC14',
                                #         'data': min_data_list,
                                #         'type': 'line',
                                #         'marker': {
                                #             'enabled': False
                                #         }
                                #     })

                                # if len(max_data_list):
                                #     chart_data.append({
                                #         'name': str("max value").title(),
                                #         'color': '#FF8716',
                                #         'data': max_data_list,
                                #         'type': 'line',
                                #         'marker': {
                                #             'enabled': False
                                #         }
                                #     })

                            # Condition of length of warning list  
                            # if len(warn_data_list):
                            #     chart_data.append({
                            #         'name': str("warning threshold").title(),
                            #         'color': WARN_COLOR,
                            #         'data': warn_data_list,
                            #         'type': WARN_TYPE,
                            #         'marker': {
                            #             'enabled': False
                            #         }
                            #     })
                            # # Condition of length of warning list  
                            # if len(crit_data_list):
                            #     chart_data.append({
                            #         'name': str("critical threshold").title(),
                            #         'color': CRIT_COLOR,
                            #         'data': crit_data_list,
                            #         'type': CRIT_TYPE,
                            #         'marker': {
                            #             'enabled': False
                            #         }
                            #     })
                        else:
                            y_value = None
                            y_down_value = None
                            y_color = '#70AFC4'
                            y_down_color = '#FF193B'
                            y_title = str(data.data_source).upper()

                            if data.current_value:
                                # title for availability
                                y_title = "Availability"

                                # Value for availability & unavailability
                                y_value = float(data.current_value)
                                y_down_value = 100.00 - float(data.current_value)
                                
                                # Color for availability & unavailability
                                y_color = '#90ee7e'
                                y_down_color = '#FF193B'

                            data_list.append({
                                "name": y_title,
                                "color": y_color,
                                "y": y_value,
                                "x": js_time
                            })

                            warn_data_list.append({
                                "name": "UnAvailability",
                                "color": y_down_color,
                                "y": y_down_value,
                                "x": js_time
                            })

                            chart_data = [
                                {
                                    'name': 'Availability',
                                    'color': y_color,
                                    'data': data_list,
                                    'type': self.result['data']['objects']['type'],
                                    'valuesuffix': self.result['data']['objects']['valuesuffix'],
                                    'valuetext': self.result['data']['objects']['valuetext']
                                },
                                {
                                    'name': 'UnAvailability',
                                    'color': y_down_color,
                                    'data': warn_data_list,
                                    'type': 'column',
                                    'marker': {
                                        'enabled': False
                                    }
                                }
                            ]

                if data_list and len(data_list) > 0:
                    chart_data.append({
                        'name': self.result['data']['objects']['display_name'],
                        'data': data_list,
                        'color' : data_list[0]['color'],
                        'type': self.result['data']['objects']['type'],
                        'valuesuffix': self.result['data']['objects']['valuesuffix'],
                        'valuetext': self.result['data']['objects']['valuetext'],
                        'is_inverted': self.result['data']['objects']['is_inverted']
                    })

                    if len(min_data_list):
                        chart_data.append({
                            'name': str("min value").title() + '(' + str(display_name) + ')' if is_unified_view else str("min value").title(),
                            'color': '#01CC14',
                            'data': min_data_list,
                            'type': 'line',
                            'marker': {
                                'enabled': False
                            }
                        })

                    if len(max_data_list):
                        chart_data.append({
                            'name': str("max value").title() + '(' + str(display_name) + ')' if is_unified_view else str("max value").title(),
                            'color': '#FF8716',
                            'data': max_data_list,
                            'type': 'line',
                            'marker': {
                                'enabled': False
                            }
                        })

                    if len(warn_data_list):
                        chart_data.append({
                            'name': str("warning threshold").title() + '(' + str(display_name) + ')' if is_unified_view else str("warning threshold").title(),
                            'color': WARN_COLOR,
                            'data': warn_data_list,
                            'type': WARN_TYPE,
                            'marker': {
                                'enabled': False
                            }
                        })
                    # Condition of length of warning list  
                    if len(crit_data_list):
                        chart_data.append({
                            'name': str("critical threshold").title() + '(' + str(display_name) + ')' if is_unified_view else str("critical threshold").title(),
                            'color': CRIT_COLOR,
                            'data': crit_data_list,
                            'type': CRIT_TYPE,
                            'marker': {
                                'enabled': False
                            }
                        })
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


        :param service_name:
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

        service_names = list()
        sds_names = list()
        service_data_sources = dict()
        bh_data_sources = None

        colors = ['#1BEAFF', '#A60CE8']

        # if is_sector:
        dr_device = None

        isSet, start_date, end_date = perf_utils.get_time(start_date, end_date, date_format, 'live')
        if not isSet:
            end_date = format(datetime.datetime.now(), 'U')
            start_date = format(datetime.datetime.now() + datetime.timedelta(minutes=-180), 'U')

        device = Device.objects.get(id=device_id)
        device_type = DeviceType.objects.get(id=device.device_type)
        # specially for DR devices
        technology = DeviceTechnology.objects.get(id=device.device_technology)


        if device.sector_configured_on.exists() or device.dr_configured_on.exists() or device.substation_set.exists():
            is_bh = False
        elif device.backhaul.exists():
            is_bh = True
        else:
            return HttpResponse(json.dumps(result), content_type="application/json")

        device_type_services = device_type.service.filter(
            name__icontains=service_name
        ).prefetch_related('servicespecificdatasource_set')

        services = device_type_services.values(
            'name',
            'alias',
            'servicespecificdatasource__service_data_sources__name',
            'servicespecificdatasource__service_data_sources__alias'
        )

        if is_bh:
            try:
                those_ports = device.backhaul.get().basestation_set.filter().values_list('bh_port_name', flat=True)

                bh_data_sources = ServiceDataSource.objects.filter(
                    name__in=DevicePort.objects.filter(alias__in=those_ports).values_list('name', flat=True)
                ).values_list('name', flat=True)

            except Exception as e:
                log.exception('{0} {1}', filter(type(e), e.message))
                is_bh = False
                bh_data_sources = None

        for s in services:
            service_names.append(s['name'])
            temp_sds_name = s['servicespecificdatasource__service_data_sources__name']
            temp_s_name = s['name']
            if is_bh:
                if bh_data_sources:
                    if temp_sds_name in bh_data_sources:
                        sds_names.append(temp_sds_name)
                    else:
                        continue
                else:
                    sds_names.append(temp_sds_name)
            else:
                sds_names.append(temp_sds_name)

            service_data_sources[temp_s_name, temp_sds_name] = \
                s['servicespecificdatasource__service_data_sources__alias']
            # if technology and technology.name.lower() in ['ptp', 'p2p']:
            if 'ul' in temp_s_name.lower():
                appnd = 'UL : '
            elif 'dl' in temp_s_name.lower():
                appnd = 'DL : '
            else:
                appnd = ''
            service_data_sources[temp_s_name, temp_sds_name] = appnd + service_data_sources[temp_s_name, temp_sds_name]



        performance = PerformanceService.objects.filter(
            device_name=device.device_name,
            service_name__in=service_names,
            data_source__in=sds_names,
            sys_timestamp__gte=start_date,
            sys_timestamp__lte=end_date
        ).using(
            alias=device.machine.name
        ).order_by('sys_timestamp')

        chart_data = []
        temp_chart_data = {}
        for data in performance:
            try:
                if (data.service_name, data.data_source) not in temp_chart_data:
                    c = SERVICE_DATA_SOURCE[data.service_name.strip() + "_" +data.data_source.strip()]['chart_color']

                    if technology and technology.name.lower() in ['ptp', 'p2p']:
                        if 'ul' in data.service_name.strip().lower():
                            c = colors[0]
                        elif 'dl' in data.service_name.strip().lower():
                            c = colors[1]
                        else:
                            pass
                    temp_chart_data[data.service_name, data.data_source] = {
                        'name': service_data_sources[data.service_name, data.data_source],
                        'data': [],
                        'color': c,
                        'type': SERVICE_DATA_SOURCE[data.service_name.strip() + "_" +data.data_source.strip()]['type']
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
                    'type': 'spline',
                    'chart_data': chart_data,
                    'valuetext': '  '
                }
            }
        }

        if(not chart_data or len(chart_data) == 0):
            result['message'] = 'Device Utilization Data not found'

        return HttpResponse(json.dumps(result), content_type="application/json")


def getLastXMonths(months_count):

    """
    This function returns last x months 'years,month' tuple & all months name, alias list
    :param months_count:
    :return:
    """
    all_months_list = [
        {"name": "jan", "alias": "Jan"},
        {"name": "feb", "alias": "Feb"},
        {"name": "march", "alias": "March"},
        {"name": "april", "alias": "April"},
        {"name": "may", "alias": "May"},
        {"name": "june", "alias": "June"},
        {"name": "july", "alias": "July"},
        {"name": "aug", "alias": "Aug"},
        {"name": "sept", "alias": "Sept"},
        {"name": "oct", "alias": "Oct"},
        {"name": "nov", "alias": "Nov"},
        {"name": "dec", "alias": "Dec"}
    ]

    now = time.localtime()

    last_six_months_list = [
        time.localtime(
            time.mktime(
                (now.tm_year, now.tm_mon - n, 1, 0, 0, 0, 0, 0, 0)
            )
        )[:2] for n in range(months_count)
    ]

    # Reverse months list
    last_six_months_list.reverse()

    return last_six_months_list, all_months_list


def get_device_status_headers(page_type='network', type_of_device=None, technology=None):
    """
    This function returns device status headers as per given
    technology & type_of_device(sub_station, sector, backhaul, other)
    :param technology:
    :param type_of_device:
    :param page_type:
    """
    headers_list = []
    # app names
    inventory_app = 'inventory'
    device_app = 'device'

    # technology & type
    device_tech_name = "device_technology"
    device_tech_key = "tech_id"

    device_type_name = "device_type"
    device_type_key = "type_id"

    # common Params
    bs_name_obj = {
        "name": "bs_name",
        "title": "BS Name",
        "value": "NA",
        "url": "",
        "app_name": inventory_app,
        "url_name": "base_station_edit",
        "kwargs_name": 'pk',
        'pk_key' : 'bs_id'
    }

    ss_name_obj = {
        "name": "ss_name",
        "title": "SS Name",
        "value": "NA",
        "url": "",
        "app_name": inventory_app,
        "url_name": "sub_station_edit",
        "kwargs_name": 'pk',
        'pk_key' : 'ss_id'
    }

    ckt_obj = {
        "name": "circuit_id",
        "title": "Circuit ID",
        "value": "NA",
        "url": "",
        "app_name": inventory_app,
        "url_name": "circuit_edit",
        "kwargs_name": 'pk',
        'pk_key' : 'ckt_pk'
    }

    cust_obj = {
        "name": "customer_name",
        "title": "Customer Name",
        "value": "NA",
        "url": "",
        "app_name": inventory_app,
        "url_name": "customer_edit",
        "kwargs_name": 'pk',
        'pk_key' : 'cust_id'
    }

    tech_name_obj = {
        "name": device_tech_name,
        "title": "Technology",
        "value": "NA",
        "url": "",
        "app_name": device_app,
        "url_name": "device_technology_edit",
        "kwargs_name": "pk",
        'pk_key' : device_tech_key
    }

    type_name_obj = {
        "name": device_type_name,
        "title": "Type",
        "value": "NA",
        "url": "",
        "app_name": device_app,
        "url_name": "wizard-device-type-update",
        "kwargs_name": "pk",
        'pk_key' : device_type_key
    }

    city_name_obj = {
        "name": "city",
        "title": "City",
        "value": "NA",
        "url": "",
        "app_name": device_app,
        "url_name": "city_edit",
        "kwargs_name": "pk",
        'pk_key' : 'city_id'
    }

    state_name_obj = {
        "name": "state",
        "title": "State",
        "value": "NA",
        "url": "",
        "app_name": device_app,
        "url_name": "state_edit",
        "kwargs_name": "pk",
        'pk_key' : 'state_id'
    }

    device_url_params = {
        "value": "NA",
        "url": "",
        "app_name": device_app,
        "url_name": "device_edit",
        "kwargs_name": "pk",
        'pk_key' : 'device_id'
    }

    ip_specific_params = {
        "name": "ip_address",
        "title": "IP Address"
    }

    mac_specific_params = {
        "name": "mac_address",
        "title": "MAC Address"
    }

    near_ip_obj = {
        "name": "near_end_ip",
        "title": "Near End IP",
        "value": "NA",
        "url": "",
        "app_name": device_app,
        "url_name": "device_edit",
        "kwargs_name": "pk",
        'pk_key' : 'near_device_id'
    }

    polled_freq_obj = {
        "name": "polled_frequency",
        "title": "Frequency(MHz)",
        "value": "NA",
        "url": "",
        "app_name": device_app,
        "url_name": "device_frequency_edit",
        "kwargs_name": "pk",
        'pk_key' : 'freq_id'
    }

    ip_obj = ip_specific_params.copy()
    ip_obj.update(device_url_params)

    mac_obj = mac_specific_params.copy()
    mac_obj.update(device_url_params)

    if type_of_device in ['sector']:
        headers_list = [
            bs_name_obj,
            tech_name_obj,
            type_name_obj,
            city_name_obj,
            state_name_obj,
            ip_obj,
            {
                "name": "planned_frequency",
                "title": "Planned Frequency(MHz)",
                "value": "NA",
                "url": ""
            },
            polled_freq_obj
        ]

        if technology in ['P2P', 'PTP', 'ptp', 'p2p']:
            headers_list.append(cust_obj)
            # For PTP near end devices add QOS BW column
            if page_type == 'customer':
                headers_list.append({
                    "name": "qos_bw",
                    "title": "Qos(Mbps)",
                    "value": "NA",
                    "url": ""
                })
        elif technology.lower() in ['wimax']:
            headers_list.append({
                "name": "sector_sector_id",
                "title": "Sector ID",
                "value": "NA",
                "url": "",
                "app_name": inventory_app,
                "url_name": "sector_edit",
                "kwargs_name": "pk",
                'pk_key' : 'sect_pk'
            })
            headers_list.append({
                "name": "pmp_port",
                "title": "PMP Port",
                "value": "NA",
                "url": "",
                "app_name": inventory_app,
                "url_name": "sector_edit",
                "kwargs_name": "pk",
                'pk_key' : 'sect_pk'
            })
        else:
            headers_list.append({
                "name": "sector_sector_id",
                "title": "Sector ID",
                "value": "NA",
                "url": "",
                "app_name": inventory_app,
                "url_name": "sector_edit",
                "kwargs_name": "pk",
                'pk_key' : 'sect_pk'
            })

    elif type_of_device in ['sub_station']:
        headers_list = [
            bs_name_obj,
            ss_name_obj,
            ckt_obj,
            cust_obj,
            tech_name_obj,
            type_name_obj,
            city_name_obj,
            state_name_obj,
            near_ip_obj,
            ip_obj,
            mac_obj,
            {
                "name": "qos_bw",
                "title": "Qos(Mbps)",
                "value": "NA",
                "url": ""
            },
            polled_freq_obj
        ]

    elif type_of_device in ['backhaul', 'other']:
        headers_list = [
            ip_obj,
            tech_name_obj,
            type_name_obj,
            bs_name_obj,
            city_name_obj,
            state_name_obj
        ]

        if type_of_device in ['backhaul']:
            headers_list.append({
                "name": "bh_port",
                "title": "BH Port",
                "value": "NA",
                "url": "",
                "app_name": inventory_app,
                "url_name": "base_station_edit",
                "kwargs_name": "pk",
                'pk_key' : 'bs_id'
            })

            headers_list.append({
                "name": "bh_capacity",
                "title": "BH Capacity(mbps)",
                "value": "NA",
                "url": "",
                "app_name": inventory_app,
                "url_name": "base_station_edit",
                "kwargs_name": "pk",
                'pk_key' : 'bs_id'
            })

    return headers_list


#TODO: Move to performance utils
def get_higher_severity(severity_dict):
    """

    :param severity_dict:
    :return:
    """
    s, a = None, None
    for severity in severity_dict:
        s = severity
        a = severity_dict[severity]

        if severity in ['down']:
            return severity, severity_dict[severity]
        elif severity in ['critical']:
            return severity, severity_dict[severity]
        elif severity in ['warning']:
            return severity, severity_dict[severity]
        elif severity in ['unknown']:
            continue
        else:
            continue

    return s, a


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_PERFORMANCE', 300))  # just for 2 minutes cache this. short running query
def device_current_status(device_object):
    """
    Device UP Status
    :param device_object:
    """
    # get the current status
    # if the current status is OK
    # check when was the element last down

    severity = dict()
    pl_value = None
    pl_age = {'age': 0, 'down': 0}

    required_fields = ['age', 'severity', 'current_value', 'sys_timestamp', 'data_source', 'refer']

    inventory_device_name = device_object.device_name
    inventory_device_machine_name = device_object.machine.name

    device_nms_uptime_query_set = NetworkStatus.objects.filter(
        device_name=inventory_device_name,
        service_name='ping',
        data_source__in=['pl']# ['pl', 'rta']
    ).using(alias=inventory_device_machine_name).values(*required_fields)

    device_nms_uptime = device_nms_uptime_query_set

    if device_nms_uptime:
        for data in device_nms_uptime:
            severity[data['severity']] = {'age': data['age'], 'down': data['refer']}
            if data['data_source'].strip().lower() == 'pl':
                pl_value = data['current_value']
                pl_age['age'] = data['age']  # refer field holds the last down time
                pl_age['down'] = data['refer']  # refer field holds the last down time
            else:
                continue
    else:
        return None, None

    if pl_value and float(pl_value) == 100:  # if PL = 100 that means AGE = AGE since PL was 100
        return 'down', pl_age
    else:
        s, a = get_higher_severity(severity_dict=severity)
        if s and s.strip().lower() == 'down':
            s = 'critical'
            return s, a
        else:
            return get_higher_severity(severity_dict=severity)


@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_PERFORMANCE', 300))  #for 5 minutes cache this. long running query
def device_last_down_time(device_object):
    """

    :param device_object:
    :return:
    """
    #first check the current PL state of the device
    s, a = device_current_status(device_object=device_object)
    return a['down']  # return the last down time of the device
    