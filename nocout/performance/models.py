from django.db import models


# performance tables
class PerformanceMetric(models.Model):
    device_name = models.CharField('Device Name', max_length=100, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=100, null=True, blank=True)
    machine_name = models.CharField('Machine Name', max_length=100, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=100, null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.IntegerField('Severity', null=True, blank=True)
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
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.IntegerField('Severity', null=True, blank=True)
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
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.IntegerField('Severity', null=True, blank=True)
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
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.IntegerField('Severity', null=True, blank=True)
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
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.IntegerField('Severity', null=True, blank=True)
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
    data_source = models.CharField('Data Source', max_length=100, null=True, blank=True)
    severity = models.IntegerField('Severity', null=True, blank=True)
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
    host = models.CharField('Device Name', max_length=40, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=40, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    state_type = models.CharField('State Type', max_length=20, null=True, blank=True)
    event_type = models.CharField('Event Type', max_length=40, null=True, blank=True)
    status = models.CharField('Status', max_length=40, null=True, blank=True)
    device_type = models.CharField('Device Type', max_length=20, null=True, blank=True)
    #service = models.CharField('Service', max_length=20, null=True, blank=True)
    time = models.IntegerField('Time', null=True, blank=True)
    event_description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.host


class EventService(models.Model):
    host = models.CharField('Device Name', max_length=40, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=40, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    state_type = models.CharField('State Type', max_length=20, null=True, blank=True)
    event_type = models.CharField('Event Type', max_length=40, null=True, blank=True)
    status = models.CharField('Status', max_length=40, null=True, blank=True)
    device_type = models.CharField('Device Type', max_length=20, null=True, blank=True)
    service = models.CharField('Service', max_length=20, null=True, blank=True)
    time = models.IntegerField('Time', null=True, blank=True)
    event_description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.host


class EventStatus(models.Model):
    host = models.CharField('Device Name', max_length=40, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=40, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    state_type = models.CharField('State Type', max_length=20, null=True, blank=True)
    event_type = models.CharField('Event Type', max_length=40, null=True, blank=True)
    status = models.CharField('Status', max_length=40, null=True, blank=True)
    device_type = models.CharField('Device Type', max_length=20, null=True, blank=True)
    service = models.CharField('Service', max_length=20, null=True, blank=True)
    time = models.IntegerField('Time', null=True, blank=True)
    event_description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.host


class EventMachine(models.Model):
    host = models.CharField('Device Name', max_length=40, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=40, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    state_type = models.CharField('State Type', max_length=20, null=True, blank=True)
    event_type = models.CharField('Event Type', max_length=40, null=True, blank=True)
    status = models.CharField('Status', max_length=40, null=True, blank=True)
    device_type = models.CharField('Device Type', max_length=20, null=True, blank=True)
    service = models.CharField('Service', max_length=20, null=True, blank=True)
    time = models.IntegerField('Time', null=True, blank=True)
    event_description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.host


class EventInventory(models.Model):
    host = models.CharField('Device Name', max_length=40, null=True, blank=True)
    site_name = models.CharField('Site Name', max_length=40, null=True, blank=True)
    ip_address = models.CharField('IP Address', max_length=20, null=True, blank=True)
    state_type = models.CharField('State Type', max_length=20, null=True, blank=True)
    event_type = models.CharField('Event Type', max_length=40, null=True, blank=True)
    status = models.CharField('Status', max_length=40, null=True, blank=True)
    device_type = models.CharField('Device Type', max_length=20, null=True, blank=True)
    service = models.CharField('Service', max_length=20, null=True, blank=True)
    time = models.IntegerField('Time', null=True, blank=True)
    event_description = models.CharField('Event Description', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.host

