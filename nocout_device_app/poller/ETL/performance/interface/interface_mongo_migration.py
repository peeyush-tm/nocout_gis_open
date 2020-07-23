"""
interface_mongo_migration.py
==========================

Script to bulk insert data from Teramatrix Pollers into
central mysql db, for interface services.
The data in the Teramatrix Pollers is stored in Mongodb.

Interface services include : Services which runs once an Hour.
"""

from nocout_site_name import *
import mysql.connector
from datetime import datetime, timedelta
import imp
import sys
import time
#from handlers.db_ops import *
mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)
db_ops_module = imp.load_source('db_ops', '/omd/sites/%s/lib/python/handlers/db_ops.py' % nocout_site_name)
def main(**configs):
    """
    The entry point for the all the functions in this file,
    calls all the appropriate functions in the file

    Kwargs:
        configs (dict): A python dictionary containing object key identifiers
    as configuration values, read from main configuration file config.ini
    Example:
        {
    "site": "nocout_gis_subordinate",
    "host": "localhost",
    "user": "root",
    "ip": "localhost",
    "sql_passwd": "admin",
    "nosql_passwd": "none",
    "port": 27019 # The port being used by mongodb process
    "status": {
        "nosql_db": "nocout" # Mongodb database name
        "sql_db": "nocout_dev" # Sql database name
        "script": "status_mongo_migration" # Script which would do all the migrations
        "table_name": "performance_performancestatus" # Sql table name

        }
    }
    """

    data_values = []
    values_list = []
    docs = []
    db=None
    try:
    	db = utility_module.mysql_conn(configs=configs)
    except Exception,e:
	print e
	return
    docs = read_data()
    print len(docs)
    if docs:
        insert_data(configs.get('table_name'), docs, db,configs)
        print "Data inserted into performance_performancestatus table"
    else:
        print "No data in the mongo db in this time frame"
    

def read_data():
    """
    Function to read data from mongodb

    Args:
        start_time (int): Start time for the entries to be fetched
    end_time (int): End time for the entries to be fetched

    Kwargs:
    kwargs (dict): Store mongodb connection variables 
    """

    #db = None
    docs = []
    current_time = datetime.now()
    memc_obj = db_ops_module.MemcacheInterface()
    key = nocout_site_name + "_interface"
    memc = memc_obj.memc_conn
    start_time = memc.get('performance_status')
    print 'in service'
    print start_time
    if start_time: 
    	start_time = datetime.fromtimestamp(start_time)
    if start_time and (start_time + timedelta(minutes=120)) < current_time:
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
    	doc_len_key = key + "_len"
    	cur=memc_obj.retrieve(key,doc_len_key) 
    
    values_list = []
    configs = config_module.parse_config_obj()
    for config, options in configs.items():
	machine_name = options.get('machine')
    for doc in cur:	 
	t = (
	    doc.get('device_name'),
	    doc.get('service_name'),
	    doc.get('sys_timestamp'),
	    doc.get('check_timestamp'),
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
	    machine_name
	)
	values_list.append(t)
        t = ()
    return values_list

def build_data(doc):
    """
    Function to make tuples to be stored into mysql db

    Args:
        doc (dict): Single mongodb entry

    Returns:
        List of tuples, each tuple would correspond to one row in mysql db
    """
    values_list = []
    configs = config_module.parse_config_obj()
    for config, options in configs.items():
        machine_name = options.get('machine')
    t = (
    doc.get('device_name'),
    doc.get('service_name'),
    doc.get('sys_timestamp'),
    doc.get('check_timestamp'),
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
    machine_name
    )
    values_list.append(t)
    t = ()
    return values_list

def insert_data(table, data_values, db,configs):
    """
    Function to bulk insert data into mysql db

    Args:
        table (str): Mysql table name
            data_values (list): List of data tuples

    Kwargs:
        kwargs: Mysqldb connection variables
    """
    if not db.is_connected():
    	db = utility_module.mysql_conn(configs=configs)
	
    query = 'INSERT INTO `%s` ' % table
    query += """
                (device_name,service_name,sys_timestamp,check_timestamp,
                current_value,min_value,max_value,avg_value,warning_threshold,
                critical_threshold,severity,site_name,data_source,
                ip_address,machine_name)
                VALUES(%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
    cursor = db.cursor()
    try:
        cursor.executemany(query, data_values)
    except mysql.connector.Error as err:
        raise mysql.connector.Error, err
    db.commit()
    cursor.close()
    db.close()


if __name__ == '__main__':
    main()
