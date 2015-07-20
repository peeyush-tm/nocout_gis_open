# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClearAlarms',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('device_name', models.CharField(max_length=128)),
                ('ip_address', models.CharField(max_length=20)),
                ('device_type', models.CharField(max_length=50)),
                ('device_technology', models.CharField(max_length=50)),
                ('device_vendor', models.CharField(max_length=50)),
                ('device_model', models.CharField(max_length=50)),
                ('trapoid', models.CharField(max_length=100)),
                ('eventname', models.CharField(max_length=100)),
                ('eventno', models.CharField(max_length=50)),
                ('severity', models.CharField(max_length=20)),
                ('uptime', models.CharField(max_length=20)),
                ('traptime', models.CharField(max_length=30)),
                ('component_name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CurrentAlarms',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('device_name', models.CharField(max_length=128)),
                ('ip_address', models.CharField(max_length=20)),
                ('device_type', models.CharField(max_length=50)),
                ('device_technology', models.CharField(max_length=50)),
                ('device_vendor', models.CharField(max_length=50)),
                ('device_model', models.CharField(max_length=50)),
                ('trapoid', models.CharField(max_length=100)),
                ('eventname', models.CharField(max_length=100)),
                ('eventno', models.CharField(max_length=50)),
                ('severity', models.CharField(max_length=20)),
                ('uptime', models.CharField(max_length=20)),
                ('traptime', models.CharField(max_length=30)),
                ('component_name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoryAlarms',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('device_name', models.CharField(max_length=128)),
                ('ip_address', models.CharField(max_length=20)),
                ('device_type', models.CharField(max_length=50)),
                ('device_technology', models.CharField(max_length=50)),
                ('device_vendor', models.CharField(max_length=50)),
                ('device_model', models.CharField(max_length=50)),
                ('trapoid', models.CharField(max_length=100)),
                ('eventname', models.CharField(max_length=100)),
                ('eventno', models.CharField(max_length=50)),
                ('severity', models.CharField(max_length=20)),
                ('uptime', models.CharField(max_length=20)),
                ('traptime', models.CharField(max_length=30)),
                ('component_name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
