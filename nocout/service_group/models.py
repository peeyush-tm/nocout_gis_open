from django.db import models
from service.models import Service


class ServiceGroup(models.Model):
    """
    Service Group Model Columns Declaration.
    """
    servicegroup_name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100)
    service = models.ManyToManyField(Service, blank=True, null=True)
    notes = models.CharField(max_length=100, null=True, blank=True)
    notes_url = models.URLField(max_length=200, null=True, blank=True)
    action_url = models.URLField(max_length=200, null=True, blank=True)