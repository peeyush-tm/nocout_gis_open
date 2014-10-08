from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext

# Create your views here.
def get_scheduler(request):

	return render_to_response('scheduling_management/scheduler_template.html',context_instance=RequestContext(request))