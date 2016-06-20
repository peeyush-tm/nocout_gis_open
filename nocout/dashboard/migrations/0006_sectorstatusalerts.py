# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_customerfaultanalysis'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectorStatusAlerts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bs_name', models.CharField(max_length=256, null=True, verbose_name=b'BS Name', blank=True)),
                ('ip_address', models.CharField(max_length=256, null=True, verbose_name=b'IP Address', blank=True)),
                ('pmp_port', models.CharField(max_length=256, null=True, verbose_name=b'PMP Port', blank=True)),
                ('sector_id', models.CharField(max_length=256, null=True, verbose_name=b'Sector ID', blank=True)),
                ('technology', models.CharField(max_length=256, null=True, verbose_name=b'Technology', blank=True)),
                ('ageing_dl_na', models.CharField(max_length=256, null=True, verbose_name=b'Ageing DL Need Augmentation', blank=True)),
                ('ageing_dl_sp', models.CharField(max_length=256, null=True, verbose_name=b'Ageing DL Stop Provisioning', blank=True)),
                ('ageing_ul_na', models.CharField(max_length=256, null=True, verbose_name=b'Ageing UL Need Augmentation', blank=True)),
                ('ageing_ul_sp', models.CharField(max_length=256, null=True, verbose_name=b'Ageing UL Stop Provisioning', blank=True)),
                ('timestamp', models.DateTimeField(null=True, verbose_name=b'Report Month', blank=True)),
            ],
        ),
    ]
