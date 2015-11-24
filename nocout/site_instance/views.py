"""
================================================================================
Module contains views and related functionality specific to 'site_instance' app.
================================================================================

Location:
* /nocout_gis/nocout/site_instance/views.py

List of constructs:
=======
Classes
=======
* SiteInstanceList
* SiteInstanceListingTable
* SiteInstanceDetail
* SiteInstanceCreate
* SiteInstanceUpdate
* SiteInstanceDelete
"""

import json
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from models import SiteInstance
from forms import SiteInstanceForm
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin, ValuesQuerySetMixin, AdvanceFilteringMixin
from user_profile.utils.auth import in_group


class SiteInstanceList(PermissionsRequiredMixin, ListView):
    """
    View to show headers of site instances datatable.
        URL - 'http://127.0.0.1:8000/site/'
    """
    model = SiteInstance
    template_name = 'site_instance/site_instance_list.html'
    required_permissions = ('site_instance.view_siteinstance',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(SiteInstanceList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'is_device_change', 'sTitle': '', 'sWidth': 'auto'},
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'machine__name', 'sTitle': 'Machine', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'live_status_tcp_port', 'sTitle': 'Live Status TCP Port', 'sWidth': 'auto',
             'sClass': 'hidden-xs'},
            {'mData': 'web_service_port', 'sTitle': 'Web Service Port', 'sWidth': 'auto', },
            {'mData': 'username', 'sTitle': 'Username', 'sWidth': 'auto', },
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
            datatable_headers.append({'mData': 'nms_actions', 'sTitle': 'NMS Actions', 'sWidth': '8%',
                                      'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class SiteInstanceListingTable(PermissionsRequiredMixin, DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    View to show list of site instances in datatable.
        URL - 'http://127.0.0.1:8000/site/'
    """
    model = SiteInstance
    required_permissions = ('site_instance.view_siteinstance',)
    columns = ['is_device_change', 'name', 'alias', 'machine__name', 'live_status_tcp_port', 'web_service_port', 'username']
    order_columns = [
        'is_device_change',
        'name', 
        'alias', 
        'machine__name', 
        'live_status_tcp_port', 
        'web_service_port', 
        'username'
    ]

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            
            icon = ""
            try:
                if dct['is_device_change'] == 1:
                    icon = '<i class="fa fa-circle red-dot"></i>'
                else:
                    icon = '<i class="fa fa-circle green-dot"></i>'
            except Exception as e:
                icon = ""
            dct.update(is_device_change=icon)
            try:
                dct.update(actions='<a href="/site/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                    <a href="/site/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct['id']))
                dct.update(nms_actions='<a href="javascript:;" onclick="sync_devices();">\
                    <i class="fa fa-refresh text-danger"title="Sync Device"></i></a>'.format(dct['id']))
            except Exception as e:
                pass
        return json_data


class SiteInstanceDetail(PermissionsRequiredMixin, DetailView):
    """
    Show details of the single site instance.
    """
    model = SiteInstance
    required_permissions = ('site_instance.view_siteinstance',)
    template_name = 'site_instance/site_instance_detail.html'


class SiteInstanceCreate(PermissionsRequiredMixin, CreateView):
    """
    Create a new site, with a response rendered by template.
    """
    template_name = 'site_instance/site_instance_new.html'
    model = SiteInstance
    form_class = SiteInstanceForm
    success_url = reverse_lazy('site_instance_list')
    required_permissions = ('site_instance.add_siteinstance',)


class SiteInstanceUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Update a new site instance, with a response rendered by template.
    """
    template_name = 'site_instance/site_instance_update.html'
    model = SiteInstance
    form_class = SiteInstanceForm
    success_url = reverse_lazy('site_instance_list')
    required_permissions = ('site_instance.change_siteinstance',)


class SiteInstanceDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Delete a single instance from database.
    """
    model = SiteInstance
    template_name = 'site_instance/site_instance_delete.html'
    success_url = reverse_lazy('site_instance_list')
    required_permissions = ('site_instance.delete_siteinstance',)
