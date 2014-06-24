# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Inventory'
        db.create_table(u'inventory_inventory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['organization.Organization'])),
            ('user_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_group.UserGroup'])),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Inventory'])

        # Adding M2M table for field device_groups on 'Inventory'
        m2m_table_name = db.shorten_name(u'inventory_inventory_device_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('inventory', models.ForeignKey(orm[u'inventory.inventory'], null=False)),
            ('devicegroup', models.ForeignKey(orm[u'device_group.devicegroup'], null=False))
        ))
        db.create_unique(m2m_table_name, ['inventory_id', 'devicegroup_id'])

        # Adding model 'Antenna'
        db.create_table(u'inventory_antenna', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
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
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
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
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('bs_site_id', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
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
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('sector_id', self.gf('django.db.models.fields.CharField')(max_length=250, null=True)),
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
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Customer'])

        # Adding model 'SubStation'
        db.create_table(u'inventory_substation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
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
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('circuit_id', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('sector', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Sector'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Customer'])),
            ('sub_station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.SubStation'])),
            ('date_of_acceptance', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Circuit'])


    def backwards(self, orm):
        # Deleting model 'Inventory'
        db.delete_table(u'inventory_inventory')

        # Removing M2M table for field device_groups on 'Inventory'
        db.delete_table(db.shorten_name(u'inventory_inventory_device_groups'))

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
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'command.command': {
            'Meta': {'object_name': 'Command'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'command_line': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'device.device': {
            'Meta': {'object_name': 'Device'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'agent_tag': ('django.db.models.fields.CharField', [], {'default': "'ping'", 'max_length': '100'}),
            'city': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'device_alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organization.Organization']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'device_children'", 'null': 'True', 'to': u"orm['device.Device']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'service': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.Service']", 'null': 'True', 'blank': 'True'}),
            'site_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['site_instance.SiteInstance']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'Asia/Kolkata'", 'max_length': '100'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'device_group.devicegroup': {
            'Meta': {'object_name': 'DeviceGroup'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['device.Device']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organization.Organization']"}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'devicegroup_children'", 'null': 'True', 'to': u"orm['device_group.DeviceGroup']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'inventory.antenna': {
            'Meta': {'object_name': 'Antenna'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'azimuth_angle': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'beam_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'make_of_antenna': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'polarization': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'splitter_installed': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'sync_splitter_used': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'tilt': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'inventory.backhaul': {
            'Meta': {'object_name': 'Backhaul'},
            'aggregator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'backhaul_aggregator'", 'null': 'True', 'to': u"orm['device.Device']"}),
            'aggregator_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'bh_capacity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bh_circuit_id': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'bh_configured_on': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'backhaul'", 'null': 'True', 'to': u"orm['device.Device']"}),
            'bh_connectivity': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'bh_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bh_type': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dr_site': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'pe_hostname': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'pe_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'pop': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'backhaul_pop'", 'null': 'True', 'to': u"orm['device.Device']"}),
            'pop_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ttsl_circuit_id': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        },
        u'inventory.basestation': {
            'Meta': {'object_name': 'BaseStation'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'backhaul': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Backhaul']"}),
            'bs_site_id': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'bs_switch': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bs_switch'", 'null': 'True', 'to': u"orm['device.Device']"}),
            'bs_type': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'building_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gps_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infra_provider': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'tower_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'inventory.circuit': {
            'Meta': {'object_name': 'Circuit'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'circuit_id': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Customer']"}),
            'date_of_acceptance': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Sector']"}),
            'sub_station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.SubStation']"})
        },
        u'inventory.customer': {
            'Meta': {'object_name': 'Customer'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'inventory.inventory': {
            'Meta': {'object_name': 'Inventory'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'device_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['device_group.DeviceGroup']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organization.Organization']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_group.UserGroup']"})
        },
        u'inventory.sector': {
            'Meta': {'object_name': 'Sector'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'odu': ('django.db.models.fields.related.ForeignKey', [], {'max_length': '250', 'related_name': "'sector_odu'", 'null': 'True', 'blank': 'True', 'to': u"orm['device.Device']"}),
            'odu_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sector_id': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'tx_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'inventory.substation': {
            'Meta': {'object_name': 'SubStation'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'building_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ethernet_extender': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
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
        u'organization.organization': {
            'Meta': {'object_name': 'Organization'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
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
        u'service.service': {
            'Meta': {'object_name': 'Service'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'command': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['command.Command']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parameters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.ServiceParameters']", 'null': 'True', 'blank': 'True'}),
            'service_data_sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['service.ServiceDataSource']", 'null': 'True', 'blank': 'True'})
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
        },
        u'user_group.usergroup': {
            'Meta': {'object_name': 'UserGroup'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organization.Organization']"}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'usergroup_children'", 'null': 'True', 'to': u"orm['user_group.UserGroup']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['user_profile.UserProfile']", 'symmetrical': 'False'})
        },
        u'user_profile.roles': {
            'Meta': {'object_name': 'Roles'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role_description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'role_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'user_profile.userprofile': {
            'Meta': {'object_name': 'UserProfile', '_ormbases': [u'auth.User']},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organization.Organization']"}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'user_children'", 'null': 'True', 'to': u"orm['user_profile.UserProfile']"}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'role': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['user_profile.Roles']", 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['inventory']