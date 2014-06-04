from django.db import models
from machine.models import Machine


class SiteInstance(models.Model):
    name = models.CharField('Name', max_length=200, unique=True)
    alias = models.CharField('Alias', max_length=255, null=True, blank=True)
    machine = models.ForeignKey(Machine, null=True, blank=True)
    site_ip = models.IPAddressField('IP Address')
    live_status_tcp_port = models.IntegerField('Live Status TCP Port', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name
    
