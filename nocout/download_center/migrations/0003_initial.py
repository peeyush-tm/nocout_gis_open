# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProcessedReportDetails'
        db.create_table(u'download_center_processedreportdetails', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('report_path', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('orgnization_id', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal(u'download_center', ['ProcessedReportDetails'])

        # Adding model 'ReportSettings'
        db.create_table(u'download_center_reportsettings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('report_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('report_frequency', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'download_center', ['ReportSettings'])


    def backwards(self, orm):
        # Deleting model 'ProcessedReportDetails'
        db.delete_table(u'download_center_processedreportdetails')

        # Deleting model 'ReportSettings'
        db.delete_table(u'download_center_reportsettings')


    models = {
        u'download_center.processedreportdetails': {
            'Meta': {'object_name': 'ProcessedReportDetails'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orgnization_id': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'report_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'report_path': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'download_center.reportsettings': {
            'Meta': {'object_name': 'ReportSettings'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'report_frequency': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'report_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['download_center']