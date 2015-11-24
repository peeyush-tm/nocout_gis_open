# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alert_center', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clearalarms',
            name='component_id',
        ),
        migrations.RemoveField(
            model_name='clearalarms',
            name='component_name',
        ),
        migrations.RemoveField(
            model_name='clearalarms',
            name='device_model',
        ),
        migrations.RemoveField(
            model_name='clearalarms',
            name='device_technology',
        ),
        migrations.RemoveField(
            model_name='clearalarms',
            name='device_type',
        ),
        migrations.RemoveField(
            model_name='clearalarms',
            name='device_vendor',
        ),
        migrations.RemoveField(
            model_name='currentalarms',
            name='component_id',
        ),
        migrations.RemoveField(
            model_name='currentalarms',
            name='component_name',
        ),
        migrations.RemoveField(
            model_name='currentalarms',
            name='device_model',
        ),
        migrations.RemoveField(
            model_name='currentalarms',
            name='device_technology',
        ),
        migrations.RemoveField(
            model_name='currentalarms',
            name='device_type',
        ),
        migrations.RemoveField(
            model_name='currentalarms',
            name='device_vendor',
        ),
        migrations.RemoveField(
            model_name='historyalarms',
            name='component_id',
        ),
        migrations.RemoveField(
            model_name='historyalarms',
            name='component_name',
        ),
        migrations.RemoveField(
            model_name='historyalarms',
            name='device_model',
        ),
        migrations.RemoveField(
            model_name='historyalarms',
            name='device_technology',
        ),
        migrations.RemoveField(
            model_name='historyalarms',
            name='device_type',
        ),
        migrations.RemoveField(
            model_name='historyalarms',
            name='device_vendor',
        ),
    ]
