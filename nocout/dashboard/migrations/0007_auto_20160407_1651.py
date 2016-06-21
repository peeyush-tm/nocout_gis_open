# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_sectorstatusalerts'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackhaulSummaryStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bs_name', models.CharField(max_length=256, null=True, verbose_name=b'BS Name', blank=True)),
                ('ip_address', models.CharField(max_length=256, null=True, verbose_name=b'BHConfigured on  IP', blank=True)),
                ('bh_port_name', models.CharField(max_length=256, null=True, verbose_name=b'BH Configured on Port', blank=True)),
                ('bh_connectivity', models.CharField(max_length=256, null=True, verbose_name=b'Onnet/Offnet', blank=True)),
                ('bh_type', models.CharField(max_length=256, null=True, verbose_name=b'BH Type', blank=True)),
                ('bh_capacity', models.CharField(max_length=256, null=True, verbose_name=b'BH Capacity', blank=True)),
                ('technology', models.CharField(max_length=256, null=True, verbose_name=b'Technology', blank=True)),
                ('ageing_dl_na', models.CharField(max_length=256, null=True, verbose_name=b'Ageing DL Need Augmentation', blank=True)),
                ('ageing_dl_sp', models.CharField(max_length=256, null=True, verbose_name=b'Ageing DL Stop Provisioning', blank=True)),
                ('ageing_ul_na', models.CharField(max_length=256, null=True, verbose_name=b'Ageing ageing_ul_na Need Augmentation', blank=True)),
                ('ageing_ul_sp', models.CharField(max_length=256, null=True, verbose_name=b'Ageing UL Stop Provisioning', blank=True)),
                ('timestamp', models.DateTimeField(null=True, verbose_name=b'Report Month', blank=True)),
            ],
        ),
        migrations.RenameModel(
            old_name='SectorStatusAlerts',
            new_name='SectorSummaryStatus',
        ),
    ]
