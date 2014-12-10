from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseRedirect

from nocout.mixins.permissions import PermissionsRequiredMixin
from scheduling_management.models import Event, Weekdays
from scheduling_management.forms import EventForm

# Create your views here.
def get_scheduler(request):

	return render_to_response('scheduling_management/scheduler_template.html',context_instance=RequestContext(request))


class EventCreate(PermissionsRequiredMixin, CreateView):
    """
    Render device type create view
    """
    template_name = 'scheduling_management/event_new.html'
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('scheduler')
    required_permissions = ('scheduling_management.add_event',)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(
            self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            user = self.request.user.userprofile
            self.object = form.save(commit=False)
            self.object.created_by = user
            self.object.organization = user.organization
            self.object.save()
            return HttpResponseRedirect(EventCreate.success_url)
        else:
            return self.render_to_response(
            self.get_context_data(form=form, ))


class EventUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Render device type create view
    """
    template_name = 'scheduling_management/event_update.html'
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('scheduler')
    required_permissions = ('scheduling_management.change_event',)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(
            self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            self.object = form.save()
            return HttpResponseRedirect(EventUpdate.success_url)
        else:
            return self.render_to_response(
            self.get_context_data(form=form, ))
