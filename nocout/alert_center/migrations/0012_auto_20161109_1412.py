# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alert_center', '0011_auto_20161104_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='clearalarms',
            name='is_manual',
            field=models.BooleanField(default=False, verbose_name=b'Is Manual Ticket'),
        ),
        migrations.AddField(
            model_name='clearalarms',
            name='ticket_number',
            field=models.CharField(max_length=64, null=True, verbose_name=b'Ticket Number', blank=True),
        ),
        migrations.AddField(
            model_name='currentalarms',
            name='is_manual',
            field=models.BooleanField(default=False, verbose_name=b'Is Manual Ticket'),
        ),
        migrations.AddField(
            model_name='currentalarms',
            name='ticket_number',
            field=models.CharField(max_length=64, null=True, verbose_name=b'Ticket Number', blank=True),
        ),
        migrations.AddField(
            model_name='historyalarms',
            name='is_manual',
            field=models.BooleanField(default=False, verbose_name=b'Is Manual Ticket'),
        ),
        migrations.AddField(
            model_name='historyalarms',
            name='ticket_number',
            field=models.CharField(max_length=64, null=True, verbose_name=b'Ticket Number', blank=True),
        ),
    ]
