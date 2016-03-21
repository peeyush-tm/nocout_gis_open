# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
import os
from downloader.models import Downloader
from nocout.settings import MEDIA_ROOT
from celery.task import task
from django.contrib.auth.models import User
from django.http import HttpRequest
from datetime import datetime
import xlwt
import xlsxwriter
import simplejson
import json

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@task
def get_datatable_response(payload):
    """
        Generating excel for datatable
        Parameters:
            - payload (dict) - payload data for e.g.
                                {
                                    'username': u'priyesh',
                                    'rows': u'LivePerformanceListing',
                                    'app': u'performance',
                                    'object_id': 3L,
                                    'headers': u'LivePerformance',
                                    'rows_data': {
                                        'data_tab': 'P2P',
                                        'page_type': 'customer',
                                        'download_excel': 'yes'
                                    },
                                    'fulltime': '2015-03-23-17-07-35',
                                    'headers_data': {
                                        'data_tab': 'P2P',
                                        'page_type': 'customer',
                                        'download_excel': 'yes'
                                    }
                                }

        URL:
           - "/downloader/datatable/?app=performance&headers=LivePerformance&rows=LivePerformanceListing&
               headers_data={'page_type': 'customer', 'data_tab': 'P2P', 'download_excel': 'yes' }&
               rows_data={'page_type': 'customer', 'data_tab': 'P2P', 'download_excel': 'yes' }"

        Note:
           - Bits used for download status:
                - 0 -> Pending
                - 1 -> Success
                - 2 -> Failed
                - 3 -> Data table has no data
                - 4 -> Wrong parameters

    """

    # get downloader object
    d_obj = None
    try:
        d_obj = Downloader.objects.get(id=payload['object_id'])
    except Exception as e:
        pass

    if all([key in payload for key in ["app", "rows", "headers"]]):
        # current user object
        user = User.objects.get(username=payload['username'])

        # import headers class
        exec "from {}.views import {}".format(payload['app'], payload['headers']) in globals(), locals()

        # import rows data class
        exec "from {}.views import {}".format(payload['app'], payload['rows']) in globals(), locals()

        # ********************************** CREATE HEADERS REQUEST (START) **********************************

        # create http request for getting rows data (for accessing list view classes)
        headers_req = HttpRequest()

        # binding data to headers request
        if payload:
            headers_req.GET = payload['headers_data']

        # create request attribute for http request
        headers_req.REQUEST = payload['headers_data']

        # bind current user with http request
        headers_req.user = user

        # *********************************** CREATE HEADERS REQUEST (END) ***********************************

        # ************************************ CREATE ROWS REQUEST (START) ***********************************

        # create http request for getting rows data (for accessing list view classes)
        rows_req = HttpRequest()

        if 'rows_data' in payload:
            payload['rows_data']['is_download_request'] = 1

        # binding data to rows request
        if payload:
            rows_req.GET = payload['rows_data']

        # create request attribute for http request
        rows_req.REQUEST = payload['rows_data']
        rows_req.REQUEST['iDisplayStart'] = 0
        rows_req.REQUEST['start'] = 0

        # bind current user with http request
        rows_req.user = user

        # ************************************ CREATE ROWS REQUEST (END) ************************************

        # create view class object (for headers data)
        headers_req_obj = eval("{}()".format(payload['headers']))
        headers_req_obj.request = headers_req
        headers_req_obj.object_list = []
        headers_req_obj.kwargs = payload['headers_data']
        headers_data_key = payload['headers_data']['headers_data_key'] \
            if 'headers_data_key' in payload['headers_data'] else 'datatable_headers'

        # get headers
        headers_data = headers_req_obj.get_context_data()

        # fetch headers
        headers_list = ""
        file_headers_list = ""

        action_headers = [
            'action',
            'actions',
            'nms_actions',
            'device_icon',
            'device_gmap_icon'
        ]

        # in case of user logs listing action colum is for changes made by user therefore we have to show it
        if payload['app'] and payload['app'] == 'activity_stream':
            action_headers = list()

        try:
            headers_list = list()
            file_headers_list = list()
            datatable_headers = simplejson.loads(headers_data[headers_data_key])
            excluded_columns = payload['excluded'] if 'excluded' in payload and payload['excluded'] else []
            # Headers which will not displayed in excel sheet
            non_display_headers = action_headers + excluded_columns

            for headers_dict in datatable_headers:
                # @priyesh-teramatrix :- Please verify. Here a condition added by which the 
                #                        action column will be not added to downloaded report.
                if headers_dict['mData'] not in non_display_headers:
                    if 'sClass' in headers_dict:
                        if headers_dict['sClass'] != 'hide':
                            headers_list.append(headers_dict['mData'])
                            file_headers_list.append(headers_dict['sTitle'])
                    # @priyesh-teramatrix :- Please verify. Here 'else' condition added because it is not 
                    #                        necessary that we have 'sClass' key in grid headers.
                    else:
                        headers_list.append(headers_dict['mData'])
                        file_headers_list.append(headers_dict['sTitle'])
        except Exception as e:
            logger.info(e.message)
        
        # create view class object (for rows data)
        rows_req_obj = eval("{}()".format(payload['rows']))
        rows_req_obj.request = rows_req

        # is the request for single sheet or multi
        try:
            is_multi_sheet = int(payload['rows_data'].get('is_multi_sheet', 0))
        except Exception, e:
            is_multi_sheet = 0

        resultset = list()
        titles_list = list()

        if is_multi_sheet:
            data_key = payload['rows_data'].get('data_key')
            data_list = payload['rows_data'].get(data_key)
            change_key = payload['rows_data'].get('change_key')

            if type(data_list) == type(str):
                data_list = json.loads(data_list)

            for item in data_list:
                # create view class object (for rows data)
                rows_req_obj = eval("{}()".format(payload['rows']))
                rows_req_obj.request = rows_req

                payload['rows_data'][change_key] = item['id']
                titles_list.append(item['title'])
                rows_req_obj.kwargs = payload['rows_data']
                rows_req_obj.request.GET = payload['rows_data']

                try:
                    # get datatable data
                    query_set_length = len(rows_req_obj.get_initial_queryset())

                    rows_req.REQUEST['iDisplayLength'] = query_set_length
                    rows_req.REQUEST['length'] = query_set_length

                    if payload['max_rows']:
                        rows_req_obj.max_display_length = int(payload['max_rows'])
                    else:
                        rows_req_obj.max_display_length = query_set_length
                except Exception, e:
                    logger.info(e.message)

                resultset.append(rows_req_obj.get_context_data())

        else:
            rows_req_obj.kwargs = payload['rows_data']

            try:
                # get datatable data
                query_set_length = len(rows_req_obj.get_initial_queryset())

                rows_req.REQUEST['iDisplayLength'] = query_set_length
                rows_req.REQUEST['length'] = query_set_length

                if payload['max_rows']:
                    rows_req_obj.max_display_length = int(payload['max_rows'])
                else:
                    rows_req_obj.max_display_length = query_set_length
            except Exception, e:
                logger.error(e.message)
            titles_list = ['Sheet 1']
            resultset.append(rows_req_obj.get_context_data())

        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()

        counter = 0

        is_created = False

        # excel workbook
        # wb = xlwt.Workbook()
        # file path
        file_name = payload['username'] + '_' + payload['fulltime'] + '.xlsx'
        file_path = 'download_excels/{0}'.format(file_name)
        wb = xlsxwriter.Workbook(MEDIA_ROOT + file_path)

        for result in resultset:

            # error rows list
            rows_list = []

            data_key = 'aaData'
            if 'data' in result and result['data']:
                data_key = 'data'

            # headers for excel sheet
            if data_key in result and result[data_key] and headers_list:
                
                headers = headers_list
                    
                is_created = True
                # create list of lists containing excel rows data (except header)
                for val in result[data_key]:
                    temp_list = list()
                    for key in headers:
                        try:
                            temp_list.append(val[key])
                        except Exception as e:
                            temp_list.append("")
                            logger.info(e.message)
                    rows_list.append(temp_list)

                # excel worksheet
                # ws = wb.add_sheet(titles_list[counter])
                ws = wb.add_worksheet(titles_list[counter])

                # xlwt style object for styling header row
                # style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')
                style = wb.add_format()
                style.set_fg_color('#F9D8AC')
                style.set_pattern(1)

                # writing header row to excel sheet
                try:
                    for i, col in enumerate(file_headers_list):
                        ws.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
                except Exception as e:
                    pass

                # writing rows (except header) in excel sheet
                try:
                    for i, l in enumerate(rows_list):
                        i += 1
                        for j, col in enumerate(l):
                            try:
                                col = nocout_utils.html_to_text(col)
                            except Exception as e:
                                pass

                            try:
                                col = col.strip()
                            except Exception, e:
                                pass

                            ws.write(i, j, col)
                except Exception as e:
                    pass
            counter += 1

        if is_created:
            # if directory for bulk upload excel sheets didn't exist than create one
            if not os.path.exists(MEDIA_ROOT + 'download_excels'):
                os.makedirs(MEDIA_ROOT + 'download_excels')

            # saving bulk upload errors excel sheet
            try:
                # saving workbook
                # wb.save(MEDIA_ROOT + file_path)
                wb.close()
                # update downloader object (on success)
                d_obj.file_path = file_path
                d_obj.file_type = 'MS-Excel'
                d_obj.status = 1
                d_obj.description += "\nSuccessfully downloaded on {}.".format(payload['fulltime'])
                d_obj.request_completion_on = datetime.now()
                d_obj.save()
            except Exception as e:
                # update downloader object
                d_obj.status = 2
                d_obj.request_completion_on = datetime.now()
                d_obj.save()
                logger.info(e.message)
        else:
            # update downloader object (on success)
            d_obj.description += "\nData table has no data."
            d_obj.status = 3
            d_obj.request_completion_on = datetime.now()
            d_obj.save()
    else:
        # update downloader object (on success)
        d_obj.description += "\nWrong parameters."
        d_obj.status = 4
        d_obj.request_completion_on = datetime.now()
        d_obj.save()