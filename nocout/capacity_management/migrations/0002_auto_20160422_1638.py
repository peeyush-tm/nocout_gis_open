# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capacity_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='avg_in_per',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'IN Current Utilization Average Percentage'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='avg_in_val',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'IN Current Utilization Average Value'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='avg_out_per',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'OUT Current Utilization Average Percentage'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='avg_out_val',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'OUT Current Utilization Average Value'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='current_in_per',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'IN Current Utilization Percentage'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='current_in_val',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'IN Current Utilization Value'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='current_out_per',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'OUT Current Utilization Percentage'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='current_out_val',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'OUT Current Utilization Value'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='peak_in_per',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'IN Peak Utilization Percentage'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='peak_in_val',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'IN Peak Utilization Value'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='peak_out_per',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'OUT Peak Utilization Percentage'),
        ),
        migrations.AlterField(
            model_name='backhaulcapacitystatus',
            name='peak_out_val',
            field=models.CharField(default=b'NA', max_length=128, verbose_name=b'OUT Peak Utilization Value'),
        ),
    ]
