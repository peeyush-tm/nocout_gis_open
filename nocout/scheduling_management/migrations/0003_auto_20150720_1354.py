# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_management', '0002_auto_20150720_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='device',
            field=models.ManyToManyField(to='device.Device', blank=True),
        ),
    ]
