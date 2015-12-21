from itertools import izip
import operator
from django.contrib.auth.models import User, Permission, Group
from nocout.utils import logged_in_user_organizations
from rest_framework.response import Response
from rest_framework.views import APIView
from user_profile.models import UserProfile
from nocout.settings import ISOLATED_NODE
from django.db.models import Max, Q
from user_profile.permissions import admin_perms, operator_perms, viewer_perms
from user_profile.utils.auth import get_child_users, get_user_organizations


class UserSoftDeleteDisplayData(APIView):
    """
    Generate display data for user soft deletion request.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/user_soft_delete_display_data/4/"
    """
    def get(self, request, value):
        """
        Processing API request.

        Args:
            value (int): Selected user ID.

        Returns:
            result (dict): Dictionary containing device information.
                           For e.g.,
                                {
                                    "message": "Successfully render form.",
                                    "data": {
                                        "meta": "",
                                        "objects": {
                                            "form_type": "user",
                                            "eligible": [
                                                {
                                                    "value": "gisoperator",
                                                    "key": 3
                                                },
                                                {
                                                    "value": "gisadmin",
                                                    "key": 10
                                                }
                                            ],
                                            "form_title": "user",
                                            "id": 4,
                                            "name": "gisviewer"
                                        }
                                    },
                                    "success": 1
                                }
        """
        user = UserProfile.objects.get(id=value)

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to render form correctly."
        result['data']['meta'] = ''
        result['data']['objects'] = {}
        result['data']['objects']['form_type'] = 'user'
        result['data']['objects']['form_title'] = 'user'
        result['data']['objects']['id'] = user.id
        result['data']['objects']['name'] = user.username

        # List of eligible parents.
        result['data']['objects']['eligible'] = []

        # Get immediate children of the user.
        user_children = user.get_children()

        if user_children:
            user_parent = user.parent

            if user_parent:
                # Get immediate children of the user's parent.
                user_parent_children = user_parent.get_children()

                # Exclude 'user' from list of eligible parent.
                user_parent_children = set(user_parent_children) - {user}

                if len(user_parent_children) > 0:
                    for e_user in user_parent_children:
                        e_dict = dict()
                        e_dict['key'] = e_user.id
                        e_dict['value'] = e_user.username
                        result['data']['objects']['eligible'].append(e_dict)
                else:
                    # If 'user_parent_children' is empty then the user's parent will
                    # be assigned as a default parent to the user's children.
                    result['data']['objects']['eligible'].append({'key': user_parent.id, 'value': user_parent.username})

        result['success'] = 1
        result['message'] = "Successfully render form."

        return Response(result)


class UserSoftDelete(APIView):
    """
    Soft delete user i.e. not deleting user from database, it just set
    it's 'is_deleted' bit to 1, remove it's relationship with any other user
    & make some other user parent of associated user's.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/user_soft_delete/4/5/"
    """
    def get(self, request, value, new_parent_id):
        """
        Processing API request.

        Args:
            user_id (unicode): Selected user ID.
            new_parent_id (unicode): New parent/manager for child user's of user which need to be deleted.

        Returns:
            result (str): Result which needs to be returned.
                           for e.g.
                                {
                                    "message": "User successfully deleted.",
                                    "data": {
                                        "meta": "",
                                        "objects": {
                                            "name": "vasu",
                                            "id": "11"
                                        }
                                    },
                                    "success": 1
                                }
        """
        user = UserProfile.objects.get(id=value)

        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "No data exists."
        result['data']['meta'] = ''
        result['data']['objects'] = {}
        result['data']['objects']['id'] = value
        result['data']['objects']['name'] = user.username

        try:
            new_parent_id = int(new_parent_id)
        except Exception, e:
            new_parent_id = 0
            pass

        if new_parent_id:
            new_parent = UserProfile.objects.get(id=new_parent_id)

            # Get immediate children of the user.
            user_children = user.get_children()

            for user_child in user_children:
                user_child.move_to(new_parent)

        max_tree_id = UserProfile.objects.aggregate(Max('tree_id'))['tree_id__max']
        user.tree_id = max_tree_id + 1
        user.is_deleted = 1
        user.lft = ISOLATED_NODE.lft
        user.rght = ISOLATED_NODE.rght
        user.level = ISOLATED_NODE.level
        user.parent = None
        user.save()

        # Rebuilds whole tree in database using `parent` link.
        UserProfile._default_manager.rebuild()

        result['success'] = 1
        result['message'] = "User successfully deleted."

        return Response(result)


class RestoreUser(APIView):
    """
    Restore user to user's inventory from archived inventory.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/restore_user/11/"
    """
    def get(self, request, value):
        """
        Processing API request.

        Args:
            value (int): Selected user ID.

        Returns:
            result (str): Result which needs to be returned.
                           for e.g.
                                {
                                    "message": "User successfully restored.",
                                    "data": {
                                        "meta": "",
                                        "objects": {
                                            "id": "12"
                                        }
                                    },
                                    "success": 1
                                }
        """
        UserProfile.objects.filter(id=value).update(**{'is_deleted': 0})

        result = dict()
        result['data'] = {}
        result['success'] = 1
        result['message'] = "User successfully restored."
        result['data']['meta'] = ''
        result['data']['objects'] = {}
        result['data']['objects']['id'] = value

        return Response(result)


class DeleteUser(APIView):
    """
    Delete user from user inventory. This action permanently delete user from database.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/delete_user/11/"
    """
    def get(self, request, value):
        """
        Processing API request.

        Args:
            value (int): Selected user ID.

        Returns:
            result (str): Result which needs to be returned.
                           for e.g. {
                                        "result": {
                                            "message": "User Successfully Deleted.",
                                            "data": {},
                                            "success": 1
                                        }
                                    }
        """
        UserProfile.objects.filter(id=value).delete()

        result = dict()
        result['data'] = {}
        result['success'] = 1
        result['message'] = "User successfully deleted."

        return Response(result)


class ResetUserPermissions(APIView):
    """
    Reset default permissions to each user corressponding to their group.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/reset_user_permissions/4/"
    """
    def get(self, request, value):
        """
        Processing API request.

        Args:
            value (int): Selected user ID.

        Returns:
            result (str): Result which needs to be returned.
                           for e.g. {
                                        "message": "Successfully assigned permissions.",
                                        "data": {
                                            "username": "gisviewer",
                                            "group": "Viewer"
                                        },
                                        "success": 1
                                    }
        """
        # Response data.
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to assign permissions."

        # Get user.
        user = None
        try:
            user = User.objects.get(id=value)
        except Exception as e:
            pass
        
        # Get user group.
        group = None
        try:
            group = user.groups.all()[0].name
        except Exception as e:
            pass

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
            user.user_permissions.add(*new_perms)

            # Remove old custom permissions.
            diff_perms = set(user.user_permissions.all()).difference(set(new_perms))
            user.user_permissions.remove(*diff_perms)

            # Set success bit and message.
            result['data'] = {
                'username': user.username,
                'group': group
            }
            result['success'] = 1
            result['message'] = "Successfully assigned permissions."

        return Response(result)


class PermissonsOnGroupChange(APIView):
    """
    Fetch permissions corresponding to the given group.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/permissions_on_group_change/44/1/"
    """
    def get(self, request, gid):
        """
        Processing API request.

        Args:
            gid (unicode): Selected group ID.
        Returns:
            result (str): Result which needs to be returned.
                           for e.g. [
                                        {
                                            "alias": "auth | user | Can change user",
                                            "id": 8,
                                            "name": "auth | user | Can change user"
                                        },
                                        {
                                            "alias": "auth | user | Can delete user",
                                            "id": 9,
                                            "name": "auth | user | Can delete user"
                                        },
                                        {
                                            "alias": "auth | user | Can view user",
                                            "id": 566,
                                            "name": "auth | user | Can view user"
                                        },
                                        {
                                            "alias": "device | device | Can add device",
                                            "id": 70,
                                            "name": "device | device | Can add device"
                                        }
                                    ]
        """
        # Selected group id.
        gid = int(gid)

        # API Response.
        result = list()

        # Get user object.
        user = None
        try:
            user = request.user.userprofile
        except Exception as e:
            pass

        # Get user group id.
        group_id = None
        try:
            group_id = user.groups.all()[0].id
        except Exception as e:
            pass

        # If group is same as the previous one, then return current users permissions.
        if group_id == gid:
            user_perms = user.user_permissions.all()
            result = [{'id': perm.id,
                       'name': "%s | %s | %s" % (perm.content_type.app_label, perm.content_type, perm.name),
                       'alias': "%s" % (perm.content_type.name.title() + ' - ' + self.format_permission_txt(perm.name))}
                      for perm in user_perms]
        else:
            group_name = Group.objects.get(id=gid).name
            if group_name:
                # Get permissions list which needs to be assigned.
                perms_list = eval(group_name.lower() + "_perms")
                app_labels = list()
                codenames = list()

                for data in perms_list:
                    # Seperate 'app_label' and 'codename' from perm string ('data') for e.g. if perm string is
                    # 'device.view_device' then app_label is 'device' and code_name is 'view_device'
                    app_label, codename = data.split('.')
                    app_labels.append(app_label)
                    codenames.append(codename)

                # Permissions which needs to be assigned.
                user_perms = reduce(
                    operator.or_,
                    (Q(codename=code, content_type__app_label=app) for code, app in izip(codenames, app_labels))
                )
                user_perms = Permission.objects.filter(user_perms)
                result = [{'id': perm.id,
                           'name': "%s | %s | %s" % (perm.content_type.app_label, perm.content_type, perm.name),
                           'alias': "%s" % (perm.content_type.name.title() + ' - ' + self.format_permission_txt(perm.name) )}
                          for perm in user_perms]

        return Response(result)

    def format_permission_txt(self, perm_txt):
        """

        """
        formatted_word = perm_txt
        if any(word in perm_txt for word in ['view', 'display']):
            formatted_word = 'View'
        elif any(word in perm_txt for word in ['change', 'update', 'update']):
            formatted_word = 'Edit'
        elif any(word in perm_txt for word in ['delete', 'remove']):
            formatted_word = 'Delete'
        elif any(word in perm_txt for word in ['create', 'add', 'new']):
            formatted_word = 'Add'
        elif any(word in perm_txt for word in ['sync']):
            formatted_word = 'Sync'

        return formatted_word


class ResetAdminUsersPermissions(APIView):
    """
    Reset permissions only for child users.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/reset_admin_users_permissions/"
    """
    def get(self, request):
        """
        Processing API request.

        Returns:
            result (str): Result which needs to be returned.
                          For e.g.  {
                                        "message": "Succesfully assigned permissions to users.",
                                        "data": {
                                            "users": "aavshyika, abhay, abhijeet, abhijit"
                                        },
                                        "success": 1
                                    }
        """
        # Response data.
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to assign permissions."

        # Get user.
        user = request.user

        # Get child users.
        child_users = get_child_users(user)

        users = child_users.prefetch_related('groups', 'user_permissions').order_by('username')
        usernames = users.values_list('username', flat=True)
        usergroups = users.values_list('groups__name', flat=True)
        response_users = list()

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
                response_users.append(name)

            if response_users:
                result['success'] = 1
                result['message'] = "Succesfully assigned permissions to users."
                result['data']['users'] = ", ".join(response_users)

        return Response(result)


class ParentOnOrganizationChange(APIView):
    """
    Get child users corresponding to the selected organization.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/parent_on_organization_change/1/"
    """

    def get(self, request, oid):
        """
        Processing API request.

        Returns:
            result (str): Result which needs to be returned.
                          For e.g. {
                                        "message": "Successfully fetched users.",
                                        "data": {
                                            "users": [
                                                {
                                                    "username": "priyesh",
                                                    "id": 64
                                                },
                                                {
                                                    "username": "test-op1",
                                                    "id": 315
                                                }
                                            ]
                                        },
                                        "success": 1
                                    }
        """
        # Response data.
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to fetch users."
        result['data']['users'] = list()

        # Get user.
        user = request.user
        result['data']['users'].append({'id': user.id, 'username': user.username})

        if user:
            child_users = user.userprofile.get_children()
            if oid:
                # Get child users existing within user's organizations.
                child_users = child_users.filter(organization__id=oid)
            for child_user in child_users:
                result['data']['users'].append({'id': child_user.id, 'username': child_user.username})

        if result['data']['users']:
            result['success'] = 1
            result['message'] = "Successfully fetched users."

        return Response(result)


class GetUserOrganizations(APIView):
    """
    Get current user organizations.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_user_organizations/"
    """

    def get(self, request):
        """
        Processing API request.

        Returns:
            result (str): Result which needs to be returned.
                          For e.g.   {
                                        "message": "Successfully fetched organizations.",
                                        "data": {
                                            "organizations": [
                                                {
                                                    "id": 1,
                                                    "name": "TCL"
                                                },
                                                {
                                                    "id": 2,
                                                    "name": "Teramatrix"
                                                },
                                                {
                                                    "id": 3,
                                                    "name": "Code Cope"
                                                },
                                                {
                                                    "id": 4,
                                                    "name": "Rajasthan"
                                                },
                                                {
                                                    "id": 6,
                                                    "name": "madras"
                                                },
                                                {
                                                    "id": 5,
                                                    "name": "TCL-Mumbai"
                                                }
                                            ]
                                        },
                                        "success": 1
                                    }
        """
        # Response data.
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = "Failed to fetch organizations."
        result['data']['organizations'] = list()

        # Get user.
        user = request.user.userprofile

        # Get user organizations.
        organizations = get_user_organizations(user)

        for org in organizations:
            result['data']['organizations'].append({
                'id': org.id,
                'name': org.name
            })

        if result['data']['organizations']:
            result['success'] = 1
            result['message'] = "Successfully fetched organizations."

        return Response(result)