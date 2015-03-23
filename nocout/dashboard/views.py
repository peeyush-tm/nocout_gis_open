import json
import datetime
import calendar
from dateutil import relativedelta
import time

from django.utils.dateformat import format
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q, Count, Sum, Avg

from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_datatables_view.base_datatable_view import BaseDatatableView

# nocout project settings # TODO: Remove the HARDCODED technology IDs
from nocout.settings import PMP, WiMAX, TCLPOP, DEBUG, PERIODIC_POLL_PROCESS_COUNT

from nocout.utils import logged_in_user_organizations
# from nocout.utils.util import convert_utc_to_local_timezone
from inventory.models import Sector
from device.models import DeviceTechnology, Device
from performance.models import ServiceStatus, NetworkAvailabilityDaily, UtilizationStatus, \
    Topology, NetworkStatus, RfNetworkAvailability

# inventory utils
from inventory.utils.util import organization_customer_devices, organization_network_devices, \
    organization_sectors, prepare_machines, organization_backhaul_devices
#inventory utils

from performance.utils.util import color_picker

from dashboard.models import DashboardSetting, MFRDFRReports, DFRProcessed, MFRProcessed, MFRCauseCode, \
    DashboardRangeStatusTimely, DashboardSeverityStatusTimely, DashboardSeverityStatusDaily, DashboardRangeStatusDaily
from dashboard.forms import DashboardSettingForm, MFRDFRReportsForm
from dashboard.utils import get_service_status_results, get_dashboard_status_range_counter, \
    get_pie_chart_json_response_dict, \
    get_dashboard_status_sector_range_counter, get_topology_status_results, get_highchart_response, \
    get_unused_dashboards, get_range_status, get_guege_chart_max_n_stops
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.permissions import SuperUserRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin, ValuesQuerySetMixin


class DashbaordSettingsListView(TemplateView):
    """
    Class Based View for the Dashboard data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'dashboard/dashboard_settings_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DashbaordSettingsListView, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'page_name', 'sTitle': 'Page Name', 'sWidth': 'auto', },
            {'mData': 'technology__name', 'sTitle': 'Technology Name', 'sWidth': 'auto', },
            {'mData': 'name', 'sTitle': 'Dashboard Name', 'sWidth': 'auto', },
            {'mData': 'range1', 'sTitle': 'Range 1', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'range2', 'sTitle': 'Range 2', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'range3', 'sTitle': 'Range 3', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'range4', 'sTitle': 'Range 4', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'range5', 'sTitle': 'Range 5', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'range6', 'sTitle': 'Range 6', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'range7', 'sTitle': 'Range 7', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'range8', 'sTitle': 'Range 8', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'range9', 'sTitle': 'Range 9', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'range10', 'sTitle': 'Range 10', 'sWidth': 'auto', 'bSortable': False},
        ]

        #if the user is superuser then the action column will appear on the datatable
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DashbaordSettingsListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    """
    Class based View to render Dashboard Settings Data table.
    """
    model = DashboardSetting
    columns = ['page_name', 'name', 'technology__name', 'range1', 'range2', 'range3', 'range4', 'range5', 'range6',
               'range7', 'range8', 'range9', 'range10']
    keys = ['page_name', 'technology__name', 'name', 'range1_start', 'range2_start', 'range3_start', 'range4_start',
            'range5_start', 'range6_start', 'range7_start', 'range8_start', 'range9_start', 'range10_start',
            'range1_end', 'range2_end', 'range3_end', 'range4_end', 'range5_end', 'range6_end', 'range7_end',
            'range8_end', 'range9_end', 'range10_end', 'range1_color_hex_value', 'range2_color_hex_value',
            'range3_color_hex_value', 'range4_color_hex_value', 'range5_color_hex_value', 'range6_color_hex_value',
            'range7_color_hex_value', 'range8_color_hex_value', 'range9_color_hex_value', 'range10_color_hex_value']
    order_columns = ['page_name', 'name', 'technology__name']
    columns = ['page_name', 'technology__name', 'name', 'range1_start', 'range2_start', 'range3_start', 'range4_start',
               'range5_start', 'range6_start', 'range7_start', 'range8_start', 'range9_start', 'range10_start',
               'range1_end', 'range2_end', 'range3_end', 'range4_end', 'range5_end', 'range6_end', 'range7_end',
               'range8_end', 'range9_end', 'range10_end', 'range1_color_hex_value', 'range2_color_hex_value',
               'range3_color_hex_value', 'range4_color_hex_value', 'range5_color_hex_value', 'range6_color_hex_value',
               'range7_color_hex_value', 'range8_color_hex_value', 'range9_color_hex_value', 'range10_color_hex_value']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for obj in json_data:
            for i in range(1, 11):
                range_start = obj.pop('range%d_start' % i)
                range_end = obj.pop('range%d_end' % i)
                color_hex_value = obj.pop('range%d_color_hex_value' % i)
                range_color = "<div style='display:block; height:20px; width:20px;\
                        background:{0}'></div>".format(color_hex_value)
                if range_start:
                    obj.update({'range%d' % i: "(%s -<br>%s)<br>%s" % (range_start, range_end, range_color)})
                else:
                    obj.update({'range%d' % i: ""})

                    # Add actions to obj.
            obj_id = obj.pop('id')
            edit_url = reverse_lazy('dashboard-settings-update', kwargs={'pk': obj_id})
            delete_url = reverse_lazy('dashboard-settings-delete', kwargs={'pk': obj_id})
            edit_action = '<a href="%s"><i class="fa fa-pencil text-dark"></i></a>' % edit_url
            delete_action = '<a href="%s"><i class="fa fa-trash-o text-danger"></i></a>' % delete_url
            obj.update({'actions': edit_action + ' ' + delete_action})
        return json_data


class DashbaordSettingsCreateView(SuperUserRequiredMixin, CreateView):
    """
    Class based view to create new Dashboard Setting.
    """
    model = DashboardSetting
    form_class = DashboardSettingForm
    template_name = "dashboard/dashboard_settings_new.html"
    success_url = reverse_lazy('dashboard-settings')

    def get_context_data(self, **kwargs):
        context = super(DashbaordSettingsCreateView, self).get_context_data(**kwargs)
        context['dashboards'] = get_unused_dashboards()
        technology_options = dict(DeviceTechnology.objects.values_list('name', 'id'))
        technology_options.update({'All': ''})
        context['technology_options'] = json.dumps(technology_options)
        return context


class DashbaordSettingsDetailView(DetailView):
    """
    Class based view to render the Dashboard Setting detail.
    """
    model = DashboardSetting
    template_name = 'dashboard/dashboard_detail.html'


class DashbaordSettingsUpdateView(SuperUserRequiredMixin, UpdateView):
    """
    Class based view to update Dashboard Setting.
    """
    model = DashboardSetting
    form_class = DashboardSettingForm
    template_name = "dashboard/dashboard_settings_update.html"
    success_url = reverse_lazy('dashboard-settings')

    def get_context_data(self, **kwargs):
        context = super(DashbaordSettingsUpdateView, self).get_context_data(**kwargs)
        context['dashboards'] = get_unused_dashboards(dashboard_setting_id=self.object.id)
        technology_options = dict(DeviceTechnology.objects.values_list('name', 'id'))
        technology_options.update({'All': ''})
        context['technology_options'] = json.dumps(technology_options)
        return context


class DashbaordSettingsDeleteView(SuperUserRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Dashboard Setting.

    """
    model = DashboardSetting
    template_name = 'dashboard/dashboard_settings_delete.html'
    success_url = reverse_lazy('dashboard-settings')
    obj_alias = 'name'


# ****************************************** RF PERFORMANCE DASHBOARD ********************************************


class PerformanceDashboardMixin(object):
    """
    Provide common method get for Performance Dashboard.

    To use this Mixin set `template_name` and implement method get_init_data to provide following attributes:

        - data_source_config
        - technology
        - devices_method_to_call
        - devices_method_kwargs
    """

    def get(self, request):
        """
        Handles the get request

        :param request:
        :return Http response object:
        """
        data_source_config, technology, devices_method_to_call, devices_method_kwargs, is_bh = self.get_init_data()
        template_dict = {
            'data_sources': json.dumps(data_source_config.keys()),
            'parallel_calling_count' : PERIODIC_POLL_PROCESS_COUNT
        }

        data_source = request.GET.get('data_source')
        if not data_source:
            return render(self.request, self.template_name, dictionary=template_dict)

        # Get Service Name from queried data_source
        try:
            service_name = data_source_config[data_source]['service_name']
            model = data_source_config[data_source]['model']
        except KeyError as e:
            return render(self.request, self.template_name, dictionary=template_dict)

        try:
            dashboard_setting = DashboardSetting.objects.get(technology=technology, page_name='rf_dashboard',
                                                             name=data_source, is_bh=is_bh)
        except DashboardSetting.DoesNotExist as e:
            return HttpResponse(json.dumps({
                "message": "Corresponding dashboard setting is not available.",
                "success": 0
            }))

        # Get User's organizations
        # (admin : organization + sub organization)
        # (operator + viewer : same organization)
        user_organizations = logged_in_user_organizations(self)

        # Get Devices of User's Organizations. [and are Sub Station]
        user_devices = devices_method_to_call(user_organizations, technology, **devices_method_kwargs)

        service_status_results = get_service_status_results(
            user_devices, model=model, service_name=service_name, data_source=data_source
        )

        range_counter = get_dashboard_status_range_counter(dashboard_setting, service_status_results)

        response_dict = get_pie_chart_json_response_dict(dashboard_setting, data_source, range_counter)

        return HttpResponse(json.dumps(response_dict))


class WiMAX_Performance_Dashboard(PerformanceDashboardMixin, View):
    """
    The Class based View to get performance dashboard page requested.

    """

    template_name = 'rf_performance/wimax.html'

    def get_init_data(self):
        """
        Handles the get request

        :param request:
        :return Http response object:
        """
        data_source_config = {
            'ul_rssi': {'service_name': 'wimax_ul_rssi', 'model': ServiceStatus},
            'dl_rssi': {'service_name': 'wimax_dl_rssi', 'model': ServiceStatus},
            'ul_cinr': {'service_name': 'wimax_ul_cinr', 'model': ServiceStatus},
            'dl_cinr': {'service_name': 'wimax_dl_cinr', 'model': ServiceStatus},
            'modulation_ul_fec': {'service_name': 'wimax_modulation_ul_fec', 'model': ServiceStatus},
            'modulation_dl_fec': {'service_name': 'wimax_modulation_dl_fec', 'model': ServiceStatus},
        }
        technology = DeviceTechnology.objects.get(name__icontains='WiMAX').id
        devices_method_to_call = organization_customer_devices
        devices_method_kwargs = dict(specify_ptp_type='all')
        is_bh = False
        return data_source_config, technology, devices_method_to_call, devices_method_kwargs, is_bh


class PMP_Performance_Dashboard(PerformanceDashboardMixin, View):
    """
    The Class based View to get performance dashboard page requested.

    """
    template_name = 'rf_performance/pmp.html'

    def get_init_data(self):
        """
        Provide data for mixin's get method.
        """

        data_source_config = {
            'ul_jitter': {'service_name': 'cambium_ul_jitter', 'model': ServiceStatus},
            'dl_jitter': {'service_name': 'cambium_dl_jitter', 'model': ServiceStatus},
            'rereg_count': {'service_name': 'cambium_rereg_count', 'model': ServiceStatus},
            'ul_rssi': {'service_name': 'cambium_ul_rssi', 'model': ServiceStatus},
            'dl_rssi': {'service_name': 'cambium_dl_rssi', 'model': ServiceStatus},
        }
        technology = DeviceTechnology.objects.get(name='PMP').id
        devices_method_to_call = organization_customer_devices
        devices_method_kwargs = dict(specify_ptp_type='all')
        is_bh = False
        return data_source_config, technology, devices_method_to_call, devices_method_kwargs, is_bh


class PTP_Performance_Dashboard(PerformanceDashboardMixin, View):
    """
    The Class based View to get performance dashboard page requested.

    """
    template_name = 'rf_performance/ptp.html'

    def get_init_data(self):
        """
        Provide data for mixin's get method.
        """

        data_source_config = {
            'rssi': {'service_name': 'radwin_rssi', 'model': ServiceStatus},
            'uas': {'service_name': 'radwin_uas', 'model': ServiceStatus},
        }
        technology = DeviceTechnology.objects.get(name='P2P').id
        devices_method_to_call = organization_customer_devices
        devices_method_kwargs = dict(specify_ptp_type='all')
        is_bh = False
        return data_source_config, technology, devices_method_to_call, devices_method_kwargs, is_bh


class PTPBH_Performance_Dashboard(PerformanceDashboardMixin, View):
    """
    The Class based View to get performance dashboard page requested.

    """
    template_name = 'rf_performance/ptp_bh.html'

    def get_init_data(self):
        """
        Provide data for mixin's get method.
        """

        data_source_config = {
            'rssi': {'service_name': 'radwin_rssi', 'model': ServiceStatus},
            'availability': {'service_name': 'availability', 'model': NetworkAvailabilityDaily},
            'uas': {'service_name': 'radwin_uas', 'model': ServiceStatus},
        }
        technology = DeviceTechnology.objects.get(name='P2P').id
        devices_method_to_call = organization_network_devices
        devices_method_kwargs = dict(specify_ptp_bh_type='all')
        is_bh = True
        return data_source_config, technology, devices_method_to_call, devices_method_kwargs, is_bh


# ####################################### MFR DFR Reports ########################################

class MFRDFRReportsListView(TemplateView):
    """
    Class Based View for the MFR-DFR-Reports data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'mfrdfr/mfr_dfr_reports_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(MFRDFRReportsListView, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Report Name', 'sWidth': 'auto', },
            {'mData': 'type', 'sTitle': 'Report Type', 'sWidth': 'auto'},
            {'mData': 'is_processed', 'sTitle': 'Processed', 'sWidth': 'auto'},
            {'mData': 'process_for', 'sTitle': 'Process For', 'sWidth': 'auto'},
        ]

        # if the user is superuser then the action column will appear on the datatable
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class MFRDFRReportsListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    model = MFRDFRReports
    columns = ['name', 'type', 'is_processed', 'process_for']
    search_columns = ['name', 'type', 'is_processed']
    order_columns = ['name', 'type', 'is_processed', 'process_for']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for obj in json_data:
            obj['is_processed'] = 'Yes' if obj['is_processed'] else 'No'
            obj_id = obj.pop('id')
            delete_url = reverse_lazy('mfr-dfr-reports-delete', kwargs={'pk': obj_id})
            delete_action = '<a href="%s"><i class="fa fa-trash-o text-danger"></i></a>' % delete_url
            obj.update({'actions': delete_action})
        return json_data


class MFRDFRReportsCreateView(CreateView):
    model = MFRDFRReports
    form_class = MFRDFRReportsForm
    template_name = "mfrdfr/mfr_dfr_reports_upload.html"
    success_url = reverse_lazy('mfr-dfr-reports-list')

    def form_valid(self, form):
        response = super(MFRDFRReportsCreateView, self).form_valid(form)
        self.object.absolute_path = self.object.upload_to.path
        self.object.save()
        return response


class MFRDFRReportsDeleteView(UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Dashboard Setting.

    """
    model = MFRDFRReports
    template_name = 'mfrdfr/mfr_dfr_reports_delete.html'
    success_url = reverse_lazy('mfr-dfr-reports-list')
    obj_alias = 'name'


class DFRProcessedListView(TemplateView):
    """
    Class Based View for the DFR-Processed data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'mfrdfr/dfr_processed_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DFRProcessedListView, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'processed_for__name', 'sTitle': 'Uploaded Report Name', 'sWidth': 'auto', },
            {'mData': 'processed_for__process_for', 'sTitle': 'Report Processed For', 'sWidth': 'auto'},
            {'mData': 'processed_on', 'sTitle': 'Processed On (Date)', 'sWidth': 'auto'},
            {'mData': 'processed_key', 'sTitle': 'Key for Processing', 'sWidth': 'auto'},
            {'mData': 'processed_value', 'sTitle': 'Value for Processing', 'sWidth': 'auto'},
            {'mData': 'processed_report_path', 'sTitle': 'Processed Report', 'sWidth': 'auto', 'bSortable': False},
        ]

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DFRProcessedListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    model = DFRProcessed
    columns = ['processed_for__name', 'processed_for__process_for', 'processed_on', 'processed_key', 'processed_value']
    search_columns = ['processed_for__name', 'processed_key', 'processed_value']
    order_columns = ['processed_for__name', 'processed_for__process_for', 'processed_on', 'processed_key',
                     'processed_value']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for obj in json_data:
            processed_report_path = reverse('dfr-processed-reports-download', kwargs={'pk': obj.pop('id')})
            obj['processed_report_path'] = '<a href="' + processed_report_path + '" target="_blank">' + \
                                           '<img src="/static/img/ms-office-icons/excel_2013_green.png" ' + \
                                           'style="float:left; display:block; height:25px; width:25px;"></a>'
        return json_data


def dfr_processed_report_download(request, pk):
    dfr_processed = DFRProcessed.objects.get(id=pk)

    f = file(dfr_processed.processed_report_path, 'r')
    response = HttpResponse(f.read(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="dfr_report_' + str(
        dfr_processed.processed_for.process_for) + '.xlsx"'
    return response


# ***************************************** DFR-REPORTS *******************************************************

class DFRReportsListView(TemplateView):
    """
    Class Based View for the DFR-Reports data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'dfr/dfr_reports_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DFRReportsListView, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Report Name', 'sWidth': 'auto', },
            {'mData': 'is_processed', 'sTitle': 'Processed', 'sWidth': 'auto'},
            {'mData': 'process_for', 'sTitle': 'Process For', 'sWidth': 'auto'},
        ]

        #if the user is superuser then the action column will appear on the datatable
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DFRReportsListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    model = MFRDFRReports
    columns = ['name', 'is_processed', 'process_for']
    search_columns = ['name', 'is_processed']
    order_columns = ['name', 'is_processed', 'process_for']

    def get_initial_queryset(self):
        qs = super(DFRReportsListingTable, self).get_initial_queryset()
        qs = qs.filter(type='DFR')
        return qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for obj in json_data:
            obj['is_processed'] = 'Yes' if obj['is_processed'] else 'No'
            obj_id = obj.pop('id')
            delete_url = reverse_lazy('dfr-reports-delete', kwargs={'pk': obj_id})
            delete_action = '<a href="%s"><i class="fa fa-trash-o text-danger"></i></a>' % delete_url
            obj.update({'actions': delete_action})
        return json_data


class DFRReportsDeleteView(UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Dashboard Setting.

    """
    model = MFRDFRReports
    template_name = 'mfrdfr/mfr_dfr_reports_delete.html'
    success_url = reverse_lazy('dfr-reports-list')
    obj_alias = 'name'


# ********************************************** MFR-Reports ************************************************


class MFRReportsListView(TemplateView):
    """
    Class Based View for the MFR-Reports data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'mfr/mfr_reports_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(MFRReportsListView, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Report Name', 'sWidth': 'auto', },
            {'mData': 'is_processed', 'sTitle': 'Processed', 'sWidth': 'auto'},
            {'mData': 'process_for', 'sTitle': 'Process For', 'sWidth': 'auto'},
        ]

        #if the user is superuser then the action column will appear on the datatable
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class MFRReportsListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    model = MFRDFRReports
    columns = ['name', 'is_processed', 'process_for']
    search_columns = ['name', 'is_processed']
    order_columns = ['name', 'is_processed', 'process_for']

    def get_initial_queryset(self):
        qs = super(MFRReportsListingTable, self).get_initial_queryset()
        qs = qs.filter(type='MFR')
        return qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for obj in json_data:
            obj['is_processed'] = 'Yes' if obj['is_processed'] else 'No'
            obj_id = obj.pop('id')
            delete_url = reverse_lazy('dfr-reports-delete', kwargs={'pk': obj_id})
            delete_action = '<a href="%s"><i class="fa fa-trash-o text-danger"></i></a>' % delete_url
            obj.update({'actions': delete_action})
        return json_data


class MFRReportsDeleteView(UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Dashboard Setting.

    """
    model = MFRDFRReports
    template_name = 'mfrdfr/mfr_dfr_reports_delete.html'
    success_url = reverse_lazy('mfr-reports-list')
    obj_alias = 'name'


# **************************************** Main Dashbaord ***************************************#


class MainDashboard(View):
    """
    The Class based View to return Main Dashboard.

    Following are charts included in main-dashboard:

        - WiMAX Sector Capicity
        - PMP Sector Capicity
        - WiMAX Sales Oppurtunity
        - PMP Sales Oppurtunity
        - WiMAX Backhaul Capicity
        - PMP Backhaul Capicity
        - Current Alarm (WiMAX, PMP, PTP BH and All)
        - Network Latency (WiMAX, PMP, PTP BH and All)
        - Packet Drop (WiMAX, PMP, PTP BH and All)
        - Temperature (WiMAX, PMP, PTP BH and All)
        - PTP RAP Backhaul
        - City Charter
        - MFR Cause Code
        - MFR Processed
    """
    template_name = 'main_dashboard/home.html'

    def get(self, request):
        """
        Handles the get request

        :param request:
        :return Http response object:
        """

        # City Charter tables Columns list

        common_headers = [
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto'},
            {'mData': 'city_name', 'sTitle': 'City', 'sWidth': 'auto'},
            {'mData': 'state_name', 'sTitle': 'State', 'sWidth': 'auto'},
            {'mData': 'customer_name', 'sTitle': 'Customer', 'sWidth': 'auto'},
            {'mData': 'bs_name', 'sTitle': 'Base Station', 'sWidth': 'auto'},
            {'mData': 'packetDrop', 'sTitle': 'PD', 'sWidth': 'auto'},
            {'mData': 'Latencydrop', 'sTitle': 'RTA', 'sWidth': 'auto'},
            {'mData': 'device_state', 'sTitle': 'Device State', 'sWidth': 'auto'},
            {'mData': 'current_value', 'sTitle': 'Current Value', 'sWidth': 'auto'},
            {'mData': 'ul', 'sTitle': 'UL', 'sWidth': 'auto'},
            {'mData': 'latency', 'sTitle': 'Latency', 'sWidth': 'auto'},
            {'mData': 'pd', 'sTitle': 'Packet Drop', 'sWidth': 'auto'}
        ]

        common_few_headers = [
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto'},
            {'mData': 'city_name', 'sTitle': 'City', 'sWidth': 'auto'},
            {'mData': 'bs_name', 'sTitle': 'Base Station', 'sWidth': 'auto'},
        ]

        sectors_common_headers = [
            {'mData': 'vendor', 'sTitle': 'Vendor', 'sWidth': 'auto'},
            {'mData': 'ss_device_technology_name', 'sTitle': 'SS Technology', 'sWidth': 'auto'},
            {'mData': 'device_ss_ip_address', 'sTitle': 'SS IP', 'sWidth': 'auto'},
            {'mData': 'device_ss_mac_address', 'sTitle': 'SS MAC', 'sWidth': 'auto'},
            {'mData': 'sector_device_ip_address', 'sTitle': 'Near End IP', 'sWidth': 'auto'},
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'auto'},
            {'mData': 'dl_rssi_during_aceptance', 'sTitle': 'DL RSSI Acceptance', 'sWidth': 'auto'},
            {'mData': 'intrf', 'sTitle': 'INTRF', 'sWidth': 'auto'},
        ]

        wimax_specific_headers = [
            {'mData': 'seg_wimax', 'sTitle': 'Seg WiMAX', 'sWidth': 'auto'},
            {'mData': 'pmp', 'sTitle': 'PMP Port', 'sWidth': 'auto'},
            {'mData': 'ul_cinr', 'sTitle': 'UL CINR', 'sWidth': 'auto'},
            {'mData': 'dl_cinr', 'sTitle': 'DL CINR', 'sWidth': 'auto'},
            {'mData': 'ptx', 'sTitle': 'PTX', 'sWidth': 'auto'}
        ]

        wimax_specific_few_headers = [
            {'mData': 'seg_wimax', 'sTitle': 'Seg WiMAX', 'sWidth': 'auto'}
        ]

        pmp_specific_headers = [
            {'mData': 'seg_pmp', 'sTitle': 'Seg PMP', 'sWidth': 'auto'},
            {'mData': 'ul_jitter', 'sTitle': 'UL Jitter', 'sWidth': 'auto'},
            {'mData': 'dl_jitter', 'sTitle': 'DL Jitter', 'sWidth': 'auto'},
            {'mData': 'rereg_count', 'sTitle': 'Rereg Count', 'sWidth': 'auto'},
            {'mData': 'reg_count', 'sTitle': 'Reg Count', 'sWidth': 'auto'},
        ]

        pmp_specific_few_headers = [
            {'mData': 'seg_pmp', 'sTitle': 'Seg PMP', 'sWidth': 'auto'}
        ]

        ptp_specific_headers = [
            {'mData': 'seg_p2p', 'sTitle': 'Seg P2P', 'sWidth': 'auto'},
            {'mData': 'technology', 'sTitle': 'Technology', 'sWidth': 'auto'},
            {'mData': 'far_ip', 'sTitle': 'Farend IP', 'sWidth': 'auto'},
            {'mData': 'near_ip', 'sTitle': 'Nearend IP', 'sWidth': 'auto'},
            {'mData': 'circuit_type', 'sTitle': 'Circuit Type', 'sWidth': 'auto'},
            {'mData': 'far_device_ss_mac_address', 'sTitle': 'Farend MAC', 'sWidth': 'auto'},
            {'mData': 'near_sector_device_mac_address', 'sTitle': 'Nearend MAC', 'sWidth': 'auto'},
            {'mData': 'rssi_during_aceptance', 'sTitle': 'RSSI During Acceptance', 'sWidth': 'auto'},
            {'mData': 'uas', 'sTitle': 'UAS', 'sWidth': 'auto'}
        ]

        ptp_specific_few_headers = [
            {'mData': 'seg_p2p', 'sTitle': 'Seg P2P', 'sWidth': 'auto'}
        ]

        # P2P Table All Columns
        ptp_charter_all_headers = []
        ptp_charter_all_headers += common_headers
        ptp_charter_all_headers += ptp_specific_headers

        # P2P Table Few Columns
        ptp_charter_few_headers = []
        ptp_charter_few_headers += common_few_headers
        ptp_charter_few_headers += ptp_specific_few_headers

        # PMP Table All Columns
        pmp_charter_all_headers = []
        pmp_charter_all_headers += common_headers
        pmp_charter_all_headers += sectors_common_headers
        pmp_charter_all_headers += pmp_specific_headers

        # PMP Table Few Columns
        pmp_charter_few_headers = []
        pmp_charter_few_headers += common_few_headers
        pmp_charter_few_headers += pmp_specific_few_headers

        # WiMAX Table All Columns
        wimax_charter_all_headers = []
        wimax_charter_all_headers += common_headers
        wimax_charter_all_headers += sectors_common_headers
        wimax_charter_all_headers += wimax_specific_headers

        # WiMAX Table Few Columns
        wimax_charter_few_headers = []
        wimax_charter_few_headers += common_few_headers
        wimax_charter_few_headers += wimax_specific_few_headers


        context = {
            "isOther": 0,
            "page_title": "Main Dashboard",
            "debug" : 0,
            "ptp_charter_few_headers" : json.dumps(ptp_charter_few_headers),
            "pmp_charter_few_headers" : json.dumps(pmp_charter_few_headers),
            "wimax_charter_few_headers" : json.dumps(wimax_charter_few_headers),
            "ptp_charter_all_headers" : json.dumps(ptp_charter_all_headers),
            "pmp_charter_all_headers" : json.dumps(pmp_charter_all_headers),
            "wimax_charter_all_headers" : json.dumps(wimax_charter_all_headers),
            "process_count" : PERIODIC_POLL_PROCESS_COUNT
        }

        if DEBUG:
            context['debug'] = 1
        
        if 'isOther' in self.request.GET:
            context['isOther'] = self.request.GET['isOther']
            context['page_title'] = "RF Main Dashboard"

        return render(self.request, self.template_name, context)


class MFRCauseCodeView(View):
    """
    Class Based View for the MFR-Cause-Code Dashboard.
    """

    def get(self, request):
        '''
        Handles the get request

        :param request:
        :retun dictionary containing data used for main dashboard charts.
        '''
        mfr_reports = MFRDFRReports.objects.order_by('-process_for').filter(is_processed=1)

        chart_series = []
        if mfr_reports.exists():
            last_mfr_report = mfr_reports[0]
            year_month_str = ""
            if last_mfr_report.process_for:
                datetime_str = unicode(last_mfr_report.process_for)+" 00:00:00"
                date_object = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                if date_object:
                    year_month_str = unicode(date_object.strftime('%B'))+" - "+unicode(date_object.year)
        else:
            # get the chart_data for the pie chart.
            response = get_highchart_response(dictionary={'type': 'pie', 'chart_series': chart_series,
                                                          'title': 'MFR Cause Code', 'name': ''})
            return HttpResponse(response)

        results = MFRCauseCode.objects.filter(processed_for=last_mfr_report).values('processed_key', 'processed_value')
        for result in results:
            chart_series.append([
                "%s : %s" % (result['processed_key'], result['processed_value']),
                int(result['processed_value'])
            ])

        # get the chart_data for the pie chart.
        response = get_highchart_response(dictionary={'type': 'pie', 'chart_series': chart_series,
                                                      'title': 'MFR Cause Code', 'name': ''})

        # Add year month string of Uploaded MFR caused code report to updated dict
        json_response = json.loads(response)

        try:
            if 'timestamp' not in json_response['data']['objects']:
                json_response['data']['objects']['timestamp'] = ''

            json_response['data']['objects']['timestamp'] = year_month_str
        except Exception, e:
            pass

        response = json.dumps(json_response)

        return HttpResponse(response)


class MFRProcesedView(View):
    """
    Class Based View for the MFR-Cause-Code Dashboard.
    """

    def get(self, request):
        '''
        Handles the get request

        :param request:
        :retun dictionary containing data used for main dashboard charts.
        '''
        # Start Calculations for MFR Processed.
        # Last 12 Months
        year_before = datetime.date.today() - datetime.timedelta(days=365)
        year_before = datetime.date(year_before.year, year_before.month, 1)

        # colors_list = [
        #     "#2b908f",
        #     "#90ee7e",
        #     "#f45b5b",
        #     "#7798BF",
        #     "#aaeeee",
        #     "#ff0066",
        #     "#eeaaee",
        #     "#55BF3B",
        #     "#DF5353",
        #     '#008B8B',
        #     '#556B2F',
        #     '#8FBC8F',
        #     '#00CED1',
        #     '#FFA07A',
        #     '#663399',
        #     '#6A5ACD',
        #     '#8470FF',
        #     '#00C5CD',
        #     '#FF7F24',
        #     '#7ec0ee',
        #     '#6495ed'
        # ]

        mfr_processed_results = MFRProcessed.objects.filter(processed_for__process_for__gte=year_before).values(
            'processed_key', 'processed_value', 'processed_for__process_for')

        day = year_before
        # area_chart_categories = []
        processed_key_dict = {result['processed_key']: [] for result in mfr_processed_results}
        # processed_key_color = {result['processed_key']: color_picker() for result in mfr_processed_results}


        # # MFR PROCESS KEYS LIST
        # mfr_process_keys = mfr_processed_results.values_list('processed_key', flat=True)
        # # Numeric counter used to get the color from specific list index 
        # processed_key_color = {}
        # color_counter = 0
        # for key in mfr_process_keys:
        #     if key not in processed_key_color: 
        #         processed_key_color[key] = ""

        #     processed_key_color[key] = ''
        #     # Increment the color index counter
        #     color_counter += 1



        while day <= datetime.date.today():
            #area_chart_categories.append(datetime.date.strftime(day, '%b %y'))

            processed_keys = processed_key_dict.keys()
            for result in mfr_processed_results:
                result_date = result['processed_for__process_for']
                if result_date.year == day.year and result_date.month == day.month:
                    processed_key_dict[result['processed_key']].append({
                        # "color": processed_key_color[result['processed_key']],
                        "color": '',
                        "y": int(result['processed_value']),
                        "name": result['processed_key'],
                        "x": calendar.timegm(day.timetuple()) * 1000,
                        # Multiply by 1000 to return correct GMT+05:30 timestamp
                    })
                    processed_keys.remove(result['processed_key'])

            # If no result is available for a processed_key put its value zero for (day.month, day.year)
            for key in processed_keys:
                processed_key_dict[key].append({
                    # "color": processed_key_color[key],
                    "color": '',
                    "y": 0,
                    "name": key,
                    "x": calendar.timegm(day.timetuple()) * 1000,
                    # Multiply by 1000 to return correct GMT+05:30 timestamp
                })

            day += relativedelta.relativedelta(months=1)

        area_chart_series = []
        for key, value in processed_key_dict.items():
            area_chart_series.append({
                'name': key,
                'data': value,
                # 'color': processed_key_color[key]
                'color': ''
            })

        # get the chart_data for the area chart.
        response = get_highchart_response(dictionary={'type': 'areaspline', 'chart_series': area_chart_series,
                                                      'title': 'MFR Processed', 'valuesuffix': 'seconds'})

        return HttpResponse(response)


# *********************** main dashboard sector capacity


class SectorCapacityMixin(object):
    '''
    Provide common method get for Sector Capacity Dashboard.

    To use this Mixin provide following attributes:

        - tech_name: name of the technology.
    '''

    def get(self, request):
        '''
        Handles the get request

        :param request:
        :retun dictionary containing data used for main dashboard charts.
        '''
        tech_name = self.tech_name
        organization = logged_in_user_organizations(self)
        technology = DeviceTechnology.objects.get(name=tech_name.lower()).id

        # Get Sector of User's Organizations. [and are Sub Station]
        # user_sector = organization_sectors(organization, technology=technology)
        # Get Device of User's Sector.
        # sector_devices_list = Device.objects.filter(id__in=user_sector.values_list('sector_configured_on', flat=True),
        #                                             is_added_to_nms=1)
        # Get Device name list of User's Sector.
        # sector_devices_list = sector_devices_list.values_list('device_name', flat=True)

        dashboard_name = '%s_sector_capacity' % (tech_name.lower())
        # Get the status of the dashboard.
        dashboard_status_dict, \
        processed_for_key = view_severity_status(dashboard_name, organization)
        chart_series = []
        color = []
        if len(dashboard_status_dict):
            for key, value in dashboard_status_dict.items():
                # create a list of "Key: value".
                chart_series.append(['%s: %s' % (key.replace('_', ' '), value), dashboard_status_dict[key]])

            color.append('rgb(255, 153, 0)')
            color.append('rgb(255, 0, 0)')
            color.append('rgb(0, 255, 0)')
            color.append('#d3d3d3')
        # get the chart_data for the pie chart.
        response = get_highchart_response(dictionary={'type': 'pie', 'chart_series': chart_series,
                                                      'title': '%s Sector Capacity' % tech_name.upper(), 'name': '',
                                                      'colors': color, 'processed_for_key': processed_for_key})

        return HttpResponse(response)


class PMPSectorCapacity(SectorCapacityMixin, View):
    """
    Class Based View for the PMP Sector Capacity Dashboard.
    """
    tech_name = 'PMP'


class WiMAXSectorCapacity(SectorCapacityMixin, View):
    """
    Class Based View for the WiMAX Sector Capacity Dashboard.
    """
    tech_name = 'WiMAX'


# *********************** main dashboard Backhaul Capacity


class BackhaulCapacityMixin(object):
    '''
    Provide common method (Mixin) get for Backhaul Capacity Dashboard.

    To use this Mixin provide following attributes:

        - tech_name: name of the technology.
    '''

    def get(self, request):
        '''
        Handles the get request

        :param request:
        :retun dictionary containing data used for main dashboard charts.
        '''
        tech_name = self.tech_name
        organization = logged_in_user_organizations(self)
        # Getting Technology ID
        try:
            technology = DeviceTechnology.objects.get(name=tech_name.lower()).id
        except Exception, e:
            technology = ""

        response = json.dumps({
            "success": 0,
            "message": "Technology doesn't exists",
            "data": []
        })

        if technology:
            # Get Backhauls Devices of User's Organizations.
            # user_backhaul = organization_backhaul_devices(organization, technology=technology)
            # Get Device name list of User's Backhaul.
            # backhaul_devices_list = user_backhaul.values_list('device_name', flat=True)
            # Creating Dashboard Name
            dashboard_name = '%s_backhaul_capacity' % (tech_name.lower())
            # Get the status of the dashboard.
            dashboard_status_dict, processed_for_key = view_severity_status(dashboard_name,
                                                                            organizations=organization
            )
            color = []
            chart_series = []
            if len(dashboard_status_dict):
                for key, value in dashboard_status_dict.items():
                    # create a list of "Key: value".
                    chart_series.append(['%s: %s' % (key.replace('_', ' '), value), dashboard_status_dict[key]])
                    
                color.append('rgb(255, 153, 0)')
                color.append('rgb(255, 0, 0)')
                color.append('rgb(0, 255, 0)')
                color.append('#d3d3d3')
            # get the chart_data for the pie chart.
            response = get_highchart_response(dictionary={'type': 'pie', 'chart_series': chart_series,
                                                          'title': '%s Backhaul Capacity' % tech_name.upper(),
                                                          'name': '', 'colors': color,
                                                          'processed_for_key': processed_for_key})

        return HttpResponse(response)


class PMPBackhaulCapacity(BackhaulCapacityMixin, View):
    """
    Class Based View for the PMP Backhaul Capacity
    """
    tech_name = 'PMP'


class WiMAXBackhaulCapacity(BackhaulCapacityMixin, View):
    """
    Class Based View for the WiMAX Backhaul Capacity
    """
    tech_name = 'WiMAX'


class TCLPOPBackhaulCapacity(BackhaulCapacityMixin, View):
    """
    Class Based View for the WiMAX Backhaul Capacity
    """
    tech_name = 'TCLPOP'


# ************************* main dashboard Sales Opportunity


class SalesOpportunityMixin(object):
    """
    Provide common method get for Sales Opportunity Dashboard.

    To use this Mixin provide following attributes:

        - tech_name: name of the technology.
    """

    def get(self, request):
        '''
        Handles the get request

        :param request:
        :retun dictionary containing data used for main dashboard charts.
        '''
        is_bh = False
        tech_name = self.tech_name

        data_source_config = {
            'topology': {'service_name': 'topology', 'model': Topology},
        }

        data_source = data_source_config.keys()[0]
        # Get Service Name from queried data_source
        service_name = data_source_config[data_source]['service_name']
        # Get Model Name from queried data_source
        model = data_source_config[data_source]['model']

        organization = logged_in_user_organizations(self)
        technology = DeviceTechnology.objects.get(name=tech_name).id
        # convert the data source in format topology-pmp/topology-wimax
        data_source = '%s-%s' % (data_source_config.keys()[0], tech_name.lower())
        try:
            dashboard_setting = DashboardSetting.objects.get(technology=technology,
                                                             page_name='main_dashboard',
                                                             name=data_source,
                                                             is_bh=is_bh)
        except DashboardSetting.DoesNotExist as e:
            return HttpResponse(json.dumps({
                "message": "Corresponding dashboard setting is not available.",
                "success": 0
            }))

        # Get Sector of User's Organizations. [and are Sub Station]
        # user_sector = organization_sectors(organization, technology)
        # Get Device of User's Sector.
        # sector_devices_list = Device.objects.filter(id__in=user_sector.values_list('sector_configured_on', flat=True),
        #     is_added_to_nms = 1)
        # Get Device Name List of User's Sector.
        # sector_devices_list = sector_devices_list.values_list('device_name', flat=True)

        dashboard_name = '%s_sales_opportunity' % (tech_name.lower())
        # Get the status of the dashbaord.
        dashboard_status_dict, processed_for_key = view_range_status(dashboard_name, organization)

        chart_series = []
        colors = []
        if len(dashboard_status_dict):
            # Get the dictionay of chart data for the dashbaord.
            response_dict = get_pie_chart_json_response_dict(dashboard_setting, data_source, dashboard_status_dict)
            # Fetch the chart series and color from the response dictionary.
            chart_series = response_dict['data']['objects']['chart_data'][0]['data']
            colors = response_dict['data']['objects']['colors']

        # get the chart_data for the pie chart.
        response = get_highchart_response(dictionary={'type': 'pie', 'chart_series': chart_series,
                                                      'title': tech_name + ' Sales Oppurtunity', 'name': '',
                                                      'colors': colors, 'processed_for_key': processed_for_key})

        return HttpResponse(response)


class PMPSalesOpportunity(SalesOpportunityMixin, View):
    """
    Class Based View for the PMP Sales Opportunity Dashboard.
    """
    tech_name = 'PMP'


class WiMAXSalesOpportunity(SalesOpportunityMixin, View):
    """
    Class Based View for the WiMAX Sales Opportunity Dashboard.
    """
    tech_name = 'WiMAX'


# *************************** Dashboard Timely Data ***********************


def view_severity_status(dashboard_name, organizations):
    '''
    Method based view to get latest data from central database table.
    retun data for the severity based dashboard.

    dashboard_name: name of the dashboard.
    sector_devices_list: list of device.

    return: dictionary
    '''

    dashboard_status_dict = DashboardSeverityStatusTimely.objects.order_by('-processed_for').filter(
        dashboard_name=dashboard_name,
        organization__in=organizations
    )
    processed_for_key_localtime = ''
    if dashboard_status_dict.exists():
        processed_for_key_utc = dashboard_status_dict[0].processed_for
        processed_for_key_localtime = processed_for_key_utc  # convert_utc_to_local_timezone(processed_for_key_utc)
        # get the latest processed_for(datetime) from the database.
        processed_for = dashboard_status_dict[0].processed_for
        # get the dashboard data on the basis of the processed_for.
        dashboard_status_dict = dashboard_status_dict.filter(processed_for=processed_for).aggregate(
            Normal=Sum('ok'),
            Needs_Augmentation=Sum('warning'),
            Stop_Provisioning=Sum('critical'),
            Unknown=Sum('unknown')
        )

    return dashboard_status_dict, str(processed_for_key_localtime)


def view_range_status(dashboard_name, organizations):
    """

    :param dashboard_name:
    :param organizations:
    :return:
    """
    dashboard_status_dict = DashboardRangeStatusTimely.objects.order_by('-processed_for').filter(
        dashboard_name=dashboard_name,
        organization__in=organizations
    )
    processed_for_key_localtime = ''
    if dashboard_status_dict.exists():
        processed_for_key_utc = dashboard_status_dict[0].processed_for
        try:
            processed_for_key_localtime = processed_for_key_utc  # convert_utc_to_local_timezone(processed_for_key_utc)
        except:
            processed_for_key_localtime = processed_for_key_utc
        # get the latest processed_for(datetime) from the database.
        processed_for = dashboard_status_dict[0].processed_for
        # get the dashboard data on the basis of the processed_for.
        dashboard_status_dict = dashboard_status_dict.filter(
            processed_for=processed_for
        ).aggregate(
            range1=Sum('range1'),
            range2=Sum('range2'),
            range3=Sum('range3'),
            range4=Sum('range4'),
            range5=Sum('range5'),
            range6=Sum('range6'),
            range7=Sum('range7'),
            range8=Sum('range8'),
            range9=Sum('range9'),
            range10=Sum('range10'),
            unknown=Sum('unknown')
        )

    return dashboard_status_dict, str(processed_for_key_localtime)


def get_severity_status_dict(dashboard_name, devices_list):
    '''
    Method based view to get latest data from central database table.
    retun data for the severity based dashboard.

    dashboard_name: name of the dashboard.
    sector_devices_list: list of device.

    return: dictionary
    '''

    dashboard_status_dict = DashboardSeverityStatusTimely.objects.order_by('-processed_for').filter(
        dashboard_name=dashboard_name,
        device_name__in=devices_list
    )
    processed_for_key_localtime = ''
    if dashboard_status_dict.exists():
        processed_for_key_utc = dashboard_status_dict[0].processed_for
        processed_for_key_localtime = processed_for_key_utc  # convert_utc_to_local_timezone(processed_for_key_utc)
        # get the latest processed_for(datetime) from the database.
        processed_for = dashboard_status_dict[0].processed_for
        # get the dashboard data on the basis of the processed_for.
        dashboard_status_dict = dashboard_status_dict.filter(processed_for=processed_for).aggregate(
            Normal=Sum('ok'),
            Needs_Augmentation=Sum('warning'),
            Stop_Provisioning=Sum('critical'),
            Unknown=Sum('unknown')
        )

    return dashboard_status_dict, processed_for_key_localtime


def get_range_status_dict(dashboard_name, sector_devices_list):
    '''
    Method based view to get latest data from central database table.
    retun data for the range based dashboard.

    dashboard_name: name of the dashboard.
    sector_devices_list: list of device.

    return: dictionary
    '''
    dashboard_status_dict = DashboardRangeStatusTimely.objects.order_by('-processed_for').filter(
        dashboard_name=dashboard_name,
        device_name__in=sector_devices_list
    )
    processed_for_key_localtime = ''
    if dashboard_status_dict.exists():
        processed_for_key_utc = dashboard_status_dict[0].processed_for
        processed_for_key_localtime = processed_for_key_utc  # convert_utc_to_local_timezone(processed_for_key_utc)
        # get the latest processed_for(datetime) from the database.
        processed_for = dashboard_status_dict[0].processed_for
        # get the dashboard data on the basis of the processed_for.
        dashboard_status_dict = dashboard_status_dict.filter(processed_for=processed_for).aggregate(
            range1=Sum('range1'), range2=Sum('range2'), range3=Sum('range3'),
            range4=Sum('range4'), range5=Sum('range5'), range6=Sum('range6'),
            range7=Sum('range7'), range8=Sum('range8'), range9=Sum('range9'),
            range10=Sum('range10'), unknown=Sum('unknown')
        )

    return (dashboard_status_dict, processed_for_key_localtime)


# *************************** Dashboard Gauge Status


class DashboardDeviceStatus(View):
    '''
    Class Based View for the Guage Chart of main Dashboard.
    '''

    def get(self, request):
        """
        Handles the get request

        :param:
            - dashboard_name: name of the dashboard.

        :retun dictionary containing data used for main dashboard charts.
        """
        dashboard_name = self.request.GET['dashboard_name']
        # remove '#' from the dashboard_name.
        dashboard_name = dashboard_name.replace('#', '')

        count = 0
        count_range = ''
        count_color = '#CED5DB'  # For Unknown Range.

        technology = None
        if 'pmp' in dashboard_name:
            technology = PMP.ID
        elif 'wimax' in dashboard_name:
            technology = WiMAX.ID

        if '-all' in dashboard_name:
            # replace the '-all' with '-network'. (e.g: 'dash-all' => 'dash-network')
            dashboard_name = dashboard_name.replace('-all', '-network')

        dashboard_status_name = dashboard_name
        if 'temperature' in dashboard_name:
            dashboard_name = 'temperature'
            # replace the '-wimax' with ''. (e.g: 'dash-wimax' => 'dash')
            dashboard_status_name = dashboard_status_name.replace('-wimax', '')

        organizations = logged_in_user_organizations(self)

        # Get Device of User's Organizations. [and are Sub Station]
        # user_devices = organization_network_devices(organizations, technology)
        # sector_devices = user_devices.filter(sector_configured_on__isnull=False)
        # Get Device Name list.
        # sector_devices = sector_devices.values_list('device_name',flat=True)

        try:
            dashboard_setting = DashboardSetting.objects.get(technology=technology,
                                                             page_name='main_dashboard',
                                                             name=dashboard_name,
                                                             is_bh=False)
        except DashboardSetting.DoesNotExist as e:
            return HttpResponse(json.dumps({
                "message": "Corresponding dashboard setting is not available.",
                "success": 0
            }))

        # Get the dictionary of dashboard status.
        dashboard_status_dict, processed_for_key = view_range_status(dashboard_status_name, organizations)

        if len(dashboard_status_dict):
            # Sum all the values of the dashboard status dict.
            count = sum(dashboard_status_dict.values())

        # Get the range from the dashbaord setting in which the count falls.
        range_status_dct = get_range_status(dashboard_setting, {'current_value': count})
        # Get the name of the range.
        count_range = range_status_dct['range_count']

        # get color of range in which count exists.
        if count_range and count_range != 'unknown':
            count_color = getattr(dashboard_setting, '%s_color_hex_value' % count_range)

        # Get the maximun range value and the range from the dashboard_setting.
        max_range, chart_stops = get_guege_chart_max_n_stops(dashboard_setting)

        chart_data_dict = {'type': 'gauge', 'name': dashboard_name, 'color': count_color, 'count': count,
                           'max': max_range, 'stops': chart_stops, 'processed_for_key': processed_for_key}

        # get the chart_data for the gauge chart.
        response = get_highchart_response(chart_data_dict)

        return HttpResponse(response)


# *************************Dashboard Monthly Data


def view_severity_status_monthly(dashboard_name, organizations):
    """

    :param dashboard_name:
    :param organizations:
    :return:
    """
    month_before = datetime.date.today() - datetime.timedelta(days=30)

    chart_data = list()

    dashboard_status_dict = DashboardSeverityStatusDaily.objects.extra(
        select={'processed_month': "date(processed_for)"}
    ).values(
        'processed_month',
        'dashboard_name'
    ).filter(
        processed_for__gte=month_before,
        dashboard_name=dashboard_name,
        organization__in=organizations
    ).annotate(
        Normal=Sum('ok'),
        Needs_Augmentation=Sum('warning'),
        Stop_Provisioning=Sum('critical'),
        Unknown=Sum('unknown')
    ).order_by('processed_month')

    item_color = ['rgb(0, 255, 0)', 'rgb(255, 153, 0)', 'rgb(255, 0, 0)', '#d3d3d3']

    trend_items = [
        {
            "id": "Normal",
            "title": "Normal",
            "color": item_color[0]
        },
        {
            "id": "Needs_Augmentation",
            "title": "Needs Augmentation",
            "color": item_color[1]
        },
        {
            "id": "Stop_Provisioning",
            "title": "Stop Provisioning",
            "color": item_color[2]
        },
        {
            "id": "Unknown",
            "title": "Unknown",
            "color": item_color[3]
        }
    ]

    for item in trend_items:

        data_dict = {
            "type": "column",
            "valuesuffix": " ",
            "name": item['title'].title(),
            "valuetext": " ",
            "color": item['color'],
            "data": list(),
        }

        for var in dashboard_status_dict:

            processed_date = var['processed_month']  # this is date object of date time
            js_time = float(format(datetime.datetime(processed_date.year,
                                                     processed_date.month,
                                                     processed_date.day,
                                                     0,
                                                     0), 'U'))
            # Preparation of final Dict for all days in One month
            data_dict['data'].append({
                "color": item['color'],
                "y": var[item['id']],
                "name": item['title'],
                "x": js_time * 1000,
                # Multiply by 1000 to return correct GMT+05:30 timestamp
            })
            # Increment Date by One
            # month_before += relativedelta.relativedelta(days=1)
        chart_data.append(data_dict)

    return chart_data


def get_severity_status_dict_monthly(dashboard_name, devices_list):
    '''
    '''
    # Start Calculations for Monthly Trend Sector
    has_data = False
    # Last 30 Days
    month_before = datetime.date.today() - datetime.timedelta(days=30)
    # Exceptional handling case
    final_dict = list()
    try:
        has_data = True
        # Query Set with filter, annotate(for summation of data),
        # extra parameter to make a new column of only date from datetime column for using group by of only date
        dashboard_status_dict = DashboardSeverityStatusDaily.objects.extra(
            select={'processed_month': "date(processed_for)"}).values('processed_month').filter(
            processed_for__gte=month_before,
            dashboard_name=dashboard_name,
            device_name__in=devices_list
        ).annotate(
            Normal=Sum('ok'),
            Needs_Augmentation=Sum('warning'),
            Stop_Provisioning=Sum('critical'),
            Unknown=Sum('unknown')
        ).order_by('processed_month')

        if has_data:
            # if 'sector' in dashboard_name:
            trends_items = [
                {
                    "id": "Normal",
                    "title": "Normal"
                },
                {
                    "id": "Needs_Augmentation",
                    "title": "Needs Augmentation"
                },
                {
                    "id": "Stop_Provisioning",
                    "title": "Stop Provisioning"
                },
                {
                    "id": "Unknown",
                    "title": "Unknown"
                }
            ]

            # Accessing all elements in sector trend items
            for i in range(len(trends_items)):
                item_color = ['rgb(0, 255, 0)', 'rgb(255, 153, 0)', 'rgb(255, 0, 0)', '#d3d3d3']

                data_dict = {
                    "type": "column",
                    "valuesuffix": " ",
                    "name": trends_items[i]['title'],
                    "valuetext": trends_items[i]['title'],
                    "color": item_color[i],
                    "data": list()
                }
                # Reseting month_before for every element of sector_trends_items
                month_before = datetime.date.today() - datetime.timedelta(days=30)
                # random color picker for sending different colors

                # Loop for sending complete 30 days Data
                # No need to put equality sign in loop because daily_main_dashboard cron runs only at midnight and also benefit of not getting redundant entry of today +1 day on chart.
                while month_before < datetime.date.today():
                    # Function for getting value for element of sector trend items on every date within month
                    data_val = getValueByTime(
                        dashboard_status_dict=dashboard_status_dict,
                        key=trends_items[i]['id'],
                        current_date=month_before,
                        date_column='processed_month'
                    )

                    # Preparation of final dict for sending to main function
                    data_dict['data'].append({
                        "color": item_color[i],
                        "y": data_val,
                        "name": trends_items[i]['title'],
                        "x": calendar.timegm(month_before.timetuple()) * 1000,
                        # Multiply by 1000 to return correct GMT+05:30 timestamp
                    })

                    # Increment of date by one
                    month_before += relativedelta.relativedelta(days=1)

                final_dict.append(data_dict)
    except Exception, e:
        has_data = False

    return final_dict


#  This function returns the given key value for given time stamp
def getValueByTime(dashboard_status_dict=[], key='', current_date='', date_column=''):
    val = 0
    # Accessing every element(dictionary) of list
    for dict_val in dashboard_status_dict:
        try:
            if ((date_column in dict_val) & (dict_val[date_column] == current_date)):
                val = dict_val[key]
        except Exception, e:
            # if condition is not matched then send value equal to zero
            val = 0

    return val


def get_range_status_dict_monthly(dashboard_name, sector_devices_list, dashboard_setting):
    '''
    '''
    # Start Calculations for Monthly Trend Sector
    has_data = False
    # Last 30 Days
    month_before = datetime.date.today() - datetime.timedelta(days=30)
    try:
        has_data = True
        # Query Set with filter, annotate(for summation of data), extra parameter to make a new column of only date from datetime column for using group by of only date
        dashboard_status_dict = DashboardRangeStatusDaily.objects.extra(
            select={'processed_month': "date(processed_for)"}).values('processed_month').filter(
            processed_for__gte=month_before,
            dashboard_name=dashboard_name,
            device_name__in=sector_devices_list
        ).annotate(
            range1=Sum('range1'), range2=Sum('range2'), range3=Sum('range3'),
            range4=Sum('range4'), range5=Sum('range5'), range6=Sum('range6'),
            range7=Sum('range7'), range8=Sum('range8'), range9=Sum('range9'),
            range10=Sum('range10'), unknown=Sum('unknown')
        ).order_by('processed_month')

    except Exception, e:
        has_data = False

    final_dict = []
    if has_data:
        trend_items = ['range1', 'range2', 'range3', 'range4', 'range5', 'range6', 'range7', 'range8', 'range9',
                       'range10', 'unknown']
        for i in range(len(trend_items)):
            if trend_items[i] != 'unknown':
                color_dict = getattr(dashboard_setting, 'range%d_color_hex_value' % (i + 1))
            else:
                color_dict = '#CED5DB'
            data_dict = {
                "type": "column",
                "valuesuffix": " ",
                "name": trend_items[i].title(),
                "valuetext": trend_items[i],
                "color": color_dict,
                "data": list()
            }
            month_before = datetime.date.today() - datetime.timedelta(days=30)
            chart_color = ''
            # Loop for sending complete 30 days Data
            # No need to put equality sign in loop because daily_main_dashboard cron runs only at midnight and also benefit of not getting redundant entry of today +1 day on chart.
            while month_before < datetime.date.today():
                # Loop for every element in list
                response_dict = {'chart_data': 0, 'color': '#000000'}
                for var in dashboard_status_dict:
                    if trend_items[i] != 'unknown':
                        # Condition for further processing
                        if var['processed_month'] == month_before:
                            response_dict = get_dashboardsettings_attributes(dashboard_setting, var, i)
                    else:
                        if var['processed_month'] == month_before:
                            response_dict = {'chart_data': var['unknown'], 'color': '#CED5DB'}
                data_dict['data'].append({
                    "color": response_dict['color'],
                    "y": response_dict['chart_data'],
                    "name": trend_items[i],
                    "x": calendar.timegm(month_before.timetuple()) * 1000,
                    # Multiply by 1000 to return correct GMT+05:30 timestamp
                })

                # Increment of date by one
                month_before += relativedelta.relativedelta(days=1)

            final_dict.append(data_dict)

    return final_dict


def get_dashboardsettings_attributes(dashboard_setting, range_counter, range_argument):
    chart_data = 0
    colors = '#000000'
    count = range_argument + 1
    # for count in range(1, 11):
    # Getting value of dashboard setting corresponding to count variable
    start_range = getattr(dashboard_setting, 'range%d_start' % count)
    end_range = getattr(dashboard_setting, 'range%d_end' % count)
    color = getattr(dashboard_setting, 'range%d_color_hex_value' % count)
    # if start_range or end_range:
    # if len(str(start_range).strip()) or len(str(end_range).strip()):
    # chart_data.append(['(%s, %s)' % (start_range, end_range), range_counter['range%d' %count]])
    chart_data = range_counter['range%d' % count]
    if color:
        colors = color
    else:
        colors = "#000000"
    # else:
    #     chart_data = 0
    #     colors = "#000000"
    # Preparation of Final List                    
    # chart_data.append(['Unknown', range_counter['unknown']])
    # colors.append("#d3d3d3")
    return {'chart_data': chart_data, 'color': colors}


def view_range_status_monthly(dashboard_name, organizations, dashboard_settings=None):
    """

    :param dashboard_name:
    :param organizations:
    :param dashboard_settings:
    :return:
    """
    month_before = datetime.date.today() - datetime.timedelta(days=30)
    dashboard_status_dict = DashboardRangeStatusDaily.objects.extra(
        select={'processed_month': "date(processed_for)"}
    ).values(
        'processed_month',
        'dashboard_name'
        # 'organization'
    ).filter(
        dashboard_name=dashboard_name,
        organization__in=organizations,
        processed_for__gte=month_before
    ).annotate(
        range1=Sum('range1'),
        range2=Sum('range2'),
        range3=Sum('range3'),
        range4=Sum('range4'),
        range5=Sum('range5'),
        range6=Sum('range6'),
        range7=Sum('range7'),
        range8=Sum('range8'),
        range9=Sum('range9'),
        range10=Sum('range10'),
        unknown=Sum('unknown')
    ).order_by('processed_month')

    chart_data = list()
    if dashboard_settings:
        trend_items = [
            {
                "id": "range1_start-range1_end",
                "title": "range1"
            },
            {
                "id": "range2_start-range2_end",
                "title": "range2"
            },
            {
                "id": "range3_start-range3_end",
                "title": "range3"
            },
            {
                "id": "range4_start-range4_end",
                "title": "range4"
            },
            {
                "id": "range5_start-range5_end",
                "title": "range5"
            },
            {
                "id": "range6_start-range6_end",
                "title": "range6"
            },
            {
                "id": "range7_start-range7_end",
                "title": "range7"
            },
            {
                "id": "range8_start-range8_end",
                "title": "range8"
            },
            {
                "id": "range9_start-range9_end",
                "title": "range9"
            },
            {
                "id": "range10_start-range10_end",
                "title": "range10"
            },
            {
                "id": "unknown",
                "title": "unknown"
            }
        ]
        # Accessing every element of trend items
        for item in trend_items:

            if item['title'] != 'unknown':
                count_color = getattr(dashboard_settings, '%s_color_hex_value' % item['title'])

            else:
                # Color for Unknown range
                count_color = '#CED5DB'

            data_dict = {
                "type": "column",
                "valuesuffix": " ",
                "name": item['title'].title(),
                "valuetext": " ",
                "color": count_color,
                "data": list(),
            }

            for var in dashboard_status_dict:

                processed_date = var['processed_month']  # this is date object of date time
                js_time = float(format(datetime.datetime(processed_date.year,
                                                         processed_date.month,
                                                         processed_date.day,
                                                         0,
                                                         0), 'U'))
                # Preparation of final Dict for all days in One month
                data_dict['data'].append({
                    "color": count_color,
                    "y": var[item['title']],
                    "name": item['title'],
                    "x": js_time * 1000,
                    # Multiply by 1000 to return correct GMT+05:30 timestamp
                })
                # Increment Date by One
                # month_before += relativedelta.relativedelta(days=1)

            chart_data.append(data_dict)
        return chart_data

    return dashboard_status_dict


def get_range_status_dict_monthly_devicestatus(dashboard_name, sector_devices_list):
    '''
    '''
    # Start Calculations for Monthly Trend Sector
    # Last 30 Days
    month_before = datetime.date.today() - datetime.timedelta(days=30)
    # Query Set with filter, annotate(for summation of data),
    # extra parameter to make a new column of only date from datetime column for using group by of only date
    dashboard_status_dict = DashboardRangeStatusDaily.objects.extra(
        select={'processed_month': "date(processed_for)"}).values('processed_month').filter(
        device_name__in=sector_devices_list,
        dashboard_name=dashboard_name,
        processed_for__gte=month_before
    ).annotate(
        range1=Sum('range1'), range2=Sum('range2'), range3=Sum('range3'),
        range4=Sum('range4'), range5=Sum('range5'), range6=Sum('range6'),
        range7=Sum('range7'), range8=Sum('range8'), range9=Sum('range9'),
        range10=Sum('range10'), unknown=Sum('unknown')
    ).order_by('processed_month')

    return dashboard_status_dict


#*************************** Monthly Trend Backhaul chart


class MonthlyTrendBackhaulMixin(object):
    '''
    '''

    def get(self, request):
        '''
        Handles the get request

        :param request:
        :retun dictionary containing data used for main dashboard Monthly charts.
        '''
        tech_name = self.tech_name
        organization = logged_in_user_organizations(self)
        # Getting Technology ID
        try:
            technology = DeviceTechnology.objects.get(name=tech_name.lower()).id
        except Exception, e:
            technology = ""

        response = json.dumps({
            "success": 0,
            "message": "Technology doesn't exists",
            "data": []
        })

        if technology:

            # Creating Dashboard Name
            dashboard_name = '%s_backhaul_capacity' % (tech_name.lower())
            # Get the status of the dashboard.
            dashboard_status_dict = view_severity_status_monthly(dashboard_name, organizations=organization)

            chart_series = dashboard_status_dict

            response = get_highchart_response(
                dictionary={'type': 'column',
                            'valuesuffix': '',
                            'chart_series': chart_series,
                            'name': '%s Backhaul Capacity' % tech_name.upper(),
                            'valuetext': ''})

        return HttpResponse(response)


class MonthlyTrendBackhaulPMP(MonthlyTrendBackhaulMixin, View):
    """
    """
    tech_name = 'PMP'


class MonthlyTrendBackhaulWiMAX(MonthlyTrendBackhaulMixin, View):
    """
    """
    tech_name = 'WiMAX'


class MonthlyTrendBackhaulTCLPOP(MonthlyTrendBackhaulMixin, View):
    """
    """
    tech_name = 'TCLPOP'


# ******************************* Monthly Trend Sector chart
# Mixin which can work for both Technologies
class MonthlyTrendSectorMixin(object):
    '''
    '''

    def get(self, request):
        tech_name = self.tech_name
        organization = logged_in_user_organizations(self)

        dashboard_name = '%s_sector_capacity' % (tech_name.lower())
        # Function call for calculating no. of hosts in different states on different days
        processed_key_dict = view_severity_status_monthly(dashboard_name=dashboard_name,
                                                          organizations=organization)

        chart_series = []
        chart_series = processed_key_dict

        response = get_highchart_response(dictionary={'type': 'column',
                                                      'valuesuffix': '',
                                                      'chart_series': chart_series,
                                                      'name': '%s Sector Capacity' % tech_name.upper(),
                                                      'valuetext': ''})

        return HttpResponse(response)


class MonthlyTrendSectorPMP(MonthlyTrendSectorMixin, View):
    """
    """
    tech_name = 'PMP'


class MonthlyTrendSectorWIMAX(MonthlyTrendSectorMixin, View):
    """
    """
    tech_name = 'WiMAX'


# ********************************* Monthly Trend Sales chart
# Sales MIXIN for both technologies
class MonthlyTrendSalesMixin(object):
    """
    """

    def get(self, request):
        '''
        '''
        is_bh = False
        tech_name = self.tech_name

        data_source_config = {
            'topology': {'service_name': 'topology', 'model': Topology},
        }

        data_source = data_source_config.keys()[0]

        # Get Service Name from queried data_source
        service_name = data_source_config[data_source]['service_name']
        model = data_source_config[data_source]['model']

        organization = logged_in_user_organizations(self)
        technology = DeviceTechnology.objects.get(name=tech_name).id
        # convert the data source in format topology_pmp/topology_wimax
        data_source = '%s-%s' % (data_source_config.keys()[0], tech_name.lower())
        # Getting Dashboard settings
        try:
            dashboard_setting = DashboardSetting.objects.get(technology=technology, page_name='main_dashboard',
                                                             name=data_source, is_bh=is_bh)
        except DashboardSetting.DoesNotExist as e:
            return HttpResponse(json.dumps({
                "message": "Corresponding dashboard setting is not available.",
                "success": 0
            }))

        # Get Sector of User's Organizations. [and are Sub Station]
        user_sector = organization_sectors(organization, technology)
        sector_devices_list = Device.objects.filter(id__in=user_sector.values_list('sector_configured_on', flat=True),
                                                    is_added_to_nms=1)
        sector_devices_list = sector_devices_list.values_list('device_name', flat=True)

        dashboard_name = '%s_sales_opportunity' % (tech_name.lower())
        dashboard_status_dict = view_range_status_monthly(dashboard_name=dashboard_name,
                                                          organizations=organization,
                                                          dashboard_settings=dashboard_setting)

        chart_series = dashboard_status_dict
        # Sending Final response
        response = get_highchart_response(dictionary={'type': 'column',
                                                      'valuesuffix': '',
                                                      'chart_series': chart_series,
                                                      'name': '%s Sales Opportunity' % tech_name.upper(),
                                                      'valuetext': ''})

        return HttpResponse(response)


class MonthlyTrendSalesPMP(MonthlyTrendSalesMixin, View):
    """
    """
    tech_name = 'PMP'


class MonthlyTrendSalesWIMAX(MonthlyTrendSalesMixin, View):
    """
    """
    tech_name = 'WIMAX'


# *********************************** Dashboard Device Status Monthly Trend


class MonthlyTrendDashboardDeviceStatus(View):
    '''
    Class Based View for the Monthly Trend of device status on Main Dashbaord.
    '''

    def get(self, request):
        """
        Handles the get request

        :param:
            - dashboard_name: name of the dashboard.

        :retun dictionary containing data used for main dashboard charts.
        """
        # Get Request for getting url name passed in URL
        dashboard_name = self.request.GET['dashboard_name']
        # remove '#' from the dashboard_name.
        if "#" in dashboard_name:
            dashboard_name = dashboard_name.replace('#', '')

        technology = None
        # Finding technology ID
        if 'wimax' in dashboard_name:
            technology = WiMAX.ID

        if '-all' in dashboard_name:
            # replace the '-all' with '-network'. (e.g: 'dash-all' => 'dash-network')
            dashboard_name = dashboard_name.replace('-all', '-network')

        dashboard_status_name = dashboard_name
        if 'temperature' in dashboard_name:
            dashboard_name = 'temperature'
            # replace the '-wimax' with ''. (e.g: 'dash-wimax' => 'dash')
            dashboard_status_name = dashboard_status_name.replace('-wimax', '')
        # Finding Organization of user   
        organizations = logged_in_user_organizations(self)

        try:
            dashboard_setting = DashboardSetting.objects.get(technology=technology,
                                                             page_name='main_dashboard',
                                                             name=dashboard_name, is_bh=False)
        except DashboardSetting.DoesNotExist as e:
            return HttpResponse(json.dumps({
                "message": "Corresponding dashboard setting is not available.",
                "success": 0
            }))


        # Get the dictionary of dashboard status.
        dashboard_status_dict = view_range_status_monthly(dashboard_name=dashboard_status_name,
                                                          organizations=organizations,
                                                          dashboard_settings=dashboard_setting)
        chart_series = dashboard_status_dict
        # Trend Items for matching range

        response = get_highchart_response(dictionary={'type': 'column', 'valuesuffix': '', 'chart_series': chart_series,
                                                      'name': dashboard_name, 'valuetext': ''})

        return HttpResponse(response)


class GetRfNetworkAvailData(View):
    """ 
    :This class calculate rf network availability data from RfNetworkAvailability model
    """

    def get(self, request):

        result = {
            "success": 0,
            "message": "No data",
            "data": {
                "objects": {
                    "chart_data": []
                }
            }
        }

        # Last 30th datetime object
        month_before = (datetime.date.today() - datetime.timedelta(days=30))
        epoch_month_before = int(month_before.strftime('%s'))

        rf_availability_data_dict = RfNetworkAvailability.objects.filter(
            sys_timestamp__gte=epoch_month_before
        ).order_by('sys_timestamp')

        # Chart data
        availability_chart_data = list()

        if rf_availability_data_dict and rf_availability_data_dict.count():
            # Get technologies list from fetched queryset
            existing_tech_list = set(rf_availability_data_dict.values_list('technology__name', flat=True))
            #  .distinct() : does not work with mysql

            # If any technology exists then proceed
            if len(existing_tech_list):

                tech_wise_dict = get_technology_wise_data_dict(rf_avail_queryset=rf_availability_data_dict)

                avail_chart_color = {
                    'PMP' : '#70AFC4',
                    'WiMAX' : '#A9FF96',
                    'PTP-BH' : '#95CEFF',
                    'P2P' : '#95CEFF'
                }

                unavail_chart_color = {
                    'PMP' : '#FF193B',
                    'WiMAX' : '#F7A35C',
                    'PTP-BH' : '#434348',
                    'P2P' : '#434348'
                }

                # Loop all technologies
                for tech in tech_wise_dict:
                    avail_chart_dict = {
                        "type": "column",
                        "valuesuffix": " ",
                        "stack": tech,
                        "name": "Availability(" + tech + ")",
                        "valuetext": "Availability (" + tech + ")",
                        "color": avail_chart_color[tech],
                        "data": list()
                    }

                    unavail_chart_dict = {
                        "type": "column",
                        "valuesuffix": " ",
                        "stack": tech,
                        "name": "Unavailability(" + tech + ")",
                        "valuetext": "Unavailability (" + tech + ")",
                        "color": unavail_chart_color[tech],
                        "data": list()
                    }

                    current_tech_data = tech_wise_dict[tech]

                    # Reseting month_before for every element of sector_trends_items
                    month_before = datetime.date.today() - datetime.timedelta(days=30)

                    # Loop for last 30 days
                    while month_before < datetime.date.today():

                        avail_day_data = {
                            "color": avail_chart_color[tech],
                            "y": 0,
                            "name": "Availability(" + tech + ")",
                            "x": calendar.timegm(month_before.timetuple()) * 1000,
                            # Multiply by 1000 to return correct GMT+05:30 timestamp
                        }

                        unavail_day_data = {
                            "color": unavail_chart_color[tech],
                            "y": 0,
                            "name": "Unavailability(" + tech + ")",
                            "x": calendar.timegm(month_before.timetuple()) * 1000,
                            # Multiply by 1000 to return correct GMT+05:30 timestamp
                        }
                        str_month_string = str(month_before)
                        if str_month_string in current_tech_data:
                            avail_day_data['y'] = int(current_tech_data[str_month_string]['avail'])
                            unavail_day_data['y'] = int(current_tech_data[str_month_string]['unavail'])

                        unavail_chart_dict['data'].append(unavail_day_data)
                        avail_chart_dict['data'].append(avail_day_data)
                        # Increment of date by one
                        month_before += relativedelta.relativedelta(days=1)

                    availability_chart_data.append(unavail_chart_dict)
                    availability_chart_data.append(avail_chart_dict)

        result['success'] = 1
        result['message'] = "RF Network Availability Data Fetched Successfully."
        result["data"]['objects']['chart_data'] = availability_chart_data

        return HttpResponse(json.dumps(result))


def get_technology_wise_data_dict(rf_avail_queryset):
    """
    : This function return data dict per technology wise
    """

    updated_data_dict = {}

    for rows in rf_avail_queryset:
        current_row = rows
        if current_row:
            technology = current_row.technology.name
            if technology not in updated_data_dict:
                updated_data_dict[technology] = {}

            sys_timestamp = current_row.sys_timestamp
            avail = current_row.avail
            unavail = current_row.unavail
            date_str = time.strftime('%Y-%m-%d', time.localtime(sys_timestamp))

            if date_str not in updated_data_dict[technology]:
                updated_data_dict[technology][date_str] = {}

            row_data = {
                "sys_timestamp": current_row.sys_timestamp,
                "avail": current_row.avail,
                "unavail": current_row.unavail
            }
            updated_data_dict[technology][date_str] = row_data

    return updated_data_dict

