"""Script to read network event data and store to snmptt"""
#from nocout_site_name import *
from datetime import datetime, timedelta
import imp
import time
from sys import path
from operator import itemgetter
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error
#path.append('nocout/performance/service')


# changed module for production
#db_ops_module = imp.load_source('db_ops', '/omd/sites/%s/lib/python/handlers/db_ops.py' % nocout_site_name)
from handlers.db_ops import *

#start_app_module = imp.load_source('start_pub', '/omd/sites/%s/lib/python/start_pub.py' % nocout_site_name)
#app = start_app_module.app
from start.start import app

#mapper_module =  imp.load_source('mapper', '/omd/sites/%s/nocout/performance/service/mapper.py' % nocout_site_name)
#from trap_handler import mapper

#from mapper import Eventmapper
from trap_handler.mapper import Eventmapper
from trap_handler.correlation import *

@app.task(name='insert_network_event')
def insert_network_event(**opt):
    machine_names = opt.get('machine_name')
    for machine_name in machine_names :
        data_list = make_network_snmptt_data(machine_name)
        if data_list :
            #print "Data list network event",data_list
            worker = Eventmapper()
            worker.filter_events(data_list)
	    #collect_down_events_from_redis.s(data_list).apply_async()

@app.task(name='insert_bs_ul_issue_event')
def insert_bs_ul_issue_event(**opt):
    machine_name =  opt.get('machine_name')
    data_list = make_bs_ul_issue_snmptt_data(machine_name)
    if data_list :
        #print "Data list BS UL issue",data_list
        worker = Eventmapper()
        worker.filter_events(data_list)

@app.task(name='make_network_snmptt_data')
def make_network_snmptt_data(machine_name):
    ds_event_mapping = {}
    {'rta':'Latency_Threshold_Breach'}
    try:
        queue = RedisInterface(perf_q = 'queue:network:snmptt:%s' % machine_name)
        cursor = queue.get(0, -1)
        docs = []
	docs = sorted(cursor, key=itemgetter(-2))
	#print "Record",docs
	logger.error("Event Record :  %s",str(docs))
        return docs
    except Exception,e :
        #print "Error in Redis Tuple in %s : %s \n" % (machine_name,str(e))
	logger.error("Error in Redis Tuple in %s : %s \n" , (machine_name,str(e)))
	pass

@app.task(name='make_bs_ul_issue_snmptt_data')
def make_bs_ul_issue_snmptt_data(machine_name):
    try:
        queue = RedisInterface(perf_q = 'q:bs_ul_issue_event:%s' % machine_name)
        cur = queue.get(0, -1)
        docs = []
        for doc in cur:
            severity = doc.get('state').lower()
            service  = doc.get('service_description')
            event_name = 'Uplink_Issue_threshold_Breach'
            if severity == 'critical' or severity == 'warning' :
                severity = 'major'
            if severity == 'ok':
                severity = 'clear'
            t = (
                 '',
                 event_name,
                 '',
                 doc.get('address'),
                 '',
                 '',
                 severity,
                 '',
                 time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(doc.get('last_chk')))),
                 ''
                 )
            docs.append(t)
            t =()
        return docs
    except Exception,e :
        #pass
        print "Error in BS UL Issue Redis Tuple : %s \n",str(e)

