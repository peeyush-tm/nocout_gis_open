# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0006_auto_20160218_1440'),
        ('device', '0016_auto_20160808_1545'),
        ('machine', '0002_auto_20150720_1351'),
        ('site_instance', '0001_initial'),
        ('performance', '0003_auto_20151029_1842'),
    ]

    operations = [
        migrations.CreateModel(
            name='PingStabilityTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip_address', models.GenericIPAddressField(null=True, verbose_name=b'IP Address', blank=True)),
                ('time_duration', models.IntegerField(default=1, verbose_name=b'Time Duration')),
                ('file_path', models.CharField(max_length=512, null=True, verbose_name=b'File', blank=True)),
                ('status', models.BooleanField(default=False, verbose_name=b'Status')),
                ('email_ids', models.CharField(max_length=512, null=True, verbose_name=b'Email IDs', blank=True)),
                ('is_deleted', models.BooleanField(default=False, verbose_name=b'Is Deleted')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('machine', models.ForeignKey(to='machine.Machine')),
                ('site_instance', models.ForeignKey(to='site_instance.SiteInstance')),
                ('technology', models.ForeignKey(to='device.DeviceTechnology')),
                ('user_profile', models.ForeignKey(to='user_profile.UserProfile')),
            ],
        ),
    ]
