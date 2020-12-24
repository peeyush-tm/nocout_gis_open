# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alert_center', '0006_auto_20160125_1521'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainAlarm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alarm_name', models.CharField(max_length=256, null=True, verbose_name=b'Alarm Name', blank=True)),
                ('oid', models.CharField(max_length=256, null=True, verbose_name=b'OID', blank=True)),
                ('severity', models.CharField(max_length=16, null=True, verbose_name=b'Severity', blank=True)),
                ('device_type', models.CharField(max_length=128, null=True, verbose_name=b'Device Type', blank=True)),
                ('alarm_mode', models.CharField(max_length=32, null=True, verbose_name=b'Alarm Mode', blank=True)),
                ('alarm_type', models.CharField(max_length=32, null=True, verbose_name=b'Alarm Type', blank=True)),
                ('sia', models.IntegerField(null=True, verbose_name=b'IS SIA', blank=True)),
                ('auto_tt', models.IntegerField(null=True, verbose_name=b'Auto TT', blank=True)),
                ('correlation', models.IntegerField(null=True, verbose_name=b'Correlation', blank=True)),
                ('to_monolith', models.IntegerField(null=True, verbose_name=b'To Monolith', blank=True)),
                ('mail', models.IntegerField(null=True, verbose_name=b'Mail', blank=True)),
                ('sms', models.IntegerField(null=True, verbose_name=b'SMS', blank=True)),
                ('coverage', models.CharField(max_length=128, null=True, verbose_name=b'Coverage', blank=True)),
                ('resource_name', models.CharField(max_length=128, null=True, verbose_name=b'Resource Name', blank=True)),
                ('resource_type', models.CharField(max_length=32, null=True, verbose_name=b'Resource Type', blank=True)),
                ('support_organization', models.CharField(max_length=256, null=True, verbose_name=b'Support Organization', blank=True)),
                ('bearer_organization', models.CharField(max_length=256, null=True, verbose_name=b'Bearer Organization', blank=True)),
                ('priority', models.IntegerField(null=True, blank=True)),
                ('refer', models.CharField(max_length=256, null=True, verbose_name=b'Refer', blank=True)),
                ('alarm_category', models.CharField(max_length=256, null=True, verbose_name=b'Alarm Category', blank=True)),
            ],
            options={
                'db_table': 'main_alarm_table',
            },
        ),
    ]
