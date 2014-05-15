from django.shortcuts import render_to_response

def locate_devices(request):
    first_name = request.user.first_name
    last_name = request.user.last_name
    c = {}
    host_ip = request.get_host().split(':')[0]
    c.update({"host_ip": host_ip, "firstname": first_name, "lastname": last_name})
    return render_to_response('devicevisualization/locate_devices.html', c)