# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PerformanceMetric.severity'
        db.add_column(u'performance_performancemetric', 'severity',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


        # Changing field 'PerformanceMetric.critical_threshold'
        db.alter_column(u'performance_performancemetric', 'critical_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'PerformanceMetric.avg_value'
        db.alter_column(u'performance_performancemetric', 'avg_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'PerformanceMetric.max_value'
        db.alter_column(u'performance_performancemetric', 'max_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'PerformanceMetric.min_value'
        db.alter_column(u'performance_performancemetric', 'min_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'PerformanceMetric.current_value'
        db.alter_column(u'performance_performancemetric', 'current_value', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'PerformanceMetric.warning_threshold'
        db.alter_column(u'performance_performancemetric', 'warning_threshold', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

    def backwards(self, orm):
        # Deleting field 'PerformanceMetric.severity'
        db.delete_column(u'performance_performancemetric', 'severity')


        # Changing field 'PerformanceMetric.critical_threshold'
        db.alter_column(u'performance_performancemetric', 'critical_threshold', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'PerformanceMetric.avg_value'
        db.alter_column(u'performance_performancemetric', 'avg_value', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'PerformanceMetric.max_value'
        db.alter_column(u'performance_performancemetric', 'max_value', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'PerformanceMetric.min_value'
        db.alter_column(u'performance_performancemetric', 'min_value', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'PerformanceMetric.current_value'
        db.alter_column(u'performance_performancemetric', 'current_value', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'PerformanceMetric.warning_threshold'
        db.alter_column(u'performance_performancemetric', 'warning_threshold', self.gf('django.db.models.fields.CharField')(max_length=20))

    models = {
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