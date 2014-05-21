import json
from dajaxice.decorators import dajaxice_register
from models import DeviceGroup

@dajaxice_register
def device_group_soft_delete_form(request, value):
    device_group = DeviceGroup.objects.get(id=value)
    child_device_groups = DeviceGroup.objects.filter(parent_id=value, is_deleted=0)
    if child_device_groups.count() > 0:
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
        basic_html = "<h5 class='text-warning'>This device is not associated with any other device group. So click on Yes! if you want to delete it.</h5>"
        basic_html += "<input type='hidden' id='id_device_group' name='device_group' value='{}' />".format(value)
        basic_html += "<input type='hidden' id='id_parent' name='parent' value='' />"
    return json.dumps({'message':basic_html})


@dajaxice_register
def device_group_soft_delete(request, device_group_id, new_parent_id):
    device_group = DeviceGroup.objects.get(id=device_group_id)
    try:
        new_parent = DeviceGroup.objects.get(id=new_parent_id)
    except:
        print "No new device group parent exist."
    try:
        child_device_groups = DeviceGroup.objects.filter(parent_id=device_group_id)
    except:
        print "No child device group exists."
    if child_device_groups.count() > 0:
        for dg in child_device_groups:
            print dg
            dg.parent = new_parent
            dg.save()
    device_group.is_deleted = 1
    device_group.save()

