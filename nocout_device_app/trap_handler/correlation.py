#from nocout_site import *
from start.start import app
from handlers.db_ops import RedisInterface,DatabaseTask 
from trap_handler.db_conn import ExportTraps,ConnectionBase
from uuid import uuid4
from operator import itemgetter
from datetime import datetime, time
from collections import defaultdict
from copy import deepcopy
import itertools
from trap_sender import Trap
from trap_sender import converter_or_ptpbh_trap_vars, idu_or_odu_trap_vars, ptp_or_ss_trap_vars, circuit_ids_trap_vars
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error
from os import system
from time import sleep
import time
import re
from pprint import pprint
def generateuuid():
	return str(uuid4())

conv_switch_mapping_dict = {
	'alrm_desc': 'alarm_description','alrm_name':'alias','time_stamp':'timestamp',
        'severity':'severity','tech':'technology','resource_name':'ip_address','pop_converter_ip':'pop_ip',
	'parent_ip':'parent_ip','parent_type':'parent_type','parent_port':'parent_port','bs_switch_ip':'bs_switch_ip',
	'aggr_switch_ip':'aggr_switch','pe_ip':'pe_ip','bs_name':'bs_name','region':'region','resource_type':'resource_type',	
	'coverage':'coverage','additional_f_1':'additional_f_1','additional_f_2':'priority',
	'additional_f_3':'city','categorization_tier_1':'alarm_type','bs_converter_ip':'bts_conv_ip',
	'categorization_tier_2':'categorization_tier_2','alrm_id':'unique_id','alrm_grp':'alarm_group',
	'corr_req':'correlation','tckt_req':'auto_tt','is_sia':'sia','alrm_category':'alarm_group',
	'IOR':'ior','parent_alrm_id':'parent_alarm_id','additional_f_4':'resource_type','additional_f_5':'additional_f_5','additional_f_6':'bso_ckt'	
}
bs_mapping_dict = {'alrm_desc': 'alarm_description',
	'alrm_name':'alias','time_stamp':'timestamp',
    	'severity':'severity','tech':'technology','resource_name':'ip_address',
    	'parent_ip':'parent_ip','parent_type':'parent_type','parent_port':'parent_port',
	'bs_name':'bs_name','region':'region','resource_type':'resource_type','sector_ids':'sector_id',
    	'coverage':'coverage','additional_f_1':'additional_f_1','additional_f_2':'priority',
    	'additional_f_3':'city','categorization_tier_1':'alarm_type',
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
    	'device_ip':'ip_address','additional_f_1':'additional_f_1','additional_f_2':'priority',
    	'additional_f_3':'city','customer_name':'customer_name',
	'impacted_circuit_id':'circuit_id','alrm_id':'unique_id','alrm_grp':'alarm_group',
	'corr_req':'correlation','tckt_req':'auto_tt','is_sia':'sia','alrm_category':'alarm_group',
	'additional_f_4':'additional_f_4','additional_f_5':'additional_f_5','child':'child',
	'additional_f_6':'bs_name'
}


ALARM_FLAGS = {
	      'critical': 3,
	      'clear':1,
	      'no': '0',
	      'major': 4,
	      'warning':6,
	      'indeterminate': 2,
	      'minor': 5
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
		circuit_dict = redis_conn.get('circuit_dict')
		cls._instance[cls].circuit_dict = eval(circuit_dict)
	    except Exception as e:
		logger.error("Exception: Redis database does not have sufficeint information for correlation process \
			      \nExecute command: python nocout/performance/service/mysql_test_ca.py\
				\nExecute command: python nocout/performance/service/fetch_device_sector_citcuit.py")
	        cls._instance[cls].mat_data = {} 
		cls._instance[cls].alarm_priority_dict = {}
		cls._instance[cls].alarm_mapping_dict = {}
		cls._instance[cls].circuit_dict = {}
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
 
    def update_event_invent_dict(self):
	"""
	Get the data(events) from redis.
	Filter it based on inventory id and store it accordingly.
	Craete a tuple (alarm_name,severity) from alarm data and store/update in alarm inventory, tuple as a key and value alarm data.
	
	Structure:
	event_invent_dict:{
		invent_id1:{
			'timestamp':342234323,
			'ip_address1':{
				(alarm_name,severity):alarm_data,
				(alarm_name,severity):alarm_data
			},
			'ip_address2':{
				(alarm_name,severity):alarm_data,
				(alarm_name,severity):alarm_data
			}
		}
		invent_id2:{
			'timestamp':234242411, 
			'ip_address3':{
				(alarm_name,severity):alarm_data,
				(alarm_name,severity):alarm_data
			}
		}
	}

	Events are being stored in redis queue named 'queue:events'
	'queue:events' = [(alarm_data1),(alarm_data2),.....,(alarm_datan)]

	Event structure will be like
	('', 'Device_not_reachable', '', '10.191.134.13', '', '', 'critical', '', '2016-09-17 10:21:05', '')

	Mapping between IP address and inventory id.
	ip_id = { ip_address: inventory_id }

	for e.g. 
	ip_id = { '10.175.44.9': 45, '121.89.44.2': 2 }

	"""
	redis_conn = self.redis_conn()
	clear_event_keys = []

	try:	
	    event_invent_dict = eval(redis_conn.get('event_invent_dict'))
	except Exception as e:
	    event_invent_dict = {}
	    redis_conn.set('event_invent_dict',{})
	
	ip_id = eval(redis_conn.get('ip_id'))                   

	# Get all the Events from redis queue
	number_of_events = redis_conn.llen('queue:events')

	if number_of_events > 0:

	    p = redis_conn.pipeline()
	    [p.lpop('queue:events') for i in range(number_of_events)]        # Alarm data(traps and events) from redis
	    events_list = p.execute()
	    events_list = [eval(t_e) for t_e in events_list]

	    #logger.error('Fetched Events list (before filter) %s'%(events_list))
	    events_list = self.filter_planned_events(events_list)
	    #logger.error('Fetched Events list (after filter) %s'%(events_list))

	    # Store events to event_invent_dict according to its structure show above.
	    for each_event in events_list:
		

	        ip = each_event[3]
	        alarm_name = each_event[1]
	        severity = each_event[6]
	        key = (alarm_name,severity)
	        id = ip_id.get(ip)

	        #if int(self.mat_data.get(key).get('correlation')) == 1:    
		if True:
		    if severity == 'clear':
		        clear_event_key = str(ip)+'_'+str(alarm_name)
		        clear_event_keys.append(clear_event_key)
     
		    alarm = dict()   
		    alarm['alarm_name'] = each_event[1]
		    alarm['alarm_description'] = each_event[2]
		    alarm['timestamp'] = int(datetime.strptime(each_event[8],"%Y-%m-%d %H:%M:%S").strftime('%s'))
		    alarm['severity'] = each_event[6]
		    alarm['unique_id'] = generateuuid()
		    alarm['ip_address'] = ip
		    alarm['inventory_id']= id
		    alarm['category'] = self.mat_data.get(key).get('category')
		    #Alarm name alias for monolith
		    alarm['alias'] = ' '.join(each_event[1].split('_'))

		    if id is not None:
		        if id in event_invent_dict:
			    if ip in event_invent_dict[id]:
			        event_invent_dict[id][ip][key] = alarm
			    else:
			        event_invent_dict[id][ip] = {}
			        event_invent_dict[id][ip][key] = alarm
		        else:
			    timestamp = each_event[8]
			    event_invent_dict[id] = {}
			    event_invent_dict[id]['timestamp'] = alarm['timestamp']
			    event_invent_dict[id][ip] = {}
			    event_invent_dict[id][ip][key] = alarm
		    else:
			logger.info("invent id not found for ip %s"%str(ip))

	    inventory_dict = {'event_invent_dict':event_invent_dict}
            self.insert_events_into_redis(inventory_dict)
	    
	    # Clear Trap Send Task
	    clear_event_keys = list(set(clear_event_keys))
	    # Call Clear Trap Task if Clear Trap Keys exsist.
	    if clear_event_keys:
	        clear_alarms.s(clear_event_keys).apply_async()

	    return True
	else:
	    return False

    def filter_planned_events(self, events_list):

	time_duration_dict = self.redis_conn().get("planned_events")
	if not time_duration_dict:
	    return events_list
	time_duration_dict = eval(time_duration_dict)

	filtered_list = []
	for each_event in events_list:
	    alarm_name = each_event[1]
	    ip = each_event[3]
	    t_time = int(datetime.strptime(each_event[8],"%Y-%m-%d %H:%M:%S").strftime('%s'))
	    trap_type = self.find_trap_type(alarm_name)
	    replaced_trap_type = {"odu1": "pmp1", "odu2":"pmp2"}.get(trap_type)	
	    try:
		t_time = int(datetime.strptime(each_event[8],"%Y-%m-%d %H:%M:%S").strftime('%s'))
		for i,v in time_duration_dict.iteritems():
		    if len(v) == 1:
		        if ip in v[0] and  int(i[0]) <= t_time and t_time < int(i[1]):
			    break
		    elif len(v) == 3:
			if ip in v[0] and  int(i[0]) <= t_time and t_time < int(i[1]) and v[2] == ip and v[1] == replaced_trap_type:
			    break
			elif trap_type not in ["odu1","odu2"] and ip in v[0] and  int(i[0]) <= t_time and t_time < int(i[1]):
			    break
		else:
		    filtered_list.append(each_event)
	    except Exception as e:
	        logger.error("Error in planned event Calculation: %s"%(e))

	return filtered_list 

    def insert_events_into_redis(self,event_dict,is_list=None):
	"""
	Insert Data to Redis Database
	"""
        p = self.redis_conn().pipeline()
        if is_list:
            [p.set(ih_count_id,event_entry) for event in event_dict for (ih_count_id,event_entry) in event.iteritems() ]
	else:
            [p.set(ih_count_id,event) for (ih_count_id,event) in event_dict.iteritems() ]
        p.execute()

    def final_trap_data_manupulation(self,trap_list):
	final_traps = []
	#trap_list = eval(trap_list)
	global converter_or_ptpbh_trap_vars
	global idu_or_odu_trap_vars
	global ptp_or_ss_trap_vars
	global circuit_ids_trap_vars

	req_fields = [
	    'parent_port', 'severity', 'corr_req', 'tckt_req',
	    'is_sia', 'impacted_sector_count', 'last_trap' ]
	dummy_attr_dict = {
	    		'additional_f_6': u'700.700.700.700',
			'additional_f_7': '600.600.600.600',
			'parent_ip': '400.400.400.400',
			'aggr_switch_ip': '700.700.700.700',
			'pe_ip': '600.600.600.600',
			'last_trap':1,
			'parent_alrm_id':''
			}
	garbage_value = 'abcd'
	garbage_int_value = '1234'
	for trap in trap_list:
	    try:
		tp = trap.get('trap_type')
		if tp == 'converter_or_ptpbh_trap':
		    compulsory_attrs = converter_or_ptpbh_trap_vars
		elif tp == 'idu_or_odu_trap':
		    compulsory_attrs = idu_or_odu_trap_vars
		elif tp == 'ptp_or_ss_trap':
		    compulsory_attrs = ptp_or_ss_trap_vars
		elif tp == 'circuit_ids_trap':
		    compulsory_attrs = circuit_ids_trap_vars
		#TODO Remove Extra lopping here
		for attr in compulsory_attrs:
		    if trap[attr] == '' or trap[attr] == 'NA' or trap[attr] == 'None' or trap[attr] == None:
			if attr in dummy_attr_dict.keys():
			    trap[attr] = dummy_attr_dict.get(attr)
			elif attr in req_fields:
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
	    'alrm_grp', 'alrm_name', 'severity', 'additional_f_1','additional_f_2', 'last_trap'
	]


	down_device_static_dict = kwargs.get('static_dict')
	idu_odu_trap_dict = kwargs.get('idu_odu_trap_dict')
	ckt_list_for_conv_sia = kwargs.get('ckt_list_for_conv_sia')
	#alarm_id = kwargs.get('alarm_id')
	circuit_dict = kwargs.get('ckt_dict')

	event_trap_dict = {}
	parent_alrm_id = None 
	final_circuit_traps_list = list()
	impacted_circuits = ''

	if idu_odu_trap_dict:

	    for key,value in idu_odu_trap_dict.iteritems():
		if down_device_static_dict.get(key).get('resource_type').lower() in ['converter','switch','ptp','PTP']:

		    impacted_circuits = ', '.join(ckt_list_for_conv_sia) if ckt_list_for_conv_sia else ''

		else:
		    ckt_list = circuit_dict.get(key) if circuit_dict.get(key) else list()
		    impacted_circuits = ', '.join(ckt_list)
		    
		event_trap_dict['seq_num'] = generateuuid()
		#  If idu/odu trap dict have parent alarm id that means it have common alarm category with it's parnet device.
		parent_alrm_id = None
		if value.get('alrm_id'):
		    parent_alrm_id = value.get('alrm_id')

		event_trap_dict['parent_alrm_id'] = parent_alrm_id 
		event_trap_dict['impacted_circuit_ids'] = impacted_circuits
		event_trap_dict['alrm_name'] = value.get('alrm_name') 
		event_trap_dict['alrm_grp'] = value.get('alrm_grp')  
		event_trap_dict['severity'] = value.get('severity')
		event_trap_dict['additional_f_1'] = ''
		event_trap_dict['additional_f_2'] = ''
		event_trap_dict['last_trap'] = ''
		event_trap_dict['trap_type'] = 'circuit_ids_trap'
		event_trap_dict['base_trap_oid'] = '.1.3.6.1.4.1.43900.2.2.1.0.3.1'
		final_circuit_traps_list.append(event_trap_dict)
		event_trap_dict = {}
		circuit_list = []

	return final_circuit_traps_list

    def make_dict_for_ss_trap(self,**kwargs):
        """ Creating Trap dictionary for SS and PTP"""
	event_trap_dict = {}
	global ss_mapping_dict
	down_device_dict = kwargs['down_device_dict']
	ss_list = kwargs['ss_list']
	attr_list = ptp_or_ss_trap_vars
	down_device_static_dict = kwargs['static_dict']

	alarm_specific_attr = ['alrm_desc','alrm_name','time_stamp','severity','alrm_id','resource_name','device_ip']
	mat_related_field = ['alrm_grp','corr_req','tckt_req','is_sia','alrm_category','additional_f_2']

	for key,value in down_device_dict.iteritems():
	    alarm_name= value.get('alarm_name','')
	    severity = value.get(ss_mapping_dict['severity'],'') 
	    mat_key = (alarm_name,severity)                     # Master Alarm Table key.
	    #Check if traps has been set already in previous correlation cycle.
	    ip = key

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
		if event_trap_dict[key]['alrm_name'] in ["PD_threshold_breach_major","PD threshold breach major"]:
            	    alarm_name_in_desc = "PD threshold breach"
		    event_trap_dict[key]['additional_f_2'] = 2

		else:
		    alarm_name_in_desc = event_trap_dict[key]['alrm_name']
		event_trap_dict[key]['alrm_desc'] = "{0} : {1} : {2} : {3}".format(down_device_static_dict.get(key).get('city'),
									     down_device_static_dict.get(key).get('bs_name'),
									     key,
									     alarm_name_in_desc)
	return event_trap_dict

    def make_dict_for_conv_swich_trap(self,**kwargs):
	"""
        Creating Trap dictionary for converter and swich.
	"""
	global conv_switch_mapping_dict
	event_trap_dict = {}

	down_device_dict = kwargs.get('down_device_dict')
	ptp_bh_flag = kwargs.get('ptp_bh_flag')
	down_device_static_dict = kwargs.get('static_dict')
	rc_element = kwargs.get('rc_element')
	is_backhaul = kwargs.get('is_backhaul')
	alarm_id = kwargs.get('alarm_id')
	siteb_switch_conv_id = kwargs.get('siteb_switch_conv_id')

	attr_list = converter_or_ptpbh_trap_vars
	# If PTP bh device is faulted, Create trap for ptpbh.
	if is_backhaul:
	    backhaul_id = kwargs.get('backhaul_id')
	    key = backhaul_id
	    static_data = down_device_static_dict[siteb_switch_conv_id]
	    static_data['resource_type'] = "PTP-BH"
	    static_data['technology'] = down_device_static_dict.get(backhaul_id).get('technology')
	    static_data['parent_type'] = down_device_static_dict.get(backhaul_id).get('parent_type')
	    static_data['parent_ip'] = down_device_static_dict.get(backhaul_id).get('parent_ip')
	    static_data['parent_port'] = down_device_static_dict.get(backhaul_id).get('parent_port')
	# Trap for switch/converter.
	else:
	    key = rc_element
	    static_data = down_device_static_dict.get(key)

	alarm_name= down_device_dict.get(key).get('alarm_name','')
	severity = down_device_dict.get(key).get(conv_switch_mapping_dict['severity'],'')
	mat_key = (alarm_name,severity)

	""" 
	#Check if traps has been set already in previous correlation cycle.
	ip = key
	correlated_trap_key = ip+'_'+alarm_name
	redis_conn = self.redis_conn()
	if redis_conn.hexists('correlated_traps',correlated_trap_key):
	    return None,None
	"""

	alarm_specific_attr = ['alrm_id','alrm_desc','alrm_name','time_stamp','severity','resource_name','additional_f_4',
	'categorization_tier_2']
	mat_related_field = ['alrm_grp','corr_req','tckt_req','is_sia','alrm_category','ior','additional_f_2','categorization_tier_1']
	event_trap_dict[key] ={}
	 
	for attr in attr_list:
	    if attr in alarm_specific_attr:
		event_trap_dict[key][attr] = down_device_dict[key].get(conv_switch_mapping_dict[attr],'')
		if attr == 'severity':
		    event_trap_dict[key][attr] = ALARM_FLAGS.get(down_device_dict[key].get(conv_switch_mapping_dict[attr],''),1)
		if attr == 'categorization_tier_2':
		    event_trap_dict[key][attr] = 'WIMAX-WiMAX-BTS'
		
	    elif attr in mat_related_field:
		attr_value =  self.mat_data.get(mat_key).get(conv_switch_mapping_dict[attr],'')
		event_trap_dict[key][attr] = attr_value
	    elif attr == 'parent_alrm_id':
		event_trap_dict[key][attr] = alarm_id
	    else:
		event_trap_dict[key][attr] = static_data.get(conv_switch_mapping_dict[attr],'')
		if attr == 'coverage':
		    event_trap_dict[key][attr] = static_data.get('device_vendor')

		if attr == 'pop_converter_ip' and static_data.get('resource_name') == 'BTSConverter':
                    event_trap_dict[key][attr] = ""

	event_trap_dict[key]['trap_type'] = 'converter_or_ptpbh_trap'
	event_trap_dict[key]['additional_f_1'] = 1
	event_trap_dict[key]['additional_f_4'] = 'Monolith-RF'

	if ptp_bh_flag:
	    ip_for_conv_cust_count = siteb_switch_conv_id
	else:
	    ip_for_conv_cust_count = key
	event_trap_dict[key]['additional_f_5'] = self.converter_customer_count(ip_for_conv_cust_count)

	event_trap_dict[key]['base_trap_oid'] = '.1.3.6.1.4.1.43900.2.2.1.0.0.1'

	if event_trap_dict[key]['alrm_name'] in ["PD_threshold_breach_major","PD threshold breach major"]:
	    alarm_name_in_desc = "PD threshold breach"
	else:
	    alarm_name_in_desc = event_trap_dict[key]['alrm_name']

	event_trap_dict[key]['alrm_desc'] = "{0} : {1} : {2}".format(
								     down_device_static_dict.get(key).get('bs_name'),
								     key,
								     alarm_name_in_desc)

	alarm_id = event_trap_dict[key]['alrm_id']
	return event_trap_dict,alarm_id

    def make_dict_for_idu_odu_trap(self,**kwargs):

	down_device_dict = kwargs.get('down_device_dict')
	down_device_static_dict = kwargs.get('static_dict')
	alarm_id = kwargs.get('alarm_id')
	bs_list = kwargs.get('bs_list')
	parent_ac = kwargs.get('parent_ac')

	event_trap_dict = {}
        global bs_mapping_dict
	attr_list = idu_or_odu_trap_vars
	idu_odu_alarm_id ={}

	alarm_specific_attr = ['alrm_desc','alrm_name','time_stamp','severity','alrm_id','resource_name','additional_f_4','device_ip']
	mat_related_field = ['alrm_grp','corr_req','tckt_req','is_sia','alrm_category','additional_f_2']
	for key,value in down_device_dict.iteritems():
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
		"""    
		#Check if traps has been set already in previous correlation cycle.
		ip = key
		correlated_trap_key = ip+'_'+alarm_name
		redis_conn = self.redis_conn()
		
		if redis_conn.hexists('correlated_traps',correlated_trap_key):
		    continue
		"""

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
			    sector_count = len(down_device_static_dict[key].get(bs_mapping_dict['sector_ids'],[]))
			    if sector_count:
				attr_value = sector_count
			    else:
				attr_value = 0
			if attr == 'sector_ids' and attr_value:
			    sectors = {}
                    	    for each_sector in attr_value:
                        	sectors[each_sector[0]]= each_sector[1]

			    attr_value = ",".join(sectors.values())
			elif attr == 'parent_alrm_id':
			    attr_value = alarm_id
		    event_trap_dict[key][attr] = attr_value
		event_trap_dict[key]['trap_type'] = 'idu_or_odu_trap'
		event_trap_dict[key]['categorization_tier_1'] = 'DEVICE'
		event_trap_dict[key]['categorization_tier_2'] = 'WIMAX-WiMAX-BTS'
		event_trap_dict[key]['additional_f_1'] = 1
		event_trap_dict[key]['additional_f_4'] = 'Monolith-RF'
		event_trap_dict[key]['additional_f_5'] = 1
		# additional_f_8: Customer count-> Number of customer affected.
		event_trap_dict[key]['base_trap_oid'] = '.1.3.6.1.4.1.43900.2.2.1.0.1.1'
		if event_trap_dict[key]['alrm_name'] in ["PD_threshold_breach_major","PD threshold breach major"]:
            	    alarm_name_in_desc = "PD threshold breach"
		else:
		    alarm_name_in_desc = event_trap_dict[key]['alrm_name']

		event_trap_dict[key]['alrm_desc'] = "{0} : {1} : {2} : {3}".format(down_device_static_dict.get(key).get('city'),
									     down_device_static_dict.get(key).get('bs_name'),
									     key,
									     alarm_name_in_desc)
		trap_type = 'event'
		customer_count = self.bs_customer_count(key, trap_type)
		if customer_count:
		    event_trap_dict[key]['additional_f_8'] = customer_count
		else:
		    event_trap_dict[key]['additional_f_8'] = "0"
		
	return event_trap_dict
   
   
    def get_siteB_switch_conv(self,backhaul_ended_switch_con_ip):
        """Function returns switch/converter information connected to PTP-BH. """
	redis_conn = self.redis_conn()
	switch_conv_id,static_dict,dynamic_dict = None,None,None
	if backhaul_ended_switch_con_ip:
	    static_dict = redis_conn.get('static_' + backhaul_ended_switch_con_ip)
	    static_dict = eval(static_dict)
	    inventory_tree = redis_conn.get(static_dict.get('inventory_id'))
	    inventory_tree = eval(inventory_tree)
	    if inventory_tree:
		switch_conv_id = inventory_tree.get(backhaul_ended_switch_con_ip)
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
	ss_list_for_sia = []
	ptp_ne_devices_list = []
	#logger.error("Max value params: %s\n%s\n%s"%(down_device_id_list, down_device_dict, static_dict))
	for key,value in down_device_dict.iteritems():

	    # key = ip_address, value = alarm_information
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
			ss_list_for_sia.append(key)
			# storing ptp device to remove from deleted devices as we need to send the trap for those devices
		        ptp_ne_devices_list.append(key)
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
		    ss_list_for_sia.append(key)
		    if parent_ac:  			
			if bool(ac & parent_ac):	# If Parent And Child have Category in common.
			    del_ss.append(key)		# Delete child device and Store it's circuit id to Circuit dict.
			    if device_static_data.get('circuit_id'):
			        ckt_dict[bs_ip].append(device_static_data.get('circuit_id'))
		            continue

	    element_dict[pvalue].append(key)

	# range(3,6) is for BsSwitch(3),BsConverter(4),PopConverter(5).
	# Ignoring Switch events in Sprint2 by assigning range(3,6) to range(4,6)
	conv_switch_list= [element_dict.get(index) for index in range(4,6) if element_dict.get(index)]
	conv_switch_list = list(itertools.chain(*conv_switch_list))
	sitea_conv_switch_list =[ih_id for ih_id in conv_switch_list if not static_dict.get(ih_id).get('ptp_bh_flag')]
	siteb_conv_switch_list = [ih_id for ih_id in conv_switch_list if static_dict.get(ih_id).get('ptp_bh_flag')]
	conv_switch_siteb = siteb_conv_switch_list[0] if siteb_conv_switch_list else None

	rc_element,non_rc_switch_conv = self.find_root_cause(sitea_conv_switch_list, down_device_dict)

	bs_list =  element_dict[2]
	ss_list =  element_dict[1]
	ckt_list_for_conv_sia = []

    	siteb_ss_down_list = filter(lambda x: static_dict[x].get('ptp_bh_flag'),ss_list_for_sia)
	#sitea_ss_down_list = list(set(ss_down_list) -set(siteb_ss_down_list)) 
	if not rc_element:
	    rc_element = conv_switch_siteb
	    if backhaul_id:
	        ckt_list_for_conv_sia,del_ss = self.extract_ckt_for_sia(backhaul_id, down_device_dict, static_dict, siteb_ss_down_list, del_ss)
		# Removing PTP list from deleted devices 
	        del_ss  = list(set(del_ss) - set(ptp_ne_devices_list)) 
	    #sitea_ckt_list_for_conv_sia = ''
	else:
	    ckt_list_for_conv_sia,del_ss = self.extract_ckt_for_sia(rc_element, down_device_dict, static_dict, ss_list_for_sia, del_ss)
	    # Removing PTP list from deleted devices 
	    del_ss  = list(set(del_ss) - set(ptp_ne_devices_list)) 
	#logger.error('$$$ %s %s'%(ckt_list_for_conv_sia,del_ss))
	flags = {}
	flags['ckt_list_for_conv_sia'] = ckt_list_for_conv_sia
	flags['backhaul_id'] = backhaul_id
	flags['is_backhaul'] = is_backhaul
	flags['ptp_bh_flag'] = ptp_bh_flag               #Inventory is having ptp backhaul device or not.
	flags['backhaul_ended_switch_con_ip']= backhaul_ended_switch_con_ip
	flags['bs_ss_dict']= bs_ss_dict                  # basestation substation device mapping
	flags['conv_switch_siteb'] = conv_switch_siteb   # Siteb switch/converter ip.
	logger.info('max value rc_element {0}'.format(rc_element))
	
	return (down_device_dict,static_dict,rc_element,non_rc_switch_conv,bs_list,ss_list,ckt_dict,flags),del_ss



    def extract_ckt_for_sia(self, rc_element,down_device_dict,static_dict,ss_list,del_ss):
	# If any Events comes for Converter and category doesn't match then for rc_element we need to send ciruit for down ss devics also
	# We need to delete those ss from current window to stop sending those alarms
	# Here we are considering only sitea scenario if any sitea converter is not down then we need to 
	# do the same thing for siteb converter(ptp-bh)
	ckt_list_for_conv_sia = []
	try:
	    ss_list_for_conv_sia = filter(lambda x: down_device_dict.get(x).get('category') & down_device_dict.get(rc_element).get('category'), ss_list)
	    del_ss_list_for_sia = list(set(ss_list_for_conv_sia) - set(del_ss))
	    del_ss.extend(del_ss_list_for_sia)
	    for entry in ss_list_for_conv_sia:

	        try:
		    ckt = static_dict.get(entry).get('circuit_id','')
		    ckt_list_for_conv_sia.append(ckt)
	        except Exception as e:
		    logger.info("Error: Could not retrieve static dict for SS")
	
	except:
	    logger.error("Error in sending the SIA traps for Converter")
        return ckt_list_for_conv_sia,del_ss	


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
    
    def make_idu_odu_trap(self,**kwargs):
        """Creating Trap dict for idu and odu."""

        idu_odu_trap = {}
        global bs_mapping_dict

        alarm = kwargs['alarm']
        static_inventory_data = kwargs['static_inventory_data']
        mat_data = kwargs['mat_data']

        attr_value = ''
        attr_list = idu_or_odu_trap_vars
	trap_type = self.find_trap_type(alarm.get('alarm_name'))

        alarm_specific_attr = ['alrm_id','alrm_desc','alrm_name','time_stamp','severity','alrm_id','resource_name','device_ip']
        mat_related_attr = ['alrm_grp','corr_req','tckt_req','is_sia','alrm_category','categorization_tier_1']

        for attr in attr_list:

            if attr in alarm_specific_attr:
		if attr == 'severity':
                    idu_odu_trap[attr] = ALARM_FLAGS.get(alarm.get(bs_mapping_dict[attr],''),1)
                else:
		    idu_odu_trap[attr] = alarm.get(bs_mapping_dict.get(attr),'')
            elif attr in mat_related_attr:
                idu_odu_trap[attr] = mat_data.get(bs_mapping_dict.get(attr),'')
            else:
                attr_value = static_inventory_data.get(bs_mapping_dict[attr],'')
                if attr == 'impacted_sector_count':
		    if trap_type in ['odu1','odu2']:
			attr_value = 1
		    else:
                        attr_value = len(static_inventory_data.get(bs_mapping_dict['sector_ids'],[]))
                if attr == 'sector_ids' and attr_value:
		    sectors = {}
		    for each_sector in attr_value:
			sectors[each_sector[0]]= each_sector[1]	

		    if trap_type == 'odu1':
			attr_value = sectors['43']
		    elif trap_type == 'odu2':
			attr_value = sectors['44']
		    else:	
                        attr_value = ','.join(sectors.values()) 

		elif attr == 'parent_alrm_id':
                    attr_value = alarm.get(bs_mapping_dict.get('alarm_id'),'')
                idu_odu_trap[attr] = attr_value

        idu_odu_trap['trap_type'] = 'idu_or_odu_trap'
        idu_odu_trap['categorization_tier_2'] = 'WIMAX-WiMAX-BTS'
        idu_odu_trap['additional_f_1'] = 1
        idu_odu_trap['additional_f_2'] = 1
        idu_odu_trap['additional_f_4'] = 'Monolith-RF'
        idu_odu_trap['additional_f_5'] = 1
	if trap_type == 'odu1' or trap_type == 'odu2':
	    idu_odu_trap['resource_type'] = 'ODU'

        # additional_f_8: Customer count-> Number of customer affected.
	idu_odu_trap['base_trap_oid'] = '.1.3.6.1.4.1.43900.2.2.1.0.1.1'
        idu_odu_trap['alrm_desc'] = "{0} : {1} : {2} : {3}".format(  static_inventory_data.get('city'),
                                                                        static_inventory_data.get('bs_name'),
                                                                        alarm.get('ip_address'),
                                                                        idu_odu_trap['alrm_name'] )
       

	customer_count = self.bs_customer_count(alarm.get('ip_address'), trap_type)

	if customer_count:
            idu_odu_trap['additional_f_8'] = customer_count
        else:
            idu_odu_trap['additional_f_8'] = "0"
       
        return idu_odu_trap

    def make_circuit_trap(self,**kwargs):
        """Create Trap for Circuit"""
	mapping_list = [
            'seq_num', 'parent_alrm_id', 'impacted_circuit_ids',
            'alrm_group', 'alrm_name', 'severity', 'additional_f_1','additional_f_2', 'last_trap'
        ]

        circuit_list = kwargs.get('circuit_list')
	idu_odu_trap = kwargs.get('idu_odu_trap')
	impacted_circuits = ', '.join(circuit_list)
        circuit_trap = {}

        if idu_odu_trap:

            circuit_trap['seq_num'] = generateuuid()
            #  If idu/odu trap dict have parent alarm id that means it have common alarm category with it's parnet device.
            parent_alrm_id = None
            if idu_odu_trap.get('parent_alrm_id'):
                parent_alrm_id = idu_odu_trap.get('parent_alrm_id')
            else:
                parent_alrm_id = idu_odu_trap.get('alrm_id')

            circuit_trap['parent_alrm_id'] = parent_alrm_id
            circuit_trap['impacted_circuit_ids'] = impacted_circuits
            circuit_trap['alrm_name'] = idu_odu_trap.get('alrm_name')
            circuit_trap['alrm_grp'] = idu_odu_trap.get('alrm_grp')
            circuit_trap['severity'] = idu_odu_trap.get('severity')
            circuit_trap['additional_f_1'] = ''
            circuit_trap['additional_f_2'] = ''
            circuit_trap['last_trap'] = ''
            circuit_trap['trap_type'] = 'circuit_ids_trap'
            circuit_trap['base_trap_oid'] = '.1.3.6.1.4.1.43900.2.2.1.0.3.1'

        return circuit_trap

    def create_alarms_for_traps(self,device_trap_list):
	"""
	Comments
	"""
	redis_conn = self.redis_conn()

	final_traps = []
	idu_odu_traps = []
	circuit_traps = []

        circuit_dict_data = redis_conn.get("circuit_dict")
        circuit_dict_data = eval(circuit_dict_data)


	if device_trap_list:

	    for each_trap in device_trap_list:
			
		trap_type = self.find_trap_type(each_trap.get('alarm_name'))
                key_for_mat_data = (each_trap.get('alarm_name'),each_trap.get('severity'))
                key_for_static_inventory_data = "static_"+str(each_trap.get('ip_address'))

                static_inventory_data = redis_conn.get(key_for_static_inventory_data)
		if not static_inventory_data:
		    logger.error('Static inventory data not found for ip %s'%str(each_trap.get('ip_address')))
		    continue
                static_inventory_data = eval(static_inventory_data)

                mat_data = redis_conn.get('mat_data')
		if not mat_data:
                    logger.error('Mat data not found')
                    continue
                mat_data = eval(mat_data)
                mat_data = mat_data.get(key_for_mat_data)
		if not mat_data:
		    looger.error('Mat data not found for alarm %s'%str(each_trap.get('alarm_name')))
                    continue
		
		circuit_dict_data_for_ip = circuit_dict_data.get(each_trap.get('ip_address'))

                alarm = dict()
                alarm['alarm_name'] = each_trap.get('alarm_name')
                alarm['severity'] = each_trap.get('severity')
                alarm['alarm_description'] = mat_data.get('description')
                alarm['timestamp'] = each_trap.get('timestamp')
                alarm['unique_id'] = generateuuid()
                alarm['ip_address'] = each_trap.get('ip_address')
                alarm['inventory_id']= static_inventory_data.get('id')
                alarm['category'] = mat_data.get('category')
                alarm['alias'] = ' '.join(each_trap.get('alarm_name').split('_'))

                device_type = static_inventory_data.get('resource_name')

		circuit_list = []
		idu_odu_trap = {}
		circuit_trap = {}
                # create trap for BS device
                if device_type == "BS":

		    if trap_type == "ip_trap":
			# In case redis does not contain circuit ids for the odu - trap will not go
                        if circuit_dict_data_for_ip:
                            for each_sector in circuit_dict_data_for_ip.keys():
                                for each_circuit in circuit_dict_data_for_ip.get(each_sector):
                                    circuit_list.append(each_circuit)
			else:
			    logger.info("Circuit dict data not Found for i p: %s"%str(each_trap.get('ip_address')))
                            circuit_list = []

                    else:
			# In case redis does not contain circuit ids for the odu - trap will not go 
			if circuit_dict_data_for_ip.get(trap_type):
                            for each_circuit in circuit_dict_data_for_ip.get(trap_type):
                                circuit_list.append(each_circuit)
			else:
			    logger.info("Circuit dict data not Found for trap type: %s"%str(trap_type))
			    circuit_list = []

		    params_for_make_idu_odu_trap = {}
                    params_for_make_idu_odu_trap['mat_data'] = mat_data
                    params_for_make_idu_odu_trap['static_inventory_data'] = static_inventory_data
                    params_for_make_idu_odu_trap['alarm'] = alarm
		    params_for_make_idu_odu_trap['no_of_circuits'] = len(circuit_list)
		    
		    idu_odu_trap = self.make_idu_odu_trap(**params_for_make_idu_odu_trap)
		    idu_odu_traps.append(idu_odu_trap)
			
		    
                    params_for_make_circuit_trap = {}
                    params_for_make_circuit_trap['idu_odu_trap'] = idu_odu_trap
                    params_for_make_circuit_trap['circuit_list'] = circuit_list
		    circuit_trap = self.make_circuit_trap(**params_for_make_circuit_trap)

                    circuit_traps.append(circuit_trap)
		    

	for each_idu_odu_trap in idu_odu_traps:
	    final_traps.append(each_idu_odu_trap)
	for each_circuit_trap in circuit_traps:
	    final_traps.append(each_circuit_trap)

	return final_traps

    def create_alarms_for_events(self,**params):
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
	ckt_list_for_conv_sia=params.get( 'ckt_list_for_conv_sia')
	trap_list = [] 
	rc_alarm_id = None
        ss_trap = {}
        bs_trap = {}
        rc_element_dict={}
	del_ss = []
	non_rc_element_dict = dict()
	# Fault in either PTP-BH device or switch/converter.
	if is_backhaul or rc_element:
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
			ckt_list_for_conv_sia,del_ss = self.extract_ckt_for_sia(backhaul_id, down_device_dict, static_dict, ss_list, del_ss)
		    elif bool(sitea_ac & siteb_ac) :
		        ckt_list_for_conv_sia =[]
		

	    rc_element_dict,rc_alarm_id = self.make_dict_for_conv_swich_trap(**params)
	    logger.info ('RC Element Dict %s'%str(rc_element_dict))
	    if not alarm_id:
	        params.update({'alarm_id': rc_alarm_id })
	    # If siteb PTP-BH device is down(is_bakchaul=True) then Use PTP BH device as parent device for SiteB idu/odu. 
	    if is_backhaul:
		parent_ac = down_device_dict.get(backhaul_id).get('category')
	    # Else Siteb switch/converter will be parent of siteb idu/odu.
	    else:
	        parent_ac = down_device_dict.get(rc_element).get('category')
	    params.update({'parent_ac':parent_ac})

	    # Make down IDU/ODU traps for the affected switch/converter 
	    bs_trap  = self.make_dict_for_idu_odu_trap(**params)

	    # Filter out the ptp devices where alarm category matches with parent device.
	    # TODO handle ptp for which category desn't match
	    filtered_ptp= []
	    for ptp_device in ptp_list:
		ac = down_device_dict[ptp_device].get('category')
		if bool(ac & parent_ac):
		   filtered_ptp.append(ptp_device)


	    # Make SS traps(idu/odu ss+ ptp trap).
	    # ss_list: list of ss/ptp device where Either parent device is Ok or category doesn't match for ss and parent.
	    ss_list = list(set(ss_list)-set(ptp_list)-set(del_ss))  # Remove PTP devices for which parent category match.
	    params.update({'ss_list':ss_list})
	    ss_trap = self.make_dict_for_ss_trap(**params)

	    # Temporary trap dict for ptp device
	    params.update({'ss_list': ptp_list})
	    ss_ptp_trap = self.make_dict_for_ss_trap(**params)
	    for key in ss_ptp_trap.keys():
		if key in filtered_ptp:    
		    ss_ptp_trap[key]['parent_alrm_id'] = params.get('alarm_id')

	    #ckt dict for idu odu and ptp ckt dict
	    input_trap_dict = {}
	    if bs_trap:
	    	input_trap_dict.update(bs_trap)
	    """
	    if ss_ptp_trap:
	    	input_trap_dict.update(ss_ptp_trap)
	    """
	    # Adding Converter/Swtich trap Info to create Consolidated Circuit Trap.
	    if rc_element_dict:
	    	input_trap_dict.update(rc_element_dict)	

	    params.update({'idu_odu_trap_dict': input_trap_dict})
	    params.update({'ckt_list_for_conv_sia': ckt_list_for_conv_sia})
	    ckt_element_list = self.make_dict_for_ckt(**params)

	    # Non Root Cause Switch Converter Traps
	    params.update({'is_backhaul':None, 'alarm_id':None})
	    #TODO Send the SIA traps for the NOn rc conv traps
	    if non_rc_switch_conv:
		for switch_conv in non_rc_switch_conv:
		    params.update({'rc_element': switch_conv})
		    trap_dict, alarm = self.make_dict_for_conv_swich_trap(**params)
		    if trap_dict:
		        non_rc_element_dict.update(trap_dict)

	    trap_list = rc_element_dict.values() + non_rc_element_dict.values() + bs_trap.values()+ \
								 ss_trap.values() + ss_ptp_trap.values() + ckt_element_list

	elif params.get('bs_list'):
	    params.update({'parent_ac':None})
	    bs_trap = self.make_dict_for_idu_odu_trap(**params)

	    ss_trap = self.make_dict_for_ss_trap(**params)
	    
	    params.update({'idu_odu_trap_dict':bs_trap, 'parent_ac':set([])})
	    ckt_element_list = self.make_dict_for_ckt(**params)
		
	    trap_list = bs_trap.values() + ss_trap.values() + ckt_element_list
	elif params.get('ss_list'):
	    ss_trap = self.make_dict_for_ss_trap(**params)
	    trap_list = ss_trap.values()
	return rc_alarm_id,trap_list

    def find_high_priority_alarm(self,alarm_dict):
	"""
	Alarm filteration for each fault device based on priority given in mat table.
	"""
	alarm_tuples = alarm_dict.keys()
	priority_values = [self.alarm_priority_dict.get(alarm) for alarm in alarm_tuples]
	# Alarm indexing list.
	index_priority = deepcopy(priority_values)
	# Sorting pirority value.
	#priority_values.sort(reverse=True)
	priority_values.sort()
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
		    if clear_alarm:
		        clear_alarm = clear_alarm[0]
		     
		    if clear_alarm and clear_alarm not in alarm_tuples:
			return alarm
		    else:
			cur_timestamp = alarm_dict[alarm]['timestamp']
			clear_timestamp = alarm_dict[clear_alarm]['timestamp']
			if clear_timestamp > cur_timestamp:
			    alarm_dict.pop(alarm)
			    self.high_priority(alarm_dict)
			else:
			    return alarm
	    except Exception as e:
		logger.error('Error in Filtering Traps/events based on priority \n Exception : {0}'.format(e))
	else:
	    return None

    def planned_events(self,redis_conn):
        planned_event_dict ={} 
	planned_events_data = redis_conn.get('planned_events')
	if planned_events_data:
	    planned_events_data = eval(planned_events_data)
	    planned_events_data = sorted(planned_events_data,key=itemgetter(0)) 
	for entry in planned_events_data:
	    if len(entry) == 3:
	        planned_event_dict[(entry[0],entry[1])] = (entry[2],)
	    elif len(entry) == 5:
		planned_event_dict[(entry[0],entry[1])] = (entry[2],entry[3],entry[4])
	
	#time_duration_list = planned_event_dict.keys() if planned_event_dict else list()
	return planned_event_dict
    def update_trap_invent_dict(self):
	"""
	Get the data(traps) from redis.
	Filter it based on inventory id and store it accordingly.
	Create a tuple (alarm_name,severity) from alarm data and store/update in alarm inventory, tuple as a key and value alarm data.
	
	Structure:
	trap_invent_dict:{
		invent_id1:{'
			timestamp':342234323,
			'ip_address1':{ 
				'ip_trap':{
					(alarm_name,severity):alarm_data,
					(alarm_name,severity):alarm_data
				},
				'odu1':{
					(alarm_name,severity):alarm_data,
					(alarm_name,severity):alarm_data
				}
				'odu2':{
					(alarm_name,severity):alarm_data,
					(alarm_name,severity):alarm_data
				}
			}
		}
	}

	Traps are being stored in redis queue named 'queue:traps'
	'queue:traps' = [(alarm_data1),(alarm_data2),.....,(alarm_datan)]

	Traps structure will be like
	('', 'ODU1_Lost', '', '10.191.134.13', '', '', 'critical', '', '2016-09-17 10:21:05', '')

	Mapping between IP address and inventory id.
	ip_id={ip_address: inventory_id}

	for e.g. ip_id = {'10.175.44.9': 45,
			  '121.89.44.2': 2}
	"""
	redis_conn = self.redis_conn()

	clear_trap_keys = []

	# Get recent Trap_Invent_dict from redis.
	try:	
	    trap_invent_dict = eval(redis_conn.get('trap_invent_dict'))
	except Exception as e:
	    trap_invent_dict = {}
	    redis_conn.set('trap_invent_dict',{})
	    logger.error('\n\nEarlier trap invent dict- New Created\n')
	
	ip_id = eval(redis_conn.get('ip_id'))
	mat_data = eval(redis_conn.get('mat_data'))

	# Get all the traps from redis queue
	number_of_traps = redis_conn.llen('queue:traps')
	
	time_duration_dict = self.planned_events(redis_conn)
	if number_of_traps > 0:

	    p = redis_conn.pipeline()
	    [p.lpop('queue:traps') for i in range(number_of_traps)]        # Alarm data(traps and events) from redis
	    traps_list = p.execute()
	    traps_list = [eval(t_e) for t_e in traps_list]

	    #logger.error('Fetched Traps list (before filter) %s'%(traps_list))
	    traps_list = self.filter_planned_events(traps_list)
	    #logger.error('Fetched Traps list (after filter) %s'%(traps_list))

	    # Store traps to trap_invent_dict according to its structure show above.
	    for each_trap in traps_list:

	        ip = each_trap[3]
		drop_trap_flag = 0
                alarm_name = each_trap[1]
                severity = each_trap[6]
                key = (alarm_name,severity)
                id = ip_id.get(ip)
		trap_type = self.find_trap_type(alarm_name)

	        #if mat_data.get(key).get('correlation') == 1:
	        if True:

		    if severity == 'clear':
		        clear_trap_key = str(ip)+'_'+str(alarm_name)
		        clear_trap_keys.append(clear_trap_key)
     
		    alarm = dict()   
		    alarm['alarm_name'] = each_trap[1]
	  	    alarm['alarm_description'] = each_trap[2]
		    alarm['timestamp'] = int(datetime.strptime(each_trap[8],"%Y-%m-%d %H:%M:%S").strftime('%s'))
		    alarm['severity'] = each_trap[6]
		    alarm['unique_id'] = generateuuid()
		    alarm['ip_address'] = ip
		    alarm['inventory_id']= id
		    alarm['category'] = mat_data.get(key).get('category')
		    # Alarm name alias for monolith
		    alarm['alias'] = ' '.join(each_trap[1].split('_'))
		    
		    if id is not None:
		        if id in trap_invent_dict:
			    if ip in trap_invent_dict[id]:
			        if trap_type in trap_invent_dict[id][ip]:
				    trap_invent_dict[id][ip][trap_type][key] = alarm
			        else:
				    trap_invent_dict[id][ip][trap_type] = {} 
				    trap_invent_dict[id][ip][trap_type][key] = alarm
			    else:
			        trap_invent_dict[id][ip] = {}
			        trap_invent_dict[id][ip][trap_type] = {}
			        trap_invent_dict[id][ip][trap_type][key] = alarm
		        else:
			    timestamp = each_trap[8]
			    trap_invent_dict[id] = {}
			    trap_invent_dict[id]['timestamp'] = alarm['timestamp']
			    trap_invent_dict[id][ip] = {}
			    trap_invent_dict[id][ip][trap_type] = {}
			    trap_invent_dict[id][ip][trap_type][key] = alarm


	    inventory_dict = {'trap_invent_dict':trap_invent_dict}
            self.insert_events_into_redis(inventory_dict)

	    # Clear Trap Send Task
	    clear_trap_keys = list(set(clear_trap_keys))
	    # Call Clear Trap Task if Clear Trap Keys exsist.
	    if clear_trap_keys:
	        clear_alarms.s(clear_trap_keys).apply_async()

	    return True
	else:
	    return False
    
    def update_testing_db(self, alarms_list, is_manual = False):

	query_data_for_testing_db = []
	sia_trap_data_list = []

	for alarm in alarms_list:
	    sia_trap_data = {}
            tp = alarm.get("trap_type")
            if tp == "circuit_ids_trap":
                sia_trap_data['parent_alrm_id'] = alarm.get('parent_alrm_id')
                sia_trap_data['impacted_circuit_ids'] = alarm.get('impacted_circuit_ids')
                sia_trap_data_list.append(sia_trap_data)

        for alarm in alarms_list:
	    tp = alarm.get("trap_type")
	    if tp == "circuit_ids_trap":
		sia_trap_data_list.append(sia_trap_data)
		continue	

	    testing_db_data = {}
            testing_db_data['ip_address']=alarm.get('resource_name')
            testing_db_data['alarm_id'] = alarm.get('alrm_id')
            testing_db_data['alarm_name'] = '_'.join(alarm.get('alrm_name').split(' '))
            testing_db_data['severity'] = alarm.get('severity')
            testing_db_data['alarm_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(alarm.get('time_stamp')))
	    testing_db_data['parent_alarm_id'] = alarm.get('parent_alrm_id')
            testing_db_data['is_manual'] = is_manual
	    testing_db_data['alarm_type'] = alarm.get('resource_type')
	    testing_db_data['circuit_ids_in_sia'] = ""
	    for sia_data in sia_trap_data_list:
		if alarm.get('alrm_id') == sia_data.get('parent_alrm_id'):
		    testing_db_data['circuit_ids_in_sia'] = sia_data.get('impacted_circuit_ids')
 
	    """
	    tp = alarm.get("trap_type")
            if tp == "ptp_or_ss_trap":
                testing_db_data['alarm_type'] = "SS & PTP"
            if tp == "converter_or_ptpbh_trap":
                testing_db_data['alarm_type'] = "Converter & PTP-BH"
            if tp =="idu_or_odu_trap":
                testing_db_data['alarm_type'] = "IDU & ODU"
	    if tp =="circuit_ids_trap":
                testing_db_data['alarm_type'] = "SIA"
	    """
	    query_data_for_testing_db.append(testing_db_data)

	#for each_query_data in query_data_for_testing_db:
	logger.error(query_data_for_testing_db)

	query_testing_db = 'insert into testing_db (ip_address, alarm_name, alarm_time, is_manual, alarm_id, severity, alarm_type, circuit_ids_in_sia, parent_alarm_id) \
				values(%(ip_address)s, %(alarm_name)s, %(alarm_time)s, %(is_manual)s, %(alarm_id)s, %(severity)s, %(alarm_type)s, %(circuit_ids_in_sia)s, %(parent_alarm_id)s)'
	
        export_traps = ExportTraps()
        if query_data_for_testing_db:
            try:
		export_traps.exec_qry(query_testing_db , query_data_for_testing_db, db_name='snmptt_db')
            except Exception as exc:
		logger.error(exc)

   
    def update_alarms_in_database(self, non_ckt_trap_list, is_manual = False):

        # Store Correlated Trap information to User Applicatin Database.
        query_data_for_alert_center = []

	if is_manual:
	    for trap_dict in non_ckt_trap_list:
		trap_dict['is_manual'] = is_manual

	redis_conn = self.redis_conn()
	p = redis_conn.pipeline()
        # Using Redis Hash to store Traps.
        # hset('dictname',key,value)
        [p.hset('correlated_traps', str(trap_dict.get('resource_name')+'_'+'_'.join(trap_dict['alrm_name'].split(' '))),
                                                         trap_dict) for trap_dict in non_ckt_trap_list]
        p.execute()

	all_monolith_tickets = redis_conn.keys('monolith_ticket:*')

        for trap in non_ckt_trap_list:
	
	    ip_address = trap.get('resource_name')
            eventname =  re.sub('[: ]', '_', trap.get('alrm_name'))
            alarm_id = trap.get('alrm_id')

            if 'monolith_ticket:' + ip_address in all_monolith_tickets :

                monolith_ticket = eval(redis_conn.get('monolith_ticket:' + ip_address))
                monolith_ticket[eventname] = { 'alarm_id' : alarm_id , 'is_manual' : is_manual, 'ticket_number' : 'Not Available' }
            else :

                monolith_ticket = {eventname : { 'alarm_id' : alarm_id , 'is_manual' : is_manual, 'ticket_number' : 'Not Available' } }

	    redis_conn.set('monolith_ticket:' + ip_address, monolith_ticket)

            data_alert_center = {}
            data_alert_center['ip_address']=trap.get('resource_name')
            data_alert_center['alarm_id'] = trap.get('alrm_id')
            data_alert_center['ticket_number'] = 'Not Available'
            data_alert_center['eventname'] = '_'.join(trap.get('alrm_name').split(' '))
            data_alert_center['traptime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(trap.get('time_stamp')))
	    data_alert_center['is_manual'] = is_manual
            query_data_for_alert_center.append(data_alert_center)


	query_current_alarm  =  'UPDATE alert_center_currentalarms SET alarm_id = %(alarm_id)s, ticket_number = %(ticket_number)s, is_manual = %(is_manual)s \
                                where ip_address = %(ip_address)s and eventname = %(eventname)s'
        query_history_alarm  =  'UPDATE alert_center_historyalarms SET alarm_id = %(alarm_id)s, ticket_number = %(ticket_number)s, is_manual = %(is_manual)s \
                                where ip_address = %(ip_address)s and eventname = %(eventname)s and traptime = %(traptime)s'

        export_traps = ExportTraps()

        if query_data_for_alert_center:
            try:
                # Store the Ticket and other information on User application database.
                export_traps.exec_qry(query_current_alarm , query_data_for_alert_center, db_name='snmptt_db')
                export_traps.exec_qry(query_history_alarm , query_data_for_alert_center, db_name='snmptt_db')

            except Exception as exc:
                inserted = False
                logger.error('Exc in mysql trap insert in alert center: {0}'.format(exc))

    def find_trap_type(self, trap_name):

	events = ('Device_not_reachable', 'PD_threshold_breach_major')
	ip_traps = ('gpsNotSynchronised','wimax_interfaces_down__synchronization_lost', 'Synchronization_problem__no_PPS')

	if trap_name in events:
	    trap_type = 'event'
	elif trap_name in ip_traps:
            trap_type = 'ip_trap'
	elif 'odu1' in trap_name.lower():
	    trap_type = 'odu1'
	elif 'odu2' in trap_name.lower():
	    trap_type = 'odu2'
	else:
	    trap_type = "do_not_monitor"
	
	return trap_type

    def filter_traps_from_sent_traps(self, traps_list):

	# Filter device trap list by checking in correlated traps
	redis_conn = self.redis_conn()
	traps_to_be_removed = []
	for trap in traps_list:
	    drop_flag = False

	    trap_ip = trap.get('ip_address')
            trap_name = trap.get('alarm_name')
	
	    trap_type = self.find_trap_type(trap_name)
	    sent_traps = redis_conn.get('monolith_ticket:%s' % (trap_ip))
	    if not sent_traps:
		logger.error('Sent traps not found for ip %s'%str(trap_ip))
                continue

	    sent_traps = eval(sent_traps)
	    sent_trap_names = sent_traps.keys()
 
	    odu1_r = re.compile("ODU1")
	    odu2_r = re.compile("ODU2")

	    odu1_sent_traps = filter(odu1_r.match, sent_trap_names)
	    odu2_sent_traps = filter(odu2_r.match, sent_trap_names)
	    events = list( filter((lambda st_name: st_name in ( "Device_not_reachable", "PD_threshold_breach_major"), sent_trap_names)))	
	    ip_traps = list( filter((lambda st_name: st_name in( "gpsNotSynchronised", \
								 "wimax_interfaces_down__synchronization_lost", \
								 "Synchronization_problem__no_PPS" \
								), sent_trap_names)))

	    if trap_name in sent_trap_names:
		drop_flag = True
	    elif trap_type == 'odu1' and ( odu1_sent_traps or ip_traps ):
                drop_flag = True
            elif trap_type == 'odu2' and ( odu2_sent_traps or ip_traps ):
                drop_flag = True
	    else:
		pass
		
	    if drop_flag == True:
		logger.info("for this ip %s trap will not go"%str(trap_ip))
		traps_to_be_removed.append(trap)

	for trap in traps_to_be_removed:
            traps_list.remove(trap)
	return traps_list

    def fetch_connected_circuits(self, ip, sector_type = "None"):

	circuits_list = []
        redis_conn = self.redis_conn()

        try:
	    circuit_dict_data = redis_conn.get('circuit_dict')
            if not circuit_dict_data:
            	logger.error('Circuit dict data is not available in redis')
                return circuits_list

	    circuit_dict_data = eval(circuit_dict_data)

            static_data = redis_conn.get("static_%s"%(ip))
	    if not static_data:
		logger.error('Static data not found for ip %s'%(ip))
		return circuits_list

	    static_data = eval(static_data)

	    device_type = static_data.get('resource_name')

	    if device_type == "BS":

		circuit_dict = circuit_dict_data.get(ip)
		if not circuit_dict:
		    logger.error("Circuits list not found for ip: %s"%(ip))
		    return circuits_list

        	if sector_type == 'odu1':
            	    for circuit in circuit_dict.get('odu1'):
                    	circuits_list.append(circuit)
        	elif sector_type == 'odu2':
            	    for circuit in circuit_dict.get('odu2'):
                    	circuits_list.append(circuit)
        	else:
            	    for circuit in circuit_dict.values():
                	circuits_list = circuits_list + circuit

	    elif device_type == "POPConverter" or device_type == "BTSConverter":

                bs_ips = static_data.get('bs_ips')

                for each_bs_ip in bs_ips:

		    circuits_list_for_bs_ip = fetch_connected_circuits(each_bs_ip)
		    circuits_list = circuits_list + circuits_list_for_bs_ip

	    elif device_type == "SS":

		circuit_id = static_data.get('circuit_id')
		circuits_list.append(circuit_id)

        except Exception as e:
            logger.error('Exception in fetching connected circuits : %s'%(e))

	return circuits_list


    def converter_customer_count(self, ip):
        redis_conn = self.redis_conn()
	try:

	    converter_static_data = eval(redis_conn.get("static_%s"%(ip)))
            bs_ips = converter_static_data.get('bs_ips')
	
	    circuit_dict_data = redis_conn.get('circuit_dict')
            if not circuit_dict_data:
                logger.error('Circuit dict data is not available in redis')
                return "0"

	    circuit_dict_data = eval(circuit_dict_data)
            circuits_list = []

            for each_bs in bs_ips:

	        circuit_dict = circuit_dict_data.get(each_bs)
	        if not circuit_dict:
		    #logger.error("Circuits list not found for bs ip: %s"%(each_bs))
		    ptp_static_data = eval(redis_conn.get("static_%s"%(each_bs)))
		    circuit_ids = ptp_static_data.get('circuit_id')
		    if not circuit_ids:
			continue
		    circuits_list = circuit_ids.split(',')

		else:
                    for circuit in circuit_dict.values():
                        circuits_list = circuits_list + circuit

	except Exception as e:
	    logger.error('Exception in finding Converter customer count: %s'%(e))

	if len(circuits_list):
	    return len(circuits_list)
	else:
	    logger.error('Circuit dict data is not for converter ip %s'%(ip))
	    return "0"

    def bs_customer_count(self, ip, trap_type):
        redis_conn = self.redis_conn()
	
        circuit_dict_data = redis_conn.get('circuit_dict')
	if not circuit_dict_data:
	    logger.error('Customer_count: Circuit dict data is not available in redis')
	    return "0"

        circuit_dict_data = eval(circuit_dict_data).get(ip)
	if not circuit_dict_data:
	    logger.error('Customer_count: Circuit Dict data not found for ip %s'%(ip))
	    return "0"

        circuits_list = []
	if trap_type in ["odu1","odu2"]:
	    for circuit in circuit_dict_data.get(trap_type):
                circuits_list.append(circuit)
	else:
            for circuit in circuit_dict_data.values():
                circuits_list = circuits_list + circuit

        return len(circuits_list)
	    
@app.task(base=DatabaseTask, name='correlation_traps')
def correlation_traps():  
    """
    Comments
    """
    cor_obj = correlation()
    redis_conn =  cor_obj.redis_conn()

    current_time = datetime.now().strftime('%s')
    trap_invent_dict = redis_conn.get('trap_invent_dict')
    trap_invent_dict = eval(trap_invent_dict)
    
    # Filtering inventory hierarchy  
    # TODO: change back time to 600
    invent_ids = filter(lambda x:int(current_time) - int(trap_invent_dict[x]['timestamp']) >1200  and 
		 int(current_time) - int(trap_invent_dict[x]['timestamp']) <= 80000 , trap_invent_dict.keys())

    map(lambda x: trap_invent_dict.pop(x),filter(lambda x: x not in invent_ids,trap_invent_dict.keys()))
    map(lambda x: trap_invent_dict[x].pop('timestamp', None), trap_invent_dict.keys())		
    
    # Task to update invent_dict:- remove invent id for which correlation is in process.
    update_invent_dict.s(invent_ids).apply_async()
  
    for id in invent_ids:

	traps_list = []
	alarm_invent_dict = trap_invent_dict.get(id)
	# For each ip filter its trap based on MAT priority.
	for ip in alarm_invent_dict.keys():
	    ip_sector_alarms = {}

	    # Filter traps based on high priority ( Single trap for each trap type )
	    for trap_type in alarm_invent_dict.get(ip).keys():
		final_alarm = {}
		alarm_dict = alarm_invent_dict[ip][trap_type]	
	        alarm = cor_obj.find_high_priority_alarm(alarm_dict)
		if alarm:
		    alarm_info_dict = alarm_dict.get(alarm)
		    final_alarm['ip_address'] = alarm_info_dict.get('ip_address')
		    final_alarm['alarm_name'] = alarm_info_dict.get('alarm_name')
		    final_alarm['severity'] = alarm_info_dict.get('severity')
		    final_alarm['timestamp'] = alarm_info_dict.get('timestamp')
		    ip_sector_alarms[trap_type] = final_alarm
		    
	    if 'ip_trap' in ip_sector_alarms.keys():
	        traps_list.append(ip_sector_alarms.get('ip_trap'))
	    else:
  	        [traps_list.append(odu_alarm) for odu_alarm in ip_sector_alarms.values()]

        # Sending final list of traps to create and send alarms to monolith
        if traps_list:
            send_alarms_for_traps.s(traps_list).apply_async()
	
    
@app.task(name='clear_alarms')
def clear_alarms(keys):
    """
    Task to send Clear traps to Monolith.
    Extract traps from redis modify trap and send it to monolith.
    """
    cor_obj = correlation()
    redis_conn = cor_obj.redis_conn()

    p = redis_conn.pipeline()
    [p.hget('correlated_traps',key) for key in keys]
    clear_alarms = p.execute()
    clear_alarms = map(lambda alarm: eval(alarm),filter(lambda alarm: alarm !=None, clear_alarms))
    
    # Remove traps from correlated_traps
    [p.hdel('correlated_traps',key) for key in keys]
    p.execute()

    # Send clear alarms to monolith
    map(lambda alarm: alarm.update({'severity':ALARM_FLAGS.get('clear')}) ,clear_alarms)

    if clear_alarms:

	remove_clear_alarms =[]
	for alarm in clear_alarms:
	    if alarm.get('is_manual'):
		remove_clear_alarms.append(alarm)
	for alarm in remove_clear_alarms:
	    clear_alarms.remove(alarm)

	cor_obj.update_testing_db(clear_alarms)

        trap_sender_task.s(clear_alarms).apply_async()

@app.task(base=DatabaseTask, name='correlation_update_inventory')
def correlation_update_inventory():
    """
    Starting point of this script, It calls individual functions for correlation of events and traps
    """
    cor_obj=correlation()
     
    if cor_obj.update_event_invent_dict():

        correlation_events.apply_async()	
   
    if cor_obj.update_trap_invent_dict():

        correlation_traps.apply_async()
    
@app.task(base=DatabaseTask, name='correlation_events')
def correlation_events():  
    """
    Comments

    """
    cor_obj = correlation()
    redis_conn =  cor_obj.redis_conn()

    current_time = datetime.now().strftime('%s')  
    
    # Extract alarm data Inventory of all devices present in Redis
    event_invent_dict = redis_conn.get('event_invent_dict')
    event_invent_dict = eval(event_invent_dict)
	
    # Filtering inventory hierarchy  
    invent_ids = filter(lambda x:int(current_time) - int(event_invent_dict[x]['timestamp']) >1200  and 
		 int(current_time) - int(event_invent_dict[x]['timestamp']) <= 80000 , event_invent_dict.keys())

    map(lambda x:  event_invent_dict.pop(x),filter(lambda x: x not in invent_ids,event_invent_dict.keys()))
    map(lambda x: event_invent_dict[x].pop('timestamp', None), event_invent_dict.keys())		
  
    # Task to update invent_dict:- remove invent id for which correlation is in process.
    update_invent_dict.s(invent_ids,events=1).apply_async()  

    for id in invent_ids:

	down_device = []
	invent_down_device_dict = {}

	alarm_invent_dict = event_invent_dict.get(id)

	# For each ip filter its trap/event based on MAT priority.
	remove_ip = []
	for ip in alarm_invent_dict.keys():
	    alarm_dict = alarm_invent_dict[ip]
	    alarm = cor_obj.find_high_priority_alarm(alarm_dict)
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
	if del_ss:
	    for del_ss_key in del_ss:
		del invent_down_device_dict[del_ss_key]
	    
        params = max_value_params,invent_ids
        send_alarms_for_events.s(params).apply_async()

@app.task(base=DatabaseTask, name='send_alarms_for_events')
def send_alarms_for_events(params):
    """ 
	This function sends alarms created from events.
	Create traps for down device.
        Args:
           params(list)        : trap_list, mat_entries, invent_id_list.
           invent_id_list(list): List of inventory id for which Correlation required.
    """
    trap_params,invent_id_list = params
    cor_obj = correlation()
    final_trap_list = []
    final_traps = []
    params = {}
    siteb_params = {}
    sitea_trap_list = []
    siteb_trap_list = []
    down_device_dict, down_device_static_dict, rc_element, non_rc_switch_conv,\
				    bs_down_list, ss_down_list, ckt_dict, flags = trap_params

    ptp_bh_flag = flags['ptp_bh_flag']
    bs_ss_dict = flags['bs_ss_dict']
    is_backhaul =flags['is_backhaul']
    backhaul_id =flags['backhaul_id']
    ckt_list_for_conv_sia = flags['ckt_list_for_conv_sia'] # Circuit list for converter sia when converter in Site a is down
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


    siteb_bs_down_list = filter(lambda x: down_device_static_dict[x].get('ptp_bh_flag'),bs_down_list)
    siteb_ss_down_list = filter(lambda x: down_device_static_dict[x].get('ptp_bh_flag'),ss_down_list)

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
			'ckt_list_for_conv_sia' : ckt_list_for_conv_sia,
			'alarm_id': None,})

    siteb_params.update({'rc_element':None,
			 'bs_list': siteb_bs_down_list,
			 'ss_list': siteb_ss_down_list,
			 'ptp_list': siteb_ptp_down_list,
			 'ckt_dict': ckt_dict,
			 'bs_ss_dict': bs_ss_dict,
			 'siteb_switch_conv_id':None,
			 'sitea_rc_element':None,
			 'ckt_list_for_conv_sia' : ckt_list_for_conv_sia,
			 'alarm_id': None})
  
    if rc_element:
	if not down_device_static_dict[rc_element].get('ptp_bh_flag'):
	    sitea_params.update({'rc_element':rc_element})
	sitea_params.update({'is_backhaul':None})
	rc_alarm_id,sitea_trap_list = cor_obj.create_alarms_for_events(**sitea_params)
    
	if ptp_bh_flag:
	    siteb_params.update({'is_backhaul':is_backhaul,
				 'sitea_rc_element':sitea_params.get('rc_element')})

	    # Update alarm id with parent alarm id where connected PTP-BH is down.
	    if is_backhaul:
		siteb_params.update({'alarm_id':rc_alarm_id})
	    # Where Highest level element is SiteB switch/converter.
	    # Update rc element and key for Siteb switch/converter
	    if down_device_static_dict[rc_element].get('ptp_bh_flag'):
		siteb_params.update({'rc_element':rc_element,
				     'siteb_switch_conv_id':rc_element})
	    #else:
	    #	siteb_params.update({'rc_element':conv_switch_siteb})
	    rc_alarm_id,siteb_trap_list = cor_obj.create_alarms_for_events(**siteb_params)
    else:
	if ptp_bh_flag:
	    alarm_id,siteb_trap_list = cor_obj.create_alarms_for_events(**siteb_params)
	sitea_params.update({'is_backhaul':None})
	alarm_id,sitea_trap_list= cor_obj.create_alarms_for_events(**sitea_params)
    
    final_traps = sitea_trap_list + siteb_trap_list
    if final_traps:

	# External Handling of data manupulation for Monolith server.
	final_trap_list = cor_obj.final_trap_data_manupulation(final_traps)
        trap_sender_task.s(final_trap_list).apply_async()
   	cor_obj.update_testing_db(final_trap_list) 
        non_ckt_trap_list = [trap_dict for trap_dict in final_trap_list if not trap_dict.get('impacted_circuit_ids')]

	cor_obj.update_alarms_in_database(non_ckt_trap_list)	
    else:
	logger.error('Final traps are none')

@app.task(base=DatabaseTask, name='send_alarms_for_traps')
def send_alarms_for_traps(traps_list, is_manual = False):
    
    """
    Comments
    """
    cor_obj=correlation()
    redis_conn = cor_obj.redis_conn()


    final_traps_list = cor_obj.filter_traps_from_sent_traps(traps_list)


    final_alarms = []
    if final_traps_list:
        final_alarms = cor_obj.create_alarms_for_traps(final_traps_list)
    
    if final_alarms:
        # External Handling of data manupulation for Monolith server.
        final_alarm_list = cor_obj.final_trap_data_manupulation(final_alarms)
        trap_sender_task.s(final_alarm_list).apply_async()
	cor_obj.update_testing_db(final_alarm_list, is_manual)
        non_ckt_trap_list = [trap_dict for trap_dict in final_alarm_list if not trap_dict.get('impacted_circuit_ids')]
        p = redis_conn.pipeline()
        # Using Redis Hash to store Traps.
        # hset('dictname',key,value)
        [p.hset('correlated_traps', str(trap_dict.get('resource_name')+'_'+'_'.join(trap_dict['alrm_name'].split(' '))),
                                                         trap_dict) for trap_dict in non_ckt_trap_list]
        p.execute()

	cor_obj.update_alarms_in_database(non_ckt_trap_list, is_manual)

@app.task(name='trap_sender_task')
def trap_sender_task(traps):
    """Task to send correlated traps to Monolith"""
    circuit_traps = filter(lambda x: x.get('impacted_circuit_ids'),traps)
    non_ckt_trap_list = [trap_dict for trap_dict in traps if not trap_dict.get('impacted_circuit_ids')]
    for trap in non_ckt_trap_list:
	t = Trap(**trap)
	t.send_trap()
    sleep(20) 
    for trap in circuit_traps:
	t = Trap(**trap)
	t.send_trap()

@app.task(base=DatabaseTask, name='update_invent_dict')
def update_invent_dict(invent_ids,events = 0):
    """
    Remove inventory id's for which correlation has started.
    """

    #events flag to identify event_invent_dict and trap_invent_dict.
    if events:
	invent_type = "event_invent_dict"
    else:
	invent_type = "trap_invent_dict"
    try:
	#invent_ids = invent_ids.split(',')
	cor_obj = correlation()
	redis_conn = cor_obj.redis_conn()
	invent_dict = redis_conn.get(invent_type)
	invent_dict = eval(invent_dict)
	map(lambda x: invent_dict.pop(x),filter(lambda y: y in invent_dict.keys(), invent_ids))
	redis_conn.set(invent_type,invent_dict)
    except Exception as e:
	logger.error('Exception : {0}'.format(e))

class manual_ticketing:

    def __init__(self):
        pass
    def create_events(self, corr_obj,event):
        """
	Comments
	"""
	redis_conn = corr_obj.redis_conn()

	device_ip = event.get('ip_address')
	alarm_name = event.get('alarm_name')
	severity = event.get('severity')
	timestamp = event.get('timestamp')
	key_for_static_inventory_data = "static_" + str(device_ip)
	static_inventory_data = redis_conn.get(key_for_static_inventory_data)
	static_inventory_data = eval(static_inventory_data)

	key_for_mat_data = (alarm_name,severity)
	mat_data = redis_conn.get('mat_data')
	mat_data = eval(mat_data)
	mat_data = mat_data.get(key_for_mat_data)

        alarm = dict()
        alarm['alarm_name'] = alarm_name
        #alarm['alarm_description'] = each_event[2]
        alarm['timestamp'] = timestamp
        alarm['severity'] = severity
        alarm['unique_id'] = generateuuid()
        alarm['ip_address'] = device_ip
        #alarm['inventory_id']= id
        alarm['category'] = mat_data.get('category')
        #Alarm name alias for monolith
        alarm['alias'] = ' '.join(alarm_name.split('_'))	
	
	down_device_dict = {}
	static_dict = {}
	down_device_dict[device_ip] = alarm
	static_dict[device_ip] = static_inventory_data

	device_type = static_inventory_data.get('resource_name')

	# create trap for idu 
	circuit_dict_data = {}
	circuit_dict_data = redis_conn.get("circuit_dict")
        circuit_dict_data = eval(circuit_dict_data)

	final_events = []
	circuit_list = []
	circuit_dict ={}
	if device_type == "BS":

	    circuit_dict_data_for_ip = circuit_dict_data.get(device_ip)
	    if circuit_dict_data_for_ip:
	        for each_sector in circuit_dict_data_for_ip.keys():
		    for each_circuit in circuit_dict_data_for_ip.get(each_sector):
		        circuit_list.append(each_circuit)
	        circuit_dict[device_ip] = circuit_list 

	    params_io = {}
	    params_io['down_device_dict'] = down_device_dict
            params_io['static_dict'] = static_dict
            params_io['bs_list'] = [device_ip]

	    idu_odu_event_dict = corr_obj.make_dict_for_idu_odu_trap(**params_io)
	    final_events.append(idu_odu_event_dict.get(device_ip))

	    params_ct = {}
	    params_ct['static_dict'] = static_dict
            params_ct['idu_odu_trap_dict'] = idu_odu_event_dict
            params_ct['ckt_list_for_conv_sia'] = []
            params_ct['ckt_dict'] = circuit_dict

            circuit_event = corr_obj.make_dict_for_ckt(**params_ct)
	    final_events.append(circuit_event[0])

	elif device_type == "POPConverter" or device_type == "BTSConverter":

	    logger.error('Manual ticketing - it is a converter')
	    bs_ips = static_inventory_data.get('bs_ips')
	    circuit_list = []
	    if bs_ips:
		logger.error("BS IPs in manual_ticketing %s"%(bs_ips))
	        for each_bs_ip in bs_ips:
		    circuit_dict_data_for_bs_ip = circuit_dict_data.get(each_bs_ip)
		    logger.error("Circuit dict data in manual_ticketing %s"%(circuit_dict_data_for_bs_ip))
            	    if circuit_dict_data_for_bs_ip:
                        for each_sector in circuit_dict_data_for_bs_ip.keys():
			    if each_sector:
                                for each_circuit in circuit_dict_data_for_bs_ip.get(each_sector):
                                    circuit_list.append(each_circuit)

	    #print circuit_list		
            params_cs = {}
            params_cs['down_device_dict'] = down_device_dict
            params_cs['static_dict'] = static_dict
            params_cs['rc_element'] = device_ip

	    converter_events = corr_obj.make_dict_for_conv_swich_trap(**params_cs)
	    final_events.append(converter_events[0].get(device_ip))

	    params_ct = {}
            params_ct['static_dict'] = static_dict
            params_ct['idu_odu_trap_dict'] = converter_events[0]
            params_ct['ckt_list_for_conv_sia'] = circuit_list
            params_ct['ckt_dict'] = {}
	    
            circuit_event = corr_obj.make_dict_for_ckt(**params_ct)
	    final_events.append(circuit_event[0])

	elif device_type == "SS":

	    params_ss = {}
	    params_ss['down_device_dict'] = down_device_dict
            params_ss['static_dict'] = static_dict
            params_ss['ss_list'] = [device_ip]

	    ss_events = corr_obj.make_dict_for_ss_trap(**params_ss)

	    final_events.append(ss_events.get(device_ip))
	pprint(final_events)
        return final_events

    def send_events(self, corr_obj, event, is_manual):
	
	"""
	Comments
	"""	

	final_events = self.create_events(corr_obj,event)

	if final_events:
            # External Handling of data manupulation for Monolith server.
            final_events= corr_obj.final_trap_data_manupulation(final_events)
            trap_sender_task.s(final_events).apply_async()
	    corr_obj.update_testing_db(final_events, is_manual)
            non_ckt_events = filter(lambda x: not x.get('impacted_circuit_ids'),final_events)
	    is_manual = True
	    corr_obj.update_alarms_in_database(non_ckt_events, is_manual)


@app.task(base=DatabaseTask, name='manual_ticketing_main')
def manual_ticketing_main(alarm):

    try:
        corr_obj = correlation()
	alarm['timestamp'] = int(datetime.strptime(alarm.get('traptime'),"%Y-%m-%d %H:%M:%S").strftime('%s'))

	manual_tkt_obj = manual_ticketing()
	if alarm:
	    alarm_type = corr_obj.find_trap_type(alarm.get('alarm_name'))
	    if alarm_type == 'event':
		manual_tkt_obj.send_events(corr_obj, alarm, is_manual = True)
	    elif alarm_type in ('odu1','odu2','ip_trap'):
		traps = [alarm]
		send_alarms_for_traps.s(traps, is_manual = True).apply_async() 
	    else:
		logger.error('Alarm name is in not to be monitored')
    except Exception as e:
	logger.error("Exception in manual ticketing process: %s"%(e))
