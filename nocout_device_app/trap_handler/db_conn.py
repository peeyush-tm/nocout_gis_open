
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

	def do_work(self, current_traps=None,clear_traps=None, mark_inactive=None, latest_id=None, flag=None, history_traps=None):
		""" Handles inserts/updates for traps"""

		insert_table = 'alert_center_historyalarms'
		current_table = 'alert_center_currentalarms'
		clear_table = 'alert_center_clearalarms'
		updated = False
		inserted = False
		# TODO: use 2 concurrent threads for insert/update ops
		if history_traps :
			inserted = self.insert_traps(history_traps, insert_table)
		if current_traps and flag is not 'update':
			table = current_table
                        current_mark_inactive = filter(lambda x: x[2] == 'clear' ,mark_inactive)
			updated = self.update_traps(current_traps, 
					table, 
					mark_inactive=current_mark_inactive,
					mask_table=clear_table,
					flag=flag
					)
		if clear_traps and flag is not 'update':
			table = clear_table
                        clear_mark_inactive = filter(lambda x: x[2] != 'clear' ,mark_inactive)
			updated = self.update_traps(
					clear_traps, 
					table, 
					mark_inactive=clear_mark_inactive,
					mask_table=current_table,
					flag=flag
					)
	
		if current_traps and flag is 'update' :
			table = current_table
			updated = self.update_trap_count(current_traps, table)
		if clear_traps and flag is 'update':
                        table = clear_table
			updated = self.update_trap_count(clear_traps, table)
		# Check this again ..
		if inserted and updated:
			# TODO: if ops are successful, update the processed_traps_info
			if flag != 'event':
			    self.update_id(latest_id)

	def exec_qry(self, qry, data=None, many=True, db_name='application_db'):
		try:
		    mysql_cnx = self.conn_base.mysql_cnx(db_name=db_name)
		    cursor = mysql_cnx.cursor()
		    if many:
			cursor.executemany(qry, data)
		    elif data :
			cursor.execute(qry,data)
		    else:
			cursor.execute(qry)
		    mysql_cnx.commit()
		    cursor.close()
		except Exception,e:
		    print e


	def update_id(self, id):
		""" Updates the id, upto which we have prcoessed traps successfully"""

		qry = """
		UPDATE processed_traps_id 
		SET processed_row = {0},timestamp = '{1}'""".format(id, datetime.now())
		self.exec_qry(qry, many=False, db_name='snmptt_db')

	def update_traps(self, traps, table, mark_inactive=None, columns=None,mask_table=None,flag=None):
		updated = True
		default_columns = (
				'device_name', 'ip_address', 'trapoid', 'eventname',
				'eventno', 'severity', 'uptime', 'traptime',
				'description', 'alarm_count', 'first_occurred',
				'last_occurred', 'is_active', 'sia', 'customer_count'
				)
		columns = columns if columns else default_columns
		# we don't need to update all the columns
		update_columns = (
				'severity', 'uptime', 'traptime',
				'description', 'last_occurred', 'is_active', 'sia', 'customer_count'
				)

		p0 = "INSERT INTO %(table)s" % {'table': table}
		p1 = ' (%s)' % ','.join(columns)
		p2 = ' , '.join(map(lambda x: ' %('+ x + ')s', columns))
		p3 = ' , '.join(map(lambda x: x + ' = VALUES(' + x + ')', update_columns))
		qry = ''.join(
				[p0, p1, ' VALUES (', p2, ') ON DUPLICATE KEY UPDATE ', p3] 
				)
		if flag == 'event' or flag == 'wimax_trap':
		    distinct_key = 'eventname'
		elif flag == 'trap':
		     distinct_key = 'trapoid' 
		# qry for updating `is_active` flag to 0
		if len(mark_inactive) == 1:
			#mark_update_columns = ('ip_address','%s' % distinct_key,'severity')
			mark_inactive_qry = """
			UPDATE {0} SET is_active = 0 WHERE (ip_address, {1}) IN 
			({2})""".format(mask_table,distinct_key, mark_inactive[0][:-1])
		elif len(mark_inactive)> 1:
			#mark_update_columns = ('ip_address','%s' % distinct_key,'severity')
                        mark_inactive = map(lambda x: x[:-1],mark_inactive)
			mark_inactive_qry = """
			UPDATE {0} SET is_active = 0 WHERE (ip_address, {1}) IN 
			{2}""".format(mask_table, distinct_key,tuple(mark_inactive))

		#print 'mark_inactive_qry: {0}'.format(mark_inactive_qry)

		if traps:
			try:
				self.exec_qry(qry, traps,db_name='snmptt_db')
				if mark_inactive:
					#p3 = ' , '.join(map(lambda x: x + ' = VALUES(' + x + ')', mark_update_columns))
					#mark_inactive_qry = ''.join(
					#[	p0, p1, ' VALUES (', p2, ') ON DUPLICATE KEY UPDATE ',p3]
					#)
					self.exec_qry(mark_inactive_qry, many=False,db_name='snmptt_db')
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
				'last_occurred', 'is_active', 'sia', 'customer_count'
				)
		columns = columns if columns else default_columns
		p0 = "INSERT INTO %(table)s" % {'table': table}
		p1 = ' (%s) ' % ','.join(columns)
		p2 = ' , '.join(map(lambda x: ' %('+ x + ')s', columns))
		qry = ''.join([p0, p1, ' VALUES (', p2, ') '])
		if traps:
			try:
				self.exec_qry(qry, traps, db_name='snmptt_db')
			except Exception as exc:
				inserted = False
				print 'Exc in mysql trap insert: {0}'.format(exc)
		return inserted

        def update_trap_count(self, traps, table):
		"""Update alarm count value"""
                updated = True
                default_columns = (
                                'device_name', 'ip_address', 'trapoid', 'eventname',
                                'eventno', 'severity', 'uptime', 'traptime',
                                'description', 'alarm_count', 'first_occurred',
                                'last_occurred', 'is_active', 'sia', 'customer_count'
                                )
                update_columns = (
		                'severity', 'uptime', 'traptime',
                                'description', 'last_occurred', 'sia',
				'customer_count'
                          )

		p0 = "INSERT INTO %(table)s" % {'table': table}
		p1 = ' (%s)' % ','.join(default_columns)
		p2 = ' , '.join(map(lambda x: ' %('+ x + ')s', default_columns))
		p3 = ' , '.join(map(lambda x: x + ' = VALUES(' + x + ')', update_columns))
		p4 = ''.join([', alarm_count = alarm_count +  VALUES(alarm_count) '])
		qry = ''.join(
                	[p0, p1, ' VALUES (', p2, ') ON DUPLICATE KEY UPDATE ' ,p3, p4]
                	)

                if traps:
                        try:
                                self.exec_qry(qry, traps,db_name='snmptt_db')
                        except Exception as exc:
                                updated = False
                                print 'Exc in mysql trap count update: {0}'.format(exc)
                return updated



if __name__ == '__main__':
	db_cls = ConnectionBase()
	print db_cls.mysql_cnx(db_name='snmptt_db')

