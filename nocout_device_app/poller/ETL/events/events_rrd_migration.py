"""
events_rrd_migration.py
=======================

This file contains the code for extracting and collecting the nagios events and storing these events in embeded mongodb database.
File contains four functions.

"""

from nocout_site_name import *
import os
from datetime import datetime, timedelta
from pprint import pformat
import imp
import time
from copy import deepcopy

utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)
db_ops_module = imp.load_source('db_ops', '/omd/sites/%s/lib/python/handlers/db_ops.py' % nocout_site_name)

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
            cursor.close()
            return time
        except TypeError, e:
                cursor.close()
                return time


    return time

def service_perf_data_live_query(site, log_split, service_events_data, service_events_update_criteria):
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

    host_ip = log_split[12]
    description=log_split[11]
    description_current_value = description[(description.find('-')+2):description.find(':')]
    # calculating the perf_data for all services except for inventory services as they do not have performance data
    #if 'invent' not in log_split[5]:
    #    query = "GET services\nColumns: service_last_state_change service_perf_data\n"+\
    #        "Filter: service_description ~ %s\nFilter: host_name = %s\n" % (log_split[5],log_split[4]) 
    #    perf_data= utility_module.get_from_socket(site, query)
    #    age1 =int(perf_data.split(';',1)[0])
    #    perf_data1 = perf_data.split(';',1)[-1]
    #    perf_data = utility_module.get_threshold(perf_data1)
    #         
    #    for ds in perf_data.iterkeys():
    #        # Adding check for not storing data for rtmin and rtmax data source of ping services
    #        if ds =='rtmin' or ds == 'rtmax':
    #            continue
    #        cur =perf_data.get(ds).get('cur')
    #        war =perf_data.get(ds).get('war')
    #        crit =perf_data.get(ds).get('cric')
    #        if ds == 'pl':
    #            cur=cur.strip('%')                
    #        serv_event_dict=dict(sys_timestamp=int(log_split[1]),device_name=log_split[4],severity=log_split[8],
    #                description=description,min_value=0,max_value=0,avg_value =0,current_value=cur,
    #                data_source = ds,warning_threshold=war,
    #                critical_threshold =crit ,check_timestamp = int(log_split[1]),
    #                ip_address=host_ip,service_name=log_split[5],site_name=site,age=age1)
    #        if log_split[5] == 'PING':
    #            serv_event_dict.update({"service_name":"ping"})
    #            mongo_module.mongo_db_insert(db,serv_event_dict,"host_event")
    #            print "data inserted in mongodb"
    #        else:
    #            mongo_module.mongo_db_insert(db,serv_event_dict,"serv_event")
    #            print "data inserted in mongodb"

    # extracting the inventory plugin output ,as these services don't have performance data
    #elif 'invent' in log_split[5]:
    #    query = "GET services\nColumns: service_plugin_output\nFilter: service_description ~ %s\nFilter: host_name = %s\n" %(
    #    log_split[5],log_split[4]) 
    #    try:
    #        perf_data= utility_module.get_from_socket(site, query)
    #        age1 =int(perf_data.split(';',1)[0])
    #        perf_data1 = perf_data.split(';',1)[-1]
    #        current_value = perf_data1.split('- ')[1].strip('\n')
    #    except:
    #        current_value =None

    # Forward the time stamp, with `second` attribute equal to zero
    t_stmp = datetime.fromtimestamp(float(log_split[1]))
    altered_timestamp = (t_stmp.replace(second=0)).strftime('%s')

    serv_event_dict=dict(sys_timestamp=int(altered_timestamp),device_name=log_split[4],severity=log_split[8],
            description=description,min_value=0, max_value=0, avg_value=0,current_value=0,
            data_source = None,warning_threshold=0,critical_threshold =0 ,
            check_timestamp = int(log_split[1]),ip_address=host_ip,service_name=log_split[5],
            site_name=site,age=int(log_split[-1]))

    # For this case we don't take service ds into consideration
    matching_criteria = {
            'device_name': log_split[4],
            'service_name': log_split[5]
            }
    # Mongo db updation
    service_events_update_criteria.append(matching_criteria)
    #mongo_module.mongo_db_update(db, matching_criteria, serv_event_dict, 'service_event_status')
    # Mongo db insertion
    service_events_data.append(serv_event_dict)
    #mongo_module.mongo_db_insert(db,serv_event_dict,"serv_event")

    return service_events_data, service_events_update_criteria


def network_perf_data_live_query(site, log_split, network_events_data, network_events_update_criteria):
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


    query = "GET hosts\nColumns: host_perf_data host_last_state_change\nFilter: host_name = %s\nOutputFormat: python\n" % (log_split[4]) 
    perf_data= eval(utility_module.get_from_socket(site, query))
    #age1 =int(perf_data.split(';',1)[0])
    age1 = int(perf_data[0][1])
    perf_data1 = perf_data[0][0]
    host_perf_data = utility_module.get_threshold(perf_data1)
    #print 'age1', age1
    #print 'host_perf_data', host_perf_data

    # Forward the time stamp, with `seconds` attribute equal to zero
    t_stmp = datetime.fromtimestamp(float(log_split[1]))
    altered_timestamp = (t_stmp.replace(second=0)).strftime('%s')

    host_ip = log_split[11]
    description=log_split[10]
    description_based_values = {'pl': None, 'rta': None}
    current_value_pl, current_value_rta = None, None
    # use values present in description field, at first priority
    # since only ips are included, we can use `ms` also, as our criteria
    if 'rta' in description and 'ms' in description and 'lost' in description:
	current_value_pl = description[description.find('lost')+5:-1]
	current_value_rta = description[description.find('rta')+4:description.find('ms')]
    description_based_values.update({'pl': current_value_pl, 'rta': current_value_rta})
    for ds in host_perf_data.iterkeys():
        if ds == 'rtmin' or ds == 'rtmax':
            continue
        cur = host_perf_data.get(ds).get('cur')
        host_cur = description_based_values[ds] if description_based_values[ds] else cur
        host_war =host_perf_data.get(ds).get('war')
        host_crit =host_perf_data.get(ds).get('cric')
        if ds == 'pl':
            host_cur=host_cur.strip('%')                
        host_event_dict=dict(sys_timestamp=int(altered_timestamp),device_name=log_split[4],severity=log_split[7],
                        description=description,min_value=0,max_value=0,avg_value=0,current_value=host_cur,
                data_source=ds,warning_threshold=host_war,critical_threshold=host_crit,
                check_timestamp=int(log_split[1]),
                ip_address=host_ip,site_name=site,service_name='ping',age=age1)
        modified_host_dict = deepcopy(host_event_dict)
        if ds  == 'rta' and eval(host_cur) > eval(host_war):
	    modified_host_dict.update({'severity':'major'}) 
        # Check whether the host has breached RTA thresholds only, but not PL
        if ds == 'pl' and eval(host_cur) < eval(host_crit) and log_split[7].lower() != 'up':
            host_event_dict.update({'severity': 'UP'})
	    modified_host_dict.update({'severity':'major'}) 
	    
        matching_criteria = {
                'device_name': log_split[4],
                'service_name': 'ping',
                'data_source': ds
                }
        # Mongo db updation
        network_events_update_criteria.append(matching_criteria)
        #mongo_module.mongo_db_update(db, matching_criteria, host_event_dict, 'network_event_status')
        # mongo db insertion
        network_events_data.append(host_event_dict)
        #mongo_module.mongo_db_insert(db,host_event_dict,"host_event")

    return network_events_data, network_events_update_criteria


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
    """ 
    db = mongo_module.mongo_conn(
            host=mongo_host,
            port=mongo_port,
            db_name=mongo_db
    )
    """
    # time for which nagios events are extracted
    #start_epoch = get_latest_event_entry(db_type = 'mongodb',db=db)
    #if start_epoch == None:
    start_time = datetime.now() - timedelta(minutes=1)
    start_time = start_time.replace(second=0)
    start_epoch = int(time.mktime(start_time.timetuple()))

    end_time = datetime.now()
    end_epoch = int(time.mktime(end_time.timetuple()))

    # sustracting 5.30 hours        
    host_event_dict ={}
    serv_event_dict={}

    # query for the extracting the log from nagios .This query is only for services except ping
    #query = "GET log\nColumns: log_type log_time log_state_type log_state  host_name service_description "\
    #    "options host_address current_service_perf_data\nFilter: log_time > %s\nFilter: class = 0\nFilter: class = 1\n"\
    #    "Filter: class = 2\nFilter: class = 3\nFilter: class = 4\nFilter: class = 6\nOr: 6\n" %(start_epoch) 
    #output= utility_module.get_from_socket(site, query)
    #for log_attr in output.split('\n'):
    #    log_split = [log_split for log_split in log_attr.split(';')]
    #    try:
    #        if log_split[0] == "CURRENT SERVICE STATE":
    #            service_perf_data_live_query(db,site,log_split)
    #        elif log_split[0] == "SERVICE ALERT" or log_split[0] == "INITIAL SERVICE STATE":
    #            service_perf_data_live_query(db,site,log_split)
    #        elif log_split[0] == "SERVICE FLAPPING ALERT":
    #                service_perf_data_live_query(db,site,log_split)
    #    except Exception, e:
    #        print 'Error with log split'

    # query for the extracting the log from nagios .This query is ping serviecs
    query = "GET log\nColumns: log_type log_time log_state_type log_state  host_name service_description " +\
        "options host_address current_host_perf_data host_last_state_change service_last_state_change \n" +\
        "Filter: log_time >= %s\nFilter: log_type !~ FLAPPING\nFilter: service_description !~ Check_MK\nFilter: class = 0\n" % start_epoch +\
        "Filter: class = 1\nFilter: class = 2\nFilter: class = 3\nFilter: class = 4\nFilter: class = 6\nOr: 6\n"
    output = utility_module.get_from_socket(site, query)
    #print output

    network_events_data = []
    service_events_data = []
    network_events_update_criteria = []
    service_events_update_criteria = []

    for log_attr in output.split('\n'):
        log_split = [log_split for log_split in log_attr.split(';')]
        #print '---------------- log_split '
        #print log_split
        try:
            if log_split[0] == 'HOST ALERT' or log_split[0] == 'INITIAL HOST STATE':
                network_events_data, network_events_update_criteria = network_perf_data_live_query(site,log_split, 
                        network_events_data, network_events_update_criteria)    
            elif log_split[0] == 'SERVICE ALERT' or log_split[0] == 'INITIAL SERVICE STATE':
		# We dont need Counter_wrapped events for utilization services
		if 'wrapped' in log_split[11]:
			continue
                service_events_data, service_events_update_criteria = service_perf_data_live_query(site, log_split,
                        service_events_data, service_events_update_criteria)
        except Exception, e:
            print 'Error with log split: ', e

    # Update the network events data into network_event_status collection of Mongodb
    #for entry in zip(network_events_update_criteria, network_events_data):
    #    mongo_module.mongo_db_update(db, entry[0], entry[1], 'network_event_status')
    # Update the service events data into service_event_status collection of Mongodb
    #for entry in zip(service_events_update_criteria, service_events_data):
    #    mongo_module.mongo_db_update(db, entry[0], entry[1], 'service_event_status')

    # Bulk insert the events data into Mongodb
    #if network_events_data:
	#print 'Host events entries %s for time %s -- %s' % (len(network_events_data), start_time, end_time)
     #   mongo_module.mongo_db_insert(db, network_events_data, 'host_event')
    #if service_events_data:
	#print 'Service events entries %s for time %s -- %s' % (len(service_events_data), start_time, end_time)
     #   mongo_module.mongo_db_insert(db, service_events_data, 'serv_event')
      
     #memcache handling of host and service events
    memc_obj=db_ops_module.MemcacheInterface()
    attempt_key =nocout_site_name+ "_attempt"

    if memc_obj.memc_conn.get(attempt_key)==1:

        key = nocout_site_name + "_network_event1"
        doc_len_key = key + "_len"
    #memc_obj=db_ops_module.MemcacheInterface()
        exp_time =300 # 2 min
        memc_obj.store(key,network_events_data,doc_len_key,exp_time,chunksize=1000)
        key = nocout_site_name + "_service_event1"
        doc_len_key = key + "_len"
        memc_obj.store(key,service_events_data,doc_len_key,exp_time,chunksize=1000)
        memc_obj.memc_conn.set(attempt_key,2)

    elif memc_obj.memc_conn.get(attempt_key)==2:

        key = nocout_site_name + "_network_event2"
        doc_len_key = key + "_len"
    #memc_obj=db_ops_module.MemcacheInterface()
        exp_time =300 # 2 min
        memc_obj.store(key,network_events_data,doc_len_key,exp_time,chunksize=1000)
        key = nocout_site_name + "_service_event2"
        doc_len_key = key + "_len"
        memc_obj.store(key,service_events_data,doc_len_key,exp_time,chunksize=1000)
        memc_obj.memc_conn.set(attempt_key,1)
    else :
        memc_obj.memc_conn.set(attempt_key,1)





  
if __name__ == '__main__':
    """
    Main function for this file which keeps track of the all services and host events.This script is regularly called with 1 min interval

    """
    configs = config_module.parse_config_obj()
    desired_site = filter(lambda x: x == nocout_site_name, configs.keys())[0]
    desired_config = configs.get(desired_site)
    site = desired_config.get('site')
    extract_nagios_events_live(
            mongo_host=desired_config.get('host'),
            mongo_db=desired_config.get('nosql_db'),
            mongo_port=int(desired_config.get('port'))
    )
