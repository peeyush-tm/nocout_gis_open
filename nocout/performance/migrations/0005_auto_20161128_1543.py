# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0004_pingstabilitytest'),
    ]

    operations = [
        migrations.AddField(
            model_name='pingstabilitytest',
            name='circuit_id',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Circuit ID', blank=True),
        ),
        migrations.AddField(
            model_name='pingstabilitytest',
            name='customer_name',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Customer Name', blank=True),
        ),
    ]
