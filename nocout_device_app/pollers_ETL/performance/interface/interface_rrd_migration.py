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
	matching_criteria = {}
	db = mongo_module.mongo_db_conn(site,"nocout")
	query_string = "GET services\nColumns: host_name host_address host_state service_description service_state service_perf_data\n" +\
			"Filter: service_description ~ _status\nOutputFormat: json\n"
	query_output = json.loads(utility_module.get_from_socket(site,query_string).strip())
	for entry in query_output:
		if int(entry[2]) == 1:
			return
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
			perf_data_output = entry[5]
		except Exception as e:
			print e
			continue
		if perf_data_output:
			current_time = int(time.time())
			perf_data = utility_module.get_threshold(perf_data_output)
                	for ds in perf_data.iterkeys():
                        	cur =perf_data.get(ds).get('cur')
                        	war =perf_data.get(ds).get('war')
                        	crit =perf_data.get(ds).get('cric')
				status_service_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,device_name=str(host),
                                                service_name=service,current_value=cur,min_value=0,max_value=0,avg_value=0,
                                                data_source=ds,severity=service_state,site_name=site,warning_threshold=war,
                                                critical_threshold=crit,ip_address=host_ip)
				matching_criteria.update({'device_name':str(host),'service_name':service,'data_source':ds})
				mongo_module.mongo_db_update(db,matching_criteria,status_service_dict,"status_services")
				matching_criteria = {}
				status_check_list.append(status_service_dict)
				status_service_dict = {}
	mongo_module.mongo_db_insert(db,status_check_list,"status_services")
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
		
				
