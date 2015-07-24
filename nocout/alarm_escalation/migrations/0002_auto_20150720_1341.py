# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alarm_escalation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='escalationstatus',
            name='ip',
            field=models.GenericIPAddressField(),
        ),
    ]
