"""
=============================================================================
Module contains database models and functions specific to 'user_profile' app.
=============================================================================

Location:
* /nocout_gis/nocout/user_profile/models.py

List of constructs:
=======
Classes
=======
* UserProfile
* Roles
* UserPasswordRecord

=======
Signals
=======
* Signal for setting site instance 'is_device_change' bit on modification and creation in device type 'service' field.
"""

from django.db import models
from django.db.models.signals import post_save, m2m_changed, pre_save
from django.contrib.auth.models import User, Group
from mptt.models import MPTTModel, TreeForeignKey
from organization.models import Organization
import signals as user_signals


class UserProfile(MPTTModel, User):
    """
    Model for creating user profile by extending django auth 'User' class.
    """
    parent = TreeForeignKey('self', null=True, blank=True, related_name='user_children')
    # role = models.ManyToManyField('Roles')
    organization = models.ForeignKey(Organization)
    phone_number = models.CharField('Phone No.', max_length=15, null=True, blank=True)
    company = models.CharField('Company', max_length=100, null=True, blank=True)
    designation = models.CharField('Designation', max_length=100, null=True, blank=True)
    address = models.CharField('Address', max_length=150, null=True, blank=True)
    comment = models.TextField('Comment', null=True, blank=True)
    is_deleted = models.IntegerField('Is Deleted', default=0)
    password_changed_at = models.DateTimeField('Password changed at', null=True, blank=True)
    user_invalid_attempt = models.IntegerField('Invalid attempt', null=True, blank=True, default=0)
    user_invalid_attempt_at = models.DateTimeField('Invalid attemp at', null=True, blank=False)


class Roles(models.Model):
    """
    Model for defining user roles.
    """
    role_name = models.CharField('Role Name', max_length=100, null=True, blank=True)
    role_description = models.CharField('Role Description', max_length=250, null=True, blank=True)

    def __unicode__(self):
        return self.role_description


class UserPasswordRecord(models.Model):
    """
    Model for keeping the record of the passwords used by user.
    """
    user_id = models.IntegerField('User Id', null=True, blank=True)
    password_used = models.CharField('Password', max_length=100, null=True, blank=True)
    password_used_on = models.DateTimeField('Password Used On', auto_now_add=True)


# ************************************ USER PROFILE SIGNALS ************************************

# Set site instance 'is_device_change' bit on device type 'service' field modification or creation.
post_save.connect(user_signals.assign_default_thematics_to_user, sender=UserProfile)

# Assign permissions as per user group.
m2m_changed.connect(user_signals.reassign_permissions, sender=User.groups.through)