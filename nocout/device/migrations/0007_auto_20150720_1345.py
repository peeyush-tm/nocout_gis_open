# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0006_auto_20150720_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicetype',
            name='device_port',
            field=models.ManyToManyField(to='device.DevicePort', blank=True),
        ),
    ]
