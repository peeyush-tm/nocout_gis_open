# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name=b'Machine Name')),
                ('alias', models.CharField(max_length=255, verbose_name=b'Alias')),
                ('machine_ip', models.IPAddressField(null=True, verbose_name=b'Machine IP', blank=True)),
                ('agent_port', models.IntegerField(null=True, verbose_name=b'Agent Port', blank=True)),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
            ],
        ),
    ]
