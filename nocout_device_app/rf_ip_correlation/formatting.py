#!/usr/bin/python

from start.start import app
from handlers.db_ops import *
logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error
from collections import defaultdict
import imp
from itertools import izip_longest
import json
ih_count = 5000
ip_id = {}
class inventory(object):
    global ip_id
    def __init__(self):
	pass

    def dicts(self,t):
	try:
	    if not len(t):
		return t
	    return dict((k, self.dicts(t[k])) for k in t)
	except TypeError:
	    return t

    def tree(self):
       return defaultdict(self.tree)

    def insert_data_in_redis(self,mapping):
	items = []
	key = 'inventory_hiearachy'
	rds_obj = RedisInterface(custom_conf={'db': 5}) 
	rds_cnx = rds_obj.redis_cnx	
	p = rds_cnx.pipeline(transaction=True)
	#for pair in mapping.iteritems():
	#	items.extend(pair)
	mapping = self.dicts(mapping) 
	try: 
	    [rds_cnx.set(pair[0],pair[1] ) for pair in mapping.iteritems()]  
	except Exception as e:
	    print e
	    
	try:
	    p.execute()
	except Exception,e:
	    print e
	    print 'Error in inserting inventory data'

    def create_inventory_data(self,resultset=None,ptp_farend_ip_list=None):
	"""
	This function is called by mysql_test.py file.
	"""
	ptp_bh_dict = dict()
	inventory_id_list = list()
	params = {}
	filtered_far_end_resultset = list()
	far_end_resultset,device_inventory = self.prepare_raw_result(resultset,ptp_farend_ip_list,ptp_bh_dict=ptp_bh_dict)
	for bs in far_end_resultset:
	    inventory_id = None
	    try: 
		if bs.get('BSswitchParentIP') and bs.get('BSswitchParentIP') != 'NA':
		    ip = bs.get('BSswitchParentIP','')
		    resource_ip = bs.get('BSswitchIP')
		elif bs.get('BTSconverterParentIP'):
		    ip = bs.get('BTSconverterParentIP','')
		    resource_ip = bs.get('BTSconverterIP')
		static_ip = 'static_'+ip
		if static_ip in device_inventory['ss_data_dict']:
		    inventory_id = device_inventory['ss_data_dict'][static_ip].get('inventory_id','')
		    device_inventory['ss_data_dict'][static_ip]['child_switch'] = resource_ip
		    if device_inventory.get('ptp_bh_dict'):
			ptp_near_end_ip = device_inventory.get('ptp_bh_dict').get(ip)
			if ptp_near_end_ip:
			    static_ip = 'static_' + str(ptp_near_end_ip)
			    device_inventory['bs_data_dict'][static_ip]['child_switch']=resource_ip
		    if inventory_id:
			inventory_id_list.append(inventory_id)
			filtered_far_end_resultset.append(bs)
	    except Exception,e:
		pass
	#ptpbh_parent_child_dict = dict([(v,k) for k,v in device_inventory['ptpbh_parent_child_dict'].iteritems()])
	is_active = 1
	ptp_farend_ip_list=None
	params['ptp_farend_ip_list'] = ptp_farend_ip_list
	params['inventory_id_list'] = inventory_id_list
	params['is_active'] = is_active
	params['ptp_bh_dict'] = device_inventory['ptp_bh_dict']
	far_end_resultset,far_end_inventory = self.prepare_raw_result(resultset=filtered_far_end_resultset,**params)
	
	for inventory_id in far_end_inventory['obj_dict'].keys():
	    device_inventory['obj_dict'][inventory_id].update(far_end_inventory['obj_dict'][inventory_id])
	device_inventory['ss_data_dict'].update(far_end_inventory['ss_data_dict'])
	device_inventory['bs_data_dict'].update(far_end_inventory['bs_data_dict'])
	device_inventory['conv_switch_data_dict'].update(far_end_inventory['conv_switch_data_dict'])
	device_inventory['ih_dynamic'].update(far_end_inventory['ih_dynamic'])
	
	ip_invent_mapping = {'ip_id':ip_id}
	self.insert_data_in_redis(device_inventory['obj_dict'])
	self.insert_data_in_redis(device_inventory['ss_data_dict'])
	self.insert_data_in_redis(device_inventory['bs_data_dict'])
	self.insert_data_in_redis(device_inventory['conv_switch_data_dict'])
	self.insert_data_in_redis(device_inventory['ih_dynamic'])
	self.insert_data_in_redis(ip_invent_mapping)
    def prepare_raw_result(self,resultset=None, ptp_farend_ip_list=None,inventory_id_list=None,is_active=0,ptp_bh_dict=None):
	# list will carry bs resultset for PTP_BH type hierarchy.
	far_end_resultset = list()
	total_inventory = dict() 
	obj_count = 0
	obj_dict = self.tree()
	bs_data_dict = self.tree() 
	ss_data_dict = self.tree()
	ptp_parent_child_dict = {}
	conv_switch_data_dict = self.tree()
	global ih_count
	ih_dynamic =defaultdict(dict)
	for bs in resultset:
	    inventory_hierarchy = self.tree()
	    sector_info_str = bs.get('SECT_STR', '')
	    if is_active == 0:
		if bs.get('BSswitchParentIP') in ptp_farend_ip_list:
		    far_end_resultset.append(bs)
		    continue
		elif bs.get('BTSconverterParentIP') in ptp_farend_ip_list:
		    far_end_resultset.append(bs)
		    continue
	    if is_active == 1:
		index = resultset.index(bs)
		inventory_id = inventory_id_list[index]
		obj_count = inventory_id
		    
	    if bs.get('POPconverterIP') and bs.get('POPconverterIP') != 'NA':
		inventory_hierarchy[bs.get('POPconverterIP')] = ih_count
		ih_dynamic[ih_count]
		ih_dynamic[ih_count]['inventory_id'] = obj_count
		ih_dynamic[ih_count]['ip_address'] = bs.get('POPconverterIP')
		ih_count = ih_count +1
		resource_name = 'POPConverter'
		conv_switch_data_dict=self.create_conv_switch_data_dict(bs,conv_switch_data_dict,obj_count,
									resource_name,is_active,ptp_bh_dict)
		    
	    if bs.get('BTSconverterIP') and bs.get('BTSconverterIP') != 'NA':
		inventory_hierarchy[bs.get('BTSconverterIP')]=ih_count
		ih_dynamic[ih_count]
		ih_dynamic[ih_count]['inventory_id'] = obj_count
		ih_dynamic[ih_count]['ip_address'] = bs.get('BTSconverterIP')
		ih_count = ih_count +1
		resource_name = 'BTSConverter'
		conv_switch_data_dict=self.create_conv_switch_data_dict(bs,conv_switch_data_dict,obj_count,
									resource_name,is_active,ptp_bh_dict)
	    
	    if bs.get('BSswitchIP') and bs.get('BSswitchIP') != 'NA':
		inventory_hierarchy[bs.get('BSswitchIP')]=ih_count
		ih_dynamic[ih_count]
		ih_dynamic[ih_count]['inventory_id'] = obj_count
		ih_dynamic[ih_count]['ip_address'] = bs.get('BSswitchIP')
		ih_count = ih_count +1
		resource_name = 'BSSwitch'
		conv_switch_data_dict=self.create_conv_switch_data_dict(bs,conv_switch_data_dict,obj_count,
									resource_name,is_active,ptp_bh_dict)

	    params = self.create_ss_dict(bs,ss_data_dict,obj_count,inventory_hierarchy,ih_dynamic,ptp_farend_ip_list,ptp_bh_dict,is_active)
	    ss_data_dict,inventory_hierarchy,ih_dynamic,ptp_parent_child_dict,ptp_bh_dict =  params

	    bs_data_dict,inventory_hierarchy,ih_dynamic = self.create_sect_dict(bs,bs_data_dict,obj_count,inventory_hierarchy,ih_dynamic,
									   ptp_parent_child_dict,ptp_bh_dict,is_active)
	    if inventory_hierarchy and is_active == 0:
		inventory_hierarchy['id'] = obj_count
		obj_dict[obj_count] = inventory_hierarchy
		obj_count = obj_count + 1
	    elif inventory_hierarchy and is_active == 1:
		obj_dict[obj_count] = inventory_hierarchy

	total_inventory['obj_dict'] = obj_dict
	total_inventory['ss_data_dict'] = ss_data_dict
	total_inventory['bs_data_dict'] = bs_data_dict
	total_inventory['conv_switch_data_dict'] = conv_switch_data_dict
	total_inventory['ih_dynamic'] = ih_dynamic
	total_inventory['ptp_bh_dict'] = ptp_bh_dict
	return far_end_resultset,total_inventory


    def create_conv_switch_data_dict(self,bs,data_dict,obj_count,resource_name,is_active,
			               ptp_bh_dict):
	"""
	Function to create static data dictionary for Converter/Switch, Key for this will be 
	'static_'+ converter/switch ip
	Dictionary data will be stored in Redis database(In memory database).
	"""
	static_data_bs = dict()
	aggr_switch = bs.get('AggregationSwitchIP','')
	pop_ip = bs.get('POPconverterIP','')
	bts_conv_ip = bs.get('BTSconverterIP','')
	pe_ip = bs.get('PE_IP')
	basestation_info_str = bs.get('BASESTATION', '')
	basestation_info = list(set(basestation_info_str.split('-|-|-')))
	bsswitch_ip_list = list(set(map(lambda x : x.split('|')[2],basestation_info)))
	try:
	    data = basestation_info[0].split('|')
	    bs_name = data[1]
	    region = data[-3]
	    city = data[-5]
	except:
	    bs_name = ''
	    region = ''
	    city = ''
	    pass
	if resource_name == 'POPConverter':  
	    ip = bs.get('POPconverterIP')   
	    parent_ip = bs.get('POPconverterParentIP')
	    parent_type = bs.get('POPconverterParentType')
	    parent_port = bs.get('POPconverterParentPort')
	    resource_type = 'Converter'
	    technology = bs.get('POPconverterTech')
	if resource_name == 'BTSConverter':
	    ip = bs.get('BTSconverterIP')
	    parent_ip = bs.get('BTSconverterParentIP')
	    parent_type = bs.get('BTSconverterParentType')
	    parent_port = bs.get('BTSconverterParentPort')
	    resource_type = 'Converter'
	    technology = bs.get('BTSconverterTech')
	if resource_name == 'BSSwitch':
	    ip = bs.get('BSswitchIP')
	    resource_type = 'Switch'
	    parent_ip = bs.get('BSswitchParentIP')
	    parent_type = bs.get('BSswitchParentType')
	    parent_port = bs.get('BSswitchParentPort')
	    technology = bs.get('BSswitchTech')

	ip_id[ip] = obj_count
	key = 'static_' + ip
	if is_active == 1:
	    data_dict[key]['ptp_bh_flag'] = 1
	    data_dict[key]['pop_ip'] = ptp_bh_dict.get(parent_ip)
	    data_dict[key]['bts_conv_ip'] = parent_ip
	else:
	    data_dict[key]['bts_conv_ip'] = bts_conv_ip 
	    data_dict[key]['pop_ip'] = pop_ip

	data_dict[key]['aggr_switch'] = aggr_switch
	data_dict[key]['pe_ip'] = pe_ip

	if 'NA' in bsswitch_ip_list:
	    bsswitch_ip_list.remove('NA')
	if bsswitch_ip_list:
	    data_dict[key]['bs_switch_ip'] = bsswitch_ip_list[0]
	else:
	    data_dict[key]['bs_switch_ip'] = None 
	
	data_dict[key]['bs_name'] = bs_name
	data_dict[key]['region'] = region
	data_dict[key]['city'] = city
	data_dict[key]['inventory_id'] = obj_count
	data_dict[key]['resource_type'] = resource_type
	data_dict[key]['resource_name'] = resource_name
	data_dict[key]['technology'] = technology 
	data_dict[key]['parent_ip'] = parent_ip
	data_dict[key]['parent_type'] = parent_type 
	data_dict[key]['parent_port'] = parent_port 
    
	return data_dict




    def create_sect_dict(self,bs,data_dict,obj_count,inventory_hierarchy,ih_dynamic,ptp_parent_child_dict,ptp_bh_dict,is_active):
	    """
	    Function to create static data dictionary for base station devices.
	    Key for this will be 'static_'+ base_station_device_ip
	    Dictionary data will be stored in Redis database(In memory database).
	    """
	    global ih_count
	    if bs.get('SECT_STR'):
		sector_info_str = bs.get('SECT_STR', '')
		ss_info_str = bs.get('SubStation', '')
		basestation_info_str = bs.get('BASESTATION','')
		sector_info = sector_info_str.split('-|-|-')
		ss_info = ss_info_str.split('-|-|-')
		basestation_info = basestation_info_str.split('-|-|-')
		bs_ip_list = list(set(map(lambda x : x.split('|')[5],sector_info)))
		bsswitch_ip_list = list(set(map(lambda x : x.split('|')[2],basestation_info)))
		bs_station = bs.get('BASESTATION')
		aggr_switch = bs.get('AggregationSwitchIP')
		pe_ip = bs.get('PE_IP')
		try:
		   region = bs_station.split('|')[-3]
		   bs_name = bs_station.split('|')[1]
		   city = bs_station.split('|')[-5]
		except:
		   region = ''
		   bs_name = ''
		   city = ''
		   pass
	       
		for b_ip in bs_ip_list:
		   if b_ip != 'NA': 
		       inventory_hierarchy[b_ip]= ih_count
		       ih_dynamic[ih_count]['inventory_id'] = obj_count
		       ih_dynamic[ih_count]['ip_address'] = b_ip
		       ih_count = ih_count + 1
     
		for sec_list in sector_info:
		   try:
		      bs_ip = sec_list.split('|')[5]
		   except Exception,e:
		      print e
		      continue
		   # Adding code for Static information of the /IDU/ODU
		   try:
		       bs_parent_ip = sec_list.split('|')[8]
		   except:
		       bs_parent_ip = ''
		       pass
		   try:
		       bs_parent_type = sec_list.split('|')[12]
		       if bs_parent_type == 'NA' or bs_parent_type is None:
			   bs_parent_type = '' 
		   except:
		       bs_parent_type = ''
		       pass
		   try:
		       bs_parent_port = sec_list.split('|')[13]
		       if bs_parent_port == 'NA' or bs_parent_port is None:
			   bs_parent_port = '' 
		   except:
		       bs_parent_port = ''
		       pass
			
	           ip_id[bs_ip] = obj_count
		   bs_key = 'static_' + bs_ip
		   data_dict[bs_key]['bs_name'] = bs_name 
		   data_dict[bs_key]['region'] = region
		   data_dict[bs_key]['city'] = city
		   data_dict[bs_key]['aggr_switch'] = aggr_switch
		   data_dict[bs_key]['pe_ip'] = pe_ip
		   data_dict[bs_key]['inventory_id'] = obj_count
		   data_dict[bs_key]['parent_ip'] = bs_parent_ip
		   data_dict[bs_key]['parent_type'] = bs_parent_type
		   data_dict[bs_key]['parent_port'] = bs_parent_port
		   try:
		      tech = sec_list.split('|')[4]
		   except Exception,e:
		      print e
		      pass
		   if 'starmax' in tech.lower():
		       data_dict[bs_key]['technology'] = 'wimax'
		       data_dict[bs_key]['coverage'] = 'Telisma'
		       data_dict[bs_key]['resource_type'] = 'IDU'
		       data_dict[bs_key]['resource_name'] = 'BS'
		   if 'canopy' in tech.lower():
		       data_dict[bs_key]['technology'] = 'pmp'
		       data_dict[bs_key]['coverage'] = 'Cambium'
		       data_dict[bs_key]['resource_type'] = 'ODU'
		       data_dict[bs_key]['resource_name'] = 'BS'
		   if 'radwin5k' in tech.lower():
		       data_dict[bs_key]['technology'] = 'pmp'
		       data_dict[bs_key]['coverage'] = 'Radwin5K'
		       data_dict[bs_key]['resource_type'] = 'ODU'
		       data_dict[bs_key]['resource_name'] = 'BS'
		   if 'radwin2k' in tech.lower():
		       data_dict[bs_key]['technology'] = 'p2p'
		       data_dict[bs_key]['resource_type'] = 'PTP'
		       data_dict[bs_key]['resource_name'] = 'SS' 
		       data_dict[bs_key]['ptp_bh_type'] = 'ne'
		       data_dict[bs_key]['custormer_name'] = sec_list.split('|')[11]
		       data_dict[bs_key]['circuit_id'] = sec_list.split('|')[10] 
		       data_dict[bs_key]['ptp_ip'] = ptp_parent_child_dict.get(bs_ip)
		   if bs_ip in ptp_bh_dict.values():
		       data_dict[bs_key]['ptp_bh_flag'] = 1
		       data_dict[bs_key]['backhaul'] = 1
		   if is_active == 1:
		       data_dict[bs_key]['ptp_bh_flag'] = 1
		   try:
		       sector_id = sec_list.split('|')[1]
		       if sector_id == 'NA':
			   continue
		       data_dict[bs_key].setdefault('sector_id',set()).add(sector_id)
		   except Exception,e:
		       print e
		       continue
	    return data_dict,inventory_hierarchy,ih_dynamic 

    def create_ss_dict(self,bs,ss_data_dict,obj_count,inventory_hierarchy,ih_dynamic,ptp_farend_ip_list,ptp_bh_dict,is_active):
	"""
	Function to create static data dictionary for sub station devices.
	Key for this will be 'static_'+ sub_station_device_ip
	Dictionary data will be stored in Redis database(In memory database).
	"""
	global ih_count
	ptp_parent_child_dict = {}
	if not ptp_farend_ip_list:
	    ptp_farend_ip_list = list()
	ss_info_str = bs.get('SubStation', '')
	ss_info = ss_info_str.split('-|-|-')
	ss_ip_list = list(set(map(lambda x : x.split('|')[4],ss_info)))
	basestation_info_str = bs.get('BASESTATION','')
	basestation_info = list(set(basestation_info_str.split('-|-|-')))
	try:
	   region = basestation_info[0].split('|')[5]
	   bs_name = basestation_info[0].split('|')[1]
	   city = basestation_info[0].split('|')[3]
	except:
	   region = ''
	   bs_name = ''
	   city = ''
	   pass
	for s_ip in ss_ip_list: 
	   if s_ip != 'NA': 
	       inventory_hierarchy[s_ip]= ih_count
	       ih_dynamic[ih_count]
	       ih_dynamic[ih_count]['ip_address'] = s_ip
	       ih_dynamic[ih_count]['inventory_id']= obj_count
	       ih_count = ih_count + 1
	for ss_list in ss_info:
	    try:
		ss_ip = ss_list.split('|')[4]
		if ss_ip == 'NA':
		    continue
		ckt_id = ss_list.split('|')[6]
		customer_name = ss_list.split('|')[7]
		ss_tech = ss_list.split('|')[5]
		ss_parent_ip = ss_list.split('|')[10]
		ss_parent_type = ss_list.split('|')[11]
	    except Exception,e:
		print e
		continue
	    
	    ip_id[ss_ip] = obj_count
	    ss_key = 'static_' + ss_ip
	    ss_data_dict[ss_key]['circuit_id'] = ckt_id
	    ss_data_dict[ss_key]['customer_name'] = customer_name
	    ss_data_dict[ss_key]['city'] = city
	    ss_data_dict[ss_key]['bs_name'] = bs_name
	    ss_data_dict[ss_key]['region'] = region
	    ss_data_dict[ss_key]['inventory_id'] = obj_count
	    ss_data_dict[ss_key]['resource_name'] = 'SS'
	    ss_data_dict[ss_key]['parent_ip'] = ss_parent_ip
	    ss_data_dict[ss_key]['parent_type'] = ss_parent_type
	    if 'starmax' in ss_tech.lower():
		ss_data_dict[ss_key]['technology'] = 'wimax'
		ss_data_dict[ss_key]['resource_type'] = 'SS'
	    if 'canopy' in ss_tech.lower():
		ss_data_dict[ss_key]['technology'] = 'pmp'
		ss_data_dict[ss_key]['resource_type'] = 'SS'
	    if 'radwin5k' in ss_tech.lower():
		ss_data_dict[ss_key]['technology'] = 'pmp'
		ss_data_dict[ss_key]['resource_type'] = 'SS'
	    if 'radwin2k' in ss_tech.lower():
		ss_data_dict[ss_key]['technology'] = 'p2p'
		ss_data_dict[ss_key]['resource_type'] = 'PTP'
		ss_data_dict[ss_key]['ptp_bh_type'] = 'fe'
		ss_data_dict[ss_key]['ptp_ip'] = ss_parent_ip
		ptp_parent_child_dict[ss_parent_ip] = ss_ip
	    # Adding ptp_bh_flag flag to identify SiteB devices
	    if ss_ip in ptp_farend_ip_list:
		ss_data_dict[ss_key]['ptp_bh_flag'] = 1
		ss_data_dict[ss_key]['backhaul'] = 1
		ptp_bh_dict[ss_ip]= ss_parent_ip
	    if is_active == 1:
		ss_data_dict[ss_key]['ptp_bh_flag'] = 1
	return ss_data_dict,inventory_hierarchy,ih_dynamic,ptp_parent_child_dict,ptp_bh_dict

    def insert_mat_data_in_redis(self,resultset=None):
	"""
	This function create dictionary type data structure for master alarm table.
	for each unique key('rf_ip_'+alarm_name+'_'+severity) value contains the alarm information from mysql table of master_alarm_table.
	mat_data dictionary data structure is stored in Redis database.
	"""
	mat_data = dict()
	for alarm_info in resultset:
	    alarm_name = alarm_info.get('alarm_name','')
	    severity = alarm_info.get('severity','')
	    key = (alarm_name,severity)
	    mat_data[key] = dict()
	    mat_data[key]['alarm_name'] = alarm_info.get('alarm_name', '') 
	    mat_data[key]['oid'] = alarm_info.get('oid', '')
	    mat_data[key]['severity'] = alarm_info.get('severity', '')
	    mat_data[key]['device_type'] = alarm_info.get('device_type', '')
	    mat_data[key]['alarm_mode'] = alarm_info.get('alarm_mode', '')
	    mat_data[key]['alarm_type'] = alarm_info.get('alarm_type', '')
	    mat_data[key]['sia'] = alarm_info.get('sia', '')
	    mat_data[key]['auto_tt'] = alarm_info.get('auto_tt', '')
	    mat_data[key]['correlation'] = alarm_info.get('correlation', '')
	    mat_data[key]['to_monolith'] = alarm_info.get('to_monolith', '')
	    mat_data[key]['mail'] = alarm_info.get('mail', '')
	    mat_data[key]['sms'] = alarm_info.get('sms', '')
	    mat_data[key]['coverage'] = alarm_info.get('coverage' , '')
	    mat_data[key]['resource_name'] = alarm_info.get('resource_name', '')
	    mat_data[key]['resource_type'] = alarm_info.get('resource_type', '')
	    mat_data[key]['support_organization'] = alarm_info.get('support_organization', '')
	    mat_data[key]['bearer_organization'] = alarm_info.get('bearer_organization', '')
	    mat_data[key]['priority'] = alarm_info.get('priority', '')
	    # Type conversion str -> Set
	    mat_data[key]['category'] = eval(alarm_info.get('alarm_category', 'set([])'))
	    mat_data[key]['refer'] = alarm_info.get('refer', '')
	# TODO: mat is stored temporary on 6 for testing
	rds_obj = RedisInterface(custom_conf={'db': 6}) 
	redis_conn = rds_obj.redis_cnx	
	redis_conn.set('mat_data',mat_data)



