# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Antenna'
        db.create_table(u'inventory_antenna', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('polarization', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('tilt', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('beam_width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('azimuth_angle', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('splitter_installed', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('sync_splitter_used', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('make_of_antenna', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Antenna'])

        # Adding model 'Backhaul'
        db.create_table(u'inventory_backhaul', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bh_configured_on', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='backhaul', null=True, to=orm['device.Device'])),
            ('bh_port', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('bh_type', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('pop', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='backhaul_pop', null=True, to=orm['device.Device'])),
            ('pop_port', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('aggregator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='backhaul_aggregator', null=True, to=orm['device.Device'])),
            ('aggregator_port', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pe_hostname', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('pe_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('bh_connectivity', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('bh_circuit_id', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('bh_capacity', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ttsl_circuit_id', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('dr_site', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Backhaul'])

        # Adding model 'BaseStation'
        db.create_table(u'inventory_basestation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bs_site_id', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('bs_site_name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('bs_switch', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='bs_switch', null=True, to=orm['device.Device'])),
            ('backhaul', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Backhaul'])),
            ('bs_type', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('infra_provider', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('building_height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('tower_height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('gps_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['BaseStation'])

        # Adding model 'Sector'
        db.create_table(u'inventory_sector', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sector_id', self.gf('django.db.models.fields.CharField')(max_length=250, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('base_station', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sector', to=orm['inventory.BaseStation'])),
            ('idu', self.gf('django.db.models.fields.related.ForeignKey')(max_length=250, related_name='sector_idu', null=True, to=orm['device.Device'])),
            ('idu_port', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('odu', self.gf('django.db.models.fields.related.ForeignKey')(max_length=250, related_name='sector_odu', null=True, blank=True, to=orm['device.Device'])),
            ('odu_port', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('antenna', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sector', null=True, to=orm['inventory.Antenna'])),
            ('mrc', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('tx_power', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('frequency', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('frame_length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('cell_radius', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Sector'])

        # Adding model 'Customer'
        db.create_table(u'inventory_customer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Customer'])

        # Adding model 'SubStation'
        db.create_table(u'inventory_substation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('serial_no', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('building_height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('tower_height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ethernet_extender', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['SubStation'])

        # Adding model 'Circuit'
        db.create_table(u'inventory_circuit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('circuit_id', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('sector', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Sector'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Customer'])),
            ('sub_station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.SubStation'])),
            ('date_of_acceptance', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Circuit'])


    def backwards(self, orm):
        # Deleting model 'Antenna'
        db.delete_table(u'inventory_antenna')

        # Deleting model 'Backhaul'
        db.delete_table(u'inventory_backhaul')

        # Deleting model 'BaseStation'
        db.delete_table(u'inventory_basestation')

        # Deleting model 'Sector'
        db.delete_table(u'inventory_sector')

        # Deleting model 'Customer'
        db.delete_table(u'inventory_customer')

        # Deleting model 'SubStation'
        db.delete_table(u'inventory_substation')

        # Deleting model 'Circuit'
        db.delete_table(u'inventory_circuit')


    models = {
        u'command.command': {
            'Meta': {'object_name': 'Command'},
            'command_line': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'device.device': {
            'Meta': {'object_name': 'Device'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'agent_tag': ('django.db.models.fields.CharField', [], {'default': "'ping'", 'max_length': '100'}),
            'city': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'device_alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'device_group': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['device_group.DeviceGroup']", 'null': 'True', 'through': u"orm['device.Inventory']", 'blank': 'True'}),
            'device_model': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'device_technology': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'device_vendor': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'dhcp_state': ('django.db.models.fields.CharField', [], {'default': "'Disable'", 'max_length': '200'}),
            'gateway': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'host_priority': ('django.db.models.fields.CharField', [], {'default': "'Normal'", 'max_length': '200'}),
            'host_state': ('django.db.models.fields.CharField', [], {'default': "'Enable'", 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'mac_address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'netmask': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'device_children'", 'null': 'True', 'to': u"orm['device.Device']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'service': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.Service']", 'null': 'True', 'blank': 'True'}),
            'site_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['site_instance.SiteInstance']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'Asia/Kolkata'", 'max_length': '100'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'device.inventory': {
            'Meta': {'object_name': 'Inventory'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Device']"}),
            'device_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device_group.DeviceGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'device_group.devicegroup': {
            'Meta': {'object_name': 'DeviceGroup'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'devicegroup_children'", 'null': 'True', 'to': u"orm['device_group.DeviceGroup']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'inventory.antenna': {
            'Meta': {'object_name': 'Antenna'},
            'azimuth_angle': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'beam_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'make_of_antenna': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'polarization': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'splitter_installed': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'sync_splitter_used': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'tilt': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'inventory.backhaul': {
            'Meta': {'object_name': 'Backhaul'},
            'aggregator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'backhaul_aggregator'", 'null': 'True', 'to': u"orm['device.Device']"}),
            'aggregator_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bh_capacity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bh_circuit_id': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'bh_configured_on': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'backhaul'", 'null': 'True', 'to': u"orm['device.Device']"}),
            'bh_connectivity': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'bh_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bh_type': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dr_site': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pe_hostname': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'pe_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'pop': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'backhaul_pop'", 'null': 'True', 'to': u"orm['device.Device']"}),
            'pop_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ttsl_circuit_id': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        },
        u'inventory.basestation': {
            'Meta': {'object_name': 'BaseStation'},
            'backhaul': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Backhaul']"}),
            'bs_site_id': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'bs_site_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'bs_switch': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bs_switch'", 'null': 'True', 'to': u"orm['device.Device']"}),
            'bs_type': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'building_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gps_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infra_provider': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'tower_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'inventory.circuit': {
            'Meta': {'object_name': 'Circuit'},
            'circuit_id': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Customer']"}),
            'date_of_acceptance': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Sector']"}),
            'sub_station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.SubStation']"})
        },
        u'inventory.customer': {
            'Meta': {'object_name': 'Customer'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'inventory.sector': {
            'Meta': {'object_name': 'Sector'},
            'antenna': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sector'", 'null': 'True', 'to': u"orm['inventory.Antenna']"}),
            'base_station': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sector'", 'to': u"orm['inventory.BaseStation']"}),
            'cell_radius': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'frame_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idu': ('django.db.models.fields.related.ForeignKey', [], {'max_length': '250', 'related_name': "'sector_idu'", 'null': 'True', 'to': u"orm['device.Device']"}),
            'idu_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mrc': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'odu': ('django.db.models.fields.related.ForeignKey', [], {'max_length': '250', 'related_name': "'sector_odu'", 'null': 'True', 'blank': 'True', 'to': u"orm['device.Device']"}),
            'odu_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sector_id': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'tx_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'inventory.substation': {
            'Meta': {'object_name': 'SubStation'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'building_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ethernet_extender': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'serial_no': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'tower_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
        u'service.service': {
            'Meta': {'object_name': 'Service'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['command.Command']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.ServiceParameters']", 'null': 'True', 'blank': 'True'}),
            'service_data_sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.ServiceDataSource']", 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'service.servicedatasource': {
            'Meta': {'object_name': 'ServiceDataSource'},
            'critical': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'data_source_alias': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'data_source_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'warning': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'service.serviceparameters': {
            'Meta': {'object_name': 'ServiceParameters'},
            'check_interval': ('django.db.models.fields.IntegerField', [], {}),
            'check_period': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_check_attempts': ('django.db.models.fields.IntegerField', [], {}),
            'notification_interval': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'notification_period': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parameter_description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'retry_interval': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'site_instance.siteinstance': {
            'Meta': {'object_name': 'SiteInstance'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'live_status_tcp_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['machine.Machine']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'site_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['inventory']