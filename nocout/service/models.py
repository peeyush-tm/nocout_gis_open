from django.db import models
from command.models import Command


class Protocol(models.Model):
    name = models.CharField('Parameters Name', max_length=255)
    protocol_name = models.CharField('Protocol Name', max_length=255)
    port = models.IntegerField('Port', null=True, blank=True)
    version = models.CharField('Version', max_length=10, blank=True, null=True)
    read_community = models.CharField('Read Community', max_length=100, blank=True, null=True)
    write_community = models.CharField('Write Community', max_length=100, blank=True, null=True)
    auth_password = models.CharField('Auth Password', max_length=100, blank=True, null=True)
    auth_protocol = models.CharField('Auth Protocol', max_length=100, blank=True, null=True)
    security_name = models.CharField('Security Name', max_length=100, blank=True, null=True)
    security_level = models.CharField('Security Level', max_length=100, blank=True, null=True)
    private_phase = models.CharField('Private Phase', max_length=100, blank=True, null=True)
    private_pass_phase = models.CharField('Private Pass Phase', max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.name


class ServiceDataSource(models.Model):
    name = models.CharField('Name', max_length=100)
    alias = models.CharField('Alias', max_length=250)
    warning = models.CharField('Warning', max_length=255, null=True, blank=True)
    critical = models.CharField('Critical', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return  self.name


class ServiceParameters(models.Model):
    parameter_description = models.CharField(max_length=250)
    protocol = models.ForeignKey(Protocol, null=True, blank=True)
    max_check_attempts = models.IntegerField()
    check_interval = models.IntegerField()
    retry_interval = models.IntegerField(null=True, blank=True)
    check_period = models.CharField(max_length=100, null=True, blank=True)
    notification_interval = models.IntegerField(null=True, blank=True)
    notification_period = models.CharField(max_length=100, null=True, blank=True)  # timeperiod_name
    '''
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
        return self.parameter_description


class Service(models.Model):
    name = models.CharField('Service Name', max_length=100)
    alias = models.CharField('Service Alias', max_length=100)
    parameters = models.ForeignKey(ServiceParameters, null=True, blank=True)
    service_data_sources = models.ManyToManyField(ServiceDataSource, null=True, blank=True)
    command = models.ForeignKey(Command, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name
    