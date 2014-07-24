from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from device.models import Country, State, DeviceTechnology, VendorModel, ModelType
import logging
logger=logging.getLogger(__name__)


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


# update service according to the technology selected
@dajaxice_register
def update_services_as_per_technology(request, tech_id=""):
    dajax = Dajax()
    out = []
    # process if tech_id is not empty
    if tech_id and tech_id != "":
        try:
            # getting vendors for selected technology
            vendors = DeviceTechnology.objects.get(pk=tech_id).device_vendors
            # initialize list for device models
            device_models = []
            for vendor in vendors.all():
                models = VendorModel.objects.filter(vendor=vendor)
                device_models.append(models)
            # initialize list of services
            services = []
            for model in device_models:
                # get all device types associated with all models
                types = ModelType.objects.filter(model=model)
                for dt in types:
                    # get all services associated with 'types'
                    for svc in dt.type.service.all():
                        services.append(svc)
            # some devices have same services, so here we are making list of distinct services
            distinct_service = set(services)
            for svc in distinct_service:
                print "{} - {}".format(svc.name, svc.id)
            out = ["<option value=''>Select</option>"]
            for svc in distinct_service:
                out.append("<option value='%d'>%s</option>" % (svc.id, svc.name))
        except Exception as e:
            logger.info(e)
    else:
        out = ["<option value=''>Select</option>"]
    dajax.assign('#id_service', 'innerHTML', ''.join(out))
    return dajax.json()

