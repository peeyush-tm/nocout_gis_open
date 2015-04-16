import json
from django.db.models.query import ValuesQuerySet, Q
from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.conf import settings
from user_profile.models import UserProfile

from django.http import HttpResponse
from activity_stream.models import UserAction

from datetime import datetime, timedelta
from pytz import timezone
from nocout.utils import logged_in_user_organizations
from nocout.utils.util import convert_utc_to_local_timezone
from nocout.mixins.permissions import PermissionsRequiredMixin

import logging

logger = logging.getLogger(__name__)


def time_converter(time_real):
    # Current time in UTC
    now_utc = time_real

    # Convert to Indoia time zone
    now_india = now_utc.astimezone(timezone(settings.TIME_ZONE))

    return now_india.strftime("%Y-%m-%d %H:%M:%S")


class ActionList(PermissionsRequiredMixin, ListView):
    """
    Class Based View for the User Log Activity
    """
    model = UserAction
    template_name = 'activity_stream/actions_logs.html'
    required_permissions = ('activity_stream.view_useraction',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

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


class ActionListingTable(PermissionsRequiredMixin, BaseDatatableView):
    """
    A generic class based view for the user log activity data table rendering.

    """
    model = UserAction
    required_permissions = ('activity_stream.view_useraction',)
    columns = [
        'user_id',
        'action',
        'module',
        'logged_at'
    ]

    # order_columns = ['-logged_at']
    order_columns = columns

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return result_list:
        """
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

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        startdate = datetime.now()
        enddate = startdate + timedelta(days=-30)

        user_logs_resultset = []

        # Get all the user ids of logged in user's organization
        user_id_list = UserProfile.objects.filter(
            organization__in=logged_in_user_organizations(self)
        ).values_list('id')

        # Get user logs of last 30 days for all fetched user ids
        user_logs_resultset = UserAction.objects.filter(
            user_id__in=user_id_list
        ).values(*self.columns).order_by('-logged_at')


        return user_logs_resultset

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        return list:

        """

        if qs:
            for dct in qs:
                dct['logged_at'] = convert_utc_to_local_timezone(dct['logged_at'])
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
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.

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
        if not (qs and isinstance(qs, ValuesQuerySet)) and len(qs):
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)

        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def log_user_action(request):
    """
    Method based view to log the user actions.
    """
    if request.method == 'POST':
        try:
            # form = UserActionForm(request.POST)
            obj = UserAction(user_id=request.user.id)
            obj.module = request.POST.get("module", "")  # form.cleaned_data['module']
            obj.action = request.POST.get("action", "")  #form.cleaned_data['action']
            obj.save()

            return HttpResponse(json.dumps({'success': True}))
        except Exception as e:
            logger.exception(e)
            return HttpResponse(json.dumps({'success': False}))
    else:
        return HttpResponse(json.dumps({'success': False}))