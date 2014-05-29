# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ServiceGroup'
        db.create_table(u'service_group_servicegroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('servicegroup_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('notes_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('action_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'service_group', ['ServiceGroup'])

        # Adding M2M table for field service on 'ServiceGroup'
        m2m_table_name = db.shorten_name(u'service_group_servicegroup_service')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('servicegroup', models.ForeignKey(orm[u'service_group.servicegroup'], null=False)),
            ('service', models.ForeignKey(orm[u'service.service'], null=False))
        ))
        db.create_unique(m2m_table_name, ['servicegroup_id', 'service_id'])


    def backwards(self, orm):
        # Deleting model 'ServiceGroup'
        db.delete_table(u'service_group_servicegroup')

        # Removing M2M table for field service on 'ServiceGroup'
        db.delete_table(db.shorten_name(u'service_group_servicegroup_service'))


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
        },
        u'service_group.servicegroup': {
            'Meta': {'object_name': 'ServiceGroup'},
            'action_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'notes_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.Service']", 'null': 'True', 'blank': 'True'}),
            'servicegroup_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['service_group']