# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.manager
import mptt.fields
import django.contrib.auth.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role_name', models.CharField(max_length=100, null=True, verbose_name=b'Role Name', blank=True)),
                ('role_description', models.CharField(max_length=250, null=True, verbose_name=b'Role Description', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPasswordRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField(null=True, verbose_name=b'User Id', blank=True)),
                ('password_used', models.CharField(max_length=100, null=True, verbose_name=b'Password', blank=True)),
                ('password_used_on', models.DateTimeField(auto_now_add=True, verbose_name=b'Password Used On')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone_number', models.CharField(max_length=15, null=True, verbose_name=b'Phone No.', blank=True)),
                ('company', models.CharField(max_length=100, null=True, verbose_name=b'Company', blank=True)),
                ('designation', models.CharField(max_length=100, null=True, verbose_name=b'Designation', blank=True)),
                ('address', models.CharField(max_length=150, null=True, verbose_name=b'Address', blank=True)),
                ('comment', models.TextField(null=True, verbose_name=b'Comment', blank=True)),
                ('is_deleted', models.IntegerField(default=0, max_length=1, verbose_name=b'Is Deleted')),
                ('password_changed_at', models.DateTimeField(null=True, verbose_name=b'Password changed at', blank=True)),
                ('user_invalid_attempt', models.IntegerField(default=0, null=True, verbose_name=b'Invalid attempt', blank=True)),
                ('user_invalid_attempt_at', models.DateTimeField(null=True, verbose_name=b'Invalid attemp at')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('organization', models.ForeignKey(to='organization.Organization')),
                ('parent', mptt.fields.TreeForeignKey(related_name='user_children', blank=True, to='user_profile.UserProfile', null=True)),
                ('role', models.ManyToManyField(to='user_profile.Roles')),
            ],
            options={
                'abstract': False,
            },
            bases=('auth.user', models.Model),
            managers=[
                ('_default_manager', django.db.models.manager.Manager()),
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
