"""
service_mongo_migration.py
==========================

Script to bulk insert data from Teramatrix Pollers into
central mysql db, for the services running on hosts,
every 5 minutes
The data in the Teramatrix pollers is stored in mongodb.

Services include: All services except Ping
"""

from nocout_site_name import *
import mysql.connector
from datetime import datetime, timedelta
import subprocess
import imp
import sys
import memcache
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
	"network": {
	    "nosql_db": "nocout" # Mongodb database name
	    "sql_db": "nocout_dev" # Sql database name
	    "script": "service_mongo_migration" # Script which would do all the migrations
	    "table_name": "performance_performanceservice" # Sql table name

	    }
	}
    """
    data_values = []
    values_list = []
    docs = []
    """
    start_time variable would store the latest time uptill which mysql
    table has an entry, so the data having time stamp greater than start_time
    would be imported to mysql, only, and this way mysql would not store
    duplicate data.
    """

    db = None
    try:
    	db = utility_module.mysql_conn(configs=configs)
    except Exception,e:
	print e
	return
    docs = read_data()
    print len(docs)
    if docs:
    	while docs:
    		insert_data(configs.get('table_name'), docs[0:50000],db,configs)
		docs = docs[50000:]
    		print "Data inserted into my mysql db"
		time.sleep(10)
	else:
    		print "No data in mongo db in this time frame"


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
    key = nocout_site_name + "_service"
    current_time = datetime.now()
    doc_len_key = key + "_len"
    memc_obj = db_ops_module.MemcacheInterface()
    memc = memc_obj.memc_conn
    start_time = memc.get('performance_servicestatus')
    print 'in service'
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
    	cur=memc_obj.retrieve(key,doc_len_key)
    #print cur
    configs = config_module.parse_config_obj()
    for config, options in configs.items():
	    machine_name = options.get('machine')
    for doc in cur:
        #check_time_epoch = utility_module.get_epoch_time(doc.get('data')[0].get('time'))
        #local_time_epoch = utility_module.get_epoch_time(doc.get('local_timestamp'))
        t = (
            #uuid,
            doc.get('host'),
            doc.get('service'),
            machine_name,
            doc.get('site'),
            doc.get('ds'),
            doc.get('data')[0].get('value'),
            doc.get('data')[0].get('value'),
            doc.get('data')[0].get('value'),
            doc.get('data')[0].get('value'),
            doc.get('meta').get('war'),
            doc.get('meta').get('cric'),
            doc.get('local_timestamp'),
            doc.get('data')[0].get('time'),
            doc.get('ip_address'),
            doc.get('severity'),
            doc.get('age')
            )
        docs.append(t)
        t =()
    return docs

def build_data(doc):
    """
    Function to make tuples out of python dict,
    data would be stored in mysql db in the form of python tuples

    Args:
	doc (dict): Single mongodb entry

    Kwargs:

    Returns:
        A list of tuples, one tuple corresponds to a single row in mysql db
    """
    values_list = []
    #uuid = get_machineid()
    configs = config_module.parse_config_obj()
    for config, options in configs.items():
	    machine_name = options.get('machine')
    for entry in doc.get('data'):
	check_time_epoch = utility_module.get_epoch_time(entry.get('time'))
	local_time_epoch = utility_module.get_epoch_time(doc.get('local_timestamp'))
	# Advancing local_timestamp/sys_timestamp to next 5 mins time frame
	#local_time_epoch = check_time_epoch + 300
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
        #values_list.append(t)
        #t = ()
    return t

def insert_data(table, data_values, db,configs):
    """
    Function to insert data into mysql tables

    Args:
        table (str): Table name into which data to be inserted
	data_values: Values in the form of list of tuples

    Kwargs:
        kwargs (dict): Python dict to store connection variables
    """  
    if not db.is_connected():
	db = utility_module.mysql_conn(configs=configs)
    query = "INSERT INTO `%s` " % table
    query += """
            (device_name, service_name, machine_name, 
            site_name, data_source, current_value, min_value, 
            max_value, avg_value, warning_threshold, 
            critical_threshold, sys_timestamp, check_timestamp,ip_address,severity,age) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s,%s,%s)
            """
    cursor = db.cursor()
    try:
        cursor.executemany(query, data_values)
    except mysql.connector.Error as err:
        raise mysql.connector.Error, err
    db.commit()
    cursor.close()
    db.close()


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



if __name__ == '__main__':
    main()
