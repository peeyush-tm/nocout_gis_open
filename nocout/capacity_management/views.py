from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext

# Create your views here.

def get_daily_alerts(request, alert_type="default"):
    """
    get request to render daily alerts pages.

    :params request object:
    :params alert_type:
    :return Https response object:

    """

    if(alert_type == "sector"):
        alert_template = 'capacity_management/sector_capacity_alert.html'
    elif(alert_type == "backhaul"):
        alert_template = 'capacity_management/backhaul_capacity_alert.html'

    return render_to_response(alert_template,context_instance=RequestContext(request))

def get_utilization_status(request, status_type="default"):
    """
    get request to render utilization pages

    :params request object:
    :params status_type:
    :return Https response object:
    """

    if(status_type == "sector"):
        status_template = 'capacity_management/sector_capacity_status.html'
    elif(status_type == "backhaul"):
        status_template = 'capacity_management/backhaul_capacity_status.html'

    return render_to_response(status_template, context_instance=RequestContext(request))
	