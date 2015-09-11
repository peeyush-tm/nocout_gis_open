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
import string

from django import forms
from django.contrib.auth.hashers import check_password
from nocout.widgets import MultipleToSingleSelectionWidget
from organization.models import Organization
from user_profile.models import UserProfile, UserPasswordRecord
from fields import PasswordField


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
        self.base_fields['role'].help_text = ''

        # If request is for updating user then initialize role, parent, organization.
        if kwargs['instance']:
            initial['role'] = kwargs['instance'].role.values_list('pk', flat=True)[0]
            initial['parent'] = kwargs['instance'].parent
            initial['organization'] = kwargs['instance'].organization

        super(UserForm, self).__init__(*args, **kwargs)

        self.fields['parent'].empty_label = 'Select'
        self.fields['organization'].empty_label = 'Select'

        if not self.request.user.is_superuser:
            logged_in_user_organization_list = self.request.user.userprofile.organization.get_descendants(
                include_self=True)
            self.fields['organization'].queryset = logged_in_user_organization_list
        else:
            self.fields['organization'].queryset = Organization.objects.all()

        # If request is for updating user then make password non mandatory fields.
        if self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            # If user is modifying his own profile then don't allow user to modify
            # his username, parent/manager, role, organization.
            if self.instance.pk == self.request.user.pk:
                self.fields['username'].widget.attrs['readonly'] = True
                self.fields['parent'].widget.attrs['disabled'] = 'disabled'
                self.fields['role'].widget.attrs['disabled'] = 'disabled'
                self.fields['role'].widget.is_required = False
                self.fields['role'].required = False
                self.fields['organization'].widget.attrs['readonly'] = True
                self.fields['parent'].label = 'Manager'
                # Don't show comment field.
                self.fields.pop('comment')

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
        """
        Meta Information required to generate model form, and to mention the fields, widgets and fieldsets
        information required to render for the form.
        """
        model = UserProfile
        fields = (
            'username', 'first_name', 'last_name', 'email', 'role', 'organization', 'parent', 'designation', 'company',
            'address', 'phone_number', 'comment',
        )
        widgets = {
            'role': MultipleToSingleSelectionWidget,
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

        print "********************* password1 - ", password1
        print "********************* password2 - ", password2

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

    def clean_role(self):
        """
        Restrict the user other than super user to create the admin.
        """
        role = self.cleaned_data['role']

        if not self.request.user.is_superuser and len(role) == 1:
            if role[0].role_name == 'admin':
                raise forms.ValidationError("Not permitted to create admin.")
            else:
                return role
        else:
            return role

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
                # # Special character validator.
                # if not set(password1).intersection(set(string.punctuation)):
                #     raise forms.ValidationError("Password must contain atleast one special character.")
                #
                # # Uppercase character validator.
                # if not set(password1).intersection(set(string.uppercase)):
                #     raise forms.ValidationError("Password must contain atleast one uppercase letter.")
                #
                # # Digit/number validator.
                # if not set(password1).intersection(set(string.digits)):
                #     raise forms.ValidationError("Password must contain atleast one digit.")

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
