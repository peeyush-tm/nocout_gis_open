# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Country'
        db.create_table(u'device_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'device', ['Country'])

        # Adding model 'State'
        db.create_table(u'device_state', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.Country'], null=True, blank=True)),
        ))
        db.send_create_signal(u'device', ['State'])

        # Adding model 'City'
        db.create_table(u'device_city', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.State'], null=True, blank=True)),
        ))
        db.send_create_signal(u'device', ['City'])

        # Adding model 'StateGeoInfo'
        db.create_table(u'device_stategeoinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.State'])),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'device', ['StateGeoInfo'])

        # Adding model 'DeviceFrequency'
        db.create_table(u'device_devicefrequency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('color_hex_value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'device', ['DeviceFrequency'])

        # Adding model 'DevicePort'
        db.create_table(u'device_deviceport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'device', ['DevicePort'])

        # Adding model 'DeviceType'
        db.create_table(u'device_devicetype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('device_icon', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('device_gmap_icon', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('agent_tag', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'device', ['DeviceType'])

        # Adding M2M table for field device_port on 'DeviceType'
        m2m_table_name = db.shorten_name(u'device_devicetype_device_port')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('devicetype', models.ForeignKey(orm[u'device.devicetype'], null=False)),
            ('deviceport', models.ForeignKey(orm[u'device.deviceport'], null=False))
        ))
        db.create_unique(m2m_table_name, ['devicetype_id', 'deviceport_id'])

        # Adding M2M table for field service on 'DeviceType'
        m2m_table_name = db.shorten_name(u'device_devicetype_service')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('devicetype', models.ForeignKey(orm[u'device.devicetype'], null=False)),
            ('service', models.ForeignKey(orm[u'service.service'], null=False))
        ))
        db.create_unique(m2m_table_name, ['devicetype_id', 'service_id'])

        # Adding model 'DeviceModel'
        db.create_table(u'device_devicemodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'device', ['DeviceModel'])

        # Adding model 'DeviceVendor'
        db.create_table(u'device_devicevendor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'device', ['DeviceVendor'])

        # Adding model 'DeviceTechnology'
        db.create_table(u'device_devicetechnology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'device', ['DeviceTechnology'])

        # Adding model 'Device'
        db.create_table(u'device_device', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('device_alias', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('site_instance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['site_instance.SiteInstance'], null=True, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['organization.Organization'])),
            ('device_technology', self.gf('django.db.models.fields.IntegerField')()),
            ('device_vendor', self.gf('django.db.models.fields.IntegerField')()),
            ('device_model', self.gf('django.db.models.fields.IntegerField')()),
            ('device_type', self.gf('django.db.models.fields.IntegerField')()),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='device_children', null=True, to=orm['device.Device'])),
            ('machine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machine.Machine'], null=True, blank=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(unique=True, max_length=15)),
            ('mac_address', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('netmask', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('gateway', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('dhcp_state', self.gf('django.db.models.fields.CharField')(default='Disable', max_length=200)),
            ('host_priority', self.gf('django.db.models.fields.CharField')(default='Normal', max_length=200)),
            ('host_state', self.gf('django.db.models.fields.CharField')(default='Enable', max_length=200)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('timezone', self.gf('django.db.models.fields.CharField')(default='Asia/Kolkata', max_length=100)),
            ('country', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('is_deleted', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('is_added_to_nms', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('is_monitored_on_nms', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'device', ['Device'])

        # Adding model 'ModelType'
        db.create_table(u'device_modeltype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceModel'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceType'])),
        ))
        db.send_create_signal(u'device', ['ModelType'])

        # Adding model 'VendorModel'
        db.create_table(u'device_vendormodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vendor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceVendor'])),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceModel'])),
        ))
        db.send_create_signal(u'device', ['VendorModel'])

        # Adding model 'TechnologyVendor'
        db.create_table(u'device_technologyvendor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('technology', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceTechnology'])),
            ('vendor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceVendor'])),
        ))
        db.send_create_signal(u'device', ['TechnologyVendor'])

        # Adding model 'DeviceTypeFields'
        db.create_table(u'device_devicetypefields', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('field_display_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('device_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceType'])),
        ))
        db.send_create_signal(u'device', ['DeviceTypeFields'])

        # Adding model 'DeviceTypeFieldsValue'
        db.create_table(u'device_devicetypefieldsvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_type_field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.DeviceTypeFields'])),
            ('field_value', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('device_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'device', ['DeviceTypeFieldsValue'])


    def backwards(self, orm):
        # Deleting model 'Country'
        db.delete_table(u'device_country')

        # Deleting model 'State'
        db.delete_table(u'device_state')

        # Deleting model 'City'
        db.delete_table(u'device_city')

        # Deleting model 'StateGeoInfo'
        db.delete_table(u'device_stategeoinfo')

        # Deleting model 'DeviceFrequency'
        db.delete_table(u'device_devicefrequency')

        # Deleting model 'DevicePort'
        db.delete_table(u'device_deviceport')

        # Deleting model 'DeviceType'
        db.delete_table(u'device_devicetype')

        # Removing M2M table for field device_port on 'DeviceType'
        db.delete_table(db.shorten_name(u'device_devicetype_device_port'))

        # Removing M2M table for field service on 'DeviceType'
        db.delete_table(db.shorten_name(u'device_devicetype_service'))

        # Deleting model 'DeviceModel'
        db.delete_table(u'device_devicemodel')

        # Deleting model 'DeviceVendor'
        db.delete_table(u'device_devicevendor')

        # Deleting model 'DeviceTechnology'
        db.delete_table(u'device_devicetechnology')

        # Deleting model 'Device'
        db.delete_table(u'device_device')

        # Deleting model 'ModelType'
        db.delete_table(u'device_modeltype')

        # Deleting model 'VendorModel'
        db.delete_table(u'device_vendormodel')

        # Deleting model 'TechnologyVendor'
        db.delete_table(u'device_technologyvendor')

        # Deleting model 'DeviceTypeFields'
        db.delete_table(u'device_devicetypefields')

        # Deleting model 'DeviceTypeFieldsValue'
        db.delete_table(u'device_devicetypefieldsvalue')


    models = {
        u'command.command': {
            'Meta': {'object_name': 'Command'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command_line': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'device.city': {
            'Meta': {'object_name': 'City'},
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.State']", 'null': 'True', 'blank': 'True'})
        },
        u'device.country': {
            'Meta': {'object_name': 'Country'},
            'country_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'device.device': {
            'Meta': {'object_name': 'Device'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'device_alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'device_model': ('django.db.models.fields.IntegerField', [], {}),
            'device_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'device_technology': ('django.db.models.fields.IntegerField', [], {}),
            'device_type': ('django.db.models.fields.IntegerField', [], {}),
            'device_vendor': ('django.db.models.fields.IntegerField', [], {}),
            'dhcp_state': ('django.db.models.fields.CharField', [], {'default': "'Disable'", 'max_length': '200'}),
            'gateway': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'host_priority': ('django.db.models.fields.CharField', [], {'default': "'Normal'", 'max_length': '200'}),
            'host_state': ('django.db.models.fields.CharField', [], {'default': "'Enable'", 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'}),
            'is_added_to_nms': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'is_monitored_on_nms': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'mac_address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['machine.Machine']", 'null': 'True', 'blank': 'True'}),
            'netmask': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organization.Organization']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'device_children'", 'null': 'True', 'to': u"orm['device.Device']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'site_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['site_instance.SiteInstance']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'Asia/Kolkata'", 'max_length': '100'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'device.devicefrequency': {
            'Meta': {'object_name': 'DeviceFrequency'},
            'color_hex_value': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'device_gmap_icon': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'device_icon': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'device_port': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['device.DevicePort']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'service': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.Service']", 'null': 'True', 'blank': 'True'})
        },
        u'device.devicetypefields': {
            'Meta': {'object_name': 'DeviceTypeFields'},
            'device_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceType']"}),
            'field_display_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'device.devicetypefieldsvalue': {
            'Meta': {'object_name': 'DeviceTypeFieldsValue'},
            'device_id': ('django.db.models.fields.IntegerField', [], {}),
            'device_type_field': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.DeviceTypeFields']"}),
            'field_value': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        u'device.state': {
            'Meta': {'object_name': 'State'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Country']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'device.stategeoinfo': {
            'Meta': {'object_name': 'StateGeoInfo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.State']"})
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
        u'machine.machine': {
            'Meta': {'object_name': 'Machine'},
            'agent_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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
            'service_data_sources': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['service.ServiceDataSource']", 'symmetrical': 'False'})
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
        u'site_instance.siteinstance': {
            'Meta': {'object_name': 'SiteInstance'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'live_status_tcp_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['machine.Machine']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'web_service_port': ('django.db.models.fields.IntegerField', [], {'default': '80'})
        }
    }

    complete_apps = ['device']