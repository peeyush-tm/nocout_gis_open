# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ServiceParameters'
        db.create_table(u'service_serviceparameters', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parameter_description', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('max_check_attempts', self.gf('django.db.models.fields.IntegerField')()),
            ('check_interval', self.gf('django.db.models.fields.IntegerField')()),
            ('retry_interval', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('check_period', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('notification_interval', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('notification_period', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'service', ['ServiceParameters'])

        # Adding model 'Service'
        db.create_table(u'service_service', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('command', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['command.Command'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'service', ['Service'])

        # Adding M2M table for field parameters on 'Service'
        m2m_table_name = db.shorten_name(u'service_service_parameters')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('service', models.ForeignKey(orm[u'service.service'], null=False)),
            ('serviceparameters', models.ForeignKey(orm[u'service.serviceparameters'], null=False))
        ))
        db.create_unique(m2m_table_name, ['service_id', 'serviceparameters_id'])


    def backwards(self, orm):
        # Deleting model 'ServiceParameters'
        db.delete_table(u'service_serviceparameters')

        # Deleting model 'Service'
        db.delete_table(u'service_service')

        # Removing M2M table for field parameters on 'Service'
        db.delete_table(db.shorten_name(u'service_service_parameters'))


    models = {
        u'command.command': {
            'Meta': {'object_name': 'Command'},
            'command_line': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'service.service': {
            'Meta': {'object_name': 'Service'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['command.Command']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.ServiceParameters']", 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'service.serviceparameters': {
            'Meta': {'object_name': 'ServiceParameters'},
            'check_interval': ('django.db.models.fields.IntegerField', [], {}),
            'check_period': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_check_attempts': ('django.db.models.fields.IntegerField', [], {}),
            'notification_interval': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'notification_period': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parameter_description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'retry_interval': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['service']