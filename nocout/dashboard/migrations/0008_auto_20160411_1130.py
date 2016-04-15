# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_auto_20160407_1651'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backhaulsummarystatus',
            name='ageing_dl_na',
        ),
        migrations.RemoveField(
            model_name='backhaulsummarystatus',
            name='ageing_dl_sp',
        ),
        migrations.RemoveField(
            model_name='backhaulsummarystatus',
            name='ageing_ul_na',
        ),
        migrations.RemoveField(
            model_name='backhaulsummarystatus',
            name='ageing_ul_sp',
        ),
        migrations.RemoveField(
            model_name='sectorsummarystatus',
            name='ageing_dl_na',
        ),
        migrations.RemoveField(
            model_name='sectorsummarystatus',
            name='ageing_dl_sp',
        ),
        migrations.RemoveField(
            model_name='sectorsummarystatus',
            name='ageing_ul_na',
        ),
        migrations.RemoveField(
            model_name='sectorsummarystatus',
            name='ageing_ul_sp',
        ),
        migrations.AddField(
            model_name='backhaulsummarystatus',
            name='dl_ageing',
            field=models.CharField(max_length=256, null=True, verbose_name=b'DL Ageing', blank=True),
        ),
        migrations.AddField(
            model_name='backhaulsummarystatus',
            name='severity',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Severity', blank=True),
        ),
        migrations.AddField(
            model_name='backhaulsummarystatus',
            name='ul_ageing',
            field=models.CharField(max_length=256, null=True, verbose_name=b'UL Ageing', blank=True),
        ),
        migrations.AddField(
            model_name='sectorsummarystatus',
            name='dl_ageing',
            field=models.CharField(max_length=256, null=True, verbose_name=b'DL Ageing', blank=True),
        ),
        migrations.AddField(
            model_name='sectorsummarystatus',
            name='severity',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Severity', blank=True),
        ),
        migrations.AddField(
            model_name='sectorsummarystatus',
            name='ul_ageing',
            field=models.CharField(max_length=256, null=True, verbose_name=b'UL Ageing', blank=True),
        ),
    ]
