import json
from dajaxice.decorators import dajaxice_register
from models import DeviceGroup

@dajaxice_register
def device_group_soft_delete_form(request, value):
    device_group = DeviceGroup.objects.get(id=value)
    child_device_groups = DeviceGroup.objects.filter(parent_id=value)
    eligible_device_groups = DeviceGroup.objects.exclude(parent_id=value)
    basic_html = "<h5 class='text-warning'>This device is parent of following devices:</h5>"
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
        basic_html += "<option value='{}'>{}</option>".format(dg.id, dg.name)
    basic_html += "</select"
    return json.dumps({'message':basic_html})


@dajaxice_register
def device_group_soft_delete(request, device_group_id, new_parent_id):
    device_group = DeviceGroup.objects.get(id=device_group_id)
    new_parent = DeviceGroup.objects.get(id=new_parent_id)
    child_device_groups = DeviceGroup.objects.filter(parent_id=device_group_id)
    for dg in child_device_groups:
        dg.parent = new_parent
        dg.save()
    device_group.is_deleted = 1
    device_group.save()

