import logging
from django import forms
from models import CityCharterSettings

logger = logging.getLogger(__name__)


class CityCharterSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """
        Initialize function to change attributes before rending the model form.
        """

        super(CityCharterSettingsForm, self).__init__(*args, **kwargs)
        self.fields.pop('technology')

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
        model = CityCharterSettings