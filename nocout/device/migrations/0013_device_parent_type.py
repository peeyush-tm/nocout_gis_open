# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0012_device_parent_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='parent_type',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Parent Type', blank=True),
        ),
    ]
