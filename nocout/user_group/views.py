from actstream import action
from django.db.models import Q
import json
from django.db.models.query import ValuesQuerySet
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from device_group.models import DeviceGroup
from nocout.utils.util import DictDiffer
from user_group.models import UserGroup, Organization
from forms import UserGroupForm

class UserGroupList(ListView):
    model = UserGroup
    template_name = 'user_group/ug_list.html'

    def get_context_data(self, **kwargs):
        context=super(UserGroupList, self).get_context_data(**kwargs)
        datatable_headers= ('name', 'alias', 'address', 'location', 'parent__name', 'device_group__name',
                            'device_group__location','actions')
        context['datatable_headers'] = json.dumps([ dict(mData=key, sTitle = key.replace('_',' ').title(),
                                    sWidth='10%' if key=='actions' else 'null') for key in datatable_headers ])
        return context

class UserGroupListingTable(BaseDatatableView):
    model = UserGroup
    columns = ['name', 'alias', 'address', 'location', 'parent__name', 'device_group__name', 'device_group__location']
    order_columns = ['name', 'alias', 'address', 'location', 'parent__name', 'device_group__name', 'device_group__location']

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
        return UserGroup.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/user_group/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="#" onclick="Dajaxice.user_group.user_group_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class UserGroupDetail(DetailView):
    model = UserGroup
    template_name = 'user_group/ug_detail.html'

class UserGroupCreate(CreateView):
    template_name = 'user_group/ug_new.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #Add the default group if the parent field is None
        # if not self.object.parent:
        #     self.object.parent=Default_group
        self.object.save()
        action.send(self.request.user, verb=u'created', action_object=self.object)

        for dg in form.cleaned_data['device_group']:
            Organization.objects.create(user_group=self.object, device_group=dg)
        return super(ModelFormMixin, self).form_valid(form)

class UserGroupUpdate(UpdateView):
    template_name = 'user_group/ug_update.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')

    def form_valid(self, form):
        #IntegrityError: (1062, "Duplicate entry 'test_group4' for key 'name'")
        #TODO:Disable the edit of name from the UI (name should be unique)
        self.object = form.save(commit=False)
        if form.cleaned_data['device_group']:
            Organization.objects.filter( user_group = self.object ).delete()

            for dg in form.cleaned_data['device_group']:
                Organization.objects.create(user_group=self.object, device_group=dg)

        UserGroup.objects.filter(name=self.object.name).update( alias=self.object.alias, address=self.object.address,
                                                      location=self.object.location, parent=self.object.parent )

        initial_field_dict = { field : [form.initial[field]]  if field in ('device_group') else form.initial[field]
                               for field in form.initial.keys() }

        def cleaned_data_field():
            cleaned_data_field_dict={}
            for field in form.cleaned_data.keys():
                if field in ('device_group'):
                    cleaned_data_field_dict[field]=map( lambda obj: obj.pk, form.cleaned_data[field])
                elif field in ('parent'):
                    cleaned_data_field_dict[field]=form.cleaned_data[field].pk if form.cleaned_data[field] else None
                else:
                    cleaned_data_field_dict[field]=form.cleaned_data[field]

            return cleaned_data_field_dict

        cleaned_data_field_dict=cleaned_data_field()


        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            initial_field_dict['parent'] = UserGroup.objects.get(pk=initial_field_dict['parent']).name if initial_field_dict['parent'] else str(None)
            initial_field_dict['device_group'] = DeviceGroup.objects.get(pk=initial_field_dict['device_group'][0]).name
            cleaned_data_field_dict['parent'] = UserGroup.objects.get(pk=cleaned_data_field_dict['parent']).name if cleaned_data_field_dict['parent'] else str(None)
            cleaned_data_field_dict['device_group'] = DeviceGroup.objects.get(pk=cleaned_data_field_dict['device_group'][0]).name

            verb_string = 'Changed values of User Group %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            action.send(self.request.user, verb=verb_string)

        return super(ModelFormMixin, self).form_valid(form)



class UserGroupDelete(DeleteView):
    model = UserGroup
    template_name = 'user_group/ug_delete.html'
    success_url = reverse_lazy('ug_list')

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting user group: %s'%(self.object.name))
        super(UserGroupDelete, self).delete(self, request, *args, **kwargs)

