"""
inventory_rrd_migration.py
=======================

This file contains the code for extracting and collecting the data for inventory services and storing this data into embeded mongodb database.

Inventory services are services for which data is coming in 1 day interval.

"""

from nocout_site_name import *
import socket,json
import time
import imp
import re
from collections import defaultdict
from itertools import groupby
from operator import itemgetter

from datetime import datetime, timedelta

utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)
db_ops_module = imp.load_source('db_ops', '/omd/sites/%s/lib/python/handlers/db_ops.py' % nocout_site_name)


class MKGeneralException(Exception):
    """
    Class defination for the Exception Class.
    Args: Exception object
    Kwargs: None
    Return: message
    Exception :None

    """
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return self.reason

def get_ss(host=None, interface=None):
        ss_device = None
        global nocout_site_name
        l_host_vars = {
                    "FOLDER_PATH": "",
                    "ALL_HOSTS": '', # [ '@all' ]
                    "all_hosts": [],
                    "clusters": {},
                    "ipaddresses": {},
                    "extra_host_conf": { "alias" : [] },
                    "extra_service_conf": { "_WATO" : [] },
                    "host_attributes": {},
                    "host_contactgroups": [],
                    "_lock": False,
        }
        # path to hosts file
        hosts_file = '/omd/sites/%s/etc/check_mk/conf.d/wato/hosts.mk' % nocout_site_name
        try:
                execfile(hosts_file, l_host_vars, l_host_vars)
                del l_host_vars['__builtins__']
                host_row = filter(lambda t: re.match(interface, t.split('|')[1]) \
                                and re.match(host, t.split('|')[2]), l_host_vars['all_hosts'])
                ss_device = host_row[0].split('|')[0]
        except Exception, e:
                raise Exception, e

        return ss_device



def inventory_perf_data(site,hostlist):
	"""
	inventory_perf_data : Function for collecting the data for inventory serviecs.Service state is also retunred for those services
	Args: site (site on poller on which devices are monitored)
	Kwargs: hostlist (all host on that site)

	Return : None
	Raises: No Exception
	"""

	invent_check_list = []
	invent_data_list = []
	invent_service_dict = {}
	multiple_ds_services = []
	interface_oriented_service= ['cambium_ss_connected_bs_ip_invent']
	ss_provis_helper_service = ['wimax_ss_ptx_invent']
	query = "GET services\nColumns: host_name host_address host_state service_description service_state plugin_output perf_data\n"+\
                            "Filter: service_description ~ _invent\n"+\
                            "OutputFormat: json\n" 
	query_output = json.loads(get_from_socket(site,query).strip())
	device_down_query = "GET services\nColumns: host_name\nFilter: service_description ~ Check_MK\nFilter: service_state = 3\n"+\
                                "And: 2\nOutputFormat: python\n"
	device_down_output = eval(get_from_socket(site, device_down_query))
	device_down_list =[str(item) for sublist in device_down_output for item in sublist]
	s_device_down_list = set(device_down_list)
	
	ss_provis_helper_serv_data = []
	for entry in query_output:
		if str(entry[0]) in s_device_down_list:
			continue
		service_state = entry[4]
		host = entry[0]
		if service_state == 0:
			service_state = "ok"
		elif service_state == 1:
			service_state = "warning"
		elif service_state == 2:
			service_state = "critical"
		elif service_state == 3:
			service_state = "unknown"
		host_ip = entry[1] 
		service = entry[3]
		try:				
			plugin_output = str(entry[5].split('- ')[1])
			plugin_output=plugin_output.strip()
		except Exception as e:
			#print e
			continue

		if interface_oriented_service[0] in service:
			ds= "bs_ip"
		else: 
			ds=service.split('_')[1:-1]
			ds = ('_').join(ds)
			if 'frequency' in ds:
				ds= 'frequency'
		
		current_time = int(time.time())
		plugin_output = plugin_output.split(' ')
		if len(plugin_output) > 1 and 'radwin' not in service and 'rad5k' not in service:
			try:
				ds_list = map(lambda x: x.split("=")[0],plugin_output)
				value_list = map(lambda x: x.split("=")[1],plugin_output)
			except Exception,e:
				continue

			for index in range(len(ds_list)):
				if value_list[index] and value_list[index] != 'unknown_value':
					value = value_list[index]
				elif  value_list[index] == '' or value_list[index] == 'unknown_value':
					try:
						value = unknwn_state_svc_data[(host,service,ds_list[index])]
					except:
						value = value_list[index]
				else:
					value = value_list[index]
					if not value:
						continue	
				invent_service_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,
				device_name=host,
				service_name=service,current_value=value,min_value=0,max_value=0,avg_value=0,
				data_source=ds_list[index],severity=service_state,site_name=site,warning_threshold=0,
				critical_threshold=0,ip_address=host_ip)
				
				invent_data_list.append(invent_service_dict)
				invent_service_dict = {}
		elif ('rad5k' in service):
			warning_t=0
			critical_t=0
			perf_data1 =  get_threshold(entry[6])
			ds_l=perf_data1.keys()
			ds = ds_l[0]
			perf_data2 = perf_data1[ds]
			value = perf_data2.get('cur','')
                        warning_t= perf_data2.get('war','')
                        critical_t= perf_data2.get('cric','')
			invent_service_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,device_name=host,
                                        service_name=service,current_value=value,min_value=0,max_value=0,avg_value=0,
                                        data_source=ds,severity=service_state,site_name=site,warning_threshold=warning_t,
                                        critical_threshold=critical_t,ip_address=host_ip)
			invent_data_list.append(invent_service_dict)
			invent_service_dict = {}
			
		else:
			try:
				if plugin_output[0] == '' or plugin_output[0] == 'unknown_value':
					value = unknwn_state_svc_data[(host,service,ds)]
				else:
					value = plugin_output[0]	
			except:
				value = plugin_output[0]
					
			if service in ss_provis_helper_service:
				ss_provis_helper_serv_data.append({
				'device_name': host,
				'service_name': service,
				'current_value': value
				})
	
				
			invent_service_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,device_name=host,
					service_name=service,current_value=value,min_value=0,max_value=0,avg_value=0,
					data_source=ds,severity=service_state,site_name=site,warning_threshold=0,
					critical_threshold=0,ip_address=host_ip)
			invent_data_list.append(invent_service_dict)
			invent_service_dict = {}

	##########################
	# Storing the value in memcache

	key = nocout_site_name + "_inventory" 
	doc_len_key = key + "_len" 
	memc_obj=db_ops_module.MemcacheInterface()
	exp_time =1440 # 1 day
	memc_obj.store(key,invent_data_list,doc_len_key,exp_time,chunksize=1000)
	#mongo_module.mongo_db_insert(db,invent_data_list,"inventory_services")
	# redis implementation
	rds_obj=db_ops_module.RedisInterface()
	#print ss_provis_helper_serv_data
	rds_obj.multi_set(ss_provis_helper_serv_data, perf_type='provis',exp_time=1440)
		


def get_from_socket(site_name, query):
    """
        Function_name : get_from_socket (collect the query data from the socket)

        Args: site_name (poller on which monitoring data is to be collected)

        Kwargs: query (query for which data to be collectes from nagios.)

        Return : None

        raise 
             Exception: SyntaxError,socket error 
    """
    socket_path = "/omd/sites/%s/tmp/run/live" % site_name
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(socket_path)
    s.send(query)
    s.shutdown(socket.SHUT_WR)
    output = ''
    while True:
     out = s.recv(100000000)
     out.strip()
     if not len(out):
        break
     output += out

    return output


def get_threshold(perf_data):
	threshold_values = {}
	if not len(perf_data):
		return threshold_values
	for param in perf_data.split(" "):
		param = param.strip("['\n', ' ']")
		if param.partition('=')[2]:
			if ';' in param.split("=")[1]:
				threshold_values[param.split("=")[0]] = {
                	"war": re.sub('ms', '', param.split("=")[1].split(";")[1]),
                	"cric": re.sub('ms', '', param.split("=")[1].split(";")[2]),
                	"cur": re.sub('ms', '', param.split("=")[1].split(";")[0])
            		}
			else:
				threshold_values[param.split("=")[0]] = {
                	"war": None,
                	"cric": None,
                	"cur": re.sub('ms', '', param.split("=")[1].strip("\n"))
            		}
		else:
			threshold_values[param.split("=")[0]] = {
				"war": None,
				"cric": None,
				"cur": None
                       		}
	return threshold_values


def inventory_perf_data_main():
	"""
	inventory_perf_data_main : Main Function for data extraction for inventory services.Function get all configuration from config.ini
	Args: None
	Kwargs: None

	Return : None
	Raises: No Exception
	"""
	try:
		configs = config_module.parse_config_obj()
		desired_site = filter(lambda x: x == nocout_site_name, configs.keys())[0]
		desired_config = configs.get(desired_site)
		site = desired_config.get('site')
		query = "GET hosts\nColumns: host_name\nOutputFormat: json\n"
		output = json.loads(utility_module.get_from_socket(site,query))
		inventory_perf_data(site,output)
	except SyntaxError, e:
		raise MKGeneralException(("Can not get performance data: %s") % (e))
	except socket.error, msg:
		raise MKGeneralException(("Failed to create socket. Error code %s Error Message %s:") % (str(msg[0]), msg[1]))
if __name__ == '__main__':

	inventory_perf_data_main()	

				
