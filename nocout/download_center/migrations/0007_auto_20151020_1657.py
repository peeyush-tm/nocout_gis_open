# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0006_auto_20151020_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bsoutagemaindaily',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='bsoutagemaindaily',
            name='report_id',
        ),
        migrations.RemoveField(
            model_name='bsoutagemainmonthly',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='bsoutagemainmonthly',
            name='report_id',
        ),
        migrations.RemoveField(
            model_name='bsoutagemainweekly',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='bsoutagemainweekly',
            name='report_id',
        ),
    ]
