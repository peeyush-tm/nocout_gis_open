"""
inventory_mongo_migration.py

File contains the data migrations of mongodb to mysql db for inventory services. Inventory services run once a day.

"""

from nocout_site_name import *
import mysql.connector
from datetime import datetime, timedelta
import socket
import imp
import time
#from handlers.db_ops import *
mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)
db_ops_module = imp.load_source('db_ops', '/omd/sites/%s/lib/python/handlers/db_ops.py' % nocout_site_name)

def main(**configs):
    """
    Main function for reading the data from mongodb database for inventory services.After reading the data ,it is formatted according to mysql
    table schema and inserted into mysql db
    Args: Multiple argument fetched from config.ini
    Return : None
    Raises: No exception
    """
    data_values = []
    values_list = []
    docs = []
    try:
    	db = utility_module.mysql_conn(configs=configs)
    except Exception,e:
	print e
	return
    docs = read_data()
    if docs:
    	insert_data(configs.get('table_name'), docs, db)
    	print "Data inserted into performance_utilization table"
    else:
	print "No data in the mongo db in this time frame"
    

def read_data():

    """
    function for reading the data from mongodb database for inventory services.After reading the data
    Args: start_time (time of last record enrty)
    Kwargs: end_time(current time) ,multiple arguments fetched from config.ini
    Return : None
    Raises: No exception

    """
    db = None
    port = None
    docs = []
    key = nocout_site_name + "_kpi"
    doc_len_key = key + "_len" 
    memc_obj = db_ops_module.MemcacheInterface()
    current_time = datetime.now()
    memc = memc_obj.memc_conn
    start_time = memc.get('performance_utilizationstatus')
    print start_time
    if start_time: 
    	start_time = datetime.fromtimestamp(start_time)
    if start_time and (start_time + timedelta(minutes=20)) < current_time:
    	if start_time + timedelta(days=1) < current_time:
		start_time = current_time -  timedelta(days=1)
	print "....in...back up...stage"
	print start_time
	redis_obj=db_ops_module.RedisInterface()
	t_stmp = start_time + timedelta(minutes=-(start_time.minute % 5))
        t_stmp = t_stmp.replace(second=0,microsecond=0)
        start_time =int(time.mktime(t_stmp.timetuple()))
        current_time = current_time + timedelta(minutes=-(current_time.minute % 5))
        current_time = current_time.replace(second=0,microsecond=0)
        current_time =int(time.mktime(current_time.timetuple()))
	cur=redis_obj.zrangebyscore_dcompress(key,start_time,current_time)
    else:		
    	cur = memc_obj.retrieve(key,doc_len_key)
    configs1 = config_module.parse_config_obj()
    for config, options in configs1.items():
	machine_name = options.get('machine')
    for doc in cur:
	local_timestamp = utility_module.get_epoch_time(doc.get('sys_timestamp'))
	check_timestamp = utility_module.get_epoch_time(doc.get('check_timestamp'))
        t = (
        		doc.get('device_name'),
        		doc.get('service_name'),
        		local_timestamp,
        		check_timestamp,
        		doc.get('current_value'),
        		doc.get('min_value'),
        		doc.get('max_value'),
        		doc.get('avg_value'),
        		doc.get('warning_threshold'),
        		doc.get('critical_threshold'),
        		doc.get('severity'),
        		doc.get('site_name'),
        		doc.get('data_source'),
        		doc.get('ip_address'),
			doc.get('refer'),
			doc.get('age'),
			machine_name	
        )
	docs.append(t)
	t = ()
     
    return docs

def build_data(doc):
	"""
	function for building the data based on the collected record from mongodb database for inventory services.
	Arg: doc (extracted doc from the mongodb )
	Kwargs: None
	Return : formatted record for the mysql
	Raises: No exception
	"""
	configs = config_module.parse_config_obj()
    	for config, options in configs.items():
            machine_name = options.get('machine')
	local_timestamp = utility_module.get_epoch_time(doc.get('local_timestamp'))
	check_timestamp = utility_module.get_epoch_time(doc.get('check_timestamp'))
	values_list = []
        t = (
        doc.get('device_name'),
        doc.get('service_name'),
        local_timestamp,
        check_timestamp,
        doc.get('current_value'),
        doc.get('min_value'),
        doc.get('max_value'),
        doc.get('avg_value'),
        doc.get('warning_threshold'),
        doc.get('critical_threshold'),
        doc.get('severity'),
        doc.get('site_name'),
        doc.get('data_source'),
        doc.get('ip_address'),
	doc.get('refer'),
	doc.get('age'),
	machine_name	
        )
	values_list.append(t)
	t = ()
	return values_list

def insert_data(table, data_values,db):
	"""
	function for building the data based on the collected record from mongodb database for inventory services.
	Arg: table (mysql database table name)
	Kwargs: data_values (formatted record)
	Return : None
	Raises: mysql.connector.Error
	"""
	query = 'INSERT INTO `%s` ' % table
	query += """
                (device_name,service_name,sys_timestamp,check_timestamp,
                current_value,min_value,max_value,avg_value,warning_threshold,
                critical_threshold,severity,site_name,data_source,
                ip_address,refer,age,machine_name)
                VALUES(%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
	cursor = db.cursor()
    	try:
        	cursor.executemany(query, data_values)
    	except mysql.connector.Error as err:
        	raise mysql.connector.Error, err
    	db.commit()
    	cursor.close()



if __name__ == '__main__':
    main()
