# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0003_auto_20151019_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bsoutagefaultdaily',
            name='city',
            field=models.CharField(max_length=256, verbose_name=b'City'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultdaily',
            name='fault_type',
            field=models.CharField(max_length=128, verbose_name=b'Type of Fault'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultdaily',
            name='organization',
            field=models.CharField(max_length=128, verbose_name=b'Organization'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultdaily',
            name='outage_count',
            field=models.CharField(max_length=128, verbose_name=b'Outage Count'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultdaily',
            name='outage_min_per_site',
            field=models.CharField(max_length=128, verbose_name=b'Outage Per Site(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultmonthly',
            name='city',
            field=models.CharField(max_length=256, verbose_name=b'City'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultmonthly',
            name='fault_type',
            field=models.CharField(max_length=128, verbose_name=b'Type of Fault'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultmonthly',
            name='organization',
            field=models.CharField(max_length=128, verbose_name=b'Organization'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultmonthly',
            name='outage_count',
            field=models.CharField(max_length=128, verbose_name=b'Outage Count'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultmonthly',
            name='outage_min_per_site',
            field=models.CharField(max_length=128, verbose_name=b'Outage Per Site(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultweekly',
            name='city',
            field=models.CharField(max_length=256, verbose_name=b'City'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultweekly',
            name='fault_type',
            field=models.CharField(max_length=128, verbose_name=b'Type of Fault'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultweekly',
            name='organization',
            field=models.CharField(max_length=128, verbose_name=b'Organization'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultweekly',
            name='outage_count',
            field=models.CharField(max_length=128, verbose_name=b'Outage Count'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultweekly',
            name='outage_min_per_site',
            field=models.CharField(max_length=128, verbose_name=b'Outage Per Site(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='alarm_observer',
            field=models.CharField(max_length=256, verbose_name=b'Alarm Observed'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='alarm_outage_min',
            field=models.CharField(max_length=128, verbose_name=b'Alarm Outage(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='alarm_restored_timestamp',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Alarm Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='bs_ip',
            field=models.CharField(max_length=128, verbose_name=b'BS IP Address'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='bs_name',
            field=models.CharField(max_length=256, verbose_name=b'BaseStation Name'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='bs_sw_version',
            field=models.CharField(max_length=128, verbose_name=b'BS Software Version'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='bs_type',
            field=models.CharField(max_length=128, verbose_name=b'BaseStation Type'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='call_assigned_to',
            field=models.CharField(max_length=256, verbose_name=b'Call Assigned To'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='cause_code',
            field=models.CharField(max_length=128, verbose_name=b'Cause Code'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='city',
            field=models.CharField(max_length=256, verbose_name=b'City'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='delay',
            field=models.CharField(max_length=128, verbose_name=b'Delay'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='delay_reason',
            field=models.CharField(max_length=256, verbose_name=b'Delay Reason'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='equipment_replaced',
            field=models.CharField(max_length=128, verbose_name=b'Equipment Replaced'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='fault_description',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Remark/Detail Fault Description', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='fault_history',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Fault History', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='fault_type',
            field=models.CharField(max_length=128, verbose_name=b'Type of Fault'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='infra_provider',
            field=models.CharField(max_length=128, verbose_name=b'INFRA Provider'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='l1_engg_name',
            field=models.CharField(max_length=256, verbose_name=b'Name of L1 Engineer'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='l2_engg_name',
            field=models.CharField(max_length=256, verbose_name=b'Name of L2 Engineer'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='last_modified_by',
            field=models.CharField(max_length=256, verbose_name=b'Last Modified By'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='mttr',
            field=models.CharField(max_length=128, verbose_name=b'MTTR'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='mttr_hrs',
            field=models.CharField(max_length=128, verbose_name=b'MTTR Hrs'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='organization',
            field=models.CharField(max_length=128, verbose_name=b'Organization'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='outage_min_per_site',
            field=models.CharField(max_length=128, verbose_name=b'Outage Per Site(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='outage_timestamp',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Outage Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='outage_total_min',
            field=models.CharField(max_length=128, verbose_name=b'Outage Total(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='restore_action',
            field=models.CharField(max_length=256, verbose_name=b'Action Taken to Restore the BS'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='restored_timestamp',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='rfo',
            field=models.CharField(max_length=256, verbose_name=b'RFO'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='site_id',
            field=models.CharField(max_length=128, verbose_name=b'Site ID'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='spot_cases',
            field=models.CharField(max_length=128, verbose_name=b'Spot Cases'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='status',
            field=models.CharField(max_length=128, verbose_name=b'Status'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='sub_cause_code',
            field=models.CharField(max_length=128, verbose_name=b'Sub Cause Code'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='switch_reachability',
            field=models.CharField(max_length=128, verbose_name=b'Switch Reachability'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='tac_tt_number',
            field=models.CharField(max_length=128, verbose_name=b'Tac TT Number'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='ticket_number',
            field=models.CharField(max_length=128, verbose_name=b'Trouble Ticket Number'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='total_affected_bs',
            field=models.CharField(max_length=128, verbose_name=b'Number of BS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='total_affected_enterprise_ss',
            field=models.CharField(max_length=128, verbose_name=b'Number of Enterprise SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='total_affected_retail_ss',
            field=models.CharField(max_length=128, verbose_name=b'Number of Retail SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='total_affected_sector',
            field=models.CharField(max_length=128, verbose_name=b'Number of Sectors Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='type_of_city',
            field=models.CharField(max_length=128, verbose_name=b'Type of City'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='unit_replaced',
            field=models.CharField(max_length=128, verbose_name=b'Unit Replaced'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='week_number',
            field=models.CharField(max_length=128, verbose_name=b'Week of the Year'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='alarm_observer',
            field=models.CharField(max_length=256, verbose_name=b'Alarm Observed'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='alarm_outage_min',
            field=models.CharField(max_length=128, verbose_name=b'Alarm Outage(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='alarm_restored_timestamp',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Alarm Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='bs_ip',
            field=models.CharField(max_length=128, verbose_name=b'BS IP Address'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='bs_name',
            field=models.CharField(max_length=256, verbose_name=b'BaseStation Name'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='bs_sw_version',
            field=models.CharField(max_length=128, verbose_name=b'BS Software Version'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='bs_type',
            field=models.CharField(max_length=128, verbose_name=b'BaseStation Type'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='call_assigned_to',
            field=models.CharField(max_length=256, verbose_name=b'Call Assigned To'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='cause_code',
            field=models.CharField(max_length=128, verbose_name=b'Cause Code'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='city',
            field=models.CharField(max_length=256, verbose_name=b'City'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='delay',
            field=models.CharField(max_length=128, verbose_name=b'Delay'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='delay_reason',
            field=models.CharField(max_length=256, verbose_name=b'Delay Reason'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='equipment_replaced',
            field=models.CharField(max_length=128, verbose_name=b'Equipment Replaced'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='fault_description',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Remark/Detail Fault Description', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='fault_history',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Fault History', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='fault_type',
            field=models.CharField(max_length=128, verbose_name=b'Type of Fault'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='infra_provider',
            field=models.CharField(max_length=128, verbose_name=b'INFRA Provider'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='l1_engg_name',
            field=models.CharField(max_length=256, verbose_name=b'Name of L1 Engineer'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='l2_engg_name',
            field=models.CharField(max_length=256, verbose_name=b'Name of L2 Engineer'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='last_modified_by',
            field=models.CharField(max_length=256, verbose_name=b'Last Modified By'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='mttr',
            field=models.CharField(max_length=128, verbose_name=b'MTTR'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='mttr_hrs',
            field=models.CharField(max_length=128, verbose_name=b'MTTR Hrs'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='organization',
            field=models.CharField(max_length=128, verbose_name=b'Organization'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='outage_min_per_site',
            field=models.CharField(max_length=128, verbose_name=b'Outage Per Site(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='outage_timestamp',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Outage Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='outage_total_min',
            field=models.CharField(max_length=128, verbose_name=b'Outage Total(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='restore_action',
            field=models.CharField(max_length=256, verbose_name=b'Action Taken to Restore the BS'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='restored_timestamp',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='rfo',
            field=models.CharField(max_length=256, verbose_name=b'RFO'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='site_id',
            field=models.CharField(max_length=128, verbose_name=b'Site ID'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='spot_cases',
            field=models.CharField(max_length=128, verbose_name=b'Spot Cases'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='status',
            field=models.CharField(max_length=128, verbose_name=b'Status'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='sub_cause_code',
            field=models.CharField(max_length=128, verbose_name=b'Sub Cause Code'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='switch_reachability',
            field=models.CharField(max_length=128, verbose_name=b'Switch Reachability'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='tac_tt_number',
            field=models.CharField(max_length=128, verbose_name=b'Tac TT Number'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='ticket_number',
            field=models.CharField(max_length=128, verbose_name=b'Trouble Ticket Number'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='total_affected_bs',
            field=models.CharField(max_length=128, verbose_name=b'Number of BS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='total_affected_enterprise_ss',
            field=models.CharField(max_length=128, verbose_name=b'Number of Enterprise SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='total_affected_retail_ss',
            field=models.CharField(max_length=128, verbose_name=b'Number of Retail SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='total_affected_sector',
            field=models.CharField(max_length=128, verbose_name=b'Number of Sectors Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='type_of_city',
            field=models.CharField(max_length=128, verbose_name=b'Type of City'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='unit_replaced',
            field=models.CharField(max_length=128, verbose_name=b'Unit Replaced'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='week_number',
            field=models.CharField(max_length=128, verbose_name=b'Week of the Year'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='alarm_observer',
            field=models.CharField(max_length=256, verbose_name=b'Alarm Observed'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='alarm_outage_min',
            field=models.CharField(max_length=128, verbose_name=b'Alarm Outage(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='alarm_restored_timestamp',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Alarm Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='bs_ip',
            field=models.CharField(max_length=128, verbose_name=b'BS IP Address'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='bs_name',
            field=models.CharField(max_length=256, verbose_name=b'BaseStation Name'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='bs_sw_version',
            field=models.CharField(max_length=128, verbose_name=b'BS Software Version'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='bs_type',
            field=models.CharField(max_length=128, verbose_name=b'BaseStation Type'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='call_assigned_to',
            field=models.CharField(max_length=256, verbose_name=b'Call Assigned To'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='cause_code',
            field=models.CharField(max_length=128, verbose_name=b'Cause Code'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='city',
            field=models.CharField(max_length=256, verbose_name=b'City'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='delay',
            field=models.CharField(max_length=128, verbose_name=b'Delay'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='delay_reason',
            field=models.CharField(max_length=256, verbose_name=b'Delay Reason'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='equipment_replaced',
            field=models.CharField(max_length=128, verbose_name=b'Equipment Replaced'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='fault_description',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Remark/Detail Fault Description', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='fault_history',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Fault History', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='fault_type',
            field=models.CharField(max_length=128, verbose_name=b'Type of Fault'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='infra_provider',
            field=models.CharField(max_length=128, verbose_name=b'INFRA Provider'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='l1_engg_name',
            field=models.CharField(max_length=256, verbose_name=b'Name of L1 Engineer'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='l2_engg_name',
            field=models.CharField(max_length=256, verbose_name=b'Name of L2 Engineer'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='last_modified_by',
            field=models.CharField(max_length=256, verbose_name=b'Last Modified By'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='mttr',
            field=models.CharField(max_length=128, verbose_name=b'MTTR'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='mttr_hrs',
            field=models.CharField(max_length=128, verbose_name=b'MTTR Hrs'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='organization',
            field=models.CharField(max_length=128, verbose_name=b'Organization'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='outage_min_per_site',
            field=models.CharField(max_length=128, verbose_name=b'Outage Per Site(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='outage_timestamp',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Outage Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='outage_total_min',
            field=models.CharField(max_length=128, verbose_name=b'Outage Total(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='restore_action',
            field=models.CharField(max_length=256, verbose_name=b'Action Taken to Restore the BS'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='restored_timestamp',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='rfo',
            field=models.CharField(max_length=256, verbose_name=b'RFO'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='site_id',
            field=models.CharField(max_length=128, verbose_name=b'Site ID'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='spot_cases',
            field=models.CharField(max_length=128, verbose_name=b'Spot Cases'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='status',
            field=models.CharField(max_length=128, verbose_name=b'Status'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='sub_cause_code',
            field=models.CharField(max_length=128, verbose_name=b'Sub Cause Code'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='switch_reachability',
            field=models.CharField(max_length=128, verbose_name=b'Switch Reachability'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='tac_tt_number',
            field=models.CharField(max_length=128, verbose_name=b'Tac TT Number'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='ticket_number',
            field=models.CharField(max_length=128, verbose_name=b'Trouble Ticket Number'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='total_affected_bs',
            field=models.CharField(max_length=128, verbose_name=b'Number of BS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='total_affected_enterprise_ss',
            field=models.CharField(max_length=128, verbose_name=b'Number of Enterprise SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='total_affected_retail_ss',
            field=models.CharField(max_length=128, verbose_name=b'Number of Retail SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='total_affected_sector',
            field=models.CharField(max_length=128, verbose_name=b'Number of Sectors Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='type_of_city',
            field=models.CharField(max_length=128, verbose_name=b'Type of City'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='unit_replaced',
            field=models.CharField(max_length=128, verbose_name=b'Unit Replaced'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='week_number',
            field=models.CharField(max_length=128, verbose_name=b'Week of the Year'),
        ),
        migrations.AlterField(
            model_name='bsoutagemttrprocessed',
            name='bs_name',
            field=models.CharField(max_length=256, verbose_name=b'BaseStation Name'),
        ),
        migrations.AlterField(
            model_name='bsoutagemttrprocessed',
            name='city',
            field=models.CharField(max_length=256, verbose_name=b'City'),
        ),
        migrations.AlterField(
            model_name='bsoutagemttrprocessed',
            name='organization',
            field=models.CharField(max_length=128, verbose_name=b'Organization'),
        ),
        migrations.AlterField(
            model_name='bsoutagemttrprocessed',
            name='processed_on',
            field=models.CharField(max_length=128, verbose_name=b'Processed Date and Time'),
        ),
        migrations.AlterField(
            model_name='bsoutagemttrprocessed',
            name='rfo',
            field=models.CharField(max_length=256, null=True, verbose_name=b'RFO', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemttrprocessed',
            name='time_frame',
            field=models.CharField(max_length=128, verbose_name=b'4-8 or Greater than 8 hrs'),
        ),
        migrations.AlterField(
            model_name='bsoutageuptimereport',
            name='bs_name',
            field=models.CharField(max_length=256, verbose_name=b'BaseStation Name'),
        ),
        migrations.AlterField(
            model_name='bsoutageuptimereport',
            name='bs_uptime',
            field=models.CharField(max_length=128, verbose_name=b'BS Uptime'),
        ),
        migrations.AlterField(
            model_name='bsoutageuptimereport',
            name='city',
            field=models.CharField(max_length=256, verbose_name=b'City'),
        ),
        migrations.AlterField(
            model_name='bsoutageuptimereport',
            name='organization',
            field=models.CharField(max_length=128, verbose_name=b'Organization'),
        ),
        migrations.AlterField(
            model_name='bsoutageuptimereport',
            name='total_uptime_min',
            field=models.CharField(max_length=128, verbose_name=b'Total Uptime(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutageuptimereport',
            name='total_uptime_percent',
            field=models.CharField(max_length=128, verbose_name=b'Uptime in %'),
        ),
    ]
