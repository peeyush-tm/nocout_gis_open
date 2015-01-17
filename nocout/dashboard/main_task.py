from celery import task

from django.utils import timezone
from django.db.models import Q, Count, F

from device.models import DeviceTechnology, Device
from capacity_management.models import SectorCapacityStatus
from dashboard.models import DashboardSetting, DashboardSeverityStatusTimely, DashboardRangeStatus
from performance.models import Topology

#inventory utils
from inventory.utils.util import organization_sectors
#inventory utils

#dashboard utils
from dashboard.utils import get_topology_status_results
#dashboard utils


@task()
def task_main_dashboard():
    '''
    '''
    created_on = timezone.now()
    sector_capacity(tech_name='PMP', dashboard_model=DashboardSeverityStatusTimely, created_on=created_on)
    sector_capacity(tech_name='WiMAX', dashboard_model=DashboardSeverityStatusTimely, created_on=created_on)

    sales_opportunity(tech_name='PMP', dashboard_model=DashboardRangeStatus, created_on=created_on)
    sales_opportunity(tech_name='WiMAX', dashboard_model=DashboardRangeStatus, created_on=created_on)


def sector_capacity(**kwargs):
    '''
    '''
    dashboard_name = '%s_sector_capacity' % (kwargs['tech_name'].lower())
    range_counter = dict(dashboard_name=dashboard_name,
                            sector_name='',
                            created_on=kwargs['created_on'],
                            ok=0,
                            warning=0,
                            critical=0,
                            unknown=0
                    )

    organization = []
    columns = ['id', 'sector__name', 'severity', 'sys_timestamp', 'age']

    try:
        technology = DeviceTechnology.objects.get(name=kwargs['tech_name'].upper()).id
    except DeviceTechnology.DoesNotExist as e:
        technology = None

    sectors = SectorCapacityStatus.objects.filter(
            Q(organization__in=organization),
            Q(sector__sector_configured_on__device_technology=technology),
            Q(severity__in=['warning', 'critical', 'ok']),
        ).values(*columns)

    data_list = list()
    for item in sectors:
        if (item['age__lte'] <= F('sys_timestamp') - 600) and (item['severity'].strip().lower() in ['warning', 'critical']):
            range_counter[item['severity'].strip().lower()] += 1
        elif item['severity'].strip().lower() == 'ok':
            range_counter['ok'] += 1
        else:
            range_counter['unknown'] += 1

        range_counter['sector_name'] = item['sector__name']

        try:
            model = kwargs['dashboard_model']
            data_list.append( model(**(range_counter)) )
        except Exception as e:
            break

    kwargs['dashboard_model'].objects.bulk_create(data_list)


def sales_opportunity(**kwargs):
    '''
    '''
    organization = []
    try:
        technology = DeviceTechnology.objects.get(name=kwargs['tech_name'].upper()).id
    except DeviceTechnology.DoesNotExist as e:
        technology = None
    # convert the data source in format topology_pmp/topology_wimax
    data_source = '%s-%s' % ('topology', kwargs['tech_name'].lower())

    try:
        dashboard_setting = DashboardSetting.objects.get(technology=technology, page_name='main_dashboard', name=data_source, is_bh=False)
    except DashboardSetting.DoesNotExist as e:
        dashboard_setting = DashboardSetting.objects.none()

    if dashboard_setting:
        # Get Sector of User's Organizations. [and are Sub Station]
        user_sector = organization_sectors(organization, technology)
        # Get device of User's Organizations. [and are Sub Station]
        sector_devices = Device.objects.filter(id__in=user_sector.\
                        values_list('sector_configured_on', flat=True))

        service_status_results = get_topology_status_results(
            sector_devices, model=Topology, service_name='topology', data_source='topology', user_sector=user_sector
        )

        data_list = list()
        dashboard_name = '%s_sales_opportunity' % (kwargs['tech_name'].lower())
        for result in service_status_results:
            range_counter = get_dashboard_status_range_count(dashboard_setting, result)
            range_counter.update({'dashboard_name': dashboard_name,
                                    'device_name': result['name'],
                                    'created_on': kwargs['created_on']})

            model = kwargs['dashboard_model']
            data_list.append( model(**(range_counter)) )

    kwargs['dashboard_model'].objects.bulk_create(data_list)


def get_dashboard_status_range_count(dashboard_setting, result):
    '''
    '''
    range_counter = dict()
    for i in range(1, 11):
        range_counter.update({'range%d' %i: 0})
    range_counter.update({'unknown': 0})

    is_unknown_range = True
    for i in range(1, 11):
        start_range = getattr(dashboard_setting, 'range%d_start' %i)
        end_range = getattr(dashboard_setting, 'range%d_end' %i)

        # dashboard type is numeric and start_range and end_range exists to compare result.
        if dashboard_setting.dashboard_type == 'INT' and start_range and end_range:
            try:
                if float(start_range) <= float(result['current_value']) <= float(end_range):
                    range_counter['range%d' %i] += 1
                    is_unknown_range = False
            except ValueError as value_error:
                range_counter['unknown'] += 1
                is_unknown_range = False
                break

        # dashboard type is string and start_range exists to compare result.
        elif dashboard_setting.dashboard_type == 'STR' and start_range:
            if result['current_value'].lower() in start_range.lower():
                range_counter['range%d' %i] += 1
                is_unknown_range = False
    if is_unknown_range:
        range_counter['unknown'] += 1

    return range_counter
