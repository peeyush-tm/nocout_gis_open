from django.shortcuts import render_to_response

def locate_devices(request):
    c = {}
    host_ip = request.get_host().split(':')[0]
    c.update({"host_ip": host_ip})
    return render_to_response('devicevisualization/locate_devices.html', c)