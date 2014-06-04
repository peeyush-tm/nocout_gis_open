from django.db import models


class Machine(models.Model):
    name = models.CharField('Machine Name', max_length=255, unique=True)
    alias = models.CharField('Alias', max_length=255)
    machine_ip = models.IPAddressField('Machine IP', null=True, blank=True)
    agent_port = models.IntegerField('Agent Port', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name