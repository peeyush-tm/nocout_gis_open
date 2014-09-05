from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from device.models import Country, State, DeviceTechnology, VendorModel, ModelType
import logging
from inventory.models import IconSettings
from service.models import Service
from django.contrib.staticfiles.templatetags.staticfiles import static

logger = logging.getLogger(__name__)


@dajaxice_register
def update_states(request, option):
    """
    updating states corresponding to the selected country
    :param request:
    :param option:
    """
    dajax = Dajax()
    country = Country.objects.get(pk=int(option))
    states = country.state_set.all().order_by('state_name')
    out = ["<option value=''>Select State....</option>"]
    for state in states:
        out.append("<option value='%d'>%s</option>" % (state.id, state.state_name))
    dajax.assign('#id_state', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_cities(request, option):
    """
    updating cities corresponding to the selected state
    :param request:
    :param option:
    """
    dajax = Dajax()
    state = State.objects.get(pk=int(option))
    cities = state.city_set.all().order_by('city_name')
    out = ["<option value=''>Select City....</option>"]
    for city in cities:
        out.append("<option value='%d'>%s</option>" % (city.id, city.city_name))
    dajax.assign('#id_city', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_states_after_invalid_form(request, option, state_id):
    """
    after invalid form submission
    updating states corresponding to the selected country
    :param request:
    :param option:
    :param state_id:
    """
    dajax = Dajax()
    country = Country.objects.get(pk=int(option))
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
    """
    updating cities corresponding to the selected state
    :param request:
    :param option:
    :param city_id:
    """
    dajax = Dajax()
    state = State.objects.get(pk=int(option))
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
def update_services_as_per_technology(request, tech_id=""):
    """
    update service according to the technology selected
    :param request:
    :param tech_id:
    """
    dajax = Dajax()
    out = list()
    # process if tech_id is not empty
    if tech_id and tech_id != "":
        try:
            # getting vendors for selected technology
            vendors = DeviceTechnology.objects.get(pk=tech_id).device_vendors
            # initialize list for device models
            device_models = list()
            for vendor in vendors.all():
                models = VendorModel.objects.filter(vendor=vendor)
                device_models.append(models)
            # initialize list of services
            services = list()
            for model in device_models:
                # get all device types associated with all models
                types = ModelType.objects.filter(model=model)
                for dt in types:
                    # get all services associated with 'types'
                    for svc in dt.type.service.all():
                        services.append(svc)
            # some devices have same services, so here we are making list of distinct services
            distinct_service = set(services)
            out = ["<option value=''>Select</option>"]
            for svc in distinct_service:
                out.append("<option value='%d'>%s</option>" % (svc.id, svc.alias))
        except Exception as e:
            logger.info(e)
    else:
        out = ["<option value=''>Select</option>"]
    dajax.assign('#id_service', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_data_sources_as_per_service(request, svc_id=""):
    """
    update data sources as per service
    :param request:
    :param svc_id:
    """
    dajax = Dajax()
    out = list()
    if svc_id and svc_id != "":
        try:
            # getting data sources associated with the selected service
            data_sources = Service.objects.get(id=svc_id).service_data_sources.all()
            out = ["<option value=''>Select</option>"]
            for data_source in data_sources:
                out.append("<option value='%d'>%s</option>" % (data_source.id, data_source.alias))
        except Exception as e:
            logger.info(e)
    else:
        out = ["<option value=''>Select</option>"]
    dajax.assign('#id_data_source', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def after_update_services_as_per_technology(request, tech_id="", selected=""):
    """
    update service according to the technology selected
    :param request:
    :param tech_id:
    :param selected:
    """
    dajax = Dajax()
    out = list()
    # process if tech_id is not empty
    if tech_id and tech_id != "":
        try:
            # getting vendors for selected technology
            vendors = DeviceTechnology.objects.get(pk=tech_id).device_vendors
            # initialize list for device models
            device_models = list()
            for vendor in vendors.all():
                models = VendorModel.objects.filter(vendor=vendor)
                device_models.append(models)
            # initialize list of services
            services = list()
            for model in device_models:
                # get all device types associated with all models
                types = ModelType.objects.filter(model=model)
                for dt in types:
                    # get all services associated with 'types'
                    for svc in dt.type.service.all():
                        services.append(svc)
            # some devices have same services, so here we are making list of distinct services
            distinct_service = set(services)
            out = ["<option value=''>Select</option>"]
            for svc in distinct_service:
                if svc.id == int(selected):
                    out.append("<option value='%d' selected>%s</option>" % (svc.id, svc.alias))
                else:
                    out.append("<option value='%d'>%s</option>" % (svc.id, svc.alias))
        except Exception as e:
            logger.info(e)
    else:
        out = ["<option value=''>Select</option>"]
    dajax.assign('#id_service', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def after_update_data_sources_as_per_service(request, svc_id="", selected=""):
    """
    update data sources as per service
    :param request:
    :param svc_id:
    :param selected:
    """
    dajax = Dajax()
    out = list()
    if svc_id and svc_id != "":
        try:
            # getting data sources associated with the selected service
            data_sources = Service.objects.get(id=svc_id).service_data_sources.all()
            out = ["<option value=''>Select</option>"]
            for data_source in data_sources:
                if data_source.id == int(selected):
                    out.append("<option value='%d' selected>%s</option>" % (data_source.id, data_source.alias))
                else:
                    out.append("<option value='%d'>%s</option>" % (data_source.id, data_source.alias))
        except Exception as e:
            logger.info(e)
    else:
        out = ["<option value=''>Select</option>"]
    dajax.assign('#id_data_source', 'innerHTML', ''.join(out))
    return dajax.json()



@dajaxice_register
def gt_warning_choices(request, option):
    """
    update 'gt_warning' field choices
    :param request:
    :param option:
    """

    dajax = Dajax()
    icon_settings = IconSettings.objects.all()
    out = list()
    out.append("<option value="">Select</option>")
    for icon_setting in icon_settings:
        img_url = "/media/"+ str(icon_setting.upload_image) \
            if "uploaded" in str(icon_setting.upload_image) \
            else static('img/{}'.format(icon_setting.upload_image))
        # img_url = static('img/{}'.format(icon_setting.upload_image))
        if icon_setting.id == int(option):
            out.append("<option value="+str(icon_setting.id)+" "
                        "style='background-image:url(\""+img_url+"\"); "
                        "background-size: 24px 24px;' selected>"+str(icon_setting.alias)+" </option>")

        else:
            out.append("<option value="+str(icon_setting.id)+" "
                        "style='background-image:url(\""+img_url+"\"); "
                        "background-size: 24px 24px;'>"+str(icon_setting.alias)+"</option>")

    dajax.assign("#id_gt_warning", 'innerHTML', ''.join(out))
    return dajax.json()

@dajaxice_register
def gt_warning_initial_choices(request):
    """
    update 'gt_warning' initial field choices
    :param request:
    """
    dajax = Dajax()
    icon_settings = IconSettings.objects.all()
    out = list()
    out.append("<option value=''>Select</option>")
    for icon_setting in icon_settings:
        img_url = "/media/"+ str(icon_setting.upload_image) \
            if "uploaded" in str(icon_setting.upload_image) \
            else static('img/{}'.format(icon_setting.upload_image))
        out.append("<option value="+str(icon_setting.id)+" "
                        "style='background-image:url(\""+img_url+"\"); "
                        "background-size: 24px 24px;'>"+str(icon_setting.alias)+"</option>")
    dajax.assign('#id_gt_warning', 'innerHTML', ''.join(out))
    return dajax.json()

@dajaxice_register
def bt_w_c_choices(request, option):
    """
    update 'bt_w_c' field choices
    :param request:
    :param option:
    """
    dajax = Dajax()
    icon_settings = IconSettings.objects.all()
    out = list()
    out.append("<option value="">Select</option>")
    for icon_setting in icon_settings:
        img_url = "/media/"+ str(icon_setting.upload_image) \
            if "uploaded" in str(icon_setting.upload_image) \
            else static('img/{}'.format(icon_setting.upload_image))
        # img_url = static('img/{}'.format(icon_setting.upload_image))
        if icon_setting.id == int(option):
            out.append("<option value="+str(icon_setting.id)+" "
                        "style='background-image:url(\""+img_url+"\"); "
                        "background-size: 24px 24px;' selected>"+str(icon_setting.alias)+" </option>")

        else:
            out.append("<option value="+str(icon_setting.id)+" "
                        "style='background-image:url(\""+img_url+"\"); "
                        "background-size: 24px 24px;'>"+str(icon_setting.alias)+"</option>")
    dajax.assign("#id_bt_w_c", 'innerHTML', ''.join(out))
    return dajax.json()

@dajaxice_register
def bt_w_c_initial_choices(request):
    """
    update 'bt_w_c' initial field choices
    :param request:
    """
    dajax = Dajax()
    icon_settings = IconSettings.objects.all()
    out = list()
    out.append("<option value=''>Select</option>")
    for icon_setting in icon_settings:
        img_url = "/media/"+ str(icon_setting.upload_image) \
            if "uploaded" in str(icon_setting.upload_image) \
            else static('img/{}'.format(icon_setting.upload_image))
        out.append("<option value="+str(icon_setting.id)+" "
                        "style='background-image:url(\""+img_url+"\"); "
                        "background-size: 24px 24px;'>"+str(icon_setting.alias)+"</option>")
    dajax.assign('#id_bt_w_c', 'innerHTML', ''.join(out))
    return dajax.json()

@dajaxice_register
def gt_critical_choices(request, option):
    """
    update 'gt_critical' field choices
    :param request:
    :param option:
    """
    dajax = Dajax()
    icon_settings = IconSettings.objects.all()
    out = list()
    out.append("<option value="">Select</option>")
    for icon_setting in icon_settings:
        img_url = "/media/"+ str(icon_setting.upload_image) \
            if "uploaded" in str(icon_setting.upload_image) \
            else static('img/{}'.format(icon_setting.upload_image))
        # img_url = static('img/{}'.format(icon_setting.upload_image))
        if icon_setting.id == int(option):
            out.append("<option value="+str(icon_setting.id)+" "
                        "style='background-image:url(\""+img_url+"\"); "
                        "background-size: 24px 24px;' selected>"+str(icon_setting.alias)+" </option>")

        else:
            out.append("<option value="+str(icon_setting.id)+" "
                        "style='background-image:url(\""+img_url+"\"); "
                        "background-size: 24px 24px;'>"+str(icon_setting.alias)+"</option>")

    dajax.assign("#id_gt_critical", 'innerHTML', ''.join(out))
    return dajax.json()

@dajaxice_register
def gt_critical_initial_choices(request):
    """
    update 'gt_critical' initial field choices
    :param request:
    """
    dajax = Dajax()
    icon_settings = IconSettings.objects.all()
    out = list()
    out.append("<option value=''>Select</option>")
    for icon_setting in icon_settings:
        img_url = static('img/{}'.format(icon_setting.upload_image))
        out.append("<option value={} style='background-image:url({}); background-size: 24px 24px;'>{}</option>"
                   .format(icon_setting.id, img_url, icon_setting.alias))
    dajax.assign('#id_gt_critical', 'innerHTML', ''.join(out))
    return dajax.json()


# @dajaxice_register
# def load_sheet_no_select_menu(request, uploaded_file):
#     dajax = Dajax()
#     book = xlrd.open_workbook(uploaded_file, file_contents=uploaded_file.read())
#     sheet = book.sheet_by_index(0)
#     print "*********************** book - ", book
#     print "*********************** sheet - ", sheet
#     print "***************** no. of rows - ", sheet.nrows
#     print "*********************** request - ", request
#     print "*********************** uploaded_file - ", uploaded_file
#     return dajax.json()
#
# @dajaxice_register
# def update_sheet_no_select_menu(request, uploaded_file):
#     print "********************** uploaded_file - ", uploaded_file
#     dajax = Dajax()
#     book = xlrd.open_workbook(uploaded_file, file_contents=uploaded_file.read())
#     sheet = book.sheet_by_index(0)
#     print "*********************** book - ", book
#     print "*********************** sheet - ", sheet
#     print "***************** no. of rows - ", sheet.nrows
#     print "*********************** request - ", request
#     print "*********************** uploaded_file - ", str(uploaded_file)
#     return dajax.json()




