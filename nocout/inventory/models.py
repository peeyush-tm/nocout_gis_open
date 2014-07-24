from django.db import models
from service.models import Service, ServiceDataSource
from user_group.models import UserGroup
from device.models import Device, DevicePort, DeviceTechnology, DeviceFrequency
from device_group.models import DeviceGroup
from organization.models import Organization
from django.utils.safestring import mark_safe


# inventory model --> mapper of user_group & device groups
class Inventory(models.Model):
    name = models.CharField('Name', max_length=200, unique=True)
    alias = models.CharField('Alias', max_length=250)
    organization = models.ForeignKey(Organization)
    user_group = models.ForeignKey(UserGroup)
    device_groups = models.ManyToManyField(DeviceGroup, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name


# gis antenna model
class Antenna(models.Model):
    name = models.CharField('Antenna Name', max_length=250, unique=True)
    alias = models.CharField('Antenna Alias', max_length=250)
    antenna_type = models.CharField('Antenna Type', max_length=100, null=True, blank=True)
    height = models.FloatField('Antenna Height', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(mtr)</span> Enter a number.'))
    polarization = models.CharField('Polarization', max_length=50, null=True, blank=True)
    tilt = models.FloatField('Tilt', null=True, blank=True, help_text='Enter a number.')
    gain = models.FloatField('Gain', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(dBi)</span> Enter a number.'))
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
    name = models.CharField('Backhaul Name', max_length=250, unique=True)
    alias = models.CharField('Backhaul Alias', max_length=250)
    bh_configured_on = models.ForeignKey(Device, null=True, blank=True, related_name='backhaul')
    bh_port_name = models.CharField(max_length=40, verbose_name=" BH Port Name", null=True, blank=True)
    bh_port = models.IntegerField('BH Port', null=True, blank=True)
    bh_type = models.CharField('BH Type', max_length=250, null=True, blank=True)
    bh_switch = models.ForeignKey(Device, null=True, blank=True, related_name='backhaul_switch')
    switch_port_name = models.CharField('Switch Port Name', max_length=40, null=True, blank=True)
    switch_port = models.IntegerField('Switch Port', null=True, blank=True)
    pop = models.ForeignKey(Device, null=True, blank=True, related_name='backhaul_pop')
    pop_port_name = models.CharField('POP Port Name', max_length=40, null=True, blank=True)
    pop_port = models.IntegerField('POP Port', null=True, blank=True)
    aggregator = models.ForeignKey(Device, null=True, blank=True, related_name='backhaul_aggregator')
    aggregator_port_name = models.CharField('Aggregator Port Name', max_length=40, null=True, blank=True)
    aggregator_port = models.IntegerField('Aggregator Port', null=True, blank=True)
    pe_hostname = models.CharField('PE Hostname', max_length=250, null=True, blank=True)
    pe_ip = models.IPAddressField('PE IP Address', null=True, blank=True)
    bh_connectivity = models.CharField('BH Connectivity', max_length=40, null=True, blank=True)
    bh_circuit_id = models.CharField('BH Circuit ID', max_length=250, null=True, blank=True)
    bh_capacity = models.IntegerField('BH Capacity', null=True, blank=True, help_text='Enter a number.')
    ttsl_circuit_id = models.CharField('TTSL Circuit ID', max_length=250, null=True, blank=True)
    dr_site = models.CharField('DR Site', max_length=150, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name


# gis base station model
class BaseStation(models.Model):
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    bs_technology = models.ForeignKey(DeviceTechnology, null=True, blank=True)
    bs_site_id = models.CharField('BS Site ID', max_length=250, null=True, blank=True)
    bs_site_type = models.CharField('BS Site Type', max_length=100, null=True, blank=True)
    bs_switch = models.ForeignKey(Device, null=True, blank=True, related_name='bs_switch')
    backhaul = models.ForeignKey(Backhaul)
    bs_type = models.CharField('BS Type', max_length=40, null=True, blank=True)
    bh_bso = models.CharField('BH BSO', max_length=40, null=True, blank=True)
    hssu_used = models.CharField('HSSU Used', max_length=40, null=True, blank=True)
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    infra_provider = models.CharField('Infra Provider', max_length=100, null=True, blank=True)
    building_height = models.FloatField('Building Height', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(mtr)</span> Enter a number.'))
    tower_height = models.FloatField('Tower Height', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(mtr)</span> Enter a number.'))
    country = models.IntegerField('Country', null=True, blank=True)
    state = models.IntegerField('State', null=True, blank=True)
    city = models.IntegerField('City', null=True, blank=True)
    gps_type = models.CharField('GPS Type', max_length=100, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name


# gis sector model
class Sector(models.Model):
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    sector_id = models.CharField('Sector ID', max_length=250, null=True, blank=True)
    base_station = models.ForeignKey(BaseStation, related_name='sector')
    sector_configured_on = models.ForeignKey(Device, max_length=250, null=True, blank=False, related_name='sector_configured_on')
    sector_configured_on_port = models.ForeignKey(DevicePort, null=True, blank=True)
    antenna = models.ForeignKey(Antenna, null=True, blank=True, related_name='sector')
    mrc = models.CharField('MRC', max_length=4, null=True, blank=True)
    tx_power = models.FloatField('TX Power', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(dB)</span> Enter a number.'))
    rx_power = models.FloatField('RX Field', null=True, blank=True, help_text='(dB) Enter a number.')
    rf_bandwidth = models.FloatField('RF Bandwidth', max_length=250, null=True, blank=True, help_text=mark_safe('<span class="si_unit">(kbps)</span> Enter a number.'))
    frame_length = models.FloatField('Frame Length', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(mtr)</span> Enter a number.'))
    cell_radius = models.FloatField('Cell Radius', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(mtr)</span> Enter a number.'))
    frequency = models.ForeignKey(DeviceFrequency, null=True, blank=True)
    modulation = models.CharField('Modulation', max_length=250, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name

# gis customer model
class Customer(models.Model):
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    address = models.CharField('Address', max_length=250, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name

# gis sub-station
class SubStation(models.Model):
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    device = models.ForeignKey(Device)
    antenna = models.ForeignKey(Antenna, null=True, blank=True)
    version = models.CharField('Version', max_length=40, null=True, blank=True)
    serial_no = models.CharField('Serial No.', max_length=250, null=True, blank=True)
    building_height = models.FloatField('Building Height', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(mtr)</span> Enter a number.'))
    tower_height = models.FloatField('Tower Height', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(mtr)</span> Enter a number.'))
    ethernet_extender = models.CharField('Ethernet Extender', max_length=250, null=True, blank=True)
    cable_length = models.FloatField('Cable Length', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(mtr)</span> Enter a number.'))
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    mac_address = models.CharField('MAC Address', max_length=100, null=True, blank=True)
    country = models.IntegerField('Country', null=True, blank=True)
    state = models.IntegerField('State', null=True, blank=True)
    city = models.IntegerField('City', null=True, blank=True)
    address = models.CharField('Address', max_length=250, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name

# gis circuit model
class Circuit(models.Model):
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    circuit_type = models.CharField('Type', max_length=250, null=True, blank=True)
    circuit_id = models.CharField('Circuit ID', max_length=250)
    sector = models.ForeignKey(Sector)
    customer = models.ForeignKey(Customer)
    sub_station = models.ForeignKey(SubStation)
    qos_bandwidth = models.FloatField('QOS(BW)', null=True, blank=True, help_text=mark_safe('<span class="si_unit">(kbps)</span> Enter a number.'))
    dl_rssi_during_acceptance = models.CharField('RSSI During Acceptance', max_length=100, null=True, blank=True)
    dl_cinr_during_acceptance = models.CharField('CINR During Acceptance', max_length=100, null=True, blank=True)
    jitter_value_during_acceptance = models.CharField('Jitter Value During Acceptance', max_length=100, null=True, blank=True)
    throughput_during_acceptance = models.CharField('Throughput During Acceptance', max_length=100, null=True, blank=True)
    date_of_acceptance = models.DateField('Date of Acceptance', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name


# icon settings model
class IconSettings(models.Model):
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    upload_image = models.ImageField(upload_to='icons/')

    def __unicode__(self):
        return self.name


# live polling settings model
class LivePollingSettings(models.Model):
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    technology = models.ForeignKey(DeviceTechnology)
    service = models.ForeignKey(Service)
    data_source = models.ForeignKey(ServiceDataSource)

    def __unicode__(self):
        return self.name


# threshold configuration model
class ThresholdConfiguration(models.Model):
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    live_polling_template = models.ForeignKey(LivePollingSettings)
    warning = models.CharField('Warning', max_length=20, null=True, blank=True)
    critical = models.CharField('Critical', max_length=20, null=True, blank=True)

    def __unicode__(self):
        return self.name


# thematic settings
class ThematicSettings(models.Model):
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    threshold_template = models.ForeignKey(ThresholdConfiguration)
    gt_warning = models.CharField('> Warning', max_length=200)
    bt_w_c = models.CharField('Warning > > Critical', max_length=200)
    gt_critical = models.CharField('> Critical', max_length=200)

    def __unicode__(self):
        return self.name

