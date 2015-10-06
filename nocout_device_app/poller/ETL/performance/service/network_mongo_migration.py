"""
network_mongo_migration.py
==========================

Script to bulk insert data from Teramatrix Pollers into
central mysql db, for network services.
The data in the Teramatrix Pollers is stored in Mongodb.

Network services include : Ping
"""

from nocout_site_name import *
import mysql.connector
from datetime import datetime, timedelta
import subprocess
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
    "site": "nocout_gis_slave",
    "host": "localhost",
    "user": "root",
    "ip": "localhost",
    "sql_passwd": "admin",
    "nosql_passwd": "none",
    "port": 27019 # The port being used by mongodb process
    "network": {
        "nosql_db": "nocout" # Mongodb database name
        "sql_db": "nocout_dev" # Sql database name
        "script": "network_mongo_migration" # Script which would do all the migrations
        "table_name": "performance_performancenetwork" # Sql table name

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

    site_spec_mongo_conf = filter(lambda e: e[0] == nocout_site_name, configs.get('mongo_conf'))[0]
    start_time, end_time,db = None, None,None
    #try:
    #    db = mongo_module.mongo_conn(
    #        host=site_spec_mongo_conf[1],
    #        port=int(site_spec_mongo_conf[2]),
    #        db_name=configs.get('nosql_db')
    #    )
    #except:
     #   sys.stdout.write('Mongodb connection problem\n')
      #  sys.exit(1)
    #end_time = datetime.now()
    # get most latest sys timstamp entry present in mysql
    #time_doc = list(db.sys_timestamp_status.find({'_id': 'performance_networkstatus'}))
    #for doc in time_doc:
     #   start_time = doc.get('sys_timestamp')
    #print start_time,end_time
    db=None
    # Get all the entries from mongodb having timestam0p greater than start_time
    docs = read_data(start_time, end_time, db)
    print '...........'
    print len(docs)
    #for doc in docs:
    #    values_list = build_data(doc)
    #    data_values.append(values_list)
    if docs:
        #insert_data(configs.get('table_name'), data_values, configs=configs)
        insert_data(configs.get('table_name'), docs, configs=configs)
        print "Data inserted into mysql db"
    else:
        print "No data in the mongo db in this time frame"
    

def read_data(start_time, end_time, db):
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
    #start_time = end_time - timedelta(minutes=10)
    # Connection to mongodb database, `db` is a python dictionary object 
    #db = mongo_module.mongo_conn(
    #    host=kwargs.get('configs')[1],
    #    port=int(kwargs.get('configs')[2]),
    #    db_name=kwargs.get('db_name')
    #)
    table_list = ['performance_networkstatus', 'performance_servicestatus',
            'performance_status']
    """
    if db:
        if start_time is None:
            # read data from status, initially
            start_time = end_time - timedelta(minutes=10)
            cur = db.device_network_status.find({"local_timestamp" : { "$gt": start_time, "$lt": end_time}})
        elif (start_time + timedelta(minutes=15)) < end_time:
            # data in mysql is older than mongo data by more than half an hour
            # so we need to read data from live mongo collection, rather than status
            if (start_time + timedelta(days=1)) < end_time:
                # max time range for data sync is 1 day
                start_time = end_time - timedelta(days=1)
            cur = db.network_perf.find({"local_timestamp" : { "$gt": start_time, "$lt": end_time}})
    """
            # we should read data from status rather than live
    current_time = datetime.now()
    key = nocout_site_name + "_network"
    doc_len_key = key + "_len" 
    memc_obj = db_ops_module.MemcacheInterface()
    memc = memc_obj.memc_conn
    start_time = memc.get('performance_networkstatus')
    #print start_time
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
    #cur = db.device_network_status.find({"local_timestamp" : { "$gt": start_time, "$lt": end_time}})
    configs = config_module.parse_config_obj()
    for config, options in configs.items():
        machine_name = options.get('machine')
    for doc in cur:
        if doc.get('ds') == 'rtmin' or doc.get('ds') == 'rtmax':
            continue
        #check_time_epoch = utility_module.get_epoch_time(doc.get('data')[0].get('time'))
        #local_time_epoch = utility_module.get_epoch_time(doc.get('local_timestamp'))
        refer = utility_module.get_epoch_time(doc.get('refer'))
        if doc.get('ds') == 'rta':
            rtmin = doc.get('data')[0].get('min_value')
            rtmax = doc.get('data')[0].get('max_value')
        else:
            rtmin=rtmax=doc.get('data')[0].get('value')
        t = (
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
                doc.get('data')[0].get('time'),
                doc.get('ip_address'),
                doc.get('severity'),
                doc.get('age'),
                refer
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
        if doc.get('ds') == 'rtmin' or doc.get('ds') == 'rtmax':
            break
        check_time_epoch = utility_module.get_epoch_time(entry.get('time'))
        # Advancing local_timestamp/sys_timestamp to next 5 mins time frame
        #local_time_epoch = check_time_epoch + 300
        local_time_epoch = utility_module.get_epoch_time(doc.get('local_timestamp'))
        if doc.get('ds') == 'rta':
            rtmin = entry.get('min_value')
            rtmax = entry.get('max_value')
        else:
            rtmin=rtmax=entry.get('value')
            t = (
                #uuid,
                doc.get('host'),
                doc.get('service'),
                machine_name,
                doc.get('site'),
                doc.get('ds'),
                entry.get('value'),
                rtmin,
                rtmax,
                entry.get('value'),
                doc.get('meta').get('war'),
                doc.get('meta').get('cric'),
                local_time_epoch,
                check_time_epoch,
                doc.get('ip_address'),
            doc.get('severity')
            )
            #values_list.append(t)

    return t

def insert_data(table, data_values, **kwargs):
    """
    Function to insert data into mysql tables

    Args:
        table (str): Table name into which data to be inserted
    data_values: Values in the form of list of tuples

    Kwargs:
        kwargs (dict): Python dict to store connection variables
    """
    db = utility_module.mysql_conn(configs=kwargs.get('configs'))
    query = "INSERT INTO `%s` " % table
    query += """
            (device_name, service_name, machine_name, 
            site_name, data_source, current_value, min_value, 
            max_value, avg_value, warning_threshold, 
            critical_threshold, sys_timestamp, check_timestamp,ip_address,severity,age,refer) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s)
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
