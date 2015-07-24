# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0005_auto_20150720_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='ports',
            field=models.ManyToManyField(to='device.DevicePort', blank=True),
        ),
    ]
