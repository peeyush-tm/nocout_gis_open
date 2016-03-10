"""
==================================================================
Module contains forms functionlity specific to 'user_profile' app.
==================================================================

Location:
* /nocout_gis/nocout/user_profile/forms.py

List of constructs:
=======
Classes
=======
* UserForm
* UserPasswordForm
"""

from django import forms
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Permission, Group
from nocout.widgets import MultipleToSingleSelectionWidget
from organization.models import Organization
from user_profile.models import UserProfile, UserPasswordRecord
from fields import PasswordField
from user_profile.utils.auth import can_edit_permissions, get_user_organizations
import logging
from nocout.settings import PERMISSIONS_MODULE_ENABLED
import re
logger = logging.getLogger(__name__)


class UserForm(forms.ModelForm):
    """
    Form required to create, update and update my profile of the user.
    """
    first_name = forms.CharField(required=True)
    email = forms.CharField(label='Email', required=True)

    password1 = PasswordField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        initial = kwargs.setdefault('initial', {})

        # Removing help text for username 'select' field
        self.base_fields['username'].help_text = ''

        # Removing help text for role 'select' field
        self.base_fields['groups'].help_text = ''
        # Update the label text of groups dropdown field
        self.base_fields['groups'].label = 'Role'
        self.base_fields['user_permissions'].help_text = ''
        # self.base_fields['organization'].queryset = get_user_organizations(self.request.user)

        # If request is for updating user then initialize role, parent, organization.
        if kwargs['instance']:
            try:
                initial['groups'] = kwargs['instance'].groups.all()[0].pk
            except Exception as e:
                pass
            initial['parent'] = kwargs['instance'].parent
            initial['organization'] = kwargs['instance'].organization

        super(UserForm, self).__init__(*args, **kwargs)

        self.fields['parent'].empty_label = 'Select'
        self.fields['organization'].empty_label = 'Select'
        logged_in_user_organization_list = get_user_organizations(self.request.user)
        self.fields['organization'].queryset = logged_in_user_organization_list

        # If permission module is disabled then remove user_permissions field
        if not PERMISSIONS_MODULE_ENABLED:
            del self.fields['user_permissions']

        # If request is for updating user then make password non mandatory fields.
        if self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            # Show permission field to only those who are allowed to edit permissions.
            if not can_edit_permissions(self.request.user, kwargs['instance']):
                try:
                    del self.fields['user_permissions']
                except Exception, e:
                    pass
            # If user is modifying his own profile then don't allow user to modify
            # his username, parent/manager, role, organization.
            if self.instance.pk == self.request.user.pk:
                self.fields['username'].widget.attrs['readonly'] = True
                self.fields['parent'].widget.attrs['disabled'] = 'disabled'
                self.fields['groups'].widget.attrs['disabled'] = 'disabled'
                self.fields['organization'].widget.attrs['readonly'] = True
                # self.fields['parent'].label = 'Manager'
                # Don't show comment field.
                self.fields.pop('comment')

        for name, field in self.fields.items():
            select2class = ' select2select'
            if name == 'user_permissions':
                select2class = ''
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += select2class
                else:
                    field.widget.attrs['class'] += ' form-control'
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 %s' % select2class})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        """
        Meta Information required to generate model form, and to mention the fields, widgets and fieldsets
        information required to render for the form.
        """
        model = UserProfile
        fields = (
            'username', 'first_name', 'last_name', 'email', 'organization', 'parent', 'groups', 'user_permissions',
            'designation', 'company', 'address', 'phone_number', 'comment'
        )
        widgets = {
            'groups': MultipleToSingleSelectionWidget
        }
        fieldsets = (
            ('Personal', {
                'fields': ('first_name', 'last_name')
            }),
        )

    def clean_password2(self):
        """
        Check that the two password entries match else generate validation error.
        """
        password2 = self.cleaned_data.get("password2")
        password1 = self.cleaned_data.get("password1")

        if (password1 or password2) and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return password2

    def clean_parent(self):
        """
        Validating parent/manager during assignment to the user.
        Rules for validation are as following:
        1. If no parent selected:
            1. If user is 'gisadmin'(system user) then do not assign any parent.
            2. If user is other than 'gisadmin' then assign 'gisadmin' as it's default parent.
        2. User cannot be parent of itself.
        3. User's child cannot be a parent of user.
        """
        if 'username' in [key for key, values in self.cleaned_data.items()]:
            parent = self.cleaned_data['parent']
            username = self.cleaned_data['username']

            # Parent of current user's parent
            parent_parent = None
            try:
                parent_parent = parent.parent.username
            except Exception as e:
                pass

            # If no parent selected:
            # 1. If user is 'gisadmin'(system user) then do not assign any parent.
            # 2. If user is other than 'gisadmin' then assign 'gisadmin' as it's default parent.
            if parent is None:
                if username == 'gisadmin':
                    return parent
                gisadmin = UserProfile.objects.get(username='gisadmin')
                parent = gisadmin
                return parent
            else:
                # User cannot be parent of itself.
                if parent.username == username:
                    raise forms.ValidationError("User cannot be parent of itself.")
                # User's child cannot be a parent of user.
                elif parent_parent == username:
                    raise forms.ValidationError("User's child cannot be a parent of user.")
                return parent

    def clean_groups(self):
        """
        Restrict the user other than super user to create the admin.
        """
        groups = self.cleaned_data['groups']

        if not self.request.user.is_superuser and len(groups) == 1:
            if groups[0].name.lower() == 'admin':
                raise forms.ValidationError("Not permitted to create admin.")
            else:
                return groups
        else:
            return groups

    def clean_first_name(self):
        """
        Restrict the user other than super user to create the admin.
        """
        first_name = self.cleaned_data['first_name']

        if first_name:
            if not re.match(r'^[A-Za-z\s]+$', first_name):
                raise forms.ValidationError("Firstname must contains only alphabets.")
            else:
                return first_name
        else:
            return first_name

    def clean_last_name(self):
        """
        Restrict the user other than super user to create the admin.
        """
        last_name = self.cleaned_data['last_name']

        if last_name:
            if not re.match(r'^[A-Za-z\s]+$', last_name):
                raise forms.ValidationError("Lastname must contains only alphabets.")
            else:
                return last_name
        else:
            return last_name

    def clean_password1(self):
        """
        Validate password based on following rules:
        1. Username and password must not be identical.
        2. If it's a password update request then neglect password if
           it's already from last five passwords used by the user.
        """
        if 'username' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            username = self.cleaned_data['username']

            # Username and password must not be identical.
            if password1 == username:
                raise forms.ValidationError("Username and password should not be identical.")

            if password1:
                # Last five password match validator.
                user = UserProfile.objects.filter(username=username)
                if user.exists():
                    # Neglect password if it's already from last five passwords used by the user.
                    user_password_used = UserPasswordRecord.objects.filter(user_id=user[0].id).order_by(
                        '-password_used_on').values_list('password_used', flat=True)[:5]
                    for pwd in user_password_used:
                        if check_password(password1, pwd):
                            raise forms.ValidationError("This password is recently used.")

            return password1


class UserPasswordForm(forms.Form):
    """
    Form for modifying user password.
    """
    new_pwd = forms.CharField(max_length=128, required=True)
    confirm_pwd = forms.CharField(max_length=128, required=True)
    user_id = forms.CharField(max_length=128, required=False)

    def clean(self):
        """
        Validate password based on following rules:
        1. If it's a password update request then neglect password if
           it's already from last five passwords used by the user.
        """
        confirm_pwd = self.cleaned_data.get("confirm_pwd")

        if confirm_pwd:
            user_id = self.cleaned_data.get("user_id")
            if user_id:
                # Neglect password if it's already from last five passwords used by the user.
                user_password_used = UserPasswordRecord.objects.filter(user_id=int(user_id)).order_by(
                    '-password_used_on').values_list('password_used', flat=True)[:5]
                for pwd in user_password_used:
                    if check_password(confirm_pwd, pwd):
                        raise forms.ValidationError("This password is recently used.")


class PermissionForm(forms.ModelForm):
    """
    Form required to create and update permission.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize function to change attributes before rending the model form.
        """
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(PermissionForm, self).__init__(*args, **kwargs)

        self.fields['content_type'].empty_label = 'Select'

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                else:
                    field.widget.attrs['class'] += ' form-control'
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Permission
        fields = "__all__"


class GroupForm(forms.ModelForm):
    """
    Form required to create and update group.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize function to change attributes before rending the model form.
        """
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(GroupForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                else:
                    field.widget.attrs['class'] += ' form-control'
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Group
        fields = "__all__"