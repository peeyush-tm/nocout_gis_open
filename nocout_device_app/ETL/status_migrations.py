from configparser import parse_config_obj


def main():
    configs = parse_config_obj()
    for section, options in configs.items():
        status_script = options.get('status').get('script')
        status_service_migration_script = __import__(status_script)
        status_service_migration_script.main(site=options.get('site'), host=options.get('host'),
                user=options.get('user'), port=options.get('port'),
                sql_passwd=options.get('sql_passwd'),
                nosql_db=options.get('status').get('nosql_db'),
                sql_db=options.get('status').get('sql_db'), table_name=options.get('status').get('table_name'), ip=options.get('ip')
        )
	status_services_status_tables_script = options.get('status_services_status_tables').get('script')
        status_services_status_tables_migration_script = __import__(status_services_status_tables_script)
        status_services_status_tables_migration_script.main(site=options.get('site'), host=options.get('host'),
                user=options.get('user'), port=options.get('port'),
                sql_passwd=options.get('sql_passwd'),
                nosql_db=options.get('status_services_status_tables').get('nosql_db'),
                sql_db=options.get('status_services_status_tables').get('sql_db'),
                table_name=options.get('status_services_status_tables').get('table_name'),ip=options.get('ip')
        )


if __name__ == '__main__':
    main()
