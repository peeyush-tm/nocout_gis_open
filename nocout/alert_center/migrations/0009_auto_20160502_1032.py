# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alert_center', '0008_auto_20160321_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='clearalarms',
            name='technology',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Technology', blank=True),
        ),
        migrations.AddField(
            model_name='currentalarms',
            name='technology',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Technology', blank=True),
        ),
        migrations.AddField(
            model_name='historyalarms',
            name='technology',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Technology', blank=True),
        ),
    ]
