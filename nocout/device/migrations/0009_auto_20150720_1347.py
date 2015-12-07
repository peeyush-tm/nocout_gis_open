# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0008_auto_20150720_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicemodel',
            name='device_types',
            field=models.ManyToManyField(to='device.DeviceType', through='device.ModelType', blank=True),
        ),
    ]
