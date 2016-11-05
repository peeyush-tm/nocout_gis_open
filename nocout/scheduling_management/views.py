import json

from datetime import datetime, timedelta

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView, ListView, DetailView

from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response

from django.core.urlresolvers import reverse_lazy, reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from datetime import datetime
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from nocout.mixins.generics import FormRequestMixin
from nocout.mixins.select2 import Select2Mixin

from scheduling_management.models import Event, Weekdays, SNMPTrapSettings
from scheduling_management.forms import EventForm, SNMPTrapSettingsForm

from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin, DatatableOrganizationFilterMixin, AdvanceFilteringMixin
from nocout.mixins.user_action import UserLogDeleteMixin
from device.models import Device, DeviceType
from user_profile.utils.auth import in_group
from alert_center.models import PlannedEvent
from dateutil.relativedelta import *
from nocout.settings import PLANNED_EVENTS_ENABLED


class SchedulingViewsGateway:
    """
    This class works as gateway between scheduling_management views & other apps
    """
    def last_day_of_the_month(self, any_day):
        """
        This function return the last day of month for given date.

        :Args:
            any_day

        :return:
            param1 :last day of month
        """
        param1 = last_day_of_the_month(any_day)

        return param1

    def event_today_status(self, dic):
        """
        This function return the status of today's events.

        :Args:
            dic

        :return:
            param1 : dictionary containing the id of today event with execution dates of that event
        """

        param1 = event_today_status(dic)

        return param1

    def get_today_event_list(self):
        """
        This function return the List of device id's which have scheduling event today.

        :return:
            param1 : List of device id's which have scheduling event today
        """        

        param1 = get_today_event_list()

        return param1


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
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'created_at', 'sTitle': 'Created At', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'repeat', 'sTitle': 'Repeat', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'start_on', 'sTitle': 'Start On', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'created_by__username', 'sTitle': 'Created By', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'scheduling_type', 'sTitle': 'Scheduling Type', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'device_specification', 'sTitle': 'Device/Device Type', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'no_of_devices', 'sTitle': 'No.of devices', 'sWidth': '5%', 'bSortable': False}
        ]

        #if the user role is Admin or superuser then the action column will appear on the datatable
        is_edit_perm = in_group(self.request.user, 'admin', 'change_event')
        is_delete_perm = in_group(self.request.user, 'admin', 'delete_event')
        if is_edit_perm or is_delete_perm:
            datatable_headers.append({
                'mData': 'actions',
                'sTitle': 'Actions',
                'sWidth': '5%',
                'bSortable': False
            })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class EventListingTable(PermissionsRequiredMixin, DatatableSearchMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Class based View to render Event Data table.
    """
    model = Event
    # columns are used for list of fields which should be displayed on data table.
    columns = ['name', 'created_at', 'repeat', 'start_on', 'created_by__username', 'scheduling_type']
    #search_columns is used for list of fields which is used for searching the data table.
    search_columns = ['name', 'repeat', 'created_by__username', 'scheduling_type']
    #order_columns is used for list of fields which is used for sorting the data table.
    order_columns = columns
    required_permissions = ('scheduling_management.view_event',)

    def get_initial_queryset(self):
        """
        A function for preparing query set from model.

        :return:
            qs : Query set
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        org = self.request.user.userprofile.organization
        qs = self.model.objects.filter(organization__in=[org])
        return qs.prefetch_related('device')

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :Args:
            qs : QuerySet object

        :return:
            json_data : list of dictionaries 

        """
        repeat_choice = dict(Event.REPEAT)
        scheduling_type_choice = dict(Event.SCHEDULING_TYPE)
        json_data = []
        for obj in qs:
            dct = {}
            repeat = repeat_choice["%s"%(obj.repeat)]
            scheduling_type = scheduling_type_choice["%s"%(obj.scheduling_type)]
            dev_list = ''
            no_of_devices = ''
            
            # display the device with ip address upto 5 devices.
            # when there are more than 5 devices than limit it to 5 devices and show with their ip_address.
            if obj.scheduling_type != "dety":
                dev_list = ["{}-{}".format(dev.device_alias,dev.ip_address) for i,dev in enumerate(obj.device.all()) if i < 5 ]
                no_of_devices = obj.device.count()

            else:
                dev_list = ["{0}".format(dev.alias) for i,dev in enumerate(obj.device_type.all()) if i < 5 ]
                no_of_devices = Device.objects.filter(
                    device_type__in=DeviceType.objects.filter(alias__in=tuple(dev_list)
                ).values_list('id')).count()
            
            dct.update(
                name=obj.name,
                created_at=obj.created_at,
                repeat=repeat,
                start_on=obj.start_on,
                created_by__username=obj.created_by.username,
                scheduling_type=scheduling_type,
                device_specification=', '.join(dev_list),
                no_of_devices = no_of_devices
            )

            if in_group(self.request.user, 'admin'):
                dct.update(actions='<a href="/scheduling/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                    <a href="/scheduling/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(obj.id))
            json_data.append(dct)
        return json_data


class EventCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view for Create Event
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
        """
        Handles POST requests and make instance of form class & 
        if form is valid then save that object else return form
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # querydict contain the device id as a comma seperated single string
        # i.e: device = ['1,2,3,4,5,6...'] and should be ['1','2','3','4',..]
        # get the device id from the querydict.
        device = self.request.POST['device']
        device_type = self.request.POST['device_type']
        # split device id from comma(,) to get in proper format and assing to querydict.
        if self.request.POST['device'] != "":
            self.request.POST['device'] = device.split(',')
            self.request.POST['device_type'] = ""
        else:
             self.request.POST['device'] = ""
             self.request.POST['device_type'] = device_type.split(',')
        # in order to check the validity of form.
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
    Class based view to update Event.
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
        device_type_initial = ','.join([str(device_id) for device_id in self.object.device_type.values_list('id', flat=True)])
        repeat_on_initial = ','.join([str(device_id) for device_id in self.object.repeat_on.values_list('id', flat=True)])
        
        form = EventForm(
            instance=self.object,
            initial={
                'device': device_initial,
                'device_type': device_type_initial,
                'repeat_on' : repeat_on_initial
            }
        )

        return self.render_to_response(
            self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests and make instance of form class & 
        if form is valid then save that object else return form
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        device = self.request.POST['device'] # device id come in format '1,2,3'
        device_type = self.request.POST['device_type']
        if self.request.POST['device'] != "":
            self.request.POST['device'] = device.split(',')
            self.request.POST['device_type'] = ""
        else:
             self.request.POST['device'] = ""
             self.request.POST['device_type'] = device_type.split(',')

        # self.request.POST['device'] = device.split(',') # update device id as ['1', '2', '3']

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


def last_day_of_the_month(any_day):
    """
    Return the last day of the month.

    :Args:
        any_day: Example: datetime.today()
    """
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)


def event_today_status(dic):
    """
    To check the status of event for today date.
    Note: in dateutil 0==Monday, while in python datetime 0==Sunday.

    :Args:
        dic: dictionary as {'event': event_object, 'month': 02, 'year': 2015}  Note: event is must.

    :return:
        the dictionary containing the event id, status for today date and the 
        list of execution date of this month. i.e: {  'status': False, 'event_ids': 2, 
                                        'execution_dates': [
                                            datetime.datetime(2014, 12, 19, 0, 0),
                                            datetime.datetime(2014, 12, 20, 0, 0),
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
        # Monday = 1, Tuesday = 2, So (-1) from id is used
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

    :return:
        dictionary containing list of events and their corresponding devices ids.
            i.e: {  'event_list': [eve_obj1, eve_obj2, eve_obj3,...],
                    'device_ids': [1,2,3,4,...],
                }
    """

    event_list = []
    event_list_type = []
    time = datetime.today().time()
    device_ids = []
    # Check for every event whether any event will execute today or not.
    for event in Event.objects.all():
        result = event_today_status({'event': event})
        # # Update event list if event is active for today.
        if result['status']:
            # Update if time now in between event's start and end on time.
            if event.start_on_time <= time and time <= event.end_on_time:
                if event.scheduling_type != 'dety':
                    event_list.append(event)
                else:
                    event_list_type.append(event)
    # Get device ids of all the active events.
    device_ids_specific = Device.objects.filter(event__in=event_list).distinct().values_list('id', flat=True)
    device_type_id = DeviceType.objects.filter(event__in=event_list_type).distinct().values_list('id', flat=True)
    device_ids_type = Device.objects.filter(device_type__in=device_type_id).distinct().values_list('id', flat=True)
    device_ids_type = list(device_ids_type)
    for id in device_ids_specific:
        if id and id not in device_ids_type:
            device_ids_type.append(id)
    # device_ids = device_ids + device_ids_type
    event_list = event_list+ event_list_type
    return {'event_list': event_list, 'device_ids': device_ids_type}


def get_month_event_list(request):
    """
    Method return the json format of the events execution date list
    using ajax call according to the month and year of scheduling_management fullcalendar.

    :Args:
        month: integer
        year: integer

    :return dictionary containing list of dictionary of event detail.
            i.e: {[
                    { 'id': 1, 'title': 'event_name1', 'start': datetime1, 'end': datetime1, 'allDay': False,}
                    { 'id': 1, 'title': 'event_name1', 'start': datetime2, 'end': datetime2, 'allDay': False,}
                    { 'id': 2, 'title': 'event2', 'start': datetime1,... },
                    { 'id': 2, 'title': 'event2', 'start': datetime2,... },...,
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
        result = event_today_status({
            'event': event, 
            'month': month+1, 
            'year': year
        })
        # Update the list if date fall in same month.
        for date in result['execution_dates']:
            if first_day_of_month <= date and date <= last_day_of_month:
                month_schedule_list.append({
                    'id': event.id,
                    'title': event.name,
                    'start': (datetime.combine(date, event.start_on_time)).strftime(fmt),
                    'end': datetime.combine(date, event.end_on_time).strftime(fmt),
                    'allDay': False
                })

    """
    ****************************************
    ****************************************
    * fetch current month's planned events *
    ****************************************
    ****************************************
    """
    if PLANNED_EVENTS_ENABLED:
        now = datetime.now()
        current_timestamp = datetime(
            now.year,
            now.month,
            now.day, 0, 0, 0
        )
        start_date = (current_timestamp + relativedelta(day=1)).strftime('%s')
        end_date = (current_timestamp + relativedelta(day=31)).strftime('%s')

        planned_events = PlannedEvent.objects.filter(
            startdate__gte=start_date,
            startdate__lte=end_date
        ).values(
            'startdate', 'enddate', 'resource_name'
        )

        for pe in planned_events:
            ip_address = pe['resource_name']
            month_schedule_list.append({
                'title': 'Planned Event - {0}'.format(ip_address),
                'start': datetime.fromtimestamp(float(pe['startdate'])).strftime(fmt),
                'end': datetime.fromtimestamp(float(pe['enddate'])).strftime(fmt)
            })

    return HttpResponse (json.dumps({
        'month_schedule_list': month_schedule_list
    }))


# **************************************** SNMP Trap Settings *********************************************
class SelectSNMPTrapSettingsListView(Select2Mixin, ListView):
    """
    Provide selector data for jquery select2 when loading data from Remote.
    :param Select2Mixin:
            ListView:
    :return qs:
    """
    model = SNMPTrapSettings


class SNMPTrapSettingsList(PermissionsRequiredMixin, TemplateView):
    """
    Class Based View for the SNMPTrapSettings data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """

    template_name = 'snmp_trap_settings/snmp_trap_settings_list.html'
    required_permissions = ('inventory.view_snmp_trap_settings',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(SNMPTrapSettingsList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'alias', 'sTitle': 'Trap Name', 'sWidth': '10%', },
            {'mData': 'device_technology__alias', 'sTitle': 'Device Technology', 'sWidth': 'auto', },
            {'mData': 'device_vendor__alias', 'sTitle': 'Device Vendor', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'device_model__alias', 'sTitle': 'Device Model', 'sWidth': 'auto', },
            {'mData': 'device_type__alias', 'sTitle': 'Device Type', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'trap_oid', 'sTitle': 'Trap OID', 'sWidth': '10%', },
            {'mData': 'severity', 'sTitle': 'Severity', 'sWidth': '10%', }]

        #if the user role is Admin or operator or superuser then the action column will appear on the datatable
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class SNMPTrapSettingsListingTable(PermissionsRequiredMixin, 
    DatatableOrganizationFilterMixin, 
    DatatableSearchMixin, 
    BaseDatatableView,
    AdvanceFilteringMixin):
    """
    Class based View to render SNMPTrapSettings Data table. Returns json data for data table.
    :param Mixins- PermissionsRequiredMixin
                   DatatableOrganizationFilterMixin
                   DatatableSearchMixin
                   BaseDatatableView
    :return json_data
    """
    model = SNMPTrapSettings
    columns = ['device_technology__alias', 'device_vendor__alias', 'device_model__alias', 'device_type__alias',
               'alias', 'trap_oid', 'severity']
    order_columns = columns
    required_permissions = ('inventory.view_antenna',)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        for dct in json_data:
            device_id = dct.pop('id')
            if self.request.user.has_perm('inventory.change_snmp_trap_settings'):
                edit_action = '<a href="/snmp_trap_settings/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_snmp_trap_settings'):
                delete_action = '<a href="/snmp_trap_settings/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data


class SNMPTrapSettingsDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the snmp_trap_settings detail.
    """
    model = SNMPTrapSettings
    template_name = 'snmp_trap_settings/snmp_trap_settings_detail.html'
    required_permissions = ('inventory.view_antenna',)


class SNMPTrapSettingsCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Class based view to create new SNMPTrapSettings.
    """
    template_name = 'snmp_trap_settings/snmp_trap_settings_new.html'
    model = SNMPTrapSettings
    form_class = SNMPTrapSettingsForm
    success_url = reverse_lazy('snmp_trap_settings_list')
    required_permissions = ('inventory.add_antenna')


class SNMPTrapSettingsUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
    """
    Class based view to update SNMPTrapSettings .
    """
    template_name = 'snmp_trap_settings/snmp_trap_settings_update.html'
    model = SNMPTrapSettings
    form_class = SNMPTrapSettingsForm
    success_url = reverse_lazy('snmp_trap_settings_list')
    required_permissions = ('inventory.change_antenna',)


class SNMPTrapSettingsDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the SNMPTrapSettings.
    """
    model = SNMPTrapSettings
    template_name = 'snmp_trap_settings/snmp_trap_settings_delete.html'
    success_url = reverse_lazy('snmp_trap_settings_list')
    required_permissions = ('inventory.delete_antenna',)
