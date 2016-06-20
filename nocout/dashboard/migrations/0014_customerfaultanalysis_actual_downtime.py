# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_auto_20160526_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerfaultanalysis',
            name='actual_downtime',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Actual Downtime', blank=True),
        ),
    ]
