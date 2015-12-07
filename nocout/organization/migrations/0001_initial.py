# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250, verbose_name=b'Name')),
                ('alias', models.CharField(max_length=250, verbose_name=b'Alias')),
                ('city', models.CharField(max_length=200, null=True, verbose_name=b'City', blank=True)),
                ('state', models.CharField(max_length=200, null=True, verbose_name=b'State', blank=True)),
                ('country', models.CharField(max_length=200, null=True, verbose_name=b'Country', blank=True)),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='organization_children', blank=True, to='organization.Organization', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
