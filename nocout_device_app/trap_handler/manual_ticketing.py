from pprint import pprint
import correlation
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
from correlation import correlation
import web
import re
try:
    urls = ("/.*", "manual_ticketing")
    app = web.application(urls, globals())
except Exception, e:
    pass

def generateuuid():
        return str(uuid4())

class manual_ticketing:

    def __init__(self):
        pass
		
    def redis_conn(self):
        """Connection to redis database."""
        rds_cli = RedisInterface(custom_conf={'db': 5})
	redis_conn =  rds_cli.redis_cnx
        return redis_conn
 
    def create_events(self, event):
        """
	Comments
	"""
	corr_obj = correlation() 
	redis_conn = self.redis_conn()

	device_ip = events.get('ip_address')
	alarm_name = events.get('alarm_name')
	severity = events.get('severity')

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

	if device_type == "BS":

	    params_io = {}
	    params_io['down_device_dict'] = down_device_dict
            params_io['static_dict'] = static_dict
            params_io['bs_list'] = [device_ip]

	    idu_odu_events = corr_obj.make_dict_for_idu_odu_trap(**params_io)
	    
	    params_ct = {}
	    params_ct['static_dict'] = static_dict
            params_ct['idu_odu_trap_dict'] = idu_odu_events
            params_ct['ckt_list_for_conv_sia'] = []
            params_ct['circuit_dict'] = []

            circuit_events = corr_obj.make_dict_for_circuit_trap(**params_ct)
	    
	    final_events = idu_odu_events + circuit_events

	elif device_type == "POPConverter" or device_type == "BTSConverter":

	    params_cs = {}
	    param_cs['down_device_dict'] = down_device_dict
            param_cs['static_dict'] = static_dict
            param_cs['rc_element'] = ip

	    converter_events = corr_obj.make_dict_for_conv_swich_trap(**params_cs)


	    params_ct = {}
            params_ct['static_dict'] = static_dict
            params_ct['idu_odu_trap_dict'] = idu_odu_events
            params_ct['ckt_list_for_conv_sia'] = []
            params_ct['circuit_dict'] = []
	    
            circuit_events = self.make_dict_for_circuit_traps(**params_ct)

	    final_events = converter_events + circuit_events

	elif device_type == "SS":

	    param_ss = {}
	    param_ss['down_device_dict'] = down_device_dict
            param_ss['static_dict'] = static_dict
            param_ss['ss_list'] = ss_list

	    ss_events = corr_obj.make_dict_for_ss_trap(**params_ss)

	    final_events = ss_events

        return final_events

    def send_events(self, event):
	
	"""
	Comments
	"""	
	corr_obj = correlation()
	redis_conn = self.redis_conn()

	final_events = corr_obj.create_events(event)

	if final_events:
            # External Handling of data manupulation for Monolith server.
            final_events= corr_obj.final_trap_data_manupulation(final_events)
            #logger.error('Manupulated Events list {0}'.format(final_events))
            correlation_s3.trap_sender_task.s(final_events).apply_async()

            non_ckt_events = filter(lambda x: not x.get('impacted_circuit_ids'),final_events)
	    is_manual = True
	    corr_obj.update_alarms_in_database(non_ckt_events, is_manual)

    def POST(self):
	"""
	This function handle POST request is this class
	"""

	return True

    def manual_ticketing_main(self, alarm):
	
	cor_obj = correlation()

	is_manual = True

	if alarm:
	    alarm_type = cor_obj.find_trap_type(alarm.get('alarm_name'))
	    if alarm_type == 'event':
		self.send_events(alarm)
	    else:
		traps = [alarm]
		correlation_s3.send_alarms_for_traps.s(traps, is_manual).apply_async() 
	     
if __name__ == '__main__':
    man_tic_obj = manual_ticketing()
    alarm = {'ip_address':'10.191.34.2', 'alarm_name': 'ODU1_Lost', 'severity': 'critical', 'is_manual':True, 'timestamp':1479275507 }
    man_tic_obj.manual_ticketing_main(alarm)
