from django import forms
from user_profile.models import UserProfile
from nocout.widgets import MultipleToSingleSelectionWidget

class UserForm(forms.ModelForm):

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request=kwargs.pop('request', None)
        initial = kwargs.setdefault('initial',{})

        if kwargs['instance']:
            initial['role'] = kwargs['instance'].role.values_list('pk', flat=True)[0]
            initial['parent'] = kwargs['instance'].parent
            initial['organization'] = kwargs['instance'].organization

        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['parent'].empty_label = 'Select'
        self.fields['organization'].empty_label = 'Select'

        if self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            if self.instance.pk == self.request.pk:
                self.fields['username'].widget.attrs['readonly'] = True
                self.fields['parent'].widget.attrs['disabled'] = 'disabled'
                self.fields['role'].widget.attrs['disabled'] = 'disabled'
                self.fields['organization'].widget.attrs['readonly'] = True
                self.fields['parent'].label='Manager'
                self.fields.pop('comment')

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})

    class Meta:
        model = UserProfile
        fields = (
            'username', 'first_name', 'last_name', 'email', 'role', 'parent', 'designation', 'company',
            'address', 'phone_number', 'comment','organization'
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
        # Check that the two password entries match
        password2 = self.cleaned_data.get("password2")
        password1 = self.cleaned_data.get("password1")
        if (password1 or password2) and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
