from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from organization.models import Organization
from user_profile.models import UserProfile


# user_group model
class UserGroup(MPTTModel, models.Model):
    name = models.CharField('Group Name', max_length=50, unique=True)
    alias = models.CharField('Group Alias', max_length=50)
    users = models.ManyToManyField(UserProfile)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='usergroup_children')
    organization = models.ForeignKey(Organization)
    address = models.CharField('Address', max_length=100, null=True, blank=True)
    location = models.CharField('Location', max_length=100, null=True, blank=True)
    is_deleted = models.IntegerField('Is Deleted', max_length=1, default=0)

    def __unicode__(self):
        return self.name

