# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0011_auto_20150720_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='parent_port',
            field=models.ForeignKey(related_name='parent_port', blank=True, to='device.DevicePort', null=True),
        ),
    ]
