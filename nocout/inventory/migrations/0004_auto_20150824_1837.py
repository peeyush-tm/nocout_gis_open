# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_auto_20150727_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='backhaul',
            name='bh_provider',
            field=models.CharField(max_length=250, null=True, verbose_name=b'BH Provider', blank=True),
        ),
        migrations.AddField(
            model_name='backhaul',
            name='ior_id',
            field=models.CharField(max_length=250, null=True, verbose_name=b'IOR ID', blank=True),
        ),
        migrations.AddField(
            model_name='basestation',
            name='mgmt_vlan',
            field=models.CharField(max_length=250, null=True, verbose_name=b'MGMT VLAN', blank=True),
        ),
        migrations.AddField(
            model_name='basestation',
            name='site_ams',
            field=models.CharField(max_length=250, null=True, verbose_name=b'Site AMS', blank=True),
        ),
        migrations.AddField(
            model_name='basestation',
            name='site_infra_type',
            field=models.CharField(max_length=250, null=True, verbose_name=b'Site Infra Type', blank=True),
        ),
        migrations.AddField(
            model_name='basestation',
            name='site_sap_id',
            field=models.CharField(max_length=250, null=True, verbose_name=b'Site SAP ID', blank=True),
        ),
        migrations.AddField(
            model_name='circuit',
            name='sold_cir',
            field=models.FloatField(help_text=b'(mbps) Enter a number.', null=True, verbose_name=b'Customer Sold CIR', blank=True),
        ),
        migrations.AddField(
            model_name='sector',
            name='rfs_date',
            field=models.DateField(null=True, verbose_name=b'RFS Date', blank=True),
        ),
        migrations.AddField(
            model_name='substation',
            name='cpe_vlan',
            field=models.CharField(max_length=250, null=True, verbose_name=b'CPE VLAN', blank=True),
        ),
        migrations.AddField(
            model_name='substation',
            name='sacfa_no',
            field=models.CharField(max_length=250, null=True, verbose_name=b'SACFA No.', blank=True),
        ),
    ]
