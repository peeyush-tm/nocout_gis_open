"""
inventory_status_tables_migration.py
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
    db = utility_module.mysql_conn(configs=configs)
    """
    start_time variable would store the latest time uptill which mysql
    table has an entry, so the data having time stamp greater than start_time
    would be imported to mysql, only, and this way mysql would not store
    duplicate data.
    """
    for i in range(len(configs.get('mongo_conf'))):
        start_time = mongo_module.get_latest_entry(
                        db_type='mysql',
                        db=db,
                        site=configs.get('mongo_conf')[i][0],
                        table_name=configs.get('table_name')
        )

    end_time = datetime.now()
    for i in range(len(configs.get('mongo_conf'))):
    	docs = read_data(start_epoch, end_epoch, configs=configs.get('mongo_conf')[i], db_name=configs.get('nosql_db'))
    	for doc in docs:
        	values_list = build_data(doc)
        	data_values.extend(values_list)
    if data_values:
    	insert_data(configs.get('table_name'), data_values, configs=configs)
    	print "Data inserted into my mysql db"
    else:
	print "Data is not present in mongodb in this time frame in %s" % (configs.get('table_name') )
    

def read_data(start_time, end_time, **kwargs):
    """
    Function to read data from mongodb

    Args:
        start_time (int): Start time for the entries to be fetched
	end_time (int): End time for the entries to be fetched

    Kwargs:
	kwargs (dict): Store mongodb connection variables 
    """

    db = None
    port = None
    docs = []
    #end_time = datetime(2014, 6, 26, 18, 30)
    #start_time = end_time - timedelta(minutes=10)
    docs = [] 
    db = mongo_module.mongo_conn(
        host=kwargs.get('configs')[1],
        port=int(kwargs.get('configs')[2]),
        db_name=kwargs.get('db_name')
    ) 
    if db:
	if start_time is None:
                cur = db.device_service_status.find()
	else:
        	cur = db.device_inventory_status.find({
            	"check_timestamp": {"$gt": start_time, "$lt": end_time}
        	})
        for doc in cur:
            docs.append(doc)
     
    return docs

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
	local_time_epoch = utility_module.get_epoch_time(doc.get('local_timestamp'))
	check_timestamp = utility_module.get_epoch_time(doc.get('check_timestamp'))
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
        local_time_epoch,
        check_timestamp,
        doc.get('ip_address'),
        doc.get('severity'),
	doc.get('age'),
	doc.get('refer')
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
	insert_dict = {'0':[],'1':[]}
	db = utility_module.mysql_conn(configs=kwargs.get('configs'))
	for i in range(len(data_values)):
		query = "SELECT * FROM %s " % table +\
                	"WHERE `device_name`='%s' AND `service_name`='%s' AND `data_source`='%s'" %(str(data_values[i][0]),data_values[i][1],data_values[i][4])
		cursor = db.cursor()
        	try:
                	cursor.execute(query)
			result = cursor.fetchone()
		except mysql.connector.Error as err:
        		raise mysql.connector.Error, err
		if result:
			insert_dict['1'].append(data_values[i])
		else:
			insert_dict['0'].append(data_values[i])
	
	if len(insert_dict['1']):
 		query = "UPDATE `%s` " % table
		query += """SET `device_name`=%s,`service_name`=%s,
		`machine_name`=%s, `site_name`=%s, `data_source`=%s, `current_value`=%s,
		`min_value`=%s,`max_value`=%s, `avg_value`=%s, `warning_threshold`=%s,
		`critical_threshold`=%s, `sys_timestamp`=%s,`check_timestamp`=%s,
		`ip_address`=%s,`severity`=%s,`age`=%s,`refer`=%s 
		WHERE `device_name`=%s AND `data_source`=%s AND `service_name`=%s
		""" 
		try:
			data_values = map(lambda x: x + (x[0], x[4], x[1],), insert_dict.get('1'))
                	cursor.executemany(query, data_values)
		except mysql.connector.Error as err:
        		raise mysql.connector.Error, err
                db.commit()
		cursor.close()

	if len(insert_dict['0']):
		query = "INSERT INTO `%s`" % table
 		query+= """(device_name, service_name, machine_name, 
            	site_name, data_source, current_value, min_value, 
            	max_value, avg_value, warning_threshold, 
            	critical_threshold, sys_timestamp, check_timestamp,ip_address,severityi,age,refer) 
           	VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s,%s,%s,%s)
		"""
    		cursor = db.cursor()
    		try:
        		cursor.executemany(query, insert_dict.get('0'))
    		except mysql.connector.Error as err:
				raise mysql.connector.Error, err
    		db.commit()
    		cursor.close()



if __name__ == '__main__':
    main()
