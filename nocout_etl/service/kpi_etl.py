#!/usr/bin/python
import time
import sys
import os
import socket
import pymongo
from celery import chord,group
from ast import literal_eval
from datetime import datetime,timedelta
from sys import path
path.append('/omd/nocout_etl')

from itertools import izip_longest

from start.start import app
from handlers.db_ops import *
from service.service_etl import *


logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error

INVENTORY_DB = getattr(app.conf, 'INVENTORY_DB', 3)


"""
Poller script which runs on ss and calculates the ul utilization of the ss connected from BS.

Poller script determines the uplink utilization of the ss.
poller script takes the snmp value of OID .1.3.6.1.4.1.161.19.3.1.4.1.21 from snmp agent of device at specific interval.
uplink utilization information is /sent to device application 

"""
# ##################################################################
# Function : check_wimax_pmp1_dl_utilization_kpi
#
#  Parameters: info(SNMP output) ,params(parameters to check the service state) 
#
#  Output: service state,plugin output ,performance data
##################################################################

def extract_cambium_bs_ul_issue_data(hostname,site,ip_address,service_list,**args):
	"""
	Connects to a socket, checks for the WELCOME-MSG and closes the
	connection.
	Returns nothing.

	"""
	d = {}
	final_value = []
	sect_id =''
	ul_issue = ''
	try:
		connected_ss_entry = extract_cambium_connected_ss(hostname,args)
		if not connected_ss_entry:
			connected_ss_entry = extract_connected_ss_from_topology(hostname)
			for ip,sect_id,machine in connected_ss_entry:
				d.setdefault(machine, [machine]).append(str(ip))
			mapped_ip = map(tuple, d.values())
			total = 0
			for entry in mapped_ip:
				try:
					db=args['mysql']
					if len(entry[1:]) == 1:
						ip_tuple = "('%s')" % entry[1:][0]
					else:
						ip_tuple = str(entry[1:])
					query = "select current_value from performance_utilizationstatus where "+\
					"service_name='cambium_ss_ul_issue_kpi' and ip_address in " + ip_tuple
					cur = db.cursor()
					cur.execute(query)
					data = cur.fetchall()
					cur.close()
					db.close()
				except:
					if db:
						db.close()
					continue
				value = [str(item) for sublist in data for item in sublist]
				final_value.extend(value)	
				for num in final_value:
					if num != '':
						total = total+int(num)
				if len(final_value):
					ul_issue = (total/float(len(final_value)))*100
		else:
			sect_id = extract_cambium_bs_sec_id(hostname)
			ss_ul_issue =collect_cambium_ss_ul_issue_data(connected_ss_entry,args)
			if len(connected_ss_entry) > 0:
				ul_issue = sum(ss_ul_issue)/float(len(connected_ss_entry)) * 100 
	except:
		ul_issue = None

	try:	
		if ul_issue != None and ul_issue != '':
			if ul_issue < args['war']:
                		state = 0
				state_string = "ok"
			elif ul_issue >= args['crit']:
				state = 2
				state_string = "critical"
			else:
				state = 1
				state_string = "warning"
		perf += 'bs_ul_issue' + "=%s;%s;%s;%s " %(ul_issue,args['war'],args['crit'],sect_id)
   
    	except:
        	perf = ';%s;%s;%s' % (args['war'],args['crit'],sect_id)

    	service_dict = service_dict_for_kpi_services(perf,state_string,hostname,site,ip_address,**args)
    	service_dict['refer'] = sect_id

	service_list.append(service_dict)
    	return service_dict

def extract_connected_ss_from_topology(hostname,**args):
        query = """select connected_device_ip from performance_topology where device_name ='%s' """ %(hostname)
	query1 = """ select M.name, D.ip_address from device_device as D left join machine_machine as M on (D.machine_id = M.id) where D.ip_address in 
	(select connected_device_ip from performance_topology where device_name ='%s')""" %(hostname)
	
	query3 ="""select device_device.ip_address, performance_topology.sector_id,machine_machine.name from 
	device_device  join (machine_machine, performance_topology)  on  ( device_device.machine_id  = machine_machine.id  and 
	device_device.ip_address = performance_topology.connected_device_ip ) where performance_topology.device_name = """ % pformat(hostname)

	query2 ="""select device_device.ip_address, performance_topology.sector_id,performance_topology.refer,machine_machine.name from 
	device_device  join (machine_machine, performance_topology)  on  ( device_device.machine_id  = machine_machine.id  and 
	device_device.ip_address = performance_topology.connected_device_ip ) where performance_topology.device_name in %s """ % pformat((hostname,args['dr_slave']))
	

	if 'wimax' in args['service']:
		mysql_query = query2
	elif 'cambium' in args['service']:
		mysql_query = query3	
	try:
		db = args['mysql']
		cur = db.cursor()
		cur.execute(mysql_query)
		data = cur.fetchall()
		cur.close()
	except  Exception,e:
		data = None

        return data

def extract_cambium_connected_ss(hostname,memc_conn):
	ss_connected = []
	try:
		if memc_conn:
			ss_connected = memc_conn.get("%s_conn_ss" % str(hostname))
	except Exception,e:
		warning('cambium connected ss: {0}'.format(e))
		pass
	return ss_connected

def extract_wimax_connected_ss(hostname,dr_slave,memc_conn):
	dr_pmp1_conn_ss_ip = dr_pmp2_conn_ss_ip = []
	pmp1_conn_ss_ip = pmp2_conn_ss_ip = []
        try:
		ss_connected_list = memc_conn.get("%s_conn_ss" % str(hostname))
		#pmp1_ss_connected = args['memc'].get("pmp1_%s" % hostname)
		#pmp2_ss_connected = args['memc'].get("pmp2_%s" % hostname)
		pmp1_conn_ss_ip=ss_connected_list[0].get(1)
		pmp2_conn_ss_ip=ss_connected_list[0].get(2)
		if dr_slave:
			dr_ss_connected_list = memc_conn.get("%s_conn_ss" % str(hostname))
			#dr_pmp1_ss_connected = args['memc'].get("pmp1_%s" % dr_slave)
			#dr_pmp2_ss_connected = args['memc'].get("pmp2_%s" % dr_slave)
			dr_pmp1_conn_ss_ip=dr_ss_connected_list[0].get(1)
			dr_pmp2_conn_ss_ip=dr_ss_connected_list[0].get(2)
	except Exception,e:
		warning('wimax connected ss: {0}'.format(e))
		pass
	if len(dr_pmp1_conn_ss_ip) > 0 or len(dr_pmp2_conn_ss_ip) > 0:
		return dr_pmp1_conn_ss_ip,dr_pmp2_conn_ss_ip
	#warning('wimax connected ss: {0} {1}'.format(pmp1_conn_ss_ip,pmp2_conn_ss_ip))
	return pmp1_conn_ss_ip,pmp2_conn_ss_ip

def collect_wimax_ss_ul_issue_data(pmp1_conn_ss_ip,pmp2_conn_ss_ip,**args):
	pmp1_ss_ul_issue = map(lambda x : args['memc'].get("ul_issue_%s" % x),pmp1_conn_ss_ip)
	pmp2_ss_ul_issue = map(lambda x : args['memc'].get("ul_issue_%s" % x),pmp2_conn_ss_ip)
	pmp1_ss_ul_issue =  filter( lambda x: x is not None ,pmp1_ss_ul_issue)	
	pmp2_ss_ul_issue =  filter( lambda x: x is not None ,pmp2_ss_ul_issue)	
	
	
	return pmp1_ss_ul_issue,pmp2_ss_ul_issue

def collect_cambium_ss_ul_issue_data(conn_ss_ip,**args):
	ss_ul_issue = map(lambda x : args['memc'].get("ul_issue_%s" % x),conn_ss_ip)
	ss_ul_issue =  filter( lambda x: x is not None ,ss_ul_issue)	
	
	return ss_ul_issue

def extract_cambium_bs_sec_id(hostname,memc_conn):
	sec_id =  ''
	try:
		if memc_conn:
			sec_id = memc_conn.get(str(hostname) + "_sec_id")
	except:
		pass
	return sec_id


def extract_wimax_bs_sec_id(hostname,memc_conn):
	pmp1_sec_id = pmp2_sec_id = ''
	try:
		if memc_conn:
			pmp1_sec_id = memc_conn.get(str(hostname) + "_pmp1_sec")
			pmp2_sec_id = memc_conn.get(str(hostname) + "_pmp2_sec")
	except Exception,e:
		warning('memc error: {0}'.format(e))
		pass
	if pmp1_sec_id == None:
		pmp1_sec_id = ''
	if  pmp2_sec_id == None:
		pmp2_sec_id = ''
	return pmp1_sec_id,pmp2_sec_id 
def extract_wimax_bs_ul_issue_data(hostname,site,ip_address,service_list,**args):
        """
        Connects to a socket, checks for the WELCOME-MSG and closes the
        connection.
        Returns nothing.
    
        """
	d1= {}
	d2= {}
	final_value = []
	pmp1_ul_issue = ''
	pmp2_ul_issue = ''
	pmp1_sect_id = ''
	pmp2_sect_id = ''
	try:
		pmp1_conn_ss_ip,pmp2_conn_ss_ip = extract_wimax_connected_ss(hostname,args)
		if not pmp1_conn_ss_ip and not pmp2_conn_ss_ip:
			connected_ss_entry = extract_connected_ss_from_topology(hostname,args)
			for ip,sector_id,port,machine in connected_ss_entry:
				if port in d1.keys():
					d1[port].append(str(ip))
				else:
					d1[port]= []
					d1[port].append(str(ip))
					if port == '1':
						pmp1_sect_id = sector_id
					if port == '2':
						pmp2_sect_id = sector_id
				if machine in d2.keys():
					d2[machine].append(str(ip))
				else:
					d2[machine]= []
					d2[machine].append(str(ip))
			pmp1_count = 0
			pmp2_count = 0
			for machine_name in d2:
				try:
					db=mysql_conn(machine=machine_name)
					ip_tuple = str(tuple(d2[machine_name]))
				
					query = "select ip_address,current_value from performance_utilizationstatus where "+ \
					"service_name='wimax_ss_ul_issue_kpi' and ip_address in " + ip_tuple
					cur = db.cursor()
					cur.execute(query)
					data = cur.fetchall()
					cur.close()
					db.close()
				except Exception,e:
					if db:
						db.close()
					continue
				for entry_value in data:
					ip =str(entry_value[0])
					value = entry_value[1]
					try:
						if ip in d1['1'] and value != '':
							pmp1_count = pmp1_count + int(value)
							continue
					except Exception,e:
						pass
					try:
						if ip in d1['2'] and value != '':
							pmp2_count = pmp2_count + int(value)
					except Exception,e:
						pass
				try:				
					if len(d1['1']):
						pmp1_ul_issue = (pmp1_count/float(len(d1['1'])))*100
				except Exception,e:
					pmp1_ul_issue = ''
				try:
					if len(d1['2']):
						pmp2_ul_issue = (pmp2_count/float(len(d1['2'])))*100
				except Exception,e:
					pmp2_ul_issue = ''
		else:
			pmp1_sect_id,pmp2_sect_id = extract_bs_sec_id(hostname)
			pmp1_ss_ul_issue,pmp2_ss_ul_issue =collect_wimax_ss_ul_issue_data(pmp1_conn_ss_ip,pmp2_conn_ss_ip,args)
			if len(pmp1_conn_ss_ip) > 0:
				pmp1_ul_issue = sum(pmp1_ss_ul_issue)/float(len(pmp1_conn_ss_ip)) * 100 
			if len(pmp2_conn_ss_ip) > 0:
				pmp2_ul_issue = sum(pmp2_ss_ul_issue)/float(len(pmp2_conn_ss_ip)) * 100

	except Exception,e:
		pmp1_ul_issue = ''
		pmp2_ul_issue = ''
		pmp2_sect_id= ''	
		pmp1_sect_id= ''	
	try:
		if pmp1_ul_issue != '':
                	pmp1_ul_issue = "%.2f" % pmp1_ul_issue
                	if float(pmp1_ul_issue) < args['war']:
                        	pmp1_state = 0
               	 	elif float(pmp1_ul_issue) >= args['crit']:
                        	pmp1_state = 2
                	else:
                        	pmp1_state = 1
        	if pmp2_ul_issue != '':
                	pmp2_ul_issue = "%.2f" % pmp2_ul_issue
                	if float(pmp2_ul_issue) < args['war']:
                        	pmp2_state = 0
                	elif float(pmp2_ul_issue) >= args['crit']:
                        	pmp2_state = 2
                	else:
                        	pmp2_state = 1
        	state = max(pmp1_state,pmp2_state)
        	state_string= match_severity[state]
        	perf += 'pmp1_ul_issue' + "=%s;%s;%s;%s " %(pmp1_ul_issue,args['war'],args['crit'],pmp1_sect_id)
        	perf += 'pmp2_ul_issue' + "=%s;%s;%s;%s " %(pmp2_ul_issue,args['war'],args['crit'],pmp2_sect_id)
    	except Exception,e:
        	state= 3
        	state_string = "unknown"
        	perf = ';%s;%s' % (args['war'],args['crit'])
    	service_dict = service_dict_for_kpi_services(perf,state_string,hostname,site,ip_address,**args)
    	return service_dict

@app.task(base=DatabaseTask, name ='extract_wimax_bs_ul_data')
def extract_wimax_bs_ul_data(ul_issue_list,host_name,site,ip,sect_id,sec_type,**args):
	count = 0
	perf = ''
	sec_ul_issue = ''
	state_string = 'unknown'
	#warning('wimax ss entry: {0}'.format(ul_issue_list))
        rds_cli = RedisInterface()
	for service_dict in ul_issue_list:
		try:
			value = int(service_dict['perf_data'].split('=')[1].split(';')[0])
		except Exception,e:
			warning('wimax_bs_ul_issue: {0}'.format(e))
			continue
		else:
			count = count +value
	try:	
		if len(ul_issue_list):	
			sec_ul_issue = count/float(len(ul_issue_list)) * 100
		if sec_ul_issue != '':
			sec_ul_issue = "%.2f" % sec_ul_issue
			if float(sec_ul_issue) < args['war']:
				state = 0
				state_string = "ok"
			elif float(sec_ul_issue) >= args['crit']:
				state = 2
				state_string = "critical"
			else:
				state = 1
				state_string = "warning"
		
		perf = ''.join('%s_ul_issue' % sec_type + "=%s;%s;%s;%s" %(sec_ul_issue,args['war'],args['crit'],sect_id))
	except:
		perf = ';%s;%s;%s' % (args['war'],args['crit'],sect_id)
	args['service'] = 'wimax_bs_ul_issue_kpi'
    	bs_service_dict = service_dict_for_kpi_services(perf,state_string,host_name,site,ip,**args)
	bs_service_dict['refer'] =sect_id
	ul_issue_list.append(bs_service_dict)		
	#warning('wimax bs entry: {0}'.format(ul_issue_list))
	rds_cli.redis_cnx.rpush('queue:ul_issue',*ul_issue_list)


def extract_cambium_util_data(host_params,**args):
    perf = cam_util = sec_id = plugin_message = ''
    state = 3
    state_string = "unknown"
    service_list = []
    util_type = args['service'].split('_')[1]
    for entry in host_params:
	if entry and len(eval(entry[0])) == 3 :
		hostname,site,ip_address = eval(entry[0])
	else:
		break
    	try:
        	if args['memc']:
        		sec_id = args['memc'].get(str(hostname) + "_sec_id")
			cam_util = args['memc'].get(str(hostname) + "_" + util_type)
			if cam_util:
				cam_util = literal_eval(cam_util)
    	except Exception,e:
		warning('memc: {0}'.format(e))
        	sec_id = ''
    	try:
		if not cam_util:
			service_name = 'cambium_%s_utilization' % util_type	
			query_string = "GET services\nColumns: service_perf_data\nFilter: host_name =%s\n" % (hostname) +\
	       		"Filter: service_description = %s\n" % service_name +\
	       		"OutputFormat: python\n"
			output = extract_data_from_live(hostname,site,query_string)
			try:
				if output[0][0]:
					cam_util = output[0][0].split('=')[1].split(';')[0]
			except:
				cam_util = None
		if cam_util:
			cam_util = (float(cam_util)/float(args['provis_bw'] )) * 100
			cam_util = round(cam_util,2)
			if cam_util < args['war']:
				state = 0
				state_string = "ok"
			elif cam_util >= args['crit']:
				state = 2
				state_string = "critical"
			else:
				state = 1
				state_string = "warning"
			perf = 'cam_%s_util_kpi' % util_type + "=%s;%s;%s;%s" %(cam_util,args['war'],args['crit'],sec_id)
	except Exception,e:
		warning('cam ss util: {0}'.format(e))
		perf = 'cam_%s_util_kpi' % util_type + "=;%s;%s;%s" %(args['war'],args['crit'],sec_id)
	service_dict = service_dict_for_kpi_services(perf,state_string,hostname,site,ip_address,**args)
	service_dict['refer'] = sec_id
	service_list.append(service_dict)
	cam_util = ''
	sec_id = ''
	perf = ''
    	state_string = "unknown"
    if len(service_list) > 0: 	
    	build_export.s(args['site_name'], service_list).apply_async()
    return None
 
def extract_wimax_util_data(host_params,**args):
    state = 3
    status_list = []
    service_list=[]
    for entry in host_params:
    	total = util = dr_util = sec_bw = dr_slave =None
    	state_string = "unknown"
    	perf = sec_kpi = sec_id = plugin_message = ''
	if entry  and len(eval(entry[0]))  == 4:
		hostname,site,ip_address,dr_slave = eval(entry[0])
	elif entry and len(eval(entry[0])) == 3:
		hostname,site,ip_address = eval(entry[0])
		dr_slave  = None
	else:
		break
	util_type = args['service'].split('_')[2]
	sec_type = args['service'].split('_')[1]

	service_name = 'wimax_%s_%s_util_bgp' % (sec_type,util_type)

	#warning('memc: {0}'.format(args))
	bw_query_string = "GET services\nColumns: plugin_output\nFilter: " + \
		"service_description = %s\nFilter: host_name =%s\nOutputFormat: python\n" % ("wimax_pmp_bw_invent",hostname)
	sec_util_query_string = "GET services\nColumns: service_perf_data\n" + \
		"Filter: service_description = %s\n"  % service_name + \
		"Filter: host_name = %s\nFilter: host_name =%s\nOr: 2\nOutputFormat: python\n" % (hostname,dr_slave)
	try:
		if args['memc']:
			sec_id_suffix = "_%s_sec" % sec_type
			util_suffix = "_%s_%s_util" % (sec_type,util_type)
			bw_suffix = "_%s_bw" % sec_type

			sec_id = args['memc'].get(str(hostname) + sec_id_suffix)
			util = args['memc'].get(str(hostname) + util_suffix)
			sec_bw = args['memc'].get(str(hostname) + bw_suffix)
			if sec_bw:
				sec_bw = literal_eval(sec_bw)
			if util:
				util = literal_eval(util)
			#warning('util: {0} ,{1},{2}'.format(util,hostname,service_name))
			#warning('sec_id: {0}'.format(sec_bw))
			if dr_slave:
				dr_util = args['memc'].get(dr_slave + util_suffix)
				if dr_util:
					dr_util = literal_eval(dr_util)
	except Exception,e:
		warning('Error in memc: {0}'.format(e))
		pass


    	try:
		if not sec_bw:
			bw_output = extract_data_from_live(hostname,site,bw_query_string)
			if sec_type == 'pmp1':
				pmp_bw_string = 0
			elif sec_type == 'pmp2':	
				pmp_bw_string = 1
			if bw_output:
				try:
					bw_output = bw_output[0][0] 
					output = [entry for entry in bw_output.split(' - ')[1].split()]
					sec_bw=eval(output[pmp_bw_string].split('=')[1])
				except Exception,e:
					#warning('Error in wimax util: {0}'.format(e))
					sec_bw = None

		if util is None and dr_util is None:
			util_output = extract_data_from_live(hostname,site,sec_util_query_string)
			try:
				if util_output[0][0]:
					util = eval(util_output[0][0].split('=')[1].split(';',1)[0])
			except:
				util = None
			try:
				if dr_slave and util_output[1][0]:
					dr_util = eval(util_output[1][0].split('=')[1].split(';',1)[0])
			except:
				dr_util = None

		if util != None and dr_util != None:
			total = util + dr_util
		elif util != None :
			total = util
		elif dr_util != None:
			total = dr_util

		if sec_bw and total != None:
			if sec_bw <= 3:
				sec_kpi = (float(total)/int(args['provis_bw'])) *100
			elif sec_bw  > 3:
				sec_kpi = (float(total)/(2*int(args['provis_bw']))) *100
			else:
				sec_kpi = ''
		if isinstance(sec_kpi,(float,int)) :
			if sec_kpi > 100:
				sec_kpi = 100.00

			if sec_kpi < args['war']:
				state = 0
				state_string = "ok"
			elif sec_kpi >= args['crit']:
				state = 2
				state_string = "critical"
			else:
				state = 1
				state_string = "warning"
		
		perf += '%s_%s_util_kpi' %(sec_type,util_type) + "=%s;%s;%s;%s" % (sec_kpi,args['war'],args['crit'],sec_id)
		#warning('wimax util: {0} {1} {2}'.format(util,sec_bw,perf))
    	except Exception as e:
		perf = ';%s;%s' % (args['war'],args['crit']) 
		warning('Error in wimax util: {0}'.format(e))
		
    	service_dict = service_dict_for_kpi_services(perf,state_string,hostname,site,ip_address,**args)
	#warning('dl_util: {0}'.format(service_dict))

    	service_dict['refer'] = sec_id

    	service_list.append(service_dict)
    if len(service_list) > 0: 	
    	build_export.s(args['site_name'], service_list).apply_async()
    #return None

def extract_data_from_live(hostname,site,query):
        """
        Connects to a socket, checks for the WELCOME-MSG and closes the
        connection.
        Returns nothing.
    
        """
	query_output = ''
        #pmp_bw = None
        #query_string = "GET services\nColumns: plugin_output\nFilter: " + \
        #                "service_description = %s\nFilter: host_name = %s\nOutputFormat: python\n" % ("wimax_pmp_bw_invent",hostname)

	try:
		s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		socket_path = "/omd/dev_slave/slave_2/var/run/live" 

		s.connect(socket_path)
		s.send(query)
		s.shutdown(socket.SHUT_WR)
		while True:
		    try:
        		out = s.recv(100000000)
     		    except socket.timeout,e:
        		break
     		    out.strip()
     		    if not len(out):
       			break
     		    query_output += out
        	#query_output = s.recv(100000000)
        	#query_output.strip("\n")
		#query_output = eval(query_output)
        	#if query_output:
		#	query_output = query_output[0][0] 
		#	output = [entry for entry in query_output.split(' - ')[1].split()]
                #	pmp_bw=output[0].split('=')[1]
	except Exception,e:
		query_output = ''

	return query_output
def service_dict_for_kpi_services(perf,state,hostname,site,ip_address,**args):	
    service_dict = {}
    service_dict['host_name'] = hostname
    service_dict['address'] = ip_address 
    service_dict['site'] = site
    service_dict['perf_data'] = perf
    service_dict['last_state_change'] = ''
    service_dict['state']  = state
    service_dict['last_chk'] = time.time()
    service_dict['service_description']=args['service']
    return service_dict	

@app.task(base=DatabaseTask,name='extract_ss_ul_issue_data')
def extract_ss_ul_issue_data(ss_info,bs_host_name,bs_site_name,bs_ip_address,sect_id,sec_type,redis_conn,**args):
    state = 3
    ul_issue =0
    perf = ''
    plugin_message = ''
    DB = None
    
    state_string = "unknown"
    service_state_type = ["warning","critical"]
    service_dict_list = []
    #warning('ss info: {0}'.format(ss_info))

    for entry in ss_info:
	if entry:
		host_name ,site ,ip_address = literal_eval(entry[0])
	else:
		break
	try:
		service_state_out = []
		ss_serv_key = redis_conn.redis_cnx.keys(pattern="ul_issue:%s:*" % host_name)
		p = redis_conn.redis_cnx.pipeline()
		#warning('redis_cnx: {0}'.format(redis_conn))
		[p.lrange(k, 0 , -1) for k  in ss_serv_key]
		service_values = p.execute()
		#warning('service values: {0}'.format(service_values))
		for entry in service_values:
			service_state_out.extend(entry)
			
		if len(service_state_out) == 4:
			state_string = "ok"
			state = 0
			for entry in service_state_out:
				if str(entry) in service_state_type:
					ul_issue=1
					continue
				else:
					ul_issue = 0
					break
		perf += 'ul_issue' + "=%s;;;" % (ul_issue)
	except Exception ,e:
		warning('error: {0}'.format(e))
		perf = '' 
	service_dict = service_dict_for_kpi_services(perf,state_string,host_name,site,ip_address,**args)
	service_dict_list.append(service_dict)
	#redis_conn = str(args['redis'])
	#arg['redis'] = ''
    #warning(' info: {0}'.format(service_dict_list))
    if 'cambium' in args['service']:
	extract_cambium_bs_ul_data.s(service_dict_list,bs_host_name,bs_site_name,bs_ip_address,sect_id,**args).apply_async()
    elif 'wimax' in args['service']:
    	extract_wimax_bs_ul_data.s(service_dict_list,bs_host_name,bs_site_name,bs_ip_address,sect_id ,sec_type,**args).apply_async()  
  


@app.task(base=DatabaseTask,name='call_kpi_services')
def call_kpi_services(**opts):
	rds_cli_invent = RedisInterface(custom_conf={'db': INVENTORY_DB})
	#wimax_bs_key = rds_cli.redis_cnx.keys(pattern="wimax:bs:*")
	wimax_bs_key = rds_cli_invent.redis_cnx.keys(pattern="wimax:bs:pub_slave_1:*")
	#wimax_ss_key = rds_cli.redis_cnx.keys(pattern="wimax:ss:*")
	wimax_ss_key = rds_cli_invent.redis_cnx.keys(pattern="wimax:ss:pub_slave_1:*")
	pmp_bs_key = rds_cli_invent.redis_cnx.keys(pattern="pmp:bs:pub_slave_1:*")
	pmp_ss_key = rds_cli_invent.redis_cnx.keys(pattern="pmp:ss:pub_slave_1:*")
	p = rds_cli_invent.redis_cnx.pipeline()
	wimax_util_kpi_services = ['wimax_pmp1_dl_util_kpi','wimax_pmp2_dl_util_kpi','wimax_pmp1_ul_util_kpi','wimax_pmp2_ul_util_kpi','wimax_ss_ul_issue_kpi','wimax_ss_provis_kpi']
	cambium_util_kpi_services = ['cambium_dl_util_kpi','cambium_ul_util_kpi','cambium_ss_ul_issue_kpi','cambium_ss_porvis_kpi']
	for i in izip_longest(*[iter(wimax_bs_key)] * 500):	
		[p.lrange(k, 0 , -1) for k  in i]
		#[p.lrange(k, 0,-1) for k  in ]
		#[p.lrange(k, 0,-1) for k  in wimax_ss_key]
		wimax_bs_params = p.execute()
		args = {}
		args['host_info'] = wimax_bs_params
		args['my_function'] = 'extract_wimax_util_data'
		args['provis_bw'] = 4
		args['war']  = 80 
		args['crit']  = 90
		args['memc']  = call_kpi_services.memc_cnx('pub_slave_1')
		#warning('memc: {0}'.format(args['memc']))
		args['service'] = wimax_util_kpi_services[0]
		rds_cli = RedisInterface()
		args['redis'] = rds_cli
		extract_kpi_services_data.s(**args).apply_async()
	
		rds_cli = RedisInterface()
		args['redis'] = rds_cli
		args['service'] = wimax_util_kpi_services[1]
		extract_kpi_services_data.s(**args).apply_async()
	
		rds_cli = RedisInterface()
		args['redis'] = rds_cli
		args['provis_bw'] = 2
		args['service'] = wimax_util_kpi_services[2]
		extract_kpi_services_data.s(**args).apply_async()
	
		rds_cli = RedisInterface()
		args['redis'] = rds_cli
		args['service'] = wimax_util_kpi_services[3]
		extract_kpi_services_data.s(**args).apply_async()

		rds_cli = RedisInterface()
		args['redis'] = rds_cli
		args['war'] = 20
		args['crit'] = 40
		args['service'] = wimax_util_kpi_services[4]
		extract_wimax_ul_issue_data.s(**args).apply_async()
		
	for i in izip_longest(*[iter(wimax_ss_key)] * 500):
		args = {}	
		[p.lrange(k, 0, -1) for k  in i]
		wimax_ss_params = p.execute()
		
		
		args['host_info'] = wimax_ss_params
		rds_cli = RedisInterface()
		args['redis'] = rds_cli
		args['service'] = wimax_util_kpi_services[5]
		args['my_function'] = 'extract_wimax_ss_provis_data' 
		extract_kpi_services_data.s(**args).apply_async()


		# Cambium services
	
	for i in izip_longest(*[iter(pmp_bs_key)] * 500):	
		args = {}	
		[p.lrange(k, 0 ,-1) for k  in i]
		cambium_bs_params = p.execute()
	
		args['host_info'] = cambium_bs_params
		args['my_function'] = 'extract_cambium_util_data' 
		args['memc']  = call_kpi_services.memc_cnx('pub_slave_1')

		args['provis_bw'] = 4.76
		args['war']  = 80 
		args['crit']  = 90
		rds_cli = RedisInterface()
		args['redis'] = rds_cli
		args['service'] = cambium_util_kpi_services[0]
		extract_kpi_services_data.s(**args).apply_async()
	
		rds_cli = RedisInterface()
		args['redis'] = rds_cli
		args['provis_bw'] = 2.24
		args['service'] = cambium_util_kpi_services[1]
		extract_kpi_services_data.s(**args).apply_async()

		rds_cli = RedisInterface()
		args['redis'] = rds_cli
		args['war']  = 20 
		args['crit']  = 40
		args['service'] = cambium_util_kpi_services[2]
		extract_cambium_ul_issue_data.s(**args).apply_async()	
		
	for i in izip_longest(*[iter(pmp_ss_key)] * 500):	
		args = {}	
		[p.lrange(k, 0 ,-1) for k  in i]
		cambium_ss_params = p.execute()

		rds_cli = RedisInterface()
		args['redis'] = rds_cli
		args['host_info'] = cambium_ss_params
		args['service'] = cambium_util_kpi_services[3]
		args['my_function'] = 'extract_cambium_ss_provis_data' 
		extract_kpi_services_data.s(**args).apply_async()	
		

@app.task(base=DatabaseTask, name='extract_cambium_ss_provis_data')		
def extract_cambium_ss_provis_data(host_params,**args):
	perf = ''
	state_string = 'unknown'
	service_list= []
	for entry in host_params:
		ul_rssi = dl_rssi = ul_jitter = dl_jitter = rereg_count = None
		perf = ''
		state_string = 'unknown'
		if entry:
			host ,site,ip = literal_eval(entry[0])
		else:
			break
		try:
			ul_rssi = args['redis'].redis_cnx.get("provis:%s:%s" % (host,'cambium_ul_rssi'))
			if ul_rssi:
				ul_rssi = eval(ul_rssi)
		except:
			ul_rssi = None
		try:
			dl_rssi = args['redis'].redis_cnx.get("provis:%s:%s" % (host,'cambium_dl_rssi'))
			if dl_rssi:
				dl_rssi = eval(dl_rssi)
		except:
			dl_rssi = None
		try:
			dl_jitter = args['redis'].redis_cnx.get("provis:%s:%s" % (host,'cambium_dl_jitter'))
			if dl_jitter:
				dl_jitter = eval(dl_jitter)
		except:
			dl_jitter = None
		try:
			ul_jitter = args['redis'].redis_cnx.get("provis:%s:%s" % (host,'cambium_ul_jitter'))
			if ul_jitter:
				ul_jitter = eval(ul_jitter)
		except:
			ul_jitter = None
		try:
			rereg_count = args['redis'].redis_cnx.get("provis:%s:%s" % (host,'cambium_rereg_count'))
			if rereg_count:
				rereg_count = eval(rereg_count)
		except:
			rereg_count = None
		try:
			if ul_rssi and dl_rssi and (int(ul_rssi) < -82 or int(dl_rssi) < -82):
				ss_state = "los"
				state = 0
				state_string= "ok"
			elif dl_jitter and ul_jitter and ( int(ul_jitter) > 7 or int(dl_jitter) > 7):
				ss_state = "jitter"
				state = 0
				state_string= "ok"
			elif rereg_count and (int (rereg_count) > 100):
				ss_state = "rereg"
				state = 0
				state_string = "ok"
			else:
				ss_state = "normal" 
				state_string= "ok"
				state = 0
		
    			perf = ''.join( 'ss_state' + "=%s;;;" % (ss_state))
		except Exception ,e:
			perf = ''
    		service_dict = service_dict_for_kpi_services(perf,state_string,host,site,ip,**args)
		service_list.append(service_dict)

    	if len(service_list) > 0: 	
    		build_export.s(args['site_name'], service_list).apply_async()


@app.task(base=DatabaseTask, name='extract_wimax_ss_provis_data')		
def extract_wimax_ss_provis_data(host_params,**args):
	service_state_out = []
	service_list = []
	for entry in host_params:
		perf = ''
		ul_rssi = dl_rssi = ss_ptx = dl_cinr = None
		state_string = 'unknown'
		if entry:
			host,site,ip  =literal_eval(entry[0])
		else:
			break
		try:
			ul_rssi = args['redis'].redis_cnx.get("provis:%s:%s" % (host,'wimax_ul_rssi'))
			if ul_rssi:
				ul_rssi = eval(ul_rssi)
		except:
			ul_rssi = None
		try:
			dl_rssi = args['redis'].redis_cnx.get("provis:%s:%s" % (host,'wimax_dl_rssi'))
			if dl_rssi:
				dl_rssi = eval(dl_rssi)
		except:
			dl_rssi = None
		try:
			dl_cinr = args['redis'].redis_cnx.get("provis:%s:%s" % (host,'wimax_dl_cinr'))
			if dl_cinr:
				dl_cinr = eval(dl_cinr)
		except:
			dl_cinr = None	
		try:
			ss_ptx = args['redis'].redis_cnx.get("provis:%s:%s" % (host,'wimax_ss_ptx_invent'))
			if ss_ptx:
				ss_ptx = eval(ss_ptx)
		except:
			ss_ptx = None
		try:
		
			if ul_rssi and dl_rssi and ss_ptx and (int(ul_rssi) < -83 or int(dl_rssi) < -83 and int(ss_ptx) > 20):
				ss_state = "los"
				state = 0
				state_string= "ok"
			elif ul_rssi and dl_rssi and ss_ptx and (int(ul_rssi) < -83 or int(dl_rssi) < -83 and int (ss_ptx) <= 20):
				ss_state = "need_alignment"
				state = 0
				state_string= "ok"
			elif dl_cinr and int(dl_cinr) <= 15:
				ss_state = "rogue_ss"
				state = 0
				state_string = "ok"
			else:
				ss_state = "normal" 
				state_string= "ok"
				state = 0
			perf = ''.join( 'ss_state' + "=%s;;;" % (ss_state))
		except Exception ,e:
			perf = ''
		#warning('ss_provis: {0}'.format(perf))
    		service_dict = service_dict_for_kpi_services(perf,state_string,host,site,ip,**args)
		service_list.append(service_dict)		
    	if len(service_list) > 0: 	
    		build_export.s(args['site_name'], service_list).apply_async()


@app.task(base=DatabaseTask, name='extract_kpi_services_data')		
def extract_kpi_services_data(**args):
    host_info = args['host_info']
    my_function  = args['my_function']
    service_list = []
    fun = eval(my_function)
    args['site_name'] = 'pub_slave_1'
    #for host_name,site,ip_address in host_info:
    fun(host_info,**args)
		
    #if len(service_list) > 0: 	
    #	build_export.s(site, service_list).apply_async()



@app.task(base=DatabaseTask, name ='extract_cambium_bs_ul_data')
def extract_cambium_bs_ul_data(ul_issue_list,host_name,site,ip,sect_id,**args):
	count = 0
	perf = ''
	sec_ul_issue = ''
	state_string = 'uknown'
	#warning('cambium ss entry: {0}'.format(ul_issue_list))
        rds_cli = RedisInterface()
	for service_dict in ul_issue_list:
		try:
			value = int(service_dict['perf_data'].split('=')[1])
		except:
			continue
		count = count +value

	if len(ul_issue_list):	
		sec_ul_issue = count/float(len(ul_issue_list)) * 100
	try:	
		if sec_ul_issue != '':
			sec_ul_issue = "%.2f" % sec_ul_issue
			if float(sec_ul_issue) < args['war']:
				state = 0
				state_string = "ok"
			elif float(sec_ul_issue) >= args['crit']:
				state = 2
				state_string = "critical"
			else:
				state = 1
				state_string = "warning"
		perf = ''.join('bs_ul_issue' + "=%s;%s;%s;%s" %(sec_ul_issue,args['war'],args['crit'],sect_id))
	except:
		perf = 'bs_ul_issue'+'=;%s;%s;%s' % (args['war'],args['crit'],sect_id)
		
	args['service'] = 'cambium_bs_ul_issue_kpi'
    	bs_service_dict = service_dict_for_kpi_services(perf,state_string,host_name,site,ip,**args)
	bs_service_dict['refer'] =sect_id
	ul_issue_list.append(bs_service_dict)		
	#warning('cambium bs entry: {0}'.format(ul_issue_list))
	rds_cli.redis_cnx.rpush('queue:ul_issue',*ul_issue_list)


		
@app.task(base=DatabaseTask, name='extract_wimax_ul_issue_data')		
def extract_wimax_ul_issue_data(**args):
    host_info = args['host_info']
    pmp1_service_list = []
    pmp2_service_list = []
    pmp1_ss_info = []
    pmp2_ss_info = []
    site_name = 'pub_slave_1'
    rds_cli = RedisInterface(custom_conf={'db': INVENTORY_DB})
    p = rds_cli.redis_cnx.pipeline()
    args['memc']  = ''
    redis_conn =args['redis']
    args['redis'] = ''
    memc_conn  = extract_wimax_ul_issue_data.memc_cnx('pub_slave_1')
    for entry in host_info:
	if entry:
		if len(literal_eval(entry[0])) == 3:
			host_name,site_name,ip_address  = literal_eval(entry[0])
			dr_slave = None
		elif len(literal_eval(entry[0])) == 4:
			host_name,site_name,ip_address,dr_slave = literal_eval(entry[0])
	else:
		break
	pmp1_sect_id,pmp2_sect_id = extract_wimax_bs_sec_id(host_name,memc_conn)			 
	#warning('pmp1 sec {0} pmp2 sec:{1}'.format(pmp1_sect_id,pmp2_sect_id))
        pmp1_conn_ss_ip,pmp2_conn_ss_ip = extract_wimax_connected_ss(host_name,dr_slave,memc_conn)
	#warning('pmp1 ss ip {0},pmp2 ss ip {1}'.format(pmp1_conn_ss_ip,pmp2_conn_ss_ip))
	#pmp2_ss_key = rds_cli.redis_cnx.keys(pattern="wimax:ss:*:10.191.79.34")
	#[p.lrange(k, 0 , -1) for k  in pmp2_ss_key]
	#pmp2_ss_info = p.execute()
	#pmp2_ss_info = args['redis'].redis_cnx.get('wimax:ss:*:10.191.79.34')
	#pmp2_ss_info = map(lambda x: args['redis'].get('wimax:ss:*:%s' % x) ,pmp2_conn_ss_ip)
	#pmp1_ss_info = map(lambda x: args['redis'].get('wimax:ss:*:%s' % x) ,pmp1_conn_ss_ip)
	#pmp2_ss_info = map(lambda x: args['redis'].get('wimax:ss:*:%s' % x) ,pmp2_conn_ss_ip)
	pmp2_ss_key = map(lambda x: rds_cli.redis_cnx.keys(pattern="wimax:ss:*:%s" %x) ,pmp2_conn_ss_ip)
	pmp1_ss_key = map(lambda x: rds_cli.redis_cnx.keys(pattern="wimax:ss:*:%s" %x)  ,pmp1_conn_ss_ip)

	#warning('pmp1 ss key {0},pmp2 ss key {1}'.format(pmp1_ss_key,pmp2_ss_key))
	[p.lrange(k[0], 0 , -1) for k  in pmp2_ss_key if k]
	pmp2_ss_info = p.execute()
	[p.lrange(k[0], 0 , -1) for k  in pmp1_ss_key if k]
	pmp1_ss_info = p.execute()
	#warning('pmp2 ss info: {0}, pmp1 ss info {1}'.format(pmp2_ss_info,pmp1_ss_info))
	#try:
	#	pmp1_ss_info = literal_eval(pmp1_ss_info)	
	#	pmp2_ss_info = literal_eval(pmp2_ss_info)	
	#except:
	#	pass
    	#chord(extract_ss_ul_issue_data(entry,**args) for entry in pmp1_ss_info if entry ) \
	#	(extract_wimax_bs_ul_data(host_name,site_name,ip_address,pmp1_sect_id ,'pmp1',pmp1_service_list,**args))
    	extract_ss_ul_issue_data.s(pmp2_ss_info,host_name,site_name,ip_address,pmp2_sect_id,'pmp2',redis_conn,**args).apply_async()
    	extract_ss_ul_issue_data.s(pmp1_ss_info,host_name,site_name,ip_address,pmp1_sect_id,'pmp1',redis_conn,**args).apply_async()
    #warning('pmp2 service list: {0}'.format(pmp2_service_list))


@app.task(base=DatabaseTask, name='extract_cambium_ul_issue_data')		
def extract_cambium_ul_issue_data(**args):
    host_info = args['host_info']
    service_list = []
    ss_info = []
    rds_cli = RedisInterface(custom_conf={'db': INVENTORY_DB})
    p = rds_cli.redis_cnx.pipeline()
    memc_conn  = extract_cambium_ul_issue_data.memc_cnx('pub_slave_1')
    args['memc'] = ''
    redis_conn =args['redis']
    args['redis'] = ''
    for entry in host_info:
	if entry:
		if len(literal_eval(entry[0])) == 3:
			host_name,site_name,ip_address  = literal_eval(entry[0])
	else:
		break
	sect_id = extract_cambium_bs_sec_id(host_name,memc_conn)			 
	#warning('cambium sec {0} '.format(sect_id))
        conn_ss_ip = extract_cambium_connected_ss(host_name,memc_conn)
	#warning('cambium conn_ss {0} '.format(conn_ss_ip))
	#ss_key = rds_cli.redis_cnx.keys(pattern="pmp:ss:*:10.172.26.18")
	if conn_ss_ip:
		ss_key = map(lambda x: rds_cli.redis_cnx.keys(pattern="pmp:ss:*:%s" %x) ,conn_ss_ip)
		[p.lrange(k[0], 0 , -1) for k  in ss_key if k] 
		ss_info = p.execute()

		extract_ss_ul_issue_data.s(ss_info,host_name,site_name,ip_address,
				sect_id,None,redis_conn,**args).apply_async()
