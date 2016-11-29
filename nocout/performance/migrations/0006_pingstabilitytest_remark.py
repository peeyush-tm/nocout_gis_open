# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0005_auto_20161128_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='pingstabilitytest',
            name='remark',
            field=models.CharField(max_length=512, null=True, verbose_name=b'Remark', blank=True),
        ),
    ]
