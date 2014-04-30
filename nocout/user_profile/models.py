from django.db import models
from django.contrib.auth.models import User, UserManager
from user_group.models import UserGroup
from mptt.models import MPTTModel, TreeForeignKey


# user profile class
class UserProfile(MPTTModel, User):
    admin = 'Admin'
    operator = 'Operator'
    viewer = 'Viewer'
    ROLES = (
        (operator, 'Operator'),
        (viewer, 'Viewer')
    )
    parent = TreeForeignKey('self', null=True, blank=True, related_name='user_children')
    role = models.ManyToManyField('Roles', null=True, blank=True)
    user_group = models.ManyToManyField(UserGroup, through='Department', null=True, blank=True)
    user_group.help_text = ''
    phone_number = models.CharField('Phone No.', max_length=15, null=True, blank=True)
    company = models.CharField('Company', max_length=100, null=True, blank=True)
    designation = models.CharField('Designation', max_length=100, null=True, blank=True)
    address = models.CharField('Address', max_length=150, null=True, blank=True)
    comment = models.TextField('Comment', null=True, blank=True)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()


# user roles class
class Roles(models.Model):
    role_name = models.CharField('Role Name', max_length=100, null=True, blank=True)
    role_description = models.CharField('Role Description', max_length=250, null=True, blank=True)

    def __unicode__(self):
        return self.role_description


# user_profile & user_group relationship class
class Department(models.Model):
    user_profile = models.ForeignKey(UserProfile)
    user_group = models.ForeignKey(UserGroup)