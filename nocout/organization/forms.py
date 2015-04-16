from django.core.exceptions import ValidationError
import re
from django import forms
from .models import Organization
from nocout.utils import logged_in_user_organizations
from django.forms.util import ErrorList
import logging
logger = logging.getLogger(__name__)


class OrganizationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop('request') # Also used in logged_in_user_organizations below
        if 'instance' in kwargs and kwargs['instance']:
            self.id = kwargs['instance'].id
        else:
            self.id = None

        super(OrganizationForm, self).__init__(*args, **kwargs)
        if self.id and self.id == self.request.user.userprofile.organization.id:
            # User can not update self organization's parent.
            self.fields.pop('parent')
        else:
            # Organization's parent is required but can not be set to self.
            self.fields['parent'].empty_label = 'Select'
            self.fields['parent'].required = True
            parent_queryset = self.fields['parent'].queryset.filter(id__in=logged_in_user_organizations(self))
            if self.id:
                self.fields['parent'].queryset = parent_queryset.exclude(id=self.id)

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
        model = Organization

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = Organization.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for command form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data
