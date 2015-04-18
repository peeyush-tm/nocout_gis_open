"""
utilization_aggregation.py
==================================

Usage ::
python utilization_aggregation.py -r mongodb -t 24 -f daily -s kpi_data -d performance_utilizationdaily
python utilization_aggregation.py -r mysql -t 168 -f weekly -s performance_utilizationdaily -d performance_utilizationweekly
python utilization_aggregation.py -r mysql -t 720 -f monthly -s performance_utilizationweekly -d performance_utilizationmonthly
python utilization_aggregation.py -r mysql -t 8640 -f yearly -s performance_utilizationmonthly -d performance_utilizationyearly
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
from operator import itemgetter
import optparse
from itertools import groupby
import collections

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
parser.add_option('-r', '--read_from', dest='read_from', type='str')
parser.add_option('-s', '--source', dest='source_db', type='str')
parser.add_option('-d', '--destination', dest='destination_db', type='str')
parser.add_option('-t', '--hours', dest='hours', type='choice', choices=['0.5', 
'1', '24', '168', '720', '8640'])
parser.add_option('-f', '--timeframe', dest='timeframe', type='choice', choices=[
'half_hourly', 'hourly', 'daily', 'weekly', 'monthly', 'yearly'])
options, remainder = parser.parse_args(sys.argv[1:])
if options.source_db and options.destination_db and options.hours and \
        options.timeframe and options.read_from:
    read_from = options.read_from
    source_perf_table=options.source_db
    destination_perf_table=options.destination_db
    hours = float(options.hours)
    time_frame = options.timeframe
else:
    print "Usage: service_mongo_aggregation_hourly.py [options]"
    sys.exit(2)



def prepare_data(aggregated_data_values=[]):
    """
    Quantifies (int, float) utilization data using `min`, `max` and `sum` funcs
    """
    
    data_values = []
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    start_time = start_time - timedelta(minutes=1)
    start_time, end_time = int(start_time.strftime('%s')), int(end_time.strftime('%s'))
    if read_from == 'mysql':
        db = mysql_migration_mod.mysql_conn(mysql_configs=mysql_configs)
        if db:
            # Read data from mysqldb, performance historical data
            data_values = mysql_migration_mod.read_data(source_perf_table, db, start_time, end_time)
    elif read_from == 'mongodb':
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        start_time, end_time = start_time - timedelta(minutes=1), end_time + timedelta(minutes=1)
        # Read data from mongodb, performance live data
        data_values = mysql_migration_mod.read_data_from_mongo(source_perf_table, start_time, end_time, mongo_configs, kpi=True)

    data_values = sorted(data_values, key=itemgetter('device_name'))
    print 'Data Values', len(data_values)
    for host, host_values in groupby(data_values, key=itemgetter('device_name')):
        aggregated_data_values.extend(quantify_utilization_data(list(host_values)))
    
    return aggregated_data_values


def quantify_utilization_data(host_specific_data):
    freq_based_util_services = ['wimax_ss_provis_kpi', 'cambium_ss_provis_kpi',
		'radwin_ss_provis_kpi', 'cambium_ss_ul_issue_kpi', 'wimax_ss_ul_issue_kpi']
    host_specific_aggregated_data = []
    #print '## Docs len ##'
    #print len(data_values)
    for doc in host_specific_data:
	doc = type_caste(doc)
        aggr_data = {}
        find_query = {}

        host = doc.get('device_name') if doc.get('device_name') else doc.get('host')
        ip_address = doc.get('ip_address')
        ds = str(doc.get('data_source')) if doc.get('data_source') else str(doc.get('ds'))
        severity = doc.get('severity')
        service = str(doc.get('service_name')) if doc.get('service_name') else str(doc.get('service'))
        site = doc.get('site_name') if doc.get('site_name') else doc.get('site')
        check_time = doc.get('check_timestamp') if doc.get('check_timestamp') else doc.get('check_time')
        if read_from == 'mysql':
            time = float(doc.get('sys_timestamp'))
            check_time = datetime.fromtimestamp(check_time)
            original_time, time = time, datetime.fromtimestamp(time)
        elif read_from == 'mongodb':
            time = doc.get('local_timestamp') if doc.get('local_timestamp') else doc.get('sys_timestamp')
	try:
            current_value = eval(doc.get('current_value'))
	except:
	    current_value = doc.get('current_value')
        war, cric = doc.get('warning_threshold'), doc.get('critical_threshold')
        # `refer` field to store Ckt-id for current device
        refer = str(doc.get('refer'))

        if time_frame == 'half_hourly':
            if time.minute < 30:
                # Pivot the time to second half of the hour
                time = time.replace(minute=30, second=0, microsecond=0)
            else:
                # Pivot the time to next hour
                time = time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif time_frame == 'hourly':
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
        elif time_frame == 'monthly':
            # Pivot the time to 23:55:00 of month end
            time = time.replace(month=time.month+1, day=1, hour=23, minute=55,
                    second=0, microsecond=0) - timedelta(days=1)
        elif time_frame == 'yearly':
            # Pivot the time to year end
            time = time.replace(month=12, day=31, hour=23, minute=55,
                    second=0, microsecond=0)

        aggr_data = {
                'host': host,
                'service': service,
                'ds': ds,
                'site': site,
                'time':time,
                'ip_address': ip_address,
                'current_value': current_value,
                'severity': severity,
                'war': war,
                'cric': cric,
                'refer': refer,
                'check_time': check_time
                }
	if read_from == 'mysql':
	    #try:
	     #   mn, mx, ag = eval(doc.get('min_value')), eval(doc.get('max_value')), eval(doc.get('avg_value'))
	   # except:
	    mn, mx, ag = doc.get('min_value'), doc.get('max_value'), doc.get('avg_value')
            aggr_data.update({
                'min': mn,
                'max': mx,
                'avg': ag,
            })
        elif read_from == 'mongodb':
            aggr_data.update({
                'min': current_value,
                'max': current_value,
                'avg': current_value,
            })
	# do not process, if doc doesn't contain a valid value in max/min/avg field
        if aggr_data.get('max') in (None, ''):
            continue
	aggr_data.update({
                'min': [aggr_data.get('min')],
                'max': [aggr_data.get('max')],
                'avg': [aggr_data.get('avg')],
                })

        # Find the existing doc to update
        find_query = {
                #'host': doc.get('host'),
                'service': aggr_data.get('service'),
                'ds': aggr_data.get('ds'),
                'refer': refer,
                #'time': time
                }
        existing_doc, existing_doc_index = find_existing_entry(find_query, host_specific_aggregated_data)
        #print 'existing_doc'
        #print existing_doc
        if existing_doc:
            existing_doc = existing_doc[0]
	    #existing_doc = type_caste(existing_doc)
            #values_list = [existing_doc.get('max'), aggr_data.get('max'), 
            #        existing_doc.get('min'), aggr_data.get('min')]
	    #values_list = [x for x in values_list if x != None]
	    #if not values_list:
	#	values_list = [None]
	#    if service in freq_based_util_services:
	#	# Calculation based on number of occurrences
	#	occur = collections.defaultdict(int)
        #        for val in values_list:
        #            occur[val] += 1
        #        freq_dist = occur.keys()
        #        min_val = freq_dist[0]
        #        max_val = freq_dist[-1]
        #        avg_val = None
	#    else:
	#	# Calculation based on normal min, max and avg
	#	if values_list:
	#		min_val = min(values_list) 
	#		max_val = max(values_list) 
        #        if existing_doc.get('avg') and aggr_data.get('avg'):
        #            avg_val = (float(str((existing_doc.get('avg')))) + float(str((aggr_data.get('avg')))))/ 2.0
	#	elif aggr_data.get('avg'):
	#	    avg_val = aggr_data.get('avg') 
        #        else:
        #            avg_val = existing_doc.get('avg')
        #    aggr_data.update({
        #        'min': min_val,
        #        'max': max_val,
        #        'avg': avg_val
        #        })
	    aggr_data['min'] += existing_doc['min']
            aggr_data['max'] += existing_doc['max']
            aggr_data['avg'] += existing_doc['avg']
            # First remove the existing entry from aggregated_data_values
            host_specific_aggregated_data.pop(existing_doc_index)
	# round floats to 2 decimal places
	# since we cant round to 2 decimal places in python <= 2.6, directly,
	# convert these values to str instead
	#try:
        #    aggr_data['current_value'] = "{0:.2f}".format((float(aggr_data['current_value'])))
	#    aggr_data['min'] = "{0:.2f}".format((float(aggr_data['min'])))
	#    aggr_data['max'] = "{0:.2f}".format((float(aggr_data['max'])))
	#    aggr_data['avg'] = "{0:.2f}".format((float(aggr_data['avg'])))
	#except:
	#    # dont change any thing
	#    pass
        host_specific_aggregated_data.append(aggr_data)
    
    return host_specific_aggregated_data


def calc_values(data):
    freq_based_util_services = ['wimax_ss_provis_kpi', 'cambium_ss_provis_kpi',
		'radwin_ss_provis_kpi', 'cambium_ss_ul_issue_kpi', 'wimax_ss_ul_issue_kpi']
    for doc in data:
        current_value = doc.get('current_value')
        min_list = doc.get('min')
        max_list = doc.get('max')
        avg_list = doc.get('avg')
        service = str(doc['service'])
        if service in freq_based_util_services:
                occur = collections.defaultdict(int)
                for val in min_list:
                    occur[val] += 1
                min_val = min(occur, key=occur.get)

                occur = collections.defaultdict(int)
                for val in max_list:
                    occur[val] += 1
                max_val = max(occur, key=occur.get)
                avg_val = None
        else:
            min_val = min(min_list)
            max_val = max(max_list)
            avg_val = sum(avg_list)/float(len(avg_list))
	try:
            doc['current_value'] = "{0:.2f}".format((float(current_value)))
            doc['min'] = "{0:.2f}".format((float(min_val)))
            doc['max'] = "{0:.2f}".format((float(max_val)))
            doc['avg'] = "{0:.2f}".format((float(avg_val)))
        except:
            doc['current_value'] = current_value
            doc['min'] = min_val
            doc['max'] = max_val
            doc['avg'] = avg_val
    return data


def type_caste(data):
    #if isinstance(data, basestring):
#       try:
#           return eval(data)
#       except:
#           return data
 #   elif isinstance(data, collections.Mapping):
  #      return dict(map(type_caste, data.iteritems()))
   # elif isinstance(data, collections.Iterable):
    #    return type(data)(map(type_caste, data))
    #else:
   #     return data
    for k, v in data.iteritems():
        try:
            v = eval(v)
        except:
            pass
        data.update({k: v})
    return data


def find_existing_entry(find_query, host_specific_aggregated_data):
    """
    Find the doc for update query
    """
       
    existing_doc = []
    existing_doc_index = None
    find_values = set(find_query.values())
    for i in xrange(len(host_specific_aggregated_data)):
	find_in = set([host_specific_aggregated_data[i].get('host'),
                host_specific_aggregated_data[i].get('ds'),
                host_specific_aggregated_data[i].get('service')])
        if find_values <= find_in:
            existing_doc = host_specific_aggregated_data[i:i+1]
            existing_doc_index = i
            break
    #docs = filter(lambda d: set(find_query.values()) <= set(d.values()), aggregated_data_values)

    return existing_doc, existing_doc_index

def usage():
    print "Usage: service_mongo_aggregation_hourly.py [options]"


if __name__ == '__main__':
    final_data_values = prepare_data()
    final_aggr_data_values = calc_values(final_data_values)
    print 'Final Data Values'
    print len(final_aggr_data_values)
    if final_aggr_data_values:
        db = mysql_migration_mod.mysql_conn(mysql_configs=mysql_configs)
        mysql_migration_mod.mysql_export(destination_perf_table, db, final_aggr_data_values)
