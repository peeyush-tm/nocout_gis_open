from django.shortcuts import render
import json
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from machine.forms import MachineForm
from models import Machine
from nocout.utils.util import DictDiffer
from django.db.models import Q
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin


#************************************** Machine *****************************************
class MachineList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render Machine List Page.
    """

    model = Machine
    template_name = 'machine/machines_list.html'
    required_permissions = ('machine.view_machine',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context=super(MachineList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                     'sTitle' : 'Name',                 'sWidth':'auto',},
            {'mData':'alias',                    'sTitle' : 'Alias',                'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'machine_ip',               'sTitle' : 'Machine IP',           'sWidth':'auto',},
            {'mData':'agent_port',               'sTitle' : 'Agent Port',           'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'description',              'sTitle' : 'Description',          'sWidth':'auto',}
        ]
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class MachineListingTable(PermissionsRequiredMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class based View to render Machine Data table.
    """
    model = Machine
    required_permissions = ('machine.view_machine',)
    columns = ['name', 'alias', 'machine_ip',  'agent_port', 'description']
    order_columns = ['name', 'alias', 'machine_ip',  'agent_port', 'description']


    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Machine.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """

        json_data = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in json_data:
            dct.update(actions='<a href="/machine/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/machine/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


class MachineDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the machine detail.
    """
    model = Machine
    required_permissions = ('machine.view_machine',)
    template_name = 'machine/machine_detail.html'


class MachineCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new machine.
    """
    template_name = 'machine/machine_new.html'
    model = Machine
    form_class = MachineForm
    success_url = reverse_lazy('machines_list')
    required_permissions = ('machine.add_machine',)


class MachineUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update machine.
    """
    template_name = 'machine/machine_update.html'
    model = Machine
    form_class = MachineForm
    success_url = reverse_lazy('machines_list')
    required_permissions = ('machine.change_machine',)


class MachineDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class based View to delete the machine
    """
    model = Machine
    template_name = 'machine/machine_delete.html'
    success_url = reverse_lazy('machines_list')
    required_permissions = ('machine.delete_machine',)
