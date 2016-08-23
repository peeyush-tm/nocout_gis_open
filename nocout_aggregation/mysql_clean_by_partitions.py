"""
mysql_clean_by_partitions.py
============================

Clean the Live as well as Historical mysql data
Usage ::
python mysql_clean.py -a live_data
python mysql_clean.py -a historical_data
"""

import sys
from ConfigParser import ConfigParser
from mysql.connector import connect
from time import sleep
from datetime import datetime, timedelta

from entry import app


def get_configs():
    desired_config = ConfigParser()
    desired_config.read('/data01/nocout/data_aggregation/mysql_db.ini')

    return desired_config


def parse_args(args_list, out=None):
    parser = optparse.OptionParser()
    parser.add_option('-a', '--action', dest='action',
                      choices=['live_data', 'historical_data'])
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
        #'performance_utilizationbihourly': 0
    }
    hourly_db_tables = {
        'performance_performancenetworkhourly': 0,
        'performance_performanceservicehourly': 0,
        #'performance_utilizationhourly': 0
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

    if line_args == 'live':
        db = connect(**live_mysql_configs)
        # We have to perform clean operations for live mysql db
        # this will give partition names for `sys_timetimestamp` < `older_than`
        # we need to use sys_timestamp, bcz we have range partition on
        # sys_timestamp field
        live_db_tables = get_partitions_names(db, live_db_tables, 31)
        clean_data(db, live_db_tables)
        db.close()
    elif line_args == 'historical':
        db = connect(**historical_mysql_configs)

        # Clean the entries older than 1 month
        bihourly_db_tables = get_partitions_names(db, bihourly_db_tables, 31)
        clean_data(db, bihourly_db_tables)

        # Clean the entries older than 3 months
        hourly_db_tables = get_partitions_names(db, hourly_db_tables, 3 * 30)
        clean_data(db, hourly_db_tables)

        # Clean the entries older than 6 months
        daily_db_tables = get_partitions_names(db, daily_db_tables, 6 * 30)
        clean_data(db, daily_db_tables)

        # Clean the entries older than 12 months
        weekly_db_tables = get_partitions_names(db, weekly_db_tables, 12 * 30)
        clean_data(db, weekly_db_tables)
        db.close()


def get_partitions_names(db, tables, older_than):
    # we would need to store one week's extra data, if we want to delete by partition
    #days = (older_than - older_than % 7) + 7 + 1
    #timerange = (datetime.now() - timedelta(days=days)).strftime('%s')
    timerange = (datetime.now() - timedelta(days=older_than)).strftime('%s')
    week_older = int(older_than) + 7
    timerange_prev_week = (datetime.now() - timedelta(days=week_older)).strftime('%s')
    cur = db.cursor()
    for t in tables.keys():
        qry = """EXPLAIN PARTITIONS SELECT (1) FROM {0}
                WHERE sys_timestamp < {1} AND sys_timestamp > {2}""".format(t, timerange, timerange_prev_week)
        cur.execute(qry)
        tables[t] = cur.fetchall()[0][3]
    cur.close()
    return tables


# Live mysql db tables would contain data for last 30 days only
# Historical db tables would contain entry for last 1, 3, 6, 12 months
@app.task(name='clean-data', ignore_result=True, bind=True)
def clean_data(self, db, tables):
    try:
        cursor = db.cursor()
        for table, partitions in tables.items():
            if partitions:
                qry = "ALTER TABLE {0} TRUNCATE PARTITION {1}".format(
                    table, partitions)
                print 'Delete query: %s' % qry
                cursor.execute(qry)
                # db.commit()
            print "Truncated partitions for table - {0} : {1}".format(table, partitions)
        cursor.close()
        print '\n'
    except Exception as exc:
        print "Exception in {0} DB. Tables : {1}".format(db, tables)
        print exc
        self.retry(args=(db, tables), max_retries=1, countdown=20)

@app.task(name='clean-main', ignore_result=True)
def main(**opts):
    configs = get_configs()
    live_mysql_configs, historical_mysql_configs = {}, {}
    if opts.get('type') == 'live':
        # get machine name
        m = opts.get('machine')
        live_mysql_configs = {
            'host': configs.get(m, 'host'),
            'user': configs.get(m, 'user'),
            'password': configs.get(m, 'password'),
            'port': configs.get(m, 'port'),
            'database': configs.get(m, 'database')
        }
    else:
        historical_mysql_configs = {
            'host': configs.get('historical', 'host'),
            'user': configs.get('historical', 'user'),
            'password': configs.get('historical', 'password'),
            'port': configs.get('historical', 'port'),
            'database': configs.get('historical', 'database')
        }
    pre_clean(
        opts.get('type'),
        live_mysql_configs,
        historical_mysql_configs
    )


if __name__ == '__main__':
    opts = {
        'type': 'historical',
    }
    main(**opts)

