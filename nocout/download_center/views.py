import json
import ast
from device.models import DeviceTechnology
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, FormView, View
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic.edit import DeleteView
from download_center.forms import CityCharterSettingsForm
from models import ProcessedReportDetails, ReportSettings, CityCharterP2P, CityCharterPMP, CityCharterWiMAX, CityCharterCommon,\
    CityCharterSettings, BSOutageMasterDaily, EmailReport
from django.db.models import Q
from django.conf import settings
from nocout.mixins.permissions import SuperUserRequiredMixin
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
# Import advance filtering mixin for BaseDatatableView
from nocout.mixins.datatable import AdvanceFilteringMixin, DatatableSearchMixin
from nocout.settings import SINGLE_REPORT_EMAIL, REPORT_EMAIL_PERM
from django.views.decorators.csrf import csrf_exempt


from django.http import HttpRequest

import os
import logging
import datetime

logger = logging.getLogger(__name__)


class DownloadCenter(ListView):
    """
        Generate datatable views for reports associated with various technologies
    """

    model = ProcessedReportDetails
    template_name = 'download_center/download_center_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        # get page type
        page_type = self.kwargs['page_type']

        # get report name & title
        report_id = ''
        report_name = ''
        report_title = ''
        email_exists = False
        try:
            report_setting_obj = ReportSettings.objects.get(page_name=page_type)
            report_id = report_setting_obj.id
            report_name = report_setting_obj.report_name
            report_title = report_setting_obj.report_title.strip()

            if not report_title:
                report_title = report_name

            if 'Report' not in report_title:
                report_title += ' Report'
        except Exception as e:
            pass

        try:
            emails = EmailReport.objects.filter(report_name=report_setting_obj)
            if emails.exists():
                email_exists = True
        except Exception, e:
            pass

        if 'bs_outage_daily' in page_type:
            report_title = 'Raw BS Outage Report'
            self.template_name = 'download_center/bs_outage_list.html'

        context = super(DownloadCenter, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'report_name', 'sTitle': 'Name', 'sWidth': 'auto'},
            {'mData': 'created_on', 'sTitle': 'Created On', 'sWidth': 'auto'},
            {'mData': 'report_date', 'sTitle': 'Report Date', 'sWidth': 'auto'},
            {'mData': 'path', 'sTitle': 'Report', 'sWidth': 'auto', 'bSortable': False}
        ]
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['page_type'] = page_type
        context['report_name'] = report_name
        context['report_id'] = report_id
        context['report_title'] = report_title
        context['email_exists'] = email_exists

        return context


class DownloadCenterListing(BaseDatatableView):
    """
    A generic class based view for the reports data table rendering.
    """
    model = ProcessedReportDetails
    columns = ['report_name', 'created_on', 'report_date', 'path']
    order_columns = ['report_name', 'created_on', 'report_date']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        # get page type
        page_type = self.request.GET.get('page_type')

        # get report name
        report_name = ""
        try:
            report_name = ReportSettings.objects.get(page_name=page_type).report_name
        except Exception as e:
            logger.info(e.message)

        # fields list those are excluded from search
        exclude_columns = ['created_on', 'report_date']

        # search keyword
        # sSearch = self.request.GET.get('sSearch', None)
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % self.model.__name__
            for column in self.columns:
                # avoid search on columns in exclude list
                if column in exclude_columns:
                    continue
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").filter(report_name='"+str(report_name)+"').values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        report_name = ""
        try:
            report_name = ReportSettings.objects.get(page_name=self.request.GET['page_type']).report_name
        except Exception as e:
            logger.info(e.message)

        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        
        qs = ProcessedReportDetails.objects.filter(
            report_name=report_name
        ).values(*self.columns+['id']).order_by('-report_date')

        return qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()

        for dct in qs:
            # icon for excel file
            excel_green = static("img/ms-office-icons/excel_2013_green.png")

            # full path of report
            report_path = ""
            try:
                report_path = dct['path']
                splitter = settings.REPORT_RELATIVE_PATH
                report_link = report_path.split(splitter)[1]
                report_path = report_link
            except Exception as e:
                logger.info(e.message)

            # 'created on' field timezone conversion from 'utc' to 'local'
            try:
                dct['created_on'] = nocout_utils.convert_utc_to_local_timezone(dct['created_on'])
            except Exception as e:
                logger.error("Timezone conversion not possible. Exception: ", e.message)

            # 'report date' field timezone conversion from 'utc' to 'local'
            try:
                dct['report_date'] = nocout_utils.convert_utc_to_local_timezone(dct['report_date'])
            except Exception as e:
                logger.error("Timezone conversion not possible. Exception: ", e.message)

            dct.update(
                path='<a href="{}"><img src="{}" style="float:left; display:block; height:25px; width:25px;">'.format(
                    report_path, excel_green))
            
            actions_data = '<a href="/download_center/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.get('id'))

            try:
                if SINGLE_REPORT_EMAIL:
                    report_email_perm = json.loads(REPORT_EMAIL_PERM)
                else:
                    report_email_perm = {}
            except Exception as e:
                logger.exception(e)
            
            page_type = self.request.GET.get('page_type')

            if report_email_perm.get(page_type):
                actions_data += '&nbsp; <span style="cursor: pointer;" class="send_report_btn" title="Email Report" report_id="{0}"> \
                                <i class="fa fa-envelope text-primary"></i></span>'.format(dct.pop('id'))

            dct.update(actions=actions_data)

        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.

        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret


class DownloadCenterReportDelete(SuperUserRequiredMixin, DeleteView):
    """
    Class based View to delete the GISInventoryBulkImport
    """
    model = ProcessedReportDetails
    template_name = 'download_center/download_center_delete.html'

    def delete(self, request, *args, **kwargs):
        # report object
        report_obj = self.get_object()

        # page type
        page_type = ""
        try:
            page_type = ReportSettings.objects.get(report_name=report_obj.report_name).page_name
        except Exception as e:
            logger.info(e.message)

        # remove report file if it exists
        try:
            os.remove(report_obj.path)
        except Exception as e:
            logger.info(e.message)

        # delete entry from database
        report_obj.delete()

        # if successfull, return to
        return HttpResponseRedirect(reverse_lazy('InventoryDownloadCenter', kwargs={'page_type': page_type}))


class CityCharterReportHeaders(ListView):
    """
        Generate datatable headers for city charter reports
    """

    model = CityCharterCommon
    template_name = 'dashboard/main_dashboard/home.html'

    def get_context_data(self, **kwargs):

        datatable_headers = [
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

        context = {
            'datatable_headers': json.dumps(datatable_headers)
        }
        
        return context


class CityCharterReportListing(BaseDatatableView, AdvanceFilteringMixin, DatatableSearchMixin):
    """
    A generic class based view for City Charter Report datatable rendering.
    """
    model = CityCharterCommon
    
    columns = [
        'city_name',
        'p2p_los',
        'p2p_uas',
        'p2p_pd',
        'p2p_latancy',
        'p2p_normal',
        'p2p_ss_count',
        'p2p_ss_percentage',
        'pmp_los',
        'pmp_jitter',
        'pmp_rereg',
        'pmp_ul',
        'pmp_pd',
        'pmp_latancy',
        'pmp_normal',
        'pmp_ss_count',
        'pmp_ss_percentage',
        'wimax_los',
        'wimax_na',
        'wimax_rogue_ss',
        'wimax_ul',
        'wimax_pd',
        'wimax_latancy',
        'wimax_normal',
        'wimax_ss_count',
        'wimax_ss_percentage',
        'total_ss_count',
        'total_ss_percentage'
    ]

    order_columns = columns
    # max limit of records returned
    max_display_length = 100

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        return self.model.objects.values(*self.columns)

    def prepare_results(self, qs):
        json_data = [{key: val if val or val == 0 else "" for key, val in dct.items()} for dct in qs]
        return json_data

    def get_context_data(self, *args, **kwargs):

        request = self.request

        self.initialize(*args, **kwargs)
        # Is Data Limited
        is_limited_data_req = self.kwargs['is_data_limited'] if 'is_data_limited' in self.kwargs else 'no'

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # prepare output data
        aaData = self.prepare_results(qs)

        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }

        return ret


class CityCharterSettingsView(FormView):
    template_name = 'download_center/city_charter_settings.html'
    success_url = '/city_charter_settings/'
    form_class = CityCharterSettingsForm

    def get_form(self, form_class):
        return form_class(
            initial=self.get_initial(),
        )

    def post(self, request, *args, **kwargs):
        # Fetch post parameters.
        tech_name = self.request.POST['technology'] if 'technology' in self.request.POST else ""
        los = self.request.POST['los'] if 'los' in self.request.POST else ""
        n_align = self.request.POST['n_align'] if 'n_align' in self.request.POST else ""
        rogue_ss = self.request.POST['rogue_ss'] if 'rogue_ss' in self.request.POST else ""
        jitter = self.request.POST['jitter'] if 'jitter' in self.request.POST else ""
        rereg = self.request.POST['rereg'] if 'rereg' in self.request.POST else ""
        uas = self.request.POST['uas'] if 'uas' in self.request.POST else ""
        pd = self.request.POST['pd'] if 'pd' in self.request.POST else ""
        latency = self.request.POST['latency'] if 'latency' in self.request.POST else ""
        normal = self.request.POST['normal'] if 'normal' in self.request.POST else ""

        # Create form.
        form = CityCharterSettingsForm(self.request.POST)

        # Process data if form is valid else redirect to form.
        if form.is_valid():
            # Get technology.
            technology = None
            try:
                technology = DeviceTechnology.objects.get(name__iexact=tech_name)
            except Exception as e:
                logger.exception(e.message)

            if technology:
                # Fetch row corresponding to the 'technology' from 'download_center_citychartersettings'.
                # If exist then update else create it.
                row = None
                try:
                    row = CityCharterSettings.objects.get(technology=technology)
                except Exception as e:
                    logger.exception(e.message)

                if row:
                    # Update record.
                    row.los = los
                    row.n_align = n_align
                    row.rogue_ss = rogue_ss
                    row.jitter = jitter
                    row.rereg = rereg
                    row.uas = uas
                    row.pd = pd
                    row.latency = latency
                    row.normal = normal
                    row.save()
                else:
                    # Create record.
                    row = CityCharterSettings()
                    row.technology = technology
                    row.los = los
                    row.n_align = n_align
                    row.rogue_ss = rogue_ss
                    row.jitter = jitter
                    row.rereg = rereg
                    row.uas = uas
                    row.pd = pd
                    row.latency = latency
                    row.normal = normal
                    row.save()
            else:
                pass

        return HttpResponseRedirect('/city_charter_settings/')


class BSOutageCustomReportHeaders(ListView):
    """

    """
    model = BSOutageMasterDaily
    template_name = 'download_center/download_center_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(BSOutageCustomReportHeaders, self).get_context_data(**kwargs)
        datatable_headers = [
            { 'mData': 'week_number', 'sTitle': 'Week of the Year' },
            { 'mData': 'ticket_number', 'sTitle': 'Trouble Ticket Number' },
            { 'mData': 'total_affected_bs', 'sTitle': 'Number of BS Affected' },
            { 'mData': 'city', 'sTitle': 'City' },
            { 'mData': 'type_of_city', 'sTitle': 'Type of City' },
            { 'mData': 'bs_name', 'sTitle': 'BaseStation Name' },
            { 'mData': 'bs_type', 'sTitle': 'BaseStation Type' },
            { 'mData': 'fault_type', 'sTitle': 'Type of Fault' },
            { 'mData': 'bs_ip', 'sTitle': 'BS IP Address' },
            { 'mData': 'bs_sw_version', 'sTitle': 'BS Software Version' },
            { 'mData': 'total_affected_sector', 'sTitle': 'Number of Sectors Affected' },
            { 'mData': 'switch_reachability', 'sTitle': 'Switch Reachability' },
            { 'mData': 'outage_timestamp', 'sTitle': 'Outage Date And Time'},
            { 'mData': 'restored_timestamp', 'sTitle': 'Restored Date And Time'},
            { 'mData': 'alarm_restored_timestamp', 'sTitle': 'Alarm Restored Date And Time'},
            { 'mData': 'outage_min_per_site', 'sTitle': 'Outage Per Site(Min.)' },
            { 'mData': 'mttr_hrs', 'sTitle': 'MTTR Hrs' },
            { 'mData': 'mttr', 'sTitle': 'MTTR' },
            { 'mData': 'outage_total_min', 'sTitle': 'Outage Total(Min.)' },
            { 'mData': 'alarm_outage_min', 'sTitle': 'Alarm Outage(Min.)' },
            { 'mData': 'total_affected_enterprise_ss', 'sTitle': 'Number of Enterprise SS Affected' },
            { 'mData': 'total_affected_retail_ss', 'sTitle': 'Number of Retail SS Affected' },
            { 'mData': 'l1_engg_name', 'sTitle': 'Name of L1 Engineer' },
            { 'mData': 'l2_engg_name', 'sTitle': 'Name of L2 Engineer' },
            { 'mData': 'call_assigned_to', 'sTitle': 'Call Assigned To' },
            { 'mData': 'last_modified_by', 'sTitle': 'Last Modified By' },
            { 'mData': 'tac_tt_number', 'sTitle': 'Tac TT Number' },
            { 'mData': 'cause_code', 'sTitle': 'Cause Code' },
            { 'mData': 'sub_cause_code', 'sTitle': 'Sub Cause Code' },
            { 'mData': 'unit_replaced', 'sTitle': 'Unit Replaced' },
            { 'mData': 'equipment_replaced', 'sTitle': 'Equipment Replaced' },
            { 'mData': 'old_sr_number', 'sTitle': 'Old Sno.' },
            { 'mData': 'new_sr_number', 'sTitle': 'New Sno.' },
            { 'mData': 'alarm_observer', 'sTitle': 'Alarm Observed' },
            { 'mData': 'delay', 'sTitle': 'Delay' },
            { 'mData': 'delay_reason', 'sTitle': 'Delay Reason' },
            { 'mData': 'restore_action', 'sTitle': 'Action Taken to Restore the BS' },
            { 'mData': 'fault_description', 'sTitle': 'Remark/Detail Fault Description'},
            { 'mData': 'status', 'sTitle': 'Status' },
            { 'mData': 'infra_provider', 'sTitle': 'INFRA Provider' },
            { 'mData': 'site_id', 'sTitle': 'Site ID' },
            { 'mData': 'spot_cases', 'sTitle': 'Spot Cases' },
            { 'mData': 'fault_history', 'sTitle': 'Fault History'},
            { 'mData': 'rfo', 'sTitle': 'RFO' }
        ]

        context['datatable_headers'] = json.dumps(datatable_headers)

        return context


class BSOutageCustomReportListing(BaseDatatableView):
    """

    """
    model = BSOutageMasterDaily
    columns = [
        'week_number', 'ticket_number', 'total_affected_bs', 'city',
        'type_of_city', 'bs_name', 'bs_type', 'fault_type',
        'bs_ip', 'bs_sw_version', 'total_affected_sector', 'switch_reachability',
        'outage_timestamp', 'restored_timestamp', 'alarm_restored_timestamp', 'outage_min_per_site',
        'mttr_hrs', 'mttr', 'outage_total_min', 'alarm_outage_min',
        'total_affected_enterprise_ss', 'total_affected_retail_ss', 'l1_engg_name', 'l2_engg_name',
        'call_assigned_to', 'last_modified_by', 'tac_tt_number', 'cause_code',
        'sub_cause_code', 'unit_replaced', 'equipment_replaced', 'old_sr_number',
        'new_sr_number', 'alarm_observer', 'delay', 'delay_reason',
        'restore_action', 'fault_description', 'status', 'infra_provider',
        'site_id', 'spot_cases', 'fault_history', 'rfo'
    ]

    order_columns = columns
    report_ids = list()

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        # search keyword
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            query = []
            exec_query = "qs = qs.filter("
            for column in self.columns:
                # avoid search on columns in exclude list
                if column in exclude_columns:
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

        start_time = self.request.GET.get('start_date')
        end_time = self.request.GET.get('end_date')

        if start_time and end_time:
            start_time_obj = datetime.datetime.fromtimestamp(float(start_time))
            end_time_obj = datetime.datetime.fromtimestamp(float(end_time))
        else:
            start_time_obj = datetime.datetime.now() - datetime.timedelta(1)
            end_time_obj = datetime.datetime.now()

        # Fetch report ids as per the selected date range
        report_ids = list(ProcessedReportDetails.objects.filter(
                        report_name__in=['DailyRawBaseStationOutage'],
                        report_date__gte=start_time_obj,
                        report_date__lte=end_time_obj
                    ).values_list('id', flat=True))

        qs = BSOutageMasterDaily.objects.filter(processed_report__in=report_ids).values(*self.columns)

        return qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request
        self.initialize(*args, **kwargs)
        
        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }
        return ret


class EmailListUpdating(View):
    """
    This Class is used for two purpose.
    1. Single report emailing which is in 'if report_id:' case
    2. To update the scheduled email for particular report type.
    """
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(EmailListUpdating, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        page_name = self.request.POST.get('page_name',None)
        email_list = self.request.POST.getlist('emails[]', None)
        report_id = self.request.POST.get('report_id',None)
        
        if report_id:
            # Args: report_id, exist means functionality is being used to send a single report.
            # Additional Functionality where we can send single report to multiple mail id's instantly.
            report_name = ProcessedReportDetails.objects.get(id=report_id).report_name
            file_path = ProcessedReportDetails.objects.get(id=report_id).path
            file_path = file_path.split()
            request_object = HttpRequest()
            from alarm_escalation.views import EmailSender
            email_sender = EmailSender()
            email_sender.request = request_object
            try:
                email_sender.request.POST = {
                    'subject': report_name,
                    'message': '',
                    'to_email': email_list,
                    'attachment_path': file_path
                }
            except Exception,e:
                pass

            try:
                email_sender.post(email_sender)
                response = {
                    'success': 1,
                    'message': 'Report Mailed Successfully.'
                }
            except Exception, e:
                logger.exception(e)
                response = {
                    'success': 0,
                    'message': 'Report Mailed not sent.'
                }
                pass

        else:
            # Comma seperated string of emails.
            email_list = ", ".join(email_list)

            try:
                report_name = ReportSettings.objects.get(page_name__iexact=page_name)
            except ReportSettings.DoesNotExist:
                report_name = ''

            post_values = {
                'email_list': email_list,
            }
            EmailReport.objects.update_or_create(report_name=report_name, defaults=post_values)
            response = {
                'success': 1,
                'message': 'Successfully Updated'
            }

        return JsonResponse(response)


class GetEmails(View):
    """
    This class is to get emails if exist for that report type.
    """
    def get(self, request, page_type, *args, **kwargs):
        page_name = page_type
        try:
            emails = EmailReport.objects.get(report_name=ReportSettings.objects.get(page_name=page_name)).email_list
        except EmailReport.DoesNotExist:
            emails = ''

        result = {
            'success': 0,
            'message': 'No existing Value',
            'data': {
                 'emails': emails
            }
        }

        if emails:
            result['success'] = 1
            result['message'] = 'Sucessfullly loaded pre-existing values'
        return JsonResponse(result)

class ResetEmailReport(View):
    """
    User can Reset Scheduled Email report which will delete record from database.
    """
    def get(self, request, *args, **kwargs):
        result = {
            'success': 0,
            'message': 'Emails not deleted. Please try again later.'
        }

        report_id = request.GET.get('id')

        if not report_id:
            return HttpResponse(json.dumps(result))

        try:
            emails = EmailReport.objects.filter(report_name__id=report_id)
            if emails.exists():
                emails.delete()
                result = {
                    'success': 1,
                    'message': 'Emails deleted successfully.'
                }
        except Exception, e:
            logger.exception(e)

        return HttpResponse(json.dumps(result))


class ProcessedReportEmailAPI(View):
    """
    ProcessedReportEmailAPI will be called after each daily report generation is complete with input variable
    'pk' which is primary key of report entry in database ProcessedReportDetails.
    """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ProcessedReportEmailAPI, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        report_email_perm = json.loads(REPORT_EMAIL_PERM)
        if pk:
            try:
                processed_reports = ProcessedReportDetails.objects.get(id=pk)
            except Exception, e:
                processed_reports = None
            if processed_reports:
                report_name = processed_reports.report_name
                page_name = ReportSettings.objects.get(report_name=report_name).page_name

                file_path = processed_reports.path
                file_path = file_path.split()

                email_list = EmailReport.objects.get(
                    report_name=ReportSettings.objects.get(report_name=report_name)).email_list
                email_list = email_list.split(",")
                email_list = [email.strip() for email in email_list]

                result = {
                    "success": 0,
                    "message": "Failed to send email.",
                    "data": {
                        "subject": report_name,
                        "message": 'None',
                        "from_email": settings.DEFAULT_FROM_EMAIL,
                        "to_email": email_list,
                        "attachment_path": file_path
                    }
                }
                # Verifying if email Report is enabled for this Report.
                if report_email_perm.get(page_name):
                    request_object = HttpRequest()
                    from alarm_escalation.views import EmailSender
                    # Generating POST Request for EmailSender API.
                    email_sender = EmailSender()
                    email_sender.request = request_object

                    try:
                        email_sender.request.POST = {
                            'subject': report_name,
                            'message': '',
                            'to_email': email_list,
                            'attachment_path': file_path
                        }
                    except Exception, e:
                        logger.exception(e)
                    try:
                        email_sender.post(email_sender)
                        result['success'] = 1
                        result['message'] = 'Mail sent Sucessfully'
                        result['data']['message'] = 'Here is Your daily Report'
                    except Exception, e:
                        logger.exception(e)

        return HttpResponse(json.dumps(result))
