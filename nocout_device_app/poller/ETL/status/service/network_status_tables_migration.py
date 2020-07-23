"""
network_status_tables_migration.py
=================================

Script to bulk insert current status data from
Teramatrix pollers to mysql in 5 min interval for ping services.

Current status data means for each host only most latest entry would
be kept in the database, which describe the status (Up/Down) for that host,
at any given time.

"""

from nocout_site_name import *
import mysql.connector
from datetime import datetime, timedelta
import subprocess
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
	"network_status_tables": {
	    "nosql_db": "nocout" # Mongodb database name
	    "sql_db": "nocout_dev" # Sql database name
	    "script": "network_status_tables_migration" # Script which would do all the migrations
	    "table_name": "performance_networkstatus" # Sql table name

	    }
	}
    """
    data_values = []
    values_list = []
    docs = []
    #db = utility_module.mysql_conn(configs=configs)
    """
    start_time variable would store the latest time uptill which mysql
    table has an entry, so the data having time stamp greater than start_time
    would be imported to mysql, only, and this way mysql would not store
    duplicate data.
    """
    #for i in range(len(configs.get('mongo_conf'))):
#    start_time = mongo_module.get_latest_entry(
#	    	db_type='mysql', 
#		    	db=db,
#		    	site=configs.get('mongo_conf')[0][0],
#		    	table_name=configs.get('table_name')
#    )	
#    db.close()

    start_time = None
    end_time = None
    #end_time = datetime.now()
    #start_time = end_time - timedelta(minutes=5)
    #end_time =int(time.mktime(end_time.timetuple()))
    #start_time =int(time.mktime(start_time.timetuple()))
    site_spec_mongo_conf = filter(lambda e: e[0] == nocout_site_name, configs.get('mongo_conf'))[0]
    # Get all the entries from mongodb having timestam0p greater than start_time
    docs = read_data(start_time, end_time, configs=site_spec_mongo_conf, db_name=configs.get('nosql_db'))
    configs1 = config_module.parse_config_obj()
    for conf, options in configs1.items():
	machine_name = options.get('machine')
    for doc in docs:
	#local_time_epoch = utility_module.get_epoch_time(doc.get('local_timestamp'))
	#check_time_epoch = utility_module.get_epoch_time(doc.get('check_time'))
	refer = utility_module.get_epoch_time(doc.get('refer'))
	if doc.get('ds') == 'rta':
		rtmin = doc.get('data')[0].get('min_value')
		rtmax = doc.get('data')[0].get('max_value')
	else:
		rtmin=rtmax=doc.get('data')[0].get('value')
	t = (
	#uuid,
	doc.get('host'),
    	doc.get('service'),
    	machine_name,
	doc.get('site'),
	doc.get('ds'),
	doc.get('data')[0].get('value'),
	rtmin,
	rtmax,
	doc.get('data')[0].get('value'),
	doc.get('meta').get('war'),
	doc.get('meta').get('cric'),
	doc.get('local_timestamp'),
	doc.get('check_time'),
	doc.get('ip_address'),
	doc.get('severity'),
	doc.get('age'),
	refer
	)
	data_values.append(t)
	t=()
    if data_values:
    	insert_data(configs.get('table_name'), data_values,configs=configs)
    	print "Data inserted into my mysql db"
    else:
    	print "No data in mongo db in this time frame for table %s" % (configs.get('table_name'))

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
    docs = []
    #start_time = end_time - timedelta(minutes=10)
    # Connection to mongodb database, `db` is a python dictionary object 
    #db = mongo_module.mongo_conn(
    #    host=kwargs.get('configs')[1],
    #    port=int(kwargs.get('configs')[2]),
    #    db_name=kwargs.get('db_name')
    #)
    """
    if db:
	if start_time is None:
		cur = db.device_network_status.find()
	else:
        	cur = db.device_network_status.find({
            	"local_timestamp": {"$gt": start_time, "$lt": end_time}
        	})
        for doc in cur:
            docs.append(doc)
    """
    memc_obj = db_ops_module.MemcacheInterface()
    key = nocout_site_name + "_network"
    doc_key_len = key + "_len"
    docs = memc_obj.retrieve(key,doc_key_len) 
    return docs


def insert_data(table, data_values,**kwargs):
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
		query = "SELECT COUNT(1) FROM %s " % table +\
                	"WHERE `device_name`='%s' AND `service_name`='%s' AND `data_source`='%s'" %(str(data_values[i][0]),data_values[i][1],data_values[i][4])
		cursor = db.cursor()
        	try:
                	cursor.execute(query)
			result = cursor.fetchone()
		except mysql.connector.Error as err:
        		raise mysql.connector.Error, err
		if result[0]:
			insert_dict['1'].append(data_values[i])
		else:
			insert_dict['0'].append(data_values[i])
	
	if len(insert_dict['1']):
 		query = "UPDATE `%s` " % table
		query += """SET `machine_name`=%s,`site_name`=%s, `current_value`=%s,
		`min_value`=%s,`max_value`=%s, `avg_value`=%s, `warning_threshold`=%s,
		`critical_threshold`=%s, `sys_timestamp`=%s,`check_timestamp`=%s,
		`ip_address`=%s,`severity`=%s,`age`=%s, `refer`=%s
		WHERE `device_name`=%s AND `service_name`=%s AND `data_source`=%s
		"""
		try:
			data_values = map(lambda x: ( x[2],x[3],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12],x[13],x[14],x[15],x[16]) + (x[0],x[1],x[4]),
					 insert_dict.get('1'))

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
            	critical_threshold, sys_timestamp, check_timestamp,ip_address,severity,age,refer) 
           	VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s,%s,%s,%s)
		"""
    		cursor = db.cursor()
    		try:
        		cursor.executemany(query, insert_dict.get('0'))
    		except mysql.connector.Error as err:
				raise mysql.connector.Error, err
    		db.commit()
    		cursor.close()
	db.close()



if __name__ == '__main__':
    main()
