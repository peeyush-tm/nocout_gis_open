"""
events_aggregation_base.py
==========================

Script aggregates events data read from live mongodb collection
and write to historical mysql table

Usage ::
python events_aggregation_base.py -t 24 -f daily -s nocout_host_event_log -d performance_eventnetworkdaily
Options ::
t - Time frame for read operation [Hours]
s - Source Mongodb collection
d - Destination Mysql table
f - Time frame for script viz. daily, hourly etc.
"""

from nocout_site_name import *
import imp
import sys
from datetime import datetime, timedelta
from pprint import pprint
from operator import itemgetter
import optparse


mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
config_mod = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)
mysql_migration_mod = imp.load_source('historical_mysql_export', '/omd/sites/%s/nocout/utils/historical_mysql_export.py' % nocout_site_name)

configs = config_mod.parse_config_obj(historical_conf=True)
desired_site = filter(lambda x: x == nocout_site_name, configs.keys())[0]
desired_config = configs.get(desired_site)

mongo_configs = {
		'host': desired_config.get('host'),
		'port': int(desired_config.get('port')),
		'db_name': desired_config.get('nosql_db')
		}
mysql_configs = {
		'host': desired_config.get('ip'),
		'port': int(desired_config.get('sql_port')),
		'user': desired_config.get('user'),
		'password': desired_config.get('sql_passwd'),
		'database': desired_config.get('sql_db')
		}
parser = optparse.OptionParser()
parser.add_option('-s', '--source', dest='source_db', type='str')
parser.add_option('-d', '--destination', dest='destination_db', type='str')
parser.add_option('-t', '--hours', dest='hours', type='choice', choices=['1', '24', '168'])
parser.add_option('-f', '--timeframe', dest='timeframe', type='choice', choices=['hourly', 'daily', 'weekly'])
options, remainder = parser.parse_args(sys.argv[1:])
if options.source_db and options.destination_db and options.hours and options.timeframe:
	source_perf_table=options.source_db
	destination_perf_table=options.destination_db
	hours = int(options.hours)
	time_frame = options.timeframe
else:
	print "Usage: service_mongo_aggregation_hourly.py [options]"
	sys.exit(2)


def read_data_from_mongo(start_time, end_time, configs):
	db = None
	docs = []
	db = mongo_module.mongo_conn(
			host=configs.get('host'),
			port=int(configs.get('port')),
			db_name='nocout')
	end_time = int(datetime.now().strftime('%s'))
	if db:
		cur = db[source_perf_table].find({'sys_timestamp': {'$lt': end_time}})
		docs = list(cur)
	return docs


def dict_rows(cur):
	desc = cur.description
	return [dict(zip([col[0] for col in desc], row)) for row in cur.fetchall()]


def quantify_events_data(aggregated_data_values=[]):
	"""
	Events aggregation
	"""
	
	end_time = datetime.now()
	start_time = end_time - timedelta(hours=hours)
	start_time, end_time = start_time - timedelta(minutes=1), end_time + timedelta(minutes=1)
	start_time, end_time = int(start_time.strftime('%s')), int(end_time.strftime('%s'))
	# Read data from mongodb, events live data
    	data_values = sorted(read_data_from_mongo(start_time, end_time, mongo_configs), key=itemgetter('sys_timestamp'))
	print '## Docs len ##'
	print len(data_values)
	for index, doc in enumerate(data_values):
		aggr_data = {}
		find_query = {}
		host, ip_address = doc.get('device_name'), doc.get('ip_address')
		ds, service = doc.get('data_source'), doc.get('service_name')
		severity = doc.get('severity')
		site = doc.get('site_name')
		original_time = doc.get('sys_timestamp') if doc.get('sys_timestamp') else doc.get('time')
		time = datetime.fromtimestamp(original_time)
		if time_frame == 'daily':
			# Pivot the time to 00:00:00
			time = time.replace(hour=0, minute=0, second=0, microsecond=0)
			# Pivot the time to next day time frame
			time += timedelta(days=1)
		elif time_frame == 'weekly':
			# Pivot the time to 00:00:00
			time = doc.get('time').replace(hour=0, minute=0, second=0, microsecond=0)
			pivot_to_weekday = 7 - time.weekday()
			# Pivoting the time to next Monday 00:00:00 [starting of next week]
			time += timedelta(days=pivot_to_weekday)
		# Key identifier `original_time` is used in finding next service state change
		aggr_data = {
				'host': host,
				'service': service,
				'ds': ds,
				'severity': severity,
				'time':time,
				'original_time': original_time,
				'site': site,
				'ip_address': ip_address,
				'current_value': 1
				}
		# Find the entry for next state change of the host service
		state_change_entry = find_next_state_change(aggr_data, data_values[index+1:]) 
		if not state_change_entry:
			continue
		age_of_state = state_change_entry[0].get('sys_timestamp') - original_time 
		aggr_data.update({
			'min': age_of_state,
			'max': age_of_state,
			'avg': age_of_state
			})

		# Find the existing doc to update
		find_query = {
				'host': aggr_data.get('host'),
				'service': aggr_data.get('service'),
				'ds': aggr_data.get('ds'),
				'severity': aggr_data.get('severity'),
				'time': aggr_data.get('time')
				}
		existing_doc = find_existing_entry(find_query, aggregated_data_values)
		#print 'existing_doc'
		#print existing_doc
		current_value = 1
		if existing_doc:
			existing_doc = existing_doc[0]
			max_val = max([aggr_data.get('max'), existing_doc.get('max')])
			min_val = min([aggr_data.get('min'), aggr_data.get('min')])
			avg_val = sum([max_val + min_val])/2
			# Update the count for service state
			current_value = aggr_data['current_value'] + 1
			aggr_data.update({
				'min': min_val,
				'max': max_val,
				'avg': avg_val,
				'current_value': current_value
				})
			# First remove the existing entry from aggregated_data_values
			aggregated_data_values = filter(lambda d: not (set(find_query.values()) <= set(d.values())), aggregated_data_values)
		# Add the new aggregated doc to final values
		aggregated_data_values.append(aggr_data)
	
	return aggregated_data_values


def find_next_state_change(aggr_data, data_values):
	intermediate_result = filter(lambda e: set([aggr_data['host'], aggr_data['service'], \
			aggr_data['ds']]) <= set(e.values()), data_values)
	return filter(lambda e: aggr_data['severity'] != e['severity'] and \
			aggr_data['original_time'] < e['sys_timestamp'], intermediate_result)[0:1]
	

def find_existing_entry(find_query, aggregated_data_values, existing=[]):
	"""
	Find the doc to upadte
	"""
       
        #print 'find_query'
	#print find_query
        existing = filter(lambda d: set(find_query.values()) <= set(d.values()), aggregated_data_values)
	return existing


def usage():
	print "Usage: service_mongo_aggregation_hourly.py [options]"


if __name__ == '__main__':
	final_data_values = quantify_events_data()
	db = mysql_migration_mod.mysql_conn(mysql_configs=mysql_configs)  
	mysql_migration_mod.mysql_export(destination_perf_table, db, final_data_values)
