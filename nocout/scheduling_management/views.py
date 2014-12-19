import json
from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView, TemplateView, View
from django.core.urlresolvers import reverse_lazy, reverse
from django.http.response import HttpResponseRedirect
from django_datatables_view.base_datatable_view import BaseDatatableView
from datetime import datetime
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY

from nocout.mixins.permissions import PermissionsRequiredMixin
from scheduling_management.models import Event, Weekdays
from scheduling_management.forms import EventForm
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin
from device.models import Device

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
            datatable_headers.append({'mData': 'no_of_devices', 'sTitle': 'No.of devices', 'sWidth': '5%', 'bSortable': False})
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
            # display the device with ip address upto 5 devices.
            dev_list = ["{}-{}".format(dev.device_alias,dev.ip_address) for i,dev in enumerate(obj.device.all()) if i < 5 ]
            dct.update(device__device_alias=', '.join(dev_list))
            dct.update(no_of_devices=obj.device.count())
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

        device = self.request.POST['device']
        self.request.POST['device'] = device.split(',')
        if not form.is_valid():
            self.request.POST['device'] = device

        if form.is_valid():
            user = self.request.user.userprofile
            self.object = form.save(commit=False)
            self.object.created_by = user
            self.object.organization = user.organization
            self.object.save()
            form.save_m2m()
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
        device_initial = ','.join([str(device_id) for device_id in self.object.device.values_list('id', flat=True)])
        form = EventForm(instance=self.object, initial={'device': device_initial})
        return self.render_to_response(
            self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        device = self.request.POST['device'] # device id come in format '1,2,3'
        self.request.POST['device'] = device.split(',') # update device id as ['1', '2', '3']
        if not form.is_valid():
            self.request.POST['device'] = device # again undo the changes if form is not valid

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


#**************************************************#
def event_today_status(event):
    """
    To check the statu of event for today date.
    Note: in dateutil 0==Monday, while in python datetime 0==Sunday.

    :param event: Event object
    :return the dictionary containing the event id and status for today date.
    """

    event_ids = event.id
    status = False
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start = event.start_on
    event_end = today.date() # case1: end never; case2: end after particular occurence
    count = 0
    if event.end_on:
        event_end = event.end_on
    elif event.end_after:
        count = event.end_after # case2: end after particular occurence

    end = event_end
    interval = 1 if not event.repeat_every else event.repeat_every

    if event.repeat == 'dai':
        if today in list(rrule(DAILY, dtstart=start, interval=interval, count=count, until=end)):
            status = True

    elif event.repeat == 'wee':
        weekday = tuple([int(x.id)-1 for x in event.repeat_on.all()])
        if today in list(rrule(WEEKLY, dtstart=start, interval=interval, count=count, until=end, byweekday=weekday)):
            status = True

    elif event.repeat == 'mon':
        if event.repeat_by == 'dofm':
            if today in list(rrule(MONTHLY, dtstart=start, interval=interval, count=count, until=end)):
                status = True
        else: # case: day of the week
            weekno = (start.day+7-1)/7
            weekday = start.isocalendar()[2] - 1
            if today in list(rrule(MONTHLY, dtstart=start, interval=interval, count=count, until=end, bysetpos=weekno, byweekday=weekday)):
                status = True

    elif event.repeat == 'yea':
        if today in list(rrule(YEARLY, dtstart=start, interval=interval, count=count, until=end)):
            status = True

    elif event.repeat == 'tat':
        # 1==Tuesday and 3==Thursday.
        if today in list(rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(1,3))):
            status = True

    elif event.repeat == 'mwf':
        # 0==Monday, 2==Wednesday and 4==Friday.
        if today in list(rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(0,2,4))):
            status = True

    elif event.repeat == 'mtf':
        # Note: 0==Monday, 1==Tuesday, 2==Wednesday, 3==Thursday and 4==Friday.
        if today in list(rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(0,1,2,3,4))):
            status = True

    return {'event_ids': event_ids, 'status': status}


def get_today_event_list():
    """
    To check event is active for time now.
    :return dictionary containing list of events and their corresponding devices ids.
    """
    event_list = []
    time = datetime.today().time()
    for event in Event.objects.all():
        result = event_today_status(event)
        if result['status']:
            if event.start_on_time <= time and time <= event.end_on_time:
                event_list.append(event)
    device_ids = Device.objects.filter(event__in=event_list).distinct().values_list('id', flat=True)

    return {'event_list': event_list, 'device_ids': device_ids}
