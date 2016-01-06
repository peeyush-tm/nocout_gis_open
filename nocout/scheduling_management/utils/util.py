import datetime
from datetime import timedelta
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from scheduling_management.models import Event
from django.db.models.query import ValuesQuerySet, Q


class SchedulingManagementGateway:
    """
    This class works as gateway between Scheduling management utils & other apps
    """

    def get_onDate_status(self, device_name, device_type, scheduling_type):
        """
        :param eventDict:
        """
        param1 = get_onDate_status(device_name, device_type, scheduling_type)

        return param1


def last_day_of_the_month(any_day):
    """
    Return the last day of the month.

    :Args:
        any_day: Example: datetime.today()
    """
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)


def get_onDate_status(device_name, device_type, scheduling_type):
    """
    To check the status of event for today date.
    Note: in dateutil 0==Monday, while in python datetime 0==Sunday.

    :Args:
        eventList: list of dictionary which are event objects as [{event_obj1},{event_obj2}......]  Note: event is must.

    :return:
        the dictionary containing the event id, status for today date and the
        list of execution date of this month. i.e: {  'status': False, 'event_ids': 2,
                                        'execution_dates': [
                                            datetime.datetime(2014, 12, 19, 0, 0),
                                            datetime.datetime(2014, 12, 20, 0, 0),
                                            ]
                                        }
    """

    # print "**********device_name - %s", device_name
    current_timestamp = datetime.datetime.now()

    columns_list = [
        'scheduling_type', 'id', 'start_on', 'start_on_time', 'end_on', 'end_after', 'repeat_by',
        'end_on_time', 'device__device_name', 'device__ip_address', 'repeat_every', 'repeat', 'repeat_on'
    ]

    scheduling_list = Event.objects.extra(select={
        'start_on_time': 'concat(start_on," ",start_on_time)',
        'end_on_time': 'concat(end_on," ",end_on_time)'
    }).filter(
            Q(scheduling_type__in=scheduling_type)
            &
            (
                (
                    Q(start_on_time__isnull=False)
                    &
                    Q(end_on_time__isnull=False)
                    &
                    Q(start_on_time__lte=current_timestamp)
                    &
                    Q(end_on_time__gte=current_timestamp)
                )
                |
                (
                    Q(start_on_time__isnull=True)
                    &
                    Q(end_on_time__isnull=False)
                    &
                    Q(end_on_time__gte=current_timestamp)
                )
                |
                (
                    Q(start_on_time__isnull=False)
                    &
                    Q(end_on_time__isnull=True)
                    &
                    Q(start_on_time__lte=current_timestamp)
                )
            )
    ).values(*columns_list)

    # Select scheduling events which are scheduled by device type
    device_type_schedules = scheduling_list.filter(scheduling_type__iexact='dety')

    # Select scheduling events which are scheduled by specific device
    device_schedules = scheduling_list.exclude(
            id__in=device_type_schedules.values_list('id', flat=True)
    )

    schdeuledDownCond1 = device_schedules.filter(device__device_name=device_name).exists()
    schdeuledDownCond2 = device_type_schedules.filter(device_type__name=device_type).exists()

    scheduling_list = list(scheduling_list)

    # print schdeuledDownCond1, schdeuledDownCond2

    if schdeuledDownCond1:
        try:
            refined_list = device_schedules.filter(device__device_name=device_name)
            for event in refined_list:
                # print "********** EVENT -> ", event

                today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                status = False  # initialize that there is no active event.
                count = 0  # initialize that event end after 0(zero) occurence.

                execution_dates = []
                last_day_of_month = last_day_of_the_month(today)
                year = (today.year)
                month = (today.month)
                # Set the start and end of month according to month and year.
                month_start = today.replace(year=year, month=month, day=1)
                month_end = last_day_of_the_month(month_start).date()

                # event_ids = event.id
                # Note: we need start and end date to find the list of execution date of event.
                # Set the start to the start_on (i.e: event.start_on) of the event.
                start = event['start_on']
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
                if event['end_on']:
                    event_end = event['end_on'] if event['end_on'] <= month_end else month_end
                elif event['end_after']:
                    count = event['end_after']  # case2: end after particular occurence
                # finally update the end date to event_end.
                end = event_end
                # get the frequency of occurence of event by default it is 1.
                interval = 1 if not event['repeat_every'] else event['repeat_every']

                # Case to repeat the event on daily basis.
                if event['repeat'] == 'dai':
                    # print "In DAILY"
                    try:
                        execution_dates = list(rrule(DAILY, dtstart=start, interval=interval, count=count, until=end))
                    except Exception, e:
                        print e
                    # check whether the event will execute today or not.
                    if today in execution_dates:
                        status = True


                # Case to repeat the event on weekly basis.
                elif event['repeat'] == 'wee':
                    # print "In WEEKLY"
                    # get the days of weeks to repeat the event.
                    # Monday = 1, Tuesday = 2, So (-1) from id is used
                    weekday = tuple([int(event['repeat_on']) - 1])
                    # print weekday
                    execution_dates = list(
                            rrule(WEEKLY, dtstart=start, interval=interval, count=count, until=end, byweekday=weekday))
                    if today in execution_dates:
                        status = True
                    if status:
                        break

                # Case to repeat the event on monthly basis.
                elif event['repeat'] == 'mon':
                    # print "In MONTHLY"
                    # repeat event on day of month.
                    if event['repeat_by'] == 'dofm':
                    	# print "In Dofm"
                        execution_dates = list(rrule(MONTHLY, dtstart=start, interval=interval, count=count, until=end))
                        # print execution_dates
                        if today in execution_dates:
                            status = True
                    else:  # case: day of the week
                        weekno = (start.day + 7 - 1) / 7  # get the position of week.
                        weekday = start.isocalendar()[2] - 1
                        execution_dates = list(
                                rrule(MONTHLY, dtstart=start, interval=interval, count=count, until=end,
                                      bysetpos=weekno,
                                      byweekday=weekday))
                        if today in execution_dates:
                            status = True

                # Case to repeat the event on yearly basis.
                elif event['repeat'] == 'yea':
                    # print "In YEARLY"
                    if today in list(rrule(YEARLY, dtstart=start, interval=interval, count=count, until=end)):
                        status = True

                # Case to repeat the event on tuesday and thursday.
                elif event['repeat'] == 'tat':
                    # print "In TAT"
                    # 1==Tuesday and 3==Thursday.
                    execution_dates = list(rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(1, 3)))
                    if today in execution_dates:
                        status = True

                # Case to repeat the event on monday, wednesday and friday.
                elif event['repeat'] == 'mwf':
                    # print "In MWF"
                    # 0==Monday, 2==Wednesday and 4==Friday.
                    execution_dates = list(rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(0, 2, 4)))
                    if today in execution_dates:
                        status = True

                # Case to repeat the event on monday to friday.
                elif event['repeat'] == 'mtf':
                    # print "In MTF"
                    # Note: 0==Monday, 1==Tuesday, 2==Wednesday, 3==Thursday and 4==Friday.
                    execution_dates = list(
                            rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(0, 1, 2, 3, 4)))
                    if today in execution_dates:
                        status = True
            # print status
            return status

        except Exception, err:
            print err

    elif schdeuledDownCond2:
        try:
            refined_list = device_type_schedules.filter(device_type__name=device_type)
            for event in refined_list:
                # print "********** EVENT -> ", event

                today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                status = False  # initialize that there is no active event.
                count = 0  # initialize that event end after 0(zero) occurence.

                execution_dates = []
                last_day_of_month = last_day_of_the_month(today)
                year = (today.year)
                month = (today.month)
                # Set the start and end of month according to month and year.
                month_start = today.replace(year=year, month=month, day=1)
                month_end = last_day_of_the_month(month_start).date()

                # event_ids = event.id
                # Note: we need start and end date to find the list of execution date of event.
                # Set the start to the start_on (i.e: event.start_on) of the event.
                start = event['start_on']
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
                if event['end_on']:
                    event_end = event['end_on'] if event['end_on'] <= month_end else month_end
                elif event['end_after']:
                    count = event['end_after']  # case2: end after particular occurence
                # finally update the end date to event_end.
                end = event_end
                # get the frequency of occurence of event by default it is 1.
                interval = 1 if not event['repeat_every'] else event['repeat_every']

                # Case to repeat the event on daily basis.
                if event['repeat'] == 'dai':
                    # print "In DAILY"
                    try:
                        execution_dates = list(rrule(DAILY, dtstart=start, interval=interval, count=count, until=end))
                    except Exception, e:
                        print e
                    # check whether the event will execute today or not.
                    if today in execution_dates:
                        status = True


                # Case to repeat the event on weekly basis.
                elif event['repeat'] == 'wee':
                    # print "In WEEKLY"
                    # get the days of weeks to repeat the event.
                    # Monday = 1, Tuesday = 2, So (-1) from id is used
                    weekday = tuple([int(event['repeat_on']) - 1])
                    # print weekday
                    execution_dates = list(
                            rrule(WEEKLY, dtstart=start, interval=interval, count=count, until=end, byweekday=weekday))
                    if today in execution_dates:
                        status = True
                    if status:
                        break

                # Case to repeat the event on monthly basis.
                elif event['repeat'] == 'mon':
                    # print "In MONTHLY"
                    # repeat event on day of month.
                    if event['repeat_by'] == 'dofm':
                        execution_dates = list(rrule(MONTHLY, dtstart=start, interval=interval, count=count, until=end))
                        # print execution_dates
                        if today in execution_dates:
                            status = True
                    else:  # case: day of the week
                        weekno = (start.day + 7 - 1) / 7  # get the position of week.
                        weekday = start.isocalendar()[2] - 1
                        execution_dates = list(
                                rrule(MONTHLY, dtstart=start, interval=interval, count=count, until=end,
                                      bysetpos=weekno,
                                      byweekday=weekday))
                        if today in execution_dates:
                            status = True

                # Case to repeat the event on yearly basis.
                elif event['repeat'] == 'yea':
                    # print "In YEARLY"
                    if today in list(rrule(YEARLY, dtstart=start, interval=interval, count=count, until=end)):
                        status = True

                # Case to repeat the event on tuesday and thursday.
                elif event['repeat'] == 'tat':
                    # print "In TAT"
                    # 1==Tuesday and 3==Thursday.
                    execution_dates = list(rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(1, 3)))
                    if today in execution_dates:
                        status = True

                # Case to repeat the event on monday, wednesday and friday.
                elif event['repeat'] == 'mwf':
                    # print "In MWF"
                    # 0==Monday, 2==Wednesday and 4==Friday.
                    execution_dates = list(rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(0, 2, 4)))
                    if today in execution_dates:
                        status = True

                # Case to repeat the event on monday to friday.
                elif event['repeat'] == 'mtf':
                    # print "In MTF"
                    # Note: 0==Monday, 1==Tuesday, 2==Wednesday, 3==Thursday and 4==Friday.
                    execution_dates = list(
                            rrule(DAILY, dtstart=start, count=count, until=end, byweekday=(0, 1, 2, 3, 4)))
                    if today in execution_dates:
                        status = True
            # print status
            return status

        except Exception, err:
        	print err


