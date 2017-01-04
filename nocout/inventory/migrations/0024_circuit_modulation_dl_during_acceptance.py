# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_auto_20161213_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuit',
            name='modulation_dl_during_acceptance',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Modulation DL during Acceptance', blank=True),
        ),
    ]
