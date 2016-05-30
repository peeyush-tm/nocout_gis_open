# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0016_auto_20160527_1416'),
    ]

    operations = [
        migrations.RenameField(
            model_name='basestationppsmapper',
            old_name='latest_timestamp',
            new_name='updated_at',
        ),
    ]
