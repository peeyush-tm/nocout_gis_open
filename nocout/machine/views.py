from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
import json
from actstream import action
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from machine.forms import MachineForm
from models import Machine
from nocout.utils.util import DictDiffer


#************************************** Machine *****************************************
class MachineList(ListView):
    model = Machine
    template_name = 'machine/machines_list.html'

    def get_context_data(self, **kwargs):
        context=super(MachineList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                     'sTitle' : 'Name',                 'sWidth':'null',},
            {'mData':'alias',                    'sTitle' : 'Alias',                'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'machine_ip',               'sTitle' : 'Machine IP',           'sWidth':'null',},
            {'mData':'agent_port',               'sTitle' : 'Agent Port',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'description',              'sTitle' : 'Description',          'sWidth':'null',},
            {'mData':'actions',                  'sTitle' : 'Actions',              'sWidth':'10%' ,}
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class MachineListingTable(BaseDatatableView):
    model = MachineList
    columns = ['name', 'alias', 'machine_ip',  'agent_port', 'description']
    order_columns = ['name', 'alias', 'machine_ip',  'agent_port', 'description']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Machine.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/machine/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/machine/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
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

class MachineDetail(DetailView):
    model = Machine
    template_name = 'machine/machine_detail.html'


class MachineCreate(CreateView):
    template_name = 'machine/machine_new.html'
    model = Machine
    form_class = MachineForm
    success_url = reverse_lazy('machines_list')

    @method_decorator(permission_required('machine.add_machine', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(MachineCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(MachineCreate.success_url)


class MachineUpdate(UpdateView):
    template_name = 'machine/machine_update.html'
    model = Machine
    form_class = MachineForm
    success_url = reverse_lazy('machines_list')

    @method_decorator(permission_required('machine.change_machine', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(MachineUpdate, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Machine : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( MachineUpdate.success_url )

class MachineDelete(DeleteView):
    model = Machine
    template_name = 'machine/machine_delete.html'
    success_url = reverse_lazy('machines_list')

    @method_decorator(permission_required('machine.delete_machine', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(MachineDelete, self).dispatch(*args, **kwargs)



