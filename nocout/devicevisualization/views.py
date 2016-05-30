import json
import os, datetime
from django.http import HttpResponseRedirect, HttpResponse
from operator import itemgetter
from django.db.models.query import ValuesQuerySet
from django.shortcuts import render_to_response
from django.template import RequestContext
import logging
from zipfile import ZipFile
import glob
from nocout.settings import MEDIA_ROOT, MEDIA_URL, LIVE_POLLING_CONFIGURATION, PERIODIC_POLL_PROCESS_COUNT, DATE_TIME_FORMAT
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, TemplateView, View
from django_datatables_view.base_datatable_view import BaseDatatableView
from forms import KmzReportForm
from django.views.generic.edit import CreateView, DeleteView
from device.models import Device, DeviceFrequency, DeviceTechnology, DeviceType
from django.db.models import Q
from inventory.models import ThematicSettings, UserThematicSettings, BaseStation, SubStation, UserPingThematicSettings, \
    PingThematicSettings, Circuit, CircuitL2Report, Sector, BaseStationPpsMapper
from performance.models import InventoryStatus, NetworkStatus, ServiceStatus, PerformanceStatus, PerformanceInventory, \
    PerformanceNetwork, PerformanceService, Status, Topology, Utilization, UtilizationStatus
# from performance.views import device_last_down_time
from user_profile.models import UserProfile
from devicevisualization.models import GISPointTool, KMZReport
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse_lazy, reverse
import re, ast
from activity_stream.models import UserAction
from device.api import prepare_raw_result
from sitesearch.views import prepare_raw_bs_result
# Import performance formulae methods
from performance.formulae import rta_null, display_time
# Import service utils gateway class
from service.utils.util import ServiceUtilsGateway
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway, getBSInventoryInfo, getSSInventoryInfo, getSectorInventoryInfo
# Import inventory utils gateway class
from inventory.utils.util import InventoryUtilsGateway
# Import advance filtering mixin for BaseDatatableView
from nocout.mixins.datatable import AdvanceFilteringMixin
from user_profile.utils.auth import in_group
from device.api import prepare_raw_result_v2
from nocout.settings import EXCLAMATION_NEEDED

logger = logging.getLogger(__name__)

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()

# Global Variables for infowindow keys
BS_INFOWINDOW_LIST = [
    'name', 'base_station_alias', 'bs_site_name', 'bs_site_id',
    'building_height', 'tower_height', 'bs_type', 'bs_gps_type',
    'bs_address', 'bs_city', 'bs_state', 'lat_lon',
    'bs_infra_provider', 'tag1', 'tag2'
]

BH_INFOWINDOW_LIST = [
    'bh_capacity', 'bh_connectivity', 'bh_type', 'bh_circuit_id',
    'bh_ttsl_circuit_id', 'bh_pe_hostname', 'pe_ip', 'bs_switch_ip',
    'aggregation_switch', 'aggregation_switch_port', 'bs_converter_ip', 'pop',
    'bh_device_type', 'bh_configured_on', 'bh_device_port'
]

SS_INFOWINDOW_LIST = [
    'cktid', 'customer_alias', 'ss_ip', 'pe_ip',
    'qos_bandwidth', 'antenna_height', 'polarisation',
    'mount_type', 'antenna_type', 'cable_length', 'ethernet_extender',
    'building_height', 'tower_height', 'ss_technology', 'lat_lon',
    'customer_address', 'alias', 'dl_rssi_during_acceptance', 'date_of_acceptance'
]


def init_network_maps(request, device_name="default_device_name", page_type="gmap"):
    """
    This function initializes gmap or gearth or wmap as per page type
    """
    is_admin = 'other'
    template_path = 'devicevisualization/locate_devices.html'

    # Update template_path as per the page type
    if page_type == "setellite":
        template_path = 'devicevisualization/google_earth_template.html'
    elif page_type == "gearth":
        template_path = 'devicevisualization/locate_devices_earth.html'
    elif page_type == "wmap":
        template_path = 'devicevisualization/locate_devices_white_map.html'

    if in_group(request.user, 'admin'):
        is_admin = 'admin'

    context_data = {
        'username': request.user.username,
        'device_name': device_name,
        'is_admin': is_admin,
        'live_poll_config': json.dumps(LIVE_POLLING_CONFIGURATION),
        'periodic_poll_process_count': PERIODIC_POLL_PROCESS_COUNT,
        'page_type': page_type
    }

    return render_to_response(
        template_path, 
        context_data, 
        context_instance=RequestContext(request)
    )


class Gis_Map_Performance_Data(View):
        """
        The request data will be
        {
            'basestation': {
                'id':<BS_ID>
                'sector':{
                    'device_name':<device_name>
                    'substation': {
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
            request_data = self.request.body
            # request_data.replace('\n','')
            if request_data:
                request_data = json.loads(request_data)
                request_data_sectors = request_data['param']['sector']
                for sector in request_data_sectors:
                    sector['performance_data'] = self.get_device_performance(sector['device_name'])
                    substations = sector['sub_station']
                    for substation in substations:
                        substation['performance_data'] = self.get_device_performance(substation['device_name'])
                return HttpResponse(json.dumps(request_data))

            return HttpResponse(json.dumps({'result': 'No Performance Data'}))

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
            device_link_color = None
            freeze_time = self.request.GET.get('freeze_time', '0')
            sector_info = {
                'azimuth_angle': "",
                'beam_width': "",
                'radius': "",
                'frequency': device_frequency
            }
            performance_data = {
                'frequency': device_frequency,
                'pl': device_pl,
                'color': device_link_color,
                'performance_paramter': "",
                'performance_value': device_performance_value,
                'performance_icon': "",
                'device_info': [
                    {
                        "name": "",
                        "title": "",
                        "show": 0,
                        "value": ""
                    },
                ],
                'sector_info': sector_info
            }
            try:
                device = Device.objects.get(
                    device_name=device_name,
                    is_added_to_nms__gt=0,
                    is_deleted=0
                )

                device_technology = DeviceTechnology.objects.get(id=device.device_technology)
                device_type = DeviceType.objects.get(id=device.device_type)
                user_obj = UserProfile.objects.get(id=self.request.user.id)

                uts = UserThematicSettings.objects.get(user_profile=user_obj,
                                                       thematic_technology=device_technology,
                                                       thematic_type =device_type)

                thematic_settings = uts.thematic_template
                threshold_template = thematic_settings.threshold_template
                live_polling_template = threshold_template.live_polling_template

                device_service_name = live_polling_template.service.name
                device_service_data_source = live_polling_template.data_source.name
                device_machine_name = device.machine.name
                try:
                    if int(freeze_time):
                        device_frequency= PerformanceInventory.objects.filter(device_name=device_name,
                                                                              data_source='frequency',
                                                                              sys_timestamp__lte=int(freeze_time)/1000).\
                                                                              using(alias=device_machine_name).\
                                                                              order_by('-sys_timestamp')[:1]
                        if len(device_frequency):
                            device_frequency = device_frequency[0].current_value
                        else:
                            device_frequency = ''

                    else:
                        device_frequency= InventoryStatus.objects.filter(device_name=device_name,
                                                                         data_source='frequency').\
                                                                         using(alias=device_machine_name)\
                                                                        [:1]
                        if len(device_frequency):
                            device_frequency = device_frequency[0].current_value
                        else:
                            device_frequency = ''
                    performance_data.update({
                    'frequency':device_frequency
                    })
                except Exception as e:
                    logger.info(e.message)
                    device_frequency=''
                    pass

                try:
                    if int(freeze_time):
                        device_pl= PerformanceNetwork.objects.filter(device_name=device_name,
                                                                     service_name='ping',
                                                                     data_source='pl',
                                                                     sys_timestamp__lte=int(freeze_time)/1000).\
                                                                     using(alias=device_machine_name).\
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
                            pass

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
                    logger.info(e.message)
                    pass

                try:
                    device_performance_value=''
                    if int(freeze_time):
                        device_performance_value= PerformanceService.objects.filter(device_name= device_name,
                                                                               service_name= device_service_name,
                                                                               data_source= device_service_data_source,
                                                                               sys_timestamp__lte= int(freeze_time)/1000).\
                                                                               using(alias=device_machine_name)\
                                                                               [:1]
                        if len(device_performance_value):
                            device_performance_value = device_performance_value[0].current_value
                        else:
                            device_performance_value = ''
                    else:

                        device_performance_value= ServiceStatus.objects.filter(device_name= device_name,
                                                                               service_name= device_service_name,
                                                                               data_source= device_service_data_source)\
                                                                               .using(alias=device_machine_name)\
                                                                               [:1]
                        if len(device_performance_value):
                            device_performance_value = device_performance_value[0].current_value
                        else:
                            device_performance_value = ''

                except Exception as e:
                    device_performance_value=''
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
            except Exception as e:
                logger.info(e.message, exc_info=True)
                pass
            return performance_data


class PointToolClass(View):
    """
    This class is used to add, update or delete point tool data
    """
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
            if(int(point_data.get("is_delete_req", 0)) > 0) :
                GISPointTool.objects.filter(pk=point_data.get('point_id')).delete()
                result["data"]["point_id"] = 0
                result["success"] = 1
                result["message"] = "Point Removed Successfully"

            elif(int(point_data.get("is_update_req", 0)) > 0) :

                current_row = GISPointTool.objects.get(pk=point_data.get('point_id'))
                current_row.name = point_data.get('name')
                current_row.description = point_data.get('desc')
                current_row.connected_lat = point_data.get('connected_lat')
                current_row.connected_lon = point_data.get('connected_lon')
                current_row.connected_point_type=point_data.get('connected_point_type')
                current_row.connected_point_info=point_data.get('connected_point_info')
                # update row with new values
                current_row.save()

                result["data"]["point_id"] = point_data.get('point_id')
                result["success"] = 1
                result["message"] = "Point Updated Successfully"

            else:
                try:
                    # check that the name already exist in db or not
                    existing_rows_count = len(GISPointTool.objects.filter(name=point_data.get('name')))

                    if(existing_rows_count == 0):
                        new_row_obj = GISPointTool(
                            name=point_data.get('name'),
                            description=point_data.get('desc'),
                            latitude=float(point_data.get('lat')),
                            longitude=float(point_data.get('lon')),
                            icon_url=point_data.get('icon_url'),
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
            point_data_obj = GISPointTool.objects.filter(
                user_id=request.user.id
            ).values(*required_columns).order_by('connected_lat')

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
                data_object['point_id'] = point_data.get('id')
                data_object['lat'] = point_data.get('latitude')
                data_object['lon'] = point_data.get('longitude')
                data_object['name'] = point_data.get('name')
                data_object['icon_url'] = point_data.get('icon_url')
                data_object['desc'] = point_data.get('description')
                data_object['connected_lat'] = point_data.get('connected_lat')
                data_object['connected_lon'] = point_data.get('connected_lon')
                data_object['connected_point_type'] = point_data.get('connected_point_type')
                data_object['connected_point_info'] = point_data.get('connected_point_info')

                # Append data to point list
                result["data"]["points"].append(data_object)

            result["success"] = 1
            result["message"] = "Tools Data Fetched Successfully"
        except Exception as e:
            logger.info(e.message)
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
        if in_group(self.request.user, 'admin') or in_group(self.request.user, 'operator'):
            table_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})

        context['table_headers'] = json.dumps(table_headers)
        return context


class Kmzreport_listingtable(BaseDatatableView, AdvanceFilteringMixin):

    model = KMZReport
    columns = ['name', 'filename', 'added_on', 'user']
    order_columns = ['name', 'filename', 'added_on', 'user']

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value """

        # sSearch = self.request.GET.get('sSearch', None)
        sSearch = self.request.GET.get('search[value]', None)

        if sSearch:
            query = []
            exec_query = "qs = qs.filter("
            for column in self.columns[:-1]:
                # avoid search on 'added_on'
                if column == 'added_on':
                    continue
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query
        return self.advance_filter_queryset(qs)

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

        return kmzreportresult

    def prepare_results(self, qs):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        report_resultset = list()
        for dct in json_data:
            report_object = {}
            report_object['name'] = dct['name'].title()
            filename_str_array = dct['filename'].split('/')
            report_object['filename'] = filename_str_array[len(filename_str_array)-1]
            report_object['added_on'] = dct['added_on']
            username = UserProfile.objects.filter(id=dct['user']).values('username')
            report_object['user'] = username[0]['username'].title()
            report_object['id'] = dct['id']
            report_object['actions'] = '<a style="cursor:pointer;" url="{0}" class="delete_kmzreport" title="Delete kmz" >\
                                        <i class="fa fa-trash-o text-danger"></i></a>\
                                        <a href="{0}/gmap/view/" title="view on google map">\
                                        <i class="fa fa-globe"></i></a>\
                                        <a href="{0}/google_earth/view/" title="view on google earth">\
                                        <i class="fa fa-globe"></i></a>\
                                        <a href="{0}/white_background/view/" title="view on white background">\
                                        <i class="fa fa-globe"></i></a>\
                                        '.format(dct.pop('id'))
            report_object['added_on'] = dct['added_on'].strftime("%Y-%m-%d") if dct['added_on'] != "" else ""
            #add dct to report_resultset list
            report_resultset.append(report_object)

        return report_resultset

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
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


class KmzDelete(DeleteView):

    def get(self, request, *args, **kwargs):
        report_id = self.kwargs['kmz_id']
        filename = lambda x: MEDIA_ROOT + x
        # KMZ report object
        kmz_obj = KMZReport.objects.filter(id=report_id).values()
        # remove original file if it exists
        try:
            os.remove(filename(kmz_obj[0]['filename']))
            UserAction.objects.create(user_id=self.request.user.id, module='Kmz Report',
                        action='A kmz report is deleted - {}'.format(kmz_obj[0]['name']))

        except Exception as e:
            logger.info(e.message)
        # delete entry from database
        KMZReport.objects.filter(id=report_id).delete()
        return HttpResponseRedirect(reverse_lazy('kmz_list'))

# class for view kmz file on google map , google earth , white background

class KmzViewAction(View):

    template = ''

    def get(self, request, *args, **kwargs):
        context_data = {}
        page_type = self.kwargs['page_type']
        kmz_id = self.kwargs['kmz_id']

        kmz_resultset = KMZReport.objects.filter(pk=kmz_id).values()
        context_data['file_url'] = kmz_resultset[0]['filename']
        context_data['kmz_id'] = kmz_id

        # If page_type is other than google earth & file type is kmz then extract kmz file & pass kml file url
        if page_type != 'google_earth':
            if context_data['file_url'].find(".kmz") > -1 :
                try:
                    kmz_file = ZipFile(str(MEDIA_ROOT+"/"+context_data['file_url']))
                    kml_file_instance = kmz_file.extractall(str(MEDIA_ROOT+"uploaded/kml/"+kmz_resultset[0]['name']+"/"))
                    kml_file = glob.glob(str(MEDIA_ROOT+"uploaded/kml/"+kmz_resultset[0]['name']+"/*.kml"))[0]
                    context_data['file_url'] = "uploaded/kml/"+kmz_resultset[0]['name']+"/"+kml_file[kml_file.rfind("/") + 1:len(kml_file)]
                except Exception, e:
                    logger.info(e.message)

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

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save(commit=False)
        self.object.user =  UserProfile.objects.get(id=self.request.user.id)

        self.object.save()
        return HttpResponseRedirect(reverse_lazy('kmz_list'))


##################################### Points Listing #################################
class PointListingInit(ListView):

    model = GISPointTool
    template_name = 'devicevisualization/points_listing.html'

    def get_context_data(self, **kwargs):

        context = super(PointListingInit, self).get_context_data(**kwargs)
        table_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto', },
            {'mData': 'icon_url', 'sTitle': 'Icon', 'sWidth': 'auto', },
            {'mData': 'latitude', 'sTitle': 'Lattitude', 'sWidth': 'auto'},
            {'mData': 'longitude', 'sTitle': 'Longitude', 'sWidth': 'auto'},
            {'mData': 'connected_lat', 'sTitle': 'Connected Lattitude', 'sWidth': 'auto'},
            {'mData': 'connected_lon', 'sTitle': 'Connected Longitude', 'sWidth': 'auto'}
        ]

        context['table_headers'] = json.dumps(table_headers)
        return context


class PointListingTable(BaseDatatableView, AdvanceFilteringMixin):

    model = GISPointTool
    columns = ['name', 'description', 'icon_url', 'latitude', 'longitude', 'connected_lat', 'connected_lon']
    order_columns = columns

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value """

        # sSearch = self.request.GET.get('sSearch', None)
        sSearch = self.request.GET.get('search[value]', None)

        if sSearch:
            query = []
            exec_query = "qs = qs.filter("
            for column in self.columns[:-1]:
                # avoid search on 'added_on'
                if column == 'added_on':
                    continue
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query
        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        # Query to fetch L2 reports data from db
        pointsresult = GISPointTool.objects.filter(user_id=self.request.user.id).values(*self.columns + ['id'])
        
        return pointsresult

    def prepare_results(self, qs):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

            resultset = []
            for data in qs:
                report_object = {}
                report_object['name'] = data['name'].title()
                report_object['description'] = data['description'].title()
                report_object['icon_url'] = "<img src='"+data['icon_url']+"' width='25px' height='30px'/>"
                report_object['latitude'] = data['latitude']
                report_object['longitude'] = data['longitude']
                report_object['connected_lat'] = data['connected_lat']
                report_object['connected_lon'] = data['connected_lon']
                report_object['id'] = data['id']
                #add data to resultset list
                resultset.append(report_object)

            return resultset

        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        order_columns = self.order_columns
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
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


class GISPerfData(View):
    """ GIS Inventory performance data

        Parameters:
            - base_stations (unicode) - list of base stations in form of unicode i.e. [1, 2, 3, 4]
            - ts (unicode) - thematic service type i.e. ping/normal
            - freeze_time (unicode) - freeze time for e.g. 0

        URL:
            - "/network_maps/perf_data/?base_stations=[47]&ts=normal&freeze_time=0"

        Returns:
            - performance_data (dictionary) - dictionary containing perf data
                        [
                            {
                                "bs_name": "jaisalmar_jai_raj",
                                "bhSeverity": "NA",
                                "param": {
                                    "sector": [
                                        {
                                            "perf_info": [
                                                {
                                                    "title": "Uas",
                                                    "name": "uas",
                                                    "value": "0",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "Management Port On Odu",
                                                    "name": "Management_Port_on_Odu",
                                                    "value": "0.0063",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "Radio Interface",
                                                    "name": "Radio_Interface",
                                                    "value": "0.0000",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "Uptime",
                                                    "name": "uptime",
                                                    "value": "30127212",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "Service Throughput",
                                                    "name": "service_throughput",
                                                    "value": "1.61",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "Rssi",
                                                    "name": "rssi",
                                                    "value": "-61",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "Site Sync State",
                                                    "name": "site_sync_state",
                                                    "value": "independentUnit",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "2",
                                                    "name": "2",
                                                    "value": "Auto",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "3",
                                                    "name": "3",
                                                    "value": "Auto",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "1",
                                                    "name": "1",
                                                    "value": "forcefullDuplex100Mb",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "4",
                                                    "name": "4",
                                                    "value": "unknown_port_ode",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "Latency",
                                                    "name": "rta",
                                                    "value": "45.133",
                                                    "show": 1
                                                },
                                                {
                                                    "title": "Packet Loss",
                                                    "name": "pl",
                                                    "value": "0",
                                                    "show": 1
                                                }
                                            ],
                                            "sector_id": 59,
                                            "color": "",
                                            "polled_frequency": "",
                                            "radius": "",
                                            "perf_value": "-61",
                                            "ip_address": "115.112.159.195",
                                            "beam_width": null,
                                            "icon": "media/uploaded/icons/2014-09-25/2014-09-25-13-59-00_P2P-Green.png",
                                            "sub_station": [
                                                {
                                                    "device_name": "221",
                                                    "data": {
                                                        "substation_device_ip_address": "115.112.159.196",
                                                        "lat": 26.91775,
                                                        "antenna_height": 12,
                                                        "perf_value": "-52",
                                                        "markerUrl": "media/uploaded/icons/2014-09-25/2014-09-25-13-59-00_P2P-Green.png",
                                                        "link_color": "rgba(255, 216, 3, 0.98)",
                                                        "lon": 70.9458611111111,
                                                        "param": {
                                                            "sub_station": [
                                                                {
                                                                    "title": "SS IP",
                                                                    "name": "ss_ip",
                                                                    "value": "115.112.159.196",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "SS MAC",
                                                                    "name": "ss_mac",
                                                                    "value": "00:15:67:2e:94:0e",
                                                                    "show": 0
                                                                },
                                                                {
                                                                    "title": "SS Name",
                                                                    "name": "name",
                                                                    "value": "091jais030007856076",
                                                                    "show": 0
                                                                },
                                                                {
                                                                    "title": "Circuit ID",
                                                                    "name": "cktid",
                                                                    "value": "091JAIS030007856076",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "QOS(BW)",
                                                                    "name": "qos_bandwidth",
                                                                    "value": 2048,
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Latitude",
                                                                    "name": "latitude",
                                                                    "value": 26.91775,
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Longitude",
                                                                    "name": "longitude",
                                                                    "value": 70.9458611111111,
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Antenna Height",
                                                                    "name": "antenna_height",
                                                                    "value": 12,
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Polarisation",
                                                                    "name": "polarisation",
                                                                    "value": "NULL",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Technology",
                                                                    "name": "ss_technology",
                                                                    "value": "P2P",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Building Height",
                                                                    "name": "building_height",
                                                                    "value": null,
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "tower_height",
                                                                    "name": "tower_height",
                                                                    "value": 40,
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "SS MountType",
                                                                    "name": "mount_type",
                                                                    "value": "NULL",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Alias",
                                                                    "name": "alias",
                                                                    "value": "091JAIS030007856076",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "SS Device ID",
                                                                    "name": "ss_device_id",
                                                                    "value": 221,
                                                                    "show": 0
                                                                },
                                                                {
                                                                    "title": "Antenna Type",
                                                                    "name": "antenna_type",
                                                                    "value": "NULL",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Ethernet Extender",
                                                                    "name": "ethernet_extender",
                                                                    "value": "",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Cable Length",
                                                                    "name": "cable_length",
                                                                    "value": null,
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Customer Address",
                                                                    "name": "customer_address",
                                                                    "value": "Taj Jaisalmer Jodhpur Jaisalmer Road,, Jaisalmer, Rajasthan 345001,prasitha@dvois.com,Jaisalmer,Rajasthan India 345001",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Date of Acceptance",
                                                                    "name": "date_of_acceptance",
                                                                    "value": "2013-04-01",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "RSSI During Acceptance",
                                                                    "name": "dl_rssi_during_acceptance",
                                                                    "value": null,
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Planned Frequency",
                                                                    "name": "planned_frequency",
                                                                    "value": "",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Service Throughput",
                                                                    "name": "service_throughput",
                                                                    "value": "2.14",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Uas",
                                                                    "name": "uas",
                                                                    "value": "0",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Management Port On Odu",
                                                                    "name": "Management_Port_on_Odu",
                                                                    "value": "0.0045",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Radio Interface",
                                                                    "name": "Radio_Interface",
                                                                    "value": "0.0000",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Uptime",
                                                                    "name": "uptime",
                                                                    "value": "1174212",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Rssi",
                                                                    "name": "rssi",
                                                                    "value": "-52",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Cbw",
                                                                    "name": "cbw",
                                                                    "value": "5000",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Frequency",
                                                                    "name": "frequency",
                                                                    "value": "5855",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Idu Sn",
                                                                    "name": "idu_sn",
                                                                    "value": "unknown_value",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Link Distance",
                                                                    "name": "link_distance",
                                                                    "value": "3300",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Mimo Diversity",
                                                                    "name": "mimo_diversity",
                                                                    "value": "unknown_value",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Producttype",
                                                                    "name": "producttype",
                                                                    "value": "WL1000-ACCESS/F58/ID",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Ssid",
                                                                    "name": "ssid",
                                                                    "value": "SELUCREH091JAIS03000",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Site Sync State",
                                                                    "name": "site_sync_state",
                                                                    "value": "notSupported",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "2",
                                                                    "name": "2",
                                                                    "value": "Auto",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "3",
                                                                    "name": "3",
                                                                    "value": "Auto",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "1",
                                                                    "name": "1",
                                                                    "value": "Auto",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "4",
                                                                    "name": "4",
                                                                    "value": "unknown_port_ode",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Latency",
                                                                    "name": "rta",
                                                                    "value": "56.952",
                                                                    "show": 1
                                                                },
                                                                {
                                                                    "title": "Packet Loss",
                                                                    "name": "pl",
                                                                    "value": "0",
                                                                    "show": 1
                                                                }
                                                            ]
                                                        }
                                                    },
                                                    "id": 221,
                                                    "name": "091jais030007856076"
                                                }
                                            ],
                                            "device_name": "220",
                                            "azimuth_angle": 0,
                                            "pl": "0"
                                        }
                                    ]
                                },
                                "bh_info": [
                                    {
                                        "show": 1,
                                        "name": "pl",
                                        "value": "NA",
                                        "title": "Packet Drop"
                                    },
                                    {
                                        "show": 1,
                                        "name": "rta",
                                        "value": "NA",
                                        "title": "Latency"
                                    }
                                ],
                                "bs_id": 57,
                                "bs_alias": "Jaisalmar",
                                "message": "Successfully fetched performance data."
                            }
                        ]
    """

    def get(self, request):

        #TODO : use only() and defer() for this data
        # defer_bs_list = []
        # defer_sector_list = []
        # defer_Ss_list = []

        device_list = list()
        machine_dict = dict()
        device_value_list = ['id', 'machine__name', 'device_name', 'ip_address']

        # get base stations id's list
        bs_ids = eval(str(self.request.GET.get('base_stations', None)))

        # type of thematic settings needs to be fetched
        ts_type = self.request.GET.get('ts', 'normal')

        # performance data dictionary
        performance_data = list()

        # base station counter
        bs_counter = 0

        # Create instance of 'InventoryUtilsGateway' class
        inventory_utils = InventoryUtilsGateway()

        # loop through all base stations having id's in bs_ids list
        try:
            for bs_id in bs_ids:
                # increment base station counter
                bs_counter += 1

                # base station data dictionary
                bs_dict = dict()

                # base station
                try:
                    #4 query state, city, backhaul, backhaul configure on
                    bs_objects = BaseStation.objects.prefetch_related(
                        'state',
                        'city',
                        'backhaul',
                        'backhaul__bh_configured_on',
                        'sector'
                    ).get(
                        id=bs_id
                    )

                    bs = bs_objects

                    bs_dict['bs_name'] = bs.name
                    bs_dict['bs_alias'] = bs.alias
                    bs_dict['maintenance_status'] = bs.maintenance_status

                    if str(bs.maintenance_status) == 'Yes':
                        bs_dict['maintenance_status_icon'] = 'static/img/icons/bs_red.png'
                    elif str(bs.maintenance_status) == 'No':
                        bs_dict['maintenance_status_icon'] = 'static/img/icons/bs_black.png'
                    else:
                        pass

                    bs_dict['bs_id'] = bs_id
                    bs_dict['message'] = "Failed to fetch performance data."
                    bs_dict['param'] = dict()
                    bs_dict['param']['sector'] = list()
                except Exception as e:
                    continue #if no bs. continue. not a possible condition

                # if base station exist
                if bs:

                    # backhaul device
                    backhaul_device = None
                    try:
                        backhaul_device = bs.backhaul.bh_configured_on
                    except Exception as e:
                        pass #no backhaul. dont care.

                    # get all sectors associated with base station (bs)
                    # query for sectors and sector configured on
                    sectors = bs.sector.prefetch_related(
                        'sector_configured_on',
                        'circuit_set',
                        'antenna',
                        'sector_configured_on_port'
                    ).filter(
                        sector_configured_on__isnull=False,
                        sector_configured_on__is_added_to_nms__gt=0
                    )

                    if bs.backhaul and bs.backhaul.bh_configured_on_id:
                        # first gather all the devices
                        device_list = Device.objects.filter(
                            Q(id__in=sectors.values_list('sector_configured_on', flat=True)) #query saved
                            |
                            Q(id__in=[bs.backhaul.bh_configured_on_id]) #query saved
                            |
                            Q(id__in=SubStation.objects.filter( # 1 query
                                id__in=Circuit.objects.filter( # 1 query
                                    sector__in=sectors
                                ).values_list('sub_station_id',flat=True)
                            ).values_list('device', flat=True)),
                            is_added_to_nms__gt=0
                        ).values('device_name', 'machine__name')
                    else:
                        device_list = Device.objects.filter(
                            Q(id__in=sectors.values_list('sector_configured_on', flat=True)) #query saved
                            |
                            Q(id__in=SubStation.objects.filter( # 1 query
                                id__in=Circuit.objects.filter( # 1 query
                                    sector__in=sectors
                                ).values_list('sub_station_id',flat=True)
                            ).values_list('device', flat=True)),
                            is_added_to_nms__gt=0
                        ).values('device_name', 'machine__name')

                    bs_devices = [
                        {
                            'device_name': device['device_name'],
                            'device_machine': device['machine__name'],
                        }
                        for device in device_list
                    ]

                    machine_dict = inventory_utils.prepare_machines(bs_devices)

                    # ############################## PERF DATA GATHERING START #################################

                    network_perf_data = list()
                    performance_perf_data = list()
                    service_perf_data = list()
                    inventory_perf_data = list()
                    status_perf_data = list()
                    utilization_perf_data = list()

                    for machine_name in machine_dict:
                        devices_list = machine_dict[machine_name]

                        # device network info
                        device_network_info = NetworkStatus.objects.filter(device_name__in=devices_list).values(
                            'device_name', 'service_name', 'data_source', 'current_value', 'sys_timestamp'
                        ).order_by().using(alias=machine_name)

                        network_perf_data.extend(list(device_network_info))

                        # device performance info
                        performance_network_info = PerformanceStatus.objects.filter(
                            device_name__in=devices_list).values('device_name',
                                                                 'service_name',
                                                                 'data_source',
                                                                 'current_value',
                                                                 'sys_timestamp').order_by().using(alias=machine_name)

                        performance_perf_data.extend(list(performance_network_info))

                        # device service info
                        device_service_info = ServiceStatus.objects.filter(device_name__in=devices_list).values(
                            'device_name', 'service_name', 'data_source', 'current_value', 'sys_timestamp'
                        ).order_by().using(alias=machine_name)

                        service_perf_data.extend(list(device_service_info))

                        # device inventory info
                        device_inventory_info = InventoryStatus.objects.filter(device_name__in=devices_list).values(
                            'device_name', 'service_name', 'data_source', 'current_value', 'sys_timestamp'
                        ).order_by().using(alias=machine_name)

                        inventory_perf_data.extend(list(device_inventory_info))

                        # device status info
                        device_status_info = Status.objects.filter(device_name__in=devices_list).values(
                            'device_name', 'service_name', 'data_source', 'current_value', 'sys_timestamp'
                        ).order_by().using(alias=machine_name)

                        status_perf_data.extend(list(device_status_info))

                        # device utilization info
                        device_utilization_info = UtilizationStatus.objects.filter(device_name__in=devices_list).values(
                            'device_name', 'service_name', 'data_source', 'current_value', 'sys_timestamp'
                        ).order_by().using(alias=machine_name)

                        utilization_perf_data.extend(list(device_utilization_info))

                    # ############################## PERF DATA GATHERING END #################################

                    # backhaul data
                    if backhaul_device and backhaul_device.is_added_to_nms > 0:
                        backhaul_data = self.get_backhaul_info(backhaul_device, network_perf_data)
                        bs_dict['bh_info'] = backhaul_data['bh_info'] if 'bh_info' in backhaul_data else []
                        bs_dict['bh_pl'] = backhaul_data['bh_pl'] if 'bh_pl' in backhaul_data else "NA"
                        bs_dict['bhSeverity'] = backhaul_data['bhSeverity'] if 'bhSeverity' in backhaul_data else "NA"

                    # loop through all sectors
                    for sector_obj in sectors:

                        # sector
                        sector = sector_obj

                        # sector configured on device
                        sector_device = sector.sector_configured_on

                        # device technology
                        try:
                            device_technology = DeviceTechnology.objects.get(id=sector_device.device_technology)
                        except Exception as e:
                            device_technology = None

                        # device technology
                        try:
                            device_type = DeviceType.objects.get(id=sector_device.device_type)
                        except Exception as e:
                            device_type = None




                        # thematic settings for current user
                        user_thematics = self.get_thematic_settings(device_technology,device_type)

                        # service & data source
                        service = ""
                        data_source = ""
                        try:
                            if ts_type == "normal":
                                service = user_thematics.thematic_template.threshold_template.live_polling_template.service.name
                                data_source = user_thematics.thematic_template.threshold_template.live_polling_template.data_source.name
                            elif ts_type == "ping":
                                service = user_thematics.thematic_template.service
                                data_source = user_thematics.thematic_template.data_source
                        except Exception as e:
                            pass

                        if sector_device and sector_device.is_added_to_nms > 0:

                            subs = SubStation.objects.prefetch_related(
                                'device',
                                'city',
                                'state',
                                'circuit_set',
                                'antenna',
                                'circuit_set__sector',
                                'circuit_set__customer',
                                'circuit_set__sector__base_station',
                                'circuit_set__sector__base_station__backhaul'
                            ).filter(
                                id__in=sector.circuit_set.values_list('sub_station', flat=True)
                            )

                            # get performance data

                            sector_performance_data = self.get_sector_performance_info(sector_device,
                                                                                       network_perf_data,
                                                                                       performance_perf_data,
                                                                                       service_perf_data,
                                                                                       inventory_perf_data,
                                                                                       status_perf_data,
                                                                                       utilization_perf_data,
                                                                                       sector_obj,
                                                                                       user_thematics,
                                                                                       device_technology,
                                                                                       service,
                                                                                       data_source)

                            # sector dictionary
                            sector_dict = dict()
                            sector_dict['device_name'] = sector_device.device_name
                            sector_dict['sector_id'] = sector.id
                            sector_dict['ip_address'] = sector_device.ip_address
                            sector_dict['azimuth_angle'] = sector_performance_data['azimuth_angle']
                            sector_dict['beam_width'] = sector_performance_data['beam_width']
                            sector_dict['radius'] = sector_performance_data['radius']
                            sector_dict['color'] = sector_performance_data['color']
                            sector_dict['polled_frequency'] = sector_performance_data['polled_frequency']
                            sector_dict['pl'] = sector_performance_data['pl']
                            sector_dict['perf_value'] = sector_performance_data['perf_value']
                            sector_dict['icon'] = sector_performance_data['icon']
                            sector_dict['perf_info'] = sector_performance_data['perf_info']
                            sector_dict['sub_station'] = list()

                            # get all substations associated with sector from 'Topology' model in performance
                            # replaceing topology code
                            # as the topology is auto-updated
                            # using celery beat

                            # loop through all substations using ips in 'substations_ips_list'
                            for ss in subs:

                                # substation
                                substation = ss

                                substation_device = ss.device

                                ss_dict = dict()
                                if substation and (substation_device.is_added_to_nms > 0):

                                    ss_default_link_color = sector_performance_data['color']
                                    ss_dict['device_name'] = substation_device.device_name
                                    ss_dict['id'] = substation_device.id
                                    ss_dict['name'] = substation.name
                                    ss_dict['data'] = self.get_substation_info(substation,
                                                                               substation_device,
                                                                               ss_default_link_color,
                                                                               network_perf_data,
                                                                               performance_perf_data,
                                                                               service_perf_data,
                                                                               inventory_perf_data,
                                                                               status_perf_data,
                                                                               utilization_perf_data,
                                                                               user_thematics,
                                                                               device_technology,
                                                                               service,
                                                                               data_source)

                                    # append substation dictionary to 'sub_station' list
                                    sector_dict['sub_station'].append(ss_dict)
                                else:
                                    continue

                            # append 'sector_dict' to 'sector' list
                            bs_dict['param']['sector'].append(sector_dict)
                        else:
                            continue

                if bs_dict:
                    bs_dict['message'] = "Successfully fetched performance data."
                    performance_data.append(bs_dict)
        except Exception as e:
            performance_data = {'message': "No Base Station to fetch performance data."}

        return HttpResponse(json.dumps(eval(str(performance_data))))

    def get_backhaul_info(self, bh_device, network_perf_data):
        """ Get Sector performance info

            Parameters:
                - bh_device (<class 'device.models.Device'>) - backhaul device for e.g. 10.175.102.3

            Returns:
               - backhaul_data (dictionary) - dictionary containing backhaul performance data
                                                {
                                                    'bhSeverity': 'NA',
                                                    'bh_info': [
                                                        {
                                                            'title': 'PacketDrop',
                                                            'name': 'pl',
                                                            'value': 'NA',
                                                            'show': 1
                                                        },
                                                        {
                                                            'title': 'Latency',
                                                            'name': 'rta',
                                                            'value': 'NA',
                                                            'show': 1
                                                        }
                                                    ]
                                                }
        """

        # backhaul data
        backhaul_data = dict()
        backhaul_data['bh_info'] = list()
        backhaul_data['bhSeverity'] = "NA"
        backhaul_data['bh_pl'] = "NA"

        # pl
        try:
            backhaul_data['bh_pl'] = [d for d in network_perf_data if d['device_name'] == bh_device.device_name and
                                d['data_source'] == 'pl'][0]['current_value']
        except Exception as e:
            # pl_dict['value'] = "NA"
            backhaul_data['bh_pl'] = "NA"

        # bh severity
        try:
            backhaul_data['bhSeverity'] = [d for d in network_perf_data if d['device_name'] == bh_device.device_name and
                                           d['data_source'] == 'pl'][0]['severity']
        except Exception as e:
            backhaul_data['bhSeverity'] = 'unknown'

        return backhaul_data

    def get_sector_performance_info(self,
                                    device,
                                    network_perf_data,
                                    performance_perf_data,
                                    service_perf_data,
                                    inventory_perf_data,
                                    status_perf_data,
                                    utilization_perf_data,
                                    sector=None,
                                    user_thematics=None,
                                    device_technology=None,
                                    service=None,
                                    data_source=None):

        """ Get Sector performance info

            Parameters:
                - device (<class 'device.models.Device'>) - device name
                - network_perf_data (list) - list of dicts containing performance data
                                             from network status table
                - other_perf_data (list) - list of dicts containing performance data from
                                           status, service, inventory status tables
                - sector (<class 'inventory.models.Sector'>) - sector object
                - user_thematics (<class 'inventory.models.UserThematicSettings'>) - thematic settings object for
                                                                                     current user
                - device_technology (<class 'device.models.DeviceTechnology'>) - sector technology object
                - service (unicode) - service name corresponding to user_thematics e.g. 'radwin_uas'
                - data_source (unicode) - data source name corresponding to user_thematics for e.g. 'uas'

            Returns:
               - performance_data (dictionary) - dictionary containing sector performance data for e.g.
                                                {
                                                    'perf_info': [
                                                        {
                                                            'url': None,
                                                            'show': 1,
                                                            'name': 'session_uptime',
                                                            'value': None,
                                                            'title': 'SessionUptime'
                                                        },
                                                        {
                                                            'show': 1,
                                                            'name': 'connected_bs_ip',
                                                            'value': 'NA',
                                                            'title': 'ConnectedBSIP'
                                                        }
                                                    ],
                                                    'color': '',
                                                    'polled_frequency': '',
                                                    'radius': '',
                                                    'beam_width': None,
                                                    'icon': 'media/uploaded/icons/2015/01/19/P2P-Gray.png',
                                                    'azimuth_angle': 0.0,
                                                    'pl': '',
                                                    'perf_value': [

                                                    ]
                                                }
        """

        # device name
        device_name = device.device_name

        # machine name
        machine_name = device.machine.name

        # performance dictionary
        performance_data = dict()
        performance_data['azimuth_angle'] = ""
        performance_data['beam_width'] = ""
        performance_data['radius'] = ""
        performance_data['color'] = ""
        performance_data['polled_frequency'] = ""
        performance_data['pl'] = ""
        performance_data['perf_value'] = ""
        performance_data['icon'] = ""
        performance_data['perf_info'] = ''
        try:
            performance_data['perf_info'] = self.get_device_info(device,
                                                                 machine_name,
                                                                 network_perf_data,
                                                                 service_perf_data,
                                                                 inventory_perf_data,
                                                                 status_perf_data)
        except Exception as e:
            pass

        # freeze time (data fetched from freeze time to latest time)
        freeze_time = self.request.GET.get('freeze_time', '0')

        # type of thematic settings needs to be fetched
        ts_type = self.request.GET.get('ts', 'normal')

        # device frequency
        device_frequency = self.get_device_polled_frequency(device_name,
                                                            machine_name,
                                                            freeze_time,
                                                            performance_perf_data,
                                                            inventory_perf_data,
                                                            sector)

        # update device frequency
        performance_data['polled_frequency'] = device_frequency

        # device pl
        device_pl = self.get_device_pl(device_name,
                                       machine_name,
                                       network_perf_data,
                                       freeze_time)

        # update device pl
        performance_data['pl'] = device_pl

        # device link/frequency color
        device_link_color = self.get_frequency_color_and_radius(device_frequency, device_pl)[0]

        # update performance color
        performance_data['color'] = device_link_color

        # antenna polarization, azimuth angle, beam width and radius
        # sector to which device is associated
        # sector antenna
        antenna = sector.antenna
        # azimuth angle
        azimuth_angle = sector.antenna.azimuth_angle if antenna else 'N/A'
        # beam width
        beam_width = sector.antenna.beam_width if antenna else 'N/A'
        # radius
        radius = self.get_frequency_color_and_radius(device_frequency, device_pl)[1]

        # update azimuth_angle, beam_width, radius
        performance_data['azimuth_angle'] = azimuth_angle
        performance_data['beam_width'] = beam_width
        performance_data['radius'] = radius

        if not device_technology:
            return performance_data

        if not user_thematics:
            return performance_data

        if service and data_source:
            # performance value
            perf_payload = {
                'device_name': device_name,
                'machine_name': machine_name,
                'freeze_time': freeze_time,
                'device_service_name': service,
                'device_service_data_source': data_source
            }
        else:
            return performance_data

        performance_value = self.get_performance_value(perf_payload,
                                                       network_perf_data,
                                                       performance_perf_data,
                                                       service_perf_data,
                                                       inventory_perf_data,
                                                       status_perf_data,
                                                       utilization_perf_data,
                                                       ts_type)

        if user_thematics:
            # icon
            icon = ""

            # device type
            device_type = DeviceType.objects.get(pk=device.device_type)

            try:
                icon = "media/" + str(device_type.device_icon)
            except Exception as e:
                pass

            if device_pl != "100":
                # fetch icon settings for thematics as per thematic type selected i.e. 'ping' or 'normal'
                th_icon_settings = ""
                try:
                    th_icon_settings = user_thematics.thematic_template.icon_settings
                except Exception as e:
                    pass

                # fetch thematic ranges as per thematic type selected i.e. 'ping' or 'normal'
                th_ranges = ""
                try:
                    if ts_type == "ping":
                        th_ranges = user_thematics.thematic_template
                    elif ts_type == "normal":
                        th_ranges = user_thematics.thematic_template.threshold_template
                    else:
                        pass
                except Exception as e:
                    pass

                # fetch service type if 'ts_type' is "normal"
                service_type = ""
                try:
                    if ts_type == "normal":
                        service_type = user_thematics.thematic_template.threshold_template.service_type
                except Exception as e:
                    pass

                # comparing threshold values to get icon
                try:
                    if performance_value and len(performance_value):
                        # get appropriate icon
                        if ts_type == "normal":
                            if service_type == "INT":
                                value = ast.literal_eval(str(performance_value))
                                icon = self.get_icon_for_numeric_service(th_ranges, th_icon_settings, value)
                            elif service_type == "STR":
                                value = str(performance_value)
                                icon = self.get_icon_for_string_service(th_ranges, th_icon_settings, value)
                            else:
                                pass
                        elif ts_type == "ping":
                            value = ast.literal_eval(str(performance_value))
                            icon = self.get_icon_for_numeric_service(th_ranges, th_icon_settings, value)
                        else:
                            pass
                except Exception as e:
                    return performance_data

            # update performance value
            if device_pl != "100":
                performance_data['perf_value'] = performance_value
            else:
                performance_data['perf_value'] = ""

            # update performance icon
            performance_data['icon'] = icon

        return performance_data

    def get_icon_for_numeric_service(self, th_ranges=None, th_icon_settings=None, value=None):
        """
            Get device icon corresponding to fetched performance value
            Parameters:
                - th_ranges (<class 'inventory.models.ThresholdConfiguration'>) - threshold configuration object
                                                                                  for e.g. Wimax DL RSSI
                - th_icon_settings (unicode) - icon settings in json format for e.g.
                        [
                            {
                                'icon_settings1': u'uploaded/icons/2014-09-26/2014-09-26-11-56-11_SM-GIF.gif'
                            },
                            {
                                'icon_settings2': u'uploaded/icons/2014-10-26/2014-10-26-14-59-40_SM-Red.png'
                            },
                            {
                                'icon_settings3': u'uploaded/icons/2014-09-25/2014-09-25-13-59-00_P2P-Green.png'
                            }
                        ]
                - value (str) - performance value for e.g "-57"

            Returns:
                - icon (str) - icon location i.e "media/uploaded/icons/2014/09/18/wifi3.png"
        """

        # default image to be loaded
        image_partial = "icons/mobilephonetower10.png"

        if th_ranges and th_icon_settings and len(str(value)):
            compare_this = float(value)
            for i in range(1, 11):
                try:
                    compare_to_start = float(eval("th_ranges.range%d_start" % i))
                    compare_to_end = float(eval("th_ranges.range%d_end" % i))
                    icon_settings = eval(th_icon_settings)
                    if compare_to_start <= compare_this <= compare_to_end:
                        icon_key = "icon_settings{0}".format(i)
                        for icon_setting in icon_settings:
                            if icon_key in icon_setting.keys():
                                image_partial = str(icon_setting[icon_key])
                                break
                except Exception as e:
                    continue

        # image url
        img_url = "media/" + str(image_partial) if "uploaded" in str(
            image_partial) else "static/img/" + str(image_partial)

        # icon to be send in response
        icon = str(img_url)

        return icon

    def get_icon_for_string_service(self, th_ranges=None, th_icon_settings=None, value=None):
        """
            Get device icon corresponding to fetched performance value
            Parameters:
                - th_ranges (<class 'inventory.models.ThresholdConfiguration'>) - threshold configuration object
                                                                                  for e.g. Wimax DL RSSI
                - th_icon_settings (unicode) - icon settings in json format for e.g.
                        [
                            {
                                'icon_settings1': u'uploaded/icons/2014-09-26/2014-09-26-11-56-11_SM-GIF.gif'
                            },
                            {
                                'icon_settings2': u'uploaded/icons/2014-10-26/2014-10-26-14-59-40_SM-Red.png'
                            },
                            {
                                'icon_settings3': u'uploaded/icons/2014-09-25/2014-09-25-13-59-00_P2P-Green.png'
                            }
                        ]
                - value (str) - performance value for e.g "-57"

            Returns:
                - icon (str) - icon location i.e "media/uploaded/icons/2014/09/18/wifi3.png"
        """

        # default image to be loaded
        image_partial = "icons/mobilephonetower10.png"
        if th_ranges and th_icon_settings and value:
            compare_this = ''.join(e for e in value if e.isalnum())
            for i in range(1, 11):
                try:
                    eval_this = eval("th_ranges.range%d_start" % i)
                    compare_to = ''.join(e for e in eval_this if e.isalnum())
                    icon_settings = eval(th_icon_settings)
                    if compare_this.strip().lower() == compare_to.strip().lower():
                        icon_key = "icon_settings{0}".format(i)
                        for icon_setting in icon_settings:
                            if icon_key in icon_setting.keys():
                                image_partial = str(icon_setting[icon_key])
                                break
                except Exception as e:
                    continue

        # image url
        img_url = "media/" + str(image_partial) if "uploaded" in str(
            image_partial) else "static/img/" + str(image_partial)

        # icon to be send in response
        icon = str(img_url)

        return icon

    def get_device_info(self,
                        device_obj,
                        machine_name,
                        network_perf_data,
                        service_perf_data,
                        inventory_perf_data,
                        status_perf_data,
                        device_pl="",
                        ss=None,
                        is_static=False):
        """ Get Sector/Sub Station device information

            Parameters:
                - device_obj (<class 'device.models.Device'>) - device name
                - machine_name (unicode) - machine name
                - network_perf_data (list) - list of dicts containing performance data
                                                                       from network status table
                - other_perf_data (list) - list of dicts containing performance data from
                                                                     status, service, inventory status tables
                - device_pl (unicode) - device pl value for e.g. "100"
                - ss (<class 'inventory.models.SubStation'>) - substation object
                - is_static (bool) - static parameter needed or not identifier

            Returns:
                - device_info (list) - list of dictionaries containing device static or polled data
                                                    [
                                                        {
                                                            'show': 1,
                                                            'name': u'uptime',
                                                            'value': u'6.0082333333',
                                                            'title': u'Uptime'
                                                        },
                                                        {
                                                            'show': 1,
                                                            'name': u'frequency',
                                                            'value': u'5830',
                                                            'title': u'Frequency'
                                                        },
                                                        {
                                                            'show': 1,
                                                            'name': u'pl',
                                                            'value': u'4',
                                                            'title': 'PacketLoss'
                                                        }
                                                    ]
        """

        # get device name
        device_name = device_obj.device_name

        # get device id (used to make url for perf api data)
        device_id = device_obj.id

        processed = {}

        # device info dictionary
        device_info = list()

        # connected bs ip
        connected_bs_ip = ""

        # is device is a substation device than add static inventory parameters in list
        if is_static:
            if ss:
                # substation
                substation = ss
                # substation device
                substation_device = device_obj

                try:
                    circuit = ss.circuit_set.get()
                except Exception as e:
                    return device_info

                try:
                    # if bs_connected_ip not exist in topology than get it from gis inventory
                    connected_bs_ip = Topology.objects.filter(connected_device_ip=device_obj.ip_address)
                    if connected_bs_ip:
                        connected_bs_ip = connected_bs_ip[0].ip_address
                    elif not connected_bs_ip:
                        connected_bs_ip = circuit.sector.sector_configured_on.ip_address
                    else:
                        pass
                except Exception as e:
                    pass

                # base station alias
                base_station_alias = ""
                try:
                    base_station_alias = circuit.sector.base_station.alias
                except Exception, e:
                    pass

                # pe ip
                pe_ip = ""
                try:
                    pe_ip = circuit.sector.base_station.backhaul.pe_ip
                except Exception as e:
                    pass

                # substation technology
                substation_technology = ""
                try:
                    substation_technology = DeviceTechnology.objects.get(id=substation_device.device_technology).name
                except Exception as e:
                    pass

                # circuit id
                circuit_id = ""
                try:
                    circuit_id = circuit.circuit_id
                except Exception as e:
                    pass

                # qos bandwidth
                qos = ""
                try:
                    qos = circuit.qos_bandwidth
                except Exception as e:
                    pass

                # customer alias
                customer_alias = ""
                try:
                    customer_alias = circuit.customer.alias
                except Exception as e:
                    pass

                # customer address
                customer_address = ""
                try:
                    customer_address = circuit.customer.address
                except Exception as e:
                    pass

                # date of acceptance
                date_of_acceptance = ""
                try:
                    date_of_acceptance = str(circuit.date_of_acceptance)
                except Exception as e:
                    pass

                # dl rssi during acceptance
                dl_rssi_during_acceptance = ""
                try:
                    dl_rssi_during_acceptance = circuit.dl_rssi_during_acceptance
                except Exception as e:
                    pass

                # dl cinr during acceptance
                dl_cinr_during_acceptance = ""
                try:
                    dl_cinr_during_acceptance = circuit.dl_cinr_during_acceptance
                except Exception as e:
                    pass

                # ss sector frequency
                ss_sector_frequency = ""
                try:
                    ss_sector_frequency = circuit.sector.frequency.value
                except Exception as e:
                    pass

                # antenna height
                antenna_height = ""
                try:
                    antenna_height = substation.antenna.height
                except Exception as e:
                    pass

                # antenna polarization
                antenna_polarization = ""
                try:
                    antenna_polarization = substation.antenna.polarization
                except Exception as e:
                    pass

                # antenna mount type
                antenna_mount_type = ""
                try:
                    antenna_mount_type = substation.antenna.mount_type

                except Exception as e:
                    pass

                # antenna type
                antenna_type = ""
                try:
                    antenna_type = substation.antenna.antenna_type

                except Exception as e:
                    pass

                # adding gis inventory static parameters to device info
                device_info = [
                    {
                        'name': 'base_station_alias',
                        'title': 'Base Station Name',
                        'show': 0,
                        'value': base_station_alias
                    },
                    {
                        'name': 'ss_ip',
                        'title': 'SS IP',
                        'show': 1,
                        'value': nocout_utils.format_value(substation_device.ip_address)
                    },
                    {
                        'name': 'ss_mac',
                        'title': 'SS MAC',
                        'show': 0,
                        'value': nocout_utils.format_value(substation_device.mac_address)
                    },
                    {
                        'name': 'name',
                        'title': 'SS Name',
                        'show': 0,
                        'value': nocout_utils.format_value(substation.name)
                    },
                    {
                        'name': 'connected_bs_ip',
                        'title': 'Connected BS IP',
                        'show': 1,
                        'value': nocout_utils.format_value(connected_bs_ip)
                    },
                    {
                        'name': 'cktid',
                        'title': 'Circuit ID',
                        'show': 1,
                        'value': nocout_utils.format_value(circuit_id)
                    },
                    {
                        'name': 'qos_bandwidth',
                        'title': 'QOS(BW)',
                        'show': 1,
                        'value': nocout_utils.format_value(qos)
                    },
                    {
                        'name': 'lat_lon',
                        'title': 'Lat, Long',
                        'show': 1,
                        'value': nocout_utils.format_value(str(substation.latitude)+","+str(substation.longitude))
                    },
                    {
                        'name': 'antenna_height',
                        'title': 'Antenna Height',
                        'show': 1,
                        'value': nocout_utils.format_value(antenna_height)
                    },
                    {
                        'name': 'polarisation',
                        'title': 'Antenna Polarisation',
                        'show': 1,
                        'value': nocout_utils.format_value(antenna_polarization)
                    },
                    {
                        'name': 'ss_technology',
                        'title': 'Technology',
                        'show': 1,
                        'value': nocout_utils.format_value(substation_technology)
                    },
                    {
                        'name': 'pe_ip',
                        'title': 'PE IP',
                        'show': 1,
                        'value': nocout_utils.format_value(pe_ip)
                    },
                    {
                        'name': 'building_height',
                        'title': 'Building Height',
                        'show': 1,
                        'value': nocout_utils.format_value(substation.building_height)
                    },
                    {
                        'name': 'tower_height',
                        'title': 'Tower Height',
                        'show': 1,
                        'value': nocout_utils.format_value(substation.tower_height)
                    },
                    {
                        'name': 'mount_type',
                        'title': 'SS MountType',
                        'show': 1,
                        'value': nocout_utils.format_value(antenna_mount_type)
                    },
                    {
                        'name': 'alias',
                        'title': 'Alias',
                        'show': 1,
                        'value': nocout_utils.format_value(substation.alias)
                    },
                    {
                        'name': 'ss_device_id',
                        'title': 'SS Device ID',
                        'show': 0,
                        'value': nocout_utils.format_value(substation_device.id)
                    },
                    {
                        'name': 'antenna_type',
                        'title': 'Antenna Type',
                        'show': 1,
                        'value': nocout_utils.format_value(antenna_type)
                    },
                    {
                        'name': 'ethernet_extender',
                        'title': 'Ethernet Extender',
                        'show': 1,
                        'value': nocout_utils.format_value(substation.ethernet_extender)
                    },
                    {
                        'name': 'cable_length',
                        'title': 'Cable Length',
                        'show': 1,
                        'value': nocout_utils.format_value(substation.cable_length)
                    },
                    {
                        'name': 'customer_alias',
                        'title': 'Customer Name',
                        'show': 1,
                        'value': nocout_utils.format_value(customer_alias)
                    },
                    {
                        'name': 'customer_address',
                        'title': 'Customer Address',
                        'show': 1,
                        'value': nocout_utils.format_value(customer_address)
                    },
                    {
                        'name': 'date_of_acceptance',
                        'title': 'Date of Acceptance',
                        'show': 1,
                        'value': nocout_utils.format_value(date_of_acceptance)
                    },
                    {
                        'name': 'dl_rssi_during_acceptance',
                        'title': 'RSSI During Acceptance',
                        'show': 1,
                        'value': nocout_utils.format_value(dl_rssi_during_acceptance)
                    },
                    {
                        'name': 'dl_cinr_during_acceptance',
                        'title': 'CINR During Acceptance',
                        'show': 1,
                        'value': nocout_utils.format_value(dl_cinr_during_acceptance)
                    },
                    {
                        'name': 'planned_frequency',
                        'title': 'Planned Frequency',
                        'show': 1,
                        'value': nocout_utils.format_value(ss_sector_frequency)
                    }
                ]

        else:
            # device network info
            # device_network_info = NetworkStatus.objects.filter(device_name=device_name).values(
            #     'service_name', 'data_source', 'current_value', 'sys_timestamp'
            # ).using(alias=machine_name)

            device_network_info = [d for d in network_perf_data if d['device_name'] == device_name]

            device_info += self.collect_performance(performance=device_network_info,
                                                    device_id=device_id,
                                                    processed=processed)

            # if device is down than don't show services data
            if device_pl != "100":
                # to update the info window with all the services
                # device performance info
                # device_performance_info = ServiceStatus.objects.filter(device_name=device_name).values(
                #     'service_name', 'data_source', 'current_value', 'sys_timestamp'
                # ).using(alias=machine_name)

                service_perf_data = [d for d in service_perf_data if d['device_name'] == device_name]
                inventory_perf_data = [d for d in inventory_perf_data if d['device_name'] == device_name]
                status_perf_data = [d for d in status_perf_data if d['device_name'] == device_name]

                # # device inventory info
                # device_inventory_info = InventoryStatus.objects.filter(device_name=device_name).values(
                #     'service_name', 'data_source', 'current_value', 'sys_timestamp'
                # ).using(alias=machine_name)
                #
                # # device status info
                # device_status_info = Status.objects.filter(device_name=device_name).values(
                #     'service_name', 'data_source', 'current_value', 'sys_timestamp'
                # ).using(alias=machine_name)

                device_info += self.collect_performance(performance=service_perf_data,
                                                        device_id=device_id,
                                                        processed=processed)

                device_info += self.collect_performance(performance=inventory_perf_data,
                                                        device_id=device_id,
                                                        processed=processed
                )

                device_info += self.collect_performance(performance=status_perf_data,
                                                        device_id=device_id,
                                                        processed=processed
                )

                # # get session uptime
                # format_session = None
                # session_uptime = device_last_down_time(device_obj)
                #
                # if session_uptime:
                #     format_session = datetime.datetime.fromtimestamp(
                #         float(session_uptime)
                #     ).strftime('%Y-%m-%d %H:%M:%S')
                # # session uptime tool tip dictionary
                # session_uptime_info = {
                #     "name": 'session_uptime',
                #     "title": 'Session Uptime',
                #     "show": 1,
                #     "url": None,
                #     "value": format_session
                # }
                #
                # device_info.append(session_uptime_info)

                # bs connected ip
                connected_bs_ip_info = {
                    'name': 'connected_bs_ip',
                    'title': 'Connected BS IP',
                    'show': 1,
                    'value': nocout_utils.format_value(connected_bs_ip)
                }

                device_info.append(connected_bs_ip_info)

            # remove duplicate dictionaries in list
        # device_info = remove_duplicate_dict_from_list(device_info)

        return device_info

    def collect_performance(self, performance, device_id, processed):
        """ Get Sector/Sub Station device information

            Parameters:
                - performance (list) - list of dictionaries containing performance data
                - device_id (long) - device id for e.g. 34925
                - processed (dict) - list of dicts containing processed/filtered performance data

            Returns:
                - device_info (list) - list of dictionaries containing device static or polled data
                                                    [
                                                        {
                                                            'show': 1,
                                                            'name': u'uptime',
                                                            'value': u'6.0082333333',
                                                            'title': u'Uptime'
                                                        },
                                                        {
                                                            'show': 1,
                                                            'name': u'frequency',
                                                            'value': u'5830',
                                                            'title': u'Frequency'
                                                        },
                                                        {
                                                            'show': 1,
                                                            'name': u'pl',
                                                            'value': u'4',
                                                            'title': 'PacketLoss'
                                                        }
                                                    ]
        """
        # Create instance of 'ServiceUtilsGateway' class
        service_utils = ServiceUtilsGateway()

        SERVICE_DATA_SOURCE = service_utils.service_data_sources()

        device_info = list()

        for perf in performance:
            res, name, title, show_gis = self.sanatize_datasource(perf['data_source'], perf['service_name'])

            if not res:
                continue
            if (perf['data_source'], perf['service_name']) in processed:
                continue
            processed[perf['data_source'], perf['service_name']] = []

            service_name = perf['service_name'].strip()

            sds_name = perf['data_source'].strip()

            if sds_name not in ['pl', 'rta']:
                sds_name = service_name.lower() + "_" + sds_name.lower()

            formula = SERVICE_DATA_SOURCE[sds_name]["formula"] \
                if sds_name in SERVICE_DATA_SOURCE \
                else None
            try:
                cur_val = None
                if perf['current_value']:
                    cur_val = perf['current_value']
                try:
                    perf_info = {
                        "name": name,
                        "title": title,
                        "show": show_gis,
                        "url": "performance/service/" + service_name + "/service_data_source/" + perf[
                            'data_source'].strip() + "/device/" + str(
                            device_id) + "?start_date=&end_date=",
                        "value": eval(str(formula) + "(" + str(cur_val) + ")") if formula
                        else cur_val,
                    }
                except Exception as e:
                    perf_info = {
                        "name": name,
                        "title": title,
                        "show": show_gis,
                        "url": "performance/service/" + service_name + "/service_data_source/" + perf[
                            'data_source'].strip() + "/device/" + str(
                            device_id) + "?start_date=&end_date=",
                        "value": cur_val,
                    }

                device_info.append(perf_info)
            except Exception as e:
                pass

        return device_info

    def sanatize_datasource(self, data_source, service_name):
        """ Get Sector performance info

            Parameters:
                - data_source (unicode) - data source name for e.g. 'rta'
                - service_name (unicode) - service name

            Returns:
                - name (unicode) - data source name for e.g. 'rta'
                - title (str) - data source name to display for e.g. 'Latency'
                - show_gis (int) - 1 to show data source; 0 for not to show
        """

        # Create instance of 'ServiceUtilsGateway' class
        service_utils = ServiceUtilsGateway()

        # fetch all data sources
        SERVICE_DATA_SOURCE = service_utils.service_data_sources()

        # if data_source and data_source[:1].isalpha():
        if data_source:
            title = " ".join(data_source.split("_")).title()

            key_name = service_name.strip().lower() + "_" +data_source.strip().lower()

            if data_source.strip().lower() in ['pl', 'rta']:
                name = data_source.strip()
                key_name = data_source.strip().lower()
            else:
                name = key_name

            show_gis = 0
            try:
                if data_source.strip().lower() not in ['pl', 'rta']:
                    title = SERVICE_DATA_SOURCE[key_name]['service_alias'] + "</br> [ " +\
                            SERVICE_DATA_SOURCE[key_name]['display_name'] + " ]"
                else:
                    title = SERVICE_DATA_SOURCE[key_name]['display_name']

                show_gis = SERVICE_DATA_SOURCE[key_name]['show_gis']
            except Exception as e:
                pass

            return True, name, title, show_gis
        return False, False, False, 0

    def get_substation_info(self,
                            substation,
                            substation_device,
                            ss_default_link_color,
                            network_perf_data,
                            performance_perf_data,
                            service_perf_data,
                            inventory_perf_data,
                            status_perf_data,
                            utilization_perf_data,
                            user_thematics=None,
                            device_technology=None,
                            service=None,
                            data_source=None):
        """ Get Sub Station information

            Parameters:
                - substation (<class 'inventory.models.SubStation'>) - substation object
                - substation_device (<class 'device.models.Device'>) - substation device object
                - ss_default_link_color (str) - substation device object
                - network_perf_data (list) - list of dicts containing performance data from network status table
                - other_perf_data (list) - list of dicts containing performance data from status, service,
                                           inventory status tables
                - user_thematics (<class 'inventory.models.UserThematicSettings'>) - thematics for current user
                - device_technology (<class 'device.models.DeviceTechnology'>) - device technology object
                - service (unicode) - service name for e.g. radwin_uas
                - data_source (unicode) - data source name for e.g. uas

            Returns:
               - substation_info (dict) - dictionary containing substation data
                                                    {
                                                        'antenna_height': 33.0,
                                                        'link_color': u'rgba(255,
                                                        192,
                                                        0,
                                                        0.97)',
                                                        'lon': 75.8075,
                                                        'param': {
                                                            'sub_station': [
                                                                {
                                                                    'show': 1,
                                                                    'name': 'ss_ip',
                                                                    'value': u'10.75.165.227',
                                                                    'title': 'SSIP'
                                                                },
                                                                {
                                                                    'show': 0,
                                                                    'name': 'ss_mac',
                                                                    'value': u'00: 15: 67: 51: 5e: 34',
                                                                    'title': 'SSMAC'
                                                                },
                                                                {
                                                                    'show': 0,
                                                                    'name': 'name',
                                                                    'value': u'091jaip623009280393',
                                                                    'title': 'SSName'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'cktid',
                                                                    'value': u'091JAIP623009280393',
                                                                    'title': 'CircuitID'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'qos_bandwidth',
                                                                    'value': 512.0,
                                                                    'title': 'QOS(BW)'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'latitude',
                                                                    'value': 26.9138611111111,
                                                                    'title': 'Latitude'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'longitude',
                                                                    'value': 75.8075,
                                                                    'title': 'Longitude'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'antenna_height',
                                                                    'value': 33.0,
                                                                    'title': 'AntennaHeight'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'polarisation',
                                                                    'value': None,
                                                                    'title': 'Polarisation'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'ss_technology',
                                                                    'value': u'P2P',
                                                                    'title': 'Technology'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'building_height',
                                                                    'value': None,
                                                                    'title': 'BuildingHeight'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'tower_height',
                                                                    'value': None,
                                                                    'title': 'tower_height'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'mount_type',
                                                                    'value': None,
                                                                    'title': 'SSMountType'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'alias',
                                                                    'value': u'091JAIP623009280393',
                                                                    'title': 'Alias'
                                                                },
                                                                {
                                                                    'show': 0,
                                                                    'name': 'ss_device_id',
                                                                    'value': 15864L,
                                                                    'title': 'SSDeviceID'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'antenna_type',
                                                                    'value': None,
                                                                    'title': 'AntennaType'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'ethernet_extender',
                                                                    'value': None,
                                                                    'title': 'EthernetExtender'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'cable_length',
                                                                    'value': None,
                                                                    'title': 'CableLength'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'customer_address',
                                                                    'value': u'IDBIFederalLifeInsuranceCo.Ltd.
                                                                               OfficeNO.802at8thFloorE-2,
                                                                               KJTower,, AshokMarg, C-Scheme,
                                                                               Jaipur, RajasthanIndia302001',
                                                                    'title': 'CustomerAddress'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'date_of_acceptance',
                                                                    'value': None,
                                                                    'title': 'DateofAcceptance'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'dl_rssi_during_acceptance',
                                                                    'value': None,
                                                                    'title': 'RSSIDuringAcceptance'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': 'planned_frequency',
                                                                    'value': '',
                                                                    'title': 'PlannedFrequency'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': u'uptime',
                                                                    'value': u'6.0082333333',
                                                                    'title': u'Uptime'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': u'frequency',
                                                                    'value': u'5830',
                                                                    'title': u'Frequency'
                                                                },
                                                                {
                                                                    'show': 1,
                                                                    'name': u'pl',
                                                                    'value': u'4',
                                                                    'title': 'PacketLoss'
                                                                }
                                                            ]
                                                        },
                                                        'substation_device_ip_address': u'10.75.165.227',
                                                        'markerUrl': '/home/priyesh/Documents/Workspace/nocout_gis/
                                                           nocout/media/uploaded/icons/2014/09/25/P2P-loading4_3.png',
                                                        'perf_value': u'6.0082333333',
                                                        'lat': 26.9138611111111
                                                    }
        """

        # sector info dict
        substation_info = dict()

        # device name
        device_name = substation_device.device_name
        
        # device id
        ss_device_id = substation_device.id

        # machine name
        machine_name = substation_device.machine.name

        # freeze time (data fetched from freeze time to latest time)
        freeze_time = self.request.GET.get('freeze_time', '0')

        # type of thematic settings needs to be fetched
        ts_type = self.request.GET.get('ts', 'normal')

        device_type = None
        try:
            device_type = DeviceType.objects.get(id=substation_device.device_type)
        except Exception as e:
            pass

        if not device_technology:
            return substation_info

        # device frequency
        device_frequency = self.get_device_polled_frequency(device_name,
                                                            machine_name,
                                                            freeze_time,
                                                            performance_perf_data,
                                                            inventory_perf_data,
                                                            sector=None,
                                                            device_type=device_type
        )

        # device pl
        device_pl = self.get_device_pl(device_name,
                                       machine_name,
                                       network_perf_data,
                                       freeze_time)

        # device link/frequency color
        device_link_color = self.get_frequency_color_and_radius(device_frequency, device_pl)[0]

        if not device_link_color:
            device_link_color = ss_default_link_color


        far_end_perf_url = ""
        far_end_inventory_url = ""

        techno_to_append = device_technology.name

        if substation.circuit_set.exists():
            c = substation.circuit_set.filter()[0]
            if c.circuit_type and c.circuit_type.strip().lower() in ['bh','backhaul']:
                techno_to_append = "PTP BH"
        # Check for technology to make perf page url
        if techno_to_append:
            page_type = 'customer'
            if techno_to_append.lower() in ['ptp bh']:
                page_type = 'network'

            far_end_perf_url = reverse(
                'SingleDevicePerf',
                kwargs={
                    'page_type': page_type,
                    'device_id': ss_device_id
                },
                current_app='performance'
            )

        # SS Device Inventory URL
        far_end_inventory_url = reverse(
            'device_edit',
            kwargs={
                'pk': ss_device_id
            },
            current_app='device'
        )

        substation_info['antenna_height'] = substation.antenna.height
        substation_info['lat'] = substation.latitude
        substation_info['lon'] = substation.longitude
        substation_info['perf_page_url'] = far_end_perf_url
        substation_info['inventory_url'] = far_end_inventory_url
        substation_info['technology'] = techno_to_append
        substation_info['link_color'] = device_link_color
        substation_info['show_link'] = 1
        substation_info['param'] = dict()

        # Fetch sub station static info
        substation_info['param']['sub_station'] = self.get_device_info(substation_device,
                                                                       machine_name,
                                                                       network_perf_data,
                                                                       service_perf_data,
                                                                       inventory_perf_data,
                                                                       status_perf_data,
                                                                       device_pl=device_pl,
                                                                       ss=substation,
                                                                       is_static=True,)
        # Fetch sub station polled info
        substation_info['param']['polled_info'] = self.get_device_info(substation_device,
                                                                       machine_name,
                                                                       network_perf_data,
                                                                       service_perf_data,
                                                                       inventory_perf_data,
                                                                       status_perf_data,
                                                                       device_pl=device_pl,
                                                                       ss=substation,
                                                                       is_static=False)

        # thematic settings for current user
        user_thematics = self.get_thematic_settings(device_technology,device_type)

        if not user_thematics:
            return substation_info

        if service and data_source:
            # performance value
            perf_payload = {
                'device_name': device_name,
                'machine_name': machine_name,
                'freeze_time': freeze_time,
                'device_service_name': service,
                'device_service_data_source': data_source
            }
        else:
            return substation_info

        performance_value = None

        if device_pl != "100":
            performance_value = self.get_performance_value(perf_payload,
                                                           network_perf_data,
                                                           performance_perf_data,
                                                           service_perf_data,
                                                           inventory_perf_data,
                                                           status_perf_data,
                                                           utilization_perf_data,
                                                           ts_type)
            substation_info['perf_value'] = performance_value
        else:
            substation_info['perf_value'] = ""

        if user_thematics:
            # icon
            icon = ""

            try:
                icon = "media/" + str(device_type.device_icon)
            except Exception as e:
                pass

            if device_pl != "100":
                # fetch icon settings for thematics as per thematic type selected i.e. 'ping' or 'normal'
                th_icon_settings = ""
                try:
                    th_icon_settings = user_thematics.thematic_template.icon_settings
                except Exception as e:
                    pass

                # fetch thematic ranges as per thematic type selected i.e. 'ping' or 'normal'
                th_ranges = ""
                try:
                    if ts_type == "ping":
                        th_ranges = user_thematics.thematic_template
                    elif ts_type == "normal":
                        th_ranges = user_thematics.thematic_template.threshold_template
                    else:
                        pass
                except Exception as e:
                    pass

                # fetch service type if 'ts_type' is "normal"
                service_type = ""
                try:
                    if ts_type == "normal":
                        service_type = user_thematics.thematic_template.threshold_template.service_type
                except Exception as e:
                    pass

                # comparing threshold values to get icon
                try:
                    if performance_value and len(performance_value):
                        # get appropriate icon
                        if ts_type == "normal":
                            if service_type == "INT":
                                value = ast.literal_eval(str(performance_value))
                                icon = self.get_icon_for_numeric_service(th_ranges, th_icon_settings, value)
                            elif service_type == "STR":
                                value = str(performance_value)
                                icon = self.get_icon_for_string_service(th_ranges, th_icon_settings, value)
                            else:
                                pass
                        elif ts_type == "ping":
                            value = ast.literal_eval(str(performance_value))
                            icon = self.get_icon_for_numeric_service(th_ranges, th_icon_settings, value)
                        else:
                            pass
                except Exception as e:
                    logger.exception(e)

            substation_info['markerUrl'] = icon

        substation_info['substation_device_ip_address'] = substation_device.ip_address

        return substation_info

    def get_device_polled_frequency(self,
                                    device_name,
                                    machine_name,
                                    freeze_time,
                                    performance_perf_data,
                                    inventory_perf_data,
                                    sector=None,
                                    device_type=None):
        """ Get device polled frequency
            Parameters:
                - device_name (unicode) - device name
                - machine_name (unicode) - machine name
                - freeze_time (str) - freeze time i.e. '0'
                - sector (<class 'inventory.models.Sector'>) - sector object
                - device_type (<class 'device.models.DeviceType'>) - device type object
            Returns:
               - device_frequency (str) - device frequency, e.g. "34525"
        """

        # device frequency
        device_frequency = ""
        try:
            # if int(freeze_time):
            #     device_frequency = PerformanceInventory.objects.filter(device_name=device_name, data_source='frequency',
            #                                                            sys_timestamp__lte=int(freeze_time) / 1000)\
            #                                                            .using(alias=machine_name)\
            #                                                            [:1]
            #     if len(device_frequency):
            #         device_frequency = device_frequency[0].current_value
            #     else:
            #         device_frequency = ""
            # else:

            port_based_frequency = False
            service_name = 'wimax_pmp1_frequency_invent'
            if sector:
                if sector.sector_configured_on_port and sector.sector_configured_on_port.name:
                    port_based_frequency = True
                    if 'pmp1' in sector.sector_configured_on_port.name.strip().lower():
                        service_name = 'wimax_pmp1_frequency_invent'
                    elif 'pmp2' in sector.sector_configured_on_port.name.strip().lower():
                        service_name = 'wimax_pmp2_frequency_invent'
                    else:
                        port_based_frequency = False

            #for SS services
            frequency_service = None
            if device_type:
                frequency_service = device_type.service.filter(name__icontains='frequency')

            if port_based_frequency:
                device_frequency = [d for d in inventory_perf_data if d['device_name'] == device_name and
                                    d['service_name'] == service_name and
                                    d['data_source'] == 'frequency']

            elif frequency_service:
                service_name = frequency_service[0]['name']
                if "_invent" in service_name:
                    device_frequency = [d for d in inventory_perf_data if d['device_name'] == device_name and
                                        d['data_source'] == 'frequency']

                    device_frequency = [d for d in performance_perf_data if d['device_name'] == device_name and
                                        d['service_name'] == service_name and
                                        d['data_source'] == 'frequency']

            else:
                device_frequency = [d for d in inventory_perf_data if d['device_name'] == device_name and
                                    d['data_source'] == 'frequency']
            if device_frequency:
                try:
                    device_frequency = device_frequency[0]['current_value']
                except Exception as e:
                    logger.exception(e)
            else:
                device_frequency = ""
        except Exception as e:
            logger.exception(e)

        return device_frequency

    def get_device_pl(self,
                      device_name,
                      machine_name,
                      network_perf_data,
                      freeze_time):
        """ Get device pl
            Parameters:
                - device_name (unicode) - device name
                - machine_name (unicode) - machine name
                - freeze_time (str) - freeze time i.e. '0'
            Returns:
               - device_frequency (str) - device frequency, e.g. "34525"
        """

        # device packet loss
        device_pl = ""

        end_time = float(freeze_time) / 1000
        start_time = end_time - 300

        try:
            if int(freeze_time):
                device_pl = PerformanceNetwork.objects.filter(device_name=device_name,
                                                              service_name='ping',
                                                              data_source='pl',
                                                              sys_timestamp__gte=start_time,
                                                              sys_timestamp__lte=end_time).order_by().using(
                    alias=machine_name).values('current_value')

            else:
                device_pl = [d for d in network_perf_data if d['device_name'] == device_name and
                             d['service_name'] == 'ping' and
                             d['data_source'] == 'pl']

            if device_pl:
                device_pl = device_pl[0]['current_value']
            else:
                device_pl = ""

        except Exception as e:
            logger.exception(e)

        return device_pl

    def get_frequency_color_and_radius(self, device_frequency, device_pl):
        """ Get device pl

            Parameters:
                - device_frequency (unicode) - device frequency, e.g 5830
                - device_pl (unicode) - device pl (packet loss) value, e.g. 4

            Returns:
                - device_link_color (unicode) - device link color, e.g. rgba(255,192,0,0.97)
                - radius (float) - radius, e.g 2.0
        """

        # device link color
        device_link_color = ""

        # radius
        radius = ""

        try:
            if len(device_frequency):
                corrected_dev_freq = device_frequency
                try:
                    chek_dev_freq = ast.literal_eval(device_frequency)
                    if int(chek_dev_freq) > 10:
                        corrected_dev_freq = chek_dev_freq
                except Exception as e:
                    pass

                device_frequency_objects = DeviceFrequency.objects.filter(value__icontains=str(corrected_dev_freq))
                device_frequency_color = DeviceFrequency.objects.filter(value__icontains=str(corrected_dev_freq)) \
                    .values_list('color_hex_value', flat=True)
                device_frequency_object = None
                if len(device_frequency_objects):
                    device_frequency_object = device_frequency_objects[0]
                radius = device_frequency_object.frequency_radius if (
                    device_frequency_object
                    and
                    device_frequency_object.frequency_radius
                ) else 0
                if len(device_frequency_color):
                    device_link_color = device_frequency_color[0]
            if len(device_pl) and int(ast.literal_eval(device_pl)) == 100:
                device_link_color = 'rgb(0,0,0)'
        except Exception as e:
            if len(device_pl) and int(ast.literal_eval(device_pl)) == 100:
                device_link_color = 'rgb(0,0,0)'

        return device_link_color, radius

    def get_thematic_settings(self, device_technology, device_type):
        """ Get device pl

            Parameters:
                - device_technology (<class 'device.models.DeviceTechnology'>) - device technology object
                - ts_type (unicode) - thematic settings type i.e 'ping' or 'normal'

            Returns:
               - user_thematics (<class 'inventory.models.UserPingThematicSettings'>) - thematic settings object
        """

        user_thematics = None

        # thematic settings type i.e. 'ping' or 'normal'
        ts_type = self.request.GET.get('ts', 'normal')

        # current user
        try:
            current_user = UserProfile.objects.get(id=self.request.user.id)
        except Exception as e:
            return None

        # device technology
        device_technology = device_technology

         # device type
        device_technology = device_type

        # fetch thematic settings for current user

        if ts_type == "normal":
            try:
                user_thematics = UserThematicSettings.objects.get(user_profile=current_user,
                                                                  thematic_technology=device_technology,
                                                                  thematic_type=device_type)
            except Exception as e:
                return user_thematics

        elif ts_type == "ping":
            try:
                user_thematics = UserPingThematicSettings.objects.get(user_profile=current_user,
                                                                      thematic_technology=device_technology,
                                                                      thematic_type=device_type)
            except Exception as e:
                return user_thematics

        return user_thematics

    def get_performance_value(self,
                              perf_payload,
                              network_perf_data,
                              performance_perf_data,
                              service_perf_data,
                              inventory_perf_data,
                              status_perf_data,
                              utilization_perf_data,
                              ts_type):
        """ Get device pl
            Parameters:
                - perf_payload (dict) - performance payload dictionary
                                            {
                                                'device_service_name': u'radwin_uptime',
                                                'machine_name': u'default',
                                                'freeze_time': '0',
                                                'device_service_data_source': u'uptime',
                                                'device_name': u'1'
                                            }
                - ts_type (unicode) - thematic settings type i.e 'ping' or 'normal'
            Returns:
                - performance_value (unicode) - performance value, e.g. 6.0082333333
        """

        # device name
        device_name = perf_payload['device_name']

        # machine name
        machine_name = perf_payload['machine_name']

        # freeze time
        freeze_time = perf_payload['freeze_time']

        # service name
        device_service_name = perf_payload['device_service_name']

        # service data source
        device_service_data_source = perf_payload['device_service_data_source']

        # performance value
        performance_value = None

        end_time = int(freeze_time) / 1000
        start_time = end_time - 300

        try:
            if ts_type == "normal":
                if "_invent" in device_service_name:
                    if int(freeze_time):

                        performance_value = PerformanceInventory.objects.filter(device_name=device_name,
                                                                                service_name=device_service_name,
                                                                                data_source=device_service_data_source,
                                                                                sys_timestamp__gte=start_time,
                                                                                sys_timestamp__lte=end_time
                        ).values('current_value').order_by().using(alias=machine_name)

                    else:
                        performance_value = [d for d in inventory_perf_data if d['device_name'] == device_name and
                                             d['service_name'] == device_service_name and
                                             d['data_source'] == device_service_data_source]

                elif "_status" in device_service_name:
                    if int(freeze_time):
                        performance_value = [d for d in performance_perf_data if d['device_name'] == device_name and
                                             d['service_name'] == device_service_name and
                                             d['data_source'] == device_service_data_source and
                                             start_time <= d['sys_timestamp'] <= end_time]

                    else:
                        performance_value = [d for d in status_perf_data if d['device_name'] == device_name and
                                             d['service_name'] == device_service_name and
                                             d['data_source'] == device_service_data_source]

                elif "_kpi" in device_service_name:
                    if int(freeze_time):
                        performance_value = Utilization.objects.filter(device_name=device_name,
                                                                      service_name=device_service_name,
                                                                      data_source=device_service_data_source,
                                                                      sys_timestamp__gte=start_time,
                                                                      sys_timestamp__lte=end_time
                        ).values('current_value').order_by().using(alias=machine_name)

                    else:
                        performance_value = [d for d in utilization_perf_data if d['device_name'] == device_name and
                                             d['service_name'] == device_service_name and
                                             d['data_source'] == device_service_data_source]
                else:
                    if int(freeze_time):
                        performance_value = PerformanceService.objects.filter(device_name=device_name,
                                                                              service_name=device_service_name,
                                                                              data_source=device_service_data_source,
                                                                              sys_timestamp__gte=start_time,
                                                                              sys_timestamp__lte=end_time
                        ).values('current_value').order_by().using(alias=machine_name)

                    else:
                        performance_value = [d for d in service_perf_data if d['device_name'] == device_name and
                                             d['service_name'] == device_service_name and
                                             d['data_source'] == device_service_data_source]

            elif ts_type == "ping":
                if int(freeze_time):
                    performance_value = PerformanceNetwork.objects.filter(device_name=device_name,
                                                                          service_name=device_service_name,
                                                                          data_source=device_service_data_source,
                                                                          sys_timestamp__gte=start_time,
                                                                          sys_timestamp__lte=end_time
                        ).values('current_value').order_by().using(alias=machine_name)

                else:
                    performance_value = [d for d in network_perf_data if d['device_name'] == device_name and
                                         d['service_name'] == device_service_name and
                                         d['data_source'] == device_service_data_source]

            if performance_value and len(performance_value):
                performance_value = performance_value[0]['current_value']

        except Exception as e:
            return performance_value

        return performance_value


def remove_duplicate_dict_from_list(input_list=None):
    """ Remove duplicate dictionaries from list of dictionaries

        :Parameters:
            - 'input_list' (list) - list of dictionaries for e.g.
                                        [
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            },
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            },
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            }
                                        ]

        :Returns:
           - 'result_list' (list) - list of dictionaries containing unique dictionaries for e.g.
                                        [
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            }
                                        ]
    """

    # list of dictionaries to be returned as a result
    result_list = []

    # temporary set containing dictionaries values in tuples for e.g
    # set([((key, value), (key, value), (key, value)), ((key, value), (key, value), (key, value))]

    temp_set = set()

    # loop through input list (list of dictionaries which needs to be filtered)
    for d in input_list:
        # t is set of dictionary values tuple for e.g
        # ((key, value), (key, value), (key, value), (key, value))
        # (('City', u'Kolkata'), ('Antenna Height', 29.0), ('BH Circuit ID', u'COPF-571'), ('PE IP', u'192.168.216.37'))
        t = tuple(d.items())
        if t not in temp_set:
            # adding tuple 't' to 'temp_set'
            temp_set.add(t)
            # append dictionary 'd' to 'result_list'
            result_list.append(d)

    return result_list


## This function returns the latest l2 report url for given circuit id.
def getL2Report(request, item_id = None, type = None):

    result = {
        "message" : "No L2 Report",
        "success" : 0,
        "data" : []
    }

    try:
        if item_id and type == 'circuit':            
            circuit_instance = Circuit.objects.filter(alias=item_id)
        else:
            circuit_instance = item_id
        report_list = CircuitL2Report.objects.filter(type_id=circuit_instance).values()[:1]
        if len(report_list) > 0:
            file_url = report_list[0]['file_name']
            file_url_dict = {
                "url": "media/"+file_url
            }
            result['data'].append(file_url_dict)
            result['success'] = 1
            result['message'] = "L2 report fetched successfully"
    except Exception, e:
        logger.exception(e.message)
    return HttpResponse(json.dumps(result))


class UpdateMaintenanceStatus(View):
    """ Update Maintenance Status of Base Station

        Parameters:
            - bs_id (unicode) - base station id for e.g. 1
            - maintenance_status (unicode) - maintenance status i.e. 'Yes' or 'No'
        URL:
            - "/network_maps/update_maintenance_status/?bs_id=1&maintenance_status=Yes"

    """

    def get(self, request):

        # get base station id's list
        bs_id = self.request.GET.get('bs_id', None)

        # get maintenance status
        maintenance_status = self.request.GET.get('maintenance_status', None)

        # result dictionary which needs to be returned as an output of api
        result = {
            "success": 0,
            "message": "Failed to update maintenance status.",
            "data": {}
        }

        if bs_id and maintenance_status:
            # get base station
            try:
                base_station = BaseStation.objects.get(pk=int(bs_id))

                # update maintenance status
                base_station.maintenance_status = maintenance_status
                base_station.save()

                # set result success bit to 1
                result['success'] = 1

                # update result message
                result['message'] = "Successfully update maintenance status."

                # update result data
                result['data']['bs_id'] = bs_id
                result['data']['maintenance_status'] = maintenance_status

                if str(maintenance_status) == 'Yes':
                    result['data']['icon'] = 'static/img/icons/bs_red.png'
                elif str(maintenance_status) == 'No':
                    result['data']['icon'] = 'static/img/icons/bs_black.png'
                else:
                    pass
            except Exception as e:
                pass

        return HttpResponse(json.dumps(result))


class GISStaticInfo(View):
    """ GIS Inventory performance data

        Parameters:
            - base_stations (unicode) - list of base stations in form of unicode i.e. [1, 2, 3, 4]
            - ts (unicode) - thematic service type i.e. ping/normal
            - freeze_time (unicode) - freeze time for e.g. 0

        URL:
            - "/network_maps/static_info/?base_stations=[47]&ts=normal&freeze_time=0"

        Returns:
           - inventory (list) - list of dictionaries containing static info for e.g.
                    {
                        "sector_configured_on_devices": "10.172.71.4|10.172.71.5|10.172.71.22|10.172.71.4|10.172.71.23|\
                        10.172.71.12|10.172.71.5|10.199.210.2|10.199.210.17|10.199.210.4|10.199.210.3|10.199.210.20|\
                        10.199.210.16|10.199.210.19|10.199.210.18",
                        "name": "minto_park_kol_wes",
                        "circuit_ids": "091KOLK623006743276|091KOLK030007674156|3331178768|091KOLK030004824159|\
                        33100128175|091KOLK623006075808|091KOLK623008941619|3331183538",
                        "sector_ss_vendor": "Telisma|Telisma|Telisma|Telisma|Cambium|Cambium|Cambium",
                        "sector_ss_technology": "WiMAX|WiMAX|WiMAX|WiMAX|PMP|PMP|PMP",
                        "alias": "Minto Park",
                        "sector_planned_frequencies": "NA|3396.0|3366|3366.0|3316|3316.0|NA|3380.0|5845|5840.0|5865|\
                        5860.0|5835|5835.0",
                        "data": {
                            "markerUrl": "static/img/icons/bs_black.png",
                            "state": "West Bengal",
                            "antenna_height": 0,
                            "vendor": null,
                            "city": "Kolkata",
                            "lat": 22.538889,
                            "maintenance_status": "No",
                            "lon": 88.355,
                            "param": {
                                "sector": [
                                    {
                                        "orientation": "Cross",
                                        "sector_id": 102,
                                        "color": "",
                                        "circuit_id": null,
                                        "polled_frequency": "3396",
                                        "frequency": "3396.0",
                                        "radius": 0,
                                        "perf_value": [],
                                        "perf_page_url": "/performance/network_live/10178/",
                                        "technology": "WiMAX",
                                        "beam_width": 60,
                                        "ss_info_list": [
                                            {
                                                "show": 0,
                                                "name": "base_station_alias",
                                                "value": "",
                                                "title": "Base Station Name"
                                            },
                                            {
                                                "show": 1,
                                                "name": "cktid",
                                                "value": "",
                                                "title": "Circuit ID"
                                            },
                                            {
                                                "show": 1,
                                                "name": "customer_alias",
                                                "value": "",
                                                "title": "Customer Name"
                                            },
                                            {
                                                "show": 1,
                                                "name": "ss_ip",
                                                "value": "",
                                                "title": "SS IP"
                                            },
                                            {
                                                "show": 1,
                                                "name": "pe_ip",
                                                "value": "",
                                                "title": "PE IP"
                                            },
                                            {
                                                "show": 1,
                                                "name": "qos_bandwidth",
                                                "value": "",
                                                "title": "QOS(BW)"
                                            },
                                            {
                                                "show": 1,
                                                "name": "antenna_height",
                                                "value": "",
                                                "title": "Antenna Height"
                                            },
                                            {
                                                "show": 1,
                                                "name": "polarisation",
                                                "value": "",
                                                "title": "Polarisation"
                                            },
                                            {
                                                "show": 1,
                                                "name": "mount_type",
                                                "value": "",
                                                "title": "SS MountType"
                                            },
                                            {
                                                "show": 1,
                                                "name": "antenna_type",
                                                "value": "",
                                                "title": "Antenna Type"
                                            },
                                            {
                                                "show": 1,
                                                "name": "cable_length",
                                                "value": "",
                                                "title": "Cable Length"
                                            },
                                            {
                                                "show": 1,
                                                "name": "ethernet_extender",
                                                "value": "",
                                                "title": "Ethernet Extender"
                                            },
                                            {
                                                "show": 1,
                                                "name": "building_height",
                                                "value": "",
                                                "title": "Building Height"
                                            },
                                            {
                                                "show": 1,
                                                "name": "tower_height",
                                                "value": "",
                                                "title": "tower_height"
                                            },
                                            {
                                                "show": 1,
                                                "name": "ss_technology",
                                                "value": "",
                                                "title": "Technology"
                                            },
                                            {
                                                "show": 1,
                                                "name": "lat_lon",
                                                "value": "",
                                                "title": "Lat, Long"
                                            },
                                            {
                                                "show": 1,
                                                "name": "customer_address",
                                                "value": "",
                                                "title": "Customer Address"
                                            },
                                            {
                                                "show": 1,
                                                "name": "alias",
                                                "value": "",
                                                "title": "Alias"
                                            },
                                            {
                                                "show": 1,
                                                "name": "dl_rssi_during_acceptance",
                                                "value": "",
                                                "title": "RSSI During Acceptance"
                                            },
                                            {
                                                "show": 1,
                                                "name": "date_of_acceptance",
                                                "value": "",
                                                "title": "Date of Acceptance"
                                            }
                                        ],
                                        "sector_configured_on": "10.172.71.4",
                                        "device_info": [
                                            {
                                                "show": 0,
                                                "name": "device_name",
                                                "value": "00:0A:10:09:05:43",
                                                "title": "Device Name"
                                            },
                                            {
                                                "show": 0,
                                                "name": "device_id",
                                                "value": 10178,
                                                "title": "Device ID"
                                            },
                                            {
                                                "show": 0,
                                                "name": "device_mac",
                                                "value": "NA",
                                                "title": "Device MAC"
                                            }
                                        ],
                                        "azimuth_angle": 20,
                                        "pl": "0",
                                        "sector_configured_on_device": "10178",
                                        "info": [],
                                        "vendor": "Telisma",
                                        "sub_station": [],
                                        "planned_frequency": "NA",
                                        "antenna_height": 38,
                                        "inventory_url": "/device/10178/",
                                        "item_index": 0,
                                        "markerUrl": "media/uploaded/icons/2014/09/25/Wimax-IDU.png"
                                    }
                                ]
                            }
                        "id": 7
                    }

    """

    def get(self, request):

        # get base stations id's list
        bs_ids = eval(str(self.request.GET.get('base_stations', None)))

        # type of thematic settings needs to be fetched
        ts_type = self.request.GET.get('ts', 'normal')

        # freeze time (data fetched from freeze time to latest time)
        freeze_time = self.request.GET.get('freeze_time', '0')

        if not freeze_time:
            freeze_time = '0'

        bs_inventory = {}

        # Create instance of 'InventoryUtilsGateway' class
        inventory_utils = InventoryUtilsGateway()

        
        # loop through all base stations having id's in bs_ids list
        for bs_id in bs_ids:
            pps_alarm_flag = False
            try:
                
                devices_ip_address_list = list()
                
                # get formatted bs inventory
                bs_inventory = prepare_raw_result_v2(nocout_utils.get_maps_initial_data_noncached(bs_id=[str(bs_id)]))[0]
                
                # if EXCLAMATION_NEEDED flag is set to False from settings.py then set has_pps_alarm to 0
                if EXCLAMATION_NEEDED:
                    try:
                        pps_alarm_flag = bs_inventory.get('has_pps_alarm', 0)
                    except Exception, e:
                        pps_alarm_flag = False

            
            
                # if bs has a pps alarm then change it's icon
                if pps_alarm_flag: 
                    bs_inventory['icon_url'] = 'static/img/icons/bs_exclamation.png'
                    
                # ******************************** GET DEVICE MACHINE MAPPING (START) ****************************
                bh_device_ip = bs_inventory.get('bh_device_ip')
                
                try:
                    bh_device = Device.objects.get(ip_address=bh_device_ip)
                except Exception, e:
                    bh_device = None

                # append backhaul device ip address
                if bh_device_ip and bh_device:
                    devices_ip_address_list.append(bh_device_ip)

                # Append Sector & SS IP Address to 'devices_ip_address_list' list
                try:
                    ips_string = bs_inventory.get('sector_configured_on_devices')
                    ips_list = filter(None, ips_string.split('|'))
                    devices_ip_address_list.extend(ips_list)
                except Exception, e:
                    for sector in bs_inventory['sectors']:
                        if sector['ip_address'] and sector['ip_address'] not in devices_ip_address_list:
                            devices_ip_address_list.append(sector['ip_address'])

                        for sub_station in sector['sub_stations']:
                            if sub_station['ip_address'] and sub_station['ip_address'] not in devices_ip_address_list:
                                devices_ip_address_list.append(sub_station['ip_address'])

                bs_devices = list(Device.objects.filter(
                    ip_address__in=devices_ip_address_list
                ).values(
                    'device_name',
                    'machine__name',
                    'device_technology',
                    'device_type',
                    'ip_address'
                ))

                ip_address_mapped_dict = nocout_utils.create_specific_key_dict(bs_devices, 'ip_address')

                # thematic settings type i.e. 'ping' or 'normal'
                ts_type = self.request.GET.get('ts', 'normal')

                tech_list = list(set(bs_inventory.get('tech_str').split('|')))

                # current user
                try:
                    current_user = UserProfile.objects.get(id=self.request.user.id)
                except Exception as e:
                    current_user = None

                machine_dict = inventory_utils.prepare_machines(bs_devices, 'machine__name')
                
                complete_performance_obj = get_complete_performance(
                    machine_dict=machine_dict,
                    tech_list=tech_list,
                    current_user=current_user,
                    ts_type=ts_type
                )

                if complete_performance_obj:
                    tech_wise_thematic = complete_performance_obj.get('tech_wise_thematic')
                    complete_performance = complete_performance_obj.get('complete_performance')
                else:
                    tech_wise_thematic = None
                    complete_performance = {
                        'network_perf_data': list(),
                        'performance_perf_data': list(),
                        'service_perf_data': list(),
                        'inventory_perf_data': list(),
                        'status_perf_data': list(),
                        'utilization_perf_data': list()
                    }

                # ********************************* BACKHAUL PERF INFO (START) ***********************************
                if bh_device_ip and bh_device:
                    backhaul_data = self.get_backhaul_info(bh_device, complete_performance['network_perf_data'])
                    bs_inventory['bh_polled_info'] = backhaul_data['bh_info'] if 'bh_info' in backhaul_data else []
                    bs_inventory['bh_pl'] = backhaul_data['bh_pl'] if 'bh_pl' in backhaul_data else "NA"
                    bs_inventory['bhSeverity'] = backhaul_data['bhSeverity'] if 'bhSeverity' in backhaul_data else "NA"

                # ********************************** BACKHAUL PERF INFO (END) ************************************

                # ******************************** GET DEVICE MACHINE MAPPING (END) ******************************

                for sector in bs_inventory['sectors']:
                    # get sector
                    try:
                        sector_obj = Sector.objects.get(id=sector['id'])
                    except Exception as e:
                        sector_obj = None

                    try:
                        sector_device = ip_address_mapped_dict[sector['ip_address']][0]
                    except Exception, e:
                        sector_device = [d for d in bs_devices if d['ip_address'] == sector['ip_address']][0]


                    try:
                        sector_configured_on_type = DeviceType.objects.get(id=sector_device['device_type'])
                    except Exception as e:
                        sector_configured_on_type = None

                    try:
                        sector_configured_on_tech = DeviceTechnology.objects.get(id=sector_device['device_technology'])
                    except Exception as e:
                        sector_configured_on_tech = None

                    # thematic settings for current user
                    try:
                        if tech_wise_thematic:
                            user_thematics = tech_wise_thematic[sector.get('technology')]
                            if user_thematics:
                                user_thematics = user_thematics[0]
                            else:
                                user_thematics = self.get_thematic_settings(sector_configured_on_tech, None)
                        else:
                            user_thematics = self.get_thematic_settings(sector_configured_on_tech, None)
                    except Exception, e:
                        user_thematics = self.get_thematic_settings(sector_configured_on_tech, None)

                    # service & data source
                    service = ""
                    data_source = ""
                    try:
                        if ts_type == "normal":
                            service = user_thematics.thematic_template.threshold_template.live_polling_template.\
                                service.name
                            data_source = user_thematics.thematic_template.threshold_template.live_polling_template.\
                                data_source.name
                        elif ts_type == "ping":
                            service = user_thematics.thematic_template.service
                            data_source = user_thematics.thematic_template.data_source
                    except Exception as e:
                        pass

                    sector['perf_value'] = ''
                    sector['pl'] = ''
                    sector['rta'] = ''
                    sector['pl_timestamp'] = ''

                    if service and data_source:
                        # performance value
                        perf_payload = {
                            'device_name': sector_device['device_name'],
                            'machine_name': sector_device['machine__name'],
                            'freeze_time': freeze_time,
                            'device_service_name': service,
                            'device_service_data_source': data_source
                        }

                        sector_extra_info = self.get_extra_info(
                            perf_payload,
                            freeze_time,
                            ts_type,
                            sector_configured_on_type,
                            user_thematics,
                            complete_performance,
                            sector_obj
                        )

                        sector['markerUrl'] = sector_extra_info['markerUrl']
                        sector['radius'] = sector_extra_info['radius']
                        sector['perf_value'] = sector_extra_info['perf_value']
                        sector['pl'] = sector_extra_info['pl']
                        sector['rta'] = sector_extra_info['rta']
                        sector['pl_timestamp'] = sector_extra_info['pl_timestamp']
                        sector['color'] = sector_extra_info['color']
                        sector['polled_frequency'] = sector_extra_info['polled_frequency']

                    for sub_station in sector['sub_stations']:
                            try:
                                substation_device = ip_address_mapped_dict[sub_station['ip_address']][0]
                            except Exception, e:
                                substation_device = [d for d in bs_devices if d['ip_address'] == sub_station['ip_address']][0]

                            try:
                                substation_device_type = DeviceType.objects.get(id=substation_device['device_type'])
                            except Exception as e:
                                substation_device_type = None

                            try:
                                substation_device_tech = DeviceTechnology.objects.get(id=substation_device['device_technology'])
                            except Exception as e:
                                substation_device_tech = None

                            # thematic settings for current user
                            try:
                                if tech_wise_thematic:
                                    fetched_thematics = tech_wise_thematic[sub_station.get('device_tech')]
                                    device_type = sub_station.get('device_tech')
                                    user_thematics = None
                                    if fetched_thematics:
                                        if device_type:
                                            for thematics in fetched_thematics:
                                                try:
                                                    thematic_device_type = thematics.thematic_type.name
                                                except Exception, e:
                                                    thematic_device_type = ''
                                                if device_type == thematic_device_type:
                                                    user_thematics = [thematics]
                                                    break

                                    if user_thematics:
                                        user_thematics = user_thematics[0]
                                    else:
                                        user_thematics = self.get_thematic_settings(substation_device_tech, substation_device_type)
                                else:
                                    user_thematics = self.get_thematic_settings(substation_device_tech, substation_device_type)
                            except Exception, e:
                                user_thematics = self.get_thematic_settings(substation_device_tech, substation_device_type)

                            # service & data source
                            service = ""
                            data_source = ""
                            try:
                                if ts_type == "normal":
                                    service = user_thematics.thematic_template.threshold_template.live_polling_template.\
                                        service.name
                                    data_source = user_thematics.thematic_template.threshold_template.\
                                        live_polling_template.data_source.name
                                elif ts_type == "ping":
                                    service = user_thematics.thematic_template.service
                                    data_source = user_thematics.thematic_template.data_source
                            except Exception as e:
                                pass

                            sub_station['perf_value'] = ''
                            sub_station['pl'] = ''
                            sub_station['pl_timestamp'] = ''
                            sub_station['rta'] = ''

                            if service and data_source:
                                # performance value
                                perf_payload = {
                                    'device_name': substation_device['device_name'],
                                    'machine_name': substation_device['machine__name'],
                                    'freeze_time': freeze_time,
                                    'device_service_name': service,
                                    'device_service_data_source': data_source
                                }

                                substation_extra_info = self.get_extra_info(
                                    perf_payload,
                                    freeze_time,
                                    ts_type,
                                    substation_device_type,
                                    user_thematics,
                                    complete_performance
                                )

                                sub_station['markerUrl'] = substation_extra_info['markerUrl']

                                if substation_extra_info['color']:
                                    sub_station['link_color'] = substation_extra_info['color']
                                else:
                                    sub_station['link_color'] = sector_extra_info['color']

                                sub_station['perf_value'] = substation_extra_info['perf_value']
                                sub_station['pl'] = substation_extra_info['pl']
                                sub_station['pl_timestamp'] = substation_extra_info['pl_timestamp']
                                sub_station['rta'] = substation_extra_info['rta']
            except Exception as e:
                pass

        return HttpResponse(json.dumps(bs_inventory))

    def get_backhaul_info(self, bh_device, network_perf_data):
        """ Get Sector performance info

            Parameters:
                - bh_device (<class 'device.models.Device'>) - backhaul device for e.g. 10.175.102.3

            Returns:
               - backhaul_data (dictionary) - dictionary containing backhaul performance data
                                                {
                                                    'bhSeverity': 'NA',
                                                    'bh_info': [
                                                        {
                                                            'title': 'PacketDrop',
                                                            'name': 'pl',
                                                            'value': 'NA',
                                                            'show': 1
                                                        },
                                                        {
                                                            'title': 'Latency',
                                                            'name': 'rta',
                                                            'value': 'NA',
                                                            'show': 1
                                                        }
                                                    ]
                                                }
        """

        # backhaul data
        backhaul_data = dict()
        backhaul_data['bh_info'] = list()
        backhaul_data['bhSeverity'] = "NA"
        backhaul_data['bh_pl'] = "NA"

        # pl
        try:
            backhaul_data['bh_pl'] = [d for d in network_perf_data if d['device_name'] == bh_device.device_name and
                                d['data_source'] == 'pl'][0]['current_value']
        except Exception as e:
            backhaul_data['bh_pl'] = "NA"

        # bh severity
        try:
            backhaul_data['bhSeverity'] = [d for d in network_perf_data if d['device_name'] == bh_device.device_name and
                                           d['data_source'] == 'pl'][0]['severity']
        except Exception as e:
            backhaul_data['bhSeverity'] = 'unknown'

        return backhaul_data

    def get_extra_info(self,
                       perf_payload,
                       freeze_time,
                       ts_type,
                       device_type=None,
                       user_thematics=None,
                       complete_performance=None,
                       sector=None):
        """ Get device polled frequency
            Parameters:
                - perf_payload (dict) - dictionary containing performance payload for e.g.
                                        {
                                            'device_service_name': u'radwin_uas',
                                            'machine_name': u'vrfprv',
                                            'freeze_time': u'0',
                                            'device_service_data_source': u'uas',
                                            'device_name': u'10740'
                                        }

                - freeze_time (unicode) - freeze time for e.g. 0
                - ts_type (unicode) - thematic service type i.e. ping/normal
                - device_type (<class 'device.models.DeviceType'>) - device type for e.g StarmaxSS
                - user_thematics (<class 'inventory.models.UserThematicSettings'>) - user thematics object
                - complete_performance (dict) - dictionary containing complete performance info
                - sector (<class 'inventory.models.Sector'>) - sector object for e.g  091kolk623005919183
            Returns:
               - device_frequency (str) - device frequency, e.g. "34525"
        """

        # result
        result = dict()

        # performance value
        performance_value = None

        network_perf_data = complete_performance['network_perf_data']
        performance_perf_data = complete_performance['performance_perf_data']
        service_perf_data = complete_performance['service_perf_data']
        inventory_perf_data = complete_performance['inventory_perf_data']
        status_perf_data = complete_performance['status_perf_data']
        utilization_perf_data = complete_performance['utilization_perf_data']

        # device frequency
        device_frequency = self.get_device_polled_frequency(
            perf_payload['device_name'],
            perf_payload['machine_name'],
            freeze_time,
            performance_perf_data,
            inventory_perf_data,
            sector
        )

        # update device frequency
        result['polled_frequency'] = device_frequency

        # pl result
        pl_result = self.get_device_pl(
            perf_payload['device_name'],
            perf_payload['machine_name'],
            network_perf_data,
            freeze_time
        )
        # device pl
        device_pl = pl_result[0]

        # device rta
        device_rta = self.get_device_rta(
            perf_payload['device_name'],
            perf_payload['machine_name'],
            network_perf_data,
            freeze_time
        )

        # update device pl
        result['pl'] = device_pl

        # update device rta
        result['rta'] = device_rta

        # device link/frequency color
        device_link_color = self.get_frequency_color_and_radius(device_frequency, device_pl)[0]

        # update performance color
        result['color'] = device_link_color

        # radius
        radius = self.get_frequency_color_and_radius(device_frequency, device_pl)[1]

        result['radius'] = radius

        # pl timstamp
        pl_timestamp = ""
        try:
            pl_timestamp = datetime.datetime.fromtimestamp(pl_result[1]).strftime('%d-%b-%Y at %H:%M:%S')
        except Exception as e:
            pass

        # update device pl timstamp
        result['pl_timestamp'] = pl_timestamp

        if device_pl != "100":
            performance_value = self.get_performance_value(
                perf_payload,
                network_perf_data,
                performance_perf_data,
                service_perf_data,
                inventory_perf_data,
                status_perf_data,
                utilization_perf_data,
                ts_type
            )
            result['perf_value'] = performance_value
        else:
            result['perf_value'] = ""

        if user_thematics:
            # icon
            icon = ""

            try:
                icon = "media/" + str(device_type.device_icon)
            except Exception as e:
                pass

            if device_pl != "100":
                # fetch icon settings for thematics as per thematic type selected i.e. 'ping' or 'normal'
                th_icon_settings = ""
                try:
                    th_icon_settings = user_thematics.thematic_template.icon_settings
                except Exception as e:
                    pass

                # fetch thematic ranges as per thematic type selected i.e. 'ping' or 'normal'
                th_ranges = ""
                try:
                    if ts_type == "ping":
                        th_ranges = user_thematics.thematic_template
                    elif ts_type == "normal":
                        th_ranges = user_thematics.thematic_template.threshold_template
                    else:
                        pass
                except Exception as e:
                    pass

                # fetch service type if 'ts_type' is "normal"
                service_type = ""
                try:
                    if ts_type == "normal":
                        service_type = user_thematics.thematic_template.threshold_template.service_type
                except Exception as e:
                    pass

                # comparing threshold values to get icon
                try:
                    if performance_value and len(performance_value):
                        # get appropriate icon
                        if ts_type == "normal":
                            if service_type == "INT":
                                value = ast.literal_eval(str(performance_value))
                                icon = self.get_icon_for_numeric_service(th_ranges, th_icon_settings, value)
                            elif service_type == "STR":
                                value = str(performance_value)
                                icon = self.get_icon_for_string_service(th_ranges, th_icon_settings, value)
                            else:
                                pass
                        elif ts_type == "ping":
                            value = ast.literal_eval(str(performance_value))
                            icon = self.get_icon_for_numeric_service(th_ranges, th_icon_settings, value)
                        else:
                            pass
                except Exception as e:
                    logger.exception(e)

            result['markerUrl'] = icon

        return result

    def get_icon_for_numeric_service(self, th_ranges=None, th_icon_settings=None, value=None):
        """
            Get device icon corresponding to fetched performance value
            Parameters:
                - th_ranges (<class 'inventory.models.ThresholdConfiguration'>) - threshold configuration object
                                                                                  for e.g. Wimax DL RSSI
                - th_icon_settings (unicode) - icon settings in json format for e.g.
                        [
                            {
                                'icon_settings1': u'uploaded/icons/2014-09-26/2014-09-26-11-56-11_SM-GIF.gif'
                            },
                            {
                                'icon_settings2': u'uploaded/icons/2014-10-26/2014-10-26-14-59-40_SM-Red.png'
                            },
                            {
                                'icon_settings3': u'uploaded/icons/2014-09-25/2014-09-25-13-59-00_P2P-Green.png'
                            }
                        ]
                - value (str) - performance value for e.g "-57"

            Returns:
                - icon (str) - icon location i.e "media/uploaded/icons/2014/09/18/wifi3.png"
        """

        # default image to be loaded
        image_partial = "icons/mobilephonetower10.png"

        if th_ranges and th_icon_settings and len(str(value)):
            compare_this = float(value)
            for i in range(1, 11):
                try:
                    compare_to_start = float(eval("th_ranges.range%d_start" % i))
                    compare_to_end = float(eval("th_ranges.range%d_end" % i))
                    icon_settings = eval(th_icon_settings)
                    if compare_to_start <= compare_this <= compare_to_end:
                        icon_key = "icon_settings{0}".format(i)
                        for icon_setting in icon_settings:
                            if icon_key in icon_setting.keys():
                                image_partial = str(icon_setting[icon_key])
                                break
                except Exception as e:
                    continue

        # image url
        img_url = "media/" + str(image_partial) if "uploaded" in str(
            image_partial) else "static/img/" + str(image_partial)

        # icon to be send in response
        icon = str(img_url)

        return icon

    def get_icon_for_string_service(self, th_ranges=None, th_icon_settings=None, value=None):
        """
            Get device icon corresponding to fetched performance value
            Parameters:
                - th_ranges (<class 'inventory.models.ThresholdConfiguration'>) - threshold configuration object
                                                                                  for e.g. Wimax DL RSSI
                - th_icon_settings (unicode) - icon settings in json format for e.g.
                        [
                            {
                                'icon_settings1': u'uploaded/icons/2014-09-26/2014-09-26-11-56-11_SM-GIF.gif'
                            },
                            {
                                'icon_settings2': u'uploaded/icons/2014-10-26/2014-10-26-14-59-40_SM-Red.png'
                            },
                            {
                                'icon_settings3': u'uploaded/icons/2014-09-25/2014-09-25-13-59-00_P2P-Green.png'
                            }
                        ]
                - value (str) - performance value for e.g "-57"

            Returns:
                - icon (str) - icon location i.e "media/uploaded/icons/2014/09/18/wifi3.png"
        """

        # default image to be loaded
        image_partial = "icons/mobilephonetower10.png"
        if th_ranges and th_icon_settings and value:
            compare_this = ''.join(e for e in value if e.isalnum())
            for i in range(1, 11):
                try:
                    eval_this = eval("th_ranges.range%d_start" % i)
                    compare_to = ''.join(e for e in eval_this if e.isalnum())
                    icon_settings = eval(th_icon_settings)
                    if compare_this.strip().lower() == compare_to.strip().lower():
                        icon_key = "icon_settings{0}".format(i)
                        for icon_setting in icon_settings:
                            if icon_key in icon_setting.keys():
                                image_partial = str(icon_setting[icon_key])
                                break
                except Exception as e:
                    continue

        # image url
        img_url = "media/" + str(image_partial) if "uploaded" in str(
            image_partial) else "static/img/" + str(image_partial)

        # icon to be send in response
        icon = str(img_url)

        return icon

    def get_device_polled_frequency(self,
                                    device_name,
                                    machine_name,
                                    freeze_time,
                                    performance_perf_data,
                                    inventory_perf_data,
                                    sector=None,
                                    device_type=None):
        """ Get device polled frequency
            Parameters:
                - device_name (unicode) - device name
                - machine_name (unicode) - machine name
                - freeze_time (str) - freeze time i.e. '0'
                - sector (<class 'inventory.models.Sector'>) - sector object
                - device_type (<class 'device.models.DeviceType'>) - device type object
            Returns:
               - device_frequency (str) - device frequency, e.g. "34525"
        """

        # device frequency
        device_frequency = ""
        try:
            port_based_frequency = False
            service_name = 'wimax_pmp1_frequency_invent'
            if sector:
                if sector.sector_configured_on_port and sector.sector_configured_on_port.name:
                    port_based_frequency = True
                    if 'pmp1' in sector.sector_configured_on_port.name.strip().lower():
                        service_name = 'wimax_pmp1_frequency_invent'
                    elif 'pmp2' in sector.sector_configured_on_port.name.strip().lower():
                        service_name = 'wimax_pmp2_frequency_invent'
                    else:
                        port_based_frequency = False

            #for SS services
            frequency_service = None
            if device_type:
                frequency_service = device_type.service.filter(name__icontains='frequency')

            if port_based_frequency:
                device_frequency = [d for d in inventory_perf_data if d['device_name'] == device_name and
                                    d['service_name'] == service_name and
                                    d['data_source'] == 'frequency']

            elif frequency_service:
                service_name = frequency_service[0]['name']
                if "_invent" in service_name:
                    device_frequency = [d for d in inventory_perf_data if d['device_name'] == device_name and
                                        d['data_source'] == 'frequency']

                    device_frequency = [d for d in performance_perf_data if d['device_name'] == device_name and
                                        d['service_name'] == service_name and
                                        d['data_source'] == 'frequency']

            else:
                device_frequency = [d for d in inventory_perf_data if d['device_name'] == device_name and
                                    d['data_source'] == 'frequency']

            if device_frequency:
                try:
                    device_frequency = device_frequency[0]['current_value']
                except Exception as e:
                    logger.exception(e)
            else:
                device_frequency = ""
        except Exception as e:
            logger.exception(e)

        return device_frequency

    def get_device_pl(self, device_name, machine_name, network_perf_data, freeze_time):
        """ Get device pl
            Parameters:
                - device_name (unicode) - device name
                - machine_name (unicode) - machine name
                - freeze_time (str) - freeze time i.e. '0'
            Returns:
               - device_frequency (str) - device frequency, e.g. "34525"
        """

        # device packet loss
        device_pl = ""

        # pl timestamp
        pl_timestamp = ""

        end_time = float(freeze_time) / 1000
        start_time = end_time - 300

        try:
            if int(freeze_time):
                result = PerformanceNetwork.objects.filter(
                    device_name=device_name,
                    service_name='ping',
                    data_source='pl',
                    sys_timestamp__gte=start_time,
                    sys_timestamp__lte=end_time
                ).order_by().using(
                    alias=machine_name
                ).values('current_value', 'sys_timestamp')

            else:
                result = [d for d in network_perf_data if d['device_name'] == device_name and
                             d['service_name'] == 'ping' and
                             d['data_source'] == 'pl']
            if result:
                device_pl = result[0]['current_value']
                pl_timestamp = result[0]['sys_timestamp']
            else:
                device_pl = ""
                pl_timestamp = ""

        except Exception as e:
            logger.exception(e)

        return [device_pl, pl_timestamp]

    def get_device_rta(self,
                       device_name,
                       machine_name,
                       network_perf_data,
                       freeze_time):
        """ Get device rta
            Parameters:
                - device_name (unicode) - device name
                - machine_name (unicode) - machine name
                - freeze_time (str) - freeze time i.e. '0'
            Returns:
               - device_frequency (str) - device frequency, e.g. "34525"
        """

        # device packet loss
        device_rta = ""

        end_time = float(freeze_time) / 1000
        start_time = end_time - 300

        try:
            if int(freeze_time):
                device_rta = PerformanceNetwork.objects.filter(
                    device_name=device_name,
                    service_name='ping',
                    data_source='rta',
                    sys_timestamp__gte=start_time,
                    sys_timestamp__lte=end_time
                ).order_by().using(
                    alias=machine_name
                ).values('current_value')

            else:
                device_rta = [d for d in network_perf_data if d['device_name'] == device_name and
                             d['service_name'] == 'ping' and
                             d['data_source'] == 'rta']

            if device_rta:
                device_rta = device_rta[0]['current_value']
            else:
                device_rta = ""

        except Exception as e:
            logger.exception(e)

        return device_rta

    def get_frequency_color_and_radius(self, device_frequency, device_pl):
        """ Get device pl

            Parameters:
                - device_frequency (unicode) - device frequency, e.g 5830
                - device_pl (unicode) - device pl (packet loss) value, e.g. 4

            Returns:
                - device_link_color (unicode) - device link color, e.g. rgba(255,192,0,0.97)
                - radius (float) - radius, e.g 2.0
        """

        # device link color
        device_link_color = ""

        # radius
        radius = ""

        try:
            if len(device_frequency):
                corrected_dev_freq = device_frequency
                try:
                    chek_dev_freq = ast.literal_eval(device_frequency)
                    if int(chek_dev_freq) > 10:
                        corrected_dev_freq = chek_dev_freq
                except Exception as e:
                    pass

                device_frequency_objects = DeviceFrequency.objects.filter(value__icontains=str(corrected_dev_freq))
                device_frequency_color = DeviceFrequency.objects.filter(value__icontains=str(corrected_dev_freq)) \
                    .values_list('color_hex_value', flat=True)
                device_frequency_object = None
                if len(device_frequency_objects):
                    device_frequency_object = device_frequency_objects[0]
                radius = device_frequency_object.frequency_radius if (
                    device_frequency_object
                    and
                    device_frequency_object.frequency_radius
                ) else 0
                if len(device_frequency_color):
                    device_link_color = device_frequency_color[0]
            if len(device_pl) and int(ast.literal_eval(device_pl)) == 100:
                device_link_color = 'rgb(0,0,0)'
        except Exception as e:
            if len(device_pl) and int(ast.literal_eval(device_pl)) == 100:
                device_link_color = 'rgb(0,0,0)'

        return device_link_color, radius

    def get_thematic_settings(self, device_technology, device_type):
        """ Get device pl

            Parameters:
                - device_technology (<class 'device.models.DeviceTechnology'>) - device technology object
                - ts_type (unicode) - thematic settings type i.e 'ping' or 'normal'

            Returns:
               - user_thematics (<class 'inventory.models.UserPingThematicSettings'>) - thematic settings object
        """

        user_thematics = None

        # thematic settings type i.e. 'ping' or 'normal'
        ts_type = self.request.GET.get('ts', 'normal')

        if not device_technology:
            return user_thematics

        # current user
        try:
            current_user = UserProfile.objects.get(id=self.request.user.id)
        except Exception as e:
            return user_thematics

        # fetch thematic settings for current user
        if ts_type == "normal":
            if device_type:
                try:
                    user_thematics = UserThematicSettings.objects.get(
                        user_profile=current_user,
                        thematic_technology=device_technology,
                        thematic_type=device_type
                    )
                except Exception as e:
                    return user_thematics
            else:
                try:
                    user_thematics = UserThematicSettings.objects.filter(
                        user_profile=current_user,
                        thematic_technology=device_technology
                    )[0]
                except Exception as e:
                    return user_thematics

        elif ts_type == "ping":
            if device_type:
                try:
                    user_thematics = UserPingThematicSettings.objects.get(
                        user_profile=current_user,
                        thematic_technology=device_technology,
                        thematic_type=device_type
                    )
                except Exception as e:
                    return user_thematics
            else:
                try:
                    user_thematics = UserPingThematicSettings.objects.filter(
                        user_profile=current_user,
                        thematic_technology=device_technology
                    )[0]
                except Exception as e:
                    return user_thematics

        return user_thematics

    def get_performance_value(self,
                              perf_payload,
                              network_perf_data,
                              performance_perf_data,
                              service_perf_data,
                              inventory_perf_data,
                              status_perf_data,
                              utilization_perf_data,
                              ts_type):
        """ Get device pl
            Parameters:
                - perf_payload (dict) - performance payload dictionary
                                            {
                                                'device_service_name': u'radwin_uptime',
                                                'machine_name': u'default',
                                                'freeze_time': '0',
                                                'device_service_data_source': u'uptime',
                                                'device_name': u'1'
                                            }
                - ts_type (unicode) - thematic settings type i.e 'ping' or 'normal'
            Returns:
                - performance_value (unicode) - performance value, e.g. 6.0082333333
        """

        # device name
        device_name = perf_payload['device_name']

        # machine name
        machine_name = perf_payload['machine_name']

        # freeze time
        freeze_time = perf_payload['freeze_time']

        # service name
        device_service_name = perf_payload['device_service_name']

        # service data source
        device_service_data_source = perf_payload['device_service_data_source']

        # performance value
        performance_value = None

        end_time = int(freeze_time) / 1000
        start_time = end_time - 300

        try:
            if ts_type == "normal":
                if "_invent" in device_service_name:
                    if int(freeze_time):

                        performance_value = PerformanceInventory.objects.filter(
                            device_name=device_name,
                            service_name=device_service_name,
                            data_source=device_service_data_source,
                            sys_timestamp__gte=start_time,
                            sys_timestamp__lte=end_time
                        ).values('current_value').order_by().using(alias=machine_name)

                    else:
                        performance_value = [d for d in inventory_perf_data if d['device_name'] == device_name and
                                             d['service_name'] == device_service_name and
                                             d['data_source'] == device_service_data_source]

                elif "_status" in device_service_name:
                    if int(freeze_time):
                        performance_value = [d for d in performance_perf_data if d['device_name'] == device_name and
                                             d['service_name'] == device_service_name and
                                             d['data_source'] == device_service_data_source and
                                             start_time <= d['sys_timestamp'] <= end_time]

                    else:
                        performance_value = [d for d in status_perf_data if d['device_name'] == device_name and
                                             d['service_name'] == device_service_name and
                                             d['data_source'] == device_service_data_source]

                elif "_kpi" in device_service_name:
                    if int(freeze_time):
                        performance_value = Utilization.objects.filter(
                            device_name=device_name,
                            service_name=device_service_name,
                            data_source=device_service_data_source,
                            sys_timestamp__gte=start_time,
                            sys_timestamp__lte=end_time
                        ).values('current_value').order_by().using(alias=machine_name)

                    else:
                        performance_value = [d for d in utilization_perf_data if d['device_name'] == device_name and
                                             d['service_name'] == device_service_name and
                                             d['data_source'] == device_service_data_source]
                else:
                    if int(freeze_time):
                        performance_value = PerformanceService.objects.filter(
                            device_name=device_name,
                            service_name=device_service_name,
                            data_source=device_service_data_source,
                            sys_timestamp__gte=start_time,
                            sys_timestamp__lte=end_time
                        ).values('current_value').order_by().using(alias=machine_name)

                    else:
                        performance_value = [d for d in service_perf_data if d['device_name'] == device_name and
                                             d['service_name'] == device_service_name and
                                             d['data_source'] == device_service_data_source]

            elif ts_type == "ping":
                if int(freeze_time):
                    performance_value = PerformanceNetwork.objects.filter(
                        device_name=device_name,
                        service_name=device_service_name,
                        data_source=device_service_data_source,
                        sys_timestamp__gte=start_time,
                        sys_timestamp__lte=end_time
                    ).values('current_value').order_by().using(alias=machine_name)

                else:
                    performance_value = [d for d in network_perf_data if d['device_name'] == device_name and
                                         d['service_name'] == device_service_name and
                                         d['data_source'] == device_service_data_source]

            if performance_value and len(performance_value):
                performance_value = performance_value[0]['current_value']
            else:
                performance_value = ''
        except Exception as e:
            return performance_value

        return performance_value


class GISPerfInfo(View):
    """ Get device performance info

        Parameters:
            - device_id (unicode) - device id for e.g 10170
            - device_pl (unicode) - device pl value for e.g. 0

        URL:
            - "/network_maps/perf_info/?device_id=11254&device_pl=0"

        Returns:
            - perf_info (list) - list of dictionaries containing device performance info for e.g.
                    [
                        {
                            "url": "performance/service/ping/service_data_source/pl/device/10170?start_date=&end_date=",
                            "show": 1,
                            "name": "pl",
                            "value": "0",
                            "title": "Packet Drop"
                        },
                        {
                            "url": "performance/service/ping/service_data_source/rta/device/10170?start_date=&end_date=",
                            "show": 1,
                            "name": "rta",
                            "value": 45.05,
                            "title": "Latency"
                        },
                        {
                            "url": "performance/service/wimax_bs_temperature_acb/service_data_source/acb_temp/device/
                            10170?start_date=&end_date=",
                            "show": true,
                            "name": "wimax_bs_temperature_acb_acb_temp",
                            "value": "35",
                            "title": "IDU ACB Temperature
                    [ ACB Temperature ]"
                        },
                        {
                            "url": "performance/service/wimax_bs_temperature_fan/service_data_source/fan_temp/device/
                            10170?start_date=&end_date=",
                            "show": true,
                            "name": "wimax_bs_temperature_fan_fan_temp",
                            "value": "29",
                            "title": "IDU FAN Temperature
                    [ FAN Temperature ]"
                        },
                        {
                            "url": "performance/service/wimax_bs_uptime/service_data_source/uptime/device/
                            10170?start_date=&end_date=",
                            "show": true,
                            "name": "wimax_bs_uptime_uptime",
                            "value": "2.0 weeks, 22.0 hours, 24.0 minutes, 48.0 seconds",
                            "title": "BS Uptime
                    [ Device Uptime ]"
                        },
                        {
                            "url": "performance/service/wimax_pmp1_dl_util_bgp/service_data_source/pmp1_dl_util/device/
                            10170?start_date=&end_date=",
                            "show": true,
                            "name": "wimax_pmp1_dl_util_bgp_pmp1_dl_util",
                            "value": "1.475359",
                            "title": "wimax pmp1 dl utilization
                    [ PMP1 DL Utilisation ]"
                        },
                        {
                            "url": "performance/service/wimax_pmp1_ul_util_bgp/service_data_source/pmp1_ul_util/device/
                            10170?start_date=&end_date=",
                            "show": true,
                            "name": "wimax_pmp1_ul_util_bgp_pmp1_ul_util",
                            "value": "0.367221",
                            "title": "wimax pmp1 ul utilization
                    [ PMP1 UL Utilisation ]"
                        },
                        {
                            "url": "performance/service/wimax_pmp2_dl_util_bgp/service_data_source/pmp2_dl_util/device/
                            10170?start_date=&end_date=",
                            "show": true,
                            "name": "wimax_pmp2_dl_util_bgp_pmp2_dl_util",
                            "value": "0.134645",
                            "title": "wimax pmp2 dl utilization
                    [ PMP2 DL Utilisation ]"
                        }
                    ]
    """

    def get(self, request):

        # get device id
        device_id = self.request.GET.get('device_id', None)

        # get device pl
        device_pl = self.request.GET.get('device_pl', None)

        # perf info list
        perf_info = list()

        # get device
        try:
            device = Device.objects.get(id=int(device_id))
        except Exception as e:
            device = None

        if device:

            processed = {}

            # device name
            device_name = device.device_name

            # ******************************** GET DEVICE MACHINE MAPPING (START) ******************************

            device_list = [device_id]

            bs_devices = Device.objects.filter(id__in=device_list).values('device_name', 'machine__name',
                                                                          'device_technology', 'device_type',
                                                                          'ip_address')

            # Create instance of 'InventoryUtilsGateway' class
            inventory_utils = InventoryUtilsGateway()

            machine_dict = inventory_utils.prepare_machines(bs_devices, 'machine__name')

            complete_performance = get_complete_performance(machine_dict=machine_dict)

            # ******************************** GET DEVICE MACHINE MAPPING (END) ********************************

            network_perf_data = complete_performance['network_perf_data']
            service_perf_data = complete_performance['service_perf_data']
            inventory_perf_data = complete_performance['inventory_perf_data']
            status_perf_data = complete_performance['status_perf_data']

            device_network_info = [d for d in network_perf_data if d['device_name'] == device_name]

            perf_info += self.collect_performance(performance=device_network_info,
                                                  device_id=device_id,
                                                  processed=processed)

            # if device is down than don't show services data
            if device_pl != "100":
                service_perf_data = [d for d in service_perf_data if d['device_name'] == device_name]
                inventory_perf_data = [d for d in inventory_perf_data if d['device_name'] == device_name]
                status_perf_data = [d for d in status_perf_data if d['device_name'] == device_name]

                perf_info += self.collect_performance(performance=service_perf_data,
                                                      device_id=device_id,
                                                      processed=processed)

                perf_info += self.collect_performance(performance=inventory_perf_data,
                                                      device_id=device_id,
                                                      processed=processed)

                perf_info += self.collect_performance(performance=status_perf_data,
                                                      device_id=device_id,
                                                      processed=processed)

            # bs connected device
            bs_connected_device = None
            try:
                bs_connected_device = Topology.objects.get(connected_device_ip=device.ip_address).ip_address
            except Exception as e:
                pass

            perf_info.append({
                "name": 'connected_bs_ip',
                "title": 'BS Connected IP',
                "show": True,
                "url": "",
                "value": bs_connected_device,
            })

            for d in perf_info:
                if '_mac_' in d['name']:
                    d['value'] = d['value'].upper()

        return HttpResponse(json.dumps(perf_info))

    def collect_performance(self, performance, device_id, processed):
        """ Get Sector/Sub Station device information

            Parameters:
                - performance (list) - list of dictionaries containing performance data
                - device_id (long) - device id for e.g. 34925
                - processed (dict) - list of dicts containing processed/filtered performance data

            Returns:
                - device_info (list) - list of dictionaries containing device static or polled data
                                                    [
                                                        {
                                                            'show': 1,
                                                            'name': u'uptime',
                                                            'value': u'6.0082333333',
                                                            'title': u'Uptime'
                                                        },
                                                        {
                                                            'show': 1,
                                                            'name': u'frequency',
                                                            'value': u'5830',
                                                            'title': u'Frequency'
                                                        },
                                                        {
                                                            'show': 1,
                                                            'name': u'pl',
                                                            'value': u'4',
                                                            'title': 'PacketLoss'
                                                        }
                                                    ]
        """
        # Create instance of 'ServiceUtilsGateway' class
        service_utils = ServiceUtilsGateway()

        SERVICE_DATA_SOURCE = service_utils.service_data_sources()

        device_info = list()

        for perf in performance:
            res, name, title, show_gis = self.sanatize_datasource(perf['data_source'], perf['service_name'])

            if not res:
                continue
            if (perf['data_source'], perf['service_name']) in processed:
                continue
            processed[perf['data_source'], perf['service_name']] = []

            service_name = perf['service_name'].strip()

            sds_name = perf['data_source'].strip()

            if sds_name not in ['pl', 'rta']:
                sds_name = service_name.lower() + "_" + sds_name.lower()

            formula = SERVICE_DATA_SOURCE[sds_name]["formula"] \
                if sds_name in SERVICE_DATA_SOURCE \
                else None
            try:
                # Current value.
                cur_val = perf['current_value']

                # severity of device
                severity = perf['severity']
                
                try:
                    perf_info = {
                        "name": name,
                        "title": title,
                        "show": show_gis,
                        "severity": severity,
                        "url": "performance/service/" + service_name + "/service_data_source/" + perf[
                            'data_source'].strip() + "/device/" + str(
                            device_id) + "?start_date=&end_date=",
                        "value": eval(str(formula) + "(" + str(cur_val) + ")") if formula
                        else cur_val,
                    }
                except Exception as e:
                    perf_info = {
                        "name": name,
                        "title": title,
                        "show": show_gis,
                        "severity": severity,
                        "url": "performance/service/" + service_name + "/service_data_source/" + perf[
                            'data_source'].strip() + "/device/" + str(
                            device_id) + "?start_date=&end_date=",
                        "value": cur_val,
                    }

                device_info.append(perf_info)
            except Exception as e:
                pass

        return device_info

    def sanatize_datasource(self, data_source, service_name):
        """ Get Sector performance info

            Parameters:
                - data_source (unicode) - data source name for e.g. 'rta'
                - service_name (unicode) - service name

            Returns:
                - name (unicode) - data source name for e.g. 'rta'
                - title (str) - data source name to display for e.g. 'Latency'
                - show_gis (int) - 1 to show data source; 0 for not to show
        """
        # Create instance of 'ServiceUtilsGateway' class
        service_utils = ServiceUtilsGateway()

        # fetch all data sources
        SERVICE_DATA_SOURCE = service_utils.service_data_sources()

        # if data_source and data_source[:1].isalpha():
        if data_source:
            title = " ".join(data_source.split("_")).title()

            key_name = service_name.strip().lower() + "_" +data_source.strip().lower()

            if data_source.strip().lower() in ['pl', 'rta']:
                name = data_source.strip()
                key_name = data_source.strip().lower()
            else:
                name = key_name

            show_gis = 0
            try:
                if data_source.strip().lower() not in ['pl', 'rta']:
                    title = SERVICE_DATA_SOURCE[key_name]['service_alias'] + "</br> [ " +\
                            SERVICE_DATA_SOURCE[key_name]['display_name'] + " ]"
                else:
                    title = SERVICE_DATA_SOURCE[key_name]['display_name']

                show_gis = SERVICE_DATA_SOURCE[key_name]['show_gis']
            except Exception as e:
                pass

            return True, name, title, show_gis
        return False, False, False, 0


def get_complete_performance(machine_dict={}, tech_list=[], current_user=None, ts_type='normal'):
    """ Get complete performance data

        Parameters:
            - machine_dict (dict) - dictionary containing device and machine mapping for e.g.
                                    {
                                        u'ospf4': [u'10023', u'10027', u'10028', u'11253', u'11254', u'11255',
                                                   u'11256', u'11258'], u'ospf1': [u'10178', u'10179', u'12754',
                                                   u'13004', u'13039']
                                    }

        Returns:
            - result (dict) - dictionary containing performance data

    """
    ds_list = list()
    thematic_obj = None
    where_condition = Q()
    has_ds = False
    tech_wise_thematic = {}
    
    if tech_list and current_user and ts_type:    
        if ts_type == "normal":
           try:
               thematic_obj = UserThematicSettings.objects.filter(
                   user_profile=current_user,
                   thematic_technology__name__in=tech_list
               )
               
               ds_list = list(thematic_obj.values_list(
                   'thematic_template__threshold_template__live_polling_template__data_source__name',
                   flat=True
               ))
           except Exception as e:
               pass
        elif ts_type == "ping":
            try:
                thematic_obj = UserPingThematicSettings.objects.filter(
                    user_profile=current_user,
                    thematic_technology__name__in=tech_list
                )

                ds_list = list(thematic_obj.values_list(
                    'thematic_template__data_source',
                    flat=True
                ))
            except Exception as e:
                pass

        if ds_list:
            has_ds = True
            ds_list.append('frequency')
            for item in thematic_obj:
                try:
                    tech_name = item.thematic_technology.name
                except Exception, e:
                    tech_name = ''

                if tech_name:
                    if tech_name not in tech_wise_thematic:
                        tech_wise_thematic[tech_name] = list()
                    tech_wise_thematic[tech_name].append(item)

    network_perf_data = list()
    performance_perf_data = list()
    service_perf_data = list()
    inventory_perf_data = list()
    status_perf_data = list()
    utilization_perf_data = list()
    polled_columns = [
        'device_name',
        'service_name',
        'data_source',
        'current_value',
        'sys_timestamp',
        'severity'
    ]

    for machine_name in machine_dict:
        devices_list = machine_dict[machine_name]
        where_condition = Q()
        if has_ds:
            where_condition &= Q(data_source__in=ds_list)
        
        where_condition &= Q(device_name__in=devices_list)

        # device network info
        device_network_info = NetworkStatus.objects.filter(where_condition).values(
            *polled_columns
        ).using(alias=machine_name)

        network_perf_data.extend(list(device_network_info))

        # device performance info
        performance_network_info = PerformanceStatus.objects.filter(where_condition).values(
            *polled_columns
        ).using(alias=machine_name)

        performance_perf_data.extend(list(performance_network_info))

        # device service info
        device_service_info = ServiceStatus.objects.filter(where_condition).values(
            *polled_columns
        ).using(alias=machine_name)

        service_perf_data.extend(list(device_service_info))
    
        # device inventory info
        device_inventory_info = InventoryStatus.objects.filter(where_condition).values(
            *polled_columns
        ).using(alias=machine_name)

        inventory_perf_data.extend(list(device_inventory_info))
    

        # device status info
        device_status_info = Status.objects.filter(where_condition).values(
            *polled_columns
        ).using(alias=machine_name)

        status_perf_data.extend(list(device_status_info))
        # device utilization info
        device_utilization_info = UtilizationStatus.objects.filter(where_condition).values(
            *polled_columns
        ).using(alias=machine_name)

        utilization_perf_data.extend(list(device_utilization_info))

    if tech_list and current_user and ts_type:
        result = {
            'complete_performance': {
                'network_perf_data': network_perf_data,
                'performance_perf_data': performance_perf_data,
                'service_perf_data': service_perf_data,
                'inventory_perf_data': inventory_perf_data,
                'status_perf_data': status_perf_data,
                'utilization_perf_data': utilization_perf_data
            },
            'tech_wise_thematic': tech_wise_thematic
        }
    else:
        result = {
            'network_perf_data': network_perf_data,
            'performance_perf_data': performance_perf_data,
            'service_perf_data': service_perf_data,
            'inventory_perf_data': inventory_perf_data,
            'status_perf_data': status_perf_data,
            'utilization_perf_data': utilization_perf_data
        }


    return result


class GetInfoWindowContent(View):
    """

    """

    def get(self, request, *args, **kwargs):
        """

        """
        result = {
            'success': 0,
            'message': 'Data not fetched',
            'data': []
        }

        elem_type = request.GET.get('elem_type')
        elem_id = request.GET.get('elem_id')
        child_id = request.GET.get('child_id', 0)
        technology = request.GET.get('technology')

        if elem_type and elem_id:
            info_list = list()
            child_info_list = list()
            if elem_type == 'base_station':
                info_list = getBSInventoryInfo(base_station_id=elem_id)
            elif elem_type == 'sub_station':
                info_list = getSSInventoryInfo(sub_station_id=elem_id)
            elif 'sector' in elem_type:
                info_list = getSectorInventoryInfo(sector_id=elem_id)
            elif elem_type == 'path':
                info_list = getBSInventoryInfo(base_station_id=elem_id)
                child_info_list = getSSInventoryInfo(sub_station_id=child_id)
            else:
                result.update(message='Invalid element type.')

            if len(info_list) > 0:
                info_list = info_list[0]
                if elem_type == 'base_station' or elem_type == 'path':
                    bs_info = list()
                    bh_info = list()

                    for key in info_list:
                        temp_dict = {
                            'show': 1,
                            'name': key,
                            'title': key,
                            'value': info_list.get(key, 'NA')
                        }
                        if key in BS_INFOWINDOW_LIST:
                            bs_info.append(temp_dict)
                        elif key in BH_INFOWINDOW_LIST:
                            bh_info.append(temp_dict)
                        else:
                            continue

                    result.update(
                        data={
                            'base_station': bs_info,
                            'backhaul': bh_info
                        }
                    )

                    if elem_type == 'path' and len(child_info_list) > 0:
                        ss_info = list()
                        child_info_list = child_info_list[0]
                        for key in child_info_list:
                            temp_dict = {
                                'show': 1,
                                'name': key,
                                'title': key,
                                'value': child_info_list.get(key, 'NA')
                            }
                            if key in SS_INFOWINDOW_LIST:
                                ss_info.append(temp_dict)
                            else:
                                continue

                        result.update(
                            data={
                                'base_station': bs_info,
                                'backhaul': bh_info,
                                'sub_station': ss_info
                            }
                        )
                else:
                    dataset = list()
                    for key in info_list:
                        temp_dict = {
                            'show': 1,
                            'name': key,
                            'title': key,
                            'value': info_list.get(key, 'NA')
                        }

                        dataset.append(temp_dict)


                    result.update(
                        data=dataset
                    )

                result.update(
                    success=1,
                    message='Data fetched successfully.'
                )

        else:
            result.update(message='Invalid element type & id.')

        return HttpResponse(json.dumps(result))
