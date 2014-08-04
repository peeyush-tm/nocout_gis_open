from django.db import models
from django.contrib.auth.models import User, UserManager
from mptt.models import MPTTModel, TreeForeignKey
from organization.models import Organization


# user profile class
class UserProfile(MPTTModel, User):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='user_children')
    role = models.ManyToManyField('Roles')
    organization = models.ForeignKey(Organization)
    phone_number = models.CharField('Phone No.', max_length=15, null=True, blank=True)
    company = models.CharField('Company', max_length=100, null=True, blank=True)
    designation = models.CharField('Designation', max_length=100, null=True, blank=True)
    address = models.CharField('Address', max_length=150, null=True, blank=True)
    comment = models.TextField('Comment', null=True, blank=True)
    is_deleted = models.IntegerField('Is Deleted', max_length=1, default=0)

# user roles class
class Roles(models.Model):
    role_name = models.CharField('Role Name', max_length=100, null=True, blank=True)
    role_description = models.CharField('Role Description', max_length=250, null=True, blank=True)

    def __unicode__(self):
        return self.role_description


