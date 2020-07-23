"""
network_events_status_mongo_migration.py
========================================

Script to bulk insert current events status data from
pollers to mysql in 5 min interval for ping services.

Current status data means for each (host, service, severity), only most latest entry would
be kept in the database, which describes the event for that host,
at any given time.

"""

from nocout_site_name import *
import mysql.connector
from datetime import datetime, timedelta
import imp

mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

def main(**configs):
    """
    The entry point for the all the functions in this file,
    calls all the appropriate functions in the file

    Kwargs:
        configs (dict): A python dictionary containing object key identifiers
    as configuration variables, read from main configuration file <site_name>.ini
    Example:
        {
    "site": "nocout_gis_subordinate",
    "host": "localhost",
    "user": "root",
    "ip": "localhost",
    "sql_passwd": "admin",
    "nosql_passwd": "none",
    "port": 27019 # The port being used by mongodb process
    "network_event_status": {
        "nosql_db": "nocout" # Mongodb database name
        "sql_db": "nocout_dev" # Sql database name
        "script": "network_events_status_mongo_migration" # Script which would do all the migrations
        "table_name": "performance_eventnetworkstatus" # Sql table name

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

    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=2)
    start_time, end_time = start_time - timedelta(minutes=1), end_time - timedelta(minutes=1)
    start_time, end_time = start_time.replace(second=0), end_time.replace(second=0)
    start_time, end_time = int(start_time.strftime('%s')), int(end_time.strftime('%s'))
    # Get site specific mongo conf
    site_spec_mongo_conf = filter(lambda e: e[0] == nocout_site_name, configs.get('mongo_conf'))[0]
    # Get all the entries from mongodb having timestam0p greater than start_time
    docs = read_data(start_time, end_time, configs=site_spec_mongo_conf, 
            db_name=configs.get('nosql_db'))
    machine_name = configs.get('machine')
    for doc in docs:
        local_time_epoch = doc.get('sys_timestamp')
        check_time_epoch = doc.get('check_timestamp')
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
            check_time_epoch,
            check_time_epoch,
            doc.get('ip_address'),
            doc.get('severity'),
            doc.get('description')
        )
        data_values.append(t)
        t=()
    if data_values:
        insert_data(configs.get('table_name'), data_values,configs=configs)
        print "Data inserted into %s" % configs.get('table_name')
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
            cur = db.network_event_status.find()
        else:
            print start_time, end_time
            cur = db.network_event_status.find({
                "sys_timestamp": {"$gt": start_time, "$lt": end_time}
                })
        for doc in cur:
            docs.append(doc)
    return docs


def insert_data(table, data_values,**kwargs):
    """
        Function to bulk insert data into mysqldb

    Args:
        table (str): Mysql table to which to be inserted
        data_value (list): List of data tuples

    Kwargs (dict): Dictionary to hold connection variables
    """
    #print 'Len Data Values'
    #print len(data_values)
    insert_dict = {'0':[],'1':[]}
    db = utility_module.mysql_conn(configs=kwargs.get('configs'))
    for index, entry in enumerate(data_values):
        query = "SELECT severity FROM %s " % table +\
                    "WHERE `device_name`='%s' " % str(entry[0])+\
                    "AND `service_name`='%s'" % str(entry[1])+\
                    "AND `data_source`='%s'" % str(entry[4])
        cursor = db.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()
        except mysql.connector.Error as err:
            raise mysql.connector.Error, err

        if result:
            #print 'result'
            #print result
            # Add the entry for updation
            insert_dict['1'].append(entry)
        else:
            # Insert the new event entry
            insert_dict['0'].append(entry)
    
    if len(insert_dict['1']):
        query = "UPDATE `%s` " % table
        query += """SET `site_name`=%s, `machine_name`=%s, `current_value`=%s,
        `min_value`=%s,`max_value`=%s, `avg_value`=%s, `warning_threshold`=%s,
        `critical_threshold`=%s, `sys_timestamp`=%s,`check_timestamp`=%s,
        `ip_address`=%s,`severity`=%s, `description`=%s
        WHERE `device_name`=%s AND `service_name`=%s AND `data_source`=%s
        """
        try:
            data_values = map(lambda x: ( x[3], x[2], x[5], x[6], x[7], x[8], x[9], x[10], x[11],
                x[12], x[13], x[14], x[15]) + (x[0], x[1], x[4]), insert_dict.get('1'))
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
                critical_threshold, sys_timestamp, check_timestamp, ip_address, severity, description) 
               VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s, %s, %s)
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
