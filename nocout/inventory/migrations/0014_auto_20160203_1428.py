# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_circuitcontacts_powersignals'),
    ]

    operations = [
        migrations.AlterField(
            model_name='powersignals',
            name='signal_type',
            field=models.CharField(default=b'Received', max_length=32, null=True, verbose_name=b'Signal Type', blank=True),
        ),
    ]
