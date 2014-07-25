import json
import pickle
from django.contrib.auth.models import Group
from django.db.models.query import ValuesQuerySet
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin, BaseUpdateView
from django.core.urlresolvers import reverse_lazy
from nocout.utils.jquery_datatable_generation import Datatable_Generation
from user_profile.models import UserProfile, Roles
from organization.models import Organization
from forms import UserForm
from django.http.response import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from collections import OrderedDict
from django_datatables_view.base_datatable_view import BaseDatatableView
from actstream import action
from nocout.utils.util import DictDiffer, project_group_role_dict_mapper
from django.contrib.auth.decorators import permission_required
from django.db.models import Q


class UserList(ListView):
    model = UserProfile
    template_name = 'user_profile/users_list.html'

    def get_context_data(self, **kwargs):
        context=super(UserList, self).get_context_data(**kwargs)
        datatable_headers=[
            {'mData':'username',           'sTitle' : 'Username',     'sWidth':'null',},
            {'mData':'full_name',          'sTitle' : 'Full Name',    'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'email',              'sTitle' : 'Email',        'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'organization__name', 'sTitle' : 'Organization', 'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'role__role_name',    'sTitle' : 'Role',         'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'manager_name',       'sTitle' : 'Manager',      'sWidth':'10%' ,'sClass':'hidden-xs'},
            {'mData':'phone_number',       'sTitle' : 'Phone Number', 'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'last_login',         'sTitle' : 'Last Login',   'sWidth':'null','sClass':'hidden-xs'},]

        #if the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class UserListingTable(BaseDatatableView):
    model = UserProfile
    columns = ['username', 'first_name', 'last_name', 'email', 'role__role_name', 'parent__first_name',
               'parent__last_name', 'organization__name','phone_number', 'last_login']
    order_columns = ['username' , 'first_name', 'email', 'organization__name', 'role__role_name', 'parent__first_name',
                     'phone_number', 'last_login']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__icontains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        organization_descendants_ids= list(self.request.user.userprofile.organization.get_children()\
                                           .values_list('id', flat=True)) + [ self.request.user.userprofile.organization.id ]

        return UserProfile.objects.filter(organization__in = organization_descendants_ids, is_deleted=0).values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
            sanity_dicts_list = [OrderedDict({'dict_final_key':'full_name','dict_key1':'first_name', 'dict_key2':'last_name' }),
            OrderedDict({'dict_final_key':'manager_name', 'dict_key1':'parent__first_name', 'dict_key2':'parent__last_name'})]
            qs, qs_headers = Datatable_Generation( qs, sanity_dicts_list ).main()
        #if the user role is Admin then the action column_values will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers= self.request.GET.get('datatable_headers','').replace('false',"\"False\"")

            for dct in qs:
                dct.update( actions='''<a href="/user/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                            <a href="#" onclick='Dajaxice.user_profile.user_soft_delete_form( get_soft_delete_form,\
                            {{ \"value\": {0} , \"datatable_headers\": {1} }})'><i class="fa fa-trash-o text-danger">\
                            </i></a>'''.format(dct['id'], datatable_headers),
                            last_login=dct['last_login'].strftime("%Y-%m-%d %H:%M:%S")
                           )
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

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

class UserArchivedListingTable(BaseDatatableView):
    model = UserProfile
    columns = ['username', 'first_name', 'last_name', 'email', 'role__role_name', 'parent__first_name',
               'parent__last_name', 'organization__name','phone_number', 'last_login']
    order_columns = ['username' , 'first_name', 'last_name', 'email', 'role__role_name', 'parent__first_name',
                     'parent__last_name', 'organization__name','phone_number', 'last_login']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__icontains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        organization_descendants_ids= list(self.request.user.userprofile.organization.get_children()\
                                           .values_list('id', flat=True)) + [ self.request.user.userprofile.organization.id ]
        return UserProfile.objects.filter(organization__in = organization_descendants_ids, is_deleted=1).values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
            sanity_dicts_list = [OrderedDict({'dict_final_key':'full_name','dict_key1':'first_name', 'dict_key2':'last_name' }),
            OrderedDict({'dict_final_key':'manager_name', 'dict_key1':'parent__first_name', 'dict_key2':'parent__last_name'})]
            qs, qs_headers = Datatable_Generation( qs, sanity_dicts_list ).main()

        #if the user role is Admin then the action column_values will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            for dct in qs:
                dct.update(actions='<a href="/user/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>')

        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

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

class UserDetail(DetailView):
    model = UserProfile
    template_name = 'user_profile/user_detail.html'


class UserCreate(CreateView):
    template_name = 'user_profile/user_new.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')

    @method_decorator(permission_required('user_profile.add_userprofile', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(UserCreate, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UserCreate, self).get_form_kwargs()
        kwargs.update({'request':self.request.user })
        return kwargs

    def form_valid(self, form):
        self.object= form.save(commit=False)
        self.object.set_password(form.cleaned_data["password2"])
        role= form.cleaned_data['role'][0]
        project_group_name= project_group_role_dict_mapper[role.role_name]
        project_group= Group.objects.get( name = project_group_name)
        self.object.save()
        form.save_m2m()
        self.object.groups.add(project_group)
        return super(ModelFormMixin, self).form_valid(form)

class UserUpdate(UpdateView):
    template_name = 'user_profile/user_update.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')


    @method_decorator(permission_required('user_profile.change_userprofile', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(UserUpdate, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        kwargs = super(UserUpdate, self).get_form_kwargs()
        kwargs.update({'request':self.request.user })
        return kwargs

    def form_valid(self, form):
        self.object= form.save(commit=False)
        self.object.set_password(form.cleaned_data["password2"])
        role= form.cleaned_data['role'][0]
        project_group_name= project_group_role_dict_mapper[role.role_name]
        project_group= Group.objects.get( name = project_group_name)
        UserProfile.groups.through.objects.filter(user_id=self.object.id).delete()
        self.object.groups.add(project_group)
        self.object.save()
        form.save_m2m()

        #User Activity Logs

        initial_field_dict={}
        for field in form.initial.keys():
            if field in ('organization','parent'):
                initial_field_dict[field]= form.initial[field].id
            else:
                initial_field_dict[field]= form.initial[field]

        cleaned_data_field_dict={}
        for field in form.cleaned_data.keys():
            if field =='role':
                cleaned_data_field_dict[field]= form.cleaned_data[field][0].id
            elif field in ('organization','parent'):
                cleaned_data_field_dict[field]= form.cleaned_data[field].id
            else:
                cleaned_data_field_dict[field]=form.cleaned_data[field]

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()

        if cleaned_data_field_dict['password2']:
            action.send(self.request.user, verb='Password changed for the user: %s !'%(self.object.username))

        if changed_fields_dict:

            initial_field_dict['role']= Roles.objects.get(id= initial_field_dict['role']).role_name
            initial_field_dict['parent']= UserProfile.objects.get(id= initial_field_dict['parent']).username
            initial_field_dict['organization'] = Organization.objects.get(id= initial_field_dict['organization']).name

            cleaned_data_field_dict['role'] = Roles.objects.get(id= cleaned_data_field_dict['role']).role_name
            cleaned_data_field_dict['parent'] = UserProfile.objects.get(id= cleaned_data_field_dict['parent']).username
            cleaned_data_field_dict['organization'] = Organization.objects.get(id= cleaned_data_field_dict['organization']).name


            verb_string = 'Changed values of user %s from initial values '%(self.object.username) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                           for k in changed_fields_dict])+\
                           ' to '+\
                           ', '.join(['%s: %s' % (k,cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(UserCreate.success_url)


class UserDelete(DeleteView):
    model = UserProfile
    template_name = 'user_profile/user_delete.html'
    success_url = reverse_lazy('user_list')

    @method_decorator(permission_required('user_profile.delete_userprofile', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(UserDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting user: %s'%(self.get_object().username))
        return super(UserDelete, self).delete(request, *args, **kwargs)

class CurrentUserProfileUpdate(UpdateView):
    model = UserProfile
    template_name = 'user_profile/user_myprofile.html'
    form_class = UserForm
    success_url = reverse_lazy('current_user_profile_update')

    def get_form_kwargs(self):
        kwargs = super(CurrentUserProfileUpdate, self).get_form_kwargs()
        kwargs.update({'request':self.request.user })
        return kwargs

    def get_object(self, queryset=None):
        return self.model._default_manager.get(pk=self.request.user.id)

    def form_valid(self, form):

        self.object = form.save(commit=False)
        kwargs=dict(first_name=self.object.first_name,
            last_name=self.object.last_name, email=self.object.email, phone_number=self.object.phone_number,
            company=self.object.company, designation=self.object.designation, address=self.object.address)

            #Adding the user log for the password change
        if  form.cleaned_data['password2']:
            kwargs.update({'password': make_password(form.cleaned_data['password2'])})
            action.send(self.request.user, verb='Changed Password !')

        changed_fields=DictDiffer(form.cleaned_data, form.initial).changed() - set(['role','username','user_group','organization'])
        if changed_fields:

            initial_field_dict = { field : form.initial[field] for field in changed_fields }
            changed_field_dict = { field : form.cleaned_data[field] for field in changed_fields }

            verb_string = 'Changed values from initial values ' + ', '.join(['%s: %s' %(k,v) for k,v in initial_field_dict.iteritems()])+\
                          ' to '+', '.join(['%s: %s' %(k,v) for k,v in changed_field_dict.iteritems()])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'
            #Adding the user log for the number of fileds and with the values changed.
            action.send(self.request.user, verb=verb_string)

        UserProfile.objects.filter(id=self.object.id).update(**kwargs)
        return super(ModelFormMixin, self).form_valid(form)

