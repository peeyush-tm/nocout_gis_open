# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0016_auto_20160808_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviceticket',
            name='is_manual',
            field=models.BooleanField(default=False, verbose_name=b'Is Manual Ticket'),
        ),
    ]
