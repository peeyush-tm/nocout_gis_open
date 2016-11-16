"""
nocout_live.py
==============

Script to handle on-demand live polling for a particular service data source
"""

from wato import *
from nocout_logger import nocout_log
from pprint import pformat
import subprocess
#import time
import re
from ast import literal_eval
from nocout import get_parent
import mysql.connector
import memcache,imp
logger = nocout_log()

def get_site_name(site=None):
    site = defaults.omd_site

    return site

db_ops_module = imp.load_source('db_ops', '/omd/sites/%s/lib/python/handlers/db_ops.py' % get_site_name())
#db_ops_module = imp.load_source('db_ops', '/omd/sites/ospf2_slave_1/lib/python/handlers/db_ops.py' )


try:
	import nocout_settings
	from nocout_settings import _DATABASES, _LIVESTATUS
except Exception as exp:
	logger.info('Error:' + pformat(exp))


interface_services = [
		'cambium_ul_rssi',
		'cambium_ul_jitter',
		'cambium_reg_count',
		'cambium_ul_jitter',
		'cambium_rereg_count',
		'cambium_ss_connected_bs_ip_invent'
		]


def main():
    """
    Entry point for all the functions

    Returns:
        {
	 "success": 1,
	 "message": "Data fetched successfully",
	 "error_message": None,
	 "value": [] # The current values for the desired service data sources
	}
    """
    response = {
        "success": 1,
        "message": "Data fetched successfully",
        "error_message": None,
        "value": []
    }
    action = ''
    action = html.var('mode')
    if action == 'live':
        response['value'] = poll_device()
    else:
        response.update({
            "message": "No data",
            "error_message": "No action defined for this case"
        })

    html.write(pformat(response))


def poll_device():
    current_values = []
    logger.info('[Polling Iteration Start]')
    device = html.var('device')
    service = html.var('service')
    logger.info('device : %s and service : %s' % (device, service))
    # If in case no `ds` supplied in req obj, [''] would be supplied as default
    try:
        data_source_list = literal_eval(html.var('ds'))
    except Exception:
        data_source_list = ['']
        logger.error('No ds provided in request object', exc_info=True)
    if not data_source_list:
        data_source_list = ['']
    logger.debug('data_source_list : %s' % data_source_list)
    
    current_values = get_current_value(device, service, data_source_list)

    return current_values


def get_current_value_old(current_values, device=None, service=None, data_source_list=None):
    response = []
    # Teramatrix poller on which this device is being monitored
    site_name = get_site_name()
    cmd = '/opt/omd/sites/%s/bin/cmk -nvp --checks=%s %s' % (site_name, service, device)
    # Fork a subprocess
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    check_output, error = p.communicate()
    if check_output:
        reg_exp1 = re.compile(r'(?<=\()[^)]*(?=\)$)', re.MULTILINE)
        reg_exp2 = re.compile(r'^ *\S+', re.MULTILINE)
        # Parse perfdata for all services running on that device
        ds_current_states = re.findall(reg_exp1, check_output)
        logger.info('ds_current_states : %s' % ds_current_states)
        # Get all the service names, currently running
	current_services = map(lambda x: x.strip(), re.findall(reg_exp2, check_output)[:-1])
        logger.info('current_services : %s' % current_services)

        service_ds_pairs = zip(current_services, ds_current_states)
        desired_service_ds_pair = filter(lambda x: service in x[0], service_ds_pairs)
        logger.debug('desired_service_ds_pair : %s' % desired_service_ds_pair)
        if desired_service_ds_pair:
            ds_values = desired_service_ds_pair[0][1].split(' ')
            logger.info('ds_values : %s' % ds_values)
            for ds in data_source_list:
		# Parse the output to get current value for that data source
                desired_ds = filter(lambda x: ds in x.split('=')[0], ds_values)
                #logger.debug('desired_ds : %s' % desired_ds)
                current_values.extend(map(lambda x: x.split('=')[1].split(';')[0], desired_ds))
            #logger.info('current_values : %s' % current_values)
            #logger.info('[Polling Iteration End]')

    return current_values



def get_current_value(q,device=None, service_list=None, data_source_list=None, bs_name_ss_mac_mapping=None, ss_name_mac_mapping=None,is_first_call=0):
     #response = []
     # Teramatrix poller on which this device is being monitored
     site_name = get_site_name()
     wimax_ss_port_service = ['wimax_ss_speed_status','wimax_ss_autonegotiation_status','wimax_ss_duplex_status','wimax_ss_uptime',
				'wimax_dl_modulation_change_invent','wimax_ss_link_status']
     wimax_services = ['wimax_dl_rssi','wimax_ul_rssi','wimax_dl_cinr','wimax_ul_cinr','wimax_dl_intrf','wimax_ul_intrf',
        'wimax_modulation_dl_fec','wimax_modulation_ul_fec']
     cambium_services = ['cambium_ul_rssi', 'cambium_ul_jitter',
		     'cambium_reg_count', 'cambium_rereg_count']
     rad5k_services = ['rad5k_ul_rssi' ,'rad5k_dl_rssi','rad5k_ss_dl_utilization' ,'rad5k_ss_ul_utilization',
	'rad5k_dl_time_slot_alloted_invent','rad5k_ul_time_slot_alloted_invent','rad5k_dl_estmd_throughput_invent',
	'rad5k_ul_estmd_throughput_invent',
	'rad5k_ul_uas_invent','rad5k_dl_es_invent','rad5k_ul_ses_invent','rad5k_ul_bbe_invent','rad5k_ss_cell_radius_invent',
	'rad5k_ss_cmd_rx_pwr_invent','rad5k_ss_dl_modulation','rad5k_ss_data_vlan_invent','rad5k_ss_mir_ul','rad5k_ss_mir_dl','rad5k_ss2_ul_rssi','rad5k_ss2_dl_rssi']
     util_service_list = ['wimax_pmp1_dl_util_bgp','wimax_pmp1_ul_util_bgp','wimax_pmp2_dl_util_bgp','wimax_pmp2_ul_util_bgp',
	'radwin_dl_utilization','radwin_ul_utilization','cambium_dl_utilization','cambium_ul_utilization',
	'cambium_ss_dl_utilization','cambium_ss_ul_utilization','mrotek_dl_utilization','mrotek_ul_utilization','rici_dl_utilization',
	'rici_ul_utilization','cisco_switch_dl_utilization','cisco_switch_ul_utilization','juniper_switch_dl_utilization','juniper_switch_ul_utilization',
	'huawei_switch_dl_utilization', 'huawei_switch_ul_utilization']

     wimax_ss_util_services = ['wimax_ss_ul_utilization','wimax_ss_dl_utilization']
     wimax_ss_params_services=['wimax_qos_invent','wimax_ss_session_uptime']
     switch_utilization = ['cisco_switch_dl_utilization','cisco_switch_ul_utilization','huawei_switch_dl_utilization', 'huawei_switch_ul_utilization']
     juniper_switch = ['juniper_switch_dl_utilization', 'juniper_switch_ul_utilization']
     huawei_switch = ['huawei_switch_dl_utilization', 'huawei_switch_ul_utilization']   
     ss_device, ss_mac, bs_device = None, None, None
     old_device = device
     #logger.debug('service_list: ' + pformat(service_list))
     filtered_ss_data = []
     ss_host_name = None
     # Pass our custom alarm handler function to signal
     #signal.signal(signal.SIGALRM, alarm_handler)
     # Set timeout to 1sec (excepts floats only)
     #signal.alarm(0.5)
     ss_mac_list, bs_device_list = [], []
     # Data sources for ping service
     pl, rta = None, None
     ip = None
     for service in service_list:
	     device = old_device
	     old_service = service
             if service in wimax_services:
			old_service = service
			service = 'wimax_topology'
	     if service in interface_services:
                     old_service = service
	             service = 'cambium_topology_discover'
	     if service in wimax_ss_port_service:
		     old_service = service
		     service = 'wimax_ss_port_params'
	     if service in rad5k_services:
		     old_service = service
		     service = 'rad5k_topology_discover'
	     if service in wimax_ss_util_services or service in wimax_ss_params_services:
		     old_service = service
		     service = 'wimax_bs_ss_params'
	     # Getting result from compiled checks output
             cmd = '/omd/sites/%s/bin/cmk -nvp --checks=%s %s' % (str(site_name), service, device)
	     # For host check [ping service]
	     if service.lower() == 'ping':
		     # Get the device ip from device name
		     try:
		         ip = get_parent(host=device, db=False, get_ip=True)
		     except Exception, e:
		     	logger.info('Error in get_parent : ' + pformat(e))
		     cmd = 'ping -w 2 -c 1 %s' % ip
	     logger.info('cmd: ' + pformat(cmd))
	     #start = datetime.datetime.now()
             # Fork a subprocess
             p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	     check_output, error = p.communicate()
	     logger.debug(' Check_output: ' + pformat(check_output))
             if check_output:
		if old_service in interface_services:
			data_value = []
			try:
				check_output = filter(lambda t: 'cambium_topology_discover' in t, check_output.split('\n'))
				check_output = check_output[0].split('- ')[1].split(' ')
				for ss_mac_entry in bs_name_ss_mac_mapping.get(device):
					filtered_ss_output = filter(lambda t:  ss_mac_entry.lower() in t, check_output)
					filtered_ss_data.extend(filtered_ss_output)
				logger.info('filtered_ss_data: ' + pformat(filtered_ss_data))
				index = cambium_services.index(old_service)
				for entry in filtered_ss_data:
					data_value = entry.split('/')[index+2]
					cal_ss_mac = entry.split('/')[1]
					for host_name,mac_value in ss_name_mac_mapping.items():
						if mac_value ==  cal_ss_mac.lower():
							ss_host_name = host_name
							break
					data_dict = {ss_host_name:data_value}
					q.put(data_dict)
			except Exception, e:
			 	logger.error('Empty check_output: ' + pformat(e))
				for host_name,mac_value in ss_name_mac_mapping.items():
					ss_host_name = host_name
					data_dict = {ss_host_name: []}
			 	        q.put(data_dict)
			 	        return
		elif str(old_service) in wimax_services:
			filtered_ss_data =[]
			try:
				data_value = []	
				check_output = filter(lambda t: 'wimax_topology' in t, check_output.split('\n'))
				check_output = check_output[0].split('- ')[1].split(' ')
				#logger.debug('Final check_output : ' + pformat(check_output))
				for ss_mac_entry in bs_name_ss_mac_mapping.get(device):
					filtered_ss_output = filter(lambda t:  ss_mac_entry.lower() in t,check_output)
					filtered_ss_data.extend(filtered_ss_output)
				index = wimax_services.index(old_service)
				#logger.debug('filterred_ss_data: ' + pformat(filtered_ss_data))
				for entry in filtered_ss_data:
					value = entry.split('=')[1].split(',')[index]
					data_value.append(value)
					cal_ss_mac = entry.split('=')[0]
					# MARK
					for host_name,mac_value in ss_name_mac_mapping.items():
						if mac_value ==  cal_ss_mac.lower():
							ss_host_name = host_name
							break
					data_dict = {ss_host_name:data_value}
					data_value = []
					q.put(data_dict)
			         			
			 	logger.error(filtered_ss_data)
			except Exception, e:
			 	logger.error('Empty check_output: ' + pformat(e))
				for host_name,mac_value in ss_name_mac_mapping.items():
					data_dict = {host_name:[]}
			 		q.put(data_dict)
			 	return
		elif str(old_service) in wimax_ss_util_services or str(old_service) in wimax_ss_params_services:
			filtered_ss_data =[]
			try:
				data_value = []	
				check_output = filter(lambda t: 'wimax_bs_ss_params' in t, check_output.split('\n'))
				check_output = check_output[0].split('- ')[1].split(' ')
				#logger.debug('Final check_output : ' + pformat(check_output))
				for ss_mac_entry in bs_name_ss_mac_mapping.get(device):
					filtered_ss_output = filter(lambda t:  ss_mac_entry.lower() in t,check_output)
					filtered_ss_data.extend(filtered_ss_output)
				if str(old_service) in wimax_ss_util_services:
					index = wimax_ss_util_services.index(old_service)
				elif str(old_service) in wimax_ss_params_services:
				    try:
				        index = wimax_ss_params_services.index(old_service)	
					if str(old_service) == 'wimax_qos_invent':
						ds = data_source_list[0]
						if 'dl' in ds:
							index = index + 3
					if str(old_service) == 'wimax_ss_session_uptime':
						index = index + 3
				    except:
					logger.error('ss_params: ' + pformat(index))
				logger.error('ss_params: ' + pformat(index))
				for entry in filtered_ss_data:
					value = entry.split('=')[1].split(',')[index]
					if str(old_service) not in wimax_ss_params_services:
						value = float(value)/1024.0
						value = "%.2f" % value
					data_value.append(value)
					cal_ss_mac = entry.split('=')[0]
					# MARK
					for host_name,mac_value in ss_name_mac_mapping.items():
						if mac_value ==  cal_ss_mac.lower():
							ss_host_name = host_name
							break
					data_dict = {ss_host_name:data_value}
					data_value = []
					q.put(data_dict)
			         			
			 	logger.error(filtered_ss_data)
			except Exception, e:
			 	logger.error('Empty check_output: ' + pformat(e))
				for host_name,mac_value in ss_name_mac_mapping.items():
					data_dict = {host_name:[]}
			 		q.put(data_dict)
			 	return
		elif str(old_service) in wimax_ss_port_service:
			try:
				data_value =  []
				check_output =  filter(lambda t: 'wimax_ss_port_params' in t, check_output.split('\n'))
				check_output = check_output[0].split('- ')[1].split(',')
				index =  wimax_ss_port_service.index(old_service)
				value = check_output[index].split('=')[1]
				value = value.strip('() ')
				data_value.append(value)
				data_dict = {old_device:data_value}
				data_value = []
				q.put(data_dict)
			except Exception,e:
				logger.error('Empty check_output: ' + pformat(e))
				data_dict = {old_device_name:[]}
				data_value = []
				q.put(data_dict)
				return	
		elif str(old_service) in rad5k_services:
			data_value = []
			try:
				check_output = filter(lambda t: 'rad5k_topology_discover' in t, check_output.split('\n'))
				check_output = check_output[0].split('- ')[1].split(' ')
				for ss_mac_entry in bs_name_ss_mac_mapping.get(device):
					filtered_ss_output = filter(lambda t:  ss_mac_entry.lower() in t, check_output)
					filtered_ss_data.extend(filtered_ss_output)
				logger.info('filtered_ss_data: ' + pformat(filtered_ss_data))
				index = rad5k_services.index(old_service)
				for entry in filtered_ss_data:
					data_entry = entry.split('=')[1]
					data_value = data_entry.split('/')[index]
					cal_ss_ip = data_entry.split('/')[-1]
					for host_name,ss_ip_value in ss_name_mac_mapping.items():
						if ss_ip_value ==  cal_ss_ip:
							ss_host_name = host_name
							break
					data_dict = {ss_host_name:data_value}
					q.put(data_dict)
			except Exception, e:
			 	logger.error('Empty check_output: ' + pformat(e))
				for host_name,mac_value in ss_name_mac_mapping.items():
					ss_host_name = host_name
					data_dict = {ss_host_name: []}
			 	        q.put(data_dict)
			 	        return
		elif old_service.lower() == 'ping':
			check_output = check_output.split('\n')[-3:]
			logger.debug('check_output after split: ' + pformat(check_output))
			pl_info, rta_info = check_output[0], check_output[1]
			if pl_info:
			        pl = pl_info.split(',')[-2].split()[0]
				pl = pl.strip('%')
			if rta_info:
			        rta = rta_info.split('=')[1].split('/')[1]
				rta = rta.strip('ms')
			if 'pl' in data_source_list:
				data_dict = {device: [pl]}
			if 'rta' in data_source_list:
				data_dict = {device: [rta]}
			q.put(data_dict)
			return
		elif service in util_service_list:
			reg_exp2 = re.compile(r'(?<=\[)[^]]*',re.MULTILINE)
                 	util_values = re.findall(reg_exp2, check_output)
                 	logger.info('current_states : %s %s' % (util_values,is_first_call))
			if util_values:
				if service == 'rici_dl_utilization' or service == 'rici_ul_utilization':
					cur_values = util_values[0].split(' ')
					this_time = cur_values[0].split('=')[1]	
					port1_value = int(cur_values[1].split('=')[1])	
					port2_value = int(cur_values[2].split('=')[1])	
					port3_value = int(cur_values[3].split('=')[1])	
					port4_value = int(cur_values[4].split('=')[1])
					this_value = max(port1_value,port2_value,port3_value,port4_value)	
                 			logger.info('values : %s' % (this_value))
				elif service in switch_utilization:
					try:
                 				logger.info('current_states : %s %s' % (util_values,is_first_call))
						ds = data_source_list[0]
						logger.info(ds)
						if 'GigabitEthernet0_0_' not in ds:
							ds = ds.lower()
						cur_values = util_values[0].rstrip().split(' ')
						this_time = cur_values[0].split('=')[1]	
						port_name = map(lambda x: x.split('=')[0] ,cur_values )
						port_value = map(lambda x: x.split('=')[1] ,cur_values )
						port_index = port_name.index(ds)
						if port_index:
							this_value = port_value[port_index]
						switch_key = "".join([old_device,"_",service,"_",ds])
                 				logger.info('port_value : %s %s' % (this_value,is_first_call))
					except Exception as e :
						pass  	

				elif service in juniper_switch:
					try:
                                                ds = data_source_list[0]
                                                ds = ds.lower()
                                                cur_values = util_values[0].rstrip().split(' ')
                                                this_time = cur_values[0].split('=')[1]
                                                port_name = map(lambda x: x.split('=')[0] ,cur_values )
                                                port_value = map(lambda x: x.split('=')[1] ,cur_values )
                                                port_index = port_name.index(ds)
                                                if port_index:
                                                        this_value = eval(port_value[port_index])
						key_value = "%.2f" % this_value
						data_dict = {old_device: key_value}
						logger.debug(data_dict)
                                                q.put(data_dict)
						continue
                                        except:
                                                pass

		
				else:
					this_time = util_values[0].split(' ')[0].split('=')[1]
					this_value = util_values[0].split(' ')[1].split('=')[1]
				if service in switch_utilization:
					key = switch_key
				else:
					key = "".join([old_device,"_",service])
				key =key.encode('ascii','ignore')
				memc_obj = db_ops_module.MemcacheInterface()
				memc = memc_obj.memc_conn
				key_value = ""
				if is_first_call:
					util_list = [this_time,this_value]
					if memc:
						memc.set(key,util_list)
						key_value = ""
					data_dict = {old_device: []}
				 	q.put(data_dict)
						
				else:
					try:
					    if memc:
						key =key.encode('ascii','ignore')
					        util = memc.get(key)
						logger.debug('util from memc: %s' % (util))
						if util:
							pre_time = util[0]
							pre_value = util[1]
							timediff =  int(this_time) - int(pre_time)
							valuediff =  float(this_value) - float(pre_value)
							if timediff <= 0 or valuediff <= 0:
								key_value = []
							else:
								rate = float(valuediff)/timediff
								rate = (rate * 8) / (1024.0 * 1024)
								key_value = "%.2f" % rate
						data_dict = {old_device: key_value}
				 		q.put(data_dict)
					except Exception,e:
                 				logger.info('Error' % e)
						data_dict = {old_device: key_value}
				 		q.put(data_dict)
			
			
		else:
			reg_exp1 = re.compile(r'(?<=\()[^)]*(?=\)$)', re.MULTILINE)
                 	# Parse perfdata for all services running on that device
                 	ds_current_states = re.findall(reg_exp1, check_output)
                 	logger.info('ds_current_states : %s' % ds_current_states)
                 	# Placing all the ds values into one single list
                 	if ds_current_states:
                        	ds_values = ds_current_states[0].split(' ')
                         	logger.info('ds_values : %s' % ds_values)
                         	for ds in data_source_list:
                                	 # Parse the output to get current value for that data source
                                 	desired_ds = filter(lambda x: ds in x.split('=')[0], ds_values)
                                 	logger.debug('desired_ds : %s' % desired_ds)
                                 	data_values = (map(lambda x: x.split('=')[1].split(';')[0], desired_ds))
				 	#logger.debug('data_values:' + pformat(data_values))
				 	data_dict = {old_device: data_values}
				 	q.put(data_dict)
				 	#q.task_done()
					# Foramt for multiple serivces
					# if data_values:
					#	 if device in host_data_dict.keys():
					#		 host_data_dict[device].update(
					#				 {
					#					 service: data_values
					#					 }
					#				 )
					#	 else:
					#		 host_data_dict.update(
					#				 {
					#					 device: {
					#						 service: data_values
					#						 }
					#					 }
					#				 )
					#	 #response.append(data_dict)
					#	 logger.debug('current_values: ' + pformat(q.qsize()))
		 	else:
				data_dict = {old_device: []}
			 	q.put(data_dict)
             #if error:
		     # Log the process error code
		     #logging.debug('Process exits with error code: ' + pformat(error))
     #q.put(host_data_dict)
     #return data_dict



def alarm_handler(signum, frame):
	raise Alarm


