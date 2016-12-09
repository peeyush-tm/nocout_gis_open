# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_powersignals_ticket_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='BSWiseCustomerCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('base_station', models.CharField(max_length=256, verbose_name=b'BS Alias')),
                ('customer_count', models.IntegerField(default=0, verbose_name=b'Customer Count')),
            ],
        ),
        migrations.CreateModel(
            name='IPWiseCustomerCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip_address', models.GenericIPAddressField(verbose_name=b'IP Address')),
                ('item_type', models.CharField(default=b'sector', max_length=64, verbose_name=b'Item Type')),
                ('customer_count', models.IntegerField(default=0, verbose_name=b'Customer Count')),
            ],
        ),
        migrations.CreateModel(
            name='SectorIDWiseCustomerCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sector_id', models.CharField(max_length=256, verbose_name=b'Sector ID')),
                ('ip_address', models.GenericIPAddressField(verbose_name=b'IP Address')),
                ('customer_count', models.IntegerField(default=0, verbose_name=b'Customer Count')),
            ],
        ),
    ]
