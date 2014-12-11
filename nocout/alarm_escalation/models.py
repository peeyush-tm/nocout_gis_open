from django.db import models
from organization.models import Organization
from device.models import DeviceType, DeviceTechnology
from service.models import Service, ServiceDataSource
from inventory.models import BaseStation

LEVEL_CHOICES = (
    (1, 'Level 1'),
    (2, 'Level 2'),
    (3, 'Level 3'),
    (4, 'Level 4'),
    (5, 'Level 5'),
    (6, 'Level 6'),
    (7, 'Level 7'),
)


class EscalationLevel(models.Model):
    """
    Class to define model Level.
    """
    name = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=1)
    region_name = models.CharField('Location Region', max_length=50, default='', blank=True)
    organization = models.ForeignKey(Organization)
    emails = models.TextField('Emails', default='', blank=True)
    phones = models.TextField('Phones', default='', blank=True)
    device_type = models.ForeignKey(DeviceType)
    service = models.ForeignKey(Service)
    service_data_source = models.ForeignKey(ServiceDataSource)
    alarm_age = models.IntegerField('Alarm Age')

    def __unicode__(self):
        return '%s' % (self.get_name_display())

    def get_phones(self):
        phones = self.phones.split(',')
        return phones

    def get_phones_field(value):
        return ",".join(value)

    def get_emails(self):
        phones = self.emails.split(',')
        return phones

    def get_emails_field(value):
        return ",".join(value)


class AlarmEscalation(models.Model):
    """
    Class to define model AlarmEscalation.
    """
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Sent'),
    )

    level = models.ManyToManyField(EscalationLevel)
    technology = models.ForeignKey(DeviceTechnology)
    base_station = models.ForeignKey(BaseStation)
    ip = models.IPAddressField('IP Address')
    l1_email_status = models.IntegerField('Level1 Email Status', default=0, choices=STATUS_CHOICES)
    l1_phone_status = models.IntegerField('Level1 SMS Status', default=0, choices=STATUS_CHOICES)
    l2_email_status = models.IntegerField('Level2 Email Status', default=0, choices=STATUS_CHOICES)
    l2_phone_status = models.IntegerField('Level2 SMS Status', default=0, choices=STATUS_CHOICES)
    l3_email_status = models.IntegerField('Level3 Email Status', default=0, choices=STATUS_CHOICES)
    l3_phone_status = models.IntegerField('Level3 SMS Status', default=0, choices=STATUS_CHOICES)
    l4_email_status = models.IntegerField('Level4 Email Status', default=0, choices=STATUS_CHOICES)
    l4_phone_status = models.IntegerField('Level4 SMS Status', default=0, choices=STATUS_CHOICES)
    l5_email_status = models.IntegerField('Level5 Email Status', default=0, choices=STATUS_CHOICES)
    l5_phone_status = models.IntegerField('Level5 SMS Status', default=0, choices=STATUS_CHOICES)
    l6_email_status = models.IntegerField('Level6 Email Status', default=0, choices=STATUS_CHOICES)
    l6_phone_status = models.IntegerField('Level6 SMS Status', default=0, choices=STATUS_CHOICES)
    l7_email_status = models.IntegerField('Level7 Email Status', default=0, choices=STATUS_CHOICES)
    l7_phone_status = models.IntegerField('Level7 SMS Status', default=0, choices=STATUS_CHOICES)
    alert_description = models.TextField('Alert Description', default='', blank=True)
    status_since = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)

    def get_level(self, age):
        to_level = None
        for level in self.level.all():
            if age>=level.alarm_age:
                to_level = level
        return to_level
