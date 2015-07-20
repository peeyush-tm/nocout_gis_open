# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machine', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='machine_ip',
            field=models.GenericIPAddressField(null=True, verbose_name=b'Machine IP', blank=True),
        ),
    ]
