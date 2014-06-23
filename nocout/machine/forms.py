from django import forms
from models import Machine


# machine form
class MachineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MachineForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = Machine
