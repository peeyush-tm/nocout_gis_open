import json
from dajaxice.decorators import dajaxice_register
from models import DeviceGroup

# generate content for soft delete popup form
@dajaxice_register
def device_group_soft_delete_form(request, value):
    # child_device_groups: these are the device groups which are associated with
    # the device group which needs to be deleted in parent-child relationship
    child_device_groups = DeviceGroup.objects.filter(parent_id=value, is_deleted=0)

    # future device group parent is needs to find out only if our device group is
    # associated with any other device group i.e if child_device_groups.count() > 0
    if child_device_groups.count() > 0:
        # eligible_device_groups: these are the device groups which are not associated with
        # the device group which needs to be deleted in any way, & are eligible to be the
        # parent of device groups in child_device_groups
        eligible_device_groups = DeviceGroup.objects.exclude(parent_id=value)
        basic_html = "<h5 class='text-warning'>This device group is parent of following device groups:</h5>"
        count = 1
        for dg in child_device_groups:
            basic_html += "<span class='text-warning'>{}: {}</span><br />".format(count, dg.alias)
            count += 1
        basic_html += "<h5 class='text-danger'>Please first choose future parent of these device groups from below choices:</h5>"
        basic_html += "<input type='hidden' id='id_device_group' name='device_group' value='{}' />".format(value)
        basic_html += "<select class='form-control' id='id_parent' name='parent'>"
        basic_html += "<option value=''>Select Device Group</option>"
        for dg in eligible_device_groups:
            if dg.id==value: continue
            if dg.is_deleted==1: continue
            basic_html += "<option value='{}'>{}</option>".format(dg.id, dg.name)
        basic_html += "</select"
    else:
        basic_html = "<h5 class='text-warning'>This device group is not associated with any other device group. So click on Yes! if you want to delete it.</h5>"
        basic_html += "<input type='hidden' id='id_device_group' name='device_group' value='{}' />".format(value)
        basic_html += "<input type='hidden' id='id_parent' name='parent' value='' />"

    return json.dumps({'message':basic_html})


# soft delete device group i.e. not deleting device group from database, it just set
# it's is_deleted field value to 1 & remove it's relationship with any other device
# group & make some other device group parent of associated device groups
@dajaxice_register
def device_group_soft_delete(request, device_group_id, new_parent_id):
    # device_group: device group which needs to be deleted
    device_group = DeviceGroup.objects.get(id=device_group_id)
    try:
        # new_parent: new parent device group for associated device groups
        new_parent = DeviceGroup.objects.get(id=new_parent_id)
    except:
        print "No new device group parent exist."
    try:
        child_device_groups = DeviceGroup.objects.filter(parent_id=device_group_id)
    except:
        print "No child device group exists."
    if child_device_groups.count() > 0:
        for dg in child_device_groups:
            dg.parent = new_parent
            dg.save()
    device_group.is_deleted = 1
    device_group.save()

