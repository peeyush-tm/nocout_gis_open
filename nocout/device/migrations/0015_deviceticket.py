# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0014_auto_20160209_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceTicket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip_address', models.CharField(max_length=128)),
                ('ticket_number', models.CharField(max_length=128)),
                ('alarm_id', models.CharField(max_length=128, null=True, blank=True)),
                ('is_active', models.IntegerField(null=True, blank=True)),
            ],
        ),
    ]
