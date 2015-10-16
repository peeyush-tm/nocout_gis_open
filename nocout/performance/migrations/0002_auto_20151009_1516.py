# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_auto_20150720_1356'),
        ('service', '0001_initial'),
        ('performance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomDashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250, verbose_name=b'Name')),
                ('title', models.CharField(max_length=250, verbose_name=b'Title')),
                ('display_type', models.CharField(default=b'table', max_length=200, verbose_name=b'Display Type ', choices=[(b'table', b'Table'), (b'chart', b'Chart')])),
                ('is_public', models.BooleanField(default=False, verbose_name=b'Is Public Dashboard')),
                ('is_required', models.BooleanField(default=False, verbose_name=b'Is Required')),
            ],
        ),
        migrations.CreateModel(
            name='DSCustomDashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('custom_dashboard', models.ForeignKey(to='performance.CustomDashboard')),
                ('data_source', models.ForeignKey(to='service.ServiceDataSource')),
            ],
        ),
        migrations.CreateModel(
            name='UsersCustomDashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('custom_dashboard', models.ForeignKey(to='performance.CustomDashboard')),
                ('user_profile', models.ForeignKey(to='user_profile.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='customdashboard',
            name='data_source',
            field=models.ManyToManyField(to='service.ServiceDataSource', through='performance.DSCustomDashboard'),
        ),
        migrations.AddField(
            model_name='customdashboard',
            name='user_profile',
            field=models.ManyToManyField(to='user_profile.UserProfile', through='performance.UsersCustomDashboard'),
        ),
    ]
