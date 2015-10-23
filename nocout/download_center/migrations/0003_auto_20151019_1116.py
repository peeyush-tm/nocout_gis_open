# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0002_auto_20151016_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bsoutagefaultdaily',
            name='outage_count',
            field=models.CharField(max_length=100, verbose_name=b'Outage Count'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultmonthly',
            name='outage_count',
            field=models.CharField(max_length=100, verbose_name=b'Outage Count'),
        ),
        migrations.AlterField(
            model_name='bsoutagefaultweekly',
            name='outage_count',
            field=models.CharField(max_length=100, verbose_name=b'Outage Count'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='alarm_outage_min',
            field=models.CharField(max_length=100, verbose_name=b'Alarm Outage(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='alarm_restored_timestamp',
            field=models.CharField(max_length=150, null=True, verbose_name=b'Alarm Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='bs_ip',
            field=models.CharField(max_length=150, verbose_name=b'BS IP Address'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='delay',
            field=models.CharField(max_length=100, verbose_name=b'Delay'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='fault_description',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Remark/Detail Fault Description', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='fault_history',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Fault History', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='mttr_hrs',
            field=models.CharField(max_length=100, verbose_name=b'MTTR Hrs'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='outage_timestamp',
            field=models.CharField(max_length=150, null=True, verbose_name=b'Outage Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='outage_total_min',
            field=models.CharField(max_length=100, verbose_name=b'Outage Total(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='restored_timestamp',
            field=models.CharField(max_length=150, null=True, verbose_name=b'Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='spot_cases',
            field=models.CharField(max_length=100, verbose_name=b'Spot Cases'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='tac_tt_number',
            field=models.CharField(max_length=100, verbose_name=b'Tac TT Number'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='total_affected_bs',
            field=models.CharField(max_length=100, verbose_name=b'Number of BS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='total_affected_enterprise_ss',
            field=models.CharField(max_length=100, verbose_name=b'Number of Enterprise SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='total_affected_retail_ss',
            field=models.CharField(max_length=100, verbose_name=b'Number of Retail SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterdaily',
            name='total_affected_sector',
            field=models.CharField(max_length=100, verbose_name=b'Number of Sectors Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='alarm_outage_min',
            field=models.CharField(max_length=100, verbose_name=b'Alarm Outage(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='alarm_restored_timestamp',
            field=models.CharField(max_length=150, null=True, verbose_name=b'Alarm Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='bs_ip',
            field=models.CharField(max_length=150, verbose_name=b'BS IP Address'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='delay',
            field=models.CharField(max_length=100, verbose_name=b'Delay'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='fault_description',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Remark/Detail Fault Description', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='fault_history',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Fault History', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='mttr_hrs',
            field=models.CharField(max_length=100, verbose_name=b'MTTR Hrs'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='outage_timestamp',
            field=models.CharField(max_length=150, null=True, verbose_name=b'Outage Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='outage_total_min',
            field=models.CharField(max_length=100, verbose_name=b'Outage Total(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='restored_timestamp',
            field=models.CharField(max_length=150, null=True, verbose_name=b'Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='spot_cases',
            field=models.CharField(max_length=100, verbose_name=b'Spot Cases'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='tac_tt_number',
            field=models.CharField(max_length=100, verbose_name=b'Tac TT Number'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='total_affected_bs',
            field=models.CharField(max_length=100, verbose_name=b'Number of BS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='total_affected_enterprise_ss',
            field=models.CharField(max_length=100, verbose_name=b'Number of Enterprise SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='total_affected_retail_ss',
            field=models.CharField(max_length=100, verbose_name=b'Number of Retail SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemastermonthly',
            name='total_affected_sector',
            field=models.CharField(max_length=100, verbose_name=b'Number of Sectors Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='alarm_outage_min',
            field=models.CharField(max_length=100, verbose_name=b'Alarm Outage(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='alarm_restored_timestamp',
            field=models.CharField(max_length=150, null=True, verbose_name=b'Alarm Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='bs_ip',
            field=models.CharField(max_length=150, verbose_name=b'BS IP Address'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='delay',
            field=models.CharField(max_length=100, verbose_name=b'Delay'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='fault_description',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Remark/Detail Fault Description', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='fault_history',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Fault History', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='mttr_hrs',
            field=models.CharField(max_length=100, verbose_name=b'MTTR Hrs'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='outage_timestamp',
            field=models.CharField(max_length=150, null=True, verbose_name=b'Outage Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='outage_total_min',
            field=models.CharField(max_length=100, verbose_name=b'Outage Total(Min.)'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='restored_timestamp',
            field=models.CharField(max_length=150, null=True, verbose_name=b'Restored Date And Time', blank=True),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='spot_cases',
            field=models.CharField(max_length=100, verbose_name=b'Spot Cases'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='tac_tt_number',
            field=models.CharField(max_length=100, verbose_name=b'Tac TT Number'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='total_affected_bs',
            field=models.CharField(max_length=100, verbose_name=b'Number of BS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='total_affected_enterprise_ss',
            field=models.CharField(max_length=100, verbose_name=b'Number of Enterprise SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='total_affected_retail_ss',
            field=models.CharField(max_length=100, verbose_name=b'Number of Retail SS Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemasterweekly',
            name='total_affected_sector',
            field=models.CharField(max_length=100, verbose_name=b'Number of Sectors Affected'),
        ),
        migrations.AlterField(
            model_name='bsoutagemttrprocessed',
            name='processed_on',
            field=models.CharField(max_length=150, verbose_name=b'Processed Date and Time'),
        ),
    ]
