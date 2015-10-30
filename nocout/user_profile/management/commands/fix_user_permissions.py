"""
===================================================================================
Module contains custom command 'fix_user_permissions' for fixing group permissions.
===================================================================================

Location:
* /nocout_gis/nocout/user_profile/management/commands/fix_user_permissions.py

Usage:
* ./manage.py fix_user_permissions

List of constructs:
=======
Classes
=======
* Command
"""
import operator
from itertools import izip
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, User
from django.db.models import Q
from django.db import connection
from user_profile.permissions import admin_perms, operator_perms, viewer_perms

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Add group permissions to each user separately.

    Workflow:
    1. Create view permissions for all apps present in project using 'create_view_permissions()'.
    2. Fetch all users.
    3. Get groups permissions from '/nocout_gis/nocout/user_profile/permissions.py' in list format
    for e.g. admin_perms = ['activity_stream.view_useraction',
                            'auth.add_user',
                            'auth.change_user',
                            'auth.delete_user',
                            'auth.view_user',
                            'device.change_device',
                            'device.view_device',
                            'device.view_devicefrequency',
                            'inventory.change_antenna']
    4. Call 'fix_user_permissions()' for assigning permissions to each user corressponding to their group.

    Perms File: /nocout_gis/nocout/user_profile/permissions.py
    """
    args = '<directory ...>'
    help = 'Adds Permissions to each user according to permissions list provided.'

    def handle(self, *args, **options):

        def fix_user_permissions():
            """
            Assign permissions to each user corressponding to their group.
            """
            print "- START -"

            users = User.objects.prefetch_related('groups', 'user_permissions').order_by('username')
            usernames = users.values_list('username', flat=True)
            usergroups = users.values_list('groups__name', flat=True)

            user_mapper = dict()
            for name, group, obj in zip(usernames, usergroups, users):
                user_mapper[name] = {
                    'group': group,
                    'obj': obj
                }

                if group:
                    # Get permissions list which needs to be assigned.
                    perms_list = eval(group.lower() + "_perms")
                    app_labels = list()
                    codenames = list()

                    for data in perms_list:
                        # Seperate 'app_label' and 'codename' from perm string ('data') for e.g. if perm string is
                        # 'device.view_device' then app_label is 'device' and code_name is 'view_device'
                        app_label, codename = data.split('.')
                        app_labels.append(app_label)
                        codenames.append(codename)

                    # Permissions which needs to be assigned.
                    new_perms = reduce(
                        operator.or_,
                        (Q(codename=code, content_type__app_label=app) for code, app in izip(codenames, app_labels))
                    )
                    new_perms = Permission.objects.filter(new_perms)

                    # Assign permissions to current user.
                    obj.user_permissions.add(*new_perms)

                    # Remove old custom permissions.
                    diff_perms = set(obj.user_permissions.all()).difference(set(new_perms))
                    obj.user_permissions.remove(*diff_perms)

            print "- END -"

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

        # Create view permissions for all apps in project.
        create_view_permissions()

        # Assigning default permissions to all users.
        fix_user_permissions()
