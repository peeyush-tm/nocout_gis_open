import os
from django.core.exceptions import ValidationError
import re
import ast
from django import forms
from device.models import Country, State, City
from device_group.models import DeviceGroup
from models import Inventory, IconSettings, LivePollingSettings, ThresholdConfiguration, ThematicSettings, \
    GISInventoryBulkImport, PingThematicSettings
from nocout.widgets import IntReturnModelChoiceField
from organization.models import Organization
from user_group.models import UserGroup
from django.forms.util import ErrorList
from device.models import Device
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit, CircuitL2Report
from django.utils.html import escape
from nocout.utils import logged_in_user_organizations
import logging
logger = logging.getLogger(__name__)


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

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
            organization_id = initial['organization']
        elif Organization.objects.all():
            organization_id = Organization.objects.all()[0].id
        if organization_id:
            organization_descendants_ids = Organization.objects.get(id= organization_id).get_descendants(include_self=True).values_list('id', flat=True)
            self.fields['device_groups'].queryset = DeviceGroup.objects.filter( organization__in = organization_descendants_ids, is_deleted=0)
            self.fields['user_group'].queryset = UserGroup.objects.filter( organization__in = organization_descendants_ids, is_deleted=0)

    class Meta:
        """
        Meta Information
        """
        model = Inventory

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = Inventory.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for inventory form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


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
        self.request = kwargs.pop('request', None)
        super(AntennaForm, self).__init__(*args, **kwargs)
        self.fields['height'].initial = 0
        self.fields['azimuth_angle'].initial = 0
        self.fields['height'].required = True
        self.fields['azimuth_angle'].required = True
        self.fields['polarization'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            organization = self.request.user.userprofile.organization
            if self.request.user.userprofile.role.values_list( 'role_name', flat=True )[0] =='admin':
                self.fields['organization'].queryset = self.request.user.userprofile.organization.get_descendants(include_self=True)
            else:
                self.fields['organization'].queryset = Organization.objects.filter(id=organization.id)
        else:
            self.fields['organization'].widget.choices = self.fields['organization'].choices

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

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = Antenna.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for antenna form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


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
    dr_site = forms.TypedChoiceField(choices=DR_SITE, initial='No', required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BackhaulForm, self).__init__(*args, **kwargs)
        self.fields['bh_configured_on'].empty_label = 'Select'
        self.fields['bh_switch'].empty_label = 'Select'
        self.fields['pop'].empty_label = 'Select'
        self.fields['aggregator'].empty_label = 'Select'
        self.fields['bh_configured_on'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            organization = self.request.user.userprofile.organization
            if self.request.user.userprofile.role.values_list( 'role_name', flat=True )[0] =='admin':
                self.fields['organization'].queryset = self.request.user.userprofile.organization.get_descendants(include_self=True)
                self.fields['bh_configured_on'].queryset = self.fields['bh_configured_on'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
                self.fields['aggregator'].queryset = self.fields['aggregator'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
                self.fields['bh_switch'].queryset = self.fields['bh_switch'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
                self.fields['pop'].queryset = self.fields['pop'].queryset.filter(organization__in=organization.get_descendants(include_self=True))

            else:

                self.fields['organization'].queryset = Organization.objects.filter(id=organization.id)
                self.fields['bh_configured_on'].queryset = self.fields['bh_configured_on'].queryset.filter(organization=organization)
                self.fields['aggregator'].queryset = self.fields['aggregator'].queryset.filter(organization=organization)
                self.fields['bh_switch'].queryset = self.fields['bh_switch'].queryset.filter(organization=organization)
                self.fields['pop'].queryset = self.fields['pop'].queryset.filter(organization=organization)
        else:
            self.fields['organization'].widget.choices = self.fields['organization'].choices

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
        fields = (
            'name', 'alias', 'organization', 'bh_configured_on', 'bh_port_name', 'bh_port', 'bh_type', 'bh_switch', 'switch_port_name',
            'switch_port', 'pop', 'pop_port_name', 'pop_port', 'aggregator', 'aggregator_port_name', 'aggregator_port', 'pe_hostname',
            'pe_ip', 'bh_connectivity', 'bh_circuit_id', 'bh_capacity', 'ttsl_circuit_id', 'dr_site', 'description',
        )

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = Backhaul.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for backhaul form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


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
        self.request = kwargs.pop('request', None)
        super(BaseStationForm, self).__init__(*args, **kwargs)
        self.fields['bs_switch'].empty_label = 'Select'
        self.fields['backhaul'].empty_label = 'Select'
        self.fields['country'].empty_label = 'Select'
        self.fields['state'].empty_label = 'Select'
        self.fields['city'].empty_label = 'Select'
        self.fields['building_height'].initial = 0
        self.fields['tower_height'].initial = 0
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['country'].required = True
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['building_height'].required = True
        self.fields['tower_height'].required = True
        self.fields['state'].required = True
        self.fields['city'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            organization = self.request.user.userprofile.organization
            if self.request.user.userprofile.role.values_list( 'role_name', flat=True )[0] =='admin':
                self.fields['organization'].queryset = self.request.user.userprofile.organization.get_descendants(include_self=True)
                self.fields['bs_switch'].queryset = self.fields['bs_switch'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
                self.fields['backhaul'].queryset = self.fields['backhaul'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
            else:
                self.fields['organization'].queryset = Organization.objects.filter(id=organization.id)
                self.fields['bs_switch'].queryset = self.fields['bs_switch'].queryset.filter(organization=organization)
                self.fields['backhaul'].queryset = self.fields['backhaul'].queryset.filter(organization=organization)
        else:
            self.fields['organization'].widget.choices = self.fields['organization'].choices

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

        fields = (
            'name', 'alias', 'organization', 'bs_site_id', 'bs_site_type', 'bs_switch', 'backhaul', 'bh_port_name', 'bh_port',
            'bh_capacity', 'bs_type', 'bh_bso', 'hssu_used', 'latitude', 'longitude', 'infra_provider', 'gps_type',
            'building_height', 'tower_height', 'country', 'state', 'city', 'address', 'description',
        )

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = BaseStation.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for base station form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


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

    DR_SITE = (
        ('', 'Select'),
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    mrc = forms.TypedChoiceField(choices=MRC, initial='No', required=False)
    dr_site = forms.TypedChoiceField(choices=DR_SITE, initial='No', required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SectorForm, self).__init__(*args, **kwargs)
        self.fields['base_station'].empty_label = 'Select'
        self.fields['bs_technology'].empty_label = 'Select'
        self.fields['bs_technology'].required = True
        self.fields['sector_configured_on'].empty_label = 'Select'
        self.fields['sector_configured_on_port'].empty_label = 'Select'
        self.fields['antenna'].empty_label = 'Select'
        self.fields['frequency'].empty_label = 'Select'
        self.fields['sector_id'].empty_label = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            organization = self.request.user.userprofile.organization
            if self.request.user.userprofile.role.values_list( 'role_name', flat=True )[0] =='admin':
                self.fields['organization'].queryset = self.request.user.userprofile.organization.get_descendants(include_self=True)
                self.fields['sector_configured_on'].queryset = self.fields['sector_configured_on'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
                self.fields['base_station'].queryset = self.fields['base_station'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
            else:
                self.fields['organization'].queryset = Organization.objects.filter(id=organization.id)
                self.fields['sector_configured_on'].queryset = self.fields['sector_configured_on'].queryset.filter(organization=organization)
                self.fields['base_station'].queryset = self.fields['base_station'].queryset.filter(organization=organization)
        else:
            self.fields['organization'].widget.choices = self.fields['organization'].choices

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

        fields = (
            'name', 'alias', 'organization', 'sector_id', 'base_station', 'bs_technology', 'sector_configured_on', 'sector_configured_on_port', 'antenna',
            'dr_site', 'mrc', 'tx_power', 'rx_power', 'rf_bandwidth', 'frame_length', 'cell_radius', 'frequency',
            'modulation', 'description',
        )

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = Sector.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for sector form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


#************************************* Customer ***************************************
class CustomerForm(forms.ModelForm):
    """
        Class Based View Customer Model form to update and create.
    """
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CustomerForm, self).__init__(*args, **kwargs)

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            organization = self.request.user.userprofile.organization
            if self.request.user.userprofile.role.values_list( 'role_name', flat=True )[0] =='admin':
                self.fields['organization'].queryset = self.request.user.userprofile.organization.get_descendants(include_self=True)
            else:
                self.fields['organization'].queryset = Organization.objects.filter(id=organization.id)
        else:
            self.fields['organization'].widget.choices = self.fields['organization'].choices

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

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = Customer.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for customer form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


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
        ('No', 'No')
    )

    ethernet_extender = forms.TypedChoiceField(choices=ETHERNET_EXTENDER, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request',None)
        super(SubStationForm, self).__init__(*args, **kwargs)
        self.fields['tower_height'].initial = 0
        self.fields['building_height'].initial = 0
        self.fields['country'].empty_label = 'Select'
        self.fields['state'].empty_label = 'Select'
        self.fields['city'].empty_label = 'Select'
        self.fields['device'].empty_label = 'Select'
        self.fields['antenna'].empty_label = 'Select'
        self.fields['antenna'].required = True
        self.fields['building_height'].required = True
        self.fields['tower_height'].required = True
        self.fields['country'].required = True
        self.fields['state'].required = True
        self.fields['city'].required = True
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['mac_address'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            organization = self.request.user.userprofile.organization
            if self.request.user.userprofile.role.values_list( 'role_name', flat=True )[0] =='admin':
                self.fields['organization'].queryset = self.request.user.userprofile.organization.get_descendants(include_self=True)
                self.fields['device'].queryset = self.fields['device'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
                self.fields['antenna'].queryset = self.fields['antenna'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
            else:
                self.fields['organization'].queryset = Organization.objects.filter(id=organization.id)
                self.fields['device'].queryset = self.fields['device'].queryset.filter(organization=organization)
                self.fields['antenna'].queryset = self.fields['antenna'].queryset.filter(organization=organization)
        else:
            self.fields['organization'].widget.choices = self.fields['organization'].choices

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
        model = SubStation
        fields = (
            'name', 'alias', 'organization', 'device', 'antenna', 'version', 'serial_no', 'building_height', 'tower_height',
            'ethernet_extender', 'cable_length', 'latitude', 'longitude', 'mac_address', 'country', 'state', 'city',
            'address', 'description',
        )

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = SubStation.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for sub station form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


#*********************************** Circuit ***************************************
class CircuitForm(forms.ModelForm):
    """
    Class Based View Circuit Model form to update and create.
    """

    date_of_acceptance = forms.DateField(input_formats=('%m/%d/%Y',), help_text='(mm-dd-yyyy) Enter a date.',
                                         required=False, widget=forms.widgets.DateInput(format="%m/%d/%Y", attrs={'class': 'datepicker'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CircuitForm, self).__init__(*args, **kwargs)
        self.fields['sector'].empty_label = 'Select'
        self.fields['customer'].empty_label = 'Select'
        self.fields['sub_station'].empty_label = 'Select'
        self.fields['date_of_acceptance'].required = True

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            organization = self.request.user.userprofile.organization
            if self.request.user.userprofile.role.values_list( 'role_name', flat=True )[0] =='admin':
                self.fields['organization'].queryset = self.request.user.userprofile.organization.get_descendants(include_self=True)
                self.fields['sector'].queryset = self.fields['sector'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
                self.fields['customer'].queryset = self.fields['customer'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
                self.fields['sub_station'].queryset = self.fields['sub_station'].queryset.filter(organization__in=organization.get_descendants(include_self=True))
            else:
                self.fields['organization'].queryset = Organization.objects.filter(id=organization.id)
                self.fields['sector'].queryset = self.fields['sector'].queryset.filter(organization=organization)
                self.fields['customer'].queryset = self.fields['customer'].queryset.filter(organization=organization)
                self.fields['sub_station'].queryset = self.fields['sub_station'].queryset.filter(organization=organization)
        else:
            self.fields['organization'].widget.choices = self.fields['organization'].choices

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
        model = Circuit
        fields = (
            'name', 'alias', 'organization', 'circuit_type', 'circuit_id', 'sector', 'customer', 'sub_station', 'qos_bandwidth',
            'dl_rssi_during_acceptance', 'dl_cinr_during_acceptance', 'jitter_value_during_acceptance', 'throughput_during_acceptance', 'date_of_acceptance', 'description',
        )


    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = Circuit.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for circuit form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


#******************************* Circuit L2 Reports Form **************************
class CircuitL2ReportForm(forms.ModelForm):
    """
    Class Based View CircuitL2Report Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        super(CircuitL2ReportForm, self).__init__(*args, **kwargs)

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
            	if not(isinstance(field.widget, forms.widgets.CheckboxInput)):
	                field.widget.attrs['class'] += ' tip-focus form-control'
	                field.widget.attrs['data-toggle'] = 'tooltip'
	                field.widget.attrs['data-placement'] = 'right'
	                field.widget.attrs['title'] = field.help_text
	                field.widget.attrs['style'] = 'padding:0px 12px;height:40px;'
                else:
                	field.widget.attrs['checked'] = "true"
            else:
            	if not(isinstance(field.widget, forms.widgets.CheckboxInput)):
	                field.widget.attrs.update({'class': ' tip-focus form-control'})
	                field.widget.attrs.update({'data-toggle': 'tooltip'})
	                field.widget.attrs.update({'data-placement': 'right'})
	                field.widget.attrs.update({'title': field.help_text})
	                field.widget.attrs.update({'style' : 'padding:0px 12px;height:40px;'})
                else:
                	field.widget.attrs['checked'] = "true"

    class Meta:
        """
        Meta Information
        """
        model = CircuitL2Report
        exclude = ['added_on', 'user_id', 'circuit_id']

    def clean_file_name(self):
        IMPORT_FILE_TYPES = ['.xls', '.xlsx']
        input_excel = self.cleaned_data.get('file_name')
        extension = os.path.splitext(input_excel.name)[1]
        if not (extension in IMPORT_FILE_TYPES):
            raise ValidationError( u'%s is not the supported file. Please make sure your input file is an excel(.xls) file.' % extension )
        else:
            return input_excel

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = CircuitL2Report.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')

        return name


#*********************************** IconSettings ***************************************
class IconSettingsForm(forms.ModelForm):
    """
    Class Based View IconSettings Model form to update and create.
    """

    def __init__(self, *args, **kwargs):

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = IconSettings.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for icon settings form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


#*********************************** LivePollingSettings ***************************************
class LivePollingSettingsForm(forms.ModelForm):
    """
    Class Based View LivePollingSettings Model form to update and create.
    """

    def __init__(self, *args, **kwargs):

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = LivePollingSettings.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for live polling form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


#*********************************** LivePollingSettings ***************************************
class ThresholdConfigurationForm(forms.ModelForm):

    """
    Class Based View Threshold Configuration Model form to update and create.
    """
    def __init__(self, *args, **kwargs):

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

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
        exclude =['range1_icon', 'range2_icon', 'range3_icon', 'range4_icon', 'range5_icon', 'range6_icon', 'range7_icon',\
                  'range8_icon','range9_icon','range10_icon']
    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = ThresholdConfiguration.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for threshold configuration form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data



#*********************************** LivePollingSettings ***************************************
class ThematicSettingsForm(forms.ModelForm):
    """
    Class Based View Thematic Settings Model form to update and create.
    """
    def __init__(self, *args, **kwargs):
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(ThematicSettingsForm, self).__init__(*args, **kwargs)
        self.fields['threshold_template'].empty_label = 'Select'
        # if self.instance.pk:
        #     self.fields['threshold_template'].widget.attrs['disabled'] = 'disabled'
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
        exclude =['icon_settings', 'user_profile']

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = ThematicSettings.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for thematic settings form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


#*********************************** Bulk Import ***************************************
class GISInventoryBulkImportForm(forms.Form):
    IMPORT_FILE_TYPES = ['.xls']
    # SHEET_CHOICES = [('', 'Select')] + [(str(id), str(id)) for id in range(50)]
    SHEET_CHOICES = (
        ("", "Select"),
        ("Wimax BS", "Wimax BS"),
        ("Wimax SS", "Wimax SS"),
        ("PMP BS", "Wimax BS"),
        ("PMP SM", "PMP SM"),
        ("Converter", "Converter"),
        ("PTP", "PTP"),
        ("PTP BH", "PTP BH")
    )
    file_upload = forms.FileField(label='Inventory Excel Sheet')
    bs_sheet = forms.ChoiceField(label='Wimax/PMP BS Sheet', choices=SHEET_CHOICES, required=False)
    ss_sheet = forms.ChoiceField(label='Wimax/PMP SS Sheet', choices=SHEET_CHOICES, required=False)
    ptp_sheet = forms.ChoiceField(label='PTP Sheet', choices=SHEET_CHOICES, required=False)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(GISInventoryBulkImportForm, self).__init__(*args, **kwargs)
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

    def clean_file_upload(self):
        input_excel = self.cleaned_data['file_upload']
        extension = os.path.splitext(input_excel.name)[1]
        if not (extension in GISInventoryBulkImportForm.IMPORT_FILE_TYPES):
            raise forms.ValidationError( u'%s is not the supported file. Please make sure your input file is an excel(.xls) file.' % extension )
        else:
            return input_excel

    def clean_description(self):
        description = self.cleaned_data['description']
        try:
            description = escape(description)
        except Exception as e:
            logger.info(e.message)
        return description


#*********************************** LivePollingSettings ***************************************
class GISInventoryBulkImportEditForm(forms.ModelForm):

    """
    Class Based View GISInventoryBulkImport Model form to update and create.
    """
    def __init__(self, *args, **kwargs):
        super(GISInventoryBulkImportEditForm, self).__init__(*args, **kwargs)
        self.fields['original_filename'].widget.attrs['readonly'] = True
        self.fields['valid_filename'].widget.attrs['readonly'] = True
        self.fields['invalid_filename'].widget.attrs['readonly'] = True
        self.fields['sheet_name'].widget.attrs['readonly'] = True
        self.fields['technology'].widget.attrs['readonly'] = True
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
        model = GISInventoryBulkImport
        exclude = ['status', 'uploaded_by', 'added_on', 'modified_on', 'upload_status']


#************************************** Ping Thematic Settings **********************************
class PingThematicSettingsForm(forms.ModelForm):
    """
        Ping thematic settings form
    """
    # icon choices fetched from 'IconSettings' model
    ICON_CHOICES = [('', 'Select')]
    try:
        ICON_CHOICES = [('', 'Select')] + [(icon.upload_image, icon.alias) for icon in IconSettings.objects.all()]
    except Exception as e:
        logger.info("No choices for icon. Exception: {}".format(e.message))

    # services select menu choices
    SERVICES = (
        ('', 'Select'),
        ('ping', 'Ping')
    )

    # data sources menu choices
    DATA_SOURCES = (
        ('', 'Select'),
        ('pl', 'PL'),
        ('rta', 'RTA')
    )

    # icon fields
    icon_settings1 = forms.ChoiceField(label='Icon 1', choices=ICON_CHOICES, required=False)
    icon_settings2 = forms.ChoiceField(label='Icon 2', choices=ICON_CHOICES, required=False)
    icon_settings3 = forms.ChoiceField(label='Icon 3', choices=ICON_CHOICES, required=False)
    icon_settings4 = forms.ChoiceField(label='Icon 4', choices=ICON_CHOICES, required=False)
    icon_settings5 = forms.ChoiceField(label='Icon 5', choices=ICON_CHOICES, required=False)
    icon_settings6 = forms.ChoiceField(label='Icon 6', choices=ICON_CHOICES, required=False)
    icon_settings7 = forms.ChoiceField(label='Icon 7', choices=ICON_CHOICES, required=False)
    icon_settings8 = forms.ChoiceField(label='Icon 8', choices=ICON_CHOICES, required=False)
    icon_settings9 = forms.ChoiceField(label='Icon 9', choices=ICON_CHOICES, required=False)
    icon_settings10 = forms.ChoiceField(label='Icon 10', choices=ICON_CHOICES, required=False)

    # service field
    service = forms.TypedChoiceField(choices=SERVICES, required=True)

    # data source field
    data_source = forms.TypedChoiceField(choices=DATA_SOURCES, required=True)

    def __init__(self, *args, **kwargs):
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(PingThematicSettingsForm, self).__init__(*args, **kwargs)

        # modify technology field initial option
        self.fields['technology'].empty_label = 'Select'

        # fetch default options for icon setting fields
        icon_settings = ""
        try:
            icon_settings = PingThematicSettings.objects.get(id=self.id).icon_settings

            # convert string into python list of dictionaries
            icon_settings = ast.literal_eval(icon_settings)

            # loop through list 'icon_settings' containing dictionaries for icon settings for all selected ranges
            for ic_dict in icon_settings:
                field, value = ic_dict.items()[0]
                # setting initial value for a field
                self.initial[field] = value

        except Exception as e:
            pass

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
        model = PingThematicSettings
        exclude = ['icon_settings', 'user_profile']

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = ThematicSettings.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        return name

    def clean(self):
        """
        Validations for thematic settings form
        """
        name = self.cleaned_data.get('name')

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data
