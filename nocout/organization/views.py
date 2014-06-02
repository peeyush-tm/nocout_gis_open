import json
from actstream import action
from django.db.models.query import ValuesQuerySet
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from device_group.models import DeviceGroup
from .forms import OrganizationForm
from .models import Organization
from nocout.utils.jquery_datatable_generation import Datatable_Generation
from nocout.utils.util import date_handler, DictDiffer
from user_group.models import UserGroup


class OrganizationList(ListView):
    model = Organization
    template_name = 'organization/organization_list.html'

    def get_context_data(self, **kwargs):
        context=super(OrganizationList, self).get_context_data(**kwargs)
        datatable_headers= ('name', 'description', 'user_group__name', 'device_group__name','actions')
        context['datatable_headers'] = json.dumps([ dict(mData=key, sTitle = key.replace('_',' ').title(),
                                    sWidth='10%' if key=='actions' else 'null') for key in datatable_headers ])
        return context

class OrganizationListingTable(BaseDatatableView):
    model = Organization
    columns = ['name', 'description', 'user_group__name', 'device_group__name']
    order_columns = ['name', 'description', 'user_group__name', 'device_group__name']

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
        return Organization.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/organization/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/organization/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class OrganizationDetail(DetailView):
    model = Organization
    template_name = 'organization/organization_detail.html'


class OrganizationCreate(CreateView):
    template_name = 'organization/organization_new.html'
    model = Organization
    form_class = OrganizationForm
    success_url = reverse_lazy('organization_list')

    def form_valid(self, form):
        self.object=form.save()
        action.send( self.request.user, verb='Created', action_object = self.object )

class OrganizationUpdate(UpdateView):
    template_name = 'organization/organization_update.html'
    model = Organization
    form_class = OrganizationForm
    success_url = reverse_lazy('organization_list')


    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field].pk if field in ('user_group','device_group')  and form.cleaned_data[field]
                                    else form.cleaned_data[field] for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            initial_field_dict['user_group']=UserGroup.objects.get( pk= initial_field_dict['user_group']).name if initial_field_dict['user_group'] else str(None)
            cleaned_data_field_dict['device_group']=DeviceGroup.objects.get( pk= initial_field_dict['device_group']).name if initial_field_dict['device_group'] else str(None)

            verb_string = 'Changed values of Organization : %s from initial values '%(self.object.name) + \
                          ', '.join(['%s: %s' %(k, initial_field_dict[k]) for k in changed_fields_dict])+\
                           ' to '+\
                           ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( OrganizationUpdate.success_url )


class OrganizationDelete(DeleteView):
    model = Organization
    template_name = 'organization/organization_delete.html'
    success_url = reverse_lazy('organization_list')



