from django.db import models


class GenericAlarm(models.Model):
    id = models.IntegerField(primary_key=True)
    device_name = models.CharField(max_length=128)
    ip_address = models.CharField(max_length=20)
    device_type = models.CharField(max_length=50)
    device_technology = models.CharField(max_length=50)
    device_vendor = models.CharField(max_length=50)
    device_model = models.CharField(max_length=50)
    trapoid = models.CharField(max_length=100)
    eventname = models.CharField(max_length=100)
    eventno = models.CharField(max_length=50)
    severity = models.CharField(max_length=20)
    uptime = models.CharField(max_length=20)
    traptime = models.CharField(max_length=30)
    component_name = models.CharField(max_length=50)
    description = models.CharField(max_length=256)

    class Meta:
        abstract = True


class HistoryAlarms(GenericAlarm):

    class Meta:
        db_table = 'history_alarms'
        managed = False


class ClearAlarms(GenericAlarm):

    class Meta:
        db_table = 'clear_alarms'
        managed = False


class CurrentAlarms(GenericAlarm):

    class Meta:
        db_table = 'current_alarms'
        managed = False
