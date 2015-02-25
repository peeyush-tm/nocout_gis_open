from celery import task, group

from django.db.models import Q, Count, F
from django.utils import timezone
import datetime

# nocout project settings # TODO: Remove the HARDCODED technology IDs
from nocout.settings import PMP, WiMAX, TCLPOP

from organization.models import Organization
from device.models import DeviceTechnology, Device
from capacity_management.models import SectorCapacityStatus, BackhaulCapacityStatus
from performance.models import Topology, NetworkStatus
from dashboard.models import (DashboardSetting, DashboardSeverityStatusTimely, DashboardSeverityStatusHourly,
        DashboardSeverityStatusDaily, DashboardSeverityStatusWeekly, DashboardSeverityStatusMonthly,
        DashboardSeverityStatusYearly, DashboardRangeStatusTimely, DashboardRangeStatusHourly, DashboardRangeStatusDaily,
        DashboardRangeStatusWeekly, DashboardRangeStatusMonthly, DashboardRangeStatusYearly,
    )

from inventory.utils.util import organization_sectors, organization_network_devices

from inventory.tasks import bulk_update_create

from dashboard.utils import get_topology_status_results, get_dashboard_status_range_counter
import logging

logger = logging.getLogger(__name__)


@task()
def calculate_timely_main_dashboard():
    '''
    Task to calculate the main dashboard status in every 5 minutes using celerybeat.
    '''
    processed_for = timezone.now()
    logger.debug('CELERYBEAT: Timely: starts at {0} '.format(processed_for))

    user_organizations = Organization.objects.all()

    calculate_timely_sector_capacity(user_organizations,
                                     technology=PMP,
                                     model=DashboardSeverityStatusTimely,
                                     processed_for=processed_for)
    calculate_timely_sector_capacity(user_organizations,
                                     technology=WiMAX,
                                     model=DashboardSeverityStatusTimely,
                                     processed_for=processed_for)

    calculate_timely_backhaul_capacity(user_organizations,
                                       technology=PMP,
                                       model=DashboardSeverityStatusTimely,
                                       processed_for=processed_for)
    calculate_timely_backhaul_capacity(user_organizations,
                                       technology=WiMAX,
                                       model=DashboardSeverityStatusTimely,
                                       processed_for=processed_for)
    calculate_timely_backhaul_capacity(user_organizations,
                                       technology=TCLPOP,
                                       model=DashboardSeverityStatusTimely,
                                       processed_for=processed_for)

    calculate_timely_sales_opportunity(user_organizations,
                                       technology=PMP,
                                       model=DashboardRangeStatusTimely,
                                       processed_for=processed_for)
    calculate_timely_sales_opportunity(user_organizations,
                                       technology=WiMAX,
                                       model=DashboardRangeStatusTimely,
                                       processed_for=processed_for)

    calculate_timely_latency(user_organizations,
                             dashboard_name='latency-pmp',
                             processed_for=processed_for,
                             technology=PMP)
    calculate_timely_latency(user_organizations,
                             dashboard_name='latency-wimax',
                             processed_for=processed_for,
                             technology=WiMAX)
    calculate_timely_latency(user_organizations,
                             dashboard_name='latency-network',
                             processed_for=processed_for)

    calculate_timely_packet_drop(user_organizations,
                                 dashboard_name='packetloss-pmp',
                                 processed_for=processed_for,
                                 technology=PMP)
    calculate_timely_packet_drop(user_organizations,
                                 dashboard_name='packetloss-wimax',
                                 processed_for=processed_for,
                                 technology=WiMAX)
    calculate_timely_packet_drop(user_organizations,
                                 dashboard_name='packetloss-network',
                                 processed_for=processed_for)

    calculate_timely_down_status(user_organizations,
                                 dashboard_name='down-pmp',
                                 processed_for=processed_for,
                                 technology=PMP)
    calculate_timely_down_status(user_organizations,
                                 dashboard_name='down-wimax',
                                 processed_for=processed_for,
                                 technology=WiMAX)
    calculate_timely_down_status(user_organizations,
                                 dashboard_name='down-network',
                                 processed_for=processed_for)

    calculate_timely_temperature(user_organizations,
                                 processed_for=processed_for,
                                 chart_type='IDU')
    calculate_timely_temperature(user_organizations,
                                 processed_for=processed_for,
                                 chart_type='ACB')
    calculate_timely_temperature(user_organizations,
                                 processed_for=processed_for,
                                 chart_type='FAN')
    logger.debug('CELERYBEAT: Timely: ends at {0} '.format(timezone.now()))

    return True

def calculate_timely_sector_capacity(organizations, technology, model, processed_for):
    '''
    :param technology: Named Tuple
    :param model: Dashboard Model to store timely dashboard data.
    :param processed_for:
    return
    '''
    dashboard_name = '%s_sector_capacity' % (technology.NAME.lower())

    sectors = SectorCapacityStatus.objects.filter(
            Q(organization__in=organizations),
            Q(sector__sector_configured_on__device_technology=technology.ID),
            Q(severity__in=['warning', 'critical', 'ok']),
        ).values('id', 'sector__name', 'sector__sector_configured_on__device_name', 'severity', 'sys_timestamp', 'age')

    logger.debug('CELERYBEAT: Timely: dashboard_name {0} & Sectors count: {1}'.format(dashboard_name, sectors.count()))
    data_list = list()
    for item in sectors:
        # Create the range_counter dictionay containg the model's field name as key
        range_counter = dict(
            dashboard_name=dashboard_name,
            device_name=item['sector__sector_configured_on__device_name'],
            reference_name=item['sector__name'],
            processed_for=processed_for,
        )
        # Update the range_counter on the basis of severity.
        if (item['age'] <= item['sys_timestamp'] - 600) and (item['severity'].strip().lower() in ['warning', 'critical']):
            range_counter.update({item['severity'].strip().lower() : 1})
        elif item['severity'].strip().lower() == 'ok':
            range_counter.update({'ok' : 1})
        else:
            range_counter.update({'unknown' : 1})

        # Create the list of model object.
        try:
            data_list.append(model(**range_counter))
        except Exception as e:
            pass

    logger.debug('calculate_timely_sector_capacity : data list = {0}'.format(data_list))
    # call the method to bulk create the onjects.
    bulk_update_create.delay(data_list, action='create', model=model)

def calculate_timely_backhaul_capacity(organizations, technology, model, processed_for):
    '''
    :param technology: Named Tuple
    :param model: Dashboard Model to store timely dashboard data.
    :param processed_for:
    return
    '''
    dashboard_name = '%s_backhaul_capacity' % (technology.NAME.lower())

    backhaul = BackhaulCapacityStatus.objects.filter(
            Q(organization__in=organizations),
            Q(backhaul__bh_configured_on__device_technology=technology.ID),
            Q(severity__in=['warning', 'critical', 'ok']),
        ).values('id', 'backhaul__name', 'backhaul__bh_configured_on__device_name', 'severity', 'sys_timestamp', 'age')

    data_list = list()
    for item in backhaul:
        # Create the range_counter dictionay containg the model's field name as key
        range_counter = dict(
            dashboard_name=dashboard_name,
            device_name=item['backhaul__bh_configured_on__device_name'],
            reference_name=item['backhaul__name'],
            processed_for=processed_for,
        )
        # Update the range_counter on the basis of severity.
        if (item['age'] <= item['sys_timestamp'] - 600) and (item['severity'].strip().lower() in ['warning', 'critical']):
            range_counter.update({item['severity'].strip().lower() : 1})
        elif item['severity'].strip().lower() == 'ok':
            range_counter.update({'ok' : 1})
        else:
            range_counter.update({'unknown' : 1})

        # Create the list of model object.
        try:
            data_list.append(model(**range_counter))
        except Exception as e:
            pass

    logger.debug('calculate_timely_backhaul_capacity : data list = {0}'.format(data_list))
    # call the method to bulk create the onjects.
    bulk_update_create.delay(data_list, action='create', model=model)

def calculate_timely_sales_opportunity(organizations, technology, model, processed_for):
    '''
    :param technology: Named Tuple
    :param model: Dashboard Model to store timely dashboard data.
    :param processed_for: datetime (example: timezone.now())
    return
    '''
    # convert the data source in format topology_pmp/topology_wimax
    data_source = '%s-%s' % ('topology', technology.NAME.lower())
    dashboard_name = '%s_sales_opportunity' % (technology.NAME.lower())

    technology_id = technology.ID if technology else None
    try:
        dashboard_setting = DashboardSetting.objects.get(technology_id=technology_id,
                                                         page_name='main_dashboard',
                                                         name=data_source,
                                                         is_bh=False)
    except DashboardSetting.DoesNotExist as e:
        logger.info("DashboardSetting for %s is not available." % dashboard_name)
        return False

    # get the sector of User's Organization [and Sub Organization]
    user_sector = organization_sectors(organizations, technology_id)
    # get the device of the user sector.
    sector_devices = Device.objects.filter(id__in=user_sector.values_list('sector_configured_on', flat=True))

    # get the list of dictionary on the basis of parameters.
    service_status_results = get_topology_status_results(
        sector_devices, model=Topology, service_name='topology', data_source='topology', user_sector=user_sector
    )

    data_list = list()
    for result in service_status_results:
        # get the dictionary containing the model's field name as key.
        # range_counter in format {'range1': 1, 'range2': 2,...}
        range_counter = get_dashboard_status_range_counter(dashboard_setting, [result])
        # update the range_counter to add further details
        range_counter.update(
            {'dashboard_name': dashboard_name,
                'device_name': result['device_name'],
                'reference_name': result['name'],   # Store sector name as reference_name
                'processed_for': processed_for
            }
        )

        # prepare a list of model object.
        data_list.append(model(**range_counter))

    logger.debug("calculate_timely_sales_opportunity : data list {0}".format(data_list))
    # call method to bulk create the model object.
    bulk_update_create.delay(data_list, action='create', model=model)


def calculate_timely_latency(organizations, dashboard_name, processed_for ,technology=None):
    '''
    Method to calculate the latency status of devices.

    :param:
    organizations: list of organization.
    dashboard_name: name of dashboard used in dashboard_setting.
    processed_for: datetime.
    technology: Named Tuple.

    return:
    '''
    processed_for = processed_for
    technology_id = technology.ID if technology else None
    # get the device of user's organization [and sub organization]
    sector_devices = organization_network_devices(organizations, technology_id)
    # get the list of dictionay where 'machine__name' and 'device_name' as key of the user's device.
    sector_devices = sector_devices.filter(sector_configured_on__isnull=False).values('machine__name', 'device_name')

    # get the dictionary of machine_name as key and device_name as a list for that machine.
    machine_dict = prepare_machines(sector_devices)
    status_dict_list = []
    # creating a list dictionary using machine name and there corresponing device list.
    # And list is order by device_name.
    for machine_name, device_list in machine_dict.items():
        status_dict_list += NetworkStatus.objects.order_by('device_name').filter(device_name__in=device_list,
                service_name='ping',
                data_source='rta',
                current_value__gt=0,
                severity__in=['warning', 'critical', 'down']
            ).using(machine_name).values()

    logger.debug('calculate_timely_latency : data list {0}'.format(status_dict_list))
    calculate_timely_network_alert(dashboard_name, processed_for, technology, status_dict_list)


def calculate_timely_packet_drop(organizations, dashboard_name, processed_for, technology=None):
    '''
    Method to calculate the packed drop status of devices.

    :param:
    organizations: list of organization.
    dashboard_name: name of dashboard used in dashboard_setting.
    processed_for: datetime.
    technology: Named Tuple.

    return:
    '''
    processed_for = processed_for
    technology_id = technology.ID if technology else None
    # get the device of user's organization [and sub organization]
    sector_devices = organization_network_devices(organizations, technology_id)
    # get the list of dictionay where 'machine__name' and 'device_name' as key of the user's device.
    sector_devices = sector_devices.filter(sector_configured_on__isnull=False).values('machine__name', 'device_name')

    machine_dict = prepare_machines(sector_devices)
    status_dict_list = []
    # creating a list dictionary using machine name and there corresponing device list.
    # And list is order by device_name.
    for machine_name, device_list in machine_dict.items():
        status_dict_list += NetworkStatus.objects.order_by('device_name').filter(device_name__in=device_list,
                service_name='ping',
                data_source='pl',
                severity__in=['warning', 'critical', 'down'],
                current_value__lt=100
            ).using(machine_name).values()

    logger.debug('calculate_timely_packet_drop : data list = {0}'.format(status_dict_list))
    calculate_timely_network_alert(dashboard_name, processed_for, technology, status_dict_list)


def calculate_timely_down_status(organizations, dashboard_name, processed_for, technology=None):
    '''
    Method to calculate the down status of devices.

    :param:
    organizations: list of organization.
    dashboard_name: name of dashboard used in dashboard_setting.
    processed_for: datetime.
    technology: Named Tuple.

    return:
    '''
    processed_for = processed_for
    technology_id = technology.ID if technology else None
    # get the device of user's organization [and sub organization]
    sector_devices = organization_network_devices(organizations, technology_id)
    # get the list of dictionay where 'machine__name' and 'device_name' as key of the user's device.
    sector_devices = sector_devices.filter(sector_configured_on__isnull=False).values('machine__name', 'device_name')

    machine_dict = prepare_machines(sector_devices)
    status_dict_list = []
    # creating a list dictionary using machine name and there corresponing device list.
    # And list is order by device_name.
    for machine_name, device_list in machine_dict.items():
        status_dict_list += NetworkStatus.objects.order_by('device_name').filter(device_name__in=device_list,
                service_name='ping',
                data_source='pl',
                severity__in=['down'],
                current_value__gte=100
            ).using(machine_name).values()

    logger.debug('calculate_timely_down_status : data list = {0}'.format(status_dict_list))
    calculate_timely_network_alert(dashboard_name, processed_for, technology, status_dict_list)


def calculate_timely_temperature(organizations, processed_for, chart_type='IDU'):
    '''
    Method to calculate the temperature status of devices.

    :param:
    organizations: list of organization.
    processed_for: datetime.
    chart_type: string.

    return:
    '''
    technology_id = 3
    processed_for=processed_for

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

    # get the device of user's organization [and sub organization]
    sector_devices = organization_network_devices(organizations, technology_id)
    # get the list of dictionay where 'machine__name' and 'device_name' as key of the user's device.
    sector_devices = sector_devices.filter(sector_configured_on__isnull=False).values('machine__name', 'device_name')

    machine_dict = prepare_machines(sector_devices)
    status_dict_list = []
    # creating a list dictionary using machine name and there corresponing device list.
    # And list is order by device_name.
    for machine_name, device_list in machine_dict.items():
        status_dict_list += NetworkStatus.objects.order_by('device_name').filter(device_name__in=device_list,
                service_name__in=service_list,
                data_source__in=data_source_list,
                severity__in=['warning', 'critical']
            ).using(machine_name).values()

    logger.debug('calculate_timely_temperature : data list = {0}'.format(status_dict_list))
    calculate_timely_network_alert('temperature', processed_for, WiMAX, status_dict_list, status_dashboard_name)


def calculate_timely_network_alert(dashboard_name, processed_for, technology=None, status_dict_list=[], status_dashboard_name=None):
    '''
    prepare a list of model object to bulk create the model objects.

    :param:
    dashboard_name: name of dashboard used in dashboard_setting.
    processed_for: datetime
    technology: Named Tuple
    status_dict_list: list of dictionay.
    status_dashboard_name: string

    return:
    '''
    technology_id = technology.ID if technology else None
    try:
        dashboard_setting = DashboardSetting.objects.get(technology_id=technology_id,
                page_name='main_dashboard', name=dashboard_name, is_bh=False)
    except DashboardSetting.DoesNotExist as e:
        logger.info(" Dashboard Setting of %s is not available." % dashboard_name)
        return None

    data_list = []
    device_name = ''
    device_result = []
    processed_for = processed_for

    if status_dashboard_name is None:
        status_dashboard_name = dashboard_name

    # status_dict_list is a ordered list of dictionay which is ordered by device_name.
    for result_dict in status_dict_list:
        # Creating list for same device_name to collectively get the status_range_counter of same devices.
        if device_name == result_dict['device_name']:
            device_result.append(result_dict)
        else:
            # Creating a list of model object for a list of same devices.
            if device_result:
                # get the dictionay where keys are same as of the model fields.
                dashboard_data_dict = get_dashboard_status_range_counter(dashboard_setting, device_result)
                # updating the dictionay with some other fields used in model.
                dashboard_data_dict.update({'device_name': device_name, 'reference_name': device_name,
                    'dashboard_name': status_dashboard_name, 'processed_for': processed_for})
                # creating a list of model object for bulk create.
                data_list.append(DashboardRangeStatusTimely(**dashboard_data_dict))

            # assign the new device name to device_name.
            device_name = result_dict['device_name']
            # creating new list for the new device.
            # so that again we can collectively get the status_range_counter for new device.
            device_result = [result_dict]
    # creating the list of model object for the final list of the device name of status_dict_list.
    if device_result:
        # get the dictionay where keys are same as of the model fields.
        dashboard_data_dict = get_dashboard_status_range_counter(dashboard_setting, device_result)
        # updating the dictionay with some other fields used in model.
        dashboard_data_dict.update({'device_name': result_dict['device_name'], 'reference_name': result_dict['device_name'],
            'dashboard_name': status_dashboard_name, 'processed_for': processed_for})
        # creating a list of model object for bulk create.
        data_list.append(DashboardRangeStatusTimely(**dashboard_data_dict))

    #logger.info("CELERYBEAT: Timely: ")
    bulk_update_create.delay(data_list, action='create', model=DashboardRangeStatusTimely)


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
    #Creating the machine as a key and device_name as a list for that machine.
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

    logger.info("CELERYBEAT: Hourly: starts at ", now)
    calculate_hourly_severity_status(now)
    calculate_hourly_range_status(now)
    logger.info("CELERYBEAT: Hourly: ends at ", timezone.now())


def calculate_hourly_severity_status(now):
    '''
    Calculate the status of dashboard from DashboardSeverityStatusTimely model
    and create list of DashboardSeverityStatusHourly model object for calculated data
    and then delete all data from the DashboardSeverityStatusTimely model.

    :param now: datetime (example: timezone.now())

    return:
    '''
    # get all data from the model order by 'dashboard_name' and 'device_name'.
    last_hour_timely_severity_status = DashboardSeverityStatusTimely.objects.order_by('dashboard_name',
            'device_name').filter(processed_for__lt=now)

    hourly_severity_status_list = []    # list for the DashboardSeverityStatusHourly model object
    hourly_severity_status = None
    dashboard_name = ''
    device_name = ''

    for timely_severity_status in last_hour_timely_severity_status:
        # Sum the status value for the same dashboard_name and device_name.
        if dashboard_name == timely_severity_status.dashboard_name and device_name == timely_severity_status.device_name:
            hourly_severity_status = sum_severity_status(hourly_severity_status, timely_severity_status)
        else:
            # Create new model object when dashboard_name and device_name are different from previous dashboard_name and device_name.
            hourly_severity_status = DashboardSeverityStatusHourly(
                dashboard_name=timely_severity_status.dashboard_name,
                device_name=timely_severity_status.device_name,
                reference_name=timely_severity_status.reference_name,
                processed_for=now,
                warning=timely_severity_status.warning,
                critical=timely_severity_status.critical,
                ok=timely_severity_status.ok,
                down=timely_severity_status.down,
                unknown=timely_severity_status.unknown
            )
            # append in list for every new dashboard_name and device_name.
            hourly_severity_status_list.append(hourly_severity_status)
            # assign new dashboard_name and device_name.
            dashboard_name = timely_severity_status.dashboard_name
            device_name = timely_severity_status.device_name

    bulk_update_create.delay(hourly_severity_status_list, action='create', model=DashboardSeverityStatusHourly)

    # delete the data from the DashboardSeverityStatusTimely model.
    last_hour_timely_severity_status.delete()


def calculate_hourly_range_status(now):
    '''
    Calculate the status of dashboard from DashboardRangeStatusTimely model
    and create list of DashboardRangeStatusHourly model object for calculated data
    and then delete all data from the DashboardRangeStatusTimely model.

    :param now: datetime (example: timezone.now())

    return:
    '''
    # get all data from the model order by 'dashboard_name' and 'device_name'.
    last_hour_timely_range_status = DashboardRangeStatusTimely.objects.order_by('dashboard_name',
            'device_name').filter(processed_for__lt=now)

    hourly_range_status_list = []   # list for the DashboardRangeStatusHourly model object
    hourly_range_status = None
    dashboard_name = ''
    device_name = ''
    for timely_range_status in last_hour_timely_range_status:
        # Sum the status value for the same dashboard_name and device_name.
        if dashboard_name == timely_range_status.dashboard_name and device_name == timely_range_status.device_name:
            hourly_range_status = sum_range_status(hourly_range_status, timely_range_status)
        else:
            # Create new model object when dashboard_name and device_name are different from previous dashboard_name and device_name.
            hourly_range_status = DashboardRangeStatusHourly(
                dashboard_name=timely_range_status.dashboard_name,
                device_name=timely_range_status.device_name,
                reference_name=timely_range_status.reference_name,
                processed_for=now,
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
            # append in list for every new dashboard_name and device_name.
            hourly_range_status_list.append(hourly_range_status)
            # assign new dashboard_name and device_name.
            dashboard_name = timely_range_status.dashboard_name
            device_name = timely_range_status.device_name

    bulk_update_create.delay(hourly_range_status_list, action='create', model=DashboardRangeStatusHourly)

    # delete the data from the DashboardRangeStatusTimely model.
    last_hour_timely_range_status.delete()


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

    logger.info("CELERYBEAT: Daily: starts at ", now)
    calculate_daily_severity_status(now)
    calculate_daily_range_status(now)
    logger.info("CELERYBEAT: Daily: ends at ", timezone.now())


def calculate_daily_severity_status(now):
    '''
    Calculate the status of dashboard from DashboardSeverityStatusHourly model
    and create list of DashboardSeverityStatusDaily model object for calculated data
    and then delete all data from the DashboardSeverityStatusHourly model.

    :param now: datetime (example: timezone.now())

    return:
    '''
    # get the current timezone.
    tzinfo = timezone.get_current_timezone()
    # get today date according to current timezone and reset time to 12 o'clock.
    today = timezone.datetime(now.year, now.month, now.day, tzinfo=tzinfo)
    previous_day = now - timezone.timedelta(days=1)
    yesterday = timezone.datetime(previous_day.year, previous_day.month, previous_day.day, tzinfo=tzinfo)
    # get all result of yesterday only and order by 'dashboard_name' and'device_name'
    last_day_timely_severity_status = DashboardSeverityStatusHourly.objects.order_by('dashboard_name',
            'device_name').filter(processed_for__gte=yesterday, processed_for__lt=today)

    daily_severity_status_list = []     # list for the DashboardSeverityStatusDaily model object
    daily_severity_status = None
    dashboard_name = ''
    device_name = ''
    for hourly_severity_status in last_day_timely_severity_status:
        if dashboard_name == hourly_severity_status.dashboard_name and device_name == hourly_severity_status.device_name:
            daily_severity_status = sum_severity_status(daily_severity_status, hourly_severity_status)
        else:
            daily_severity_status = DashboardSeverityStatusDaily(
                dashboard_name=hourly_severity_status.dashboard_name,
                device_name=hourly_severity_status.device_name,
                reference_name=hourly_severity_status.reference_name,
                processed_for=yesterday,
                warning=hourly_severity_status.warning,
                critical=hourly_severity_status.critical,
                ok=hourly_severity_status.ok,
                down=hourly_severity_status.down,
                unknown=hourly_severity_status.unknown
            )
            daily_severity_status_list.append(daily_severity_status)
            dashboard_name = hourly_severity_status.dashboard_name
            device_name = hourly_severity_status.device_name

    bulk_update_create.delay(daily_severity_status_list, action='create', model=DashboardSeverityStatusDaily)

    last_day_timely_severity_status.delete()


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
    today = timezone.datetime(now.year, now.month, now.day, tzinfo=tzinfo)
    previous_day = now - timezone.timedelta(days=1)
    yesterday = timezone.datetime(previous_day.year, previous_day.month, previous_day.day, tzinfo=tzinfo)
    # get all result of yesterday only and order by 'dashboard_name' and'device_name'
    last_day_hourly_range_status = DashboardRangeStatusHourly.objects.order_by('dashboard_name',
            'device_name').filter(processed_for__gte=yesterday, processed_for__lt=today)

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
                reference_name=hourly_range_status.reference_name,
                processed_for=yesterday,
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
            dashboard_name = hourly_range_status.dashboard_name
            device_name = hourly_range_status.device_name

    bulk_update_create.delay(daily_range_status_list, action='create', model=DashboardRangeStatusDaily)

    last_day_hourly_range_status.delete()


@task()
def calculate_weekly_main_dashboard():
    '''
    Task to calculate the weekly status of main dashboard.
    '''
    logger.info("CELERYBEAT: Weekly: starts at ", timezone.now())
    tzinfo = timezone.get_current_timezone()
    previous_day = timezone.datetime.today() - timezone.timedelta(days=1)
    previous_day = timezone.datetime(previous_day.year, previous_day.month, previous_day.day, tzinfo=tzinfo) # Reset to 12 o'clock
    first_day = previous_day - timezone.timedelta(previous_day.weekday()) # First Day of Week [Date of Monday]
    first_day = timezone.datetime(first_day.year, first_day.month, first_day.day, tzinfo=tzinfo) # Reset to 12 o'clock

    calculate_weekly_severity_status(previous_day, first_day)
    calculate_weekly_range_status(previous_day, first_day)
    logger.info("CELERYBEAT: Weekly: ends at ", timezone.now())


def calculate_weekly_severity_status(day, first_day):
    '''
    Calculate the status of dashboard from DashboardSeverityStatusDaily model
    and create list of DashboardSeverityStatusWeekly model object for calculated data
    and result's processed_for date will be first day of week (i.e date of monday)

    :param day: datetime - previous day of today
    :param first_day: datetime - first day of Week(Date of Monday)

    return:
    '''
    # get all result of day and order by 'dashboard_name' and'device_name'
    last_week_daily_severity_status = DashboardSeverityStatusDaily.objects.order_by('dashboard_name',
            'device_name').filter(processed_for=day)

    weekly_severity_status_list = []
    weekly_severity_status = None
    # check if the day is monday or not.
    is_monday = True if day.weekday() == 0 else False
    for daily_severity_status in last_week_daily_severity_status:
        # Creating object for the processed_for date of monday.
        if is_monday:
            weekly_severity_status = DashboardSeverityStatusWeekly(
                dashboard_name=daily_severity_status.dashboard_name,
                device_name=daily_severity_status.device_name,
                reference_name=daily_severity_status.reference_name,
                processed_for=first_day,
                warning=daily_severity_status.warning,
                critical=daily_severity_status.critical,
                ok=daily_severity_status.ok,
                down=daily_severity_status.down,
                unknown=daily_severity_status.unknown
            )
        # getting object where processed_for is monday of that week or creating object for the same.
        else:
            weekly_severity_status, created  = DashboardSeverityStatusWeekly.objects.get_or_create(
                dashboard_name=daily_severity_status.dashboard_name,
                device_name=daily_severity_status.device_name,
                processed_for=first_day
            )
            weekly_severity_status = sum_severity_status(weekly_severity_status, daily_severity_status)
        weekly_severity_status_list.append(weekly_severity_status)

    # Create the bulk object if day is monday else bulk update the model.
    if is_monday:
        bulk_update_create.delay(weekly_severity_status_list, action='create', model=DashboardSeverityStatusWeekly)
    else:
        bulk_update_create.delay(weekly_severity_status_list)


def calculate_weekly_range_status(day, first_day):
    '''
    Calculate the status of dashboard from DashboardRangeStatusDaily model
    and create list of DashboardRangeStatusWeekly model object for calculated data
    and result's processed_for date will be first day of week (i.e date of monday)

    :param day: datetime - previous day of today
    :param first_day: datetime - first day of Week(Date of Monday)

    return:
    '''
    # get all result of day and order by 'dashboard_name' and'device_name'
    last_week_daily_range_status = DashboardRangeStatusDaily.objects.order_by('dashboard_name',
            'device_name').filter(processed_for=day)

    weekly_range_status_list = []
    weekly_range_status = None
    # check if the day is monday or not.
    is_monday = True if day.weekday() == 0 else False
    for daily_range_status in last_week_daily_range_status:
        # Creating object for the processed_for date of monday.
        if is_monday:
            weekly_range_status = DashboardRangeStatusWeekly(
                dashboard_name=daily_range_status.dashboard_name,
                device_name=daily_range_status.device_name,
                reference_name=daily_range_status.reference_name,
                processed_for=first_day,
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
        # getting object where processed_for is monday of that week or creating object for the same.
        else:
            weekly_range_status, created = DashboardRangeStatusWeekly.objects.get_or_create(
                dashboard_name=daily_range_status.dashboard_name,
                device_name=daily_range_status.device_name,
                processed_for=first_day,
            )
            weekly_range_status = sum_range_status(weekly_range_status, daily_range_status)
        weekly_range_status_list.append(weekly_range_status)

    # Create the bulk object if day is monday else bulk update the model.
    if is_monday:
        bulk_update_create.delay(weekly_range_status_list, action='create', model=DashboardRangeStatusWeekly)
    else:
        bulk_update_create.delay(weekly_range_status_list)


@task()
def calculate_monthly_main_dashboard():
    """
    Task to calculate the monthly status of main dashboard.
    """
    now = timezone.now()
    logger.info("CELERYBEAT: Monthly: starts at ", now)
    tzinfo = timezone.get_current_timezone()
    previous_day = timezone.datetime.today() - timezone.timedelta(days=1)
    previous_day = timezone.datetime(previous_day.year, previous_day.month, previous_day.day, tzinfo=tzinfo) # Reset to 12 o'clock
    first_day = timezone.datetime(previous_day.year, previous_day.month, 1, tzinfo=timezone.get_current_timezone())

    calculate_monthly_severity_status(previous_day, first_day)
    calculate_monthly_range_status(previous_day, first_day)
    logger.info("CELERYBEAT: Monthly: ends at ", timezone.now())


def calculate_monthly_range_status(day, first_day):
    '''
    Calculate the status of dashboard from DashboardRangeStatusDaily model
    and create list of DashboardRangeStatusMonthly model object for calculated data
    and result's processed_for date will be first day of month.

    :param day: datetime - previous day of today
    :param first_day: datetime - first day of month.

    return:
    '''
    # get all result of day and order by 'dashboard_name' and'device_name'
    last_month_daily_range_status = DashboardRangeStatusDaily.objects.order_by('dashboard_name',
            'device_name').filter(processed_for=day)

    monthly_range_status_list = []
    monthly_range_status = None
    # check if the day is first day of month or not.
    is_first_day_of_month = True if day.day == 1 else False
    for daily_range_status in last_month_daily_range_status:
        # getting object where processed_for is first day of month or creating object for the same.
        if not is_first_day_of_month:
            monthly_range_status, created = DashboardRangeStatusMonthly.objects.get_or_create(
                dashboard_name=daily_range_status.dashboard_name,
                device_name=daily_range_status.device_name,
                processed_for=first_day
            )
            monthly_range_status = sum_range_status(monthly_range_status, daily_range_status)
            # monthly_range_status.save() # Save later so current process doesn't slow.
        # Creating object for the processed_for date of first day of month.
        else:
            monthly_range_status = DashboardRangeStatusMonthly(
                dashboard_name=daily_range_status.dashboard_name,
                device_name=daily_range_status.device_name,
                reference_name=daily_range_status.reference_name,
                processed_for=first_day,
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
        monthly_range_status_list.append(monthly_range_status)

    if is_first_day_of_month:
        bulk_update_create.delay(monthly_range_status_list, action='create', model=DashboardRangeStatusMonthly)
    else:
        bulk_update_create.delay(monthly_range_status_list)


def calculate_monthly_severity_status(day, first_day):
    '''
    Calculate the status of dashboard from DashboardSeverityStatusDaily model
    and create list of DashboardSeverityStatusMonthly model object for calculated data
    and result's processed_for date will be first day of month.

    :param day: datetime - previous day of today
    :param first_day: datetime - first day of month.

    return:
    '''
    # get all result of day and order by 'dashboard_name' and'device_name'
    last_month_daily_severity_status = DashboardSeverityStatusDaily.objects.order_by('dashboard_name',
            'device_name').filter(processed_for=day)

    monthly_severity_status_list = []
    monthly_severity_status = None
    # check if the day is first day of month or not.
    is_first_day_of_month = True if day.day == 1 else False
    for daily_severity_status in last_month_daily_severity_status:
        # getting object where processed_for is first day of month or creating object for the same.
        if not is_first_day_of_month:
            monthly_severity_status, created = DashboardSeverityStatusMonthly.objects.get_or_create(
                dashboard_name=daily_severity_status.dashboard_name,
                device_name=daily_severity_status.device_name,
                processed_for=first_day
            )
            monthly_severity_status = sum_severity_status(monthly_severity_status, daily_severity_status)
            # monthly_severity_status.save() # Save later so current process doesn't slow.
        # Creating object for the processed_for date of first day of month.
        else:
            monthly_severity_status = DashboardSeverityStatusMonthly(
                dashboard_name=daily_severity_status.dashboard_name,
                device_name=daily_severity_status.device_name,
                reference_name=daily_severity_status.reference_name,
                processed_for=first_day,
                warning=daily_severity_status.warning,
                critical=daily_severity_status.critical,
                ok=daily_severity_status.ok,
                down=daily_severity_status.down,
                unknown=daily_severity_status.unknown
            )
        monthly_severity_status_list.append(monthly_severity_status)

    if is_first_day_of_month:
        bulk_update_create.delay(monthly_severity_status_list, action='create', model=DashboardSeverityStatusMonthly)
    else:
        bulk_update_create.delay(monthly_severity_status_list)


@task()
def calculate_yearly_main_dashboard():
    """
    Task to calculate the yearly status of main dashboard.
    """
    now = timezone.now()
    logger.info("CELERYBEAT: Yearly: starts at ", now)
    tzinfo = timezone.get_current_timezone()
    previous_day = timezone.datetime.today() - timezone.timedelta(days=1)
    previous_day = timezone.datetime(previous_day.year, previous_day.month, previous_day.day, tzinfo=tzinfo) # Reset to 12 o'clock
    first_month = timezone.datetime(previous_day.year, 1, previous_day.day, tzinfo=timezone.get_current_timezone())

    calculate_yearly_severity_status(previous_day, first_month)
    calculate_yearly_range_status(previous_day, first_month)
    logger.info("CELERYBEAT: Yearly: ends at ", timezone.now())


def calculate_yearly_range_status(day, first_month):
    '''
    Calculate the status of dashboard from DashboardRangeStatusMonthly model
    and create list of DashboardRangeStatusYearly model object for calculated data
    and result's processed_for date will be first day of month.

    :param day: datetime - previous day of today
    :param first_month: datetime - first month of today's year.

    return:
    '''
    # get all result of day and order by 'dashboard_name' and'device_name'
    last_year_monthly_range_status = DashboardRangeStatusMonthly.objects.order_by('dashboard_name',
            'device_name').filter(processed_for__year=day.year)

    yearly_range_status_list = []
    yearly_range_status = None
    # check if the day of the month is january or not.
    is_january = True if day.month == 1 else False
    for monthly_range_status in last_year_monthly_range_status:
        # getting object where processed_for is first month or creating object for the same.
        if not is_january:
            yearly_range_status, created = DashboardRangeStatusYearly.objects.get_or_create(
                dashboard_name=monthly_range_status.dashboard_name,
                device_name=monthly_range_status.device_name,
                processed_for=first_month
            )
            yearly_range_status = sum_range_status(yearly_range_status, monthly_range_status)
            # yearly_range_status.save() # Save later so current process doesn't slow.
        # Creating object for the processed_for date of first month.
        else:
            yearly_range_status = DashboardRangeStatusYearly(
                dashboard_name=monthly_range_status.dashboard_name,
                device_name=monthly_range_status.device_name,
                reference_name=monthly_range_status.reference_name,
                processed_for=first_month,
                range1=monthly_range_status.range1,
                range2=monthly_range_status.range2,
                range3=monthly_range_status.range3,
                range4=monthly_range_status.range4,
                range5=monthly_range_status.range5,
                range6=monthly_range_status.range6,
                range7=monthly_range_status.range7,
                range8=monthly_range_status.range8,
                range9=monthly_range_status.range9,
                range10=monthly_range_status.range10,
                unknown=monthly_range_status.unknown
            )
        yearly_range_status_list.append(yearly_range_status)

    if is_january:
        bulk_update_create.delay(yearly_range_status_list, action='create', model=DashboardRangeStatusYearly)
    else:
        bulk_update_create.delay(yearly_range_status_list)


def calculate_yearly_severity_status(day, first_month):
    '''
    Calculate the status of dashboard from DashboardSeverityStatusMonthly model
    and create list of DashboardSeverityStatusYearly model object for calculated data
    and result's processed_for date will be first day of month.

    :param day: datetime - previous day of today
    :param first_month: datetime - first month of today's year.

    return:
    '''
    # get all result of day and order by 'dashboard_name' and'device_name'
    last_year_monthly_severity_status = DashboardSeverityStatusMonthly.objects.order_by('dashboard_name',
            'device_name').filter(processed_for__year=day.year)

    yearly_severity_status_list = []
    yearly_severity_status = None
    is_january = True if day.month == 1 else False
    # check if the day of the month is january or not.
    for monthly_severity_status in last_year_monthly_severity_status:
        # getting object where processed_for is first month or creating object for the same.
        if not is_january:
            yearly_severity_status, created = DashboardSeverityStatusYearly.objects.get_or_create(
                dashboard_name=monthly_severity_status.dashboard_name,
                device_name=monthly_severity_status.device_name,
                processed_for=first_month
            )
            yearly_severity_status = sum_severity_status(yearly_severity_status, monthly_severity_status)
            # yearly_severity_status.save() # Save later so current process doesn't slow.
        # Creating object for the processed_for date of first month.
        else:
            yearly_severity_status = DashboardSeverityStatusYearly(
                dashboard_name=monthly_severity_status.dashboard_name,
                device_name=monthly_severity_status.device_name,
                reference_name=monthly_severity_status.reference_name,
                processed_for=first_month,
                warning=monthly_severity_status.warning,
                critical=monthly_severity_status.critical,
                ok=monthly_severity_status.ok,
                down=monthly_severity_status.down,
                unknown=monthly_severity_status.unknown
            )
        yearly_severity_status_list.append(yearly_severity_status)

    if is_january:
        bulk_update_create.delay(yearly_severity_status_list, action='create', model=DashboardSeverityStatusYearly)
    else:
        bulk_update_create.delay(yearly_severity_status_list)