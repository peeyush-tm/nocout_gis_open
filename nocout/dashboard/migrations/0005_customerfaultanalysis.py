# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_rfoanalysis_mttr'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerFaultAnalysis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial_no', models.CharField(max_length=256, null=True, verbose_name=b'Serial No.', blank=True)),
                ('docket_id', models.CharField(max_length=256, null=True, verbose_name=b'Docket ID', blank=True)),
                ('severity', models.CharField(max_length=256, null=True, verbose_name=b'Severity', blank=True)),
                ('downtime_slab', models.CharField(max_length=256, null=True, verbose_name=b'Downtime Slab', blank=True)),
                ('timestamp', models.DateTimeField(null=True, verbose_name=b'Report Month', blank=True)),
            ],
        ),
    ]
