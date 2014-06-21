from django.db import models
from device.models import Device


# gis antenna model
class Antenna(models.Model):
    name = models.CharField('Antenna Name', max_length=250)
    height = models.IntegerField('Antenna Height', null=True, blank=True)
    polarization = models.CharField('Polarization', max_length=50, null=True, blank=True)
    tilt = models.IntegerField('Tilt', null=True, blank=True)
    beam_width = models.IntegerField('Beam Width', null=True, blank=True)
    azimuth_angle = models.IntegerField('Azimuth Angle', null=True, blank=True)
    splitter_installed = models.CharField('Splitter Installed', max_length=4, null=True, blank=True)
    sync_splitter_used = models.CharField('Sync Splitter User', max_length=4, null=True, blank=True)
    make_of_antenna = models.CharField('Make Of Antenna', max_length=40, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)

    def __unicode__(self):
        return self.name


# gis backhaul model
class Backhaul(models.Model):
    bh_configured_on = models.ForeignKey(Device, null=True, blank=True, related_name='backhaul')
    bh_port = models.IntegerField('BH Port', null=True, blank=True)
    bh_type = models.CharField('BH Type', max_length=250, null=True, blank=True)
    pop = models.ForeignKey(Device, null=True, blank=True, related_name='backhaul_pop')
    pop_port = models.IntegerField('Pop Port', null=True, blank=True)
    aggregator = models.ForeignKey(Device, null=True, blank=True, related_name='backhaul_aggregator')
    aggregator_port = models.IntegerField('Aggregator Port', null=True, blank=True)
    pe_hostname = models.CharField('PE Hostname', max_length=250, null=True, blank=True)
    pe_ip = models.IPAddressField('PE IP Address', null=True, blank=True)
    bh_connectivity = models.CharField('BH Connectivity', max_length=40, null=True, blank=True)
    bh_circuit_id = models.CharField('BH Circuit ID', max_length=250, null=True, blank=True)
    bh_capacity = models.IntegerField('BH Capacity', null=True, blank=True)
    ttsl_circuit_id = models.CharField('TTSL Circuit ID', max_length=250, null=True, blank=True)
    dr_site = models.CharField('DR Site', max_length=150, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)


# gis base station model
class BaseStation(models.Model):
    bs_site_id = models.CharField('BS Site ID', max_length=250, null=True, blank=True)
    bs_site_name = models.CharField('BS Site Name', max_length=250, null=True, blank=True)
    bs_switch = models.ForeignKey(Device, null=True, blank=True, related_name='bs_switch')
    backhaul = models.ForeignKey(Backhaul)
    bs_type = models.CharField('BS Type', max_length=40, null=True, blank=True)
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    infra_provider = models.CharField('Infra Provider', max_length=100, null=True, blank=True)
    building_height = models.IntegerField('Building Height', null=True, blank=True)
    tower_height = models.IntegerField('Tower Height', null=True, blank=True)
    gps_type = models.CharField('GPS Type', max_length=100, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)


# gis sector model
class Sector(models.Model):
    sector_id = models.CharField('Sector ID', max_length=250, null=True, blank=False)
    name = models.CharField('Sector Name', max_length=250)
    base_station = models.ForeignKey(BaseStation, related_name='sector')
    idu = models.ForeignKey(Device, max_length=250, null=True, blank=False, related_name='sector_idu')
    idu_port = models.IntegerField('IDU Port', null=True, blank=True)
    odu = models.ForeignKey(Device, max_length=250, null=True, blank=True, related_name='sector_odu')
    odu_port = models.IntegerField('ODU Port', null=True, blank=True)
    antenna = models.ForeignKey(Antenna, null=True, blank=True, related_name='sector')
    mrc = models.CharField('MRC', max_length=4, null=True, blank=True)
    tx_power = models.IntegerField('TX Power', null=True, blank=True)
    frequency = models.IntegerField('Frequency', null=True, blank=True)
    frame_length = models.IntegerField('Frame Length', null=True, blank=True)
    cell_radius = models.IntegerField('Cell Radius', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)


# gis customer model
class Customer(models.Model):
    name = models.CharField('Name', max_length=250)
    city = models.CharField('City', max_length=250)
    state = models.CharField('State', max_length=250)
    address = models.CharField('Address', max_length=250, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)


# gis sub-station
class SubStation(models.Model):
    ETHERNET_EXTENDER = (
        ('', 'Select....'),
        ('yes', 'Yes'),
        ('no', 'No')
    )
    name = models.CharField('Name', max_length=250)
    ip = models.IPAddressField('IP Address')
    mac = models.CharField('MAC Address', max_length=250)
    serial_no = models.CharField('Serial No.', max_length=250, null=True, blank=True)
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    building_height = models.IntegerField('Building Height', null=True, blank=True)
    tower_height = models.IntegerField('Tower Height', null=True, blank=True)
    ethernet_extender = models.CharField('Ethernet Extender', max_length=250, null=True, blank=True)
    city = models.CharField('City', max_length=250)
    state = models.CharField('State', max_length=250)
    address = models.CharField('Address', max_length=250, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)


# gis circuit model
class Circuit(models.Model):
    circuit_id = models.CharField('Circuit ID', max_length=250)
    name = models.CharField('Circuit Name', max_length=250, null=True, blank=True)
    sector = models.ForeignKey(Sector)
    customer = models.ForeignKey(Customer)
    sub_station = models.ForeignKey(SubStation)
    date_of_acceptance = models.DateTimeField('Date of Acceptance', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)