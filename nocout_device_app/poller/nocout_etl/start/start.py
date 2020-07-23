from __future__ import absolute_import

import os
from sys import path

from celery.beat import PersistentScheduler
from celery.schedules import crontab
from kombu import Queue

from celery import Celery
from celery.utils.celery_sentinel import register_celery_alias

register_celery_alias('redis-sentinel')

app = Celery()


class MyBeatScheduler(PersistentScheduler):
    def __init__(self, *args, **kwargs):
        # remove old schedule db file
        try:
            os.remove(kwargs.get('schedule_filename'))
        except OSError:
            pass
        super(MyBeatScheduler, self).__init__(*args, **kwargs)


class Config:
    PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # redis db to store device inventory info
    INVENTORY_DB = 3

    SENTINELS = [
		    ('115.114.79.37', 26379), 
		    ('115.114.79.38', 26379), 
		    ('115.114.79.39', 26380), 
		    ('115.114.79.40', 26379), 
		    ('115.114.79.41', 26379)
		    ]
    MEMCACHE_CONFIG = [
		'115.114.79.37:11211', 
		'115.114.79.38:11211', 
		'115.114.79.39:11211', 
		'115.114.79.40:11211', 
		'115.114.79.41:11211'
		]

    # quorum
    MIN_OTHER_SENTINELS = 3
    SERVICE_NAME = 'ospf2'

    # options needed for celery broker connection
    BROKER_TRANSPORT_OPTIONS = {
		    'service_name': 'ospf2',
		    'sentinels': SENTINELS,
		    'min_other_sentinels': 3,
		    'db': 15
		    }
    BROKER_URL = 'redis-sentinel://'

    #CELERY_RESULT_BACKEND = 'amqp://'

    CELERY_IMPORTS = (
            #'handlers.db_ops',
            #'network.network_etl',
            #'service.service_etl',
	    'service.kpi_etl',
	    #'events.events_etl',
	    #'add_dummy',
	    'trap_handler.events_snmptt',
	    'trap_handler.mapper',
            'trap_handler.read_raw_traps',
	)
    CELERYD_LOG_COLOR = False
    CELERY_CHORD_PROPAGATES = False
    #CELERY_ALWAYS_EAGER = True
    #CELERY_IGNORE_RESULT = True
    CNX_FROM_CONF = os.path.join(PROJ_DIR, 'db_conf.ini')
    CELERYBEAT_SCHEDULE = {
	     'get-ul-issue-service-checks-ospf2-1':{
	        'task' : 'get-ul-issue-service-checks',
	        'schedule': crontab(minute='*/2'),
	        'kwargs':{'site_name':'ospf2_subordinate_1'}
	     },
	     'call_kpi_services-ospf2-1':{
	        'task' : 'call_kpi_services',
	        'schedule': crontab(minute='*/5'),
	        'kwargs':{'site_name':'ospf2_subordinate_1'}
	      },
	     'get-ul-issue-service-checks-ospf2-2':{
	        'task' : 'get-ul-issue-service-checks',
	        'schedule': crontab(minute='*/2'),
	        'kwargs':{'site_name':'ospf2_subordinate_2'}
	     },
	     'call_kpi_services-ospf2-2':{
	        'task' : 'call_kpi_services',
	        'schedule': crontab(minute='*/5'),
	        'kwargs':{'site_name':'ospf2_subordinate_2'}
	      },
	     'get-ul-issue-service-checks-ospf2-3':{
	        'task' : 'get-ul-issue-service-checks',
	        'schedule': crontab(minute='*/2'),
	        'kwargs':{'site_name':'ospf2_subordinate_3'}
	     },
	     'call_kpi_services-ospf2-3':{
	        'task' : 'call_kpi_services',
	        'schedule': crontab(minute='*/5'),
	        'kwargs':{'site_name':'ospf2_subordinate_3'}
	      },
	     'get-ul-issue-service-checks-ospf2-4':{
	        'task' : 'get-ul-issue-service-checks',
	        'schedule': crontab(minute='*/2'),
	        'kwargs':{'site_name':'ospf2_subordinate_4'}
	     },
	     'call_kpi_services-ospf2-4':{
	        'task' : 'call_kpi_services',
	        'schedule': crontab(minute='*/5'),
	        'kwargs':{'site_name':'ospf2_subordinate_4'}
	      },
	     'get-ul-issue-service-checks-ospf2-5':{
	        'task' : 'get-ul-issue-service-checks',
	        'schedule': crontab(minute='*/2'),
	        'kwargs':{'site_name':'ospf2_subordinate_5'}
	     },
	     'call_kpi_services-ospf2-5':{
	        'task' : 'call_kpi_services',
	        'schedule': crontab(minute='*/5'),
	        'kwargs':{'site_name':'ospf2_subordinate_5'}
	      },
	     'get-ul-issue-service-checks-ospf2-6':{
	        'task' : 'get-ul-issue-service-checks',
	        'schedule': crontab(minute='*/2'),
	        'kwargs':{'site_name':'ospf2_subordinate_6'}
	     },
	     'call_kpi_services-ospf2-6':{
	        'task' : 'call_kpi_services',
	        'schedule': crontab(minute='*/5'),
	        'kwargs':{'site_name':'ospf2_subordinate_6'}
	      },
	     'get-ul-issue-service-checks-ospf2-7':{
	        'task' : 'get-ul-issue-service-checks',
	        'schedule': crontab(minute='*/2'),
	        'kwargs':{'site_name':'ospf2_subordinate_7'}
	     },
	     'call_kpi_services-ospf2-7':{
	        'task' : 'call_kpi_services',
	        'schedule': crontab(minute='*/5'),
	        'kwargs':{'site_name':'ospf2_subordinate_7'}
	      },
	     'get-ul-issue-service-checks-ospf2-8':{
	        'task' : 'get-ul-issue-service-checks',
	        'schedule': crontab(minute='*/2'),
	        'kwargs':{'site_name':'ospf2_subordinate_8'}
	     },
	     'call_kpi_services-ospf2-8':{
	        'task' : 'call_kpi_services',
	        'schedule': crontab(minute='*/5'),
	        'kwargs':{'site_name':'ospf2_subordinate_8'}
	      },
            'insert-network-event-ospf1': {
                'task': 'insert_network_event',
                'schedule': crontab(minute='*/2'),
                'kwargs': {'machine_name' : 'ospf1'}
                },
	    'insert-bs-ul-issue-event-ospf1': {
	    	'task': 'insert_bs_ul_issue_event',
		'schedule': crontab(minute='*/5'),
                'kwargs': {'machine_name': 'ospf1'},
		},
            'get_passive_checks-ospf2-1-service': {
               'task': 'get_passive_checks_output',
               'schedule': crontab(minute='*/5'),
               'kwargs': {'site_name': 'ospf2_subordinate_1'}
               },
            'get_passive_checks-ospf2-1-interface': {
               'task': 'get_passive_checks_output',
               'schedule': crontab(minute=4),
               'kwargs': {'site_name': 'ospf2_subordinate_1',
                          'ends_with' : 'status'
                         }
               },

	     'load_customer_count_in_redis': {
		'task': 'load_customer_count_in_redis',
		'schedule' : crontab(minute=5)
	     },

             'read_raw_traps': {
                'task': 'read_raw_traps',
                'schedule' : crontab(minute='*/5')
             },

            }

app.config_from_object(Config)
