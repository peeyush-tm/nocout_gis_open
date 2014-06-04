from django import forms
from .models import SiteInstance


class SiteInstanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteInstanceForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = SiteInstance
        fields = ('name', 'alias', 'machine', 'site_ip', 'live_status_tcp_port', 'description')
