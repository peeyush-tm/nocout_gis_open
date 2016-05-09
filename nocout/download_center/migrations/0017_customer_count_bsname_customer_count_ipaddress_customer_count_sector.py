# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0016_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer_Count_BSname',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bs_name', models.CharField(max_length=55, null=True, verbose_name=b'Base Station Name')),
                ('bs_converter', models.CharField(max_length=55, null=True, verbose_name=b'BS Converter')),
                ('bs_switch', models.CharField(max_length=45, null=True, verbose_name=b'BS Switch')),
                ('pop_converter', models.CharField(max_length=45, null=True, verbose_name=b'POP Converter')),
                ('count_of_customer', models.CharField(max_length=45, null=True, verbose_name=b'Count Of Customer')),
                ('technology', models.CharField(max_length=45, null=True, verbose_name=b'Technology')),
            ],
        ),
        migrations.CreateModel(
            name='Customer_Count_IPaddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sector_config_ip', models.CharField(max_length=55, null=True, verbose_name=b'Sector Config IP')),
                ('bs_name', models.CharField(max_length=55, null=True, verbose_name=b'BS Name')),
                ('count_of_customer', models.CharField(max_length=55, null=True, verbose_name=b'Count Of Customer')),
                ('technology', models.CharField(max_length=55, null=True, verbose_name=b'Technology')),
            ],
        ),
        migrations.CreateModel(
            name='Customer_Count_Sector',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sector_id', models.CharField(max_length=55, null=True, verbose_name=b'Sector ID')),
                ('sector_config_ip', models.CharField(max_length=55, null=True, verbose_name=b'Sector Config IP')),
                ('bs_name', models.CharField(max_length=55, null=True, verbose_name=b'BS Name')),
                ('count_of_customer', models.CharField(max_length=55, null=True, verbose_name=b'Count Of Customer')),
                ('technology', models.CharField(max_length=55, null=True, verbose_name=b'Technology')),
            ],
        ),
    ]
