# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0016_sector_rfs_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='basestation',
            name='has_pps_alarm',
            field=models.BooleanField(default=False, verbose_name=b'Has PPS Alarm'),
        ),
    ]
