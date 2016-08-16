from django.db import models

from inventory.models import Sector
from device.models import Device, DeviceTechnology
from user_profile.models import UserProfile
from machine.models import Machine
from site_instance.models import SiteInstance
from service.models import ServiceDataSource,Service


##################################################################
############ One Table To Rule them all Performance##############
##################################################################


class PerformanceMetric(models.Model):
    """
    Performance Metric Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


##################################################################
############ One Table To Rule them all Performance##############
##################################################################

#==============================================================================================================#

##################################################################
############  Network Performance : Per 5 minutes   ##############
##################################################################


class PerformanceNetwork(models.Model):
    """
    Performance Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


### Every 30 Minutes

class PerformanceNetworkBiHourly(models.Model):
    """
    Performance Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


### Hourly Tables

class PerformanceNetworkHourly(models.Model):
    """
    Performance Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


### Daily Tables

class PerformanceNetworkDaily(models.Model):
    """
    Performance Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


### Weekly Tables

class PerformanceNetworkWeekly(models.Model):
    """
    Performance Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


##Monthly Tables

class PerformanceNetworkMonthly(models.Model):
    """
    Performance Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


### Yearly Tables

class PerformanceNetworkYearly(models.Model):
    """
    Performance Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

##################################################################
############  Network Performance : Per 5 minutes   ##############
##################################################################

#==============================================================================================================#

##################################################################
###########  Services Performance : Per 5 minutes   ##############
##################################################################


class PerformanceService(models.Model):
    """
    Performance Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Bi Hourly : twice in one hour

class PerformanceServiceBiHourly(models.Model):
    """
    Performance Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Hourly

class PerformanceServiceHourly(models.Model):
    """
    Performance Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


### Daily

class PerformanceServiceDaily(models.Model):
    """
    Performance Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Weekly

class PerformanceServiceWeekly(models.Model):
    """
    Performance Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Monthly

class PerformanceServiceMonthly(models.Model):
    """
    Performance Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Yearly

class PerformanceServiceYearly(models.Model):
    """
    Performance Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

##################################################################
###########  Services Performance : Per 5 minutes   ##############
##################################################################

#==============================================================================================================#

##################################################################
########### Status Services Performance : HOURLY    ##############
##################################################################


#### Status Services : On Live : Hourly

class PerformanceStatus(models.Model):
    """
    Performance Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


### Daily

class PerformanceStatusDaily(models.Model):
    """
    Performance Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Weekly update of status tables

class PerformanceStatusWeekly(models.Model):
    """
    Performance Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Monthly update of status tables

class PerformanceStatusMonthly(models.Model):
    """
    Performance Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Yearly update of status tables

class PerformanceStatusYearly(models.Model):
    """
    Performance Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

##################################################################
########### Status Services Performance : HOURLY    ##############
##################################################################

#==============================================================================================================#

##################################################################
########### Machine Service Performance : Once Daily##############
##################################################################

class PerformanceMachine(models.Model):
    """
    Performance Machine Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

##################################################################
########### Machine Service Performance : Once Daily##############
##################################################################


#==============================================================================================================#

##################################################################
########### Inventory Service Performance : Once Daily############
##################################################################


class PerformanceInventory(models.Model):
    """
    Performance Inventory Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Inventory Service Performance : Once Daily

class PerformanceInventoryDaily(models.Model):
    """
    Performance Inventory Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class PerformanceInventoryWeekly(models.Model):
    """
    Performance Inventory Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class PerformanceInventoryMonthly(models.Model):
    """
    Performance Inventory Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class PerformanceInventoryYearly(models.Model):
    """
    Performance Inventory Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

##################################################################
########### Inventory Service Performance : Once Daily###########
##################################################################


#==============================================================================================================#

########################HIGH PRIORITY#############################
##################################################################
########################EVENTS TABLES#############################
##################################################################
# events tables
class EventNetwork(models.Model):
    """
    Event Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class EventNetworkDaily(models.Model):
    """
    Event Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class EventNetworkWeekly(models.Model):
    """
    Event Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class EventNetworkMonthly(models.Model):
    """
    Event Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class EventNetworkYearly(models.Model):
    """
    Event Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']



########################HIGH PRIORITY#############################
##################################################################
########################EVENTS TABLES#############################
##################################################################

########################HIGH PRIORITY#############################
##################################################################
########################EVENTS TABLES#############################
##################################################################

class EventService(models.Model):
    """
    Event Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class EventServiceDaily(models.Model):
    """
    Event Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class EventServiceWeekly(models.Model):
    """
    Event Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class EventServiceYearly(models.Model):
    """
    Event Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

########################HIGH PRIORITY#############################
##################################################################
########################EVENTS TABLES#############################
##################################################################


##################################################################
########################EVENTS TABLES#############################
##################################################################
########################LOW PRIORITY#############################

class EventStatus(models.Model):
    """
    Event Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class EventMachine(models.Model):
    """
    Event Machine Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class EventInventory(models.Model):
    """
    Event Inventory Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

######################## LOW PRIORITY#############################
##################################################################
########################EVENTS TABLES#############################
##################################################################

#==============================================================================================================#

##################################################################
##################EVENT STATUS TABLES#############################
##################################################################
########################HIGH PRIORITY#############################


class EventNetworkStatus(models.Model):
    """
    Event Network Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True, db_index=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
       # ordering = ['-sys_timestamp']
        index_together = [
            ["device_name", "service_name", "data_source"],
        ]


class EventServiceStatus(models.Model):
    """
    Event Service Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True, db_index=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
       # ordering = ['-sys_timestamp']
        index_together = [
            ["device_name", "service_name", "data_source"],
        ]


class EventStatusStatus(models.Model):
    """
    Event Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    #class Meta:
    #    ordering = ['-sys_timestamp']


class EventMachineStatus(models.Model):
    """
    Event Machine Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    #class Meta:
    #    ordering = ['-sys_timestamp']


class EventInventoryStatus(models.Model):
    """
    Event Inventory Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    #class Meta:
    #    ordering = ['-sys_timestamp']


########################HIGH PRIORITY#############################
##################################################################
##################EVENT STATUS TABLES#############################
##################################################################

#==============================================================================================================#

##################################################################
############PERFORMANCE STATUS TABLES#############################
##################################################################


class NetworkStatus(models.Model):
    """
    Network Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        # ordering = ['-sys_timestamp']
        # index_together = [
        #     ["device_name", "service_name", "data_source"],
        # ]
        unique_together = (
            ("device_name", "service_name", "data_source")
        )


class ServiceStatus(models.Model):
    """
    Service Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        # ordering = ['-sys_timestamp']
        unique_together = (
            ("device_name", "service_name", "data_source")
        )


class MachineStatus(models.Model):
    """
    Machine Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        #ordering = ['-sys_timestamp']
        unique_together = (
            ("device_name", "service_name", "data_source")
        )


class InventoryStatus(models.Model):
    """
    Inventory Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        # ordering = ['-sys_timestamp']
        unique_together = (
            ("device_name", "service_name", "data_source")
        )


class Status(models.Model):
    """
    Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        # ordering = ['-sys_timestamp']
        unique_together = (
            ("device_name", "service_name", "data_source")
        )

##################################################################
############PERFORMANCE STATUS TABLES#############################
##################################################################

#==============================================================================================================#

##################################################################
##################################################################
##############################Network Availability################
##################################################################
##################################################################


class NetworkAvailabilityDaily(models.Model):
    """
    Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class NetworkAvailabilityWeekly(models.Model):
    """
    Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class NetworkAvailabilityMonthly(models.Model):
    """
    Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class NetworkAvailabilityYearly(models.Model):
    """
    Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#==============================================================================================================#

#####################################################################
#####################################################################
#####################Network Topology################################
#####################################################################
#####################################################################


class Topology(models.Model):
    """
    Status Table columns declared
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    mac_address = models.CharField('MAC Address', max_length=20, null=True, db_index=True, blank=True)
    sector_id = models.CharField('Sector Id', max_length=32, null=True, db_index=True, blank=True)
    connected_device_ip = models.CharField('Connected Device IP Address', max_length=20, null=True, db_index=True,
                                           blank=True)
    connected_device_mac = models.CharField('Connected Device MAC Address', max_length=20, null=True, db_index=True,
                                            blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return "Sector : {0} | Device {1} | IP {2}".format(self.sector_id,
                                                           self.device_name,
                                                           self.ip_address
        )

    # class Meta:
    #     ordering = ['-sys_timestamp']


#==============================================================================================================#

#####################################################################
#####################################################################
##################### Sector//Backhaul Utilization ##################
#####################################################################
#####################################################################

## Creating Separate Tables because these are KPI reports
## which does not instantly affect the system
## but are pre calculated based on various fields
## and formulas defined by any user
## TODO: create a separate app for holding this
## that would ensure easy removal
## we will user "refer" varaible as SECTOR ID in case of PMP and WiMAX
## we will use "refer variable as PORT Number in case of BAckhaul

class Utilization(models.Model):
    """
    Sector Utilization model for calculating the sector Utilization per sector
    It keeps the current Value for the Sector Utilization Status.
    Per device, per sector, per port
    Age here will be calculated of the STATUS AGE while NORMAL, MAJOR, CRITICAL
    """
    device_name = models.CharField('Device Name', max_length=100, db_index=True, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, db_index=True, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, db_index=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class UtilizationBiHourly(models.Model):
    """
    Sector Utilization model for calculating the sector Utilization per sector
    It keeps the current Value for the Sector Utilization Status.
    Per device, per sector, per port
    Age here will be calculated of the STATUS AGE while NORMAL, MAJOR, CRITICAL
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']
        index_together = [
            ["device_name", "service_name", "data_source"],
        ]


class UtilizationHourly(models.Model):
    """
    Sector Utilization model for calculating the sector Utilization per sector
    It keeps the current Value for the Sector Utilization Status.
    Per device, per sector, per port
    Age here will be calculated of the STATUS AGE while NORMAL, MAJOR, CRITICAL
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']
        index_together = [
            ["device_name", "service_name", "data_source"],
        ]


class UtilizationDaily(models.Model):
    """
    Sector Utilization model for calculating the sector Utilization per sector
    It keeps the current Value for the Sector Utilization Status.
    Per device, per sector, per port
    Age here will be calculated of the STATUS AGE while NORMAL, MAJOR, CRITICAL
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']
        index_together = [
            ["device_name", "service_name", "data_source"],
        ]


class UtilizationWeekly(models.Model):
    """
    Sector Utilization model for calculating the sector Utilization per sector
    It keeps the current Value for the Sector Utilization Status.
    Per device, per sector, per port
    Age here will be calculated of the STATUS AGE while NORMAL, MAJOR, CRITICAL
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']
        index_together = [
            ["device_name", "service_name", "data_source"],
        ]


class UtilizationMonthly(models.Model):
    """
    Sector Utilization model for calculating the sector Utilization per sector
    It keeps the current Value for the Sector Utilization Status.
    Per device, per sector, per port
    Age here will be calculated of the STATUS AGE while NORMAL, MAJOR, CRITICAL
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']
        index_together = [
            ["device_name", "service_name", "data_source"],
        ]


class UtilizationYearly(models.Model):
    """
    Sector Utilization model for calculating the sector Utilization per sector
    It keeps the current Value for the Sector Utilization Status.
    Per device, per sector, per port
    Age here will be calculated of the STATUS AGE while NORMAL, MAJOR, CRITICAL
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']
        index_together = [
            ["device_name", "service_name", "data_source"],
        ]


class UtilizationStatus(models.Model):
    """
    Sector Utilization model for calculating the sector Utilization per sector
    It keeps the current Value for the Sector Utilization Status.
    Per device, per sector, per port
    Age here will be calculated of the STATUS AGE while NORMAL, MAJOR, CRITICAL
    """
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, db_index=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    age = models.IntegerField('Status Age', default=0)
    refer = models.CharField('Reference Variable', max_length=32, null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']
        unique_together = (
            ("device_name", "service_name", "data_source")
        )

##################################################################
############ Table for Spot Dashboard Data #######################
##################################################################

class SpotDashboard(models.Model):
    """
    Sector SpotDashboard model
    """

    sector = models.ForeignKey(Sector)
    device = models.ForeignKey(Device)
    #static information so as to save another db
    sector_sector_id = models.CharField('Sector ID', max_length=64, unique=True, null=True, blank=True)
    sector_sector_configured_on = models.CharField('IP Address', max_length=64,  null=True, blank=True)
    sector_device_technology = models.CharField('Technology', max_length=64,  null=True, blank=True)
    #Calculated information
    # Last 6 monthns calculation for UL issues
    ul_issue_1 = models.BooleanField('UL Issue 1', default=False)
    ul_issue_2 = models.BooleanField('UL Issue 2', default=False)
    ul_issue_3 = models.BooleanField('UL Issue 3', default=False)
    ul_issue_4 = models.BooleanField('UL Issue 4', default=False)
    ul_issue_5 = models.BooleanField('UL Issue 5', default=False)
    ul_issue_6 = models.BooleanField('UL Issue 6', default=False)
    # Last 6 monthns calculation for Augmentation
    augment_1 = models.BooleanField('Augementation 1', default=False)
    augment_2 = models.BooleanField('Augementation 2', default=False)
    augment_3 = models.BooleanField('Augementation 3', default=False)
    augment_4 = models.BooleanField('Augementation 4', default=False)
    augment_5 = models.BooleanField('Augementation 5', default=False)
    augment_6 = models.BooleanField('Augementation 6', default=False)
    # Last 6 monthns calculation for SIA
    sia_1 = models.BooleanField('SIA 1', default=False)
    sia_2 = models.BooleanField('SIA 2', default=False)
    sia_3 = models.BooleanField('SIA 3', default=False)
    sia_4 = models.BooleanField('SIA 4', default=False)
    sia_5 = models.BooleanField('SIA 5', default=False)
    sia_6 = models.BooleanField('SIA 6', default=False)


##################################################################
############## Table for RF Network Availability #################
##################################################################

class RfNetworkAvailability(models.Model):

    # technology = models.CharField('Technology', max_length=100, null=True, blank=True)
    technology = models.ForeignKey(DeviceTechnology, default=0)
    avail = models.FloatField('Availability', default=0, null=True, blank=True)
    unavail = models.FloatField('Unavailability', default=0, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)


class CustomDashboard(models.Model):
    """
    CustomDashboard Model Columns Declaration.
    """
    DISPLAY_TYPE = (
        ('table', 'Table'),
        ('chart', 'Chart')
    )

    name = models.CharField('Name', max_length=250, unique=True)
    title = models.CharField('Title', max_length=250)
    display_type = models.CharField('Display Type ', max_length=200, choices=DISPLAY_TYPE, default='table')
    user_profile = models.ManyToManyField(UserProfile, through="UsersCustomDashboard")
    data_source = models.ManyToManyField(ServiceDataSource, through="DSCustomDashboard")
    is_public = models.BooleanField('Is Public Dashboard',default=False)
    is_required = models.BooleanField('Is Required',default=False)

    def __unicode__(self):
        return self.title


class UsersCustomDashboard(models.Model):
    """
    CustomDashboard-UserProfile mapper Model Columns Declaration.
    """
    user_profile = models.ForeignKey(UserProfile)
    custom_dashboard = models.ForeignKey(CustomDashboard)
    created_at = models.DateTimeField(auto_now_add=True)


class DSCustomDashboard(models.Model):
    """
    CustomDashboard-ServiceDataSource mapper Model Columns Declaration.
    """
    service = models.ForeignKey(Service, null=True, blank=True)
    data_source = models.ForeignKey(ServiceDataSource)
    custom_dashboard = models.ForeignKey(CustomDashboard)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class PingStabilityTest(models.Model):
    """
    This model stores ping stability test data
    """
    user_profile = models.ForeignKey(UserProfile)
    machine = models.ForeignKey(Machine)
    site_instance = models.ForeignKey(SiteInstance)
    ip_address = models.GenericIPAddressField('IP Address', null=True, blank=True)
    technology = models.ForeignKey(DeviceTechnology)
    time_duration = models.IntegerField('Time Duration', default=1)
    file_path = models.CharField('File', max_length=512, null=True, blank=True)
    status = models.BooleanField('Status', default=False)
    email_ids = models.CharField('Email IDs', null=True, blank=True, max_length=512)
    is_deleted = models.BooleanField('Is Deleted',default=False)
    created_at = models.DateTimeField(auto_now_add=True)
