# -*- coding: utf-8 -*-

import datetime
# faster json processing module
import ujson as json

from django.db.models.query import ValuesQuerySet
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render_to_response, render
from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from device.models import Device, City, State, DeviceTechnology, DeviceType

from performance.models import EventNetwork, EventService

from operator import itemgetter
# utilities performance
from performance.utils import util as perf_utils

# utilities inventory
from inventory.utils import util as inventory_utils

from django.utils.dateformat import format

# nocout project settings # TODO: Remove the HARDCODED technology IDs
from nocout.settings import P2P, WiMAX, PMP, DEBUG, DATE_TIME_FORMAT

#utilities core
from nocout.utils import util as nocout_utils

#get the organisation of logged in user
from nocout.utils import logged_in_user_organizations

#alert center utilities
from alert_center.utils import util as alert_utils

import logging
logger = logging.getLogger(__name__)


def getCustomerAlertDetail(request):
    """
    get request to render customer detail list
    :params request object:
    :return Http Response Object::

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
        {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'auto', 'sClass': 'hidden-xs',
         'bSortable': False}
    ]

    datatable_headers = starting_headers
    datatable_headers += specific_headers
    datatable_headers += common_headers
    datatable_headers += polled_headers
    datatable_headers += other_headers

    context = {'datatable_headers': json.dumps(datatable_headers)}
    return render(request, 'alert_center/customer_alert_details_list.html', context)


class GetCustomerAlertDetail(BaseDatatableView):
    """
    Generic Class Based View for the Alert Center Customer Listing Tables.
    """
    is_polled = False
    model = EventService
    columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
               'current_value', 'max_value', 'sys_timestamp', 'description']
    order_columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
                     'current_value', 'max_value', 'sys_timestamp', 'description']

    polled_columns = ["id",
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
                      # "description"
    ]

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        else:
            organizations = logged_in_user_organizations(self)

            return self.get_initial_query_set_data(organizations=organizations)

    def get_initial_query_set_data(self, **kwargs):
        """
        Generic function required to fetch the initial data with respect to the page_type parameter in the get request requested.

        :param device_association:
        :param kwargs:
        :return: list of devices
        """

        page_type = "customer"

        required_value_list = ['id', 'machine__name', 'device_name', 'ip_address']

        if not DeviceTechnology.objects.filter(name__iexact=self.request.GET.get('data_tab').strip).exists():
            return []

        device_tab_technology = self.request.GET.get('data_tab')

        devices = inventory_utils.filter_devices(organizations=kwargs['organizations'],
                                                 data_tab=device_tab_technology,
                                                 page_type=page_type,
                                                 required_value_list=required_value_list
        )
        # query set for customer devices of the technology : P2P, WiMAX, PMP
        return devices

    def prepare_devices(self, qs, perf_results):
        """

        :param device_list:
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

        return perf_utils.prepare_gis_devices(qs,
                                              page_type,
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

    def prepare_polled_results(self, qs, machine_dict=None):
        """
        preparing polled results
        after creating static inventory first
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
            performance_data = alert_utils.raw_prepare_result(performance_data=performance_data,
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
                performance_data = alert_utils.raw_prepare_result(performance_data=performance_data,
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
            service_tab_name = 'service'
            for dct in qs:
                dct.update(action=''
                                  '<a href="/alert_center/{2}/device/{0}/service_tab/{1}/" title="Device Alerts"><i class="fa fa-warning text-warning"></i></a>'
                                  '<a href="/performance/{2}_live/{0}/" title="Device Performance"><i class="fa fa-bar-chart-o text-info"></i></a>'
                                  '<a href="/device/{0}" title="Device Inventory"><i class="fa fa-dropbox text-muted"></i></a>'
                           .format(dct['id'], service_tab_name, page_type)
                )
                dct = alert_utils.common_prepare_results(dct)

            return qs

        return []

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, prepare and display the data on the data table.

        """

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # machines dict
        machines = self.prepare_machines(qs)
        # machines dict

        # prepare the polled results
        perf_results = self.prepare_polled_results(qs, machine_dict=machines)
        # this is query set with complete polled result

        qs = alert_utils.map_results(perf_results, qs)

        # this function is for mapping to GIS inventory
        qs = self.prepare_devices(qs, perf_results)
        # this function is for mapping to GIS inventory

        # number of records before filtering
        total_records = len(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # qs = self.ordering(qs)
        # qs = self.paging(qs) #Removing pagination as of now to render all the data at once.
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


def getNetworkAlertDetail(request):
    """
    get request to render network detail list
    :params request object:
    :return Http Response Object:
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

    bh_specific_headers = [
        {'mData': 'alias', 'sTitle': 'BH Alias', 'sWidth': 'auto', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'bh_port_name', 'sTitle': 'BH Port Name', 'sWidth': 'auto', 'sClass': 'hidden-xs',
         'bSortable': True}
    ]

    common_headers = [
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
        {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'auto', 'sClass': 'hidden-xs',
         'bSortable': False}
    ]

    datatable_headers = []
    datatable_headers += starting_headers
    datatable_headers += specific_headers
    datatable_headers += common_headers
    datatable_headers += polled_headers
    datatable_headers += other_headers

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
        {'mData': 'sector__base_station__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'sector__base_station__state__state_name', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'sector__base_station__city__city_name', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'sector__sector_configured_on__ip_address', 'sTitle': 'BS IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'sector__sector_configured_on__device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'sector_sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'severity', 'sTitle': 'Status', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'age', 'sTitle': 'Aging (seconds)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
    ]

    sector_utils_headers = []
    sector_utils_headers += sector_util_hidden_headers
    sector_utils_headers += sector_util_common_headers

    bh_util_hidden_headers = [
        {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
        {'mData': 'organization__alias', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
    ]

    bh_util_common_headers = [
        {'mData': 'backhaul__bh_configured_on__ip_address', 'sTitle': 'BH IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'backhaul__alias', 'sTitle': 'Backhaul', 'sWidth': 'auto', 'bSortable': True},
        {'mData': 'basestation__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'bSortable': True},
        {'mData': 'bh_port_name', 'sTitle': 'Configured On Port', 'sWidth': 'auto', 'bSortable': True},
        {'mData': 'backhaul__bh_configured_on__device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'bSortable': True},
        {'mData': 'basestation__city__city_name', 'sTitle': 'BS City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'basestation__state__state_name', 'sTitle': 'BS State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'severity', 'sTitle': 'Status', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        {'mData': 'age', 'sTitle': 'Aging', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
    ]

    bh_utils_headers = []
    bh_utils_headers += bh_util_hidden_headers
    bh_utils_headers += bh_util_common_headers



    context = {
        'datatable_headers': json.dumps(datatable_headers),
        'bh_utils_headers' : json.dumps(bh_utils_headers),
        'bh_headers': json.dumps(bh_dt_headers),
        'sector_utils_headers': json.dumps(sector_utils_headers)
    }
    return render(request, 'alert_center/network_alert_details_list.html', context)


class GetNetworkAlertDetail(BaseDatatableView):
    """
    Generic Class Based View for the Alert Center Network  Detail Listing Tables.

    """
    model = EventNetwork
    columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
               'current_value', 'sys_time', 'sys_date', 'description']
    order_columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
                     'current_value', 'sys_time', 'sys_date', 'description']
    polled_columns = ["id",
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
                      # "description"
    ]
    data_sources = []
    table_name = "performance_servicestatus"

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        organizations = logged_in_user_organizations(self)

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
            elif tab_id in ["ULIssue"]:
                # technology = [int(WiMAX.ID), int(PMP.ID)]
                technology = ["WiMAX", "PMP"]
                self.data_sources = ['bs_ul_issue']
            elif tab_id in ["Backhaul", "BackhaulUtil"]:
                technology = None
                is_bh = True
                page_type = "other"
            else:
                return []

            if not is_bh:
                for techno in technology:
                    device_list += inventory_utils.filter_devices(organizations=organizations,
                                                                  data_tab=techno,
                                                                  page_type=page_type,
                                                                  required_value_list=required_value_list
                    )
            else:
                device_list += inventory_utils.filter_devices(organizations=organizations,
                                                              data_tab=None,
                                                              page_type=page_type,
                                                              required_value_list=required_value_list
                )

            return device_list

        else:
            return []

    def prepare_polled_results(self, qs, machine_dict=None):
        """
        preparing polled results
        after creating static inventory first
        """

        search_table = self.table_name

        extra_query_condition = ' AND `{0}`.`severity` in ("down","warning","critical","warn","crit") '

        sorted_device_list = list()

        #Fetching the data for the device w.r.t to their machine.
        for machine, machine_device_list in machine_dict.items():
            device_list = list()
            performance_data = list()
            performance_data = alert_utils.raw_prepare_result(performance_data=performance_data,
                                                              machine=machine,
                                                              table_name=search_table,
                                                              devices=machine_device_list,
                                                              data_sources=self.data_sources,
                                                              columns=self.polled_columns,
                                                              condition=extra_query_condition
                                                              if extra_query_condition
                                                              else None
            )

            device_list = alert_utils.prepare_raw_alert_results(performance_data=performance_data)

            sorted_device_list += device_list

        return sorted_device_list

    def prepare_devices(self, qs, perf_results):
        """

        :param device_list:
        :return:
        """
        page_type = self.request.GET.get('page_type', "network")
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

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return queryset.
        """
        page_type = self.request.GET.get('page_type', "network")
        if qs:
            service_tab_name = 'service'
            for dct in qs:
                dct.update(action='<a href="/alert_center/{2}/device/{0}/service_tab/{1}/" title="Device Alerts"><i class="fa fa-warning text-warning"></i></a>\
                                   <a href="/performance/{2}_live/{0}/" title="Device Performance"><i class="fa fa-bar-chart-o text-info"></i></a>\
                                   <a href="/device/{0}" title="Device Inventory"><i class="fa fa-dropbox text-muted"></i></a>'.
                           format(dct["id"],
                                  service_tab_name,
                                  page_type)
                )
                dct = alert_utils.common_prepare_results(dct)

        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, prepare and display the data on the data table.

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
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
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

        """

        context = super(AlertCenterListing, self).get_context_data(**kwargs)

        page_type = self.kwargs.get('page_type')

        data_source = self.kwargs.get('data_source')

        data_source_title = "Latency Avg (ms) " \
            if data_source == "latency" \
            else ("value".title() if data_source in ["service"] else "packet drop (%)".title())

        data_tab = self.kwargs.get('data_tab')

        # List of headers which are used in calculation but not shown in grid
        hidden_headers = [
            {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True}
        ]

        # List of headers which are shown first in grid for all pages
        starting_headers = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True}
        ]

        # List of common headers for all pages of alerts listing
        common_headers = [
            {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            # {'mData': 'device_technology', 'sTitle': 'Tech', 'sWidth': 'auto', 'sClass': 'hidden-xs',
            #  'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            # {'mData': 'sub_station', 'sTitle': 'Sub Station', 'sWidth': 'auto', 'sClass': 'hidden-xs',
            #  'bSortable': True},
            {'mData': 'bs_name', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'city', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'state', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            ]

        # Page specific & polled headers list initialization
        specific_headers = []
        polled_headers = []

        # if data_tab == 'P2P' or data_tab is None:
        #     specific_headers += [
        #         {'mData': 'circuit_id',
        #          'sTitle': 'Circuit ID',
        #          'sWidth': 'auto',
        #          'sClass': 'hidden-xs',
        #          'bSortable': True
        #         },
        #     ]

        if data_tab != 'P2P' or data_tab is not None:
            specific_headers += [
                {'mData': 'sector_id',
                 'sTitle': 'Sector ID',
                 'sWidth': 'auto',
                 'sClass': 'hidden-xs',
                 'bSortable': True
                }
            ]

        if page_type == 'customer' or data_tab == 'P2P' or data_tab is None:
            specific_headers += [
                {
                    'mData': 'circuit_id',
                    'sTitle': 'Circuit ID',
                    'sWidth': 'auto',
                    'sClass': 'hidden-xs',
                    'bSortable': True
                },
                {
                    'mData': 'customer_name',
                    'sTitle': 'Customer Name',
                    'sWidth': 'auto',
                    'bSortable': True
                }
            ]

        if page_type == 'customer':
            specific_headers += [
                {
                    'mData': 'near_end_ip',
                    'sTitle': 'Near End IP',
                    'sWidth': 'auto',
                    'sClass': 'hidden-xs',
                    'bSortable': True
                },
                ]

        if data_source == 'service':
            polled_headers += [
                {
                    'mData': 'data_source_name',
                    'sTitle': 'Data Source',
                    'sWidth': 'auto',
                    'sClass': 'hidden-xs',
                    'bSortable': True
                }
            ]

        polled_headers += [
            {
                'mData': 'current_value',
                'sTitle': '{0}'.format(data_source_title),
                'sWidth': 'auto',
                'sClass': 'hidden-xs',
                'bSortable': True, "sSortDataType": "dom-text", "sType": "numeric"
            }
        ]

        if data_source == "latency":
            polled_headers += [
                {
                    'mData': 'max_value',
                    'sTitle': 'Latency Max (ms)',
                    'sWidth': 'auto',
                    'sClass': 'hidden-xs',
                    'bSortable': True,
                    "sSortDataType": "dom-text",
                    "sType": "numeric"
                },
                {
                    'mData': 'min_value',
                    'sTitle': 'Latency Min (ms)',
                    'sWidth': 'auto',
                    'sClass': 'hidden-xs',
                    'bSortable': True,
                    "sSortDataType": "dom-text",
                    "sType": "numeric"
                }
            ]
        other_headers = [
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'Status Since', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'auto', 'bSortable': True},
            ]

        datatable_headers = hidden_headers
        datatable_headers += starting_headers
        datatable_headers += specific_headers
        datatable_headers += common_headers
        datatable_headers += polled_headers
        datatable_headers += other_headers

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['data_source'] = " ".join(self.kwargs['data_source'].split('_')).title()
        context['page_type'] = page_type
        return context


class AlertListingTable(BaseDatatableView):
    """
    Generic Class Based View for the Alert Center Network Listing Tables.

    """
    is_polled = False
    model = EventNetwork
    columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
               'current_value', 'max_value', 'sys_timestamp', 'description']
    order_columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
                     'current_value', 'max_value', 'sys_timestamp', 'description']

    polled_columns = ["id",
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
                      # "description"
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

    def prepare_devices(self, qs, perf_results):
        """

        :param device_list:
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

        return perf_utils.prepare_gis_devices(qs,
                                              page_type,
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

    def prepare_polled_results(self, qs, machine_dict=None):
        """
        preparing polled results
        after creating static inventory first
        """
        device_tab_technology = self.request.GET.get('data_tab')
        device_technology_id = DeviceTechnology.objects.get(name__icontains=device_tab_technology).id

        page_type = self.request.GET.get('page_type')
        data_source = self.request.GET.get('data_source')

        device_list, performance_data, data_sources_list = list(), list(), list()

        search_table = "performance_networkstatus"

        data_sources_list = list()

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
            search_table = "performance_networkstatus"
        elif data_source == 'service':
            extra_query_condition = ' AND `{0}`.`severity` in ("down","warning","critical","warn","crit") '
            search_table = "performance_servicestatus"

        required_data_columns = self.polled_columns

        sorted_device_list = list()

        #Fetching the data for the device w.r.t to their machine.
        for machine, machine_device_list in machine_dict.items():
            device_list = list()
            performance_data = list()
            performance_data = alert_utils.raw_prepare_result(performance_data=performance_data,
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

        page_type = self.request.GET.get('page_type')

        if qs:
            data_unit = "%"
            service_tab = 'down'
            # figure out which tab call is made.
            data_source = self.request.GET.get('data_source', '')
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
                dct.update(action='<a href="/alert_center/{2}/device/{0}/service_tab/{1}/" title="Device Alerts"><i class="fa fa-warning text-warning"></i></a>\
                                       <a href="/performance/{2}_live/{0}/" title="Device Performance"><i class="fa fa-bar-chart-o text-info"></i></a>\
                                       <a href="/device/{0}" title="Device Inventory"><i class="fa fa-dropbox text-muted"></i></a>'.
                           format(dct['id'], service_tab, page_type))

                dct = alert_utils.common_prepare_results(dct)

            return qs

        return []

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, prepare and display the data on the data table.

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
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
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


# This class initialize the single device alert page with appropriate params
class SingleDeviceAlertsInit(ListView):

    model = EventNetwork
    template_name = 'alert_center/single_device_alert.html'

    def get_context_data(self, **kwargs):

        service_name = self.kwargs['service_name']
        page_type = self.kwargs['page_type']
        device_id = self.kwargs['device_id']

        context = super(SingleDeviceAlertsInit, self).get_context_data(**kwargs)

        table_headers = [
            {"mData": "ip_address", "sTitle": "IP Address", "sWidth": "auto"},
            {"mData": "service_name", "sTitle": "Service Name", "sWidth": "auto"},
            {"mData": "data_source", "sTitle": "Data Source", "sWidth": "auto"},
            {"mData": "severity", "sTitle": "Severity", "sWidth": "auto"},
            {"mData": "current_value", "sTitle": "Current Value", "sWidth": "auto"},
            {"mData": "sys_timestamp", "sTitle": "Alert Datetime", "sWidth": "auto"},
            {"mData": "description", "sTitle": "Description", "sWidth": "auto"}
        ]

        ping_table_headers = [
            {"mData": "ip_address", "sTitle": "IP Address", "sWidth": "auto"},
            {"mData": "service_name", "sTitle": "Service Name", "sWidth": "auto"},
            # {"mData": "data_source", "sTitle": "Data Source", "sWidth": "auto"},
            {"mData": "severity", "sTitle": "Severity", "sWidth": "auto"},
            {"mData": "latency", "sTitle": "Latency", "sWidth": "auto"},
            {"mData": "packet_loss", "sTitle": "Packet Loss", "sWidth": "auto"},
            {"mData": "sys_timestamp", "sTitle": "Alert Datetime", "sWidth": "auto"},
            {"mData": "description", "sTitle": "Description", "sWidth": "auto"}
        ]

        device_obj = Device.objects.get(id=device_id)
        device_name = device_obj.device_name
        device_alias = device_obj.device_alias + "(" + device_obj.ip_address + ")"
        #  GET Technology of current device
        device_technology_name = DeviceTechnology.objects.get(id=device_obj.device_technology).name
        # context = {}

        # Create Context Dict
        context['table_headers'] = json.dumps(table_headers)
        context['ping_table_headers'] = json.dumps(ping_table_headers)
        context['current_device_id'] = device_id
        context['page_type'] = page_type
        # Device Inventory page url
        context['inventory_page_url'] = reverse(
            'device_edit',
            kwargs={'pk': device_id},
            current_app='device'
        )
        # Single Device perf page url
        context['perf_page_url'] = reverse(
            'SingleDevicePerf',
            kwargs={'page_type': page_type, 'device_id' : device_id},
            current_app='performance'
        )
        context['get_status_url'] = 'performance/get_inventory_device_status/' + page_type + '/device/' + str(device_id)
        context['device_technology_name'] = device_technology_name
        context['device_alias'] = device_alias
        context['current_device_name'] = device_name

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

    # order_columns = required_columns

    def filter_queryset(self, qs, info_dict):
        """ Filter datatable as per requested value """

        sSearch = self.request.GET.get('sSearch', None)

        if sSearch:

            if info_dict['service_name'] == 'ping':

                self.required_columns = [
                    "ip_address",
                    "service_name",
                    "severity",
                    "latency",
                    "packet_loss",
                    "sys_timestamp",
                    "description"
                ]

                # raw query is required here so as to get data
                query = alert_utils.ping_service_query(info_dict['device_name'], info_dict['start_date'], info_dict['end_date'])
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

                qs = nocout_utils.fetch_raw_result(final_query, info_dict['machine_name'])

            else:

                query = []
                if info_dict['service_name'] == 'service':
                    self.model = EventService

                # Create the default model condition string
                pre_condition_query = "("
                pre_condition_query += "Q(device_name="+str(info_dict['device_name'])+")"

                if info_dict['service_name'] == 'latency' :
                    pre_condition_query += " & Q(data_source='rta')"
                elif info_dict['service_name'] == 'packet_drop' :
                    pre_condition_query += " & Q(data_source='pl')"
                elif info_dict['service_name'] == 'down' :
                    pre_condition_query += " & Q(data_source='pl')"
                    pre_condition_query += " & Q(current_value=100)"
                    pre_condition_query += " & Q(severity='DOWN')"

                pre_condition_query += " & Q({0}__gte={1})".format('sys_timestamp',info_dict['start_date'])
                pre_condition_query += " & Q({0}__lte={1})".format('sys_timestamp',info_dict['end_date'])

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
                exec_query += ".using(alias='" +info_dict['machine_name']+"')"

                exec exec_query
        return qs

    def get_initial_queryset(self,info_dict):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        if info_dict['service_name'] == 'ping':
            self.required_columns = [
                "ip_address",
                "service_name",
                "severity",
                "latency",
                "packet_loss",
                "sys_timestamp",
                "description"
            ]

        if info_dict['service_name'] == 'service':

            report_resultset = EventService.objects.filter(
                device_name=info_dict['device_name'],
                sys_timestamp__gte=info_dict['start_date'],
                sys_timestamp__lte=info_dict['end_date']
            ).order_by("-sys_timestamp").values(*self.required_columns).using(alias=info_dict['machine_name'])

        elif info_dict['service_name'] == 'ping':

            # raw query is required here so as to get data
            query = alert_utils.ping_service_query(info_dict['device_name'], info_dict['start_date'], info_dict['end_date'])
            report_resultset = nocout_utils.fetch_raw_result(query, info_dict['machine_name'])

        elif info_dict['service_name'] == 'latency':

            report_resultset = EventNetwork.objects.filter(
                device_name=info_dict['device_name'],
                data_source='rta',
                sys_timestamp__gte=info_dict['start_date'],
                sys_timestamp__lte=info_dict['end_date']
            ).order_by("-sys_timestamp").values(*self.required_columns).using(alias=info_dict['machine_name'])

        elif info_dict['service_name'] == 'packet_drop':

            report_resultset = EventNetwork.objects.filter(
                device_name=info_dict['device_name'],
                data_source='pl',
                sys_timestamp__gte=info_dict['start_date'],
                sys_timestamp__lte=info_dict['end_date']
            ).order_by("-sys_timestamp").values(*self.required_columns).using(alias=info_dict['machine_name'])

        elif info_dict['service_name'] == 'down':

            report_resultset = EventNetwork.objects.filter(
                device_name=info_dict['device_name'],
                data_source='pl',
                current_value=100,  #need to show up and down both
                severity='DOWN',
                sys_timestamp__gte=info_dict['start_date'],
                sys_timestamp__lte=info_dict['end_date']
            ).order_by("-sys_timestamp").values(*self.required_columns).using(alias=info_dict['machine_name'])

        else:

            report_resultset = []

        return report_resultset

    def prepare_results(self, qs,service_name):
        """
        Preparing Final dataset for rendering the data table.
        """
        final_list = list()
        if qs:
            for data in qs:
                single_dict = {}
                single_dict = data
                single_dict['sys_timestamp'] = datetime.datetime.fromtimestamp(float(data["sys_timestamp"])).strftime(DATE_TIME_FORMAT)

                #add data to report_resultset list
                final_list.append(single_dict)
                # qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        else:
            final_list = qs

        return final_list

    def ordering(self, qs, service_name):
        """ Get parameters from the request and prepare order by clause
        """
        request = self.request
        # Number of columns that are used in sorting
        try:
            i_sorting_cols = int(request.REQUEST.get('iSortingCols', 0))
        except Exception:
            i_sorting_cols = 0

        order = []

        order_columns = self.required_columns

        if service_name == 'ping':
            order_columns = [
                "ip_address",
                "service_name",
                "severity",
                "latency",
                "packet_loss",
                "sys_timestamp",
                "description"
            ]

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

        service_name = self.request.GET.get('service_name', 'ping')

        device_id = self.kwargs['device_id']
        device_obj = Device.objects.get(id=device_id)
        device_name = device_obj.device_name
        machine_name = device_obj.machine.name

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

        params_dict = {
            'service_name' : service_name,
            'device_name' : device_name,
            'page_type' : self.kwargs['page_type'],
            'machine_name' : machine_name,
            'start_date' : start_date,
            'end_date' : end_date
        }

        qs = self.get_initial_queryset(params_dict)

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs,params_dict)
        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs,service_name)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        aaData = self.prepare_results(qs,service_name)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret