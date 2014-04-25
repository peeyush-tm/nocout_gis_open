from django import forms
from .models import SiteInstance

class SiteInstanceForm(forms.ModelForm):
    class Meta:
        model = SiteInstance
        fields = ('name', 'site_ip', 'agent_port', 'live_status_tcp_port', 'description') 