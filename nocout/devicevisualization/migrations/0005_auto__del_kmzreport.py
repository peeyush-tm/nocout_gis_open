# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'KMZReport'
        db.delete_table(u'devicevisualization_kmzreport')


    def backwards(self, orm):
        # Adding model 'KMZReport'
        db.create_table(u'devicevisualization_kmzreport', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('filename', self.gf('django.db.models.fields.files.FileField')(max_length=300)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_profile.UserProfile'])),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'devicevisualization', ['KMZReport'])


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