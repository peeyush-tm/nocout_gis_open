import json
import datetime
import calendar
from dateutil import relativedelta
import time
from django.http import Http404

from django.utils.dateformat import format
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q, Count, Sum, Avg
from django.db.models.query import ValuesQuerySet

from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_datatables_view.base_datatable_view import BaseDatatableView

# nocout project settings # TODO: Remove the HARDCODED technology IDs
from nocout.settings import PMP, WiMAX, TCLPOP, DEBUG, PERIODIC_POLL_PROCESS_COUNT, REPORT_RELATIVE_PATH
# Import 404 page function from nocout views
from nocout.views import handler404

from inventory.models import Sector
from device.models import DeviceTechnology, Device
from performance.models import ServiceStatus, NetworkAvailabilityDaily, UtilizationStatus, \
    Topology, NetworkStatus, RfNetworkAvailability

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
# Import Dashboard Models
from dashboard.models import DashboardSetting, MFRDFRReports, DFRProcessed, \
    MFRProcessed, MFRCauseCode, DashboardRangeStatusTimely, DashboardSeverityStatusTimely, \
    DashboardSeverityStatusDaily, DashboardRangeStatusDaily, RFOAnalysis, CustomerFaultAnalysis

from dashboard.forms import DashboardSettingForm, MFRDFRReportsForm
from dashboard.utils import get_service_status_results, get_dashboard_status_range_counter, \
    get_pie_chart_json_response_dict, get_highchart_response, \
    get_unused_dashboards, get_range_status, get_guege_chart_max_n_stops

from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.permissions import SuperUserRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin, ValuesQuerySetMixin, AdvanceFilteringMixin

# BEGIN: logging module
import logging
logger = logging.getLogger(__name__)
# END: logging module

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


class DashbaordSettingsListView(TemplateView):
    """
    Class Based View for the Dashboard data table rendering.
    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.

    :return:
        context : list of dictionaries in which datatable headers are present for passing them to template.
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


class DashbaordSettingsListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Class based View to render Dashboard Settings Data table.
    This view inherit many properties from DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView.
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

        :Args:
            qs : ValuesQuerySet object

        :return:
            json_data : list of dictionaries 

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
    UserLogDeleteMixin class used for saving the deleted object in model. 

    """
    model = DashboardSetting
    template_name = 'dashboard/dashboard_settings_delete.html'
    success_url = reverse_lazy('dashboard-settings')
    obj_alias = 'name'


# ****************************************** RF PERFORMANCE DASHBOARD ********************************************


class PerformanceDashboardMixin(object):
    """
    Provide common method for getting Performance Dashboard for diffrent technologies. 
    """

    def get(self, request):
        """
        Handles the get request

        :Args:
            request
        :return:
            Http response object:
        """
        # Getting parameters from child class
        data_source_config, tech_name, is_bh = self.get_init_data()
        template_dict = {
            'data_sources': json.dumps(data_source_config.keys()),
            'parallel_calling_count' : PERIODIC_POLL_PROCESS_COUNT
        }
        try:
            technology = DeviceTechnology.objects.get(name=tech_name.lower()).id
        except Exception, e:
            technology = ""

        data_source = request.GET.get('data_source')
        data_source=str(data_source)
        dashboard_name=data_source+'_'+tech_name
        if is_bh:
            dashboard_name=dashboard_name+'_bh'
        
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
        user_organizations = nocout_utils.logged_in_user_organizations(self)
        dashboard_status_dict, processed_for_key = view_range_status(dashboard_name, user_organizations)
        chart_series = []
        colors = []
        response_dict ={
                "message": "Corresponding Dashboard data is not available.",
                "success": 0
            }
        if len(dashboard_status_dict):
            # Get the dictionay of chart data for the dashbaord.
            response_dict = get_pie_chart_json_response_dict(dashboard_setting, data_source, dashboard_status_dict)
            # Add timestamp with API response
            if 'timestamp' not in response_dict['data']['objects']:
                response_dict['data']['objects']['timestamp'] = ''

            response_dict['data']['objects']['timestamp'] = processed_for_key

        return HttpResponse(json.dumps(response_dict))


class WiMAX_Performance_Dashboard(PerformanceDashboardMixin, View):
    """
    The Class based View to get performance dashboard page requested.
    """

    template_name = 'rf_performance/wimax.html'
    def get_init_data(self):
        """
        The Class based View to get performance dashboard page requested.
        """
        data_source_config = {
            'ul_rssi': {'service_name': 'wimax_ul_rssi', 'model': ServiceStatus},
            'dl_rssi': {'service_name': 'wimax_dl_rssi', 'model': ServiceStatus},
            'ul_cinr': {'service_name': 'wimax_ul_cinr', 'model': ServiceStatus},
            'dl_cinr': {'service_name': 'wimax_dl_cinr', 'model': ServiceStatus},
            'modulation_ul_fec': {'service_name': 'wimax_modulation_ul_fec', 'model': ServiceStatus},
            'modulation_dl_fec': {'service_name': 'wimax_modulation_dl_fec', 'model': ServiceStatus},
        }
        tech_name = 'WiMAX'
        is_bh = False        
        return data_source_config, tech_name, is_bh


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
        tech_name = 'PMP'
        is_bh = False

        return data_source_config, tech_name, is_bh


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
        tech_name = 'P2P'
        is_bh = False

        return data_source_config, tech_name, is_bh


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
        tech_name = 'P2P'
        is_bh = True

        return data_source_config, tech_name, is_bh


# ####################################### MFR DFR Reports ########################################

class MFRDFRReportsListView(TemplateView):
    """
    Class Based View for the MFR report data table rendering.
    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.

    :return:
        context : list of dictionaries in which datatable headers are present for passing them to template.
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



class MFRDFRReportsListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Class based View to render MFR report Data table.
    This view inherit many properties from DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView.
    """
    model = MFRDFRReports
    columns = ['name', 'type', 'is_processed', 'process_for']
    search_columns = ['name', 'type', 'is_processed']
    order_columns = ['name', 'type', 'is_processed', 'process_for']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :Args:
            qs : ValuesQuerySet object

        :return:
            json_data : list of dictionaries 

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
    """
    Class based view to create new upload MFRDFR Report form.
    """
    model = MFRDFRReports
    form_class = MFRDFRReportsForm
    template_name = "mfrdfr/mfr_dfr_reports_upload.html"
    success_url = reverse_lazy('mfr-dfr-reports-list')

    def form_valid(self, form):
        """
        function for saing object if form is valid

        :Args:
            form : form object
        """
        response = super(MFRDFRReportsCreateView, self).form_valid(form)
        self.object.absolute_path = self.object.upload_to.path
        self.object.save()
        return response


class MFRDFRReportsDeleteView(UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the MFRDFR Report entry.

    """
    model = MFRDFRReports
    template_name = 'mfrdfr/mfr_dfr_reports_delete.html'
    success_url = reverse_lazy('mfr-dfr-reports-list')
    obj_alias = 'name'


class DFRProcessedListView(TemplateView):
    """
    Class Based View for the DFR report data table rendering.
    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.

    :return:
        context : list of dictionaries in which datatable headers are present for passing them to template.
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


class DFRProcessedListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Class based View to render MFR report Data table.
    This view inherit many properties from DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView.
    """
    model = DFRProcessed
    columns = ['processed_for__name', 'processed_for__process_for', 'processed_on', 'processed_key', 'processed_value']
    search_columns = ['processed_for__name', 'processed_key', 'processed_value']
    order_columns = ['processed_for__name', 'processed_for__process_for', 'processed_on', 'processed_key',
                     'processed_value']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :Args:
            qs : ValuesQuerySet object

        :return:
            json_data : list of dictionaries 

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for obj in json_data:
            processed_report_path = reverse('dfr-processed-reports-download', kwargs={'pk': obj.pop('id')})
            obj['processed_report_path'] = '<a href="' + processed_report_path + '" target="_blank">' + \
                                           '<img src="/static/img/ms-office-icons/excel_2013_green.png" ' + \
                                           'style="float:left; display:block; height:25px; width:25px;"></a>'
        return json_data


def dfr_processed_report_download(request, pk):
    """
    A function for downloading DFR processed report.

    :Args:
        pk : primary key of DFR report which user wants to download.

    :return:
        response : response pattern from which report is downloaded.
    """
    dfr_processed = DFRProcessed.objects.get(processed_for=pk)
    file_obj = None
    try:
        file_obj = file(dfr_processed.processed_report_path)
        file_path = dfr_processed.processed_report_path
        splitted_path = file_path.split("/")
        actual_filename = str(splitted_path[len(splitted_path)-1])
    except Exception as e:
        logger.exception(e)
        response = handler404(request)

    if file_obj:
        response = HttpResponse(file_obj.read(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="'+actual_filename+'"'

    return response

# ***************************************** DFR-REPORTS *******************************************************

class DFRReportsListingTableMain(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Class based View to render DFR report Data table on main dashboard Page.
    This view inherit many properties from DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView.
    """
    model = DFRProcessed
    columns = ['processed_for__name', 'processed_on', 'processed_report_path']
    order_columns = ['processed_for__name', 'processed_on']
    search_columns = ['processed_for__name']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :Args:
            qs : ValuesQuerySet object

        :return:
            json_data : list of dictionaries 

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for obj in json_data:
            fetched_path = obj['processed_report_path']
            download_path = ''
            if '/static/' in fetched_path:
                download_path = fetched_path.split("/static/")
                download_path = "/static/"+download_path[1]
            elif '/media/' in fetched_path:
                download_path = fetched_path.split("/media/")
                download_path = "/media/"+download_path[1]
            else:
                download_path = fetched_path

            download_action = '<a href="'+download_path+'" target="_blank"><i class=" fa fa-download"> </i></a>'
            if self.request.user.is_superuser:
                obj.update({'actions': download_action})
        return json_data


class DFRReportsListView(TemplateView):
    """
    Class Based View for the DFR report data table rendering.
    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.

    :return:
        context : list of dictionaries in which datatable headers are present for passing them to template.
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


class DFRReportsListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Class based View to render DFR report Data table on DFR page.
    This view inherit many properties from DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView.
    """
    model = MFRDFRReports
    columns = ['name', 'is_processed', 'process_for']
    search_columns = ['name', 'is_processed']
    order_columns = ['name', 'is_processed', 'process_for']

    def get_initial_queryset(self):
        """
        A function for overiding query set from BaseDatatableView.get_initial_queryset()

        :return:
            qs : Query set
        """
        qs = super(DFRReportsListingTable, self).get_initial_queryset()
        qs = qs.filter(type='DFR')
        return qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :Args:
            qs : ValuesQuerySet object

        :return:
            json_data : list of dictionaries 

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for obj in json_data:
            obj['is_processed'] = 'Yes' if obj['is_processed'] else 'No'
            obj_id = obj.pop('id')
            delete_url = reverse_lazy('dfr-reports-delete', kwargs={'pk': obj_id})
            delete_action = '<a href="%s"><i class="fa fa-trash-o text-danger"></i></a>' % delete_url
            download_action = ''
            if obj['is_processed'] == 'Yes':
                download_action = '<a href="javascript:;" dfr_id="%s" class="download_dfr_btn"><i class=" fa fa-download"> </i></a>&nbsp;&nbsp;&nbsp;' % obj_id
            
            obj.update({'actions': download_action+" "+delete_action})
        return json_data


class DFRReportsDeleteView(UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the DFR report. 

    """
    model = MFRDFRReports
    template_name = 'mfrdfr/mfr_dfr_reports_delete.html'
    success_url = reverse_lazy('dfr-reports-list')
    obj_alias = 'name'


# ********************************************** MFR-Reports ************************************************

class MFRReportsListView(TemplateView):
    """
    Class Based View for the MFR report data table rendering.
    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.

    :return:
        context : list of dictionaries in which datatable headers are present for passing them to template.
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


class MFRReportsListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Class based View to render MFR report Data table on MFR page.
    This view inherit many properties from DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView.
    """
    model = MFRDFRReports
    columns = ['name', 'is_processed', 'process_for']
    search_columns = ['name', 'is_processed']
    order_columns = ['name', 'is_processed', 'process_for']

    def get_initial_queryset(self):
        """
        A function for overiding query set from BaseDatatableView.get_initial_queryset()

        :return:
            qs : Query set
        """
        qs = super(MFRReportsListingTable, self).get_initial_queryset()
        qs = qs.filter(type='MFR')
        return qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :Args:
            qs : ValuesQuerySet object

        :return:
            json_data : list of dictionaries 

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
    Class based View to delete the MFR report

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

        :Args:
            request:

        :return:
            Http response object:
        """

        # City Charter tables Columns list

        city_charter_headers = [
            {'mData': 'city_name', 'sTitle': 'City', 'sWidth': 'auto'},
            {'mData': 'p2p_los', 'sTitle': 'LOS PTP', 'sWidth': 'auto'},
            {'mData': 'p2p_uas', 'sTitle': 'UAS', 'sWidth': 'auto'},
            {'mData': 'p2p_pd', 'sTitle': 'PD PTP', 'sWidth': 'auto'},
            {'mData': 'p2p_latancy', 'sTitle': 'Latency PTP', 'sWidth': 'auto'},
            {'mData': 'p2p_normal', 'sTitle': 'Normal PTP', 'sWidth': 'auto'},
            {'mData': 'p2p_ss_count', 'sTitle': 'Count PTP', 'sWidth': 'auto'},
            {'mData': 'p2p_ss_percentage', 'sTitle': '% PTP', 'sWidth': 'auto'},
            {'mData': 'pmp_los', 'sTitle': 'LOS PMP', 'sWidth': 'auto'},
            {'mData': 'pmp_jitter', 'sTitle': 'Jitter PMP', 'sWidth': 'auto'},
            {'mData': 'pmp_rereg', 'sTitle': 'ReReg PMP', 'sWidth': 'auto'},
            {'mData': 'pmp_ul', 'sTitle': 'UL PMP', 'sWidth': 'auto'},
            {'mData': 'pmp_pd', 'sTitle': 'PD PMP', 'sWidth': 'auto'},
            {'mData': 'pmp_latancy', 'sTitle': 'Latency PMP', 'sWidth': 'auto'},
            {'mData': 'pmp_normal', 'sTitle': 'Normal PMP', 'sWidth': 'auto'},
            {'mData': 'pmp_ss_count', 'sTitle': 'Count PMP', 'sWidth': 'auto'},
            {'mData': 'pmp_ss_percentage', 'sTitle': '% PMP', 'sWidth': 'auto'},
            {'mData': 'wimax_los', 'sTitle': 'LOS WiMAX', 'sWidth': 'auto'},
            {'mData': 'wimax_na', 'sTitle': 'NA WiMAX', 'sWidth': 'auto'},
            {'mData': 'wimax_rogue_ss', 'sTitle': 'Rogue SS WiMAX', 'sWidth': 'auto'},
            {'mData': 'wimax_ul', 'sTitle': 'UL WiMAX', 'sWidth': 'auto'},
            {'mData': 'wimax_pd', 'sTitle': 'PD WiMAX', 'sWidth': 'auto'},
            {'mData': 'wimax_latancy', 'sTitle': 'Latency WiMAX', 'sWidth': 'auto'},
            {'mData': 'wimax_normal', 'sTitle': 'Normal WiMAX', 'sWidth': 'auto'},
            {'mData': 'wimax_ss_count', 'sTitle': 'Count WiMAX', 'sWidth': 'auto'},
            {'mData': 'wimax_ss_percentage', 'sTitle': '% WiMAX', 'sWidth': 'auto'},
            {'mData': 'total_ss_count', 'sTitle': 'Total Count', 'sWidth': 'auto'},
            {'mData': 'total_ss_percentage', 'sTitle': 'Total %', 'sWidth': 'auto'}
        ]

        dfr_processed_header = [
            {'mData': 'processed_for__name', 'sTitle': 'Name', 'sWidth': 'auto'},
            {'mData': 'processed_on', 'sTitle': 'Processed On', 'sWidth': 'auto'}
        ]
        if self.request.user.is_superuser:
            dfr_processed_header.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context = {
            "isOther": 0,
            "page_title": "Main Dashboard",
            "debug" : 0,
            "city_charter_headers" : json.dumps(city_charter_headers),
            "dfr_processed_header" : json.dumps(dfr_processed_header),
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

        :Args:
            request

        :retun:
            HTTPresponse object : dictionary containing data used for main dashboard charts.
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
            response = get_highchart_response(
                dictionary={
                    'type': 'pie',
                    'chart_series': chart_series,
                    'title': 'MFR Cause Code',
                    'name': ''
                }
            )
            return HttpResponse(response)

        results = MFRCauseCode.objects.filter(processed_for=last_mfr_report).values('processed_key', 'processed_value')
        for result in results:
            try:
                processed_val = float(result['processed_value'].replace(',', ''))
            except Exception, e:
                logger.info(e)
                processed_val = result['processed_value']
            chart_series.append([
                "%s : %s" % (result['processed_key'], result['processed_value']),
                processed_val
            ])

        # get the chart_data for the pie chart.
        response = get_highchart_response(
            dictionary={
                'type': 'pie',
                'chart_series': chart_series,
                'title': 'MFR Cause Code',
                'name': ''
            }
        )

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

        :Args:
            request

        :retun:
            HTTPresponse object : dictionary containing data used for main dashboard charts.
        '''
        # Start Calculations for MFR Processed.
        # Last 12 Months
        year_before = datetime.date.today() - datetime.timedelta(days=365)
        year_before = datetime.date(year_before.year, year_before.month, 1)

        mfr_processed_results = MFRProcessed.objects.filter(
            processed_for__process_for__gte=year_before
        ).values(
            'processed_key',
            'processed_value',
            'processed_for__process_for'
        )

        day = year_before
        # area_chart_categories = []
        processed_key_dict = {result['processed_key']: [] for result in mfr_processed_results}
        
        while day <= datetime.date.today():
            #area_chart_categories.append(datetime.date.strftime(day, '%b %y'))

            processed_keys = processed_key_dict.keys()
            for result in mfr_processed_results:
                result_date = result['processed_for__process_for']
                if result_date.year == day.year and result_date.month == day.month:
                    try:
                        processed_val = float(result['processed_value'].replace(',', ''))
                    except Exception, e:
                        logger.info(e)
                        processed_val = result['processed_value']
                    processed_key_dict[result['processed_key']].append({
                        "color": '',
                        "y": processed_val,
                        "name": result['processed_key'],
                        "x": calendar.timegm(day.timetuple()) * 1000,  # Multiply by 1000 to return correct GMT+05:30 timestamp
                    })
                    processed_keys.remove(result['processed_key'])

            # If no result is available for a processed_key put its value zero for (day.month, day.year)
            for key in processed_keys:
                processed_key_dict[key].append({
                    "color": '',
                    "y": 0,
                    "name": key,
                    "x": calendar.timegm(day.timetuple()) * 1000  # Multiply by 1000 to return correct GMT+05:30 timestamp
                })

            day += relativedelta.relativedelta(months=1)

        area_chart_series = []
        for key, value in processed_key_dict.items():
            area_chart_series.append({
                'name': key,
                'data': value,
                'color': ''
            })

        # get the chart_data for the area chart.
        response = get_highchart_response(
            dictionary={
                'type': 'areaspline',
                'chart_series': area_chart_series,
                'title': 'MFR Processed',
                'valuesuffix': ' Minutes'
            }
        )

        return HttpResponse(response)


# *********************** main dashboard sector capacity

class SectorCapacityMixin(object):
    """
    Provide common method get for Sector Capacity Dashboard for both PMP/Wimax Technology.
    To use this Mixin provide following attributes:
    tech_name: name of the technology
    """

    def get(self, request):
        """
        Handles the get request

        :Args:
            request

        :retun:
            HTTPresponse object : dictionary containing data used for main dashboard charts.
        """
        tech_name = self.tech_name
        organization = nocout_utils.logged_in_user_organizations(self)
        technology = DeviceTechnology.objects.get(name=tech_name.lower()).id

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
        response = get_highchart_response(
            dictionary={
                'type': 'pie',
                'chart_series': chart_series,
                'title': '%s Sector Capacity' % tech_name.upper(), 'name': '',
                'colors': color,
                'processed_for_key': processed_for_key
            }
        )

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
    """
    Provide common method (Mixin) get for Backhaul Capacity Dashboard for technologies PMP/WiMAX/TCLPOP
    To use this Mixin provide following attributes:
    tech_name: name of the technology.
    """

    def get(self, request):
        """
        Handles the get request

        :Args:
            request

        :retun:
            HTTPresponse object : dictionary containing data used for main dashboard charts.
        """
        tech_name = self.tech_name
        organization = nocout_utils.logged_in_user_organizations(self)
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
            response = get_highchart_response(
                dictionary={
                    'type': 'pie',
                    'chart_series': chart_series,
                    'title': '%s Backhaul Capacity' % tech_name.upper(),
                    'name': '', 'colors': color,
                    'processed_for_key': processed_for_key
                }
            )

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
    Class Based View for the TCLPOP Backhaul Capacity
    """
    tech_name = 'TCLPOP'

# ************************* main dashboard Sales Opportunity

class SalesOpportunityMixin(object):
    """
    Provide common method get for Sales Opportunity Dashboard for both technology PMP/WiMAX.
    To use this Mixin provide following attributes:
    tech_name: name of the technology.
    """

    def get(self, request):
        """
        Handles the get request

        :Args:
            request

        :retun:
            HTTPresponse object : dictionary containing data used for main dashboard charts.
        """
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

        organization = nocout_utils.logged_in_user_organizations(self)
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
        response = get_highchart_response(
            dictionary={
                'type': 'pie',
                'chart_series': chart_series,
                'title': tech_name + ' Sales Oppurtunity', 'name': '',
                'colors': colors,
                'processed_for_key': processed_for_key
            }
        )

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
    """
    Method based view to get latest data from central database table.
    retun data for the severity based dashboard.

    :Args:
        dashboard_name: name of the dashboard.
        organizations: All organizations

    :return:
        dashboard_status_dict : list of dictionaries
        processed_for_key_localtime : time in format %d-%m-%Y %H:%M
    """

    dashboard_status_dict = DashboardSeverityStatusTimely.objects.order_by('-processed_for').filter(
        dashboard_name=dashboard_name,
        organization__in=organizations
    )
    processed_for_key_localtime = ''
    if dashboard_status_dict.exists():
        processed_for = dashboard_status_dict[0].processed_for

        if processed_for:
            processed_for_key_localtime = datetime.datetime.strftime(
                processed_for,"%d-%m-%Y %H:%M"
            )
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
    Method based view to get latest data from central database table.
    retun data for the range based dashboard.

    :Args:
        dashboard_name: name of the dashboard.
        organizations: All organizations

    :return:
        dashboard_status_dict : list of dictionaries
        processed_for_key_localtime : time in format %d-%m-%Y %H:%M
    """

    dashboard_status_dict = DashboardRangeStatusTimely.objects.order_by('-processed_for').filter(
        dashboard_name=dashboard_name,
        organization__in=organizations
    )
    processed_for_key_localtime = ''
    if dashboard_status_dict.exists():

        processed_for = dashboard_status_dict[0].processed_for
        if processed_for:
            processed_for_key_localtime = datetime.datetime.strftime(
                processed_for,"%d-%m-%Y %H:%M"
            )
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

# *************************** Dashboard Gauge Status

class DashboardDeviceStatus(View):
    '''
    Class Based View for the Guage Chart of main Dashboard.
    '''

    def get(self, request):
        """
        Handles the get request

        :Args:
            request

        :retun:
            HTTPresponse object : dictionary containing data used for main dashboard charts.
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

        organizations = nocout_utils.logged_in_user_organizations(self)

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

        chart_data_dict = {
            'type': 'gauge',
            'name': dashboard_name,
            'color': count_color,
            'count': count,
            'max': max_range,
            'stops': chart_stops,
            'processed_for_key': processed_for_key
        }

        # get the chart_data for the gauge chart.
        response = get_highchart_response(chart_data_dict)

        return HttpResponse(response)

# *************************Dashboard Monthly Data

def view_severity_status_monthly(dashboard_name, organizations):
    """
    Method based view to get latest data from central database table.
    retun data for the trends of severity based dashboard.

    :Args:
        dashboard_name: name of the dashboard.
        organizations: All organizations

    :return:
        dashboard_status_dict : list of dictionaries
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
            
        chart_data.append(data_dict)

    return chart_data

def view_range_status_dashboard_monthly(dashboard_name, organizations, dashboard_settings=None):
    """
    Method based view to get latest data from central database table.
    retun data for the trends of range based dashboard only Guage Chart dashboards.

    :Args:
        dashboard_name: name of the dashboard.
        organizations: All organizations
        dashboard_settings: None/object of settings of Dashboard

    :return:
        dashboard_status_dict : list of dictionaries
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
    count_color = '#7CB5EC'
    data_dict = {
                "type": "column",
                "valuesuffix": " ",
                "name": dashboard_name,
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
            "y": var['range1'],
            "name": dashboard_name,
            "x": js_time * 1000,
            # Multiply by 1000 to return correct GMT+05:30 timestamp
        })
        
    chart_data.append(data_dict)

    return chart_data

def view_range_status_monthly(dashboard_name, organizations, dashboard_settings=None):
    """
    Method based view to get latest data from central database table.
    retun data for the trends of range based dashboard (only sales opportunity)

    :Args:
        dashboard_name: name of the dashboard.
        organizations: All organizations

    :return:
        dashboard_status_dict : list of dictionaries
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
                start_range = getattr(dashboard_settings, '%s_start' % item['title'])
                end_range = getattr(dashboard_settings, '%s_end' % item['title'])
                if dashboard_settings.dashboard_type == 'INT' and start_range and end_range:              
                    range_param = '(%s,%s)' %(start_range, end_range)
                elif dashboard_settings.dashboard_type == 'STR' and start_range:
                    range_param = '%s' %start_range
                else:
                    continue    
            else:
                # Color for Unknown range
                count_color = '#CED5DB'
                range_param = ''

            final_param_name = '%s %s' %(item['title'].title(), range_param)
            data_dict = {
                "type": "column",
                "valuesuffix": " ",
                "name": final_param_name, 
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

            chart_data.append(data_dict)
        return chart_data

    return dashboard_status_dict

#*************************** Monthly Trend Backhaul chart

class MonthlyTrendBackhaulMixin(object):
    """
    Provide common method (Mixin) get for Trends of Backhaul Capacity Dashboard for technologies PMP/WiMAX/TCLPOP
    To use this Mixin provide following attributes:
    tech_name: name of the technology.
    """

    def get(self, request):
        """
        Handles the get request

        :Args:
            request

        :retun:
            HTTPresponse object : dictionary containing data used for main dashboard charts.
        """
        tech_name = self.tech_name
        y_axis_text = 'Number of Base Station'
        organization = nocout_utils.logged_in_user_organizations(self)
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
                dictionary={
                    'type': 'column',
                    'valuesuffix': '',
                    'chart_series': chart_series,
                    'name': '%s Backhaul Capacity' % tech_name.upper(),
                    'valuetext': y_axis_text
                }
            )

        return HttpResponse(response)


class MonthlyTrendBackhaulPMP(MonthlyTrendBackhaulMixin, View):
    """
    Class Based View for the PMP Backhaul Capacity
    """
    tech_name = 'PMP'


class MonthlyTrendBackhaulWiMAX(MonthlyTrendBackhaulMixin, View):
    """
    Class Based View for the WiMAX Backhaul Capacity
    """
    tech_name = 'WiMAX'


class MonthlyTrendBackhaulTCLPOP(MonthlyTrendBackhaulMixin, View):
    """
    Class Based View for the TCLPOP Backhaul Capacity
    """
    tech_name = 'TCLPOP'


# ******************************* Monthly Trend Sector chart
# Mixin which can work for both Technologies
class MonthlyTrendSectorMixin(object):
    """
    Provide common method get for Trends for Sector Capacity Dashboard for both PMP/Wimax Technology.
    To use this Mixin provide following attributes:
    tech_name: name of the technology
    """

    def get(self, request):
        """
        Handles the get request

        :Args:
            request

        :retun:
            HTTPresponse object : dictionary containing data used for main dashboard charts.
        """
        tech_name = self.tech_name
        y_axis_text = 'Number of Sectors'
        organization = nocout_utils.logged_in_user_organizations(self)

        dashboard_name = '%s_sector_capacity' % (tech_name.lower())
        # Function call for calculating no. of hosts in different states on different days
        processed_key_dict = view_severity_status_monthly(dashboard_name=dashboard_name,
                                                          organizations=organization)

        chart_series = []
        chart_series = processed_key_dict

        response = get_highchart_response(
            dictionary={
                'type': 'column',
                'valuesuffix': '',
                'chart_series': chart_series,
                'name': '%s Sector Capacity' % tech_name.upper(),
                'valuetext': y_axis_text
            }
        )

        return HttpResponse(response)


class MonthlyTrendSectorPMP(MonthlyTrendSectorMixin, View):
    """
    Class Based View for the PMP Sector Capacity Dashboard Trends.
    """
    tech_name = 'PMP'


class MonthlyTrendSectorWIMAX(MonthlyTrendSectorMixin, View):
    """
    Class Based View for the WiMAX Sector Capacity Dashboard Trends.
    """
    tech_name = 'WiMAX'


# ********************************* Monthly Trend Sales chart

class MonthlyTrendSalesMixin(object):
    """
    Provide common method get for Trend of Sales Opportunity Dashboard for both technology PMP/WiMAX.
    To use this Mixin provide following attributes:
    tech_name: name of the technology.
    """

    def get(self, request):
        """
        Handles the get request

        :Args:
            request

        :retun:
            HTTPresponse object : dictionary containing data used for main dashboard charts.
        """
        is_bh = False
        tech_name = self.tech_name
        y_axis_text = 'Number of Sectors'
        data_source_config = {
            'topology': {'service_name': 'topology', 'model': Topology},
        }

        data_source = data_source_config.keys()[0]

        # Get Service Name from queried data_source
        service_name = data_source_config[data_source]['service_name']
        model = data_source_config[data_source]['model']

        organization = nocout_utils.logged_in_user_organizations(self)
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

        dashboard_name = '%s_sales_opportunity' % (tech_name.lower())
        dashboard_status_dict = view_range_status_monthly(dashboard_name=dashboard_name, organizations=organization, dashboard_settings=dashboard_setting)

        chart_series = dashboard_status_dict
        # Sending Final response
        response = get_highchart_response(
            dictionary={
            'type': 'column',
            'valuesuffix': '',
            'chart_series': chart_series,
            'name': '%s Sales Opportunity' % tech_name.upper(),
            'valuetext': y_axis_text
        })

        return HttpResponse(response)


class MonthlyTrendSalesPMP(MonthlyTrendSalesMixin, View):
    """
    Class Based View for the PMP Sales Opportunity Dashboard Trends.
    """
    tech_name = 'PMP'


class MonthlyTrendSalesWIMAX(MonthlyTrendSalesMixin, View):
    """
    Class Based View for the WiMAX Sales Opportunity Dashboard Trends
    """
    tech_name = 'WIMAX'


#************************************ Monthly Trend RF Performance Dashboard

class GetMonthlyRFTrendData(View):
    '''
    Class Based View for the Monthly Trend of RF Performance Dashboard for all services.
    '''

    def get(self, request):
        """
        Handles the get request

        :Args:
            dashboard_name: name of the dashboard.

        :retun:
            dictionary containing data used for main dashboard charts.
        """
        # Get Request for getting url name passed in URL
        dashboard_name = self.request.GET.get('dashboard_name')
        is_bh = self.request.GET.get('is_bh',0)
        tech_name = self.request.GET.get('technology')
        dashboard_status_name=dashboard_name
        response=''
        technology = DeviceTechnology.objects.get(name=tech_name).id
        if "#" in dashboard_name:
            dashboard_name = dashboard_name.replace('#', '')

        dashboard_status_name=dashboard_name+'_'+tech_name
        if int(is_bh):
            dashboard_status_name=dashboard_status_name+'_bh'
        organization = nocout_utils.logged_in_user_organizations(self)
        try:
            dashboard_setting = DashboardSetting.objects.get(technology=technology,
                                                             page_name='rf_dashboard',
                                                             name=dashboard_name, is_bh=is_bh)
        except DashboardSetting.DoesNotExist as e:
            return HttpResponse(json.dumps({
                "message": "Corresponding dashboard setting is not available.",
                "success": 0
            }))

        dashboard_status_dict = view_range_status_monthly(dashboard_name=dashboard_status_name, organizations=organization, dashboard_settings=dashboard_setting)

        if dashboard_status_dict:
            chart_series = dashboard_status_dict
            dashboard_name=dashboard_name.replace('_', ' ')
            # Sending Final response
            response = get_highchart_response(
                dictionary={
                    'type': 'column',
                    'valuesuffix': '',
                    'chart_series': chart_series,
                    'name': '%s ' % dashboard_name.upper(),
                    'valuetext': ''
                }
            )

        return HttpResponse(response)
# *********************************** Dashboard Device Status Monthly Trend
class MonthlyTrendDashboardDeviceStatus(View):
    '''
    Class Based View for the Monthly Trend of device status on Main Dashbaord.
    '''

    def get(self, request):
        """
        Handles the get request

        :Args:
            dashboard_name: name of the dashboard.

        :retun:
            dictionary containing data used for main dashboard charts.
        """
        # Get Request for getting url name passed in URL
        dashboard_name = self.request.GET['dashboard_name']
        y_axis_text = 'Number of Network Devices (WiMAX+PMP)'
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
            y_axis_text = 'Number of IDU'
            # replace the '-wimax' with ''. (e.g: 'dash-wimax' => 'dash')
            dashboard_status_name = dashboard_status_name.replace('-wimax', '')
        # Finding Organization of user   
        organizations = nocout_utils.logged_in_user_organizations(self)

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
        dashboard_status_dict = view_range_status_dashboard_monthly(
            dashboard_name=dashboard_status_name,
            organizations=organizations,
            dashboard_settings=dashboard_setting
        )
        chart_series = dashboard_status_dict
        # Trend Items for matching range

        response = get_highchart_response(
            dictionary={
                'type': 'column',
                'valuesuffix': '',
                'chart_series': chart_series,
                'name': dashboard_name,
                'valuetext': y_axis_text
            }
        )

        return HttpResponse(response)
 
class GetRfNetworkAvailData(View):
    """ 
    This class calculate rf network availability data from RfNetworkAvailability model
    """

    def get(self, request):
        """
        Handles the get request

        :Args:
            request

        :retun:
            HTTPresponse object : dictionary containing data used for main dashboard charts.
        """
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
    This function return data dict per technology wise
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

def get_rfo_analysis_context():
    """
    This function returns context data required for RFO dashboards
    """

    # Fetch states from RFOAnalysis model
    states_data = list(RFOAnalysis.objects.extra({
        'id': 'REPLACE(state, " ", "_")',
        'value': 'state'
    }).filter(
        state__isnull=False
    ).values('value', 'id').distinct().order_by('value'))

    # Fetch cities from RFOAnalysis model
    city_data = list(RFOAnalysis.objects.extra({
        'id': 'REPLACE(city, " ", "_")',
        'value': 'city',
        'state_id': 'REPLACE(state, " ", "_")',
    }).filter(
        city__isnull=False,
        state__isnull=False
    ).values('value', 'id', 'state_id').distinct().order_by('value'))

    # Fetch month data from RFOAnalysis model
    months_data = list(RFOAnalysis.objects.extra({
        'id': 'CAST(unix_timestamp(timestamp) * 1000 AS CHAR)'
    }).values('id').distinct().order_by('id'))

    context = {
        'states_data': json.dumps(states_data),
        'city_data': json.dumps(city_data),
        'months_data': json.dumps(months_data)
    }

    return context


class RFOAnalysisView(View):
    """
    This class populates PB TT RFO Analysis dashboard template
    """
    def get(self, request, *args, **kwargs):

        template_name = 'rfo_dashboard/rfo_analysis.html'

        context = get_rfo_analysis_context()

        summation_headers = [
            {'mData': 'master_causecode', 'sTitle': 'Master Cause Code'},
            {'mData': 'outage_in_minutes', 'sTitle': 'Total Minutes'}
        ]

        all_data_headers = [
            {'mData': 'master_causecode', 'sTitle': 'Master Cause Code'},
            {'mData': 'sub_causecode', 'sTitle': 'Sub Cause Code'},
            {'mData': 'outage_in_minutes', 'sTitle': 'Total Minutes'}
        ]

        context['summation_headers'] = json.dumps(summation_headers)
        context['all_data_headers'] = json.dumps(all_data_headers)

        return render(self.request, template_name, context)


outage_minutes_casting = 'CAST(outage_in_minutes AS DECIMAL(15,2))'

class RFOAnalysisList(BaseDatatableView):
    """
    This class defines BaseDatatableView for RFO Analysis all data listing
    """
    model = RFOAnalysis
    columns = [
        'master_causecode',
        'sub_causecode',
        'outage_in_minutes',
        'state',
        'city'
    ]
    order_columns = [
        'master_causecode',
        'sub_causecode',
        'outage_in_minutes'
    ]

    def get_initial_queryset(self):

        month = self.request.GET.get('month')
        state_name = self.request.GET.get('state_name')
        city_name = self.request.GET.get('city_name')

        if state_name:
            state_name = state_name.replace('_', ' ')

        if city_name:
            city_name = city_name.replace('_', ' ')

        try:
            if state_name and city_name:
                qs = self.model.objects.extra({
                    'outage_in_minutes': outage_minutes_casting,
                    'master_causecode': 'IF(isnull(master_causecode) or master_causecode = "", "NA", master_causecode)',
                    'sub_causecode': 'IF(isnull(sub_causecode) or sub_causecode = "", "NA", sub_causecode)'
                }).exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    state__exact=state_name,
                    city__exact=city_name,
                    master_causecode__isnull=False,
                    sub_causecode__isnull=False,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values(*self.columns)

            elif state_name and not city_name:
                qs = self.model.objects.extra({
                    'outage_in_minutes': outage_minutes_casting,
                    'master_causecode': 'IF(isnull(master_causecode) or master_causecode = "", "NA", master_causecode)',
                    'sub_causecode': 'IF(isnull(sub_causecode) or sub_causecode = "", "NA", sub_causecode)'
                }).exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    state__exact=state_name,
                    master_causecode__isnull=False,
                    sub_causecode__isnull=False,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values(*self.columns)
            elif not state_name and city_name:
                qs = self.model.objects.extra({
                    'outage_in_minutes': outage_minutes_casting,
                    'master_causecode': 'IF(isnull(master_causecode) or master_causecode = "", "NA", master_causecode)',
                    'sub_causecode': 'IF(isnull(sub_causecode) or sub_causecode = "", "NA", sub_causecode)'
                }).exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    city__exact=city_name,
                    master_causecode__isnull=False,
                    sub_causecode__isnull=False,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values(*self.columns)

            else:
                qs = self.model.objects.extra({
                    'outage_in_minutes': outage_minutes_casting,
                    'master_causecode': 'IF(isnull(master_causecode) or master_causecode = "", "NA", master_causecode)',
                    'sub_causecode': 'IF(isnull(sub_causecode) or sub_causecode = "", "NA", sub_causecode)'
                }).exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    master_causecode__isnull=False,
                    sub_causecode__isnull=False,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values(*self.columns)
        except Exception, e:
            qs = self.model.objects.filter(id=0).values(*self.columns)

        return qs

    def filter_queryset(self, qs):
        """ If search['value'] is provided then filter all searchable columns using istartswith
        """
        # get global search value
        sSearch = self.request.GET.get('search[value]', None)

        if sSearch:
            query = []
            exec_query = "qs = qs.filter("
            if not self.request.GET.get('request_for_chart'):
                for column in self.columns[:-1]:
                    # avoid search on 'added_on'
                    if column == 'added_on':
                        continue
                    query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            else:
                # in case of chart data only filter with master cause code
                query = ['Q(master_causecode__iexact="%s")' % sSearch]
            
            exec_query += " | ".join(query)
            exec_query += ")"
            exec exec_query
        return qs

    def prepare_results(self, qs):

        json_data = [{
            key: round(val, 2) if key == 'outage_in_minutes' and val else val for key, val in dct.items()
        } for dct in qs]

        return json_data


    def get_context_data(self, *args, **kwargs):

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)

        if not self.request.GET.get('request_for_chart'):
            qs = self.paging(qs)

        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
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


class RFOAnalysisSummationList(BaseDatatableView):
    """
    This class defines BaseDatatableView for RFO Analysis all data listing
    """
    model = RFOAnalysis
    columns = [
        'master_causecode',
        'outage_in_minutes',
        'state',
        'city'
    ]
    order_columns = [
        'master_causecode',
        'outage_in_minutes'
    ]
    pre_camel_case_notation = False

    def get_initial_queryset(self):

        month = self.request.GET.get('month')
        state_name = self.request.GET.get('state_name')
        city_name = self.request.GET.get('city_name')

        if state_name:
            state_name = state_name.replace('_', ' ')

        if city_name:
            city_name = city_name.replace('_', ' ')

        try:
            if state_name and city_name:
                
                qs = self.model.objects.extra({
                    'outage_in_minutes': outage_minutes_casting,
                    'master_causecode': 'IF(isnull(master_causecode) or master_causecode = "", "NA", master_causecode)',
                    'sub_causecode': 'IF(isnull(sub_causecode) or sub_causecode = "", "NA", sub_causecode)'
                }).exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    state__iexact=state_name,
                    city__iexact=city_name,
                    master_causecode__isnull=False,
                    sub_causecode__isnull=False,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('master_causecode').annotate(outage_in_minutes=Sum('outage_in_minutes'))

            elif state_name and not city_name:

                qs = self.model.objects.extra({
                    'outage_in_minutes': outage_minutes_casting,
                    'master_causecode': 'IF(isnull(master_causecode) or master_causecode = "", "NA", master_causecode)',
                    'sub_causecode': 'IF(isnull(sub_causecode) or sub_causecode = "", "NA", sub_causecode)'
                }).exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    state__iexact=state_name,
                    master_causecode__isnull=False,
                    sub_causecode__isnull=False,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('master_causecode').annotate(outage_in_minutes=Sum('outage_in_minutes'))

            elif not state_name and city_name:

                qs = self.model.objects.extra({
                    'outage_in_minutes': outage_minutes_casting,
                    'master_causecode': 'IF(isnull(master_causecode) or master_causecode = "", "NA", master_causecode)',
                    'sub_causecode': 'IF(isnull(sub_causecode) or sub_causecode = "", "NA", sub_causecode)'
                }).exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    city__iexact=city_name,
                    master_causecode__isnull=False,
                    sub_causecode__isnull=False,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('master_causecode').annotate(outage_in_minutes=Sum('outage_in_minutes'))

            else:

                qs = self.model.objects.extra({
                    'outage_in_minutes': outage_minutes_casting,
                    'master_causecode': 'IF(isnull(master_causecode) or master_causecode = "", "NA", master_causecode)',
                    'sub_causecode': 'IF(isnull(sub_causecode) or sub_causecode = "", "NA", sub_causecode)'
                }).exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    master_causecode__isnull=False,
                    sub_causecode__isnull=False,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('master_causecode').annotate(outage_in_minutes=Sum('outage_in_minutes'))
                
        except Exception, e:
            qs = self.model.objects.filter(id=0).values(*self.columns)

        return qs

    def prepare_results(self, qs):

        json_data = [{
            key: round(val, 2) if key == 'outage_in_minutes' and val else val for key, val in dct.items()
        } for dct in qs]

        return json_data


    def get_context_data(self, *args, **kwargs):

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        
        if not self.request.GET.get('request_for_chart'):
            qs = self.paging(qs)

        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
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


class LoadMTTRSummaryTemplate(View):
    """
    This class loads MTTR dashboard template
    """

    def get(self, request, *args, **kwargs):

        template_name = 'rfo_dashboard/mttr_summary.html'
        context = get_rfo_analysis_context()
        return render(self.request, template_name, context)

class MTTRSummaryData(View):
    """
    This class generate percentage count for mttr data of PB TT RFO Analysis
    """
    def get(self, request, *args, **kwargs):
        result = {
            'success': 1,
            'message': 'MTTR data fetched successfully',
            'data': []
        }

        month = self.request.GET.get('month')
        state_name = self.request.GET.get('state_name')
        city_name = self.request.GET.get('city_name')
        mttr_dataset = []
        total_dataset = None

        if state_name:
            state_name = state_name.replace('_', ' ')

        if city_name:
            city_name = city_name.replace('_', ' ')

        try:
            if state_name and city_name:
                mttr_dataset = list(RFOAnalysis.objects.extra({
                    'name': 'mttr'
                }).exclude(
                    master_causecode__exact=''
                ).filter(
                    state__iexact=state_name,
                    city__iexact=city_name,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('name').annotate(total_count=Count('id')))

                total_dataset = RFOAnalysis.objects.filter(
                    state__iexact=state_name,
                    city__iexact=city_name,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).count()
            elif state_name and not city_name:
                mttr_dataset = list(RFOAnalysis.objects.extra({
                    'name': 'mttr'
                }).exclude(
                    master_causecode__exact=''
                ).filter(
                    state__iexact=state_name,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('name').annotate(total_count=Count('id')))

                total_dataset = RFOAnalysis.objects.filter(
                    state__iexact=state_name,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).count()
            elif not state_name and city_name:
                mttr_dataset = list(RFOAnalysis.objects.extra({
                    'name': 'mttr'
                }).exclude(
                    master_causecode__exact=''
                ).filter(
                    city__iexact=city_name,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('name').annotate(total_count=Count('id')))

                total_dataset = RFOAnalysis.objects.filter(
                    city__iexact=city_name,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).count()
            else:
                mttr_dataset = list(RFOAnalysis.objects.extra({
                    'name': 'mttr'
                }).exclude(
                    master_causecode__exact=''
                ).filter(
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('name').annotate(total_count=Count('id')))

                total_dataset = RFOAnalysis.objects.filter(
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).count()
                
        except Exception, e:
            pass

        if total_dataset and mttr_dataset:
            i = 0
            for data in mttr_dataset:
                i += 1
                if not data.get('name'):
                    data['name'] = 'NA'

                if 'less' in data.get('name').lower():
                    legend_index = 1
                elif 'between' in data.get('name').lower():
                    legend_index = 2
                elif 'more than' in data.get('name').lower():
                    legend_index = 3
                else:
                    legend_index = i

                data['legendIndex'] = legend_index

                try:
                    data['y'] = round(float(data.get('total_count', 0)) / float(total_dataset) * 100 , 2)
                except Exception, e:
                    pass

            result.update(
                success=1,
                message='MTTR data fetched successfully',
                data=mttr_dataset 
            )

        return HttpResponse(json.dumps(result))


class MTTRDetailData(View):
    """
    This class returns all data for specific MTTR value
    """
    def get(self, request, *args, **kwargs):
        result = {
            'success': 1,
            'message': 'MTTR detailed data fetched successfully',
            'data': []
        }

        month = self.request.GET.get('month')
        state_name = self.request.GET.get('state_name')
        city_name = self.request.GET.get('city_name')
        mttr_param = self.request.GET.get('mttr_param')
        mttr_dataset = []
        total_dataset = None

        if state_name:
            state_name = state_name.replace('_', ' ')

        if city_name:
            city_name = city_name.replace('_', ' ')
        try:
            if state_name and city_name:
                
                mttr_dataset = list(RFOAnalysis.objects.exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    state__iexact=state_name,
                    city__iexact=city_name,
                    master_causecode__isnull=False,
                    mttr__iexact=mttr_param,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('master_causecode').annotate(total_count=Count('id')))

                total_dataset = RFOAnalysis.objects.exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    state__iexact=state_name,
                    city__iexact=city_name,
                    master_causecode__isnull=False,
                    mttr__iexact=mttr_param,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).count()

            elif state_name and not city_name:

                mttr_dataset = list(RFOAnalysis.objects.exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    state__iexact=state_name,
                    master_causecode__isnull=False,
                    mttr__iexact=mttr_param,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('master_causecode').annotate(total_count=Count('id')))

                total_dataset = RFOAnalysis.objects.exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    state__iexact=state_name,
                    master_causecode__isnull=False,
                    mttr__iexact=mttr_param,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).count()

            elif not state_name and city_name:

                mttr_dataset = list(RFOAnalysis.objects.exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    city__iexact=city_name,
                    master_causecode__isnull=False,
                    mttr__iexact=mttr_param,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('master_causecode').annotate(total_count=Count('id')))

                total_dataset = RFOAnalysis.objects.exclude(
                    master_causecode__exact='',
                    sub_causecode__exact=''
                ).filter(
                    city__iexact=city_name,
                    master_causecode__isnull=False,
                    mttr__iexact=mttr_param,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).count()

            else:

                mttr_dataset = list(RFOAnalysis.objects.exclude(
                    master_causecode__exact=''
                ).filter(
                    master_causecode__isnull=False,
                    mttr__iexact=str(mttr_param).strip(),
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('master_causecode').annotate(total_count=Count('id')))

                total_dataset = RFOAnalysis.objects.exclude(
                    master_causecode__exact=''
                ).filter(
                    master_causecode__isnull=False,
                    mttr__iexact=mttr_param,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).count()
        except Exception, e:
            pass

        if mttr_dataset and total_dataset:
            for data in mttr_dataset:
                data['name'] = data['master_causecode']
                try:
                    data['y'] = round(float(data.get('total_count', 0)) / float(total_dataset) * 100 , 2)
                except Exception, e:
                    pass

            result.update(
                success=1,
                message='MTTR data fetched successfully',
                data=mttr_dataset 
            )

        return HttpResponse(json.dumps(result))


class INCTicketRateInit(View):
    """
    This class loads the INC ticket rate template
    """
    def get(self, request, *args, **kwargs):
        
        template_name = 'rfo_dashboard/inc_ticket_dashboard.html'
        # Fetch month data from RFOAnalysis model
        months_data = list(CustomerFaultAnalysis.objects.extra({
            'id': 'CAST(unix_timestamp(timestamp) * 1000 AS CHAR)'
        }).values('id').distinct().order_by('id'))

        severity_data = list(CustomerFaultAnalysis.objects.extra({
            'id': 'REPLACE(severity, " ", "_")',
            'value': 'severity'
        }).values('value', 'id').distinct().order_by('value'))

        inc_ticket_headers = [
            {'mData': 'month', 'sTitle': 'Month'},
            {'mData': 'tt_percent', 'sTitle': 'TT %'},
            {'mData': 'target_percent', 'sTitle': 'Target %'},
            {'mData': 'tt_count', 'sTitle': 'TT Count'}
        ]

        context = {
            'months_data': json.dumps(months_data),
            'severity_data': json.dumps(severity_data),
            'inc_ticket_headers': json.dumps(inc_ticket_headers)
        }

        return render(self.request, template_name, context)


class INCTicketRateListing(BaseDatatableView):
    """
    This class defines BaseDatatableView for RFO Analysis all data listing
    """
    model = CustomerFaultAnalysis
    columns = [
        'timestamp',
        'id',
        'severity',
        'city'
    ]
    order_columns = [
        'timestamp',
        'tt_count',
        'severity',
        'tt_count'
    ]

    def get_initial_queryset(self):

        month = self.request.GET.get('month')
        severity = self.request.GET.get('severity')
        target = 10
        try:
            # If month present in GET params then filter by it else return last 6 months data
            if month:
                qs = self.model.objects.extra({
                    'timestamp': 'unix_timestamp(timestamp)'
                }).filter(
                    severity__iexact=severity,
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values('severity', 'timestamp').annotate(tt_count=Count('id'))
            else:
                current_timestamp = datetime.datetime.now()
                qs = self.model.objects.extra({
                    'timestamp': 'unix_timestamp(timestamp)'
                }).filter(
                    severity__iexact=severity,
                    timestamp__gte=current_timestamp - datetime.timedelta(6 * 365/12),
                    timestamp__lte=current_timestamp
                ).values(
                    'severity',
                    'timestamp'
                ).annotate(tt_count=Count('id'))
            if self.request.GET.get('request_for_chart'):
                qs.order_by('tt_count')
        except Exception, e:
            qs = self.model.objects.filter(id=0)

        return qs

    def prepare_results(self, qs):

        json_data = [{
            key: val for key, val in dct.items()
        } for dct in qs]

        current_target = self.request.GET.get('current_target', 60)
        severity_wise_count = {}
        current_timestamp = datetime.datetime.now()

        for data in json_data:
            data['tt_percent'] = ''
            try:
                unique_id = '{0}_{1}'.format(
                    data['severity'].replace(' ', '_'),
                    str(data['timestamp'])
                ).lower()
                if unique_id not in severity_wise_count:
                    # Calculate the total count per severity
                    severity_wise_count[unique_id] = self.model.objects.filter(
                        timestamp=datetime.datetime.fromtimestamp(data['timestamp'])
                    ).count()

                total_count = severity_wise_count[unique_id]
                # Calculate % as per the total count & sererity wise total count
                data['tt_percent'] = round((float(data['tt_count'])/float(total_count)) * 100, 2)
            except Exception, e:
                pass

            # Format timestamp to 'Month'
            try:
                data['month'] = datetime.datetime.fromtimestamp(data['timestamp']).strftime('%B - %Y')
            except Exception, e:
                data['month'] = datetime.datetime.fromtimestamp(data['timestamp'])
            try:
                data['target_percent'] = round(float(current_target), 2)
            except Exception, e:
                data['target_percent'] = current_target

        print severity_wise_count

        return json_data


    def get_context_data(self, *args, **kwargs):

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        
        if not self.request.GET.get('request_for_chart'):
            qs = self.paging(qs)

        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
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


class ResolutionEfficiencyInit(View):
    """
    This class loads the INC ticket rate template
    """
    def get(self, request, *args, **kwargs):
        
        template_name = 'rfo_dashboard/resolution_efficiency.html'
        # Fetch month data from RFOAnalysis model
        months_data = list(CustomerFaultAnalysis.objects.extra({
            'id': 'CAST(unix_timestamp(timestamp) * 1000 AS CHAR)'
        }).values('id').distinct().order_by('id'))

        severity_data = list(CustomerFaultAnalysis.objects.extra({
            'id': 'REPLACE(severity, " ", "_")',
            'value': 'severity'
        }).values('value', 'id').distinct().order_by('value'))

        resolution_efficiency_headers = [
            {'mData': 'month', 'sTitle': 'Month'},
            {'mData': '2_hrs', 'sTitle': '2 Hours'},
            {'mData': '2_hrs_percent', 'sTitle': '2 Hours %'},
            {'mData': '4_hrs', 'sTitle': '4 Hours'},
            {'mData': '4_hrs_percent', 'sTitle': '4 Hours %'},
            {'mData': 'more_than_4_hrs', 'sTitle': 'More Than 4 Hours'},
            {'mData': 'more_than_4_hrs_percent', 'sTitle': 'More Than 4 Hours %'},
            {'mData': 'total_count', 'sTitle': 'Total TT'}
        ]

        context = {
            'months_data': json.dumps(months_data),
            'severity_data': json.dumps(severity_data),
            'resolution_efficiency_headers': json.dumps(resolution_efficiency_headers)
        }

        return render(self.request, template_name, context)


class ResolutionEfficiencyListing(BaseDatatableView):
    """
    This class defines BaseDatatableView for RFO Analysis all data listing
    """
    model = CustomerFaultAnalysis
    columns = [
        'timestamp',
        'id',
        'severity',
        'city'
    ]
    order_columns = [
        'timestamp',
        'tt_count',
        'tt_count',
        'tt_count',
        'tt_count',
        'tt_count',
        'tt_count',
        'tt_count'
    ]

    pre_camel_case_notation = False

    def get_initial_queryset(self):

        month = self.request.GET.get('month')
        try:
            # If month present in GET params then filter by it else return last 6 months data
            if month:
                qs = self.model.objects.extra({
                    'timestamp': 'unix_timestamp(timestamp)'
                }).filter(
                    timestamp=datetime.datetime.fromtimestamp(float(month))
                ).values(
                    'downtime_slab',
                    'timestamp'
                ).annotate(tt_count=Count('id'))
            else:
                current_timestamp = datetime.datetime.now()
                qs = self.model.objects.extra({
                    'timestamp': 'unix_timestamp(timestamp)'
                }).filter(
                    timestamp__gte=current_timestamp - datetime.timedelta(6 * 365/12),
                    timestamp__lte=current_timestamp
                ).values(
                    'downtime_slab',
                    'timestamp'
                ).annotate(tt_count=Count('id'))

            if self.request.GET.get('request_for_chart'):
                qs.order_by('tt_count')
        except Exception, e:
            qs = self.model.objects.filter(id=0)

        return qs

    def prepare_results(self, qs):

        json_data = [{
            key: val for key, val in dct.items()
        } for dct in qs]

        current_target = self.request.GET.get('current_target', 60)
        downtime_slab_wise_count = {}
        current_timestamp = datetime.datetime.now()
        temp_dict = {}
        for data in json_data:
            tt_count = data['tt_count']
            if data['timestamp'] not in temp_dict:
                temp_dict[data['timestamp']] = {
                    'timestamp': data['timestamp'],
                    'month': '',
                    '2_hrs': '',
                    '2_hrs_percent': '',
                    '4_hrs': '',
                    '4_hrs_percent': '',
                    'more_than_4_hrs': '',
                    'more_than_4_hrs_percent': '',
                    'total_count': ''
                }

            if not temp_dict[data['timestamp']]['month']:
                try:
                    formatted_month = datetime.datetime.fromtimestamp(data['timestamp']).strftime('%B - %Y')
                except Exception, e:
                    formatted_month = datetime.datetime.fromtimestamp(data['timestamp'])
                temp_dict[data['timestamp']]['month'] = formatted_month

            if not temp_dict[data['timestamp']]['total_count']:
                try:
                    temp_dict[data['timestamp']]['total_count'] = self.model.objects.extra({
                        'timestamp': 'unix_timestamp(timestamp)'
                    }).filter(
                        timestamp=datetime.datetime.fromtimestamp(float(data['timestamp']))
                    ).count()
                except Exception, e:
                    temp_dict[data['timestamp']]['total_count'] = self.model.objects.filter(id=0).count()

            total_count = temp_dict[data['timestamp']]['total_count']
                
            hrs_percent = round((float(tt_count) / float(total_count)) * 100, 2)

            if 'Hours' not in data['downtime_slab']:
                data['downtime_slab'] += ' Hours'

            if '2' in data['downtime_slab']:
                temp_dict[data['timestamp']]['2_hrs'] = tt_count
                temp_dict[data['timestamp']]['2_hrs_percent'] = hrs_percent
            elif '4' in data['downtime_slab'] and 'greater' not in data['downtime_slab']:
                temp_dict[data['timestamp']]['4_hrs'] = tt_count
                temp_dict[data['timestamp']]['4_hrs_percent'] = hrs_percent
            elif 'greater' in data['downtime_slab']:
                temp_dict[data['timestamp']]['more_than_4_hrs'] = tt_count
                temp_dict[data['timestamp']]['more_than_4_hrs_percent'] = hrs_percent

        return temp_dict.values()


    def get_context_data(self, *args, **kwargs):

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count() / len(set(qs.values_list('downtime_slab', flat=True)))

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count() / len(set(qs.values_list('downtime_slab', flat=True)))

        qs = self.ordering(qs)
        
        if not self.request.GET.get('request_for_chart'):
            qs = self.paging(qs)

        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
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

