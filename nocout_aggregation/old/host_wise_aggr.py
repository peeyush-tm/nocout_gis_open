from __future__ import absolute_import
import time
import sys
from datetime import datetime, timedelta
from pprint import pprint
import collections
from random import randint
from operator import itemgetter
from itertools import groupby
from celery import chord, chain, group
from celery.exceptions import WorkerLostError as WLE

from historical_mysql_export import mysql_export
from entry import app


@app.task(name='reducer')
def reducer(it):
    return it


#@app.task(name='quantify_perf_data_caller', ignore_result=True)
#def call_quantify_perf_data(host_data_list, **kw):
#    if not host_data_list:
#	return
#    chord(
#	group(
#	    chain(
#		quantify_perf_data.s(list(host_data), time_frame=kw.get('time_frame'),
#			table=kw.get('destination_perf_table')), 
#		calc_values.s()
#	    )
#	    for host_key, host_data in groupby(host_data_list, key=itemgetter(0))
#	    ), 
#	collector.s(kw.get('destination_perf_table'))
#    ).apply_async()


#@app.task(name='collector', ignore_result=True)
#def collector(it, table):
#    # TODO : call the inserts in batches or some other mech
#    if it:
#        mysql_export.s(table, sum(it, [])).apply_async(countdown=randint(10, 100))


@app.task(name='per-host-aggr', time_limit=60*6, ignore_result=True)
def quantify_perf_data(host_specific_data, **kw):
    time_frame = kw.get('time_frame')
    host_specific_aggregated_data = []
    for doc in host_specific_data:
	try:
            # need to convert `str` into proper int, float values, where ever possible
            doc = type_caste(doc)
            # These services contain perf which can't be evaluated using regular `min`, `max` functions
            wimax_mrotek_services = ['wimax_ss_sector_id', 'wimax_ss_mac', 
		'wimax_dl_intrf', 'wimax_ul_intrf', 'wimax_ss_ip',
                'wimax_modulation_dl_fec', 'wimax_modulation_ul_fec', 'wimax_ss_frequency',
                'rici_line_1_port_state', 'rici_fe_port_state', 'rici_e1_interface_alarm',
                'rici_device_type', 'mrotek_line_1_port_state', 'mrotek_fe_port_state',
                'mrotek_e1_interface_alarm', 'mrotek_device_type']
            aggr_data = ()
            find_query = ()

            # sys timestamp
            time = datetime.fromtimestamp(doc[12])
            check_time = doc[13]

            if time_frame == 'half_hourly':
                if time.minute < 30:
                    # Pivot the time to second half of the hour
                    time = time.replace(minute=30, second=0, microsecond=0)
                else:
                    # Pivot the time to next hour
                    time = time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            elif time_frame == 'hourly':
                #time = (datetime.now()).replace(minute=0, second=0, microsecond=0)
                time = time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            elif time_frame == 'daily':
                time = (datetime.now()).replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_frame == 'weekly':
                time = (datetime.now()).replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_frame == 'monthly':
                time = (datetime.now()).replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_frame == 'yearly':
                # Pivot the time to year end
                time = time.replace(month=12, day=31, hour=23, minute=55,
                    second=0, microsecond=0)
            if doc[8] in (None, ''):
                continue
            # Ex. ('host_name', 'radwin_rssi', 'rssi', -78, [-79], [-74], [-77.7])
            aggr_data = (doc[0], doc[1], doc[2], doc[6], [doc[7]], [doc[8]], [doc[9]])
            find_query = (doc[0], doc[1], doc[2])

            existing_doc, existing_doc_index = find_existing_entry(find_query, host_specific_aggregated_data)

            if existing_doc:
                existing_doc = existing_doc[0]
                try:
                    aggr_data[4] += existing_doc[7]
                except:
                    pass
                try:
                    aggr_data[5] += existing_doc[8]
                except:
                    pass
                try:
                    aggr_data[6] += existing_doc[9]
                except:
                    pass

	        host_specific_aggregated_data.pop(existing_doc_index)
	    try:
	        aggr_data = (
			doc[0], doc[1], doc[2], doc[3], doc[4], doc[5], 
			doc[6], aggr_data[4], aggr_data[5], aggr_data[6], 
			doc[10], doc[11], time, check_time, doc[14], doc[15]
			)
	    except:
	        print 'Exception in aggr_data !!'
	        continue
            host_specific_aggregated_data.append(aggr_data)
	except Exception as exc:
	    print 'Exc in host aggr data, ', exc
    # call calc_values, instead of returning result
    calc_values.s(host_specific_aggregated_data, 
	destination_perf_table=kw.get('destination_perf_table')
	).apply_async()


@app.task(name='calc_values', bind=True, time_limit=60*6, ignore_result=True)
def calc_values(self, docs, **kw):
    try:
	    if not docs:
		print '@@@ No Doc @@@'
		return []
	    wimax_mrotek_services = [
				'wimax_ss_sector_id', 'wimax_ss_mac', 
				'wimax_dl_intrf', 'wimax_ul_intrf', 'wimax_ss_ip',
				'wimax_modulation_dl_fec', 'wimax_modulation_ul_fec', 
				'wimax_ss_frequency', 'rici_line1_port_state', 
				'rici_fe_port_state', 'rici_e1_interface_alarm',
				'rici_device_type', 'mrotek_line1_port_state', 
				'mrotek_fe_port_state','mrotek_e1_interface_alarm', 
				'mrotek_device_type'
				]
	    calculated_values = []
	    for doc in docs:
		    final_tup = ()
		    current_value = doc[6]
		    min_list = doc[7]
		    max_list = doc[8]
		    avg_list = doc[9]
		    service = doc[1]
		    if str(doc[2]) == 'rta':
			min_list = [x for x in min_list if x != 0]
			if not min_list:
			    min_list = [0.0]
			max_list = [x for x in max_list if x != 0]
			if not max_list:
			    max_list = [0.0]
			avg_list = [x for x in avg_list if x != 0]
			if not avg_list:
			    avg_list = [0.0]

		    if (service in wimax_mrotek_services or '_status' in service or 
			'_invent' in service):
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
			try:
			    min_val = min(min_list)
			    max_val = max(max_list)
			    avg_val = sum(avg_list)/float(len(avg_list))
			except:
			    avg_val = None
		    try:
			    current_value = "{0:.2f}".format((float(current_value)))
			    min_value = "{0:.2f}".format((float(min_val)))
			    max_value = "{0:.2f}".format((float(max_val)))
			    avg_value = "{0:.2f}".format((float(avg_val)))
		    except:
			    current_value = current_value
			    min_value = min_val
			    max_value = max_val
			    avg_value = avg_val
		    final_tup = (doc[0], doc[1], doc[2], doc[3], doc[4], doc[5], 
				current_value, min_value, max_value, avg_value, 
				doc[10], doc[11], doc[12].strftime('%s'),
				doc[13], doc[14], doc[15])
	    	    calculated_values.append(final_tup)
    except WLE as exc:
	print 'WLE !! retrying...'
	raise self.retry(args=docs, max_retries=1, countdown=20, exc=exc)

    # call mysql insert, instead of returning result
    mysql_export.s(kw.get('destination_perf_table'), calculated_values
	).apply_async(countdown=randint(10, 100))


@app.task(name='type_caste')
def type_caste(data):
    evaled_data = ()
    for v in data:
        try:
            v = eval(v)
        except:
            pass
        evaled_data += (v,)
    return evaled_data


@app.task(name='existing_entry')
def find_existing_entry(find_query, host_specific_aggregated_data):
    """
    Find the doc for update query
    """

    existing_doc = []
    existing_doc_index = None
    find_values = set(find_query)
    for i in xrange(len(host_specific_aggregated_data)):
        find_in = set((host_specific_aggregated_data[i][0],
			host_specific_aggregated_data[i][1],
                        host_specific_aggregated_data[i][2]))
        if find_values <= find_in:
            existing_doc = host_specific_aggregated_data[i:i+1]
            existing_doc_index = i
            break

    return existing_doc, existing_doc_index

