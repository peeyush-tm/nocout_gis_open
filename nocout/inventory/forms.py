import os
from django.core.exceptions import ValidationError
import re
import ast
from django import forms
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from device.models import Country, State, City, StateGeoInfo
from models import IconSettings, LivePollingSettings, ThresholdConfiguration, ThematicSettings, \
    GISInventoryBulkImport, PingThematicSettings, GISExcelDownload
from nocout.widgets import IntReturnModelChoiceField
from organization.models import Organization
from django.forms.util import ErrorList
from device.models import Device
from models import Antenna, BaseStation, Backhaul, Sector, Customer, SubStation, Circuit, CircuitL2Report
from django.utils.html import escape
from django.forms.models import inlineformset_factory, BaseInlineFormSet, modelformset_factory
import logging
from user_profile.utils.auth import in_group

logger = logging.getLogger(__name__)


# *************************************** Antenna **************************************
class AntennaForm(forms.ModelForm):
    """
    Class Based View Antenna Model form to update and create.
    """
    POLARIZATION = (
        ('', 'Select'),
        ('Vertical', 'Vertical'),
        ('Horizontal', 'Horizontal'),
        ('Dual', 'Dual')
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
        ('Internal', 'Internal'),
        ('External', 'External')
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
            '''
            Checks if user is admin then organization field will be admin's organization & suborganization else
            organization field will be user's organization only.
            '''
            organization = self.request.user.userprofile.organization
            if in_group(self.request.user, 'admin'):
                self.fields['organization'].queryset = self.request.user.userprofile.organization.get_descendants(
                    include_self=True)
            else:
                self.fields['organization'].queryset = Organization.objects.filter(id=organization.id)

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
        fields = "__all__"

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


# ************************************* Backhaul ****************************************
class BackhaulForm(forms.ModelForm):
    """
        Class Based View Backhaul Model form to update and create.
    """
    BH_TYPE = (
        ('', 'Select'),
        ('E1', 'E1'),
        ('Ethernet', 'Ethernet'),
        ('Fiber', 'Fiber'),
        ('Dark Fibre', 'Dark Fibre'),
        ('UBR', 'UBR'),
        ('SDH', 'SDH')
    )

    DR_SITE = (
        ('', 'Select'),
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    bh_type = forms.TypedChoiceField(choices=BH_TYPE, required=False)
    dr_site = forms.TypedChoiceField(choices=DR_SITE, initial='No', required=False)
    pe_hostname = forms.CharField(label='PE Hostname', required=False,
                                  validators=[RegexValidator(regex=r'^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$',
                                                             message="Enter valid domain name.")]
                                  )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BackhaulForm, self).__init__(*args, **kwargs)
        self.fields['bh_configured_on'].empty_label = 'Select'
        self.fields['bh_switch'].empty_label = 'Select'
        self.fields['pop'].empty_label = 'Select'
        self.fields['aggregator'].empty_label = 'Select'
        self.fields['bh_configured_on'].required = True

        self.fields['bh_configured_on'].widget = forms.HiddenInput()
        self.fields['bh_switch'].widget = forms.HiddenInput()
        self.fields['pop'].widget = forms.HiddenInput()
        self.fields['aggregator'].widget = forms.HiddenInput()
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id

        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            request = self.request

            if in_group(request.user, 'admin'):
                self.fields['organization'].queryset = request.user.userprofile.organization.get_descendants(
                    include_self=True)
            else:
                self.fields['organization'].queryset = Organization.objects.filter(
                    id=request.user.userprofile.organization.id)

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
        # fields = "__all__"
        exclude = ['ior_id', 'bh_provider', 'bh_port_name', 'bh_port', 'bh_capacity']

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


# ************************************ Base Station ****************************************
class BaseStationForm(forms.ModelForm):
    """
    Class Based View Base Station Model form to update and create.
    """

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

    MAINTENANCE_STATUS = (
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    PROVISIONING_STATUS = (
        ('', 'Select'),
        ('Installed', 'Installed'),
        ('Ready for Migration', 'Ready for Migration'),
        ('Ready - Non Operational', 'Ready - Non Operational'),
        ('Ready in Service', 'Ready in Service'),
        ('Decommissioned', 'Decommissioned')
    )

    bs_type = forms.TypedChoiceField(choices=BS_TYPE, required=False)
    maintenance_status = forms.TypedChoiceField(choices=MAINTENANCE_STATUS, required=False, initial='No')
    provisioning_status = forms.TypedChoiceField(choices=PROVISIONING_STATUS, required=False)
    bs_site_type = forms.TypedChoiceField(choices=BS_SITE_TYPE, required=False)
    building_height = forms.FloatField(label='Building Height', required=True, initial=0,
                                       help_text='(mtr) Enter a number.',
                                       validators=[MaxValueValidator(99), MinValueValidator(-1)])
    tower_height = forms.FloatField(label='Tower Height', required=True, initial=0, help_text='(mtr) Enter a number.',
                                    validators=[MaxValueValidator(99), MinValueValidator(-1)])

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BaseStationForm, self).__init__(*args, **kwargs)
        self.fields['bs_switch'].empty_label = 'Select'
        self.fields['backhaul'].empty_label = 'Select'
        self.fields['country'].empty_label = 'Select'
        self.fields['state'].empty_label = 'Select'
        self.fields['city'].empty_label = 'Select'
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['country'].required = True
        self.fields['state'].required = True
        self.fields['city'].required = True

        self.fields['bs_switch'].widget = forms.HiddenInput()
        self.fields['backhaul'].widget = forms.HiddenInput()
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id

        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            request = self.request

            if in_group(request.user, 'admin'):
                self.fields['organization'].queryset = request.user.userprofile.organization.get_descendants(
                    include_self=True)
            else:
                self.fields['organization'].queryset = Organization.objects.filter(
                    id=request.user.userprofile.organization.id)

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
        # fields = "__all__"
        exclude = ['site_ams', 'site_infra_type', 'site_sap_id', 'mgmt_vlan', 'has_pps_alarm']

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
        latitude = self.request.POST.get('latitude') #self.cleaned_data.get('latitude')
        longitude = self.request.POST.get('longitude') #self.cleaned_data.get('longitude')
        state = self.cleaned_data.get('state')
        name = self.cleaned_data.get('name')

        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()

        try:
            is_lat_long_valid = nocout_utils.is_lat_long_in_state(float(latitude), float(longitude), state)
        except Exception, e:
            is_lat_long_valid = False

        if not is_lat_long_valid:
            self._errors["latitude"] = ErrorList(
                [u"Latitude, longitude specified doesn't exist within selected state."])

        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


# ************************************* Sector *************************************
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
        self.fields['dr_configured_on'].empty_label = 'Select'
        self.fields['sector_configured_on_port'].empty_label = 'Select'
        self.fields['antenna'].empty_label = 'Select'
        self.fields['frequency'].empty_label = 'Select'
        self.fields['sector_id'].empty_label = True

        self.fields['sector_configured_on'].widget = forms.HiddenInput()
        self.fields['dr_configured_on'].widget = forms.HiddenInput()
        self.fields['base_station'].widget = forms.HiddenInput()
        self.fields['antenna'].widget = forms.HiddenInput()
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id

        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            request = self.request

            if in_group(request.user, 'admin'):
                self.fields['organization'].queryset = request.user.userprofile.organization.get_descendants(
                    include_self=True)
            else:
                self.fields['organization'].queryset = Organization.objects.filter(
                    id=request.user.userprofile.organization.id)

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
        # fields = "__all__"
        exclude = ['rfs_date']

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


# ************************************* Customer ***************************************
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
            '''
            Checks if user is admin then organization field will be admin's organization & suborganization else
            organization field will be user's organization only.
            '''
            organization = self.request.user.userprofile.organization
            if in_group(self.request.user, 'admin'):
                self.fields['organization'].queryset = self.request.user.userprofile.organization.get_descendants(
                    include_self=True)
            else:
                self.fields['organization'].queryset = Organization.objects.filter(id=organization.id)

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
        fields = "__all__"

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


# *********************************** Sub Station *************************************
class SubStationForm(forms.ModelForm):
    """
    Class Based View SubStation Model form to update and create.
    """

    ETHERNET_EXTENDER = (
        ('', 'Select'),
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    ethernet_extender = forms.TypedChoiceField(choices=ETHERNET_EXTENDER, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
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

        self.fields['device'].widget = forms.HiddenInput()
        self.fields['antenna'].widget = forms.HiddenInput()
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            request = self.request

            if in_group(request.user, 'admin'):
                self.fields['organization'].queryset = request.user.userprofile.organization.get_descendants(
                    include_self=True)
            else:
                self.fields['organization'].queryset = Organization.objects.filter(
                    id=request.user.userprofile.organization.id)

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
        # fields = "__all__"
        exclude = ['cpe_vlan', 'sacfa_no']

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
        latitude = self.request.POST.get('latitude') #self.cleaned_data.get('latitude')
        longitude = self.request.POST.get('longitude') #self.cleaned_data.get('longitude')
        state = self.cleaned_data.get('state')
        name = self.cleaned_data.get('name')

        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()

        try:
            is_lat_long_valid = nocout_utils.is_lat_long_in_state(float(latitude), float(longitude), state)
        except Exception, e:
            is_lat_long_valid = False

        if not is_lat_long_valid:
            self._errors["latitude"] = ErrorList(
                [u"Latitude, longitude specified doesn't exist within selected state."])

        # '''
        # check that name must be alphanumeric & can only contains .(dot), -(hyphen), _(underscore).
        try:
            if not re.match(r'^[A-Za-z0-9\._-]+$', name):
                self._errors['name'] = ErrorList(
                    [u"Name must be alphanumeric & can only contains .(dot), -(hyphen) and _(underscore)."])
        except Exception as e:
            logger.info(e.message)
        return self.cleaned_data


# *********************************** Circuit ***************************************
class CircuitForm(forms.ModelForm):
    """
    Class Based View Circuit Model form to update and create.
    """

    date_of_acceptance = forms.DateField(input_formats=('%m/%d/%Y',), help_text='(mm-dd-yyyy) Enter a date.',
                                         required=False, widget=forms.widgets.DateInput(format="%m/%d/%Y",
                                                                                        attrs={'class': 'datepicker'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CircuitForm, self).__init__(*args, **kwargs)
        self.fields['sector'].empty_label = 'Select'
        self.fields['customer'].empty_label = 'Select'
        self.fields['sub_station'].empty_label = 'Select'
        self.fields['date_of_acceptance'].required = True

        self.fields['sector'].widget = forms.HiddenInput()
        self.fields['customer'].widget = forms.HiddenInput()
        self.fields['sub_station'].widget = forms.HiddenInput()
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        if self.request is not None:
            request = self.request

            if in_group(request.user, 'admin'):
                self.fields['organization'].queryset = request.user.userprofile.organization.get_descendants(
                    include_self=True)
            else:
                self.fields['organization'].queryset = Organization.objects.filter(
                    id=request.user.userprofile.organization.id)

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
        # fields = "__all__"
        exclude = ['sold_cir']

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


# ******************************* Circuit L2 Reports Form **************************
class L2ReportForm(forms.ModelForm):
    """
    Class Based View CircuitL2Report Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        super(L2ReportForm, self).__init__(*args, **kwargs)

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if not (isinstance(field.widget, forms.widgets.CheckboxInput)):
                    field.widget.attrs['class'] += ' tip-focus form-control'
                    field.widget.attrs['data-toggle'] = 'tooltip'
                    field.widget.attrs['data-placement'] = 'right'
                    field.widget.attrs['title'] = field.help_text
                    field.widget.attrs['style'] = 'padding:0px 12px;height:40px;'
                else:
                    field.widget.attrs['checked'] = "true"
            else:
                if not (isinstance(field.widget, forms.widgets.CheckboxInput)):
                    field.widget.attrs.update({'class': ' tip-focus form-control'})
                    field.widget.attrs.update({'data-toggle': 'tooltip'})
                    field.widget.attrs.update({'data-placement': 'right'})
                    field.widget.attrs.update({'title': field.help_text})
                    field.widget.attrs.update({'style': 'padding:0px 12px;height:40px;'})
                else:
                    field.widget.attrs['checked'] = "true"

    class Meta:
        """
        Meta Information
        """
        model = CircuitL2Report
        exclude = ['added_on', 'user_id', 'report_type', 'type_id']

    def clean_file_name(self):
        IMPORT_FILE_TYPES = ['.xls', '.xlsx', '.doc', '.docx', '.pdf', '.eml', '.msg']
        input_excel = self.cleaned_data.get('file_name')
        extension = os.path.splitext(input_excel.name)[1]
        if not (extension in IMPORT_FILE_TYPES):
            raise ValidationError(
                u'%s is not the supported file format. Please make sure your input file is in .xls, .xlsx, .doc, .docx, .pdf, .eml, .msg file format.' % extension)
        else:
            return input_excel

            # def clean_name(self):
            #     """
            #     Name unique validation
            #     """
            #     name = self.cleaned_data['name']
            #     names = CircuitL2Report.objects.filter(name=name)
            #     try:
            #         if self.id:
            #             names = names.exclude(pk=self.id)
            #     except Exception as e:
            #         logger.info(e.message)
            #     if names.count() > 0:
            #         raise ValidationError('This name is already in use.')

            #     return name


# *********************************** IconSettings ***************************************
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
        fields = "__all__"

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


# *********************************** ServiceThresholdConfiguration *****************************
class ServiceThresholdConfigurationForm(forms.ModelForm):
    """
    Class Based View  Service Threshold Configuration Model form to update and create.
    """

    def __init__(self, *args, **kwargs):

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(ServiceThresholdConfigurationForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'style': 'width:20%'})
            if name.endswith('start'):
                field.widget.attrs.update({'placeholder': 'Start'})
            else:
                field.widget.attrs.update({'placeholder': 'End'})

            field.widget.attrs.update({'class': 'form-control col-md-4'})
        self.fields['service_type'].widget.attrs.update({'style': 'width:340px'})

    class Meta:
        """
        Meta Information
        """
        model = ThresholdConfiguration
        exclude = ('name', 'alias', 'live_polling_template')


# *********************************** ServiceLivePollingSettings ********************************
class ServiceLivePollingSettingsForm(forms.ModelForm):
    """
    Class Based View ServiceLivePollingSettings Model form to update and create.
    """

    def __init__(self, *args, **kwargs):

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(ServiceLivePollingSettingsForm, self).__init__(*args, **kwargs)
        self.fields['technology'].empty_label = 'Select'
        self.fields['device_type'].empty_label = 'Select'
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
        exclude = ('name', 'alias')


# *********************************** LivePollingSettings ***************************************
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
        fields = "__all__"

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


# *********************************** LivePollingSettings ***************************************
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
        exclude = ['range1_icon', 'range2_icon', 'range3_icon', 'range4_icon', 'range5_icon', 'range6_icon',
                   'range7_icon', \
                   'range8_icon', 'range9_icon', 'range10_icon']

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


# *********************************** LivePollingSettings ***************************************
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


# *********************************** Service Thematic Settings *************************
class ServiceThematicSettingsForm(forms.ModelForm):
    """
    Class Based View Service Thematic Settings Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(ServiceThematicSettingsForm, self).__init__(*args, **kwargs)
        # self.fields['threshold_template'].empty_label = 'Select'
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
        exclude = ['icon_settings', 'user_profile', 'threshold_template']

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        thematic_name = ThematicSettings.objects.filter(name=name)
        threshold_name = ThresholdConfiguration.objects.filter(name=name)
        live_polling_name = LivePollingSettings.objects.filter(name=name)
        try:
            if self.id:
                thematic_name = thematic_name.exclude(pk=self.id)
                threshold_name = list()
                live_polling_name = list()
        except Exception as e:
            logger.info(e.message)
        if thematic_name.count() > 0 or len(threshold_name) > 0 or len(live_polling_name) > 0:
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


# *********************************** Bulk Import ***************************************
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
        ("PTP BH", "PTP BH"),
        ("Backhaul", "Backhaul")
    )
    file_upload = forms.FileField(label='Inventory Excel Sheet')
    bs_sheet = forms.ChoiceField(label='Wimax/PMP BS Sheet', choices=SHEET_CHOICES, required=False)
    ss_sheet = forms.ChoiceField(label='Wimax/PMP SS Sheet', choices=SHEET_CHOICES, required=False)
    ptp_sheet = forms.ChoiceField(label='PTP Sheet', choices=SHEET_CHOICES, required=False)
    backhaul_sheet = forms.ChoiceField(label='Backhaul Sheet', choices=SHEET_CHOICES, required=False)
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
            raise forms.ValidationError(
                u'%s is not the supported file. Please make sure your input file is an excel(.xls) file.' % extension)
        else:
            return input_excel

    def clean_description(self):
        description = self.cleaned_data['description']
        try:
            description = escape(description)
        except Exception as e:
            logger.info(e.message)
        return description


# ****************************** GIS Inventory Bulk Import Update ********************************
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
        exclude = ['status', 'uploaded_by', 'added_on', 'modified_on', 'upload_status', 'is_auto', 'is_new']


# **************************** GIS Inventory Excel Download Update ******************************
class DownloadSelectedBSInventoryEditForm(forms.ModelForm):
    """
    Class Based View GISInventoryBulkImport Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        super(DownloadSelectedBSInventoryEditForm, self).__init__(*args, **kwargs)
        self.fields['file_path'].widget.attrs['readonly'] = True
        self.fields['downloaded_by'].widget.attrs['readonly'] = True

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
        model = GISExcelDownload
        fields = ['file_path', 'downloaded_by', 'description']


# ************************************** Ping Thematic Settings **********************************
class PingThematicSettingsForm(forms.ModelForm):
    """
        Ping thematic settings form
    """
    # icon choices fetched from 'IconSettings' model
    ICON_CHOICES = [('', 'Select')]
    try:
        ICON_CHOICES = [('', 'Select')] + [(icon.upload_image.name, icon.alias) for icon in IconSettings.objects.all()]
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
        # modify type field initial option
        self.fields['type'].empty_label = 'Select'

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


# **************************************** GIS Wizard Forms ****************************************#

class WizardBaseStationForm(BaseStationForm):
    """
    Class Based View Base Station Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        super(WizardBaseStationForm, self).__init__(*args, **kwargs)
        self.fields['alias'].widget = forms.TextInput(attrs={'placeholder': 'Enter Base Station Name',
                                                             'class': ' col-md-12 form-control'})
        self.fields.pop('backhaul')

    class Meta:
        """
        Meta Information
        """
        model = BaseStation
        fields = (
        'alias', 'organization', 'backhaul', 'latitude', 'longitude', 'building_height', 'tower_height', 'country',
        'state', 'city', 'address', 'bs_site_id', 'bs_site_type', 'bs_switch', 'bs_type', 'bh_bso', 'hssu_used',
        'infra_provider', 'gps_type', 'tag1', 'tag2', 'description',
        )

    def clean(self):
        """
        Validations for base station form
        """
        latitude = self.request.POST.get('latitude') #self.cleaned_data.get('latitude')
        longitude = self.request.POST.get('longitude') #self.cleaned_data.get('longitude')
        state = self.cleaned_data.get('state')

        state_id = None
        try:
            state_id = State.objects.get(state_name=state)
        except Exception as e:
            pass

        if ('alias' not in self.cleaned_data) or (not self.cleaned_data['alias']):
            self._errors['alias'] = ErrorList(
                [u"This field is required."])
        else:
            alias = re.compile(r'[^\w]').sub("_", self.cleaned_data['alias'])
            city = self.cleaned_data['city'].city_name[:3]
            state = self.cleaned_data['state'].state_name[:3]
            name = (alias + "_" + city + "_" + state).lower()
            names = BaseStation.objects.filter(name=name)
            try:
                if self.id:
                    names = names.exclude(pk=self.id)
            except Exception as e:
                logger.info(e.message)
            if names.count() > 0:
                self._errors['alias'] = ErrorList(
                    [u"This name already in use."])

        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()

        try:
            is_lat_long_valid = nocout_utils.is_lat_long_in_state(float(latitude), float(longitude), state)
        except Exception, e:
            is_lat_long_valid = False

        if not is_lat_long_valid:
            self._errors["latitude"] = ErrorList(
                [u"Latitude, longitude specified doesn't exist within selected state."])
        # '''

        return self.cleaned_data


class WizardBackhaulForm(BackhaulForm):
    """
    Class Based View Backhaul Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        super(WizardBackhaulForm, self).__init__(*args, **kwargs)

        self.fields.pop('dr_site')

    class Meta:
        """
        Meta Information
        """
        model = Backhaul
        fields = ('organization', 'bh_configured_on', 'bh_port_name', 'bh_port', 'bh_type', 'bh_switch',
                  'switch_port_name', 'switch_port', 'pop', 'pop_port_name', 'pop_port', 'aggregator',
                  'aggregator_port_name', 'aggregator_port', 'pe_hostname', 'pe_ip', 'bh_connectivity', 'bh_circuit_id',
                  'bh_capacity', 'ttsl_circuit_id', 'dr_site',
                  )

    def clean(self):
        """
        Validations for base station form
        """
        if ('bh_configured_on' not in self.cleaned_data) or (not self.cleaned_data['bh_configured_on']):
            self._errors['alias'] = ErrorList(
                [u"This field is required."])
        else:
            name = self.cleaned_data['bh_configured_on'].ip_address
            names = Backhaul.objects.filter(name=name)
            try:
                if self.id:
                    names = names.exclude(pk=self.id)
            except Exception as e:
                logger.info(e.message)
            if names.count() > 0:
                self._errors['bh_configured_on'] = ErrorList(
                    [u"This name already in use."])
        return self.cleaned_data


class WizardSectorForm(SectorForm):
    """
    Class Based View Sector Model form to update and create.
    """

    def __init__(self, *args, **kwargs):
        self.technology = kwargs.pop('technology')
        super(WizardSectorForm, self).__init__(*args, **kwargs)

        self.fields['dr_configured_on'].widget = forms.HiddenInput()

        self.fields.pop('organization')
        self.fields.pop('base_station')
        self.fields.pop('bs_technology')
        self.fields.pop('antenna')

        if self.technology == 'P2P':
            self.fields.pop('sector_id')

        if self.technology != 'WiMAX':
            self.fields.pop('sector_configured_on_port')
            self.fields.pop('dr_site')
            self.fields.pop('mrc')
            self.fields.pop('dr_configured_on')

        if self.technology != 'PMP':
            self.fields.pop('rf_bandwidth')

    class Meta:
        """
        Meta Information
        """
        model = Sector
        fields = ('alias', 'sector_id', 'sector_configured_on', 'sector_configured_on_port', 'dr_site',
                  'dr_configured_on', 'mrc', 'tx_power', 'rx_power', 'rf_bandwidth', 'frame_length',
                  'cell_radius', 'frequency', 'modulation', 'organization', 'base_station', 'bs_technology', 'antenna',)

    def clean_sector_id(self):
        """
        Sector ID: unique validation.
        """
        sector_id = self.cleaned_data['sector_id']
        sector_ids = Sector.objects.filter(sector_id=sector_id)
        try:
            if self.id:
                sector_ids = sector_ids.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if sector_ids.count() > 0:
            raise ValidationError('This sector_id is already in use.')
        return sector_id


class WizardAntennaForm(AntennaForm):
    """
    Class Based View Antenna Model form to update and create.
    """

    ANTENNA_TYPE = (
        ('', 'Select'),
        ('Normal', 'Normal'),
        ('Narrow Beam', 'Narrow Beam'),
        ('Lens', 'Lens')
    )

    PTP_ANTENNA_TYPE = (
        ('', 'Select'),
        ('Internal', 'Internal'),
        ('External', 'External')
    )

    def __init__(self, *args, **kwargs):
        self.technology = kwargs.pop('technology')

        super(WizardAntennaForm, self).__init__(*args, **kwargs)

        # Organization is used from base station.
        self.fields.pop('organization')
        self.fields['antenna_type'] = forms.TypedChoiceField(choices=WizardAntennaForm.ANTENNA_TYPE, required=False)
        self.fields['antenna_type'].widget.attrs['class'] = 'col-md-12 select2select'

        if self.technology == 'P2P':
            self.fields['antenna_type'] = forms.TypedChoiceField(choices=WizardAntennaForm.PTP_ANTENNA_TYPE,
                                                                 required=False)
            self.fields['antenna_type'].widget.attrs['class'] = 'col-md-12 select2select'
            self.fields.pop('tilt')
            self.fields.pop('gain')
            self.fields.pop('beam_width')
            self.fields.pop('azimuth_angle')
            self.fields.pop('reflector')
            self.fields.pop('splitter_installed')
            self.fields.pop('sync_splitter_used')
            self.fields.pop('make_of_antenna')

    class Meta:
        """
        Meta Information
        """
        model = Antenna
        fields = ('organization', 'antenna_type', 'height', 'polarization', 'tilt', 'gain', 'mount_type', 'beam_width',
                  'azimuth_angle', 'reflector', 'splitter_installed', 'sync_splitter_used', 'make_of_antenna')


class RequestFormSet(forms.models.BaseModelFormSet):
    """
    Formset that passes the HttpRequest on to every Form's __init__
    Suitable to populate Fields dynamically depending on request
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.technology = kwargs.pop('technology', None)
        super(RequestFormSet, self).__init__(*args, **kwargs)  # this calls _construct_forms()

    def _construct_form(self, i, **kwargs):  # this one is merely taken from django's BaseFormSet
        # except the additional request parameter for the Form-constructor
        return super(RequestFormSet, self)._construct_form(i, technology=self.technology, request=self.request,
                                                           **kwargs)


WizardPTPSubStationAntennaFormSet = forms.models.modelformset_factory(Antenna, form=WizardAntennaForm,
                                                                      formset=RequestFormSet, max_num=1, extra=1,
                                                                      validate_max=True)


class WizardSubStationForm(SubStationForm):
    def __init__(self, *args, **kwargs):
        kwargs.pop('technology')
        super(WizardSubStationForm, self).__init__(*args, **kwargs)

        self.fields.pop('name')
        self.fields.pop('alias')
        self.fields.pop('organization')
        self.fields.pop('antenna')
        self.fields.pop('address')
        self.fields.pop('description')

    def clean(self):
        """
        Validations for base station form
        """
        latitude = self.request.POST.get('latitude') #self.cleaned_data.get('latitude')
        longitude = self.request.POST.get('longitude') #self.cleaned_data.get('longitude')
        state = self.cleaned_data.get('state')

        state_id = None
        try:
            state_id = State.objects.get(state_name=state)
        except Exception as e:
            pass

        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()

        try:
            is_lat_long_valid = nocout_utils.is_lat_long_in_state(float(latitude), float(longitude), state)
        except Exception, e:
            is_lat_long_valid = False

        if not is_lat_long_valid:
            self._errors["latitude"] = ErrorList(
                [u"Latitude, longitude specified doesn't exist within selected state."])

        # '''
        return self.cleaned_data


class WizardCustomerForm(CustomerForm):
    def __init__(self, *args, **kwargs):
        kwargs.pop('technology')
        super(WizardCustomerForm, self).__init__(*args, **kwargs)
        self.fields['alias'].widget = forms.TextInput(attrs={'placeholder': 'Enter Customer Name',
                                                             'class': ' col-md-12 form-control'})
        self.fields.pop('name')
        self.fields.pop('organization')
        self.fields.pop('description')


class WizardCircuitForm(CircuitForm):
    def __init__(self, *args, **kwargs):
        self.technology = kwargs.pop('technology')
        super(WizardCircuitForm, self).__init__(*args, **kwargs)
        self.fields['circuit_id'].required = True

        self.fields.pop('name')
        self.fields.pop('alias')
        self.fields.pop('organization')
        self.fields.pop('circuit_type')
        self.fields.pop('sector')
        self.fields.pop('customer')
        self.fields.pop('sub_station')
        self.fields.pop('date_of_acceptance')
        self.fields.pop('description')

        if self.technology == 'P2P':
            self.fields.pop('dl_cinr_during_acceptance')
            self.fields.pop('jitter_value_during_acceptance')
        else:  # WiMAX & PMP
            self.fields.pop('throughput_during_acceptance')
