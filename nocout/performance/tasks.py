from celery import task
from pprint import pformat
from nocout.utils.util import fetch_raw_result
from device.models import Device
# from performance.views import device_last_down_time
import performance.views as perf_views
# getLastXMonths
from performance.models import SpotDashboard
from device.models import DeviceType, DeviceTechnology
from inventory.models import Sector
import inventory.tasks as inventory_tasks

import inventory.utils.util as inventory_utils

from celery.utils.log import get_task_logger
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
    devices = Device.objects.filter(is_added_to_nms=1)
    try:
        if device_type:
            dtype = DeviceType.objects.filter(name=device_type).get().id
            devices = devices.filter(device_type=dtype)
    except:
        pass

    for device_object in devices:
        x = perf_views.device_last_down_time(device_object=device_object)
    return True


################### Task for Sector Spot Dashboard Calculation - Start ###################

@task()
def get_all_sector_devices(technology):

    if not technology:
        return False

    # Get the list of organization which are user accessible
    organizations = inventory_tasks.get_organizations()
    
    try:
        tech = DeviceTechnology.objects.get(name=technology).id
    except Exception, e:
        return False
    
    sector_objects = inventory_utils.organization_sectors(organization=organizations, technology=tech)
    
    sector_devices_list = sector_objects.select_related('sector_configured_on','sector_configured_on__machine').values(
        'id',
        'sector_id',
        'sector_configured_on',
        'sector_configured_on__machine__name',
        'sector_configured_on__device_name',
        'sector_configured_on__ip_address'
    )

    # Get machine wise seperated devices,sectors list
    machine_wise_data = get_machines_wise_devices(sectorObject=sector_devices_list)

    # Machine by machine loop
    complete_augmentation_data = list()
    complete_ul_issue_data = list()

    # Datasources list
    data_source_list = [
        'bs_ul_issue'
    ]

    for machine_name in machine_wise_data.keys():
        current_row = machine_wise_data[machine_name]
        # List of sector_id on current machine
        sector_ids = current_row['sector_id']
        # List of device_name on current machine
        device_names = current_row['device_name']
        # Call 'getSectorAugmentationData' to get the sector augmentation data per machine
        complete_augmentation_data += getSectorAugmentationData(sector_ids)
        # Call 'getSectorULIssueData' to get the sector UL issue data per machine
        complete_ul_issue_data += getSectorULIssueData(device_names,data_source_list)

    # Format augmentation data
    if len(complete_augmentation_data) > 0:
        complete_augmentation_data = format_polled_data(data=complete_augmentation_data,key_column_name='sector_id')

    # Format UL issue data
    if len(complete_ul_issue_data) > 0:
        complete_ul_issue_data = format_polled_data(data=complete_ul_issue_data,key_column_name='device_name')

    # Call function to create resultant data from the calculated data
    resultant_data = getSpotDashboardResult(
        sectors_list=sector_devices_list,
        augmentation_list=complete_augmentation_data,
        ul_issues_list=complete_ul_issue_data
    )

    # This function insert or update resultant data in SpotDashboard model
    updateSpotDashboardData(
        calculated_data=resultant_data,
        technology=technology
    )

    return True

# this function returns dict of devices,sectors list as per machines
def get_machines_wise_devices(sectorObject=[]):

    machines_wise_dict = {}
    machine_names_list = list()
    for device in sectorObject:
        machine_name = device['sector_configured_on__machine__name']
        # If any machine is present then proceed
        if machine_name:
            # if new machine then add key else append details of that machine 
            if machine_name not in machine_names_list:
                # Append the new machine name in machine list
                machine_names_list.append(machine_name)
                # initialize machine name dict with the device elements
                machines_wise_dict[machine_name] = {
                    "device_id" : list(),
                    "sector_id" : list(),
                    "sector__sector_id" : list(),
                    "device_name" : list(),
                    "ip_address" : list()
                }

            machines_wise_dict[machine_name]["sector_id"].append(device['id'])
            machines_wise_dict[machine_name]["sector__sector_id"].append(device['sector_id'])
            machines_wise_dict[machine_name]["device_id"].append(device['sector_configured_on'])
            machines_wise_dict[machine_name]["device_name"].append(device['sector_configured_on__device_name'])
            machines_wise_dict[machine_name]["ip_address"].append(device['sector_configured_on__ip_address'])

    return machines_wise_dict

# This function returns sector augmentation detail of last 6 month from SectorCapacityStatus Model
def getSectorAugmentationData(sector_ids=[]):

    table_name = 'capacity_management_sectorcapacitystatus'
    
    in_string = lambda x: "'" + str(x) + "'"

    augmentation_raw_query = 'SELECT FROM_UNIXTIME(sys_timestamp,"%c") AS sys_timestamp,sector_id FROM ' + table_name + '\
                             WHERE sector_id IN ( {0} ) \
                             AND \
                             sys_timestamp > UNIX_TIMESTAMP(now()- INTERVAL {1} MONTH) \
                             ORDER BY sys_timestamp desc'.format(
                                (",".join(map(in_string, sector_ids))),
                                6
                            )


    # Execute Query to get augmentation data
    augmentation_data = fetch_raw_result(augmentation_raw_query)

    return augmentation_data

# This function returns sector UL Issues of last 6 month from Utilization Model
def getSectorULIssueData(devices_names=[],ds_list=[]):

    table_name = 'performance_utilization'
    
    in_string = lambda x: "'" + str(x) + "'"

    ul_issue_raw_query = 'SELECT  FROM_UNIXTIME(sys_timestamp,"%c") AS sys_timestamp,device_name FROM ' + table_name + '\
                         WHERE device_name IN ( {0} ) \
                         AND \
                         data_source IN ( {1} )\
                         AND \
                         sys_timestamp > UNIX_TIMESTAMP(now()- INTERVAL {2} MONTH)\
                         ORDER BY sys_timestamp desc'.format(
                            (",".join(map(in_string, devices_names))),
                            (",".join(map(in_string, ds_list))),
                            6
                        )


    # Execute Query to get augmentation data
    ul_issue_data = fetch_raw_result(ul_issue_raw_query)

    return ul_issue_data

# This function format the fetched polled data as per the given key
def format_polled_data(data=[],key_column_name=''):

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

    return resultant_dict




# This function creates resultant data from the calculated data & sectors list
def getSpotDashboardResult(sectors_list=[],augmentation_list={},ul_issues_list={}):

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
        
        for x in range(6):
            
            month_num = int(last_six_months_list[x][1])

            augment_key = 'augment_'+str(x+1)
            if augment_key not in sectors_list[i]:
                sectors_list[i][augment_key] = ""

            # if '10.193.142.2_25' == str(sectors_list[i]['sector_id']):
            #     logger.debug("^^^^^^^^^^^^^^^^^^")
            #     logger.debug(augment_data)
            #     logger.debug(sector_id)
            #     logger.debug(month_num)
            #     logger.debug("^^^^^^^^^^^^^^^^^^")
            try:
                # if augment_data[x] > 0:
                if month_num in augment_data:
                    sectors_list[i][augment_key] = 1
            except Exception, e:
                sectors_list[i][augment_key] = 0

            ul_issue_key = 'ul_issue_'+str(x+1)
            if ul_issue_key not in sectors_list[i]:
                sectors_list[i][ul_issue_key] = ""

            try:
                # if ul_issue_data[x] > 0:
                if month_num in ul_issue_data:
                    sectors_list[i][ul_issue_key] = 1
            except Exception, e:
                sectors_list[i][ul_issue_key] = 0

    return sectors_list

# This function insert or update SpotDashboard data as per the calculated data.
def updateSpotDashboardData(calculated_data=[],technology=''):

    counter_val = len(calculated_data)

    for i in range(counter_val):
        current_row = calculated_data[i]
        
        # Foreign Keys
        sector_id = Sector.objects.filter(pk=calculated_data[i]['id'])[0]
        device_id = Device.objects.filter(pk=calculated_data[i]['sector_configured_on'])[0]
        
        # Sector Details
        sector_sector_id = calculated_data[i]['sector_id']
        sector_sector_configured_on = calculated_data[i]['sector_configured_on__ip_address']
        sector_device_technology = technology
        
        # UL Issues
        ul_issue_1 = calculated_data[i]['ul_issue_1']
        ul_issue_2 = calculated_data[i]['ul_issue_2']
        ul_issue_3 = calculated_data[i]['ul_issue_3']
        ul_issue_4 = calculated_data[i]['ul_issue_4']
        ul_issue_5 = calculated_data[i]['ul_issue_5']
        ul_issue_6 = calculated_data[i]['ul_issue_6']

        # Augmentation
        augment_1 = calculated_data[i]['augment_1']
        augment_2 = calculated_data[i]['augment_2']
        augment_3 = calculated_data[i]['augment_3']
        augment_4 = calculated_data[i]['augment_4']
        augment_5 = calculated_data[i]['augment_5']
        augment_6 = calculated_data[i]['augment_6']

        sectorObject = SpotDashboard.objects.filter(sector_sector_id=sector_sector_id)

        # Sector Exist, Update entry
        if len(sectorObject) > 0:
            sectorObject.update(
                ul_issue_1=ul_issue_1,
                ul_issue_2=ul_issue_2,
                ul_issue_3=ul_issue_3,
                ul_issue_4=ul_issue_4,
                ul_issue_5=ul_issue_5,
                ul_issue_6=ul_issue_6,
                augment_1=augment_1,
                augment_2=augment_2,
                augment_3=augment_3,
                augment_4=augment_4,
                augment_5=augment_5,
                augment_6=augment_6
            )
        else:
            # Sector Not Exist, Create new entry
            SpotDashboard.objects.create(
                sector=sector_id,
                device=device_id,
                sector_sector_id=sector_sector_id,
                sector_sector_configured_on=sector_sector_configured_on,
                sector_device_technology=sector_device_technology,
                ul_issue_1=ul_issue_1,
                ul_issue_2=ul_issue_2,
                ul_issue_3=ul_issue_3,
                ul_issue_4=ul_issue_4,
                ul_issue_5=ul_issue_5,
                ul_issue_6=ul_issue_6,
                augment_1=augment_1,
                augment_2=augment_2,
                augment_3=augment_3,
                augment_4=augment_4,
                augment_5=augment_5,
                augment_6=augment_6
            )


################### Task for Sector Spot Dashboard Calculation - End ###################