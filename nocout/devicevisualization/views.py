from django.shortcuts import render_to_response

def locate_devices(request):
    context = {}
    context.update({
    	"host_ip": request.get_host().split(':')[0],
    	"firstname": request.user.first_name,
    	"lastname": request.user.last_name,
    	"username": request.user.username
    })
    return render_to_response('devicevisualization/locate_devices.html', context)