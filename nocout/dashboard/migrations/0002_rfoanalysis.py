# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RFOAnalysis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pb_tt_no', models.CharField(max_length=256, null=True, verbose_name=b'PB TT NO', blank=True)),
                ('city', models.CharField(max_length=256, null=True, verbose_name=b'City', blank=True)),
                ('state', models.CharField(max_length=256, null=True, verbose_name=b'State', blank=True)),
                ('master_causecode', models.CharField(max_length=256, null=True, verbose_name=b'Master Cause Code', blank=True)),
                ('sub_causecode', models.CharField(max_length=256, null=True, verbose_name=b'Sub Cause Code', blank=True)),
                ('outage_in_minutes', models.CharField(max_length=256, null=True, verbose_name=b'Outage In Minutes', blank=True)),
                ('timestamp', models.DateField(null=True, verbose_name=b'Report Month', blank=True)),
            ],
        ),
    ]
