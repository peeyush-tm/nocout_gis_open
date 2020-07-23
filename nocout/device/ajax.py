"""
===============================================================================
Module contains ajax functionality specific to 'device' app.
===============================================================================

Location:
* /nocout_gis/nocout/device/ajax.py

List of constructs:
=======
Methods
=======
* update_vendor
* update_model
* update_type
* update_ports
* update_sites
* after_update_site
* after_update_vendor
* after_update_model
* after_update_type
* after_update_ports
* device_type_extra_fields
* device_parent_choices_initial
* device_parent_choices_selected
* device_extra_fields_update
* device_soft_delete_form
* device_soft_delete
* device_restore_form
* device_restore
* update_states
* update_cities
* update_states_after_invalid_form
* update_cities_after_invalid_form
* add_device_to_nms_core_form
* add_device_to_nms_core
* edit_device_in_nms_core
* delete_device_from_nms_core
* modify_device_state
* sync_device_with_nms_core
* remove_sync_deadlock
* edit_single_service_form
* get_service_para_table
* edit_single_service
* delete_single_service_form
* delete_single_service
* edit_service_form
* get_old_configuration_for_svc_edit
* get_new_configuration_for_svc_edit
* get_ping_configuration_for_svc_edit
* edit_services
* delete_service_form
* delete_services
* add_service_form
* get_old_configuration_for_svc_add
* get_new_configuration_for_svc_add
* add_services
* device_services_status
* reset_service_configuration
"""

import ast
import json
from datetime import datetime
import time
from machine.models import Machine
import requests
import logging
import urllib
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType, \
    DeviceTypeFieldsValue, Country, State, DeviceSyncHistory
from service.models import Service, ServiceParameters, DeviceServiceConfiguration, DevicePingConfiguration
from site_instance.models import SiteInstance
from django.conf import settings

logger = logging.getLogger(__name__)


@dajaxice_register(method='GET')
def update_vendor(request, option):
    """
    Updating vendors corresponding to selected technology.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected technology.
    tech = DeviceTechnology.objects.get(pk=int(option))

    # Vendors associated with the selected technology.
    vendors = tech.device_vendors.all()

    out = list()
    out.append("<option value='' selected>Select</option>")

    for vendor in vendors:
        out.append("<option value='%d'>%s</option>" % (vendor.id, vendor.alias))

    dajax.assign('#id_device_vendor', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def update_model(request, option):
    """
    Updating models corresponding to the selected vendor.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected vendor.
    vendor = DeviceVendor.objects.get(pk=int(option))

    # Models associated with the selected vendor.
    models = vendor.device_models.all()

    out = list()
    out.append("<option value=''>Select</option>")

    for model in models:
        out.append("<option value='%d'>%s</option>" % (model.id, model.name))

    dajax.assign('#id_device_model', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def update_type(request, option):
    """
    Updating types corresponding to the selected model.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected model.
    model = DeviceModel.objects.get(pk=int(option))

    # Types associated with the selected model.
    types = model.device_types.all()

    out = list()
    out.append("<option value=''>Select</option>")

    for dtype in types:
        out.append("<option value='%d'>%s</option>" % (dtype.id, dtype.name))

    dajax.assign('#id_device_type', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def update_ports(request, option):
    """
    Updating ports corresponding to the selected type.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected device type.
    device_type = DeviceType.objects.get(pk=int(option))

    # Ports associated with the selected type.
    ports = device_type.device_port.all()

    out = list()
    out.append("<option value=''>Select</option>")

    for port in ports:
        out.append("<option value='%d'>%s - (%d)</option>" % (port.id, port.alias, port.value))

    dajax.assign('#id_ports', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def update_sites(request, option):
    """
    Updating sites corresponding to selected machine.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected machine.
    machine = Machine.objects.get(pk=int(option))

    # Vendors associated with the selected technology.
    sites = machine.siteinstance_set.all()

    out = list()
    out.append("<option value='' selected>Select</option>")

    for site in sites:
        out.append("<option value='%d'>%s</option>" % (site.id, site.alias))
    dajax.assign('#id_site_instance', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def after_update_site(request, option, selected=''):
    """
    Get site selection menu with last selected site after unsuccessful form submission.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Kwargs:
        selected (unicode): Option value selected before unsuccessful form submission.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected machine.
    machine = Machine.objects.get(pk=int(option))

    # Sites associated with selected technology.
    sites = machine.siteinstance_set.all()

    out = list()
    out.append("<option value=''>Select</option>")

    for site in sites:
        if site.id == int(selected):
            out.append("<option value='%d' selected>%s</option>" % (site.id, site.alias))
        else:
            out.append("<option value='%d'>%s</option>" % (site.id, site.alias))

    dajax.assign('#id_site_instance', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def after_update_vendor(request, option, selected=''):
    """
    Get vendor selection menu with last selected vendor after unsuccessful form submission.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Kwargs:
        selected (unicode): Option value selected before unsuccessful form submission.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected technology.
    tech = DeviceTechnology.objects.get(pk=int(option))

    # Vendors associated with selected technology.
    vendors = tech.device_vendors.all()

    out = list()
    out.append("<option value=''>Select</option>")

    for vendor in vendors:
        if vendor.id == int(selected):
            out.append("<option value='%d' selected>%s</option>" % (vendor.id, vendor.alias))
        else:
            out.append("<option value='%d'>%s</option>" % (vendor.id, vendor.alias))

    dajax.assign('#id_device_vendor', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def after_update_model(request, option, selected=''):
    """
    Get model selection menu with last selected model after unsuccessful form submission.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Kwargs:
        selected (unicode): Option value selected before unsuccessful form submission.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected vendor.
    vendor = DeviceVendor.objects.get(pk=int(option))

    # Models associated with selected vendor.
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


@dajaxice_register(method='GET')
def after_update_type(request, option, selected=''):
    """
    Get type selection menu with last selected type after unsuccessful form submission.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Kwargs:
        selected (unicode): Option value selected before unsuccessful form submission.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected model.
    model = DeviceModel.objects.get(pk=int(option))

    # Types associated with selected model.
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


@dajaxice_register(method='GET')
def after_update_ports(request, option, selected=list()):
    """
    Get ports selection menu with last selected port after unsuccessful form submission.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Kwargs:
        selected (unicode): Option value selected before unsuccessful form submission.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected type.
    device_type = DeviceType.objects.get(pk=int(option))

    # Ports associated with selected type.
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


@dajaxice_register(method='GET')
def device_type_extra_fields(request, option):
    """
    Show extra fields associated with device type on selecting device type.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected device type.
    device_type = DeviceType.objects.get(pk=int(option))

    # Selected device extra.
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


@dajaxice_register(method='GET')
def device_parent_choices_initial(request):
    """
    Get parent selection menu having option titles including ip address.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    out = ["<option value=''>Select</option>"]

    for device in Device.objects.all():
        out.append("<option value='%d'>%s - (%s)</option>"
                   % (int(device.id), device.device_alias, device.ip_address))

    dajax.assign("#id_parent", 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def device_parent_choices_selected(request, option):
    """
    Get parent selection menu having option titles including ip address after unsuccessful form submission.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
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


@dajaxice_register(method='GET')
def device_extra_fields_update(request, device_type, device_name):
    """
    Show device extra fields in device update form.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_type (unicode): Device type value.
        device_name (unicode): Device name.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Current device.
    device = Device.objects.get(device_name=device_name)

    # Device type of current device.
    device_type = DeviceType.objects.filter(id=device_type)[0]

    # Extra fields associated with current device.
    device_extra_fields = device_type.devicetypefields_set.all()

    out = list()

    for extra_field in device_extra_fields:
        field_value = ""
        try:
            dtfv = DeviceTypeFieldsValue.objects.get(device_type_field=extra_field.id, device_id=device.id)
            field_value = dtfv.field_value
        except Exception as e:
            logger.info("Device type field doesn't exist.")
        out.append(
            "<div class='form-group'><label for='%s' class='col-sm-5 control-label'>\
            %s:</label><div class='col-sm-7'><input id='%s' name='%s' type='text' class='form-control' value='%s' />\
            </div></div>"
            % (extra_field.field_name, extra_field.field_display_name,
               extra_field.field_name, extra_field.field_name, field_value))

    dajax.assign('#extra_fields', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def device_soft_delete_form(request, value):
    """
    Get data to show on device soft delete form.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        value (int): Device ID.

    Returns:
        result (dictionary): Dictionary contains device and it's children's values.
                             For e.g.,
                                {
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

    Note:
        * Child Devices: These are the devices which are associated with the device,
                         which needs to be deleted in parent-child relationship.
        * Child Device Descendant: Set of all child devices descendants (needs for
                                   filtering new parent devices choice).
        * Eligible Devices: These are the devices which are not associated with the device,
                            (which needs to be deleted) & are eligible to be the
                            parent of devices in child devices.
    """
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

    # These are the devices which are associated with the device,
    # which needs to be deleted in parent-child relationship.
    child_devices = Device.objects.filter(parent_id=value, is_deleted=0)

    # Set of all child devices descendants (needs for filtering new parent devices choice).
    child_device_descendants = []
    for child_device in child_devices:
        device_descendant = child_device.get_descendants()
        for cd in device_descendant:
            child_device_descendants.append(cd)

    result['data']['objects']['childs'] = []
    result['data']['objects']['eligible'] = []

    # Future device parent is needed to find out only if our device is
    # associated with any other device i.e if child_devices.count() > 0.
    if child_devices.count() > 0:
        # These are the devices which are not associated with the
        # device (which needs to be deleted) & are eligible to be the
        # parent of devices in child_devices.
        remaining_devices = Device.objects.exclude(parent_id=value)
        selected_devices = set(remaining_devices) - set(child_device_descendants)
        result['data']['objects']['eligible'] = []
        for e_dv in selected_devices:
            e_dict = dict()
            e_dict['key'] = e_dv.id
            e_dict['value'] = e_dv.device_name
            # For excluding 'device' which we are deleting from eligible
            # device choices.
            if e_dv.id == device.id:
                continue
            if e_dv.is_deleted == 1:
                continue
            # For excluding devices from eligible device choices those are not from
            # same device_group as the device which we are deleting.
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


@dajaxice_register(method='GET')
def device_soft_delete(request, device_id, new_parent_id):
    """ 
    Soft delete device i.e. not deleting device from database, it just set
    it's is_deleted field value to 1 & remove it's relationship with any other device
    & make some other device parent of associated device.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        value (int): Device ID.

    Returns:
        result (dictionary): Dictionary contains device and it's children's values.
                             For e.g.,
                                 {
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
    device = Device.objects.get(id=device_id)

    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "No data exists."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['device_id'] = device_id
    result['data']['objects']['device_name'] = device.device_name

    # New parent device for associated devices.
    new_parent = ""

    try:
        new_parent = Device.objects.get(id=new_parent_id)
    except Exception as e:
        logger.info("No new device parent exist. Exception: ", e.message)

    # Fetching all child devices of device which needs to be deleted.
    child_devices = ""
    try:
        child_devices = Device.objects.filter(parent_id=device_id)
    except Exception as e:
        logger.info("No child device exists. Exception: ", e.message)

    # Assign new parent device to all child devices.
    if new_parent:
        if child_devices.count() > 0:
            child_devices.update(parent=new_parent)

    # Delete device from nms core if it is already added there(nms core).
    if device.host_state != "Disable" and device.is_added_to_nms != 0:
        device.is_added_to_nms = 0
        device.is_monitored_on_nms = 0
        device.save()
        # Remove device services from 'service_deviceserviceconfiguration' table.
        DeviceServiceConfiguration.objects.filter(device_name=device.device_name).delete()
        # Remove device ping service from 'service_devicepingconfiguration' table.
        DevicePingConfiguration.objects.filter(device_name=device.device_name).delete()

    # Setting 'is_deleted' bit of device to 1 which means device is soft deleted.
    if device.is_deleted == 0:
        device.is_deleted = 1
        device.save()
        # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
        try:
            device.site_instance.is_device_change = 1
            device.site_instance.save()
        except Exception as e:
            pass
        result['success'] = 1
        result['message'] = "Successfully deleted."
    else:
        result['success'] = 0
        result['message'] = "Already soft deleted."

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def device_restore_form(request, value):
    """ 
    Get data to show on device restore form.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        value (int): Device ID.

    Returns:
        result (dictionary): Dictionary contains device and it's children's values.
                             For e.g.,
                                {
                                    'message': 'Successfully render form.',
                                    'data': {
                                        'meta': '',
                                        'objects': {
                                            'alias': u'091HYDE030007077237_NE',
                                            'id': 6247L,
                                            'name': u'1'
                                        }
                                    },
                                    'success': 1
                                }
    """
    device = Device.objects.get(id=value)

    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Failed to render form correctly."
    result['data']['meta'] = ''
    result['data']['objects'] = {}

    if device:
        result['data']['objects']['id'] = device.id
        result['data']['objects']['name'] = device.device_name
        result['data']['objects']['alias'] = device.device_alias
        result['success'] = 1
        result['message'] = "Successfully render form."

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def device_restore(request, device_id):
    """ 
    Restoring device to device inventory.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_id (int): Device ID.

    Returns:
        result (dictionary): Dictionary contains device and it's children's values.
                             For e.g., 
                                {
                                    'message': 'Successfully restored device (091HYDE030007077237_NE).',
                                    'data': {
                                        'meta': '',
                                        'objects': {
                                            'device_name': u'1',
                                            'device_id': u'6247'
                                        }
                                    },
                                    'success': 1
                                }

    """
    device = Device.objects.get(id=device_id)

    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "No data exists."
    result['data']['meta'] = ''
    result['data']['objects'] = {}
    result['data']['objects']['device_id'] = device_id
    result['data']['objects']['device_name'] = device.device_name

    # Setting 'is_deleted' bit of device to 0 which means device is restored.
    if device.is_deleted == 1:
        device.is_deleted = 0
        device.save()
        # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
        try:
            device.site_instance.is_device_change = 1
            device.site_instance.save()
        except Exception as e:
            pass
        result['success'] = 1
        result['message'] = "Successfully restored device ({}).".format(device.device_alias)
    else:
        result['success'] = 0
        result['message'] = "Already restored."

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def update_states(request, option):
    """
    Updating states corresponding to the selected country.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request
        option (unicode): selected option value

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected country.
    country = Country.objects.get(pk=int(option))

    # States associated with selected country.
    states = country.state_set.all().order_by('state_name')

    out = ["<option value=''>Select State...</option>"]

    for state in states:
        out.append("<option value='%d'>%s</option>" % (state.id, state.state_name))

    dajax.assign('#id_state', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def update_cities(request, option):
    """
    Updating cities corresponding to the selected state.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected state.
    state = State.objects.get(pk=int(option))

    # Cities associated with selected state.
    cities = state.city_set.all().order_by('city_name')

    out = ["<option value=''>Select City...</option>"]

    for city in cities:
        out.append("<option value='%d'>%s</option>" % (city.id, city.city_name))

    dajax.assign('#id_city', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def update_states_after_invalid_form(request, option, state_id):
    """
    Updating states corresponding to the selected country after invalid form submission.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.
        state_id (int): State ID.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected country.
    country = Country.objects.get(pk=int(option))

    # States associated with selected country.
    states = country.state_set.all().order_by('state_name')

    out = ["<option value=''>Select State...</option>"]

    for state in states:
        if state.id == int(state_id):
            out.append("<option value='%d' selected='selected'>%s</option>" % (state.id, state.state_name))
        else:
            out.append("<option value='%d'>%s</option>" % (state.id, state.state_name))

    dajax.assign('#id_state', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def update_cities_after_invalid_form(request, option, city_id):
    """
    Updating cities corresponding to the selected state after invalid form submission.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (unicode): Selected option value.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    # Selected state.
    state = State.objects.get(pk=int(option))

    # Cities associated with the selected state.
    cities = state.city_set.all().order_by('city_name')

    out = ["<option value=''>Select City...</option>"]

    for city in cities:
        if city.id == int(city_id):
            out.append("<option value='%d' selected='selected'>%s</option>" % (city.id, city.city_name))
        else:
            out.append("<option value='%d'>%s</option>" % (city.id, city.city_name))

    dajax.assign('#id_city', 'innerHTML', ''.join(out))

    return dajax.json()


@dajaxice_register(method='GET')
def add_device_to_nms_core_form(request, device_id):
    """
    Generate form content for device addition to nms core.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_id (int): Device ID.

    Returns:
        result (dict): Dictionary of ping parameters associated with device type.
                       For e.g.,
                            {
                                "result": {
                                    "message": "Successfully fetched ping parameters from database.",
                                    "data": {
                                        "rta_critical": 3000,
                                        "packets": 60,
                                        "meta": "",
                                        "timeout": 20,
                                        "pl_critical": 100,
                                        "normal_check_interval": 5,
                                        "pl_warning": 80,
                                        "rta_warning": 1500,
                                        "device_id": 23
                                    },
                                    "success": 1
                                }
                            }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Failed to get device ping data."
    result['data']['meta'] = ''

    device = Device.objects.get(pk=device_id)

    try:
        device_type = DeviceType.objects.get(pk=device.device_type)
        # Get device ping information which is a ssociated which device type (if exist).
        ping_packets = device_type.packets if device_type.packets else settings.PING_PACKETS
        ping_timeout = device_type.timeout if device_type.timeout else settings.PING_TIMEOUT
        ping_normal_check_interval = device_type.normal_check_interval if device_type.normal_check_interval \
            else settings.PING_NORMAL_CHECK_INTERVAL
        ping_rta_warning = device_type.rta_warning if device_type.rta_warning else settings.PING_RTA_WARNING
        ping_rta_critical = device_type.rta_critical if device_type.rta_critical else settings.PING_RTA_CRITICAL
        ping_pl_warning = device_type.pl_warning if device_type.pl_warning else settings.PING_PL_WARNING
        ping_pl_critical = device_type.pl_critical if device_type.pl_critical else settings.PING_PL_CRITICAL
        result['message'] = "Successfully fetched ping parameters from database."
        result['success'] = 1
    except Exception as e:
        # If device type doesn't have ping parameters associated than use default ones.
        ping_packets = 60
        ping_timeout = 20
        ping_normal_check_interval = 5
        ping_rta_warning = 1500
        ping_rta_critical = 3000
        ping_pl_warning = 80
        ping_pl_critical = 100
        result['message'] = "Successfully get default ping parameters."
        result['success'] = 1
        logger.info(e.message)

    result['data']['device_id'] = device_id
    result['data']['packets'] = ping_packets
    result['data']['timeout'] = ping_timeout
    result['data']['normal_check_interval'] = ping_normal_check_interval
    result['data']['rta_warning'] = ping_rta_warning
    result['data']['rta_critical'] = ping_rta_critical
    result['data']['pl_warning'] = ping_pl_warning
    result['data']['pl_critical'] = ping_pl_critical

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def add_device_to_nms_core(request, device_id, ping_data):
    """
    Adding device to nms core.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_id (int): Device ID.

    Returns:
        result (dict): Dictionary of device info.
                       For e.g.,
                          {
                              'message': 'Deviceaddedsuccessfully.',
                              'data': {
                                  'site': u'nocout_gis_subordinate',
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

    ping_levels = {"rta": (ping_data['rta_warning'] if ping_data['rta_warning'] else 1500,
                           ping_data['rta_critical'] if ping_data['rta_critical'] else 3000),
                   "loss": (ping_data['pl_warning'] if ping_data['pl_warning'] else 80,
                            ping_data['pl_critical'] if ping_data['pl_critical'] else 100),
                   "packets": ping_data['packets'] if ping_data['packets'] and ping_data['packets'] <= 20 else 6,
                   "timeout": ping_data['timeout'] if ping_data['timeout'] else 20}

    if device.host_state != "Disable":
        # Get 'agent_tag' from DeviceType model.
        agent_tag = ""
        device_type_name = ""
        try:
            device_type_object = DeviceType.objects.get(id=device.device_type)
            agent_tag = device_type_object.agent_tag
            device_type_name = device_type_object.name
        except Exception as e:
            logger.info(e.message)

        device_data = {
            'device_name': str(device.device_name),
            'device_alias': str(device.device_alias),
            'ip_address': str(device.ip_address),
            'agent_tag': str(agent_tag),
            'site': str(device.site_instance.name),
            'mode': 'addhost',
            'ping_levels': ping_levels,
            'parent_device_name': None,
            'mac': str(device.mac_address),
            'device_type': device_type_name
        }

        device_tech = DeviceTechnology.objects.filter(id=device.device_technology)
        if len(device_tech) and device_tech[0].name.lower() in ['pmp', 'wimax']:
            if device.substation_set.exists():
                try:
                    substation = device.substation_set.get()

                    # Check for the circuit.
                    if substation.circuit_set.exists():
                        circuit = substation.circuit_set.get()
                        sector = circuit.sector
                        parent_device = sector.sector_configured_on
                        device_data.update({
                            'parent_device_name': parent_device.device_name
                        })
                    else:
                        result['message'] = "<i class=\"fa fa-check red-dot\"></i> \
                                             Could not find BS for this SS in the topology."
                        return json.dumps({'result': result})

                except Exception as e:
                    result['message'] = "<i class=\"fa fa-check red-dot\"></i> \
                                         Could not find BS for this SS in the topology."
                    logger.exception(e.message)
                    return json.dumps({'result': result})

        dpc = DevicePingConfiguration()
        dpc.device_name = device.device_name
        dpc.device_alias = device.device_alias
        dpc.packets = ping_data['packets']
        dpc.timeout = ping_data['timeout']
        dpc.normal_check_interval = ping_data['normal_check_interval']
        dpc.rta_warning = ping_data['rta_warning']
        dpc.rta_critical = ping_data['rta_critical']
        dpc.pl_warning = ping_data['pl_warning']
        dpc.pl_critical = ping_data['pl_critical']
        dpc.save()
        result['message'] = "<i class=\"fa fa-check green-dot\"></i> Device added successfully."
        # Set 'is_added_to_nms' to 1 after device successfully added to nocout nms core.
        device.is_added_to_nms = 1
        result['success'] = 1
        # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
        try:
            device.site_instance.is_device_change = 1
            device.site_instance.save()
        except Exception as e:
            pass
        device.save()
    else:
        result['message'] = "<i class=\"fa fa-check red-dot\"></i> Device state is disabled. \
                             First enable it than add it to nms core."
    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def edit_device_in_nms_core(request, device_id):
    """
    Editing device in nms core.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_id (int): Device ID.

    Returns:
        result (dict): Dictionary of device info.
                       For e.g,
                          {
                              'message': 'Deviceeditedsuccessfully.',
                              'data': {
                                  'site': u'nocout_gis_subordinate',
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
        # Get 'agent_tag' from DeviceType model.
        agent_tag = ""
        try:
            agent_tag = DeviceType.objects.get(id=device.device_type).agent_tag
        except Exception as e:
            logger.info(e.message)
        device_data = {
            'device_name': device.device_name,
            'device_alias': device.device_alias,
            'ip_address': device.ip_address,
            'agent_tag': agent_tag,
            'site': device.site_instance.name,
            'mode': 'edithost',
            'parent_device_name': None,
            'mac': device.mac_address
        }
        device_tech = DeviceTechnology.objects.filter(id=device.device_technology)

        if len(device_tech) and device_tech[0].name.lower() in ['pmp', 'wimax']:
            if device.substation_set.exists():
                try:
                    substation = device.substation_set.get()
                    # Check for the circuit.
                    if substation.circuit_set.exists():
                        circuit = substation.circuit_set.get()
                        sector = circuit.sector
                        parent_device = sector.sector_configured_on
                        device_data.update({
                            'parent_device_name': parent_device.device_name
                        })
                    else:
                        result['message'] = "<i class=\"fa fa-check red-dot\"></i> \
                                             Could not find BS for this SS in the topology."
                        return json.dumps({'result': result})
                except Exception as e:
                    result['message'] = "<i class=\"fa fa-check red-dot\"></i> \
                                         Could not find BS for this SS in the topology."
                    logger.exception(e.message)
                    return json.dumps({'result': result})

        result['message'] = "<i class=\"fa fa-check green-dot\"></i> Device edited successfully."
        # Set 'is_added_to_nms' to 1 after device successfully edited in nocout nms core.
        device.is_added_to_nms = 1
        device.save()
        result['success'] = 1

        # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
        try:
            device.site_instance.is_device_change = 1
            device.site_instance.save()
        except Exception as e:
            pass
    else:
        result['message'] = "<i class=\"fa fa-info text-info\"></i> Device state is disabled. \
                             First enable it than add it to nms core."
    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def delete_device_from_nms_core(request, device_id):
    """
    Delete device from nms core.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_id (int): Device ID.

    Returns:
        result (dict): Dictionary of device info.
                       For e.g,
                         {
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
        result['success'] = 1
        result['message'] = "Device disabled and deleted Successfully."

        # Set 'is_added_to_nms' to 1 after device successfully added to nocout nms core.
        device.is_added_to_nms = 0

        # Set 'is_monitored_on_nms' to 1 if service is added successfully.
        device.is_monitored_on_nms = 0

        # Set device state to 'Disable'.
        device.host_state = "Disable"
        device.save()

        # Remove device services from 'service_deviceserviceconfiguration' table.
        DeviceServiceConfiguration.objects.filter(device_name=device.device_name).delete()

        # Remove device ping service from 'service_devicepingconfiguration' table.
        DevicePingConfiguration.objects.filter(device_name=device.device_name).delete()

        # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
        try:
            device.site_instance.is_device_change = 1
            device.site_instance.save()
        except Exception as e:
            pass
    else:
        result['message'] = "<i class=\"fa fa-times red-dot\"></i> Device state is disabled. \
                             First enable it than add it to nms core."

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def modify_device_state(request, device_id):
    """
    Enable or disable device state.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_id (int): Device ID.

    Returns:
        result (dict): Dictionary of device info.
                       For e.g.,
                         {
                             'message': 'Device state modified successfully.',
                             'success': 1
                         }

    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Device state modifictaion failed."
    result['data']['meta'] = ''

    device = Device.objects.get(pk=device_id)

    if device:
        result['success'] = 1
        result['message'] = "Device state modified successfully."

        # Revert current device state.
        if device.host_state == "Enable":
            device.host_state = "Disable"
        else:
            device.host_state = "Enable"

        device.save()

        # Modify site instance 'is_device_change' bit to reflect change in corresponding site for sync.
        try:
            device.site_instance.is_device_change = 1
            device.site_instance.save()
        except Exception as e:
            pass
    else:
        result['message'] = "<i class=\"fa fa-times red-dot\"></i> Device state modification failed."

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def sync_device_with_nms_core(request):
    """
    Sync devices configuration to nms core.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_id (int): Device ID.

    Returns:
        result (dict): Dictionary of device info.
                    For e.g.,
                         {
                            'message': 'Configpushedtomysite,nocout_gis_subordinate',
                            'data': {
                                'mode': 'sync'
                            },
                            'success': 1
                         }

    Note:
        Sync status bits are as following:
        0 => Pending
        1 => Success
        2 => Failed
        3 => Deadlock Removal
        4 => Table(device_device_devicesynchistory) has no entry
    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Device activation for monitoring failed."
    result['data']['meta'] = ''

    timestamp = time.time()
    fulltime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S')

    # Get last status bit of 'DeviceSyncHistory'.
    try:
        last_sync_obj = DeviceSyncHistory.objects.latest('id')
        # Last sync status.
        last_syn_status = last_sync_obj.status
    except Exception as e:
        last_syn_status = 4
        logger.error("DeviceSyncHistory table has no entry.")

    # Sync status bits are as following:
    # 0 => Pending
    #     1 => Success
    #     2 => Failed
    #     3 => Deadlock Removal
    #     4 => Table(device_device_devicesynchistory) has no entry
    if last_syn_status in [1, 2, 3, 4]:
        # Current user's username.
        username = request.user.username
        # Create entry in 'device_devicesynchistory' table.
        device_sync_history = DeviceSyncHistory()
        device_sync_history.status = 0
        device_sync_history.description = "Sync run at {}.".format(fulltime)
        device_sync_history.sync_by = username
        device_sync_history.save()

        # Get 'device sync history' object.
        sync_obj_id = device_sync_history.id

        device_data = {
            'mode': 'sync',
            'sync_obj_id': sync_obj_id
        }

        # Site to which configuration needs to be pushed.
        main_site = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME'])

        # URL for nocout.py.
        url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(main_site.username,
                                                                main_site.password,
                                                                main_site.machine.machine_ip,
                                                                main_site.web_service_port,
                                                                main_site.name)

        # Sending post request to device app for syncing configuration to associated sites.
        r = requests.post(url, data=device_data)

        try:
            # Converting raw string 'r' into dictionary.
            response_dict = ast.literal_eval(r.text)
            if r:
                result['data'] = device_data
                result['success'] = 1
                result['message'] = response_dict['message'].capitalize()
        except Exception as e:
            device_sync_history.status = 2
            device_sync_history.description = "Sync failed to run at {}.".format(fulltime)
            device_sync_history.completed_on = datetime.now()
            device_sync_history.save()
            result['message'] = "Failed to sync device and services."
            logger.info(r.text)
    else:
        result['message'] = "Someone is already running sync."

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def remove_sync_deadlock(request):
    """
    Remove deadlock created in sync history table.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.

    Returns:
        result (dict): Dictionary of device info.
                       For e.g.,
                            {
                                "result": {
                                    "message": "Successfully removed sync deadlock.",
                                    "data": {
                                        "meta": ""
                                    },
                                    "success": 1
                                }
                            }
    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Deadlock removal for sync failed."
    result['data']['meta'] = ''

    # Get last id of 'DeviceSyncHistory'.
    try:
        # Get a formatted timestamp.
        timestamp = time.time()
        fulltime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S')
        # Updating last device sync history object.
        last_sync_obj = DeviceSyncHistory.objects.latest('id')
        # Modify status of last 'sync' to 3 i.e. 'Deadlock'.
        last_sync_obj.status = 3
        last_sync_obj.description = "Deadlock created during this sync, removed at {}.".format(fulltime)
        last_sync_obj.save()
        result['success'] = 1
        result['message'] = "Successfully removed sync deadlock."
    except Exception as e:
        logger.error("DeviceSyncHistory table has no entry. Exception: ", e.message)

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def edit_single_service_form(request, dsc_id):
    """
    Edit single service for a device from nms core.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        dsc_id (int): Device service configuration ID.

    Returns:
        result (dict): Dictionary of device service info.
                       For e.g.,
                            {
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


@dajaxice_register(method='GET')
def get_service_para_table(request, device_name, service_name, template_id=""):
    """
    Get service parameters and data source tables for service edit form.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_name (unicode): Device name.
        service_name (unicode): Service name.

    Kwargs:
        template_id (unicode): Template ID.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
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


@dajaxice_register(method='GET')
def edit_single_service(request, dsc_id, svc_temp_id, data_sources):
    """
    Edit single service corresponding to a device.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        dsc_id (unicode): Device service configuration ID.
        svc_temp_id (unicode): Service template ID.
        data_sources (list): List of data sources dictionaries.
                             For e.g.,
                                [
                                    {
                                        'data_source': u'rssi',
                                        'warning': u'-50',
                                        'critical': u'-85'
                                    }
                                ]

    Returns:
        result (dict): Dictionary containing service information.
                       For e.g.,
                            {
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

    # Device service configuration object.
    dsc = ""
    try:
        dsc = DeviceServiceConfiguration.objects.get(id=dsc_id)
        try:
            # Payload data for post request.
            service_data = result['data']['objects']
            service_para = ServiceParameters.objects.get(pk=svc_temp_id)
            service_data['mode'] = "editservice"
            service_data['device_name'] = str(dsc.device_name)
            service_data['service_name'] = str(dsc.service_name)
            service_data['serv_params'] = {}
            service_data['serv_params']['normal_check_interval'] = int(service_para.normal_check_interval)
            service_data['serv_params']['retry_check_interval'] = int(service_para.retry_check_interval)
            service_data['serv_params']['max_check_attempts'] = int(service_para.max_check_attempts)
            service_data['snmp_community'] = {}
            service_data['snmp_community']['version'] = str(service_para.protocol.version)
            service_data['snmp_community']['read_community'] = str(service_para.protocol.read_community)
            service_data['cmd_params'] = {}

            # Looping through data sources add them to 'cmd_params' dictionary.
            for sds in data_sources:
                service_data['cmd_params'][str(sds['data_source'])] = {'warning': str(sds['warning']),
                                                                       'critical': str(sds['critical'])}

            service_data['snmp_port'] = str(dsc.port)
            service_data['agent_tag'] = str(dsc.agent_tag) if eval(dsc.agent_tag) is not None else "snmp"

            # Main site on which service needs to be added.
            main_site = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME'])
            # URL for nocout.py.
            url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(main_site.username,
                                                                    main_site.password,
                                                                    main_site.machine.machine_ip,
                                                                    main_site.web_service_port,
                                                                    main_site.name)
            # Encode payload data.
            encoded_data = urllib.urlencode(service_data)

            # Sending post request to nocout device app to add service.
            r = requests.post(url, data=encoded_data)

            # Converting post response data into python dictionary.
            response_dict = ast.literal_eval(r.text)

            # If response(r) is given by post request than process it further to get success/failure messages.
            if r:
                result['data'] = service_data
                result['success'] = 1

                # If response_dict doesn't have key 'success'.
                if not response_dict.get('success'):
                    logger.info(response_dict.get('error_message'))
                    result['message'] += "<i class=\"fa fa-times red-dot\"></i>\
                                          Failed to updated service '%s'. <br />" % dsc.service_name
                else:
                    result[
                        'message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                       Successfully updated service '%s'. <br />" % dsc.service_name

                    # Saving service to 'service_deviceserviceconfiguration' table.
                    try:
                        # If service exist in 'service_deviceserviceconfiguration' table then update it.
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


@dajaxice_register(method='GET')
def delete_single_service_form(request, dsc_id):
    """
    Get parameters for single service deletion form.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        dsc_id (int): Device service configuration object ID.

    Returns:
        result (dict): Dictionary containing service information.
                       For e.g.,
                            {
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
    # Device service configuration object.
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
            # Fetch data sources from 'DeviceServiceConfiguration' model.
            dsc_for_data_sources = DeviceServiceConfiguration.objects.filter(device_name=dsc.device_name,
                                                                             service_name=dsc.service_name)
            for dsc_for_data_source in dsc_for_data_sources:
                service_data['data_sources'].append(dsc_for_data_source.data_source)
        except Exception as e:
            logger.info(e)
    except Exception as e:
        logger.info(e)

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def delete_single_service(request, device_name, service_name):
    """
    Delete service corresponding to the device.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_name (unicode): Device name.
        service_name (unicode): Service name.

    Returns:
        result (dict): Dictionary containing service information.
                       For e.g.,
                            {
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

        main_site = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME'])
        # URL for nocout.py.
        url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(main_site.username,
                                                                main_site.password,
                                                                main_site.machine.machine_ip,
                                                                main_site.web_service_port,
                                                                main_site.name)

        # Encode service payload data.
        encoded_data = urllib.urlencode(service_data)

        # Sending post request to nocout device app to add a service.
        r = requests.post(url, data=encoded_data)

        # Converting post response data into python dictionary.
        response_dict = ast.literal_eval(r.text)

        # If response(r) is given by post request than process it further to get success/failure messages.
        if r:
            result['data'] = service_data
            result['success'] = 1

            # If response dictionary doesn't have key 'success'.
            if not response_dict.get('success'):
                logger.info(response_dict.get('error_message'))
                result['message'] += "<i class=\"fa fa-times red-dot\"></i>\
                                      Failed to delete service '%s'. <br />" % service_name
            else:
                result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                      Successfully updated service '%s'. <br />" % service_name

            # Delete service rows form 'service_deviceserviceconfiguration' table.
            DeviceServiceConfiguration.objects.filter(device_name=device_name, service_name=service_name).delete()
    except Exception as e:
        result['message'] += e.message

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def edit_service_form(request, value):
    """
    Get parameters for service edit form.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        value (int): Device ID.

    Returns:
        result (dict): Dictionary containing service information.
                       For e.g,
                            {
                                'message': 'Successfully render form.',
                                'data': {
                                    'meta': '',
                                    'objects': {
                                        'main_site': u'main_UA',
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
    result['data']['objects']['main_site'] = ""
    result['data']['objects']['is_added'] = device.is_added_to_nms

    # Get device type.
    device_type = None
    try:
        device_type = DeviceType.objects.get(id=device.device_type)
    except Exception as e:
        pass

    # Get all services associated with the devic type.
    dt_services = None
    try:
        dt_services = device_type.service.all()
    except Exception as e:
        pass

    # Get deleted services.
    del_svc = list()
    try:
        del_svc = list(set(DeviceServiceConfiguration.objects.filter(
            device_name=device.device_name, operation="d").values_list('service_name', flat=True)))
    except Exception as e:
        pass

    # Get monitored services except in deletion queue.
    editable_svc = dt_services.exclude(name__in=del_svc)

    # Get services associated with device.
    try:
        try:
            main_site_name = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME']).name
            result['data']['objects']['main_site'] = main_site_name
        except Exception as e:
            logger.info("Main site doesn't exist.")

        if device.is_added_to_nms == 1:
            result['data']['objects']['services'] = []
            for svc in editable_svc:
                service = Service.objects.get(name=svc)
                svc_dict = dict()
                svc_dict['key'] = service.id
                svc_dict['value'] = service.alias
                result['data']['objects']['services'].append(svc_dict)
        else:
            result['message'] = "First add device in nms core."
    except Exception as e:
        logger.info("No service to monitor.")

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def get_old_configuration_for_svc_edit(request, option="", service_id="", device_id=""):
    """
    Show currently present information of service in schema.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (int): Checkbox value.
        service_id (unicode): Service ID.
        device_id (unicode): Device ID.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    params = []
    svc_templates = []

    show_old_configuration = "#show_old_configuration_{0}".format(option)
    template_options_id = "#template_options_id_{0}".format(option)

    # Get device.
    device = None
    try:
        device = Device.objects.get(pk=device_id)
    except Exception as e:
        pass

    # Get service.
    service = None
    try:
        service = Service.objects.get(pk=service_id)
    except Exception as e:
        pass

    # Get service template.
    svc_template = None
    try:
        svc_template = service.parameters
    except Exception as e:
        pass

    # Get service data sources.
    svc_data_sources = None
    try:
        svc_data_sources = service.service_data_sources.all()
    except Exception as e:
        pass

    if option and option != "":
        svc_params = ServiceParameters.objects.all()
        if svc_params:
            try:
                if svc_params:
                    # Get device service configuration.
                    dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                                    service_name=service.name).exclude(operation="d")

                    if dsc:
                        svc_template = dsc[0]
                        svc_data_sources = dsc

                    params.append("<br />")
                    params.append("<h5 class='text-primary'><b>Current configuration:</b></h5>")
                    params.append("<div class=''>\
                                   <div class='box border primary'>\
                                   <div class='box-title'>\
                                        <h4><i class='fa fa-table'></i>Current Service Parameters</h4>\
                                   </div>")
                    params.append("<div class='box-body'><table class='table'>")
                    params.append("<thead><tr>\
                                        <th>Normal Check Interval</th>\
                                        <th>Retry Check Interval</th>\
                                        <th>Max Check Attemps</th>\
                                   </tr></thead>")
                    params.append("<tbody><tr><td>%d</td><td>%d</td><td>%d</td></tr>" % (
                        svc_template.normal_check_interval,
                        svc_template.retry_check_interval,
                        svc_template.max_check_attempts))
                    params.append("</tbody>")

                    # Set show templates or not bit.
                    show_svc_templates = True

                    if svc_data_sources:
                        params.append(
                            "<thead><tr><th>DS Name</th><th>Warning</th><th>Critical</th></tr></thead><tbody>")
                        for sds in svc_data_sources:
                            if dsc:
                                data_source = sds.data_source
                            else:
                                data_source = sds.name
                            try:
                                params.append("<tr><td class='ds_name'>{}</td><td class='ds_warning'>{}</td>\
                                               <td class='ds_critical'>{}</td></tr>"
                                              .format(data_source if data_source else "",
                                                      int(sds.warning) if sds.warning else "",
                                                      int(sds.critical) if sds.critical else ""))
                            except Exception as e:
                                params.append("<tr><td class='ds_name'>{}</td><td class='ds_warning'>{}</td>\
                                               <td class='ds_critical'>{}</td></tr>"
                                              .format(data_source if data_source else "",
                                                      sds.warning if sds.warning else "",
                                                      sds.critical if sds.critical else ""))
                                show_svc_templates = False
                        params.append("</tbody></table></div></div></div>")

                        if show_svc_templates:
                            svc_templates.append("<p class='text-danger'><b>Select service template:</b></p> ")
                            svc_templates.append("<select class='form-control' id='service_template_%d'>" % option)
                            svc_templates.append("<option value='' selected>Select</option>")
                            for svc_param in svc_params:
                                svc_templates.append("<option value='%d'>%s</option>" % (svc_param.id,
                                                                                         svc_param.parameter_description))
                            svc_templates.append("</select>")
                        else:
                            svc_templates.append("<p class='text-danger' align='center'><b>\
                                                  Data source parameters are not editable.</b></p> ")
                else:
                    params.append("<h5 class='text-warning'>No data source associated.</h5> ")
            except Exception as e:
                logger.info("No data source available.")
    else:
        params.append("<h5 class='text-warning'>No data source associated.</h5> ")

    dajax.assign(show_old_configuration, 'innerHTML', ''.join(params))
    dajax.assign(template_options_id, 'innerHTML', ''.join(svc_templates))

    return dajax.json()


@dajaxice_register(method='GET')
def get_new_configuration_for_svc_edit(request, service_id="", template_id=""):
    """
    Show modified information of the service.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        service_id (int): Service ID.
        template_id (unicode): Template ID.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    field_id = "#show_new_configuration_{0}".format(service_id)
    params = []

    # Get service.
    service = None
    try:
        service = Service.objects.get(id=service_id)
    except Exception as e:
        pass

    # Get template.
    template = None
    try:
        template = ServiceParameters.objects.get(pk=template_id)
    except Exception as e:
        pass

    # Get data sources.
    data_sources = None
    try:
        data_sources = service.service_data_sources.all()
    except Exception as e:
        pass

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


@dajaxice_register(method='GET')
def get_ping_configuration_for_svc_edit(request, device_id):
    """
    Get ping configuration for the service.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_id (int): Device ID.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()
    params = []

    # Get device.
    device = Device.objects.get(pk=device_id)
    try:
        # Get device ping configuration object.
        dpc = DevicePingConfiguration.objects.get(device_name=device.device_name)
        packets = dpc.packets
        timeout = dpc.timeout
        normal_check_interval = dpc.normal_check_interval
        rta_warning = dpc.rta_warning
        rta_critical = dpc.rta_critical
        pl_warning = dpc.pl_warning
        pl_critical = dpc.pl_critical
    except Exception as e:
        # If there are no ping parmeters for this device in 'service_devicepingconfiguration'
        # then get default ping parameters from 'settings.py".
        packets = settings.PING_PACKETS
        timeout = settings.PING_TIMEOUT
        normal_check_interval = settings.PING_NORMAL_CHECK_INTERVAL
        rta_warning = settings.PING_RTA_WARNING
        rta_critical = settings.PING_RTA_CRITICAL
        pl_warning = settings.PING_PL_WARNING
        pl_critical = settings.PING_PL_CRITICAL
        logger.info(e.message)

    # Generating html content for ping parameters table.
    params.append('<br />')
    params.append('<h5 class="text-danger"><b>Ping configuration:</b></h5>')
    params.append('<div class=""><div class="box border red"><div class="box-title"><h4>\
                   <i class="fa fa-table"></i>Ping Parameters:</h4></div>')
    params.append('<div class="box-body"><table class="table">')
    params.append('<thead><tr><th>Packets</th><th>Timeout</th><th>Normal Check Interval</th></tr></thead>')
    params.append('<tbody>')
    params.append('<tr>')
    params.append('<td contenteditable="true" id="packets">{}</td>'.format(packets))
    params.append('<td contenteditable="true" id="timeout">{}</td>'.format(timeout))
    params.append('<td contenteditable="true" id="normal_check_interval">{}</td>'.format(normal_check_interval))
    params.append('</tr>')
    params.append('</tbody>')
    params.append('<thead><tr><th>Data Source</th><th>Warning</th><th>Critical</th></tr></thead>')
    params.append('<tbody>')
    params.append('<tr><td>RTA</td><td contenteditable="true" id="rta_warning">{}</td>\
                   <td contenteditable="true" id="rta_critical">{}</td></tr>'.format(rta_warning, rta_critical))
    params.append('<tr><td>PL</td><td contenteditable="true" id="pl_warning">{}</td>\
                   <td contenteditable="true" id="pl_critical">{}</td></tr>'.format(pl_warning, pl_critical))
    params.append('</tbody>')
    params.append('</table>')
    params.append('</div></div></div>')

    dajax.assign("#ping_svc", 'innerHTML', ''.join(params))

    return dajax.json()


@dajaxice_register(method='GET')
def edit_services(request, svc_data, svc_ping=None, device_id=""):
    """
    Edit services corresponding to the device.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        svc_data (list): List of dictionaries containing service data.
                         For e.g.,
                            [
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

        svc_ping (dict): Dictionary containing ping data.
                         For e.g.,
                             {
                                'rta_critical': 3000,
                                'packets': 60,
                                'timeout': 20,
                                'pl_critical': 100,
                                'normal_check_interval': 5,
                                'pl_warning': 80,
                                'rta_warning': 1500
                            }

        device_id (int): 11343

    Returns:
        result (dict): Dictionary containing service information.
                       For e.g.,
                            {
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

    # Collects messages returned from service addition api.
    messages = ""

    # Get device.
    device = None
    try:
        device = Device.objects.get(id=device_id)
    except Exception as e:
        pass

    # Edit 'ping' service.
    try:
        if device and svc_ping:
            device_name = device.device_name

            # Get device ping configuration object.
            dpc = ""
            try:
                dpc = DevicePingConfiguration.objects.get(device_name=device_name)
            except Exception as e:
                logger.info(e.message)

            if dpc:
                try:
                    # Device ping configuration.
                    dpc.device_name = device_name
                    dpc.device_alias = device.device_alias
                    dpc.packets = svc_ping['packets']
                    dpc.timeout = svc_ping['timeout']
                    dpc.normal_check_interval = svc_ping['normal_check_interval']
                    dpc.rta_warning = svc_ping['rta_warning']
                    dpc.rta_critical = svc_ping['rta_critical']
                    dpc.pl_warning = svc_ping['pl_warning']
                    dpc.pl_critical = svc_ping['pl_critical']
                    dpc.operation = "e"
                    dpc.save()

                    # Set site instance bit corresponding to the device.
                    device.site_instance.is_device_change = 1
                    device.site_instance.save()

                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                           Successfully edited service 'ping'. <br />"
                    messages += result['message']
                except Exception as e:
                    result['message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to edit service ping. <br />"
                    messages += result['message']
            else:
                # Device ping configuration.
                try:
                    dpc = DevicePingConfiguration()
                    dpc.device_name = device_name
                    dpc.device_alias = device.device_alias
                    dpc.packets = svc_ping['packets']
                    dpc.timeout = svc_ping['timeout']
                    dpc.normal_check_interval = svc_ping['normal_check_interval']
                    dpc.rta_warning = svc_ping['rta_warning']
                    dpc.rta_critical = svc_ping['rta_critical']
                    dpc.pl_warning = svc_ping['pl_warning']
                    dpc.pl_critical = svc_ping['pl_critical']
                    dpc.operation = "c"
                    dpc.save()

                    # Set site instance bit corresponding to the device.
                    device.site_instance.is_device_change = 1
                    device.site_instance.save()

                    result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                           Successfully created service 'ping'. <br />"
                    messages += result['message']
                except Exception as e:
                    result['message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to create service ping. <br />"
                    messages += result['message']
    except Exception as e:
        logger.info(e.message)
        result['message'] += "<i class=\"fa fa-times red-dot\"></i>Failed to edit/create service 'ping'. <br />"
        messages += result['message']

    # Edit other services.
    for sd in svc_data:
        result = dict()
        result['data'] = {}
        result['success'] = 0
        result['message'] = ""

        # Get service.
        service = None
        try:
            service = Service.objects.get(pk=int(sd['service_id']))
        except Exception as e:
            pass

        # Get service parameters.
        service_para = service.parameters
        try:
            service_para = ServiceParameters.objects.get(pk=int(sd['template_id']))
        except Exception as e:
            logger.info(e)

        try:
            for sds in sd['data_source']:
                if sds['warning'] != "":
                    try:
                        # If service exist in 'service_deviceserviceconfiguration' table
                        # then update service, else create it.
                        for data_source in sd['data_source']:
                            dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                                            service_name=service.name,
                                                                            data_source=data_source['name'])
                            if dsc:
                                dsc = dsc[0]
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
                                dsc.operation = "e"
                                dsc.save()

                                # Set site instance bit corresponding to the device.
                                device.site_instance.is_device_change = 1
                                device.site_instance.save()

                                # Set 'is_monitored_on_nms' to 1 if service is added successfully.
                                device.is_monitored_on_nms = 1
                                device.save()

                                result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                                       Successfully edited service '%s'. <br />" % service.name
                                messages += result['message']
                            else:
                                dsc = DeviceServiceConfiguration()
                                dsc.device_name = device.device_name
                                dsc.service_name = service.name
                                dsc.data_source = data_source['name']
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
                                dsc.operation = "c"
                                dsc.save()

                                # Set site instance bit corresponding to the device.
                                device.site_instance.is_device_change = 1
                                device.site_instance.save()

                                # Set 'is_monitored_on_nms' to 1 if service is added successfully.
                                device.is_monitored_on_nms = 1
                                device.save()

                                result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                                       Successfully created service '%s'. <br />" % service.name
                                messages += result['message']

                    except Exception as e:
                        logger.exception(e)
                else:
                    # Save service to 'service_deviceserviceconfiguration' table.
                    try:
                        # If service exist in 'service_deviceserviceconfiguration' table
                        # then update service, else create it.
                        for data_source in sd['data_source']:
                            dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                                            service_name=service.name,
                                                                            data_source=data_source['name'])
                            if dsc:
                                dsc = dsc[0]
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
                                dsc.operation = "e"
                                dsc.save()

                                # Set site instance bit corresponding to the device.
                                device.site_instance.is_device_change = 1
                                device.site_instance.save()

                                # Set 'is_monitored_on_nms' to 1 if service is added successfully.
                                device.is_monitored_on_nms = 1
                                device.save()

                                result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                                       Successfully edited service '%s'. <br />" % service.name
                                messages += result['message']
                            else:
                                dsc = DeviceServiceConfiguration()
                                dsc.device_name = device.device_name
                                dsc.service_name = service.name
                                dsc.data_source = data_source['name']
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
                                dsc.operation = "c"
                                dsc.save()

                                # Set 'is_monitored_on_nms' to 1 if service is added successfully.
                                device.is_monitored_on_nms = 1
                                device.save()

                                # Set site instance bit corresponding to the device.
                                device.site_instance.is_device_change = 1
                                device.site_instance.save()

                                result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                                       Successfully created service '%s'. <br />" % service.name
                                messages += result['message']
                    except Exception as e:
                        logger.exception(e)
        except Exception as e:
            logger.exception(e)
            result['message'] += "<i class=\"fa fa-times red-dot\"></i>\
                                   Failed to edit service '%s'. <br />" % service.name
            messages += result['message']

    # Assign messages to result dict message key.
    if messages:
        result['message'] = messages
    else:
        result['message'] = "No template is selected for any service"

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def delete_service_form(request, value):
    """
    Get parameters for service deletion form.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        value (int): Device ID.

    Returns:
        result (dict): Dictionary containing services information.
                       For e.g.,
                            {
                                'message': 'Successfully render form.',
                                'data': {
                                    'meta': '',
                                    'objects': {
                                        'main_site': u'main_UA',
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
    # Device to which services are associated.
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
    result['data']['objects']['main_site'] = ""
    result['data']['objects']['is_added'] = device.is_added_to_nms

    # Get device type.
    device_type = DeviceType.objects.get(id=device.device_type)

    # Get all services associated with the device type.
    dt_services = device_type.service.all()

    # Get services associated with the device.
    try:
        try:
            main_site_name = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME']).name
            result['data']['objects']['main_site'] = main_site_name
        except Exception as e:
            logger.info("Main site doesn't exist.")
        if device.is_added_to_nms == 1:
            # Fetching all services those were already deleted from 'service device configuration' table.
            dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name, operation='d')

            # Services those are already running for this device.
            services = []
            for svc in dsc:
                services.append(svc.service_name)

            # Extracting unique set of services from 'services' list.
            monitored_services = dt_services.exclude(name__in=list((set(services))))

            result['data']['objects']['services'] = []

            for svc in monitored_services:
                svc_dict = dict()
                svc_dict['key'] = svc.id
                svc_dict['value'] = svc.alias
                result['data']['objects']['services'].append(svc_dict)
        else:
            result['message'] = "First add device in nms core."
    except Exception as e:
        logger.info("No service to monitor.")
        logger.info(e.message)

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def delete_services(request, device_id, service_data):
    """
    Delete services corresponding to the device.

    Args:
        device_id (int): Device ID.
        service_data (list): List containing service data.
                             For e.g.,
                                 [u'54', u'55', u'56']

    Returns:
        result (dict):  Dictionary containing service information.
                        For e.g.,
                            {
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

    # Get device.
    device = None
    try:
        device = Device.objects.get(id=device_id)
    except Exception as e:
        pass

    # Get agent tag.
    agent_tag = "snmp"
    try:
        agent_tag = DeviceType.objects.get(id=device.device_type).agent_tag
    except Exception as e:
        pass

    # Collects messages returned from service addition api.
    messages = ""

    for svc_id in service_data:
        result['message'] = ""

        try:
            # Get service.
            service = Service.objects.get(pk=svc_id)

            # Delete services corresponding to the device.
            result['success'] = 1

            # If response dict doesn't have key 'success'.
            if device:
                # Create entry in 'device service configuration'.
                dsc = DeviceServiceConfiguration()
                dsc.device_name = device.device_name
                dsc.service_name = service.name
                dsc.agent_tag = agent_tag
                dsc.operation = "d"
                dsc.save()

                # Delete service rows from 'service_deviceserviceconfiguration' table.
                DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                          service_name=service.name,
                                                          operation__in=["c", "e"]).delete()

                result['message'] += "<i class=\"fa fa-check green-dot\"></i>\
                                      Successfully deleted service '%s'. <br />" % service.name
                messages += result['message']
            else:
                result['message'] += "<i class=\"fa fa-times red-dot\"></i>\
                                      Failed to delete service '%s'. <br />" % service.name
                messages += result['message']
        except Exception as e:
            result['message'] += e.message

    result['message'] = messages

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def add_service_form(request, value):
    """
    Show form for adding services corresponding to the device.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        value (int): Device ID.

    Returns:
        result (dict): Dictionary containing services information.
                       For e.g.,
                            {
                                'message': 'Successfully render form.',
                                'data': {
                                    'meta': '',
                                    'objects': {
                                        'main_site': u'main_UA',
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
    # Device to which services are associated.
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
    result['data']['objects']['main_site'] = ""
    result['data']['objects']['is_added'] = device.is_added_to_nms

    # Get services associated with device.
    try:
        try:
            main_site_name = SiteInstance.objects.get(name=settings.DEVICE_APPLICATION['default']['NAME']).name
            result['data']['objects']['main_site'] = main_site_name
        except Exception as e:
            logger.info(e.message)

        if device.is_added_to_nms == 1:
            # Fetching all services from 'service device configuration' table.
            deleted_services = DeviceServiceConfiguration.objects.filter(device_name=device.device_name,
                                                                         operation="d").values_list('service_name',
                                                                                                    flat=True)

            # Filter duplicate service entries from 'deleted_services' list.
            deleted_services = list(set(deleted_services))

            # Get services those can be added (i.e. services already deleted).
            services = Service.objects.filter(name__in=deleted_services)

            result['data']['objects']['services'] = []

            for svc in services:
                svc_dict = dict()
                svc_dict['key'] = svc.id
                svc_dict['value'] = svc.alias
                result['data']['objects']['services'].append(svc_dict)
        else:
            result['message'] = "First add device in nms core."
    except Exception as e:
        logger.info("No service to monitor.")
        logger.info(e.message)

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def get_old_configuration_for_svc_add(request, option="", service_id="", device_id=""):
    """
    Show current information of service present in schema.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        option (int): Checkbox value.
        service_id (unicode): Service ID.
        device_id (unicode): Device ID.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
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
                    params.append("<br />")
                    svc_templates.append("<p class='text-green'><b>Select service template:</b></p> ")
                    svc_templates.append("<select class='form-control' id='service_template_%d'>" % option)
                    svc_templates.append("<option value='' selected>Select</option>")
                    for svc_param in svc_params:
                        svc_templates.append("<option value='%d'>%s</option>" % (svc_param.id,
                                                                                 svc_param.parameter_description))
                    svc_templates.append("</select>")
                else:
                    params.append("<h5 class='text-green'>No data source associated.</h5> ")
            except Exception as e:
                logger.info("No data source available.")
                logger.info(e.message)
    else:
        params.append("<h5 class='text-green'>No data source associated.</h5> ")

    dajax.assign(template_options_id, 'innerHTML', ''.join(svc_templates))

    return dajax.json()


@dajaxice_register(method='GET')
def get_new_configuration_for_svc_add(request, service_id="", template_id=""):
    """
    Show modified information of service.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        service_id (int): Service ID.
        template_id (unicode): Template ID.

    Returns:
        dajax (str): String containing list of dictionaries.
                     For e.g.,
                     [
                         {
                             "cmd": "as",
                             "id": "#name_id",
                             "val": "<option value='' selected>Select</option><option value='2'>Name</option>",
                             "prop": "innerHTML"
                         }
                     ]
    """
    dajax = Dajax()

    field_id = "#show_new_configuration_{0}".format(service_id)
    params = []
    service = Service.objects.get(pk=service_id)
    template = ServiceParameters.objects.get(pk=template_id)
    params.append("<br />")
    params.append("<h5 class='text-green'><b>Selected configuration:</b></h5>")
    params.append("<div class=''>\
                   <div class='box border green'>\
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

    # Data sources associated with the service.
    data_sources = service.service_data_sources.all()

    for sds in data_sources:
        try:
            params.append("<tr class='data_source_field'><td class='ds_name'>{}</td>\
                           <td contenteditable='true' class='ds_warning'>{}</td>\
                           <td contenteditable='true' class='ds_critical'>{}</td></tr>"
                          .format(sds.name if sds.name else "",
                                  int(sds.warning) if sds.warning else "",
                                  int(sds.critical) if sds.critical else ""))
        except Exception as e:
            params.append("<tr class='data_source_field'><td class='ds_name'>{}</td>\
                           <td contenteditable='false' title='Non editable.' class='ds_warning'>{}</td>\
                           <td contenteditable='false' title='Non editable.' class='ds_critical'>{}</td></tr>"
                          .format(sds.name if sds.name else "",
                                  sds.warning if sds.warning else "",
                                  sds.critical if sds.critical else ""))

    params.append("</tbody></table></div></div></div>")

    dajax.assign(field_id, 'innerHTML', ''.join(params))

    return dajax.json()


@dajaxice_register(method='GET')
def add_services(request, device_id, svc_data):
    """
    Adding services corresponding to the device.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        svc_data (list): List of dictionaries containing service data.
                         For e.g.,
                                [
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
        result (dict): Dictionary containing services information.
                       For e.g.,
                            {
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

    # Get device.
    device = None
    try:
        device = Device.objects.get(id=device_id)
    except Exception as e:
        pass

    # Get device name.
    device_name = ""
    if device:
        device_name = device.device_name

    # Collects messages returned from service addition api.
    messages = ""

    for sd in svc_data:
        # Reset message value.
        result['message'] = ""

        try:
            service = Service.objects.get(pk=int(sd['service_id']))

            # If service template is not selected than default will be considered.
            try:
                service_para = ServiceParameters.objects.get(pk=int(sd['template_id']))
            except Exception as e:
                service_para = service.parameters
                logger.info(e.message)

            # List of data sources.
            data_sources = []
            try:
                if 'data_source' in sd:
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

            result['success'] = 1

            try:
                # Delete entry corresponding to this service with operation 'd'.
                # Because we can only add services those were already deleted
                # and which has operation bit set to 'd' (for deleted).
                DeviceServiceConfiguration.objects.filter(device_name=device_name,
                                                          service_name=service.name,
                                                          operation="d").delete()

                # Add service in 'service_deviceserviceconfiguration' table.
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
                    dsc.operation = "c"
                    dsc.is_added = 0
                    dsc.save()

                    result['message'] += "<i class=\"fa fa-check green-dot\"></i> \
                                           Successfully added service '%s'. <br />" % service.name

                    messages += result['message']
            except Exception as e:
                result['message'] += "<i class=\"fa fa-check green-dot\"></i> \
                                       Failed to add service '%s'. <br />" % service.name
                messages += result['message']

            # Set 'is_monitored_on_nms' to 1 if service is added successfully.
            device.is_monitored_on_nms = 1
            device.save()

            # Set site instance bit corresponding to the device.
            device.site_instance.is_device_change = 1
            device.site_instance.save()
        except Exception as e:
            logger.info(e)
            result['message'] += "<i class=\"fa fa-times red-dot\"></i> Something wrong with the form data. <br />"
            messages += result['message']

    # Assign messages to result dict message key.
    result['message'] = messages

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def device_services_status(request, device_id):
    """
    Show current configuration/status of services corresponding to the device.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.
        device_id (int): Device ID.

    Returns:
        result (dict): Dictionary of device and associated services information.
                       For e.g.,
                            {
                                'message': '',
                                'data': {
                                    'meta': {

                                    },
                                    'objects': {
                                        'site_instance': 'nocout_gis_subordinate',
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

    # Get device.
    device = Device.objects.get(pk=device_id)

    # Fetching all services from 'service device configuration' table.
    dsc = DeviceServiceConfiguration.objects.filter(device_name=device.device_name)

    # Get device type.
    device_type = DeviceType.objects.get(id=device.device_type)

    # Get deleted services.
    deleted_services_list = dsc.filter(operation="d").values_list("service_name", flat=True)
    deleted_services = Service.objects.filter(name__in=list(set(deleted_services_list)))

    # Get active services.
    active_services = device_type.service.all().exclude(name__in=deleted_services_list)

    result['data']['objects']['device_name'] = str(device.device_alias)
    result['data']['objects']['machine'] = str(device.machine)
    result['data']['objects']['site_instance'] = str(device.site_instance)
    result['data']['objects']['ip_address'] = str(device.ip_address)
    result['data']['objects']['device_type'] = str(DeviceType.objects.get(pk=device.device_type))
    result['data']['objects']['active_services'] = []
    result['data']['objects']['inactive_services'] = []

    for svc in active_services:
        temp_svc = dict()
        temp_svc['service'] = svc.alias
        temp_svc['data_sources'] = ""
        for ds in svc.service_data_sources.all():
            temp_svc['data_sources'] += "{}, ".format(ds.alias)
        result['data']['objects']['active_services'].append(temp_svc)

    for svc in deleted_services:
        temp_svc = dict()
        temp_svc['service'] = svc.alias
        temp_svc['data_sources'] = ""
        for ds in svc.service_data_sources.all():
            temp_svc['data_sources'] += "{}, ".format(ds.alias)
        result['data']['objects']['inactive_services'].append(temp_svc)

    return json.dumps({'result': result})


@dajaxice_register(method='GET')
def reset_service_configuration(request):
    """ Reset device service configuration

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request.

    Returns:
        result (dict): Dictionary containing device information.
                       For e.g.,
                            {
                                "message": "Failed to render form correctly.",
                                "data": {
                                    "meta": "",
                                    "objects": {
                                        "main_site": "main_UA",
                                        "device_alias": "1131208803",
                                        "is_added": 1,
                                        "services": [
                                            {
                                                "value": "downlink cinr",
                                                "key": 54
                                            },
                                            {
                                                "value": "uplink cinr",
                                                "key": 55
                                            },
                                            {
                                                "value": "downlink intrf",
                                                "key": 56
                                            },
                                            {
                                                "value": "uplink intrf",
                                                "key": 57
                                            },
                                            {
                                                "value": "uplink rssi",
                                                "key": 59
                                            },
                                            {
                                                "value": "dl_modulation_change",
                                                "key": 60
                                            },
                                            {
                                                "value": "modulation_dl_fec",
                                                "key": 61
                                            },
                                            {
                                                "value": "modulation_ul_fec",
                                                "key": 62
                                            },
                                            {
                                                "value": "ss_autonegotiation_status",
                                                "key": 63
                                            },
                                            {
                                                "value": "ss_dl_utilization",
                                                "key": 64
                                            },
                                            {
                                                "value": "ss_ul_utilization",
                                                "key": 65
                                            },
                                            {
                                                "value": "ss_duplex_status",
                                                "key": 66
                                            },
                                            {
                                                "value": "ss_errors_status",
                                                "key": 67
                                            },
                                            {
                                                "value": "ss_frequency",
                                                "key": 68
                                            },
                                            {
                                                "value": "ss_ip",
                                                "key": 69
                                            },
                                            {
                                                "value": "ss_link_status",
                                                "key": 70
                                            },
                                            {
                                                "value": "ss_ptx_invent",
                                                "key": 72
                                            },
                                            {
                                                "value": "ss_mac",
                                                "key": 71
                                            },
                                            {
                                                "value": "ss_sector_id",
                                                "key": 73
                                            },
                                            {
                                                "value": "downlink rssi",
                                                "key": 58
                                            },
                                            {
                                                "value": "wimax_qos_invent",
                                                "key": 108
                                            },
                                            {
                                                "value": "ss_session_uptime",
                                                "key": 74
                                            },
                                            {
                                                "value": "SS Uptime",
                                                "key": 76
                                            },
                                            {
                                                "value": "ss_speed_status",
                                                "key": 75
                                            },
                                            {
                                                "value": "ss_vlan_invent",
                                                "key": 77
                                            },
                                            {
                                                "value": "ss provisioning ",
                                                "key": 150
                                            },
                                            {
                                                "value": "ss ul issue",
                                                "key": 149
                                            },
                                            {
                                                "value": "wimax_ss_port_params",
                                                "key": 159
                                            }
                                        ],
                                        "device_name": "11343",
                                        "device_id": "11343"
                                    }
                                },
                                "success": 0
                            }
    """
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Failed to reset device service configuration."
    result['data']['meta'] = ''

    # Get last id of 'DeviceSyncHistory'.
    try:
        # Get all devices list from 'service_devicepingconfiguration'.
        ping_devices = DevicePingConfiguration.objects.all().values_list('device_name', flat=True)

        # Get list of sites associated with 'ping_devices'.
        ping_sites = Device.objects.filter(device_name__in=list(set(ping_devices))).values_list('site_instance__id',
                                                                                                flat=True)

        # Get all devices list from 'service_deviceserviceconfiguration'.
        svc_devices = DeviceServiceConfiguration.objects.all().values_list('device_name', flat=True)

        # Get list of sites associated with 'svc_devices'.
        svc_sites = Device.objects.filter(device_name__in=list(set(svc_devices))).values_list('site_instance__id',
                                                                                              flat=True)

        # Effected sites.
        effected_sites = set(list(ping_sites) + list(svc_sites))

        # Set 'is_device_change' bit of corresponding sites.
        SiteInstance.objects.filter(id__in=effected_sites).update(is_device_change=1)

        # Truncate 'service_deviceserviceconfiguration'.
        DeviceServiceConfiguration.objects.all().delete()

        # Truncate 'service_devicepingconfiguration'.
        DevicePingConfiguration.objects.all().delete()

        result['success'] = 1
        result['message'] = "Successfully reset device service configuration."

    except Exception as e:
        logger.info(e.message)

    return json.dumps({'result': result})