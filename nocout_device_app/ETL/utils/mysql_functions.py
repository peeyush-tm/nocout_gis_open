from nocout_site_name import *
import MySQLdb
import imp
from pprint import pformat

logging_module = imp.load_source('get_site_logger', '/opt/omd/sites/%s/nocout/utils/nocout_site_logs.py' % nocout_site_name)

# Get logger
logger = logging_module.get_site_logger('utils.log')

def mysql_execute(query,event_db):
	conn = MySQLdb.connect(host= "localhost",
                  user="root",
                  passwd="lnmiit",
                  db=event_db)
	x = conn.cursor()

	try:
   		x.execute(query)
   		conn.commit()

	except MySQLdb.Error, e:
		logger.error('Error in Mysql Conn: ' + pformat(e))
   		conn.rollback()

	finally:
		if conn:
			conn.close()
	return x
