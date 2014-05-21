from django.db.models import Q
from django.db.models.query import ValuesQuerySet
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from nocout.utils.jquery_datatable_generation import Datatable_Generation
from user_profile.models import UserProfile, Department, Roles
from forms import UserForm
from django.http.response import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from collections import OrderedDict
from django_datatables_view.base_datatable_view import BaseDatatableView
import json


class UserList(ListView):
    model = UserProfile
    template_name = 'user_profile/users_list.html'

    def get_context_data(self, **kwargs):
        context=super(UserList, self).get_context_data(**kwargs)
        datatable_headers=('username', 'full_name', 'email', 'role__role_name', 'user_group__name', 'manager_name',
                       'phone_number', 'last_login')
        context['datatable_headers'] = json.dumps([ dict(mData=key, sTitle = key.replace('_',' ').title()) for key in datatable_headers ])
        return context

class UserDetail(DetailView):
    model = UserProfile
    template_name = 'user_profile/user_detail.html'


class UserCreate(CreateView):
    template_name = 'user_profile/user_new.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        user_profile = UserProfile()
        user_profile.username = form.cleaned_data['username']
        user_profile.first_name = form.cleaned_data['first_name']
        user_profile.last_name = form.cleaned_data['last_name']
        user_profile.email = form.cleaned_data['email']
        user_profile.password = make_password(form.cleaned_data['password1'])
        user_profile.phone_number = form.cleaned_data['phone_number']
        user_profile.company = form.cleaned_data['company']
        user_profile.designation = form.cleaned_data['designation']
        user_profile.address = form.cleaned_data['address']
        user_profile.comment = form.cleaned_data['comment']
        user_profile.save()

        # saving parent --> FK Relation
        try:
            parent_user = UserProfile.objects.get(username=form.cleaned_data['parent'])
            user_profile.parent = parent_user
            user_profile.save()
        except:
            print "User has no parent."

        # creating roles  --> M2M Relation (Model: Roles)
        for role in form.cleaned_data['role']:
            user_role = Roles.objects.get(role_name=role)
            user_profile.role.add(user_role)
            user_profile.save()

        # saving user_group --> M2M Relation (Model: Department)
        for ug in form.cleaned_data['user_group']:
            department = Department()
            department.user_profile = user_profile
            department.user_group = ug
            department.save()
        return HttpResponseRedirect(UserCreate.success_url)


class UserUpdate(UpdateView):
    template_name = 'user_profile/user_update.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        self.object.username = form.cleaned_data['username']
        self.object.first_name = form.cleaned_data['first_name']
        self.object.last_name = form.cleaned_data['last_name']
        self.object.email = form.cleaned_data['email']
        self.object.password = make_password(form.cleaned_data['password1'])
        self.object.phone_number = form.cleaned_data['phone_number']
        self.object.company = form.cleaned_data['company']
        self.object.designation = form.cleaned_data['designation']
        self.object.address = form.cleaned_data['address']
        self.object.comment = form.cleaned_data['comment']
        self.object.save()

        # updating parent --> FK Relation
        try:
            parent_user = UserProfile.objects.get(username=form.cleaned_data['parent'])
            self.object.parent = parent_user
            self.object.save()
        except:
            print "User has no parent."

        # deleting old roles of user
        self.object.role.clear()

        # updating roles  --> M2M Relation (Model: Roles)
        for role in form.cleaned_data['role']:
            user_role = Roles.objects.get(role_name=role)
            self.object.role.add(user_role)
            self.object.save()

        # delete old relationship exist in department
        Department.objects.filter(user_profile=self.object).delete()

        # updating user_group --> M2M Relation (Model: Department)
        for ug in form.cleaned_data['user_group']:
            department = Department()
            department.user_profile = self.object
            department.user_group = ug
            department.save()
        return HttpResponseRedirect(UserCreate.success_url)


class UserDelete(DeleteView):
    model = UserProfile
    template_name = 'user_profile/user_delete.html'
    success_url = reverse_lazy('user_list')

class UserListingTable(BaseDatatableView):
    model = UserProfile
    columns = ['username', 'first_name', 'last_name', 'email', 'role__role_name', 'user_group__name', 'parent__first_name',
               'parent__last_name', 'phone_number', 'last_login']
    order_columns = ['username' , 'first_name', 'last_name', 'email', 'role__role_name', 'user_group__name', 'parent__first_name',
                     'parent__last_name', 'phone_number', 'last_login']

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
        return UserProfile.objects.values(*self.columns)

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
            sanity_dicts_list = [OrderedDict({'dict_final_key':'full_name','dict_key1':'first_name', 'dict_key2':'last_name' }),
            OrderedDict({'dict_final_key':'manager_name', 'dict_key1':'parent__first_name', 'dict_key2':'parent__last_name'})]
            qs, qs_headers = Datatable_Generation( qs, sanity_dicts_list ).main()

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
