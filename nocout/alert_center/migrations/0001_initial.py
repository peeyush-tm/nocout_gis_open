# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HistoryAlarms'
        db.create_table(u'alert_center_historyalarms', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('ip_address', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('device_type', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('device_technology', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('device_vendor', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('device_model', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('trapoid', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('eventname', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('eventno', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('severity', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('uptime', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('traptime', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=30, null=True, blank=True)),
            ('component_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal(u'alert_center', ['HistoryAlarms'])

        # Adding model 'ClearAlarms'
        db.create_table(u'alert_center_clearalarms', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('ip_address', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('device_type', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('device_technology', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('device_vendor', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('device_model', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('trapoid', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('eventname', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('eventno', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('severity', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('uptime', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('traptime', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=30, null=True, blank=True)),
            ('component_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal(u'alert_center', ['ClearAlarms'])

        # Adding model 'CurrentAlarms'
        db.create_table(u'alert_center_currentalarms', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('ip_address', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('device_type', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('device_technology', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('device_vendor', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('device_model', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('trapoid', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('eventname', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('eventno', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('severity', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('uptime', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('traptime', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=30, null=True, blank=True)),
            ('component_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal(u'alert_center', ['CurrentAlarms'])

    def backwards(self, orm):
        # Deleting model 'HistoryAlarms'
        db.delete_table(u'alert_center_historyalarms')

        # Deleting model 'ClearAlarms'
        db.delete_table(u'alert_center_clearalarms')

        # Deleting model 'CurrentAlarms'
        db.delete_table(u'alert_center_currentalarms')

    models = {
        u'alert_center.clearalarms': {
            'Meta': {'object_name': 'ClearAlarms', 'db_table': "'clear_alarms'", 'managed': 'False'},
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
            'Meta': {'object_name': 'CurrentAlarms', 'db_table': "'current_alarms'", 'managed': 'False'},
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
            'Meta': {'object_name': 'HistoryAlarms', 'db_table': "'history_alarms'", 'managed': 'False'},
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