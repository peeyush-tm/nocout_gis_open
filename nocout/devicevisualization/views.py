from django.shortcuts import render_to_response
from user_profile.models import UserProfile
from user_group.models import Organization
from django.template import RequestContext


def locate_devices(request):

    username = request.user.username
    
    template_data = { 'host_info' : 
    					request.META['SERVER_NAME'] + ":" + \
    					request.META['SERVER_PORT'] + "/",
    				'username' : request.user.username
    				}

    return render_to_response('devicevisualization/locate_devices.html', 
    							template_data, 
    							context_instance=RequestContext(request))