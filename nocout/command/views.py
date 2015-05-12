"""
==========================================================================
Module contains views and related functionality specific to 'command' app.
==========================================================================

Location:
* /nocout_gis/nocout/command/views.py

List of constructs:
=======
Classes
=======
* CommandList
* CommandListingTable
* CommandDetail
* CommandCreate
* CommandUpdate
* CommandDelete
"""

import json
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from models import Command
from forms import CommandForm
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin, ValuesQuerySetMixin


class CommandList(PermissionsRequiredMixin, ListView):
    """
    View to show headers of users datatable.
        URL - 'http://127.0.0.1:8000/command'
    """
    model = Command
    template_name = 'command/commands_list.html'
    required_permissions = ('command.view_command',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """
        context = super(CommandList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', },
            {'mData': 'command_line', 'sTitle': 'Command Line', 'sWidth': 'auto', },
        ]
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class CommandListingTable(PermissionsRequiredMixin, ValuesQuerySetMixin, DatatableSearchMixin, BaseDatatableView):
    """
    View to show list of commands in datatable.
        URL - 'http://127.0.0.1:8000/command'
    """
    model = Command
    required_permissions = ('command.view_command',)
    columns = ['name', 'alias', 'command_line']
    order_columns = ['name', 'alias', 'command_line']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            dct.update(actions='<a href="/command/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/command/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


class CommandDetail(PermissionsRequiredMixin, DetailView):
    """
    Show details of the single command instance.
    """
    model = Command
    required_permissions = ('command.view_command',)
    template_name = 'command/command_detail.html'


class CommandCreate(PermissionsRequiredMixin, CreateView):
    """
    Create a new user command, with a response rendered by template.
    """
    template_name = 'command/command_new.html'
    model = Command
    form_class = CommandForm
    success_url = reverse_lazy('commands_list')
    required_permissions = ('command.add_command',)


class CommandUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Update a new command instance, with a response rendered by template.
    """
    template_name = 'command/command_update.html'
    model = Command
    form_class = CommandForm
    success_url = reverse_lazy('commands_list')
    required_permissions = ('command.change_command',)


class CommandDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Delete a single instance from database.
    """
    model = Command
    template_name = 'command/command_delete.html'
    success_url = reverse_lazy('commands_list')
    required_permissions = ('command.delete_command',)
