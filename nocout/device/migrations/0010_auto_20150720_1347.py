# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0009_auto_20150720_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicevendor',
            name='device_models',
            field=models.ManyToManyField(to='device.DeviceModel', through='device.VendorModel', blank=True),
        ),
    ]
