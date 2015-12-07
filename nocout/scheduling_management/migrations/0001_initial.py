# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
        ('organization', '0001_initial'),
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'Title')),
                ('repeat', models.CharField(default=b'dai', max_length=10, verbose_name=b'Repeats', choices=[(b'dai', b'Daily'), (b'mtf', b'Every weekday (Monday to Friday)'), (b'mwf', b'Every Monday, Wednesday, and Friday'), (b'tat', b'Every Tuesday and Thursday'), (b'wee', b'Weekly'), (b'mon', b'Monthly'), (b'yea', b'Yearly')])),
                ('repeat_every', models.IntegerField(max_length=2, null=True, verbose_name=b'Repeat every', blank=True)),
                ('repeat_by', models.CharField(default=b'dofm', choices=[(b'dofm', b'day of the month'), (b'dofw', b'day of the week')], max_length=10, blank=True, null=True, verbose_name=b'Repeat by')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Created at')),
                ('start_on', models.DateField(verbose_name=b'Starts on')),
                ('start_on_time', models.TimeField(verbose_name=b'Start time')),
                ('end_on_time', models.TimeField(verbose_name=b'End time')),
                ('end_never', models.BooleanField(default=False, verbose_name=b'Ends')),
                ('end_after', models.IntegerField(null=True, verbose_name=b'Ends after', blank=True)),
                ('end_on', models.DateField(null=True, verbose_name=b'Ends on', blank=True)),
                ('scheduling_type', models.CharField(default=b'', max_length=10, verbose_name=b'Scheduling type', choices=[(b'', b'Select'), (b'devi', b'Device Specific'), (b'dety', b'Device Type'), (b'cust', b'Customer Device'), (b'netw', b'Network Device'), (b'back', b'Backhaul Device')])),
                ('created_by', models.ForeignKey(to='user_profile.UserProfile')),
                ('device', models.ManyToManyField(to='device.Device', null=True, blank=True)),
                ('device_type', models.ManyToManyField(to='device.DeviceType', null=True, blank=True)),
                ('organization', models.ForeignKey(to='organization.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='SNMPTrapSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name=b'Trap Name')),
                ('alias', models.CharField(max_length=150, null=True, verbose_name=b'Trap Alias', blank=True)),
                ('trap_oid', models.CharField(max_length=255, null=True, verbose_name=b'Trap OID', blank=True)),
                ('severity', models.CharField(max_length=20, null=True, verbose_name=b'Severity', blank=True)),
                ('device_model', models.ForeignKey(related_name='device_model', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='device.DeviceModel', null=True)),
                ('device_technology', models.ForeignKey(related_name='device_technology', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='device.DeviceTechnology', null=True)),
                ('device_type', models.ForeignKey(related_name='device_type', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='device.DeviceType', null=True)),
                ('device_vendor', models.ForeignKey(related_name='device_vendor', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='device.DeviceVendor', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Weekdays',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(blank=True, max_length=128, null=True, verbose_name=b'Weekdays', choices=[(b'1', b'Monday'), (b'2', b'Tuesday'), (b'3', b'Wednesday'), (b'4', b'Thursday'), (b'5', b'Friday'), (b'6', b'Saturday'), (b'7', b'Sunday')])),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='repeat_on',
            field=models.ManyToManyField(to='scheduling_management.Weekdays', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='technology',
            field=models.ForeignKey(blank=True, to='device.DeviceTechnology', null=True),
        ),
    ]
