# -*- coding: utf-8 -*-

# import json
import ujson as json
import datetime
import time
from django.db.models import Count, Q
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import ListView
from django.views.generic.base import View
from django_datatables_view.base_datatable_view import BaseDatatableView

from device.models import Device, City, State, DeviceType, DeviceTechnology, DevicePort
from service.models import ServiceDataSource
from inventory.models import SubStation, Circuit, Sector, BaseStation, Backhaul, Customer

from performance.models import PerformanceService, PerformanceNetwork, \
    EventService, NetworkStatus, \
    ServiceStatus, InventoryStatus, \
    PerformanceStatus, PerformanceInventory, \
    Status, NetworkAvailabilityDaily, Topology, Utilization, UtilizationStatus, SpotDashboard, \
    PerformanceServiceBiHourly, PerformanceServiceHourly, PerformanceServiceDaily, PerformanceServiceWeekly, \
    PerformanceServiceMonthly, PerformanceServiceYearly, PerformanceNetworkBiHourly, PerformanceNetworkHourly, \
    PerformanceNetworkDaily, PerformanceNetworkWeekly, PerformanceNetworkMonthly, PerformanceNetworkYearly, \
    PerformanceStatusDaily, PerformanceStatusWeekly, PerformanceStatusMonthly, PerformanceStatusYearly, \
    PerformanceInventoryDaily, PerformanceInventoryWeekly, PerformanceInventoryMonthly, PerformanceInventoryYearly

from nocout.utils import logged_in_user_organizations

from django.utils.dateformat import format

from operator import itemgetter

from nocout.utils import util as nocout_utils

#utilities inventory
from inventory.utils import util as inventory_utils

from performance.utils import util as perf_utils

from service.utils.util import service_data_sources

from nocout.settings import DATE_TIME_FORMAT, LIVE_POLLING_CONFIGURATION

from performance.formulae import display_time, rta_null
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin, DatatableOrganizationFilterMixin
from nocout.utils.util import fetch_raw_result

##execute this globally
SERVICE_DATA_SOURCE = service_data_sources()
##execute this globally

import logging

log = logging.getLogger(__name__)

# def uptime_to_days(uptime=0):
#     if uptime:
#         ret_val = int(float(uptime)/(60 * 60 * 2``))
#         return ret_val if ret_val > 0 else int(float(uptime)/(60 * 60))

#
# def rta_null(rta=0):
#     """
#
#     :param rta:
#     :return:
#     """
#     try:
#         if float(rta) == 0:
#             return None
#     except Exception as e:
#         return None
#
#     return rta


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

        hidden_headers = []
        common_headers = []
        polled_headers = []
        action_headers = []
        specific_headers = []

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

        if page_type in ["network"]:
            specific_headers += [
                {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
                {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
                {'mData': 'customer_name', 'sTitle': 'Customer', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
            ]

        elif page_type in ["customer"]:
            specific_headers += [
                {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
                {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
                {'mData': 'customer_name', 'sTitle': 'Customer', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
                {'mData': 'near_end_ip', 'sTitle': 'Near End Ip', 'sWidth': 'auto', 'sClass': 'hidden-xs',
                 'bSortable': True},
            ]

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
        Generic function required to fetch the initial data with respect to the page_type parameter in the get request requested.

        :param device_association:
        :param kwargs:
        :return: list of devices
        """

        page_type = self.request.GET.get('page_type')

        other_type = self.request.GET.get('other_type', None)

        required_value_list = ['id', 'machine__name', 'device_name', 'ip_address']

        device_tab_technology = self.request.GET.get('data_tab')

        devices = inventory_utils.filter_devices(organizations=kwargs['organizations'],
                                                 data_tab=device_tab_technology,
                                                 page_type=page_type,
                                                 other_type=other_type,
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
        page_type = self.request.GET.get('page_type')
        device_tab_technology = self.request.GET.get('data_tab')

        if page_type == 'network':
            type_rf = 'sector'
        elif page_type == 'customer':
            type_rf = 'ss'
        else:
            type_rf = None

        return perf_utils.prepare_gis_devices(qs, page_type,
                                              monitored_only=True,
                                              technology=device_tab_technology,
                                              type_rf=type_rf
        )

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

    def paging(self, qs):
        """ Paging
        """
        limit = min(int(self.request.REQUEST.get('iDisplayLength', 10)), self.max_display_length)
        # if pagination is disabled ("bPaginate": false)
        if limit == -1:
            return qs
        start = int(self.request.REQUEST.get('iDisplayStart', 0))
        offset = start + limit
        return qs[start:offset]

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request

        page_type = self.request.GET['page_type']

        download_excel = self.request.GET.get('download_excel', None)

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

        # if download_excel != "yes":
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
            if download_excel == "yes":
                qs = self.prepare_polled_results(qs, multi_proc=False, machine_dict=machines)
            else:
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

        is_util_tab = request.GET.get('is_util',0)

        page_data = {
            'page_title': page_type.capitalize(),
            'device_technology': device_technology,
            'device': device,
            'realdevice': realdevice,
            'get_devices_url': 'performance/get_inventory_devices/' + page_type,
            'get_status_url': 'performance/get_inventory_device_status/' + page_type + '/device/' + str(device_id),
            'get_services_url': 'performance/get_inventory_service_data_sources/device/'+str(device_id)+'/?is_util='+str(is_util_tab),
            'inventory_page_url' : reverse(
                'device_edit',
                kwargs={'pk': device_id},
                current_app='device'
            ),
            'alert_page_url' : reverse(
                'SingleDeviceAlertsInit',
                kwargs={'page_type': page_type, 'device_id' : device_id, 'service_name' : 'ping'},
                current_app='alert_center'
            ),
            'page_type': page_type,
            'live_poll_config' : json.dumps(LIVE_POLLING_CONFIGURATION),
            'is_util_tab' : int(is_util_tab)
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

# This function returns last x months 'years,month' tuple & all months name, alias list
def getLastXMonths(months_count):

    # month name list
    all_months_list = [
        {"name" : "jan","alias" : "Jan"},
        {"name" : "feb","alias" : "Feb"},
        {"name" : "march","alias" : "March"},
        {"name" : "april","alias" : "April"},
        {"name" : "may","alias" : "May"},
        {"name" : "june","alias" : "June"},
        {"name" : "july","alias" : "July"},
        {"name" : "aug","alias" : "Aug"},
        {"name" : "sept","alias" : "Sept"},
        {"name" : "oct","alias" : "Oct"},
        {"name" : "nov","alias" : "Nov"},
        {"name" : "dec","alias" : "Dec"}
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

    return (last_six_months_list, all_months_list)

# Sector Spot Dashboard ListView
class SectorDashboard(ListView):
    """
    The Class based view to get sector dashboard page requested.

    """

    model = SpotDashboard
    template_name = 'performance/sector_dashboard.html'

    def get_context_data(self, **kwargs):

        context = super(SectorDashboard, self).get_context_data(**kwargs)
        # Sector Info Headers
        sector_headers = [
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', },
            {'mData': 'sector_sector_configured_on', 'sTitle': 'Sector Configured On', 'sWidth': 'auto', },
            {'mData': 'sector_device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', }
        ]


        ul_last_six_month_headers = list()
        sia_last_six_month_headers = list()
        augt_last_six_month_headers = list()
        months_index_list = list()

        # Get Last Six Month List
        last_six_months_list, \
        months_list = getLastXMonths(6)

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
                {'mData': 'ul_issue_'+str(i+1), 'sTitle': month_alias, 'sWidth': 'auto', 'bSortable': False}
            )
            # Last Six Month SIA Headers
            sia_last_six_month_headers.append(
                {'mData': 'sia_'+str(i+1), 'sTitle': month_alias, 'sWidth': 'auto', 'bSortable': False}
            )
            # Last Six Month Augmentation Headers
            augt_last_six_month_headers.append(
                {'mData': 'augment_'+str(i+1), 'sTitle': month_alias, 'sWidth': 'auto', 'bSortable': False}
            )

        table_headers = []
        table_headers += sector_headers
        table_headers += ul_last_six_month_headers
        table_headers += sia_last_six_month_headers
        table_headers += augt_last_six_month_headers

        context['table_headers'] = json.dumps(table_headers)
        context['months_index'] = json.dumps(months_index_list)
        return context

class SectorDashboardListing(BaseDatatableView):
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

    def prepare_results(self,qs):

        report_resultset = []

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
                    report_object['ul_issue_'+columns_concat_counter] = '<i class="fa fa-circle text-danger"> </i>'
                else:
                    report_object['ul_issue_'+columns_concat_counter] = '-'


                # Condition for Augmentation
                if data['augment_'+columns_concat_counter]:
                    report_object['augment_'+columns_concat_counter] = '<i class="fa fa-circle text-danger"> </i>'
                else:
                    report_object['augment_'+columns_concat_counter] = '-'


                # Condition for SIA
                if data['sia_'+columns_concat_counter]:
                    report_object['sia_'+columns_concat_counter] = '<i class="fa fa-circle text-danger"> </i>'
                else:
                    report_object['sia_'+columns_concat_counter] = '-'

            #add data to report_resultset list
            report_resultset.append(report_object)

        return report_resultset

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value """

        sSearch = self.request.GET.get('sSearch', None)

        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                # avoid search on 'added_on'
                if column == 'added_on':
                    continue
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        request = self.request
        # Number of columns that are used in sorting
        try:
            i_sorting_cols = int(request.REQUEST.get('iSortingCols', 0))
        except Exception:
            i_sorting_cols = 0

        order = []

        order_columns = self.static_columns
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
            key_name=order[0][1:] if '-' in order[0] else order[0]
            sorted_device_data = sorted(qs, key=itemgetter(key_name), reverse= True if '-' in order[0] else False)
            return sorted_device_data
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
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
            'success': 1,
            'message': 'Devices Not Fetched Successfully.',
            'data': {
                'meta': {},
                'objects': []
            }
        }
        return HttpResponse(json.dumps(result), content_type="application/json")

        #not being used any longer

        # logged_in_user = request.user.userprofile
        #
        # if 'admin' in logged_in_user.role.values_list('role_name', flat=True):
        #     organizations = list(logged_in_user.organization.get_descendants(include_self=True))
        # else:
        #     organizations = [logged_in_user.organization]
        #
        # result['data']['objects'] += self.get_result(page_type, organizations)
        #
        # result['success'] = 1
        # result['message'] = 'Substation Devices Fetched Successfully.'
        # return HttpResponse(json.dumps(result), content_type="application/json")

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


def get_device_status_headers(page_type='network', type_of_device=None, technology=None):
    """
    This function returns device status headers as per given
    technology & type_of_device(sub_station, sector, backhaul, other)
    """
    headers_list = []

    if type_of_device in ['sector']:
        headers_list = [
            'BS Name',
            'Technology',
            'Type',
            'City',
            'State',
            'IP Address',
            'Planned Frequency(MHz)',
            'Frequency(MHz)'
        ]

        if technology in ['P2P', 'PTP', 'ptp', 'p2p']:
            headers_list.append('Customer Name')
            # For PTP near end devices add QOS BW column
            if page_type == 'customer':
                headers_list.append("Qos(Mbps)")
        elif technology.lower() in ['wimax']:
            headers_list.append('Sector ID')
            headers_list.append('PMP Port')
        else:
            headers_list.append('Sector ID')

    elif type_of_device in ['sub_station']:

        headers_list = [
            'BS Name',
            'SS Name',
            'Circuit ID',
            'Customer Name',
            'Technology',
            'Type',
            'City',
            'State',
            'Near End IP',
            'IP Address',
            'MAC Address',
            'Qos(Mbps)',
            'Frequency(MHz)'
        ]

    elif type_of_device in ['backhaul']:
        headers_list = [
            'IP',
            'Technology',
            'Type',
            'BS Name',
            'BH Port',
            'BH Capacity(mbps)',
            'City',
            'State'
        ]
    elif type_of_device in ['other']:
        headers_list = [
            'IP',
            'Technology',
            'Type',
            'BS Name',
            # 'BH Port',
            # 'BH Capacity(mbps)',
            'City',
            'State',
            # 'Aggregation Sw/Con',
            # 'POP Sw/Con',
            # 'PE IP',
            # 'BH Connectivity'
        ]

    return headers_list

def get_sector_device_status_data(page_type='network', device=None, technology=None, type=None):
    """
    This function returns sector device status data as per given params
    """
    sector_device_status_data = []

    # If device id or technology not exists then return blank list
    if not device or not technology or not type:
        return sector_device_status_data

    # Fetch Sector Info
    sector_objects = Sector.objects.select_related(
        'base_station__id',
        'base_station__alias',
        'base_station__city',
        'base_station__city__city_name',
        'base_station__state',
        'base_station__state__state_name',
        'frequency__value'
    ).filter(
        sector_configured_on=device.id
    )

    # Device Type URL
    device_type_url = reverse(
        'wizard-device-type-update',
        kwargs={'pk': type.id},
        current_app='device'
    ) if type else ""

    # Device Technology URL
    device_tech_url = reverse(
        'device_technology_edit',
        kwargs={'pk': technology.id},
        current_app='device'
    ) if technology else ""

    device_url = reverse(
        'device_edit',
        kwargs={'pk': device.id},
        current_app='device'
    ) if device else ""

    for sector in sector_objects:

        # Fetch BS name, city & state
        base_station_alias = sector.base_station.alias.upper() if sector.base_station else "N/A"
        bs_name_url = reverse(
            'base_station_edit',
            kwargs={'pk': sector.base_station.id},
            current_app='inventory'
        ) if sector.base_station.alias else ""

        # Get city of base station
        city_name = sector.base_station.city.city_name if sector.base_station.city else "N/A"
        city_url = reverse(
            'city_edit',
            kwargs={'pk': sector.base_station.city.id},
            current_app='device'
        ) if sector.base_station.city else ""
        
        # Get state of base station
        state_name = sector.base_station.state.state_name if sector.base_station.state else "N/A"
        state_url = reverse(
            'state_edit',
            kwargs={'pk': sector.base_station.state.id},
            current_app='device'
        ) if sector.base_station.state else ""

        if sector:

            planned_frequency = sector.planned_frequency if sector.planned_frequency else "N/A"
            
            frequency = sector.frequency.value if sector.frequency else "N/A"
            frequency_url = reverse(
                'device_frequency_edit',
                kwargs={'pk': sector.frequency.id},
                current_app='device'
            ) if sector.frequency else ""

            if technology.name.lower() in ['ptp', 'p2p']:
                try:
                    circuits = sector.circuit_set.get()
                    customer_name = circuits.customer.alias
                    customer_name_url = reverse('customer_edit', kwargs={'pk': circuits.customer.id}, current_app='inventory')
                except Exception as no_circuit:
                    # log.exception(no_circuit)
                    customer_name = "N/A"
                    customer_name_url = ""
            else:
                sector_id = sector.sector_id
                sector_id_url = reverse(
                    'sector_edit',
                    kwargs={'pk' : sector.id},
                    current_app='inventory'
                )

                if technology.name.lower() in ['wimax']:
                    try:
                        pmp_port = sector.sector_configured_on_port.alias.upper()
                        pmp_port_url = reverse(
                            'sector_edit',
                            kwargs={'pk': sector.id},
                            current_app='inventory'
                        )
                    except Exception as no_port:
                        # log.exception(no_port)
                        pmp_port = "N/A"
                        pmp_port_url = ""

                    try:
                        dr_ip = sector.dr_configured_on.ip_address
                        dr_ip_url = reverse(
                            'device_edit',
                            kwargs={'pk': sector.dr_configured_on.id},
                            current_app='device'
                        )
                    except Exception as no_dr:
                        # log.exception(no_dr.message)
                        dr_ip = None
                        dr_ip_url = ""


        if technology.name.lower() in ['ptp', 'p2p']:

            table_values = [
                {"val" : base_station_alias,"url" : bs_name_url},
                {"val" : technology.alias,"url" : device_tech_url},
                {"val" : type.alias,"url" : device_type_url},
                {"val" : city_name,"url" : city_url},
                {"val" : state_name,"url" : state_url},
                {"val" : device.ip_address,"url" : device_url},
                {"val" : planned_frequency,"url" : ""},
                {"val" : frequency,"url" : frequency_url},
                {"val" : customer_name,"url" : customer_name_url}
            ]


            if page_type == 'customer':
                # Get QOS BW from circuit 
                qos_bw = ""
                qos_bw_url = ""
                if circuits:
                    ptp_qos_val = "N/A"
                    if circuits.qos_bandwidth:
                        ptp_qos_val = circuits.qos_bandwidth/1000
                    qos_bw = ptp_qos_val
                    qos_bw_url = reverse(
                        'circuit_edit',
                        kwargs={'pk' : circuits.id},
                        current_app='inventory'
                    )

                table_values.append({"val" : qos_bw,"url" : qos_bw_url})

            sector_device_status_data.append(table_values)

        elif technology.name.lower() in ['wimax']:
            # table_values = []
            table_values = [
                {"val" : base_station_alias,"url" : bs_name_url},
                {"val" : technology.alias,"url" : device_tech_url},
                {"val" : type.alias,"url" : device_type_url},
                {"val" : city_name,"url" : city_url},
                {"val" : state_name,"url" : state_url},
                {"val" : device.ip_address,"url" : device_url},
                {"val" : planned_frequency,"url" : ""},
                {"val" : frequency,"url" : frequency_url},
                {"val" : sector_id,"url" : sector_id_url},
                {"val" : pmp_port,"url" : pmp_port_url}
            ]

            sector_device_status_data.append(table_values)

            if dr_ip:
                dr_ip += " (DR) "

                table_values = [
                    {"val" : base_station_alias,"url" : bs_name_url},
                    {"val" : technology.alias,"url" : device_tech_url},
                    {"val" : type.alias,"url" : device_type_url},
                    {"val" : city_name,"url" : city_url},
                    {"val" : state_name,"url" : state_url},
                    {"val" : dr_ip,"url" : dr_ip_url},
                    {"val" : planned_frequency,"url" : ""},
                    {"val" : frequency,"url" : frequency_url},
                    {"val" : sector_id,"url" : sector_id_url},
                    {"val" : pmp_port,"url" : pmp_port_url}
                ]

                sector_device_status_data.append(table_values)

        else:
            table_values = [
                {"val" : base_station_alias,"url" : bs_name_url},
                {"val" : technology.alias,"url" : device_tech_url},
                {"val" : type.alias,"url" : device_type_url},
                {"val" : city_name,"url" : city_url},
                {"val" : state_name,"url" : state_url},
                {"val" : device.ip_address,"url" : device_url},
                {"val" : planned_frequency,"url" : ""},
                {"val" : frequency,"url" : frequency_url},
                {"val" : sector_id,"url" : sector_id_url}
            ]
            
            sector_device_status_data.append(table_values)

    return sector_device_status_data


def get_sub_station_status_data(device=None, technology=None, type=None):
    """
    This function returns SS device status data as per given params
    """
    ss_device_status_data = []

    # If device id or technology not exists then return blank list
    if not device or not technology or not type:
        return ss_device_status_data


    substation_objects = device.substation_set.filter()

    if not len(substation_objects):
        return ss_device_status_data

    # Device Type URL
    device_type_url = reverse(
        'wizard-device-type-update',
        kwargs={'pk': type.id},
        current_app='device'
    ) if type else ""

    # Device Technology URL
    device_tech_url = reverse(
        'device_technology_edit',
        kwargs={'pk': technology.id},
        current_app='device'
    ) if technology else ""

    device_url = reverse(
        'device_edit',
        kwargs={'pk': device.id},
        current_app='device'
    ) if device else ""
    
    # Machine name on which device is alloted
    machine_name = device.machine.name if(device.machine and device.machine.name) else ""
    
    # Device name
    device_name = device.device_name if device else ""

    # Service & DS Name as per technology
    service_name = ''
    ds_name = ''
    if technology.name in ['PMP']:
        service_name = 'cambium_qos_invent'
        ds_name = 'bw_dl_sus_rate'
    elif technology.name in ['WiMAX']:
        service_name = 'wimax_qos_invent'
        ds_name = 'dl_qos'

    ss_qos_bw = "N/A"

    substation = substation_objects[0]
    customer_name = "N/A"

    if substation.circuit_set.exists():
        customer_id = Circuit.objects.filter(sub_station_id=substation.id).values('customer_id')
        customer_name = Customer.objects.filter(id=customer_id[0]["customer_id"])
        circuit = substation.circuit_set.get()

        sector = circuit.sector
        base_station = 'N/A'
        near_end_ip = 'N/A'
        near_end_ip_url = ''
        frequency_url = ''

        if sector:
            base_station = sector.base_station
            
            near_end_ip = sector.sector_configured_on.ip_address
            near_end_ip_url = reverse('device_edit', kwargs={'pk': sector.sector_configured_on.id}, current_app='device')
            
            planned_frequency = sector.planned_frequency if sector.planned_frequency else "N/A"

            frequency = sector.frequency.value if sector.frequency else "N/A"
            frequency_url = reverse(
                'device_frequency_edit',
                kwargs={'pk': sector.frequency.id},
                current_app='device'
            ) if sector.frequency else ""

        #Device Technology
        ss_type = type.alias if type else "N/A"
        ss_type_url = device_type_url

        # Handling for city name
        try:
            city_name = base_station.city.city_name
            city_url = reverse('city_edit', kwargs={'pk': base_station.city.id}, current_app='device')
        except Exception, e:
            city_name = 'N/A'
            city_url = ''

        # Handling for state name
        try:
            state_name = base_station.state.state_name
            state_url = reverse('state_edit', kwargs={'pk': base_station.state.id}, current_app='device')
        except Exception, e:
            state_name = 'N/A'
            state_url = ''

        display_mac_address = device.mac_address.upper() if device.mac_address else "N/A"

        display_bs_name = "N/A"
        display_bs_url = ""
        base_station_url = ''
        if base_station and base_station != 'N/A':
            display_bs_name = base_station.alias
            base_station_url = reverse('base_station_edit', kwargs={'pk': base_station.id}, current_app='inventory')

        # Condition to show Customer name as BS Name in case of backhaul
        if circuit.circuit_type:
            if circuit.circuit_type.lower().strip() in ['bh', 'backhaul']:
                display_bs_name = customer_name[0].alias
                display_bs_url = reverse('customer_edit', kwargs={'pk': customer_name[0].id}, current_app='inventory')
            else:
                display_bs_name = base_station.alias
                display_bs_url = base_station_url

        if display_bs_name:
            display_bs_name = display_bs_name.upper()

        # QOS BW will fetch from circuit in case of PTP else from polled params
        ss_qos_bw_url = ''
        if technology.name in ['PTP','P2P']:
            ss_qos_bw = circuit.qos_bandwidth/1000 if(circuit and circuit.qos_bandwidth) else "N/A"
            ss_qos_bw_url = reverse(
                'circuit_edit',
                kwargs={'pk' : circuit.id},
                current_app='inventory'
            )
        # Fetch QOS BW(Polled) in case of PMP & WiMAX SS
        elif technology.name in ['PMP','WiMAX']:
            ss_qos_bw = "N/A"
            if device_name and machine_name and service_name and ds_name:
                invent_status_obj = InventoryStatus.objects.filter(
                    device_name=device_name,
                    service_name=service_name,
                    data_source=ds_name
                ).order_by('-sys_timestamp').using(alias=machine_name)[:1]

                if invent_status_obj and invent_status_obj[0].current_value:
                    ss_qos_bw = invent_status_obj[0].current_value

        table_values = [
            {"val" : display_bs_name,"url" : base_station_url},
            {"val" : substation.alias,"url" : reverse('sub_station_edit', kwargs={'pk': substation.id}, current_app='inventory')},
            {"val" : circuit.circuit_id,"url" : reverse('circuit_edit', kwargs={'pk': circuit.id}, current_app='inventory')},
            {"val" : customer_name[0].alias,"url" : reverse('customer_edit', kwargs={'pk': customer_name[0].id}, current_app='inventory')},
            {"val" : technology.alias,"url" : device_tech_url},
            {"val" : ss_type,"url" : ss_type_url},
            {"val" : city_name,"url" : city_url},
            {"val" : state_name,"url" : state_url},
            {"val" : near_end_ip,"url" : near_end_ip_url},
            {"val" : device.ip_address,"url" : device_url},
            {"val" : display_mac_address,"url" : device_url if device.mac_address else ""},
            {"val" : ss_qos_bw,"url" : ss_qos_bw_url},
            {"val" : frequency,"url" : frequency_url}
        ]
        
        ss_device_status_data.append(table_values)

    return ss_device_status_data


def get_backhaul_status_data(device=None, technology=None, type=None, type_of_device='backhaul'):
    """
    This function returns Backhaul device status data which are connected 
    to atleast one BS as per given params
    """
    bh_device_status_data = []

    # If device id or technology not exists then return blank list
    if not device or not technology or not type:
        return bh_device_status_data

    # Device Type URL
    device_type_url = reverse(
        'wizard-device-type-update',
        kwargs={'pk': type.id},
        current_app='device'
    ) if type else ""

    # Device Technology URL
    device_tech_url = reverse(
        'device_technology_edit',
        kwargs={'pk': technology.id},
        current_app='device'
    ) if technology else ""

    device_url = reverse(
        'device_edit',
        kwargs={'pk': device.id},
        current_app='device'
    ) if device else ""

    if type_of_device == 'backhaul':
        backhaul_object = Backhaul.objects.select_related(
            'aggregator__ip_address',
            'pop__ip_address',
            'bh_configured_on__ip_address'
        ).filter(bh_configured_on=device.id)
    else:
        backhaul_object = Backhaul.objects.select_related(
            'aggregator__ip_address',
            'pop__ip_address',
            'bh_configured_on__ip_address'
        ).filter(
            Q(aggregator=device.id) | Q(pop=device.id) | Q(bh_switch=device.id)
        )

    bs_object = BaseStation.objects.filter(backhaul=backhaul_object[0].id)
    bh_ip_address = device.ip_address if device else ""
    # bh_ip_address = backhaul_object[0].bh_configured_on.ip_address if backhaul_object[0].bh_configured_on else ""
    bh_technology = technology.name if technology else "N/A"
    bh_type = type.name if type else "N/A"

    device_info_columns = [
        {"val" : bh_ip_address,"url" : device_url},
        {"val" : bh_technology,"url" : device_tech_url},
        {"val" : bh_type,"url" : device_type_url}
    ]

    if not device.backhaul.exists():
        # backhaul_edit_url = reverse('backhaul_edit', kwargs={'pk': backhaul_object[0].id}, current_app='inventory')
        # aggregator_ip = backhaul_object[0].aggregator.ip_address if backhaul_object[0].aggregator else "N/A"
        # pop_ip = backhaul_object[0].pop.ip_address if backhaul_object[0].pop else "N/A"
        # pe_ip = backhaul_object[0].pe_ip if backhaul_object[0].pe_ip else "N/A"
        # bh_connectivity = backhaul_object[0].bh_connectivity if backhaul_object[0].bh_connectivity else "N/A"

        bh_other_specific_columns = [
            # {"val" : aggregator_ip,"url" : backhaul_edit_url if aggregator_ip != 'N/A' else ""},
            # {"val" : pop_ip,"url" : backhaul_edit_url if pop_ip != 'N/A' else ""},
            # {"val" : pe_ip,"url" : backhaul_edit_url if pe_ip != 'N/A' else ""},
            # {"val" : bh_connectivity,"url" : backhaul_edit_url if bh_connectivity != 'N/A' else ""}
        ]

    if bs_object and len(bs_object):
        for bs_instance in bs_object:
            if bs_instance:
                # BS Name & Url
                bs_name = bs_instance.alias if(bs_instance and bs_instance.alias) else "N/A"
                bs_url = reverse('base_station_edit', kwargs={'pk': bs_instance.id}, current_app='inventory')

                # BH Port
                bh_port = bs_instance.bh_port_name if(bs_instance and bs_instance.bh_port_name) else "N/A"
                bh_capacity = bs_instance.bh_capacity if(bs_instance and bs_instance.bh_capacity) else "N/A"

                # Handling for city name
                try:
                    city_name = bs_instance.city.city_name if bs_instance.city else "N/A"
                    city_url = reverse('city_edit', kwargs={'pk': bs_instance.city.id}, current_app='device')
                except Exception, e:
                    city_name = 'N/A'
                    city_url = ''

                # Handling for state name
                try:
                    state_name = bs_instance.state.state_name if bs_instance.state else "N/A"
                    state_url = reverse('state_edit', kwargs={'pk': bs_instance.state.id}, current_app='device')
                except Exception, e:
                    state_name = 'N/A'
                    state_url = ''

                bs_bh_specific_columns = [
                    {"val" : bs_name,"url" : bs_url}
                ]

                if device.backhaul.exists():
                    bs_bh_specific_columns.append({"val" : bh_port,"url" : ""})
                    bs_bh_specific_columns.append({"val" : bh_capacity,"url" : ""})

                bs_bh_specific_columns.append({"val" : city_name,"url" : city_url},)
                bs_bh_specific_columns.append({"val" : state_name,"url" : state_url})


                table_values = device_info_columns + bs_bh_specific_columns

                if not device.backhaul.exists():
                    table_values = table_values + bh_other_specific_columns

                bh_device_status_data.append(table_values)

    return bh_device_status_data


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
                'objects': {
                    "headers" : list(),
                    "values" : list(),
                    "is_others_page" : 0
                }
            }
        }

        # Get Device Object
        device = Device.objects.get(id=device_id)
        # Get Device Technogy Object
        technology = DeviceTechnology.objects.get(id=device.device_technology)
        # Get Device Type Object
        type = DeviceType.objects.get(id=device.device_type)

        if device.sector_configured_on.exists():
            # Fetch the headers for 'sector'
            result['data']['objects']['headers'] = get_device_status_headers(page_type, 'sector',technology.name)

            # Fetch the data for 'sector'
            result['data']['objects']['values'] = get_sector_device_status_data(page_type, device, technology, type)

        elif device.substation_set.exists():

            # Fetch the headers for 'sector'
            result['data']['objects']['headers'] = get_device_status_headers(page_type, 'sub_station',"all")
            
            # Fetch the data for 'Sub Station'
            result['data']['objects']['values'] = get_sub_station_status_data(device, technology, type)

        # Case of backhaul
        elif device.backhaul.exists():

            type_of_device = "backhaul"

            result['data']['objects']['headers'] = get_device_status_headers(page_type, type_of_device,"")

            result['data']['objects']['values'] = get_backhaul_status_data(device, technology, type, type_of_device)

        elif (device.backhaul_switch.exists() or device.backhaul_pop.exists() or device.backhaul_aggregator.exists()) \
                and not (device.backhaul.exists()):

            type_of_device = "other"

            result['data']['objects']['headers'] = get_device_status_headers(page_type, type_of_device,"")
            result['data']['objects']['values'] = get_backhaul_status_data(device, technology, type, type_of_device)
            result['data']['objects']['is_others_page'] = 1

        result['success'] = 1
        result['message'] = 'Inventory Device Status Fetched Successfully.'
        return HttpResponse(json.dumps(result), content_type="application/json")


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
        is_util_tab = request.GET.get('is_util',0)

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

        # if is_util_tab is 1 then make isActive key of utilization_top_tab to 1
        if int(is_util_tab):
            result['data']['objects']['network_perf_tab']["isActive"] = 0
            result['data']['objects']['utilization_top_tab']["isActive"] = 1

        device = Device.objects.get(id=device_id)
        device_type = DeviceType.objects.get(id=device.device_type)

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
        return HttpResponse(json.dumps(result), content_type="application/json")


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
                    'age': None,
                    'last_down_time': None
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
            age = datetime.datetime.fromtimestamp(float(age)).strftime(DATE_TIME_FORMAT)

        if last_down_time:
            last_down_time = datetime.datetime.fromtimestamp(float(last_down_time)).strftime(DATE_TIME_FORMAT)

        self.result = {
            'success': 1,
            'message': 'Service Status Fetched Successfully',
            'data': {
                'meta': {},
                'objects': {
                    'perf': None,
                    'last_updated': None,
                    'status': severity.lower().strip() if severity else None,
                    'age': age,
                    'last_down_time': last_down_time
                }
            }
        }

        if service_data_source_type in ['pl', 'rta']:
            performance_data_query_set = NetworkStatus.objects.filter(device_name=inventory_device_name,
                                                            service_name=service_name,
                                                            data_source=service_data_source_type,
            ).using(alias=inventory_device_machine_name)

        elif "rf" == service_name and "rf" == service_data_source_type:
            performance_data_query_set = None

        elif service_name in ['util', 'topology', 'availability'] or service_data_source_type in ['util', 'availability', 'topology']:
            performance_data_query_set = None

        elif '_status' in service_name:
            performance_data_query_set = Status.objects.filter(device_name=inventory_device_name,
                                                     service_name=service_name,
                                                     data_source=service_data_source_type,
            ).using(alias=inventory_device_machine_name)

        elif '_invent' in service_name:
            performance_data_query_set = InventoryStatus.objects.filter(device_name=inventory_device_name,
                                                              service_name=service_name,
                                                              data_source=service_data_source_type
            ).using(alias=inventory_device_machine_name)

        elif '_kpi' in service_name:
            performance_data_query_set = UtilizationStatus.objects.filter(device_name=inventory_device_name,
                                                              service_name=service_name,
                                                              data_source=service_data_source_type
            ).using(alias=inventory_device_machine_name)

        else:
            performance_data_query_set = ServiceStatus.objects.filter(device_name=inventory_device_name,
                                                            service_name=service_name,
                                                            data_source=service_data_source_type,
            ).using(alias=inventory_device_machine_name)

        if performance_data_query_set:
            performance_data = performance_data_query_set #.using(alias=inventory_device_machine_name)
            #log.debug(performance_data)
                                                           #nocout_utils.nocout_query_results(query_set=performance_data_query_set,
                                                           #      using=inventory_device_machine_name)
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

        return HttpResponse(json.dumps(self.result), content_type="application/json")

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
        # GET param to check the the data is requested for live data or historical data
        data_for = self.request.GET.get('data_for','live')

        # for wimax devices special case
        dr_device = None

        # for topology service these would come in handy
        sector_object = None
        sector_device = None

        date_format = DATE_TIME_FORMAT
        device = Device.objects.get(id=int(device_id))
        inventory_device_name = device.device_name
        inventory_device_machine_name = device.machine.name  # Device Machine Name required in Query to fetch data.

        # date time settings
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        isSet, start_date, end_date = perf_utils.get_time(start_date, end_date, date_format)
        if not isSet:
            end_date = float(format(datetime.datetime.now(), 'U'))
            start_date = float(format(datetime.datetime.now() + datetime.timedelta(minutes=-180), 'U'))


        if service_data_source_type.strip() not in ['topology', 'rta', 'pl', 'availability', 'rf']:
            sds_name = service_name.strip() + "_" + service_data_source_type.strip()
        else:
            sds_name = service_data_source_type.strip()

        # to check if data source would be displayed as a chart or as a table
        #
        show_chart = False
        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]['type'] == 'table':
            show_chart = False
        else:
            show_chart = True

        # check for the formula
        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]['formula']:
            formula = SERVICE_DATA_SOURCE[sds_name]['formula']
        else:
            formula = None

        # Update 'default' machine name in case of historical data request
        if data_for and data_for not in ['live']:
            if(
                '_kpi' not in service_name
                and
                service_data_source_type not in ['availability', 'topology']
                and
                data_for in ['bi_hourly', 'hourly', 'daily', 'weekly', 'monthly', 'yearly']
            ):
                inventory_device_machine_name = 'default'

        parameters = {
            'model': PerformanceService,
            'start_time': start_date,
            'end_time': end_date,
            'devices': [inventory_device_name],
            'services': [service_name],
            'sds': [service_data_source_type]
        }

        if data_for:
            if data_for == 'bi_hourly':
                parameters.update({
                    'model' : PerformanceServiceBiHourly
                })
            elif data_for == 'hourly':
                parameters.update({
                    'model' : PerformanceServiceHourly
                })
            elif data_for == 'daily':
                parameters.update({
                    'model' : PerformanceServiceDaily
                })
            elif data_for == 'weekly':
                parameters.update({
                    'model' : PerformanceServiceWeekly
                })
            elif data_for == 'monthly':
                parameters.update({
                    'model' : PerformanceServiceMonthly
                })
            elif data_for == 'yearly':
                parameters.update({
                    'model' : PerformanceServiceYearly
                })

        # test once for technology
        try:
            technology = DeviceTechnology.objects.get(id=device.device_technology)
        except:
            return HttpResponse(json.dumps(self.result), content_type="application/json")
        try:
            # test now for sector
            if technology and technology.name.lower() in ['wimax'] and device.sector_configured_on.exists():
                dr_devices = device.sector_configured_on.filter()
                sector_device = device
                for dr_d in dr_devices:
                    dr_device = dr_d.dr_configured_on # there can only be a DR device
                # append dr device here only
                parameters['devices'].append(dr_device.device_name)
                # parameters updated with all devices
        except:
            pass  # no dr site

        if service_data_source_type in ['pl', 'rta']:
            if data_for:
                if data_for == 'bi_hourly':
                    parameters.update({
                        'model' : PerformanceNetworkBiHourly
                    })
                elif data_for == 'hourly':
                    parameters.update({
                        'model' : PerformanceNetworkHourly
                    })
                elif data_for == 'daily':
                    parameters.update({
                        'model' : PerformanceNetworkDaily
                    })
                elif data_for == 'weekly':
                    parameters.update({
                        'model' : PerformanceNetworkWeekly
                    })
                elif data_for == 'monthly':
                    parameters.update({
                        'model' : PerformanceNetworkMonthly
                    })
                elif data_for == 'yearly':
                    parameters.update({
                        'model' : PerformanceNetworkYearly
                    })
                else:
                    parameters.update({
                        'model': PerformanceNetwork
                    })
            else:
                parameters.update({
                    'model': PerformanceNetwork
                })

            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name)

            if dr_device:
                result = self.dr_performance_data_result(performance_data=performance_data,
                                                         sector_device=device,
                                                         dr_device=dr_device
                                                         )
            else:

                result = self.get_performance_data_result(performance_data)

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

            if data_for:
                if data_for == 'bi_hourly':
                    parameters.update({
                        'model' : PerformanceNetworkBiHourly
                    })
                elif data_for == 'hourly':
                    parameters.update({
                        'model' : PerformanceNetworkHourly
                    })
                elif data_for == 'daily':
                    parameters.update({
                        'model' : PerformanceNetworkDaily
                    })
                elif data_for == 'weekly':
                    parameters.update({
                        'model' : PerformanceNetworkWeekly
                    })
                elif data_for == 'monthly':
                    parameters.update({
                        'model' : PerformanceNetworkMonthly
                    })
                elif data_for == 'yearly':
                    parameters.update({
                        'model' : PerformanceNetworkYearly
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
                result = self.get_performance_data_result(performance_data)

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

            if dr_device:
                result = self.dr_performance_data_result(performance_data=performance_data,
                                                         sector_device=device,
                                                         dr_device=dr_device,
                                                         availability=True
                                                         )
            else:

                result = self.get_performance_data_result(performance_data, data_source="availability")

        elif "topology" in service_name or service_data_source_type in ['topology']:
            if not isSet:
                end_date = format(datetime.datetime.now(), 'U')
                start_date = format(datetime.datetime.now() + datetime.timedelta(weeks=-1), 'U')
            #for wimax devices there can be a case of DR
            #we need to incorporate the DR devices as well

            try:
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
            if dr_device:
                result = self.get_topology_result(performance_data,
                                                  dr_ip=dr_device.ip_address,
                                                  technology=technology,
                                                  sectors=sector_object
                )
            else:
                result = self.get_topology_result(performance_data,
                                                  technology=technology,
                                                  sectors=sector_object
                )


        elif '_status' in service_name:
            if not isSet:
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

            if data_for:
                if data_for == 'daily':
                    parameters.update({
                        'model' : PerformanceStatusDaily
                    })
                elif data_for == 'weekly':
                    parameters.update({
                        'model' : PerformanceStatusWeekly
                    })
                elif data_for == 'monthly':
                    parameters.update({
                        'model' : PerformanceStatusMonthly
                    })
                elif data_for == 'yearly':
                    parameters.update({
                        'model' : PerformanceStatusYearly
                    })

            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name)

            result = self.get_perf_table_result(performance_data)

        elif '_invent' in service_name:
            if not isSet:
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

            if data_for:
                if data_for == 'daily':
                    parameters.update({
                        'model' : PerformanceInventoryDaily
                    })
                elif data_for == 'weekly':
                    parameters.update({
                        'model' : PerformanceInventoryWeekly
                    })
                elif data_for == 'monthly':
                    parameters.update({
                        'model' : PerformanceInventoryMonthly
                    })
                elif data_for == 'yearly':
                    parameters.update({
                        'model' : PerformanceInventoryYearly
                    })

            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name)

            result = self.get_perf_table_result(performance_data)

        elif '_kpi' in service_name:

            parameters.update({
                'model': Utilization,
                'start_time': start_date,
                'end_time': end_date,
                'services': [service_name],
                'sds': [service_data_source_type]
            })

            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name)

            if not show_chart:  # show the table
                result = self.get_perf_table_result(
                    performance_data=performance_data,
                    formula=formula
                )
            else:  # show the chart
                if dr_device:
                    result = self.dr_performance_data_result(performance_data=performance_data,
                                                             sector_device=device,
                                                             dr_device=dr_device
                                                             )
                else:
                    result = self.get_performance_data_result(performance_data)

        else:
            performance_data = self.get_performance_data(
                **parameters
            ).using(alias=inventory_device_machine_name)

            if not show_chart: # show the table
                result = self.get_perf_table_result(
                    performance_data=performance_data,
                    formula=formula
                )
            else: # show the chart
                if dr_device:
                    result = self.dr_performance_data_result(performance_data=performance_data,
                                                             sector_device=device,
                                                             dr_device=dr_device
                                                             )
                else:
                    result = self.get_performance_data_result(performance_data)

        return HttpResponse(json.dumps(result), content_type="application/json")

    def get_performance_data(self, model=None, start_time=None, end_time=None, devices=None, services=None, sds=None):
        if services:
            performance_data = model.objects.filter(
                device_name__in=devices,
                service_name__in=services,
                data_source__in=sds,
                sys_timestamp__gte=start_time,
                sys_timestamp__lte=end_time
            ).order_by('sys_timestamp')
        else:
            performance_data = model.objects.filter(
                device_name__in=devices,
                data_source__in=sds,
                sys_timestamp__gte=start_time,
                sys_timestamp__lte=end_time
            ).order_by('sys_timestamp')

        return performance_data

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

    def get_perf_table_result(self, performance_data, formula=None):

        result_data, aggregate_data = list(), dict()
        for data in performance_data:
            temp_time = data.sys_timestamp

            if temp_time in aggregate_data:
                continue
            else:
                aggregate_data[temp_time] = data.sys_timestamp

                value = eval(str(formula) + "(" + str(data.current_value) + ")") \
                                if formula \
                                else data.current_value

                result_data.append({
                    # 'date': datetime.datetime.fromtimestamp(float(data.sys_timestamp)).strftime("%d/%B/%Y"),
                    'time': datetime.datetime.fromtimestamp(float(data.sys_timestamp)).strftime(DATE_TIME_FORMAT),
                    'ip_address': data.ip_address,
                    'value': value,
                })

        self.result['success'] = 1
        self.result[
            'message'] = 'Device Performance Data Fetched Successfully To Plot Table.' if result_data else 'No Record Found.'
        self.result['data']['objects']['table_data'] = result_data
        self.result['data']['objects']['table_data_header'] = ['time', 'ip_address', 'value']
        return self.result

    def get_topology_result(self, performance_data, dr_ip=None, technology=None, sectors=None):
        """
        Getting the current topology of any elements of the network
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

                        vlan = self.ss_vlan_performance_data_result(technology=technology,
                                                                    ss_device_object=connected_device,
                                                                    machine=machine
                        )

                        packet_loss, latency, status_since = self.ss_network_performance_data_result(
                            ss_device_object=connected_device,
                            machine=machine
                        )

                last_updated = datetime.datetime.fromtimestamp(
                                float(data.sys_timestamp)
                                ).strftime(DATE_TIME_FORMAT)

                show_ip_address = data.ip_address
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
                    'up_down_since': status_since,
                    'last_updated': last_updated,
                })

        #here we will append the rest of the SS
        #which are not in topology now
        #but are connected to the sector
        if sectors:
            not_connected_ss = SubStation.objects.filter(circuit__sector__in=sectors
            ).exclude(device__ip_address__in=connected_ss_ip).prefetch_related('circuit_set')

            circuit_id = 'NA'
            customer_name = 'NA'
            sector_ip = 'NA'
            sector_mac = 'NA'
            sector_id = None

            for ss in not_connected_ss:
                vlan = self.ss_vlan_performance_data_result(technology=technology,
                                                                    ss_device_object=ss.device,
                                                                    machine=ss.device.machine.name
                        )
                packet_loss, latency, status_since = self.ss_network_performance_data_result(
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
                        'up_down_since': status_since,
                        'last_updated': last_updated,
                    })


        self.result['success'] = 1
        self.result['message'] = 'Device Data Fetched Successfully.' if result_data else 'No Record Found.'
        self.result['data']['objects']['table_data'] = result_data
        self.result['data']['objects']['table_data_header'] = [#'device_name',
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
                                                               'up_down_since',
                                                               'last_updated'
        ]
        return self.result

    def ss_vlan_performance_data_result(self, technology, ss_device_object, machine):
        """
        provide the SS vlan data
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
        """
        packet_loss = None
        latency = None
        status_since = None

        perf_data = NetworkStatus.objects.filter(device_name=ss_device_object.device_name
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

        #last time down results
        severity, a = device_current_status(device_object=ss_device_object)
        age = a['age'] if(a and 'age' in a) else ""
        down = a['down'] if(a and 'down' in a) else ""
        #last time pl = 100 results
        if age:
            status_since = datetime.datetime.fromtimestamp(float(age)
                ).strftime(DATE_TIME_FORMAT)


        return packet_loss, latency, status_since

    def rf_performance_data_result(self, performance_data_ss, performance_data_bs):
        """
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
                        valid_end_time = data.sys_timestamp + 30 #30 seconds buffer added
                        valid_start_time = data.sys_timestamp - 330 #30 seconds buffer added
                        ##in between 5 minutes the bs result will come before ss result
                        bs_lat = performance_data_bs.filter(sys_timestamp__gte=valid_start_time,
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

            chart_data = [{'name': "RF Latency",
                            'data': data_list,
                            'type': 'area',
                            'valuesuffix': ' ms ',
                            'valuetext': ' ms '
                          }
                        ]
            if rf_prop['show_ss']:
                chart_data.append(
                    {'name': "SS Latency",
                        'data': ss_data_list,
                        'type': 'spline',
                        'valuesuffix': ' ms ',
                        'valuetext': ' ms '
                    }
                )
            if rf_prop['show_bs']:
                chart_data.append(
                    {'name': "BS Latency",
                        'data': bs_data_list,
                        'type': 'spline',
                        'valuesuffix': ' ms ',
                        'valuetext': ' ms '
                    }
                )


        self.result['success'] = 1
        self.result['data']['objects']['chart_data'] = chart_data
        self.result['message'] = 'Device Performance Data Fetched Successfully To Plot Graphs.'

        if(not chart_data or len(chart_data) == 0):
            self.result['message'] = 'No Data'

        return self.result

    def dr_performance_data_result(self, performance_data, sector_device, dr_device, availability=False):
        """
        specially for dr devices
        """


        sector_performance_data = performance_data.filter(device_name=sector_device.device_name)
        dr_performance_data = performance_data.filter(device_name=dr_device.device_name)

        sector_result = self.performance_data_result(performance_data=sector_performance_data)
        dr_result = self.performance_data_result(performance_data=dr_performance_data)
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
                        if sds_name not in ['pl','rta']:
                            sds_name = str(data.service_name).strip() + "_" + str(data.data_source).strip()

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

                        sds_inverted = False

                        if sds_name in SERVICE_DATA_SOURCE and SERVICE_DATA_SOURCE[sds_name]["is_inverted"]:
                            sds_inverted = SERVICE_DATA_SOURCE[sds_name]["is_inverted"]

                        if not sds_inverted:
                            compare_point = lambda p1, p2, p3: chart_color \
                                if abs(p1) < abs(p2) \
                                else ('#FFE90D'
                                      if abs(p2) < abs(p1) < abs(p3)
                                      else ('#FF193B' if abs(p3) < abs(p1)
                                            else chart_color
                                )
                            )
                        else:
                            compare_point = lambda p1, p2, p3: chart_color \
                                if abs(p1) > abs(p2) \
                                else ('#FFE90D'
                                      if abs(p2) > abs(p1) > abs(p3)
                                      else ('#FF193B' if abs(p3) > abs(p1)
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
                                       'valuetext': result['data']['objects']['valuetext'],
                                       'is_inverted': sds_inverted
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
                                "color": '#90ee7e',
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

    # TODO: Mix charts support
    
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

                    sds_name = str(data.data_source).strip()
                    if sds_name not in ['availability']:
                        if sds_name not in ['pl','rta']:
                            sds_name = str(data.service_name).strip() + "_" + str(data.data_source).strip()

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
                                      else ('#FF193B' if abs(p3) < abs(p1)
                                            else chart_color
                                )
                            )
                        else:
                            compare_point = lambda p1, p2, p3: chart_color \
                                if abs(p1) > abs(p2) \
                                else ('#FFE90D'
                                      if abs(p2) > abs(p1) > abs(p3)
                                      else ('#FF193B' if abs(p3) > abs(p1)
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
                                       'valuetext': self.result['data']['objects']['valuetext'],
                                       'is_inverted': self.result['data']['objects']['is_inverted']
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

        service_names = list()
        sds_names = list()
        service_data_sources = dict()
        bh_data_sources = None

        colors = ['#1BEAFF', '#A60CE8']

        # if is_sector:
        dr_device = None

        isSet, start_date, end_date = perf_utils.get_time(start_date, end_date, date_format)
        if not isSet:
            end_date = format(datetime.datetime.now(), 'U')
            start_date = format(datetime.datetime.now() + datetime.timedelta(minutes=-180), 'U')

        device = Device.objects.get(id=device_id)
        device_type = DeviceType.objects.get(id=device.device_type)
        # specially for DR devices
        technology = DeviceTechnology.objects.get(id=device.device_technology)

        if device.sector_configured_on.exists():
            is_sector = True
            is_bh = False
            is_ss = False
        elif device.backhaul.exists():
            is_sector = False
            is_bh = True
            is_ss = False
        elif device.substation_set.exists():
            is_sector = False
            is_bh = False
            is_ss = True
        else:
            return HttpResponse(json.dumps(result), content_type="application/json")



        device_type_services = device_type.service.filter(name__icontains=service_name
        ).prefetch_related('servicespecificdatasource_set')

        services = device_type_services.values('name',
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
            service_data_sources[temp_s_name, temp_sds_name] = appnd + \
                                                               service_data_sources[temp_s_name, temp_sds_name]



        performance = PerformanceService.objects.filter(
            device_name=device.device_name,
            service_name__in=service_names,
            data_source__in=sds_names,
            sys_timestamp__gte=start_date,
            sys_timestamp__lte=end_date).using(
                alias=device.machine.name).order_by('sys_timestamp')

        chart_data = []
        color = {}
        temp_chart_data = {}
        for data in performance:
            try:
                if (data.service_name, data.data_source) not in temp_chart_data:
                    # color[data.service_name, data.data_source] = perf_utils.color_picker()
                    c = SERVICE_DATA_SOURCE[
                                    data.service_name.strip() + "_" +data.data_source.strip()
                                ]['chart_color']
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
                        'type': SERVICE_DATA_SOURCE[
                                    data.service_name.strip() + "_" +data.data_source.strip()
                                ]['type']
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


@nocout_utils.cache_for(120)  # just for 2 minutes cache this. short running query
def device_current_status(device_object):
    """
    Device UP Status
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
        data_source__in=['pl', 'rta']
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


@nocout_utils.cache_for(300) #for 5 minutes cache this. long running query
def device_last_down_time(device_object):
    """

    :param device_object:
    :return:
    """
    #first check the current PL state of the device
    s, a = device_current_status(device_object=device_object)

    return a['down']  # return the last down time of the device
