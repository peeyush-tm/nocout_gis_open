# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0007_auto_20151020_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='bsoutagemaindaily',
            name='processed_report',
            field=models.ForeignKey(blank=True, to='download_center.ProcessedReportDetails', null=True),
        ),
        migrations.AddField(
            model_name='bsoutagemainmonthly',
            name='processed_report',
            field=models.ForeignKey(blank=True, to='download_center.ProcessedReportDetails', null=True),
        ),
        migrations.AddField(
            model_name='bsoutagemainweekly',
            name='processed_report',
            field=models.ForeignKey(blank=True, to='download_center.ProcessedReportDetails', null=True),
        ),
    ]
