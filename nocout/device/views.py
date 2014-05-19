import json
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from device.models import Device, Inventory, DeviceType, DeviceTypeFields, DeviceTypeFieldsValue, DeviceTechnology, \
    TechnologyVendor, DeviceVendor, VendorModel, DeviceModel, ModelType
from forms import DeviceForm, DeviceTypeFieldsForm, DeviceTypeFieldsUpdateForm, DeviceTechnologyForm, \
    DeviceVendorForm, DeviceModelForm, DeviceTypeForm
from nocout.utils.jquery_datatable_generation import Datatable_Generation
from nocout.utils.util import date_handler
from site_instance.models import SiteInstance
from django.http.response import HttpResponseRedirect
from service.models import Service


# ***************************************** Device Views ********************************************


class DeviceList(ListView):
    model = Device
    template_name = 'device/devices_list.html'


    def get_queryset(self):
        queryset = self.model._default_manager.values('device_name', 'site_instance__name', 'device_group__name',
                                                      'ip_address','city','state')
        return queryset[:10]

    def get_context_data(self, **kwargs):

        context=super( DeviceList, self ).get_context_data(**kwargs)
        object_list = context['object_list']
        object_list, object_list_headers = Datatable_Generation( object_list ).main()
        context['object_list'] = json.dumps( object_list, default=date_handler )
        context.update({
            'object_list_headers' : json.dumps(object_list_headers, default=date_handler )
        })
        return context




class DeviceDetail(DetailView):
    model = Device
    template_name = 'device/device_detail.html'

    def get_context_data(self, **kwargs):
        print "*********************************************************************************"
        print self.object
        print "*********************************************************************************"
        print kwargs
        context = super(DeviceDetail, self).get_context_data(**kwargs)
        return context


class DeviceCreate(CreateView):
    template_name = 'device/device_new.html'
    model = Device
    form_class = DeviceForm
    success_url = reverse_lazy('device_list')

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """

        # post_fields: it contains form post data
        # for e.g. <QueryDict: {u'tower_height': [u''], u'qos_bw': [u'fevefvef']}>
        post_fields = self.request.POST

        # all_non_empty_post_fields: it's a list which contains all non empty fields
        # for e.g. [u'qos_bw', u'device_group', u'device_type', u'timezone', u'device_technology']
        all_non_empty_post_fields = []

        # It inserts all non empty fields keys from 'post_fields' into 'all_non_empty_post_fields'
        # except 'csrf' hidden field
        for key, value in post_fields.iteritems():
            if key == "csrfmiddlewaretoken": continue
            if value != "":
                all_non_empty_post_fields.append(key)

        # saving device data
        device = Device()
        device.device_name = form.cleaned_data['device_name']
        device.device_alias = form.cleaned_data['device_alias']
        device.device_technology = form.cleaned_data['device_technology']
        device.device_vendor = form.cleaned_data['device_vendor']
        device.device_model = form.cleaned_data['device_model']
        device.device_type = form.cleaned_data['device_type']
        device.ip_address = form.cleaned_data['ip_address']
        device.mac_address = form.cleaned_data['mac_address']
        device.netmask = form.cleaned_data['netmask']
        device.gateway = form.cleaned_data['gateway']
        device.dhcp_state = form.cleaned_data['dhcp_state']
        device.host_priority = form.cleaned_data['host_priority']
        device.host_state = form.cleaned_data['host_state']
        device.address = form.cleaned_data['address']
        device.city = form.cleaned_data['city']
        device.state = form.cleaned_data['state']
        device.timezone = form.cleaned_data['timezone']
        device.latitude = form.cleaned_data['latitude']
        device.longitude = form.cleaned_data['longitude']
        device.description = form.cleaned_data['description']
        device.save()

        # saving site_instance --> FK Relation
        try:
            device.site_instance = SiteInstance.objects.get(name=form.cleaned_data['site_instance'])
            device.save()
        except:
            print "No instance to add."

        # saving associated services  --> M2M Relation (Model: Service)
        for service in form.cleaned_data['service']:
            device_service = Service.objects.get(service_name=service)
            device.service.add(device_service)
            device.save()

        # saving device 'parent device' --> FK Relation
        try:
            parent_device = Device.objects.get(device_name=form.cleaned_data['parent'])
            device.parent = parent_device
            device.save()
        except:
            print "Device has no parent."

        # fetching device extra fields associated with 'device type'
        try:
            device_type = DeviceType.objects.get(id=int(self.request.POST.get('device_type')))
            # it gives all device fields associated with device_type object
            device_type.devicetypefields_set.all()
        except:
            print "No device type exists."

        # saving eav relation data i.e. device extra fields those depends on device type
        for field in all_non_empty_post_fields:
            try:
                # dtf: device type field object
                # dtfv: device type field value object
                dtf = DeviceTypeFields.objects.filter(field_name=field,
                                                      device_type_id=int(self.request.POST.get('device_type')))
                dtfv = DeviceTypeFieldsValue()
                dtfv.device_type_field = dtf[0]
                dtfv.field_value = self.request.POST.get(field)
                dtfv.device_id = device.id
                dtfv.save()
            except:
                pass

        # saving device_group --> M2M Relation (Model: Inventory)
        for dg in form.cleaned_data['device_group']:
            inventory = Inventory()
            inventory.device = device
            inventory.device_group = dg
            inventory.save()
        return HttpResponseRedirect(DeviceCreate.success_url)


class DeviceUpdate(UpdateView):
    template_name = 'device/device_update.html'
    model = Device
    form_class = DeviceForm
    success_url = reverse_lazy('device_list')


class DeviceDelete(DeleteView):
    model = Device

    template_name = 'device/device_delete.html'
    success_url = reverse_lazy('device_list')

# ******************************** Device Type Form Fields Views ************************************


class DeviceTypeFieldsList(ListView):
    model = DeviceTypeFields
    template_name = 'device_extra_fields/device_extra_fields_list.html'


class DeviceTypeFieldsDetail(DetailView):
    model = DeviceTypeFields
    template_name = 'device_extra_fields/device_extra_field_detail.html'


class DeviceTypeFieldsCreate(CreateView):
    template_name = 'device_extra_fields/device_extra_field_new.html'
    model = DeviceTypeFields
    form_class = DeviceTypeFieldsForm
    success_url = reverse_lazy('device_extra_field_list')


class DeviceTypeFieldsUpdate(UpdateView):
    template_name = 'device_extra_fields/device_extra_field_update.html'
    model = DeviceTypeFields
    form_class = DeviceTypeFieldsUpdateForm
    success_url = reverse_lazy('device_extra_field_list')


class DeviceTypeFieldsDelete(DeleteView):
    model = DeviceTypeFields
    template_name = 'device_extra_fields/device_extra_field_delete.html'
    success_url = reverse_lazy('device_extra_field_list')


# **************************************** Device Technology ****************************************


class DeviceTechnologyList(ListView):
    model = DeviceTechnology
    template_name = 'device_technology/device_technology_list.html'


class DeviceTechnologyDetail(DetailView):
    model = DeviceTechnology
    template_name = 'device_technology/device_technology_detail.html'


class DeviceTechnologyCreate(CreateView):
    template_name = 'device_technology/device_technology_new.html'
    model = DeviceTechnology
    form_class = DeviceTechnologyForm
    success_url = reverse_lazy('device_technology_list')

    def form_valid(self, form):
        device_technology = DeviceTechnology()
        device_technology.name = form.cleaned_data['name']
        device_technology.alias = form.cleaned_data['alias']
        device_technology.save()

        # saving device_vendors --> M2M Relation (Model: TechnologyVendor)
        for device_vendor in form.cleaned_data['device_vendors']:
            tv = TechnologyVendor()
            tv.technology = device_technology
            tv.vendor = device_vendor
            tv.save()
        return HttpResponseRedirect(DeviceTechnologyCreate.success_url)


class DeviceTechnologyUpdate(UpdateView):
    template_name = 'device_technology/device_technology_update.html'
    model = DeviceTechnology
    form_class = DeviceTechnologyForm
    success_url = reverse_lazy('device_technology_list')

    def form_valid(self, form):
        self.object.name = form.cleaned_data['name']
        self.object.alias = form.cleaned_data['alias']
        self.object.save()

        # delete old relationship exist in technology-vendor
        TechnologyVendor.objects.filter(technology=self.object).delete()

        # updating device_vendors --> M2M Relation (Model: TechnologyVendor)
        for device_vendor in form.cleaned_data['device_vendors']:
            tv = TechnologyVendor()
            tv.technology = self.object
            tv.vendor = device_vendor
            tv.save()
        return HttpResponseRedirect(DeviceTechnologyUpdate.success_url)


class DeviceTechnologyDelete(DeleteView):
    model = DeviceTechnology
    template_name = 'device_technology/device_technology_delete.html'
    success_url = reverse_lazy('device_technology_list')


# ************************************* Device Vendor ***********************************************


class DeviceVendorList(ListView):
    model = DeviceVendor
    template_name = 'device_vendor/device_vendor_list.html'


class DeviceVendorDetail(DetailView):
    model = DeviceVendor
    template_name = 'device_vendor/device_vendor_detail.html'


class DeviceVendorCreate(CreateView):
    template_name = 'device_vendor/device_vendor_new.html'
    model = DeviceVendor
    form_class = DeviceVendorForm
    success_url = reverse_lazy('device_vendor_list')

    def form_valid(self, form):
        device_vendor = DeviceVendor()
        device_vendor.name = form.cleaned_data['name']
        device_vendor.alias = form.cleaned_data['alias']
        device_vendor.save()

        # saving device_models --> M2M Relation (Model: VendorModel)
        for device_model in form.cleaned_data['device_models']:
            vm = VendorModel()
            vm.vendor = device_vendor
            vm.model = device_model
            vm.save()
        return HttpResponseRedirect(DeviceVendorCreate.success_url)


class DeviceVendorUpdate(UpdateView):
    template_name = 'device_vendor/device_vendor_update.html'
    model = DeviceVendor
    form_class = DeviceVendorForm
    success_url = reverse_lazy('device_vendor_list')

    def form_valid(self, form):
        self.object.name = form.cleaned_data['name']
        self.object.alias = form.cleaned_data['alias']
        self.object.save()

        # delete old relationship exist in vendor-model
        VendorModel.objects.filter(vendor=self.object).delete()

        # updating device_models --> M2M Relation (Model: VendorModel)
        for device_model in form.cleaned_data['device_models']:
            vm = VendorModel()
            vm.vendor = self.object
            vm.model = device_model
            vm.save()
        return HttpResponseRedirect(DeviceVendorUpdate.success_url)


class DeviceVendorDelete(DeleteView):
    model = DeviceVendor
    template_name = 'device_vendor/device_vendor_delete.html'
    success_url = reverse_lazy('device_vendor_list')


# ****************************************** Device Model *******************************************


class DeviceModelList(ListView):
    model = DeviceModel
    template_name = 'device_model/device_model_list.html'


class DeviceModelDetail(DetailView):
    model = DeviceModel
    template_name = 'device_model/device_model_detail.html'


class DeviceModelCreate(CreateView):
    template_name = 'device_model/device_model_new.html'
    model = DeviceModel
    form_class = DeviceModelForm
    success_url = reverse_lazy('device_model_list')

    def form_valid(self, form):
        device_model = DeviceModel()
        device_model.name = form.cleaned_data['name']
        device_model.alias = form.cleaned_data['alias']
        device_model.save()

        # saving device_types --> M2M Relation (Model: ModelType)
        for device_type in form.cleaned_data['device_types']:
            mt = ModelType()
            mt.model = device_model
            mt.type = device_type
            mt.save()
        return HttpResponseRedirect(DeviceModelCreate.success_url)


class DeviceModelUpdate(UpdateView):
    template_name = 'device_model/device_model_update.html'
    model = DeviceModel
    form_class = DeviceModelForm
    success_url = reverse_lazy('device_model_list')

    def form_valid(self, form):
        self.object.name = form.cleaned_data['name']
        self.object.alias = form.cleaned_data['alias']
        self.object.save()

        # delete old relationship exist in model-type
        ModelType.objects.filter(model=self.object).delete()

        # updating model_types --> M2M Relation (Model: ModelType)
        for device_type in form.cleaned_data['device_types']:
            mt = ModelType()
            mt.model = self.object
            mt.type = device_type
            mt.save()
        return HttpResponseRedirect(DeviceModelUpdate.success_url)


class DeviceModelDelete(DeleteView):
    model = DeviceModel
    template_name = 'device_model/device_model_delete.html'
    success_url = reverse_lazy('device_model_list')


# ****************************************** Device Type *******************************************


class DeviceTypeList(ListView):
    model = DeviceType
    template_name = 'device_type/device_type_list.html'


class DeviceTypeDetail(DetailView):
    model = DeviceType
    template_name = 'device_type/device_type_detail.html'


class DeviceTypeCreate(CreateView):
    template_name = 'device_type/device_type_new.html'
    model = DeviceType
    form_class = DeviceTypeForm
    success_url = reverse_lazy('device_type_list')


class DeviceTypeUpdate(UpdateView):
    template_name = 'device_type/device_type_update.html'
    model = DeviceType
    form_class = DeviceTypeForm
    success_url = reverse_lazy('device_type_list')


class DeviceTypeDelete(DeleteView):
    model = DeviceType
    template_name = 'device_type/device_type_delete.html'
    success_url = reverse_lazy('device_type_list')
