from django.db import models
from command.models import Command
from datetime import datetime


class Protocol(models.Model):
    """
    Protocol Model Columns declaration
    """
    name = models.CharField('Parameters Name', max_length=255)
    protocol_name = models.CharField('Protocol Name', max_length=255)
    port = models.IntegerField('Port')
    version = models.CharField('Version', max_length=10)
    read_community = models.CharField('Read Community', max_length=100)
    write_community = models.CharField('Write Community', max_length=100, blank=True, null=True)
    auth_password = models.CharField('Auth Password', max_length=100, blank=True, null=True)
    auth_protocol = models.CharField('Auth Protocol', max_length=100, blank=True, null=True)
    security_name = models.CharField('Security Name', max_length=100, blank=True, null=True)
    security_level = models.CharField('Security Level', max_length=100, blank=True, null=True)
    private_phase = models.CharField('Private Phase', max_length=100, blank=True, null=True)
    private_pass_phase = models.CharField('Private Pass Phase', max_length=100, null=True, blank=True)

    def __unicode__(self):
        """
        Protocol Object presentation
        """
        return self.name


class ServiceDataSource(models.Model):
    """
    Service Data Source Model Columns declaration
    """
    name = models.CharField('Name', max_length=100)
    alias = models.CharField('Alias', max_length=250)
    warning = models.CharField('Warning', max_length=255, null=True, blank=True)
    critical = models.CharField('Critical', max_length=255, null=True, blank=True)

    def __unicode__(self):
        """
        Service Data Source Object presentation
        """
        return self.name


class ServiceParameters(models.Model):
    """
    Service Parameters Model Columns Declaration.
    """
    parameter_description = models.CharField(max_length=250)
    protocol = models.ForeignKey(Protocol, verbose_name=" SNMP Parameters")
    normal_check_interval = models.IntegerField()
    retry_check_interval = models.IntegerField()
    max_check_attempts = models.IntegerField()

    '''
    max_check_attempts = models.IntegerField()
    check_interval = models.IntegerField()
    retry_interval = models.IntegerField(null=True, blank=True)
    check_period = models.CharField(max_length=100, null=True, blank=True)
    notification_interval = models.IntegerField(null=True, blank=True)
    notification_period = models.CharField(max_length=100, null=True, blank=True)  # timeperiod_name
    is_volatile = models.IntegerField(null=True, blank=True)
    initial_state = models.CharField(max_length=1, null=True, blank=True)                              # [o,w,u,c]
    active_checks_enabled = models.IntegerField(null=True, blank=True)                                 # [0/1]
    passive_checks_enabled = models.IntegerField(null=True, blank=True)                                # [0/1]
    obsess_over_service = models.IntegerField(null=True, blank=True)                                   # [0/1]
    check_freshness = models.IntegerField(null=True, blank=True)                                       # [0/1]
    freshness_threshold = models.CharField(max_length=100, null=True, blank=True)
    event_handler = models.CharField(max_length=100, null=True, blank=True)
    event_handler_enabled = models.IntegerField()                                                      # [0/1]
    low_flap_threshold = models.CharField(max_length=100, null=True, blank=True)
    high_flap_threshold = models.CharField(max_length=100, null=True, blank=True)
    flap_detection_enabled = models.IntegerField(null=True, blank=True)                                # [0/1]
    flap_detection_options = models.CharField(max_length=100, null=True, blank=True)                   # [o,w,c,u]
    process_perf_data = models.CharField(max_length=100, null=True, blank=True)                        # [0/1]
    retain_status_information = models.IntegerField(null=True, blank=True)                             # [0/1]
    retain_nonstatus_information = models.IntegerField(null=True, blank=True)                          # [0/1]
    first_notification_delay = models.IntegerField(null=True, blank=True)
    notification_options = models.CharField(max_length=1, null=True, blank=True)                       # [w,u,c,r,f,s]
    notifications_enabled = models.IntegerField(null=True, blank=True)
    stalking_options = models.CharField(max_length=1, null=True, blank=True)                           # [o,w,u,c]
    notes = models.CharField(max_length=100, null=True, blank=True)
    notes_url = models.URLField(max_length=200, null=True, blank=True)
    action_url = models.URLField(max_length=200, null=True, blank=True)
    '''

    def __unicode__(self):
        """
        Service Parameters object presentation.
        """
        return self.parameter_description


class Service(models.Model):
    """
    Service Model Column Declaration.
    """
    name = models.CharField('Name', max_length=100)
    alias = models.CharField('Alias', max_length=100)
    parameters = models.ForeignKey(ServiceParameters)
    service_data_sources = models.ManyToManyField(ServiceDataSource, through="ServiceSpecificDataSource")
    command = models.ForeignKey(Command, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        """
        Service object presentation
        """
        return self.name


class ServiceSpecificDataSource(models.Model):
    """
    Service Based Data Source Model Column Declaration.
    """
    service_data_sources = models.ForeignKey(ServiceDataSource)
    service = models.ForeignKey(Service)
    warning = models.CharField('Warning', max_length=255, null=True, blank=True)
    critical = models.CharField('Critical', max_length=255, null=True, blank=True)


# device service configuration --> it contains services those are already running
class DeviceServiceConfiguration(models.Model):
    """
    Device Service Configuration Model Declaration.
    """
    device_name = models.CharField('Device Name', max_length=200, null=True, blank=True)
    service_name = models.CharField('Service Name', max_length=200, null=True, blank=True)
    agent_tag = models.CharField('Agent Tag', max_length=50, null=True, blank=True)
    port = models.IntegerField('Port', null=True, blank=True)
    data_source = models.CharField('Data Source', max_length=200, null=True, blank=True)
    version = models.CharField('Version', max_length=10, blank=True, null=True)
    read_community = models.CharField('Read Community', max_length=100, blank=True, null=True)
    svc_template = models.CharField('Service Template', max_length=200, blank=True, null=True)
    normal_check_interval = models.IntegerField('Normal Check Interval', null=True, blank=True)
    retry_check_interval = models.IntegerField('Retry Check Interval', null=True, blank=True)
    max_check_attempts = models.IntegerField('Max Check Attempts', null=True, blank=True)
    warning = models.CharField('Warning', max_length=20, null=True, blank=True)
    critical = models.CharField('Critical', max_length=20, null=True, blank=True)
    added_on = models.DateTimeField('Added On', null=True, blank=True)
    modified_on = models.DateTimeField('Modified On', null=True, blank=True)
    is_added = models.IntegerField('Is Added', default=0)

    class Meta:
        ordering = ["added_on"]

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.added_on = datetime.now()
        self.modified_on = datetime.now()
        return super(DeviceServiceConfiguration, self).save(*args, **kwargs)

    def __unicode__(self):
        """
        Device Service Configuration object presentation
        """
        return "{} - {} - {}".format(self.device_name, self.service_name, self.added_on)


# device service configuration --> it contains services those are already running
class DevicePingConfiguration(models.Model):
    """
    Device Ping Configuration Model Declaration.
    """
    device_name = models.CharField('Device Name', max_length=200, null=True, blank=True)
    device_alias = models.CharField('Device Alias', max_length=200, null=True, blank=True)
    packets = models.IntegerField('Packets', null=True, blank=True)
    timeout = models.IntegerField('Timeout', null=True, blank=True)
    normal_check_interval = models.IntegerField('Normal Check Interval', null=True, blank=True)
    rta_warning = models.IntegerField('RTA Warning', null=True, blank=True)
    rta_critical = models.IntegerField('RTA Critical', null=True, blank=True)
    pl_warning = models.IntegerField('PL Warning', null=True, blank=True)
    pl_critical = models.IntegerField('PL Critical', null=True, blank=True)
    added_on = models.DateTimeField('Added On', null=True, blank=True)
    modified_on = models.DateTimeField('Modified On', null=True, blank=True)

    class Meta:
        ordering = ["added_on"]

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.added_on = datetime.now()
        self.modified_on = datetime.now()
        return super(DevicePingConfiguration, self).save(*args, **kwargs)

    def __unicode__(self):
        """
        Device Ping Configuration object presentation
        """
        return "{} - {} - {}".format(self.device_name, self.service_name, self.added_on)
