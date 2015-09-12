# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_auto_20150818_1052'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thematicsettings',
            name='thematic_type',
        ),
    ]
