# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'AlarmEscalation'
        db.delete_table(u'alarm_escalation_alarmescalation')

        # Removing M2M table for field level on 'AlarmEscalation'
        db.delete_table(db.shorten_name(u'alarm_escalation_alarmescalation_level'))

        # Adding model 'EscalationStatus'
        db.create_table(u'alarm_escalation_escalationstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['organization.Organization'])),
            ('device_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceType'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service.Service'])),
            ('service_data_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service.ServiceDataSource'])),
            ('technology', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceTechnology'])),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('l1_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l1_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l2_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l2_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l3_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l3_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l4_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l4_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l5_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l5_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l6_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l6_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l7_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l7_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('alert_description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('status_since', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('old_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('new_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'alarm_escalation', ['EscalationStatus'])


    def backwards(self, orm):
        # Adding model 'AlarmEscalation'
        db.create_table(u'alarm_escalation_alarmescalation', (
            ('l7_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l5_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('l2_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l4_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status_since', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('technology', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceTechnology'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('l2_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l6_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l3_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l7_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('base_station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.BaseStation'])),
            ('l1_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l5_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l6_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l1_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l4_email_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('l3_phone_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('alert_description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal(u'alarm_escalation', ['AlarmEscalation'])

        # Adding M2M table for field level on 'AlarmEscalation'
        m2m_table_name = db.shorten_name(u'alarm_escalation_alarmescalation_level')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('alarmescalation', models.ForeignKey(orm[u'alarm_escalation.alarmescalation'], null=False)),
            ('escalationlevel', models.ForeignKey(orm[u'alarm_escalation.escalationlevel'], null=False))
        ))
        db.create_unique(m2m_table_name, ['alarmescalation_id', 'escalationlevel_id'])

        # Deleting model 'EscalationStatus'
        db.delete_table(u'alarm_escalation_escalationstatus')


    models = {
        u'alarm_escalation.escalationlevel': {
            'Meta': {'object_name': 'EscalationLevel'},
            'alarm_age': ('django.db.models.fields.IntegerField', [], {}),
            'device_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceType']"}),
            'emails': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organization.Organization']"}),
            'phones': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'region_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.Service']"}),
            'service_data_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.ServiceDataSource']"})
        },
        u'alarm_escalation.escalationstatus': {
            'Meta': {'object_name': 'EscalationStatus'},
            'alert_description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'device_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'l1_email_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l1_phone_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l2_email_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l2_phone_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l3_email_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l3_phone_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l4_email_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l4_phone_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l5_email_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l5_phone_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l6_email_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l6_phone_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l7_email_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'l7_phone_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'new_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'old_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organization.Organization']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.Service']"}),
            'service_data_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.ServiceDataSource']"}),
            'status_since': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'technology': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceTechnology']"})
        },
        u'command.command': {
            'Meta': {'object_name': 'Command'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command_line': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'device.devicemodel': {
            'Meta': {'object_name': 'DeviceModel'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'device_types': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['device.DeviceType']", 'null': 'True', 'through': u"orm['device.ModelType']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'device.deviceport': {
            'Meta': {'object_name': 'DevicePort'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'device.devicetechnology': {
            'Meta': {'object_name': 'DeviceTechnology'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'device_vendors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['device.DeviceVendor']", 'null': 'True', 'through': u"orm['device.TechnologyVendor']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'device.devicetype': {
            'Meta': {'object_name': 'DeviceType'},
            'agent_tag': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'device_gmap_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'device_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'device_port': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['device.DevicePort']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'normal_check_interval': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'packets': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pl_critical': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pl_warning': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rta_critical': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rta_warning': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.Service']", 'null': 'True', 'through': u"orm['device.DeviceTypeService']", 'blank': 'True'}),
            'timeout': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'device.devicetypeservice': {
            'Meta': {'object_name': 'DeviceTypeService'},
            'device_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.ServiceParameters']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.Service']"}),
            'service_data_sources': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['service.ServiceDataSource']", 'through': u"orm['device.DeviceTypeServiceDataSource']", 'symmetrical': 'False'})
        },
        u'device.devicetypeservicedatasource': {
            'Meta': {'object_name': 'DeviceTypeServiceDataSource'},
            'critical': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_type_service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceTypeService']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service_data_sources': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.ServiceDataSource']"}),
            'warning': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'device.devicevendor': {
            'Meta': {'object_name': 'DeviceVendor'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'device_models': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['device.DeviceModel']", 'null': 'True', 'through': u"orm['device.VendorModel']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'device.modeltype': {
            'Meta': {'object_name': 'ModelType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceModel']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceType']"})
        },
        u'device.technologyvendor': {
            'Meta': {'object_name': 'TechnologyVendor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'technology': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceTechnology']"}),
            'vendor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceVendor']"})
        },
        u'device.vendormodel': {
            'Meta': {'object_name': 'VendorModel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceModel']"}),
            'vendor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceVendor']"})
        },
        u'organization.organization': {
            'Meta': {'object_name': 'Organization'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'organization_children'", 'null': 'True', 'to': u"orm['organization.Organization']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'service.protocol': {
            'Meta': {'object_name': 'Protocol'},
            'auth_password': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'auth_protocol': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'private_pass_phase': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'private_phase': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'protocol_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'read_community': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'security_level': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'security_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'write_community': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'service.service': {
            'Meta': {'object_name': 'Service'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['command.Command']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parameters': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.ServiceParameters']"}),
            'service_data_sources': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['service.ServiceDataSource']", 'through': u"orm['service.ServiceSpecificDataSource']", 'symmetrical': 'False'})
        },
        u'service.servicedatasource': {
            'Meta': {'object_name': 'ServiceDataSource'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'critical': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'warning': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'service.serviceparameters': {
            'Meta': {'object_name': 'ServiceParameters'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_check_attempts': ('django.db.models.fields.IntegerField', [], {}),
            'normal_check_interval': ('django.db.models.fields.IntegerField', [], {}),
            'parameter_description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'protocol': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.Protocol']"}),
            'retry_check_interval': ('django.db.models.fields.IntegerField', [], {})
        },
        u'service.servicespecificdatasource': {
            'Meta': {'object_name': 'ServiceSpecificDataSource'},
            'critical': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.Service']"}),
            'service_data_sources': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.ServiceDataSource']"}),
            'warning': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['alarm_escalation']