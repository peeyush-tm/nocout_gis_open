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
from django.conf import settings
from django.shortcuts import render_to_response, render
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.base import View
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.dateformat import format

from device.models import Device, DeviceType, DeviceTechnology, DevicePort
from service.models import ServiceDataSource,Service
from machine.models import Machine
from inventory.models import SubStation, Circuit, Sector, BaseStation, Backhaul, PowerSignals, Customer, CircuitContacts
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
    UtilizationBiHourly, UtilizationHourly, UtilizationDaily, UtilizationWeekly, UtilizationMonthly, UtilizationYearly, \
    CustomDashboard, DSCustomDashboard, PingStabilityTest

from dashboard.utils import MultiQuerySet
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway, getBSInventoryInfo, getSSInventoryInfo, getSectorInventoryInfo, getBHInventoryInfo

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
    AVG_CHART_COLOR, CACHE_TIME, ENV_NAME, SHOW_SS_PERF_LINK_IA_TABLE, \
    WARN_COLOR, CRIT_COLOR, WARN_TYPE, CRIT_TYPE, MULTI_PROCESSING_ENABLED

from performance.formulae import display_time, rta_null

# Create instance of 'ServiceUtilsGateway' class
from user_profile.utils.auth import in_group

from user_profile.models import PowerLogs
from django.views.decorators.csrf import csrf_exempt
import os
from nocout.settings import BASE_DIR
from alert_center.models import PlannedEvent

service_utils = ServiceUtilsGateway()

##execute this globally
SERVICE_DATA_SOURCE = service_utils.service_data_sources()

import logging

log = logging.getLogger(__name__)

### SMS Sending
import requests

#### SMS GATEWAY SETTINGS
GATEWAY_SETTINGS = {
    'URL': 'http://121.244.239.140/csend.dll'
}
GATEWAY_PARAMETERS = {
    'Username': 'wirelessonetool',
    'Password': '12345vgsmhttp',
    'Priority': 3,
    'Commmethod': 'cellent',
    'Returnseq': 1,
    'Sender': 'TATACOMM Anil . Now',
    'N': '',
    'M': ''
}
#### SMS GATEWAY SETTINGS

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
        name_key = 'bs_name'
        name_title = 'BS Name'

        if page_type == 'pe':
            name_key = 'pe_hostname'
            name_title = 'PE Hostname'

        common_headers = [
            {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'auto', 'bSortable': True},
            {'mData': name_key, 'sTitle': name_title, 'sWidth': 'auto', 'bSortable': True},
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
            # if in_group(self.request.user, 'admin'):
            #     organizations = list(self.request.user.userprofile.organization.get_descendants(include_self=True))
            # else:
            #     organizations = [self.request.user.userprofile.organization]
            organizations = list(self.request.user.userprofile.organization.get_descendants(include_self=True))

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
        elif page_type == 'pe':
            type_rf = 'pe'
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
        other_type = self.request.GET.get('other_type')
        alert_page_type = page_type

        # In case of other page update page type to 'network' for alert center link
        if page_type not in ["customer", "network"]:
            alert_page_type = 'network'

        if other_type == 'pe':
            page_type = 'pe'
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

                try:
                    latency = round(float(dct.get('latency')), 3)
                except Exception, e:
                    latency = dct.get('latency')

                try:
                    packet_loss = round(float(dct.get('packet_loss')), 3)
                except Exception, e:
                    packet_loss = dct.get('packet_loss')

                dct.update(
                    latency=latency,
                    packet_loss=packet_loss,
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
        device_type = DeviceType.objects.get(id=device.device_type).name
        realdevice = device
        bs_alias = None
        bs_id = list()
        is_radwin5 = 0
        is_others_other_tab = 0
        is_viewer_flag = 0
        user_role = self.request.user
        sector_configured_on_id = []

        try:
            if 'radwin5' in device_type.lower():
                is_radwin5 = 1
        except Exception, e:
            is_radwin5 = 0

        '''
        This flag is needed because if device is in Other Live's Other tab
        then hide Topology view tab
        '''
        try:
            if page_type not in ['network', 'customer']:
                if not device.backhaul.exists():
                    is_others_other_tab = 1
        except Exception, e:
            pass

        try:
            if in_group(self.request.user, 'viewer'):
                is_viewer_flag = 1
        except Exception, e:
            is_viewer_flag = 0       

        sector_perf_url = None
        bh_perf_url = None
        try:
            if device.sector_configured_on.exists():
                bs_obj = device.sector_configured_on.filter()[0].base_station
                bs_alias = bs_obj.alias
                bs_id = [str(bs_obj.id)]
            elif device.dr_configured_on.exists():
                bs_obj = device.dr_configured_on.filter()[0].base_station
                bs_alias = bs_obj.alias
                bs_id = [str(bs_obj.id)]
            elif device.substation_set.exists():
                sector_obj = Sector.objects.get(
                    id=Circuit.objects.get(
                        sub_station=device.substation_set.get().id
                    ).sector_id
                )
                bs_obj = sector_obj.base_station
                bs_alias = bs_obj.alias
                bs_id = [str(bs_obj.id)]
                sector_configured_on_id = sector_obj.sector_configured_on_id

                try:
                    sector_perf_url  = reverse(
                        'SingleDevicePerf',
                        kwargs={'page_type': 'network', 'device_id': sector_obj.sector_configured_on.id},
                        current_app='performance'
                    )
                except Exception, e:
                    pass

                try:
                    bh_perf_url = reverse(
                        'SingleDevicePerf',
                        kwargs={'page_type': 'other', 'device_id': bs_obj.backhaul.bh_configured_on.id},
                        current_app='performance'
                    )
                except Exception, e:
                    pass
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

                bh_bs_ids = BaseStation.objects.filter(
                    backhaul= bh_id
                ).values_list('id', flat=True)
                bs_id = [str(bs_id) for bs_id in bh_bs_ids]
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

        power_listing_headers = []
        if page_type in ['customer']:
            power_listing_headers = [
                {'mData': 'msg', 'sTitle': 'Message'},
                {'mData': 'created_at', 'sTitle': 'Timestamp'},
                {'mData': 'status_type', 'sTitle': 'Status Type'}
            ]
        
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

        if sector_perf_url:
            sector_perf_url += '?is_util=1'

        if bh_perf_url:
            bh_perf_url += '?is_util=1'

        page_data = {
            'page_title': page_type.capitalize(),
            'device_technology': device_technology,
            'device_type': device_type,
            'device': device,
            'realdevice': realdevice,
            'bs_alias' : bs_alias,
            'is_others_other_tab': is_others_other_tab,
            'bs_id' : json.dumps(bs_id),
            'sector_configured_on_id' : json.dumps(sector_configured_on_id),
            'get_status_url': inventory_status_url,
            'get_services_url': service_ds_url,
            'inventory_page_url': inventory_page_url,
            'alert_page_url': alert_page_url,
            'page_type': page_type,
            'live_poll_config': json.dumps(LIVE_POLLING_CONFIGURATION),
            'is_util_tab': int(is_util_tab),
            'is_dr_device' : is_dr_device,
            'is_radwin5' : is_radwin5,
            'is_viewer_flag': is_viewer_flag,
            'perf_base_url' : 'performance/service/srv_name/service_data_source/all/device/' + str(device_id),
            'power_listing_headers': json.dumps(power_listing_headers),
            'sector_perf_url': sector_perf_url,
            'bh_perf_url': bh_perf_url
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
        elif device.pe_ip.exists():
            type_of_device = "other"
            type_rf = 'pe'
            page_type = 'pe'
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
            if device_tech in ['WiMAX'] or page_type in ['other']:
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

            if list_devices_invent_info:
                lowered_device_tech = list_devices_invent_info[0]['device_technology'].lower()
                # get device name from fetched info
                device_name = list_devices_invent_info[0]['device_name']
                # get machine name from fetched info
                machine_name = list_devices_invent_info[0]['machine_name']
                # If customer device then fetch the polled frequency from distributed DB's
                if (page_type == 'customer') or (page_type == 'network' and lowered_device_tech in ['ptp', 'p2p']):
                    service_name = ''
                    ds_name = ''
                    if lowered_device_tech in ['ptp', 'p2p']:
                        service_name = 'radwin_frequency_invent'
                    elif lowered_device_tech == 'pmp':
                        try:
                            device_type_name = DeviceType.objects.get(
                                id=Device.objects.get(device_name=device_name).device_type
                            ).name
                            device_type_name = device_type_name.lower()
                        except Exception, e:
                            device_type_name = ''

                        if 'cambium' in device_type_name or 'canopy' in device_type_name:
                            service_name = 'cambium_ss_frequency_invent'
                        else:
                            service_name = 'rad5k_ss_frequency_invent'
                    elif  lowered_device_tech == 'wimax':
                        service_name = 'wimax_ss_frequency'
                    else:
                        pass

                    if service_name and device_name and machine_name:
                        if lowered_device_tech in ['wimax']:
                            freq_data_obj = ServiceStatus.objects.filter(
                                device_name=device_name,
                                service_name=service_name,
                                data_source='frequency'
                            ).order_by('-sys_timestamp').using(alias=machine_name)[:1]
                        else:
                            freq_data_obj = InventoryStatus.objects.filter(
                                device_name=device_name,
                                service_name=service_name,
                                data_source='frequency'
                            ).order_by('-sys_timestamp').using(alias=machine_name)[:1]

                        if freq_data_obj and freq_data_obj[0].current_value:
                            list_devices_invent_info[0]['polled_frequency'] = freq_data_obj[0].current_value

                # If SS device & of PMP or Wimax Technology then fetch the qos_bandwidth from distributed DB
                if page_type == 'customer' and lowered_device_tech in ['pmp', 'wimax']:
                    
                    list_devices_invent_info[0]['polled_sector_id'] = ''

                    service_name = ''
                    ds_name = ''
                    model_name = InventoryStatus
                    invent_machine_name = machine_name
                    sector_id_service_name = ''
                    sector_id_ds_name = ''
                    
                    # GET Service & DS as per the technology
                    if lowered_device_tech in ['pmp']:
                        service_name = 'cambium_qos_invent'
                        ds_name = 'bw_dl_sus_rate'

                        sector_id_service_name = 'cambium_ss_sector_id_invent'
                        sector_id_ds_name = 'ss_sector_id'

                    elif lowered_device_tech in ['wimax']:
                        service_name = 'wimax_qos_invent'
                        ds_name = 'dl_qos'

                        model_name = ServiceStatus
                        sector_id_service_name = 'wimax_ss_sector_id'
                        sector_id_ds_name = 'ss_sector_id'

                    # If we have device_name, machine_name, service & db only then proceed
                    if device_name and machine_name and service_name and ds_name:
                        invent_status_obj = InventoryStatus.objects.filter(
                            device_name=device_name,
                            service_name=service_name,
                            data_source=ds_name
                        ).order_by('-sys_timestamp').using(alias=machine_name)[:1]

                        if invent_status_obj and invent_status_obj[0].current_value:
                            list_devices_invent_info[0]['qos_bw'] = invent_status_obj[0].current_value

                    if model_name and device_name and invent_machine_name and sector_id_service_name and sector_id_ds_name:
                        sector_invent_obj = model_name.objects.filter(
                            device_name=device_name,
                            service_name__iexact=sector_id_service_name,
                            data_source__iexact=sector_id_ds_name
                        ).order_by('-sys_timestamp').using(
                            alias=invent_machine_name
                        )

                        if sector_invent_obj:
                            list_devices_invent_info[0]['polled_sector_id'] = sector_invent_obj[0].current_value

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
                    },
                    'custom_dashboard_tab':{
                        "info": [],
                        "isActive": 0

                    },
                    'power_content':{
                        "info": [{
                            'name': "power_signal",
                            'title': "Power Signals",
                            'url': 'performance/powerlisting/?device_id=' + str(device_id),
                            'active': 1
                        }],
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

        is_other_device = False

        if not device.backhaul.exists():
            if device.backhaul_switch.exists() or device.backhaul_pop.exists() or device.backhaul_aggregator.exists():
                is_other_device = True

        if service_view_type == 'normal':

            result['data']['objects']['network_perf_tab']["info"].append({
                'name': "pl",
                'title': "Packet Drop",
                'url': 'performance/service/ping/service_data_source/pl/device/' + str(device_id),
                'active': 0,
                'sds_key': 'pl',
                'service_type_tab': 'network_perf_tab'
            })

            result['data']['objects']['network_perf_tab']["info"].append({
                'name': "rta",
                'title': "Latency",
                'url': 'performance/service/ping/service_data_source/rta/device/' + str(device_id),
                'active': 0,
                'sds_key': 'rta',
                'service_type_tab': 'network_perf_tab'
            })

            if device.substation_set.exists():
                result['data']['objects']['network_perf_tab']["info"].append({
                    'name': "rf",
                    'title': "RF Latency",
                    'url': 'performance/service/rf/service_data_source/rf/device/' + str(device_id),
                    'active': 0,
                    'sds_key': 'rf',
                    'service_type_tab': 'network_perf_tab'
                })

            is_bh = False
            excluded_bh_data_sources = []
            if device.backhaul.exists():
                # if the backhaul exists, that means we need to check for the PORT
                # if there is a port
                try:
                    ports = device.backhaul.get().basestation_set.filter().values_list('bh_port_name', flat=True)
                    those_ports = list()
                    try:
                        for port in ports:
                            if ',' in port:
                                try:
                                    those_ports.extend(port.replace(' ', '').split(','))
                                except Exception, e:
                                    those_ports.extend(port.split(','))
                            else:
                                those_ports.append(port)
                    except Exception, e:

                        those_ports = ports

                    bh_data_sources = ServiceDataSource.objects.filter(
                        name__in=DevicePort.objects.filter(alias__in=those_ports).values_list('name', flat=True)
                    ).values_list('name', flat=True)

                    excluded_bh_data_sources = list(ServiceDataSource.objects.filter(
                        name__in=DevicePort.objects.filter().values_list('name', flat=True)
                    ).exclude(
                        name__in=bh_data_sources).values_list('name', flat=True))

                    excluded_bh_data_sources_status = [str(x)+"_state" for x in excluded_bh_data_sources]
                    excluded_bh_data_sources += excluded_bh_data_sources_status

                    excluded_bh_data_sources_kpi = [str(x)+"_kpi" for x in excluded_bh_data_sources]
                    excluded_bh_data_sources += excluded_bh_data_sources_kpi

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
                                    'sds_key': service_name + '_' + sds_name
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
                        if is_other_device:
                            if 'util' not in service_name:
                                result['data']['objects']['service_perf_tab']["info"].append(sds_info)
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
                    if is_other_device:
                        if 'util' not in service_name:
                            result['data']['objects']['service_perf_tab']["info"].append(sds_info)
                    else:
                        result['data']['objects']['service_perf_tab']["info"].append(sds_info)

        result['data']['objects']['availability_tab']["info"].append({
            'name': 'availability',
            'title': 'Availability',
            'url': 'performance/service/availability/service_data_source/availability/device/' +
                   str(device_id),
            'active': 0
        })

        if not device.pe_ip.exists():
            result['data']['objects']['topology_tab']["info"].append({
                'name': 'topology',
                'title': 'Topology',
                'url': 'performance/service/topology/service_data_source/topology/device/' +
                       str(device_id),
                'active': 0
            })

        if not device.pe_ip.exists():
            result['data']['objects']['utilization_top_tab']["info"].append({
                'name': 'utilization_top',
                'title': 'Utilization',
                'url': 'performance/servicedetail/util/device/'+str(device_id),
                'active': 0
            })
        
        custom_dashboard = CustomDashboard.objects.filter(Q(user_profile=self.request.user.pk) | Q(is_public=1))       

        for dashboard in custom_dashboard:
            cdb_info = {
                    'name': dashboard.name,                    
                    'title': dashboard.title.strip(),
                    'url': 'performance/custom_dashboard/' + str(dashboard.id) +
                            '/device/' + str(device_id),
                    'active': 0,
                }
            
            result['data']['objects']['custom_dashboard_tab']["info"].append(cdb_info)
                

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
        # Device Machine Name required in query to fetch data.
        inventory_device_machine_name = device.machine.name 
        # If 'only_service' is set, only then send the status as per service
        only_service = self.request.GET.get('only_service')
        # GET param to detect the request is for service view or data_source view
        display_view = self.request.GET.get('service_view_type', 'normal')
        # Is service view flag
        is_unified_view = display_view and display_view == 'unified'

        """
        get the current status,
        if the current status is OK
        check when was the element last down
        """
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

        if only_service and service_name not in ['ping']:
            if '_invent' in service_name:
                table_name = 'performance_inventorystatus'
                model_name = InventoryStatus
            elif '_status' in service_name:
                table_name = 'performance_status'
                model_name = Status
            else:
                table_name = 'performance_servicestatus'
                model_name = ServiceStatus

            severity_status = self.getSeverity(
                table_name=table_name, 
                machine_name=inventory_device_machine_name, 
                device_name=inventory_device_name,
                service_name=service_name,
                is_unified_view=True
            )

            severities = list()
            if severity_status.get('ok', 0) > 0:
                severities = ['ok', 'up']

            if severity_status.get('down', 0) > 0:
                severities = ['critical', 'down', 'crit']

            if severity_status.get('warn', 0) > 0:
                severities = ['warning', 'warn']

            if severity_status.get('unknown', 0) > 0:
                severities = ['unknown']

            result = model_name.objects.filter(
                service_name=service_name,
                severity__in=severities
            ).values('severity', 'sys_timestamp').using(alias=inventory_device_machine_name)

            if result.count() > 0:
                try:
                    last_updated = datetime.datetime.fromtimestamp(
                        float(result[0]['sys_timestamp'])
                    ).strftime(DATE_TIME_FORMAT)
                    severity_val = result[0]['severity'].lower().strip() if result[0]['severity'] else None

                    self.result['data']['objects']['last_updated'] = last_updated
                    self.result['data']['objects']['status'] = severities[0]
                except Exception as e:
                    log.exception(e.message)

        else:
            pass

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
                machine_name=inventory_device_machine_name,
                is_unified_view=is_unified_view
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
        else:
            pass

        # Update severity if planned event is defined for current ip address
        try:
            planned_events = nocout_utils.get_current_planned_event_ips(ip_address=device.ip_address)
            if planned_events:
                self.result['data']['objects']['pl_status'] = 'inDownTime'
        except Exception as e:
            pass

        return HttpResponse(json.dumps(self.result), content_type="application/json")

    def get_status_severity(
        self,
        device_name=None,
        machine_name=None,
        is_unified_view=False
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
        # network_severity = self.getSeverity(
        #     table_name='performance_networkstatus', 
        #     machine_name=machine_name, 
        #     device_name=device_name,
        #     is_unified_view=is_unified_view
        # )
        # InventoryStatus Severity
        invent_severity = self.getSeverity(
            table_name='performance_inventorystatus', 
            machine_name=machine_name, 
            device_name=device_name,
            is_unified_view=is_unified_view
        )
        # Status Severity
        status_severity = self.getSeverity(
            table_name='performance_status', 
            machine_name=machine_name, 
            device_name=device_name,
            is_unified_view=is_unified_view
        )
        # UtilizationStatus Severity
        utilization_severity = self.getSeverity(
            table_name='performance_utilizationstatus', 
            machine_name=machine_name, 
            device_name=device_name,
            is_unified_view=is_unified_view
        )
        # ServiceStatus Severity
        service_severity = self.getSeverity(
            table_name='performance_servicestatus', 
            machine_name=machine_name, 
            device_name=device_name,
            is_unified_view=is_unified_view
        )

        # Sum all severities count
        total_ok = status_severity.get('ok', 0) + invent_severity.get('ok', 0) + utilization_severity.get('ok', 0) + service_severity.get('ok', 0)
        total_warn = status_severity.get('warn', 0) + invent_severity.get('warn', 0) + utilization_severity.get('warn', 0) + service_severity.get('warn', 0)
        total_crit = status_severity.get('crit', 0) + invent_severity.get('crit', 0) + utilization_severity.get('crit', 0) + service_severity.get('crit', 0)
        total_unknown = status_severity.get('unknown', 0) + invent_severity.get('unknown', 0) + utilization_severity.get('unknown', 0) + service_severity.get('unknown', 0)

        # Update severity_count_dict
        severity_count_dict.update(
            ok=total_ok,
            warn=total_warn,
            crit=total_crit,
            unknown=total_unknown
        )

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

    def getSeverity(self, table_name=None, machine_name=None, device_name=None, service_name=None, is_unified_view=False):
        """

        """
        severity_list = list()
        extra_column = ''
        if not device_name or not table_name or not machine_name:
            return severity_list

        if is_unified_view:
            extra_column = ' , service_name '

        severity_query = '''
                         SELECT 
                            IF(
                                ISNULL(SUM(severity='ok' OR severity='up')),
                                0,
                                SUM(severity='ok' OR severity='up')
                            ) AS ok,
                            IF(
                                ISNULL(SUM(severity='down' OR severity='critical' OR severity='crit')),
                                0,
                                SUM(severity='down' OR severity='critical' OR severity='crit')
                            ) AS crit,
                            IF(
                                ISNULL(SUM(severity='warning' OR severity='warn')),
                                0,
                                SUM(severity='warning' OR severity='warn')
                            ) AS warn,
                            IF(
                                ISNULL(SUM(severity='unknown')),
                                0,
                                SUM(severity='unknown')
                            ) AS unknown
                         FROM 
                            {0} 
                         WHERE 
                            device_name = {1}
                         '''.format(table_name, device_name)

        if service_name:
            severity_query += " AND service_name = '{0}' ".format(service_name)

        if is_unified_view:
            severity_query += " GROUP BY service_name "

        # Execute Query to get severity data
        severity_response = nocout_utils.fetch_raw_result(query=severity_query, machine=machine_name)

        # If not unified view then send dict object else list
        if is_unified_view:
            severity_counters = {
                "ok": 0,
                "warn": 0,
                "crit": 0,
                "unknown": 0,
            }

            for severity_obj in severity_response:
                if severity_obj.get('crit', 0) > 0 or severity_obj.get('warn', 0) > 0:
                    if severity_obj.get('crit', 0) > 0:
                        severity_counters['crit'] += 1
                    else:
                        severity_counters['warn'] += 1
                elif severity_obj.get('ok', 0) > 0:
                    severity_counters['ok'] += 1
                else:
                    severity_counters['unknown'] += severity_obj.get('unknown', 0)

            severity_response = [severity_counters]

        return severity_response[0]


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
            {'mData': 'sys_timestamp', 'sTitle': 'Time', 'sWidth': 'auto'},
            {'mData': 'data_source', 'sTitle': 'Data Source', 'sWidth': 'auto'},
            {'mData': 'current_value', 'sTitle': 'Current Value', 'sWidth': 'auto'},
            {'mData': 'severity', 'sTitle': 'Severity', 'sWidth': 'auto'},
            {'mData': 'warning_threshold', 'sTitle': 'Warning Threshold', 'sWidth': 'auto'},
            {'mData': 'critical_threshold', 'sTitle': 'Critical Threshold', 'sWidth': 'auto'},
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
        'sys_timestamp',
        'current_value',
        'severity',
        'warning_threshold',
        'critical_threshold',
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

    sds_type = 'Numeric'

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
        is_unified_view = (service_view_type and service_view_type == 'unified') or data_source == 'all'

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
            self.columns = [
                'sys_timestamp',
                'data_source',
                'current_value',
                'severity',
                'warning_threshold',
                'critical_threshold',
                'service_name',
                'min_value',
                'max_value',
                'avg_value',
                'ip_address'
            ]

            for sds in SERVICE_DATA_SOURCE:
                if not self.formula:
                    if service.strip().lower() in sds and SERVICE_DATA_SOURCE[sds]['type'] == 'table':
                        self.formula = SERVICE_DATA_SOURCE[sds]['formula']
                else:
                    break

            for sds in SERVICE_DATA_SOURCE:
                if self.sds_type != 'String':
                    if service.strip().lower() in sds and 'data_source_type' in SERVICE_DATA_SOURCE[sds]:
                        self.sds_type = SERVICE_DATA_SOURCE[sds]['data_source_type']
                else:
                    break
            if 'min_value' not in self.columns:
                self.columns.append('min_value')

            if 'max_value' not in self.columns:
                self.columns.append('max_value')
        else:
            if data_for == 'live' and data_source not in ['rta']:
                self.columns = [
                    'sys_timestamp',
                    'current_value',
                    'severity',
                    'warning_threshold',
                    'critical_threshold',
                    'service_name',
                    'min_value',
                    'max_value',
                    'avg_value',
                    'ip_address',
                    'data_source'
                ]
            else:
                self.columns = [
                    'sys_timestamp',
                    'avg_value',
                    'min_value',
                    'max_value',
                    'current_value',
                    'severity',
                    'warning_threshold',
                    'critical_threshold',
                    'service_name',
                    'data_source'
                ]

            if self.data_source in SERVICE_DATA_SOURCE and 'data_source_type' in  SERVICE_DATA_SOURCE[self.data_source]:
                self.sds_type = SERVICE_DATA_SOURCE[self.data_source].get('data_source_type', 'Numeric')
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
            'services': [str(service)],
            'sds': [str(data_source)]
        }

        self.order_columns = self.columns

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

            display_name = item['data_source']

            # Prepare sds key to fetch actual display name for DS
            if item['data_source'] in ['pl', 'rta', 'availability']:
                sds_key = item['data_source']
            else:
                sds_key = str(item['service_name']).strip().lower() + '_' + str(item['data_source']).strip().lower()
            try:
                if SERVICE_DATA_SOURCE.get(sds_key):
                    display_name = SERVICE_DATA_SOURCE.get(sds_key).get('display_name')
            except Exception, e:
                display_name = item['data_source']

            item.update(
                data_source=display_name,
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
                    Q(data_source__icontains=sSearch)
                    |
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
        sort_using = ''
        reverse = ''
        order_columns = self.order_columns

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
            sort_using = order_columns[sort_col]

            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
            else:
                order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))
        if order:
            # Try catch is added because in some cases 
            # we receive list instead of queryset
            try:
                try:
                    if self.sds_type == 'Numeric' and sort_using == 'current_value':
                        sorted_device_data = qs.extra(
                            select={sort_using: 'CAST(' + sort_using + ' AS DECIMAL(9,3))'}
                        ).order_by(*order)
                    else:
                        sorted_device_data = qs.order_by(*order)
                except Exception, e:
                    sorted_device_data = qs.order_by(*order)
            except Exception, e:
                try:
                    sorted_device_data = sorted(
                        qs, 
                        key=itemgetter(sort_using),
                        reverse=True if '-' in order[0] else False
                    )
                except Exception, e:
                    sorted_device_data = qs

            return sorted_device_data
        return qs 

        # return nocout_utils.nocout_datatable_ordering(self, qs, self.order_columns)

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
            sds_name = service_name.strip().lower() + "_" + service_data_source_type.strip().lower()
        else:
            sds_name = service_data_source_type.strip()

        # to check if data source would be displayed as a chart or as a table
        show_chart = True

        service_view_type = self.request.GET.get('service_view_type')
        # is_unified_view = service_view_type and service_view_type == 'unified'
        is_unified_view = (service_view_type and service_view_type == 'unified') or service_data_source_type == 'all'

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
            try:
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

                    action_html = 'NA'
                    try:
                        if data.connected_device_ip:
                            device_instance = Device.objects.get(ip_address=data.connected_device_ip)
                            perf_page_url = reverse(
                                'SingleDevicePerf',
                                kwargs={'page_type': 'customer', 'device_id': device_instance.id},
                                current_app='performance'
                            )
                            action_html = '<a href="{0}" title="Device Performance" target="_blank"> \
                                           <i class="fa fa-bar-chart-o text-info"></i></a>'.format(perf_page_url)
                    except Exception, e:
                        pass

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
                        'action': action_html
                    })
            except Exception, e:
                pass

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
                try:
                    try:
                        vlan = self.ss_vlan_performance_data_result(
                            technology=technology,
                            ss_device_object=ss.device,
                            machine=ss.device.machine.name
                        )
                    except Exception, e:
                        vlan = None

                    try:
                        packet_loss, latency, status_since, last_down = self.ss_network_performance_data_result(
                            ss_device_object=ss.device,
                            machine=ss.device.machine.name
                        )
                    except Exception, e:
                        packet_loss = None
                        latency = None
                        status_since = None
                        last_down = None

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
                        action_html = 'NA'
                        try:
                            if device_ip:
                                device_instance = Device.objects.get(ip_address=device_ip)
                                perf_page_url = reverse(
                                    'SingleDevicePerf',
                                    kwargs={'page_type': 'customer', 'device_id': device_instance.id},
                                    current_app='performance'
                                )
                                action_html = '<a href="{0}" title="Device Performance" target="_blank"> \
                                               <i class="fa fa-bar-chart-o text-info"></i></a>'.format(perf_page_url)
                        except Exception, e:
                            pass

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
                            'action': action_html
                        })
                except Exception, e:
                    pass

        self.result['success'] = 1
        self.result['message'] = 'Device Data Fetched Successfully.' if result_data else 'No Record Found.'
        try:
            self.result['data']['objects']['table_data'] = result_data
        except Exception, e:
            self.result['data']['objects']['table_data'] = []

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

        if SHOW_SS_PERF_LINK_IA_TABLE:
            self.result['data']['objects']['table_data_header'].append('action')

        return self.result

    def ss_vlan_performance_data_result(self, technology, ss_device_object, machine):
        """
        provide the SS vlan data
        :param machine:
        :param ss_device_object:
        :param technology:
        """
        vlan = "NA"

        ss_type = None
        try:
            ss_type = DeviceType.objects.get(id=ss_device_object.device_type).name
        except Exception as e:
            pass

        if technology and technology.name.lower() in ['wimax']:
            service_name = 'wimax_ss_vlan_invent'
            data_source = 'ss_vlan'
        elif technology and technology.name.lower() in ['pmp']:
            if ss_type.lower() == 'radwin5kss':
                service_name = 'rad5k_man_vlan_invent'
                data_source = 'ss_vlan'
            else:
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
                            sds_name = str(data.service_name).strip().lower() + "_" + str(data.data_source).strip().lower()

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
                                      if abs(p2) <= abs(p1) < abs(p3)
                                      else ('#FF193B' if abs(p3) <= abs(p1) else chart_color)
                                )
                        else:
                            compare_point = lambda p1, p2, p3: chart_color \
                                if abs(p1) > abs(p2) \
                                else ('#FFE90D'
                                      if abs(p2) >= abs(p1) > abs(p3)
                                      else ('#FF193B' if abs(p3) >= abs(p1) else chart_color)
                                )

                        formula = SERVICE_DATA_SOURCE[sds_name]["formula"] \
                            if sds_name in SERVICE_DATA_SOURCE else None

                        if data.current_value:
                            val = float(data.current_value) if data.current_value else 0
                            warn_val = float(data.warning_threshold) if data.warning_threshold else val
                            crit_val = float(data.critical_threshold) if data.critical_threshold else val
                            c_color = chart_color

                            if data.warning_threshold not in ['', None] and data.critical_threshold not in ['', None]:
                                c_color = compare_point(val, warn_val, crit_val)

                            formatter_data_point = {
                                "name": sds_display_name,
                                "color": c_color,
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
            SERVICE_DATA_SOURCE = service_utils.service_data_sources()
            ds_list = list(set(performance_data.values_list('data_source', flat=True)))
            service_view_type = self.request.GET.get('service_view_type')
            is_unified_view = service_view_type and service_view_type == 'unified'
            counter = -1
            for ds in ds_list:
                try:
                    is_pl = False
                    legend_color = ''
                    if ds == 'pl':
                        is_pl = True
                        legend_color = 'transparent'
                    # Variables used for HISTORICAL data
                    data_list, warn_data_list, crit_data_list, aggregate_data = list(), list(), list(), dict()
                    data_list_min, data_list_max, data_list_avg =  list(), list(), list()
                    min_data_list = list()
                    max_data_list = list()
                    is_dual_axis = False
                    counter += 1
                    # If data source is PL/RTA then enable 'is_dual_axis' flag
                    if ds in ['pl', 'rta'] and is_unified_view:
                        is_dual_axis = True

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
                                    sds_name = str(data.service_name).strip().lower() + "_" + str(data.data_source).strip().lower()

                            sds_display_name = SERVICE_DATA_SOURCE[sds_name]["display_name"] \
                                if sds_name in SERVICE_DATA_SOURCE else str(data.data_source).upper()

                            if 'chart_display_name' not in self.result['data']['objects']:
                                self.result['data']['objects']['chart_display_name'] = ''

                            if sds_display_name not in self.result['data']['objects']['chart_display_name']:
                                if self.result['data']['objects']['chart_display_name']:
                                    self.result['data']['objects']['chart_display_name'] += ' & ' + sds_display_name
                                else:
                                    self.result['data']['objects']['chart_display_name'] += sds_display_name

                            self.result['data']['objects']['display_name'] = sds_display_name

                            display_name = sds_display_name

                            self.result['data']['objects']['type'] = SERVICE_DATA_SOURCE[sds_name]["type"] \
                                if sds_name in SERVICE_DATA_SOURCE else "area"
                            
                            if is_dual_axis:
                                self.result['data']['objects']['is_single'] = 0
                            else:
                                self.result['data']['objects']['is_single'] = 1
                                
                            if 'valuesuffix' not in self.result['data']['objects']:
                                self.result['data']['objects']['valuesuffix'] = list()
                            if 'valuetext' not in self.result['data']['objects']:
                                self.result['data']['objects']['valuetext'] = list()

                            ds_suffix = SERVICE_DATA_SOURCE[sds_name]["valuesuffix"] if sds_name in SERVICE_DATA_SOURCE else ""
                            ds_txt = SERVICE_DATA_SOURCE[sds_name]["valuetext"] if sds_name in SERVICE_DATA_SOURCE else str(data.data_source).upper()
                            
                            if ds_suffix not in self.result['data']['objects']['valuesuffix']:
                                self.result['data']['objects']['valuesuffix'].append(ds_suffix)

                            if ds_txt not in self.result['data']['objects']['valuetext']:
                                self.result['data']['objects']['valuetext'].append(ds_txt)
                            # else:
                            #     self.result['data']['objects']['valuesuffix'] = SERVICE_DATA_SOURCE[sds_name]["valuesuffix"] \
                            #         if sds_name in SERVICE_DATA_SOURCE else ""

                            #     self.result['data']['objects']['valuetext'] = SERVICE_DATA_SOURCE[sds_name]["valuetext"] \
                            #         if sds_name in SERVICE_DATA_SOURCE else str(data.data_source).upper()

                            self.result['data']['objects']['plot_type'] = SERVICE_DATA_SOURCE[sds_name].get('data_source_type', 'numeric')

                            chart_color = SERVICE_DATA_SOURCE[sds_name]["chart_color"] \
                                if sds_name in SERVICE_DATA_SOURCE else '#70AFC4'

                            sds_inverted = False
                            self.result['data']['objects']['is_inverted'] = sds_inverted

                            if sds_name not in ["availability"]:

                                self.result['data']['objects']['is_inverted'] = sds_inverted

                                if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["is_inverted"]:
                                    sds_inverted = SERVICE_DATA_SOURCE[sds_name]["is_inverted"]
                                    self.result['data']['objects']['is_inverted'] = sds_inverted

                                if not sds_inverted:
                                    compare_point = lambda p1, p2, p3: chart_color \
                                        if abs(p1) < abs(p2) \
                                        else ('#FFE90D'
                                              if abs(p2) <= abs(p1) < abs(p3)
                                              else ('#FF193B' if abs(p3) <= abs(p1) else chart_color)
                                        )
                                else:
                                    compare_point = lambda p1, p2, p3: chart_color \
                                        if abs(p1) > abs(p2) \
                                        else ('#FFE90D'
                                              if abs(p2) >= abs(p1) > abs(p3)
                                              else ('#FF193B' if abs(p3) >= abs(p1) else chart_color)
                                        )

                                formula = SERVICE_DATA_SOURCE[sds_name]["formula"] if sds_name in SERVICE_DATA_SOURCE else None

                                #only display warning if there exists a warning
                                if data.warning_threshold:
                                    try:
                                        warn_data_list.append([js_time, float(data.warning_threshold)])
                                    except Exception, e:
                                        warn_data_list.append([js_time, data.warning_threshold])

                                #only display critical if there exists a critical
                                if data.critical_threshold:
                                    try:
                                        crit_data_list.append([js_time, float(data.critical_threshold)])
                                    except Exception, e:
                                        crit_data_list.append([js_time, data.critical_threshold])

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
                                        try:
                                            val = float(data.current_value) if data.current_value else 0
                                        except Exception, e:
                                            val = ''

                                        if val or val == 0:
                                            warn_val = float(data.warning_threshold) if data.warning_threshold else val
                                            crit_val = float(data.critical_threshold) if data.critical_threshold else val
                                            try:
                                                current_value = eval(str(formula) + "(" + str(val) + ")") if formula else float(data.current_value)
                                            except Exception, e:
                                                pass

                                            if data.warning_threshold not in ['', None] and data.critical_threshold not in ['', None]:
                                                current_color = compare_point(val, warn_val, crit_val)
                                            else:
                                                current_color = chart_color
                                        else:
                                            continue

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
                                        try:
                                            val = float(data.current_value) if data.current_value else 0
                                        except Exception, e:
                                            val = ''

                                        if val or val == 0:
                                            warn_val = float(data.warning_threshold) if data.warning_threshold else val
                                            crit_val = float(data.critical_threshold) if data.critical_threshold else val
                                            
                                            try:
                                                current_value = eval(str(formula) + "(" + str(val) + ")") if formula else float(data.current_value)
                                            except Exception, e:
                                                pass

                                            if data.warning_threshold not in ['', None] and data.critical_threshold not in ['', None]:
                                                current_color = compare_point(val, warn_val, crit_val)
                                            else:
                                                current_color = chart_color

                                    data_list.append({
                                        "name": sds_display_name,
                                        "color": current_color,
                                        "y": current_value,
                                        "x": js_time
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

                    if data_list and len(data_list) > 0 and sds_name not in ["availability"]:
                        base_color = data_list[0]['color']
                        if is_pl:
                            base_color = legend_color
                        if is_dual_axis:
                            chart_data.append({
                                'name': self.result['data']['objects']['display_name'],
                                'data': data_list,
                                'yAxis' : counter,
                                'color' : base_color, #data_list[0]['color'],
                                'type': self.result['data']['objects']['type'],
                                'valuesuffix': self.result['data']['objects']['valuesuffix'],
                                'valuetext': self.result['data']['objects']['valuetext'],
                                'is_inverted': self.result['data']['objects']['is_inverted']
                            })
                        else:
                            chart_data.append({
                                'name': self.result['data']['objects']['display_name'],
                                'data': data_list,
                                'color' : base_color, #data_list[0]['color'],
                                'type': self.result['data']['objects']['type'],
                                'valuesuffix': self.result['data']['objects']['valuesuffix'],
                                'valuetext': self.result['data']['objects']['valuetext'],
                                'is_inverted': self.result['data']['objects']['is_inverted']
                            })

                        if len(min_data_list):
                            if is_dual_axis:
                                chart_data.append({
                                    'name': str("min value").title() + '(' + str(display_name) + ')' if is_unified_view else str("min value").title(),
                                    'color': '#01CC14',
                                    'data': min_data_list,
                                    'yAxis' : counter,
                                    'type': 'line',
                                    'marker': {
                                        'enabled': False
                                    }
                                })
                            else:
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
                            if is_dual_axis:
                                chart_data.append({
                                    'name': str("max value").title() + '(' + str(display_name) + ')' if is_unified_view else str("max value").title(),
                                    'color': '#FF8716',
                                    'yAxis' : counter,
                                    'data': max_data_list,
                                    'type': 'line',
                                    'marker': {
                                        'enabled': False
                                    }
                                })
                            else:
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
                            if is_dual_axis:
                                chart_data.append({
                                    'name': str("warning threshold").title() + '(' + str(display_name) + ')' if is_unified_view else str("warning threshold").title(),
                                    'color': WARN_COLOR,
                                    'data': warn_data_list,
                                    'yAxis' : counter,
                                    'type': WARN_TYPE,
                                    'marker': {
                                        'enabled': False
                                    }
                                })
                            else:
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
                            if is_dual_axis:
                                chart_data.append({
                                    'name': str("critical threshold").title() + '(' + str(display_name) + ')' if is_unified_view else str("critical threshold").title(),
                                    'color': CRIT_COLOR,
                                    'data': crit_data_list,
                                    'yAxis' : counter,
                                    'type': CRIT_TYPE,
                                    'marker': {
                                        'enabled': False
                                    }
                                })
                            else:
                                chart_data.append({
                                    'name': str("critical threshold").title() + '(' + str(display_name) + ')' if is_unified_view else str("critical threshold").title(),
                                    'color': CRIT_COLOR,
                                    'data': crit_data_list,
                                    'type': CRIT_TYPE,
                                    'marker': {
                                        'enabled': False
                                    }
                                })
                except Exception, e:
                    log.error(' ---------------- Single Device Perf Page - Chart ---------------- ')
                    log.error(e)
                    pass

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

        valuesuffix_list = list()
        valuetext_list = list()

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

            service_data_sources[temp_s_name, temp_sds_name] = s['servicespecificdatasource__service_data_sources__alias']

            try:
                sds_key = s['name'].strip().lower() + '_' + temp_sds_name.strip().lower()
                if sds_key in SERVICE_DATA_SOURCE:
                    if SERVICE_DATA_SOURCE[sds_key]['valuetext'] not in valuetext_list:
                        valuetext_list.append(SERVICE_DATA_SOURCE[sds_key]['valuetext'])

                    if SERVICE_DATA_SOURCE[sds_key]['valuesuffix'] not in valuesuffix_list:
                        valuesuffix_list.append(SERVICE_DATA_SOURCE[sds_key]['valuesuffix'])
            except Exception, e:
                pass

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
        temp_bh_color = {
            'ul': {},
            'dl': {}
        }

        bh_ul_colors = ['#B5E51D', '#9BDAEB']
        bh_dl_colors = ['#23B14D', '#00A3E8']

        for data in performance:
            try:
                if (data.service_name, data.data_source) not in temp_chart_data:
                    c = SERVICE_DATA_SOURCE[data.service_name.strip().lower() + "_" +data.data_source.strip().lower()]['chart_color']

                    if technology and technology.name.lower() in ['ptp', 'p2p']:
                        if 'ul' in data.service_name.strip().lower():
                            c = colors[0]
                        elif 'dl' in data.service_name.strip().lower():
                            c = colors[1]
                        else:
                            pass
                    elif is_bh and device_type.name.lower() in ['huawei', 'juniper', 'cisco']:
                        if 'ul' in data.service_name.strip().lower():
                            if data.data_source.strip().lower() not in temp_bh_color['ul']:
                                try:
                                    temp_bh_color['ul'][data.data_source.strip().lower()] = bh_ul_colors.pop(0)
                                    c = temp_bh_color['ul'][data.data_source.strip().lower()]
                                except Exception, e:
                                    temp_bh_color['ul'][data.data_source.strip().lower()] = c
                            else:
                                c = temp_bh_color['ul'][data.data_source.strip().lower()]
                        elif 'dl' in data.service_name.strip().lower():
                            if data.data_source.strip().lower() not in temp_bh_color['dl']:
                                try:
                                    temp_bh_color['dl'][data.data_source.strip().lower()] = bh_dl_colors.pop(0)
                                    c = temp_bh_color['dl'][data.data_source.strip().lower()]
                                except Exception, e:
                                    temp_bh_color['dl'][data.data_source.strip().lower()] = c
                            else:
                                c = temp_bh_color['dl'][data.data_source.strip().lower()]
                    else:
                        pass

                    try:
                        alias = service_data_sources[data.service_name.strip().lower(), data.data_source.strip().lower()]
                    except Exception, e:
                        alias = SERVICE_DATA_SOURCE[data.service_name.strip().lower() + "_" +data.data_source.strip().lower()]['service_alias']
                        name = SERVICE_DATA_SOURCE[data.service_name.strip().lower() + "_" +data.data_source.strip().lower()]['service_name']
                        if 'ul' in name.lower():
                            alias = 'UL : ' + alias
                        elif 'dl' in name.lower():
                            alias = 'DL : ' + alias
                        else:
                            alias = alias

                    if is_bh:
                        try:
                            ds_name = SERVICE_DATA_SOURCE[data.service_name.strip().lower() + "_" +data.data_source.strip().lower()]['ds_name']
                            if ds_name:
                                ds_name = ds_name.replace('_', '/')
                                alias += ' (' + ds_name.title() + ')'
                        except Exception, e:
                            pass

                    temp_chart_data[data.service_name, data.data_source] = {
                        'name': alias,
                        'data': [],
                        'color': c,
                        'type': SERVICE_DATA_SOURCE[data.service_name.strip().lower() + "_" +data.data_source.strip().lower()]['type']
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
                    'valuesuffix': valuesuffix_list[0] if valuesuffix_list else ' ',
                    'type': 'spline',
                    'is_single': 1,
                    'chart_data': chart_data,
                    'valuetext': valuetext_list[0] if valuetext_list else ' '
                }
            }
        }

        if(not chart_data or len(chart_data) == 0):
            result['message'] = 'Device Utilization Data not found'

        return HttpResponse(json.dumps(result), content_type="application/json")

class CustomDashboardPerformanceData(View):
    """
    Generic Class based View to Fetch the Performance Data.
    """

    def get(self, request, custom_dashboard_id, device_id):
        """
        Handles the get request to fetch performance data w.r.t to arguments requested.

        :param device_id:
        :param custom_dashboard_id:       
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

        try:
            dashboard_obj = CustomDashboard.objects.get(id=custom_dashboard_id)
        except Exception, e:
            self.result.update(
                message='Invalid dashboard ID'
            )
            return HttpResponse(json.dumps(self.result), content_type="application/json")

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
        result_data_combined=list()
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

        # data sources and service names of the data sources
        custom_data_source_names = DSCustomDashboard.objects.filter(custom_dashboard_id = custom_dashboard_id ).values('data_source__name', 'service__name')
        display_type = str(dashboard_obj.display_type).lower()
        result_data=list()
        ds_list = list()
        # to check if data source would be displayed as a chart or as a table
        for ds_obj in custom_data_source_names:
            data_source_type = ds_obj.get('data_source__name')
            service_name = ds_obj.get('service__name')
            show_chart = True if display_type == 'chart' else False
                        
            if data_source_type.strip() not in ['topology', 'rta', 'pl', 'availability', 'rf']:
                # for service in service_name:
                sds_name = service_name.strip().lower() + "_" + data_source_type.strip().lower()        
            else:
                sds_name = data_source_type.strip()            

            # check for the formula
            # for sds in sds_name:
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
                'sds': [data_source_type]
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

            if (service_name == 'ping' or data_source_type in ['pl', 'rta']) and data_source_type not in ['rf']:
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


            elif data_source_type == 'rf':
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

            elif "availability" in service_name or data_source_type in ['availability']:
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

            elif "topology" in service_name or data_source_type in ['topology']:
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
                    'sds': [data_source_type]
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
                    'sds': [data_source_type]
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
                    'sds': [data_source_type]
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
                    if performance_data:
                        dataset = self.get_performance_data_result(performance_data, '', is_historical_data)
                        result_data_combined.append(json.loads(json.dumps(dataset)))

            else:
                performance_data = self.get_performance_data(
                    **parameters
                ).using(alias=inventory_device_machine_name)

                if not show_chart:
                    # show the table
                    result = self.get_perf_table_result(
                        performance_data=performance_data,
                        formula=formula,
                        is_historical_data=is_historical_data
                    )
                else: # show the chart
                    if performance_data:
                        dataset = self.get_performance_data_result(performance_data, '', is_historical_data)
                        result_data_combined.append(json.loads(json.dumps(dataset)))
                        

        result = self.custom_charts_data_result(result_data_combined)        
        return HttpResponse(json.dumps(result), content_type="application/json")

    def custom_charts_data_result(self, performance_data):
        """
        :param performance_data_bs:
        :param performance_data_ss:
        """
        
        result = [{
            'success': 0,
            'message': 'Custom Dashboard Data not found',
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
        }]
        
        chart_data=list()     
        
        if performance_data and len(performance_data)==2:                    
            chart_data=performance_data[0]['data']['objects']['chart_data']+performance_data[1]['data']['objects']['chart_data']            
            self.result['data']['objects']['chart_data'] = chart_data

            if performance_data[0]['data']['objects']['valuesuffix'] == performance_data[1]['data']['objects']['valuesuffix']:
                valuesuffix = performance_data[0]['data']['objects']['valuesuffix']                
                self.result['data']['objects']['valuesuffix'] = valuesuffix
            else:
                valuesuffix = performance_data[0]['data']['objects']['valuesuffix'] + p_data[1]['data']['objects']['valuesuffix']
                self.result['data']['objects']['valuesuffix'] = valuesuffix

            if performance_data[0]['data']['objects']['valuetext'] == performance_data[1]['data']['objects']['valuetext']:
                valuetext = performance_data[0]['data']['objects']['valuetext']
                self.result['data']['objects']['valuesuffix'] = valuetext
            else:
                valuetext = performance_data[0]['data']['objects']['valuetext'] + performance_data[1]['data']['objects']['valuetext']
                self.result['data']['objects']['valuesuffix'] = valuetext

            
            self.result['data']['objects']['display_name'] = performance_data[0]['data']['objects']['display_name'] +' & '+ performance_data[1]['data']['objects']['display_name']

            
            self.result['data']['objects']['type'] = "area"
            self.result['success'] = 1      
            
            self.result['data']['objects']['plot_type'] = 'charts'
            self.result['message'] = 'Device Performance Data Fetched Successfully To Plot Graphs.'
            

        if not chart_data or len(chart_data) == 0:
            self.result['message'] = 'No Data'
        return self.result
  
    def get_performance_data_result(self, performance_data, data_source=None, is_historical_data=False):
        """

        :param performance_data:
        :param data_source:
        :param is_historical_data:
        :return:
        """
        is_dual_axis = False
        chart_data= list()
        if performance_data:
            ds_list = list(set(performance_data.values_list('data_source', flat=True)))
            counter = -1
            for ds in ds_list:
                # Variables used for HISTORICAL data
                data_list, warn_data_list, crit_data_list, aggregate_data = list(), list(), list(), dict()
                data_list_min, data_list_max, data_list_avg =  list(), list(), list()
                min_data_list = list()
                max_data_list = list()
                counter += 1

                ds_specific_data = performance_data.filter(data_source=ds)
                for data in ds_specific_data:
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
                                sds_name = str(data.service_name).strip().lower() + "_" + str(data.data_source).strip().lower()

                        sds_display_name = SERVICE_DATA_SOURCE[sds_name]["display_name"] \
                            if sds_name in SERVICE_DATA_SOURCE else str(data.data_source).upper()

                        if 'chart_display_name' not in self.result['data']['objects']:
                            self.result['data']['objects']['chart_display_name'] = ''

                        if sds_display_name not in self.result['data']['objects']['chart_display_name']:
                            if self.result['data']['objects']['chart_display_name']:
                                self.result['data']['objects']['chart_display_name'] += ' & ' + sds_display_name
                            else:
                                self.result['data']['objects']['chart_display_name'] += sds_display_name

                        self.result['data']['objects']['display_name'] = sds_display_name

                        display_name = sds_display_name

                        self.result['data']['objects']['type'] = SERVICE_DATA_SOURCE[sds_name]["type"] \
                            if sds_name in SERVICE_DATA_SOURCE else "area"
                        
                        if is_dual_axis:
                            
                            if 'valuesuffix' not in self.result['data']['objects']:
                                self.result['data']['objects']['valuesuffix'] = list()
                            if 'valuetext' not in self.result['data']['objects']:
                                self.result['data']['objects']['valuetext'] = list()

                            ds_suffix = SERVICE_DATA_SOURCE[sds_name]["valuesuffix"] if sds_name in SERVICE_DATA_SOURCE else ""
                            ds_txt = SERVICE_DATA_SOURCE[sds_name]["valuetext"] if sds_name in SERVICE_DATA_SOURCE else str(data.data_source).upper()
                            
                            if ds_suffix not in self.result['data']['objects']['valuesuffix']:
                                self.result['data']['objects']['valuesuffix'].append(ds_suffix)

                            if ds_txt not in self.result['data']['objects']['valuetext']:
                                self.result['data']['objects']['valuetext'].append(ds_txt)
                        else:
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
                                          if abs(p2) <= abs(p1) < abs(p3)
                                          else ('#FF193B' if abs(p3) <= abs(p1) else chart_color)
                                    )
                            else:
                                compare_point = lambda p1, p2, p3: chart_color \
                                    if abs(p1) > abs(p2) \
                                    else ('#FFE90D'
                                          if abs(p2) >= abs(p1) > abs(p3)
                                          else ('#FF193B' if abs(p3) >= abs(p1) else chart_color)
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
                    if is_dual_axis:
                        chart_data.append({
                            'name': self.result['data']['objects']['display_name'],
                            'data': data_list,
                            'yAxis' : counter,
                            'color' : data_list[0]['color'],
                            'type': self.result['data']['objects']['type'],
                            'valuesuffix': self.result['data']['objects']['valuesuffix'],
                            'valuetext': self.result['data']['objects']['valuetext'],
                            'is_inverted': self.result['data']['objects']['is_inverted']
                        })
                    else:
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
                        if is_dual_axis:
                            chart_data.append({
                                'name': str("min value").title() + '(' + str(display_name) + ')' if is_unified_view else str("min value").title(),
                                'color': '#01CC14',
                                'data': min_data_list,
                                'yAxis' : counter,
                                'type': 'line',
                                'marker': {
                                    'enabled': False
                                }
                            })
                        else:
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
                        if is_dual_axis:
                            chart_data.append({
                                'name': str("max value").title() + '(' + str(display_name) + ')' if is_unified_view else str("max value").title(),
                                'color': '#FF8716',
                                'yAxis' : counter,
                                'data': max_data_list,
                                'type': 'line',
                                'marker': {
                                    'enabled': False
                                }
                            })
                        else:
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
                        if is_dual_axis:
                            chart_data.append({
                                'name': str("warning threshold").title() + '(' + str(display_name) + ')' if is_unified_view else str("warning threshold").title(),
                                'color': WARN_COLOR,
                                'data': warn_data_list,
                                'yAxis' : counter,
                                'type': WARN_TYPE,
                                'marker': {
                                    'enabled': False
                                }
                            })
                        else:
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
                        if is_dual_axis:
                            chart_data.append({
                                'name': str("critical threshold").title() + '(' + str(display_name) + ')' if is_unified_view else str("critical threshold").title(),
                                'color': CRIT_COLOR,
                                'data': crit_data_list,
                                'yAxis' : counter,
                                'type': CRIT_TYPE,
                                'marker': {
                                    'enabled': False
                                }
                            })
                        else:
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

        ss_type = None
        try:
            ss_type = DeviceType.objects.get(id=ss_device_object.device_type).name
        except Exception as e:
            pass

        if technology and technology.name.lower() in ['wimax']:
            service_name = 'wimax_ss_vlan_invent'
            data_source = 'ss_vlan'
        elif technology and technology.name.lower() in ['pmp']:
            if ss_type.lower() == 'radwin5kss':
                service_name = 'rad5k_man_vlan_invent'
                data_source = 'ss_vlan'
            else:
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
                            sds_name = str(data.service_name).strip().lower() + "_" + str(data.data_source).strip().lower()

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
                                      if abs(p2) <= abs(p1) < abs(p3)
                                      else ('#FF193B' if abs(p3) <= abs(p1) else chart_color)
                                )
                        else:
                            compare_point = lambda p1, p2, p3: chart_color \
                                if abs(p1) > abs(p2) \
                                else ('#FFE90D'
                                      if abs(p2) >= abs(p1) > abs(p3)
                                      else ('#FF193B' if abs(p3) >= abs(p1) else chart_color)
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

class CustomDashboardPerformanceListing(BaseDatatableView,AdvanceFilteringMixin):
    """
    A generic class based view for the single device page CustomDashboardPerformanceListing rendering.

    """
    model = PerformanceService

    columns = [
        'sys_timestamp',
        'current_value',
        'severity',
        'warning_threshold',
        'critical_threshold',
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

    custom_data_instance = ''

    parameters = []

    inventory_device_machine_name = ""

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        # If params not initialized the init them by calling initialize_params
        if not self.custom_data_instance or not self.parameters:            
            self.initialize_params()

            
        if self.parameters:
            updated_resultset = list()                 
            for paramerters in self.parameters:
                resultset = self.custom_data_instance.get_performance_data(
                    **paramerters
                ).using(alias=self.inventory_device_machine_name)                
                required_result = resultset.values(*self.columns).order_by('-sys_timestamp')
                
                if required_result:
                    updated_resultset.append(required_result)             
                    
        # Merge all querysets present in 'updated_resultset' list
        if updated_resultset:
            combined_queryset = MultiQuerySet(*updated_resultset)
            return combined_queryset
        else:
            return required_result


    def initialize_params(self):
        """
        This function initializes public variables of this class
        """

        # REQUIRED GET PARAMS
        device_id = self.kwargs['device_id']
        custom_dashboard_id = self.kwargs['custom_dashboard_id']        
        data_for = self.request.GET.get('data_for', 'live')
        
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        
        date_format = DATE_TIME_FORMAT
        device = Device.objects.get(id=int(device_id))
        inventory_device_name = device.device_name
       
        # data sources and service names of the data sources  
        custom_data_source_names = DSCustomDashboard.objects.filter(custom_dashboard_id = custom_dashboard_id ).values('data_source__name', 'service__name')      
        
        display_type = CustomDashboard.objects.filter(id = custom_dashboard_id ).values_list('display_type',flat=True)
        # to check if data source would be displayed as a chart or as a table   
        
        # Create instance of "CustomPerformanceDashboard" class
        self.custom_data_instance = CustomDashboardPerformanceData()       
        self.parameters =[]      
        for ds_obj in custom_data_source_names:
            data_source_type = ds_obj.get('data_source__name')
            service_name = ds_obj.get('service__name')                 
            
            service_view_type = display_type            
            service = str(service_name)
            self.service=service
            self.data_source = data_source_type                       
                                                      
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
                
            if service_view_type:
                self.columns = [
                    'sys_timestamp',
                    'data_source',
                    'current_value',
                    'severity',
                    'warning_threshold',
                    'critical_threshold',
                    'service_name',
                    'min_value',
                    'max_value',
                    'avg_value',
                    'ip_address'
                ]

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

            params = {
                'model': PerformanceService,
                'start_time': start_date,
                'end_time': end_date,
                'devices': [inventory_device_name],
                'services': [service_name],
                'sds': [data_source_type]
            }
            params_copy=params.copy()  

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

           

            if (service == 'ping' or data_source_type in ['pl', 'rta']) and data_source_type not in ['rf']:
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
                params_copy.update(
                    model=self.model,
                    start_time=start_date,
                    end_time=end_date,
                    services=[service_name],
                    devices=[inventory_device_name],
                    sds=[data_source_type]
                )if params['model'] != "" else ""        

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
                params_copy.update(
                    model=self.model,
                    start_time=start_date,
                    end_time=end_date,
                    services=[service_name],
                    devices=[inventory_device_name],
                    sds=[data_source_type]
                )if params['model'] != "" else ""

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

                params_copy.update(
                    model=self.model,
                    start_time=start_date,
                    end_time=end_date,
                    services=[service_name],
                    devices=[inventory_device_name],
                    sds=[data_source_type]
                )if params['model'] != "" else ""
                
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
                
                params_copy.update(
                    model=self.model,
                    start_time=start_date,
                    end_time=end_date,
                    services=[service_name],
                    devices=[inventory_device_name],
                    sds=[data_source_type]
                )if params['model'] != "" else ""

                # self.parameters.append(params_copy)
            else:
                params = {
                'model': PerformanceService,
                'start_time': start_date,
                'end_time': end_date,
                'devices': [inventory_device_name],
                'services': [service_name],
                'sds': [data_source_type]
            }                     
                
            self.parameters.append(params_copy)
        
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

            display_name = item['data_source']

            # Prepare sds key to fetch actual display name for DS
            if item['data_source'] in ['pl', 'rta', 'availability']:
                sds_key = item['data_source']
            else:
                sds_key = str(item['service_name']) + '_' + str(item['data_source'])
            try:
                if SERVICE_DATA_SOURCE.get(sds_key):
                    display_name = SERVICE_DATA_SOURCE.get(sds_key).get('display_name')
            except Exception, e:
                display_name = item['data_source']

            item.update(
                data_source=display_name,
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
       
        sSearch = self.request.GET.get('search[value]', None)
        updated_resultset = list()

        if sSearch:
            try:
                for params in self.parameters:
                    main_resultset = self.custom_data_instance.get_performance_data(
                    **params
                    ).using(alias=self.inventory_device_machine_name)                  

                    qs = main_resultset.filter(
                        Q(data_source__icontains=sSearch)
                        |
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

                    updated_resultset.append(qs)
                # Merge all querysets present in 'updated_resultset' list
                qs = MultiQuerySet(*updated_resultset)
            except Exception, e:
                pass
        return qs

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
        if not self.custom_data_instance or not self.parameters:
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
            polled_freq_obj,
            {
                "name": "polled_sector_id",
                "title": "Sector ID",
                "value": "NA",
                "url": ""
            }
        ]

    elif type_of_device in ['backhaul', 'other']:
        if page_type == 'pe':
            bs_name_obj = {
                "name": "pe_hostname",
                "title": "PE Hostname",
                "value": "NA",
                "url": "",
                "app_name": inventory_app,
                "url_name": "backhaul_edit",
                "kwargs_name": 'pk',
                'pk_key' : 'bh_id'
            }
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
            severity[data['severity']] = {'age': data['age'], 'down': data['refer'], 'c_val' : data['current_value']}
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

@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_PERFORMANCE', 300))  # just for 2 minutes cache this. short running query
def device_pl_latency_values(device_object):
    """
    Device pl_latency Status
    :param device_object:
    """

    required_fields = ['data_source', 'current_value']

    inventory_device_name = device_object.device_name
    inventory_device_machine_name = device_object.machine.name

    device_nms_uptime_query_set = NetworkStatus.objects.filter(
        device_name=inventory_device_name,
        service_name='ping',
        data_source__in=['rta', 'pl']# ['pl', 'rta']
    ).using(alias=inventory_device_machine_name).values(*required_fields)

    device_nms_uptime = device_nms_uptime_query_set

    if device_nms_uptime:
        for data in device_nms_uptime:
            if data['data_source'].strip().lower() == 'pl':
                pl_value = data['current_value']

            if data['data_source'].strip().lower() == 'rta': 
                latency = data['current_value']
        return pl_value, latency
    else:
        return None, None
    



@nocout_utils.cache_for(CACHE_TIME.get('DEFAULT_PERFORMANCE', 300))  #for 5 minutes cache this. long running query
def device_last_down_time(device_object):
    """

    :param device_object:
    :return:
    """
    #first check the current PL state of the device
    s, a = device_current_status(device_object=device_object)
    return a['down']  # return the last down time of the device


class GetSeverityWiseStatus(View):
    """
    This class fetch & return service - ds values as per given severities
    """
    def get(self, request, *args, **kwargs):
        result = {
            'success': 0,
            'message': 'No data fetched',
            'data' : []
        }
        severity = request.GET.get('severity')
        device_id = request.GET.get('device_id')
        view_type = request.GET.get('view_type')

        if not severity or not device_id:
            return HttpResponse(json.dumps(result), content_type="application/json") 

        try:
            device = Device.objects.select_related('machine').get(id=int(device_id))
        except Exception, e:
            result.update(
                message='Invalid Device ID'
            )
            return HttpResponse(json.dumps(result), content_type="application/json") 

        machine_name = device.machine.name
        device_name = device.device_name
        severity_check = ['unknown']
        columns = [
            'sys_timestamp',
            'data_source',
            'service_name',
            'current_value',
            'severity',
            'warning_threshold',
            'critical_threshold'
        ]

        if severity == 'ok':
            severity_check = ['ok', 'up']

        if severity == 'warning':
            severity_check = ['warning', 'warn']

        if severity == 'critical':
            severity_check = ['critical', 'crit', 'down']

        invent_data = InventoryStatus.objects.filter(
            device_name=device_name,
            severity__in=severity_check
        ).values(*columns).order_by('service_name').using(alias=machine_name)

        status_data = Status.objects.filter(
            device_name=device_name,
            severity__in=severity_check
        ).values(*columns).order_by('service_name').using(alias=machine_name)

        service_data = ServiceStatus.objects.filter(
            device_name=device_name,
            severity__in=severity_check
        ).values(*columns).order_by('service_name').using(alias=machine_name)

        all_dataset = list(invent_data) + list(status_data) + list(service_data)

        # Format resultset as per the requirement
        for data in all_dataset:
            service_name = data.get('service_name')
            data_source = data.get('data_source')
            srv_ds_info = SERVICE_DATA_SOURCE.get(service_name + '_' + data_source)
            display_name = srv_ds_info.get('display_name') if srv_ds_info and srv_ds_info.get('display_name') else data_source
            service_alias = srv_ds_info.get('service_alias') if srv_ds_info and srv_ds_info.get('service_alias') else service_name
            datetime_obj = datetime.datetime.fromtimestamp(data.get('sys_timestamp'))

            data.update(
                service_name=display_name,
                data_source=service_alias,
                sys_timestamp=datetime_obj.strftime(DATE_TIME_FORMAT)
            )
        
        result.update(
            success=1,
            message='Data fetched successfully.',
            data=all_dataset
        )
        
        return HttpResponse(json.dumps(result), content_type="application/json")


class GetTopology(View):
    """
    The Class based View to get topology for the single device.

    """
    def get(self, request):
        result = {
            'success': 0,
            'message': 'Device Topology Details Not Fetched Successfully.',
            'data': list()
        }

        bs_id = self.request.GET.get('bs_id')
        page_type = self.request.GET.get('page_type').lower()
        current_device_id = self.request.GET.get('device_id')
        device_technology = self.request.GET.get('device_tech')
        have_ptp_bh = False
        limit_till_bs = False


        try:
            bs_id = json.loads(str(bs_id))
        except Exception, e:
            bs_id = []

        if not bs_id:
            return HttpResponse(json.dumps(result), content_type="application/json")

        multiple_bs = False

        try:
            device = Device.objects.get(id=current_device_id)
        except Exception, e:
            return HttpResponse(json.dumps(result), content_type="application/json")

        try:
            device_type = DeviceType.objects.get(id=device.device_type)
        except Exception, e:
            return HttpResponse(json.dumps(result), content_type="application/json")

        if len(bs_id) > 1:
            multiple_bs = True
        
        # Query for getting topology info of selected device 
        if page_type == 'network':

            bs_alias_qs = BaseStation.objects.filter(id=bs_id[0]).values('alias')
            bs_alias = str(bs_alias_qs[0]['alias']).lower()

            if device_technology.lower() == 'p2p' :
                queryset = list(Circuit.objects.filter(circuit_id__icontains = '#'+ bs_alias).values())
                limit_till_bs = True    
            else :
                queryset = list(Circuit.objects.filter(circuit_id__icontains = bs_alias + '#').values())
            
            if len(queryset):
                have_ptp_bh = True

                circuit_id = queryset[0]['circuit_id']
                # spliiting current circuit in case of having PTP-BH, because there we have Far-end and Near-End
                splitted_circuit_id_list = circuit_id.split('#')
                

                if len(splitted_circuit_id_list) > 1:
                    far_end_bs = str(splitted_circuit_id_list[0]).lower()
                    near_end_bs = str(splitted_circuit_id_list[1]).lower()

                    far_bs_queryset = list(BaseStation.objects.filter(alias__iexact = far_end_bs).values('id'))
                    far_end_bs_id = 0
                    if len(far_bs_queryset):
                        far_end_bs_id = far_bs_queryset[0]['id']

                    near_bs_queryset = list(BaseStation.objects.filter(alias__iexact = near_end_bs).values('id'))
                    near_end_bs_id = 0
                    if len(near_bs_queryset):
                        near_end_bs_id = near_bs_queryset[0]['id']

            
            if str(device_type).lower() == 'radwin2kss':
                if have_ptp_bh:
                    if device_technology.lower() == 'p2p':
                        query_filter_condition1 = 'ss_device.id'    
                    else :
                        query_filter_condition1 = 'far_end_ss_device.id'
                    
                    query_filter_condition2 = 'far_end_sect_sector_id'
                else:    
                    # in case of radwin2kss we have to filter according to substation device
                    query_filter_condition1 = 'ss_device.id'
                    query_filter_condition2 = 'sect_sector_id'
            else :
                if have_ptp_bh:
                    if device_technology.lower() == 'p2p':
                        query_filter_condition1 = 'sect_device.id'    
                    else :
                        query_filter_condition1 = 'far_end_sect_device.id'
                    
                    query_filter_condition2 = 'far_end_sect_sector_id'
                else:
                    query_filter_condition1 = 'sect_device.id'
                    query_filter_condition2 = 'sect_sector_id'
            

            if have_ptp_bh:

                topology_query = '''
                    SELECT
                        IF(isnull(bs.id), 'NA', bs.id) AS bs_id,
                        IF(isnull(bs.name), 'NA', bs.name) AS bs_name,
                        IF(isnull(bs.alias), 'NA', bs.alias) AS bs_alias,
                        IF(isnull(bs_switch.id), 'NA', bs_switch.id) AS bs_switch_id, 
                        IF(isnull(far_end_bs.id), 'NA', far_end_bs.id) AS far_end_bs_id,
                        IF(isnull(far_end_device.ip_address), 'NA', far_end_device.ip_address) AS far_end_ip,
                        IF(isnull(far_end_device.id), 'NA', far_end_device.id) AS far_end_id,
                        IF(isnull(near_end_device.ip_address), 'NA', near_end_device.ip_address) AS near_end_ip,
                        IF(isnull(near_end_device.id), 'NA', near_end_device.id) AS near_end_id,
                        IF(isnull(far_end_bs.name), 'NA', far_end_bs.name) AS far_end_bs_name,
                        IF(isnull(far_end_bs.alias), 'NA', far_end_bs.alias) AS far_end_bs_alias,
                        IF(isnull(far_end_bs_switch.id), 'NA', far_end_bs_switch.id) AS far_end_bs_switch_id, 
                        IF(isnull(far_end_bs_switch.ip_address), 'NA', far_end_bs_switch.ip_address) AS far_end_bs_switch_ip,
                        IF(isnull(backhaul.bh_switch_id), 'NA', backhaul.bh_switch_id) AS bs_convertor_id,
                        IF(isnull(backhaul.aggregator_id), 'NA', backhaul.aggregator_id) AS bh_aggregator_id,
                        IF(isnull(backhaul.pop_id), 'NA', backhaul.pop_id) AS bh_pop_id,
                        IF(isnull(bs_switch.ip_address), 'NA', bs_switch.ip_address) AS bs_switch_ip,
                        IF(isnull(bs.backhaul_id), 'NA', bs.backhaul_id) AS bh_id,
                        IF(isnull(backhaul.pe_hostname), 'NA', backhaul.pe_hostname) AS pe_hostname,
                        IF(isnull(bh_pe_device.ip_address), 'NA', bh_pe_device.ip_address) AS pe_ip,
                        IF(isnull(backhaul.bh_configured_on_id), 'NA', backhaul.bh_configured_on_id) AS bh_device_id,
                        IF(isnull(bs_convertor_device.ip_address), 'NA', bs_convertor_device.ip_address) AS bs_convertor_ip,
                        IF(isnull(bh_pop_device.ip_address), 'NA', bh_pop_device.ip_address) AS bh_pop_ip,
                        IF(isnull(bh_aggregator_device.ip_address), 'NA', bh_aggregator_device.ip_address) AS bh_aggregator_ip,
                        IF(isnull(backhaul.aggregator_port_name), 'NA', backhaul.aggregator_port_name) AS bh_aggregator_port,
                        IF(isnull(bh_device_type.name), 'NA', bh_device_type.name) AS bh_device_type,
                        IF(isnull(bh_device_tech.name), 'NA', bh_device_tech.name) AS bh_device_tech,   
                        IF(isnull(bh_device.ip_address), 'NA', bh_device.ip_address) AS bh_ip,
                        IF(isnull(sect.id), 'NA', sect.id) AS sect_id,
                        IF(isnull(far_end_sect.id), 'NA', far_end_sect.id) AS far_end_sect_id,
                        IF(isnull(sect.sector_id), 'NA', sect.sector_id) AS sect_sector_id,
                        IF(isnull(far_end_sect.sector_id), 'NA', far_end_sect.sector_id) AS far_end_sect_sector_id,
                        IF(isnull(sect.sector_configured_on_id), 'NA', sect.sector_configured_on_id) AS sect_device_id,
                        IF(isnull(far_end_sect.sector_configured_on_id), 'NA', far_end_sect.sector_configured_on_id) AS far_end_sect_device_id,
                        IF(isnull(device.device_name), 'NA', device.device_name) AS sect_device_name,
                        IF(isnull(far_end_sect_device.device_name), 'NA', far_end_sect_device.device_name) AS far_end_sect_device_name,
                        IF(isnull(sect_device_tech.name), 'NA', sect_device_tech.name) AS sect_device_tech,
                        IF(isnull(sect_device_type.name), 'NA', sect_device_type.name) AS sect_device_type,
                        IF(isnull(device.ip_address), 'NA', device.ip_address) AS sect_device_ip,
                        IF(not isnull(sect.sector_id), sect.sector_id, device.ip_address) AS sect_ip_id_title,
                        IF(isnull(far_end_sect_device_tech.name), 'NA', far_end_sect_device_tech.name) AS far_end_sect_device_tech,
                        IF(isnull(far_end_sector_port.alias), 'NA', far_end_sector_port.alias) AS far_end_sect_port,
                        IF(isnull(far_end_bs.bh_port_name), 'NA', far_end_bs.bh_port_name) AS far_end_bs_switch_port ,
                        IF(isnull(far_end_sect_device_type.name), 'NA', far_end_sect_device_type.name) AS far_end_sect_device_type,
                        IF(isnull(far_end_sect_device.ip_address), 'NA', far_end_sect_device.ip_address) AS far_end_sect_device_ip,
                        IF(far_end_sect_device_tech.name = 'WiMAX', CONCAT(far_end_sect_device.ip_address, ' - ', far_end_sect.sector_id), far_end_sect_device.ip_address) AS far_end_sect_ip_id_title,
                        'NA' AS far_end_ss_circuit_id,
                        'NA' AS far_end_ss_id,
                        'NA' AS far_end_ss_device_id,
                        'NA' AS far_end_ss_device_tech,
                        'NA' AS far_end_ss_device_type,
                        'NA' AS far_end_ss_device_name,
                        'NA' AS far_end_ss_device_ip,
                        IF(isnull(bh_pe_device.device_name), 'NA', bh_pe_device.device_name) AS pe_name,
                        IF(isnull(bs_switch.device_name), 'NA', bs_switch.device_name) AS bs_switch_name,
                        IF(isnull(bs_convertor_device.device_name), 'NA', bs_convertor_device.device_name) AS bs_convertor_device_name,
                        IF(isnull(bh_aggregator_device.device_name), 'NA', bh_aggregator_device.device_name) AS bh_aggregator_device_name,
                        IF(isnull(bh_pop_device.device_name), 'NA', bh_pop_device.device_name) AS bh_pop_device_name,
                        IF(isnull(bh_device.device_name), 'NA', bh_device.device_name) AS bh_device_name,
                        IF(isnull(far_end_bs_switch.device_name), 'NA', far_end_bs_switch.device_name) AS far_end_bs_switch_name,
                        IF(isnull(near_end_device.device_name), 'NA', near_end_device.device_name) AS near_end_device_name,
                        IF(isnull(far_end_device.device_name), 'NA', far_end_device.device_name) AS far_end_device_name,
                        IF(isnull(far_end_sect_device.device_name), 'NA', far_end_sect_device.device_name) AS far_end_sect_device_name,
                        sect_device_type.device_icon as sect_icon,
                        bh_device_type.device_icon as bh_icon,
                        sect_freq.color_hex_value as sect_color,
                        IF((backhaul.bh_configured_on_id = backhaul.bh_switch_id), backhaul.bh_port_name,'NA') AS bs_convertor_port,
                        IF((backhaul.bh_configured_on_id = bs.bs_switch_id), backhaul.bh_port_name,'NA') AS bs_switch_port,
                        IF((backhaul.bh_configured_on_id = backhaul.pop_id), backhaul.bh_port_name,'NA') AS bh_pop_port

                    FROM
                        inventory_basestation AS bs
                    LEFT JOIN
                        device_device AS bs_switch
                    ON
                        bs.bs_switch_id = bs_switch.id
                    LEFT JOIN
                        inventory_backhaul AS backhaul
                    ON
                        bs.backhaul_id = backhaul.id
                    LEFT JOIN
                        device_device AS bh_pe_device
                    ON
                        backhaul.pe_ip_id = bh_pe_device.id
                    LEFT JOIN
                        device_device AS bs_convertor_device
                    ON
                        backhaul.bh_switch_id = bs_convertor_device.id
                    LEFT JOIN
                        device_device AS bh_aggregator_device
                    ON
                        backhaul.aggregator_id = bh_aggregator_device.id
                    LEFT JOIN
                        device_device AS bh_pop_device
                    ON
                        backhaul.pop_id = bh_pop_device.id
                    LEFT JOIN
                        device_device AS bh_device
                    ON
                        backhaul.bh_configured_on_id = bh_device.id
                    LEFT JOIN 
                        device_devicetechnology AS bh_device_tech
                    ON
                        bh_device.device_technology = bh_device_tech.id
                    LEFT JOIN
                        inventory_sector AS sect
                    ON
                        bs.id = sect.base_station_id
                    LEFT JOIN
                        device_device AS device
                    ON
                        sect.sector_configured_on_id = device.id
                    LEFT JOIN 
                        device_devicetechnology AS sect_device_tech
                    ON
                        device.device_technology = sect_device_tech.id
                    LEFT JOIN
                        device_device as sect_device
                    ON
                        sect.sector_configured_on_id = sect_device.id
                    LEFT JOIN
                        inventory_circuit AS ckt
                    ON
                        sect.id = ckt.sector_id
                    LEFT JOIN
                        device_devicetype as sect_device_type
                    ON
                        sect_device_type.id = device.device_type
                    LEFT JOIN
                        device_devicetype as bh_device_type
                    ON
                        bh_device_type.id = bh_device.device_type
                    LEFT JOIN
                        device_devicefrequency as sect_freq
                    ON
                        sect_freq.id = sect.frequency_id
                    LEFT join
                        inventory_substation as ss
                    ON
                        ckt.sub_station_id = ss.id
                    LEFT JOIN
                        device_device AS ss_device
                    ON
                        ss.device_id = ss_device.id
                    LEFT JOIN
                        inventory_basestation as far_end_bs
                    ON
                        far_end_bs.id = {0}
                    LEFT JOIN
                        inventory_backhaul as far_end_backhaul
                    ON
                        far_end_bs.backhaul_id = far_end_backhaul.id
                    LEFT JOIN
                        device_device as far_end_bs_switch
                    ON
                        far_end_bs_switch.id = far_end_backhaul.bh_configured_on_id
                    LEFT JOIN
                        inventory_circuit as far_near_circuit
                    ON 
                        far_near_circuit.circuit_id = '{1}'
                    LEFT JOIN
                        inventory_sector as near_end
                    ON
                        near_end.id = far_near_circuit.sector_id
                    LEFT JOIN
                        device_device as near_end_device
                    ON
                        near_end.sector_configured_on_id = near_end_device.id
                    LEFT JOIN
                        inventory_substation as far_end
                    ON
                        far_end.id = far_near_circuit.sub_station_id
                    LEFT JOIN
                        device_device as far_end_device
                    ON
                        far_end.device_id = far_end_device.id
                    LEFT JOIN
                        inventory_sector AS far_end_sect
                    ON
                        far_end_bs.id = far_end_sect.base_station_id
                    LEFT JOIN
                        device_deviceport AS far_end_sector_port
                    ON
                        far_end_sect.sector_configured_on_port_id = far_end_sector_port.id
                    LEFT JOIN
                        device_device as far_end_sect_device
                    ON
                        far_end_sect.sector_configured_on_id = far_end_sect_device.id
                    LEFT JOIN 
                        device_devicetechnology AS far_end_sect_device_tech
                    ON
                        far_end_sect_device.device_technology = far_end_sect_device_tech.id
                    LEFT JOIN
                        inventory_circuit AS far_end_ckt
                    ON
                        far_end_sect.id = far_end_ckt.sector_id
                    LEFT JOIN
                        device_devicetype as far_end_sect_device_type
                    ON
                        far_end_sect_device_type.id = far_end_sect_device.device_type
                    LEFT JOIN
                        device_devicefrequency as far_end_sect_freq
                    ON
                        far_end_sect_freq.id = far_end_sect.frequency_id
                    LEFT join
                        inventory_substation as far_end_ss
                    ON
                        far_end_ckt.sub_station_id = far_end_ss.id
                    LEFT JOIN
                        device_device AS far_end_ss_device
                    ON
                        far_end_ss.device_id = far_end_ss_device.id
                    LEFT JOIN
                        device_device as current_device
                    ON
                        current_device.id = {4}
                    where
                        current_device.is_added_to_nms > 0
                        AND
                        bs.id = {2}
                        AND
                        {3} = {4}
                    GROUP by({5})
            '''.format(far_end_bs_id, circuit_id, near_end_bs_id, query_filter_condition1 , current_device_id, query_filter_condition2)                

            else:
                topology_query = ''' 
                    SELECT
                        IF(isnull(bs.id), 'NA', bs.id) AS bs_id,
                        IF(isnull(bs.name), 'NA', bs.name) AS bs_name,
                        IF(isnull(bs.alias), 'NA', bs.alias) AS bs_alias,
                        IF(isnull(bs_switch.id), 'NA', bs_switch.id) AS bs_switch_id, 
                        IF(isnull(backhaul.bh_switch_id), 'NA', backhaul.bh_switch_id) AS bs_convertor_id,
                        IF(isnull(backhaul.aggregator_id), 'NA', backhaul.aggregator_id) AS bh_aggregator_id,
                        IF(isnull(backhaul.pop_id), 'NA', backhaul.pop_id) AS bh_pop_id,
                        IF(isnull(bs_switch.ip_address), 'NA', bs_switch.ip_address) AS bs_switch_ip,
                        IF(isnull(bs.backhaul_id), 'NA', bs.backhaul_id) AS bh_id,
                        IF(isnull(backhaul.pe_hostname), 'NA', backhaul.pe_hostname) AS pe_hostname,
                        IF(isnull(bh_pe_device.id), 'NA', bh_pe_device.id) AS pe_id,
                        IF(isnull(bh_pe_device.ip_address), 'NA', bh_pe_device.ip_address) AS pe_ip,
                        IF(isnull(bs_convertor_device.ip_address), 'NA', bs_convertor_device.ip_address) AS bs_convertor_ip,
                        IF(isnull(bh_pop_device.ip_address), 'NA', bh_pop_device.ip_address) AS bh_pop_ip,
                        IF(isnull(bh_aggregator_device.ip_address), 'NA', bh_aggregator_device.ip_address) AS bh_aggregator_ip,
                        IF(isnull(backhaul.aggregator_port_name), 'NA', backhaul.aggregator_port_name) AS bh_aggregator_port,
                        IF(isnull(backhaul.bh_configured_on_id), 'NA', backhaul.bh_configured_on_id) AS bh_device_id,
                        IF(isnull(bh_device_type.name), 'NA', bh_device_type.name) AS bh_device_type,
                        IF(isnull(bh_device_tech.name), 'NA', bh_device_tech.name) AS bh_device_tech,   
                        IF(isnull(bh_device.ip_address), 'NA', bh_device.ip_address) AS bh_ip,
                        IF(isnull(sect.id), 'NA', sect.id) AS sect_id,
                        IF(isnull(sect.sector_id), 'NA', sect.sector_id) AS sect_sector_id,
                        IF(isnull(sect.sector_configured_on_id), 'NA', sect.sector_configured_on_id) AS sect_device_id,
                        IF(isnull(device.device_name), 'NA', device.device_name) AS sect_device_name,
                        IF(isnull(sect_device_tech.name), 'NA', sect_device_tech.name) AS sect_device_tech,
                        IF(isnull(sect_device_type.name), 'NA', sect_device_type.name) AS sect_device_type,
                        IF(isnull(device.ip_address), 'NA', device.ip_address) AS sect_device_ip,
                        IF(not isnull(sect.sector_id), sect.sector_id, device.ip_address) AS sect_ip_id_title,
                        'NA' AS ss_circuit_id,
                        'NA' AS ss_id,
                        'NA' AS ss_device_id,
                        'NA' AS ss_device_tech,
                        'NA' AS ss_device_type,
                        'NA' AS ss_device_name,
                        'NA' AS ss_device_ip,
                        IF(isnull(bh_pe_device.device_name), 'NA', bh_pe_device.device_name) AS pe_name,
                        IF(isnull(bs_switch.device_name), 'NA', bs_switch.device_name) AS bs_switch_name,
                        IF(isnull(bs_convertor_device.device_name), 'NA', bs_convertor_device.device_name) AS bs_convertor_device_name,
                        IF(isnull(bh_aggregator_device.device_name), 'NA', bh_aggregator_device.device_name) AS bh_aggregator_device_name,
                        IF(isnull(bh_pop_device.device_name), 'NA', bh_pop_device.device_name) AS bh_pop_device_name,
                        IF(isnull(bh_device.device_name), 'NA', bh_device.device_name) AS bh_device_name,
                        sect_device_type.device_icon as sect_icon,
                        bh_device_type.device_icon as bh_icon,
                        sect_freq.color_hex_value as sect_color,
                        IF((backhaul.bh_configured_on_id = backhaul.bh_switch_id), backhaul.bh_port_name,'NA') AS bs_convertor_port,
                        IF((backhaul.bh_configured_on_id = bs.bs_switch_id), backhaul.bh_port_name,'NA') AS bs_switch_port,
                        IF((backhaul.bh_configured_on_id = backhaul.pop_id), backhaul.bh_port_name,'NA') AS bh_pop_port

                    FROM
                        inventory_basestation AS bs
                    LEFT JOIN
                        device_device AS bs_switch
                    ON
                        bs.bs_switch_id = bs_switch.id
                    LEFT JOIN
                        inventory_backhaul AS backhaul
                    ON
                        bs.backhaul_id = backhaul.id
                    LEFT JOIN
                        device_device AS bh_pe_device
                    ON
                        backhaul.pe_ip_id = bh_pe_device.id
                    LEFT JOIN
                        device_device AS bs_convertor_device
                    ON
                        backhaul.bh_switch_id = bs_convertor_device.id
                    LEFT JOIN
                        device_device AS bh_aggregator_device
                    ON
                        backhaul.aggregator_id = bh_aggregator_device.id
                    LEFT JOIN
                        device_device AS bh_pop_device
                    ON
                        backhaul.pop_id = bh_pop_device.id
                    LEFT JOIN
                        device_device AS bh_device
                    ON
                        backhaul.bh_configured_on_id = bh_device.id
                    LEFT JOIN 
                        device_devicetechnology AS bh_device_tech
                    ON
                        bh_device.device_technology = bh_device_tech.id
                    LEFT JOIN
                        inventory_sector AS sect
                    ON
                        bs.id = sect.base_station_id
                    LEFT JOIN
                        device_device AS device
                    ON
                        sect.sector_configured_on_id = device.id
                    LEFT JOIN 
                        device_devicetechnology AS sect_device_tech
                    ON
                        device.device_technology = sect_device_tech.id
                    LEFT JOIN
                        device_device as sect_device
                    ON
                        sect.sector_configured_on_id = sect_device.id
                    LEFT JOIN
                        inventory_circuit AS ckt
                    ON
                        sect.id = ckt.sector_id
                    LEFT JOIN
                        device_devicetype as sect_device_type
                    ON
                        sect_device_type.id = device.device_type
                    LEFT JOIN
                        device_devicetype as bh_device_type
                    ON
                        bh_device_type.id = bh_device.device_type
                    LEFT JOIN
                        device_devicefrequency as sect_freq
                    ON
                        sect_freq.id = sect.frequency_id
                    LEFT join
                        inventory_substation as ss
                    ON
                        ckt.sub_station_id = ss.id
                    LEFT JOIN
                        device_device AS ss_device
                    ON
                        ss.device_id = ss_device.id
                    LEFT JOIN
                        device_device as current_device
                    ON
                        current_device.id = {2}
                    where
                        current_device.is_added_to_nms > 0
                        AND
                        bs.id in ({0})
                        AND
                        {1} = {2}
                    GROUP by(sect_sector_id)
                '''.format(', '.join(bs_id), query_filter_condition1 , current_device_id)

        
        elif page_type == 'customer':
            current_sector_device_id = 0
            if 'SS' in device_type.name:
                queryset = list(Circuit.objects.filter(sub_station__device=device).values('sector__sector_configured_on__id'))
                if len(queryset):
                    current_sector_device_id = queryset[0]['sector__sector_configured_on__id']
            else:
                current_sector_device_id = current_device_id

            topology_query = ''' 
                SELECT
                    IF(isnull(bs.id), 'NA', bs.id) AS bs_id,
                    IF(isnull(bs.name), 'NA', bs.name) AS bs_name,
                    IF(isnull(bs.alias), 'NA', bs.alias) AS bs_alias,
                    IF(isnull(bs_switch.id), 'NA', bs_switch.id) AS bs_switch_id, 
                    IF(isnull(backhaul.bh_switch_id), 'NA', backhaul.bh_switch_id) AS bs_convertor_id,
                    IF(isnull(backhaul.aggregator_id), 'NA', backhaul.aggregator_id) AS bh_aggregator_id,
                    IF(isnull(backhaul.pop_id), 'NA', backhaul.pop_id) AS bh_pop_id,
                    IF(isnull(bs_switch.ip_address), 'NA', bs_switch.ip_address) AS bs_switch_ip,
                    IF(isnull(bs.backhaul_id), 'NA', bs.backhaul_id) AS bh_id,
                    IF(isnull(backhaul.pe_hostname), 'NA', backhaul.pe_hostname) AS pe_hostname,
                    IF(isnull(bh_pe_device.id), 'NA', bh_pe_device.id) AS pe_id,
                    IF(isnull(bh_pe_device.ip_address), 'NA', bh_pe_device.ip_address) AS pe_ip,
                    IF(isnull(backhaul.bh_configured_on_id), 'NA', backhaul.bh_configured_on_id) AS bh_device_id,
                    IF(isnull(bs_convertor_device.ip_address), 'NA', bs_convertor_device.ip_address) AS bs_convertor_ip,
                    -- IF(isnull(switch_port_name), 'NA', switch_port_name) AS bs_convertor_port,
                    IF(isnull(bh_pop_device.ip_address), 'NA', bh_pop_device.ip_address) AS bh_pop_ip,
                    IF(isnull(backhaul.pop_port_name), 'NA', backhaul.pop_port_name) AS bh_pop_port,
                    IF(isnull(bh_aggregator_device.ip_address), 'NA', bh_aggregator_device.ip_address) AS bh_aggregator_ip,
                    IF(isnull(backhaul.aggregator_port_name), 'NA', backhaul.aggregator_port_name) AS bh_aggregator_port,
                    IF(isnull(bh_device_type.name), 'NA', bh_device_type.name) AS bh_device_type,
                    IF(isnull(bh_device_tech.name), 'NA', bh_device_tech.name) AS bh_device_tech,   
                    IF(isnull(bh_device.ip_address), 'NA', bh_device.ip_address) AS bh_ip,
                    IF(isnull(sect.id), 'NA', sect.id) AS sect_id,
                    IF(isnull(sect.sector_id), 'NA', sect.sector_id) AS sect_sector_id,
                    IF(isnull(sect.sector_configured_on_id), 'NA', sect.sector_configured_on_id) AS sect_device_id,
                    IF(isnull(device.device_name), 'NA', device.device_name) AS sect_device_name,
                    IF(isnull(sect_device_tech.name), 'NA', sect_device_tech.name) AS sect_device_tech,
                    IF(isnull(sector_port.alias), 'NA', sector_port.alias) AS sect_port,
                    IF(isnull(sect_device_type.name), 'NA', sect_device_type.name) AS sect_device_type,
                    IF(isnull(device.ip_address), 'NA', device.ip_address) AS sect_device_ip,
                    IF(not isnull(sect.sector_id), sect.sector_id, device.ip_address) AS sect_ip_id_title,
                    IF(isnull(ckt.circuit_id), 'NA', ckt.circuit_id) AS ss_circuit_id,
                    IF(isnull(ckt.sub_station_id), 'NA', ckt.sub_station_id) AS ss_id,
                    IF(isnull(ss.device_id), 'NA', ss.device_id) AS ss_device_id,
                    IF(isnull(ss_device_tech.name), 'NA', ss_device_tech.name) AS ss_device_tech,
                    IF(isnull(ss_device_type.name), 'NA', ss_device_type.name) AS ss_device_type,
                    IF(isnull(ss_device.device_name), 'NA', ss_device.device_name) AS ss_device_name,
                    IF(isnull(ss_device.ip_address), 'NA', ss_device.ip_address) AS ss_device_ip,
                    IF(isnull(bh_pe_device.device_name), 'NA', bh_pe_device.device_name) AS pe_name,
                    IF(isnull(bs_switch.device_name), 'NA', bs_switch.device_name) AS bs_switch_name,
                    IF(isnull(bs_convertor_device.device_name), 'NA', bs_convertor_device.device_name) AS bs_convertor_device_name,
                    IF(isnull(bh_aggregator_device.device_name), 'NA', bh_aggregator_device.device_name) AS bh_aggregator_device_name,
                    IF(isnull(bh_pop_device.device_name), 'NA', bh_pop_device.device_name) AS bh_pop_device_name,
                    IF(isnull(bh_device.device_name), 'NA', bh_device.device_name) AS bh_device_name,
                    ss_device_type.device_icon as ss_icon,
                    sect_device_type.device_icon as sect_icon,
                    bh_device_type.device_icon as bh_icon,
                    sect_freq.color_hex_value as sect_color,
                    IF((backhaul.bh_configured_on_id = backhaul.bh_switch_id), backhaul.bh_port_name,'NA') AS bs_convertor_port,
                    IF((backhaul.bh_configured_on_id = bs.bs_switch_id), backhaul.bh_port_name,'NA') AS bs_switch_port,
                    IF((backhaul.bh_configured_on_id = backhaul.pop_id), backhaul.bh_port_name,'NA') AS bh_pop_port

                FROM
                    inventory_basestation AS bs
                LEFT JOIN
                    device_device AS bs_switch
                ON
                    bs.bs_switch_id = bs_switch.id
                LEFT JOIN
                    inventory_backhaul AS backhaul
                ON
                    bs.backhaul_id = backhaul.id
                LEFT JOIN
                    device_device AS bh_pe_device
                ON
                    backhaul.pe_ip_id = bh_pe_device.id
                LEFT JOIN
                    device_device AS bs_convertor_device
                ON
                    backhaul.bh_switch_id = bs_convertor_device.id
                LEFT JOIN
                    device_device AS bh_aggregator_device
                ON
                    backhaul.aggregator_id = bh_aggregator_device.id
                LEFT JOIN
                    device_device AS bh_pop_device
                ON
                    backhaul.pop_id = bh_pop_device.id
                LEFT JOIN
                    device_device AS bh_device
                ON
                    backhaul.bh_configured_on_id = bh_device.id
                LEFT JOIN 
                    device_devicetechnology AS bh_device_tech
                ON
                    bh_device.device_technology = bh_device_tech.id
                LEFT JOIN
                    inventory_sector AS sect
                ON
                    bs.id = sect.base_station_id
                LEFT JOIN
                    device_deviceport AS sector_port
                ON
                    sect.sector_configured_on_port_id = sector_port.id
                LEFT JOIN
                    device_device AS device
                ON
                    sect.sector_configured_on_id = device.id
                LEFT JOIN 
                    device_devicetechnology AS sect_device_tech
                ON
                    device.device_technology = sect_device_tech.id
                LEFT JOIN
                    device_device as sect_device
                ON
                    sect.sector_configured_on_id = sect_device.id
                LEFT JOIN
                    inventory_circuit AS ckt
                ON
                    sect.id = ckt.sector_id
                LEFT join
                    inventory_substation as ss
                ON
                    ckt.sub_station_id = ss.id
                LEFT JOIN
                    device_device AS ss_device
                ON
                    ss.device_id = ss_device.id
                LEFT JOIN 
                    device_devicetechnology AS ss_device_tech
                ON
                    ss_device.device_technology = ss_device_tech.id
                LEFT JOIN
                    device_devicetype as sect_device_type
                ON
                    sect_device_type.id = device.device_type
                LEFT JOIN
                    device_devicetype as ss_device_type
                ON
                    ss_device_type.id = ss_device.device_type
                LEFT JOIN
                    device_devicetype as bh_device_type
                ON
                    bh_device_type.id = bh_device.device_type
                LEFT JOIN
                    device_devicefrequency as sect_freq
                ON
                    sect_freq.id = sect.frequency_id
                LEFT JOIN
                    device_device as current_device
                ON
                    current_device.id = {2}
                where
                    current_device.is_added_to_nms > 0
                    AND
                    bs.id in ({0})
                    AND
                    sect_device.id = {1}
            '''.format(', '.join(bs_id), current_sector_device_id, current_device_id)

        elif page_type == 'other':
            case_of_ptp_bh = False
            bs_alias_qs = BaseStation.objects.filter(id=bs_id[0]).values('alias')
            bs_alias = str(bs_alias_qs[0]['alias']).lower()

            queryset = list(Circuit.objects.filter(circuit_id__icontains = bs_alias + '#').values())
            
            if len(queryset):
                case_of_ptp_bh = True

                circuit_id = queryset[0]['circuit_id']
                # spliiting current circuit in case of having PTP-BH, because there we have Far-end and Near-End
                splitted_circuit_id_list = circuit_id.split('#')
                

                if len(splitted_circuit_id_list) > 1:
                    # far_end_bs = str(splitted_circuit_id_list[0]).lower()
                    near_end_bs = str(splitted_circuit_id_list[1]).lower()

                    # far_bs_queryset = list(BaseStation.objects.filter(alias__iexact = far_end_bs).values('id'))
                    # far_end_bs_id = 0
                    # if len(far_bs_queryset):
                    #     far_end_bs_id = far_bs_queryset[0]['id']

                    near_bs_queryset = list(BaseStation.objects.filter(alias__iexact = near_end_bs).values('id'))
                    near_end_bs_id = 0
                    if len(near_bs_queryset):
                        near_end_bs_id = near_bs_queryset[0]['id']
            if case_of_ptp_bh : 
                query_filter = near_end_bs_id
            else :
                query_filter = bs_id[0]

            topology_query = ''' 
                SELECT
                    IF(isnull(bs.id), 'NA', bs.id) AS bs_id,
                    IF(isnull(bs.name), 'NA', bs.name) AS bs_name,
                    IF(isnull(bs.alias), 'NA', bs.alias) AS bs_alias,
                    IF(isnull(bs_switch.id), 'NA', bs_switch.id) AS bs_switch_id, 
                    IF(isnull(backhaul.bh_switch_id), 'NA', backhaul.bh_switch_id) AS bs_convertor_id,
                    IF(isnull(backhaul.aggregator_id), 'NA', backhaul.aggregator_id) AS bh_aggregator_id,
                    IF(isnull(backhaul.pop_id), 'NA', backhaul.pop_id) AS bh_pop_id,
                    IF(isnull(bs_switch.ip_address), 'NA', bs_switch.ip_address) AS bs_switch_ip,
                    IF(isnull(bs.backhaul_id), 'NA', bs.backhaul_id) AS bh_id,
                    IF(isnull(backhaul.pe_hostname), 'NA', backhaul.pe_hostname) AS pe_hostname,
                    IF(isnull(bh_pe_device.id), 'NA', bh_pe_device.id) AS pe_id,
                    IF(isnull(bh_pe_device.ip_address), 'NA', bh_pe_device.ip_address) AS pe_ip,
                    IF(isnull(backhaul.bh_configured_on_id), 'NA', backhaul.bh_configured_on_id) AS bh_device_id,
                    IF(isnull(bs_convertor_device.ip_address), 'NA', bs_convertor_device.ip_address) AS bs_convertor_ip,
                    -- IF(isnull(switch_port_name), 'NA', switch_port_name) AS bs_convertor_port,
                    IF(isnull(bh_pop_device.ip_address), 'NA', bh_pop_device.ip_address) AS bh_pop_ip,
                    IF(isnull(backhaul.pop_port_name), 'NA', backhaul.pop_port_name) AS bh_pop_port,
                    IF(isnull(bh_aggregator_device.ip_address), 'NA', bh_aggregator_device.ip_address) AS bh_aggregator_ip,
                    IF(isnull(backhaul.aggregator_port_name), 'NA', backhaul.aggregator_port_name) AS bh_aggregator_port,
                    IF(isnull(bh_device_type.name), 'NA', bh_device_type.name) AS bh_device_type,
                    IF(isnull(bh_device_tech.name), 'NA', bh_device_tech.name) AS bh_device_tech,   
                    IF(isnull(bh_device.ip_address), 'NA', bh_device.ip_address) AS bh_ip,
                    IF(isnull(sect.id), 'NA', sect.id) AS sect_id,
                    IF(isnull(sect.sector_id), 'NA', sect.sector_id) AS sect_sector_id,
                    IF(isnull(sect.sector_configured_on_id), 'NA', sect.sector_configured_on_id) AS sect_device_id,
                    IF(isnull(device.device_name), 'NA', device.device_name) AS sect_device_name,
                    IF(isnull(sect_device_tech.name), 'NA', sect_device_tech.name) AS sect_device_tech,
                    IF(isnull(sector_port.alias), 'NA', sector_port.alias) AS sect_port,
                    IF(isnull(sect_device_type.name), 'NA', sect_device_type.name) AS sect_device_type,
                    IF(isnull(device.ip_address), 'NA', device.ip_address) AS sect_device_ip,
                    IF(not isnull(sect.sector_id), sect.sector_id, device.ip_address) AS sect_ip_id_title,
                    'NA' AS ss_circuit_id,
                    'NA' AS ss_id,
                    'NA' AS ss_device_id,
                    'NA' AS ss_device_tech,
                    'NA' AS ss_device_type,
                    'NA' AS ss_device_name,
                    'NA' AS ss_device_ip,
                    IF(isnull(bh_pe_device.device_name), 'NA', bh_pe_device.device_name) AS pe_name,
                    IF(isnull(bs_switch.device_name), 'NA', bs_switch.device_name) AS bs_switch_name,
                    IF(isnull(bs_convertor_device.device_name), 'NA', bs_convertor_device.device_name) AS bs_convertor_device_name,
                    IF(isnull(bh_aggregator_device.device_name), 'NA', bh_aggregator_device.device_name) AS bh_aggregator_device_name,
                    IF(isnull(bh_pop_device.device_name), 'NA', bh_pop_device.device_name) AS bh_pop_device_name,
                    IF(isnull(bh_device.device_name), 'NA', bh_device.device_name) AS bh_device_name,
                    sect_device_type.device_icon as sect_icon,
                    bh_device_type.device_icon as bh_icon,
                    sect_freq.color_hex_value as sect_color,
                    IF((backhaul.bh_configured_on_id = backhaul.bh_switch_id), backhaul.bh_port_name,'NA') AS bs_convertor_port,
                    IF((backhaul.bh_configured_on_id = bs.bs_switch_id), backhaul.bh_port_name,'NA') AS bs_switch_port,
                    IF((backhaul.bh_configured_on_id = backhaul.pop_id), backhaul.bh_port_name,'NA') AS bh_pop_port

                FROM
                    inventory_basestation AS bs
                LEFT JOIN
                    device_device AS bs_switch
                ON
                    bs.bs_switch_id = bs_switch.id
                LEFT JOIN
                    inventory_backhaul AS backhaul
                ON
                    bs.backhaul_id = backhaul.id
                LEFT JOIN
                    device_device AS bh_pe_device
                ON
                    backhaul.pe_ip_id = bh_pe_device.id
                LEFT JOIN
                    device_device AS bs_convertor_device
                ON
                    backhaul.bh_switch_id = bs_convertor_device.id
                LEFT JOIN
                    device_device AS bh_aggregator_device
                ON
                    backhaul.aggregator_id = bh_aggregator_device.id
                LEFT JOIN
                    device_device AS bh_pop_device
                ON
                    backhaul.pop_id = bh_pop_device.id
                LEFT JOIN
                    device_device AS bh_device
                ON
                    backhaul.bh_configured_on_id = bh_device.id
                LEFT JOIN 
                    device_devicetechnology AS bh_device_tech
                ON
                    bh_device.device_technology = bh_device_tech.id
                LEFT JOIN
                    inventory_sector AS sect
                ON
                    sect.base_station_id = {2}
                LEFT JOIN
                    device_deviceport AS sector_port
                ON
                    sect.sector_configured_on_port_id = sector_port.id
                LEFT JOIN
                    device_device AS device
                ON
                    sect.sector_configured_on_id = device.id
                LEFT JOIN 
                    device_devicetechnology AS sect_device_tech
                ON
                    device.device_technology = sect_device_tech.id
                LEFT JOIN
                    device_device as sect_device
                ON
                    sect.sector_configured_on_id = sect_device.id
                LEFT JOIN
                    inventory_circuit AS ckt
                ON
                    sect.id = ckt.sector_id
                LEFT JOIN
                    device_devicetype as sect_device_type
                ON
                    sect_device_type.id = device.device_type
                LEFT JOIN
                    device_devicetype as bh_device_type
                ON
                    bh_device_type.id = bh_device.device_type
                LEFT JOIN
                    device_devicefrequency as sect_freq
                ON
                    sect_freq.id = sect.frequency_id
                LEFT JOIN
                    device_device as current_device
                ON
                    current_device.id = {1}
                where
                    current_device.is_added_to_nms > 0
                    AND
                    bs.id in ({0})
                GROUP by(sect_sector_id)
            '''.format(', '.join(bs_id), current_device_id, query_filter)

        # calling global method for executing query
        result_of_query = nocout_utils.fetch_raw_result(topology_query)

        resultant_dict = dict()
        bs_ids = list()
        sector_ids = list()
        ss_ids = list()
        sector_dict = dict()
        bs_ids_dict = dict()
        bh_aggregator_id = ''
        bh_pop_id = ''
        bs_convertor_id = ''
        bs_alias = ''
        bs_icon = ''

        is_init = False

        # In case of No PL Info available
        blank_pl_info = {
            "severity" : "",
            "value": "",
            "packet_loss": "",
            "latency": ""
        }

        # converting query result in required format 

        if have_ptp_bh:
            bs_id = ''
            bs_alias = ''
            far_end_bs_id = ''
            far_end_bs_alias = ''
            bs_icon = ''
            for bs in result_of_query:
                if bs.get('bs_id') not in bs_ids:
                    bs_ids.append(bs.get('bs_id'))
                    if bs.get('pe_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('pe_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('pe_id')))
                            pe_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            pe_pl_info = blank_pl_info
                    else:
                        pe_pl_info = blank_pl_info

                    if bs.get('bh_device_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('bh_device_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('bh_device_id')))
                            bh_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            bh_pl_info = blank_pl_info
                    else:
                        bh_pl_info = blank_pl_info

                    if bs.get('bh_aggregator_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('bh_aggregator_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('bh_aggregator_id')))
                            bh_aggr_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            bh_aggr_pl_info = blank_pl_info
                    else:
                        bh_aggr_pl_info = blank_pl_info

                    if bs.get('bh_pop_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('bh_pop_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('bh_pop_id')))
                            bh_pop_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            bh_pop_pl_info = blank_pl_info
                    else:
                        bh_pop_pl_info = blank_pl_info

                    if bs.get('bs_convertor_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('bs_convertor_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('bs_convertor_id')))
                            bs_convertor_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            bs_convertor_pl_info = blank_pl_info
                    else:
                        bs_convertor_pl_info = blank_pl_info

                    if bs.get('far_end_bs_switch_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('far_end_bs_switch_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('far_end_bs_switch_id')))
                            far_end_bs_switch_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            far_end_bs_switch_pl_info = blank_pl_info
                    else:
                        far_end_bs_switch_pl_info = blank_pl_info

                    if bs.get('near_end_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('near_end_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('near_end_id')))
                            near_end_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            near_end_pl_info = blank_pl_info
                    else:
                        near_end_pl_info = blank_pl_info

                    if bs.get('far_end_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('far_end_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('far_end_id')))
                            far_end_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            far_end_pl_info = blank_pl_info
                    else:
                        far_end_pl_info = blank_pl_info

                    if not is_init:
                        resultant_dict = {
                            "bh_id": bs.get('bh_id'),
                            "bh_icon": "/static/img/icons/mobile_blackhaul_icon_small.png" if not bs.get('bh_icon') else "/media/" + bs.get('bh_icon'),
                            "bh_device_id": bs.get('bh_device_id'),
                            "bh_device_tech": bs.get('bh_device_tech'),
                            "bh_device_type": bs.get('bh_device_type'),
                            "bh_ip": bs.get('bh_ip'),
                            "pe_ip" : bs.get('pe_ip'),
                            "pe_hostname" : bs.get('pe_hostname'),
                            "bs_switch_ip" : bs.get('bs_switch_ip'),
                            "bs_switch_port" : bs.get('bs_switch_port'),
                            "far_end_bs_switch_port" : bs.get('far_end_bs_switch_port'),
                            "far_end_bs_switch_ip" : bs.get('far_end_bs_switch_ip'),
                            "aggregation_switch_ip" : bs.get('bh_aggregator_ip'),
                            "aggregation_switch_port" : bs.get('bh_aggregator_port'),
                            "pop_convertor_ip" : bs.get('bh_pop_ip'),
                            "pop_convertor_port" : bs.get('bh_pop_port'),
                            "bs_convertor_ip" : bs.get('bs_convertor_ip'),
                            "bs_convertor_port" : bs.get('bs_convertor_port'),
                            "far_end_ip" : bs.get('far_end_ip'),
                            "near_end_ip" : bs.get('near_end_ip'),
                            "bs_switch_pl_info": bh_pl_info,
                            "pe_pl_info": pe_pl_info,
                            "bh_aggr_pl_info": bh_aggr_pl_info,
                            "bh_pop_pl_info": bh_pop_pl_info,
                            "bs_convertor_pl_info": bs_convertor_pl_info,
                            "far_end_bs_switch_pl_info" : far_end_bs_switch_pl_info,
                            "near_end_pl_info" : near_end_pl_info,
                            "far_end_pl_info" : far_end_pl_info,
                            "bs_switch_name" : bs.get('bs_switch_name'),
                            "pe_name" : bs.get('pe_name'),
                            "bs_convertor_device_name" : bs.get('bs_convertor_device_name'),
                            "bh_aggregator_device_name" : bs.get('bh_aggregator_device_name'),
                            "bh_pop_device_name" : bs.get('bh_pop_device_name'),
                            "bh_device_name" : bs.get('bh_device_name'),
                            "far_end_bs_switch_name" : bs.get('far_end_bs_switch_name'),
                            "near_end_device_name" : bs.get('near_end_device_name'),
                            "far_end_device_name" : bs.get('far_end_device_name'),
                            "far_end_base_station" : list(),
                            "base_station" : list()
                        }

                    bs_ids_dict[bs.get('far_end_bs_id')] = {
                        "sectors": list(),
                        "bs_id": bs.get('bs_id'),
                        "bs_alias": bs.get('bs_alias'),
                        "far_end_bs_id": bs.get('far_end_bs_id'),
                        "far_end_bs_alias": bs.get('far_end_bs_alias'),
                        "bs_icon": "/static/img/icons/bs-big.png",

                    }
                    bs_id = bs.get('bs_id')
                    bs_alias = bs.get('bs_alias')
                    far_end_bs_id = bs.get('far_end_bs_id')
                    far_end_bs_alias = bs.get('far_end_bs_alias')
                    bs_icon = "/static/img/icons/bs-big.png"

                    is_init = True

                if not multiple_bs:
                    if str(bs.get('far_end_sect_id')) not in sector_dict:
                        if bs.get('far_end_sect_device_id'):
                            try:
                                severity, other_detail = device_current_status(Device.objects.get(id=bs.get('far_end_sect_device_id')))
                                pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('far_end_sect_device_id')))
                                far_end_sect_pl_info = {
                                    "severity" : severity if severity else 'NA',
                                    "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                    "packet_loss" : pack_loss if pack_loss else 'NA',
                                    "latency" : latency if latency else 'NA'
                                }
                            except Exception, e:
                                far_end_sect_pl_info = blank_pl_info
                        else:
                            far_end_sect_pl_info = blank_pl_info
                        

                        sector_dict[str(bs.get('far_end_sect_id'))] = {
                            "id": str(bs.get('far_end_sect_id')),
                            "device_name": bs.get('far_end_sect_device_name'),
                            "device_id": bs.get('far_end_sect_device_id'),
                            "device_tech": bs.get('far_end_sect_device_tech'),
                            "device_type": bs.get('far_end_sect_device_type'),
                            "sect_port" : bs.get('far_end_sect_port'),
                            "ip_address": bs.get('far_end_sect_device_ip'),
                            "sect_ip_id_title": bs.get('far_end_sect_ip_id_title'),
                            "icon": "/media/" + bs.get('sect_icon'),
                            "pl_info": far_end_sect_pl_info,
                            "sub_station": list()
                        }

                    try:
                        if bs.get('far_end_ss_device_id'):
                            try:
                                severity, other_detail = device_current_status(Device.objects.get(id=bs.get('far_end_ss_device_id')))
                                pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('far_end_ss_device_id')))
                                far_end_ss_pl_info = {
                                    "severity" : severity if severity else 'NA',
                                    "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                    "packet_loss" : pack_loss if pack_loss else 'NA',
                                    "latency" : latency if latency else 'NA'
                                }
                            except Exception, e:
                                far_end_ss_pl_info = blank_pl_info
                        else:
                            far_end_ss_pl_info = blank_pl_info
                        # Only appending the selected substaion
                        if bs.get('far_end_ss_device_id') == current_device_id:
                            sector_dict[str(bs.get('far_end_sect_id'))]['sub_station'].append({
                                "id": bs.get('far_end_ss_id'),
                                "device_name": bs.get('far_end_ss_device_name'),
                                "device_id": bs.get('far_end_ss_device_id'),
                                "device_tech": bs.get('far_end_ss_device_tech'),
                                "device_type": bs.get('far_end_ss_device_type'),
                                "ip_address": bs.get('far_end_ss_device_ip'),
                                "ckt_id": bs.get('far_end_ss_circuit_id'),
                                "link_color": bs.get('sect_color'),
                                "icon": "/media/" + bs.get('ss_icon'),
                                "pl_info": far_end_ss_pl_info
                            })
                    except Exception, e:
                        pass
                
                    bs_ids_dict[str(bs.get('far_end_bs_id'))]['sectors'].append(sector_dict[str(bs.get('far_end_sect_id'))])
            
            if multiple_bs:
                resultant_dict['far_end_base_station'] = bs_ids_dict.values()
            else:
                if not resultant_dict['far_end_base_station']:
                    resultant_dict['far_end_base_station'] = list()

                if not resultant_dict['base_station']:
                    resultant_dict['base_station'] = list()

                resultant_dict['base_station'].append({
                    'bs_id': bs_id,
                    'bs_alias': bs_alias
                })

                resultant_dict['far_end_base_station'].append({
                    "sectors": sector_dict.values(),
                    'far_end_bs_id': far_end_bs_id,
                    'far_end_bs_alias': far_end_bs_alias,
                    'bs_icon': bs_icon
                })            

        else:

            for bs in result_of_query:
                if bs.get('bs_id') not in bs_ids:
                    bs_ids.append(bs.get('bs_id'))
                    if bs.get('pe_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('pe_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('pe_id')))
                            pe_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            pe_pl_info = blank_pl_info
                    else:
                        pe_pl_info = blank_pl_info

                    if bs.get('bh_device_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('bh_device_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('bh_device_id')))
                            bh_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            bh_pl_info = blank_pl_info
                    else:
                        bh_pl_info = blank_pl_info

                    if bs.get('bh_aggregator_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('bh_aggregator_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('bh_aggregator_id')))
                            bh_aggr_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            bh_aggr_pl_info = blank_pl_info
                    else:
                        bh_aggr_pl_info = blank_pl_info

                    if bs.get('bh_pop_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('bh_pop_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('bh_pop_id')))
                            bh_pop_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            bh_pop_pl_info = blank_pl_info
                    else:
                        bh_pop_pl_info = blank_pl_info

                    if bs.get('bs_convertor_id'):
                        try:
                            severity, other_detail = device_current_status(Device.objects.get(id=bs.get('bs_convertor_id')))
                            pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('bs_convertor_id')))
                            bs_convertor_pl_info = {
                                "severity" : severity if severity else 'NA',
                                "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                "packet_loss" : pack_loss if pack_loss else 'NA',
                                "latency" : latency if latency else 'NA'
                            }
                        except Exception, e:
                            bs_convertor_pl_info = blank_pl_info
                    else:
                        bs_convertor_pl_info = blank_pl_info

                    if not is_init:
                        resultant_dict = {
                            "bh_id": bs.get('bh_id'),
                            "bh_icon": "/static/img/icons/mobile_blackhaul_icon_small.png" if not bs.get('bh_icon') else "/media/" + bs.get('bh_icon'),
                            "bh_device_id": bs.get('bh_device_id'),
                            "bh_device_tech": bs.get('bh_device_tech'),
                            "bh_device_type": bs.get('bh_device_type'),
                            "bs_switch_ip": bs.get('bs_switch_ip'),
                            "bh_ip": bs.get('bh_ip'),
                            "pe_ip" : bs.get('pe_ip'),
                            "pe_hostname" : bs.get('pe_hostname'),
                            "aggregation_switch_ip" : bs.get('bh_aggregator_ip'),
                            "aggregation_switch_port" : bs.get('bh_aggregator_port'),
                            "pop_convertor_ip" : bs.get('bh_pop_ip'),
                            "pop_convertor_port" : bs.get('bh_pop_port'),
                            "bs_convertor_ip" : bs.get('bs_convertor_ip'),
                            "bs_convertor_port" : bs.get('bs_convertor_port'),
                            "bs_switch_port" : bs.get('bs_switch_port'),
                            "far_end_bs_switch_port" : bs.get('far_end_bs_switch_port'),
                            "pe_pl_info": pe_pl_info,
                            "bs_switch_pl_info": bh_pl_info,
                            "bh_aggr_pl_info": bh_aggr_pl_info,
                            "bh_pop_pl_info": bh_pop_pl_info,
                            "bs_convertor_pl_info": bs_convertor_pl_info,
                            "pe_name" : bs.get('pe_name'),
                            "bs_switch_name" : bs.get('bs_switch_name'),
                            "bs_convertor_device_name" : bs.get('bs_convertor_device_name'),
                            "bh_aggregator_device_name" : bs.get('bh_aggregator_device_name'),
                            "bh_pop_device_name" : bs.get('bh_pop_device_name'),
                            "bh_device_name" : bs.get('bh_device_name'),
                            "far_end_bs_switch_name" : bs.get('far_end_bs_switch_name'),
                            "near_end_device_name" : bs.get('near_end_device_name'),
                            "far_end_device_name" : bs.get('far_end_device_name'),
                            "base_station" : list()
                        }

                    bs_ids_dict[bs.get('bs_id')] = {
                        "sectors": list(),
                        "bs_id": bs.get('bs_id'),
                        "bs_alias": bs.get('bs_alias'),
                        "bs_icon": "/static/img/icons/bs-big.png",

                    }
                    bs_id = bs.get('bs_id')
                    bs_alias = bs.get('bs_alias')
                    bs_icon = "/static/img/icons/bs-big.png"

                    is_init = True

                if not multiple_bs:
                    if bs.get('sect_id') and str(bs.get('sect_id')) not in sector_dict:
                        if bs.get('sect_device_id'):
                            try:
                                severity, other_detail = device_current_status(Device.objects.get(id=bs.get('sect_device_id')))
                                pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('sect_device_id')))
                                sect_pl_info = {
                                    "severity" : severity if severity else 'NA',
                                    "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                    "packet_loss" : pack_loss if pack_loss else 'NA',
                                    "latency" : latency if latency else 'NA'
                                }
                            except Exception, e:
                                sect_pl_info = blank_pl_info
                        else:
                            sect_pl_info = blank_pl_info
                        

                        sector_dict[str(bs.get('sect_id'))] = {
                            "id": str(bs.get('sect_id')),
                            "device_name": bs.get('sect_device_name'),
                            "device_id": bs.get('sect_device_id'),
                            "device_tech": bs.get('sect_device_tech'),
                            "device_type": bs.get('sect_device_type'),
                            "sect_port" : bs.get('sect_port'),
                            "ip_address": bs.get('sect_device_ip'),
                            "sect_ip_id_title": bs.get('sect_ip_id_title'),
                            "icon": "/media/" + str(bs.get('sect_icon', '')),
                            "pl_info": sect_pl_info,
                            "sub_station": list()
                        }

                    try:
                        if bs.get('ss_device_id'):
                            try:
                                severity, other_detail = device_current_status(Device.objects.get(id=bs.get('ss_device_id')))
                                pack_loss, latency = device_pl_latency_values(Device.objects.get(id=bs.get('ss_device_id')))
                                ss_pl_info = {
                                    "severity" : severity if severity else 'NA',
                                    "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                                    "packet_loss" : pack_loss if pack_loss else 'NA',
                                    "latency" : latency if latency else 'NA'
                                }
                            except Exception, e:
                                ss_pl_info = blank_pl_info
                        else:
                            ss_pl_info = blank_pl_info
                        # Only appending the selected substaion
                        if bs.get('ss_device_id') == current_device_id:
                            sector_dict[str(bs.get('sect_id'))]['sub_station'].append({
                                "id": bs.get('ss_id'),
                                "device_name": bs.get('ss_device_name'),
                                "device_id": bs.get('ss_device_id'),
                                "device_tech": bs.get('ss_device_tech'),
                                "device_type": bs.get('ss_device_type'),
                                "ip_address": bs.get('ss_device_ip'),
                                "ckt_id": bs.get('ss_circuit_id'),
                                "link_color": bs.get('sect_color'),
                                "icon": "/media/" + bs.get('ss_icon'),
                                "pl_info": ss_pl_info
                            })
                    except Exception, e:
                        pass
                
                    try:
                        bs_ids_dict[str(bs.get('bs_id'))]['sectors'].append(sector_dict[str(bs.get('sect_id'))])
                    except Exception, e:
                        pass

            if multiple_bs:
                resultant_dict['base_station'] = bs_ids_dict.values()
            else:
                if 'base_station' not in resultant_dict:
                    resultant_dict['base_station'] = list()

                resultant_dict['base_station'].append({
                    "sectors": sector_dict.values(),
                    'bs_id': bs_id,
                    'bs_alias': bs_alias,
                    'bs_icon': bs_icon
                })

        result['data'].append(resultant_dict)
        result['message'] = 'Device Topology Details Fetched Successfully.'
        result['success'] = 1
        result['have_ptp_bh'] = have_ptp_bh
        result['limit_till_bs'] = limit_till_bs

        return HttpResponse(json.dumps(result), content_type="application/json")

class EveryFiveMinDeviceStatus(View):
    """
    The Class based View to get pl info in every 5 min. for each device in topo-view.
    """
    def get(self, request):

        result = {
            'success': 0,
            'message': 'Device pl info not fetched successfully.',
            'data': []
        }

        try:
            pl_device_list = json.loads(self.request.GET.get('data'))
        except Exception, e:
            pl_device_list = list()
        
        pl_info_list = list()
        for pl_device in pl_device_list:

            try:
                severity, other_detail = device_current_status(Device.objects.get(device_name=pl_device))
                pack_loss, latency = device_pl_latency_values(Device.objects.get(device_name=pl_device))
                current_pl_info = {
                    "id" : pl_device,
                    "severity" : severity if severity else 'NA',
                    "value": other_detail['c_val'] if other_detail and 'c_val' in other_detail else 'NA',
                    "packet_loss" : pack_loss if pack_loss else 'NA',
                    "latency" : latency if latency else 'NA'
                }
            except Exception, e:
                current_pl_info = {
                    "id" : pl_device,
                    "severity" : "",
                    "value": "",
                    "packet_loss": "",
                    "latency": ""
                }
            pl_info_list.append(current_pl_info)


        result = {
            'success': 1,
            'message': 'Device pl info fetched successfully.',
            'data': pl_info_list
        }
        return HttpResponse(json.dumps(result), content_type="application/json")


class GetTopologyToolTip(View):
    """
    The Class based View to get tooltip for each device on topo-view page.
    """

    def get(self, request):
        station_type = self.request.GET.get('type')
        required_id = self.request.GET.get('id')

        result = {
            'success': 0,
            'message': 'Device info not fetched',
            'data': list()
        }

        if not required_id:
            return HttpResponse(json.dumps(result), content_type="application/json")    
        
        if (station_type == 'BS'):
            resultset = getBSInventoryInfo(required_id)
        elif (station_type == 'BH'):
            resultset = getBHInventoryInfo(required_id)
        elif (station_type == 'SECT'):
            resultset = getSectorInventoryInfo(required_id)
        elif (station_type == 'SS'):
            resultset = getSSInventoryInfo(required_id)       

        
        formatted_result = self.format_result(resultset[0])
        result = {
            'success': 1,
            'message': 'Device info fetched successfully.',
            'data': formatted_result
        }
        
        return HttpResponse(json.dumps(result), content_type="application/json")

    def format_result(self, dataset):
        """
        This function format tooltip data as per required format
        """
        formatted_result = list()
        for key in dataset:
            temp_dict = {
                'name': key,
                'title': key,
                'show'  : 1,
                'value': dataset.get(key, 'NA')
            }

            formatted_result.append(temp_dict)

        return formatted_result


class PowerStatusListing(BaseDatatableView):

    model = PowerSignals
    columns = [
        'id',
        'message',
        'created_at',
        'signal_type',
        'circuit_contacts__circuit__sub_station__device__device_name'
    ]

    order_columns = [
        'message',
        'created_at',
        'signal_type'
    ]

    def get_initial_queryset(self):
        device_id = self.request.GET.get('device_id', None)
        if device_id:
            qs = self.model.objects.filter(
                circuit_contacts__circuit__sub_station__device__id=device_id
            ).values(*self.columns).order_by('-created_at')
        else:
            qs = self.model.objects.filter(id=0)

        return qs

    def prepare_results(self, qs):
        latest_timestamp = ''
        resultset = list()
        for data in qs:
            temp_dict = {
                'msg': data.get('message'),
                'created_at': data.get('created_at'),
                'status_type': data.get('signal_type')
            }

            if data.get('created_at'):
                try:
                    temp_dict.update(
                        created_at=data.get('created_at').strftime(DATE_TIME_FORMAT)
                    )
                except Exception, e:
                    pass

            resultset.append(temp_dict)

        return resultset

    def get_context_data(self, *args, **kwargs):

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
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

class PowerStatus(View):
    """
    The Class based View to get the last updated power status for single device.
    """
    def get(self, request):

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
        device_id = int(self.request.GET.get('device_id'))
        
        if device_id:
            # getting latest updated value from dataset
            qs_dict = PowerSignals.objects.filter(
                circuit_contacts__circuit__sub_station__device__id=device_id, signal_type='Received'
            ).values().order_by('-created_at')
            

            if qs_dict.exists():
                qs_dict = qs_dict[0]

                # updating resultset
                self.result.update(success= 1, message= 'Current status fetched successfully')
                self.result['data']['objects']['perf'] = qs_dict['message']
                self.result['data']['objects']['status'] = qs_dict['message']
                self.result['data']['objects']['last_updated'] = qs_dict['created_at'].strftime(date_format)
            else :
                self.result.update(message= 'Data not fetched successfully')


        else:
            qs_dict = PowerSignals.objects.filter(id=0)

        return HttpResponse(json.dumps(self.result), content_type="application/json")

class SendPowerSms(View):
    """
    The Class based View to send button specific sms .
    """

    def get(self, request):
        result = {
            'success': 0,
            'message': 'No Data.',
        }

        device_id = self.request.GET.get('device_id')
        button_name = self.request.GET.get('button_name').strip().lower()
        message = ''
        send_to = ''

        # variables for sending sms using provided sms gateway
        payload =  GATEWAY_PARAMETERS
        url = GATEWAY_SETTINGS['URL']

        if not device_id:
            return HttpResponse(json.dumps(result), content_type="application/json")
        
        # getting the device related phone number from database
        circuit_contact_instance = CircuitContacts.objects.filter(
            circuit__sub_station__device__id=device_id
        )

        if circuit_contact_instance.exists():
            send_to = circuit_contact_instance[0].phone_number
            
            # getting suitable response for clicked button from power_sms_dict, defined in settings.py
            message = settings.POWER_SMS_DICT[button_name]

            payload['N'] = send_to
            payload['M'] = message
            try:
                r = requests.get(url, params=payload, timeout=(60, 60))
            except Exception, e:
                r = None

            if r and r.status_code == 200:
                power_instance = PowerSignals()
                power_instance.circuit_contacts = circuit_contact_instance[0]
                power_instance.message = str(message)
                power_instance.signal_type = 'Sent'
                power_instance.save()

                result.update(success=1, message='Message sent successfully')
            else:
                result.update(success=0, message='Error in accessing gateway')

        else:
            result.update(message='Phone number does not exist')

        return HttpResponse(json.dumps(result), content_type="application/json")


class SavePowerLog(View):
    """
    This class saves power logs as per the given POST params
    """
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(SavePowerLog, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        result = {
            'success': 0,
            'message': 'Power logs not saved',
        }

        try:
            # POST Params
            device_id = self.request.POST.get('device_id')
            reason_str = self.request.POST.get('reason_str')
            action = self.request.POST.get('action')

            # Fetch circuit instance for given SS device
            circuit_instance = Circuit.objects.get(sub_station__device__id=device_id)
            customer_alias = circuit_instance.customer.alias
            circuit_id = circuit_instance.circuit_id
            ss_ip = circuit_instance.sub_station.device.ip_address

            # Create PowerLogs instance
            logs_instance = PowerLogs()
            logs_instance.user_id = self.request.user.id
            logs_instance.reason = reason_str
            logs_instance.action = action
            logs_instance.ss_ip = ss_ip
            logs_instance.circuit_id = circuit_id
            logs_instance.customer_alias = customer_alias

            # Save log
            logs_instance.save()

            # Update response dict
            result.update(
                success=1,
                message='Log saved successfully.'
            )
        except Exception, e:
            pass

        return HttpResponse(json.dumps(result))


class InitDeviceReboot(View):
    """
    This function reboot given device by executing the shell script
    """
    def get(self, request, *args, **kwargs):
        
        result = {
            'success': 0,
            'message': 'Device reboot not successful.',
        }

        try:
            import subprocess
            device_id = self.request.GET.get('device_id')
            device = Device.objects.get(id=device_id)
            machine_name = device.machine.name
            ip_address = device.ip_address
            device_type = DeviceType.objects.get(id=device.device_type).name
            
            env_name = 'omd'
            if ENV_NAME != 'uat':
                env_name = 'apps'

            cmd_list = [
                'bash', 
                '/' +str(env_name)+ '/nocout/nocout/nocout/performance/script/ss_reboot.sh', 
                machine_name, 
                ip_address, 
                device_type, 
                env_name
            ]

            reboot_response = subprocess.Popen(
                cmd_list, 
                stdout=subprocess.PIPE
            )

            response = reboot_response.stdout.read()

            if 'yes' in response:
                result.update(
                    success=1,
                    message='Device successfully reboot.'
                )
            elif 'no' in response:
                result.update(
                    success=1,
                    message='Connection not established or Authentication Error.'
                )
            elif 'nr' in response:
                result.update(
                    success=1,
                    message='Device Not Reachable.'
                )
            else:
                pass
        except Exception, e:
            log.error('Device Reboot Exception ---')
            log.error(e)
            pass

        return HttpResponse(json.dumps(result))



class GetSSTelnet(View):
    """
    Generic class view for giving required info for SS telnet
    """

    def get(self, request):
        result = {
            'success' : 0,
            'message' : 'telnet info not fetched',
            'data' : []
        }

        
        device_id = self.request.GET.get('device_id')
        if not device_id:
            return HttpResponse(json.dumps(result), content_type="application/json")

        device_qs = Device.objects.filter(id = device_id).values('ip_address', 'machine_id', 'device_type')
        machine_qs = Machine.objects.filter(id = device_qs[0]['machine_id']).values('name')
        deviceType_qs = DeviceType.objects.filter(id = device_qs[0]['device_type']).values('name')

        machine_name = machine_qs[0]['name']
        device_ip = device_qs[0]['ip_address']
        device_type = deviceType_qs[0]['name']

        result['data'].append({
            'machine_name' : machine_name,
            'device_ip' : device_ip,
            'device_type' : device_type
            })

        result.update(success= 1, message= 'Telnet info fetched successfully')

        return HttpResponse(json.dumps(result), content_type="application/json")

class GetBSTelnet(View):
    """
    Generic class view for giving required info for BS telnet
    """

    def get(self, request):
        result = {
            'success' : 0,
            'message' : 'telnet info not fetched',
            'data' : []
        }

        
        device_id = self.request.GET.get('device_id')
        if not device_id:
            return HttpResponse(json.dumps(result), content_type="application/json")

        device_qs = Device.objects.filter(id = device_id).values('ip_address', 'machine_id', 'device_type')
        machine_qs = Machine.objects.filter(id = device_qs[0]['machine_id']).values('name')
        deviceType_qs = DeviceType.objects.filter(id = device_qs[0]['device_type']).values('name')

        machine_name = machine_qs[0]['name']
        device_ip = device_qs[0]['ip_address']
        device_type = deviceType_qs[0]['name']

        result['data'].append({
            'machine_name' : machine_name,
            'device_ip' : device_ip,
            'device_type' : device_type
            })

        result.update(success= 1, message= 'Telnet info fetched successfully')

        return HttpResponse(json.dumps(result), content_type="application/json")
        
class InitStabilityTest(ListView):
    """
    A generic class view to load ping stability test listing

    """
    model = PingStabilityTest
    template_name = 'performance/stability_test.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        :param kwargs:
        """
        context = super(InitStabilityTest, self).get_context_data(**kwargs)

        datatable_headers = [
            {'mData': 'status', 'sTitle': 'Status', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'user_profile__username', 'sTitle': 'Username', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'technology__alias', 'sTitle': 'Technology', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'time_duration', 'sTitle': 'Time Duration (In Hrs)', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'created_at', 'sTitle': 'Started At', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'email_ids', 'sTitle': 'Email Address', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'auto', 'bSortable': False},
        ]

        tech_list = list(DeviceTechnology.objects.exclude(
            name__iexact='default'
        ).values(
            'id', 'alias', 'name'
        ))

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['tech_list'] = tech_list
        return context


class PingStabilityTestListing(BaseDatatableView):
    """
    Render JQuery datatables for listing of device type fields
    """
    model = PingStabilityTest
    columns = [
        'status',
        'user_profile__username',
        'ip_address',
        'technology__alias',
        'time_duration',
        'created_at',
        'email_ids',
        'file_path'
    ]
    order_columns = columns

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            query_object = Q()
            for column in self.columns:
                query_object = query_object | Q(**{"%s__icontains" % column: sSearch})

            qs = qs.filter(query_object)
        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        return self.model.objects.values(*self.columns + ['id']).order_by('-id')

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        for dct in qs:
            dct['action'] = ''
            if dct.get('status') == 1:
                dct['status'] = 'Success'
                if dct.get('file_path'):
                    if '/media/' in dct.get('file_path'):
                        try:
                            dct['file_path'] = '/media/'+dct.get('file_path').split('/media/')[1]
                        except Exception, e:
                            dct['file_path'] = ''
                    else:
                        dct['file_path'] = ''

                    dct.update(
                        action='<a href="{0}" target="_blank"><i class="fa fa-download text-primary"> \
                                </i></a>'.format(dct.get('file_path'))
                    )
            else:
                dct['status'] = 'Pending'

            try:
                dct['email_ids'] = ', '.join(str(dct['email_ids']).split(','))
            except Exception as e:
                pass

            created_at = dct.get('created_at')
            if created_at:
                dct['created_at'] = created_at.strftime(DATE_TIME_FORMAT)

        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
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
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret
