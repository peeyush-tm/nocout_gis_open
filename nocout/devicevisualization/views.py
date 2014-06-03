from django.shortcuts import render_to_response
from user_profile.models import UserProfile
from user_group.models import Organization
from django.template import RequestContext


def locate_devices(request , device_name = "default_device_name"):
    template_data = { 'host_info' : 
                        request.META['SERVER_NAME'] + ":" + \
                        request.META['SERVER_PORT'] + "/",
                    'username' : request.user.username,
                    'device_name' : device_name,
                    'get_filter_api': get_url(request, 'GET'),
                    'set_filter_api': get_url(request, 'POST')
                    }
    print "-- template_data --"
    print template_data

    print "*******************device_name*******************"
    print device_name

    return render_to_response('devicevisualization/locate_devices.html', 
                                template_data, 
                                context_instance=RequestContext(request))

def get_url(req, method):
    url = None
    if method == 'GET':
        url = "//" + req.META['SERVER_NAME'] + ":" + \
            req.META['SERVER_PORT'] + "/gis/get_filters/"
    elif method == 'POST':
        url = "//" + req.META['SERVER_NAME'] + ":" + \
            req.META['SERVER_PORT'] + "/gis/set_filters/"

    return url