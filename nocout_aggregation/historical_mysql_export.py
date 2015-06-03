"""
historical_mysql_export.py
==========================

Provides functionality to export aggregated data into
historical mysql, using bulk insert.
"""

from __future__ import absolute_import

import mysql.connector
import imp
from ConfigParser import ConfigParser
from mysql.connector import connect
from operator import itemgetter
from itertools import izip_longest, chain
from celery import Task
from celery.exceptions import WorkerLostError as WLE

from entry import app


class DatabaseTask(Task):
	abstract = True 
	# maintains one connection per database
	connect_pool = {}
	desired_config = ConfigParser()
	desired_config.read('/data01/nocout/data_aggregation/mysql_db.ini')
	
	#@property
	def mysql_cnx(self, machine='historical'):
	    # identifies connection object using machine name
	    connect_key = machine
            mysql_configs = {
                'host': self.desired_config.get(connect_key, 'host'),
                'port': int(self.desired_config.get(connect_key, 'port')),
                'user': self.desired_config.get(connect_key, 'user'),
                'password': self.desired_config.get(connect_key, 'password'),
                'database': self.desired_config.get(connect_key, 'database')
            }
	    if not self.connect_pool.get(connect_key):
	        try:
	            self.connect_pool[connect_key] = connect(**mysql_configs)
	        except mysql.connector.Error, err:
		    print 'Error in Mysql Connection for key %s !!' % connect_key, err
	            #raise mysql.connector.Error, err
	    else:
		# ping mysql server, reconnect if connection is stale
		if not self.connect_pool[connect_key].is_connected():
		    self.connect_pool[connect_key] = connect(**mysql_configs)

	    return self.connect_pool.get(connect_key)


@app.task(base=DatabaseTask, name='mysql_export', ignore_result=True, time_limit=60*4, bind=True)
def mysql_export(self, table, data_values):
	mapped_values = map(lambda e: 
		(e[0], e[1], e[3][:-8], e[3], e[4], e[2], e[5], 
		e[6], e[7], e[8], e[9], e[10], e[11], e[12], e[13], e[15]), 
		data_values)

	insert_query = "INSERT INTO %s" % table
	insert_query += """
	(device_name, service_name, machine_name, site_name, ip_address, data_source, 
	severity, current_value, min_value, max_value, avg_value, warning_threshold, 
	critical_threshold, sys_timestamp, check_timestamp, refer)
	 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
	"""
	cnx = mysql_export.mysql_cnx()
	cursor = cnx.cursor()
	try:
		cursor.executemany(insert_query, mapped_values)
	except (mysql.connector.Error, WLE) as exc:
		cursor.close()
		print 'Mysql Export Error, retrying...', exc
		raise self.retry(args=(table, data_values), max_retries=1, 
			countdown=20, exc=exc)
	else:
		cnx.commit()
		cursor.close()
		print 'Data exported'
	#db.close()


def mysql_export_device_availability(table, db, data_values):
	data_values = map(lambda e: 
		(e['host'], e['service'], e['site'][:-8], e['site'], e['ip_address'], 
		e['ds'], e.get('severity'), e.get('current_value'), e['min'], e['max'], 
		e['avg'], e['war'], e['cric'], e['time'].strftime('%s'), 
		e['check_time'].strftime('%s')), data_values)

	insert_query = "INSERT INTO %s" % table
	insert_query += """
	(device_name, service_name, machine_name, site_name, ip_address, 
	data_source, severity, current_value, min_value, max_value, avg_value, 
	warning_threshold, critical_threshold, sys_timestamp, check_timestamp)
	VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
	"""
	cursor = db.cursor()
	try:
		cursor.executemany(insert_query, data_values)
	except mysql.connector.Error as err:
		raise mysql.connector.Error, err
	db.commit()
	cursor.close()
	db.close()

def mysql_conn(mysql_configs=None, db=None):
	try:
		db = connect(host=mysql_configs['host'], user=mysql_configs['user'],
			password=mysql_configs['password'], 	
			database=mysql_configs['database'], port=mysql_configs['port'])
	except mysql.connector.Error, err:
		raise mysql.connector.Error, err 

	return db


@app.task(base=DatabaseTask, name='get_inventory_devices')
def get_active_inventory_devices(machine=None, all=True):
	# number of devices for single read query
	DEVICE_SET = app.conf.DEVICE_SET
	devices = []
	if all:
		query = ( 
		    	"SELECT device_name FROM device_device "
		    	"WHERE device_device.is_added_to_nms = 1"
		)
	else:
		query = """
			SELECT D.device_name FROM device_device D LEFT JOIN 
			machine_machine M ON D.machine_id = M.id WHERE 
			M.name = '{0}' AND D.is_added_to_nms = 1
			""".format(str(machine))

	if get_active_inventory_devices.mysql_cnx():
		try:
			cnx = get_active_inventory_devices.mysql_cnx()
			cursor = cnx.cursor()
			cursor.execute(query)
			#docs = dict_rows(cursor)
			devices = cursor.fetchall()
			cursor.close()
			print 'no of devices --', len(devices)
		except mysql.connector.Error as err:
		        print 'Mysql Error in get devices ', err
	for device_set in izip_longest(*[iter(devices)] * DEVICE_SET, fillvalue=''):
		yield chain.from_iterable(device_set)
	print '### Completed ###'


@app.task(base=DatabaseTask, name='mysql_read', time_limit=60*8, bind=True)
def read_data(self, device_list, table, start_time, end_time, machine='historical'):
	#db = mysql_conn(mysql_configs=mysql_configs)
	docs = []
	kwargs = {
		'start_time': start_time,
		'end_time' : end_time,
		'table': table,
		'devices': tuple(device_list)
		}
	query = """
		SELECT device_name, service_name, data_source, site_name, ip_address, 
		severity, current_value, min_value, max_value, avg_value, warning_threshold, 
		critical_threshold, sys_timestamp, check_timestamp, age, refer 
		FROM {table} WHERE device_name IN {devices} AND 
		sys_timestamp BETWEEN {start_time} AND {end_time}
		""".format(**kwargs)
	if read_data.mysql_cnx(machine=machine):
		try:
			cnx = read_data.mysql_cnx(machine=machine)
			cursor = cnx.cursor()
			cursor.execute(query)
			#docs = dict_rows(cursor)
			docs = cursor.fetchall()
			cursor.close()
		except (mysql.connector.Error, WLE) as err:
			print 'Mysql Read Error, retrying...'
			raise self.retry(
					args=(
						device_list, 
						table, start_time, 
						end_time), 
					kwargs={'machine': machine},
					max_retries=1, 
					countdown=20, 
					exc=err)
	print 'devices %s, %s docs', len(device_list), len(docs)
	return sorted(docs, key=itemgetter(0))


def dict_rows(cur):
	desc = cur.description
	return [dict(zip([col[0] for col in desc], row)) for row in cur.fetchall()]


if __name__ == '__main__':
	#mysql_main()
	print "Script can't be run in stand alone mode"
