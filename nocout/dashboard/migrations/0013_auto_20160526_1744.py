# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ptpbhuptime',
            name='datetime',
        ),
        migrations.RemoveField(
            model_name='ptpbhuptime',
            name='device_name',
        ),
        migrations.RemoveField(
            model_name='ptpbhuptime',
            name='ip_address',
        ),
        migrations.RemoveField(
            model_name='ptpbhuptime',
            name='organization',
        ),
        migrations.AddField(
            model_name='ptpbhuptime',
            name='timestamp',
            field=models.DateTimeField(max_length=100, null=True, verbose_name=b'Time', blank=True),
        ),
    ]
