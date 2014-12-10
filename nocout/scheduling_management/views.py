import json
from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView, TemplateView, View
from django.core.urlresolvers import reverse_lazy, reverse
from django.http.response import HttpResponseRedirect
from django_datatables_view.base_datatable_view import BaseDatatableView

from nocout.mixins.permissions import PermissionsRequiredMixin
from scheduling_management.models import Event, Weekdays
from scheduling_management.forms import EventForm
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin

# Create your views here.
# def get_scheduler(request):

# 	return render_to_response('scheduling_management/scheduler_template.html',context_instance=RequestContext(request))

class EventList(PermissionsRequiredMixin, TemplateView):
    """
    Class Based View for the Event data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """

    template_name = 'scheduling_management/scheduler_template.html'
    required_permissions = ('scheduling_management.view_event',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(EventList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': '10%', 'bSortable': True},
            {'mData': 'created_at', 'sTitle': 'Created At', 'sWidth': '10%', 'bSortable': True},
            {'mData': 'repeat', 'sTitle': 'Repeat', 'sWidth': '10%', 'bSortable': True},
            {'mData': 'start_on', 'sTitle': 'Start On', 'sWidth': '10%', 'bSortable': True},
            {'mData': 'created_by__username', 'sTitle': 'Created By', 'sWidth': '10%', 'bSortable': True},
            {'mData': 'scheduling_type', 'sTitle': 'Scheduling Type', 'sWidth': '15%', 'bSortable': True},
            {'mData': 'device__device_alias', 'sTitle': 'Device', 'sWidth': 'auto', 'bSortable': True}, ]

        #if the user role is Admin or operator or superuser then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role or self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class EventListingTable(PermissionsRequiredMixin,
        DatatableSearchMixin,
        BaseDatatableView,
    ):
    """
    Class based View to render Event Data table.
    """
    model = Event
    columns = ['name', 'created_at', 'repeat', 'start_on', 'created_by__username', 'scheduling_type', 'device__device_alias']
    search_columns = ['name', 'repeat', 'created_by__username', 'scheduling_type', 'device__device_alias']
    order_columns = ['name', 'created_at', 'repeat', 'start_on', 'created_by__username', 'scheduling_type', 'device__device_alias']
    required_permissions = ('scheduling_management.view_event',)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        qs = self.model.objects.filter()
        return qs.prefetch_related('device')

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        repeat_choice = dict(Event.REPEAT)
        scheduling_type_choice = dict(Event.SCHEDULING_TYPE)
        json_data = []
        for obj in qs:
            dct = {}
            dct.update(name=obj.name)
            dct.update(created_at=obj.created_at)
            repeat = repeat_choice["%s"%(obj.repeat)]
            dct.update(repeat=repeat)
            dct.update(start_on=obj.start_on)
            dct.update(created_by__username=obj.created_by.username)
            scheduling_type = scheduling_type_choice["%s"%(obj.scheduling_type)]
            dct.update(scheduling_type=scheduling_type)
            dct.update(device__device_alias=', '.join(list(obj.device.values_list('device_alias', flat=True))))
            dct.update(actions='<a href="/scheduling/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/scheduling/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(obj.id))
            json_data.append(dct)
        return json_data


class EventCreate(PermissionsRequiredMixin, CreateView):
    """
    Render event create view
    """
    template_name = 'scheduling_management/event_new.html'
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('event_list')
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
    Render event create view
    """
    template_name = 'scheduling_management/event_update.html'
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('event_list')
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


def event_delete(request, pk):
    """
    delete the event.
    """
    event = Event.objects.get(id=pk)
    event.delete()
    return HttpResponseRedirect(reverse('event_list'))
