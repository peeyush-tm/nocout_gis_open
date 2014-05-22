from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class DeviceGroup(MPTTModel, models.Model):
    name = models.CharField('Name', max_length=50, unique=True)
    alias = models.CharField('Alias', max_length=200)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='devicegroup_children')
    location = models.CharField('Location', max_length=200, null=True, blank=True)
    address = models.CharField('Address', max_length=200, null=True, blank=True)
    is_deleted = models.IntegerField('Is Deleted', max_length=1, default=0)

    def __unicode__(self):
        return self.name