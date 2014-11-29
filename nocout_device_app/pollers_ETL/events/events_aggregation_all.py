"""
events_aggregation_all.py
==========================

Script aggregates events data read from historical mysql table
and write to historical mysql table, next in aggregation

Usage ::
python events_aggregation_all.py -t 168 -f weekly -s performance_eventnetworkdaily -d performance_eventnetworkweekly
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


config_mod = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)
mysql_migration_mod = imp.load_source('historical_mysql_export', '/omd/sites/%s/nocout/utils/historical_mysql_export.py' % nocout_site_name)

configs = config_mod.parse_config_obj(historical_conf=True)
desired_site = filter(lambda x: x == nocout_site_name, configs.keys())[0]
desired_config = configs.get(desired_site)

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



def quantify_events_data(aggregated_data_values=[]):
	"""
	Events aggregation
	"""
	
	data_values = []
	end_time = datetime.now()
	start_time = end_time - timedelta(hours=hours)
	start_time, end_time = start_time - timedelta(minutes=1), end_time + timedelta(minutes=1)
	start_time, end_time = int(start_time.strftime('%s')), int(end_time.strftime('%s'))
	db = mysql_migration_mod.mysql_conn(mysql_configs=mysql_configs)
	if db:
		# Read data from mysql, events historical data
		data_values = sorted(mysql_migration_mod.read_data(source_perf_table, db, start_time, end_time), key=itemgetter('sys_timestamp'))
	print '## Docs len ##'
	print len(data_values)
	for index, doc in enumerate(data_values):
		aggr_data = {}
		find_query = {}
		host, ip_address = doc.get('device_name'), doc.get('ip_address')
		ds, service = doc.get('data_source'), doc.get('service_name')
		severity = doc.get('severity')
		current_value = int(doc.get('current_value'))
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
			time = time.replace(hour=23, minute=55, second=0, microsecond=0)
			pivot_to_weekday = 7 - time.weekday()
			# Pivoting the time to Sunday 23:55:00 [end of present week]
			time += timedelta(days=pivot_to_weekday-1)
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
				'current_value': current_value
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
		if existing_doc:
			existing_doc = existing_doc[0]
			max_val = max([aggr_data.get('max'), existing_doc.get('max')])
			min_val = min([aggr_data.get('min'), aggr_data.get('min')])
			avg_val = sum([max_val + min_val])/2
			# Update the count for service state
			current_value += int(existing_doc['current_value'])
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
	if final_data_values:
		db = mysql_migration_mod.mysql_conn(mysql_configs=mysql_configs)  
		mysql_migration_mod.mysql_export(destination_perf_table, db, final_data_values)
