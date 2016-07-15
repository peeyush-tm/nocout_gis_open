#!/usr/bin/python

"""
Poller script which runs on ss and calculates 
the ul utilization of the ss connected from BS.

Poller script determines the uplink utilization of the ss.
poller script takes the snmp value of 
OID .1.3.6.1.4.1.161.19.3.1.4.1.21 from snmp agent of device at specific interval.
uplink utilization information is /sent to device application 
"""

from ast import literal_eval
from ConfigParser import ConfigParser
from datetime import datetime,timedelta
from itertools import izip_longest
import memcache
import os
import pymongo
import sys
import socket
import time

from celery import chord,group

#from sys import path
#path.append('/omd/nocout_etl')

#from start_pub import app
from start.start import app
from handlers.db_ops import *
from service.service_etl import *
#from service_etl import *

logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error

INVENTORY_DB = getattr(app.conf, 'INVENTORY_DB', 3)


@app.task(name='get-ul-issue-service-checks', ignore_result=True)
def get_ul_issue_service_checks_output(**opt):
	# get check results from redis backed queue
	# pulling 2000 values from queue, at a time
	#DB_CONF = getattr(app.conf, 'CNX_FROM_CONF', None)
	#conf = ConfigParser()
	#conf.read(DB_CONF)
	site_name = opt.get('site_name')
	queue = RedisInterface(perf_q='queue:ul_issue:%s' % site_name)
	check_results = queue.get(0, -1)
	warning('ul_issue Queue len: {0}'.format(len(check_results)))
	if check_results:
		build_export.s(site_name, check_results).apply_async()


def extract_cambium_connected_ss(hostname,memc_conn):
    ss_connected = []
    try:
        if memc_conn:
            ss_connected = memc_conn.get("%s_conn_ss" % str(hostname))
    except Exception,e:
        warning('cambium connected ss: {0}'.format(e))
        pass
    return ss_connected

def fetch_cisco_util_from_memc(hostname,site,util_type,memc):
	try:
		key1 = str(hostname) + "switch_%s_utilization" % util_type
		dict2 = memc.get(key1)
		mro_dl_dict=dict(dict2)
	except Exception ,e:
		mro_dl_dict = {}
	#print mro_dl_dict
        return mro_dl_dict

def fetch_juni_util_from_memc(hostname,site,util_type,memc):
	try:
		key1 = str(hostname)+"juniper_switch_%s_utilization" % util_type
		dict2 = memc.get(key1)
		mro_dl_dict=dict(dict2)
	except Exception ,e:
		mro_dl_dict = {}
        return mro_dl_dict
def extract_juniper_util_data(host_params,**args):
    service_list = []
    for entry in host_params:
	crit_flag = warn_flag = normal_flag = 0
	kpi = perf = ''
    	dict1_kpi = []
    	kpi_list_index = []
        state_string = "unknown"
        if entry and len(eval(entry[0])) == 4:
            hostname, site, ip_address,qos_value = eval(entry[0])
        else:
            break
	try:
    		kpi_list_index = [i for i,x in enumerate(qos_value) if int(x) >0]
	except:
		continue
	if 'dl_util' in args['service']:
		util_type = 'dl'
	if 'ul_util' in args['service']:
		util_type = 'ul'
	try:
		dl_util_dict= fetch_juni_util_from_memc(hostname,site,util_type,args['memc'])
		for entry in dl_util_dict.keys():
			each, inc , index = entry.split("_") #['ge-0', '1', '12'],['ge-0', '0', '12']
			index =int(index)	
			if inc == '1':
				index = index+48
			if index in kpi_list_index:
				kpi =  dl_util_dict[entry]
				try:
					kpi = (float(kpi)/float(qos_value[index])) *100
					entry = entry+"_kpi"
					war = float(args['war'])
					crit = float(args['crit'])
					kpi = round(kpi,2)
					#tup1 = (entry,kpi, index )
					#dict1_kpi.append(tup1)
				except Exception,e:
					continue
			#kpi = round(kpi,2)
			if kpi or kpi == 0:
				perf += str(entry) + "=%s;%s;%s;%s " % (kpi,war,crit,qos_value[index])
				if kpi >= crit:
					crit_flag = 1
				elif kpi >= war and kpi < crit:
					warn_flag = 1
				else:
					normal_flag = 1
			if crit_flag:
				state =2
				state_string = "critical"
			elif warn_flag:
				state =1
				state_string = "warning"
			elif normal_flag:
				state = 0
				state_string = "ok"
			
	except Exception ,e:
	    perf = ''	
	    error('Juniper excetiom*****: {0}'.format(e)) 
    	age_of_state = age_since_last_state(hostname, args['service'], state_string)
	
	service_dict = service_dict_for_kpi_services(
	    perf, state_string, hostname, site, ip_address, age_of_state, **args)
	service_list.append(service_dict)
    if len(service_list) > 0:     
	build_export.s(args['site_name'], service_list).apply_async()
	
def fetch_huawei_util_from_memc(hostname,site,util_type,memc):
        try:
                key1 = str(hostname)+"switch_%s_utilization" % util_type
                dict2 = memc.get(key1)
                mro_dl_dict=dict(dict2)
        except Exception ,e:
                mro_dl_dict = {}
        return mro_dl_dict

def extract_huawei_util_data(host_params,**args):
    service_list = []
    for entry in host_params:
        crit_flag = warn_flag = normal_flag = 0
        kpi = perf = ''
        dict1_kpi = []
        kpi_list_index = []
        state_string = "unknown"
        if entry and len(eval(entry[0])) == 4:
            hostname, site, ip_address,qos_value = eval(entry[0])
        else:
            break
        try:
                kpi_list = [x for i,x in enumerate(qos_value) if int(x) >0]
        except:
                continue
        if 'dl_util' in args['service']:
                util_type = 'dl'
        if 'ul_util' in args['service']:
                util_type = 'ul'
        try:
                ul_util_dict= fetch_huawei_util_from_memc(hostname,site,util_type,args['memc'])
		#error('huawei dictionary: {0}'.format(ul_util_dict))
                if len(ul_util_dict) >1:   # if 2 port are there 
                    if len(kpi_list)==1: # but capacity only one given 
                          kpi_list.append(kpi_list[0])  # add one more value
                for x in xrange(len(ul_util_dict)):
                    entry = ul_util_dict.keys()[x]  #entry = Gi0/1
                    kpi =  ul_util_dict[entry] # kpi = utilization like 7.4
                    try:
                        kpi = (float(kpi)/float(kpi_list[x])) *100
                        entry = entry+"_kpi"
			war = float(args['war'])
			crit = float(args['crit'])
                    except Exception,e:
                        #error('huawei eerr$: {0}'.format(e))
                        continue  
                    ul_kpi = kpi
                    ul_kpi = round(ul_kpi,2)
                    if ul_kpi or ul_kpi ==0:
                    	perf += str(entry) + "=%s;%s;%s;%s " % (ul_kpi,war,crit,kpi_list[x])
                   	if ul_kpi >= crit:
                        	crit_flag = 1
                    	elif ul_kpi >= war and ul_kpi < crit:
                        	warn_flag = 1
                    	else:
                        	normal_flag = 1
                	if crit_flag:
                    		state =2
                    		state_string = "critical"
                	elif warn_flag:
                    		state =1
                    		state_string = "warning"
                	elif normal_flag:
                    		state = 0
                    		state_string = "ok"

        except Exception ,e:
            perf = ''
        age_of_state = age_since_last_state(hostname, args['service'], state_string)

        service_dict = service_dict_for_kpi_services(
            perf, state_string, hostname, site, ip_address, age_of_state, **args)
        service_list.append(service_dict)
    if len(service_list) > 0:
        build_export.s(args['site_name'], service_list).apply_async()

	
def extract_cisco_util_data(host_params,**args):
    service_list = []
    for entry in host_params:
	crit_flag = warn_flag = normal_flag = 0
	kpi = perf = ''
        kpi_list_index = []
        dict1_kpi = []
        state_string = "unknown"
        if entry and len(eval(entry[0])) == 4:
            hostname, site, ip_address,qos_value = eval(entry[0])
        else:
            break
        try:
    		kpi_list_index = [i+1 for i,x in enumerate(qos_value) if int(x) >0]
	except Exception,e:
		continue
	if 'dl_util' in args['service']:
		util_type = 'dl'
	if 'ul_util' in args['service']:
		util_type = 'ul'
	try:
		dl_util_dict= fetch_cisco_util_from_memc(hostname,site,util_type,args['memc'])
		for entry in dl_util_dict.keys():
			each, index = entry.split("_")	
			index = int(index)
			if each == "gi0":
				index = index+24
			if index in kpi_list_index:
				kpi =  dl_util_dict[entry]
				try:
					kpi = (float(kpi)/float(qos_value[index-1])) *100
					entry = entry+"_kpi"
					war = float(args['war'])
		                        crit = float(args['crit'])

					#tup1 = (entry,kpi, index )
					#dict1_kpi.append(tup1)
					#max_tuple = max(dict1_kpi, key = lambda x:x[1])
					#print "max ", max_tuple
				except Exception,e:
					continue
			kpi = round(kpi,2)
			if kpi or kpi ==0:
				perf += str(entry) + "=%s;%s;%s;%s " % (kpi,war,crit,qos_value[index-1])
				if kpi >= crit:
					crit_flag = 1
				elif kpi >= war and kpi < crit:
					warn_flag = 1
				else:
					normal_flag = 1
			if crit_flag:
				state =2
				state_string = "critical"
			elif warn_flag:
				state =1
				state_string = "warning"
			elif normal_flag:
				state = 0
				state_string = "ok"
			
	except Exception ,e:
		warning('cisco: {0}'.format(e))
		perf = ''
    	age_of_state = age_since_last_state(hostname, args['service'], state_string)
	
	service_dict = service_dict_for_kpi_services(
	    perf, state_string, hostname, site, ip_address, age_of_state, **args)
	service_list.append(service_dict)
    if len(service_list) > 0:     
	build_export.s(args['site_name'], service_list).apply_async()

def extract_wimax_connected_ss(hostname,dr_slave,memc_conn):
    dr_pmp1_conn_ss_ip = dr_pmp2_conn_ss_ip = []
    pmp1_conn_ss_ip = pmp2_conn_ss_ip = []
    try:
        ss_connected_list = memc_conn.get("%s_conn_ss" % str(hostname))
	#ss_connected_list = eval(ss_connected_list)
        #pmp1_ss_connected = args['memc'].get("pmp1_%s" % hostname)
        #pmp2_ss_connected = args['memc'].get("pmp2_%s" % hostname)
        #warning('wimax connected ss: {0} {1}'.format(ss_connected_list,memc_conn))
        try:
            if ss_connected_list: 
                pmp1_conn_ss_ip=ss_connected_list.get(1)
                pmp2_conn_ss_ip=ss_connected_list.get(2)
        except:
            pass
        if dr_slave:
            dr_ss_connected_list = memc_conn.get("%s_conn_ss" % str(hostname))
	    #dr_ss_connected_list = eval(dr_ss_connected_list)
            #dr_pmp1_ss_connected = args['memc'].get("pmp1_%s" % dr_slave)
            #dr_pmp2_ss_connected = args['memc'].get("pmp2_%s" % dr_slave)
            if dr_ss_connected_list:
                dr_pmp1_conn_ss_ip=dr_ss_connected_list.get(1)
                dr_pmp2_conn_ss_ip=dr_ss_connected_list.get(2)
    except Exception,e:
        warning('wimax connected ss: {0}'.format(e))
        pass
    if len(dr_pmp1_conn_ss_ip) > 0 or len(dr_pmp2_conn_ss_ip) > 0:
        return dr_pmp1_conn_ss_ip,dr_pmp2_conn_ss_ip
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


@app.task(base=DatabaseTask, name ='extract_wimax_bs_ul_issue_data')
def extract_wimax_bs_ul_issue_data(wimax_bs_ul_issue_data,**args):
    count = 0
    perf = ''
    sec_ul_issue = ''
    state_string = 'unknown'
    #warning('wimax ss entry: {0}'.format(ul_issue_list))
    rds_cli = RedisInterface()
    redis_cnx = rds_cli.redis_cnx
    bs_service_dict_list = []
    for (ul_issue_list, host_name, site, ip, sect_id, sec_type) in wimax_bs_ul_issue_data :
            perf = ''
            sec_ul_issue = ''
    	    state_string = 'unknown'
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
		    if sec_ul_issue > 100:
			sec_ul_issue = 100
		if sec_ul_issue not in ['',None]:
		    sec_ul_issue = "%.2f" % sec_ul_issue
		    if float(sec_ul_issue) < float(args['war']):
			state = 0
			state_string = "ok"
		    elif float(sec_ul_issue) >= float(args['crit']):
			state = 2
			state_string = "critical"
		    else:
			state = 1
			state_string = "warning"
		
		perf = ''.join('%s_ul_issue' % sec_type + "=%s;%s;%s;%s" %(sec_ul_issue,args['war'],args['crit'],sect_id))
	    except Exception,e:
		error('wimax bs entry: {0} {1} {2} {3} {4}'.format(e,sec_ul_issue,perf,args['war'],args['crit']))
		perf = ''
	    args['service'] = 'wimax_bs_ul_issue_kpi'
	    age_of_state = age_since_last_state(host_name, args['service'], state_string)
	    bs_service_dict = service_dict_for_kpi_services(
		    perf,
		    state_string,
		    host_name,
		    site,
		    ip,
		    age_of_state,
		    **args)
	    bs_service_dict['refer'] =sect_id
	    ul_issue_list.append(bs_service_dict)        
	    #warning('wimax bs ul issue: {0}'.format(len(ul_issue_list)))
	    redis_cnx.rpush('queue:ul_issue:%s' % site,*ul_issue_list)
	    #bs_service_dict_list.append((bs_service_dict, site))
    #insert_bs_ul_issue_data_to_redis(bs_service_dict)

def insert_bs_ul_issue_data_to_redis(bs_service_dict_list):
    try :
	#print "BS Dict Here",bs_service_dict
	#bs_service_dict = self.bs_service_dict
        rds_cli = RedisInterface()
        #print "BS UL issue record state : %s \n" %str(bs_service_dict['state'])
        for (bs_service_dict,site) in bs_service_dict_list :
	    machine_name = site.split('_')[0]
	    if bs_service_dict['state'] in ['ok','warning','critical'] :
	        rds_cli.redis_cnx.rpush('q:bs_ul_issue_event:%s' % machine_name, bs_service_dict)
                #print "BS UL issue record inserted in Redis : ",rds_cli.redis_cnx.lrange('q:bs_ul_issue_event',0, -1),"\n"
    except Exception ,exp :
        print "Error in Redis DB Data Insertion UL Issue : %s \n" % str(exp)

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
                if cam_util != None and isinstance(cam_util,basestring):
                    cam_util = literal_eval(cam_util)
        except Exception,e:
                warning('memc: {0} {1}'.format(e,"extract_cambium_util_data"))
                #warning('args: {0}'.format(args))
                sec_id = ''
        try:
            if cam_util != None:
                cam_util = (float(cam_util)/float(args['provis_bw'] )) * 100
                cam_util = round(cam_util,2)
                if cam_util < float(args['war']):
                    state = 0
                    state_string = "ok"
                elif cam_util >= float(args['crit']):
                    state = 2
                    state_string = "critical"
                else:
                    state = 1
                    state_string = "warning"
            perf = 'cam_%s_util_kpi' % util_type + "=%s;%s;%s;%s" %(cam_util,args['war'],args['crit'],sec_id)
        except Exception,e:
            warning('cam ss util: {0}'.format(e))
            perf = 'cam_%s_util_kpi' % util_type + "=;%s;%s;%s" %(args['war'],args['crit'],sec_id)

    	# calculate age since last state change
    	age_of_state = age_since_last_state(hostname, args['service'], state_string)

    	service_dict = service_dict_for_kpi_services(
            perf, state_string, hostname, site, ip_address, age_of_state, **args)
    	service_dict['refer'] = sec_id
    	service_list.append(service_dict)

    	cam_util = ''
    	sec_id = ''
    	perf = ''
    	state_string = "unknown"
    #error('cambium util data : {0}'.format(len(service_list)))
    if len(service_list) > 0:     
        build_export.s(args['site_name'], service_list).apply_async()
    return None

def extract_radwin_util_data(host_params,**args):
    perf = rad_util = sec_id = plugin_message = ''
    state = 3
    state_string = "unknown"
    service_list = []
    #warning('host_params: {0}'.format(host_params))
    util_type = args['service'].split('_')[1]
    for entry in host_params:
        if entry and len(eval(entry[0])) == 6 :
            hostname,site,ip_address,d_type,d_tech,bw = eval(entry[0])
        else:
            break
        try:
                if args['memc']:
                    #sec_id = args['memc'].get(str(hostname) + "_sec_id")
                    rad_util = args['memc'].get(str(hostname) + "_" + util_type)
                    #warning('radwin util: {0}'.format(rad_util))
                    if rad_util != None and isinstance(rad_util,basestring):
                        rad_util = literal_eval(rad_util)
        except Exception,e:
                warning('memc: {0} {1} {2} {3}'.format(e,rad_util,hostname,args['service']))
                #warning('args: {0}'.format(args))
                sec_id = ''
        try:
                if rad_util != None and bw != None:
                    rad_util = (float(rad_util)/float(bw/1024.0)) * 100
                    rad_util = round(rad_util,2)
                    if rad_util < float(args['war']):
                        state = 0
                        state_string = "ok"
                    elif rad_util >= float(args['crit']):
                        state = 2
                        state_string = "critical"
                    else:
                        state = 1
                        state_string = "warning"
                perf = 'rad_%s_util_kpi' % util_type + "=%s;%s;%s;%s" %(rad_util,args['war'],args['crit'],sec_id)
        except Exception,e:
                #warning('cam ss util: {0}'.format(e))
                perf = 'rad_%s_util_kpi' % util_type + "=;%s;%s;%s" %(args['war'],args['crit'],sec_id)

    	# calculate age since last state change
    	age_of_state = age_since_last_state(hostname, args['service'], state_string)

    	service_dict = service_dict_for_kpi_services(
            perf, state_string, hostname, site, ip_address, age_of_state, **args)
    	service_dict['refer'] = sec_id
    	service_list.append(service_dict)

    	rad_util = ''
    	sec_id = ''
    	perf = ''
    	state_string = "unknown"
    if len(service_list) > 0:     
        build_export.s(args['site_name'], service_list).apply_async()
    return None

def extract_mrotek_util_data(host_params,**args):
    perf = mrotek_util = sec_id = plugin_message = ''
    state = 3
    state_string = "unknown"
    service_list = []
    #warning('host_params: {0}'.format(host_params))
    util_type = args['service'].split('_')[1]
    for entry in host_params:
        if entry and len(eval(entry[0])) == 4 :
            hostname,site,ip_address,capacity = eval(entry[0])
        else:
            break
        try:
                if args['memc']:
                    #sec_id = args['memc'].get(str(hostname) + "_sec_id")
                    #mrotek_util = args['memc'].get(str(hostname) + "_" + util_type)
                    #warning('radwin util: {0}'.format(rad_util))
                    util_values =  args['memc'].get(str(hostname) + "_" + util_type) # got values like '0.7,9'
                    util_list = util_values.split(",")
                    try :
                        mrotek_util = float(util_list[0])
                        index1 = util_list[1]
                        data_s = "fe_"+str(index1)+"_kpi"
                    except Exception as e:
                        error('Mrotek conversion: {0}'.format(e))

                if mrotek_util != None and isinstance(mrotek_util,basestring):
                    mrotek_util = literal_eval(mrotek_util)
        except Exception,e:
                warning('memc: {0}'.format(e))
                #warning('args: {0}'.format(args))
                sec_id = ''
        try:
                if mrotek_util != None and capacity[int(index1)-1]:
                    mrotek_util = (float(mrotek_util)/float(capacity[int(index1)-1])) * 100
                    mrotek_util = round(mrotek_util,2)
                    if mrotek_util < float(args['war']):
                       state = 0
                       state_string = "ok"
                    elif mrotek_util >= float(args['crit']):
                       state = 2
                       state_string = "critical"
                    else:
                       state = 1
                       state_string = "warning"
                    perf = data_s + "=%s;%s;%s" %(mrotek_util,args['war'],args['crit'])
        except Exception,e:
                #warning('cam ss util: {0}'.format(e))
                perf = "fe_1_kpi" + "=;%s;%s" %(args['war'],args['crit'])

    	# calculate age since last state change
    	age_of_state = age_since_last_state(hostname, args['service'], state_string)

    	service_dict = service_dict_for_kpi_services(
            perf, state_string, hostname, site, ip_address, age_of_state, **args)
    	service_dict['refer'] = sec_id
    	service_list.append(service_dict)

    	mrotek_util = ''
    	sec_id = ''
    	perf = ''
    	state_string = "unknown"
    if len(service_list) > 0:     
        build_export.s(args['site_name'], service_list).apply_async()
    return None


def extract_rici_util_data(host_params,**args):
    perf = rici_util = sec_id = plugin_message = ''
    crit_flag = warn_flag = normal_flag = None
    state = 3
    state_string = "unknown"
    service_list = []
    #warning('host_params: {0}'.format(host_params))
    util_type = args['service'].split('_')[1]
    for entry in host_params:
        if entry and len(eval(entry[0])) == 4 :
            hostname,site,ip_address,capacity = eval(entry[0])
        else:
            break
	try:
		if args['memc']:
                    #sec_id = args['memc'].get(str(hostname) + "_sec_id")
                    rici_util = args['memc'].get(str(hostname) + "_" + util_type)
                    #warning('radwin util: {0}'.format(rad_util))
                if rici_util != None and isinstance(rici_util,basestring):
                    rici_util = literal_eval(rici_util)
	except Exception,e:
                warning('memc: {0}'.format(e))
                #warning('args: {0}'.format(args))
                sec_id = ''
	try:
	    if rici_util != None:
                for index,entry in enumerate(rici_util):
                    rici_kpi =  entry[1]
                    try:
                        index1 = int(entry[0].split('_')[1])
                        if rici_kpi != None and capacity[index1-1]:
                            rici_kpi = (float(rici_kpi)/float(capacity[index1-1])) *100
                            rici_kpi  = round(rici_kpi,2)
                    except Exception,e:
                        perf += str(entry[0]) + '_kpi' + "=;%s;%s;%s " % (args['war'],args['crit'],capacity[index1-1])
                	warning('Rici kpi error: {0}'.format(e))
                        continue
                    if rici_kpi != None:
                        perf += str(entry[0]) + '_kpi'+ "=%s;%s;%s;%s " % (rici_kpi,args['war'],args['crit'],capacity[index1-1])
                        if rici_kpi >= args['crit']:
                            crit_flag = 1
                        elif rici_kpi >= args['war'] and rici_kpi < args['crit']:
                            warn_flag = 1
                        else:
                            normal_flag = 1
                if crit_flag:
                    state =2
                    state_string = "critical"
                elif warn_flag:
                    state =1
                    state_string = "warning"
                elif normal_flag:
                    state = 0
                    state_string = "ok"
		perf = perf.strip()
	except Exception,e:
                warning('Rici utilization Error: {0}'.format(e))

    	# calculate age since last state change
    	age_of_state = age_since_last_state(hostname, args['service'], state_string)

    	service_dict = service_dict_for_kpi_services(
            perf, state_string, hostname, site, ip_address, age_of_state, **args)
    	service_dict['refer'] = sec_id
    	service_list.append(service_dict)

    	rici_util = ''
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
        total = util = dr_util = sec_bw = dr_slave = None
        state_string = "unknown"
        perf = sec_kpi = sec_id = plugin_message = ''
        if entry  and len(eval(entry[0]))  == 4:
            hostname, site, ip_address, dr_slave = eval(entry[0])
        elif entry and len(eval(entry[0])) == 3:
            hostname, site, ip_address = eval(entry[0])
            dr_slave  = None
        else:
            break

        util_type = args['service'].split('_')[2]
        sec_type = args['service'].split('_')[1]

        service_name = 'wimax_%s_%s_util_bgp' % (sec_type, util_type)
        try:
	    
            #error('Memc connection: {0}'.format(args['memc']))
            if args['memc']:
                sec_id_suffix = "_%s_sec" % sec_type
                util_suffix = "_%s_%s_util" % (sec_type,util_type)
                bw_suffix = "_%s_bw" % sec_type

                sec_id = args['memc'].get(str(hostname) + sec_id_suffix)
                util = args['memc'].get(str(hostname) + util_suffix)
                sec_bw = args['memc'].get(str(hostname) + bw_suffix)
                if sec_bw and isinstance(sec_bw,basestring):
                    sec_bw = literal_eval(sec_bw)
                if util and isinstance(util,basestring):
                    util = literal_eval(util)
                #warning('util: {0} ,{1},{2}'.format(util,hostname,service_name))
                #warning('sec_id: {0}'.format(sec_bw))
                if dr_slave:
                    dr_util = args['memc'].get(str(dr_slave) + util_suffix)
                    if dr_util != None and isinstance(dr_util,basestring):
                        dr_util = literal_eval(dr_util)
        except Exception,e:
            error('Error in memc: {0}'.format(e))
            pass


        try:
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

                if sec_kpi < float(args['war']):
                    state = 0
                    state_string = "ok"
                elif sec_kpi >= float(args['crit']):
                    state = 2
                    state_string = "critical"
                else:
                    state = 1
                    state_string = "warning"
            
            perf += '%s_%s_util_kpi' %(sec_type,util_type) + "=%s;%s;%s;%s" % (sec_kpi,args['war'],args['crit'],sec_id)
        except Exception as e:
            perf = ';%s;%s' % (args['war'],args['crit']) 
            error('Error in wimax util: {0}'.format(e))

    	# calculate age since last state change
    	age_of_state = age_since_last_state(hostname, args['service'], state_string)

	service_dict = service_dict_for_kpi_services(
		perf, state_string, hostname, site, ip_address, age_of_state, **args
	)
	service_dict['refer'] = sec_id
	service_list.append(service_dict)

    if len(service_list) > 0:     
	build_export.s(args['site_name'], service_list).apply_async()

    #warning('wimax util data len: {0}'.format(len(service_list)))
    return None


@app.task(base=DatabaseTask, name='age_since_last_state')
def age_since_last_state(host, service, state):
    """ Calculates the age since when service
    was in the given state
    """

    prefix = 'util:'
    key = prefix + host + ':' + service
    # memc connection to get the state
    #memc = memcache.Client(['10.133.19.165:11211'])
    memc = age_since_last_state.memc_cnx
    out = memc.get(str(key))
    set_key = True

    now = datetime.now().strftime('%s')
    age = now
    value = state + ',' + age

    if out:
        out = out.split(',')
        old_state = out[0]
        time_since = out[1]
        # dont update the existing state if not changed
        if old_state == state:
            set_key = False
            age = time_since
    if set_key:
        memc.set(str(key), value)

    return int(age)


def service_dict_for_kpi_services(
        perf, state, hostname, site, 
        ip_address, age_of_state, **args):    
    service_dict = {}
    service_dict['host_name'] = hostname
    service_dict['address'] = ip_address 
    service_dict['site'] = site
    service_dict['perf_data'] = perf
    service_dict['last_state_change'] = age_of_state
    service_dict['state']  = state
    service_dict['last_chk'] = time.time()
    service_dict['service_description']=args['service']
    service_dict['age']= age_of_state

    return service_dict    


@app.task(base=DatabaseTask,name='extract_ss_ul_issue_data')
def extract_ss_ul_issue_data(pmp_data_dict,redis_conn,**args):        
    state = 3
    ul_issue =0
    perf = ''
    plugin_message = ''
    DB = None
    
    state_string = "unknown"
    service_state_type = ["warning","critical"]
    service_dict_list = []
    cambium_bs_ul_issue_data = []
    wimax_bs_ul_issue_data = []
    #warning('ss info: {0}'.format(ss_info))

    local_cnx = redis_conn.redis_cnx
    p = local_cnx.pipeline()
    for (ss_info, bs_host_name, bs_site_name, bs_ip_address, sect_id, sec_type) in pmp_data_dict :
        service_dict_list = []
        state_string = 'unknown'
        ul_issue = 0
	perf = ''
	for entry in ss_info:
		if entry:
		    host_name ,site ,ip_address = literal_eval(entry[0])
		else:
		    break
		try:
		    service_state_out = []
		    if 'wimax' in args['service']:
			ul_intrf_serv_key = local_cnx.keys(pattern="ul_issue:%s:wimax_ul_intrf" % host_name)
			[p.lrange(k, 0 , -1) for k  in ul_intrf_serv_key]
			ul_intrf_values = p.execute()
			dl_intrf_serv_key = local_cnx.keys(pattern="ul_issue:%s:wimax_dl_intrf" % host_name)
			[p.lrange(k, 0 , -1) for k  in dl_intrf_serv_key]
			dl_intrf_values = p.execute()
			if len(dl_intrf_values[0]) == 2 and dl_intrf_values[0][0].lower() == 'critical' and \
			    dl_intrf_values[0][1].lower() == 'critical':
			    ul_issue = 0 
			    state_string = "ok"
			elif len(ul_intrf_values[0]) == 2 and ul_intrf_values[0][0].lower() in service_state_type and \
			    ul_intrf_values[0][1].lower() in service_state_type:
			    ul_issue = 1
			    state_string = "ok"
			elif len(ul_intrf_values[0]) == 2  and len(dl_intrf_values[0]) == 2:
			    ul_issue = 0
			    state_string = "ok"
		    else:
			ul_jitter_count = 0
			rereg_count = 0
			ul_jitter_key = local_cnx.keys(pattern="ul_issue:%s:cambium_ul_jitter" % host_name)
			rereg_count_key = local_cnx.keys(pattern="ul_issue:%s:cambium_rereg_count" % host_name)
			[p.lrange(k, 0 , -1) for k  in ul_jitter_key]
			ul_jitter_values = p.execute()
			[p.lrange(k, 0 , -1) for k  in rereg_count_key]
			rereg_values = p.execute()
			#error('ss ul issue: {0} {1} {2}'.format(ul_jitter_values,rereg_values,host_name))
			try:
			    for entry in ul_jitter_values[0]:
				if entry in service_state_type:
				    ul_jitter_count = ul_jitter_count +1
			except:
			    ul_jitter_count = 0
			for entry in rereg_values[0]:
			    if entry in service_state_type:
				rereg_count = rereg_count + 1

			
			if ul_jitter_count == 2 or rereg_count == 2 :
			    state_string = "ok"
			    state = 0
			    ul_issue = 1
			else:
			    state_string = "ok"
			    ul_issue = 0
		    perf = 'ul_issue' + "=%s;;;" % (ul_issue)
		except Exception ,e:
		    warning('error: {0}'.format(e))
		    perf = ''

		age_of_state = age_since_last_state(host_name, args['service'], state_string)
		service_dict = service_dict_for_kpi_services(
		    perf,state_string,host_name,
		    site,ip_address,age_of_state,**args)
		service_dict_list.append(service_dict)
	if 'cambium' in args['service']:
		cambium_bs_ul_issue_data.append((service_dict_list,bs_host_name,bs_site_name,bs_ip_address,sect_id))
	elif 'wimax' in args['service']:
		wimax_bs_ul_issue_data.append((service_dict_list,bs_host_name,bs_site_name,bs_ip_address,sect_id,sec_type))

    #redis_conn = str(args['redis'])
    #arg['redis'] = ''
    #warning(' ul issue dict: {0}'.format(len(service_dict_list)))
    """
    if 'cambium' in args['service']:
        extract_cambium_bs_ul_issue_data.s(
                service_dict_list,
                bs_host_name,
                bs_site_name,
                bs_ip_address,
                sect_id,
                **args).apply_async()
    elif 'wimax' in args['service']:
        extract_wimax_bs_ul_issue_data.s(
                service_dict_list,
                bs_host_name,
                bs_site_name,
                bs_ip_address,
                sect_id ,
                sec_type,
                **args).apply_async()
    """
    if 'cambium' in args['service']:
        extract_cambium_bs_ul_issue_data.s(cambium_bs_ul_issue_data,**args).apply_async()
    elif 'wimax' in args['service']:
        extract_wimax_bs_ul_issue_data.s(wimax_bs_ul_issue_data,**args).apply_async()

@app.task(base=DatabaseTask,name='call_kpi_services')
def call_kpi_services(**opt):
    #DB_CONF = getattr(app.conf, 'CNX_FROM_CONF', None)
    #conf = ConfigParser()
    #conf.read(DB_CONF)
    opts = {'site_name': opt.get('site_name')}
    
    rds_cli_invent = RedisInterface(custom_conf={'db': INVENTORY_DB})
    redis_cnx = rds_cli_invent.redis_cnx
    #wimax_bs_key = redis_cnx.keys(pattern="wimax:bs:*")
    wimax_bs_key = redis_cnx.keys(pattern="wimax:bs:%s:*" % opts['site_name'])
    #wimax_ss_key = redis_cnx.keys(pattern="wimax:ss:*")
    wimax_ss_key = redis_cnx.keys(pattern="wimax:ss:%s:*" % opts['site_name'])
    #warning('wimax_bs_key len: {0}'.format(len(wimax_bs_key)))
    #warning('wimax_ss_key len: {0}'.format(len(wimax_ss_key)))

    pmp_bs_key = redis_cnx.keys(pattern="pmp:bs:%s:*" % opts['site_name'])
    pmp_ss_key = redis_cnx.keys(pattern="pmp:ss:%s:*" % opts['site_name'])
    radwin_ss_key = redis_cnx.keys(pattern="p2p:ss:%s:*" % opts['site_name'])
    mrotek_bs_key = redis_cnx.keys(pattern="pine:bs:%s:*" % opts['site_name'])
    rici_bs_key = redis_cnx.keys(pattern="rici:bs:%s:*" % opts['site_name'])
    cisco_bs_key = redis_cnx.keys(pattern="cisco:bs:%s:*" % opts['site_name'])
    juniper_bs_key = redis_cnx.keys(pattern="juniper:bs:%s:*" % opts['site_name'])
    huawei_bs_key = redis_cnx.keys(pattern="huawei:bs:%s:*" % opts['site_name'])
    p = redis_cnx.pipeline()

    wimax_util_kpi_services = [
            'wimax_pmp1_dl_util_kpi',
            'wimax_pmp2_dl_util_kpi',
            'wimax_pmp1_ul_util_kpi',
            'wimax_pmp2_ul_util_kpi',
            'wimax_ss_ul_issue_kpi',
            'wimax_ss_provis_kpi'
            ]
    cambium_util_kpi_services = [
            'cambium_dl_util_kpi',
            'cambium_ul_util_kpi',
            'cambium_ss_ul_issue_kpi',
            'cambium_ss_provis_kpi'
            ]
    radwin_util_kpi_services = [
            'radwin_dl_util_kpi',
           'radwin_ul_util_kpi',
	    'radwin_ss_provis_kpi'
            ]
    mrotek_util_kpi_services = [
            'mrotek_dl_util_kpi',
            'mrotek_ul_util_kpi'
            ]
    rici_util_kpi_services = [
            'rici_dl_util_kpi',
            'rici_ul_util_kpi'
            ]
    cisco_util_kpi_services = [
            'cisco_switch_dl_util_kpi',
            'cisco_switch_ul_util_kpi'
            ]
    juniper_util_kpi_services = [
            'juniper_switch_dl_util_kpi',
            'juniper_switch_ul_util_kpi'
            ]
    huawei_util_kpi_services = [
            'huawei_switch_dl_util_kpi',
            'huawei_switch_ul_util_kpi'
            ]



    service_threshold = {}
    total_services = []
    total_services.extend(wimax_util_kpi_services)
    total_services.extend(cambium_util_kpi_services)
    total_services.extend(radwin_util_kpi_services)
    total_services.extend(mrotek_util_kpi_services)
    total_services.extend(rici_util_kpi_services)
    total_services.extend(cisco_util_kpi_services)
    total_services.extend(juniper_util_kpi_services)
    total_services.extend(huawei_util_kpi_services)
    total_services.extend(['wimax_bs_ul_issue_kpi', 'cambium_bs_ul_issue_kpi'])

    for service_name in total_services:
        bs_war_key  = service_name + ':war'
        bs_crit_key  = service_name + ':crit'
        service_threshold[bs_war_key]  =  redis_cnx.get(bs_war_key)
        service_threshold[bs_crit_key]  =  redis_cnx.get(bs_crit_key)

    ## calling tasks for wimax services
    call_tasks(
            wimax_bs_key,
            wimax_util_kpi_services[:5],
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_wimax_util_data'
            )
    #for i in izip_longest(*[iter(wimax_bs_key)] * 500):
    #    [p.lrange(k, 0 , -1) for k  in i]
    #    #[p.lrange(k, 0,-1) for k  in ]
    #    #[p.lrange(k, 0,-1) for k  in wimax_ss_key]
    #    wimax_bs_params = p.execute()
    #    args = {}
    #    args['site_name'] =  opts['site_name']
    #    args['host_info'] = wimax_bs_params
    #    args['my_function'] = 'extract_wimax_util_data'
    #    args['provis_bw'] = 4
    #    args['memc']  = call_kpi_services.memc_cnx
    #    #warning('memc: {0}'.format(args['memc']))
    #    args['service'] = wimax_util_kpi_services[0]
    #    bs_war_key  = args['service'] + ':war'
    #    bs_crit_key  = args['service'] + ':crit'
    #    args['war']  = service_threshold[bs_war_key] 
    #    args['crit']  = service_threshold[bs_crit_key]
    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    extract_kpi_services_data.s(**args).apply_async()
    #
    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['service'] = wimax_util_kpi_services[1]
    #    bs_war_key  = args['service'] + ':war'
    #    bs_crit_key  = args['service'] + ':crit'
    #    args['war']  = service_threshold[bs_war_key] 
    #    args['crit']  = service_threshold[bs_crit_key]
    #    extract_kpi_services_data.s(**args).apply_async()
    #
    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['provis_bw'] = 2
    #    args['service'] = wimax_util_kpi_services[2]
    #    bs_war_key  = args['service'] + ':war'
    #    bs_crit_key  = args['service'] + ':crit'
    #    args['war']  = service_threshold[bs_war_key] 
    #    args['crit']  = service_threshold[bs_crit_key]
    #    extract_kpi_services_data.s(**args).apply_async()
    #
    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['service'] = wimax_util_kpi_services[3]
    #    bs_war_key  = args['service'] + ':war'
    #    bs_crit_key  = args['service'] + ':crit'
    #    args['war']  = service_threshold[bs_war_key] 
    #    args['crit']  = service_threshold[bs_crit_key]
    #    extract_kpi_services_data.s(**args).apply_async()

    #rds_cli = RedisInterface()
    #args['redis'] = rds_cli
    #args['service'] = wimax_util_kpi_services[4]
    #extract_wimax_ul_issue_data.s(**args).apply_async()

    #for i in izip_longest(*[iter(wimax_ss_key)] * 500):
    #    args = {}    
    #    args['site_name'] =  opts['site_name']
    #    [p.lrange(k, 0, -1) for k  in i]
    #    wimax_ss_params = p.execute()
    #    
    #    
    #    args['host_info'] = wimax_ss_params
    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['service'] = wimax_util_kpi_services[5]
    #    args['my_function'] = 'extract_wimax_ss_provis_data' 
    #    extract_kpi_services_data.s(**args).apply_async()

    ## calling tasks for wimax ss provis data
    call_tasks(
            wimax_ss_key,
            wimax_util_kpi_services[5],
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_wimax_ss_provis_data'
            )
    #for i in izip_longest(*[iter(pmp_bs_key)] * 500):    
        #args = {}    
        #args['site_name'] =  opts['site_name']
        #[p.lrange(k, 0 ,-1) for k  in i]
        #cambium_bs_params = p.execute()
    
        #args['host_info'] = cambium_bs_params
        #args['my_function'] = 'extract_cambium_util_data' 
        #args['memc']  = call_kpi_services.memc_cnx

        #args['provis_bw'] = 4.76
        #rds_cli = RedisInterface()
        #args['redis'] = rds_cli
        #args['service'] = cambium_util_kpi_services[0]
        #bs_war_key  = args['service'] + ':war'
        #bs_crit_key  = args['service'] + ':crit'
        #args['war']  = service_threshold[bs_war_key] 
        #args['crit']  = service_threshold[bs_crit_key]
        #extract_kpi_services_data.s(**args).apply_async()

    ## calling tasks for cambium bs util services
    call_tasks(
            pmp_bs_key,
            cambium_util_kpi_services[:3],
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_cambium_util_data'
            )
        #rds_cli = RedisInterface()
        #args['redis'] = rds_cli
        #args['provis_bw'] = 2.24
        #args['service'] = cambium_util_kpi_services[1]
        #bs_war_key  = args['service'] + ':war'
        #bs_crit_key  = args['service'] + ':crit'
        #args['war']  = service_threshold[bs_war_key]
        #args['crit']  = service_threshold[bs_crit_key]
        #extract_kpi_services_data.s(**args).apply_async()

        #rds_cli = RedisInterface()
        #args['redis'] = rds_cli
        #args['service'] = cambium_util_kpi_services[2]
        #extract_cambium_ul_issue_data.s(**args).apply_async()

    ## calling tasks for cambium ss provis services
    call_tasks(
            pmp_ss_key,
            cambium_util_kpi_services[3],
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_cambium_ss_provis_data'
            )
    #for i in izip_longest(*[iter(pmp_ss_key)] * 500):    
    #    args = {}    
    #    args['site_name'] =  opts['site_name']
    #    [p.lrange(k, 0 ,-1) for k  in i]
    #    cambium_ss_params = p.execute()

    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['host_info'] = cambium_ss_params
    #    args['service'] = cambium_util_kpi_services[3]
    #    args['my_function'] = 'extract_cambium_ss_provis_data' 
    #    extract_kpi_services_data.s(**args).apply_async()    

    ## calling tasks for radwin util services
    call_tasks(
            radwin_ss_key,
            radwin_util_kpi_services[:2],
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_radwin_util_data'
            )
    call_tasks(
            radwin_ss_key,
            radwin_util_kpi_services[2],
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_radwin_ss_provis_data'
            )
    #for i in izip_longest(*[iter(radwin_ss_key)] * 500):    
    #    args = {}    
    #    args['site_name'] =  opts['site_name']
    #    [p.lrange(k, 0 ,-1) for k  in i]
    #    radwin_ss_params = p.execute()
    #    args['memc']  = call_kpi_services.memc_cnx
    #    #warning('memc: {0}'.format(args['memc']))
    #
    #    args['host_info'] = radwin_ss_params
    #    args['my_function'] = 'extract_radwin_util_data' 

    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['service'] = radwin_util_kpi_services[0]
    #    bs_war_key  = args['service'] + ':war'
    #    bs_crit_key  = args['service'] + ':crit'
    #    args['war']  = service_threshold[bs_war_key] 
    #    args['crit']  = service_threshold[bs_crit_key]
    #    extract_kpi_services_data.s(**args).apply_async()
    #    
    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['service'] = radwin_util_kpi_services[1]
    #    bs_war_key  = args['service'] + ':war'
    #    bs_crit_key  = args['service'] + ':crit'
    #    args['war']  = service_threshold[bs_war_key] 
    #    args['crit']  = service_threshold[bs_crit_key]
    #    extract_kpi_services_data.s(**args).apply_async()

    ## calling tasks for radwin util services
 
    
    call_tasks(
            mrotek_bs_key,
            mrotek_util_kpi_services,
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_mrotek_util_data'
            )
    
    #for i in izip_longest(*[iter(mrotek_bs_key)] * 500):
    #    args = {}
    #    args['site_name'] =  opts['site_name']
    #    [p.lrange(k, 0 ,-1) for k  in i]
    #    mrotek_bs_params = p.execute()
    #    args['memc']  = call_kpi_services.memc_cnx
    #    #warning('memc: {0}'.format(args['memc']))
    #
    #    args['host_info'] = mrotek_bs_params
    #    args['my_function'] = 'extract_mrotek_util_data'

    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['service'] = mrotek_util_kpi_services[0]
    #    bs_war_key  = args['service'] + ':war'
    #    bs_crit_key  = args['service'] + ':crit'
    #    args['war']  = service_threshold[bs_war_key]
    #    args['crit']  = service_threshold[bs_crit_key]
    #    extract_kpi_services_data.s(**args).apply_async()
    #    
    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['service'] = mrotek_util_kpi_services[1]
    #    bs_war_key  = args['service'] + ':war'
    #    bs_crit_key  = args['service'] + ':crit'
    #    args['war']  = service_threshold[bs_war_key] 
    #    args['crit']  = service_threshold[bs_crit_key]
    #    extract_kpi_services_data.s(**args).apply_async()

    ## calling tasks for radwin util services

    call_tasks(
            rici_bs_key,
            rici_util_kpi_services,
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_rici_util_data'
            )
    call_tasks(
            juniper_bs_key,
            juniper_util_kpi_services,
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_juniper_util_data'
            )
    
    call_tasks(
            cisco_bs_key,
            cisco_util_kpi_services,
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_cisco_util_data'
            )
    
    call_tasks(
            huawei_bs_key,
            huawei_util_kpi_services,
            service_threshold,
            site_name=opt.get('site_name'),
            func='extract_huawei_util_data'
            )

    #for i in izip_longest(*[iter(rici_bs_key)] * 500):
    #    args = {}
    #    args['site_name'] =  opts['site_name']
    #    [p.lrange(k, 0 ,-1) for k  in i]
    #    rici_bs_params = p.execute()
    #    args['memc']  = call_kpi_services.memc_cnx
    #    #warning('memc: {0}'.format(args['memc']))
    #
    #    args['host_info'] = rici_bs_params
    #    args['my_function'] = 'extract_rici_util_data'

    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['service'] = rici_util_kpi_services[0]
    #    bs_war_key  = args['service'] + ':war'
    #    bs_crit_key  = args['service'] + ':crit'
    #    args['war']  = service_threshold[bs_war_key]
    #    args['crit']  = service_threshold[bs_crit_key]
    #    extract_kpi_services_data.s(**args).apply_async()
    #    
    #    rds_cli = RedisInterface()
    #    args['redis'] = rds_cli
    #    args['service'] = rici_util_kpi_services[1]
    #    bs_war_key  = args['service'] + ':war'
    #    bs_crit_key  = args['service'] + ':crit'
    #    args['war']  = service_threshold[bs_war_key]
    #    args['crit']  = service_threshold[bs_crit_key]
    #    extract_kpi_services_data.s(**args).apply_async()


@app.task(base=DatabaseTask, name='call_tasks')
def call_tasks(hosts, services, services_thresholds, site_name=None, func=None, batch=200):
    """ Sends messages for given tasks in celery queue"""
    redis_cnx = RedisInterface(custom_conf={'db': INVENTORY_DB}).redis_cnx
    p = redis_cnx.pipeline()
    #warning('Sending kpi tasks for: {0} hosts'.format(len(hosts)))
    if not isinstance(services, list):
	    services = [services]

    while  hosts:
        [p.lrange(k, 0 ,-1) for k in hosts[:batch]]
        host_params = p.execute()
        for service in services:
            args = {}
            memc = call_tasks.memc_cnx
            war = services_thresholds[service + ':war']
            crit = services_thresholds[service + ':crit']
            provis_bw = bw_services_mapping(service)
            local_cnx = RedisInterface()
            args = {
                    'host_info': host_params,
                    'site_name': site_name,
                    'service': service,
                    'war': war,
                    'crit': crit,
                    'redis': local_cnx,
                    'memc': memc,
                    'provis_bw': provis_bw,
                    'my_function': func
                    }
            if service == 'wimax_ss_ul_issue_kpi':
		args.update({
			'war': services_thresholds['wimax_bs_ul_issue_kpi:war'],
			'crit': services_thresholds['wimax_bs_ul_issue_kpi:crit']
			})
                calling_func = extract_wimax_ul_issue_data
            elif service == 'cambium_ss_ul_issue_kpi':
		args.update({
			'war': services_thresholds['cambium_bs_ul_issue_kpi:war'],
			'crit': services_thresholds['cambium_bs_ul_issue_kpi:crit']
			})
                calling_func = extract_cambium_ul_issue_data
            else:
                calling_func = extract_kpi_services_data
            calling_func.delay(**args)
        hosts = hosts[batch:]


def bw_services_mapping(service):
    mapping = {
            'wimax_pmp1_dl_util_kpi': 4,
            'wimax_pmp2_dl_util_kpi': 4,
            'wimax_pmp1_ul_util_kpi': 2,
            'wimax_pmp2_ul_util_kpi': 2,
            'wimax_ss_ul_issue_kpi': 2,
            'wimax_ss_provis_kpi': 2,
            'cambium_dl_util_kpi': 4.76,
            'cambium_ul_util_kpi': 2.24,
            'cambium_ss_ul_issue_kpi': 2.24,
            }
    return mapping.get(service)

@app.task(base=DatabaseTask, name='extract_radwin_ss_provis_data')
def extract_radwin_ss_provis_data(host_params,**args):
    perf = ''
    state_string = 'unknown'
    service_list= []
    #warning('radwin ss entry: {0}'.format(host_params))
    redis_cnx = args['redis'].redis_cnx
    for entry in host_params:
        rssi = uas = None
        perf = ''
	ss_state = ''
        state_string = 'unknown'
        if entry:
            host ,site,ip,_,_,_ = literal_eval(entry[0])
        else:
            break
        try:
            rssi = redis_cnx.get("provis:%s:%s" % (host,'radwin_rssi'))
            if rssi != None:
                rssi = eval(rssi)
        except:
            rssi = None
	try:
            uas = redis_cnx.get("provis:%s:%s" % (host,'radwin_uas'))
        except:
            uas = None
	try:
	    if rssi != None and int(rssi) < -80:
		ss_state = "los"
		state = 0
		state_string= "ok"
	    elif uas != None and int(uas) != 900 and int(uas) > 20:
		ss_state = "uas"
		state = 0
		state_string= "ok"
	    else:
		ss_state = "normal" 
		state_string= "ok"
		state = 0

	    perf += 'ss_state' + "=%s" % (ss_state)
	except Exception ,e:
	    perf += 'ss_state' + "=%s" % (ss_state)
        
	age_of_state = age_since_last_state(host, args['service'], state_string)

        service_dict = service_dict_for_kpi_services(
                perf, state_string, host, site, ip, age_of_state, **args)
        service_list.append(service_dict)
	ss_state=''
    #warning('radwin ss entry: {0}'.format(service_list))
    if len(service_list) > 0:
	build_export.s(args['site_name'], service_list).apply_async()

@app.task(base=DatabaseTask, name='extract_cambium_ss_provis_data')
def extract_cambium_ss_provis_data(host_params,**args):
    perf = ''
    state_string = 'unknown'
    service_list= []
    #warning('cambium ss entry: {0}'.format(host_params))
    redis_cnx  = args['redis'].redis_cnx
    for entry in host_params:
        ul_rssi = dl_rssi = ul_jitter = dl_jitter = rereg_count = None
        perf = ''
        state_string = 'unknown'
        if entry:
            host ,site,ip = literal_eval(entry[0])
        else:
            break
        try:
            ul_rssi = redis_cnx.get("provis:%s:%s" % (
                host,'cambium_ul_rssi'))
            if ul_rssi != None:
                ul_rssi = eval(ul_rssi)
        except:
            ul_rssi = None
        try:
            dl_rssi = redis_cnx.get("provis:%s:%s" % (
                host,'cambium_dl_rssi'))
            if dl_rssi != None:
                dl_rssi = eval(dl_rssi)
        except:
            dl_rssi = None
        try:
            dl_jitter = redis_cnx.get("provis:%s:%s" % (
                host,'cambium_dl_jitter'))
            if dl_jitter != None:
                dl_jitter = eval(dl_jitter)
        except:
            dl_jitter = None
        try:
            ul_jitter = redis_cnx.get("provis:%s:%s" % (
                host,'cambium_ul_jitter'))
            if ul_jitter != None:
                ul_jitter = eval(ul_jitter)
        except:
            ul_jitter = None
        try:
            rereg_count = redis_cnx.get("provis:%s:%s" % (
                host,'cambium_rereg_count'))
            if rereg_count != None:
                rereg_count = eval(rereg_count)
        except:
            rereg_count = None
        try:
            if ul_rssi != None and dl_rssi != None and (int(ul_rssi) < -82 or int(dl_rssi) < -82):
                ss_state = "los"
                state = 0
                state_string= "ok"
            elif dl_jitter !=None and ul_jitter != None and ( int(ul_jitter) > 7 or int(dl_jitter) > 7):
                ss_state = "jitter"
                state = 0
                state_string= "ok"
            elif rereg_count != None and (int (rereg_count) > 100):
                ss_state = "rereg"
                state = 0
                state_string = "ok"
            else:
                ss_state = "normal" 
                state_string= "ok"
                state = 0
        
            perf = ''.join( 'ss_state' + "=%s;;;" % (ss_state))
        except Exception ,e:
	    ss_state=''
            perf = ''.join( 'ss_state' + "=%s;;;" % (ss_state))

        # calculate age since last state change
        age_of_state = age_since_last_state(host, args['service'], state_string)

        service_dict = service_dict_for_kpi_services(
                perf, state_string, host, site, ip, age_of_state, **args)
        service_list.append(service_dict)
	ss_state=''

    #error('cambium ss provis : {0}'.format(len(service_list)))
    if len(service_list) > 0:
            build_export.s(args['site_name'], service_list).apply_async()


@app.task(base=DatabaseTask, name='extract_wimax_ss_provis_data')
def extract_wimax_ss_provis_data(host_params,**args):
    service_state_out = []
    service_list = []
    redis_cnx = args['redis'].redis_cnx
    for entry in host_params:
        perf =  ss_state = ''
        ul_rssi = dl_rssi = ss_ptx = dl_cinr = None
        state_string = 'unknown'
        if entry:
            host,site,ip  =literal_eval(entry[0])
        else:
            break
        try:
            ul_rssi = redis_cnx.get("provis:%s:%s" % (
                host,'wimax_ul_rssi'))
            if ul_rssi != None:
                ul_rssi = eval(ul_rssi)
        except:
            ul_rssi = None
        try:
            dl_rssi = redis_cnx.get("provis:%s:%s" % (
                host,'wimax_dl_rssi'))
            if dl_rssi != None:
                dl_rssi = eval(dl_rssi)
        except:
            dl_rssi = None
        try:
            dl_cinr = redis_cnx.get("provis:%s:%s" % (
                host,'wimax_dl_cinr'))
            if dl_cinr != None:
                dl_cinr = eval(dl_cinr)
        except:
            dl_cinr = None    
        try:
            ss_ptx = redis_cnx.get("provis:%s:%s" % (
                host,'wimax_ss_ptx_invent'))
            if ss_ptx != None:
                ss_ptx = eval(ss_ptx)
        except:
            ss_ptx = None
        try:
        
            if (ul_rssi !=None and dl_rssi !=None and ss_ptx != None and (int(ul_rssi) < -83 or 
                int(dl_rssi) < -83 and int(ss_ptx) > 20)):
                ss_state = "los"
                state = 0
                state_string= "ok"
            elif (ul_rssi !=None and dl_rssi != None and ss_ptx != None and (int(ul_rssi) < -83 or 
                int(dl_rssi) < -83 and int (ss_ptx) <= 20)):
                ss_state = "need_alignment"
                state = 0
                state_string= "ok"
            elif dl_cinr != None and int(dl_cinr) <= 15:
                ss_state = "rogue_ss"
                state = 0
                state_string = "ok"
            else:
                ss_state = "normal" 
                state_string= "ok"
                state = 0
            perf = ''.join( 'ss_state' + "=%s;;;" % (ss_state))
        except Exception ,e:
            perf = ''.join( 'ss_state' + "=%s;;;" % (ss_state))

        # calculate age since last state change
        age_of_state = age_since_last_state(host, args['service'], state_string)
        service_dict = service_dict_for_kpi_services(
                perf, state_string, host, site, ip, age_of_state, **args)
        service_list.append(service_dict)

    if len(service_list) > 0:
            build_export.s(args['site_name'], service_list).apply_async()


@app.task(base=DatabaseTask, name='extract_kpi_services_data')
def extract_kpi_services_data(**args):
    host_info = args['host_info']
    my_function  = args['my_function']
    service_list = []
    fun = eval(my_function)
    fun(host_info,**args)


@app.task(base=DatabaseTask, name ='extract_cambium_bs_ul_issue_data')
def extract_cambium_bs_ul_issue_data(bs_ul_issue_data,**args):
    count = 0
    perf = ''
    sec_ul_issue = ''
    state_string = 'uknown'
    #warning('cambium ss entry: {0}'.format(ul_issue_list))
    rds_cli = RedisInterface()
    redis_cnx = rds_cli.redis_cnx
    bs_service_dict_list = []
    for (ul_issue_list, host_name, site, ip, sect_id) in bs_ul_issue_data :
            perf = ''
            sec_ul_issue = ''
            state_string = 'unknown'
	    for service_dict in ul_issue_list:
		try:
		    value = int(service_dict['perf_data'].split('=')[1])
		except:
		    continue
		count = count +value

	    if len(ul_issue_list):
		sec_ul_issue = count/float(len(ul_issue_list)) * 100
		if sec_ul_issue > 100:
		    sec_ul_issue = 100
	    try:
		if sec_ul_issue not in ['',None]:
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
		perf = ''.join(
			'bs_ul_issue' + "=%s;%s;%s;%s" %(sec_ul_issue,args['war'],
			    args['crit'],sect_id))
	    except Exception,e:
    	        error('cambium ss entry: {0}'.format(e))
		perf = 'bs_ul_issue'+'=;%s;%s;%s' % (args['war'],args['crit'],sect_id)
		
	    args['service'] = 'cambium_bs_ul_issue_kpi'
	    age_of_state = age_since_last_state(host_name, args['service'], state_string)
	    bs_service_dict = service_dict_for_kpi_services(
		    perf,state_string,
		    host_name,site,ip,age_of_state,**args)
	    bs_service_dict['refer'] =sect_id
	    ul_issue_list.append(bs_service_dict)
	    #warning('cambium bs entry: {0}'.format(len(ul_issue_list)))
	    redis_cnx.rpush('queue:ul_issue:%s' % site,*ul_issue_list)
	    #bs_service_dict_list.append((bs_service_dict, site))
    #insert_bs_ul_issue_data_to_redis(bs_service_dict_list)


@app.task(base=DatabaseTask, name='extract_wimax_ul_issue_data')
def extract_wimax_ul_issue_data(**args):
    host_info = args['host_info']
    pmp1_service_list = []
    pmp2_service_list = []
    pmp1_ss_info = []
    pmp2_ss_info = []
    pmp_data_dict = []
    rds_cli = RedisInterface(custom_conf={'db': INVENTORY_DB})
    redis_cnx = rds_cli.redis_cnx
    p = redis_cnx.pipeline()
    args['memc']  = ''
    redis_conn =args['redis']
    args['redis'] = ''
    memc_conn  = extract_wimax_ul_issue_data.memc_cnx
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
        pmp1_conn_ss_ip,pmp2_conn_ss_ip = extract_wimax_connected_ss(host_name,dr_slave,memc_conn)
        pmp2_ss_key = map(lambda x: 
                redis_cnx.keys(pattern="wimax:ss:*:%s" %x) ,pmp2_conn_ss_ip)
        pmp1_ss_key = map(lambda x: 
                redis_cnx.keys(pattern="wimax:ss:*:%s" %x)  ,pmp1_conn_ss_ip)

        [p.lrange(k[0], 0 , -1) for k  in pmp2_ss_key if k]
        pmp2_ss_info = p.execute()
        [p.lrange(k[0], 0 , -1) for k  in pmp1_ss_key if k]
        pmp1_ss_info = p.execute()
        #warning('pmp2 ss info: {0}, pmp1 ss info {1}'.format(pmp2_ss_info,pmp1_ss_info))
        
        pmp_data_dict.append((pmp2_ss_info,host_name,site_name,ip_address,pmp2_sect_id,'pmp2'))
        pmp_data_dict.append((pmp1_ss_info,host_name,site_name,ip_address,pmp1_sect_id,'pmp1'))
        
        """
        extract_ss_ul_issue_data.s(
                pmp2_ss_info,
                host_name,
                site_name,
                ip_address,
                pmp2_sect_id,
                'pmp2',
                redis_conn,
                **args).apply_async()
        extract_ss_ul_issue_data.s(
                pmp1_ss_info,
                host_name,
                site_name,
                ip_address,
                pmp1_sect_id,
                'pmp1',
                redis_conn,
                **args).apply_async()
		"""
    extract_ss_ul_issue_data.s(pmp_data_dict,redis_conn,**args).apply_async()
    #warning('pmp2 service list: {0}'.format(pmp2_service_list))


@app.task(base=DatabaseTask, name='extract_cambium_ul_issue_data')
def extract_cambium_ul_issue_data(**args):
    host_info = args['host_info']
    service_list = []
    ss_info = []
    rds_cli = RedisInterface(custom_conf={'db': INVENTORY_DB})
    redis_cnx = rds_cli.redis_cnx
    p = redis_cnx.pipeline()
    memc_conn  = extract_cambium_ul_issue_data.memc_cnx
    args['memc'] = ''
    redis_conn =args['redis']
    args['redis'] = ''
    ss_ul_issue_data = []
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
            ss_key = map(lambda x: redis_cnx.keys(pattern="pmp:ss:*:%s" %x) ,conn_ss_ip)
            [p.lrange(k[0], 0 , -1) for k  in ss_key if k]
            ss_info = p.execute()
            ss_ul_issue_data.append((ss_info,host_name,site_name,ip_address,sect_id,None))

    extract_ss_ul_issue_data.s(ss_ul_issue_data,redis_conn,**args).apply_async()


if __name__ == '__main__':
	call_kpi_services.delay(site_name='ospf2_slave_7')
