# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('command', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevicePingConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_name', models.CharField(max_length=200, null=True, verbose_name=b'Device Name', blank=True)),
                ('device_alias', models.CharField(max_length=200, null=True, verbose_name=b'Device Alias', blank=True)),
                ('packets', models.IntegerField(null=True, verbose_name=b'Packets', blank=True)),
                ('timeout', models.IntegerField(null=True, verbose_name=b'Timeout', blank=True)),
                ('normal_check_interval', models.IntegerField(null=True, verbose_name=b'Normal Check Interval', blank=True)),
                ('rta_warning', models.IntegerField(null=True, verbose_name=b'RTA Warning', blank=True)),
                ('rta_critical', models.IntegerField(null=True, verbose_name=b'RTA Critical', blank=True)),
                ('pl_warning', models.IntegerField(null=True, verbose_name=b'PL Warning', blank=True)),
                ('pl_critical', models.IntegerField(null=True, verbose_name=b'PL Critical', blank=True)),
                ('operation', models.CharField(max_length=1, null=True, verbose_name=b'Opeartion', blank=True)),
                ('added_on', models.DateTimeField(null=True, verbose_name=b'Added On', blank=True)),
                ('modified_on', models.DateTimeField(null=True, verbose_name=b'Modified On', blank=True)),
            ],
            options={
                'ordering': ['added_on'],
            },
        ),
        migrations.CreateModel(
            name='DeviceServiceConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_name', models.CharField(max_length=200, null=True, verbose_name=b'Device Name', blank=True)),
                ('service_name', models.CharField(max_length=200, null=True, verbose_name=b'Service Name', blank=True)),
                ('agent_tag', models.CharField(max_length=50, null=True, verbose_name=b'Agent Tag', blank=True)),
                ('port', models.IntegerField(null=True, verbose_name=b'Port', blank=True)),
                ('data_source', models.CharField(max_length=200, null=True, verbose_name=b'Data Source', blank=True)),
                ('version', models.CharField(max_length=10, null=True, verbose_name=b'Version', blank=True)),
                ('read_community', models.CharField(max_length=100, null=True, verbose_name=b'Read Community', blank=True)),
                ('svc_template', models.CharField(max_length=200, null=True, verbose_name=b'Service Template', blank=True)),
                ('normal_check_interval', models.IntegerField(null=True, verbose_name=b'Normal Check Interval', blank=True)),
                ('retry_check_interval', models.IntegerField(null=True, verbose_name=b'Retry Check Interval', blank=True)),
                ('max_check_attempts', models.IntegerField(null=True, verbose_name=b'Max Check Attempts', blank=True)),
                ('warning', models.CharField(max_length=20, null=True, verbose_name=b'Warning', blank=True)),
                ('critical', models.CharField(max_length=20, null=True, verbose_name=b'Critical', blank=True)),
                ('operation', models.CharField(max_length=1, null=True, verbose_name=b'Operation', blank=True)),
                ('added_on', models.DateTimeField(null=True, verbose_name=b'Added On', blank=True)),
                ('modified_on', models.DateTimeField(null=True, verbose_name=b'Modified On', blank=True)),
                ('is_added', models.IntegerField(default=0, verbose_name=b'Is Added')),
            ],
            options={
                'ordering': ['added_on'],
            },
        ),
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'Parameters Name')),
                ('protocol_name', models.CharField(max_length=255, verbose_name=b'Protocol Name')),
                ('port', models.IntegerField(verbose_name=b'Port')),
                ('version', models.CharField(max_length=10, verbose_name=b'Version')),
                ('read_community', models.CharField(max_length=100, verbose_name=b'Read Community')),
                ('write_community', models.CharField(max_length=100, null=True, verbose_name=b'Write Community', blank=True)),
                ('auth_password', models.CharField(max_length=100, null=True, verbose_name=b'Auth Password', blank=True)),
                ('auth_protocol', models.CharField(max_length=100, null=True, verbose_name=b'Auth Protocol', blank=True)),
                ('security_name', models.CharField(max_length=100, null=True, verbose_name=b'Security Name', blank=True)),
                ('security_level', models.CharField(max_length=100, null=True, verbose_name=b'Security Level', blank=True)),
                ('private_phase', models.CharField(max_length=100, null=True, verbose_name=b'Private Phase', blank=True)),
                ('private_pass_phase', models.CharField(max_length=100, null=True, verbose_name=b'Private Pass Phase', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Name')),
                ('alias', models.CharField(max_length=100, verbose_name=b'Alias')),
                ('description', models.TextField(null=True, blank=True)),
                ('command', models.ForeignKey(blank=True, to='command.Command', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceDataSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Name')),
                ('alias', models.CharField(max_length=250, verbose_name=b'Alias')),
                ('chart_type', models.CharField(max_length=50, choices=[(b'line', b'Line'), (b'spline', b'Spline'), (b'column', b'Column'), (b'area', b'Area'), (b'pie', b'Pie'), (b'table', b'Table'), (b'areaspline', b'Areaspline'), (b'bar', b'Bar'), (b'scatter', b'Scatter'), (b'polar', b'Polar'), (b'angular', b'Angular'), (b'range', b'Range'), (b'candlestick', b'Candlestick'), (b'ohlc', b'OHLC'), (b'flag', b'Flag'), (b'errorbar', b'Error bar'), (b'funnel', b'Funnel'), (b'waterfall', b'Waterfall'), (b'heatmap', b'Heat Map')])),
                ('formula', models.CharField(max_length=100, null=True, verbose_name=b'Formula', blank=True)),
                ('valuesuffix', models.CharField(max_length=100, verbose_name=b'Value Suffix')),
                ('valuetext', models.CharField(max_length=100, verbose_name=b'Value Text')),
                ('show_min', models.BooleanField(default=False, verbose_name=b'Show Min')),
                ('show_max', models.BooleanField(default=False, verbose_name=b'Show Max')),
                ('show_gis', models.BooleanField(default=True, verbose_name=b'Show Gis')),
                ('show_performance_center', models.BooleanField(default=True, verbose_name=b'Show In Performance Center')),
                ('is_inverted', models.BooleanField(default=False, verbose_name=b'The Comparison is inverted')),
                ('data_source_type', models.IntegerField(default=1, choices=[(1, b'Numeric'), (2, b'String')])),
                ('warning', models.CharField(max_length=255, null=True, verbose_name=b'Warning', blank=True)),
                ('critical', models.CharField(max_length=255, null=True, verbose_name=b'Critical', blank=True)),
                ('chart_color', models.CharField(max_length=100, verbose_name=b'Chart Color')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceParameters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parameter_description', models.CharField(max_length=250)),
                ('normal_check_interval', models.IntegerField()),
                ('retry_check_interval', models.IntegerField()),
                ('max_check_attempts', models.IntegerField()),
                ('protocol', models.ForeignKey(verbose_name=b' SNMP Parameters', to='service.Protocol')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceSpecificDataSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('warning', models.CharField(max_length=255, null=True, verbose_name=b'Warning', blank=True)),
                ('critical', models.CharField(max_length=255, null=True, verbose_name=b'Critical', blank=True)),
                ('service', models.ForeignKey(to='service.Service')),
                ('service_data_sources', models.ForeignKey(to='service.ServiceDataSource')),
            ],
        ),
        migrations.AddField(
            model_name='service',
            name='parameters',
            field=models.ForeignKey(to='service.ServiceParameters'),
        ),
        migrations.AddField(
            model_name='service',
            name='service_data_sources',
            field=models.ManyToManyField(to='service.ServiceDataSource', through='service.ServiceSpecificDataSource'),
        ),
    ]
