from start.start import app
from handlers.db_ops import RedisInterface,DatabaseTask 
from trap_handler.db_conn import ExportTraps,ConnectionBase
from uuid import uuid4
from datetime import datetime
from collections import defaultdict
from copy import deepcopy
import itertools
from trap_sender import Trap
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error
from os import system
from time import sleep

def generateuuid():
	return str(uuid4())
# Sprint2 requirement RF-IP correlation
# Ignore events for Swtich.
# IF
#   BTSConverter/POPConverter is down, Do not generate any trap
# ELSE 
#   Generate traps for Idu/Odu , ss ptp trap and circuit trap.

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
	'alrm_desc': 'alarm_description','alrm_name':'alias','time_stamp':'timestamp',
        'severity':'severity','tech':'technology','resource_name':'ip_address','pop_converter_ip':'pop_ip',
	'parent_ip':'parent_ip','parent_type':'parent_type','parent_port':'parent_port','bs_switch_ip':'bs_switch_ip',
	'aggr_switch_ip':'aggr_switch','pe_ip':'pe_ip','bs_name':'bs_name','region':'region','resource_type':'resource_type',	
	'coverage':'coverage','additional_f_1':'additional_f_1','additional_f_2':'additional_f_2',
	'additional_f_3':'additional_f_3','categorization_tier_1':'categorization_tier_1','bs_converter_ip':'bts_conv_ip',
	'categorization_tier_2':'categorization_tier_2','alrm_id':'unique_id','alrm_grp':'alarm_group',
	'corr_req':'correlation','tckt_req':'auto_tt','is_sia':'sia','alrm_category':'alarm_group',
	'IOR':'ior','parent_alrm_id':'parent_alarm_id','additional_f_4':'resource_type'	
}
bs_mapping_dict = {'alrm_desc': 'alarm_description',
	'alrm_name':'alias','time_stamp':'timestamp',
    	'severity':'severity','tech':'technology','resource_name':'ip_address',
    	'parent_ip':'parent_ip','parent_type':'parent_type','parent_port':'parent_port',
	'bs_name':'bs_name','region':'region','resource_type':'resource_type','sector_ids':'sector_id',
    	'coverage':'coverage','additional_f_1':'additional_f_1','additional_f_2':'additional_f_2',
    	'additional_f_3':'city','categorization_tier_1':'categorization_tier_1',
	'impacted_sector_count':'impacted_sector_count','device_ip':'ip_address',
	'categorization_tier_2':'categorization_tier_2','alrm_id':'unique_id','alrm_grp':'alarm_group',
	'corr_req':'correlation','tckt_req':'auto_tt','is_sia':'sia','alrm_category':'alarm_group',
    	'parent_alrm_id':'parent_alarm_id','additional_f_4':'additional_f_4','additional_f_5':'additional_f_5',
	'additional_f_6':'aggr_switch','additional_f_7':'pe_ip','additional_f_8':'additional_f_8'	
}

ss_mapping_dict = {'alrm_desc': 'alarm_description',
	'alrm_name':'alias','time_stamp':'timestamp',
    	'severity':'severity','tech':'technology','resource_name':'ip_address',
    	'parent_ip':'parent_ip','parent_type':'parent_type','parent_port':'parent_port',
	'region':'region','resource_type':'resource_type',
    	'device_ip':'ip_address','additional_f_1':'additional_f_1','additional_f_2':'additional_f_2',
    	'additional_f_3':'city','customer_name':'customer_name',
	'impacted_circuit_id':'circuit_id','alrm_id':'unique_id','alrm_grp':'alarm_group',
	'corr_req':'correlation','tckt_req':'auto_tt','is_sia':'sia','alrm_category':'alarm_group',
	'additional_f_4':'additional_f_4','additional_f_5':'additional_f_5','child':'child',
	'additional_f_6':'bs_name'
}

ALARM_FLAGS = {
	      'critical': 3,
	      'clear':1,
	      '0': 'no'
}

# Python Singleton pattern used to Stop creation of unnecessary class instance.
class Singleton(type):
    _instance = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(Singleton,cls).__call__(*args,**kwargs)
	    rds_cli = RedisInterface(custom_conf={'db': 5})
	    redis_conn =  rds_cli.redis_cnx
	    try:
		mat_flag = redis_conn.exists('mat_data')
		# Run script mysql_test if Master Alarm Table not available in database.
		# Sleep programm  for 10 second meanwhile data will be restored.
		if not mat_flag:
		    logger.error('mat_data not available in redis')
		    system('python /apps/nocout_etl/raw_mysql_data.py')
		    sleep(10)
	        mat_data = redis_conn.get('mat_data')
	        cls._instance[cls].mat_data = eval(mat_data)


		alarm_priority_dict = redis_conn.get('alarm_priority_dict')
		cls._instance[cls].alarm_priority_dict = eval(alarm_priority_dict)
		alarm_mapping_dict = redis_conn.get('alarm_mapping_dict')
		cls._instance[cls].alarm_mapping_dict = eval(alarm_mapping_dict)
	    except Exception as e:
		logger.error("Exception: Redis database does not have sufficeint information for correlation process \
			      \nExecute command: python nocout/performance/service/mysql_test_ca.py")
	        cls._instance[cls].mat_data = {} 
		cls._instance[cls].alarm_priority_dict = {}
		cls._instance[cls].alarm_mapping_dict = {}
        return cls._instance[cls]

class correlation:
    __metaclass__ = Singleton
    def __init__(self):
	pass
    def redis_conn(self):
	"""Connection to redis database."""
        rds_cli = RedisInterface(custom_conf={'db': 5})
        redis_conn =  rds_cli.redis_cnx
    	return redis_conn 
 
    def update_redis_inventory_hierarchy(self,redis_conn):
	"""
	Get the data(traps/events) from redis.
	Filter it based on inventory id and store it accordingly.
	Craete a tuple (alarm_name,severity) from alarm data and store/update in alarm inventory, tuple as a key and value alarm data.
	
	Structure:
	invent_dict:{invent_id1:{'timestamp':342234323,
				'ip_address1':{
						(alarm_name,severity):alarm_data,
						(alarm_name,severity):alarm_data},
				'ip_address2':{
						(alarm_name,severity):alarm_data,
						(alarm_name,severity):alarm_data},
				}
		     invent_id2:{'timestamp':234242411, 
				'ip_address3':{
						(alarm_name,severity):alarm_data,
						(alarm_name,severity):alarm_data},
				'ip_address5':{
						(alarm_name,severity):alarm_data,
						(alarm_name,severity):alarm_data},
				}
		}

	'queue:traps' = [[alarm_data1],[alarm_data2],.....,[alamr_datan]]

	Mapping between IP address and inventory id.
	ip_id={ip_address: inventory_id}

	for e.g. ip_id = {'10.175.44.9': 45,
			  '121.89.44.2': 2}
	"""
	ct_keys = []
	redis_conn = self.redis_conn()
	try:	
	    invent_dict = redis_conn.get('invent_dict')
	    invent_dict = eval(invent_dict)
	except Exception as e:
	    invent_dict = {}
	    redis_conn.set('invent_dict',{})
	
	ip_id = redis_conn.get('ip_id')                    # Ip address to Inventory id mapping.
	ip_id = eval(ip_id)
	len = redis_conn.llen('queue:traps')
	p = redis_conn.pipeline()
	[p.lpop('queue:traps') for i in range(len)]        # Alarm data(traps and events) from redis
	trap_event_list = p.execute()
	trap_event_list = [eval(t_e) for t_e in trap_event_list]

	# Store traps to invent_dict according to its structure show above.
	#logger.error('{0}'.format(trap_event_list))
	for trap_event in trap_event_list:
	    try:
		if trap_event[1] == 'Device_not_reachable':
		    ip = trap_event[3]
		    alarm_name = trap_event[1]
		    severity = trap_event[6]
		    key = (alarm_name,severity)
		    id = ip_id.get(ip)
		    if alarm_name == 'Device_not_reachable' and severity == 'clear':
			ct_key = str(ip)+'_'+str(alarm_name)
			ct_keys.append(ct_key)

		    alarm = dict()   
		    alarm['alarm_name'] = trap_event[1]
		    alarm['alarm_description'] = trap_event[2]
		    alarm['timestamp'] = int(datetime.strptime(trap_event[8],"%Y-%m-%d %H:%M:%S").strftime('%s'))
		    alarm['severity'] = trap_event[6]
		    alarm['unique_id'] = generateuuid()
		    alarm['ip_address'] = ip
		    alarm['inventory_id']= id
		    alarm['category'] = self.mat_data.get(key).get('category')
		    #Alarm name alias for monolith
		    alarm['alias'] = ' '.join(trap_event[1].split('_'))
		    if id is not None:
			if id in invent_dict:
			    if ip in invent_dict[id]:
				invent_dict[id][ip][key] = alarm
			    else:
				invent_dict[id][ip] = {}
				invent_dict[id][ip][key] = alarm
			else:
			    timestamp = trap_event[8]
			    invent_dict[id] = {}
			    invent_dict[id]['timestamp'] = alarm['timestamp']
			    invent_dict[id][ip] = {}
			    invent_dict[id][ip][key] = alarm
		    else:
			timestamp = trap_event[8]
			invent_dict[id] = {}
			invent_dict[id]['timestamp'] = alarm['timestamp']
			invent_dict[id][ip] = {}
			invent_dict[id][ip][key] = alarm
	    except Exception as e:
		logger.error('Error creating Alarm information \n Excetion : {0}'.format(e))
	inventory_dict = {'invent_dict':invent_dict}
        self.insert_events_into_redis(inventory_dict)

	# Clear Trap Send Task
	ct_keys = list(set(ct_keys))
	# Call Clear Trap Task if Clear Trap Keys exsist.
	if ct_keys:
	    clear_trap.s(ct_keys).apply_async()
	
	# Task call to Start Correlation Process.
	correlation_down_event.apply_async()

    def insert_events_into_redis(self,event_dict,is_list=None):
	"""Insert Data to Redis Database"""
        p = self.redis_conn().pipeline()
        if is_list:
            [p.set(ih_count_id,event_entry) for event in event_dict for (ih_count_id,event_entry) in event.iteritems() ]
	else:
            [p.set(ih_count_id,event) for (ih_count_id,event) in event_dict.iteritems() ]
        p.execute()

    def final_trap_data_manupulation(self,trap_list):
	final_traps = []

	converter_or_ptpbh_trap_vars = [
	    'parent_type', 'parent_ip','parent_port', 'tech', 'alrm_grp',
	    'aggr_switch_ip', 'pe_ip', 'severity', 'time_stamp',
	    'bs_name', 'corr_req', 'tckt_req', 'is_sia',
	    'categorization_tier_1', 'categorization_tier_2',
	    'alrm_category', 'resource_name', 'resource_type',
	    'additional_f_1', 'additional_f_2',
	    'additional_f_4',

	]
	idu_or_odu_trap_vars = [
		'alrm_id', 'device_ip', 'parent_type', 'parent_ip', 'parent_port',
		'sector_ids', 'tech', 'alrm_grp', 'alrm_name',
		'severity', 'time_stamp', 'bs_name', 
		'corr_req', 'tckt_req', 'is_sia', 'impacted_sector_count',
		'categorization_tier_1', 'categorization_tier_2',
		'alrm_category', 'coverage', 'resource_name', 'resource_type',
		'additional_f_1', 'additional_f_2',
		'additional_f_4', 'additional_f_5', 'additional_f_6', 'additional_f_7',
	]
	ptp_or_ss_trap_vars = [
		'alrm_id', 'device_ip', 'parent_type', 'parent_ip', 
		'parent_port', 'tech', 'alrm_grp', 'alrm_name',
		'impacted_circuit_id', 'severity', 'time_stamp',
		'corr_req', 'tckt_req', 'is_sia', 'resource_name',
		'resource_type', 'alrm_category', 'additional_f_2',
		'additional_f_6'
	]

	circuit_ids_trap_vars = [
		'seq_num', 'parent_alrm_id', 'impacted_circuit_ids',
		'alrm_grp', 'alrm_name', 'severity',
		'last_trap'
	]

	data_types = {
	    'parent_port': 'i', 'severity': 'i', 'corr_req': 'i', 'tckt_req': 'i',
	    'is_sia': 'i', 'impacted_sector_count': 'i', 'last_trap':'i',
	    
	    }
	dummy_attr_dict = {
	    		'additional_f_6': '700.700.700.700',
			'additional_f_7': '600.600.600.600',
			'parent_ip': '400.400.400.400',
			'aggr_switch_ip': '700.700.700.700',
			'pe_ip': '600.600.600.600',
			'last_trap':1
			}
	garbage_value = 'abcd'
	garbage_int_value = '1234'
	for trap in trap_list:
	    try:
		tp = trap.get('trap_type')
		if tp == 'converter_or_ptpbh_trap':
		    comulsory_attrs = converter_or_ptpbh_trap_vars
		elif tp == 'idu_or_odu_trap':
		    comulsory_attrs = idu_or_odu_trap_vars
		elif tp == 'ptp_or_ss_trap':
		    comulsory_attrs = ptp_or_ss_trap_vars
		elif tp == 'circuit_ids_trap':
		    comulsory_attrs = circuit_ids_trap_vars

		for attr in comulsory_attrs:
		    dt = data_types.get(attr)
		    if trap[attr] == '' or trap[attr] == 'NA' or trap[attr] == 'None':
			if attr in dummy_attr_dict.keys():
			    trap[attr] = dummy_attr_dict.get(attr)
			elif dt== 'i':
			    trap[attr] = garbage_int_value
			else:
			    trap[attr] = garbage_value
		final_traps.append(trap)
	    except Exception as e:
		logger.error('Error manupulating final trap data \n Exception : {0}'.format(e))
	return final_traps
			
		    
	
    
    def make_dict_for_ckt(self,**kwargs):
	"""Create Trap for Circuit"""
	mapping_list = [
	    'seq_num', 'parent_alrm_id', 'impacted_circuit_ids',
	    'alrm_group', 'alrm_name', 'severity', 'additional_f_1','additional_f_2', 'last_trap'
	]
	#alarm_id = kwargs['alarm_id']
	ckt_dict = kwargs['ckt_dict']
	event_trap_dict = {}
	parent_alrm_id = None 
	final_ckt_list = list()
	try:
	    if kwargs.get('idu_odu_trap_dict'):
		idu_odu_trap_dict = kwargs['idu_odu_trap_dict']
		for key,value in idu_odu_trap_dict.iteritems():
		    if ckt_dict.get(key):
			ckt_list = ",".join([ckt for ckt in ckt_dict.get(key) ])	
		    else:
			continue

		    event_trap_dict['seq_num'] = generateuuid()
		    #  If idu/odu trap dict have parent alarm id that means it have common alarm category with it's parnet device.
		    parent_alrm_id = None
		    if value.get('parent_alrm_id'):
			parent_alrm_id = value.get('parent_alrm_id')
		    else:
			parent_alrm_id = value.get('alrm_id') 

		    event_trap_dict['parent_alrm_id'] = parent_alrm_id 
		    event_trap_dict['impacted_circuit_ids'] = ckt_list
		    event_trap_dict['alrm_name'] = value.get('alrm_name')  
		    event_trap_dict['alrm_grp'] = value.get('alrm_grp')  
		    event_trap_dict['severity'] = value.get('severity')
		    event_trap_dict['additional_f_1'] = ''
		    event_trap_dict['additional_f_2'] = ''
		    event_trap_dict['last_trap'] = ''
		    event_trap_dict['trap_type'] = 'circuit_ids_trap'
		    event_trap_dict['base_trap_oid'] = '.1.3.6.1.4.1.43900.2.2.1.0.3.1'
		    final_ckt_list.append(event_trap_dict)
		    event_trap_dict = {}
	except Exception as e:
	    logger.error('Error Creating Circuit Trap \n Exception : {0}'.format(e))
	return final_ckt_list

    def make_dict_for_ss_trap(self,**kwargs):
        """ Creating Trap dictionary for SS and PTP"""
	event_trap_dict = {}
	global ss_mapping_dict
	down_device_dict = kwargs['down_device_dict']
	ss_list = kwargs['ss_list']
	bs_list = kwargs['bs_list']
	bs_ss_dict = kwargs['bs_ss_dict']
	attr_list = ptp_or_ss_trap_vars
	down_device_static_dict = kwargs['static_dict']

	alarm_specific_attr = ['alrm_desc','alrm_name','time_stamp','severity','alrm_id','resource_name','device_ip']
	mat_related_field = ['alrm_grp','corr_req','tckt_req','is_sia','alrm_category']
	for key,value in down_device_dict.iteritems():
	    try:
		alarm_name= value.get('alarm_name','')
		severity = value.get(ss_mapping_dict['severity'],'') 
		mat_key = (alarm_name,severity)                     # Master Alarm Table key.
		#Check if traps has been set already in previous correlation cycle.
		ip = key
		correlated_trap_key = ip+'_'+alarm_name
		redis_conn = self.redis_conn()
		if redis_conn.hexists('correlated_traps',correlated_trap_key):
		    continue
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
			    attr_value = self.mat_data.get(mat_key).get(ss_mapping_dict[attr],'')
			else:
			    attr_value = down_device_static_dict[key].get(ss_mapping_dict[attr],'')

			if attr == 'device_ip' and tech.lower() == 'p2p' and \
				down_device_static_dict[key].get('ptp_bh_type') == 'ne':
			    attr_value =  ",".join([down_device_static_dict[key].get('ptp_ip',''),value.get('ip_address')])
			elif attr == 'device_ip' and tech.lower() == 'p2p' and \
				down_device_static_dict[key].get('ptp_bh_type') == 'fe':

			    attr_value =  value.get('ip_address')
			event_trap_dict[key][attr] = attr_value
	    
		    event_trap_dict[key]['trap_type'] = 'ptp_or_ss_trap'
		    event_trap_dict[key]['base_trap_oid'] = '.1.3.6.1.4.1.43900.2.2.1.0.2.1'
		    event_trap_dict[key]['additional_f_2'] = 1
		    event_trap_dict[key]['alrm_desc'] = "{0} : {1} : {2} : {3}".format(down_device_static_dict.get(key).get('city'),
										 down_device_static_dict.get(key).get('bs_name'),
										 key,
										 event_trap_dict[key]['alrm_name'])
	    except Exception as e:
		logger.error('Error Creating  Sub Station Trap \n Exception : {0}'.format(e))

	return event_trap_dict

    def make_dict_for_conv_swich_trap(self,**kwargs):
	"""
        Creating Trap dictionary for converter and swich.
	"""
	global conv_switch_mapping_dict
	event_trap_dict = {}
	down_device_dict = kwargs['down_device_dict']

	down_device_static_dict = kwargs['static_dict']
	rc_element = kwargs.get('rc_element')
	is_backhaul = kwargs.get('is_backhaul')
	alarm_id = kwargs.get('alarm_id')
	attr_list = converter_or_ptpbh_trap_vars
	try:
	    # If PTP bh device is faulted, Create trap for ptpbh.
	    if is_backhaul:
		backhaul_id = kwargs.get('backhaul_id')
		key = backhaul_id
		siteb_switch_conv_id = kwargs['siteb_switch_conv_id']
		static_data = down_device_static_dict[siteb_switch_conv_id]
	    # Trap for switch/converter.
	    else:
		key = rc_element
		static_data = down_device_static_dict.get(key)

	    alarm_name= down_device_dict.get(key).get('alarm_name','')
	    severity = down_device_dict.get(key).get(conv_switch_mapping_dict['severity'],'')
	    mat_key = (alarm_name,severity)
     
	    #Check if traps has been set already in previous correlation cycle.
	    ip = key
	    correlated_trap_key = ip+'_'+alarm_name
	    redis_conn = self.redis_conn()
	    if redis_conn.hexists('correlated_traps',correlated_trap_key):
		return None,None

	    alarm_specific_attr = ['alrm_id','alrm_desc','alrm_name','time_stamp','severity','resource_name','additional_f_4']
	    mat_related_field = ['alrm_grp','corr_req','tckt_req','is_sia','alrm_category','ior']
	    event_trap_dict[key] ={}
	     
	    for attr in attr_list:
		if attr in alarm_specific_attr:
		    event_trap_dict[key][attr] = down_device_dict[key].get(conv_switch_mapping_dict[attr],'')
		    if attr == 'severity':
			event_trap_dict[key][attr] = ALARM_FLAGS.get(down_device_dict[key].get(conv_switch_mapping_dict[attr],''),1)
		elif attr in mat_related_field:
		    attr_value =  self.mat_data.get(mat_key).get(conv_switch_mapping_dict[attr],'')
		    event_trap_dict[key][attr] = attr_value
		elif attr == 'parent_alrm_id':
		    event_trap_dict[key][attr] = alarm_id
		else:
		    event_trap_dict[key][attr] = static_data.get(conv_switch_mapping_dict[attr],'')
	    event_trap_dict[key]['trap_type'] = 'converter_or_ptpbh_trap'
	    event_trap_dict[key]['base_trap_oid'] = '.1.3.6.1.4.1.43900.2.2.1.0.0.1'
	    event_trap_dict[key]['alrm_desc'] = "{0} : {1} : {2} : {3}".format(down_device_static_dict.get(key).get('city'),
									 down_device_static_dict.get(key).get('bs_name'),
									 key,
									 event_trap_dict[key]['alrm_name'])
	    alarm_id = event_trap_dict[key]['alrm_id']
        except Exception as e:
	    logger.error('Error Creating  Converter/Switch Trap \n Exception : {0}'.format(e))

	return event_trap_dict,alarm_id

    def make_dict_for_idu_odu_trap(self,**kwargs):
        """Creating Trap dict for idu and odu."""   
	event_trap_dict = {}
	global bs_mapping_dict
	down_device_dict = kwargs['down_device_dict']
	down_device_static_dict = kwargs['static_dict']
	ckt_dict = kwargs['ckt_dict']
	alarm_id = kwargs.get('alarm_id')
	bs_list = kwargs['bs_list']
	parent_ac = kwargs['parent_ac']
	attr_list = idu_or_odu_trap_vars
	idu_odu_alarm_id ={}

	alarm_specific_attr = ['alrm_desc','alrm_name','time_stamp','severity','alrm_id','resource_name','additional_f_4','device_ip']
	mat_related_field = ['alrm_grp','corr_req','tckt_req','is_sia','alrm_category']
	for key,value in down_device_dict.iteritems():
	    try:
		if key in bs_list:
		    alarm_name= value.get('alarm_name','')
		    severity = value.get(bs_mapping_dict['severity'],'') 
		    mat_key = (alarm_name,severity)                     # Master Alarm Table key.
		    ac = down_device_dict.get(key).get('category')      # Device alarm category.
		    # If parent, child alarm category doesn't match then parent alarm id = None.
		    if parent_ac:
			if not bool(ac & parent_ac):
			    alarm_id = None
			else:
			    alarm_id = kwargs.get('alarm_id')
			
		    #Check if traps has been set already in previous correlation cycle.
		    ip = key
		    correlated_trap_key = ip+'_'+alarm_name
		    redis_conn = self.redis_conn()
		    if redis_conn.hexists('correlated_traps',correlated_trap_key):
			continue

		    event_trap_dict[key] ={} 
		    #idu_odu_alarm_id[value.get('ip_address')] = value.get('unique_id')	
		    for attr in attr_list:
			if attr in alarm_specific_attr:
			    if attr == 'severity':
				attr_value = ALARM_FLAGS.get(value.get(bs_mapping_dict[attr],''),1)
			    else:	
				attr_value = value.get(bs_mapping_dict[attr],'')
			elif attr in mat_related_field:
			    attr_value = self.mat_data.get(mat_key).get(bs_mapping_dict[attr],'')
			else:
			    attr_value = down_device_static_dict[key].get(bs_mapping_dict[attr],'')
			    if attr == 'impacted_sector_count':
				attr_value = len(down_device_static_dict[key].get(bs_mapping_dict['sector_ids'],[]))
			    if attr == 'sector_ids' and attr_value:
				attr_value = ",".join(list(attr_value))
			    elif attr == 'parent_alrm_id':
				attr_value = alarm_id
			event_trap_dict[key][attr] = attr_value
		    event_trap_dict[key]['trap_type'] = 'idu_or_odu_trap'
		    event_trap_dict[key]['categorization_tier_1'] = 'DEVICE'
		    event_trap_dict[key]['categorization_tier_2'] = 'WIMAX-WiMAX-BTS'
		    event_trap_dict[key]['additional_f_1'] = 1
		    event_trap_dict[key]['additional_f_2'] = 1
		    event_trap_dict[key]['additional_f_4'] = 'Monolith-RF'
		    event_trap_dict[key]['additional_f_5'] = 1
		    # additional_f_8: Customer count-> Number of customer affected.
		    event_trap_dict[key]['base_trap_oid'] = '.1.3.6.1.4.1.43900.2.2.1.0.1.1'
		    event_trap_dict[key]['alrm_desc'] = "{0} : {1} : {2} : {3}".format(down_device_static_dict.get(key).get('city'),
										 down_device_static_dict.get(key).get('bs_name'),
										 key,
										 event_trap_dict[key]['alrm_name'])
		    if key in ckt_dict:
			event_trap_dict[key]['additional_f_8'] = len(ckt_dict.get(key))
		    else:
			event_trap_dict[key]['additional_f_8'] = 0
	    except Exception as e:
		logger.error('Error Creating  IDU/ODU Trap \n Exception : {0}'.format(e))
		
	return event_trap_dict
   
   
    def get_siteB_switch_conv(self,backhaul_ended_switch_con_ip):
        """Function returns switch/converter information connected to PTP-BH. """
	redis_conn = self.redis_conn()
	switch_conv_id,static_dict,dynamic_dict = None,None,None
	if backhaul_ended_switch_con_ip:
	    try:
		static_dict = redis_conn.get('static_' + backhaul_ended_switch_con_ip)
		static_dict = eval(static_dict)
		inventory_tree = redis_conn.get(static_dict.get('inventory_id'))
		inventory_tree = eval(inventory_tree)
		if inventory_tree:
		    switch_conv_id = inventory_tree.get(backhaul_ended_switch_con_ip)
	    except Exception as e:
		logger.error('Error get_siteB_switch_conv \n Exception : {0}'.format(e))
	return backhaul_ended_switch_con_ip,static_dict

    def max_value(self, down_device_id_list, down_device_dict, static_dict):

	"""Calclculate root cause element of the down devices and send idu/odu and circuit of connected ss for sending traps
           Args:
                down_device_id_list(list): List of down devices
                down_device_dict(dict): Key value pair of device id and it's alarm information.
                static_dict(dict): Dictionary of device information.

            return:
                rc_element_id: rooc cause element device id(Either converter/Switch).
                ckt_dict: circuit list for each idu/odu device down in topology.
                flags: dictionary of variables to identify PTP_BH scenario and information needed in correlation.
                down_device_dict: Alarm information dictionary for down devices.
                static_dict: Device information dictionary for down devices.
		non_rc_switch_conv: Swtich/converter ip which is not root cause in hierarchy.
                bs_list:  List of down BaseStation devices.
                ss_list:  List of down SubStation devices.
                del_ss: SS device list needs to be deleted.

        """
	element_dict = defaultdict(list)
	rc_element = None
	bs_ss_dict = {}
	priority = {
		    'popconverter':5,
		    'btsconverter':4,
		    'bsswitch':3,
		    'bs':2,
		    'ss':1,
	}
	ptp_bh_flag = 0
	is_backhaul = 0
	backhaul_id = None
	backhaul_ended_switch_con_ip =None
	conv_switch_siteb = None	
	ckt_dict = defaultdict(list)
	del_ss = []
	for key,value in down_device_dict.iteritems():
	    try:
		device_static_data = static_dict.get(key)
		ip_address = value.get('ip_address')
		ac = value.get('category')			# ac stands for alarm category.
		resource_name = device_static_data['resource_name'].lower()
		pvalue = priority.get(resource_name)
		if device_static_data.get('ptp_bh_flag') == 1:
		    ptp_bh_flag = 1 
		# pvalue=1: device is either substaion/ptp type device.
		if pvalue == 1:
		    backhaul = device_static_data.get('backhaul')
		    bs_ip = device_static_data.get('parent_ip')
		    if bs_ip in down_device_dict.keys():
			# parent alarm category parent_ac
			parent_ac = down_device_dict.get(bs_ip).get('category')
		    else:
			parent_ac = None
     
		    ptp_bh_type = device_static_data.get('ptp_bh_type')
		    # Max value filteration for ptp device
		    # It could be normal ptp/ptpbackhaul device.
		    if ptp_bh_type == 'fe' or ptp_bh_type == 'ne':
			if backhaul and ptp_bh_type == 'ne':
			    backhaul_id = key
			    backhaul_ended_switch_con_ip = device_static_data.get('child_switch')
			    # if condition to check is_backhaul is already assigned value or not.
			    if not is_backhaul:
				is_backhaul = 1

			elif backhaul and ptp_bh_type == 'fe':
			    # Condition if NearEnd is having alarm.
			    # if parent_ac:- mean if parent exist then check the category
			    if parent_ac: 
				# bool(ac & parent_ac), checks if category is common with parent device.
				if bool(ac & parent_ac):
				    del_ss.append(key)
				    continue
			    else:
				backhaul_id = key
				backhaul_ended_switch_con_ip = device_static_data.get('child_switch')
			    if not is_backhaul:
				is_backhaul = 1
		    
			elif ptp_bh_type == 'ne':
			    if device_static_data.get('circuit_id'):
				ckt_dict[key].append(device_static_data.get('circuit_id'))

			elif ptp_bh_type == 'fe':
			    if parent_ac:
				if bool(ac & parent_ac):
				    del_ss.append(key)
				    continue
			    else:
				if device_static_data.get('circuit_id'):
				    ckt_dict[key].append(device_static_data.get('circuit_id'))

		    else:
			if parent_ac:  			
			    if bool(ac & parent_ac):	# If Parent And Child have Category in common.
				del_ss.append(key)		# Delete child device and Store it's circuit id to Circuit dict.
				if device_static_data.get('circuit_id'):
				    ckt_dict[bs_ip].append(device_static_data.get('circuit_id'))
				continue

			    elif ptp_bh_type == 'fe':
				if parent_ac: 
				    if bool(ac & parent_ac):
					del_ss.append(key)
					continue
				else:
				    if device_static_data.get('circuit_id'):
					ckt_dict[key].append(device_static_data.get('circuit_id'))
			else:
			    if parent_ac:  			
				if bool(ac & parent_ac):	# If Parent And Child have Category in common.
				    del_ss.append(key)		# Delete child device and Store it's circuit id to Circuit dict.
				    if device_static_data.get('circuit_id'):
					ckt_dict[bs_ip].append(device_static_data.get('circuit_id'))
				    continue

	        element_dict[pvalue].append(key)
	    except Exception as e:
		logger.error('Error Max Value function \n Exception : {0}'.format(e))	
	# range(3,6) is for BsSwitch(3),BsConverter(4),PopConverter(5).
	# Ignoring Switch events in Sprint2 by assigning range(3,6) to range(4,6)
	conv_switch_list= [element_dict.get(index) for index in range(4,6) if element_dict.get(index)]
	conv_switch_list = list(itertools.chain(*conv_switch_list))
	sitea_conv_switch_list =[ih_id for ih_id in conv_switch_list if not static_dict.get(ih_id).get('ptp_bh_flag')]
	siteb_conv_switch_list = [ih_id for ih_id in conv_switch_list if static_dict.get(ih_id).get('ptp_bh_flag')]
	conv_switch_siteb = siteb_conv_switch_list[0] if siteb_conv_switch_list else None

	rc_element,non_rc_switch_conv = self.find_root_cause(sitea_conv_switch_list, down_device_dict)
	if not rc_element:
	    rc_element = conv_switch_siteb

	bs_list =  element_dict[2]
	ss_list =  element_dict[1]
	flags = {}
	flags['backhaul_id'] = backhaul_id
	flags['is_backhaul'] = is_backhaul
	flags['ptp_bh_flag'] = ptp_bh_flag               #Inventory is having ptp backhaul device or not.
	flags['backhaul_ended_switch_con_ip']= backhaul_ended_switch_con_ip
	flags['bs_ss_dict']= bs_ss_dict                  # basestation substation device mapping
	flags['conv_switch_siteb'] = conv_switch_siteb   # Siteb switch/converter ip.
	#return (down_device_dict,static_dict,rc_element,non_rc_switch_conv,bs_list,ss_list,ckt_dict,flags),del_ss

	# Changes For new Requirement
	# Generate trap only if SS or BS devices are down
	# If converter is Down: Do not generate any Traps.
	#Cases Handled here:
	#1.) SiteA down
	#2.) SiteA and SiteB down
	#
	#Case Need to handle in further code.
	#1.) Only SiteB down.
	if sitea_conv_switch_list:
	    return None,None
	else:
	    non_rc_switch_conv = None
	    return (down_device_dict,static_dict,rc_element,non_rc_switch_conv,bs_list,ss_list,ckt_dict,flags),del_ss 

    def find_root_cause(self,switch_conv_list,down_device_dict):
	"""Find Root Cause in Switch and converters connected in hierarchy
	   return:
		rc_element = root cause element, used as parent device for basestation.
		non_rc_switch_conv: list of switch/conv device,traps will be sent seperately.
	 """
	non_rc_switch_conv = list()
	length = len(switch_conv_list)
	rc_element = None
	if length== 1:
	    rc_element = switch_conv_list[0]
	elif length== 2:
	    element0_category = down_device_dict[switch_conv_list[0]].get('category')
	    element1_category = down_device_dict[switch_conv_list[1]].get('category')
	    if bool(element0_category & element1_category):
		rc_element = switch_conv_list[1]
	    else:
		rc_element = switch_conv_list[0]
		non_rc_switch_conv.append(switch_conv_list[1])
	elif length== 3:
	    element0_category = down_device_dict[switch_conv_list[0]].get('category')
	    element1_category = down_device_dict[switch_conv_list[1]].get('category')
	    element2_category = down_device_dict[switch_conv_list[2]].get('category')
	    if bool(element0_category & element1_category) and bool(element1_category & element2_category):
		rc_element = switch_conv_list[2]
	    elif bool(element0_category & element1_category):
		rc_element = switch_conv_list[1]
		non_rc_switch_conv.append(switch_conv_list[2])
	    else:
		rc_element = switch_conv_list[0]
		if bool(element1_category & element2_category):
		    non_rc_switch_conv.append(switch_conv_list[2])
		else:
		    non_rc_switch_conv.append(switch_conv_list[1])
		    non_rc_switch_conv.append(switch_conv_list[2])	
	return rc_element,non_rc_switch_conv

    def create_traps(self,**params):
        """Create traps for Down devices according to Scenarios defined in document.

           :kwargs
                params(dict): parameters to create trap for down devices
                params['down_device_dict']: Alarm information dictionary for fault devices.
                params['static_dict']: Device information dictionary for fault devices.
                params['backhaul_id']: Device id for PTPBH(Nearend/Farend), if any trap/event occured.
                params['backhaul_ended_switch_con_ip']: SiteB swith/converter id.
                params['ptp_bh_flag']: Flag to identify if PTP BH present in inventory toplogy.
                params['is_backhaul']: Flag to identify if any PTP BH (Nearend/farend) id down.
                params['rc_element']: Conv/switch down information.
                params['non_rc_switch_conv']: Not root cause elment, traps will be sent seperately.
                params['bs_list']:  List of down BaseStation devices.
                params['ss_list']:  List of down SubStation devices.
                params['bs_ss_dict']: bs ss parent child mapping.
                params['ptp_list']: List of faulted PTP devices.
                params['ckt_dict']: Circuit list corrospoding to each idu/odu device down.
                params['alarm_id']: Alarm Unique id
        """

	backhaul_id = params['backhaul_id']
	is_backhaul = params.get('is_backhaul')
	rc_element = params['rc_element']
	down_device_static_dict = params['static_dict']
	down_device_dict = params['down_device_dict']
 	siteb_switch_conv_id = params.get('siteb_switch_conv_id')
	non_rc_switch_conv = params.get('non_rc_switch_conv')	
	ptp_list = params.get('ptp_list')
	ss_list = params.get('ss_list')
	alarm_id = params.get('alarm_id')
	trap_list = [] 
	rc_alarm_id = None
        ss_trap = {}
        bs_trap = {}
        rc_element_dict=None
	non_rc_element_dict = dict()
	# Fault in either PTP-BH device or switch/converter.
	if is_backhaul or rc_element:
	    try:
		if is_backhaul:
		    if not siteb_switch_conv_id:
			siteb_switch_conv_id, siteb_switch_conv_static_data = self.get_siteB_switch_conv(params['backhaul_ended_switch_con_ip'])
			down_device_static_dict[siteb_switch_conv_id] = siteb_switch_conv_static_data
			params.update({'siteb_switch_conv_id': siteb_switch_conv_id})
		    down_device_static_dict[siteb_switch_conv_id]['parent_ip'] = down_device_static_dict[backhaul_id].get('parent_ip')

		    if down_device_static_dict[backhaul_id]['ptp_bh_type'] == 'fe':
			down_device_static_dict[siteb_switch_conv_id]['pop_ip'] = ''

		    if params.get('sitea_rc_element'):
			sitea_rc_element = params.get('sitea_rc_element')
			sitea_ac = down_device_dict.get(sitea_rc_element).get('category')
			siteb_ac = down_device_dict.get(backhaul_id).get('category')
			# Update alarm id as None if SiteA switch/conv and PTP-bh don't have common Alarm Category.
			if not bool(sitea_ac & siteb_ac):   
			    params.update({'alarm_id':None})
		rc_element_dict,rc_alarm_id = self.make_dict_for_conv_swich_trap(**params)
		if not alarm_id:
		    params.update({'alarm_id': rc_alarm_id })
		# If siteb PTP-BH device is down(is_bakchaul=True) then Use PTP BH device as parent device for SiteB idu/odu. 
		if is_backhaul:
		    parent_ac = down_device_dict.get(backhaul_id).get('category')
		# Else Siteb switch/converter will be parent of siteb idu/odu.
		else:
		    parent_ac = down_device_dict.get(rc_element).get('category')
		params.update({'parent_ac':parent_ac})

		# Make down IDU/ODU traps for the affected siteB switch/converter 
		bs_trap  = self.make_dict_for_idu_odu_trap(**params)

		# Filter out the ptp devices where alarm category matches with parent device.
		filtered_ptp= []
		for ptp_device in ptp_list:
		    ac = down_device_dict[ptp_device].get('category')
		    if bool(ac & parent_ac):
		       filtered_ptp.append(ptp_device) 

		# Make SS traps(idu/odu ss+ ptp trap).
		# ss_list: list of ss/ptp device where Either parent device is Ok or category doesn't match for ss and parent.
		ss_list = list(set(ss_list)-set(filtered_ptp))  # Remove PTP devices for which parent category match.
		params.update({'ss_list':ss_list})
		ss_trap = self.make_dict_for_ss_trap(**params)

		# Temporary trap dict for ptp device
		params.update({'ss_list':filtered_ptp})
		ss_ptp_trap = self.make_dict_for_ss_trap(**params)
		for key in ss_ptp_trap.keys():
		    ss_ptp_trap[key]['parent_alrm_id'] = params.get('alarm_id')

		#ckt dict for idu odu and ptp ckt dict
		input_trap_dict = {}
		input_trap_dict.update(bs_trap)
		input_trap_dict.update(ss_ptp_trap)
		params.update({'idu_odu_trap_dict': input_trap_dict})
		ckt_element_list = self.make_dict_for_ckt(**params)
	    
		# Non Root Cause Switch Converter Traps
		params.update({'is_backhaul':None, 'alarm_id':None})
		if non_rc_switch_conv:
		    for switch_conv in non_rc_switch_conv:
			params.update({'rc_element': switch_conv})
			trap_dict, alarm = self.make_dict_for_conv_swich_trap(**params)
			if trap_dict:
			    non_rc_element_dict.update(trap_dict)

		trap_list = rc_element_dict.values() + non_rc_element_dict.values() + bs_trap.values()+ \
								 ss_trap.values() + ckt_element_list
	    except Exception as e:
		logger.error('Error in  Create Traps Root Cause clause \n Exception : {0}'.format(e))

	elif params.get('bs_list'):
	    try:
		params.update({'parent_ac':None})
		bs_trap = self.make_dict_for_idu_odu_trap(**params)

		ss_trap = self.make_dict_for_ss_trap(**params)
		
		params.update({'idu_odu_trap_dict':bs_trap, 'parent_ac':set([])})
		ckt_element_list = self.make_dict_for_ckt(**params)
		    
		trap_list = bs_trap.values() + ss_trap.values() + ckt_element_list
	    except Exception as e:
		logger.error('Error in  Create Traps  Base Station clause \n Exception : {0}'.format(e))
	    
	elif params.get('ss_list'):
	    try:
		ss_trap = self.make_dict_for_ss_trap(**params)
		trap_list = ss_trap.values()
	    except Exception as e:
		logger.error('Error in  Create Traps  Sub Station clause \n Exception : {0}'.format(e))
	return rc_alarm_id,trap_list

    def high_priority(self,alarm_dict):
	"""
	Alarm filteration for each fault device based on priority given in mat table.
	"""
	alarm_tuples = alarm_dict.keys()
	priority_values = [self.alarm_priority_dict.get(alarm) for alarm in alarm_tuples]
	index_priority = deepcopy(priority_values)
	priority_values.sort(reverse=True)
	if priority_values:
	    try:
		priority = priority_values[0]
		index = index_priority.index(priority)
		alarm = alarm_tuples[index]
		alarm_severity = alarm[1]
		if alarm_severity == 'clear':
		    return None
		else:
		    clear_alarm = self.alarm_mapping_dict.get(alarm)
		    if clear_alarm not in alarm_tuples:
			return alarm
		    else:
			cur_timestamp = alarm_dict[alarm]['timestamp']
			clear_timestamp = alarm_dict[clear_alarm]['timestamp']
			if clear_timestamp > cur_timestamp:
			    alarm_dict.remove(alarm)
			    self.high_priority(alarm_dict)
			else:
			    return alarm
	    except Exception as e:
		logger.error('Error in Filtering Traps/events based on priority \n Exception : {0}'.format(e))
	else:
	    return None

@app.task(name='clear_trap')
def clear_trap(keys):
    """
    Task to send Clear traps to Monolith.
    Extract traps from redis modify trap and send it to monolith.
    """
    cor_obj = correlation()
    redis_conn = cor_obj.redis_conn()
    p = redis_conn.pipeline()

    [p.hget('correlated_traps',key) for key in keys]
    clear_traps = p.execute()
    clear_traps = map(lambda trap: eval(trap),filter(lambda trap: trap !=None, clear_traps))
    
    #Remove traps from Redis database
    [p.hdel('correlated_traps',key) for key in keys]
    p.execute()
    map(lambda trap: trap.update({'severity':ALARM_FLAGS.get('clear')}) ,clear_traps)
    if clear_traps:
	trap_sender_task.s(clear_traps).apply_async()

    # Update device_deviceticket table for clear trap.
    query_data = []
    for trap in clear_traps:
	data = {}
	data = {
		'ip_address':trap.get('resource_name'),
		'alarm_id':trap.get('alrm_id')
		}
	query_data.append(data)
    table = 'device_deviceticket'
    columns = ('ip_address','alarm_id')
    p0 = "DELETE FROM  %(table)s WHERE " % {'table': table}
    p2 = ' and '.join(map(lambda x: x+'= %('+ x + ')s', columns))
    qry = ''.join([p0, p2])
    if query_data:
	    try:
		# Remove Alarm information fro User application database.
		export_traps = ExportTraps()
		# Choose database name according to User application server.
		export_traps.exec_qry(qry, query_data, db_name='application_db')
	    except Exception as exc:
		inserted = False
		logger.error('Exc in mysql trap insert: {0}'.format(exc))


@app.task(base=DatabaseTask, name='correlation_update_inventory')
def correlation_update_inventory():
    """ Task Updates traps and events into inventory hierarchy"""
    cor_obj=correlation()
    redis_cnx = cor_obj.redis_conn()
    cor_obj.update_redis_inventory_hierarchy(redis_cnx)

@app.task(base=DatabaseTask, name='correlation_down_event')
def correlation_down_event():  
    inventory_list = list()
    cor_obj = correlation() 
    # redis Connection
    #rds_cli = RedisInterface(custom_conf={'db': 5})
    redis_conn =  cor_obj.redis_conn()
  
    # Extract alarm data Inventory of all devices present in Redis
    current_time = datetime.now().strftime('%s')
    invent_dict = redis_conn.get('invent_dict')
    invent_dict = eval(invent_dict)
	
    # Filtering inventory hierarchy  
    # TODO: change back time to 600
    invent_ids = filter(lambda x:int(current_time) - int(invent_dict[x]['timestamp']) >360  and 
		 int(current_time) - int(invent_dict[x]['timestamp']) <= 80000 , invent_dict.keys())
    map(lambda x:  invent_dict.pop(x),filter(lambda x: x not in invent_ids,invent_dict.keys()))
    map(lambda x: invent_dict[x].pop('timestamp', None), invent_dict.keys())		
  
    # Task to update invent_dict:- remove invent id for which correlation is in process.
    update_invent_dict.s(invent_ids).apply_async()  

    # Todo: filter trap/event based on mat . store the final alarm data to redis and forward the inventory for correlation.
    """
    Dictionary from MAT to filter trap/event based on priority.
    
    priority = {alarm1:1,
		alarm2:2,
		alarm3:3,
		alarm4:4,
		}

    """
    trap_list = []
    redis_keys = []
    #redis_keys.extend(down_device_dict.keys())
    for id in invent_ids:
	alarm_invent_dict = invent_dict.get(id)
	down_device = []
	invent_down_device_dict = {}

	# For each ip filter its trap/event based on MAT priority.
	remove_ip = []
	for ip in alarm_invent_dict.keys():
	    alarm_dict = alarm_invent_dict[ip]
	    alarm= cor_obj.high_priority(alarm_dict)
	    if alarm:
	        alarm_info = alarm_invent_dict[ip].get(alarm)
	        invent_down_device_dict[ip] = alarm_info
                down_device.append(ip)	
	    else:
		remove_ip.append(ip)
	# remove ip from inventory for, which no fault found.
	map(lambda ip: alarm_invent_dict.pop(ip), remove_ip)
	ip_s = alarm_invent_dict.keys()
	p = redis_conn.pipeline()
	[p.get(str('static_')+ip) for ip in ip_s]
	static_info = p.execute()
	invent_static_dict = dict((ip,eval(static_data)) for ip,static_data in zip(ip_s,static_info))
        max_value_params,del_ss= cor_obj.max_value(down_device, invent_down_device_dict, invent_static_dict)
	if not max_value_params:
	    continue
	trap_list.append(max_value_params)
	if del_ss:
	    for del_ss_key in del_ss:
		del invent_down_device_dict[del_ss_key]
	    
        params = max_value_params,invent_ids,redis_keys
        send_traps.s(params).apply_async()

@app.task(base=DatabaseTask, name='send_traps')
def send_traps(params):
    """ Create traps for down device.
        :Args:
           params(list)        : trap_list, mat_entries, invent_id_list, redis_keys.
           invent_id_list(list): List of inventory id for which Correlation required.
           redis_keys(list)    : List of Redis keys.
    """
    trap_params,invent_id_list,redis_keys = params
    cor_obj = correlation()
    final_trap_list = []
    final_traps = []
    params = {}
    query_data = []
    siteb_params = {}
    sitea_trap_list = []
    siteb_trap_list = []
    down_device_dict, down_device_static_dict, rc_element, non_rc_switch_conv,\
				    bs_down_list, ss_down_list, ckt_dict, flags = trap_params
    ptp_bh_flag = flags['ptp_bh_flag']
    bs_ss_dict = flags['bs_ss_dict']
    is_backhaul =flags['is_backhaul']
    backhaul_id =flags['backhaul_id']
    conv_switch_siteb = flags['conv_switch_siteb']
    backhaul_ended_switch_con_ip = flags['backhaul_ended_switch_con_ip']
    params.update({'down_device_dict': down_device_dict,
		   'static_dict': down_device_static_dict,
		   'backhaul_id':backhaul_id ,
		   'backhaul_ended_switch_con_ip': backhaul_ended_switch_con_ip, 
		   'is_backhaul': is_backhaul ,
		   'ptp_bh_flag' : ptp_bh_flag
    })

    if backhaul_id and backhaul_id in ss_down_list:
	ss_down_list.remove(backhaul_id)

    sitea_ptp_down_list = [ptp_down_device for ptp_down_device in ss_down_list
			    if down_device_static_dict[ptp_down_device].get('resource_type') == 'PTP'
			    and not down_device_static_dict[ptp_down_device].get('ptp_bh_flag')]

    siteb_ptp_down_list = [ptp_down_device for ptp_down_device in ss_down_list
			    if down_device_static_dict[ptp_down_device].get('resource_type') == 'PTP'
			    and down_device_static_dict[ptp_down_device].get('ptp_bh_flag')]

    siteb_bs_down_list = [bs_down_device for bs_down_device in bs_down_list  
			    if down_device_static_dict[bs_down_device].get('ptp_bh_flag') ]
    siteb_ss_down_list = [ss_down_device for ss_down_device in ss_down_list 
		    if down_device_static_dict[ss_down_device].get('ptp_bh_flag') ]
    sitea_bs_down_list = list(set(bs_down_list) - set(siteb_bs_down_list))
    sitea_ss_down_list = list(set(ss_down_list) - set(siteb_ss_down_list))
    sitea_params = deepcopy(params)
    siteb_params = deepcopy(params)

    sitea_params.update({'rc_element':None,
			'bs_list':sitea_bs_down_list,
			'ss_list':sitea_ss_down_list,
			'ptp_list': sitea_ptp_down_list,
			'bs_ss_dict': bs_ss_dict,
			'ckt_dict': ckt_dict,
			'non_rc_switch_conv': non_rc_switch_conv,
			'alarm_id': None,})

    siteb_params.update({'rc_element':None,
			 'bs_list': siteb_bs_down_list,
			 'ss_list': siteb_ss_down_list,
			 'ptp_list': siteb_ptp_down_list,
			 'ckt_dict': ckt_dict,
			 'bs_ss_dict': bs_ss_dict,
			 'siteb_switch_conv_id':None,
			 'sitea_rc_element':None,
			 'alarm_id': None})
    if rc_element:
	#if not down_device_static_dict[rc_element].get('ptp_bh_flag'):
	#    sitea_params.update({'rc_element':rc_element})
	sitea_params.update({'is_backhaul':None})
	rc_alarm_id,sitea_trap_list = cor_obj.create_traps(**sitea_params)
    
	if ptp_bh_flag:
	    siteb_params.update({'is_backhaul':is_backhaul,
				 'sitea_rc_element':sitea_params.get('rc_element')})
	    
	    # This is a case where both backhaul and SiteB switch/converter is down.
	    # Update alarm id with parent alarm id where connected PTP-BH is down.
	    siteb_params.update({'bs_list':[],
				 'ss_list':[],
				 'ptp_list':[]})
	    if is_backhaul:
		siteb_params.update({'alarm_id':rc_alarm_id})

	    #Flag to identify if SiteB switch/conv down or not.
	    #flag = 0 		
	    # Where Highest level element is SiteB switch/converter.
	    # Update rc element and key for Siteb switch/converter
	    #if down_device_static_dict[rc_element].get('ptp_bh_flag'):
	    #	flag = 1	
	    #	siteb_params.update({'rc_element':rc_element,
	    #		     'siteb_switch_conv_id':rc_element})
	    #else:
	    #	siteb_params.update({'rc_element':conv_switch_siteb})
	    #if flag==0:		
	    rc_alarm_id,siteb_trap_list = cor_obj.create_traps(**siteb_params)
    else:
	if ptp_bh_flag:
	    #Case: Backhaul device is down. Switch/conv fine.
	    # If Backhaul down do not generate trap for SiteB bs and ss devices.
	    # Generate trap only for PTP-BH.
	    if is_backhaul:
		siteb_params.update({'bs_list':[],
				     'ss_list':[],
				     'ptp_list':[]})
	        alarm_id,siteb_trap_list = cor_obj.create_traps(**siteb_params)
	    else:
		alarm_id,siteb_trap_list = cor_obj.create_traps(**siteb_params)
	sitea_params.update({'is_backhaul':None})
	alarm_id,sitea_trap_list= cor_obj.create_traps(**sitea_params)
    final_traps = sitea_trap_list + siteb_trap_list

    cor_obj=correlation()
    redis_conn = cor_obj.redis_conn()
    
    if final_traps:
	# External Handling of data manupulation for Monolith server.
	final_trap_list = cor_obj.final_trap_data_manupulation(final_traps)
        trap_sender_task.s(final_trap_list).apply_async()
    
    logger.error('Manupulated trap list {0}'.format(final_trap_list))
    non_ckt_trap_list = [trap_dict for trap_dict in final_trap_list if not trap_dict.get('impacted_circuit_ids')]
    p = redis_conn.pipeline()
    # Using Redis Hash to store Traps.
    # hset('dictname',key,value)
    [p.hset('correlated_traps', str(trap_dict.get('resource_name')+'_'+'_'.join(trap_dict['alrm_name'].split(' '))),
							 trap_dict) for trap_dict in non_ckt_trap_list]
    p.execute()

    # Store Correlated Trap information to User Applicatin Database.
    for trap in non_ckt_trap_list:
	data = {}
	data['ip_address']=trap.get('resource_name')
	data['alarm_id'] = trap.get('alrm_id')
	data['ticket_number'] = 'Not Available'
	query_data.append(data)
	
    table = 'device_deviceticket'
    columns = ('ip_address','ticket_number','alarm_id')
    p0 = "INSERT INTO %(table)s" % {'table': table}
    p1 = ' (%s) ' % ','.join(columns)
    p2 = ' , '.join(map(lambda x: ' %('+ x + ')s', columns))
    qry = ''.join([p0, p1, ' VALUES (', p2, ') '])
    if query_data:
	    try:
		# Store the Ticket and other information on User application database.
	        export_traps = ExportTraps()
		#cursor.executemany(qry,query_data)
		# Choose database name according to User application server.
		export_traps.exec_qry(qry, query_data, db_name='application_db')
	    except Exception as exc:
		inserted = False
		logger.error('Exc in mysql trap insert: {0}'.format(exc))

     


@app.task(name='trap_sender_task')
def trap_sender_task(traps):
    """Task to send correlated traps to Monolith"""
    for trap in traps:
	t = Trap(**trap)
	t.send_trap() 

 
@app.task(base=DatabaseTask, name='update_invent_dict')
def update_invent_dict(invent_ids):
    """Update invent_dict data in Redis database
       Remove inventory id's for which correlation has started.
    """
    #invent_ids = invent_ids.split(',')
    cor_obj = correlation()
    redis_conn = cor_obj.redis_conn()
    invent_dict = redis_conn.get('invent_dict')
    invent_dict = eval(invent_dict)
    map(lambda x: invent_dict.pop(x),filter(lambda y: y in invent_dict.keys(), invent_ids))
    redis_conn.set('invent_dict',invent_dict)
