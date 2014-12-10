from django.db import models


# performance tables
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

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


####Network Performance Tables

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

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

####Network Performance Tables

#### Service Performance Tables

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

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Service Perfromance Tables

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

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


#### Status Services

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

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

#### Inventory Service Performance : Once Daily

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

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

#### Inventory Service Perfomance

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


#### Event Network

#### Event Service

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

#### Events Service

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


class NetworkStatus(models.Model):
    """
    Network Status Table columns declared
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

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class ServiceStatus(models.Model):
    """
    Service Status Table columns declared
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

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']


class MachineStatus(models.Model):
    """
    Machine Status Table columns declared
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


class InventoryStatus(models.Model):
    """
    Inventory Status Table columns declared
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


class Status(models.Model):
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



############################################################################################################
############################################################################################################
##############################Network Availability##########################################################
############################################################################################################
############################################################################################################


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


############################################################################################################
############################################################################################################
#####################             Network Topology                 #########################################
############################################################################################################
############################################################################################################


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
    connected_device_ip = models.CharField('Connected Device IP Address', max_length=20, null=True, db_index=True, blank=True)
    connected_device_mac = models.CharField('Connected Device MAC Address', max_length=20, null=True, db_index=True, blank=True)
    sys_timestamp = models.IntegerField('SYS Timestamp', default=0)
    check_timestamp = models.IntegerField('Check Timestamp', null=True, blank=True)

    def __unicode__(self):
        return self.device_name

    class Meta:
        ordering = ['-sys_timestamp']

############################################################################################################
############################################################################################################
#####################      Sector//Backhaul Utilization            #########################################
############################################################################################################
############################################################################################################

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


class UtilizationDaily(models.Model):
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


class UtilizationWeekly(models.Model):
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


class UtilizationMonthly(models.Model):
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


class UtilizationYearly(models.Model):
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


class UtilizationStatus(models.Model):
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