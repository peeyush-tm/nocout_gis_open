import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import logging
from django.utils.decorators import method_decorator
from django.views.generic import View
from device.models import Device, DeviceFrequency
from inventory.models import ThematicSettings
from performance.models import InventoryStatus, NetworkStatus, ServiceStatus
from django.views.decorators.csrf import csrf_exempt
import re, ast
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

                return HttpResponse(json.dumps(request_data))

            return HttpResponse(json.dumps({'result':'No Performance Data'}))

        def get_device_performance(self, device_name):
            performance_data={}
            try:
                device= Device.objects.get(device_name= device_name)
                thematic_settings= ThematicSettings.objects.get(user_profile= self.request.user)
                threshold_template=thematic_settings.threshold_template
                live_polling_template= threshold_template.live_polling_template

                device_service_name= live_polling_template.service.name
                device_service_data_source= live_polling_template.data_source.name
                device_machine_name= device.machine.name
                try:
                    device_frequency= InventoryStatus.objects.filter(device_name= device_name, data_source= 'frequency').\
                        using(alias=device_machine_name).get().current_value
                    device_frequency= device_frequency
                except Exception as e:
                    logger.info(e.message)
                    device_frequency=''
                    pass

                try:
                    device_pl= NetworkStatus.objects.filter( device_name= device_name, service_name= 'ping',
                    data_source= 'pl').using(alias=device_machine_name).get().current_value
                except Exception as e:
                    logger.info(e.message)
                    device_pl=''
                    pass

                try:

                    device_performance_value= ServiceStatus.objects.filter( device_name= device_name, service_name= device_service_name,
                    data_source= device_service_data_source).using(alias=device_machine_name).get().current_value

                except Exception as e:
                    device_performance_value=''
                    logger.info(e.message)
                    pass

                device_link_color=None


                if len(device_frequency):
                    corrected_dev_freq = device_frequency
                    try:
                        chek_dev_freq = ast.literal_eval(device_frequency)
                        if int(chek_dev_freq) > 10:
                            corrected_dev_freq = chek_dev_freq
                    except Exception as e:
                        logger.exception("Frequency is Empty : %s" %(e.message))

                    device_frequency_color= DeviceFrequency.objects.filter(value__icontains=str(corrected_dev_freq)).\
                        values_list('color_hex_value', flat=True)
                    if len(device_frequency_color):
                        device_link_color= device_frequency_color[0]

                elif len(device_pl) and int(ast.literal_eval(device_pl))==100:
                    device_link_color='rgb(0,0,0)'

                else:
                    device_link_color='rgb(180,180,180)'

                performance_icon=''
                if device_performance_value:
                    corrected_device_performance_value = ast.literal_eval(device_performance_value)
                    icon_settings_json_string= thematic_settings.icon_settings if thematic_settings.icon_settings!='NULL' else None
                    if icon_settings_json_string:
                        icon_settings_json= eval(icon_settings_json_string)
                        range_start, range_end= None, None
                        for data in icon_settings_json:
                            range_number=''.join(re.findall("[0-9]", data.keys()[0]))
                            exec 'range_start=threshold_template.range'+str(range_number)+ '_start'
                            exec 'range_end=threshold_template.range'+str(range_number)+ '_end'
                            if abs(int(range_start)) <= abs(corrected_device_performance_value) <= abs(int(range_end)):
                               performance_icon= data.values()[0]


                performance_data= {
                    'frequency':device_frequency,
                    'pl':device_pl,
                    'color':device_link_color,
                    'performance_paramter':device_service_name,
                    'performance_value':device_performance_value,
                    'performance_icon':"media/"+str(performance_icon)
                                        if "uploaded" in str(performance_icon)
                                        else ("static/" + str(performance_icon) if len(str(performance_icon)) else ""),
                }
                logger.info("%s : %s" %(device_name, performance_data))
            except Exception as e:
                logger.info(e.message, exc_info=True)
                pass
            return performance_data

