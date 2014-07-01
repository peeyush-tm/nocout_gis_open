from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext

# Create your views here.

def get_live_performance(request, page_type = "no_page"):

	# Customer live performance case
	if(page_type == "customer"):
		return render_to_response('performance/customer_perf.html',context_instance=RequestContext(request))
	# Network live performance case
	elif(page_type == "network"):
		return render_to_response('performance/network_perf.html',context_instance=RequestContext(request))
	# Other live performance case
	else:
		return render_to_response('performance/other_perf.html',context_instance=RequestContext(request))

def get_performance(request, page_type = "no_page", device_id=0):
	page_data = {
					'page_title' : page_type.capitalize(),
					'device_id' : device_id,
					'get_devices_url' : 'https://www.dropbox.com/s/l6spjfkf02b4vqb/devices_list.json',
					'get_status_url' : 'get_status',
					'get_services_url' : 'get_services',
					'get_service_data_url' : 'get_service_data'
				}

	return render_to_response('performance/single_device_perf.html',page_data,context_instance=RequestContext(request))

def get_performance_dashboard(request):

	return render_to_response('performance/perf_dashboard.html',context_instance=RequestContext(request))


def get_sector_dashboard(request):

	return render_to_response('performance/sector_dashboard.html',context_instance=RequestContext(request))

