from django.shortcuts import render_to_response
from user_profile.models import UserProfile
from user_group.models import Organization


def locate_devices(request):

    username = request.user.username
    
    c = {}

    host_info = request.META['SERVER_NAME'] + ":" +\
                request.META['SERVER_PORT'] + "/"

    c.update({"host_info": host_info,
                "username": username
        })

    return render_to_response('devicevisualization/locate_devices.html', c)