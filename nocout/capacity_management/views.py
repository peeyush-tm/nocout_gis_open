import datetime

from operator import itemgetter

from django.shortcuts import render_to_response

from django.template import RequestContext

from django.db.models import Q, Count, F, Max
from django.db.models.query import ValuesQuerySet
from django.utils.dateformat import format

from django.core.urlresolvers import reverse

from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView

import ujson as json

from device.models import DeviceTechnology, Device, DeviceType

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway, time_delta_calculator

from nocout.mixins.datatable import AdvanceFilteringMixin

from nocout.settings import DATE_TIME_FORMAT, RADWIN5K_CONFIG, SHOW_SPRINT3

from capacity_management.models import SectorCapacityStatus, BackhaulCapacityStatus

from performance.formulae import display_time

import logging

# This import needs to be done becuase in case of Radwin5K sector Utilization
# Headers are getting defined in NetworkAlertDetailHeaders class
from alert_center.views import NetworkAlertDetailHeaders

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
            {'mData': 'id', 'sTitle': 'Device ID', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'sector__sector_id', 'sTitle': 'Sector', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'severity', 'sTitle': 'severity', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'age', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'organization__alias', 'sTitle': 'organization', 'sClass': 'hide', 'bSortable': True},
        ]

        inventory_headers = [
            {'mData': 'sector_sector_id', 'sTitle': 'Sector ID', 'bSortable': True},
            {'mData': 'sector__base_station__alias', 'sTitle': 'BS Name', 'bSortable': True},
            {'mData': 'sector__base_station__city__city_name', 'sTitle': 'City', 'bSortable': True},
            {'mData': 'sector__base_station__state__state_name', 'sTitle': 'State', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__ip_address', 'sTitle': 'IP', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__device_technology', 'sTitle': 'Technology', 'bSortable': True},
        ]

        current_headers = [
            {'mData': 'sector_capacity', 'sTitle': 'Cbw (MHz)', 'bSortable': True},
            {'mData': 'current_in_per', 'sTitle': 'DL (%)', 'bSortable': True},
            {'mData': 'current_in_val', 'sTitle': 'DL (mbps)', 'bSortable': True},
            {'mData': 'sector_capacity_in', 'sTitle': 'Capacity DL', 'bSortable': True},
        ]

        # Create Cambium, Wimax headers
        datatable_headers = list()
        datatable_headers.extend(hidden_headers)
        datatable_headers.extend(inventory_headers)
        datatable_headers.extend(current_headers)
        datatable_headers.extend([
            {'mData': 'avg_in_per', 'sTitle': 'AVG DL (%)', 'bSortable': True},
            {'mData': 'avg_in_val', 'sTitle': 'AVG DL (mbps)', 'bSortable': True},
            {'mData': 'peak_in_per', 'sTitle': 'PEAK DL (%)', 'bSortable': True},
            {'mData': 'peak_in_val', 'sTitle': 'PEAK DL (mbps)', 'bSortable': True},
            {'mData': 'peak_in_timestamp', 'sTitle': 'PEAK Time', 'bSortable': True},
            {'mData': 'current_out_per', 'sTitle': 'UL (%)', 'bSortable': True},
            {'mData': 'current_out_val', 'sTitle': 'UL (mbps)', 'bSortable': True},
            {'mData': 'sector_capacity_out', 'sTitle': 'Capacity UL', 'bSortable': True},
            {'mData': 'avg_out_per', 'sTitle': 'AVG UL (%)', 'bSortable': True},
            {'mData': 'avg_out_val', 'sTitle': 'AVG UL (mbps)', 'bSortable': True},
            {'mData': 'peak_out_per', 'sTitle': 'PEAK UL (%)', 'bSortable': True},
            {'mData': 'peak_out_val', 'sTitle': 'PEAK UL (mbps)', 'bSortable': True},
            {'mData': 'peak_out_timestamp', 'sTitle': 'PEAK Time', 'bSortable': True},
            {'mData': 'actions', 'sTitle': 'Actions', 'bSortable': False}
        ])

        # Create Radwin5K headers
        rad5k_datatable_headers = list()
        rad5k_datatable_headers.extend(hidden_headers)
        rad5k_datatable_headers.extend(inventory_headers)

        if RADWIN5K_CONFIG.get('SECTOR_STATUS_CUSTOMER_COUNT'):
            rad5k_datatable_headers.insert(len(rad5k_datatable_headers) - 1, {
                'mData': 'customer_count', 
                'sTitle': 'Customer Count', 
                'bSortable': True
            })

        rad5k_datatable_headers.extend(current_headers)
        rad5k_datatable_headers.extend([
            {'mData': 'peak_in_per', 'sTitle': 'PEAK DL (%)', 'bSortable': True},
            {'mData': 'peak_in_val', 'sTitle': 'PEAK DL (mbps)', 'bSortable': True},
            {'mData': 'peak_in_timestamp', 'sTitle': 'PEAK Time', 'bSortable': True},
            {'mData': 'peak_in_duration', 'sTitle': 'Duration', 'bSortable': True},
            {'mData': 'current_out_per', 'sTitle': 'UL (%)', 'bSortable': True},
            {'mData': 'current_out_val', 'sTitle': 'UL (mbps)', 'bSortable': True},
            {'mData': 'sector_capacity_out', 'sTitle': 'Capacity UL', 'bSortable': True},
            {'mData': 'peak_out_per', 'sTitle': 'PEAK UL (%)', 'bSortable': True},
            {'mData': 'peak_out_val', 'sTitle': 'PEAK UL (mbps)', 'bSortable': True},
            {'mData': 'peak_out_timestamp', 'sTitle': 'PEAK Time', 'bSortable': True},
            {'mData': 'peak_out_duration', 'sTitle': 'Duration', 'bSortable': True},
            {'mData': 'actions', 'sTitle': 'Actions', 'bSortable': False}
        ])
        context['datatable_headers'] = json.dumps(datatable_headers)
        context['rad5k_datatable_headers'] = json.dumps(rad5k_datatable_headers)
        return context


class SectorStatusListing(BaseDatatableView, AdvanceFilteringMixin):
    """
    Extend the Sector Status View
    """
    model = SectorCapacityStatus
    is_ordered = False
    is_polled = False
    is_searched = False
    is_initialised = True
    technology = 'ALL'
    is_type = 0

    columns = [
        'id', 'sector__sector_id', 'sector_sector_id', 'sector__base_station__alias',
        'sector__base_station__city__city_name', 'sector__base_station__state__state_name', 
        'sector__sector_configured_on__ip_address', 'sector__sector_configured_on__device_technology',
        'sector__sector_configured_on__id', 'sector_capacity', 'sector_capacity_in',
        'sector_capacity_out', 'current_in_per', 'current_in_val', 'avg_in_per',
        'avg_in_val', 'peak_in_per', 'peak_in_val', 'peak_in_timestamp', 'peak_in_duration', 'current_out_per',
        'current_out_val', 'avg_out_per', 'avg_out_val', 'peak_out_per', 'peak_out_val',
        'peak_out_timestamp', 'peak_out_duration', 'organization__alias', 'severity', 'age'
    ]

    order_columns = [
        'id', 'sector__sector_id', 'severity', 'age', 'organization__alias',
        'sector_sector_id', 'sector__base_station__alias', 'sector__base_station__city__city_name',
        'sector__base_station__state__state_name', 'sector__sector_configured_on__ip_address', 
        'sector__sector_configured_on__device_technology', 'sector_capacity', 'current_in_per', 'current_in_val',
        'sector_capacity_in', 'avg_in_per', 'avg_in_val', 'peak_in_per', 'peak_in_val',
        'peak_in_timestamp', 'current_out_per', 'current_out_val', 'sector_capacity_out', 'avg_out_per',
        'avg_out_val', 'peak_out_per', 'peak_out_val', 'peak_out_timestamp'
    ]

    related_columns = [
        'sector__base_station',
        'sector__base_station__city',
        'sector__base_station__state',
        'sector__sector_configured_on',
        'organization'
    ]

    is_technology_searched = False

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('search[value]', None)
        self.is_technology_searched = False
        if sSearch:
            if sSearch.lower() in ['pmp', 'wimax']:
                self.is_technology_searched = True
                prepared_data = self.prepare_results(qs)
                filtered_result = list()

                for data in prepared_data:
                    if sSearch.lower() in str(data).lower():
                        filtered_result.append(data)
                        
                return self.advance_filter_queryset(filtered_result)
            else:
                query = []
                exec_query = "qs = qs.filter("
                for column in self.columns[:-1]:
                    query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

                exec_query += " | ".join(query)
                exec_query += ").values(*" + str(self.columns) + ")"
                exec exec_query
        return self.advance_filter_queryset(qs)

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
                sector__sector_configured_on__isnull=False,
                organization__in=kwargs['organizations']
            ).prefetch_related(*self.related_columns).values(*self.columns)
        else:
            where_condition = Q()
            where_condition &= Q(sector__sector_configured_on__isnull=False)
            where_condition &= Q(organization__in=kwargs['organizations'])

            if self.is_type:
                try:
                    device_type_id = DeviceType.objects.get(name__iexact=self.technology).id
                    where_condition &= Q(sector__sector_configured_on__device_type=device_type_id)
                except Exception, e:
                    return self.model.objects.filter(id=0)
                    pass
            else:
                try:
                    tech_id = DeviceTechnology.objects.get(name__iexact=self.technology).id
                    where_condition &= Q(sector__sector_configured_on__device_technology=tech_id)
                    if self.technology.lower() == 'pmp':
                        excluded_device_type = DeviceType.objects.filter(
                            name__icontains='radwin5'
                        ).values_list('id', flat=True)
                        where_condition &= ~Q(sector__sector_configured_on__device_type__in=excluded_device_type)
                except Exception, e:
                    pass

            sectors = self.model.objects.filter(
                where_condition
            ).prefetch_related(*self.related_columns).values(*self.columns)

        return sectors

    def prepare_results(self, qs):
        """
        """
        json_data = [{key: val if val not in ['', 'undefined', 'None'] else "" for key, val in dct.items()} for dct in
                     qs]
        technology_object = DeviceTechnology.objects.all()

        for item in json_data:
            try:
                techno_name = technology_object.get(id=item['sector__sector_configured_on__device_technology']).alias
                device_id = item['sector__sector_configured_on__id']

                perf_page_link = ''
                if device_id:
                    performance_url = reverse(
                        'SingleDevicePerf',
                        kwargs={
                            'page_type': 'network',
                            'device_id': device_id
                        },
                        current_app='performance'
                    )
                    perf_page_link = '<a href="' + performance_url + '?is_util=1" \
                                      title="Device Performance"><i class="fa \
                                      fa-bar-chart-o text-info"></i></a>'

                item['actions'] = perf_page_link
                item['sector__sector_configured_on__device_technology'] = techno_name
                # Format DL Peak Time
                item['peak_out_timestamp'] = datetime.datetime.fromtimestamp(
                    float(item['peak_out_timestamp'])
                ).strftime(
                    DATE_TIME_FORMAT
                ) if str(item['peak_out_timestamp']) not in ['', 'undefined', 'None', '0'] else 'NA'
                # Format UL Peak Time
                item['peak_in_timestamp'] = datetime.datetime.fromtimestamp(
                    float(item['peak_in_timestamp'])
                ).strftime(
                    DATE_TIME_FORMAT
                ) if str(item['peak_in_timestamp']) not in ['', 'undefined', 'None', '0'] else 'NA'
            except Exception, e:
                logger.exception(e)
                continue

        return json_data

    def ordering(self, qs):
        """
        Get parameters from the request and prepare order by clause
        """
        if 'Radwin5K' in self.technology and self.is_type:
            self.order_columns = [
                'id', 'sector__sector_id', 'severity', 'age', 'organization__alias',
                'sector_sector_id', 'sector__base_station__alias', 'sector__base_station__city__city_name',
                'sector__base_station__state__state_name', 'sector__sector_configured_on__ip_address', 
                'sector__sector_configured_on__device_technology', 'sector_capacity', 'current_in_per', 'current_in_val',
                'sector_capacity_in', 'peak_in_per', 'peak_in_val', 'peak_in_timestamp', 'peak_in_duration',
                'current_out_per', 'current_out_val', 'sector_capacity_out', 'peak_out_per', 
                'peak_out_val', 'peak_out_timestamp', 'peak_out_duration'
            ]

        return nocout_utils.nocout_datatable_ordering(self, qs, self.order_columns)

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request

        self.initialize(*args, **kwargs)

        self.technology = request.GET.get('technology', 'ALL')
        self.is_type = request.GET.get('is_type', 0)

        qs = self.get_initial_queryset()

        # number of records before filtering
        if type(qs) == type(list()):
            total_records = len(qs)
        else:
            total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        if type(qs) == type(list()):
            total_display_records = len(qs)
        else:
            total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # if the qs is empty then JSON is unable to serialize the empty
        # ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        if self.is_technology_searched:
            aaData = qs
        else:
            aaData = self.prepare_results(qs)

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
            {'mData': 'organization__alias', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hide',
             'bSortable': True},
        ]

        common_headers = [
            {'mData': 'sector__base_station__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'sector__base_station__state__state_name', 'sTitle': 'State', 'sWidth': 'auto',
             'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__base_station__city__city_name', 'sTitle': 'City', 'sWidth': 'auto',
             'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__ip_address', 'sTitle': 'BS IP', 'sWidth': 'auto',
             'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__device_technology', 'sTitle': 'Technology', 'sWidth': 'auto',
             'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector_sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'current_out_per', 'sTitle': '% UL Utilization', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'current_in_per', 'sTitle': '% DL Utilization', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'severity', 'sTitle': 'Status', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'Aging', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
        ]
        # datatable_headers = list()
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
    is_type = 0
    is_rad5 = 0

    columns = [
        'id',
        'sector__sector_id',
        'organization__alias',
        'sector__base_station__alias',
        'sector__base_station__state__state_name',
        'sector__base_station__city__city_name',
        'sector__sector_configured_on__ip_address',
        'sector__sector_configured_on__device_technology',
        'sector_sector_id',
        'current_out_per',
        'current_in_per',
        'severity',
        'age',
        'sys_timestamp'
    ]

    order_columns = columns

    related_columns = [
        'sector__base_station',
        'sector__base_station__city',
        'sector__base_station__state',
        'sector__sector_configured_on',
        'organization'
    ]

    is_technology_searched = False

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value """

        # sSearch = self.request.GET.get('sSearch', None)
        sSearch = self.request.GET.get('search[value]', None)

        if sSearch:
            # In case of severity search, update the search txt
            if sSearch.lower() in 'needs augmentation':
                sSearch = 'warning'
            elif sSearch in 'stop provisioning':
                sSearch = 'critical'
            else:
                pass

            # In case of technology search, search the text in
            # prepared result instead of queryset because we have
            # technology id in queryset not the name
            if sSearch.lower() in ['pmp', 'wimax']:
                self.is_technology_searched = True
                prepared_data = self.prepare_results(qs)
                filtered_result = list()

                for data in prepared_data:
                    if sSearch.lower() in str(data).lower():
                        filtered_result.append(data)

                return self.advance_filter_queryset(filtered_result)
            else:
                self.is_technology_searched = False
                query = []
                exec_query = "qs = qs.filter("
                for column in self.columns[:-1]:
                    # avoid search on 'added_on'
                    if column == 'added_on':
                        continue
                    query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

                exec_query += " | ".join(query)
                exec_query += ").values(*" + str(self.columns + ['id']) + ")"
                exec exec_query
        return self.advance_filter_queryset(qs)

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
        max_timestamp = self.model.objects.filter(
            Q(organization__in=kwargs['organizations']),
            Q(severity__in=['warning', 'critical'])
        ).aggregate(Max('sys_timestamp'))['sys_timestamp__max']

        sectors = list()
        if max_timestamp:
            if self.technology == 'ALL':
                # Excluding Radwin5K devices
                excluded_device_type = DeviceType.objects.filter(
                    name__icontains='radwin5'
                ).values_list('id', flat=True)

                sectors = self.model.objects.filter(
                    ~Q(sector__sector_configured_on__device_type__in=excluded_device_type),
                    sector__sector_configured_on__isnull=False,
                    organization__in=kwargs['organizations']
                ).prefetch_related(*self.related_columns).values(*self.columns)
            else:
                where_condition = Q()
                where_condition &= Q(organization__in=kwargs['organizations'])
                where_condition &= Q(sys_timestamp__gte=max_timestamp - 420)

                if self.is_type:
                    try:
                        device_type_id = DeviceType.objects.get(name__iexact=self.technology).id
                        where_condition &= Q(sector__sector_configured_on__device_type=device_type_id)
                    except Exception, e:
                        return self.model.objects.filter(id=0)
                        pass
                else:
                    try:
                        tech_id = DeviceTechnology.objects.get(name__iexact=self.technology).id
                        where_condition &= Q(sector__sector_configured_on__device_technology=tech_id)
                        
                        if SHOW_SPRINT3:
                            if self.technology.lower() == 'pmp':
                                excluded_device_type = DeviceType.objects.filter(
                                    name__icontains='radwin5'
                                ).values_list('id', flat=True)

                                # Case handling for Radwin5k devices
                                if self.is_rad5:
                                    where_condition &= Q(sector__sector_configured_on__device_type__in=excluded_device_type)
                                else:
                                    where_condition &= ~Q(sector__sector_configured_on__device_type__in=excluded_device_type)
                    except Exception, e:
                        pass

                sectors = self.model.objects.filter(
                    where_condition
                    &
                    Q(severity__in=['warning', 'critical'])
                ).prefetch_related(*self.related_columns).values(*self.columns)
        return sectors

    def prepare_results(self, qs):
        """
        """
        # number of records after filtering
        if type(qs) == type(list()):
            json_data = qs
        else:
            json_data = [{key: val if val not in ['', 'undefined', 'None'] else "" for key, val in dct.items()} for dct
                         in qs]

        technology_object = DeviceTechnology.objects.all()

        for item in json_data:
            try:
                techno_name = technology_object.get(id=item['sector__sector_configured_on__device_technology']).alias
                item['sector__sector_configured_on__device_technology'] = techno_name
                
                if item['sys_timestamp'] and item['age']:
                    item['age'] = display_time(float(item['sys_timestamp']) - float(item['age']))
                else:
                    item['age'] = str(item['age']) + ' second'

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
        self.is_type = request.GET.get('is_type', 0)
        self.is_rad5 = int(request.GET.get('is_rad5', 0))

        if self.is_rad5:
            self.columns = [
                'sector__base_station__alias',
                'sector__base_station__state__state_name',
                'sector__base_station__city__city_name',
                'organization__alias',
                'sector__sector_configured_on__ip_address',
                'sector__sector_configured_on__device_technology',
                'sector_sector_id',
                'current_out_per',
                'current_in_per',
                'timeslot_dl',
                'timeslot_ul',
                'severity',
                'age',
                'sector__base_station__bs_site_id',
                'sys_timestamp'
            ]

            self.order_columns = self.columns

        qs = self.get_initial_queryset()

        # number of records before filtering
        if type(qs) == type(list()):
            total_records = len(qs)
        else:
            total_records = qs.annotate(Count('sector_sector_id')).count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        if type(qs) == type(list()):
            total_display_records = len(qs)
        else:
            total_display_records = qs.annotate(Count('id')).count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # if the qs is empty then JSON is unable to serialize the empty
        # ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        if self.is_technology_searched:
            aaData = qs
        else:
            aaData = self.prepare_results(qs)

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
            {'mData': 'organization__alias', 'sTitle': 'organization', 'sWidth': 'auto', 'sClass': 'hide',
             'bSortable': True},
        ]

        common_headers = [
            {'mData': 'backhaul__bh_configured_on__ip_address', 'sTitle': 'BH IP', 'sWidth': 'auto',
             'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'backhaul__alias', 'sTitle': 'Backhaul', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'basestation__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'backhaul__bh_type', 'sTitle': 'BH Type', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'backhaul__bh_connectivity', 'sTitle': 'Onnet/Offnet', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'bh_port_name', 'sTitle': 'Configured On Port', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'basestation__city__city_name', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'basestation__state__state_name', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'backhaul__bh_configured_on__device_technology', 'sTitle': 'Technology', 'sClass': 'hidden-xs',
             'sWidth': 'auto', 'bSortable': True},
            {'mData': 'backhaul_capacity', 'sTitle': 'BH Capacity (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},

            {'mData': 'current_in_per', 'sTitle': 'DL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'current_in_val', 'sTitle': 'DL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'avg_in_per', 'sTitle': 'AVG DL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'avg_in_val', 'sTitle': 'AVG DL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'peak_in_per', 'sTitle': 'PEAK DL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'peak_in_val', 'sTitle': 'PEAK DL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'peak_in_timestamp', 'sTitle': 'PEAK Time', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},

            {'mData': 'current_out_per', 'sTitle': 'UL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'current_out_val', 'sTitle': 'UL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'avg_out_per', 'sTitle': 'AVG UL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'avg_out_val', 'sTitle': 'AVG UL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'peak_out_per', 'sTitle': 'PEAK UL (%)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'peak_out_val', 'sTitle': 'PEAK UL (mbps)', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'peak_out_timestamp', 'sTitle': 'PEAK Time', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': 'auto', 'bSortable': False},
        ]

        datatable_headers = []

        datatable_headers += hidden_headers

        datatable_headers += common_headers

        context['datatable_headers'] = json.dumps(datatable_headers)

        return context


class BackhaulStatusListing(BaseDatatableView, AdvanceFilteringMixin):
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

    order_columns = [
        'id',
        'severity',
        'age',
        'organization__alias',
        'backhaul__bh_configured_on__ip_address',
        'backhaul__alias',
        'basestation__alias',
        'backhaul__bh_type',
        'backhaul__bh_connectivity',
        'bh_port_name',
        'basestation__city__city_name',
        'basestation__state__state_name',
        'backhaul__bh_configured_on__device_technology',
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

    related_columns = [
        'basestation__city',
        'basestation__state',
        'backhaul__bh_configured_on',
        'organization'
    ]

    is_technology_searched = False

    is_technology_ordered = False

    def filter_queryset(self, qs):
        # sSearch = self.request.GET.get('sSearch', None)
        sSearch = self.request.GET.get('search[value]', None)
        self.is_technology_searched = False
        if sSearch:
            if sSearch.lower() in ['pmp', 'wimax', 'tcl pop', 'pop']:
                self.is_technology_searched = True
                prepared_data = self.prepare_results(qs)
                filtered_result = list()

                for data in prepared_data:
                    if sSearch.lower() in str(data).lower():
                        filtered_result.append(data)
                return self.advance_filter_queryset(filtered_result)
            else:
                query = []
                exec_query = "qs = qs.filter("
                for column in self.columns[:-1]:
                    query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

                exec_query += " | ".join(query)
                exec_query += ").values(*" + str(self.columns) + ")"
                exec exec_query
        return self.advance_filter_queryset(qs)

    def ordering(self, qs):
        """
         Get parameters from the request and prepare order by clause
        :param order_columns:
        :param self_instance:
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
        order_columns = self.get_order_columns()

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
            sortcol = order_columns[sort_col]

            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
            else:
                order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))

        if order:
            key_name = order[0][1:] if '-' in order[0] else order[0]
            if key_name == 'backhaul__bh_configured_on__device_technology':
                self.is_technology_ordered = True
                prepared_data = self.prepare_results(qs)
                filtered_result = list()
                for data in prepared_data:
                    filtered_result.append(data)
                sorted_device_data = sorted(
                    filtered_result,
                    key=itemgetter(key_name),
                    reverse=True if '-' in order[0] else False
                )
                return sorted_device_data

            # Try catch is added because in some cases
            # we receive instead of queryset
            try:
                sorted_device_data = qs.order_by(*order)
            except Exception, e:
                try:
                    sorted_device_data = sorted(
                        qs,
                        key=itemgetter(key_name),
                        reverse=True if '-' in order[0] else False
                    )
                except Exception, e:
                    sorted_device_data = qs
                    logger.info(e.message)
            return sorted_device_data
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
        json_data = [{key: val if val not in ['', 'undefined', 'None'] else "NA" for key, val in dct.items()} for dct in
                     qs]
        technology_object = DeviceTechnology.objects.all()

        for item in json_data:
            try:
                techno_name = technology_object.get(id=item['backhaul__bh_configured_on__device_technology']).alias
                device_id = item['backhaul__bh_configured_on__id']

                perf_page_link = ''
                if device_id:
                    performance_url = reverse(
                        'SingleDevicePerf',
                        kwargs={
                            'page_type': 'other',
                            'device_id': device_id
                        },
                        current_app='performance'
                    )
                    perf_page_link = '<a href="' + performance_url + '?is_util=1" \
                                      title="Device Performance"><i class="fa \
                                      fa-bar-chart-o text-info"></i></a>'

                item['actions'] = perf_page_link

                item['backhaul__bh_configured_on__device_technology'] = techno_name
                item['peak_out_timestamp'] = datetime.datetime.fromtimestamp(
                    float(item['peak_out_timestamp'])
                ).strftime(DATE_TIME_FORMAT) if str(item['peak_out_timestamp']) not in ['', 'undefined', 'None',
                                                                                        '0'] else 'NA'

                item['peak_in_timestamp'] = datetime.datetime.fromtimestamp(
                    float(item['peak_in_timestamp'])
                ).strftime(DATE_TIME_FORMAT) if str(item['peak_in_timestamp']) not in ['', 'undefined', 'None',
                                                                                       '0'] else 'NA'

            except Exception, e:
                logger.exception(e)
                continue

        return json_data

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request

        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        # total_records = qs.annotate(Count('sector_sector_id')).count()
        total_records = qs.annotate(Count('id')).count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        if type(qs) == type(list()):
            total_display_records = len(qs)
        else:
            total_display_records = qs.annotate(Count('id')).count()

        if total_display_records and total_records:
            # check if this has just initialised
            # if so : process the results

            qs = self.ordering(qs)
            qs = self.paging(qs)

            # if the qs is empty then JSON is unable to serialize the empty
            # ValuesQuerySet.Therefore changing its type to list.
            if not qs and isinstance(qs, ValuesQuerySet):
                qs = list(qs)

            if self.is_technology_searched or self.is_technology_ordered:
                aaData = qs
            else:
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
            {'mData': 'organization__alias', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hide',
             'bSortable': True},
        ]

        common_headers = [
            {'mData': 'backhaul__bh_configured_on__ip_address', 'sTitle': 'BH IP', 'sWidth': 'auto',
             'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'basestation__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'bh_port_name', 'sTitle': 'Configured On Port', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'backhaul__bh_connectivity', 'sTitle': 'Onnet/Offnet', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'backhaul__bh_configured_on__device_technology', 'sTitle': 'Technology', 'sWidth': 'auto',
             'bSortable': True},
            {'mData': 'backhaul_capacity', 'sTitle': 'BH Capacity (mbps)', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'backhaul__bh_type', 'sTitle': 'BH Type', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'basestation__city__city_name', 'sTitle': 'BS City', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'basestation__state__state_name', 'sTitle': 'BS State', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'current_out_per', 'sTitle': '% UL Utilization', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'current_in_per', 'sTitle': '% DL Utilization', 'sWidth': 'auto', 'sClass': 'hidden-xs',
             'bSortable': True},
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
        'basestation__alias',
        'bh_port_name',
        'backhaul__bh_connectivity',
        'backhaul__bh_configured_on__device_technology',
        'backhaul_capacity',
        'backhaul__bh_type',
        'basestation__city__city_name',
        'basestation__state__state_name',
        'organization__alias',
        'current_out_per',
        'current_in_per',
        'severity',
        'sys_timestamp',
        'age'
    ]

    order_columns = [
        'id',
        'organization__alias',
        'backhaul__bh_configured_on__ip_address',
        'basestation__alias',
        'bh_port_name',
        'backhaul__bh_connectivity',
        'backhaul__bh_configured_on__device_technology',
        'backhaul_capacity',
        'backhaul__bh_type',
        'basestation__city__city_name',
        'basestation__state__state_name',
        'current_out_per',
        'current_in_per',
        'severity',
        'age'
    ]

    related_columns = [
        'backhaul__bh_configured_on',
        'basestation__city',
        'basestation__state',
        'organization'
    ]

    is_technology_searched = False

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value """

        # sSearch = self.request.GET.get('sSearch', None)
        sSearch = self.request.GET.get('search[value]', None)

        if sSearch:
            # In case of severity search, update the search txt
            if sSearch.lower() in 'needs augmentation':
                sSearch = 'warning'
            elif sSearch in 'stop provisioning':
                sSearch = 'critical'
            else:
                pass

            # In case of technology search, search the text in
            # prepared result instead of queryset because we have
            # technology id in queryset not the name
            if sSearch.lower() in ['pmp', 'wimax', 'tcl pop', 'pop']:
                self.is_technology_searched = True
                prepared_data = self.prepare_results(qs)
                filtered_result = list()

                for data in prepared_data:
                    if sSearch.lower() in str(data).lower():
                        filtered_result.append(data)

                return self.advance_filter_queryset(filtered_result)
            else:
                self.is_technology_searched = False
                query = []
                exec_query = "qs = qs.filter("
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
        :param order_columns:
        :param self_instance:
        :param qs:
        """
        request = self.request
        is_alert_page = request.GET.get('is_alert_page', 0)

        if int(is_alert_page):
            self.order_columns = [
                'id',
                'organization__alias',
                'backhaul__bh_configured_on__ip_address',
                'basestation__alias',
                'bh_port_name',
                'backhaul__bh_configured_on__device_technology',
                'basestation__city__city_name',
                'basestation__state__state_name',
                'severity',
                'age'
            ]

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
            sortcol = self.order_columns[sort_col]
            sort_using = self.order_columns[sort_col]

            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
            else:
                order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))

        if order:
            # sort_using = order[0][1:] if '-' in order[0] else order[0]
            if sort_using == 'backhaul__bh_configured_on__device_technology':
                self.is_technology_ordered = True
                prepared_data = self.prepare_results(qs)
                # filtered_result = list()
                # for data in prepared_data:
                #     filtered_result.append(data)
                sorted_device_data = sorted(
                    prepared_data,
                    key=itemgetter(sort_using),
                    reverse=reverse
                )
                return sorted_device_data

            # Try catch is added because in some cases
            # we receive instead of queryset
            try:
                if sort_using == 'age':
                    updated_sort_column = 'difference'
                    if reverse:
                        updated_sort_column = '-difference'
                    sorted_device_data = qs.extra({
                        'difference': 'IF(age != 0 and sys_timestamp != 0, sys_timestamp - age, age)'
                    }).order_by(updated_sort_column)
                else:
                    sorted_device_data = qs.order_by(*order)
            except Exception, e:
                try:
                    sorted_device_data = sorted(
                        qs,
                        key=itemgetter(sort_using),
                        reverse=reverse
                    )
                except Exception, e:
                    sorted_device_data = qs
                    logger.error(e.message)
            return sorted_device_data
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

        # current_epoch_timestamp = datetime.datetime.now().strftime('%s')

        max_timestamp = self.model.objects.filter(
            Q(organization__in=kwargs['organizations']),
            Q(severity__in=['warning', 'critical'])
        ).aggregate(Max('sys_timestamp'))['sys_timestamp__max']
        
        backhauls = list()
        
        if max_timestamp:
            backhauls = self.model.objects.filter(
                Q(organization__in=kwargs['organizations']),
                Q(severity__in=['warning', 'critical']),
                Q(sys_timestamp__gte=max_timestamp - 420)
                # Q(age__lte=F('sys_timestamp') - 600)
            ).prefetch_related(*self.related_columns).values(*self.columns)

        return backhauls

    def prepare_results(self, qs):
        """
        """
        # data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        json_data = [{key: val if val not in ['', 'undefined', 'None'] else "" for key, val in dct.items()} for dct in qs]
        technology_object = DeviceTechnology.objects.all()

        for item in json_data:
            try:
                try:
                    techno_name = technology_object.get(id=item['backhaul__bh_configured_on__device_technology']).alias
                    item['backhaul__bh_configured_on__device_technology'] = techno_name
                except Exception, e:
                    pass

                if item['sys_timestamp'] and item['age']:
                    item['age'] = display_time(float(item['sys_timestamp']) - float(item['age']))
                else:
                    item['age'] = str(item['age']) + ' second'

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
        if type(qs) == type(list()):
            total_records = len(qs)
        else:
            total_records = qs.annotate(Count('id')).count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        if type(qs) == type(list()):
            total_display_records = len(qs)
        else:
            total_display_records = qs.annotate(Count('id')).count()

        if total_display_records and total_records:

            # check if this has just initialised
            # if so : process the results

            qs = self.ordering(qs)
            qs = self.paging(qs)

            # if the qs is empty then JSON is unable to serialize the empty
            # ValuesQuerySet.Therefore changing its type to list.
            if not qs and isinstance(qs, ValuesQuerySet):
                qs = list(qs)

            if self.is_technology_searched:
                aaData = qs
            else:
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

