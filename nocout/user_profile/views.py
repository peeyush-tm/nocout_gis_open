import json
import pickle

from django.contrib.auth.models import Group
from django.db.models.query import ValuesQuerySet
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin, BaseUpdateView
from django.core.urlresolvers import reverse_lazy
from mptt.forms import TreeNodeChoiceField
from nocout.utils.jquery_datatable_generation import Datatable_Generation
from user_profile.models import UserProfile, Roles
from organization.models import Organization
from forms import UserForm
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.auth.hashers import make_password
from collections import OrderedDict
from django_datatables_view.base_datatable_view import BaseDatatableView
from nocout.utils.util import DictDiffer, project_group_role_dict_mapper
from django.template.loader import render_to_string
from django.db.models import Q
from nocout.utils import logged_in_user_organizations
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.datatable import DatatableSearchMixin, DatatableOrganizationFilterMixin
from nocout.mixins.generics import FormRequestMixin


class UserList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to for User Listing.

    """
    model = UserProfile
    template_name = 'user_profile/users_list.html'
    required_permissions = ('user_profile.view_userprofile',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context=super(UserList, self).get_context_data(**kwargs)
        datatable_headers=[
            {'mData':'username',           'sTitle' : 'Username',     'sWidth':'auto',},
            {'mData':'full_name',          'sTitle' : 'Full Name',    'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'email',              'sTitle' : 'Email',        'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'organization__name', 'sTitle' : 'Organization', 'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'role__role_name',    'sTitle' : 'Role',         'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'manager_name',       'sTitle' : 'Manager',      'sWidth':'10%' ,'sClass':'hidden-xs'},
            {'mData':'phone_number',       'sTitle' : 'Phone Number', 'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'last_login',         'sTitle' : 'Last Login',   'sWidth':'auto','sClass':'hidden-xs'},]

        #if the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class UserListingTable(PermissionsRequiredMixin, DatatableOrganizationFilterMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class Based View for the User data table rendering.
    """
    model = UserProfile
    required_permissions = ('user_profile.view_userprofile',)
    columns = ['username', 'first_name', 'last_name', 'email', 'role__role_name', 'parent__first_name',
               'parent__last_name', 'organization__name','phone_number', 'last_login']
    order_columns = ['username' , 'first_name', 'email', 'organization__name', 'role__role_name', 'parent__first_name',
                     'phone_number', 'last_login']
    search_columns = ['username', 'first_name', 'last_name', 'email', 'role__role_name', 'parent__first_name',
               'parent__last_name', 'organization__name','phone_number']
    extra_qs_kwargs = {
        'is_deleted': 0
    }

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """

        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
            sanity_dicts_list = [OrderedDict({'dict_final_key':'full_name','dict_key1':'first_name', 'dict_key2':'last_name' }),
            OrderedDict({'dict_final_key':'manager_name', 'dict_key1':'parent__first_name', 'dict_key2':'parent__last_name'})]
            qs, qs_headers = Datatable_Generation( qs, sanity_dicts_list ).main()
        #if the user role is Admin then the action column_values will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers= self.request.GET.get('datatable_headers','').replace('false',"\"False\"")

            for dct in qs:
                if dct['id'] == self.request.user.id:
                    actions = '<a href="/user/myprofile/"><i class="fa fa-pencil text-dark"></i></a>'
                else:
                    actions = '''<a href="/user/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                            <a href="#UserListing" onclick='Dajaxice.user_profile.user_soft_delete_form( get_soft_delete_form,\
                            {{ \"value\": {0} , \"datatable_headers\": {1} }})'><i class="fa fa-trash-o text-danger">\
                            </i></a>'''.format(dct['id'], datatable_headers)
                dct.update( actions=actions,
                            last_login=dct['last_login'].strftime("%Y-%m-%d %H:%M:%S")
                          )
        return qs


class UserArchivedListingTable(DatatableSearchMixin, DatatableOrganizationFilterMixin, BaseDatatableView):
    """
    Class Based View for the Archived User data table rendering.
    """
    model = UserProfile
    columns = ['username', 'first_name', 'last_name', 'email', 'role__role_name', 'parent__first_name',
               'parent__last_name', 'organization__name','phone_number', 'last_login']
    order_columns = ['username' , 'first_name', 'last_name', 'email', 'role__role_name', 'parent__first_name',
                     'parent__last_name', 'organization__name','phone_number', 'last_login']
    search_columns = ['username' , 'first_name', 'last_name', 'email', 'role__role_name', 'parent__first_name',
                     'parent__last_name', 'organization__name','phone_number']
    extra_qs_kwargs = {
        'is_deleted':1
    }

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """

        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
            sanity_dicts_list = [OrderedDict({'dict_final_key':'full_name','dict_key1':'first_name', 'dict_key2':'last_name' }),
            OrderedDict({'dict_final_key':'manager_name', 'dict_key1':'parent__first_name', 'dict_key2':'parent__last_name'})]
            qs, qs_headers = Datatable_Generation( qs, sanity_dicts_list ).main()

        #if the user role is Admin then the action column_values will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            for dct in qs:

                dct.update( actions= '<a href="#UserArchivedListing" onclick= "add_confirmation(id={0})"<i class="fa fa-plus text-success"></i></a>'
                                     '<a href="#UserArchivedListing" onclick= "hard_delete_confirmation(id={0})"<i class="fa fa-trash-o text-danger"></i></a>'.format(dct['id'])
                )

        return qs


class UserDetail(PermissionsRequiredMixin, DetailView):
    """
    Class Based View to render User Detail.
    """
    model = UserProfile
    required_permissions = ('user_profile.view_userprofile',)
    template_name = 'user_profile/user_detail.html'

    def get_queryset(self):
        return UserProfile.objects.filter(organization__in=logged_in_user_organizations(self))


class UserCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Class Based View to Create a User.
    """
    template_name = 'user_profile/user_new.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')
    required_permissions = ('user_profile.add_userprofile',)

    def form_valid(self, form):
        """
        To Assigned User a group for the permissions as per the role the user is created with.

        """
        self.object= form.save(commit=False)
        self.object.set_password(form.cleaned_data["password2"])
        role= form.cleaned_data['role'][0]
        project_group_name= project_group_role_dict_mapper[role.role_name]
        project_group= Group.objects.get( name = project_group_name)
        self.object.save()
        form.save_m2m()
        self.object.groups.add(project_group)
        return super(ModelFormMixin, self).form_valid(form)

class UserUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
    """
    Class Based View to Update the user.
    """
    template_name = 'user_profile/user_update.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')

    required_permissions = ('user_profile.change_userprofile',)

    def get_queryset(self):
        queryset = super(UserUpdate, self).get_queryset()
        queryset = queryset.filter(organization__in=logged_in_user_organizations(self))
        queryset = queryset.exclude(id=self.request.user.id)
        return queryset

    def form_valid(self, form):
        """
        To update the form before submitting and log the user activity.
        """
        self.object = form.save(commit=False)
        if form.cleaned_data["password2"]:
            self.object.set_password(form.cleaned_data["password2"])

        role = form.cleaned_data['role'][0]
        project_group_name = project_group_role_dict_mapper[role.role_name]
        project_group = Group.objects.get(name=project_group_name)
        UserProfile.groups.through.objects.filter(user_id=self.object.id).delete()
        self.object.groups.add(project_group)

        self.object.save()
        form.save_m2m()

        return HttpResponseRedirect(UserCreate.success_url)


class UserDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class Based View to Delete the User.
    """
    model = UserProfile
    template_name = 'user_profile/user_delete.html'
    success_url = reverse_lazy('user_list')
    required_permissions = ('user_profile.delete_userprofile',)
    obj_alias = 'first_name'

    def get(self, *args, **kwargs):
        """
        To surpass the delete confirmation and delete the user directly.
        """
        return self.post(*args, **kwargs)

    def get_queryset(self):
        return UserProfile.objects.filter(organization__in=logged_in_user_organizations(self))


class CurrentUserProfileUpdate(FormRequestMixin, UpdateView):
    """
    Class Based view to update the current logged in user profile.
    """
    model = UserProfile
    template_name = 'user_profile/user_myprofile.html'
    form_class = UserForm
    success_url = reverse_lazy('current_user_profile_update')

    def get_object(self, queryset=None):
        """
        To fecth the current user object.
        """
        return self.model._default_manager.get(pk=self.request.user.id)

    def form_valid(self, form):
        """
        To log the user activity before submitting the form.
        """

        self.object = form.save(commit=False)
        kwargs=dict(first_name=self.object.first_name,
            last_name=self.object.last_name, email=self.object.email, phone_number=self.object.phone_number,
            company=self.object.company, designation=self.object.designation, address=self.object.address)

            #Adding the user log for the password change
        if  form.cleaned_data['password2']:
            kwargs.update({'password': make_password(form.cleaned_data['password2'])})

        UserProfile.objects.filter(id=self.object.id).update(**kwargs)
        return super(ModelFormMixin, self).form_valid(form)


def organisation_user_list(request):
    """
    To fetch the user based on the organisation for the user-profile form.
    """
    if request.is_ajax():
        parent_list = UserProfile.objects.filter(organization__id=request.GET['organisation_id'])
        user_tree_choice_field = TreeNodeChoiceField(queryset=parent_list)
        ctx_dict = {
                'user_choices': user_tree_choice_field.choices,
            }
        # get the user list in the html <option> format.
        parent_list_option = render_to_string('user_profile/parent_list_option.html', ctx_dict)
        parent_list_option.content_subtype = "html"
        return HttpResponse( parent_list_option )
    else:
        return HttpResponse("Invalid Url")

def organisation_user_select(request):
    """
    return the user if parent is selected
    while creation and updation of the user-profile.
    """
    parent_id = request.GET['parent_id']
    parent_select = UserProfile.objects.get(id=parent_id)
    html = "<option value=>Select</option>"
    html += "<option value={0}>{1}</option>".format(parent_select.id, parent_select.username)
    return HttpResponse( html )
