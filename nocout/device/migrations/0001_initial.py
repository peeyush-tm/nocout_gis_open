# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
        ('machine', '0001_initial'),
        ('site_instance', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city_name', models.CharField(max_length=250, verbose_name=b'Name')),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country_name', models.CharField(max_length=200, verbose_name=b'Name')),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_name', models.CharField(unique=True, max_length=200, verbose_name=b'Name')),
                ('device_alias', models.CharField(help_text=b'\n        <ul><li>PTP <ul><li>Near End : Circuit ID_NE</li>\n        <li>Far End : Circuit ID</li></ul>\n        </li><li>PMP<ul><li>ODU : AP IP_Color Code { Eg: AP IP\n        = 10.11.12.13 Color Code=11  =>  Sector ID - 10111213_11}</li>\n        <li>SM : Circuit ID</li></ul></li><li>WiMAX<ul><li>IDU : Sector\n        ID of PMP1 or PMP2</li><li>IDU DR : Sector ID of PMP1 or\n        PMP2</li><li>SS : Circuit ID</li></ul></li>\n        <li>Converter : IP</li><li>Switch : IP</li></ul>\n    ', max_length=200, verbose_name=b'Alias')),
                ('device_technology', models.IntegerField(verbose_name=b'Device Technology')),
                ('device_vendor', models.IntegerField(verbose_name=b'Device Vendor')),
                ('device_model', models.IntegerField(verbose_name=b'Device Model')),
                ('device_type', models.IntegerField(verbose_name=b'Device Type')),
                ('ip_address', models.IPAddressField(unique=True, verbose_name=b'IP Address')),
                ('mac_address', models.CharField(max_length=100, null=True, verbose_name=b'MAC Address', blank=True)),
                ('netmask', models.IPAddressField(null=True, verbose_name=b'Netmask', blank=True)),
                ('gateway', models.IPAddressField(null=True, verbose_name=b'Gateway', blank=True)),
                ('dhcp_state', models.CharField(default=b'Disable', max_length=200, verbose_name=b'DHCP State', choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')])),
                ('host_priority', models.CharField(default=b'Normal', max_length=200, verbose_name=b'Host Priority', choices=[(b'High', b'High'), (b'Normal', b'Normal'), (b'Low', b'Low')])),
                ('host_state', models.CharField(default=b'Enable', max_length=200, verbose_name=b'Host Monitoring State', choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')])),
                ('latitude', models.FloatField(null=True, verbose_name=b'Latitude', blank=True)),
                ('longitude', models.FloatField(null=True, verbose_name=b'Longitude', blank=True)),
                ('timezone', models.CharField(default=b'Asia/Kolkata', max_length=100, verbose_name=b'Timezone')),
                ('address', models.TextField(null=True, verbose_name=b'Address', blank=True)),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('is_deleted', models.IntegerField(default=0, max_length=1, verbose_name=b'Is Deleted')),
                ('is_added_to_nms', models.IntegerField(default=0, max_length=1, verbose_name=b'Is Added')),
                ('is_monitored_on_nms', models.IntegerField(default=0, max_length=1, verbose_name=b'Is Monitored')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('city', models.ForeignKey(blank=True, to='device.City', null=True)),
                ('country', models.ForeignKey(blank=True, to='device.Country', null=True)),
                ('machine', models.ForeignKey(blank=True, to='machine.Machine', null=True)),
                ('organization', models.ForeignKey(to='organization.Organization')),
                ('parent', models.ForeignKey(related_name='device_children', blank=True, to='device.Device', null=True)),
            ],
            options={
                'ordering': ['machine'],
            },
        ),
        migrations.CreateModel(
            name='DeviceFrequency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(help_text=b'MHz', max_length=50)),
                ('color_hex_value', models.CharField(max_length=100)),
                ('frequency_radius', models.FloatField(default=0, help_text=b'Km', verbose_name=b'Frequency Radius')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name=b'Device Model')),
                ('alias', models.CharField(max_length=200, verbose_name=b'Alias')),
            ],
        ),
        migrations.CreateModel(
            name='DevicePort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name=b'Name')),
                ('alias', models.CharField(max_length=200, verbose_name=b'Alias')),
                ('value', models.IntegerField(default=0, verbose_name=b'Port Value')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceSyncHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(null=True, verbose_name=b'Status', blank=True)),
                ('message', models.TextField(null=True, verbose_name=b'NMS Message', blank=True)),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('sync_by', models.CharField(max_length=100, null=True, verbose_name=b'Sync By', blank=True)),
                ('added_on', models.DateTimeField(null=True, verbose_name=b'Applied On', blank=True)),
                ('completed_on', models.DateTimeField(null=True, verbose_name=b'Completed On', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='DeviceTechnology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name=b'Device Technology')),
                ('alias', models.CharField(max_length=200, verbose_name=b'Alias')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name=b'Device Type')),
                ('alias', models.CharField(max_length=200, verbose_name=b'Alias')),
                ('packets', models.IntegerField(null=True, verbose_name=b'Packets', blank=True)),
                ('timeout', models.IntegerField(null=True, verbose_name=b'Timeout', blank=True)),
                ('normal_check_interval', models.IntegerField(null=True, verbose_name=b'Normal Check Interval', blank=True)),
                ('rta_warning', models.IntegerField(null=True, verbose_name=b'RTA Warning', blank=True)),
                ('rta_critical', models.IntegerField(null=True, verbose_name=b'RTA Critical', blank=True)),
                ('pl_warning', models.IntegerField(null=True, verbose_name=b'PL Warning', blank=True)),
                ('pl_critical', models.IntegerField(null=True, verbose_name=b'PL Critical', blank=True)),
                ('agent_tag', models.CharField(max_length=200, null=True, verbose_name=b'Agent Tag', blank=True)),
                ('device_icon', models.ImageField(upload_to=b'uploaded/icons/%Y/%m/%d')),
                ('device_gmap_icon', models.ImageField(upload_to=b'uploaded/icons/%Y/%m/%d')),
                ('device_port', models.ManyToManyField(to='device.DevicePort', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='DeviceTypeFields',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_name', models.CharField(max_length=100)),
                ('field_display_name', models.CharField(max_length=200)),
                ('device_type', models.ForeignKey(to='device.DeviceType')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceTypeFieldsValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_value', models.CharField(max_length=250)),
                ('device_id', models.IntegerField()),
                ('device_type_field', models.ForeignKey(to='device.DeviceTypeFields')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceTypeService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_type', models.ForeignKey(to='device.DeviceType')),
                ('parameter', models.ForeignKey(to='service.ServiceParameters')),
                ('service', models.ForeignKey(to='service.Service')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceTypeServiceDataSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('warning', models.CharField(max_length=255, null=True, verbose_name=b'Warning', blank=True)),
                ('critical', models.CharField(max_length=255, null=True, verbose_name=b'Critical', blank=True)),
                ('device_type_service', models.ForeignKey(to='device.DeviceTypeService')),
                ('service_data_sources', models.ForeignKey(to='service.ServiceDataSource')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceVendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name=b'Device Vendor')),
                ('alias', models.CharField(max_length=200, verbose_name=b'Alias')),
            ],
        ),
        migrations.CreateModel(
            name='ModelType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model', models.ForeignKey(to='device.DeviceModel')),
                ('type', models.ForeignKey(to='device.DeviceType')),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state_name', models.CharField(max_length=200, verbose_name=b'Name')),
                ('country', models.ForeignKey(blank=True, to='device.Country', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StateGeoInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitude', models.FloatField(verbose_name=b'Latitude')),
                ('longitude', models.FloatField(verbose_name=b'Longitude')),
                ('state', models.ForeignKey(to='device.State')),
            ],
        ),
        migrations.CreateModel(
            name='TechnologyVendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('technology', models.ForeignKey(to='device.DeviceTechnology')),
                ('vendor', models.ForeignKey(to='device.DeviceVendor')),
            ],
        ),
        migrations.CreateModel(
            name='VendorModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model', models.ForeignKey(to='device.DeviceModel')),
                ('vendor', models.ForeignKey(to='device.DeviceVendor')),
            ],
        ),
        migrations.AddField(
            model_name='devicevendor',
            name='device_models',
            field=models.ManyToManyField(to='device.DeviceModel', null=True, through='device.VendorModel', blank=True),
        ),
        migrations.AddField(
            model_name='devicetypeservice',
            name='service_data_sources',
            field=models.ManyToManyField(to='service.ServiceDataSource', through='device.DeviceTypeServiceDataSource'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='service',
            field=models.ManyToManyField(to='service.Service', null=True, through='device.DeviceTypeService', blank=True),
        ),
        migrations.AddField(
            model_name='devicetechnology',
            name='device_vendors',
            field=models.ManyToManyField(to='device.DeviceVendor', null=True, through='device.TechnologyVendor', blank=True),
        ),
        migrations.AddField(
            model_name='devicemodel',
            name='device_types',
            field=models.ManyToManyField(to='device.DeviceType', null=True, through='device.ModelType', blank=True),
        ),
        migrations.AddField(
            model_name='device',
            name='ports',
            field=models.ManyToManyField(to='device.DevicePort', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='device',
            name='site_instance',
            field=models.ForeignKey(blank=True, to='site_instance.SiteInstance', null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='state',
            field=models.ForeignKey(blank=True, to='device.State', null=True),
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(blank=True, to='device.State', null=True),
        ),
    ]
