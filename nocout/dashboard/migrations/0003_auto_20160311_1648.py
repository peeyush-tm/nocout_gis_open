# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_rfoanalysis'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rfoanalysis',
            name='timestamp',
            field=models.DateTimeField(null=True, verbose_name=b'Report Month', blank=True),
        ),
    ]
