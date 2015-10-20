# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0006_auto_20151020_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bsoutagemasterdaily',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='bsoutagemasterdaily',
            name='report_id',
        ),
        migrations.RemoveField(
            model_name='bsoutagemastermonthly',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='bsoutagemastermonthly',
            name='report_id',
        ),
        migrations.RemoveField(
            model_name='bsoutagemasterweekly',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='bsoutagemasterweekly',
            name='report_id',
        ),
    ]
