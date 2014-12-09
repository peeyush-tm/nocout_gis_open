from django.db import models

from user_profile.models import UserProfile
from organization.models import Organization
from device.models import Device, DeviceType
from service.models import Service, ServiceDataSource


class Weekdays(models.Model):
    """
    Display the weekdays if repeat of event is by Weeks.
    """
    WEEKDAYS = (
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    )
    name = models.CharField('Weekdays', max_length=128, null=True, blank=True,
                            choices=WEEKDAYS, unique=True)

    def __unicode__(self):
        return self.name

class Event(models.Model):
    """
    Event Model Columns Declaration.
    """

    REPEAT = (
        ('dai', 'Daily'),
        ('mtf', 'Every weekday (Monday to Friday)'),
        ('mwf', 'Every Monday, Wednesday, and Friday'),
        ('tat', 'Every Tuesday and Thursday'),
        ('wee', 'Weekly'),
        ('mon', 'Monthly'),
        ('yea', 'Yearly'),
    )

    # choices if repeat is by month.
    REPEAT_BY = (
        ('dofm', 'day of the month'),
        ('dofw', 'day of the week'),
    )

    # choices for the scheduling type.
    SCHEDULING_TYPE = (
        (None, 'Select'),
        ('devi', 'Device Specific'),
        ('dety', 'Device Type'),
        ('serv', 'Service'),
        ('sdso', 'Service Data Source'),
    )
    name = models.CharField('Title', max_length=255)
    repeat = models.CharField('Repeats', max_length=10, choices=REPEAT, default='dai')
    repeat_every = models.IntegerField('Repeat every', max_length=2, null=True, blank=True)
    repeat_on = models.ManyToManyField(Weekdays, 'Repeat on')
    repeat_by = models.CharField('Repeat by', max_length=10, null=True, blank=True, choices=REPEAT_BY, default='dofm')
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    start_on = models.DateTimeField('Starts on')
    end_never = models.BooleanField('Ends', default=False)
    end_after = models.IntegerField('Ends after', null=True, blank=True)
    end_on = models.DateTimeField('Ends on', null=True, blank=True)
    created_by = models.ForeignKey(UserProfile)
    organization = models.ForeignKey(Organization)
    scheduling_type = models.CharField('Scheduling type', max_length=10, choices=SCHEDULING_TYPE, default='')
    device = models.ManyToManyField(Device)
