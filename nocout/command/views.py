import json
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from models import Command
from .forms import CommandForm
from nocout.utils.util import DictDiffer
from django.db.models import Q
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin, ValuesQuerySetMixin


class CommandList(PermissionsRequiredMixin, ListView):
    """
    Generic Class based View to List the Commands.
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
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class CommandListingTable(PermissionsRequiredMixin, ValuesQuerySetMixin, DatatableSearchMixin, BaseDatatableView):
    """
    A generic class based view for the command data table rendering.

    """
    model = Command
    required_permissions = ('command.view_command',)
    columns = ['name', 'alias', 'command_line']
    order_columns = ['name', 'alias', 'command_line']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """

        json_data = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in json_data:
            dct.update(actions='<a href="/command/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/command/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


class CommandDetail(PermissionsRequiredMixin, DetailView):
    """
    Class Based Detail View

    """
    model = Command
    required_permissions = ('command.view_command',)
    template_name = 'command/command_detail.html'


class CommandCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based View to create Command

    """
    template_name = 'command/command_new.html'
    model = Command
    form_class = CommandForm
    success_url = reverse_lazy('commands_list')
    required_permissions = ('command.add_command',)


class CommandUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based View to update Command

    """
    template_name = 'command/command_update.html'
    model = Command
    form_class = CommandForm
    success_url = reverse_lazy('commands_list')
    required_permissions = ('command.change_command',)


class CommandDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete Command

    """
    model = Command
    template_name = 'command/command_delete.html'
    success_url = reverse_lazy('commands_list')
    required_permissions = ('command.delete_command',)
