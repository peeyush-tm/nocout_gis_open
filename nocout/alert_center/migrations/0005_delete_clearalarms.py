# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alert_center', '0004_auto_20151121_1121'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ClearAlarms',
        ),
    ]
