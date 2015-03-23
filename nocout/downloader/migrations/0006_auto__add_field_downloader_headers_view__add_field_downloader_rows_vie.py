# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Downloader.headers_view'
        db.add_column(u'downloader_downloader', 'headers_view',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Downloader.rows_view'
        db.add_column(u'downloader_downloader', 'rows_view',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Downloader.headers_view'
        db.delete_column(u'downloader_downloader', 'headers_view')

        # Deleting field 'Downloader.rows_view'
        db.delete_column(u'downloader_downloader', 'rows_view')


    models = {
        u'downloader.downloader': {
            'Meta': {'object_name': 'Downloader'},
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'downloaded_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'file_path': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'headers_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'headers_view': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request_completion_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'requested_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rows_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rows_view': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['downloader']