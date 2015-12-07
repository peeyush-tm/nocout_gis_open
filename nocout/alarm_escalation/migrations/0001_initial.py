# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
        ('organization', '0001_initial'),
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EscalationLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.PositiveSmallIntegerField(default=1, choices=[(1, b'Level 1'), (2, b'Level 2'), (3, b'Level 3'), (4, b'Level 4'), (5, b'Level 5'), (6, b'Level 6'), (7, b'Level 7')])),
                ('region_name', models.CharField(default=b'', max_length=50, verbose_name=b'Location Region', blank=True)),
                ('emails', models.TextField(default=b'', verbose_name=b'Emails', blank=True)),
                ('phones', models.TextField(default=b'', verbose_name=b'Phones', blank=True)),
                ('alarm_age', models.IntegerField(verbose_name=b'Alarm Age')),
                ('device_type', models.ForeignKey(to='device.DeviceType')),
                ('organization', models.ForeignKey(to='organization.Organization')),
                ('service', models.ForeignKey(to='service.Service')),
                ('service_data_source', models.ForeignKey(to='service.ServiceDataSource')),
            ],
        ),
        migrations.CreateModel(
            name='EscalationStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.IPAddressField()),
                ('l1_email_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l1_phone_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l2_email_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l2_phone_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l3_email_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l3_phone_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l4_email_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l4_phone_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l5_email_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l5_phone_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l6_email_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l6_phone_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l7_email_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('l7_phone_status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Sent')])),
                ('status_since', models.DateTimeField(auto_now_add=True)),
                ('severity', models.CharField(max_length=20)),
                ('old_status', models.IntegerField(choices=[(0, b'Bad'), (1, b'Good')])),
                ('new_status', models.IntegerField(choices=[(0, b'Bad'), (1, b'Good')])),
                ('device', models.ForeignKey(to='device.Device')),
                ('organization', models.ForeignKey(to='organization.Organization')),
                ('service', models.ForeignKey(to='service.Service')),
                ('service_data_source', models.ForeignKey(to='service.ServiceDataSource')),
            ],
        ),
    ]
