"""
network_events_mongo_migration.py

File contains code for migrating the embeded mongodb data to mysql database.This File is specific to events data and only migrates the data for events

"""

from nocout_site_name import *
import mysql.connector
from datetime import datetime
from datetime import timedelta
from events_rrd_migration import get_latest_event_entry
import imp

#from handlers.db_ops import *

mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)
db_ops_module = imp.load_source('db_ops', '/omd/sites/%s/lib/python/handlers/db_ops.py' % nocout_site_name)

def main(**configs):
    """

    Main function for the migrating the data from mongodb to mysql db.Latest record time in mysql is carried out and from latest record time to
    current time all records are migrated from mongodb to mysql.
    Args: Multiple arguments for configuration
    Kwargs: None
    Return : None
    Raise : No exception

    """
    data_values = []
    values_list = []
    docs = []

    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=2)
    start_time, end_time = start_time - timedelta(minutes=1), end_time - timedelta(minutes=1)
    start_time, end_time = start_time.replace(second=0), end_time.replace(second=0)
    start_time, end_time = int(start_time.strftime('%s')), int(end_time.strftime('%s'))

    # Get site specific configurations for Mongodb connection
    # Ex conf : ('ospf4_slave_1', 'localhost', 27018)
    site_spec_mongo_conf = filter(lambda e: e[0] == nocout_site_name, configs.get('mongo_conf'))[0]
   
    # Read data function reads the data from mongodb and insert into mysql
    docs = read_data(start_time, end_time,configs=site_spec_mongo_conf, db_name=configs.get('nosql_db'))
    print 'Found %s values for %s' % (len(docs), configs.get('table_name'))
    for doc in docs:
        values_list = build_data(doc)
        data_values.extend(values_list)
    if data_values:
        insert_data(configs.get('table_name'), data_values, configs=configs)
        print "Data inserted into mysql table %s between %s -- %s" % (configs.get('table_name'), start_time, end_time)
    else:
        print "No data in the mongo db between %s -- %s" % (start_time, end_time)

def read_data(start_time, end_time, **kwargs):
    """
    Function reads the data from mongodb specific event tables for ping services and return the document
    Args: start_time(check_timestamp field in mongodb record is checked with start_time and end_time and data is extracted only
          for time interval)
    Kwargs: end_time (time till to collect the data)
    Return : document containing data for this time interval
    Raise : No exception

    """
    db = None
    port = None
    docs = []
    """
    db = mongo_module.mongo_conn(
        host=kwargs.get('configs')[1],
        port=int(kwargs.get('configs')[2]),
        db_name=kwargs.get('db_name')
    )
    """
    key = nocout_site_name + "_network_event1"
    doc_len_key = key + "_len"
    memc_obj = db_ops_module.MemcacheInterface()
    cur=memc_obj.retrieve(key,doc_len_key)

    key = nocout_site_name + "_network_event2"
    doc_len_key = key + "_len"
    cur1=memc_obj.retrieve(key,doc_len_key)

    cur.extend(cur1)



    #if db:
    #        cur = db.nocout_host_event_log.find({
    #            "sys_timestamp": {"$gte": start_time, "$lt": end_time}
    #        })
    for doc in cur:
        docs.append(doc)
    return docs

def build_data(doc):
    """
    Function builds the data collected from mongodb for events according to mysql table schema and return the formatted record
    Args: doc (document fetched from the mongodb database for specific time interval)
    Kwargs: None
    Return : formatted document containing data for multiple devices
    Raise : No exception
    """
    values_list = []
    configs = config_module.parse_config_obj()
    for config, options in configs.items():
        machine_name = options.get('machine')
    t = (
        doc.get('device_name'),
    doc.get('service_name'),
        doc.get('check_timestamp'),
    doc.get('check_timestamp'),
    doc.get('current_value'),
    doc.get('min_value'),
    doc.get('max_value'),
    doc.get('avg_value'),
        doc.get('warning_threshold'),
    doc.get('critical_threshold'),    
        doc.get('description'),
        doc.get('severity'),
        doc.get('site_name'),
    doc.get('data_source'),
    doc.get('ip_address'),
    machine_name
    )
    values_list.append(t)
    t = ()
    return values_list

def insert_data(table,data_values,**kwargs):
    """
    Function insert the formatted record into mysql table for multiple devices
    Args: table (mysql table on which we have to insert the data.table information is fetched from config.ini)
    Kwargs: data_values (list of formatted doc )
    Return : None
    Raise : MYSQLdb.error

    """
    db = utility_module.mysql_conn(configs=kwargs.get('configs'))
    query = 'INSERT INTO `%s` ' % table
    query += """
        (device_name,service_name,sys_timestamp,check_timestamp,
        current_value,min_value,max_value,avg_value,warning_threshold,
        critical_threshold,description,severity,site_name,data_source,
        ip_address,machine_name)
        VALUES(%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
