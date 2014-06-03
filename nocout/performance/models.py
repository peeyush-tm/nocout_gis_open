from django.db import models

class PerformanceMetric(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_id = models.IntegerField('Machine ID', null=True, blank=True)
    site_id = models.IntegerField('Site ID', null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    value = models.CharField('Value', max_length=50, null=True, blank=True)
    sys_timestamp = models.DateTimeField('System Timestamp', null=True, blank=True)
    check_timestamp = models.DateTimeField('Check Timestamp', null=True, blank=True)