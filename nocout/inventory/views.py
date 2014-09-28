import ast
import copy
from operator import itemgetter
import time
from datetime import datetime
from django.contrib.auth.models import User
from machine.models import Machine
import os
from os.path import basename
from django.views.generic.base import View
import re
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, render_to_response
import json
from actstream import action
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, TemplateView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from device_group.models import DeviceGroup
from nocout.settings import GISADMIN, NOCOUT_USER
from nocout.utils.util import DictDiffer
from models import Inventory, DeviceTechnology, IconSettings, LivePollingSettings, ThresholdConfiguration, \
    ThematicSettings, GISInventoryBulkImport
from forms import InventoryForm, IconSettingsForm, LivePollingSettingsForm, ThresholdConfigurationForm, \
    ThematicSettingsForm, GISInventoryBulkImportForm, GISInventoryBulkImportEditForm
from organization.models import Organization
from site_instance.models import SiteInstance
from user_group.models import UserGroup
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit
from forms import AntennaForm, BaseStationForm, BackhaulForm, SectorForm, CustomerForm, SubStationForm, CircuitForm
from device.models import Country, State, City, Device
from django.contrib.staticfiles.templatetags.staticfiles import static
from user_profile.models import UserProfile
import xlrd
import xlwt
import logging
from IPy import IP
from django.template import RequestContext
from tasks import validate_gis_inventory_excel_sheet

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
        except Exception:
            i_sorting_cols = 0

        order = []
        order_columns = self.get_order_columns()
        for i in range(i_sorting_cols):
            # sorting column
            try:
                i_sort_col = int(request.REQUEST.get('iSortCol_%s' % i))
            except Exception:
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
        user_id = self.request.user.id
        #if user is superadmin or gisadmin
        if user_id in [1,2]:
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
            ]
        user_id = self.request.user.id
        #if user is superadmin or gisadmin
        if user_id in [1,2]:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ThresholdConfigurationListingTable(BaseDatatableView):
    """
    Class based View to render ThresholdConfiguration Data table.
    """
    model = ThresholdConfiguration
    columns = ['name', 'alias', 'live_polling_template__alias']
    order_columns = ['name', 'alias', 'live_polling_template__alias']

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

    def get_initial_queryset(self, technology="no"):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        # return ThresholdConfiguration.objects.values(*self.columns + ['id'])
        return ThresholdConfiguration.objects.filter(live_polling_template__id__in=LivePollingSettings.objects.filter(technology__name=technology).values('id')).values(*self.columns + ['id'])

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

    def get_context_data(self, technology):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        # self.initialize(*args, **kwargs)
        self.initialize()

        qs = self.get_initial_queryset(technology)

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
            {'mData': 'icon_settings',           'sTitle': 'Icons Range',               'sWidth': 'null'},
            {'mData': 'user_selection',          'sTitle': 'Setting Selection',         'sWidth': 'null'},]

        user_id = self.request.user.id

        #if user is superadmin or gisadmin
        if user_id in [NOCOUT_USER.ID, GISADMIN.ID]:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ThematicSettingsListingTable(BaseDatatableView):
    """
    Class based View to render Thematic Settings Data table.
    """
    model = ThematicSettings
    columns = ['name', 'alias', 'threshold_template', 'icon_settings']
    order_columns = ['name', 'alias', 'threshold_template']
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

    def get_initial_queryset(self, technology="no"):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        if self.request.user.id in [NOCOUT_USER.ID, GISADMIN.ID]:
            # return ThematicSettings.objects.values(*self.columns + ['id'])
            return ThematicSettings.objects.filter(threshold_template__in=ThresholdConfiguration.objects.filter(live_polling_template__id__in=LivePollingSettings.objects.filter(technology__name=technology).values('id')).values('id')).values(*self.columns + ['id'])

        else:
            # return ThematicSettings.objects.filter(is_global=True).values(*self.columns + ['id'])
            return ThematicSettings.objects.filter(threshold_template__in=ThresholdConfiguration.objects.filter(live_polling_template__id__in=LivePollingSettings.objects.filter(technology__name=technology).values('id')).values('id')).filter(is_global=True).values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            image_string, range_text, full_string='','',''
            if dct['icon_settings'] and dct['icon_settings'] !='NULL':
                ###@nishant-teatrix. PLEASE SHOW THE RANGE MIN < ICON < RANGE MAX
                for d in eval(dct['icon_settings']):
                    img_url = str("/media/"+ (d.values()[0]) if "uploaded" in d.values()[0] else static("img/" + d.values()[0]))
                    image_string= '<img src="{0}" style="height:25px; width:25px">'.format(img_url.strip())
                    range_text= ' Range '+ d.keys()[0][-1] +', '
                    full_string+= image_string + range_text + "</br>"
            else:
                full_string='N/A'
            user_current_thematic_setting= self.request.user.id in ThematicSettings.objects.get(id=dct['id']).user_profile.values_list('id', flat=True)
            checkbox_checked_true='checked' if user_current_thematic_setting else ''
            dct.update(
                threshold_template=ThresholdConfiguration.objects.get(id=int(dct['threshold_template'])).name,
                icon_settings= full_string,
                user_selection='<input type="checkbox" class="check_class" '+ checkbox_checked_true +' name="setting_selection" value={0}><br>'.format(dct['id']),
                actions='<a href="/thematic_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/thematic_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, technology):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request

        # self.initialize(*args, **kwargs)
        self.initialize()

        qs = self.get_initial_queryset(technology)

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
        icon_settings_keys= list(set(form.data.keys())-set(form.cleaned_data.keys()+['csrfmiddlewaretoken']))
        icon_settings_values_list=[ { key: form.data[key] }  for key in icon_settings_keys if form.data[key]]
        self.object = form.save()
        self.object.icon_settings=icon_settings_values_list
        self.object.save()
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
        icon_settings_keys= list(set(form.data.keys())-set(form.cleaned_data.keys()+['csrfmiddlewaretoken']))
        icon_settings_values_list=[ { key: form.data[key] }  for key in icon_settings_keys if form.data[key]]
        self.object = form.save()
        self.object.icon_settings=icon_settings_values_list
        self.object.save()
        # self.object = form.save()
        if changed_fields_dict:
            verb_string = 'Changed values of ThematicSettings : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
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


class Get_Threshold_Ranges_And_Icon_For_Thematic_Settings(View):
    """
    The Class Based View to Response the Ajax call on click to return the respective
    ranges for the  threshold_template_id selected in the template.
    """

    def get(self, request):

        self.result = {
            "success": 0,
            "message": "Threshold range not fetched.",
            "data": {
                "meta": None,
                "objects": {}
            }
        }

        threshold_template_id= self.request.GET.get('threshold_template_id','')
        thematic_setting_name= self.request.GET.get('thematic_setting_name','')
        if threshold_template_id:
           threshold_configuration_selected=ThresholdConfiguration.objects.get(id=int(threshold_template_id))
           self.get_all_ranges(threshold_configuration_selected)
           if self.result['data']['objects']['range_list']:
              self.get_icon_details()
              self.result['success']=1


        if thematic_setting_name:
            thematic_setting_object= ThematicSettings.objects.get(name=thematic_setting_name)
            thematic_icon_setting= thematic_setting_object.icon_settings
            thematic_icon_setting= '[]' if thematic_icon_setting =='NULL' or thematic_icon_setting =='' else thematic_icon_setting
            thematic_icon_setting= eval(thematic_icon_setting)
            if thematic_icon_setting:
               icon_details, icon_details_selected=list(), dict()

               for icon_setting in thematic_icon_setting:
                   # range_list.append('Range ' + icon_setting.keys()[0][-1])
                   icon_details_selected['Range ' + icon_setting.keys()[0][-1]] = icon_setting.values()[0]

               # self.result['data']['objects']['range_list'] = range_list
               self.result['data']['objects']['icon_details_selected'] = icon_details_selected
               # self.get_icon_details()
               # self.result['success']=1

        return HttpResponse(json.dumps(self.result))

    def get_all_ranges(self, threshold_configuration_object):
        range_list=list()
        for ran in range(1, 11):

            range_start= None

            query= "range_start= threshold_configuration_object.range{0}_{1}".format(ran, 'start')
            exec query
            if range_start:
               range_list.append('Range {0}'.format(ran))

        self.result['data']['objects']['range_list'] = range_list

    def get_icon_details(self):
        icon_details= IconSettings.objects.all().values('id','name', 'upload_image')
        self.result['data']['objects']['icon_details'] =list(icon_details)


class Update_User_Thematic_Setting(View):
    """
    The Class Based View to Response the Ajax call on click to bind the user with the thematic setting.
    """
    def get(self, request):
        self.result = {
            "success": 0,
            "message": "Thematic Setting Not Bind to User",
            "data": {
                "meta": None,
                "objects": {}
            }
        }

        thematic_setting_id= self.request.GET.get('threshold_template_id',None)
        user_profile_id = self.request.user.id
        if thematic_setting_id:

            old_entries=ThematicSettings.objects.filter(user_profile__in= [user_profile_id])
            for entries in old_entries:
                entries.user_profile.remove(self.request.user)

            ThematicSettings.objects.get(id= int(thematic_setting_id)).user_profile.add(user_profile_id)
            self.result['success']=1
            self.result['message']='Thematic Setting Bind to User Successfully'
            self.result['data']['objects']['username']=self.request.user.userprofile.username
            self.result['data']['objects']['thematic_setting_name']= ThematicSettings.objects.get(id=int(thematic_setting_id)).name

        return HttpResponse(json.dumps(self.result))


#************************************ GIS Inventory Bulk Upload ******************************************
class GISInventoryBulkImportView(FormView):
    template_name = 'bulk_import/gis_bulk_import.html'
    success_url = '/bulk_import/'
    form_class = GISInventoryBulkImportForm

    def form_valid(self, form):
        # get uploaded file
        uploaded_file = self.request.FILES['file_upload']
        description = self.request.POST['description']
        timestamp = time.time()
        full_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S')

        # if directory for uploaded excel sheets didn't exist than create one
        if not os.path.exists('media/uploaded/inventory_files/original'):
            os.makedirs('media/uploaded/inventory_files/original')

        filepath = 'media/uploaded/inventory_files/original/{}_{}'.format(full_time, uploaded_file.name)

        # used in checking headers of excel sheet
        # dictionary containing all 'pts bs' fields
        ptp_bs_fields = ['City', 'State', 'Circuit ID', 'Circuit Type', 'Customer Name', 'BS Address', 'BS Name',
                         'QOS (BW)', 'Latitude', 'Longitude', 'Antenna Height', 'Polarization', 'Antenna Type',
                         'Antenna Gain', 'Antenna Mount Type', 'Ethernet Extender', 'Building Height',
                         'Tower/Pole Height', 'Cable Length', 'RSSI During Acceptance',
                         'Throughput During Acceptance', 'Date Of Acceptance', 'BH BSO', 'IP', 'MAC', 'HSSU Used',
                         'BS Switch IP', 'Aggregation Switch', 'Aggregation Switch Port', 'BS Converter IP',
                         'POP Converter IP', 'Converter Type', 'BH Configured On Switch/Converter',
                         'Switch/Converter Port', 'BH Capacity', 'BH Offnet/Onnet', 'Backhaul Type',
                         'BH Circuit ID', 'PE Hostname', 'PE IP', 'BSO Circuit ID', 'Site ID', 'HSSU Port']

        # dictionary containing all 'pmp bs' fields
        pmp_bs_fields = ['City', 'State', 'Address', 'BS Name', 'Type Of BS (Technology)', 'Site Type',
                         'Infra Provider', 'Site ID', 'Building Height', 'Tower Height', 'Latitude', 'Longitude',
                         'ODU IP', 'Sector Name', 'Make Of Antenna', 'Polarization', 'Antenna Tilt',
                         'Antenna Height', 'Antenna Beamwidth', 'Azimuth', 'Sync Splitter Used',
                         'Type Of GPS', 'BS Switch IP', 'Aggregation Switch', 'Aggregation Switch Port',
                         'BS Converter IP', 'POP Converter IP', 'Converter Type', 'BH Configured On Switch/Converter',
                         'Switch/Converter Port', 'BH Capacity', 'BH Offnet/Onnet', 'Backhaul Type', 'BH Circuit ID',
                         'PE Hostname', 'PE IP', 'DR Site', 'BSO Circuit ID']

        # dictionary containing all 'wimax bs' fields
        wimax_bs_fields = ['City', 'State', 'Address', 'BS Name', 'Type Of BS (Technology)', 'Site Type',
                           'Infra Provider', 'Site ID', 'Building Height', 'Tower Height', 'Latitude', 'Longitude',
                           'IDU IP', 'Sector Name', 'PMP', 'Make Of Antenna', 'Polarization', 'Antenna Tilt',
                           'Antenna Height', 'Antenna Beamwidth', 'Azimuth', 'Installation Of Splitter',
                           'Type Of GPS', 'BS Switch IP', 'Aggregation Switch', 'Aggregation Switch Port',
                           'BS Converter IP', 'POP Converter IP', 'Converter Type', 'BH Configured On Switch/Converter',
                           'Switch/Converter Port', 'BH Capacity', 'BH Offnet/Onnet', 'Backhaul Type', 'BH Circuit ID',
                           'PE Hostname', 'PE IP', 'DR Site', 'BSO Circuit ID']

        # dictionary containing all 'ptp ss' fields
        ptp_ss_fields = ['SS City', 'SS State', 'SS Circuit ID', 'SS Customer Name', 'SS Customer Address',
                         'SS BS Name', 'SS QOS (BW)', 'SS Latitude', 'SS Longitude', 'SS MIMO/Diversity',
                         'SS Antenna Height', 'SS Polarization', 'SS Antenna Type', 'SS Antenna Gain',
                         'SS Antenna Mount Type', 'SS Ethernet Extender', 'SS Building Height', 'SS Tower/Pole Height',
                         'SS Cable Length', 'SS RSSI During Acceptance', 'SS Throughput During Acceptance',
                         'SS Date Of Acceptance', 'SS BH BSO', 'SS IP', 'SS MAC']

        # dictionary containing all 'pmp ss' fields
        pmp_ss_fields = ['Customer Name', 'Circuit ID', 'QOS (BW)', 'Latitude', 'Longitude', 'Building Height',
                         'Tower/Pole Height', 'Antenna Height', 'Polarization', 'Antenna Type', 'SS Mount Type',
                         'Ethernet Extender', 'Cable Length', 'RSSI During Acceptance', 'CINR During Acceptance',
                         'Customer Address', 'Date Of Acceptance', 'SS IP', 'Lens/Reflector', 'Antenna Beamwidth']

        # dictionary containing all 'wimax ss' fields
        wimax_ss_fields = ['Customer Name', 'Circuit ID', 'QOS (BW)', 'Latitude', 'Longitude', 'Building Height',
                           'Tower/Pole Height', 'Antenna Height', 'Polarization', 'Antenna Type', 'SS Mount Type',
                           'Ethernet Extender', 'Cable Length', 'RSSI During Acceptance',
                           'CINR During Acceptance', 'Customer Address', 'Date Of Acceptance', 'SS IP']

        # initialize variables for bs sheet name, ss sheet name, ptp sheet name
        bs_sheet = ""
        ss_sheet = ""
        ptp_sheet = ""
        technology = ""

        # fetching values form POST
        try:
            bs_sheet = self.request.POST['bs_sheet'] if self.request.POST['bs_sheet'] else ""
            ss_sheet = self.request.POST['ss_sheet'] if self.request.POST['ss_sheet'] else ""
            ptp_sheet = self.request.POST['ptp_sheet'] if self.request.POST['ptp_sheet'] else ""
        except Exception as e:
            logger.info(e.message)

        # reading workbook using 'xlrd' module
        try:
            book = xlrd.open_workbook(uploaded_file.name, file_contents=uploaded_file.read(), formatting_info=True)
        except Exception as e:
            return render_to_response('bulk_import/gis_bulk_validator.html', {'headers': "",
                                                                              'filename': uploaded_file.name,
                                                                              'sheet_name': "",
                                                                              'valid_rows': "",
                                                                              'invalid_rows': "",
                                                                              'error_message': "There is some internel error in sheet."},
                                      context_instance=RequestContext(self.request))

        # execute only if a valid sheet is selected from form
        if bs_sheet or ss_sheet or ptp_sheet:
            if bs_sheet:
                sheet = book.sheet_by_name(bs_sheet)
                sheet_name = bs_sheet
            elif ss_sheet:
                sheet = book.sheet_by_name(ss_sheet)
                sheet_name = ss_sheet
            elif ptp_sheet:
                sheet = book.sheet_by_name(ptp_sheet)
                sheet_name = ptp_sheet
            else:
                sheet = ""
                sheet_name = ""

            # get the technology of uploaded inventory sheet
            if "Wimax" in sheet_name:
                technology = "Wimax"
            elif "PMP" in sheet_name:
                technology = "PMP"
            elif "PTP" in sheet_name:
                technology = "PTP"
            elif "Converter" in sheet_name:
                technology = "Converter"
            else:
                technology = "Unknown"

            keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
            keys_list = [x.encode('utf-8').strip() for x in keys]
            complete_d = list()
            for row_index in xrange(1, sheet.nrows):
                d = {keys[col_index].encode('utf-8').strip(): sheet.cell(row_index, col_index).value
                     for col_index in xrange(len(keys))}
                complete_d.append(d)

            # book_to_upload = xlcopy(book)
            destination = open(filepath, 'wb+')
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
            destination.close()
            #xlsave(book, filepath)
            gis_bulk_obj = GISInventoryBulkImport()
            gis_bulk_obj.original_filename = filepath
            gis_bulk_obj.status = 0
            gis_bulk_obj.sheet_name = sheet_name
            gis_bulk_obj.technology = technology
            gis_bulk_obj.description = description
            gis_bulk_obj.uploaded_by = self.request.user
            gis_bulk_obj.save()
            gis_bulk_id = gis_bulk_obj.id

            result = validate_gis_inventory_excel_sheet.delay(gis_bulk_id, complete_d, sheet_name, keys_list, full_time, uploaded_file.name)
            return HttpResponseRedirect('/bulk_import/')
        else:
            print "No sheet is selected."
        return super(GISInventoryBulkImportView, self).get(self, form)


class ExcelWriterRowByRow(View):
    def get(self, request):
        filename = request.GET['filename'].split(".")[0]
        sheetname = request.GET['sheetname']
        sheettype = request.GET['sheettype']

        if sheettype == repr('valid'):
            content = request.session['valid_rows_lists']
            filename = "valid_{}_{}.xls".format(sheetname.lower().replace(" ", "_"), filename.lower().replace(" ", "_"))
        elif sheettype == repr('invalid'):
            content = request.session['invalid_rows_lists']
            filename = "invalid_{}_{}.xls".format(sheetname.lower().replace(" ", "_"),
                                                  filename.lower().replace(" ", "_"))
        else:
            content = ""

        wb = xlwt.Workbook()
        ws = wb.add_sheet(sheetname)

        style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')
        style_errors = xlwt.easyxf('pattern: pattern solid, fore_colour red;' 'font: colour white, bold True;')

        try:
            for i, col in enumerate(request.session['headers']):
                if col != 'Errors':
                    ws.write(0, i, col, style)
                else:
                    ws.write(0, i, col, style_errors)
        except Exception as e:
            logger.info(e.message)

        try:
            for i, l in enumerate(content):
                i += 1
                for j, col in enumerate(l):
                    ws.write(i, j, col)
        except Exception as e:
            logger.info(e.message)

        response = HttpResponse(mimetype='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

        wb.save(response)

        return response


class BulkUploadValidData(View):
    def get(self, request, *args, **kwargs):
        # user organization
        organization = ''

        try:
            # user organization id
            organization_id = UserProfile.objects.get(username=self.request.user).organization.id
            organization = Organization.objects.get(pk=organization_id)
        except Exception as e:
            logger.info("Current User Organization:", e.message)

        # timestamp
        timestamp = time.time()
        full_time = datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y at %H:%M:%S')

        # get object for 'GISInventoryBulkImport' model
        gis_bu_obj = ""
        try:
            gis_bu_obj = GISInventoryBulkImport.objects.get(pk=kwargs['pk'])
        except Exception as e:
            logger.info(e.message)

        book = xlrd.open_workbook(gis_bu_obj.invalid_filename)
        sheet = book.sheet_by_index(0)

        keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
        keys_list = [x.encode('utf-8').strip() for x in keys]
        complete_d = list()

        for row_index in xrange(1, sheet.nrows):
            d = {keys[col_index].encode('utf-8').strip(): sheet.cell(row_index, col_index).value
                 for col_index in xrange(len(keys))}
            complete_d.append(d)

        for row in complete_d:
            # ----------------------------- Base Station Device ---------------------------
            # get machine
            machine = get_ptp_machine(row['IP'])

            # base station data
            base_station_data = {
                'device_name': row['IP'] if 'IP' in row.keys() else "",
                'organization': organization,
                'machine': machine,
                'site': 1,
                'device_technology': 2,
                'device_vendor': 2,
                'device_model': 2,
                'device_type': 3,
                'ip': row['IP'] if 'IP' in row.keys() else "",
                'mac': row['MAC'] if 'MAC' in row.keys() else "",
                'state': row['State'] if 'State' in row.keys() else "",
                'city': row['City'] if 'City' in row.keys() else "",
                'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                'description': 'Base Station created on {}.'.format(full_time)
            }
            # base station object
            base_station = create_device(base_station_data)

            # ----------------------------- Sub Station Device ---------------------------
            # get machine
            machine = get_ptp_machine(row['SS IP'] if 'SS IP' in row.keys() else "")

            # base station data
            sub_station_data = {
                'device_name': row['SS IP'] if 'SS IP' in row.keys() else "",
                'organization': organization,
                'machine': machine,
                'site': 1,
                'device_technology': 2,
                'device_vendor': 2,
                'device_model': 2,
                'device_type': 2,
                'ip': row['SS IP'] if 'SS IP' in row.keys() else "",
                'mac': row['SS MAC'] if 'SS MAC' in row.keys() else "",
                'state': row['SS State'] if 'SS State' in row.keys() else "",
                'city': row['SS City'] if 'SS City' in row.keys() else "",
                'latitude': row['SS Latitude'] if 'SS Latitude' in row.keys() else "",
                'longitude': row['SS Longitude'] if 'SS Longitude' in row.keys() else "",
                'address': row['SS Customer Address'] if 'SS Customer Address' in row.keys() else "",
                'description': 'Sub Station created on {}.'.format(full_time)
            }
            # base station object
            sub_station = create_device(sub_station_data)

            # ------------------------------ Create BS Switch -----------------------------
            # get machine
            machine = get_ptp_machine(row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "")

            # base station data
            bs_switch_data = {
                'device_name': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                'organization': organization,
                'machine': machine,
                'site': 1,
                'device_technology': 7,
                'device_vendor': 9,
                'device_model': 12,
                'device_type': 12,
                'ip': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                'mac': "",
                'state': row['State'] if 'State' in row.keys() else "",
                'city': row['City'] if 'City' in row.keys() else "",
                'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                'description': 'BS Switch created on {}.'.format(full_time)
            }
            # base station object
            bs_switch = create_device(bs_switch_data)

            # --------------------------- Aggregation Switch IP ---------------------------
            # get machine
            machine = get_ptp_machine(row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "")

            # base station data
            aggregation_switch_data = {
                'device_name': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                'organization': organization,
                'machine': machine,
                'site': 1,
                'device_technology': 7,
                'device_vendor': 9,
                'device_model': 12,
                'device_type': 12,
                'ip': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                'mac': "",
                'state': row['State'] if 'State' in row.keys() else "",
                'city': row['City'] if 'City' in row.keys() else "",
                'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                'description': 'Aggregation Switch created on {}.'.format(full_time)
            }
            # base station object
            aggregation_switch = create_device(aggregation_switch_data)

            # -------------------------------- BS Converter IP ---------------------------
            # get machine
            machine = get_ptp_machine(row['BS Converter IP'])

            # base station data
            bs_converter_data = {
                'device_name': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                'organization': organization,
                'machine': machine,
                'site': 1,
                'device_technology': 8,
                'device_vendor': 8,
                'device_model': 10,
                'device_type': 13,
                'ip': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                'mac': "",
                'state': row['State'] if 'State' in row.keys() else "",
                'city': row['City'] if 'City' in row.keys() else "",
                'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                'description': 'BS Converter created on {}.'.format(full_time)
            }
            # base station object
            bs_converter = create_device(bs_converter_data)

            # -------------------------------- POP Converter IP ---------------------------
            # get machine
            machine = get_ptp_machine(row['POP Converter IP'] if 'IP' in row.keys() else "")

            # base station data
            pop_converter_data = {
                'device_name': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                'organization': organization,
                'machine': machine,
                'site': 1,
                'device_technology': 8,
                'device_vendor': 8,
                'device_model': 10,
                'device_type': 13,
                'ip': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                'mac': "",
                'state': row['State'] if 'State' in row.keys() else "",
                'city': row['City'] if 'City' in row.keys() else "",
                'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                'description': 'POP Converter created on {}.'.format(full_time)
            }
            # base station object
            pop_converter = create_device(pop_converter_data)

            # ------------------------------- Sector Antenna -------------------------------
            # sector antenna data
            sector_antenna_data = {
                'ip': row['IP'] if 'IP' in row.keys() else "",
                'antenna_type': row['Antenna Type'] if 'Antenna Type' in row.keys() else "",
                'height': row['Antenna Height'] if 'Antenna Height' in row.keys() else "",
                'polarization': row['Polarization'] if 'Polarization' in row.keys() else "",
                'gain': row['Antenna Gain'] if 'Antenna Gain' in row.keys() else "",
                'mount_type': row['Antenna Mount Type'] if 'Antenna Mount Type' in row.keys() else "",
                'description': 'Sector Antenna created on {}.'.format(full_time)
            }
            # sector antenna object
            sector_antenna = create_antenna(sector_antenna_data)

            # ------------------------------- Sub Station Antenna -------------------------------
            # sub station antenna data
            substation_antenna_data = {
                'ip': row['SS IP'] if 'SS IP' in row.keys() else "",
                'antenna_type': row['SS Antenna Type'] if 'SS Antenna Type' in row.keys() else "",
                'height': row['SS Antenna Height'] if 'SS Antenna Height' in row.keys() else "",
                'polarization': row['SS Polarization'] if 'SS Polarization' in row.keys() else "",
                'gain': row['SS Antenna Gain'] if 'SS Antenna Gain' in row.keys() else "",
                'mount_type': row['SS Antenna Mount Type'] if 'SS Antenna Mount Type' in row.keys() else "",
                'description': 'Sector Antenna created on {}.'.format(full_time)
            }
            # sector antenna object
            substation_antenna = create_antenna(substation_antenna_data)

            # ------------------------------- Backhaul -------------------------------
            # backhaul data
            bh_configured_on = ""
            try:
                bh_configured_on = Device.objects.get(device_name=row['BH Configured On Switch/Converter'])
            except Exception as e:
                logger.info(e.message)

            backhaul_data = {
                'ip': row['BH Configured On Switch/Converter'] if 'BH Configured On Switch/Converter' in row.keys() else "",
                'bh_configured_on': bh_configured_on,
                'bh_port_name': row['Switch/Converter Port'] if 'Switch/Converter Port' in row.keys() else "",
                'bh_port': 0,
                'bh_type': row['Backhaul Type'] if 'Backhaul Type' in row.keys() else "",
                'bh_switch': bs_converter,
                'pop': pop_converter,
                'aggregator': aggregation_switch,
                'aggregator_port_name': row['Aggregation Switch Port'] if 'Aggregation Switch Port' in row.keys() else "",
                'aggregator_port': 0,
                'pe_hostname': row['PE Hostname'] if 'PE Hostname' in row.keys() else "",
                'pe_ip': row['PE IP'] if 'PE IP' in row.keys() else "",
                'bh_connectivity': row['BH Offnet/Onnet'] if 'BH Offnet/Onnet' in row.keys() else "",
                'bh_circuit_id': row['BH Circuit ID'] if 'BH Circuit ID' in row.keys() else "",
                'bh_capacity': row['BH Capacity'] if 'BH Capacity' in row.keys() else "",
                'ttsl_circuit_id': row['BSO Circuit ID'] if 'BSO Circuit ID' in row.keys() else "",
                'description': 'Backhaul created on {}.'.format(full_time)
            }

            # backhaul object
            backhaul = ""
            if row['BH Configured On Switch/Converter']:
                if row['BH Configured On Switch/Converter'] not in ['NA', 'na', 'N/A', 'n/a']:
                    backhaul = create_backhaul(backhaul_data)

            # ------------------------------- Base Station -------------------------------
            # base station data
            # sanitize bs name
            name = name_sanitizer(row['BS Name'] if 'BS Name' in row.keys() else "")
            alias = row['BS Name'] if 'BS Name' in row.keys() else ""
            basestation_data = {
                'name': name,
                'alias': alias,
                'bs_switch': bs_switch,
                'backhaul': backhaul,
                'bh_bso': row['BH BSO'] if 'BH BSO' in row.keys() else "",
                'hssu_used': row['HSSU Used'] if 'HSSU Used' in row.keys() else "",
                'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                'building_height': row['Building Height'] if 'Building Height' in row.keys() else "",
                'tower_height': row['Tower/Pole Height'] if 'Tower/Pole Height' in row.keys() else "",
                'state': row['State'] if 'State' in row.keys() else "",
                'city': row['City'] if 'City' in row.keys() else "",
                'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                'description': 'Base Station created on {}.'.format(full_time)
            }

            # base station object
            basestation = ""
            if name and alias:
                basestation = create_basestation(basestation_data)

            # ---------------------------------- Sector ---------------------------------
            # sector data
            sector_data = {
                'ip': row['IP'] if 'IP' in row.keys() else "",
                'base_station': basestation,
                'bs_technology': 2,
                'sector_configured_on': base_station,
                'antenna': sector_antenna,
                'description': 'Sector created on {}.'.format(full_time)
            }

            # sector object
            sector = create_sector(sector_data)

            # ------------------------------- Sub Station -------------------------------
            # sub station data
            # sanitize bs name
            name = name_sanitizer(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
            alias = row['SS IP'] if 'SS IP' in row.keys() else ""
            substation_data = {
                'name': name,
                'alias': alias,
                'device': sub_station,
                'antenna': substation_antenna,
                'building_height': row['SS Building Height'] if 'SS Building Height' in row.keys() else "",
                'tower_height': row['SS Tower/Pole Height'] if 'SS Tower/Pole Height' in row.keys() else "",
                'ethernet_extender': row['SS Ethernet Extender'] if 'SS Ethernet Extender' in row.keys() else "",
                'cable_length': row['SS Cable Length'] if 'SS Cable Length' in row.keys() else "",
                'longitude': row['SS Longitude'] if 'SS Longitude' in row.keys() else "",
                'latitude': row['SS Latitude'] if 'SS Latitude' in row.keys() else "",
                'mac_address': row['SS MAC'] if 'SS MAC' in row.keys() else "",
                'state': row['SS State'] if 'SS State' in row.keys() else "",
                'city': row['SS City'] if 'SS City' in row.keys() else "",
                'address': row['SS Customer Address'] if 'SS Customer Address' in row.keys() else "",
                'description': 'Sub Station created on {}.'.format(full_time)
            }

            # sub station object
            substation = ""
            if name and alias:
                substation = create_substation(substation_data)

            # ------------------------------- Customer -------------------------------
            # customer data
            # sanitize customer name
            name = name_sanitizer(row['SS Customer Name'] if 'SS Customer Name' in row.keys() else "")
            alias = row['SS Customer Name'] if 'SS Customer Name' in row.keys() else ""
            customer_data = {
                'name': name,
                'alias': alias,
                'address': row['SS Customer Address'] if 'SS Customer Address' in row.keys() else "",
                'description': 'SS Customer created on {}.'.format(full_time)
            }

            # customer object
            customer = ""
            if name:
                customer = create_customer(customer_data)

            # ------------------------------- Circuit -------------------------------
            # sanitize circuit name
            name = name_sanitizer(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")

            # validate date of acceptance
            if 'SS Date Of Acceptance' in row.keys():
                date_of_acceptance = validate_date(row['SS Date Of Acceptance'])
            else:
                date_of_acceptance = ""

            # circuit data
            alias = row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else ""
            circuit_data = {
                'name': name,
                'alias': alias,
                'circuit_id': row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "",
                'sector': sector,
                'customer': customer,
                'sub_station': substation,
                'qos_bandwidth': row['SS QOS (BW)'] if 'SS QOS (BW)' in row.keys() else "",
                'dl_rssi_during_acceptance': row['SS RSSI During Acceptance'] if 'SS RSSI During Acceptance' in row.keys() else "",
                'throughput_during_acceptance': row['SS Throughput During Acceptance'] if 'SS Throughput During Acceptance' in row.keys() else "",
                'date_of_acceptance': date_of_acceptance,
                'description': 'Circuit created on {}.'.format(full_time)
            }
            # circuit object
            circuit = ""
            if name and alias:
                circuit = create_circuit(circuit_data)
        return HttpResponseRedirect('/bulk_import/')


def create_device(device_payload):
    """ Create Device object

    Args:
        device_payload (dict): {
                                    'city': u'Delhi(NewDelhi)',
                                    'description': 'BaseStationcreatedon28-Sep-2014at22: 55: 03.',
                                    'state': u'Delhi',
                                    'device_model': 2,
                                    'ip': u'10.75.158.219',
                                    'site': 1,
                                    'longitude': 77.253333333333,
                                    'device_name': u'10.75.158.219',
                                    'machine': '',
                                    'mac': u'00: 15: 67: d7: 88: 02',
                                    'device_type': 3,
                                    'address': u'A-88,
                                    EastOfKailash,
                                    Delhi',
                                    'latitude': 28.560277777778,
                                    'organization': <Organization: TCL>,
                                    'device_vendor': 2,
                                    'device_technology': 2
                                }

    Returns:
        device (class 'device.models.Device'): <Device: 10.75.158.219>

    """

    # dictionary containing device data
    device_payload = device_payload

    # initializing variables
    device_name, device_alias, machine, device_technology, device_vendor, device_model, device_type = [''] * 7
    site_instance, ip_address, mac_address, state, city, latitude, longitude, address, description = [''] * 9

    # get device parameters
    if 'device_name' in device_payload.keys():
        device_name = device_payload['device_name'] if device_payload['device_name'] else ""
    if 'organization' in device_payload.keys():
        organization = device_payload['organization'] if device_payload['organization'] else ""
    if 'ip' in device_payload.keys():
        device_alias = device_payload['ip'] if device_payload['ip'] else ""
    if 'machine' in device_payload.keys():
        machine = device_payload['machine'] if device_payload['machine'] else ""
    if 'site' in device_payload.keys():
        site_instance = device_payload['site'] if device_payload['site'] else ""
    if 'device_technology' in device_payload.keys():
        device_technology = device_payload['device_technology'] if device_payload['device_technology'] else ""
    if 'device_vendor' in device_payload.keys():
        device_vendor = device_payload['device_vendor'] if device_payload['device_vendor'] else ""
    if 'device_model' in device_payload.keys():
        device_model = device_payload['device_model'] if device_payload['device_model'] else ""
    if 'device_type' in device_payload.keys():
        device_type = device_payload['device_type'] if device_payload['device_type'] else ""
    if 'ip' in device_payload.keys():
        ip_address = device_payload['ip'] if device_payload['ip'] else ""
    if 'mac' in device_payload.keys():
        mac_address = device_payload['mac'] if device_payload['mac'] else ""
    if 'state' in device_payload.keys():
        state = device_payload['state'] if device_payload['state'] else ""
    if 'city' in device_payload.keys():
        city = device_payload['city'] if device_payload['city'] else ""
    if 'latitude' in device_payload.keys():
        latitude = device_payload['latitude'] if device_payload['latitude'] else ""
    if 'longitude' in device_payload.keys():
        longitude = device_payload['longitude'] if device_payload['longitude'] else ""
    if 'address' in device_payload.keys():
        address = device_payload['address'] if device_payload['address'] else ""
    if 'description' in device_payload.keys():
        description = device_payload['description'] if device_payload['description'] else ""

    # update device if it exists in database
    if device_name:
        if device_name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING DEVICE -------------------------------
            try:
                # device object
                device = Device.objects.get(device_name=device_name, ip_address=ip_address)
                # device alias
                if device_alias:
                    try:
                        device.device_alias = device_alias
                    except Exception as e:
                        logger.info("Device Alias: ({} - {})".format(device_alias, e.message))
                # machine
                if machine:
                    try:
                        device.machine = machine
                    except Exception as e:
                        logger.info("Machine: ({} - {})".format(machine, e.message))
                # site instance
                if site_instance:
                    try:
                        device.site_instance = SiteInstance.objects.get(pk=site_instance)
                    except Exception as e:
                        logger.info("Site Instance: ({} - {})".format(site_instance, e.message))
                # organization
                try:
                    device.organization = organization
                except Exception as e:
                    logger.info("Organization: ({})".format(e.message))
                # device technology
                if device_technology:
                    try:
                        device.device_technology = device_technology
                    except Exception as e:
                        logger.info("Device Technology: ({} - {})".format(device_technology, e.message))
                # device vendor
                if device_vendor:
                    try:
                        device.device_vendor = device_vendor
                    except Exception as e:
                        logger.info("Device Vendor: ({} - {})".format(device_vendor, e.message))
                # device model
                if device_model:
                    try:
                        device.device_model = device_model
                    except Exception as e:
                        logger.info("Device Vendor: ({} - {})".format(device_model, e.message))
                # device type
                if device_type:
                    try:
                        device.device_type = device_type
                    except Exception as e:
                        logger.info("Device Type: ({} - {})".format(device_type, e.message))
                # parent
                try:
                    device.parent = Device.objects.all()[0]
                except Exception as e:
                    logger.info("Parent: ({})".format(e.message))
                # mac address
                if mac_address:
                    try:
                        device.mac_address = mac_address
                    except Exception as e:
                        logger.info("MAC Address: ({} - {})".format(mac_address, e.message))
                # netmask
                device.netmask = '255.255.255.0'
                # dhcp state
                device.dhcp_state = 'Disable'
                # host priority
                device.host_priority = 'Normal'
                # host state
                device.host_state = 'Enable'
                # latitude
                if latitude:
                    try:
                        device.latitude = latitude
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude:
                    try:
                        device.longitude = longitude
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # timezone
                device.timezone = 'Asia/Kolkata'
                # country
                device.country = 1
                # state
                if state:
                    try:
                        device.state = State.objects.get(state_name=state).id
                    except Exception as e:
                        logger.info("State: ({})".format(e.message))
                # city
                if city:
                    try:
                        device.city = City.objects.get(city_name=city).id
                    except Exception as e:
                        logger.info("City: ({})".format(e.message))
                # address
                if address:
                    try:
                        device.address = address
                    except Exception as e:
                        logger.info("Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        device.description = description
                    except Exception as e:
                        logger.info("Description: ({} - {})".format(description, e.message))
                # saving device
                try:
                    device.save()
                    return device
                except Exception as e:
                    logger.info("Device Object: ({} - {})".format(device_name, e.message))
                    return ""
            except Exception as e:
                # ---------------------------- CREATING DEVICE -------------------------------
                # device object
                device = Device()
                # device name
                if device_name:
                    try:
                        device.device_name = device_name
                    except Exception as e:
                        logger.info("Device Name: ({} - {})".format(device_name, e.message))
                # device alias
                if device_alias:
                    try:
                        device.device_alias = device_alias
                    except Exception as e:
                        logger.info("Device Alias: ({} - {})".format(device_alias, e.message))
                # machine
                if machine:
                    try:
                        device.machine = machine
                    except Exception as e:
                        logger.info("Machine: ({} - {})".format(machine, e.message))
                # site instance
                if site_instance:
                    try:
                        device.site_instance = SiteInstance.objects.get(pk=site_instance)
                    except Exception as e:
                        logger.info("Site Instance: ({} - {})".format(site_instance, e.message))
                # organization
                try:
                    device.organization = organization
                except Exception as e:
                    logger.info("Organization: ({})".format(e.message))
                # device technology
                if device_technology:
                    try:
                        device.device_technology = device_technology
                    except Exception as e:
                        logger.info("Device Technology: ({} - {})".format(device_technology, e.message))
                # device vendor
                if device_vendor:
                    try:
                        device.device_vendor = device_vendor
                    except Exception as e:
                        logger.info("Device Vendor: ({} - {})".format(device_vendor, e.message))
                # device model
                if device_model:
                    try:
                        device.device_model = device_model
                    except Exception as e:
                        logger.info("Device Vendor: ({} - {})".format(device_model, e.message))
                # device type
                if device_type:
                    try:
                        device.device_type = device_type
                    except Exception as e:
                        logger.info("Device Type: ({} - {})".format(device_type, e.message))
                # parent
                try:
                    device.parent = Device.objects.all()[0]
                except Exception as e:
                    logger.info("Parent: ({})".format(e.message))
                # ip address
                if ip_address:
                    try:
                        device.ip_address = ip_address
                    except Exception as e:
                        logger.info("IP Address: ({} - {})".format(ip_address, e.message))
                # mac address
                if mac_address:
                    try:
                        device.mac_address = mac_address
                    except Exception as e:
                        logger.info("MAC Address: ({} - {})".format(mac_address, e.message))
                # latitude
                if latitude:
                    try:
                        device.latitude = latitude
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude:
                    try:
                        device.longitude = longitude
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # timezone
                device.timezone = 'Asia/Kolkata'
                # country
                device.country = 1
                # state
                if state:
                    try:
                        device.state = State.objects.get(state_name=state).id
                    except Exception as e:
                        logger.info("State: ({})".format(e.message))
                # city
                if city:
                    try:
                        device.city = City.objects.get(city_name=city).id
                    except Exception as e:
                        logger.info("City: ({})".format(e.message))
                # address
                if address:
                    try:
                        device.address = address
                    except Exception as e:
                        logger.info("Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        device.description = description
                    except Exception as e:
                        logger.info("Description: ({} - {})".format(description, e.message))
                # is deleted
                device.is_deleted = 0
                # is added to nms
                device.is_added_to_nms = 0
                # is monitored on nms
                device.is_monitored_on_nms = 0
                # saving device
                try:
                    device.save()
                    return device
                except Exception as e:
                    logger.info("Device Object: ({} - {})".format(device_name, e.message))
                    return ""


def create_antenna(antenna_payload):
    """ Create Antenna object

    Args:
        antenna_payload (dict): {
                                    'description': 'SectorAntennacreatedon28-Sep-2014at22: 55: 03.',
                                    'mount_type': u'NA',
                                    'ip': u'10.75.158.219',
                                    'height': 28.0,
                                    'polarization': u'vertical',
                                    'gain': u'NA',
                                    'antenna_type': u'NA'
                               }

    Returns:
        antenna (class 'inventory.models.Antenna'): <Antenna: 10.75.158.219>

    """

    # dictionary containing antenna payload
    antenna_payload = antenna_payload

    # initializing variables
    name, alias, antenna_type, height, tilt, gain, mount_type, beam_width, azimuth_angle, reflector = [''] * 10
    splitter_installed, sync_splitter_used, make_of_antenna, description = [''] * 4

    # get antenna parameters
    if 'ip' in antenna_payload.keys():
        name = antenna_payload['ip'] if antenna_payload['ip'] else ""
        alias = antenna_payload['ip'] if antenna_payload['ip'] else ""
    if 'antenna_type' in antenna_payload.keys():
        antenna_type = antenna_payload['antenna_type'] if antenna_payload['antenna_type'] else ""
    if 'height' in antenna_payload.keys():
        height = antenna_payload['height'] if antenna_payload['height'] else ""
    if 'tilt' in antenna_payload.keys():
        tilt = antenna_payload['tilt'] if antenna_payload['tilt'] else ""
    if 'gain' in antenna_payload.keys():
        gain = antenna_payload['gain'] if antenna_payload['gain'] else ""
    if 'mount_type' in antenna_payload.keys():
        mount_type = antenna_payload['mount_type'] if antenna_payload['mount_type'] else ""
    if 'beam_width' in antenna_payload.keys():
        beam_width = antenna_payload['beam_width'] if antenna_payload['beam_width'] else ""
    if 'azimuth_angle' in antenna_payload.keys():
        azimuth_angle = antenna_payload['azimuth_angle'] if antenna_payload['azimuth_angle'] else ""
    if 'reflector' in antenna_payload.keys():
        reflector = antenna_payload['reflector'] if antenna_payload['reflector'] else ""
    if 'splitter_installed' in antenna_payload.keys():
        splitter_installed = antenna_payload['splitter_installed'] if antenna_payload['splitter_installed'] else ""
    if 'sync_splitter_used' in antenna_payload.keys():
        sync_splitter_used = antenna_payload['sync_splitter_used'] if antenna_payload['sync_splitter_used'] else ""
    if 'make_of_antenna' in antenna_payload.keys():
        make_of_antenna = antenna_payload['make_of_antenna'] if antenna_payload['make_of_antenna'] else ""
    if 'description' in antenna_payload.keys():
        description = antenna_payload['description'] if antenna_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ------------------------------ UPDATING ANTENNA -------------------------------
            try:
                # update antenna if it exists in database
                antenna = Antenna.objects.get(name=name)
                # alias
                if alias:
                    try:
                        antenna.alias = alias
                    except Exception as e:
                        logger.info("Antenna Alias: ({} - {})".format(alias, e.message))
                # antenna type
                if antenna_type:
                    try:
                        antenna.antenna_type = antenna_type
                    except Exception as e:
                        logger.info("Antenna Type: ({} - {})".format(antenna_type, e.message))
                # height
                if height:
                    if isinstance(height, int) or isinstance(height, float):
                        try:
                            antenna.height = height
                        except Exception as e:
                            logger.info("Antenna Height: ({} - {})".format(height, e.message))
                # tilt
                if tilt:
                    if isinstance(tilt, int) or isinstance(tilt, float):
                        try:
                            antenna.tilt = tilt
                        except Exception as e:
                            logger.info("Antenna Tilt: ({} - {})".format(tilt, e.message))
                # gain
                if gain:
                    if isinstance(gain, int) or isinstance(gain, float):
                        try:
                            antenna.gain = gain
                        except Exception as e:
                            logger.info("Antenna Gain: ({} - {})".format(gain, e.message))
                # mount type
                if mount_type:
                    try:
                        antenna.mount_type = mount_type
                    except Exception as e:
                        logger.info("Antenna Mount Type: ({} - {})".format(mount_type, e.message))
                # beam width
                if beam_width:
                    if isinstance(beam_width, int) or isinstance(beam_width, float):
                        try:
                            antenna.beam_width = beam_width
                        except Exception as e:
                            logger.info("Antenna Beamwidth: ({} - {})".format(beam_width, e.message))
                # azimuth angle
                if azimuth_angle:
                    if isinstance(azimuth_angle, int) or isinstance(azimuth_angle, float):
                        try:
                            antenna.azimuth_angle = azimuth_angle
                        except Exception as e:
                            logger.info("Azimuth Angle: ({} - {})".format(azimuth_angle, e.message))
                    else:
                        antenna.azimuth_angle = 0
                # reflector
                if reflector:
                    try:
                        antenna.reflector = reflector
                    except Exception as e:
                        logger.info("Antenna Reflector: ({} - {})".format(reflector, e.message))
                # splitter installed
                if splitter_installed:
                    try:
                        antenna.splitter_installed = splitter_installed
                    except Exception as e:
                        logger.info("Antenna Alias: ({} - {})".format(alias, e.message))
                # sync splitter installed
                if sync_splitter_used:
                    try:
                        antenna.sync_splitter_used = sync_splitter_used
                    except Exception as e:
                        logger.info("Antenna Sync Splitter Used: ({} - {})".format(sync_splitter_used, e.message))
                # make of antenna
                if make_of_antenna:
                    try:
                        antenna.make_of_antenna = make_of_antenna
                    except Exception as e:
                        logger.info("Antenna Make Of Antenna: ({} - {})".format(make_of_antenna, e.message))
                # description
                if description:
                    try:
                        antenna.description = description
                    except Exception as e:
                        logger.info("Antenna Description: ({} - {})".format(description, e.message))
                try:
                    antenna.save()
                    return antenna
                except Exception as e:
                    logger.info("Antenna Object: ({} - {})".format(name, e.message))
                    return ""
            except Exception as e:
                # ---------------------------- CREATING ANTENNA -------------------------------
                # create antenna if it doesn't exist in database
                antenna = Antenna()
                # name
                antenna.name = name
                # alias
                if alias:
                    try:
                        antenna.alias = alias
                    except Exception as e:
                        logger.info("Antenna Alias: ({} - {})".format(alias, e.message))
                # antenna type
                if antenna_type:
                    try:
                        antenna.antenna_type = antenna_type
                    except Exception as e:
                        logger.info("Antenna Type: ({} - {})".format(antenna_type, e.message))
                # height
                if height:
                    if isinstance(height, int) or isinstance(height, float):
                        try:
                            antenna.height = height
                        except Exception as e:
                            logger.info("Antenna Height: ({} - {})".format(height, e.message))
                # tilt
                if tilt:
                    if isinstance(tilt, int) or isinstance(tilt, float):
                        try:
                            antenna.tilt = tilt
                        except Exception as e:
                            logger.info("Antenna Tilt: ({} - {})".format(tilt, e.message))
                # gain
                if gain:
                    if isinstance(gain, int) or isinstance(gain, float):
                        try:
                            antenna.gain = gain
                        except Exception as e:
                            logger.info("Antenna Gain: ({} - {})".format(gain, e.message))
                # mount type
                if mount_type:
                    try:
                        antenna.mount_type = mount_type
                    except Exception as e:
                        logger.info("Antenna Mount Type: ({} - {})".format(mount_type, e.message))
                # beam width
                if beam_width:
                    if isinstance(beam_width, int) or isinstance(beam_width, float):
                        try:
                            antenna.beam_width = beam_width
                        except Exception as e:
                            logger.info("Antenna Beamwidth: ({} - {})".format(beam_width, e.message))
                # azimuth angle
                if azimuth_angle:
                    if isinstance(azimuth_angle, int) or isinstance(azimuth_angle, float):
                        try:
                            antenna.azimuth_angle = azimuth_angle
                        except Exception as e:
                            logger.info("Azimuth Angle: ({} - {})".format(azimuth_angle, e.message))
                    else:
                        antenna.azimuth_angle = 0
                else:
                    antenna.azimuth_angle = 0
                # reflector
                if reflector:
                    try:
                        antenna.reflector = reflector
                    except Exception as e:
                        logger.info("Antenna Reflector: ({} - {})".format(reflector, e.message))
                # splitter installed
                if splitter_installed:
                    try:
                        antenna.splitter_installed = splitter_installed
                    except Exception as e:
                        logger.info("Antenna Alias: ({} - {})".format(alias, e.message))
                # sync splitter installed
                if sync_splitter_used:
                    try:
                        antenna.sync_splitter_used = sync_splitter_used
                    except Exception as e:
                        logger.info("Antenna Sync Splitter Used: ({} - {})".format(sync_splitter_used, e.message))
                # make of antenna
                if make_of_antenna:
                    try:
                        antenna.make_of_antenna = make_of_antenna
                    except Exception as e:
                        logger.info("Antenna Make Of Antenna: ({} - {})".format(make_of_antenna, e.message))
                # description
                if description:
                    try:
                        antenna.description = description
                    except Exception as e:
                        logger.info("Antenna Description: ({} - {})".format(description, e.message))
                try:
                    antenna.save()
                    return antenna
                except Exception as e:
                    logger.info("Antenna Object: ({} - {})".format(name, e.message))
                    return ""


def create_backhaul(backhaul_payload):
    """ Create Backhaul object

    Args:
        backhaul_payload (dict): {
                                    'bh_configured_on': <Device: 10.175.16.199>,
                                    'description': 'Backhaulcreatedon28-Sep-2014at22: 55: 03.',
                                    'bh_connectivity': u'Onnet',
                                    'bh_circuit_id': u'IOR_166748',
                                    'pe_hostname': u'dl-con-kcl-mi07-rt01',
                                    'ip': u'10.175.16.199',
                                    'bh_type': u'Ethernet',
                                    'bh_switch': None,
                                    'pop': None,
                                    'bh_port': 0,
                                    'aggregator_port': 0,
                                    'bh_capacity': 100.0,
                                    'aggregator_port_name': u'NA',
                                    'ttsl_circuit_id': '',
                                    'pe_ip': u'192.168.192.43',
                                    'aggregator': None,
                                    'bh_port_name': u'Fa0/25'
                                }

    Returns:
        backhaul (class 'inventory.models.Backhaul'): <Backhaul: 10.75.158.219>

    """

    # dictionary containing backhaul payload
    backhaul_payload = backhaul_payload

    # initializing variables
    name, alias, bh_configured_on, bh_port_name, bh_port, bh_type, bh_switch, switch_port_name, switch_port = [''] * 9
    pop, pop_port_name, pop_port, aggregator, aggregator_port_name, aggregator_port, pe_hostname, pe_ip = [''] * 8
    bh_connectivity, bh_circuit_id, ttsl_circuit_id, dr_site, description = [''] * 5

    # get backhaul parameters
    if 'ip' in backhaul_payload.keys():
        name = backhaul_payload['ip'] if backhaul_payload['ip'] else ""
        alias = backhaul_payload['ip'] if backhaul_payload['ip'] else ""
    if 'bh_configured_on' in backhaul_payload.keys():
        bh_configured_on = backhaul_payload['bh_configured_on'] if backhaul_payload['bh_configured_on'] else ""
    if 'bh_port_name' in backhaul_payload.keys():
        bh_port_name = backhaul_payload['bh_port_name'] if backhaul_payload['bh_port_name'] else ""
    if 'bh_port' in backhaul_payload.keys():
        bh_port = backhaul_payload['bh_port'] if backhaul_payload['bh_port'] else ""
    if 'bh_type' in backhaul_payload.keys():
        bh_type = backhaul_payload['bh_type'] if backhaul_payload['bh_type'] else ""
    if 'bh_switch' in backhaul_payload.keys():
        bh_switch = backhaul_payload['bh_switch'] if backhaul_payload['bh_switch'] else ""
    if 'switch_port_name' in backhaul_payload.keys():
        switch_port_name = backhaul_payload['switch_port_name'] if backhaul_payload['switch_port_name'] else ""
    if 'switch_port' in backhaul_payload.keys():
        switch_port = backhaul_payload['switch_port'] if backhaul_payload['switch_port'] else ""
    if 'pop' in backhaul_payload.keys():
        pop = backhaul_payload['pop'] if backhaul_payload['pop'] else ""
    if 'pop_port_name' in backhaul_payload.keys():
        pop_port_name = backhaul_payload['pop_port_name'] if backhaul_payload['pop_port_name'] else ""
    if 'pop_port' in backhaul_payload.keys():
        pop_port = backhaul_payload['pop_port'] if backhaul_payload['pop_port'] else ""
    if 'aggregator' in backhaul_payload.keys():
        aggregator = backhaul_payload['aggregator'] if backhaul_payload['aggregator'] else ""
    if 'aggregator_port_name' in backhaul_payload.keys():
        aggregator_port_name = backhaul_payload['aggregator_port_name'] if backhaul_payload['aggregator_port_name'] else ""
    if 'aggregator_port' in backhaul_payload.keys():
        aggregator_port = backhaul_payload['aggregator_port'] if backhaul_payload['aggregator_port'] else ""
    if 'pe_hostname' in backhaul_payload.keys():
        pe_hostname = backhaul_payload['pe_hostname'] if backhaul_payload['pe_hostname'] else ""
    if 'pe_ip' in backhaul_payload.keys():
        pe_ip = backhaul_payload['pe_ip'] if backhaul_payload['pe_ip'] else ""
    if 'bh_connectivity' in backhaul_payload.keys():
        bh_connectivity = backhaul_payload['bh_connectivity'] if backhaul_payload['bh_connectivity'] else ""
    if 'bh_circuit_id' in backhaul_payload.keys():
        bh_circuit_id = backhaul_payload['bh_circuit_id'] if backhaul_payload['bh_circuit_id'] else ""
    if 'bh_capacity' in backhaul_payload.keys():
        pobh_capacityp = backhaul_payload['bh_capacity'] if backhaul_payload['bh_capacity'] else ""
    if 'ttsl_circuit_id' in backhaul_payload.keys():
        ttsl_circuit_id = backhaul_payload['ttsl_circuit_id'] if backhaul_payload['ttsl_circuit_id'] else ""
    if 'dr_site' in backhaul_payload.keys():
        dr_site = backhaul_payload['dr_site'] if backhaul_payload['dr_site'] else ""
    if 'description' in backhaul_payload.keys():
        description = backhaul_payload['description'] if backhaul_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ------------------------------ UPDATING BACKHAUL -------------------------------
            try:
                # update backhaul if it exists in database
                backhaul = Backhaul.objects.get(name=name)
                # alias
                if alias:
                    try:
                        backhaul.alias = alias
                    except Exception as e:
                        logger.info("BH Alias: ({} - {})".format(alias, e.message))
                # bh configured on
                if bh_configured_on:
                    try:
                        backhaul.bh_configured_on = bh_configured_on
                    except Exception as e:
                        logger.info("BH Configured On: ({} - {})".format(bh_configured_on, e.message))
                # bh port name
                if bh_port_name:
                    try:
                        backhaul.bh_port_name = bh_port_name
                    except Exception as e:
                        logger.info("BH Port Name: ({} - {})".format(bh_port_name, e.message))
                # bh port
                if bh_port:
                    try:
                        backhaul.bh_port = bh_port
                    except Exception as e:
                        logger.info("BH Port: ({} - {})".format(bh_port, e.message))
                # bh type
                if bh_type:
                    try:
                        backhaul.bh_type = bh_type
                    except Exception as e:
                        logger.info("BH Type: ({} - {})".format(bh_type, e.message))
                # bh switch
                if bh_switch:
                    try:
                        backhaul.bh_switch = bh_switch
                    except Exception as e:
                        logger.info("BH Switch: ({} - {})".format(bh_switch, e.message))
                # switch port name
                if switch_port_name:
                    try:
                        backhaul.switch_port_name = switch_port_name
                    except Exception as e:
                        logger.info("Switch Port Name: ({} - {})".format(switch_port_name, e.message))
                # switch port
                if switch_port:
                    try:
                        backhaul.switch_port = switch_port
                    except Exception as e:
                        logger.info("Switch Port: ({} - {})".format(switch_port, e.message))
                # pop
                if pop:
                    try:
                        backhaul.pop = pop
                    except Exception as e:
                        logger.info("POP: ({} - {})".format(pop, e.message))
                # pop port name
                if pop_port_name:
                    try:
                        backhaul.pop_port_name = pop_port_name
                    except Exception as e:
                        logger.info("POP Port Name: ({} - {})".format(pop_port_name, e.message))
                # pop_port
                if pop_port:
                    try:
                        backhaul.pop_port = pop_port
                    except Exception as e:
                        logger.info("POP Port: ({} - {})".format(pop_port, e.message))
                # aggregator
                if aggregator:
                    try:
                        backhaul.aggregator = aggregator
                    except Exception as e:
                        logger.info("Aggregator: ({} - {})".format(aggregator, e.message))
                # aggregator port name
                if aggregator_port_name:
                    try:
                        backhaul.aggregator_port_name = aggregator_port_name
                    except Exception as e:
                        logger.info("Aggregator Port Name: ({} - {})".format(aggregator_port_name, e.message))
                # aggregator port
                if aggregator_port:
                    try:
                        backhaul.aggregator_port = aggregator_port
                    except Exception as e:
                        logger.info("Aggregator Port: ({} - {})".format(aggregator_port, e.message))
                # pe hostname
                if pe_hostname:
                    try:
                        backhaul.pe_hostname = pe_hostname
                    except Exception as e:
                        logger.info("PE Hostname: ({} - {})".format(pe_hostname, e.message))
                # pe ip
                if pe_ip:
                    try:
                        backhaul.pe_ip = pe_ip
                    except Exception as e:
                        logger.info("PE IP: ({} - {})".format(pe_ip, e.message))
                # bh connectivity
                if bh_connectivity:
                    try:
                        backhaul.bh_connectivity = bh_connectivity
                    except Exception as e:
                        logger.info("BH Connectivity: ({} - {})".format(bh_connectivity, e.message))
                # bh circuit id
                if bh_circuit_id:
                    try:
                        backhaul.bh_circuit_id = bh_circuit_id
                    except Exception as e:
                        logger.info("BH Circuit ID: ({} - {})".format(bh_circuit_id, e.message))
                # ttsl circuit id
                if ttsl_circuit_id:
                    try:
                        backhaul.ttsl_circuit_id = ttsl_circuit_id
                    except Exception as e:
                        logger.info("BSO Circuit IB: ({} - {})".format(ttsl_circuit_id, e.message))
                # dr site
                if dr_site:
                    try:
                        backhaul.dr_site = dr_site
                    except Exception as e:
                        logger.info("DR Site: ({} - {})".format(dr_site, e.message))
                # description
                if description:
                    try:
                        backhaul.description = description
                    except Exception as e:
                        logger.info("Description: ({} - {})".format(description, e.message))
                try:
                    backhaul.save()
                    return backhaul
                except Exception as e:
                    logger.info("Backhaul Object: ({} - {})".format(name, e.message))
                    return ""
            except Exception as e:
                # ---------------------------- CREATING BACKHAUL -------------------------------
                # create backhaul if it doesn't exist in database
                backhaul = Backhaul()
                # name
                if name:
                    try:
                        backhaul.name = name
                    except Exception as e:
                        logger.info("BH Alias: ({} - {})".format(alias, e.message))
                # alias
                if alias:
                    try:
                        backhaul.alias = alias
                    except Exception as e:
                        logger.info("BH Alias: ({} - {})".format(alias, e.message))
                # bh configured on
                if bh_configured_on:
                    try:
                        backhaul.bh_configured_on = bh_configured_on
                    except Exception as e:
                        logger.info("BH Configured On: ({} - {})".format(bh_configured_on, e.message))
                # bh port name
                if bh_port_name:
                    try:
                        backhaul.bh_port_name = bh_port_name
                    except Exception as e:
                        logger.info("BH Port Name: ({} - {})".format(bh_port_name, e.message))
                # bh port
                if bh_port:
                    try:
                        backhaul.bh_port = bh_port
                    except Exception as e:
                        logger.info("BH Port: ({} - {})".format(bh_port, e.message))
                # bh type
                if bh_type:
                    try:
                        backhaul.bh_type = bh_type
                    except Exception as e:
                        logger.info("BH Type: ({} - {})".format(bh_type, e.message))
                # bh switch
                if bh_switch:
                    try:
                        backhaul.bh_switch = bh_switch
                    except Exception as e:
                        logger.info("BH Switch: ({} - {})".format(bh_switch, e.message))
                # switch port name
                if switch_port_name:
                    try:
                        backhaul.switch_port_name = switch_port_name
                    except Exception as e:
                        logger.info("Switch Port Name: ({} - {})".format(switch_port_name, e.message))
                # switch port
                if switch_port:
                    try:
                        backhaul.switch_port = switch_port
                    except Exception as e:
                        logger.info("Switch Port: ({} - {})".format(switch_port, e.message))
                # pop
                if pop:
                    try:
                        backhaul.pop = pop
                    except Exception as e:
                        logger.info("POP: ({} - {})".format(pop, e.message))
                # pop port name
                if pop_port_name:
                    try:
                        backhaul.pop_port_name = pop_port_name
                    except Exception as e:
                        logger.info("POP Port Name: ({} - {})".format(pop_port_name, e.message))
                # pop_port
                if pop_port:
                    try:
                        backhaul.pop_port = pop_port
                    except Exception as e:
                        logger.info("POP Port: ({} - {})".format(pop_port, e.message))
                # aggregator
                if aggregator:
                    try:
                        backhaul.aggregator = aggregator
                    except Exception as e:
                        logger.info("Aggregator: ({} - {})".format(aggregator, e.message))
                # aggregator port name
                if aggregator_port_name:
                    try:
                        backhaul.aggregator_port_name = aggregator_port_name
                    except Exception as e:
                        logger.info("Aggregator Port Name: ({} - {})".format(aggregator_port_name, e.message))
                # aggregator port
                if aggregator_port:
                    try:
                        backhaul.aggregator_port = aggregator_port
                    except Exception as e:
                        logger.info("Aggregator Port: ({} - {})".format(aggregator_port, e.message))
                # pe hostname
                if pe_hostname:
                    try:
                        backhaul.pe_hostname = pe_hostname
                    except Exception as e:
                        logger.info("PE Hostname: ({} - {})".format(pe_hostname, e.message))
                # pe ip
                if pe_ip:
                    try:
                        backhaul.pe_ip = pe_ip
                    except Exception as e:
                        logger.info("PE IP: ({} - {})".format(pe_ip, e.message))
                # bh connectivity
                if bh_connectivity:
                    try:
                        backhaul.bh_connectivity = bh_connectivity
                    except Exception as e:
                        logger.info("BH Connectivity: ({} - {})".format(bh_connectivity, e.message))
                # bh circuit id
                if bh_circuit_id:
                    try:
                        backhaul.bh_circuit_id = bh_circuit_id
                    except Exception as e:
                        logger.info("BH Circuit ID: ({} - {})".format(bh_circuit_id, e.message))
                # ttsl circuit id
                if ttsl_circuit_id:
                    try:
                        backhaul.ttsl_circuit_id = ttsl_circuit_id
                    except Exception as e:
                        logger.info("BSO Circuit IB: ({} - {})".format(ttsl_circuit_id, e.message))
                # dr site
                if dr_site:
                    try:
                        backhaul.dr_site = dr_site
                    except Exception as e:
                        logger.info("DR Site: ({} - {})".format(dr_site, e.message))
                # description
                if description:
                    try:
                        backhaul.description = description
                    except Exception as e:
                        logger.info("Description: ({} - {})".format(description, e.message))
                try:
                    backhaul.save()
                    return backhaul
                except Exception as e:
                    logger.info("Backhaul Object: ({} - {})".format(name, e.message))
                    return ""


def create_basestation(basestation_payload):
    """ Create BaseStation object

    Args:
        basestation_payload (dict): {
                                        'tower_height': 14.0,
                                        'description': 'BaseStationcreatedon28-Sep-2014at22: 55: 03.',
                                        'building_height': 14.0,
                                        'address': u'A-88,
                                        EastOfKailash,
                                        Delhi',
                                        'hssu_used': '',
                                        'bs_switch': <Device: 10.175.16.199>,
                                        'bh_bso': u'RadwinwithWimax',
                                        'city': u'Delhi(NewDelhi)',
                                        'name': 'east_of_kailash_dr',
                                        'longitude': 77.253333333333,
                                        'alias': u'EastOfKailash-DR',
                                        'state': u'Delhi',
                                        'backhaul': <Backhaul: 10.175.16.199>,
                                        'latitude': 28.560277777778
                                    }

    Returns:
        basestation (class 'inventory.models.BaseStation'): <BaseStation: 10.75.158.219>

    """

    # dictionary containing base station payload
    basestation_payload = basestation_payload

    # initializing variables
    name, alias, bs_site_id, bs_site_type, bs_switch, backhaul, bs_type, bh_bso, hssu_used = [''] * 9
    latitude, longitude, infra_provider, gps_type, building_height, tower_height, country, state, city = [''] * 9
    address, description = [''] * 2

    # get base station parameters
    if 'name' in basestation_payload.keys():
        name = basestation_payload['name'] if basestation_payload['name'] else ""
    if 'alias' in basestation_payload.keys():
        alias = basestation_payload['alias'] if basestation_payload['alias'] else ""
    if 'bs_site_id' in basestation_payload.keys():
        bs_site_id = basestation_payload['bs_site_id'] if basestation_payload['bs_site_id'] else ""
    if 'bs_site_type' in basestation_payload.keys():
        bs_site_type = basestation_payload['bs_site_type'] if basestation_payload['bs_site_type'] else ""
    if 'bs_switch' in basestation_payload.keys():
        bs_switch = basestation_payload['bs_switch'] if basestation_payload['bs_switch'] else ""
    if 'backhaul' in basestation_payload.keys():
        backhaul = basestation_payload['backhaul'] if basestation_payload['backhaul'] else ""
    if 'bs_type' in basestation_payload.keys():
        bs_type = basestation_payload['bs_type'] if basestation_payload['bs_type'] else ""
    if 'bh_bso' in basestation_payload.keys():
        bh_bso = basestation_payload['bh_bso'] if basestation_payload['bh_bso'] else ""
    if 'switch_port' in basestation_payload.keys():
        switch_port = basestation_payload['switch_port'] if basestation_payload['switch_port'] else ""
    if 'latitude' in basestation_payload.keys():
        latitude = basestation_payload['latitude'] if basestation_payload['latitude'] else ""
    if 'longitude' in basestation_payload.keys():
        longitude = basestation_payload['longitude'] if basestation_payload['longitude'] else ""
    if 'pop_port' in basestation_payload.keys():
        pop_port = basestation_payload['pop_port'] if basestation_payload['pop_port'] else ""
    if 'infra_provider' in basestation_payload.keys():
        infra_provider = basestation_payload['infra_provider'] if basestation_payload['infra_provider'] else ""
    if 'gps_type' in basestation_payload.keys():
        gps_type = basestation_payload['gps_type'] if basestation_payload['gps_type'] else ""
    if 'building_height' in basestation_payload.keys():
        building_height = basestation_payload['building_height'] if basestation_payload['building_height'] else ""
    if 'tower_height' in basestation_payload.keys():
        tower_height = basestation_payload['tower_height'] if basestation_payload['tower_height'] else ""
    if 'country' in basestation_payload.keys():
        country = basestation_payload['country'] if basestation_payload['country'] else ""
    if 'state' in basestation_payload.keys():
        state = basestation_payload['state'] if basestation_payload['state'] else ""
    if 'city' in basestation_payload.keys():
        city = basestation_payload['city'] if basestation_payload['city'] else ""
    if 'address' in basestation_payload.keys():
        address = basestation_payload['address'] if basestation_payload['address'] else ""
    if 'description' in basestation_payload.keys():
        description = basestation_payload['description'] if basestation_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING BASE STATION -----------------------------
            try:
                # update basestation if it exists in database
                basestation = BaseStation.objects.get(name=name)
                # alias
                if alias:
                    try:
                        basestation.alias = alias
                    except Exception as e:
                        logger.info("BH Alias: ({} - {})".format(alias, e.message))
                # bs site id
                if bs_site_id:
                    try:
                        basestation.bs_site_id = bs_site_id
                    except Exception as e:
                        logger.info("BS Site ID: ({} - {})".format(bs_site_id, e.message))
                # bs site type
                if bs_site_type:
                    try:
                        basestation.bs_site_type = bs_site_type
                    except Exception as e:
                        logger.info("BS Site Type: ({} - {})".format(bs_site_type, e.message))
                # bs switch
                if bs_switch:
                    try:
                        basestation.bs_switch = bs_switch
                    except Exception as e:
                        logger.info("BS Switch: ({} - {})".format(bs_switch, e.message))
                # backhaul
                if backhaul:
                    try:
                        basestation.backhaul = backhaul
                    except Exception as e:
                        logger.info("Backhaul: ({} - {})".format(backhaul, e.message))
                # bs type
                if bs_type:
                    try:
                        basestation.bs_type = bs_type
                    except Exception as e:
                        logger.info("BS Type: ({} - {})".format(bs_type, e.message))
                # bh bso
                if bh_bso:
                    try:
                        basestation.bh_bso = bh_bso
                    except Exception as e:
                        logger.info("BH BSO: ({} - {})".format(bh_bso, e.message))
                # hssu used
                if hssu_used:
                    try:
                        basestation.hssu_used = hssu_used
                    except Exception as e:
                        logger.info("HSSU Used: ({} - {})".format(hssu_used, e.message))
                # latitude
                if latitude:
                    if isinstance(latitude, int) or isinstance(latitude, float):
                        try:
                            basestation.latitude = latitude
                        except Exception as e:
                            logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude:
                    if isinstance(longitude, int) or isinstance(longitude, float):
                        try:
                            basestation.longitude = longitude
                        except Exception as e:
                            logger.info("Longitude: ({} - {})".format(longitude, e.message))
                # infra provider
                if infra_provider:
                    try:
                        basestation.infra_provider = infra_provider
                    except Exception as e:
                        logger.info("Infra Provider: ({} - {})".format(infra_provider, e.message))
                # gps type
                if gps_type:
                    try:
                        basestation.gps_type = gps_type
                    except Exception as e:
                        logger.info("GPS Type: ({} - {})".format(gps_type, e.message))
                # building height
                if building_height:
                    if isinstance(building_height, int) or isinstance(building_height, float):
                        try:
                            basestation.building_height = building_height
                        except Exception as e:
                            logger.info("Building Height: ({} - {})".format(building_height, e.message))
                # tower height
                if tower_height:
                    if isinstance(tower_height, int) or isinstance(tower_height, float):
                        try:
                            basestation.tower_height = tower_height
                        except Exception as e:
                            logger.info("Tower Height: ({} - {})".format(tower_height, e.message))
                # country
                basestation.country = 1
                # state
                if state:
                    try:
                        basestation.state = State.objects.get(state_name=state).id
                    except Exception as e:
                        logger.info(" BS State: ({})".format(e.message))
                # city
                if city:
                    try:
                        basestation.city = City.objects.get(city_name=city).id
                    except Exception as e:
                        logger.info("BS City: ({})".format(e.message))
                # address
                if address:
                    try:
                        basestation.address = address
                    except Exception as e:
                        logger.info("BS Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        basestation.description = description
                    except Exception as e:
                        logger.info("BS Description: ({} - {})".format(description, e.message))
                try:
                    basestation.save()
                    return basestation
                except Exception as e:
                    logger.info("Backhaul Object: ({} - {})".format(name, e.message))
                    return ""
            except Exception as e:
                # ---------------------------- CREATING BASE STATION -------------------------------
                # create basestation if it doesn't exist in database
                basestation = BaseStation()
                # name
                if name:
                    try:
                        basestation.name = name
                    except Exception as e:
                        logger.info("BH Name: ({} - {})".format(name, e.message))
                # alias
                if alias:
                    try:
                        basestation.alias = alias
                    except Exception as e:
                        logger.info("BH Alias: ({} - {})".format(alias, e.message))
                # bs site id
                if bs_site_id:
                    try:
                        basestation.bs_site_id = bs_site_id
                    except Exception as e:
                        logger.info("BS Site ID: ({} - {})".format(bs_site_id, e.message))
                # bs site type
                if bs_site_type:
                    try:
                        basestation.bs_site_type = bs_site_type
                    except Exception as e:
                        logger.info("BS Site Type: ({} - {})".format(bs_site_type, e.message))
                # bs switch
                if bs_switch:
                    try:
                        basestation.bs_switch = bs_switch
                    except Exception as e:
                        logger.info("BS Switch: ({} - {})".format(bs_switch, e.message))
                # backhaul
                if backhaul:
                    try:
                        basestation.backhaul = backhaul
                    except Exception as e:
                        logger.info("Backhaul: ({} - {})".format(backhaul, e.message))
                # bs type
                if bs_type:
                    try:
                        basestation.bs_type = bs_type
                    except Exception as e:
                        logger.info("BS Type: ({} - {})".format(bs_type, e.message))
                # bh bso
                if bh_bso:
                    try:
                        basestation.bh_bso = bh_bso
                    except Exception as e:
                        logger.info("BH BSO: ({} - {})".format(bh_bso, e.message))
                # hssu used
                if hssu_used:
                    try:
                        basestation.hssu_used = hssu_used
                    except Exception as e:
                        logger.info("HSSU Used: ({} - {})".format(hssu_used, e.message))
                # latitude
                if latitude:
                    try:
                        basestation.latitude = latitude
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude:
                    try:
                        basestation.longitude = longitude
                    except Exception as e:
                        logger.info("Longitude: ({} - {})".format(longitude, e.message))
                # infra provider
                if infra_provider:
                    try:
                        basestation.infra_provider = infra_provider
                    except Exception as e:
                        logger.info("Infra Provider: ({} - {})".format(infra_provider, e.message))
                # gps type
                if gps_type:
                    try:
                        basestation.gps_type = gps_type
                    except Exception as e:
                        logger.info("GPS Type: ({} - {})".format(gps_type, e.message))
                # building height
                if building_height:
                    try:
                        basestation.building_height = building_height
                    except Exception as e:
                        logger.info("Building Height: ({} - {})".format(building_height, e.message))
                # tower height
                if tower_height:
                    try:
                        basestation.tower_height = tower_height
                    except Exception as e:
                        logger.info("Tower Height: ({} - {})".format(tower_height, e.message))
                # country
                basestation.country = 1
                # state
                if state:
                    try:
                        basestation.state = State.objects.get(state_name=state).id
                    except Exception as e:
                        logger.info(" BS State: ({})".format(e.message))
                # city
                if city:
                    try:
                        basestation.city = City.objects.get(city_name=city).id
                    except Exception as e:
                        logger.info("BS City: ({})".format(e.message))
                # address
                if address:
                    try:
                        basestation.address = address
                    except Exception as e:
                        logger.info("BS Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        basestation.description = description
                    except Exception as e:
                        logger.info("BS Description: ({} - {})".format(description, e.message))
                try:
                    basestation.save()
                    return basestation
                except Exception as e:
                    logger.info("Base Station Object: ({} - {})".format(name, e.message))
                    return ""


def create_sector(sector_payload):
    """ Create Sector object

    Args:
        sector_payload (dict): {
                                    'description': 'Sectorcreatedon28-Sep-2014at22: 55: 03.',
                                    'antenna': <Antenna: 10.75.158.219>,
                                    'ip': u'10.75.158.219',
                                    'sector_configured_on': <Device: 10.75.158.219>,
                                    'base_station': <BaseStation: east_of_kailash_dr>,
                                    'bs_technology': 2
                               }

    Returns:
        sector (class 'inventory.models.Sector'): <Sector: 10.75.158.219>

    """

    # dictionary containing sector payload
    sector_payload = sector_payload

    # initializing variables
    name, alias, sector_id, base_station, bs_technology, sector_configured_on, sector_configured_on_port = [''] * 7
    antenna, mrc, tx_power, rx_power, rf_bandwidth, frame_length, cell_radius, frequency, modulation = [''] * 9
    description = ''

    # get sector parameters
    if 'ip' in sector_payload.keys():
        name = sector_payload['ip'] if sector_payload['ip'] else ""
        alias = sector_payload['ip'] if sector_payload['ip'] else ""
    if 'sector_id' in sector_payload.keys():
        sector_id = sector_payload['sector_id'] if sector_payload['sector_id'] else ""
    if 'base_station' in sector_payload.keys():
        base_station = sector_payload['base_station'] if sector_payload['base_station'] else ""
    if 'bs_technology' in sector_payload.keys():
        bs_technology = sector_payload['bs_technology'] if sector_payload['bs_technology'] else ""
    if 'sector_configured_on' in sector_payload.keys():
        sector_configured_on = sector_payload['sector_configured_on'] if sector_payload['sector_configured_on'] else ""
    if 'sector_configured_on_port' in sector_payload.keys():
        sector_configured_on_port = sector_payload['sector_configured_on_port'] if sector_payload['sector_configured_on_port'] else ""
    if 'antenna' in sector_payload.keys():
        antenna = sector_payload['antenna'] if sector_payload['antenna'] else ""
    if 'mrc' in sector_payload.keys():
        mrc = sector_payload['mrc'] if sector_payload['mrc'] else ""
    if 'tx_power' in sector_payload.keys():
        tx_power = sector_payload['tx_power'] if sector_payload['tx_power'] else ""
    if 'rx_power' in sector_payload.keys():
        rx_power = sector_payload['rx_power'] if sector_payload['rx_power'] else ""
    if 'rf_bandwidth' in sector_payload.keys():
        rf_bandwidth = sector_payload['rf_bandwidth'] if sector_payload['rf_bandwidth'] else ""
    if 'frame_length' in sector_payload.keys():
        frame_length = sector_payload['frame_length'] if sector_payload['frame_length'] else ""
    if 'cell_radius' in sector_payload.keys():
        cell_radius = sector_payload['cell_radius'] if sector_payload['cell_radius'] else ""
    if 'frequency' in sector_payload.keys():
        frequency = sector_payload['frequency'] if sector_payload['frequency'] else ""
    if 'modulation' in sector_payload.keys():
        modulation = sector_payload['modulation'] if sector_payload['modulation'] else ""
    if 'description' in sector_payload.keys():
        description = sector_payload['description'] if sector_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING SECTOR -----------------------------
            try:
                # update sector if it exists in database
                sector = Sector.objects.get(name=name)
                # alias
                if alias:
                    try:
                        sector.alias = alias
                    except Exception as e:
                        logger.info("Sector Alias: ({} - {})".format(alias, e.message))
                # sector id
                if sector_id:
                    try:
                        sector.sector_id = sector_id
                    except Exception as e:
                        logger.info("Sector ID: ({} - {})".format(sector_id, e.message))
                # base station
                if base_station:
                    try:
                        sector.base_station = base_station
                    except Exception as e:
                        logger.info("Sector Base Station: ({} - {})".format(base_station, e.message))
                # bs technology
                if bs_technology:
                    try:
                        sector.bs_technology = DeviceTechnology.objects.get(pk=bs_technology)
                    except Exception as e:
                        logger.info("BS Technology: ({} - {})".format(bs_technology, e.message))
                # sector configured on
                if sector_configured_on:
                    try:
                        sector.sector_configured_on = sector_configured_on
                    except Exception as e:
                        logger.info("Sector Configured On: ({} - {})".format(sector_configured_on, e.message))
                # sector configured on port
                if sector_configured_on_port:
                    try:
                        sector.sector_configured_on_port = sector_configured_on_port
                    except Exception as e:
                        logger.info("Sector Configured On Port: ({} - {})".format(sector_configured_on_port, e.message))
                # antenna
                if antenna:
                    try:
                        sector.antenna = antenna
                    except Exception as e:
                        logger.info("Sector Antenna: ({} - {})".format(antenna, e.message))
                # mrc
                if mrc:
                    try:
                        sector.mrc = mrc
                    except Exception as e:
                        logger.info("MRC: ({} - {})".format(mrc, e.message))
                # tx power
                if tx_power:
                    if isinstance(tx_power, int) or isinstance(tx_power, float):
                        try:
                            sector.tx_power = tx_power
                        except Exception as e:
                            logger.info("TX Power: ({} - {})".format(tx_power, e.message))
                # rx power
                if rx_power:
                    if isinstance(rx_power, int) or isinstance(rx_power, float):
                        try:
                            sector.rx_power = rx_power
                        except Exception as e:
                            logger.info("RX Power: ({} - {})".format(rx_power, e.message))
                # rf bandwidth
                if rf_bandwidth:
                    if isinstance(rf_bandwidth, int) or isinstance(rf_bandwidth, float):
                        try:
                            sector.rf_bandwidth = rf_bandwidth
                        except Exception as e:
                            logger.info("RF Bandwidth: ({} - {})".format(rf_bandwidth, e.message))
                # frame length
                if frame_length:
                    if isinstance(frame_length, int) or isinstance(frame_length, float):
                        try:
                            sector.frame_length = frame_length
                        except Exception as e:
                            logger.info("Frame Length: ({} - {})".format(frame_length, e.message))
                # cell radius
                if cell_radius:
                    if isinstance(cell_radius, int) or isinstance(cell_radius, float):
                        try:
                            sector.cell_radius = cell_radius
                        except Exception as e:
                            logger.info("Cell Radius: ({} - {})".format(cell_radius, e.message))
                # frequency
                if frequency:
                    if isinstance(frequency, int) or isinstance(frequency, float):
                        try:
                            sector.frequency = frequency
                        except Exception as e:
                            logger.info("Frequency: ({} - {})".format(frequency, e.message))
                # modulation
                if modulation:
                    try:
                        sector.modulation = modulation
                    except Exception as e:
                        logger.info("Modulation: ({} - {})".format(modulation, e.message))
                # description
                if description:
                    try:
                        sector.description = description
                    except Exception as e:
                        logger.info("Sector Description: ({} - {})".format(description, e.message))
                try:
                    sector.save()
                    return sector
                except Exception as e:
                    logger.info("Sector Object: ({} - {})".format(name, e.message))
                    return ""
            except Exception as e:
                # ---------------------------- CREATING BASE STATION -------------------------------
                # create sector if it doesn't exist in database
                sector = Sector()
                # name
                if name:
                    try:
                        sector.name = name
                    except Exception as e:
                        logger.info("Sector Name: ({} - {})".format(name, e.message))
                # alias
                if alias:
                    try:
                        sector.alias = alias
                    except Exception as e:
                        logger.info("Sector Alias: ({} - {})".format(alias, e.message))
                # sector id
                if sector_id:
                    try:
                        sector.sector_id = sector_id
                    except Exception as e:
                        logger.info("Sector ID: ({} - {})".format(sector_id, e.message))
                # base station
                if base_station:
                    try:
                        sector.base_station = base_station
                    except Exception as e:
                        logger.info("Sector Base Station: ({} - {})".format(base_station, e.message))
                # bs technology
                if bs_technology:
                    try:
                        sector.bs_technology = DeviceTechnology.objects.get(pk=bs_technology)
                    except Exception as e:
                        logger.info("BS Technology: ({} - {})".format(bs_technology, e.message))
                # sector configured on
                if sector_configured_on:
                    try:
                        sector.sector_configured_on = sector_configured_on
                    except Exception as e:
                        logger.info("Sector Configured On: ({} - {})".format(sector_configured_on, e.message))
                # sector configured on port
                if sector_configured_on_port:
                    try:
                        sector.sector_configured_on_port = sector_configured_on_port
                    except Exception as e:
                        logger.info("Sector Configured On Port: ({} - {})".format(sector_configured_on_port, e.message))
                # antenna
                if antenna:
                    try:
                        sector.antenna = antenna
                    except Exception as e:
                        logger.info("Sector Antenna: ({} - {})".format(antenna, e.message))
                # mrc
                if mrc:
                    try:
                        sector.mrc = mrc
                    except Exception as e:
                        logger.info("MRC: ({} - {})".format(mrc, e.message))
                # tx power
                if tx_power:
                    if isinstance(tx_power, int) or isinstance(tx_power, float):
                        try:
                            sector.tx_power = tx_power
                        except Exception as e:
                            logger.info("TX Power: ({} - {})".format(tx_power, e.message))
                # rx power
                if rx_power:
                    if isinstance(rx_power, int) or isinstance(rx_power, float):
                        try:
                            sector.rx_power = rx_power
                        except Exception as e:
                            logger.info("RX Power: ({} - {})".format(rx_power, e.message))
                # rf bandwidth
                if rf_bandwidth:
                    if isinstance(rf_bandwidth, int) or isinstance(rf_bandwidth, float):
                        try:
                            sector.rf_bandwidth = rf_bandwidth
                        except Exception as e:
                            logger.info("RF Bandwidth: ({} - {})".format(rf_bandwidth, e.message))
                # frame length
                if frame_length:
                    if isinstance(frame_length, int) or isinstance(frame_length, float):
                        try:
                            sector.frame_length = frame_length
                        except Exception as e:
                            logger.info("Frame Length: ({} - {})".format(frame_length, e.message))
                # cell radius
                if cell_radius:
                    if isinstance(cell_radius, int) or isinstance(cell_radius, float):
                        try:
                            sector.cell_radius = cell_radius
                        except Exception as e:
                            logger.info("Cell Radius: ({} - {})".format(cell_radius, e.message))
                # frequency
                if frequency:
                    if isinstance(frequency, int) or isinstance(frequency, float):
                        try:
                            sector.frequency = frequency
                        except Exception as e:
                            logger.info("Frequency: ({} - {})".format(frequency, e.message))
                # modulation
                if modulation:
                    try:
                        sector.modulation = modulation
                    except Exception as e:
                        logger.info("Modulation: ({} - {})".format(modulation, e.message))
                # description
                if description:
                    try:
                        sector.description = description
                    except Exception as e:
                        logger.info("Sector Description: ({} - {})".format(description, e.message))
                try:
                    sector.save()
                    return sector
                except Exception as e:
                    logger.info("Sector Object: ({} - {})".format(name, e.message))
                    return ""


def create_customer(customer_payload):
    """ Create Customer object

    Args:
        customer_payload (dict): {
                                    'alias': u'Lotte-India-Corp-Ltd',
                                    'description': 'SSCustomercreatedon28-Sep-2014at22: 55: 03.',
                                    'name': 'lotte_india_corp_ltd',
                                    'address': u'LOTTEINDIACORPORATIONLTD.,
                                    FLATNO.301,
                                    IIIrdFLOOR,
                                    SHAYOGBUILDING-58,
                                    NEHRUPALACE,
                                    ,
                                    NEWDELHI-110019.,
                                    NewDelhi,
                                    DelhiIndia110019'
                                }

    Returns:
        customer (class 'inventory.models.Customer'): <Customer: 10.75.158.219>

    """

    # dictionary containing customer payload
    customer_payload = customer_payload

    # initializing variables
    name, alias, address, description = [''] * 4
    
    # get customer parameters
    if 'name' in customer_payload.keys():
        name = customer_payload['name'] if customer_payload['name'] else ""
    if 'alias' in customer_payload.keys():
        alias = customer_payload['alias'] if customer_payload['alias'] else ""
    if 'address' in customer_payload.keys():
        address = customer_payload['address'] if customer_payload['address'] else ""
    if 'description' in customer_payload.keys():
        description = customer_payload['description'] if customer_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING CUSTOMER -----------------------------
            try:
                # update customer if it exists in database
                customer = Customer.objects.get(name=name)
                # alias
                if alias:
                    try:
                        customer.alias = alias
                    except Exception as e:
                        logger.info("Customer Alias: ({} - {})".format(alias, e.message))
                # address
                if address:
                    try:
                        customer.address = address
                    except Exception as e:
                        logger.info("Customer Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        customer.description = description
                    except Exception as e:
                        logger.info("Customer Description: ({} - {})".format(description, e.message))
                try:
                    customer.save()
                    return customer
                except Exception as e:
                    logger.info("Customer Object: ({} - {})".format(name, e.message))
                    return ""
            except Exception as e:
                # ---------------------------- CREATING CUSTOMER -------------------------------
                # create sector if it doesn't exist in database
                customer = Customer()
                # name
                if name:
                    try:
                        customer.name = name
                    except Exception as e:
                        logger.info("Customer Name: ({} - {})".format(name, e.message))
                # alias
                if alias:
                    try:
                        customer.alias = alias
                    except Exception as e:
                        logger.info("Customer Alias: ({} - {})".format(alias, e.message))
                # address
                if address:
                    try:
                        customer.address = address
                    except Exception as e:
                        logger.info("Customer Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        customer.description = description
                    except Exception as e:
                        logger.info("Customer Description: ({} - {})".format(description, e.message))
                try:
                    customer.save()
                    return customer
                except Exception as e:
                    logger.info("Customer Object: ({} - {})".format(name, e.message))
                    return ""


def create_substation(substation_payload):
    """ Create SubStation object

    Args:
        substation_payload (dict): {
                                        'tower_height': 15.0,
                                        'description': 'SubStationcreatedon28-Sep-2014at22: 55: 03.',
                                        'building_height': 31.0,
                                        'address': u'LOTTEINDIACORPORATIONLTD.,
                                        FLATNO.301,
                                        IIIrdFLOOR,
                                        SHAYOGBUILDING-58,
                                        NEHRUPALACE,
                                        ,
                                        NEWDELHI-110019.,
                                        NewDelhi,
                                        DelhiIndia110019',
                                        'device': <Device: 10.75.158.220>,
                                        'cable_length': 45.0,
                                        'city': u'Delhi(NewDelhi)',
                                        'name': '091newd623009178956',
                                        'antenna': <Antenna: 10.75.158.220>,
                                        'ethernet_extender': u'NA',
                                        'longitude': 77.25227777777778,
                                        'alias': u'10.75.158.220',
                                        'state': u'Delhi',
                                        'mac_address': u'00: 15: 67: da: 1a: 29',
                                        'latitude': 28.548944444444444
                                   }

    Returns:
        substation (class 'inventory.models.SubStation'): <SubStation: 10.75.158.219>

    """

    # dictionary containing substation payload
    substation_payload = substation_payload

    # initializing variables
    name, alias, device, antenna, version, serial_no, building_height, tower_height, ethernet_extender = [''] * 9
    cable_length, latitude, longitude, mac_address, country, state, city, address, description = [''] * 9

    # get substation parameters
    if 'name' in substation_payload.keys():
        name = substation_payload['name'] if substation_payload['name'] else ""
    if 'alias' in substation_payload.keys():
        alias = substation_payload['alias'] if substation_payload['alias'] else ""
    if 'device' in substation_payload.keys():
        device = substation_payload['device'] if substation_payload['device'] else ""
    if 'antenna' in substation_payload.keys():
        antenna = substation_payload['antenna'] if substation_payload['antenna'] else ""
    if 'version' in substation_payload.keys():
        version = substation_payload['version'] if substation_payload['version'] else ""
    if 'serial_no' in substation_payload.keys():
        serial_no = substation_payload['serial_no'] if substation_payload['serial_no'] else ""
    if 'building_height' in substation_payload.keys():
        building_height = substation_payload['building_height'] if substation_payload['building_height'] else ""
    if 'tower_height' in substation_payload.keys():
        tower_height = substation_payload['tower_height'] if substation_payload['tower_height'] else ""
    if 'ethernet_extender' in substation_payload.keys():
        ethernet_extender = substation_payload['ethernet_extender'] if substation_payload['ethernet_extender'] else ""
    if 'cable_length' in substation_payload.keys():
        cable_length = substation_payload['cable_length'] if substation_payload['cable_length'] else ""
    if 'latitude' in substation_payload.keys():
        latitude = substation_payload['latitude'] if substation_payload['latitude'] else ""
    if 'longitude' in substation_payload.keys():
        longitude = substation_payload['longitude'] if substation_payload['longitude'] else ""
    if 'mac_address' in substation_payload.keys():
        mac_address = substation_payload['mac_address'] if substation_payload['mac_address'] else ""
    if 'country' in substation_payload.keys():
        country = substation_payload['country'] if substation_payload['country'] else ""
    if 'state' in substation_payload.keys():
        state = substation_payload['state'] if substation_payload['state'] else ""
    if 'city' in substation_payload.keys():
        city = substation_payload['city'] if substation_payload['city'] else ""
    if 'address' in substation_payload.keys():
        address = substation_payload['address'] if substation_payload['address'] else ""
    if 'description' in substation_payload.keys():
        description = substation_payload['description'] if substation_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING SUB STATION -----------------------------
            try:
                # update substation if it exists in database
                substation = SubStation.objects.get(name=name)
                # alias
                if alias:
                    try:
                        substation.alias = alias
                    except Exception as e:
                        logger.info("Sub Station Alias: ({} - {})".format(alias, e.message))
                # device
                if device:
                    try:
                        substation.device = device
                    except Exception as e:
                        logger.info("Sub Station Device: ({} - {})".format(device, e.message))
                # antenna
                if antenna:
                    try:
                        substation.antenna = antenna
                    except Exception as e:
                        logger.info("Sub Station Antenna: ({} - {})".format(antenna, e.message))
                # version
                if version:
                    try:
                        substation.version = version
                    except Exception as e:
                        logger.info("Sub Station Version: ({} - {})".format(version, e.message))
                # serial no
                if serial_no:
                    try:
                        substation.serial_no = serial_no
                    except Exception as e:
                        logger.info("Sub Station Serial No.: ({} - {})".format(serial_no, e.message))
                # building_height
                if building_height:
                    if isinstance(building_height, int) or isinstance(building_height, float):
                        try:
                            substation.building_height = building_height
                        except Exception as e:
                            logger.info("Sub Station Building Height: ({} - {})".format(building_height, e.message))
                # tower_height
                if tower_height:
                    if isinstance(tower_height, int) or isinstance(tower_height, float):
                        try:
                            substation.tower_height = tower_height
                        except Exception as e:
                            logger.info("Sub Station Tower Height: ({} - {})".format(antenna, e.message))
                # ethernet extender
                if ethernet_extender:
                    try:
                        substation.ethernet_extender = ethernet_extender
                    except Exception as e:
                        logger.info("Sub Station Ethernet Extender: ({} - {})".format(ethernet_extender, e.message))
                # cable length
                if cable_length:
                    if isinstance(cable_length, int) or isinstance(cable_length, float):
                        try:
                            substation.cable_length = cable_length
                        except Exception as e:
                            logger.info("Sub Station Cable Length: ({} - {})".format(cable_length, e.message))
                # latitude
                if latitude:
                    if isinstance(latitude, int) or isinstance(latitude, float):
                        try:
                            substation.latitude = latitude
                        except Exception as e:
                            logger.info("Sub Station Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude:
                    if isinstance(longitude, int) or isinstance(longitude, float):
                        try:
                            substation.longitude = longitude
                        except Exception as e:
                            logger.info("Sub Station Longitude: ({} - {})".format(longitude, e.message))
                # mac_address
                if mac_address:
                    try:
                        substation.mac_address = mac_address
                    except Exception as e:
                        logger.info("Sub Station MAC Address: ({} - {})".format(mac_address, e.message))
                # country
                substation.country = 1
                # state
                if state:
                    try:
                        substation.state = State.objects.get(state_name=state).id
                    except Exception as e:
                        logger.info("Sub Station BS State: ({})".format(e.message))
                # city
                if city:
                    try:
                        substation.city = City.objects.get(city_name=city).id
                    except Exception as e:
                        logger.info("Sub Station BS City: ({})".format(e.message))
                # description
                if description:
                    try:
                        substation.description = description
                    except Exception as e:
                        logger.info("Sub Station Sector Description: ({} - {})".format(description, e.message))
                try:
                    substation.save()
                    return substation
                except Exception as e:
                    logger.info("Sub Station Sector Object: ({} - {})".format(name, e.message))
                    return ""
            except Exception as e:
                # ---------------------------- CREATING BASE STATION -------------------------------
                # create substation if it doesn't exist in database
                substation = SubStation()
                # name
                if name:
                    try:
                        substation.name = name
                    except Exception as e:
                        logger.info("Sub Station Name: ({} - {})".format(name, e.message))
                # alias
                if alias:
                    try:
                        substation.alias = alias
                    except Exception as e:
                        logger.info("Sub Station Alias: ({} - {})".format(alias, e.message))
                # device
                if device:
                    try:
                        substation.device = device
                    except Exception as e:
                        logger.info("Sub Station Device: ({} - {})".format(device, e.message))
                # antenna
                if antenna:
                    try:
                        substation.antenna = antenna
                    except Exception as e:
                        logger.info("Sub Station Antenna: ({} - {})".format(antenna, e.message))
                # version
                if version:
                    try:
                        substation.version = version
                    except Exception as e:
                        logger.info("Sub Station Version: ({} - {})".format(version, e.message))
                # serial no
                if serial_no:
                    try:
                        substation.serial_no = serial_no
                    except Exception as e:
                        logger.info("Sub Station Serial No.: ({} - {})".format(serial_no, e.message))
                # building_height
                if building_height:
                    if isinstance(building_height, int) or isinstance(building_height, float):
                        try:
                            substation.building_height = building_height
                        except Exception as e:
                            logger.info("Sub Station Building Height: ({} - {})".format(building_height, e.message))
                # tower_height
                if tower_height:
                    if isinstance(tower_height, int) or isinstance(tower_height, float):
                        try:
                            substation.tower_height = tower_height
                        except Exception as e:
                            logger.info("Sub Station Tower Height: ({} - {})".format(antenna, e.message))
                # ethernet extender
                if ethernet_extender:
                    try:
                        substation.ethernet_extender = ethernet_extender
                    except Exception as e:
                        logger.info("Sub Station Ethernet Extender: ({} - {})".format(ethernet_extender, e.message))
                # cable length
                if cable_length:
                    if isinstance(cable_length, int) or isinstance(cable_length, float):
                        try:
                            substation.cable_length = cable_length
                        except Exception as e:
                            logger.info("Sub Station Cable Length: ({} - {})".format(cable_length, e.message))
                # latitude
                if latitude:
                    if isinstance(latitude, int) or isinstance(latitude, float):
                        try:
                            substation.latitude = latitude
                        except Exception as e:
                            logger.info("Sub Station Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude:
                    if isinstance(longitude, int) or isinstance(longitude, float):
                        try:
                            substation.longitude = longitude
                        except Exception as e:
                            logger.info("Sub Station Longitude: ({} - {})".format(longitude, e.message))
                # mac_address
                if mac_address:
                    try:
                        substation.mac_address = mac_address
                    except Exception as e:
                        logger.info("Sub Station MAC Address: ({} - {})".format(mac_address, e.message))
                # country
                substation.country = 1
                # state
                if state:
                    try:
                        substation.state = State.objects.get(state_name=state).id
                    except Exception as e:
                        logger.info("Sub Station BS State: ({})".format(e.message))
                # city
                if city:
                    try:
                        substation.city = City.objects.get(city_name=city).id
                    except Exception as e:
                        logger.info("Sub Station BS City: ({})".format(e.message))
                # description
                if description:
                    try:
                        substation.description = description
                    except Exception as e:
                        logger.info("Sub Station Sector Description: ({} - {})".format(description, e.message))
                try:
                    substation.save()
                    return substation
                except Exception as e:
                    logger.info("Sub Station Object: ({} - {})".format(name, e.message))
                    return ""


def create_circuit(circuit_payload):
    """ Create Circuit object

    Args:
        circuit_payload (dict): {
                                        'sector': <Sector: 10.75.158.219>,
                                        'description': 'Circuitcreatedon28-Sep-2014at22: 55: 03.',
                                        'date_of_acceptance': '',
                                        'circuit_id': u'091NEWD623009178956',
                                        'qos_bandwidth': 256.0,
                                        'sub_station': <SubStation: 091newd623009178956>,
                                        'dl_rssi_during_acceptance': u'NA',
                                        'customer': <Customer: lotte_india_corp_ltd>,
                                        'throughput_during_acceptance': u'NA',
                                        'name': '091newd623009178956',
                                        'alias': u'091NEWD623009178956'
                                    }

    Returns:
        circuit (class 'inventory.models.Circuit'): <Circuit: 10.75.158.219>

    """

    # dictionary containing circuit payload
    circuit_payload = circuit_payload

    # initializing variables
    name, alias, circuit_type, circuit_id, sector, customer, sub_station, qos_bandwidth = [''] * 8
    dl_rssi_during_acceptance, dl_cinr_during_acceptance, jitter_value_during_acceptance = [''] * 3
    throughput_during_acceptance, date_of_acceptance, description = [''] * 3

    # get circuit parameters
    if 'name' in circuit_payload.keys():
        name = circuit_payload['name'] if circuit_payload['name'] else ""
    if 'alias' in circuit_payload.keys():
        alias = circuit_payload['alias'] if circuit_payload['alias'] else ""
    if 'circuit_type' in circuit_payload.keys():
        circuit_type = circuit_payload['circuit_type'] if circuit_payload['circuit_type'] else ""
    if 'circuit_id' in circuit_payload.keys():
        circuit_id = circuit_payload['circuit_id'] if circuit_payload['circuit_id'] else ""
    if 'sector' in circuit_payload.keys():
        sector = circuit_payload['sector'] if circuit_payload['sector'] else ""
    if 'customer' in circuit_payload.keys():
        customer = circuit_payload['customer'] if circuit_payload['customer'] else ""
    if 'sub_station' in circuit_payload.keys():
        sub_station = circuit_payload['sub_station'] if circuit_payload['sub_station'] else ""
    if 'qos_bandwidth' in circuit_payload.keys():
        qos_bandwidth = circuit_payload['qos_bandwidth'] if circuit_payload['qos_bandwidth'] else ""
    if 'dl_rssi_during_acceptance' in circuit_payload.keys():
        dl_rssi_during_acceptance = circuit_payload['dl_rssi_during_acceptance'] if circuit_payload['dl_rssi_during_acceptance'] else ""
    if 'dl_cinr_during_acceptance' in circuit_payload.keys():
        dl_cinr_during_acceptance = circuit_payload['dl_cinr_during_acceptance'] if circuit_payload['dl_cinr_during_acceptance'] else ""
    if 'jitter_value_during_acceptance' in circuit_payload.keys():
        jitter_value_during_acceptance = circuit_payload['jitter_value_during_acceptance'] if circuit_payload['jitter_value_during_acceptance'] else ""
    if 'throughput_during_acceptance' in circuit_payload.keys():
        throughput_during_acceptance = circuit_payload['throughput_during_acceptance'] if circuit_payload['throughput_during_acceptance'] else ""
    if 'date_of_acceptance' in circuit_payload.keys():
        date_of_acceptance = circuit_payload['date_of_acceptance'] if circuit_payload['date_of_acceptance'] else ""
    if 'description' in circuit_payload.keys():
        description = circuit_payload['description'] if circuit_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING CIRCUIT -----------------------------
            try:
                # update circuit if it exists in database
                circuit = Circuit.objects.get(name=name)
                # alias
                if alias:
                    try:
                        circuit.alias = alias
                    except Exception as e:
                        logger.info("Circuit Alias: ({} - {})".format(alias, e.message))
                # circuit type
                if circuit_type:
                    try:
                        circuit.circuit_type = circuit_type
                    except Exception as e:
                        logger.info("Circuit Type: ({} - {})".format(circuit_type, e.message))
                # circuit id
                if circuit_id:
                    try:
                        circuit.circuit_id = circuit_id
                    except Exception as e:
                        logger.info("Circuit ID: ({} - {})".format(circuit_id, e.message))
                # sector
                if sector:
                    try:
                        circuit.sector = sector
                    except Exception as e:
                        logger.info("Sector: ({} - {})".format(sector, e.message))
                # customer
                if customer:
                    try:
                        circuit.customer = customer
                    except Exception as e:
                        logger.info("Customer: ({} - {})".format(customer, e.message))
                # sub station
                if sub_station:
                    try:
                        circuit.sub_station = sub_station
                    except Exception as e:
                        logger.info("Sub Station: ({} - {})".format(sub_station, e.message))
                # qos bandwidth
                if qos_bandwidth:
                    if isinstance(qos_bandwidth, int) or isinstance(qos_bandwidth, float):
                        try:
                            circuit.qos_bandwidth = qos_bandwidth
                        except Exception as e:
                            logger.info("QOS (BW): ({} - {})".format(qos_bandwidth, e.message))
                # dl rssi during acceptance
                if dl_rssi_during_acceptance:
                    try:
                        circuit.dl_rssi_during_acceptance = dl_rssi_during_acceptance
                    except Exception as e:
                        logger.info("RSSI During Acceptance: ({} - {})".format(dl_rssi_during_acceptance, e.message))
                # dl cinr during acceptance
                if dl_cinr_during_acceptance:
                    try:
                        circuit.dl_cinr_during_acceptance = dl_cinr_during_acceptance
                    except Exception as e:
                        logger.info("CINR During Acceptance: ({} - {})".format(dl_cinr_during_acceptance, e.message))
                # jitter value during acceptance
                if jitter_value_during_acceptance:
                    try:
                        circuit.jitter_value_during_acceptance = jitter_value_during_acceptance
                    except Exception as e:
                        logger.info("Jitter Value During Acceptance: ({} - {})".format(jitter_value_during_acceptance, e.message))
                # throughput during acceptance
                if throughput_during_acceptance:
                    try:
                        circuit.throughput_during_acceptance = throughput_during_acceptance
                    except Exception as e:
                        logger.info("Throughput During Acceptance: ({} - {})".format(throughput_during_acceptance, e.message))
                # date_of_acceptance
                if date_of_acceptance:
                    try:
                        circuit.date_of_acceptance = date_of_acceptance
                    except Exception as e:
                        logger.info("Date Of Acceptance: ({} - {})".format(date_of_acceptance, e.message))
                # description
                if description:
                    try:
                        circuit.description = description
                    except Exception as e:
                        logger.info("Circuit Description: ({} - {})".format(description, e.message))
                try:
                    circuit.save()
                    return circuit
                except Exception as e:
                    logger.info("Circuit Object: ({} - {})".format(name, e.message))
                    return ""
            except Exception as e:
                # ---------------------------- CREATING CIRCUIT -------------------------------
                # create circuit if it doesn't exist in database
                circuit = Circuit()
                # name
                if name:
                    try:
                        circuit.name = name
                    except Exception as e:
                        logger.info("Circuit Name: ({} - {})".format(name, e.message))
                # alias
                if alias:
                    try:
                        circuit.alias = alias
                    except Exception as e:
                        logger.info("Circuit Alias: ({} - {})".format(alias, e.message))
                # circuit type
                if circuit_type:
                    try:
                        circuit.circuit_type = circuit_type
                    except Exception as e:
                        logger.info("Circuit Type: ({} - {})".format(circuit_type, e.message))
                # circuit id
                if circuit_id:
                    try:
                        circuit.circuit_id = circuit_id
                    except Exception as e:
                        logger.info("Circuit ID: ({} - {})".format(circuit_id, e.message))
                # sector
                if sector:
                    try:
                        circuit.sector = sector
                    except Exception as e:
                        logger.info("Sector: ({} - {})".format(sector, e.message))
                # customer
                if customer:
                    try:
                        circuit.customer = customer
                    except Exception as e:
                        logger.info("Customer: ({} - {})".format(customer, e.message))
                # sub station
                if sub_station:
                    try:
                        circuit.sub_station = sub_station
                    except Exception as e:
                        logger.info("Sub Station: ({} - {})".format(sub_station, e.message))
                # qos bandwidth
                if qos_bandwidth:
                    if isinstance(qos_bandwidth, int) or isinstance(qos_bandwidth, float):
                        try:
                            circuit.qos_bandwidth = qos_bandwidth
                        except Exception as e:
                            logger.info("QOS (BW): ({} - {})".format(qos_bandwidth, e.message))
                # dl rssi during acceptance
                if dl_rssi_during_acceptance:
                    try:
                        circuit.dl_rssi_during_acceptance = dl_rssi_during_acceptance
                    except Exception as e:
                        logger.info("RSSI During Acceptance: ({} - {})".format(dl_rssi_during_acceptance, e.message))
                # dl cinr during acceptance
                if dl_cinr_during_acceptance:
                    try:
                        circuit.dl_cinr_during_acceptance = dl_cinr_during_acceptance
                    except Exception as e:
                        logger.info("CINR During Acceptance: ({} - {})".format(dl_cinr_during_acceptance, e.message))
                # jitter value during acceptance
                if jitter_value_during_acceptance:
                    try:
                        circuit.jitter_value_during_acceptance = jitter_value_during_acceptance
                    except Exception as e:
                        logger.info("Jitter Value During Acceptance: ({} - {})".format(jitter_value_during_acceptance, e.message))
                # throughput during acceptance
                if throughput_during_acceptance:
                    try:
                        circuit.throughput_during_acceptance = throughput_during_acceptance
                    except Exception as e:
                        logger.info("Throughput During Acceptance: ({} - {})".format(throughput_during_acceptance, e.message))
                # date_of_acceptance
                if date_of_acceptance:
                    try:
                        circuit.date_of_acceptance = date_of_acceptance
                    except Exception as e:
                        logger.info("Date Of Acceptance: ({} - {})".format(date_of_acceptance, e.message))
                # description
                if description:
                    try:
                        circuit.description = description
                    except Exception as e:
                        logger.info("Circuit Description: ({} - {})".format(description, e.message))
                try:
                    circuit.save()
                    return circuit
                except Exception as e:
                    logger.info("Circuit Object: ({} - {})".format(name, e.message))
                    return ""


def get_ptp_machine(ip):
    """ Get PTP Machine object

    Args:
        ip (unicode): u'10.1.231.179'

    Returns:
        machine (class 'machine.models.Machine'): <Machine: default>

    """

    # machine
    machine = ""

    try:
        # check whether IP is public or private
        test_ip = IP(ip)
        if test_ip.iptype() == 'PRIVATE':
            machine = Machine.objects.get(name='vrfprv')
        elif test_ip.iptype() == 'PUBLIC':
            machine = Machine.objects.get(name='pub')
        else:
            machine = ""
    except Exception as e:
        logger.info(e.message)

    return machine


def get_port_name_and_number(ports):
    """ Get Port Name and Number of first port

    Args:
        ports (unicode): u'Gi0/1,Gi0/2'

    Returns:
        [port_name, port_number] (list): ['Gi0', '1']

    """

    try:
        port = ports.split(',', 1)[0]
        port_name, port_number = port.rsplit('/', 1)
        return [port_name, port_number]
    except Exception as e:
        return ""


def validate_date(date_string):
    """ Get date string if it's a valid 'date' else return empty string

    Args:
        date_string (unicode): u'15-Aug-2014'

    Returns:
        date_string (str): '15-Aug-2014'

    """

    # 'date of acceptance' validation (must be like '15-Aug-2014')
    if date_string:
        try:
            datetime.datetime.strptime(date_string, '%d-%b-%Y')
            date_string = date_string
        except Exception as e:
            date_string = ""

        return date_string


def name_sanitizer(name):
    """ Clean and remove all special characters form string and replace them (special characters) from underscore

    Args:
        name (unicode): u'Maniyar Complex'

    Returns:
        name (str): 'maniyar_complex'

    """

    # remove all non-word characters (everything except numbers and letters)
    output = re.sub(r"[^\w\s+]", '_', str(name))
    # replace all runs of whitespace with a single underscore, convert to lower chars and then strip '_'
    output = re.sub(r"\s+", '_', output).lower().strip('_')
    # return output

    return str(output)


class GISInventoryBulkImportList(ListView):
    """
    Generic Class based View to List the GISInventoryBulkImports.
    """

    model = GISInventoryBulkImport
    template_name = 'bulk_import/gis_inventory_bulk_imports_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """
        context = super(GISInventoryBulkImportList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'original_filename', 'sTitle': 'Inventory Sheet', 'sWidth': 'null', },
            {'mData': 'valid_filename', 'sTitle': 'Valid Sheet', 'sWidth': 'null', },
            {'mData': 'invalid_filename', 'sTitle': 'Invalid Sheet', 'sWidth': 'null', },
            {'mData': 'status', 'sTitle': 'Status', 'sWidth': 'null', },
            {'mData': 'sheet_name', 'sTitle': 'Sheet Name', 'sWidth': 'null', },
            {'mData': 'technology', 'sTitle': 'Technology', 'sWidth': 'null', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'null', },
            {'mData': 'uploaded_by', 'sTitle': 'Uploaded By', 'sWidth': 'null', },
            {'mData': 'added_on', 'sTitle': 'Added On', 'sWidth': 'null', },
            {'mData': 'modified_on', 'sTitle': 'Modified On', 'sWidth': 'null', },
        ]
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class GISInventoryBulkImportListingTable(BaseDatatableView):
    """
    A generic class based view for the gis inventory bulk import data table rendering.

    """
    model = GISInventoryBulkImport
    columns = ['original_filename', 'valid_filename', 'invalid_filename', 'status', 'sheet_name', 'technology', 'description', 'uploaded_by', 'added_on', 'modified_on']
    order_columns = ['original_filename', 'valid_filename', 'invalid_filename', 'status', 'sheet_name', 'technology', 'description', 'uploaded_by', 'added_on', 'modified_on']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return GISInventoryBulkImport.objects.values(*self.columns+['id'])

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
                excel_green = static("img/ms-office-icons/excel_2013_green.png")
                excel_grey = static("img/ms-office-icons/excel_2013_grey.png")
                excel_red = static("img/ms-office-icons/excel_2013_red.png")
                excel_light_green = static("img/ms-office-icons/excel_2013_light_green.png")
                # excel_blue = static("img/ms-office-icons/excel_2013_blue.png")

                # show 'Success', 'Pending' and 'Failed' in status
                try:
                    if not dct.get('status'):
                        dct.update(status='Pending')
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('status') == 0:
                        dct.update(status='Pending')
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('status') == 1:
                        dct.update(status='Success')
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('status') == 2:
                        dct.update(status='Failed')
                except Exception as e:
                    logger.info(e.message)

                # show icon instead of url in data tables view
                try:
                    dct.update(original_filename='<a href="/{0}"><img src="{1}" style="float:left; display:block; height:25px; width:25px;">'.format(dct.pop('original_filename'), excel_light_green))
                except Exception as e:
                    logger.info(e.message)
                try:
                    if dct.get('status') == "Success":
                        dct.update(valid_filename='<a href="/{0}"><img src="{1}" style="float:left; display:block; height:25px; width:25px;">'.format(dct.pop('valid_filename'), excel_green))
                    else:
                        dct.update(valid_filename='<img src="{0}" style="float:left; display:block; height:25px; width:25px;">'.format(excel_grey))
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('status') == "Success":
                        dct.update(invalid_filename='<a href="/{0}"><img src="{1}" style="float:left; display:block; height:25px; width:25px;">'.format(dct.pop('invalid_filename'), excel_red))
                    else:
                        dct.update(invalid_filename='<img src="{0}" style="float:left; display:block; height:25px; width:25px;">'.format(excel_grey))
                except Exception as e:
                    logger.info(e.message)

                # show user full name in uploded by field
                try:
                    if dct.get('uploaded_by'):
                        user = User.objects.get(pk=2)
                        dct.update(uploaded_by='{} {}'.format(user.first_name, user.last_name))
                except Exception as e:
                    logger.info(e.message)

            except Exception as e:
                logger.info(e)
            dct.update(actions='<a href="/bulk_import/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                                <a href="/bulk_import/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>\
                                <a href="/bulk_import/bulk_upload_valid_data/{0}"><i class="fa fa-flash text-dark"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.

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
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret


class GISInventoryBulkImportDelete(DeleteView):
    """
    Class based View to delete the GISInventoryBulkImport
    """
    model = GISInventoryBulkImport
    template_name = 'bulk_import/gis_bulk_import_delete.html'
    success_url = reverse_lazy('gis_inventory_bulk_import_list')

    def delete(self, request, *args, **kwargs):
        # bulk import object
        bi_obj = self.get_object()

        # remove original file if it exists
        try:
            os.remove(bi_obj.original_filename)
        except Exception as e:
            logger.info(e.message)

        # remove valid rows file if it exists
        try:
            os.remove(bi_obj.valid_filename)
        except Exception as e:
            logger.info(e.message)

        # remove invalid rows file if it exists
        try:
            os.remove(bi_obj.invalid_filename)
        except Exception as e:
            logger.info(e.message)

        # delete entry from database
        bi_obj.delete()
        return HttpResponseRedirect(GISInventoryBulkImportDelete.success_url)


class GISInventoryBulkImportUpdate(UpdateView):
    """
    Class based view to update GISInventoryBulkImport .
    """
    template_name = 'bulk_import/gis_bulk_import_update.html'
    model = GISInventoryBulkImport
    form_class = GISInventoryBulkImportEditForm
    success_url = reverse_lazy('gis_inventory_bulk_import_list')






