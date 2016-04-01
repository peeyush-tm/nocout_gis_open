""" Module to read and prcoss raw traps from snmptt databse"""

from trap_handler.db_conn import ConnectionBase
#from process_traps import ProcessTraps

# changed module for production
#from mapper import Eventmapper 
from trap_handler.mapper import Eventmapper

class RawTraps(object):

	def __init__(self, **kw):
		self.conn_base = ConnectionBase(**kw)
		# TODO: move inventory caching to some other module
		self.export_invent_into_redis()

	def do_work(self):
		self.read_raw_traps()

	def exec_qry(self, qry, db_name):
		try:
			mysql_cnx = self.conn_base.mysql_cnx(db_name=db_name)
			cur = mysql_cnx.cursor()
			cur.execute(qry)
			data = cur.fetchall()
		except Exception as exc:
			data = []
			print 'Error executing qry: {0}'.format(exc)
		finally:
			cur.close()
			mysql_cnx.close()

		return data

	# TODO: move this along with update_id_info, to db_ops mod
	def get_start_id(self):
		""" Get id from which we need to read traps"""

		qry = "SELECT processed_row FROM processed_traps_id"
		id_info = self.exec_qry(qry, 'snmptt_db')
		id_info = id_info[0][0] if id_info else None

		return id_info

	def read_raw_traps(self):
		""" Bulk read traps from snmptt database"""

		qry = """SELECT id, eventname, eventid, agentip, trapoid, category, 
		severity, uptime, traptime, formatline FROM snmptt WHERE id > {0}
		""".format(self.get_start_id())

		data = self.exec_qry(qry, 'snmptt_db')
		#print data
		if data:
			# TODO: move this functionality to init()
			#worker = ProcessTraps()
			worker = Eventmapper()
			worker.filter_traps(data)

	def export_invent_into_redis(self):
		""" Load inventory info (ip, device name etc.) present in 
		mysql into redis
		Usually this task would be taken care by Sync
		"""

		qry = "SELECT ip_address, device_name FROM device_device"
		data = self.exec_qry(qry, 'application_db')

		if data:
			mapping = {}
			[mapping.update({k: v}) for (k, v) in data]
			# load these ip --> device name mapping into redis hash table
			redis_cnx = self.conn_base.redis_cnx(db_name='redis_master')
			try:
				p = redis_cnx.pipeline()
				p.hmset('ip:host', mapping)
				p.execute()
			except Exception as exc:
				print 'Error in redis qry: {0}'.format(exc)


if __name__ == '__main__':
	worker = RawTraps()
	worker.do_work()
