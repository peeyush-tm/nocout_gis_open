import json
from actstream import action
from django.db.models.query import ValuesQuerySet
from django.http.response import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from device_group.models import DeviceGroup
from forms import DeviceGroupForm
from django.db.models import Q
from nocout.utils.util import DictDiffer
from user_group.models import UserGroup


class DeviceGroupList(ListView):
    model = DeviceGroup
    template_name = 'device_group/dg_list.html'

    def get_context_data(self, **kwargs):
        context=super(DeviceGroupList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                   'sTitle' : 'Name',              'sWidth':'null',},
            {'mData':'alias',                  'sTitle' : 'Alias',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'parent__name',           'sTitle' : 'Parent Name',       'sWidth':'null',},
            {'mData':'location',               'sTitle' : 'Location',          'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'address',                'sTitle' : 'Address',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'actions',                'sTitle' : 'Actions',           'sWidth':'5%' ,}
            ,]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class DeviceGroupListingTable(BaseDatatableView):
    model = DeviceGroup
    columns = ['name', 'alias', 'parent__name', 'location','address']
    order_columns = ['name', 'alias', 'parent__name', 'location','address']

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
        return DeviceGroup.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/device_group/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="#" onclick="Dajaxice.device_group.device_group_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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


class DeviceGroupDetail(DetailView):
    model = DeviceGroup
    template_name = 'device_group/dg_detail.html'


class DeviceGroupCreate(CreateView):
    template_name = 'device_group/dg_new.html'
    model = DeviceGroup
    form_class = DeviceGroupForm
    success_url = reverse_lazy('dg_list')

    def form_valid( self, form ):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect( DeviceGroupCreate.success_url )


class DeviceGroupUpdate(UpdateView):
    template_name = 'device_group/dg_update.html'
    model = DeviceGroup
    form_class = DeviceGroupForm
    success_url = reverse_lazy('dg_list')

    def form_valid( self, form ):

        initial_field_dict = { field : [ form.initial[field] ]  if field in ('parent') else form.initial[field]
                               for field in form.initial.keys() }

        cleaned_data_field_dict = { field : [form.cleaned_data[field].pk]
        if field in ('parent') and  form.cleaned_data[field] else form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()

        if changed_fields_dict:
            initial_field_dict['parent'] = DeviceGroup.objects.get(pk=initial_field_dict['parent'][0]).name if initial_field_dict['parent'][0] else str(None)
            cleaned_data_field_dict['parent']=DeviceGroup.objects.get(pk=cleaned_data_field_dict['parent'][0]).name if cleaned_data_field_dict['parent'] else str(None)

            verb_string = 'Changed values of Device Group: %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            action.send(self.request.user, verb=verb_string)
            self.object=form.save()

        return HttpResponseRedirect( DeviceGroupCreate.success_url )



class DeviceGroupDelete(DeleteView):
    model = DeviceGroup
    template_name = 'device_group/dg_delete.html'
    success_url = reverse_lazy('dg_list')

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting device group: %s'%(self.object.name))
        super(DeviceGroupDelete, self).delete(self, request, *args, **kwargs)




