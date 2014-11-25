"""
historical_mysql_export.py
==========================

Provides functionality to export aggregated data into
historical mysql, using bulk insert.
"""

from nocout_site_name import *
import mysql.connector
from mysql.connector import connect


def mysql_export(table, db, data_values):
	data_values = map(lambda e: (e['host'], e['service'], e['site'][:-8], e['site'], e['ip_address'], e['ds'], None, None, e['min'], e['max'], e['avg'], None, None, e['time'].strftime('%s'), e['time'].strftime('%s')), data_values)

	insert_query = "INSERT INTO %s" % table
	insert_query += """
	(device_name, service_name, machine_name, site_name, ip_address, data_source, severity, current_value,
	min_value, max_value, avg_value, warning_threshold, critical_threshold, sys_timestamp, check_timestamp)
	 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
	"""
	cursor = db.cursor()
	try:
		cursor.executemany(insert_query, data_values)
	except mysql.connector.Error as err:
		raise mysql.connector.Error, err
	db.commit()
	cursor.close()


def mysql_conn(mysql_configs=None, db=None):
	try:
		db = connect(host=mysql_configs['host'], user=mysql_configs['user'],
			password=mysql_configs['password'], database=mysql_configs['database'], port=mysql_configs['port'])
	except mysql.connector.Error, err:
		raise mysql.connector.Error, err 

	return db


if __name__ == '__main__':
	#mysql_main()
	print "Script can't be run in stand alone mode"
