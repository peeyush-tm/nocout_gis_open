import json
from actstream.models import Action
from django.db.models.query import ValuesQuerySet
from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.conf import settings
from user_profile.models import UserProfile
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from django.http import HttpResponse
from activity_stream.models import UserAction
from activity_stream.forms import UserActionForm

from datetime import datetime,timedelta
from pytz import timezone

import logging

logger = logging.getLogger(__name__)


def time_converter(time_real):

    # Current time in UTC
    now_utc = time_real

    # Convert to Indoia time zone
    now_india = now_utc.astimezone(timezone(settings.TIME_ZONE))

    return now_india.strftime("%Y-%m-%d %H:%M:%S")


class ActionList(ListView):
    """
    Class Based View for the User Log Activity
    """
    model = UserAction
    template_name = 'activity_stream/actions_logs.html'

    @method_decorator(permission_required('actstream.view_action', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.
        """
        return super(ActionList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """
        context=super(ActionList, self).get_context_data(**kwargs)
        context['datatable_headers'] = json.dumps([ {'mData':'user_id', 'sTitle' : 'User','sWidth':'15%','bSortable': True},
                                                    {'mData':'module', 'sTitle' : 'Module','bSortable': True},
                                                    {'mData':'action', 'sTitle' : 'Actions','bSortable': False},
                                                    {'mData':'logged_at', 'sTitle': 'Timestamp','sWidth':'17%','bSortable': True} ])
        return context


class ActionListingTable(BaseDatatableView):
    """
    A generic class based view for the user log activity data table rendering.

    """
    model = UserAction
    columns = [ 'logged_at']
    order_columns = ['-logged_at']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return result_list:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            user_ids_list = UserProfile.objects.filter(username__icontains=sSearch).values_list('id', flat=True)
            qs =UserAction.objects.filter( user_id__in=user_ids_list ).values('id', 'logged_at')
        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        startdate = datetime.now()
        enddate = startdate + timedelta(days=15)

        qs = []
        limit = 10
        offset = 0
        start = 0
        for x in range(0, UserAction.objects.count(), limit):
            offset = start + limit
            qs += UserAction.objects.filter(
                logged_at__range=(startdate.strftime("%Y-%m-%d 00:00:00"), enddate.strftime("%Y-%m-%d 00:00:00"))
            ).values("id", "logged_at")[start:offset]
            start += limit


        return qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        return list:

        """

        if qs:
            for dct in qs:
                dct['logged_at'] = time_converter(dct['logged_at'])
                # logger.debug(dct)
                for key, val in dct.items():
                    if key=='id':
                        action_object = UserAction.objects.get(pk= val)
                        dct['user_id'] = unicode(UserProfile.objects.get(id=action_object.user_id) )
                        dct['module'] = action_object.module
                        dct['action'] = action_object.action
                    else:
                        dct[key] = val
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
        # qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # qs = self.ordering(qs)
        # qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not (qs and isinstance(qs, ValuesQuerySet)) and len(qs):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret


def log_user_action(request):
    """
    Method based view to log the user actions.
    """
    if request.method == 'POST':
        form = UserActionForm(request.POST)
        if form.is_valid():
            obj = UserAction(user_id=request.user.id)
            obj.module = form.cleaned_data['module']
            obj.action = form.cleaned_data['action']
            obj.save()

            return HttpResponse(json.dumps({'success':True}))
        else:
            return HttpResponse(json.dumps({'success':False}))
    else:
        return HttpResponse(json.dumps({'success':False}))

