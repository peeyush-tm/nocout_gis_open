# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0015_deviceticket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceticket',
            name='alarm_id',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Alarm id', blank=True),
        ),
        migrations.AlterField(
            model_name='deviceticket',
            name='ip_address',
            field=models.CharField(max_length=128, verbose_name=b'IP Address'),
        ),
        migrations.AlterField(
            model_name='deviceticket',
            name='ticket_number',
            field=models.CharField(max_length=128, verbose_name=b'Ticket Number'),
        ),
    ]
