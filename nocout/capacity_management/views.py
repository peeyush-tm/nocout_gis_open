from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext

from django.db.models import Q, Count

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
        'sector_id',
        'bs_name'
        'city'
        'state'
        'ip_address',
        'technology',
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
        'organization__alias'
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
        ).values(*self.columns)

        return sectors


    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request

        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.annotate(Count('sector_id'))

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.annotate(Count('id'))

        #check if this has just initialised
        #if so : process the results

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # if the qs is empty then JSON is unable to serialize the empty
        # ValuesQuerySet.Therefore changing its type to list.
        if not qs:
            qs = list(qs)

        aaData = self.prepare_results(qs)
        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }
        return ret