"""
device_availability.py
=======================

This file contains the code for extracting and collecting the data for inventory services and storing this data into embeded mongodb database.

Inventory services are services for which data is coming in 1 day interval.

"""

from nocout_site_name import *
import socket,json
import time
import imp
import sys
from datetime import datetime, timedelta
from device_availability_migration import main as data_migration


utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)
db_ops_module = imp.load_source('configparser', '/omd/sites/%s/lib/python/handlers/db_ops.py' % nocout_site_name)



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

def device_availability_data(site,mongo_host,mongo_port,mongo_db_name):
	"""
	inventory_perf_data : Function for collecting the data for inventory serviecs.Service state is also retunred for those services
	Args: site (site on poller on which devices are monitored)
	Kwargs: hostlist (all host on that site)

	Return : None
	Raises: No Exception
	"""


        #db = mongo_module.mongo_conn(host = mongo_host,port = mongo_port,db_name =mongo_db_name)
        service = "availability"
	availability_list= []
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)

	start_time = start_time + timedelta(minutes=-(start_time.minute % 5))
	end_time = end_time + timedelta(minutes=-(end_time.minute % 5))

	start_time =start_time.replace(second=0,microsecond=0)
	end_time =end_time.replace(second=0,microsecond=0)

        start_time =int(time.mktime(start_time.timetuple()))
        end_time =int(time.mktime(end_time.timetuple()))
	"""
        pipe =  [
                {"$match": {
                "local_timestamp": { "$gt": start_time, "$lt": end_time}, "service": "ping", "ds": "pl"
                }},
                {"$unwind": "$data"},
                {"$group": {
                        "_id": "$host",
                        "count": {"$sum": {"$cond":[{"$eq":["$data.value","100"]},1,0]}},
                        "ip":{"$first":"$ip_address"}
                }},
                ]
	try:
        	result = db['network_perf'].aggregate(pipeline=pipe)
		result = result.get('result')
	except:
		return
        """
	
	try:
		redis_obj = db_ops_module.RedisInterface()
		key = nocout_site_name + "_network"
		print "Before redis ",time.ctime()
		result=redis_obj.zrangebyscore_dcompress(key,start_time,end_time)
		print "After redis ",time.ctime()
	except Exception,e:
		print e
	host_down_result = {}
	pl_devices = filter(lambda x: x.get('ds') == "pl" ,result)
	print start_time,end_time
	for entry in pl_devices:
		if (entry['host'],entry['ip_address']) in host_down_result:
			if entry.get('data')[0].get('value') == "100":
				host_down_result[(entry['host'],entry['ip_address'])] =  host_down_result.get((entry['host'],entry['ip_address'])) + 1
		else:
			host_down_result[(entry['host'],entry['ip_address'])] = 0
			if entry.get('data')[0].get('value') == "100":
				host_down_result[(entry['host'],entry['ip_address'])] =  host_down_result.get((entry['host'],entry['ip_address'])) + 1
 	for key in host_down_result:
		try:
			down_count = host_down_result[key]
			total_down = ((down_count * 5)/(24*60.0) *100)
			if total_down >=100:
				total_down = 100.0
			total_up = "%.2f" % (100 -total_down )
 			host_state = "ok"
                except Exception ,e:
                        print e
                        continue
                ds="availability"

		current_time = int(time.time())
		availability_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,device_name=str(key[0]),
						service_name=service,current_value=total_up,min_value=0,max_value=0,avg_value=0,
						data_source=ds,severity=host_state,site_name=site,warning_threshold=0,
						critical_threshold=0,ip_address=str(key[1]))
		availability_list.append(availability_dict)	
	print "After for loop ",time.ctime()
	key = nocout_site_name + "_availability" 
	doc_len_key = key + "_len" 
	memc_obj=db_ops_module.MemcacheInterface()
	exp_time =1440 # 1 day\
	print time.ctime()
	print len(availability_list)
	memc_obj.store(key,availability_list,doc_len_key,exp_time,chunksize=1000)
		#mongo_module.mongo_db_insert(db,availability_dict,"availability")

def device_availability_main():
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
		device_availability_data(site,mongo_host,int(mongo_port),mongo_db_name)
	except SyntaxError, e:
		raise MKGeneralException(("Can not get performance data: %s") % (e))
	except socket.error, msg:
		raise MKGeneralException(("Failed to create socket. Error code %s Error Message %s:") % (str(msg[0]), msg[1]))
if __name__ == '__main__':
	device_availability_main()
	time.sleep(200)
	data_migration()	
		
				
