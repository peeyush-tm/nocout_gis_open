from django import forms
from .models import SiteInstance
import re
from django.forms.util import ErrorList
import logging
logger = logging.getLogger(__name__)


class SiteInstanceForm(forms.ModelForm):
    """
    Class Based SiteInstance Model Form required to create and update the SiteInstance.
    """
    def __init__(self, *args, **kwargs):
        super(SiteInstanceForm, self).__init__(*args, **kwargs)
        self.fields['machine'].empty_label = 'Select'
        self.fields['machine'].required = True
        self.fields['username'].required = True
        self.fields['password'].required = True

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
        Model Form Meta Information.
        """
        model = SiteInstance

    def clean(self):
        """
        Validations for site instance form
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

