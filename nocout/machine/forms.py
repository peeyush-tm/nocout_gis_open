"""
=============================================================
Module contains forms functionlity specific to 'machine' app.
=============================================================

Location:
* /nocout_gis/nocout/machine/forms.py

List of constructs:
=======
Classes
=======
* MachineForm
"""

from django.core.exceptions import ValidationError
import re
from django import forms
from models import Machine
from django.forms.util import ErrorList
import logging

logger = logging.getLogger(__name__)


class MachineForm(forms.ModelForm):
    """
    Form required to create and update machine.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize function to change attributes before rending the model form.
        """

        super(MachineForm, self).__init__(*args, **kwargs)

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        self.fields['machine_ip'].required=True
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
        model = Machine

    def clean_name(self):
        """
        Validate name already exist in database or not.
        Unique name validation check.
        """
        name = self.cleaned_data['name']
        names = Machine.objects.filter(name=name)

        # Check for name existance in database.
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

