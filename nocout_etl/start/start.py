from __future__ import absolute_import

import os
from sys import path

from celery.beat import PersistentScheduler
from celery.schedules import crontab
from kombu import Queue

from celery import Celery

path.append('/omd/nocout_etl')

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
    BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    REDIS_PORT = 6379
    INVENTORY_DB = 3
    BROKER_URL = 'redis://localhost:' + str(REDIS_PORT) + "/" + str(0)
    CELERY_RESULT_BACKEND = 'redis://localhost:' + str(REDIS_PORT) + "/" + str(1)
    CELERY_IMPORTS = [
            'handlers.db_ops',
            'network.network_etl',
            'service.service_etl',
	]
    #CELERY_QUEUES = (
    #        Queue('celery', routing_key='celery'),
    #        Queue('trans1', routing_key='trans1', delivery_mode=1),
    #        )
    #CELERY_TRACK_STARTED = True
    CELERYD_LOG_COLOR = False
    CELERY_CHORD_PROPAGATES = False
    #CELERY_ALWAYS_EAGER = True
    #CELERY_IGNORE_RESULT = True
    CNX_FROM_CONF = '/omd/nocout_etl/db_conf.ini'
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
            'service-main': {
                'task': 'service-main',
                'schedule': crontab(),
                }
            }

app.config_from_object(Config)
