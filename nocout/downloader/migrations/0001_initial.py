# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Downloader'
        db.create_table(u'downloader_downloader', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_path', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('app_name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('view_name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('downloaded_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('requested_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('request_completion_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'downloader', ['Downloader'])


    def backwards(self, orm):
        # Deleting model 'Downloader'
        db.delete_table(u'downloader_downloader')


    models = {
        u'downloader.downloader': {
            'Meta': {'object_name': 'Downloader'},
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'downloaded_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'file_path': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request_completion_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'requested_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'view_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['downloader']