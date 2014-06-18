from django import forms
from models import Antenna


# gis antenna form
class AntennaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AntennaForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = Antenna

