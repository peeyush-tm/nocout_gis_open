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
from django.core.urlresolvers import reverse_lazy, reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from device_group.models import DeviceGroup
from nocout.settings import GISADMIN, NOCOUT_USER, MEDIA_ROOT, MEDIA_URL

from nocout.utils.util import DictDiffer, cache_for, cache_get_key

from models import Inventory, DeviceTechnology, IconSettings, LivePollingSettings, ThresholdConfiguration, \
    ThematicSettings, GISInventoryBulkImport, UserThematicSettings, CircuitL2Report, PingThematicSettings, \
    UserPingThematicSettings
from forms import InventoryForm, IconSettingsForm, LivePollingSettingsForm, ThresholdConfigurationForm, \
    ThematicSettingsForm, GISInventoryBulkImportForm, GISInventoryBulkImportEditForm, PingThematicSettingsForm, \
    ServiceThematicSettingsForm, ServiceThresholdConfigurationForm, ServiceLivePollingSettingsForm, \
    WizardBaseStationForm, WizardBackhaulForm, WizardSectorForm, WizardAntennaForm, WizardSubStationForm, \
    WizardCustomerForm, WizardCircuitForm, WizardPTPSubStationAntennaFormSet
from organization.models import Organization
from performance.models import ServiceStatus, InventoryStatus, NetworkStatus, Status
from site_instance.models import SiteInstance
from user_group.models import UserGroup
from user_profile.models import UserProfile
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit
from forms import AntennaForm, BaseStationForm, BackhaulForm, SectorForm, CustomerForm, SubStationForm, CircuitForm, CircuitL2ReportForm
from device.models import Country, State, City, Device, DeviceType
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
from nocout.mixins.generics import FormRequestMixin
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.datatable import DatatableOrganizationFilterMixin, DatatableSearchMixin, ValuesQuerySetMixin

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
            dct.update(actions='<a href="/inventory/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                       <a href="/inventory/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
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


class InventoryUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update new Inventory.
    """
    template_name = 'inventory/inventory_update.html'
    model = Inventory
    form_class = InventoryForm
    success_url = reverse_lazy('InventoryList')
    required_permissions = ('inventory.change_inventory',)


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
    Used to return the list to the select2 element using ajax call.
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    if str(org_id) == "0":
        class SelfObject: pass
        self_object = SelfObject()
        self_object.request = request
        organizations = logged_in_user_organizations(self_object)
        devices = Device.objects.filter(organization__id__in=organizations).\
            filter(device_alias__icontains=sSearch).values('id', 'device_alias')[:50]
    else:
        devices = Device.objects.filter(organization_id=org_id).\
            filter(device_alias__icontains=sSearch).values('id', 'device_alias')[:50]

    return HttpResponse(json.dumps({
        "total_count": devices.count(),
        "incomplete_results": False,
        "items": list(devices)
    }))

def select_device(request, pk):
    """
    Called when Select2 is created to allow the user to initialize the selection based on the value of the element select2 is attached to.
    """
    return HttpResponse(json.dumps([Device.objects.get(id=pk).device_alias]))


#**************************************** Antenna *********************************************
class AntennaList(PermissionsRequiredMixin, TemplateView):
    """
    Class Based View for the Antenna data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """

    template_name = 'antenna/antenna_list.html'
    required_permissions = ('inventory.view_antenna',)

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
                edit_action = '<a href="/antenna/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_antenna'):
                delete_action = '<a href="/antenna/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
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


class AntennaCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Class based view to create new Antenna.
    """
    template_name = 'antenna/antenna_new.html'
    model = Antenna
    form_class = AntennaForm
    success_url = reverse_lazy('antennas_list')
    required_permissions = ('inventory.add_antenna',)


class AntennaUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
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


class AntennaDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Antenna.
    """
    model = Antenna
    template_name = 'antenna/antenna_delete.html'
    success_url = reverse_lazy('antennas_list')
    required_permissions = ('inventory.delete_antenna',)


def list_antenna(request):
    """
    Used to return the list to the select2 element using ajax call.
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    antennas = Antenna.objects.filter(organization__id=org_id).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]

    return HttpResponse(json.dumps({
        "total_count": antennas.count(),
        "incomplete_results": False,
        "items": list(antennas)
    }))

def select_antenna(request, pk):
    """
    Called when Select2 is created to allow the user to initialize the selection based on the value of the element select2 is attached to.
    """
    return HttpResponse(json.dumps([Antenna.objects.get(id=pk).alias]))


#****************************************** Base Station ********************************************
class BaseStationList(PermissionsRequiredMixin, TemplateView):
    """
    Class Based View for the Base Station data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'base_station/base_stations_list.html'
    required_permissions = ('inventory.view_basestation',)

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
                edit_action = '<a href="/base_station/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_basestation'):
                delete_action = '<a href="/base_station/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
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


class BaseStationCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Class based view to create new Base Station.
    """
    template_name = 'base_station/base_station_new.html'
    model = BaseStation
    form_class = BaseStationForm
    success_url = reverse_lazy('base_stations_list')
    required_permissions = ('inventory.add_basestation',)


class BaseStationUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
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
    Used to return the list to the select2 element using ajax call.
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    if str(org_id) == "0":
        class SelfObject: pass
        self_object = SelfObject()
        self_object.request = request
        organizations = logged_in_user_organizations(self_object)
        base_stations = BaseStation.objects.filter(organization__id__in=organizations).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]
    else:
        base_stations = BaseStation.objects.filter(organization__id=org_id).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]

    return HttpResponse(json.dumps({
        "total_count": base_stations.count(),
        "incomplete_results": False,
        "items": list(base_stations)
    }))

def select_base_station(request, pk):
    """
    Called when Select2 is created to allow the user to initialize the selection based on the value of the element select2 is attached to.
    """
    return HttpResponse(json.dumps([BaseStation.objects.get(id=pk).alias]))


#**************************************** Backhaul *********************************************
class BackhaulList(PermissionsRequiredMixin, TemplateView):
    """
    Class Based View for the Backhaul data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'backhaul/backhauls_list.html'
    required_permissions = ('inventory.view_backhaul',)

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
                edit_action = '<a href="/backhaul/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_backhaul'):
                delete_action = '<a href="/backhaul/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
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


class BackhaulCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Class based view to create new backhaul..
    """
    template_name = 'backhaul/backhaul_new.html'
    model = Backhaul
    form_class = BackhaulForm
    success_url = reverse_lazy('backhauls_list')
    required_permissions = ('inventory.add_backhaul',)


class BackhaulUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
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
    Used to return the list to the select2 element using ajax call.
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    if str(org_id) == "0":
        class SelfObject: pass
        self_object = SelfObject()
        self_object.request = request
        organizations = logged_in_user_organizations(self_object)
        backhauls = Backhaul.objects.filter(organization__id__in=organizations).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]
    else:
        backhauls = Backhaul.objects.filter(organization__id=org_id).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]

    return HttpResponse(json.dumps({
        "total_count": backhauls.count(),
        "incomplete_results": False,
        "items": list(backhauls)
    }))

def select_backhaul(request, pk):
    """
    Called when Select2 is created to allow the user to initialize the selection based on the value of the element select2 is attached to.
    """
    return HttpResponse(json.dumps([Backhaul.objects.get(id=pk).alias]))


#**************************************** Sector *********************************************
class SectorList(PermissionsRequiredMixin, TemplateView):
    """
    Class Based View for the Sector data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'sector/sectors_list.html'
    required_permissions = ('inventory.view_sector',)

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
                edit_action = '<a href="/sector/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_sector'):
                delete_action = '<a href="/sector/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
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


class SectorCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Class based view to create new Sector.
    """
    template_name = 'sector/sector_new.html'
    model = Sector
    form_class = SectorForm
    success_url = reverse_lazy('sectors_list')
    required_permissions = ('inventory.add_sector',)


class SectorUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
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
    Used to return the list to the select2 element using ajax call.
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    if str(org_id) == "0":
        class SelfObject: pass
        self_object = SelfObject()
        self_object.request = request
        organizations = logged_in_user_organizations(self_object)
        sectors = Sector.objects.filter(organization__id__in=organizations).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]
    else:
        sectors = Sector.objects.filter(organization__id=org_id).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]

    return HttpResponse(json.dumps({
        "total_count": sectors.count(),
        "incomplete_results": False,
        "items": list(sectors)
    }))

def select_sector(request, pk):
    """
    Called when Select2 is created to allow the user to initialize the selection based on the value of the element select2 is attached to.
    """
    return HttpResponse(json.dumps([Sector.objects.get(id=pk).alias]))


#**************************************** Customer *********************************************
class CustomerList(PermissionsRequiredMixin, TemplateView):
    """
    Class Based View for the Customer data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'customer/customers_list.html'
    required_permissions = ('inventory.view_customer',)

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
                edit_action = '<a href="/customer/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_customer'):
                delete_action = '<a href="/customer/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
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


class CustomerCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Class based view to create new customer.
    """
    template_name = 'customer/customer_new.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customers_list')
    required_permissions = ('inventory.add_customer',)


class CustomerUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
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


class CustomerDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Customer.
    """
    model = Customer
    template_name = 'customer/customer_delete.html'
    success_url = reverse_lazy('customers_list')
    required_permissions = ('inventory.delete_customer',)

def list_customer(request):
    """
    Used to return the list to the select2 element using ajax call.
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    customers = Customer.objects.filter(organization__id=org_id).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]

    return HttpResponse(json.dumps({
        "total_count": customers.count(),
        "incomplete_results": False,
        "items": list(customers)
    }))

def select_customer(request, pk):
    """
    Called when Select2 is created to allow the user to initialize the selection based on the value of the element select2 is attached to.
    """
    return HttpResponse(json.dumps([Customer.objects.get(id=pk).alias]))


#**************************************** Sub Station *********************************************
class SubStationList(PermissionsRequiredMixin, TemplateView):
    """
    Class Based View for the Sub Station data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'sub_station/sub_stations_list.html'
    required_permissions = ('inventory.view_substation',)

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
                edit_action = '<a href="/sub_station/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_substation'):
                delete_action = '<a href="/sub_station/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
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


class SubStationCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Class based view to create new Sub Station.
    """
    template_name = 'sub_station/sub_station_new.html'
    model = SubStation
    form_class = SubStationForm
    success_url = reverse_lazy('sub_stations_list')
    required_permissions = ('inventory.add_substation',)


class SubStationUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
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


class SubStationDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Sub Station.
    """
    model = SubStation
    template_name = 'sub_station/sub_station_delete.html'
    success_url = reverse_lazy('sub_stations_list')
    required_permissions = ('inventory.delete_substation',)


def list_sub_station(request):
    """
    Used to return the list to the select2 element using ajax call.
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    if str(org_id) == "0":
        class SelfObject: pass
        self_object = SelfObject()
        self_object.request = request
        organizations = logged_in_user_organizations(self_object)
        sub_stations = SubStation.objects.filter(organization__id__in=organizations).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]
    else:
        sub_stations = SubStation.objects.filter(organization__id=org_id).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]

    return HttpResponse(json.dumps({
        "total_count": sub_stations.count(),
        "incomplete_results": False,
        "items": list(sub_stations)
    }))

def select_sub_station(request, pk):
    """
    Called when Select2 is created to allow the user to initialize the selection based on the value of the element select2 is attached to.
    """
    return HttpResponse(json.dumps([SubStation.objects.get(id=pk).alias]))

#**************************************** Circuit *********************************************
class CircuitList(PermissionsRequiredMixin, TemplateView):
    """
    Class Based View for the Circuit data table rendering.

    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.
    """
    template_name = 'circuit/circuits_list.html'
    required_permissions = ('inventory.view_circuit',)

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
                edit_action = '<a href="/circuit/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_circuit'):
                delete_action = '<a href="/circuit/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>&nbsp&nbsp'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                actions = edit_action + delete_action
            else:
                actions = ''
            actions = actions + '<a href="/circuit/{0}/l2_reports/"><i class="fa fa-sign-in text-info" title="View L2 reports for circuit"\
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


class CircuitCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Class based view to create new Circuit.
    """

    template_name = 'circuit/circuit_new.html'
    model = Circuit
    form_class = CircuitForm
    success_url = reverse_lazy('circuits_list')
    required_permissions = ('inventory.add_circuit',)


class CircuitUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
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


class CircuitDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Circuit.
    """
    model = Circuit
    template_name = 'circuit/circuit_delete.html'
    success_url = reverse_lazy('circuits_list')
    required_permissions = ('inventory.delete_circuit',)


def list_circuit(request):
    """
    Used to return the list to the select2 element using ajax call.
    """
    org_id = request.GET['org']
    sSearch = request.GET['sSearch']
    if str(org_id) == "0":
        class SelfObject: pass
        self_object = SelfObject()
        self_object.request = request
        organizations = logged_in_user_organizations(self_object)
        circuits = Circuit.objects.filter(organization__id__in=organizations).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]
    else:
        circuits = Circuit.objects.filter(organization__id=org_id).\
            filter(alias__icontains=sSearch).values('id', 'alias')[:50]

    return HttpResponse(json.dumps({
        "total_count": circuits.count(),
        "incomplete_results": False,
        "items": list(circuits)
    }))


def select_circuit(request, pk):
    """
    Called when Select2 is created to allow the user to initialize the selection based on the value of the element select2 is attached to.
    """
    return HttpResponse(json.dumps([Circuit.objects.get(id=pk).alias]))


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
        if not ('circuit_id' in self.kwargs):
            datatable_headers.append({'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'auto', });

        #if the user role is Admin or operator then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        if 'circuit_id' in self.kwargs:
            context['circuit_id'] = self.kwargs['circuit_id']
            context['page_type'] = 'individual'
        else:
            context['circuit_id'] = 0
            context['page_type'] = 'all'

        return context

## This class load L2 reports datatable for particular circuit_id
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

        condition = ""

        if int(circuit_id) > 0:
            circuit_instance = Circuit.objects.filter(id=circuit_id)
            # condition to fetch l2 reports data from db
            condition = (Q(user_id=self.request.user) | Q(is_public=1)) & (Q(circuit_id=circuit_instance))
        else:
            condition = (Q(user_id=self.request.user) | Q(is_public=1))
            self.columns.append('circuit_id')

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
            # Append Circuit Alias when all listing is shown
            if int(circuit_id) == 0:
                circuit_alias = Circuit.objects.filter(id=data['circuit_id']).values('alias')
                report_object['circuit_id'] = circuit_alias[0]['alias'].title()

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

        if len(qs) > 0:
            if('circuit_id' in qs[0]):
                for dct in qs:
                    dct.update(actions='<a href="../../../media/'+dct['file_url']+'" target="_blank" title="Download Report">\
                        <i class="fa fa-arrow-circle-o-down text-info"></i></a>\
                        '.format(dct.pop('id')),
                       added_on=dct['added_on'].strftime("%Y-%m-%d") if dct['added_on'] != "" else "")
            else:
                for dct in qs:
                    dct.update(actions='<a href="../../../media/'+dct['file_url']+'" target="_blank" title="Download Report">\
                        <i class="fa fa-arrow-circle-o-down text-info"></i></a>\
                        <a class="delete_l2report" style="cursor:pointer;" title="Delete Report" url="{0}/delete/">\
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

        if 'circuit_id' in self.kwargs:
            ckt_id = self.kwargs['circuit_id']
        else:
            ckt_id = 0

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

## This class load all L2 reports datatable
class AllL2ReportListingTable(BaseDatatableView):
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

        # condition to fetch l2 reports data from db
        condition = (Q(user_id=self.request.user) | Q(is_public=1))
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


class IconSettingsListingTable(PermissionsRequiredMixin, DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    """
    Class based View to render IconSettings Data table.
    """
    model = IconSettings
    required_permissions = ('inventory.view_iconsettings',)
    columns = ['alias', 'upload_image']
    order_columns = ['alias', 'upload_image']

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

            dct.update(actions='<a href="/icon_settings/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/icon_settings/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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


class IconSettingsUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update IconSettings.
    """
    template_name = 'icon_settings/icon_settings_update.html'
    model = IconSettings
    form_class = IconSettingsForm
    success_url = reverse_lazy('icon_settings_list')
    required_permissions = ('inventory.change_iconsettings',)


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
        ValuesQuerySetMixin,
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

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            dct.update(actions='<a href="/live_polling_settings/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/live_polling_settings/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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


class LivePollingSettingsUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update LivePollingSettings.
    """
    template_name = 'live_polling_settings/live_polling_settings_update.html'
    model = LivePollingSettings
    form_class = LivePollingSettingsForm
    success_url = reverse_lazy('live_polling_settings_list')
    required_permissions = ('inventory.change_livepollingsettings',)


class LivePollingSettingsDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the LivePollingSettings
    """
    model = LivePollingSettings
    template_name = 'live_polling_settings/live_polling_settings_delete.html'
    success_url = reverse_lazy('live_polling_settings_list')
    required_permissions = ('inventory.delete_livepollingsettings',)


# **************************************** ThresholdConfiguration *********************************************
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
        # if user is superadmin or gisadmin
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ThresholdConfigurationListingTable(PermissionsRequiredMixin, DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    """
    Class based View to render ThresholdConfiguration Data table.
    """
    model = ThresholdConfiguration
    required_permissions = ('inventory.view_thresholdconfiguration',)
    columns = ['alias', 'live_polling_template__alias']
    order_columns = ['alias', 'live_polling_template__alias']
    tab_search = {
                   "tab_kwarg": 'technology',
                   "tab_attr": "live_polling_template__technology__name",
                 }

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            dct.update(actions='<a href="/threshold_configuration/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/threshold_configuration/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


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


class ThresholdConfigurationUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Threshold Configuration.
    """
    template_name = 'threshold_configuration/threshold_configuration_update.html'
    model = ThresholdConfiguration
    form_class = ThresholdConfigurationForm
    success_url = reverse_lazy('threshold_configuration_list')
    required_permissions = ('inventory.change_threshold_configuration',)


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
            {'mData': 'icon_settings',           'sTitle': 'Icons Range',               'sWidth': 'auto',     'bSortable': False},
            {'mData': 'user_selection',          'sTitle': 'Setting Selection',         'sWidth': 'auto',     'bSortable': False},]

        # user_id = self.request.user.id

        #if user is superadmin or gisadmin
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)

        is_global = False
        if 'admin' in self.request.path:
            is_global = True

        context['is_global'] = json.dumps(is_global)

        return context


class ThematicSettingsListingTable(PermissionsRequiredMixin, ValuesQuerySetMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class based View to render Thematic Settings Data table.
    """
    model = ThematicSettings
    required_permissions = ('inventory.view_thematicsettings',)
    columns = ['alias', 'threshold_template', 'icon_settings']
    order_columns = ['alias', 'threshold_template']
    search_columns = ['alias', 'icon_settings']

    tab_search = {
        "tab_kwarg": 'technology',
        "tab_attr": "threshold_template__live_polling_template__technology__name",
    }

    def get_initial_queryset(self):
        is_global = 1
        if self.request.GET.get('admin'):
            is_global = 0

        qs = super(ThematicSettingsListingTable, self).get_initial_queryset()

        return qs.filter(is_global=is_global)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
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
        return json_data


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
        icon_settings_keys= list(set(form.data.keys())-set(form.cleaned_data.keys()+['csrfmiddlewaretoken']))
        icon_settings_values_list=[ { key: form.data[key] }  for key in icon_settings_keys if form.data[key]]
        self.object = form.save()
        self.object.icon_settings=icon_settings_values_list
        self.object.save()
        # self.object = form.save()
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
            self.result['message']='Service Thematic Setting Bind to User Successfully'
            self.result['data']['objects']['username']=self.request.user.userprofile.username
            self.result['data']['objects']['thematic_setting_name']= ThematicSettings.objects.get(id=int(thematic_setting_id)).name

        return HttpResponse(json.dumps(self.result))

#************************************ Service Thematic Settings ******************************************
class ServiceThematicSettingsList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render ServiceThematicSettings List Page.
    """
    model = ThematicSettings
    template_name = 'service_thematic_settings/service_thematic_settings_list.html'
    required_permissions = ('inventory.view_thematicsettings',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(ServiceThematicSettingsList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'alias',                   'sTitle': 'Alias',                     'sWidth': 'auto'},
            {'mData': 'threshold_template',      'sTitle': 'Threshold Template',        'sWidth': 'auto'},
            {'mData': 'icon_settings',           'sTitle': 'Icons Range',               'sWidth': 'auto',   'bSortable': False},
            {'mData': 'user_selection',          'sTitle': 'Setting Selection',         'sWidth': 'auto',   'bSortable': False},]

        # user_id = self.request.user.id

        #if user is superadmin or gisadmin
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)

        is_global = False
        if 'admin' in self.request.path:
            is_global = True

        context['is_global'] = json.dumps(is_global)

        return context


class ServiceThematicSettingsListingTable(PermissionsRequiredMixin, ValuesQuerySetMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class based View to render Thematic Settings Data table.
    """
    model = ThematicSettings
    required_permissions = ('inventory.view_thematicsettings',)
    columns = ['alias', 'threshold_template', 'icon_settings']
    order_columns = ['alias', 'threshold_template']
    search_columns = ['alias', 'icon_settings']

    tab_search = {
        "tab_kwarg": 'technology',
        "tab_attr": "threshold_template__live_polling_template__technology__name",
    }

    def get_initial_queryset(self):
        is_global = 1
        if self.request.GET.get('admin'):
            is_global = 0

        qs = super(ServiceThematicSettingsListingTable, self).get_initial_queryset()

        return qs.filter(is_global=is_global)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
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
                actions='<a href="/serv_thematic_settings/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/serv_thematic_settings/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


class ServiceThematicSettingsDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the Service Thematic Settings detail.
    """
    model = ThematicSettings
    required_permissions = ('inventory.view_thematicsettings',)
    template_name = 'service_thematic_settings/service_thematic_settings_detail.html'


class ServiceThematicSettingsCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new ServiceThematicSettings.
    """
    template_name = 'service_thematic_settings/service_thematic_settings_new.html'
    model = ThematicSettings
    form_class = ThematicSettingsForm
    success_url = reverse_lazy('service_thematic_settings_list')
    required_permissions = ('inventory.add_thematicsettings',)
    icon_settings_keys = ( 'icon_settings1', 'icon_settings2', 'icon_settings3', 'icon_settings4', 'icon_settings5',
                           'icon_settings6', 'icon_settings7', 'icon_settings8', 'icon_settings9', 'icon_settings10'
            )

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = ServiceThematicSettingsForm()
        icon_settings = IconSettings.objects.all()
        threshold_configuration_form = ServiceThresholdConfigurationForm()
        live_polling_settings_form = ServiceLivePollingSettingsForm()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  threshold_configuration_form=threshold_configuration_form,
                                  live_polling_settings_form=live_polling_settings_form,
                                  icon_settings=icon_settings))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = ServiceThematicSettingsForm(self.request.POST)
        threshold_configuration_form = ServiceThresholdConfigurationForm(self.request.POST)
        live_polling_settings_form = ServiceLivePollingSettingsForm(self.request.POST)
        if (form.is_valid() and threshold_configuration_form.is_valid() and live_polling_settings_form.is_valid()):
            return self.form_valid(form, threshold_configuration_form, live_polling_settings_form)
        else:
            return self.form_invalid(form, threshold_configuration_form, live_polling_settings_form)

    def form_valid(self, form, threshold_configuration_form, live_polling_settings_form):
        """
        Called if all forms are valid. Creates a ThematicSettings, LivePollingSettings and IconSettings.
        """
        name = form.instance.name
        alias = form.instance.alias
        live_polling_settings_form.instance.name = name
        live_polling_settings_form.instance.alias = alias
        live_polling_object = live_polling_settings_form.save()
        threshold_configuration_form.instance.name = name
        threshold_configuration_form.instance.alias = alias
        threshold_configuration_form.instance.live_polling_template = live_polling_object
        threshold_configuration_object = threshold_configuration_form.save()
        form.instance.threshold_template = threshold_configuration_object
        icon_settings_values_list = [ { key: form.data[key] }  for key in self.icon_settings_keys if form.data[key]]
        form.instance.icon_settings = icon_settings_values_list
        self.object = form.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, threshold_configuration_form, live_polling_settings_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        icon_settings = IconSettings.objects.all()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  threshold_configuration_form=threshold_configuration_form,
                                  live_polling_settings_form=live_polling_settings_form,
                                  icon_settings=icon_settings))


class ServiceThematicSettingsUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update Service Thematic Settings.
    """
    template_name = 'service_thematic_settings/service_thematic_settings_update.html'
    model = ThematicSettings
    form_class = ServiceThematicSettingsForm
    success_url = reverse_lazy('service_thematic_settings_list')
    required_permissions = ('inventory.change_thematicsettings',)
    icon_settings_keys = ( 'icon_settings1', 'icon_settings2', 'icon_settings3', 'icon_settings4', 'icon_settings5',
                           'icon_settings6', 'icon_settings7', 'icon_settings8', 'icon_settings9', 'icon_settings10'
            )

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = ServiceThematicSettingsForm(instance=self.object)
        icon_settings = IconSettings.objects.all()
        threshold_configuration_form = ServiceThresholdConfigurationForm(instance=self.object.threshold_template)
        icon_details = list()
        icon_details_selected = dict()
        if form.instance.icon_settings:
            form.instance.icon_settings = eval(form.instance.icon_settings)
            for icon_setting in form.instance.icon_settings:
                icon_details_selected['range_' + icon_setting.keys()[0][-1]] = icon_setting.values()[0]
        live_polling_settings_form = ServiceLivePollingSettingsForm(instance=self.object.threshold_template.live_polling_template)
        return self.render_to_response(
            self.get_context_data(form=form,
                                  threshold_configuration_form=threshold_configuration_form,
                                  live_polling_settings_form=live_polling_settings_form,
                                  icon_settings=icon_settings,
                                  icon_details_selected=icon_details_selected,))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = ServiceThematicSettingsForm(self.request.POST, instance=self.object)
        threshold_configuration_form = ServiceThresholdConfigurationForm(self.request.POST, instance=self.object.threshold_template)
        live_polling_settings_form = ServiceLivePollingSettingsForm(self.request.POST, instance=self.object.threshold_template.live_polling_template)
        if (form.is_valid() and threshold_configuration_form.is_valid() and live_polling_settings_form.is_valid()):
            return self.form_valid(form, threshold_configuration_form, live_polling_settings_form)
        else:
            return self.form_invalid(form, threshold_configuration_form, live_polling_settings_form)

    def form_valid(self, form, threshold_configuration_form, live_polling_settings_form):
        """
        Called if all forms are valid. Updates ThematicSettings, LivePollingSettings and IconSettings.
        """
        self.object = self.get_object()
        icon_settings_values_list = [ { key: form.data[key] }  for key in self.icon_settings_keys if form.data[key]]
        form.instance.icon_settings = icon_settings_values_list
        form.save()
        threshold_configuration_form.save()
        live_polling_settings_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, threshold_configuration_form, live_polling_settings_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        icon_settings = IconSettings.objects.all()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  threshold_configuration_form=threshold_configuration_form,
                                  live_polling_settings_form=live_polling_settings_form,
                                  icon_settings=icon_settings))


class ServiceThematicSettingsDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the Thematic Settings.
    """
    model = ThematicSettings
    template_name = 'service_thematic_settings/service_thematic_settings_delete.html'
    success_url = reverse_lazy('service_thematic_settings_list')
    required_permissions = ('inventory.delete_thematicsettings',)


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


class GISInventoryBulkImportListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    """
    A generic class based view for the gis inventory bulk import data table rendering.

    """
    model = GISInventoryBulkImport
    columns = ['original_filename', 'valid_filename', 'invalid_filename', 'status', 'sheet_name', 'technology', 'upload_status', 'description', 'uploaded_by', 'added_on', 'modified_on']
    order_columns = ['original_filename', 'valid_filename', 'invalid_filename', 'status', 'sheet_name', 'technology', 'upload_status', 'description', 'uploaded_by', 'added_on', 'modified_on']
    search_columns = ['sheet_name', 'technology', 'description', 'uploaded_by']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
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

            dct.update(actions='<a href="/bulk_import/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                                <a href="/bulk_import/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.get('id')))
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
        return json_data


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
class PingThematicSettingsList(ListView):
    """
    Class Based View to render PingThematicSettings List Page.
    """
    model = PingThematicSettings
    template_name = 'ping_thematic_settings/ping_thematic_settings_list.html'

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


class PingThematicSettingsListingTable(ValuesQuerySetMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class based View to render Thematic Settings Data table.
    """
    model = PingThematicSettings
    columns = ['alias', 'service', 'data_source', 'icon_settings']
    order_columns = ['alias', 'service', 'data_source']
    tab_search = {
        "tab_kwarg": 'technology',
        "tab_attr": "technology__name",
    }

    def get_initial_queryset(self):
        is_global = 1
        if self.request.GET.get('admin'):
            is_global = 0

        qs = super(PingThematicSettingsListingTable, self).get_initial_queryset()

        return qs.filter(is_global=is_global)

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


class PingThematicSettingsDetail(DetailView):
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
        icon_settings_keys = list(set(form.data.keys()) - set(
            [key for key in form.cleaned_data.keys() if "icon" not in key] + ['csrfmiddlewaretoken']))

        # sorting icon settings list
        icon_settings_keys = sorted(icon_settings_keys, key=lambda r: int(''.join(x for x in r if x.isdigit())))

        icon_settings_values_list = [{key: form.data[key]} for key in icon_settings_keys if form.data[key]]
        self.object = form.save()
        self.object.icon_settings = icon_settings_values_list
        self.object.save()
        # self.object = form.save()
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


class DownloadSelectedBSInventory(View):
    """ Download GIS Inventory excel sheet of selected Base Stations

        :Parameters:
            - 'base_stations' (str) - list of base stations in form of string i.e. [1, 2, 3, 4]

        :Returns:
           - 'file' (file) - inventory excel sheet
    """
    def get(self, request):
        # get base stations id's list
        bs_ids = eval(str(self.request.GET.get('base_stations', None)))

        # list of ptp rows
        ptp_rows = []

        # list of ptp bh rows
        ptp_bh_rows = []

        # list of pmp bs
        pmp_bs_rows = []

        # list of pmp sm sheet
        pmp_sm_rows = []

        # list of wimax bs rows
        wimax_bs_rows = []

        # list of wimax ss rows
        wimax_ss_rows = []

        # selected inventory
        selected_inventory = dict()

        # ptp dictionary
        ptp_fields = ['State', 'City', 'Circuit ID', 'Circuit Type', 'Customer Name', 'BS Address', 'BS Name',
                      'QOS (BW)', 'Latitude', 'Longitude', 'MIMO/Diversity', 'Antenna Height', 'Polarization',
                      'Antenna Type', 'Antenna Gain', 'Antenna Mount Type', 'Ethernet Extender', 'Building Height',
                      'Tower/Pole Height', 'Cable Length', 'RSSI During Acceptance', 'Throughput During Acceptance',
                      'Date Of Acceptance', 'BH BSO', 'IP', 'MAC', 'HSSU Used', 'BS Switch IP', 'Aggregation Switch',
                      'Aggregation Switch Port', 'BS Converter IP', 'POP Converter IP', 'Converter Type',
                      'BH Configured On Switch/Converter', 'Switch/Converter Port', 'BH Capacity', 'BH Offnet/Onnet',
                      'Backhaul Type', 'BH Circuit ID', 'PE Hostname', 'PE IP', 'BSO Circuit ID', 'SS City', 'SS State',
                      'SS Circuit ID', 'SS Customer Name', 'SS Customer Address', 'SS BS Name', 'SS QOS (BW)',
                      'SS Latitude', 'SS Longitude', 'SS Antenna Height', 'SS Antenna Type', 'SS Antenna Gain',
                      'SS Antenna Mount Type', 'SS Ethernet Extender', 'SS Building Height', 'SS Tower/Pole Height',
                      'SS Cable Length', 'SS RSSI During Acceptance', 'SS Throughput During Acceptance',
                      'SS Date Of Acceptance', 'SS BH BSO', 'SS IP', 'SS MAC',
                      'BS Product Type', 'BS Frequency', 'BS UAS', 'BS RSSI', 'BS Estimated Throughput',
                      'BS Utilisation DL', 'BS Utilisation UL', 'BS Uptime', 'BS Link Distance', 'BS CBW', 'BS Latency',
                      'BS PD', 'BS Auto Negotiation', 'BS Duplex', 'BS Speed', 'BS Link',
                      'SS Product Type', 'SS Frequency', 'SS UAS', 'SS RSSI', 'SS Estimated Throughput',
                      'SS Utilisation DL', 'SS Utilisation UL', 'SS Uptime', 'SS Link Distance', 'SS CBW', 'SS Latency',
                      'SS PD', 'SS Auto Negotiation', 'SS Duplex', 'SS Speed', 'SS Link']

        # ptp bh dictionary
        ptp_bh_fields = ['State', 'City', 'Circuit ID', 'Circuit Type', 'Customer Name', 'BS Address', 'BS Name',
                         'QOS (BW)', 'Latitude', 'Longitude', 'MIMO/Diversity', 'Antenna Height', 'Polarization',
                         'Antenna Type', 'Antenna Gain', 'Antenna Mount Type', 'Ethernet Extender', 'Building Height',
                         'Tower/Pole Height', 'Cable Length', 'RSSI During Acceptance', 'Throughput During Acceptance',
                         'Date Of Acceptance', 'BH BSO', 'IP', 'MAC', 'HSSU Used', 'BS Switch IP', 'Aggregation Switch',
                         'Aggregation Switch Port', 'BS Converter IP', 'POP Converter IP', 'Converter Type',
                         'BH Configured On Switch/Converter', 'Switch/Converter Port', 'BH Capacity', 'BH Offnet/Onnet',
                         'Backhaul Type', 'BH Circuit ID', 'PE Hostname', 'PE IP', 'BSO CKT ID', 'SS City', 'SS State',
                         'SS Circuit ID', 'SS Customer Name', 'SS Customer Address', 'SS BS Name', 'SS QOS (BW)',
                         'SS Latitude', 'SS Longitude', 'SS Antenna Height', 'SS Antenna Type', 'SS Antenna Gain',
                         'SS Antenna Mount Type', 'SS Ethernet Extender', 'SS Building Height', 'SS Tower/Pole Height',
                         'SS Cable Length', 'SS RSSI During Acceptance', 'SS Throughput During Acceptance',
                         'SS Date Of Acceptance', 'SS BH BSO', 'SS IP', 'SS MAC', 'SS MIMO/Diversity',
                         'SS Polarization',
                         'BS Product Type', 'BS Frequency', 'BS UAS', 'BS RSSI', 'BS Estimated Throughput',
                         'BS Utilisation DL', 'BS Utilisation UL', 'BS Uptime', 'BS Link Distance', 'BS CBW',
                         'BS Latency', 'BS PD', 'BS Auto Negotiation', 'BS Duplex', 'BS Speed', 'BS Link',
                         'SS Product Type', 'SS Frequency', 'SS UAS', 'SS RSSI', 'SS Estimated Throughput',
                         'SS Utilisation DL', 'SS Utilisation UL', 'SS Uptime', 'SS Link Distance', 'SS CBW',
                         'SS Latency', 'SS PD', 'SS Auto Negotiation', 'SS Duplex', 'SS Speed', 'SS Link']

        # pmp bs dictionary
        pmp_bs_fields = ['State', 'City', 'Address', 'BS Name', 'Type Of BS (Technology)', 'Site Type',
                         'Infra Provider', 'Site ID', 'Building Height', 'Tower Height', 'Latitude', 'Longitude',
                         'ODU IP', 'Sector Name', 'Make Of Antenna', 'Polarization', 'Antenna Tilt', 'Antenna Height',
                         'Antenna Beamwidth', 'Azimuth', 'Sync Splitter Used', 'Type Of GPS', 'BS Switch IP',
                         'Aggregation Switch', 'Aggregation Switch Port', 'BS Converter IP', 'POP Converter IP',
                         'Converter Type', 'BH Configured On Switch/Converter', 'Switch/Converter Port', 'BH Capacity',
                         'BH Offnet/Onnet', 'Backhaul Type', 'BH Circuit ID', 'PE Hostname', 'PE IP', 'DR Site',
                         'Sector ID', 'BSO Circuit ID', 'Frequency', 'Cell Radius', 'Utilization DL', 'Utilization UL',
                         'Sector Uptime', 'TX Power', 'RX Power']

        # pmp ss dictionary
        pmp_sm_fields = ['Customer Name', 'Circuit ID', 'SS IP', 'QOS (BW)', 'Latitude', 'Longitude', 'MAC',
                         'Building Height', 'Tower/Pole Height', 'Antenna Height', 'Antenna Beamwidth',
                         'Polarization', 'Antenna Type', 'SS Mount Type', 'Ethernet Extender', 'Cable Length',
                         'RSSI During Acceptance', 'CINR During Acceptance', 'Customer Address', 'Date Of Acceptance',
                         'Lens/Reflector', 'AP IP', 'Frequency', 'Sector ID', 'RSSI DL', 'RSSI UL', 'Jitter DL',
                         'Jitter UL', 'Transmit Power', 'Polled SS IP', 'Polled SS MAC', 'Polled BS IP',
                         'Polled BS MAC', 'Session Uptime', 'Latency', 'PD', 'Utilization DL', 'Utilization UL',
                         'Auto Negotiation', 'Duplex', 'Speed', 'Link']

        # wimax bs dictionary
        wimax_bs_fields = ['State', 'City', 'Address', 'BS Name', 'Type Of BS (Technology)', 'Site Type',
                           'Infra Provider', 'Site ID', 'Building Height', 'Tower Height', 'Latitude', 'Longitude',
                           'IDU IP', 'Sector Name', 'Make Of Antenna', 'Polarization', 'Antenna Tilt', 'Antenna Height',
                           'Antenna Beamwidth', 'Azimuth', 'Installation Of Splitter', 'Type Of GPS', 'BS Switch IP',
                           'Aggregation Switch', 'Aggregation Switch Port', 'BS Converter IP', 'POP Converter IP',
                           'Converter Type', 'BH Configured On Switch/Converter', 'Switch/Converter Port',
                           'BH Capacity', 'BH Offnet/Onnet', 'Backhaul Type', 'BH Circuit ID', 'PE Hostname',
                           'PE IP', 'DR Site', 'Sector ID', 'BSO Circuit ID', 'PMP', 'Vendor', 'Sector Utilization',
                           'Frequency', 'MRC', 'IDU Type', 'System Uptime', 'Latency', 'PD']

        # wimax ss dictionary
        wimax_ss_fields = ['Customer Name', 'Circuit ID', 'SS IP', 'QOS (BW)', 'Latitude', 'Longitude', 'MAC',
                           'Building Height', 'Tower/Pole Height', 'Antenna Height', 'Antenna Beamwidth',
                           'Polarization', 'Antenna Type', 'SS Mount Type', 'Ethernet Extender', 'Cable Length',
                           'RSSI During Acceptance', 'CINR During Acceptance', 'Customer Address', 'Date Of Acceptance',
                           'Vendor', 'Frequency', 'Sector ID', 'Polled SS IP', 'Polled SS MAC', 'RSSI DL', 'RSSI UL',
                           'CINR DL', 'CINR UL', 'INTRF DL', 'INTRF UL', 'PTX', 'Session Uptime', 'Device Uptime',
                           'Modulation UL FEC', 'Modulation DL FEC', 'Latency', 'PD', 'Utilization DL',
                           'Utilization UL', 'Auto Negotiation', 'Duplex', 'Speed', 'Link']

        # loop on base stations by using bs_ids list conatining base stations id's
        try:
            for bs_id in bs_ids:
                # base station
                base_station = BaseStation.objects.get(pk=int(bs_id))

                # sectors associated with base station (base_station)
                sectors = base_station.sector.all()

                # loop on sectors to get inventory rows by technology
                for sector in sectors:
                    # sector technology
                    technology = sector.bs_technology.name
                    if technology == "P2P":
                        rows = self.get_selected_ptp_inventory(base_station, sector)
                        # insert 'ptp' data dictionary in 'ptp_rows' list
                        ptp_rows.extend(rows['ptp'])
                        # insert 'ptp_bh' data dictionary in 'ptp_bh_rows' list
                        ptp_bh_rows.extend(rows['ptp_bh'])
                    elif technology == "PMP":
                        rows = self.get_selected_pmp_inventory(base_station, sector)
                        # insert 'pmp bs' data dictionary in 'pmp_bs_rows' list
                        pmp_bs_rows.extend(rows['pmp_bs'])
                        # insert 'pmp_sm' data dictionary in 'pmp_sm_rows' list
                        pmp_sm_rows.extend(rows['pmp_sm'])
                    elif technology == "WiMAX":
                        rows = self.get_selected_wimax_inventory(base_station, sector)
                        # insert 'wimax bs' data dictionary in 'wimax_bs_rows' list
                        wimax_bs_rows.extend(rows['wimax_bs'])
                        # insert 'wimax_ss' data dictionary in 'wimax_ss_rows' list
                        wimax_ss_rows.extend(rows['wimax_ss'])
                    else:
                        pass

        except Exception as e:
            logger.info("Something wrongs with base station in initial loop. Exception: {}".format(e.message))

        # insert 'ptp rows' in selected inventory dictionary
        selected_inventory['ptp'] = ptp_rows

        # insert 'ptp rows' in selected inventory dictionary
        selected_inventory['ptp_bh'] = ptp_bh_rows

        # insert 'ptp rows' in selected inventory dictionary
        selected_inventory['pmp_bs'] = pmp_bs_rows

        # insert 'ptp rows' in selected inventory dictionary
        selected_inventory['pmp_sm'] = pmp_sm_rows

        # insert 'ptp rows' in selected inventory dictionary
        selected_inventory['wimax_bs'] = wimax_bs_rows

        # insert 'ptp rows' in selected inventory dictionary
        selected_inventory['wimax_ss'] = wimax_ss_rows

        # inventory excel workbook
        inventory_wb = xlwt.Workbook()

        # ***************************** PTP *******************************
        # ptp bs excel rows
        ptp_excel_rows = []
        for val in ptp_rows:
            temp_list = list()
            for key in ptp_fields:
                try:
                    temp_list.append(val[key])
                except Exception as e:
                    temp_list.append("")
                    logger.info(e.message)
            ptp_excel_rows.append(temp_list)

        # wimax bs sheet (contain by inventory excel workbook i.e inventory_wb)
        ws_ptp = inventory_wb.add_sheet("PTP")

        # style for header row in excel
        style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

        # creating excel headers
        try:
            for i, col in enumerate(ptp_fields):
                ws_ptp.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
        except Exception as e:
            logger.info("Problem in creating excel headers. Exception: ", e.message)

        # creating excel rows
        try:
            for i, l in enumerate(ptp_excel_rows):
                i += 1
                for j, col in enumerate(l):
                    ws_ptp.write(i, j, col)
        except Exception as e:
            logger.info("Problem in creating excel rows. Exception: ", e.message)

        # ***************************** PTP BH *******************************
        # ptp bh bs excel rows
        ptp_bh_excel_rows = []
        for val in ptp_bh_rows:
            temp_list = list()
            for key in ptp_bh_fields:
                try:
                    temp_list.append(val[key])
                except Exception as e:
                    temp_list.append("")
                    logger.info(e.message)
            ptp_bh_excel_rows.append(temp_list)

        # wimax bs sheet (contain by inventory excel workbook i.e inventory_wb)
        ws_ptp_bh = inventory_wb.add_sheet("PTP BH")

        # style for header row in excel
        style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

        # creating excel headers
        try:
            for i, col in enumerate(ptp_bh_fields):
                ws_ptp_bh.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
        except Exception as e:
            logger.info("Problem in creating excel headers. Exception: ", e.message)

        # creating excel rows
        try:
            for i, l in enumerate(ptp_bh_excel_rows):
                i += 1
                for j, col in enumerate(l):
                    ws_ptp_bh.write(i, j, col)
        except Exception as e:
            logger.info("Problem in creating excel rows. Exception: ", e.message)

        # ***************************** PMP BS *******************************
        # pmp bs excel rows
        pmp_bs_excel_rows = []
        for val in pmp_bs_rows:
            temp_list = list()
            for key in pmp_bs_fields:
                try:
                    temp_list.append(val[key])
                except Exception as e:
                    temp_list.append("")
                    logger.info(e.message)
            pmp_bs_excel_rows.append(temp_list)

        # wimax bs sheet (contain by inventory excel workbook i.e inventory_wb)
        ws_pmp_bs = inventory_wb.add_sheet("PMP BS")

        # style for header row in excel
        style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

        # creating excel headers
        try:
            for i, col in enumerate(pmp_bs_fields):
                ws_pmp_bs.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
        except Exception as e:
            logger.info("Problem in creating excel headers. Exception: ", e.message)

        # creating excel rows
        try:
            for i, l in enumerate(pmp_bs_excel_rows):
                i += 1
                for j, col in enumerate(l):
                    ws_pmp_bs.write(i, j, col)
        except Exception as e:
            logger.info("Problem in creating excel rows. Exception: ", e.message)

        # ***************************** PMP SM *******************************
        # pmp sm excel rows
        pmp_sm_excel_rows = []
        for val in pmp_sm_rows:
            temp_list = list()
            for key in pmp_sm_fields:
                try:
                    temp_list.append(val[key])
                except Exception as e:
                    temp_list.append("")
                    logger.info(e.message)
            pmp_sm_excel_rows.append(temp_list)

        # wimax sm sheet (contain by inventory excel workbook i.e inventory_wb)
        ws_pmp_sm = inventory_wb.add_sheet("PMP SM")

        # style for header row in excel
        style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

        # creating excel headers
        try:
            for i, col in enumerate(pmp_sm_fields):
                ws_pmp_sm.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
        except Exception as e:
            logger.info("Problem in creating excel headers. Exception: ", e.message)

        # creating excel rows
        try:
            for i, l in enumerate(pmp_sm_excel_rows):
                i += 1
                for j, col in enumerate(l):
                    ws_pmp_sm.write(i, j, col)
        except Exception as e:
            logger.info("Problem in creating excel rows. Exception: ", e.message)

        # ***************************** Wimax BS *******************************
        # remove duplicate dictionaries from wimax bs list
        wimax_bs_rows = remove_duplicate_dict_from_list(wimax_bs_rows)

        # wimax bs excel rows
        wimax_bs_excel_rows = []
        for val in wimax_bs_rows:
            temp_list = list()
            for key in wimax_bs_fields:
                try:
                    temp_list.append(val[key])
                except Exception as e:
                    temp_list.append("")
                    logger.info(e.message)
            wimax_bs_excel_rows.append(temp_list)

        print "************************ WIMAX BS ROWS - ", wimax_bs_rows

        # wimax bs sheet (contain by inventory excel workbook i.e inventory_wb)
        ws_wimax_bs = inventory_wb.add_sheet("Wimax BS")

        # style for header row in excel
        style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

        # creating excel headers
        try:
            for i, col in enumerate(wimax_bs_fields):
                ws_wimax_bs.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
        except Exception as e:
            logger.info("Problem in creating excel headers. Exception: ", e.message)

        # creating excel rows
        try:
            for i, l in enumerate(wimax_bs_excel_rows):
                i += 1
                for j, col in enumerate(l):
                    ws_wimax_bs.write(i, j, col)
        except Exception as e:
            logger.info("Problem in creating excel rows. Exception: ", e.message)

        # ***************************** Wimax SS *******************************
        # wimax ss excel rows
        wimax_ss_excel_rows = []
        for val in wimax_ss_rows:
            temp_list = list()
            for key in wimax_ss_fields:
                try:
                    temp_list.append(val[key])
                except Exception as e:
                    temp_list.append("")
                    logger.info(e.message)
            wimax_ss_excel_rows.append(temp_list)

        # wimax ss sheet (contain by inventory excel workbook i.e inventory_wb)
        ws_wimax_ss = inventory_wb.add_sheet("Wimax SS")

        # style for header row in excel
        style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

        # creating excel headers
        try:
            for i, col in enumerate(wimax_ss_fields):
                ws_wimax_ss.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
        except Exception as e:
            logger.info("Problem in creating excel headers. Exception: ", e.message)

        # creating excel rows
        try:
            for i, l in enumerate(wimax_ss_excel_rows):
                i += 1
                for j, col in enumerate(l):
                    ws_wimax_ss.write(i, j, col)
        except Exception as e:
            logger.info("Problem in creating excel rows. Exception: ", e.message)

        fname = 'bs_inventory.xls'
        response = HttpResponse(mimetype="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=%s' % fname

        # ***************************** Saving Excel (Start) ******************************
        # saving bulk upload errors excel sheet
        try:
            inventory_wb.save(response)
        except Exception as e:
            logger.info(e.message)
        # ***************************** Saving Excel (End) **********************************

        return response

    def get_selected_ptp_inventory(self, base_station, sector):
        # result dictionary (contains ptp and ptp bh inventory)
        result = dict()

        # base station device name
        bs_device_name = ""
        try:
            bs_device_name = sector.sector_configured_on.device_name
        except Exception as e:
            logger.info("PTP BS Device not exist. Exception: ", e.message)

        # base station machine
        bs_machine_name = ""
        try:
            bs_machine_name = sector.sector_configured_on.machine.name
        except Exception as e:
            logger.info("PTP BS Machine not found.  Exception: ", e.message)

        # ptp rows list
        ptp_rows = list()

        # ptp bh rows list
        ptp_bh_rows = list()

        # circuits associated with current sector
        circuits = sector.circuit_set.all()

        # loop through circuits; if available to get inventory rows
        if circuits:
            for circuit in circuits:
                # sub station
                sub_station = circuit.sub_station

                # sub station device name
                ss_device_name = ""
                try:
                    ss_device_name = sub_station.device.device_name
                except Exception as e:
                    logger.info("PTP SS device not found. Exception: ", e.message)

                # sub station machine
                ss_machine_name = ""
                try:
                    ss_machine_name = sub_station.device.machine.name
                except Exception as e:
                    logger.info("PTP SS machine not found. Exception: ", e.message)

                # backhaul
                backhaul = base_station.backhaul

                # customer
                customer = circuit.customer

                # ptp row dictionary
                ptp_row = dict()

                # state
                try:
                    ptp_row['State'] = State.objects.get(pk=base_station.state).state_name
                except Exception as e:
                    logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

                # city
                try:
                    ptp_row['City'] = City.objects.get(pk=base_station.city).city_name
                except Exception as e:
                    logger.info("City not exist for base station ({}).".format(base_station.name, e.message))

                # circuit id
                try:
                    if circuit.circuit_type == "Customer":
                        ptp_row['Circuit ID'] = circuit.circuit_id
                    elif circuit.circuit_type == "Backhaul":
                        ptp_row['Circuit ID'] = circuit.circuit_id.split("#")[-1]
                    else:
                        pass
                except Exception as e:
                    logger.info("Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

                # circuit type
                try:
                    ptp_row['Circuit Type'] = circuit.circuit_type
                except Exception as e:
                    logger.info("Circuit Type not exist for base station ({}).".format(base_station.name, e.message))

                # customer name
                try:
                    ptp_row['Customer Name'] = customer.alias
                except Exception as e:
                    logger.info("Customer Name not exist for base station ({}).".format(base_station.name, e.message))

                # bs address
                try:
                    ptp_row['BS Address'] = base_station.address
                except Exception as e:
                    logger.info("BS Address not exist for base station ({}).".format(base_station.name, e.message))

                # bs name
                try:
                    ptp_row['BS Name'] = base_station.alias
                except Exception as e:
                    logger.info("BS Name not exist for base station ({}).".format(base_station.name, e.message))

                # qos bandwidth
                try:
                    ptp_row['QOS (BW)'] = circuit.qos_bandwidth
                except Exception as e:
                    logger.info("QOS (BW) not exist for base station ({}).".format(base_station.name, e.message))

                # latitude
                try:
                    ptp_row['Latitude'] = base_station.latitude
                except Exception as e:
                    logger.info("Latitude not exist for base station ({}).".format(base_station.name, e.message))

                # longitude
                try:
                    ptp_row['Longitude'] = base_station.longitude
                except Exception as e:
                    logger.info("Longitude not exist for base station ({}).".format(base_station.name, e.message))

                # antenna height
                try:
                    ptp_row['Antenna Height'] = sector.antenna.height
                except Exception as e:
                    logger.info("Antenna Height not exist for base station ({}).".format(base_station.name, e.message))

                # polarization
                try:
                    ptp_row['Polarization'] = sector.antenna.polarization
                except Exception as e:
                    logger.info("Polarization not exist for base station ({}).".format(base_station.name, e.message))

                # antenna type
                try:
                    ptp_row['Antenna Type'] = sector.antenna.antenna_type
                except Exception as e:
                    logger.info("Antenna Type not exist for base station ({}).".format(base_station.name, e.message))

                # antenna gain
                try:
                    ptp_row['Antenna Gain'] = sector.antenna.gain
                except Exception as e:
                    logger.info("Antenna Gain not exist for base station ({}).".format(base_station.name, e.message))

                # antenna mount type
                try:
                    ptp_row['Antenna Mount Type'] = sector.antenna.mount_type
                except Exception as e:
                    logger.info("Antenna Mount Type not exist for base station ({}).".format(base_station.name,
                                                                                             e.message))

                # ethernet extender
                try:
                    ptp_row['Ethernet Extender'] = sub_station.ethernet_extender
                except Exception as e:
                    logger.info("Ethernet Extender not exist for base station ({}).".format(base_station.name,
                                                                                            e.message))

                # building height
                try:
                    ptp_row['Building Height'] = base_station.building_height
                except Exception as e:
                    logger.info("Building Height not exist for base station ({}).".format(base_station.name, e.message))

                # tower/pole height
                try:
                    ptp_row['Tower/Pole Height'] = base_station.tower_height
                except Exception as e:
                    logger.info("Tower/Pole Height not exist for base station ({}).".format(base_station.name,
                                                                                            e.message))

                # cable length
                try:
                    ptp_row['Cable Length'] = sub_station.cable_length
                except Exception as e:
                    logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

                # rssi during acceptance
                try:
                    ptp_row['RSSI During Acceptance'] = circuit.dl_rssi_during_acceptance
                except Exception as e:
                    logger.info("RSSI During Acceptance not exist for base station ({}).".format(base_station.name,
                                                                                                 e.message))

                # throughput during acceptance
                try:
                    ptp_row['Throughput During Acceptance'] = circuit.throughput_during_acceptance
                except Exception as e:
                    logger.info("Throughput During Acceptance not exist for base station ({}).".format(
                        base_station.name,
                        e.message))

                # date of acceptance
                try:
                    ptp_row['Date Of Acceptance'] = circuit.date_of_acceptance.strftime('%d/%b/%Y')
                except Exception as e:
                    logger.info("Date Of Acceptance not exist for base station ({}).".format(base_station.name,
                                                                                             e.message))

                # bh bso
                try:
                    ptp_row['BH BSO'] = base_station.bh_bso
                except Exception as e:
                    logger.info("BH BSO not exist for base station ({}).".format(base_station.name, e.message))

                # ip
                try:
                    ptp_row['IP'] = sector.sector_configured_on.ip_address
                except Exception as e:
                    logger.info("IP not exist for base station ({}).".format(base_station.name, e.message))

                # mac
                try:
                    ptp_row['MAC'] = sector.sector_configured_on.mac_address
                except Exception as e:
                    logger.info("MAC not exist for base station ({}).".format(base_station.name, e.message))

                # hssu used
                try:
                    ptp_row['HSSU Used'] = base_station.hssu_used
                except Exception as e:
                    logger.info("HSSU Used not exist for base station ({}).".format(base_station.name, e.message))

                # bs switch ip
                try:
                    ptp_row['BS Switch IP'] = base_station.bs_switch.ip_address
                except Exception as e:
                    logger.info("BS Switch IP not exist for base station ({}).".format(base_station.name, e.message))

                # aggregation switch
                try:
                    ptp_row['Aggregation Switch'] = backhaul.aggregator.ip_address
                except Exception as e:
                    logger.info("Aggregation Switch not exist for base station ({}).".format(base_station.name,
                                                                                             e.message))

                # aggregation swith port
                try:
                    ptp_row['Aggregation Switch Port'] = backhaul.aggregator_port_name
                except Exception as e:
                    logger.info("Aggregation Switch Port not exist for base station ({}).".format(base_station.name,
                                                                                                  e.message))

                # bs conveter ip
                try:
                    ptp_row['BS Converter IP'] = backhaul.bh_switch.ip_address
                except Exception as e:
                    logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

                # pop converter ip
                try:
                    ptp_row['POP Converter IP'] = backhaul.pop.ip_address
                except Exception as e:
                    logger.info("POP Converter IP not exist for base station ({}).".format(base_station.name,
                                                                                           e.message))

                # converter type
                try:
                    ptp_row['Converter Type'] = DeviceType.objects.get(pk=backhaul.bh_switch.device_type).alias
                except Exception as e:
                    logger.info("Converter Type not exist for base station ({}).".format(base_station.name, e.message))

                # bh configured switch or converter
                try:
                    ptp_row['BH Configured On Switch/Converter'] = backhaul.bh_configured_on.ip_address
                except Exception as e:
                    logger.info("BH Configured On Switch/Converter not exist for base station ({}).".format(
                        base_station.name,
                        e.message))

                # bh configured switch or converter port
                try:
                    ptp_row['Switch/Converter Port'] = backhaul.bh_port_name
                except Exception as e:
                    logger.info("Switch/Converter Port not exist for base station ({}).".format(base_station.name,
                                                                                                e.message))

                # bh capacity
                try:
                    ptp_row['BH Capacity'] = backhaul.bh_capacity
                except Exception as e:
                    logger.info("BH Capacity not exist for base station ({}).".format(base_station.name, e.message))

                # bh offnet/onnet
                try:
                    ptp_row['BH Offnet/Onnet'] = backhaul.bh_connectivity
                except Exception as e:
                    logger.info("BH Offnet/Onnet not exist for base station ({}).".format(base_station.name, e.message))

                # backhaul type
                try:
                    ptp_row['Backhaul Type'] = backhaul.bh_type
                except Exception as e:
                    logger.info("Backhaul Type not exist for base station ({}).".format(base_station.name, e.message))

                # bh circuit id
                try:
                    ptp_row['BH Circuit ID'] = backhaul.bh_circuit_id
                except Exception as e:
                    logger.info("BH Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

                # pe hostname
                try:
                    ptp_row['PE Hostname'] = backhaul.pe_hostname
                except Exception as e:
                    logger.info("PE Hostname not exist for base station ({}).".format(base_station.name, e.message))

                # pe ip
                try:
                    ptp_row['PE IP'] = backhaul.pe_ip
                except Exception as e:
                    logger.info("PE IP not exist for base station ({}).".format(base_station.name, e.message))

                # bso circuit id
                try:
                    ptp_row['BSO Circuit ID'] = backhaul.ttsl_circuit_id
                except Exception as e:
                    logger.info("BSO Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

                # ********************************* PTP BS Perf Info *************************************
                # bs product type
                try:
                    ptp_row['BS Product Type'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                                data_source='producttype').using(
                                                                                alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Product Type not exist for base station ({}).".format(base_station.name, e.message))

                # bs frequency
                try:
                    ptp_row['BS Frequency'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                             data_source='frequency').using(
                                                                             alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Frequency not exist for base station ({}).".format(base_station.name, e.message))

                # bs uas
                try:
                    ptp_row['BS UAS'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                     data_source='uas').using(
                                                                     alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS UAS not exist for base station ({}).".format(base_station.name, e.message))

                # bs rssi
                try:
                    ptp_row['BS RSSI'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                      data_source='rssi').using(
                                                                      alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS RSSI not exist for base station ({}).".format(base_station.name, e.message))

                # bs estimated throughput
                try:
                    ptp_row['BS Estimated Throughput'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                        service_name='radwin_service_throughput',
                                                                        data_source='service_throughput').using(
                                                                        alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Estimated Throughput not exist for base station ({}).".format(base_station.name,
                                                                                                  e.message))

                # bs utilization dl
                try:
                    ptp_row['BS Utilisation DL'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                        service_name='radwin_dl_utilization',
                                                                        data_source='Management_Port_on_Odu').using(
                                                                        alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Utilisation DL not exist for base station ({}).".format(base_station.name,
                                                                                            e.message))

                # bs utilization ul
                try:
                    ptp_row['BS Utilisation UL'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                        service_name='radwin_ul_utilization',
                                                                        data_source='Management_Port_on_Odu').using(
                                                                        alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Utilisation UL not exist for base station ({}).".format(base_station.name,
                                                                                            e.message))

                # bs uptime
                try:
                    ptp_row['BS Uptime'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                        service_name='radwin_uptime',
                                                                        data_source='uptime').using(
                                                                        alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Uptime not exist for base station ({}).".format(base_station.name, e.message))

                # bs link distance
                try:
                    ptp_row['BS Link Distance'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                                 data_source='link_distance').using(
                                                                                 alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Link Distance not exist for base station ({}).".format(base_station.name,
                                                                                           e.message))

                # bs cbw
                try:
                    ptp_row['BS CBW'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                       data_source='cbw').using(
                                                                       alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS CBW not exist for base station ({}).".format(base_station.name, e.message))

                # bs latency
                try:
                    ptp_row['BS Latency'] = NetworkStatus.objects.filter(device_name=bs_device_name,
                                                                         data_source='rta').using(
                                                                         alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Latency not exist for base station ({}).".format(base_station.name, e.message))

                # bs pl/pd (packet loss/drop)
                try:
                    ptp_row['BS PD'] = NetworkStatus.objects.filter(device_name=bs_device_name,
                                                                    data_source='pl').using(
                                                                    alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS PD not exist for base station ({}).".format(base_station.name, e.message))

                # bs auto negotiation
                try:
                    ptp_row['BS Auto Negotiation'] = Status.objects.filter(device_name=bs_device_name,
                                                                           service_name='radwin_autonegotiation_status',
                                                                           data_source='1').using(
                                                                           alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Auto Negotiation not exist for base station ({}).".format(base_station.name,
                                                                                              e.message))

                # bs duplex
                try:
                    ptp_row['BS Duplex'] = Status.objects.filter(device_name=bs_device_name,
                                                                 service_name='radwin_port_mode_status',
                                                                 data_source='1').using(
                                                                 alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Duplex not exist for base station ({}).".format(base_station.name, e.message))

                # bs speed
                try:
                    ptp_row['BS Speed'] = Status.objects.filter(device_name=bs_device_name,
                                                                service_name='radwin_port_speed_status',
                                                                data_source='1').using(
                                                                alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Speed not exist for base station ({}).".format(base_station.name, e.message))

                # bs link
                try:
                    ptp_row['BS Link'] = Status.objects.filter(device_name=bs_device_name,
                                                               service_name='radwin_link_ethernet_status',
                                                               data_source='Management_Port_on_Odu').using(
                                                               alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Link not exist for base station ({}).".format(base_station.name, e.message))

                # ********************************** PTP Far End (SS) ************************************

                # ss city
                try:
                    ptp_row['SS City'] = City.objects.get(pk=sub_station.city).city_name
                except Exception as e:
                    logger.info("SS City not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss state
                try:
                    ptp_row['SS State'] = State.objects.get(pk=sub_station.state).state_name
                except Exception as e:
                    logger.info("SS State not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss circuit id
                try:
                    if circuit.circuit_type == "Customer":
                        ptp_row['SS Circuit ID'] = circuit.circuit_id
                    elif circuit.circuit_type == "Backhaul":
                        ptp_row['SS Circuit ID'] = circuit.circuit_id.split("#")[0]
                    else:
                        pass
                except Exception as e:
                    logger.info("SS Circuit ID not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss customer name
                try:
                    ptp_row['SS Customer Name'] = customer.alias
                except Exception as e:
                    logger.info("SS Customer Name not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss customer address
                try:
                    ptp_row['SS Customer Address'] = customer.address
                except Exception as e:
                    logger.info("SS Customer Address not exist for sub station ({}).".format(sub_station.name,
                                                                                             e.message))

                # ss bs name
                try:
                    ptp_row['SS BS Name'] = base_station.alias
                except Exception as e:
                    logger.info("SS BS Name not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss qos bandwidth
                try:
                    ptp_row['SS QOS (BW)'] = circuit.qos_bandwidth
                except Exception as e:
                    logger.info("SS QOS (BW) not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss latitude
                try:
                    ptp_row['SS Latitude'] = sub_station.latitude
                except Exception as e:
                    logger.info("SS Latitude not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss longitude
                try:
                    ptp_row['SS Longitude'] = sub_station.longitude
                except Exception as e:
                    logger.info("SS Longitude not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss antenna height
                try:
                    ptp_row['SS Antenna Height'] = sub_station.antenna.height
                except Exception as e:
                    logger.info("SS Antenna Height not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss antenna type
                try:
                    ptp_row['SS Antenna Type'] = sub_station.antenna.antenna_type
                except Exception as e:
                    logger.info("SS Antenna Type not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss antenna gain
                try:
                    ptp_row['SS Antenna Gain'] = sub_station.antenna.gain
                except Exception as e:
                    logger.info("SS Antenna Gain not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss antenna mount type
                try:
                    ptp_row['SS Antenna Mount Type'] = sub_station.antenna.mount_type
                except Exception as e:
                    logger.info("SS Antenna Mount Type not exist for sub station ({}).".format(sub_station.name,
                                                                                               e.message))

                # ss ethernet extender
                try:
                    ptp_row['SS Ethernet Extender'] = sub_station.ethernet_extender
                except Exception as e:
                    logger.info("SS Ethernet Extender not exist for sub station ({}).".format(sub_station.name,
                                                                                              e.message))

                # ss building height
                try:
                    ptp_row['SS Building Height'] = sub_station.building_height
                except Exception as e:
                    logger.info("SS Building Height not exist for sub station ({}).".format(sub_station.name,
                                                                                            e.message))

                # ss tower or pole height
                try:
                    ptp_row['SS Tower/Pole Height'] = sub_station.tower_height
                except Exception as e:
                    logger.info("SS Tower/Pole Height not exist for sub station ({}).".format(sub_station.name,
                                                                                              e.message))

                # ss cable length
                try:
                    ptp_row['SS Cable Length'] = sub_station.cable_length
                except Exception as e:
                    logger.info("SS Cable Length not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss rssi during acceptance
                try:
                    ptp_row['SS RSSI During Acceptance'] = circuit.dl_rssi_during_acceptance
                except Exception as e:
                    logger.info("SS RSSI During Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                                   e.message))

                # ss throughput during acceptance
                try:
                    ptp_row['SS Throughput During Acceptance'] = circuit.throughput_during_acceptance
                except Exception as e:
                    logger.info("SS Throughput During Acceptance not exist for sub station ({}).".format(
                        sub_station.name,
                        e.message))

                # ss date of acceptance
                try:
                    ptp_row['SS Date Of Acceptance'] = circuit.date_of_acceptance.strftime('%d/%b/%Y')
                except Exception as e:
                    logger.info("SS Date Of Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                               e.message))

                # ss bh bso
                try:
                    ptp_row['SS BH BSO'] = base_station.bh_bso
                except Exception as e:
                    logger.info("SS BH BSO not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss ip
                try:
                    ptp_row['SS IP'] = sub_station.device.ip_address
                except Exception as e:
                    logger.info("SS IP not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss mac
                try:
                    ptp_row['SS MAC'] = sub_station.device.mac_address
                except Exception as e:
                    logger.info("SS MAC not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss polarization
                try:
                    ptp_row['SS Polarization'] = sub_station.antenna.polarization
                except Exception as e:
                    logger.info("SS Polarization not exist for sub station ({}).".format(sub_station.name, e.message))

                # ********************************* PTP SS Perf Info *************************************
                # ss product type
                try:
                    ptp_row['SS Product Type'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='producttype').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Product Type not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss frequency
                try:
                    ptp_row['SS Frequency'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                             data_source='frequency').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Frequency not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss uas
                try:
                    ptp_row['SS UAS'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                     data_source='uas').using(
                                                                     alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS UAS not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss rssi
                try:
                    ptp_row['SS RSSI'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                      data_source='rssi').using(
                                                                      alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS RSSI not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss estimated throughput
                try:
                    ptp_row['SS Estimated Throughput'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                        service_name='radwin_service_throughput',
                                                                        data_source='service_throughput').using(
                                                                        alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Estimated Throughput not exist for sub station ({}).".format(sub_station.name,
                                                                                                 e.message))

                # ss utilization dl
                try:
                    ptp_row['SS Utilisation DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                        service_name='radwin_dl_utilization',
                                                                        data_source='Management_Port_on_Odu').using(
                                                                        alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Utilisation DL not exist for sub station ({}).".format(sub_station.name,
                                                                                           e.message))

                # ss utilization ul
                try:
                    ptp_row['SS Utilisation UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                        service_name='radwin_ul_utilization',
                                                                        data_source='Management_Port_on_Odu').using(
                                                                        alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Utilisation UL not exist for sub station ({}).".format(sub_station.name,
                                                                                           e.message))

                # ss uptime
                try:
                    ptp_row['SS Uptime'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                        service_name='radwin_uptime',
                                                                        data_source='uptime').using(
                                                                        alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Uptime not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss link distance
                try:
                    ptp_row['SS Link Distance'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                 data_source='link_distance').using(
                                                                                 alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Link Distance not exist for sub station ({}).".format(sub_station.name,
                                                                                          e.message))

                # ss cbw
                try:
                    ptp_row['SS CBW'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                       data_source='cbw').using(
                                                                       alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS CBW not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss latency
                try:
                    ptp_row['SS Latency'] = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                                         data_source='rta').using(
                                                                         alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Latency not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss pl/pd (packet loss/drop)
                try:
                    ptp_row['SS PD'] = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                                    data_source='pl').using(
                                                                    alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS PD not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss auto negotiation
                try:
                    ptp_row['SS Auto Negotiation'] = Status.objects.filter(device_name=ss_device_name,
                                                                           service_name='radwin_autonegotiation_status',
                                                                           data_source='1').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Auto Negotiation not exist for sub station ({}).".format(sub_station.name,
                                                                                             e.message))

                # ss duplex
                try:
                    ptp_row['SS Duplex'] = Status.objects.filter(device_name=ss_device_name,
                                                                 service_name='radwin_port_mode_status',
                                                                 data_source='1').using(
                                                                 alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Duplex not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss speed
                try:
                    ptp_row['SS Speed'] = Status.objects.filter(device_name=ss_device_name,
                                                                service_name='radwin_port_speed_status',
                                                                data_source='1').using(
                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Speed not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss link
                try:
                    ptp_row['SS Link'] = Status.objects.filter(device_name=ss_device_name,
                                                               service_name='radwin_link_ethernet_status',
                                                               data_source='Management_Port_on_Odu').using(
                                                               alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Link not exist for sub station ({}).".format(sub_station.name, e.message))

                # filter 'ptp' and 'ptp bh' rows
                if circuit.circuit_type == "Customer":
                    ptp_rows.append(ptp_row)
                elif circuit.circuit_type == "Backhaul":
                    ptp_bh_rows.append(ptp_row)
                else:
                    pass

        # insert 'ptp' rows in result dictionary
        result['ptp'] = ptp_rows if ptp_rows else ""

        # insert 'ptp bh' rows in result dictionary
        result['ptp_bh'] = ptp_bh_rows if ptp_bh_rows else ""

        print "****************************** ptp (result) - ", result
        return result

    def get_selected_pmp_inventory(self, base_station, sector):
        # result dictionary (contains ptp and ptp bh inventory)
        result = dict()

        # base station device name
        bs_device_name = ""
        try:
            bs_device_name = sector.sector_configured_on.device_name
        except Exception as e:
            logger.info("PMP BS Device not exist. Exception: ", e.message)

        # base station machine
        bs_machine_name = ""
        try:
            bs_machine_name = sector.sector_configured_on.machine.name
        except Exception as e:
            logger.info("PMP BS Machine not found.  Exception: ", e.message)

        # pmp bs rows list
        pmp_bs_rows = list()

        # pmp sm rows list
        pmp_sm_rows = list()

        # circuits associated with current sector
        circuits = sector.circuit_set.all()

        # loop through circuits; if available to get inventory rows
        if circuits:
            for circuit in circuits:
                # sub station
                sub_station = circuit.sub_station

                # sub station device name
                ss_device_name = ""
                try:
                    ss_device_name = sub_station.device.device_name
                except Exception as e:
                    logger.info("PMP SS device not found. Exception: ", e.message)

                # sub station machine
                ss_machine_name = ""
                try:
                    ss_machine_name = sub_station.device.machine.name
                except Exception as e:
                    logger.info("PMP SS machine not found. Exception: ", e.message)

                # backhaul
                backhaul = base_station.backhaul

                # customer
                customer = circuit.customer

                # ptp row dictionary
                pmp_bs_row = dict()

                # ptp row dictionary
                pmp_sm_row = dict()

                # *********************************** Near End (PMP BS) *********************************

                # state
                try:
                    pmp_bs_row['State'] = State.objects.get(pk=base_station.state).state_name
                except Exception as e:
                    logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

                # city
                try:
                    pmp_bs_row['City'] = City.objects.get(pk=base_station.city).city_name
                except Exception as e:
                    logger.info("City not exist for base station ({}).".format(base_station.name, e.message))

                # address
                try:
                    pmp_bs_row['Address'] = base_station.address
                except Exception as e:
                    logger.info("Address not exist for base station ({}).".format(base_station.name, e.message))

                # bs name
                try:
                    pmp_bs_row['BS Name'] = base_station.alias
                except Exception as e:
                    logger.info("BS Name not exist for base station ({}).".format(base_station.name, e.message))

                # type of bs (technology)
                try:
                    pmp_bs_row['Type Of BS (Technology)'] = base_station.bs_type
                except Exception as e:
                    logger.info("Type Of BS (Technology) not exist for base station ({}).".format(base_station.name,
                                                                                                  e.message))

                # site type
                try:
                    pmp_bs_row['Site Type'] = base_station.bs_site_type
                except Exception as e:
                    logger.info("Site Type not exist for base station ({}).".format(base_station.name, e.message))

                # infra provider
                try:
                    pmp_bs_row['Infra Provider'] = base_station.infra_provider
                except Exception as e:
                    logger.info("Infra Provider not exist for base station ({}).".format(base_station.name, e.message))

                # building height
                try:
                    pmp_bs_row['Building Height'] = base_station.building_height
                except Exception as e:
                    logger.info("Building Height not exist for base station ({}).".format(base_station.name, e.message))

                # tower height
                try:
                    pmp_bs_row['Tower Height'] = base_station.tower_height
                except Exception as e:
                    logger.info("Tower Height not exist for base station ({}).".format(base_station.name, e.message))

                # latitude
                try:
                    pmp_bs_row['Latitude'] = base_station.latitude
                except Exception as e:
                    logger.info("Latitude not exist for base station ({}).".format(base_station.name, e.message))

                # longitude
                try:
                    pmp_bs_row['Longitude'] = base_station.longitude
                except Exception as e:
                    logger.info("Longitude not exist for base station ({}).".format(base_station.name, e.message))

                # odu ip
                try:
                    pmp_bs_row['ODU IP'] = sector.sector_configured_on.ip_address
                except Exception as e:
                    logger.info("ODU IP not exist for base station ({}).".format(base_station.name, e.message))

                # sector name
                try:
                    pmp_bs_row['Sector Name'] = sector.name.split("_")[-1]
                except Exception as e:
                    logger.info("Sector Name not exist for base station ({}).".format(base_station.name, e.message))

                # make of antenna
                try:
                    pmp_bs_row['Make Of Antenna'] = sector.antenna.make_of_antenna
                except Exception as e:
                    logger.info("Make Of Antenna not exist for base station ({}).".format(base_station.name,
                                                                                          e.message))

                # polarization
                try:
                    pmp_bs_row['Polarization'] = sector.antenna.polarization
                except Exception as e:
                    logger.info("Polarization not exist for base station ({}).".format(base_station.name, e.message))

                # antenna tilt
                try:
                    pmp_bs_row['Antenna Tilt'] = sector.antenna.tilt
                except Exception as e:
                    logger.info("Antenna Tilt not exist for base station ({}).".format(base_station.name, e.message))

                # antenna height
                try:
                    pmp_bs_row['Antenna Height'] = sector.antenna.height
                except Exception as e:
                    logger.info("Antenna Height not exist for base station ({}).".format(base_station.name, e.message))

                # antenna beamwidth
                try:
                    pmp_bs_row['Antenna Beamwidth'] = sector.antenna.beam_width
                except Exception as e:
                    logger.info("Antenna Beamwidth not exist for base station ({}).".format(base_station.name,
                                                                                            e.message))

                # azimuth
                try:
                    pmp_bs_row['Azimuth'] = sector.antenna.azimuth_angle
                except Exception as e:
                    logger.info("Azimuth not exist for base station ({}).".format(base_station.name, e.message))

                # sync splitter used
                try:
                    pmp_bs_row['Sync Splitter Used'] = sector.antenna.sync_splitter_used
                except Exception as e:
                    logger.info("Sync Splitter Used not exist for base station ({}).".format(base_station.name,
                                                                                             e.message))

                # type of gps
                try:
                    pmp_bs_row['Type Of GPS'] = base_station.gps_type
                except Exception as e:
                    logger.info("Type Of GPS not exist for base station ({}).".format(base_station.name, e.message))

                # bs switch ip
                try:
                    pmp_bs_row['BS Switch IP'] = base_station.bs_switch.ip_address
                except Exception as e:
                    logger.info("BS Switch IP not exist for base station ({}).".format(base_station.name, e.message))

                # aggregation switch
                try:
                    pmp_bs_row['Aggregation Switch'] = backhaul.aggregator.ip_address
                except Exception as e:
                    logger.info("Aggregation Switch not exist for base station ({}).".format(base_station.name,
                                                                                             e.message))

                # aggregation swith port
                try:
                    pmp_bs_row['Aggregation Switch Port'] = backhaul.aggregator_port_name
                except Exception as e:
                    logger.info("Aggregation Switch Port not exist for base station ({}).".format(base_station.name,
                                                                                                  e.message))

                # bs conveter ip
                try:
                    pmp_bs_row['BS Converter IP'] = backhaul.bh_switch.ip_address
                except Exception as e:
                    logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

                # pop converter ip
                try:
                    pmp_bs_row['POP Converter IP'] = backhaul.pop.ip_address
                except Exception as e:
                    logger.info("POP Converter IP not exist for base station ({}).".format(base_station.name,
                                                                                           e.message))

                # converter type
                try:
                    pmp_bs_row['Converter Type'] = DeviceType.objects.get(pk=backhaul.bh_switch.device_type).alias
                except Exception as e:
                    logger.info("Converter Type not exist for base station ({}).".format(base_station.name, e.message))

                # bh configured switch or converter
                try:
                    pmp_bs_row['BH Configured On Switch/Converter'] = backhaul.bh_configured_on.ip_address
                except Exception as e:
                    logger.info("BH Configured On Switch/Converter not exist for base station ({}).".format(
                        base_station.name,
                        e.message))

                # bh configured switch or converter port
                try:
                    pmp_bs_row['Switch/Converter Port'] = backhaul.bh_port_name
                except Exception as e:
                    logger.info("Switch/Converter Port not exist for base station ({}).".format(base_station.name,
                                                                                                e.message))

                # bh capacity
                try:
                    pmp_bs_row['BH Capacity'] = backhaul.bh_capacity
                except Exception as e:
                    logger.info("BH Capacity not exist for base station ({}).".format(base_station.name, e.message))

                # bh offnet/onnet
                try:
                    pmp_bs_row['BH Offnet/Onnet'] = backhaul.bh_connectivity
                except Exception as e:
                    logger.info("BH Offnet/Onnet not exist for base station ({}).".format(base_station.name, e.message))

                # backhaul type
                try:
                    pmp_bs_row['Backhaul Type'] = backhaul.bh_type
                except Exception as e:
                    logger.info("Backhaul Type not exist for base station ({}).".format(base_station.name, e.message))

                # bh circuit id
                try:
                    pmp_bs_row['BH Circuit ID'] = backhaul.bh_circuit_id
                except Exception as e:
                    logger.info("BH Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

                # pe hostname
                try:
                    pmp_bs_row['PE Hostname'] = backhaul.pe_hostname
                except Exception as e:
                    logger.info("PE Hostname not exist for base station ({}).".format(base_station.name, e.message))

                # pe ip
                try:
                    pmp_bs_row['PE IP'] = backhaul.pe_ip
                except Exception as e:
                    logger.info("PE IP not exist for base station ({}).".format(base_station.name, e.message))

                # bso circuit id
                try:
                    pmp_bs_row['BSO Circuit ID'] = backhaul.ttsl_circuit_id
                except Exception as e:
                    logger.info("BSO Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

                # dr site
                try:
                    pmp_bs_row['DR Site'] = sector.dr_site
                except Exception as e:
                    logger.info("DR Site not exist for base station ({}).".format(base_station.name, e.message))

                # sector id
                try:
                    pmp_bs_row['Sector ID'] = sector.sector_id
                except Exception as e:
                    logger.info("Sector ID not exist for base station ({}).".format(base_station.name, e.message))

                # ************************************* BS Perf Parameters **********************************
                # frequency
                try:
                    pmp_bs_row['Frequency'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                             data_source='frequency').using(
                                                                             alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Frequency not exist for base station ({}).".format(base_station.name, e.message))

                # cell radius
                try:
                    pmp_bs_row['Cell Radius'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                               data_source='cell_radius').using(
                                                                               alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Cell Radius not exist for base station ({}).".format(base_station.name, e.message))

                # dl utilization
                try:
                    pmp_bs_row['Utilization DL'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                                data_source='dl_utilization').using(
                                                                                alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Utilization DL not exist for base station ({}).".format(base_station.name, e.message))

                # ul utilization
                try:
                    pmp_bs_row['Utilization UL'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                                data_source='ul_utilization').using(
                                                                                alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Utilization UL not exist for base station ({}).".format(base_station.name, e.message))

                # uptime
                try:
                    pmp_bs_row['Sector Uptime'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                               data_source='uptime').using(
                                                                               alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Sector Uptime not exist for base station ({}).".format(base_station.name, e.message))

                # transmit power
                try:
                    pmp_bs_row['TX Power'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                            data_source='transmit_power').using(
                                                                            alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("TX Power not exist for base station ({}).".format(base_station.name, e.message))

                # frequency
                try:
                    pmp_bs_row['RX Power'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                            data_source='commanded_rx_power').using(
                                                                            alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("RX Power not exist for base station ({}).".format(base_station.name, e.message))

                # ********************************** Far End (PMP SM) ********************************

                # customer name
                try:
                    pmp_sm_row['Customer Name'] = customer.alias
                except Exception as e:
                    logger.info("Customer Name not exist for base station ({}).".format(sub_station.name, e.message))

                # circuit id
                try:
                    pmp_sm_row['Circuit ID'] = circuit.circuit_id
                except Exception as e:
                    logger.info("Circuit ID not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss ip
                try:
                    pmp_sm_row['SS IP'] = sub_station.device.ip_address
                except Exception as e:
                    logger.info("SS IP not exist for sub station ({}).".format(sub_station.name, e.message))

                # qos bandwidth
                try:
                    pmp_sm_row['QOS (BW)'] = circuit.qos_bandwidth
                except Exception as e:
                    logger.info("QOS (BW) not exist for sub station ({}).".format(sub_station.name, e.message))

                # latitude
                try:
                    pmp_sm_row['Latitude'] = sub_station.latitude
                except Exception as e:
                    logger.info("Latitude not exist for sub station ({}).".format(sub_station.name, e.message))

                # longitude
                try:
                    pmp_sm_row['Longitude'] = sub_station.longitude
                except Exception as e:
                    logger.info("Longitude not exist for sub station ({}).".format(sub_station.name, e.message))

                # mac address
                try:
                    pmp_sm_row['MAC'] = State.objects.get(pk=base_station.state).state_name
                except Exception as e:
                    logger.info("MAC not exist for sub station ({}).".format(sub_station.name, e.message))

                # building height
                try:
                    pmp_sm_row['Building Height'] = sub_station.building_height
                except Exception as e:
                    logger.info("Building Height not exist for sub station ({}).".format(sub_station.name, e.message))

                # tower/pole height
                try:
                    pmp_sm_row['Tower/Pole Height'] = sub_station.tower_height
                except Exception as e:
                    logger.info("Tower/Pole Height not exist for sub station ({}).".format(sub_station.name, e.message))

                # antenna height
                try:
                    pmp_sm_row['Antenna Height'] = sub_station.antenna.height
                except Exception as e:
                    logger.info("Antenna Height not exist for sub station ({}).".format(sub_station.name, e.message))

                # antenna beamwidth
                try:
                    pmp_sm_row['Antenna Beamwidth'] = sub_station.antenna.beam_width
                except Exception as e:
                    logger.info("Antenna Beamwidth not exist for sub station ({}).".format(sub_station.name, e.message))

                # polarization
                try:
                    pmp_sm_row['Polarization'] = sub_station.antenna.polarization
                except Exception as e:
                    logger.info("Polarization not exist for sub station ({}).".format(sub_station.name, e.message))

                # antenna type
                try:
                    pmp_sm_row['Antenna Type'] = sub_station.antenna.antenna_type
                except Exception as e:
                    logger.info("Antenna Type not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss mount type
                try:
                    pmp_sm_row['SS Mount Type'] = sub_station.antenna.mount_type
                except Exception as e:
                    logger.info("SS Mount Type not exist for sub station ({}).".format(sub_station.name, e.message))

                # ethernet extender
                try:
                    pmp_sm_row['Ethernet Extender'] = sub_station.ethernet_extender
                except Exception as e:
                    logger.info("Ethernet Extender not exist for sub station ({}).".format(sub_station.name, e.message))

                # cable length
                try:
                    pmp_sm_row['Cable Length'] = sub_station.cable_length
                except Exception as e:
                    logger.info("Cable Length not exist for sub station ({}).".format(sub_station.name, e.message))

                # rssi during acceptance
                try:
                    pmp_sm_row['RSSI During Acceptance'] = circuit.dl_rssi_during_acceptance
                except Exception as e:
                    logger.info("RSSI During Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                                e.message))

                # cinr during acceptance
                try:
                    pmp_sm_row['CINR During Acceptance'] = circuit.dl_cinr_during_acceptance
                except Exception as e:
                    logger.info("CINR During Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                                e.message))

                # Customer Address
                try:
                    pmp_sm_row['Customer Address'] = customer.address
                except Exception as e:
                    logger.info("Customer Address not exist for sub station ({}).".format(sub_station.name, e.message))

                # date of acceptance
                try:
                    pmp_sm_row['Date Of Acceptance'] = circuit.date_of_acceptance.strftime('%d/%b/%Y')
                except Exception as e:
                    logger.info("Date Of Acceptance not exist for base station ({}).".format(base_station.name,
                                                                                             e.message))

                # ************************************* SS Perf Parameters **********************************
                # frequency
                try:
                    pmp_sm_row['Frequency'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                             data_source='frequency').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Frequency not exist for sub station ({}).".format(sub_station.name, e.message))

                # dl rssi
                try:
                    pmp_sm_row['RSSI DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                         data_source='dl_rssi').using(
                                                                         alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("RSSI DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # ul rssi
                try:
                    pmp_sm_row['RSSI UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                         data_source='ul_rssi').using(
                                                                         alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("RSSI UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # dl jitter
                try:
                    pmp_sm_row['Jitter DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='dl_jitter').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Jitter DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # ul jitter
                try:
                    pmp_sm_row['Jitter UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='ul_jitter').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Jitter UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # transmit power
                try:
                    pmp_sm_row['Transmit Power'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                  data_source='transmit_power').using(
                                                                                  alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Transmit Power not exist for sub station ({}).".format(sub_station.name, e.message))

                # polles ss ip
                try:
                    pmp_sm_row['Polled SS IP'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='ss_ip').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled SS IP not exist for sub station ({}).".format(sub_station.name, e.message))

                # polled ss mac
                try:
                    pmp_sm_row['Polled SS MAC'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                 data_source='ss_mac').using(
                                                                                 alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled SS MAC not exist for sub station ({}).".format(sub_station.name, e.message))

                # polled bs ip
                try:
                    pmp_sm_row['Polled BS IP'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='bs_ip').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled BS IP not exist for sub station ({}).".format(sub_station.name, e.message))

                # polles bs mac
                try:
                    pmp_sm_row['Polled BS MAC'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                             data_source='ss_connected_bs_mac').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled BS MAC not exist for sub station ({}).".format(sub_station.name, e.message))

                # uptime
                try:
                    pmp_sm_row['Session Uptime'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='uptime').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Session Uptime not exist for sub station ({}).".format(sub_station.name, e.message))

                # latency
                try:
                    pmp_sm_row['Latency'] = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                                         data_source='rta').using(
                                                                         alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Latency not exist for sub station ({}).".format(sub_station.name, e.message))

                # pl
                try:
                    pmp_sm_row['PD'] = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                                    data_source='pl').using(
                                                                    alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("PD not exist for sub station ({}).".format(sub_station.name, e.message))

                # dl utilization
                try:
                    pmp_sm_row['Utilization DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='dl_utilization').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Utilization DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # ul utilization
                try:
                    pmp_sm_row['Utilization UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='ul_utilization').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Utilization UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # auto negotiation
                try:
                    pmp_sm_row['Auto Negotiation'] = Status.objects.filter(device_name=ss_device_name,
                                                                           data_source='autonegotiation').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Auto Negotiation not exist for sub station ({}).".format(sub_station.name, e.message))

                # duplex
                try:
                    pmp_sm_row['Duplex'] = Status.objects.filter(device_name=ss_device_name,
                                                                 data_source='duplex').using(
                                                                 alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Duplex not exist for sub station ({}).".format(sub_station.name, e.message))

                # speed
                try:
                    pmp_sm_row['Speed'] = Status.objects.filter(device_name=ss_device_name,
                                                                data_source='ss_speed').using(
                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Speed not exist for sub station ({}).".format(sub_station.name, e.message))

                # link state
                try:
                    pmp_sm_row['Link'] = Status.objects.filter(device_name=ss_device_name,
                                                               data_source='link_state').using(
                                                               alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Link not exist for sub station ({}).".format(sub_station.name, e.message))

                # append 'pmp_bs_row' dictionary in 'pmp_bs_rows'
                pmp_bs_rows.append(pmp_bs_row)

                # append 'pmp_sm_row' dictionary in 'pmp_sm_rows'
                pmp_sm_rows.append(pmp_sm_row)

        # insert 'pmp bs' rows in result dictionary
        result['pmp_bs'] = pmp_bs_rows if pmp_bs_rows else ""

        # insert 'pmp sm' rows in result dictionary
        result['pmp_sm'] = pmp_sm_rows if pmp_sm_rows else ""

        print "****************************** pmp (result) - ", result

        return result

    def get_selected_wimax_inventory(self, base_station, sector):
        # result dictionary (contains ptp and ptp bh inventory)
        result = dict()

        # base station device name
        bs_device_name = ""
        try:
            bs_device_name = sector.sector_configured_on.device_name
        except Exception as e:
            logger.info("BS Device not exist. Exception: ", e.message)

        # base station machine
        bs_machine_name = ""
        try:
            bs_machine_name = sector.sector_configured_on.machine.name
        except Exception as e:
            logger.info("BS Machine not found.  Exception: ", e.message)

        # wimax bs rows list
        wimax_bs_rows = list()

        # wimax ss rows list
        wimax_ss_rows = list()

        # circuits associated with current sector
        circuits = sector.circuit_set.all()

        # loop through circuits; if available to get inventory rows
        if circuits:
            for circuit in circuits:
                # sub station
                sub_station = circuit.sub_station

                # sub station device name
                ss_device_name = ""
                try:
                    ss_device_name = sub_station.device.device_name
                except Exception as e:
                    logger.info("WiMAX SS device not found. Exception: ", e.message)

                # sub station machine
                ss_machine_name = ""
                try:
                    ss_machine_name = sub_station.device.machine.name
                except Exception as e:
                    logger.info("WiMAX SS machine not found. Exception: ", e.message)

                # backhaul
                backhaul = base_station.backhaul

                # customer
                customer = circuit.customer

                # ptp row dictionary
                wimax_bs_row = dict()

                # ptp row dictionary
                wimax_ss_row = dict()

                # *********************************** Near End (Wimax BS) *********************************
                # state
                try:
                    wimax_bs_row['State'] = State.objects.get(pk=base_station.state).state_name
                except Exception as e:
                    logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

                # city
                try:
                    wimax_bs_row['City'] = City.objects.get(pk=base_station.city).city_name
                except Exception as e:
                    logger.info("City not exist for base station ({}).".format(base_station.name, e.message))

                # address
                try:
                    wimax_bs_row['Address'] = base_station.address
                except Exception as e:
                    logger.info("Address not exist for base station ({}).".format(base_station.name, e.message))

                # bs name
                try:
                    wimax_bs_row['BS Name'] = base_station.alias
                except Exception as e:
                    logger.info("BS Name not exist for base station ({}).".format(base_station.name, e.message))

                # type of bs (technology)
                try:
                    wimax_bs_row['Type Of BS (Technology)'] = base_station.bs_type
                except Exception as e:
                    logger.info("Type Of BS (Technology) not exist for base station ({}).".format(base_station.name,
                                                                                                  e.message))

                # site type
                try:
                    wimax_bs_row['Site Type'] = base_station.bs_site_type
                except Exception as e:
                    logger.info("Site Type not exist for base station ({}).".format(base_station.name, e.message))

                # infra provider
                try:
                    wimax_bs_row['Infra Provider'] = base_station.infra_provider
                except Exception as e:
                    logger.info("Infra Provider not exist for base station ({}).".format(base_station.name, e.message))

                # building height
                try:
                    wimax_bs_row['Building Height'] = base_station.building_height
                except Exception as e:
                    logger.info("Building Height not exist for base station ({}).".format(base_station.name, e.message))

                # tower height
                try:
                    wimax_bs_row['Tower Height'] = base_station.tower_height
                except Exception as e:
                    logger.info("Tower Height not exist for base station ({}).".format(base_station.name, e.message))

                # latitude
                try:
                    wimax_bs_row['Latitude'] = base_station.latitude
                except Exception as e:
                    logger.info("Latitude not exist for base station ({}).".format(base_station.name, e.message))

                # longitude
                try:
                    wimax_bs_row['Longitude'] = base_station.longitude
                except Exception as e:
                    logger.info("Longitude not exist for base station ({}).".format(base_station.name, e.message))

                # idu ip
                try:
                    wimax_bs_row['IDU IP'] = sector.sector_configured_on.ip_address
                except Exception as e:
                    logger.info("IDU IP not exist for base station ({}).".format(base_station.name, e.message))

                # sector name
                try:
                    wimax_bs_row['Sector Name'] = sector.name.split("_")[-1]
                except Exception as e:
                    logger.info("Sector Name not exist for base station ({}).".format(base_station.name, e.message))

                # make of antenna
                try:
                    wimax_bs_row['Make Of Antenna'] = sector.antenna.make_of_antenna
                except Exception as e:
                    logger.info("Make Of Antenna not exist for base station ({}).".format(base_station.name,
                                                                                          e.message))

                # polarization
                try:
                    wimax_bs_row['Polarization'] = sector.antenna.polarization
                except Exception as e:
                    logger.info("Polarization not exist for base station ({}).".format(base_station.name, e.message))

                # antenna tilt
                try:
                    wimax_bs_row['Antenna Tilt'] = sector.antenna.tilt
                except Exception as e:
                    logger.info("Antenna Tilt not exist for base station ({}).".format(base_station.name, e.message))

                # antenna height
                try:
                    wimax_bs_row['Antenna Height'] = sector.antenna.height
                except Exception as e:
                    logger.info("Antenna Height not exist for base station ({}).".format(base_station.name, e.message))

                # antenna beamwidth
                try:
                    wimax_bs_row['Antenna Beamwidth'] = sector.antenna.beam_width
                except Exception as e:
                    logger.info("Antenna Beamwidth not exist for base station ({}).".format(base_station.name, e.message))

                # azimuth
                try:
                    wimax_bs_row['Azimuth'] = sector.antenna.azimuth_angle
                except Exception as e:
                    logger.info("Azimuth not exist for base station ({}).".format(base_station.name, e.message))

                # installation of splitter
                try:
                    wimax_bs_row['Installation Of Splitter'] = sector.antenna.sync_splitter_used
                except Exception as e:
                    logger.info("Installation Of Splitter not exist for base station ({}).".format(base_station.name, e.message))

                # type of gps
                try:
                    wimax_bs_row['Type Of GPS'] = base_station.gps_type
                except Exception as e:
                    logger.info("Type Of GPS not exist for base station ({}).".format(base_station.name, e.message))

                # bs switch ip
                try:
                    wimax_bs_row['BS Switch IP'] = base_station.bs_switch.ip_address
                except Exception as e:
                    logger.info("BS Switch IP not exist for base station ({}).".format(base_station.name, e.message))

                # aggregation switch
                try:
                    wimax_bs_row['Aggregation Switch'] = backhaul.aggregator.ip_address
                except Exception as e:
                    logger.info("Aggregation Switch not exist for base station ({}).".format(base_station.name,
                                                                                             e.message))

                # aggregation switch port
                try:
                    wimax_bs_row['Aggregation Switch Port'] = backhaul.aggregator_port_name
                except Exception as e:
                    logger.info("Aggregation Switch Port not exist for base station ({}).".format(base_station.name,
                                                                                                  e.message))

                # bs converter ip
                try:
                    wimax_bs_row['BS Converter IP'] = backhaul.bh_switch.ip_address
                except Exception as e:
                    logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

                # pop converter ip
                try:
                    wimax_bs_row['POP Converter IP'] = backhaul.pop.ip_address
                except Exception as e:
                    logger.info("POP Converter IP not exist for base station ({}).".format(base_station.name,
                                                                                           e.message))

                # converter type
                try:
                    wimax_bs_row['Converter Type'] = DeviceType.objects.get(pk=backhaul.bh_switch.device_type).alias
                except Exception as e:
                    logger.info("Converter Type not exist for base station ({}).".format(base_station.name, e.message))

                # bh configured switch or converter
                try:
                    wimax_bs_row['BH Configured On Switch/Converter'] = backhaul.bh_configured_on.ip_address
                except Exception as e:
                    logger.info("BH Configured On Switch/Converter not exist for base station ({}).".format(
                        base_station.name,
                        e.message))

                # bh configured switch or converter port
                try:
                    wimax_bs_row['Switch/Converter Port'] = backhaul.bh_port_name
                except Exception as e:
                    logger.info("Switch/Converter Port not exist for base station ({}).".format(base_station.name,
                                                                                                e.message))

                # bh capacity
                try:
                    wimax_bs_row['BH Capacity'] = backhaul.bh_capacity
                except Exception as e:
                    logger.info("BH Capacity not exist for base station ({}).".format(base_station.name, e.message))

                # bh offnet/onnet
                try:
                    wimax_bs_row['BH Offnet/Onnet'] = backhaul.bh_connectivity
                except Exception as e:
                    logger.info("BH Offnet/Onnet not exist for base station ({}).".format(base_station.name, e.message))

                # backhaul type
                try:
                    wimax_bs_row['Backhaul Type'] = backhaul.bh_type
                except Exception as e:
                    logger.info("Backhaul Type not exist for base station ({}).".format(base_station.name, e.message))

                # bh circuit id
                try:
                    wimax_bs_row['BH Circuit ID'] = backhaul.bh_circuit_id
                except Exception as e:
                    logger.info("BH Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

                # pe hostname
                try:
                    wimax_bs_row['PE Hostname'] = backhaul.pe_hostname
                except Exception as e:
                    logger.info("PE Hostname not exist for base station ({}).".format(base_station.name, e.message))

                # pe ip
                try:
                    wimax_bs_row['PE IP'] = backhaul.pe_ip
                except Exception as e:
                    logger.info("PE IP not exist for base station ({}).".format(base_station.name, e.message))

                # bso circuit id
                try:
                    wimax_bs_row['BSO Circuit ID'] = backhaul.ttsl_circuit_id
                except Exception as e:
                    logger.info("BSO Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

                # dr site
                try:
                    wimax_bs_row['DR Site'] = sector.dr_site
                except Exception as e:
                    logger.info("DR Site not exist for base station ({}).".format(base_station.name, e.message))

                # sector id
                try:
                    wimax_bs_row['Sector ID'] = sector.sector_id
                except Exception as e:
                    logger.info("Sector ID not exist for base station ({}).".format(base_station.name, e.message))

                # pmp
                try:
                    wimax_bs_row['PMP'] = sector.name.split("_")[-1]
                except Exception as e:
                    logger.info("Sector ID not exist for base station ({}).".format(base_station.name, e.message))

                # sector id
                try:
                    wimax_bs_row['Sector ID'] = sector.sector_id
                except Exception as e:
                    logger.info("Sector ID not exist for base station ({}).".format(base_station.name, e.message))

                # ************************************* BS Perf Parameters **********************************
                # sector utilization
                try:
                    # by splitting last string after underscore from sector name; we get pmp port number
                    if sector.name.split("_")[-1] == '1':
                        wimax_bs_row['Sector Utilization'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                        data_source='wimax_pmp1_utilization').using(
                                                                        alias=bs_machine_name)[0].current_value
                    elif sector.name.split("_")[-1] == '2':
                        wimax_bs_row['Sector Utilization'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                        data_source='wimax_pmp2_utilization').using(
                                                                        alias=bs_machine_name)[0].current_value
                    else:
                        pass
                except Exception as e:
                    logger.info("Sector Utilization not exist for base station ({}).".format(base_station.name,
                                                                                             e.message))

                # frequency
                try:
                    wimax_bs_row['Frequency'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                               data_source='frequency').using(
                                                                               alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Frequency not exist for base station ({}).".format(base_station.name, e.message))

                # mrc
                try:
                    # by splitting last string after underscore from sector name; we get pmp port number
                    if sector.name.split("_")[-1] == '1':
                        wimax_bs_row['MRC'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                             data_source='pmp1_mrc').using(
                                                                             alias=bs_machine_name)[0].current_value
                    elif sector.name.split("_")[-1] == '2':
                        wimax_bs_row['MRC'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                             data_source='pmp2_mrc').using(
                                                                             alias=bs_machine_name)[0].current_value
                    else:
                        pass
                except Exception as e:
                    logger.info("MRC not exist for base station ({}).".format(base_station.name, e.message))

                # idu type
                try:
                    wimax_bs_row['IDU Type'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                              data_source='idu_type').using(
                                                                              alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("IDU Type not exist for base station ({}).".format(base_station.name, e.message))

                # system uptime
                try:
                    wimax_bs_row['System Uptime'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                                 data_source='bs_uptime').using(
                                                                                 alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("System Uptime not exist for base station ({}).".format(base_station.name, e.message))

                # latency
                try:
                    wimax_bs_row['Latency'] = NetworkStatus.objects.filter(device_name=bs_device_name,
                                                                           data_source='rta').using(
                                                                           alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Latency not exist for base station ({}).".format(base_station.name, e.message))

                # pl
                try:
                    wimax_bs_row['PD'] = NetworkStatus.objects.filter(device_name=bs_device_name,
                                                                      data_source='pl').using(
                                                                      alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("PD not exist for base station ({}).".format(base_station.name, e.message))

                # ********************************** Far End (Wimax SS) ********************************

                # customer name
                try:
                    wimax_ss_row['Customer Name'] = customer.alias
                except Exception as e:
                    logger.info("Customer Name not exist for base station ({}).".format(sub_station.name, e.message))

                # circuit id
                try:
                    wimax_ss_row['Circuit ID'] = circuit.circuit_id
                except Exception as e:
                    logger.info("Circuit ID not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss ip
                try:
                    wimax_ss_row['SS IP'] = sub_station.device.ip_address
                except Exception as e:
                    logger.info("SS IP not exist for sub station ({}).".format(sub_station.name, e.message))

                # qos bandwidth
                try:
                    wimax_ss_row['QOS (BW)'] = circuit.qos_bandwidth
                except Exception as e:
                    logger.info("QOS (BW) not exist for sub station ({}).".format(sub_station.name, e.message))

                # latitude
                try:
                    wimax_ss_row['Latitude'] = sub_station.latitude
                except Exception as e:
                    logger.info("Latitude not exist for sub station ({}).".format(sub_station.name, e.message))

                # longitude
                try:
                    wimax_ss_row['Longitude'] = sub_station.longitude
                except Exception as e:
                    logger.info("Longitude not exist for sub station ({}).".format(sub_station.name, e.message))

                # mac address
                try:
                    wimax_ss_row['MAC'] = sub_station.device.mac_address
                except Exception as e:
                    logger.info("MAC not exist for sub station ({}).".format(sub_station.name, e.message))

                # building height
                try:
                    wimax_ss_row['Building Height'] = sub_station.building_height
                except Exception as e:
                    logger.info("Building Height not exist for sub station ({}).".format(sub_station.name, e.message))

                # tower/pole height
                try:
                    wimax_ss_row['Tower/Pole Height'] = sub_station.tower_height
                except Exception as e:
                    logger.info("Tower/Pole Height not exist for sub station ({}).".format(sub_station.name, e.message))

                # antenna height
                try:
                    wimax_ss_row['Antenna Height'] = sub_station.antenna.height
                except Exception as e:
                    logger.info("Antenna Height not exist for sub station ({}).".format(sub_station.name, e.message))

                # antenna beamwidth
                try:
                    wimax_ss_row['Antenna Beamwidth'] = sub_station.antenna.beam_width
                except Exception as e:
                    logger.info("Antenna Beamwidth not exist for sub station ({}).".format(sub_station.name, e.message))

                # polarization
                try:
                    wimax_ss_row['Polarization'] = sub_station.antenna.polarization
                except Exception as e:
                    logger.info("Polarization not exist for sub station ({}).".format(sub_station.name, e.message))

                # antenna type
                try:
                    wimax_ss_row['Antenna Type'] = sub_station.antenna.antenna_type
                except Exception as e:
                    logger.info("Antenna Type not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss mount type
                try:
                    wimax_ss_row['SS Mount Type'] = sub_station.antenna.mount_type
                except Exception as e:
                    logger.info("SS Mount Type not exist for sub station ({}).".format(sub_station.name, e.message))

                # ethernet extender
                try:
                    wimax_ss_row['Ethernet Extender'] = sub_station.ethernet_extender
                except Exception as e:
                    logger.info("Ethernet Extender not exist for sub station ({}).".format(sub_station.name, e.message))

                # cable length
                try:
                    wimax_ss_row['Cable Length'] = sub_station.cable_length
                except Exception as e:
                    logger.info("Cable Length not exist for sub station ({}).".format(sub_station.name, e.message))

                # rssi during acceptance
                try:
                    wimax_ss_row['RSSI During Acceptance'] = circuit.dl_rssi_during_acceptance
                except Exception as e:
                    logger.info("RSSI During Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                                e.message))

                # cinr during acceptance
                try:
                    wimax_ss_row['CINR During Acceptance'] = circuit.dl_cinr_during_acceptance
                except Exception as e:
                    logger.info("CINR During Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                                e.message))

                # Customer Address
                try:
                    wimax_ss_row['Customer Address'] = customer.address
                except Exception as e:
                    logger.info("Customer Address not exist for sub station ({}).".format(sub_station.name, e.message))

                # date of acceptance
                try:
                    wimax_ss_row['Date Of Acceptance'] = circuit.date_of_acceptance.strftime('%d/%b/%Y')
                except Exception as e:
                    logger.info("Date Of Acceptance not exist for base station ({}).".format(base_station.name,
                                                                                             e.message))

                # ************************************* SS Perf Parameters **********************************
                # frequency
                try:
                    wimax_ss_row['Frequency'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                             data_source='frequency').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Frequency not exist for sub station ({}).".format(sub_station.name, e.message))

                # sector id
                try:
                    # by splitting last string after underscore from sector name; we get pmp port number
                    if sector.name.split("_")[-1] == '1':
                        wimax_ss_row['Sector ID'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                        data_source='sector_id_pmp1').using(
                                                                        alias=ss_machine_name)[0].current_value
                    elif sector.name.split("_")[-1] == '2':
                        wimax_ss_row['Sector ID'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                        data_source='sector_id_pmp2').using(
                                                                        alias=ss_machine_name)[0].current_value
                    else:
                        pass
                except Exception as e:
                    logger.info("Sector ID not exist for sub station ({}).".format(sub_station.name, e.message))

                # polled ss ip
                try:
                    wimax_ss_row['Polled SS IP'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='ss_ip').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled SS IP not exist for sub station ({}).".format(sub_station.name, e.message))

                # polled ss mac
                try:
                    wimax_ss_row['Polled SS MAC'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                             data_source='ss_mac').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled SS MAC not exist for sub station ({}).".format(sub_station.name, e.message))

                # rssi dl
                try:
                    wimax_ss_row['RSSI DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='dl_rssi').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("RSSI DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # rssi ul
                try:
                    wimax_ss_row['RSSI UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='ul_rssi').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("RSSI UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # cinr dl
                try:
                    wimax_ss_row['CINR DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='dl_cinr').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("CINR DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # cinr ul
                try:
                    wimax_ss_row['CINR UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='ul_cinr').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("CINR UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # intrf dl
                try:
                    wimax_ss_row['INTRF DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='dl_intrf').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("INTRF DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # intrf ul
                try:
                    wimax_ss_row['INTRF UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='ul_intrf').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("INTRF UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # ptx
                try:
                    wimax_ss_row['PTX'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                         data_source='ss_ptx').using(
                                                                         alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("PTX not exist for sub station ({}).".format(sub_station.name, e.message))

                # session uptime
                try:
                    wimax_ss_row['Session Uptime'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                              data_source='session_uptime').using(
                                                                              alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Session Uptime not exist for sub station ({}).".format(sub_station.name, e.message))

                # device uptime
                try:
                    wimax_ss_row['Device Uptime'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                              data_source='uptime').using(
                                                                              alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Device Uptime  not exist for sub station ({}).".format(sub_station.name, e.message))

                # modulation dl fec
                try:
                    wimax_ss_row['Modulation DL FEC'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='modulation_dl_fec').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Modulation DL FEC not exist for sub station ({}).".format(sub_station.name, e.message))

                # modulation ul fec
                try:
                    wimax_ss_row['Modulation UL FEC'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='modulation_ul_fec').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Modulation UL FEC not exist for sub station ({}).".format(sub_station.name, e.message))

                # latency
                try:
                    wimax_ss_row['Latency'] = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='rta').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Latency not exist for sub station ({}).".format(sub_station.name, e.message))

                # pl (packet loss)
                try:
                    wimax_ss_row['PD'] = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                                      data_source='pl').using(
                                                                      alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("PD not exist for sub station ({}).".format(sub_station.name, e.message))

                # utilization dl
                try:
                    wimax_ss_row['Utilization DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='dl_utilization').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Utilization DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # utilization ul
                try:
                    wimax_ss_row['Utilization UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='ul_utilization').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Utilization UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # auto negotiation
                try:
                    wimax_ss_row['Auto Negotiation'] = Status.objects.filter(device_name=ss_device_name,
                                                                             data_source='autonegotiation').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Auto Negotiation not exist for sub station ({}).".format(sub_station.name, e.message))

                # duplex
                try:
                    wimax_ss_row['Duplex'] = Status.objects.filter(device_name=ss_device_name,
                                                                   data_source='duplex').using(
                                                                   alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Duplex not exist for sub station ({}).".format(sub_station.name, e.message))

                # speed
                try:
                    wimax_ss_row['Speed'] = Status.objects.filter(device_name=ss_device_name,
                                                                   data_source='ss_speed').using(
                                                                   alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Speed not exist for sub station ({}).".format(sub_station.name, e.message))

                # link
                try:
                    wimax_ss_row['Link'] = Status.objects.filter(device_name=ss_device_name,
                                                                 data_source='link_state').using(
                                                                 alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Link not exist for sub station ({}).".format(sub_station.name, e.message))

                # append 'wimax_bs_row' dictionary in 'wimax_bs_rows'
                wimax_bs_rows.append(wimax_bs_row)

                # append 'wimax_ss_row' dictionary in 'wimax_ss_rows'
                wimax_ss_rows.append(wimax_ss_row)

        # insert 'wimax bs' rows in result dictionary
        result['wimax_bs'] = wimax_bs_rows if wimax_bs_rows else ""

        # insert 'wimax ss' rows in result dictionary
        result['wimax_ss'] = wimax_ss_rows if wimax_ss_rows else ""

        print "****************************** wimax (result) - ", result

        return result


def remove_duplicate_dict_from_list(input_list=None):
    """ Remove duplicate dictionaries from list of dictionaries

        :Parameters:
            - 'input_list' (list) - list of dictionaries for e.g.
                                        [
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            },
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            },
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            }
                                        ]

        :Returns:
           - 'result_list' (list) - list of dictionaries containing unique dictionaries for e.g.
                                        [
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            }
                                        ]
    """

    # list of dictionaries to be returned as a result
    result_list = []

    # temporary set containing dictionaries values in tuples for e.g
    # set([((key, value), (key, value), (key, value)), ((key, value), (key, value), (key, value))]

    temp_set = set()

    # loop through input list (list of dictionaries which needs to be filtered)
    for d in input_list:
        # t is set of dictionary values tuple for e.g
        # ((key, value), (key, value), (key, value), (key, value))
        # (('City', u'Kolkata'), ('Antenna Height', 29.0), ('BH Circuit ID', u'COPF-571'), ('PE IP', u'192.168.216.37'))
        t = tuple(d.items())
        if t not in temp_set:
            # adding tuple 't' to 'temp_set'
            temp_set.add(t)
            # append dictionary 'd' to 'result_list'
            result_list.append(d)

    return result_list


#**************************************** GIS Wizard ****************************************#

class GisWizardListView(BaseStationList):
    template_name = 'gis_wizard/wizard_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(GisWizardListView, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            # {'mData': 'bs_technology__alias', 'sTitle': 'Technology', 'sWidth': 'auto', },
            {'mData': 'bs_site_id', 'sTitle': 'Site ID', 'sWidth': 'auto', },
            {'mData': 'bs_switch__id', 'sTitle': 'BS Switch', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'backhaul__name', 'sTitle': 'Backhaul', 'sWidth': 'auto', },
            {'mData': 'bs_type', 'sTitle': 'BS Type', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'building_height', 'sTitle': 'Building Height', 'sWidth': 'auto', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False},
        ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class GisWizardListingTable(BaseStationListingTable):

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
            detail_action = '<a href="/gis-wizard/base-station/{0}/details/"><i class="fa fa-list-alt text-info"></i></a>&nbsp'.format(device_id)
            if self.request.user.has_perm('inventory.change_basestation'):
                edit_action = '<a href="/gis-wizard/base-station/{0}/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_basestation'):
                delete_action = '<a href="/base_station/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            delete_action = ''
            if edit_action or delete_action:
                dct.update(actions=detail_action+edit_action+delete_action)
            else:
                dct.update(actions=detail_action)
        return json_data


class GisWizardBaseStationDetailView(BaseStationDetail):
    template_name = 'gis_wizard/base_station_detail.html'


def gis_wizard_base_station_select(request):
    return render(request, 'gis_wizard/base_station.html', {'select_view': True})


class GisWizardBaseStationMixin(object):
    form_class = WizardBaseStationForm
    template_name = 'gis_wizard/base_station.html'

    def get_success_url(self):
        if self.request.GET.get('show', None):
            return reverse('gis-wizard-base-station-update', kwargs={'pk': self.object.id})
        if self.object.backhaul:
            return reverse('gis-wizard-backhaul-update', kwargs={'bs_pk': self.object.id, 'pk': self.object.backhaul.id})
        else:
            return reverse('gis-wizard-backhaul-select', kwargs={'bs_pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(GisWizardBaseStationMixin, self).get_context_data(**kwargs)
        if 'pk' in self.kwargs: # Update View

            base_station = BaseStation.objects.get(id=self.kwargs['pk'])
            if base_station.backhaul:
                skip_url = reverse('gis-wizard-backhaul-update', kwargs={'bs_pk': base_station.id, 'pk': base_station.backhaul.id})
            else:
                skip_url = reverse('gis-wizard-backhaul-select', kwargs={'bs_pk': base_station.id})

            save_text = 'Update'
            context['skip_url'] = skip_url
        else: # Create View
            save_text = 'Save'

        context['save_text'] = save_text
        return context

    def form_valid(self, form):
        alias = re.compile(r'[^\w]').sub("_", form.cleaned_data['alias'])
        city = City.objects.get(id=form.cleaned_data['city']).city_name[:3]
        state = State.objects.get(id=form.cleaned_data['state']).state_name[:3]
        form.instance.name = alias + "_" + city + "_" + state
        return super(GisWizardBaseStationMixin, self).form_valid(form)


class GisWizardBaseStationCreateView(GisWizardBaseStationMixin, BaseStationCreate):
    pass


class GisWizardBaseStationUpdateView(GisWizardBaseStationMixin, BaseStationUpdate):
    pass


class GisWizardBackhaulDetailView(BackhaulDetail):
    template_name = 'gis_wizard/backhaul_detail.html'

    def get_context_data(self, **kwargs):
        context = super(GisWizardBackhaulDetailView, self).get_context_data(**kwargs)
        context['base_station'] = BaseStation.objects.get(id=self.kwargs['bs_pk'])
        return context


def gis_wizard_backhaul_select(request, bs_pk):
    base_station = BaseStation.objects.get(id=bs_pk)
    if base_station.backhaul:
        return HttpResponseRedirect(reverse('gis-wizard-backhaul-update', kwargs={'bs_pk': bs_pk, 'pk': base_station.backhaul.id}))

    return render(request, 'gis_wizard/backhaul.html',
        {
            'select_view': True,
            'bs_pk': bs_pk,
            'organization': base_station.organization,
            'base_station': base_station,
        }
    )


def gis_wizard_backhaul_delete(request, bs_pk):
    base_station = BaseStation.objects.get(id=bs_pk)
    if base_station.backhaul:
        base_station.backhaul = None
        base_station.bh_port_name = None
        base_station.bh_port = None
        base_station.bh_capacity = None
        base_station.save()
    return HttpResponseRedirect(reverse('gis-wizard-backhaul-create', kwargs={'bs_pk': bs_pk}))


class GisWizardBackhaulMixin(object):
    form_class = WizardBackhaulForm
    template_name = 'gis_wizard/backhaul.html'

    def get_success_url(self):
        if self.request.GET.get('show', None):
            return reverse('gis-wizard-backhaul-update', kwargs={'bs_pk': self.kwargs['bs_pk'], 'pk': self.object.id})
        return reverse('gis-wizard-sector-list', kwargs = {
            'bs_pk': self.kwargs['bs_pk']
        })

    def form_valid(self, form):
        ip_address = form.cleaned_data['bh_configured_on'].ip_address
        form.instance.name = ip_address
        form.instance.alias = ip_address
        form.instance.dr_site = 'No'
        response = super(GisWizardBackhaulMixin, self).form_valid(form)

        base_station = BaseStation.objects.get(id=self.kwargs['bs_pk'])
        base_station.backhaul = self.object
        base_station.bh_port_name = self.object.bh_port_name
        base_station.bh_port = self.object.bh_port
        base_station.bh_capacity = self.object.bh_capacity
        base_station.save()

        return response

    def get_context_data(self, **kwargs):
        context = super(GisWizardBackhaulMixin, self).get_context_data(**kwargs)
        context['bs_pk'] = self.kwargs['bs_pk']
        base_station = BaseStation.objects.get(id=context['bs_pk'])
        context['base_station'] = base_station
        if base_station.backhaul:
            context['base_station_has_backhaul'] = True
        else:
            context['base_station_has_backhaul'] = False
        if 'pk' in self.kwargs: # Update View
            save_text = 'Update'
        else: # Create View
            save_text = 'Save'
        context['save_text'] = save_text
        return context


class GisWizardBackhaulCreateView(GisWizardBackhaulMixin, BackhaulCreate):
    pass


class GisWizardBackhaulUpdateView(GisWizardBackhaulMixin, BackhaulUpdate):
    pass


class GisWizardSectorListView(SectorList):
    template_name = 'gis_wizard/sectors_list.html'

    def get_context_data(self, **kwargs):
        context = super(GisWizardSectorListView, self).get_context_data(**kwargs)
        base_station = BaseStation.objects.get(id=self.kwargs['bs_pk'])
        context['base_station'] = base_station

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
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False},
        ]

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class GisWizardSectorListing(SectorListingTable):

    def get_initial_queryset(self):
        qs = super(GisWizardSectorListing, self).get_initial_queryset()
        qs = qs.filter(base_station_id=self.kwargs['bs_pk'], bs_technology_id=self.kwargs['selected_technology'])
        return qs

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

            sector_id = dct.pop('id')
            kwargs = {key: self.kwargs[key] for key in ['bs_pk', 'selected_technology']}
            kwargs.update({'pk': sector_id})
            detail_action = '<a href="' + reverse('gis-wizard-sector-detail', kwargs=kwargs) + '"><i class="fa fa-list-alt text-info"></i></a>&nbsp'
            if self.request.user.has_perm('inventory.change_sector'):
                edit_url = reverse('gis-wizard-sector-update', kwargs=kwargs)
                edit_action = '<a href="' + edit_url + '"><i class="fa fa-pencil text-dark"></i></a>&nbsp'
            else:
                edit_action = ''
            dct.update(actions=detail_action+edit_action)
        return json_data


class GisWizardSectorDetailView(SectorDetail):
    template_name = 'gis_wizard/sector_detail.html'

    def get_context_data(self, **kwargs):
        context = super(GisWizardSectorDetailView, self).get_context_data(**kwargs)
        base_station = BaseStation.objects.get(id=self.kwargs['bs_pk'])
        context['selected_technology'] = self.kwargs['selected_technology']
        context['base_station'] = base_station
        if self.object:
            if self.object.antenna:
                context['sector_antenna'] = self.object.antenna
            if int(self.kwargs['selected_technology']) == 2: # Technology is P2P
                if len(self.object.circuit_set.all()) == 1:
                    circuit = self.object.circuit_set.all()[0]
                    context['circuit'] = circuit
                    if circuit.sub_station:
                        context['sub_station'] = circuit.sub_station
                        if circuit.sub_station.antenna:
                            context['sub_station_antenna'] = circuit.sub_station.antenna
                    if circuit.customer:
                        context['customer'] = circuit.customer

        if self.kwargs['selected_technology'] == '2':
            context['sector_text'] = 'PTP'
        else:
            context['sector_text'] = 'Sector'

        return context


def gis_wizard_sector_select(request, bs_pk, selected_technology):
     base_station = BaseStation.objects.get(id=bs_pk)
     technologies = DeviceTechnology.objects.filter(name__in=['P2P', 'WiMAX', 'PMP'])
     return render(request, 'gis_wizard/sector.html',
         {
             'select_view': True,
             'bs_pk': bs_pk,
             'selected_technology': selected_technology,
             'technologies': technologies,
             'base_station': base_station,
         }
     )


def gis_wizard_sector_delete(request, bs_pk, pk):
    sector = Sector.objects.get(id=pk)
    sector.base_station = None
    sector.save()
    return HttpResponseRedirect(reverse('gis-wizard-sector-create', kwargs={'bs_pk': bs_pk, 'selected_technology': sector.bs_technology_id}))


class GisWizardSectorMixin(object):
    form_class = WizardSectorForm
    antenna_form_class = WizardAntennaForm
    sub_station_form_class = WizardSubStationForm
    customer_form_class = WizardCustomerForm
    circuit_form_class = WizardCircuitForm
    template_name = 'gis_wizard/sector.html'
    success_url = reverse_lazy('gis-wizard-base-station-list')

    def get_success_url(self):
        technology_id = self.kwargs['selected_technology']
        if self.request.GET.get('show', None):
            return reverse('gis-wizard-sector-update', kwargs={'bs_pk': self.kwargs['bs_pk'], 'pk': self.object.id,
                'selected_technology': technology_id})
        if int(technology_id) == 2:
            return self.success_url

        return reverse('gis-wizard-sub-station-list', kwargs = {
            'bs_pk': self.kwargs['bs_pk'], 'selected_technology': technology_id, 'sector_pk': self.object.id
        })

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        form_kwargs = super(GisWizardSectorMixin, self).get_form_kwargs()
        technology = DeviceTechnology.objects.get(id=self.kwargs['selected_technology'])
        form_kwargs.update({'technology': technology.name})
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(GisWizardSectorMixin, self).get_context_data(**kwargs)
        technologies = DeviceTechnology.objects.filter(name__in=['P2P', 'WiMAX', 'PMP'])
        base_station = BaseStation.objects.get(id=self.kwargs['bs_pk'])
        context['bs_pk'] = self.kwargs['bs_pk']
        context['selected_technology'] = self.kwargs['selected_technology']
        context['technologies'] = technologies
        context['base_station'] = base_station
        if self.object:
            form_kwargs = self.get_form_kwargs()
            if self.object.antenna:
                form_kwargs.update({'instance': self.object.antenna})
                context['sector_antenna_form'] = self.antenna_form_class(**form_kwargs)

            ## If technology is P2P and method is GET; Then provide sub station, antenna, circuit and customer forms in context.
            if int(self.kwargs['selected_technology']) == 2 and self.request.method == 'GET': # Technology is P2P
                if len(self.object.circuit_set.all()) == 1:
                    circuit = self.object.circuit_set.all()[0]
                    form_kwargs.update({'instance': circuit})
                    context['circuit_form'] = self.circuit_form_class(**form_kwargs)
                    if circuit.sub_station:
                        form_kwargs.update({'instance': circuit.sub_station})
                        context['sub_station_form'] = self.sub_station_form_class(**form_kwargs)
                        if circuit.sub_station.antenna: # Use formset as there are two antenna to avoid name conflicts
                            form_kwargs.pop('instance')
                            queryset = Antenna.objects.filter(id=circuit.sub_station.antenna.id)
                            formset = WizardPTPSubStationAntennaFormSet(queryset=queryset, **form_kwargs)
                            context['sub_station_antenna_form'] = formset
                    if circuit.customer:
                        form_kwargs.update({'instance': circuit.customer})
                        context['customer_form'] = self.customer_form_class(**form_kwargs)

        ## Create Skip URL and Delete & Show URL
        skip_url = reverse('gis-wizard-base-station-list')
        if self.object and self.object.base_station == base_station:
            context['base_station_has_sector'] = True
            context['delete_url'] = reverse('gis-wizard-sector-delete', kwargs={'bs_pk': base_station.id, 'pk': self.object.id})
            if self.object.bs_technology_id != 2:
                skip_url = reverse('gis-wizard-sub-station-list', kwargs={'bs_pk': base_station.id,
                    'selected_technology': self.kwargs['selected_technology'], 'sector_pk': self.object.id})
        else:
            context['base_station_has_sector'] = False
        context['skip_url'] = skip_url

        if 'pk' in self.kwargs: # Update View
            save_text = 'Update'
        else: # Create View
            save_text = 'Save'
        context['save_text'] = save_text
        return context

    def post(self, request, *args, **kwargs):
        """
        Save sector and antenna.
        """

        try: # if update view
            self.object = self.get_object()
        except AttributeError as e: # if create view
            self.object = None

        form_kwargs = self.get_form_kwargs()
        if self.object and self.object.antenna:
            antenna_instance = self.object.antenna
        elif request.POST.get('sector_antenna_radio') == 'existing' and request.POST.get('sector_antenna'):
            antenna_id = request.POST.get('sector_antenna')
            antenna_instance = Antenna.objects.get(id=antenna_id)
        else:
            antenna_instance = None

        sector_form = self.get_form(self.get_form_class())

        form_kwargs.update({'instance': antenna_instance})
        antenna_form = self.antenna_form_class(**form_kwargs)

        technology = self.kwargs['selected_technology']
        if int(technology) == 2:
            if request.POST.get('sub_station_radio') == 'existing' and request.POST.get('sub_station'):
                sub_station_id = request.POST.get('sub_station')
                sub_station_instance = SubStation.objects.get(id=sub_station_id)
            else:
                sub_station_instance = None
            if request.POST.get('sub_station_customer_radio') == 'existing' and request.POST.get('sub_station_customer'):
                customer_id = request.POST.get('sub_station_customer')
                customer_instance = Customer.objects.get(id=customer_id)
            else:
                customer_instance = None
            if request.POST.get('sub_station_circuit_radio') == 'existing' and request.POST.get('sub_station_circuit'):
                circuit_id = request.POST.get('sub_station_circuit')
                circuit_instance = Circuit.objects.get(id=circuit_id)
            else:
                circuit_instance = None
            if self.object and len(self.object.circuit_set.all()) == 1:
                circuit = self.object.circuit_set.all()[0]
                circuit_instance = circuit
                if circuit.sub_station:
                    sub_station_instance = circuit.sub_station
                if circuit.customer:
                    customer_instance = circuit.customer

            form_kwargs.update({'instance': sub_station_instance})
            sub_station_form = self.sub_station_form_class(**form_kwargs)

            # form_kwargs.update({'instance': antenna_instance})
            form_kwargs.pop('instance')
            sub_station_antenna_formset = WizardPTPSubStationAntennaFormSet(**form_kwargs)

            form_kwargs.update({'instance': customer_instance})
            customer_form = self.customer_form_class(**form_kwargs)

            form_kwargs.update({'instance': circuit_instance})
            circuit_form = self.circuit_form_class(**form_kwargs)

            if (sector_form.is_valid() and antenna_form.is_valid() and sub_station_form.is_valid()
                and sub_station_antenna_formset.is_valid() and customer_form.is_valid() and circuit_form.is_valid()):
                return self.form_valid(sector_form, antenna_form, sub_station_form, sub_station_antenna_formset, customer_form, circuit_form)
            else:
                return self.form_invalid(sector_form, antenna_form, sub_station_form, sub_station_antenna_formset, customer_form, circuit_form)
        else:

            if (sector_form.is_valid() and antenna_form.is_valid()):
                return self.form_valid(sector_form, antenna_form)
            else:
                return self.form_invalid(sector_form, antenna_form)

    def form_valid(self, sector_form, antenna_form, sub_station_form=None, sub_station_antenna_formset=None, customer_form=None, circuit_form=None):
        form_kwargs = self.get_form_kwargs()
        base_station = BaseStation.objects.get(id=self.kwargs['bs_pk'])
        technology = self.kwargs['selected_technology']
        sector_configured_on_id = form_kwargs['data']['sector_configured_on']
        sector_configured_on = Device.objects.get(id=sector_configured_on_id)

        antenna = antenna_form.save(commit=False)
        antenna.name = sector_configured_on.ip_address
        antenna.alias = sector_configured_on.ip_address
        antenna.organization = base_station.organization
        antenna.save()

        self.object = sector_form.save(commit=False)
        self.object.name = sector_configured_on.ip_address

        # Alias: the IP address of the device for P2P; FOR PMP and WIMAX this would be Sector ID.
        if int(technology) == 2:
            self.object.alias = sector_configured_on.ip_address
        else:
            self.object.alias = form_kwargs['data']['sector_id']
        self.object.bs_technology_id = technology
        self.object.organization = base_station.organization
        self.object.base_station = base_station
        self.object.antenna = antenna
        self.object.save()

        if int(technology) == 2:
            device_id = form_kwargs['data']['device']
            device = Device.objects.get(id=device_id)

            sub_station_antenna = sub_station_antenna_formset[0].save(commit=False)
            sub_station_antenna.name = device.ip_address
            sub_station_antenna.alias = device.ip_address
            sub_station_antenna.organization = base_station.organization
            sub_station_antenna.save()

            sub_station = sub_station_form.save(commit=False)
            sub_station.name = device.ip_address
            sub_station.alias = device.ip_address
            sub_station.organization = base_station.organization
            sub_station.antenna = sub_station_antenna # Far End Antenna.
            sub_station.save()

            customer = customer_form.save(commit=False)
            customer.name = form_kwargs['data']['alias']
            customer.organization = base_station.organization
            customer.save()

            circuit = circuit_form.save(commit=False)
            circuit.name = form_kwargs['data']['circuit_id']
            circuit.alias = form_kwargs['data']['circuit_id']
            circuit.organization = base_station.organization
            circuit.sector = self.object
            circuit.customer = customer
            circuit.sub_station = sub_station
            circuit.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, sector_form, antenna_form, sub_station_form=None, sub_station_antenna_formset=None, customer_form=None, circuit_form=None):
        return self.render_to_response(self.get_context_data(form=sector_form, antenna_form=antenna_form, sub_station_form=sub_station_form, sub_station_antenna_form=sub_station_antenna_formset, customer_form=customer_form, circuit_form=circuit_form))


class GisWizardSectorCreateView(GisWizardSectorMixin, SectorCreate):
    pass


class GisWizardSectorUpdateView(GisWizardSectorMixin, SectorUpdate):
    pass


def get_wizard_form(request):
    model_str = request.GET.get('model')
    form_class = {
                'antenna': WizardAntennaForm,
                'sub_station': WizardSubStationForm,
                'customer': WizardCustomerForm,
                'circuit': WizardCircuitForm,
        }[model_str]
    model = {
            'antenna': Antenna,
            'sub_station': SubStation,
            'customer': Customer,
            'circuit': Circuit,
        }[model_str]
    technology = DeviceTechnology.objects.get(id=request.GET.get('technology')).name
    form_kwargs = {'request': request, 'technology': technology}
    if 'pk' in request.GET:
        pk = request.GET.get('pk')
        instance = model.objects.get(id=pk)
        form = form_class(instance=instance, **form_kwargs)
    else:
        form = form_class(**form_kwargs)

    return render(request, 'gis_wizard/form.html', {'form': form})


def get_ptp_sub_station_antenna_wizard_form(request):
    technology = DeviceTechnology.objects.get(id=2).name
    form_kwargs = {'request': request, 'technology': technology}
    if 'pk' in request.GET:
        pk = request.GET.get('pk')
        queryset = Antenna.objects.filter(id=pk)
        formset = WizardPTPSubStationAntennaFormSet(queryset=queryset, **form_kwargs)
    else:
        formset = WizardPTPSubStationAntennaFormSet(queryset=Antenna.objects.none(), **form_kwargs)

    return render(request, 'gis_wizard/ptp_sub_station_antenna_form.html', {'formset': formset})


class GisWizardSectorSubStationListView(SubStationList):
    """
    """
    template_name = 'gis_wizard/sub_stations_list.html'

    def get_context_data(self, **kwargs):
        context = super(GisWizardSectorSubStationListView, self).get_context_data(**kwargs)
        base_station = BaseStation.objects.get(id=self.kwargs['bs_pk'])
        context['base_station'] = base_station
        sector = Sector.objects.get(id=self.kwargs['sector_pk'])
        context['sector'] = sector
        context['selected_technology'] = self.kwargs['selected_technology']

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
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False}
        ]

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class GisWizardSubStationListing(SubStationListingTable):
    """
    Class based View to render Sub Station Data table.
    """

    def get_initial_queryset(self):
        qs = super(GisWizardSubStationListing, self).get_initial_queryset()
        qs = qs.filter(circuit__sector=self.kwargs['sector_pk'])
        return qs

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

            sub_station_id = dct.pop('id')
            kwargs = {key: self.kwargs[key] for key in ['bs_pk', 'selected_technology', 'sector_pk']}
            kwargs.update({'pk': sub_station_id})
            detail_action = '<a href="' + reverse('gis-wizard-sub-station-detail', kwargs=kwargs) + '"><i class="fa fa-list-alt text-info"></i></a>&nbsp'
            if self.request.user.has_perm('inventory.change_substation'):
                edit_url = reverse('gis-wizard-sub-station-update', kwargs=kwargs)
                edit_action = '<a href="' + edit_url + '"><i class="fa fa-pencil text-dark"></i></a>&nbsp'
            else:
                edit_action = ''
            dct.update(actions=detail_action+edit_action)
        return json_data


def gis_wizard_sub_station_select(request, bs_pk, selected_technology, sector_pk):
    technologies = DeviceTechnology.objects.order_by('-name').filter(name__in=['WiMAX', 'PMP'])
    return render(request, 'gis_wizard/sub_station.html',
        {
            'select_view': True,
            'bs_pk': bs_pk,
            'selected_technology': selected_technology,
            'sector_pk': sector_pk,
            'technologies': technologies,
            'organization': BaseStation.objects.get(id=bs_pk).organization
        }
    )


class GisWizardSubStationDetailView(SubStationDetail):
    template_name = 'gis_wizard/sub_station_detail.html'

    def get_context_data(self, **kwargs):
        context = super(GisWizardSubStationDetailView, self).get_context_data(**kwargs)
        context['selected_technology'] = self.kwargs['selected_technology']
        base_station = BaseStation.objects.get(id=self.kwargs['bs_pk'])
        context['base_station'] = base_station
        context['sector_pk'] = self.kwargs['sector_pk']
        if self.object.antenna:
            context['sub_station_antenna'] = self.object.antenna
        if len(self.object.circuit_set.all()) == 1:
            circuit = self.object.circuit_set.all()[0]
            context['circuit'] = circuit
            if circuit.customer:
                context['customer'] = circuit.customer
        return context


def gis_wizard_sub_station_delete(request, bs_pk, selected_technology, sector_pk, pk):
    circuit = Circuit.objects.get(sub_station_id=pk)
    circuit.sector = None
    circuit.save()
    return HttpResponseRedirect(reverse('gis-wizard-sub-station-create', kwargs={'bs_pk': bs_pk,
        'selected_technology': selected_technology, 'sector_pk': sector_pk}))


class GisWizardSubStationMixin(object):
    form_class = WizardSubStationForm
    antenna_form_class = WizardAntennaForm
    customer_form_class = WizardCustomerForm
    circuit_form_class = WizardCircuitForm
    template_name = 'gis_wizard/sub_station.html'
    success_url = reverse_lazy('gis-wizard-base-station-list')

    def get_success_url(self):
        if self.request.GET.get('show', None):
            return reverse('gis-wizard-sub-station-update', kwargs={'bs_pk': self.kwargs['bs_pk'], 'pk': self.object.id,
                'selected_technology': self.kwargs['selected_technology'], 'sector_pk': self.kwargs['sector_pk']})

        return self.success_url

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        form_kwargs = super(GisWizardSubStationMixin, self).get_form_kwargs()
        technology = DeviceTechnology.objects.get(id=self.kwargs['selected_technology'])
        form_kwargs.update({'technology': technology.name})
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(GisWizardSubStationMixin, self).get_context_data(**kwargs)
        technologies = DeviceTechnology.objects.order_by('-name').filter(name__in=['WiMAX', 'PMP'])
        context['bs_pk'] = self.kwargs['bs_pk']
        context['selected_technology'] = self.kwargs['selected_technology']
        context['sector_pk'] = self.kwargs['sector_pk']
        context['technologies'] = technologies
        context['organization'] = BaseStation.objects.get(id=self.kwargs['bs_pk']).organization
        if self.object:
            form_kwargs = self.get_form_kwargs()
            context['sub_station_antenna_id'] = self.object.antenna.id if self.object.antenna else 0
            # context['sub_station_customer_id'] = self.object.customer.id if self.object.customer else 0
            # context['sub_station_circuit_id'] = self.object.circuit.id if self.object.circuit else 0

            ## If method is GET; Then provide antenna, circuit and customer forms in context.
            if self.request.method == 'GET':
                if self.object.antenna:
                    form_kwargs.update({'instance': self.object.antenna})
                    context['sub_station_antenna_form'] = self.antenna_form_class(**form_kwargs)
                if len(self.object.circuit_set.all()) == 1:
                    circuit = self.object.circuit_set.all()[0]
                    form_kwargs.update({'instance': circuit})
                    context['circuit_form'] = self.circuit_form_class(**form_kwargs)
                    if circuit.customer:
                        form_kwargs.update({'instance': circuit.customer})
                        context['customer_form'] = self.customer_form_class(**form_kwargs)
        if self.object and Circuit.objects.filter(sector_id=self.kwargs['sector_pk'], sub_station_id=self.object.id).exists():
            context['sector_has_sub_station'] = True
        else:
            context['sector_has_sub_station'] = False

        if 'pk' in self.kwargs: # Update View
            save_text = 'Update'
        else: # Create View
            save_text = 'Save'
        context['save_text'] = save_text
        return context

    def post(self, request, *args, **kwargs):
        """
        Save sub_station, antenna, customer and circuit for WiMAX and PMP.
        """

        try: # if update view
            self.object = self.get_object()
        except AttributeError as e: # if create view
            self.object = None

        form_kwargs = self.get_form_kwargs()
        if self.object and self.object.antenna:
            antenna_instance = self.object.antenna
        elif request.POST.get('sub_station_antenna_radio') == 'existing':
            antenna_id = request.POST.get('sub_station_antenna')
            antenna_instance = Antenna.objects.get(id=antenna_id)
        else:
            antenna_instance = None
        if request.POST.get('sub_station_customer_radio') == 'existing' and request.POST.get('sub_station_customer'):
            customer_id = request.POST.get('sub_station_customer')
            customer_instance = Customer.objects.get(id=customer_id)
        else:
            customer_instance = None
        if request.POST.get('sub_station_circuit_radio') == 'existing' and request.POST.get('sub_station_circuit'):
            circuit_id = request.POST.get('sub_station_circuit')
            circuit_instance = Circuit.objects.get(id=circuit_id)
        else:
            circuit_instance = None

        if self.object and len(self.object.circuit_set.all()) == 1:
            circuit = self.object.circuit_set.all()[0]
            circuit_instance = circuit
            if circuit.sub_station:
                sub_station_instance = circuit.sub_station
            if circuit.customer:
                customer_instance = circuit.customer

        sub_station_form = self.get_form(self.get_form_class())

        form_kwargs.update({'instance': antenna_instance})
        antenna_form = self.antenna_form_class(**form_kwargs)

        form_kwargs.update({'instance': customer_instance})
        customer_form = self.customer_form_class(**form_kwargs)

        form_kwargs.update({'instance': circuit_instance})
        circuit_form = self.circuit_form_class(**form_kwargs)

        if (sub_station_form.is_valid() and antenna_form.is_valid() and customer_form.is_valid() and circuit_form.is_valid()):
            return self.form_valid(sub_station_form, antenna_form, customer_form, circuit_form)
        else:
            return self.form_invalid(sub_station_form, antenna_form, customer_form, circuit_form)

    def form_valid(self, sub_station_form, antenna_form, customer_form, circuit_form):
        form_kwargs = self.get_form_kwargs()
        base_station = BaseStation.objects.get(id=self.kwargs['bs_pk'])
        sector = Sector.objects.get(id=self.kwargs['sector_pk'])
        technology = self.kwargs['selected_technology']
        device_id = form_kwargs['data']['device']
        device = Device.objects.get(id=device_id)

        antenna = antenna_form.save(commit=False)
        antenna.name = device.ip_address
        antenna.alias = device.ip_address
        antenna.organization = base_station.organization
        antenna.save()

        self.object = sub_station_form.save(commit=False)
        self.object.name = device.ip_address
        self.object.alias = device.ip_address
        self.object.organization = base_station.organization
        self.object.antenna = antenna
        self.object.save()

        customer = customer_form.save(commit=False)
        customer.name = form_kwargs['data']['alias']
        customer.organization = base_station.organization
        customer.save()

        circuit = circuit_form.save(commit=False)
        circuit.name = form_kwargs['data']['circuit_id']
        circuit.alias = form_kwargs['data']['circuit_id']
        circuit.organization = base_station.organization
        circuit.sector = sector
        circuit.customer = customer
        circuit.sub_station = self.object
        circuit.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, sub_station_form, antenna_form, customer_form, circuit_form):
        return self.render_to_response(self.get_context_data(form=sub_station_form, sub_station_antenna_form=antenna_form, customer_form=customer_form, circuit_form=circuit_form))


class GisWizardSubStationCreateView(GisWizardSubStationMixin, SubStationCreate):
    pass


class GisWizardSubStationUpdateView(GisWizardSubStationMixin, SubStationUpdate):
    pass

#************************************** Gis Wizard Start With PTP ****************************

class GisWizardPTPListView(SectorList):
    template_name = 'gis_wizard/wizard_list_ptp.html'


class GisWizardPTPListingTable(SectorListingTable):

    def get_initial_queryset(self):
        qs=super(GisWizardPTPListingTable, self).get_initial_queryset()
        qs = qs.filter(bs_technology__name='p2p')
        return qs

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
            sector = Sector.objects.get(id=device_id)
            if self.request.user.has_perm('inventory.change_sector'):
                edit_action = '<a href="/gis-wizard/base-station/{0}/technology/{1}/sector/{2}/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(sector.base_station.id, sector.bs_technology.id , device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_sector'):
                delete_action = ''#'<a href="/sector/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data


class GisWizardSubStationListView(SubStationList):

    template_name = 'gis_wizard/wizard_list_sub-station.html'


class GisWizardSubStationListingTable(SubStationListingTable):

    def get_initial_queryset(self):

        qs = super(GisWizardSubStationListingTable, self).get_initial_queryset()
        qs = qs.filter(device__device_technology__in=[3,4])
        return qs

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
            sub_station = SubStation.objects.get(id=device_id)
            if self.request.user.has_perm('inventory.change_substation') and len(sub_station.circuit_set.all())==1:
                edit_action = '<a href="/gis-wizard/base-station/{0}/technology/{1}/sector/{2}/sub-station/{3}/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(sub_station.circuit_set.all()[0].sector.base_station.id, sub_station.circuit_set.all()[0].sector.bs_technology.id, sub_station.circuit_set.all()[0].sector.id, device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('inventory.delete_substation'):
                delete_action = '<a href="/sub_station/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data

