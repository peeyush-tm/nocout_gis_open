from django.db import models
from machine.models import Machine
from organization.models import Organization
from site_instance.models import SiteInstance
from service.models import Service
from mptt.models import MPTTModel


#************************************ Device Inventory**************************************
# table for countries
class Country(models.Model):
    country_name = models.CharField('Name', max_length=200)

    def __unicode__(self):
        return self.country_name


# table for states
class State(models.Model):
    state_name = models.CharField('Name', max_length=200)
    country = models.ForeignKey(Country, null=True, blank=True)

    def __unicode__(self):
        return self.state_name


# table for cities
class City(models.Model):
    city_name = models.CharField('Name', max_length=250)
    state = models.ForeignKey(State, null=True, blank=True)

    def __unicode__(self):
        return self.city_name


# table for state latitude & longitude
class StateGeoInfo(models.Model):
    state = models.ForeignKey(State)
    latitude = models.FloatField('Latitude')
    longitude = models.FloatField('Longitude')


class DeviceFrequency(models.Model):
    value = models.CharField(max_length=50, help_text="MHz")
    color_hex_value = models.CharField(max_length=100)
    frequency_radius = models.FloatField(verbose_name="Frequency Radius", default=0, help_text="Km")

    def __unicode__(self):
        return self.value


# device ports
class DevicePort(models.Model):
    name = models.CharField('Name', max_length=100, unique=True)
    alias = models.CharField('Alias', max_length=200)
    value = models.IntegerField('Port Value', default=0)

    def __unicode__(self):
        return self.name


# device types info table
class DeviceType(models.Model):
    name = models.CharField('Device Type', max_length=200, unique=True)
    alias = models.CharField('Alias', max_length=200)
    device_port = models.ManyToManyField(DevicePort, null=True, blank=True)
    service = models.ManyToManyField(Service, blank=True, null=True)
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
        Delete method: deletes the device_icon and device_gmap_icon.
        """
        self.device_icon.delete()
        self.device_gmap_icon.delete()
        super(DeviceType, self).delete(*args, **kwargs)


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
    alias = models.CharField('Alias', max_length=200)
    device_models = models.ManyToManyField(DeviceModel, through="VendorModel", blank=True, null=True)

    def __unicode__(self):
        return self.name


# device technology info table
class DeviceTechnology(models.Model):
    name = models.CharField('Device Technology', max_length=100, unique=True)
    alias = models.CharField('Alias', max_length=200)
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

    device_name = models.CharField('Name', max_length=200, unique=True)
    device_alias = models.CharField('Alias', max_length=200)
    machine = models.ForeignKey(Machine, null=True, blank=True)
    site_instance = models.ForeignKey(SiteInstance, null=True, blank=True)
    organization = models.ForeignKey(Organization)
    device_technology = models.IntegerField('Device Technology')
    device_vendor = models.IntegerField('Device Vendor')
    device_model = models.IntegerField('Device Model')
    device_type = models.IntegerField('Device Type')
    ports = models.ManyToManyField(DevicePort, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='device_children')
    ip_address = models.IPAddressField('IP Address', unique=True)
    mac_address = models.CharField('MAC Address', max_length=100, null=True, blank=True)
    netmask = models.IPAddressField('Netmask', null=True, blank=True)
    gateway = models.IPAddressField('Gateway', null=True, blank=True)
    dhcp_state = models.CharField('DHCP State', max_length=200, choices=DHCP_STATE, default=disable)
    host_priority = models.CharField('Host Priority', max_length=200, choices=PRIORITY, default=normal)
    host_state = models.CharField('Host Monitoring State', max_length=200, choices=HOST_STATE, default=enable)
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    timezone = models.CharField('Timezone', max_length=100, default="Asia/Kolkata")
    country = models.IntegerField('Country', null=True, blank=True)
    state = models.IntegerField('State', null=True, blank=True)
    city = models.IntegerField('City', null=True, blank=True)
    address = models.TextField('Address', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    is_deleted = models.IntegerField('Is Deleted', max_length=1, default=0)
    is_added_to_nms = models.IntegerField('Is Added', max_length=1, default=0)
    is_monitored_on_nms = models.IntegerField('Is Monitored', max_length=1, default=0)

    def __unicode__(self):
        return self.device_alias

    class Meta:
        ordering = ['machine']


# model-type mapper
class ModelType(models.Model):
    model = models.ForeignKey(DeviceModel)
    type = models.ForeignKey(DeviceType)


# vendor-model mapper
class VendorModel(models.Model):
    vendor = models.ForeignKey(DeviceVendor)
    model = models.ForeignKey(DeviceModel)


# technology-vendor mapper
class TechnologyVendor(models.Model):
    technology = models.ForeignKey(DeviceTechnology)
    vendor = models.ForeignKey(DeviceVendor)


# table for extra fields of device (depends upon device type)
class DeviceTypeFields(models.Model):
    field_name = models.CharField(max_length=100)
    field_display_name = models.CharField(max_length=200)
    device_type = models.ForeignKey(DeviceType)

    def __unicode__(self):
        return self.field_display_name


# table for device extra fields values
class DeviceTypeFieldsValue(models.Model):
    device_type_field = models.ForeignKey(DeviceTypeFields)
    field_value = models.CharField(max_length=250)
    device_id = models.IntegerField()
