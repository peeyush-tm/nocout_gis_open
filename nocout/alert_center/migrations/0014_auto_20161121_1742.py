# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alert_center', '0013_manualticketinghistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plannedevent',
            name='device_type',
            field=models.ForeignKey(blank=True, to='device.DeviceType', null=True),
        ),
        migrations.AlterField(
            model_name='plannedevent',
            name='technology',
            field=models.ForeignKey(blank=True, to='device.DeviceTechnology', null=True),
        ),
    ]
