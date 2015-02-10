import json

from datetime import datetime, timedelta

from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView, View

from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response

from django.core.urlresolvers import reverse_lazy, reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from datetime import datetime
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY

from scheduling_management.models import Event, Weekdays
from scheduling_management.forms import EventForm

from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin
from nocout.mixins.user_action import UserLogDeleteMixin
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

        #if the user role is Admin or superuser then the action column will appear on the datatable
        datatable_headers.append({'mData': 'no_of_devices', 'sTitle': 'No.of devices', 'sWidth': '5%', 'bSortable': False})
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or self.request.user.is_superuser:
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
    # columns are used for list of fields which should be displayed on data table.
    columns = ['name', 'created_at', 'repeat', 'start_on', 'created_by__username', 'scheduling_type', 'device__device_alias']
    #search_columns is used for list of fields which is used for searching the data table.
    search_columns = ['name', 'repeat', 'created_by__username', 'scheduling_type', 'device__device_alias']
    #order_columns is used for list of fields which is used for sorting the data table.
    order_columns = ['name', 'created_at', 'repeat', 'start_on', 'created_by__username', 'scheduling_type', 'device__device_alias']
    required_permissions = ('scheduling_management.view_event',)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        org = self.request.user.userprofile.organization
        qs = self.model.objects.filter(organization__in=[org])
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
            # when there are more than 5 devices than limit it to 5 devices and show with their ip_address.
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
        title = self.request.GET.get('title', None)
        return self.render_to_response(
            self.get_context_data(form=form, title=title))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        # querydict contain the device id as a comma seperated single string
        # i.e: device = ['1,2,3,4,5,6...'] and should be ['1','2','3','4',..]
        # get the device id from the querydict.
        device = self.request.POST['device']
        # split device id from comma(,) to get in proper format and assing to querydict.
        # in order to check the validity of form.
        self.request.POST['device'] = device.split(',')
        if not form.is_valid():
            # for invalid form again assing the previous format of device id to querydict.
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
        # device id need to in format ['1,2,3,...'] when rendering the templates so,
        # set initial of device in the required format.
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


class EventDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Event.
    """
    model = Event
    template_name = 'scheduling_management/event_delete.html'
    success_url = reverse_lazy('event_list')
    required_permissions = ('scheduling_management.delete_event',)
    obj_alias = 'name'


#**************************************************#
def last_day_of_the_month(any_day):
    """
    Return the last day of the month.

    :param:
    day: Example: datetime.today()
    """
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)


def event_today_status(dic):
    """
    To check the status of event for today date.
    Note: in dateutil 0==Monday, while in python datetime 0==Sunday.

    :param:
    dic: dictionary as {'event': event_object, 'month': 02, 'year': 2015}  Note: event is must.

    :return the dictionary containing the event id, status for today date
    		and the list of execution date of this month.
            i.e: {  'status': False,
                    'event_ids': 2,
                    'execution_dates': [
                                        datetime.datetime(2014, 12, 19, 0, 0),
                                        datetime.datetime(2014, 12, 20, 0, 0),
                                        datetime.datetime(2014, 12, 21, 0, 0),...
                                    ]
                }
    """
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    status = False  # initialize that there is no active event.
    count = 0   # initialize that event end after 0(zero) occurence.

    execution_dates = []
    last_day_of_month = last_day_of_the_month(today)

    event = dic['event']
    year = dic['year'] if 'year' in dic else (today.year)
    month = dic['month'] if 'month' in dic else (today.month)
    # Set the start and end of month according to month and year.
    month_start = today.replace(year=year, month=month, day=1)
    month_end = last_day_of_the_month(month_start).date()

    event_ids = event.id
    # Note: we need start and end date to find the list of execution date of event.
    # Set the start to the start_on (i.e: event.start_on) of the event.
    start = event.start_on
    # by default set the end of event to the month of today.
    # because findind all execution dates upto end of event (i.e: event.end_on) is of no use.
    # And what for cases like (case1: end never; case2: end after particular occurence) it may become infinite.
    event_end = last_day_of_month.date()
    # if request month is not same as month of today. Update the event_end.
    # it is case when 'month' and 'year' is there in dic and not same as today's month or today's year.
    if month_end >= event_end:
        event_end = month_end
    # it is case when month_end is lesst than event_end but greater than start of event.
    # i.e. start = (2014, 09, 01), event_end = (2015, 02, 01) and month_end = (2014, 11, 30)
    elif month_end >= start:
        event_end = month_end

    # Now Update event_end to event.end_on if event.end_on date is there and is less than month_end.
    # case when event execution will end on (2014, 10, 01) and month_end is (2014, 11, 30)
    if event.end_on:
        event_end = event.end_on if event.end_on <= month_end else month_end
    elif event.end_after:
        count = event.end_after # case2: end after particular occurence
    # finally update the end date to event_end.
    end = event_end
    # get the frequency of occurence of event by default it is 1.
    interval = 1 if not event.repeat_every else event.repeat_every

    # Case to repeat the event on daily basis.
    if event.repeat == 'dai':
        execution_dates = list(rrule(DAILY, dtstart=start, interval=interval, count=count, until=end))
        # check whether the event will execute today or not.
        if today in execution_dates:
            status = True

    # Case to repeat the event on weekly basis.
    elif event.repeat == 'wee':
        # get the days of weeks to repeat the event.
        weekday = tuple([int(x.id)-1 for x in event.repeat_on.all()])
        execution_dates = list(rrule(WEEKLY, dtstart=start, interval=interval, count=count, until=end, byweekday=weekday))
        if today in execution_dates:
            status = True

    # Case to repeat the event on monthly basis.
    elif event.repeat == 'mon':
        # repeat event on day of month.
        if event.repeat_by == 'dofm':
            execution_dates = list(rrule(MONTHLY, dtstart=start, interval=interval, count=count, until=end))
            if today in execution_dates:
                status = True
        else: # case: day of the week
            weekno = (start.day+7-1)/7  # get the position of week.
            weekday = start.isocalendar()[2] - 1
            execution_dates = list(rrule(MONTHLY, dtstart=start, interval=interval, count=count, until=end, bysetpos=weekno, byweekday=weekday))
            if today in execution_dates:
                status = True

    # Case to repeat the event on yearly basis.
    elif event.repeat == 'yea':
        if today in list(rrule(YEARLY, dtstart=start, interval=interval, count=count, until=end)):
            status = True

    # Case to repeat the event on tuesday and thursday.
    elif event.repeat == 'tat':
        # 1==Tuesday and 3==Thursday.
        execution_dates = list(rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(1,3)))
        if today in execution_dates:
            status = True

    # Case to repeat the event on monday, wednesday and friday.
    elif event.repeat == 'mwf':
        # 0==Monday, 2==Wednesday and 4==Friday.
        execution_dates = list(rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(0,2,4)))
        if today in execution_dates:
            status = True

    # Case to repeat the event on monday to friday.
    elif event.repeat == 'mtf':
        # Note: 0==Monday, 1==Tuesday, 2==Wednesday, 3==Thursday and 4==Friday.
        execution_dates = list(rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(0,1,2,3,4)))
        if today in execution_dates:
            status = True

    return {'event_ids': event_ids, 'status': status, 'execution_dates': execution_dates}


def get_today_event_list():
    """
    To check status of event whether active for time now or not.
    Used in check_device_status method of alarm_escalation.tasks

    :return dictionary containing list of events and their corresponding devices ids.
                    i.e: {  'event_list': [eve_obj1, eve_obj2, eve_obj3,...],
                            'device_ids': [1,2,3,4,...],
                        }
    """
    event_list = []
    time = datetime.today().time()
    # Check for every event whether any event will execute today or not.
    for event in Event.objects.all():
        result = event_today_status({'event': event})
        # Update event list if event is active for today.
        if result['status']:
            # Update if time now in between event's start and end on time.
            if event.start_on_time <= time and time <= event.end_on_time:
                event_list.append(event)

    # Get device ids of all the active events.
    device_ids = Device.objects.filter(event__in=event_list).distinct().values_list('id', flat=True)

    return {'event_list': event_list, 'device_ids': device_ids}


def get_month_event_list(request):
    """
    Method return the json format of the events execution date list
    using ajax call according to the month and year of scheduling_management fullcalendar.

    :param:
    month: integer
    year: integer

    :return dictionary containing list of dictionary of event detail.
                    i.e: {[
                            { 'id': 1, 'title': 'event_name1', 'start': datetime1, 'end': datetime1, 'allDay': False,}
                            { 'id': 1, 'title': 'event_name1', 'start': datetime2, 'end': datetime2, 'allDay': False,}
                            { 'id': 2, 'title': 'event2', 'start': datetime1,... },
                            { 'id': 2, 'title': 'event2', 'start': datetime2,... },...,
                            { 'id': 3, 'title': 'e3',... }, ...,
                        ]}
    """
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    # Initialize the month and year.
    month = int(request.GET.get('month', today.month - 1))
    year = int(request.GET.get('year', today.year))

    month_schedule_list = [] # contain the list of this month event.
    org = request.user.userprofile.organization

    fmt = "%a %b %d %Y %H:%M:%S"
    # set the first day and last day of request month and year.
    first_day_of_month = today.replace(year=year, month=month+1, day=1)
    last_day_of_month = last_day_of_the_month(first_day_of_month)

    for event in Event.objects.filter(organization__in=[org]):
        # Get the event's date list of execution.
        result = event_today_status({'event': event, 'month': month+1, 'year': year})
        # Update the list if date fall in same month.
        for date in result['execution_dates']:
            if first_day_of_month <= date and date <= last_day_of_month:
                # convert the start and end date in specific format.
                dic = { 'id': event.id, 'title': event.name,
                        'start': (datetime.combine(date, event.start_on_time)).strftime(fmt),
                        'end': datetime.combine(date, event.end_on_time).strftime(fmt),
                        'allDay': False,
                        }
                month_schedule_list.append(dic)

    return HttpResponse ( json.dumps({
            'month_schedule_list': month_schedule_list
            }) )
