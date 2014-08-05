"""
inventory_migration.py

File contains code for migrating the mongodb data to mysql.This File is specific to Inventory services and only migrates the data for inventory
services.

Mysql has another table inventory status table which keeps the latest data for each device configured on that site.This file also migrates the mongodb data to mysql for this table too.

"""

from configparser import parse_config_obj


def main():
    configs = parse_config_obj()
    for section, options in configs.items():
        inventory_script = options.get('inventory').get('script')
        inventory_service_migration_script = __import__(inventory_script)
        inventory_service_migration_script.main(site=options.get('site'), host=options.get('host'),
                user=options.get('user'), port=options.get('port'),
                sql_passwd=options.get('sql_passwd'),
                nosql_db=options.get('inventory').get('nosql_db'),
                sql_db=options.get('inventory').get('sql_db'), table_name=options.get('inventory').get('table_name'), ip=options.get('ip')
        )
	inventory_status_tables_script = options.get('inventory_status_tables').get('script')
        inventory_status_tables_migration_script = __import__(inventory_status_tables_script)
        inventory_status_tables_migration_script.main(site=options.get('site'), host=options.get('host'),
                user=options.get('user'), port=options.get('port'),
                sql_passwd=options.get('sql_passwd'),
                nosql_db=options.get('inventory_status_tables').get('nosql_db'),
                sql_db=options.get('inventory_status_tables').get('sql_db'),
                 table_name=options.get('inventory_status_tables').get('table_name'),ip=options.get('ip')
        )


if __name__ == '__main__':
    main()

