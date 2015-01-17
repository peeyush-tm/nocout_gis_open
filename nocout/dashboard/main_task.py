import datetime

from celery import task

from django.db.models import Q, Count, F

from device.models import DeviceTechnology
from capacity_management.models import SectorCapacityStatus
from dashboard.models import DashboardSeverityStatusTimely

#inventory utils
from inventory.utils.util import organization_sectors
#inventory utils


@task()
def task_main_dashboard():
    '''
    '''
    created_on = datetime.datetime.today()
    sector_capacity(tech_name='PMP', dashboard_model=DashboardSeverityStatusTimely, created_on=created_on)
    sector_capacity(tech_name='WiMAX', dashboard_model=DashboardSeverityStatusTimely, created_on=created_on)


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

    for item in sectors:
        if (item['age__lte'] <= F('sys_timestamp') - 600) and (item['severity'].strip().lower() in ['warning', 'critical']):
            range_counter[item['severity'].strip().lower()] += 1
        elif item['severity'].strip().lower() == 'ok':
            range_counter['ok'] += 1
        else:
            range_counter['unknown'] += 1

        range_counter['sector_name'] = item['sector__name']

        try:
            dash_model = kwargs['dashboard_name']
            dash_model.objects.create(**range_counter)
        except Exception as e:
            break

