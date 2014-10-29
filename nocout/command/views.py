import json
from django.contrib.auth.decorators import permission_required
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from models import Command
from .forms import CommandForm
from nocout.utils.util import DictDiffer
from django.db.models import Q


class CommandList(ListView):
    """
    Generic Class based View to List the Commands.
    """

    model = Command
    template_name = 'command/commands_list.html'

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


class CommandListingTable(BaseDatatableView):
    """
    A generic class based view for the command data table rendering.

    """
    model = Command
    columns = ['name', 'alias', 'command_line']
    order_columns = ['name', 'alias', 'command_line']

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
        return Command.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/command/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/command/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class CommandDetail(DetailView):
    """
    Class Based Detail View

    """
    model = Command
    template_name = 'command/command_detail.html'


class CommandCreate(CreateView):
    """
    Class based View to create Command

    """
    template_name = 'command/command_new.html'
    model = Command
    form_class = CommandForm
    success_url = reverse_lazy('commands_list')

    @method_decorator(permission_required('command.add_command', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.

        """
        return super(CommandCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        to check the validation of the form before submit.
        and to log the activity in the user log
        """
        self.object=form.save()
        return HttpResponseRedirect(CommandCreate.success_url)


class CommandUpdate(UpdateView):
    """
    Class based View to update Command

    """
    template_name = 'command/command_update.html'
    model = Command
    form_class = CommandForm
    success_url = reverse_lazy('commands_list')

    @method_decorator(permission_required('command.change_command', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.

        """
        return super(CommandUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        to check the validation of the form before submit.
        and to log the activity in the user log
        """
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:

            verb_string = 'Changed values of Command: %s from initial values '%(self.object.command_name) +\
                          ', '.join(['%s: %s' %(k, initial_field_dict[k]) for k in changed_fields_dict])+\
                          ' to '+\
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            self.object=form.save()
        return HttpResponseRedirect( CommandUpdate.success_url )


class CommandDelete(DeleteView):
    """
    Class based View to delete Command

    """
    model = Command
    template_name = 'command/command_delete.html'
    success_url = reverse_lazy('commands_list')
    
    @method_decorator(permission_required('command.delete_command', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.

        """
        return super(CommandDelete, self).dispatch(*args, **kwargs)

