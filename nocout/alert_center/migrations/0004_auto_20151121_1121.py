# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alert_center', '0003_auto_20151121_1120'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusAlarms',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('device_name', models.CharField(max_length=128)),
                ('ip_address', models.CharField(max_length=20)),
                ('trapoid', models.CharField(max_length=100)),
                ('eventname', models.CharField(max_length=100)),
                ('eventno', models.CharField(max_length=50)),
                ('severity', models.CharField(max_length=20)),
                ('uptime', models.CharField(max_length=20)),
                ('traptime', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=256)),
                ('alarm_count', models.IntegerField(null=True, blank=True)),
                ('first_occurred', models.DateTimeField(null=True, blank=True)),
                ('last_occurred', models.DateTimeField(null=True, blank=True)),
                ('is_active', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='CurrentAlarms',
        ),
    ]
