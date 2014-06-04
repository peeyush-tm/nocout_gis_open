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
            ('device_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('machine_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('site_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('data_source', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('current_value', self.gf('django.db.models.fields.CharField')(default=0, max_length=20)),
            ('min_value', self.gf('django.db.models.fields.CharField')(default=0, max_length=20)),
            ('max_value', self.gf('django.db.models.fields.CharField')(default=0, max_length=20)),
            ('avg_value', self.gf('django.db.models.fields.CharField')(default=0, max_length=20)),
            ('warning_threshold', self.gf('django.db.models.fields.CharField')(default=0, max_length=20)),
            ('critical_threshold', self.gf('django.db.models.fields.CharField')(default=0, max_length=20)),
            ('sys_timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True)),
            ('check_timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True)),
        ))
        db.send_create_signal(u'performance', ['PerformanceMetric'])


    def backwards(self, orm):
        # Deleting model 'PerformanceMetric'
        db.delete_table(u'performance_performancemetric')


    models = {
        u'performance.performancemetric': {
            'Meta': {'object_name': 'PerformanceMetric'},
            'avg_value': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'check_timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'current_value': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'min_value': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'site_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'sys_timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '20'})
        }
    }

    complete_apps = ['performance']