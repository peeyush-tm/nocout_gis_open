from celery import task

from django.db.models import Count, Max, Avg #F, Max, Min, Q, Sum, Avg

#task for updating the sector capacity per 5 minutes
#need to run for PMP, WiMAX technology

from capacity_management.models import SectorCapacityStatus
from inventory.models import get_default_org, Sector
from device.models import DeviceTechnology, Device

from inventory.utils.util import prepare_machines

from inventory.tasks import get_devices

from nocout.utils.util import fetch_raw_result

from performance.models import UtilizationStatus, InventoryStatus, ServiceStatus, Utilization, PerformanceService

from django.utils.dateformat import format
import datetime

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@task()
def gather_sector_status(technology):
    """

    :return:
    """
    #we need devices
    #we need the values
    #we need the machines

    technology_object = DeviceTechnology.objects.get(name__icontains=technology)

    network_devices = get_devices(technology)
    device_list = []
    for device in network_devices:
        device_list.append(
            {
                'id': device['id'],
                'device_name': device['device_name'],
                'device_machine': device['machine__name']
            }
        )

    machine_dict = {}
    #prepare_machines(device_list)
    machine_dict = prepare_machines(device_list)
    #need to gather from various sources
    #will do a raw query
    tech_model_service = {
        'wimax': {
            'cbw': {
                'model': 'performance_inventorystatus',
                'service_name': ['wimax_pmp_bw_invent'],
                'data_source': ['pmp2_bw', 'pmp1_bw']
            },
            'val': {
                'model': 'performance_servicestatus',
                'service_name': ['wimax_pmp1_ul_util_bgp', 'wimax_pmp2_ul_util_bgp',
                                 'wimax_pmp1_dl_util_bgp', 'wimax_pmp2_dl_util_bgp'
                ],
                'data_source': ['pmp1_ul_util', 'pmp2_ul_util',
                                'pmp1_dl_util', 'pmp2_dl_util'
                ]

            },
            'per': {
                'model': 'performance_utilizationstatus',
                'service_name': ['wimax_pmp1_ul_util_kpi', 'wimax_pmp2_ul_util_kpi',
                                 'wimax_pmp1_dl_util_kpi', 'wimax_pmp2_dl_util_kpi'
                ],
                'data_source': ['pmp1_ul_util_kpi', 'pmp2_ul_util_kpi',
                                'pmp1_dl_util_kpi', 'pmp2_dl_util_kpi'
                ]
            }
        },
        'pmp': {
            'cbw': {
                'model': None,
                'service_name': None,
                'data_source': None
            },
            'val': {
                'model': 'performance_servicestatus',
                'service_name': None,
                'data_source': None

            },
            'per': {
                'model': 'performance_utilizationstatus',
                'service_name': None,
                'data_source': None
            }
        },
    }

    if technology.lower() == 'wimax':
        sectors = Sector.objects.filter(sector_configured_on__device_technology=technology_object.id,
                                        sector_id__isnull=False,
                                        sector_configured_on_port__isnull=False
                                        ).prefetch_related('sector_configured_on',
                                                           'sector_configured_on_port',
                                                           'base_station',
                                                           'base_station__city',
                                                           'base_station__state'
                                        ).annotate(Count('sector_id'))

        cbw = get_sector_bw(machine_dict=machine_dict,
                            service_name=tech_model_service['wimax']['cbw']['service_name'],
                            data_source=tech_model_service['wimax']['cbw']['data_source'],
        )

        sector_val = get_sector_val(machine_dict=machine_dict,
                                    service_name=tech_model_service['wimax']['val']['service_name'],
                                    data_source=tech_model_service['wimax']['val']['data_source'],
        )

        sector_kpi = get_sector_kpi(machine_dict=machine_dict,
                                    service_name=tech_model_service['wimax']['per']['service_name'],
                                    data_source=tech_model_service['wimax']['per']['data_source']
        )

        return update_sector_status(sectors=sectors, cbw=cbw, kpi=sector_kpi, val=sector_val, technology=technology)

    elif technology.lower() == 'pmp':
        sectors = Sector.objects.filter(sector_configured_on__device_technology=technology_object.id,
                                        sector_id__isnull=False,
                                        sector_configured_on_port__isnull=True
                                        ).prefetch_related('sector_configured_on',
                                                           'base_station',
                                                           'base_station__city',
                                                           'base_station__state'
                                        ).annotate(Count('sector_id'))

    else:
        return False

    return True


def get_sector_bw(machine_dict, service_name, data_source):
    """

    :return:
    """
    performance = None

    for machine in machine_dict:
        if performance:
            performance |= InventoryStatus.objects.filter(
                device_name__in=machine_dict[machine],
                service_name__in=service_name,
                data_source__in=data_source
            ).using(alias=machine)

        else:
            performance = InventoryStatus.objects.filter(
                device_name__in=machine_dict[machine],
                service_name__in=service_name,
                data_source__in=data_source
            ).using(alias=machine)

    return performance


def get_sector_val(machine_dict, service_name, data_source):
    """


    :param machine_dict:
    :param service_name:
    :param data_source:
    :return:
    """
    performance = None
    for machine in machine_dict:
        if performance:
            performance |= ServiceStatus.objects.filter(
                device_name__in=machine_dict[machine],
                service_name__in=service_name,
                data_source__in=data_source
            ).using(alias=machine)

        else:
            performance = ServiceStatus.objects.filter(
                device_name__in=machine_dict[machine],
                service_name__in=service_name,
                data_source__in=data_source
            ).using(alias=machine)
    return performance


def get_sector_kpi(machine_dict, service_name, data_source):
    """

    :param machine_dict:
    :param service_name:
    :param data_source:
    :return:
    """
    performance = None

    for machine in machine_dict:
        if performance:
            performance |= UtilizationStatus.objects.filter(
                device_name__in=machine_dict[machine],
                service_name__in=service_name,
                data_source__in=data_source
            ).using(alias=machine)

        else:
            performance = UtilizationStatus.objects.filter(
                device_name__in=machine_dict[machine],
                service_name__in=service_name,
                data_source__in=data_source
            ).using(alias=machine)
    return performance


def get_higher_severity(severity_dict):
    """

    :param severity_dict:
    :return:
    """
    s, a = None, None
    for severity in severity_dict:
        s = severity
        a = severity_dict[severity]
        if severity in ['critical']:
            #return severity, age
            return severity, severity_dict[severity]
        elif severity in ['warning']:
            return severity, severity_dict[severity]
        elif severity in ['unknown']:
            continue
        else:
            continue

    return s, float(a)


def get_time():
    """

    :return: start time and end time
    """
    end_date = format(datetime.datetime.now(), 'U')
    start_date = format(datetime.datetime.now() + datetime.timedelta(days=-1), 'U')

    return start_date, end_date


def get_average_sector_util(device_object, service, data_source, getit='val'):
    """

    :return:
    """
    start_date, end_date = get_time()
    if getit == 'val':
        perf = PerformanceService.objects.filter(
            device_name=device_object.device_name,
            service_name=service,
            data_source=data_source,
            sys_timestamp__gte=start_date,
            sys_timestamp__lte=end_date
        ).using(alias=device_object.machine.name).aggregate(Avg('current_value'))

    elif getit == 'per':
        perf = Utilization.objects.filter(
            device_name=device_object.device_name,
            service_name=service,
            data_source=data_source,
            sys_timestamp__gte=start_date,
            sys_timestamp__lte=end_date
        ).using(alias=device_object.machine.name).aggregate(Avg('current_value'))

    else:
        return 0

    return float(perf['current_value__avg'])


def get_peak_sector_util(device_object, service, data_source, getit='val'):
    """

    :return:
    """
    start_date, end_date = get_time()
    if getit == 'val':
        max_value = PerformanceService.objects.filter(
            device_name=device_object.device_name,
            service_name=service,
            data_source=data_source,
            sys_timestamp__gte=start_date,
            sys_timestamp__lte=end_date
        ).using(alias=device_object.machine.name).aggregate(Max('current_value'))['current_value__max']

        perf = PerformanceService.objects.filter(
                device_name=device_object.device_name,
                service_name=service,
                data_source=data_source,
                sys_timestamp__gte=start_date,
                sys_timestamp__lte=end_date,
                current_value=max_value
            ).using(alias=device_object.machine.name).values('current_value', 'sys_timestamp')

    elif getit == 'per':
        max_value = Utilization.objects.filter(
            device_name=device_object.device_name,
            service_name=service,
            data_source=data_source,
            sys_timestamp__gte=start_date,
            sys_timestamp__lte=end_date
        ).using(alias=device_object.machine.name).aggregate(Max('current_value'))['current_value__max']

        perf = Utilization.objects.filter(
                device_name=device_object.device_name,
                service_name=service,
                data_source=data_source,
                sys_timestamp__gte=start_date,
                sys_timestamp__lte=end_date,
                current_value=max_value
            ).using(alias=device_object.machine.name).values('current_value', 'sys_timestamp')

    else:
        return 0

    if perf and len(perf):
        return float(perf[0]['current_value']), float(perf[0]['sys_timestamp'])


def update_sector_status(sectors, cbw, kpi, val, technology):
    """
    update the sector status per sector id wise
    :return:
    """
    bulk_create_scs = []
    sector_capacity = None
    current_in_per = None
    current_in_val = None

    avg_in_per = None
    avg_in_val = None
    peak_in_per = None
    peak_in_val = None
    peak_in_timestamp = None

    current_out_per = None
    current_out_val = None

    avg_out_per = None
    avg_out_val = None
    peak_out_per = None
    peak_out_val = None
    peak_out_timestamp = None

    sys_timestamp = 0
    organization = get_default_org()
    severity = 'unknown'
    age = 0

    for sector in sectors:
        #start with single sector
        #get the sector --> device
        #stitch together values
        #take special care of PMP1 & PMP2 cases
        if technology.lower() == 'wimax':
            scs = None
            try:
                scs = SectorCapacityStatus.objects.get(sector=sector)
            except Exception as e:
                logger.exception(e)

            if 'pmp1' in sector.sector_configured_on_port.name.lower():
                sector_capacity_s = cbw.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp_bw_invent',
                    data_source='pmp1_bw'
                ).values_list('current_value', flat=True)

                if sector_capacity_s and len(sector_capacity_s):
                    sector_capacity = sector_capacity_s[0]
                else:
                    #we dont want to store any data till we get a CBW
                    continue

                #current in/out values
                current_in_val_s = val.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp1_dl_util_bgp',
                    data_source='pmp1_dl_util'
                ).values_list('current_value', flat=True)

                if current_in_val_s and len(current_in_val_s):
                    current_in_val = current_in_val_s[0]

                current_out_val_s = val.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp1_ul_util_bgp',
                    data_source='pmp1_ul_util'
                ).values_list('current_value', flat=True)

                if current_out_val_s and len(current_out_val_s):
                    current_out_val = current_out_val_s[0]
                #current in/out values

                severity_s = {}

                #current in/out percentage
                current_in_per_s = kpi.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp1_dl_util_kpi',
                    data_source='pmp1_dl_util_kpi'
                ).values('current_value', 'age', 'severity', 'sys_timestamp')

                if current_in_per_s and len(current_in_per_s):
                    current_in_per = current_in_per_s[0]['current_value']
                    severity_s[current_in_per_s[0]['severity']] = current_in_per_s[0]['age']
                    sys_timestamp = current_in_per_s[0]['sys_timestamp']

                current_out_per_s = kpi.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp1_ul_util_kpi',
                    data_source='pmp1_ul_util_kpi'
                ).values('current_value', 'age', 'severity', 'sys_timestamp')

                if current_out_per_s and len(current_out_per_s):
                    current_out_per = current_out_per_s[0]['current_value']
                    severity_s[current_out_per_s[0]['severity']] = current_out_per_s[0]['age']
                    sys_timestamp = current_out_per_s[0]['sys_timestamp']

                severity, age = get_higher_severity(severity_s)
                #now that we have severity and age
                #all we need to do now
                #is gather the average and peak values
                avg_in_val = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='wimax_pmp1_dl_util_bgp',
                                                     data_source='pmp1_dl_util',
                                                     getit='val'
                )

                avg_out_val = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='wimax_pmp1_ul_util_bgp',
                                                     data_source='pmp1_ul_util',
                                                     getit='val'
                )

                avg_in_per = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='wimax_pmp1_dl_util_kpi',
                                                     data_source='pmp1_dl_util_kpi',
                                                     getit='per'
                )

                avg_out_per = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='wimax_pmp1_ul_util_kpi',
                                                     data_source='pmp1_ul_util_kpi',
                                                     getit='per'
                )

                peak_in_val, peak_in_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='wimax_pmp1_dl_util_bgp',
                                                    data_source='pmp1_dl_util',
                                                    getit='val'
                )

                peak_out_val, peak_out_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='wimax_pmp1_ul_util_bgp',
                                                    data_source='pmp1_ul_util',
                                                    getit='val'
                )

                peak_in_per, peak_in_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='wimax_pmp1_dl_util_kpi',
                                                    data_source='pmp1_dl_util_kpi',
                                                    getit='per'
                )

                peak_out_per, peak_out_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='wimax_pmp1_ul_util_kpi',
                                                    data_source='pmp1_ul_util_kpi',
                                                    getit='per'
                )


            elif 'pmp2' in sector.sector_configured_on_port.name.lower():
                sector_capacity_s = cbw.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp_bw_invent',
                    data_source='pmp2_bw'
                ).values_list('current_value', flat=True)

                if sector_capacity_s and len(sector_capacity_s):
                    sector_capacity = sector_capacity_s[0]
                else:
                    #we dont want to store any data till we get a CBW
                    continue
                #current in/out values
                current_in_val_s = val.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp2_dl_util_bgp',
                    data_source='pmp2_dl_util'
                ).values_list('current_value', flat=True)

                if current_in_val_s and len(current_in_val_s):
                    current_in_val = current_in_val_s[0]

                current_out_val_s = val.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp2_ul_util_bgp',
                    data_source='pmp2_ul_util'
                ).values_list('current_value', flat=True)

                if current_out_val_s and len(current_out_val_s):
                    current_out_val = current_out_val_s[0]
                #current in/out values

                severity_s = {}

                #current in/out percentage
                current_in_per_s = kpi.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp2_dl_util_kpi',
                    data_source='pmp2_dl_util_kpi'
                ).values('current_value', 'age', 'severity', 'sys_timestamp')

                if current_in_per_s and len(current_in_per_s):
                    current_in_per = current_in_per_s[0]['current_value']
                    severity_s[current_in_per_s[0]['severity']] = current_in_per_s[0]['age']
                    sys_timestamp = current_in_per_s[0]['sys_timestamp']

                current_out_per_s = kpi.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp2_ul_util_kpi',
                    data_source='pmp2_ul_util_kpi'
                ).values('current_value', 'age', 'severity', 'sys_timestamp')

                if current_out_per_s and len(current_out_per_s):
                    current_out_per = current_out_per_s[0]['current_value']
                    severity_s[current_out_per_s[0]['severity']] = current_out_per_s[0]['age']
                    sys_timestamp = current_out_per_s[0]['sys_timestamp']

                severity, age = get_higher_severity(severity_s)
                #now that we have severity and age
                #all we need to do now
                #is gather the average and peak values
                avg_in_val = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='wimax_pmp2_dl_util_bgp',
                                                     data_source='pmp2_dl_util',
                                                     getit='val'
                )

                avg_out_val = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='wimax_pmp2_ul_util_bgp',
                                                     data_source='pmp2_ul_util',
                                                     getit='val'
                )

                avg_in_per = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='wimax_pmp2_dl_util_kpi',
                                                     data_source='pmp2_dl_util_kpi',
                                                     getit='per'
                )

                avg_out_per = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='wimax_pmp2_ul_util_kpi',
                                                     data_source='pmp2_ul_util_kpi',
                                                     getit='per'
                )

                peak_in_val, peak_in_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='wimax_pmp2_dl_util_bgp',
                                                    data_source='pmp2_dl_util',
                                                    getit='val'
                )

                peak_out_val, peak_out_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='wimax_pmp2_ul_util_bgp',
                                                    data_source='pmp2_ul_util',
                                                    getit='val'
                )

                peak_in_per, peak_in_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='wimax_pmp2_dl_util_kpi',
                                                    data_source='pmp2_dl_util_kpi',
                                                    getit='per'
                )

                peak_out_per, peak_out_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='wimax_pmp2_ul_util_kpi',
                                                    data_source='pmp2_ul_util_kpi',
                                                    getit='per'
                )
            else:
                #we dont give a f*** if we dont get a valid port
                continue

            if scs:
                #update the scs
                scs.sector = sector
                scs.sector_sector_id = sector.sector_id
                scs.sector_capacity = float(sector_capacity)
                scs.current_in_per = float(current_in_per)
                scs.current_in_val = float(current_in_val)
                scs.avg_in_per = float(avg_in_per)
                scs.avg_in_val = float(avg_in_val)
                scs.peak_in_per = float(peak_in_per)
                scs.peak_in_val = float(peak_in_val)
                scs.peak_in_timestamp = float(peak_in_timestamp)
                scs.current_out_per = float(current_out_per)
                scs.current_out_val = float(current_out_val)
                scs.avg_out_per = float(avg_out_per)
                scs.avg_out_val = float(avg_out_val)
                scs.peak_out_per = float(peak_out_per)
                scs.peak_out_val = float(peak_out_val)
                scs.peak_out_timestamp = float(peak_out_timestamp)
                scs.sys_timestamp = float(sys_timestamp)
                scs.organization = sector.organization
                scs.severity = severity
                scs.age = float(age)
                scs.save()

            else:
                bulk_create_scs.append(
                    SectorCapacityStatus
                    (
                        sector=sector,
                        sector_sector_id=sector.sector_id,
                        sector_capacity=float(sector_capacity),

                        current_in_per=float(current_in_per),
                        current_in_val=float(current_in_val),

                        avg_in_per=float(avg_in_per),
                        avg_in_val=float(avg_in_val),
                        peak_in_per=float(peak_in_per),
                        peak_in_val=float(peak_in_val),
                        peak_in_timestamp=float(peak_in_timestamp),

                        current_out_per=float(current_out_per),
                        current_out_val=float(current_out_val),

                        avg_out_per=float(avg_out_per),
                        avg_out_val=float(avg_out_val),
                        peak_out_per=float(peak_out_per),
                        peak_out_val=float(peak_out_val),
                        peak_out_timestamp=float(peak_out_timestamp),

                        sys_timestamp=float(sys_timestamp),
                        organization=sector.organization,
                        severity=severity,
                        age=float(age)
                    )
                )

        elif technology.lower() == 'pmp':
            pass
        else:
            return False
    if len(bulk_create_scs):
        SectorCapacityStatus.objects.bulk_create(bulk_create_scs)
        return True
    return False


def performance_query(table_name, device_list, service_list, data_source_list):
    """

    :return:
    """
    query = '''
    SELECT device_name, ip_address, current_value, severity, age, refer
    FROM {0}
    WHERE (device_name in {1} and service_name in {2} and data_source in {3})
        '''.format(table_name, device_list, service_list, data_source_list)
    return query