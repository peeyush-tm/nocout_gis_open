from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from device.models import Device
from organization.models import Organization


# device_group model
class DeviceGroup(MPTTModel, models.Model):
    name = models.CharField('Name', max_length=50, unique=True)
    alias = models.CharField('Alias', max_length=200)
    devices = models.ManyToManyField(Device, null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='devicegroup_children')
    organization = models.ForeignKey(Organization)
    is_deleted = models.IntegerField('Is Deleted', max_length=1, default=0)

    def __unicode__(self):
        return self.name
