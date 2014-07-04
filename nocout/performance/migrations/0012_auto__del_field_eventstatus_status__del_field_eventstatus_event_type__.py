# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'EventStatus.status'
        db.delete_column(u'performance_eventstatus', 'status')

        # Deleting field 'EventStatus.event_type'
        db.delete_column(u'performance_eventstatus', 'event_type')

        # Deleting field 'EventStatus.state_type'
        db.delete_column(u'performance_eventstatus', 'state_type')

        # Deleting field 'EventStatus.host'
        db.delete_column(u'performance_eventstatus', 'host')

        # Deleting field 'EventStatus.device_type'
        db.delete_column(u'performance_eventstatus', 'device_type')

        # Deleting field 'EventStatus.event_description'
        db.delete_column(u'performance_eventstatus', 'event_description')

        # Deleting field 'EventStatus.service'
        db.delete_column(u'performance_eventstatus', 'service')

        # Deleting field 'EventStatus.time'
        db.delete_column(u'performance_eventstatus', 'time')

        # Adding field 'EventStatus.device_name'
        db.add_column(u'performance_eventstatus', 'device_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.service_name'
        db.add_column(u'performance_eventstatus', 'service_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.machine_name'
        db.add_column(u'performance_eventstatus', 'machine_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.data_source'
        db.add_column(u'performance_eventstatus', 'data_source',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.severity'
        db.add_column(u'performance_eventstatus', 'severity',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.current_value'
        db.add_column(u'performance_eventstatus', 'current_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.min_value'
        db.add_column(u'performance_eventstatus', 'min_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.max_value'
        db.add_column(u'performance_eventstatus', 'max_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.avg_value'
        db.add_column(u'performance_eventstatus', 'avg_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.warning_threshold'
        db.add_column(u'performance_eventstatus', 'warning_threshold',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.critical_threshold'
        db.add_column(u'performance_eventstatus', 'critical_threshold',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.sys_timestamp'
        db.add_column(u'performance_eventstatus', 'sys_timestamp',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.check_timestamp'
        db.add_column(u'performance_eventstatus', 'check_timestamp',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.description'
        db.add_column(u'performance_eventstatus', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


        # Changing field 'EventStatus.site_name'
        db.alter_column(u'performance_eventstatus', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))
        # Adding field 'PerformanceMetric.ip_address'
        db.add_column(u'performance_performancemetric', 'ip_address',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)


        # Changing field 'PerformanceMetric.severity'
        db.alter_column(u'performance_performancemetric', 'severity', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))
        # Deleting field 'EventService.status'
        db.delete_column(u'performance_eventservice', 'status')

        # Deleting field 'EventService.host'
        db.delete_column(u'performance_eventservice', 'host')

        # Deleting field 'EventService.device_type'
        db.delete_column(u'performance_eventservice', 'device_type')

        # Deleting field 'EventService.event_description'
        db.delete_column(u'performance_eventservice', 'event_description')

        # Deleting field 'EventService.service'
        db.delete_column(u'performance_eventservice', 'service')

        # Deleting field 'EventService.time'
        db.delete_column(u'performance_eventservice', 'time')

        # Adding field 'EventService.device_name'
        db.add_column(u'performance_eventservice', 'device_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.service_name'
        db.add_column(u'performance_eventservice', 'service_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.data_source'
        db.add_column(u'performance_eventservice', 'data_source',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.severity'
        db.add_column(u'performance_eventservice', 'severity',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.current_value'
        db.add_column(u'performance_eventservice', 'current_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.min_value'
        db.add_column(u'performance_eventservice', 'min_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.max_value'
        db.add_column(u'performance_eventservice', 'max_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.avg_value'
        db.add_column(u'performance_eventservice', 'avg_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.warning_threshold'
        db.add_column(u'performance_eventservice', 'warning_threshold',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.critical_threshold'
        db.add_column(u'performance_eventservice', 'critical_threshold',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.sys_timestamp'
        db.add_column(u'performance_eventservice', 'sys_timestamp',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.check_timestamp'
        db.add_column(u'performance_eventservice', 'check_timestamp',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.description'
        db.add_column(u'performance_eventservice', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


        # Changing field 'EventService.site_name'
        db.alter_column(u'performance_eventservice', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))
        # Deleting field 'EventNetwork.status'
        db.delete_column(u'performance_eventnetwork', 'status')

        # Deleting field 'EventNetwork.event_description'
        db.delete_column(u'performance_eventnetwork', 'event_description')

        # Deleting field 'EventNetwork.device_type'
        db.delete_column(u'performance_eventnetwork', 'device_type')

        # Deleting field 'EventNetwork.time'
        db.delete_column(u'performance_eventnetwork', 'time')

        # Deleting field 'EventNetwork.host'
        db.delete_column(u'performance_eventnetwork', 'host')

        # Adding field 'EventNetwork.device_name'
        db.add_column(u'performance_eventnetwork', 'device_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.service_name'
        db.add_column(u'performance_eventnetwork', 'service_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.data_source'
        db.add_column(u'performance_eventnetwork', 'data_source',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.severity'
        db.add_column(u'performance_eventnetwork', 'severity',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.current_value'
        db.add_column(u'performance_eventnetwork', 'current_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.min_value'
        db.add_column(u'performance_eventnetwork', 'min_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.max_value'
        db.add_column(u'performance_eventnetwork', 'max_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.avg_value'
        db.add_column(u'performance_eventnetwork', 'avg_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.warning_threshold'
        db.add_column(u'performance_eventnetwork', 'warning_threshold',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.critical_threshold'
        db.add_column(u'performance_eventnetwork', 'critical_threshold',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.sys_timestamp'
        db.add_column(u'performance_eventnetwork', 'sys_timestamp',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.check_timestamp'
        db.add_column(u'performance_eventnetwork', 'check_timestamp',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.description'
        db.add_column(u'performance_eventnetwork', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


        # Changing field 'EventNetwork.site_name'
        db.alter_column(u'performance_eventnetwork', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))
        # Adding field 'PerformanceStatus.ip_address'
        db.add_column(u'performance_performancestatus', 'ip_address',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)


        # Changing field 'PerformanceStatus.severity'
        db.alter_column(u'performance_performancestatus', 'severity', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))
        # Adding field 'PerformanceMachine.ip_address'
        db.add_column(u'performance_performancemachine', 'ip_address',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)


        # Changing field 'PerformanceMachine.severity'
        db.alter_column(u'performance_performancemachine', 'severity', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))
        # Deleting field 'EventInventory.status'
        db.delete_column(u'performance_eventinventory', 'status')

        # Deleting field 'EventInventory.event_type'
        db.delete_column(u'performance_eventinventory', 'event_type')

        # Deleting field 'EventInventory.state_type'
        db.delete_column(u'performance_eventinventory', 'state_type')

        # Deleting field 'EventInventory.host'
        db.delete_column(u'performance_eventinventory', 'host')

        # Deleting field 'EventInventory.device_type'
        db.delete_column(u'performance_eventinventory', 'device_type')

        # Deleting field 'EventInventory.event_description'
        db.delete_column(u'performance_eventinventory', 'event_description')

        # Deleting field 'EventInventory.service'
        db.delete_column(u'performance_eventinventory', 'service')

        # Deleting field 'EventInventory.time'
        db.delete_column(u'performance_eventinventory', 'time')

        # Adding field 'EventInventory.device_name'
        db.add_column(u'performance_eventinventory', 'device_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.service_name'
        db.add_column(u'performance_eventinventory', 'service_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.machine_name'
        db.add_column(u'performance_eventinventory', 'machine_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.data_source'
        db.add_column(u'performance_eventinventory', 'data_source',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.severity'
        db.add_column(u'performance_eventinventory', 'severity',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.current_value'
        db.add_column(u'performance_eventinventory', 'current_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.min_value'
        db.add_column(u'performance_eventinventory', 'min_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.max_value'
        db.add_column(u'performance_eventinventory', 'max_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.avg_value'
        db.add_column(u'performance_eventinventory', 'avg_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.warning_threshold'
        db.add_column(u'performance_eventinventory', 'warning_threshold',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.critical_threshold'
        db.add_column(u'performance_eventinventory', 'critical_threshold',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.sys_timestamp'
        db.add_column(u'performance_eventinventory', 'sys_timestamp',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.check_timestamp'
        db.add_column(u'performance_eventinventory', 'check_timestamp',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.description'
        db.add_column(u'performance_eventinventory', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


        # Changing field 'EventInventory.site_name'
        db.alter_column(u'performance_eventinventory', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'PerformanceService.severity'
        db.alter_column(u'performance_performanceservice', 'severity', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'PerformanceNetwork.severity'
        db.alter_column(u'performance_performancenetwork', 'severity', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))
        # Adding field 'PerformanceInventory.ip_address'
        db.add_column(u'performance_performanceinventory', 'ip_address',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)


        # Changing field 'PerformanceInventory.severity'
        db.alter_column(u'performance_performanceinventory', 'severity', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))
        # Deleting field 'EventMachine.status'
        db.delete_column(u'performance_eventmachine', 'status')

        # Deleting field 'EventMachine.event_type'
        db.delete_column(u'performance_eventmachine', 'event_type')

        # Deleting field 'EventMachine.state_type'
        db.delete_column(u'performance_eventmachine', 'state_type')

        # Deleting field 'EventMachine.host'
        db.delete_column(u'performance_eventmachine', 'host')

        # Deleting field 'EventMachine.device_type'
        db.delete_column(u'performance_eventmachine', 'device_type')

        # Deleting field 'EventMachine.event_description'
        db.delete_column(u'performance_eventmachine', 'event_description')

        # Deleting field 'EventMachine.service'
        db.delete_column(u'performance_eventmachine', 'service')

        # Deleting field 'EventMachine.time'
        db.delete_column(u'performance_eventmachine', 'time')

        # Adding field 'EventMachine.device_name'
        db.add_column(u'performance_eventmachine', 'device_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.service_name'
        db.add_column(u'performance_eventmachine', 'service_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.machine_name'
        db.add_column(u'performance_eventmachine', 'machine_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.data_source'
        db.add_column(u'performance_eventmachine', 'data_source',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.severity'
        db.add_column(u'performance_eventmachine', 'severity',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.current_value'
        db.add_column(u'performance_eventmachine', 'current_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.min_value'
        db.add_column(u'performance_eventmachine', 'min_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.max_value'
        db.add_column(u'performance_eventmachine', 'max_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.avg_value'
        db.add_column(u'performance_eventmachine', 'avg_value',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.warning_threshold'
        db.add_column(u'performance_eventmachine', 'warning_threshold',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.critical_threshold'
        db.add_column(u'performance_eventmachine', 'critical_threshold',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.sys_timestamp'
        db.add_column(u'performance_eventmachine', 'sys_timestamp',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.check_timestamp'
        db.add_column(u'performance_eventmachine', 'check_timestamp',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.description'
        db.add_column(u'performance_eventmachine', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


        # Changing field 'EventMachine.site_name'
        db.alter_column(u'performance_eventmachine', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

    def backwards(self, orm):
        # Adding field 'EventStatus.status'
        db.add_column(u'performance_eventstatus', 'status',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.event_type'
        db.add_column(u'performance_eventstatus', 'event_type',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.state_type'
        db.add_column(u'performance_eventstatus', 'state_type',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.host'
        db.add_column(u'performance_eventstatus', 'host',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.device_type'
        db.add_column(u'performance_eventstatus', 'device_type',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.event_description'
        db.add_column(u'performance_eventstatus', 'event_description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.service'
        db.add_column(u'performance_eventstatus', 'service',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventStatus.time'
        db.add_column(u'performance_eventstatus', 'time',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'EventStatus.device_name'
        db.delete_column(u'performance_eventstatus', 'device_name')

        # Deleting field 'EventStatus.service_name'
        db.delete_column(u'performance_eventstatus', 'service_name')

        # Deleting field 'EventStatus.machine_name'
        db.delete_column(u'performance_eventstatus', 'machine_name')

        # Deleting field 'EventStatus.data_source'
        db.delete_column(u'performance_eventstatus', 'data_source')

        # Deleting field 'EventStatus.severity'
        db.delete_column(u'performance_eventstatus', 'severity')

        # Deleting field 'EventStatus.current_value'
        db.delete_column(u'performance_eventstatus', 'current_value')

        # Deleting field 'EventStatus.min_value'
        db.delete_column(u'performance_eventstatus', 'min_value')

        # Deleting field 'EventStatus.max_value'
        db.delete_column(u'performance_eventstatus', 'max_value')

        # Deleting field 'EventStatus.avg_value'
        db.delete_column(u'performance_eventstatus', 'avg_value')

        # Deleting field 'EventStatus.warning_threshold'
        db.delete_column(u'performance_eventstatus', 'warning_threshold')

        # Deleting field 'EventStatus.critical_threshold'
        db.delete_column(u'performance_eventstatus', 'critical_threshold')

        # Deleting field 'EventStatus.sys_timestamp'
        db.delete_column(u'performance_eventstatus', 'sys_timestamp')

        # Deleting field 'EventStatus.check_timestamp'
        db.delete_column(u'performance_eventstatus', 'check_timestamp')

        # Deleting field 'EventStatus.description'
        db.delete_column(u'performance_eventstatus', 'description')


        # Changing field 'EventStatus.site_name'
        db.alter_column(u'performance_eventstatus', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))
        # Deleting field 'PerformanceMetric.ip_address'
        db.delete_column(u'performance_performancemetric', 'ip_address')


        # Changing field 'PerformanceMetric.severity'
        db.alter_column(u'performance_performancemetric', 'severity', self.gf('django.db.models.fields.IntegerField')(null=True))
        # Adding field 'EventService.status'
        db.add_column(u'performance_eventservice', 'status',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.host'
        db.add_column(u'performance_eventservice', 'host',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.device_type'
        db.add_column(u'performance_eventservice', 'device_type',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.event_description'
        db.add_column(u'performance_eventservice', 'event_description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.service'
        db.add_column(u'performance_eventservice', 'service',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventService.time'
        db.add_column(u'performance_eventservice', 'time',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'EventService.device_name'
        db.delete_column(u'performance_eventservice', 'device_name')

        # Deleting field 'EventService.service_name'
        db.delete_column(u'performance_eventservice', 'service_name')

        # Deleting field 'EventService.data_source'
        db.delete_column(u'performance_eventservice', 'data_source')

        # Deleting field 'EventService.severity'
        db.delete_column(u'performance_eventservice', 'severity')

        # Deleting field 'EventService.current_value'
        db.delete_column(u'performance_eventservice', 'current_value')

        # Deleting field 'EventService.min_value'
        db.delete_column(u'performance_eventservice', 'min_value')

        # Deleting field 'EventService.max_value'
        db.delete_column(u'performance_eventservice', 'max_value')

        # Deleting field 'EventService.avg_value'
        db.delete_column(u'performance_eventservice', 'avg_value')

        # Deleting field 'EventService.warning_threshold'
        db.delete_column(u'performance_eventservice', 'warning_threshold')

        # Deleting field 'EventService.critical_threshold'
        db.delete_column(u'performance_eventservice', 'critical_threshold')

        # Deleting field 'EventService.sys_timestamp'
        db.delete_column(u'performance_eventservice', 'sys_timestamp')

        # Deleting field 'EventService.check_timestamp'
        db.delete_column(u'performance_eventservice', 'check_timestamp')

        # Deleting field 'EventService.description'
        db.delete_column(u'performance_eventservice', 'description')


        # Changing field 'EventService.site_name'
        db.alter_column(u'performance_eventservice', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))
        # Adding field 'EventNetwork.status'
        db.add_column(u'performance_eventnetwork', 'status',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.event_description'
        db.add_column(u'performance_eventnetwork', 'event_description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.device_type'
        db.add_column(u'performance_eventnetwork', 'device_type',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.time'
        db.add_column(u'performance_eventnetwork', 'time',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventNetwork.host'
        db.add_column(u'performance_eventnetwork', 'host',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'EventNetwork.device_name'
        db.delete_column(u'performance_eventnetwork', 'device_name')

        # Deleting field 'EventNetwork.service_name'
        db.delete_column(u'performance_eventnetwork', 'service_name')

        # Deleting field 'EventNetwork.data_source'
        db.delete_column(u'performance_eventnetwork', 'data_source')

        # Deleting field 'EventNetwork.severity'
        db.delete_column(u'performance_eventnetwork', 'severity')

        # Deleting field 'EventNetwork.current_value'
        db.delete_column(u'performance_eventnetwork', 'current_value')

        # Deleting field 'EventNetwork.min_value'
        db.delete_column(u'performance_eventnetwork', 'min_value')

        # Deleting field 'EventNetwork.max_value'
        db.delete_column(u'performance_eventnetwork', 'max_value')

        # Deleting field 'EventNetwork.avg_value'
        db.delete_column(u'performance_eventnetwork', 'avg_value')

        # Deleting field 'EventNetwork.warning_threshold'
        db.delete_column(u'performance_eventnetwork', 'warning_threshold')

        # Deleting field 'EventNetwork.critical_threshold'
        db.delete_column(u'performance_eventnetwork', 'critical_threshold')

        # Deleting field 'EventNetwork.sys_timestamp'
        db.delete_column(u'performance_eventnetwork', 'sys_timestamp')

        # Deleting field 'EventNetwork.check_timestamp'
        db.delete_column(u'performance_eventnetwork', 'check_timestamp')

        # Deleting field 'EventNetwork.description'
        db.delete_column(u'performance_eventnetwork', 'description')


        # Changing field 'EventNetwork.site_name'
        db.alter_column(u'performance_eventnetwork', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))
        # Deleting field 'PerformanceStatus.ip_address'
        db.delete_column(u'performance_performancestatus', 'ip_address')


        # Changing field 'PerformanceStatus.severity'
        db.alter_column(u'performance_performancestatus', 'severity', self.gf('django.db.models.fields.IntegerField')(null=True))
        # Deleting field 'PerformanceMachine.ip_address'
        db.delete_column(u'performance_performancemachine', 'ip_address')


        # Changing field 'PerformanceMachine.severity'
        db.alter_column(u'performance_performancemachine', 'severity', self.gf('django.db.models.fields.IntegerField')(null=True))
        # Adding field 'EventInventory.status'
        db.add_column(u'performance_eventinventory', 'status',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.event_type'
        db.add_column(u'performance_eventinventory', 'event_type',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.state_type'
        db.add_column(u'performance_eventinventory', 'state_type',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.host'
        db.add_column(u'performance_eventinventory', 'host',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.device_type'
        db.add_column(u'performance_eventinventory', 'device_type',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.event_description'
        db.add_column(u'performance_eventinventory', 'event_description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.service'
        db.add_column(u'performance_eventinventory', 'service',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventInventory.time'
        db.add_column(u'performance_eventinventory', 'time',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'EventInventory.device_name'
        db.delete_column(u'performance_eventinventory', 'device_name')

        # Deleting field 'EventInventory.service_name'
        db.delete_column(u'performance_eventinventory', 'service_name')

        # Deleting field 'EventInventory.machine_name'
        db.delete_column(u'performance_eventinventory', 'machine_name')

        # Deleting field 'EventInventory.data_source'
        db.delete_column(u'performance_eventinventory', 'data_source')

        # Deleting field 'EventInventory.severity'
        db.delete_column(u'performance_eventinventory', 'severity')

        # Deleting field 'EventInventory.current_value'
        db.delete_column(u'performance_eventinventory', 'current_value')

        # Deleting field 'EventInventory.min_value'
        db.delete_column(u'performance_eventinventory', 'min_value')

        # Deleting field 'EventInventory.max_value'
        db.delete_column(u'performance_eventinventory', 'max_value')

        # Deleting field 'EventInventory.avg_value'
        db.delete_column(u'performance_eventinventory', 'avg_value')

        # Deleting field 'EventInventory.warning_threshold'
        db.delete_column(u'performance_eventinventory', 'warning_threshold')

        # Deleting field 'EventInventory.critical_threshold'
        db.delete_column(u'performance_eventinventory', 'critical_threshold')

        # Deleting field 'EventInventory.sys_timestamp'
        db.delete_column(u'performance_eventinventory', 'sys_timestamp')

        # Deleting field 'EventInventory.check_timestamp'
        db.delete_column(u'performance_eventinventory', 'check_timestamp')

        # Deleting field 'EventInventory.description'
        db.delete_column(u'performance_eventinventory', 'description')


        # Changing field 'EventInventory.site_name'
        db.alter_column(u'performance_eventinventory', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

        # Changing field 'PerformanceService.severity'
        db.alter_column(u'performance_performanceservice', 'severity', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'PerformanceNetwork.severity'
        db.alter_column(u'performance_performancenetwork', 'severity', self.gf('django.db.models.fields.IntegerField')(null=True))
        # Deleting field 'PerformanceInventory.ip_address'
        db.delete_column(u'performance_performanceinventory', 'ip_address')


        # Changing field 'PerformanceInventory.severity'
        db.alter_column(u'performance_performanceinventory', 'severity', self.gf('django.db.models.fields.IntegerField')(null=True))
        # Adding field 'EventMachine.status'
        db.add_column(u'performance_eventmachine', 'status',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.event_type'
        db.add_column(u'performance_eventmachine', 'event_type',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.state_type'
        db.add_column(u'performance_eventmachine', 'state_type',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.host'
        db.add_column(u'performance_eventmachine', 'host',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.device_type'
        db.add_column(u'performance_eventmachine', 'device_type',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.event_description'
        db.add_column(u'performance_eventmachine', 'event_description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.service'
        db.add_column(u'performance_eventmachine', 'service',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EventMachine.time'
        db.add_column(u'performance_eventmachine', 'time',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'EventMachine.device_name'
        db.delete_column(u'performance_eventmachine', 'device_name')

        # Deleting field 'EventMachine.service_name'
        db.delete_column(u'performance_eventmachine', 'service_name')

        # Deleting field 'EventMachine.machine_name'
        db.delete_column(u'performance_eventmachine', 'machine_name')

        # Deleting field 'EventMachine.data_source'
        db.delete_column(u'performance_eventmachine', 'data_source')

        # Deleting field 'EventMachine.severity'
        db.delete_column(u'performance_eventmachine', 'severity')

        # Deleting field 'EventMachine.current_value'
        db.delete_column(u'performance_eventmachine', 'current_value')

        # Deleting field 'EventMachine.min_value'
        db.delete_column(u'performance_eventmachine', 'min_value')

        # Deleting field 'EventMachine.max_value'
        db.delete_column(u'performance_eventmachine', 'max_value')

        # Deleting field 'EventMachine.avg_value'
        db.delete_column(u'performance_eventmachine', 'avg_value')

        # Deleting field 'EventMachine.warning_threshold'
        db.delete_column(u'performance_eventmachine', 'warning_threshold')

        # Deleting field 'EventMachine.critical_threshold'
        db.delete_column(u'performance_eventmachine', 'critical_threshold')

        # Deleting field 'EventMachine.sys_timestamp'
        db.delete_column(u'performance_eventmachine', 'sys_timestamp')

        # Deleting field 'EventMachine.check_timestamp'
        db.delete_column(u'performance_eventmachine', 'check_timestamp')

        # Deleting field 'EventMachine.description'
        db.delete_column(u'performance_eventmachine', 'description')


        # Changing field 'EventMachine.site_name'
        db.alter_column(u'performance_eventmachine', 'site_name', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

    models = {
        u'performance.eventinventory': {
            'Meta': {'object_name': 'EventInventory'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.eventmachine': {
            'Meta': {'object_name': 'EventMachine'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.eventnetwork': {
            'Meta': {'object_name': 'EventNetwork'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.eventservice': {
            'Meta': {'object_name': 'EventService'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.eventstatus': {
            'Meta': {'object_name': 'EventStatus'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performanceinventory': {
            'Meta': {'object_name': 'PerformanceInventory'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performancemachine': {
            'Meta': {'object_name': 'PerformanceMachine'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performancemetric': {
            'Meta': {'object_name': 'PerformanceMetric'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performancenetwork': {
            'Meta': {'object_name': 'PerformanceNetwork'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performanceservice': {
            'Meta': {'object_name': 'PerformanceService'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performancestatus': {
            'Meta': {'object_name': 'PerformanceStatus'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['performance']