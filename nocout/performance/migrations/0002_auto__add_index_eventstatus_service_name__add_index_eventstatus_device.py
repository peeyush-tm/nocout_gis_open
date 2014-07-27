# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'EventStatus', fields ['service_name']
        db.create_index(u'performance_eventstatus', ['service_name'])

        # Adding index on 'EventStatus', fields ['device_name']
        db.create_index(u'performance_eventstatus', ['device_name'])

        # Adding index on 'EventStatus', fields ['data_source']
        db.create_index(u'performance_eventstatus', ['data_source'])

        # Adding index on 'EventStatus', fields ['sys_timestamp']
        db.create_index(u'performance_eventstatus', ['sys_timestamp'])

        # Adding index on 'EventStatus', fields ['ip_address']
        db.create_index(u'performance_eventstatus', ['ip_address'])

        # Adding index on 'PerformanceMetric', fields ['service_name']
        db.create_index(u'performance_performancemetric', ['service_name'])

        # Adding index on 'PerformanceMetric', fields ['device_name']
        db.create_index(u'performance_performancemetric', ['device_name'])

        # Adding index on 'PerformanceMetric', fields ['data_source']
        db.create_index(u'performance_performancemetric', ['data_source'])

        # Adding index on 'PerformanceMetric', fields ['sys_timestamp']
        db.create_index(u'performance_performancemetric', ['sys_timestamp'])

        # Adding index on 'PerformanceMetric', fields ['ip_address']
        db.create_index(u'performance_performancemetric', ['ip_address'])

        # Adding index on 'MachineStatus', fields ['service_name']
        db.create_index(u'performance_machinestatus', ['service_name'])

        # Adding index on 'MachineStatus', fields ['device_name']
        db.create_index(u'performance_machinestatus', ['device_name'])

        # Adding index on 'MachineStatus', fields ['data_source']
        db.create_index(u'performance_machinestatus', ['data_source'])

        # Adding index on 'MachineStatus', fields ['sys_timestamp']
        db.create_index(u'performance_machinestatus', ['sys_timestamp'])

        # Adding index on 'MachineStatus', fields ['ip_address']
        db.create_index(u'performance_machinestatus', ['ip_address'])

        # Adding index on 'EventInventory', fields ['service_name']
        db.create_index(u'performance_eventinventory', ['service_name'])

        # Adding index on 'EventInventory', fields ['device_name']
        db.create_index(u'performance_eventinventory', ['device_name'])

        # Adding index on 'EventInventory', fields ['data_source']
        db.create_index(u'performance_eventinventory', ['data_source'])

        # Adding index on 'EventInventory', fields ['sys_timestamp']
        db.create_index(u'performance_eventinventory', ['sys_timestamp'])

        # Adding index on 'EventInventory', fields ['ip_address']
        db.create_index(u'performance_eventinventory', ['ip_address'])

        # Adding index on 'EventService', fields ['service_name']
        db.create_index(u'performance_eventservice', ['service_name'])

        # Adding index on 'EventService', fields ['device_name']
        db.create_index(u'performance_eventservice', ['device_name'])

        # Adding index on 'EventService', fields ['data_source']
        db.create_index(u'performance_eventservice', ['data_source'])

        # Adding index on 'EventService', fields ['sys_timestamp']
        db.create_index(u'performance_eventservice', ['sys_timestamp'])

        # Adding index on 'EventService', fields ['ip_address']
        db.create_index(u'performance_eventservice', ['ip_address'])

        # Deleting field 'EventNetwork.description'
        db.delete_column(u'performance_eventnetwork', 'description')

        # Adding index on 'EventNetwork', fields ['service_name']
        db.create_index(u'performance_eventnetwork', ['service_name'])

        # Adding index on 'EventNetwork', fields ['device_name']
        db.create_index(u'performance_eventnetwork', ['device_name'])

        # Adding index on 'EventNetwork', fields ['data_source']
        db.create_index(u'performance_eventnetwork', ['data_source'])

        # Adding index on 'EventNetwork', fields ['sys_timestamp']
        db.create_index(u'performance_eventnetwork', ['sys_timestamp'])

        # Adding index on 'EventNetwork', fields ['ip_address']
        db.create_index(u'performance_eventnetwork', ['ip_address'])

        # Adding index on 'Status', fields ['service_name']
        db.create_index(u'performance_status', ['service_name'])

        # Adding index on 'Status', fields ['device_name']
        db.create_index(u'performance_status', ['device_name'])

        # Adding index on 'Status', fields ['data_source']
        db.create_index(u'performance_status', ['data_source'])

        # Adding index on 'Status', fields ['sys_timestamp']
        db.create_index(u'performance_status', ['sys_timestamp'])

        # Adding index on 'Status', fields ['ip_address']
        db.create_index(u'performance_status', ['ip_address'])

        # Adding index on 'PerformanceStatus', fields ['service_name']
        db.create_index(u'performance_performancestatus', ['service_name'])

        # Adding index on 'PerformanceStatus', fields ['device_name']
        db.create_index(u'performance_performancestatus', ['device_name'])

        # Adding index on 'PerformanceStatus', fields ['data_source']
        db.create_index(u'performance_performancestatus', ['data_source'])

        # Adding index on 'PerformanceStatus', fields ['sys_timestamp']
        db.create_index(u'performance_performancestatus', ['sys_timestamp'])

        # Adding index on 'PerformanceStatus', fields ['ip_address']
        db.create_index(u'performance_performancestatus', ['ip_address'])

        # Adding index on 'InventoryStatus', fields ['service_name']
        db.create_index(u'performance_inventorystatus', ['service_name'])

        # Adding index on 'InventoryStatus', fields ['device_name']
        db.create_index(u'performance_inventorystatus', ['device_name'])

        # Adding index on 'InventoryStatus', fields ['data_source']
        db.create_index(u'performance_inventorystatus', ['data_source'])

        # Adding index on 'InventoryStatus', fields ['sys_timestamp']
        db.create_index(u'performance_inventorystatus', ['sys_timestamp'])

        # Adding index on 'InventoryStatus', fields ['ip_address']
        db.create_index(u'performance_inventorystatus', ['ip_address'])

        # Adding index on 'PerformanceMachine', fields ['service_name']
        db.create_index(u'performance_performancemachine', ['service_name'])

        # Adding index on 'PerformanceMachine', fields ['device_name']
        db.create_index(u'performance_performancemachine', ['device_name'])

        # Adding index on 'PerformanceMachine', fields ['data_source']
        db.create_index(u'performance_performancemachine', ['data_source'])

        # Adding index on 'PerformanceMachine', fields ['sys_timestamp']
        db.create_index(u'performance_performancemachine', ['sys_timestamp'])

        # Adding index on 'PerformanceMachine', fields ['ip_address']
        db.create_index(u'performance_performancemachine', ['ip_address'])

        # Adding index on 'ServiceStatus', fields ['service_name']
        db.create_index(u'performance_servicestatus', ['service_name'])

        # Adding index on 'ServiceStatus', fields ['device_name']
        db.create_index(u'performance_servicestatus', ['device_name'])

        # Adding index on 'ServiceStatus', fields ['data_source']
        db.create_index(u'performance_servicestatus', ['data_source'])

        # Adding index on 'ServiceStatus', fields ['sys_timestamp']
        db.create_index(u'performance_servicestatus', ['sys_timestamp'])

        # Adding index on 'ServiceStatus', fields ['ip_address']
        db.create_index(u'performance_servicestatus', ['ip_address'])

        # Adding index on 'PerformanceService', fields ['service_name']
        db.create_index(u'performance_performanceservice', ['service_name'])

        # Adding index on 'PerformanceService', fields ['device_name']
        db.create_index(u'performance_performanceservice', ['device_name'])

        # Adding index on 'PerformanceService', fields ['data_source']
        db.create_index(u'performance_performanceservice', ['data_source'])

        # Adding index on 'PerformanceService', fields ['sys_timestamp']
        db.create_index(u'performance_performanceservice', ['sys_timestamp'])

        # Adding index on 'PerformanceService', fields ['ip_address']
        db.create_index(u'performance_performanceservice', ['ip_address'])

        # Adding index on 'NetworkStatus', fields ['service_name']
        db.create_index(u'performance_networkstatus', ['service_name'])

        # Adding index on 'NetworkStatus', fields ['device_name']
        db.create_index(u'performance_networkstatus', ['device_name'])

        # Adding index on 'NetworkStatus', fields ['data_source']
        db.create_index(u'performance_networkstatus', ['data_source'])

        # Adding index on 'NetworkStatus', fields ['sys_timestamp']
        db.create_index(u'performance_networkstatus', ['sys_timestamp'])

        # Adding index on 'NetworkStatus', fields ['ip_address']
        db.create_index(u'performance_networkstatus', ['ip_address'])

        # Adding index on 'PerformanceNetwork', fields ['service_name']
        db.create_index(u'performance_performancenetwork', ['service_name'])

        # Adding index on 'PerformanceNetwork', fields ['device_name']
        db.create_index(u'performance_performancenetwork', ['device_name'])

        # Adding index on 'PerformanceNetwork', fields ['data_source']
        db.create_index(u'performance_performancenetwork', ['data_source'])

        # Adding index on 'PerformanceNetwork', fields ['sys_timestamp']
        db.create_index(u'performance_performancenetwork', ['sys_timestamp'])

        # Adding index on 'PerformanceNetwork', fields ['ip_address']
        db.create_index(u'performance_performancenetwork', ['ip_address'])

        # Adding index on 'PerformanceInventory', fields ['service_name']
        db.create_index(u'performance_performanceinventory', ['service_name'])

        # Adding index on 'PerformanceInventory', fields ['device_name']
        db.create_index(u'performance_performanceinventory', ['device_name'])

        # Adding index on 'PerformanceInventory', fields ['data_source']
        db.create_index(u'performance_performanceinventory', ['data_source'])

        # Adding index on 'PerformanceInventory', fields ['sys_timestamp']
        db.create_index(u'performance_performanceinventory', ['sys_timestamp'])

        # Adding index on 'PerformanceInventory', fields ['ip_address']
        db.create_index(u'performance_performanceinventory', ['ip_address'])

        # Adding index on 'EventMachine', fields ['service_name']
        db.create_index(u'performance_eventmachine', ['service_name'])

        # Adding index on 'EventMachine', fields ['device_name']
        db.create_index(u'performance_eventmachine', ['device_name'])

        # Adding index on 'EventMachine', fields ['data_source']
        db.create_index(u'performance_eventmachine', ['data_source'])

        # Adding index on 'EventMachine', fields ['sys_timestamp']
        db.create_index(u'performance_eventmachine', ['sys_timestamp'])

        # Adding index on 'EventMachine', fields ['ip_address']
        db.create_index(u'performance_eventmachine', ['ip_address'])


    def backwards(self, orm):
        # Removing index on 'EventMachine', fields ['ip_address']
        db.delete_index(u'performance_eventmachine', ['ip_address'])

        # Removing index on 'EventMachine', fields ['sys_timestamp']
        db.delete_index(u'performance_eventmachine', ['sys_timestamp'])

        # Removing index on 'EventMachine', fields ['data_source']
        db.delete_index(u'performance_eventmachine', ['data_source'])

        # Removing index on 'EventMachine', fields ['device_name']
        db.delete_index(u'performance_eventmachine', ['device_name'])

        # Removing index on 'EventMachine', fields ['service_name']
        db.delete_index(u'performance_eventmachine', ['service_name'])

        # Removing index on 'PerformanceInventory', fields ['ip_address']
        db.delete_index(u'performance_performanceinventory', ['ip_address'])

        # Removing index on 'PerformanceInventory', fields ['sys_timestamp']
        db.delete_index(u'performance_performanceinventory', ['sys_timestamp'])

        # Removing index on 'PerformanceInventory', fields ['data_source']
        db.delete_index(u'performance_performanceinventory', ['data_source'])

        # Removing index on 'PerformanceInventory', fields ['device_name']
        db.delete_index(u'performance_performanceinventory', ['device_name'])

        # Removing index on 'PerformanceInventory', fields ['service_name']
        db.delete_index(u'performance_performanceinventory', ['service_name'])

        # Removing index on 'PerformanceNetwork', fields ['ip_address']
        db.delete_index(u'performance_performancenetwork', ['ip_address'])

        # Removing index on 'PerformanceNetwork', fields ['sys_timestamp']
        db.delete_index(u'performance_performancenetwork', ['sys_timestamp'])

        # Removing index on 'PerformanceNetwork', fields ['data_source']
        db.delete_index(u'performance_performancenetwork', ['data_source'])

        # Removing index on 'PerformanceNetwork', fields ['device_name']
        db.delete_index(u'performance_performancenetwork', ['device_name'])

        # Removing index on 'PerformanceNetwork', fields ['service_name']
        db.delete_index(u'performance_performancenetwork', ['service_name'])

        # Removing index on 'NetworkStatus', fields ['ip_address']
        db.delete_index(u'performance_networkstatus', ['ip_address'])

        # Removing index on 'NetworkStatus', fields ['sys_timestamp']
        db.delete_index(u'performance_networkstatus', ['sys_timestamp'])

        # Removing index on 'NetworkStatus', fields ['data_source']
        db.delete_index(u'performance_networkstatus', ['data_source'])

        # Removing index on 'NetworkStatus', fields ['device_name']
        db.delete_index(u'performance_networkstatus', ['device_name'])

        # Removing index on 'NetworkStatus', fields ['service_name']
        db.delete_index(u'performance_networkstatus', ['service_name'])

        # Removing index on 'PerformanceService', fields ['ip_address']
        db.delete_index(u'performance_performanceservice', ['ip_address'])

        # Removing index on 'PerformanceService', fields ['sys_timestamp']
        db.delete_index(u'performance_performanceservice', ['sys_timestamp'])

        # Removing index on 'PerformanceService', fields ['data_source']
        db.delete_index(u'performance_performanceservice', ['data_source'])

        # Removing index on 'PerformanceService', fields ['device_name']
        db.delete_index(u'performance_performanceservice', ['device_name'])

        # Removing index on 'PerformanceService', fields ['service_name']
        db.delete_index(u'performance_performanceservice', ['service_name'])

        # Removing index on 'ServiceStatus', fields ['ip_address']
        db.delete_index(u'performance_servicestatus', ['ip_address'])

        # Removing index on 'ServiceStatus', fields ['sys_timestamp']
        db.delete_index(u'performance_servicestatus', ['sys_timestamp'])

        # Removing index on 'ServiceStatus', fields ['data_source']
        db.delete_index(u'performance_servicestatus', ['data_source'])

        # Removing index on 'ServiceStatus', fields ['device_name']
        db.delete_index(u'performance_servicestatus', ['device_name'])

        # Removing index on 'ServiceStatus', fields ['service_name']
        db.delete_index(u'performance_servicestatus', ['service_name'])

        # Removing index on 'PerformanceMachine', fields ['ip_address']
        db.delete_index(u'performance_performancemachine', ['ip_address'])

        # Removing index on 'PerformanceMachine', fields ['sys_timestamp']
        db.delete_index(u'performance_performancemachine', ['sys_timestamp'])

        # Removing index on 'PerformanceMachine', fields ['data_source']
        db.delete_index(u'performance_performancemachine', ['data_source'])

        # Removing index on 'PerformanceMachine', fields ['device_name']
        db.delete_index(u'performance_performancemachine', ['device_name'])

        # Removing index on 'PerformanceMachine', fields ['service_name']
        db.delete_index(u'performance_performancemachine', ['service_name'])

        # Removing index on 'InventoryStatus', fields ['ip_address']
        db.delete_index(u'performance_inventorystatus', ['ip_address'])

        # Removing index on 'InventoryStatus', fields ['sys_timestamp']
        db.delete_index(u'performance_inventorystatus', ['sys_timestamp'])

        # Removing index on 'InventoryStatus', fields ['data_source']
        db.delete_index(u'performance_inventorystatus', ['data_source'])

        # Removing index on 'InventoryStatus', fields ['device_name']
        db.delete_index(u'performance_inventorystatus', ['device_name'])

        # Removing index on 'InventoryStatus', fields ['service_name']
        db.delete_index(u'performance_inventorystatus', ['service_name'])

        # Removing index on 'PerformanceStatus', fields ['ip_address']
        db.delete_index(u'performance_performancestatus', ['ip_address'])

        # Removing index on 'PerformanceStatus', fields ['sys_timestamp']
        db.delete_index(u'performance_performancestatus', ['sys_timestamp'])

        # Removing index on 'PerformanceStatus', fields ['data_source']
        db.delete_index(u'performance_performancestatus', ['data_source'])

        # Removing index on 'PerformanceStatus', fields ['device_name']
        db.delete_index(u'performance_performancestatus', ['device_name'])

        # Removing index on 'PerformanceStatus', fields ['service_name']
        db.delete_index(u'performance_performancestatus', ['service_name'])

        # Removing index on 'Status', fields ['ip_address']
        db.delete_index(u'performance_status', ['ip_address'])

        # Removing index on 'Status', fields ['sys_timestamp']
        db.delete_index(u'performance_status', ['sys_timestamp'])

        # Removing index on 'Status', fields ['data_source']
        db.delete_index(u'performance_status', ['data_source'])

        # Removing index on 'Status', fields ['device_name']
        db.delete_index(u'performance_status', ['device_name'])

        # Removing index on 'Status', fields ['service_name']
        db.delete_index(u'performance_status', ['service_name'])

        # Removing index on 'EventNetwork', fields ['ip_address']
        db.delete_index(u'performance_eventnetwork', ['ip_address'])

        # Removing index on 'EventNetwork', fields ['sys_timestamp']
        db.delete_index(u'performance_eventnetwork', ['sys_timestamp'])

        # Removing index on 'EventNetwork', fields ['data_source']
        db.delete_index(u'performance_eventnetwork', ['data_source'])

        # Removing index on 'EventNetwork', fields ['device_name']
        db.delete_index(u'performance_eventnetwork', ['device_name'])

        # Removing index on 'EventNetwork', fields ['service_name']
        db.delete_index(u'performance_eventnetwork', ['service_name'])

        # Removing index on 'EventService', fields ['ip_address']
        db.delete_index(u'performance_eventservice', ['ip_address'])

        # Removing index on 'EventService', fields ['sys_timestamp']
        db.delete_index(u'performance_eventservice', ['sys_timestamp'])

        # Removing index on 'EventService', fields ['data_source']
        db.delete_index(u'performance_eventservice', ['data_source'])

        # Removing index on 'EventService', fields ['device_name']
        db.delete_index(u'performance_eventservice', ['device_name'])

        # Removing index on 'EventService', fields ['service_name']
        db.delete_index(u'performance_eventservice', ['service_name'])

        # Removing index on 'EventInventory', fields ['ip_address']
        db.delete_index(u'performance_eventinventory', ['ip_address'])

        # Removing index on 'EventInventory', fields ['sys_timestamp']
        db.delete_index(u'performance_eventinventory', ['sys_timestamp'])

        # Removing index on 'EventInventory', fields ['data_source']
        db.delete_index(u'performance_eventinventory', ['data_source'])

        # Removing index on 'EventInventory', fields ['device_name']
        db.delete_index(u'performance_eventinventory', ['device_name'])

        # Removing index on 'EventInventory', fields ['service_name']
        db.delete_index(u'performance_eventinventory', ['service_name'])

        # Removing index on 'MachineStatus', fields ['ip_address']
        db.delete_index(u'performance_machinestatus', ['ip_address'])

        # Removing index on 'MachineStatus', fields ['sys_timestamp']
        db.delete_index(u'performance_machinestatus', ['sys_timestamp'])

        # Removing index on 'MachineStatus', fields ['data_source']
        db.delete_index(u'performance_machinestatus', ['data_source'])

        # Removing index on 'MachineStatus', fields ['device_name']
        db.delete_index(u'performance_machinestatus', ['device_name'])

        # Removing index on 'MachineStatus', fields ['service_name']
        db.delete_index(u'performance_machinestatus', ['service_name'])

        # Removing index on 'PerformanceMetric', fields ['ip_address']
        db.delete_index(u'performance_performancemetric', ['ip_address'])

        # Removing index on 'PerformanceMetric', fields ['sys_timestamp']
        db.delete_index(u'performance_performancemetric', ['sys_timestamp'])

        # Removing index on 'PerformanceMetric', fields ['data_source']
        db.delete_index(u'performance_performancemetric', ['data_source'])

        # Removing index on 'PerformanceMetric', fields ['device_name']
        db.delete_index(u'performance_performancemetric', ['device_name'])

        # Removing index on 'PerformanceMetric', fields ['service_name']
        db.delete_index(u'performance_performancemetric', ['service_name'])

        # Removing index on 'EventStatus', fields ['ip_address']
        db.delete_index(u'performance_eventstatus', ['ip_address'])

        # Removing index on 'EventStatus', fields ['sys_timestamp']
        db.delete_index(u'performance_eventstatus', ['sys_timestamp'])

        # Removing index on 'EventStatus', fields ['data_source']
        db.delete_index(u'performance_eventstatus', ['data_source'])

        # Removing index on 'EventStatus', fields ['device_name']
        db.delete_index(u'performance_eventstatus', ['device_name'])

        # Removing index on 'EventStatus', fields ['service_name']
        db.delete_index(u'performance_eventstatus', ['service_name'])

        # Adding field 'EventNetwork.description'
        db.add_column(u'performance_eventnetwork', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


    models = {
        u'performance.eventinventory': {
            'Meta': {'object_name': 'EventInventory'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.eventmachine': {
            'Meta': {'object_name': 'EventMachine'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.eventnetwork': {
            'Meta': {'object_name': 'EventNetwork'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.eventservice': {
            'Meta': {'object_name': 'EventService'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.eventstatus': {
            'Meta': {'object_name': 'EventStatus'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.inventorystatus': {
            'Meta': {'object_name': 'InventoryStatus'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.machinestatus': {
            'Meta': {'object_name': 'MachineStatus'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.networkstatus': {
            'Meta': {'object_name': 'NetworkStatus'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performanceinventory': {
            'Meta': {'object_name': 'PerformanceInventory'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performancemachine': {
            'Meta': {'object_name': 'PerformanceMachine'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performancemetric': {
            'Meta': {'object_name': 'PerformanceMetric'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performancenetwork': {
            'Meta': {'object_name': 'PerformanceNetwork'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performanceservice': {
            'Meta': {'object_name': 'PerformanceService'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.performancestatus': {
            'Meta': {'object_name': 'PerformanceStatus'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.servicestatus': {
            'Meta': {'object_name': 'ServiceStatus'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'performance.status': {
            'Meta': {'object_name': 'Status'},
            'avg_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'check_timestamp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'critical_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'service_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sys_timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'warning_threshold': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['performance']