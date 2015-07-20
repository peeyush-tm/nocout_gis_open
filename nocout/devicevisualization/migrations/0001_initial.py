# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import devicevisualization.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GISPointTool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name=b'Name')),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('latitude', models.FloatField(null=True, verbose_name=b'Latitude', blank=True)),
                ('longitude', models.FloatField(null=True, verbose_name=b'Longitude', blank=True)),
                ('icon_url', models.CharField(max_length=255, verbose_name=b'Icon Url')),
                ('connected_point_type', models.CharField(max_length=255, null=True, verbose_name=b'Connected Point Type', blank=True)),
                ('connected_point_info', models.TextField(null=True, verbose_name=b'Connected Point Info', blank=True)),
                ('connected_lat', models.FloatField(null=True, verbose_name=b'Connected Latitude', blank=True)),
                ('connected_lon', models.FloatField(null=True, verbose_name=b'Connected Longitude', blank=True)),
                ('user_id', models.IntegerField(verbose_name=b'User Id')),
            ],
        ),
        migrations.CreateModel(
            name='KMZReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name=b'Name')),
                ('filename', models.FileField(max_length=300, upload_to=devicevisualization.models.KMZ_report_name)),
                ('added_on', models.DateTimeField(auto_now_add=True, verbose_name=b'Added On')),
                ('is_public', models.BooleanField(default=True, verbose_name=b'Is Public')),
                ('user', models.ForeignKey(to='user_profile.UserProfile')),
            ],
        ),
    ]
