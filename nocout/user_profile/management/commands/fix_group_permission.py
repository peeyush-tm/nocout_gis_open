import os, time

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission

from user_profile.permissions import admin_perms, operator_perms, viewer_perms


class Command(BaseCommand):
    """
    Add permissions to asociated groups.
    """
    args = '<directory ...>'
    help = 'Adds Permissions to each group according to permissions list provided.'

    def handle(self, *args, **options):
    
        def fix_group_permissions(group, perms):
            """
              Add permissions to group from permission list 
                and delete permissions from group which is not in permission list.
            """

            perm_list = []
            for data in perms:
                app_label, codename = data.split('.')
                perm = Permission.objects.get(codename=codename, content_type__app_label=app_label)
                group.permissions.add(perm)
                perm_list.append(perm.id)
            for perm in group.permissions.exclude(id__in=perm_list):
                group.permissions.remove(perm)

        group_admin = Group.objects.get(name='group_admin')
        fix_group_permissions(group_admin, admin_perms)
        
        group_operator = Group.objects.get(name='group_operator')
        fix_group_permissions(group_operator, operator_perms)

        group_viewer = Group.objects.get(name='group_viewer')
        fix_group_permissions(group_viewer, viewer_perms)
