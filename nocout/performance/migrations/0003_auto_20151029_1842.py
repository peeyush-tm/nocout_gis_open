# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
        ('performance', '0002_auto_20151009_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='dscustomdashboard',
            name='service',
            field=models.ForeignKey(blank=True, to='service.Service', null=True),
        ),
        migrations.AlterField(
            model_name='dscustomdashboard',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
