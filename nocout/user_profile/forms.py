from django import forms
from user_profile.models import UserProfile
from nocout.widgets import MultipleToSingleSelectionWidget


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
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

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
