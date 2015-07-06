# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ClearAlarms.component_id'
        db.add_column(u'alert_center_clearalarms', 'component_id',
                      self.gf('django.db.models.fields.CharField')(default='NA', max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'CurrentAlarms.component_id'
        db.add_column(u'alert_center_currentalarms', 'component_id',
                      self.gf('django.db.models.fields.CharField')(default='NA', max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'HistoryAlarms.component_id'
        db.add_column(u'alert_center_historyalarms', 'component_id',
                      self.gf('django.db.models.fields.CharField')(default='NA', max_length=50, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ClearAlarms.component_id'
        db.delete_column(u'alert_center_clearalarms', 'component_id')

        # Deleting field 'CurrentAlarms.component_id'
        db.delete_column(u'alert_center_currentalarms', 'component_id')

        # Deleting field 'HistoryAlarms.component_id'
        db.delete_column(u'alert_center_historyalarms', 'component_id')


    models = {
        u'alert_center.clearalarms': {
            'Meta': {'object_name': 'ClearAlarms'},
            'component_id': ('django.db.models.fields.CharField', [], {'default': "'NA'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'component_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'device_model': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'device_technology': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_vendor': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'eventname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'eventno': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'trapoid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'traptime': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'uptime': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'alert_center.currentalarms': {
            'Meta': {'object_name': 'CurrentAlarms'},
            'component_id': ('django.db.models.fields.CharField', [], {'default': "'NA'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'component_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'device_model': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'device_technology': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_vendor': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'eventname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'eventno': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'trapoid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'traptime': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'uptime': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'alert_center.historyalarms': {
            'Meta': {'object_name': 'HistoryAlarms'},
            'component_id': ('django.db.models.fields.CharField', [], {'default': "'NA'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'component_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'device_model': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'device_technology': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_vendor': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'eventname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'eventno': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'trapoid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'traptime': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'uptime': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['alert_center']