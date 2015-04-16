from nocout_site_name import *
import socket,json
import imp
import time
import imp

from collections import defaultdict
from itertools import groupby
from operator import itemgetter

from datetime import datetime, timedelta


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
	device_down_query = "GET services\nColumns: host_name\nFilter: service_description ~ Check_MK\nFilter: service_state = 3\n"+\
                                "And: 2\nOutputFormat: python\n"
	device_down_output = eval(utility_module.get_from_socket(site, device_down_query))
	device_down_list =[str(item) for sublist in device_down_output for item in sublist]
	s_device_down_list = set(device_down_list)
	
        unknown_svc_data = filter(lambda x: x[4] == 3,query_output)
        unknwn_state_svc_data = filter(lambda x: x[0] not in s_device_down_list,unknown_svc_data)
	#print unknwn_state_svc_data
        unknwn_state_svc_data  = calculate_avg_value(unknwn_state_svc_data,db)
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
				if cur and cur != 'unknown_value':
					value = cur
				elif  cur == '' or cur == 'unknown_value':
					try:
						value = unknwn_state_svc_data[(str(host),str(service),ds)]
						#print '........'
						#print value
					except Exception,e:
						#print e
						value = cur
				else:
					value = cur
					if not value:
						continue

				status_service_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,device_name=str(host),
                                                service_name=service,current_value=value,min_value=0,max_value=0,avg_value=0,
                                                data_source=ds,severity=service_state,site_name=site,warning_threshold=war,
                                                critical_threshold=crit,ip_address=host_ip)
				matching_criteria.update({'device_name':str(host),'service_name':service,'data_source':ds})
				mongo_module.mongo_db_update(db,matching_criteria,status_service_dict,"status_services")
				matching_criteria = {}
				status_check_list.append(status_service_dict)
				status_service_dict = {}
	mongo_module.mongo_db_insert(db,status_check_list,"status_services")


def calculate_avg_value(unknwn_state_svc_data,db):
	end_time = datetime.now()
	start_time = end_time - timedelta(hours=12)
	start_epoch = int(time.mktime(start_time.timetuple()))
	end_epoch = int(time.mktime(end_time.timetuple()))
	#print start_epoch,end_epoch
	host_svc_ds_dict ={}
	svc_host_key={}
	host_list = []
	avg = None
	service_list = []
	for doc in unknwn_state_svc_data:
		host_list.append(doc[0])
		service_list.append(doc[3])
	query_results = db.status_perf.aggregate([
	{
	 "$match" :{"device_name": {"$in": host_list},"service_name":{"$in": service_list},"sys_timestamp":{"$gte":start_epoch,"$lte":end_epoch} }

	}
	])
	#print query_results
	for key,entry in groupby(sorted(query_results['result'],key=itemgetter('device_name','service_name','data_source')),
		key=itemgetter('device_name','service_name','data_source')):
		doc_list = list(entry)
                try:
			value_list =[str(x['current_value']) for x in doc_list if x['current_value'] != '']
			#print x['device_name'],x['service_name'],value_list
			#print len(doc_list),doc_list[len(doc_list)-1]['host'],doc_list[len(doc_list)-1]['service_name'],value_list
			if '_status' in x['service_name'] :
				# calculating the Maximum number of times value has occured
				c = defaultdict(int)
				for item in value_list:
					c[item] += 1
				if value_list:
					avg= max(c.iteritems(), key=itemgetter(1))
					avg=avg[0]
		except Exception,e:
			avg= None
			#print '####'
			print e 
			#print x['service_name'], x['device_name'],value_list
			continue
                #svc_host_key[key]=avg
		if key not in host_svc_ds_dict:
			if avg:
				host_svc_ds_dict[key] =avg
		avg= None
		#svc_host_key={}
	#print host_svc_ds_dict
	return host_svc_ds_dict


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
		
				
