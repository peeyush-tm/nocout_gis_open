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

    site_spec_mongo_conf = filter(lambda e: e[0] == nocout_site_name, configs.get('mongo_conf'))[0]
    start_time, end_time = None, None
    try:
        db = mongo_module.mongo_conn(
            host=site_spec_mongo_conf[1],
            port=int(site_spec_mongo_conf[2]),
            db_name=configs.get('nosql_db')
        ) 
    except:
        sys.stdout.write('Mongodb connection problem\n')
        sys.exit(1)
    end_time = datetime.now()
    end_epoch = int(end_time.strftime('%s'))
    # get most latest sys timestamp entry present in mysql for interface services
    time_doc = list(db.sys_timestamp_status.find({'_id': 'performance_status'}))
    for doc in time_doc:
        start_time = doc.get('sys_timestamp')
        start_epoch = int(start_time.strftime('%s'))
    print start_time,end_time
    
    docs = read_data(start_epoch, end_epoch, db)
    for doc in docs:
        values_list = build_data(doc)
        data_values.extend(values_list)
    if data_values:
        insert_data(configs.get('table_name'), data_values, configs=configs)
        print "Data inserted into performance_performancestatus table"
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
    docs = [] 
    #db = mongo_module.mongo_conn(
    #    host=kwargs.get('configs')[1],
    #    port=int(kwargs.get('configs')[2]),
    #    db_name=kwargs.get('db_name')
    #) 
    if db:
        if start_time is None:
            # read data from status, initially
            start_time = end_time - 3600
            cur = db.device_status_services_status.find({
                "check_timestamp": {"$gt": start_time, "$lt": end_time}})
        elif (end_time - start_time) >= 7200:
            # data in mysql is older than mongo data by more thn 2 hours
            # so we need to read data from live mongo collection rather than status collection
            if (end_time - start_time) > 86400:
                # max time range for data sync is 1 day
                start_time = end_time - 86400
            cur = db.status_perf.find({
                "check_timestamp": {"$gt": start_time, "$lt": end_time}})
        else:
            # read data from status collection, normally
            cur = db.device_status_services_status.find({
                "check_timestamp": {"$gt": start_time, "$lt": end_time}})
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

def insert_data(table, data_values, **kwargs):
    """
    Function to bulk insert data into mysql db

    Args:
        table (str): Mysql table name
            data_values (list): List of data tuples

    Kwargs:
        kwargs: Mysqldb connection variables
    """
    db = utility_module.mysql_conn(configs=kwargs.get('configs'))
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
