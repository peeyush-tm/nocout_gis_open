from django.db import models
from device_group.models import DeviceGroup
from site_instance.models import SiteInstance
from service.models import Service
from mptt.models import MPTTModel, TreeForeignKey

# table for countries

class Country(models.Model):
    country_name = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.country_name


# table for states
class State(models.Model):
    state_name = models.CharField(max_length=200, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)

    def __unicode__(self):
        return self.state_name


# table for cities
class City(models.Model):
    city_name = models.CharField(max_length=250, null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True)

    def __unicode__(self):
        return self.city_name


# table for state latitude & longitude
class StateGeoInfo(models.Model):
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True)


# table for device frequencies color coding
class DeviceFrequency(models.Model):
    frequency_name = models.CharField(max_length=100)
    frequency_value = models.CharField(max_length=50)
    color_hex_value = models.CharField(max_length=10)

    def __unicode__(self):
        return self.frequency_name


# device types info table
class DeviceType(models.Model):
    name = models.CharField('Device Type', max_length=200, unique=True)
    alias = models.CharField('Device Description', max_length=200, null=True, blank=True)
    device_icon = models.CharField('Device GMap Icon', max_length=200, null=True, blank=True)
    device_gmap_icon = models.CharField('Device GMap Icon', max_length=200, null=True, blank=True)
    frequency = models.ManyToManyField(DeviceFrequency, null=True, blank=True)

    def __unicode__(self):
        return self.name


# device model info table
class DeviceModel(models.Model):
    name = models.CharField('Device Model', max_length=100, unique=True)
    alias = models.CharField('Alias', max_length=200)
    device_types = models.ManyToManyField(DeviceType, through="ModelType", blank=True, null=True)

    def __unicode__(self):
        return self.name


# device vendor info table
class DeviceVendor(models.Model):
    name = models.CharField('Device Vendor', max_length=100, unique=True)
    alias = models.CharField('Alias', max_length=200, null=True, blank=True)
    device_models = models.ManyToManyField(DeviceModel, through="VendorModel", blank=True, null=True)

    def __unicode__(self):
        return self.name


# device technology info table
class DeviceTechnology(models.Model):
    name = models.CharField('Device Technology', max_length=100, unique=True)
    alias = models.CharField('Alias', max_length=200, null=True, blank=True)
    device_vendors = models.ManyToManyField(DeviceVendor, through="TechnologyVendor", blank=True, null=True)

    def __unicode__(self):
        return self.name


# device info table
class Device(MPTTModel, models.Model):
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

    device_name = models.CharField('Device Name', max_length=200, unique=True)
    device_alias = models.CharField('Device Alias', max_length=200)
    site_instance = models.ForeignKey(SiteInstance, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='device_children')
    device_group = models.ManyToManyField(DeviceGroup, through='Inventory', blank=True, null=True)
    device_technology = models.IntegerField('Device Technology', null=True, blank=True)
    device_vendor = models.IntegerField('Device Vendor', null=True, blank=True)
    device_model = models.IntegerField('Device Model', null=True, blank=True)
    device_type = models.IntegerField('Device Type', null=True, blank=True)
    service = models.ManyToManyField(Service, null=True, blank=True)
    ip_address = models.IPAddressField('IP Address', unique=True)
    mac_address = models.CharField('MAC Address', max_length=100, )
    netmask = models.IPAddressField('Netmask', null=True, blank=True)
    gateway = models.IPAddressField('Gateway', null=True, blank=True)
    dhcp_state = models.CharField('DHCP State', max_length=200, choices=DHCP_STATE, default=disable)
    host_priority = models.CharField('Host Priority', max_length=200, choices=PRIORITY, default=normal)
    host_state = models.CharField('Host State', max_length=200, choices=HOST_STATE, default=enable)
    country = models.IntegerField('Country', null=True, blank=True)
    state = models.IntegerField('State', null=True, blank=True)
    city = models.IntegerField('City', null=True, blank=True)
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    timezone = models.CharField('Timezone', max_length=100, default="Asia/Kolkata")
    description = models.TextField('Description')
    address = models.TextField('Address', null=True, blank=True)
    is_deleted = models.IntegerField('Is Deleted', max_length=1, default=0)

    def __unicode__(self):
        return self.device_name


# model-type mapper
class ModelType(models.Model):
    model = models.ForeignKey(DeviceModel)
    type = models.ForeignKey(DeviceType)
    service = models.ManyToManyField(Service, blank=True, null=True)


# vendor-model mapper
class VendorModel(models.Model):
    vendor = models.ForeignKey(DeviceVendor)
    model = models.ForeignKey(DeviceModel)


# technology-vendor mapper
class TechnologyVendor(models.Model):
    technology = models.ForeignKey(DeviceTechnology)
    vendor = models.ForeignKey(DeviceVendor)


# inventory mapper table
class Inventory(models.Model):
    device = models.ForeignKey(Device)
    device_group = models.ForeignKey(DeviceGroup)


# table for extra fields of device (depends upon device type)
class DeviceTypeFields(models.Model):
    device_type = models.ForeignKey(DeviceType, null=True, blank=True)
    field_name = models.CharField(max_length=100)
    field_display_name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.field_display_name


# table for device extra fields values
class DeviceTypeFieldsValue(models.Model):
    device_type_field = models.ForeignKey(DeviceTypeFields)
    field_value = models.CharField(max_length=250)
    device_id = models.IntegerField()

