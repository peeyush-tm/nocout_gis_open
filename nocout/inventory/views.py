from operator import itemgetter
import re
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
import json
from actstream import action
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from device_group.models import DeviceGroup
from nocout.utils.util import DictDiffer
from models import Inventory, IconSettings, LivePollingSettings, ThresholdConfiguration, ThematicSettings
from forms import InventoryForm, IconSettingsForm, LivePollingSettingsForm, ThresholdConfigurationForm, \
    ThematicSettingsForm, GISInventoryBulkImportForm
from organization.models import Organization
from user_group.models import UserGroup
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit
from forms import AntennaForm, BaseStationForm, BackhaulForm, SectorForm, CustomerForm, SubStationForm, CircuitForm
from device.models import Country, State, City
from django.contrib.staticfiles.templatetags.staticfiles import static
import xlrd
import logging
logger = logging.getLogger(__name__)


# **************************************** Inventory *********************************************
def inventory(request):
    """
    Render the inventory page.
    """
    return render(request, 'inventory/inventory.html')


class InventoryListing(ListView):
    """
    Class Based Inventory View to render list page.
    """
    model = Inventory
    template_name = 'inventory/inventory_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
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
    """
    Class based View to render Inventory Data table.
    """

    model = Inventory
    columns = ['name', 'alias', 'user_group__name', 'organization__name', 'description']
    order_columns = ['name', 'alias', 'user_group__name', 'organization__name', 'description']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        organization_descendants_ids = self.request.user.userprofile.organization.get_descendants(
            include_self=True).values_list('id', flat=True)
        return Inventory.objects.filter(organization__in=organization_descendants_ids).values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/inventory/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                       <a href="/inventory/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))

        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
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
    """
    Class based view to create new Inventory.
    """

    template_name = 'inventory/inventory_new.html'
    model = Inventory
    form_class = InventoryForm
    success_url = reverse_lazy('InventoryList')

    @method_decorator(permission_required('inventory.add_inventory', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(InventoryCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(InventoryCreate.success_url)


class InventoryUpdate(UpdateView):
    """
    Class based view to update new Inventory.
    """
    template_name = 'inventory/inventory_update.html'
    model = Inventory
    form_class = InventoryForm
    success_url = reverse_lazy('InventoryList')

    @method_decorator(permission_required('inventory.change_inventory', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(InventoryUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(InventoryCreate.success_url)


class InventoryDelete(DeleteView):
    """
    Class based View to delete the Inventory

    """
    model = Inventory
    template_name = 'inventory/inventory_delete.html'
    success_url = reverse_lazy('InventoryList')

    @method_decorator(permission_required('inventory.delete_inventory', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(InventoryDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        overriding the delete method to log the user activity.
        """
        action.send(request.user, verb='deleting inventory: %s' % (self.get_object().name))
        return super(InventoryDelete, self).delete(request, *args, **kwargs)


def inventory_details_wrt_organization(request):
    """
    Inventory details organization as a get organization parameter.
    """
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
    """
    Class based view to render Antenna list page.
    """
    model = Antenna
    template_name = 'antenna/antenna_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
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
    """
    Class based View to render Antenna Data table.
    """
    model = Antenna
    columns = ['name', 'alias', 'height', 'polarization', 'tilt', 'beam_width', 'azimuth_angle']
    order_columns = ['name', 'alias', 'height', 'polarization', 'tilt', 'beam_width', 'azimuth_angle']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:

        """
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
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Antenna.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/antenna/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/antenna/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
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
    """
    Class based view to render the antenna detail.
    """
    model = Antenna
    template_name = 'antenna/antenna_detail.html'


class AntennaCreate(CreateView):
    """
    Class based view to create new Antenna.
    """
    template_name = 'antenna/antenna_new.html'
    model = Antenna
    form_class = AntennaForm
    success_url = reverse_lazy('antennas_list')

    @method_decorator(permission_required('inventory.add_antenna', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(AntennaCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(AntennaCreate.success_url)


class AntennaUpdate(UpdateView):
    """
    Class based view to update Antenna .
    """
    template_name = 'antenna/antenna_update.html'
    model = Antenna
    form_class = AntennaForm
    success_url = reverse_lazy('antennas_list')

    @method_decorator(permission_required('inventory.change_antenna', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(AntennaUpdate, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the Antenna.
    """
    model = Antenna
    template_name = 'antenna/antenna_delete.html'
    success_url = reverse_lazy('antennas_list')

    @method_decorator(permission_required('inventory.delete_antenna', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(AntennaDelete, self).dispatch(*args, **kwargs)


#****************************************** Base Station ********************************************
class BaseStationList(ListView):
    """
    Class based View to render Base Station Data table.
    """
    model = BaseStation
    template_name = 'base_station/base_stations_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(BaseStationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', },
            # {'mData': 'bs_technology__alias', 'sTitle': 'Technology', 'sWidth': 'null', },
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
    """
    Class based View to render Base Station Data table.
    """
    model = BaseStation
    columns = ['name', 'alias', 'bs_site_id',
               'bs_switch__device_name', 'backhaul__name', 'bs_type', 'building_height', 'description']
    order_columns = ['name', 'alias', 'bs_site_id',
                     'bs_switch__device_name', 'backhaul__name', 'bs_type', 'building_height', 'description']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
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
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return BaseStation.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/base_station/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/base_station/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
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
    """
    Class based view to render the Base Station detail.
    """
    model = BaseStation
    template_name = 'base_station/base_station_detail.html'


class BaseStationCreate(CreateView):
    """
    Class based view to create new Base Station.
    """
    template_name = 'base_station/base_station_new.html'
    model = BaseStation
    form_class = BaseStationForm
    success_url = reverse_lazy('base_stations_list')

    @method_decorator(permission_required('inventory.add_basestation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(BaseStationCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(BaseStationCreate.success_url)


class BaseStationUpdate(UpdateView):
    """
    Class based view to update Base Station.
    """
    template_name = 'base_station/base_station_update.html'
    model = BaseStation
    form_class = BaseStationForm
    success_url = reverse_lazy('base_stations_list')

    @method_decorator(permission_required('inventory.change_basestation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(BaseStationUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the Base Station.
    """
    model = BaseStation
    template_name = 'base_station/base_station_delete.html'
    success_url = reverse_lazy('base_stations_list')

    @method_decorator(permission_required('inventory.delete_basestation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(BaseStationDelete, self).dispatch(*args, **kwargs)


#**************************************** Backhaul *********************************************
class BackhaulList(ListView):
    """
    Class based View to render Backhaul Listing page..
    """
    model = Backhaul
    template_name = 'backhaul/backhauls_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
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
    """
    Class based View to render Backhaul Data table.
    """
    model = Backhaul
    columns = ['name', 'alias', 'bh_configured_on__device_name', 'bh_port', 'bh_type', 'pop__device_name', 'pop_port',
               'bh_connectivity', 'bh_circuit_id', 'bh_capacity']
    order_columns = ['name', 'alias', 'bh_configured_on__device_name', 'bh_port', 'bh_type', 'pop__device_name',
                     'pop_port', 'bh_connectivity', 'bh_circuit_id', 'bh_capacity']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:

        """
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
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Backhaul.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/backhaul/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/backhaul/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
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
    """
    Class based view to render the Backhaul detail.
    """
    model = Backhaul
    template_name = 'backhaul/backhaul_detail.html'


class BackhaulCreate(CreateView):
    """
    Class based view to create new backhaul..
    """
    template_name = 'backhaul/backhaul_new.html'
    model = Backhaul
    form_class = BackhaulForm
    success_url = reverse_lazy('backhauls_list')

    @method_decorator(permission_required('inventory.add_backhaul', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(BackhaulCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(BackhaulCreate.success_url)


class BackhaulUpdate(UpdateView):
    """
    Class based view to update Backhaul.
    """
    template_name = 'backhaul/backhaul_update.html'
    model = Backhaul
    form_class = BackhaulForm
    success_url = reverse_lazy('backhauls_list')

    @method_decorator(permission_required('inventory.change_backhaul', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(BackhaulUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the Backhaul.
    """
    model = Backhaul
    template_name = 'backhaul/backhaul_delete.html'
    success_url = reverse_lazy('backhauls_list')

    @method_decorator(permission_required('inventory.delete_backhaul', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(BackhaulDelete, self).dispatch(*args, **kwargs)


#**************************************** Sector *********************************************
class SectorList(ListView):
    """
    Class Based View to render Sector List Page.
    """
    model = Sector
    template_name = 'sector/sectors_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(SectorList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', },
            {'mData': 'bs_technology__alias', 'sTitle': 'Technology', 'sWidth': 'null', },
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
    """
    Class based View to render Sector Data Table.
    """
    model = Sector
    columns = ['name', 'alias', 'bs_technology__alias' ,'sector_id', 'sector_configured_on__device_name',
               'sector_configured_on_port__name', 'antenna__name', 'mrc', 'description']
    order_columns = ['name', 'alias', 'bs_technology__alias' ,'sector_id', 'sector_configured_on__device_name',
               'sector_configured_on_port__name', 'antenna__name', 'mrc', 'description']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:

        """
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
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Sector.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/sector/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/sector/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
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
    """
    Class based view to render the Sector detail.
    """
    model = Sector
    template_name = 'sector/sector_detail.html'


class SectorCreate(CreateView):
    """
    Class based view to create new Sector.
    """
    template_name = 'sector/sector_new.html'
    model = Sector
    form_class = SectorForm
    success_url = reverse_lazy('sectors_list')

    @method_decorator(permission_required('inventory.add_sector', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(SectorCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(SectorCreate.success_url)


class SectorUpdate(UpdateView):
    """
    Class based view to update Sector.
    """
    template_name = 'sector/sector_update.html'
    model = Sector
    form_class = SectorForm
    success_url = reverse_lazy('sectors_list')

    @method_decorator(permission_required('inventory.change_sector', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(SectorUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the Sector.
    """
    model = Sector
    template_name = 'sector/sector_delete.html'
    success_url = reverse_lazy('sectors_list')

    @method_decorator(permission_required('inventory.delete_sector', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(SectorDelete, self).dispatch(*args, **kwargs)


#**************************************** Customer *********************************************
class CustomerList(ListView):
    """
    Class based View to render Customer listing page.
    """
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
    """
    Class based View to render Customer Data table.
    """
    model = Customer
    columns = ['name', 'alias', 'address', 'description']
    order_columns = ['name', 'alias']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:

        """
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
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Customer.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/customer/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/customer/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """

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
    """
    Class based view to render the customer detail.
    """
    model = Customer
    template_name = 'customer/customer_detail.html'


class CustomerCreate(CreateView):
    """
    Class based view to create new customer.
    """
    template_name = 'customer/customer_new.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customers_list')

    @method_decorator(permission_required('inventory.add_customer', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(CustomerCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(CustomerCreate.success_url)


class CustomerUpdate(UpdateView):
    """
    Class based view to update Customer.
    """
    template_name = 'customer/customer_update.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customers_list')

    @method_decorator(permission_required('inventory.change_customer', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(CustomerUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the Customer.
    """
    model = Customer
    template_name = 'customer/customer_delete.html'
    success_url = reverse_lazy('customers_list')

    @method_decorator(permission_required('inventory.delete_customer', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(CustomerDelete, self).dispatch(*args, **kwargs)


#**************************************** Sub Station *********************************************
class SubStationList(ListView):
    """
    Class Based View to render Sub Station List Page.
    """
    model = SubStation
    template_name = 'sub_station/sub_stations_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
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
    """
    Class based View to render Sub Station Data table.
    """
    model = SubStation
    columns = ['name', 'alias', 'device__device_name', 'antenna__name', 'version', 'serial_no', 'building_height',
               'tower_height', 'city', 'state', 'address', 'description']
    order_columns = ['name', 'alias', 'device__device_name', 'antenna__name', 'version', 'serial_no', 'building_height',
                     'tower_height']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:

        """
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
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return SubStation.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct['city__name']= City.objects.get(pk=int(dct['city'])).city_name if dct['city'] else ''
            dct['state__name']= State.objects.get(pk=int(dct['state'])).state_name if dct['state'] else ''
            dct.update(actions='<a href="/sub_station/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/sub_station/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
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
    """
    Class based view to render the Sub Station detail.
    """
    model = SubStation
    template_name = 'sub_station/sub_station_detail.html'


class SubStationCreate(CreateView):
    """
    Class based view to create new Sub Station.
    """
    template_name = 'sub_station/sub_station_new.html'
    model = SubStation
    form_class = SubStationForm
    success_url = reverse_lazy('sub_stations_list')

    @method_decorator(permission_required('inventory.add_substation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(SubStationCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(SubStationCreate.success_url)


class SubStationUpdate(UpdateView):
    """
    Class based view to update the Sub Station.
    """
    template_name = 'sub_station/sub_station_update.html'
    model = SubStation
    form_class = SubStationForm
    success_url = reverse_lazy('sub_stations_list')

    @method_decorator(permission_required('inventory.change_substation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(SubStationUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the Sub Station.
    """
    model = SubStation
    template_name = 'sub_station/sub_station_delete.html'
    success_url = reverse_lazy('sub_stations_list')

    @method_decorator(permission_required('inventory.delete_substation', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(SubStationDelete, self).dispatch(*args, **kwargs)


#**************************************** Circuit *********************************************
class CircuitList(ListView):
    """
    Class Based View to render Circuit List Page.
    """
    model = Circuit
    template_name = 'circuit/circuits_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
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
    """
    Class based View to render Circuit Data table.
    """
    model = Circuit
    columns = ['name', 'alias', 'circuit_id','sector__base_station__name', 'sector__name', 'customer__name',
               'sub_station__name', 'date_of_acceptance', 'description']
    order_columns = ['name', 'alias', 'circuit_id','sector__base_station__name', 'sector__name', 'customer__name',
                     'sub_station__name', 'date_of_acceptance', 'description']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        :param qs:
        :return qs:

        """
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
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Circuit.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/circuit/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/circuit/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')),
                       date_of_acceptance=dct['date_of_acceptance'].strftime("%Y-%m-%d") if dct['date_of_acceptance'] != "" else "")

        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        request = self.request
        # Number of columns that are used in sorting
        try:
            i_sorting_cols = int(request.REQUEST.get('iSortingCols', 0))
        except ValueError:
            i_sorting_cols = 0

        order = []
        order_columns = self.get_order_columns()
        for i in range(i_sorting_cols):
            # sorting column
            try:
                i_sort_col = int(request.REQUEST.get('iSortCol_%s' % i))
            except ValueError:
                i_sort_col = 0
            # sorting order
            s_sort_dir = request.REQUEST.get('sSortDir_%s' % i)

            sdir = '-' if s_sort_dir == 'desc' else ''

            sortcol = order_columns[i_sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            key_name=order[0][1:] if '-' in order[0] else order[0]
            sorted_device_data = sorted(qs, key=itemgetter(key_name), reverse= True if '-' in order[0] else False)
            return sorted_device_data
        return qs


    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)
        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


class CircuitDetail(DetailView):
    """
    Class based view to render the Circuit detail.
    """
    model = Circuit
    template_name = 'circuit/circuit_detail.html'


class CircuitCreate(CreateView):
    """
    Class based view to create new Circuit.
    """

    template_name = 'circuit/circuit_new.html'
    model = Circuit
    form_class = CircuitForm
    success_url = reverse_lazy('circuits_list')

    @method_decorator(permission_required('inventory.add_circuit', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(CircuitCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(CircuitCreate.success_url)


class CircuitUpdate(UpdateView):
    """
    Class based view to update Cicuit.
    """
    template_name = 'circuit/circuit_update.html'
    model = Circuit
    form_class = CircuitForm
    success_url = reverse_lazy('circuits_list')

    @method_decorator(permission_required('inventory.change_circuit', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(CircuitUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the Circuit.
    """
    model = Circuit
    template_name = 'circuit/circuit_delete.html'
    success_url = reverse_lazy('circuits_list')

    @method_decorator(permission_required('inventory.delete_circuit', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(CircuitDelete, self).dispatch(*args, **kwargs)


#**************************************** IconSettings *********************************************
class IconSettingsList(ListView):
    """
    Class Based View to render IconSettings List Page.
    """
    model = IconSettings
    template_name = 'icon_settings/icon_settings_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
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
    """
    Class based View to render IconSettings Data table.
    """
    model = IconSettings
    columns = ['name', 'alias', 'upload_image']
    order_columns = ['name', 'alias', 'upload_image']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return IconSettings.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            try:
                img_url = "/media/"+ (dct['upload_image']) if \
                    "uploaded" in dct['upload_image'] \
                    else static("img/" + dct['upload_image'])
                dct.update(upload_image='<img src="{0}" style="float:left; display:block; height:25px; width:25px;">'.format(img_url))
            except Exception as e:
                logger.info(e)

            dct.update(actions='<a href="/icon_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/icon_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
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
    """
    Class based view to render the IconSettings detail.
    """
    model = IconSettings
    template_name = 'icon_settings/icon_settings_detail.html'


class IconSettingsCreate(CreateView):
    """
    Class based view to create new IconSettings.
    """
    template_name = 'icon_settings/icon_settings_new.html'
    model = IconSettings
    form_class = IconSettingsForm
    success_url = reverse_lazy('icon_settings_list')

    @method_decorator(permission_required('inventory.add_icon_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(IconSettingsCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(IconSettingsCreate.success_url)


class IconSettingsUpdate(UpdateView):
    """
    Class based view to update IconSettings.
    """
    template_name = 'icon_settings/icon_settings_update.html'
    model = IconSettings
    form_class = IconSettingsForm
    success_url = reverse_lazy('icon_settings_list')

    @method_decorator(permission_required('inventory.change_icon_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(IconSettingsUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the machine
    """
    model = IconSettings
    template_name = 'icon_settings/icon_settings_delete.html'
    success_url = reverse_lazy('icon_settings_list')

    @method_decorator(permission_required('inventory.delete_icon_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(IconSettingsDelete, self).dispatch(*args, **kwargs)
    
    
#**************************************** LivePollingSettings *********************************************
class LivePollingSettingsList(ListView):
    """
    Class Based View to render LivePollingSettings List Page.
    """
    model = LivePollingSettings
    template_name = 'live_polling_settings/live_polling_settings_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
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
    """
    Class based View to render LivePollingSettings Data table.
    """
    model = LivePollingSettings
    columns = ['name', 'alias', 'technology__alias', 'service__alias', 'data_source__alias']
    order_columns = ['name', 'alias', 'technology__alias', 'service__alias', 'data_source__alias']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
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
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return LivePollingSettings.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/live_polling_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/live_polling_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
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
    """
    Class based view to render the LivePollingSettings detail.
    """
    model = LivePollingSettings
    template_name = 'live_polling_settings/live_polling_settings_detail.html'


class LivePollingSettingsCreate(CreateView):
    """
    Class based view to create new LivePollingSettings.
    """
    template_name = 'live_polling_settings/live_polling_settings_new.html'
    model = LivePollingSettings
    form_class = LivePollingSettingsForm
    success_url = reverse_lazy('live_polling_settings_list')

    @method_decorator(permission_required('inventory.add_live_polling_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(LivePollingSettingsCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(LivePollingSettingsCreate.success_url)


class LivePollingSettingsUpdate(UpdateView):
    """
    Class based view to update LivePollingSettings.
    """
    template_name = 'live_polling_settings/live_polling_settings_update.html'
    model = LivePollingSettings
    form_class = LivePollingSettingsForm
    success_url = reverse_lazy('live_polling_settings_list')

    @method_decorator(permission_required('inventory.change_live_polling_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(LivePollingSettingsUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the LivePollingSettings
    """
    model = LivePollingSettings
    template_name = 'live_polling_settings/live_polling_settings_delete.html'
    success_url = reverse_lazy('live_polling_settings_list')

    @method_decorator(permission_required('inventory.delete_live_polling_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(LivePollingSettingsDelete, self).dispatch(*args, **kwargs)


#**************************************** ThresholdConfiguration *********************************************
class ThresholdConfigurationList(ListView):
    """
    Class Based View to render ThresholdConfiguration List Page.
    """
    model = ThresholdConfiguration
    template_name = 'threshold_configuration/threshold_configuration_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
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
    """
    Class based View to render ThresholdConfiguration Data table.
    """
    model = ThresholdConfiguration
    columns = ['name', 'alias', 'live_polling_template__alias', 'warning', 'critical']
    order_columns = ['name', 'alias', 'live_polling_template__alias', 'warning', 'critical']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
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
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return ThresholdConfiguration.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/threshold_configuration/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/threshold_configuration/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
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
    """
    Class based view to render the Threshold Configuration detail.
    """
    model = ThresholdConfiguration
    template_name = 'threshold_configuration/threshold_configuration_detail.html'


class ThresholdConfigurationCreate(CreateView):
    """
    Class based view to create new Threshold Configuration.
    """
    template_name = 'threshold_configuration/threshold_configuration_new.html'
    model = ThresholdConfiguration
    form_class = ThresholdConfigurationForm
    success_url = reverse_lazy('threshold_configuration_list')

    @method_decorator(permission_required('inventory.add_threshold_configuration', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(ThresholdConfigurationCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(ThresholdConfigurationCreate.success_url)


class ThresholdConfigurationUpdate(UpdateView):
    """
    Class based view to update Threshold Configuration.
    """
    template_name = 'threshold_configuration/threshold_configuration_update.html'
    model = ThresholdConfiguration
    form_class = ThresholdConfigurationForm
    success_url = reverse_lazy('threshold_configuration_list')

    @method_decorator(permission_required('inventory.change_threshold_configuration', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(ThresholdConfigurationUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the Threshold Configuration.
    """
    model = ThresholdConfiguration
    template_name = 'threshold_configuration/threshold_configuration_delete.html'
    success_url = reverse_lazy('threshold_configuration_list')

    @method_decorator(permission_required('inventory.delete_threshold_configuration', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(ThresholdConfigurationDelete, self).dispatch(*args, **kwargs)


#**************************************** ThematicSettings *********************************************
class ThematicSettingsList(ListView):
    """
    Class Based View to render ThematicSettings List Page.
    """
    model = ThematicSettings
    template_name = 'thematic_settings/thematic_settings_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
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
    """
    Class based View to render Thematic Settings Data table.
    """
    model = ThematicSettings
    columns = ['name', 'alias', 'threshold_template', 'gt_warning__name', 'bt_w_c__name', 'gt_critical__name']
    order_columns = ['name', 'alias', 'threshold_template', 'gt_warning__name', 'bt_w_c__name', 'gt_critical__name']
    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:

        """
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
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return ThematicSettings.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/thematic_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/thematic_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
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
    """
    Class based view to render the Thematic Settings detail.
    """
    model = ThematicSettings
    template_name = 'thematic_settings/thematic_settings_detail.html'


class ThematicSettingsCreate(CreateView):
    """
    Class based view to create new ThematicSettings.
    """
    template_name = 'thematic_settings/thematic_settings_new.html'
    model = ThematicSettings
    form_class = ThematicSettingsForm
    success_url = reverse_lazy('thematic_settings_list')

    @method_decorator(permission_required('inventory.add_thematic_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(ThematicSettingsCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(ThematicSettingsCreate.success_url)


class ThematicSettingsUpdate(UpdateView):
    """
    Class based view to update Thematic Settings.
    """
    template_name = 'thematic_settings/thematic_settings_update.html'
    model = ThematicSettings
    form_class = ThematicSettingsForm
    success_url = reverse_lazy('thematic_settings_list')

    @method_decorator(permission_required('inventory.change_thematic_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(ThematicSettingsUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
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
    """
    Class based View to delete the Thematic Settings.
    """
    model = ThematicSettings
    template_name = 'thematic_settings/thematic_settings_delete.html'
    success_url = reverse_lazy('thematic_settings_list')

    @method_decorator(permission_required('inventory.delete_thematic_settings', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(ThematicSettingsDelete, self).dispatch(*args, **kwargs)


#************************************ GIS Inventory Bulk Upload ******************************************
class GISInventoryBulkImport(FormView):
    template_name = 'bulk_import/gis_bulk_import.html'
    success_url = '/bulk_import/gis_inventory/'
    form_class = GISInventoryBulkImportForm

    def form_valid(self, form):
        print "************************ form_valid **********************", form
        uploaded_file = self.request.FILES['file_upload']

        # dictionary containing all 'pts bs' fields
        ptp_bs_fields = ['City', 'State', 'Ckt ID', 'Circuit Type', 'Customer Name', 'BS Address', 'BS Name',
                         'Qos(BW)', 'Latitude', 'Longititude', 'Antenna height', 'Polarisation', 'Antenna Type',
                         'Antena Gain', 'Antenna mount type', 'Ethernet Extender', 'Building height',
                         'Tower/Pole height', 'Cable Length', 'RSSI during acceptance',
                         'Throughput during acceptance', 'Date of acceptance', 'BH BSO', 'IP', 'MAC', 'HSSU used',
                         'BS Switch IP', 'Aggregation Switch', 'Aggregation Switch Port', 'BS Converter IP',
                         'POP Converter IP', 'Converter Type', 'BH Configured On Switch/Converter',
                         'Switch/Converter Port', 'BH Capacity', 'BH Offnet/Onnet', 'Backhaul Type',
                         'BH Circuit ID', 'PE Hostname', 'PE IP', 'TTSL CIRCUIT ID']

        # dictionary containing all 'pmp bs' fields
        pmp_bs_fields = ['City', 'State', 'Address', 'BS Name', 'Type_Of_BS(Technology)', 'Site_Type',
                         'Infra Provider', 'Site ID', 'Building_Height', 'Tower_Height', 'Latitude', 'Longitude',
                         'ODU IP', 'Sector_name', 'Make of Antenna', 'Antenna Polarisation', 'Antenna_Tilt',
                         'Antenna_Height', 'Antenna_BeamWidth', 'Azimuth', 'Sync Splitter Used(Y/N)',
                         'Type of GPS', 'BS Switch IP', 'Aggregation Switch', 'Aggregation Switch Port',
                         'BS Converter IP', 'POP Converter IP', 'Converter Type', 'BH Configured On Switch/Converter',
                         'Switch/Converter Port', 'BH Capacity', 'BH Offnet/Onnet', 'Backhaul Type', 'BH Circuit ID',
                         'PE Hostname', 'PE IP', 'DR site', 'TTSL CIRCUIT ID']

        # dictionary containing all 'wimax bs' fields
        wimax_bs_fields = ['City', 'State', 'Address', 'BS Name', 'Type_Of_BS(Technology)', 'Site_Type',
                           'Infra Provider', 'Site ID', 'Building_Height', 'Tower_Height', 'Latitude', 'Longitude',
                           'IDU IP', 'Sector_name', 'PMP', 'Make of Antenna', 'Antenna Polarisation', 'Antenna_Tilt',
                           'Antenna_Height', 'Antenna_BeamWidth', 'Azimuth', 'Installation of Splitter',
                           'Type of GPS', 'BS Switch IP', 'Aggregation Switch', 'Aggregation Switch Port',
                           'BS Converter IP', 'POP Converter IP', 'Converter Type', 'BH Configured On Switch/Converter',
                           'Switch/Converter Port', 'BH Capacity', 'BH Offnet/Onnet', 'Backhaul Type', 'BH Circuit ID',
                           'PE Hostname', 'PE IP', 'DR site', 'TTSL CIRCUIT ID']

        # dictionary containing all 'ptp ss' fields
        ptp_ss_fields = ['City', 'State', 'Ckt ID', 'Customer Name', 'Customer Address', 'BS NAME', 'Qos(BW)',
                         'Latitide', 'Longitude', 'MIMO/Diversity', 'Antenna height', 'Polarisation', 'Antenna Type',
                         'Antena Gain', 'Antenna mount type', 'Ethernet Extender', 'Building height',
                         'Tower/Pole height', 'Cable Length', 'RSSI during acceptance', 'Throughput during acceptance',
                         'Date of acceptance', 'BH BSO', 'IP', 'MAC']

        # dictionary containing all 'pmp ss' fields
        pmp_ss_fields = ['Customer Name', 'Ckt ID', 'Qos(BW)', 'Latitude', 'Longitude', 'Building height',
                         'Tower/Pole height', 'Antenna height', 'Polarisation', 'Antenna Type', 'SS mount type',
                         'Ethernet Extender', 'Cable Length', 'DL RSSI during acceptance', 'DL CINR during acceptance',
                         'Customer Address', 'Date of acceptance', 'SS IP', 'Lens/Reflector', 'Antenna Beamwidth']

        # dictionary containing all 'wimax ss' fields
        wimax_ss_fields = ['Customer Name', 'Ckt ID', 'Qos(BW)', 'Latitude', 'Longitude', 'Building height',
                           'Tower/Pole height', 'Antenna height', 'Polarisation(Horizontal/Vertical)',
                           'Antenna Type(Narrowbeam/Normal)', 'SS mount type (Wallmount/pole mount/Mast)',
                           'Ethernet Extender(Yes/no)', 'Cable Length', 'DL RSSI during acceptance',
                           'DL CINR during acceptance', 'Customer Address', 'Date of acceptance', 'SS IP']

        bs_sheet = ""
        ss_sheet = ""
        ptp_sheet = ""

        try:
            bs_sheet = str(self.request.POST['bs_sheet'])
            ss_sheet = str(self.request.POST['ss_sheet'])
            ptp_sheet = str(self.request.POST['ptp_sheet'])
        except Exception as e:
            logger.info(e.message)

        print "***************** bs_sheet - ", bs_sheet
        print "***************** ss_sheet - ", ss_sheet
        print "***************** ptp_sheet - ", ptp_sheet
        book = xlrd.open_workbook(uploaded_file.name, file_contents=uploaded_file.read())

        if bs_sheet and ss_sheet:
            sheet = book.sheet_by_name(bs_sheet)
            print "***************** sheet - ", sheet
            print "***************** no. of rows - ", sheet.nrows
            print "***************** 1st row - ", sheet.row(0)
            keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
            print "&&&&&&&&&&&&&&&&&"
            print len(keys)
            print "&&&&&&&&&&&&&&&&&"
            keys_list = [str(x) for x in keys]
            print keys_list
            valid_rows_list = []
            invalid_rows_list = []
            for row_index in xrange(1, sheet.nrows):
                d = {keys[col_index]: sheet.cell(row_index, col_index).value
                     for col_index in xrange(sheet.ncols)}
                # print "***************************************************"
                # print str(d['Make of Antenna'])
                # print "***************************************************"
                city = d['City']
                state = d['State']
                address = d['Address']
                bs_name = d['BS Name']
                type_of_bs = d['Type_Of_BS(Technology)']
                site_type = d['Site_Type']
                infra_provider = d['Infra Provider']
                site_id = str(int(d['Site ID'])) if isinstance(d['Site ID'], float) else str(d['Site ID'])
                building_height = d['Building_Height']
                tower_height = d['Tower_Height']
                latitude = d['Latitude']
                longitude = d['Longitude']
                idu_ip = d['IDU IP']
                sector_name = d['Sector_name']
                pmp = int(d['PMP']) if isinstance(d['PMP'], float) else d['PMP']
                make_of_antenna = "#N/A" if isinstance(d['Make of Antenna'], int) else d['Make of Antenna']
                antenna_polarization = d['Antenna Polarisation']
                antenna_tilt = int(d['Antenna_Tilt']) if isinstance(d['Antenna_Tilt'], float) else d['Antenna_Tilt']
                antenna_height = d['Antenna_Height']
                antenna_beamwidth = int(d['Antenna_BeamWidth']) if isinstance(d['Antenna_BeamWidth'], float) else d['Antenna_BeamWidth']
                azimuth = d['Azimuth']
                installation_of_splitter = d['Installation of Splitter']
                type_of_gps = d['Type of GPS']
                bs_switch_ip = d['BS Switch IP']
                aggregation_switch = d['Aggregation Switch']
                aggregation_switch_port = d['Aggregation Switch Port']
                bs_converter_ip = d['BS Converter IP']
                pop_converter_ip = d['POP Converter IP']
                converter_type = d['Converter Type']
                bh_configured_on = d['BH Configured On Switch/Converter']
                switch_or_converter_port = d['Switch/Converter Port']
                bh_capacity = int(d['BH Capacity']) if isinstance(d['BH Capacity'], float) else d['BH Capacity']
                bh_off_or_onnet = d['BH Offnet/Onnet']
                backhaul_type = d['Backhaul Type']
                bh_circuit_id = d['BH Circuit ID']
                pe_hostname = d['PE Hostname']
                pe_ip = d['PE IP']
                dr_site = d['DR site']
                ttsl_circuit_id = d['TTSL CIRCUIT ID']
                errors = ""

                # dropdown lists
                types_of_bs_list = ['WIMAX', 'CAMBIUM', 'RADWIN']
                site_types_list = ['GBT', 'RTT', 'POLE']
                infra_provider_list = ['TVI', 'VIOM', 'INDUS', 'ATC', 'IDEA', 'QUIPPO', 'SPICE', 'TTML', 'TCL', 'TOWER VISION', 'RIL', 'WTTIL', 'OTHER']
                make_of_antenna_list = ['MTI H Pol', 'Xhat', 'Andrew', 'MTI', 'Twin', 'Proshape']
                antenna_polarisation_list = ['Vertical', 'Horizontal', 'Cross', 'Dual']
                bh_off_or_onnet_list = ['OFFNET', 'ONNET', 'OFFNET+ONNET', 'OFFNET+ONNET UBR', 'ONNET+UBR', 'ONNET COLO','ONNET COLO+UBR']
                backhaul_type_list = ['SDH', 'Ethernet', 'E1', 'EoSDH', 'Dark Fibre', 'UBR']
                pmp_list = [1, 2]
                azimuth_angles_list = range(0, 361)
                installation_of_splitter_list = ['Yes', 'No']
                dr_site_list = ['Yes', 'No']

                # regex for checking whether string contains only numbers and .(dot)
                regex_numbers_and_single_dot = '^[0-9]*\\.?[0-9]*$'
                regex_upto_two_dec_places = '^\d{1,3}($|\.\d{1,2}$)'
                regex_ip_address = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
                regex_alnum_comma_hyphen_fslash_underscore_space = '^[a-zA-Z0-9\s,_/-]+$'
                regex_alnum_comma_underscore_space = '^[a-zA-Z0-9,\s_]+$'
                regex_alpha_underscore = '^[a-zA-Z_]+$'
                regex_alpha_space = '^[a-zA-Z\s]+$'
                regex_alnum_comma_underscore_space = '^[a-zA-Z0-9\s,_]+$'
                regex_alnum_comma_underscore_space_asterisk = '^[a-zA-Z0-9\s,\*_]+$'
                regex_alnum_hyphen = '^[a-zA-Z0-9-]+$'
                regex_alnum_space = '^[a-zA-Z0-9\s]+$'

                # 'city' validation (must be alphabetical and can contain space)
                if city:
                    if not re.match(regex_alpha_space, str(city).strip()):
                        errors += 'City must be alpha and can contain space.\n'
                else:
                    errors += 'City must not be empty.\n'

                # 'state' validation (must be alphabetical and can contain space)
                if state:
                    if not re.match(regex_alpha_space, str(state).strip()):
                        errors += 'State must be alpha and can contain space.\n'
                else:
                    errors += 'State must not be empty.\n'

                # 'type of bs' validation (must be from provided list)
                if type_of_bs:
                    if type_of_bs.strip().lower() not in [x.lower() for x in types_of_bs_list]:
                        errors += '{} is not valid option for bs type.\n'.format(type_of_bs)
                else:
                    errors += 'Type of BS must not be empty.\n'

                # 'site type' validation (must be from provided list)
                if site_type:
                    if site_type.strip().lower() not in [x.lower() for x in site_types_list]:
                        errors += '{} is not a valid option for site type.\n'.format(site_type)
                else:
                    errors += 'Site type must not be empty.\n'

                # 'infra provider' validation (must be from provided list)
                if infra_provider:
                    if infra_provider.strip().lower() not in [x.lower() for x in infra_provider_list]:
                        errors += '{} is not a valid option for infra provider.\n'.format(infra_provider)
                else:
                    errors += 'Infra provider must not be empty.\n'

                #  'site id' validation (must be alphanumeric)
                if site_id:
                    if not re.match(regex_alnum_comma_underscore_space, str(site_id).strip()):
                        errors += 'Site ID {} must be alphanumeric.\n'.format(site_id)
                else:
                    errors += 'Site ID must not be empty.\n'

                # 'building height' validation (must be upto 2 decimal places)
                if building_height:
                    if not re.match(regex_upto_two_dec_places, str(building_height).strip()):
                        errors += 'Building height must be upto 2 decimal places.\n'
                else:
                    errors += 'Building height must not be empty.\n'

                # 'tower height' validation (must be upto 2 decimal places)
                if tower_height:
                    if not re.match(regex_upto_two_dec_places, str(tower_height).strip()):
                        errors += 'Tower height must be upto 2 decimal places.\n'
                else:
                    errors += 'Tower height must not be empty.\n'

                # 'idu ip' validation (must be an ip address)
                if idu_ip:
                    if not re.match(regex_ip_address, idu_ip.strip()):
                        errors += 'IDU IP must be an ip address.'
                else:
                    errors += 'IDU IP must not be empty.\n'

                # 'sector name' validation (matches pattern for V1, V2, V3, V4 etc.)
                if sector_name:
                    if not sector_name.lower().startswith('v'):
                        errors += 'Sector name must be like V1, V2, V3, V4 etc.'
                else:
                    errors += 'Sector name must not be empty.\n'

                # 'pmp' validation (must be from provided list)
                if pmp:
                    if pmp not in pmp_list:
                        errors += '{} is not a valid option for pmp.\n'.format(pmp)
                else:
                    errors += 'PMP must not be empty.\n'

                # 'make of antenna' validation (must be form provided list)
                if make_of_antenna:
                    if make_of_antenna not in ['#N/A', 'na', 'NA']:
                        if make_of_antenna.strip().lower() not in [x.lower() for x in make_of_antenna_list]:
                            errors += '{} is not a valid option for make of antenna.\n'.format(make_of_antenna)

                # 'antenna polarisation' validation (must be from provided list)
                if antenna_polarization:
                    if antenna_polarization.strip().lower() not in [x.lower() for x in antenna_polarisation_list]:
                        errors += '{} is not a valid option for antenna polarization.\n'.format(antenna_polarization)
                else:
                    errors += 'Antenna polarization must not be empty.\n'

                # 'antenna tilt' validation (must be numeric)
                if antenna_tilt:
                    if not isinstance(antenna_tilt, int):
                        errors += 'Antenna tilt must be numeric.\n'
                # else:
                #     errors += 'Antenna tilt must not be empty.\n'

                # 'antenna height' validation (must be upto 2 decimal places)
                if antenna_height:
                    if not re.match(regex_upto_two_dec_places, str(antenna_height).strip()):
                        errors += 'Antenna height must be upto 2 decimal places.\n'
                else:
                    errors += 'Antenna height must not be empty.\n'

                # 'antenna beamwidth' validation (must be numeric)
                if antenna_beamwidth:
                    if not isinstance(antenna_beamwidth, int):
                        errors += 'Antenna beamwidth must be numeric.\n'
                else:
                    errors += 'Antenna beamwidth must not be empty.\n'

                # 'azimuth' validation (must be in range 0-360)
                if azimuth:
                    if azimuth not in azimuth_angles_list:
                        errors += 'Azimuth must be in range 0-360.\n'
                else:
                    errors += 'Azimuth must not be empty.\n'

                # 'installation of splitter' validation (must be 'Yes' or 'No')
                if installation_of_splitter:
                    if installation_of_splitter.strip().lower() not in [x.lower() for x in installation_of_splitter_list]:
                        errors += 'Installation of splitter must be from \'Yes\' or \'No\'.\n'
                else:
                    errors += 'Installation of splitter must not be empty.\n'

                # 'type of gps' validation (must be alphanumeric)
                if type_of_gps:
                    if not (isinstance(type_of_gps, unicode) and type_of_gps.strip().isalnum()):
                        errors += 'Type of GPS must be alphanumeric.\n'
                else:
                    errors += 'Type of GPS must not be empty.\n'

                # 'bs switch ip' validation (must be an ip address)

                if bs_switch_ip:
                    if bs_switch_ip != 'NA':
                        if not re.match(regex_ip_address, bs_switch_ip.strip()):
                            errors += 'BS Switch IP {} must be an ip address.\n'.format(bs_switch_ip)
                else:
                    errors += 'BS switch IP must not be empty.\n'

                # 'aggregation switch' validation (must be an ip address)
                if aggregation_switch:
                    if aggregation_switch != 'NA':
                        if not re.match(regex_ip_address, aggregation_switch.strip()):
                            errors += 'Aggregation Switch must be an ip address.\n'

                # 'aggregation switch port' validation
                # (can only contains alphanumeric, underscore, hyphen, space, comma, forward slash)
                if aggregation_switch_port:
                    if aggregation_switch_port != 'NA':
                        if not re.match(regex_alnum_comma_hyphen_fslash_underscore_space, aggregation_switch_port.strip()):
                            errors += 'Aggregation Switch Port can only contains alphanumeric, underscore, hyphen, space, \
                                       comma, forward slash.\n'

                # 'bs converter ip' validation (must be an ip address)
                if bs_converter_ip:
                    if bs_converter_ip != 'NA':
                        if not re.match(regex_ip_address, bs_converter_ip.strip()):
                            errors += 'BS Converter IP must be an ip address.\n'
                else:
                    errors += 'BS Converter IP must not be empty.\n'

                # 'pop conveter ip' validation (must be an ip address)
                if pop_converter_ip:
                    if pop_converter_ip != 'NA':
                        if not re.match(regex_ip_address, pop_converter_ip.strip()):
                            errors += 'POP Converter IP must be an ip address.\n'
                else:
                    errors += 'POP Converter must not be empty.\n'

                # 'converter type' validation (can only contains alphabets or underscore)
                if converter_type:
                    if converter_type != 'NA':
                        if not re.match(regex_alpha_underscore, converter_type.strip()):
                            errors += 'Converter type can only contains alphabets or underscore.\n'
                else:
                    errors += 'Converter type must not be empty.\n'

                # 'bh configured on' validation (must be an ip address)
                if bh_configured_on:
                    if not re.match(regex_ip_address, bh_configured_on.strip()):
                        errors += 'BH Configured On must be an ip address.\n'
                else:
                    errors += 'BH Configured On must not be empty.\n'

                # 'switch or converter port' validation
                # (can only contains alphanumeric, underscore, hyphen, space, comma, forward slash)
                if switch_or_converter_port:
                    if not re.match(regex_alnum_comma_hyphen_fslash_underscore_space, switch_or_converter_port.strip()):
                        errors += 'Switch/Converter Port {} can only contains alphanumeric, underscore, hyphen, space, \
                                   comma, forward slash.\n'.format(switch_or_converter_port)
                else:
                    errors += 'Switch/Converter Port must not be empty.\n'

                # 'bh capacity' validation (must be numeric)
                if bh_capacity:
                    if not isinstance(bh_capacity, int):
                        errors += 'BH Capacity must be numeric.\n'
                else:
                    errors += 'BH Capacity must not be empty.\n'

                # 'bh off or onnet' validation (must be from provided list)
                if bh_off_or_onnet:
                    if bh_off_or_onnet.strip().lower() not in [x.lower() for x in bh_off_or_onnet_list]:
                        errors += '{} is not a valid option for bh off or onnet.\n'.format(bh_off_or_onnet)
                else:
                    errors += 'BH Offnet/Onnet must not be empty.\n'

                # 'backhaul type' validation (must be from provided list)
                if backhaul_type:
                    if backhaul_type.strip().lower() not in [x.lower() for x in backhaul_type_list]:
                        errors += '{} is not a valid option for backhaul type.\n'.format(backhaul_type)

                # # 'bh circuit id' validation
                # # (can only contains alphanumeric, underscore, space, comma)
                # if bh_circuit_id:
                #     if not re.match(regex_alnum_comma_underscore_space_asterisk, bh_circuit_id.strip()):
                #         errors += 'BH Circuit ID - {} can only contains alphanumeric, underscore, space, comma.\n'.format(bh_circuit_id)

                # 'pe hostname' validation
                # (can only contains alphanumerics and hyphen)
                if pe_hostname:
                    if not re.match(regex_alnum_hyphen, pe_hostname.strip()):
                        errors += 'PE Hostname can only contains alphanumerics and hyphen.\n'
                else:
                    errors += 'PE Hostname must not be empty.\n'

                # 'pe ip' validation (must be an ip address)
                if pe_ip:
                    if not re.match(regex_ip_address, pe_ip.strip()):
                        errors += 'PE IP must be an ip address.\n'
                else:
                    errors += 'PE IP must not be empty.\n'

                # 'dr site' validation (must be 'Yes' or 'No')
                if dr_site:
                    if dr_site.strip().lower() not in [x.lower() for x in dr_site_list]:
                        errors += 'DR Site {} must be from \'Yes\' or \'No\'.\n'.format(dr_site)

                # # 'ttsl circuit id' validation
                # # (can only contains alphanumeric, underscore, space, comma)
                # if ttsl_circuit_id:
                #     if ttsl_circuit_id != "NA":
                #         if not re.match(regex_alnum_comma_underscore_space, ttsl_circuit_id.strip()):
                #             errors += 'TTSL Circuit ID can only contains alphanumeric, underscore, space, comma.\n'

                # insert key 'errors' in dict 'd'
                d['errors'] = errors

                # check whether there are errors exist or not
                try:
                    if not errors:
                        valid_rows_list.append(d)
                    else:
                        invalid_rows_list.append(d)
                except Exception as e:
                    logger.info(e.message)

                # print "&&&&&&&&&&&&&&&&&"
                # print len(d)
                # print "&&&&&&&&&&&&&&&&&"
                # print d
                # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            print "Valid - "
            for row in valid_rows_list:
                print "It's valid."
                print "**********************************"
                print row['errors']
            print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
            print "\n\n\n\n\n\n\n\n\n"
            print "InValid - "
            for row in invalid_rows_list:
                print "**********************************"
                print row['errors']
        else:
            print "There are no BS & SS."
        return super(GISInventoryBulkImport, self).get(self, form)
