import json
from operator import itemgetter
from actstream import action
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.query import ValuesQuerySet
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from device.models import Device, DeviceType, DeviceTypeFields, DeviceTypeFieldsValue, DeviceTechnology, \
    TechnologyVendor, DeviceVendor, VendorModel, DeviceModel, ModelType, DevicePort, Country, State, City, \
    DeviceFrequency
from forms import DeviceForm, DeviceTypeFieldsForm, DeviceTypeFieldsUpdateForm, DeviceTechnologyForm, \
    DeviceVendorForm, DeviceModelForm, DeviceTypeForm, DevicePortForm, DeviceFrequencyForm
from nocout.utils.util import DictDiffer
from django.http.response import HttpResponseRedirect
from organization.models import Organization
from service.models import Service
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings #Importing settings for logger
from site_instance.models import SiteInstance
from inventory.models import Backhaul, SubStation, Sector
from django.contrib.staticfiles.templatetags.staticfiles import static

if settings.DEBUG:
    import logging
    logger = logging.getLogger(__name__)

# ***************************************** Device Views ********************************************


class DeviceList(ListView):
    model = Device
    template_name = 'device/devices_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'status_icon',               'sTitle' : '',              'sWidth':'null',},
            {'mData':'organization__name',     'sTitle' : 'Organization',  'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'device_alias',           'sTitle' : 'Alias',         'sWidth':'null',},
            {'mData':'site_instance__name',    'sTitle' : 'Site Instance', 'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'machine__name',          'sTitle' : 'Machine',       'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'device_technology__name','sTitle' : 'Device Technology',   'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'device_type__name',      'sTitle' : 'Device Type',   'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'host_state',             'sTitle' : 'Host State',    'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'ip_address',             'sTitle' : 'IP Address',    'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'mac_address',            'sTitle' : 'MAC Address',   'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'state__name',            'sTitle' : 'State',   'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},]

        #if the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Device Actions', 'sWidth':'9%', 'bSortable': False})
            datatable_headers.append({'mData':'nms_actions', 'sTitle':'NMS Actions', 'sWidth':'8%', 'bSortable': False})

        datatable_headers_no_nms_actions = [
            {'mData':'status_icon',            'sTitle' : '',              'sWidth':'null',},
            {'mData':'organization__name',     'sTitle' : 'Organization',  'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'device_alias',           'sTitle' : 'Alias',         'sWidth':'null',},
            {'mData':'site_instance__name',    'sTitle' : 'Site Instance', 'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'machine__name',          'sTitle' : 'Machine',       'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'device_technology__name','sTitle' : 'Device Technology',   'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'device_type__name',      'sTitle' : 'Device Type',   'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'host_state',             'sTitle' : 'Host State',    'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'ip_address',             'sTitle' : 'IP Address',    'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'mac_address',            'sTitle' : 'MAC Address',   'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'state__name',            'sTitle' : 'State',   'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},]

        #if the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers_no_nms_actions.append({'mData':'actions', 'sTitle':'Device Actions', 'sWidth':'15%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['datatable_headers_no_nms_actions'] = json.dumps(datatable_headers_no_nms_actions)
        return context


def create_device_tree(request):

    templateData = {
        'username' : request.user.username
    }
    
    return render_to_response('device/devices_tree_view.html',templateData,context_instance=RequestContext(request))


class OperationalDeviceListingTable(BaseDatatableView):
    model = Device
    columns = [ 'device_alias', 'site_instance__name', 'machine__name', 'organization__name','device_technology',
                'device_type', 'host_state','ip_address', 'mac_address', 'state']
    order_columns = ['organization__name', 'device_alias', 'site_instance__name', 'machine__name']

    def pop_filter_keys(self, dct):
        keys_list=['device_type__name', 'device_technology__name', 'state__name']
        for k in keys_list:
            dct.pop(k)


    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()

            for dictionary in qs:
                try:
                    dictionary['device_type__name']= DeviceType.objects.get(pk=int(dictionary['device_type'])).name \
                        if dictionary['device_type'] else ''
                except Exception as device_type_exp:
                    dictionary['device_type__name'] = ""

                try:
                    dictionary['device_technology__name']=DeviceTechnology.objects.get(pk=int(dictionary['device_technology'])).name \
                                                if dictionary['device_technology'] else ''
                except Exception as device_tech_exp:
                    dictionary['device_technology__name'] = ""

                try:
                    dictionary['state__name']= State.objects.get(pk=int(dictionary['state'])).state_name if dictionary['state'] else ''
                except Exception as device_state_exp:
                    dictionary['state__name'] = ""


                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        self.pop_filter_keys(dictionary)
                        break
                map(lambda x:  dictionary.pop(x) if x in dictionary else None, ['device_type__name', 'device_technology__name', 'state__name'])

            return result_list

        if settings.DEBUG:
            logger.debug(qs, exc_info=True, extra={'stack': True, 'request': self.request})

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

            sdir = '-' if s_sort_dir == 'desc' else ' '

            sortcol = order_columns[i_sort_col-1]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key=itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs

    def logged_in_user_organization_ids(self):
        organization_descendants_ids= list(self.request.user.userprofile.organization.get_children()\
                                           .values_list('id', flat=True)) + [ self.request.user.userprofile.organization.id ]
        return organization_descendants_ids

    def get_initial_queryset(self):
        if not self.model:

            if settings.DEBUG:
                logger.error("Need to provide a model or implement get_initial_queryset!",
                                 extra={'stack': True, 'request': self.request})

            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        organization_descendants_ids= self.logged_in_user_organization_ids()
        return Device.objects.filter(organization__in = organization_descendants_ids, is_deleted=0, is_monitored_on_nms=1) \
                                     .values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            # current device in loop
            current_device = Device.objects.get(pk=dct['id'])

            try:
                dct['device_type__name']= DeviceType.objects.get(pk=int(dct['device_type'])).name if dct['device_type'] else ''
            except Exception as device_type_exp:
                dct['device_type__name'] = ""

            try:
                dct['device_technology__name']=DeviceTechnology.objects.get(pk=int(dct['device_technology'])).name \
                                            if dct['device_technology'] else ''
            except Exception as device_tech_exp:
                dct['device_technology__name'] = ""

            try:
                dct['state__name']= State.objects.get(pk=int(dct['state'])).state_name if dct['state'] else ''
            except Exception as device_state_exp:
                dct['state__name'] = ""

            img_url = static('img/nms_icons/circle_green.png')
            dct.update(status_icon='<img src="{0}">'.format(img_url))

            # There are two set of links in device list table
            # 1. Device Actions --> device detail, edit, delete from inventory. They are always present in device table if user role is 'Admin'
            # 2. NMS Actions --> device add, sync, service add etc. form nocout nms core. They are only present
            # in device table if device id one of the following:
            # a. backhaul configured on (from model Backhaul)
            # b. sector configures on (from model Sector)
            # c. sub-station configured on (from model SubStation)
            dct.update(actions='<a href="/device/{0}"><i class="fa fa-list-alt text-info" title="Detail"></i></a>\
               <a href="/device/edit/{0}"><i class="fa fa-pencil text-dark" title="Edit"></i></a>\
               <a href="#" onclick="Dajaxice.device.device_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger" title="Delete"></i></a>'.format(dct['id']))
            dct.update(nms_actions='')
            # device is monitored only if it's a backhaul configured on, sector configured on or sub-station
            # checking whether device is 'backhaul configured on' or not
            try:
                if Backhaul.objects.get(bh_configured_on=current_device):
                    dct.update(nms_actions='<a href="#" onclick="delete_device({0});"><i class="fa fa-minus-square text-info" title="Delete Device"></i></a>\
                                            <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-info" title="Add Service"></i></a>\
                                            <a href="#" onclick="Dajaxice.device.edit_service_form(get_service_edit_form, {{\'value\': {0}}})"><i class="fa fa-pencil text-info" title="Edit Service"></i></a>'.format(dct['id']))
            except:
                logger.info("Device is not a backhaul")

            # checking whether device is 'sector configured on' or not
            try:
                if Sector.objects.get(sector_configured_on=current_device):
                    dct.update(nms_actions='<a href="#" onclick="delete_device({0});"><i class="fa fa-minus-square text-success" title="Delete Device"></i></a>\
                                            <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>\
                                            <a href="#" onclick="Dajaxice.device.edit_service_form(get_service_edit_form, {{\'value\': {0}}})"><i class="fa fa-pencil text-success" title="Edit Service"></i></a>'.format(dct['id']))
            except:
                logger.info("Device is not sector configured on.")

            # checking whether device is 'sub station' or not
            try:
                if SubStation.objects.get(device=current_device):
                    dct.update(nms_actions='<a href="#" onclick="delete_device({0});"><i class="fa fa-minus-square text-danger" title="Delete Device"></i></a>\
                                            <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-danger" title="Add Service"></i></a>\
                                            <a href="#" onclick="Dajaxice.device.edit_service_form(get_service_edit_form, {{\'value\': {0}}})"><i class="fa fa-pencil text-danger" title="Edit Service"></i></a>'.format(dct['id']))
            except:
                logger.info("Device is not a substation.")
        return qs

    def get_context_data(self, *args, **kwargs):
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
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData,
               }
        return ret


class NonOperationalDeviceListingTable(BaseDatatableView):
    model = Device
    columns = [ 'device_alias', 'site_instance__name', 'machine__name', 'organization__name','device_technology',
                'device_type', 'host_state','ip_address', 'mac_address', 'state']
    order_columns = ['organization__name', 'device_alias', 'site_instance__name', 'machine__name']

    def pop_filter_keys(self, dct):
        keys_list=['device_type__name', 'device_technology__name', 'state__name']
        for k in keys_list:
            dct.pop(k)


    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()

            for dictionary in qs:
                try:
                    dictionary['device_type__name']= DeviceType.objects.get(pk=int(dictionary['device_type'])).name \
                        if dictionary['device_type'] else ''
                except Exception as device_type_exp:
                    dictionary['device_type__name'] = ""

                try:
                    dictionary['device_technology__name']=DeviceTechnology.objects.get(pk=int(dictionary['device_technology'])).name \
                                                if dictionary['device_technology'] else ''
                except Exception as device_tech_exp:
                    dictionary['device_technology__name'] = ""

                try:
                    dictionary['state__name']= State.objects.get(pk=int(dictionary['state'])).state_name if dictionary['state'] else ''
                except Exception as device_state_exp:
                    dictionary['state__name'] = ""


                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        self.pop_filter_keys(dictionary)
                        break
                map(lambda x:  dictionary.pop(x) if x in dictionary else None, ['device_type__name', 'device_technology__name', 'state__name'])

            return result_list

        if settings.DEBUG:
            logger.debug(qs, exc_info=True, extra={'stack': True, 'request': self.request})

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

            sdir = '-' if s_sort_dir == 'desc' else ' '

            sortcol = order_columns[i_sort_col-1]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key=itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs

    def logged_in_user_organization_ids(self):
        organization_descendants_ids= list(self.request.user.userprofile.organization.get_children()\
                                           .values_list('id', flat=True)) + [ self.request.user.userprofile.organization.id ]
        return organization_descendants_ids

    def get_initial_queryset(self):
        if not self.model:

            if settings.DEBUG:
                logger.error("Need to provide a model or implement get_initial_queryset!",
                                 extra={'stack': True, 'request': self.request})

            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        organization_descendants_ids= self.logged_in_user_organization_ids()
        return Device.objects.filter(organization__in = organization_descendants_ids, is_deleted=0, is_monitored_on_nms=0, host_state="Enable") \
                                     .values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            # current device in loop
            current_device = Device.objects.get(pk=dct['id'])

            try:
                dct['device_type__name']= DeviceType.objects.get(pk=int(dct['device_type'])).name if dct['device_type'] else ''
            except Exception as device_type_exp:
                dct['device_type__name'] = ""

            try:
                dct['device_technology__name']=DeviceTechnology.objects.get(pk=int(dct['device_technology'])).name \
                                            if dct['device_technology'] else ''
            except Exception as device_tech_exp:
                dct['device_technology__name'] = ""

            try:
                dct['state__name']= State.objects.get(pk=int(dct['state'])).state_name if dct['state'] else ''
            except Exception as device_state_exp:
                dct['state__name'] = ""

            img_url = static('img/nms_icons/circle_orange.png')
            dct.update(status_icon='<img src="{0}">'.format(img_url))

            # There are two set of links in device list table
            # 1. Device Actions --> device detail, edit, delete from inventory. They are always present in device table if user role is 'Admin'
            # 2. NMS Actions --> device add, sync, service add etc. form nocout nms core. They are only present
            # in device table if device id one of the following:
            # a. backhaul configured on (from model Backhaul)
            # b. sector configures on (from model Sector)
            # c. sub-station configured on (from model SubStation)
            dct.update(actions='<a href="/device/{0}"><i class="fa fa-list-alt text-info" title="Detail"></i></a>\
               <a href="/device/edit/{0}"><i class="fa fa-pencil text-dark" title="Edit"></i></a>\
               <a href="#" onclick="Dajaxice.device.device_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger" title="Delete"></i></a>'.format(dct['id']))
            dct.update(nms_actions='')
            # device is monitored only if it's a backhaul configured on, sector configured on or sub-station
            # checking whether device is 'backhaul configured on' or not
            try:
                if Backhaul.objects.get(bh_configured_on=current_device):
                    dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-info" title="Add Device"></i></a>\
                        <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-info" title="Add Service"></i></a>'.format(dct['id']))
            except:
                logger.info("Device is not a backhaul.")

            # checking whether device is 'sector configured on' or not
            try:
                if Sector.objects.get(sector_configured_on=current_device):
                    dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-success" title="Add Device"></i></a>\
                        <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>'.format(dct['id']))
            except:
                logger.info("Device is not sector configured on.")

            # checking whether device is 'sub station' or not
            try:
                if SubStation.objects.get(device=current_device):
                    dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-danger"></i></a>\
                        <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-danger" title="Add Service"></i></a>'.format(dct['id']))
            except:
                logger.info("Device is not a substation.")
        return qs

    def get_context_data(self, *args, **kwargs):
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
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data

        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData,
               }
        return ret


class DisabledDeviceListingTable(BaseDatatableView):
    model = Device
    columns = [ 'device_alias', 'site_instance__name', 'machine__name', 'organization__name','device_technology',
                'device_type', 'host_state','ip_address', 'mac_address', 'state']
    order_columns = ['organization__name', 'device_alias', 'site_instance__name', 'machine__name']

    def pop_filter_keys(self, dct):
        keys_list=['device_type__name', 'device_technology__name', 'state__name']
        for k in keys_list:
            dct.pop(k)


    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()

            for dictionary in qs:
                try:
                    dictionary['device_type__name']= DeviceType.objects.get(pk=int(dictionary['device_type'])).name \
                        if dictionary['device_type'] else ''
                except Exception as device_type_exp:
                    dictionary['device_type__name'] = ""

                try:
                    dictionary['device_technology__name']=DeviceTechnology.objects.get(pk=int(dictionary['device_technology'])).name \
                                                if dictionary['device_technology'] else ''
                except Exception as device_tech_exp:
                    dictionary['device_technology__name'] = ""

                try:
                    dictionary['state__name']= State.objects.get(pk=int(dictionary['state'])).state_name if dictionary['state'] else ''
                except Exception as device_state_exp:
                    dictionary['state__name'] = ""


                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        self.pop_filter_keys(dictionary)
                        break
                map(lambda x:  dictionary.pop(x) if x in dictionary else None, ['device_type__name', 'device_technology__name', 'state__name'])

            return result_list

        if settings.DEBUG:
            logger.debug(qs, exc_info=True, extra={'stack': True, 'request': self.request})

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

            sdir = '-' if s_sort_dir == 'desc' else ' '

            sortcol = order_columns[i_sort_col-1]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key=itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs

    def logged_in_user_organization_ids(self):
        organization_descendants_ids= list(self.request.user.userprofile.organization.get_children()\
                                           .values_list('id', flat=True)) + [ self.request.user.userprofile.organization.id ]
        return organization_descendants_ids

    def get_initial_queryset(self):
        if not self.model:

            if settings.DEBUG:
                logger.error("Need to provide a model or implement get_initial_queryset!",
                                 extra={'stack': True, 'request': self.request})

            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        organization_descendants_ids= self.logged_in_user_organization_ids()
        return Device.objects.filter(organization__in = organization_descendants_ids, is_deleted=0, host_state="Disable") \
                                     .values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            # current device in loop
            current_device = Device.objects.get(pk=dct['id'])

            try:
                dct['device_type__name']= DeviceType.objects.get(pk=int(dct['device_type'])).name if dct['device_type'] else ''
            except Exception as device_type_exp:
                dct['device_type__name'] = ""

            try:
                dct['device_technology__name']=DeviceTechnology.objects.get(pk=int(dct['device_technology'])).name \
                                            if dct['device_technology'] else ''
            except Exception as device_tech_exp:
                dct['device_technology__name'] = ""

            try:
                dct['state__name']= State.objects.get(pk=int(dct['state'])).state_name if dct['state'] else ''
            except Exception as device_state_exp:
                dct['state__name'] = ""

            img_url = static('img/nms_icons/circle_grey.png')
            dct.update(status_icon='<img src="{0}">'.format(img_url))

            # There are two set of links in device list table
            # 1. Device Actions --> device detail, edit, delete from inventory. They are always present in device table if user role is 'Admin'
            # 2. NMS Actions --> device add, sync, service add etc. form nocout nms core. They are only present
            # in device table if device id one of the following:
            # a. backhaul configured on (from model Backhaul)
            # b. sector configures on (from model Sector)
            # c. sub-station configured on (from model SubStation)
            dct.update(actions='<a href="/device/{0}"><i class="fa fa-list-alt text-info" title="Detail"></i></a>\
               <a href="/device/edit/{0}"><i class="fa fa-pencil text-dark" title="Edit"></i></a>\
               <a href="#" onclick="Dajaxice.device.device_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger" title="Delete"></i></a>'.format(dct['id']))
            # dct.update(nms_actions='')
            # # device is monitored only if it's a backhaul configured on, sector configured on or sub-station
            # # checking whether device is 'backhaul configured on' or not
            # try:
            #     if Backhaul.objects.get(bh_configured_on=current_device):
            #         dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-warning"></i></a>\
            #             <a href="#" onclick="sync_devices({0});"><i class="fa fa-share-square-o text-success" title="Sync device for monitoring"></i></a>\
            #             <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>'.format(dct['id']))
            # except:
            #     logger.info("Device is not basestation")
            #
            # # checking whether device is 'sector configured on' or not
            # try:
            #     if Sector.objects.get(sector_configured_on=current_device):
            #         dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-warning"></i></a>\
            #             <a href="#" onclick="sync_devices({0});"><i class="fa fa-share-square-o text-success" title="Sync device for monitoring"></i></a>\
            #             <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>'.format(dct['id']))
            # except:
            #     logger.info("Device is not basestation")
            #
            # # checking whether device is 'sub station' or not
            # try:
            #     if SubStation.objects.get(device=current_device):
            #         dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-warning"></i></a>\
            #             <a href="#" onclick="sync_devices({0});"><i class="fa fa-share-square-o text-success" title="Sync device for monitoring"></i></a>\
            #             <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>'.format(dct['id']))
            # except:
            #     logger.info("Device is not substation.")
        return qs

    def get_context_data(self, *args, **kwargs):
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
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData,
               }
        return ret


class ArchivedDeviceListingTable(BaseDatatableView):
    model = Device
    columns = [ 'device_alias', 'site_instance__name', 'machine__name', 'organization__name','device_technology',
                'device_type', 'host_state','ip_address', 'mac_address', 'state']
    order_columns = ['organization__name', 'device_alias', 'site_instance__name', 'machine__name']

    def pop_filter_keys(self, dct):
        keys_list=['device_type__name', 'device_technology__name', 'state__name']
        for k in keys_list:
            dct.pop(k)


    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()

            for dictionary in qs:
                try:
                    dictionary['device_type__name']= DeviceType.objects.get(pk=int(dictionary['device_type'])).name \
                        if dictionary['device_type'] else ''
                except Exception as device_type_exp:
                    dictionary['device_type__name'] = ""

                try:
                    dictionary['device_technology__name']=DeviceTechnology.objects.get(pk=int(dictionary['device_technology'])).name \
                                                if dictionary['device_technology'] else ''
                except Exception as device_tech_exp:
                    dictionary['device_technology__name'] = ""

                try:
                    dictionary['state__name']= State.objects.get(pk=int(dictionary['state'])).state_name if dictionary['state'] else ''
                except Exception as device_state_exp:
                    dictionary['state__name'] = ""


                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        self.pop_filter_keys(dictionary)
                        break
                map(lambda x:  dictionary.pop(x) if x in dictionary else None, ['device_type__name', 'device_technology__name', 'state__name'])

            return result_list

        if settings.DEBUG:
            logger.debug(qs, exc_info=True, extra={'stack': True, 'request': self.request})

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

            sdir = '-' if s_sort_dir == 'desc' else ' '

            sortcol = order_columns[i_sort_col-1]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key=itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs

    def logged_in_user_organization_ids(self):
        organization_descendants_ids= list(self.request.user.userprofile.organization.get_children()\
                                           .values_list('id', flat=True)) + [ self.request.user.userprofile.organization.id ]
        return organization_descendants_ids

    def get_initial_queryset(self):
        if not self.model:

            if settings.DEBUG:
                logger.error("Need to provide a model or implement get_initial_queryset!",
                                 extra={'stack': True, 'request': self.request})

            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        organization_descendants_ids= self.logged_in_user_organization_ids()
        return Device.objects.filter(organization__in = organization_descendants_ids, is_deleted=1) \
                                     .values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            # current device in loop
            current_device = Device.objects.get(pk=dct['id'])

            try:
                dct['device_type__name']= DeviceType.objects.get(pk=int(dct['device_type'])).name if dct['device_type'] else ''
            except Exception as device_type_exp:
                dct['device_type__name'] = ""

            try:
                dct['device_technology__name']=DeviceTechnology.objects.get(pk=int(dct['device_technology'])).name \
                                            if dct['device_technology'] else ''
            except Exception as device_tech_exp:
                dct['device_technology__name'] = ""

            try:
                dct['state__name']= State.objects.get(pk=int(dct['state'])).state_name if dct['state'] else ''
            except Exception as device_state_exp:
                dct['state__name'] = ""

            img_url = static('img/nms_icons/circle_red.png')
            dct.update(status_icon='<img src="{0}">'.format(img_url))

            # There are two set of links in device list table
            # 1. Device Actions --> device detail, edit, delete from inventory. They are always present in device table if user role is 'Admin'
            # 2. NMS Actions --> device add, sync, service add etc. form nocout nms core. They are only present
            # in device table if device id one of the following:
            # a. backhaul configured on (from model Backhaul)
            # b. sector configures on (from model Sector)
            # c. sub-station configured on (from model SubStation)
            dct.update(actions='<a href="/device/{0}"><i class="fa fa-list-alt text-info" title="Detail"></i></a>\
               <a href="/device/edit/{0}"><i class="fa fa-pencil text-dark" title="Edit"></i></a>\
               <a href="#" onclick="Dajaxice.device.device_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger" title="Delete"></i></a>'.format(dct['id']))
            # dct.update(nms_actions='')
            # # device is monitored only if it's a backhaul configured on, sector configured on or sub-station
            # # checking whether device is 'backhaul configured on' or not
            # try:
            #     if Backhaul.objects.get(bh_configured_on=current_device):
            #         dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-warning"></i></a>\
            #             <a href="#" onclick="sync_devices({0});"><i class="fa fa-share-square-o text-success" title="Sync device for monitoring"></i></a>\
            #             <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>'.format(dct['id']))
            # except:
            #     logger.info("Device is not basestation")
            #
            # # checking whether device is 'sector configured on' or not
            # try:
            #     if Sector.objects.get(sector_configured_on=current_device):
            #         dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-warning"></i></a>\
            #             <a href="#" onclick="sync_devices({0});"><i class="fa fa-share-square-o text-success" title="Sync device for monitoring"></i></a>\
            #             <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>'.format(dct['id']))
            # except:
            #     logger.info("Device is not basestation")
            #
            # # checking whether device is 'sub station' or not
            # try:
            #     if SubStation.objects.get(device=current_device):
            #         dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-warning"></i></a>\
            #             <a href="#" onclick="sync_devices({0});"><i class="fa fa-share-square-o text-success" title="Sync device for monitoring"></i></a>\
            #             <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>'.format(dct['id']))
            # except:
            #     logger.info("Device is not substation.")
        return qs

    def get_context_data(self, *args, **kwargs):
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
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData,
               }
        return ret


class AllDeviceListingTable(BaseDatatableView):
    model = Device
    columns = [ 'device_alias', 'site_instance__name', 'machine__name', 'organization__name','device_technology',
                'device_type', 'host_state','ip_address', 'mac_address', 'state']
    order_columns = ['organization__name', 'device_alias', 'site_instance__name', 'machine__name']

    def pop_filter_keys(self, dct):
        keys_list=['device_type__name', 'device_technology__name', 'state__name']
        for k in keys_list:
            dct.pop(k)


    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()

            for dictionary in qs:
                try:
                    dictionary['device_type__name']= DeviceType.objects.get(pk=int(dictionary['device_type'])).name \
                        if dictionary['device_type'] else ''
                except Exception as device_type_exp:
                    dictionary['device_type__name'] = ""

                try:
                    dictionary['device_technology__name']=DeviceTechnology.objects.get(pk=int(dictionary['device_technology'])).name \
                                                if dictionary['device_technology'] else ''
                except Exception as device_tech_exp:
                    dictionary['device_technology__name'] = ""

                try:
                    dictionary['state__name']= State.objects.get(pk=int(dictionary['state'])).state_name if dictionary['state'] else ''
                except Exception as device_state_exp:
                    dictionary['state__name'] = ""


                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        self.pop_filter_keys(dictionary)
                        break
                map(lambda x:  dictionary.pop(x) if x in dictionary else None, ['device_type__name', 'device_technology__name', 'state__name'])

            return result_list

        if settings.DEBUG:
            logger.debug(qs, exc_info=True, extra={'stack': True, 'request': self.request})

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

            sdir = '-' if s_sort_dir == 'desc' else ' '

            sortcol = order_columns[i_sort_col-1]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key=itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs

    def logged_in_user_organization_ids(self):
        organization_descendants_ids= list(self.request.user.userprofile.organization.get_children()\
                                           .values_list('id', flat=True)) + [ self.request.user.userprofile.organization.id ]
        return organization_descendants_ids

    def get_initial_queryset(self):
        if not self.model:

            if settings.DEBUG:
                logger.error("Need to provide a model or implement get_initial_queryset!",
                                 extra={'stack': True, 'request': self.request})

            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        organization_descendants_ids= self.logged_in_user_organization_ids()
        return Device.objects.filter(organization__in = organization_descendants_ids, is_deleted=0) \
                                     .values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            # current device in loop
            current_device = Device.objects.get(pk=dct['id'])

            try:
                dct['device_type__name']= DeviceType.objects.get(pk=int(dct['device_type'])).name if dct['device_type'] else ''
            except Exception as device_type_exp:
                dct['device_type__name'] = ""

            try:
                dct['device_technology__name']=DeviceTechnology.objects.get(pk=int(dct['device_technology'])).name \
                                            if dct['device_technology'] else ''
            except Exception as device_tech_exp:
                dct['device_technology__name'] = ""

            try:
                dct['state__name']= State.objects.get(pk=int(dct['state'])).state_name if dct['state'] else ''
            except Exception as device_state_exp:
                dct['state__name'] = ""

            # if device is already added to nms core than show icon in device table
            img_url = ""
            try:
                if current_device.is_monitored_on_nms == 1:
                    img_url = static('img/nms_icons/circle_green.png')
                elif current_device.is_monitored_on_nms == 0 and current_device.host_state == "Enable":
                    img_url = static('img/nms_icons/circle_orange.png')
                elif current_device.is_monitored_on_nms == 0 and current_device.host_state == "Disable":
                    img_url = static('img/nms_icons/circle_grey.png')
                dct.update(status_icon='<img src="{0}">'.format(img_url))
            except Exception as e:
                logger.info(e.message)
                dct.update(status_icon='<img src="">')
            # There are two set of links in device list table
            # 1. Device Actions --> device detail, edit, delete from inventory. They are always present in device table if user role is 'Admin'
            # 2. NMS Actions --> device add, sync, service add etc. form nocout nms core. They are only present
            # in device table if device id one of the following:
            # a. backhaul configured on (from model Backhaul)
            # b. sector configures on (from model Sector)
            # c. sub-station configured on (from model SubStation)
            dct.update(actions='<a href="/device/{0}"><i class="fa fa-list-alt text-info" title="Detail"></i></a>\
               <a href="/device/edit/{0}"><i class="fa fa-pencil text-dark" title="Edit"></i></a>\
               <a href="#" onclick="Dajaxice.device.device_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger" title="Delete"></i></a>'.format(dct['id']))
            dct.update(nms_actions='')
            # device is monitored only if it's a backhaul configured on, sector configured on or sub-station
            # checking whether device is 'backhaul configured on' or not
            try:
                if Backhaul.objects.get(bh_configured_on=current_device):
                    dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-warning"></i></a>\
                        <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>'.format(dct['id']))
            except:
                logger.info("Device is not basestation")

            # checking whether device is 'sector configured on' or not
            try:
                if Sector.objects.get(sector_configured_on=current_device):
                    dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-warning"></i></a>\
                        <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>'.format(dct['id']))
            except:
                logger.info("Device is not basestation")

            # checking whether device is 'sub station' or not
            try:
                if SubStation.objects.get(device=current_device):
                    dct.update(nms_actions='<a href="#" onclick="add_device({0});"><i class="fa fa-plus-square text-warning"></i></a>\
                        <a href="#" onclick="Dajaxice.device.add_service_form(get_service_add_form, {{\'value\': {0}}})"><i class="fa fa-plus text-success" title="Add Service"></i></a>'.format(dct['id']))
            except:
                logger.info("Device is not substation.")
        return qs

    def get_context_data(self, *args, **kwargs):
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
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData,
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

        try:
            if kwargs['object'].device_technology:
                context['device_technology'] = DeviceTechnology.objects.get(pk=kwargs['object'].device_technology).alias
            if kwargs['object'].device_vendor:
                context['device_vendor'] = DeviceVendor.objects.get(pk=kwargs['object'].device_vendor).alias
            if kwargs['object'].device_model:
                context['device_model'] = DeviceModel.objects.get(pk=kwargs['object'].device_model).alias
            if kwargs['object'].device_type:
                context['device_type'] = DeviceType.objects.get(pk=kwargs['object'].device_type).alias
            if kwargs['object'].country:
                context['country'] = Country.objects.get(pk=kwargs['object'].country).country_name
            if kwargs['object'].state:
                context['state'] = State.objects.get(pk=kwargs['object'].state).state_name
            if kwargs['object'].city:
                context['city'] = City.objects.get(pk=kwargs['object'].city).city_name
        except Exception as e:
            logger.info(e.message)

        return context


class DeviceCreate(CreateView):
    template_name = 'device/device_new.html'
    model = Device
    form_class = DeviceForm
    success_url = reverse_lazy('device_list')


    @method_decorator(permission_required('device.add_device', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceCreate, self).dispatch(*args, **kwargs)

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
        device.country = form.cleaned_data['country']
        device.state = form.cleaned_data['state']
        device.city = form.cleaned_data['city']
        device.timezone = form.cleaned_data['timezone']
        device.latitude = form.cleaned_data['latitude']
        device.longitude = form.cleaned_data['longitude']
        device.description = form.cleaned_data['description']
        device.organization_id= form.cleaned_data['organization'].id
        device.save()

        # saving site_instance --> FK Relation
        try:
            device.site_instance = SiteInstance.objects.get(name=form.cleaned_data['site_instance'])
            device.save()
        except:
            logger.info("No instance to add.")

        # # saving associated ports  --> M2M Relation (Model: DevicePort)
        # for port in form.cleaned_data['ports']:
        #     device_port = DevicePort.objects.get(name=port)
        #     device.ports.add(device_port)
        #     device.save()

        # # saving associated services  --> M2M Relation (Model: Service)
        # for service in form.cleaned_data['service']:
        #     device_service = Service.objects.get(name=service)
        #     device.service.add(device_service)
        #     device.save()

        # saving device 'parent device' --> FK Relation
        try:
            parent_device = Device.objects.get(device_name=form.cleaned_data['parent'])
            device.parent = parent_device
            device.save()
        except:
            logger.info("Device has no parent.")

        # fetching device extra fields associated with 'device type'
        try:
            device_type = DeviceType.objects.get(id=int(self.request.POST.get('device_type')))
            # it gives all device fields associated with device_type object
            device_type.devicetypefields_set.all()
        except:
            logger.info("No device type exists.")

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

        action.send( self.request.user, verb='Created', action_object=device )
        return HttpResponseRedirect( DeviceCreate.success_url )


class DeviceUpdate(UpdateView):
    template_name = 'device/device_update.html'
    model = Device
    form_class = DeviceForm
    success_url = reverse_lazy('device_list')


    @method_decorator(permission_required('device.change_device', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceUpdate, self).dispatch(*args, **kwargs)

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
        #self.object.ports = form.cleaned_data['ports']
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
        self.object.country = form.cleaned_data['country']
        self.object.state = form.cleaned_data['state']
        self.object.city = form.cleaned_data['city']
        self.object.timezone = form.cleaned_data['timezone']
        self.object.latitude = form.cleaned_data['latitude']
        self.object.longitude = form.cleaned_data['longitude']
        self.object.description = form.cleaned_data['description']
        self.object.organization=form.cleaned_data['organization']
        self.object.save()

        # saving site_instance --> FK Relation
        try:
            self.object.site_instance = SiteInstance.objects.get(name=form.cleaned_data['site_instance'])
            self.object.save()
        except Exception as site_exception:
            if settings.DEBUG:
                logger.critical("Instance(site) information missing : %s" % (site_exception),
                                exc_info=True,
                                extra={'stack': True, 'request': self.request}
                                )
            pass

        # # deleting old services of device
        # self.object.service.clear()

        # # saving associated services  --> M2M Relation (Model: Service)
        # for service in form.cleaned_data['service']:
        #     device_service = Service.objects.get(name=service)
        #     self.object.service.add(device_service)
        #     self.object.save()

        # saving device 'parent device' --> FK Relation
        try:
            parent_device = Device.objects.get(device_name=form.cleaned_data['parent'])
            self.object.parent = parent_device
            self.object.save()
        except Exception as device_parent_exception:
            if settings.DEBUG:
                logger.critical("Device Parent information missing : %s" % (device_parent_exception),
                                exc_info=True,
                                extra={'stack': True, 'request': self.request}
                                )
            pass

        # deleting old device extra field values
        try:
            DeviceTypeFieldsValue.objects.filter(device_id=self.object.id).delete()
        except Exception as device_extra_exception:
            if settings.DEBUG:
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
            if settings.DEBUG:
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

        initial_field_dict = form.initial
        def cleaned_data_field():
            cleaned_data_field_dict={}
            for field in form.cleaned_data.keys():
                # if field in ('service'):
                #     cleaned_data_field_dict[field]=map(lambda obj: obj.pk, form.cleaned_data[field])
                if field in ('parent', 'site_instance','organization'):
                    cleaned_data_field_dict[field]=form.cleaned_data[field].pk if form.cleaned_data[field] else None
                elif field in ('device_model', 'device_type', 'device_vendor', 'device_technology') and form.cleaned_data[field]:
                    cleaned_data_field_dict[field]=int(form.cleaned_data[field])
                else:
                    cleaned_data_field_dict[field]=form.cleaned_data[field]

            return cleaned_data_field_dict

        cleaned_data_field_dict=cleaned_data_field()
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        try:
            if changed_fields_dict:
                initial_field_dict['parent'] = Device.objects.get(pk=initial_field_dict['parent']).device_name \
                    if initial_field_dict['parent'] else str(None)
                initial_field_dict['organization'] = Organization.objects.get(pk=initial_field_dict['organization']).name \
                    if initial_field_dict['organization'] else str(None)
                initial_field_dict['site_instance'] = SiteInstance.objects.get(pk=initial_field_dict['site_instance']).name \
                    if initial_field_dict['site_instance'] else str(None)
                # initial_field_dict['service'] = ', '.join([Service.objects.get(pk=service).name for service in initial_field_dict['service']])\
                #     if initial_field_dict['service'] else str(None)
                initial_field_dict['device_model'] = DeviceModel.objects.get(pk=initial_field_dict['device_model']).name \
                    if initial_field_dict['device_model'] else str(None)
                initial_field_dict['device_type'] = DeviceType.objects.get(pk=initial_field_dict['device_type']).name \
                    if initial_field_dict['device_type'] else str(None)
                initial_field_dict['device_vendor'] = DeviceVendor.objects.get(pk=initial_field_dict['device_vendor']).name \
                    if initial_field_dict['device_vendor'] else str(None)
                initial_field_dict['device_technology'] = DeviceTechnology.objects.get(pk=initial_field_dict['device_technology']).name \
                    if initial_field_dict['device_technology'] else str(None)

                cleaned_data_field_dict['parent'] = Device.objects.get(pk=cleaned_data_field_dict['parent']).device_name \
                    if cleaned_data_field_dict['parent'] else str(None)
                cleaned_data_field_dict['organization'] = Organization.objects.get(pk=cleaned_data_field_dict['organization']).name \
                    if cleaned_data_field_dict['organization'] else str(None)
                cleaned_data_field_dict['site_instance'] = SiteInstance.objects.get(pk=cleaned_data_field_dict['site_instance']).name \
                    if cleaned_data_field_dict['site_instance'] else str(None)
                # cleaned_data_field_dict['service'] = ', '.join([Service.objects.get(pk=service).name for service in cleaned_data_field_dict['service'] \
                #     if cleaned_data_field_dict['service']])
                cleaned_data_field_dict['device_model'] = DeviceModel.objects.get(pk=cleaned_data_field_dict['device_model']).name \
                    if cleaned_data_field_dict['device_model'] else str(None)
                cleaned_data_field_dict['device_type'] = DeviceType.objects.get(pk=cleaned_data_field_dict['device_type']).name \
                    if cleaned_data_field_dict['device_type'] else str(None)
                cleaned_data_field_dict['device_vendor'] = DeviceVendor.objects.get(pk=cleaned_data_field_dict['device_vendor']).name \
                    if cleaned_data_field_dict['device_vendor'] else str(None)
                cleaned_data_field_dict['device_technology'] = DeviceTechnology.objects.get(pk=cleaned_data_field_dict['device_technology']).name \
                    if cleaned_data_field_dict['device_technology'] else str(None)

                verb_string = 'Changed values of Device %s from initial values '%(self.object.device_name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                                   for k in changed_fields_dict])+\
                                   ' to '+\
                                   ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
                if len(verb_string)>=255:
                    verb_string=verb_string[:250] + '...'

                action.send(self.request.user, verb=verb_string)
        except Exception as user_audit_exeption:
            action.send(self.request.user, verb="Changed the Physical Device Inventory")
            if settings.DEBUG:
                logger.error(user_audit_exeption)

        return HttpResponseRedirect(DeviceCreate.success_url)


class DeviceDelete(DeleteView):
    model = Device

    template_name = 'device/device_delete.html'
    success_url = reverse_lazy('device_list')

    @method_decorator(permission_required('device.delete_device', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device: %s'%(self.get_object().device_name))
        return super(DeviceDelete, self).delete(request, *args, **kwargs)

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
            {'mData':'actions',            'sTitle' : 'Actions', 'sWidth':'10%' ,'bSortable': False}
            ,]
        context['datatable_headers'] = json.dumps( datatable_headers )
        return context

class DeviceTypeFieldsListingTable(BaseDatatableView):
    model = DeviceTypeFields
    columns = ['field_name', 'field_display_name','device_type__name']
    order_columns = ['field_name', 'field_display_name','device_type__name']

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
        return DeviceTypeFields.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/device_fields/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/device_fields/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

            sdir = '-' if s_sort_dir == 'desc' else ' '

            sortcol = order_columns[i_sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key= itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs

    def get_context_data(self, *args, **kwargs):
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

    @method_decorator(permission_required('device.add_devicetypefieldsvalue', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceTypeFieldsCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(DeviceTypeFieldsCreate.success_url)

class DeviceTypeFieldsUpdate(UpdateView):
    template_name = 'device_extra_fields/device_extra_field_update.html'
    model = DeviceTypeFields
    form_class = DeviceTypeFieldsUpdateForm
    success_url = reverse_lazy('device_extra_field_list')

    @method_decorator(permission_required('device.change_devicetypefieldsvalue', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceTypeFieldsUpdate, self).dispatch(*args, **kwargs)

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

    @method_decorator(permission_required('device.delete_devicetypefieldsvalue', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceTypeFieldsDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device type field: %s'%(self.get_object().field_name))
        return super(DeviceTypeFieldsDelete, self).delete(request, *args, **kwargs)

# **************************************** Device Technology ****************************************

class DeviceTechnologyList(ListView):
    model = DeviceTechnology
    template_name = 'device_technology/device_technology_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceTechnologyList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                               'sTitle' : 'Name',             'sWidth':'null' },
            {'mData':'alias',                              'sTitle' : 'Alias',            'sWidth':'null' },
            {'mData':'device_vendor',                      'sTitle' : 'Device Vendor',    'sWidth':'10%'  },
            {'mData':'device_vendor__model__name',         'sTitle' : 'Device Model',     'sWidth':'10%' ,},
            {'mData':'device_vendor__model_type__name',    'sTitle' : 'Device Type',      'sWidth':'10%' ,},
            {'mData':'actions',                            'sTitle':  'Actions',          'sWidth':'10%' ,'bSortable': False}
            ]
        context['datatable_headers'] = json.dumps( datatable_headers )
        return context

class DeviceTechnologyListingTable(BaseDatatableView):
    model = DeviceTechnology
    columns = ['name', 'alias','device_vendor','device_vendor__model__name','device_vendor__model_type__name' ]
    order_columns = ['name', 'alias', 'device_vendor', 'device_vendor__model__name', 'device_vendor__model_type__name']

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
        qs_query= DeviceTechnology.objects.prefetch_related()
        qs=list()
        for dtechnology in qs_query:
            dct=dict()
            for dtechnology_vendor in dtechnology.device_vendors.values_list('name', flat=True):
                dct={
                    'id':dtechnology.id, 'name': dtechnology.name, 'alias': dtechnology.alias,
                    'device_vendor':dtechnology_vendor
                    }
                dvendor=DeviceVendor.objects.get(name=dtechnology_vendor)

                dct['device_vendor__model__name']=', '.join( dvendor.device_models.values_list('name', flat=True) )

                for dmodel in dvendor.device_models.prefetch_related():
                        dct['device_vendor__model_type__name']= ', '.join(dmodel.device_types.values_list('name', flat=True))

                qs.append(dct)
        return qs

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/technology/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/technology/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

            sdir = '-' if s_sort_dir == 'desc' else ' '

            sortcol = order_columns[i_sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key=itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs


    def get_context_data(self, *args, **kwargs):
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

    @method_decorator(permission_required('device.add_devicetechnology', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceTechnologyCreate, self).dispatch(*args, **kwargs)

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

    @method_decorator(permission_required('device.change_devicetechnology', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceTechnologyUpdate, self).dispatch(*args, **kwargs)

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

    @method_decorator(permission_required('device.delete_devicetechnology', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceTechnologyDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device technology: %s'%(self.get_object().name))
        return super(DeviceTechnologyDelete, self).delete(self, request, *args, **kwargs)


# ************************************* Device Vendor ***********************************************
class DeviceVendorList(ListView):
    model = DeviceVendor
    template_name = 'device_vendor/device_vendor_list.html'

    def get_context_data(self, **kwargs):
            context=super(DeviceVendorList, self).get_context_data(**kwargs)
            datatable_headers = [
            {'mData':'name',                   'sTitle' : 'Name',               'sWidth':'null',},
            {'mData':'alias',                  'sTitle' : 'Alias',              'sWidth':'null',},
            {'mData':'device_models',          'sTitle' : 'Device Models',      'sWidth':'null',},
            {'mData':'device_types',           'sTitle' : 'Device Types',       'sWidth':'null',},
            {'mData':'actions',                'sTitle' : 'Actions',            'sWidth':'10%' ,'bSortable': False} ]
            context['datatable_headers'] = json.dumps(datatable_headers)
            return context

class DeviceVendorListingTable(BaseDatatableView):
    model = DeviceVendor
    columns = ['name', 'alias','device_models','device_types']
    order_columns = ['name', 'alias', 'device_models', 'device_types']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
            return result_list

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        qs=list()

        qs_query= DeviceVendor.objects.prefetch_related()
        for dvendor in qs_query:
            dct=dict()
            dct={
                'id':dvendor.id,
                'name':dvendor.name,
                'alias':dvendor.alias,
                'device_models':', '.join(dvendor.device_models.values_list('name', flat=True)),
                 }
            for dmodels in dvendor.device_models.prefetch_related():
                dct['device_types']=', '.join(dmodels.device_types.values_list('name', flat=True))
            qs.append(dct)

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

            sdir = '-' if s_sort_dir == 'desc' else ' '

            sortcol = order_columns[i_sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key=itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs

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
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

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

    @method_decorator(permission_required('device.add_devicevendor', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceVendorCreate, self).dispatch(*args, **kwargs)

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

    @method_decorator(permission_required('device.change_devicevendor', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceVendorUpdate, self).dispatch(*args, **kwargs)

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

    @method_decorator(permission_required('device.delete_devicevendor', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceVendorDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device vendor: %s'%(self.get_object().name))
        return super(DeviceVendorDelete, self).delete(request, *args, **kwargs)

# ****************************************** Device Model *******************************************


class DeviceModelList(ListView):
    model = DeviceModel
    template_name = 'device_model/device_model_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceModelList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',              'sTitle' : 'Name',              'sWidth':'null',},
            {'mData':'alias',             'sTitle' : 'Alias',             'sWidth':'null',},
            {'mData':'device_types',      'sTitle' : 'Device Types',      'sWidth':'null',},
            {'mData':'actions',           'sTitle' : 'Actions',           'sWidth':'10%' ,'bSortable': False} ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class DeviceModelListingTable(BaseDatatableView):
    model = DeviceModel
    columns = ['name', 'alias', 'device_types']
    order_columns = ['name', 'alias', 'device_types']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
            return result_list

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        qs_query=DeviceModel.objects.prefetch_related()
        qs=list()
        for dmodel in qs_query:
            dct=dict()
            dct={
                'id':dmodel.id,
                'name':dmodel.name,
                'alias':dmodel.alias,
                'device_types':', '.join(dmodel.device_types.values_list('name', flat=True)),
                }
            qs.append(dct)
        return qs

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/model/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                        <a href="/model/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

            sdir = '-' if s_sort_dir == 'desc' else ' '

            sortcol = order_columns[i_sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key= itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs


    def get_context_data(self, *args, **kwargs):
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

    @method_decorator(permission_required('device.add_devicemodel', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceModelCreate, self).dispatch(*args, **kwargs)

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

    @method_decorator(permission_required('device.change_devicemodel', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceModelUpdate, self).dispatch(*args, **kwargs)

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

    @method_decorator(permission_required('device.delete_devicemodel', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceModelDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device model: %s'%(self.get_object().name))
        return super(DeviceModelDelete, self).delete(request, *args, **kwargs)

# ****************************************** Device Type *******************************************


class DeviceTypeList(ListView):
    model = DeviceType
    template_name = 'device_type/device_type_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceTypeList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                   'sTitle' : 'Name',       'sWidth':'null',},
            {'mData':'alias',                  'sTitle' : 'Alias',      'sWidth':'null',},
            {'mData':'agent_tag',              'sTitle' : 'Agent tag',  'sWidth':'null',},
            {'mData':'actions',                'sTitle' : 'Actions',    'sWidth':'10%' ,'bSortable': False}
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class DeviceTypeListingTable(BaseDatatableView):
    model = DeviceType
    columns = ['name', 'alias', 'agent_tag']
    order_columns = ['name', 'alias', 'agent_tag']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
            return result_list

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

            sdir = '-' if s_sort_dir == 'desc' else ' '

            sortcol = order_columns[i_sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key= itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs


    def get_context_data(self, *args, **kwargs):
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

    @method_decorator(permission_required('device.add_devicetype', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceTypeCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(DeviceTypeCreate.success_url)


class DeviceTypeUpdate(UpdateView):
    template_name = 'device_type/device_type_update.html'
    model = DeviceType
    form_class = DeviceTypeForm
    success_url = reverse_lazy('device_type_list')

    @method_decorator(permission_required('device.change_devicetype', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceTypeUpdate, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:

            verb_string = 'Changed values of Device Type: %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            self.object=form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(DeviceTypeUpdate.success_url)

class DeviceTypeDelete(DeleteView):
    model = DeviceType
    template_name = 'device_type/device_type_delete.html'
    success_url = reverse_lazy('device_type_list')

    @method_decorator(permission_required('device.delete_devicetype', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceTypeDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device type: %s'%(self.get_object().name))
        return super(DeviceTypeDelete, self).delete(request, *args, **kwargs)

# ****************************************** Device Type *******************************************
class DevicePortList(ListView):
    model = DevicePort
    template_name = 'device_port/device_ports_list.html'

    def get_context_data(self, **kwargs):
        context=super(DevicePortList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',             'sTitle' : 'Name',          'sWidth':'null', },
            {'mData':'alias',            'sTitle' : 'Alias',         'sWidth':'null', },
            {'mData':'value',            'sTitle' : 'Value',         'sWidth':'null', },
            {'mData':'actions',          'sTitle' : 'Actions',       'sWidth':'10%', 'bSortable': False },
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DevicePortListingTable(BaseDatatableView):
    model = DevicePort
    columns = ['name', 'alias', 'value']
    order_columns = ['name', 'alias', 'value']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DevicePort.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/device_port/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/device_port/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
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

class DevicePortDetail(DetailView):
    model = DevicePort
    template_name = 'device_port/device_port_detail.html'


class DevicePortCreate(CreateView):
    template_name = 'device_port/device_port_new.html'
    model = DevicePort
    form_class = DevicePortForm
    success_url = reverse_lazy('device_ports_list')

    @method_decorator(permission_required('device.add_deviceport', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DevicePortCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(DevicePortCreate.success_url)


class DevicePortUpdate(UpdateView):
    template_name = 'device_port/device_port_update.html'
    model = DevicePort
    form_class = DevicePortForm
    success_url = reverse_lazy('device_ports_list')

    @method_decorator(permission_required('device.change_deviceport', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DevicePortUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:

            verb_string = 'Changed values of DevicePort: %s from initial values '%(self.object.name) +\
                          ', '.join(['%s: %s' %(k, initial_field_dict[k]) for k in changed_fields_dict])+\
                          ' to '+\
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            self.object=form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect( DevicePortUpdate.success_url )


class DevicePortDelete(DeleteView):
    model = DevicePort
    template_name = 'device_port/device_port_delete.html'
    success_url = reverse_lazy('device_ports_list')
    
    @method_decorator(permission_required('device.delete_deviceport', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DevicePortDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device port: %s'%(self.get_object().name))
        return super(DevicePortDelete, self).delete(request, *args, **kwargs)

class DeviceFrequencyListing(ListView):
    model = DeviceFrequency
    template_name = 'device_frequency/device_frequency_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceFrequencyListing, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'value',            'sTitle' : 'Value',        'sWidth':'null', },
            {'mData':'color_hex_value',  'sTitle' : 'Hex Value',     'sWidth':'null', },
            {'mData':'actions',          'sTitle' : 'Actions',       'sWidth':'10%', 'bSortable': False },
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class DeviceFrequencyListingTable(BaseDatatableView):
    model = DeviceFrequency
    columns = ['value', 'color_hex_value']
    order_columns = ['value', 'color_hex_value']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DeviceFrequency.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            if "color_hex_value" in dct:
                dct.update(color_hex_value="<div style='float:left; display:block; height:20px; width:20px; background:{0}'>"
                       "</div>"\
                       "<span style='margin-left: 5px;'>{0}</span>".
                       format(dct["color_hex_value"]))
            dct.update(actions='<a href="/frequency/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/frequency/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
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

class DeviceFrequencyCreate(CreateView):
    template_name = 'device_frequency/device_frequency_new.html'
    model = DeviceFrequency
    form_class = DeviceFrequencyForm
    success_url = reverse_lazy('device_frequency_list')

    @method_decorator(permission_required('device.add_devicefrequency', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceFrequencyCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(DeviceFrequencyCreate.success_url)

class DeviceFrequencyUpdate(UpdateView):
    template_name = 'device_frequency/device_frequency_update.html'
    model = DeviceFrequency
    form_class = DeviceFrequencyForm
    success_url = reverse_lazy('device_frequency_list')

    @method_decorator(permission_required('device.change_devicefrequency', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceFrequencyUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(DeviceFrequencyUpdate.success_url)

class DeviceFrequencyDelete(DeleteView):
    model = DeviceFrequency
    template_name = 'device_frequency/device_frequency_delete.html'
    success_url = reverse_lazy('device_frequency_list')

    @method_decorator(permission_required('device.delete_devicefrequency', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceFrequencyDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device frequency: %s'%(self.get_object().value))
        return super(DeviceFrequencyDelete, self).delete(request, *args, **kwargs)
