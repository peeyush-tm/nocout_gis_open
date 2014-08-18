from nocout_site_name import *
import socket,json
import imp
import time
import imp

utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

class MKGeneralException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return self.reason

def status_perf_data(site,hostlist):

	status_check_list = []
	status_service_dict = {}
	matching_criteria = {}
	db = mongo_module.mongo_db_conn(site,"nocout")
	for host in hostlist:
		query = "GET hosts\nColumns: host_services\nFilter: host_name = %s\n" %(host[0])
		query_output = utility_module.get_from_socket(site,query).strip()
		service_list = [service_name for service_name in query_output.split(',')]
		for service in service_list:
			if service.endswith('_status'):
				status_check_list.append(service)
		for service in status_check_list:
			query_string = "GET services\nColumns: service_state service_perf_data host_address\nFilter: " + \
			"service_description = %s\nFilter: host_name = %s\nOutputFormat: json\n" 	 	% (service,host[0])
			query_output = json.loads(utility_module.get_from_socket(site,query_string).strip())

			if query_output[0][1]:
				perf_data_output = str(query_output[0][1])
				service_state = (query_output[0][0])
				host_ip = str(query_output[0][2])
                        	current_time = int(time.time())
				if service_state == 0:
					service_state = "OK"
				elif service_state == 1:
					service_state = "WARNING"
				elif service_state == 2:
					service_state = "CRITICAL"
				elif service_state == 3:
					service_state = "UNKNOWN"
                		perf_data = utility_module.get_threshold(perf_data_output)
			else:
				continue
                	for ds in perf_data.iterkeys():
                        	cur =perf_data.get(ds).get('cur')
                        	war =perf_data.get(ds).get('war')
                        	crit =perf_data.get(ds).get('cric')
				status_service_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,device_name=str(host[0]),
                                                service_name=service,current_value=cur,min_value=0,max_value=0,avg_value=0,
                                                data_source=ds,severity=service_state,site_name=site,warning_threshold=war,
                                                critical_threshold=crit,ip_address=host_ip)
				matching_criteria.update({'device_name':str(host[0]),'service_name':service,'site_name':site,'data_source':ds})
				mongo_module.mongo_db_update(db,matching_criteria,status_service_dict,"status_services")
                        	mongo_module.mongo_db_insert(db,status_service_dict,"status_services")
				matching_criteria = {}
			#query_output = json.loads(rrd_main.get_from_socket(site,query_string).strip())
		status_service_dict = {}
		status_check_list = [] 

def status_perf_data_main():
	try:
		configs = config_module.parse_config_obj()
		desired_site = filter(lambda x: x == nocout_site_name, configs.keys())[0]
		desired_config = configs.get(desired_site)
		site = desired_config.get('site')
		query = "GET hosts\nColumns: host_name\nOutputFormat: json\n"
		output = json.loads(utility_module.get_from_socket(site,query))
		status_perf_data(site,output)
	except SyntaxError, e:
		raise MKGeneralException(("Can not get performance data: %s") % (e))
	except socket.error, msg:
		raise MKGeneralException(("Failed to create socket. Error code %s Error Message %s:") % (str(msg[0]), msg[1]))
if __name__ == '__main__':
	status_perf_data_main()	
		
				
