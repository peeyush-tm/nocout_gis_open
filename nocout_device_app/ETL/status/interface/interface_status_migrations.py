"""
Main file for migration of data from mongodb to mysql for status services.This file runs the script status_mongo_migration.py(which it read from the config.ini and status_mongo_migration.py migrate the mongodb data (data for the status services)into mysql db.
"""

from nocout_site_name import *
import imp

config_module = imp.load_source('configparser', '/opt/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

def main():
    mongo_conf = []
    configs = config_module.parse_config_obj()
    for section, options in configs.items():
	mongo_conf.append((options.get('site'),options.get('host'), options.get('port')))
	
    interface_status_tables_script = configs.get(mongo_conf[0][0]).get('interface_status_tables').get('script')
    interface_status_tables_migration_script = __import__(interface_status_tables_script)
    interface_status_tables_migration_script.main(mongo_conf=mongo_conf,
    user=configs.get(mongo_conf[0][0]).get('user'),
    sql_passwd=configs.get(mongo_conf[0][0]).get('sql_passwd'),
    nosql_db=configs.get(mongo_conf[0][0]).get('nosql_db'),
    sql_db=configs.get(mongo_conf[0][0]).get('sql_db'), table_name=configs.get(mongo_conf[0][0]).get('interface_status_tables').get('table_name'), ip=configs.get(mongo_conf[0][0]).get('ip')
    )


if __name__ == '__main__':
    main()
