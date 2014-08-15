"""
events_rrd_migration.py
=======================

This file contains the code for extracting and collecting the nagios events and storing these events in embeded mongodb database.
File contains four functions.

"""

from nocout_site_name import *
import os
from datetime import datetime, timedelta
import imp
import time

utility_module = imp.load_source('utility_functions', '/opt/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
mongo_module = imp.load_source('mongo_functions', '/opt/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/opt/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

def get_latest_event_entry(db_type=None, db=None, site=None,table_name=None):
	"""
                get_latest_event_entry function find the time of latest record in monodb or mysql db.

                Args:
                        db_type: type of data connection 
                
                Kwargs:
                        db (database connection),site (poller on which device is monitored),table_name(name for database table_name)

                Returns:
                        time (int) :
                               latest time from the embeded database or mysql database depending upon calling 
                        Raises:
                               Exception
	"""
	time = None
	# Mongodb Connection
    	if db_type == 'mongodb':
        	cur = db.nocout_host_event_log.find({}, {"check_timestamp": 1}).sort("_id", -1).limit(1)
        	for c in cur:
                	entry = c
                	time = entry.get('check_timestamp')
	# MYSQL Connection
    	elif db_type == 'mysql':
        	query = "SELECT `check_timestamp` FROM `%s` WHERE" % table_name +\
                " `site_name` = '%s' ORDER BY `check_timestamp` DESC LIMIT 1" % (site)
        	cursor = db.cursor()
        	cursor.execute(query)
        	entry = cursor.fetchone()
        	try:
            		time = entry[0]
			return time
        	except TypeError, e:
            		cursor.close()
           		return time

        	cursor.close()

	return time

def service_perf_data_live_query(db,site,log_split):
	"""
                service_perf_data_live_query function perform the live query for service for which log is received and store
		the event data in the embeded mongodb database.

                Args: 
                        db: database connection either mysql or mongodb 
                
                Kwargs:
                        site (on which poller device is monitored),nagios log

                Returns:
                        None
                        Raises:
                              No Exception
        """

	# Adding check for not storing data for check_mk service
	if log_split[5] == 'Check_MK':
		return
	if log_split[0] == "CURRENT SERVICE STATE":
		host_ip = log_split[12]
		description=log_split[11]
	elif log_split[0] == "SERVICE ALERT" or log_split[0] == "INITIAL SERVICE STATE":
		host_ip = log_split[12]
		description=log_split[11]
	elif log_split[0] == "SERVICE FLAPPING ALERT":
		host_ip = log_split[10]
		description=log_split[9]
	# calculating the perf_data for all services except for inventory services as they do not have performance data
	if 'invent' not in log_split[5]:
		query = "GET services\nColumns: service_perf_data\nFilter: service_description ~ %s\nFilter: host_name = %s\n" % ( 
		log_split[5],log_split[4]) 
		perf_data= utility_module.get_from_socket(site, query)
		perf_data = utility_module.get_threshold(perf_data)
		
		for ds in perf_data.iterkeys():
			# Adding check for not storing data for rtmin and rtmax data source of ping services
			if ds =='rtmin' or ds == 'rtmax':
				continue
			cur =perf_data.get(ds).get('cur')
			war =perf_data.get(ds).get('war')
			crit =perf_data.get(ds).get('cric')
			if ds == 'pl':
				cur=cur.strip('%')				
			serv_event_dict=dict(sys_timestamp=int(log_split[1]),device_name=log_split[4],severity=log_split[8],
					description=description,min_value=0,max_value=0,avg_value =0,current_value=cur,
					data_source = ds,warning_threshold=war,
					critical_threshold =crit ,check_timestamp = int(log_split[1]),
					ip_address=host_ip,service_name=log_split[5],site_name=site)
			if log_split[5] == 'PING':
				serv_event_dict.update({"service_name":"ping"})
                		mongo_module.mongo_db_insert(db,serv_event_dict,"host_event")
				print "data inserted in mongodb"
			else:
				mongo_module.mongo_db_insert(db,serv_event_dict,"serv_event")
				print "data inserted in mongodb"

	# extracting the inventory plugin output ,as these services don't have performance data
	elif 'invent' in log_split[5]:
		query = "GET services\nColumns: service_plugin_output\nFilter: service_description ~ %s\nFilter: host_name = %s\n" %(
		log_split[5],log_split[4]) 
		try:
			perf_data= utility_module.get_from_socket(site, query)
			current_value = perf_data.split('- ')[1].strip('\n')
		except:
			current_value =None
		serv_event_dict=dict(sys_timestamp=int(log_split[1]),device_name=log_split[4],severity=log_split[8],
                                description=description,min_value=0,max_value=0,avg_value =0,
				current_value=current_value,
				data_source = log_split[5],warning_threshold=0,
				critical_threshold =0 ,check_timestamp = int(log_split[1]),
				ip_address=host_ip,service_name=log_split[5],site_name=site)
		mongo_module.mongo_db_insert(db,serv_event_dict,"serv_event")



def network_perf_data_live_query(db,site,log_split):
	"""
                network_perf_data_live_query function live query to ping services and stores performance data and extracts and 
		stores the events data in mongodb.

                Args: 
                        db: database connection instance 
                
                Kwargs:
                        site(poller on which device is monitored),nagios log

                Returns:
                        None
                        Raises:
                               No Exception
        """


	query = "GET hosts\nColumns: host_perf_data\nFilter: host_name = %s\n" % (log_split[4]) 
	perf_data= utility_module.get_from_socket(site, query)
	host_perf_data = utility_module.get_threshold(perf_data)
	if log_split[0] == "CURRENT HOST STATE":
		host_ip = log_split[11]
		description=log_split[10]
	elif log_split[0] == "HOST ALERT" or log_split[0] == "INITIAL HOST STATE":
		host_ip = log_split[11]
		description=log_split[10]
	elif log_split[0] == "HOST FLAPPING ALERT":
		host_ip = log_split[9]
		description=log_split[8]
	for ds in host_perf_data.iterkeys():
		if ds == 'rtmin' or ds == 'rtmax':
			continue
		host_cur =host_perf_data.get(ds).get('cur')
		host_war =host_perf_data.get(ds).get('war')
		host_crit =host_perf_data.get(ds).get('cric')
		if ds == 'pl':
			host_cur=host_cur.strip('%')				
		host_event_dict=dict(sys_timestamp=int(log_split[1]),device_name=log_split[4],severity=log_split[7],
                		description=description,min_value=0,max_value=0,avg_value=0,current_value=host_cur,
				data_source=ds,warning_threshold=host_war,critical_threshold=host_crit,
				check_timestamp=int(log_split[1]),
				ip_address=host_ip,site_name=site,service_name='ping')
		# mongo db insertion
                mongo_module.mongo_db_insert(db,host_event_dict,"host_event")



def extract_nagios_events_live(mongo_host, mongo_db, mongo_port):
	"""
                Main function for extracting the nagios events from log files and seperating them in based on services

                Args: 
                        db: mongo_host (query for host) (device on which event is triggered) 
                
                Kwargs:
                        mongo_db (mongo_db connection type),mongo_port(port of mongo db on which connection is opened)

                Returns:
                        None
                        Raises:
                               No Exception
        """

	db = None
	perf_data  = {}
        file_path = os.path.dirname(os.path.abspath(__file__))
        path = [path for path in file_path.split('/')]
	war = None
	crit = None
	cur = None
        if 'sites' not in path:
                raise Exception, "File is not in omd specific directory"
        else:
                site = path[path.index('sites')+1]
	
        db = mongo_module.mongo_conn(
		host=mongo_host,
		port=mongo_port,
		db_name=mongo_db
	)
	utc_time = datetime(1970, 1,1,5,30)

	# time for which nagios events are extracted
	#start_epoch = get_latest_event_entry(db_type = 'mongodb',db=db)
	#if start_epoch == None:
	start_time = datetime.now() - timedelta(minutes=1)
	start_epoch = int(time.mktime(start_time.timetuple()))

        end_time = datetime.now()
	end_epoch = int(time.mktime(end_time.timetuple()))

        # sustracting 5.30 hours        
        host_event_dict ={}
        serv_event_dict={}

	# query for the extracting the log from nagios .This query is only for services except ping
	query = "GET log\nColumns: log_type log_time log_state_type log_state  host_name service_description "\
		"options host_address current_service_perf_data\nFilter: log_time > %s\nFilter: class = 0\nFilter: class = 1\n"\
		"Filter: class = 2\nFilter: class = 3\nFilter: class = 4\nFilter: class = 6\nOr: 6\n" %(start_epoch) 
	output= utility_module.get_from_socket(site, query)
	for log_attr in output.split('\n'):
		log_split = [log_split for log_split in log_attr.split(';')]
		if log_split[0] == "CURRENT SERVICE STATE":
			service_perf_data_live_query(db,site,log_split)
		elif log_split[0] == "SERVICE ALERT" or log_split[0] == "INITIAL SERVICE STATE":
			service_perf_data_live_query(db,site,log_split)
		elif log_split[0] == "SERVICE FLAPPING ALERT":
			service_perf_data_live_query(db,site,log_split)

	# query for the extracting the log from nagios .This query is ping serviecs
	query = "GET log\nColumns: log_type log_time log_state_type log_state  host_name service_description "\
		"options host_address current_host_perf_data\nFilter: log_time > %s\nFilter: class = 0\n"\
		"Filter: class = 1\nFilter: class = 2\nFilter: class = 3\nFilter: class = 4\nFilter: class = 6\nOr: 6\n" %(start_epoch) 
	output= utility_module.get_from_socket(site, query)

	for log_attr in output.split('\n'):
		log_split = [log_split for log_split in log_attr.split(';')]
		if log_split[0] == "CURRENT HOST STATE":
			network_perf_data_live_query(db,site,log_split)	
		elif log_split[0] == "HOST ALERT" or log_split[0] == "INITIAL HOST STATE":
			network_perf_data_live_query(db,site,log_split)	
		elif log_split[0] == "HOST FLAPPING ALERT":
			network_perf_data_live_query(db,site,log_split)	
		
if __name__ == '__main__':
    """
    Main function for this file which keeps track of the all services and host events.This script is regularly called with 1 min interval

    """
    configs = config_module.parse_config_obj()
    configs = config_module.parse_config_obj()
    desired_site = filter(lambda x: x == nocout_site_name, configs.keys())[0]
    desired_config = configs.get(desired_site)
    site = desired_config.get('site')
    extract_nagios_events_live(
			mongo_host=desired_config.get('host'),
			mongo_db=desired_config.get('nosql_db'),
			mongo_port=int(desired_config.get('port'))
    )
