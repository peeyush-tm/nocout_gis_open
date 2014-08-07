"""
This file is the main file for migrating the mongodb data to mysql data for ping services and other services.It reads all configuration required for connecting the db from config.ini

File also migrates the mongodb data for the latest enrty for each devices to mysql data .so in mysql status tables store the latest data entry 
for each device
"""

from nocout_site_name import *
import imp

config_module = imp.load_source('configparser', '/opt/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

def main():
    configs = config_module.parse_config_obj()
    for section, options in configs.items():
	service_status_tables_script = options.get('service_status_tables').get('script')
	print service_status_tables_script
        service_status_tables_migration_script = __import__(service_status_tables_script)
        service_status_tables_migration_script.main(site=options.get('site'), host=options.get('host'),
        	user=options.get('user'), port=options.get('port'),
             	sql_passwd=options.get('sql_passwd'),
                nosql_db=options.get('service_status_tables').get('nosql_db'),
                sql_db=options.get('service_status_tables').get('sql_db'), table_name=options.get('service_status_tables').get('table_name'), 
		ip=options.get('ip')
        )

	network_status_tables_script = options.get('network_status_tables').get('script')
        network_status_tables_migration_script = __import__(network_status_tables_script)
        network_status_tables_migration_script.main(site=options.get('site'), host=options.get('host'),
        	user=options.get('user'), port=options.get('port'),
             	sql_passwd=options.get('sql_passwd'),
                nosql_db=options.get('network_status_tables').get('nosql_db'),
                sql_db=options.get('network_status_tables').get('sql_db'), table_name=options.get('network_status_tables').get('table_name'), 
		ip=options.get('ip')
        )

if __name__ == '__main__':
    main()
