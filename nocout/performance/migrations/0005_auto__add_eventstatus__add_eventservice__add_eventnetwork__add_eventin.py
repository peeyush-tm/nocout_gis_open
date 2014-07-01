# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EventStatus'
        db.create_table(u'performance_eventstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('machine_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('data_source', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('severity', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('current_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('min_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('max_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('avg_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('warning_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('critical_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('sys_timestamp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('check_timestamp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'performance', ['EventStatus'])

        # Adding model 'EventService'
        db.create_table(u'performance_eventservice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('machine_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('data_source', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('severity', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('current_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('min_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('max_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('avg_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('warning_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('critical_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('sys_timestamp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('check_timestamp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'performance', ['EventService'])

        # Adding model 'EventNetwork'
        db.create_table(u'performance_eventnetwork', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('machine_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('data_source', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('severity', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('current_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('min_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('max_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('avg_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('warning_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('critical_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('sys_timestamp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('check_timestamp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'performance', ['EventNetwork'])

        # Adding model 'EventInventory'
        db.create_table(u'performance_eventinventory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('machine_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('data_source', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('severity', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('current_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('min_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('max_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('avg_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('warning_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('critical_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('sys_timestamp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('check_timestamp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'performance', ['EventInventory'])

        # Adding model 'EventMachine'
        db.create_table(u'performance_eventmachine', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('machine_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('site_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('data_source', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('severity', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('current_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('min_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('max_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('avg_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('warning_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('critical_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('sys_timestamp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('check_timestamp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'performance', ['EventMachine'])


    def backwards(self, orm):
        # Deleting model 'EventStatus'
        db.delete_table(u'performance_eventstatus')

        # Deleting model 'EventService'
        db.delete_table(u'performance_eventservice')

        # Deleting model 'EventNetwork'
        db.delete_table(u'performance_eventnetwork')

        # Deleting model 'EventInventory'
        db.delete_table(u'performance_eventinventory')

        # Deleting model 'EventMachine'
        db.delete_table(u'performance_eventmachine')


    models = {
        u'performance.eventinventory': {
            'Meta': {'object_name': 'EventInventory'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['performance']