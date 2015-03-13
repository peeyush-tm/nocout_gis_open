# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'EscalationStatus.device_type'
        db.alter_column(u'alarm_escalation_escalationstatus', 'device_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))
        # Removing index on 'EscalationStatus', fields ['device_type']
        db.delete_index(u'alarm_escalation_escalationstatus', ['device_type'])


        # Changing field 'EscalationStatus.service'
        db.alter_column(u'alarm_escalation_escalationstatus', 'service', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))
        # Removing index on 'EscalationStatus', fields ['service']
        db.delete_index(u'alarm_escalation_escalationstatus', ['service'])


        # Changing field 'EscalationStatus.service_data_source'
        db.alter_column(u'alarm_escalation_escalationstatus', 'service_data_source', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))
        # Removing index on 'EscalationStatus', fields ['service_data_source']
        db.delete_index(u'alarm_escalation_escalationstatus', ['service_data_source'])


        # Changing field 'EscalationStatus.device_name'
        db.alter_column(u'alarm_escalation_escalationstatus', 'device_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))
        # Removing index on 'EscalationStatus', fields ['device_name']
        db.delete_index(u'alarm_escalation_escalationstatus', ['device_name'])

        # Deleting field 'EscalationStatus.device_type'
        db.delete_column(u'alarm_escalation_escalationstatus', 'device_type')

        # Deleting field 'EscalationStatus.device_name'
        db.delete_column(u'alarm_escalation_escalationstatus', 'device_name')

        # Deleting field 'EscalationStatus.device_type'
        db.delete_column(u'alarm_escalation_escalationstatus', 'service')

        # Deleting field 'EscalationStatus.device_name'
        db.delete_column(u'alarm_escalation_escalationstatus', 'service_data_source')

    def backwards(self, orm):

        # Deleting field 'EscalationStatus.device_type'
        # db.add_column(u'alarm_escalation_escalationstatus', 'device_type')

        # Deleting field 'EscalationStatus.device_name'
        # db.add_column(u'alarm_escalation_escalationstatus', 'device_name')

        # Deleting field 'EscalationStatus.device_type'
        # db.add_column(u'alarm_escalation_escalationstatus', 'service')

        # Deleting field 'EscalationStatus.device_name'
        # db.add_column(u'alarm_escalation_escalationstatus', 'service_data_source')

        # Adding index on 'EscalationStatus', fields ['device_name']
        db.create_index(u'alarm_escalation_escalationstatus', ['device_name'])

        # Adding index on 'EscalationStatus', fields ['service_data_source']
        db.create_index(u'alarm_escalation_escalationstatus', ['service_data_source'])

        # Adding index on 'EscalationStatus', fields ['service']
        db.create_index(u'alarm_escalation_escalationstatus', ['service'])

        # Adding index on 'EscalationStatus', fields ['device_type']
        db.create_index(u'alarm_escalation_escalationstatus', ['device_type'])


        # User chose to not deal with backwards NULL issues for 'EscalationStatus.device_type'
        raise RuntimeError("Cannot reverse this migration. 'EscalationStatus.device_type' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'EscalationStatus.device_type'
        # db.alter_column(u'alarm_escalation_escalationstatus', 'device_type', self.gf('django.db.models.fields.CharField')(max_length=100))

        # User chose to not deal with backwards NULL issues for 'EscalationStatus.service'
        raise RuntimeError("Cannot reverse this migration. 'EscalationStatus.service' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'EscalationStatus.service'
        # db.alter_column(u'alarm_escalation_escalationstatus', 'service', self.gf('django.db.models.fields.CharField')(max_length=100))

        # User chose to not deal with backwards NULL issues for 'EscalationStatus.service_data_source'
        raise RuntimeError("Cannot reverse this migration. 'EscalationStatus.service_data_source' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'EscalationStatus.service_data_source'
        # db.alter_column(u'alarm_escalation_escalationstatus', 'service_data_source', self.gf('django.db.models.fields.CharField')(max_length=100))

        # User chose to not deal with backwards NULL issues for 'EscalationStatus.device_name'
        raise RuntimeError("Cannot reverse this migration. 'EscalationStatus.device_name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'EscalationStatus.device_name'
        # db.alter_column(u'alarm_escalation_escalationstatus', 'device_name', self.gf('django.db.models.fields.CharField')(max_length=100))

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
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
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
            'new_status': ('django.db.models.fields.IntegerField', [], {}),
            'old_status': ('django.db.models.fields.IntegerField', [], {}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organization.Organization']"}),
            'service': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'service_data_source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'status_since': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'command.command': {
            'Meta': {'object_name': 'Command'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command_line': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
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
            'chart_color': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'chart_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'critical': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'data_source_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'formula': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_inverted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'show_gis': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_max': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_min': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_performance_center': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'valuesuffix': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'valuetext': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
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