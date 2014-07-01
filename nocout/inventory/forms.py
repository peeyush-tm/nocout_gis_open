from django import forms
from device_group.models import DeviceGroup
from models import Inventory
# gis antenna form
from organization.models import Organization
from user_group.models import UserGroup
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit


#*************************************** Inventory ************************************
class InventoryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        initial = kwargs.setdefault('initial',{})
        if kwargs['instance']:
            initial['organization']= kwargs['instance'].organization.id
            initial['user_group']= kwargs['instance'].user_group.id
            initial['device_groups']= kwargs['instance'].device_groups.values_list('id', flat=True)

        elif Organization.objects.all():
            initial['organization']=Organization.objects.all()[0].id
        else:
            initial['organization']=None

        super(InventoryForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})

        organization_id=None
        if kwargs['instance']:
            self.fields['name'].widget.attrs['readonly'] = True
            organization_id=initial['organization']
        elif Organization.objects.all():
            organization_id=Organization.objects.all()[0].id
        if organization_id:
            organization_descendants_ids= Organization.objects.get(id= organization_id).get_descendants(include_self=True).values_list('id', flat=True)
            self.fields['device_groups'].queryset= DeviceGroup.objects.filter( organization__in = organization_descendants_ids, is_deleted=0)
            self.fields['user_group'].queryset = UserGroup.objects.filter( organization__in = organization_descendants_ids, is_deleted=0)

    class Meta:
        model = Inventory


#*************************************** Antenna **************************************
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


#************************************* Backhaul ****************************************
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


#************************************ Base Station ****************************************
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


#************************************* Sector *************************************
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
        
        
#************************************* Customer ***************************************
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
        
        
#*********************************** Sub Station *************************************
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
        
        
#*********************************** Circuit ***************************************
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
