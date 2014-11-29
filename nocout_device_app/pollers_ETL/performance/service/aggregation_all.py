"""
aggregation_all.py
==================================

Usage ::
python aggregation_all.py -t 1 -f hourly -s performance_performancenetworkbihourly -d performance_performancenetworkhourly
python aggregation_all.py -t 1 -f hourly -d performance_performanceservicebihourly -d performance_performanceservicehourly
python aggregation_all.py -t 24 -f daily -d performance_performanceservicehourly -d performance_performanceservicedaily
python aggregation_all.py -t (7*24) -f weekly -d performance_performancestatusdaily -d performance_performancestatusweekly
python aggregation_all.py -t (7*24) -f weekly -d performance_performanceinventorydaily -d performance_performanceinventoryweekly
Options ::
t - Time frame for read operation [Hours]
s - Source Mongodb collection
d - Destination Mongodb collection
f - Time frame for script viz. daily, hourly etc.
"""

from nocout_site_name import *
import imp
import sys
from datetime import datetime, timedelta
from pprint import pprint
import collections
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



def quantify_perf_data(aggregated_data_values=[]):
	"""
	Quantifies (int, float) perf data using `min`, `max` and `sum` funcs
	and frequency based data on number of  occurrences of values
	"""
	
	data_values = []
	end_time = datetime.now()
	start_time = end_time - timedelta(hours=hours)
	start_time, end_time = start_time - timedelta(minutes=1), end_time + timedelta(minutes=1)
	start_time, end_time = int(start_time.strftime('%s')), int(end_time.strftime('%s'))
	db = mysql_migration_mod.mysql_conn(mysql_configs=mysql_configs)
	if db:
		# Read data from mysqldb, performance historical data
		data_values = mysql_migration_mod.read_data(source_perf_table, db, start_time, end_time)
	print '## Docs len ##'
	print len(data_values)
	for doc in data_values:
		# These services contain perf which can't be evaluated using regular `min`, `max` functions
		wimax_mrotek_services = ['wimax_ss_sector_id', 'wimax_ss_mac', 'wimax_dl_intrf', 'wimax_ul_intrf', 'wimax_ss_ip',
				'wimax_modulation_dl_fec', 'wimax_modulation_ul_fec', 'wimax_ss_frequency',
				'rici_line_1_port_state', 'rici_fe_port_state', 'rici_e1_interface_alarm',
				'rici_device_type', 'mrotek_line_1_port_state', 'mrotek_fe_port_state',
				'mrotek_e1_interface_alarm', 'mrotek_device_type']
		aggr_data = {}
		find_query = {}
		host, ip_address = doc.get('device_name'), doc.get('ip_address')
		ds, service = doc.get('data_source'), doc.get('service_name')
		site = doc.get('site_name')
		time = float(doc.get('sys_timestamp'))
		original_time, time = time, datetime.fromtimestamp(time)
		if time_frame == 'hourly':
			# Pivot the time to H:00:00
			time = time.replace(minute=0, second=0, microsecond=0)
			# Pivoting the time to next hour time frame [as explained in doc string]
			time += timedelta(hours=1)
		elif time_frame == 'daily':
			# Pivot the time to 00:00:00
			time = time.replace(hour=0, minute=0, second=0, microsecond=0)
			# Pivot the time to next day time frame
			time += timedelta(days=1)
		elif time_frame == 'weekly':
			# Pivot the time to 23:55:00
			time = time.replace(hour=23, minute=55, second=0, microsecond=0)
			pivot_to_weekday = 7 - time.weekday()
			# Pivoting the time to Sunday 23:55:00 [end of present week]
			time += timedelta(days=pivot_to_weekday-1)
		aggr_data = {
				'host': host,
				'service': service,
				'ds': ds,
				'site': site,
				'time':time,
				'ip_address': ip_address,
				'min': doc.get('min'),
				'max': doc.get('max'),
				'avg': doc.get('avg')
				}

		# Find the existing doc to update
		find_query = {
				'host': doc.get('host'),
				'service': doc.get('service'),
				'ds': aggr_data.get('ds'),
				'time': time
				}
		existing_doc = find_existing_entry(find_query, aggregated_data_values)
		#print 'existing_doc'
		#print existing_doc
		if existing_doc:
			existing_doc = existing_doc[0]
			values_list = [existing_doc.get('max'), aggr_data.get('max'), 
					existing_doc.get('min'), aggr_data.get('min')]
			if service in wimax_mrotek_services or '_status' in service or '_invent' in service:
				occur = collections.defaultdict(int)
				for val in values_list:
					occur[val] += 1
				freq_dist = occur.keys()
				min_val = freq_dist[0]
				max_val = freq_dist[-1]
				avg_val = None
			else:
				min_val = min(values_list) 
				max_val = max(values_list) 
				if aggr_data.get('avg'):
					avg_val = (existing_doc.get('avg') + aggr_data.get('avg'))/ 2
				else:
					avg_val = existing_doc.get('avg')
			aggr_data.update({
				'min': min_val,
				'max': max_val,
				'avg': avg_val
				})
			# First remove the existing entry from aggregated_data_values
			aggregated_data_values = filter(lambda d: not (set(find_query.values()) <= set(d.values())), aggregated_data_values)
		#upsert_aggregated_data(find_query, aggr_data)
		aggregated_data_values.append(aggr_data)
	
	return aggregated_data_values


def find_existing_entry(find_query, aggregated_data_values):
	"""
	Find the doc for update query
	"""
       
	docs = []
	docs = filter(lambda d: set(find_query.values()) <= set(d.values()), aggregated_data_values)

	return docs

def usage():
	print "Usage: service_mongo_aggregation_hourly.py [options]"


if __name__ == '__main__':
	final_data_values = quantify_perf_data()
	if final_data_values:
		db = mysql_migration_mod.mysql_conn(mysql_configs=mysql_configs)
		mysql_migration_mod.mysql_export(destination_perf_table, db, final_data_values)
