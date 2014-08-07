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
        
	network_script = options.get('network').get('script')
	network_migration_script = __import__(network_script)
	network_migration_script.main(site=options.get('site'), host=options.get('host'),
		user=options.get('user'), port=options.get('port'),
		sql_passwd=options.get('sql_passwd'),
		nosql_db=options.get('network').get('nosql_db'),
		sql_db=options.get('network').get('sql_db'), table_name=options.get('network').get('table_name'), ip=options.get('ip')
        )

	service_script = options.get('service').get('script')
	service_migration_script = __import__(service_script)
	service_migration_script.main(site=options.get('site'), host=options.get('host'),
	    	user=options.get('user'), port=options.get('port'),
            	sql_passwd=options.get('sql_passwd'),
            	nosql_db=options.get('service').get('nosql_db'),
            	sql_db=options.get('service').get('sql_db'), table_name=options.get('service').get('table_name'), ip=options.get('ip')
        )
	

if __name__ == '__main__':
    main()
