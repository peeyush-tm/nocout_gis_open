from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from device.models import DeviceTechnology, DeviceVendor, DeviceModel, DeviceType


@dajaxice_register
def update_vendor(request, option):
    dajax = Dajax()
    tech = DeviceTechnology.objects.filter(id=option)[0]
    vendors = tech.device_vendors.all()
    out = []
    for vendor in vendors:
        out.append("<option value='%d'>%s - %d</option>" % (int(vendor.id), vendor.name, int(vendor.id)))

    dajax.assign('#id_device_vendor', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_model(request, option):
    dajax = Dajax()
    vendor = DeviceVendor.objects.filter(id=option)[0]
    models = vendor.device_models.all()
    out = []
    for model in models:
        out.append("<option value='%d'>%s - %d</option>" % (int(model.id), model.name, int(model.id)))

    dajax.assign('#id_device_model', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_type(request, option):
    dajax = Dajax()
    model = DeviceModel.objects.filter(id=option)[0]
    types = model.device_types.all()
    out = []
    for dtype in types:
        out.append("<option value='%d'>%s - %d</option>" % (int(dtype.id), dtype.name, int(dtype.id)))

    dajax.assign('#id_device_type', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def device_type_extra_fields(request, option):
    dajax = Dajax()
    device_type = DeviceType.objects.filter(id=option)[0]
    device_extra_fields = device_type.devicetypefields_set.all()
    out = []
    for extra_field in device_extra_fields:
        out.append(
            "<tr><th><label for='%s'>%s:</label></th><td><input id='%s' name='%s' type='text' /></td></tr>"
            % (extra_field.field_name, extra_field.field_display_name, extra_field.field_name, extra_field.field_name))

    dajax.assign('#extra_fields', 'innerHTML', ''.join(out))
    return dajax.json()
