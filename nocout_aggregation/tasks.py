"""
tasks.py
========
Defines aggregation tasks

"""

import collections
from datetime import datetime, timedelta
from random import randint
import resource

from celery.utils.log import get_task_logger

from db_tasks import mysql_export
from entry import app

logger = get_task_logger(__name__)
info, warning, critical = (logger.info, logger.warning,
                           logger.critical)



@app.task(name='per-host-aggr-new', time_limit=60 * 10, ignore_result=True)
def quantify_perf_data(host_specific_data, **kw):
	""" """
	if not host_specific_data:
		return
	#warning('Data len: %s' % len(host_specific_data))
	#warning('Memory usage %s kb()' % 
	#		resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
	time_frame = kw.get('time_frame')
	host_specific_aggregated_data = []
	timestamp = datetime.now().replace(second=0, microsecond=0)
	day, mon = timestamp.day, timestamp.month
	hr, min = timestamp.hour, timestamp.minute
	if time_frame == 'half_hourly':
		if timestamp.minute < 30:
			min = 0
		else:
			min = 30
	elif time_frame == 'hourly':
		min = 0
	elif time_frame in ('daily', 'weekly', 'monthly'):
		hr = min = 0
	elif time_frame == 'yearly':
		hr, min = 23, 0
	timestamp = timestamp.replace(day=day, month=mon, hour=hr, minute=min)
	check_time = host_specific_data[-1][13]

	# extra condition added bcz inventory and interface tables
	# does not contain min, max and avg in live tables
	interface_daily_cond = (host_specific_data[0][1].endswith('_status') 
			and time_frame == 'daily')
	inventory_daily_cond = (host_specific_data[0][1].endswith('_invent') 
			and time_frame == 'daily')
	util_bihourly_cond = ('utilization' in kw.get('destination_perf_table')
			and time_frame == 'half_hourly')

	for doc in host_specific_data:
		try:
			# need to convert `str` into proper int, float values, where ever possible
			doc = type_caste(doc)
			#warning('***DOC***{0}'.format(doc))
			aggr_data = ()
			find_query = ()

			# sys timestamp
			#time = datetime.fromtimestamp(doc[12])
			#check_time = doc[13]

			if doc[8] in (None, ''):
				continue

			# Ex. ('host_name', 'radwin_rssi', 'rssi', -78, [-79], [-74], [-77.7])
			if (interface_daily_cond or inventory_daily_cond or 
					util_bihourly_cond):
				aggr_data = (doc[0], doc[1], doc[2], doc[6], [doc[6]], 
						[doc[6]], [doc[6]])
			else:
				aggr_data = (doc[0], doc[1], doc[2], doc[6], [doc[7]], 
						[doc[8]], [doc[9]])
			#warning('aggr_data: {0}'.format(aggr_data))

			find_query = (doc[0], doc[1], doc[2])

			existing_doc, existing_doc_index = find_existing_entry(find_query,
					host_specific_aggregated_data)

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
					doc[10], doc[11], timestamp, check_time, doc[14], doc[15]
				)
				#warning('+++updated aggr_data++{0}'.format(aggr_data))
			except:
				print 'Exception in aggr_data !!'
				continue
			host_specific_aggregated_data.append(aggr_data)
		except Exception as exc:
			print 'Exc in host aggr data, ', exc

	# call calc_values, instead of returning result
	calc_values(host_specific_aggregated_data, 
			destination_perf_table=kw.get('destination_perf_table'))


@app.task(name='calc_values-new', time_limit=60 * 6, ignore_result=True)
def calc_values(docs, **kw):
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
			'mrotek_fe_port_state', 'mrotek_e1_interface_alarm',
			'mrotek_device_type'
		]
		calculated_values = []
		for doc in docs:
			#warning('%%%calculated doc%%%{0}'.format(doc))
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

				#warning('service: %s; min-list: %s; max-list: %s; avg-list: %s' % (
					#service, min_list, max_list, avg_list))
			else:
				try:
					min_val = min(min_list)
					max_val = max(max_list)
					avg_val = sum(avg_list) / float(len(avg_list))
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
			#warning('###final calculated doc###{0}'.format(final_tup))
			calculated_values.append(final_tup)

	except Exception as exc:
		warning('Problem in calc_values: %s' % exc)
	# call mysql insert, instead of returning result  
	mysql_export.s(kw.get('destination_perf_table'), calculated_values
			).apply_async(countdown=randint(10, 40))


@app.task(name='type_caste-new')
def type_caste(data):
	evaled_data = ()
	for i, v in enumerate(data):
		if i in xrange(6, 10):
		    try:
			v = eval(v)
		    except:
			pass
		evaled_data += (v,)
	return evaled_data


@app.task(name='existing_entry-new')
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
			existing_doc = host_specific_aggregated_data[i:i + 1]
			existing_doc_index = i
			break

	return existing_doc, existing_doc_index
