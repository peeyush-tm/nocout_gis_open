import json
from actstream import action
from django.db.models.query import ValuesQuerySet
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
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
        datatable_headers = [
            {'mData':'name',                'sTitle' : 'Name',          'sWidth':'null',},
            {'mData':'alias',               'sTitle' : 'Alias',         'sWidth':'null',},
            {'mData':'parent__name',        'sTitle' : 'Parent',        'sWidth':'null',},
            {'mData':'city',                'sTitle' : 'City',          'sWidth':'null',},
            {'mData':'state',               'sTitle' : 'State',         'sWidth':'null',},
            {'mData':'country',             'sTitle' : 'Country',       'sWidth':'null',},
            {'mData':'description',         'sTitle' : 'Description',   'sWidth':'null','bSortable': False},]

        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%','bSortable': False })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class OrganizationListingTable(BaseDatatableView):
    model = Organization
    columns = ['name', 'alias', 'parent__name','city','state','country', 'description']
    order_columns = ['name',  'alias', 'parent__name', 'city', 'state', 'country']

    def logged_in_user_organization_ids(self):
        organization_descendants_ids= list(self.request.user.userprofile.organization.get_children()\
                                           .values_list('id', flat=True)) + [ self.request.user.userprofile.organization.id ]
        return organization_descendants_ids


    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query=[]
            organization_descendants_ids= self.logged_in_user_organization_ids()
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__icontains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query) + ", id__in = %s"%organization_descendants_ids + \
                          ").values(*"+str(self.columns+['id'])+")"
            exec exec_query
        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        organization_descendants_ids= self.logged_in_user_organization_ids()
        return Organization.objects.filter(pk__in=organization_descendants_ids).values(*self.columns + ['id'])

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
        return super(ModelFormMixin, self).form_valid(form)

class OrganizationUpdate(UpdateView):
    template_name = 'organization/organization_update.html'
    model = Organization
    form_class = OrganizationForm
    success_url = reverse_lazy('organization_list')


    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Organization : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( OrganizationUpdate.success_url )


class OrganizationDelete(DeleteView):
    model = Organization
    template_name = 'organization/organization_delete.html'
    success_url = reverse_lazy('organization_list')



