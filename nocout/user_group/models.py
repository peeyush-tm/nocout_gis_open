from django.db import models
#from audit_log.models.fields import LastUserField
#from audit_log.models.managers import AuditLog
from mptt.models import MPTTModel, TreeForeignKey
from device_group.models import DeviceGroup
                                    
class UserGroup(MPTTModel, models.Model):
    name = models.CharField('Group Name', max_length=50, unique=True)
    alias = models.CharField('Group Alias', max_length=50)
    address = models.CharField('Address', max_length=100, null=True, blank=True)
    location = models.CharField('Location', max_length=100, null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='usergroup_children')
    device_group = models.ManyToManyField(DeviceGroup, through="Organization", null=True, blank=True)
    #audit_log = AuditLog()
    
    def __unicode__(self):
        return self.name
    
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=-True)
    description = models.TextField(null=True, blank=True)
    user_group = models.ForeignKey(UserGroup)
    device_group = models.ForeignKey(DeviceGroup)
