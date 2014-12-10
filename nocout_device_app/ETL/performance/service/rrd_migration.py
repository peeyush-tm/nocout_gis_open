"""
rrd_migration.py
================

This script collects and stores data for all services running on all configured devices for this poller.

"""

from nocout_site_name import *
import os
import demjson,json
from pprint import pformat
import re
from datetime import datetime, timedelta
import subprocess
import pymongo
import imp
import time

utility_module = imp.load_source('utility_functions', '/omd/sites/%s/nocout/utils/utility_functions.py' % nocout_site_name)
mongo_module = imp.load_source('mongo_functions', '/omd/sites/%s/nocout/utils/mongo_functions.py' % nocout_site_name)
config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

# Logger would write all activities to rrd_migration.log file

def build_export(site, host, ip, nw_qry_output, serv_qry_output, mongo_host, mongo_db, mongo_port):
	"""
	Function name: build_export  (function export data from the rrdtool (which stores the period data) for all services for particular host
	and stores them in mongodb in particular structure)

	Args: site : site_name (poller name on which  deviecs are monitored)
	Kwargs: host(Device from which data to collected) , ip (ip for the device) ,mongo_host (mongodb host name ),
                mongo_db (mongo db connection),mongo_port(port for mongodb)
	Return : None
        Raises:
	    Exception: None
	"""
	network_data_values = []
	service_data_values = []
        age = None
	data_dict = {
		"host": str(host),
		"service": None,
		"ds": None,
		"data": [],
		"meta": None,
		"ip_address": str(ip),
		"severity":None,
		"age": None
	}
	matching_criteria ={}
	threshold_values = {}
	severity = 'UNKNOWN'
	db = mongo_module.mongo_conn(
	    host=mongo_host,
	    port=int(mongo_port),
	    db_name=mongo_db
	)
	# Process network perf data
	for entry in nw_qry_output:
		threshold_values = get_threshold(entry[-1])
		# rtmin, rtmax values are not used in perf calc
		threshold_values.pop('rtmin', '')
		threshold_values.pop('rtmax', '')
		print '-- threshold_values'
		print threshold_values
		if entry[2] == 0:
			severity = 'UP'
		elif entry[2] == 1:
			severity = 'DOWN'
		# Age of last service state change
		last_state_change = entry[-2]
		current_time = int(time.time())
		age = current_time - last_state_change
		for ds, ds_values in threshold_values.items():
			check_time = datetime.fromtimestamp(entry[3]) 
			# Pivot the time stamp to next 5 mins time frame
			local_timestamp = pivot_timestamp_fwd(check_time)
			data_values = [{'time': check_time, 'value': ds_values.get('cur')}]
			data_dict.update({
				'host': host,
				'service': 'ping',
				'ip_address': ip,
				'severity': severity,
				'age': age,
				'ds': ds,
				'data': data_values,
				'meta': ds_values,
				'check_time': check_time,
				'local_timestamp': local_timestamp 
				})
			matching_criteria.update({
				'host': host,
				'service': 'ping',
				'ds': str(ds)
				})
			# Update the value in status collection, Mongodb
			mongo_module.mongo_db_update(db, matching_criteria, data_dict, 'network_perf_data')
			network_data_values.append(data_dict)
			data_dict = {}
	print 'network_data_values'
	print network_data_values
	try:
		mongo_module.mongo_db_insert(db, network_data_values, 'network_perf_data')
	except Exception, e:
		print e.message
	# If host is Down, do not process its servive perf data
	if severity == 'DOWN':
		return
	# Process service perf data
	for entry in serv_qry_output:
		if not len(entry[-1]):
			continue
		threshold_values = get_threshold(entry[-1])
		print '-- threshold_values'
		print threshold_values
		severity = calculate_severity(entry[3])
		# Age of last service state change
		last_state_change = entry[-2]
		current_time = int(time.time())
		age = current_time - last_state_change
		for ds, ds_values in threshold_values.items():
			check_time = datetime.fromtimestamp(entry[4])
			# Pivot the time stamp to next 5 mins time frame
			local_timestamp = pivot_timestamp_fwd(check_time)
			data_values = [{'time': check_time, 'value': ds_values.get('cur')}]
			data_dict.update({
				'host': host,
				'service': str(entry[2]),
				'ip_address': ip,
				'severity': severity,
				'age': age,
				'ds': ds,
				'data': data_values,
				'meta': ds_values,
				'check_time': check_time,
				'local_timestamp': local_timestamp 
				})
			matching_criteria.update({
				'host': host,
				'service': str(entry[2]),
				'ds': str(ds)
				})
			# Update the value in status collection, Mongodb
			mongo_module.mongo_db_update(db, matching_criteria, data_dict, 'service_perf_data')
			service_data_values.append(data_dict)
		        data_dict = {}
	print 'service_data_values'
	print pformat(service_data_values)
	# Bulk insert the values into Mongodb
	try:
		mongo_module.mongo_db_insert(db, service_data_values, 'service_perf_data')
	except Exception, e:
		print e.message

def calculate_severity(severity_bit):
	"""
	Function to compute host service states
	"""
	severity = 'UNKNOWN'
	if severity_bit == 0:
		severity = 'OK'
	elif severity_bit == 1:
		severity = 'WARNING'
	elif severity_bit == 2:
		severity = 'CRITICAL'

	return severity


def get_ss(host=None, interface=None):
	ss_device = None
	global nocout_site_name
        l_host_vars = {
		    "FOLDER_PATH": "",
		    "ALL_HOSTS": '', # [ '@all' ]
		    "all_hosts": [],
		    "clusters": {},
		    "ipaddresses": {},
		    "extra_host_conf": { "alias" : [] },
		    "extra_service_conf": { "_WATO" : [] },
		    "host_attributes": {},
		    "host_contactgroups": [],
		    "_lock": False,
	}
	# path to hosts file
	hosts_file = '/omd/sites/%s/etc/check_mk/conf.d/wato/hosts.mk' % nocout_site_name
	try:
		execfile(hosts_file, l_host_vars, l_host_vars)
		del l_host_vars['__builtins__']
		
		host_row = filter(lambda t: re.match(interface, t.split('|')[2]) \
				and re.match(host, t.split('|')[3]), l_host_vars['all_hosts'])
		ss_device = host_row[0].split('|')[0]
	except Exception, e:
		return ss_device

	return ss_device


def split_service_interface(serv_disc):

	return serv_disc[:-18], serv_disc[-17:]


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
	start_time = start_time + timedelta(minutes=1)

    #end_time = datetime.now() - timedelta(minutes=10)
    #start_time = end_time - timedelta(minutes=5)
    
    start_epoch = int(time.mktime(start_time.timetuple()))
    end_epoch = int(time.mktime(end_time.timetuple()))
   
    #Subtracting 5:30 Hrs to epoch times, to get IST
    #start_epoch -= 19800
    #end_epoch -= 19800

    # Command for rrdtool data extraction
    if start_time > end_time:
	return
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

def pivot_timestamp_fwd(timestamp):
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
    if (timestamp.minute %5) != 0:
    	t_stmp = t_stmp + timedelta(minutes=5)

  
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

"""if __name__ == '__main__':
    build_export('BT','AM-400','PING')
"""



def collect_data_for_wimax(host,site,db):
		matching_criteria = {}
		wimax_service_list = ['wimax_modulation_dl_fec','wimax_modulation_ul_fec','wimax_dl_intrf','wimax_ul_intrf','wimax_ss_ip','wimax_ss_mac']
                for service in wimax_service_list:
                        query_string = "GET services\nColumns: service_state service_perf_data host_address last_check\nFilter: " + \
                        "service_description = %s\nFilter: host_name = %s\nOutputFormat: json\n"                % (service,host)
                        query_output = json.loads(utility_module.get_from_socket(site,query_string).strip())
                        try:
                                if query_output[0][1]:
                                        perf_data_output = str(query_output[0][1])
                                        service_state = (query_output[0][0])
                                        host_ip = str(query_output[0][2])
					last_check = (query_output[0][3])
                                        if service_state == 0:
                                                service_state = "OK"
                                        elif service_state == 1:
                                                service_state = "WARNING"
                                        elif service_state == 2:
                                                service_state = "CRITICAL"
                                        elif service_state == 3:
                                                service_state = "UNKNOWN"
                                        perf_data = utility_module.get_threshold(perf_data_output)
                                else:
                                        continue
                        except:
                                continue
                        for datasource in perf_data.iterkeys():
				data = []
                                cur =perf_data.get(datasource).get('cur')
                                war =perf_data.get(datasource).get('war')
                                crit =perf_data.get(datasource).get('cric')
				temp_dict = dict(value = cur,time = pivot_timestamp_fwd(datetime.fromtimestamp(last_check)))
                                wimax_service_dict = dict (check_time=datetime.fromtimestamp(last_check),
						local_timestamp=pivot_timestamp_fwd(datetime.fromtimestamp(last_check)),host=str(host),
                                                service=service,data=[temp_dict],meta ={'cur':cur,'war':war,'cric':crit},
                                                ds=datasource,severity=service_state,site=site,ip_address=host_ip)
                                matching_criteria.update({'host':str(host),'service':service,'ds':datasource})
                                mongo_module.mongo_db_update(db,matching_criteria,wimax_service_dict,"serv_perf_data")
                                mongo_module.mongo_db_insert(db,wimax_service_dict,"serv_perf_data")
				matching_criteria = {}
                wimax_service_dict = {}


def collect_data_from_rrd(db,site,path,host,replaced_host,service,ds_index,start_time,data_dict,status_dict):

	service_data_type = {
		"radwin_rssi" : int,
		"radwin_uas"  : int,
		"radwin_uptime": int,
		"radwin_service_throughput" : float,
		"radwin_dl_utilization": int,
		"radwin_ul_utilization" : int
	}

	m = -5
	data_series = do_export(site, host, path, ds_index, start_time, service)
	if data_series is None:
		return 1
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
                                                                host=replaced_host, serv=data_dict['service'], ds=ds_index)
	temp_dict = {}
	for d in ds_values:
		if d[-1] is not None:
			m += 5
			if service in service_data_type:
				d_type = service_data_type[service]
			else:
				d_type = float
					
			temp_dict = dict(
					time=data_series.get('check_time') + timedelta(minutes=m),
						value=d_type(d[-1]))
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
	if len(temp_dict):
		status_dict.get('data').append(temp_dict)
		status_dict.update({"local_timestamp":temp_dict.get('time'),"check_time":temp_dict.get('time')})
