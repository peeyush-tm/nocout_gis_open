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
from models import Inventory, IconSettings, LivePollingSettings, ThresholdConfiguration, ThematicSettings
from forms import InventoryForm, IconSettingsForm, LivePollingSettingsForm, ThresholdConfigurationForm, \
    ThematicSettingsForm
from organization.models import Organization
from user_group.models import UserGroup
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit
from forms import AntennaForm, BaseStationForm, BackhaulForm, SectorForm, CustomerForm, SubStationForm, CircuitForm
from device.models import Country, State, City
from django.contrib.staticfiles.templatetags.staticfiles import static
import logging
logger = logging.getLogger(__name__)


# **************************************** Inventory *********************************************
def inventory(request):
    return render(request, 'inventory/inventory.html')


class InventoryListing(ListView):
    model = Inventory
    template_name = 'inventory/inventory_list.html'

    def get_context_data(self, **kwargs):
        context = super(InventoryListing, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', },
            {'mData': 'user_group__name', 'sTitle': 'User Group', 'sWidth': 'null', },
            {'mData': 'organization__name', 'sTitle': 'Organization', 'sWidth': 'null', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'null', },]

        #if the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class InventoryListingTable(BaseDatatableView):
    model = Inventory
    columns = ['name', 'alias', 'user_group__name', 'organization__name', 'description']
    order_columns = ['name', 'alias', 'user_group__name', 'organization__name', 'description']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        organization_descendants_ids = self.request.user.userprofile.organization.get_descendants(
            include_self=True).values_list('id', flat=True)
        return Inventory.objects.filter(organization__in=organization_descendants_ids).values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/inventory/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                       <a href="/inventory/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))

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
            qs = list(qs)

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

    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(InventoryCreate.success_url)


class InventoryUpdate(UpdateView):
    template_name = 'inventory/inventory_update.html'
    model = Inventory
    form_class = InventoryForm
    success_url = reverse_lazy('InventoryList')

    @method_decorator(permission_required('inventory.change_inventory', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(InventoryUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(InventoryCreate.success_url)


class InventoryDelete(DeleteView):
    model = Inventory
    template_name = 'inventory/inventory_delete.html'
    success_url = reverse_lazy('InventoryList')

    @method_decorator(permission_required('inventory.delete_inventory', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(InventoryDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting inventory: %s' % (self.get_object().name))
        return super(InventoryDelete, self).delete(request, *args, **kwargs)


def inventory_details_wrt_organization(request):
    organization_id = request.GET['organization']
    organization_descendants_ids = Organization.objects.get(id=organization_id).get_descendants(
        include_self=True).values_list('id', flat=True)
    user_group = UserGroup.objects.filter(organization__in=organization_descendants_ids, is_deleted=0).values_list('id',
                                                                                                                   'name')
    device_groups = DeviceGroup.objects.filter(organization__in=organization_descendants_ids, is_deleted=0).values_list(
        'id', 'name')
    response_device_groups = response_user_group = ''
    for index in range(len(device_groups)):
        response_device_groups += '<option value={0}>{1}</option>'.format(*map(str, device_groups[index]))
    for index in range(len(user_group)):
        response_user_group += '<option value={0}>{1}</option>'.format(*map(str, user_group[index]))

    return HttpResponse(
        json.dumps({'response': {'device_groups': response_device_groups, 'user_groups': response_user_group}}), \
        mimetype='application/json')


#**************************************** Antenna *********************************************
class AntennaList(ListView):
    model = Antenna
    template_name = 'antenna/antenna_list.html'

    def get_context_data(self, **kwargs):
        context = super(AntennaList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', },
            {'mData': 'height', 'sTitle': 'Height', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'polarization', 'sTitle': 'Polarization', 'sWidth': 'null', },
            {'mData': 'tilt', 'sTitle': 'Tilt', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'beam_width', 'sTitle': 'Beam Width', 'sWidth': '10%', },
            {'mData': 'azimuth_angle', 'sTitle': 'Azimuth Angle', 'sWidth': '10%', }, ]

        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class AntennaListingTable(BaseDatatableView):
    model = Antenna
    columns = ['name', 'alias', 'height', 'polarization', 'tilt', 'beam_width', 'azimuth_angle']
    order_columns = ['name', 'alias', 'height', 'polarization', 'tilt', 'beam_width', 'azimuth_angle']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query
        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Antenna.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
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
            qs = list(qs)

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
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
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
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Antenna : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(AntennaUpdate.success_url)


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
        context = super(BaseStationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', },
            {'mData': 'bs_technology__alias', 'sTitle': 'Technology', 'sWidth': 'null', },
            {'mData': 'bs_site_id', 'sTitle': 'Site ID', 'sWidth': 'null', },
            {'mData': 'bs_switch__device_name', 'sTitle': 'BS Switch', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'backhaul__name', 'sTitle': 'Backhaul', 'sWidth': 'null', },
            {'mData': 'bs_type', 'sTitle': 'BS Type', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'building_height', 'sTitle': 'Building Height', 'sWidth': 'null', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class BaseStationListingTable(BaseDatatableView):
    model = BaseStation
    columns = ['name', 'alias', 'bs_technology__alias', 'bs_site_id',
               'bs_switch__device_name', 'backhaul__name', 'bs_type', 'building_height', 'description']
    order_columns = ['name', 'alias', 'bs_technology__alias', 'bs_site_id',
                     'bs_switch__device_name', 'backhaul__name', 'bs_type', 'building_height', 'description']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return BaseStation.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
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
            qs = list(qs)

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
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
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
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Base Station : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(BaseStationUpdate.success_url)


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
        context = super(BackhaulList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', },
            {'mData': 'bh_configured_on__device_name', 'sTitle': 'Backhaul Configured On', 'sWidth': 'null', },
            {'mData': 'bh_port', 'sTitle': 'Backhaul Port', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'bh_type', 'sTitle': 'Backhaul Type', 'sWidth': 'null', },
            {'mData': 'pop__device_name', 'sTitle': 'POP', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'pop_port', 'sTitle': 'POP Port', 'sWidth': 'null', },
            {'mData': 'bh_connectivity', 'sTitle': 'Connectivity', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'bh_circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'null', },
            {'mData': 'bh_capacity', 'sTitle': 'Capacity', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            ]

        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class BackhaulListingTable(BaseDatatableView):
    model = Backhaul
    columns = ['name', 'alias', 'bh_configured_on__device_name', 'bh_port', 'bh_type', 'pop__device_name', 'pop_port',
               'bh_connectivity', 'bh_circuit_id', 'bh_capacity']
    order_columns = ['name', 'alias', 'bh_configured_on__device_name', 'bh_port', 'bh_type', 'pop__device_name',
                     'pop_port', 'bh_connectivity', 'bh_circuit_id', 'bh_capacity']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Backhaul.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
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
            qs = list(qs)

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
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
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
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Backhaul : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(BackhaulUpdate.success_url)


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
        context = super(SectorList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', },
            {'mData': 'sector_id', 'sTitle': 'ID', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'sector_configured_on__device_name', 'sTitle': 'Sector Configured On', 'sWidth': 'null', },
            {'mData': 'sector_configured_on_port__name', 'sTitle': 'Sector Configured On Port', 'sWidth': 'null',
             'sClass': 'hidden-xs'},
            {'mData': 'antenna__name', 'sTitle': 'Antenna', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'mrc', 'sTitle': 'MRC', 'sWidth': 'null', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            ]

        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class SectorListingTable(BaseDatatableView):
    model = Sector
    columns = ['name', 'alias', 'sector_id', 'sector_configured_on__device_name',
               'sector_configured_on_port__name', 'antenna__name', 'mrc', 'description']
    order_columns = ['name', 'alias', 'sector_id', 'sector_configured_on__device_name',
               'sector_configured_on_port__name', 'antenna__name', 'mrc', 'description']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Sector.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
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
            qs = list(qs)

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
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
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
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Customer : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(SectorUpdate.success_url)


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
        context = super(CustomerList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', },
            {'mData': 'address', 'sTitle': 'Address', 'sWidth': 'null', 'sClass': 'hidden-xs','bSortable': False},
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'null', 'bSortable': False},
            ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class CustomerListingTable(BaseDatatableView):
    model = Customer
    columns = ['name', 'alias', 'address', 'description']
    order_columns = ['name', 'alias']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Customer.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
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
            qs = list(qs)

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
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
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
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Customer : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(CustomerUpdate.success_url)


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
        context = super(SubStationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', },
            {'mData': 'device__device_name', 'sTitle': 'Device', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'antenna__name', 'sTitle': 'Antenna', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'version', 'sTitle': 'Version', 'sWidth': 'null', },
            {'mData': 'serial_no', 'sTitle': 'Serial No.', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'building_height', 'sTitle': 'Building Height', 'sWidth': 'null', },
            {'mData': 'tower_height', 'sTitle': 'Tower Height', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'city__name', 'sTitle': 'City', 'sWidth': 'null', 'bSortable': False},
            {'mData': 'state__name', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs','bSortable': False},
            {'mData': 'address', 'sTitle': 'Address', 'sWidth': 'null', 'bSortable': False},
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'null', 'sClass': 'hidden-xs','bSortable': False},
            ]

        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class SubStationListingTable(BaseDatatableView):
    model = SubStation
    columns = ['name', 'alias', 'device__device_name', 'antenna__name', 'version', 'serial_no', 'building_height',
               'tower_height', 'city', 'state', 'address', 'description']
    order_columns = ['name', 'alias', 'device__device_name', 'antenna__name', 'version', 'serial_no', 'building_height',
                     'tower_height']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return SubStation.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct['city__name']= City.objects.get(pk=int(dct['city'])).city_name if dct['city'] else ''
            dct['state__name']= State.objects.get(pk=int(dct['state'])).state_name if dct['state'] else ''
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
            qs = list(qs)

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
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
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
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of SubStation : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(SubStationUpdate.success_url)


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
        context = super(CircuitList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', },
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'null'},
            {'mData': 'sector__base_station__name', 'sTitle': 'Base Station', 'sWidth': 'null'},
            {'mData': 'sector__name', 'sTitle': 'Sector', 'sWidth': 'null', },
            {'mData': 'customer__name', 'sTitle': 'Customer', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'sub_station__name', 'sTitle': 'Sub Station', 'sWidth': 'null', },
            {'mData': 'date_of_acceptance', 'sTitle': 'Date of Acceptance', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'null',  'sClass': 'hidden-xs'},
            ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class CircuitListingTable(BaseDatatableView):
    model = Circuit
    columns = ['name', 'alias', 'circuit_id','sector__base_station__name', 'sector__name', 'customer__name',
               'sub_station__name', 'date_of_acceptance', 'description']
    order_columns = ['name', 'alias', 'circuit_id','sector__base_station__name', 'sector__name', 'customer__name',
                     'sub_station__name', 'date_of_acceptance', 'description']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        break
            return result_list
        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Circuit.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/circuit/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/circuit/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')),
                date_of_acceptance=dct['date_of_acceptance'].strftime("%Y-%m-%d")
            )

        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()


        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # prepare output data
        qs = self.prepare_results(qs)
        aaData = self.filter_queryset(qs)
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
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
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
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Circuit : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(CircuitUpdate.success_url)


class CircuitDelete(DeleteView):
    model = Circuit
    template_name = 'circuit/circuit_delete.html'
    success_url = reverse_lazy('circuits_list')

    @method_decorator(permission_required('inventory.delete_circuit', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CircuitDelete, self).dispatch(*args, **kwargs)


#**************************************** IconSettings *********************************************
class IconSettingsList(ListView):
    model = IconSettings
    template_name = 'icon_settings/icon_settings_list.html'

    def get_context_data(self, **kwargs):
        context = super(IconSettingsList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name',             'sTitle': 'Name',               'sWidth': 'null'},
            {'mData': 'alias',            'sTitle': 'Alias',              'sWidth': 'null'},
            {'mData': 'upload_image',     'sTitle': 'Image',       'sWidth': 'null'},
            ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class IconSettingsListingTable(BaseDatatableView):
    model = IconSettings
    columns = ['name', 'alias', 'upload_image']
    order_columns = ['name', 'alias', 'upload_image']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return IconSettings.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            try:
                img_url = static('img/{}'.format(dct['upload_image']))
                dct.update(upload_image='<img src="{0}" style="float:left; display:block; height:25px; width:25px;">'.format(img_url))
            except Exception as e:
                logger.info(e)

            dct.update(actions='<a href="/icon_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/icon_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


class IconSettingsDetail(DetailView):
    model = IconSettings
    template_name = 'icon_settings/icon_settings_detail.html'


class IconSettingsCreate(CreateView):
    template_name = 'icon_settings/icon_settings_new.html'
    model = IconSettings
    form_class = IconSettingsForm
    success_url = reverse_lazy('icon_settings_list')

    @method_decorator(permission_required('inventory.add_icon_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(IconSettingsCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(IconSettingsCreate.success_url)


class IconSettingsUpdate(UpdateView):
    template_name = 'icon_settings/icon_settings_update.html'
    model = IconSettings
    form_class = IconSettingsForm
    success_url = reverse_lazy('icon_settings_list')

    @method_decorator(permission_required('inventory.change_icon_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(IconSettingsUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of IconSettings : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(IconSettingsUpdate.success_url)


class IconSettingsDelete(DeleteView):
    model = IconSettings
    template_name = 'icon_settings/icon_settings_delete.html'
    success_url = reverse_lazy('icon_settings_list')

    @method_decorator(permission_required('inventory.delete_icon_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(IconSettingsDelete, self).dispatch(*args, **kwargs)
    
    
#**************************************** LivePollingSettings *********************************************
class LivePollingSettingsList(ListView):
    model = LivePollingSettings
    template_name = 'live_polling_settings/live_polling_settings_list.html'

    def get_context_data(self, **kwargs):
        context = super(LivePollingSettingsList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name',                    'sTitle': 'Name',              'sWidth': 'null'},
            {'mData': 'alias',                   'sTitle': 'Alias',             'sWidth': 'null'},
            {'mData': 'technology__alias',       'sTitle': 'Technology',        'sWidth': 'null'},
            {'mData': 'service__alias',          'sTitle': 'Service',           'sWidth': 'null'},
            {'mData': 'data_source__alias',      'sTitle': 'Data Source',       'sWidth': 'null'},
            ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class LivePollingSettingsListingTable(BaseDatatableView):
    model = LivePollingSettings
    columns = ['name', 'alias', 'technology__alias', 'service__alias', 'data_source__alias']
    order_columns = ['name', 'alias', 'technology__alias', 'service__alias', 'data_source__alias']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return LivePollingSettings.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/live_polling_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/live_polling_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


class LivePollingSettingsDetail(DetailView):
    model = LivePollingSettings
    template_name = 'live_polling_settings/live_polling_settings_detail.html'


class LivePollingSettingsCreate(CreateView):
    template_name = 'live_polling_settings/live_polling_settings_new.html'
    model = LivePollingSettings
    form_class = LivePollingSettingsForm
    success_url = reverse_lazy('live_polling_settings_list')

    @method_decorator(permission_required('inventory.add_live_polling_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(LivePollingSettingsCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(LivePollingSettingsCreate.success_url)


class LivePollingSettingsUpdate(UpdateView):
    template_name = 'live_polling_settings/live_polling_settings_update.html'
    model = LivePollingSettings
    form_class = LivePollingSettingsForm
    success_url = reverse_lazy('live_polling_settings_list')

    @method_decorator(permission_required('inventory.change_live_polling_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(LivePollingSettingsUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of LivePollingSettings : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(LivePollingSettingsUpdate.success_url)


class LivePollingSettingsDelete(DeleteView):
    model = LivePollingSettings
    template_name = 'live_polling_settings/live_polling_settings_delete.html'
    success_url = reverse_lazy('live_polling_settings_list')

    @method_decorator(permission_required('inventory.delete_live_polling_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(LivePollingSettingsDelete, self).dispatch(*args, **kwargs)


#**************************************** ThresholdConfiguration *********************************************
class ThresholdConfigurationList(ListView):
    model = ThresholdConfiguration
    template_name = 'threshold_configuration/threshold_configuration_list.html'

    def get_context_data(self, **kwargs):
        context = super(ThresholdConfigurationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name',                           'sTitle': 'Name',                   'sWidth': 'null'},
            {'mData': 'alias',                          'sTitle': 'Alias',                  'sWidth': 'null'},
            {'mData': 'live_polling_template__alias',   'sTitle': 'Live Polling Template',  'sWidth': 'null'},
            {'mData': 'warning',                        'sTitle': 'Warning',                'sWidth': 'null'},
            {'mData': 'critical',                       'sTitle': 'Critical',               'sWidth': 'null'},
            ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ThresholdConfigurationListingTable(BaseDatatableView):
    model = ThresholdConfiguration
    columns = ['name', 'alias', 'live_polling_template__alias', 'warning', 'critical']
    order_columns = ['name', 'alias', 'live_polling_template__alias', 'warning', 'critical']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return ThresholdConfiguration.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/threshold_configuration/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/threshold_configuration/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


class ThresholdConfigurationDetail(DetailView):
    model = ThresholdConfiguration
    template_name = 'threshold_configuration/threshold_configuration_detail.html'


class ThresholdConfigurationCreate(CreateView):
    template_name = 'threshold_configuration/threshold_configuration_new.html'
    model = ThresholdConfiguration
    form_class = ThresholdConfigurationForm
    success_url = reverse_lazy('threshold_configuration_list')

    @method_decorator(permission_required('inventory.add_threshold_configuration', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ThresholdConfigurationCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(ThresholdConfigurationCreate.success_url)


class ThresholdConfigurationUpdate(UpdateView):
    template_name = 'threshold_configuration/threshold_configuration_update.html'
    model = ThresholdConfiguration
    form_class = ThresholdConfigurationForm
    success_url = reverse_lazy('threshold_configuration_list')

    @method_decorator(permission_required('inventory.change_threshold_configuration', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ThresholdConfigurationUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of ThresholdConfiguration : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(ThresholdConfigurationUpdate.success_url)


class ThresholdConfigurationDelete(DeleteView):
    model = ThresholdConfiguration
    template_name = 'threshold_configuration/threshold_configuration_delete.html'
    success_url = reverse_lazy('threshold_configuration_list')

    @method_decorator(permission_required('inventory.delete_threshold_configuration', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ThresholdConfigurationDelete, self).dispatch(*args, **kwargs)


#**************************************** ThematicSettings *********************************************
class ThematicSettingsList(ListView):
    model = ThematicSettings
    template_name = 'thematic_settings/thematic_settings_list.html'

    def get_context_data(self, **kwargs):
        context = super(ThematicSettingsList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name',                    'sTitle': 'Name',                      'sWidth': 'null'},
            {'mData': 'alias',                   'sTitle': 'Alias',                     'sWidth': 'null'},
            {'mData': 'threshold_template',      'sTitle': 'Threshold Template',        'sWidth': 'null'},
            {'mData': 'gt_warning__name',        'sTitle': '> Warning',                 'sWidth': 'null'},
            {'mData': 'bt_w_c__name',            'sTitle': 'Warning > > Critical',      'sWidth': 'null'},
            {'mData': 'gt_critical__name',       'sTitle': '> Critical',                'sWidth': 'null'},
            ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ThematicSettingsListingTable(BaseDatatableView):
    model = ThematicSettings
    columns = ['name', 'alias', 'threshold_template', 'gt_warning__name', 'bt_w_c__name', 'gt_critical__name']
    order_columns = ['name', 'alias', 'threshold_template', 'gt_warning__name', 'bt_w_c__name', 'gt_critical__name']
    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return ThematicSettings.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/thematic_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/thematic_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


class ThematicSettingsDetail(DetailView):
    model = ThematicSettings
    template_name = 'thematic_settings/thematic_settings_detail.html'


class ThematicSettingsCreate(CreateView):
    template_name = 'thematic_settings/thematic_settings_new.html'
    model = ThematicSettings
    form_class = ThematicSettingsForm
    success_url = reverse_lazy('thematic_settings_list')

    @method_decorator(permission_required('inventory.add_thematic_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ThematicSettingsCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(ThematicSettingsCreate.success_url)


class ThematicSettingsUpdate(UpdateView):
    template_name = 'thematic_settings/thematic_settings_update.html'
    model = ThematicSettings
    form_class = ThematicSettingsForm
    success_url = reverse_lazy('thematic_settings_list')

    @method_decorator(permission_required('inventory.change_thematic_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ThematicSettingsUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of ThematicSettings : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(ThematicSettingsUpdate.success_url)


class ThematicSettingsDelete(DeleteView):
    model = ThematicSettings
    template_name = 'thematic_settings/thematic_settings_delete.html'
    success_url = reverse_lazy('thematic_settings_list')

    @method_decorator(permission_required('inventory.delete_thematic_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ThematicSettingsDelete, self).dispatch(*args, **kwargs)
