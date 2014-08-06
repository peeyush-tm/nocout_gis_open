from django.shortcuts import render_to_response
from user_profile.models import UserProfile
from user_group.models import Organization
from django.template import RequestContext
import logging
logger=logging.getLogger(__name__)


def locate_devices(request , device_name = "default_device_name"):
    """
    Returns the Context Variable to GIS Map page.
    """
    template_data = { 'username' : request.user.username,
                    'device_name' : device_name,
                    'get_filter_api': get_url(request, 'GET'),
                    'set_filter_api': get_url(request, 'POST')
                    }

    logger.info('Template Data : %s'%(str(template_data)))
    return render_to_response('devicevisualization/locate_devices.html',
                                template_data, 
                                context_instance=RequestContext(request))

def load_google_earth(request):

    """
    Returns the Context Variable for google earth.
    """
    template_data = { 'username' : request.user.username,
                      'get_filter_api': get_url(request, 'GET'),
                      'set_filter_api': get_url(request, 'POST')
                    }

    return render_to_response('devicevisualization/google_earth_template.html',
                                template_data, 
                                context_instance=RequestContext(request))


def get_url(req, method):
    """
    Return Url w.r.t to the request type.
    """
    url = None
    if method == 'GET':
        url = "/gis/get_filters/"
    elif method == 'POST':
        url = "/gis/set_filters/"

    return url