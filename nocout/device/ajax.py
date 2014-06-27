import ast
import json
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType, \
    DeviceTypeFieldsValue, Country, State, City
import logging
import requests
logger=logging.getLogger(__name__)


# updating vendor corresponding to the selected technology
@dajaxice_register
def update_vendor(request, option):
    dajax = Dajax()
    tech = DeviceTechnology.objects.get(pk=int(option))
    vendors = tech.device_vendors.all()
    out = []
    out.append("<option value='' selected>Select Vendor....</option>")
    for vendor in vendors:
        out.append("<option value='%d'>%s</option>" % (vendor.id, vendor.name))
    dajax.assign('#id_device_vendor', 'innerHTML', ''.join(out))
    print dajax.json()
    return dajax.json()

# updating model corresponding to the selected vendor
@dajaxice_register
def update_model(request, option):
    dajax = Dajax()
    vendor = DeviceVendor.objects.get(pk=int(option))
    models = vendor.device_models.all()
    out = []
    out.append("<option value=''>Select Model....</option>")
    for model in models:
        out.append("<option value='%d'>%s</option>" % (model.id, model.name))

    dajax.assign('#id_device_model', 'innerHTML', ''.join(out))
    print dajax.json()
    return dajax.json()


# updating type corresponding to the selected model
@dajaxice_register
def update_type(request, option):
    dajax = Dajax()
    model = DeviceModel.objects.get(pk=int(option))
    types = model.device_types.all()
    out = []
    out.append("<option value=''>Select Type....</option>")
    for dtype in types:
        out.append("<option value='%d'>%s</option>" % (dtype.id, dtype.name))
    dajax.assign('#id_device_type', 'innerHTML', ''.join(out))
    print dajax.json()
    return dajax.json()

# to get vendor as during device update
@dajaxice_register
def after_update_vendor(request, option, selected=''):
    dajax = Dajax()
    tech = DeviceTechnology.objects.get(pk=int(option))
    vendors = tech.device_vendors.all()
    out = []
    out.append("<option value=''>Select Vendor....</option>")
    for vendor in vendors:
        if vendor.id==int(selected):
            out.append("<option value='%d' selected>%s</option>" % (vendor.id, vendor.name))
        else:
            out.append("<option value='%d'>%s</option>" % (vendor.id, vendor.name))
    dajax.assign('#id_device_vendor', 'innerHTML', ''.join(out))
    print dajax.json()
    return dajax.json()

# updating model corresponding to the selected vendor
@dajaxice_register
def after_update_model(request, option, selected=''):

    dajax = Dajax()
    vendor = DeviceVendor.objects.get(pk=int(option))
    models = vendor.device_models.all()
    out = []
    out.append("<option value=''>Select Model....</option>")
    for model in models:
        if model.id==int(selected):
            out.append("<option value='%d' selected>%s</option>" % (model.id, model.name))
        else:
            out.append("<option value='%d'>%s</option>" % (model.id, model.name))

    dajax.assign('#id_device_model', 'innerHTML', ''.join(out))
    print dajax.json()
    return dajax.json()


# updating type corresponding to the selected model
@dajaxice_register
def after_update_type(request, option, selected=''):
    print 'type', selected
    dajax = Dajax()
    model = DeviceModel.objects.get(pk=int(option))
    types = model.device_types.all()
    out = []
    out.append("<option value=''>Select Type....</option>")
    for dtype in types:
        if dtype.id==int(selected):
            out.append("<option value='%d' selected>%s</option>" % (dtype.id, dtype.name))
        else:
            out.append("<option value='%d'>%s</option>" % (dtype.id, dtype.name))
    dajax.assign('#id_device_type', 'innerHTML', ''.join(out))
    print dajax.json()
    return dajax.json()

# pop up device 'extra fields' corresponding to the selected 'device type'
@dajaxice_register
def device_type_extra_fields(request, option):
    dajax = Dajax()
    device_type = DeviceType.objects.get(pk=int(option))
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
    out = ["<option value=''>Select Parent Device......</option>"]
    for device in Device.objects.all():
        out.append("<option value='%d'>%s - (%s)</option>"
                   % (int(device.id), device.device_alias, device.ip_address))
    dajax.assign("#id_parent", 'innerHTML', ''.join(out))
    return dajax.json()


# update device 'parent field' selection menu as per last selection on invalid form submission
@dajaxice_register
def device_parent_choices_selected(request, option):
    dajax = Dajax()
    out = ["<option value=''>Select Parent Device......</option>"]
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
    result['data']['objects']['form_type'] = 'device'
    result['data']['objects']['form_title'] = 'device'
    result['data']['objects']['id'] = device.id
    result['data']['objects']['name'] = device.device_name

    # child_devices: these are the devices which are associated with
    # the device which needs to be deleted in parent-child relationship
    child_devices = Device.objects.filter(parent_id=value, is_deleted=0)

    # child_device_descendants: set of all child devices descendants (needs for
    # filtering new parent devices choice)
    child_device_descendants = []
    for child_device in child_devices:
        device_descendant = child_device.get_descendants()
        for cd in device_descendant:
            child_device_descendants.append(cd)

    result['data']['objects']['childs'] = []    
    # future device parent is needs to find out only if our device is
    # associated with any other device i.e if child_devices.count() > 0
    if child_devices.count() > 0:
        # eligible_devices: these are the devices which are not associated with
        # the device which needs to be deleted in any way, & are eligible to be the
        # parent of devices in child_devices
        remaining_devices = Device.objects.exclude(parent_id=value)
        selected_devices = set(remaining_devices) - set(child_device_descendants)
        result['data']['objects']['eligible'] = []
        for e_dv in selected_devices:
            e_dict = dict()
            e_dict['key'] = e_dv.id
            e_dict['value'] = e_dv.device_name
            # for excluding 'device' which we are deleting from eligible
            # device choices
            if e_dv.id == device.id: continue
            if e_dv.is_deleted == 1: continue
            # for excluding devices from eligible device choices those are not from
            # same device_group as the device which we are deleting
            if set(e_dv.device_group.all()) != set(device.device_group.all()): continue
            result['data']['objects']['eligible'].append(e_dict)
        for c_dv in child_devices:
            c_dict = {}
            c_dict['key'] = c_dv.id
            c_dict['value'] = c_dv.device_name
            result['data']['objects']['childs'].append(c_dict)
    result['success'] = 1
    result['message'] = "Successfully render form."
    return json.dumps({'result': result})


# soft delete device i.e. not deleting device from database, it just set
# it's is_deleted field value to 1 & remove it's relationship with any other device
# & make some other device parent of associated device
@dajaxice_register
def device_soft_delete(request, device_id, new_parent_id):
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
    # setting new parent device
    try:
        # new_parent: new parent device for associated devices
        new_parent = Device.objects.get(id=new_parent_id)
    except:
        print "No new device parent exist."

    # fetching all child devices of device which needs to be deleted
    try:
        child_devices = Device.objects.filter(parent_id=device_id)
    except:
        print "No child device exists."

    # assign new parent device to all child devices
    if child_devices.count() > 0:
        for dv in child_devices:
            dv.parent = new_parent
            dv.save()

    # setting 'is_deleted' bit of device to 1 which means device is soft deleted
    if device.is_deleted == 0:
        device.is_deleted = 1
        device.save()
        result['success'] = 1
        result['message'] = "Successfully deleted."
    else:
        result['success'] = 0
        result['message'] = "Already soft deleted."
    return json.dumps({'result': result})


# updating states corresponding to the selected country
@dajaxice_register
def update_states(request, option):
    dajax = Dajax()
    country = Country.objects.get(pk=int(option))
    states = country.state_set.all().order_by('state_name')
    out = []
    out = ["<option value=''>Select State....</option>"]
    for state in states:
        out.append("<option value='%d'>%s</option>" % (state.id, state.state_name))
    dajax.assign('#id_state', 'innerHTML', ''.join(out))
    return dajax.json()


# updating cities corresponding to the selected state
@dajaxice_register
def update_cities(request, option):
    dajax = Dajax()
    state = State.objects.get(pk=int(option))
    cities = state.city_set.all().order_by('city_name')
    out = []
    out = ["<option value=''>Select City....</option>"]
    for city in cities:
        out.append("<option value='%d'>%s</option>" % (city.id, city.city_name))
    dajax.assign('#id_city', 'innerHTML', ''.join(out))
    return dajax.json()


# after invalid form submission
# updating states corresponding to the selected country
@dajaxice_register
def update_states_after_invalid_form(request, option, state_id):
    dajax = Dajax()
    country = Country.objects.get(pk=int(option))
    states = country.state_set.all().order_by('state_name')
    out = []
    out = ["<option value=''>Select State....</option>"]
    for state in states:
        if state.id == int(state_id):
            out.append("<option value='%d' selected='selected'>%s</option>" % (state.id, state.state_name))
        else:
            out.append("<option value='%d'>%s</option>" % (state.id, state.state_name))
    dajax.assign('#id_state', 'innerHTML', ''.join(out))
    return dajax.json()


# updating cities corresponding to the selected state
@dajaxice_register
def update_cities_after_invalid_form(request, option, city_id):
    dajax = Dajax()
    state = State.objects.get(pk=int(option))
    cities = state.city_set.all().order_by('city_name')
    out = []
    out = ["<option value=''>Select City....</option>"]
    for city in cities:
        if city.id == int(city_id):
            out.append("<option value='%d' selected='selected'>%s</option>" % (city.id, city.city_name))
        else:
            out.append("<option value='%d'>%s</option>" % (city.id, city.city_name))
    dajax.assign('#id_city', 'innerHTML', ''.join(out))
    return dajax.json()


# add device for monitoring
@dajaxice_register
def add_device_to_nms_core(request, device_id):
    print "device_id", device_id
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Device addition failed."
    result['data']['meta'] = ''
    device = Device.objects.get(pk=device_id)
    device_data = {'device_name': device.device_name,
                   'device_alias': device.device_alias,
                   'ip_address':device.ip_address,
                   'agent_tag': device.agent_tag,
                   'site': device.site_instance.name,
                   'mode' : 'addhost'}
    r = requests.post('http://omdadmin:omd@192.168.0.166/site1/check_mk/nocout.py', data=device_data)
    print "r: ", r.text
    response_dict = ast.literal_eval(r.text)
    if r:
        result['data'] = device_data
        result['success'] = 1
        if response_dict['error_code'] != None:
            result['message'] = response_dict['error_message'].capitalize()
        else:
            result['message'] = "Device added successfully."

    return json.dumps({'result': result})


# sending device  information for it's monitoring
@dajaxice_register
def start_device_monitoring(request):
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Device activation for monitoring failed."
    result['data']['meta'] = ''
    device_data = {'mode' : 'sync'}
    r = requests.post('http://omdadmin:omd@localhost/site1/check_mk/nocout.py', data=device_data)
    response_dict = ast.literal_eval(r.text)
    if r:
        result['data'] = device_data
        result['success'] = 1
        result['message'] = response_dict['error_message'].capitalize()
    return json.dumps({'result': result})