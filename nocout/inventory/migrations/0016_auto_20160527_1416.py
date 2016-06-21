# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_basestation_has_pps_alarm'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseStationPpsMapper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_pps_alarm', models.BooleanField(default=False)),
                ('latest_timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='basestation',
            name='has_pps_alarm',
        ),
        migrations.AddField(
            model_name='basestationppsmapper',
            name='base_station',
            field=models.ForeignKey(to='inventory.BaseStation'),
        ),
    ]
