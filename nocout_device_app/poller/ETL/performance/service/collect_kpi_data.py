"""
wimax_kpi_data.py
=======================

This file contains the code for extracting and collecting the data for wimax topology and storing this data into embeded mongodb database.

"""

from nocout_site_name import *
import socket,json
import time
import imp
from datetime import datetime,timedelta


from collections import defaultdict
from itertools import groupby
from operator import itemgetter


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



def calculate_avg_value(unknwn_state_svc_data,db):
	end_time = datetime.now()
	start_time = end_time - timedelta(minutes=60)

	host_svc_ds_dict ={}
	svc_host_key={}
	host_list = []
	avg = None
	service_list = []
	for doc in unknwn_state_svc_data:
		host_list.append(doc[0])
		service_list.append(doc[3])
	#print unknwn_state_svc_data
	query_results = db.kpi_data.aggregate([
	{
	 "$match" :{"device_name": {"$in": host_list},"service_name":{"$in": service_list},"sys_timestamp":{"$gte":start_time,"$lte":end_time} }

	}
	])
	for key,entry in groupby(sorted(query_results['result'],key=itemgetter('device_name','service_name','data_source')),
		key=itemgetter('device_name','service_name','data_source')):
		doc_list = list(entry)
		try:
			value_list =[str(x['current_value']) for x in doc_list if x['current_value'] != '']
			#print x['service_name'],x['device_name'],value_list
			#print len(doc_list),doc_list[len(doc_list)-1]['host'],doc_list[len(doc_list)-1]['service'],value_list
			if 'util' in x['service_name'] :
				value_list = map(float,value_list)
				if len(value_list):
					avg = format(sum(value_list)/len(value_list),'.2f')
					#print avg
		except Exception,e:
			avg= None
			print e, x['service_name'], x['device_name'],value_list
			continue
		if key not in host_svc_ds_dict:
			if avg:
				host_svc_ds_dict[key] =avg
		avg= None
		#print host_svc_ds_dict
	return host_svc_ds_dict


def format_kpi_data(site,output,output1,unknwn_state_svc_data,device_down_list,db):
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
	kpi_update =[]
	kpi_services = ['wimax_bs_ul_issue_kpi','wimax_pmp1_dl_util_kpi','wimax_pmp1_ul_util_kpi','wimax_pmp2_dl_util_kpi',
	'wimax_pmp2_ul_util_kpi','cambium_dl_util_kpi','cambium_ul_util_kpi','cambium_bs_ul_issue_kpi']
	device_sector_id =""
	pmp1_device_sector_id =""
	pmp2_device_sector_id =""
        port_sec_mapping = {}
	for entry in output:
		reverse= 0
		device_sector_id =""
		if str(entry[0]) in device_down_list:
			continue
		service_state = int(entry[4])
		host = str(entry[0])
		host_ip = entry[1]
		service = str(entry[3])
		last_state_change  = entry[6]
                age = last_state_change
		perf_data = entry[-1]
		if service_state == 0:
			service_state = "ok"
		elif service_state == 1:
			service_state = "warning"
		elif service_state == 2:
			service_state = "critical"
		elif service_state == 3:
			service_state = "unknown"

		try:
			if 'radwin' in service or 'mrotek' in service or 'rici' in service:
				if entry[-1]:
					device_sector_id= entry[-1].split('=')[1].split(';')[3]
			elif service in kpi_services:
				if 'wimax_bs_ul_issue_kpi' == service:
					service_for_sector = "wimax_pmp1_sector_id_invent"
					device_sector_id = filter(lambda x: host in x and service_for_sector in x,output1)
					pmp1_device_sector_id = str(device_sector_id[0][2].split('- ')[1])

					service_for_sector = "wimax_pmp2_sector_id_invent"
					device_sector_id = filter(lambda x: host in x and service_for_sector in x,output1)
					pmp2_device_sector_id = str(device_sector_id[0][2].split('- ')[1])
					
				elif 'pmp1' in service:
					service_for_sector = "wimax_pmp1_sector_id_invent"
					device_sector_id = filter(lambda x: host in x and service_for_sector in x,output1)
					device_sector_id = str(device_sector_id[0][2].split('- ')[1])
				elif 'pmp2' in service:
					service_for_sector = "wimax_pmp2_sector_id_invent"
					device_sector_id = filter(lambda x: host in x and service_for_sector in x,output1)
					device_sector_id = str(device_sector_id[0][2].split('- ')[1])
				elif 'cambium' in service:
					service_for_sector = "cambium_bs_sector_id_invent"
					device_sector_id = filter(lambda x: host in x and service_for_sector in x,output1)
					device_sector_id = str(device_sector_id[0][2].split('- ')[1])
		
 
		except:
			device_sector_id = ""

		
		try:
			if service == 'wimax_bs_ul_issue_kpi':
        			port_sec_mapping = {}
				try:
					polled_port1 = entry[-1].split(' ')[0].split('=')[0]
					polled_sec_id_1=entry[-1].split(' ')[0].split('=')[1].split(';')[3]
					if polled_sec_id_1 == pmp1_device_sector_id:
						port_sec_mapping['pmp1_ul_issue'] = pmp1_device_sector_id
					elif polled_sec_id_1 == pmp2_device_sector_id:
						reverse = 1
						port_sec_mapping['pmp2_ul_issue'] = pmp2_device_sector_id
				except:
					port_sec_mapping[polled_port1]= None
				try:
					polled_port2 = entry[-1].split(' ')[1].split('=')[0]
					polled_sec_id_2=entry[-1].split(' ')[1].split('=')[1].split(';')[3]
					if polled_sec_id_2 == pmp1_device_sector_id:
						reverse  = 1
						port_sec_mapping['pmp1_ul_issue'] = pmp1_device_sector_id
					elif polled_sec_id_2 == pmp2_device_sector_id:
						port_sec_mapping['pmp2_ul_issue'] = pmp2_device_sector_id
				except:
					port_sec_mapping[polled_port2]= None
					
		except:
			device_sector_id= ''
		try:
			threshold_values =  utility_module.get_threshold(entry[-1])
			for ds, ds_values in threshold_values.items():
				check_time =datetime.fromtimestamp(entry[5])
				local_timestamp = utility_module.pivot_timestamp_fwd(check_time)
				try:
					if service == 'wimax_bs_ul_issue_kpi':
						if reverse == 1:
							if ds == 'pmp2_ul_issue':
							 	ds = 'pmp1_ul_issue'
							elif ds == 'pmp1_ul_issue':
								ds = 'pmp2_ul_issue'
						device_sector_id= port_sec_mapping[ds]
				except:
					device_sector_id = ''
				if ds_values.get('cur'):
					value = ds_values.get('cur')
				else:
					try:
						value = unknwn_state_svc_data[(host,service,str(ds))]
						if not value:
							continue		
					except:
						continue
				utilization_ds = str(ds)
				kpi_data_dict.update({
						'sys_timestamp':local_timestamp,
						'check_timestamp':check_time,
						'device_name':host,
						'service_name':service,
						'current_value':value,
						'severity':service_state,
						'data_source':ds,
						'site_name':site,
						'ip_address':host_ip,
						'age':age,
						'warning_threshold': ds_values.get('war'),
						'critical_threshold': ds_values.get('cric'),
						'refer':device_sector_id})
				matching_criteria.update({'device_name':host,'service_name':service,'data_source':utilization_ds})
				kpi_update.append(matching_criteria)
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
	index1 = 0
        index2 = min(1000,len(kpi_data_list))
        try:
                for index3 in range(len(kpi_data_list)):
                        mongo_module.mongo_db_update(db,kpi_update[index3], kpi_data_list[index3], 'kpi_services')

                while(index2 <= len(kpi_data_list)):
                        mongo_module.mongo_db_insert(db, kpi_data_list[index1:index2], 'kpi_services')
                        index1 = index2
                        if index2 >= len(kpi_data_list):
                                break
                        if (len(kpi_data_list) - index2)  < 1000:
                                index2 += (len(kpi_data_list) - index2)
                        else:
                                index2 += 1000
	except Exception,e:
		print e
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
		db = mongo_module.mongo_conn(host = mongo_host,port = int(mongo_port),db_name =mongo_db_name)
		query = "GET services\nColumns: host_name host_address host_state service_description service_state last_check"+\
                        " service_last_state_change service_perf_data\n"+\
			"Filter: service_description ~ .*_kpi\n"+\
                        "OutputFormat: python\n"
                query1= "GET services\nColumns: host_name service_description plugin_output\n" +\
                        "Filter: service_description ~ wimax_pmp1_sector_id_invent\n"+\
                        "Filter: service_description ~ wimax_pmp2_sector_id_invent\n"+ \
                        "Filter: service_description ~ cambium_bs_sector_id_invent\n"+ \
                        "Or: 3\n" +\
                        "OutputFormat: python\n"

		device_down_query = "GET services\nColumns: host_name\nFilter: service_description ~ Check_MK\n" +\
		"Filter: service_state = 3\nAnd: 2\nOutputFormat: python\n"
		service_qry_output = utility_module.get_from_socket(site,query)
		output1 = utility_module.get_from_socket(site,query1)
		query_output1 = eval(utility_module.get_from_socket(site,device_down_query).strip())
		device_down_list =[str(item) for sublist in query_output1 for item in sublist]
		
		service_qry_output = eval(service_qry_output)
		output1 =eval(output1)

		unknown_svc_data = filter(lambda x: x[4] == 3,service_qry_output)
		unknwn_state_svc_data = filter(lambda x: x[0] not in device_down_list and 'util' in str(x[3]) ,unknown_svc_data)
		unknwn_state_svc_data  =  calculate_avg_value(unknwn_state_svc_data,db)

		

		format_kpi_data(site,service_qry_output,output1,unknwn_state_svc_data,device_down_list,db)
	except SyntaxError, e:
		raise MKGeneralException(("Can not get performance data: %s") % (e))
	except socket.error, msg:
		raise MKGeneralException(("Failed to create socket. Error code %s Error Message %s:") % (str(msg[0]), msg[1]))
	except Exception,e:
		print e
if __name__ == '__main__':
	kpi_data_data_main()	
		
				
