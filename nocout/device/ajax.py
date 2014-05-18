from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from device.models import Device, DeviceTechnology, DeviceVendor, DeviceModel, DeviceType


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
            "<tr><th><label for='%s'>%s:</label></th><td><input id='%s' name='%s' type='text' class='form-control' width='400px'/></td></tr>"
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
