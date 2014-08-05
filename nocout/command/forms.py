from django import forms
from models import Command


# command form
class CommandForm(forms.ModelForm):
    """
    The Class Based Command Model Form.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize function to change attributes before rending the model form.

        """
        super(CommandForm, self).__init__(*args, **kwargs)
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
        Model name required for the model form to generate in the meta information
        """
        model = Command
