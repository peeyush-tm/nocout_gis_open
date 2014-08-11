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

mongo_module = imp.load_source('mongo_functions', '/opt/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)

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
	"network_status_tables": {
	    "nosql_db": "nocout" # Mongodb database name
	    "sql_db": "nocout_dev" # Sql database name
	    "scripit": "network_status_tables_migration" # Script which would do all the migrations
	    "table_name": "performance_networkstatus" # Sql table name

	    }
	}
    """
    data_values = []
    values_list = []
    docs = []
    db = mysql_conn(configs=configs)
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
    	# Get all the entries from mongodb having timestam0p greater than start_time
    	docs = read_data(start_time, end_time, configs=configs.get('mongo_conf')[i], db_name=configs.get('nosql_db'))
    	for doc in docs:
        	values_list = build_data(doc)
        	data_values.extend(values_list)
    if data_values:
    	insert_data(configs.get('table_name'), data_values, configs=configs)
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
    db = mongo_module.mongo_conn(
        host=kwargs.get('configs')[1],
        port=int(kwargs.get('configs')[2]),
        db_name=kwargs.get('db_name')
    )
    if db:
	if start_time is None:
		cur = db.device_network_status.find()
	else:
        	cur = db.device_network_status.find({
            	"check_time": {"$gt": start_time, "$lt": end_time}
        	})
        for doc in cur:
            docs.append(doc)
    return docs

def build_data(doc):
    """
    Function to make tuples out of python dict,
    data would be stored in mysql db in the form of python tuples

    Args:
	doc (dict): Single mongodb entry

    Returns:
        A list of tuples, one tuple corresponds to a single row in mysql db
    """
    values_list = []
    #uuid = get_machineid()
    machine_name = get_machine_name()
    local_time_epoch = get_epoch_time(doc.get('local_timestamp'))
    # Advancing local_timestamp/sys_timetamp to next 5 mins time frame
    local_time_epoch += 300
    for entry in doc.get('data'):
	check_time_epoch = get_epoch_time(entry.get('time'))
        t = (
       		#uuid,
                doc.get('host'),
                doc.get('service'),
                machine_name,
                doc.get('site'),
                doc.get('ds'),
                entry.get('value'),
                entry.get('value'),
                entry.get('value'),
                entry.get('value'),
                doc.get('meta').get('war'),
                doc.get('meta').get('cric'),
                local_time_epoch,
                check_time_epoch,
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
	db = mysql_conn(configs=kwargs.get('configs'))
	query = "SELECT * FROM %s " % table +\
                "WHERE `device_name`='%s' AND `site_name`='%s' AND `service_name`='%s'" %(str(data_values[0][0]),
		data_values[0][3],data_values[0][1])
        cursor = db.cursor()
        try:
                cursor.execute(query)
		result = cursor.fetchone()
        except MySQLdb.Error, e:
                raise MySQLdb.Error, e
        db.commit()
	
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
			data_values = map(lambda x: x + (x[0], x[3], x[1],x[4]), data_values)
                	cursor.executemany(query, data_values)
		except MySQLdb.Error, e:
                        raise MySQLdb.Error, e
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

def get_epoch_time(datetime_obj):
    """
    Function to convert datetime_obj into unix
    epoch time

    Args:
        datetime_obj (datetime): Python datetime object

    Returns:
        Unix epoch time in integer
    """
    # Get India times (GMT+5.30)
    #utc_time = datetime(1970, 1,1, 5, 30)
    if isinstance(datetime_obj, datetime):
	start_epoch = datetime_obj
        epoch_time = int(time.mktime(start_epoch.timetuple()))

        return epoch_time
    else:
        return datetime_obj

def mysql_conn(db=None, **kwargs):
    """
    Function to create connection to mysql database

    Args:
        db (dict): Mysqldb connection object

    Kwargs:
        kwargs (dict): Dict to store mysql connection variables
    """
    try:
        db = mysql.connector.connect(
                user=kwargs.get('configs').get('user'),
                passwd=kwargs.get('configs').get('sql_passwd'),
                host=kwargs.get('configs').get('ip'),
                db=kwargs.get('configs').get('sql_db')
        )
    except mysql.connector.Error as err:
        raise mysql.connector.Error, err

    return db

def get_machineid():
    uuid = None
    proc = subprocess.Popen(
        'sudo -S dmidecode | grep -i uuid',
        stdout=subprocess.PIPE,
        shell=True
    )
    cmd_output, err = proc.communicate()
    if not err:
        uuid = cmd_output.split(':')[1].strip()
    else:
        uuid = err

    return uuid


def get_machine_name(machine_name=None):
    """
    Function get the fully qualified domain name of the machine
    on which Python interpreter is executing
    """
    try:
        machine_name = socket.gethostname()
    except Exception, e:
        raise Exception(e)

    return machine_name


if __name__ == '__main__':
    main()
