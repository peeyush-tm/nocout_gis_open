import json
from actstream import action
from django.db.models import Q
from django.db.models.query import ValuesQuerySet
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from device.models import Device, Inventory, DeviceType, DeviceTypeFields, DeviceTypeFieldsValue, DeviceTechnology, \
    TechnologyVendor, DeviceVendor, VendorModel, DeviceModel, ModelType
from device_group.models import DeviceGroup
from forms import DeviceForm, DeviceTypeFieldsForm, DeviceTypeFieldsUpdateForm, DeviceTechnologyForm, \
    DeviceVendorForm, DeviceModelForm, DeviceTypeForm
from nocout.utils.util import DictDiffer
from site_instance.models import SiteInstance
from django.http.response import HttpResponseRedirect
from service.models import Service
from django.shortcuts import render_to_response
from django.template import RequestContext

#BEGIN: import django settings
#we need DEBUG varaible for collecting the logs
from django.conf import settings
#END: import django settings
if settings.DEBUG:
    import logging
    logger = logging.getLogger(__name__)

# ***************************************** Device Views ********************************************
from user_group.models import UserGroup


class DeviceList(ListView):
    model = Device
    template_name = 'device/devices_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'device_name',         'sTitle' : 'Device Name',   'sWidth':'null',},
            {'mData':'site_instance__name', 'sTitle' : 'Site Instance', 'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'device_group__name',  'sTitle' : 'Device Group',  'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'ip_address',          'sTitle' : 'IP Address',    'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'city',                'sTitle' : 'City',          'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'state',               'sTitle' : 'State',         'sWidth':'10%' ,'sClass':'hidden-xs'},
            {'mData':'actions',             'sTitle' : 'Actions',       'sWidth':'5%' ,}
            ,]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


def create_device_tree(request):

    templateData = {
        'username' : request.user.username,
        'hostIp' : request.META["SERVER_NAME"] +":"+request.META["SERVER_PORT"]
    }
    
    return render_to_response('device/devices_tree_view.html',templateData,context_instance=RequestContext(request))


        

class DeviceListingTable(BaseDatatableView):
    model = Device
    columns = ['device_name', 'site_instance__name', 'device_group__name', 'ip_address', 'city', 'state']
    order_columns = ['device_name', 'site_instance__name', 'device_group__name', 'ip_address', 'city', 'state']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        if settings.DEBUG:
            logger.debug(qs, exc_info=True, extra={'stack': True, 'request': self.request})

        return qs

    def get_initial_queryset(self):
        if not self.model:
            
            if settings.DEBUG:
                logger.error("Need to provide a model or implement get_initial_queryset!",
                                 extra={'stack': True, 'request': self.request})

            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Device.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/device/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
               <a href="#" onclick="Dajaxice.device.device_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret



class DeviceDetail(DetailView):
    model = Device
    template_name = 'device/device_detail.html'

    def get_context_data(self, **kwargs):
        
        if settings.DEBUG:
            logger.debug(self.object, extra={'stack': True, 'request': self.request})
            logger.debug(kwargs, extra={'stack': True, 'request': self.request})

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

        action.send( self.request.user, verb='Created', action_object=device )
        return HttpResponseRedirect( DeviceCreate.success_url )


class DeviceUpdate(UpdateView):
    template_name = 'device/device_update.html'
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
        self.object.device_name = form.cleaned_data['device_name']
        self.object.device_alias = form.cleaned_data['device_alias']
        self.object.device_technology = form.cleaned_data['device_technology']
        self.object.device_vendor = form.cleaned_data['device_vendor']
        self.object.device_model = form.cleaned_data['device_model']
        self.object.device_type = form.cleaned_data['device_type']
        self.object.ip_address = form.cleaned_data['ip_address']
        self.object.mac_address = form.cleaned_data['mac_address']
        self.object.netmask = form.cleaned_data['netmask']
        self.object.gateway = form.cleaned_data['gateway']
        self.object.dhcp_state = form.cleaned_data['dhcp_state']
        self.object.host_priority = form.cleaned_data['host_priority']
        self.object.host_state = form.cleaned_data['host_state']
        self.object.address = form.cleaned_data['address']
        self.object.city = form.cleaned_data['city']
        self.object.state = form.cleaned_data['state']
        self.object.timezone = form.cleaned_data['timezone']
        self.object.latitude = form.cleaned_data['latitude']
        self.object.longitude = form.cleaned_data['longitude']
        self.object.description = form.cleaned_data['description']
        self.object.save()

        # saving site_instance --> FK Relation
        try:
            self.object.site_instance = SiteInstance.objects.get(name=form.cleaned_data['site_instance'])
            self.object.save()
        except Exception as site_exception:
            if settings.Debug:
                logger.critical("Instance(site) information missing : %s" % (site_exception),
                                exc_info=True, 
                                extra={'stack': True, 'request': self.request}
                                )
            pass

        # deleting old services of device
        self.object.service.clear()

        # saving associated services  --> M2M Relation (Model: Service)
        for service in form.cleaned_data['service']:
            device_service = Service.objects.get(service_name=service)
            self.object.service.add(device_service)
            self.object.save()

        # saving device 'parent device' --> FK Relation
        try:
            parent_device = Device.objects.get(device_name=form.cleaned_data['parent'])
            self.object.parent = parent_device
            self.object.save()
        except Exception as device_parent_exception:
            if settings.Debug:
                logger.critical("Device Parent information missing : %s" % (device_parent_exception),
                                exc_info=True, 
                                extra={'stack': True, 'request': self.request}
                                )
            pass

        # deleting old device extra field values
        try:
            DeviceTypeFieldsValue.objects.filter(device_id=self.object.id).delete()
        except Exception as device_extra_exception:
            if settings.Debug:
                logger.critical("Device Extra information missing : %s" % (device_extra_exception),
                                exc_info=True, 
                                extra={'stack': True, 'request': self.request}
                                )
            pass

        # fetching device extra fields associated with 'device type'
        try:
            device_type = DeviceType.objects.get(id=int(self.request.POST.get('device_type')))
            # it gives all device fields associated with device_type object
            device_type.devicetypefields_set.all()
        except Exception as device_type_exception:
            if settings.Debug:
                logger.critical("Device Type information missing : %s" % (device_type_exception),
                                exc_info=True, 
                                extra={'stack': True, 'request': self.request}
                                )
            pass

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
                dtfv.device_id = self.object.id
                dtfv.save()
            except:
                pass

        # delete old relationship exist in inventory
        Inventory.objects.filter(device=self.object).delete()

        # saving device_group --> M2M Relation (Model: Inventory)
        for dg in form.cleaned_data['device_group']:
            inventory = Inventory()
            inventory.device = self.object
            inventory.device_group = dg
            inventory.save()

        initial_field_dict = { field : [ form.initial[field] ] if field in ('site_instance','parent','device_group') and
                               form.initial[field] else form.initial[field] for field in form.initial.keys() }
        def cleaned_data_field():
            cleaned_data_field_dict={}
            for field in form.cleaned_data.keys():
                if field in ('device_group', 'service'):
                    cleaned_data_field_dict[field]=map(lambda obj: obj.pk, form.cleaned_data[field])
                elif field in ('parent', 'site_instance'):
                    cleaned_data_field_dict[field]=[form.cleaned_data[field].pk] if form.cleaned_data[field] else None
                elif field in ('device_model', 'device_type', 'device_vendor', 'device_technology'):
                    cleaned_data_field_dict[field]=int(form.cleaned_data[field])
                else:
                    cleaned_data_field_dict[field]=form.cleaned_data[field]

            return cleaned_data_field_dict

        cleaned_data_field_dict=cleaned_data_field()
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            initial_field_dict['parent'] = UserGroup.objects.get(pk=initial_field_dict['parent'][0]).name if initial_field_dict['parent'] else str(None)
            initial_field_dict['site_instance'] = SiteInstance.objects.get(pk=initial_field_dict['site_instance'][0]).name if initial_field_dict['site_instance'] else str(None)
            initial_field_dict['device_group'] = DeviceGroup.objects.get(pk=initial_field_dict['device_group'][0]).name
            initial_field_dict['service'] = ', '.join([Service.objects.get(pk=service).service_name for service in initial_field_dict['service']])

            cleaned_data_field_dict['parent'] = UserGroup.objects.get(pk=cleaned_data_field_dict['parent'][0]).name if cleaned_data_field_dict['parent'] else str(None)
            cleaned_data_field_dict['site_instance'] = SiteInstance.objects.get(pk=cleaned_data_field_dict['site_instance'][0]).name if cleaned_data_field_dict['site_instance'] else str(None)
            cleaned_data_field_dict['device_group'] = DeviceGroup.objects.get(pk=cleaned_data_field_dict['device_group'][0]).name
            cleaned_data_field_dict['service'] = ', '.join([Service.objects.get(pk=service).service_name for service in cleaned_data_field_dict['service']])

            verb_string = 'Changed values of Device %s from initial values '%(self.object.device_name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            action.send(self.request.user, verb=verb_string)

        return HttpResponseRedirect(DeviceCreate.success_url)


class DeviceDelete(DeleteView):
    model = Device

    template_name = 'device/device_delete.html'
    success_url = reverse_lazy('device_list')

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device: %s'%(self.object.device_name))
        super(DeviceDelete, self).delete(self, request, *args, **kwargs)



# ******************************** Device Type Form Fields Views ************************************


class DeviceTypeFieldsList(ListView):
    model = DeviceTypeFields
    template_name = 'device_extra_fields/device_extra_fields_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceTypeFieldsList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'field_name',         'sTitle' : 'Name',    'sWidth':'null',},
            {'mData':'field_display_name', 'sTitle' : 'Field Display Name',   'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'device_type__name',  'sTitle' : 'Device Type',  'sWidth':'null'},
            {'mData':'actions',            'sTitle' : 'Actions', 'sWidth':'10%' ,}
            ,]
        context['datatable_headers'] = json.dumps( datatable_headers )
        return context

class DeviceTypeFieldsListingTable(BaseDatatableView):
    model = DeviceTypeFields
    columns = ['field_name', 'field_display_name','device_type__name']
    order_columns = ['field_name', 'field_display_name','device_type__name']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DeviceTypeFields.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/device_fields/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/device_fields/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret




class DeviceTypeFieldsDetail(DetailView):
    model = DeviceTypeFields
    template_name = 'device_extra_fields/device_extra_field_detail.html'


class DeviceTypeFieldsCreate(CreateView):
    template_name = 'device_extra_fields/device_extra_field_new.html'
    model = DeviceTypeFields
    form_class = DeviceTypeFieldsForm
    success_url = reverse_lazy('device_extra_field_list')

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(DeviceTypeFieldsCreate.success_url)

class DeviceTypeFieldsUpdate(UpdateView):
    template_name = 'device_extra_fields/device_extra_field_update.html'
    model = DeviceTypeFields
    form_class = DeviceTypeFieldsUpdateForm
    success_url = reverse_lazy('device_extra_field_list')

    def form_valid(self, form):

        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : form.cleaned_data[field].pk
        if field in ('device_type') and  form.cleaned_data[field] else form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            initial_field_dict['device_type'] = DeviceType.objects.get( pk= initial_field_dict['device_type']).name if initial_field_dict['device_type'] else str(None)
            cleaned_data_field_dict['device_type'] = DeviceType.objects.get( pk=cleaned_data_field_dict['device_type']).name if cleaned_data_field_dict['device_type'] else str(None)

            verb_string = 'Changed values of Device Fields: %s from initial values '%(self.object.field_name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            self.object=form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(DeviceTypeFieldsCreate.success_url)



class DeviceTypeFieldsDelete(DeleteView):
    model = DeviceTypeFields
    template_name = 'device_extra_fields/device_extra_field_delete.html'
    success_url = reverse_lazy('device_extra_field_list')

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting user: %s'%(self.object.field_name))
        super(DeviceTypeFieldsDelete, self).delete(self, request, *args, **kwargs)



# **************************************** Device Technology ****************************************


class DeviceTechnologyList(ListView):
    model = DeviceTechnology
    template_name = 'device_technology/device_technology_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceTechnologyList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',       'sTitle' : 'Name',       'sWidth':'null'},
            {'mData':'alias',      'sTitle' : 'Alias',      'sWidth':'null'},
            {'mData':'actions',    'sTitle' : 'Actions',    'sWidth':'10%' ,},
            ]
        context['datatable_headers'] = json.dumps( datatable_headers )
        return context

class DeviceTechnologyListingTable(BaseDatatableView):
    model = DeviceTechnology
    columns = ['name', 'alias']
    order_columns = ['name', 'alias']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DeviceTechnology.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/technology/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/technology/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret



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

        action.send(self.request.user, verb='Created', action_object = device_technology)
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

        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : map(lambda obj: obj.pk, form.cleaned_data[field])
        if field in ('device_vendors') and  form.cleaned_data[field] else form.cleaned_data[field] for field in form.cleaned_data.keys() }


        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            initial_field_dict['device_vendors'] = ', '.join([DeviceVendor.objects.get(pk=vendor).name for vendor in initial_field_dict['device_vendors']])
            cleaned_data_field_dict['device_vendors'] = ', '.join([DeviceVendor.objects.get(pk=vendor).name for vendor in cleaned_data_field_dict['device_vendors']])

            verb_string ='Changed values of Device Technology : %s from initial values '%(self.object.name) \
                          + ', '.join(['%s: %s' %(k, initial_field_dict[k]) for k in changed_fields_dict])\
                          +' to '+\
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            action.send(self.request.user, verb=verb_string)

        return HttpResponseRedirect(DeviceTechnologyUpdate.success_url)


class DeviceTechnologyDelete(DeleteView):
    model = DeviceTechnology
    template_name = 'device_technology/device_technology_delete.html'
    success_url = reverse_lazy('device_technology_list')


    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device technology: %s'%(self.object.field_name))
        super(DeviceTechnologyDelete, self).delete(self, request, *args, **kwargs)

# ************************************* Device Vendor ***********************************************


class DeviceVendorList(ListView):
    model = DeviceVendor
    template_name = 'device_vendor/device_vendor_list.html'

    def get_context_data(self, **kwargs):
            context=super(DeviceVendorList, self).get_context_data(**kwargs)
            datatable_headers = [
            {'mData':'name',                   'sTitle' : 'Name',       'sWidth':'null',},
            {'mData':'alias',                  'sTitle' : 'Alias',      'sWidth':'null',},
            {'mData':'actions',                'sTitle' : 'Actions',    'sWidth':'10%' ,}
            ]
            context['datatable_headers'] = json.dumps(datatable_headers)
            return context

class DeviceVendorListingTable(BaseDatatableView):
    model = DeviceVendor
    columns = ['name', 'alias']
    order_columns = ['name', 'alias']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DeviceVendor.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/vendor/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/vendor/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret





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

        action.send(self.request.user, verb='Created', action_object = device_vendor)
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
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : map(lambda obj: obj.pk, form.cleaned_data[field])
        if field in ('device_models') and  form.cleaned_data[field] else form.cleaned_data[field]
        for field in form.cleaned_data.keys() }

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            initial_field_dict['device_models'] = ', '.join([DeviceModel.objects.get(pk=vendor).name for vendor in initial_field_dict['device_models']])
            cleaned_data_field_dict['device_models'] = ', '.join([DeviceModel.objects.get(pk=vendor).name for vendor in cleaned_data_field_dict['device_models']])

            verb_string ='Changed values of Device Vendor : %s from initial values '%(self.object.name) \
                          + ', '.join(['%s: %s' %(k, initial_field_dict[k]) for k in changed_fields_dict])\
                          +' to '+\
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])

            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            action.send(self.request.user, verb=verb_string)

        return HttpResponseRedirect(DeviceVendorUpdate.success_url)


class DeviceVendorDelete(DeleteView):
    model = DeviceVendor
    template_name = 'device_vendor/device_vendor_delete.html'
    success_url = reverse_lazy('device_vendor_list')

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device vendor: %s'%(self.object.name))
        super(DeviceVendorDelete, self).delete(self, request, *args, **kwargs)


# ****************************************** Device Model *******************************************


class DeviceModelList(ListView):
    model = DeviceModel
    template_name = 'device_model/device_model_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceModelList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',       'sTitle' : 'Name',       'sWidth':'null',},
            {'mData':'alias',      'sTitle' : 'Alias',      'sWidth':'null',},
            {'mData':'actions',    'sTitle' : 'Actions',    'sWidth':'10%' ,}
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class DeviceModelListingTable(BaseDatatableView):
    model = DeviceModel
    columns = ['name', 'alias']
    order_columns = ['name', 'alias']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DeviceModel.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/model/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/model/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret

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

        action.send(self.request.user, verb='Created', action_object = device_model)
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

        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : map(lambda obj: obj.pk, form.cleaned_data[field])
        if field in ('device_types') and  form.cleaned_data[field] else form.cleaned_data[field]
        for field in form.cleaned_data.keys() }

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            initial_field_dict['device_types'] = ', '.join([DeviceType.objects.get(pk=vendor).name for vendor in initial_field_dict['device_types']])
            cleaned_data_field_dict['device_types'] = ', '.join([DeviceType.objects.get(pk=vendor).name for vendor in cleaned_data_field_dict['device_types']])

            verb_string ='Changed values of Device Models : %s from initial values '%(self.object.name) \
                          + ', '.join(['%s: %s' %(k, initial_field_dict[k]) for k in changed_fields_dict])\
                          +' to '+\
                          ', '.join(['%s: %s' %(k, cleaned_data_field_dict[k]) for k in changed_fields_dict])

            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            action.send(self.request.user, verb=verb_string)


        return HttpResponseRedirect(DeviceModelUpdate.success_url)


class DeviceModelDelete(DeleteView):
    model = DeviceModel
    template_name = 'device_model/device_model_delete.html'
    success_url = reverse_lazy('device_model_list')

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device vendor: %s'%(self.object.name))
        super(DeviceModelDelete, self).delete(self, request, *args, **kwargs)

# ****************************************** Device Type *******************************************


class DeviceTypeList(ListView):
    model = DeviceType
    template_name = 'device_type/device_type_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceTypeList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                   'sTitle' : 'Name',       'sWidth':'null',},
            {'mData':'alias',                  'sTitle' : 'Alias',      'sWidth':'null',},
            {'mData':'actions',                'sTitle' : 'Actions',    'sWidth':'10%' ,}
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class DeviceTypeListingTable(BaseDatatableView):
    model = DeviceType
    columns = ['name', 'alias']
    order_columns = ['name', 'alias']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DeviceType.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/type/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/type/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret

class DeviceTypeDetail(DetailView):
    model = DeviceType
    template_name = 'device_type/device_type_detail.html'


class DeviceTypeCreate(CreateView):
    template_name = 'device_type/device_type_new.html'
    model = DeviceType
    form_class = DeviceTypeForm
    success_url = reverse_lazy('device_type_list')

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(DeviceTypeCreate.success_url)


class DeviceTypeUpdate(UpdateView):
    template_name = 'device_type/device_type_update.html'
    model = DeviceType
    form_class = DeviceTypeForm
    success_url = reverse_lazy('device_type_list')

    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:

            verb_string = 'Changed values of Device Type: %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object=form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(DeviceTypeUpdate.success_url)

class DeviceTypeDelete(DeleteView):
    model = DeviceType
    template_name = 'device_type/device_type_delete.html'
    success_url = reverse_lazy('device_type_list')


    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device type: %s'%(self.object.name))
        super(DeviceTypeDelete, self).delete(self, request, *args, **kwargs)





