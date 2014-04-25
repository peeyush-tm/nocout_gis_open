from django.db import models

class SiteInstance(models.Model):
    name = models.CharField('Name', max_length=200, unique=True)
    description = models.TextField('Description', null=True, blank=True)
    site_ip = models.IPAddressField('IP Address')
    agent_port = models.IntegerField('Agent Port', null=True, blank=True)
    live_status_tcp_port = models.IntegerField('Live Status TCP Port', null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
