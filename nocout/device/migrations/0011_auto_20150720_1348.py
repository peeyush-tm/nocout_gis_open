# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0010_auto_20150720_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicetechnology',
            name='device_vendors',
            field=models.ManyToManyField(to='device.DeviceVendor', through='device.TechnologyVendor', blank=True),
        ),
    ]
