from django.db import models

from user_profile.models import UserProfile
from organization.models import Organization
from device.models import Device, DeviceType, DeviceModel, DeviceVendor, DeviceTechnology
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
        ('', 'Select'),
        ('devi', 'Device Specific'),
        ('dety', 'Device Type'),
        ('cust', 'Customer Device'),
        ('netw', 'Network Device'),
        ('back', 'Backhaul Device'),
    )
    name = models.CharField('Title', max_length=255)
    repeat = models.CharField('Repeats', max_length=10, choices=REPEAT, default='dai')
    repeat_every = models.IntegerField('Repeat every', max_length=2, null=True, blank=True)
    repeat_on = models.ManyToManyField(Weekdays, 'Repeat on')
    repeat_by = models.CharField('Repeat by', max_length=10, null=True, blank=True, choices=REPEAT_BY, default='dofm')
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    start_on = models.DateField('Starts on')
    start_on_time = models.TimeField('Start time')
    end_on_time = models.TimeField('End time')
    end_never = models.BooleanField('Ends', default=False)
    end_after = models.IntegerField('Ends after', null=True, blank=True)
    end_on = models.DateField('Ends on', null=True, blank=True)
    created_by = models.ForeignKey(UserProfile)
    organization = models.ForeignKey(Organization)
    scheduling_type = models.CharField('Scheduling type', max_length=10, choices=SCHEDULING_TYPE, default='')
    device = models.ManyToManyField(Device, null=True, blank=True)
    device_type = models.ManyToManyField(DeviceType, null=True, blank=True)


class SNMPTrapSettings(models.Model):
    device_technology = models.ForeignKey(DeviceTechnology, null=True, blank=True, on_delete=models.SET_NULL,
                                          related_name='device_technology')
    device_vendor = models.ForeignKey(DeviceVendor, null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='device_vendor')
    device_model = models.ForeignKey(DeviceModel, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='device_model')
    device_type = models.ForeignKey(DeviceType, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='device_type')
    name = models.CharField('Trap Name', max_length=150)
    alias = models.CharField('Trap Alias', max_length=150, null=True, blank=True)
    trap_oid = models.CharField('Trap OID', max_length=255, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
