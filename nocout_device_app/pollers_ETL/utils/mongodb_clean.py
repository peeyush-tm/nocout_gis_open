
from nocout_site_name import *
import mysql.connector
from datetime import datetime, timedelta
import subprocess
import socket
import imp
import time

mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

def main(**configs):
	service_tables = ['service_perf','network_perf']
        interface_tables = ['status_perf']
	inventory_tables = ['nocout_inventory_service_perf_data']
	events_tables = ['nocout_service_event_log','nocout_host_event_log']
	for i in range(len(configs.get('mongo_conf'))):
		db = mongo_module.mongo_conn(
		host=configs.get('mongo_conf')[i][1],
		port=int(configs.get('mongo_conf')[i][2]),
		db_name=configs.get('nosql_db')
                )  
		collections = db.collection_names()
		end_time =datetime.today() + timedelta(days=-7)
		#start_time =datetime.today() + datetime.timedelta(days=-2)
		#start_epoch = int(time.mktime(start_time.timetuple()))
    		end_epoch = int(time.mktime(end_time.timetuple()))
	        for table in service_tables:
			if table in collections:
				try:
					db[table].remove({"data":{ "$elemMatch": { "time" : {"$lt": end_time}}}})
				except Exception as e:
					print e
		for table in interface_tables:
			if table in collections:
				try:
					db[table].remove( {"check_timestamp": { "$lt": end_epoch}})
				except Exception as e:
					print e
		for table in events_tables:
			if table in collections:
				try:
					db[table].remove( {"check_timestamp": {"$lt": end_epoch}})
				except Exception as e:
					print e
		for table in inventory_tables:
			if table in collections:
				try:
					db[table].remove({"check_timestamp": {"$lt": end_epoch}})
				except Exception as e:
					print e
		# Requires extra 2 GB space to run... May block other operation on Mongodb and takes time ,so commented, space will be marked as deleted 
		# although space will not be returned to OS.
		#db.repairDatabase()

if __name__ == '__main__':
	main()
