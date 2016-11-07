# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0018_auto_20160928_1229'),
        ('alert_center', '0009_auto_20160502_1032'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlannedEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startdate', models.IntegerField(default=0, verbose_name=b'Scheduled Start Datetime')),
                ('enddate', models.IntegerField(default=0, verbose_name=b'Scheduled End Datetime')),
                ('event_type', models.CharField(max_length=128, null=True, verbose_name=b'Event Type', blank=True)),
                ('owner_details', models.CharField(max_length=255, null=True, verbose_name=b'PE Owner Details', blank=True)),
                ('change_coordinator', models.CharField(max_length=255, null=True, verbose_name=b'Change Coordinator', blank=True)),
                ('pettno', models.CharField(max_length=255, null=True, verbose_name=b'PE TT No.', blank=True)),
                ('sr_number', models.CharField(max_length=255, null=True, verbose_name=b'SR Number', blank=True)),
                ('impacted_customer', models.IntegerField(default=0, verbose_name=b'Impacted Customer')),
                ('timing', models.CharField(max_length=255, null=True, verbose_name=b'Timing', blank=True)),
                ('summary', models.CharField(max_length=255, null=True, verbose_name=b'Change Summary', blank=True)),
                ('status', models.CharField(max_length=255, null=True, verbose_name=b'Change Status', blank=True)),
                ('impacted_domain', models.CharField(max_length=255, null=True, verbose_name=b'Impacted Domain', blank=True)),
                ('component', models.CharField(max_length=255, null=True, verbose_name=b'Component', blank=True)),
                ('sectorid', models.CharField(max_length=255, null=True, verbose_name=b'SectorID', blank=True)),
                ('resource_name', models.CharField(max_length=255, null=True, verbose_name=b'Resource Name/IP Address', blank=True)),
                ('service_ids', models.TextField(null=True, verbose_name=b'Service IDs', blank=True)),
                ('nia', models.TextField(null=True, verbose_name=b'NIA', blank=True)),
                ('device_type', models.ForeignKey(to='device.DeviceType')),
                ('technnology', models.ForeignKey(to='device.DeviceTechnology')),
            ],
        ),
    ]
