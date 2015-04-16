# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GISPointTool'
        db.create_table(u'devicevisualization_gispointtool', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('icon_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('connected_point_type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('connected_point_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('connected_lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('connected_lon', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'devicevisualization', ['GISPointTool'])


    def backwards(self, orm):
        # Deleting model 'GISPointTool'
        db.delete_table(u'devicevisualization_gispointtool')


    models = {
        u'devicevisualization.gispointtool': {
            'Meta': {'object_name': 'GISPointTool'},
            'connected_lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'connected_lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'connected_point_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'connected_point_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'icon_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['devicevisualization']