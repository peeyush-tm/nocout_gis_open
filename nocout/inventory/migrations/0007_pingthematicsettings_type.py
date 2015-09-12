# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0011_auto_20150720_1348'),
        ('inventory', '0006_remove_thematicsettings_thematic_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='pingthematicsettings',
            name='type',
            field=models.ForeignKey(to='device.DeviceType', null=True),
        ),
    ]
