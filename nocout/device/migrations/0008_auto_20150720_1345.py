# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0007_auto_20150720_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicetype',
            name='service',
            field=models.ManyToManyField(to='service.Service', through='device.DeviceTypeService', blank=True),
        ),
    ]
