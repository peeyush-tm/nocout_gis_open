# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capacity_management', '0002_auto_20160422_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectorcapacitystatus',
            name='peak_in_duration',
            field=models.IntegerField(default=0, verbose_name=b'Peak In Duration'),
        ),
        migrations.AddField(
            model_name='sectorcapacitystatus',
            name='peak_out_duration',
            field=models.IntegerField(default=0, verbose_name=b'Peak Out Duration'),
        ),
    ]
