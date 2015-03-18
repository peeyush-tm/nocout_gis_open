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
    live_db_tables = [
            'performance_eventnetwork', 'performance_eventservice', 'performance_performanceservice',
            'performance_performancenetwork', 'performance_performancestatus',
            'performance_performanceinventory', 'performance_networkavailabilitydaily'
            ]
    bihourly_db_tables = [
            'performance_performanceservicebihourly', 'performance_performancenetworkbihourly'
            ]
    hourly_db_tables = [
            'performance_performancenetworkhourly', 'performance_performanceservicehourly'
            ]
    daily_db_tables = [
            'performance_performancenetworkdaily', 'performance_performanceservicedaily',
            'performance_performancestatusdaily', 'performance_performanceinventorydaily',
            'performance_networkavailabilitydaily', 'performance_eventservicedaily',
            'performance_eventnetworkdaily', 'performance_utilizationdaily'
            ]
    weekly_db_tables = [
            'performance_performancenetworkweekly', 'performance_performanceserviceweekly',
            'performance_performancestatusweekly', 'performance_performanceinventoryweekly',
            'performance_networkavailabilityweekly', 'performance_eventserviceweekly',
            'performance_eventnetworkweekly', 'performance_utilizationweekly'
            ]

    if line_args == 'live_data':
        db = utility_module.mysql_conn(configs=live_mysql_configs) 
        # We have to perform clean operations for live mysql db
        end_time = int((datetime.now()- timedelta(days=30)).strftime('%s'))
        clean_data(db, end_time, live_db_tables)
        db.close()
    elif line_args == 'historical_data':
        db = utility_module.mysql_conn(configs=historical_mysql_configs) 
        # Clean the entries older than 1 month
        end_time = int((datetime.now() - timedelta(days=30)).strftime('%s'))
        clean_data(db, end_time, bihourly_db_tables)
        # Clean the entries older than 3 months
        end_time = int((datetime.now() - timedelta(days=90)).strftime('%s'))
        clean_data(db, end_time, hourly_db_tables)
        # Clean the entries older than 6 months
        end_time = int((datetime.now() - timedelta(days=180)).strftime('%s'))
        clean_data(db, end_time, daily_db_tables)
        # Clean the entries older than 12 months
        end_time = int((datetime.now() - timedelta(days=360)).strftime('%s'))
        clean_data(db, end_time, weekly_db_tables)

        db.close()


# Live mysql db tables would contain data for last 30 days only
# Historical db tables would contain entry for last 1, 3, 6, 12 months
def clean_data(db, end_time, tables):
    for entry in tables:
        query = "DELETE FROM %s WHERE " % entry
        query += "sys_timestamp < %s" % (end_time)
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        cursor.close()
        print 'Data cleaned for table - %s , older than - %s' % (entry, \
                datetime.fromtimestamp(float(end_time)))
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
