# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Organization'
        db.delete_table(u'organization_organization')

        # Removing M2M table for field device_group on 'Organization'
        db.delete_table(db.shorten_name(u'organization_organization_device_group'))


    def backwards(self, orm):
        # Adding model 'Organization'
        db.create_table(u'organization_organization', (
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_group.UserGroup'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('created_by', self.gf('django.db.models.fields.IntegerField')()),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'organization', ['Organization'])

        # Adding M2M table for field device_group on 'Organization'
        m2m_table_name = db.shorten_name(u'organization_organization_device_group')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organization', models.ForeignKey(orm[u'organization.organization'], null=False)),
            ('devicegroup', models.ForeignKey(orm[u'device_group.devicegroup'], null=False))
        ))
        db.create_unique(m2m_table_name, ['organization_id', 'devicegroup_id'])


    models = {
        
    }

    complete_apps = ['organization']