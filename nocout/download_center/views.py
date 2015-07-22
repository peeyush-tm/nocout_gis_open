import json
from device.models import DeviceTechnology
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, FormView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic.edit import DeleteView
from download_center.forms import CityCharterSettingsForm
from models import ProcessedReportDetails, ReportSettings, CityCharterP2P, CityCharterPMP, CityCharterWiMAX, CityCharterCommon, \
    CityCharterSettings
from django.db.models import Q
from django.conf import settings
from nocout.mixins.permissions import SuperUserRequiredMixin
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

import os
import logging

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

        # get report name
        report_name = ""
        try:
            report_name = ReportSettings.objects.get(page_name=page_type).report_name
        except Exception as e:
            pass

        context = super(DownloadCenter, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'report_name', 'sTitle': 'Name', 'sWidth': 'auto'},
            {'mData': 'path', 'sTitle': 'Alias', 'sWidth': 'auto'},
            {'mData': 'created_on', 'sTitle': 'Created On', 'sWidth': 'auto'},
            {'mData': 'report_date', 'sTitle': 'Report Date', 'sWidth': 'auto'},
        ]
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['page_type'] = page_type
        context['report_name'] = report_name

        return context


class DownloadCenterListing(BaseDatatableView):
    """
    A generic class based view for the reports data table rendering.
    """
    model = ProcessedReportDetails
    columns = ['report_name', 'path', 'created_on', 'report_date']
    order_columns = ['report_name', 'path', 'created_on', 'report_date']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        # get page type
        page_type = self.request.GET['page_type']

        # get report name
        report_name = ""
        try:
            report_name = ReportSettings.objects.get(page_name=self.request.GET['page_type']).report_name
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
        return ProcessedReportDetails.objects.filter(report_name=report_name).values(*self.columns+['id'])

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
            dct.update(
                actions='<a href="/download_center/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                    dct.pop('id')))
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


class CityCharterReportListing(BaseDatatableView):
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

        # if is_limited_data_req.lower() == 'yes':
            # max limit of records returned
            # self.max_display_length = 5

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
