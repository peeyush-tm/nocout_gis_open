# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alert_center', '0010_plannedevent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plannedevent',
            old_name='technnology',
            new_name='technology',
        ),
    ]
