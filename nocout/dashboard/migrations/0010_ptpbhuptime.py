# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
        ('dashboard', '0009_auto_20160412_1409'),
    ]

    operations = [
        migrations.CreateModel(
            name='PTPBHUptime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_name', models.CharField(max_length=100, null=True, verbose_name=b'Device Name', blank=True)),
                ('ip_address', models.CharField(max_length=20, null=True, verbose_name=b'IP Address', blank=True)),
                ('uptime_percent', models.CharField(max_length=10, null=True, verbose_name=b'Uptime percent', blank=True)),
                ('datetime', models.DateTimeField(max_length=100, null=True, verbose_name=b'Date-Time', blank=True)),
                ('organization', models.ForeignKey(to='organization.Organization')),
            ],
        ),
    ]
