"""
Service impacting alarms
"""

from django.views.generic.list import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from alert_center.models import CurrentAlarms, ClearAlarms, HistoryAlarms
import json

class SIAListing(ListView):
    """
    View to render service impacting alarms page with appropriate column headers.
    """

    # need to associate ListView class with a model here
    model = CurrentAlarms
    template_name = 'alert_center/current_list.html'

    def get_context_data(self, **kwargs):
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
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.using('traps').values(*self.columns).all()


class CurrentAlarmsListingTable(SIAListingTable):
    model = CurrentAlarms


class ClearAlarmsListingTable(SIAListingTable):
    model = ClearAlarms
    

class HistoryAlarmsListingTable(SIAListingTable):
    model = HistoryAlarms
