"""
===============================================================================
Module contains views and related functionality specific to 'user_profile' app.
===============================================================================

Location:
* /nocout_gis/nocout/user_profile/views.py

List of constructs:
=======
Classes
=======
* UserList
* UserListingTable
* UserArchivedListingTable
* UserDetail
* UserCreate
* UserUpdate
* UserDelete
* CurrentUserProfileUpdate

=======
Methods
=======
* organisation_user_list
* organisation_user_select
* change_password
"""

import json
from collections import OrderedDict
from django.utils import timezone
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from session_management.models import Visitor
from user_profile.models import UserProfile, UserPasswordRecord
from forms import UserForm, UserPasswordForm, GroupForm, PermissionForm
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse_lazy
from mptt.forms import TreeNodeChoiceField
from django.contrib import auth
from django.contrib.sessions.models import Session
from django.contrib.auth.hashers import make_password
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.template.loader import render_to_string
from nocout.utils.jquery_datatable_generation import Datatable_Generation
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.datatable import DatatableSearchMixin, DatatableOrganizationFilterMixin, AdvanceFilteringMixin, \
    ValuesQuerySetMixin
from nocout.mixins.generics import FormRequestMixin
from user_profile.utils.auth import in_group


class UserList(PermissionsRequiredMixin, ListView):
    """
    View to show headers of users datatable.
        URL - 'http://127.0.0.1:8000/user'
    """
    model = UserProfile
    template_name = 'user_profile/users_list.html'
    required_permissions = ('user_profile.view_userprofile',)

    def get_context_data(self, **kwargs):
        """
        Preparing the context data required in the template rendering.
        """
        context = super(UserList, self).get_context_data(**kwargs)

        datatable_headers = [
            {'mData': 'username', 'sTitle': 'Username', 'sWidth': 'auto', },
            {'mData': 'first_name', 'sTitle': 'Full Name', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'email', 'sTitle': 'Email', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'organization__name', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'groups__name', 'sTitle': 'Group', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'parent__first_name', 'sTitle': 'Manager', 'sWidth': '10%', 'sClass': 'hidden-xs'},
            {'mData': 'phone_number', 'sTitle': 'Phone Number', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'last_login', 'sTitle': 'Last Login', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'comment', 'sTitle': 'Comment', 'sWidth': 'auto', 'sClass': 'hidden-xs'}
        ]

        # If the user role is 'admin' then the action column will appear on the datatable.
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '7%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)

        return context


class UserListingTable(PermissionsRequiredMixin,
                       DatatableOrganizationFilterMixin,
                       DatatableSearchMixin,
                       BaseDatatableView,
                       AdvanceFilteringMixin):
    """
    View to show list of users in datatable.
        URL - 'http://127.0.0.1:8000/user/#UserListing'
    """
    model = UserProfile
    required_permissions = ('user_profile.view_userprofile',)

    # Columns that are going to be displayed.
    # columns = ['username', 'first_name', 'last_name', 'email', 'group', 'parent__first_name',
    #            'parent__last_name', 'organization__name', 'phone_number', 'last_login', 'comment']
    columns = ['username', 'first_name', 'last_name', 'email', 'groups__name', 'parent__first_name',
               'parent__last_name', 'organization__name', 'phone_number', 'last_login', 'comment']

    # Columns on which sorting/ordering is allowed.
    # order_columns = ['username', 'first_name', 'email', 'organization__name', 'group', 'parent__first_name',
    #                  'phone_number', 'last_login', 'comment']
    order_columns = ['username', 'first_name', 'email', 'organization__name', 'groups__name', 'parent__first_name',
                     'phone_number', 'last_login', 'comment']

    # Columns based on which searching is done.
    # search_columns = ['username', 'first_name', 'last_name', 'email', 'group', 'parent__first_name',
    #                   'parent__last_name', 'organization__name', 'phone_number', 'comment']
    search_columns = ['username', 'first_name', 'last_name', 'email', 'groups__name', 'parent__first_name',
                      'parent__last_name', 'organization__name', 'phone_number', 'comment']

    # Used in 'DatatableOrganizationFilterMixin' as extra parameters required to be passed during filtering queryset.
    extra_qs_kwargs = {
        'is_deleted': 0
    }

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the database to render on the datatable.
        """
        # Get 'json_data' from qs which is returned from 'get_initial_queryset'.
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        sanity_dicts_list = [
            OrderedDict({'dict_final_key': 'first_name', 'dict_key1': 'first_name', 'dict_key2': 'last_name'}),
            OrderedDict({'dict_final_key': 'parent__first_name', 'dict_key1': 'parent__first_name',
                         'dict_key2': 'parent__last_name'})]

        if json_data:
            json_data, qs_headers = Datatable_Generation(json_data, sanity_dicts_list).main()
            # Show 'actions' column only if user role is 'admin'.
            if in_group(self.request.user, 'admin'):
                datatable_headers = self.request.GET.get('datatable_headers', '').replace('false', "\"False\"")
                # Create instance of 'NocoutUtilsGateway' class
                nocout_utils = NocoutUtilsGateway()
                for dct in json_data:
                    # Last login field timezone conversion from 'utc' to 'local'.
                    try:
                        dct['last_login'] = nocout_utils.convert_utc_to_local_timezone(dct['last_login'])
                    except Exception as e:
                        pass
                    if dct['id'] == self.request.user.id:
                        actions = '<a href="/user/{0}/"><i class="fa fa-list-alt text-info" title="Detail"></i></a>\
                                   <a href="/user/myprofile/"><i class="fa fa-pencil text-dark"></i></a>'.format(
                            dct['id'])
                    else:
                        actions = '<a href="/user/{0}/"><i class="fa fa-list-alt text-info" title="Detail"></i></a>\
                                   <a href="/user/{0}/edit/"><i class="fa fa-pencil text-dark" title="Edit"></i></a>\
                                   <a href="javascript:;" class="user_soft_delete_btn" pk="{0}"><i class="fa fa-trash-o\
                                    text-danger" title="Archive user."></i></a> \
                                  <a href="javascript:;" class="reset_perm_btn" pk="{0}"><i class="fa fa-level-down \
                                  text-danger" title="Reset permissions to default."></i></a>'.format(
                            dct['id'], datatable_headers
                        )
                    dct.update(actions=actions)

        return json_data


class UserArchivedListingTable(DatatableSearchMixin, DatatableOrganizationFilterMixin, BaseDatatableView, AdvanceFilteringMixin):
    """
    View to show list of deleted users in datatable.
        URL - 'http://127.0.0.1:8000/user/#UserArchivedListing'
    """

    model = UserProfile

    # Columns that are going to be displayed.
    columns = ['username', 'first_name', 'last_name', 'email', 'groups__name', 'parent__first_name',
               'parent__last_name', 'organization__name', 'phone_number', 'last_login', 'comment']

    # Columns on which sorting/ordering is allowed.
    order_columns = ['username', 'first_name', 'last_name', 'email', 'groups__name', 'parent__first_name',
                     'parent__last_name', 'organization__name', 'phone_number', 'last_login', 'comment']

    # Columns based on which searching is done.
    search_columns = ['username', 'first_name', 'last_name', 'email', 'groups__name', 'parent__first_name',
                      'parent__last_name', 'organization__name', 'phone_number', 'comment']

    # Used in 'DatatableOrganizationFilterMixin' as extra parameters required to be passed during filtering queryset.
    extra_qs_kwargs = {
        'is_deleted': 1
    }

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        sanity_dicts_list = [
            OrderedDict({'dict_final_key': 'first_name', 'dict_key1': 'first_name', 'dict_key2': 'last_name'}),
            OrderedDict({'dict_final_key': 'parent__first_name', 'dict_key1': 'parent__first_name',
                         'dict_key2': 'parent__last_name'})]

        if json_data:
            json_data, qs_headers = Datatable_Generation(json_data, sanity_dicts_list).main()

            # Show 'actions' column only if user role is 'admin'.
            if in_group(self.request.user, 'admin'):
                # Create instance of 'NocoutUtilsGateway' class
                nocout_utils = NocoutUtilsGateway()
                for dct in json_data:
                    # Last login field timezone conversion from 'utc' to 'local'.
                    try:
                        dct['last_login'] = nocout_utils.convert_utc_to_local_timezone(dct['last_login'])
                    except Exception as e:
                        pass

                    dct.update(
                        actions='<a href="/user/{0}/"><i class="fa fa-list-alt text-info" title="Detail"></i></a>\
                                 <a href="#UserArchivedListing" onclick= "add_confirmation(id={0})"><i class="fa fa-plus text-success"></i></a> \
                                 <a href="#UserArchivedListing" onclick= "hard_delete_confirmation(id={0})"<i class="fa fa-trash-o text-danger"></i></a>'.format(dct['id'])
                    )

        return json_data


class UserDetail(PermissionsRequiredMixin, DetailView):
    """
    Show details of the single user instance.
    """
    model = UserProfile
    required_permissions = ('user_profile.view_userprofile',)
    template_name = 'user_profile/user_detail.html'

    def get_queryset(self):
        """
        Get the queryset to look an object up against.
        Only objects which belongs to organization's accessible to the user were returned.
        """
        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()
        return UserProfile.objects.filter(organization__in=nocout_utils.logged_in_user_organizations(self))


class UserCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Create a new user instance, with a response rendered by template.
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
        # Creating but not saving the new user instance.
        self.object = form.save(commit=False)

        # Set password for new user instance.
        self.object.set_password(form.cleaned_data["password2"])

        # Saving instance and it's m2m relationship.
        self.object.save()
        form.save_m2m()

        return super(ModelFormMixin, self).form_valid(form)

    def form_invalid(self, form):
        return super(ModelFormMixin, self).form_invalid(form)


class UserUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
    """
    Update a new user instance, with a response rendered by template.
    """
    template_name = 'user_profile/user_update.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')

    required_permissions = ('user_profile.change_userprofile',)

    def get_queryset(self):
        """
        Get the queryset to look an object up against.
        Only objects which belongs to organization's accessible to the user were returned.
        """
        queryset = super(UserUpdate, self).get_queryset()
        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()
        queryset = queryset.filter(organization__in=nocout_utils.logged_in_user_organizations(self))
        queryset = queryset.exclude(id=self.request.user.id)

        return queryset

    def form_valid(self, form):
        """
        To update the form before submitting and log the user activity.
        To update the record of the password used by user.
        """
        self.object = form.save(commit=False)

        if form.cleaned_data["password2"]:
            self.object.set_password(form.cleaned_data["password2"])
            # Adding the user log for the password change.
            UserPasswordRecord.objects.create(user_id=self.object.id, password_used=self.object.password)

        # Any user can have only one group, so first we need to remove user's previous group
        # before assigning new group.
        UserProfile.groups.through.objects.filter(user_id=self.object.id).delete()

        # # Assign new group to user.
        # self.object.groups.add(project_group)

        # Saving instance and it's m2m relationship.
        self.object.save()
        form.save_m2m()

        return HttpResponseRedirect(UserCreate.success_url)

    def form_invalid(self, form):
        return super(UserUpdate, self).form_invalid(form)


class UserDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Delete a single user instance.
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
        """
        User can delete the user of self organization or descendant organization.
        User can't delete self.
        """
        queryset = super(UserDelete, self).get_queryset()
        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()
        queryset = queryset.filter(organization__in=nocout_utils.logged_in_user_organizations(self))
        queryset = queryset.exclude(id=self.request.user.id)

        return queryset


class CurrentUserProfileUpdate(FormRequestMixin, UpdateView):
    """
    Update the current logged in user profile.
    """
    model = UserProfile
    template_name = 'user_profile/user_myprofile.html'
    form_class = UserForm
    success_url = reverse_lazy('current_user_profile_update')

    def get_object(self, queryset=None):
        """
        Get current user object.
        """
        return self.model._default_manager.get(pk=self.request.user.id)

    def form_valid(self, form):
        """
        To log the user activity before submitting the form.
        To update the record of the password used by user
        And delete old password other than five previously used.
        """
        self.object = form.save(commit=False)

        kwargs = dict(first_name=self.object.first_name, last_name=self.object.last_name, email=self.object.email,
                      phone_number=self.object.phone_number, company=self.object.company,
                      designation=self.object.designation, address=self.object.address)

        if form.cleaned_data['password2']:
            password = make_password(form.cleaned_data['password2'])
            kwargs.update({'password': password, 'password_changed_at': timezone.now()})
            # Adding the user log for the password change.
            UserPasswordRecord.objects.create(user_id=self.object.id, password_used=password)

        UserProfile.objects.filter(id=self.object.id).update(**kwargs)

        return super(ModelFormMixin, self).form_valid(form)


def organisation_user_list(request):
    """
    Get the user based on the organisation for the user-profile form.
    """
    if request.is_ajax():
        parent_list = UserProfile.objects.filter(organization__id=request.GET['organisation_id'])
        user_tree_choice_field = TreeNodeChoiceField(queryset=parent_list)
        ctx_dict = {
            'user_choices': user_tree_choice_field.choices,
        }
        # Get the user list in the html <option> format.
        parent_list_option = render_to_string('user_profile/parent_list_option.html', ctx_dict)
        parent_list_option.content_subtype = "html"
        return HttpResponse(parent_list_option)
    else:
        return HttpResponse("Invalid Url")


def organisation_user_select(request):
    """
    Return the user if parent is selected while creation and updation of the user profile.
    """
    parent_id = request.GET['parent_id']
    parent_select = UserProfile.objects.get(id=parent_id)
    html = "<option value=>Select</option>"
    html += "<option value={0}>{1}</option>".format(parent_select.id, parent_select.username)

    return HttpResponse(html)


@csrf_exempt
def change_password(request):
    """
    The Action of the Dialog box appears on the screen.
    If the action is continue then the user get prompt to set new password.
    """
    # Get the url from request.POST
    url = request.POST.get('url', '/home/')

    # Authenticate the user using auth_token present in request.POST.
    user = auth.authenticate(token=request.POST.get('auth_token', None))

    # If user clicks on continue button of password change form and the form is valid, then login the user.
    if request.POST.get('action') == 'continue' and user:
        form = UserPasswordForm(request.POST)
        if form.is_valid():
            # If user is visitor. Delete the session of user and removes the user from visitor.
            if hasattr(user, 'visitor'):
                Session.objects.filter(session_key=user.visitor.session_key).delete()
                # If Session object is modified as session key is changed.
                # Above doesn't remove existing Visitor object. So removing it below.
                Visitor.objects.filter(user=user).delete()

            # Login the request user.
            auth.login(request, user)

            # Create new visitor with new session_key for the user.
            Visitor.objects.create(session_key=request.session.session_key, user=request.user)

            # Update the field password_changed_at.
            user.userprofile.password_changed_at = timezone.now()
            # Update the user_invalid_attempt to zero.
            user.userprofile.user_invalid_attempt = 0
            # Save the user profile of user.
            user.userprofile.save()
            # Update the password of user.
            user.set_password(form.data['confirm_pwd'])

            # Save the user.
            user.save()

            # Adding the user log for the password change.
            UserPasswordRecord.objects.create(user_id=user.id, password_used=user.password)

            success = 1                     # 0 - fail, 1 - success, 2 - exception
            message = "Success/Fail message.",
            object_values = dict(url=url)

        else:
            success = 0                     # 0 - fail, 1 - success, 2 - exception
            message = "Invalid Password."
            object_values = dict(url='/login/', reason="Ignore dictionary common words and previously used password.")
    else:
        success = 1                         # 0 - fail, 1 - success, 2 - exception
        message = "Success/Fail message."
        object_values = dict(url='/login/')

    result = {
        "success": success,                 # 0 - fail, 1 - success, 2 - exception
        "message": message,
        "data": {
            "meta": {},
            "objects": object_values
        }
    }

    return HttpResponse(json.dumps(result), content_type='application/json')


class GroupList(PermissionsRequiredMixin, ListView):
    """
    View to show headers of groups datatable.
        URL - 'http://127.0.0.1:8000/group'
    """
    model = Group
    template_name = 'group/groups_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(GroupList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class GroupListingTable(ValuesQuerySetMixin,
                        DatatableSearchMixin,
                        BaseDatatableView,
                        AdvanceFilteringMixin):
    """
    View to show list of groups in datatable.
        URL - 'http://127.0.0.1:8000/group'
    """
    model = Group
    columns = ['name']
    order_columns = ['name']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            dct.update(actions='<a href="/group/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/group/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


class GroupDetail(PermissionsRequiredMixin, DetailView):
    """
    Show details of the single group instance.
    """
    model = Group
    template_name = 'group/group_detail.html'


class GroupCreate(PermissionsRequiredMixin, CreateView):
    """
    Create a new group, with a response rendered by template.
    """
    template_name = 'group/group_new.html'
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy('groups_list')


class GroupUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Update a new group instance, with a response rendered by template.
    """
    template_name = 'group/group_update.html'
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy('groups_list')


class GroupDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Delete a single instance from database.
    """
    model = Group
    obj_alias = 'name'
    template_name = 'group/group_delete.html'
    success_url = reverse_lazy('groups_list')


class PermissionList(PermissionsRequiredMixin, ListView):
    """
    View to show headers of permissions datatable.
        URL - 'http://127.0.0.1:8000/permission'
    """
    model = Permission
    template_name = 'permission/permissions_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(PermissionList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'content_type', 'sTitle': 'Content Type', 'sWidth': 'auto', },
            {'mData': 'codename', 'sTitle': 'Codename', 'sWidth': 'auto', },
        ]
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class PermissionListingTable(ValuesQuerySetMixin,
                             DatatableSearchMixin,
                             BaseDatatableView,
                             AdvanceFilteringMixin):
    """
    View to show list of permissions in datatable.
        URL - 'http://127.0.0.1:8000/permission'
    """
    model = Permission
    columns = ['name', 'content_type', 'codename']
    order_columns = ['name', 'content_type', 'codename']
    search_columns = ['name', 'codename']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            try:
                content_type = ContentType.objects.get(id=dct['content_type'])
                dct['content_type'] = content_type.app_label + " | " + content_type.model
            except Exception as e:
                pass
            dct.update(actions='<a href="/permission/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/permission/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


class PermissionDetail(PermissionsRequiredMixin, DetailView):
    """
    Show details of the single permission instance.
    """
    model = Permission
    template_name = 'permission/permission_detail.html'


class PermissionCreate(PermissionsRequiredMixin, CreateView):
    """
    Create a new permission, with a response rendered by template.
    """
    template_name = 'permission/permission_new.html'
    model = Permission
    form_class = PermissionForm
    success_url = reverse_lazy('permissions_list')


class PermissionUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Update a new permission instance, with a response rendered by template.
    """
    template_name = 'permission/permission_update.html'
    model = Permission
    form_class = PermissionForm
    success_url = reverse_lazy('permissions_list')


class PermissionDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Delete a single instance from database.
    """
    model = Permission
    obj_alias = 'name'
    template_name = 'permission/permission_delete.html'
    success_url = reverse_lazy('permissions_list')
