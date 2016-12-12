""" This module is used to hold varbind info for traps based 
on device types. Creates and sends SNMP traps using pysnmp module"""
import threading
import unicodedata
from pprint import pprint
from pysnmp.hlapi import *
from handlers.db_ops import *
logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error


# variable binding data types
# NOTE: keeping info for int types only, rest will have type str
data_types = {
     'severity': 'i','corr_req': 'i', 'tckt_req': 'i',
    'is_sia': 'i', 'impacted_sector_count': 'i',
   
}

# Trap var binds
# NOTE: Additional fields marked as additional_f_*, can be replaced
# with some useful fields like city, alarm_source etc, accordingly
converter_or_ptpbh_trap_vars = [
    'alrm_id', 'pop_converter_ip', 'bs_converter_ip', 'parent_type', 'parent_ip',
    'parent_port', 'tech', 'alrm_grp', 'alrm_name', 'alrm_desc',
    'bs_switch_ip', 'aggr_switch_ip', 'pe_ip', 'severity', 'time_stamp',
    'bs_name', 'region', 'corr_req', 'tckt_req', 'is_sia',
    'categorization_tier_1', 'categorization_tier_2',
    'alrm_category', 'coverage', 'resource_name', 'resource_type',
    'IOR', 'parent_alrm_id', 'additional_f_1', 'additional_f_2',
    'additional_f_3', 'additional_f_4','additional_f_5','additional_f_6'
]
idu_or_odu_trap_vars = [
        'alrm_id', 'device_ip', 'parent_type', 'parent_ip', 'parent_port',
        'sector_ids', 'tech', 'alrm_grp', 'alrm_name', 'alrm_desc',
        'severity', 'time_stamp', 'bs_name', 'region', 
        'corr_req', 'tckt_req', 'is_sia', 'impacted_sector_count',
        'categorization_tier_1', 'categorization_tier_2', 'alrm_category',
       'coverage', 'resource_name', 'resource_type', 'parent_alrm_id', 
       'additional_f_1', 'additional_f_2', 'additional_f_3', 'additional_f_4', 
       'additional_f_5', 'additional_f_6', 'additional_f_7','additional_f_8',
]
ptp_or_ss_trap_vars = [
        'alrm_id', 'device_ip', 'parent_type', 'parent_ip', 
        'parent_port', 'tech', 'alrm_grp', 'alrm_name', 'alrm_desc',
        'impacted_circuit_id', 'severity', 'time_stamp', 'customer_name', 
        'region', 'corr_req', 'tckt_req', 'is_sia', 'resource_name',
        'resource_type', 'alrm_category', 'additional_f_1', 'additional_f_2',
        'additional_f_3', 'additional_f_4', 'additional_f_5', 'additional_f_6'
]
circuit_ids_trap_vars = [
        'seq_num', 'parent_alrm_id', 'impacted_circuit_ids',
        'alrm_grp', 'alrm_name', 'severity', 'additional_f_1', 
        'additional_f_2', 'last_trap'
]

# base OIDs
OID = '.1.3.6.1.6.3.1.1.4.1.0'
time_ticks = '.1.3.6.1.2.1.1.3.0'
converter_or_ptpbh = '.1.3.6.1.4.1.43900.2.2.1.0.0.1'
idu_or_odu = '.1.3.6.1.4.1.43900.2.2.1.0.1.1'
ptp_or_ss = '.1.3.6.1.4.1.43900.2.2.1.0.2.1'
circuit_ids = '.1.3.6.1.4.1.43900.2.2.1.0.3.1'

# partial OIDs
converter_or_ptpbh_partial = '.1.3.6.1.4.1.43900.2.2.1.0.0.3.1.'
idu_or_odu_partial = '.1.3.6.1.4.1.43900.2.2.1.0.1.3.1.'
ptp_or_ss_partial = '.1.3.6.1.4.1.43900.2.2.1.0.2.3.1.'
circuit_ids_partial = '.1.3.6.1.4.1.43900.2.2.1.0.3.3.1.'

# OID listing based on trap type
converter_or_ptpbh_oids = [''.join([converter_or_ptpbh_partial, str(x)])
                           for x in range(1, 35)]
idu_or_odu_oids = [''.join([idu_or_odu_partial, str(x)]) for x in range(1, 34)]
ptp_or_ss_oids = [''.join([ptp_or_ss_partial, str(x)]) for x in range(1, 27)]
circuit_ids_oids = [''.join([circuit_ids_partial, str(x)]) for x in range(1, 10)]

# (trap_attribute, OID) mapping for each trap type
## NOTE: can't use dict comprehension for python 2.6 compatibility
converter_or_ptpbh_varbinds = dict(
    [(k, v) for k, v in zip(converter_or_ptpbh_trap_vars, converter_or_ptpbh_oids)]
)
idu_or_odu_varbinds = dict([(k, v) for k, v in zip(idu_or_odu_trap_vars, idu_or_odu_oids)])
ptp_or_ss_varbinds = dict([(k, v) for k, v in zip(ptp_or_ss_trap_vars, ptp_or_ss_oids)])
circuit_ids_varbinds = dict(
    [(k, v) for k, v in zip(circuit_ids_trap_vars, circuit_ids_oids)]
)

# updating OID and time_ticks variables for each trap type
common_varbinds = {
    'base_trap_oid': OID,
    'time_ticks': time_ticks,
}
converter_or_ptpbh_varbinds.update(common_varbinds)
idu_or_odu_varbinds.update(common_varbinds)
ptp_or_ss_varbinds.update(common_varbinds)
circuit_ids_varbinds.update(common_varbinds)


class Trap(threading.Thread):
    """ Defines a trap object along with related var binds

    Example
    -------
    >>> trap_opts = {
    ...             'trap_type': 'idu_or_odu_trap',
    ...             'base_trap_oid': '.1.3.6.1.4.1.43900.2.2.1.0.2.1',
    ...             'target_ip': '10.133.19.165', 'target_port': 162,
    ...             'alrm_id': '1221', 'device_ip': '10.141.45.333',
    ...             'alrm_name': 'IDU1_down', 'alrm_desc': 'some desc',
    ...             'bs_name': 'kerdsfs', 'time_ticks': 456472321.45654,
    ...             'time_stamp': 11567345621, 'sector_ids': '12:56434:d43;34:454:3we',
    ...             'tckt_req': 1, 'is_sia': 1,
    ...             }
    >>> trap = Trap(**trap_opts)
    >>> trap.send_trap()
    >>> 

    """

    def __init__(self, **kwds):
	#super(Trap,self).__init__()
	threading.Thread.__init__(self)
        self.__dict__.update(**kwds)
        self._fill_defaults()

    def __getattr__(self, attr):
        return ''

    def run(self):
	self.send_trap()

    def send_trap(self):
        # community auth password
        comm_str = getattr(self, 'comm_str', 'public')
        # UDP transport target
        #target = UdpTransportTarget((getattr(self, 'target_ip', '10.133.12.157'),
        #        getattr(self, 'target_port', 162)))
        target = UdpTransportTarget((getattr(self, 'target_ip', '121.244.255.83'),
                getattr(self, 'target_port', 163)))
        snmp_engine = SnmpEngine()
        # community data
        comm_data = CommunityData(comm_str, mpModel=0)
        # trap context data
        context = ContextData()
        notiftype = NotificationType(
                ObjectIdentity(self.base_trap_oid)
                ).addVarBinds(*self.get_trap_varbinds()) 

        send_notif = sendNotification(
            snmp_engine, comm_data, target,
            context, 'trap', notiftype
        )
        # error_indication - `True` value indicates SNMP engine error
        # error_status - `True` value indicates SNMP PDU error
        # varbinds - MIB variables returned in snmp response
        error_indication, error_status, error_index, varbinds = next(
                send_notif)
    def get_trap_varbinds(self):
        return self._generate_varbinds()

    def _fill_defaults(self):
        """ Provides mandatory instance variables like 
        target_ip, target_port etc, if not provided already"""
        defaults = (('target_ip', '121.244.255.83'), ('target_port', 163),
                ('time_ticks', 444555),)
        for t in defaults:
            # can't call hasattr() as we have already overrided __getattr__
            if not getattr(self, t[0]):
                setattr(self, t[0], t[1])

    def _generate_varbinds(self):
        """ Generates tuples of OIDs along with their values"""
        varbinds = []
        attr_oid_mapping = {}
        tp = self.trap_type
        # default data type
        d_t = OctetString
        if tp == 'converter_or_ptpbh_trap':
            attr_oid_mapping = converter_or_ptpbh_varbinds
        elif tp == 'idu_or_odu_trap':
            attr_oid_mapping = idu_or_odu_varbinds 
        elif tp == 'ptp_or_ss_trap':
            attr_oid_mapping = ptp_or_ss_varbinds
        elif tp == 'circuit_ids_trap':
            attr_oid_mapping = circuit_ids_varbinds
        for (attr, oid) in attr_oid_mapping.items():
            if attr == 'time_ticks':
                d_t = TimeTicks
                # actual OID along with base trap oid
            elif attr == 'base_trap_oid':
                d_t = ObjectIdentifier
            elif data_types.get(attr) == 'i':
                d_t = Integer
            else:
                d_t = OctetString
	    value = getattr(self,attr)
            if attr == 'alrm_name' and value == 'PD threshold breach major' :
		value = 'PD threshold breach'
	    #if attr == 'impacted_sector_count':
	    #	logger.error('impacted_sector_count %s'%str(value))
	    if attr in ['IOR','additional_f_6'] and tp == 'converter_or_ptpbh_trap':
	        value = unicodedata.normalize('NFKD',value).encode('ascii', 'ignore')
	    if not value:
		value = ''
	    try:
                varbinds.append((oid, d_t(value)))
	    except Exception,e:
		logger.error('Error in trap %s %s' % (e,attr))
	  
	logger.error('chanish :varbinds {0}'.format(varbinds))
        return varbinds


if __name__ == '__main__':
    trap_opts = {
                 'trap_type': 'idu_or_odu_trap',
                 'base_trap_oid': '.1.3.6.1.4.1.43900.2.2.1.0.2.1',
                 'target_ip': '10.133.19.165', 'target_port': 162,
                 'alrm_id': '1221', 'device_ip': '10.141.45.333',
                 'alrm_name': 'IDU1_down', 'alrm_desc': 'some desc',
                 'bs_name': 'kerdsfs', 'time_ticks': 456472321,
                 'time_stamp': 1156734562, 'sector_ids': '12:56434:d43;34:454:3we',
                 'tckt_req': 1, 'is_sia': 1,'corr_req':1,'severity':1,'last_count':1,'impacted_sector_count':2,
                 }
    t = Trap(**trap_opts)
    t.start()
