import socket
import re


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
    
    port_conf_file = '/opt/omd/sites/%s/etc/mongodb/mongod.d/port.conf' % site
    try:
        with open(port_conf_file, 'r') as portfile:
            port = portfile.readline().split('=')[1].strip()
    except IOError, e:
        raise IOError, e

    return port


def get_nocout_site_name(site=None):
	file_path = os.path.dirname(os.path.abspath(__file__))
	path = [p for p in file_path.split('/')]
	
	if len(path) <= 4 or 'sites' not in path:
		raise Exception, 'Place the ETL scripts in appropriate omd site location'
	else:
		site = path[path.index('sites') + 1]


	return site
