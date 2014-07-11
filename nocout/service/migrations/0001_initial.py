# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Protocol'
        db.create_table(u'service_protocol', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('protocol_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('port', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('read_community', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('write_community', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('auth_password', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('auth_protocol', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('security_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('security_level', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('private_phase', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('private_pass_phase', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'service', ['Protocol'])

        # Adding model 'ServiceDataSource'
        db.create_table(u'service_servicedatasource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('warning', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('critical', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'service', ['ServiceDataSource'])

        # Adding model 'ServiceParameters'
        db.create_table(u'service_serviceparameters', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parameter_description', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('protocol', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service.Protocol'], null=True, blank=True)),
            ('normal_check_interval', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('retry_check_interval', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max_check_attempts', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'service', ['ServiceParameters'])

        # Adding model 'Service'
        db.create_table(u'service_service', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('parameters', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service.ServiceParameters'], null=True, blank=True)),
            ('command', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['command.Command'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'service', ['Service'])

        # Adding M2M table for field service_data_sources on 'Service'
        m2m_table_name = db.shorten_name(u'service_service_service_data_sources')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('service', models.ForeignKey(orm[u'service.service'], null=False)),
            ('servicedatasource', models.ForeignKey(orm[u'service.servicedatasource'], null=False))
        ))
        db.create_unique(m2m_table_name, ['service_id', 'servicedatasource_id'])


    def backwards(self, orm):
        # Deleting model 'Protocol'
        db.delete_table(u'service_protocol')

        # Deleting model 'ServiceDataSource'
        db.delete_table(u'service_servicedatasource')

        # Deleting model 'ServiceParameters'
        db.delete_table(u'service_serviceparameters')

        # Deleting model 'Service'
        db.delete_table(u'service_service')

        # Removing M2M table for field service_data_sources on 'Service'
        db.delete_table(db.shorten_name(u'service_service_service_data_sources'))


    models = {
        u'command.command': {
            'Meta': {'object_name': 'Command'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command_line': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'service.protocol': {
            'Meta': {'object_name': 'Protocol'},
            'auth_password': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'auth_protocol': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'private_pass_phase': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'private_phase': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'protocol_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'read_community': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'security_level': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'security_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'write_community': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'service.service': {
            'Meta': {'object_name': 'Service'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['command.Command']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parameters': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.ServiceParameters']", 'null': 'True', 'blank': 'True'}),
            'service_data_sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.ServiceDataSource']", 'null': 'True', 'blank': 'True'})
        },
        u'service.servicedatasource': {
            'Meta': {'object_name': 'ServiceDataSource'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'critical': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'warning': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'service.serviceparameters': {
            'Meta': {'object_name': 'ServiceParameters'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_check_attempts': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'normal_check_interval': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parameter_description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'protocol': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.Protocol']", 'null': 'True', 'blank': 'True'}),
            'retry_check_interval': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['service']