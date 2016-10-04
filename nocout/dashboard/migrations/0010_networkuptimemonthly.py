# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_auto_20160412_1409'),
    ]

    operations = [
        migrations.CreateModel(
            name='NetworkUptimeMonthly',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bs_name', models.CharField(max_length=256, null=True, verbose_name=b'BS Name', blank=True)),
                ('ip_address', models.CharField(max_length=256, null=True, verbose_name=b'BS Device IP', blank=True)),
                ('technology', models.CharField(max_length=256, null=True, verbose_name=b'Technology', blank=True)),
                ('uptime_percent', models.CharField(max_length=256, verbose_name=b'Uptime Percent')),
                ('timestamp', models.DateTimeField(verbose_name=b'Report Month')),
            ],
        ),
    ]
