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



utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)



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



def inventory_perf_data(site,hostlist,mongo_host,mongo_port,mongo_db_name):
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
	matching_criteria = {}
	multiple_ds_services = []
	interface_oriented_service= ['cambium_ss_connected_bs_ip_invent']
	db = mongo_module.mongo_conn(host = mongo_host,port = mongo_port,db_name =mongo_db_name)
	query = "GET services\nColumns: host_name host_address host_state service_description service_state plugin_output\n"+\
                            "Filter: service_description ~ _invent\n"+\
                            "OutputFormat: json\n" 
	query_output = json.loads(get_from_socket(site,query).strip())
	for entry in query_output:
		if int(entry[2]) == 1:
			continue
		service_state = entry[4]
		host = entry[0]
		if service_state == 0:
			service_state = "OK"
		elif service_state == 1:
			service_state = "WARNING"
		elif service_state == 2:
			service_state = "CRITICAL"
		elif service_state == 3:
			service_state = "UNKNOWN"
		host_ip = entry[1] 
		service = entry[3]
		try:				
			plugin_output = str(entry[5].split('- ')[1])
		except Exception as e:
			print e
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
		if len(plugin_output) > 1 and 'radwin' not in service:
			ds_list = map(lambda x: x.split("=")[0],plugin_output)
			value_list = map(lambda x: x.split("=")[1],plugin_output)

			for index in range(len(ds_list)):
				if value_list[index]:
					invent_service_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,
					device_name=host,
					service_name=service,current_value=value_list[index],min_value=0,max_value=0,avg_value=0,
					data_source=ds_list[index],severity=service_state,site_name=site,warning_threshold=0,
					critical_threshold=0,ip_address=host_ip)
				
					matching_criteria.update({'device_name':str(host),'service_name':service,
					'data_source':ds_list[index]})
					
					mongo_module.mongo_db_update(db,matching_criteria,invent_service_dict,"inventory_services")
					invent_data_list.append(invent_service_dict)
					matching_criteria ={}
					invent_service_dict = {}
		else:
			invent_service_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,device_name=host,
					service_name=service,current_value=plugin_output[0],min_value=0,max_value=0,avg_value=0,
					data_source=ds,severity=service_state,site_name=site,warning_threshold=0,
					critical_threshold=0,ip_address=host_ip)
			matching_criteria.update({'device_name':host,'service_name':service,'data_source':ds})
			mongo_module.mongo_db_update(db,matching_criteria,invent_service_dict,"inventory_services")
			invent_data_list.append(invent_service_dict)
			matching_criteria ={}
			invent_service_dict = {}
	mongo_module.mongo_db_insert(db,invent_data_list,"inventory_services")



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
		mongo_host = desired_config.get('host')
                mongo_port = desired_config.get('port')
                mongo_db_name = desired_config.get('nosql_db')
		query = "GET hosts\nColumns: host_name\nOutputFormat: json\n"
		output = json.loads(utility_module.get_from_socket(site,query))
		inventory_perf_data(site,output,mongo_host,int(mongo_port),mongo_db_name)
	except SyntaxError, e:
		raise MKGeneralException(("Can not get performance data: %s") % (e))
	except socket.error, msg:
		raise MKGeneralException(("Failed to create socket. Error code %s Error Message %s:") % (str(msg[0]), msg[1]))
if __name__ == '__main__':
	inventory_perf_data_main()	
		
				
