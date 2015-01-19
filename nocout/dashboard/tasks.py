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

    calculate_sector_capacity(technology=PMP, model=DashboardSeverityStatusTimely, created_on=created_on)
    calculate_sector_capacity(technology=WiMAX, model=DashboardSeverityStatusTimely, created_on=created_on)

    calculate_sales_opportunity(technology=PMP, model=DashboardRangeStatusTimely, created_on=created_on)
    calculate_sales_opportunity(technology=WiMAX, model=DashboardRangeStatusTimely, created_on=created_on)

    user_organizations = Organization.objects.all()

    pmp_latency_data = calculate_timely_network_alert(user_organizations, False, False, '', 4)
    wimax_latency_data = calculate_timely_network_alert(user_organizations, False, False, '', 3)
    all_latency_data = calculate_timely_network_alert(user_organizations, False, False, '', None)

    pmp_packet_loss_data = calculate_timely_network_alert(user_organizations, True, False, '', 4)
    wimax_packet_loss_data = calculate_timely_network_alert(user_organizations, True, False, '', 3)
    all_packet_loss_data = calculate_timely_network_alert(user_organizations, True, False, '', None)

    pmp_down_data = calculate_timely_network_alert(user_organizations, False, True, '', 4)
    wimax_down_data = calculate_timely_network_alert(user_organizations, False, True, '', 3)
    all_down_data = calculate_timely_network_alert(user_organizations, False, True, '', None)

    idu_temperature_data = calculate_timely_network_alert(user_organizations, False, False, 'IDU', 3)
    acb_temperature_data = calculate_timely_network_alert(user_organizations, False, False, 'ACB', 3)
    fan_temperature_data = calculate_timely_network_alert(user_organizations, False, False, 'FAN', 3)


def calculate_sector_capacity(technology, model, created_on):
    '''
    :param technology: Named Tuple
    :param model: Dashboard Model to store timely dashboard data.
    :param created_on:
    return
    '''
    dashboard_name = '%s_sector_capacity' % (technology.NAME.lower())
    range_counter = dict(
            dashboard_name = dashboard_name,
            sector_name = '',
            created_on = created_on,
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
            data_list.append( model(**(range_counter)) )
        except Exception as e:
            pass

    model.objects.bulk_create(data_list)


def calculate_sales_opportunity(technology, model, created_on):
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

        data_list.append( model(**(range_counter)) )

    model.objects.bulk_create(data_list)


def calculate_timely_network_alert(organizations, packet_loss, down, temperature, technology):

    data_list = []
    if technology:
        technology_name = DeviceTechnology.objects.get(id=technology).name.lower()
    else:
        technology_name = 'network'

    if packet_loss:
        dashboard_name = 'packetloss-%s'%technology_name
    elif down:
        dashboard_name = 'down-%s'%technology_name
    elif temperature:
        dashboard_name = 'temperature'
    else:
        dashboard_name = 'latency-%s'%technology_name

    try:
        dashboard_setting = DashboardSetting.objects.get(technology=technology, page_name='main_dashboard', name=dashboard_name, is_bh=False)
    except DashboardSetting.DoesNotExist as e:
        return None

    user_devices = organization_network_devices(organizations, technology)
    # Get Sectors of technology.Technology is PMP or WIMAX or None(For All: PMP+WIMAX )
    if technology:
        device_id_list = Sector.objects.filter(bs_technology=technology, sector_configured_on__in=user_devices).values_list('sector_configured_on', flat=True)

    else:
        device_id_list = Sector.objects.filter(sector_configured_on__in=user_devices)

    # Make device_list distinct and remove duplicate devices from list.
    device_id_list = list(set(device_id_list))
    device_name_list = Device.objects.filter(id__in=device_id_list).values_list('device_name', flat=True)

    if dashboard_setting:
        status_dict_list = NetworkStatus.objects.order_by('device_name').filter(device_name__in=device_name_list,
                service_name__in=['ping'],
                data_source__in=['rta'],
                severity__in=['warning','critical','down']
            ).values()
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
            # dashboard_data_dict = get_dashboard_range_status(dashboard_setting, result)
            # dashboard_data_dict.update({'device_name': result['device_name'], 'dashboard_name': dashboard_setting.name})

        DashboardRangeStatusTimely.objects.bulk_create(data_list)
