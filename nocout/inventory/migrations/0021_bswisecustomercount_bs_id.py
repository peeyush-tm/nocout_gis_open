# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0020_bswisecustomercount_ipwisecustomercount_sectoridwisecustomercount'),
    ]

    operations = [
        migrations.AddField(
            model_name='bswisecustomercount',
            name='bs_id',
            field=models.IntegerField(default='0', verbose_name=b'BS ID'),
            preserve_default=False,
        ),
    ]
