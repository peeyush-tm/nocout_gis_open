from django.db.models import Q
import json
from django.db.models.query import ValuesQuerySet
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from user_group.models import UserGroup, Organization
from forms import UserGroupForm

class UserGroupList(ListView):
    model = UserGroup
    template_name = 'user_group/ug_list.html'

    def get_context_data(self, **kwargs):
        context=super(UserGroupList, self).get_context_data(**kwargs)
        datatable_headers= ('name', 'alias', 'address', 'location', 'parent__name', 'device_group__name', 'device_group__location')
        context['datatable_headers'] = json.dumps([ dict(mData=key, sTitle = key.replace('_',' ').title()) for key in datatable_headers ])
        return context

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
        return super(ModelFormMixin, self).form_valid(form)



class UserGroupDelete(DeleteView):
    model = UserGroup
    template_name = 'user_group/ug_delete.html'
    success_url = reverse_lazy('ug_list')


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
            exec_query += ").values(*"+str(self.columns)+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return UserGroup.objects.values(*self.columns)

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
            # sanity_dicts_list = [OrderedDict({'dict_final_key':'full_name','dict_key1':'first_name', 'dict_key2':'last_name' }),
            # OrderedDict({'dict_final_key':'manager_name', 'dict_key1':'parent__first_name', 'dict_key2':'parent__last_name'})]
            # qs, qs_headers = Datatable_Generation( qs, sanity_dicts_list ).main()

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

