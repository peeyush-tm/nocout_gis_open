# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_auto_20160824_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='powersignals',
            name='ticket_id',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Ticket ID', blank=True),
        ),
    ]
