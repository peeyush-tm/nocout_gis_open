# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capacity_management', '0004_auto_20161108_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectorcapacitystatus',
            name='timeslot_dl',
            field=models.FloatField(default=None, verbose_name=b'Dynamic TimeSlot-DL'),
        ),
        migrations.AlterField(
            model_name='sectorcapacitystatus',
            name='timeslot_ul',
            field=models.FloatField(default=None, verbose_name=b'Dynamic TimeSlot-UL'),
        ),
    ]
