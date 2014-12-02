"""
wimax_kpi_data.py
=======================

This file contains the code for extracting and collecting the data for wimax topology and storing this data into embeded mongodb database.

"""

from nocout_site_name import *
import socket,json
import time
import imp
from datetime import datetime



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

def format_kpi_data(site,output,output1,mongo_host,mongo_port,mongo_db_name):
	"""
	inventory_perf_data : Function for collecting the data for inventory serviecs.Service state is also retunred for those services
	Args: site (site on poller on which devices are monitored)
	Kwargs: hostlist (all host on that site)

	Return : None
	Raises: No Exception
	"""

	kpi_data_list = []
	kpi_data_dict = {
			"warning_threshold":0,
			"critical_threshold":0,
			"min_value":0,
			"max_value":0,
			"avg_value":0
	}
	matching_criteria = {}
	utilization_ds = None
	db = mongo_module.mongo_conn(host = mongo_host,port = mongo_port,db_name =mongo_db_name)

	for entry in output:
		if int(entry[2]) == 1:
			continue
		service_state = int(entry[4])
		host = entry[0]
		host_ip = entry[1]
		service = entry[3]
		last_state_change  = entry[5]
		current_time = int(time.time())
                age = current_time - last_state_change
		perf_data = entry[-1]
		if service_state == 0:
			service_state = "OK"
		elif service_state == 1:
			service_state = "WARNING"
		elif service_state == 2:
			service_state = "CRITICAL"
		elif service_state == 3:
			service_state = "UNKNOWN"
		try:
			threshold_values =  utility_module.get_threshold(entry[-1])
			for ds, ds_values in threshold_values.items():
				check_time =datetime.fromtimestamp(entry[5])
				local_timestamp = utility_module.pivot_timestamp_fwd(check_time)
				if ds_values.get('cur') and ds != "sector_id":
					utilization_ds = ds
					kpi_data_dict.update({
						'sys_timestamp':local_timestamp,
						'check_timestamp':check_time,
						'device_name':host,
						'service_name':service,
						'current_value':ds_values.get('cur'),
						'severity':service_state,
						'data_source':ds,
						'site_name':site,
						'ip_address':host_ip,
						'age':age})
				elif ds == "sector_id":
					kpi_data_dict.update({"refer": ds_values.get('cur')})	
			matching_criteria.update({'device_name':host,'service_name':service,'data_source':utilization_ds})
			mongo_module.mongo_db_update(db,matching_criteria,kpi_data_dict,"kpi_services")
			matching_criteria ={}
			kpi_data_list.append(kpi_data_dict)
			kpi_data_dict = {
				"warning_threshold":0,
				"critical_threshold":0,
				"min_value":0,
				"max_value":0,
				"avg_value":0
			}
		except Exception as e:
			print e
			continue
	mongo_module.mongo_db_insert(db,kpi_data_list,"kpi_services")

def kpi_data_data_main():
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
		query = "GET services\nColumns: host_name host_address host_state service_description service_state last_check"+\
			"service_last_state_change service_perf_data\n"+\
                        "Filter: service_description ~ wimax_pmp1_util_kpi\n"+\
			"Filter: service_description ~ wimax_pmp2_util_kpi\n"+\
			"Filter: service_description ~ cambium_dl_utilization_kpi\n"+\
			"Filter: service_description ~ cambium_ul_utilization_kpi\n"+\
			"Or: 4\nOutputFormat: python"
		query1= "GET services\nColumns: host_name plugin_output\n" +\
			"Filter: service_description ~ wimax_pmp1_sector_id_invent\n"+\
			"Filter: service_description ~ wimax_pmp2_sector_id_invent\n"+ \
			"Or: 2\n" +\
			"OutputFormat: python\n"
		output = utility_module.get_from_socket(site,query)
		output1 = utility_module.get_from_socket(site,query1)
		print output,output1
		format_kpi_data(site,output,output1 ,mongo_host,int(mongo_port),mongo_db_name)
	except SyntaxError, e:
		raise MKGeneralException(("Can not get performance data: %s") % (e))
	except socket.error, msg:
		raise MKGeneralException(("Failed to create socket. Error code %s Error Message %s:") % (str(msg[0]), msg[1]))
if __name__ == '__main__':
	kpi_data_data_main()	
		
				
