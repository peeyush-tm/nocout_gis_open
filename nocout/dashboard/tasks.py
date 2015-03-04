from celery import task, group

from django.db.models import Q, Sum, Avg
from django.utils import timezone
import datetime

# nocout project settings # TODO: Remove the HARDCODED technology IDs
from nocout.settings import PMP, WiMAX, TCLPOP, DEBUG

from organization.models import Organization
from device.models import DeviceTechnology, Device
from capacity_management.models import SectorCapacityStatus, BackhaulCapacityStatus
from performance.models import Topology, NetworkStatus, ServiceStatus
from dashboard.models import (DashboardSetting, DashboardSeverityStatusTimely, DashboardSeverityStatusHourly,
        DashboardSeverityStatusDaily, DashboardSeverityStatusWeekly, DashboardSeverityStatusMonthly,
        DashboardSeverityStatusYearly, DashboardRangeStatusTimely, DashboardRangeStatusHourly, DashboardRangeStatusDaily,
        DashboardRangeStatusWeekly, DashboardRangeStatusMonthly, DashboardRangeStatusYearly,
    )

from inventory.utils.util import organization_sectors, organization_network_devices
from inventory.models import get_default_org

from inventory.tasks import bulk_update_create

from dashboard.utils import \
    get_topology_status_results, \
    get_dashboard_status_range_counter, \
    get_dashboard_status_range_mapped


import logging
logger = logging.getLogger(__name__)


@task()
def network_speedometer_dashboards():
    """

    :return: Calculation Status for the objects
    """
    g_jobs = list()
    ret = False

    user_organizations = Organization.objects.all()
    processed_for = timezone.now()

    network_dashboards = {
        'latency-network': {
            'model': NetworkStatus,
            'data_source': 'rta',
            'service_name': 'ping',
            'severity': ['warning', 'critical'],
            'current_value': ' current_value > 0 '
        },
        'packetloss-network': {
            'model': NetworkStatus,
            'data_source': 'rta',
            'service_name': 'ping',
            'severity': ['warning', 'critical', 'down'],
            'current_value': ' current_value < 100 '
        },
        'down-network': {
            'model': NetworkStatus,
            'data_source': 'pl',
            'service_name': 'ping',
            'severity': ['critical', 'down'],
            'current_value': ' current_value >= 100 '
        }
    }

    for organization in user_organizations:

        required_devices = organization_network_devices(organizations=[organization.id],
                                                        technology=None,
                                                        specify_ptp_bh_type=None
                                                        )  # this will give PMP and WiMAX devices

        if not required_devices.exists():  # this evaluates the query set
            continue

        for dashboard in network_dashboards:
            # organization,
            # dashboard_name,
            # processed_for,
            # dashboard_config,
            # technology=None,
            # required_devices=None
            g_jobs.append(
                prepare_network_alert.s(
                    organization=organization,
                    dashboard_name=dashboard,
                    processed_for=processed_for,
                    dashboard_config=network_dashboards,
                    technology=None,
                    required_devices=required_devices
                )
            )

    if not len(g_jobs):
        return ret

    job = group(g_jobs)
    result = job.apply_async()
    for r in result.get():
        ret |= r

    return ret


@task()
def temperature_speedometer_dashboards():
    """

    :return: True
    """
    g_jobs = list()
    ret = False

    user_organizations = Organization.objects.all()
    processed_for = timezone.now()

    temperatures = ['IDU']
    if DEBUG:
        temperatures = ['IDU', 'ACB', 'FAN']

    for organization in user_organizations:

        required_devices = organization_network_devices(organizations=[organization.id],
                                                        technology=WiMAX.ID,
                                                        specify_ptp_bh_type=None
                                                        )
        if required_devices.exists():
            for temp in temperatures:
                # organization,
                # processed_for,
                # required_devices,
                # chart_type='IDU'
                g_jobs.append(
                    calculate_timely_temperature.s(
                        organization=organization,
                        processed_for=processed_for,
                        required_devices=required_devices,
                        chart_type=temp
                    )
                )
    if not len(g_jobs):
        return ret

    job = group(g_jobs)
    result = job.apply_async()
    for r in result.get():
        ret |= r

    return ret


@task()
def calculate_status_dashboards(technology):
    """

    :return:
    """
    g_jobs = list()
    ret = False

    if not DEBUG:  # calculate technology wise only if the debug is set
        return ret

    if not technology:
        return ret

    try:
        tech_id = eval(technology).ID
    except:
        return ret

    user_organizations = Organization.objects.all()
    processed_for = timezone.now()

    dashboards = {
        "latency-{0}".format(technology): {
            'model': NetworkStatus,
            'data_source': 'rta',
            'service_name': 'ping',
            'severity': ['warning', 'critical'],
            'current_value': ' current_value > 0 '
        },
        "packetloss-{0}".format(technology): {
            'model': NetworkStatus,
            'data_source': 'rta',
            'service_name': 'ping',
            'severity': ['warning', 'critical', 'down'],
            'current_value': ' current_value < 100 '
        },
        "down-{0}".format(technology): {
            'model': NetworkStatus,
            'data_source': 'pl',
            'service_name': 'ping',
            'severity': ['critical', 'down'],
            'current_value': ' current_value >= 100 '
        }
    }

    for organization in user_organizations:
        required_devices = organization_network_devices(organizations=[organization.id],
                                                        technology=tech_id,
                                                        specify_ptp_bh_type=None
                                                        )
        if required_devices.exists():
            for dashboard in dashboards:
                g_jobs.append(
                    prepare_network_alert.s(
                        organization=organization,
                        dashboard_name=dashboard,
                        processed_for=processed_for,
                        dashboard_config=dashboards,
                        technology=technology,
                        required_devices=required_devices
                    )
                )

    if len(g_jobs):
        job = group(g_jobs)
        result = job.apply_async()
        for r in result.get():
            ret |= r
    return ret


@task()
def calculate_range_dashboards(technology, type):
    """

    :return:
    """
    g_jobs = list()
    ret = False

    user_organizations = Organization.objects.all()
    processed_for = timezone.now()

    # sector_tech = ['PMP', 'WiMAX']
    # backhaul_tech = ['TCLPOP', 'PMP', 'WiMAX']

    tech = technology
    if type == 'sector':
        g_jobs.append(
            calculate_timely_sector_capacity.s(
                user_organizations,
                technology=tech,
                model=DashboardSeverityStatusTimely,
                processed_for=processed_for
            )
        )

        g_jobs.append(
            calculate_timely_sales_opportunity.s(
                user_organizations,
                technology=tech,
                model=DashboardRangeStatusTimely,
                processed_for=processed_for
            )
        )

    elif type == 'backhaul':
        g_jobs.append(
            calculate_timely_backhaul_capacity.s(
                user_organizations,
                technology=tech,
                model=DashboardSeverityStatusTimely,
                processed_for=processed_for
            )
        )

    else:
        return False

    if len(g_jobs):
        job = group(g_jobs)
        result = job.apply_async()
        for r in result.get():
            ret |= r

    return ret


@task()
def calculate_timely_sector_capacity(organizations, technology, model, processed_for):
    '''
    :param technology: Named Tuple
    :param model: Dashboard Model to store timely dashboard data.
    :param processed_for:
    return
    '''
    try:
        sector_technology = eval(technology)
    except Exception as e:
        logger.exception(e)
        return False

    required_values = [
        'id',
        'sector__name',
        'sector__sector_configured_on__device_name',
        'severity',
        'sys_timestamp',
        'age',
        'organization'
    ]

    dashboard_name = '%s_sector_capacity' % (sector_technology.NAME.lower())

    for organization in organizations:
        sector_objects = SectorCapacityStatus.objects.filter(
                Q(organization__in=[organization]),
                Q(sector__sector_configured_on__device_technology=sector_technology.ID),
                Q(severity__in=['warning', 'critical', 'ok', 'unknown']),
            )


        if sector_objects.exists():
            range_counter = {
                'dashboard_name': dashboard_name,
                'device_name': dashboard_name,
                'reference_name': dashboard_name,
                'warning': 0,
                'critical': 0,
                'ok': 0,
                'down': 0,
                'unknown': 0,
                'organization': organization,
                'processed_for': processed_for
            }
            bulk_data_list = list()
            sectors = sector_objects.values(*required_values)

            for item in sectors:
                # Create the range_counter dictionay containg the model's field name as key
                # Update the range_counter on the basis of severity.
                if (item['age'] <= item['sys_timestamp'] - 600) and (item['severity'].strip().lower() in ['warning', 'critical']):
                    range_counter[item['severity'].strip().lower()] += 1
                elif item['severity'].strip().lower() == 'ok':
                    range_counter['ok'] += 1
                else:
                    range_counter['unknown'] += 1

            bulk_data_list.append(model(**range_counter))

            if len(bulk_data_list):
                # call the method to bulk create the onjects.
                bulk_update_create.delay(
                    bulky=bulk_data_list,
                    action='create',
                    model=model)
    return True


@task()
def calculate_timely_backhaul_capacity(organizations, technology, model, processed_for):
    '''
    :param technology: Named Tuple
    :param model: Dashboard Model to store timely dashboard data.
    :param processed_for:
    return
    '''
    try:
        backhaul_technology = eval(technology)
    except Exception, e:
        return False

    dashboard_name = '%s_backhaul_capacity' % (backhaul_technology.NAME.lower())

    required_values = [
        'id',
        'backhaul__name',
        'backhaul__bh_configured_on__device_name',
        'severity',
        'sys_timestamp',
        'age',
        'organization'
    ]

    for organization in organizations:

        backhaul_objects = BackhaulCapacityStatus.objects.filter(
                Q(organization__in=[organization]),
                Q(backhaul__bh_configured_on__device_technology=backhaul_technology.ID),
                Q(severity__in=['warning', 'critical', 'ok', 'unknown']),
            )

        if backhaul_objects.exists():
            range_counter = {
                'dashboard_name': dashboard_name,
                'device_name': dashboard_name,
                'reference_name': dashboard_name,
                'warning': 0,
                'critical': 0,
                'ok': 0,
                'down': 0,
                'unknown': 0,
                'organization': organization,
                'processed_for': processed_for
            }

            data_list = list()
            backhaul = backhaul_objects.values(*required_values)

            for item in backhaul:
                # Update the range_counter on the basis of severity.
                if (item['age'] <= item['sys_timestamp'] - 600) and (item['severity'].strip().lower() in ['warning', 'critical']):
                    range_counter[item['severity'].strip().lower()] += 1
                elif item['severity'].strip().lower() == 'ok':
                    range_counter['ok'] += 1
                else:
                    range_counter['unknown'] += 1

            # Create the list of model object.
            data_list.append(model(**range_counter))

            if len(data_list):
                # call the method to bulk create the onjects.
                bulk_update_create.delay(
                    bulky=data_list,
                    action='create',
                    model=model)

    return True


@task()
def calculate_timely_sales_opportunity(organizations, technology, model, processed_for):
    '''
    :param technology: Named Tuple
    :param model: Dashboard Model to store timely dashboard data.
    :param processed_for: datetime (example: timezone.now())
    return
    '''
    try:
        sales_technology = eval(technology)
    except Exception, e:
        return False
    # convert the data source in format topology_pmp/topology_wimax
    data_source = '%s-%s' % ('topology', sales_technology.NAME.lower())
    dashboard_name = '%s_sales_opportunity' % (sales_technology.NAME.lower())

    technology_id = sales_technology.ID if sales_technology else None
    try:
        dashboard_setting = DashboardSetting.objects.get(technology_id=technology_id,
                                                         page_name='main_dashboard',
                                                         name=data_source,
                                                         is_bh=False)
    except DashboardSetting.DoesNotExist as e:
        logger.info("DashboardSetting for %s is not available." % dashboard_name)
        return False

    for organization in organizations:

        # get the sector of User's Organization [and Sub Organization]
        sector_objects = organization_sectors([organization], technology_id)
        # get the device of the user sector.
        # sector_devices = Device.objects.filter(id__in=user_sector.values_list('sector_configured_on', flat=True))

        if sector_objects.exists():
            data_list = list()
            user_sector = sector_objects
            status_counter = {
                "dashboard_name": dashboard_name,
                "device_name": dashboard_name,
                "reference_name": dashboard_name,
                "processed_for": processed_for,
                "organization": organization,
                "range1": 0,
                "range2": 0,
                "range3": 0,
                "range4": 0,
                "range5": 0,
                "range6": 0,
                "range7": 0,
                "range8": 0,
                "range9": 0,
                "range10": 0,
                "unknown": 0,
            }
            # get the list of dictionary on the basis of parameters.
            service_status_results = get_topology_status_results(
                user_devices=None,
                model=Topology,
                service_name=None,
                data_source='topology',
                user_sector=user_sector
            )

            for result in service_status_results:
                # get the dictionary containing the model's field name as key.
                # range_counter in format {'range1': 1, 'range2': 2,...}
                range_counter = get_dashboard_status_range_counter(dashboard_setting, [result])
                for ranges in range_counter:
                    status_counter[ranges] += range_counter[ranges]
                # prepare a list of model object.
            data_list.append(model(**status_counter))

            if len(data_list):
                # call method to bulk create the model object.
                bulk_update_create.delay(
                    bulky=data_list,
                    action='create',
                    model=model
                )

    return True


@task()
def prepare_network_alert(organization,
                          dashboard_name,
                          processed_for,
                          dashboard_config,
                          required_devices,
                          technology=None,
                          ):
    """


    :param dashboard_config:
    :param required_devices:
    :param organization:
    :param dashboard_name:
    :param processed_for:
    :param technology:
    :return:
    """
    processed_for = processed_for
    technology_id = None

    if not technology:
        try:
            latency_technology = eval(technology)
            technology_id = latency_technology.ID
        except Exception as e:
            logger.exception(e)
            return False
    else:
        pass

    g_jobs = list()
    ret = False

    if not required_devices:
        return ret

    # get the list of dictionay where 'machine__name' and 'device_name' as key of the user's device.
    sector_devices = required_devices.values('machine__name', 'device_name')

    # get the dictionary of machine_name as key and device_name as a list for that machine.
    machine_dict = prepare_machines(sector_devices)

    status_count = 0

    model = dashboard_config[dashboard_name]['model']
    service_name = dashboard_config[dashboard_name]['service_name']
    data_source = dashboard_config[dashboard_name]['data_source']
    severity = dashboard_config[dashboard_name]['severity']
    current_value = dashboard_config[dashboard_name]['current_value']

    for machine_name, device_list in machine_dict.items():
        status_count += model.objects.order_by(

        ).extra(
            where=[current_value]
        ).filter(
            device_name__in=device_list,
            service_name=service_name,
            data_source=data_source,
            severity__in=severity
        ).using(machine_name).count()

    g_jobs.append(
        calculate_timely_network_alert.s(
            dashboard_name=dashboard_name,
            processed_for=processed_for,
            organization=organization,
            technology=technology,
            status_count=status_count,
            status_dashboard_name=None
        )
    )

    if len(g_jobs):
        job = group(g_jobs)
        result = job.apply_async()
        for r in result.get():
            ret |= r

    return ret


@task()
def calculate_timely_temperature(organization, processed_for, required_devices, chart_type='IDU'):
    '''
    Method to calculate the temperature status of devices.

    :param organization:
    :param processed_for:
    :param required_devices:
    :param chart_type:
    :param:
    return:
    '''

    if chart_type == 'IDU':
        service_list = ['wimax_bs_temperature_acb', 'wimax_bs_temperature_fan']
        data_source_list = ['acb_temp', 'fan_temp']
    elif chart_type == 'ACB':
        service_list = ['wimax_bs_temperature_acb']
        data_source_list = ['acb_temp']
    elif chart_type == 'FAN':
        service_list = ['wimax_bs_temperature_fan']
        data_source_list = ['fan_temp']
    else:
        return False

    g_jobs = list()
    ret = False

    technology_id = 3
    processed_for = processed_for

    status_dashboard_name = 'temperature-' + chart_type.lower()

    # get the device of user's organization [and sub organization]

    # get the list of dictionay where 'machine__name' and 'device_name' as key of the user's device.
    sector_devices = required_devices.values('machine__name', 'device_name')

    machine_dict = prepare_machines(sector_devices)

    # count of devices in severity
    status_count = 0
    # creating a list dictionary using machine name and there corresponing device list.
    # And list is order by device_name.
    for machine_name, device_list in machine_dict.items():
        status_count += ServiceStatus.objects.order_by().filter(
            device_name__in=device_list,
            service_name__in=service_list,
            data_source__in=data_source_list,
            severity__in=['warning', 'critical']
            ).using(machine_name).count()

    g_jobs.append(
        # dashboard_name,
        # processed_for,
        # organization,
        # technology=None,
        # status_count=0,
        # status_dashboard_name=None
        calculate_timely_network_alert.s(
            dashboard_name='temperature',
            processed_for=processed_for,
            organization=organization,
            technology='WiMAX',
            status_count=status_count,
            status_dashboard_name=status_dashboard_name
        )
    )

    if len(g_jobs):
        job = group(g_jobs)
        result = job.apply_async()
        for r in result.get():
            ret |= r

    return ret


@task()
def calculate_timely_network_alert(dashboard_name,
                                   processed_for,
                                   organization,  # assume the organization to be default
                                   technology=None,
                                   status_count=0,
                                   status_dashboard_name=None
                                   ):
    """
    prepare a list of model object to bulk create the model objects.

    :param dashboard_name: dashboard_name: name of dashboard used in dashboard_setting.
    :param processed_for: processed_for: datetime
    :param technology: technology: Named Tuple
    :param status_count: count of status of objects in warning, critical
    :param status_dashboard_name: string
    return: True
    """
    assumed_organization = get_default_org()

    if organization:
        assumed_organization = organization

    try:
        if technology:
            network_technology = eval(technology)
        else:
            network_technology = None
    except Exception as e:
        logger.exception(e)
        return False

    technology_id = network_technology.ID if network_technology else None
    try:
        dashboard_setting = DashboardSetting.objects.get(
            technology_id=technology_id,
            page_name='main_dashboard',
            name=dashboard_name,
            is_bh=False
        )
    except DashboardSetting.DoesNotExist as e:
        logger.exception(" Dashboard Setting of {0} is not available. {1}".format(dashboard_name, e))
        return False

    # device_name = '-1'  # lets just say it does not exists # todo remove this s**t
    processed_for = processed_for

    bulky = list()

    if not status_dashboard_name:
        status_dashboard_name = dashboard_name

    # get the dictionay where keys are same as of the model fields.
    dashboard_data_dict = get_dashboard_status_range_mapped(dashboard_setting, status_count)
    # updating the dictionay with some other fields used in model.

    if dashboard_data_dict:
        dashboard_data_dict.update(
            {
                'device_name': status_dashboard_name,
                'reference_name': status_dashboard_name,
                'dashboard_name': status_dashboard_name,
                'processed_for': processed_for,
                'organization': assumed_organization
            }
        )
        # creating a list of model object for bulk create.
        bulky.append(DashboardRangeStatusTimely(**dashboard_data_dict))

        # call celery task to create dashboard data
        bulk_update_create.delay(bulky=bulky,
                                 action='create',
                                 model=DashboardRangeStatusTimely)

    return True


def prepare_machines(device_list):
    """
    Create a dictionay machine as a key and device_name as a list for that machine.

    :param:
    device_list: list of devices.

    return: dictionay.
    """
    # Unique machine from the device_list
    unique_device_machine_list = {device['machine__name']: True for device in device_list}.keys()

    machine_dict = {}
    # Creating the machine as a key and device_name as a list for that machine.
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device['device_name'] for device in device_list if
                                 device['machine__name'] == machine]

    return machine_dict


@task()
def calculate_hourly_main_dashboard():
    '''
    Task to calculate the main dashboard status in every hour using celerybeat.
    '''

    now = timezone.now()
    buffer_now = now + datetime.timedelta(minutes=-5)
    then = now + datetime.timedelta(hours=-1)
    calculate_hourly_range_status(now=buffer_now, then=then)
    calculate_hourly_range_status(now=buffer_now, then=then)
    return True


def calculate_hourly_severity_status(now, then):
    '''
    Calculate the status of dashboard from DashboardSeverityStatusTimely model
    and create list of DashboardSeverityStatusHourly model object for calculated data
    and then delete all data from the DashboardSeverityStatusTimely model.

    :param now: datetime (example: timezone.now())

    return:
    '''
    # get all data from the model order by 'dashboard_name' and 'device_name'.
    last_hour_timely_severity_status = DashboardSeverityStatusTimely.objects.order_by().filter(
        processed_for__lte=now,
        processed_for__gte=then
    ).values(
        'dashboard_name',
        'organization'
    ).annotate(
        Normal=Sum('ok'),
        Needs_Augmentation=Avg('warning'),
        Stop_Provisioning=Avg('critical'),
        Down=Avg('down'),
        Unknown=Avg('unknown')
    )

    organizations = Organization.objects.all()

    hourly_severity_status_list = []    # list for the DashboardSeverityStatusHourly model object

    for timely_severity_status in last_hour_timely_severity_status:
        # Sum the status value for the same dashboard_name and device_name.
        # Create new model object when dashboard_name and
        # device_name are different from previous dashboard_name and device_name.
        hourly_severity_status = DashboardSeverityStatusHourly(
            dashboard_name=timely_severity_status['dashboard_name'],
            device_name=timely_severity_status['dashboard_name'],
            reference_name=timely_severity_status['dashboard_name'],
            processed_for=now,
            warning=timely_severity_status['Needs_Augmentation'],
            critical=timely_severity_status['Stop_Provisioning'],
            ok=timely_severity_status['Normal'],
            down=timely_severity_status['Down'],
            unknown=timely_severity_status['Unknown'],
            organization=organizations.get(id=timely_severity_status['organization'])
        )
        # append in list for every new dashboard_name and device_name.
        hourly_severity_status_list.append(hourly_severity_status)

    if len(hourly_severity_status_list):
        bulk_update_create.delay(bulky=hourly_severity_status_list,
                                 action='create',
                                 model=DashboardSeverityStatusHourly)

    # delete the data from the DashboardSeverityStatusTimely model.
    DashboardSeverityStatusTimely.objects.order_by().filter(
        processed_for__lte=now,
        processed_for__gte=then
    ).delete()
    return True


def calculate_hourly_range_status(now, then):
    '''
    Calculate the status of dashboard from DashboardRangeStatusTimely model
    and create list of DashboardRangeStatusHourly model object for calculated data
    and then delete all data from the DashboardRangeStatusTimely model.

    :param now: datetime (example: timezone.now())

    return:
    '''
    # get all data from the model order by 'dashboard_name' and 'device_name'.
    last_hour_timely_range_status = DashboardRangeStatusTimely.objects.order_by().filter(
        processed_for__lte=now,
        processed_for__gte=then
    ).values(
        'dashboard_name',
        'organization'
    ).annotate(
        Range1=Avg('range1'),
        Range2=Avg('range2'),
        Range3=Avg('range3'),
        Range4=Avg('range4'),
        Range5=Avg('range5'),
        Range6=Avg('range6'),
        Range7=Avg('range7'),
        Range8=Avg('range8'),
        Range9=Avg('range9'),
        Range10=Avg('range10'),
        Unknown=Avg('unknown')
    )

    organizations = Organization.objects.all()

    hourly_range_status_list = []   # list for the DashboardRangeStatusHourly model object

    for timely_range_status in last_hour_timely_range_status:
        # Create new model object when dashboard_name and device_name are different
        # from previous dashboard_name and device_name.
        hourly_range_status = DashboardRangeStatusHourly(
            dashboard_name=timely_range_status['dashboard_name'],
            device_name=timely_range_status['dashboard_name'],
            reference_name=timely_range_status['dashboard_name'],
            processed_for=now,
            range1=timely_range_status['Range1'],
            range2=timely_range_status['Range2'],
            range3=timely_range_status['Range3'],
            range4=timely_range_status['Range4'],
            range5=timely_range_status['Range5'],
            range6=timely_range_status['Range6'],
            range7=timely_range_status['Range7'],
            range8=timely_range_status['Range8'],
            range9=timely_range_status['Range9'],
            range10=timely_range_status['Range10'],
            unknown=timely_range_status['Unknown'],
            organization=organizations.get(id=timely_range_status['organization'])
        )
        # append in list for every new dashboard_name and device_name.
        hourly_range_status_list.append(hourly_range_status)

    if len(hourly_range_status_list):
        bulk_update_create.delay(bulky=hourly_range_status_list,
                                 action='create',
                                 model=DashboardRangeStatusHourly)

    # delete the data from the DashboardRangeStatusTimely model.
    DashboardRangeStatusTimely.objects.order_by().filter(
        processed_for__lte=now,
        processed_for__gte=then
    ).delete()
    return True


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


@task()
def calculate_daily_main_dashboard():
    '''
    Task to calculate the daily status of main dashboard.
    '''
    now = timezone.now()
    calculate_daily_severity_status(now)
    calculate_daily_range_status(now)


def calculate_daily_severity_status(now):
    '''
    Calculate the status of dashboard from DashboardSeverityStatusHourly model
    and create list of DashboardSeverityStatusDaily model object for calculated data
    and then delete all data from the DashboardSeverityStatusHourly model.

    :param now: datetime (example: timezone.now())

    return:
    '''
    # get the current timezone.
    # tzinfo = timezone.get_current_timezone()
    # get today date according to current timezone and reset time to 12 o'clock.

    today = timezone.datetime(now.year, now.month, now.day, 0, 0)
    previous_day = now - timezone.timedelta(days=1)
    yesterday = timezone.datetime(previous_day.year, previous_day.month, previous_day.day, 0, 0)

    # get all result of yesterday only and order by 'dashboard_name' and'device_name'
    last_day_timely_severity_status = DashboardSeverityStatusHourly.objects.order_by().filter(
        processed_for__gte=yesterday,
        processed_for__lt=today
    ).values(
        'dashboard_name',
        'organization'
    ).annotate(
        Normal=Sum('ok'),
        Needs_Augmentation=Avg('warning'),
        Stop_Provisioning=Avg('critical'),
        Down=Avg('down'),
        Unknown=Avg('unknown')
    )
    organizations = Organization.objects.all()
    # [
    # {
    #   'dashboard_name': u'pmp_backhaul_capacity',
    #   'Needs_Augmentation': 0, '
    #   Normal': 1102,
    #   'Unknown': 0,
    #   'Stop_Provisioning': 0
    #  }
    # ]

    daily_severity_status_list = []     # list for the DashboardSeverityStatusDaily model object

    for hourly_severity_status in last_day_timely_severity_status:
        daily_severity_status = DashboardSeverityStatusDaily(
            dashboard_name=hourly_severity_status['dashboard_name'],
            device_name=hourly_severity_status['dashboard_name'],
            reference_name=hourly_severity_status['dashboard_name'],
            processed_for=yesterday,
            warning=hourly_severity_status['Needs_Augmentation'],
            critical=hourly_severity_status['Stop_Provisioning'],
            ok=hourly_severity_status['Normal'],
            down=hourly_severity_status['Down'],
            unknown=hourly_severity_status['Unknown'],
            organization=organizations.get(id=hourly_severity_status['organization'])
        )
        daily_severity_status_list.append(daily_severity_status)

    if len(daily_severity_status_list):
        bulk_update_create.delay(bulky=daily_severity_status_list,
                                 action='create',
                                 model=DashboardSeverityStatusDaily)

    DashboardSeverityStatusHourly.objects.order_by().filter(
        processed_for__gte=yesterday,
        processed_for__lt=today
    ).delete()
    return True


def calculate_daily_range_status(now):
    '''
    Calculate the status of dashboard from DashboardRangeStatusHourly model
    and create list of DashboardRangeStatusDaily model object for calculated data
    and then delete all data from the DashboardRangeStatusHourly model.

    :param now: datetime (example: timezone.now())

    return:
    '''
    # get the current timezone.
    tzinfo = timezone.get_current_timezone()
    # get today date according to current timezone and reset time to 12 o'clock.
    today = timezone.datetime(now.year, now.month, now.day, 0, 0)
    previous_day = now - timezone.timedelta(days=1)
    yesterday = timezone.datetime(previous_day.year, previous_day.month, previous_day.day, 0, 0)
    # get all result of yesterday only and order by 'dashboard_name' and'device_name'
    last_day_hourly_range_status = DashboardRangeStatusHourly.objects.order_by().filter(
        processed_for__gte=yesterday,
        processed_for__lt=today
    ).values(
        'dashboard_name',
        'organization'
    ).annotate(
        Range1=Avg('range1'),
        Range2=Avg('range2'),
        Range3=Avg('range3'),
        Range4=Avg('range4'),
        Range5=Avg('range5'),
        Range6=Avg('range6'),
        Range7=Avg('range7'),
        Range8=Avg('range8'),
        Range9=Avg('range9'),
        Range10=Avg('range10'),
        Unknown=Avg('unknown')
    )

    organizations = Organization.objects.all()

    daily_range_status_list = []

    for hourly_range_status in last_day_hourly_range_status:
        daily_range_status = DashboardRangeStatusDaily(
            dashboard_name=hourly_range_status['dashboard_name'],
            device_name=hourly_range_status['dashboard_name'],
            reference_name=hourly_range_status['dashboard_name'],
            processed_for=yesterday,
            range1=hourly_range_status['Range1'],
            range2=hourly_range_status['Range2'],
            range3=hourly_range_status['Range3'],
            range4=hourly_range_status['Range4'],
            range5=hourly_range_status['Range5'],
            range6=hourly_range_status['Range6'],
            range7=hourly_range_status['Range7'],
            range8=hourly_range_status['Range8'],
            range9=hourly_range_status['Range9'],
            range10=hourly_range_status['Range10'],
            unknown=hourly_range_status['Unknown'],
            organization=organizations.get(id=hourly_range_status['organization'])
        )
        daily_range_status_list.append(daily_range_status)

    if len(daily_range_status_list):
        bulk_update_create.delay(bulky=daily_range_status_list,
                                 action='create',
                                 model=DashboardRangeStatusDaily)

    DashboardRangeStatusHourly.objects.order_by().filter(
        processed_for__gte=yesterday,
        processed_for__lt=today
    ).delete()
    return True

