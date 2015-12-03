# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0009_emailreport'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmailReport',
        ),
    ]
