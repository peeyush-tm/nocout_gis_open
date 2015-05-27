"""
================================================================
Module contains permissions for groups/roles defined in project.
================================================================
Roles:
* Admin
* Operator
* Viewer

Usage:
* Used to modify permissions assigned to different roles in project.

Location:
* /nocout_gis/nocout/user_profile/permissions.py

List of constructs:
=========
Variables
=========
* admin_perms
* operator_perms
* viewer_perms

======================
Additional Permissions
======================
* Create permission to allow sync
> from django.contrib.auth.models import Permission
> from django.contrib.contenttypes.models import ContentType
> ct = ContentType.objects.get(model='device')
> Permission.objects.create(codename='can_sync', name='Can sync devices', content_type=ct)
"""

# List of permissions assigned to 'admin' role.
admin_perms = [
    'activity_stream.view_useraction',
    'auth.add_user',
    'auth.change_user',
    'auth.delete_user',
    'auth.view_user',
    'device.add_device',
    'device.delete_device',
    'device.sync_devices',
    'device.change_device',
    'device.view_device',
    'device.view_devicefrequency',
    'inventory.add_antenna',
    'inventory.delete_antenna',
    'inventory.change_antenna',
    'inventory.view_antenna',
    'inventory.add_backhaul',
    'inventory.delete_backhaul',
    'inventory.change_backhaul',
    'inventory.view_backhaul',
    'inventory.add_basestation',
    'inventory.delete_basestation',
    'inventory.change_basestation',
    'inventory.view_basestation',
    'inventory.add_circuit',
    'inventory.delete_circuit',
    'inventory.change_circuit',
    'inventory.view_circuit',
    'inventory.add_customer',
    'inventory.delete_customer',
    'inventory.change_customer',
    'inventory.view_customer',
    'inventory.view_iconsettings',
    'inventory.view_livepollingsettings',
    'inventory.add_sector',
    'inventory.delete_sector',
    'inventory.change_sector',
    'inventory.view_sector',
    'inventory.add_substation',
    'inventory.delete_substation',
    'inventory.change_substation',
    'inventory.view_substation',
    'inventory.view_thematicsettings',
    'inventory.view_thresholdconfiguration',
    'organization.add_organization',
    'organization.change_organization',
    'organization.delete_organization',
    'organization.view_organization',
    'user_profile.add_userprofile',
    'user_profile.change_userprofile',
    'user_profile.view_userprofile',
    'user_profile.delete_userprofile',
    'alarm_escalation.add_escalationlevel',
    'alarm_escalation.change_escalationlevel',
    'alarm_escalation.delete_escalationlevel',
    'alarm_escalation.view_escalationlevel',
    'scheduling_management.add_event',
    'scheduling_management.change_event',
    'scheduling_management.delete_event',
    'scheduling_management.view_event',
]

# List of permissions assigned to 'operator' role.
operator_perms = [
    'activity_stream.view_useraction',
    'auth.view_user',
    'device.view_device',
    'device.view_devicefrequency',
    'inventory.change_antenna',
    'inventory.view_antenna',
    'inventory.change_backhaul',
    'inventory.view_backhaul',
    'inventory.change_basestation',
    'inventory.view_basestation',
    'inventory.change_circuit',
    'inventory.view_circuit',
    'inventory.change_customer',
    'inventory.view_customer',
    'inventory.view_iconsettings',
    'inventory.view_livepollingsettings',
    'inventory.change_sector',
    'inventory.view_sector',
    'inventory.change_substation',
    'inventory.view_substation',
    'inventory.view_thematicsettings',
    'inventory.view_thresholdconfiguration',
    'organization.view_organization',
    'user_profile.view_userprofile',
    'alarm_escalation.view_escalationlevel',
    'scheduling_management.view_event',
]

# List of permissions assigned to 'viewer' role.
viewer_perms = [
    'device.view_device',
    'device.view_devicefrequency',
    'inventory.view_antenna',
    'inventory.view_backhaul',
    'inventory.view_basestation',
    'inventory.view_circuit',
    'inventory.view_customer',
    'inventory.view_iconsettings',
    'inventory.view_livepollingsettings',
    'inventory.view_sector',
    'inventory.view_substation',
    'inventory.view_thematicsettings',
    'inventory.view_thresholdconfiguration',
    'alarm_escalation.view_escalationlevel',
    'scheduling_management.view_event',
]

# List of custom permissions which we want to be created in database.
# If 'content_type' is defined for new perm then dictionary format is like,
# {
#     'codename': 'can_sync',
#     'name': 'Can sync devices',
#     'content_type': {
#         'app_label': 'device',
#         'model': 'device'
#     }
# }

custom_perms = [
    # Create device sync permission.
    {
        'codename': 'sync_devices',
        'name': 'Can sync devices',
        'content_type': {
            'app_label': 'device',
            'model': 'device'
        }
    }
]