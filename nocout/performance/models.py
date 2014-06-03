from django.db import models

class PerformanceMetric(models.Model):
    device_name = models.CharField('Device Name', max_length=100)
    service_name = models.CharField('Service Name', max_length=100)
    machine_id = models.IntegerField('Machine ID')
    site_id = models.IntegerField('Site ID')
    data_source = models.CharField('Data Source', max_length=100)
    value = models.CharField('Value', max_length=50)
    sys_timestamp = models.DateTimeField('System Timestamp')
    check_timestamp = models.DateTimeField('Check Timestamp')