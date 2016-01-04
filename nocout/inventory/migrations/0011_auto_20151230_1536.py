# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basestation',
            name='bh_port_name',
            field=models.CharField(max_length=100, null=True, verbose_name=b' BH Port Name', blank=True),
        ),
    ]
