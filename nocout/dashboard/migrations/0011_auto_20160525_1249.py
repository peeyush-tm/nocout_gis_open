# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_networkuptimemonthly'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='networkuptimemonthly',
            name='bs_name',
        ),
        migrations.RemoveField(
            model_name='networkuptimemonthly',
            name='ip_address',
        ),
    ]
