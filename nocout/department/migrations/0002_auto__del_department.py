# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Department'
        db.delete_table(u'department_department')

        # Removing M2M table for field users on 'Department'
        db.delete_table(db.shorten_name(u'department_department_users'))


    def backwards(self, orm):
        # Adding model 'Department'
        db.create_table(u'department_department', (
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_group.UserGroup'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('created_by', self.gf('django.db.models.fields.IntegerField')()),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'department', ['Department'])

        # Adding M2M table for field users on 'Department'
        m2m_table_name = db.shorten_name(u'department_department_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('department', models.ForeignKey(orm[u'department.department'], null=False)),
            ('userprofile', models.ForeignKey(orm[u'user_profile.userprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['department_id', 'userprofile_id'])


    models = {
        
    }

    complete_apps = ['department']