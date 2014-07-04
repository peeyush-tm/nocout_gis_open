from django.contrib.auth.decorators import permission_required
from django.db.models.query import ValuesQuerySet
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from models import SiteInstance
from forms import SiteInstanceForm
from django.http.response import HttpResponseRedirect
from nocout.utils.util import DictDiffer
from actstream import action

import json

class SiteInstanceList(ListView):
    model = SiteInstance
    template_name = 'site_instance/site_instance_list.html'

    def get_context_data(self, **kwargs):
        context=super(SiteInstanceList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                   'sTitle' : 'Name',            'sWidth':'null',},
            {'mData':'alias',                  'sTitle' : 'Alias',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'site_ip',                'sTitle' : 'Site IP',         'sWidth':'null',},
            {'mData':'machine__name',                'sTitle' : 'Machine',         'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'live_status_tcp_port',   'sTitle' : 'Live Status TCP PORT','sWidth':'null','sClass':'hidden-xs'},
            {'mData':'actions',                'sTitle' : 'Actions',             'sWidth':'5%' ,}
            ,]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class SiteInstanceListingTable(BaseDatatableView):
    model = SiteInstance
    columns = ['name', 'alias','site_ip', 'machine__name', 'live_status_tcp_port']
    order_columns = ['name', 'alias', 'site_ip', 'machine__name', 'live_status_tcp_port']

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
        return SiteInstance.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/site/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/site/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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



class SiteInstanceDetail(DetailView):
    model = SiteInstance
    template_name = 'site_instance/site_instance_detail.html'


class SiteInstanceCreate(CreateView):
    template_name = 'site_instance/site_instance_new.html'
    model = SiteInstance
    form_class = SiteInstanceForm
    success_url = reverse_lazy('site_instance_list')

    @method_decorator(permission_required('site_instance.add_siteinstance', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SiteInstanceCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(SiteInstanceCreate.success_url)

class SiteInstanceUpdate(UpdateView):
    template_name = 'site_instance/site_instance_update.html'
    model = SiteInstance
    form_class = SiteInstanceForm
    success_url = reverse_lazy('site_instance_list')

    @method_decorator(permission_required('site_instance.change_siteinstance', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SiteInstanceUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer( initial_field_dict, cleaned_data_field_dict ).changed()

        if changed_fields_dict:

            verb_string = 'Changed values of Site Instance: %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object=form.save()
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(SiteInstanceUpdate.success_url)


class SiteInstanceDelete(DeleteView):
    model = SiteInstance
    template_name = 'site_instance/site_instance_delete.html'
    success_url = reverse_lazy('site_instance_list')

    @method_decorator(permission_required('site_instance.delete_siteinstance', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SiteInstanceDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting site instance: %s'%(self.get_object().name))
        return super(SiteInstanceDelete, self).delete(request, *args, **kwargs)