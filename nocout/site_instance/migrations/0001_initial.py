# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name=b'Name')),
                ('alias', models.CharField(max_length=255, verbose_name=b'Alias')),
                ('live_status_tcp_port', models.IntegerField(null=True, verbose_name=b'Live Status TCP Port', blank=True)),
                ('web_service_port', models.IntegerField(default=80, verbose_name=b'Web Service Port')),
                ('username', models.CharField(max_length=100, null=True, verbose_name=b'Username', blank=True)),
                ('password', models.CharField(max_length=100, null=True, verbose_name=b'Password', blank=True)),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('is_device_change', models.IntegerField(default=0, verbose_name=b'Is Device Change')),
                ('machine', models.ForeignKey(blank=True, to='machine.Machine', null=True)),
            ],
        ),
    ]
