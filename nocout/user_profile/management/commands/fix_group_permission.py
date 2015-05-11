"""
===============================================================
Module contains custom commands specific to 'user_profile' app.
===============================================================

Location:
* /nocout_gis/nocout/user_profile/management/commands/fix_group_permission.py

List of constructs:
=======
Classes
=======
* Command
"""

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from user_profile.permissions import admin_perms, operator_perms, viewer_perms


class Command(BaseCommand):
    """
    Add permissions to associated groups.

    Get groups permissions from '/nocout_gis/nocout/user_profile/permissions.py' in list format
    for e.g. admin_perms = ['activity_stream.view_useraction',
                            'auth.add_user',
                            'auth.change_user',
                            'auth.delete_user',
                            'auth.view_user',
                            'device.change_device',
                            'device.view_device',
                            'device.view_devicefrequency',
                            'inventory.change_antenna']

    """
    args = '<directory ...>'
    help = 'Adds Permissions to each group according to permissions list provided.'

    def handle(self, *args, **options):

        def fix_group_permissions(group, perms):
            """
            Add permissions to group from permission list and delete permissions from
            group which is not in permission list.

            Perms File: /nocout_gis/nocout/user_profile/permissions.py
            """
            perm_list = []

            for data in perms:
                # Seperate 'app_label' and 'codename' from perm string ('data') for e.g. if perm string is
                # 'device.view_device' then app_label is 'device' and code_name is 'view_device'
                app_label, codename = data.split('.')
                perm = Permission.objects.get(codename=codename, content_type__app_label=app_label)
                group.permissions.add(perm)
                perm_list.append(perm.id)

            for perm in group.permissions.exclude(id__in=perm_list):
                group.permissions.remove(perm)

        def create_view_permissions():
            """
            Create view permissions for all models if already not present in database.

            ==========
            Reference:
            ==========

            ===========
            ContentType model track all of the models installed in project.
            It includes following fields:
            1. name - The human-readable name of the content type for e.g. 'migration history'.
            2. app_label - The name of the application the model is part of for e.g. 'south'.
            3. model - The name of the model class for e.g. 'migrationhistory'.

            ==========
            Permission model store basic permissions for project.
            It includes following fields:
            1. codename - The name of permissions used in application code for e.g. 'can_publish'
            2. name - The human-readable name of permission for e.g. 'Can Publish Posts'
            3. content_type - ContentType object to specify model and app to which permission is associated.

            =====
            Group model used for catagorizing the application users.
            It includes following fields:
            1. name - Name of the group.
            2. permissions - M2M field for assigning permissions to the group.
            """
            # Loop on all content types available.
            for content_type in ContentType.objects.all():
                # Get code name for permission for e.g. 'view_user'.
                codename = "view_%s" % content_type.model
                # Create permission if already not present in database.
                Permission.objects.get_or_create(content_type=content_type,
                                                 codename=codename,
                                                 defaults={'name': "Can view %s" % content_type.name})

        create_view_permissions()

        group_admin = Group.objects.get(name='group_admin')
        fix_group_permissions(group_admin, admin_perms)

        group_operator = Group.objects.get(name='group_operator')
        fix_group_permissions(group_operator, operator_perms)

        group_viewer = Group.objects.get(name='group_viewer')
        fix_group_permissions(group_viewer, viewer_perms)
