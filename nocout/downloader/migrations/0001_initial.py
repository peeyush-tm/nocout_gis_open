# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Downloader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_path', models.CharField(max_length=250, null=True, verbose_name=b'File', blank=True)),
                ('file_type', models.CharField(max_length=20, null=True, verbose_name=b'File Type', blank=True)),
                ('app_name', models.CharField(max_length=250, null=True, verbose_name=b'App Name', blank=True)),
                ('headers_view', models.CharField(max_length=250, null=True, verbose_name=b'Headers View Name', blank=True)),
                ('rows_view', models.CharField(max_length=250, null=True, verbose_name=b'View Name', blank=True)),
                ('headers_data', models.TextField(null=True, verbose_name=b'Headers Data', blank=True)),
                ('rows_data', models.TextField(null=True, verbose_name=b'Rows Data', blank=True)),
                ('status', models.IntegerField(null=True, verbose_name=b'Status', blank=True)),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('downloaded_by', models.CharField(max_length=100, null=True, verbose_name=b'Downloaded By', blank=True)),
                ('requested_on', models.DateTimeField(null=True, verbose_name=b'Requested On', blank=True)),
                ('request_completion_on', models.DateTimeField(null=True, verbose_name=b'Request Completion On', blank=True)),
            ],
        ),
    ]
