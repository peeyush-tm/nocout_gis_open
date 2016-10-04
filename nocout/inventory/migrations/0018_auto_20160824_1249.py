# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0017_auto_20160528_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backhaul',
            name='pe_ip',
            field=models.ForeignKey(related_name='pe_ip', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='device.Device', null=True),
        ),
    ]
