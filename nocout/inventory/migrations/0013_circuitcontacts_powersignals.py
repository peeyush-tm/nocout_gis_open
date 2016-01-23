# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_auto_20160105_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='CircuitContacts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=15, null=True, verbose_name=b'Phone No.', blank=True)),
                ('circuit', models.ForeignKey(blank=True, to='inventory.Circuit', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PowerSignals',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=512, null=True, verbose_name=b'Message', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Created at')),
                ('signal_type', models.CharField(default=b'RECEIVED', choices=[(b'RECEIVED', b'Received'), (b'SENT', b'Sent')], max_length=32, blank=True, null=True, verbose_name=b'Signal Type')),
                ('circuit_contacts', models.ForeignKey(blank=True, to='inventory.CircuitContacts', max_length=250, null=True)),
            ],
        ),
    ]
