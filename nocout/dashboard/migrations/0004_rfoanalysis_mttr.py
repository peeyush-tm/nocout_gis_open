# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20160311_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfoanalysis',
            name='mttr',
            field=models.CharField(max_length=256, null=True, verbose_name=b'MTTR', blank=True),
        ),
    ]
