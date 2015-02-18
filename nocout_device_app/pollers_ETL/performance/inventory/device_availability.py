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

def device_availability_data(site,mongo_host,mongo_port,mongo_db_name):
	"""
	inventory_perf_data : Function for collecting the data for inventory serviecs.Service state is also retunred for those services
	Args: site (site on poller on which devices are monitored)
	Kwargs: hostlist (all host on that site)

	Return : None
	Raises: No Exception
	"""


        db = mongo_module.mongo_conn(host = mongo_host,port = mongo_port,db_name =mongo_db_name)
        service = "availability"
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
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
        for entry in result:
                try:
                        host = entry.get('_id')
                        host_ip = entry.get('ip')
                        down_count = entry.get('count')
                        total_down = ((down_count * 5)/(24*60) *100)
                        total_up = 100 -total_down
                        host_state = "ok"
                except Exception ,e:
                        print e
                        continue
                ds="availability"

		current_time = int(time.time())
		availability_dict = dict (sys_timestamp=current_time,check_timestamp=current_time,device_name=str(host),
						service_name=service,current_value=total_up,min_value=0,max_value=0,avg_value=0,
						data_source=ds,severity=host_state,site_name=site,warning_threshold=0,
						critical_threshold=0,ip_address=host_ip)
		mongo_module.mongo_db_insert(db,availability_dict,"availability")

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
		
				
