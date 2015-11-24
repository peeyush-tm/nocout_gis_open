# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0008_auto_20151020_1658'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_list', models.CharField(max_length=128, verbose_name=b'To')),
                ('subject', models.CharField(max_length=128, null=True, verbose_name=b'Subject', blank=True)),
                ('message', models.CharField(max_length=400, null=True, verbose_name=b'Message', blank=True)),
                ('report_type', models.CharField(max_length=3, verbose_name=b'Report Type', choices=[(b'CustomerReport', b'Customer Report'), (b'NetworkReport', b'Network Report'), (b'Fault Report', b'Fault Report')])),
            ],
        ),
    ]
