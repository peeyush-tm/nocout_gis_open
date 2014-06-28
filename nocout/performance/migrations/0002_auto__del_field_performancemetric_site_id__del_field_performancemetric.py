# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'PerformanceMetric.site_id'
        db.delete_column(u'performance_performancemetric', 'site_id')

        # Deleting field 'PerformanceMetric.machine_id'
        db.delete_column(u'performance_performancemetric', 'machine_id')

        # Adding field 'PerformanceMetric.machine_name'
        db.add_column(u'performance_performancemetric', 'machine_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True),
                      keep_default=False)

        # Adding field 'PerformanceMetric.site_name'
        db.add_column(u'performance_performancemetric', 'site_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True),
                      keep_default=False)


        # Changing field 'PerformanceMetric.check_timestamp'
        db.alter_column(u'performance_performancemetric', 'check_timestamp', self.gf('django.db.models.fields.BigIntegerField')(null=True))

        # Changing field 'PerformanceMetric.sys_timestamp'
        db.alter_column(u'performance_performancemetric', 'sys_timestamp', self.gf('django.db.models.fields.BigIntegerField')(null=True))

    def backwards(self, orm):
        # Adding field 'PerformanceMetric.site_id'
        db.add_column(u'performance_performancemetric', 'site_id',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'PerformanceMetric.machine_id'
        db.add_column(u'performance_performancemetric', 'machine_id',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Deleting field 'PerformanceMetric.machine_name'
        db.delete_column(u'performance_performancemetric', 'machine_name')

        # Deleting field 'PerformanceMetric.site_name'
        db.delete_column(u'performance_performancemetric', 'site_name')


        # Changing field 'PerformanceMetric.check_timestamp'
        db.alter_column(u'performance_performancemetric', 'check_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'PerformanceMetric.sys_timestamp'
        db.alter_column(u'performance_performancemetric', 'sys_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True))

    models = {
        u'performance.performancemetric': {
            'Meta': {'object_name': 'PerformanceMetric'},
            'avg_value': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'check_timestamp': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'current_value': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'min_value': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'sys_timestamp': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'})
        }
    }

    complete_apps = ['performance']