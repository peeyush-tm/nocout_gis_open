from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
import json
from actstream import action
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from device_group.models import DeviceGroup
from nocout.utils.util import DictDiffer
from models import Inventory
from forms import InventoryForm
from organization.models import Organization
from user_group.models import UserGroup
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit
from forms import AntennaForm, BaseStationForm, BackhaulForm, SectorForm, CustomerForm, SubStationForm, CircuitForm



#**************************************** Inventory *********************************************
def inventory(request):
    return render(request,'inventory/inventory.html')

class InventoryListing(ListView):
    model = Inventory
    template_name = 'inventory/inventory_list.html'

    def get_context_data(self, **kwargs):
        context=super(InventoryListing, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                'sTitle' : 'Name',             'sWidth':'null',},
            {'mData':'alias',               'sTitle' : 'Alias',            'sWidth':'null',},
            {'mData':'user_group__name',    'sTitle' : 'User Group',       'sWidth':'null',},
            {'mData':'organization__name',  'sTitle' : 'Organization',     'sWidth':'null',},
            {'mData':'city',                'sTitle' : 'City',             'sWidth':'null',},
            {'mData':'state',               'sTitle' : 'State',            'sWidth':'null',},
            {'mData':'country',             'sTitle' : 'Country',          'sWidth':'null',},
            {'mData':'description',         'sTitle' : 'Description',      'sWidth':'null',},
            ]
        #if the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%' ,})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class InventoryListingTable(BaseDatatableView):
    model = Inventory
    columns = ['name', 'alias', 'user_group__name','organization__name', 'city', 'state', 'country', 'description']
    order_columns = ['name', 'alias', 'user_group__name','organization__name', 'city', 'state', 'country', 'description']

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
        organization_descendants_ids= self.request.user.userprofile.organization.get_descendants(include_self=True).values_list('id', flat=True)
        return Inventory.objects.filter(organization__in = organization_descendants_ids).values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/inventory/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                       <a href="/inventory/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))

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


class InventoryCreate(CreateView):
    template_name = 'inventory/inventory_new.html'
    model = Inventory
    form_class = InventoryForm
    success_url = reverse_lazy('InventoryList')

    @method_decorator(permission_required('inventory.add_inventory', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(InventoryCreate, self).dispatch(*args, **kwargs)

    def form_valid( self, form):
        self.object= form.save()
        action.send( self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect( InventoryCreate.success_url )


class InventoryUpdate(UpdateView):
    template_name = 'inventory/inventory_update.html'
    model = Inventory
    form_class = InventoryForm
    success_url = reverse_lazy('InventoryList')

    @method_decorator(permission_required('inventory.change_inventory', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(InventoryUpdate, self).dispatch(*args, **kwargs)

    def form_valid( self, form):
        self.object= form.save()
        action.send( self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect( InventoryCreate.success_url )

class InventoryDelete(DeleteView):
    model = Inventory
    template_name = 'inventory/inventory_delete.html'
    success_url = reverse_lazy('InventoryList')

    @method_decorator(permission_required('inventory.delete_inventory', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(InventoryDelete, self).dispatch(*args, **kwargs)

def inventory_details_wrt_organization(request):
    organization_id= request.GET['organization']
    organization_descendants_ids= Organization.objects.get(id= organization_id).get_descendants(include_self=True).values_list('id', flat=True)
    user_group= UserGroup.objects.filter(organization__in = organization_descendants_ids, is_deleted=0).values_list('id','name')
    device_groups= DeviceGroup.objects.filter(organization__in = organization_descendants_ids, is_deleted=0).values_list('id','name')
    response_device_groups=response_user_group=''
    for index in range(len(device_groups)):
        response_device_groups+='<option value={0}>{1}</option>'.format(*map(str, device_groups[index]))
    for index in range(len(user_group)):
        response_user_group+='<option value={0}>{1}</option>'.format(*map(str, user_group[index]))

    return HttpResponse( json.dumps({'response': {'device_groups': response_device_groups , 'user_groups': response_user_group} }), \
                        mimetype='application/json')


#**************************************** Antenna *********************************************
class AntennaList(ListView):
    model = Antenna
    template_name = 'antenna/antenna_list.html'

    def get_context_data(self, **kwargs):
        context=super(AntennaList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',              'sTitle' : 'Name',             'sWidth':'null',},
            {'mData':'alias',             'sTitle' : 'Alias',            'sWidth':'null',},
            {'mData':'height',            'sTitle' : 'Height',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'polarization',      'sTitle' : 'Polarization',     'sWidth':'null',},
            {'mData':'tilt',              'sTitle' : 'Tilt',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'beam_width',        'sTitle' : 'Beam Width',       'sWidth':'10%' ,},]

        #if the user role is Admin or operator then the action column will appear on the datatable
        if 'admin' or 'operator' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'10%' ,})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class AntennaListingTable(BaseDatatableView):
    model = AntennaList
    columns = ['name', 'alias', 'height', 'polarization', 'tilt', 'beam_width']
    order_columns = ['name', 'alias', 'height', 'polarization', 'tilt', 'beam_width']

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
        return Antenna.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/antenna/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/antenna/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class AntennaDetail(DetailView):
    model = Antenna
    template_name = 'antenna/antenna_detail.html'


class AntennaCreate(CreateView):
    template_name = 'antenna/antenna_new.html'
    model = Antenna
    form_class = AntennaForm
    success_url = reverse_lazy('antennas_list')

    @method_decorator(permission_required('inventory.add_antenna', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(AntennaCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(AntennaCreate.success_url)


class AntennaUpdate(UpdateView):
    template_name = 'antenna/antenna_update.html'
    model = Antenna
    form_class = AntennaForm
    success_url = reverse_lazy('antennas_list')

    @method_decorator(permission_required('inventory.change_antenna', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(AntennaUpdate, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Antenna : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( AntennaUpdate.success_url )

class AntennaDelete(DeleteView):
    model = Antenna
    template_name = 'antenna/antenna_delete.html'
    success_url = reverse_lazy('antennas_list')

    @method_decorator(permission_required('inventory.delete_antenna', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(AntennaDelete, self).dispatch(*args, **kwargs)

#****************************************** Base Station ********************************************
class BaseStationList(ListView):
    model = BaseStation
    template_name = 'base_station/base_stations_list.html'

    def get_context_data(self, **kwargs):
        context=super(BaseStationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                      'sTitle' : 'Name',                'sWidth':'null',},
            {'mData':'alias',                     'sTitle' : 'Alias',               'sWidth':'null',},
            {'mData':'bs_site_id',                'sTitle' : 'Base Site ID',        'sWidth':'null',},
            {'mData':'bs_switch__device_name',    'sTitle' : 'Base Switch Name',    'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'backhaul__name',           'sTitle' : 'Backhaul',            'sWidth':'null',},
            {'mData':'bs_type',                   'sTitle' : 'Base Station Type',   'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'building_height',           'sTitle' : 'Building Height',     'sWidth':'null',},
            {'mData':'description',               'sTitle' : 'Description',         'sWidth':'null','sClass':'hidden-xs'},
            ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        if 'admin' or 'operator' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'10%' ,})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class BaseStationListingTable(BaseDatatableView):
    model = BaseStationList
    columns = ['name', 'alias', 'bs_site_id', 'bs_switch__device_name', 'backhaul__name', 'bs_type', 'building_height', 'description']
    order_columns = ['name', 'alias', 'bs_site_id', 'bs_switch__device_name', 'backhaul__name', 'bs_type', 'building_height', 'description']

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
        return BaseStation.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/base_station/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/base_station/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class BaseStationDetail(DetailView):
    model = BaseStation
    template_name = 'base_station/base_station_detail.html'


class BaseStationCreate(CreateView):
    template_name = 'base_station/base_station_new.html'
    model = BaseStation
    form_class = BaseStationForm
    success_url = reverse_lazy('base_stations_list')

    @method_decorator(permission_required('inventory.add_basestation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(BaseStationCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(BaseStationCreate.success_url)


class BaseStationUpdate(UpdateView):
    template_name = 'base_station/base_station_update.html'
    model = BaseStation
    form_class = BaseStationForm
    success_url = reverse_lazy('base_stations_list')

    @method_decorator(permission_required('inventory.change_basestation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(BaseStationUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Base Station : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( BaseStationUpdate.success_url )

class BaseStationDelete(DeleteView):
    model = BaseStation
    template_name = 'base_station/base_station_delete.html'
    success_url = reverse_lazy('base_stations_list')
    
    @method_decorator(permission_required('inventory.delete_basestation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(BaseStationDelete, self).dispatch(*args, **kwargs)



#**************************************** Backhaul *********************************************
class BackhaulList(ListView):
    model = Backhaul
    template_name = 'backhaul/backhauls_list.html'

    def get_context_data(self, **kwargs):
        context=super(BackhaulList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                    'sTitle' : 'Name',                         'sWidth':'null',},
            {'mData':'alias',                   'sTitle' : 'Alias',                        'sWidth':'null',},
            {'mData':'bh_configured_on__device_name',        'sTitle' : 'Backhaul Configured On',       'sWidth':'null',},
            {'mData':'bh_port',                 'sTitle' : 'Backhaul Port',                'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'bh_type',                 'sTitle' : 'Backhaul Type',                'sWidth':'null',},
            {'mData':'pop__device_name',                     'sTitle' : 'POP',                          'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'pop_port',                'sTitle' : 'POP Port',                     'sWidth':'null',},
            {'mData':'bh_connectivity',         'sTitle' : 'Connectivity',                 'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'bh_circuit_id',           'sTitle' : 'Circuit ID',                   'sWidth':'null',},
            {'mData':'bh_capacity',             'sTitle' : 'Capacity',                     'sWidth':'null','sClass':'hidden-xs'},
            ]

        #if the user role is Admin or operator then the action column will appear on the datatable
        if 'admin' or 'operator' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'10%' ,})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class BackhaulListingTable(BaseDatatableView):
    model = BackhaulList
    columns = ['name', 'alias', 'bh_configured_on__device_name', 'bh_port', 'bh_type', 'pop__device_name', 'pop_port', 'bh_connectivity', 'bh_circuit_id', 'bh_capacity']
    order_columns = ['name', 'alias', 'bh_configured_on__device_name', 'bh_port', 'bh_type', 'pop__device_name', 'pop_port', 'bh_connectivity', 'bh_circuit_id', 'bh_capacity']

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
        return Backhaul.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/backhaul/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/backhaul/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class BackhaulDetail(DetailView):
    model = Backhaul
    template_name = 'backhaul/backhaul_detail.html'


class BackhaulCreate(CreateView):
    template_name = 'backhaul/backhaul_new.html'
    model = Backhaul
    form_class = BackhaulForm
    success_url = reverse_lazy('backhauls_list')

    @method_decorator(permission_required('inventory.add_backhaul', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(BackhaulCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(BackhaulCreate.success_url)


class BackhaulUpdate(UpdateView):
    template_name = 'backhaul/backhaul_update.html'
    model = Backhaul
    form_class = BackhaulForm
    success_url = reverse_lazy('backhauls_list')

    @method_decorator(permission_required('inventory.change_backhaul', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(BackhaulUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Backhaul : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( BackhaulUpdate.success_url )

class BackhaulDelete(DeleteView):
    model = Backhaul
    template_name = 'backhaul/backhaul_delete.html'
    success_url = reverse_lazy('backhauls_list')

    @method_decorator(permission_required('inventory.delete_backhaul', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(BackhaulDelete, self).dispatch(*args, **kwargs)


#**************************************** Sector *********************************************
class SectorList(ListView):
    model = Sector
    template_name = 'sector/sectors_list.html'

    def get_context_data(self, **kwargs):
        context=super(SectorList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                       'sTitle' : 'Name',             'sWidth':'null',},
            {'mData':'alias',                      'sTitle' : 'Alias',            'sWidth':'null',},
            {'mData':'sector_id',                  'sTitle' : 'ID',               'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'sector_configured_on__device_name',       'sTitle' : 'Sector Configured On',     'sWidth':'null',},
            {'mData':'sector_configured_on_port__name',  'sTitle' : 'Sector Configured On Port',              'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'antenna__name',              'sTitle' : 'Antenna',          'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'mrc',                        'sTitle' : 'MRC',              'sWidth':'null',},
            {'mData':'description',                'sTitle' : 'Description',      'sWidth':'null','sClass':'hidden-xs'},
            ]

        #if the user role is Admin or operator then the action column will appear on the datatable
        if 'admin' or 'operator' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'10%' ,})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class SectorListingTable(BaseDatatableView):
    model = SectorList
    columns = ['name', 'alias', 'sector_id', 'base_station__name', 'sector_configured_on__device_name', 'sector_configured_on_port__name', 'antenna__name', 'mrc', 'description']
    order_columns = ['name', 'alias', 'sector_id', 'base_station__name', 'sector_configured_on__device_name', 'sector_configured_on_port__name', 'antenna__name', 'mrc', 'description']

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
        return Sector.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/sector/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/sector/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class SectorDetail(DetailView):
    model = Sector
    template_name = 'sector/sector_detail.html'


class SectorCreate(CreateView):
    template_name = 'sector/sector_new.html'
    model = Sector
    form_class = SectorForm
    success_url = reverse_lazy('sectors_list')

    @method_decorator(permission_required('inventory.add_sector', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SectorCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(SectorCreate.success_url)


class SectorUpdate(UpdateView):
    template_name = 'sector/sector_update.html'
    model = Sector
    form_class = SectorForm
    success_url = reverse_lazy('sectors_list')

    @method_decorator(permission_required('inventory.change_sector', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SectorUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Customer : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( SectorUpdate.success_url )

class SectorDelete(DeleteView):
    model = Sector
    template_name = 'sector/sector_delete.html'
    success_url = reverse_lazy('sectors_list')

    @method_decorator(permission_required('inventory.delete_sector', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SectorDelete, self).dispatch(*args, **kwargs)


#**************************************** Customer *********************************************
class CustomerList(ListView):
    model = Customer
    template_name = 'customer/customers_list.html'

    def get_context_data(self, **kwargs):
        context=super(CustomerList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',              'sTitle' : 'Name',             'sWidth':'null',},
            {'mData':'alias',             'sTitle' : 'Alias',            'sWidth':'null',},
            {'mData':'city',              'sTitle' : 'City',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'state',             'sTitle' : 'State',            'sWidth':'null',},
            {'mData':'address',           'sTitle' : 'Address',          'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'description',       'sTitle' : 'Description',      'sWidth':'null',},
            ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        if 'admin' or 'operator' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'10%' ,})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class CustomerListingTable(BaseDatatableView):
    model = CustomerList
    columns = ['name', 'alias', 'city', 'state', 'address', 'description']
    order_columns = ['name', 'alias', 'city', 'state', 'address', 'description']

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
        return Customer.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/customer/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/customer/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class CustomerDetail(DetailView):
    model = Customer
    template_name = 'customer/customer_detail.html'


class CustomerCreate(CreateView):
    template_name = 'customer/customer_new.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customers_list')

    @method_decorator(permission_required('inventory.add_customer', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CustomerCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(CustomerCreate.success_url)


class CustomerUpdate(UpdateView):
    template_name = 'customer/customer_update.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customers_list')

    @method_decorator(permission_required('inventory.change_customer', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CustomerUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Customer : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( CustomerUpdate.success_url )

class CustomerDelete(DeleteView):
    model = Customer
    template_name = 'customer/customer_delete.html'
    success_url = reverse_lazy('customers_list')

    @method_decorator(permission_required('inventory.delete_customer', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CustomerDelete, self).dispatch(*args, **kwargs)
    

#**************************************** Sub Station *********************************************
class SubStationList(ListView):
    model = SubStation
    template_name = 'sub_station/sub_stations_list.html'

    def get_context_data(self, **kwargs):
        context=super(SubStationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',             'sTitle' : 'Name',               'sWidth':'null',},
            {'mData':'alias',            'sTitle' : 'Alias',              'sWidth':'null',},
            {'mData':'device__device_name',               'sTitle' : 'Device',                 'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'version',              'sTitle' : 'Version',                'sWidth':'null',},
            {'mData':'serial_no',        'sTitle' : 'Serial No.',         'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'building_height',  'sTitle' : 'Building Height',    'sWidth':'null',},
            {'mData':'tower_height',     'sTitle' : 'Tower Height',       'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'city',             'sTitle' : 'City',               'sWidth':'null',},
            {'mData':'state',            'sTitle' : 'State',              'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'address',          'sTitle' : 'Address',            'sWidth':'null',},
            {'mData':'description',      'sTitle' : 'Description',        'sWidth':'null','sClass':'hidden-xs'},
            ]

        #if the user role is Admin or operator then the action column will appear on the datatable
        if 'admin' or 'operator' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'10%' ,})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class SubStationListingTable(BaseDatatableView):
    model = SubStationList
    columns = ['name', 'alias', 'device__device_name', 'version', 'serial_no', 'building_height', 'tower_height', 'city', 'state', 'address', 'description']
    order_columns = ['name', 'alias', 'device__device_name', 'version', 'serial_no', 'building_height', 'tower_height', 'city', 'state', 'address', 'description']

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
        return SubStation.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/sub_station/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/sub_station/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class SubStationDetail(DetailView):
    model = SubStation
    template_name = 'sub_station/sub_station_detail.html'


class SubStationCreate(CreateView):
    template_name = 'sub_station/sub_station_new.html'
    model = SubStation
    form_class = SubStationForm
    success_url = reverse_lazy('sub_stations_list')

    @method_decorator(permission_required('inventory.add_substation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SubStationCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(SubStationCreate.success_url)


class SubStationUpdate(UpdateView):
    template_name = 'sub_station/sub_station_update.html'
    model = SubStation
    form_class = SubStationForm
    success_url = reverse_lazy('sub_stations_list')

    @method_decorator(permission_required('inventory.change_substation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SubStationUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of SubStation : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( SubStationUpdate.success_url )

class SubStationDelete(DeleteView):
    model = SubStation
    template_name = 'sub_station/sub_station_delete.html'
    success_url = reverse_lazy('sub_stations_list')

    @method_decorator(permission_required('inventory.delete_substation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SubStationDelete, self).dispatch(*args, **kwargs)


#**************************************** Circuit *********************************************
class CircuitList(ListView):
    model = Circuit
    template_name = 'circuit/circuits_list.html'

    def get_context_data(self, **kwargs):
        context=super(CircuitList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                    'sTitle' : 'Name',                 'sWidth':'null',},
            {'mData':'alias',                   'sTitle' : 'Alias',                'sWidth':'null',},
            {'mData':'circuit_id',              'sTitle' : 'Circuit ID',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'sector__name',                  'sTitle' : 'Sector',               'sWidth':'null',},
            {'mData':'customer__name',                'sTitle' : 'Customer',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'sub_station__name',             'sTitle' : 'Sub Station',          'sWidth':'null',},
            {'mData':'date_of_acceptance',      'sTitle' : 'Date of Acceptance',   'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'description',             'sTitle' : 'Description',          'sWidth':'null',},
            ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        if 'admin' or 'operator' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'10%' ,})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class CircuitListingTable(BaseDatatableView):
    model = CircuitList
    columns = ['name', 'alias', 'circuit_id', 'sector__name', 'customer__name', 'sub_station__name', 'date_of_acceptance', 'description']
    order_columns = ['name', 'alias', 'circuit_id', 'sector__name', 'customer__name', 'sub_station__name', 'date_of_acceptance', 'description']

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
        return Circuit.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/circuit/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/circuit/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class CircuitDetail(DetailView):
    model = Circuit
    template_name = 'circuit/circuit_detail.html'


class CircuitCreate(CreateView):
    template_name = 'circuit/circuit_new.html'
    model = Circuit
    form_class = CircuitForm
    success_url = reverse_lazy('circuits_list')

    @method_decorator(permission_required('inventory.add_circuit', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CircuitCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(CircuitCreate.success_url)


class CircuitUpdate(UpdateView):
    template_name = 'circuit/circuit_update.html'
    model = Circuit
    form_class = CircuitForm
    success_url = reverse_lazy('circuits_list')

    @method_decorator(permission_required('inventory.change_circuit', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CircuitUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Circuit : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( CircuitUpdate.success_url )

class CircuitDelete(DeleteView):
    model = Circuit
    template_name = 'circuit/circuit_delete.html'
    success_url = reverse_lazy('circuits_list')

    @method_decorator(permission_required('inventory.delete_circuit', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CircuitDelete, self).dispatch(*args, **kwargs)
