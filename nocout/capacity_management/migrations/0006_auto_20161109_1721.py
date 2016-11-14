# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capacity_management', '0005_auto_20161108_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectorcapacitystatus',
            name='timeslot_dl',
            field=models.FloatField(default=None, null=True, verbose_name=b'Dynamic TimeSlot-DL'),
        ),
        migrations.AlterField(
            model_name='sectorcapacitystatus',
            name='timeslot_ul',
            field=models.FloatField(default=None, null=True, verbose_name=b'Dynamic TimeSlot-UL'),
        ),
    ]
