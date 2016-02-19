"""
=======================================================================
Module contains database models and functions specific to 'device' app.
=======================================================================

Location:
* /nocout_gis/nocout/user_profile/models.py

List of constructs:
=======
Classes
=======
* Country
* State
* City
* StateGeoInfo
* DeviceFrequency
* DevicePort
* DeviceType
* DeviceTypeService
* DeviceTypeServiceDataSource
* DeviceModel
* DeviceVendor
* DeviceTechnology
* Device
* ModelType
* VendorModel
* TechnologyVendor
* DeviceTypeFields
* DeviceTypeFieldsValue
* DeviceSyncHistory

=======
Signals
=======
* Set site instance 'is_device_change' bit on device modification or creation.
* Set site instance 'is_device_change' bit on device type modification.
* Set site instance 'is_device_change' bit on device type service modification or creation.
* Set site instance 'is_device_change' bit on device type service deletion.
* If a new device type service is created auto assign default data source of service to it.
"""

from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from machine.models import Machine
from organization.models import Organization
from site_instance.models import SiteInstance
from service.models import Service, ServiceParameters, ServiceDataSource
from mptt.models import MPTTModel
from datetime import datetime
from device import signals as device_signals


class Country(models.Model):
    """
    Model for storing country instances.
    """
    country_name = models.CharField('Name', max_length=200)

    def __unicode__(self):
        return self.country_name


class State(models.Model):
    """
    Model for storing state instances.
    """
    state_name = models.CharField('Name', max_length=200)
    country = models.ForeignKey(Country, null=True, blank=True)

    def __unicode__(self):
        return self.state_name


class City(models.Model):
    """
    Model for storing city instances.
    """
    city_name = models.CharField('Name', max_length=250)
    state = models.ForeignKey(State, null=True, blank=True)

    def __unicode__(self):
        return self.city_name


class StateGeoInfo(models.Model):
    """
    Model for storing states boundary latitudes and longitudes.
    """
    state = models.ForeignKey(State)
    latitude = models.FloatField('Latitude')
    longitude = models.FloatField('Longitude')


class DeviceFrequency(models.Model):
    """
    Model for storing device frequency instances.
    """
    value = models.CharField(max_length=50, help_text="MHz")
    color_hex_value = models.CharField(max_length=100)
    frequency_radius = models.FloatField(verbose_name="Frequency Radius", default=0, help_text="Km")

    def __unicode__(self):
        return self.value


class DevicePort(models.Model):
    """
    Model for storing device port instances.
    """
    name = models.CharField('Name', max_length=100, unique=True)
    alias = models.CharField('Alias', max_length=200)
    value = models.IntegerField('Port Value', default=0)

    def __unicode__(self):
        return self.name


class DeviceType(models.Model):
    """
    Model for storing device type instances.
    """
    name = models.CharField('Device Type', max_length=200, unique=True)
    alias = models.CharField('Alias', max_length=200)
    device_port = models.ManyToManyField(DevicePort, blank=True)
    service = models.ManyToManyField(Service, through="DeviceTypeService", blank=True)
    packets = models.IntegerField('Packets', blank=True, null=True)
    timeout = models.IntegerField('Timeout', blank=True, null=True)
    normal_check_interval = models.IntegerField('Normal Check Interval', blank=True, null=True)
    rta_warning = models.IntegerField('RTA Warning', blank=True, null=True)
    rta_critical = models.IntegerField('RTA Critical', blank=True, null=True)
    pl_warning = models.IntegerField('PL Warning', blank=True, null=True)
    pl_critical = models.IntegerField('PL Critical', blank=True, null=True)
    agent_tag = models.CharField('Agent Tag', max_length=200, null=True, blank=True)
    device_icon = models.ImageField(upload_to='uploaded/icons/%Y/%m/%d')
    device_gmap_icon = models.ImageField(upload_to='uploaded/icons/%Y/%m/%d')

    def __unicode__(self):
        return self.name

    def delete(self, *args, **kwargs):
        """
        Deletes the 'device_icon' and 'device_gmap_icon'.
        """
        self.device_icon.delete()
        self.device_gmap_icon.delete()
        super(DeviceType, self).delete(*args, **kwargs)


class DeviceTypeService(models.Model):
    """
    Model for storing services and data sources corresponding to the device type.
    """
    device_type = models.ForeignKey(DeviceType)
    service = models.ForeignKey(Service)
    parameter = models.ForeignKey(ServiceParameters)
    service_data_sources = models.ManyToManyField(ServiceDataSource, through="DeviceTypeServiceDataSource")


class DeviceTypeServiceDataSource(models.Model):
    """
    M2M mapper model for mapping data sources with specific service in device type model.
    Mapping: DeviceTypeService (1:M) ServiceDataSource
    """
    device_type_service = models.ForeignKey(DeviceTypeService)
    service_data_sources = models.ForeignKey(ServiceDataSource)
    warning = models.CharField('Warning', max_length=255, null=True, blank=True)
    critical = models.CharField('Critical', max_length=255, null=True, blank=True)


class DeviceModel(models.Model):
    """
    Model for storing device model instances.
    """
    name = models.CharField('Device Model', max_length=100, unique=True)
    alias = models.CharField('Alias', max_length=200)
    device_types = models.ManyToManyField(DeviceType, through="ModelType", blank=True)

    def __unicode__(self):
        return self.name


class DeviceVendor(models.Model):
    """
    Model for storing device vendor instances.
    """
    name = models.CharField('Device Vendor', max_length=100, unique=True)
    alias = models.CharField('Alias', max_length=200)
    device_models = models.ManyToManyField(DeviceModel, through="VendorModel", blank=True)

    def __unicode__(self):
        return self.name


class DeviceTechnology(models.Model):
    """
    Model for storing device technology instances.
    """
    name = models.CharField('Device Technology', max_length=100, unique=True)
    alias = models.CharField('Alias', max_length=200)
    device_vendors = models.ManyToManyField(DeviceVendor, through="TechnologyVendor", blank=True)

    def __unicode__(self):
        return self.name


class Device(MPTTModel, models.Model):
    """
    Model for storing device instances.
    """
    enable = 'Enable'
    disable = 'Disable'
    high = 'High'
    normal = 'Normal'
    low = 'Low'

    DHCP_STATE = (
        (enable, 'Enable'),
        (disable, 'Disable'),
    )
    HOST_STATE = (
        (enable, 'Enable'),
        (disable, 'Disable'),
    )
    PRIORITY = (
        (high, 'High'),
        (normal, 'Normal'),
        (low, 'Low')
    )

    device_alias_help_text = '''
        <ul><li>PTP <ul><li>Near End : Circuit ID_NE</li>
        <li>Far End : Circuit ID</li></ul>
        </li><li>PMP<ul><li>ODU : AP IP_Color Code { Eg: AP IP
        = 10.11.12.13 Color Code=11  =>  Sector ID - 10111213_11}</li>
        <li>SM : Circuit ID</li></ul></li><li>WiMAX<ul><li>IDU : Sector
        ID of PMP1 or PMP2</li><li>IDU DR : Sector ID of PMP1 or
        PMP2</li><li>SS : Circuit ID</li></ul></li>
        <li>Converter : IP</li><li>Switch : IP</li></ul>
    '''

    device_name = models.CharField('Name', max_length=200, unique=True)
    device_alias = models.CharField('Alias', max_length=200, help_text=device_alias_help_text)
    machine = models.ForeignKey(Machine, null=True, blank=True)
    site_instance = models.ForeignKey(SiteInstance, null=True, blank=True)
    organization = models.ForeignKey(Organization)
    device_technology = models.IntegerField('Device Technology')
    device_vendor = models.IntegerField('Device Vendor')
    device_model = models.IntegerField('Device Model')
    device_type = models.IntegerField('Device Type')
    ports = models.ManyToManyField(DevicePort, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='device_children')
    parent_type = models.CharField('Parent Type', null=True, blank=True, max_length=200)
    parent_port = models.CharField('Parent Port', null=True, blank=True, max_length=200)
    ip_address = models.GenericIPAddressField('IP Address', unique=True)
    mac_address = models.CharField('MAC Address', max_length=100, null=True, blank=True)
    netmask = models.GenericIPAddressField(null=True, blank=True)
    gateway = models.GenericIPAddressField('Gateway', null=True, blank=True)
    dhcp_state = models.CharField('DHCP State', max_length=200, choices=DHCP_STATE, default=disable)
    host_priority = models.CharField('Host Priority', max_length=200, choices=PRIORITY, default=normal)
    host_state = models.CharField('Host Monitoring State', max_length=200, choices=HOST_STATE, default=enable)
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    timezone = models.CharField('Timezone', max_length=100, default="Asia/Kolkata")
    country = models.ForeignKey(Country, null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True)
    address = models.TextField('Address', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    is_deleted = models.IntegerField('Is Deleted', default=0)
    is_added_to_nms = models.IntegerField('Is Added', default=0)
    is_monitored_on_nms = models.IntegerField('Is Monitored', default=0)

    class Meta:
        ordering = ['machine']

    def __unicode__(self):
        return self.device_alias


class ModelType(models.Model):
    """
    M2M mapper model for mapping device model with device types.
    Mapping: DeviceModel (1:M) DeviceType
    """
    model = models.ForeignKey(DeviceModel)
    type = models.ForeignKey(DeviceType)


class VendorModel(models.Model):
    """
    M2M mapper model for mapping device vendor with device models.
    Mapping: DeviceVendor (1:M) DeviceModel
    """
    vendor = models.ForeignKey(DeviceVendor)
    model = models.ForeignKey(DeviceModel)


class TechnologyVendor(models.Model):
    """
    M2M mapper model for mapping device technology with device vendors.
    Mapping: DeviceTechnology (1:M) DeviceVendor
    """
    technology = models.ForeignKey(DeviceTechnology)
    vendor = models.ForeignKey(DeviceVendor)


class DeviceTypeFields(models.Model):
    """
    Model for associating extra fields with the specific device type.
    """
    field_name = models.CharField(max_length=100)
    field_display_name = models.CharField(max_length=200)
    device_type = models.ForeignKey(DeviceType)

    def __unicode__(self):
        return self.field_display_name


class DeviceTypeFieldsValue(models.Model):
    """
    Model for storing extra fields values corresponding to the device.
    """
    device_type_field = models.ForeignKey(DeviceTypeFields)
    field_value = models.CharField(max_length=250)
    device_id = models.IntegerField()


class DeviceSyncHistory(models.Model):
    """
    Model for storing device sync information/status.
    """
    status = models.IntegerField('Status', null=True, blank=True)
    message = models.TextField('NMS Message', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    sync_by = models.CharField('Sync By', max_length=100, null=True, blank=True)
    added_on = models.DateTimeField('Applied On', null=True, blank=True)
    completed_on = models.DateTimeField('Completed On', null=True, blank=True)

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.added_on = datetime.now()
        return super(DeviceSyncHistory, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.status


# ********************************** DEVICE SIGNALS ***********************************

# Set site instance 'is_device_change' bit on device modification or creation.
pre_save.connect(device_signals.update_site_on_device_change, sender=Device)

# Set site instance 'is_device_change' bit on device type modification.
pre_save.connect(device_signals.update_site_on_devicetype_change, sender=DeviceType)

# Set site instance 'is_device_change' bit on device type service modification or creation.
post_save.connect(device_signals.update_site_on_service_change, sender=DeviceTypeService)

# Set site instance 'is_device_change' bit on device type service deletion.
post_delete.connect(device_signals.update_site_on_service_change, sender=DeviceTypeService)

# If a new device type service is created auto assign default data source of service to it.
post_save.connect(device_signals.update_device_type_service, sender=DeviceTypeService)

