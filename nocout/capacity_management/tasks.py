from celery import task, group

from django.db.models import Count, Max, Min, Avg
from django.db.models import Q
import json

#task for updating the sector capacity per 5 minutes
#need to run for PMP, WiMAX technology

from capacity_management.models import SectorCapacityStatus, BackhaulCapacityStatus
from inventory.models import get_default_org, Sector, Backhaul, BaseStation
from device.models import DeviceTechnology, Device, DevicePort, DeviceType
from service.models import ServiceDataSource

# Import inventory utils gateway class
from inventory.utils.util import InventoryUtilsGateway

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway, time_delta_calculator

from inventory.tasks import get_devices, bulk_update_create

from performance.models import UtilizationStatus, InventoryStatus, ServiceStatus, Utilization, PerformanceService, Topology

from django.utils.dateformat import format
import datetime

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from nocout.settings import CAPACITY_SPECIFIC_TIME

# to be moved to settings.py

CAPACITY_SETTINGS = {
    'wimax': {
        3: {
            'ul': 2,
            'dl': 4,
        },
        6: {
            'ul': 4,
            'dl': 8,
        }
    },
    'pmp': {
        7: {
            'ul': 2.24,
            'dl': 4.76
        }
    }
}

CAPACTIY_STATUS_MODELS = {
    'cbw': InventoryStatus,
    'val': ServiceStatus,
    'per': UtilizationStatus,
    'kpi': UtilizationStatus
}


CAPACTIY_MODELS = {
    'cbw': InventoryStatus,
    'val': PerformanceService,
    'per': Utilization,
    'kpi': Utilization
}


CAPACTIY_TABLES = {
    'cbw': 'performance_inventorystatus',
    'val': 'performance_performanceservice',
    'per': 'performance_utilization',
    'kpi': 'performance_utilization'
}

tech_model_service = {
    'wimax': {
        'cbw': {
            'model': 'performance_inventorystatus',
            'service_name': ['wimax_pmp_bw_invent'],
            'data_source': ['pmp2_bw', 'pmp1_bw'],
            'values': ['current_value', 'age', 'severity', 'sys_timestamp'],
            'values_list': ['current_value']
        },
        'val': {
            'model': 'performance_servicestatus',
            'service_name': [
                'wimax_pmp1_ul_util_bgp', 'wimax_pmp2_ul_util_bgp',
                'wimax_pmp1_dl_util_bgp', 'wimax_pmp2_dl_util_bgp'
            ],
            'data_source': [
                'pmp1_ul_util', 'pmp2_ul_util',
                'pmp1_dl_util', 'pmp2_dl_util'
            ],
            'values': ['current_value', 'age', 'severity', 'sys_timestamp'],
            'values_list': ['current_value']

        },
        'per': {
            'model': 'performance_utilizationstatus',
            'service_name': [
                'wimax_pmp1_ul_util_kpi', 'wimax_pmp2_ul_util_kpi',
                'wimax_pmp1_dl_util_kpi', 'wimax_pmp2_dl_util_kpi'
            ],
            'data_source': [
                'pmp1_ul_util_kpi', 'pmp2_ul_util_kpi',
                'pmp1_dl_util_kpi', 'pmp2_dl_util_kpi'
            ],
            'values': ['current_value', 'age', 'severity', 'sys_timestamp'],
            'values_list': None
        }
    },
    'pmp': {
        'cbw': {
            'model': None,
            'service_name': None,
            'data_source': None,
            'values': None
        },
        'val': {
            'model': 'performance_servicestatus',
            'service_name': [
                'cambium_ul_utilization', 'cambium_dl_utilization', 
                'rad5k_bs_ul_utilization', 'rad5k_bs_dl_utilization',
                'radwin5k_ss_ul_dyn_tl', 'radwin5k_ss_dl_dyn_tl'
            ],
            'data_source': [
                'ul_utilization', 'dl_utilization',
                'rad5k_ss_ul_dyn_tl', 'rad5k_ss_dl_dyn_tl'
            ],
            'values': ['current_value', 'age', 'severity', 'sys_timestamp'],
            'values_list': ['current_value']

        },
        'per': {
            'model': 'performance_utilizationstatus',
            'service_name': [
                'cambium_ul_util_kpi', 'cambium_dl_util_kpi',
                'radwin5k_ul_util_kpi', 'radwin5k_dl_util_kpi'
            ],
            'data_source': [
                'cam_ul_util_kpi', 'cam_dl_util_kpi',
                'rad5k_ul_util_kpi', 'rad5k_dl_util_kpi'
            ],
            'values': ['current_value', 'age', 'severity', 'sys_timestamp'],
            'values_list': None
        }
    },
}


backhaul_tech_model_services = {
    'juniper': {
        'device_type': 12
    },
    'cisco': {
        'device_type': 18
    },
    'mrotek': {
        'device_type': 13
    },
    'rici': {
        'device_type': 14
    },
    'huawei': {
        'device_type': 19
    },
    12: {
        'val': {
            'model': None,
            'dl': {
                'service_name': 'juniper_switch_dl_utilization',
                'data_source': None
            },
            'ul': {
                'service_name': 'juniper_switch_ul_utilization',
                'data_source': None
            },
        },
        'kpi': {
            'model': None,
            'dl': {
                'service_name': 'juniper_switch_dl_util_kpi',
                'data_source': None
            },
            'ul': {
                'service_name': 'juniper_switch_ul_util_kpi',
                'data_source': None
            },
        },
    },
    13: {
        'val': {
            'model': None,
            'dl': {
                'service_name': 'mrotek_dl_utilization',
                'data_source': None
            },
            'ul': {
                'service_name': 'mrotek_ul_utilization',
                'data_source': None
            },
        },
        'kpi': {
            'model': None,
            'dl': {
                'service_name': 'mrotek_dl_util_kpi',
                'data_source': None
            },
            'ul': {
                'service_name': 'mrotek_ul_util_kpi',
                'data_source': None
            },
        },
    },
    14: {
        'val': {
            'model': None,
            'dl': {
                'service_name': 'rici_dl_utilization',
                'data_source': None
            },
            'ul': {
                'service_name': 'rici_ul_utilization',
                'data_source': None
            },
        },
        'kpi': {
            'model': None,
            'dl': {
                'service_name': 'rici_dl_util_kpi',
                'data_source': None
            },
            'ul': {
                'service_name': 'rici_ul_util_kpi',
                'data_source': None
            },
        },
    },
    18: {
        'val': {
            'model': None,
            'dl': {
                'service_name': 'cisco_switch_dl_utilization',
                'data_source': None
            },
            'ul': {
                'service_name': 'cisco_switch_ul_utilization',
                'data_source': None
            },
        },
        'kpi': {
            'model': None,
            'dl': {
                'service_name': 'cisco_switch_dl_util_kpi',
                'data_source': None
            },
            'ul': {
                'service_name': 'cisco_switch_ul_util_kpi',
                'data_source': None
            },
        },
    },
    19: {
        'val': {
            'model': None,
            'dl': {
                'service_name': 'huawei_switch_dl_utilization',
                'data_source': None
            },
            'ul': {
                'service_name': 'huawei_switch_ul_utilization',
                'data_source': None
            },
        },
        'kpi': {
            'model': None,
            'dl': {
                'service_name': 'huawei_switch_dl_util_kpi',
                'data_source': None
            },
            'ul': {
                'service_name': 'huawei_switch_ul_util_kpi',
                'data_source': None
            },
        },
    }
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
        backhaul__bh_configured_on__is_added_to_nms__gt=0,
        bh_capacity__isnull=False
    ).select_related(
        'backhaul',
        'backhaul__bh_configured_on',
        'backhaul__bh_configured_on__machine'
    )

    bh_devices = Backhaul.objects.select_related(
        'bh_configured_on',
        'bh_configured_on__machine',
        'bh_configured_on__device_name'
    ).filter(
        id__in=base_stations.values_list('backhaul__id', flat=True),
        bh_configured_on__isnull=False,
        bh_configured_on__is_added_to_nms__gt=0
    )

    # get machines associated to all base station devices
    machines = set([bs.backhaul.bh_configured_on.machine.name for bs in base_stations])

    # get data sources
    tmp_ports = set([bs.bh_port_name for bs in base_stations])

    ports = list()

    for port in tmp_ports:
        if ',' in port:
            for pt in port.split(','):
                ports.append(pt.strip())
        else:
            ports.append(port)

    device_ports = list(DevicePort.objects.filter(alias__in=ports).values_list('name', flat=True))
    kpi_ds = list()
    
    # Add KPI DS to port list
    for port in device_ports:
        if port and str(port) + '_kpi' not in kpi_ds:
            kpi_ds.append(str(port) + '_kpi')

    device_ports += kpi_ds

    data_sources = set(list(ServiceDataSource.objects.filter(name__in=device_ports).values_list('name', flat=True)))

    kpi_services = ['rici_dl_util_kpi', 'rici_ul_util_kpi', 'mrotek_dl_util_kpi', 'mrotek_ul_util_kpi',
                    'cisco_switch_dl_util_kpi', 'cisco_switch_ul_util_kpi', 'juniper_switch_dl_util_kpi',
                    'juniper_switch_ul_util_kpi', 'huawei_switch_dl_util_kpi', 'huawei_switch_ul_util_kpi']

    val_services = ['rici_dl_utilization', 'rici_ul_utilization', 'mrotek_dl_utilization', 'mrotek_ul_utilization',
                    'cisco_switch_dl_utilization', 'cisco_switch_ul_utilization', 'juniper_switch_dl_utilization',
                    'juniper_switch_ul_utilization', 'huawei_switch_dl_utilization', 'huawei_switch_ul_utilization']

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
        ).order_by('-sys_timestamp').using(alias=machine)

        kpi = UtilizationStatus.objects.filter(
            device_name__in=machine_bh_devices,
            service_name__in=kpi_services,
            data_source__in=data_sources
        ).order_by('-sys_timestamp').using(alias=machine)

        # pass only base stations connected on a machine
        avg_max_val = None
        avg_max_per = None

        if calc_util_last_day():
            avg_max_val = get_avg_max_sector_util(
                devices=machine_bh_devices,
                services=val_services,
                data_sources=data_sources,
                machine=machine,
                getit='val'
            )

            avg_max_per = get_avg_max_sector_util(
                devices=machine_bh_devices,
                services=kpi_services,
                data_sources=data_sources,
                machine=machine,
                getit='per'
            )

        # Commented because some entries are not appearing in Backhaul status due to no data in polled info
        # if kpi.exists() and val.exists(): 
        bs = base_stations.filter(backhaul__bh_configured_on__machine__name=machine)
        g_jobs.append(
            update_backhaul_status.s(
                basestations=bs,
                kpi=kpi,
                val=val,
                avg_max_per=avg_max_per,
                avg_max_val=avg_max_val
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
    technology_low = technology.strip().lower()
    rad5k_network_devices = list()
    if technology_low == 'pmp':
        network_devices = list()
        cambium_network_devices = list(get_devices(technology))
        rad5k_network_devices = list(get_devices(technology=technology, is_rad5=True))
        network_devices = cambium_network_devices + rad5k_network_devices
    else:
        network_devices = get_devices(technology)
    device_list = []

    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    for device in network_devices:
        device_list.append({
            'id': device['id'],
            'device_name': device['device_name'],
            'device_machine': device['machine__name']
        })

    machine_dict = {}

    machine_dict = inventory_utils.prepare_machines(device_list)
    rad5k_device_list = list()
    rad5k_machine_dict = {}
    if technology_low == 'pmp':
        for device in rad5k_network_devices:
            rad5k_device_list.append({
                'id': device['id'],
                'device_name': device['device_name'],
                'device_machine': device['machine__name']
            })

        rad5k_machine_dict = inventory_utils.prepare_machines(rad5k_device_list)
    #need to gather from various sources
    #will do a raw query

    g_jobs = list()

    for machine in machine_dict:
        if technology_low == 'wimax':
            sectors = Sector.objects.filter(
                sector_configured_on__device_technology=technology_object.id,
                sector_configured_on__is_added_to_nms__gt=0,
                sector_configured_on__machine__name=machine,
                sector_id__isnull=False,
                sector_configured_on_port__isnull=False
            ).select_related(
                'sector_configured_on',
                'sector_configured_on_port',
                'base_station',
                'base_station__city',
                'base_station__state'
            ).annotate(Count('sector_id'))

        elif technology_low == 'pmp':
            sectors = Sector.objects.filter(
                sector_configured_on__device_technology=technology_object.id,
                sector_configured_on__is_added_to_nms__gt=0,
                sector_configured_on__machine__name=machine,
                sector_id__isnull=False,
                sector_configured_on_port__isnull=True
            ).select_related(
                'sector_configured_on',
                'base_station',
                'base_station__city',
                'base_station__state'
            ).annotate(Count('sector_id'))
        else:
            logger.error('No Technology from WiMAX and PMP')
            return False

        if technology_low == 'pmp':
            cbw = None
        elif technology_low == 'wimax':
            cbw = get_sectors_cbw_val_kpi(
                devices=machine_dict[machine],
                service_name=tech_model_service[technology_low]['cbw']['service_name'],
                data_source=tech_model_service[technology_low]['cbw']['data_source'],
                machine=machine,
                getit='cbw'
            )

        else:
            logger.error('No Technology from WiMAX and PMP')
            return False

        sector_val = None

        # values for current utilization of rad5 devices
        sector_val_rad5 = None
        if technology_low == 'pmp' and rad5k_machine_dict.get(machine):
            sector_val_rad5 = get_sectors_cbw_val_kpi(
                devices=rad5k_machine_dict[machine],
                service_name=tech_model_service[technology_low]['val']['service_name'],
                data_source=tech_model_service[technology_low]['val']['data_source'],
                machine=machine,
                getit='val'
            )

        # values for current Percentage KPIs
        sector_kpi = get_sectors_cbw_val_kpi(
            devices=machine_dict[machine],
            service_name=tech_model_service[technology_low]['per']['service_name'],
            data_source=tech_model_service[technology_low]['per']['data_source'],
            machine=machine,
            getit='per'
        )

        avg_max_val = None
        avg_max_per = None
        util_duration = None
        if calc_util_last_day():

            if technology_low == 'pmp' and rad5k_machine_dict.get(machine):
                util_duration = get_duration_sector_util(
                    devices=rad5k_machine_dict[machine],
                    services=tech_model_service[technology_low]['per']['service_name'],
                    data_sources=tech_model_service[technology_low]['per']['data_source'],
                    machine=machine,
                    getit='per'
                )

            avg_max_per = get_avg_max_sector_util(
                devices=machine_dict[machine],
                services=tech_model_service[technology_low]['per']['service_name'],
                data_sources=tech_model_service[technology_low]['per']['data_source'],
                machine=machine,
                getit='per'
            )

        g_jobs.append(
            update_sector_status.s(
                sectors=sectors,
                cbw=cbw,
                kpi=sector_kpi,
                val=sector_val,
                technology=technology,
                avg_max_per=avg_max_per,
                avg_max_val=avg_max_val,
                util_duration=util_duration,
                rad5_val=sector_val_rad5,
            )
        )

    ret = False
    if len(g_jobs):
        job = group(g_jobs)
        result = job.apply_async()
        # for r in result.get():
        #     ret |= r
        return True

    return ret

def get_higher_severity(severity_dict):
    """

    :param severity_dict:
    :return:
    """
    s, a = None, None

    if 'critical' in severity_dict:
        return 'critical', severity_dict['critical']
    elif 'warning' in severity_dict:
        return 'warning', severity_dict['warning']
    elif 'unknown' in severity_dict:
        return 'unknown', severity_dict['unknown']
    elif 'ok' in severity_dict:
        return 'ok', severity_dict['ok']
    else:
        pass

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

def get_sectors_cbw_val_kpi(devices, service_name, data_source, machine, getit):
    """

    :param devices:
    :param service_name:
    :param data_source:
    :param machine:
    :param type:
    :return:
    """
    try:
        performance = CAPACTIY_STATUS_MODELS[getit].objects.order_by(

        ).filter(
            device_name__in=devices,
            service_name__in=service_name,
            data_source__in=data_source
        ).using(alias=machine)

        return performance
    except:
        return None

def get_avg_max_sector_util(devices, services, data_sources, machine, getit):
    """

    :param devices: device list for the object
    :param services: service name for the object
    :param data_sources: data source for the object
    :param machine: machine name for the devices
    :param getit: val or per ( as in value or percentage)
    :return:
    """
    # Create instance of 'NocoutUtilsGateway' class
    nocout_utils = NocoutUtilsGateway()

    devices = nocout_utils.check_item_is_list(items=devices)
    services = nocout_utils.check_item_is_list(items=services)
    data_sources = nocout_utils.check_item_is_list(items=data_sources)

    start_date, end_date = get_time()

    try:
        in_string = lambda x: "'" + str(x) + "'"

        # cast as DECIMAL
        # MAX(CAST(`current_value` AS DECIMAL(3,6)) AS `max_val`,
        # AVG(CAST(`current_value` AS DECIMAL(3,6)) AS `avg_val`

        query = """
        SELECT
            `device_name`,
            `service_name`,
            `data_source`,
            MAX(`current_value` * 1) AS `max_val`,
            AVG(`current_value` * 1) AS `avg_val`
        FROM {0}
        WHERE
            `sys_timestamp` >= {4}
            AND
            `sys_timestamp` <= {5}
            AND
            `device_name`  IN ({1})
            AND
            `service_name` IN ({2})
            AND
            `data_source`  IN ({3})
        GROUP BY
            `device_name`,
            `service_name`,
            `data_source`
        """.format(
            CAPACTIY_TABLES[getit],
            (",".join(map(in_string, devices))),
            (",".join(map(in_string, services))),
            (",".join(map(in_string, data_sources))),
            start_date,
            end_date
        )

        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()

        perf = nocout_utils.fetch_raw_result(query=query, machine=machine)

    except Exception as e:
        logger.error(e)
        return None

    return perf

def get_duration_sector_util(devices, services, data_sources, machine, getit):
    """

    :param devices: device list for the object
    :param services: service name for the object
    :param data_sources: data source for the object
    :param machine: machine name for the devices
    :param getit: val or per ( as in value or percentage)
    :return:
    """
    # Create instance of 'NocoutUtilsGateway' class
    nocout_utils = NocoutUtilsGateway()

    devices = nocout_utils.check_item_is_list(items=devices)
    services = nocout_utils.check_item_is_list(items=services)
    data_sources = nocout_utils.check_item_is_list(items=data_sources)

    start_date, end_date = get_time()

    try:
        in_string = lambda x: "'" + str(x) + "'"

        # cast as DECIMAL
        # MAX(CAST(`current_value` AS DECIMAL(3,6)) AS `max_val`,
        # AVG(CAST(`current_value` AS DECIMAL(3,6)) AS `avg_val`

        query = """
        SELECT
            `device_name`,
            `service_name`,
            `data_source`,
            COUNT(`id`) AS `duration`,
        FROM {0}
        WHERE
            `sys_timestamp` >= {4}
            AND
            `sys_timestamp` <= {5}
            AND
            `severity` = 'critical'
            AND
            `device_name`  IN ({1})
            AND
            `service_name` IN ({2})
            AND
            `data_source`  IN ({3})
        GROUP BY
            `device_name`,
            `service_name`,
            `data_source`
        """.format(
            CAPACTIY_TABLES[getit],
            (",".join(map(in_string, devices))),
            (",".join(map(in_string, services))),
            (",".join(map(in_string, data_sources))),
            start_date,
            end_date
        )

        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()
        perf = nocout_utils.fetch_raw_result(query=query, machine=machine)
    except Exception as e:
        logger.error(e)
        return None

    return perf

def get_peak_sectors_util(device, service, data_source, machine, max_value, getit):
    """

    :param device:
    :param service:
    :param data_source:
    :param machine:
    :param max_value:
    :param getit:
    :return:
    """
    start_date, end_date = get_time()

    if '_kpi' not in data_source:
        data_source += '_kpi'

    if not max_value:
        return 0, 0

    where_clause = ' current_value >= {0} '.format(max_value)

    try:
        perf = CAPACTIY_MODELS[getit].objects.order_by(

        ).extra(
            where=[where_clause]
        ).filter(
            sys_timestamp__gte=start_date,
            sys_timestamp__lte=end_date,
            device_name=device,
            service_name=service,
            data_source=data_source,
            # current_value=max_value
        ).using(alias=machine).values('current_value', 'sys_timestamp')
    except Exception as e:
        logger.error(e)
        return 0, 0

    if perf and perf.exists():
        return float(perf[0]['current_value']), float(perf[0]['sys_timestamp'])
    else:
        return 0, 0

def get_average_sector_util(device_object, service, data_source, getit='val'):
    """

    :param device_object:
    :param service:
    :param data_source:
    :param getit:
    :return:
    """
    start_date, end_date = get_time()
    if getit == 'val':
        perf = PerformanceService.objects.order_by(

        ).filter(
            device_name=device_object.device_name,
            service_name=service,
            data_source=data_source,
            sys_timestamp__gte=start_date,
            sys_timestamp__lte=end_date
        ).using(alias=device_object.machine.name).aggregate(Avg('current_value'))

    elif getit == 'per':
        perf = Utilization.objects.order_by(

        ).filter(
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

    :param device_object:
    :param service:
    :param data_source:
    :param getit:
    :return:
    """
    start_date, end_date = get_time()
    if getit == 'val':
        max_value = PerformanceService.objects.order_by(

        ).filter(
            device_name=device_object.device_name,
            service_name=service,
            data_source=data_source,
            sys_timestamp__gte=start_date,
            sys_timestamp__lte=end_date
        ).using(alias=device_object.machine.name).aggregate(Max('current_value'))['current_value__max']

        perf = PerformanceService.objects.order_by(

        ).filter(
                device_name=device_object.device_name,
                service_name=service,
                data_source=data_source,
                sys_timestamp__gte=start_date,
                sys_timestamp__lte=end_date,
                current_value=max_value
            ).using(alias=device_object.machine.name).values('current_value', 'sys_timestamp')

    elif getit == 'per':
        max_value = Utilization.objects.order_by(

        ).filter(
            device_name=device_object.device_name,
            service_name=service,
            data_source=data_source,
            sys_timestamp__gte=start_date,
            sys_timestamp__lte=end_date
        ).using(alias=device_object.machine.name).aggregate(Max('current_value'))['current_value__max']

        perf = Utilization.objects.order_by(

        ).filter(
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

@task()
def update_backhaul_status(basestations, kpi, val, avg_max_val, avg_max_per):
    """

    :param basestations:
    :param kpi:
    :param val:
    :param avg_max_val:
    :param avg_max_per:
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

    if not kpi.exists() and not val.exists():
        return False

    # Create instance of 'NocoutUtilsGateway' class
    nocout_utils = NocoutUtilsGateway()

    indexed_kpi = nocout_utils.indexed_query_set(
        query_set=kpi,
        indexes=['device_name', 'service_name', 'data_source'],
        values=['device_name', 'service_name', 'data_source', 'current_value', 'age', 'severity', 'sys_timestamp'],
    )

    indexed_val = nocout_utils.indexed_query_set(
        query_set=val,
        indexes=['device_name', 'service_name', 'data_source'],
        values=['device_name', 'service_name', 'data_source', 'current_value', 'age', 'severity', 'sys_timestamp'],
    )

    indexed_avg_max_val = dict()
    indexed_avg_max_per = dict()
    if avg_max_per and avg_max_val:
        indexed_avg_max_val = nocout_utils.indexed_query_set(
            query_set=avg_max_val,
            indexes=['device_name', 'service_name', 'data_source'],
            values=['device_name', 'service_name', 'data_source', 'max_val', 'avg_val'],
            is_raw=True
        )
        indexed_avg_max_per = nocout_utils.indexed_query_set(
            query_set=avg_max_per,
            indexes=['device_name', 'service_name', 'data_source'],
            values=['device_name', 'service_name', 'data_source', 'max_val', 'avg_val'],
            is_raw=True
        )
    count = 0
    logger.error("********************************** count - {}".format(basestations.count()))
    for bs in basestations:
        # logger.error("***************************** {}".format(count))
        count += 1
        # base station device
        bh_device = bs.backhaul.bh_configured_on

        # BH device port.
        device_port = bs.bh_port_name

        # BH device machine.
        device_machine = bh_device.machine.name

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
            val_ul_service = 'juniper_switch_ul_utilization'
            val_dl_service = 'juniper_switch_dl_utilization'
            kpi_ul_service = 'juniper_switch_ul_util_kpi'
            kpi_dl_service = 'juniper_switch_dl_util_kpi'
        # if device type is 'pine converter'
        elif bs_device_type == 13:
            val_ul_service = 'mrotek_ul_utilization'
            val_dl_service = 'mrotek_dl_utilization'
            kpi_ul_service = 'mrotek_ul_util_kpi'
            kpi_dl_service = 'mrotek_dl_util_kpi'
        # # if device type is 'rici converter'
        elif bs_device_type == 14:
            val_ul_service = 'rici_ul_utilization'
            val_dl_service = 'rici_dl_utilization'
            kpi_ul_service = 'rici_ul_util_kpi'
            kpi_dl_service = 'rici_dl_util_kpi'
        elif bs_device_type == 18:
            val_ul_service = 'cisco_switch_ul_utilization'
            val_dl_service = 'cisco_switch_dl_utilization'
            kpi_ul_service = 'cisco_switch_ul_util_kpi'
            kpi_dl_service = 'cisco_switch_dl_util_kpi'
        elif bs_device_type == 19:
            val_ul_service = 'huawei_switch_ul_utilization'
            val_dl_service = 'huawei_switch_dl_utilization'
            kpi_ul_service = 'huawei_switch_ul_util_kpi'
            kpi_dl_service = 'huawei_switch_dl_util_kpi'
        else:
            # proceed only if there is proper device type mapping
            continue

        # Ring Scenario: If device follows ring scenario then get
        # data source corressponding to the port having max value.
        data_source = None
        if ',' in device_port:
            try:
                data_sources = device_port.split(',')
                ds_dict = dict()
                dp_dict = dict()
                for ds in data_sources:
                    ds = ds.strip()
                    tmp_port = DevicePort.objects.get(alias=ds).name
                    data_source_name = ServiceDataSource.objects.get(name__iexact=tmp_port).name
                    ds_name = data_source_name.lower()
                    try:
                        util = ServiceStatus.objects.filter(
                            device_name=bh_device.device_name,
                            service_name=val_dl_service,
                            data_source__iexact=ds_name
                        ).using(device_machine)[0].current_value

                        if util not in ['', None]:
                            util = float(util)

                        ds_dict[util] = ds_name
                        dp_dict[ds_name] = tmp_port
                    except Exception, e:
                        data_source = data_source_name
                        device_port = tmp_port

                if ds_dict:
                    data_source = ds_dict[max(ds_dict.keys())]

                if dp_dict:
                    device_port = dp_dict[data_source]
            except Exception as e:
                logger.error('Utilization Error ----- ')
                logger.error(e)
                continue
        else:
            try:
                # we don't care about port, till it actually is mapped to a data source
                data_source = ServiceDataSource.objects.get(
                    name__in=DevicePort.objects.filter(alias=bs.bh_port_name).values_list('name', flat=True)
                ).name.lower()
            except Exception as e:
                logger.error('Back-hual Port {0} for {1} IP address'.format(bs.bh_port_name, bh_device.ip_address))
                # logger.error('Device Port : {0}'.format(DevicePort.objects.get(alias=bs.bh_port_name).name))
                pass
                # if we don't have a port mapping
                # do not query database
                continue

        if data_source:
            try:
                # in % values index
                in_per_index = (bs.backhaul.bh_configured_on.device_name,
                                backhaul_tech_model_services[bs_device_type]['kpi']['dl']['service_name'],
                                str(data_source) + '_kpi')

                # out % values index
                out_per_index = (bs.backhaul.bh_configured_on.device_name,
                                 backhaul_tech_model_services[bs_device_type]['kpi']['ul']['service_name'],
                                 str(data_source) + '_kpi')
            except Exception, e:
                # in % values index
                in_per_index = (bs.backhaul.bh_configured_on.device_name,
                                backhaul_tech_model_services[bs_device_type]['kpi']['dl']['service_name'],
                                data_source)

                # out % values index
                out_per_index = (bs.backhaul.bh_configured_on.device_name,
                                 backhaul_tech_model_services[bs_device_type]['kpi']['ul']['service_name'],
                                 data_source)

            # in % values index
            in_val_index = (bs.backhaul.bh_configured_on.device_name,
                            backhaul_tech_model_services[bs_device_type]['val']['dl']['service_name'],
                            data_source)

            # out % values index
            out_val_index = (bs.backhaul.bh_configured_on.device_name,
                             backhaul_tech_model_services[bs_device_type]['val']['ul']['service_name'],
                             data_source)

            # backhaul capacity
            if bs.bh_capacity:
                backhaul_capacity = bs.bh_capacity
            else:
                logger.exception('No Base-Station - Back-haul Capacity Not Possible')
                continue

            severity_s = dict()
            try:
                try:
                    # time of update
                    sys_timestamp = indexed_kpi[in_per_index][0]['sys_timestamp']
                    if time_delta_calculator(sys_timestamp, minutes=20):
                        # current in/out %
                        current_in_per = float(indexed_kpi[in_per_index][0]['current_value'])
                        # current in/out %
                        current_out_per = float(indexed_kpi[out_per_index][0]['current_value'])
                    else:
                        current_in_per = 'NA'
                        current_out_per = 'NA'
                except Exception, e:
                    current_in_per = 'NA'
                    current_out_per = 'NA'

                try:
                    val_sys_timestamp = indexed_val[in_val_index][0]['sys_timestamp']
                    if time_delta_calculator(val_sys_timestamp, minutes=20):
                        # current in/out values
                        current_in_val = float(indexed_val[in_val_index][0]['current_value'])
                        # current in/out values
                        current_out_val = float(indexed_val[out_val_index][0]['current_value'])
                    else:
                        current_in_val = 'NA'
                        current_out_val = 'NA'
                except Exception, e:
                    current_in_val = 'NA'
                    current_out_val = 'NA'

                try:
                    severity_s = {
                        indexed_kpi[in_per_index][0]['severity']: indexed_kpi[in_per_index][0]['age'],
                        indexed_kpi[out_per_index][0]['severity']: indexed_kpi[out_per_index][0]['age'],
                    }

                    severity, age = get_higher_severity(severity_s)
                except Exception, e:
                    severity = 'unknown'
                    age = 'NA'
            except Exception as e:
                pass
                current_in_per = 'NA'
                current_out_per = 'NA'
                current_in_val = 'NA'
                current_out_val = 'NA'
                severity = 'unknown'
                age = 'NA'
                sys_timestamp = 'NA'

            # now that we have severity and age all we need to do now is gather the average and peak values
            if calc_util_last_day():
                try:
                    # average percentage in/out
                    avg_in_per = float(indexed_avg_max_per[in_per_index][0]['avg_val'])
                    # peak percentage in/out
                    peak_in_per = float(indexed_avg_max_per[in_per_index][0]['max_val'])
                except Exception, e:
                    avg_in_per = None
                    peak_in_per = None
                    pass

                try:
                    # average percentage in/out
                    avg_out_per = float(indexed_avg_max_per[out_per_index][0]['avg_val'])
                    # peak percentage in/out
                    peak_out_per = float(indexed_avg_max_per[out_per_index][0]['max_val'])

                except Exception as e:
                    avg_out_per = None
                    peak_out_per = None
                    pass

                try:
                    # average percentage in/out
                    avg_in_val = float(indexed_avg_max_val[in_val_index][0]['avg_val'])
                    # peak percentage in/out
                    peak_in_val = float(indexed_avg_max_val[in_val_index][0]['max_val'])
                except Exception, e:
                    avg_in_val = 'NA'
                    peak_in_val = 'NA'
                    pass

                try:
                    # average percentage in/out
                    avg_out_val = float(indexed_avg_max_val[out_val_index][0]['avg_val'])
                    # peak percentage in/out
                    peak_out_val = float(indexed_avg_max_val[out_val_index][0]['max_val'])

                except Exception as e:
                    avg_out_val = 'NA'
                    peak_out_val = 'NA'
                    pass

                peak_in_per, peak_in_timestamp = get_peak_sectors_util(
                    device=bs.backhaul.bh_configured_on.device_name,
                    service=backhaul_tech_model_services[bs_device_type]['kpi']['dl']['service_name'],
                    data_source=data_source,
                    machine=bs.backhaul.bh_configured_on.machine.name,
                    max_value=peak_in_per,
                    getit='per'
                )

                peak_out_per, peak_out_timestamp = get_peak_sectors_util(
                    device=bs.backhaul.bh_configured_on.device_name,
                    service=backhaul_tech_model_services[bs_device_type]['kpi']['ul']['service_name'],
                    data_source=data_source,
                    machine=bs.backhaul.bh_configured_on.machine.name,
                    max_value=peak_out_per,
                    getit='per'
                )

            bhs = None
            bhs_count = None
            try:
                bhs = BackhaulCapacityStatus.objects.filter(
                    backhaul=bs.backhaul,
                    basestation=bs
                    # bh_port_name=bs.bh_port_name
                )
                bhs_count = bhs.count()

                temp_bhs = bhs[0]

                if bhs_count > 1:
                    deleted_bh = bhs.exclude(id=temp_bhs.id)
                    deleted_bh.delete()
                
                bhs = temp_bhs
            except Exception as e:
                pass

            if bhs_count < 1:
                try:
                    logger.exception("******************************* Creating - {}".format(bs.backhaul.bh_configured_on.ip_address))
                except Exception, e:
                    logger.error("******************************* Creating - {}".format(bhs_count))

                bulk_create_bhs.append(
                    BackhaulCapacityStatus(
                        backhaul=bs.backhaul,
                        basestation=bs,
                        bh_port_name=device_port.replace("_", "/") if device_port else '',
                        backhaul_capacity=round(float(backhaul_capacity), 2) if backhaul_capacity not in ['', 'NA', None] else 0,
                        current_in_per=round(float(current_in_per), 2) if current_in_per not in ['NA', '', None] else 'NA',
                        current_in_val=round(float(current_in_val), 2) if current_in_val not in ['NA', '', None] else 'NA',
                        avg_in_per=round(float(avg_in_per), 2) if avg_in_per not in ['NA', '', None] else 'NA',
                        avg_in_val=round(float(avg_in_val), 2) if avg_in_val not in ['NA', '', None] else 'NA',
                        peak_in_per=round(float(peak_in_per), 2) if peak_in_per not in ['NA', '', None] else 'NA',
                        peak_in_val=round(float(peak_in_val), 2) if peak_in_val not in ['NA', '', None] else 'NA',
                        peak_in_timestamp=float(peak_in_timestamp) if peak_in_timestamp not in ['NA', '', None] else 0,
                        current_out_per=round(float(current_out_per), 2) if current_out_per not in ['NA', '', None] else 'NA',
                        current_out_val=round(float(current_out_val), 2) if current_out_val not in ['NA', '', None] else 'NA',
                        avg_out_per=round(float(avg_out_per), 2) if avg_out_per not in ['NA', '', None] else 'NA',
                        avg_out_val=round(float(avg_out_val), 2) if avg_out_val not in ['NA', '', None] else 'NA',
                        peak_out_per=round(float(peak_out_per), 2) if peak_out_per not in ['NA', '', None] else 'NA',
                        peak_out_val=round(float(peak_out_val), 2) if peak_out_val not in ['NA', '', None] else 'NA',
                        peak_out_timestamp=float(peak_out_timestamp) if peak_out_timestamp not in ['NA', '', None] else 0,
                        sys_timestamp=float(sys_timestamp) if sys_timestamp not in ['NA', '', None] else 0,
                        organization=bs.backhaul.organization if bs.backhaul.organization else 1,
                        severity=severity if severity else 'unknown',
                        age=float(age) if age not in ['NA', '', None] else 0
                    )
                )
            else:
                try:
                    logger.error("******************************* Updating - {}".format(bs.backhaul.bh_configured_on.ip_address))
                except Exception, e:
                    logger.error("******************************* Updating - {}".format(bhs_count))

                # values that would be updated per 5 minutes
                bhs.backhaul_capacity = float(backhaul_capacity) if backhaul_capacity not in ['', 'NA', None] else 0
                bhs.bh_port_name = device_port.replace("_", "/") if device_port else ''
                bhs.sys_timestamp = float(sys_timestamp) if sys_timestamp not in ['', 'NA', None] else 0
                bhs.organization = bs.backhaul.organization if bs.backhaul.organization else 1
                bhs.severity = severity if severity else 'unknown'
                bhs.age = float(age) if age not in ['', 'NA', None] else 0

                bhs.current_in_per = round(float(current_in_per), 2) if current_in_per not in ['', 'NA', None] else current_in_per
                bhs.current_in_val = round(float(current_in_val), 2) if current_in_val not in ['', 'NA', None] else current_in_val

                bhs.current_out_per = round(float(current_out_per), 2) if current_out_per not in ['', 'NA', None] else current_out_per
                bhs.current_out_val = round(float(current_out_val), 2) if current_out_val not in ['', 'NA', None] else current_out_val

                if calc_util_last_day():  # values that would be updated once in a day
                    bhs.avg_in_per = round(float(avg_in_per), 2) if avg_in_per not in ['', 'NA', None] else 'NA'
                    bhs.avg_in_val = round(float(avg_in_val), 2) if avg_in_val not in ['', 'NA', None] else 'NA'
                    bhs.peak_in_per = round(float(peak_in_per), 2) if peak_in_per not in ['', 'NA', None] else 'NA'
                    bhs.peak_in_val = round(float(peak_in_val), 2) if peak_in_val not in ['', 'NA', None] else 'NA'

                    bhs.peak_in_timestamp = float(peak_in_timestamp) if peak_in_timestamp not in ['', 'NA', None] else 0

                    bhs.avg_out_per = round(float(avg_out_per), 2) if avg_out_per not in ['', 'NA', None] else 'NA'
                    bhs.avg_out_val = round(float(avg_out_val), 2) if avg_out_val not in ['', 'NA', None] else 'NA'
                    bhs.peak_out_per = round(float(peak_out_per), 2) if peak_out_per not in ['', 'NA', None] else 'NA'
                    bhs.peak_out_val = round(float(peak_out_val), 2) if peak_out_val not in ['', 'NA', None] else 'NA'

                    bhs.peak_out_timestamp = float(peak_out_timestamp) if peak_out_timestamp not in ['', 'NA', None] else 0

                bulk_update_bhs.append(bhs)

    g_jobs = list()

    if len(bulk_create_bhs):
        logger.exception("******************************* bulk_create_bhs Create Length - {}".format(len(bulk_create_bhs)))
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
def update_sector_status(sectors, cbw, kpi, val, technology, avg_max_val, avg_max_per, util_duration, rad5_val=None):
    """

    :param sectors: sectors query set
    :param cbw: cbw query set
    :param kpi: kpi query set
    :param val: values query set
    :param technology: technology ID
    :param avg_max_val: Values Query Set when it is required to calculate the average and max value
    :param avg_max_per: Values Query Set when it is required to calculate the average and max %
    :return:
    """
    bulk_update_scs = []
    bulk_create_scs = []

    sector_capacity = 0
    sector_capacity_in = 0
    sector_capacity_out = 0

    current_in_per = 0
    current_in_val = 0

    avg_in_per = 0
    avg_in_val = 0
    peak_in_per = 0
    peak_in_val = 0
    peak_in_timestamp = 0

    current_out_per = 0
    current_out_val = 0

    current_timeslot_ul = None
    current_timeslot_dl = None

    avg_out_per = 0
    avg_out_val = 0
    peak_out_per = 0
    peak_out_val = 0
    peak_out_timestamp = 0

    sys_timestamp = 0
    organization = get_default_org()
    severity = 'unknown'
    age = 0

    processed_sectors = {}

    indexed_cbw = dict()
    indexed_kpi = dict()
    indexed_val = dict()
    indexed_avg_max_val = dict()
    indexed_avg_max_per = dict()
    indexed_util_duration = dict()

    # Create instance of 'NocoutUtilsGateway' class
    nocout_utils = NocoutUtilsGateway()

    # force evaluation of query set
    if technology.lower() == 'wimax' and cbw.exists():
        indexed_cbw = nocout_utils.indexed_query_set(
            query_set=cbw,
            indexes=['device_name', 'service_name', 'data_source'],
            values=['device_name', 'service_name', 'data_source', 'current_value'],
        )

    if kpi.exists():  # and val.exists():
        indexed_kpi = nocout_utils.indexed_query_set(
            query_set=kpi,
            indexes=['device_name', 'service_name', 'data_source'],
            values=['device_name', 'service_name', 'data_source', 'current_value', 'age', 'severity', 'sys_timestamp'],
        )
    # else:
    #     return False

    indexed_rad5_val = {}
    if technology.lower() == 'pmp' and rad5_val.exists():
        indexed_rad5_val = nocout_utils.indexed_query_set(
            query_set=rad5_val,
            indexes=['device_name', 'service_name', 'data_source'],
            values=['device_name', 'service_name', 'data_source', 'current_value'],
        )

    if avg_max_per:
        indexed_avg_max_per = nocout_utils.indexed_query_set(
            query_set=avg_max_per,
            indexes=['device_name', 'service_name', 'data_source'],
            values=['device_name', 'service_name', 'data_source', 'max_val', 'avg_val'],
            is_raw=True
        )

    if util_duration:
        indexed_util_duration = nocout_utils.indexed_query_set(
            query_set=util_duration,
            indexes=['device_name', 'service_name', 'data_source'],
            values=['device_name', 'service_name', 'data_source', 'max_val', 'avg_val'],
            is_raw=True
        )

    rad5k_type_id = 0
    try:
        if technology.lower() == 'pmp':
            rad5k_type_id = DeviceType.objects.get(name__iexact='Radwin5KBS').id
    except Exception as e:
        pass

    for sector in sectors:
        # deduplication of the sector on the basis of sector ID
        if sector.sector_id in processed_sectors:
            continue
        else:
            processed_sectors[sector.sector_id] = sector.sector_id

        # start with single sector
        # get the sector --> device
        # stitch together values
        # take special care of PMP1 & PMP2 cases
        if technology.lower() == 'wimax':
            scs = None
            try:
                scs = SectorCapacityStatus.objects.get(
                    sector=sector,
                    sector_sector_id=sector.sector_id
                )
            except Exception as e:
                # logger.error("WiMAX : {0}".format(e.message))
                pass

            if 'pmp1' in sector.sector_configured_on_port.name.lower():

                # index for cbw value
                cbw_index = (sector.sector_configured_on.device_name,
                             'wimax_pmp_bw_invent',
                             'pmp1_bw')

                # in % values index
                in_per_index = (sector.sector_configured_on.device_name,
                                'wimax_pmp1_dl_util_kpi',
                                'pmp1_dl_util_kpi')

                # out % values index
                out_per_index = (sector.sector_configured_on.device_name,
                                 'wimax_pmp1_ul_util_kpi',
                                 'pmp1_ul_util_kpi')

                peak_dl_service_name = 'wimax_pmp1_dl_util_kpi'
                peak_dl_data_source = 'pmp1_dl_util_kpi'

                peak_ul_service_name = 'wimax_pmp1_ul_util_kpi'
                peak_ul_data_source = 'pmp1_ul_util_kpi'

            elif 'pmp2' in sector.sector_configured_on_port.name.lower():
                # index for cbw value
                cbw_index = (sector.sector_configured_on.device_name,
                             'wimax_pmp_bw_invent',
                             'pmp2_bw')

                # in % values index
                in_per_index = (sector.sector_configured_on.device_name,
                                'wimax_pmp2_dl_util_kpi',
                                'pmp2_dl_util_kpi')

                # out % values index
                out_per_index = (sector.sector_configured_on.device_name,
                                 'wimax_pmp2_ul_util_kpi',
                                 'pmp2_ul_util_kpi')

                peak_dl_service_name = 'wimax_pmp2_dl_util_kpi'
                peak_dl_data_source = 'pmp2_dl_util_kpi'

                peak_ul_service_name = 'wimax_pmp2_ul_util_kpi'
                peak_ul_data_source = 'pmp2_ul_util_kpi'

            else:
                # no port specified
                continue

            try:
                sector_capacity = indexed_cbw[cbw_index][0]['current_value']
            except Exception as e:
                # logger.error("we dont want to store any data till we get a CBW for : {0}".format(sector.sector_id))
                logger.error(e)
                continue

            try:
                sector_capacity_in = CAPACITY_SETTINGS['wimax'][int(float(sector_capacity))]['dl']
                sector_capacity_out = CAPACITY_SETTINGS['wimax'][int(float(sector_capacity))]['ul']
            except:
                continue

            try:
                # time of update
                sys_timestamp = indexed_kpi[in_per_index][0]['sys_timestamp']

                if time_delta_calculator(sys_timestamp, minutes=20):
                    # current in/out percentages
                    current_in_per = float(indexed_kpi[in_per_index][0]['current_value'])

                    # current in/out percentages
                    current_out_per = float(indexed_kpi[out_per_index][0]['current_value'])
                else:
                    current_in_per = 0
                    current_out_per = 0

                # severity for KPI services
                severity_s = {
                    indexed_kpi[in_per_index][0]['severity']: indexed_kpi[in_per_index][0]['age'],
                    indexed_kpi[out_per_index][0]['severity']: indexed_kpi[out_per_index][0]['age'],
                }

                severity, age = get_higher_severity(severity_s)

                # current in/out values
                current_in_val = current_in_per * sector_capacity_in / 100.00

                # current in/out values
                current_out_val = current_out_per * sector_capacity_out / 100.00

            except Exception as e:
                logger.error(e)
                continue  # we dont have any current values with us

            if calc_util_last_day():

                try:
                    # average percentage in/out
                    avg_in_per = float(indexed_avg_max_per[in_per_index][0]['avg_val'])
                    # peak percentage in/out
                    peak_in_per = float(indexed_avg_max_per[in_per_index][0]['max_val'])
                    # average percentage in/out
                    avg_out_per = float(indexed_avg_max_per[out_per_index][0]['avg_val'])
                    # peak percentage in/out
                    peak_out_per = float(indexed_avg_max_per[out_per_index][0]['max_val'])
                except Exception as e:
                    logger.error(e)
                    avg_in_per = 0
                    peak_in_per = None
                    avg_out_per = 0
                    peak_out_per = None

                peak_in_per, peak_in_timestamp = get_peak_sectors_util(
                    device=sector.sector_configured_on.device_name,
                    service=peak_dl_service_name,
                    data_source=peak_dl_data_source,
                    machine=sector.sector_configured_on.machine.name,
                    max_value=peak_in_per,
                    getit='per'
                )

                peak_out_per, peak_out_timestamp = get_peak_sectors_util(
                    device=sector.sector_configured_on.device_name,
                    service=peak_ul_service_name,
                    data_source=peak_ul_data_source,
                    machine=sector.sector_configured_on.machine.name,
                    max_value=peak_out_per,
                    getit='per'
                )

                try:
                    # average value in/out
                    avg_in_val = avg_in_per * sector_capacity_in / 100.00
                    # peak value in/out
                    peak_in_val = peak_in_per * sector_capacity_in / 100.00
                    # average value in/out
                    avg_out_val = avg_out_per * sector_capacity_out / 100.00
                    # peak value in/out
                    peak_out_val = peak_out_per * sector_capacity_out / 100.00

                except Exception as e:
                    logger.error(e)
                    avg_in_val = 0
                    peak_in_val = 0
                    avg_out_val = 0
                    peak_out_val = 0
            if scs:
                # update the scs
                # scs.sector = sector
                # scs.sector_sector_id = sector.sector_id
                scs.sector_capacity = float(sector_capacity) if sector_capacity else 0

                scs.sys_timestamp = float(sys_timestamp) if sys_timestamp else 0
                scs.organization = sector.organization if sector.organization else 1
                scs.severity = severity if severity else 'unknown'
                scs.age = float(age) if age else 0
                # new fileds for better representation of IN and OUT

                scs.sector_capacity_in = sector_capacity_in
                scs.sector_capacity_out = sector_capacity_out

                scs.current_in_per = round(float(current_in_per), 2) if current_in_per else 0
                scs.current_in_val = round(float(current_in_val), 2) if current_in_val else 0

                scs.current_out_per = round(float(current_out_per), 2) if current_out_per else 0
                scs.current_out_val = round(float(current_out_val), 2) if current_in_val else 0

                if calc_util_last_day():
                    scs.avg_in_per = round(float(avg_in_per), 2) if avg_in_per else 0
                    scs.avg_in_val = round(float(avg_in_val), 2) if avg_in_val else 0
                    scs.peak_in_per = round(float(peak_in_per), 2) if peak_in_per else 0
                    scs.peak_in_val = round(float(peak_in_val), 2) if peak_in_val else 0

                    scs.peak_in_timestamp = float(peak_in_timestamp) if peak_in_timestamp else 0

                    scs.avg_out_per = round(float(avg_out_per), 2) if avg_out_per else 0
                    scs.avg_out_val = round(float(avg_out_val), 2) if avg_out_val else 0
                    scs.peak_out_per = round(float(peak_out_per), 2) if peak_out_per else 0
                    scs.peak_out_val = round(float(peak_out_val), 2) if peak_out_val else 0

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
                logger.error("PMP : {0}".format(e.message))
                pass
            
            try:
                sector_device_name = sector.sector_configured_on.device_name
            except Exception as e:
                sector_device_name = 0

            try:
                if sector.sector_configured_on.device_type == rad5k_type_id:
                    # index for dl values
                    in_value_index = (sector_device_name, 'rad5k_bs_dl_utilization', 'dl_utilization')
                    # index for ul values
                    out_value_index = (sector_device_name, 'rad5k_bs_ul_utilization', 'ul_utilization')
                    # in % values index
                    in_per_index = (sector_device_name, 'radwin5k_dl_util_kpi', 'rad5k_dl_util_kpi')
                    # out % values index
                    out_per_index = (sector_device_name, 'radwin5k_ul_util_kpi', 'rad5k_ul_util_kpi')
                    # index for dl_timeslot values
                    timeslot_ul_index = (sector_device_name, 'radwin5k_ss_ul_dyn_tl', 'rad5k_ss_ul_dyn_tl')
                    # index for ul values
                    timeslot_dl_index = (sector_device_name, 'radwin5k_ss_dl_dyn_tl', 'rad5k_ss_dl_dyn_tl')

                    current_timeslot_ul = None
                    current_timeslot_dl = None
                    # Current values for Dynamic TS-UL and Dynamic TS-DL for rad5 devices
                    if indexed_rad5_val.get(timeslot_ul_index):
                        current_timeslot_ul = float(indexed_rad5_val.get(timeslot_ul_index)[0]['current_value'])
                    if indexed_rad5_val.get(timeslot_dl_index):
                        current_timeslot_dl = float(indexed_rad5_val.get(timeslot_dl_index)[0]['current_value'])
                else:
                    # index for dl values
                    in_value_index = (sector_device_name, 'cambium_dl_utilization', 'dl_utilization')
                    # index for ul values
                    out_value_index = (sector_device_name, 'cambium_ul_utilization', 'ul_utilization')
                    # in % values index
                    in_per_index = (sector_device_name, 'cambium_dl_util_kpi', 'cam_dl_util_kpi')
                    # out % values index
                    out_per_index = (sector_device_name, 'cambium_ul_util_kpi', 'cam_ul_util_kpi')
            except Exception as e:
                # index for dl values
                in_value_index = (sector_device_name, 'cambium_dl_utilization', 'dl_utilization')
                # index for ul values
                out_value_index = (sector_device_name, 'cambium_ul_utilization', 'ul_utilization')
                # in % values index
                in_per_index = (sector_device_name, 'cambium_dl_util_kpi', 'cam_dl_util_kpi')
                # out % values index
                out_per_index = (sector_device_name, 'cambium_ul_util_kpi', 'cam_ul_util_kpi')

            severity_s = dict()

            try:
                sector_capacity = 7
                sector_capacity_in = CAPACITY_SETTINGS['pmp'][int(sector_capacity)]['dl']
                sector_capacity_out = CAPACITY_SETTINGS['pmp'][int(sector_capacity)]['ul']
            except Exception as e:
                # logger.error("we dont want to store any data till we get a CBW for : {0}".format(sector.sector_id))
                logger.error(e)
                continue

            try:
                # time of update
                sys_timestamp = indexed_kpi[in_per_index][0]['sys_timestamp']

                if time_delta_calculator(sys_timestamp, minutes=20):
                    # current in/out percentages
                    current_in_per = float(indexed_kpi[in_per_index][0]['current_value'])

                    # current in/out percentages
                    current_out_per = float(indexed_kpi[out_per_index][0]['current_value'])
                else:
                    current_in_per = 0
                    current_out_per = 0

                # severity for KPI services
                severity_s = {
                    indexed_kpi[in_per_index][0]['severity']: indexed_kpi[in_per_index][0]['age'],
                    indexed_kpi[out_per_index][0]['severity']: indexed_kpi[out_per_index][0]['age'],
                }

                severity, age = get_higher_severity(severity_s)

                # current in/out values
                current_in_val = current_in_per * sector_capacity_in / 100.00

                # current in/out values
                current_out_val = current_out_per * sector_capacity_out / 100.00

            except Exception as e:
                logger.error(e)
                continue  # we dont have any current values with us

            # condition is : if the topology count >= 8 : the sector is
            # stop provisioning state
            if Topology.objects.filter(device_name=sector.sector_configured_on.device_name).count() >= 8:
                severity = 'critical'

            if not severity and not age:
                continue

            peak_in_duration = 0
            peak_out_duration = 0

            if calc_util_last_day():
                try:
                    # average percentage in/out
                    avg_in_per = float(indexed_avg_max_per[in_per_index][0]['avg_val'])
                    # peak percentage in/out
                    peak_in_per = float(indexed_avg_max_per[in_per_index][0]['max_val'])
                    # average percentage in/out
                    avg_out_per = float(indexed_avg_max_per[out_per_index][0]['avg_val'])
                    # peak percentage in/out
                    peak_out_per = float(indexed_avg_max_per[out_per_index][0]['max_val'])
                    # Duration in/out  (Multiply threshold breached count with 5 to get the duration)
                    peak_in_duration = int(indexed_util_duration[in_per_index][0]['duration']) * 5
                    peak_out_duration = int(indexed_util_duration[out_per_index][0]['duration']) * 5
                except Exception as e:
                    logger.error(e)
                    avg_in_per = 0
                    peak_in_per = None
                    avg_out_per = 0
                    peak_out_per = None
                    peak_in_duration = 0
                    peak_out_duration = 0

                peak_in_per, peak_in_timestamp = get_peak_sectors_util(
                    device=sector.sector_configured_on.device_name,
                    service='cambium_dl_util_kpi',
                    data_source='cam_dl_util_kpi',
                    machine=sector.sector_configured_on.machine.name,
                    max_value=peak_in_per,
                    getit='per'
                )

                peak_out_per, peak_out_timestamp = get_peak_sectors_util(
                    device=sector.sector_configured_on.device_name,
                    service='cambium_ul_util_kpi',
                    data_source='cam_ul_util_kpi',
                    machine=sector.sector_configured_on.machine.name,
                    max_value=peak_out_per,
                    getit='per'
                )

                try:
                    # average value in/out
                    avg_in_val = avg_in_per * sector_capacity_in / 100.00
                    # peak value in/out
                    peak_in_val = peak_in_per * sector_capacity_in / 100.00
                    # average value in/out
                    avg_out_val = avg_out_per * sector_capacity_out / 100.00
                    # peak value in/out
                    peak_out_val = peak_out_per * sector_capacity_out / 100.00
                except Exception as e:
                    logger.error(e)
                    avg_in_val = 0
                    peak_in_val = 0
                    avg_out_val = 0
                    peak_out_val = 0
        
            if scs:
                scs.sector_capacity = float(sector_capacity) if sector_capacity else 0
                scs.sys_timestamp = float(sys_timestamp) if sys_timestamp else 0
                scs.organization = sector.organization if sector.organization else 1
                scs.severity = severity if severity else 'unknown'
                scs.age = float(age) if age else 0
                scs.timeslot_ul = current_timeslot_ul 
                scs.timeslot_dl = current_timeslot_dl 


                # new fileds for better representation of IN and OUT

                scs.sector_capacity_in = sector_capacity_in
                scs.sector_capacity_out = sector_capacity_out

                scs.current_in_per = round(float(current_in_per), 2) if current_in_per else 0
                scs.current_in_val = round(float(current_in_val), 2) if current_in_val else 0

                scs.current_out_per = round(float(current_out_per), 2) if current_out_per else 0
                scs.current_out_val = round(float(current_out_val), 2) if current_in_val else 0

                if calc_util_last_day():
                    scs.avg_in_per = round(float(avg_in_per), 2) if avg_in_per else 0
                    scs.avg_in_val = round(float(avg_in_val), 2) if avg_in_val else 0
                    scs.peak_in_per = round(float(peak_in_per), 2) if peak_in_per else 0
                    scs.peak_in_val = round(float(peak_in_val), 2) if peak_in_val else 0

                    scs.peak_in_timestamp = float(peak_in_timestamp) if peak_in_timestamp else 0
                    scs.peak_in_duration = int(peak_in_duration) if peak_in_duration else 0

                    scs.avg_out_per = round(float(avg_out_per), 2) if avg_out_per else 0
                    scs.avg_out_val = round(float(avg_out_val), 2) if avg_out_val else 0
                    scs.peak_out_per = round(float(peak_out_per), 2) if peak_out_per else 0
                    scs.peak_out_val = round(float(peak_out_val), 2) if peak_out_val else 0

                    scs.peak_out_timestamp = float(peak_out_timestamp) if peak_out_timestamp else 0
                    scs.peak_out_duration = int(peak_out_duration) if peak_out_duration else 0

                bulk_update_scs.append(scs)
            else:
                bulk_create_scs.append(
                    SectorCapacityStatus(
                        sector=sector,
                        sector_sector_id=sector.sector_id,
                        sector_capacity=float(sector_capacity) if sector_capacity else 0,
                        sector_capacity_in=sector_capacity_in,
                        sector_capacity_out=sector_capacity_out,
                        current_in_per=round(float(current_in_per), 2) if current_in_per else 0,
                        current_in_val=round(float(current_in_val), 2) if current_in_val else 0,
                        avg_in_per=round(float(avg_in_per), 2) if avg_in_per else 0,
                        avg_in_val=round(float(avg_in_val), 2) if avg_in_val else 0,
                        peak_in_per=round(float(peak_in_per), 2) if peak_in_per else 0,
                        peak_in_val=round(float(peak_in_val), 2) if peak_in_val else 0,
                        peak_in_timestamp=float(peak_in_timestamp) if peak_in_timestamp else 0,
                        peak_in_duration=int(peak_in_duration) if peak_in_duration else 0,
                        current_out_per=round(float(current_out_per), 2) if current_out_per else 0,
                        current_out_val=round(float(current_out_val), 2) if current_out_val else 0,
                        avg_out_per=round(float(avg_out_per), 2) if avg_out_per else 0,
                        avg_out_val=round(float(avg_out_val), 2) if avg_out_val else 0,
                        peak_out_per=round(float(peak_out_per), 2) if peak_out_per else 0,
                        peak_out_val=round(float(peak_out_val), 2) if peak_out_val else 0,
                        timeslot_ul=round(float(current_timeslot_ul), 2) if current_timeslot_ul else None, 
                        timeslot_dl=round(float(current_timeslot_dl), 2) if current_timeslot_dl else None,
                        peak_out_timestamp=float(peak_out_timestamp) if peak_out_timestamp else 0,
                        peak_out_duration=int(peak_out_duration) if peak_out_duration else 0,
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
