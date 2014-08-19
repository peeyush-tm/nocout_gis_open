""" This file contains AJAX functions applied in 'device' app. """

import ast
import json
import requests
import logging
import urllib
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType, \
    DeviceTypeFieldsValue, Country, State
from service.models import Service, ServiceParameters, DeviceServiceConfiguration
from site_instance.models import SiteInstance

logger = logging.getLogger(__name__)


@dajaxice_register
def update_vendor(request, option):
    """Updating vendors corresponding to selected technology

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # selected technology
    tech = DeviceTechnology.objects.get(pk=int(option))
    # vendors associated to the selected technology
    vendors = tech.device_vendors.all()
    out = list()
    out.append("<option value='' selected>Select</option>")
    for vendor in vendors:
        out.append("<option value='%d'>%s</option>" % (vendor.id, vendor.name))
    dajax.assign('#id_device_vendor', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_model(request, option):
    """Updating models corresponding to the selected vendor

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # selected vendor
    vendor = DeviceVendor.objects.get(pk=int(option))
    # models associated to the selected vendor
    models = vendor.device_models.all()
    out = list()
    out.append("<option value=''>Select</option>")
    for model in models:
        out.append("<option value='%d'>%s</option>" % (model.id, model.name))
    dajax.assign('#id_device_model', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_type(request, option):
    """Updating types corresponding to the selected model

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()

    # selected model
    model = DeviceModel.objects.get(pk=int(option))
    # types associated to the selected model
    types = model.device_types.all()
    out = list()
    out.append("<option value=''>Select</option>")
    for dtype in types:
        out.append("<option value='%d'>%s</option>" % (dtype.id, dtype.name))
    dajax.assign('#id_device_type', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_ports(request, option):
    """Updating ports corresponding to the selected type

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()

    # selected type
    device_type = DeviceType.objects.get(pk=int(option))
    # ports associated to the selected type
    ports = device_type.device_port.all()
    out = list()
    out.append("<option value=''>Select</option>")
    for port in ports:
        out.append("<option value='%d'>%s - (%d)</option>" % (port.id, port.alias, port.value))
    dajax.assign('#id_ports', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def after_update_vendor(request, option, selected=''):
    """Get vendor selection menu with last time selected vendor as selected option after unsuccessful form submission

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Kwargs:
        selected (unicode): option value selected before unsuccessful form submission

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # selected technology
    tech = DeviceTechnology.objects.get(pk=int(option))
    # vendors associated to selected technology
    vendors = tech.device_vendors.all()
    out = list()
    out.append("<option value=''>Select</option>")
    for vendor in vendors:
        if vendor.id == int(selected):
            out.append("<option value='%d' selected>%s</option>" % (vendor.id, vendor.name))
        else:
            out.append("<option value='%d'>%s</option>" % (vendor.id, vendor.name))
    dajax.assign('#id_device_vendor', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def after_update_model(request, option, selected=''):
    """Get model selection menu with last time selected model as selected option after unsuccessful form submission

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Kwargs:
        selected (unicode): option value selected before unsuccessful form submission

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # selected vendor
    vendor = DeviceVendor.objects.get(pk=int(option))
    # models associated to selected vendor
    models = vendor.device_models.all()
    out = list()
    out.append("<option value=''>Select</option>")
    for model in models:
        if model.id == int(selected):
            out.append("<option value='%d' selected>%s</option>" % (model.id, model.name))
        else:
            out.append("<option value='%d'>%s</option>" % (model.id, model.name))
    dajax.assign('#id_device_model', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def after_update_type(request, option, selected=''):
    """Get type selection menu with last time selected type as selected option after unsuccessful form submission

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Kwargs:
        selected (unicode): option value selected before unsuccessful form submission

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # selected model
    model = DeviceModel.objects.get(pk=int(option))
    # types associated to selected model
    types = model.device_types.all()
    out = list()
    out.append("<option value=''>Select</option>")
    for dtype in types:
        if dtype.id == int(selected):
            out.append("<option value='%d' selected>%s</option>" % (dtype.id, dtype.name))
        else:
            out.append("<option value='%d'>%s</option>" % (dtype.id, dtype.name))
    dajax.assign('#id_device_type', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def after_update_ports(request, option, selected=[]):
    """Get ports selection menu with last time selected port as selected option after unsuccessful form submission

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Kwargs:
        selected (unicode): option value selected before unsuccessful form submission

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    
    # selected type
    device_type = DeviceType.objects.get(pk=int(option))

    # ports associated to selected type
    ports = device_type.device_port.all()
    out = list()
    out.append("<option value=''>Select</option>")
    for port in ports:
        if selected:
            if port.id in [int(x) for x in selected]:
                out.append("<option value='%d' selected>%s - (%d)</option>" % (port.id, port.alias, port.value))
            else:
                out.append("<option value='%d'>%s - (%d)</option>" % (port.id, port.alias, port.value))
        else:
            out.append("<option value='%d'>%s - (%d)</option>" % (port.id, port.alias, port.value))
    dajax.assign('#id_ports', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def device_type_extra_fields(request, option):
    """Show extra fields associated with device type on selecting device type

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # selected device type
    device_type = DeviceType.objects.get(pk=int(option))
    # selected device extra
    device_extra_fields = device_type.devicetypefields_set.all()
    out = []
    for extra_field in device_extra_fields:
        out.append("<div class='form-group'><label for='%s' class='col-sm-5 control-label'>\
                    %s:</label><div class='col-sm-7'><input id='%s' name='%s' type='text' class='form-control' />\
                    </div></div>"
                   % (extra_field.field_name, extra_field.field_display_name,
                      extra_field.field_name, extra_field.field_name))
    dajax.assign('#extra_fields', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def device_parent_choices_initial(request):
    """Get parent selection menu having option titles including ip address

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    out = ["<option value=''>Select</option>"]
    for device in Device.objects.all():
        out.append("<option value='%d'>%s - (%s)</option>"
                   % (int(device.id), device.device_alias, device.ip_address))
    dajax.assign("#id_parent", 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def device_parent_choices_selected(request, option):
    """Get parent selection menu having option titles including ip address after unsuccessful form submission

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """

    dajax = Dajax()
    out = ["<option value=''>Select</option>"]
    for device in Device.objects.all():
        if device.id == int(option):
            out.append("<option value='%d' selected='selected'>%s - (%s)</option>"
                       % (int(device.id), device.device_alias, device.ip_address))
        else:
            out.append("<option value='%d'>%s - (%s)</option>"
                       % (int(device.id), device.device_alias, device.ip_address))
    dajax.assign("#id_parent", 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def device_extra_fields_update(request, device_type, device_name):
    """Show device extra fields in device update form

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        device_type (unicode): device type value
        device_name (unicode): device name

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # current device
    device = Device.objects.get(device_name=device_name)
    # device type of current device
    device_type = DeviceType.objects.filter(id=device_type)[0]
    # extra fields associated with current device
    device_extra_fields = device_type.devicetypefields_set.all()
    out = list()
    for extra_field in device_extra_fields:
        field_value = ""
        try:
            dtfv = DeviceTypeFieldsValue.objects.get(device_type_field=extra_field.id, device_id=device.id)
            field_value = dtfv.field_value
        except:
            logger.info("Device type field doesn't exist.")
        out.append(
            "<div class='form-group'><label for='%s' class='col-sm-5 control-label'>\
            %s:</label><div class='col-sm-7'><input id='%s' name='%s' type='text' class='form-control' value='%s' />\
            </div></div>"
            % (extra_field.field_name, extra_field.field_display_name,
               extra_field.field_name, extra_field.field_name, field_value))

    dajax.assign('#extra_fields', 'innerHTML', ''.join(out))
    return dajax.json()


# generate content for soft delete popup form
@dajaxice_register
def device_soft_delete_form(request, value):
    """Get data to show on device soft delete form

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        value (int): device id

    Returns:
        result (dictionary): dictionary contains device and it's children's values
                            i.e. {
                                    "success": 1,
                                    "message": "Success/Fail message.",       # 0 - fail, 1 - success, 2 - exception
                                    "data": {
                                        "meta": {},
                                        "objects": {
                                            "form_type": <name>,
                                            "form_title": <name>,
                                            "device_name": <name>,
                                            "child_devices": [
                                                {
                                                    "id": <id>,
                                                    "value": <value>
                                                },
                                                {
                                                    "id": <id>,
                                                    "value": <value>
                                                }
                                            ]
                                        }
                                    }
                                }

    """
    # device which needs to be deleted
    device = Device.objects.get(id=value)

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
            if e_dv.id == device.id:
                continue
            if e_dv.is_deleted == 1:
                continue
            # for excluding devices from eligible device choices those are not from
            # same device_group as the device which we are deleting
            # if set(e_dv.device_group.all()) != set(device.device_group.all()): continue
            result['data']['objects']['eligible'].append(e_dict)
        for c_dv in child_devices:
            c_dict = dict()
            c_dict['key'] = c_dv.id
            c_dict['value'] = c_dv.device_name
            result['data']['objects']['childs'].append(c_dict)
    result['success'] = 1
    result['message'] = "Successfully render form."
    return json.dumps({'result': result})


@dajaxice_register
def device_soft_delete(request, device_id, new_parent_id):
    """ Soft delete device i.e. not deleting device from database, it just set
        it's is_deleted field value to 1 & remove it's relationship with any other device
        & make some other device parent of associated device

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        value (int): device id

    Returns:
        result (dictionary): dictionary contains device and it's children's values
                            i.e. {
                                    "success": 1,
                                    "message": "Success/Fail message.",       # 0 - fail, 1 - success, 2 - exception
                                    "data": {
                                        "meta": {},
                                        "objects": {
                                            "form_type": <name>,
                                            "form_title": <name>,
                                            "device_name": <name>,
                                            "child_devices": [
                                                {
                                                    "id": <id>,
                                                    "value": <value>
                                                },
                                                {
                                                    "id": <id>,
                                                    "value": <value>
                                                }
                                            ]
                                        }
                                    }
                                }

    """
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
    new_parent = ""
    try:
        # new_parent: new parent device for associated devices
        new_parent = Device.objects.get(id=new_parent_id)
    except:
        logger.info("No new device parent exist.")

    # fetching all child devices of device which needs to be deleted
    child_devices = ""
    try:
        child_devices = Device.objects.filter(parent_id=device_id)
    except:
        logger.info("No child device exists.")

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


@dajaxice_register
def update_states(request, option):
    """Updating states corresponding to the selected country

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # selected country
    country = Country.objects.get(pk=int(option))
    # states associated with selected country
    states = country.state_set.all().order_by('state_name')
    out = ["<option value=''>Select State....</option>"]
    for state in states:
        out.append("<option value='%d'>%s</option>" % (state.id, state.state_name))
    dajax.assign('#id_state', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_cities(request, option):
    """Updating cities corresponding to the selected state

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # selected state
    state = State.objects.get(pk=int(option))
    # cities associated to selected state
    cities = state.city_set.all().order_by('city_name')
    out = ["<option value=''>Select City....</option>"]
    for city in cities:
        out.append("<option value='%d'>%s</option>" % (city.id, city.city_name))
    dajax.assign('#id_city', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_states_after_invalid_form(request, option, state_id):
    """Updating states corresponding to the selected country after invalid form submission

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value
        state_id (int): state id

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # selected country
    country = Country.objects.get(pk=int(option))
    # states associated to selected country
    states = country.state_set.all().order_by('state_name')
    out = ["<option value=''>Select State....</option>"]
    for state in states:
        if state.id == int(state_id):
            out.append("<option value='%d' selected='selected'>%s</option>" % (state.id, state.state_name))
        else:
            out.append("<option value='%d'>%s</option>" % (state.id, state.state_name))
    dajax.assign('#id_state', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_cities_after_invalid_form(request, option, city_id):
    """Updating cities corresponding to the selected state after invalid form submission

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (unicode): selected option value

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    # selected state
    state = State.objects.get(pk=int(option))
    # cities associated to the selected state
    cities = state.city_set.all().order_by('city_name')
    out = ["<option value=''>Select City....</option>"]
    for city in cities:
        if city.id == int(city_id):
            out.append("<option value='%d' selected='selected'>%s</option>" % (city.id, city.city_name))
        else:
            out.append("<option value='%d'>%s</option>" % (city.id, city.city_name))
    dajax.assign('#id_city', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def add_device_to_nms_core(request, device_id):
    """Adding device to nms core

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        device_id (int): device id

    Returns:
        result (dict): dict of device info
                    i.e. {
                              'message': 'Deviceaddedsuccessfully.',
                              'data': {
                                  'site': u'nocout_gis_slave',
                                  'agent_tag': u'snmp',
                                  'mode': 'addhost',
                                  'device_name': u'device_116',
                                  'device_alias': u'Device116',
                                  'ip_address': u'115.111.183.116'
                              },
                              'success': 1
                          }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "<i class=\"fa fa-times red-dot\"></i>Device addition failed."
    result['data']['meta'] = ''
    device = Device.objects.get(pk=device_id)
    if device.host_state != "Disable":
        # get 'agent_tag' from DeviceType model
        agent_tag = ""
        try:
            agent_tag = DeviceType.objects.get(id=device.device_type).agent_tag
        except Exception as e:
            logger.info(e.message)

        device_data = {'device_name': device.device_name,
                       'device_alias': device.device_alias,
                       'ip_address': device.ip_address,
                       'agent_tag': agent_tag,
                       'site': device.site_instance.name,
                       'mode': 'addhost'}

        print "Device data -------------------------------", device_data

        # site to which configuration needs to be pushed
        master_site = SiteInstance.objects.get(name='master_UA')
        # url for nocout.py
        # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
        # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
        url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                master_site.password,
                                                                master_site.machine.machine_ip,
                                                                master_site.web_service_port,
                                                                master_site.name)
        # sending post request to device app for adding device to nms core
        r = requests.post(url, data=device_data)
        # converting string in 'r' to dictionary
        response_dict = ast.literal_eval(r.text)
        if r:
            result['data'] = device_data
            result['success'] = 1
            if response_dict['error_code'] is not None:
                result['message'] = response_dict['error_message'].capitalize()
            else:
                result['message'] = "<i class=\"fa fa-check green-dot\"></i>Device added successfully."
                # set 'is_added_to_nms' to 1 after device successfully added to nocout nms core
                device.is_added_to_nms = 1
                device.save()
    else:
        result['message'] = "Device state is disabled. First enable it than add it to nms core."
    return json.dumps({'result': result})


@dajaxice_register
def edit_device_in_nms_core(request, device_id):
    """Editing device in nms core

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        device_id (int): device id

    Returns:
        result (dict): dict of device info
                    i.e. {
                              'message': 'Deviceeditedsuccessfully.',
                              'data': {
                                  'site': u'nocout_gis_slave',
                                  'agent_tag': u'snmp',
                                  'mode': 'edithost',
                                  'device_name': u'device_116',
                                  'device_alias': u'Device116',
                                  'ip_address': u'115.111.183.116'
                              },
                              'success': 1
                          }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Device edit failed."
    result['data']['meta'] = ''
    device = Device.objects.get(pk=device_id)
    if device.host_state != "Disable":

        # get 'agent_tag' from DeviceType model
        agent_tag = ""
        try:
            agent_tag = DeviceType.objects.get(id=device.device_type).agent_tag
        except Exception as e:
            logger.info(e.message)

        device_data = {'device_name': device.device_name,
                       'device_alias': device.device_alias,
                       'ip_address': device.ip_address,
                       'agent_tag': agent_tag,
                       'site': device.site_instance.name,
                       'mode': 'edithost'}

        # site to which configuration needs to be pushed
        master_site = SiteInstance.objects.get(name='master_UA')

        # url for nocout.py
        # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
        # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
        url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                master_site.password,
                                                                master_site.machine.machine_ip,
                                                                master_site.web_service_port,
                                                                master_site.name)

        # sending post request to device app for adding device to nms core
        r = requests.post(url, data=device_data)

        # converting string in 'r' to dictionary
        response_dict = ast.literal_eval(r.text)
        if r:
            result['data'] = device_data
            result['success'] = 1
            if response_dict['error_code'] is not None:
                result['message'] = response_dict['error_message'].capitalize()
            else:
                result['message'] = "<i class=\"fa fa-check green-dot\"></i>Device edited successfully."
                # set 'is_added_to_nms' to 1 after device successfully edited in nocout nms core
                device.is_added_to_nms = 1
                device.save()
    else:
        result['message'] = "<i class=\"fa fa-info text-info\"></i>Device state is disabled. First enable it than add it to nms core."
    return json.dumps({'result': result})


@dajaxice_register
def delete_device_from_nms_core(request, device_id):
    """Delete device from nms core

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        device_id (int): device id

    Returns:
        result (dict): dict of device info
                    i.e. {
                             'message': 'Devicedeletedsuccessfully',
                             'data': {
                                 'mode': 'deletehost',
                                 'device_name': u'device_116'
                             },
                             'success': 1
                         }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Device deletion failed."
    result['data']['meta'] = ''
    device = Device.objects.get(pk=device_id)
    if device.host_state != "Disable":
        # get 'agent_tag' from DeviceType model
        agent_tag = ""
        try:
            agent_tag = DeviceType.objects.get(id=device.device_type).agent_tag
        except:
            logger.info("Device has no device type.")
        device_data = {'mode': 'deletehost', 'device_name': device.device_name,}
        # site to which configuration needs to be pushed
        master_site = SiteInstance.objects.get(name='master_UA')
        # url for nocout.py
        # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
        # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
        url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                master_site.password,
                                                                master_site.machine.machine_ip,
                                                                master_site.web_service_port,
                                                                master_site.name)
        # sending post request to device app for deleting device to nms core
        r = requests.post(url, data=device_data)
        # converting string in 'r' to dictionary
        response_dict = ast.literal_eval(r.text)
        if r:
            result['data'] = device_data
            result['success'] = 1
            if response_dict['error_code'] is not None:
                result['message'] = response_dict['error_message'].capitalize()
            else:
                result['message'] = response_dict['message'].capitalize()
                # set 'is_added_to_nms' to 1 after device successfully added to nocout nms core
                device.is_added_to_nms = 0
                # set 'is_monitored_on_nms' to 1 if service is added successfully
                device.is_monitored_on_nms = 0
                device.save()
                # remove device services from 'service_deviceserviceconfiguration' table
                DeviceServiceConfiguration.objects.filter(device_name=device.device_name).delete()
    else:
        result['message'] = "Device state is disabled. First enable it than add it to nms core."
    return json.dumps({'result': result})


@dajaxice_register
def sync_device_with_nms_core(request, device_id):
    """Sync devices configuration to nms core

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        device_id (int): device id

    Returns:
        result (dict): dict of device info
                    i.e. {
                            'message': 'Configpushedtomysite,nocout_gis_slave',
                            'data': {
                                'mode': 'sync'
                            },
                            'success': 1
                         }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Device activation for monitoring failed."
    result['data']['meta'] = ''
    device_data = {'mode': 'sync'}
    # get device
    device = Device.objects.get(pk=device_id)
    # site to which configuration needs to be pushed
    master_site = SiteInstance.objects.get(name='master_UA')
    # url for nocout.py
    # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
    # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
    url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                            master_site.password,
                                                            master_site.machine.machine_ip,
                                                            master_site.web_service_port,
                                                            master_site.name)
    # sending post request to device app for syncing configuration to associated sites
    r = requests.post(url, data=device_data)
    try:
        # converting string in 'r' to dictionary
        response_dict = ast.literal_eval(r.text)
        if r:
            result['data'] = device_data
            result['success'] = 1
            result['message'] = response_dict['message'].capitalize()
    except:
        result['message'] = "Failed to sync device and services."
        logger.info(r.text)
    return json.dumps({'result': result})


@dajaxice_register
def edit_single_service_form(request, dsc_id):
    """Edit single service for a device from nms core

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        dsc_id (int): device service configuration id

    Returns:
        result (dict): dict of device service info
                    i.e. {
                            'message': '',
                            'data': {
                                'meta': {

                                },
                                'objects': {
                                    'current_template': u'radwin_snmp_v1_222',
                                    'templates': [
                                        {
                                            'value': u'radwin_snmp_v1_224',
                                            'key': 1L
                                        },
                                        {
                                            'value': u'radwin_snmp_v1_223',
                                            'key': 2L
                                        }
                                    ],
                                    'data_source': u'rssi',
                                    'agent_tag': u'snmp',
                                    'version': u'v1',
                                    'read_community': u'public',
                                    'service_name': u'radwin_rssi',
                                    'device_alias': u'Device116',
                                    'dsc_id': 68,
                                    'warning': u'-50',
                                    'critical': u'-85',
                                    'retry_check_interval': 1L,
                                    'normal_check_interval': 6L,
                                    'max_check_attempts': 6L,
                                    'device_name': u'device_116',
                                    'port': 163L
                                }
                            },
                            'success': 0
                        }

    """
    # device service configuration object
    dsc = DeviceServiceConfiguration.objects.get(id=dsc_id)
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = ""
    result['data']['meta'] = {}
    result['data']['objects'] = {}
    try:
        device = Device.objects.get(device_name=dsc.device_name)
        service_data = result['data']['objects']
        service_data['dsc_id'] = dsc_id
        service_data['device_name'] = dsc.device_name
        service_data['device_alias'] = device.device_alias
        service_data['service_name'] = dsc.service_name
        service_data['current_template'] = dsc.svc_template
        service_data['normal_check_interval'] = dsc.normal_check_interval
        service_data['retry_check_interval'] = dsc.retry_check_interval
        service_data['max_check_attempts'] = dsc.max_check_attempts
        service_data['data_source'] = dsc.data_source
        service_data['warning'] = dsc.warning
        service_data['critical'] = dsc.critical
        service_data['agent_tag'] = dsc.agent_tag
        service_data['version'] = dsc.version
        service_data['read_community'] = dsc.read_community
        service_data['port'] = dsc.port
        service_data['templates'] = []
        service_templates = ServiceParameters.objects.all()
        for svc_template in service_templates:
            temp_dict = dict()
            temp_dict['key'] = svc_template.id
            temp_dict['value'] = svc_template.parameter_description
            service_data['templates'].append(temp_dict)
    except Exception as e:
        logger.info(e)
    return json.dumps({'result': result})


@dajaxice_register
def get_service_para_table(request, device_name, service_name, template_id=""):
    """Get service parameters and data source tables for service edit form

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        device_name (unicode): device name
        service_name (unicode): service name

    Kwargs:
        template_id (unicode): template id

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    params = []
    if template_id and template_id != "":
        svc_template = ServiceParameters.objects.get(id=template_id)
        params.append("<br />")
        params.append("<div class=''><div class='box border red'><div class='box-title'><h4>\
                      <i class='fa fa-table'></i>Modified Service Parameters</h4></div>")
        params.append("<div class='box-body'><table class='table'>")
        params.append("<thead><tr><th>Normal Check Interval</th><th>Retry Check Interval</th>\
                       <th>Max Check Attempts</th></tr></thead>")
        params.append("<tbody><tr><td>%d</td><td>%d</td><td>%d</td></tr>" % (svc_template.normal_check_interval,
                                                                             svc_template.retry_check_interval,
                                                                             svc_template.max_check_attempts))
        params.append("</tbody>")
        params.append("<thead><tr><th>DS Name</th><th>Warning</th><th>Critical</th></tr></thead><tbody>")
        for sds in DeviceServiceConfiguration.objects.filter(device_name=device_name, service_name=service_name):
            params.append("<tr class='data_source_field'><td class='ds_name'>%s</td>\
                          <td contenteditable='true' class='ds_warning'>%d</td>\
                          <td contenteditable='true' class='ds_critical'>%d</td></tr>" % (sds.data_source,
                                                                                          int(sds.warning),
                                                                                          int(sds.critical)))
        params.append("</tbody></table></div></div></div>")
    else:
        params.append("<h5 class='text-danger'>No data to show.</h5> ")
    dajax.assign("#modified_info", 'innerHTML', ''.join(params))
    return dajax.json()


@dajaxice_register
def edit_single_service(request, dsc_id, svc_temp_id, data_sources):
    """Edit single service form nms core

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        dsc_id (unicode): device service configuration id
        svc_temp_id (unicode): service template id
        data_sources (list): list of data sources dictionaries
                          i.e. [
                                    {
                                        'data_source': u'rssi',
                                        'warning': u'-50',
                                        'critical': u'-85'
                                    }
                                ]

    Returns:
        result (dict): dictionary containing service information
                    i.e. {
                            "snmp_community": {
                                "read_community": "public",
                                "version": "v2c"
                            },
                            "agent_tag": "snmp",
                            "service_name": "radwin_rssi",
                            "snmp_port": 161,
                            "serv_params": {
                                "normal_check_interval": 5,
                                "max_check_attempts": 5,
                                "retry_check_interval": 5
                            },
                            "device_name": "radwin",
                            "mode": "editservice",
                            "cmd_params": {
                                "rssi": {
                                    "warning": "-50",
                                    "critical": "-80"
                                }
                            }
                        }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = ""
    result['data']['meta'] = {}
    result['data']['objects'] = {}
    dsc = ""
    try:
        # service device service configuration object
        dsc = DeviceServiceConfiguration.objects.get(id=dsc_id)
        try:
            # payload data for post request
            service_data = result['data']['objects']
            service_para = ServiceParameters.objects.get(pk=svc_temp_id)
            # mode
            service_data['mode'] = "editservice"
            # device name
            service_data['device_name'] = str(dsc.device_name)
            # service name
            service_data['service_name'] = str(dsc.service_name)
            # service parameters
            service_data['serv_params'] = {}
            service_data['serv_params']['normal_check_interval'] = int(service_para.normal_check_interval)
            service_data['serv_params']['retry_check_interval'] = int(service_para.retry_check_interval)
            service_data['serv_params']['max_check_attempts'] = int(service_para.max_check_attempts)
            # snmp parameters
            service_data['snmp_community'] = {}
            service_data['snmp_community']['version'] = str(service_para.protocol.version)
            service_data['snmp_community']['read_community'] = str(service_para.protocol.read_community)
            # command parameters
            service_data['cmd_params'] = {}

            # looping through data sources add them to 'cmd_params' dictionary
            for sds in data_sources:
                service_data['cmd_params'][str(sds['data_source'])] = {'warning': str(sds['warning']),
                                                                       'critical': str(sds['critical'])}

            # snmp port
            service_data['snmp_port'] = str(dsc.port)
            # agent tag
            service_data['agent_tag'] = str(dsc.agent_tag)

            # master site on which service needs to be added
            master_site = SiteInstance.objects.get(name='master_UA')
            # url for nocout.py
            # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
            # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
            url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                    master_site.password,
                                                                    master_site.machine.machine_ip,
                                                                    master_site.web_service_port,
                                                                    master_site.name)
            # encoding service_data
            encoded_data = urllib.urlencode(service_data)

            # sending post request to nocout device app to add single service at a time
            r = requests.post(url, data=encoded_data)

            # converting post response data into python dict expression
            response_dict = ast.literal_eval(r.text)

            # if response(r) is given by post request than process it further to get success/failure messages
            if r:
                result['data'] = service_data
                result['success'] = 1

                # if response_dict doesn't have key 'success'
                if not response_dict.get('success'):
                    logger.info(response_dict.get('error_message'))
                    result['message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to updated service '%s'. <br />" % dsc.service_name
                else:
                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>Successfully updated service '%s'. <br />" % dsc.service_name
                    device = Device.objects.get(device_name=dsc.device_name)

                    # save service to 'service_deviceserviceconfiguration' table
                    try:
                        # if service exist in 'service_deviceserviceconfiguration' table than update it
                        for data_source in data_sources:
                            dsc_obj = DeviceServiceConfiguration.objects.get(device_name=dsc.device_name,
                                                                             service_name=dsc.service_name,
                                                                             data_source=data_source['data_source'])
                            dsc_obj.agent_tag = str(dsc.agent_tag)
                            dsc_obj.port = str(service_para.protocol.port)
                            dsc_obj.version = str(service_para.protocol.version)
                            dsc_obj.read_community = str(service_para.protocol.read_community)
                            dsc_obj.svc_template = str(service_para.parameter_description)
                            dsc_obj.normal_check_interval = int(service_para.normal_check_interval)
                            dsc_obj.retry_check_interval = int(service_para.retry_check_interval)
                            dsc_obj.max_check_attempts = int(service_para.max_check_attempts)
                            dsc_obj.warning = data_source['warning']
                            dsc_obj.critical = data_source['critical']
                            dsc_obj.save()
                    except Exception as e:
                        logger.info(e)
        except Exception as e:
            logger.info(e)
            result['message'] = "Failed to updated service '%s'. <br />" % dsc.service_name
    except Exception as e:
        logger.info(e)
        result['message'] = "Failed to updated service '%s'. <br />" % dsc.service_name
    return json.dumps({'result': result})


# delete single service form
@dajaxice_register
def delete_single_service_form(request, dsc_id):
    """Get parameters in the form of JSON object for delete form

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        dsc_id (int): device service configuration object id

    Returns:
        result (dict): dictionary containing service information
                    i.e. {
                            'message': '',
                            'data': {
                                'meta': {

                                },
                                'objects': {
                                    'service_name': u'radwin_rssi',
                                    'data_sources': [
                                        u'rssi'
                                    ],
                                    'device_alias': u'Device116',
                                    'service_alias': u'Receivedsignalstrength',
                                    'device_name': u'device_116'
                                }
                            },
                            'success': 0
                        }

    """
    # device service configuration object
    dsc = DeviceServiceConfiguration.objects.get(id=dsc_id)
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = ""
    result['data']['meta'] = {}
    result['data']['objects'] = {}

    try:
        service_data = result['data']['objects']
        service_data['service_name'] = dsc.service_name
        service_data['service_alias'] = Service.objects.get(name=str(dsc.service_name)).alias
        service_data['device_name'] = dsc.device_name
        service_data['device_alias'] = Device.objects.get(device_name=str(dsc.device_name)).device_alias
        service_data['data_sources'] = []
        try:
            # data sources queryset
            dsc_for_data_sources = DeviceServiceConfiguration.objects.filter(device_name=dsc.device_name,
                                                                             service_name=dsc.service_name)
            for dsc_for_data_source in dsc_for_data_sources:
                service_data['data_sources'].append(dsc_for_data_source.data_source)
        except Exception as e:
            logger.info(e)
    except Exception as e:
        logger.info(e)
    return json.dumps({'result': result})


@dajaxice_register
def delete_single_service(request, device_name, service_name):
    """Delete single service for a device

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        device_name (unicode): device name
        service_name (unicode): service name

    Returns:
        result (dict): dictionary containing service information
                    i.e. {
                            'message': '',
                            'data': {
                                'meta': {

                                },
                                'objects': {
                                    'service_name': u'radwin_rssi',
                                    'data_sources': [
                                        u'rssi'
                                    ],
                                    'device_alias': u'Device116',
                                    'service_alias': u'Receivedsignalstrength',
                                    'device_name': u'device_116'
                                }
                            },
                            'success': 0
                        }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = ""
    result['data']['meta'] = {}
    result['data']['objects'] = {}

    try:
        service_data = {
            'mode': 'deleteservice',
            'device_name': str(device_name),
            'service_name': str(service_name)
        }

        master_site = SiteInstance.objects.get(name='master_UA')
        # url for nocout.py
        # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
        # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
        url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                master_site.password,
                                                                master_site.machine.machine_ip,
                                                                master_site.web_service_port,
                                                                master_site.name)

        # encoding service_data
        encoded_data = urllib.urlencode(service_data)

        # sending post request to nocout device app to add single service at a time
        r = requests.post(url, data=encoded_data)

        # converting post response data into python dict expression
        response_dict = ast.literal_eval(r.text)

        # if response(r) is given by post request than process it further to get success/failure messages
        if r:
            result['data'] = service_data
            result['success'] = 1

            # if response_dict doesn't have key 'success'
            if not response_dict.get('success'):
                logger.info(response_dict.get('error_message'))
                result['message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to delete service '%s'. <br />" % service_name
            else:
                result['message'] += "<i class=\"fa fa-check green-dot\"></i>Successfully updated service '%s'. <br />" % service_name

            # delete service rows form 'service_deviceserviceconfiguration' table
            DeviceServiceConfiguration.objects.filter(device_name=device_name, service_name=service_name).delete()
    except Exception as e:
        result['message'] += e.message
    return json.dumps({'result': result})


@dajaxice_register
def edit_service_form(request, value):
    """Get parameters for service edit form

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        value (int): device id

    Returns:
        result (dict): dictionary containing service information
                    i.e. {
                            'message': 'Successfully render form.',
                            'data': {
                                'meta': '',
                                'objects': {
                                    'master_site': u'master_UA',
                                    'device_alias': u'Device116',
                                    'is_added': 1L,
                                    'services': [
                                        {
                                            'value': u'ODUserialnumber',
                                            'key': 14L
                                        }
                                    ],
                                    'device_name': u'device_116',
                                    'device_id': 545
                                }
                            },
                            'success': 0
                        }

    """
    # device to which services are associated
    device = Device.objects.get(id=value)
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Failed to render form correctly."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['device_id'] = value
    result['data']['objects']['device_name'] = device.device_name
    result['data']['objects']['device_alias'] = device.device_alias
    result['data']['objects']['services'] = []
    result['data']['objects']['master_site'] = ""
    result['data']['objects']['is_added'] = device.is_added_to_nms

    # get services associated with device
    try:
        master_site_name = ""
        try:
            master_site_name = SiteInstance.objects.get(name='master_UA').name
            result['data']['objects']['master_site'] = master_site_name
        except:
            logger.info("Master site doesn't exist.")
        if device.is_added_to_nms == 1:
            if master_site_name == "master_UA":
                # fetching all services from 'service device configuration' table
                dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name)

                # services those are already running for this device
                services = []
                for svc in dsc:
                    services.append(svc.service_name)

                # extracting unique set of services form 'services' list
                monitored_services = set(services)

                result['data']['objects']['services'] = []
                for svc in monitored_services:
                    service = Service.objects.get(name=svc)
                    svc_dict = dict()
                    svc_dict['key'] = service.id
                    svc_dict['value'] = service.alias
                    result['data']['objects']['services'].append(svc_dict)
            else:
                result['message'] = "Master site doesn't exist. <br />\
                                     Please first create master site with name 'master_UA'."
        else:
            result['message'] = "First add device in nms core."
    except:
        logger.info("No service to monitor.")

    return json.dumps({'result': result})


@dajaxice_register
def get_old_configuration_for_svc_edit(request, option="", service_id="", device_id=""):
    """Show currently present information of service in schema

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (int): checkbox value
        service_id (unicode): service id
        device_id (unicode): device id

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    params = []
    svc_templates = []
    show_old_configuration = "#show_old_configuration_{0}".format(option)
    template_options_id = "#template_options_id_{0}".format(option)
    if option and option != "":
        svc_params = ServiceParameters.objects.all()
        if svc_params:
            try:
                if svc_params:
                    device = Device.objects.get(pk=device_id)
                    service = Service.objects.get(pk=service_id)
                    dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                                    service_name=service.name)
                    params.append("<br />")
                    params.append("<h5 class='text-warning'><b>Current configuration:</b></h5>")
                    params.append("<div class=''>\
                                   <div class='box border orange'>\
                                   <div class='box-title'>\
                                        <h4><i class='fa fa-table'></i>Current Service Parameters</h4>\
                                   </div>")
                    params.append("<div class='box-body'><table class='table'>")
                    params.append("<thead><tr>\
                                        <th>Normal Check Interval</th>\
                                        <th>Retry Check Interval</th>\
                                        <th>Max Check Attemps</th>\
                                   </tr></thead>")
                    params.append("<tbody><tr><td>%d</td><td>%d</td><td>%d</td></tr>" % (dsc[0].normal_check_interval,
                                                                                         dsc[0].retry_check_interval,
                                                                                         dsc[0].max_check_attempts))
                    params.append("</tbody>")
                    params.append("<thead><tr><th>DS Name</th><th>Warning</th><th>Critical</th></tr></thead><tbody>")
                    for sds in dsc:
                        params.append("<tr><td class='ds_name'>{}</td><td class='ds_warning'>{}</td>\
                                       <td class='ds_critical'>{}</td></tr>"
                                      .format(sds.data_source if sds.data_source else "",
                                              int(sds.warning) if sds.warning else "",
                                              int(sds.critical) if sds.critical else ""))
                    params.append("</tbody></table></div></div></div>")
                    svc_templates.append("<p class='text-danger'><b>Select service template:</b></p> ")
                    svc_templates.append("<select class='form-control' id='service_template_%d'>" % option)
                    svc_templates.append("<option value='' selected>Select</option>")
                    for svc_param in svc_params:
                        svc_templates.append("<option value='%d'>%s</option>" % (svc_param.id,
                                                                                 svc_param.parameter_description))
                    svc_templates.append("</select>")
                else:
                    params.append("<h5 class='text-warning'>No data source associated.</h5> ")
            except:
                logger.info("No data source available.")
    else:
        params.append("<h5 class='text-warning'>No data source associated.</h5> ")
    dajax.assign(show_old_configuration, 'innerHTML', ''.join(params))
    dajax.assign(template_options_id, 'innerHTML', ''.join(svc_templates))
    return dajax.json()


@dajaxice_register
def get_new_configuration_for_svc_edit(request, service_id="", template_id=""):
    """Show modified information of service

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        service_id (int): service id
        template_id (unicode): template id

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    field_id = "#show_new_configuration_{0}".format(service_id)
    params = []
    service = Service.objects.get(pk=service_id)
    template = ServiceParameters.objects.get(pk=template_id)
    params.append("<br />")
    params.append("<h5 class='text-danger'><b>Modified configuration:</b></h5>")
    params.append("<div class=''>\
                   <div class='box border red'>\
                   <div class='box-title'>\
                       <h4><i class='fa fa-table'></i>Modified Service Parameters</h4>\
                   </div>")
    params.append("<div class='box-body'><table class='table'>")
    params.append("<thead><tr>\
                       <th>Normal Check Interval</th>\
                       <th>Retry Check Interval</th>\
                       <th>Max Check Attempts</th>\
                   </tr></thead>")
    params.append("<tbody><tr><td>%d</td><td>%d</td><td>%d</td></tr>" % (template.normal_check_interval,
                                                                         template.retry_check_interval,
                                                                         template.max_check_attempts))
    params.append("</tbody>")
    params.append("<thead><tr>\
                       <th>DS Name</th>\
                       <th>Warning</th>\
                       <th>Critical</th>\
                   </tr></thead><tbody>")
    data_sources = service.service_data_sources.all()
    for sds in data_sources:
        params.append("<tr class='data_source_field'><td class='ds_name'>{}</td>\
                       <td contenteditable='true' class='ds_warning'>{}</td>\
                       <td contenteditable='true' class='ds_critical'>{}</td></tr>"
                      .format(sds.name if sds.name else "",
                              int(sds.warning) if sds.warning else "",
                              int(sds.critical) if sds.critical else ""))
    params.append("</tbody></table></div></div></div>")
    dajax.assign(field_id, 'innerHTML', ''.join(params))
    return dajax.json()


@dajaxice_register
def edit_services(request, svc_data):
    """Edit device services

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        svc_data (list): list of dictionaries
                        i.e. [
                            {
                                'service_id': u'1',
                                'data_source': [
                                    {
                                        'warning': u'-50',
                                        'critical': u'-85',
                                        'name': u'rssi'
                                    }
                                ],
                                'template_id': u'2',
                                'device_id': u'545'
                            },
                            {
                                'service_id': u'13',
                                'data_source': [
                                    {
                                        'warning': u'',
                                        'critical': u'',
                                        'name': u'idu_sn'
                                    }
                                ],
                                'template_id': u'3',
                                'device_id': u'545'
                            }
                        ]

    Returns:
        result (dict): dictionary containing service information
                    i.e. {
                            'message': u"Successfully edited service 'radwin_rssi'. <br />
                                         Successfully edited service 'radwin_idu_sn_invent'. <br />",
                            'data': {
                                'snmp_community': {
                                    'read_community': 'public',
                                    'version': 'v1'
                                },
                                'service_name': 'radwin_idu_sn_invent',
                                'serv_params': {
                                    'normal_check_interval': 5,
                                    'max_check_attempts': 5,
                                    'retry_check_interval': 1
                                },
                                'device_name': 'device_116',
                                'mode': 'editservice',
                                'cmd_params': {

                                }
                            },
                            'success': 1
                        }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = ""
    result['data']['meta'] = {}
    result['data']['objects'] = {}

    # messages variable collects message coming from service addition api response
    messages = ""

    for sd in svc_data:
        service = ""
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}
        try:
            device = Device.objects.get(pk=int(sd['device_id']))
            service = Service.objects.get(pk=int(sd['service_id']))
            try:
                service_para = ServiceParameters.objects.get(pk=int(sd['template_id']))
            except Exception as e:
                service_para = service.parameters
                logger.info(e)
            # mode
            result['data']['objects']['mode'] = "editservice"
            # device name
            result['data']['objects']['device_name'] = str(device.device_name)
            # service name
            result['data']['objects']['service_name'] = str(service.name)
            # service parameters
            result['data']['objects']['serv_params'] = {}
            result['data']['objects']['serv_params']['normal_check_interval'] = int(service_para.normal_check_interval)
            result['data']['objects']['serv_params']['retry_check_interval'] = int(service_para.retry_check_interval)
            result['data']['objects']['serv_params']['max_check_attempts'] = int(service_para.max_check_attempts)
            # snmp parameters
            result['data']['objects']['snmp_community'] = {}
            result['data']['objects']['snmp_community']['version'] = str(service_para.protocol.version)
            result['data']['objects']['snmp_community']['read_community'] = str(service_para.protocol.read_community)
            # command parameters
            result['data']['objects']['cmd_params'] = {}
            for sds in sd['data_source']:
                if sds['warning'] != "":
                    result['data']['objects']['cmd_params'][str(sds['name'])] = {
                        'warning': str(sds['warning']) if sds['warning'] != "" else "",
                        'critical': str(sds['critical']) if sds['critical'] != "" else ""
                    }
            # snmp port
            # result['data']['objects']['snmp_port'] = str(service_para.protocol.port)
            # agent tag
            # result['data']['objects']['agent_tag'] = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
            # payload data for post request
            service_data = result['data']['objects']
            # master site on which service needs to be added
            master_site = SiteInstance.objects.get(name='master_UA')
            # url for nocout.py
            # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
            # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
            url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                    master_site.password,
                                                                    master_site.machine.machine_ip,
                                                                    master_site.web_service_port,
                                                                    master_site.name)
            # encoding service_data
            encoded_data = urllib.urlencode(service_data)

            # sending post request to nocout device app to add single service at a time
            r = requests.post(url, data=encoded_data)

            # converting post response data into python dict expression
            response_dict = ast.literal_eval(r.text)

            # if response(r) is given by post request than process it further to get success/failure messages
            if r:
                result['data'] = service_data
                result['success'] = 1
                # if response_dict doesn't have key 'success'
                if response_dict.get('success') != 1:
                    logger.info(response_dict.get('error_message'))
                    result['message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to edit service '%s'. <br />" % (service.name)
                    messages += result['message']

                    try:
                        # if service exist in 'service_deviceserviceconfiguration' table
                        # than update service else create it
                        for data_source in sd['data_source']:
                            dsc = DeviceServiceConfiguration.objects.get(device_name=device.device_name,
                                                                         service_name=service.name,
                                                                         data_source=data_source['name'])
                            dsc.agent_tag = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
                            dsc.port = str(service_para.protocol.port)
                            dsc.version = str(service_para.protocol.version)
                            dsc.read_community = str(service_para.protocol.read_community)
                            dsc.svc_template = str(service_para.parameter_description)
                            dsc.normal_check_interval = int(service_para.normal_check_interval)
                            dsc.retry_check_interval = int(service_para.retry_check_interval)
                            dsc.max_check_attempts = int(service_para.max_check_attempts)
                            if data_source['warning'] != "":
                                dsc.warning = int(data_source['warning'])
                            if data_source['critical'] != "":
                                dsc.critical = int(data_source['critical'])
                            dsc.is_added = 0
                            dsc.save()
                    except Exception as e:
                        logger.info(e)
                else:
                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>Successfully edited service '%s'. <br />" % service.name
                    device = Device.objects.get(pk=int(sd['device_id']))
                    messages += result['message']

                    # save service to 'service_deviceserviceconfiguration' table
                    try:
                        # if service exist in 'service_deviceserviceconfiguration' table
                        # than update service else create it
                        for data_source in sd['data_source']:
                            dsc = DeviceServiceConfiguration.objects.get(device_name=device.device_name,
                                                                         service_name=service.name,
                                                                         data_source=data_source['name'])
                            dsc.agent_tag = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
                            dsc.port = str(service_para.protocol.port)
                            dsc.version = str(service_para.protocol.version)
                            dsc.read_community = str(service_para.protocol.read_community)
                            dsc.svc_template = str(service_para.parameter_description)
                            dsc.normal_check_interval = int(service_para.normal_check_interval)
                            dsc.retry_check_interval = int(service_para.retry_check_interval)
                            dsc.max_check_attempts = int(service_para.max_check_attempts)
                            dsc.warning = int(data_source['warning']) if data_source['warning'] else ""
                            dsc.critical = int(data_source['critical']) if data_source['critical'] else ""
                            dsc.is_added = 1
                            dsc.save()
                    except Exception as e:
                        logger.info(e)

                    # set 'is_monitored_on_nms' to 1 if service is added successfully
                    device.is_monitored_on_nms = 1
                    device.save()
        except Exception as e:
            logger.info(e)
            result['message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to edit service '%s'. <br />" % service.name
            messages += result['message']

    # assign messages to result dict message key
    if messages:
        result['message'] = messages
    else:
        result['message'] = "No template is selected for any service"
    return json.dumps({'result': result})


@dajaxice_register
def delete_service_form(request, value):
    """Get parameters for service delete form

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        value (int): device id

    Returns:
        result (dict): dictionary containing services information
                    i.e. {
                            'message': 'Successfully render form.',
                            'data': {
                                'meta': '',
                                'objects': {
                                    'master_site': u'master_UA',
                                    'device_alias': u'Device116',
                                    'is_added': 1L,
                                    'services': [
                                        {
                                            'value': u'Receivedsignalstrength',
                                            'key': 1L
                                        },
                                        {
                                            'value': u'IDUserialnumber',
                                            'key': 13L
                                        },
                                        {
                                            'value': u'totaldownlinkutilization',
                                            'key': 7L
                                        },
                                        {
                                            'value': u'ODUserialnumber',
                                            'key': 14L
                                        },
                                        {
                                            'value': u'portspeedstatus',
                                            'key': 11L
                                        },
                                        {
                                            'value': u'totaluplinkutilization',
                                            'key': 8L
                                        },
                                        {
                                            'value': u'channelbandwidth',
                                            'key': 15L
                                        },
                                        {
                                            'value': u'portup-downstatus',
                                            'key': 10L
                                        }
                                    ],
                                    'device_name': u'device_116',
                                    'device_id': 545
                                }
                            },
                            'success': 0
                        }

    """
    # device to which services are associated
    device = Device.objects.get(id=value)
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Failed to render form correctly."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['device_id'] = value
    result['data']['objects']['device_name'] = device.device_name
    result['data']['objects']['device_alias'] = device.device_alias
    result['data']['objects']['services'] = []
    result['data']['objects']['master_site'] = ""
    result['data']['objects']['is_added'] = device.is_added_to_nms

    # get services associated with device
    try:
        master_site_name = ""
        try:
            master_site_name = SiteInstance.objects.get(name='master_UA').name
            result['data']['objects']['master_site'] = master_site_name
        except:
            logger.info("Master site doesn't exist.")
        if device.is_added_to_nms == 1:
            if master_site_name == "master_UA":
                # fetching all services from 'service device configuration' table
                dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name)

                # services those are already running for this device
                services = []
                for svc in dsc:
                    services.append(svc.service_name)

                # extracting unique set of services form 'services' list
                monitored_services = set(services)

                result['data']['objects']['services'] = []
                for svc in monitored_services:
                    service = Service.objects.get(name=svc)
                    svc_dict = dict()
                    svc_dict['key'] = service.id
                    svc_dict['value'] = service.alias
                    result['data']['objects']['services'].append(svc_dict)
            else:
                result['message'] = "Master site doesn't exist. <br />\
                                     Please first create master site with name 'master_UA'."
        else:
            result['message'] = "First add device in nms core."
    except:
        logger.info("No service to monitor.")
    return json.dumps({'result': result})


@dajaxice_register
def delete_services(request, service_data):
    """Delete device services

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        service_data (list): list of dictionaries
                        i.e. [
                                {
                                    'service_id': u'1',
                                    'device_id': u'545'
                                },
                                {
                                    'service_id': u'7',
                                    'device_id': u'545'
                                },
                                {
                                    'service_id': u'14',
                                    'device_id': u'545'
                                }
                            ]

    Returns:
        result (dict):  dictionary containing service information
                    i.e. {
                            'message': u"Successfully deleted service 'radwin_rssi'. <br />
                                         Successfully deleted service 'radwin_dl_utilization'. <br />
                                         Successfully deleted service 'radwin_odu_sn_invent'. <br />",
                            'data': {
                                'service_name': 'radwin_odu_sn_invent',
                                'mode': 'deleteservice',
                                'device_name': 'device_116'
                            },
                            'success': 1
                        }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = ""
    result['data']['meta'] = {}
    result['data']['objects'] = {}

    # messages variable collects message coming from service addition api response
    messages = ""
    for svc in service_data:
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}

        try:
            device = Device.objects.get(pk=svc['device_id'])
            service = Service.objects.get(pk=svc['service_id'])
            service_data = {
                'mode': 'deleteservice',
                'device_name': str(device.device_name),
                'service_name': str(service.name)
            }

            master_site = SiteInstance.objects.get(name='master_UA')
            # url for nocout.py
            # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
            # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
            url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                    master_site.password,
                                                                    master_site.machine.machine_ip,
                                                                    master_site.web_service_port,
                                                                    master_site.name)

            # encoding service_data
            encoded_data = urllib.urlencode(service_data)

            # sending post request to nocout device app to add single service at a time
            r = requests.post(url, data=encoded_data)

            # converting post response data into python dict expression
            response_dict = ast.literal_eval(r.text)

            # if response(r) is given by post request than process it further to get success/failure messages
            if r:
                result['data'] = service_data
                result['success'] = 1

                # if response_dict doesn't have key 'success'
                if response_dict.get('success') != 1:
                    logger.info(response_dict.get('error_message'))
                    result['message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to delete service '%s'. <br />" % service.name
                    messages += result['message']
                else:
                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>Successfully deleted service '%s'. <br />" % service.name
                    messages += result['message']
                    # delete service rows form 'service_deviceserviceconfiguration' table
                    DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                              service_name=service.name).delete()

        except Exception as e:
            logger.info(e.message)
            result['message'] += e.message
    result['message'] = messages
    return json.dumps({'result': result})


@dajaxice_register
def add_service_form(request, value):
    """Show add service form

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        value (int): device id

    Returns:
        result (dict):  dictionary containing services information
                    i.e. {
                            'message': 'Successfully render form.',
                            'data': {
                                'meta': '',
                                'objects': {
                                    'master_site': u'master_UA',
                                    'device_alias': u'Device116',
                                    'is_added': 1L,
                                    'services': [
                                        {
                                            'value': u'Receivedsignalstrength',
                                            'key': 1L
                                        },
                                        {
                                            'value': u'totaldownlinkutilization',
                                            'key': 7L
                                        },
                                        {
                                            'value': u'ODUserialnumber',
                                            'key': 14L
                                        },
                                        {
                                            'value': u'ssid',
                                            'key': 20L
                                        },
                                        {
                                            'value': u'IDUserialnumber',
                                            'key': 13L
                                        },
                                        {
                                            'value': u'totaluptime',
                                            'key': 4L
                                        },
                                        {
                                            'value': u'frequency',
                                            'key': 16L
                                        },
                                        {
                                            'value': u'RadwinUAS',
                                            'key': 5L
                                        },
                                        {
                                            'value': u'portautonegotiationstatus',
                                            'key': 12L
                                        },
                                        {
                                            'value': u'linkdistance',
                                            'key': 18L
                                        },
                                        {
                                            'value': u'portlinkethernetstatus',
                                            'key': 9L
                                        },
                                        {
                                            'value': u'estimatedthroughput',
                                            'key': 6L
                                        },
                                        {
                                            'value': u'mimoanddiversitytype',
                                            'key': 17L
                                        },
                                        {
                                            'value': u'portup-downstatus',
                                            'key': 10L
                                        },
                                        {
                                            'value': u'producttype',
                                            'key': 19L
                                        }
                                    ],
                                    'device_name': u'device_116',
                                    'device_id': 545
                                }
                            },
                            'success': 0
                        }

    """
    # device to which services are associated
    device = Device.objects.get(id=value)
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Failed to render form correctly."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['device_id'] = value
    result['data']['objects']['device_name'] = device.device_name
    result['data']['objects']['device_alias'] = device.device_alias
    result['data']['objects']['services'] = []
    result['data']['objects']['master_site'] = ""
    result['data']['objects']['is_added'] = device.is_added_to_nms

    # get services associated with device
    try:
        master_site_name = ""
        try:
            master_site_name = SiteInstance.objects.get(name='master_UA').name
            result['data']['objects']['master_site'] = master_site_name
        except Exception as e:
            logger.info(e.message)

        if device.is_added_to_nms == 1:
            if master_site_name == "master_UA":
                # fetching all services from 'service device configuration' table
                dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name)
                device_type = DeviceType.objects.get(id=device.device_type)

                # complete no. of services associated with this device
                complete_services = []
                for svc in device_type.service.all():
                    complete_services.append(svc.name)

                # services those are already running for this device
                services = []
                for svc in dsc:
                    services.append(svc.service_name)

                # services those are already running for this device
                already_added_services = []
                for svc in dsc:
                    already_added_services.append(svc.service_name)

                # services those are not currently running but associated with that device
                services = set(complete_services) - set(already_added_services)

                result['data']['objects']['services'] = []
                for svc in services:
                    service = Service.objects.get(name=svc)
                    svc_dict = dict()
                    svc_dict['key'] = service.id
                    svc_dict['value'] = service.alias
                    result['data']['objects']['services'].append(svc_dict)

            else:
                result['message'] = "Master site doesn't exist. <br />\
                                     Please first create master site with name 'master_UA'."
        else:
            result['message'] = "First add device in nms core."
    except:
        logger.info("No service to monitor.")
    return json.dumps({'result': result})


@dajaxice_register
def get_old_configuration_for_svc_add(request, option="", service_id="", device_id=""):
    """Show currently present information of service in schema

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        option (int): checkbox value
        service_id (unicode): service id
        device_id (unicode): device id

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    params = []
    svc_templates = []
    template_options_id = "#template_options_id_{0}".format(option)
    if option and option != "":
        svc_params = ServiceParameters.objects.all()
        if svc_params:
            try:
                if svc_params:
                    device = Device.objects.get(pk=device_id)
                    service = Service.objects.get(pk=service_id)
                    params.append("<br />")
                    svc_templates.append("<p class='text-warning'><b>Select service template:</b></p> ")
                    svc_templates.append("<select class='form-control' id='service_template_%d'>" % option)
                    svc_templates.append("<option value='' selected>Select</option>")
                    for svc_param in svc_params:
                        svc_templates.append("<option value='%d'>%s</option>" % (svc_param.id,
                                                                                 svc_param.parameter_description))
                    svc_templates.append("</select>")
                else:
                    params.append("<h5 class='text-warning'>No data source associated.</h5> ")
            except:
                logger.info("No data source available.")
    else:
        params.append("<h5 class='text-warning'>No data source associated.</h5> ")
    dajax.assign(template_options_id, 'innerHTML', ''.join(svc_templates))
    return dajax.json()


@dajaxice_register
def get_new_configuration_for_svc_add(request, service_id="", template_id=""):
    """Show modified information of service

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        service_id (int): service id
        template_id (unicode): template id

    Returns:
        dajax (str): string containing list of dictionaries
                    i.e. [{"cmd": "as",
                           "id": "#name_id",
                           "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                           "prop": "innerHTML"}]

    """
    dajax = Dajax()
    field_id = "#show_new_configuration_{0}".format(service_id)
    params = []
    service = Service.objects.get(pk=service_id)
    template = ServiceParameters.objects.get(pk=template_id)
    params.append("<br />")
    params.append("<h5 class='text-warning'><b>Selected configuration:</b></h5>")
    params.append("<div class=''>\
                   <div class='box border orange'>\
                   <div class='box-title'>\
                       <h4><i class='fa fa-table'></i>Selected Service Parameters</h4>\
                   </div>")
    params.append("<div class='box-body'><table class='table'>")
    params.append("<thead><tr>\
                       <th>Normal Check Interval</th>\
                       <th>Retry Check Interval</th>\
                       <th>Max Check Attempts</th>\
                   </tr></thead>")
    params.append("<tbody><tr><td>%d</td><td>%d</td><td>%d</td></tr>" % (template.normal_check_interval,
                                                                         template.retry_check_interval,
                                                                         template.max_check_attempts))
    params.append("</tbody>")
    params.append("<thead><tr><th>DS Name</th><th>Warning</th><th>Critical</th></tr></thead><tbody>")
    # data sources associated with service
    data_sources = service.service_data_sources.all()
    for sds in data_sources:
        params.append("<tr class='data_source_field'><td class='ds_name'>{}</td>\
                       <td contenteditable='true' class='ds_warning'>{}</td>\
                       <td contenteditable='true' class='ds_critical'>{}</td></tr>"
                      .format(sds.name if sds.name else "",
                              int(sds.warning) if sds.warning else "",
                              int(sds.critical) if sds.critical else ""))
    params.append("</tbody></table></div></div></div>")
    dajax.assign(field_id, 'innerHTML', ''.join(params))
    return dajax.json()


@dajaxice_register
def add_services(request, svc_data):
    """Add device services

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        svc_data (list): list of dictionaries
                        i.e. [
                            {
                                'service_id': u'1',
                                'data_source': [
                                    {
                                        'warning': u'-50',
                                        'critical': u'-85',
                                        'name': u'rssi'
                                    }
                                ],
                                'template_id': u'2',
                                'device_id': u'545'
                            },
                            {
                                'service_id': u'13',
                                'data_source': [
                                    {
                                        'warning': u'',
                                        'critical': u'',
                                        'name': u'idu_sn'
                                    }
                                ],
                                'template_id': u'3',
                                'device_id': u'545'
                            }
                        ]

    Returns:
        result (dict): dictionary of services information
                    i.e. {
                            'message': u"Successfully edited service 'radwin_rssi'. <br />
                                         Successfully edited service 'radwin_idu_sn_invent'. <br />",
                            'data': {
                                'snmp_community': {
                                    'read_community': 'public',
                                    'version': 'v1'
                                },
                                'service_name': 'radwin_idu_sn_invent',
                                'serv_params': {
                                    'normal_check_interval': 5,
                                    'max_check_attempts': 5,
                                    'retry_check_interval': 1
                                },
                                'device_name': 'device_116',
                                'mode': 'editservice',
                                'cmd_params': {

                                }
                            },
                            'success': 1
                        }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = ""
    result['data']['meta'] = {}
    result['data']['objects'] = {}

    # messages variable collects message coming from service addition api response
    messages = ""

    for sd in svc_data:
        service = ""
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""
        result['data']['meta'] = {}
        result['data']['objects'] = {}
        try:
            device = Device.objects.get(pk=int(sd['device_id']))
            service = Service.objects.get(pk=int(sd['service_id']))

            # if service template is not selected than default is taken
            try:
                service_para = ServiceParameters.objects.get(pk=int(sd['template_id']))
            except Exception as e:
                service_para = service.parameters
                logger.info(e.message)

            # data_sources --> contains list of data sources
            data_sources = []
            try:
                if 'data' in sd:
                    for sds in sd['data_source']:
                        temp_dict = dict()
                        temp_dict['name'] = str(sds['name']) if sds['name'] != "" else ""
                        temp_dict['warning'] = str(sds['warning']) if sds['warning'] != "" else ""
                        temp_dict['critical'] = str(sds['critical']) if sds['critical'] != "" else ""
                        data_sources.append(temp_dict)
                else:
                    for sds in service.service_data_sources.all():
                        temp_dict = dict()
                        temp_dict['name'] = str(sds.name) if sds.name != "" else ""
                        temp_dict['warning'] = str(sds.warning) if sds.warning != "" else ""
                        temp_dict['critical'] = str(sds.critical) if sds.critical != "" else ""
                        data_sources.append(temp_dict)
            except Exception as e:
                logger.info(e.message)

            # mode
            result['data']['objects']['mode'] = "addservice"
            # device name
            result['data']['objects']['device_name'] = str(device.device_name)
            # service name
            result['data']['objects']['service_name'] = str(service.name)
            # service parameters
            result['data']['objects']['serv_params'] = {}
            result['data']['objects']['serv_params']['normal_check_interval'] = int(service_para.normal_check_interval)
            result['data']['objects']['serv_params']['retry_check_interval'] = int(service_para.retry_check_interval)
            result['data']['objects']['serv_params']['max_check_attempts'] = int(service_para.max_check_attempts)
            # snmp parameters
            result['data']['objects']['snmp_community'] = {}
            result['data']['objects']['snmp_community']['version'] = str(service_para.protocol.version)
            result['data']['objects']['snmp_community']['read_community'] = str(service_para.protocol.read_community)
            # command parameters
            result['data']['objects']['cmd_params'] = {}
            for data_source in data_sources:
                if data_source['warning'] != "":
                    result['data']['objects']['cmd_params'][str(data_source['name'])] = {
                        'warning': data_source['warning'],
                        'critical': data_source['critical']
                    }

            # snmp port
            result['data']['objects']['snmp_port'] = str(service_para.protocol.port)
            # agent tag
            result['data']['objects']['agent_tag'] = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
            # payload data for post request
            service_data = result['data']['objects']
            # master site on which service needs to be added
            master_site = SiteInstance.objects.get(name='master_UA')
            # url for nocout.py
            # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
            # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
            url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                    master_site.password,
                                                                    master_site.machine.machine_ip,
                                                                    master_site.web_service_port,
                                                                    master_site.name)
            # encoding service_data
            encoded_data = urllib.urlencode(service_data)

            # sending post request to nocout device app to add single service at a time
            r = requests.post(url, data=encoded_data)

            # converting post response data into python dict expression
            response_dict = ast.literal_eval(r.text)

            # if response(r) is given by post request than process it further to get success/failure messages
            if r:
                result['data'] = service_data
                result['success'] = 1
                # if response_dict doesn't have key 'success'
                if response_dict.get('success') != 1:
                    logger.info(response_dict.get('error_message'))
                    result['message'] += "<i class=\"fa fa-times red-dot\"></i> Failed to add service '%s'. <br />" % (service.name)
                    messages += result['message']

                    try:
                        # add service in 'service_deviceserviceconfiguration' table
                        for data_source in data_sources:
                            dsc = DeviceServiceConfiguration()
                            dsc.device_name = device.device_name
                            dsc.service_name = service.name
                            dsc.agent_tag = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
                            dsc.port = str(service_para.protocol.port)
                            dsc.version = str(service_para.protocol.version)
                            dsc.read_community = str(service_para.protocol.read_community)
                            dsc.svc_template = str(service_para.parameter_description)
                            dsc.normal_check_interval = int(service_para.normal_check_interval)
                            dsc.retry_check_interval = int(service_para.retry_check_interval)
                            dsc.max_check_attempts = int(service_para.max_check_attempts)
                            dsc.data_source = data_source['name']
                            dsc.warning = data_source['warning']
                            dsc.critical = data_source['critical']
                            dsc.is_added = 0
                            dsc.save()
                    except Exception as e:
                        logger.info(e)
                else:
                    result['message'] += "<i class=\"fa fa-check green-dot\"></i> Successfully added service '%s'. <br />" % service.name
                    device = Device.objects.get(pk=int(sd['device_id']))
                    messages += result['message']

                    # save service to 'service_deviceserviceconfiguration' table
                    try:
                        # if service exist in 'service_deviceserviceconfiguration' table
                        # than update service else create it
                        for data_source in data_sources:
                            dsc = DeviceServiceConfiguration()
                            dsc.device_name = device.device_name
                            dsc.service_name = service.name
                            dsc.agent_tag = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
                            dsc.port = str(service_para.protocol.port)
                            dsc.version = str(service_para.protocol.version)
                            dsc.read_community = str(service_para.protocol.read_community)
                            dsc.svc_template = str(service_para.parameter_description)
                            dsc.normal_check_interval = int(service_para.normal_check_interval)
                            dsc.retry_check_interval = int(service_para.retry_check_interval)
                            dsc.max_check_attempts = int(service_para.max_check_attempts)
                            dsc.data_source = data_source['name']
                            dsc.warning = data_source['warning']
                            dsc.critical = data_source['critical']
                            dsc.is_added = 1
                            dsc.save()
                    except Exception as e:
                        logger.info(e.message)

                    # set 'is_monitored_on_nms' to 1 if service is added successfully
                    device.is_monitored_on_nms = 1
                    device.save()
        except Exception as e:
            logger.info(e)
            result['message'] += "<i class=\"fa fa-times red-dot\"></i> Failed to add service '%s'. <br />" % service.name
            messages += result['message']

    # assign messages to result dict message key
    result['message'] = messages
    return json.dumps({'result': result})


@dajaxice_register
def device_services_status(request, device_id):
    """Show current device services status

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): POST request
        device_id (int): device id

    Returns:
        result (dict): dictionary of device and associated services information
                    i.e. {
                            'message': '',
                            'data': {
                                'meta': {

                                },
                                'objects': {
                                    'site_instance': 'nocout_gis_slave',
                                    'inactive_services': [
                                        {
                                            'service': u'Receivedsignalstrength',
                                            'data_sources': 'Receivedsignalstrength,
                                            '
                                        },
                                        {
                                            'service': u'totaluplinkutilization',
                                            'data_sources': 'Management_Port_on_Odu,
                                            Radio_Interface,
                                            '
                                        },
                                        {
                                            'service': u'channelbandwidth',
                                            'data_sources': 'channelbandwidth,
                                            '
                                        },
                                        {
                                            'service': u'portspeedstatus',
                                            'data_sources': 'ethernet_port_1,
                                            ethernet_port_2,
                                            ethernet_port_3,
                                            ethernet_port_4,
                                            '
                                        },
                                        {
                                            'service': u'IDUserialnumber',
                                            'data_sources': 'IDUserialnumber,
                                            '
                                        },
                                        {
                                            'service': u'totaluptime',
                                            'data_sources': 'totaluptime,
                                            '
                                        },
                                        {
                                            'service': u'frequency',
                                            'data_sources': 'frequency,
                                            '
                                        },
                                        {
                                            'service': u'RadwinUAS',
                                            'data_sources': 'unavailableseconds,
                                            '
                                        },
                                        {
                                            'service': u'portautonegotiationstatus',
                                            'data_sources': 'ethernet_port_1,
                                            ethernet_port_2,
                                            ethernet_port_3,
                                            ethernet_port_4,
                                            '
                                        }
                                    ],
                                    'active_services': [

                                    ],
                                    'device_name': '115.112.95.187',
                                    'machine': 'default',
                                    'device_type': 'Radwin2KBS',
                                    'ip_address': '115.112.95.187'
                                }
                            },
                            'success': 1
                        }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = ""
    result['data']['meta'] = {}
    result['data']['objects'] = {}

    # current device
    device = Device.objects.get(pk=device_id)

    # fetching all services from 'service device configuration' table
    dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name)
    device_type = DeviceType.objects.get(id=device.device_type)

    # complete no. of services associated with this device
    complete_services = []
    for svc in device_type.service.all():
        complete_services.append(svc.name)

    # services those are already running for this device
    already_added_services = []
    for svc in dsc:
        already_added_services.append(svc.service_name)

    # services those are not currently running but associated with that device
    inactive_services = set(complete_services) - set(already_added_services)

    # services those are currently running and associated with current device
    active_services = set(already_added_services)

    result['data']['objects']['device_name'] = str(device.device_alias)
    result['data']['objects']['machine'] = str(device.machine)
    result['data']['objects']['site_instance'] = str(device.site_instance)
    result['data']['objects']['ip_address'] = str(device.ip_address)
    result['data']['objects']['device_type'] = str(DeviceType.objects.get(pk=device.device_type))
    result['data']['objects']['active_services'] = []
    result['data']['objects']['inactive_services'] = []

    for svc in active_services:
        service = Service.objects.get(name=svc)
        temp_svc = dict()
        temp_svc['service'] = service.alias
        temp_svc['data_sources'] = ""
        for ds in service.service_data_sources.all():
            temp_svc['data_sources'] += "{}, ".format(ds.alias)
        result['data']['objects']['active_services'].append(temp_svc)

    for svc in inactive_services:
        service = Service.objects.get(name=svc)
        temp_svc = dict()
        temp_svc['service'] = service.alias
        temp_svc['data_sources'] = ""
        for ds in service.service_data_sources.all():
            temp_svc['data_sources'] += "{}, ".format(ds.alias)
        result['data']['objects']['inactive_services'].append(temp_svc)

    return json.dumps({'result': result})