# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0012_auto_20151123_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailReport',
            fields=[
                ('reportsettings_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='download_center.ReportSettings')),
                ('email_list', models.TextField()),
            ],
            bases=('download_center.reportsettings',),
        ),
    ]
