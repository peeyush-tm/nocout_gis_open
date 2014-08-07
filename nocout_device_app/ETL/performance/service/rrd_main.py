"""
File_name : rrd_main.py
Content: rrd_main file extracts the all devices and associated services with them for that particular poller and pass the host list and
         services configured on those devices to another function which calculates the services data and stores into mongodb.

"""

from nocout_site_name import *
import rrd_migration
import socket
import json
import imp

config_module = imp.load_source('configparser', '/opt/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

class MKGeneralException(Exception):
    """
        This is the Exception class handing exception in this file.
	Args: Exception instance

	Kwargs: None

	return: class object

    """
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return self.reason


def get_host_services_name(site_name=None, mongo_host=None, mongo_db=None, mongo_port=None):
	"""
	Function_name : get_host_services_name (extracts the services monitotred on that poller)

	Args: site_name (poller on which monitoring data is to be collected)

	Kwargs: mongo_host(host on which we have to monitor services and collect the data),mongo_db(mongo_db connection),
	        mongo_port( port for the mongodb database)
	Return : None

	raise 
	     Exception: SyntaxError,socket error 
	"""
        try:
            query = "GET hosts\nColumns: host_name\nOutputFormat: json\n"
                
            output = json.loads(get_from_socket(site_name, query))
            for host_name in output:
                modified_query = "GET hosts\nColumns: host_services host_address\n" +\
                    "Filter: host_name = %s\nOutputFormat: json\n" % (host_name[0])
                output= json.loads(get_from_socket(site_name, modified_query))
                rrd_migration.rrd_migration_main(
                    site_name,
                    host_name[0],
                    output[0],
                    output[0][1],
                    mongo_host,
                    mongo_db,
                    mongo_port
                )
        except SyntaxError, e:
            raise MKGeneralException(("Can not get performance data: %s") % (e))
        except socket.error, msg:
            raise MKGeneralException(("Failed to create socket. Error code %s Error Message %s:") % (str(msg[0]), msg[1]))

def get_from_socket(site_name, query):
    """
	Function_name : get_from_socket (collect the query data from the socket)

	Args: site_name (poller on which monitoring data is to be collected)

	Kwargs: query (query for which data to be collectes from nagios.)

	Return : None

	raise 
	     Exception: SyntaxError,socket error 
    """
    socket_path = "/opt/omd/sites/%s/tmp/run/live" % site_name
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(socket_path)
    s.send(query)
    s.shutdown(socket.SHUT_WR)
    output = s.recv(100000000)
    output.strip("\n")
    return output


    
if __name__ == '__main__':
    """
    main function for this file which is called in 5 minute interval.Every 5 min interval calculates the host configured on this poller
    and extracts data

    """
    configs = config_module.parse_config_obj()
    for section, options in configs.items():
        site = options.get('site')
        get_host_services_name(
            site_name=site,
            mongo_host=options.get('host'),
            mongo_db=options.get('nosql_db'),
            mongo_port=options.get('port')
        )
    
