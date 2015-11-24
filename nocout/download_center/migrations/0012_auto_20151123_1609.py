# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('download_center', '0011_emailreport'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailreport',
            name='report_name',
        ),
        migrations.DeleteModel(
            name='EmailReport',
        ),
    ]
