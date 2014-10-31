# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ProcessedReportDetails.orgnization_id'
        db.delete_column(u'download_center_processedreportdetails', 'orgnization_id')

        # Adding field 'ProcessedReportDetails.organization_id'
        db.add_column(u'download_center_processedreportdetails', 'organization_id',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'ProcessedReportDetails.orgnization_id'
        db.add_column(u'download_center_processedreportdetails', 'orgnization_id',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Deleting field 'ProcessedReportDetails.organization_id'
        db.delete_column(u'download_center_processedreportdetails', 'organization_id')


    models = {
        u'download_center.processedreportdetails': {
            'Meta': {'object_name': 'ProcessedReportDetails'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization_id': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'report_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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