# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0022_sectoridwisecustomercount_pmp_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='antenna',
            name='gps',
            field=models.CharField(max_length=256, null=True, verbose_name=b'GPS', blank=True),
        ),
        migrations.AddField(
            model_name='antenna',
            name='gsu_ip',
            field=models.CharField(max_length=256, null=True, verbose_name=b'GSU IP', blank=True),
        ),
        migrations.AddField(
            model_name='basestation',
            name='sdh_pdh',
            field=models.CharField(max_length=256, null=True, verbose_name=b'SDH/PDH', blank=True),
        ),
    ]
