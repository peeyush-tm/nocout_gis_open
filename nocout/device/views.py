# -*- coding: utf-8 -*-
import json
from operator import itemgetter
from django.contrib.auth.models import User
from django.db.models.query import ValuesQuerySet
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.core.urlresolvers import reverse_lazy, reverse
from datetime import datetime, timedelta
from device.models import Device, DeviceType, DeviceTypeFields, DeviceTypeFieldsValue, DeviceTechnology, \
    TechnologyVendor, DeviceVendor, VendorModel, DeviceModel, ModelType, DevicePort, Country, State, City, \
    DeviceFrequency, DeviceTypeService, DeviceSyncHistory
from forms import DeviceForm, DeviceTypeFieldsForm, DeviceTypeFieldsUpdateForm, DeviceTechnologyForm, \
    DeviceVendorForm, DeviceModelForm, DevicePortForm, DeviceFrequencyForm, \
    CountryForm, StateForm, CityForm, DeviceTypeServiceCreateFormset, DeviceTypeServiceUpdateFormset, \
    WizardDeviceTypeForm, WizardDeviceTypeServiceForm, DeviceTypeServiceDataSourceCreateFormset, \
    DeviceTypeServiceDataSourceUpdateFormset, DeviceSyncHistoryEditForm
from django.http.response import HttpResponseRedirect, HttpResponse
from organization.models import Organization
from service.models import Service
from django.shortcuts import render_to_response
from django.template import RequestContext
from site_instance.models import SiteInstance
from inventory.models import Backhaul, SubStation, Sector
from django.contrib.staticfiles.templatetags.staticfiles import static
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.permissions import PermissionsRequiredMixin, SuperUserRequiredMixin
from nocout.mixins.generics import FormRequestMixin
from nocout.mixins.datatable import DatatableSearchMixin, DatatableOrganizationFilterMixin, ValuesQuerySetMixin, AdvanceFilteringMixin
from nocout.mixins.select2 import Select2Mixin
from django.db.models import Q
# Import inventory utils gateway class
from inventory.utils.util import InventoryUtilsGateway
from scheduling_management.models import Event
import logging
from user_profile.utils.auth import in_group

logger = logging.getLogger(__name__)

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()

# ***************************************** Device Views ********************************************
class SelectDeviceListView(Select2Mixin, ListView):
    """
    Provide selector data for jquery select2 when loading data from Remote.
    """
    model = Device
    obj_alias = 'device_alias'


class DeviceList(PermissionsRequiredMixin, ListView):
    """
    Render list of devices
    """
    model = Device
    template_name = 'device/devices_list.html'
    required_permissions = ('device.view_device',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DeviceList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'status_icon', 'sTitle': '', 'sWidth': 'auto'},
            {'mData': 'organization__name', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'device_name', 'sTitle': 'Name', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'site_instance__name', 'sTitle': 'Site Instance', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'machine__name', 'sTitle': 'Machine', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'device_technology__name', 'sTitle': 'Device Technology', 'sWidth': 'auto',
             'sClass': 'hidden-xs'},
            {'mData': 'device_type__name', 'sTitle': 'Device Type', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'host_state', 'sTitle': 'Host State', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'mac_address', 'sTitle': 'MAC Address', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'state__state_name', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'city__city_name', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs'}, ]

        # Show 'actions' column only if user has the desired permissions
        is_edit_perm = in_group(self.request.user, 'admin', 'change_device')
        is_delete_perm = in_group(self.request.user, 'admin', 'delete_device')
        if is_edit_perm or is_delete_perm:
            datatable_headers.append({
                'mData': 'actions',
                'sTitle': 'Device Actions',
                'sWidth': '9%',
                'bSortable': False
            })

            datatable_headers.append({
                'mData': 'nms_actions',
                'sTitle': 'NMS Actions',
                'sWidth': '8%',
                'bSortable': False
            })

        datatable_headers_no_nms_actions = [
            {'mData': 'status_icon', 'sTitle': '', 'sWidth': 'auto', },
            {'mData': 'organization__name', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'device_name', 'sTitle': 'Name', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'site_instance__name', 'sTitle': 'Site Instance', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'machine__name', 'sTitle': 'Machine', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'device_technology__name', 'sTitle': 'Device Technology', 'sWidth': 'auto',
             'sClass': 'hidden-xs'},
            {'mData': 'device_type__name', 'sTitle': 'Device Type', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'host_state', 'sTitle': 'Host State', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'mac_address', 'sTitle': 'MAC Address', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'state__state_name', 'sTitle': 'State', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'city__city_name', 'sTitle': 'City', 'sWidth': 'auto', 'sClass': 'hidden-xs'}, ]

        # if the user role is Admin then the action column will appear on the datatable
        if is_edit_perm or is_delete_perm:
            datatable_headers_no_nms_actions.append({
                'mData': 'actions',
                'sTitle': 'Device Actions',
                'sWidth': '15%',
                'bSortable': False
            })

        # get deadlock status
        deadlock_status = ""

        # get last sync run time
        last_sync_time = ""

        try:
            last_sync_status = get_current_sync_status()
            deadlock_status = last_sync_status[0]
            last_sync_time = last_sync_status[1]
        except Exception as e:
            pass

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['datatable_headers_no_nms_actions'] = json.dumps(datatable_headers_no_nms_actions)

        # show sync only if user is admin
        if in_group(self.request.user, 'admin'):
            context['deadlock_status'] = deadlock_status
            context['last_sync_time'] = last_sync_time

        return context


def create_device_tree(request):
    """
    Render tree structure for devices
    """
    templateData = {
        'username': request.user.username
    }

    return render_to_response('device/devices_tree_view.html', templateData, context_instance=RequestContext(request))


class OperationalDeviceListingTable(PermissionsRequiredMixin, DatatableOrganizationFilterMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing operational devices only
    """
    model = Device
    required_permissions = ('device.view_device',)
    # columns are used for list of fields which should be displayed on data table.
    columns = [
        'device_name', 
        'site_instance__name', 
        'machine__name', 
        'organization__name', 
        'device_technology',
        'device_type', 
        'host_state', 
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name',
        'device_alias',
        'is_monitored_on_nms'
    ]

    # order_columns is used for list of fields which is used for sorting the data table.
    order_columns = [
        '',
        'organization__name', 
        'device_name', 
        'site_instance__name', 
        'machine__name', 
        'device_technology',
        'device_type', 
        'host_state', 
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name'
    ]

    # search_columns is used for list of fields which is used for searching the data table.
    search_columns = [
        'device_alias', 
        'site_instance__name', 
        'machine__name', 
        'organization__name', 
        'host_state',
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name'
    ]

    # extra_qs_kwargs is used for filter the device using some extra fields in Mixin DatatableOrganizationFilterMixin.
    extra_qs_kwargs = {
        'is_deleted': 0,
        'is_added_to_nms__in': [1, 2]
    }

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        :param qs:
        :return qs:
        """
        
        sSearch = self.request.GET.get('search[value]', None)

        # If searched character is 3 or more than 3. Then search the entered text on the basis fields of search_columns.
        if sSearch:

            state_qs = State.objects.filter(state_name__icontains=sSearch)
            device_type_qs = DeviceType.objects.filter(name__icontains=sSearch)
            device_tech_qs = DeviceTechnology.objects.filter(name__icontains=sSearch)

            query_object = Q()
            for column in self.search_columns:
                query_object = query_object | Q(**{"%s__icontains" % column: sSearch})

            query_object = query_object | Q(state__in=state_qs) | Q(device_type__in=device_type_qs) | Q(
                device_technology__in=device_tech_qs)
            qs = qs.filter(query_object)

        return self.advance_filter_queryset(qs)

    def ordering(self, qs):
        """
        Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        :param qs:
        :return json:
        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        
        device_type_data = list()
        device_tech_data = list()
        if len(json_data):
            device_type_data = list(DeviceType.objects.all().values('id', 'name'))
            device_tech_data = list(DeviceTechnology.objects.all().values('id', 'name'))

        is_edit_perm = in_group(self.request.user, 'admin', 'change_device')
        is_delete_perm = in_group(self.request.user, 'admin', 'delete_device')
        is_sync_perm = in_group(self.request.user, 'admin', 'sync_devices')

        for dct in json_data:
            # modify device name format in datatable i.e. <device alias> (<device ip>)
            try:
                if 'device_name' in dct:
                    dct['device_name'] = "{} ({})".format(dct.get('device_alias'), dct.get('ip_address'))
            except Exception as e:
                logger.exception("Device not present. Exception: ", e.message)

            # current device in loop
            if not self.request.GET.get('is_download_request'):
                current_device = Device.objects.get(pk=dct['id'])

            try:
                # dct['device_type__name'] = DeviceType.objects.get(pk=int(dct['device_type'])).name if dct['device_type'] else ''
                dtype = filter(
                    lambda dtype: dtype if dtype.get('id') == int(dct['device_type']) else '',
                    device_type_data
                )[0].get('name')
                dct['device_type__name'] = dtype
            except Exception as e:
                dct['device_type__name'] = ""

            try:
                # dct['device_technology__name'] = DeviceTechnology.objects.get(pk=int(dct['device_technology'])).name if dct['device_technology'] else ''
                dtech = filter(
                    lambda dtech: dtech if dtech.get('id') == int(dct['device_technology']) else '',
                    device_tech_data
                )[0].get('name')
                dct['device_technology__name'] = dtech
            except Exception as e:
                dct['device_technology__name'] = ""

            if dct.get('is_monitored_on_nms') == 1:
                status_icon_color = "green-dot"
                dct.update(status_icon='<i class="fa fa-circle {0}"></i>'.format(status_icon_color))
            else:
                status_icon_color = "light-green-dot"
                dct.update(status_icon='<i class="fa fa-circle {0}"></i>'.format(status_icon_color))

            # Following are two set of links in device list view:
            # 1. Device Actions --> Device detail, edit, delete from inventory.
            # They are always present in device table if user role is 'Admin'
            # 2. NMS Actions --> Device add, sync, service add etc. from nocout nms core.
            #                    Following are the device type present in device listing:
            #                       a. backhaul configured on (from model Backhaul)
            #                       b. sector configures on (from model Sector)
            #                       c. sub-station configured on (from model SubStation)
            #                       d. others (any device, may be out of inventory)

            device_actions = ''
            device_nms_actions = ''

            # device detail action
            device_actions += '<a href="/device/{0}"><i class="fa fa-list-alt text-info" title="Detail"></i></a>'

            # view device edit action only if user has permissions
            if is_edit_perm:
                device_actions += '<a href="/device/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>'

            # view device delete action only if user has permissions
            if is_delete_perm:
                device_actions += '<a href="javascript:;" class="device_soft_delete_btn" pk="{0}"><i class="fa fa-trash-o text-danger" title="Soft Delete"></i></a>'

            if device_actions:
                dct.update(actions=device_actions.format(dct['id']))

            dct.update(nms_actions='')

            # text color
            text_color = "text-dark"
            try:
                if not self.request.GET.get('is_download_request'):
                    if len(Backhaul.objects.filter(bh_configured_on=current_device)):
                        text_color = "text-info"
                    elif len(Sector.objects.filter(sector_configured_on=current_device)) or \
                            len(Sector.objects.filter(dr_configured_on=current_device)):
                        text_color = "text-success"
                    elif SubStation.objects.get(device=current_device):
                        text_color = "text-danger"
                    else:
                        pass
            except Exception as e:
                pass

            try:
                dct.update(
                    nms_actions='<a href="javascript:;" class="nms_action view" pk="{0}"> \
                                 <i class="fa fa-list-alt {1}" title="Services Status"></i></a>\
                                 <a href="javascript:;" class="nms_action disable" pk="{0}"> \
                                 <i class="fa fa-ban {1}" title="Disable Device"></i></a>\
                                 <a href="javascript:;" class="nms_action add" pk="{0}"> \
                                 <i class="fa fa-plus {1}" title="Add Services"></i></a>\
                                 <a href="javascript:;" class="nms_action edit" pk="{0}"> \
                                 <i class="fa fa-pencil {1}" title="Edit Services"></i></a>\
                                 <a href="javascript:;" class="nms_action delete" pk="{0}"> \
                                 <i class="fa fa-minus {1}" title="Delete Services"></i></a>'.format(
                                    dct['id'], text_color
                                )
                )
            except Exception as e:
                logger.exception("Device is not a substation. %s" % e.message)

            # show sync button only if user is superuser or admin
            if is_sync_perm:
                try:
                    dct['nms_actions'] += '<a href="javascript:;" onclick="sync_devices();"> \
                                           <i class="fa fa-refresh {1}" title="Sync Device"></i> \
                                           </a>'.format(dct['id'], text_color)
                except Exception as e:
                    logger.exception("Device is not a substation. %s" % e.message)

        return json_data


class NonOperationalDeviceListingTable(DatatableOrganizationFilterMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing non-operational devices only
    """
    model = Device
    # columns are used for list of fields which should be displayed on data table.
    columns = [
        'device_name', 
        'site_instance__name', 
        'machine__name', 
        'organization__name', 
        'device_technology',
        'device_type', 
        'host_state', 
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name',
        'device_alias',
        'is_monitored_on_nms'
    ]

    # order_columns is used for list of fields which is used for sorting the data table.
    order_columns = [
        '',
        'organization__name', 
        'device_name', 
        'site_instance__name', 
        'machine__name', 
        'device_technology',
        'device_type', 
        'host_state', 
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name'
    ]

    # search_columns is used for list of fields which is used for searching the data table.
    search_columns = [
        'device_alias', 
        'site_instance__name', 
        'machine__name', 
        'organization__name', 
        'host_state',
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name'
    ]

    extra_qs_kwargs = {
        "is_deleted": 0,
        "is_monitored_on_nms": 0,
        "is_added_to_nms": 0,
        "host_state": 'Enable'
    }

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:

            state_qs = State.objects.filter(state_name__icontains=sSearch)
            device_type_qs = DeviceType.objects.filter(name__icontains=sSearch)
            device_tech_qs = DeviceTechnology.objects.filter(name__icontains=sSearch)

            query_object = Q()
            for column in self.search_columns:
                query_object = query_object | Q(**{"%s__icontains" % column: sSearch})

            query_object = query_object | Q(state__in=state_qs) | Q(device_type__in=device_type_qs) | Q(
                device_technology__in=device_tech_qs)
            qs = qs.filter(query_object)

        return self.advance_filter_queryset(qs)

    def ordering(self, qs):
        """
        Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        device_type_data = list()
        device_tech_data = list()
        if len(json_data):
            device_type_data = list(DeviceType.objects.all().values('id', 'name'))
            device_tech_data = list(DeviceTechnology.objects.all().values('id', 'name'))

        is_edit_perm = in_group(self.request.user, 'admin', 'change_device')
        is_delete_perm = in_group(self.request.user, 'admin', 'delete_device')

        for dct in json_data:
            # modify device name format in datatable i.e. <device alias> (<device ip>)
            try:
                if 'device_name' in dct:
                    # device_alias = Device.objects.get(pk=dct['id']).device_alias
                    # device_ip = Device.objects.get(pk=dct['id']).ip_address
                    dct['device_name'] = "{} ({})".format(dct.get('device_alias'), dct.get('ip_address'))
            except Exception as e:
                logger.exception("Device not present. Exception: ", e.message)

            # current device in loop
            if not self.request.GET.get('is_download_request'):
                current_device = Device.objects.get(pk=dct['id'])

            # device type name
            try:
                # dct['device_type__name'] = DeviceType.objects.get(pk=int(dct['device_type'])).name if dct['device_type'] else ''
                dtype = filter(
                    lambda dtype: dtype.get('name') if dtype.get('id') == int(dct['device_type']) else '',
                    device_type_data
                )[0].get('name')
                dct['device_type__name'] = dtype
            except Exception as e:
                dct['device_type__name'] = ""

            # device technology name
            try:
                # dct['device_technology__name'] = DeviceTechnology.objects.get(pk=int(dct['device_technology'])).name if dct['device_technology'] else ''
                dtech = filter(
                    lambda dtech: dtech.get('name') if dtech.get('id') == int(dct['device_technology']) else '',
                    device_tech_data
                )[0].get('name')
                dct['device_technology__name'] = dtech
            except Exception as e:
                dct['device_technology__name'] = ""

            dct.update(status_icon='<i class="fa fa-circle orange-dot"></i>')

            # Following are two set of links in device list view:
            # 1. Device Actions --> Device detail, edit, delete from inventory.
            # They are always present in device table if user role is 'Admin'
            # 2. NMS Actions --> Device add, sync, service add etc. from nocout nms core.
            #                    Following are the device type present in device listing:
            #                       a. backhaul configured on (from model Backhaul)
            #                       b. sector configures on (from model Sector)
            #                       c. sub-station configured on (from model SubStation)
            #                       d. others (any device, may be out of inventory)

            device_actions = ''
            device_nms_actions = ''

            # device detail action
            device_actions += '<a href="/device/{0}"><i class="fa fa-list-alt text-info" title="Detail"></i></a>'

            # view device edit action only if user has permissions
            if is_edit_perm:
                device_actions += '<a href="/device/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>'

            # view device delete action only if user has permissions
            if is_delete_perm:
                device_actions += '<a href="javascript:;" class="device_soft_delete_btn" pk="{0}"><i class="fa fa-trash-o text-danger" title="Soft Delete"></i></a>'

            if device_actions:
                dct.update(actions=device_actions.format(dct['id']))

            dct.update(nms_actions='')

            # text color
            text_color = "text-dark"
            try:
                if not self.request.GET.get('is_download_request'):
                    if len(Backhaul.objects.filter(bh_configured_on=current_device)):
                        text_color = "text-info"
                    elif len(Sector.objects.filter(sector_configured_on=current_device)) or \
                            len(Sector.objects.filter(dr_configured_on=current_device)):
                        text_color = "text-success"
                    elif SubStation.objects.get(device=current_device):
                        text_color = "text-danger"
                    else:
                        pass
            except Exception as e:
                pass

            # update nms actions
            try:
                dct.update(
                    nms_actions='<a href="javascript:;" class="device_add_to_nms_form_btn" pk="{0}"><i class="fa fa-plus-square {1}" title="Add device to NMS."></i></a>'.format(dct['id'], text_color)
                )
            except Exception as e:
                pass

        return json_data


class DisabledDeviceListingTable(DatatableOrganizationFilterMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing disabled devices only
    """
    model = Device

    # columns are used for list of fields which should be displayed on data table.
    columns = [
        'device_name', 
        'site_instance__name', 
        'machine__name', 
        'organization__name', 
        'device_technology',
        'device_type', 
        'host_state', 
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name',
        'device_alias',
        'is_monitored_on_nms'
    ]

    # order_columns is used for list of fields which is used for sorting the data table.
    order_columns = [
        '',
        'organization__name', 
        'device_name', 
        'site_instance__name', 
        'machine__name', 
        'device_technology',
        'device_type', 
        'host_state', 
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name'
    ]

    # search_columns is used for list of fields which is used for searching the data table.
    search_columns = [
        'device_alias', 
        'site_instance__name', 
        'machine__name', 
        'organization__name', 
        'host_state',
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name'
    ]

    extra_qs_kwargs = {
        "is_deleted": 0,
        "host_state": 'Disable'
    }

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:

            state_qs = State.objects.filter(state_name__icontains=sSearch)
            device_type_qs = DeviceType.objects.filter(name__icontains=sSearch)
            device_tech_qs = DeviceTechnology.objects.filter(name__icontains=sSearch)

            query_object = Q()
            for column in self.search_columns:
                query_object = query_object | Q(**{"%s__icontains" % column: sSearch})

            query_object = query_object | Q(state__in=state_qs) | Q(device_type__in=device_type_qs) | Q(
                device_technology__in=device_tech_qs)
            qs = qs.filter(query_object)

        return self.advance_filter_queryset(qs)

    def ordering(self, qs):
        """
        Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        device_type_data = list()
        device_tech_data = list()
        if len(json_data):
            device_type_data = list(DeviceType.objects.all().values('id', 'name'))
            device_tech_data = list(DeviceTechnology.objects.all().values('id', 'name'))

        is_edit_perm = in_group(self.request.user, 'admin', 'change_device')
        is_delete_perm = in_group(self.request.user, 'admin', 'delete_device')

        for dct in json_data:
            # modify device name format in datatable i.e. <device alias> (<device ip>)
            try:
                if 'device_name' in dct:
                    # device_alias = Device.objects.get(pk=dct['id']).device_alias
                    # device_ip = Device.objects.get(pk=dct['id']).ip_address
                    dct['device_name'] = "{} ({})".format(dct.get('device_alias'), dct.get('ip_address'))
            except Exception as e:
                logger.exception("Device not present. Exception: ", e.message)

            # current device in loop
            if not self.request.GET.get('is_download_request'):
                current_device = Device.objects.get(pk=dct['id'])

            # device type name
            try:
                # dct['device_type__name'] = DeviceType.objects.get(pk=int(dct['device_type'])).name if dct['device_type'] else ''
                dtype = filter(
                    lambda dtype: dtype.get('name') if dtype.get('id') == int(dct['device_type']) else '',
                    device_type_data
                )[0].get('name')
                dct['device_type__name'] = dtype
            except Exception as e:
                dct['device_type__name'] = ""

            # device technology name
            try:
                # dct['device_technology__name'] = DeviceTechnology.objects.get(pk=int(dct['device_technology'])).name if dct['device_technology'] else ''
                dtech = filter(
                    lambda dtech: dtech.get('name') if dtech.get('id') == int(dct['device_technology']) else '',
                    device_tech_data
                )[0].get('name')
                dct['device_technology__name'] = dtech
            except Exception as e:
                dct['device_technology__name'] = ""

            dct.update(status_icon='<i class="fa fa-circle orange-dot"></i>')

            # Following are two set of links in device list view:
            # 1. Device Actions --> Device detail, edit, delete from inventory.
            # They are always present in device table if user role is 'Admin'
            # 2. NMS Actions --> Device add, sync, service add etc. from nocout nms core.
            #                    Following are the device type present in device listing:
            #                       a. backhaul configured on (from model Backhaul)
            #                       b. sector configures on (from model Sector)
            #                       c. sub-station configured on (from model SubStation)
            #                       d. others (any device, may be out of inventory)


            device_actions = ''
            device_nms_actions = ''

            # device detail action
            device_actions += '<a href="/device/{0}"><i class="fa fa-list-alt text-info" title="Detail"></i></a>'

            # view device edit action only if user has permissions
            if is_edit_perm:
                device_actions += '<a href="/device/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>'

            # view device delete action only if user has permissions
            if is_delete_perm:
                device_actions += '<a href="javascript:;" class="device_soft_delete_btn" pk="{0}"><i class="fa fa-trash-o text-danger" title="Soft Delete"></i></a>'

            if device_actions:
                dct.update(actions=device_actions.format(dct['id']))

            dct.update(nms_actions='')

            # text color
            text_color = "text-dark"
            try:
                if not self.request.GET.get('is_download_request'):
                    if len(Backhaul.objects.filter(bh_configured_on=current_device)):
                        text_color = "text-info"
                    elif len(Sector.objects.filter(sector_configured_on=current_device)) or \
                            len(Sector.objects.filter(dr_configured_on=current_device)):
                        text_color = "text-success"
                    elif SubStation.objects.get(device=current_device):
                        text_color = "text-danger"
                    else:
                        pass
            except Exception as e:
                pass

            # update nms actions
            try:
                dct.update(nms_actions='<a href="javascript:;" onclick="modify_device_state({0});"><i class="fa fa-check {1}" title="Enable Device"></i></a>'.format(
                    dct['id'], text_color))
            except Exception as e:
                pass

        return json_data


class ArchivedDeviceListingTable(DatatableOrganizationFilterMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing archived devices only
    """

    model = Device

    # columns are used for list of fields which should be displayed on data table.
    columns = [
        'device_name', 
        'site_instance__name', 
        'machine__name', 
        'organization__name', 
        'device_technology',
        'device_type', 
        'host_state', 
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name',
        'device_alias',
        'is_monitored_on_nms'
    ]

    # order_columns is used for list of fields which is used for sorting the data table.
    order_columns = [
        '',
        'organization__name', 
        'device_name', 
        'site_instance__name', 
        'machine__name', 
        'device_technology',
        'device_type', 
        'host_state', 
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name'
    ]

    # search_columns is used for list of fields which is used for searching the data table.
    search_columns = [
        'device_alias', 
        'site_instance__name', 
        'machine__name', 
        'organization__name', 
        'host_state',
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name'
    ]

    extra_qs_kwargs = {
        'is_deleted': 1
    }

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:

            state_qs = State.objects.filter(state_name__icontains=sSearch)
            device_type_qs = DeviceType.objects.filter(name__icontains=sSearch)
            device_tech_qs = DeviceTechnology.objects.filter(name__icontains=sSearch)

            query_object = Q()
            for column in self.search_columns:
                query_object = query_object | Q(**{"%s__icontains" % column: sSearch})

            query_object = query_object | Q(state__in=state_qs) | Q(device_type__in=device_type_qs) | Q(
                device_technology__in=device_tech_qs)
            qs = qs.filter(query_object)

        return self.advance_filter_queryset(qs)

    def ordering(self, qs):
        """
        Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        device_type_data = list()
        device_tech_data = list()
        if len(json_data):
            device_type_data = list(DeviceType.objects.all().values('id', 'name'))
            device_tech_data = list(DeviceTechnology.objects.all().values('id', 'name'))

        # device object
        device = None

        is_add_perm = in_group(self.request.user, 'admin', 'add_device')
        is_edit_perm = in_group(self.request.user, 'admin', 'change_device')
        is_delete_perm = in_group(self.request.user, 'admin', 'delete_device')

        for dct in json_data:
            # modify device name format in datatable i.e. <device alias> (<device ip>)
            try:
                if 'device_name' in dct:
                    # device_alias = Device.objects.get(pk=dct['id']).device_alias
                    # device_ip = Device.objects.get(pk=dct['id']).ip_address
                    dct['device_name'] = "{} ({})".format(dct.get('device_alias'), dct.get('ip_address'))
            except Exception as e:
                logger.exception("Device not present. Exception: ", e.message)

            # device type name
            try:
                # dct['device_type__name'] = DeviceType.objects.get(pk=int(dct['device_type'])).name if dct['device_type'] else ''
                dtype = filter(
                    lambda dtype: dtype.get('name') if dtype.get('id') == int(dct['device_type']) else '',
                    device_type_data
                )[0].get('name')
                dct['device_type__name'] = dtype
            except Exception as e:
                dct['device_type__name'] = ""

            # device technology name
            try:
                # dct['device_technology__name'] = DeviceTechnology.objects.get(pk=int(dct['device_technology'])).name if dct['device_technology'] else ''
                dtech = filter(
                    lambda dtech: dtech.get('name') if dtech.get('id') == int(dct['device_technology']) else '',
                    device_tech_data
                )[0].get('name')
                dct['device_technology__name'] = dtech
            except Exception as e:
                dct['device_technology__name'] = ""

            # update status icon
            dct.update(status_icon='<i class="fa fa-circle red-dot"></i>')


            device_actions = ''
            device_nms_actions = ''

            if is_add_perm:
                device_actions += '<a href="javascript:;" pk="{0}" class="nms_action restore"><i class="fa fa-plus green-dot" title="Restore"></i></a>'

            # device detail action
            device_actions += '<a href="/device/{0}"><i class="fa fa-list-alt text-info" title="Detail"></i></a>'

            # view device edit action only if user has permissions
            if is_edit_perm:
                device_actions += '<a href="/device/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>'

            # view device delete action only if user has permissions
            if is_delete_perm:
                device_actions += '<a href="/device/{0}/delete/"><i class="fa fa-trash-o text-dark" title="Delete"></i></a>'

            if device_actions:
                dct.update(actions=device_actions.format(dct['id']))

        return json_data


class AllDeviceListingTable(DatatableOrganizationFilterMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of all devices
    """
    model = Device

    # columns are used for list of fields which should be displayed on data table.
    columns = [
        'device_name', 
        'site_instance__name', 
        'machine__name', 
        'organization__name', 
        'device_technology',
        'device_type', 
        'host_state', 
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name',
        'device_alias',
        'is_monitored_on_nms'
    ]

    # order_columns is used for list of fields which is used for sorting the data table.
    order_columns = [
        '',
        'organization__name', 
        'device_name', 
        'site_instance__name', 
        'machine__name', 
        'device_technology',
        'device_type', 
        'host_state', 
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name'
    ]

    # search_columns is used for list of fields which is used for searching the data table.
    search_columns = [
        'device_alias', 
        'site_instance__name', 
        'machine__name', 
        'organization__name', 
        'host_state',
        'ip_address', 
        'mac_address', 
        'state__state_name', 
        'city__city_name'
    ]

    extra_qs_kwargs = {
        'is_deleted': 0
    }

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:

            state_qs = State.objects.filter(state_name__icontains=sSearch)
            device_type_qs = DeviceType.objects.filter(name__icontains=sSearch)
            device_tech_qs = DeviceTechnology.objects.filter(name__icontains=sSearch)

            query_object = Q()
            for column in self.search_columns:
                query_object = query_object | Q(**{"%s__icontains" % column: sSearch})

            query_object = query_object | Q(state__in=state_qs) | Q(device_type__in=device_type_qs) | Q(
                device_technology__in=device_tech_qs)
            qs = qs.filter(query_object)

        return self.advance_filter_queryset(qs)

    def ordering(self, qs):
        """
        Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        
        device_type_data = list()
        device_tech_data = list()
        if len(json_data):
            device_type_data = list(DeviceType.objects.all().values('id', 'name'))
            device_tech_data = list(DeviceTechnology.objects.all().values('id', 'name'))

        is_edit_perm = in_group(self.request.user, 'admin', 'change_device')
        is_delete_perm = in_group(self.request.user, 'admin', 'delete_device')
        
        for dct in json_data:
            # modify device name format in datatable i.e. <device alias> (<device ip>)
            try:
                if 'device_name' in dct:
                    # device_alias = Device.objects.get(pk=dct['id']).device_alias
                    # device_ip = Device.objects.get(pk=dct['id']).ip_address
                    dct['device_name'] = "{} ({})".format(dct.get('device_alias'), dct.get('ip_address'))
            except Exception as e:
                logger.exception("Device not present. Exception: ", e.message)

            # current device in loop
            if not self.request.GET.get('is_download_request'):
                current_device = Device.objects.get(pk=dct['id'])

            # device type name
            try:
                # dct['device_type__name'] = DeviceType.objects.get(pk=int(dct['device_type'])).name if dct['device_type'] else ''
                dtype = filter(
                    lambda dtype: dtype if dtype.get('id') == int(dct['device_type']) else '',
                    device_type_data
                )[0].get('name')
                dct['device_type__name'] = dtype
            except Exception as e:
                dct['device_type__name'] = ""

            # device technology name
            try:
                # dct['device_technology__name'] = DeviceTechnology.objects.get(pk=int(dct['device_technology'])).name if dct['device_technology'] else ''
                dtech = filter(
                    lambda dtech: dtech if dtech.get('id') == int(dct['device_technology']) else '',
                    device_tech_data
                )[0].get('name')
                dct['device_technology__name'] = dtech
            except Exception as e:
                dct['device_technology__name'] = ""

            # if device is already added to nms core than show icon in device table
            icon = ""
            try:
                if not self.request.GET.get('is_download_request'):
                    if current_device.is_added_to_nms == 0 and current_device.host_state == "Enable":
                        icon = '<i class="fa fa-circle orange-dot"></i>'
                    elif current_device.is_added_to_nms == 0 and current_device.host_state == "Disable":
                        icon = '<i class="fa fa-circle grey-dot"></i>'
                    elif current_device.is_added_to_nms == 1:
                        icon = '<i class="fa fa-circle green-dot"></i>'
                    elif current_device.is_added_to_nms == 2:
                        icon = '<i class="fa fa-circle green-dot"></i>'
                dct.update(status_icon=icon)
            except Exception as e:
                dct.update(status_icon='<img src="">')


            device_actions = ''

            # device detail action
            device_actions += '<a href="/device/{0}"><i class="fa fa-list-alt text-info" title="Detail"></i></a>'

            # view device edit action only if user has permissions
            if is_edit_perm:
                device_actions += '<a href="/device/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>'

            # view device delete action only if user has permissions
            if is_delete_perm:
                device_actions += '<a href="javascript:;" class="device_soft_delete_btn" pk="{0}"> \
                                   <i class="fa fa-trash-o text-danger" title="Soft Delete"></i></a>'

            if device_actions:
                dct.update(actions=device_actions.format(dct['id']))

            dct.update(nms_actions='')

        return json_data


class DeviceDetail(PermissionsRequiredMixin, DetailView):
    """
    Render detail view for device
    """
    model = Device
    required_permissions = ('device.view_device',)
    template_name = 'device/device_detail.html'

    def get_context_data(self, **kwargs):

        context = super(DeviceDetail, self).get_context_data(**kwargs)

        try:
            if kwargs['object'].device_technology:
                context['device_technology'] = DeviceTechnology.objects.get(pk=kwargs['object'].device_technology).alias
            if kwargs['object'].device_vendor:
                context['device_vendor'] = DeviceVendor.objects.get(pk=kwargs['object'].device_vendor).alias
            if kwargs['object'].device_model:
                context['device_model'] = DeviceModel.objects.get(pk=kwargs['object'].device_model).alias
            if kwargs['object'].device_type:
                context['device_type'] = DeviceType.objects.get(pk=kwargs['object'].device_type).alias
        except Exception as e:
            logger.exception(e.message)

        return context


class DeviceCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Render device create view
    """
    template_name = 'device/device_new.html'
    model = Device
    form_class = DeviceForm
    success_url = reverse_lazy('device_list')
    required_permissions = ('device.add_device',)

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

        # id of last inserted row in 'device' model
        device_latest_id = 1

        # get device latest inserted in schema
        try:
            id_list = [Device.objects.latest('id').id, int(Device.objects.latest('id').device_name)]
            device_latest_id = max(id_list) + 1
        except Exception as e:
            logger.exception("No device is added in database till now. Exception: ", e.message)

        # saving device data
        device = Device()
        device.device_name = device_latest_id
        device.device_alias = form.cleaned_data['device_alias']
        device.machine = form.cleaned_data['machine']
        device.site_instance = form.cleaned_data['site_instance']
        device.organization_id = form.cleaned_data['organization'].id
        device.device_technology = form.cleaned_data['device_technology']
        device.device_vendor = form.cleaned_data['device_vendor']
        device.device_model = form.cleaned_data['device_model']
        device.device_type = form.cleaned_data['device_type']
        if 'parent' in form.cleaned_data:
            device.parent = form.cleaned_data['parent']
        device.ip_address = form.cleaned_data['ip_address']
        device.mac_address = form.cleaned_data['mac_address']
        device.netmask = form.cleaned_data['netmask']
        device.gateway = form.cleaned_data['gateway']
        device.dhcp_state = form.cleaned_data['dhcp_state']
        device.host_priority = form.cleaned_data['host_priority']
        device.host_state = form.cleaned_data['host_state']
        device.latitude = form.cleaned_data['latitude']
        device.longitude = form.cleaned_data['longitude']
        device.timezone = form.cleaned_data['timezone']
        device.country = form.cleaned_data['country']
        device.state = form.cleaned_data['state']
        device.city = form.cleaned_data['city']
        device.address = form.cleaned_data['address']
        device.description = form.cleaned_data['description']
        device.save()

        # saving associated ports  --> M2M Relation (Model: DevicePort)
        for port in form.cleaned_data['ports']:
            device_port = DevicePort.objects.get(name=port)
            device.ports.add(device_port)
            device.save()

        # fetching device extra fields associated with 'device type'
        try:
            device_type = DeviceType.objects.get(id=int(self.request.POST.get('device_type')))
            # it gives all device fields associated with device_type object
            device_type.devicetypefields_set.all()
        except Exception as e:
            logger.exception(e.message)

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
            except Exception as e:
                logger.exception(e.message)
        return HttpResponseRedirect(DeviceCreate.success_url)


class DeviceUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
    """
    Render device update view
    """
    template_name = 'device/device_update.html'
    model = Device
    form_class = DeviceForm
    success_url = reverse_lazy('device_list')
    required_permissions = ('device.change_device',)

    def get_queryset(self):

        return Device.objects.filter(organization__in=nocout_utils.logged_in_user_organizations(self))

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
        # self.object.device_name = form.cleaned_data['device_name']
        self.object.device_alias = form.cleaned_data['device_alias']
        self.object.machine = form.cleaned_data['machine']
        self.object.site_instance = form.cleaned_data['site_instance']
        self.object.organization_id = form.cleaned_data['organization']
        self.object.device_technology = form.cleaned_data['device_technology']
        self.object.device_vendor = form.cleaned_data['device_vendor']
        self.object.device_model = form.cleaned_data['device_model']
        self.object.device_type = form.cleaned_data['device_type']
        if 'parent' in form.cleaned_data:
            self.object.parent = form.cleaned_data['parent']
        self.object.ip_address = form.cleaned_data['ip_address']
        self.object.mac_address = form.cleaned_data['mac_address']
        self.object.netmask = form.cleaned_data['netmask']
        self.object.gateway = form.cleaned_data['gateway']
        self.object.dhcp_state = form.cleaned_data['dhcp_state']
        self.object.host_priority = form.cleaned_data['host_priority']
        self.object.host_state = form.cleaned_data['host_state']
        self.object.latitude = form.cleaned_data['latitude']
        self.object.longitude = form.cleaned_data['longitude']
        self.object.timezone = form.cleaned_data['timezone']
        self.object.country = form.cleaned_data['country']
        self.object.state = form.cleaned_data['state']
        self.object.city = form.cleaned_data['city']
        self.object.address = form.cleaned_data['address']
        self.object.description = form.cleaned_data['description']
        self.object.organization = form.cleaned_data['organization']
        self.object.save()

        # delete old ports
        self.object.ports.clear()

        # saving associated ports  --> M2M Relation (Model: DevicePort)
        for port in form.cleaned_data['ports']:
            device_port = DevicePort.objects.get(name=port)
            self.object.ports.add(device_port)
            self.object.save()

        # deleting old device extra field values
        try:
            DeviceTypeFieldsValue.objects.filter(device_id=self.object.id).delete()
        except Exception as e:
            logger.exception(e.message)

        # fetching device extra fields associated with 'device type'
        try:
            device_type = DeviceType.objects.get(id=int(self.request.POST.get('device_type')))
            # it gives all device fields associated with device_type object
            device_type.devicetypefields_set.all()
        except Exception as e:
            logger.exception(e.message)

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
            except Exception as e:
                logger.exception(e.message)

        # dictionary containing old values of current device
        initial_field_dict = form.initial

        # if 'site_instance' value is changed and 'is_added_to_nms' is 1 than set 'is_added_to_nms' to 2
        try:
            if (initial_field_dict['site_instance'] != form.cleaned_data['site_instance'].id) and (
                        self.object.is_added_to_nms == 1):
                self.object.is_added_to_nms = 2
                self.object.save()
        except Exception as e:
            logger.exception(e.message)

        # if 'ip_address' value is changed and 'is_added_to_nms' is 1 than set 'is_added_to_nms' to 2
        try:
            if (initial_field_dict['ip_address'] != form.cleaned_data['ip_address']) and (
                        self.object.is_added_to_nms == 1):
                self.object.is_added_to_nms = 2
                self.object.save()
        except Exception as e:
            logger.exception(e.message)

        def cleaned_data_field():
            """
            Clean data after submitting the form
            """
            cleaned_data_field_dict = {}
            for field in form.cleaned_data.keys():
                # if field in ('parent', 'site_instance', 'organization'):
                if field in ('site_instance', 'organization'):
                    cleaned_data_field_dict[field] = form.cleaned_data[field].pk if form.cleaned_data[field] else None
                elif field in ('device_model', 'device_type', 'device_vendor', 'device_technology') and \
                        form.cleaned_data[field]:
                    cleaned_data_field_dict[field] = int(form.cleaned_data[field])
                else:
                    cleaned_data_field_dict[field] = form.cleaned_data[field]

            return cleaned_data_field_dict

        cleaned_data_field_dict = cleaned_data_field()

        changed_fields_dict = nocout_utils.init_dict_differ_changed(initial_field_dict, cleaned_data_field_dict)
        try:
            if changed_fields_dict:
                # initial_field_dict['parent'] = Device.objects.get(pk=initial_field_dict['parent']).device_name \
                #     if initial_field_dict['parent'] else str(None)
                initial_field_dict['organization'] = Organization.objects.get(
                    pk=initial_field_dict['organization']).name \
                    if initial_field_dict['organization'] else str(None)
                initial_field_dict['site_instance'] = SiteInstance.objects.get(
                    pk=initial_field_dict['site_instance']).name \
                    if initial_field_dict['site_instance'] else str(None)
                initial_field_dict['device_model'] = DeviceModel.objects.get(pk=initial_field_dict['device_model']).name \
                    if initial_field_dict['device_model'] else str(None)
                initial_field_dict['device_type'] = DeviceType.objects.get(pk=initial_field_dict['device_type']).name \
                    if initial_field_dict['device_type'] else str(None)
                initial_field_dict['device_vendor'] = DeviceVendor.objects.get(
                    pk=initial_field_dict['device_vendor']).name \
                    if initial_field_dict['device_vendor'] else str(None)
                initial_field_dict['device_technology'] = DeviceTechnology.objects.get(
                    pk=initial_field_dict['device_technology']).name \
                    if initial_field_dict['device_technology'] else str(None)

                cleaned_data_field_dict['parent'] = Device.objects.get(pk=cleaned_data_field_dict['parent']).device_name \
                    if cleaned_data_field_dict['parent'] else str(None)
                cleaned_data_field_dict['organization'] = Organization.objects.get(
                    pk=cleaned_data_field_dict['organization']).name \
                    if cleaned_data_field_dict['organization'] else str(None)
                cleaned_data_field_dict['site_instance'] = SiteInstance.objects.get(
                    pk=cleaned_data_field_dict['site_instance']).name \
                    if cleaned_data_field_dict['site_instance'] else str(None)
                cleaned_data_field_dict['device_model'] = DeviceModel.objects.get(
                    pk=cleaned_data_field_dict['device_model']).name \
                    if cleaned_data_field_dict['device_model'] else str(None)
                cleaned_data_field_dict['device_type'] = DeviceType.objects.get(
                    pk=cleaned_data_field_dict['device_type']).name \
                    if cleaned_data_field_dict['device_type'] else str(None)
                cleaned_data_field_dict['device_vendor'] = DeviceVendor.objects.get(
                    pk=cleaned_data_field_dict['device_vendor']).name \
                    if cleaned_data_field_dict['device_vendor'] else str(None)
                cleaned_data_field_dict['device_technology'] = DeviceTechnology.objects.get(
                    pk=cleaned_data_field_dict['device_technology']).name \
                    if cleaned_data_field_dict['device_technology'] else str(None)

                verb_string = 'Changed values of Device %s from initial values ' % (
                    self.object.device_name) + ', '.join(['%s: %s' % (k, initial_field_dict[k]) \
                                                          for k in changed_fields_dict]) + \
                              ' to ' + \
                              ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
                if len(verb_string) >= 255:
                    verb_string = verb_string[:250] + '...'

        except Exception as user_audit_exeption:
            logger.exception(user_audit_exeption.message)

        return HttpResponseRedirect(DeviceCreate.success_url)


class DeviceDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render device delete view
    """
    model = Device
    required_permissions = ('device.delete_device',)
    template_name = 'device/device_delete.html'
    success_url = reverse_lazy('device_list')
    obj_alias = 'device_alias'


# ******************************** Device Type Form Fields Views ************************************


class DeviceTypeFieldsList(PermissionsRequiredMixin, ListView):
    """
    Render list of device type extra fields
    """
    model = DeviceTypeFields
    template_name = 'device_extra_fields/device_extra_fields_list.html'
    required_permissions = ('device.view_devicetypefields',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DeviceTypeFieldsList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'field_name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'field_display_name', 'sTitle': 'Field Display Name', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'device_type__name', 'sTitle': 'Device Type', 'sWidth': 'auto'},
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DeviceTypeFieldsListingTable(PermissionsRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of device type fields
    """
    model = DeviceTypeFields
    required_permissions = ('device.view_devicetypefields',)
    columns = ['field_name', 'field_display_name', 'device_type__name']
    order_columns = ['field_name', 'field_display_name', 'device_type__name']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            result_list = list()
            for dictionary in qs:

                x = json.dumps(dictionary)
                dictionary = json.loads(x)

                for dict in dictionary:
                    if dictionary[dict]:
                        if (isinstance(dictionary[dict], unicode) or isinstance(dictionary[dict], str)) and (
                                    dictionary not in result_list
                        ):
                            if sSearch.encode('utf-8').lower() in dictionary[dict].encode('utf-8').lower():
                                result_list.append(dictionary)
                        else:
                            if sSearch == dictionary[dict] and dictionary not in result_list:
                                result_list.append(dictionary)
            # advance filtering the query set
            return self.advance_filter_queryset(result_list)
        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DeviceTypeFields.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/device_fields/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/device_fields/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
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


class DeviceTypeFieldsDetail(PermissionsRequiredMixin, DetailView):
    """
    Render detail view for device extra field
    """
    model = DeviceTypeFields
    required_permissions = ('device.view_devicetypefields',)
    template_name = 'device_extra_fields/device_extra_field_detail.html'


class DeviceTypeFieldsCreate(PermissionsRequiredMixin, CreateView):
    """
    Render device type field create view
    """
    template_name = 'device_extra_fields/device_extra_field_new.html'
    model = DeviceTypeFields
    form_class = DeviceTypeFieldsForm
    success_url = reverse_lazy('device_extra_field_list')
    required_permissions = ('device.add_devicetypefieldsvalue',)


class DeviceTypeFieldsUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Render device type fields update view
    """
    template_name = 'device_extra_fields/device_extra_field_update.html'
    model = DeviceTypeFields
    form_class = DeviceTypeFieldsUpdateForm
    success_url = reverse_lazy('device_extra_field_list')
    required_permissions = ('device.change_devicetypefieldsvalue',)


class DeviceTypeFieldsDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render device type field delete view
    """
    model = DeviceTypeFields
    template_name = 'device_extra_fields/device_extra_field_delete.html'
    success_url = reverse_lazy('device_extra_field_list')
    required_permissions = ('device.delete_devicetypefieldsvalue',)
    obj_alias = 'field_display_name'


# **************************************** Device Technology ****************************************

class DeviceTechnologyList(PermissionsRequiredMixin, ListView):
    """
    Render list of technologies
    """
    model = DeviceTechnology
    template_name = 'device_technology/device_technology_list.html'
    required_permissions = ('device.view_devicetechnology',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DeviceTechnologyList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto'},
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto'},
            {'mData': 'device_vendor', 'sTitle': 'Device Vendor', 'sWidth': '10%'},
            {'mData': 'device_vendor__model__name', 'sTitle': 'Device Model', 'sWidth': '10%', },
            {'mData': 'device_vendor__model_type__name', 'sTitle': 'Device Type', 'sWidth': '10%', }
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DeviceTechnologyListingTable(PermissionsRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of device technologies
    """
    model = DeviceTechnology
    required_permissions = ('device.view_devicetechnology',)
    columns = ['name', 'alias', 'device_vendor', 'device_vendor__model__name', 'device_vendor__model_type__name']
    order_columns = ['name', 'alias', 'device_vendor', 'device_vendor__model__name', 'device_vendor__model_type__name']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            result_list = list()
            for dictionary in qs:

                x = json.dumps(dictionary)
                dictionary = json.loads(x)

                for dict in dictionary:
                    if dictionary[dict]:
                        if (isinstance(dictionary[dict], unicode) or isinstance(dictionary[dict], str)) and (
                                    dictionary not in result_list
                        ):
                            if sSearch.encode('utf-8').lower() in dictionary[dict].encode('utf-8').lower():
                                result_list.append(dictionary)
                        else:
                            if sSearch == dictionary[dict] and dictionary not in result_list:
                                result_list.append(dictionary)
            return self.advance_filter_queryset(result_list)
        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        qs_query = DeviceTechnology.objects.prefetch_related()
        qs = list()
        for dtechnology in qs_query:
            dct = dict()
            for dtechnology_vendor in dtechnology.device_vendors.values_list('name', flat=True):
                dct = {
                    'id': dtechnology.id, 'name': dtechnology.name, 'alias': dtechnology.alias,
                    'device_vendor': dtechnology_vendor
                }
                dvendor = DeviceVendor.objects.get(name=dtechnology_vendor)

                dct['device_vendor__model__name'] = ', '.join(dvendor.device_models.values_list('name', flat=True))

                for dmodel in dvendor.device_models.prefetch_related():
                    dct['device_vendor__model_type__name'] = ', '.join(
                        dmodel.device_types.values_list('name', flat=True))

                qs.append(dct)
        return qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/technology/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/technology/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
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


class DeviceTechnologyDetail(PermissionsRequiredMixin, DetailView):
    """
    Render detail view for technology
    """
    model = DeviceTechnology
    required_permissions = ('device.view_devicetechnology',)
    template_name = 'device_technology/device_technology_detail.html'


class DeviceTechnologyCreate(PermissionsRequiredMixin, CreateView):
    """
    Render device technology create view
    """
    template_name = 'device_technology/device_technology_new.html'
    model = DeviceTechnology
    form_class = DeviceTechnologyForm
    success_url = reverse_lazy('device_technology_list')
    required_permissions = ('device.add_devicetechnology',)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
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


class DeviceTechnologyUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Render device technology update view
    """
    template_name = 'device_technology/device_technology_update.html'
    model = DeviceTechnology
    form_class = DeviceTechnologyForm
    success_url = reverse_lazy('device_technology_list')
    required_permissions = ('device.change_devicetechnology',)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
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
        try:
            initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}

            cleaned_data_field_dict = {field: map(lambda obj: obj.pk, form.cleaned_data[field])
            if field in ('device_vendors') and form.cleaned_data[field] else form.cleaned_data[field] for field in
                                       form.cleaned_data.keys()}

            changed_fields_dict = nocout_utils.init_dict_differ_changed(initial_field_dict, cleaned_data_field_dict)
            if changed_fields_dict:
                initial_field_dict['device_vendors'] = ', '.join(
                    [DeviceVendor.objects.get(pk=vendor).name for vendor in initial_field_dict['device_vendors']])
                cleaned_data_field_dict['device_vendors'] = ', '.join(
                    [DeviceVendor.objects.get(pk=vendor).name for vendor in cleaned_data_field_dict['device_vendors']])

                verb_string = 'Changed values of Device Technology : %s from initial values ' % (self.object.name) \
                              + ', '.join(['%s: %s' % (k, initial_field_dict[k]) for k in changed_fields_dict]) \
                              + ' to ' + \
                              ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
                if len(verb_string) >= 255:
                    verb_string = verb_string[:250] + '...'

        except Exception as activity:
            pass

        return HttpResponseRedirect(DeviceTechnologyUpdate.success_url)


class DeviceTechnologyDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render device technology delete view
    """
    model = DeviceTechnology
    template_name = 'device_technology/device_technology_delete.html'
    success_url = reverse_lazy('device_technology_list')
    required_permissions = ('device.delete_devicetechnology',)


# ************************************* Device Vendor ***********************************************
class DeviceVendorList(PermissionsRequiredMixin, ListView):
    """
    Render list of vendors
    """
    model = DeviceVendor
    template_name = 'device_vendor/device_vendor_list.html'
    required_permissions = ('device.view_devicevendor',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DeviceVendorList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'device_models', 'sTitle': 'Device Models', 'sWidth': 'auto', },
            {'mData': 'device_types', 'sTitle': 'Device Types', 'sWidth': 'auto', },
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DeviceVendorListingTable(PermissionsRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of device vendors
    """
    model = DeviceVendor
    required_permissions = ('device.view_devicevendor',)
    columns = ['name', 'alias', 'device_models', 'device_types']
    order_columns = ['name', 'alias', 'device_models', 'device_types']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            result_list = list()
            for dictionary in qs:

                x = json.dumps(dictionary)
                dictionary = json.loads(x)

                for dict in dictionary:
                    if dictionary[dict]:
                        if (isinstance(dictionary[dict], unicode) or isinstance(dictionary[dict], str)) and (
                                    dictionary not in result_list
                        ):
                            if sSearch.encode('utf-8').lower() in dictionary[dict].encode('utf-8').lower():
                                result_list.append(dictionary)
                        else:
                            if sSearch == dictionary[dict] and dictionary not in result_list:
                                result_list.append(dictionary)
            return self.advance_filter_queryset(result_list)
        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        qs = list()

        qs_query = DeviceVendor.objects.prefetch_related()
        for dvendor in qs_query:
            dct = {'id': dvendor.id,
                   'name': dvendor.name,
                   'alias': dvendor.alias,
                   'device_models': ', '.join(dvendor.device_models.values_list('name', flat=True))}
            dct['device_types'] = ''
            for dmodels in dvendor.device_models.prefetch_related():
                if dct['device_types']:
                    dct['device_types'] += ', ' + ', '.join(dmodels.device_types.values_list('name', flat=True))
                else:
                    dct['device_types'] += ', '.join(dmodels.device_types.values_list('name', flat=True))
            qs.append(dct)

        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/vendor/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/vendor/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
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


class DeviceVendorDetail(PermissionsRequiredMixin, DetailView):
    """
    Render detail view for vendor
    """
    model = DeviceVendor
    required_permissions = ('device.view_devicevendor',)
    template_name = 'device_vendor/device_vendor_detail.html'


class DeviceVendorCreate(PermissionsRequiredMixin, CreateView):
    """
    Render device vendor create view
    """
    template_name = 'device_vendor/device_vendor_new.html'
    model = DeviceVendor
    form_class = DeviceVendorForm
    success_url = reverse_lazy('device_vendor_list')
    required_permissions = ('device.add_devicevendor',)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
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


class DeviceVendorUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Render device vendor update view
    """
    template_name = 'device_vendor/device_vendor_update.html'
    model = DeviceVendor
    form_class = DeviceVendorForm
    success_url = reverse_lazy('device_vendor_list')
    required_permissions = ('device.change_devicevendor',)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
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

        try:
            initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}

            cleaned_data_field_dict = {field: map(lambda obj: obj.pk, form.cleaned_data[field])
            if field in ('device_models') and form.cleaned_data[field] else form.cleaned_data[field]
                                       for field in form.cleaned_data.keys()}

            changed_fields_dict = nocout_utils.init_dict_differ_changed(initial_field_dict, cleaned_data_field_dict)
            if changed_fields_dict:
                initial_field_dict['device_models'] = ', '.join(
                    [DeviceModel.objects.get(pk=vendor).name for vendor in initial_field_dict['device_models']])
                cleaned_data_field_dict['device_models'] = ', '.join(
                    [DeviceModel.objects.get(pk=vendor).name for vendor in cleaned_data_field_dict['device_models']])

                verb_string = 'Changed values of Device Vendor : %s from initial values ' % (self.object.name) \
                              + ', '.join(['%s: %s' % (k, initial_field_dict[k]) for k in changed_fields_dict]) \
                              + ' to ' + \
                              ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])

                if len(verb_string) >= 255:
                    verb_string = verb_string[:250] + '...'

        except Exception as activity:
            pass

        return HttpResponseRedirect(DeviceVendorUpdate.success_url)


class DeviceVendorDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render device vendor delete view
    """
    model = DeviceVendor
    template_name = 'device_vendor/device_vendor_delete.html'
    success_url = reverse_lazy('device_vendor_list')
    required_permissions = ('device.delete_devicevendor',)


# ****************************************** Device Model *******************************************


class DeviceModelList(PermissionsRequiredMixin, ListView):
    """
    Render list of models
    """
    model = DeviceModel
    template_name = 'device_model/device_model_list.html'
    required_permissions = ('device.view_devicemodel',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DeviceModelList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'device_types', 'sTitle': 'Device Types', 'sWidth': 'auto', }
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DeviceModelListingTable(PermissionsRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of device models
    """
    model = DeviceModel
    required_permissions = ('device.view_devicemodel',)
    columns = ['name', 'alias', 'device_types']
    order_columns = ['name', 'alias', 'device_types']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            result_list = list()
            for dictionary in qs:

                x = json.dumps(dictionary)
                dictionary = json.loads(x)

                for dict in dictionary:
                    if dictionary[dict]:
                        if (isinstance(dictionary[dict], unicode) or isinstance(dictionary[dict], str)) and (
                                    dictionary not in result_list
                        ):
                            if sSearch.encode('utf-8').lower() in dictionary[dict].encode('utf-8').lower():
                                result_list.append(dictionary)
                        else:
                            if sSearch == dictionary[dict] and dictionary not in result_list:
                                result_list.append(dictionary)
            return self.advance_filter_queryset(result_list)

        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        qs_query = DeviceModel.objects.prefetch_related()
        qs = list()
        for dmodel in qs_query:
            dct = dict()
            dct = {
                'id': dmodel.id,
                'name': dmodel.name,
                'alias': dmodel.alias,
                'device_types': ', '.join(dmodel.device_types.values_list('name', flat=True)),
            }
            qs.append(dct)
        return qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/model/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/model/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
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


class DeviceModelDetail(PermissionsRequiredMixin, DetailView):
    """
    Render detail view for model
    """
    model = DeviceModel
    required_permissions = ('device.view_devicemodel',)
    template_name = 'device_model/device_model_detail.html'


class DeviceModelCreate(PermissionsRequiredMixin, CreateView):
    """
    Render device model create view
    """
    template_name = 'device_model/device_model_new.html'
    model = DeviceModel
    form_class = DeviceModelForm
    success_url = reverse_lazy('device_model_list')
    required_permissions = ('device.add_devicemodel',)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
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


class DeviceModelUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Render device model update view
    """
    template_name = 'device_model/device_model_update.html'
    model = DeviceModel
    form_class = DeviceModelForm
    success_url = reverse_lazy('device_model_list')
    required_permissions = ('device.change_devicemodel',)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
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


class DeviceModelDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render device model delete view
    """
    model = DeviceModel
    template_name = 'device_model/device_model_delete.html'
    success_url = reverse_lazy('device_model_list')
    required_permissions = ('device.delete_devicemodel',)


# ****************************************** Device Type *******************************************


class DeviceTypeList(PermissionsRequiredMixin, ListView):
    """
    Render list of device types
    """
    model = DeviceType
    template_name = 'device_type/device_type_list.html'
    required_permissions = ('device.view_devicetype',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DeviceTypeList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'agent_tag', 'sTitle': 'Agent tag', 'sWidth': 'auto', },
            {'mData': 'packets', 'sTitle': 'Packets', 'sWidth': 'auto'},
            {'mData': 'timeout', 'sTitle': 'Timeout (ms)', 'sWidth': 'auto'},
            {'mData': 'normal_check_interval', 'sTitle': 'Normal Check Interval', 'sWidth': 'auto'},
            {'mData': 'rta_warning', 'sTitle': 'Latency Warning (ms)', 'sWidth': 'auto'},
            {'mData': 'rta_critical', 'sTitle': 'Latency Critical (ms)', 'sWidth': 'auto'},
            {'mData': 'pl_warning', 'sTitle': 'PD Warning (%)', 'sWidth': 'auto'},
            {'mData': 'pl_critical', 'sTitle': 'PD Critical (%)', 'sWidth': 'auto'},
            {'mData': 'device_icon', 'sTitle': 'Device Icon', 'sWidth': 'auto'},
            {'mData': 'device_gmap_icon', 'sTitle': 'Device GMap Icon', 'sWidth': 'auto'},
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DeviceTypeListingTable(PermissionsRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of device types
    """
    model = DeviceType
    required_permissions = ('device.view_devicetype',)
    columns = ['name', 'alias', 'agent_tag', 'packets', 'timeout', 'normal_check_interval',
               'rta_warning', 'rta_critical', 'pl_warning', 'pl_critical', 'device_icon', 'device_gmap_icon']
    order_columns = ['name', 'alias', 'agent_tag', 'packets', 'timeout', 'normal_check_interval',
                     'rta_warning', 'rta_critical', 'pl_warning', 'pl_critical', 'device_icon', 'device_gmap_icon']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            result_list = list()
            for dictionary in qs:

                x = json.dumps(dictionary)
                dictionary = json.loads(x)

                for dict in dictionary:
                    if dictionary[dict]:
                        if (isinstance(dictionary[dict], unicode) or isinstance(dictionary[dict], str)) and (
                                    dictionary not in result_list
                        ):
                            if sSearch.encode('utf-8').lower() in dictionary[dict].encode('utf-8').lower():
                                result_list.append(dictionary)
                        else:
                            if sSearch == dictionary[dict] and dictionary not in result_list:
                                result_list.append(dictionary)
            return self.advance_filter_queryset(result_list)
        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DeviceType.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            try:
                device_icon_img_url = "/media/" + (dct['device_icon']) if \
                    "uploaded" in dct['device_icon'] \
                    else static("img/" + dct['device_icon'])
                dct.update(
                    device_icon='<img src="{0}" style="float:left; display:block; height:25px; width:25px;">'.format(
                        device_icon_img_url))
            except Exception as e:
                logger.exception(e)

            try:
                device_gmap_icon_img_url = "/media/" + (dct['device_gmap_icon']) if \
                    "uploaded" in dct['device_gmap_icon'] \
                    else static("img/" + dct['device_gmap_icon'])
                dct.update(
                    device_gmap_icon='<img src="{0}" style="float:left; display:block; height:25px; width:25px;">'.format(
                        device_gmap_icon_img_url))
            except Exception as e:
                logger.exception(e)

            dct.update(actions='<a href="/wizard/device-type/{0}/"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/type/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        order_columns = self.get_order_columns()
        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)
        
    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
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


class DeviceTypeDetail(PermissionsRequiredMixin, DetailView):
    """
    Render detail view for device type
    """
    model = DeviceType
    required_permissions = ('device.view_devicetype',)
    template_name = 'device_type/device_type_detail.html'


class DeviceTypeCreate(PermissionsRequiredMixin, CreateView):
    """
    Render device type create view
    """
    template_name = 'device_type/device_type_new.html'
    model = DeviceType
    success_url = reverse_lazy('device_type_list')
    required_permissions = ('device.add_devicetype',)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        device_type_service_form = DeviceTypeServiceCreateFormset(prefix='dts')
        return self.render_to_response(
            self.get_context_data(form=form,
                                  device_type_service_form=device_type_service_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        device_type_service_form = DeviceTypeServiceCreateFormset(self.request.POST, prefix='dts')
        if (form.is_valid() and device_type_service_form.is_valid()):
            return self.form_valid(form, device_type_service_form)
        else:
            return self.form_invalid(form, device_type_service_form)


class DeviceTypeUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Render device type update view
    """
    template_name = 'device_type/device_type_update.html'
    model = DeviceType
    success_url = reverse_lazy('device_type_list')
    required_permissions = ('device.change_devicetype',)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        device_type_service_form = DeviceTypeServiceUpdateFormset(instance=self.object, prefix='dts')
        if len(device_type_service_form):
            device_type_service_form = device_type_service_form
        else:
            device_type_service_form = DeviceTypeServiceCreateFormset(prefix='dts')
        return self.render_to_response(
            self.get_context_data(form=form,
                                  device_type_service_form=device_type_service_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        device_type_service_form = DeviceTypeServiceUpdateFormset(self.request.POST, instance=self.object, prefix='dts')
        if (form.is_valid() and device_type_service_form.is_valid()):
            return self.form_valid(form, device_type_service_form)
        else:
            return self.form_invalid(form, device_type_service_form)


class DeviceTypeDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render device type delete view
    """
    model = DeviceType
    template_name = 'device_type/device_type_delete.html'
    success_url = reverse_lazy('device_type_list')
    required_permissions = ('device.delete_devicetype',)


# ****************************************** Device Type *******************************************
class DevicePortList(PermissionsRequiredMixin, ListView):
    """
    Render list of ports
    """
    model = DevicePort
    template_name = 'device_port/device_ports_list.html'
    required_permissions = ('device.view_deviceport',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DevicePortList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'value', 'sTitle': 'Value', 'sWidth': 'auto', },
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DevicePortListingTable(PermissionsRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of device ports
    """
    model = DevicePort
    required_permissions = ('device.view_deviceport',)
    columns = ['name', 'alias', 'value']
    order_columns = ['name', 'alias', 'value']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DevicePort.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/device_port/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/device_port/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
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


class DevicePortDetail(PermissionsRequiredMixin, DetailView):
    """
    Render detail view for device port
    """
    model = DevicePort
    required_permissions = ('device.view_deviceport',)
    template_name = 'device_port/device_port_detail.html'


class DevicePortCreate(PermissionsRequiredMixin, CreateView):
    """
    Render device port create view
    """
    template_name = 'device_port/device_port_new.html'
    model = DevicePort
    form_class = DevicePortForm
    success_url = reverse_lazy('device_ports_list')
    required_permissions = ('device.add_deviceport',)


class DevicePortUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Render device port update view
    """
    template_name = 'device_port/device_port_update.html'
    model = DevicePort
    form_class = DevicePortForm
    success_url = reverse_lazy('device_ports_list')
    required_permissions = ('device.change_deviceport',)


class DevicePortDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render device port delete view
    """
    model = DevicePort
    template_name = 'device_port/device_port_delete.html'
    success_url = reverse_lazy('device_ports_list')
    required_permissions = ('device.delete_deviceport',)


class DeviceFrequencyListing(PermissionsRequiredMixin, ListView):
    """
    Render list of device frequencies list
    """
    model = DeviceFrequency
    template_name = 'device_frequency/device_frequency_list.html'
    required_permissions = ('device.view_devicefrequency',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DeviceFrequencyListing, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'value', 'sTitle': 'Value', 'sWidth': 'auto', },
            {'mData': 'color_hex_value', 'sTitle': 'Hex Value', 'sWidth': 'auto', },
            {'mData': 'frequency_radius', 'sTitle': 'Frequency Radius (Km)', 'sWidth': 'auto', }
        ]
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DeviceFrequencyListingTable(PermissionsRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of device frequencies
    """
    model = DeviceFrequency
    required_permissions = ('device.view_devicefrequency',)
    columns = ['value', 'color_hex_value', 'frequency_radius']
    order_columns = ['value', 'color_hex_value', 'frequency_radius']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        : param qs:
        : return qs:
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        # search if the entered text is atleast 3 characters long.
        if sSearch:
            # If character '\' is in entered text then replace the character '\' from entered text. Because it will create an error in sql query execution.
            sSearch = sSearch.replace("\\", "")

            # Replace the 'MHz' keyword from search txt
            sSearch = sSearch.lower().replace("mhz", "")
            sSearch = sSearch.strip()
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)

            # filter the model on the basis of the fields present in columns list.
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"  # returns the id of DeviceFrequency
            exec exec_query

        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DeviceFrequency.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            if "color_hex_value" in dct:
                dct.update(value=dct["value"] + " MHz")

                dct.update(
                    color_hex_value="<div style='float:left; display:block; height:20px; width:20px; background:{0}'>"
                                    "</div>" \
                                    "<span style='margin-left: 5px;'>{0}</span>".
                    format(dct["color_hex_value"]))

                dct.update(frequency_radius="0.0" if dct['frequency_radius'] in [None, ''] else dct['frequency_radius'])

            dct.update(actions='<a href="/frequency/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/frequency/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
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


class DeviceFrequencyCreate(PermissionsRequiredMixin, CreateView):
    """
    Render device frequency create view
    """
    template_name = 'device_frequency/device_frequency_new.html'
    model = DeviceFrequency
    form_class = DeviceFrequencyForm
    success_url = reverse_lazy('device_frequency_list')
    required_permissions = ('device.add_devicefrequency',)


class DeviceFrequencyUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Render device frequency update view
    """
    template_name = 'device_frequency/device_frequency_update.html'
    model = DeviceFrequency
    form_class = DeviceFrequencyForm
    success_url = reverse_lazy('device_frequency_list')
    required_permissions = ('device.change_devicefrequency',)


class DeviceFrequencyDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render device frequency delete view
    """
    model = DeviceFrequency
    template_name = 'device_frequency/device_frequency_delete.html'
    success_url = reverse_lazy('device_frequency_list')
    required_permissions = ('device.delete_devicefrequency',)
    obj_alias = 'value'


# **************************************** Country *********************************************
class CountryListing(SuperUserRequiredMixin, ListView):
    """
    Render list of country list
    :param Mixin SuperUserRequiredMixin- Only SuperUser can see the country list.
    :return json {'country_name', 'actions'}.
    """
    model = Country
    template_name = 'country/country_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(CountryListing, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'country_name', 'sTitle': 'Country', 'sWidth': 'auto', },
        ]
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class CountryListingTable(SuperUserRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of country
    """
    model = Country
    columns = ['country_name', ]
    order_columns = ['country_name', ]

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        :param qs:
        :return qs:
        """
        
        sSearch = self.request.GET.get('search[value]', None)

        #if entered text is atleast 3 characters long, then search.
        if sSearch:
            # if character '\' is in entered text, then remove the character '\' from entered text. because '\' will raise the error in execution of sql query.
            sSearch = sSearch.replace("\\", "")
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Country.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        :param qs:
        :return qs:
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/country/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/country/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
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


class CountryDetail(SuperUserRequiredMixin, DetailView):
    """
    Render detail view for Country
    """
    model = Country
    template_name = 'country/country_detail.html'


class CountryCreate(SuperUserRequiredMixin, CreateView):
    """
    Render country create view
    """
    template_name = 'country/country_new.html'
    model = Country
    form_class = CountryForm
    success_url = reverse_lazy('country_list')


class CountryUpdate(SuperUserRequiredMixin, UpdateView):
    """
    Render country update view
    """
    template_name = 'country/country_update.html'
    model = Country
    form_class = CountryForm
    success_url = reverse_lazy('country_list')


class CountryDelete(SuperUserRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render device country view
    """
    model = Country
    template_name = 'country/country_delete.html'
    success_url = reverse_lazy('country_list')
    obj_alias = 'country_name'


#**************************************** State *********************************************
class StateListing(SuperUserRequiredMixin, ListView):
    """
    Render list of state list. Only SuperUser can see the state list for that SuperUserRequiredMixin is used.
    """
    model = State
    template_name = 'state/state_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(StateListing, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'country__country_name', 'sTitle': 'Country', 'sWidth': '40%', },
            {'mData': 'state_name', 'sTitle': 'State', 'sWidth': 'auto', },
        ]
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class StateListingTable(SuperUserRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of state. Only SuperUser can see the state list for that SuperUserRequiredMixin is used.
    """
    model = State
    columns = ['country__country_name', 'state_name']
    order_columns = ['country__country_name', 'state_name', ]

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        : param qs:
        : return qs:
        """
        
        sSearch = self.request.GET.get('search[value]', None)

        # if entered text is atleast 3 characters long, then search.
        if sSearch:
            # if character '\' is in entered text, then replace '\' from entered text because it will raise the error in sql query execution.
            sSearch = sSearch.replace("\\", "")
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return State.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        :param qs:
        :return qs:
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/state/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/state/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
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


class StateDetail(SuperUserRequiredMixin, DetailView):
    """
    Render detail view for State
    """
    model = State
    template_name = 'state/state_detail.html'


class StateCreate(SuperUserRequiredMixin, CreateView):
    """
    Render state create view
    """
    template_name = 'state/state_new.html'
    model = State
    form_class = StateForm
    success_url = reverse_lazy('state_list')


class StateUpdate(SuperUserRequiredMixin, UpdateView):
    """
    Render state update view
    """
    template_name = 'state/state_update.html'
    model = State
    form_class = StateForm
    success_url = reverse_lazy('state_list')


class StateDelete(SuperUserRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render state delete view
    """
    model = State
    template_name = 'state/state_delete.html'
    success_url = reverse_lazy('state_list')
    obj_alias = 'state_name'


#**************************************** City *********************************************
class CityListing(SuperUserRequiredMixin, ListView):
    """
    Render list of city list. Only SuperUser can see the city list for that SuperUserRequiredMixin is used.
    """
    model = City
    template_name = 'city/city_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(CityListing, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'state__state_name', 'sTitle': 'State', 'sWidth': '40%', },
            {'mData': 'city_name', 'sTitle': 'City', 'sWidth': 'auto', },
        ]
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class CityListingTable(SuperUserRequiredMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Render JQuery datatables for listing of city. Only SuperUser can see the city list for that SuperUserRequiredMixin is used.
    """
    model = City
    columns = ['state__state_name', 'city_name']
    order_columns = ['state__state_name', 'city_name', ]

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        : param qs:
        : return qs:
        """
        
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            sSearch = sSearch.replace("\\", "")
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return self.advance_filter_queryset(qs)

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return City.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/cities/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/cities/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
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


class CityDetail(SuperUserRequiredMixin, DetailView):
    """
    Render detail view for city
    """
    model = City
    template_name = 'city/city_detail.html'


class CityCreate(SuperUserRequiredMixin, CreateView):
    """
    Render city create view
    """
    template_name = 'city/city_new.html'
    model = City
    form_class = CityForm
    success_url = reverse_lazy('city_list')


class CityUpdate(SuperUserRequiredMixin, UpdateView):
    """
    Render city update view
    """
    template_name = 'city/city_update.html'
    model = City
    form_class = CityForm
    success_url = reverse_lazy('city_list')


class CityDelete(SuperUserRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Render city delete view
    """
    model = City
    template_name = 'city/city_delete.html'
    success_url = reverse_lazy('city_list')
    obj_alias = 'city_name'


class GisWizardDeviceTypeMixin(object):
    """
    Class based mixin for gis wizard device type create and update.
    """
    form_class = WizardDeviceTypeForm
    template_name = 'wizard/device_type.html'

    def get_success_url(self):
        if self.request.GET.get('show', None):
            return reverse('wizard-device-type-update', kwargs={'pk': self.object.id})
        else:
            return reverse('wizard-service-list', kwargs={'dt_pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(GisWizardDeviceTypeMixin, self).get_context_data(**kwargs)
        if 'pk' in self.kwargs:  # Update View

            device_type = DeviceType.objects.get(id=self.kwargs['pk'])
            skip_url = reverse('wizard-service-list', kwargs={'dt_pk': self.object.id})

            save_text = 'Update'
            context['skip_url'] = skip_url
        else:  # Create View
            save_text = 'Save'

        service_dict = dict()
        qs = Service.objects.all()
        for obj in qs:
            service_dict.update({obj.id: {'text': '%s(%s)' % (obj.alias, obj.name), 'select': False, 'remove': False}})
        context['service_dict'] = json.dumps(service_dict)
        context['save_text'] = save_text
        return context

    def form_valid(self, form, device_type_service_form):

        """
        Called if all forms are valid. Update the Device Type instance along with
        associated Device Type Services and then redirects to a
        success page.
        """
        self.object = form.save()
        device_type_service_form.instance = self.object
        device_type_service_form.save()
        return super(GisWizardDeviceTypeMixin, self).form_valid(form)

    def form_invalid(self, form, device_type_service_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  device_type_service_form=device_type_service_form))


class GisWizardDeviceTypeCreateView(GisWizardDeviceTypeMixin, DeviceTypeCreate):
    pass


class GisWizardDeviceTypeUpdateView(GisWizardDeviceTypeMixin, DeviceTypeUpdate):
    pass


#**************************************** Device Type Service Wizard ****************************************#
class GisWizardServiceListView(PermissionsRequiredMixin, ListView):
    model = DeviceTypeService
    template_name = 'wizard/service_list.html'
    required_permissions = ('device.view_devicetypeservice',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(GisWizardServiceListView, self).get_context_data(**kwargs)
        device_type = DeviceType.objects.get(id=self.kwargs['dt_pk'])
        context['device_type'] = device_type
        datatable_headers = [
            {'mData': 'device_type', 'sTitle': 'Device Type', 'sWidth': 'auto', },
            {'mData': 'service__name', 'sTitle': 'Name', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'service__alias', 'sTitle': 'Alias', 'sWidth': 'auto', 'bSortable': True},
            {'mData': 'parameter__parameter_description', 'sTitle': 'Parameter', 'sWidth': 'auto', },
            {'mData': 'service_data_sources__alias', 'sTitle': 'Service Data Sources', 'sWidth': 'auto', },
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class GisWizardServiceListing(PermissionsRequiredMixin, DatatableSearchMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    Class based View to render Service Listing Table.
    """
    model = DeviceTypeService
    required_permissions = ('device.view_devicetypeservice',)
    columns = ['device_type', 'service__name', 'service__alias', 'parameter__parameter_description',
               'service_data_sources__alias']
    search_columns = ['device_type__alias', 'service__name', 'service__alias', 'parameter__parameter_description',
                      'service_data_sources__alias']
    order_columns = ['device_type', 'service__name', 'service__alias']

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        qs = self.model.objects.filter(device_type__id=self.kwargs['dt_pk'])
        return qs.prefetch_related('service_data_sources')

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = []
        for obj in qs:
            dct = {}
            dct.update(device_type=obj.device_type.alias)
            dct.update(service__name=obj.service.name)
            dct.update(service__alias=obj.service.alias)
            dct.update(parameter__parameter_description=obj.parameter.parameter_description)
            dct.update(
                service_data_sources__alias=', '.join(list(obj.service_data_sources.values_list('alias', flat=True))))
            dct.update(
                actions='<a href="/wizard/device-type/{0}/service/{1}/"><i class="fa fa-pencil text-dark"></i></a>'.format(
                    self.kwargs['dt_pk'], obj.id))
            json_data.append(dct)
        return json_data


class DeviceTypeServiceUpdateView(PermissionsRequiredMixin, UpdateView):
    """
    Render device type service update view.
    """
    model = DeviceTypeService
    template_name = 'wizard/device_type_service_update.html'
    form_class = WizardDeviceTypeServiceForm
    required_permissions = ('device.change_devicetypeservice',)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = WizardDeviceTypeServiceForm(instance=self.object)
        dts_data_source_form = DeviceTypeServiceDataSourceUpdateFormset(instance=self.object, prefix='dtsds')
        if len(dts_data_source_form):
            dts_data_source_form = dts_data_source_form
        else:
            dts_data_source_form = DeviceTypeServiceDataSourceCreateFormset(prefix='dtsds')
        return self.render_to_response(
            self.get_context_data(form=form,
                                  dts_data_source_form=dts_data_source_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        dts_data_source_form = DeviceTypeServiceDataSourceUpdateFormset(self.request.POST, instance=self.object,
                                                                        prefix='dtsds')
        if (form.is_valid() and dts_data_source_form.is_valid()):
            return self.form_valid(form, dts_data_source_form)
        else:
            return self.form_invalid(form, dts_data_source_form)


class GisWizardDeviceTypeServiceMixin(object):
    """
    Render device type update view. Mixin for gis wizard device type service update.
    """

    def get_success_url(self):
        if self.request.GET.get('show', None):
            return reverse('wizard-service-update', kwargs={'pk': self.object.id,
                                                            'dt_pk': self.kwargs['dt_pk']})
        else:
            return reverse('wizard-service-list', kwargs={'dt_pk': self.kwargs['dt_pk']})

    def get_context_data(self, **kwargs):
        context = super(GisWizardDeviceTypeServiceMixin, self).get_context_data(**kwargs)
        if 'pk' in self.kwargs:  # Update View

            device_type_service = DeviceTypeService.objects.get(id=self.kwargs['pk'])
            skip_url = reverse('wizard-service-list', kwargs={'dt_pk': self.kwargs['dt_pk']})
            try:
                service_alias = device_type_service.service.name
            except Exception, e:
                service_alias = ''
            save_text = 'Update'
            context['skip_url'] = skip_url
            context['service_alias'] = service_alias
        else:  # Create View
            save_text = 'Save'

        context['save_text'] = save_text
        return context

    def form_valid(self, form, dts_data_source_form):

        """
        Called if all forms are valid. Update the Device Type instance along with
        associated Device Type Services and then redirects to a
        success page.
        """
        self.object = form.save()
        dts_data_source_form.instance = self.object
        dts_data_source_form.save()
        return super(GisWizardDeviceTypeServiceMixin, self).form_valid(form)

    def form_invalid(self, form, dts_data_source_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  dts_data_source_form=dts_data_source_form))


class GisWizardServiceUpdateView(GisWizardDeviceTypeServiceMixin, DeviceTypeServiceUpdateView):
    pass


def list_schedule_device(request):
    """
    Used to return the list to the select2 element using ajax call.
    Return the list of devices while creating/updating the event.
    :param obj_id
           sSearch
           scheduling_type
           start_on_time
           end_on_time
           technology_id
    :return json:
    """

    # In case of Event Create set object_id = None.
    obj_id = None
    if 'obj_id' in request.GET:
        obj_id = request.GET['obj_id']  # update case
    # Get the entered text.
    sSearch = request.GET['sSearch']
    # Get the selected scheduling type.
    scheduling_type = request.GET['scheduling_type']
    # Set new_start_time and new_end_time if start_on_time and end_on_time is empty.
    new_start_time = datetime.today().time()
    new_end_time = datetime.today().time()
    # if start_on_time and end_on_time is not empty. Update the new_start_time and new_end_time.
    if request.GET['start_on_time'] and request.GET['end_on_time']:
        new_start_time = datetime.strptime(request.GET['start_on_time'], '%H:%M').time()
        new_end_time = datetime.strptime(request.GET['end_on_time'], '%H:%M').time()
    # Get the events which are overlapped.
    over_lap_event = Event.objects.exclude(id=obj_id).exclude(
        Q(start_on_time__gte=new_end_time) | Q(end_on_time__lte=new_start_time))
    # Get the device's id of overlapped events
    over_lap_device_ids = Device.objects.filter(event__in=over_lap_event).values_list("id", flat=True)

    # Get the organization of logged in user.
    org = request.user.userprofile.organization
    device_list = Device.objects.filter(
        organization__in=[org],
        is_added_to_nms__gt=0,
        is_deleted=0
    )
    technology_id = None

    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    # Get the technology_id. And Get the devices of that technology.
    if request.GET['technology_id']:
        technology_id = request.GET['technology_id']
        device_list = device_list.filter(device_technology=int(technology_id))

    # if scheduling type is device, then filter the devices on the basis of device alias.
    if scheduling_type == 'devi':
        device_list = device_list.filter(device_alias__icontains=sSearch)
    # if scheduling type is device type, then filter the devices on the basis of device type.
    elif scheduling_type == 'dety':
        # device_list = device_list.filter(device_type__in=DeviceType.objects.\
        #

        if technology_id:
            device_vendor = DeviceVendor.objects.filter(devicetechnology=int(technology_id))
            device_model = DeviceModel.objects.filter(devicevendor__in=device_vendor)
            device_type = DeviceType.objects.filter(devicemodel__in=device_model)
            device_list = device_type.filter(alias__icontains=sSearch)
        else:
            device_list = DeviceType.objects.filter(alias__icontains=sSearch)

        resultant_data = []
        for key in device_list:
            resultant_data.append({
                "id": key.id,
                "value": key.alias,
                "text": key.alias
            })

            # device_list = device_list.values_list('id', 'alias')

    # if scheduling type is customer, then filter the devices from organization_customer_devices.
    elif scheduling_type == 'cust':
        device_list = inventory_utils.organization_customer_devices(
            organizations=[org],
            technology=technology_id,
            specify_ptp_type='all'
        ).filter(device_alias__icontains=sSearch)
    # if scheduling type is network, then filter devices from organization_network_devices.
    elif scheduling_type == 'netw':
        device_list = inventory_utils.organization_network_devices(
            organizations=[org],
            technology=technology_id,
            specify_ptp_bh_type='all'
        ).filter(device_alias__icontains=sSearch)
    # if scheduling type is backhaul, then filter devices from organization_backhaul_devices.
    elif scheduling_type == 'back':
        device_list = inventory_utils.organization_backhaul_devices(
            organizations=[org],
            technology=technology_id
        ).filter(device_alias__icontains=sSearch)
    else:  # if no schedling type is available
        device_list = device_list.filter(device_alias__icontains=sSearch)

    if scheduling_type != 'dety':
        # excule the overlapping devices.
        device = device_list.exclude(id__in=over_lap_device_ids).values('id', 'device_alias')
        total_count = device.count()
        device_items = list(device)
    else:
        device = resultant_data
        total_count = len(device)
        device_items = device

    return HttpResponse(json.dumps({
        "total_count": total_count,
        "incomplete_results": False,
        "items": device_items
    }))


def select_schedule_device(request):
    """
    Called when Select2 is created to allow the user to initialize the selection based on the value of the element select2 is attached to.
    Call to initialize the device list when create/update the event.
    :param ids:
    :return json:
    """
    ids = request.GET['ids']
    scheduling_type = request.GET['scheduling_type'] if 'scheduling_type' in request.GET else ""

    if scheduling_type and scheduling_type == 'dety':
        device_result = [{'id': dev.id, 'text': dev.alias} for dev in DeviceType.objects.filter(id__in=ids.split(','))]
    else:
        device_result = [{'id': dev.id, 'device_alias': dev.device_alias} for dev in
                         Device.objects.filter(id__in=ids.split(','))]
    return HttpResponse(json.dumps({
        'device_result': device_result
    }))


def filter_selected_device(request):
    """
    On change of the time filter the devices.
    i.e it removes the devices from the selest2 if device overlaps on that duration.
    :param ids
           obj_id
           start_on_time
           end_on_time
    :return json:
    """

    ids = request.GET['ids']
    obj_id = None  # create case
    if 'obj_id' in request.GET:
        obj_id = request.GET['obj_id']  # update case
    new_start_time = datetime.strptime(request.GET['start_on_time'], '%H:%M').time()
    new_end_time = datetime.strptime(request.GET['end_on_time'], '%H:%M').time()
    over_lap_event = Event.objects.exclude(id=obj_id).exclude(
        Q(start_on_time__gte=new_end_time) | Q(end_on_time__lte=new_start_time))
    over_lap_device_ids = Device.objects.filter(event__in=over_lap_event).values_list("id", flat=True)

    device_result = [{'id': dev.id, 'device_alias': dev.device_alias} for dev in
                     Device.objects.filter(id__in=ids.split(',')).exclude(id__in=over_lap_device_ids)]
    return HttpResponse(json.dumps({
        'device_result': device_result
    }))


class DeviceSyncHistoryList(ListView):
    """
    Generic Class based View to List the DeviceSyncHistory.
    """

    model = DeviceSyncHistory
    template_name = 'device_sync_history/device_sync_history_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """
        context = super(DeviceSyncHistoryList, self).get_context_data(**kwargs)

        # get deadlock status
        deadlock_status = ""

        # get last sync run time
        last_sync_time = ""

        try:
            last_sync_status = get_current_sync_status()
            deadlock_status = last_sync_status[0]
            last_sync_time = last_sync_status[1]
        except Exception as e:
            pass

        datatable_headers = [
            {'mData': 'status', 'sTitle': 'Status', 'sWidth': 'auto', },
            {'mData': 'message', 'sTitle': 'Response Message', 'sWidth': 'auto', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto', },
            {'mData': 'sync_by', 'sTitle': 'Synced By', 'sWidth': 'auto', },
            {'mData': 'added_on', 'sTitle': 'Synced On Timestamp', 'sWidth': 'auto', },
            {'mData': 'completed_on', 'sTitle': 'Sync Completion Timestamp', 'sWidth': 'auto', },
        ]

        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
            context['deadlock_status'] = deadlock_status
            context['last_sync_time'] = last_sync_time

        context['datatable_headers'] = json.dumps(datatable_headers)

        return context


class DeviceSyncHistoryListingTable(DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    A generic class based view for the gis inventory bulk import data table rendering.

    """
    model = DeviceSyncHistory
    columns = ['status', 'message', 'description', 'sync_by', 'added_on', 'completed_on']
    order_columns = ['status', 'message', 'description', 'sync_by', 'added_on', 'completed_on']
    search_columns = ['status', 'message', 'description', 'sync_by']

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        # queryset
        queryset = DeviceSyncHistory.objects.all().values(*self.columns + ['id']).order_by('-added_on')

        return queryset

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            try:
                # show 'Success', 'Pending' and 'Failed' in upload status
                try:
                    if not dct.get('status'):
                        status_icon_color = "grey-dot"
                        dct.update(
                            status='<i class="fa fa-circle {0}"></i> Pending'.format(status_icon_color)
                        )
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('status') == 0:
                        status_icon_color = "grey-dot"
                        dct.update(
                            status='<i class="fa fa-circle {0}"></i> Pending'.format(status_icon_color)
                        )
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('status') == 1:
                        status_icon_color = "green-dot"
                        dct.update(
                            status='<i class="fa fa-circle {0}"></i> Success'.format(status_icon_color)
                        )
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('status') == 2:
                        status_icon_color = "red-dot"
                        dct.update(
                            status='<i class="fa fa-circle {0}"></i> Failed'.format(status_icon_color)
                        )
                except Exception as e:
                    logger.info(e.message)

                try:
                    if dct.get('status') == 3:
                        status_icon_color = "orange-dot"
                        dct.update(
                            status='<i class="fa fa-circle {0}"></i> Deadlock'.format(status_icon_color)
                        )
                except Exception as e:
                    logger.info(e.message)

                # show user full name in uploded by field
                try:
                    if dct.get('sync_by'):
                        user = User.objects.get(username=dct.get('sync_by'))
                        dct.update(sync_by='{} {}'.format(user.first_name, user.last_name))
                except Exception as e:
                    logger.info(e.message)

            except Exception as e:
                logger.info(e)

            # added on field timezone conversion from 'utc' to 'local'
            try:
                dct['added_on'] = nocout_utils.convert_utc_to_local_timezone(dct['added_on'])
            except Exception as e:
                logger.error("Timezone conversion not possible. Exception: ", e.message)

            # completed on field timezone conversion from 'utc' to 'local'
            try:
                dct['completed_on'] = nocout_utils.convert_utc_to_local_timezone(dct['completed_on'])
            except Exception as e:
                logger.error("Timezone conversion not possible. Exception: ", e.message)

            dct.update(actions='<a href="/device_sync_history/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                                <a href="/device_sync_history/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.get('id')))

        return json_data


class DeviceSyncHistoryDelete(DeleteView):
    """
    Class based View to delete the GISInventoryBulkImport
    """
    model = DeviceSyncHistory
    template_name = 'device_sync_history/device_sync_history_delete.html'
    success_url = reverse_lazy('device_sync_history_list')

    def delete(self, request, *args, **kwargs):
        device_sync_obj = self.get_object()

        # delete entry from database
        device_sync_obj.delete()
        return HttpResponseRedirect(DeviceSyncHistoryDelete.success_url)


class DeviceSyncHistoryUpdate(UpdateView):
    """
    Class based view to update GISInventoryBulkImport.
    """
    template_name = 'device_sync_history/device_sync_history_update.html'
    model = DeviceSyncHistory
    form_class = DeviceSyncHistoryEditForm
    success_url = reverse_lazy('device_sync_history_list')


def get_current_sync_status():
    """ Get current sync status i.e. deadlock exist or not and last sync timestamp

    Returns:
        [deadlock_status, last_sync_time] (list): list containing deadlock status and last sync time

    """

    # deadlock status
    deadlock_status = 'no'

    # last sync status
    last_sync_time = ""

    try:
        device_history_obj = DeviceSyncHistory.objects.latest('id')
        if device_history_obj:
            # time of last sync run
            try:
                last_sync_time = nocout_utils.convert_utc_to_local_timezone(device_history_obj.added_on)
            except Exception as e:
                pass

            # current timestamp (with 'utc' as timezone)
            current_timstamp = datetime.utcnow().replace(tzinfo=None)

            # 'added_on' timestamp of last run of sync (with 'utc' as timezone)
            added_on_time = device_history_obj.added_on.replace(tzinfo=None)

            # current timestamp and added on timestamp difference
            time_difference = datetime.utcnow() - added_on_time

            # status of last run of sync
            last_sync_status = device_history_obj.status

            if last_sync_status == 0 and time_difference > timedelta(minutes=30, seconds=0):
                deadlock_status = 'yes'
    except Exception as e:
        pass

    return [deadlock_status, last_sync_time]
