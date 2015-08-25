from __future__ import absolute_import

import os
from sys import path

from celery.beat import PersistentScheduler
from celery.schedules import crontab
from kombu import Queue

from celery import Celery

app = Celery()
#app.control.purge()


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
    BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    REDIS_PORT = 6379
    # redis db to store device inventory info
    INVENTORY_DB = 3
    BROKER_URL = 'redis://localhost:' + str(REDIS_PORT) + "/" + str(11)
    CELERY_RESULT_BACKEND = 'redis://localhost:' + str(REDIS_PORT) + "/" + str(12)
    CELERY_IMPORTS = [
            'handlers.db_ops',
            'network.network_etl',
            'service.service_etl',
	    'service.kpi_etl'
	]
    d_route = {'queue': 'service', 'routing_key': 'service'}
    #CELERY_QUEUES = (
    #        Queue('celery', routing_key='celery'),
    #        Queue('service', routing_key='service'),
    #        )
#    CELERY_ROUTES = {
#		    'handlers.db_ops': d_route,
#		    'network.network_etl': d_route,
#		    'service.service_etl': d_route,
#		    'service.kpi_etl': d_route,
#		    }
    #CELERY_TRACK_STARTED = True
    CELERYD_LOG_COLOR = False
    CELERY_CHORD_PROPAGATES = False
    #CELERY_ALWAYS_EAGER = True
    #CELERY_IGNORE_RESULT = True
    CNX_FROM_CONF = os.path.join(PROJ_DIR, 'db_conf.ini')
    CELERYBEAT_SCHEDULE = {
            'network-5': {
                'task': 'add',
                'schedule': crontab(hour=1, minute=5),
                'args': (2, 3),
                },
            #'network-main': {
             #   'task': 'network-main',
             #   'schedule': crontab(),
             #   },
            'network-main': {
                'task': 'network-main',
                'schedule': crontab(),
	     	'kwargs' : {'site_name':'pub_slave_1'},
                },
            'service-main': {
                'task': 'service-main',
                'schedule': crontab(),
		'kwargs' : {'site_name':'pub_slave_1'},
                },
	     'get-ul-issue-service-checks':{
		'task' : 'get-ul-issue-service-checks',
		'schedule': crontab(minute='*/2'),
		'kwargs' : {'site_name':'pub_slave_1'},
	     },
	     'build-export-dr-mrc':{
		'task' : 'build-export-dr-mrc',
		'schedule': crontab(minute='*/5'),
		'kwargs' : {'site_name':'pub_slave_1'},
	     },
	     'call_kpi_services':{
		'task' : 'call_kpi_services',
		'schedule': crontab(minute='*/5'),
	      }
            }

app.config_from_object(Config)
