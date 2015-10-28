# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0005_reportsettings_report_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bsoutagefaultdaily',
            name='report_id',
        ),
        migrations.RemoveField(
            model_name='bsoutagefaultmonthly',
            name='report_id',
        ),
        migrations.RemoveField(
            model_name='bsoutagefaultweekly',
            name='report_id',
        ),
        migrations.RemoveField(
            model_name='bsoutagemttrprocessed',
            name='report_id',
        ),
        migrations.RemoveField(
            model_name='bsoutageuptimereport',
            name='report_id',
        ),
        migrations.DeleteModel(
            name='BSOutageFaultDaily',
        ),
        migrations.DeleteModel(
            name='BSOutageFaultMonthly',
        ),
        migrations.DeleteModel(
            name='BSOutageFaultWeekly',
        ),
        migrations.DeleteModel(
            name='BSOutageMTTRProcessed',
        ),
        migrations.DeleteModel(
            name='BSOutageUptimeReport',
        ),
    ]
