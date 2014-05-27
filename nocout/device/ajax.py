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
        field_value = ""
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
    # device which needs to be deleted
    device = Device.objects.get(id=value)
    # result: data dictionary send in ajax response
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
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Failed to render form correctly."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['device_id'] = device.id
    result['data']['objects']['device_name'] = device.device_name
    # child_devices: these are the devices which are associated with
    # the device which needs to be deleted in parent-child relationship
    child_devices = Device.objects.filter(parent_id=value, is_deleted=0)
    result['data']['objects']['child_devices'] = []
    # future device parent is needs to find out only if our device is
    # associated with any other device i.e if child_devices.count() > 0
    if child_devices.count() > 0:
        # eligible_devices: these are the devices which are not associated with
        # the device which needs to be deleted in any way, & are eligible to be the
        # parent of devices in child_devices
        selected_devices = Device.objects.exclude(parent_id=value)
        result['data']['objects']['eligible_devices'] = []
        for e_dv in selected_devices:
            e_dict = dict()
            e_dict['key'] = e_dv.id
            e_dict['value'] = e_dv.device_name
            if e_dv.id == device.id: continue
            if e_dv.is_deleted == 1: continue
            if set(e_dv.device_group.all()) != set(device.device_group.all()): continue
            result['data']['objects']['eligible_devices'].append(e_dict)
        for c_dv in child_devices:
            c_dict = {}
            c_dict['key'] = c_dv.id
            c_dict['value'] = c_dv.device_name
            result['data']['objects']['child_devices'].append(c_dict)
    result['success'] = 1
    result['message'] = "Successfully render form."
    return json.dumps({'result': result})


# soft delete device i.e. not deleting device from database, it just set
# it's is_deleted field value to 1 & remove it's relationship with any other device
# & make some other device parent of associated device
@dajaxice_register
def device_soft_delete(request, device_id, new_parent_id=1):
    # device: device which needs to be deleted
    device = Device.objects.get(id=device_id)
    # result: data dictionary send in ajax response
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "No data exists."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['device_id'] = device_id
    result['data']['objects']['device_name'] = device.device_name
    try:
        # new_parent: new parent device for associated devices
        new_parent = Device.objects.get(id=new_parent_id)
    except:
        print "No new device parent exist."
    try:
        child_devices = Device.objects.filter(parent_id=device_id)
    except:
        print "No child device exists."
    if child_devices.count() > 0:
        for dv in child_devices:
            dv.parent = new_parent
            dv.save()
    if device.is_deleted == 0:
        device.is_deleted = 1
        device.save()
        result['success'] = 1
        result['message'] = "Successfully deleted."
    else:
        result['success'] = 0
        result['message'] = "Already soft deleted."
    return json.dumps({'result': result})
