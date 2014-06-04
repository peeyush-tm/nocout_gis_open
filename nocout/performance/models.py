from django.db import models
from datetime import datetime

class PerformanceMetric(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True)
    service_name = models.CharField('Service Name', max_length=100, null=True)
    machine_id = models.IntegerField('Machine ID', null=True)
    site_id = models.IntegerField('Site ID', null=True)
    data_source = models.CharField('Data Source', max_length=100, null=True)
    current_value = models.CharField('Current Value', max_length=20, default=0)
    min_value = models.CharField('Min Value', max_length=20, default=0)
    max_value = models.CharField('Max Value', max_length=20, default=0)
    avg_value = models.CharField('Avg Value', max_length=20, default=0)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, default=0)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, default=0)
    sys_timestamp = models.DateTimeField(default=datetime.now, null=True)
    check_timestamp = models.DateTimeField(default=datetime.now, null=True)

    def __unicode__(self):
        return self.device_name

