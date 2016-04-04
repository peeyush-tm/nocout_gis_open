#from nocout_site import *
from start.start import app
from handlers.db_ops import *
from uuid import uuid4
from datetime import datetime
from collections import defaultdict
from copy import deepcopy
import itertools
logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error

def generateuuid():
	return str(uuid4())

converter_or_ptpbh_trap_vars = [
    'alrm_id', 'pop_converter_ip', 'bs_converter_ip', 'parent_type', 'parent_ip',
    'parent_port', 'tech', 'alrm_grp', 'alrm_name', 'alrm_desc',
    'bs_switch_ip', 'aggr_switch_ip', 'pe_ip', 'severity', 'time_stamp',
    'bs_name', 'region', 'corr_req', 'tckt_req', 'is_sia',
    'categorization_tier_1', 'categorization_tier_2',
    'alrm_category', 'coverage', 'resource_name', 'resource_type',
    'IOR', 'parent_alrm_id', 'additional_f_1', 'additional_f_2',
    'additional_f_3', 'additional_f_4',

]
idu_or_odu_trap_vars = [
        'alrm_id', 'device_ip', 'parent_type', 'parent_ip', 'parent_port',
        'sector_ids', 'tech', 'alrm_grp', 'alrm_name', 'alrm_desc',
        'severity', 'time_stamp', 'bs_name', 'region', 
        'corr_req', 'tckt_req', 'is_sia', 'impacted_sector_count',
        'categorization_tier_1', 'categorization_tier_2',
        'alrm_category', 'coverage', 'resource_name', 'resource_type',
        'parent_alrm_id', 'additional_f_1', 'additional_f_2', 'additional_f_3', 
        'additional_f_4', 'additional_f_5', 'additional_f_6', 'additional_f_7',
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
        'alrm_group', 'alrm_name', 'severity', 'additional_f_1', 
        'additional_f_2', 'last_trap'
]

conv_switch_mapping_dict = {
	'alrm_desc': 'alarm_description','alrm_name':'alarm_name','time_stamp':'timestamp',
        'severity':'severity','tech':'technology','resource_name':'ip_address','pop_converter_ip':'pop_ip',
	'parent_ip':'parent_ip','parent_type':'parent_type','parent_port':'parent_port','bs_switch_ip':'bs_switch_ip',
	'aggr_switch_ip':'aggr_switch','pe_ip':'pe_ip','bs_name':'bs_name','region':'region','resource_type':'resource_type',	
	'coverage':'coverage','additional_f_1':'additional_f_1','additional_f_2':'additional_f_2',
	'additional_f_3':'additional_f_3','categorization_tier_1':'categorization_tier_1','bs_converter_ip':'bts_conv_ip',
	'categorization_tier_2':'categorization_tier_2','alrm_id':'unique_id','alrm_grp':'category',
	'corr_req':'correlation','tckt_req':'auto_tt','is_sia':'sia','alrm_category':'category',
	'IOR':'ior','parent_alrm_id':'parent_alarm_id','additional_f_4':'resource_type'	
}
bs_mapping_dict = {'alrm_desc': 'alarm_description',
	'alrm_name':'alarm_name','time_stamp':'timestamp',
    	'severity':'severity','tech':'technology','resource_name':'ip_address',
    	'parent_ip':'parent_ip','parent_type':'parent_type','parent_port':'parent_port',
	'bs_name':'bs_name','region':'region','resource_type':'resource_type','sector_ids':'sector_id',
    	'coverage':'coverage','additional_f_1':'additional_f_1','additional_f_2':'additional_f_2',
    	'additional_f_3':'city','categorization_tier_1':'categorization_tier_1',
	'impacted_sector_count':'impacted_sector_count','device_ip':'ip_address',
	'categorization_tier_2':'categorization_tier_2','alrm_id':'unique_id','alrm_grp':'category',
	'corr_req':'correlation','tckt_req':'auto_tt','is_sia':'sia','alrm_category':'category',
    	'parent_alrm_id':'parent_alarm_id','additional_f_4':'additional_f_4','additional_f_5':'additional_f_5',
	'additional_f_6':'aggr_switch','additional_f_7':'pe_ip','additional_f_8':'additional_f_8'	
}

ss_mapping_dict = {'alrm_desc': 'alarm_description',
	'alrm_name':'alarm_name','time_stamp':'timestamp',
    	'severity':'severity','tech':'technology','resource_name':'ip_address',
    	'parent_ip':'parent_ip','parent_type':'parent_type','parent_port':'parent_port',
	'region':'region','resource_type':'resource_type',
    	'device_ip':'ip_address','additional_f_1':'additional_f_1','additional_f_2':'additional_f_2',
    	'additional_f_3':'city','customer_name':'customer_name',
	'impacted_circuit_id':'impacted_circuit_id','alrm_id':'unique_id','alrm_grp':'category',
	'corr_req':'correlation','tckt_req':'auto_tt','is_sia':'sia','alrm_category':'category',
	'additional_f_4':'additional_f_4','additional_f_5':'additional_f_5','child':'child',
	'additional_f_6':'bs_name'
}

ALARM_FLAGS = {
	      'critical': 1,
	      '0': 'no'
}
class correlation(object):
    def __init__(self):
        pass


    def find(self,key, invent_dict):
	for k, v in invent_dict.iteritems():
            if k == key:
	        yield v     
            elif isinstance(v, dict):
                for result in self.find(key, v):
                    yield result
   
    def redis_conn(self):
        rds_cli = RedisInterface(custom_conf={'db': 5})
        redis_conn =  rds_cli.redis_cnx
    	return redis_conn 
 
    def update_redis_inventory_hiearachy(self,redis_conn,current_events):
	event_dict = {}
        ih_dict = {}
	#logger.error("Before updating")
	my_useful_list = filter(lambda x: x[1] == 'Device_not_reachable',current_events )
	#logger.error("{0}".format(my_useful_list))
	for event in current_events:
	    if 'Device_not_reachable' in event[1]:
	        ip = event[3]
                static_data = redis_conn.get('static_'+ip)
	        if static_data:
	            static_data = eval(static_data)
		    inventory_id = static_data['inventory_id']
		    if not ih_dict.get(inventory_id):
	            	inventory_hierarchy = redis_conn.get(inventory_id)
		    	if inventory_hierarchy:
		    	    inventory_hierarchy = eval(inventory_hierarchy)
			if not inventory_hierarchy.get('ip_list'):
			    inventory_hierarchy.setdefault('ip_list',set())
			timestamp = inventory_hierarchy.get('timestamp')
			ih_dict[inventory_id]=inventory_hierarchy
			if not timestamp and event[6] != 'clear':
			    ih_dict[inventory_id]['timestamp'] = datetime.strptime(event[8],"%Y-%m-%d %H:%M:%S").strftime('%s')
				
		    ih_count = ih_dict[inventory_id].get(ip)
                    oldest_time = ih_dict[inventory_id].get('timestamp')
		    if not oldest_time and event[6] != 'clear':
			ih_dict[inventory_id]['timestamp'] =  datetime.strptime(event[8],"%Y-%m-%d %H:%M:%S").strftime('%s')
		    if event[6] != 'clear' and (int(ih_dict[inventory_id]['timestamp']) - int(datetime.now().strftime('%s')) > 660):
		    	ih_dict[inventory_id]['timestamp'] =  datetime.strptime(event[8],"%Y-%m-%d %H:%M:%S").strftime('%s')
			
		    if ih_count:
		    	if not event_dict.get(ih_count):
	    	    	    device_invent_dict = redis_conn.get(ih_count)
		    	    if device_invent_dict:
	                        device_invent_dict = eval(device_invent_dict)
		        else:
			    device_invent_dict=event_dict[ih_count]
			if event[6] == 'clear':
			    if ih_count in ih_dict[inventory_id]['ip_list']:
			        ih_dict[inventory_id]['ip_list'].remove(ih_count)
				if len(ih_dict[inventory_id]['ip_list']) == 0:
				    ih_dict[inventory_id]['timestamp']= ''
			    	    ih_dict[inventory_id]['change_bit'] = 0
			    if device_invent_dict and device_invent_dict.get('inventory_id'):
				id = device_invent_dict.get('inventory_id')
			        device_invent_dict={}
				device_invent_dict['inventory_id'] = id
			    event_dict[ih_count]=device_invent_dict
			elif event[6] != 'clear' and device_invent_dict:
			    device_invent_dict['alarm_name'] = event[1]
			    device_invent_dict['alarm_description'] = event[2]
			    device_invent_dict['timestamp'] = datetime.strptime(event[8],"%Y-%m-%d %H:%M:%S").strftime('%s')
			    device_invent_dict['severity'] = event[6]
			    device_invent_dict['unique_id'] = generateuuid()
			    device_invent_dict['ip_address'] = ip
			    event_dict[ih_count]=device_invent_dict
			    # Storing all device redis id in that hirearchy for which alarm is updated
			    ih_dict[inventory_id]['ip_list'].add(ih_count)
			    ih_dict[inventory_id]['change_bit'] = 1
	# Code commented for sending clear traps Needs to be modified
	"""    if 'Device_not_reachable' in event[1] and 'clear' in event[6]:
		ip = event[3]
		key = 'trap_Device_not_reachable_'+ip
		if redis_conn.exist(key):
		    trap = redis_conn.get(key)
		    trap = eval(trap_dict)
		    trap['severity'] = 'clear'
		    trap = list(trap)
		    trap_sender_task(trap).apply_async()
		    redis_conn.del(key)
        """

        self.insert_events_into_redis(event_dict)
        self.insert_events_into_redis(ih_dict)
	#logger.error("final event list")
	#logger.error("{0}\n\n".format(event_dict))

    def insert_events_into_redis(self,event_dict,is_list=None):
        p = self.redis_conn().pipeline()
        if is_list:
            [p.set(ih_count_id,event_entry) for event in event_dict for (ih_count_id,event_entry) in event.iteritems() ]
	else:
            [p.set(ih_count_id,event) for (ih_count_id,event) in event_dict.iteritems() ]
        p.execute()
    
    def make_dict_for_ckt(self,**kwargs):
	mapping_list = [
	    'seq_num', 'parent_alrm_id', 'impacted_circuit_ids',
	    'alrm_group', 'alrm_name', 'severity', 'additional_f_1','additional_f_2', 'last_trap'
	]
	alarm_id = kwargs['alarm_id']
	ckt_dict = kwargs['ckt_dict']
	event_trap_dict = {}
	alrm_id = None 
	final_ckt_list = list()
	if kwargs.get('idu_odu_trap_dict'):
	    idu_odu_trap_dict = kwargs['idu_odu_trap_dict']
	    for key,value in idu_odu_trap_dict.iteritems():
		if ckt_dict.get(key):
		    ckt_list = ",".join([ckt for ckt in ckt_dict.get(key) ])	
		else:
		    continue

		event_trap_dict['seq_num'] = generateuuid()
		if value.get('parent_alrm_id'):
		    alrm_id = value.get('parent_alrm_id')
		else:
		    alrm_id = value.get('alrm_id') 
		event_trap_dict['parent_alrm_id'] = alrm_id 
		event_trap_dict['impacted_circuit_ids'] = ckt_list
		event_trap_dict['alrm_name'] = value.get('alrm_name')  
		event_trap_dict['alrm_grp'] = value.get('alrm_grp')  
		event_trap_dict['severity'] = value.get('severity')
		event_trap_dict['additional_f_1'] = ''
		event_trap_dict['additional_f_2'] = ''
		event_trap_dict['last_trap'] = ''
		final_ckt_list.append(event_trap_dict)
		event_trap_dict = {}
	return final_ckt_list

    # Creating Trap dictionary for SS and PTP
    def make_dict_for_ss_trap(self,**kwargs):
	event_trap_dict = {}
	global ss_mapping_dict
	down_device_dict = kwargs['down_device_dict']
	ss_list = kwargs['ss_list']
	bs_list = kwargs['bs_list']
	bs_ss_dict = kwargs['bs_ss_dict']
	attr_list = ptp_or_ss_trap_vars
	down_device_static_dict = kwargs['static_dict']
	mat_entries = kwargs['mat_entries']

	alarm_specific_attr = ['alrm_desc','alrm_name','time_stamp','severity','alrm_id','resource_name','device_ip']
	mat_related_field = ['alrm_grp','corr_req','tckt_req','is_sia','alrm_category']
	for key,value in down_device_dict.iteritems():
	    if key in ss_list :
		event_trap_dict[key] ={} 
		tech = down_device_static_dict[key].get(ss_mapping_dict['tech'],'')
		for attr in attr_list:
		    if attr in alarm_specific_attr:
			if attr == 'severity':
			    attr_value = ALARM_FLAGS.get(value.get(ss_mapping_dict[attr],''),1)
			else:	
			    attr_value = value.get(ss_mapping_dict[attr],'')
		    elif attr in mat_related_field:
			attr_value = mat_entries.get(ss_mapping_dict[attr],'')
		    else:
			attr_value = down_device_static_dict[key].get(ss_mapping_dict[attr],'')

		    if attr == 'device_ip' and tech.lower() == 'p2p' and \
			    down_device_static_dict[key].get('ptp_bh_type') == 'ne':
			attr_value =  ",".join([down_device_static_dict[key].get('ptp_ip',''),value.get('ip_address')])
		    elif attr == 'device_ip' and tech.lower() == 'p2p' and \
			    down_device_static_dict[key].get('ptp_bh_type') == 'fe':

			attr_value =  value.get('ip_address')
			    
		    
		    event_trap_dict[key][attr] = attr_value
	return event_trap_dict

    # Creating Trap dictionary for converter and swich.
    def make_dict_for_conv_swich_trap(self,**kwargs):
	"""
	Making dict
	"""
	event_trap_dict = {}
	down_device_dict = kwargs['down_device_dict']

	down_device_static_dict = kwargs['static_dict']
	rc_element = kwargs.get('rc_element')
	mat_entries = kwargs['mat_entries']
	is_backhaul = kwargs.get('is_backhaul')
	alarm_id = kwargs.get('alarm_id')
	attr_list = converter_or_ptpbh_trap_vars
	if is_backhaul:
	    backhaul_id = kwargs.get('backhaul_id')
	    key = backhaul_id
	    siteb_switch_conv_id = kwargs['siteb_switch_conv_id']
	    static_data = down_device_static_dict[siteb_switch_conv_id]
	else:
	    #logger.error("key as rc_element {0}".format(rc_element))
	    key = rc_element
	    static_data = down_device_static_dict[key]
	alarm_specific_attr = ['alrm_id','alrm_desc','alrm_name','time_stamp','severity','resource_name','additional_f_4']
	mat_related_field = ['alrm_grp','corr_req','tckt_req','is_sia','alrm_category','ior']
	event_trap_dict[key] ={}
	 
	for attr in attr_list:
	    if attr in alarm_specific_attr:
		event_trap_dict[key][attr] = down_device_dict[key].get(conv_switch_mapping_dict[attr],'')
		if attr == 'severity':
		    event_trap_dict[key][attr] = ALARM_FLAGS.get(down_device_dict[key].get(conv_switch_mapping_dict[attr],''),1)
	    elif attr in mat_related_field:
		attr_value =  mat_entries.get(conv_switch_mapping_dict[attr],'')
		event_trap_dict[key][attr] = attr_value
	    elif attr == 'parent_alrm_id':
		event_trap_dict[key][attr] = alarm_id
	    else:
		event_trap_dict[key][attr] = static_data.get(conv_switch_mapping_dict[attr],'')
	alarm_id = event_trap_dict[key]['alrm_id']
	return event_trap_dict,alarm_id

    # Creating Trap dict for idu and odu
    def make_dict_for_idu_odu_trap(self,**kwargs):
	event_trap_dict = {}
	global bs_mapping_dict
	down_device_dict = kwargs['down_device_dict']
	down_device_static_dict = kwargs['static_dict']
	alarm_id = kwargs.get('alarm_id')
	bs_list = kwargs['bs_list']
	mat_entries = kwargs['mat_entries']
	attr_list = idu_or_odu_trap_vars
	idu_odu_alarm_id ={} 
	alarm_specific_attr = ['alrm_desc','alrm_name','time_stamp','severity','alrm_id','resource_name','additional_f_4','device_ip']
	mat_related_field = ['alrm_grp','corr_req','tckt_req','is_sia','alrm_category']
	for key,value in down_device_dict.iteritems():
	    if key in bs_list:
		event_trap_dict[key] ={} 
		#idu_odu_alarm_id[value.get('ip_address')] = value.get('unique_id')	
		for attr in attr_list:
		    if attr in alarm_specific_attr:
			if attr == 'severity':
			    attr_value = ALARM_FLAGS.get(value.get(bs_mapping_dict[attr],''),1)
			else:	
			    attr_value = value.get(bs_mapping_dict[attr],'')
		    elif attr in mat_related_field:
			attr_value = mat_entries.get(bs_mapping_dict[attr],'')
		    else:
			attr_value = down_device_static_dict[key].get(bs_mapping_dict[attr],'')
			if attr == 'impacted_sector_count':
			    attr_value = len(down_device_static_dict[key].get(bs_mapping_dict['sector_ids'],[]))
			if attr == 'sector_ids' and attr_value:
			    attr_value = ",".join(list(attr_value))
			elif attr == 'parent_alrm_id':
			    attr_value = alarm_id
		    event_trap_dict[key][attr] = attr_value
	return event_trap_dict
   
    # Fucntion return idu&odu for siteA and siteB and circuit list for inventory hierarchy.
    def get_idu_odu_ckt(self,inventory_hierarchy,redis_conn):
	"""This function return idu_odu_list and circuit dict for Inventory hierarchy.
	    return siteA_idu_odu_list : list of idu_odu id's for siteA.
		   siteB_idu_odu_list : list of idu_odu id's for siteB.
		   ckt_dict : key value pair of dynamic_id as a key and circuit id as value.
	    siteB_idu_odu_list will be empty in case on non PTP_BH scenario."""
	siteA_idu_odu = list()
	siteB_idu_odu = list()
	ptp_bh_flag = 0	
	ckt_dict = defaultdict(list)
	inv_h_keys = inventory_hierarchy.keys()
	special_keys = ['change_bit','ip_list','timestamp','id']
	inv_h_keys = filter(lambda x: x not in special_keys,inv_h_keys)
	for ip_address in inv_h_keys:
	    dynamic_id = inventory_hierarchy[ip_address]
	    key = 'static_' + ip_address
	    static_data = redis_conn.get(key)
	    if static_data:
		static_data = eval(static_data)
		parent_ip = static_data.get('parent_ip')
		rs_type = static_data.get('resource_type')
		if rs_type and (rs_type.lower() == 'idu' or rs_type.lower() == 'odu'):  
		    if static_data.get('ptp_bh_flag'):
			siteB_idu_odu.append(dynamic_id)
		    else:
			siteA_idu_odu.append(dynamic_id)
		if rs_type and rs_type.lower() == 'ss':
		    ss_parent_ip = static_data.get('parent_ip')
		    if static_data.get('ptp_bh_flag'):
			ptp_bh_flag = 1 
		    if ss_parent_ip:
			ss_parent_id = inventory_hirarchy.get(ss_parent_ip)
			ckt_dict[ss_parent_id].append(static_data['circuit_id'])
	return siteA_idu_odu,siteB_idu_odu,ckt_dict,ptp_bh_flag
   
    # Function returns switch/converter information connected to PTP-BH. 
    def get_siteB_switch_conv(self,backhaul_ended_switch_con_ip):
	redis_conn = self.redis_conn()
	switch_conv_id,static_dict,dynamic_dict = None,None,None
	if backhaul_ended_switch_con_ip:
	    static_dict = redis_conn.get('static_' + backhaul_ended_switch_con_ip)
	    static_dict = eval(static_dict)
	    inventory_tree = redis_conn.get(static_dict.get('inventory_id'))
	    inventory_tree = eval(inventory_tree)
	    #logger.error("inventory tree {0}".format(inventory_tree))
	    dynamic_id = inventory_tree.get(backhaul_ended_switch_con_ip)
	    dynamic_dict = redis_conn.get(dynamic_id)
	    dynamic_dict = eval(dynamic_dict)
	    if inventory_tree:
		switch_conv_id = inventory_tree.get(backhaul_ended_switch_con_ip)
	return switch_conv_id,static_dict

    def max_value(self,inventory_hierarchy, down_device_id_list, down_device_dict, static_dict):
	"Calculate root cause element of the down devices and send idu/odu and circuit of connected ss for sending traps"
	elements_ip_list = []
	element_dict = defaultdict(list)
	rc_element = None
	bs_list = []
	ss_list = []
	bs_ss_dict = {}
	priority = {
		    'popconverter':5,
		    'btsconverter':4,
		    'bsswitch':3,
		    'bs':2,
		    'ss':1,
	}
	rc_ip_data = defaultdict(list)
	global_max = 0
	ptp_bh_flag = 0
	is_backhaul = 0
	backhaul_id = None
	backhaul_ended_switch_con_ip =None
	ckt_dict = defaultdict(list)
	del_ss = []
	for key,value in down_device_dict.iteritems():
	    device_static_data = static_dict.get(key)
	    ip_address = value.get('ip_address')
	    resource_name = device_static_data['resource_name'].lower()
	    pvalue = priority.get(resource_name)
	    if device_static_data.get('ptp_bh_flag') == 1:
		ptp_bh_flag = 1 
	    if pvalue == 1:
		# if condition to check is_backhaul is already assigned value or not.
		backhaul = device_static_data.get('backhaul')
		bs_ip = device_static_data.get('parent_ip')
		bs_id = inventory_hierarchy.get(bs_ip)
		ptp_bh_type = device_static_data.get('ptp_bh_type')

		if ptp_bh_type == 'fe' or ptp_bh_type == 'ne':
		    if backhaul and ptp_bh_type == 'ne':
			backhaul_id = key
			backhaul_ended_switch_con_ip = device_static_data.get('child_switch')
			if not is_backhaul:
			    is_backhaul = 1
		    elif backhaul and ptp_bh_type == 'fe':
			if bs_id and bs_id in down_device_dict.keys():
			    del_ss.append(key)
			else:
			    backhaul_id = key
			    backhaul_ended_switch_con_ip = device_static_data.get('child_switch')
			if not is_backhaul:
			    is_backhaul = 1
		    elif ptp_bh_type == 'ne':
			if device_static_data.get('circuit_id'):
			    ckt_dict[key].append(device_static_data.get('circuit_id'))
		    elif ptp_bh_type == 'fe':
			if bs_id and bs_id in down_device_dict.keys():
			    del_ss.append(key)
			    continue
			else:
			    if device_static_data.get('circuit_id'):
				ckt_dict[key].append(device_static_data.get('circuit_id'))
		else:
		    if bs_id and bs_id in down_device_dict.keys():
			bs_ss_dict[bs_id] = key
			del_ss.append(key)
			if device_static_data.get('circuit_id'):
			    ckt_dict[bs_id].append(device_static_data.get('circuit_id'))
			continue
		
	    if global_max < pvalue:
		global_max = priority[resource_name]
		rc_element_ip = ip_address
		global_max_id = key
	    rc_ip_data[pvalue].append(ip_address)
	    element_dict[pvalue].append(key)

	conv_switch_list = []
	if global_max > 2:
	    if ptp_bh_flag:
		conv_switch_list.extend(element_dict.get(index) for index in range(5,2,-1) if element_dict.get(index)) 
		conv_switch_list = list(itertools.chain(*conv_switch_list))
		rc_element =[ih_id for ih_id in conv_switch_list if not static_dict.get(ih_id).get('ptp_bh_flag')]
		if rc_element:
		    rc_element = rc_element[0]
		else:
		    rc_element = conv_switch_list[0]
	    else:
		rc_element = element_dict[global_max][0] 
	    bs_list =  element_dict[2]
	    ss_list =  element_dict[1]
	elif global_max == 2:
	    bs_list =  element_dict[2]
	    ss_list =  element_dict[1]
	else:
	    ss_list =  element_dict[1]
	flags = {}
	flags['backhaul_id'] = backhaul_id
	flags['is_backhaul'] = is_backhaul
	flags['ptp_bh_flag'] = ptp_bh_flag
	flags['backhaul_ended_switch_con_ip']= backhaul_ended_switch_con_ip
	flags['bs_ss_dict']= bs_ss_dict

	return (rc_element,bs_list,ss_list,ckt_dict,flags),del_ss

@app.task(base=DatabaseTask, name='collect_down_events_from_redis')
def collect_down_events_from_redis(event_list):
    """ TODO: implement code to take values from redis"""
    print '....In collect_down_events_from_redis.....................'
    print event_list
    cor_obj=correlation()
    redis_cnx = cor_obj.redis_conn()
    cor_obj.update_redis_inventory_hiearachy(redis_cnx,event_list)

@app.task(base=DatabaseTask, name='correlation_down_event')
def correlation_down_event():
    inventory_list = list()
    cor_obj = correlation() 
    # redis Connection
    rds_cli = RedisInterface(custom_conf={'db': 5})
    redis_conn =  rds_cli.redis_cnx
    p=redis_conn.pipeline()
   
    # Calculate entries for Down event in MAT tables Event: Device_not_rechable
    key = 'rf_ip_Device_not_reachable_critical'
    mat_entries = redis_conn.get(key)
    if mat_entries:
        mat_entries = eval(mat_entries)

    # Extract Inventory of all devices present in Redis
    current_time = datetime.now().strftime('%s')
    [p.get(k) for k  in range(5000)]
    invent_obj=p.execute()
 
    # Extract those inventory on which any alarm has been updated for devices under them and their alarm is in range of 2 
    # polling cycle
    invent_obj = [eval(entry) for entry in invent_obj if entry is not None]
    invent_obj = filter(lambda x: x['change_bit'] == 1 ,invent_obj)
    #logger.error('Before timestamp {0}'.format(invent_obj)) 
    invent_obj_list = filter(lambda x:int(current_time) - int(x['timestamp']) > 300 and 
		 int(current_time) - int(x['timestamp']) <= 600 and x.get('ip_list') , invent_obj)
    #logger.error('after timestamp {0}'.format(invent_obj_list)) 


    invent_id_list = [inventory_hierarchy.get('id') for inventory_hierarchy in invent_obj_list]
    down_device_list = [inventory_hierarchy.get('ip_list') for inventory_hierarchy in invent_obj_list
	 	  if inventory_hierarchy.get('ip_list')]
    #down_device = [down_device_id for down_id_list in down_device_list for down_device_id in down_id_list ] 
    down_device = list(itertools.chain(*down_device_list))

    #logger.error('Down device data {0}'.format(down_device))

    [p.get(dynamic_id) for dynamic_id in down_device]
    down_device_data = p.execute()
    # key-value pair for storing device redis key and their alarm data
    down_device_dict = dict([ (dynamic_id,eval(alarm_data)) for dynamic_id,alarm_data in zip(down_device,down_device_data)])
    
    #Caluculate Static data for all down devices
    down_device_ips = map(lambda x: x.get('ip_address'),down_device_dict.values()) 
    [p.get('static_' + str(ip)) for ip in down_device_ips]
    static_info = p.execute()
    # key-value pair for storing device redis key and their staitc data
    #logger.error("inventory tree {0} values {1}".format(down_device_dict.keys(),len(static_info)))
    static_dict = dict([ (dynamic_id,eval(static_entry)) for dynamic_id, static_entry in zip(down_device_dict.keys(), static_info)])

    trap_list = []
    redis_keys = []
    redis_keys.extend(down_device_dict.keys()) 
    for inventory_hierarchy in invent_obj_list:
	index = invent_obj_list.index(inventory_hierarchy)
	down_device = list(down_device_list[index])
	invent_down_device_dict= dict([(id,down_device_dict[id]) for id in down_device])
        mv_params,del_ss= cor_obj.max_value(inventory_hierarchy, down_device, invent_down_device_dict, static_dict)
	#logger.error("inventory tree {0}".format(mv_params))
	trap_list.append(mv_params)
	if del_ss:
	    for del_ss_key in del_ss:
		del down_device_dict[del_ss_key]

    params = trap_list,down_device_dict,static_dict,mat_entries,invent_id_list,redis_keys
    #send_traps.s(trap_list, down_device_dict, static_dict, mat_entries, invent_id_list,redis_keys).apply_async()
    send_traps.s(params).apply_async()

@app.task(base=DatabaseTask, name='delete_redis_key')
def delete_redis_key(element_keys,invent_id_list):
    """
    Deleting redis key from ip_list key in inventory dictionary for that tree
    Deleting the Redis alarm entry from the redis key for sent trap idu/odu/con/switch/ss
    """
    rds_cli = RedisInterface(custom_conf={'db': 5})
    redis_conn =  rds_cli.redis_cnx
    p=redis_conn.pipeline()
    [p.get(id) for id in invent_id_list]
    invent_list = p.execute()
    [p.get(id) for id in element_keys]
    element_list = p.execute()
    final_invent_list = []
    final_element_list = []
    mod_invent_dict = {}
    mod_element_dict = {}
    for invent_dict in invent_list:
	invent_dict = eval(invent_dict)
        if invent_dict.get('ip_list'):
	    id_list =  deepcopy(invent_dict.get('ip_list'))
	    [ invent_dict.get('ip_list').remove(id) for id in id_list if id in element_keys]
	    if not invent_dict.get('ip_list'):
	    	invent_dict['change_bit'] = 0
	    	invent_dict['timestamp'] = ''
	    mod_invent_dict[invent_dict['id']] = invent_dict 
    	    final_invent_list.append(mod_invent_dict) 
    for element_id,element_dict in zip(element_keys,element_list):
	element_dict = eval(element_dict)
	id = element_dict.get('inventory_id')
	element_dict ={}
	element_dict['inventory_id']  = id 
	mod_element_dict[element_id] = element_dict 
    	final_element_list.append(mod_element_dict)
    cor_obj = correlation() 
    cor_obj.insert_events_into_redis(final_invent_list,is_list=1)
    cor_obj.insert_events_into_redis(final_element_list,is_list=1)

@app.task(base=DatabaseTask, name='send_traps')
def send_traps(params):
    trap_list,down_device_dict,down_device_static_dict,mat_entries,invent_id_list,redis_keys = params
    cor_obj = correlation()
    final_trap_list = []
    device_params = {
           'down_device_dict': down_device_dict,
           'static_dict' :down_device_static_dict,
           'mat_entries': mat_entries
    }
    for trap_params in trap_list:
	params = {}
	params.update(device_params)
        rc_element,bs_down_list,ss_down_list,ckt_dict,flags = trap_params
        #logger.error("\nFlags \t{0}".format(flags))
        ptp_bh_flag = flags['ptp_bh_flag']
	bs_ss_dict = flags['bs_ss_dict']
	is_backhaul =flags['is_backhaul']
	backhaul_id =flags['backhaul_id']
	backhaul_ended_switch_con_ip = flags['backhaul_ended_switch_con_ip']
        params.update({'backhaul_id':backhaul_id ,
		       'backhaul_ended_switch_con_ip': backhaul_ended_switch_con_ip, 
		      'is_backhaul': is_backhaul ,
		      'ptp_bh_flag' : ptp_bh_flag
	})

        trap_dict = {}
        idu_odu_trap_dict = {}
        idu_odu_alarm_id_dict = {}
        mat_entries = {}
        rc_element_dict=None
        alarm_id = None
        #logger.error("Before sending for conv ckt {0} {1}".format(down_device_static_dict,down_device_dict))
	sitea_ptp_down_list = [ptp_down_device for ptp_down_device in ss_down_list
				if down_device_static_dict[ptp_down_device].get('resource_type') == 'PTP'
				and not down_device_static_dict[ptp_down_device].get('ptp_bh_flag')]

	siteb_ptp_down_list = [ptp_down_device for ptp_down_device in ss_down_list
				if down_device_static_dict[ptp_down_device].get('resource_type') == 'PTP'
				and down_device_static_dict[ptp_down_device].get('ptp_bh_flag')
				and not down_device_static_dict[ptp_down_device].get('backhaul')]
	if ptp_bh_flag:
        	siteb_bs_down_list = [bs_down_device for bs_down_device in bs_down_list  
					if down_device_static_dict[bs_down_device].get('ptp_bh_flag') ]
        	siteb_ss_down_list = [ss_down_device for ss_down_device in ss_down_list 
					if down_device_static_dict[ss_down_device].get('ptp_bh_flag') ]
		sitea_bs_down_list = list(set(bs_down_list) - set(siteb_bs_down_list))
		sitea_ss_down_list = list(set(ss_down_list) - set(siteb_ss_down_list))
		

        if rc_element:
	    params.update( {
                   	'rc_element':rc_element,
            })
	    if ptp_bh_flag and down_device_static_dict[rc_element].get('ptp_bh_flag'):
		#Make traps for site B affected Switch/coverter

		if backhaul_id:
		    params.update({'siteb_switch_conv_id': rc_element})
		    down_device_static_dict[rc_element]['parent_ip'] = down_device_static_dict[backhaul_id].get('parent_ip')
		    if down_device_static_dict[backhaul_id]['ptp_bh_type'] == 'fe':
			down_device_static_dict[rc_element]['pop_ip'] = ''
                rc_element_dict, alarm_id = cor_obj.make_dict_for_conv_swich_trap(**params)

    	        params.update({
    	    		     'bs_list':bs_down_list,
	   		     'alarm_id': None
		})
		# Make down IDU/ODU traps for the affected siteB switch/converter 
          	bs_trap  = cor_obj.make_dict_for_idu_odu_trap(**params)
		
		# Temporary trap dict for site B ptp
		ss_down = siteb_ptp_down_list + sitea_ss_down_list
		params.update({'ss_list':ss_down,
			     'bs_list': bs_down_list,
			     'bs_ss_dict':bs_ss_dict
		})
                # first store siteb ptp list and then Delete siteb_ptp_dict from ss_trap  
		ss_trap_dict = cor_obj.make_dict_for_ss_trap(**params)
		siteb_ptp_ss_trap = dict([(key,ss_trap_dict.pop(key,None)) for key in siteb_ptp_down_list if key in ss_trap_dict])
	        	
		# update alarm_id for siteb idu/odu/ptpss
		for id in siteb_bs_down_list:
		    bs_trap[id]['parent_alrm_id'] = alarm_id
		for id in siteb_ptp_down_list:
		    siteb_ptp_ss_trap[id]['parent_alrm_id'] = alarm_id
		input_for_ckt_dict = {}
		input_for_ckt_dict.update(bs_trap)
		input_for_ckt_dict.update(siteb_ptp_ss_trap)

		#siteb ptp ckt dict
		params.update({'alarm_id':alarm_id,
			     'ckt_dict':ckt_dict,
			     'idu_odu_trap_dict': input_for_ckt_dict
		})
		ckt_element_list = cor_obj.make_dict_for_ckt(**params)


		final_trap_list = rc_element_dict.values() + bs_trap.values() + ss_trap_dict.values() + ckt_element_list	
		    
	    else:
		# PTP Backhaul Case where SiteA (switch/coverter) is down.
		params.update( {
                        'rc_element':rc_element,
			'is_backhaul':None
                })
		#Make traps for site A affected Switch/coverter
		rc_element_dict,alarm_id = cor_obj.make_dict_for_conv_swich_trap(**params)
                params.update({'alarm_id':alarm_id})

		#ptp_bh trap Calculate Site B switch Static Dict
		if is_backhaul:
		    params.update({'is_backhaul':is_backhaul})
		    siteb_switch_conv_id, siteb_switch_conv_static_data = cor_obj.get_siteB_switch_conv(backhaul_ended_switch_con_ip)
		    if not down_device_static_dict.get(siteb_switch_conv_id):
			down_device_static_dict[siteb_switch_conv_id] = siteb_switch_conv_static_data

		    # In case of ptp_bh if down device is far-end then pop_ip should be null 
		    # for both near end and far end down devices bts conv and pop conv has to be there.

                    if down_device_static_dict[backhaul_id].get('ptp_bh_type') == 'fe':
			down_device_static_dict[siteb_switch_conv_id]['pop_ip'] = ''

		    # Changing conv switch/conv parent ip to parent ip of down ptp bh device.
		    down_device_static_dict[siteb_switch_conv_id]['parent_ip'] = down_device_static_dict[backhaul_id].get('parent_ip')

		    params.update({'siteb_switch_conv_id': siteb_switch_conv_id})

		    # Make trap for PTP BH Site B(near end bs----- far end ss)
		    siteb_switch_conv_dict,siteb_alarm_id= cor_obj.make_dict_for_conv_swich_trap(**params)
		    if siteb_switch_conv_dict:
	            	final_trap_list.extend(siteb_switch_conv_dict.values())		


                params.update({'bs_list':bs_down_list})
                idu_odu_trap_dict = cor_obj.make_dict_for_idu_odu_trap(**params)

		# Temporary trap dict for ptp ss down devices
		total_ptp_ss_down = siteb_ptp_down_list + sitea_ptp_down_list
		params.update({'ss_list':total_ptp_ss_down,
			      'bs_list': [] ,
			      'bs_ss_dict':bs_ss_dict
		})
		ptp_dict = cor_obj.make_dict_for_ss_trap(**params)
		
		for id,value in ptp_dict.iteritems():
		    ptp_dict[id]['parent_alrm_id'] = alarm_id

		#ptp ckt dict
	        input_for_ckt_dict = {}
		input_for_ckt_dict.update(idu_odu_trap_dict)  
		input_for_ckt_dict.update(ptp_dict) 
 
		params.update({'ckt_dict':ckt_dict,'idu_odu_trap_dict': input_for_ckt_dict})
		ckt_element_list = cor_obj.make_dict_for_ckt(**params)


		final_trap_list = final_trap_list + rc_element_dict.values() + idu_odu_trap_dict.values() + ckt_element_list

				
        elif bs_down_list:
	    if ptp_bh_flag and is_backhaul:
		siteb_switch_conv_id,siteb_switch_conv_static_data = cor_obj.get_siteB_switch_conv(backhaul_ended_switch_con_ip)
		if not down_device_static_dict.get(siteb_switch_conv_id):
		    down_device_static_dict[siteb_switch_conv_id] = siteb_switch_conv_static_data
		down_device_static_dict[siteb_switch_conv_id]['parent_ip'] = down_device_static_dict[backhaul_id].get('parent_ip')
		if down_device_static_dict[backhaul_id]['ptp_bh_type'] == 'fe':
		    down_device_static_dict[siteb_switch_conv_id]['pop_ip'] = ''
		params.update({
			      'siteb_switch_conv_id': siteb_switch_conv_id ,
			      'alarm_id':None
			      })
	
		# send traps for the ptp backhaul devices if down	
                rc_element_dict,alarm_id= cor_obj.make_dict_for_conv_swich_trap(**params)

		
		total_idu_odu_down = siteb_bs_down_list + sitea_bs_down_list

		params.update({'bs_list': total_idu_odu_down,'alarm_id':None})

                bs_trap = cor_obj.make_dict_for_idu_odu_trap(**params)
		total_ss_down = siteb_ptp_down_list + sitea_ss_down_list
 	
		params.update({'ss_list':total_ss_down,
			     'bs_list':[],
			     'bs_ss_dict':bs_ss_dict
		})
		ss_trap_dict = cor_obj.make_dict_for_ss_trap(**params)
		
		siteb_ptp_ss_trap = dict([(key,ss_trap_dict.pop(key,None)) for key in siteb_ptp_down_list if key in ss_trap_dict])
	        	
		# update alarm_id for siteb idu/odu/ptpss
		for id in siteb_bs_down_list:
		    bs_trap[id]['parent_alrm_id'] = alarm_id
		
		for id in siteb_ptp_down_list:
		    siteb_ptp_ss_trap[id]['parent_alrm_id'] = alarm_id

		input_for_ckt_dict = {}
		input_for_ckt_dict.update(bs_trap)
		input_for_ckt_dict.update(siteb_ptp_ss_trap)


		#siteb ptp ckt dict
		params.update({'ckt_dict':ckt_dict,'idu_odu_trap_dict': input_for_ckt_dict})
		ckt_element_list = cor_obj.make_dict_for_ckt(**params)


		final_trap_list = final_trap_list + bs_trap.values() + ss_trap_dict.values() + ckt_element_list + \
					rc_element_dict.values()

            else:
    	    	params.update({'bs_list':bs_down_list,'alarm_id':None})
            	idu_odu_trap_dict = cor_obj.make_dict_for_idu_odu_trap(**params)

	    	params.update({'idu_odu_trap_dict':idu_odu_trap_dict,
    	    		     'ss_list':ss_down_list,
			     'bs_ss_dict':bs_ss_dict
		})

	   	ss_trap_dict = cor_obj.make_dict_for_ss_trap(**params)
	    	params.update({'ckt_dict':ckt_dict,'idu_odu_trap_dict':idu_odu_trap_dict,'alarm_id':None})

	    	ckt_element_list = cor_obj.make_dict_for_ckt(**params)

		final_trap_list = final_trap_list + ss_trap_dict.values() + idu_odu_trap_dict.values() + ckt_element_list

        elif ss_down_list:
	    if ptp_bh_flag and is_backhaul:
		siteb_switch_conv_id, siteb_switch_conv_static_data = cor_obj.get_siteB_switch_conv(backhaul_ended_switch_con_ip)
		if not down_device_static_dict.get(siteb_switch_conv_id):
		    down_device_static_dict[siteb_switch_conv_id] = siteb_switch_conv_static_data
		if down_device_static_dict[backhaul_id]['ptp_bh_type'] == 'fe':
		    down_device_static_dict[siteb_switch_conv_id]['pop_ip'] = ''
		params.update({
			      'siteb_switch_conv_id': siteb_switch_conv_id 
		})
                rc_element_dict,alarm_id= cor_obj.make_dict_for_conv_swich_trap(**params)

		total_ss_down = siteb_ptp_down_list + sitea_ss_down_list
 	
		params.update({'ss_list':total_ss_down,
			      'bs_list':[],
			      'bs_ss_dict':bs_ss_dict
		})
		ss_trap_dict = cor_obj.make_dict_for_ss_trap(**params)
		
		siteb_ptp_ss_trap = dict([(key,ss_trap_dict.pop(key,None)) for key in siteb_ptp_down_list if key in ss_trap_dict])
	        	
		# update alarm_id for siteb idu/odu/ptpss
		for id in siteb_ptp_down_list:
		    siteb_ptp_ss_trap[id]['parent_alrm_id'] = alarm_id

		input_for_ckt_dict = siteb_ptp_ss_trap

		#siteb ptp ckt dict
		params.update({'ckt_dict':ckt_dict,'idu_odu_trap_dict': input_for_ckt_dict})
		ckt_element_list = cor_obj.make_dict_for_ckt(**params)


		final_trap_list = final_trap_list + s_trap_dict.values() + ckt_element_list + rc_element_dict.values()

	    else:
    	        params.update({'ss_list':ss_down_list,
    	        	      'bs_list':[],
			      'bs_ss_dict':bs_ss_dict
		})
	        ss_trap_dict = cor_obj.make_dict_for_ss_trap(**params)
	        final_trap_list.extend(ss_trap_dict.values())		
 
    #logger.error("Keys to be deleted {0} {1}\n".format(redis_keys,invent_id_list))
    #logger.error("final trap list id {0}\n".format(final_trap_list))

    """
    trap_sender_task.s(final_trap_list).apply_async()
    
    non_ckt_trap_dict = {}
    [ non_ckt_trap_dict.update(trap_dict) for trap_dict in [ss_trap_dict,idu_odu_trap_dict,rc_element_dict] if trap_dict]
    cor_obj=correlation()
    redis_conn = cor_obj.redis_conn()
    p = redis_conn.pipeline()
    [p.set('trap_'+str(trap_dict['alrm_name']+str('_')+str(ip)),trap_dict) for ip,trap_dict in non_ckt_trap_dict.iteritems()]
    p.execute()

    """
    # Update Redis keys to delete affected element as traps has been sent
    delete_redis_key.s(redis_keys,invent_id_list).apply_async()
     


#@app.task(base=DatabaseTask, name='trap_sender_task')
def trap_sender_task(traps):
   for trap in traps:
	t = Trap(**trap)
	t.send_trap() 

 




