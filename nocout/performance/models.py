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

    def __unicode__(self):
        return self.device_name


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

    def __unicode__(self):
        return self.device_name


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
