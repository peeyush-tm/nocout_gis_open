from celery import task, group

from django.db.models import Count, Max, Avg #F, Max, Min, Q, Sum, Avg

#task for updating the sector capacity per 5 minutes
#need to run for PMP, WiMAX technology

from capacity_management.models import SectorCapacityStatus, BackhaulCapacityStatus
from inventory.models import get_default_org, Sector, Backhaul, BaseStation
from device.models import DeviceTechnology, Device, DevicePort, DeviceType
from service.models import ServiceDataSource
from inventory.utils.util import prepare_machines

from inventory.tasks import get_devices

from nocout.utils.util import fetch_raw_result

from performance.models import UtilizationStatus, InventoryStatus, ServiceStatus, Utilization, PerformanceService, Topology

from django.utils.dateformat import format
import datetime

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

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
    bh_devices = Backhaul.objects.filter(bh_configured_on__isnull=False).values_list('bh_configured_on', flat=True)

    # fetch all base stations
    base_stations = BaseStation.objects.filter(backhaul__bh_configured_on__isnull=False,
                                               bh_port_name__isnull=False).select_related(
        'backhaul__bh_configured_on',
        'backhaul__bh_configured_on__machine__name',
        'backhaul__bh_configured_on__device_type',
        'backhaul__bh_capacity')

    # get machines associated to all base station devices
    machines = set([bs.backhaul.bh_configured_on.machine.name for bs in base_stations])

    # get data sources
    ports = set([bs.bh_port_name for bs in base_stations])

    data_sources = set(DevicePort.objects.filter(alias__in=ports).values_list('name', flat=True))

    kpi_services = ['rici_dl_util_kpi', 'rici_ul_util_kpi', 'mrotek_dl_util_kpi', 'mrotek_ul_util_kpi',
                    'switch_dl_util_kpi', 'switch_ul_util_kpi']
    val_services = ['rici_dl_utilization', 'rici_ul_utilization', 'mrotek_dl_utilization', 'mrotek_ul_utilization',
                    'switch_dl_utilization', 'switch_ul_utilization']

    kpi = None
    val = None

    for machine in machines:
        if val:
            val |= ServiceStatus.objects.filter(
                    device_name__in=bh_devices,
                    service_name__in=val_services,
                    data_source__in=data_sources).using(alias=machine)
        else:
            val = ServiceStatus.objects.filter(
                    device_name__in=bh_devices,
                    service_name__in=val_services,
                    data_source__in=data_sources).using(alias=machine)

        if kpi:
            kpi |= UtilizationStatus.objects.filter(
                    device_name__in=bh_devices,
                    service_name__in=kpi_services,
                    data_source__in=data_sources).using(alias=machine)
        else:
            kpi = UtilizationStatus.objects.filter(
                    device_name__in=bh_devices,
                    service_name__in=kpi_services,
                    data_source__in=data_sources).using(alias=machine)

    return update_backhaul_status(base_stations, kpi, val)


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


    if technology.lower() == 'wimax':
        sectors = Sector.objects.filter(sector_configured_on__device_technology=technology_object.id,
                                        sector_configured_on__is_added_to_nms=1,
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
                                        sector_configured_on__is_added_to_nms=1,
                                        sector_id__isnull=False,
                                        sector_configured_on_port__isnull=True
                                        ).prefetch_related('sector_configured_on',
                                                           'base_station',
                                                           'base_station__city',
                                                           'base_station__state'
                                        ).annotate(Count('sector_id'))

        cbw = None

        sector_val = get_sector_val(machine_dict=machine_dict,
                                    service_name=tech_model_service['pmp']['val']['service_name'],
                                    data_source=tech_model_service['pmp']['val']['data_source'],
        )

        sector_kpi = get_sector_kpi(machine_dict=machine_dict,
                                    service_name=tech_model_service['pmp']['per']['service_name'],
                                    data_source=tech_model_service['pmp']['per']['data_source']
        )

        return update_sector_status(sectors=sectors, cbw=cbw, kpi=sector_kpi, val=sector_val, technology=technology)

    else:
        return False


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

    return s, a


def get_time():
    """

    :return: start time and end time
    """
    end_date = format(datetime.datetime.now(), 'U')
    start_date = format(datetime.datetime.now() + datetime.timedelta(days=-1), 'U')

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
        val_ul_service = ''
        val_dl_service = ''
        kpi_ul_service = ''
        kpi_dl_service = ''

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
            val_ul_service = 'switch_ul_utilization'
            val_dl_service = 'switch_dl_utilization'
            kpi_ul_service = 'switch_ul_util_kpi'
            kpi_dl_service = 'switch_dl_util_kpi'
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

                bhs.backhaul_capacity = float(backhaul_capacity) if backhaul_capacity else None
                bhs.current_in_per = float(current_in_per) if current_in_per else None
                bhs.current_in_val = float(current_in_val) if current_in_val else None
                bhs.avg_in_per = float(avg_in_per) if avg_in_per else None
                bhs.avg_in_val = float(avg_in_val) if avg_in_val else None
                bhs.peak_in_per = float(peak_in_per) if peak_in_per else None
                bhs.peak_in_val = float(peak_in_val) if peak_in_val else None
                bhs.peak_in_timestamp = float(peak_in_timestamp) if peak_in_timestamp else None
                bhs.current_out_per = float(current_out_per) if current_out_per else None
                bhs.current_out_val = float(current_out_val) if current_out_val else None
                bhs.avg_out_per = float(avg_out_per) if avg_out_per else None
                bhs.avg_out_val = float(avg_out_val) if avg_out_val else None
                bhs.peak_out_per = float(peak_out_per) if peak_out_per else None
                bhs.peak_out_val = float(peak_out_val) if peak_out_val else None
                bhs.peak_out_timestamp = float(peak_out_timestamp) if peak_out_timestamp else None
                bhs.sys_timestamp = float(sys_timestamp) if sys_timestamp else None
                bhs.organization = bs.backhaul.organization if bs.backhaul.organization else 1
                bhs.severity = severity if severity else 'unknown'
                bhs.age = float(age) if age else None
                bulk_update_bhs.append(bhs)

            else:

                bulk_create_bhs.append(
                    BackhaulCapacityStatus
                    (
                        backhaul=bs.backhaul,
                        basestation=bs,
                        bh_port_name=bs.bh_port_name,

                        backhaul_capacity=float(backhaul_capacity) if backhaul_capacity else None,
                        current_in_per=float(current_in_per) if current_in_per else None,
                        current_in_val=float(current_in_val) if current_in_val else None,
                        avg_in_per=float(avg_in_per) if avg_in_per else None,
                        avg_in_val=float(avg_in_val) if avg_in_val else None,
                        peak_in_per=float(peak_in_per) if peak_in_per else None,
                        peak_in_val=float(peak_in_val) if peak_in_val else None,
                        peak_in_timestamp=float(peak_in_timestamp) if peak_in_timestamp else None,
                        current_out_per=float(current_out_per) if current_out_per else None,
                        current_out_val=float(current_out_val) if current_out_val else None,
                        avg_out_per=float(avg_out_per) if avg_out_per else None,
                        avg_out_val=float(avg_out_val) if avg_out_val else None,
                        peak_out_per=float(peak_out_per) if peak_out_per else None,
                        peak_out_val=float(peak_out_val) if peak_out_val else None,
                        peak_out_timestamp=float(peak_out_timestamp) if peak_out_timestamp else None,
                        sys_timestamp=float(sys_timestamp) if sys_timestamp else None,
                        organization=bs.backhaul.organization if bs.backhaul.organization else 1,
                        severity=severity if severity else 'unknown',
                        age=float(age) if age else None
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

    result = job.apply_async()
    ret = False

    for r in result.get():
        ret |= r

    return ret


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
                    logger.exception(sector.sector_id)
                    logger.exception("No Fucking CBW. Not Fucking Possible")
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
                    logger.exception(sector.sector_id)
                    logger.exception("No Fucking CBW. Not Fucking Possible")
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
                logger.exception(sector.sector_id)
                logger.exception("No Fucking Port. Not Fucking Possible")
                continue

            if scs:
                #update the scs
                # scs.sector = sector
                # scs.sector_sector_id = sector.sector_id
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
                # scs.save()
                bulk_update_scs.append(scs)

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
            scs = None
            try:
                scs = SectorCapacityStatus.objects.get(
                    sector=sector,
                    sector_sector_id=sector.sector_id
                )
            except Exception as e:
                logger.exception(e)

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
                #update the scs
                # scs.sector = sector
                # scs.sector_sector_id = sector.sector_id
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
                # scs.save()
                bulk_update_scs.append(scs)

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

    result = job.apply_async()
    ret = False

    for r in result.get():
        ret |= r

    return ret


@task()
def bulk_update(bulky, action='update', entity='sector'):
    """

    :param bulky: bulk object list
    :param action: update or save
    :return: True
    """
    logger.debug(bulky)
    if bulky and len(bulky):
        if action == 'update':
            for update_this in bulky:
                try:
                    update_this.save()
                except Exception as e:
                    logger.exception(e)
            return True

        elif action == 'create':
            if entity == 'backhaul':
                BackhaulCapacityStatus.objects.bulk_create(bulky)
            else:
                SectorCapacityStatus.objects.bulk_create(bulky)
            return True

    return False


@task()
def bulk_create(bulky, action='create', entity='sector'):
    """

    :param bulky: bulk object list
    :param action: update or save
    :return: True
    """
    logger.debug(bulky)
    if bulky and len(bulky):
        if action == 'update':
            for update_this in bulky:
                try:
                    update_this.save()
                except Exception as e:
                    logger.exception(e)
            return True

        elif action == 'create':
            if entity == 'backhaul':
                BackhaulCapacityStatus.objects.bulk_create(bulky)
            else:
                SectorCapacityStatus.objects.bulk_create(bulky)
            return True

    return False

#TODO: make this common
@task()
def bulk_update_create(bulky, action='update', model=None):
    """

    :param bulky: bulk object list
    :param action: create or update?
    :param model: model object
    :return:
    """
    logger.debug(bulky)
    if bulky and len(bulky):
        if action == 'update':
            for update_this in bulky:
                try:
                    update_this.save()
                except Exception as e:
                    logger.exception(e)
            return True

        elif action == 'create':
            if model:
                model.objects.bulk_create(bulky)
            return True

    return False