"""
mysql_clean.py
==============

Clean the Live as well as Historical mysql data
Usage ::
python mysql_clean.py -a live_data
python mysql_clean.py -a historical_data
"""

import optparse
import sys
from datetime import datetime, timedelta
import imp

from nocout_site_name import *
config_mod = imp.load_source('configparser', \
        '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)
utility_module = imp.load_source('utility_functions', \
        '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)


def get_site_configs(desired_config={}):
    configs = config_mod.parse_config_obj(historical_conf=True)
    desired_site = filter(lambda x: x == nocout_site_name, configs.keys())[0]
    desired_config = configs.get(desired_site)

    return desired_config


def parse_args(args_list, out=None):
    parser = optparse.OptionParser()
    parser.add_option('-a', '--action', dest='action', choices=['live_data', 'historical_data'])
    options, remainder = parser.parse_args(args_list)
    if options.action: 
        out = options.action
    else:
        print "Usage: mysql_clean.py [options]"
        sys.exit(2)

    return out


def pre_clean(line_args, live_mysql_configs=None, historical_mysql_configs=None):
    # we need to store partition names for these tables
    live_db_tables = {
            'performance_eventnetwork': 0, 
            'performance_eventservice': 0, 
            'performance_performanceservice': 0,
            'performance_performancenetwork': 0, 
            'performance_performancestatus': 0,
            'performance_performanceinventory': 0, 
            'performance_networkavailabilitydaily': 0,
            'performance_utilization': 0
            }
    bihourly_db_tables = {
            'performance_performanceservicebihourly': 0, 
            'performance_performancenetworkbihourly': 0,
            'performance_utilizationbihourly': 0
            }
    hourly_db_tables = {
            'performance_performancenetworkhourly': 0, 
            'performance_performanceservicehourly': 0,
            'performance_utilizationhourly': 0
            }
    daily_db_tables = {
            'performance_performancenetworkdaily': 0, 
            'performance_performanceservicedaily': 0,
            'performance_performancestatusdaily': 0, 
            'performance_performanceinventorydaily': 0,
            'performance_networkavailabilitydaily': 0, 
            'performance_eventservicedaily': 0,
            'performance_eventnetworkdaily': 0, 
            'performance_utilizationdaily': 0
            }
    weekly_db_tables = {
            'performance_performancenetworkweekly': 0, 
            'performance_performanceserviceweekly': 0,
            'performance_performancestatusweekly': 0, 
            'performance_performanceinventoryweekly': 0,
            'performance_networkavailabilityweekly': 0, 
            'performance_eventserviceweekly': 0,
            'performance_eventnetworkweekly': 0, 
            'performance_utilizationweekly': 0
            }

    if line_args == 'live_data':
        db = utility_module.mysql_conn(configs=live_mysql_configs) 
        # We have to perform clean operations for live mysql db
        # this will give partition names for `sys_timetimestamp` < `older_than`
        # we need to use sys_timestamp, bcz we have range partition on sys_timestamp field
        live_db_tables = get_partitions_names(db, live_db_tables, 1*30)
        clean_data(db, live_db_tables)
        db.close()
    elif line_args == 'historical_data':
        db = utility_module.mysql_conn(configs=historical_mysql_configs) 

        # Clean the entries older than 1 month
        bihourly_db_tables = get_partitions_names(db, bihourly_db_tables, 1*30)
        clean_data(db, bihourly_db_tables)

        # Clean the entries older than 3 months
        hourly_db_tables = get_partitions_names(db, hourly_db_tables, 3*30)
        clean_data(db, hourly_db_tables)

        # Clean the entries older than 6 months
        daily_db_tables = get_partitions_names(db, daily_db_tables, 6*30)
        clean_data(db, daily_db_tables)

        # Clean the entries older than 12 months
        weekly_db_tables = get_partitions_names(db, weekly_db_tables, 12*30)
        clean_data(db, weekly_db_tables)

        db.close()


def get_partitions_names(db, tables, older_than):
    # we would store one week's extra data, if we want to delete by partition
    days = (older_than - older_than % 7) + 7 + 1
    timerange = (datetime.now() - timedelta(days=days)).strftime('%s')
    cur = db.cursor()
    for t in tables.keys():
        qry = """EXPLAIN PARTITIONS SELECT (1) FROM {0} 
                 WHERE sys_timestamp < {1}""".format(t, timerange)
        cur.execute(qry)
        tables[t] = cur.fetchall()[0][3]
    cur.close()

    return tables


# Live mysql db tables would contain data for last 30 days only
# Historical db tables would contain entry for last 1, 3, 6, 12 months
def clean_data(db, tables):
    cursor = db.cursor()
    for table, partitions in tables.items():
        qry = "ALTER TABLE {0} DROP PARTITION {1}".format(table, partitions)
        cursor.execute(qry)
        #db.commit()
        print "Dropped partitions for table - {0} : {1}".format(table, partitions)
    cursor.close()
    print '\n'


def main():
    site_specific_configs = get_site_configs()
    line_args = parse_args(sys.argv[1:])
    live_mysql_configs = {
            'ip': site_specific_configs.get('live_ip'),
            'user': site_specific_configs.get('live_user'),
            'sql_passwd': site_specific_configs.get('live_sql_passwd'),
            'sql_port': site_specific_configs.get('live_sql_port'),
            'sql_db': site_specific_configs.get('live_sql_db')
            }
    historical_mysql_configs = {
            'ip': site_specific_configs.get('ip'),
            'user': site_specific_configs.get('user'),
            'sql_passwd': site_specific_configs.get('sql_passwd'),
            'sql_port': site_specific_configs.get('sql_port'),
            'sql_db': site_specific_configs.get('sql_db')
            }
    pre_clean(line_args, live_mysql_configs, historical_mysql_configs)


if __name__ == '__main__':
    main()
