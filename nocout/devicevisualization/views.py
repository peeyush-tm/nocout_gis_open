from django.shortcuts import render_to_response
from user_profile.models import UserProfile
from user_group.models import Organization


def locate_devices(request):
    try:
        first_name = request.user.first_name
        last_name = request.user.last_name
        user_profile = UserProfile.objects.get(username=request.user)
        user_department = user_profile.department_set.all()[0].user_group.alias
        user_group = user_profile.department_set.all()[0].user_group
        user_organization = Organization.objects.get(user_group=user_group.id).name
        print "User Organization: {}".format(user_organization)
    except:
        print "User doesn't exist."
    c = {}
    host_ip = request.get_host().split(':')[0]
    try:
        c.update({"host_ip": host_ip,
                  "firstname": first_name,
                  "lastname": last_name,
                  "user_department": user_department,
                  "user_organization": user_organization})
    except:
        print "Something is not set."
    return render_to_response('devicevisualization/locate_devices.html', c)