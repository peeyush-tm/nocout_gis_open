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
        phones = self.phones.replace(' ','')
        phones = self.phones.split(',')
        return phones

    def get_phones_field(value):
        return ",".join(value)

    def get_emails(self):
        emails = self.emails.replace(' ','')
        emails = self.emails.split(',')
        return emails

    def get_emails_field(value):
        return ",".join(value)


class EscalationStatus(models.Model):
    """
    Class to define model AlarmEscalation.
    """
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Sent'),
    )

    PERFOEMANCE_CHOICES = (
        (0, 'Bad'),
        (1, 'Good')
    )

    organization = models.ForeignKey(Organization)
    device_type = models.CharField(max_length=100, db_index=True)
    service = models.CharField(max_length=100, db_index=True)
    service_data_source =  models.CharField(max_length=100, db_index=True)
    ip = models.IPAddressField()
    l1_email_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l1_phone_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l2_email_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l2_phone_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l3_email_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l3_phone_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l4_email_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l4_phone_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l5_email_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l5_phone_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l6_email_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l6_phone_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l7_email_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    l7_phone_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    status_since = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=20)
    old_status = models.IntegerField(choices=PERFOEMANCE_CHOICES)
    new_status = models.IntegerField(choices=PERFOEMANCE_CHOICES)
