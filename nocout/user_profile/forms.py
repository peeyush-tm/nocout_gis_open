from django import forms
from user_profile.models import UserProfile
from nocout.widgets import MultipleToSingleSelectionWidget

class UserForm(forms.ModelForm):

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request=kwargs.pop('request', None)
        super(UserForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        if instance and instance.pk==self.request.pk:
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['parent'].widget.attrs['disabled'] = 'disabled'
            self.fields['role'].widget.attrs['disabled'] = 'disabled'
            self.fields['parent'].label='Manager'
            self.fields.pop('comment')
            self.fields.pop('user_group')
            self.fields['password1'].required = False
            self.fields['password2'].required = False

            if 'password1' in self.errors:
                if 'This field is required.' == self.errors['password1'][0]:
                    del self.errors['password1']
            if 'password2' in self.errors:
                if (('This field is required.' == self.errors['password2'][0]) and (self.cleaned_data['password1'])):
                        del self.errors['password2'][0]
                elif 'This field is required.' == self.errors['password2'][0]:
                        del self.errors['password2'][0]

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
        self.base_fields['user_group'].help_text = "Please select a Usergroup."

    class Meta:
        model = UserProfile
        fields = (
            'username', 'first_name', 'last_name', 'email', 'role', 'user_group', 'parent', 'designation', 'company',
            'address', 'phone_number', 'comment',
        )
        widgets = {
            'role': MultipleToSingleSelectionWidget,
            'user_group': MultipleToSingleSelectionWidget,
        }
        fieldsets = (
            ('Personal', {
                'fields': ('first_name', 'last_name')
            }),
        )

    def clean(self):
         super(UserForm, self).clean()
         return self.cleaned_data

    def clean_password2(self):
        # Check that the two password entries match
        password2 = self.cleaned_data.get("password2")
        password1 = self.cleaned_data.get("password1")
        if (password1 or password2) and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_username(self):
        if self.instance.pk==self.request.pk:
            return self.instance.username
        else:
            return self.cleaned_data['username']

    def clean_parent(self):
        if self.instance.pk==self.request.pk:
            return self.instance.parent
        else:
            return self.cleaned_data['parent']

    def clean_role(self):
        if self.instance.pk==self.request.pk:
            return self.instance.role
        else:
            return self.cleaned_data['role']

    def clean_user_group(self):
        if self.instance.pk==self.request.pk:
            return self.instance.user_group
        else:
            return self.cleaned_data['user_group']
