# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alert_center', '0007_mainalarm'),
    ]

    operations = [
        migrations.AddField(
            model_name='clearalarms',
            name='customer_count',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='clearalarms',
            name='sia',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='currentalarms',
            name='customer_count',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='currentalarms',
            name='sia',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historyalarms',
            name='customer_count',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historyalarms',
            name='sia',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
    ]
