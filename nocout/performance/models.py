from django.db import models


# performance tables
class PerformanceMetric(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class PerformanceNetwork(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class PerformanceService(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class PerformanceStatus(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class PerformanceMachine(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class PerformanceInventory(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name


# events tables
class EventNetwork(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class EventService(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class EventStatus(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class EventMachine(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class EventInventory(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)
    description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class NetworkStatus(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class ServiceStatus(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class MachineStatus(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name


class InventoryStatus(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=20, null=True, blank=True)
    min_value = models.CharField('Min Value', max_length=20, null=True, blank=True)
    max_value = models.CharField('Max Value', max_length=20, null=True, blank=True)
    avg_value = models.CharField('Avg Value', max_length=20, null=True, blank=True)
    warning_threshold = models.CharField('Warning Threshold', max_length=20, null=True, blank=True)
    critical_threshold = models.CharField('Critical Threshold', max_length=20, null=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', null=True, blank=True)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name