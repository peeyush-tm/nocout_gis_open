import json
from dajaxice.decorators import dajaxice_register
from django.db.models import Max
from models import UserProfile
from collections import namedtuple
# generate content for soft delete popup form
from nocout.settings import GISADMIN, ISOLATED_NODE


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

    result['data']['objects']['eligible'] = []
    if user.get_children():
        user_parent=user.parent

        if user_parent:
            user_childrens = user_parent.get_children()
            user_childrens = set(user_childrens) - set([user])

            if len(user_childrens) > 0:

                for e_user in user_childrens:
                    e_dict = dict()
                    e_dict['key'] = e_user.id
                    e_dict['value'] = e_user.username
                    result['data']['objects']['eligible'].append(e_dict)
            else:
                #if user_childrens are empty then the user`s parent will be assigned the user`s children
                result['data']['objects']['eligible'].append({ 'key':user_parent.id , 'value': user_parent.username })

    result['success'] = 1
    result['message'] = "Successfully render form."
    return json.dumps({'result': result })


# soft delete user i.e. not deleting user from database, it just set
# it's is_deleted field value to 1 & remove it's relationship with any other user
# & make some other user parent of associated user
@dajaxice_register
def user_soft_delete(request, user_id, new_parent_id, datatable_headers, userlistingtable, userarchivelisting):

    user = UserProfile.objects.get(id= user_id)

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
        new_parent = UserProfile.objects.get(id= new_parent_id)
        user_childrens= user.get_children()

        for user_children in user_childrens:
            user_children.move_to(new_parent)

    max_tree_id = UserProfile.objects.aggregate(Max('tree_id'))['tree_id__max']
    user.tree_id= max_tree_id+ 1
    user.is_deleted = 1
    user.lft= ISOLATED_NODE.lft
    user.rght= ISOLATED_NODE.rght
    user.level= ISOLATED_NODE.level
    user.parent= None
    user.save()
    UserProfile._default_manager.rebuild()

    result['success'] = 1
    result['message'] = "Successfully deleted."
    return json.dumps({ 'result': result })

@dajaxice_register
def user_add( request, user_id):
    UserProfile.objects.filter(id= user_id).update( **{'is_deleted':0 })
    result = dict()
    result['data'] = {}
    result['success'] = 1
    result['message'] = "User Successfully Added."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    return json.dumps({ 'result': result })


@dajaxice_register
def user_hard_delete(request, user_id):
    UserProfile.objects.filter(id= user_id).delete()
    result = dict()
    result['data'] = {}
    result['success'] = 1
    result['message'] = "User Successfully Deleted."
    return json.dumps({ 'result': result })




