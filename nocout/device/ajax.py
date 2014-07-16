import ast
import json
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType, \
    DeviceTypeFieldsValue, Country, State, City, DevicePort
import requests
import logging
from service.models import Service, ServiceDataSource, ServiceParameters
import urllib
from site_instance.models import SiteInstance

logger=logging.getLogger(__name__)


# updating vendor corresponding to the selected technology
@dajaxice_register
def update_vendor(request, option):
    dajax = Dajax()
    tech = DeviceTechnology.objects.get(pk=int(option))
    vendors = tech.device_vendors.all()
    out = []
    out.append("<option value='' selected>Select</option>")
    for vendor in vendors:
        out.append("<option value='%d'>%s</option>" % (vendor.id, vendor.name))
    dajax.assign('#id_device_vendor', 'innerHTML', ''.join(out))
    return dajax.json()

# updating model corresponding to the selected vendor
@dajaxice_register
def update_model(request, option):
    dajax = Dajax()
    vendor = DeviceVendor.objects.get(pk=int(option))
    models = vendor.device_models.all()
    out = []
    out.append("<option value=''>Select</option>")
    for model in models:
        out.append("<option value='%d'>%s</option>" % (model.id, model.name))

    dajax.assign('#id_device_model', 'innerHTML', ''.join(out))
    return dajax.json()


# updating type corresponding to the selected model
@dajaxice_register
def update_type(request, option):
    dajax = Dajax()
    model = DeviceModel.objects.get(pk=int(option))
    types = model.device_types.all()
    out = []
    out.append("<option value=''>Select</option>")
    for dtype in types:
        out.append("<option value='%d'>%s</option>" % (dtype.id, dtype.name))
    dajax.assign('#id_device_type', 'innerHTML', ''.join(out))
    return dajax.json()

# to get vendor as during device update
@dajaxice_register
def after_update_vendor(request, option, selected=''):
    dajax = Dajax()
    tech = DeviceTechnology.objects.get(pk=int(option))
    vendors = tech.device_vendors.all()
    out = []
    out.append("<option value=''>Select</option>")
    for vendor in vendors:
        if vendor.id==int(selected):
            out.append("<option value='%d' selected>%s</option>" % (vendor.id, vendor.name))
        else:
            out.append("<option value='%d'>%s</option>" % (vendor.id, vendor.name))
    dajax.assign('#id_device_vendor', 'innerHTML', ''.join(out))
    return dajax.json()

# updating model corresponding to the selected vendor
@dajaxice_register
def after_update_model(request, option, selected=''):

    dajax = Dajax()
    vendor = DeviceVendor.objects.get(pk=int(option))
    models = vendor.device_models.all()
    out = []
    out.append("<option value=''>Select</option>")
    for model in models:
        if model.id==int(selected):
            out.append("<option value='%d' selected>%s</option>" % (model.id, model.name))
        else:
            out.append("<option value='%d'>%s</option>" % (model.id, model.name))

    dajax.assign('#id_device_model', 'innerHTML', ''.join(out))
    return dajax.json()


# updating type corresponding to the selected model
@dajaxice_register
def after_update_type(request, option, selected=''):
    dajax = Dajax()
    model = DeviceModel.objects.get(pk=int(option))
    types = model.device_types.all()
    out = []
    out.append("<option value=''>Select</option>")
    for dtype in types:
        if dtype.id==int(selected):
            out.append("<option value='%d' selected>%s</option>" % (dtype.id, dtype.name))
        else:
            out.append("<option value='%d'>%s</option>" % (dtype.id, dtype.name))
    dajax.assign('#id_device_type', 'innerHTML', ''.join(out))
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
    out = ["<option value=''>Select</option>"]
    for device in Device.objects.all():
        out.append("<option value='%d'>%s - (%s)</option>"
                   % (int(device.id), device.device_alias, device.ip_address))
    dajax.assign("#id_parent", 'innerHTML', ''.join(out))
    return dajax.json()


# update device 'parent field' selection menu as per last selection on invalid form submission
@dajaxice_register
def device_parent_choices_selected(request, option):
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
            logger.info("Device type field doesn't exist.")
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
        logger.info("No new device parent exist.")

    # fetching all child devices of device which needs to be deleted
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


# add device to nms core
@dajaxice_register
def add_device_to_nms_core(request, device_id):
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Device addition failed."
    result['data']['meta'] = ''
    device = Device.objects.get(pk=device_id)
    if device.host_state != "Disable":
        # get 'agent_tag' from DeviceType model
        agent_tag = ""
        try :
            agent_tag = DeviceType.objects.get(id=device.device_type).agent_tag
        except:
            logger.info("Device has no device type.")


        device_data = {'device_name': device.device_name,
                       'device_alias': device.device_alias,
                       'ip_address':device.ip_address,
                       'agent_tag': agent_tag,
                       'site': device.site_instance.name,
                       'mode' : 'addhost'}

        master_site = SiteInstance.objects.get(name='master_UA')
        # url for nocout.py
        # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
        # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
        url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                master_site.password,
                                                                master_site.machine.machine_ip,
                                                                master_site.web_service_port,
                                                                master_site.name)

        r = requests.post(url , data=device_data)
        response_dict = ast.literal_eval(r.text)
        if r:
            result['data'] = device_data
            result['success'] = 1
            if response_dict['error_code'] != None:
                result['message'] = response_dict['error_message'].capitalize()
            else:
                result['message'] = "Device added successfully."
                # set 'is_added_to_nms' to 1 after device successfully added to nocout nms core
                device.is_added_to_nms = 1
                device.save()
    else:
        result['message'] = "Device state is disabled. First enable it than add it to nms core."
    return json.dumps({'result': result})


# sync devices with monitoring core
@dajaxice_register
def sync_device_with_nms_core(request, device_id):
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = "Device activation for monitoring failed."
    result['data']['meta'] = ''
    device_data = {'mode' : 'sync'}
    # get device
    device = Device.objects.get(pk=device_id)
    master_site = SiteInstance.objects.get(name='master_UA')
    # url for nocout.py
    # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
    # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
    url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                            master_site.password,
                                                            master_site.machine.machine_ip,
                                                            master_site.web_service_port,
                                                            master_site.name)

    r = requests.post(url, data=device_data)

    try:
        response_dict = ast.literal_eval(r.text)
        if r:
            result['data'] = device_data
            result['success'] = 1
            result['message'] = response_dict['message'].capitalize()
    except:
        result['message'] = "Failed to sync device and services."
        logger.info(r.text)
    return json.dumps({'result': result})


# generate content for add service popup form
@dajaxice_register
def add_service_form(request, value):
    # device to which services are associated
    device = Device.objects.get(id=value)
    # result: data dictionary send in ajax response
    #{
    #  "success": 1,     # 0 - fail, 1 - success, 2 - exception
    #  "message": "Success/Fail message.",
    #  "data": {
    #     "meta": {},
    #     "objects": {
    #          "device_name": <id>,
    #          "device_name": <name>,
    #          "device_alias": <name>,
    #          "services": [
    #                   {
    #                       "name': <id>,
    #                       "value": <value>,
    #                   },
    #                   {
    #                       "name': <id>,
    #                       "value": <value>,
    #                   }
    #           ]
    #          "ports": [
    #                   {
    #                       "name': <id>,
    #                       "value": <value>,
    #                   },
    #                   {
    #                       "name': <id>,
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
                device_type = DeviceType.objects.get(id=device.device_type)
                services = device_type.service.all()
                for service in services:
                    svc_dict = {}
                    svc_dict['key'] = service.id
                    svc_dict['value'] = service.alias
                    result['data']['objects']['services'].append(svc_dict)
            else:
                result['message'] = "Master site doesn't exist. <br /> Please first create master site with name 'master_UA'."
        else:
            result['message'] = "First add device in nms core."
    except:
        logger.info("No service to monitor.")

    return json.dumps({'result': result})


# service data sources select menu popup for service addition form
@dajaxice_register
def service_data_sources_popup(request, option=""):
    dajax = Dajax()
    out = []
    if option and option != "":
        service = Service.objects.get(pk=int(option))
        if service:
            try:
                service_data_sources = service.service_data_sources.all()
                if service_data_sources:
                    out.append("<h5 class='text-warning'>Select data sources:</h5> ")
                    out.append("<select class='form-control'  id='service_data_source_select_id'>")
                    out.append("<option value='' selected>Select</option>")
                    for sds in service_data_sources:
                        out.append("<option value='%d'>%s</option>" % (sds.id, sds.alias))
                    out.append("</select>")
                else:
                    out.append("<h5 class='text-warning'>No data source associated.</h5> ")
            except:
                logger.info("No data source available.")
    else:
        out.append("<h5 class='text-warning'>No data source associated.</h5> ")
    dajax.assign('#service_data_source_id', 'innerHTML', ''.join(out))
    return dajax.json()


# get service templates for service addition form
@dajaxice_register
def get_service_templates(request, option=""):
    dajax = Dajax()
    out = []
    field_id = "#svc_params_id_{0}".format(option)
    if option and option != "":
        svc_params = ServiceParameters.objects.all()
        if svc_params:
            try:
                if svc_params:
                    out.append("<h5>Select service template:</h5> ")
                    out.append("<select class='form-control'  id='service_%d'>" % option)
                    out.append("<option value='' selected>Select</option>")
                    for svc_param in svc_params:
                        out.append("<option value='%d'>%s</option>" % (svc_param.id, svc_param.parameter_description))
                    out.append("</select>")
                else:
                    out.append("<h5 class='text-warning'>No data source associated.</h5> ")
            except:
                logger.info("No data source available.")
    else:
        out.append("<h5 class='text-warning'>No data source associated.</h5> ")
    dajax.assign(field_id, 'innerHTML', ''.join(out))
    return dajax.json()


# get service parameters and data source tables for service addition form
@dajaxice_register
def get_service_para_and_data_source_tables(request, service_value="", para_value="" ):
    dajax = Dajax()
    params = []
    data_sources = []
    service_paras_table_id = "#svc_params_table_id_{0}".format(service_value)
    service_data_source_table_id = "#service_data_source_table_id_{0}".format(service_value)
    if service_value and service_value != "":
        service = Service.objects.get(pk=service_value)
        svc_param = ServiceParameters.objects.get(pk=para_value)
        params.append("<br />")
        params.append("<div class=''><div class='box border orange'><div class='box-title'><h4><i class='fa fa-table'></i>Service Parameters</h4></div>")
        params.append("<div class='box-body'><table class='table'>")
        params.append("<thead><tr><th>Normal Check Interval</th><th>Retry Check Interval</th><th>Max Check Attemps</th></tr></thead>")
        params.append("<tbody><tr><td>%d</td><td>%d</td><td>%d</td></tr></tbody>" % (svc_param.normal_check_interval,
                                                                             svc_param.retry_check_interval,
                                                                             svc_param.max_check_attempts)
        )
        params.append("</div></div></div>")
        try:
            svc_data_sources = service.service_data_sources.all()
            data_sources.append("<br />")
            data_sources.append("<div class=''><div class='box border orange'><div class='box-title'><h4><i class='fa fa-table'></i>Service Data Sources</h4></div>")
            data_sources.append("<div class='box-body'><table class='table'>")
            data_sources.append("<thead><tr><th>Name</th><th>Warning</th><th>Critical</th></tr></thead><tbody>")
            for svc_data_source in svc_data_sources:
                data_sources.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (svc_data_source.alias,
                                                                                    svc_data_source.warning,
                                                                                    svc_data_source.critical)
            )
            params.append("</tbody></div></div></div>")
        except:
            logger.info("Service data source doesn't exist.")
    else:
        params.append("<h5 class='text-warning'>No data to show.</h5> ")
    dajax.assign(service_paras_table_id, 'innerHTML', ''.join(params))
    dajax.assign(service_data_source_table_id, 'innerHTML', ''.join(data_sources))
    return dajax.json()


# adding services to nocout core
@dajaxice_register
def add_service(request, service_data):
    # service format for nocout core
    # {
    #     "snmp_community": {
    #         "read_community": "public",
    #         "version": "v2c"
    #     },
    #     "agent_tag": "snmp",
    #     "service_name": "radwin_rssi",
    #     "snmp_port": 161,
    #     "serv_params": {
    #         "normal_check_interval": 5,
    #         "max_check_attempts": 5,
    #         "retry_check_interval": 5
    #     },
    #     "device_name": "radwin",
    #     "mode": "addservice",
    #     "cmd_params": {
    #         "rssi": {
    #             "warning": "-50",
    #             "critical": "-80"
    #         }
    #     }
    # }
    result = dict()
    result['data'] = {}
    result['success'] = 0
    result['message'] = ""
    result['data']['meta'] = {}
    result['data']['objects'] = {}

    for sd in service_data:
        try:
            result = dict()
            result['data'] = {}
            result['success'] = 0
            result['message'] = ""
            result['data']['meta'] = {}
            result['data']['objects'] = {}
            device = Device.objects.get(pk=int(sd['device_id']))
            service = Service.objects.get(pk=int(sd['service_id']))
            service_para = ServiceParameters.objects.get(pk=int(sd['template_id']))
            print "************************************** sd *********************************************"
            print sd

            print "&&&&&&&&&&&&&&&&&&&&&&&&&&&& Enter &&&&&&&&&&&&&&&&&&&&&&&&&&&&&"

            # mode
            result['data']['objects']['mode'] = "addservice"
            print "**************************** result['data']['objects']['mode'] *********************"
            print result['data']
            # device name
            result['data']['objects']['device_name'] = str(device.device_name)
            # service name
            result['data']['objects']['service_name'] = str(service.name)
            print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& result['data']['objects']['service_name'] *********************"
            print result['data']['objects']['service_name']
            # service parameters
            result['data']['objects']['serv_params'] = {}
            result['data']['objects']['serv_params']['normal_check_interval'] = str(service_para.normal_check_interval)
            result['data']['objects']['serv_params']['retry_check_interval'] = str(service_para.retry_check_interval)
            result['data']['objects']['serv_params']['max_check_attempts'] = str(service_para.max_check_attempts)
            # snmp parameters
            result['data']['objects']['snmp_community'] = {}
            result['data']['objects']['snmp_community']['version'] = str(service_para.protocol.version)
            result['data']['objects']['snmp_community']['read_community'] = str(service_para.protocol.read_community)
            # command parameters
            result['data']['objects']['cmd_params'] = {}
            print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ result['data']['objects']['cmd_params'] ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            print result['data']['objects']['cmd_params']
            for sds in service.service_data_sources.all():
                result['data']['objects']['cmd_params'][str(sds.name)] = {'warning': str(sds.warning), 'critical': str(sds.critical)}
            # snmp port
            result['data']['objects']['snmp_port'] = str(service_para.protocol.port)
            # agent tag
            result['data']['objects']['agent_tag'] = str(DeviceType.objects.get(pk=device.device_type).agent_tag)
            # payload data
            service_data = result['data']['objects']
            print "***************************************service_data ***********************************"
            print service_data

            master_site = SiteInstance.objects.get(name='master_UA')
            # url for nocout.py
            # url = 'http://omdadmin:omd@localhost:90/master_UA/check_mk/nocout.py'
            # url = 'http://<username>:<password>@<domain_name>:<port>/<site_name>/check_mk/nocout.py'
            url = "http://{}:{}@{}:{}/{}/check_mk/nocout.py".format(master_site.username,
                                                                    master_site.password,
                                                                    master_site.machine.machine_ip,
                                                                    master_site.web_service_port,
                                                                    master_site.name)

            encoded_data = urllib.urlencode(service_data)

            r = requests.post(url , data=encoded_data)

            response_dict = ast.literal_eval(r.text)
            print "********************************* response_dict.get('error_message')**********************"
            print response_dict.get('error_message')

            if r:
                result['data'] = service_data
                result['success'] = 1
                if not response_dict.get('success'):
                    logger.info(response_dict.get('error_message'))
                    result['message'] += "Failed to add service '%s'. <br />" % (service.name)
                else:
                    result['message'] += "Successfully added service '%s'. <br />" % (service.name)
                    device = Device.objects.get(pk=int(sd['device_id']))

                    # set 'is_monitored_on_nms' to 1 if service is added successfully
                    device.is_monitored_on_nms = 1
                    device.save()

        except:
            result['message'] += "Failed to add service '%s'. <br />" % (service.name)
    return json.dumps({'result': result})

