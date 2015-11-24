# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alert_center', '0002_auto_20151121_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='clearalarms',
            name='alarm_count',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='clearalarms',
            name='first_occurred',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='clearalarms',
            name='is_active',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='clearalarms',
            name='last_occurred',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='currentalarms',
            name='alarm_count',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='currentalarms',
            name='first_occurred',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='currentalarms',
            name='is_active',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='currentalarms',
            name='last_occurred',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historyalarms',
            name='alarm_count',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historyalarms',
            name='first_occurred',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historyalarms',
            name='is_active',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historyalarms',
            name='last_occurred',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
