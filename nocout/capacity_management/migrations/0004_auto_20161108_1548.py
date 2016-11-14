# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capacity_management', '0003_auto_20161027_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectorcapacitystatus',
            name='timeslot_dl',
            field=models.FloatField(default=0, verbose_name=b'Dynamic TimeSlot-DL'),
        ),
        migrations.AddField(
            model_name='sectorcapacitystatus',
            name='timeslot_ul',
            field=models.FloatField(default=0, verbose_name=b'Dynamic TimeSlot-UL'),
        ),
    ]
