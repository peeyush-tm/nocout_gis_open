from django.db import models
from device.models import DeviceTechnology, DeviceType


class GenericAlarm(models.Model):
	id = models.IntegerField(primary_key=True)
	device_name = models.CharField(max_length=128)
	ip_address = models.CharField(max_length=20)
	trapoid = models.CharField(max_length=100)
	eventname = models.CharField(max_length=100)
	eventno = models.CharField(max_length=50)
	severity = models.CharField(max_length=20)
	uptime = models.CharField(max_length=20)
	traptime = models.CharField(max_length=30)
	description = models.CharField(max_length=256)
	alarm_count = models.IntegerField(null=True,blank=True)
	first_occurred = models.DateTimeField(null=True,blank=True)
	last_occurred = models.DateTimeField(null=True,blank=True)
	is_active = models.IntegerField(null=True,blank=True)
	sia = models.CharField(max_length=32, blank=True, null=True)
	customer_count = models.IntegerField(blank=True, null=True)
	technology = models.CharField("Technology", max_length=256, null=True, blank=True)
	# ticket_number = models.CharField('Ticket Number', max_length=256, null=True, blank=True)

	class Meta:
		abstract = True


class HistoryAlarms(GenericAlarm):
	pass


class CurrentAlarms(GenericAlarm):
	pass


class ClearAlarms(GenericAlarm):
	pass


class MasterAlarm(models.Model):
	"""

	"""
	alarm_name = models.CharField('Alarm Name', max_length=256, null=True, blank=True)
	oid = models.CharField('OID', max_length=256, null=True, blank=True)
	severity = models.CharField('Severity', max_length=16, null=True, blank=True)
	device_type = models.CharField('Device Type', max_length=128, null=True, blank=True)
	alarm_mode = models.CharField('Alarm Mode', max_length=32, null=True, blank=True)
	alarm_type = models.CharField('Alarm Type', max_length=32, null=True, blank=True)
	sia = models.IntegerField('IS SIA', null=True, blank=True)
	auto_tt = models.IntegerField('Auto TT', null=True, blank=True)
	correlation = models.IntegerField('Correlation', null=True, blank=True)
	to_monolith = models.IntegerField('To Monolith', null=True, blank=True)
	mail = models.IntegerField('Mail', null=True, blank=True)
	sms = models.IntegerField('SMS', null=True, blank=True)
	coverage = models.CharField('Coverage', max_length=128, null=True, blank=True)
	resource_name = models.CharField('Resource Name', max_length=128, null=True, blank=True)
	resource_type = models.CharField('Resource Type', max_length=32, null=True, blank=True)
	support_organization = models.CharField('Support Organization', max_length=256, null=True, blank=True)
	bearer_organization = models.CharField('Bearer Organization', max_length=256, null=True, blank=True)
	priority = models.IntegerField(null=True,blank=True)
	refer = models.CharField('Refer', max_length=256, null=True, blank=True)
	alarm_category = models.CharField('Alarm Category', max_length=256, null=True, blank=True)

	class Meta:
		db_table = 'master_alarm_table'


class PlannedEvent(models.Model):
	'''
	This model contains planned events data fetched from monolith DB
	'''
	startdate = models.IntegerField('Scheduled Start Datetime', default=0)
	enddate = models.IntegerField('Scheduled End Datetime', default=0)
	event_type = models.CharField('Event Type', max_length=128, null=True, blank=True)
	technology = models.ForeignKey(DeviceTechnology)
	device_type = models.ForeignKey(DeviceType)
	owner_details = models.CharField('PE Owner Details', max_length=255, null=True, blank=True)
	change_coordinator = models.CharField('Change Coordinator', max_length=255, null=True, blank=True)
	pettno = models.CharField('PE TT No.', max_length=255, null=True, blank=True)
	sr_number = models.CharField('SR Number', max_length=255, null=True, blank=True)
	impacted_customer = models.IntegerField('Impacted Customer', default=0)
	timing = models.CharField('Timing', max_length=255, null=True, blank=True)
	summary = models.CharField('Change Summary', max_length=255, null=True, blank=True)
	status = models.CharField('Change Status', max_length=255, null=True, blank=True)
	impacted_domain = models.CharField('Impacted Domain', max_length=255, null=True, blank=True)
	component = models.CharField('Component', max_length=255, null=True, blank=True)
	sectorid = models.CharField('SectorID', max_length=255, null=True, blank=True)
	resource_name = models.CharField('Resource Name/IP Address', max_length=255, null=True, blank=True)
	service_ids = models.TextField('Service IDs', null=True, blank=True)
	nia = models.TextField('NIA', null=True, blank=True)
