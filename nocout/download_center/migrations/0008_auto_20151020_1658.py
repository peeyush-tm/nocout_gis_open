# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0007_auto_20151020_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='bsoutagemasterdaily',
            name='processed_report',
            field=models.ForeignKey(blank=True, to='download_center.ProcessedReportDetails', null=True),
        ),
        migrations.AddField(
            model_name='bsoutagemastermonthly',
            name='processed_report',
            field=models.ForeignKey(blank=True, to='download_center.ProcessedReportDetails', null=True),
        ),
        migrations.AddField(
            model_name='bsoutagemasterweekly',
            name='processed_report',
            field=models.ForeignKey(blank=True, to='download_center.ProcessedReportDetails', null=True),
        ),
    ]
