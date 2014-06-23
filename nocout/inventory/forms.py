from django import forms
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit

# antenna form
class AntennaForm(forms.ModelForm):

    POLARIZATION = (
        ('', 'Select....'),
        ('vertical', 'Vertical'),
        ('horizontal', 'Horizontal')
    )

    SPLITTER_INSTALLED = (
        ('', 'Select....'),
        ('yes', 'Yes'),
        ('no', 'No')
    )

    polarization = forms.TypedChoiceField(choices=POLARIZATION, required=False)
    splitter_installed = forms.TypedChoiceField(choices=SPLITTER_INSTALLED, required=False)
    sync_splitter_used = forms.TypedChoiceField(choices=SPLITTER_INSTALLED, required=False)

    def __init__(self, *args, **kwargs):
        super(AntennaForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = Antenna


# base station form
class BaseStationForm(forms.ModelForm):
    BS_TYPE = (
        ('', 'Select....'),
        ('master', 'Master'),
        ('slave', 'Slave')
    )

    bs_type = forms.TypedChoiceField(choices=BS_TYPE, required=False)

    def __init__(self, *args, **kwargs):
        super(BaseStationForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = BaseStation


# base station form
class BackhaulForm(forms.ModelForm):
    BH_TYPE = (
        ('', 'Select....'),
        ('e1', 'E1'),
        ('ethernet', 'Ethernet')
    )
    BH_CONNECTIVITY = (
        ('', 'Select....'),
        ('onnet', 'Onnet'),
        ('offnet', 'Offnet')
    )

    bh_type = forms.TypedChoiceField(choices=BH_TYPE, required=False)
    bh_connectivity = forms.TypedChoiceField(choices=BH_CONNECTIVITY, required=False)

    def __init__(self, *args, **kwargs):
        super(BackhaulForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = Backhaul
        
        
# sector form
class SectorForm(forms.ModelForm):
    MRC = (
        ('', 'Select....'),
        ('yes', 'Yes'),
        ('no', 'No')
    )

    mrc = forms.TypedChoiceField(choices=MRC, required=False)

    def __init__(self, *args, **kwargs):
        super(SectorForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = Sector
        
        
# customer form
class CustomerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = Customer
        
        
# sub_station form
class SubStationForm(forms.ModelForm):
    ETHERNET_EXTENDER = (
        ('', 'Select....'),
        ('yes', 'Yes'),
        ('no', 'No')
    )

    ethernet_extender = forms.TypedChoiceField(choices=ETHERNET_EXTENDER, required=False)

    def __init__(self, *args, **kwargs):
        super(SubStationForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = SubStation
        
        
# circuit form
class CircuitForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CircuitForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})
    class Meta:
        model = Circuit
