# -*- encoding: utf-8; py-indent-offset: 4 -*-
from celery import task, group
import math
from django.db.models import Avg, F, Q

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
# performance gateway class import
from performance.views import PerformanceViewsGateway
# getLastXMonths
from performance.models import SpotDashboard, RfNetworkAvailability, NetworkAvailabilityDaily
from device.models import DeviceType, DeviceTechnology, SiteInstance, Device
from organization.models import Organization
from dashboard.models import PTPBHUptime
from inventory.models import Sector
import inventory.tasks as inventory_tasks
# Import inventory utils gateway class
from inventory.utils.util import InventoryUtilsGateway

from celery.utils.log import get_task_logger
# Django Dateformat utility
from django.utils.dateformat import format
# datetime utility
import datetime
from dateutil.relativedelta import *
from inventory.tasks import bulk_update_create

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

    # devices = Device.objects.filter(is_added_to_nms__gt=0)
    #logger.debug(devices)
    devices = None
    try:
        if device_type:
            dtype = DeviceType.objects.filter(name=device_type).get().id
            devices = Device.objects.filter(
                is_added_to_nms__gt=0,
                device_type=dtype
            )
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
        # Create instance of 'PerformanceViewsGateway' class
        perf_views = PerformanceViewsGateway()
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
    ret = False
    g_jobs = list()

    bulky_create = list()
    bulky_update = list()

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

    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    sector_objects = inventory_utils.organization_sectors(
        organization=organizations,
        technology=tech
    )

    if not sector_objects.exists():
        return False

    spot_objects = SpotDashboard.objects.select_related(
        'sector',
        'device'
    ).filter(
        Q(ul_issue_1=False)
        |
        Q(augment_1=False),  # if any of these is False only then we should process
        sector__in=sector_objects
    )

    existing_sectors = spot_objects.values_list('sector', flat=True)

    # the sectors we want to manipulate are the existing sectors
    # rest of the sectors we would want to create if not exists
    # or skip completely

    sector_devices_list = sector_objects.filter(
        id__in=existing_sectors
    ).values(*sector_values)

    # Get machine wise seperated devices,sectors list
    machine_wise_data, sectors_id_list = get_machines_wise_devices(sectorObject=sector_devices_list)

    # Machine by machine loop
    complete_augmentation_data = list()
    complete_ul_issue_data = list()

    # list of services
    service_list = list()

    # datasources technology wise
    data_source_tech = {
        'wimax': ['pmp1_ul_issue', 'pmp2_ul_issue'],
        'pmp': ['bs_ul_issue']
    }

    # Datasources list
    try:
        data_source_list = data_source_tech[technology.strip().lower()]
    except Exception as e:
        logger.exception(e)
        return False

    # Call 'get_sector_augmentation_data' to get the sector augmentation data from default machine
    # because sector capacity is calculated per 5 minutes and status is stored

    # If any sectors present then proceed forward
    if len(sectors_id_list) > 0:
        complete_augmentation_data = get_sector_augmentation_data(sector_ids=sectors_id_list)
    # If any sectors present then proceed forward
    if len(sectors_id_list) > 0:
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
        complete_ul_issue_data = format_polled_data(data=complete_ul_issue_data, key_column_name='sector_id')

    # Create instance of 'PerformanceViewsGateway' class
    perf_views = PerformanceViewsGateway()

    # Reverse the list to get the current month at first index
    last_six_months_list, months_list = perf_views.getLastXMonths(6)
    last_six_months_list.reverse()
    month_num = int(last_six_months_list[0][1])

    processed_sectors = dict()

    for sector in sector_objects:
        spot_object = None

        # deduplication of the sector on the basis of sector ID
        if sector.sector_id in processed_sectors:
            continue
        else:
            processed_sectors[sector.sector_id] = sector.sector_id
        # de duplicate sector

        try:
            spot_object = spot_objects.get(
                sector_sector_id=sector.sector_id,
                sector=sector
            )
            sector_id = sector.id
            sector_sector_id = sector.sector_id

            update_this = False

            if sector_sector_id in complete_augmentation_data:
                augment_data = complete_augmentation_data[sector_sector_id]
                if (month_num in augment_data) and not spot_object.augment_1:
                    spot_object.augment_1 = 1
                    update_this = True

            if sector_sector_id in complete_ul_issue_data:
                ul_issue_data = complete_ul_issue_data[sector_sector_id]
                if (month_num in ul_issue_data) and not spot_object.ul_issue_1:
                    spot_object.ul_issue_1 = 1
                    update_this = True

            if update_this:
                bulky_update.append(spot_object)

        except Exception as e:
            if not spot_object and not (SpotDashboard.objects.filter(
                sector_sector_id=sector.sector_id,
                sector=sector
            ).exists()):
                bulky_create.append(
                    SpotDashboard(
                        sector_sector_id=sector.sector_id,
                        sector=sector,
                        device=sector.sector_configured_on,
                        sector_device_technology=technology,
                        sector_sector_configured_on=sector.sector_configured_on.ip_address
                    )
                )

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
    if not len(g_jobs):
        return False

    job = group(g_jobs)
    ret = False
    result = job.apply_async()  # start the jobs
    # for r in result.get():
    #     ret |= r
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
                            SELECT FROM_UNIXTIME(sys_timestamp,"%c") AS sys_timestamp, sector_sector_id as sector_id
                            FROM {0}
                            WHERE
                              sector_id IN ( {1} )
                              AND
                              severity IN ( 'warning', 'critical' )
                            '''.format(table_name, (",".join(map(in_string, sector_ids))))

    # Create instance of 'NocoutUtilsGateway' class
    nocout_utils = NocoutUtilsGateway()
    # Execute Query to get augmentation data
    augmentation_data = nocout_utils.fetch_raw_result(augmentation_raw_query)
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
                         SELECT FROM_UNIXTIME(sys_timestamp,"%c") AS sys_timestamp, device_name, refer as sector_id
                         FROM {0}
                         WHERE
                            device_name IN ( {1} )
                            AND
                            data_source IN ( {2} )
                            AND
                            severity IN ( 'warning', 'critical' )
                            AND isnull(refer) = false
                         '''.format(
                                    table_name,
                                    (",".join(map(in_string, devices_names))),
                                    (",".join(map(in_string, ds_list)))
                                )
    
    # Create instance of 'NocoutUtilsGateway' class
    nocout_utils = NocoutUtilsGateway()
    # Execute Query to get augmentation data
    ul_issue_data = nocout_utils.fetch_raw_result(query=ul_issue_raw_query, machine=machine)
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
        spot_dashboard_data.update(
            ul_issue_6=F('ul_issue_5'),
            augment_6=F('augment_5'),
            sia_6=F('sia_5'),
        )
        spot_dashboard_data.update(
            ul_issue_5=F('ul_issue_4'),
            augment_5=F('augment_4'),
            sia_5=F('sia_4'),
        )
        spot_dashboard_data.update(
            ul_issue_4=F('ul_issue_3'),
            augment_4=F('augment_3'),
            sia_4=F('sia_3'),
        )
        spot_dashboard_data.update(
            ul_issue_3=F('ul_issue_2'),
            augment_3=F('augment_2'),
            sia_3=F('sia_2'),
        )
        spot_dashboard_data.update(
            ul_issue_2=F('ul_issue_1'),
            augment_2=F('augment_1'),
            sia_2=F('sia_1'),

        )

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
        tech_object = DeviceTechnology.objects.get(name=technology)
        tech_id = tech_object.id
    except Exception as e:
        return False

    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    organization_devices = inventory_utils.filter_devices(
        organizations=organizations,
        data_tab=technology,
        page_type="network",
        required_value_list=['id', 'machine__name', 'device_name', 'ip_address'],
        other_bh=False
    )

    # Get machine wise data
    machine_wise_devices = inventory_utils.prepare_machines(
        organization_devices,
        machine_key='machine_name'
    )

    # Model used to collect data from distributed databases
    availability_model = NetworkAvailabilityDaily

    # Data sources name list
    data_source_list = [
        "availability"
    ]

    services_list = data_source_list

    # initialize complete availability data variable
    complete_rf_network_avail_data = list()

    # the devices filtered are present int organization devices
    total_devices_count = len(organization_devices)

    machine_count = 0

    for machine in machine_wise_devices:

        # List of device_name on current machine
        device_names = machine_wise_devices[machine]

        # Call 'get_network_availability_data' to get the network availability data per machine
        complete_rf_network_avail_data += get_network_availability_data(
            devices_names=device_names,
            service_name_list=services_list,
            ds_name_list=data_source_list,
            machine=machine,
            avail_model=availability_model
        )

    availability = 0
    for rf_network_avail_data in complete_rf_network_avail_data:
        try:
            availability += float(rf_network_avail_data['Availability'])
            machine_count += 1
        except Exception as e:
            logger.exception(e)
            continue

    try:
        availability = availability/machine_count
    except Exception as e:
        logger.exception(e)
        return False

    av = math.floor(availability)
    unav = math.ceil(100 - float(av))

    # Call function to get the count & % wise availability
    resultant_dict = insert_network_avail_result(
        resultant_data=[av, unav],
        tech_id=tech_object
    )

    return resultant_dict


def get_network_availability_data(devices_names, machine, avail_model, service_name_list, ds_name_list):
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
        'data_source'
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
        start_time = end_time + datetime.timedelta(days=-1)

        # start time in UNIX TIME
        start_time = float(format(start_time, 'U'))

        # end time in UNIX TIME
        end_time = float(format(end_time, 'U'))

        # Fetch data from given model
        polled_data_list = avail_model.objects.filter(
            device_name__in=devices_names,
            service_name__in=service_name_list,
            data_source__in=ds_name_list,
            sys_timestamp__gte=start_time,
            sys_timestamp__lte=end_time
        ).using(machine).values(*required_values).annotate(
            Availability=Avg('current_value')  # average of all the availablity of the devices. group by data_source
        )
        # output = ['data_source': 'availability', 'Availability': <value>]

    except Exception as e:
        logger.exception(e)

    return polled_data_list


def insert_network_avail_result(resultant_data, tech_id):
    """
    :This function calcultes the availability & unavailability of devices as per the fetched result
    :param resultant_data: It contains the list of data fetched from distributed databases
    """
    g_jobs = list()
    ret = False

    # Calculate the percentage availability
    try:
        avg_avail = resultant_data[0]
        avg_unavail = resultant_data[1]
    except Exception as e:
        logger.exception(e)
        return ret

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
        # Start create & update jobs parallely
        if not len(g_jobs):
            return False

        job = group(g_jobs)
        ret = False
        result = job.apply_async()  # start the jobs
        # for r in result.get():
        #     ret |= r
        return True
        
    except Exception as e:
        logger.exception(e)
        return False


################## Task for RF Main Dashboard Network Availability Calculation - End ###################
def ptpbh_uptime_resultset(machine='default',devices=[], first_day=None, last_day=None):
    """
    This function return uptime percentage as per the given params
    :param machine: machine name to filter out devices based on machine.
    :param devices: list of device_name.
    :param first_day: Epoch time for first day of month.
    :param last_day: Epoch time for last day of month.
    :return:
    """
    if not (devices and first_day and last_day):
        return []

    nocout_utils = NocoutUtilsGateway()
    devices_str = ','.join(str(device) for device in devices)

    query = """select
                    round(Avg(current_value),3) as uptime_percent
                from
                    performance_networkavailabilitydaily
                where
                    device_name in ({0})
                And
                    sys_timestamp >= {1}
                And
                    sys_timestamp < {2}
                Group by
                    ip_address
                """.format(devices_str, first_day, last_day)

    result = nocout_utils.fetch_raw_result(query, machine=machine)
    logger.error("query result {0}".format(result))
    if result:
        uptime_percent_list = [data['uptime_percent'] for data in result]
        length = len(uptime_percent_list)
        value = sum(val>99.5 for val in uptime_percent_list)
        percent = round(float((float(value)/float(length))*100.0), 3)
    else:
        percent = 0.0
    return percent



@task()
def calculate_avg_availability_ptpbh():
    """
    Calcualate Average uptime for ptp backhaul type devices.
    Task scheduled to 1st day of every month.
    Database keeps last 12 month data in PTPBHUptime model.

    :return: True/False
    """
    inventory_utils = InventoryUtilsGateway()
    org_id_list = list(Organization.objects.values_list('id',flat=True))
    # Filter devices for page_type , organizations and data_tab.
    devices = inventory_utils.filter_devices(
       organizations= org_id_list,
       data_tab='P2P',
       page_type='network',
       required_value_list=['id', 'machine__name', 'device_name', 'ip_address', 'organization__id']
    )

    # Return dict, key:machine_name and value:list of device.
    machines_dict = inventory_utils.prepare_machines(
       devices, machine_key='machine_name'
    )
    # # key value mapping for device_name and organization id.
    # mapping_device_organization = dict([(device['device_name'],device['organization_id']) for device in devices])

    resultset = dict()

    cur_time = datetime.datetime.now()
    cur_time = datetime.datetime(cur_time.year, cur_time.month, cur_time.day, 0, 0, 0)

    PTPBHUptime_set = PTPBHUptime.objects.all()

    # If True: Delete the entries from oldest month and Insert last month entries.
    if PTPBHUptime_set.exists():
        last_year = datetime.datetime(cur_time.year-1, cur_time.month, cur_time.day)
        # Delete Entry for oldest month
        PTPBHUptime.objects.filter(
            datetime__lt=last_year
        ).delete()

        last_month_start = datetime.datetime(cur_time.year, cur_time.month-1, 1)
        last_month_end = last_month_start + relativedelta(day=31)

        # Datetime object to Epoch time conversion.
        last_month_start_epoch = int(last_month_start.strftime('%s'))
        last_month_end_epoch = int(last_month_end.strftime('%s'))
        # Insert Entry for latest month
        for machine in machines_dict:
            devices = machines_dict.get(machine)
            result = ptpbh_uptime_resultset(
                machine=machine,
                devices=devices,
                first_day=last_month_start_epoch,
                last_day=last_month_end_epoch
            )
            resultset[last_month_start] = result

    # Calculate and Store entries for last 12 months.
    else:
        # Network Availability data for devices is stored in their respective machine location.
        year = cur_time.year-1
        month = cur_time.month
        day = 1

        # Query over Each machine in database.
        for machine in machines_dict:
            devices = machines_dict.get(machine)
            for i in range(12):
                first_day = datetime.datetime(year,month,day)
                last_day = datetime.datetime(year,month,day) + relativedelta(day=31)

                first_day_epoch = int(first_day.strftime('%s'))
                last_day_epoch = int(last_day.strftime('%s'))

                result = ptpbh_uptime_resultset(
                    machine=machine,
                    devices=devices,
                    first_day=first_day_epoch,
                    last_day=last_day_epoch
                )

                resultset[first_day] = result

                month = month+1
                if month>12:
                    year = year+1
                    month = 1

    bulk_bh_entry = [PTPBHUptime(timestamp=date_time,
                                 uptime_percent=percent) \
                for date_time,percent in resultset.iteritems()]

    g_jobs = list()

    if len(bulk_bh_entry):
        g_jobs.append(inventory_tasks.bulk_update_create.s(
            bulk_bh_entry,
            action='create',
            model=PTPBHUptime
        ))
    else:
        return False

    job = group(g_jobs)
    job.apply_async()  # Start the Job.

    return True