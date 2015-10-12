"""
mysql_clean.py
==============

Clean the Live as well as Historical mysql data
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


@app.task(name='pre-clean', ignore_result=True)
def pre_clean(type, live_mysql_configs=None, historical_mysql_configs=None):
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

    # No sending the messages in celery queue, for now
    if type == 'live':
        db = connect(**live_mysql_configs)
        # We have to perform clean operations for live mysql db
        end_time = int((datetime.now()- timedelta(days=30)).strftime('%s'))
        clean_data(db, end_time, live_db_tables)
        db.close()
    elif type == 'historical':
        db = connect(**historical_mysql_configs) 
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
@app.task(name='clean-data', ignore_result=True, bind=True)
def clean_data(self, db, end_time, tables):
    try:
        for entry in tables:
            query = "DELETE FROM %s WHERE " % entry
            query += "sys_timestamp < %s" % (end_time)
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            cursor.close()
            print 'Data cleaned for table - %s , older than - %s' % (entry, \
                datetime.fromtimestamp(float(end_time)))
            sleep(20)
    except Exception as exc:
	self.retry(args=(db, end_time, tables), max_retries=1, countdown=20)
    print '\n'


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
    pre_clean.s(
	opts.get('type'), 
	live_mysql_configs, 
	historical_mysql_configs
    ).apply_async()


if __name__ == '__main__':
    opts = {
	'type': 'live',
	'machine': 'ospf2',
    }
    main(**opts)
