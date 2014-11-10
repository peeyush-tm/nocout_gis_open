import re
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
from django.shortcuts import render, render_to_response
import json
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, DetailView, TemplateView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from device_group.models import DeviceGroup
from nocout.settings import GISADMIN, NOCOUT_USER, MEDIA_ROOT, MEDIA_URL

from nocout.utils.util import DictDiffer, cache_for, cache_get_key

from models import Inventory, DeviceTechnology, IconSettings, LivePollingSettings, ThresholdConfiguration, \
    ThematicSettings, GISInventoryBulkImport, UserThematicSettings, CircuitL2Report, PingThematicSettings, \
    UserPingThematicSettings
from forms import InventoryForm, IconSettingsForm, LivePollingSettingsForm, ThresholdConfigurationForm, \
    ThematicSettingsForm, GISInventoryBulkImportForm, GISInventoryBulkImportEditForm, PingThematicSettingsForm
from organization.models import Organization
from site_instance.models import SiteInstance
from user_group.models import UserGroup
from user_profile.models import UserProfile
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit
from forms import AntennaForm, BaseStationForm, BackhaulForm, SectorForm, CustomerForm, SubStationForm, CircuitForm, CircuitL2ReportForm
from device.models import Country, State, City, Device
from django.contrib.staticfiles.templatetags.staticfiles import static
from user_profile.models import UserProfile
import xlrd
import xlwt
import logging
from django.template import RequestContext
from nocout.utils import logged_in_user_organizations
from tasks import validate_gis_inventory_excel_sheet, bulk_upload_ptp_inventory, bulk_upload_pmp_sm_inventory, \
    bulk_upload_pmp_bs_inventory, bulk_upload_ptp_bh_inventory, bulk_upload_wimax_bs_inventory, \
    bulk_upload_wimax_ss_inventory
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.datatable import DatatableOrganizationFilterMixin, DatatableSearchMixin

logger = logging.getLogger(__name__)

##caching
from django.core.cache import cache
##caching

# **************************************** Inventory *********************************************
def inventory(request):
    """
    Render the inventory page.
    """
    return render(request, 'inventory/inventory.html')


class InventoryListing(PermissionsRequiredMixin, ListView):
    """
    Class Based Inventory View to render list page.
    """
    model = Inventory
    template_name = 'inventory/inventory_list.html'
    required_permissions = ('inventory.view_inventory',)

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


class InventoryListingTable(PermissionsRequiredMixin, BaseDatatableView):
    """
    Class based View to render Inventory Data table.
    """

    model = Inventory
    required_permissions = ('inventory.view_inventory',)
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


class InventoryCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new Inventory.
    """

    template_name = 'inventory/inventory_new.html'
    model = Inventory
    form_class = InventoryForm
    success_url = reverse_lazy('InventoryList')
    required_permissions = ('inventory.add_inventory',)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        return HttpResponseRedirect(InventoryCreate.success_url)


class InventoryUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update new Inventory.
    """
    template_name = 'inventory/inventory_update.html'
    model = Inventory
    form_class = InventoryForm
    success_url = reverse_lazy('InventoryList')
    required_permissions = ('inventory.change_inventory',)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        return HttpResponseRedirect(InventoryCreate.success_url)


class InventoryDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Inventory

    """
    model = Inventory
    template_name = 'inventory/inventory_delete.html'
    success_url = reverse_lazy('InventoryList')
    required_permissions = ('inventory.delete_inventory',)


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

def list_device(request):
    """
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    devices = Device.objects.filter(organization_id=org_id).\
            filter(device_name__icontains=sSearch).values('id', 'device_name')[:50]

    return HttpResponse(json.dumps({
        "total_count": devices.count(),
        "incomplete_results": False,
        "items": list(devices)
    }))

def select_device(request, pk):
    """
    """
    return HttpResponse(json.dumps([Device.objects.get(id=pk).device_name]))


#**************************************** Antenna *********************************************
class AntennaList(PermissionsRequiredMixin, ListView):
    """
    Class based view to render Antenna list page.
    """
    model = Antenna
    template_name = 'antenna/antenna_list.html'
    required_permissions = ('inventory.view_antenna',)

    def get_queryset(self):
        """
        In this view no data is passed to datatable while rendering template.
        Another ajax call is made to fill in datatable.
        """
        queryset = super(AntennaList, self).get_queryset()
        queryset = queryset.none()
        return queryset

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

        #if the user role is Admin or operator or superuser then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role or self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class AntennaListingTable(PermissionsRequiredMixin,
        DatatableOrganizationFilterMixin,
        DatatableSearchMixin,
        BaseDatatableView,
    ):
    """
    Class based View to render Antenna Data table.
    """
    model = Antenna
    columns = ['alias', 'height', 'polarization', 'tilt', 'beam_width', 'azimuth_angle']
    order_columns = ['alias', 'height', 'polarization', 'tilt', 'beam_width', 'azimuth_angle']
    required_permissions = ('inventory.view_antenna',)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        for dct in json_data:
            device_id = dct.pop('id')
            if self.request.user.has_perm('inventory.change_antenna'):
                edit_action = '<a href="/antenna/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_antenna'):
                delete_action = '<a href="/antenna/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data


class AntennaDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the antenna detail.
    """
    model = Antenna
    template_name = 'antenna/antenna_detail.html'
    required_permissions = ('inventory.view_antenna',)


class AntennaCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new Antenna.
    """
    template_name = 'antenna/antenna_new.html'
    model = Antenna
    form_class = AntennaForm
    success_url = reverse_lazy('antennas_list')
    required_permissions = ('inventory.add_antenna',)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(AntennaCreate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        verb_string = "Create Antenna : %s" %(self.object.alias)
        return HttpResponseRedirect(AntennaCreate.success_url)


class AntennaUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Antenna .
    """
    template_name = 'antenna/antenna_update.html'
    model = Antenna
    form_class = AntennaForm
    success_url = reverse_lazy('antennas_list')
    required_permissions = ('inventory.change_antenna',)

    def get_queryset(self):
        return Antenna.objects.filter(organization__in=logged_in_user_organizations(self))

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(AntennaUpdate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

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
        return HttpResponseRedirect(AntennaUpdate.success_url)


class AntennaDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Antenna.
    """
    model = Antenna
    template_name = 'antenna/antenna_delete.html'
    success_url = reverse_lazy('antennas_list')
    required_permissions = ('inventory.delete_antenna',)


#****************************************** Base Station ********************************************
class BaseStationList(PermissionsRequiredMixin, ListView):
    """
    Class based View to render Base Station Data table.
    """
    model = BaseStation
    template_name = 'base_station/base_stations_list.html'
    required_permissions = ('inventory.view_basestation',)

    def get_queryset(self):
        """
        In this view no data is passed to datatable while rendering template.
        Another ajax call is made to fill in datatable.
        """
        queryset = super(BaseStationList, self).get_queryset()
        queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(BaseStationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            # {'mData': 'bs_technology__alias', 'sTitle': 'Technology', 'sWidth': 'auto', },
            {'mData': 'bs_site_id', 'sTitle': 'Site ID', 'sWidth': 'auto', },
            {'mData': 'bs_switch__id', 'sTitle': 'BS Switch', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
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


class BaseStationListingTable(PermissionsRequiredMixin,
        DatatableOrganizationFilterMixin,
        DatatableSearchMixin,
        BaseDatatableView,
    ):
    """
    Class based View to render Base Station Data table.
    """
    model = BaseStation
    required_permissions = ('inventory.view_basestation',)
    columns = ['alias', 'bs_site_id',
               'bs_switch__id', 'backhaul__name', 'bs_type', 'building_height', 'description']
    order_columns = ['alias', 'bs_site_id',
                     'bs_switch__id', 'backhaul__name', 'bs_type', 'building_height', 'description']


    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            # modify device name format in datatable i.e. <device alias> (<device ip>)
            try:
                if 'bs_switch__id' in dct:
                    bs_device_alias = Device.objects.get(id=dct['bs_switch__id']).device_alias
                    bs_device_ip = Device.objects.get(id=dct['bs_switch__id']).ip_address
                    dct['bs_switch__id'] = "{} ({})".format(bs_device_alias, bs_device_ip)
            except Exception as e:
                logger.info("BS Switch not present. Exception: ", e.message)

            device_id = dct.pop('id')
            if self.request.user.has_perm('inventory.change_basestation'):
                edit_action = '<a href="/base_station/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_basestation'):
                delete_action = '<a href="/base_station/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data


class BaseStationDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the Base Station detail.
    """
    model = BaseStation
    template_name = 'base_station/base_station_detail.html'
    required_permissions = ('inventory.view_basestation',)


class BaseStationCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new Base Station.
    """
    template_name = 'base_station/base_station_new.html'
    model = BaseStation
    form_class = BaseStationForm
    success_url = reverse_lazy('base_stations_list')
    required_permissions = ('inventory.add_basestation',)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(BaseStationCreate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        verb_string = "Create Base Station : %s" %(self.object.alias)
        return HttpResponseRedirect(BaseStationCreate.success_url)


class BaseStationUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Base Station.
    """
    template_name = 'base_station/base_station_update.html'
    model = BaseStation
    form_class = BaseStationForm
    success_url = reverse_lazy('base_stations_list')
    required_permissions = ('inventory.change_basestation',)

    def get_queryset(self):
        return BaseStation.objects.filter(organization__in=logged_in_user_organizations(self))

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(BaseStationUpdate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

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
        return HttpResponseRedirect(BaseStationUpdate.success_url)


class BaseStationDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Base Station.
    """
    model = BaseStation
    template_name = 'base_station/base_station_delete.html'
    success_url = reverse_lazy('base_stations_list')
    required_permissions = ('inventory.delete_basestation',)


def list_base_station(request):
    """
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    base_stations = BaseStation.objects.filter(organization__id=org_id).\
            filter(name__icontains=sSearch).values('id', 'name')[:50]

    return HttpResponse(json.dumps({
        "total_count": base_stations.count(),
        "incomplete_results": False,
        "items": list(base_stations)
    }))

def select_base_station(request, pk):
    """
    """
    return HttpResponse(json.dumps([BaseStation.objects.get(id=pk).name]))


#**************************************** Backhaul *********************************************
class BackhaulList(PermissionsRequiredMixin, ListView):
    """
    Class based View to render Backhaul Listing page..
    """
    model = Backhaul
    template_name = 'backhaul/backhauls_list.html'
    required_permissions = ('inventory.view_backhaul',)

    def get_queryset(self):
        """
        In this view no data is passed to datatable while rendering template.
        Another ajax call is made to fill in datatable.
        """
        queryset = super(BackhaulList, self).get_queryset()
        queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(BackhaulList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto'},
            {'mData': 'bh_configured_on__id', 'sTitle': 'Backhaul Configured On', 'sWidth': 'auto'},
            {'mData': 'bh_port', 'sTitle': 'Backhaul Port', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'bh_type', 'sTitle': 'Backhaul Type', 'sWidth': 'auto', },
            {'mData': 'pop__id', 'sTitle': 'POP', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
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


class BackhaulListingTable(PermissionsRequiredMixin,
        DatatableOrganizationFilterMixin,
        DatatableSearchMixin,
        BaseDatatableView,
    ):
    """
    Class based View to render Backhaul Data table.
    """
    model = Backhaul
    required_permissions = ('inventory.view_backhaul',)
    columns = ['alias', 'bh_configured_on__id', 'bh_port', 'bh_type', 'pop__id', 'pop_port',
               'bh_connectivity', 'bh_circuit_id', 'bh_capacity']
    order_columns = ['alias', 'bh_configured_on__id', 'bh_port', 'bh_type', 'pop__id',
                     'pop_port', 'bh_connectivity', 'bh_circuit_id', 'bh_capacity']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            # modify device name format in datatable i.e. <device alias> (<device ip>)
            try:
                if 'bh_configured_on__id' in dct:
                    bh_device_alias = Device.objects.get(id=dct['bh_configured_on__id']).device_alias
                    bh_device_ip = Device.objects.get(id=dct['bh_configured_on__id']).ip_address
                    dct['bh_configured_on__id'] = "{} ({})".format(bh_device_alias, bh_device_ip)
            except Exception as e:
                logger.info("Backhaul configured on not present. Exception: ", e.message)

            try:
                if 'pop__id' in dct:
                    pop_device_alias = Device.objects.get(id=dct['pop__id']).device_alias
                    pop_device_ip = Device.objects.get(id=dct['pop__id']).ip_address
                    dct['pop__id'] = "{} ({})".format(pop_device_alias, pop_device_ip)
            except Exception as e:
                logger.info("POP not present. Exception: ", e.message)

            device_id = dct.pop('id')
            if self.request.user.has_perm('inventory.change_backhaul'):
                edit_action = '<a href="/backhaul/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_backhaul'):
                delete_action = '<a href="/backhaul/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data


class BackhaulDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the Backhaul detail.
    """
    model = Backhaul
    required_permissions = ('inventory.view_backhaul',)
    template_name = 'backhaul/backhaul_detail.html'


class BackhaulCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new backhaul..
    """
    template_name = 'backhaul/backhaul_new.html'
    model = Backhaul
    form_class = BackhaulForm
    success_url = reverse_lazy('backhauls_list')
    required_permissions = ('inventory.add_backhaul',)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(BackhaulCreate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        verb_string = "Create Backhaul : %s" %(self.object.alias)
        return HttpResponseRedirect(BackhaulCreate.success_url)


class BackhaulUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Backhaul.
    """
    template_name = 'backhaul/backhaul_update.html'
    model = Backhaul
    form_class = BackhaulForm
    success_url = reverse_lazy('backhauls_list')
    required_permissions = ('inventory.change_backhaul',)

    def get_queryset(self):
        return Backhaul.objects.filter(organization__in=logged_in_user_organizations(self))

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(BackhaulUpdate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

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
        return HttpResponseRedirect(BackhaulUpdate.success_url)


class BackhaulDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Backhaul.
    """
    model = Backhaul
    template_name = 'backhaul/backhaul_delete.html'
    success_url = reverse_lazy('backhauls_list')
    required_permissions = ('inventory.delete_backhaul',)


def list_backhaul(request):
    """
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    backhauls = Backhaul.objects.filter(organization__id=org_id).\
            filter(name__icontains=sSearch).values('id', 'name')[:50]

    return HttpResponse(json.dumps({
        "total_count": backhauls.count(),
        "incomplete_results": False,
        "items": list(backhauls)
    }))

def select_backhaul(request, pk):
    """
    """
    return HttpResponse(json.dumps([Backhaul.objects.get(id=pk).name]))


#**************************************** Sector *********************************************
class SectorList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render Sector List Page.
    """
    model = Sector
    template_name = 'sector/sectors_list.html'
    required_permissions = ('inventory.view_sector',)

    def get_queryset(self):
        """
        In this view no data is passed to datatable while rendering template.
        Another ajax call is made to fill in datatable.
        """
        queryset = super(SectorList, self).get_queryset()
        queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(SectorList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'bs_technology__alias', 'sTitle': 'Technology', 'sWidth': 'auto', },
            {'mData': 'sector_id', 'sTitle': 'ID', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'sector_configured_on__id', 'sTitle': 'Sector Configured On', 'sWidth': 'auto', },
            {'mData': 'sector_configured_on_port__alias', 'sTitle': 'Sector Configured On Port', 'sWidth': 'auto',
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


class SectorListingTable(PermissionsRequiredMixin,
        DatatableOrganizationFilterMixin,
        DatatableSearchMixin,
        BaseDatatableView,
    ):
    """
    Class based View to render Sector Data Table.
    """
    model = Sector
    required_permissions = ('inventory.view_sector',)
    columns = ['alias', 'bs_technology__alias', 'sector_id', 'sector_configured_on__id',
               'base_station__alias', 'sector_configured_on_port__alias', 'antenna__alias', 'mrc', 'description']
    order_columns = ['alias', 'bs_technology__alias', 'sector_id', 'sector_configured_on__id',
                     'base_station__alias', 'sector_configured_on_port__alias', 'antenna__alias', 'mrc', 'description']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            # modify device name format in datatable i.e. <device alias> (<device ip>)
            try:
                if 'sector_configured_on__id' in dct:
                    sector_device_alias = Device.objects.get(id=dct['sector_configured_on__id']).device_alias
                    sector_device_ip = Device.objects.get(id=dct['sector_configured_on__id']).ip_address
                    dct['sector_configured_on__id'] = "{} ({})".format(sector_device_alias, sector_device_ip)
            except Exception as e:
                logger.info("Sector Configured On not present. Exception: ", e.message)

            device_id = dct.pop('id')
            if self.request.user.has_perm('inventory.change_sector'):
                edit_action = '<a href="/sector/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_sector'):
                delete_action = '<a href="/sector/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data


class SectorDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the Sector detail.
    """
    model = Sector
    required_permissions = ('inventory.view_sector',)
    template_name = 'sector/sector_detail.html'


class SectorCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new Sector.
    """
    template_name = 'sector/sector_new.html'
    model = Sector
    form_class = SectorForm
    success_url = reverse_lazy('sectors_list')
    required_permissions = ('inventory.add_sector',)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(SectorCreate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        verb_string = "Create Sector : %s" %(self.object.alias)
        return HttpResponseRedirect(SectorCreate.success_url)


class SectorUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Sector.
    """
    template_name = 'sector/sector_update.html'
    model = Sector
    form_class = SectorForm
    success_url = reverse_lazy('sectors_list')
    required_permissions = ('inventory.change_sector',)

    def get_queryset(self):
        return Sector.objects.filter(organization__in=logged_in_user_organizations(self))

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(SectorUpdate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

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
        return HttpResponseRedirect(SectorUpdate.success_url)


class SectorDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Sector.
    """
    model = Sector
    template_name = 'sector/sector_delete.html'
    success_url = reverse_lazy('sectors_list')
    required_permissions = ('inventory.delete_sector',)

def list_sector(request):
    """
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    sectors = Sector.objects.filter(organization__id=org_id).\
            filter(name__icontains=sSearch).values('id', 'name')[:50]

    return HttpResponse(json.dumps({
        "total_count": sectors.count(),
        "incomplete_results": False,
        "items": list(sectors)
    }))

def select_sector(request, pk):
    """
    """
    return HttpResponse(json.dumps([Sector.objects.get(id=pk).name]))


#**************************************** Customer *********************************************
class CustomerList(PermissionsRequiredMixin, ListView):
    """
    Class based View to render Customer listing page.
    """
    model = Customer
    template_name = 'customer/customers_list.html'
    required_permissions = ('inventory.view_customer',)

    def get_queryset(self):
        """
        In this view no data is passed to datatable while rendering template.
        Another ajax call is made to fill in datatable.
        """
        queryset = super(CustomerList, self).get_queryset()
        queryset = queryset.none()
        return queryset

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


class CustomerListingTable(PermissionsRequiredMixin,
        DatatableOrganizationFilterMixin,
        DatatableSearchMixin,
        BaseDatatableView,
    ):
    """
    Class based View to render Customer Data table.
    """
    model = Customer
    required_permissions = ('inventory.view_customer',)
    columns = ['alias', 'address', 'description']
    order_columns = ['alias']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            device_id = dct.pop('id')
            if self.request.user.has_perm('inventory.change_customer'):
                edit_action = '<a href="/customer/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_customer'):
                delete_action = '<a href="/customer/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data


class CustomerDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the customer detail.
    """
    model = Customer
    required_permissions = ('inventory.view_customer',)
    template_name = 'customer/customer_detail.html'


class CustomerCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new customer.
    """
    template_name = 'customer/customer_new.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customers_list')
    required_permissions = ('inventory.add_customer',)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(CustomerCreate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        verb_string = "Create Customer : %s" %(self.object.alias)
        return HttpResponseRedirect(CustomerCreate.success_url)


class CustomerUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Customer.
    """
    template_name = 'customer/customer_update.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customers_list')
    required_permissions = ('inventory.change_customer',)

    def get_queryset(self):
        return Customer.objects.filter(organization__in=logged_in_user_organizations(self))

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(CustomerUpdate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

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
        return HttpResponseRedirect(CustomerUpdate.success_url)


class CustomerDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Customer.
    """
    model = Customer
    template_name = 'customer/customer_delete.html'
    success_url = reverse_lazy('customers_list')
    required_permissions = ('inventory.delete_customer',)


#**************************************** Sub Station *********************************************
class SubStationList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render Sub Station List Page.
    """
    model = SubStation
    template_name = 'sub_station/sub_stations_list.html'
    required_permissions = ('inventory.view_substation',)

    def get_queryset(self):
        """
        In this view no data is passed to datatable while rendering template.
        Another ajax call is made to fill in datatable.
        """
        queryset = super(SubStationList, self).get_queryset()
        queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(SubStationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'device__id', 'sTitle': 'Device', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
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


class SubStationListingTable(PermissionsRequiredMixin,
        DatatableOrganizationFilterMixin,
        DatatableSearchMixin,
        BaseDatatableView,
    ):
    """
    Class based View to render Sub Station Data table.
    """
    model = SubStation
    required_permissions = ('inventory.view_substation',)
    columns = ['alias', 'device__id', 'antenna__alias', 'version', 'serial_no', 'building_height',
               'tower_height', 'city', 'state', 'address', 'description']
    order_columns = ['alias', 'device__id', 'antenna__alias', 'version', 'serial_no', 'building_height',
                     'tower_height']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            # modify device name format in datatable i.e. <device alias> (<device ip>)
            try:
                if 'device__id' in dct:
                    ss_device_alias = Device.objects.get(id=dct['device__id']).device_alias
                    ss_device_ip = Device.objects.get(id=dct['device__id']).ip_address
                    dct['device__id'] = "{} ({})".format(ss_device_alias, ss_device_ip)
            except Exception as e:
                logger.info("Sub Station Device not present. Exception: ", e.message)

            dct['city__name'] = City.objects.get(pk=int(dct['city'])).city_name if dct['city'] else ''
            dct['state__name'] = State.objects.get(pk=int(dct['state'])).state_name if dct['state'] else ''
            device_id = dct.pop('id')
            if self.request.user.has_perm('inventory.change_substation'):
                edit_action = '<a href="/sub_station/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_substation'):
                delete_action = '<a href="/sub_station/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data


class SubStationDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the Sub Station detail.
    """
    model = SubStation
    required_permissions = ('inventory.view_substation',)
    template_name = 'sub_station/sub_station_detail.html'


class SubStationCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new Sub Station.
    """
    template_name = 'sub_station/sub_station_new.html'
    model = SubStation
    form_class = SubStationForm
    success_url = reverse_lazy('sub_stations_list')
    required_permissions = ('inventory.add_substation',)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(SubStationCreate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        verb_string = "Create Sub Station : %s" %(self.object.alias)
        return HttpResponseRedirect(SubStationCreate.success_url)


class SubStationUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update the Sub Station.
    """
    template_name = 'sub_station/sub_station_update.html'
    model = SubStation
    form_class = SubStationForm
    success_url = reverse_lazy('sub_stations_list')
    required_permissions = ('inventory.change_substation',)

    def get_queryset(self):
        return SubStation.objects.filter(organization__in=logged_in_user_organizations(self))

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(SubStationUpdate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

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
        return HttpResponseRedirect(SubStationUpdate.success_url)


class SubStationDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Sub Station.
    """
    model = SubStation
    template_name = 'sub_station/sub_station_delete.html'
    success_url = reverse_lazy('sub_stations_list')
    required_permissions = ('inventory.delete_substation',)


#**************************************** Circuit *********************************************
class CircuitList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render Circuit List Page.
    """
    model = Circuit
    template_name = 'circuit/circuits_list.html'
    required_permissions = ('inventory.view_circuit',)

    def get_queryset(self):
        """
        In this view no data is passed to datatable while rendering template.
        Another ajax call is made to fill in datatable.
        """
        queryset = super(CircuitList, self).get_queryset()
        queryset = queryset.none()
        return queryset

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


class CircuitListingTable(PermissionsRequiredMixin,
        DatatableOrganizationFilterMixin,
        DatatableSearchMixin,
        BaseDatatableView,
    ):
    """
    Class based View to render Circuit Data table.
    """
    model = Circuit
    required_permissions = ('inventory.view_circuit',)
    columns = ['alias', 'circuit_id','sector__base_station__alias', 'sector__alias', 'customer__alias',
               'sub_station__alias', 'date_of_acceptance', 'description']
    order_columns = ['alias', 'circuit_id','sector__base_station__alias', 'sector__alias', 'customer__alias',
                     'sub_station__alias', 'date_of_acceptance', 'description']
    search_columns = ['alias', 'circuit_id','sector__base_station__alias', 'sector__alias', 'customer__alias',
               'sub_station__alias']

    def prepare_results(self, qs):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            device_id = dct.pop('id')
            if self.request.user.has_perm('inventory.change_circuit'):
                edit_action = '<a href="/circuit/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>&nbsp&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_circuit'):
                delete_action = '<a href="/circuit/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>&nbsp&nbsp'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                actions = edit_action + delete_action
            else:
                actions = ''
            actions = actions + '<a href="/circuit/l2_reports/{0}/"><i class="fa fa-sign-in text-info" title="View L2 reports for circuit"\
                            alt="View L2 reports for circuit"></i></a>'.format(device_id)
            dct.update(actions=actions, date_of_acceptance=dct['date_of_acceptance'].strftime("%Y-%m-%d") if dct['date_of_acceptance'] != "" else "")

        return json_data


class CircuitDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the Circuit detail.
    """
    model = Circuit
    required_permissions = ('inventory.view_circuit',)
    template_name = 'circuit/circuit_detail.html'


class CircuitCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new Circuit.
    """

    template_name = 'circuit/circuit_new.html'
    model = Circuit
    form_class = CircuitForm
    success_url = reverse_lazy('circuits_list')
    required_permissions = ('inventory.add_circuit',)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(CircuitCreate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        verb_string = "Create Circuit : %s" %(self.object.alias)
        return HttpResponseRedirect(CircuitCreate.success_url)


class CircuitUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Cicuit.
    """
    template_name = 'circuit/circuit_update.html'
    model = Circuit
    form_class = CircuitForm
    success_url = reverse_lazy('circuits_list')
    required_permissions = ('inventory.change_circuit',)

    def get_queryset(self):
        return Circuit.objects.filter(organization__in=logged_in_user_organizations(self))

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(CircuitUpdate, self).get_form_kwargs()
        kwargs.update({'request':self.request })
        return kwargs

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Update Circuit : %s, ' % (self.object.alias) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
        return HttpResponseRedirect(CircuitUpdate.success_url)


class CircuitDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Circuit.
    """
    model = Circuit
    template_name = 'circuit/circuit_delete.html'
    success_url = reverse_lazy('circuits_list')
    required_permissions = ('inventory.delete_circuit',)


#********************************* Circuit L2 Reports*******************************************

class CircuitL2Report_Init(ListView):
    """
    Class Based View to render Circuit based L2 reports List Page.
    """
    model = CircuitL2Report
    template_name = 'circuit_l2/circuit_l2_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(CircuitL2Report_Init, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'file_name', 'sTitle': 'Report', 'sWidth': 'auto', },
            {'mData': 'added_on', 'sTitle': 'Uploaded On', 'sWidth': 'auto'},
            {'mData': 'user_id', 'sTitle': 'Uploaded By', 'sWidth': 'auto'},
        ]
        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['circuit_id'] = self.kwargs['circuit_id']
        return context

class L2ReportListingTable(BaseDatatableView):
    """
    Class based View to render Circuit Data table.
    """
    model = CircuitL2Report
    columns = ['name', 'file_name', 'added_on', 'user_id']
    order_columns = ['name', 'file_name', 'added_on']

    def filter_queryset(self, qs):
        """ Filter datatable as per requested value """

        sSearch = self.request.GET.get('sSearch', None)

        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                # avoid search on 'added_on'
                if column == 'added_on':
                    continue
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query
        return qs

    def get_initial_queryset(self,circuit_id):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        circuit_instance = Circuit.objects.filter(id=circuit_id)
        # condition to fetch l2 reports data from db
        condition = (Q(user_id=self.request.user) | Q(is_public=1)) & (Q(circuit_id=circuit_instance))
        # Query to fetch L2 reports data from db
        l2ReportsResult = CircuitL2Report.objects.filter(condition).values(*self.columns + ['id'])

        report_resultset = []
        for data in l2ReportsResult:
            report_object = {}
            report_object['name'] = data['name'].title()
            filename_str_array = data['file_name'].split('/')
            report_object['file_name'] = filename_str_array[len(filename_str_array)-1]
            report_object['file_url'] = data['file_name']
            report_object['added_on'] = data['added_on']
            username = UserProfile.objects.filter(id=data['user_id']).values('username')
            report_object['user_id'] = username[0]['username'].title()
            report_object['id'] = data['id']
            #add data to report_resultset list
            report_resultset.append(report_object)
        return report_resultset

    def prepare_results(self, qs):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="../../../media/'+dct['file_url']+'" target="_blank" title="Download Report">\
                <i class="fa fa-arrow-circle-o-down text-info"></i></a>\
                <a class="delete_l2report" style="cursor:pointer;" title="Delete Report" url="delete/{0}/">\
                <i class="fa fa-trash-o text-danger"></i></a>\
                '.format(dct.pop('id')),
               added_on=dct['added_on'].strftime("%Y-%m-%d") if dct['added_on'] != "" else "")

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

        ckt_id = self.kwargs['circuit_id']

        qs = self.get_initial_queryset(ckt_id)

        # number of records before filtering
        total_records = len(qs)

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

class CircuitL2ReportCreate(CreateView):
    """
    Class based view to create new Circuit.
    """

    template_name = 'circuit_l2/circuit_l2_new.html'
    model = CircuitL2Report
    form_class = CircuitL2ReportForm

    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(CircuitL2ReportCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save(commit=False)
        self.object.user_id =  UserProfile.objects.get(id=self.request.user.id)
        self.object.circuit_id =  Circuit.objects.get(id=self.kwargs['circuit_id'])

        self.object.save()
        return HttpResponseRedirect(reverse_lazy('circuit_l2_report', kwargs = {'circuit_id' : self.kwargs['circuit_id']}))

class CircuitL2ReportDelete(DeleteView):

    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(CircuitL2ReportDelete, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        report_id = self.kwargs['l2_id']
        file_name = lambda x: MEDIA_ROOT + x
        # l2 report object
        l2_obj = CircuitL2Report.objects.filter(id=report_id).values()

        # remove original file if it exists
        try:
            os.remove(file_name(l2_obj[0]['file_name']))
        except Exception as e:
            logger.info(e.message)

        # delete entry from database
        CircuitL2Report.objects.filter(id=report_id).delete()
        return HttpResponseRedirect(reverse_lazy('circuit_l2_report', kwargs = {'circuit_id' : self.kwargs['circuit_id']}))

#**************************************** IconSettings *********************************************
class IconSettingsList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render IconSettings List Page.
    """
    model = IconSettings
    template_name = 'icon_settings/icon_settings_list.html'
    required_permissions = ('inventory.view_iconsettings',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(IconSettingsList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'alias',            'sTitle': 'Alias',              'sWidth': 'auto'},
            {'mData': 'upload_image',     'sTitle': 'Image',       'sWidth': 'auto'},
            ]
        #if the user is superuser action column can be appeared in datatable.
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class IconSettingsListingTable(PermissionsRequiredMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class based View to render IconSettings Data table.
    """
    model = IconSettings
    required_permissions = ('inventory.view_iconsettings',)
    columns = ['alias', 'upload_image']
    order_columns = ['alias', 'upload_image']

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
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            try:
                img_url = "/media/"+ (dct['upload_image']) if \
                    "uploaded" in dct['upload_image'] \
                    else static("img/" + dct['upload_image'])
                dct.update(upload_image='<img src="{0}" style="float:left; display:block; height:25px; width:25px;">'.format(img_url))
            except Exception as e:
                logger.info(e)

            dct.update(actions='<a href="/icon_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/icon_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


class IconSettingsDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the IconSettings detail.
    """
    model = IconSettings
    required_permissions = ('inventory.view_iconsettings',)
    template_name = 'icon_settings/icon_settings_detail.html'


class IconSettingsCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new IconSettings.
    """
    template_name = 'icon_settings/icon_settings_new.html'
    model = IconSettings
    form_class = IconSettingsForm
    success_url = reverse_lazy('icon_settings_list')
    required_permissions = ('inventory.add_iconsettings',)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        verb_string = "Create Icon Setting : %s" %(self.object.alias)
        return HttpResponseRedirect(IconSettingsCreate.success_url)


class IconSettingsUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update IconSettings.
    """
    template_name = 'icon_settings/icon_settings_update.html'
    model = IconSettings
    form_class = IconSettingsForm
    success_url = reverse_lazy('icon_settings_list')
    required_permissions = ('inventory.change_iconsettings',)

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
        return HttpResponseRedirect(IconSettingsUpdate.success_url)


class IconSettingsDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the machine
    """
    model = IconSettings
    template_name = 'icon_settings/icon_settings_delete.html'
    success_url = reverse_lazy('icon_settings_list')
    required_permissions = ('inventory.delete_iconsettings',)


#**************************************** LivePollingSettings *********************************************
class LivePollingSettingsList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render LivePollingSettings List Page.
    """
    model = LivePollingSettings
    template_name = 'live_polling_settings/live_polling_settings_list.html'
    required_permissions = ('inventory.view_livepollingsettings',)

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


class LivePollingSettingsListingTable(PermissionsRequiredMixin,
        DatatableSearchMixin,
        BaseDatatableView
    ):
    """
    Class based View to render LivePollingSettings Data table.
    """
    model = LivePollingSettings
    required_permissions = ('inventory.view_livepollingsettings',)
    columns = ['alias', 'technology__alias', 'service__alias', 'data_source__alias']
    order_columns = ['alias', 'technology__alias', 'service__alias', 'data_source__alias']
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
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            dct.update(actions='<a href="/live_polling_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/live_polling_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


class LivePollingSettingsDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the LivePollingSettings detail.
    """
    model = LivePollingSettings
    required_permissions = ('inventory.view_livepollingsettings',)
    template_name = 'live_polling_settings/live_polling_settings_detail.html'


class LivePollingSettingsCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new LivePollingSettings.
    """
    template_name = 'live_polling_settings/live_polling_settings_new.html'
    model = LivePollingSettings
    form_class = LivePollingSettingsForm
    success_url = reverse_lazy('live_polling_settings_list')
    required_permissions = ('inventory.add_livepollingsettings',)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        verb_string = "Create Live Polling Setting : %s" %(self.object.alias)
        return HttpResponseRedirect(LivePollingSettingsCreate.success_url)


class LivePollingSettingsUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update LivePollingSettings.
    """
    template_name = 'live_polling_settings/live_polling_settings_update.html'
    model = LivePollingSettings
    form_class = LivePollingSettingsForm
    success_url = reverse_lazy('live_polling_settings_list')
    required_permissions = ('inventory.change_livepollingsettings',)

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
        return HttpResponseRedirect(LivePollingSettingsUpdate.success_url)


class LivePollingSettingsDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the LivePollingSettings
    """
    model = LivePollingSettings
    template_name = 'live_polling_settings/live_polling_settings_delete.html'
    success_url = reverse_lazy('live_polling_settings_list')
    required_permissions = ('inventory.delete_livepollingsettings',)


#**************************************** ThresholdConfiguration *********************************************
class ThresholdConfigurationList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render ThresholdConfiguration List Page.
    """
    model = ThresholdConfiguration
    template_name = 'threshold_configuration/threshold_configuration_list.html'
    required_permissions = ('inventory.view_thresholdconfiguration',)


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


class ThresholdConfigurationListingTable(PermissionsRequiredMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class based View to render ThresholdConfiguration Data table.
    """
    model = ThresholdConfiguration
    required_permissions = ('inventory.view_thresholdconfiguration',)
    columns = ['alias', 'live_polling_template__alias']
    order_columns = ['alias', 'live_polling_template__alias']
    search_columns = ['alias', 'live_polling_template__alias']

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
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            dct.update(actions='<a href="/threshold_configuration/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/threshold_configuration/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data

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



class ThresholdConfigurationDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the Threshold Configuration detail.
    """
    model = ThresholdConfiguration
    required_permissions = ('inventory.view_thresholdconfiguration',)
    template_name = 'threshold_configuration/threshold_configuration_detail.html'


class ThresholdConfigurationCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new Threshold Configuration.
    """
    template_name = 'threshold_configuration/threshold_configuration_new.html'
    model = ThresholdConfiguration
    form_class = ThresholdConfigurationForm
    success_url = reverse_lazy('threshold_configuration_list')
    required_permissions = ('inventory.add_threshold_configuration',)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object = form.save()
        verb_string = "Create Threshold Configuration : %s" %(self.object.alias)
        return HttpResponseRedirect(ThresholdConfigurationCreate.success_url)


class ThresholdConfigurationUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Threshold Configuration.
    """
    template_name = 'threshold_configuration/threshold_configuration_update.html'
    model = ThresholdConfiguration
    form_class = ThresholdConfigurationForm
    success_url = reverse_lazy('threshold_configuration_list')
    required_permissions = ('inventory.change_threshold_configuration',)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Update Threshold Configuration : %s, ' % (self.object.alias) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
        return HttpResponseRedirect(ThresholdConfigurationUpdate.success_url)


class ThresholdConfigurationDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Threshold Configuration.
    """
    model = ThresholdConfiguration
    template_name = 'threshold_configuration/threshold_configuration_delete.html'
    success_url = reverse_lazy('threshold_configuration_list')
    required_permissions = ('inventory.delete_threshold_configuration',)


#**************************************** ThematicSettings *********************************************
class ThematicSettingsList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render ThematicSettings List Page.
    """
    model = ThematicSettings
    template_name = 'thematic_settings/thematic_settings_list.html'
    required_permissions = ('inventory.view_thematicsettings',)

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


class ThematicSettingsListingTable(PermissionsRequiredMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class based View to render Thematic Settings Data table.
    """
    model = ThematicSettings
    required_permissions = ('inventory.view_thematicsettings',)
    columns = ['alias', 'threshold_template', 'icon_settings']
    order_columns = ['alias', 'threshold_template']
    search_columns = ['alias', 'icon_settings']

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
            threshold_config = ThresholdConfiguration.objects.get(id=int(dct['threshold_template']))
            image_string, range_text, full_string='','',''
            if dct['icon_settings'] and dct['icon_settings'] !='NULL':
                ###@nishant-teatrix. PLEASE SHOW THE RANGE MIN < ICON < RANGE MAX
                for d in eval(dct['icon_settings']):
                    img_url = str("/media/"+ (d.values()[0]) if "uploaded" in d.values()[0] else static("img/" + d.values()[0]))
                    image_string= '<img src="{0}" style="height:25px; width:25px">'.format(img_url.strip())
                    range_id_groups = re.match(r'[a-zA-Z_]+(\d+)', d.keys()[0])
                    if range_id_groups:
                        range_id = range_id_groups.groups()[-1]
                        range_text= ' Range '+ range_id +', '
                        range_start = 'range' + range_id +'_start'
                        range_end = 'range' + range_id +'_end'
                        range_start_value = getattr(threshold_config, range_start)
                        range_end_value = getattr(threshold_config, range_end)
                    else:
                        range_text = ''
                        range_start_value = ''
                        range_end_value = ''

                    full_string += image_string + range_text + "(" + range_start_value + ", " + range_end_value + ")" + "</br>"
            else:
                full_string='N/A'
            user_current_thematic_setting= self.request.user.id in ThematicSettings.objects.get(id=dct['id']).user_profile.values_list('id', flat=True)
            checkbox_checked_true='checked' if user_current_thematic_setting else ''
            dct.update(
                threshold_template=threshold_config.name,
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



class ThematicSettingsDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the Thematic Settings detail.
    """
    model = ThematicSettings
    required_permissions = ('inventory.view_thematicsettings',)
    template_name = 'thematic_settings/thematic_settings_detail.html'


class ThematicSettingsCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new ThematicSettings.
    """
    template_name = 'thematic_settings/thematic_settings_new.html'
    model = ThematicSettings
    form_class = ThematicSettingsForm
    success_url = reverse_lazy('thematic_settings_list')
    required_permissions = ('inventory.add_thematicsettings',)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        icon_settings_keys= list(set(form.data.keys())-set(form.cleaned_data.keys()+['csrfmiddlewaretoken']))
        icon_settings_values_list=[ { key: form.data[key] }  for key in icon_settings_keys if form.data[key]]
        self.object = form.save()
        self.object.icon_settings=icon_settings_values_list
        self.object.save()
        verb_string = "Create Thematic Settings : %s" %(self.object.alias)
        return HttpResponseRedirect(ThematicSettingsCreate.success_url)


class ThematicSettingsUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Thematic Settings.
    """
    template_name = 'thematic_settings/thematic_settings_update.html'
    model = ThematicSettings
    form_class = ThematicSettingsForm
    success_url = reverse_lazy('thematic_settings_list')
    required_permissions = ('inventory.change_thematicsettings',)

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
            verb_string = 'Update Thematic Settings : %s, ' % (self.object.alias) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
        return HttpResponseRedirect(ThematicSettingsUpdate.success_url)


class ThematicSettingsDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Thematic Settings.
    """
    model = ThematicSettings
    template_name = 'thematic_settings/thematic_settings_delete.html'
    success_url = reverse_lazy('thematic_settings_list')
    required_permissions = ('inventory.delete_thematicsettings',)


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
        ##we are using caching for GIS inventory
        ## we need to reset caching, as soon as
        ##user bulk uploads
        try:
            # cached_functions = ['prepare_raw_gis_info',
            #                     'organization_backhaul_devices',
            #                     'organization_network_devices',
            #                     'organization_customer_devices',
            #                     'ptp_device_circuit_backhaul',
            #                     'perf_gis_raw_inventory'
            #                     ]
            # keys = []
            # for cf in cached_functions:
            #     keys.append(cache_get_key(cf))
            # cache.delete_many(keys)
            cache.clear() #delete GIS cache on bulk upload
        except Exception as caching_exp:
            logger.exception(caching_exp.message)
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


class GISInventoryBulkImportListingTable(DatatableSearchMixin, BaseDatatableView):
    """
    A generic class based view for the gis inventory bulk import data table rendering.

    """
    model = GISInventoryBulkImport
    columns = ['original_filename', 'valid_filename', 'invalid_filename', 'status', 'sheet_name', 'technology', 'upload_status', 'description', 'uploaded_by', 'added_on', 'modified_on']
    order_columns = ['original_filename', 'valid_filename', 'invalid_filename', 'status', 'sheet_name', 'technology', 'upload_status', 'description', 'uploaded_by', 'added_on', 'modified_on']

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


#**************************************** Ping Thematic Settings *********************************************
class PingThematicSettingsList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render PingThematicSettings List Page.
    """
    model = PingThematicSettings
    template_name = 'ping_thematic_settings/ping_thematic_settings_list.html'

    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.
        """
        return super(PingThematicSettingsList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(PingThematicSettingsList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'alias',                   'sTitle': 'Alias',                     'sWidth': 'auto'},
            {'mData': 'service',                 'sTitle': 'Service',                   'sWidth': 'auto'},
            {'mData': 'data_source',             'sTitle': 'Data Source',               'sWidth': 'auto'},
            {'mData': 'icon_settings',           'sTitle': 'Icons Range',               'sWidth': 'auto'},
            {'mData': 'user_selection',          'sTitle': 'Setting Selection',         'sWidth': 'auto'}]

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


class PingThematicSettingsListingTable(PermissionsRequiredMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class based View to render Thematic Settings Data table.
    """
    model = PingThematicSettings
    columns = ['alias', 'service', 'data_source', 'icon_settings']
    order_columns = ['alias', 'service', 'data_source']


    def get_initial_queryset(self, technology="P2P"):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        is_global = 1
        if self.request.GET.get('admin'):
            is_global = 0

        return PingThematicSettings.objects.filter(technology=DeviceTechnology.objects.filter(name=technology)).filter(is_global=is_global).values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            # modify 'icon_setting' field for display in datatables i.e. format: "start_range > icon > end_range"
            icon_settings_display_field = ""

            # after converting 'icon_settings' string in list of icon_setting dictionaries using eval, loop on it
            for d in eval(dct['icon_settings']):
                r = d.keys()[0]

                # fetching number from dictionary key for e.g. 4 from 'icon_settings4'
                s = ''.join(x for x in r if x.isdigit())

                # range fields corresponding to current icon setting
                range_start_field = "range{}_start".format(s)
                range_end_field = "range{}_end".format(s)

                # initialize start and end range
                start_range, end_range = [''] * 2

                # start range
                try:
                    start_range = PingThematicSettings.objects.filter(id=dct['id']).values(range_start_field)[0].values()[0]
                    if not start_range:
                        start_range = "N/A"
                except Exception as e:
                    logger.info("Start Range Exception: ", e.message)

                # end range
                try:
                    end_range = PingThematicSettings.objects.filter(id=dct['id']).values(range_end_field)[0].values()[0]
                    if not end_range:
                        end_range = "N/A"
                except Exception as e:
                    logger.info("End Range Exception: ", e.message)

                # image url
                img_url = str("/media/" + (d.values()[0])
                              if "uploaded" in d.values()[0]
                              else static("img/" + d.values()[0]))

                # image html content
                image_string = '<img src="{0}" style="height:25px; width:25px">'.format(img_url.strip())

                # icon settings content to be displayed in datatable
                icon_settings_display_field += " {} > {} > {} <br />".format(start_range, image_string, end_range)

            user_current_thematic_setting = self.request.user.id in PingThematicSettings.objects.get(
                id=dct['id']).user_profile.values_list('id', flat=True)
            checkbox_checked_true = 'checked' if user_current_thematic_setting else ''
            dct.update(
                icon_settings=icon_settings_display_field,
                user_selection='<input type="checkbox" class="check_class" ' + checkbox_checked_true +
                               ' name="setting_selection" value={0}><br>'.format(dct['id']),
                actions='<a href="/ping_thematic_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/ping_thematic_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                    dct.pop('id')))
        return json_data


class PingThematicSettingsDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the Thematic Settings detail.
    """
    model = PingThematicSettings
    template_name = 'ping_thematic_settings/ping_thematic_settings_detail.html'


class PingThematicSettingsCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new PingThematicSettings.
    """
    template_name = 'ping_thematic_settings/ping_thematic_settings_new.html'
    model = PingThematicSettings
    form_class = PingThematicSettingsForm
    success_url = reverse_lazy('ping_thematic_settings_list')
    required_permissions = ('inventory.add_pingthematicsettings',)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        icon_settings_keys = list(set(form.data.keys()) - set(
            [key for key in form.cleaned_data.keys() if "icon" not in key] + ['csrfmiddlewaretoken']))

        # sorting icon settings list
        icon_settings_keys = sorted(icon_settings_keys, key=lambda r: int(''.join(x for x in r if x.isdigit())))

        icon_settings_values_list = [{key: form.data[key]} for key in icon_settings_keys if form.data[key]]
        self.object = form.save()
        self.object.icon_settings = icon_settings_values_list
        self.object.save()
        verb_string = "Create Thematic Settings : %s" % self.object.alias
        return HttpResponseRedirect(PingThematicSettingsCreate.success_url)


class PingThematicSettingsUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Thematic Settings.
    """
    template_name = 'ping_thematic_settings/ping_thematic_settings_update.html'
    model = PingThematicSettings
    form_class = PingThematicSettingsForm
    success_url = reverse_lazy('ping_thematic_settings_list')
    required_permissions = ('inventory.change_pingthematicsettings',)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        icon_settings_keys = list(set(form.data.keys()) - set(
            [key for key in form.cleaned_data.keys() if "icon" not in key] + ['csrfmiddlewaretoken']))

        # sorting icon settings list
        icon_settings_keys = sorted(icon_settings_keys, key=lambda r: int(''.join(x for x in r if x.isdigit())))

        icon_settings_values_list = [{key: form.data[key]} for key in icon_settings_keys if form.data[key]]
        self.object = form.save()
        self.object.icon_settings = icon_settings_values_list
        self.object.save()
        # self.object = form.save()
        if changed_fields_dict:
            verb_string = 'Update Thematic Settings : %s, ' % (self.object.alias) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
        return HttpResponseRedirect(PingThematicSettingsUpdate.success_url)


class PingThematicSettingsDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Thematic Settings.
    """
    model = PingThematicSettings
    template_name = 'ping_thematic_settings/ping_thematic_settings_delete.html'
    success_url = reverse_lazy('ping_thematic_settings_list')
    required_permissions = ('inventory.delete_pingthematicsettings',)


class Ping_Update_User_Thematic_Setting(View):
    """
    The Class Based View to Response the Ajax call on click to bind the user with the thematic setting.
    """

    def get(self, request):
        result = {
            "success": 0,
            "message": "Thematic Setting Not Bind to User",
            "data": {
                "meta": None,
                "objects": {}
            }
        }

        thematic_setting_id = self.request.GET.get('ts_template_id', None)
        user_profile_id = self.request.user.id
        if thematic_setting_id:
            ts_obj = PingThematicSettings.objects.get(id=int(thematic_setting_id))
            user_obj = UserProfile.objects.get(id=user_profile_id)
            tech_obj = ts_obj.technology
            to_delete = UserPingThematicSettings.objects.filter(user_profile=user_obj, thematic_technology=tech_obj)

            if len(to_delete):
                to_delete.delete()

            uts = UserPingThematicSettings(user_profile=user_obj,
                                           thematic_template=ts_obj,
                                           thematic_technology=tech_obj)
            uts.save()

            result['success'] = 1
            result['message'] = 'Thematic Setting Bind to User Successfully'
            result['data']['objects']['username'] = self.request.user.userprofile.username
            result['data']['objects']['thematic_setting_name'] = PingThematicSettings.objects.get(
                id=int(thematic_setting_id)).name

        return HttpResponse(json.dumps(result))






