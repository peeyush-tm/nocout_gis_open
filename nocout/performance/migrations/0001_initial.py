# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PerformanceMetric'
        db.create_table(u'performance_performancemetric', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('machine_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('site_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('data_source', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('sys_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('check_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'performance', ['PerformanceMetric'])


    def backwards(self, orm):
        # Deleting model 'PerformanceMetric'
        db.delete_table(u'performance_performancemetric')


    models = {
        u'performance.performancemetric': {
            'Meta': {'object_name': 'PerformanceMetric'},
            'check_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'site_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['performance']