from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext

# Create your views here.

def getNetworkAlert(request):

	return render_to_response('alert_center/network_alerts_list.html',context_instance=RequestContext(request))

def getCustomerAlert(request):

	return render_to_response('alert_center/customer_alerts_list.html',context_instance=RequestContext(request))

def getCustomerAlertDetail(request):

	return render_to_response('alert_center/customer_details_list.html',context_instance=RequestContext(request))

def getNetworkAlertDetail(request):

	return render_to_response('alert_center/network_details_list.html',context_instance=RequestContext(request))