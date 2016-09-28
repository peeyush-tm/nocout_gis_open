# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0017_deviceticket_is_manual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceticket',
            name='ip_address',
            field=models.CharField(unique=True, max_length=128, verbose_name=b'IP Address'),
        ),
    ]
