"""
get_latest_entry.py
===================
""" 
from nocout_site_name import *
import mysql.connector
import imp
import sys
from pprint import pformat
from datetime import datetime
import time

config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)
utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
db_ops_module = imp.load_source('db_ops', '/omd/sites/%s/lib/python/handlers/db_ops.py' % nocout_site_name)


def get_and_insert_last_timestamp():
    sys.stdout.write('Start -- %s\n' % (datetime.now()))
    latest_sys_timestamp = None
    configs = config_module.parse_config_obj()
    desired_site = filter(lambda x: x == nocout_site_name, configs.keys())[0]
    desired_config = configs.get(desired_site)
    mysql_configs = {
            'ip': desired_config.get('ip'),
            'user': desired_config.get('user'),
            'sql_passwd': desired_config.get('sql_passwd'),
            'sql_port': desired_config.get('mysql_port'),
            'sql_db': desired_config.get('sql_db')
            }
    mongo_configs = {
            'host': desired_config.get('host'),
            'port': desired_config.get('port'),
            'db_name': desired_config.get('nosql_db')
            }
    table_list = ['performance_networkstatus', 'performance_servicestatus',
            'performance_status','performance_utilizationstatus']
    try:
        db = utility_module.mysql_conn(configs=mysql_configs)
        cursor = db.cursor()
    except mysql.connector.Error as err:
        sys.stdout.write('Error in Mysql connection\n{0}\n'.format(pformat(err)))
        sys.exit(1)
    # Insert the latest timestamp into Mongodb
    mongo_db = mongo_module.mongo_conn(
            host=mongo_configs.get('host'),
            port=mongo_configs.get('port'),
            db_name=mongo_configs.get('db_name')
            )
    for table in table_list:
        query = """SELECT max(sys_timestamp) FROM `{0}` 
                  WHERE site_name = '{1}'
                  """.format(table, nocout_site_name)
        latest_sys_timestamp = None
        try:
            cursor.execute(query)
            latest_sys_timestamp = datetime.fromtimestamp(float(cursor.fetchone()[0]))
        except Exception as exp:
            sys.stdout.write('Exception in DB query !!!\n{0}\n'.format(pformat(exp)))
            continue
        sys.stdout.write('%s   [%s]\n' % (table, latest_sys_timestamp))
        doc = {
                'sys_timestamp': latest_sys_timestamp,
		'_id': table
                }
	try:
		updated_time =int(time.mktime(latest_sys_timestamp.timetuple()))	
		memc_obj=db_ops_module.MemcacheInterface()
		memc=memc_obj.memc_conn
		memc.set(table,updated_time,300)
	except Exception,e:
            sys.stdout.write('Exception in DB query !!!\n{0}\n'.format(pformat(e)))
	    pass	
        #if mongo_db:
        #    mongo_db['sys_timestamp_status'].update({'_id': table}, doc, upsert=True)
    #db.close()
    sys.stdout.write('End -- %s\n' % (datetime.now()))


if __name__ == '__main__':
    get_and_insert_last_timestamp()
