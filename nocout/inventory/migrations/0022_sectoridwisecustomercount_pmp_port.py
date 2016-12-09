# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0021_bswisecustomercount_bs_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectoridwisecustomercount',
            name='pmp_port',
            field=models.CharField(max_length=64, null=True, verbose_name=b'PMP Port', blank=True),
        ),
    ]
