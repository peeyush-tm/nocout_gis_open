from celery import task

from django.db.models import Q, Count, F
from django.utils import timezone

from nocout.settings import PMP, WiMAX

from organization.models import Organization
from device.models import DeviceTechnology, Device
from capacity_management.models import SectorCapacityStatus
from performance.models import Topology, NetworkStatus
from dashboard.models import (DashboardSetting, DashboardSeverityStatusTimely, DashboardSeverityStatusHourly,
        DashboardSeverityStatusDaily, DashboardSeverityStatusWeekly, DashboardSeverityStatusMonthly,
        DashboardSeverityStatusYearly, DashboardRangeStatusTimely, DashboardRangeStatusHourly, DashboardRangeStatusDaily,
        DashboardRangeStatusWeekly, DashboardRangeStatusMonthly, DashboardRangeStatusYearly,
    )

from inventory.utils.util import organization_sectors, organization_network_devices
from dashboard.utils import get_topology_status_results, get_dashboard_status_range_counter


@task()
def calculate_timely_main_dashboard():
    '''
    '''
    created_on = timezone.now()

    calculate_timely_sector_capacity(technology=PMP, model=DashboardSeverityStatusTimely, created_on=created_on)
    calculate_timely_sector_capacity(technology=WiMAX, model=DashboardSeverityStatusTimely, created_on=created_on)

    calculate_timely_sales_opportunity(technology=PMP, model=DashboardRangeStatusTimely, created_on=created_on)
    calculate_timely_sales_opportunity(technology=WiMAX, model=DashboardRangeStatusTimely, created_on=created_on)

    user_organizations = Organization.objects.all()

    calculate_timely_latency(user_organizations, dashboard_name='latency-pmp', technology=PMP)
    calculate_timely_latency(user_organizations, dashboard_name='latency-wimax', technology=WiMAX)
    calculate_timely_latency(user_organizations, dashboard_name='latency-network')

    calculate_timely_packet_drop(user_organizations, dashboard_name='packetloss-pmp', technology=PMP)
    calculate_timely_packet_drop(user_organizations, dashboard_name='packetloss-wimax', technology=WiMAX)
    calculate_timely_packet_drop(user_organizations, dashboard_name='packetloss-network')

    calculate_timely_down_status(user_organizations, dashboard_name='down-pmp', technology=PMP)
    calculate_timely_down_status(user_organizations, dashboard_name='down-wimax', technology=WiMAX)
    calculate_timely_down_status(user_organizations, dashboard_name='down-network')

    calculate_timely_temperature(user_organizations, chart_type='IDU')
    calculate_timely_temperature(user_organizations, chart_type='ACB')
    calculate_timely_temperature(user_organizations, chart_type='FAN')


def calculate_timely_sector_capacity(technology, model, created_on):
    '''
    :param technology: Named Tuple
    :param model: Dashboard Model to store timely dashboard data.
    :param created_on:
    return
    '''
    dashboard_name = '%s_sector_capacity' % (technology.NAME.lower())
    range_counter = dict(
            dashboard_name=dashboard_name,
            sector_name='',
            created_on=created_on,
            ok=0,
            warning=0,
            critical=0,
            unknown=0
        )

    sectors = SectorCapacityStatus.objects.filter(
            Q(organization__in=[]),
            Q(sector__sector_configured_on__device_technology=technology.ID),
            Q(severity__in=['warning', 'critical', 'ok']),
        ).values('id', 'sector__name', 'severity', 'sys_timestamp', 'age')

    data_list = list()
    for item in sectors:
        if (item['age'] <= item['sys_timestamp'] - 600) and (item['severity'].strip().lower() in ['warning', 'critical']):
            range_counter[item['severity'].strip().lower()] += 1
        elif item['severity'].strip().lower() == 'ok':
            range_counter['ok'] += 1
        else:
            range_counter['unknown'] += 1

        range_counter['sector_name'] = item['sector__name']

        try:
            data_list.append(model(**range_counter))
        except Exception as e:
            pass

    model.objects.bulk_create(data_list)


def calculate_timely_sales_opportunity(technology, model, created_on):
    '''
    :param technology: Named Tuple
    :param model: Dashboard Model to store timely dashboard data.
    :param created_on:
    return
    '''
    organization = []
    # convert the data source in format topology_pmp/topology_wimax
    data_source = '%s-%s' % ('topology', technology.NAME.lower())

    technology_id = technology.ID if technology else None
    try:
        dashboard_setting = DashboardSetting.objects.get(technology_id=technology_id, page_name='main_dashboard', name=data_source, is_bh=False)
    except DashboardSetting.DoesNotExist as e:
        return

    user_sector = organization_sectors(organization, technology_id)
    sector_devices = Device.objects.filter(id__in=user_sector.values_list('sector_configured_on', flat=True))

    service_status_results = get_topology_status_results(
        sector_devices, model=Topology, service_name='topology', data_source='topology', user_sector=user_sector
    )

    data_list = list()
    dashboard_name = '%s_sales_opportunity' % (technology.NAME.lower())
    for result in service_status_results:
        range_counter = get_dashboard_status_range_counter(dashboard_setting, [result])
        range_counter.update(
            {'dashboard_name': dashboard_name,
                'device_name': result['name'], # Store sector name as device_name
                'created_on': created_on
            }
        )

        data_list.append(model(**range_counter))

    model.objects.bulk_create(data_list)


def calculate_timely_latency(organizations, dashboard_name, technology=None):

    technology_id = technology.ID if technology else None
    sector_devices = organization_network_devices(organizations, technology_id)
    sector_devices = sector_devices.filter(sector_configured_on__isnull=False).values('machine__name', 'device_name')

    machine_dict = prepare_machines(sector_devices)
    status_dict_list = []
    for machine_name, device_list in machine_dict.items():
        status_dict_list += NetworkStatus.objects.order_by('device_name').filter(device_name__in=device_list,
                service_name='ping',
                data_source='rta',
                severity__in=['warning', 'critical', 'down']
            ).using(machine_name).values()

    calculate_timely_network_alert(dashboard_name, technology, status_dict_list)


def calculate_timely_packet_drop(organizations, dashboard_name, technology=None):
    technology_id = technology.ID if technology else None
    sector_devices = organization_network_devices(organizations, technology_id)
    sector_devices = sector_devices.filter(sector_configured_on__isnull=False).values('machine__name', 'device_name')

    machine_dict = prepare_machines(sector_devices)
    status_dict_list = []
    for machine_name, device_list in machine_dict.items():
        status_dict_list += NetworkStatus.objects.order_by('device_name').filter(device_name__in=device_list,
                service_name='ping',
                data_source='pl',
                severity__in=['warning', 'critical', 'down'],
                current_value__lt=100
            ).using(machine_name).values()

    calculate_timely_network_alert(dashboard_name, technology, status_dict_list)


def calculate_timely_down_status(organizations, dashboard_name, technology=None):
    technology_id = technology.ID if technology else None
    sector_devices = organization_network_devices(organizations, technology_id)
    sector_devices = sector_devices.filter(sector_configured_on__isnull=False).values('machine__name', 'device_name')

    machine_dict = prepare_machines(sector_devices)
    status_dict_list = []
    for machine_name, device_list in machine_dict.items():
        status_dict_list += NetworkStatus.objects.order_by('device_name').filter(device_name__in=device_list,
                service_name='ping',
                data_source='pl',
                severity__in=['down'],
                current_value__gte=100
            ).using(machine_name).values()

    calculate_timely_network_alert(dashboard_name, technology, status_dict_list)


def calculate_timely_temperature(organizations, chart_type='IDU'):

    technology_id = 3
    sector_devices = organization_network_devices(organizations, technology_id)
    sector_devices = sector_devices.filter(sector_configured_on__isnull=False).values('machine__name', 'device_name')

    if chart_type == 'IDU':
        service_list = ['wimax_bs_temperature_acb', 'wimax_bs_temperature_fan']
        data_source_list = ['acb_temp', 'fan_temp']
    elif chart_type == 'ACB':
        service_list = ['wimax_bs_temperature_acb']
        data_source_list = ['acb_temp']
    elif chart_type == 'FAN':
        service_list = ['wimax_bs_temperature_fan']
        data_source_list = ['fan_temp']
    status_dashboard_name = 'temperature-' + chart_type.lower()

    machine_dict = prepare_machines(sector_devices)
    status_dict_list = []
    for machine_name, device_list in machine_dict.items():
        status_dict_list += NetworkStatus.objects.order_by('device_name').filter(device_name__in=device_list,
                service_name__in=service_list,
                data_source__in=data_source_list,
                severity__in=['warning', 'critical']
            ).using(machine_name).values()

    calculate_timely_network_alert('temperature', WiMAX, status_dict_list, status_dashboard_name)


def calculate_timely_network_alert(dashboard_name, technology=None, status_dict_list=[], status_dashboard_name=None ):

    technology_id = technology.ID if technology else None
    try:
        dashboard_setting = DashboardSetting.objects.get(technology_id=technology_id,
                page_name='main_dashboard', name=dashboard_name, is_bh=False)
    except DashboardSetting.DoesNotExist as e:
        return None

    data_list = []
    device_name = ''
    device_result = []
    created_on = timezone.now()
    if status_dashboard_name is None:
        status_dashboard_name = dashboard_name
    for result_dict in status_dict_list:
        if device_name == result_dict['device_name']:
            device_result.append(result_dict)
        else:
            dashboard_data_dict = get_dashboard_status_range_counter(dashboard_setting, device_result)
            dashboard_data_dict.update({'device_name': result_dict['device_name'],
               'dashboard_name': status_dashboard_name, 'created_on': created_on})
            data_list.append(DashboardRangeStatusTimely(**dashboard_data_dict))

            device_name = result_dict['device_name']
            device_result = [result_dict]
    if device_result:
        dashboard_data_dict = get_dashboard_status_range_counter(dashboard_setting, device_result)
        dashboard_data_dict.update({'device_name': result_dict['device_name'],
            'dashboard_name': status_dashboard_name, 'created_on': created_on})
        data_list.append(DashboardRangeStatusTimely(**dashboard_data_dict))

    DashboardRangeStatusTimely.objects.bulk_create(data_list)


def prepare_machines(device_list):
    """

    :return:
    """
    # Unique machine from the device_list
    unique_device_machine_list = {device['machine__name']: True for device in device_list}.keys()

    machine_dict = {}
    #Creating the machine as a key and device_name as a list for that machine.
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device['device_name'] for device in device_list if
                                 device['machine__name'] == machine]

    return machine_dict


@task
def calculate_hourly_main_dashboard():
    '''
    '''
    now = timezone.now()

    calculate_hourly_severity_status(now)
    calculate_hourly_range_status(now)


def calculate_hourly_severity_status(now):
    last_hour_timely_severity_status = DashboardSeverityStatusTimely.objects.order_by('dashboard_name',
            'sector_name').filter(created_on__lt=now)

    hourly_severity_status_list = []
    hourly_severity_status = None
    dashboard_name = ''
    sector_name = ''
    for timely_severity_status in last_hour_timely_severity_status:
        if dashboard_name == timely_severity_status.dashboard_name and sector_name == timely_severity_status.sector_name:
            hourly_severity_status = sum_severity_status(hourly_severity_status, timely_severity_status)
        else:
            hourly_severity_status = DashboardSeverityStatusHourly(
                dashboard_name=timely_severity_status.dashboard_name,
                sector_name=timely_severity_status.sector_name,
                created_on=now,
                warning=timely_severity_status.warning,
                critical=timely_severity_status.critical,
                ok=timely_severity_status.ok,
                down=timely_severity_status.down,
                unknown=timely_severity_status.unknown
            )
            hourly_severity_status_list.append(hourly_severity_status)

    DashboardSeverityStatusHourly.objects.bulk_create(hourly_severity_status_list)

    last_hour_timely_severity_status.delete()


def calculate_hourly_range_status(now):
    last_hour_timely_range_status = DashboardRangeStatusTimely.objects.order_by('dashboard_name',
            'device_name').filter(created_on__lt=now)

    hourly_range_status_list = []
    hourly_range_status = None
    dashboard_name = ''
    device_name = ''
    for timely_range_status in last_hour_timely_range_status:
        if dashboard_name == timely_range_status.dashboard_name and device_name == timely_range_status.device_name:
            hourly_range_status = sum_range_status(hourly_range_status, timely_range_status)
        else:
            hourly_range_status = DashboardRangeStatusHourly(
                dashboard_name=timely_range_status.dashboard_name,
                device_name=timely_range_status.device_name,
                created_on=now,
                range1=timely_range_status.range1,
                range2=timely_range_status.range2,
                range3=timely_range_status.range3,
                range4=timely_range_status.range4,
                range5=timely_range_status.range5,
                range6=timely_range_status.range6,
                range7=timely_range_status.range7,
                range8=timely_range_status.range8,
                range9=timely_range_status.range9,
                range10=timely_range_status.range10,
                unknown=timely_range_status.unknown
            )
            hourly_range_status_list.append(hourly_range_status)

    DashboardRangeStatusHourly.objects.bulk_create(hourly_range_status_list)

    last_hour_timely_range_status.delete()


def calculate_weekly_range_status(now):
    last_week_daily_range_status = DashboardRangeStatusDaily.objects.order_by('dashboard_name',
            'device_name').filter(created_on__lt=now)

    daily_range_status_list = []
    weekly_range_status = None
    dashboard_name = ''
    device_name = ''
    for daily_range_status in last_week_daily_range_status:
        if dashboard_name == daily_range_status.dashboard_name and device_name == daily_range_status.device_name:
            weekly_range_status = sum_range_status(weekly_range_status, daily_range_status)
        else:
            weekly_range_status = DashboardRangeStatusWeekly(
                dashboard_name=daily_range_status.dashboard_name,
                device_name=daily_range_status.device_name,
                created_on=now,
                range1=daily_range_status.range1,
                range2=daily_range_status.range2,
                range3=daily_range_status.range3,
                range4=daily_range_status.range4,
                range5=daily_range_status.range5,
                range6=daily_range_status.range6,
                range7=daily_range_status.range7,
                range8=daily_range_status.range8,
                range9=daily_range_status.range9,
                range10=daily_range_status.range10,
                unknown=daily_range_status.unknown
            )
            daily_range_status_list.append(daily_range_status)

    DashboardRangeStatusWeekly.objects.bulk_create(daily_range_status_list)


def sum_severity_status(parent, child):
    parent.warning += child.warning
    parent.critical += child.critical
    parent.ok += child.ok
    parent.down += child.down
    parent.unknown += child.unknown

    return parent


def sum_range_status(parent, child):
    parent.range1 += child.range1
    parent.range2 += child.range2
    parent.range3 += child.range3
    parent.range4 += child.range4
    parent.range5 += child.range5
    parent.range6 += child.range6
    parent.range7 += child.range7
    parent.range8 += child.range8
    parent.range9 += child.range9
    parent.range10 += child.range10
    parent.unknown += child.unknown

    return parent


@task
def calculate_daily_main_dashboard():
    '''
    '''
    now = timezone.now()

    calculate_daily_severity_status(now)
    calculate_daily_range_status(now)


def calculate_daily_severity_status(now):
    last_day_timely_severity_status = DashboardSeverityStatusHourly.objects.order_by('dashboard_name',
            'sector_name').filter(created_on__lt=now)

    daily_severity_status_list = []
    daily_severity_status = None
    dashboard_name = ''
    sector_name = ''
    for hourly_severity_status in last_day_timely_severity_status:
        if dashboard_name == hourly_severity_status.dashboard_name and sector_name == hourly_severity_status.sector_name:
            daily_severity_status = sum_severity_status(daily_severity_status, hourly_severity_status)
        else:
            daily_severity_status = DashboardSeverityStatusDaily(
                dashboard_name=hourly_severity_status.dashboard_name,
                sector_name=hourly_severity_status.sector_name,
                created_on=now,
                warning=hourly_severity_status.warning,
                critical=hourly_severity_status.critical,
                ok=hourly_severity_status.ok,
                down=hourly_severity_status.down,
                unknown=hourly_severity_status.unknown
            )
            daily_severity_status_list.append(daily_severity_status)

    DashboardSeverityStatusDaily.objects.bulk_create(daily_severity_status_list)

    last_day_timely_severity_status.delete()


def calculate_daily_range_status(now):
    last_day_hourly_range_status = DashboardRangeStatusHourly.objects.order_by('dashboard_name',
            'device_name').filter(created_on__lt=now)

    daily_range_status_list = []
    daily_range_status = None
    dashboard_name = ''
    device_name = ''
    for hourly_range_status in last_day_hourly_range_status:
        if dashboard_name == hourly_range_status.dashboard_name and device_name == hourly_range_status.device_name:
            daily_range_status = sum_range_status(daily_range_status, hourly_range_status)
        else:
            daily_range_status = DashboardRangeStatusDaily(
                dashboard_name=hourly_range_status.dashboard_name,
                device_name=hourly_range_status.device_name,
                created_on=now,
                range1=hourly_range_status.range1,
                range2=hourly_range_status.range2,
                range3=hourly_range_status.range3,
                range4=hourly_range_status.range4,
                range5=hourly_range_status.range5,
                range6=hourly_range_status.range6,
                range7=hourly_range_status.range7,
                range8=hourly_range_status.range8,
                range9=hourly_range_status.range9,
                range10=hourly_range_status.range10,
                unknown=hourly_range_status.unknown
            )
            daily_range_status_list.append(daily_range_status)

    DashboardRangeStatusDaily.objects.bulk_create(daily_range_status_list)

    last_day_hourly_range_status.delete()
