# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_auto_20160411_1130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backhaulsummarystatus',
            name='dl_ageing',
        ),
        migrations.RemoveField(
            model_name='backhaulsummarystatus',
            name='severity',
        ),
        migrations.RemoveField(
            model_name='backhaulsummarystatus',
            name='ul_ageing',
        ),
        migrations.RemoveField(
            model_name='sectorsummarystatus',
            name='dl_ageing',
        ),
        migrations.RemoveField(
            model_name='sectorsummarystatus',
            name='severity',
        ),
        migrations.RemoveField(
            model_name='sectorsummarystatus',
            name='ul_ageing',
        ),
        migrations.AddField(
            model_name='backhaulsummarystatus',
            name='ageing_dl_na',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Ageing DL Need Augmentation', blank=True),
        ),
        migrations.AddField(
            model_name='backhaulsummarystatus',
            name='ageing_dl_sp',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Ageing DL Stop Provisioning', blank=True),
        ),
        migrations.AddField(
            model_name='backhaulsummarystatus',
            name='ageing_ul_na',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Ageing ageing_ul_na Need Augmentation', blank=True),
        ),
        migrations.AddField(
            model_name='backhaulsummarystatus',
            name='ageing_ul_sp',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Ageing UL Stop Provisioning', blank=True),
        ),
        migrations.AddField(
            model_name='sectorsummarystatus',
            name='ageing_dl_na',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Ageing DL Need Augmentation', blank=True),
        ),
        migrations.AddField(
            model_name='sectorsummarystatus',
            name='ageing_dl_sp',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Ageing DL Stop Provisioning', blank=True),
        ),
        migrations.AddField(
            model_name='sectorsummarystatus',
            name='ageing_ul_na',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Ageing UL Need Augmentation', blank=True),
        ),
        migrations.AddField(
            model_name='sectorsummarystatus',
            name='ageing_ul_sp',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Ageing UL Stop Provisioning', blank=True),
        ),
    ]
