import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext

# Create your views here.
from device.models import Device, City, State

from inventory.models import SubStation, Circuit, Sector, BaseStation


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
					'get_devices_url' : 'get_substation_devices/',
					'get_status_url' : 'get_substation_status/'+str(device_id)+'/',
					'get_services_url' : 'get_services',
					'get_service_data_url' : 'get_service_data'
				}

	return render_to_response('performance/single_device_perf.html',page_data,context_instance=RequestContext(request))

def get_performance_dashboard(request):

	return render_to_response('performance/perf_dashboard.html',context_instance=RequestContext(request))


def get_sector_dashboard(request):

	return render_to_response('performance/sector_dashboard.html',context_instance=RequestContext(request))



def get_substation_devices(request):

    result={
        'success' : 0,
        'message' : 'Substation Devices Not Fetched Successfully.',
        'data' : {
            'meta' : {},
            'objects' : []
        }
    }

    logged_in_user=request.user.userprofile

    if 'admin' in logged_in_user.role.values_list('role_name', flat=True):
        organizations= logged_in_user.organization.get_descendants(include_self=True)
        for organization in organizations:
            substation_result= organization_devices_substations(organization)
            result['data']['objects']+= substation_result
    else:
        organization= logged_in_user.organization
        substation_result= organization_devices_substations(organization)
        result['data']['objects']= substation_result

    result['success']=1
    result['message']='Substation Devices Fetched Successfully.'
    return HttpResponse(json.dumps(result))


def organization_devices_substations(organization):
    #To result back the all the substations from the given organization as an argument.
    organization_substations= SubStation.objects.filter(device__in = Device.objects.filter(organization= organization.id).\
                              values_list('id', flat=True)).values_list('id', 'name', 'alias')
    result=list()
    for substation in organization_substations:
        result.append({ 'id':substation[0], 'name':substation[1], 'alias':substation[2] })

    return result

def get_substation_status(request, device_id):
    result={
        'success' : 0,
        'message' : 'Substation Devices Not Fetched Successfully.',
        'data' : {
            'meta' : {},
            'objects' : {}
        }
    }


    substation= SubStation.objects.get(id=device_id)
    substation_device= Device.objects.get(id= substation.device_id)
    sector= Circuit.objects.get(sub_station= substation.id).sector
    base_station= BaseStation.objects.get(id= Sector.objects.get(id=sector.id).base_station.id)
    result['data']['objects']['headers']= ['BS Name', 'Building Height',
                                           'Tower Height', 'City', 'State',
                                           'IP Address', 'MAC Address']
    result['data']['objects']['values']= [base_station.name,
                                          substation.building_height,
                                          substation.tower_height,
                                          substation.city,
                                          substation.state,
                                          substation_device.ip_address,
                                          substation_device.mac_address ]

    result['success']=1
    result['message']='Substation Devices Fetched Successfully.'
    return HttpResponse(json.dumps(result))












