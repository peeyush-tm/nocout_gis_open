# -*- encoding: utf-8; py-indent-offset: 4 -*-
from celery import task, group
# nocout utils import
from nocout.utils.util import fetch_raw_result
# performance views import
import performance.views as perf_views
# getLastXMonths
from performance.models import SpotDashboard, RfNetworkAvailability, NetworkAvailabilityDaily
from device.models import DeviceType, DeviceTechnology, SiteInstance, Device
from inventory.models import Sector
import inventory.tasks as inventory_tasks

import inventory.utils.util as inventory_utils

from celery.utils.log import get_task_logger
# Django Dateformat utility
from django.utils.dateformat import format
# datetime utility
import datetime

logger = get_task_logger(__name__)


@task()
def device_last_down_time_task(device_type=None):
    """

    :param device_type: can be
     MariaDB [nocout_m5]> select name, id from device_devicetype;
                            +---------------+----+
                            | name          | id |
                            +---------------+----+
                            | CanopyPM100AP |  6 | --> added
                            | CanopyPM100SS |  7 | --> added
                            | CanopySM100AP |  8 | --> added
                            | CanopySM100SS |  9 | --> added
                        | Converter     | 15 |
                            | Default       |  1 | --> DON'T ADD
                        | PINE          | 13 |
                            | Radwin2KBS    |  3 | --> added
                            | Radwin2KSS    |  2 | --> added
                        | RiCi          | 14 |
                            | StarmaxIDU    |  4 | --> added
                            | StarmaxSS     |  5 | --> added
                        | Switch        | 12 |
                            +---------------+----+
    :return: True
    """
    g_jobs = list()
    ret = False

    # devices = Device.objects.filter(is_added_to_nms=1)
    #logger.debug(devices)
    devices = None
    try:
        if device_type:
            dtype = DeviceType.objects.filter(name=device_type).get().id
            devices = Device.objects.filter(is_added_to_nms=1, device_type=dtype)
    except Exception as e:
        return ret

    sites = SiteInstance.objects.all().values_list('name', flat=True)

    for site in sites:
        if devices:
            site_devices = devices.filter(site_instance__name=site)
            if site_devices and site_devices.count():
                g_jobs.append(device_last_down_time_site_wise.s(devices=site_devices))
        else:
            continue

    if len(g_jobs):
        job = group(g_jobs)
        result = job.apply_async()
        for r in result.get():
            ret |= r

    return ret


@task()
def device_last_down_time_site_wise(devices):
    """
    collect device information per site wise
    :return: True
    """
    if devices and devices.count():
        for device_object in devices:
            x = perf_views.device_last_down_time(device_object=device_object)
        return True
    else:
        return False


################### Task for Sector Spot Dashboard Calculation - Start ###################

@task()
def get_all_sector_devices(technology):
    """

    :param technology:
    :return:
    """
    if not technology:
        return False

    # Get the list of organization which are user accessible
    organizations = inventory_tasks.get_organizations()

    try:
        tech = DeviceTechnology.objects.get(name=technology).id
    except Exception as e:
        return False

    sector_values = [
        'id',
        'sector_id',
        'sector_configured_on',
        'sector_configured_on__machine__name',
        'sector_configured_on__device_name',
        'sector_configured_on__ip_address'
    ]

    sector_objects = inventory_utils.organization_sectors(organization=organizations, technology=tech)

    sector_devices_list = sector_objects.select_related(
        'sector_configured_on',
        'sector_configured_on__machine'
    ).values(*sector_values)

    # Get machine wise seperated devices,sectors list
    machine_wise_data,\
    sectors_id_list = get_machines_wise_devices(sectorObject=sector_devices_list)

    # Machine by machine loop
    complete_augmentation_data = list()
    complete_ul_issue_data = list()

    #list of services
    service_list = list()

    # Datasources list
    data_source_list = [
        'bs_ul_issue'
    ]

    # Call 'get_sector_augmentation_data' to get the sector augmentation data from default machine
    # because sector capacity is calculated per 5 minutes and status is stored

    # If any sectors present then proceed forward
    if len(sectors_id_list) > 0:
        complete_augmentation_data = get_sector_augmentation_data(sector_ids=sectors_id_list)

    # Machine wise data calculation for performance utilization status
    for machine_name in machine_wise_data:
        current_row = machine_wise_data[machine_name]
        # List of sector_id on current machine
        sector_ids = current_row['sector_id']
        # List of device_name on current machine
        device_names = current_row['device_name']
        # If any devices present then proceed forward
        if len(device_names) > 0:
            # Call 'get_sector_ul_issue_data' to get the sector UL issue data per machine
            complete_ul_issue_data += get_sector_ul_issue_data(
                devices_names=device_names,
                ds_list=data_source_list,
                machine=machine_name
            )

    # Format augmentation data
    if len(complete_augmentation_data) > 0:
        complete_augmentation_data = format_polled_data(data=complete_augmentation_data, key_column_name='sector_id')

    # Format UL issue data
    if len(complete_ul_issue_data) > 0:
        complete_ul_issue_data = format_polled_data(data=complete_ul_issue_data, key_column_name='device_name')

    # Call function to create resultant data from the calculated data
    resultant_data = get_spot_dashboard_result(
        sectors_list=sector_devices_list,
        augmentation_list=complete_augmentation_data,
        ul_issues_list=complete_ul_issue_data
    )

    # This function insert or update resultant data in SpotDashboard model
    update_spot_dashboard_data(
        calculated_data=resultant_data,
        technology=technology
    )

    return True


def get_machines_wise_devices(sectorObject=[]):
    """
    # this function returns dict of devices,sectors list as per machines
    :param sectorObject: Object of Sector from inventory.models
    :return: dictionary of machines
    """
    machines_wise_dict = {}
    sector_ids_list = list()

    for device in sectorObject:
        machine_name = device['sector_configured_on__machine__name']
        # If any machine is present then proceed
        if machine_name:
            # if new machine then add key else append details of that machine 
            if machine_name not in machines_wise_dict:
                # initialize machine name dict with the device elements
                machines_wise_dict[machine_name] = {
                    "device_id": list(),
                    "sector_id": list(),
                    "sector__sector_id": list(),
                    "device_name": list(),
                    "ip_address": list()
                }
            try:
                if device['id'] not in sector_ids_list:
                    sector_ids_list.append(device['id'])

                machines_wise_dict[machine_name]["sector_id"].append(device['id'])
                machines_wise_dict[machine_name]["sector__sector_id"].append(device['sector_id'])
                machines_wise_dict[machine_name]["device_id"].append(device['sector_configured_on'])
                machines_wise_dict[machine_name]["device_name"].append(device['sector_configured_on__device_name'])
                machines_wise_dict[machine_name]["ip_address"].append(device['sector_configured_on__ip_address'])
            except Exception as e:
                continue

    return (machines_wise_dict, sector_ids_list)


def get_sector_augmentation_data(sector_ids=[]):
    """
    # This function returns sector augmentation detail of last 6 month from SectorCapacityStatus Model
    :param sector_ids:
    :return:
    """
    table_name = 'capacity_management_sectorcapacitystatus'

    in_string = lambda x: "'" + str(x) + "'"

    augmentation_raw_query = '''
                            SELECT FROM_UNIXTIME(sys_timestamp,"%c") AS sys_timestamp, sector_id
                            FROM {0}
                            WHERE
                              sector_id IN ( {1} )
                              AND
                              severity IN ( 'warning', 'critical' )
                              AND
                              sys_timestamp - age > 600
                            '''.format(table_name, (",".join(map(in_string, sector_ids))))

    # Execute Query to get augmentation data
    augmentation_data = fetch_raw_result(augmentation_raw_query)
    #logger.debug(augmentation_data)
    return augmentation_data


def get_sector_ul_issue_data(devices_names=[], ds_list=[], machine='default'):
    """
    # This function returns sector UL Issues Utilization Status performance.models
    :param devices_names:
    :param ds_list:
    :param machine:
    :return:
    """
    table_name = 'performance_utilizationstatus'

    in_string = lambda x: "'" + str(x) + "'"

    ul_issue_raw_query = '''
                         SELECT FROM_UNIXTIME(sys_timestamp,"%c") AS sys_timestamp, device_name
                         FROM {0}
                         WHERE
                            device_name IN ( {1} )
                            AND
                            data_source IN ( {2} )
                            AND
                            severity IN ( 'warning', 'critical' )
                         '''.format(
                                    table_name,
                                    (",".join(map(in_string, devices_names))),
                                    (",".join(map(in_string, ds_list)))
                                )

    # Execute Query to get augmentation data
    ul_issue_data = fetch_raw_result(query=ul_issue_raw_query, machine=machine)
    #logger.debug(ul_issue_data)
    return ul_issue_data


def format_polled_data(data=[], key_column_name=''):
    """
    # This function format the fetched polled data as per the given key
    :param data:
    :param key_column_name:
    :return:
    """
    if not key_column_name:
        return data

    resultant_dict = {}

    for i in range(len(data)):
        current_key = str(data[i][key_column_name])
        current_timestamp_month = int(data[i]['sys_timestamp'])
        if current_key not in resultant_dict:
            resultant_dict[current_key] = list()

        if current_timestamp_month not in resultant_dict[current_key]:
            resultant_dict[current_key].append(current_timestamp_month)
    #logger.debug(resultant_dict)
    return resultant_dict


def get_spot_dashboard_result(sectors_list=[], augmentation_list={}, ul_issues_list={}):
    """
    # This function creates resultant data from the calculated data & sectors list
    :param sectors_list:
    :param augmentation_list:
    :param ul_issues_list:
    :return:
    """
    if len(sectors_list) < 1:
        return []

    # Get Last Six Month List
    last_six_months_list, \
    months_list = perf_views.getLastXMonths(6);

    # loop sectors list
    for i in range(len(sectors_list)):
        sector_id = str(sectors_list[i]['id'])
        device_name = sectors_list[i]['sector_configured_on__device_name']

        augment_data = []
        ul_issue_data = []

        if sector_id in augmentation_list:
            augment_data = augmentation_list[sector_id]

        if device_name in ul_issues_list:
            ul_issue_data = ul_issues_list[device_name]

        # for x in range(1):

        # Reverse the list to get the current month at first index
        last_six_months_list.reverse()
        month_num = int(last_six_months_list[0][1])

        augment_key = 'augment_1'

        if augment_key not in sectors_list[i]:
            sectors_list[i][augment_key] = ""

        try:
            if month_num in augment_data:
                sectors_list[i][augment_key] = 1
        except Exception, e:
            sectors_list[i][augment_key] = 0

        ul_issue_key = 'ul_issue_1'
        if ul_issue_key not in sectors_list[i]:
            sectors_list[i][ul_issue_key] = ""

        try:
            if month_num in ul_issue_data:
                sectors_list[i][ul_issue_key] = 1
        except Exception as e:
            sectors_list[i][ul_issue_key] = 0
    #logger.debug(sectors_list)
    return sectors_list


def update_spot_dashboard_data(calculated_data=[], technology=''):
    """
    # This function insert or update SpotDashboard data as per the calculated data.
    :param calculated_data:
    :param technology:
    """
    
    g_jobs = list()
    bulky_update = list()
    bulky_create = list()

    #counter_val = len(calculated_data)

    for current_row in calculated_data:

        #current_row = calculated_data[i]
        try:
            # Foreign Keys
            sector_id = Sector.objects.get(pk=current_row['id'])
            device_id = sector_id.sector_configured_on #Device.objects.filter(pk=current_row['sector_configured_on'])[0]

            # Sector Details
            sector_sector_id = current_row['sector_id']
            sector_sector_configured_on = current_row['sector_configured_on__ip_address']
            sector_device_technology = technology

            # UL Issues for current month
            ul_issue_1 = current_row['ul_issue_1']

            # Augmentation for current month
            augment_1 = current_row['augment_1']

            logger.debug(current_row)

        except Exception as e:
            logger.exception(e)
            continue

        #bulk operations
        sector_object = None
    
    
        try:
            sector_object = SpotDashboard.objects.get(
                sector_sector_id=sector_sector_id,
                sector=sector_id,
                device=device_id
            )

            sector_object.sector_sector_configured_on = sector_sector_configured_on
            sector_object.sector_device_technology=sector_device_technology
            sector_object.ul_issue_1 = ul_issue_1
            sector_object.augment_1 = augment_1
    
            bulky_update.append(sector_object)
    
        except Exception as e:
            sector_object = SpotDashboard(
                sector=sector_id,
                device=device_id,
                sector_sector_id=sector_sector_id,
                sector_sector_configured_on=sector_sector_configured_on,
                sector_device_technology=sector_device_technology,
                ul_issue_1=ul_issue_1,
                augment_1=augment_1
            )
            bulky_create.append(sector_object)
    

    # If any create item exist then start bulk create job
    if len(bulky_create):
        g_jobs.append(
            inventory_tasks.bulk_update_create.s(
                bulky=bulky_create,
                action='create',
                model=SpotDashboard
            )
        )
    
    # If any update item exist then start bulk update job
    if len(bulky_update):
        g_jobs.append(
            inventory_tasks.bulk_update_create.s(
                bulky=bulky_update,
                action='update',
                model=SpotDashboard
            )
        )
    # Start create & update jobs parallely
    job = group(g_jobs)
    result = job.apply_async()
    ret = False
    
    for r in result.get():
        ret |= r
    
    return ret


@task()
def check_for_monthly_spot():
    """

    """
    ret = False
    g_jobs = list()
    technology = ['WiMAX', 'PMP']
    
    tdy = datetime.datetime.now()
    tom = tdy + datetime.timedelta(days = 1)

    if tom.month - tdy.month:
        for tech in technology:
            g_jobs.append(
                update_spot_dashboard_monthly.s(
                    technology=tech
                )
            )
        if len(g_jobs):
            job = group(g_jobs)
            result = job.apply_async()
            ret = False
            
            for r in result.get():
                ret |= r
    
    return ret


@task()
def update_spot_dashboard_monthly(technology=None):
    """
    # This task runs once in a month(in the end of month).
    # It moves the spotdashboard values to 1 next column & set first column(ul_issue_1,augment_1,sia_1) to 0
    """
    if technology:
        # Get all rows with the given technology
        spot_dashboard_data = SpotDashboard.objects.filter(sector_device_technology=technology)

        total_records = len(spot_dashboard_data)

        bulky_update = list()
        g_jobs = list()

        for i in range(total_records):
            
            current_row = spot_dashboard_data[i]

            # current_row.ul_issue_1 = False
            current_row.ul_issue_2 = current_row.ul_issue_1
            current_row.ul_issue_3 = current_row.ul_issue_2
            current_row.ul_issue_4 = current_row.ul_issue_3
            current_row.ul_issue_5 = current_row.ul_issue_4
            current_row.ul_issue_6 = current_row.ul_issue_5

            # current_row.augment_1 = False
            current_row.augment_2 = current_row.augment_1
            current_row.augment_3 = current_row.augment_2
            current_row.augment_4 = current_row.augment_3
            current_row.augment_5 = current_row.augment_4
            current_row.augment_6 = current_row.augment_5

            # current_row.sia_1 = False
            current_row.sia_2 = current_row.sia_1
            current_row.sia_3 = current_row.sia_2
            current_row.sia_4 = current_row.sia_3
            current_row.sia_5 = current_row.sia_4
            current_row.sia_6 = current_row.sia_5

            bulky_update.append(current_row)

        # If any update item exist then start bulk update job
        if len(bulky_update):
            g_jobs.append(
                inventory_tasks.bulk_update_create.s(
                    bulky=bulky_update,
                    action='update',
                    model=SpotDashboard
                )
            )
        # Start create & update jobs parallely
        job = group(g_jobs)
        result = job.apply_async()
        ret = False
        
        for r in result.get():
            ret |= r
        
        return ret
    else:
        return True

################## Task for Sector Spot Dashboard Calculation - End ###################


################## Task for RF Main Dashboard Network Availability Calculation - Start ###################

@task()
def calculate_rf_network_availability(technology=None):
    """
    This function calculates rf network availability & updates model accordingly
    :param technology: It contains staring value name of technology
    :return: boolean(True)
    """

    # If technology exist then proceed
    if not technology:
        return False

    # Get the list of organization which are user accessible
    organizations = inventory_tasks.get_organizations()

    # If no organization then return
    if not len(organizations):
        return False

    try:
        tech_id = DeviceTechnology.objects.get(name=technology).id
    except Exception as e:
        return False

    inventory_devices = inventory_utils.organization_network_devices(organizations, tech_id)

    if not len(inventory_devices):
        return False

    # Get machine wise data
    machine_wise_devices = rf_getMachineWiseData(inventory_devices)

    # Model used to collect data from distributed databases
    availability_model = NetworkAvailabilityDaily

    # Data sources name list
    data_source_list = [
        "availability"
    ]

    services_list = data_source_list

    # initialize complete availability data variable
    complete_rf_network_avail_data = list()
    total_devices_count = 0

    for machine_name in machine_wise_devices:
        current_row = machine_wise_devices[machine_name]
        # List of device_name on current machine
        device_names = current_row['device_name']
        # If any devices present then proceed forward
        if len(device_names) > 0:
            total_devices_count += len(device_names)
            # Call 'get_network_availability_data' to get the network availability data per machine
            complete_rf_network_avail_data += get_network_availability_data(
                devices_names=device_names,
                service_name_list=services_list,
                ds_name_list=data_source_list,
                machine=machine_name,
                avail_model=availability_model
            )

    if len(complete_rf_network_avail_data) and total_devices_count > 0:
        # Call function to get the count & % wise availability
        resultant_dict = insert_network_avail_result(
            resultant_data=complete_rf_network_avail_data,
            devices_count=total_devices_count,
            tech_id=tech_id
        )

    return True


def rf_getMachineWiseData(devices_list):
    """
    This function returns dict of devices list as per machines
    :param devices_list: Object of devices from device.models
    :return: dictionary of machines
    """
    machines_wise_dict = {}

    for device in devices_list:
        try:
            machine_name = device.machine.name
        except Exception, e:
            machine_name = ''
        # If any machine is present then proceed
        if machine_name:
            # if new machine then add key else append details of that machine 
            if machine_name not in machines_wise_dict:
                # initialize machine name dict with the device elements
                machines_wise_dict[machine_name] = {
                    "device_name": list(),
                    "ip_address": list()
                }
            try:
                # IF device name not present then append
                if device.device_name and device.device_name not in machines_wise_dict[machine_name]["device_name"]:
                    machines_wise_dict[machine_name]["device_name"].append(device.device_name)

                # IF IP adress not present then append
                if device.ip_address and device.ip_address not in machines_wise_dict[machine_name]["ip_address"]:
                    machines_wise_dict[machine_name]["ip_address"].append(device.ip_address)
            except Exception as e:
                continue

    return machines_wise_dict


def get_network_availability_data(devices_names=[], service_name_list=["availability"], ds_name_list=["availability"], machine='', avail_model=''):
    """
    :This function fetch availability data as per given params
    :param devices_names: It contains list of device names
    :param ds_name_list: It contains list of data source names
    :param service_name_list: It contains list of service names
    :param machine: It contains the name of machine
    :param avail_model: It contains the model from which data is to be fetched
    :return polled_data_list: It contains the fetched polled data as per given params
    """

    polled_data_list = []
    
    # Columns required to be fetched
    required_values = [
        'device_name',
        'current_value',
        'sys_timestamp'
    ]

    # If no model present then return blank list
    if not avail_model:
        return polled_data_list

    try:
        # this is today object
        tdy = datetime.datetime.today()

        # this is the end time today's 00:00:00
        end_time = datetime.datetime(tdy.year, tdy.month, tdy.day, 0, 0)

        # this is the start time today's 00:00:00
        start_time = end_time +  datetime.timedelta(days = -1)

        # start time in UNIX TIME
        start_time = float( format ( start_time , 'U' ))

        # end time in UNIX TIME
        end_time = float( format ( end_time , 'U' ))

        # Fetch data from given model
        polled_data_list = avail_model.objects.filter(
            device_name__in=devices_names,
            service_name__in=service_name_list,
            data_source__in=ds_name_list,
            sys_timestamp__gte=start_time,
            sys_timestamp__lte=end_time
        ).using(machine).values(*required_values)

        return polled_data_list

    except Exception, e:
        return polled_data_list


def insert_network_avail_result(resultant_data=[], devices_count=0, tech_id=''):
    """
    :This function calcultes the availability & unavailability of devices as per the fetched result
    :param resultant_data: It contains the list of data fetched from distributed databases
    """
    g_jobs = list()
    ret = False

    if not len(resultant_data) or devices_count == 0:
        return False

    total_current_val = 0
    devices_list = []

    for val in resultant_data:
        current_row = resultant_data[val]
        if current_row:
            try:
                device_name = current_row.device_name
                current_value = current_row.current_value
            except Exception, e:
                device_name = ''
                current_value = 0

            if device_name and device_name not in devices_list:
                devices_list.append(device_name)
                total_current_val += current_value

    # Calculate the percentage availability
    avg_avail = total_current_val / devices_count
    avg_unavail = 100 - avg_avail

    try:
        current_date_time = int((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%s'))
        bulky_create = list()

        rf_network_avail_instance = RfNetworkAvailability(
            technology=tech_id,
            avail=avg_avail,
            unavail=avg_unavail,
            sys_timestamp=current_date_time
        )

        bulky_create.append(rf_network_avail_instance)

        # If any create item exist then start bulk create job
        if len(bulky_create):
            g_jobs.append(
                inventory_tasks.bulk_update_create.s(
                    bulky=bulky_create,
                    action='create',
                    model=RfNetworkAvailability
                )
            )

        # If any g_jobs exists
        if len(g_jobs):
            # Start create jobs parallely
            job = group(g_jobs)
            result = job.apply_async()
            ret = False
            
            for r in result.get():
                ret |= r
            
            return ret
        
    except Exception as e:
        logger.exception(e)
        return False

    return True


################## Task for RF Main Dashboard Network Availability Calculation - End ###################

