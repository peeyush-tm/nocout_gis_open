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

def inventory_perf_data(site,hostlist,mongo_host,mongo_port,mongo_db_name):
	"""
	inventory_perf_data : Function for collecting the data for inventory serviecs.Service state is also retunred for those services
	Args: site (site on poller on which devices are monitored)
	Kwargs: hostlist (all host on that site)

	Return : None
	Raises: No Exception
	"""

	invent_check_list = []
	invent_service_dict = {}
	matching_criteria = {}
	db = mongo_module.mongo_conn(host = mongo_host,port = mongo_port,db_name =mongo_db_name)
	for host in hostlist:
		query = "GET hosts\nColumns: host_services\nFilter: host_name = %s\n" %(host[0])
		query_output = utility_module.get_from_socket(site,query).strip()
		service_list = [service_name for service_name in query_output.split(',')]
		for service in service_list:
			if service.endswith('_invent'):
				invent_check_list.append(service)
		for service in invent_check_list:
			query_string = "GET services\nColumns: service_state plugin_output host_address\nFilter: " + \
			"service_description = %s\nFilter: host_name = %s\nOutputFormat: json\n" 	 	% (service,host[0])
			query_output = json.loads(utility_module.get_from_socket(site,query_string).strip())
			try:
				if query_output[0][1]:
					plugin_output = str(query_output[0][1].split('- ')[1])
					service_state = (query_output[0][0])
					if service_state == 0:
						service_state = "OK"
					elif service_state == 1:
						service_state = "WARNING"
					elif service_state == 2:
						service_state = "CRITICAL"
					elif service_state == 3:
						service_state = "UNKNOWN"
					host_ip = str(query_output[0][2])
				else:
					continue
				ds=service.split('_')[1:-1]
				ds = ('_').join(ds)
			except:
				continue
			current_time = int(time.time())
			invent_service_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,device_name=str(host[0]),
						service_name=service,current_value=plugin_output,min_value=0,max_value=0,avg_value=0,
						data_source=ds,severity=service_state,site_name=site,warning_threshold=0,
						critical_threshold=0,ip_address=host_ip)
			matching_criteria.update({'device_name':str(host[0]),'service_name':service,'site_name':site})
			mongo_module.mongo_db_update(db,matching_criteria,invent_service_dict,"inventory_services")
			mongo_module.mongo_db_insert(db,invent_service_dict,"inventory_services")
			matching_criteria ={}
			invent_service_dict = {}
		invent_check_list = []

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
		
				
