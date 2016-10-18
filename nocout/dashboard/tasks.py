from celery import task, group

from django.db.models import Q, Avg, Sum, Max
from django.utils import timezone
import datetime

# nocout project settings # TODO: Remove the HARDCODED technology IDs
from nocout.settings import P2P, PMP, WiMAX, TCLPOP, DEBUG, SPEEDOMETER_DASHBAORDS

from organization.models import Organization
from device.models import DeviceTechnology, Device
from capacity_management.models import SectorCapacityStatus, BackhaulCapacityStatus
from performance.models import Topology, NetworkStatus, ServiceStatus, NetworkAvailabilityDaily
from dashboard.models import (DashboardSetting, DashboardSeverityStatusTimely, DashboardSeverityStatusHourly,
        DashboardSeverityStatusDaily, DashboardSeverityStatusWeekly, DashboardSeverityStatusMonthly,
        DashboardSeverityStatusYearly, DashboardRangeStatusTimely, DashboardRangeStatusHourly, DashboardRangeStatusDaily,
        DashboardRangeStatusWeekly, DashboardRangeStatusMonthly, DashboardRangeStatusYearly,
    )

import math

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

# Import inventory utils gateway class
from inventory.utils.util import InventoryUtilsGateway

from inventory.models import get_default_org, Circuit

from inventory.tasks import bulk_update_create

from dashboard.utils import \
    get_dashboard_status_range_counter, \
    get_service_status_results, \
    get_total_connected_device_per_sector


import logging
logger = logging.getLogger(__name__)


@task()
def network_speedometer_dashboards():
    """
    This Function calls from settings file of Project and initialise the values of speedometer dashboard 
    configs (Except Temperature dashboard) and divide the celery tasks according to Number of organizations 
    and Dashboard configs per organization for further calculations. 

    :Args: 
        No input Arguments

    :return:
        True/False
    """
    g_jobs = list()
    ret = False
    # Query set for fetching all orgnizations
    user_organizations = Organization.objects.all()
    processed_for = timezone.now()

    # Defining Speedometer Dashboard Configs
    network_dashboards = {
        'latency-network': {
            'model': NetworkStatus,
            'data_source': 'rta',
            'service_name': 'ping',
            'severity': ['warning', 'critical', 'down'],
            'current_value': ' current_value > 0 '
        },
        'packetloss-network': {
            'model': NetworkStatus,
            'data_source': 'pl',
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
    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    for organization in user_organizations:
        # Fetching devices for particular organization & Technology (this will give PMP and WiMAX devices)
        required_devices = inventory_utils.organization_network_devices(
            organizations=[organization.id],
            technology=None,
            specify_ptp_bh_type=None
        )  

        if not required_devices.exists():  # this evaluates the query set
            continue

        sector_devices = required_devices.filter(~Q(machine__name='default')).values('machine__name', 'device_name')
        # Function for distributing devices according to their corresponding machine
        machine_dict = prepare_machines(sector_devices)
    
        for dashboard in network_dashboards:
            # Appending Jobs for dashboard configs per organization
            g_jobs.append(
                prepare_network_alert.s(
                    organization=organization,
                    dashboard_name=dashboard,
                    processed_for=processed_for,
                    dashboard_config=network_dashboards,
                    technology=None,
                    machine_dict=machine_dict
                )
            )

    if not len(g_jobs):
        return ret

    job = group(g_jobs)
    result = job.apply_async()  # start the jobs
    # for r in result.get():
    #     ret |= r
    return True


@task()
def temperature_speedometer_dashboards():
    """
    This Function calls from settings file of Project and initialise temperature speedometer dashboard 
    and divide the celery tasks according to Number of organizations and No. of Dashboards per 
    organization for further calculations.

    :Args: 
        No input Arguments

    :return:
        True/False
    """
    g_jobs = list()
    ret = False
    # Query set for fetching all orgnizations
    user_organizations = Organization.objects.all()
    processed_for = timezone.now()

    temperatures = ['IDU']
    if DEBUG:
        temperatures = ['IDU', 'ACB', 'FAN']

    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    for organization in user_organizations:
        # Query set for devices as per organization & Technology (In this case technology = WiMAX)
        required_devices = inventory_utils.organization_network_devices(
            organizations=[organization.id],
            technology=WiMAX.ID,
            specify_ptp_bh_type=None
        )
        if required_devices.exists():
            sector_devices = required_devices.values('machine__name', 'device_name')
            machine_dict = prepare_machines(sector_devices)
            for temp in temperatures:
                # Appending Jobs for all temperature dashboard per organization
                g_jobs.append(
                    calculate_timely_temperature.s(
                        organization=organization,
                        processed_for=processed_for,
                        machine_dict=machine_dict,
                        chart_type=temp
                    )
                )
    if not len(g_jobs):
        return ret

    job = group(g_jobs)
    result = job.apply_async()  # start the jobs
    # for r in result.get():
    #     ret |= r
    return True


@task()
def calculate_status_dashboards(technology):
    """
    This Function calls from settings file of Project and initialise speedometer dashboard for 
    particular technology and divide the celery tasks according to Number of organizations 
    and No. of Dashboards per organization for further calculations.

    :Args: 
        technology : PMP/WiMAX

    :return:
        True/False
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
    # Query set for fetching all organizations
    user_organizations = Organization.objects.all()
    processed_for = timezone.now()
    # Defining Dashboards Config for particular technology
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
            'data_source': 'pl',
            'service_name': 'ping',
            'severity': ['warning', 'critical', 'down'],
            'current_value': ' current_value BETWEEN 0 AND 99 '
        },
        "down-{0}".format(technology): {
            'model': NetworkStatus,
            'data_source': 'pl',
            'service_name': 'ping',
            'severity': ['critical', 'down'],
            'current_value': ' current_value >= 100 '
        }
    }

    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    for organization in user_organizations:
        # Query set for gettinf devices are per organization & Technology
        required_devices = inventory_utils.organization_network_devices(
            organizations=[organization.id],
            technology=tech_id,
            specify_ptp_bh_type=None
        )
        if required_devices.exists():
            sector_devices = required_devices.values('machine__name', 'device_name')
            # Function for distributing devices according to there corresponding machine
            machine_dict = prepare_machines(sector_devices)
            for dashboard in dashboards:
                # Appeding Jobs for all dashboards config per organization
                g_jobs.append(
                    prepare_network_alert.s(
                        organization=organization,
                        dashboard_name=dashboard,
                        processed_for=processed_for,
                        dashboard_config=dashboards,
                        technology=technology,
                        machine_dict=machine_dict
                    )
                )

    if not len(g_jobs):
        return ret

    job = group(g_jobs)
    result = job.apply_async()  # start the jobs
    # for r in result.get():
    #     ret |= r
    return True


@task()
def calculate_range_dashboards(technology, type):
    """
    This Function calls from settings file Project and initialise Sector Capacity & Sales Opportunity 
    dashboards for particular technology and divide the celery tasks according to No. of Dashboards 
    for further calculations.

    :Args: 
        technology : PMP/WiMAX/TCLPOP
        type : sector/backhaul

    :return:
        True/False
    """
    g_jobs = list()
    ret = False
    # Query set for fetching all orgnizations
    user_organizations = Organization.objects.all()
    processed_for = timezone.now()

    tech = technology
    # Diffrent celery task functions for different types ("sector"/"backhaul")
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

    if not len(g_jobs):
        return ret

    job = group(g_jobs)
    result = job.apply_async()  # start the jobs
    # for r in result.get():
    #     ret |= r
    return True


@task()
def calculate_timely_sector_capacity(organizations, technology, model, processed_for):
    """
    This is celery task function which insert Bulk entries in table/model as per calculation of particular Dashboard & Technology.

    :Args:
        organizations : object of all organizations 
        technology : PMP/WiMAX
        model : DashboardSeverityStatusTimely
        processed_for : Datetime Field 

    :return:
        True/False
    """
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
        max_timestamp = None
        try:
            max_timestamp = SectorCapacityStatus.objects.filter(
                Q(organization__in=[organization]),
                Q(severity__in=['warning', 'critical'])
            ).aggregate(Max('sys_timestamp'))['sys_timestamp__max']
        except Exception, e:
            logger.error('Sector Capacity MAX Timestamp Exception --------')
            logger.error(e)
            logger.error('Sector Capacity MAX Timestamp Exception --------')
            pass

        sector_objects = SectorCapacityStatus.objects.filter(
            Q(organization__in=[organization]),
            Q(sector__sector_configured_on__device_technology=sector_technology.ID),
            Q(severity__in=['warning', 'critical', 'ok', 'unknown'])
        )


        if sector_objects.exists():
            # Create the range_counter dictionay containg the model's field name as key
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
                if item['severity'].strip().lower() in ['warning', 'critical']:
                    # Update the range_counter on the basis of severity.
                    if max_timestamp and float(item['sys_timestamp']) >= float(max_timestamp) - 420:
                        range_counter[item['severity'].strip().lower()] += 1
                elif item['severity'].strip().lower() == 'ok':
                    range_counter['ok'] += 1
                else:
                    range_counter['unknown'] += 1
            # Create the list of model object.
            bulk_data_list.append(model(**range_counter))

            if len(bulk_data_list):
                # call the method to bulk create the objects.
                bulk_update_create.delay(
                    bulky=bulk_data_list,
                    action='create',
                    model=model)
    return True


@task()
def calculate_timely_backhaul_capacity(organizations, technology, model, processed_for):
    """
    This is celery task function which insert Bulk entries in table/model as per calculation of particular Dashboard & Technology.

    :Args:
        organizations : object of all organizations 
        model : DashboardSeverityStatusTimely
        processed_for : Datetime Field 

    :return:
        True/False
    """
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
            # Create the range_counter dictionay containg the model's field name as key
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
                # if (item['age'] <= item['sys_timestamp'] - 600) and (item['severity'].strip().lower() in ['warning', 'critical']):
                if item['severity'].strip().lower() in ['warning', 'critical']:
                    # Update the range_counter on the basis of severity.
                    range_counter[item['severity'].strip().lower()] += 1
                elif item['severity'].strip().lower() == 'ok':
                    range_counter['ok'] += 1
                else:
                    range_counter['unknown'] += 1

            # Create the list of model object.
            data_list.append(model(**range_counter))

            if len(data_list):
                # call the method to bulk create the objects.
                bulk_update_create.delay(
                    bulky=data_list,
                    action='create',
                    model=model)

    return True


@task()
def calculate_timely_sales_opportunity(organizations, technology, model, processed_for):
    """
    This is celery task function which insert Bulk entries in table/model as per calculation of particular Dashboard & Technology.

    :Args:
        organizations : object of all organizations 
        technology : PMP/WiMAX
        model : DashboardRangeStatusTimely
        processed_for : Datetime Field 

    :return:
        True/False
    """
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

    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    for organization in organizations:

        # get the sector of User's Organization [and Sub Organization]
        sector_objects = inventory_utils.organization_sectors([organization], technology_id)
        
        if sector_objects.exists():
            data_list = list()
            user_sector = sector_objects.values_list('sector_id', flat=True)
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
            # get the list of dictionary of count of connected device IP for each and every sector
            service_status_results = get_total_connected_device_per_sector(
                user_sector=user_sector
                )

            for result in service_status_results:
                # get the dictionary containing hits for all ranges according to range define in dashboard settings for particular dashboards.
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
                          machine_dict,
                          technology=None,
                          ):
    """
    This is celery task function which count the no. of devices in model as per given conditions 
    of organizations, dashboard configs in different databases and open another celery job after 
    this calculation.

    :Args:
        organizations : object of all organizations 
        dashboard_name : name of Dashboard (Key of dashboard config)
        processed_for : datetime field 
        dashboard_config : parameters of all dashboards
        machine_dict : dict (key : value) key = machine name, value = list of all devices corresponding to that machine.
        technology : PMP/WiMAX

    :return:
        True/False
    """
    processed_for = processed_for
    technology_id = None

    if technology:
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

    if not machine_dict:
        return ret

    machine_dict = machine_dict
    # Intialisation of all variables
    status_count = 0
    service_status_results = list()
    result = dict()
    result['current_value'] = 0
    # Extracting all parameters from dashboard config corresponding to particular dashboard name
    model = dashboard_config[dashboard_name]['model']
    service_name = dashboard_config[dashboard_name]['service_name']
    data_source = dashboard_config[dashboard_name]['data_source']
    severity = dashboard_config[dashboard_name]['severity']
    current_value = dashboard_config[dashboard_name]['current_value']

    for machine_name, device_list in machine_dict.items():
        # Query set for count of all devices as per conditions on particular dashboards for different databases.
        status_count += model.objects.order_by(
        ).extra(
            where=[current_value]
        ).filter(
            device_name__in=list(set(device_list)),
            service_name=service_name,
            data_source=data_source,
            severity__in=severity
        ).using(machine_name).count()

    result['current_value'] = status_count
    service_status_results.append(result)
    # Appending to new job for further calculation
    g_jobs.append(
        calculate_timely_network_alert.s(
            dashboard_name=dashboard_name,
            processed_for=processed_for,
            organization=organization,
            technology=technology,
            service_status_results=service_status_results,
            status_dashboard_name=None
        )
    )

    if not len(g_jobs):
        return ret

    job = group(g_jobs)
    result = job.apply_async()  # start the jobs
    # for r in result.get():
    #     ret |= r
    return True


@task()
def calculate_timely_temperature(organization, processed_for, machine_dict, chart_type='IDU'):
    """
    This is celery task function which count the no. of devices in ServiceStatus table as per given 
    conditions of chart_type, severity in different databases and open another celery job after 
    this calculation.

    :Args:
        organizations : object of all organizations 
        processed_for : datetime field 
        machine_dict : dict (key : value) key = machine name, value = list of all devices corresponding to that machine.
        chart_type : IDU,ACB,FAN

    :return:
        True/False
    """

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
    # Initialisation of variables
    g_jobs = list()
    ret = False
    # WiNAX Technology have id = 3
    technology_id = 3
    processed_for = processed_for
    status_dashboard_name = 'temperature-' + chart_type.lower()
    machine_dict = machine_dict
    # count of devices in severity
    status_count =0
    service_status_results = list()
    result = dict()
    result['current_value'] = 0

    for machine_name, device_list in machine_dict.items():
        # Coutn of devices in ServiceStatus table in different databases acc. to severity, service & datasource list conditions
        status_count += ServiceStatus.objects.order_by().filter(
            device_name__in=device_list,
            service_name__in=service_list,
            data_source__in=data_source_list,
            severity__in=['warning', 'critical']
            ).using(machine_name).count()

    result['current_value'] = status_count
    service_status_results.append(result)
    # Appending of new job
    g_jobs.append(
        calculate_timely_network_alert.s(
            dashboard_name='temperature',
            processed_for=processed_for,
            organization=organization,
            technology='WiMAX',
            service_status_results=service_status_results,
            status_dashboard_name=status_dashboard_name
        )
    )

    if not len(g_jobs):
        return ret

    job = group(g_jobs)
    result = job.apply_async()  # start the jobs
    # for r in result.get():
    #     ret |= r
    return True


@task()
def calculate_timely_network_alert(dashboard_name,
                                   processed_for,
                                   organization,  # assume the organization to be default
                                   technology=None,
                                   service_status_results=list(),
                                   status_dashboard_name=None
                                   ):
    """
    This is celery task function which prepare a list of model object to bulk create the model 
    objects as per total hits of ranges from count of devices.

    :Args:
        dashboard_name : name of Dashboard (Key of dashboard config)
        processed_for : datetime Field 
        organizations : object of all organizations 
        technology : PMP/WiMAX
        service_status_results : list of dictionaries having count of status of objects in warning, critical in key = 'current_value'
        status_dashboard_name : temperature-idu/temperature-acb/temperature-fan

    :return:
        True/False
    """
    # Function for getting default organization
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
    # Query set for fetching data from dashboard settings corresponding to dashboard name
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

    # get the dictionay where keys are same as of the model fields. (Total hits for ranges)
    dashboard_data_dict = get_dashboard_status_range_counter(dashboard_setting, service_status_results)
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

    :Args:
        device_list: list of devices.

    :return:
        dictionay.
    """
    # Unique machine from the device_list
    unique_device_machine_list = {device['machine__name']: True for device in device_list}.keys()

    machine_dict = {}
    # Creating the machine as a key and device_name as a list for that machine.
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device['device_name'] for device in device_list if
                                 device['machine__name'] == machine]

    return machine_dict

#****************************RF Performance Dashboard
@task()
def calculate_RF_Performance_dashboards(technology, is_rad5=False, is_bh = False):
    """
    This Function calls from settings file of Project and initialise the parameters for 
    all RF Performance dashboards and divide the celery tasks according to Number of 
    organizations and Dashboard configs (made according to technology, is_bh & different 
    services corresponding to that technology) per organization for further calculations.

    :Args: 
        technology : PMP/WiMAX/P2P
        is_bh : True/False

    :return:
        True/False
    """
    g_jobs = list()
    ret = False


    try:
        tech_id = eval(technology).ID
    except:
        return ret

    tech=technology
    # Fetching all organizations
    user_organizations = Organization.objects.all()
    processed_for = timezone.now()

    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    devices_method_to_call = inventory_utils.organization_customer_devices
    devices_method_kwargs = dict(specify_ptp_type='all', is_rad5=is_rad5)
    # Making of dashboard configs according to values of technology, is_bh
    if technology == 'WiMAX' and is_bh == False:
        dashboards = {
            'ul_rssi':{
                'model': ServiceStatus,
                'data_source': ['ul_rssi'],
                'service_name': ['wimax_ul_rssi']
            },
            'dl_rssi':{
                'model': ServiceStatus,
                'data_source': ['dl_rssi'],
                'service_name': ['wimax_dl_rssi']
            },
            'ul_cinr':{
                'model': ServiceStatus,
                'data_source': ['ul_cinr'],
                'service_name': ['wimax_ul_cinr']
            },
            'dl_cinr':{
                'model': ServiceStatus,
                'data_source': ['dl_cinr'],
                'service_name': ['wimax_dl_cinr']
            },
            'modulation_ul_fec':{
                'model': ServiceStatus,
                'data_source': ['modulation_ul_fec'],
                'service_name': ['wimax_modulation_ul_fec']
            },
            'modulation_dl_fec':{
                'model': ServiceStatus,
                'data_source': ['modulation_dl_fec'],
                'service_name': ['wimax_modulation_dl_fec']
            }
        }

    elif technology == 'PMP' and is_bh == False:
        if is_rad5:
            dashboards = {
                'ul_rssi':{
                    'model': ServiceStatus,
                    'data_source': ['ul_rssi'],
                    'service_name': ['rad5k_ul_rssi']
                },
                'dl_rssi':{
                    'model': ServiceStatus,
                    'data_source': ['dl_rssi'],
                    'service_name': ['rad5k_dl_rssi']
                },
                'ul_uas':{
                    'model': ServiceStatus,
                    'data_source': ['ul_uas'],
                    'service_name': ['rad5k_ul_uas_invent']
                },
                'dl_uas':{
                    'model': ServiceStatus,
                    'data_source': ['dl_uas'],
                    'service_name': ['rad5k_dl_uas_invent']
                },
                'rad5k_ss_ul_modulation':{
                    'model': ServiceStatus,
                    'data_source': ['rad5k_ss_ul_modulation'],
                    'service_name': ['rad5k_ss_ul_modulation']
                },
                'rad5k_ss_dl_modulation':{
                    'model': ServiceStatus,
                    'data_source': ['rad5k_ss_dl_modulation'],
                    'service_name': ['rad5k_ss_dl_modulation']
                }
            }
        else:
            dashboards = {
                'ul_jitter':{
                    'model': ServiceStatus,
                    'data_source': ['ul_jitter'],
                    'service_name': ['cambium_ul_jitter']
                },
                'dl_jitter':{
                    'model': ServiceStatus,
                    'data_source': ['dl_jitter'],
                    'service_name': ['cambium_dl_jitter']
                },
                'rereg_count':{
                    'model': ServiceStatus,
                    'data_source': ['rereg_count'],
                    'service_name': ['cambium_rereg_count']
                },
                'ul_rssi':{
                    'model': ServiceStatus,
                    'data_source': ['ul_rssi'],
                    'service_name': ['cambium_ul_rssi','rad5k_ul_rssi']
                },
                'dl_rssi':{
                    'model': ServiceStatus,
                    'data_source': ['dl_rssi'],
                    'service_name': ['cambium_dl_rssi','rad5k_dl_rssi']
                }
            }

    elif technology == 'P2P' and is_bh == False:
        dashboards = {
            'rssi':{
                'model': ServiceStatus,
                'data_source': ['rssi'],
                'service_name': ['radwin_rssi']
            },
            'uas':{
                'model': ServiceStatus,
                'data_source': ['uas'],
                'service_name': ['radwin_uas']
            }
        }

    elif technology == 'P2P' and is_bh == True:
        dashboards = {
            'rssi':{
                'model': ServiceStatus,
                'data_source': ['rssi'],
                'service_name': ['radwin_rssi']
            },
            'uas':{
                'model': ServiceStatus,
                'data_source': ['uas'],
                'service_name': ['radwin_uas']
            },
            'availability':{
                'model': NetworkAvailabilityDaily,
                'data_source': ['availability'],
                'service_name': ['availability']
            }
        }

        devices_method_to_call = inventory_utils.organization_network_devices
        devices_method_kwargs = dict(specify_ptp_bh_type='ss')

    for organization in user_organizations:
        for dashboard in dashboards:
            
            if dashboard == 'rssi' and technology == 'P2P' and is_bh == True:
                devices_method_kwargs = dict(specify_ptp_bh_type='all')

            prepare_Rf_dashboard_devices(
                organizations=organization,
                dashboard_name=dashboard,
                processed_for=processed_for,
                dashboard_config=dashboards,
                devices_method_to_call = devices_method_to_call,
                devices_method_kwargs = devices_method_kwargs,
                technology=tech,
                is_bh=is_bh,
                is_rad5=is_rad5
            )
            
    return True


def prepare_Rf_dashboard_devices(organizations,
                                dashboard_name,
                                processed_for,
                                dashboard_config,
                                devices_method_to_call,
                                devices_method_kwargs,
                                technology=None,
                                is_bh=False,
                                is_rad5=False
                            ):
    """
    This Function calls from settings file of Project and initialise the parameters for all RF 
    Performance dashboards and divide the celery tasks according to Number of organizations and 
    Dashboard configs (made according to technology, is_bh & different services corresponding to 
    that technology) per organization for further calculations.

    :Args: 
        technology : PMP/WiMAX/P2P
        is_bh : True/False

    :return:
        True/False
    """
    processed_for = processed_for
    technology_id = None

    if technology:
        try:
            technology_id = eval(technology).ID
        except Exception as e:
            logger.exception(e)
            return False
    else:
        return

    service_status_results = list()
    g_jobs = list()
    ret = False

    user_devices = devices_method_to_call(
        organizations=[organizations.id],
        technology=technology_id,
        **devices_method_kwargs
    )

    dashboard_status_name=dashboard_name
    model = dashboard_config[dashboard_name]['model']
    service_name = dashboard_config[dashboard_name]['service_name']
    data_source = dashboard_config[dashboard_name]['data_source']

    # Handling Radwin5K Case
    filter_condition = ''
    if is_rad5:
        device_type = DeviceType.objects.get(name='Radwin5KSS').id
        filter_condition = 'device_type={0}'.format(device_type)
    else:
        technology = DeviceTechnology.objects.get(name=tech_name.lower()).id
        filter_condition = 'technology_id={0}'.format(technology_id)

    try:
        query = """dashboard_setting = DashboardSetting.objects.get(
                                    {0},
                                    page_name='rf_dashboard',
                                    name=dashboard_status_name,
                                    is_bh=is_bh
                        )""".format(filter_condition)
        exec query
    except DashboardSetting.DoesNotExist as e:
        logger.exception(" Dashboard Setting of {0} is not available. {1}".format(dashboard_name, e))
        return False

    dashboard_name = dashboard_name+'_'+technology
    if is_bh:
        dashboard_name = dashboard_name+'_bh' 

    if user_devices.exists():
        data_list = list()
        # user_sector = sector_objects
        status_counter = {
            "dashboard_name": dashboard_name,
            "device_name": dashboard_name,
            "reference_name": dashboard_name,
            "processed_for": processed_for,
            "organization": organizations,
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
        service_status_results = get_service_status_results(
            user_devices,
            model=model,
            service_name=service_name,
            data_source=data_source
        )

        for result in service_status_results:
            # get the dictionary containing hits for all ranges according to range define in dashboard settings for particular dashboards.
            # range_counter in format {'range1': 1, 'range2': 2,...}
            range_counter = get_dashboard_status_range_counter(dashboard_setting, [result])
            for ranges in range_counter:
                status_counter[ranges] += range_counter[ranges]
            # prepare a list of model object.
        data_list.append(DashboardRangeStatusTimely(**status_counter))

        if len(data_list):
            # call method to bulk create the model object.
            bulk_update_create.delay(
                bulky=data_list,
                action='create',
                model=DashboardRangeStatusTimely
            )

    return True

#***************************** Trend Calculation
def speedometer_sum_query(desired_table, now, then, counter=12):
    """
    This is not a celery function, this function gives us the query on given table, time interval & counter. 

    :Args: 
        desired_table : Table name on which query is executed
        now : timezone.now() format time
        then : timezone.now() format time
        counter : integer 12/24

    :return:
        query : SQL raw query
    """
    in_string = lambda x: "'" + str(x) + "'"
    query = '''
      SELECT
        dashboard_name,
        (
            sum(range1)+
            sum(range2)+
            sum(range3)+
            sum(range4)+
            sum(range5)+
            sum(range6)+
            sum(range7)+
            sum(range8)+
            sum(range9)+
            sum(range10)
        )/{4} as tot,
        organization_id
       FROM {0}
       WHERE
        processed_for <= '{1}'
        AND
        processed_for >= '{2}'
        AND
        dashboard_name in ({3})
       GROUP BY dashboard_name, organization_id
      '''.format(desired_table,
                 now.strftime('%Y-%m-%d %H:%M:%S'),
                 then.strftime('%Y-%m-%d %H:%M:%S'),
                 (",".join(map(in_string, SPEEDOMETER_DASHBAORDS))),
                 counter
                 )
    return query

@task()
def calculate_hourly_speedometer_dashboard():
    """
    This Function calls from settings file of Project in every one hour and it gathers all 5 minutes timely 
    data for SPEEDOMETER_DASHBAORDS within interval of 1 hour (i.e 12 rows) and sum them, divide them by 
    12 & bulk create in other hourly table after that delete 5 minutes table entries from Timely table 
    within interval of 1 hour. 

    :Args: 
        No input Arguments

    :return:
        True/False
    """
    in_string = lambda x: "'" + str(x) + "'"
    # Initialization of variables
    now = timezone.now()
    then = now + datetime.timedelta(hours=-1)
    buffer_now = now + datetime.timedelta(minutes=-5)
    now = buffer_now
    # Mysql Table name (i.e dashboard_dashboardrangestatustimely)
    desired_table = DashboardRangeStatusTimely._meta.db_table
    # Getting raw query
    last_hour_timely_range_status_query = speedometer_sum_query(
        desired_table,
        now,
        then,
        counter=12
    )

    # Create instance of 'NocoutUtilsGateway' class
    nocout_utils = NocoutUtilsGateway()
    # Execution of raw query
    raw_result = nocout_utils.fetch_raw_result(last_hour_timely_range_status_query)
    # Fetching all organizations
    organizations = Organization.objects.all()
    hourly_range_status_list = list()
    count = 0
    for timely_range_status in raw_result:
        count = math.ceil(float(timely_range_status['tot']))

        hourly_range_status = DashboardRangeStatusHourly(
            dashboard_name=timely_range_status['dashboard_name'],
            device_name=timely_range_status['dashboard_name'],
            reference_name=timely_range_status['dashboard_name'],
            processed_for=now,
            range1=count,
            range2=0,
            range3=0,
            range4=0,
            range5=0,
            range6=0,
            range7=0,
            range8=0,
            range9=0,
            range10=0,
            unknown=0,
            organization=organizations.get(id=timely_range_status['organization_id'])
        )
        # append in list
        hourly_range_status_list.append(hourly_range_status)
    # Bulk update the list in model
    if len(hourly_range_status_list):
        bulk_update_create.delay(
            bulky=hourly_range_status_list,
            action='create',
            model=DashboardRangeStatusHourly)
    # Deletion of SPEEDOMETER_DASHBAORDS 5 minutes entries in DashboardRangeStatusTimely model
    DashboardRangeStatusTimely.objects.order_by().filter(
        processed_for__lte=now,
        processed_for__gte=then,
        dashboard_name__in=SPEEDOMETER_DASHBAORDS
    ).delete()    

    return True

@task()
def calculate_hourly_main_dashboard():
    """
    This Function calls from settings file of Project in every one hour and it calls other two function 
    (severity dashboards & range defined dashboards) for further calculations.

    :Args: 
        No input Arguments

    :return:
        True/False
    """

    now = timezone.now()
    buffer_now = now + datetime.timedelta(minutes=-5)
    then = now + datetime.timedelta(hours=-1)
    calculate_hourly_severity_status(now=buffer_now, then=then)
    calculate_hourly_range_status(now=buffer_now, then=then)
    return True


def calculate_hourly_severity_status(now, then):
    """
    This Function calls from calculate_hourly_main_dashboard celery task function and it gathers all 5 minutes 
    DashboardSeverityStatusTimely data within interval of 1 hour (i.e 12 rows) and average their values & bulk 
    create in DashboardSeverityStatusHourly model after that delete 5 minutes table entries from 
    DashboardSeverityStatusTimely table within interval of 1 hour. 

    :Args: 
        now : timezone.now() format
        then : timezone.now() format

    :return:
        True/False
    """
    # Fetching all data in given time range and averaging their values.
    last_hour_timely_severity_status = DashboardSeverityStatusTimely.objects.order_by().filter(
        processed_for__lte=now,
        processed_for__gte=then
    ).values(
        'dashboard_name',
        'organization'
    ).annotate(
        Normal=Avg('ok'),
        Needs_Augmentation=Avg('warning'),
        Stop_Provisioning=Avg('critical'),
        Down=Avg('down'),
        Unknown=Avg('unknown')
    )
    # Fetching all organizations
    organizations = Organization.objects.all()

    hourly_severity_status_list = []    # list for the DashboardSeverityStatusHourly model object

    for timely_severity_status in last_hour_timely_severity_status:

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
        # append in list
        hourly_severity_status_list.append(hourly_severity_status)
    # Bulk create in DashboardSeverityStatusHourly model
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
    """
    This Function calls from calculate_hourly_main_dashboard celery task function and it gathers all 5 minutes 
    DashboardRangeStatusTimely data except SPEEDOMETER_DASHBAORDS within interval of 1 hour (i.e 12 rows) 
    and average their values & bulk create in DashboardRangeStatusHourly model after that delete 5 
    minutes table entries from DashboardRangeStatusTimely table within interval of 1 hour. 

    :Args: 
        now : timezone.now() format
        then : timezone.now() format

    :return:
        True/False
    """
    # Fetching all data from DashboardRangeStatusTimely model within 1 hour interval excluding SPEEDOMETER_DASHBAORDS and Avg their values.
    last_hour_timely_range_status = DashboardRangeStatusTimely.objects.order_by().filter(
        processed_for__lte=now,
        processed_for__gte=then
    ).exclude(dashboard_name__in=SPEEDOMETER_DASHBAORDS
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
    # Fetching all Organizations
    organizations = Organization.objects.all()

    hourly_range_status_list = []   # list for the DashboardRangeStatusHourly model object

    for timely_range_status in last_hour_timely_range_status:
        
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
        # append in list
        hourly_range_status_list.append(hourly_range_status)
    # Bulk create in model DashboardRangeStatusHourly
    if len(hourly_range_status_list):
        bulk_update_create.delay(bulky=hourly_range_status_list,
                                 action='create',
                                 model=DashboardRangeStatusHourly)

    # delete the data from the DashboardRangeStatusTimely model exclude SPEEDOMETER_DASHBAORDS
    DashboardRangeStatusTimely.objects.order_by().filter(
        processed_for__lte=now,
        processed_for__gte=then
    ).exclude(dashboard_name__in=SPEEDOMETER_DASHBAORDS
    ).delete()
    return True

@task()
def calculate_daily_main_dashboard():
    """
    This Function calls from settings file of Project in every 24 hour (1 day) at midnight and it calls other two functions 
    (severity dashboards & range defined dashboards) for further calculations.

    :Args: 
        No input Arguments

    :return:
        True/False
    """

    now = timezone.now()
    # Calling of functions
    calculate_daily_severity_status(now)
    calculate_daily_range_status(now)


def calculate_daily_severity_status(now):
    """
    This Function calls from calculate_daily_main_dashboard celery task function and it gathers all 24 entries of 
    DashboardSeverityStatusHouly data within interval of 24 hour (i.e 24 rows) and average their values & bulk 
    create in DashboardSeverityStatusDaily model after that delete hourly entries from 
    DashboardSeverityStatusHourly table within interval of 24 hours. 

    :Args: 
        now : timezone.now() format

    :return:
        True/False
    """
    # get the current timezone.
    # tzinfo = timezone.get_current_timezone()
    # get today date according to current timezone and reset time to 12 o'clock.

    today = timezone.datetime(now.year, now.month, now.day, 0, 0)
    previous_day = now - timezone.timedelta(days=1)
    yesterday = timezone.datetime(previous_day.year, previous_day.month, previous_day.day, 0, 0)

    # Fetching all data from DashboardSeverityStatusHourly model within 24 hours intervals and Avg their values.
    last_day_timely_severity_status = DashboardSeverityStatusHourly.objects.order_by().filter(
        processed_for__gte=yesterday,
        processed_for__lt=today
    ).values(
        'dashboard_name',
        'organization'
    ).annotate(
        Normal=Avg('ok'),
        Needs_Augmentation=Avg('warning'),
        Stop_Provisioning=Avg('critical'),
        Down=Avg('down'),
        Unknown=Avg('unknown')
    )
    # Fetching all organizations
    organizations = Organization.objects.all()

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
    # Bulk create in model DashboardSeverityStatusDaily
    if len(daily_severity_status_list):
        bulk_update_create.delay(bulky=daily_severity_status_list,
                                 action='create',
                                 model=DashboardSeverityStatusDaily)

    # Delete 24 hours entries from DashboardSeverityStatusHourly model 
    DashboardSeverityStatusHourly.objects.order_by().filter(
        processed_for__gte=yesterday,
        processed_for__lt=today
    ).delete()
    return True


def calculate_daily_range_status(now):
    """
    This Function calls from calculate_daily_main_dashboard celery task function and it gathers all 24 entries 
    DashboardRangeStatusTimely data except SPEEDOMETER_DASHBAORDS within interval of 24 hours (i.e 24 rows) 
    and average their values & bulk create in DashboardRangeStatusDaily model after that delete 24 hours 
    entries from DashboardRangeStatusHourly table within interval of 24 hours. 

    :Args: 
        now : timezone.now() format

    :return:
        True/False
    """

    # get the current timezone.
    # tzinfo = timezone.get_current_timezone()
    # get today date according to current timezone and reset time to 12 o'clock.
    today = timezone.datetime(now.year, now.month, now.day, 0, 0)
    previous_day = now - timezone.timedelta(days=1)
    yesterday = timezone.datetime(previous_day.year, previous_day.month, previous_day.day, 0, 0)
    # Fetching data from DashboardRangeStatusHourly model except SPEEDOMETER_DASHBAORDS within interval of 24 Hours and Avg. values.
    last_day_hourly_range_status = DashboardRangeStatusHourly.objects.order_by().filter(
        processed_for__gte=yesterday,
        processed_for__lt=today
    ).exclude(dashboard_name__in=SPEEDOMETER_DASHBAORDS
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
    # Bulk create in model DashboardRangeStatusDaily
    if len(daily_range_status_list):
        bulk_update_create.delay(bulky=daily_range_status_list,
                                 action='create',
                                 model=DashboardRangeStatusDaily)

    # Bulk delete 24 hours entries from DashboardRangeStatusHourly model except SPEEDOMETER_DASHBAORDS.
    DashboardRangeStatusHourly.objects.order_by().filter(
        processed_for__gte=yesterday,
        processed_for__lt=today
    ).exclude(dashboard_name__in=SPEEDOMETER_DASHBAORDS
    ).delete()
    return True


@task()
def calculate_daily_speedometer_dashboard():
    """
    This Function calls from settings file of Project in every 24 hour (1 day) at midnight and it gathers all 24 Hours entries 
    for SPEEDOMETER_DASHBAORDS within interval of 24 hours (i.e 24 rows) and sum them, divide them by 24 & bulk create in 
    DashboardRangeStatusDaily model after that delete 24 hours entries from DashboardRangeStatusHourly model within interval of 1 day. 

    :Args: 
        No input Arguments

    :return:
        True/False
    """
    now = timezone.now()
    # get the current timezone.
    tzinfo = timezone.get_current_timezone()
    # get today date according to current timezone and reset time to 12 o'clock.
    today = timezone.datetime(now.year, now.month, now.day, 0, 0)
    previous_day = now - timezone.timedelta(days=1)
    yesterday = timezone.datetime(previous_day.year, previous_day.month, previous_day.day, 0, 0)
    # Getting Mysql table name corresponsing to Model name (i.e dashboard_dashboardrangestatushourly) for creating raw query
    desired_table = DashboardRangeStatusHourly._meta.db_table
    # Creation of raw query
    last_hour_timely_range_status_query = speedometer_sum_query(
        desired_table,
        now=today,
        then=yesterday,
        counter=24
    )

    # Create instance of 'NocoutUtilsGateway' class
    nocout_utils = NocoutUtilsGateway()
    # Execution of raw query
    raw_result = nocout_utils.fetch_raw_result(last_hour_timely_range_status_query)
    # Fetching all organizations
    organizations = Organization.objects.all()

    daily_range_status_list = list()
    for hourly_range_status in raw_result:
        count = math.ceil(float(hourly_range_status['tot']))
        daily_range_status = DashboardRangeStatusDaily(
            dashboard_name=hourly_range_status['dashboard_name'],
            device_name=hourly_range_status['dashboard_name'],
            reference_name=hourly_range_status['dashboard_name'],
            processed_for=yesterday,
            range1=count,
            range2=0,
            range3=0,
            range4=0,
            range5=0,
            range6=0,
            range7=0,
            range8=0,
            range9=0,
            range10=0,
            unknown=0,
            organization=organizations.get(id=hourly_range_status['organization_id'])
        )
        daily_range_status_list.append(daily_range_status)
    # Bulk create in DashboardRangeStatusDaily model
    if len(daily_range_status_list):
        bulk_update_create.delay(bulky=daily_range_status_list,
                                 action='create',
                                 model=DashboardRangeStatusDaily)

    # Delete 24 hours entries of SPEEDOMETER_DASHBAORDS from DashboardRangeStatusHourly model 
    DashboardRangeStatusHourly.objects.order_by().filter(
        processed_for__gte=yesterday,
        processed_for__lt=today,
        dashboard_name__in=SPEEDOMETER_DASHBAORDS
    ).delete()
    return True