
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
db_ops_module = imp.load_source('db_ops', '/omd/sites/%s/lib/python/handlers/db_ops.py' % nocout_site_name)

def main(**configs):
	set_name  = [nocout_site_name + "_network",nocout_site_name + "_service",nocout_site_name + "_kpi",nocout_site_name + "_interface"]
	for i in range(len(set_name)):
		end_time =datetime.today() + timedelta(days=-2)
		start_time =datetime.today() + timedelta(days=-1)
		end_time = end_time + timedelta(minutes=-(end_time.minute % 5))
		start_time = start_time + timedelta(minutes=-(start_time.minute % 5))
		end_time = end_time.replace(second=0,microsecond=0)
		end_time =int(time.mktime(end_time.timetuple()))
		start_time = start_time.replace(second=0,microsecond=0)
		start_time =int(time.mktime(start_time.timetuple()))
		#start_time =datetime.today() + datetime.timedelta(days=-2)
		#start_epoch = int(time.mktime(start_time.timetuple()))
		try:
			redis_obj = db_ops_module.RedisInterface()
			print start_time,end_time
			doc_len  = redis_obj.zremrangebyscore_remove(set_name[i],start_time,end_time)
			print set_name[i],doc_len
		except Exception as e:
			print e
			continue

if __name__ == '__main__':
	main()
