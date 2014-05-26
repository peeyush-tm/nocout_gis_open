import json
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType, \
    DeviceTypeFieldsValue


# updating vendor corresponding to the selected technology
@dajaxice_register
def update_vendor(request, option):
    dajax = Dajax()
    tech = DeviceTechnology.objects.filter(id=option)[0]
    vendors = tech.device_vendors.all()
    out = []
    for vendor in vendors:
        out.append("<option value='%d'>%s - %d</option>"
                   % (int(vendor.id), vendor.name, int(vendor.id)))

    dajax.assign('#id_device_vendor', 'innerHTML', ''.join(out))
    return dajax.json()


# updating model corresponding to the selected vendor
@dajaxice_register
def update_model(request, option):
    dajax = Dajax()
    vendor = DeviceVendor.objects.filter(id=option)[0]
    models = vendor.device_models.all()
    out = []
    for model in models:
        out.append("<option value='%d'>%s - %d</option>"
                   % (int(model.id), model.name, int(model.id)))

    dajax.assign('#id_device_model', 'innerHTML', ''.join(out))
    return dajax.json()


# updating type corresponding to the selected model
@dajaxice_register
def update_type(request, option):
    dajax = Dajax()
    model = DeviceModel.objects.filter(id=option)[0]
    types = model.device_types.all()
    out = []
    for dtype in types:
        out.append("<option value='%d'>%s - %d</option>"
                   % (int(dtype.id), dtype.name, int(dtype.id)))

    dajax.assign('#id_device_type', 'innerHTML', ''.join(out))
    return dajax.json()


# pop up device 'extra fields' corresponding to the selected 'device type'
@dajaxice_register
def device_type_extra_fields(request, option):
    dajax = Dajax()
    device_type = DeviceType.objects.filter(id=option)[0]
    device_extra_fields = device_type.devicetypefields_set.all()
    out = []
    for extra_field in device_extra_fields:
        out.append(
            "<div class='form-group'><label for='%s' class='col-sm-5 control-label'>%s:</label><div class='col-sm-7'><input id='%s' name='%s' type='text' class='form-control' /></div></div>"
            % (extra_field.field_name, extra_field.field_display_name,
               extra_field.field_name, extra_field.field_name))

    dajax.assign('#extra_fields', 'innerHTML', ''.join(out))
    return dajax.json()


# change device 'parent field' selection menu format when page loads first time
@dajaxice_register
def device_parent_choices_initial(request):
    dajax = Dajax()
    out = ["<option value=''>Select......</option>"]
    for device in Device.objects.all():
        out.append("<option value='%d'>%s - (%s)</option>"
                   % (int(device.id), device.device_alias, device.ip_address))
    dajax.assign("#id_parent", 'innerHTML', ''.join(out))
    return dajax.json()


# update device 'parent field' selection menu as per last selection on invalid form submission
@dajaxice_register
def device_parent_choices_selected(request, option):
    dajax = Dajax()
    out = ["<option value=''>Select......</option>"]
    for device in Device.objects.all():
        if device.id == int(option):
            out.append("<option value='%d' selected='selected'>%s - (%s)</option>"
                       % (int(device.id), device.device_alias, device.ip_address))
        else:
            out.append("<option value='%d'>%s - (%s)</option>"
                       % (int(device.id), device.device_alias, device.ip_address))
    dajax.assign("#id_parent", 'innerHTML', ''.join(out))
    return dajax.json()

# generate device extra device fields during device update
@dajaxice_register
def device_extra_fields_update(request, device_type, device_name):
    dajax = Dajax()
    device = Device.objects.get(device_name=device_name)
    device_type = DeviceType.objects.filter(id=device_type)[0]
    device_extra_fields = device_type.devicetypefields_set.all()
    out = []
    for extra_field in device_extra_fields:
        field_value=""
        try:
            dtfv = DeviceTypeFieldsValue.objects.get(device_type_field=extra_field.id, device_id=device.id)
            field_value = dtfv.field_value
        except:
            print "Device type field doesn't exist."
        out.append(
            "<div class='form-group'><label for='%s' class='col-sm-5 control-label'>%s:</label><div class='col-sm-7'><input id='%s' name='%s' type='text' class='form-control' value='%s' /></div></div>"
            % (extra_field.field_name, extra_field.field_display_name,
               extra_field.field_name, extra_field.field_name, field_value))

    dajax.assign('#extra_fields', 'innerHTML', ''.join(out))
    return dajax.json()

# generate content for soft delete popup form
@dajaxice_register
def device_soft_delete_form(request, value):
    data = {}
    # device which needs to be deleted
    device = Device.objects.get(id=value)
    # child_device_groups: these are the device groups which are associated with
    # the device group which needs to be deleted in parent-child relationship
    child_devices = Device.objects.filter(parent_id=value, is_deleted=0)
    # future device parent is needs to find out only if our device is
    # associated with any other device i.e if child_devices.count() > 0
    if child_devices.count() > 0:
        # eligible_devices: these are the devices which are not associated with
        # the device which needs to be deleted in any way, & are eligible to be the
        # parent of devices in child_devices
        #{
        #  "success": 1,     # 0 - fail, 1 - success, 2 - exception
        #  "message": "Success/Fail message.",
        #  "data": {
        #     "meta": {},
        #     "objects": {
        #          "device_name": <name>,
        #          "child_devices": [
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
        selected_devices = Device.objects.exclude(parent_id=value)
        eligible_devices = []
        for dv in selected_devices:
            if dv.device_group.all()[0] != device.device_group.all()[0]: continue
            eligible_devices.append(dv)
        basic_html = "<h5 class='text-warning'>This device ({}) is parent of following devices:</h5>".format(device.device_name)
        data['objects'] = {}
        data['objects']['device_name'] = device.device_name
        data['objects']['child_devices'] = child_devices
        count = 1
        for device in child_devices:
            basic_html += "<span class='text-warning'>{}: {}</span><br />".format(count, device.device_alias)
            count += 1
        basic_html += "<h5 class='text-danger'>Please first choose future parent of these devices from below choices:</h5>"
        basic_html += "<input type='hidden' id='id_device' name='device' value='{}' />".format(value)
        basic_html += "<select class='form-control' id='id_parent' name='parent'>"
        basic_html += "<option value=''>Select Device</option>"
        for device in eligible_devices:
            if device.id==value: continue
            if device.is_deleted==1: continue
            basic_html += "<option value='{}'>{}</option>".format(device.id, device.device_name)
        basic_html += "</select"
    else:
        basic_html = "<h5 class='text-warning'>This device ({}) is not associated with any other device. So click on Yes! if you want to delete it.</h5>".format(device.device_name)
        basic_html += "<input type='hidden' id='id_device' name='device' value='{}' />".format(value)
        basic_html += "<input type='hidden' id='id_parent' name='parent' value='' />"

    return json.dumps({'message':basic_html})


# soft delete device i.e. not deleting device from database, it just set
# it's is_deleted field value to 1 & remove it's relationship with any other device
# & make some other device parent of associated device
@dajaxice_register
def device_soft_delete(request, device_id, new_parent_id=1):
    # device: device which needs to be deleted
    device = Device.objects.get(id=device_id)
    try:
        # new_parent: new parent device for associated devices
        new_parent = Device.objects.get(id=new_parent_id)
    except:
        print "No new device group parent exist."
    try:
        child_devices = Device.objects.filter(parent_id=device_id)
    except:
        print "No child device exists."
    if child_devices.count() > 0:
        for dv in child_devices:
            dv.parent = new_parent
            dv.save()
    device.is_deleted = 1
    device.save()
