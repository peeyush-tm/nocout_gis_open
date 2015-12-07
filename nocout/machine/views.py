"""
==========================================================================
Module contains views and related functionality specific to 'machine' app.
==========================================================================

Location:
* /nocout_gis/nocout/machine/views.py

List of constructs:
=======
Classes
=======
* MachineList
* MachineListingTable
* MachineDetail
* MachineCreate
* MachineUpdate
* MachineDelete
"""

import json
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from machine.forms import MachineForm
from models import Machine
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin, ValuesQuerySetMixin, AdvanceFilteringMixin
from user_profile.utils.auth import in_group


class MachineList(PermissionsRequiredMixin, ListView):
    """
    View to show headers of machines datatable.
        URL - 'http://127.0.0.1:8000/command'
    """
    model = Machine
    template_name = 'machine/machines_list.html'
    required_permissions = ('machine.view_machine',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(MachineList, self).get_context_data(**kwargs)

        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto'},
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'machine_ip', 'sTitle': 'Machine IP', 'sWidth': 'auto'},
            {'mData': 'agent_port', 'sTitle': 'Agent Port', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto'}
        ]

        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)

        return context


class MachineListingTable(PermissionsRequiredMixin, ValuesQuerySetMixin, DatatableSearchMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    View to show list of machines in datatable.
        URL - 'http://127.0.0.1:8000/machine'
    """
    model = Machine
    required_permissions = ('machine.view_machine',)
    columns = ['name', 'alias', 'machine_ip', 'agent_port', 'description']
    order_columns = ['name', 'alias', 'machine_ip', 'agent_port', 'description']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        for dct in json_data:
            dct.update(actions='<a href="/machine/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/machine/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))

        return json_data


class MachineDetail(PermissionsRequiredMixin, DetailView):
    """
    Show details of the single machine instance.
    """
    model = Machine
    required_permissions = ('machine.view_machine',)
    template_name = 'machine/machine_detail.html'


class MachineCreate(PermissionsRequiredMixin, CreateView):
    """
    Create a new machine, with a response rendered by template.
    """
    template_name = 'machine/machine_new.html'
    model = Machine
    form_class = MachineForm
    success_url = reverse_lazy('machines_list')
    required_permissions = ('machine.add_machine',)


class MachineUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Update a new machine instance, with a response rendered by template.
    """
    template_name = 'machine/machine_update.html'
    model = Machine
    form_class = MachineForm
    success_url = reverse_lazy('machines_list')
    required_permissions = ('machine.change_machine',)


class MachineDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Delete a single instance from database.
    """
    model = Machine
    template_name = 'machine/machine_delete.html'
    success_url = reverse_lazy('machines_list')
    required_permissions = ('machine.delete_machine',)
