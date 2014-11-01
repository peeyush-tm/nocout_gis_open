import json
import os
from django.http import HttpResponseRedirect, HttpResponse
from operator import itemgetter
from django.db.models.query import ValuesQuerySet
from django.shortcuts import render_to_response
from django.template import RequestContext
import logging
from nocout.settings import MEDIA_ROOT, MEDIA_URL
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, TemplateView, View
from django_datatables_view.base_datatable_view import BaseDatatableView
from forms import KmzReportForm
from django.views.generic.edit import CreateView, DeleteView
from device.models import Device, DeviceFrequency, DeviceTechnology
from django.db.models import Q
from inventory.models import ThematicSettings, UserThematicSettings
from performance.models import InventoryStatus, NetworkStatus, ServiceStatus, PerformanceStatus, PerformanceInventory, \
    PerformanceNetwork, PerformanceService, Status
from user_profile.models import UserProfile
from devicevisualization.models import GISPointTool, KMZReport
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse_lazy
import re, ast
from actstream import action
logger=logging.getLogger(__name__)


def locate_devices(request , device_name = "default_device_name"):
    """
    Returns the Context Variable to GIS Map page.
    """
    template_data = { 'username' : request.user.username,
                    'device_name' : device_name,
                    'get_filter_api': get_url(request, 'GET'),
                    'set_filter_api': get_url(request, 'POST')
                    }

    return render_to_response('devicevisualization/locate_devices.html',
                                template_data, 
                                context_instance=RequestContext(request))

def load_google_earth(request, device_name = "default_device_name"):

    """
    Returns the Context Variable for google earth.
    """
    template_data = { 'username' : request.user.username,
                    'device_name' : device_name,
                    'get_filter_api': get_url(request, 'GET'),
                    'set_filter_api': get_url(request, 'POST')
                    }
                    
    return render_to_response('devicevisualization/google_earth_template.html',
                                template_data, 
                                context_instance=RequestContext(request))

def load_earth(request):
    """
    Returns the Context Variable for google earth.
    """
    template_data = {}
                    
    return render_to_response('devicevisualization/locate_devices_earth.html',
                                template_data, 
                                context_instance=RequestContext(request))    
    
def get_url(req, method):
    """
    Return Url w.r.t to the request type.
    """
    url = None
    if method == 'GET':
        url = "/gis/get_filters/"
    elif method == 'POST':
        url = "/gis/set_filters/"

    return url

class Gis_Map_Performance_Data(View):
        """
        The request data will be
        {
        'basestation':{'id':<BS_ID>
                       'sector':{
                                'device_name':<device_name>
                                'substation':{
                                        'device_name':<device_name>
                                    }
                       }


                       }
        }

        """
        @method_decorator(csrf_exempt)
        def dispatch(self, *args, **kwargs):
            return super(Gis_Map_Performance_Data, self).dispatch(*args, **kwargs)


        def post(self, request):
            request_data= self.request.body
            # request_data.replace('\n','')
            if request_data:
                request_data= json.loads(request_data)
                request_data_sectors= request_data['param']['sector']
                for sector in request_data_sectors:
                    sector['performance_data']= self.get_device_performance(sector['device_name'])
                    substations= sector['sub_station']
                    for substation in substations:
                        substation['performance_data']= self.get_device_performance(substation['device_name'])
                #logger.debug(request_data)
                return HttpResponse(json.dumps(request_data))

            return HttpResponse(json.dumps({'result':'No Performance Data'}))

        def tech_info(self, device_technology):
            """

            :param device_technology: technology for the device
            :return: the list of data sources to be checked
            """
            return []

        def get_device_performance(self, device_name):
            device_performance_value = ''
            device_frequency = ''
            device_pl = ''
            device_link_color=None
            freeze_time= self.request.GET.get('freeze_time','0')
            sector_info = {
                    'azimuth_angle': "",
                    'beam_width': "",
                    'radius': "",
                    'frequency':device_frequency
                }
            performance_data= {
                'frequency':device_frequency,
                'pl':device_pl,
                'color':device_link_color,
                'performance_paramter':"",
                'performance_value':device_performance_value,
                'performance_icon': "",
                'device_info' : [
                    {
                        "name": "",
                        "title": "",
                        "show": 0,
                        "value": ""
                     },
                ],
                'sector_info' : sector_info
            }
            try:
                device= Device.objects.get(device_name= device_name, is_added_to_nms=1, is_deleted=0)

                device_technology = DeviceTechnology.objects.get(id=device.device_technology)
                user_obj = UserProfile.objects.get(id= self.request.user.id)

                uts = UserThematicSettings.objects.get(user_profile=user_obj,
                                                       thematic_technology=device_technology)

                thematic_settings= uts.thematic_template
                threshold_template=thematic_settings.threshold_template
                live_polling_template= threshold_template.live_polling_template

                device_service_name= live_polling_template.service.name
                device_service_data_source= live_polling_template.data_source.name
                device_machine_name= device.machine.name
                try:
                    if int(freeze_time):
                        device_frequency= PerformanceInventory.objects.filter(device_name= device_name,
                                                                             data_source= 'frequency',
                                                                             sys_timestamp__lte= int(freeze_time)/1000).\
                                                                             using(alias= device_machine_name).\
                                                                             order_by('-sys_timestamp')[:1]
                        if len(device_frequency):
                            device_frequency = device_frequency[0].current_value
                        else:
                            device_frequency = ''

                    else:
                        device_frequency= InventoryStatus.objects.filter(device_name= device_name,
                                                                         data_source= 'frequency').\
                                                                         using(alias= device_machine_name)\
                                                                        .order_by('-sys_timestamp')[:1]
                        if len(device_frequency):
                            device_frequency = device_frequency[0].current_value
                        else:
                            device_frequency = ''
                    performance_data.update({
                    'frequency':device_frequency
                    })
                except Exception as e:
                    logger.info(device)
                    logger.info(e.message)
                    device_frequency=''
                    pass

                try:
                    if int(freeze_time):
                        device_pl= PerformanceNetwork.objects.filter(device_name= device_name,
                                                                     service_name= 'ping',
                                                                     data_source= 'pl',
                                                                     sys_timestamp__lte= int(freeze_time)/1000).\
                                                                     using(alias= device_machine_name).\
                                                                     order_by('-sys_timestamp')[:1]
                        if len(device_pl):
                            device_pl = device_pl[0].current_value
                        else:
                            device_pl = ''
                    else:
                        device_pl= NetworkStatus.objects.filter(device_name= device_name,
                                                                service_name= 'ping',
                                                                data_source= 'pl').\
                                                                using(alias= device_machine_name).\
                                                                order_by('-sys_timestamp')[:1]
                        if len(device_pl):
                            device_pl = device_pl[0].current_value
                        else:
                            device_pl = ''

                except Exception as e:
                    logger.info(device)
                    logger.info(e.message)
                    device_pl=''
                    pass

                try:
                    if len(device_frequency):
                        corrected_dev_freq = device_frequency

                        try:
                            chek_dev_freq = ast.literal_eval(device_frequency)
                            if int(chek_dev_freq) > 10:
                                corrected_dev_freq = chek_dev_freq
                        except Exception as e:
                            logger.info(device)
                            logger.exception("Frequency is Empty : %s" %(e.message))

                        device_frequency_objects = DeviceFrequency.objects.filter(value__icontains=str(corrected_dev_freq))
                        device_frequency_color= DeviceFrequency.objects.filter(value__icontains=str(corrected_dev_freq)).\
                                                                               values_list('color_hex_value', flat=True)

                        device_frequency_object = None
                        if len(device_frequency_objects):
                            device_frequency_object = device_frequency_objects[0]

                        if len(device_frequency_color):
                            device_link_color= device_frequency_color[0]

                        if device.sector_configured_on.exists():
                            ##device is sector device
                            device_sector_objects = device.sector_configured_on.filter()
                            if len(device_sector_objects):
                                sector = device_sector_objects[0]
                                antenna = sector.antenna
                                azimuth_angle = sector.antenna.azimuth_angle if antenna else 'N/A'
                                beam_width = sector.antenna.beam_width if antenna else 'N/A'
                                radius = device_frequency_object.frequency_radius if (
                                    device_frequency_object
                                    and
                                    device_frequency_object.frequency_radius
                                ) else 0
                                performance_data.update({
                                    'azimuth_angle': azimuth_angle,
                                    'beam_width': beam_width,
                                    'radius': radius,
                                    'frequency':device_frequency
                                })


                    if len(device_pl) and int(ast.literal_eval(device_pl))==100:
                        device_link_color='rgb(0,0,0)'

                except Exception as e:

                    if len(device_pl) and int(ast.literal_eval(device_pl))==100:
                        device_link_color='rgb(0,0,0)'

                    else:
                        device_link_color=''
                    logger.info(device)
                    logger.info(e.message)
                    pass

                try:
                    device_performance_value=''
                    if int(freeze_time):
                        device_performance_value= PerformanceService.objects.filter(device_name= device_name,
                                                                               service_name= device_service_name,
                                                                               data_source= device_service_data_source,
                                                                               sys_timestamp__lte= int(freeze_time)/1000).\
                                                                               using(alias=device_machine_name).\
                                                                               order_by('-sys_timestamp')[:1]
                        if len(device_performance_value):
                            device_performance_value = device_performance_value[0].current_value
                        else:
                            device_performance_value = ''
                    else:

                        device_performance_value= ServiceStatus.objects.filter(device_name= device_name,
                                                                               service_name= device_service_name,
                                                                               data_source= device_service_data_source)\
                                                                               .using(alias=device_machine_name)\
                                                                               .order_by('-sys_timestamp')[:1]
                        if len(device_performance_value):
                            device_performance_value = device_performance_value[0].current_value
                        else:
                            device_performance_value = ''

                except Exception as e:
                    device_performance_value=''
                    logger.info(device)
                    logger.info(e.message)
                    pass

                performance_icon=''
                if len(str(device_performance_value)):
                    corrected_device_performance_value = ast.literal_eval(str(device_performance_value))
                    icon_settings_json_string= thematic_settings.icon_settings if thematic_settings.icon_settings!='NULL' else None
                    if icon_settings_json_string:
                        icon_settings_json= eval(icon_settings_json_string)
                        range_start, range_end= None, None
                        for data in icon_settings_json:
                            try:
                                range_number=''.join(re.findall("[0-9]", data.keys()[0]))
                                exec 'range_start=threshold_template.range'+str(range_number)+ '_start'
                                exec 'range_end=threshold_template.range'+str(range_number)+ '_end'
                                ##known bug: the complete range should be checked and not just the values
                                ##between two ranges for example : range 1 = 0,2
                                ##range 2 = 3,5
                                ## value should be checked if it in in range 1
                                ## value should be checked if between range 2 (that is 3,5)
                                if (float(range_start)) <= float(corrected_device_performance_value) <= (float(range_end)):
                                    performance_icon= data.values()[0]
                            except Exception as e:
                                logger.info(device)
                                logger.exception(e.message)
                                continue

                device_info = []
                try:
                    #to update the info window with all the services
                    device_performance_info = ServiceStatus.objects.filter(device_name=device_name).values(
                        'data_source','current_value','sys_timestamp'
                    ).using(alias=device_machine_name)

                    device_inventory_info = InventoryStatus.objects.filter(device_name=device_name).values(
                        'data_source','current_value','sys_timestamp'
                    ).using(alias=device_machine_name)

                    device_status_info = Status.objects.filter(device_name=device_name).values(
                        'data_source','current_value','sys_timestamp'
                    ).using(alias=device_machine_name)

                    device_network_info = NetworkStatus.objects.filter(device_name=device_name).values(
                        'data_source','current_value','sys_timestamp'
                    ).using(alias=device_machine_name)

                    for perf in device_performance_info:
                        perf_info = {
                                "name": perf['data_source'],
                                "title": " ".join(perf['data_source'].split("_")).title(),
                                "show": 1,
                                "value": perf['current_value'],
                            }
                        device_info.append(perf_info)

                    for perf in device_inventory_info:
                        perf_info = {
                                "name": perf['data_source'],
                                "title": " ".join(perf['data_source'].split("_")).title(),
                                "show": 1,
                                "value": perf['current_value'],
                            }
                        device_info.append(perf_info)

                    for perf in device_status_info:
                        perf_info = {
                                "name": perf['data_source'],
                                "title": " ".join(perf['data_source'].split("_")).title(),
                                "show": 1,
                                "value": perf['current_value'],
                            }

                        device_info.append(perf_info)

                    for perf in device_network_info:
                        perf_info = {
                                "name": perf['data_source'],
                                "title": "Latency" if ("rta" in perf['data_source'].lower()) else "Packet Loss",
                                "show": 1,
                                "value": perf['current_value'],
                            }

                        device_info.append(perf_info)

                except Exception as e:
                    logger.info(device)
                    logger.exception(e.message)
                    pass

                performance_data.update({
                    'frequency':device_frequency,
                    'pl':device_pl,
                    'color':device_link_color,
                    'performance_paramter':device_service_name,
                    'performance_value':device_performance_value,
                    'performance_icon':"media/"+str(performance_icon)
                                        if "uploaded" in str(performance_icon)
                                        else ("static/img/" + str(performance_icon) if len(str(performance_icon)) else ""),
                    'device_info' : device_info,
                    'sector_info' : sector_info
                })
                #logger.info(performance_data)
            except Exception as e:
                logger.info(e.message, exc_info=True)
                pass
            return performance_data

" This class is used to add, update or delete point tool data"
class PointToolClass(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PointToolClass, self).dispatch(*args, **kwargs)

    def post(self, request):
        result = {
            "success": 0,
            "message": "Point can not be saved. Please Try Again.",
            "data": {
                "point_id":0,
            }
        }
        point_data= self.request.body
        if point_data:
            point_data = json.loads(point_data)
            # point_data = json_loads(point_data)
            if(int(point_data["is_delete_req"]) > 0) :
                GISPointTool.objects.filter(pk=point_data['point_id']).delete()
                result["data"]["point_id"] = 0
                result["success"] = 1
                result["message"] = "Point Removed Successfully"

            elif(int(point_data["is_update_req"]) > 0) :

                current_row = GISPointTool.objects.get(pk=point_data['point_id'])
                current_row.name = point_data['name']
                current_row.description = point_data['desc']
                current_row.connected_lat = point_data['connected_lat']
                current_row.connected_lon = point_data['connected_lon']
                current_row.connected_point_type=point_data['connected_point_type']
                current_row.connected_point_info=point_data['connected_point_info']
                # update row with new values
                current_row.save()


                result["data"]["point_id"] = point_data['point_id']
                result["success"] = 1
                result["message"] = "Point Updated Successfully"

            else:
                try:
                    # check that the name already exist in db or not
                    existing_rows_count = len(GISPointTool.objects.filter(name=point_data['name']))

                    if(existing_rows_count == 0):
                        new_row_obj = GISPointTool(
                            name=point_data['name'],
                            description=point_data['desc'],
                            latitude=float(point_data['lat']),
                            longitude=float(point_data['lon']),
                            icon_url=point_data['icon_url'],
                            connected_lat=0,
                            connected_lon=0,
                            connected_point_type='',
                            connected_point_info='',
                            user_id=self.request.user.id
                        )
                        new_row_obj.save()
                        inserted_id = new_row_obj.id
                        result["data"]["point_id"] = inserted_id
                        result["success"] = 1
                        result["message"] = "Point Saved Successfully"
                    else:
                        result["message"] = "Name already exist. Please enter another"

                except Exception as e:
                    print "---------------------Exception---------------------"
                    logger.info(e.message)
            return HttpResponse(json.dumps(result))
        return HttpResponse(json.dumps(result))

" This class retruns gmap tools(point,line,etc.) data"
class GetToolsData(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(GetToolsData, self).dispatch(*args, **kwargs)

    def get(self, request):

        # initialize exchange format
        result = {
            "success": 0,
            "message": "Data not fetched",
            "data": {
                "points": [],
                "ruler": []
            }
        }
        try:
            # list of columns to be fetched
            required_columns = [
                'id',
                'name',
                'description',
                'icon_url',
                'latitude',
                'longitude',
                'connected_lat',
                'connected_lon',
                'connected_point_type',
                'connected_point_info'
            ]

            # Fetch all the points info associated with logged in user
            point_data_obj = GISPointTool.objects.filter(user_id=request.user.id).values(*required_columns)

            # Loop fetched result & append it to points list
            for point_data in point_data_obj :
                data_object = {
                    "point_id" : "",
                    "lat" : "",
                    "lon" : "",
                    "name" : "",
                    "icon_url" : "",
                    "desc" : "",
                    "connected_lat" : "",
                    "connected_lon" : "",
                    "connected_point_type" : "",
                    "connected_point_info" : ""
                }
                data_object['point_id'] = point_data['id']
                data_object['lat'] = point_data['latitude']
                data_object['lon'] = point_data['longitude']
                data_object['name'] = point_data['name']
                data_object['icon_url'] = point_data['icon_url']
                data_object['desc'] = point_data['description']
                data_object['connected_lat'] = point_data['connected_lat']
                data_object['connected_lon'] = point_data['connected_lon']
                data_object['connected_point_type'] = point_data['connected_point_type']
                data_object['connected_point_info'] = point_data['connected_point_info']
                
                #Append data to point list
                result["data"]["points"].append(data_object)

            result["success"] = 1
            result["message"] = "Tools Data Fetched Successfully"
        except Exception as e:
            print "-------------Exception-------------"
            print logger.info(e.message)
            result["success"] = 0
            result["data"]["points"] = []
            result["data"]["ruler"] = []
            result["message"] = "Data not Fetched."

        return HttpResponse(json.dumps(result))


##************************************* KMZ Report****************************************##

class KmzListing(ListView):
   
    model = KMZReport
    template_name = 'devicevisualization/kmz.html'

    def get_context_data(self, **kwargs):
        
        context = super(KmzListing, self).get_context_data(**kwargs)
        table_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'filename', 'sTitle': 'KMZ', 'sWidth': 'auto', },
            {'mData': 'added_on', 'sTitle': 'Uploaded On', 'sWidth': 'auto'},
            {'mData': 'user', 'sTitle': 'Uploaded By', 'sWidth': 'auto'},
        ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            table_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})

        context['table_headers'] = json.dumps(table_headers)
        return context


class Kmzreport_listingtable(BaseDatatableView):
   
    model = KMZReport
    columns = ['name', 'filename', 'added_on', 'user']
    order_columns = ['name', 'filename', 'added_on', 'user']

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value """

        sSearch = self.request.GET.get('sSearch', None)

        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                # avoid search on 'added_on'
                if column == 'added_on':
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
        
        # condition to fetch KMZ Report data from database
        condition = (Q(user=self.request.user) | Q(is_public=1)) 
        # Query to fetch L2 reports data from db
        kmzreportresult = KMZReport.objects.filter(condition).values(*self.columns + ['id'])
       
        report_resultset = []
        for data in kmzreportresult:
            report_object = {}
            report_object['name'] = data['name'].title()
            filename_str_array = data['filename'].split('/')
            report_object['filename'] = filename_str_array[len(filename_str_array)-1]
            report_object['added_on'] = data['added_on']
            username = UserProfile.objects.filter(id=data['user']).values('username')
            report_object['user'] = username[0]['username'].title()
            report_object['id'] = data['id']
            #add data to report_resultset list
            report_resultset.append(report_object)
        return report_resultset

    def prepare_results(self, qs):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a style="cursor:pointer;" url="{0}" class="delete_kmzreport" title="Delete kmz" >\
                <i class="fa fa-trash-o text-danger"></i></a>\
                <a href="view/gmap/{0}/" title="view on google map">\
                <i class="fa fa-globe"></i></a>\
                <a href="view/google_earth/{0}" title="view on google earth">\
                <i class="fa fa-globe"></i></a>\
                <a href="view/white_background/{0}" title="view on white background">\
                <i class="fa fa-globe"></i></a>\
                '.format(dct.pop('id')),
               added_on=dct['added_on'].strftime("%Y-%m-%d") if dct['added_on'] != "" else "")

        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        request = self.request
        # Number of columns that are used in sorting
        try:
            i_sorting_cols = int(request.REQUEST.get('iSortingCols', 0))
        except Exception:
            i_sorting_cols = 0

        order = []
        order_columns = self.get_order_columns()
        for i in range(i_sorting_cols):
            # sorting column
            try:
                i_sort_col = int(request.REQUEST.get('iSortCol_%s' % i))
            except Exception:
                i_sort_col = 0
            # sorting order
            s_sort_dir = request.REQUEST.get('sSortDir_%s' % i)

            sdir = '-' if s_sort_dir == 'desc' else ''

            sortcol = order_columns[i_sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            key_name=order[0][1:] if '-' in order[0] else order[0]
            sorted_device_data = sorted(qs, key=itemgetter(key_name), reverse= True if '-' in order[0] else False)
            return sorted_device_data
        return qs


    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request
        self.initialize(*args, **kwargs)

        
        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)
        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret



class KmzDelete(DeleteView):

    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(KmzDelete, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        report_id = self.kwargs['kmz_id']
        filename = lambda x: MEDIA_ROOT + x
        # KMZ report object
        kmz_obj = KMZReport.objects.filter(id=report_id).values()
        # remove original file if it exists
        try:
            os.remove(filename(kmz_obj[0]['filename']))
            print "*********************************"

        except Exception as e:
            print "***********************************"
            print e.message
            logger.info(e.message)
        # delete entry from database
        KMZReport.objects.filter(id=report_id).delete()
        return HttpResponseRedirect(reverse_lazy('kmz_list'))

# class for view kmz file on google map , google earth , white background 

class KmzViewAction(View):
    
    template = ''
    
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(KmzViewAction, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context_data = {}
        page_type = self.kwargs['page_type']
        kmz_id = self.kwargs['kmz_id']

        file_url = KMZReport.objects.filter(pk=kmz_id).values('filename')
        context_data['file_url'] = file_url[0]['filename']

        if page_type == 'white_background':
            template = 'devicevisualization/kmz_whitebg.html'
        elif page_type == 'google_earth':
            template = 'devicevisualization/kmz_earth.html'
        else:
            template = 'devicevisualization/kmz_gmap.html'
        
        return render_to_response(template,
                context_data, 
                context_instance=RequestContext(request))

##************************************ Create KMZ File class **************************************##
class KmzCreate(CreateView):

    template_name = 'devicevisualization/kmzuploadnew.html'
    model = KMZReport
    form_class = KmzReportForm 

    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(KmzCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save(commit=False)
        self.object.user =  UserProfile.objects.get(id=self.request.user.id)
        
        self.object.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(reverse_lazy('kmz_list'))
