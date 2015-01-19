from celery import task

from django.db.models import Q, Count, F
from django.utils import timezone

from nocout.settings import PMP, WiMAX

from organization.models import Organization
from device.models import DeviceTechnology, Device
from capacity_management.models import SectorCapacityStatus
from performance.models import Topology
from dashboard.models import (DashboardSetting, DashboardSeverityStatusTimely, DashboardSeverityStatusHourly,
        DashboardSeverityStatusDaily, DashboardSeverityStatusWeekly, DashboardSeverityStatusMonthly,
        DashboardSeverityStatusYearly, DashboardRangeStatusTimely, DashboardRangeStatusHourly, DashboardRangeStatusDaily,
        DashboardRangeStatusWeekly, DashboardRangeStatusMonthly, DashboardRangeStatusYearly,
    )

from inventory.utils.util import organization_sectors
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

    calculate_timely_network_alert(user_organizations, dashboard_name='latency-pmp', technology=PMP)
    calculate_timely_network_alert(user_organizations, dashboard_name='latency-wimax', technology=WiMAX)
    calculate_timely_network_alert(user_organizations, dashboard_name='latency-network')

    calculate_timely_network_alert(user_organizations, dashboard_name='packetloss-pmp', technology=PMP)
    calculate_timely_network_alert(user_organizations, dashboard_name='packetloss-wimax', technology=WiMAX)
    calculate_timely_network_alert(user_organizations, dashboard_name='packetloss-network')

    calculate_timely_network_alert(user_organizations, dashboard_name='down-pmp', technology=PMP)
    calculate_timely_network_alert(user_organizations, dashboard_name='down-wimax', technology=WiMAX)
    calculate_timely_network_alert(user_organizations, dashboard_name='down-network')

    calculate_timely_network_alert(user_organizations, dashboard_name='temperature', technology=PMP)
    calculate_timely_network_alert(user_organizations, dashboard_name='temperature', technology=WiMAX)
    calculate_timely_network_alert(user_organizations, dashboard_name='temperature')


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

    try:
        dashboard_setting = DashboardSetting.objects.get(technology_id=technology.ID, page_name='main_dashboard', name=data_source, is_bh=False)
    except DashboardSetting.DoesNotExist as e:
        return

    user_sector = organization_sectors(organization, technology.ID)
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


def calculate_timely_network_alert(organizations, dashboard_name, technology=None):

    try:
        dashboard_setting = DashboardSetting.objects.get(technology_id=technology.ID,
                page_name='main_dashboard', name=dashboard_name, is_bh=False)
    except DashboardSetting.DoesNotExist as e:
        return None

    sector_devices = organization_network_devices(organizations, technology.ID)
    sector_devices = sector_devices.filter(sector_configured_on__isnull=True).values_list('device_name', flat=True)

    status_dict_list = NetworkStatus.objects.order_by('device_name').filter(device_name__in=sector_devices,
            service_name__in=['ping'],
            data_source__in=['rta'],
            severity__in=['warning', 'critical', 'down']
        ).values()

    data_list = []
    device_name = ''
    device_result = []
    created_on = timezone.now()
    for result_dict in status_dict_list:
        if device_name == result_dict['device_name']:
            device_result.append(result_dict)
        else:
            dashboard_data_dict = get_dashboard_status_range_counter(dashboard_setting, device_result)
            dashboard_data_dict.update({'device_name': result_dict['device_name'],
               'dashboard_name': dashboard_setting.name, 'created_on': created_on})
            data_list.append(DashboardRangeStatusTimely(**dashboard_data_dict))

            device_name = result_dict['device_name']
            device_result = []

    DashboardRangeStatusTimely.objects.bulk_create(data_list)
