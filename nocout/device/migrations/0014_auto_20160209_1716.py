# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0013_device_parent_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='parent_port',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Parent Port', blank=True),
        ),
    ]
