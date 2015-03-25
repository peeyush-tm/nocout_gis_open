import json
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic.edit import DeleteView
from models import ProcessedReportDetails, ReportSettings, CityCharterP2P, CityCharterPMP, CityCharterWiMAX
from django.db.models import Q
from django.conf import settings
from nocout.utils.util import convert_utc_to_local_timezone

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
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
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
        sSearch = self.request.GET.get('sSearch', None)
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
                dct['created_on'] = convert_utc_to_local_timezone(dct['created_on'])
            except Exception as e:
                logger.error("Timezone conversion not possible. Exception: ", e.message)

            # 'report date' field timezone conversion from 'utc' to 'local'
            try:
                dct['report_date'] = convert_utc_to_local_timezone(dct['report_date'])
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


class DownloadCenterReportDelete(DeleteView):
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

class CityCharterReportListing(BaseDatatableView):
    """
    A generic class based view for City Charter Report datatable rendering.
    """
    model = CityCharterP2P
    
    columns = [
        'circuit_id',
        'city_name',
        'state_name',
        'customer_name',
        'bs_name',
        'seg_p2p',
        'far_ip',
        'near_ip',
        'circuit_type',
        'far_device_ss_mac_address',
        'near_sector_device_mac_address',
        'rssi_during_aceptance',
        'uas',
        'packetDrop',
        'Latencydrop',
        'device_state',
        'current_value',
        'ul',
        'latency',
        'pd'
    ]

    order_columns = columns
    # max limit of records returned
    max_display_length = 100

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        return self.model.objects.values(*self.columns)

    def prepare_results(self, qs):
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        return json_data

    def get_context_data(self, *args, **kwargs):

        request = self.request

        self.initialize(*args, **kwargs)
        # Technology name
        technology_name = self.kwargs['tech_name'] if 'tech_name' in self.kwargs else 'P2P'
        # Is Data Limited
        is_limited_data_req = self.kwargs['is_data_limited'] if 'is_data_limited' in self.kwargs else 'no'

        if is_limited_data_req.lower() == 'yes':
            # max limit of records returned
            self.max_display_length = 5
            # Few Columns List
            self.columns = [
                'city_name',
                'bs_name',
                'circuit_id'
            ]
            # Append Column as per the technology
            if technology_name in ['PMP']:
                self.columns.append('seg_pmp')
            elif technology_name in ['WiMAX']:
                self.columns.append('seg_wimax')
            else:
                self.columns.append('seg_p2p')

            self.order_columns = self.columns
        else:
            # Columns list as per the technology
            if technology_name in ['PMP']:
                self.columns = [
                    'circuit_id',
                    'city_name',
                    'state_name',
                    'customer_name',
                    'bs_name',
                    'vendor',
                    'ss_device_technology_name',
                    'device_ss_ip_address',
                    'device_ss_mac_address',
                    'sector_device_ip_address',
                    'sector_id',
                    'dl_rssi_during_aceptance',
                    'intrf',
                    'seg_pmp',
                    'ul_jitter',
                    'dl_jitter',
                    'rereg_count',
                    'reg_count',
                    'packetDrop',
                    'Latencydrop',
                    'device_state',
                    'current_value',
                    'ul',
                    'latency',
                    'pd'
                ]
            elif technology_name in ['WiMAX']:
                self.columns = [
                    'circuit_id',
                    'city_name',
                    'state_name',
                    'customer_name',
                    'bs_name',
                    'vendor',
                    'ss_device_technology_name',
                    'device_ss_ip_address',
                    'device_ss_mac_address',
                    'sector_device_ip_address',
                    'sector_id',
                    'dl_rssi_during_aceptance',
                    'intrf',
                    'seg_wimax',
                    'pmp',
                    'ul_cinr',
                    'dl_cinr',
                    'ptx',
                    'packetDrop',
                    'Latencydrop',
                    'device_state',
                    'current_value',
                    'ul',
                    'latency',
                    'pd'
                ]
            else:
                self.columns = self.columns

            self.order_columns = self.columns

        # Update the current model as per the technology
        if technology_name in ['PMP']:
            self.model = CityCharterPMP
        elif technology_name in ['WiMAX']:
            self.model = CityCharterWiMAX

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