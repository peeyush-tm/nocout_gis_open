
"""
Main file for migration of data from mongodb to mysql for events.This file runs the script event_mongo_migration.py(which it read from the config.ini and event_mongo_migration.py migrate the data from mongodb to mysql db.

"""

from nocout_site_name import *
import imp

config_module = imp.load_source('configparser', '/opt/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

def main():
    mongo_conf = []
    configs = config_module.parse_config_obj()
    for section, options in configs.items():
	mongo_conf.append((options.get('site'),options.get('host'), options.get('port')))
	
    network_event_script = configs.get(mongo_conf[0][0]).get('network_event').get('script')
    network_event_migration_script = __import__(network_event_script)
    network_event_migration_script.main(mongo_conf=mongo_conf,
    user=configs.get(mongo_conf[0][0]).get('user'),
    sql_passwd=configs.get(mongo_conf[0][0]).get('sql_passwd'),
    nosql_db=configs.get(mongo_conf[0][0]).get('nosql_db'),
    sql_db=configs.get(mongo_conf[0][0]).get('sql_db'), table_name=configs.get(mongo_conf[0][0]).get('network_event').get('table_name'), ip=configs.get(mongo_conf[0][0]).get('ip')
    )
	
    service_event_script = configs.get(mongo_conf[0][0]).get('service_event').get('script')
    service_event_migration_script = __import__(service_event_script)
    service_event_migration_script.main(mongo_conf=mongo_conf,
    user=configs.get(mongo_conf[0][0]).get('user'),
    sql_passwd=configs.get(mongo_conf[0][0]).get('sql_passwd'),
    nosql_db=configs.get(mongo_conf[0][0]).get('nosql_db'),
    sql_db=configs.get(mongo_conf[0][0]).get('sql_db'), table_name=configs.get(mongo_conf[0][0]).get('service_event').get('table_name'), ip=configs.get(mongo_conf[0][0]).get('ip')
    )

if __name__ == '__main__':
    main()
