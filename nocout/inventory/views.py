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
from nocout.settings import GISADMIN, NOCOUT_USER, MEDIA_ROOT, MEDIA_URL
from nocout.utils.util import DictDiffer
from models import Inventory, DeviceTechnology, IconSettings, LivePollingSettings, ThresholdConfiguration, \
    ThematicSettings, GISInventoryBulkImport, UserThematicSettings
from forms import InventoryForm, IconSettingsForm, LivePollingSettingsForm, ThresholdConfigurationForm, \
    ThematicSettingsForm, GISInventoryBulkImportForm, GISInventoryBulkImportEditForm
from organization.models import Organization
from site_instance.models import SiteInstance
from user_group.models import UserGroup
from user_profile.models import UserProfile
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit
from forms import AntennaForm, BaseStationForm, BackhaulForm, SectorForm, CustomerForm, SubStationForm, CircuitForm
from device.models import Country, State, City, Device
from django.contrib.staticfiles.templatetags.staticfiles import static
from user_profile.models import UserProfile
import xlrd
import xlwt
import logging
from django.template import RequestContext
from tasks import validate_gis_inventory_excel_sheet, bulk_upload_ptp_inventory, bulk_upload_pmp_sm_inventory, \
    bulk_upload_pmp_bs_inventory, bulk_upload_ptp_bh_inventory, bulk_upload_wimax_bs_inventory, \
    bulk_upload_wimax_ss_inventory

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
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'user_group__name', 'sTitle': 'User Group', 'sWidth': 'auto', },
            {'mData': 'organization__name', 'sTitle': 'Organization', 'sWidth': 'auto', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto', },]

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
    columns = ['alias', 'user_group__name', 'organization__name', 'description']
    order_columns = ['alias', 'user_group__name', 'organization__name', 'description']

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
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'height', 'sTitle': 'Height', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'polarization', 'sTitle': 'Polarization', 'sWidth': 'auto', },
            {'mData': 'tilt', 'sTitle': 'Tilt', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
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
    columns = ['alias', 'height', 'polarization', 'tilt', 'beam_width', 'azimuth_angle']
    order_columns = ['alias', 'height', 'polarization', 'tilt', 'beam_width', 'azimuth_angle']

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
        verb_string = "Create Antenna : %s" %(self.object.alias)
        action.send(self.request.user, verb=verb_string, action_object=self.object)
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
            verb_string = 'Update Antenna : %s, ' % (self.object.alias) + ', ' .join(
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
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            # {'mData': 'bs_technology__alias', 'sTitle': 'Technology', 'sWidth': 'auto', },
            {'mData': 'bs_site_id', 'sTitle': 'Site ID', 'sWidth': 'auto', },
            {'mData': 'bs_switch__device_alias', 'sTitle': 'BS Switch', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'backhaul__name', 'sTitle': 'Backhaul', 'sWidth': 'auto', },
            {'mData': 'bs_type', 'sTitle': 'BS Type', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'building_height', 'sTitle': 'Building Height', 'sWidth': 'auto', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
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
    columns = ['alias', 'bs_site_id',
               'bs_switch__device_alias', 'backhaul__name', 'bs_type', 'building_height', 'description']
    order_columns = ['alias', 'bs_site_id',
                     'bs_switch__device_alias', 'backhaul__name', 'bs_type', 'building_height', 'description']

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
        verb_string = "Create Base Station : %s" %(self.object.alias)
        action.send(self.request.user, verb=verb_string, action_object=self.object)
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
            verb_string = 'Update Base Station : %s, ' % (self.object.alias) + ', '.join(
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
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'bh_configured_on__device_alias', 'sTitle': 'Backhaul Configured On', 'sWidth': 'auto', },
            {'mData': 'bh_port', 'sTitle': 'Backhaul Port', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'bh_type', 'sTitle': 'Backhaul Type', 'sWidth': 'auto', },
            {'mData': 'pop__device_alias', 'sTitle': 'POP', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'pop_port', 'sTitle': 'POP Port', 'sWidth': 'auto', },
            {'mData': 'bh_connectivity', 'sTitle': 'Connectivity', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'bh_circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', },
            {'mData': 'bh_capacity', 'sTitle': 'Capacity', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
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
    columns = ['alias', 'bh_configured_on__device_alias', 'bh_port', 'bh_type', 'pop__device_alias', 'pop_port',
               'bh_connectivity', 'bh_circuit_id', 'bh_capacity']
    order_columns = ['alias', 'bh_configured_on__device_alias', 'bh_port', 'bh_type', 'pop__device_alias',
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
        verb_string = "Create Backhaul : %s" %(self.object.alias)
        action.send(self.request.user, verb=verb_string, action_object=self.object)
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
            verb_string = 'Updated Backhaul : %s, ' % (self.object.alias) + ', '.join(
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
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'bs_technology__alias', 'sTitle': 'Technology', 'sWidth': 'auto', },
            {'mData': 'sector_id', 'sTitle': 'ID', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'sector_configured_on__device_alias', 'sTitle': 'Sector Configured On', 'sWidth': 'auto', },
            {'mData': 'sector_configured_on_port__name', 'sTitle': 'Sector Configured On Port', 'sWidth': 'auto',
             'sClass': 'hidden-xs'},
            {'mData': 'base_station__alias', 'sTitle': 'Base Station', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'antenna__alias', 'sTitle': 'Antenna', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'mrc', 'sTitle': 'MRC', 'sWidth': 'auto', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
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
    columns = ['alias', 'bs_technology__alias' ,'sector_id', 'sector_configured_on__device_alias',
            'base_station__alias', 'sector_configured_on_port__name', 'antenna__alias', 'mrc', 'description']
    order_columns = ['alias', 'bs_technology__alias' ,'sector_id', 'sector_configured_on__device_alias',
            'base_station__alias', 'sector_configured_on_port__name', 'antenna__alias', 'mrc', 'description']

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
        verb_string = "Create Sector : %s" %(self.object.alias)
        action.send(self.request.user, verb=verb_string, action_object=self.object)
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
            verb_string = 'Update Sector : %s, ' % (self.object.alias) + ', '.join(
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
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'address', 'sTitle': 'Address', 'sWidth': 'auto', 'sClass': 'hidden-xs','bSortable': False},
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto', 'bSortable': False},
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
    columns = ['alias', 'address', 'description']
    order_columns = ['alias']

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
        verb_string = "Create Customer : %s" %(self.object.alias)
        action.send(self.request.user, verb=verb_string, action_object=self.object)
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
            verb_string = 'Update Customer : %s, ' % (self.object.alias) + ', '.join(
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
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'device__device_alias', 'sTitle': 'Device', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'antenna__alias', 'sTitle': 'Antenna', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'version', 'sTitle': 'Version', 'sWidth': 'auto', },
            {'mData': 'serial_no', 'sTitle': 'Serial No.', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'building_height', 'sTitle': 'Building Height', 'sWidth': 'auto', },
            {'mData': 'tower_height', 'sTitle': 'Tower Height', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'city__name', 'sTitle': 'City', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'state__name', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs','bSortable': False},
            {'mData': 'address', 'sTitle': 'Address', 'sWidth': 'auto', 'bSortable': False},
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto', 'sClass': 'hidden-xs','bSortable': False},
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
    columns = ['alias', 'device__device_alias', 'antenna__alias', 'version', 'serial_no', 'building_height',
               'tower_height', 'city', 'state', 'address', 'description']
    order_columns = ['alias', 'device__device_alias', 'antenna__alias', 'version', 'serial_no', 'building_height',
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
        verb_string = "Create Sub Station : %s" %(self.object.alias)
        action.send(self.request.user, verb=verb_string, action_object=self.object)
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
            verb_string = 'Updaete Sub Station : %s, ' % (self.object.alias) + ', '.join(
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
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto'},
            {'mData': 'sector__base_station__alias', 'sTitle': 'Base Station', 'sWidth': 'auto'},
            {'mData': 'sector__alias', 'sTitle': 'Sector', 'sWidth': 'auto', },
            {'mData': 'customer__alias', 'sTitle': 'Customer', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'sub_station__alias', 'sTitle': 'Sub Station', 'sWidth': 'auto', },
            {'mData': 'date_of_acceptance', 'sTitle': 'Date of Acceptance', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto',  'sClass': 'hidden-xs'}
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
    columns = ['alias', 'circuit_id','sector__base_station__alias', 'sector__alias', 'customer__alias',
               'sub_station__alias', 'date_of_acceptance', 'description']
    order_columns = ['alias', 'circuit_id','sector__base_station__alias', 'sector__alias', 'customer__alias',
                     'sub_station__alias', 'date_of_acceptance', 'description']

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value

        Args:
            self (class 'inventory.views.CircuitListingTable'): <inventory.views.CircuitListingTable object>
            qs (class 'django.db.models.query.ValuesQuerySet'):
                                                [
                                                    {
                                                        'name': u'091pond030008938479',
                                                        'customer__name': u'roots_corporation_ltd',
                                                        'date_of_acceptance': None,
                                                        'circuit_id': u'091POND030008938479',
                                                        'alias': u'091POND030008938479',
                                                        'sector__name': u'115.111.183.115',
                                                        'sub_station__name': u'091pond030008938479',
                                                        'sector__base_station__name': u'mission_street__ttsl',
                                                        'id': 13136L,
                                                        'description': u'Circuitcreatedon30-Sep-2014at18: 19: 28.'
                                                    },
                                                    {
                                                        'name': u'091newd623009151684',
                                                        'customer__name': u'usha_international_limited',
                                                        'date_of_acceptance': None,
                                                        'circuit_id': u'091NEWD623009151684',
                                                        'alias': u'091NEWD623009151684',
                                                        'sector__name': u'10.75.164.19',
                                                        'sub_station__name': u'091newd623009151684',
                                                        'sector__base_station__name': u'alipur_ii',
                                                        'id': 13137L,
                                                        'description': u'Circuitcreatedon30-Sep-2014at18: 19: 28.'
                                                    },
                                                    {
                                                        'name': u'091prak623008993022',
                                                        'customer__name': u'itc_limited',
                                                        'date_of_acceptance': None,
                                                        'circuit_id': u'091PRAK623008993022',
                                                        'alias': u'091PRAK623008993022',
                                                        'sector__name': None,
                                                        'sub_station__name': u'091prak623008993022',
                                                        'sector__base_station__name': None,
                                                        'id': 13138L,
                                                        'description': u'Circuitcreatedon30-Sep-2014at18: 19: 28.'
                                                    },
                                                    {
                                                        'name': u'091hyde623009000750',
                                                        'customer__name': u'nufuture_digital__india__limited',
                                                        'date_of_acceptance': None,
                                                        'circuit_id': u'091HYDE623009000750',
                                                        'alias': u'091HYDE623009000750',
                                                        'sector__name': u'172.25.117.187',
                                                        'sub_station__name': u'091hyde623009000750',
                                                        'sector__base_station__name': u'fern_hills',
                                                        'id': 13139L,
                                                        'description': u'Circuitcreatedon30-Sep-2014at18: 19: 28.'
                                                    }
                                                ]
        Returns:
            qs (class 'django.db.models.query.ValuesQuerySet'):
                                                            [
                                                                {
                                                                    'name': u'091agra623006651037',
                                                                    'customer__name': u'fortis_health_management',
                                                                    'date_of_acceptance': None,
                                                                    'circuit_id': u'091AGRA623006651037',
                                                                    'alias': u'091AGRA623006651037',
                                                                    'sector__name': None,
                                                                    'sub_station__name': u'091agra623006651037',
                                                                    'sector__base_station__name': None,
                                                                    'id': 15013L,
                                                                    'description': u'Circuitcreatedon30-Sep-2014at18: 19: 28.'
                                                                }
                                                            ]

        """

        sSearch = self.request.GET.get('sSearch', None)

        # self.columns is a list of columns e.g. ['name', 'alias', 'circuit_id', 'sector__base_station__name',
        # 'sector__name', 'customer__name', 'sub_station__name', 'date_of_acceptance', 'description']

        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                # avoid search on 'date_of_acceptance'
                if column == 'date_of_acceptance':
                    continue
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
        verb_string = "Create Circuit : %s" %(self.object.alias)
        action.send(self.request.user, verb=verb_string, action_object=self.object)
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
            verb_string = 'Updatte Circuit : %s, ' % (self.object.alias) + ', '.join(
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
            {'mData': 'alias',            'sTitle': 'Alias',              'sWidth': 'auto'},
            {'mData': 'upload_image',     'sTitle': 'Image',       'sWidth': 'auto'},
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
    columns = ['alias', 'upload_image']
    order_columns = ['alias', 'upload_image']

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
        verb_string = "Create Icon Setting : %s" %(self.object.alias)
        action.send(self.request.user, verb=verb_string, action_object=self.object)
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
            verb_string = 'Update Icon Settings : %s, ' % (self.object.alias) + ', '.join(
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
            {'mData': 'alias',                   'sTitle': 'Alias',             'sWidth': 'auto'},
            {'mData': 'technology__alias',       'sTitle': 'Technology',        'sWidth': 'auto'},
            {'mData': 'service__alias',          'sTitle': 'Service',           'sWidth': 'auto'},
            {'mData': 'data_source__alias',      'sTitle': 'Data Source',       'sWidth': 'auto'},
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
    columns = ['alias', 'technology__alias', 'service__alias', 'data_source__alias']
    order_columns = ['alias', 'technology__alias', 'service__alias', 'data_source__alias']

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
        verb_string = "Create Live Polling Setting : %s" %(self.object.alias)
        action.send(self.request.user, verb=version, action_object=self.object)
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
            verb_string = 'Update Live Polling Settings : %s, ' % (self.object.alias) + ', '.join(
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
            {'mData': 'alias',                          'sTitle': 'Alias',                  'sWidth': 'auto'},
            {'mData': 'live_polling_template__alias',   'sTitle': 'Live Polling Template',  'sWidth': 'auto'},
            ]
        user_id = self.request.user.id
        #if user is superadmin or gisadmin
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ThresholdConfigurationListingTable(BaseDatatableView):
    """
    Class based View to render ThresholdConfiguration Data table.
    """
    model = ThresholdConfiguration
    columns = ['alias', 'live_polling_template__alias']
    order_columns = ['alias', 'live_polling_template__alias']

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
            {'mData': 'alias',                   'sTitle': 'Alias',                     'sWidth': 'auto'},
            {'mData': 'threshold_template',      'sTitle': 'Threshold Template',        'sWidth': 'auto'},
            {'mData': 'icon_settings',           'sTitle': 'Icons Range',               'sWidth': 'auto'},
            {'mData': 'user_selection',          'sTitle': 'Setting Selection',         'sWidth': 'auto'},]

        # user_id = self.request.user.id

        #if user is superadmin or gisadmin
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', })

        context['datatable_headers'] = json.dumps(datatable_headers)

        is_global = False
        if 'admin' in self.request.path:
            is_global = True

        context['is_global'] = json.dumps(is_global)

        return context


class ThematicSettingsListingTable(BaseDatatableView):
    """
    Class based View to render Thematic Settings Data table.
    """
    model = ThematicSettings
    columns = ['alias', 'threshold_template', 'icon_settings']
    order_columns = ['alias', 'threshold_template']
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

    def get_initial_queryset(self, technology="P2P"):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        is_global = 1
        if self.request.GET.get('admin'):
            is_global = 0

        return ThematicSettings.objects.filter(
        threshold_template__in=ThresholdConfiguration.objects.filter(
            live_polling_template__id__in=LivePollingSettings.objects.filter(
                technology__name=technology).values('id')).values('id')).filter(is_global=is_global).values(*self.columns + ['id'])

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


            ts_obj = ThematicSettings.objects.get(id= int(thematic_setting_id))
            user_obj = UserProfile.objects.get(id= user_profile_id)
            tech_obj = ts_obj.threshold_template.live_polling_template.technology

            to_delete = UserThematicSettings.objects.filter(user_profile=user_obj, thematic_technology=tech_obj)
            if len(to_delete):
                to_delete.delete()

            uts = UserThematicSettings(user_profile= user_obj,
                                       thematic_template=ts_obj,
                                       thematic_technology=tech_obj
            )
            uts.save()
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
        if not os.path.exists(MEDIA_ROOT + 'inventory_files/original'):
            os.makedirs(MEDIA_ROOT + 'inventory_files/original')

        filepath = MEDIA_ROOT + 'inventory_files/original/{}_{}'.format(full_time, uploaded_file.name)
        relative_filepath = 'inventory_files/original/{}_{}'.format(full_time, uploaded_file.name)
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
            gis_bulk_obj.original_filename = relative_filepath
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

            # update data import status in GISInventoryBulkImport model
            try:
                gis_obj = GISInventoryBulkImport.objects.get(pk=kwargs['id'])
                gis_obj.upload_status = 1
                gis_obj.save()
            except Exception as e:
                logger.info(e.message)

            if 'sheetname' in kwargs:
                if kwargs['sheetname'] == 'PTP':
                    result = bulk_upload_ptp_inventory.delay(kwargs['id'], organization, kwargs['sheettype'])
                elif kwargs['sheetname'] == 'PTP BH':
                    result = bulk_upload_ptp_bh_inventory.delay(kwargs['id'], organization, kwargs['sheettype'])
                elif kwargs['sheetname'] == 'PMP BS':
                    result = bulk_upload_pmp_bs_inventory.delay(kwargs['id'], organization, kwargs['sheettype'])
                elif kwargs['sheetname'] == 'PMP SM':
                    result = bulk_upload_pmp_sm_inventory.delay(kwargs['id'], organization, kwargs['sheettype'])
                elif kwargs['sheetname'] == 'Wimax BS':
                    result = bulk_upload_wimax_bs_inventory.delay(kwargs['id'], organization, kwargs['sheettype'])
                elif kwargs['sheetname'] == 'Wimax SS':
                    result = bulk_upload_wimax_ss_inventory.delay(kwargs['id'], organization, kwargs['sheettype'])
                else:
                    result = ""
        except Exception as e:
            logger.info("Current User Organization:", e.message)

        return HttpResponseRedirect('/bulk_import/')


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
            {'mData': 'original_filename', 'sTitle': 'Inventory Sheet', 'sWidth': 'auto', },
            {'mData': 'valid_filename', 'sTitle': 'Valid Sheet', 'sWidth': 'auto', },
            {'mData': 'invalid_filename', 'sTitle': 'Invalid Sheet', 'sWidth': 'auto', },
            {'mData': 'status', 'sTitle': 'Status', 'sWidth': 'auto', },
            {'mData': 'sheet_name', 'sTitle': 'Sheet Name', 'sWidth': 'auto', },
            {'mData': 'technology', 'sTitle': 'Technology', 'sWidth': 'auto', },
            {'mData': 'upload_status', 'sTitle': 'Upload Status', 'sWidth': 'auto', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto', },
            {'mData': 'uploaded_by', 'sTitle': 'Uploaded By', 'sWidth': 'auto', },
            {'mData': 'added_on', 'sTitle': 'Added On', 'sWidth': 'auto', },
            {'mData': 'modified_on', 'sTitle': 'Modified On', 'sWidth': 'auto', },
        ]
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})
        if self.request.user.is_superuser:
            datatable_headers.append({'mData':'bulk_upload_actions', 'sTitle':'Inventory Upload', 'sWidth':'5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class GISInventoryBulkImportListingTable(BaseDatatableView):
    """
    A generic class based view for the gis inventory bulk import data table rendering.

    """
    model = GISInventoryBulkImport
    columns = ['original_filename', 'valid_filename', 'invalid_filename', 'status', 'sheet_name', 'technology', 'upload_status', 'description', 'uploaded_by', 'added_on', 'modified_on']
    order_columns = ['original_filename', 'valid_filename', 'invalid_filename', 'status', 'sheet_name', 'technology', 'upload_status', 'description', 'uploaded_by', 'added_on', 'modified_on']

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

                # show 'Success', 'Pending' and 'Failed' in upload status
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

                # show 'Not Yet', 'Pending', 'Success', 'Failed' in import status
                try:
                    if not dct.get('upload_status'):
                        dct.update(upload_status='Not Yet')
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('upload_status') == 0:
                        dct.update(upload_status='Not Yet')
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('upload_status') == 1:
                        dct.update(upload_status='Pending')
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('upload_status') == 2:
                        dct.update(upload_status='Success')
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('upload_status') == 3:
                        dct.update(upload_status='Failed')
                except Exception as e:
                    logger.info(e.message)

                # show icon instead of url in data tables view
                try:
                    dct.update(original_filename='<a href="{}{}"><img src="{}" style="float:left; display:block; height:25px; width:25px;">'.format(MEDIA_URL, dct.pop('original_filename'), excel_light_green))
                except Exception as e:
                    logger.info(e.message)
                try:
                    if dct.get('status') == "Success":
                        dct.update(valid_filename='<a href="{}{}"><img src="{}" style="float:left; display:block; height:25px; width:25px;">'.format(MEDIA_URL, dct.pop('valid_filename'), excel_green))
                    else:
                        dct.update(valid_filename='<img src="{0}" style="float:left; display:block; height:25px; width:25px;">'.format(excel_grey))
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('status') == "Success":
                        dct.update(invalid_filename='<a href="{}{}"><img src="{}" style="float:left; display:block; height:25px; width:25px;">'.format(MEDIA_URL, dct.pop('invalid_filename'), excel_red))
                    else:
                        dct.update(invalid_filename='<img src="{0}" style="float:left; display:block; height:25px; width:25px;">'.format(excel_grey))
                except Exception as e:
                    logger.info(e.message)

                # show user full name in uploded by field
                try:
                    if dct.get('uploaded_by'):
                        user = User.objects.get(username=dct.get('uploaded_by'))
                        dct.update(uploaded_by='{} {}'.format(user.first_name, user.last_name))
                except Exception as e:
                    logger.info(e.message)

            except Exception as e:
                logger.info(e)

            dct.update(actions='<a href="/bulk_import/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                                <a href="/bulk_import/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.get('id')))
            try:
                sheet_names_list = ['PTP', 'PMP BS', 'PMP SM', 'PTP BH', 'Wimax BS', 'Wimax SS']
                if dct.get('sheet_name'):
                    if dct.get('sheet_name') in sheet_names_list:
                        dct.update(bulk_upload_actions='<a href="/bulk_import/bulk_upload_valid_data/valid/{0}/{1}" class="bulk_import_link" title="Upload Valid Inventory"><i class="fa fa-upload text-success"></i></a>\
                                                        <a href="/bulk_import/bulk_upload_valid_data/invalid/{0}/{1}" class="bulk_import_link" title="Upload Invalid Inventory"><i class="fa fa-upload text-danger"></i></a>'.format(dct.get('id'), dct.get('sheet_name')))
                    else:
                        dct.update(bulk_upload_actions='')
            except Exception as e:
                logger.info()
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
        file_name = lambda x: MEDIA_ROOT + x
        # bulk import object
        bi_obj = self.get_object()

        # remove original file if it exists
        try:
            os.remove(file_name(bi_obj.original_filename))
        except Exception as e:
            logger.info(e.message)

        # remove valid rows file if it exists
        try:
            os.remove(file_name(bi_obj.valid_filename))
        except Exception as e:
            logger.info(e.message)

        # remove invalid rows file if it exists
        try:
            os.remove(file_name(bi_obj.invalid_filename))
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






