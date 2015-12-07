# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0011_auto_20150720_1348'),
        ('inventory', '0003_auto_20150727_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='livepollingsettings',
            name='device_type',
            field=models.ForeignKey(to='device.DeviceType', null=True),
        ),
        migrations.AddField(
            model_name='userthematicsettings',
            name='thematic_type',
            field=models.ForeignKey(to='device.DeviceType', null=True),
        ),
    ]
