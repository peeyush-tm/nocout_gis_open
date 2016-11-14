# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0006_auto_20160218_1440'),
        ('alert_center', '0012_auto_20161109_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualTicketingHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip_address', models.CharField(max_length=32, verbose_name=b'IP Address')),
                ('eventname', models.CharField(max_length=128, verbose_name=b'Event Name')),
                ('ticket_number', models.CharField(max_length=64, null=True, verbose_name=b'Ticket Number', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name=b'Updated At')),
                ('user_profile', models.ForeignKey(to='user_profile.UserProfile')),
            ],
        ),
    ]
