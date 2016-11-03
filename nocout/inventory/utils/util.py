# -*- coding: utf-8 -*-
# nocout project settings # TODO: Remove the HARDCODED technology IDs
from nocout.settings import P2P, WiMAX, PMP, CACHE_TIME

#django core model functions
from django.db.models import Count, Q

#nocout specific functions
from device.models import Device, DeviceTechnology, DeviceType, DeviceFrequency

#inventory specific functions
from inventory.models import Sector, Circuit, SubStation, Backhaul

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

#logging the performance of function
import logging
log = logging.getLogger(__name__)
# logging the performance of function

VALID_PAGE_LIST = ["customer", "network", "backhaul", "others"]
VALID_SPECIFICATION = ['all', 'ss', 'bs']

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


class InventoryUtilsGateway:
    """
    This class works as gateway between inventory utils & other apps
    """
    def ptp_device_circuit_backhaul(self, specify_type='all'):
        """

        :param specify_type:
        """
        param1 = ptp_device_circuit_backhaul(specify_type=specify_type)

        return param1

    def organization_customer_devices(
        self,
        organizations,
        is_rad5 = False,
        technology=None, 
        specify_ptp_type='all'
    ):
        """

        :param technology:
        :param specify_ptp_type:
        :param organizations:
        """
        param1 = organization_customer_devices(
            organizations,
            is_rad5,
            technology=technology,
            specify_ptp_type=specify_ptp_type
        )

        return param1

    def organization_network_devices(
        self, 
        organizations, 
        is_rad5=False,
        technology=None, 
        specify_ptp_bh_type='all'
    ):
        """

        :param organizations:
        :param technology:
        :param specify_ptp_bh_type:
        """
        param1 = organization_network_devices(
            organizations,
            is_rad5,
            technology=technology, 
            specify_ptp_bh_type=specify_ptp_bh_type
        )

        return param1

    def organization_backhaul_devices(
        self, 
        organizations, 
        technology=None, 
        others=False, 
        other_type="backhaul"
    ):
        """

        :param organizations:
        :param others:
        :param other_type:
        :param technology:
        """
        param1 = organization_backhaul_devices(
            organizations, 
            technology=technology, 
            others=others, 
            other_type=other_type
        )

        return param1

    def filter_devices(
        self, 
        organizations, 
        is_rad5=False,
        data_tab=None, 
        page_type="customer", 
        other_type=None, 
        required_value_list=None, 
        other_bh=False,
        specify_ptp_bh_type='all'
    ):
        """

        :param organizations:
        :param page_type:
        :param required_value_list:
        :param other_bh:
        :param other_type:
        :param data_tab:
        """

        param1 = filter_devices(
            organizations, 
            is_rad5,
            data_tab=data_tab, 
            page_type=page_type, 
            other_type=other_type, 
            required_value_list=required_value_list, 
            other_bh=other_bh,
            specify_ptp_bh_type=specify_ptp_bh_type
        )

        return param1

    def prepare_machines(self, device_list, machine_key='device_machine'):
        """

        :param device_list:
        :param machine_key:
        """
        param1 = prepare_machines(device_list, machine_key=machine_key)

        return param1

    def organization_sectors(self, organization, technology=0):
        """

        :param technology:
        :param organization:
        """
        param1 = organization_sectors(organization, technology=technology)

        return param1

    def list_to_indexed_dict(self, inventory_list, key):
        """

        :param key:
        :param inventory_list:
        """
        param1 = list_to_indexed_dict(inventory_list, key)

        return param1


def organization_monitored_devices(organizations, **kwargs):
    """
    Common function to get the devices
    :param organizations: list of organizations
    :param kwargs: keyword arguments defining the elements that are required to be gathered
    :return: Devices for the organization, based on the argumentas passed
    """
    if not organizations:
        return list()
    organizations = nocout_utils.check_item_is_list(organizations)

    organization_devices = Device.objects.select_related(
        'organization',
        'substation_set',
        'substation_set__circuit_set',
        'substation_set__circuit_set__sector',
        'backhaul',
        'backhaul_pop',
        'backhaul_aggregator',
        'backhaul_switch',
        'sector_configured_on',
        'sector_configured_on__base_station',
        'sector_configured_on__base_station__city',
        'sector_configured_on__base_station__state',
        'sector_configured_on__base_station__bs_switch',
        'machine',
        'site_instance'
    ).filter(
        is_added_to_nms__gt=0,
        # is_added_to_nms=1,
        is_deleted=0,
        organization__in=organizations
    )

    if {'technology'}.issubset(kwargs.keys()):
        # technology would denote the section to be monitored devices
        # this must be the name of the technology
        # or the ID of the technology
        required_techs = nocout_utils.check_item_is_list(kwargs['technology'])

        try:
            technology = DeviceTechnology.objects.filter(
                id__in=required_techs
            )
        except Exception, e:
            technology = DeviceTechnology.objects.filter(
                name__in=required_techs
            )

        technology = technology.values_list('id', flat=True)
        organization_devices = organization_devices.filter(
            device_technology__in=technology
        )
    else:
        organization_devices = organization_devices

    if {'page_type'}.issubset(kwargs.keys()) and {kwargs['page_type']}.issubset(VALID_PAGE_LIST):
        # can be re-written as set(['page_type', 'technology']).issubset(kwargs.keys())
        page = kwargs['page_type']  # customer, network, backhaul, others
        # check about the P2P devices
        # what are the P2P devices required ?
        if page == 'customer':
            # check for the P2P devices required
            # by the configuration of ' specify_type ' = all. ss. bs
            if {'specify_type'}.issubset(kwargs.keys()):
                # this means that key is present
                # key must indicate one of the words all. ss. bs
                type_specification = kwargs['specify_type']
                if {type_specification}.issubset(VALID_SPECIFICATION):
                    pass
                ptp_bh = ptp_device_circuit_backhaul(specify_type=type_specification)
                organization_devices = organization_devices.exclude(
                    id__in=ptp_bh
                )
            else:
                # it is now assumed that devices are not PTP
                # so PMP and WiMAX
                organization_devices = organization_devices.filter(
                    substation__isnull=False,
                    substation__circuit__isnull=False,
                    substation__circuit__sector__isnull=False,
                    substation__circuit__sector__sector_configured_on__isnull=False
                )
            return organization_devices
        elif page == 'network':
            pass
        elif page == 'backhaul':
            pass
        elif page == 'others':
            pass
        else:
            return organization_devices


def ptp_device_circuit_backhaul(specify_type='all'):
    """
    Special case fot PTP technology devices. Wherein Circuit type backhaul is required
    :param specify_type:
    :return:
    """
    if specify_type == 'all':
        device_list_with_circuit_type_backhaul = Device.objects.filter(
            Q(
                id__in=Sector.objects.filter(
                    id__in=Circuit.objects.filter(
                        circuit_type__icontains="Backhaul"
                    ).values_list('sector', flat=True)
                ).values_list('sector_configured_on', flat=True)
            )
            |
            Q(
                id__in=SubStation.objects.filter(
                    id__in=Circuit.objects.filter(
                        circuit_type__icontains="Backhaul"
                    ).values_list('sub_station', flat=True)
                ).values_list('device', flat=True)
            )
        )
    elif specify_type == 'ss':
        device_list_with_circuit_type_backhaul = Device.objects.filter(
            Q(
                id__in=SubStation.objects.filter(
                    id__in=Circuit.objects.filter(
                        circuit_type__icontains="Backhaul"
                    ).values_list('sub_station', flat=True)
                ).values_list('device', flat=True)
            )
        )
    elif specify_type == 'bs':
        device_list_with_circuit_type_backhaul = Device.objects.filter(
            Q(
                id__in=Sector.objects.filter(
                    id__in=Circuit.objects.filter(
                        circuit_type__icontains="Backhaul"
                    ).values_list('sector', flat=True)
                ).values_list('sector_configured_on', flat=True)
            )
        )
    else:
        device_list_with_circuit_type_backhaul = []

    return device_list_with_circuit_type_backhaul


def organization_customer_devices(organizations, is_rad5=False, technology=None, specify_ptp_type='all'):
    """
    To result back the all the customer devices from the respective organization..


    :param specify_ptp_type:
    :param technology:
    :param organizations:
    :return list of customer devices
    """
    if not technology:
        customer_devices = Device.objects.filter(
            Q(sector_configured_on__isnull=False) 
            | 
            Q(substation__isnull=False),
            is_added_to_nms__gt=0,
            # is_added_to_nms=1,
            is_deleted=0,
            organization__in=organizations
        )
    else:
        if int(technology) == int(P2P.ID):
            if specify_ptp_type in ['ss', 'bs']:
                if specify_ptp_type == 'ss':
                    choose_ss_bs = Q(substation__isnull=False)
                else:
                    choose_ss_bs = Q(sector_configured_on__isnull=False)

                customer_devices = Device.objects.filter(
                    ~Q(id__in=ptp_device_circuit_backhaul(specify_type=specify_ptp_type)),
                    choose_ss_bs,  # calls the specific set of devices
                    is_added_to_nms__gt=0,
                    # is_added_to_nms=1,
                    is_deleted=0,
                    organization__in=organizations,
                    device_technology=technology
                )
            else:
                customer_devices = Device.objects.filter(
                    ~Q(id__in=ptp_device_circuit_backhaul()),
                    Q(substation__isnull=False)
                    |
                    Q(sector_configured_on__isnull=False),
                    is_added_to_nms__gt=0,
                    # is_added_to_nms=1,
                    is_deleted=0,
                    organization__in=organizations,
                    device_technology=technology
                )
        else:
            customer_devices = Device.objects.filter(
                is_added_to_nms__gt=0,
                # is_added_to_nms=1,
                substation__isnull=False,
                is_deleted=0,
                organization__in=organizations,
                device_technology=technology
            )

            try:
                rad5_device_type_id = DeviceType.objects.get(name='Radwin5KSS').id
            except Exception, e:
                rad5_device_type_id = None

            # Filtering device queryset further for radwin devices
            if is_rad5 and int(technology) == int(PMP.ID):
                customer_devices = customer_devices.filter(device_type=rad5_device_type_id)
            elif (not is_rad5) and (int(technology) == int(PMP.ID)):
                customer_devices = customer_devices.exclude(device_type=rad5_device_type_id)
            else:
                pass

    return customer_devices


def organization_network_devices(organizations, is_rad5=False, technology=None, specify_ptp_bh_type='all'):
    """
    To result back the all the network devices from the respective organization..

    :param specify_ptp_bh_type:
    :param organizations:
    :param technology:
    :param organizations:
    :return list of network devices
    """
    if not technology and specify_ptp_bh_type:
        devices = Device.objects.filter(
            Q(id__in=ptp_device_circuit_backhaul())
            |
            (
                Q(
                    device_technology=int(PMP.ID),
                    sector_configured_on__isnull=False,
                    sector_configured_on__sector_id__isnull=False
                )
                |
                Q(
                    device_technology=int(WiMAX.ID),
                    sector_configured_on__isnull=False,
                    sector_configured_on__sector_id__isnull=False
                )
            ),
            is_added_to_nms__gt=0,
            # is_added_to_nms=1,
            is_deleted=0,
            organization__in=organizations
        )

    elif (not technology) and (not specify_ptp_bh_type):
        devices = Device.objects.filter(
            Q(
                device_technology=int(PMP.ID),
                sector_configured_on__isnull=False,
                sector_configured_on__sector_id__isnull=False
            )
            |
            Q(
                Q(device_technology=int(WiMAX.ID))
        &
        Q(
            Q(
                sector_configured_on__isnull=False,
                sector_configured_on__sector_id__isnull=False
            )
            |
            Q(dr_configured_on__isnull=False)
        )
            ),
            is_added_to_nms__gt=0,
            # is_added_to_nms=1,
            is_deleted=0,
            organization__in=organizations
        )

    else:
        if int(technology) == int(P2P.ID):
            if specify_ptp_bh_type in ['ss', 'bs']:
                devices = Device.objects.filter(
                    Q(
                        id__in=ptp_device_circuit_backhaul(
                            specify_type=specify_ptp_bh_type
                        )
                    ),
                    is_added_to_nms__gt=0,
                    # is_added_to_nms=1,
                    is_deleted=0,
                    organization__in=organizations
                )
            else:
                devices = Device.objects.filter(
                    Q(
                        id__in=ptp_device_circuit_backhaul()
                    ),
                    is_added_to_nms__gt=0,
                    # is_added_to_nms=1,
                    is_deleted=0,
                    organization__in=organizations
                )
        elif int(technology) == int(WiMAX.ID):
            devices = Device.objects.filter(
                Q(
                    sector_configured_on__isnull=False,
                    sector_configured_on__sector_id__isnull=False
                )
                |
                Q(dr_configured_on__isnull=False),
                device_technology=int(technology),
                is_added_to_nms__gt=0,
                # is_added_to_nms=1,  # sector id must be present for PMP and WiMAX
                is_deleted=0,
                organization__in=organizations
            ).annotate(dcount=Count('id'))
        else:
            devices = Device.objects.filter(
                device_technology=int(technology),
                is_added_to_nms__gt=0,
                # is_added_to_nms=1,
                sector_configured_on__isnull=False,
                sector_configured_on__sector_id__isnull=False,  # sector id must be present for PMP and WiMAX
                is_deleted=0,
                organization__in=organizations
            ).annotate(dcount=Count('id'))
            
            try:
                rad5_device_type_id = DeviceType.objects.get(name='Radwin5KBS').id
            except Exception, e:
                rad5_device_type_id = None

            # Filtering device queryset further for radwin devices
            if is_rad5:
                devices = devices.filter(device_type=rad5_device_type_id)
            else:
                devices = devices.exclude(device_type=rad5_device_type_id)


    return devices


def organization_backhaul_devices(organizations, technology=None, others=False, other_type="backhaul"):
    """
    To result back the all the network devices from the respective organization..

    :param other_type:
    :param others:
    :param organizations:
    :param technology:
    :param organizations:
    :return list of network devices
    """
    if other_type == 'pe':
        try:
            pe_tech_id = DeviceTechnology.objects.filter(
                name__iexact='pe'
            ).values_list('id', flat=True)

            backhaul_devices = Device.objects.filter(
                pe_ip__isnull=False,
                is_added_to_nms__gt=0,
                device_technology__in=pe_tech_id,
                is_deleted=0,
                organization__in=organizations
            ).prefetch_related('backhaul')
        except Exception, e:
            backhaul_devices = list()
            log.error('PE Device Tech Filtering Error')
            log.error(e)
            pass
    else:
        backhaul_devices = Device.objects.filter(
            backhaul__isnull=False,
            is_added_to_nms__gt=0,
            # is_added_to_nms=1,
            is_deleted=0,
            organization__in=organizations
        ).prefetch_related('backhaul')
    
    if others:
        backhaul_objects = Backhaul.objects.filter(
            bh_configured_on_id__in=backhaul_devices.values_list('id', flat=True)
        )

        backhaul_devices = Device.objects.filter(
            ~Q(id__in=backhaul_devices.values_list('id', flat=True)),
            (
                Q(
                    id__in=backhaul_objects.filter(
                        pop__isnull=False
                    ).values_list('pop', flat=True)
                )
                |
                Q(
                    id__in=backhaul_objects.filter(
                        aggregator__isnull=False
                    ).values_list('aggregator', flat=True)
                )
                |
                Q(
                    id__in=backhaul_objects.filter(
                        bh_switch__isnull=False
                    ).values_list('bh_switch', flat=True)
                )
            ),
            is_added_to_nms__gt=0,
            # is_added_to_nms=1,
            is_deleted=0,
            organization__in=organizations
        )
    
    return backhaul_devices.annotate(dcount=Count('id'))


@nocout_utils.cache_for(CACHE_TIME.get('INVENTORY', 300))
def filter_devices(
    organizations, 
    is_rad5,
    data_tab=None,
    page_type="customer", 
    other_type=None, 
    required_value_list=None, 
    other_bh=False,
    specify_ptp_bh_type='all'
):

    """


    :param other_type:
    :param organizations: list of organizations
    :param data_tab: technology
    :param page_type: customer, network, backhaul, others
    :param required_value_list: values list
    :param other_bh: other than backhaul objects
    :return: list of devices
    """
    if not organizations:
        return list()

    if required_value_list:
        device_value_list = required_value_list
    else:
        device_value_list = [
            'id', 
            'machine__name', 
            'device_name', 
            'ip_address',
            'organization__alias'
        ]

    device_tab_technology = data_tab
    # This is for handling report download for radwin5 devices
    # Because Radwin5 is device type and not technology.
    if device_tab_technology and device_tab_technology.lower() == 'radwin5':
        device_tab_technology = 'PMP'
        is_rad5 = True
    device_technology_id = None

    try:
        device_technology_id = DeviceTechnology.objects.get(name=device_tab_technology).id
    except Exception as e:
        log.exception("Backhaul Device Filter %s" % e.message)

    if page_type == "customer":
        device_list = organization_customer_devices(
            organizations,
            is_rad5,
            device_technology_id
        ).values(*device_value_list)
    elif page_type == "network":
        device_list = organization_network_devices(
            organizations,
            is_rad5,
            device_technology_id,
        ).values(*device_value_list)
    elif page_type == "other":
        is_other = False
        if other_type not in ["backhaul", "pe"]:
            is_other = True
        
        device_list = organization_backhaul_devices(
            organizations,
            others=is_other,
            other_type=other_type
        ).values(*device_value_list)

    else:
        device_list = []
    # get the devices in an organisation which are added for monitoring
    organization_devices = [
        {
            'device_name': device['device_name'],
            'machine_name': device['machine__name'],
            'id': device['id'],
            'ip_address': device['ip_address'],
            'organization_id' : device.get('organization__id'),
            # 'region': device.get('organization__alias', 'NA')
        }
        for device in device_list
    ]

    return organization_devices


@nocout_utils.cache_for(CACHE_TIME.get('INVENTORY', 300))
def prepare_machines(device_list, machine_key='device_machine'):
    """


    :param device_list:
    :param machine_key:
    :return:
    """
    # Unique machine from the device_list
    unique_device_machine_list = {device[machine_key]: True for device in device_list}.keys()

    machine_dict = {}
    #Creating the machine as a key and device_name as a list for that machine.
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device['device_name'] for device in device_list if
                                 device[machine_key] == machine]

    return machine_dict


def organization_sectors(organization, technology=0):
    """
    To result back the all the sector from the respective organization.

    :param organization: organization list
    :param technology:
    :return list of sector
    """
    sector_objects = Sector.objects.select_related(
        'sector_configured_on',
        'sector_configured_on__machine',
        'sector_configured_on__site_instance',
        'organization'
    ).filter(
        sector_configured_on__is_added_to_nms__gt=0,
        # sector_configured_on__is_added_to_nms=1,
        sector_configured_on__isnull=False
    )

    if organization:
        sector_objects = sector_objects.filter(organization__in=organization)

    if int(technology) == int(PMP.ID):
        sector_list = sector_objects.filter(
            sector_id__isnull=False,
            sector_configured_on_port__isnull=True,
            sector_configured_on__device_technology=technology
        ).annotate(
            total_sector=Count('sector_id')
        )

    elif int(technology) == int(WiMAX.ID):
        sector_list = sector_objects.select_related(
            'sector_configured_on_port'
        ).filter(
            sector_id__isnull=False,
            sector_configured_on_port__isnull=False,
            sector_configured_on__device_technology=technology
        ).annotate(
            total_sector=Count('sector_id')
        )

    elif int(technology) == int(P2P.ID):
        sector_list = Sector.objects.select_related(
            'sector_configured_on',
            'sector_configured_on__machine',
            'sector_configured_on__site_instance',
            'organization',
        ).filter(
            sector_configured_on__device_technology=technology
        ).annotate(
            total_sector=Count('id')
        )

    else:
        sector_list = sector_objects

    return sector_list


@nocout_utils.cache_for(CACHE_TIME.get('INVENTORY', 300))
def list_to_indexed_dict(inventory_list, key):
    """
    Convert list of dictionaries into indexed dictionaries

    :param inventory_list:
    :param key:
    Args:
        inventory_list (list): List of dictionaries
        key (str): Element needs to be the key of dictionary

    Returns:
        inventory_dict (dict): containing list of dictionaries
                    i.e.{u'10518': {
                                'bs_name': u'SAMALKHA',
                                'circuit_id': u'1131176457',
                                'city': u'Delhi',
                                'customer_name': u'SPFLSecuritiesLtd.',
                                'device_name': u'10518',
                                'device_technology': u'WiMAX',
                                'device_type': u'StarmaxIDU',
                                'machine__name': u'ospf3',
                                'near_end_ip': u'10.158.176.2',
                                'sector_id': u'(PMP1)</BR>00: 0b: 10: 05: 39: 61',
                                'state': u'Delhi'
                            }
                        }

    """

    inventory_dict = dict()

    for device_info in inventory_list:
        if device_info[key] not in inventory_dict:
            inventory_dict[device_info[key]] = {}

        inventory_dict[device_info[key]] = device_info

    return inventory_dict


@nocout_utils.cache_for(CACHE_TIME.get('INVENTORY', 3600))
def getDeviceTypeNamedDict():
    """
    This function returns device type data dict with devicetype name as key
    """
    device_type_dict = dict()

    deviceTypeObj = DeviceType.objects.all()

    for device_type in deviceTypeObj:
        if device_type.name not in device_type_dict:
            if len(str(device_type.device_gmap_icon)) > 5:
                img_url = str("media/"+ str(device_type.device_gmap_icon)) if "uploaded" in str(device_type.device_gmap_icon) else "static/img/" + str(device_type.device_gmap_icon)
            else:
                img_url = 'static/img/icons/mobilephonetower10.png'

            device_type_dict[device_type.name] = {
                'gmap_icon': img_url
            }

    return device_type_dict

@nocout_utils.cache_for(CACHE_TIME.get('INVENTORY', 3600))
def getFrequencyDict():
    """
    This function returns all frequency name & color in dict with id(PK) as key
    """
    frequency_dict = dict()

    freq_obj = DeviceFrequency.objects.all()

    for freq in freq_obj:
        pk = str(freq.id)
        if pk not in frequency_dict:
            frequency_dict[pk] = {
                'color': freq.color_hex_value,
                'value': freq.value,
                'radius': freq.frequency_radius
            }


    return frequency_dict
