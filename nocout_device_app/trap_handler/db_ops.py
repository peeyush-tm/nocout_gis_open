#!/usr/bin/python

""" Module for database connections"""

from datetime import datetime
from mysql.connector import connect
import os
from pprint import pprint
from redis import StrictRedis


try:
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	BASE_CONF = os.path.join(BASE_DIR, 'base_conf.py')
except OSError as exc:
	# TODO: log the error
	print exc


class ConnectionBase(object):
	""" Base class to handle database connections"""

	def __init__(self, from_conf=BASE_CONF, **kw):
		self.configs = {}

		try:
			execfile(from_conf, self.configs)
		except Exception as exc:
			# TODO: log the exc
			print 'Error in execfile: {0}'.format(exc)

	def mysql_cnx(self, db_name=None):
		mysql_config = self.configs.get(db_name)

		try:
			mysql_db = connect(**mysql_config)
		except Exception as exc:
			mysql_db = None
			print 'Error in mysql conn: {0}'.format(exc)

		return mysql_db

	def redis_cnx(self, db_name=None):
		redis_config = self.configs.get(db_name)
		# TODO: Use sentinel to make connection to main
		try:
			redis_db = StrictRedis(**redis_config) 
		except Exception as exc:
			redis_db = None
			print 'Error redis conn: {0}'.format(exc)

		return redis_db


class ExportTraps(object):

	def __init__(self, **kw):

		self.conn_base = ConnectionBase()

	def do_work(self, traps, mark_inactive=None, latest_id=None):
		""" Handles inserts/updates for traps"""

		insert_table = 'alert_center_historyalarms_v2'
		update_table = 'alert_center_statusalarms_v2'

		#print 'my traps: {0}'.format(pprint(traps[:5]))
		# TODO: use 2 concurrent threads for insert/update ops
		inserted = self.insert_traps(traps, insert_table)
		updated = self.update_traps(traps, update_table, mark_inactive=mark_inactive)
		
		if inserted and updated:
			# TODO: if ops are successful, update the processed_traps_info
			self.update_id(latest_id)

	def exec_qry(self, qry, data=None, many=True, db_name='application_db'):
		mysql_cnx = self.conn_base.mysql_cnx(db_name=db_name)
		cursor = mysql_cnx.cursor()
		if many:
			cursor.executemany(qry, data)
		else:
			cursor.execute(qry)
		mysql_cnx.commit()
		cursor.close()

	def update_id(self, id):
		""" Updates the id, upto which we have prcoessed traps successfully"""

		qry = """
		UPDATE processed_traps_id 
		SET processed_row = {0},timestamp = '{1}'""".format(id, datetime.now())
		self.exec_qry(qry, many=False, db_name='snmptt_db')

	def update_traps(self, traps, table, mark_inactive=None, columns=None):
		updated = True
		default_columns = (
				'device_name', 'ip_address', 'trapoid', 'eventname',
				'eventno', 'severity', 'uptime', 'traptime',
				'description', 'alarm_count', 'first_occurred',
				'last_occurred', 'is_active'
				)
		columns = columns if columns else default_columns
		# we don't need to update all the columns
		update_columns = (
				'severity', 'uptime', 'traptime',
				'description', 'last_occurred', 'is_active'
				)

		p0 = "INSERT INTO %(table)s" % {'table': table}
		p1 = ' (%s)' % ','.join(columns)
		p2 = ' , '.join(map(lambda x: ' %('+ x + ')s', columns))
		p3 = ' , '.join(map(lambda x: x + ' = VALUES(' + x + ')', update_columns))
		# incr count of trap
		p3 = ''.join([p3, ', alarm_count = alarm_count + 1'])
		qry = ''.join(
				[p0, p1, ' VALUES (', p2, ') ON DUPLICATE KEY UPDATE ', p3]
				)

		# qry for updating `is_active` flag to 0

		# TODO: need to handle this case in a more pythonic way
		if len(mark_inactive) == 1:
			mark_inactive_qry = """
			UPDATE {0} SET is_active = 0 WHERE (ip_address, trapoid) IN 
			({1})""".format(table, mark_inactive[0])
		elif len(mark_inactive)> 1:
			mark_inactive_qry = """
			UPDATE {0} SET is_active = 0 WHERE (ip_address, trapoid) IN 
			{1}""".format(table, tuple(mark_inactive))

		#print 'mark_inactive_qry: {0}'.format(mark_inactive_qry)

		if traps:
			try:
				self.exec_qry(qry, traps)
				self.exec_qry(mark_inactive_qry, many=False)
			except Exception as exc:
				updated = False
				print 'Exc in mysql trap update: {0}'.format(exc)
		return updated

	def insert_traps(self, traps, table, columns=None):
		inserted = True
		default_columns = (
				'device_name', 'ip_address', 'trapoid', 'eventname',
				'eventno', 'severity', 'uptime', 'traptime',
				'description', 'alarm_count', 'first_occurred',
				'last_occurred', 'is_active'
				)
		columns = columns if columns else default_columns

		p0 = "INSERT INTO %(table)s" % {'table': table}
		p1 = ' (%s) ' % ','.join(columns)
		p2 = ' , '.join(map(lambda x: ' %('+ x + ')s', columns))
		qry = ''.join([p0, p1, ' VALUES (', p2, ') '])

		if traps:
			try:
				self.exec_qry(qry, traps)
			except Exception as exc:
				inserted = False
				print 'Exc in mysql trap insert: {0}'.format(exc)
		return inserted


if __name__ == '__main__':
	db_cls = ConnectionBase()
	print db_cls.mysql_cnx(db_name='snmptt_db')
