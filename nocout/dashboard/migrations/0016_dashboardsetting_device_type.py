# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0018_auto_20160928_1229'),
        ('dashboard', '0015_rfotrends'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboardsetting',
            name='device_type',
            field=models.ForeignKey(blank=True, to='device.DeviceType', null=True),
        ),
    ]
