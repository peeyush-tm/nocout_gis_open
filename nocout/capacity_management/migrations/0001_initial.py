# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import inventory.models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackhaulCapacityStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bh_port_name', models.CharField(db_index=True, max_length=64, null=True, verbose_name=b'BH Configured On Port', blank=True)),
                ('backhaul_capacity', models.FloatField(default=0, verbose_name=b'Backhaul Capacity')),
                ('current_in_per', models.FloatField(default=0, verbose_name=b'IN Current Utilization Percentage')),
                ('current_in_val', models.FloatField(default=0, verbose_name=b'IN Current Utilization Value')),
                ('avg_in_per', models.FloatField(default=0, verbose_name=b'IN Current Utilization Average Percentage')),
                ('avg_in_val', models.FloatField(default=0, verbose_name=b'IN Current Utilization Average Value')),
                ('peak_in_per', models.FloatField(default=0, verbose_name=b'IN Peak Utilization Percentage')),
                ('peak_in_val', models.FloatField(default=0, verbose_name=b'IN Peak Utilization Value')),
                ('peak_in_timestamp', models.IntegerField(default=0, verbose_name=b'Peak In Timestamp')),
                ('current_out_per', models.FloatField(default=0, verbose_name=b'OUT Current Utilization Percentage')),
                ('current_out_val', models.FloatField(default=0, verbose_name=b'OUT Current Utilization Value')),
                ('avg_out_per', models.FloatField(default=0, verbose_name=b'OUT Current Utilization Average Percentage')),
                ('avg_out_val', models.FloatField(default=0, verbose_name=b'OUT Current Utilization Average Value')),
                ('peak_out_per', models.FloatField(default=0, verbose_name=b'OUT Peak Utilization Percentage')),
                ('peak_out_val', models.FloatField(default=0, verbose_name=b'OUT Peak Utilization Value')),
                ('peak_out_timestamp', models.IntegerField(default=0, verbose_name=b'Peak Out Timestamp')),
                ('sys_timestamp', models.IntegerField(default=0, verbose_name=b'SYS Timestamp', db_index=True)),
                ('severity', models.CharField(max_length=20, null=True, verbose_name=b'Severity', blank=True)),
                ('age', models.IntegerField(default=0, verbose_name=b'Status Age')),
                ('backhaul', models.ForeignKey(to='inventory.Backhaul')),
                ('basestation', models.ForeignKey(to='inventory.BaseStation')),
                ('organization', models.ForeignKey(default=inventory.models.get_default_org, to='organization.Organization')),
            ],
            options={
                'ordering': ['-sys_timestamp'],
            },
        ),
        migrations.CreateModel(
            name='SectorCapacityStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sector_sector_id', models.CharField(max_length=64, unique=True, null=True, verbose_name=b'Sector ID', blank=True)),
                ('sector_capacity', models.FloatField(default=0, verbose_name=b'Sector Capacity')),
                ('sector_capacity_in', models.FloatField(default=0, verbose_name=b'IN Sector Capacity')),
                ('sector_capacity_out', models.FloatField(default=0, verbose_name=b'OUT Sector Capacity')),
                ('current_in_per', models.FloatField(default=0, verbose_name=b'IN Current Utilization Percentage')),
                ('current_in_val', models.FloatField(default=0, verbose_name=b'IN Current Utilization Value')),
                ('avg_in_per', models.FloatField(default=0, verbose_name=b'IN Current Utilization Average Percentage')),
                ('avg_in_val', models.FloatField(default=0, verbose_name=b'IN Current Utilization Average Value')),
                ('peak_in_per', models.FloatField(default=0, verbose_name=b'IN Peak Utilization Percentage')),
                ('peak_in_val', models.FloatField(default=0, verbose_name=b'IN Peak Utilization Value')),
                ('peak_in_timestamp', models.IntegerField(default=0, verbose_name=b'Peak In Timestamp')),
                ('current_out_per', models.FloatField(default=0, verbose_name=b'OUT Current Utilization Percentage')),
                ('current_out_val', models.FloatField(default=0, verbose_name=b'OUT Current Utilization Value')),
                ('avg_out_per', models.FloatField(default=0, verbose_name=b'OUT Current Utilization Average Percentage')),
                ('avg_out_val', models.FloatField(default=0, verbose_name=b'OUT Current Utilization Average Value')),
                ('peak_out_per', models.FloatField(default=0, verbose_name=b'OUT Peak Utilization Percentage')),
                ('peak_out_val', models.FloatField(default=0, verbose_name=b'OUT Peak Utilization Value')),
                ('peak_out_timestamp', models.IntegerField(default=0, verbose_name=b'Peak Out Timestamp')),
                ('sys_timestamp', models.IntegerField(default=0, verbose_name=b'SYS Timestamp', db_index=True)),
                ('severity', models.CharField(max_length=20, null=True, verbose_name=b'Severity', blank=True)),
                ('age', models.IntegerField(default=0, verbose_name=b'Status Age')),
                ('organization', models.ForeignKey(default=inventory.models.get_default_org, to='organization.Organization')),
                ('sector', models.ForeignKey(to='inventory.Sector')),
            ],
            options={
                'ordering': ['-sys_timestamp'],
            },
        ),
    ]
