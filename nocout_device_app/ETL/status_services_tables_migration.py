"""
service_status_tables_migration.py
==========================

Script to bulk insert current status data from teramatrix pollers to mysql in 5 min interval

"""


import os
import MySQLdb
import pymongo
from datetime import datetime, timedelta
from rrd_migration import mongo_conn, db_port
import subprocess
import socket


def main(**configs):
    data_values = []
    values_list = []
    docs = []
    db = mysql_conn(configs=configs)
    # Get the time for latest entry in mysql
    #start_time = get_latest_entry(db_type='mysql', db=db, site=configs.get('site'),table_name=configs.get('table_name'))
    utc_time = datetime(1970, 1,1,5,30)


    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=60)
    start_epoch = int((start_time - utc_time).total_seconds())
    end_epoch =  int((end_time - utc_time).total_seconds())
    print start_time,end_time
    docs = read_data(start_epoch, end_epoch, configs=configs)
    print docs
    for doc in docs:
        values_list = build_data(doc)
        data_values.extend(values_list)
    field_names = [
        'device_name',
        'service_name',
        'machine_name',
        'site_name',
        'data_source',
        'current_value',
        'min_value',
        'max_value',
        'avg_value',
        'warning_threshold',
        'critical_threshold',
        'sys_timestamp',
        'check_timestamp',
	'ip_address'
    ]
    if data_values:
    	insert_data(configs.get('table_name'), data_values, configs=configs)
   	print "Data inserted into my mysql db"
    else:
    	print "No data in mongodb in this time frame for table %s" % (configs.get('table_name'))

def read_data(start_time, end_time, **kwargs):

    db = None
    port = None
    #end_time = datetime(2014, 6, 26, 18, 30)
    #start_time = end_time - timedelta(minutes=10)
    docs = [] 
    db = mongo_conn(
        host=kwargs.get('configs').get('host'),
        port=int(kwargs.get('configs').get('port')),
        db_name=kwargs.get('configs').get('nosql_db')
    )
    if db:
        cur = db.device_status_services_status.find({
            "check_timestamp": {"$gt": start_time, "$lt": end_time}
        })
        for doc in cur:
            docs.append(doc)
    return docs

def build_data(doc):
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
	db = mysql_conn(configs=kwargs.get('configs'))
	query = "SELECT * FROM %s " % table +\
                "WHERE `device_name`='%s' AND `site_name`='%s' AND `service_name`='%s' AND `data_source`='%s'" %(str(data_values[0][0]),data_values[0][11],data_values[0][1],data_values[0][12])
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
		WHERE `device_name`=%s AND `site_name`=%s AND `service_name`=%s
		""" 
		try:
			data_values = map(lambda x: x + (x[0], x[11], x[1],x[12],), data_values)
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
    		except MySQLdb.Error, e:
       			raise MySQLdb.Error, e
    		db.commit()
    		cursor.close()

def get_epoch_time(datetime_obj):
    # Get India times (GMT+5.30)
    utc_time = datetime(1970, 1,1, 5, 30)
    if isinstance(datetime_obj, datetime):
        epoch_time = int((datetime_obj - utc_time).total_seconds())
        return epoch_time
    else:
        return datetime_obj

def mysql_conn(db=None, **kwargs):
    try:
        db = MySQLdb.connect(
                host=kwargs.get('configs').get('host'),
                user=kwargs.get('configs').get('user'),
                passwd=kwargs.get('configs').get('sql_passwd'),
                db=kwargs.get('configs').get('sql_db')
        )
    except MySQLdb.Error, e:
        raise MySQLdb.Error, e

    return db
def get_machine_name(machine_name=None):
    try:
        machine_name = socket.gethostname()
    except Exception, e:
        raise Exception(e)

    return machine_name


if __name__ == '__main__':
    main()
