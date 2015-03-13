from celery import task, group

from django.db.models import Count, Max, Avg #F, Max, Min, Q, Sum, Avg

#task for updating the sector capacity per 5 minutes
#need to run for PMP, WiMAX technology

from capacity_management.models import SectorCapacityStatus, BackhaulCapacityStatus
from inventory.models import get_default_org, Sector, Backhaul, BaseStation
from device.models import DeviceTechnology, Device, DevicePort, DeviceType
from service.models import ServiceDataSource
from inventory.utils.util import prepare_machines

from inventory.tasks import get_devices, bulk_update_create

from nocout.utils.util import fetch_raw_result

from performance.models import UtilizationStatus, InventoryStatus, ServiceStatus, Utilization, PerformanceService, Topology

from django.utils.dateformat import format
import datetime

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from nocout.settings import CAPACITY_SPECIFIC_TIME

#to be moved to settings.py
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
            'service_name': ['cambium_ul_utilization', 'cambium_dl_utilization'],
            'data_source': ['ul_utilization', 'dl_utilization']

        },
        'per': {
            'model': 'performance_utilizationstatus',
            'service_name': ['cambium_ul_util_kpi', 'cambium_dl_util_kpi'],
            'data_source': ['cam_ul_util_kpi', 'cam_dl_util_kpi']
        }
    },
}


@task()
def gather_backhaul_status():
    """

    :return:
    """
    # we need devices
    # we need the values
    # we need the machines

    # fetch all backhaul device
    # bh_devices = Backhaul.objects.filter('bh_configured_on__isnull=False).values_list('bh_configured_on', flat=True)

    # fetch all base stations
    base_stations = BaseStation.objects.filter(
        backhaul__bh_configured_on__isnull=False,
        bh_port_name__isnull=False,
        backhaul__bh_configured_on__is_added_to_nms=1,
        bh_capacity__isnull=False
    ).select_related(
        'backhaul',
        'backhaul__bh_configured_on',
        'backhaul__bh_configured_on__machine'
    )

    bh_devices = Backhaul.objects.select_related(
        'bh_configured_on',
        'bh_configured_on__machine'
    ).filter(
        id__in=base_stations.values_list('backhaul__id', flat=True),
        bh_configured_on__isnull=False,
        bh_configured_on__is_added_to_nms=1
    )

    # get machines associated to all base station devices
    machines = set([bs.backhaul.bh_configured_on.machine.name for bs in base_stations])

    # get data sources
    ports = set([bs.bh_port_name for bs in base_stations])

    data_sources = set(ServiceDataSource.objects.filter(
        name__in=DevicePort.objects.filter(alias__in=ports).values_list('name', flat=True)
    ).values_list('name', flat=True))

    kpi_services = ['rici_dl_util_kpi', 'rici_ul_util_kpi', 'mrotek_dl_util_kpi', 'mrotek_ul_util_kpi',
                    'switch_dl_util_kpi', 'switch_ul_util_kpi']
    val_services = ['rici_dl_utilization', 'rici_ul_utilization', 'mrotek_dl_utilization', 'mrotek_ul_utilization',
                    'switch_dl_utilization', 'switch_ul_utilization']

    g_jobs = list()
    ret = False

    for machine in machines:
        machine_bh_devices = set(bh_devices.filter(
            bh_configured_on__machine__name=machine
        ).values_list(
            'bh_configured_on__device_name',
            flat=True
        ))

        val = ServiceStatus.objects.filter(
                    device_name__in=machine_bh_devices,
                    service_name__in=val_services,
                    data_source__in=data_sources
        ).order_by().using(alias=machine)
        kpi = UtilizationStatus.objects.filter(
                    device_name__in=machine_bh_devices,
                    service_name__in=kpi_services,
                    data_source__in=data_sources
        ).order_by().using(alias=machine)

        # pass only base stations connected on a machine

        if kpi.count() and val.count():
            bs = base_stations.filter(backhaul__bh_configured_on__machine__name=machine)
            g_jobs.append(
                update_backhaul_status.s(
                    basestations=bs,
                    kpi=kpi,
                    val=val
                )
            )

    if len(g_jobs):
        job = group(g_jobs)
        result = job.apply_async()
        # for r in result.get():
        #     ret |= r
        return True

    return ret

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

    g_jobs = list()

    for machine in machine_dict:
        if technology.lower() == 'wimax':
            sectors = Sector.objects.filter(sector_configured_on__device_technology=technology_object.id,
                                            sector_configured_on__is_added_to_nms=1,
                                            sector_configured_on__in=machine_dict[machine],
                                            sector_id__isnull=False,
                                            sector_configured_on_port__isnull=False
                                            ).prefetch_related('sector_configured_on',
                                                               'sector_configured_on_port',
                                                               'base_station',
                                                               'base_station__city',
                                                               'base_station__state'
                                            ).annotate(Count('sector_id'))

            cbw = get_sector_bw(devices=machine_dict[machine],
                                service_name=tech_model_service['wimax']['cbw']['service_name'],
                                data_source=tech_model_service['wimax']['cbw']['data_source'],
                                machine=machine
            )

            sector_val = get_sector_val(devices=machine_dict[machine],
                                        service_name=tech_model_service['wimax']['val']['service_name'],
                                        data_source=tech_model_service['wimax']['val']['data_source'],
                                        machine=machine
            )

            sector_kpi = get_sector_kpi(devices=machine_dict[machine],
                                        service_name=tech_model_service['wimax']['per']['service_name'],
                                        data_source=tech_model_service['wimax']['per']['data_source'],
                                        machine=machine
            )

            g_jobs.append(update_sector_status.s(sectors=sectors,
                                                 cbw=cbw,
                                                 kpi=sector_kpi,
                                                 val=sector_val,
                                                 technology=technology)
            )

        elif technology.lower() == 'pmp':
            sectors = Sector.objects.filter(sector_configured_on__device_technology=technology_object.id,
                                            sector_configured_on__is_added_to_nms=1,
                                            sector_configured_on__in=machine_dict[machine],
                                            sector_id__isnull=False,
                                            sector_configured_on_port__isnull=True
                                            ).prefetch_related('sector_configured_on',
                                                               'base_station',
                                                               'base_station__city',
                                                               'base_station__state'
                                            ).annotate(Count('sector_id'))

            cbw = None

            sector_val = get_sector_val(devices=machine_dict[machine],
                                        service_name=tech_model_service['pmp']['val']['service_name'],
                                        data_source=tech_model_service['pmp']['val']['data_source'],
                                        machine=machine
            )

            sector_kpi = get_sector_kpi(devices=machine_dict[machine],
                                        service_name=tech_model_service['pmp']['per']['service_name'],
                                        data_source=tech_model_service['pmp']['per']['data_source'],
                                        machine=machine
            )

            g_jobs.append(update_sector_status.s(sectors=sectors,
                                                 cbw=cbw,
                                                 kpi=sector_kpi,
                                                 val=sector_val,
                                                 technology=technology)
            )

        else:
            return False
    ret = False
    if len(g_jobs):
        job = group(g_jobs)
        result = job.apply_async()
        # for r in result.get():
        #     ret |= r
        return True

    return ret


def get_sector_bw(devices, service_name, data_source, machine):
    """

    :return:
    """

    performance = InventoryStatus.objects.filter(
        device_name__in=devices,
        service_name__in=service_name,
        data_source__in=data_source
    ).order_by().using(alias=machine)

    return performance


def get_sector_val(devices, service_name, data_source, machine):
    """


    :param machine_dict:
    :param service_name:
    :param data_source:
    :return:
    """

    performance = ServiceStatus.objects.filter(
        device_name__in=devices,
        service_name__in=service_name,
        data_source__in=data_source
    ).order_by().using(alias=machine)

    return performance


def get_sector_kpi(devices, service_name, data_source, machine):
    """

    :param machine_dict:
    :param service_name:
    :param data_source:
    :return:
    """

    performance = UtilizationStatus.objects.filter(
        device_name__in=devices,
        service_name__in=service_name,
        data_source__in=data_source
    ).order_by().using(alias=machine)

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

    return s, a


def compare_old_severity(old_severity, new_severity, old_age, new_age):
    """

    :param old_severity: 'warning', 'critical', 'unknown', 'ok'
    :param new_severity: 'warning', 'critical', 'unknown', 'ok'
    :param old_age: float
    :param new_age: float
    :return:
    """
    if old_severity in ['warning', 'critical'] and new_severity in ['warning', 'critical']:
        # since both were in non ok state
        # lets just return the higher value
        severity_dict = {
            old_severity: old_age,
            new_severity: new_age
        }
        return get_higher_severity(severity_dict)

    elif old_severity in ['ok', 'unknown'] or new_severity in ['ok', 'unknown']:
        # we don't know what's going on
        # what ever is the latest lets just go with it
        return new_severity, new_age

    else:
        # severity must be existsting
        return new_severity, new_age


def get_time():
    """

    :return: start time and end time
    """
    tdy = datetime.datetime.today()
    end_time = datetime.datetime(tdy.year, tdy.month, tdy.day, 0, 0)
    end_date = format(end_time, 'U')
    start_date = format(end_time + datetime.timedelta(days=-1), 'U')

    return float(start_date), float(end_date)


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

    if perf and perf['current_value__avg']:
        return float(perf['current_value__avg'])
    else:
        return 0


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
        return 0, 0

    if perf and len(perf):
        return float(perf[0]['current_value']), float(perf[0]['sys_timestamp'])

    else:
        return 0, 0


def calc_util_last_day():
    """

    :return: True. False
    """

    tdy = datetime.datetime.today()

    # this is the end time today's 00:10:00
    end_time = float(format(datetime.datetime(tdy.year, tdy.month, tdy.day, 0, 10), 'U'))

    # this is the start time yesterday's 00:00:00
    start_time = float(format(datetime.datetime(tdy.year, tdy.month, tdy.day, 0, 0), 'U'))

    # this is the time when we would be considering to get last 24 hours performance
    time_now = float(format(datetime.datetime.now(), 'U'))

    if start_time < time_now < end_time or CAPACITY_SPECIFIC_TIME:
        return True
    return False


@task()
def update_backhaul_status(basestations, kpi, val):
    """
    update the backhaul status per sector id wise
    :return:
    """

    bulk_update_bhs = []
    bulk_create_bhs = []
    backhaul_capacity = None
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

    for bs in basestations:
        # base station device
        bh_device = bs.backhaul.bh_configured_on

        # base station device type
        bs_device_type = bh_device.device_type

        # device type mapping
        # <device type: id>
        # switch: 12
        # pine: 13
        # rici: 14
        # define service names as per device type

        # this complete mapping can be fetced from
        # device type : service : service data source mapping
        # if device type is 'switch'
        if bs_device_type == 12:
            val_ul_service = 'switch_ul_utilization'
            val_dl_service = 'switch_dl_utilization'
            kpi_ul_service = 'switch_ul_util_kpi'
            kpi_dl_service = 'switch_dl_util_kpi'
        # if device type is 'pine converter'
        elif bs_device_type == 13:
            val_ul_service = 'mrotek_ul_utilization'
            val_dl_service = 'mrotek_dl_utilization'
            kpi_ul_service = 'mrotek_ul_util_kpi'
            kpi_dl_service = 'mrotek_dl_util_kpi'
        # if device type is 'rici converter'
        elif bs_device_type == 14:
            val_ul_service = 'rici_ul_utilization'
            val_dl_service = 'rici_dl_utilization'
            kpi_ul_service = 'rici_ul_util_kpi'
            kpi_dl_service = 'rici_dl_util_kpi'
        else:
            # proceed only if there is proper device type mapping
            continue

        # get data source name
        data_source = None
        try:
            #we dont care about port, till it actually is mapped to a data source
            data_source = ServiceDataSource.objects.get(name=DevicePort.objects.get(alias=bs.bh_port_name).name).name
        except Exception as e:
            # logger.debug('Back-hual Port {0}'.format(bs.bh_port_name))
            # logger.debug('Device Port : {0}'.format(DevicePort.objects.get(alias=bs.bh_port_name).name))
            logger.exception(e)
            # if we don't have a port mapping
            # do not query database
            continue

        if data_source:
            bhs = None
            try:
                bhs = BackhaulCapacityStatus.objects.get(
                    backhaul=bs.backhaul,
                    basestation=bs
                    # bh_port_name=bs.bh_port_name
                )
            except Exception as e:
                pass

            # backhaul capacity
            if bs.bh_capacity:
                backhaul_capacity = bs.bh_capacity
            else:
                logger.exception('No Base-Station - Back-haul Capacity Not Possible')
                continue

            # current in/out values
            current_in_val_s = val.filter(
                device_name=bh_device.device_name,
                service_name=val_dl_service,
                data_source=data_source
            ).values_list('current_value', flat=True)

            if current_in_val_s and len(current_in_val_s):
                current_in_val = current_in_val_s[0]

            current_out_val_s = val.filter(
                device_name=bh_device.device_name,
                service_name=val_ul_service,
                data_source=data_source
            ).values_list('current_value', flat=True)

            if current_out_val_s and len(current_out_val_s):
                current_out_val = current_out_val_s[0]

            severity_s = {}

            # current in/out percentage
            current_in_per_s = kpi.filter(
                device_name=bh_device.device_name,
                service_name=kpi_ul_service,
                data_source=data_source
            ).values('current_value', 'age', 'severity', 'sys_timestamp')

            if current_in_per_s and len(current_in_per_s):
                current_in_per = current_in_per_s[0]['current_value']
                severity_s[current_in_per_s[0]['severity']] = current_in_per_s[0]['age']
                sys_timestamp = current_in_per_s[0]['sys_timestamp']

            current_out_per_s = kpi.filter(
                device_name=bh_device.device_name,
                service_name=kpi_ul_service,
                data_source=data_source
            ).values('current_value', 'age', 'severity', 'sys_timestamp')

            if current_out_per_s and len(current_out_per_s):
                current_out_per = current_out_per_s[0]['current_value']
                severity_s[current_out_per_s[0]['severity']] = current_out_per_s[0]['age']
                sys_timestamp = current_out_per_s[0]['sys_timestamp']

            severity, age = get_higher_severity(severity_s)

            # now that we have severity and age all we need to do now is gather the average and peak values
            if calc_util_last_day():
                avg_in_val = get_average_sector_util(device_object=bh_device,
                                                     service=val_dl_service,
                                                     data_source=data_source,
                                                     getit='val'
                )

                avg_out_val = get_average_sector_util(device_object=bh_device,
                                                     service=val_ul_service,
                                                     data_source=data_source,
                                                     getit='val'
                )

                avg_in_per = get_average_sector_util(device_object=bh_device,
                                                     service=kpi_dl_service,
                                                     data_source=data_source,
                                                     getit='per'
                )

                avg_out_per = get_average_sector_util(device_object=bh_device,
                                                     service=kpi_ul_service,
                                                     data_source=data_source,
                                                     getit='per'
                )

                peak_in_val, peak_in_timestamp = get_peak_sector_util(device_object=bh_device,
                                                    service=val_dl_service,
                                                    data_source=data_source,
                                                    getit='val'
                )

                peak_out_val, peak_out_timestamp = get_peak_sector_util(device_object=bh_device,
                                                    service=val_ul_service,
                                                    data_source=data_source,
                                                    getit='val'
                )

                peak_in_per, peak_in_timestamp = get_peak_sector_util(device_object=bh_device,
                                                    service=kpi_dl_service,
                                                    data_source=data_source,
                                                    getit='per'
                )

                peak_out_per, peak_out_timestamp = get_peak_sector_util(device_object=bh_device,
                                                    service=kpi_ul_service,
                                                    data_source=data_source,
                                                    getit='per'
                )

            if bhs:
                # values that would be updated per 5 minutes
                bhs.backhaul_capacity = float(backhaul_capacity) if backhaul_capacity else 0
                bhs.current_in_per = float(current_in_per) if current_in_per else 0
                bhs.current_in_val = float(current_in_val) if current_in_val else 0
                bhs.sys_timestamp = float(sys_timestamp) if sys_timestamp else 0
                bhs.organization = bs.backhaul.organization if bs.backhaul.organization else 1
                bhs.severity = severity if severity else 'unknown'
                bhs.age = float(age) if age else 0
                if calc_util_last_day():  # values that would be updated once in a day
                    bhs.avg_in_per = float(avg_in_per) if avg_in_per else 0
                    bhs.avg_in_val = float(avg_in_val) if avg_in_val else 0
                    bhs.peak_in_per = float(peak_in_per) if peak_in_per else 0
                    bhs.peak_in_val = float(peak_in_val) if peak_in_val else 0
                    bhs.peak_in_timestamp = float(peak_in_timestamp) if peak_in_timestamp else 0
                    bhs.current_out_per = float(current_out_per) if current_out_per else 0
                    bhs.current_out_val = float(current_out_val) if current_out_val else 0
                    bhs.avg_out_per = float(avg_out_per) if avg_out_per else 0
                    bhs.avg_out_val = float(avg_out_val) if avg_out_val else 0
                    bhs.peak_out_per = float(peak_out_per) if peak_out_per else 0
                    bhs.peak_out_val = float(peak_out_val) if peak_out_val else 0
                    bhs.peak_out_timestamp = float(peak_out_timestamp) if peak_out_timestamp else 0

                bulk_update_bhs.append(bhs)

            else:

                bulk_create_bhs.append(
                    BackhaulCapacityStatus
                    (
                        backhaul=bs.backhaul,
                        basestation=bs,
                        bh_port_name=bs.bh_port_name,

                        backhaul_capacity=float(backhaul_capacity) if backhaul_capacity else 0,
                        current_in_per=float(current_in_per) if current_in_per else 0,
                        current_in_val=float(current_in_val) if current_in_val else 0,
                        avg_in_per=float(avg_in_per) if avg_in_per else 0,
                        avg_in_val=float(avg_in_val) if avg_in_val else 0,
                        peak_in_per=float(peak_in_per) if peak_in_per else 0,
                        peak_in_val=float(peak_in_val) if peak_in_val else 0,
                        peak_in_timestamp=float(peak_in_timestamp) if peak_in_timestamp else 0,
                        current_out_per=float(current_out_per) if current_out_per else 0,
                        current_out_val=float(current_out_val) if current_out_val else 0,
                        avg_out_per=float(avg_out_per) if avg_out_per else 0,
                        avg_out_val=float(avg_out_val) if avg_out_val else 0,
                        peak_out_per=float(peak_out_per) if peak_out_per else 0,
                        peak_out_val=float(peak_out_val) if peak_out_val else 0,
                        peak_out_timestamp=float(peak_out_timestamp) if peak_out_timestamp else 0,
                        sys_timestamp=float(sys_timestamp) if sys_timestamp else 0,
                        organization=bs.backhaul.organization if bs.backhaul.organization else 1,
                        severity=severity if severity else 'unknown',
                        age=float(age) if age else 0
                    )
                )


    g_jobs = list()

    if len(bulk_create_bhs):
        g_jobs.append(bulk_update_create.s(bulk_create_bhs, action='create', model=BackhaulCapacityStatus))

    if len(bulk_update_bhs):
        g_jobs.append(bulk_update_create.s(bulk_update_bhs, action='update', model=BackhaulCapacityStatus))

    if not len(g_jobs):
        return False

    job = group(g_jobs)
    ret = False
    result = job.apply_async()  # start the jobs
    # for r in result.get():
    #     ret |= r
    return True


@task()
def update_sector_status(sectors, cbw, kpi, val, technology):
    """
    update the sector status per sector id wise
    :return:
    """


    bulk_update_scs = []
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

    processed_sectors = {}

    for sector in sectors:
        #deduplication of the sector on the basis of sector ID
        if sector.sector_id in processed_sectors:
            continue
        else:
            processed_sectors[sector.sector_id] = sector.sector_id

        #start with single sector
        #get the sector --> device
        #stitch together values
        #take special care of PMP1 & PMP2 cases
        if technology.lower() == 'wimax':
            scs = None
            try:
                scs = SectorCapacityStatus.objects.get(
                    sector=sector,
                    sector_sector_id=sector.sector_id
                )
            except Exception as e:
                logger.debug("WiMAX : {0}".format(e.message))
                pass

            if 'pmp1' in sector.sector_configured_on_port.name.lower():
                sector_capacity_s = cbw.filter(
                    device_name=sector.sector_configured_on.device_name,
                    service_name='wimax_pmp_bw_invent',
                    data_source='pmp1_bw'
                ).values_list('current_value', flat=True)

                if sector_capacity_s and len(sector_capacity_s):
                    sector_capacity = sector_capacity_s[0]
                else:
                    logger.debug("#we dont want to store any data till we get a CBW No CBW for : {0}".format(sector.sector_id))
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

                # check for the time_noe
                # time now would be between start_time
                # and end_time
                # for a limited cycle between last day's 23:55:00 and 00:05:00

                if calc_util_last_day():
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
                    logger.debug("#we dont want to store any data till we get a CBW No CBW for : {0}".format(sector.sector_id))
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

                if calc_util_last_day():
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
                logger.debug("WiMAX : #we dont give a f*** if we dont get a valid port")
                continue

            if scs:
                #update the scs
                # scs.sector = sector
                # scs.sector_sector_id = sector.sector_id
                scs.sector_capacity = float(sector_capacity) if sector_capacity else 0
                scs.current_in_per = float(current_in_per) if current_in_per else 0
                scs.current_in_val = float(current_in_val) if current_in_val else 0
                scs.sys_timestamp = float(sys_timestamp) if sys_timestamp else 0
                scs.organization = sector.organization if sector.organization else 1
                scs.severity = severity if severity else 'unknown'
                scs.age = float(age) if age else 0
                if calc_util_last_day():
                    scs.avg_in_per = float(avg_in_per) if avg_in_per else 0
                    scs.avg_in_val = float(avg_in_val) if avg_in_val else 0
                    scs.peak_in_per = float(peak_in_per) if peak_in_per else 0
                    scs.peak_in_val = float(peak_in_val) if peak_in_val else 0
                    scs.peak_in_timestamp = float(peak_in_timestamp) if peak_in_timestamp else 0
                    scs.current_out_per = float(current_out_per) if current_out_per else 0
                    scs.current_out_val = float(current_out_val) if current_in_val else 0
                    scs.avg_out_per = float(avg_out_per) if avg_out_per else 0
                    scs.avg_out_val = float(avg_out_val) if avg_out_val else 0
                    scs.peak_out_per = float(peak_out_per) if peak_out_per else 0
                    scs.peak_out_val = float(peak_out_val) if peak_out_val else 0
                    scs.peak_out_timestamp = float(peak_out_timestamp) if peak_out_timestamp else 0
                # scs.save()
                bulk_update_scs.append(scs)

            else:
                bulk_create_scs.append(
                    SectorCapacityStatus
                    (
                        sector=sector,
                        sector_sector_id=sector.sector_id,
                        sector_capacity=float(sector_capacity) if sector_capacity else 0,

                        current_in_per=float(current_in_per) if current_in_per else 0,
                        current_in_val=float(current_in_val) if current_in_val else 0,

                        avg_in_per=float(avg_in_per) if avg_in_per else 0,
                        avg_in_val=float(avg_in_val) if avg_in_val else 0,
                        peak_in_per=float(peak_in_per) if peak_in_per else 0,
                        peak_in_val=float(peak_in_val) if peak_in_val else 0,
                        peak_in_timestamp=float(peak_in_timestamp) if peak_in_timestamp else 0,

                        current_out_per=float(current_out_per) if current_out_per else 0,
                        current_out_val=float(current_out_val) if current_out_val else 0,

                        avg_out_per=float(avg_out_per) if avg_out_per else 0,
                        avg_out_val=float(avg_out_val) if avg_out_val else 0,
                        peak_out_per=float(peak_out_per) if peak_out_per else 0,
                        peak_out_val=float(peak_out_val) if peak_out_val else 0,
                        peak_out_timestamp=float(peak_out_timestamp) if peak_out_timestamp else 0,

                        sys_timestamp=float(sys_timestamp) if sys_timestamp else 0,
                        organization=sector.organization if sector.organization else 1,
                        severity=severity if severity else 'unknown',
                        age=float(age) if age else 0
                    )
                )

        elif technology.lower() == 'pmp':
            scs = None
            try:
                scs = SectorCapacityStatus.objects.get(
                    sector=sector,
                    sector_sector_id=sector.sector_id
                )
            except Exception as e:
                logger.debug("PMP : {0}".format(e.message))
                pass
                # logger.exception(e)

            sector_capacity = 7 #fixed for PMP

            #current in/out values
            current_in_val_s = val.filter(
                device_name=sector.sector_configured_on.device_name,
                service_name='cambium_dl_utilization',
                data_source='dl_utilization'
            ).values_list('current_value', flat=True)

            if current_in_val_s and len(current_in_val_s):
                current_in_val = current_in_val_s[0]

            current_out_val_s = val.filter(
                device_name=sector.sector_configured_on.device_name,
                service_name='cambium_ul_utilization',
                data_source='ul_utilization'
            ).values_list('current_value', flat=True)

            if current_out_val_s and len(current_out_val_s):
                current_out_val = current_out_val_s[0]
            #current in/out values

            severity_s = {}

            #current in/out percentage
            current_in_per_s = kpi.filter(
                device_name=sector.sector_configured_on.device_name,
                service_name='cambium_dl_util_kpi',
                data_source='cam_dl_util_kpi'
            ).values('current_value', 'age', 'severity', 'sys_timestamp')

            if current_in_per_s and len(current_in_per_s):
                current_in_per = current_in_per_s[0]['current_value']
                severity_s[current_in_per_s[0]['severity']] = current_in_per_s[0]['age']
                sys_timestamp = current_in_per_s[0]['sys_timestamp']

            current_out_per_s = kpi.filter(
                device_name=sector.sector_configured_on.device_name,
                service_name='cambium_ul_util_kpi',
                data_source='cam_ul_util_kpi'
            ).values('current_value', 'age', 'severity', 'sys_timestamp')

            if current_out_per_s and len(current_out_per_s):
                current_out_per = current_out_per_s[0]['current_value']
                severity_s[current_out_per_s[0]['severity']] = current_out_per_s[0]['age']
                sys_timestamp = current_out_per_s[0]['sys_timestamp']

            severity, age = get_higher_severity(severity_s)

            #condition is : if the topology count >= 8 : the sector is
            #stop provisioning state
            if Topology.objects.filter(device_name=sector.sector_configured_on.device_name).count() >= 8:
                severity = 'critical'

            if not severity and not age:
                continue

            if calc_util_last_day():
                avg_in_val = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='cambium_dl_utilization',
                                                     data_source='dl_utilization',
                                                     getit='val'
                )

                avg_out_val = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='cambium_ul_utilization',
                                                     data_source='ul_utilization',
                                                     getit='val'
                )

                avg_in_per = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='cambium_dl_util_kpi',
                                                     data_source='cam_dl_util_kpi',
                                                     getit='per'
                )

                avg_out_per = get_average_sector_util(device_object=sector.sector_configured_on,
                                                     service='cambium_ul_util_kpi',
                                                     data_source='cam_ul_util_kpi',
                                                     getit='per'
                )

                peak_in_val, peak_in_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='cambium_dl_utilization',
                                                    data_source='dl_utilization',
                                                    getit='val'
                )

                peak_out_val, peak_out_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='cambium_ul_utilization',
                                                    data_source='ul_utilization',
                                                    getit='val'
                )

                peak_in_per, peak_in_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='cambium_dl_util_kpi',
                                                    data_source='cam_dl_util_kpi',
                                                    getit='per'
                )

                peak_out_per, peak_out_timestamp = get_peak_sector_util(device_object=sector.sector_configured_on,
                                                    service='cambium_ul_util_kpi',
                                                    data_source='cam_ul_util_kpi',
                                                    getit='per'
                )
            if scs:
                # update the scs
                # scs.sector = sector
                # scs.sector_sector_id = sector.sector_id
                # values taht would be updated per 5 minutes
                scs.sector_capacity = float(sector_capacity) if sector_capacity else 0
                scs.current_in_per = float(current_in_per) if current_in_per else 0
                scs.current_in_val = float(current_in_val) if current_in_val else 0
                scs.sys_timestamp = float(sys_timestamp) if sys_timestamp else 0
                scs.organization = sector.organization if sector.organization else 1
                scs.severity = severity if severity else 'unknown'
                scs.age = float(age) if age else 0
                if calc_util_last_day():  # values that would be updated once 24 hours
                    scs.avg_in_per = float(avg_in_per) if avg_in_per else 0
                    scs.avg_in_val = float(avg_in_val) if avg_in_val else 0
                    scs.peak_in_per = float(peak_in_per) if peak_in_per else 0
                    scs.peak_in_val = float(peak_in_val) if peak_in_val else 0
                    scs.peak_in_timestamp = float(peak_in_timestamp) if peak_in_timestamp else 0
                    scs.current_out_per = float(current_out_per) if current_out_per else 0
                    scs.current_out_val = float(current_out_val) if current_in_val else 0
                    scs.avg_out_per = float(avg_out_per) if avg_out_per else 0
                    scs.avg_out_val = float(avg_out_val) if avg_out_val else 0
                    scs.peak_out_per = float(peak_out_per) if peak_out_per else 0
                    scs.peak_out_val = float(peak_out_val) if peak_out_val else 0
                    scs.peak_out_timestamp = float(peak_out_timestamp) if peak_out_timestamp else 0

                # scs.save()
                bulk_update_scs.append(scs)

            else:
                bulk_create_scs.append(
                    SectorCapacityStatus
                    (
                        sector=sector,
                        sector_sector_id=sector.sector_id,
                        sector_capacity=float(sector_capacity) if sector_capacity else 0,

                        current_in_per=float(current_in_per) if current_in_per else 0,
                        current_in_val=float(current_in_val) if current_in_val else 0,

                        avg_in_per=float(avg_in_per) if avg_in_per else 0,
                        avg_in_val=float(avg_in_val) if avg_in_val else 0,
                        peak_in_per=float(peak_in_per) if peak_in_per else 0,
                        peak_in_val=float(peak_in_val) if peak_in_val else 0,
                        peak_in_timestamp=float(peak_in_timestamp) if peak_in_timestamp else 0,

                        current_out_per=float(current_out_per) if current_out_per else 0,
                        current_out_val=float(current_out_val) if current_out_val else 0,

                        avg_out_per=float(avg_out_per) if avg_out_per else 0,
                        avg_out_val=float(avg_out_val) if avg_out_val else 0,
                        peak_out_per=float(peak_out_per) if peak_out_per else 0,
                        peak_out_val=float(peak_out_val) if peak_out_val else 0,
                        peak_out_timestamp=float(peak_out_timestamp) if peak_out_timestamp else 0,

                        sys_timestamp=float(sys_timestamp) if sys_timestamp else 0,
                        organization=sector.organization if sector.organization else 1,
                        severity=severity if severity else 'unknown',
                        age=float(age) if age else 0
                    )
                )

        else:
            return False

    g_jobs = list()

    if len(bulk_create_scs):
        g_jobs.append(bulk_update_create.s(bulk_create_scs, action='create', model=SectorCapacityStatus))

    if len(bulk_update_scs):
        g_jobs.append(bulk_update_create.s(bulk_update_scs, action='update', model=SectorCapacityStatus))

    if not len(g_jobs):
        return False

    job = group(g_jobs)
    ret = False
    result = job.apply_async()  # start the jobs
    # for r in result.get():
    #     ret |= r
    return True