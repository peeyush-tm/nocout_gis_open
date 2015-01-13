import json
import datetime
from dateutil import relativedelta

from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q, Count
from django.db.models.query import ValuesQuerySet
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_datatables_view.base_datatable_view import BaseDatatableView

from nocout.utils import logged_in_user_organizations
from inventory.models import Sector
from device.models import DeviceTechnology, Device
from performance.models import ServiceStatus, NetworkAvailabilityDaily, UtilizationStatus, Topology, NetworkStatus

#inventory utils
from inventory.utils.util import organization_customer_devices, organization_network_devices,\
    organization_sectors, prepare_machines
#inventory utils

from dashboard.models import DashboardSetting, MFRDFRReports, DFRProcessed, MFRProcessed, MFRCauseCode
from dashboard.forms import DashboardSettingForm, MFRDFRReportsForm
from dashboard.utils import get_service_status_results, get_dashboard_status_range_counter, get_pie_chart_json_response_dict,\
    get_dashboard_status_sector_range_counter, get_topology_status_results, get_highchart_response
from dashboard.config import dashboards
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
            {'mData': 'range1', 'sTitle': 'Range 1', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range2', 'sTitle': 'Range 2', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range3', 'sTitle': 'Range 3', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range4', 'sTitle': 'Range 4', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range5', 'sTitle': 'Range 5', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range6', 'sTitle': 'Range 6', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range7', 'sTitle': 'Range 7', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range8', 'sTitle': 'Range 8', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range9', 'sTitle': 'Range 9', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range10', 'sTitle': 'Range 10', 'sWidth': 'auto', 'bSortable': False },
        ]

        #if the user is superuser then the action column will appear on the datatable
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DashbaordSettingsListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    """
    Class based View to render Dashboard Settings Data table.
    """
    model = DashboardSetting
    columns = ['page_name', 'name', 'technology__name', 'range1', 'range2', 'range3', 'range4', 'range5', 'range6', 'range7', 'range8', 'range9', 'range10']
    keys = ['page_name', 'technology__name', 'name', 'range1_start', 'range2_start', 'range3_start', 'range4_start', 'range5_start', 'range6_start', 'range7_start', 'range8_start', 'range9_start', 'range10_start', 'range1_end', 'range2_end', 'range3_end', 'range4_end', 'range5_end', 'range6_end', 'range7_end', 'range8_end', 'range9_end', 'range10_end', 'range1_color_hex_value', 'range2_color_hex_value', 'range3_color_hex_value', 'range4_color_hex_value', 'range5_color_hex_value', 'range6_color_hex_value', 'range7_color_hex_value', 'range8_color_hex_value', 'range9_color_hex_value', 'range10_color_hex_value']
    order_columns = ['page_name', 'name', 'technology__name']
    columns = ['page_name', 'technology__name', 'name', 'range1_start', 'range2_start', 'range3_start', 'range4_start', 'range5_start', 'range6_start', 'range7_start', 'range8_start', 'range9_start', 'range10_start', 'range1_end', 'range2_end', 'range3_end', 'range4_end', 'range5_end', 'range6_end', 'range7_end', 'range8_end', 'range9_end', 'range10_end', 'range1_color_hex_value', 'range2_color_hex_value', 'range3_color_hex_value', 'range4_color_hex_value', 'range5_color_hex_value', 'range6_color_hex_value', 'range7_color_hex_value', 'range8_color_hex_value', 'range9_color_hex_value', 'range10_color_hex_value']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for obj in json_data:
            for i in range(1, 11):
                range_start = obj.pop('range%d_start' %i)
                range_end = obj.pop('range%d_end' %i)
                color_hex_value = obj.pop('range%d_color_hex_value' %i)
                range_color = "<div style='display:block; height:20px; width:20px;\
                        background:{0}'></div>".format(color_hex_value)
                if range_start:
                    obj.update({'range%d' %i : "(%s -<br>%s)<br>%s" % (range_start, range_end, range_color)})
                else:
                    obj.update({'range%d' %i : ""})

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
        context['dashboards'] = json.dumps(dashboards)
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
        context['dashboards'] = json.dumps(dashboards)
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

#****************************************** RF PERFORMANCE DASHBOARD ********************************************


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
        template_dict = {'data_sources': json.dumps(data_source_config.keys())}

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
            dashboard_setting = DashboardSetting.objects.get(technology=technology, page_name='rf_dashboard', name=data_source, is_bh=is_bh)
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
        devices_method_kwargs = dict(specify_ptp_type='ss')
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
        devices_method_kwargs = dict(specify_ptp_bh_type='ss')
        is_bh = True
        return data_source_config, technology, devices_method_to_call, devices_method_kwargs, is_bh


######################################## MFR DFR Reports ########################################

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

        #if the user is superuser then the action column will appear on the datatable
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False })

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
    order_columns = ['processed_for__name', 'processed_for__process_for', 'processed_on', 'processed_key', 'processed_value']

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
    response['Content-Disposition'] = 'attachment; filename="dfr_report_' + str(dfr_processed.processed_for.process_for) + '.xlsx"'
    return response

#***************************************** DFR-REPORTS *******************************************************

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
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False })

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


#********************************************** MFR-Reports ************************************************


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
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False })

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


#**************************************** Main Dashbaord ***************************************#


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

        return render(self.request, self.template_name, )

class MainDashboardMixin(object):
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
        technology = self.technology
        count = 0
        status_list = []
        device_list = []
        count_range = ''
        count_color = ''

        # Get User's organizations
        # (admin : organization + sub organization)
        # (operator + viewer : same organization)
        user_organizations = logged_in_user_organizations(self)

        # Get Devices of User's Organizations and/or Sub Organization.
        user_devices = organization_network_devices(user_organizations, technology)
        # Get Sectors of technology.Technology is PMP or WIMAX or None(For All: PMP+WIMAX )
        if technology:
            sector_list = Sector.objects.filter(bs_technology=technology, sector_configured_on__in=user_devices)
        else:
            sector_list = Sector.objects.filter(sector_configured_on__in=user_devices)
        # Get Devices of sector_list.
        for sector in sector_list:
            device_list.append(sector.sector_configured_on)

        # Make device_list distinct and remove duplicate devices from list.
        device_list = list(set(device_list))
        #Get dictionary of machine and device list.
        machine_dict = self.prepare_machines(device_list)

        if technology:
            technology_name = DeviceTechnology.objects.get(id=technology).name.lower()
        else:
            technology_name = 'network'

        if self.temperature:
            dashboard_name = 'temperature'
            if self.temperature == 'IDU':
                service_list = ['wimax_bs_temperature_acb', 'wimax_bs_temperature_fan']
                data_source_list = ['acb_temp', 'fan_temp']
                severity_list = ['warning', 'critical', 'ok', 'unknown']
            elif self.temperature == 'ACB':
                service_list = ['wimax_bs_temperature_acb']
                data_source_list = ['acb_temp']
                severity_list = ['warning', 'critical']
            elif self.temperature == 'FAN':
                service_list = ['wimax_bs_temperature_fan']
                data_source_list = ['fan_temp']
                severity_list = ['warning', 'critical']

            for machine_name, device_list in machine_dict.items():
                status_list += ServiceStatus.objects.filter(device_name__in=device_list,
                                            service_name__in=service_list,
                                            data_source__in=data_source_list,
                                            severity__in=severity_list).using(machine_name).annotate(Count('device_name'))
        elif self.packet_loss:
            dashboard_name = 'packetloss-%s'%technology_name
            for machine_name, device_list in machine_dict.items():
                status_list += NetworkStatus.objects.filter(device_name__in=device_list,
                                            service_name='ping',
                                            data_source='pl',
                                            severity__in=['warning', 'critical', 'down'],
                                            current_value__lt=100).using(machine_name).annotate(Count('device_name'))
        elif self.down:
            dashboard_name = 'down-%s'%technology_name
            for machine_name, device_list in machine_dict.items():
                status_list += NetworkStatus.objects.filter(device_name__in=device_list,
                                            service_name='ping',
                                            data_source='pl',
                                            severity__in=['down'],
                                            current_value__gte=100).using(machine_name).annotate(Count('device_name'))
        else:
            dashboard_name = 'latency-%s'%technology_name
            for machine_name, device_list in machine_dict.items():
                status_list += NetworkStatus.objects.filter(device_name__in=device_list,
                                            service_name='ping',
                                            data_source='rta',
                                            severity__in=['warning', 'critical', 'down']).using(machine_name).annotate(Count('device_name'))

        try:
            dashboard_setting = DashboardSetting.objects.get(technology=technology, page_name='main_dashboard', name=dashboard_name, is_bh=False)
        except DashboardSetting.DoesNotExist as e:
            return HttpResponse(json.dumps({
                "message": "Corresponding dashboard setting is not available.",
                "success":0
            }))
        count = len(status_list)

        for i in range(1, 11):
            start_range = getattr(dashboard_setting, 'range%d_start' %i)
            end_range = getattr(dashboard_setting, 'range%d_end' %i)

            # dashboard type is numeric and start_range and end_range exists to compare result.
            if start_range and end_range:
                if float(start_range) <= float(count) <= float(end_range):
                    count_range = 'range%d' %i

            #dashboard type is string and start_range exists to compare result.
            elif dashboard_setting.dashboard_type == 'STR' and start_range:
                if str(count).lower() in start_range.lower():
                    count_range = 'range%d' %i

        # get color of range in which count exists.
        if count_range:
            count_color = getattr(dashboard_setting, '%s_color_hex_value' %count_range)
        else:
            count_color = '#CED5DB' # For Unknown Range.

        dictionary = {'type': 'gauge', 'name': dashboard_name, 'color': count_color, 'count': count}
        response = get_highchart_response(dictionary)
        return HttpResponse(response)

    def prepare_machines(self, device_list_qs):
        """
        Return dict of machine name keys containing values of related devices list.

        :param device_list_qs:
        :return machine_dict:
        """
        unique_device_machine_list = {device.machine.name: True for device in device_list_qs}.keys()

        machine_dict = {}
        for machine in unique_device_machine_list:
            machine_dict[machine] = [device.device_name for device in device_list_qs if device.machine.name == machine]
        return machine_dict


class WiMAX_Latency(MainDashboardMixin, View):
    """
    The Class based View to get Latency of WIMAX.

    """
    packet_loss = False
    down = False
    temperature = ''
    technology = DeviceTechnology.objects.get(name__icontains='WIMAX').id


class PMP_Latency(MainDashboardMixin, View):
    """
    The Class based View to get Latency of PMP.

    """
    packet_loss = False
    down = False
    temperature = ''
    technology = DeviceTechnology.objects.get(name__icontains='PMP').id


class ALL_Latency(MainDashboardMixin, View):
    """
    The Class based View to get Latency of All(WIMAX and PMP).

    """
    packet_loss = False
    down = False
    temperature = ''
    technology = None


class WIMAX_Packet_Loss(MainDashboardMixin, View):
    """
    The Class based View to get Packet Loss of WIMAX.

    """
    packet_loss = True
    down = False
    temperature = ''
    technology = DeviceTechnology.objects.get(name__icontains='WIMAX').id


class PMP_Packet_Loss(MainDashboardMixin, View):
    """
    The Class based View to get Packet Loss of PMP.

    """
    packet_loss = True
    down = False
    temperature = ''
    technology = DeviceTechnology.objects.get(name__icontains='PMP').id


class ALL_Packet_Loss(MainDashboardMixin, View):
    """
    The Class based View to get Packet Loss of All(WIMAX and PMP).

    """
    packet_loss = True
    down = False
    temperature = ''
    technology = None


class WIMAX_Down(MainDashboardMixin, View):
    """
    The Class based View to get down of WIMAX.

    """
    packet_loss = False
    down = True
    temperature = ''
    technology = DeviceTechnology.objects.get(name__icontains='WIMAX').id


class PMP_Down(MainDashboardMixin, View):
    """
    The Class based View to get down of WIMAX.

    """
    packet_loss = False
    down = True
    temperature = ''
    technology = DeviceTechnology.objects.get(name__icontains='PMP').id


class ALL_Down(MainDashboardMixin, View):
    """
    The Class based View to get down of WIMAX.

    """
    packet_loss = False
    down = True
    temperature = ''
    technology = None


class WIMAX_Temperature_Idu(MainDashboardMixin, View):
    """
    The Class based View to get Temperature-IDU of WIMAX.

    """
    packet_loss = False
    down = False
    temperature = 'IDU'
    technology = DeviceTechnology.objects.get(name__icontains='WIMAX').id


class WIMAX_Temperature_Acb(MainDashboardMixin, View):
    """
    The Class based View to get Temperature-ACB of WIMAX.

    """
    packet_loss = False
    down = False
    temperature = 'ACB'
    technology = DeviceTechnology.objects.get(name__icontains='WIMAX').id


class WIMAX_Temperature_Fan(MainDashboardMixin, View):
    """
    The Class based View to get Temperature-FAN of WIMAX.

    """
    packet_loss = False
    down = False
    temperature = 'FAN'
    technology = DeviceTechnology.objects.get(name__icontains='WIMAX').id


class MFRCauseCodeView(View):
    """
    """

    def get(self, request):
        mfr_reports = MFRDFRReports.objects.order_by('-process_for').filter(is_processed=1)

        chart_series = []
        if mfr_reports.exists():
            last_mfr_report = mfr_reports[0]
        else:
            response = get_highchart_response(dictionary={'type': 'pie', 'chart_series': chart_series,
                'title': 'MFR Cause Code', 'name': ''})
            return HttpResponse(response)

        results = MFRCauseCode.objects.filter(processed_for=last_mfr_report).values('processed_key', 'processed_value')
        for result in results:
            chart_series.append([
                "%s : %s" % (result['processed_key'], result['processed_value']),
                int(result['processed_value'])
            ])

        response = get_highchart_response(dictionary={'type': 'pie', 'chart_series': chart_series,
            'title': 'MFR Cause Code', 'name': ''})

        return HttpResponse(response)


class MFRProcesedView(View):
    """
    """
    def get(self, request):
        # Start Calculations for MFR Processed.
        # Last 12 Months
        year_before = datetime.date.today() - datetime.timedelta(days=365)
        year_before = datetime.date(year_before.year, year_before.month, 1)

        mfr_processed_results = MFRProcessed.objects.filter(processed_for__process_for__gte=year_before).values(
                'processed_key', 'processed_value', 'processed_for__process_for')

        day = year_before
        area_chart_categories = []
        processed_key_dict = {result['processed_key']: [] for result in mfr_processed_results}

        while day <= datetime.date.today():
            area_chart_categories.append(datetime.date.strftime(day, '%b %y'))

            processed_keys = processed_key_dict.keys()
            for result in mfr_processed_results:
                result_date = result['processed_for__process_for']
                if result_date.year == day.year and result_date.month == day.month:
                    processed_key_dict[result['processed_key']].append(int(result['processed_value']))
                    processed_keys.remove(result['processed_key'])

            # If no result is available for a processed_key put its value zero for (day.month, day.year)
            for key in processed_keys:
                processed_key_dict[key].append(0)

            day += relativedelta.relativedelta(months=1)

        area_chart_series = []
        for key, value in processed_key_dict.items():
            area_chart_series.append({'name': key, 'data': value})

        return HttpResponse(json.dumps({
                            'categories': area_chart_categories,
                            'series': area_chart_series
                        }))

#********************************************** main dashboard sector capacity ************************************************

class PMPSectorCapacity(View):
    """
    """
    def get(self, sector_devices):
        pmp_data_source_config = {
            'cam_ul_util_kpi': {'service_name': 'cambium_ul_util_kpi', 'model': UtilizationStatus},
            'cam_dl_util_kpi': {'service_name': 'cambium_dl_util_kpi', 'model': UtilizationStatus},
        }

        organization = []
        technology = DeviceTechnology.objects.get(name='PMP').id
        sector_list = organization_sectors(organization, technology=technology)
        sector_devices = Device.objects.filter(id__in=sector_list.\
                            values_list('sector_configured_on', flat=True))

        data_source_list = pmp_data_source_config.keys()

        service_status_results = []
        for data_source in data_source_list:
            # Get Service Name from queried data_source
            service_name = pmp_data_source_config[data_source]['service_name']
            model = pmp_data_source_config[data_source]['model']

            service_status_results += get_service_status_results(
                sector_devices, model=model, service_name=service_name, data_source=data_source
            )

        range_counter = get_dashboard_status_sector_range_counter(service_status_results)

        chart_series = []
        for key,value in range_counter.items():
            chart_series.append(['%s: %s' % (key, value), range_counter[key]])

        response = get_highchart_response(dictionary={'type': 'pie', 'chart_series': chart_series,
            'title': 'PMP Sector Capacity', 'name': ''})

        return HttpResponse(response)


class WiMAXSectorCapacity(View):
    """
    """
    def get(self, request):
        wimax_data_source_config = {
            'pmp1_ul_util_kpi': {'service_name': 'wimax_pmp1_ul_util_kpi', 'model': UtilizationStatus},
            'pmp1_dl_util_kpi': {'service_name': 'wimax_pmp1_dl_util_kpi', 'model': UtilizationStatus},
            'pmp2_ul_util_kpi': {'service_name': 'wimax_pmp2_ul_util_kpi', 'model': UtilizationStatus},
            'pmp2_dl_util_kpi': {'service_name': 'wimax_pmp2_dl_util_kpi', 'model': UtilizationStatus},
        }

        organization = []
        technology = DeviceTechnology.objects.get(name='WiMAX').id
        sector_list = organization_sectors(organization, technology=technology)

        port_dict = {
            'pmp1': ['pmp1_ul_util_kpi', 'pmp1_dl_util_kpi'],
            'pmp2': ['pmp2_ul_util_kpi', 'pmp2_dl_util_kpi'],
        }

        service_status_results = []
        for port in port_dict.keys():

            data_source_list = port_dict[port]
            user_sector = sector_list.filter(sector_configured_on_port__name__icontains=port)

            for data_source in data_source_list:
                # Get Service Name from queried data_source
                service_name = wimax_data_source_config[data_source]['service_name']
                model = wimax_data_source_config[data_source]['model']

                sector_devices = Device.objects.filter(id__in=user_sector.\
                                values_list('sector_configured_on', flat=True))

                service_status_results += get_service_status_results(
                    sector_devices, model=model, service_name=service_name, data_source=data_source
                )

        range_counter = get_dashboard_status_sector_range_counter(service_status_results)

        chart_series = []
        for key,value in range_counter.items():
            chart_series.append(['%s: %s' % (key, value), range_counter[key]])

        response = get_highchart_response(dictionary={'type': 'pie', 'chart_series': chart_series,
            'title': 'WiMAX Sector Capacity', 'name': ''})

        return HttpResponse(response)


#********************************************** main dashboard sector capacity ************************************************

class SalesOpportunityMixin(object):
    """
    """
    def get(self, request):
        '''
        '''
        is_bh = False
        tech_name = self.get_technology()

        data_source_config = {
            'topology': {'service_name': 'topology', 'model': Topology},
        }

        data_source = data_source_config.keys()[0]
        # Get Service Name from queried data_source
        service_name = data_source_config[data_source]['service_name']
        model = data_source_config[data_source]['model']

        organization = []
        technology = DeviceTechnology.objects.get(name=tech_name).id
        # convert the data source in format topology_pmp/topology_wimax
        data_source = '%s-%s' % (data_source_config.keys()[0], tech_name.lower())
        try:
            dashboard_setting = DashboardSetting.objects.get(technology=technology, page_name='main_dashboard', name=data_source, is_bh=is_bh)
        except DashboardSetting.DoesNotExist as e:
            return HttpResponse(json.dumps({
                "message": "Corresponding dashboard setting is not available.",
                "success": 0
            }))

        # Get Sector of User's Organizations. [and are Sub Station]
        user_sector = organization_sectors(organization, technology)
        # Get device of User's Organizations. [and are Sub Station]
        sector_devices = Device.objects.filter(id__in=user_sector.\
                        values_list('sector_configured_on', flat=True))

        service_status_results = get_topology_status_results(
            sector_devices, model=model, service_name=service_name, data_source=data_source, user_sector=user_sector
        )

        range_counter = get_dashboard_status_range_counter(dashboard_setting, service_status_results)

        response_dict = get_pie_chart_json_response_dict(dashboard_setting, data_source, range_counter)
        chart_series = response_dict['data']['objects']['chart_data'][0]['data']

        response = get_highchart_response(dictionary={'type': 'pie', 'chart_series': chart_series,
            'title': tech_name + ' Sales Oppurtunity', 'name': ''})

        return HttpResponse(response)


class PMPSalesOpportunity(SalesOpportunityMixin, View):
    """
    """
    def get_technology(self):
        tech_name = 'PMP'

        return tech_name


class WiMAXSalesOpportunity(SalesOpportunityMixin, View):
    """
    """
    def get_technology(self):
        tech_name = 'WiMAX'

        return tech_name
