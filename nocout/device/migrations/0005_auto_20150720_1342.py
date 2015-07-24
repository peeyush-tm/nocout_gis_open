# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0004_auto_20150720_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='is_added_to_nms',
            field=models.IntegerField(default=0, verbose_name=b'Is Added'),
        ),
        migrations.AlterField(
            model_name='device',
            name='is_deleted',
            field=models.IntegerField(default=0, verbose_name=b'Is Deleted'),
        ),
        migrations.AlterField(
            model_name='device',
            name='is_monitored_on_nms',
            field=models.IntegerField(default=0, verbose_name=b'Is Monitored'),
        ),
    ]
