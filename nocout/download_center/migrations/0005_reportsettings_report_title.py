# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0004_auto_20151019_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportsettings',
            name='report_title',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Report Title', blank=True),
        ),
    ]
