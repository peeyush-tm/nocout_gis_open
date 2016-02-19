"""
==================================================================================
Module contains views and related functionality specific to 'activity_stream' app.
==================================================================================

Location:
* /nocout_gis/nocout/activity_stream/views.py

List of constructs:
=======
Classes
=======
* ActionList
* ActionListingTable

=======
Methods
=======
* log_user_action
"""

import json
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.db.models.query import ValuesQuerySet, Q
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django_datatables_view.base_datatable_view import BaseDatatableView
from user_profile.models import UserProfile, PowerLogs
from activity_stream.models import UserAction
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
# Import advance filtering mixin for BaseDatatableView
from nocout.mixins.datatable import AdvanceFilteringMixin

from nocout.mixins.permissions import PermissionsRequiredMixin
import logging

logger = logging.getLogger(__name__)


class ActionList(PermissionsRequiredMixin, ListView):
    """
    View to show headers of user log activity datatable.
        URL - 'http://127.0.0.1:8000/logs/actions/'
    """
    model = UserAction
    template_name = 'activity_stream/actions_logs.html'
    required_permissions = ('activity_stream.view_useraction',)

    def get_context_data(self, **kwargs):
        """
        Preparing the context variables required in the template rendering.
        """
        context = super(ActionList, self).get_context_data(**kwargs)
        context['datatable_headers'] = json.dumps(
            [
                {'mData': 'user_id', 'sTitle': 'User', 'sWidth': '15%', 'bSortable': True},
                {'mData': 'module', 'sTitle': 'Module', 'bSortable': True},
                {'mData': 'action', 'sTitle': 'Actions', 'bSortable': False},
                {'mData': 'logged_at', 'sTitle': 'Timestamp', 'sWidth': '17%', 'bSortable': True}
            ]
        )

        return context


class ActionListingTable(PermissionsRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    View to show list of user log activity in datatable.
        URL - 'http://127.0.0.1:8000/logs/actions/'
    """
    model = UserAction
    required_permissions = ('activity_stream.view_useraction',)
    columns = [
        'user_id',
        'action',
        'module',
        'logged_at'
    ]

    order_columns = columns

    # Create instance of 'NocoutUtilsGateway' class
    nocout_utils = NocoutUtilsGateway()

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        # get global search value
        sSearch = self.request.GET.get('search[value]', None)

        if sSearch and not self.pre_camel_case_notation:
            q = Q()
            for col in self.columns:
                if col == 'logged_at':
                    continue

                q |= Q(**{'%s__icontains' % col : sSearch})

            qs = qs.filter(q)
        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  initial queryset for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        # Get all the user ids of logged in user's organization.
        user_id_list = UserProfile.objects.filter(
            organization__in=self.nocout_utils.logged_in_user_organizations(self)
        ).values_list('id')

        # Show logs from start time to end time.
        start_time = datetime.today() - timedelta(days=30)
        end_time = datetime.today()

        # Get user logs of last 30 days for all fetched user id's.
        user_logs_resultset = UserAction.objects.filter(
            user_id__in=user_id_list,
            logged_at__gt=start_time,
            logged_at__lte=end_time,
        ).values(*self.columns).order_by('-logged_at')

        return user_logs_resultset

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            for dct in qs:
                dct['logged_at'] = self.nocout_utils.convert_utc_to_local_timezone(dct['logged_at'])
                user_id = dct['user_id']
                try:
                    dct['user_id'] = unicode(UserProfile.objects.get(id=user_id))
                except Exception, e:
                    dct['user_id'] = 'User Unknown/Deleted'
                    pass
            return list(qs)

        return []

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering, prepare and display the data on the datatable.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # Number of records before filtering.
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # Number of records after filtering.
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # If the 'qs' is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
        if not (qs and isinstance(qs, ValuesQuerySet)) and len(qs):
            qs = list(qs)

        # Preparing output data.
        aaData = self.prepare_results(qs)

        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }

        return ret


class PowerLogsInit(PermissionsRequiredMixin, ListView):
    """

    """
    model = PowerLogs
    template_name = 'activity_stream/power_logs.html'
    required_permissions = ('activity_stream.view_useraction',)

    def get_context_data(self, **kwargs):
        """
        Preparing the context variables required in the template rendering.
        """
        context = super(PowerLogsInit, self).get_context_data(**kwargs)
        context['datatable_headers'] = json.dumps([
            {'mData': 'user_id', 'sTitle': 'User', 'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'bSortable': True},
            {'mData': 'logged_at', 'sTitle': 'Timestamp', 'bSortable': True},
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'bSortable': True},
            {'mData': 'reason', 'sTitle': 'Reason', 'bSortable': True},
            {'mData': 'ss_ip', 'sTitle': 'SS IP', 'bSortable': True},
            {'mData': 'customer_alias', 'sTitle': 'Customer', 'bSortable': True}
        ])

        return context


class PowerLogsListing(PermissionsRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    """
    model = PowerLogs
    required_permissions = ('activity_stream.view_useraction',)
    columns = [
        'user_id',
        'action',
        'logged_at',
        'circuit_id',
        'reason',
        'ss_ip',
        'customer_alias'
    ]

    order_columns = columns

    # Create instance of 'NocoutUtilsGateway' class
    nocout_utils = NocoutUtilsGateway()

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        # get global search value
        sSearch = self.request.GET.get('search[value]', None)

        if sSearch and not self.pre_camel_case_notation:
            q = Q()
            for col in self.columns:
                if col == 'logged_at':
                    continue

                q |= Q(**{'%s__icontains' % col : sSearch})

            qs = qs.filter(q)
        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  initial queryset for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        # Get all the user ids of logged in user's organization.
        user_id_list = UserProfile.objects.filter(
            organization__in=self.nocout_utils.logged_in_user_organizations(self)
        ).values_list('id')

        # Show logs from start time to end time.
        start_time = datetime.today() - timedelta(days=30)
        end_time = datetime.today()

        # Get user logs of last 30 days for all fetched user id's.
        user_logs_resultset = self.model.objects.filter(
            user_id__in=user_id_list,
            logged_at__gt=start_time,
            logged_at__lte=end_time,
        ).values(*self.columns).order_by('-logged_at')

        return user_logs_resultset

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            for dct in qs:
                dct['logged_at'] = self.nocout_utils.convert_utc_to_local_timezone(dct['logged_at'])
                user_id = dct['user_id']
                try:
                    dct['user_id'] = unicode(UserProfile.objects.get(id=user_id))
                except Exception, e:
                    dct['user_id'] = 'User Unknown/Deleted'
                    pass
            return list(qs)

        return []

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering, prepare and display the data on the datatable.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # Number of records before filtering.
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # Number of records after filtering.
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # If the 'qs' is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
        if not (qs and isinstance(qs, ValuesQuerySet)) and len(qs):
            qs = list(qs)

        # Preparing output data.
        aaData = self.prepare_results(qs)

        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }

        return ret    


@csrf_exempt
def log_user_action(request):
    """
    Handle the request for logging action by logging user action in database.
    """
    if request.method == 'POST':
        try:
            obj = UserAction(user_id=request.user.id)
            obj.module = request.POST.get("module", "")  # form.cleaned_data['module']
            obj.action = request.POST.get("action", "")  # form.cleaned_data['action']
            obj.save()
            return HttpResponse(json.dumps({'success': True}))
        except Exception as e:
            logger.exception(e)
            return HttpResponse(json.dumps({'success': False}))
    else:
        return HttpResponse(json.dumps({'success': False}))
