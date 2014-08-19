"""
status_services_tables_migration.py
==========================

Script to bulk insert current status data (for services) from
Teramatrix pollers to mysql in 5 min interval for all services except Ping.

Current status data means for each (host, service) pair only most latest entry would
be kept in the database, which describe the status for that service running on a host,
at any given time.

"""

from nocout_site_name import *
import mysql.connector
from datetime import datetime, timedelta
import socket
import imp
import time
mongo_module = imp.load_source('mongo_functions', '/opt/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
utility_module = imp.load_source('utility_functions', '/opt/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/opt/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

def main(**configs):
    """
    The entry point for the all the functions in this file,
    calls all the appropriate functions in the file

    Kwargs:
        configs (dict): A python dictionary containing object key identifiers
	as configuration values, read from main configuration file config.ini
    Example:
        {
	"site": "nocout_gis_slave",
	"host": "localhost",
	"user": "root",
	"ip": "localhost",
	"sql_passwd": "admin",
	"nosql_passwd": "none",
	"port": 27019 # The port being used by mongodb process
	"status_services_tables": {
	    "nosql_db": "nocout" # Mongodb database name
	    "sql_db": "nocout_dev" # Sql database name
	    "scripit": "status_services_tables_migration" # Script which would do all the migrations
	    "table_name": "performance_status" # Sql table name

	    }
	}
    """
    data_values = []
    values_list = []
    docs = []
    db = utility_module.mysql_conn(configs=configs)
    # Get the time for latest entry in mysql
    #start_time = get_latest_entry(db_type='mysql', db=db, site=configs.get('site'),table_name=configs.get('table_name'))
    utc_time = datetime(1970, 1,1,5,30)


    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=60)
    start_epoch = int(time.mktime(start_time.timetuple()))
    end_epoch = int(time.mktime(end_time.timetuple()))

    print start_time,end_time
    
    for i in range(len(configs.get('mongo_conf'))):
    	docs = read_data(start_epoch, end_epoch, configs=configs.get('mongo_conf')[i], db_name=configs.get('nosql_db'))
    	for doc in docs:
        	values_list = build_data(doc)
        	data_values.extend(values_list)
    if data_values:
    	insert_data(configs.get('table_name'), data_values, configs=configs)
   	print "Data inserted into my mysql db"
    else:
    	print "No data in mongodb in this time frame for table %s" % (configs.get('table_name'))

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
        cur = db.device_status_services_status.find({
            "check_timestamp": {"$gt": start_time, "$lt": end_time}
        })
        for doc in cur:
            docs.append(doc)
     
    return docs

def build_data(doc):
	"""
	Function to make tuples to be stored into mysql db

	Args:
	    doc (dict): Single mongodb entry

	Returns:
	    List of tuples, each tuple would correspond to one row in mysql db
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
        doc.get('severity'),
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
	query = "SELECT * FROM %s " % table +\
                "WHERE `device_name`='%s' AND `site_name`='%s' AND `service_name`='%s' AND `data_source`='%s'" %(str(data_values[0][0]),data_values[0][3],data_values[0][1],data_values[0][4])
        cursor = db.cursor()
        try:
                cursor.execute(query)
		result = cursor.fetchone()
	except mysql.connector.Error as err:
        	raise mysql.connector.Error, err

	if result:
 		query = "UPDATE `%s` " % table
		query += """SET `device_name`=%s,`service_name`=%s,
		`machine_name`=%s, `site_name`=%s, `data_source`=%s, `current_value`=%s,
		`min_value`=%s,`max_value`=%s, `avg_value`=%s, `warning_threshold`=%s,
		`critical_threshold`=%s, `sys_timestamp`=%s,`check_timestamp`=%s,
		`ip_address`=%s,`severity`=%s
		WHERE `device_name`=%s AND `site_name`=%s AND `service_name`=%s AND `data_source`=%s 
		""" 
		try:
			data_values = map(lambda x: x + (x[0], x[3], x[1],x[4],), data_values)
                	cursor.executemany(query, data_values)
		except mysql.connector.Error as err:
        		raise mysql.connector.Error, err
                db.commit()
		cursor.close()

	else:
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


if __name__ == '__main__':
    main()
