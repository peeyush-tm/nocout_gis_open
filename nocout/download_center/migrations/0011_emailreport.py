# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0010_delete_emailreport'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_list', models.TextField()),
                ('report_name', models.ForeignKey(to='download_center.ReportSettings')),
            ],
        ),
    ]
