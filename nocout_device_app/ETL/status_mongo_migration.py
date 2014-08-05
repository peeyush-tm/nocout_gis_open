"""
status_mongo_migration.py
==========================

Script to bulk insert data from Teramatrix Pollers into
central mysql db, for status services.
The data in the Teramatrix Pollers is stored in Mongodb.

Status services include : Services which runs once an Hour.
"""


import MySQLdb
from datetime import datetime, timedelta
from rrd_migration import mongo_conn
import mongo_functions
import socket

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
    db = mysql_conn(configs=configs)
    utc_time = datetime(1970, 1,1,5,30)


    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=60)
    start_epoch = int((start_time - utc_time).total_seconds())
    end_epoch =  int((end_time - utc_time).total_seconds())
    #print start_time,end_time
    docs = read_data(start_epoch, end_epoch, configs=configs)
    #print docs
    for doc in docs:
        values_list = build_data(doc)
        data_values.extend(values_list)
    insert_data(configs.get('table_name'), data_values, configs=configs)
    print "Data inserted into performance_performancestatus table"
    

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
    db = mongo_conn(
        host=kwargs.get('configs').get('host'),
        port=int(kwargs.get('configs').get('port')),
        db_name=kwargs.get('configs').get('nosql_db')
    )
    if db:
        cur = db.status_perf.find({
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
	machine_name = get_machine_name()
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

def insert_data(table, data_values, **kwargs):
	"""
	Function to bulk insert data into mysql db

	Args:
	    table (str): Mysql table name
            data_values (list): List of data tuples

	Kwargs:
	    kwargs: Mysqldb connection variables
	"""
	db = mysql_conn(configs=kwargs.get('configs'))
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
    	except MySQLdb.Error, e:
        	raise MySQLdb.Error, e
    	db.commit()
    	cursor.close()

def get_epoch_time(datetime_obj):
    """
    Function to convert python datetime object into
    unix epoch time

    Args:
        datetime_obj (datetime): Python datetime object

    Output:
        Unix epoch time in intteger format
    """
    # Get the time in IST (GMT+5:30)
    utc_time = datetime(1970, 1,1, 5, 30)
    if isinstance(datetime_obj, datetime):
        epoch_time = int((datetime_obj - utc_time).total_seconds())
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
        db = MySQLdb.connect(host=kwargs.get('configs').get('host'), user=kwargs.get('configs').get('user'),
            passwd=kwargs.get('configs').get('sql_passwd'), db=kwargs.get('configs').get('sql_db'))
    except MySQLdb.Error, e:
        raise MySQLdb.Error, e

    return db
def get_machine_name(machine_name=None):
    """
    Function to get fqdn of the machine on which
    Python interpreter is currently executing
    """
    try:
        machine_name = socket.gethostname()
    except Exception, e:
        raise Exception(e)

    return machine_name


if __name__ == '__main__':
    main()
