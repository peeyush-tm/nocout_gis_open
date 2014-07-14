# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SiteInstance.web_service_port'
        db.add_column(u'site_instance_siteinstance', 'web_service_port',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'SiteInstance.username'
        db.add_column(u'site_instance_siteinstance', 'username',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True),
                      keep_default=False)

        # Adding field 'SiteInstance.password'
        db.add_column(u'site_instance_siteinstance', 'password',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SiteInstance.web_service_port'
        db.delete_column(u'site_instance_siteinstance', 'web_service_port')

        # Deleting field 'SiteInstance.username'
        db.delete_column(u'site_instance_siteinstance', 'username')

        # Deleting field 'SiteInstance.password'
        db.delete_column(u'site_instance_siteinstance', 'password')


    models = {
        u'machine.machine': {
            'Meta': {'object_name': 'Machine'},
            'agent_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'site_instance.siteinstance': {
            'Meta': {'object_name': 'SiteInstance'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'live_status_tcp_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['machine.Machine']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'site_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'web_service_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['site_instance']