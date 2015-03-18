"""
service_mongo_aggregation_half_hourly.py
=======================================

Usage ::
python service_mongo_aggregation_half_hourly.py -t 30 -s network_perf -d performance_performancenetworkbihourly
python service_mongo_aggregation_half_hourly.py -t 30 -s service_perf -d performance_performanceneservicebihourly
Options ::
t - Time frame for which data to be read from Mongodb (minutes)
s - Mongodb source collection name to read data from
d - Mongodb historical collection to put data in
"""

from nocout_site_name import *
import imp
import sys
from datetime import datetime, timedelta
from itertools import groupby
from operator import itemgetter
from pprint import pprint, pformat
import collections
import optparse
from historical_mysql_export import mysql_conn, mysql_export

mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
config_mod = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

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
parser.add_option('-s', '--source', dest='source_db', type='choice', choices=['service_perf', 'network_perf'])
parser.add_option('-d', '--destination', dest='destination_db', type='choice', choices=['performance_performancenetworkbihourly', 'performance_performanceservicebihourly'])
parser.add_option('-t', '--timeframe', dest='mins', type='choice', choices=['30'])
options, remainder = parser.parse_args(sys.argv[1:])
if options.source_db and options.destination_db and options.mins:
	perf_table=options.source_db
	hist_perf_table=options.destination_db
	time_frame = int(options.mins)
else:
	print "Usage: service_mongo_aggregation_half_hourly.py [options]"
	sys.exit(2)

aggregated_data_values = []

def mongo_main():
	global mongo_configs
	docs = []
	#end_time = datetime.now()
	end_time = datetime.now()
	start_time = end_time - timedelta(minutes=time_frame)
	# Read data from mongodb, performance live data
    	docs = sorted(read_data(start_time, end_time, configs=mongo_configs), key=itemgetter('host'))
	print '## Doc len ##'
	print len(docs)
        # Grouping based on hosts names
        group_hosts = groupby(docs, key=itemgetter('host'))
	for host, services in group_hosts:
		#print "$$$$$$$$$$$$$$$$$$$$$$$$$"
		#print host
		# Sort based on services
		host_services = sorted(list(services), key=itemgetter('host'))
		# Grouping based on service types, for a particular host
		group_services = groupby(host_services, key=itemgetter('service'))
                for serv_name, serv_data in group_services:
			#print serv_name
			# Docs for a particular service, to be aggregated
			service_doc_list = list(serv_data)
			# Grouping based on service data source
			service_doc_list = sorted(service_doc_list, key=itemgetter('ds'))
			service_data_source_grouping = groupby(service_doc_list, key=itemgetter('ds'))
			for data_source, values in service_data_source_grouping:
				#print data_source
				#print 'DS Values'
				#print pprint(list(values))
				make_half_hourly_data(list(values))
			#print '###############'


def read_data(start_time, end_time, **configs):
	db = None
	docs = []
       	db = mongo_module.mongo_conn(
		host=configs.get('configs').get('host'),
			port=configs.get('configs').get('port'),
			db_name='nocout'
			)
	print start_time, end_time
	if db:
		#if perf_table == 'network_perf':
		#        cur = db.network_perf.find({"check_time": {"$gt": start_time, "$lt": end_time}})
		#elif perf_table == 'service_perf':
		#        cur = db.service_perf.find({"check_time": {"$gt": start_time, "$lt": end_time}})
		cur = db[perf_table].find({'check_time': {'$gt': start_time, '$lt': end_time}})
        
	for doc in cur:
		docs.append(doc)
	
	return docs


def make_half_hourly_data(docs):
	"""
	Quantifies the perf data in 30 mins time frame
	"""
	
	global aggregated_data_values
	# Aggregated data doc to be inserted into historical mongodb 
	aggr_data = {}
	# Store the hour-wise perf data into a dict
	hour_wise_perf = {}
	host, ip_address = docs[0].get('host'), docs[0].get('ip_address')
	ds, service = str(docs[0].get('ds')), docs[0].get('service')
	site = docs[0].get('site')
	val_frequencies = None
	# These services contain perf which can't be evaluated using regular `min`, `max` functions
	wimax_mrotek_services = ['wimax_ss_sector_id', 'wimax_ss_mac', 'wimax_dl_intrf', 'wimax_ul_intrf', 'wimax_ss_ip', 
			'wimax_modulation_dl_fec', 'wimax_modulation_ul_fec', 'wimax_ss_frequency',
			'rici_line_1_port_state', 'rici_fe_port_state', 'rici_e1_interface_alarm',
			'rici_device_type', 'mrotek_line_1_port_state', 'mrotek_fe_port_state',
			'mrotek_e1_interface_alarm', 'mrotek_device_type']
	for doc in docs:
		data_values = sorted(doc.get('data'), key=itemgetter('time'))
		# Club the data entries based on hour value
		group_values_on_hour = groupby(data_values, key=lambda entry: entry.get('time').hour)
		for hours, hour_values in group_values_on_hour:
			if hours in hour_wise_perf.keys():
			        hour_wise_perf[hours] += list(hour_values)
			else:
				hour_wise_perf[hours] = list(hour_values)

        #print '==== hour_wise_perf ===='
	#pprint(hour_wise_perf)
	for hour, perf in hour_wise_perf.items():
		perf = map(lambda t: convert(t), perf)
		#print '---- perf after eval----------'
		#print perf
		# The aggregated data for the first-half would be pivoted to this time
		f_h_pivot_time = perf[0].get('time').replace(minute=30, second=0, microsecond=0)
		# The aggregated data for the second-half would be pivoted to this time
		s_h_pivot_time = f_h_pivot_time + timedelta(minutes=30)
		# 0 - 30 mins data for the particular hour
		first_half_data = filter(lambda entry: entry.get('time').minute <= 30, perf) 
		if first_half_data:
		        first_half_data_values = map(lambda e: e.get('value'), first_half_data)
			if first_half_data_values[0] == '':
				f_h_min_val, f_h_max_val, f_h_avg_val = None, None, None
			else:
				if service in wimax_mrotek_services:
					f_h_min_val = first_half_data_values[0]
					f_h_max_val = first_half_data_values[0]
					f_h_avg_val = None
				else:
					f_h_min_val = min(first_half_data_values)
					f_h_max_val = max(first_half_data_values)
					f_h_avg_val = sum(first_half_data_values)/len(first_half_data_values)

			aggr_data = {
					'host': str(host),
					'ip_address': str(ip_address),
					'time': f_h_pivot_time,
					'ds': str(ds),
					'service': service,
					'site': str(site),
					'min': f_h_min_val,
					'max': f_h_max_val,
					'avg': f_h_avg_val
					}
			# Find the existing doc to update
			find_query = {
					'host': aggr_data.get('host'),
					'service': aggr_data.get('service'),
					'ds': aggr_data.get('ds'),
					'time': aggr_data.get('time')
					}
			existing_doc, existing_doc_index = find_existing_entry(find_query)
			#print '========================='
			#print 'existing_doc'
			#print existing_doc
			#print 'aggr_data'
			#print aggr_data
			if existing_doc:
				existing_doc = existing_doc[0]
				if service in wimax_mrotek_services:
					val_frequencies = [existing_doc.get('min'), existing_doc.get('max'),
							aggr_data.get('min'), aggr_data.get('max')]
					occur = collections.defaultdict(int)
					for val in val_frequencies:
						occur[val] += 1
					freq_dist = occur.keys()
					max_val = freq_dist[0]
					min_val = freq_dist[-1]
					avg_val = None
				else:
					min_val = min([existing_doc.get('min'), aggr_data.get('min')]) 
					max_val = max([existing_doc.get('max'), aggr_data.get('max')]) 
					if aggr_data.get('avg') and existing_doc.get('avg'):
						avg_val = (existing_doc.get('avg') + aggr_data.get('avg')) / 2
					else:
						avg_val = existing_doc.get('avg')
				aggr_data.update({
					'min': min_val,
					'max': max_val,
					'avg': avg_val
					})
				# First remove the existing entry from aggregated_data_values
				#aggregated_data_values = filter(lambda d: not (set(find_query.values()) <= set(d.values())), aggregated_data_values)
				# First remove the existing entry from aggregated_data_values
				aggregated_data_values.pop(existing_doc_index)
			#print 'Updated aggr_data'
			#print aggr_data
			#upsert_aggregated_data(find_query, aggr_data)
			aggregated_data_values.append(aggr_data)

		# 30 - 60 mins data for the particular hour
	        second_half_data = filter(lambda entry: entry.get('time').minute > 30, perf) 
		#print "-- second half data --"
		#print second_half_data
		if second_half_data:
			#print 'second_half_data ------'
			#print second_half_data
		        second_half_data_values = map(lambda e: e.get('value'), second_half_data)
			#print 'second_half_data_values--'
			#print second_half_data_values
			if second_half_data_values[0] == '':
				s_h_min_val, s_h_max_val, s_h_avg_val = None, None, None
			else:
				if service in wimax_mrotek_services:
					s_h_min_val = second_half_data_values[0]
					s_h_max_val = second_half_data_values[0]
					s_h_avg_val = None
				else:
					s_h_min_val = min(second_half_data_values)
					s_h_max_val = max(second_half_data_values)
					s_h_avg_val = sum(second_half_data_values)/len(second_half_data_values)

			aggr_data = {
					'host': host,
					'ip_address': ip_address,
					'time': s_h_pivot_time,
					'ds': ds,
					'service': service,
					'site': site,
					'min': s_h_min_val,
					'max': s_h_max_val,
					'avg': s_h_avg_val
					}
			# Find the existing doc to update
			find_query = {
					'host': aggr_data.get('host'),
					'service': aggr_data.get('service'),
					'ds': aggr_data.get('ds'),
					'time': aggr_data.get('time')
					}
			existing_doc, existing_doc_index = find_existing_entry(find_query)
			#print '========================='
			#print 'existing_doc'
			#print existing_doc
			#print 'aggr_data'
			#print aggr_data
			if existing_doc:
				existing_doc = existing_doc[0]
				if service in wimax_mrotek_services:
					val_frequencies = [existing_doc.get('min'), existing_doc.get('max'),
							aggr_data.get('min'), aggr_data.get('max')]
					occur = collections.defaultdict(int)
					for val in val_frequencies:
						occur[val] += 1
					freq_dist = occur.keys()
					max_val = freq_dist[0]
					min_val = freq_dist[-1]
					avg_val = None
				else:
					min_val = min([existing_doc.get('min'), aggr_data.get('min')]) 
					max_val = max([existing_doc.get('max'), aggr_data.get('max')]) 
					if aggr_data.get('avg') and existing_doc.get('avg'):
						avg_val = (existing_doc.get('avg') + aggr_data.get('avg')) / 2
					else:
						avg_val = existing_doc.get('avg')
				aggr_data.update({
					'min': min_val,
					'max': max_val,
					'avg': avg_val
					})
				# First remove the existing entry from aggregated_data_values
				#aggregated_data_values = filter(lambda d: not (set(find_query.values()) <= set(d.values())), aggregated_data_values)
				# First remove the existing entry from aggregated_data_values
				aggregated_data_values.pop(existing_doc_index)
			#print 'Updated aggr_data'
			#print aggr_data
			#upsert_aggregated_data(find_query, aggr_data)
			aggregated_data_values.append(aggr_data)


def convert(data):
	if isinstance(data, basestring):
		try:
			data = eval(data)
		except Exception:
		        data =  str(data)
		return data
	elif isinstance(data, collections.Mapping):
		return dict(map(convert, data.iteritems()))
	elif isinstance(data, collections.Iterable):
		return type(data)(map(convert, data))
	else:
	        return data


def find_existing_entry(find_query):
	"""
	Find the doc for update query
	"""

	existing_doc = []
	existing_doc_index = None
	for i in xrange(len(aggregated_data_values)):
		if set(find_query.values()) <= set(aggregated_data_values[i].values()):
			existing_doc = aggregated_data_values[i:i+1]
			existing_doc_index = i
			break

	return existing_doc, existing_doc_index


def usage():
	print "Usage: service_mongo_aggregation_half_hourly.py [options]"


if __name__ == '__main__':
	mongo_main()
	db = mysql_conn(mysql_configs=mysql_configs)
	mysql_export(hist_perf_table, db, aggregated_data_values)
