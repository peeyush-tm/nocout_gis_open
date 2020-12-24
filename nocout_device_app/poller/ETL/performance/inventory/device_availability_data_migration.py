"""
device_availability_data_migration.py
====================================

Script to bulk insert current status data (for inventory_services) from
Teramatrix pollers to mysql in 1 day time interval.

Current status data means for each (host, service) pair only most latest entry would
be kept in the database, which describe the status for that inventory service running on a host,
at any given time.

Inventory services include: Services that should run once in a day.

"""

from nocout_site_name import *
import mysql.connector
from datetime import datetime, timedelta
import socket
import imp
import time

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
	"inventory_status_tables": {
	    "nosql_db": "nocout" # Mongodb database name
	    "sql_db": "nocout_dev" # Sql database name
	    "scripit": "inventory_status_tables_migration" # Script which would do all the migrations
	    "table_name": "performance_servicestatus" # Sql table name

	    }
	}
    """
    data_values = []
    values_list = []
    docs = []

    site_spec_mongo_conf = filter(lambda e: e[0] == nocout_site_name, configs.get('mongo_conf'))[0]
    docs = read_data()
    for doc in docs:
        values_list = build_data(doc)
        data_values.extend(values_list)
    if data_values:
    	insert_data(configs.get('table_name'), data_values, configs=configs)
    	print "Data inserted into my mysql db"
    else:
	print "Data is not present in mongodb in this time frame in %s" % (configs.get('table_name') )
    

def read_data():
    """
    Function to read data from mongodb

    Args:
        start_time (int): Start time for the entries to be fetched
	end_time (int): End time for the entries to be fetched

    Kwargs:
	kwargs (dict): Store mongodb connection variables 
    """

    """
    db = mongo_module.mongo_conn(
        host=kwargs.get('configs')[1],
        port=int(kwargs.get('configs')[2]),
        db_name=kwargs.get('db_name')
    )
    """
    """ 
    if db:
        cur = db.device_availability.find({
            "check_timestamp": {"$gt": start_time, "$lt": end_time}
        })
    """
    memc_obj = db_ops_module.MemcacheInterface()
    key = nocout_site_name + "_availability"
    doc_len_key = key + "_len"
    cur=memc_obj.retrieve(key,doc_len_key)
     
    return cur

def build_data(doc):
	"""
	Function to make data that would be inserted into mysql db

	Args:
	    doc (dict): Single mongodb document
	"""
	values_list = []
	time = doc.get('time')
	configs = config_module.parse_config_obj()
        for config, options in configs.items():
		machine_name = options.get('machine')
        t = (
        doc.get('device_name'),
        doc.get('service_name'),
        machine_name,
        doc.get('site_name'),
        doc.get('data_source'),
        doc.get('current_value'),
        doc.get('min_value'),
        doc.get('max_value'),
       	doc.get('avg_value'),
        doc.get('warning_threshold'),
        doc.get('critical_threshold'),
        doc.get('sys_timestamp'),
        doc.get('check_timestamp'),
        doc.get('ip_address'),
        doc.get('severity')
        )
	values_list.append(t)
	t = ()
	return values_list

def insert_data(table, data_values, **kwargs):
	"""
        Function to bulk insert data into mysqldb

	Args:
	    table (str): Mysql table to which to be inserted
	    data_value (list): List of data tuples

	Kwargs (dict): Dictionary to hold connection variables
	"""
	db = utility_module.mysql_conn(configs=kwargs.get('configs'))
	
	query = "INSERT INTO `%s`" % table
 	query+= """(device_name, service_name, machine_name, 
        site_name, data_source, current_value, min_value, 
        max_value, avg_value, warning_threshold, 
        critical_threshold, sys_timestamp, check_timestamp,ip_address,severity) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s,%s)
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
