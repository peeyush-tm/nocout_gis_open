# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0004_delete_roles'),
    ]

    operations = [
        migrations.CreateModel(
            name='PowerLogs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('reason', models.TextField()),
                ('module', models.CharField(max_length=256)),
                ('ss_ip', models.GenericIPAddressField(null=True, blank=True)),
                ('circuit_id', models.CharField(max_length=256, null=True, blank=True)),
                ('customer_alias', models.CharField(max_length=250)),
                ('logged_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
