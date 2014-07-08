from django import forms
from .models import SiteInstance


class SiteInstanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteInstanceForm, self).__init__(*args, **kwargs)
        self.fields['machine'].empty_label = 'Select'
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
        model = SiteInstance
        fields = ('name', 'alias', 'machine', 'site_ip', 'live_status_tcp_port', 'description')

