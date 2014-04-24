from django import forms
from models import Service

class ServiceForm(forms.ModelForm):
    
    class Meta:
        model = Service
        fields = ('service_name', 'alias', 'parameters', 'command', 'description')
