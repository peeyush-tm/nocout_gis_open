import json
from dajaxice.decorators import dajaxice_register
from models import DeviceGroup
# from device.models import Inventory
from user_group.models import Organization

@dajaxice_register
def device_group_soft_delete_form(request, value):
    """
    generate content for soft delete popup form
    """
    # result: data dictionary send in ajax response
    #{
    #  "success": 1,     # 0 - fail, 1 - success, 2 - exception
    #  "message": "Success/Fail message.",
    #  "data": {
    #     "meta": {},
    #     "objects": {
    #          "device_group_name": <name>,
    #          "child_device_groups": [
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
    device_group = DeviceGroup.objects.get(id=value)
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Failed to render form correctly."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['form_type'] = 'device_group'
    result['data']['objects']['form_title'] = 'device group'
    result['data']['objects']['id'] = device_group.id
    result['data']['objects']['name'] = device_group.name

    # child_device_groups: list of device groups which are associated with the
    # device group which we are deleting
    child_device_groups = DeviceGroup.objects.filter(parent_id=value, is_deleted=0)
    if child_device_groups.count > 0:
        try:
            # child_device_groups_parent_set: set which contains parents of all
            # child device groups of 'device_group' which we are deleting
            child_device_groups_parent_set = []
            for child_dg in child_device_groups:
                child_device_groups_parent_set.append(child_dg.id)
        except:
            print "Some device group from 'child device groups parent set' had no parent."

    # child_device_group_descendants: set of all child device groups descendants (needs for
    # filtering new parent device groups choice)
    child_device_group_descendants = []
    for child_device_group in child_device_groups:
        device_group_descendant = child_device_group.get_descendants()
        for cdv in device_group_descendant:
            child_device_group_descendants.append(cdv)

    result['data']['objects']['childs'] = []
    # future device group parent needs to find out only if our device group is
    # associated with any other device group i.e if child_device_groups.count() > 0
    if child_device_groups.count() > 0:
        # eligible_device_groups: these are the device groups which are not associated with
        # the device group which needs to be deleted in any way, & are eligible to be the
        # parent of device groups in child_device_groups
        remaining_devices = DeviceGroup.objects.exclude(parent_id=value)
        selected_device_groups = set(remaining_devices) - set(child_device_group_descendants)
        result['data']['objects']['eligible'] = []
        for e_dvg in selected_device_groups:
            e_dict = dict()
            e_dict['key'] = e_dvg.id
            e_dict['value'] = e_dvg.name
            # for excluding 'device_group' which we are deleting from eligible
            # device group choices
            if e_dvg.id == device_group.id: continue
            if e_dvg.is_deleted == 1: continue
            result['data']['objects']['eligible'].append(e_dict)
        for c_dvg in child_device_groups:
            c_dict = {}
            c_dict['key'] = c_dvg.id
            c_dict['value'] = c_dvg.name
            result['data']['objects']['childs'].append(c_dict)
    result['success'] = 1
    result['message'] = "Successfully render form."
    return json.dumps({'result': result})

@dajaxice_register
def device_group_soft_delete(request, device_group_id, new_parent_id):
    """
    soft delete device group i.e. not deleting device group from database, it just set
    it's is_deleted field value to 1 & remove it's relationship with any other device
    group & make some other device group parent of associated device groups
    """
    # if new_parent is not available than make it default (id=1)
    if not new_parent_id:
        new_parent_id = 1

    # device_group: device group which needs to be deleted
    device_group = DeviceGroup.objects.get(id=device_group_id)

    # result: data dictionary send in ajax response
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "No data exists."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['device_group_id'] = device_group_id
    result['data']['objects']['device_group_name'] = device_group.name

    # default device group
    default_device_group = DeviceGroup.objects.get(id=1)

    # setting new parent device group
    try:
        # new_parent: new parent device group for associated device groups
        new_parent = DeviceGroup.objects.get(id=new_parent_id)
    except:
        print "No new device group parent exist."

    # fetching all child device groups of device group which needs to be deleted
    try:
        child_device_groups = DeviceGroup.objects.filter(parent_id=device_group_id)
    except:
        print "No child device group exists."

    # replace device group which we are deleting with default device group in 'inventory'
    # try:
    #     inventory = Inventory.objects.filter(device_group=device_group)
    #     for inv in inventory:
    #         inv.device_group = default_device_group
    #         inv.save()
    # except:
    #     print "Device group is not present in inventory."

    # replace device group which we are deleting with default device group in 'organization'
    try:
        organization = Organization.objects.filter(device_group=device_group)
        for org in organization:
            org.device_group = default_device_group
            org.save()
    except:
        print "Device group is not present in organization."

    # assign new parent device group to all child groups
    if child_device_groups.count() > 0:
        for dg in child_device_groups:
            dg.parent = new_parent
            dg.save()

    # setting 'is_deleted' bit of device group to 1 which means device group
    # is soft deleted
    if device_group.is_deleted == 0:
        device_group.is_deleted = 1
        device_group.save()
        result['success'] = 1
        result['message'] = "Successfully deleted."
    else:
        result['success'] = 0
        result['message'] = "Already soft deleted."
    return json.dumps({'result': result})
