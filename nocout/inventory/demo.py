from celery import task, group
from device.models import Device
from inventory.models import Circuit, Sector
from performance.models import Topology
from inventory.tasks import bulk_update_create
import logging

logger = logging.getLogger(__name__)

# @task
def update_inventory():
    # Sector ID's list.
    sector_ids = set(Sector.objects.values_list('sector_id', flat=True))
    topo_sector_ids = set(Topology.objects.values_list('sector_id', flat=True))
    common_sector_ids = sector_ids.intersection(topo_sector_ids)

    # Sectors & sub stations mapping from Topology.
    topology = Topology.objects.filter(sector_id__in=common_sector_ids).values('connected_device_ip', 'sector_id',
                                                                               'connected_device_mac', 'mac_address',
                                                                               'ip_address')

    # # Sector ID's from Topology.
    # topology_sector_ids = topology.values_list('sector_id', flat=True)

    # Sectors from Inventory corressponding to sector_id's fetched from Topology.
    sectors = Sector.objects.filter(sector_id__in=common_sector_ids)

    # Sector ID's list.
    sector_ids = sectors.values_list('sector_id', flat=True)

    # Sectors Mapper: {<sector_id>: <sector object>, ....} ******************************
    sectors_mapper = {}
    for s_id, obj in zip(sector_ids, sectors):
        sectors_mapper[s_id] = obj

    # BS devices corressponding to the sector_configured_on ip's from Topology.
    bs_devices = Device.objects.filter(ip_address__in=topology.values_list('ip_address', flat=True))

    # BS devices IP's list.
    bs_devices_ips = bs_devices.values_list('ip_address', flat=True)

    # BS Devices Mapper: {<sector_configured_on__ip_address>: <device object>, ....} *****************************
    bs_devices_mapper = {}
    for ip, bs_device in zip(bs_devices_ips, bs_devices):
        bs_devices_mapper[ip] = bs_device

    # Serialized sectors & sub stations mapping from Topology.
    serialized_topology = list(topology)

    # Sectors & sub stations mapping from Circuit.
    circuits = Circuit.objects.select_related('sub_station', 'sub_station__device__ip_address', 'sector__sector_id'
                                              ).filter(sector__sector_id__in=common_sector_ids)

    # Sub Station devices IP's list corressponding to the connected_device_ip ip's.
    circuits_ss_ips = circuits.values_list('sub_station__device__ip_address', flat=True)

    # Circuit Mapper: {<sub_station__device__ip_address>: <circuit object>, ....} **************************
    circuits_mapper = {}
    for ss_ip, circuit in zip(circuits_ss_ips, circuits):
        circuits_mapper[ss_ip] = circuit

    # List of sectors & sub stations mapping from Topology.
    sectors_list = circuits.values('sector__sector_id', 'sub_station__device__ip_address',
                                   'sub_station__device__mac_address',
                                   'sector__sector_configured_on__ip_address',
                                   'sector__sector_configured_on__mac_address')

    # Serialized sectors & sub stations mapping from Circuit.
    serialized_sectors_list = [{'connected_device_ip': a['sub_station__device__ip_address'],
                                'sector_id': a['sector__sector_id'],
                                'connected_device_mac': a['sub_station__device__mac_address'],
                                'mac_address': a['sector__sector_configured_on__mac_address'],
                                'ip_address': a['sector__sector_configured_on__ip_address']} for a in sectors_list]

    # Updated mapping.
    updated_mapping = compare_lists_of_dicts(serialized_sectors_list, serialized_topology)

    print "******************************** serialized_sectors_list len - ", len(serialized_sectors_list)
    print "******************************** serialized_topology len - ", len(serialized_topology)
    print "******************************** updated_mapping len - ", len(updated_mapping)

    print "******************************** uml - ", updated_mapping[0:25]

    sec_up = compare_lists_of_dicts(updated_mapping, serialized_sectors_list)
    topo_up = compare_lists_of_dicts(updated_mapping, serialized_topology)

    print "************************* sec_up - ", len(sec_up)
    print "************************* topo_up - ", len(topo_up)

    update_ss_list = []
    update_device_list = []
    update_circuit_list = []

    # Update inventory from updated topology.
    for info in updated_mapping:
        # Get circuit from inventory.
        circuit = None
        try:
            circuit = circuits_mapper[info['connected_device_ip']]
        except Exception as e:
            logger.info(e.message)

        if circuit:
            try:
                # Update sub station.
                ss = circuit.sub_station
                ss.mac_address = info['connected_device_mac']
                update_ss_list.append(ss)
            except Exception as e:
                logger.info(e.message)

            try:
                # Update sub station device.
                ss_device = circuit.sub_station.device
                ss_device.ip_address = info['connected_device_ip']
                ss_device.mac_address = info['connected_device_mac']
                update_device_list.append(ss_device)
            except Exception as e:
                logger.info(e.message)

            try:
                sector_device = bs_devices_mapper[info['ip_address']]
                sector_device.mac_address = info['mac_address']
                update_device_list.append(sector_device)
            except Exception as e:
                logger.info(e.message)

            try:
                circuit.sector = sectors_mapper[info['sector_id']]
                update_circuit_list.append(circuit)
            except Exception as e:
                logger.info(e.message)

    # g_jobs = list()
    #
    # if len(update_ss_list):
    #     g_jobs.append(bulk_update_create.s(bulky=update_ss_list, action='update'))
    #
    # if len(update_device_list):
    #     g_jobs.append(bulk_update_create.s(bulky=update_device_list, action='update'))
    #
    # if len(update_circuit_list):
    #     g_jobs.append(bulk_update_create.s(bulky=update_circuit_list, action='update'))
    #
    # print "************************ update_ss_list - ", len(update_ss_list)
    # print "************************ update_device_list - ", len(update_device_list)
    # print "************************ update_circuit_list - ", len(update_circuit_list)
    #
    # if not len(g_jobs):
    #     return False
    #
    # job = group(g_jobs)
    # result = job.apply_async()
    #
    # return result


def compare_lists_of_dicts(list1, list2):
    # print "************************ list1 - ", list1[0:10]
    # print "************************ list2 - ", list2[0:10]
    check = set([(d['connected_device_ip'],
                  d['sector_id'],
                  d['connected_device_mac'],
                  d['mac_address'],
                  d['ip_address']
                  ) for d in list2])

    return [d for d in list1 if (d['connected_device_ip'],
                                 d['sector_id'],
                                 d['connected_device_mac'],
                                 d['mac_address'],
                                 d['ip_address']
                                 ) not in check]

def sample():
    list1 = [{'a': 1, 'b': 2, 'c': 3, 'd': 4},
             {'a': 1, 'b': 8, 'c': 3, 'd': 4},
             {'a': 1, 'b': 2, 'c': 3, 'd': 7}]

    list2 = [{'a': 1, 'b': 2, 'c': 3, 'd': 4},
             {'a': 1, 'b': 8, 'c': 3, 'd': 5},
             {'a': 1, 'b': 2, 'c': 3, 'd': 7},
             {'a': 1, 'b': 2, 'c': 3, 'd': 11}]

    return compare_lists(list2, list1)

def compare_lists(list1, list2):
    check = set(
        [(d['a'], d['b'], d['c'], d['d']) for d
         in list2])

    return [d for d in list1 if (d['a'], d['b'], d['c'], d['d']) not in check]
