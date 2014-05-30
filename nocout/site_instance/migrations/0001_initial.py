# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SiteInstance'
        db.create_table(u'site_instance_siteinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('site_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('agent_port', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('live_status_tcp_port', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'site_instance', ['SiteInstance'])


    def backwards(self, orm):
        # Deleting model 'SiteInstance'
        db.delete_table(u'site_instance_siteinstance')


    models = {
        u'site_instance.siteinstance': {
            'Meta': {'object_name': 'SiteInstance'},
            'agent_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'live_status_tcp_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'site_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['site_instance']