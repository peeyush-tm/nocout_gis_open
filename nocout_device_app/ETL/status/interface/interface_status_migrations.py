"""
Main file for migration of data from mongodb to mysql for status services.This file runs the script status_mongo_migration.py(which it read from the config.ini and status_mongo_migration.py migrate the mongodb data (data for the status services)into mysql db.
"""

from nocout_site_name import *
import imp

config_module = imp.load_source('configparser', '/opt/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

def main():
    configs = config_module.parse_config_obj()
    for section, options in configs.items():
	interface_status_tables_script = options.get('interface_status_tables').get('script')
    interface_status_tables_migration_script = __import__(interface_status_tables_script)
    interface_status_tables_migration_script.main(site=options.get('site'), host=options.get('host'),
            user=options.get('user'), port=options.get('port'),
            sql_passwd=options.get('sql_passwd'),
            nosql_db=options.get('interface_status_tables').get('nosql_db'),
            sql_db=options.get('interface_status_tables').get('sql_db'),
            table_name=options.get('interface_status_tables').get('table_name'),ip=options.get('ip')
    )


if __name__ == '__main__':
    main()
