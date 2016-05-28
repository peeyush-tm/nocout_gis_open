"""
Contain Gis Inventory models.

Following are basic models of this module.

- Base Station
- Backhaul
- Sector / PTP Near End
- Sub STation / PTP Far End
- Circuit
- Antenna
- Customer
- Thematic Settings
"""

import time
from datetime import datetime

from django.db import models
from django.db.models.signals import post_save, pre_save, pre_delete

from organization.models import Organization
from user_profile.models import UserProfile
from service.models import Service, ServiceDataSource
from device.models import Device, DevicePort, DeviceTechnology, DeviceFrequency, Country, State, City, DeviceType

from inventory import signals as inventory_signals


def get_default_org():
    """
    :return: organisation ID = 1
    """
    return Organization.objects.get(id=1)


# gis antenna model
class Antenna(models.Model):
    """
    Antenna Model Columns Declaration.
    """
    name = models.CharField('Antenna Name', max_length=250, unique=True)
    alias = models.CharField('Antenna Alias', max_length=250)
    organization = models.ForeignKey(Organization, default=get_default_org)
    antenna_type = models.CharField('Antenna Type', max_length=100, null=True, blank=True)
    height = models.FloatField('Antenna Height', null=True, blank=True, help_text='(mtr) Enter a number.')
    polarization = models.CharField('Polarization', max_length=50, null=True, blank=True)
    tilt = models.FloatField('Tilt', null=True, blank=True, help_text='Enter a number.')
    gain = models.FloatField('Gain', null=True, blank=True, help_text='(dBi) Enter a number.')
    mount_type = models.CharField('Mount Type', max_length=100, null=True, blank=True)
    beam_width = models.FloatField('Beam Width', null=True, blank=True, help_text='Enter a number.')
    azimuth_angle = models.FloatField('Azimuth Angle', null=True, blank=True, help_text='Enter a number.')
    reflector = models.CharField('Lens/Reflector', max_length=100, null=True, blank=True)
    splitter_installed = models.CharField('Splitter Installed', max_length=4, null=True, blank=True)
    sync_splitter_used = models.CharField('Sync Splitter User', max_length=4, null=True, blank=True)
    make_of_antenna = models.CharField('Make Of Antenna', max_length=40, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name


# gis backhaul model
class Backhaul(models.Model):
    """
    Backhaul Model Columns Declaration.
    """
    name = models.CharField('Backhaul Name', max_length=250, unique=True)
    alias = models.CharField('Backhaul Alias', max_length=250)
    organization = models.ForeignKey(Organization, default=get_default_org)
    bh_configured_on = models.ForeignKey(Device, null=True, blank=True, on_delete=models.SET_NULL, related_name='backhaul')
    bh_port_name = models.CharField(max_length=40, verbose_name=" BH Port Name", null=True, blank=True)
    bh_port = models.IntegerField('BH Port', null=True, blank=True)
    bh_type = models.CharField('BH Type', max_length=250, null=True, blank=True)
    bh_switch = models.ForeignKey(Device, null=True, blank=True, on_delete=models.SET_NULL, related_name='backhaul_switch')
    switch_port_name = models.CharField('Switch Port Name', max_length=40, null=True, blank=True)
    switch_port = models.IntegerField('Switch Port', null=True, blank=True)
    pop = models.ForeignKey(Device, null=True, blank=True, on_delete=models.SET_NULL, related_name='backhaul_pop')
    pop_port_name = models.CharField('POP Port Name', max_length=40, null=True, blank=True)
    pop_port = models.IntegerField('POP Port', null=True, blank=True)
    aggregator = models.ForeignKey(Device, null=True, blank=True, on_delete=models.SET_NULL, related_name='backhaul_aggregator')
    aggregator_port_name = models.CharField('Aggregator Port Name', max_length=40, null=True, blank=True)
    aggregator_port = models.IntegerField('Aggregator Port', null=True, blank=True)
    pe_hostname = models.CharField('PE Hostname', max_length=250, null=True, blank=True)
    pe_ip = models.GenericIPAddressField('PE IP Address', null=True, blank=True)
    bh_connectivity = models.CharField('BH Connectivity', max_length=40, null=True, blank=True)
    bh_circuit_id = models.CharField('BH Circuit ID', max_length=250, null=True, blank=True)
    bh_capacity = models.IntegerField('BH Capacity', null=True, blank=True, help_text='Enter a number.')
    ttsl_circuit_id = models.CharField('TTSL Circuit ID', max_length=250, null=True, blank=True)
    dr_site = models.CharField('DR Site', max_length=150, null=True, blank=True)
    ior_id = models.CharField('IOR ID', max_length=250, null=True, blank=True)
    bh_provider = models.CharField('BH Provider', max_length=250, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name


# gis base station model
class BaseStation(models.Model):
    """
    BaseStation Model Columns Declaration.
    """
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    organization = models.ForeignKey(Organization, default=get_default_org)
    bs_site_id = models.CharField('BS Site ID', max_length=250, null=True, blank=True)
    bs_site_type = models.CharField('BS Site Type', max_length=100, null=True, blank=True)
    bs_switch = models.ForeignKey(Device, null=True, blank=True, related_name='bs_switch')
    backhaul = models.ForeignKey(Backhaul, null=True, blank=True, on_delete=models.SET_NULL, default=None)
    bh_port_name = models.CharField(max_length=64, verbose_name=" BH Port Name", null=True, blank=True)
    bh_port = models.IntegerField('BH Port', null=True, blank=True)
    bh_capacity = models.IntegerField('BH Capacity', null=True, blank=True, help_text='Enter a number.')
    bs_type = models.CharField('BS Type', max_length=40, null=True, blank=True)
    bh_bso = models.CharField('BH BSO', max_length=40, null=True, blank=True)
    hssu_used = models.CharField('HSSU Used', max_length=40, null=True, blank=True)
    hssu_port = models.CharField('HSSU Port', max_length=40, null=True, blank=True)
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    infra_provider = models.CharField('Infra Provider', max_length=100, null=True, blank=True)
    gps_type = models.CharField('GPS Type', max_length=100, null=True, blank=True)
    building_height = models.FloatField('Building Height', null=True, blank=True, help_text='(mtr) Enter a number.')
    tower_height = models.FloatField('Tower Height', null=True, blank=True, help_text='(mtr) Enter a number.')
    country = models.ForeignKey(Country, null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True)
    address = models.TextField('Address', null=True, blank=True)
    maintenance_status = models.CharField('Maintenance Status', max_length=250, null=True, blank=True)
    provisioning_status = models.CharField('Provisioning Status', max_length=250, null=True, blank=True)
    tag1 = models.CharField('Tag 1', max_length=60, null=True, blank=True)
    tag2 = models.CharField('Tag 2', max_length=60, null=True, blank=True)
    site_ams = models.CharField('Site AMS', max_length=250, null=True, blank=True)
    site_infra_type = models.CharField('Site Infra Type', max_length=250, null=True, blank=True)
    site_sap_id = models.CharField('Site SAP ID', max_length=250, null=True, blank=True)
    mgmt_vlan = models.CharField('MGMT VLAN', max_length=250, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    # has_pps_alarm = models.BooleanField('Has PPS Alarm', default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['city', 'state']


# gis sector model
class Sector(models.Model):
    """
    Sector Model Columns Declaration.
    """
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    organization = models.ForeignKey(Organization, default=get_default_org)
    sector_id = models.CharField('Sector ID', max_length=250, null=True, blank=True)
    base_station = models.ForeignKey(BaseStation, null=True, blank=True, on_delete=models.SET_NULL, related_name='sector')
    bs_technology = models.ForeignKey(DeviceTechnology, null=True, blank=True)
    sector_configured_on = models.ForeignKey(Device, max_length=250, null=True, blank=False, on_delete=models.SET_NULL, related_name='sector_configured_on')
    sector_configured_on_port = models.ForeignKey(DevicePort, null=True, blank=True)
    antenna = models.ForeignKey(Antenna, null=True, blank=True, on_delete=models.SET_NULL, related_name='antenna')
    dr_site = models.CharField('DR Site', max_length=150, null=True, blank=True)
    dr_configured_on = models.ForeignKey(Device, max_length=250, null=True, blank=True, related_name='dr_configured_on')
    mrc = models.CharField('MRC', max_length=4, null=True, blank=True)
    tx_power = models.FloatField('TX Power', null=True, blank=True, help_text='(dB) Enter a number.')
    rx_power = models.FloatField('RX Power', null=True, blank=True, help_text='(dB) Enter a number.')
    rf_bandwidth = models.FloatField('RF Bandwidth', max_length=250, null=True, blank=True, help_text='(kbps) Enter a number.')
    frame_length = models.FloatField('Frame Length', null=True, blank=True, help_text='(mtr) Enter a number.')
    cell_radius = models.FloatField('Cell Radius', null=True, blank=True, help_text='(mtr) Enter a number.')
    frequency = models.ForeignKey(DeviceFrequency, null=True, blank=True)
    planned_frequency = models.CharField('Planned Frequency', max_length=250, null=True, blank=True)
    modulation = models.CharField('Modulation', max_length=250, null=True, blank=True)
    rfs_date = models.DateField('RFS Date', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name


# gis customer model
class Customer(models.Model):
    """
    Customer Model Columns Declaration.
    """
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    organization = models.ForeignKey(Organization, default=get_default_org)
    address = models.TextField('Address', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name


# gis sub-station
class SubStation(models.Model):
    """
    SubStation Model Columns Declaration.
    """
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    organization = models.ForeignKey(Organization, default=get_default_org)
    device = models.ForeignKey(Device, null=True, on_delete=models.SET_NULL)
    antenna = models.ForeignKey(Antenna, null=True, blank=True, on_delete=models.SET_NULL)
    version = models.CharField('Version', max_length=40, null=True, blank=True)
    serial_no = models.CharField('Serial No.', max_length=250, null=True, blank=True)
    building_height = models.FloatField('Building Height', null=True, blank=True, help_text='(mtr) Enter a number.')
    tower_height = models.FloatField('Tower Height', null=True, blank=True, help_text='(mtr) Enter a number.')
    ethernet_extender = models.CharField('Ethernet Extender', max_length=250, null=True, blank=True)
    cable_length = models.FloatField('Cable Length', null=True, blank=True, help_text='(mtr) Enter a number.')
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    mac_address = models.CharField('MAC Address', max_length=100, null=True, blank=True)
    cpe_vlan = models.CharField('CPE VLAN', max_length=250, null=True, blank=True)
    sacfa_no = models.CharField('SACFA No.', max_length=250, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True)
    address = models.TextField('Address', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name


# gis circuit model
class Circuit(models.Model):
    """
    Circuit Model Columns Declaration.
    """
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    organization = models.ForeignKey(Organization, default=get_default_org)
    circuit_type = models.CharField('Type', max_length=250, null=True, blank=True)
    circuit_id = models.CharField('Circuit ID', max_length=250, null=True, blank=True)
    sector = models.ForeignKey(Sector, null=True, blank=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    sub_station = models.ForeignKey(SubStation, null=True, blank=True, on_delete=models.SET_NULL)
    qos_bandwidth = models.FloatField('QOS(BW)', null=True, blank=True, help_text='(kbps) Enter a number.')
    sold_cir = models.FloatField('Customer Sold CIR', null=True, blank=True, help_text='(mbps) Enter a number.')
    dl_rssi_during_acceptance = models.CharField('RSSI During Acceptance', max_length=100, null=True, blank=True)
    dl_cinr_during_acceptance = models.CharField('CINR During Acceptance', max_length=100, null=True, blank=True)
    jitter_value_during_acceptance = models.CharField('Jitter Value During Acceptance', max_length=100, null=True, blank=True)
    throughput_during_acceptance = models.CharField('Throughput During Acceptance', max_length=100, null=True, blank=True)
    date_of_acceptance = models.DateField('Date of Acceptance', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name

# Circuit id and phone number mapper model
class CircuitContacts(models.Model):
    """
    CircuitContacts table's Columns Declaration.
    """ 
    phone_number = models.CharField('Phone No.', max_length=15, null=True, blank=True)
    circuit = models.ForeignKey(Circuit, null=True, blank=True)

# Model for getting message related to particular circuit id
class PowerSignals(models.Model):
    """
    PowerSignals Model Columns Declaration.
    """
    # SIGNAL_TYPE_CHOICES = (
    #     ('RECEIVED', 'Received'),
    #     ('SENT', 'Sent'),
    # )

    circuit_contacts = models.ForeignKey(CircuitContacts, max_length=250, null=True, blank=True)
    message = models.CharField('Message', max_length=512, null=True, blank=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    signal_type = models.CharField('Signal Type', max_length=32, null=True, blank=True, default='Received')

# function to modify name and path of uploaded file
def uploaded_file_name(instance, filename):
    timestamp = time.time()
    full_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S')
    year_month_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    # modified filename
    filename = "{}_{}".format(full_time, filename)

    # modified path where file is uploaded
    path = "uploaded/icons"

    return '{}/{}/{}'.format(path, year_month_date, filename)


# icon settings model
class IconSettings(models.Model):
    """
    IconSettings Model Columns Declaration.
    """

    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    upload_image = models.ImageField(upload_to=uploaded_file_name)

    def __unicode__(self):
        return self.alias

    def delete(self, *args, **kwargs):
        """
        Delete method: deletes the upload image.
        """
        self.upload_image.delete()
        super(IconSettings, self).delete(*args, **kwargs)


# live polling settings model
class LivePollingSettings(models.Model):
    """
    LivePollingSettings Model Columns Declaration.
    """
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    technology = models.ForeignKey(DeviceTechnology)
    device_type = models.ForeignKey(DeviceType, null=True)
    service = models.ForeignKey(Service)
    data_source = models.ForeignKey(ServiceDataSource)

    def __unicode__(self):
        return self.alias


# threshold configuration model
class ThresholdConfiguration(models.Model):
    """
    ThresholdConfiguration Model Columns Declaration.
    """
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    service_type = models.CharField('Service Type', max_length=3, default='INT', choices=(('INT', 'Numeric'), ('STR', 'String')))
    live_polling_template = models.ForeignKey(LivePollingSettings)

    range1_start = models.CharField('Range1 Start', max_length=20, null=True, blank=True)
    range1_end = models.CharField('Range1 End', max_length=20, null=True, blank=True)

    range2_start = models.CharField('Range2 Start', max_length=20, null=True, blank=True)
    range2_end = models.CharField('Range2 End', max_length=20, null=True, blank=True)

    range3_start = models.CharField('Range3 Start', max_length=20, null=True, blank=True)
    range3_end = models.CharField('Range3 End', max_length=20, null=True, blank=True)

    range4_start = models.CharField('Range4 Start', max_length=20, null=True, blank=True)
    range4_end = models.CharField('Range4 End', max_length=20, null=True, blank=True)

    range5_start = models.CharField('Range5 Start', max_length=20, null=True, blank=True)
    range5_end = models.CharField('Range5 End', max_length=20, null=True, blank=True)

    range6_start = models.CharField('Range6 Start', max_length=20, null=True, blank=True)
    range6_end = models.CharField('Range6 End', max_length=20, null=True, blank=True)

    range7_start = models.CharField('Range7 Start', max_length=20, null=True, blank=True)
    range7_end = models.CharField('Range7 End', max_length=20, null=True, blank=True)

    range8_start = models.CharField('Range8 Start', max_length=20, null=True, blank=True)
    range8_end = models.CharField('Range8 End', max_length=20, null=True, blank=True)

    range9_start = models.CharField('Range9 Start', max_length=20, null=True, blank=True)
    range9_end = models.CharField('Range9 End', max_length=20, null=True, blank=True)

    range10_start = models.CharField('Range10 Start', max_length=20, null=True, blank=True)
    range10_end = models.CharField('Range10 End', max_length=20, null=True, blank=True)

    def __unicode__(self):
        return self.alias


# thematic settings
class ThematicSettings(models.Model):
    """
    ThematicSettings Model Columns Declaration.
    """

    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    threshold_template = models.ForeignKey(ThresholdConfiguration)
    icon_settings =models.TextField(default='NULL')
    user_profile = models.ManyToManyField(UserProfile, through="UserThematicSettings")
    is_global = models.BooleanField('Global Setting',default=False)

    def __unicode__(self):
        return self.name


#user Profile based thematic settings
class UserThematicSettings(models.Model):
    """
    user based thematic settings
    """
    user_profile = models.ForeignKey(UserProfile)
    thematic_template = models.ForeignKey(ThematicSettings)
    thematic_technology = models.ForeignKey(DeviceTechnology, null=True)
    thematic_type = models.ForeignKey(DeviceType, null=True)

class GISInventoryBulkImport(models.Model):
    original_filename = models.CharField('Inventory', max_length=250, null=True, blank=True)
    valid_filename = models.CharField('Valid', max_length=250, null=True, blank=True)
    invalid_filename = models.CharField('Invalid', max_length=250, null=True, blank=True)
    status = models.IntegerField('Status', null=True, blank=True)
    sheet_name = models.CharField('Sheet Name', max_length=100, null=True, blank=True)
    technology = models.CharField('Technology', max_length=40, null=True, blank=True)
    upload_status = models.IntegerField('Upload Status', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    uploaded_by = models.CharField('Uploaded By', max_length=100, null=True, blank=True)
    added_on = models.DateTimeField('Added On', null=True, blank=True)
    modified_on = models.DateTimeField('Modified On', null=True, blank=True)
    is_auto = models.IntegerField('Is Auto', null=True, blank=True)
    is_new = models.IntegerField('Is New', null=True, blank=True)

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.added_on = datetime.now()
        self.modified_on = datetime.now()
        return super(GISInventoryBulkImport, self).save(*args, **kwargs)

    def __unicode__(self):
        """
        Device Ping Configuration object presentation
        """
        return self.original_filename



# function to modify name and path of uploaded file
def uploaded_report_name(instance, filename):
    timestamp = time.time()
    year_month_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    filename = instance.file_name
    if instance.report_type == 'base_station':
        prefixreportname = BaseStation.objects.filter(id=instance.type_id).values('state__state_name', 'city__city_name')
        filename = "{0}-{1}_{2}".format(prefixreportname[0]['state__state_name'], prefixreportname[0]['city__city_name'], instance.file_name)

    # modified path where file is uploaded
    path = "uploaded/l2"

    return '{}/{}/{}'.format(path, year_month_date, filename)


# *********** L2 Reports Model *******************
class CircuitL2Report(models.Model):

    name = models.CharField('Name', max_length=250, unique=False)
    file_name = models.FileField(max_length=512, upload_to=uploaded_report_name)
    added_on = models.DateTimeField('Added On', null=True, blank=True, auto_now_add=True)
    user_id = models.ForeignKey(UserProfile)
    type_id = models.IntegerField('Type ID')
    is_public = models.BooleanField('Is Public', default=True)
    report_type = models.CharField('Type', max_length=15)


class PingThematicSettings(models.Model):
    """
        ThematicSettings Model Columns Declaration.
    """
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)

    technology = models.ForeignKey(DeviceTechnology)
    type = models.ForeignKey(DeviceType,null=True)
    service = models.CharField('Service', max_length=250)
    data_source = models.CharField('Data Source', max_length=250)

    range1_start = models.CharField('Range1 Start', max_length=20, null=True, blank=True)
    range1_end = models.CharField('Range1 End', max_length=20, null=True, blank=True)

    range2_start = models.CharField('Range2 Start', max_length=20, null=True, blank=True)
    range2_end = models.CharField('Range2 End', max_length=20, null=True, blank=True)

    range3_start = models.CharField('Range3 Start', max_length=20, null=True, blank=True)
    range3_end = models.CharField('Range3 End', max_length=20, null=True, blank=True)

    range4_start = models.CharField('Range4 Start', max_length=20, null=True, blank=True)
    range4_end = models.CharField('Range4 End', max_length=20, null=True, blank=True)

    range5_start = models.CharField('Range5 Start', max_length=20, null=True, blank=True)
    range5_end = models.CharField('Range5 End', max_length=20, null=True, blank=True)

    range6_start = models.CharField('Range6 Start', max_length=20, null=True, blank=True)
    range6_end = models.CharField('Range6 End', max_length=20, null=True, blank=True)

    range7_start = models.CharField('Range7 Start', max_length=20, null=True, blank=True)
    range7_end = models.CharField('Range7 End', max_length=20, null=True, blank=True)

    range8_start = models.CharField('Range8 Start', max_length=20, null=True, blank=True)
    range8_end = models.CharField('Range8 End', max_length=20, null=True, blank=True)

    range9_start = models.CharField('Range9 Start', max_length=20, null=True, blank=True)
    range9_end = models.CharField('Range9 End', max_length=20, null=True, blank=True)

    range10_start = models.CharField('Range10 Start', max_length=20, null=True, blank=True)
    range10_end = models.CharField('Range10 End', max_length=20, null=True, blank=True)

    icon_settings = models.TextField(default='NULL')
    user_profile = models.ManyToManyField(UserProfile, through="UserPingThematicSettings")
    is_global = models.BooleanField('Global Setting', default=False)

    def __unicode__(self):
        return self.name


class UserPingThematicSettings(models.Model):
    """
    User PING thematic settings
    """
    user_profile = models.ForeignKey(UserProfile)
    thematic_template = models.ForeignKey(PingThematicSettings)
    thematic_technology = models.ForeignKey(DeviceTechnology, null=True)
    thematic_type = models.ForeignKey(DeviceType, null=True)


class GISExcelDownload(models.Model):
    file_path = models.CharField('Inventory File', max_length=250, null=True, blank=True)
    status = models.IntegerField('Status', null=True, blank=True)
    base_stations = models.CharField('Base Stations', max_length=250, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    downloaded_by = models.CharField('Downloaded By', max_length=100, null=True, blank=True)
    added_on = models.DateTimeField('Added On', null=True, blank=True)
    modified_on = models.DateTimeField('Modified On', null=True, blank=True)

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.added_on = datetime.now()
        self.modified_on = datetime.now()
        return super(GISExcelDownload, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.file_path) or u''

class BaseStationPpsMapper(models.Model):
    """
    This model works as a mapper between Base Stations and their
    PPS Alarms.
    """
    base_station = models.ForeignKey(BaseStation)
    has_pps_alarm = models.BooleanField(default=False)
    latest_timestamp = models.DateTimeField(auto_now=True)

# ********************* Connect Inventory Signals *******************
pre_save.connect(inventory_signals.update_site_on_bs_bhport_change, sender=BaseStation)
post_save.connect(inventory_signals.auto_assign_thematic, sender=UserProfile)
pre_save.connect(inventory_signals.resize_icon_size, sender=IconSettings)
pre_delete.connect(inventory_signals.delete_antenna_of_sector, sender=Sector)
pre_delete.connect(inventory_signals.delete_antenna_of_substation, sender=SubStation)
pre_delete.connect(inventory_signals.delete_customer_of_circuit, sender=Circuit)
