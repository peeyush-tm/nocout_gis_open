"""
=============================================================================
Module contains database models and functions specific to 'site_instance' app.
=============================================================================

Location:
* /nocout_gis/nocout/site_instance/models.py

List of constructs:
=======
Classes
=======
* SiteInstance
"""

from django.db import models
from machine.models import Machine


class SiteInstance(models.Model):
    """
    Model for storing site instances.
    """
    name = models.CharField('Name', max_length=200, unique=True)
    alias = models.CharField('Alias', max_length=255)
    machine = models.ForeignKey(Machine, null=True, blank=True)
    live_status_tcp_port = models.IntegerField('Live Status TCP Port', null=True, blank=True)
    web_service_port = models.IntegerField('Web Service Port', default=80)
    username = models.CharField('Username', max_length=100, null=True, blank=True)
    password = models.CharField('Password', max_length=100, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    is_device_change = models.IntegerField('Is Device Change', default=0)

    def __unicode__(self):
        return self.name