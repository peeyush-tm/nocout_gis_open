# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0005_powerlogs'),
    ]

    operations = [
        migrations.RenameField(
            model_name='powerlogs',
            old_name='module',
            new_name='action',
        ),
    ]
