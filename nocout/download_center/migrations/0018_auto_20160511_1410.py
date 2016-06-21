# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0017_customer_count_bsname_customer_count_ipaddress_customer_count_sector'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer_count_bsname',
            old_name='bs_name',
            new_name='base_station_name',
        ),
    ]
