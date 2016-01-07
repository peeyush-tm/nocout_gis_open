# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_auto_20151231_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='gisinventorybulkimport',
            name='is_auto',
            field=models.IntegerField(null=True, verbose_name=b'Is Auto', blank=True),
        ),
        migrations.AddField(
            model_name='gisinventorybulkimport',
            name='is_new',
            field=models.IntegerField(null=True, verbose_name=b'Is New', blank=True),
        ),
    ]
