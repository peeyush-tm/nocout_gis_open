# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_auto_20160203_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='basestation',
            name='has_pps_alarm',
            field=models.BooleanField(default=False, verbose_name=b'Has PPS Alarm'),
        ),
    ]
