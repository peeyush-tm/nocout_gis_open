# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_management', '0004_auto_20150720_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='repeat_every',
            field=models.IntegerField(null=True, verbose_name=b'Repeat every', blank=True),
        ),
    ]
