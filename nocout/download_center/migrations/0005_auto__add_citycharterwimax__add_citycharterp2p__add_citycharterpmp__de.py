# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CityCharterWiMAX'
        db.create_table(u'download_center_citycharterwimax', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('circuit_id', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('city_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('state_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('customer_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('bs_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('packetDrop', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('Latencydrop', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('device_state', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('current_value', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ul', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('latency', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('pd', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('vendor', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ss_device_technology_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('device_ss_ip_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('device_ss_mac_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('sector_device_ip_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('sector_id', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('dl_rssi_during_aceptance', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('intrf', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('seg_wimax', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('pmp', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ul_cinr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('dl_cinr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ptx', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal(u'download_center', ['CityCharterWiMAX'])

        # Adding model 'CityCharterP2P'
        db.create_table(u'download_center_citycharterp2p', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('circuit_id', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('city_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('state_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('customer_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('bs_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('packetDrop', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('Latencydrop', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('device_state', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('current_value', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ul', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('latency', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('pd', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('seg_p2p', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('technology', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('far_ip', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('near_ip', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('circuit_type', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('far_device_ss_mac_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('near_sector_device_mac_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('rssi_during_aceptance', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('uas', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal(u'download_center', ['CityCharterP2P'])

        # Adding model 'CityCharterPMP'
        db.create_table(u'download_center_citycharterpmp', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('circuit_id', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('city_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('state_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('customer_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('bs_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('packetDrop', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('Latencydrop', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('device_state', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('current_value', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ul', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('latency', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('pd', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('vendor', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ss_device_technology_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('device_ss_ip_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('device_ss_mac_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('sector_device_ip_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('sector_id', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('dl_rssi_during_aceptance', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('intrf', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('seg_pmp', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ul_jitter', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('dl_jitter', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('rereg_count', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('reg_count', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal(u'download_center', ['CityCharterPMP'])

        # # Deleting field 'ProcessedReportDetails.report_path'
        # db.delete_column(u'download_center_processedreportdetails', 'report_path')
        #
        # # Adding field 'ProcessedReportDetails.path'
        # db.add_column(u'download_center_processedreportdetails', 'path',
        #               self.gf('django.db.models.fields.CharField')(default='/opt/nocout/nocout_gis/nocout/media/download_center/reports', max_length=512),
        #               keep_default=False)
        #
        #
        # # Changing field 'ReportSettings.report_name'
        # db.alter_column(u'download_center_reportsettings', 'report_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))
        #
        # # Changing field 'ReportSettings.page_name'
        # db.alter_column(u'download_center_reportsettings', 'page_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))
        #
        # # Changing field 'ReportSettings.report_frequency'
        # db.alter_column(u'download_center_reportsettings', 'report_frequency', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

    def backwards(self, orm):
        # Deleting model 'CityCharterWiMAX'
        db.delete_table(u'download_center_citycharterwimax')

        # Deleting model 'CityCharterP2P'
        db.delete_table(u'download_center_citycharterp2p')

        # Deleting model 'CityCharterPMP'
        db.delete_table(u'download_center_citycharterpmp')


        # # User chose to not deal with backwards NULL issues for 'ProcessedReportDetails.report_path'
        # raise RuntimeError("Cannot reverse this migration. 'ProcessedReportDetails.report_path' and its values cannot be restored.")
        #
        # # The following code is provided here to aid in writing a correct migration        # Adding field 'ProcessedReportDetails.report_path'
        # db.add_column(u'download_center_processedreportdetails', 'report_path',
        #               self.gf('django.db.models.fields.CharField')(max_length=512),
        #               keep_default=False)
        #
        # # Deleting field 'ProcessedReportDetails.path'
        # db.delete_column(u'download_center_processedreportdetails', 'path')
        #
        #
        # # User chose to not deal with backwards NULL issues for 'ReportSettings.report_name'
        # raise RuntimeError("Cannot reverse this migration. 'ReportSettings.report_name' and its values cannot be restored.")
        #
        # # The following code is provided here to aid in writing a correct migration
        # # Changing field 'ReportSettings.report_name'
        # db.alter_column(u'download_center_reportsettings', 'report_name', self.gf('django.db.models.fields.CharField')(max_length=255))
        #
        # # User chose to not deal with backwards NULL issues for 'ReportSettings.page_name'
        # raise RuntimeError("Cannot reverse this migration. 'ReportSettings.page_name' and its values cannot be restored.")
        #
        # # The following code is provided here to aid in writing a correct migration
        # # Changing field 'ReportSettings.page_name'
        # db.alter_column(u'download_center_reportsettings', 'page_name', self.gf('django.db.models.fields.CharField')(max_length=128))
        #
        # # User chose to not deal with backwards NULL issues for 'ReportSettings.report_frequency'
        # raise RuntimeError("Cannot reverse this migration. 'ReportSettings.report_frequency' and its values cannot be restored.")
        #
        # # The following code is provided here to aid in writing a correct migration
        # # Changing field 'ReportSettings.report_frequency'
        # db.alter_column(u'download_center_reportsettings', 'report_frequency', self.gf('django.db.models.fields.CharField')(max_length=128))

    models = {
        u'download_center.citycharterp2p': {
            'Latencydrop': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'CityCharterP2P'},
            'bs_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'circuit_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'circuit_type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'customer_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'device_state': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'far_device_ss_mac_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'far_ip': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latency': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'near_ip': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'near_sector_device_mac_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'packetDrop': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'pd': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'rssi_during_aceptance': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'seg_p2p': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'state_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'technology': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'uas': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ul': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        u'download_center.citycharterpmp': {
            'Latencydrop': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'CityCharterPMP'},
            'bs_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'circuit_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'customer_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'device_ss_ip_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'device_ss_mac_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'device_state': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dl_jitter': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dl_rssi_during_aceptance': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intrf': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'latency': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'packetDrop': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'pd': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reg_count': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'rereg_count': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'sector_device_ip_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'sector_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'seg_pmp': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ss_device_technology_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'state_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ul': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ul_jitter': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        u'download_center.citycharterwimax': {
            'Latencydrop': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'CityCharterWiMAX'},
            'bs_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'circuit_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'current_value': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'customer_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'device_ss_ip_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'device_ss_mac_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'device_state': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dl_cinr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dl_rssi_during_aceptance': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intrf': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'latency': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'packetDrop': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'pd': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'pmp': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ptx': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'sector_device_ip_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'sector_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'seg_wimax': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ss_device_technology_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'state_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ul': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ul_cinr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        u'download_center.processedreportdetails': {
            'Meta': {'object_name': 'ProcessedReportDetails'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization_id': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'path': ('django.db.models.fields.CharField', [], {'default': "'/opt/nocout/nocout_gis/nocout/media/download_center/reports'", 'max_length': '512'}),
            'report_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'report_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'download_center.reportsettings': {
            'Meta': {'object_name': 'ReportSettings'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'report_frequency': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'report_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['download_center']