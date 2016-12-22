# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0016_dashboardsetting_device_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardsetting',
            name='name',
            field=models.CharField(max_length=250, verbose_name=b'Dashboard Name', choices=[(b'latency-pmp', b'latency-pmp'), (b'packetloss-network', b'packetloss-network'), (b'down-wimax', b'down-wimax'), (b'ul_uas', b'ul_uas'), (b'uas', b'uas'), (b'modulation_dl_fec', b'modulation_dl_fec'), (b'modulation_ul_fec', b'modulation_ul_fec'), (b'down-pmp', b'down-pmp'), (b'down-network', b'down-network'), (b'rad5k_ss_dl_modulation', b'rad5k_ss_dl_modulation'), (b'availability', b'availability'), (b'latency-network', b'latency-network'), (b'ul_rssi', b'ul_rssi'), (b'topology-pmp', b'topology-pmp'), (b'temperature', b'temperature'), (b'topology-wimax', b'topology-wimax'), (b'rad5k_ss_ul_modulation', b'rad5k_ss_ul_modulation'), (b'ul_cinr', b'ul_cinr'), (b'packetloss-wimax', b'packetloss-wimax'), (b'latency-wimax', b'latency-wimax'), (b'dl_rssi', b'dl_rssi'), (b'dl_jitter', b'dl_jitter'), (b'packetloss-pmp', b'packetloss-pmp'), (b'ul_jitter', b'ul_jitter'), (b'latency-p2p-bh', b'latency-p2p-bh'), (b'rereg_count', b'rereg_count'), (b'dl_cinr', b'dl_cinr'), (b'dl_uas', b'dl_uas'), (b'rssi', b'rssi')]),
        ),
        migrations.AlterUniqueTogether(
            name='dashboardsetting',
            unique_together=set([('name', 'page_name', 'technology', 'is_bh', 'device_type')]),
        ),
    ]
