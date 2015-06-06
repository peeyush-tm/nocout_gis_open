import datetime

from operator import itemgetter

from django.shortcuts import render_to_response

from django.template import RequestContext

from django.db.models import Q, Count, F
from django.db.models.query import ValuesQuerySet
from django.utils.dateformat import format

from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView

import ujson as json

from device.models import DeviceTechnology, Device

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

from nocout.settings import DATE_TIME_FORMAT

from capacity_management.models import SectorCapacityStatus, BackhaulCapacityStatus

from performance.formulae import display_time

import logging
logger = logging.getLogger(__name__)

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


class SectorStatusHeaders(ListView):
    """
    Headers for sector status
    """
    model = SectorCapacityStatus
    template_name = 'capacity_management/sector_capacity_status.html'
    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """
        context = super(SectorStatusHeaders, self).get_context_data(**kwargs)

        hidden_headers = [
            {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'sector__sector_id', 'sTitle': 'Sector', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'severity', 'sTitle': 'severity', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'age', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'organization__alias', 'sTitle': 'organization', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
        ]
        
        common_headers = [
            {'mData': 'sector_sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__base_station__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__base_station__city__city_name', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__base_station__state__state_name', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'sector_capacity', 'sTitle': 'Cbw (MHz)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},

            {'mData': 'current_in_per', 'sTitle': 'DL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'current_in_val', 'sTitle': 'DL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector_capacity_in', 'sTitle': 'Capacity DL', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'avg_in_per', 'sTitle': 'AVG DL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'avg_in_val', 'sTitle': 'AVG DL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_in_per', 'sTitle': 'PEAK DL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_in_val', 'sTitle': 'PEAK DL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_in_timestamp', 'sTitle': 'PEAK Time', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},

            {'mData': 'current_out_per', 'sTitle': 'UL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'current_out_val', 'sTitle': 'UL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector_capacity_out', 'sTitle': 'Capacity UL', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'avg_out_per', 'sTitle': 'AVG UL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'avg_out_val', 'sTitle': 'AVG UL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_out_per', 'sTitle': 'PEAK UL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_out_val', 'sTitle': 'PEAK UL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_out_timestamp', 'sTitle': 'PEAK Time', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': 'auto', 'bSortable': False}
        ]

        datatable_headers = hidden_headers

        datatable_headers += common_headers

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class SectorStatusListing(BaseDatatableView):
    """
    Extend the Sector Status View
    """
    model = SectorCapacityStatus
    is_ordered = False
    is_polled = False
    is_searched = False
    is_initialised = True
    technology = 'ALL'

    columns = [
        'id',
        'sector__sector_id',
        'sector_sector_id',
        'sector__base_station__alias',
        'sector__base_station__city__city_name',
        'sector__base_station__state__state_name',
        'sector__sector_configured_on__ip_address',
        'sector__sector_configured_on__device_technology',
        'sector__sector_configured_on__id',
        'sector_capacity',
        'sector_capacity_in',
        'sector_capacity_out',
        'current_in_per',
        'current_in_val',
        'avg_in_per',
        'avg_in_val',
        'peak_in_per',
        'peak_in_val',
        'peak_in_timestamp',
        'current_out_per',
        'current_out_val',
        'avg_out_per',
        'avg_out_val',
        'peak_out_per',
        'peak_out_val',
        'peak_out_timestamp',
        'organization__alias',
        'severity',
        'age'
    ]

    order_columns = [
        'id',
        'sector__sector_id',
        'severity',
        'age',
        'organization__alias',
        'sector_sector_id',
        'sector__base_station__alias',
        'sector__base_station__city__city_name',
        'sector__base_station__state__state_name',
        'sector__sector_configured_on__ip_address',
        'sector__sector_configured_on__device_technology',
        'sector_capacity',
        'current_in_per',
        'current_in_val',
        'sector_capacity_in',
        'avg_in_per',
        'avg_in_val',
        'peak_in_per',
        'peak_in_val',
        'peak_in_timestamp',
        'current_out_per',
        'current_out_val',
        'sector_capacity_out',
        'avg_out_per',
        'avg_out_val',
        'peak_out_per',
        'peak_out_val',
        'peak_out_timestamp'
    ]

    related_columns = [
        'sector__base_station',
        'sector__base_station__city',
        'sector__base_station__state',
        'sector__sector_configured_on',
        'organization'
    ]

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        else:
            organizations = nocout_utils.logged_in_user_organizations(self)

            return self.get_initial_query_set_data(organizations=organizations)

    def get_initial_query_set_data(self, **kwargs):
        """
        Generic function required to fetch the initial data with respect to the page_type parameter in the get request requested.

        :param device_association:
        :param kwargs:
        :return: list of devices
        """
        if self.technology == 'ALL':
            sectors = self.model.objects.filter(
                Q(organization__in=kwargs['organizations'])
            ).prefetch_related(*self.related_columns).values(*self.columns)
        else:
            tech_id = DeviceTechnology.objects.get(name=self.technology).id
            if tech_id:
                sectors = self.model.objects.filter(
                    Q(organization__in=kwargs['organizations']),
                    Q(sector__sector_configured_on__device_technology=tech_id)
                ).prefetch_related(*self.related_columns).values(*self.columns)

        return sectors

    def prepare_results(self, qs):
        """
        """
        # data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        technology_object = DeviceTechnology.objects.all()

        for item in json_data:
            try:
                techno_name = technology_object.get(id=item['sector__sector_configured_on__device_technology']).alias
                device_id = item['sector__sector_configured_on__id']

                perf_page_link = ''
                if device_id:
                    perf_page_link = '<a href="/performance/network_live/'+str(device_id)+'/?is_util=1" \
                                      title="Device Performance"><i class="fa fa-bar-chart-o text-info"></i></a>'

                item['actions']=perf_page_link

                item['sector__sector_configured_on__device_technology'] = techno_name
                item['peak_out_timestamp'] = datetime.datetime.fromtimestamp(
                    float(item['peak_out_timestamp'])
                ).strftime(DATE_TIME_FORMAT)
                item['peak_in_timestamp'] = datetime.datetime.fromtimestamp(
                    float(item['peak_in_timestamp'])
                ).strftime(DATE_TIME_FORMAT)
            except Exception, e:
                logger.exception(e)
                continue

        return json_data

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        return nocout_utils.nocout_datatable_ordering(self, qs, self.order_columns)

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request


        self.initialize(*args, **kwargs)
        
        self.technology = request.GET['technology'] if 'technology' in request.GET else 'ALL'

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.annotate(Count('sector_sector_id')).count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.annotate(Count('id')).count()


        if total_display_records and total_records:

            #check if this has just initialised
            #if so : process the results

            qs = self.ordering(qs)
            qs = self.paging(qs)

            # if the qs is empty then JSON is unable to serialize the empty
            # ValuesQuerySet.Therefore changing its type to list.
            if not qs and isinstance(qs, ValuesQuerySet):
                qs = list(qs)

            aaData = self.prepare_results(qs)
        else:
            aaData = list()

        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }
        return ret

# This class loads headers for Sector Augmentation Alerts Listing Table
class SectorAugmentationAlertsHerders(ListView):
    """
    Headers for sector Augmentation Alerts
    """
    model = SectorCapacityStatus
    template_name = 'capacity_management/sector_capacity_alert.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """
        context = super(SectorAugmentationAlertsHerders, self).get_context_data(**kwargs)

        hidden_headers = [
            {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'sector__sector_id', 'sTitle': 'Sector', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'organization__alias', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
        ]

        common_headers = [
            {'mData': 'sector__base_station__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__base_station__state__state_name', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__base_station__city__city_name', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__ip_address', 'sTitle': 'BS IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector_sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'current_out_per', 'sTitle': '% UL Utilization', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'current_in_per', 'sTitle': '% DL Utilization', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'severity', 'sTitle': 'Status', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'Aging', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        ]

        datatable_headers = hidden_headers

        datatable_headers += common_headers

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

# This class loads data for Sector Augmentation Alerts Listing Table
class SectorAugmentationAlertsListing(SectorStatusListing):
    """
    Sector Augmentation Alerts Listing is subset for the Sector Capacity only
    """
    model = SectorCapacityStatus
    is_ordered = False
    is_polled = False
    is_searched = False
    is_initialised = True
    technology = 'ALL'

    columns = [
        'id',
        'sector__sector_id',
        'sector_sector_id',
        'sector__base_station__alias',
        'sector__base_station__city__city_name',
        'sector__base_station__state__state_name',
        'sector__sector_configured_on__ip_address',
        'sector__sector_configured_on__device_technology',
        'organization__alias',
        'current_out_per',
        'current_in_per',
        'severity',
        'sys_timestamp',
        'age'
    ]

    order_columns = columns

    related_columns = [
        'sector__base_station',
        'sector__base_station__city',
        'sector__base_station__state',
        'sector__sector_configured_on',
        'organization'
    ]

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        else:
            organizations = nocout_utils.logged_in_user_organizations(self)

            return self.get_initial_query_set_data(organizations=organizations)

    def get_initial_query_set_data(self, **kwargs):
        """
        Generic function required to fetch the initial data with respect to the page_type parameter in the get request requested.

        :param device_association:
        :param kwargs:
        :return: list of devices
        """

        if self.technology == 'ALL':
            sectors = self.model.objects.filter(
                Q(organization__in=kwargs['organizations']),
                Q(severity__in=['warning', 'critical']),
                # Q(age__lte = F('sys_timestamp') - 600)
            ).prefetch_related(*self.related_columns).values(*self.columns)
        else:
            tech_id = DeviceTechnology.objects.get(name=self.technology).id
            sectors = self.model.objects.filter(
                Q(organization__in=kwargs['organizations']),
                Q(sector__sector_configured_on__device_technology=tech_id),
                Q(severity__in=['warning', 'critical']),
                # Q(age__lte = F('sys_timestamp') - 600)
            ).prefetch_related(*self.related_columns).values(*self.columns)

        return sectors

    def prepare_results(self, qs):
        """
        """
        # data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        technology_object = DeviceTechnology.objects.all()

        for item in json_data:
            try:
                techno_name = technology_object.get(id=item['sector__sector_configured_on__device_technology']).alias
                item['sector__sector_configured_on__device_technology'] = techno_name
                item['age'] = display_time(float(item['sys_timestamp']) - float(item['age']))

                if item['severity'].strip().lower() == 'warning':
                    item['severity'] = "Needs Augmentation"
                elif item['severity'].strip().lower() == 'critical':
                    item['severity'] = "Stop Provisioning"
                else:
                    continue

            except Exception as e:
                logger.exception(e)

        return json_data

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request

        self.initialize(*args, **kwargs)

        self.technology = request.GET['technology'] if 'technology' in request.GET else 'ALL'

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.annotate(Count('sector_sector_id')).count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.annotate(Count('id')).count()

        if total_display_records and total_records:

            #check if this has just initialised
            #if so : process the results

            qs = self.ordering(qs)
            qs = self.paging(qs)

            # if the qs is empty then JSON is unable to serialize the empty
            # ValuesQuerySet.Therefore changing its type to list.
            if not qs and isinstance(qs, ValuesQuerySet):
                qs = list(qs)

            aaData = self.prepare_results(qs)
        else:
            aaData = list()

        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }
        return ret


class BackhaulStatusHeaders(ListView):
    """
    Headers for backhaul status
    """
    model = BackhaulCapacityStatus
    template_name = 'capacity_management/backhaul_capacity_status.html'
    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """
        context = super(BackhaulStatusHeaders, self).get_context_data(**kwargs)

        hidden_headers = [
            {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'severity', 'sTitle': 'severity', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'age', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'organization__alias', 'sTitle': 'organization', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
        ]

        common_headers = [
            {'mData': 'backhaul__bh_configured_on__ip_address', 'sTitle': 'BH IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'backhaul__alias', 'sTitle': 'Backhaul', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'basestation__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'backhaul__bh_type', 'sTitle': 'BH Type', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'backhaul__bh_connectivity', 'sTitle': 'Onnet/Offnet', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'bh_port_name', 'sTitle': 'Configured On Port', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'basestation__city__city_name', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'basestation__state__state_name', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'backhaul__bh_configured_on__device_technology', 'sTitle': 'Technology', 'sClass': 'hidden-xs',  'sWidth': 'auto', 'bSortable': True},
            {'mData': 'backhaul_capacity', 'sTitle': 'BH Capacity (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},

            {'mData': 'current_in_per', 'sTitle': 'DL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'current_in_val', 'sTitle': 'DL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'avg_in_per', 'sTitle': 'AVG DL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'avg_in_val', 'sTitle': 'AVG DL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_in_per', 'sTitle': 'PEAK DL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_in_val', 'sTitle': 'PEAK DL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_in_timestamp', 'sTitle': 'PEAK Time', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},

            {'mData': 'current_out_per', 'sTitle': 'UL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'current_out_val', 'sTitle': 'UL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'avg_out_per', 'sTitle': 'AVG UL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'avg_out_val', 'sTitle': 'AVG UL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_out_per', 'sTitle': 'PEAK UL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_out_val', 'sTitle': 'PEAK UL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'peak_out_timestamp', 'sTitle': 'PEAK Time', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': 'auto', 'bSortable': False},
        ]

        datatable_headers = []

        datatable_headers += hidden_headers

        datatable_headers += common_headers

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class BackhaulStatusListing(BaseDatatableView):
    """
    Extend the Backhaul Status View
    """
    model = BackhaulCapacityStatus
    is_ordered = False
    is_polled = False
    is_searched = False
    is_initialised = True

    columns = [
        'id',
        'severity',
        'age',
        'organization__alias',
        'backhaul__bh_configured_on__ip_address',
        'backhaul__bh_configured_on__id',
        'backhaul__alias',
        'basestation__alias',
        'backhaul__bh_type',
        'backhaul__bh_connectivity',
        'bh_port_name',
        'backhaul__bh_configured_on__device_technology',
        'basestation__city__city_name',
        'basestation__state__state_name',
        'backhaul_capacity',
        'current_in_per',
        'current_in_val',
        'avg_in_per',
        'avg_in_val',
        'peak_in_per',
        'peak_in_val',
        'peak_in_timestamp',
        'current_out_per',
        'current_out_val',
        'avg_out_per',
        'avg_out_val',
        'peak_out_per',
        'peak_out_val',
        'peak_out_timestamp'
    ]

    order_columns = columns

    related_columns = [
        'basestation__city',
        'basestation__state',
        'backhaul__bh_configured_on',
        'organization'
    ]

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        else:
            organizations = nocout_utils.logged_in_user_organizations(self)

            return self.get_initial_query_set_data(organizations=organizations)

    def get_initial_query_set_data(self, **kwargs):
        """
        Generic function required to fetch the initial data with respect to the page_type parameter in the get request requested.

        :param device_association:
        :param kwargs:
        :return: list of devices
        """

        sectors = self.model.objects.filter(
            Q(organization__in=kwargs['organizations'])
        ).prefetch_related(*self.related_columns).values(*self.columns)

        return sectors

    def prepare_results(self, qs):
        """
        """
        # data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        technology_object = DeviceTechnology.objects.all()

        for item in json_data:
            try:
                techno_name = technology_object.get(id=item['backhaul__bh_configured_on__device_technology']).alias
                device_id = item['backhaul__bh_configured_on__id']

                perf_page_link = ''
                if device_id:
                    perf_page_link = '<a href="/performance/other_live/'+str(device_id)+'/?is_util=1" \
                                      title="Device Performance"><i class="fa fa-bar-chart-o text-info"></i></a>'

                item['actions']=perf_page_link

                item['backhaul__bh_configured_on__device_technology'] = techno_name
                
                item['peak_out_timestamp'] = datetime.datetime.fromtimestamp(
                    float(item['peak_out_timestamp'])
                ).strftime(DATE_TIME_FORMAT) if item['peak_out_timestamp'] else ''

                item['peak_in_timestamp'] = datetime.datetime.fromtimestamp(
                    float(item['peak_in_timestamp'])
                ).strftime(DATE_TIME_FORMAT) if item['peak_in_timestamp'] else ''

            except Exception, e:
                logger.exception(e)
                continue

        return json_data

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request

        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        # total_records = qs.annotate(Count('sector_sector_id')).count()
        total_records = qs.annotate(Count('id')).count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.annotate(Count('id')).count()

        if total_display_records and total_records:

            #check if this has just initialised
            #if so : process the results

            qs = self.ordering(qs)
            qs = self.paging(qs)

            # if the qs is empty then JSON is unable to serialize the empty
            # ValuesQuerySet.Therefore changing its type to list.
            if not qs and isinstance(qs, ValuesQuerySet):
                qs = list(qs)

            aaData = self.prepare_results(qs)
        else:
            aaData = list()

        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }
        return ret


# This class loads headers for Backhaul Augmentation Alerts Listing Table
class BackhaulAugmentationAlertsHeaders(ListView):
    """
    Headers for backhaul Augmentation Alerts
    """
    model = BackhaulCapacityStatus
    template_name = 'capacity_management/backhaul_capacity_alert.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """
        context = super(BackhaulAugmentationAlertsHeaders, self).get_context_data(**kwargs)

        hidden_headers = [
            {'mData': 'id', 'sTitle': 'Device ID', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'organization__alias', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
        ]

        common_headers = [
            {'mData': 'backhaul__bh_configured_on__ip_address', 'sTitle': 'BH IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'backhaul__alias', 'sTitle': 'Backhaul', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'basestation__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'bh_port_name', 'sTitle': 'Configured On Port', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'backhaul__bh_configured_on__device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'basestation__city__city_name', 'sTitle': 'BS City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'basestation__state__state_name', 'sTitle': 'BS State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'current_out_per', 'sTitle': '% UL Utilization', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'current_in_per', 'sTitle': '% DL Utilization', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'severity', 'sTitle': 'Status', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'Aging', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        ]

        datatable_headers = hidden_headers

        datatable_headers += common_headers

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


# This class loads data for Backhaul Augmentation Alerts Listing Table
class BackhaulAugmentationAlertsListing(BackhaulStatusListing):
    """
    Backhaul Augmentation Alerts Listing is subset for the Backhaul Capacity only
    """
    model = BackhaulCapacityStatus
    is_ordered = False
    is_polled = False
    is_searched = False
    is_initialised = True

    columns = [
        'id',
        'backhaul__bh_configured_on__ip_address',
        'backhaul__alias',
        'basestation__alias',
        'bh_port_name',
        'backhaul__bh_configured_on__device_technology',
        'basestation__city__city_name',
        'basestation__state__state_name',
        'organization__alias',
        'current_out_per',
        'current_in_per',
        'severity',
        'sys_timestamp',
        'age'
    ]

    order_columns = columns

    related_columns = [
        'backhaul__bh_configured_on',
        'basestation__city',
        'basestation__state',
        'organization'
    ]

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        else:
            organizations = nocout_utils.logged_in_user_organizations(self)

            return self.get_initial_query_set_data(organizations=organizations)

    def get_initial_query_set_data(self, **kwargs):
        """
        Generic function required to fetch the initial data with respect to the page_type parameter in the get request requested.

        :param device_association:
        :param kwargs:
        :return: list of devices
        """

        backhauls = self.model.objects.filter(
            Q(organization__in=kwargs['organizations']),
            Q(severity__in=['warning', 'critical']),
            # Q(age__lte=F('sys_timestamp') - 600)
        ).prefetch_related(*self.related_columns).values(*self.columns)

        return backhauls

    def prepare_results(self, qs):
        """
        """
        # data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        technology_object = DeviceTechnology.objects.all()

        for item in json_data:
            try:
                techno_name = technology_object.get(id=item['backhaul__bh_configured_on__device_technology']).alias
                item['backhaul__bh_configured_on__device_technology'] = techno_name
                item['age'] = display_time(float(item['sys_timestamp']) - float(item['age']))

                if item['severity'].strip().lower() == 'warning':
                    item['severity'] = "Needs Augmentation"
                elif item['severity'].strip().lower() == 'critical':
                    item['severity'] = "Stop Provisioning"
                else:
                    continue

            except Exception as e:
                logger.exception(e)

        return json_data

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request

        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        # total_records = qs.annotate(Count('sector_sector_id')).count()
        total_records = qs.annotate(Count('id')).count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.annotate(Count('id')).count()

        if total_display_records and total_records:

            #check if this has just initialised
            #if so : process the results

            qs = self.ordering(qs)
            qs = self.paging(qs)

            # if the qs is empty then JSON is unable to serialize the empty
            # ValuesQuerySet.Therefore changing its type to list.
            if not qs and isinstance(qs, ValuesQuerySet):
                qs = list(qs)

            aaData = self.prepare_results(qs)
        else:
            aaData = list()

        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }
        return ret
