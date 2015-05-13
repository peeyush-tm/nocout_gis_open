"""
==============================================================
Module contains ajax functions specific to 'user_profile' app.
==============================================================

Location:
* /nocout_gis/nocout/user_profile/ajax.py

List of constructs:
=========
Functions
=========
* user_soft_delete_form
* user_soft_delete
* user_add
* user_hard_delete
"""

import json
from dajaxice.decorators import dajaxice_register
from django.db.models import Max
from models import UserProfile
from nocout.settings import ISOLATED_NODE


@dajaxice_register(method='GET')
def user_soft_delete_form(request, value, datatable_headers):
    """
    Generate form on user soft deletion request.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request
        value (int): Selected user ID.
        datatable_headers (unicode): Datatable headers.

    Returns:
        result (str): Result which needs to be returned.
                       for e.g. {
                                    "result": {
                                        "message": "Successfully render form.",
                                        "data": {
                                            "meta": "",
                                            "objects": {
                                                "name": "user11",
                                                "eligible": [],
                                                "datatable_headers": "",
                                                "form_title": "user",
                                                "form_type": "user",
                                                "id": 61
                                            }
                                        },
                                        "success": 1
                                    }
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
    result['data']['objects']['datatable_headers'] = datatable_headers

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

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def user_soft_delete(request, user_id, new_parent_id, datatable_headers, userlistingtable, userarchivelisting):
    """
    Soft delete user i.e. not deleting user from database, it just set
    it's 'is_deleted' bit to 1, remove it's relationship with any other user
    & make some other user parent of associated user's.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request
        user_id (unicode): Selected user ID.
        new_parent_id (unicode): New parent/manager for child user's of user which need to be deleted.
        userlistingtable (int): User's listing datatable url.
        userarchivelisting (unicode): Archived user's listing datatable url.

    Returns:
        result (str): Result which needs to be returned.
                       for e.g. {
                                    "result": {
                                        "message": "Successfully deleted.",
                                        "data": {
                                            "meta": "",
                                            "objects": {
                                                "user_name": "vasu",
                                                "user_id": "11",
                                                "userlistingtable": "/user/userlistingtable/",
                                                "datatable_headers": "",
                                                "userarchivelisting": "/user/userarchivedlistingtable/"
                                            }
                                        },
                                        "success": 1
                                    }
                                }
    """
    user = UserProfile.objects.get(id=user_id)

    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "No data exists."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['user_id'] = user_id
    result['data']['objects']['user_name'] = user.username
    result['data']['objects']['datatable_headers'] = datatable_headers
    result['data']['objects']['userlistingtable'] = userlistingtable
    result['data']['objects']['userarchivelisting'] = userarchivelisting

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

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def user_add(request, user_id):
    """
    Re-add user to user's inventory from archived inventory.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request
        user_id (int): Selected user ID.

    Returns:
        result (str): Result which needs to be returned.
                       for e.g. {
                                    "result": {
                                        "message": "User Successfully Added.",
                                        "data": {
                                            "meta": "",
                                            "objects": {}
                                        },
                                        "success": 1
                                    }
                                }
    """
    UserProfile.objects.filter(id=user_id).update(**{'is_deleted': 0})

    result = dict()
    result['data'] = {}
    result['success'] = 1
    result['message'] = "User successfully re-added."
    result['data']['meta'] = ''
    result['data']['objects'] = {}

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def user_hard_delete(request, user_id):
    """
    Delete user from user inventory. This action permanently delete user from database.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request
        user_id (int): Selected user ID.

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
    UserProfile.objects.filter(id=user_id).delete()

    result = dict()
    result['data'] = {}
    result['success'] = 1
    result['message'] = "User successfully deleted."

    return json.dumps({'result': result})