"""
===================================================================
Module contains forms functionlity specific to 'site_instance' app.
===================================================================

Location:
* /nocout_gis/nocout/site_instance/forms.py

List of constructs:
=======
Classes
=======
* SiteInstanceForm
"""

import re
from django import forms
from django.core.exceptions import ValidationError
from models import SiteInstance
from django.forms.util import ErrorList
import logging

logger = logging.getLogger(__name__)


class SiteInstanceForm(forms.ModelForm):
    """
    Form required to create and update site instance.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize function to change attributes before rending the model form.
        """
        super(SiteInstanceForm, self).__init__(*args, **kwargs)

        self.fields['machine'].empty_label = 'Select'
        self.fields['machine'].required = True
        self.fields['username'].required = True
        self.fields['password'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        model = SiteInstance

    def clean_name(self):
        """
        Validate name already exist in database or not.
        Unique name validation check.
        """
        name = self.cleaned_data['name']
        names = SiteInstance.objects.filter(name=name)

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
        Validations for all fields or field validations which are dependent on each other can be defined here.
        """
        name = self.cleaned_data.get('name')

        # Check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data

