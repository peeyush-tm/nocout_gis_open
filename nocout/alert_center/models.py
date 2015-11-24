from django.db import models


class GenericAlarm(models.Model):
    id = models.IntegerField(primary_key=True)
    device_name = models.CharField(max_length=128)
    ip_address = models.CharField(max_length=20)
    # device_type = models.CharField(max_length=50)
    # device_technology = models.CharField(max_length=50)
    # device_vendor = models.CharField(max_length=50)
    # device_model = models.CharField(max_length=50)
    trapoid = models.CharField(max_length=100)
    eventname = models.CharField(max_length=100)
    eventno = models.CharField(max_length=50)
    severity = models.CharField(max_length=20)
    uptime = models.CharField(max_length=20)
    traptime = models.CharField(max_length=30)
    # component_name = models.CharField(max_length=50)
    # component_id = models.CharField('Component ID', default='NA', max_length=50, null=True, blank=True)
    description = models.CharField(max_length=256)
    alarm_count = models.IntegerField(null=True,blank=True)
    first_occurred = models.DateTimeField(null=True,blank=True)
    last_occurred = models.DateTimeField(null=True,blank=True)
    is_active = models.IntegerField(null=True,blank=True)

    class Meta:
        abstract = True


class HistoryAlarms(GenericAlarm):
    pass
    #class Meta:
    #    db_table = 'history_alarms'
    #    managed = False


class StatusAlarms(GenericAlarm):
    pass
    #class Meta:
    #    db_table = 'current_alarms'
    #    managed = False
