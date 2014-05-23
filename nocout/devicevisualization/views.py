from django.shortcuts import render_to_response
from user_profile.models import UserProfile
from user_group.models import Organization
from django.template import RequestContext


def locate_devices(request):
    template_data = { 'host_info' : 
                        request.META['SERVER_NAME'] + ":" + \
                        request.META['SERVER_PORT'] + "/",
                    'username' : request.user.username,
                    'get_filter_api':
                        "http://" + \
                        request.META['SERVER_NAME'] + ":" + \
                        request.META['SERVER_PORT'] + "/" + \
                        "gis/get_filters/",
                    'set_filter_api':
                        "http://" + \
                        request.META['SERVER_NAME'] + ":" + \
                        request.META['SERVER_PORT'] + "/" + \
                        "gis/set_filters/",
                    }

    return render_to_response('devicevisualization/locate_devices.html', 
                                template_data, 
                                context_instance=RequestContext(request))