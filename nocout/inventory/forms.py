from django import forms
from device.models import Country, State, City
from device_group.models import DeviceGroup
from models import Inventory, IconSettings, LivePollingSettings, ThresholdConfiguration, ThematicSettings
from nocout.widgets import IntReturnModelChoiceField
from organization.models import Organization
from user_group.models import UserGroup
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit


#*************************************** Inventory ************************************
class InventoryForm(forms.ModelForm):
    """
    Class Based View Inventory Model form to update and create.
    """

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

        # removing help text for device_groups 'select' field
        self.base_fields['device_groups'].help_text = ''

        super(InventoryForm, self).__init__(*args, **kwargs)
        self.fields['user_group'].empty_label = 'Select'
        self.fields['organization'].empty_label = 'Select'
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
        """
        Meta Information
        """
        model = Inventory


#*************************************** Antenna **************************************
class AntennaForm(forms.ModelForm):
    """
    Class Based View Antenna Model form to update and create.
    """
    POLARIZATION = (
        ('', 'Select'),
        ('Vertical', 'Vertical'),
        ('Horizontal', 'Horizontal')
    )

    SPLITTER_INSTALLED = (
        ('', 'Select'),
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    REFLECTOR = (
        ('', 'Select'),
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    ANTENNA_TYPE = (
        ('', 'Select'),
        ('Normal', 'Normal'),
        ('Narrow Beam', 'Narrow Beam'),
        ('Lens', 'Lens'),
    )

    antenna_type = forms.TypedChoiceField(choices=ANTENNA_TYPE, required=False)
    polarization = forms.TypedChoiceField(choices=POLARIZATION, required=False)
    splitter_installed = forms.TypedChoiceField(choices=SPLITTER_INSTALLED, required=False)
    sync_splitter_used = forms.TypedChoiceField(choices=SPLITTER_INSTALLED, required=False)
    reflector = forms.TypedChoiceField(choices=REFLECTOR, required=False)

    def __init__(self, *args, **kwargs):
        super(AntennaForm, self).__init__(*args, **kwargs)
        self.fields['height'].initial = 0
        self.fields['azimuth_angle'].initial = 0
        self.fields['height'].required = True
        self.fields['azimuth_angle'].required = True
        self.fields['polarization'].required = True

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                else:
                    field.widget.attrs['class'] += ' tip-focus form-control'
                    field.widget.attrs['data-toggle'] = 'tooltip'
                    field.widget.attrs['data-placement'] = 'right'
                    field.widget.attrs['title'] = field.help_text
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': ' tip-focus form-control'})
                    field.widget.attrs.update({'data-toggle': 'tooltip'})
                    field.widget.attrs.update({'data-placement': 'right'})
                    field.widget.attrs.update({'title': field.help_text})

    class Meta:
        """
        Meta Information
        """
        model = Antenna


#************************************* Backhaul ****************************************
class BackhaulForm(forms.ModelForm):
    """
        Class Based View Backhaul Model form to update and create.
    """
    BH_TYPE = (
        ('', 'Select'),
        ('E1', 'E1'),
        ('Ethernet', 'Ethernet'),
        ('SDH', 'SDH'),
        ('UBR', 'UBR')
    )
    BH_CONNECTIVITY = (
        ('', 'Select'),
        ('Onnet', 'Onnet'),
        ('Offnet', 'Offnet')
    )

    DR_SITE = (
        ('', 'Select'),
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    bh_type = forms.TypedChoiceField(choices=BH_TYPE, required=False)
    bh_connectivity = forms.TypedChoiceField(choices=BH_CONNECTIVITY, required=False)
    dr_site = forms.TypedChoiceField(choices=DR_SITE, required=False)

    def __init__(self, *args, **kwargs):
        super(BackhaulForm, self).__init__(*args, **kwargs)
        self.fields['bh_configured_on'].empty_label = 'Select'
        self.fields['bh_switch'].empty_label = 'Select'
        self.fields['pop'].empty_label = 'Select'
        self.fields['aggregator'].empty_label = 'Select'
        self.fields['bh_configured_on'].required = True

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                else:
                    field.widget.attrs['class'] += ' tip-focus form-control'
                    field.widget.attrs['data-toggle'] = 'tooltip'
                    field.widget.attrs['data-placement'] = 'right'
                    field.widget.attrs['title'] = field.help_text
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': ' tip-focus form-control'})
                    field.widget.attrs.update({'data-toggle': 'tooltip'})
                    field.widget.attrs.update({'data-placement': 'right'})
                    field.widget.attrs.update({'title': field.help_text})
    class Meta:
        """
        Meta Information
        """
        model = Backhaul


#************************************ Base Station ****************************************
class BaseStationForm(forms.ModelForm):
    """
    Class Based View Base Station Model form to update and create.
    """

    country = IntReturnModelChoiceField(queryset=Country.objects.all(),
                                        required=False)
    state = IntReturnModelChoiceField(queryset=State.objects.all(),
                                      required=False)
    city = IntReturnModelChoiceField(queryset=City.objects.all(),
                                     required=False)

    BS_TYPE = (
        ('', 'Select'),
        ('Master', 'Master'),
        ('Slave', 'Slave')
    )

    BS_SITE_TYPE = (
        ('', 'Select'),
        ('RTT', 'RTT'),
        ('GBT', 'GBT')
    )

    bs_type = forms.TypedChoiceField(choices=BS_TYPE, required=False)
    bs_site_type = forms.TypedChoiceField(choices=BS_SITE_TYPE, required=False)

    def __init__(self, *args, **kwargs):
        super(BaseStationForm, self).__init__(*args, **kwargs)
        self.fields['bs_technology'].empty_label = 'Select'
        self.fields['bs_switch'].empty_label = 'Select'
        self.fields['backhaul'].empty_label = 'Select'
        self.fields['country'].empty_label = 'Select'
        self.fields['state'].empty_label = 'Select'
        self.fields['city'].empty_label = 'Select'
        self.fields['building_height'].initial =0
        self.fields['tower_height'].initial =0

        self.fields['bs_technology'].required =True
        self.fields['latitude'].required =True
        self.fields['longitude'].required =True
        self.fields['country'].required = True
        self.fields['city'].required =True
        self.fields['state'].required =True
        self.fields['building_height'].required =True
        self.fields['tower_height'].required =True
        self.fields['state'].required= True
        self.fields['city'].required= True

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                else:
                    field.widget.attrs['class'] += ' tip-focus form-control'
                    field.widget.attrs['data-toggle'] = 'tooltip'
                    field.widget.attrs['data-placement'] = 'right'
                    field.widget.attrs['title'] = field.help_text
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': ' tip-focus form-control'})
                    field.widget.attrs.update({'data-toggle': 'tooltip'})
                    field.widget.attrs.update({'data-placement': 'right'})
                    field.widget.attrs.update({'title': field.help_text})
    class Meta:
        """
        Meta Information
        """
        model = BaseStation


#************************************* Sector *************************************
class SectorForm(forms.ModelForm):
    """
    Class Based View Sector Model form to update and create.
    """
    MRC = (
        ('', 'Select'),
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    mrc = forms.TypedChoiceField(choices=MRC, required=False)

    def __init__(self, *args, **kwargs):
        super(SectorForm, self).__init__(*args, **kwargs)
        self.fields['base_station'].empty_label = 'Select'
        self.fields['sector_configured_on'].empty_label = 'Select'
        self.fields['sector_configured_on_port'].empty_label = 'Select'
        self.fields['antenna'].empty_label = 'Select'
        self.fields['antenna'].empty_label = 'Select'
        self.fields['sector_id'].empty_label = True

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                else:
                    field.widget.attrs['class'] += ' tip-focus form-control'
                    field.widget.attrs['data-toggle'] = 'tooltip'
                    field.widget.attrs['data-placement'] = 'right'
                    field.widget.attrs['title'] = field.help_text
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': ' tip-focus form-control'})
                    field.widget.attrs.update({'data-toggle': 'tooltip'})
                    field.widget.attrs.update({'data-placement': 'right'})
                    field.widget.attrs.update({'title': field.help_text})
    class Meta:
        """
        Meta Information
        """
        model = Sector
        
        
#************************************* Customer ***************************************
class CustomerForm(forms.ModelForm):
    """
        Class Based View Customer Model form to update and create.
    """
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
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
        Meta Information
        """
        model = Customer
        
        
#*********************************** Sub Station *************************************
class SubStationForm(forms.ModelForm):
    """
    Class Based View SubStation Model form to update and create.
    """

    country = IntReturnModelChoiceField(queryset=Country.objects.all(),
                                        required=False)
    state = IntReturnModelChoiceField(queryset=State.objects.all(),
                                      required=False)
    city = IntReturnModelChoiceField(queryset=City.objects.all(),
                                     required=False)

    ETHERNET_EXTENDER = (
        ('', 'Select'),
        ('Yes', 'Yes'),
        ('Yo', 'No')
    )

    ethernet_extender = forms.TypedChoiceField(choices=ETHERNET_EXTENDER, required=False)

    def __init__(self, *args, **kwargs):
        super(SubStationForm, self).__init__(*args, **kwargs)
        self.fields['tower_height'].initial = 0
        self.fields['building_height'].initial = 0
        self.fields['country'].empty_label = 'Select'
        self.fields['state'].empty_label = 'Select'
        self.fields['city'].empty_label = 'Select'
        self.fields['device'].empty_label = 'Select'
        self.fields['antenna'].required = True
        self.fields['building_height'].required = True
        self.fields['tower_height'].required = True
        self.fields['country'].required = True
        self.fields['state'].required = True
        self.fields['city'].required = True
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['mac_address'].required = True

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
        Meta Information
        """
        model = SubStation
        
        
#*********************************** Circuit ***************************************
class CircuitForm(forms.ModelForm):
    """
    Class Based View Circuit Model form to update and create.
    """

    date_of_acceptance = forms.DateField(input_formats=('%m/%d/%Y',), help_text='(mm-dd-yyyy) Enter a date.',
                                         required=False, widget=forms.widgets.DateInput(format="%m/%d/%Y", attrs={'class': 'datepicker'}))

    def __init__(self, *args, **kwargs):
        super(CircuitForm, self).__init__(*args, **kwargs)
        self.fields['sector'].empty_label = 'Select'
        self.fields['customer'].empty_label = 'Select'
        self.fields['sub_station'].empty_label = 'Select'
        self.fields['date_of_acceptance'].required = True
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
        Meta Information
        """
        model = Circuit


#*********************************** IconSettings ***************************************
class IconSettingsForm(forms.ModelForm):
    """
    Class Based View IconSettings Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        super(IconSettingsForm, self).__init__(*args, **kwargs)
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
        Meta Information
        """
        model = IconSettings
        
        
#*********************************** LivePollingSettings ***************************************
class LivePollingSettingsForm(forms.ModelForm):
    """
    Class Based View LivePollingSettings Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        super(LivePollingSettingsForm, self).__init__(*args, **kwargs)
        self.fields['technology'].empty_label = 'Select'
        self.fields['service'].empty_label = 'Select'
        self.fields['data_source'].empty_label = 'Select'
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
        Meta Information
        """
        model = LivePollingSettings


#*********************************** LivePollingSettings ***************************************
class ThresholdConfigurationForm(forms.ModelForm):

    """
    Class Based View Threshold Configuration Model form to update and create.
    """
    def __init__(self, *args, **kwargs):
        super(ThresholdConfigurationForm, self).__init__(*args, **kwargs)
        self.fields['live_polling_template'].empty_label = 'Select'
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
        Meta Information
        """
        model = ThresholdConfiguration



#*********************************** LivePollingSettings ***************************************
class ThematicSettingsForm(forms.ModelForm):
    """
    Class Based View Thematic Settings Model form to update and create.
    """
    def __init__(self, *args, **kwargs):
        self.base_fields['gt_warning'].label = '> Warning'
        self.base_fields['bt_w_c'].label = 'Warning > > Critical'
        self.base_fields['gt_critical'].label = '> Critical'

        super(ThematicSettingsForm, self).__init__(*args, **kwargs)
        self.fields['threshold_template'].empty_label = 'Select'
        self.fields['gt_warning'].empty_label = 'Select'
        self.fields['bt_w_c'].empty_label = 'Select'
        self.fields['gt_critical'].empty_label = 'Select'
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12 form-control'
                else:
                    field.widget.attrs['class'] += ' form-control'
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 form-control'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})
    class Meta:
        """
        Meta Information
        """
        model = ThematicSettings
