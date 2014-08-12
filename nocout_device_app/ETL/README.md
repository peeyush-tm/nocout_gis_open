ETL
===

Base staging directory for all the scripts which migrates the data from Mongodb
to central Mysql db, for all the services.

I. File List
------------

.
|-- ./config.ini
|-- ./configparser.py
|-- ./events
|   |-- ./events/events_migrations.py
|   |-- ./events/events_rrd_migration.py
|   |-- ./events/network_events_mongo_migration.py
|   |-- ./events/nocout_site_name.py
|   `-- ./events/service_events_mongo_migration.py
|-- ./performance
|   |-- ./performance/interface
|   |   |-- ./performance/interface/__init__.py
|   |   |-- ./performance/interface/interface_migrations.py
|   |   |-- ./performance/interface/interface_mongo_migration.py
|   |   |-- ./performance/interface/interface_rrd_migration.py
|   |   `-- ./performance/interface/nocout_site_name.py
|   |-- ./performance/inventory
|   |   |-- ./performance/inventory/inventory_migrations.py
|   |   |-- ./performance/inventory/inventory_mongo_migration.py
|   |   |-- ./performance/inventory/inventory_rrd_migration.py
|   |   `-- ./performance/inventory/nocout_site_name.py
|   `-- ./performance/service
|       |-- ./performance/service/__init__.py
|       |-- ./performance/service/migrations.py
|       |-- ./performance/service/network_mongo_migration.py
|       |-- ./performance/service/nocout_site_name.py
|       |-- ./performance/service/rrd_main.py
|       |-- ./performance/service/rrd_migration.py
|       `-- ./performance/service/service_mongo_migration.py
|-- ./README.md
|-- ./status
|   |-- ./status/interface
|   |   |-- ./status/interface/interface_status_migrations.py
|   |   |-- ./status/interface/interface_status_tables_migration.py
|   |   `-- ./status/interface/nocout_site_name.py
|   |-- ./status/inventory
|   |   |-- ./status/inventory/inventory_status_migrations.py
|   |   |-- ./status/inventory/inventory_status_tables_migration.py
|   |   `-- ./status/inventory/nocout_site_name.py
|   `-- ./status/service
|       |-- ./status/service/network_status_tables_migration.py
|       |-- ./status/service/nocout_site_name.py
|       |-- ./status/service/service_status_migrations.py
|       `-- ./status/service/service_status_tables_migration.py
`-- ./utils
    |-- ./utils/mongo_functions.py
    |-- ./utils/mysql_functions.py
    |-- ./utils/nagios_notification_extraction.py
    |-- ./utils/nocout_site_name.py
    |-- ./utils/snmp_alarm_extraction.py
    |-- ./utils/store_notification_in_db.py
    `-- ./utils/utility_functions.py

III. Description
----------------

./config.ini :: Main configuration file
./configparser.py :: Parses the main configuration file

./events/events_migrations.py :: Main migration file for the events
./events/events_rrd_migration.py :: Script to insert data from Nagios RRDTool into Mongodb
./events/network_events_mongo_migration.py :: Events for Ping services
./events/service_events_mongo_migration.py :: Mysql migrations for events for all services except Ping

./performance/interface/interface_migrations.py :: Main file for Mysql migration for servies which runs every 1 hour
./performance/interface/interface_mongo_migration.py :: Mysql migration for servies which runs every 1 hour
./performance/interface/interface_rrd_migration.py :: Nagios RRDTool to Mongodb migration for services which runs every 1 hour

./performance/inventory/inventory_migrations.py :: Main file for Mysql migration for servies which runs once in a day
./performance/inventory/inventory_mongo_migration.py :: Mysql migration for services which runs once in a day
./performance/inventory/inventory_rrd_migration.py :: Nagios RRDTool to Mongodb migration for servies which runs once in a day

./performance/service/migrations.py :: Main file for Mysql migration for servies which runs every 5 mins
./performance/service/network_mongo_migration.py :: Mysql migration for servies Ping
./performance/service/rrd_main.py :: Main rrd migration file
./performance/service/rrd_migration.py :: Migration file for Nagios RRDTool to Mongodb
./performance/service/service_mongo_migration.py :: Mysql migration for servies which runs every 5 mins

./status/interface/interface_status_migrations.py :: Main migrations file for status of services which runs once in an hour
./status/interface/interface_status_tables_migration.py :: Mysql migrations file for status of services which runs once in an hour

./status/inventory/inventory_status_migrations.py :: Main migrations file for status of services which runs once in a day
./status/inventory/inventory_status_tables_migration.py :: Mysql migrations file for status of services which runs once in a day

./status/service/network_status_tables_migration.py :: Mysql migrations file for status of services which runs once every 5 mins
./status/service/service_status_migrations.py :: Main migrations file for status of services which runs every 5 mins
./status/service/service_status_tables_migration.py :: Mysql migrations file for status of services which runs once every 5 mins

./utils/mongo_functions.py :: Functions which reads data from mongodb
./utils/mysql_functions.py :: Functions which reads data from mysqldb
./utils/nagios_notification_extraction.py :: Notification parsing from Nagios Logs
./utils/nocout_site_name.py :: Returns the current site name
./utils/utility_functions.py :: Contains the common utility functions used in ETL