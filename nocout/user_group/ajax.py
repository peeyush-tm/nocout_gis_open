import json
from dajaxice.decorators import dajaxice_register
from models import UserGroup
# from user_profile.models import Department
from user_group.models import Organization


# generate content for soft delete popup form
@dajaxice_register
def user_group_soft_delete_form(request, value):
    # user group which needs to be deleted
    user_group = UserGroup.objects.get(id=value)

    # result: data dictionary send in ajax response
    #{
    #  "success": 1,     # 0 - fail, 1 - success, 2 - exception
    #  "message": "Success/Fail message.",
    #  "data": {
    #     "meta": {},
    #     "objects": {
    #          "user_group_name": <name>,
    #          "child_user_groups": [
    #                   {
    #                       "id': <id>,
    #                       "value": <value>,
    #                   },
    #                   {
    #                       "id': <id>,
    #                       "value": <value>,
    #                   }
    #           ]
    #}
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Failed to render form correctly."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['form_type'] = 'user_group'
    result['data']['objects']['form_title'] = 'user group'
    result['data']['objects']['id'] = user_group.id
    result['data']['objects']['name'] = user_group.name

    # child_user_groups: list of user groups which are associated with the
    # user group which we are deleting
    child_user_groups = UserGroup.objects.filter(parent_id=value, is_deleted=0)

    # child_user_group_descendants: set of all child user groups descendants (needs for
    # filtering new parent user groups choice)
    child_user_group_descendants = []
    for child_user_group in child_user_groups:
        user_group_descendant = child_user_group.get_descendants()
        for cug in user_group_descendant:
            child_user_group_descendants.append(cug)

    result['data']['objects']['childs'] = []
    # future user group parent needs to find out only if our user group is
    # associated with any other user group i.e if child_user_groups.count() > 0
    if child_user_groups.count() > 0:
        # eligible: these are the user groups which are not associated with
        # the user group which needs to be deleted in any way, & are eligible to be the
        # parent of user groups in child_user_groups
        remaining_user_groups = UserGroup.objects.exclude(parent_id=value)
        selected_user_groups = set(remaining_user_groups) - set(child_user_group_descendants)
        result['data']['objects']['eligible'] = []
        for e_ug in selected_user_groups:
            e_dict = dict()
            e_dict['key'] = e_ug.id
            e_dict['value'] = e_ug.name
            # for excluding 'user_group' which we are deleting from eligible
            # user group choices
            if e_ug.id == user_group.id: continue
            if e_ug.is_deleted == 1: continue
            result['data']['objects']['eligible'].append(e_dict)
        for c_ug in child_user_groups:
            c_dict = {}
            c_dict['key'] = c_ug.id
            c_dict['value'] = c_ug.name
            result['data']['objects']['childs'].append(c_dict)
    result['success'] = 1
    result['message'] = "Successfully render form."
    return json.dumps({'result': result})


# soft delete user group i.e. not deleting user group from database, it just set
# it's is_deleted field value to 1 & remove it's relationship with any other user
# group & make some other user group parent of associated user groups
@dajaxice_register
def user_group_soft_delete(request, user_group_id, new_parent_id):
    # if new_parent is not available than make it default (id=1)
    if not new_parent_id:
        new_parent_id = 1

    # user_group: user group which needs to be deleted
    user_group = UserGroup.objects.get(id=user_group_id)

    # result: data dictionary send in ajax response
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "No data exists."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['user_group_id'] = user_group_id
    result['data']['objects']['user_group_name'] = user_group.name

    # default user group
    default_user_group = UserGroup.objects.get(id=1)

    # setting new parent user group
    try:
        # new_parent: new parent user group for associated user groups
        new_parent = UserGroup.objects.get(id=new_parent_id)
    except:
        print "No new user group parent exist."

    # fetching all child user groups of user group which needs to be deleted
    try:
        child_user_groups = UserGroup.objects.filter(parent_id=user_group_id)
    except:
        print "No child user group exists."

    # replace user group which we are deleting with default user group in 'department'
    # try:
    #     print "user_group", user_group
    #     department = Department.objects.filter(user_group=user_group)
    #     print "department", department
    #     for dept in department:
    #         dept.user_group = default_user_group
    #         dept.save()
    # except:
    #     print "User group is not present in department."

    # replace user group which we are deleting with default user group in 'organization'
    try:
        organization = Organization.objects.filter(user_group=user_group)
        for org in organization:
            print "organization", organization
            org.user_group = default_user_group
            org.save()
    except:
        print "User group is not present in organization."

    # assign new parent user group to all child groups
    if child_user_groups.count() > 0:
        for ug in child_user_groups:
            ug.parent = new_parent
            ug.save()

    # setting 'is_deleted' bit of user group to 1 which means user group
    # is soft deleted
    if user_group.is_deleted == 0:
        user_group.is_deleted = 1
        user_group.save()
        result['success'] = 1
        result['message'] = "Successfully deleted."
    else:
        result['success'] = 0
        result['message'] = "Already soft deleted."
    return json.dumps({'result': result})
