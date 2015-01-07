from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext

from django.db.models import Q, Count
from django.db.models.query import ValuesQuerySet

from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView

import ujson as json

from inventory.models import Sector
from device.models import DeviceTechnology

#get the organisation of logged in user
from nocout.utils import logged_in_user_organizations

from capacity_management.models import SectorCapacityStatus

def get_daily_alerts(request, alert_type="default"):
    """
    get request to render daily alerts pages.

    :params request object:
    :params alert_type:
    :return Https response object:

    """

    if(alert_type == "sector"):
        alert_template = 'capacity_management/sector_capacity_alert.html'
    elif(alert_type == "backhaul"):
        alert_template = 'capacity_management/backhaul_capacity_alert.html'

    return render_to_response(alert_template,context_instance=RequestContext(request))


def get_utilization_status(request, status_type="default"):
    """
    get request to render utilization pages

    :params request object:
    :params status_type:
    :return Https response object:
    """

    if(status_type == "sector"):
        status_template = 'capacity_management/sector_capacity_status.html'
    elif(status_type == "backhaul"):
        status_template = 'capacity_management/backhaul_capacity_status.html'

    return render_to_response(status_template, context_instance=RequestContext(request))


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
            {'mData': 'sector', 'sTitle': 'Sector', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'severity', 'sTitle': 'severity', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'age', 'sTitle': 'age', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'organization__alias', 'sTitle': 'organization', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__device_technology', 'sTitle': 'Technology', 'sWidth': 'auto', 'sClass': 'hide', 'bSortable': True},
        ]

        common_headers = [
            {'mData': 'sector_sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__base_station__alias', 'sTitle': 'BS Name', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__base_station__city__city_name', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__base_station__state__state_name', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector__sector_configured_on__ip_address', 'sTitle': 'IP', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},
            {'mData': 'sector_capacity', 'sTitle': 'Capacity', 'sWidth': 'auto', 'sClass': 'hidden-xs', 'bSortable': True},

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

    columns = [
        'id',
        'sector',
        'sector_sector_id',
        'sector__base_station__alias',
        'sector__base_station__city__city_name',
        'sector__base_station__state__state_name',
        'sector__sector_configured_on__ip_address',
        'sector__sector_configured_on__device_technology',
        'sector_capacity',
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
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

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
                techno_name = technology_object.get(id=item['sector__sector_configured_on__device_technology']).alias
                item['sector__sector_configured_on__device_technology'] = techno_name
            except:
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
        total_records = qs.annotate(Count('sector_sector_id')).count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.annotate(Count('id')).count()

        #check if this has just initialised
        #if so : process the results

        qs = self.ordering(qs)
        qs = self.paging(qs)

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