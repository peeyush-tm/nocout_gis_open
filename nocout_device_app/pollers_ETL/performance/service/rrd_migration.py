"""
rrd_migration.py
================

This script collects and stores data for all services running on all configured devices for this poller.

"""

from nocout_site_name import *
import os
import demjson,json
import re
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import subprocess
import pymongo
import imp
import time

utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

def build_export(site, host, ip, mongo_host, mongo_db, mongo_port):
	"""
	Function name: build_export  (function export data from the rrdtool (which stores the period data) for all services for particular host
	and stores them in mongodb in particular structure)

	Args: site : site_name (poller name on which  deviecs are monitored)
	Kwargs: host(Device from which data to collected) , ip (ip for the device) ,mongo_host (mongodb host name ),
                mongo_db (mongo db connection),mongo_port(port for mongodb)
	Return : None
        Raises:
	     Exception: IOError 
	"""
	_folder = '/omd/sites/%s/var/pnp4nagios/perfdata/%s/' % (site,host)
	xml_file_list = []
	#tmp_service =service
	#service = service.replace(' ','_')
	params = []
	perf_data =None
	m = 0
	ds_index =None
	file_paths = []
	temp_dict = {}
	data_dict = {
		"host": str(host),
		"service": None,
		"ds": None,
		"data": [],
		"meta": None,
		"ip_address": str(ip),
		"severity":None
	}
	status_dict = {
		"host": str(host),
		"service": None,
		"ds": None,
		"data": [],
		"meta": None,
		"ip_address": str(ip),
		"severity":None
	}
	matching_criteria ={}
    	perf_db = None
	threshold_values = {}
	db = mongo_module.mongo_conn(
	    host=mongo_host,
	    port=int(mongo_port),
	    db_name=mongo_db
	)
	# all rrdtool .xml files corresponding to services
	for perf_file in os.listdir(_folder):
		if perf_file.endswith(".xml"):
			xml_file_list.append(perf_file)
	# Extracts the services data for each host from rrdtool
	for xml_file in xml_file_list:
		try:
			tree = ET.parse(_folder + xml_file)
			root = tree.getroot()
		except IOError, e:
			raise IOError ,e

		perf_data = root.find("NAGIOS_PERFDATA").text.strip()
		serv_disc = root.find("NAGIOS_SERVICEDESC").text.strip()
		if serv_disc == '_HOST_':
			data_dict['service'] = 'ping'
			status_dict['service'] = 'ping'
			serv_disc = 'ping'
		else:
			data_dict['service'] = serv_disc
			status_dict['service'] = serv_disc

		if serv_disc.endswith('_status') or serv_disc == 'Check_MK':
			continue
		# Extracts the performance data from the rrdtool for services
		try:
			if serv_disc == 'ping':
				query_string = "GET services\nColumns: host_state\nFilter: host_name = %s\nOutputFormat: json\n" % (host)
				query_output = json.loads(utility_module.get_from_socket(site,query_string).strip())
				if query_output:
					service_state = (query_output[0][0])
					if service_state == 0:
						service_state = "up"
					elif service_state == 1:
						service_state = "down"
				else:
					service_state= "UNKNOWN"
					
			else:
				query_string = "GET services\nColumns: service_state\nFilter: " + \
				"service_description = %s\nFilter: host_name = %s\nOutputFormat: json\n" % (serv_disc,host)
				query_output = json.loads(utility_module.get_from_socket(site,query_string).strip())
				if query_output:
					service_state = (query_output[0][0])
					if service_state == 0:
						service_state = "OK"
					elif service_state == 1:
						service_state = "WARNING"
					elif service_state == 2:
						service_state = "CRITICAL"
					elif service_state == 3:
						service_state = "UNKNOWN"
				else:
					service_state = "UNKNOWN"
		except:
			service_state= "UNKNOWN"
		
		threshold_values = get_threshold(perf_data)
		for ds in root.findall('DATASOURCE'):
			params.append(ds.find('NAME').text)
			file_paths.append(ds.find('RRDFILE').text)
		for i, path in enumerate(file_paths):
			if params[file_paths.index(path)] == 'rtmin' or params[file_paths.index(path)] == 'rtmax':
				continue
			m = -5
			ds_index = params[file_paths.index(path)]
			if i == 0:
	    			# Data will be exported from last inserted entry in mongodb uptill current time
				start_time = mongo_module.get_latest_entry(db_type='mongodb', db=db, table_name=None,
								host=host, serv=data_dict['service'], ds=ds_index)
			data_series = do_export(site, host, path, ds_index, start_time, data_dict['service'])
                        if len(data_series) == 0:
                            continue
			data_dict.update({
				"check_time": data_series.get('check_time'),
				"local_timestamp": data_series.get('local_timestamp'),
				"site": data_series.get('site')
				})
			
			status_dict.update({
				"check_time": data_series.get('check_time'),
				"local_timestamp": data_series.get('local_timestamp'),
				"site": data_series.get('site')
				})
			data_dict['ds'] = ds_index

			status_dict['ds'] = ds_index
			ds_values = data_series['data'][:-1]
			start_time = mongo_module.get_latest_entry(db_type='mongodb', db=db, table_name=None,
                                                                host=host, serv=data_dict['service'], ds=ds_index)
			for d in ds_values:
				if d[-1] is not None:
					m += 5
					temp_dict = dict(
						time=data_series.get('check_time') + timedelta(minutes=m),
						value=d[-1]
					)
					# forcing to not add deuplicate entry in mongo db. currenltly suppose at time 45.00 50.00 data comes in
					# in one iteration then in second iteration 50.00 55.00 data comes .So Not adding second iteration
					# 50.00 data again.
					if ds_index == 'rta':
						temp_dict.update({"min_value":d[-3],"max_value":d[-2]}) 
					if start_time == temp_dict.get('time'):
						data_dict.update({"local_timestamp":temp_dict.get('time')+timedelta(minutes=5),
						"check_time":temp_dict.get('time')+ timedelta(minutes=5)})
						continue
					data_dict.get('data').append(temp_dict)
			data_dict['meta'] = threshold_values.get(ds_index)
			# dictionariers to hold values for the service status tables
			status_dict.get('data').append(temp_dict)	
			status_dict['meta'] = threshold_values.get(ds_index)
			status_dict.update({"local_timestamp":temp_dict.get('time'),"check_time":temp_dict.get('time')})
			
			data_dict['severity'] = service_state
			status_dict['severity'] = service_state
			matching_criteria.update({'host':str(host),'service':data_dict['service'],'site':site,'ds':ds_index})
			if xml_file == '_HOST_.xml':
				mongo_module.mongo_db_update(db,matching_criteria,status_dict,"network_perf_data")
				mongo_module.mongo_db_insert(db,data_dict,"network_perf_data")
			else:
				mongo_module.mongo_db_update(db,matching_criteria,status_dict,"serv_perf_data")
				mongo_module.mongo_db_insert(db,data_dict,"serv_perf_data")

		#status = insert_data(data_dict)

			data_dict = {
					"host": str(host),
					"service": serv_disc,
					"ip_address": str(ip),
					"data": [],
					"meta": None,
					"severity": None,
					"ds": None
			}
			matching_criteria = {}
			status_dict = {
					"host": str(host),
					"service": serv_disc,
					"ip_address": str(ip),
					"data": [],
					"meta": None,
					"severity": None,
					"ds": None
			}
	
		params = []
		file_paths = []


def do_export(site, host, file_name,data_source, start_time, serv):
    """
    Function_name : do_export (Main function for extracting the data for the services from rrdtool)

    Args: site (poller on which devices are monitored)

    Kwargs: host(Device from which data to collected) , file_name (rrd file for data source) ,data_source (service data source),
                start_time (time from which data is extracted),serv (service)
    return:
           None
    Exception:
           JSONDecodeError
    """
    data_series = {}
    cmd_output ={}
    CF = 'AVERAGE'
    resolution = '-300sec';

    # Get India times (GMT+5.30)
    utc_time = datetime(1970, 1,1, 5, 30)
    end_time = datetime.now()

    year, month, day = end_time.year, end_time.month, end_time.day
    hour = end_time.hour
    #Pivoting minutes to multiple of 5, to synchronize with rrd dump
    minute = end_time.minute - (end_time.minute % 5)
    end_time = datetime(year, month, day, hour, minute)

    if start_time is None:
        start_time = end_time - timedelta(minutes=6)
    else:
	start_time = start_time - timedelta(minutes=1)

    #end_time = datetime.now() - timedelta(minutes=10)
    #start_time = end_time - timedelta(minutes=5)
    
    start_epoch = int(time.mktime(start_time.timetuple()))
    end_epoch = int(time.mktime(end_time.timetuple()))
   
    #Subtracting 5:30 Hrs to epoch times, to get IST
    #start_epoch -= 19800
    #end_epoch -= 19800

    print start_epoch,end_epoch
    # Command for rrdtool data extraction
    cmd = '/omd/sites/%s/bin/rrdtool xport --json --daemon unix:/omd/sites/%s/tmp/run/rrdcached.sock -s %s -e %s --step 300 '\
        %(site,site, str(start_epoch), str(end_epoch))
    RRAs = ['MIN','MAX','AVERAGE']

    for RRA in RRAs:
    	cmd += 'DEF:%s_%s=%s:%d:%s XPORT:%s_%s:%s_%s '\
            %(data_source, RRA, file_name, 1, RRA, data_source,
                RRA, data_source, RRA)
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
    cmd_output, err = p.communicate()
    try:
        cmd_output = demjson.decode(cmd_output)
    except demjson.JSONDecodeError, e:
        return data_series

    legend = cmd_output.get('meta').get('legend')
    start_check = cmd_output['meta']['start']
    end_check = start_check+300
    start_check = datetime.fromtimestamp(start_check)
    end_check = datetime.fromtimestamp(end_check)
    local_timestamp = pivot_timestamp(start_check)

    data_series.update({
        "site": site,
        "legend": legend,
        "data" :cmd_output['data'],
        "start_time": start_check,
        "end_time": end_check,
        "check_time": start_check,
        "local_timestamp": local_timestamp
    })
    return data_series


def get_threshold(perf_data):
    """
    Function_name : get_threshold (function for parsing the performance data and storing in the datastructure)

    Args: perf_data performance_data extracted from rrdtool

    Kwargs: None
    return:
           threshold_values (data strucutre containing the performance_data for all data sources)
    Exception:
           None
    """

    threshold_values = {}

    #if len(perf_data) == 1:
     #   return threshold_values
    for param in perf_data.split(" "):
	param = param.strip("['\n', ' ']")
	if param.partition('=')[2]:
        	if ';' in param.split("=")[1]:
            		threshold_values[param.split("=")[0]] = {
                	"war": re.sub('[ms]', '', param.split("=")[1].split(";")[1]),
                	"cric": re.sub('[ms]', '', param.split("=")[1].split(";")[2]),
                	"cur": re.sub('[ms]', '', param.split("=")[1].split(";")[0])
            		}
        	else:
            		threshold_values[param.split("=")[0]] = {
                	"war": None,
                	"cric": None,
                	"cur": re.sub('[ms]', '', param.split("=")[1].strip("\n"))
            		}
	else:
		threshold_values[param.split("=")[0]] = {
			"war": None,
			"cric": None,
			"cur": None
                        }

    return threshold_values


def pivot_timestamp(timestamp):
    """
    Function_name : pivot_timestamp (function for pivoting the time to 5 minutes interval)

    Args: timestamp

    Kwargs: None
    return:
           t_stmp (pivoted time stamp)
    Exception:
           None
    """
    t_stmp = timestamp + timedelta(minutes=-(timestamp.minute % 5))

    return t_stmp


def db_port(site_name=None):
    """
    Function_name : db_port (function for extracting the port value for mongodb for particular poller,As different poller will 
		    have different)

    Args: site_name (poller on which monitoring is performed)

    Kwargs: None
    return:
           port (mongodb port)
    Exception:
           IOError
    """
    port = None
    if site_name:
        site = site_name
    else:
        file_path = os.path.dirname(os.path.abspath(__file__))
        path = [path for path in file_path.split('/')]

        if len(path) <= 4 or 'sites' not in path:
            raise Exception, "Place the file in appropriate omd site"
        else:
            site = path[path.index('sites') + 1]
    
    port_conf_file = '/omd/sites/%s/etc/mongodb/mongod.d/port.conf' % site
    try:
        with open(port_conf_file, 'r') as portfile:
            port = portfile.readline().split('=')[1].strip()
    except IOError, e:
        raise IOError, e

    return port


def mongo_conn(**kwargs):
    """
    Function_name : mongo_conn (function for making mongo db connection)

    Args: site_name (poller on which monitoring is performed)

    Kwargs: Multiple arguments
    return:
           db (mongdb object)
    Exception:
           PyMongoError
    """
    DB = None
    try:
        CONN = pymongo.Connection(
            host=kwargs.get('host'),
            port=kwargs.get('port')
        )
        DB = CONN[kwargs.get('db_name')]
    except pymongo.errors.PyMongoError, e:
        raise pymongo.errors.PyMongoError, e
    return DB


def insert_data(data_dict):
    """
    Function_name : insert_data (inserting data in mongo db)

    Args: data_dict (data_dict which is inserted)

    Kwargs: None
    return:
           None
    Exception:
           None
    """
    port = None
    db  = None
    #Get the port for mongodb process, specific to this multisite instance
    port = db_port()

    #Get the mongodb connection object
    db = mongo_module.mongo_conn(
        host='localhost',
        port=int(port),
        db_name='nocout'
    )

    if db:
        db.device_perf.insert(data_dict)
        return "Data Inserted into Mongodb"
    else:
        return "Data couldn't be inserted into Mongodb"


def rrd_migration_main(site,host,services,ip, mongo_host, mongo_db, mongo_port):
	"""
	Main function for the rrd_migration which extracts and store data in mongodb databses for all services configured on all devices
	Args: site : site (poller name on which  deviecs are monitored)
        Kwargs: host(Device from which data to collected) ,services(host services) ,ip (ip for the device) ,mongo_host (mongodb host name ),
	                mongo_db (mongo db connection),mongo_port(port for mongodb)
	return:
	      None
	Raise
	    Exception : None
	"""
	build_export(site, host, ip, mongo_host, mongo_db, mongo_port)
        #for service in services[0]:

"""if __name__ == '__main__':
    build_export('BT','AM-400','PING')
"""

