import os
import json
import simplejson
import time
import operator
from django.db.models import Q
from nocout.settings import MEDIA_URL, MEDIA_ROOT, USE_TZ
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.views.generic.base import View
from tasks import get_datatable_response
from models import Downloader
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic.edit import DeleteView
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
# Import advance filtering mixin for BaseDatatableView
from nocout.mixins.datatable import AdvanceFilteringMixin
import logging
from operator import itemgetter
from user_profile.utils.auth import in_group

logger = logging.getLogger(__name__)

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


class DownloaderHome(View):
    def get(self):
        # result
        result = dict()
        result['message'] = "Please select proper view."

        return HttpResponse(json.dumps(result), content_type="application/json")


class DataTableDownloader(View):
    """
        Generating headers for datatables
        Parameters:
            - app (unicode) - name of app for e.g. performance
            - rows (unicode) - name of datatable listing class for e.g. LivePerformanceListing
            - headers (unicode) - name datatable headers class for e.g. LivePerformance
            - headers_data (dict) - dictionary of GET/POST parameters passed in datatable headers view as request
                                    for e.g.
                                    {
                                        'data_tab': 'P2P',
                                        'page_type': 'customer',
                                        'download_excel': 'yes'
                                    }
            - rows_data (dict) - dictionary of GET/POST parameters passed in datatable listing view as request for e.g.
                                    {
                                        'data_tab': 'P2P',
                                        'page_type': 'customer',
                                        'download_excel': 'yes'
                                    }

        URL:
           - "/downloader/datatable/?app=performance&headers=LivePerformance&rows=LivePerformanceListing&
               headers_data={'page_type': 'customer', 'data_tab': 'P2P', 'download_excel': 'yes' }&
               rows_data={'page_type': 'customer', 'data_tab': 'P2P', 'download_excel': 'yes' }"

        Returns:
           - 'response' (dict) - response dict send in json format for e.g.
                                {
                                    'message': 'Startdownloading.',
                                    'success': 1
                                }
    """
    def get(self, request):
        # response
        response = {
            'success': 0,
            'message': "Failed to download.",
        }

        # get app
        app = self.request.GET.get('app', None)

        # get name
        rows = self.request.GET.get('rows', None)

        # get headers
        headers = self.request.GET.get('headers', None)

        # get fields needs to be excluded
        excluded = list()
        try:
            excluded = eval(self.request.GET.get('excluded', None))
        except Exception as e:
            pass

        # maximum no. of rows in excel
        max_rows = self.request.GET.get('max_rows', None)

        if app and rows and headers:
            # get current user name
            username = self.request.user.username

            timestamp = time.time()
            fulltime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S')

            # downloader object
            d_obj = Downloader()
            d_obj.app_name = app
            d_obj.headers_view = headers
            d_obj.rows_view = rows
            d_obj.downloaded_by = username
            d_obj.status = 2
            d_obj.description = "Failed to download on {}.".format(fulltime)

            # get rows and headers request data
            headers_data = ""
            rows_data = {}
            advance_filter = ""
            try:
                try:
                    rows_data = eval(self.request.GET.get('rows_data', None))
                except Exception, e:
                    # logger.info(e.message)
                    pass

                try:
                    headers_data = eval(self.request.GET.get('headers_data', None))
                except Exception, e:
                    # logger.info(e.message)
                    pass
                # get advance filtering object
                try:
                    advance_filter = self.request.GET.get('advance_filter', None)
                    rows_data['advance_filter'] = advance_filter
                except Exception, e:
                    logger.info(e.message)
                    pass

                response['message'] = "Inventory download started. Please check status \
                <a href='/downloader/' target='_blank'>Here</a>."
                response['success'] = 1
                d_obj.status = 0
                d_obj.description = "Start downloading on {}.".format(fulltime)
            except Exception as e:
                response['message'] = "Wrong data format."

            d_obj.headers_data = headers_data
            d_obj.rows_data = rows_data

            # saving downloader object
            d_obj.save()
            
            # payload for celery job
            payload = {
                'app': app,
                'headers': headers,
                'headers_data': headers_data,
                'rows': rows,
                'rows_data': rows_data,
                'username': username,
                'fulltime': fulltime,
                'object_id': d_obj.id,
                'excluded': excluded,
                'max_rows': max_rows
            }

            # queue download to celery
            get_datatable_response.delay(payload)
        else:
            response['message'] = "Downloading failed due to wrong data format."

        return HttpResponse(json.dumps(response), content_type="application/json")


class DownloaderHeaders(ListView):
    """
        Generating headers for datatables
        Parameters:
            - download_name (unicode) - display name for datatable for e.g. Backhaul Status
            - download_type (unicode) - datatable listing class name for e.g. LivePerformanceListing
            - params (unicode) - string containing extra paramaters received by datatable
                                 for e.g. {'page_type' : 'network'}

        URL:
           - "/downloader/list/?download_name=Backhaul%20Status&download_type=LivePerformanceListing&params={}"

        Returns:
           - 'result' (dict) - dictionary containing context data for e.g.
                                {
                                    u'paginator': None,
                                    u'object_list': [
                                        <Downloader: download_excels/device_priyesh_2015-03-23-10-50-33.xls>,
                                        <Downloader: download_excels/performance_priyesh_2015-03-23-10-51-49.xls>
                                    ],
                                    'datatable_headers': '[
                                        {
                                            "mData": "file_path",
                                            "sTitle": "File",
                                            "sWidth": "auto"
                                        },
                                        {
                                            "mData": "file_type",
                                            "sTitle": "File Type",
                                            "sWidth": "auto"
                                        },
                                        {
                                            "mData": "status",
                                            "sTitle": "Status",
                                            "sWidth": "auto"
                                        },
                                        {
                                            "mData": "description",
                                            "sTitle": "Description",
                                            "sWidth": "auto"
                                        },
                                        {
                                            "mData": "downloaded_by",
                                            "sTitle": "Downloaded By",
                                            "sWidth": "auto"
                                        },
                                        {
                                            "mData": "requested_on",
                                            "sTitle": "Requested On",
                                            "sWidth": "auto"
                                        },
                                        {
                                            "mData": "request_completion_on",
                                            "sTitle": "Request Completion Date",
                                            "sWidth": "auto"
                                        },
                                        {
                                            "mData": "actions",
                                            "sTitle": "Actions",
                                            "bSortable": false,
                                            "sWidth": "5%"
                                        }
                                    ]',
                                    u'downloader_list': [
                                        <Downloader: download_excels/device_priyesh_2015-03-23-10-50-33.xls>,
                                        <Downloader: download_excels/performance_priyesh_2015-03-23-10-51-49.xls>
                                    ],
                                    u'page_obj': None,
                                    'params': u'{

                                    }',
                                    'download_name': u'BackhaulStatus',
                                    'download_type': u'LivePerformanceListing',
                                    u'is_paginated': False,
                                    u'view': <downloader.views.DownloaderHeadersobjectat0x7fbaf612a850>
                                }
    """

    model = Downloader
    template_name = 'downloader/downloader_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        # get download name
        download_name = self.request.GET.get('download_name', None)

        # get download type
        download_type = self.request.GET.get('download_type', None)

        # get extra parameters
        params = self.request.GET.get('params', None)

        context = super(DownloaderHeaders, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'file_path', 'sTitle': 'File', 'sWidth': 'auto'},
            {'mData': 'file_type', 'sTitle': 'File Type', 'sWidth': 'auto'},
            {'mData': 'status', 'sTitle': 'Status', 'sWidth': 'auto'},
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto'},
            {'mData': 'downloaded_by', 'sTitle': 'Downloaded By', 'sWidth': 'auto'},
            {'mData': 'requested_on', 'sTitle': 'Requested On', 'sWidth': 'auto'},
            {'mData': 'request_completion_on', 'sTitle': 'Request Completion Date', 'sWidth': 'auto'},
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['download_name'] = download_name
        context['download_type'] = download_type
        context['params'] = params

        return context


class DownloaderListing(BaseDatatableView, AdvanceFilteringMixin):
    """
    A generic class based view for the reports data table rendering.
    """
    model = Downloader
    columns = ['file_path',
               'file_type',
               'status',
               'description',
               'downloaded_by',
               'requested_on',
               'request_completion_on']
    order_columns = ['file_path',
                     'file_type',
                     'status',
                     'description',
                     'downloaded_by',
                     'requested_on',
                     'request_completion_on']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """

        # get download type
        download_type = self.request.GET.get('download_type', None)

        # get extra parameters
        params = self.request.GET.get('params', None)

        # extra params list
        params_list = list()

        if params:
            try:
                params = eval(params)
                for key, val in params.items():
                    temp_dict = dict()
                    temp_dict[key] = val
                    params_list.append(str(temp_dict).replace('{', '').replace('}', ''))
            except Exception as e:
                pass
        
        # fields list those are excluded from search
        exclude_columns = ['requested_on', 'request_completion_on']

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
            if params:
                exec_query += ").filter(reduce(operator.and_, (Q(rows_data__contains=x) for x in "+str(params_list)+"))).filter( \
                    rows_view="+str(download_type)+", downloaded_by="+str(self.request.user.username)+").values(*self.columns + ['id'])"
            else:
                exec_query += ").filter(rows_view='"+str(download_type)+"').values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        # get download type
        download_type = self.request.GET.get('download_type', None)

        # get extra parameters
        params = self.request.GET.get('params', None)

        # extra params list
        params_list = list()

        if params:
            try:
                params = eval(params)
                for key, val in params.items():
                    temp_dict = dict()
                    temp_dict[key] = val
                    params_list.append(str(temp_dict).replace('{', '').replace('}', ''))
            except Exception as e:
                pass

        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        if params:
            return Downloader.objects.filter(
                reduce(operator.and_, (Q(rows_data__contains=x) for x in params_list))).filter(
                rows_view=download_type, downloaded_by=self.request.user.username).values(*self.columns + ['id'])
        else:
            return Downloader.objects.filter(rows_view=download_type, downloaded_by=self.request.user.username).values(
                *self.columns + ['id'])

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

            # icon for excel file
            excel_red = static("img/ms-office-icons/excel_2013_red.png")

            # full path of download
            download_path = ""
            try:
                download_path = MEDIA_URL + dct['file_path']
            except Exception as e:
                logger.info(e.message)

            try:
                if dct.get('status') == 0:
                    dct.update(status='<span class="text-warning">Pending</span>')
            except Exception as e:
                logger.info(e.message)

            try:
                if dct.get('status') == 1:
                    dct.update(status='<span class="text-success">Success</span>')
            except Exception as e:
                logger.info(e.message)

            try:
                if dct.get('status') == 2:
                    dct.update(status='<span class="text-danger">Failed</span>')
            except Exception as e:
                logger.info(e.message)

            # 'requested on' field timezone conversion from 'utc' to 'local'
            try:
                dct['requested_on'] = nocout_utils.convert_utc_to_local_timezone(dct['requested_on'])
            except Exception as e:
                logger.error("Timezone conversion not possible. Exception: ", e.message)

            # 'request completion on' field timezone conversion from 'utc' to 'local'
            try:
                dct['request_completion_on'] = nocout_utils.convert_utc_to_local_timezone(dct['request_completion_on'])
            except Exception as e:
                logger.error("Timezone conversion not possible. Exception: ", e.message)

            try:
                if dct.get('status') == "Success":
                    dct.update(
                        file_path='<a href="{}"><img src="{}" style="float:left; display:block; height:25px; width:25px;">'.format(
                            download_path, excel_green))
                else:
                    dct.update(
                        file_path='<img src="{}" style="float:left; display:block; height:25px; width:25px;">'.format(
                            excel_red))
            except Exception as e:
                dct.update(
                    file_path='<img src="{}" style="float:left; display:block; height:25px; width:25px;">'.format(
                        excel_red))
                pass

            dct.update(
                actions='<a href="/downloader/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(
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


class DownloaderCompleteHeaders(ListView):
    """
        Generating headers for datatables
    """

    model = Downloader
    template_name = 'downloader/downloader_complete_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """

        context = super(DownloaderCompleteHeaders, self).get_context_data(**kwargs)

        datatable_headers = [
            {'mData': 'file', 'sTitle': 'File', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'file_name', 'sTitle': 'Filename', 'sWidth': 'auto'},
            {'mData': 'file_type', 'sTitle': 'File Type', 'sWidth': 'auto'},
            {'mData': 'rows_view', 'sTitle': 'Module', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'status', 'sTitle': 'Status', 'sWidth': 'auto'},
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto'},
            {'mData': 'downloaded_by', 'sTitle': 'Downloaded By', 'sWidth': 'auto'},
            {'mData': 'requested_on', 'sTitle': 'Requested On', 'sWidth': 'auto'},
            {'mData': 'request_completion_on', 'sTitle': 'Request Completion Date', 'sWidth': 'auto'},
        ]

        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)

        return context


class DownloaderCompleteListing(BaseDatatableView, AdvanceFilteringMixin):
    """
    A generic class based view for the reports data table rendering.
    """
    model = Downloader
    columns = [
        'file_path',
        'file_path',
        'file_type',
        'rows_view',
        'status',
        'description',
        'downloaded_by',
        'requested_on',
        'request_completion_on',
        'rows_data',
        'app_name'
    ]

    order_columns = columns

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """

        # fields list those are excluded from search
        exclude_columns = ['downloaded_by', 'requested_on', 'request_completion_on']

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
            exec_query += ").filter(downloaded_by='"+str(self.request.user.username)+"').values(*" + \
                          str(self.columns + ['id']) + ")"
            exec exec_query

        return self.advance_filter_queryset(qs)

    def ordering(self, qs):
        """ 
        Get parameters from the request and prepare order by clause
        """
        order_columns = self.order_columns
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        # @priyesh-teramatrix :- Please varify. Returned the latest queryset first as per 'requested_on' time
        return Downloader.objects.filter(
            downloaded_by=self.request.user.username
        ).values(*self.columns + ['id', 'app_name']).order_by('-requested_on')

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """

        success_html = '<span class="text-success">Success</span>'
        fail_html = '<span class="text-danger">Failed</span>'
        pending_html = '<span class="text-warning">Pending</span>'
        no_data_html = '<span class="text-danger">Data table has no data</span>'
        wrong_para_html = '<span class="text-danger">Wrong parameters</span>'

        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        for dct in qs:

            # modified module name
            modified_module_name = ""

            # get app name
            app_name = dct['app_name'].replace("_", " ").title().replace(" ", "")

            # module name
            module_name = dct['rows_view'].replace("Listing", "").replace("Table", "")

            # modified module name
            modified_module_name = "[{}] : [{}]".format(app_name, module_name)

            # green icon for excel file
            excel_green = static("img/ms-office-icons/excel_2013_green.png")

            # red icon for excel file
            excel_red = static("img/ms-office-icons/excel_2013_red.png")

            # grey icon for excel file
            excel_grey = static("img/ms-office-icons/excel_2013_grey.png")

            # set pending status to failed if added_on time is more than 10 minutes

            # get added on timestamp
            time_difference = None
            try:
                if USE_TZ:
                    added_timestamp = dct['requested_on'].replace(tzinfo=None)
                    time_difference = datetime.utcnow() - added_timestamp
                else:
                    added_timestamp = dct['requested_on']
                    time_difference = datetime.now() - added_timestamp
            except Exception as e:
                pass

            # File name which will be downloaded
            try:
                file_name = dct['file_path'].split("/")[1] if dct['file_path'] else "N/A"
            except Exception, e:
                file_name = dct['file_path']

            # File type
            dct['file_type'] = dct['file_type'] if dct['file_type'] else "N/A"

            # Title for report
            try:
                rows_data = eval(dct["rows_data"])
                report_title = rows_data['report_title'] if "report_title" in rows_data else False
            except Exception, e:
                report_title = False

            # full path of download
            download_path = ""
            try:
                download_path = MEDIA_URL + dct['file_path']
            except Exception as e:
                logger.info(e.message)

            try:
                if not dct.get('status'):
                    logger.info("*********************** time_difference - {}".format(time_difference))
                    if time_difference > timedelta(minutes=10, seconds=0):
                        dct.update(status=fail_html)
                    else:
                        dct.update(status=pending_html)
            except Exception as e:
                logger.info(e.message)

            try:
                if dct.get('status') == 1:
                    dct.update(status=success_html)
            except Exception as e:
                logger.info(e.message)

            try:
                if dct.get('status') == 2:
                    dct.update(status=fail_html)
            except Exception as e:
                logger.info(e.message)

            try:
                if dct.get('status') == 3:
                    dct.update(status=no_data_html)
            except Exception as e:
                logger.info(e.message)

            try:
                if dct.get('status') == 4:
                    dct.update(status=wrong_para_html)
            except Exception as e:
                logger.info(e.message)

            # Module name for which the report is downloaded
            if not report_title:
                if modified_module_name:
                    try:
                        dct['rows_view'] = modified_module_name
                    except Exception as e:
                        pass
            else:
                dct['rows_view'] = report_title

            # 'requested on' field timezone conversion from 'utc' to 'local'
            try:
                dct['requested_on'] = nocout_utils.convert_utc_to_local_timezone(dct['requested_on'])
            except Exception as e:
                logger.error("Timezone conversion not possible. Exception: ", e.message)

            # 'request completion on' field timezone conversion from 'utc' to 'local'
            try:
                dct['request_completion_on'] = nocout_utils.convert_utc_to_local_timezone(dct['request_completion_on'])
            except Exception as e:
                logger.error("Timezone conversion not possible. Exception: ", e.message)

            try:
                if dct.get('status') == success_html:
                    download_img_str = '<a href="{}" title="Download Report"><img src="{}" \
                                       style="width:25px;"></a>'.format(download_path, excel_green)

                elif dct.get('status') == pending_html:

                    download_img_str = '<img src="{}" style="width:25px;" title="Please Wait...">'.format(excel_grey)

                else:

                    download_img_str = '<img src="{}" style="width:25px;">'.format(excel_red)

            except Exception as e:
                
                download_img_str = '<img src="{}" style="width:25px;">'.format(excel_red)
                pass

            dct.update(
                file=download_img_str,
                file_name=file_name,
                actions='<a href="/downloader/delete/{0}" title="Delete Report"><i class="fa fa-trash-o text-danger">&nbsp;</i></a>\
                        '.format(dct.pop('id'))
            )
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


class DownloaderDelete(DeleteView):
    """
    Class based View to delete the GISInventoryBulkImport
    """
    model = Downloader
    template_name = 'downloader/downloader_delete.html'

    def delete(self, request, *args, **kwargs):
        # report object
        download_obj = self.get_object()

        # remove report file if it exists
        try:
            os.remove(MEDIA_ROOT + download_obj.file_path)
        except Exception as e:
            logger.info(e.message)

        # delete entry from database
        download_obj.delete()

        # if successfull, return to
        return HttpResponseRedirect('/downloader/')

