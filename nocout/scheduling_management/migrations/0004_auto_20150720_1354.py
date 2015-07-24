# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_management', '0003_auto_20150720_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='device_type',
            field=models.ManyToManyField(to='device.DeviceType', blank=True),
        ),
    ]
