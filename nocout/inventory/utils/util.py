# -*- coding: utf-8 -*-

#python core functions
import datetime

#django settings
from nocout.settings import P2P, WiMAX, PMP, DEBUG

#django core model functions
from django.db.models import Count, Q

#nocout specific functions
from device.models import Device, DeviceTechnology

#inventory specific functions
from inventory.models import Sector, Circuit, SubStation

#nocout utilities
from nocout.utils.util import cache_for

#logging the performance of function
import logging
log = logging.getLogger(__name__)
#logging the performance of function



#common function to get the devices
# @cache_for(300)
def ptp_device_circuit_backhaul(specify_type='all'):
    """
    Special case fot PTP technology devices. Wherein Circuit type backhaul is required
    :return:
    """
    if specify_type == 'all':
        device_list_with_circuit_type_backhaul = Device.objects.filter(
            Q(id__in=Sector.objects.filter(id__in=Circuit.objects.filter(circuit_type__icontains="Backhaul").
                                            values_list('sector', flat=True)).
                                            values_list('sector_configured_on', flat=True))
            |
            Q(id__in=SubStation.objects.filter(id__in=Circuit.objects.filter(circuit_type__icontains="Backhaul").
                                            values_list('sub_station', flat=True)).
                                            values_list('device', flat=True))
        )
    elif specify_type == 'ss':
        device_list_with_circuit_type_backhaul = Device.objects.filter(
            Q(id__in=SubStation.objects.filter(id__in=Circuit.objects.filter(circuit_type__icontains="Backhaul").
                                            values_list('sub_station', flat=True)).
                                            values_list('device', flat=True))
        )
    elif specify_type == 'bs':
        device_list_with_circuit_type_backhaul = Device.objects.filter(
            Q(id__in=Sector.objects.filter(id__in=Circuit.objects.filter(circuit_type__icontains="Backhaul").
                                            values_list('sector', flat=True)).
                                            values_list('sector_configured_on', flat=True))
        )
    else:
        device_list_with_circuit_type_backhaul = []

    return device_list_with_circuit_type_backhaul


# @cache_for(300)
def organization_customer_devices(organizations, technology = None, specify_ptp_type='all'):
    """
    To result back the all the customer devices from the respective organization..

    :param organization:
    :return list of customer devices
    """
    if not technology:
        organization_customer_devices= Device.objects.filter(
                                    Q(sector_configured_on__isnull=False) | Q(substation__isnull=False),
                                    is_added_to_nms=1,
                                    is_deleted=0,
                                    organization__in= organizations
        )
    else:
        if int(technology) == int(P2P.ID):
            if specify_ptp_type in ['ss','bs']:
                choose_ss_bs = None
                if specify_ptp_type == 'ss':
                    choose_ss_bs = Q(substation__isnull=False)
                else:
                    choose_ss_bs = Q(sector_configured_on__isnull=False)
                organization_customer_devices = Device.objects.filter(
                    ~Q(id__in=ptp_device_circuit_backhaul(specify_type=specify_ptp_type)),
                    choose_ss_bs,  #calls the specific set of devices
                    is_added_to_nms= 1,
                    is_deleted= 0,
                    organization__in= organizations,
                    device_technology= technology
                )
            else:
                organization_customer_devices = Device.objects.filter(
                    ~Q(id__in=ptp_device_circuit_backhaul()),
                    Q(substation__isnull=False)
                    |
                    Q(sector_configured_on__isnull=False),
                    is_added_to_nms= 1,
                    is_deleted= 0,
                    organization__in= organizations,
                    device_technology= technology
                )
        else:
            organization_customer_devices = Device.objects.filter(
                is_added_to_nms= 1,
                substation__isnull=False,
                is_deleted= 0,
                organization__in= organizations,
                device_technology= technology
            )

    return organization_customer_devices


# @cache_for(300)
def organization_network_devices(organizations, technology = None, specify_ptp_bh_type='all'):
    """
    To result back the all the network devices from the respective organization..

    :param organizations:
    :param technology:
    :param organization:
    :return list of network devices
    """


    if not technology:
        organization_network_devices = Device.objects.filter(
                                        Q(id__in= ptp_device_circuit_backhaul())
                                        |
                                        Q(device_technology = int(WiMAX.ID))
                                        |
                                        Q(device_technology = int(PMP.ID)),
                                        is_added_to_nms=1,
                                        is_deleted=0,
                                        organization__in= organizations
        )
    else:
        if int(technology) == int(P2P.ID):
            if specify_ptp_bh_type in ['ss', 'bs']:
                organization_network_devices = Device.objects.filter(
                                            Q(id__in= ptp_device_circuit_backhaul(specify_type=specify_ptp_bh_type)),
                                            is_added_to_nms=1,
                                            is_deleted=0,
                                            organization__in= organizations
                )
            else:
                organization_network_devices = Device.objects.filter(
                                            Q(id__in= ptp_device_circuit_backhaul()),
                                            is_added_to_nms=1,
                                            is_deleted=0,
                                            organization__in= organizations
                )
        else:
            organization_network_devices = Device.objects.filter(
                                            device_technology = int(technology),
                                            is_added_to_nms=1,
                                            sector_configured_on__isnull = False,
                                            sector_configured_on__sector_id__isnull=False, #sector id must be present for PMP and WiMAX
                                            is_deleted=0,
                                            organization__in= organizations
            ).annotate(dcount=Count('id'))

    return organization_network_devices


# @cache_for(300)
def organization_backhaul_devices(organizations, technology = None):
    """
    To result back the all the network devices from the respective organization..

    :param organizations:
    :param technology:
    :param organization:
    :return list of network devices
    """

    return  Device.objects.filter(
                                    backhaul__isnull=False,
                                    is_added_to_nms=1,
                                    is_deleted=0,
                                    organization__in= organizations
    )


@cache_for(300)
def filter_devices(organizations=[],
                   data_tab=None,
                   page_type="customer",
                   required_value_list=[]
                   ):

    """

    :param logged_in_user: authenticated user
    :param data_tab: the technology user wants to retrive
    :return: the list of devices that user has been assigned via organization
    """
    device_list = list()
    organization_devices = list()

    if len(required_value_list):
        device_value_list = required_value_list
    else:
        device_value_list = ['id','machine__name','device_name','ip_address']

    device_tab_technology = data_tab ##
    device_technology_id = None
    try:
        device_technology_id = DeviceTechnology.objects.get(name=device_tab_technology).id
    except Exception as e:
        log.exception("Backhaul Device Filter %s" %(e.message))

    if page_type == "customer":
        device_list = organization_customer_devices(organizations, device_technology_id
        ).values(*device_value_list)
    elif page_type == "network":
        device_list = organization_network_devices(organizations, device_technology_id
        ).values(*device_value_list)
    elif page_type == "other":
        device_list = organization_backhaul_devices(organizations).values(*device_value_list)
    else:
        device_list = []
    # get the devices in an organisation which are added for monitoring
    organization_devices = [
        {
            'device_name': device['device_name'],
            'machine_name': device['machine__name'],
            'id': device['id'],
            'ip_address': device['ip_address']
        }
        for device in device_list
    ]

    return organization_devices


@cache_for(300)
def prepare_machines(device_list):
    """

    :return:
    """
    # Unique machine from the device_list
    unique_device_machine_list = {device['device_machine']: True for device in device_list}.keys()

    machine_dict = {}
    #Creating the machine as a key and device_name as a list for that machine.
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device['device_name'] for device in device_list if
                                 device['device_machine'] == machine]

    return machine_dict
