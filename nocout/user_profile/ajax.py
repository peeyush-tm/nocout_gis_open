import json
from dajaxice.decorators import dajaxice_register
from models import UserProfile

# generate content for soft delete popup form
@dajaxice_register
def user_soft_delete_form(request, value, datatable_headers):
    # user which needs to be deleted
    user = UserProfile.objects.get(id=value)
    # result: data dictionary send in ajax response
    #{
    #  "success": 1,     # 0 - fail, 1 - success, 2 - exception
    #  "message": "Success/Fail message.",
    #  "data": {
    #     "meta": {},
    #     "objects": {
    #          "user_name": <name>,
    #          "child_users": [
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
    result['data']['objects']['form_type'] = 'user'
    result['data']['objects']['form_title'] = 'user'
    result['data']['objects']['id'] = user.id
    result['data']['objects']['name'] = user.username
    result['data']['objects']['datatable_headers'] = datatable_headers

    # child_users: these are the users which are associated with
    # the user which needs to be deleted in parent-child relationship
    child_users = UserProfile.objects.filter(parent_id=value, is_deleted=0)

    # child_user_descendants: set of all child users descendants (needs for
    # filtering new parent users choice)
    child_user_descendants = []
    for child_user in child_users:
        user_descendant = child_user.get_descendants()
        for cu in user_descendant:
            child_user_descendants.append(cu)

    result['data']['objects']['childs'] = []

    # future users parent is needs to find out only if our user is
    # associated with any other user i.e if child_users.count() > 0
    if child_users.count() > 0:
        # eligible_users: these are the users which are not associated with
        # the user which needs to be deleted in any way, & are eligible to be the
        # parent of users in child_users
        remaining_users = UserProfile.objects.exclude(parent_id=value)
        selected_users = set(remaining_users) - set(child_user_descendants)
        result['data']['objects']['eligible'] = []
        for e_user in selected_users:
            e_dict = dict()
            e_dict['key'] = e_user.id
            e_dict['value'] = e_user.username
            # for excluding 'user' which we are deleting from eligible
            # user choices
            if e_user.id == user.id: continue
            if e_user.is_deleted == 1: continue
            # for excluding users from eligible user choices those are not from
            # same user_group as the user which we are deleting
            # if set(e_user.user_group.all()) != set(user.user_group.all()): continue
            result['data']['objects']['eligible'].append(e_dict)
        for c_user in child_users:
            c_dict = {}
            c_dict['key'] = c_user.id
            c_dict['value'] = c_user.username
            result['data']['objects']['childs'].append(c_dict)
    result['success'] = 1
    result['message'] = "Successfully render form."
    return json.dumps({'result': result})


# soft delete user i.e. not deleting user from database, it just set
# it's is_deleted field value to 1 & remove it's relationship with any other user
# & make some other user parent of associated user
@dajaxice_register
def user_soft_delete(request, user_id, new_parent_id, datatable_headers, userlistingtable, userarchivelisting):
    # if new_parent is not available than make it default (id=2)
    if not new_parent_id:
        new_parent_id = 2
    # user: user which needs to be deleted
    user = UserProfile.objects.get(id=user_id)
    # result: data dictionary send in ajax response
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


    # setting new parent user
    try:
        # new_parent: new parent user for associated users
        new_parent = UserProfile.objects.get(id=new_parent_id)
    except:
        print "No new user parent exist."

    # fetching all child users of user which needs to be deleted
    try:
        child_users = UserProfile.objects.filter(parent_id=user_id)
    except:
        print "No child user exists."

    # assign new parent user to all child users
    if child_users.count() > 0:
        for c_user in child_users:
            c_user.parent = new_parent
            c_user.save()

    # setting 'is_deleted' bit of user to 1 which means user is soft deleted
    if user.is_deleted == 0:
        user.is_deleted = 1
        user.save()
        result['success'] = 1
        result['message'] = "Successfully deleted."
    else:
        result['success'] = 0
        result['message'] = "Already soft deleted."
    return json.dumps({'result': result})