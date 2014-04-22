from django import forms
from site_instance.models import SiteInstance

class SiteInstanceForm(forms.ModelForm):
    class Meta:
        model = SiteInstance
        fields = ('name','description','site_ip')