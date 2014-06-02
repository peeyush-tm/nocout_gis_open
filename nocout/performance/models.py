from django.db import models
from device.models import Device
from service.models import Service

class PerformanceMetric(models.Model):
    device = models.ForeignKey(Device, null=True, blank=True)
    service = models.ForeignKey(Service, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    value = models.CharField(max_length=500, null=True, blank=True)