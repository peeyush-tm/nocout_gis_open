"""
nocout.py
=========

nocout_gis Device App web services to Create/Update/Delete a host/service into Nagios
monitoring core.
"""

from wato import *
import pymongo
from pymongo import Connection
import pprint
import os
import ast
from itertools import ifilterfalse
from nocout_live import nocout_log


hosts_file = root_dir + "hosts.mk"
rules_file = root_dir + "rules.mk"

nocout_replication_paths = [
    ( "dir",  "check_mk",   root_dir ),
    ( "dir",  "multisite",  multisite_dir ),
    ( "file", "htpasswd",   defaults.htpasswd_file ),
    ( "file", "auth.secret",  '%s/auth.secret' % os.path.dirname(defaults.htpasswd_file) ),
    ( "file", "auth.serials", '%s/auth.serials' % os.path.dirname(defaults.htpasswd_file) ),
    ( "dir", "usersettings", defaults.var_dir + "/web" ),
]
nocout_backup_paths = nocout_replication_paths + [
    ( "file", "sites",      sites_mk)
]

host_tags = {
    "snmp": "snmp-only|snmp",
    "cmk_agent": "cmk-agent|tcp",
    "snmp-v1|snmp": "snmp-v1|snmp",
    "snmp-v2|snmp": "snmp-v2|snmp",
    "v3|snmp": "v3|snmp",
    "dual": "snmp-tcp|snmp|tcp",
    "ping": "ping"
}

g_host_vars = {
    "FOLDER_PATH": "",
    "ALL_HOSTS": ALL_HOSTS, # [ '@all' ]
    "all_hosts": [],
    "clusters": {},
    "ipaddresses": {},
    "extra_host_conf": { "alias" : [] },
    "extra_service_conf": { "_WATO" : [] },
    "host_attributes": {},
    "host_contactgroups": [],
    "_lock": False,
}

g_service_vars = {
    "only_hosts": None,
    "ALL_HOSTS": [],
    "host_contactgroups": [],
    "bulkwalk_hosts": [],
    "extra_host_conf": {},
    "extra_service_conf": {
        "retry_check_interval": [],
        "max_check_attempts": [],
        "normal_check_interval": []
    },
    "static_checks": {},
    "ping_levels": [],
    "checks": [],
    "snmp_ports": [],
    "snmp_communities": []
}

logger = nocout_log()


def main():
    response = ''
    action = ''
    action = html.var('mode')
    host = html.var('device_name')
    #f = (lambda x: x)
    #f(addhost)()
    # Calling the appropriate function based on action
    #response = globals()[action]()
    #TO DO:: Call the appropriate modes through a global
    if action == 'addhost':
        response = addhost()
    elif action == 'addservice':
        response = addservice()
    elif action == 'edithost':
        response = edithost()
    elif action == 'editservice':
        response = editservice()
    elif action == 'deletehost':
        response = deletehost()
    elif action == 'deleteservice':
        response = deleteservice()
    elif action == 'sync':
        response = sync()

    html.write(pprint.pformat(response))


def addhost():
    logger.debug('[-- addhost --]')
    global g_host_vars
    response = {
        "success": 1,
        "device_name": html.var('device_name'),
        "message": "Device added successfully",
        "error_code": None,
        "error_message": None
    }
    payload = {
        "host": html.var("device_name"),
        "attr_alias": html.var("device_alias"),
        "attr_ipaddress": html.var("ip_address"),
        "site": html.var("site"),
        "agent_tag": html.var("agent_tag"),
	"ping_levels": html.var('ping_levels'),
	"parent_device_name": html.var('parent_device_name')
    }
    # Save the host info into mongodb configuration collection
#    add_host_to_mongo_conf(
#		    host=payload.get('host'),
#		    ip=payload.get('attr_ipaddress'),
#		    parent_device_name=payload.get('parent_device_name')
#		    )
    try:
	    ping_levels = ast.literal_eval(payload.get('ping_levels'))
	    logger.debug('ping_levels: '  + pprint.pformat(ping_levels))
    except Exception, e:
	    logger.exception('ping levels: ' + pprint.pformat(e))
    # Set rules for the ping service
    set_ping_levels(payload.get('host'), ping_levels)
    logger.debug('payload : ' + pprint.pformat(payload))
    #for key, attr in payload.items():
    #    if not attr:
    #        response.update({
    #            "success": 0,
    #            "message": None,
    #            "error_code": 2,
    #            "error_message": payload.get('host') + " " + key + " is missing"
    #        })
    #        return response

    give_permissions(hosts_file)
    load_file(hosts_file)

    if len(g_host_vars['all_hosts']) > 1000:
        response.update({
                "success": 0,
                "message": None,
                "error_code": 3,
                "error_message": "Multisite instance couldn't accept more devices"
        })
        return response
    new_host = nocout_find_host(payload.get('host'))
    
    if new_host:
        nocout_add_host_attributes(payload)
    """else:
        response.update({
                "success": 0,
                "message": None,
                "error_code": 1,
                "error_message": payload['host'] + " is already present in some other " +\
                   "multisite instance" 
        })
        return response"""
            

    flag = save_host(hosts_file)
    if not flag:
        response.update({
                "success": 0,
                "message": None,
                "error_code": 4,
                "error_message": "hosts.mk is locked or some other message"
        })
	logger.error('host could not be saved, flag value :' + pprint.pformat(flag))
        return response
    logger.debug('[-- addhost finish --]')
    return response


def addservice():
    logger.debug("[-- addservice --]")
    global g_service_vars
    response = {
        "success": 1,
        "device_name": html.var('device_name'),
        "service_name": html.var('service_name'),
        "message": "Service added successfully",
        "error_code": None,
        "error_message": None
    }
    interface = None
    # Device name on which check would be added
    device_name = None
    service = html.var('service_name').strip().lower()
    # Check for interfaces in HTTP request
    if service == 'cambium_ul_rssi' or service == 'cambium_ul_jitter':
	    if html.var('interface'):
		    interface = html.var('interface').lower()
		    # Get BS device name
		    device_name = get_parent(host=html.var('device_name'), db=False)
		    # Add the MAC addr of SS device into mongodb
		#    add_host_to_mongo_conf(
		#		    host=html.var('device_name'),
		#		    interface=interface
		#		    )
    else:
	    device_name = html.var('device_name')
    if not device_name:
			response.update({
				'success': 0,
				'message': 'Service not added',
				'error_message': 'Could not find BS for this SS'
				}
				)
			return response
    payload = {
        "host": html.var("device_name"),
        "service": html.var("service_name").strip().lower(),
	"interface": interface,
        "serv_params": html.var('serv_params'),
        "cmd_params": html.var('cmd_params'),
        "agent_tag": html.var('agent_tag'),
        "snmp_port": html.var("snmp_port"),
        "snmp_community": html.var("snmp_community")
    }
    new_host = nocout_find_host(payload.get('host'))

    if not new_host:
        # First delete all the existing entries for (host, service) pair
        delete_host_rules(
			hostname=device_name,
			servicename=payload.get('service'),
			interface=payload.get('interface')
			)
        cmd_params = None
        t = ()
        if payload.get('cmd_params'):
            try:
                cmd_params = ast.literal_eval(payload.get('cmd_params'))
		logger.debug("cmd_params : " + pprint.pformat(cmd_params))
                for param, thresholds in cmd_params.items():
                    t = ()
                    if thresholds.get('warning') and thresholds.get('critical'):
                        t += (int(thresholds.get('warning')),)
                        t += (int(thresholds.get('critical')),)
                    else:
                        t = None
		# Add device interfaces as check items, if passed in HTTP request
		check_tuple = ([device_name], payload.get('service'), payload.get('interface'), t)
		g_service_vars['checks'].append(check_tuple)
            except Exception, e:
		logger.error('Error in cmd_params : ' + pprint.pformat(e))
                response.update({
                    "success": 0,
                    "message": "Service not added",
                    "error_message": "cmd_params " + pprint.pformat(e)
                })

        serv_params = None
        if payload.get('serv_params'):
            try:
                serv_params = ast.literal_eval((payload.get('serv_params')))
		logger.debug('serv_params : ' + pprint.pformat(serv_params))
            except Exception, e:
		logger.error('Error in serv_params : ' + pprint.pformat(e))
                response.update({
                    "success": 0,
                    "message": "Service not added",
                    "error_message": "serv_params " + pprint.pformat(e)
                })
                return response
            for param, val in serv_params.items():
                t = (val, [], [device_name], payload.get('service'))
                g_service_vars['extra_service_conf'][param].append(t)
                t = ()

            # Changing SNMP polling period from default 1 to 5 mins
            n_c_i = g_service_vars['extra_service_conf']['normal_check_interval']
            n_c_i = sorted(n_c_i, key=lambda x: x[3])
            if not filter(lambda x: 'Check_MK' in x[3], n_c_i):
                n_c_i.append((5, [], ALL_HOSTS, 'Check_MK'))
                g_service_vars['extra_service_conf']['normal_check_interval'] = n_c_i
	

        snmp_port_tuple = None
        if payload.get('snmp_port'):
		snmp_port_tuple = (int(payload.get('snmp_port')), [], [device_name])
		g_service_vars['snmp_ports'].append(snmp_port_tuple)
        
        snmp_community = None
        if payload.get('snmp_community'):
            snmp_community_list = ast.literal_eval(payload.get('snmp_community'))
            if snmp_community_list.get('version') == 'v1':
                snmp_community = (snmp_community_list.get('read_community'), [], [device_name])
            elif snmp_community_list.get('version') == 'v2':
                snmp_community = (snmp_community_list.get('read_community'), [], [device_name])
            elif snmp_community_list.get('version') == 'v3':
                snmp_community = ((snmp_community_list.get('security_level'),snmp_community_list.get('auth_protocol'),
                    snmp_community_list.get('security_name'),snmp_community_list.get('auth_password'),
                    snmp_community_list.get('private_phase'),snmp_community_list.get('private_passphase')),
                    [device_name])
            g_service_vars['snmp_communities'].append(snmp_community)

        flag = write_new_host_rules()
        if not flag:
            response.update({
                    "success": 0,
                    "message": "Service couldn't added",
                    "error_code": None,
                    "error_message": "rules.mk is locked or some other message"
            })
    else:
        response.update({
            "success": 0,
            "error_message": html.var('device_name') + " not added yet",
            "message": "Service not added",
            "error_code": 1
        })
    logger.debug('[-- addservice finish --]')

    return response


def edithost():
    logger.debug('[-- edithost --]')
    response = {
        "success": 1,
        "device_name": html.var('device_name'),
        "message": "Device edited successfully",
        "error_code": None,
        "error_message": None
    }
    payload = {
        "host": html.var("device_name"),
        "attr_alias": html.var("device_alias"),
        "attr_ipaddress": html.var("ip_address"),
        "site": html.var("site"),
        "agent_tag": html.var("agent_tag"),
	"parent_device_name": html.var('parent_device_name')
    }
    # Save the host info into mongodb configuration collection
#    add_host_to_mongo_conf(
#		    host=payload.get('host'),
#		    ip=payload.get('attr_ipaddress'),
#		    parent_device_name=payload.get('parent_device_name')
#		    )

    logger.debug('payload: ' + pprint.pformat(payload))
    load_file(hosts_file)
    new_host = nocout_find_host(payload.get('host'))
    if not new_host:
        #for i, v in enumerate(g_host_vars['all_hosts']):
        #    if payload.get('host') in v:
        #        g_host_vars['all_hosts'].pop(i)

        nocout_add_host_attributes(payload)

        flag = save_host(hosts_file)
        if not flag:
            response.update({
                    "success": 0,
                    "message": None,
                    "error_code": 2,
                    "error_message": "rules.mk is locked or some other message"
            })
            return response
    else:
        response.update({
            "success": 0,
            "message": None,
            "error_code": 1,
            "error_message": payload.get('host') + " not found"
        })
        return response

    logger.debug('[-- edithost finish --]')
    return response


def editservice():
    logger.debug('[-- editservice --]')
    global g_service_vars
    response = {
        "success": 1,
        "device_name": html.var('device_name'),
        "service_name": html.var('service_name'),
        "message": "Service edited successfully",
        "error_code": None,
        "error_message": None
    }
    interface = None
    # Device name on which check would be added
    device_name = None
    service = html.var('service_name').strip().lower()
    # Check for interfaces in HTTP request
    if service == 'cambium_ul_rssi' or service == 'cambium_ul_jitter':
	    if html.var('interface'):
		    interface = html.var('interface').lower()
		    # Get BS device name from mongo conf
		    device_name = get_parent(host=html.var('device_name'), db=False)
    else:
	    device_name = html.var('device_name')
    if not device_name:
			response.update({
				'success': 0,
				'message': 'Service not edited',
				'error_message': 'Could not find BS for this SS'
				}
				)
			return response
    payload = {
        "host": html.var("device_name"),
        "service": html.var("service_name"),
	"interface": interface,
        "serv_params": html.var('serv_params'),
        "cmd_params": html.var('cmd_params'),
        "agent_tag": html.var('agent_tag'),
        "snmp_port": html.var("snmp_port"),
        "snmp_community": html.var("snmp_community")
    }
    new_host = nocout_find_host(payload.get('host'))
    
    if not new_host:
        #First delete the existing extries for the service
        delete_host_rules(
			hostname=device_name,
			servicename=payload.get('service'),
			interface=payload.get('interface')
			)
        cmd_params = None
        t = ()
        ping_level = ()
        ping_attributes = {}
        if payload.get('cmd_params'):
            try:
                cmd_params = ast.literal_eval(payload.get('cmd_params'))
                logger.debug('cmd_params : ' + pprint.pformat(cmd_params))
                if payload.get('service').strip().lower() == 'ping':
                    ping_attributes.update({
                        'loss': cmd_params.get('loss'),
                        'rta': cmd_params.get('rta'),
                        'packets': cmd_params.get('packets'),
			'timeout': cmd_params.get('timeout')
                    })
                    ping_level += (ping_attributes,)
                    ping_level += (['wan'],)
                    ping_level += ([payload.get('host')],)
                    g_service_vars['ping_levels'].append(ping_level)
                else:
                    for param, thresholds in cmd_params.items():
                        t = ()
                        t += (int(thresholds.get('warning')),)
                        t += (int(thresholds.get('critical')),)
		# Add device interfaces as check items, if passed in HTTP request
                check_tuple = ([device_name], payload.get('service'), payload.get('interface'), t)
                g_service_vars['checks'].append(check_tuple)
            except Exception, e:
                response.update({
                    "success": 0,
                    "message": "Service not edited",
                    "error_message": "cmd_params " + pprint.pformat(e)
                })

	if 'ping' not in payload.get('service').strip().lower():
		serv_params = None
		if payload.get('serv_params'):
		    try:
			serv_params = ast.literal_eval(payload.get('serv_params'))
			logger.debug('serv_params : ' + pprint.pformat(serv_params))
		    except Exception, e:
			response.update({
			    "success": 0,
			    "message": "Service not added",
			    "error_message": "serv_params " + pprint.pformat(e)
			})
			logger.error('Error in serv_params : ' + pprint.pformat(e))
			return response
		    for param, val in serv_params.items():
			t = (val, [], [device_name], payload.get('service'))
			g_service_vars['extra_service_conf'][param].append(t)
			t = ()

        snmp_port_tuple = None
        if payload.get('snmp_port'):
            snmp_port_tuple = (int(payload.get('snmp_port')), [], [device_name])
            g_service_vars['snmp_ports'].append(snmp_port_tuple)
        
        snmp_community = None
        if payload.get('snmp_community'):
            snmp_community_list = ast.literal_eval(payload.get('snmp_community'))
            if snmp_community_list.get('version') == 'v1':
                snmp_community = (snmp_community_list.get('read_community'), [], [device_name])
            elif snmp_community_list.get('version') == 'v2':
                snmp_community = (snmp_community_list.get('read_community'), [], [device_name])
            elif snmp_community_list.get('version') == 'v3':
                snmp_community = ((snmp_community_list.get('security_level'),snmp_community_list.get('auth_protocol'),
                    snmp_community_list.get('security_name'),snmp_community_list.get('auth_password'),
                    snmp_community_list.get('private_phase'),snmp_community_list.get('private_passphase')),
                    [device_name])
            g_service_vars['snmp_communities'].append(snmp_community)

        flag = write_new_host_rules()
        if not flag:
            response.update({
                    "success": 0,
                    "message": "Service Couldn't be edited",
                    "error_code": None,
                    "error_message": "rules.mk is locked or some other message"
            })
    else:
        response.update({
            "success": 0,
            "error_message": html.var('device_name') + " not added yet",
            "message": "Service not edited",
            "error_code": 1
        })

    logger.debug('[-- editservice finish --]')
    return response


def deletehost():
    logger.debug('[-- deletehost --]')
    global g_host_vars
    response = {
        "success": 1,
        "device_name": html.var('device_name'),
        "message": "Device deleted successfully",
        "error_code": None,
        "error_message": None
    }
    interface = None
    device_name = None
    # Check for interfaces in HTTP request
    if html.var('interface'):
		    # Get BS device
		    device_name = get_parent(host=html.var('device_name'), db=False)
		    if html.var('interface'):
			    interface = html.var('interface')
    else:
	    device_name = html.var('device_name')
    payload = {
        "host": html.var("device_name")
    }
    load_file(hosts_file)
    new_host = nocout_find_host(device_name)

    if not new_host:
        delete_host_rules(hostname=device_name, interface=interface)
        flag = write_new_host_rules()
        if not flag:
            response.update({
                    "success": 0,
                    "message": "Device Couldn't be deleted",
                    "error_code": None,
                    "error_message": "rules.mk is locked or some other message"
            })
            return response

        g_host_vars['all_hosts'] = filter(lambda t: not re.match(payload.get('host'), t), g_host_vars['all_hosts'])
        del g_host_vars['host_attributes'][payload.get('host')]
        del g_host_vars['ipaddresses'][payload.get('host')]

        flag = 0
        flag = save_host(hosts_file)
        if not flag:
            response.update({
                    "success": 0,
                    "message": "Device Couldn't be deleted",
                    "error_code": None,
                    "error_message": "hosts.mk is locked or some other message"
            })
    else:
        response.update({
            "success": 0,
            "message": payload.get('host') + " is not added yet"
        })
    logger.debug('[-- deletehost finish --]')
    
    return response


def deleteservice():
    response = {
        "success": 1,
        "device_name": html.var('device_name'),
        "service_name": html.var('service_name'),
        "message": "Service deleted successfully",
        "error_code": None,
        "error_message": None
    }
    interface = None
    # Device name from which check would be deleted
    device_name = None
    service = html.var('service_name').strip().lower()
    # Check for interfaces in HTTP request
    if service == 'cambium_ul_rssi' or service == 'cambium_ul_jitter':
		    # Get BS device name from mongo conf
		    device_name = get_parent(host=html.var('device_name'), db=False)
		    if html.var('interface'):
			    interface = html.var('interface')
    else:
	    device_name = html.var('device_name')
    if not device_name:
			response.update({
				'success': 0,
				'message': 'Service could not be deleted',
				'error_message': 'Could not find BS for this SS'
				}
				)
			return response
    payload = {
        "host": html.var("device_name"),
        "service": html.var("service_name"),
	"interface": interface
    }
    delete_host_rules(
		    hostname=device_name,
		    servicename=payload.get('service'),
		    interface=payload.get('interface'),
		    flag=True
		    )
    flag = write_new_host_rules()
    if not flag:
        response.update({
                "success": 0,
                "message": "Service Couldn't be deleted",
                "error_code": None,
                "error_message": "rules.mk is locked or some other message"
        })
        
    return response


def add_host_to_mongo_conf(**values):
	device_conf = {
			'host': values.get('host'),
			'ip': values.get('ip'),
			'interface': values.get('interface'),
			'parent_device_name': values.get('parent_device_name')
			}
	device_conf = dict(filter(lambda t: t[1], device_conf.items()))
	# Mongodb conn object
	try:
		conn = Connection(host='localhost', port=27017)
		db = conn['nocout']
		# Keep the latest host info
		db.device_conf.update(
				{ 'host': device_conf.get('host')},
				{'$set': device_conf},
				True
				)
	except pymongo.errors.PyMongoError, e:
		logger.error('Could not save the device conf into mongodb' + pprint.pformat(e))


def get_parent(host=None, db=True):
	bs = None
	if db:
		if host:
			try:
				conn = Connection(host='localhost', port=27017)
				db = conn['nocout']
				cur = db.device_conf.find({'host': host}, {'parent_device_name': 1, '_id': 0})
				for row in cur:
					logger.debug('Mongodb output: ' + pprint.pformat(row))
					bs = row
				bs = bs.get('parent_device_name')
			except pymongo.errors.PyMongoError, e:
				logger.error('Could not find BS name: ' + pprint.pformat(e))
	else:
		if host:
			load_file(hosts_file)
			# Filter out the host's old config
			# Filter the required row
			host_row = filter(lambda e: host in e, g_host_vars['all_hosts'])
			try:
				bs = host_row[0].split('|')[1]
			except AttributeError, e:
				logger.error('Could not find BS name' + pprint.pformat(e))

	return str(bs)


def set_ping_levels(host, ping_levels):
	global g_service_vars
	# Load rules file
	g_service_vars = {
    	"only_hosts": None,
    	"ALL_HOSTS": [],
    	"host_contactgroups": [],
    	"bulkwalk_hosts": [],
    	"extra_host_conf": {},
    	"extra_service_conf": {
            "retry_check_interval": [],
            "max_check_attempts": [],
            "normal_check_interval": []
    	   },
        "static_checks": {},
        "ping_levels": [],
        "checks": [],
        "snmp_ports": [],
        "snmp_communities": []
    	}
	try:
                os.open(rules_file, os.O_RDWR|os.O_CREAT)
                execfile(rules_file, g_service_vars, g_service_vars)
                del g_service_vars['__builtins__']
	except OSError, e:
		logger.error('Could not open rules file: ' + pprint.pformat(e))

	# Add tag for SNMP V2c devices in bulkwalk_hosts
	v2_hosts = g_service_vars['bulkwalk_hosts']
	if not filter(lambda x: 'snmp-v2' in x[0], v2_hosts):
		v2_hosts.append((["snmp-v2"], ALL_HOSTS))
		g_service_vars['bulkwalk_hosts'] = v2_hosts

	if ping_levels:
                # Delete existing ping rules for that host, first
                g_service_vars['ping_levels'] = filter(lambda t: host not in t[2], g_service_vars['ping_levels'])

		ping_rule_set = ({
			'loss': ping_levels.get('loss'),
			'packets': ping_levels.get('packets'),
			'rta': ping_levels.get('rta'),
			'timeout': ping_levels.get('timeout')
			},
			['wan'], [host], {}
		) 
		logger.debug('ping_rule_set:' + pprint.pformat(ping_rule_set))
		g_service_vars['ping_levels'].append(ping_rule_set)
	write_new_host_rules()

def delete_host_rules(hostname=None, servicename=None, interface=None, flag=False):
    global g_service_vars
    g_service_vars = {
        "only_hosts": None,
        "ALL_HOSTS": [],
        "host_contactgroups": [],
        "bulkwalk_hosts": [],
        "extra_host_conf": {},
        "extra_service_conf": {
            "retry_check_interval": [],
            "max_check_attempts": [],
            "normal_check_interval": []
        },
        "static_checks": {},
        "ping_levels": [],
        "checks": [],
        "snmp_ports": [],
        "snmp_communities": []
    }

    try:
	    os.open(rules_file, os.O_RDWR|os.O_CREAT)
	    execfile(rules_file, g_service_vars, g_service_vars)
	    del g_service_vars['__builtins__']
    except OSError, e:
	    logger.error('Could not open rules file: ' + pprint.pformat(e))

    if hostname is None:
        return
    if not servicename:
	if interface:
		g_service_vars['checks'] = map(lambda x: x, ifilterfalse(lambda t: hostname in t[0] and interface in t[2], g_service_vars['checks']))
	else:
                g_service_vars['ping_levels'] = filter(lambda t: hostname not in t[2], g_service_vars['ping_levels'])
		g_service_vars['checks'] = filter(lambda t: hostname not in t[0], g_service_vars['checks'])

		for serv_param, param_vals in g_service_vars['extra_service_conf'].items():
		    g_service_vars['extra_service_conf'][serv_param] = filter(lambda t: hostname not in t[2], param_vals)

		g_service_vars['snmp_ports'] = filter(lambda t: hostname not in t[2], g_service_vars['snmp_ports'])
		g_service_vars['snmp_communities'] = filter(lambda t: hostname not in t[-1], g_service_vars['snmp_communities'])

		for check, check_vals in g_service_vars['static_checks'].items():
		    g_service_vars['static_checks'][check] = filter(lambda t: hostname not in t[2], check_vals)
    else:
        if servicename.strip().lower() == 'ping':
            g_service_vars['ping_levels'] = filter(lambda t: hostname not in t[2], g_service_vars['ping_levels'])
            return
        if interface:
                iter_func = ifilterfalse(lambda t: hostname in t[0] and servicename in t[1] and interface in t[2], g_service_vars['checks'])
                g_service_vars['checks'] = map(lambda x: x, iter_func)
        else:
                iter_func = ifilterfalse(lambda t: hostname in t[0] and servicename in t[1], g_service_vars['checks'])
                g_service_vars['checks'] = map(lambda x: x, iter_func)
	    

	for serv_param, param_vals in g_service_vars['extra_service_conf'].items():
                iter_func = ifilterfalse(lambda t: hostname in t[2] and servicename in t[3], param_vals)
                g_service_vars['extra_service_conf'][serv_param] = map(lambda x: x, iter_func)
	if not flag:
                g_service_vars['snmp_ports'] = filter(lambda t: hostname not in t[2], g_service_vars['snmp_ports'])
                g_service_vars['snmp_communities'] = filter(lambda t: hostname not in t[-1], g_service_vars['snmp_communities'])


def write_new_host_rules():
    global g_service_vars
    open(rules_file, 'w').close()
    try:
        f = os.open(rules_file, os.O_RDWR)
    except OSError, e:
	    logger.error('Could not open rules files: ' + pprint.pformat(e))

    fcntl.flock(f, fcntl.LOCK_EX)
    os.write(f, "bulkwalk_hosts = ")
    os.write(f, pprint.pformat(g_service_vars['bulkwalk_hosts']))
    os.write(f, " + bulkwalk_hosts\n\n")
    os.write(f, "ping_levels = ")
    os.write(f, pprint.pformat(g_service_vars['ping_levels']))
    os.write(f, " + ping_levels\n\n")
    os.write(f, "checks += ")
    os.write(f, pprint.pformat(g_service_vars['checks']))
    os.write(f, "\n\n")
    os.write(f, "snmp_ports += ")
    os.write(f, pprint.pformat(g_service_vars['snmp_ports']))
    os.write(f, "\n\n")
    os.write(f, "snmp_communities += ")
    os.write(f, pprint.pformat(g_service_vars['snmp_communities']))
    os.write(f, "\n\n")

    for serv_param, param_vals in g_service_vars['extra_service_conf'].items():
        os.write(f, 'extra_service_conf[' + pprint.pformat(serv_param) + '] = ')
        os.write(f, pprint.pformat(param_vals))
        os.write(f, '\n\n')
    os.close(f)

    return True


def sync():
    logger.debug('[-- sync --]')
    sites_affected = []
    response = {
        "success": 1,
        "message": "Config pushed to "
    }
    # Snapshot for the local-site; to be used only by master site
    #nocout_create_snapshot()

    # Create backup for the hosts and rules file
    if os.path.exists(hosts_file):
        os.system('rsync -a %s /opt/omd/sites/%s/nocout/' % (hosts_file, defaults.omd_site))
    if os.path.exists(rules_file):
        os.system('rsync -a %s /opt/omd/sites/%s/nocout/' % (rules_file, defaults.omd_site))

    nocout_create_sync_snapshot()
    nocout_sites = nocout_distributed_sites()
    try:
        f = os.system('~/bin/cmk -R')
	logger.debug('f : '  + pprint.pformat(f))
    except Exception, e:
        logger.error('[sync]' + pprint.pformat(e))
    if f == 0:
        sites_affected.append(defaults.omd_site)
    for site, attrs in nocout_sites.items():
	logger.debug('site :' + pprint.pformat(site))
        response_text = nocout_synchronize_site(site, attrs, True)
        if response_text is True:
            sites_affected.append(site)
    if len(sites_affected) == len(nocout_sites):
        response.update({
            "message": "Config pushed to " + ','.join(sites_affected)
        })
    else:
        if os.path.exists('/opt/omd/sites/%s/nocout/rules.mk' % defaults.omd_site):
            os.system('cp /opt/omd/sites/%s/nocout/rules.mk %s' % (defaults.omd_site, rules_file))
            for site, attrs in nocout_sites.items():
                response_text = nocout_synchronize_site(site, attrs, True)
            response.update({
                "message": "Problem with the new config, old config retained",
                "success": 1
            })
        else:
            response.update({
                "message": "Config not pushed",
                "success": 0
            })
    logger.debug('[-- sync finish --]')
    return response


def nocout_synchronize_site(site, site_attrs, restart):
    response = nocout_push_snapshot_to_site(site, site_attrs, True)

    return response


def nocout_distributed_sites():
    logger.debug('[nocout_distributed_sites]')
    nocout_site_vars = {
        "sites": {}
    }
    sites_file = defaults.default_config_dir + "/multisite.d/sites.mk"
    if os.path.exists(sites_file):
        execfile(sites_file, nocout_site_vars, nocout_site_vars)
    logger.debug('Slave sites to push data to - ' + pprint.pformat(nocout_site_vars.get('sites')))
    logger.debug('[--]')

    return nocout_site_vars.get('sites')


def nocout_push_snapshot_to_site(site, site_attrs, restart):
    mode = "slave"
    url_base = site_attrs.get('multisiteurl') + "automation.py?"
    var_string = htmllib.urlencode_vars([
        ("command", "push-snapshot"),
        ("siteid", site),
        ("mode", mode),
        ("restart", "yes"),
        ("debug", "1"),
        ("secret", site_attrs.get('secret'))
    ])
    url = url_base + var_string
    try:
            response_text = upload_file(url, sync_snapshot_file, '')
    except:
	    logger.debug('Slave site ' + pprint.pformat(site) + ' not running')
            return "Garbled response from automation"

    try:
        response = eval(response_text)
	logger.debug('Push to site : ' + pprint.pformat(site) + ' response ' + pprint.pformat(response))
        return response
    except:
        return "Garbled response from automation"


def nocout_create_sync_snapshot():
    global nocout_replication_paths
    #os.remove(sync_snapshot_file)
    tmp_path = "%s-%s" % (sync_snapshot_file, 'nocout')
    multitar.create(tmp_path, nocout_replication_paths)
    os.rename(tmp_path, sync_snapshot_file)


def nocout_create_snapshot():
    global nocout_backup_paths
    snapshot_name = "wato-snapshot-%s.tar.gz" %  \
                    time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
    multitar.create(snapshot_dir + snapshot_name, nocout_backup_paths)

    return "Snapshot created " + snapshot_name
    

def load_file(file_path):
    global g_host_vars
    #Reset the global vars
    g_host_vars = {
        "FOLDER_PATH": "",
        "ALL_HOSTS": ALL_HOSTS, # [ '@all' ]
        "all_hosts": [],
        "clusters": {},
        "ipaddresses": {},
        "extra_host_conf": { "alias" : [] },
        "extra_service_conf": { "_WATO" : [] },
        "host_attributes": {},
        "host_contactgroups": [],
        "_lock": False,
    }
    try:
        execfile(file_path, g_host_vars, g_host_vars)
        del g_host_vars['__builtins__']
    except IOError, e:
        pass


def save_host(file_path):
    global g_host_vars
    #Erase the file contents first
    open(file_path, 'w').close()
    try:
        f = os.open(file_path, os.O_RDWR)
    except OSError, e:
	    logger.error('Could not open rules file: ' + pprint.pformat(e))

    fcntl.flock(f, fcntl.LOCK_EX)
    os.write(f, "# encoding: utf-8\n\n")

    os.write(f, "\nhost_contactgroups += [\n")
    for host_contactgroup in g_host_vars.get('host_contactgroups'):
        os.write(f, pprint.pformat(host_contactgroup))
        os.write(f, ",\n")
    os.write(f, "]\n\n")

    os.write(f, "all_hosts += [\n")

    for host in g_host_vars.get('all_hosts'):
        os.write(f, pprint.pformat(host))
        os.write(f, ",\n")
    os.write(f, "]\n")

    os.write(f, "\n# Explicit IP addresses\n")
    os.write(f, "ipaddresses.update(")
    os.write(f, pprint.pformat(g_host_vars.get('ipaddresses')))
    os.write(f, ")")
    os.write(f, "\n\n")

    os.write(f, "host_attributes.update(\n%s)\n" 
        % pprint.pformat(g_host_vars.get('host_attributes'))
    )
    os.close(f)

    return True


def save_service(host, service_name, host_tag, service_tuple, serv_params, ping_levels, snmp_port_tuple, snmp_community):
    conf = None
    try:
        with open(rules_file, 'a') as f:
            if service_tuple[3]:
                f.write("\nchecks += [\n")
                f.write(" " + pprint.pformat(service_tuple) + "\n")
                f.write("]\n")
            if snmp_port_tuple:
                f.write("\nsnmp_ports += [\n")
                f.write(" " + pprint.pformat(snmp_port_tuple) + "\n")
                f.write("]\n\n")
            if serv_params:
                for param, val in serv_params.items():
                    f.write('extra_service_conf["' + param + '"] = [\n')
                    conf = (val, [host_tags.get(host_tag, 'snmp')], [host], service_name)
                    f.write(pprint.pformat(conf) + "\n")
                    f.write("]")
                    f.write('\n\n')
            if ping_levels:
                conf = None
                f.write("ping_levels += [\n(")
                conf = ({
                    'loss': ping_levels.get('pl', (80.0, 100.0)),
                    'rta': ping_levels.get('rta', (3000.0, 5000.0)),
                    'packets': ping_levels.get('packets', 20)
                })
                f.write(pprint.pformat(conf) + "),\n]")
                f.write("\n\n")
            if snmp_community:
                f.write("snmp_communities += [\n")
                f.write(pprint.pformat(snmp_community) + ",\n]")
                f.write("\n\n")
    except OSError, e:
        raise OSError(e)
    

def nocout_add_host_attributes(host_attrs):
    global host_tags
    # Filter out the host's old config
    g_host_vars['all_hosts'] = filter(lambda t: not re.match(host_attrs.get('host'), t), g_host_vars['all_hosts'])
    host_entry = "%s|wan|prod|%s|site:%s|wato|//" % (
    host_attrs.get('host'), host_tags.get(html.var('agent_tag'), 'snmp'), host_attrs.get('site'))
    # Insert the ip of the parent device, as an auxiliary tag for the host
    if host_attrs.get('parent_device_name'):
	    host_entry = host_entry[:(host_entry.find('|') + 1)] + str(host_attrs.get('parent_device_name')) + \
			    '|' + host_entry[(host_entry.find('|') + 1):]

    g_host_vars['all_hosts'].append(host_entry)

    g_host_vars['ipaddresses'].update({
        host_attrs.get('host'): host_attrs.get('attr_ipaddress')
    })
    g_host_vars['host_attributes'].update({
        host_attrs.get('host'): {
            'alias': host_attrs.get('attr_alias'),
            'contactgroups': (True, ['all']),
            'ipaddress': host_attrs.get('attr_ipaddress'),
            'site': host_attrs.get('site'),
            'tag_agent': host_tags.get(html.var('agent_tag'))
        }
    })


def nocout_find_host(host):
    new_host = True
    ALL_HOSTS = None
    local_host_vars = {
        "FOLDER_PATH": "",
        "ALL_HOSTS": ALL_HOSTS, # [ '@all' ]
        "all_hosts": [],
        "clusters": {},
        "ipaddresses": {},
        "extra_host_conf": { "alias" : [] },
        "extra_service_conf": { "_WATO" : [] },
        "host_attributes": {},
        "host_contactgroups": [],
        "_lock": False,
    }
    try:
        execfile(hosts_file, local_host_vars, local_host_vars)
        for entry in local_host_vars['all_hosts']:
            if host in entry:
                new_host = False
                break
    except IOError, e:
        pass

    return new_host


def give_permissions(file_path):
    import grp
    fd = os.open(file_path, os.O_RDWR | os.O_CREAT)
    # Give file permissions to apache user group
    #gid = grp.getgrnam('www-data').gr_gid
    os.chmod(file_path, 0775)
    os.close(fd)
