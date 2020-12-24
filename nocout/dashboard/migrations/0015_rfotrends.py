# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_customerfaultanalysis_actual_downtime'),
    ]

    operations = [
        migrations.CreateModel(
            name='RFOTrends',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('docket_id', models.CharField(max_length=256, null=True, verbose_name=b'Docket ID', blank=True)),
                ('city', models.CharField(max_length=256, null=True, verbose_name=b'City', blank=True)),
                ('state', models.CharField(max_length=256, null=True, verbose_name=b'State', blank=True)),
                ('main_causecode', models.CharField(max_length=256, null=True, verbose_name=b'Main Cause Code', blank=True)),
                ('sub_causecode', models.CharField(max_length=256, null=True, verbose_name=b'Sub Cause Code', blank=True)),
                ('actual_downtime', models.CharField(max_length=256, null=True, verbose_name=b'Actual Downtime', blank=True)),
                ('severity', models.CharField(max_length=256, null=True, verbose_name=b'Severity', blank=True)),
                ('timestamp', models.DateTimeField(null=True, verbose_name=b'Report Month', blank=True)),
            ],
        ),
    ]
