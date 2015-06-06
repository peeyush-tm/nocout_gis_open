# -*- coding: utf-8 -*-

import datetime
# faster json processing module
import ujson as json

from django.db.models.query import ValuesQuerySet
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from device.models import Device, DeviceTechnology
# For SIA Listing
from alert_center.models import CurrentAlarms, ClearAlarms, HistoryAlarms

from performance.models import EventNetwork, EventService

from operator import itemgetter
# Import performance utils gateway class
from performance.utils.util import PerformanceUtilsGateway

# Import inventory utils gateway class
from inventory.utils.util import InventoryUtilsGateway

# Import alert_center utils gateway class
from alert_center.utils.util import AlertCenterUtilsGateway

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

from django.utils.dateformat import format

# nocout project settings # TODO: Remove the HARDCODED technology IDs
from nocout.settings import DATE_TIME_FORMAT, TRAPS_DATABASE

import logging
logger = logging.getLogger(__name__)

# Create instance of 'InventoryUtilsGateway' class
inventory_utils = InventoryUtilsGateway()

# Create instance of 'AlertCenterUtilsGateway' class
alert_utils = AlertCenterUtilsGateway()

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


class CustomerAlertDetailHeaders(ListView):
    """
    A generic class view for the network alert details view

    """
    model = EventService
    template_name = 'alert_center/customer_alert_details_list.html'

    def get_context_data(self, **kwargs):

        """

        :param kwargs:
        :return:
        """
        starting_headers = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True}
        ]

        specific_headers = [
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'customer_name', 'sTitle': 'Customer', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True}
        ]

        common_headers = [
            {'mData': 'near_end_ip', 'sTitle': 'Near End IP', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'bs_name', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'city', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'state', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True}
        ]

        polled_headers = [
            {'mData': 'data_source_name', 'sTitle': 'Data Source Name', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'current_value', 'sTitle': 'Value', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True, "sSortDataType": "dom-text", "sType": "numeric"}
        ]

        other_headers = [
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'Status Since', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': False}
        ]

        datatable_headers = starting_headers
        datatable_headers += specific_headers
        datatable_headers += common_headers
        datatable_headers += polled_headers
        datatable_headers += other_headers

        context = {'datatable_headers': json.dumps(datatable_headers)}

        return context


class GetCustomerAlertDetail(BaseDatatableView):
    """
    Generic Class Based View for the Alert Center Customer Listing Tables.
    """
    is_polled = False
    model = EventService

    columns = [
        'severity',
        'sector_id',
        'circuit_id',
        'customer_name',
        'near_end_ip',
        'ip_address',
        'device_type',
        'bs_name',
        'city',
        'state',
        'data_source_name',
        'current_value',
        'sys_timestamp'
    ]

    order_columns = columns

    polled_columns = [
        "id",
        "ip_address",
        "service_name",
        "data_source",
        "device_name",
        "severity",
        "current_value",
        "max_value",
        "min_value",
        "sys_timestamp",
        "age"
    ]

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        organizations = nocout_utils.logged_in_user_organizations(self)

        return self.get_initial_query_set_data(organizations=organizations)

    def get_initial_query_set_data(self, **kwargs):
        """
        Generic function required to fetch the initial data with respect 
        to the page_type parameter in the get request requested.

        :param kwargs:
        :return: list of devices
        """

        page_type = "customer"

        required_value_list = ['id', 'machine__name', 'device_name', 'ip_address']

        if not DeviceTechnology.objects.filter(name__iexact=self.request.GET.get('data_tab').strip).exists():
            return []

        device_tab_technology = self.request.GET.get('data_tab')

        devices = inventory_utils.filter_devices(
            organizations=kwargs['organizations'],
            data_tab=device_tab_technology,
            page_type=page_type,
            required_value_list=required_value_list
        )

        # machines dict
        machines = self.prepare_machines(devices)
        # machines dict

        # prepare the polled results
        perf_results = self.prepare_polled_results(devices, machine_dict=machines)
        # this is query set with complete polled result

        map_result = alert_utils.map_results(perf_results, devices)

        # this function is for mapping to GIS inventory
        prepared_devices = self.prepare_devices(map_result, perf_results)
        # this function is for mapping to GIS inventory

        # query set for customer devices of the technology : P2P, WiMAX, PMP
        return prepared_devices

    def prepare_devices(self, qs, perf_results):
        """


        :param perf_results:
        :param qs:
        :return:
        """
        page_type = "customer"
        device_tab_technology = self.request.GET.get('data_tab')
        type_rf = None

        if device_tab_technology not in DeviceTechnology.objects.all().values_list('name', flat=True):
            device_tab_technology = None

            if page_type == 'network':
                type_rf = 'sector'
            elif page_type == 'customer':
                type_rf = 'ss'
            else:
                type_rf = None

        # Create instance of 'PerformanceUtilsGateway' class
        perf_utils = PerformanceUtilsGateway()

        return perf_utils.prepare_gis_devices(
            qs,
            page_type,
            monitored_only=True,
            technology=device_tab_technology,
            type_rf=type_rf
        )

    def prepare_machines(self, qs):
        """

        :param qs:
        """
        device_list = []
        for device in qs:
            device_list.append({
                'device_name': device['device_name'],
                'device_machine': device['machine_name'],
                'id': device['id'],
                'ip_address': device['ip_address']
            })

        return inventory_utils.prepare_machines(device_list)

    def prepare_polled_results(self, qs, machine_dict=None):
        """
        preparing polled results
        after creating static inventory first
        :param machine_dict:
        :param qs:
        """

        device_tab_technology = self.request.GET.get('data_tab')

        search_table = "performance_servicestatus"

        data_sources_list = list()

        extra_query_condition = ' AND `{0}`.`severity` in ("down","warning","critical","warn","crit") '

        sorted_device_list = list()

        #Fetching the data for the device w.r.t to their machine.
        for machine, machine_device_list in machine_dict.items():
            device_list = list()
            performance_data = list()
            performance_data = alert_utils.raw_prepare_result(
                performance_data=performance_data,
                machine=machine,
                table_name=search_table,
                devices=machine_device_list,
                data_sources=data_sources_list,
                columns=self.polled_columns,
                condition=extra_query_condition if extra_query_condition else None
            )

            device_list = alert_utils.prepare_raw_alert_results(performance_data=performance_data)

            sorted_device_list += device_list

        if device_tab_technology.strip().lower() in ['wimax']:
            search_table = "performance_inventorystatus"
            extra_query_condition = ' AND `{0}`.`severity` in ("down","warning","critical","warn","crit") '
            for machine, machine_device_list in machine_dict.items():
                device_list = list()
                performance_data = list()
                performance_data = alert_utils.raw_prepare_result(
                    performance_data=performance_data,
                    machine=machine,
                    table_name=search_table,
                    devices=machine_device_list,
                    data_sources=data_sources_list,
                    columns=self.polled_columns,
                    condition=extra_query_condition if extra_query_condition else None
                )

                device_list = alert_utils.prepare_raw_alert_results(performance_data=performance_data)

                sorted_device_list += device_list

        return sorted_device_list

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return queryset
        """
        page_type = "customer"
        if qs:
            service_tab_name = 'down'
            for dct in qs:
                dct.update(
                    action='<a href="/alert_center/{2}_alert/{1}/{0}/" title="Device Alerts">\
                           <i class="fa fa-warning text-warning">&nbsp;</i></a>'
                           '<a href="/performance/{2}_live/{0}/" title="Device Performance">\
                           <i class="fa fa-bar-chart-o text-info">&nbsp;</i></a>'
                           '<a href="/device/{0}" title="Device Inventory">\
                           <i class="fa fa-dropbox text-muted">&nbsp;</i>\
                           </a>'.format(dct['id'], service_tab_name, page_type)
                )
                dct = alert_utils.common_prepare_results(dct)

            return qs

        return []

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return result_list:
        """

        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            if len(sSearch) > 3:
                search_data = qs
                result_list = list()
                for dictionary in search_data:
                    x = json.dumps(dictionary)
                    dictionary = json.loads(x)
                    for data in dictionary:
                        if dictionary[data]:
                            condition_1 = isinstance(dictionary[data], unicode)
                            condition_2 = isinstance(dictionary[data], str)
                            if (condition_1 or condition_2) and (dictionary not in result_list):
                                if sSearch.encode('utf-8').lower() in dictionary[data].encode('utf-8').lower():
                                    result_list.append(dictionary)
                            else:
                                if sSearch == dictionary[data] and dictionary not in result_list:
                                    result_list.append(dictionary)

                return result_list
        return qs

    def ordering(self, qs):
        """
        sorting for the table
        :param qs:
        """
        return nocout_utils.nocout_datatable_ordering(self, qs, self.columns)

    def paging(self, qs):
        """

        :param qs : query set contains all the required data mapped properly
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
        The maine function call to fetch, search, prepare and display the data on the data table.

        :param kwargs:
        :param args:
        """

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        # filtering the query set
        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # order by column
        qs = self.ordering(qs)
        # pagination enabled
        qs = self.paging(qs)  # Removing pagination as of now to render all the data at once.

        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }
        return ret


class NetworkAlertDetailHeaders(ListView):
    """
    A generic class view for the network alert details view

    """
    model = EventNetwork
    template_name = 'alert_center/network_alert_details_list.html'

    def get_context_data(self, **kwargs):

        """

        :param kwargs:
        :return:
        """
        starting_headers = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True}
        ]

        specific_headers = [
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'customer_name', 'sTitle': 'Customer', 'sWidth': 'auto', 'bSortable': True}
        ]

        ul_issue_specific_headers = [
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'refer', 'sTitle': 'Affected Sectors', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'customer_name', 'sTitle': 'Customer', 'sWidth': 'auto', 'bSortable': True}
        ]

        bh_specific_headers = [
            {'mData': 'alias', 'sTitle': 'BH Alias', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'bh_port_name', 'sTitle': 'BH Port Name', 'sWidth': 'auto', 'bSortable': True}
        ]

        common_headers = [
            {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'bs_name', 'sTitle': 'BS Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'city', 'sTitle': 'City', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'state', 'sTitle': 'State', 'sWidth': 'auto', 'bSortable': True}
        ]

        bh_specific_headers = [
            {'mData': 'bh_connectivity', 'sTitle': 'Onnet/Offnet', 'sWidth': 'auto', 'bSortable': True}
        ]

        polled_headers = [
            {'mData': 'data_source_name', 'sTitle': 'Data Source Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'current_value', 'sTitle': 'Value', 'sWidth': 'auto',
             'bSortable': True, "sSortDataType": "dom-text", "sType": "numeric"}
        ]

        other_headers = [
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'Status Since', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'auto', 'bSortable': False}
        ]

        datatable_headers = []
        datatable_headers += starting_headers
        datatable_headers += specific_headers
        datatable_headers += common_headers
        datatable_headers += polled_headers
        datatable_headers += other_headers

        backhaul_headers = []
        backhaul_headers += starting_headers
        backhaul_headers += specific_headers
        backhaul_headers += common_headers
        backhaul_headers += bh_specific_headers
        backhaul_headers += polled_headers
        backhaul_headers += other_headers

        ul_issue_datatable_headers = []
        ul_issue_datatable_headers += starting_headers
        ul_issue_datatable_headers += ul_issue_specific_headers
        ul_issue_datatable_headers += common_headers
        ul_issue_datatable_headers += polled_headers
        ul_issue_datatable_headers += other_headers

        bh_dt_headers = []
        bh_dt_headers += starting_headers
        bh_dt_headers += bh_specific_headers
        bh_dt_headers += common_headers
        bh_dt_headers += polled_headers
        bh_dt_headers += other_headers

        # Sector Utilization Headers
        sector_util_hidden_headers = [
            {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'sector__sector_id', 'sTitle': 'Sector', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'organization__alias', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
        ]

        sector_util_common_headers = [
            {'mData': 'sector__base_station__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'sector__base_station__state__state_name', 'sTitle': 'State', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'sector__base_station__city__city_name', 'sTitle': 'City', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__ip_address', 'sTitle': 'BS IP', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'sector_sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'current_out_per', 'sTitle': '% UL Utilization', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'current_in_per', 'sTitle': '% DL Utilization', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'severity', 'sTitle': 'Status', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'Aging (seconds)', 'sWidth': 'auto', 'bSortable': True},
        ]

        sector_utils_headers = []
        sector_utils_headers += sector_util_hidden_headers
        sector_utils_headers += sector_util_common_headers

        bh_util_hidden_headers = [
            {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'organization__alias', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
        ]

        bh_util_common_headers = [
            {'mData': 'backhaul__bh_configured_on__ip_address', 'sTitle': 'BH IP', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'backhaul__alias', 'sTitle': 'Backhaul', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'basestation__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'bh_port_name', 'sTitle': 'Configured On Port', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'backhaul__bh_configured_on__device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'basestation__city__city_name', 'sTitle': 'BS City', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'basestation__state__state_name', 'sTitle': 'BS State', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'severity', 'sTitle': 'Status', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'Aging', 'sWidth': 'auto', 'bSortable': True},
        ]

        bh_utils_headers = []
        bh_utils_headers += bh_util_hidden_headers
        bh_utils_headers += bh_util_common_headers

        context = {
            'datatable_headers': json.dumps(datatable_headers),
            'backhaul_headers': json.dumps(backhaul_headers),
            'bh_utils_headers': json.dumps(bh_utils_headers),
            'ul_issue_headers': json.dumps(ul_issue_datatable_headers),
            'bh_headers': json.dumps(bh_dt_headers),
            'sector_utils_headers': json.dumps(sector_utils_headers)
        }

        return context


class GetNetworkAlertDetail(BaseDatatableView):
    """
    Generic Class Based View for the Alert Center Network  Detail Listing Tables.

    """
    model = EventNetwork
    columns = [
        'device_name',
        'device_type',
        'machine_name',
        'site_name',
        'ip_address',
        'severity',
        'current_value',
        'sys_time',
        'sys_date',
        'description'
    ]

    order_columns = columns

    polled_columns = [
        "id",
        "ip_address",
        "service_name",
        "device_name",
        "data_source",
        "severity",
        "current_value",
        "max_value",
        "min_value",
        "sys_timestamp",
        "age"
    ]

    data_sources = []
    table_name = "performance_servicestatus"

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        organizations = nocout_utils.logged_in_user_organizations(self)

        required_value_list = ['id', 'machine__name', 'device_name', 'ip_address']

        page_type = self.request.GET.get('page_type', "network")

        if self.request.GET.get("data_source"):
            tab_id = self.request.GET.get("data_source")
        else:
            return []

        is_bh = False

        if tab_id:
            device_list = []
            if tab_id == "P2P":
                technology = [tab_id]
            elif tab_id in "WiMAX":
                technology = [tab_id]
            elif tab_id == "PMP":
                technology = [tab_id]
            elif tab_id == "Temperature":
                #for handelling the temperature alarms
                #temperature alarms would be for WiMAX
                technology = ["WiMAX"]
                self.data_sources = ['fan_temp', 'acb_temp']
            elif tab_id == "Temperature_bh":
                is_bh = True
                technology = None
                page_type = "other"
                self.data_sources = ['temperature']
            elif tab_id == "WiMAXULIssue":
                # technology = [int(WiMAX.ID), int(PMP.ID)]
                technology = ["WiMAX"]
                self.data_sources = ['pmp1_ul_issue', 'pmp2_ul_issue']
                self.table_name = 'performance_utilizationstatus'
                # Add 'refer column' in case of ULIssue
                self.polled_columns.append('refer')
            elif tab_id == "PMPULIssue":
                # technology = [int(WiMAX.ID), int(PMP.ID)]
                technology = ["PMP"]
                self.data_sources = ['bs_ul_issue']
                self.table_name = 'performance_utilizationstatus'
                # Add 'refer column' in case of ULIssue
                self.polled_columns.append('refer')
            elif tab_id in ["Backhaul", "Backhaul_Down", "Backhaul_PD", "Backhaul_RTA"]:
                technology = None
                is_bh = True
                page_type = "other"
                self.table_name = 'performance_networkstatus'
                # Onnet/Offnet column added for Backhaul tab
                self.columns.append("bh_connectivity")
                self.data_sources = ''
            else:
                return []

            if not is_bh:
                for techno in technology:
                    device_list += inventory_utils.filter_devices(
                        organizations=organizations,
                        data_tab=techno,
                        page_type=page_type,
                        required_value_list=required_value_list
                    )
            else:
                device_list += inventory_utils.filter_devices(
                    organizations=organizations,
                    data_tab=None,
                    page_type=page_type,
                    required_value_list=required_value_list,
                    other_type='backhaul'
                )

            return device_list

        else:
            return []

    def prepare_polled_results(self, qs, machine_dict=None):
        """
        preparing polled results
        after creating static inventory first
        :param machine_dict:
        :param qs:
        """

        search_table = self.table_name

        extra_query_condition = ' AND `{0}`.`severity` in ("down","warning","critical","warn","crit") '

        # Add extra condition for UL Issues listing
        if self.data_sources and 'ul_issue' in ', '.join(self.data_sources):
            extra_query_condition += " AND `{0}`.`current_value` > 0 "

        get_param = self.request.GET.get("data_source")

        if get_param:
            if get_param in ["Backhaul_Down"]:
                extra_query_condition += " AND `{0}`.`current_value` = 100 AND `{0}`.`data_source` = 'pl'"
            elif get_param in ["Backhaul_PD"]:
                extra_query_condition += " AND `{0}`.`current_value` != 100 AND `{0}`.`data_source` = 'pl'"
            elif get_param in ["Backhaul_RTA"]:
                extra_query_condition += " AND `{0}`.`data_source` = 'rta'"

        sorted_device_list = list()

        #Fetching the data for the device w.r.t to their machine.
        for machine, machine_device_list in machine_dict.items():
            device_list = list()
            performance_data = list()
            performance_data = alert_utils.raw_prepare_result(
                performance_data=performance_data,
                machine=machine,
                table_name=search_table,
                devices=machine_device_list,
                data_sources=self.data_sources,
                columns=self.polled_columns,
                condition=extra_query_condition if extra_query_condition else None
            )

            device_list = alert_utils.prepare_raw_alert_results(performance_data=performance_data)

            sorted_device_list += device_list

        return sorted_device_list

    def prepare_devices(self, qs, perf_results):
        """


        :param perf_results:
        :param qs:
        :return:
        """
        page_type = self.request.GET.get('page_type', "network")

        # Create instance of 'PerformanceUtilsGateway' class
        perf_utils = PerformanceUtilsGateway()

        return perf_utils.prepare_gis_devices(qs, page_type)

    def prepare_machines(self, qs):
        """

        :param qs:
        """
        device_list = []
        for device in qs:
            device_list.append({
                'device_name': device['device_name'],
                'device_machine': device['machine_name'],
                'id': device['id'],
                'ip_address': device['ip_address']
            })

        return inventory_utils.prepare_machines(device_list)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return queryset.
        """
        page_type = self.request.GET.get('page_type', "network")
        ds_param = self.request.GET.get("data_source", '')
        perf_page_type = page_type
        if qs:
            service_tab_name = 'down'
            # In case of backhaul tab update page type to 'other'
            if 'backhaul' in ds_param.lower():
                perf_page_type = 'other'
                try:
                    if ds_param.lower().split("_")[1] == 'rta':
                        service_tab_name = 'latency'
                    elif ds_param.lower().split("_")[1] == 'pl':
                        service_tab_name = 'packet_drop'
                    else:
                        service_tab_name = 'down'
                except Exception, e:
                    service_tab_name = 'down'

            for dct in qs:
                dct.update(
                    action='<a href="/alert_center/{2}_alert/{1}/{0}/" title="Device Alerts">\
                            <i class="fa fa-warning text-warning"></i></a>\
                            <a href="/performance/{3}_live/{0}/" title="Device Performance">\
                            <i class="fa fa-bar-chart-o text-info"></i></a>\
                            <a href="/device/{0}" title="Device Inventory">\
                            <i class="fa fa-dropbox text-muted"></i>\
                            </a>'.format(dct["id"], service_tab_name, page_type, perf_page_type)
                )

                dct = alert_utils.common_prepare_results(dct)

        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, prepare and display the data on the data table.

        :param kwargs:
        :param args:
        """

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        #machines dict
        machines = self.prepare_machines(qs)
        #machines dict

        #prepare the polled results
        perf_results = self.prepare_polled_results(qs, machine_dict=machines)
        # this is query set with complete polled result

        qs = alert_utils.map_results(perf_results, qs)

        #this function is for mapping to GIS inventory
        qs = self.prepare_devices(qs, perf_results)
        #this function is for mapping to GIS inventory

        # number of records before filtering
        total_records = len(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # qs = self.ordering(qs)
        # qs = self.paging(qs) #Removing pagination as of now to render all the data at once.
        # if the qs is empty then JSON is unable to serialize the 
        # empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }
        return ret


# **************************************** Latency *********************************************
class AlertCenterListing(ListView):
    """
    Class Based View to render Alert Center Network Listing page with latency, packet drop
    down and service impact alert tabs.

    """
    model = EventNetwork
    template_name = 'alert_center/alerts_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        :param kwargs:
        """

        context = super(AlertCenterListing, self).get_context_data(**kwargs)

        page_type = self.kwargs.get('page_type', 'network')

        data_source = self.kwargs.get('data_source', 'packet_drop')

        data_tab = self.kwargs.get('data_tab')

        data_source_title = "Latency Avg (ms) " \
            if data_source == "latency" \
            else ("value".title() if data_source in ["service"] else "packet drop (%)".title())

        severity_headers = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True}
        ]

        ckt_customer_headers = [
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'customer_name', 'sTitle': 'Customer Name', 'sWidth': 'auto', 'bSortable': True}
        ]

        # List of headers which are shown first in grid for PTP Tab in both pages(network & customer)
        ptp_starting_headers = []
        ptp_starting_headers += ckt_customer_headers

        # List of headers which are shown first in grid for PMP & WiMAX Tab in both pages(network & customer)
        pmp_wimax_starting_headers = []
        pmp_wimax_starting_headers += [
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'bSortable': True}
        ]

        # If customer page then add near end ip column to all stating columns list
        if page_type == 'customer':
            near_ip_column = [{
                'mData': 'near_end_ip',
                'sTitle': 'Near End IP',
                'sWidth': 'auto',
                'bSortable': True
            }]

            ptp_starting_headers += near_ip_column

            pmp_wimax_starting_headers += ckt_customer_headers
            pmp_wimax_starting_headers += near_ip_column

        # List of common headers for all pages of alerts listing
        common_headers = [
            {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'bs_name', 'sTitle': 'BS Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'city', 'sTitle': 'City', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'state', 'sTitle': 'State', 'sWidth': 'auto', 'bSortable': True},
        ]

        bh_specific_headers = [
            {'mData': 'bh_connectivity', 'sTitle': 'Onnet/Offnet', 'sWidth': 'auto', 'bSortable': True}
        ]

        # Page specific & polled headers list initialization
        polled_headers = []

        if data_source == 'service':
            polled_headers += [{
                'mData': 'data_source_name',
                'sTitle': 'Data Source',
                'sWidth': 'auto',
                'bSortable': True
            }]

        polled_headers += [{
            'mData': 'current_value',
            'sTitle': '{0}'.format(data_source_title),
            'sWidth': 'auto',
            'bSortable': True,
            "sSortDataType": "dom-text",
            "sType": "numeric"
        }]

        if data_source == "latency":
            polled_headers += [
                {
                    'mData': 'max_value',
                    'sTitle': 'Latency Max (ms)',
                    'sWidth': 'auto',
                    'bSortable': True,
                    "sSortDataType": "dom-text",
                    "sType": "numeric"
                },
                {
                    'mData': 'min_value',
                    'sTitle': 'Latency Min (ms)',
                    'sWidth': 'auto',
                    'bSortable': True,
                    "sSortDataType": "dom-text",
                    "sType": "numeric"
                }
            ]

        other_headers = [
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'Status Since', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'auto', 'bSortable': False}
        ]
        
        # Initialize headers list for all tabs
        ptp_datatable_headers = []
        pmp_wimax_datatable_headers = []
        bh_datatable_headers = []

        ptp_datatable_headers += severity_headers
        ptp_datatable_headers += ptp_starting_headers
        ptp_datatable_headers += common_headers
        ptp_datatable_headers += polled_headers
        ptp_datatable_headers += other_headers

        pmp_wimax_datatable_headers += severity_headers
        pmp_wimax_datatable_headers += pmp_wimax_starting_headers
        pmp_wimax_datatable_headers += common_headers
        pmp_wimax_datatable_headers += polled_headers
        pmp_wimax_datatable_headers += other_headers

        # Pass bh_datatable_headers only in case of 'network' page
        if page_type == 'network':
            bh_datatable_headers += severity_headers
            bh_datatable_headers += common_headers
            bh_datatable_headers += bh_specific_headers
            bh_datatable_headers += polled_headers
            bh_datatable_headers += other_headers

        context['ptp_datatable_headers'] = json.dumps(ptp_datatable_headers)
        context['pmp_wimax_datatable_headers'] = json.dumps(pmp_wimax_datatable_headers)
        context['bh_datatable_headers'] = json.dumps(bh_datatable_headers)
        context['data_source'] = " ".join(self.kwargs['data_source'].split('_')).title()
        context['url_data_source'] = self.kwargs['data_source']
        context['page_type'] = page_type
        context['data_tab'] = data_tab
        return context


class AlertListingTable(BaseDatatableView):
    """
    Generic Class Based View for the Alert Center Network Listing Tables.

    """
    is_polled = False
    model = EventNetwork
    columns = []
    order_columns = columns

    polled_columns = [
        "id",
        "ip_address",
        "service_name",
        "data_source",
        "device_name",
        "severity",
        "current_value",
        "max_value",
        "min_value",
        "sys_timestamp",
        "age"
    ]

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        else:

            if not len(self.columns):
                self.prepare_initial_params()

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

        page_type = self.request.GET.get('page_type', 'network')

        other_type = self.request.GET.get('other_type', None)

        required_value_list = ['id', 'machine__name', 'device_name', 'ip_address']

        device_tab_technology = self.request.GET.get('data_tab')

        devices = inventory_utils.filter_devices(
            organizations=kwargs['organizations'],
            data_tab=device_tab_technology,
            page_type=page_type,
            other_type=other_type,
            required_value_list=required_value_list
        )

        #machines dict
        machines = self.prepare_machines(devices)

        # prepare the polled results, this is query set with complete polled result
        perf_results = self.prepare_polled_results(devices, machine_dict=machines)

        # this function is for mapping to GIS inventory
        map_result = alert_utils.map_results(perf_results, devices)

        #this function is for mapping to GIS inventory
        prepared_devices = self.prepare_devices(map_result, perf_results)

        return prepared_devices

    def prepare_devices(self, qs, perf_results):
        """


        :param perf_results:
        :param qs:
        :return:
        """
        page_type = self.request.GET.get('page_type')
        device_tab_technology = self.request.GET.get('data_tab')
        type_rf = None

        if device_tab_technology not in DeviceTechnology.objects.all().values_list('name', flat=True):
            device_tab_technology = None

            if page_type == 'network':
                type_rf = 'sector'
            elif page_type == 'customer':
                type_rf = 'ss'
            else:
                type_rf = None

        # Create instance of 'PerformanceUtilsGateway' class
        perf_utils = PerformanceUtilsGateway()

        return perf_utils.prepare_gis_devices(
            qs,
            page_type,
            monitored_only=True,
            technology=device_tab_technology,
            type_rf=type_rf
        )

    def prepare_machines(self, qs):
        """

        :param qs:
        """
        device_list = []
        for device in qs:
            device_list.append({
                'device_name': device['device_name'],
                'device_machine': device['machine_name'],
                'id': device['id'],
                'ip_address': device['ip_address']
            })

        return inventory_utils.prepare_machines(device_list)

    def prepare_polled_results(self, qs, machine_dict=None):
        """
        preparing polled results
        after creating static inventory first
        :param machine_dict:
        :param qs:
        """
        data_source = self.request.GET.get('data_source')

        device_list, data_sources_list = list(), list()

        search_table = "performance_networkstatus"

        extra_query_condition = None

        if data_source == 'latency':
            extra_query_condition = ' AND (`{0}`.`current_value` > 0 ) '
            extra_query_condition += ' AND `{0}`.`severity` in ("down","warning","critical","warn","crit") '
            data_sources_list = ['rta']
        elif data_source == 'packet_drop':
            data_sources_list = ['pl']
            extra_query_condition = ' AND (`{0}`.`current_value` BETWEEN 1 AND 99 ) '
            extra_query_condition += ' AND `{0}`.`severity` in ("down","warning","critical","warn","crit") '
        elif data_source == 'down':
            data_sources_list = ['pl']
            extra_query_condition = ' AND (`{0}`.`current_value` >= 100 ) '
            extra_query_condition += ' AND `{0}`.`severity` in ("down") '
        elif data_source == 'service':
            extra_query_condition = ' AND `{0}`.`severity` in ("down","warning","critical","warn","crit") '
            search_table = "performance_servicestatus"

        required_data_columns = self.polled_columns

        sorted_device_list = list()

        #Fetching the data for the device w.r.t to their machine.
        for machine, machine_device_list in machine_dict.items():
            device_list = list()
            performance_data = list()
            performance_data = alert_utils.raw_prepare_result(
                performance_data=performance_data,
                machine=machine,
                table_name=search_table,
                devices=machine_device_list,
                data_sources=data_sources_list,
                columns=required_data_columns,
                condition=extra_query_condition if extra_query_condition else None
            )

            device_list = alert_utils.prepare_raw_alert_results(performance_data=performance_data)

            sorted_device_list += device_list

        return sorted_device_list

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return queryset
        """

        if qs:
            data_unit = "%"
            service_tab = 'down'
            # figure out which tab call is made.
            data_source = self.request.GET.get('data_source', '')
            page_type = self.request.GET.get('page_type')
            if 'latency' == data_source:
                service_tab = 'latency'
                data_unit = "ms"
            elif 'packet_drop' == data_source:
                service_tab = 'packet_drop'
            elif 'service' == data_source:
                data_unit = ''
                service_tab = 'service'

            for dct in qs:
                try:
                    dct.update(current_value=float(dct["current_value"]))
                except:
                    dct.update(current_value=dct["current_value"] + " " + data_unit)
                dct.update(
                    action='<a href="/alert_center/{2}_alert/{1}/{0}/" title="Device Alerts">\
                            <i class="fa fa-warning text-warning"></i></a>\
                            <a href="/performance/{2}_live/{0}/" title="Device Performance">\
                            <i class="fa fa-bar-chart-o text-info"></i></a>\
                            <a href="/device/{0}" title="Device Inventory">\
                            <i class="fa fa-dropbox text-muted"></i>\
                            </a>'.format(dct['id'], service_tab, page_type)
                )

                dct = alert_utils.common_prepare_results(dct)

            return qs

        return []

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        :param qs:
        :return result_list:
        """

        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list = list()
            for dictionary in qs:
                dictionary = json.loads(json.dumps(dictionary))
                for data in dictionary:
                    if dictionary[data]:
                        condition_1 = isinstance(dictionary[data], unicode)
                        condition_2 = isinstance(dictionary[data], str)
                        if (condition_1 or condition_2) and (dictionary not in result_list):
                            if sSearch.encode('utf-8').lower() in dictionary[data].encode('utf-8').lower():
                                result_list.append(dictionary)
                        else:
                            if sSearch == dictionary[data] and dictionary not in result_list:
                                result_list.append(dictionary)

            return result_list
        return qs

    def ordering(self, qs):
        """
        sorting for the table
        :param qs:
        """
        return nocout_utils.nocout_datatable_ordering(self, qs, self.columns)

    def prepare_initial_params(self):
        """
        The function prepares the columns & order_columns as per kwargs & 
        get params used in all function within the class
        """

        page_type = self.request.GET.get('page_type', 'network')
        data_source = self.request.GET.get('data_source', 'packet_drop')
        data_tab = self.request.GET.get('data_tab', 'P2P')

        severity_columns = ['severity']
        ckt_customer_column = ['circuit_id', 'customer_name']
        common_columns = ['ip_address', 'device_type', 'bs_name', 'city', 'state']

        starting_columns = []
        if data_tab in ['P2P', 'PTP', 'PTP-BH', 'PTP_BH']:
            starting_columns += ckt_customer_column
        else:
            starting_columns += ['sector_id']

        if page_type == 'customer':
            near_ip_column = ['near_end_ip']

            if data_tab not in ['P2P', 'PTP', 'PTP-BH', 'PTP_BH']:
                starting_columns += ckt_customer_column

            starting_columns += near_ip_column

        polled_columns = []

        polled_columns += ['current_value']

        if data_source == "latency":
            polled_columns += ['max_value', 'min_value']

        other_columns = ['sys_timestamp', 'age', 'action']

        self.columns = []
        self.columns += severity_columns
        self.columns += starting_columns
        self.columns += common_columns
        self.columns += polled_columns
        self.columns += other_columns

        self.order_columns = self.columns

        return True

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, prepare and display the data on the data table.

        :param kwargs:
        :param args:
        """

        request = self.request
        self.initialize(*args, **kwargs)

        if not len(self.columns):
            self.prepare_initial_params()

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        # filtering the query set
        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # order by column
        qs = self.ordering(qs)
        # pagination enabled
        qs = self.paging(qs)  # Removing pagination as of now to render all the data at once.

        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }

        return ret


# This class initialize the single device alert page with appropriate params
class SingleDeviceAlertsInit(ListView):

    model = EventNetwork
    template_name = 'alert_center/single_device_alert.html'

    def get_context_data(self, **kwargs):

        """

        :param kwargs:
        :return:
        """
        data_source = self.kwargs['data_source']
        page_type = self.kwargs['page_type']
        device_id = self.kwargs['device_id']

        context = super(SingleDeviceAlertsInit, self).get_context_data(**kwargs)

        column_list_1 = [
            {"mData": "ip_address", "sTitle": "IP Address", "sWidth": "auto"},
            {"mData": "service_name", "sTitle": "Service Name", "sWidth": "auto"},
        ]

        ds_column_list = [
            {"mData": "data_source", "sTitle": "Data Source", "sWidth": "auto"},
        ]

        polling_alerts_specific_headers = [
            {"mData": "machine_name", "sTitle": "Machine", "sWidth": "auto"},
            {"mData": "site_name", "sTitle": "Site", "sWidth": "auto"},
        ]

        severity_column_list = [
            {"mData": "severity", "sTitle": "Severity", "sWidth": "auto"},
        ]

        current_val_list = [
            {"mData": "current_value", "sTitle": "Current Value", "sWidth": "auto"},
        ]

        column_list_2 = [
            {"mData": "sys_timestamp", "sTitle": "Alert Datetime", "sWidth": "auto"},
            {"mData": "description", "sTitle": "Description", "sWidth": "auto"}
        ]

        ping_specific_columns = [
            {"mData": "latency", "sTitle": "Latency", "sWidth": "auto"},
            {"mData": "packet_loss", "sTitle": "Packet Loss", "sWidth": "auto"},
        ]

        table_headers = []
        table_headers += column_list_1
        table_headers += ds_column_list
        table_headers += severity_column_list
        table_headers += current_val_list
        table_headers += column_list_2

        ping_table_headers = []
        ping_table_headers += column_list_1
        ping_table_headers += severity_column_list
        ping_table_headers += ping_specific_columns
        ping_table_headers += column_list_2

        polling_alerts_table_headers = []
        polling_alerts_table_headers += column_list_1
        polling_alerts_table_headers += polling_alerts_specific_headers
        polling_alerts_table_headers += severity_column_list
        polling_alerts_table_headers += current_val_list
        polling_alerts_table_headers += column_list_2

        device_obj = Device.objects.get(id=device_id)
        device_name = device_obj.device_name
        device_alias = device_obj.device_alias + "(" + device_obj.ip_address + ")"
        #  GET Technology of current device
        device_technology_name = DeviceTechnology.objects.get(id=device_obj.device_technology).name
        
        is_dr_device = device_obj.dr_configured_on.exists()

        # Create Context Dict
        context['table_headers'] = json.dumps(table_headers)
        context['ping_table_headers'] = json.dumps(ping_table_headers)
        context['polling_alerts_headers'] = json.dumps(polling_alerts_table_headers)
        context['current_device_id'] = device_id
        context['page_type'] = page_type
        context['data_source'] = data_source
        # Device Inventory page url
        context['inventory_page_url'] = reverse(
            'device_edit',
            kwargs={'pk': device_id},
            current_app='device'
        )
        # Single Device perf page url
        context['perf_page_url'] = reverse(
            'SingleDevicePerf',
            kwargs={
                'page_type': page_type,
                'device_id': device_id
            },
            current_app='performance'
        )
        # Inventory device status url
        inventory_status_url = reverse(
            'DeviceStatusUrl',
            kwargs={
                'page_type': page_type,
                'device_id': device_id
            },
            current_app='performance'
        )

        # service status url
        service_status_url = reverse(
            'GetServiceStatus',
            kwargs={
                'service_name': 'ping',
                'service_data_source_type': 'pl',
                'device_id': device_id
            },
            current_app='performance'
        )

        context['get_status_url'] = inventory_status_url
        context['service_status_url'] = service_status_url

        context['device_technology_name'] = device_technology_name
        context['device_alias'] = device_alias
        context['current_device_name'] = device_name

        context['is_dr_device'] = is_dr_device

        return context


class SingleDeviceAlertsListing(BaseDatatableView):

    model = EventNetwork
    required_columns = [
        "ip_address",
        "service_name",
        "data_source",
        "severity",
        "current_value",
        "sys_timestamp",
        "description"
    ]

    public_params = {}

    order_columns = required_columns

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value
        :param qs:
        """

        sSearch = self.request.GET.get('sSearch', None)

        if sSearch:

            if self.public_params['service_name'] == 'ping':

                # raw query is required here so as to get data
                query = alert_utils.ping_service_query(
                    self.public_params['device_name'],
                    self.public_params['start_date'],
                    self.public_params['end_date']
                )

                condition_str = ''
                final_query = ''

                counter = 0

                for column in self.required_columns:
                    counter += 1

                    if counter == len(self.required_columns):
                        condition_str += " data_tab."+column+" LIKE '"+sSearch+"%' "
                    else:
                        condition_str += " data_tab."+column+" LIKE '"+sSearch+"%' or "

                if condition_str:
                    final_query += 'select data_tab.* from ('+query+') as data_tab where '+condition_str
                else:
                    final_query += query

                qs = self.nocout_utils.fetch_raw_result(final_query, self.public_params['machine_name'])

            else:
                if self.public_params['service_name'] == 'service':
                    # Update model for 'service'
                    self.model = EventService

                query = []

                # Create query condition string
                pre_condition_query = "("
                pre_condition_query += "Q(device_name="+str(self.public_params['device_name'])+")"

                if self.public_params['service_name'] == 'latency':
                    pre_condition_query += " & Q(data_source='rta')"
                elif self.public_params['service_name'] == 'packet_drop':
                    pre_condition_query += " & Q(data_source='pl')"
                elif self.public_params['service_name'] == 'down':
                    pre_condition_query += " & Q(data_source='pl')"
                    pre_condition_query += " & Q(current_value=100)"
                    pre_condition_query += " & Q(severity='DOWN')"

                pre_condition_query += " & Q({0}__gte={1})".format('sys_timestamp', self.public_params['start_date'])
                pre_condition_query += " & Q({0}__lte={1})".format('sys_timestamp', self.public_params['end_date'])

                pre_condition_query += ")"

                query.append(pre_condition_query)

                # Create the search condition string
                search_condition_query = ''
                exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
                counter = 0
                for column in self.required_columns:
                    counter += 1

                    if counter == len(self.required_columns):
                        search_condition_query += " Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ") "
                    else:
                        search_condition_query += " Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ") | "

                if search_condition_query:
                    search_condition_query = "("+search_condition_query+")"
                    query.append(search_condition_query)

                exec_query += " & ".join(query)
                exec_query += ").values(*" + str(self.required_columns) + ")"
                exec_query += ".using(alias='" + self.public_params['machine_name'] + "')"

                exec exec_query
        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        if not len(self.public_params):
            self.initialize_params()

        if self.public_params['service_name'] == 'service':

            report_resultset = EventService.objects.filter(
                device_name=self.public_params['device_name'],
                sys_timestamp__gte=self.public_params['start_date'],
                sys_timestamp__lte=self.public_params['end_date']
            ).order_by("-sys_timestamp").values(*self.required_columns).using(
                alias=self.public_params['machine_name']
            )

        elif self.public_params['service_name'] == 'ping':

            # raw query is required here so as to get data
            query = alert_utils.ping_service_query(
                self.public_params['device_name'],
                self.public_params['start_date'],
                self.public_params['end_date']
            )
            report_resultset = self.nocout_utils.fetch_raw_result(query, self.public_params['machine_name'])

        elif self.public_params['service_name'] == 'latency':

            report_resultset = EventNetwork.objects.filter(
                device_name=self.public_params['device_name'],
                data_source='rta',
                sys_timestamp__gte=self.public_params['start_date'],
                sys_timestamp__lte=self.public_params['end_date']
            ).order_by("-sys_timestamp").values(*self.required_columns).using(
                alias=self.public_params['machine_name']
            )

        elif self.public_params['service_name'] == 'packet_drop':

            report_resultset = EventNetwork.objects.filter(
                device_name=self.public_params['device_name'],
                data_source='pl',
                sys_timestamp__gte=self.public_params['start_date'],
                sys_timestamp__lte=self.public_params['end_date']
            ).order_by("-sys_timestamp").values(*self.required_columns).using(
                alias=self.public_params['machine_name']
            )

        elif self.public_params['service_name'] == 'down':

            report_resultset = EventNetwork.objects.filter(
                device_name=self.public_params['device_name'],
                data_source='pl',
                current_value=100,  # need to show up and down both
                severity='DOWN',
                sys_timestamp__gte=self.public_params['start_date'],
                sys_timestamp__lte=self.public_params['end_date']
            ).order_by("-sys_timestamp").values(*self.required_columns).using(
                alias=self.public_params['machine_name']
            )

        else:

            report_resultset = []

        return report_resultset

    def prepare_results(self, qs):
        """
        Preparing Final dataset for rendering the data table.
        :param qs:
        """
        final_list = list()
        if qs:
            for data in qs:
                single_dict = {}
                single_dict = data
                single_dict['sys_timestamp'] = datetime.datetime.fromtimestamp(
                    float(data["sys_timestamp"])
                ).strftime(DATE_TIME_FORMAT)

                # add data to report_resultset list
                final_list.append(single_dict)
        else:
            final_list = qs

        return final_list

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        :param qs:
        """
        return nocout_utils.nocout_datatable_ordering(self, qs, self.required_columns)

    def initialize_params(self):
        """
        This function initializes global variables used within the class
        """

        device_id = self.kwargs['device_id']
        device_obj = Device.objects.get(id=device_id)
        device_name = device_obj.device_name
        machine_name = device_obj.machine.name
        service_name = self.request.GET.get('service_name', 'ping')

        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')

        if len(start_date) and len(end_date) and 'undefined' not in [start_date, end_date]:
            try:
                start_date = float(start_date)
                end_date = float(end_date)
            except Exception, e:
                start_date_object = datetime.datetime.strptime(start_date, "%d-%m-%Y %H:%M:%S")
                end_date_object = datetime.datetime.strptime(end_date, "%d-%m-%Y %H:%M:%S")
                start_date = format(start_date_object, 'U')
                end_date = format(end_date_object, 'U')
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

        # Prepare columns array as per service name

        if service_name in ['ping']:
            self.required_columns = [
                "ip_address",
                "service_name",
                "severity",
                "latency",
                "packet_loss",
                "sys_timestamp",
                "description"
            ]
        elif service_name in ['service']:
            self.required_columns = [
                "ip_address",
                "service_name",
                "machine_name",
                "site_name",
                "severity",
                "current_value",
                "sys_timestamp",
                "description"
            ]

        self.public_params = {
            'service_name': service_name,
            'device_name': device_name,
            'page_type': self.kwargs['page_type'],
            'machine_name': machine_name,
            'start_date': start_date,
            'end_date': end_date
        }

        return True

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        :param kwargs:
        :param args:
        """

        request = self.request
        self.initialize(*args, **kwargs)

        if not len(self.public_params):
            self.initialize_params()

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)
        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        
        # if the qs is empty then JSON is unable to serialize 
        # the empty ValuesQuerySet.Therefore changing its type to list.
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


# SIA LISTING CODE
class SIAListing(ListView):
    """
    View to render service impacting alarms page with appropriate column headers.
    """

    # need to associate ListView class with a model here
    model = CurrentAlarms
    template_name = 'alert_center/current_list.html'

    def get_context_data(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        context = super(SIAListing, self).get_context_data(**kwargs)

        datatable_headers = [
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Device Type', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'trapoid', 'sTitle': 'Trap OID', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'eventname', 'sTitle': 'Event Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'severity', 'sTitle': 'Severity', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'traptime', 'sTitle': 'Trap Time', 'sWidth': 'auto', 'bSortable': True},
        ]
        context['datatable_headers'] = json.dumps(datatable_headers)

        return context


class SIAListingTable(BaseDatatableView):
    """
    View to render service impacting alarms;
    namely history, current and clear alarms for all the devices.
    """

    model = None
    columns = ['device_name', 'ip_address', 'device_type', 'trapoid', 'eventname',
               'severity', 'traptime']
    order_columns = ['device_name', 'ip_address', 'device_type', 'trapoid', 'eventname',
                     'severity', 'traptime']

    def get_context_data(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        total_records = total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        final_data = list(qs)

        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': final_data
               }

        return ret

    def get_initial_queryset(self):
        """


        :return: :raise NotImplementedError:
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.using(TRAPS_DATABASE).values(*self.columns).all()


class CurrentAlarmsListingTable(SIAListingTable):
    model = CurrentAlarms


class ClearAlarmsListingTable(SIAListingTable):
    model = ClearAlarms


class HistoryAlarmsListingTable(SIAListingTable):
    model = HistoryAlarms