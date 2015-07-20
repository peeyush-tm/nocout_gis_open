# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='repeat_on',
            field=models.ManyToManyField(to='scheduling_management.Weekdays', blank=True),
        ),
    ]
