from __future__ import absolute_import
import os
from celery.schedules import crontab
from datetime import timedelta
from kombu import Queue
from celery.beat import PersistentScheduler

from celery import Celery

app = Celery('entry')


class MyBeatScheduler(PersistentScheduler):
    def __init__(self, *args, **kwargs):
        # remove old schedule db
	try:
	    os.remove(kwargs.get('schedule_filename'))
	except OSError:
	    pass
	super(MyBeatScheduler, self).__init__(*args, **kwargs)


class Config:
        # REDIS
        REDIS_HOST = "127.0.0.1"
        REDIS_PORT = 6380
        REDIS_DB = 0
        # celery result backend configuration
        CELERY_RESULT_BACKEND = 'redis://' + str(REDIS_HOST) + ':' + str(REDIS_PORT) + '/' + str(REDIS_DB)

        REDIS_CONNECT_RETRY = True
        #BROKER_HOST = REDIS_HOST  # Maps to redis host.
        #BROKER_PORT = REDIS_PORT  # Maps to redis port.
        #BROKER_VHOST = (REDIS_DB + 1)   # Maps to database number.
        # celery broker configuration
        BROKER_URL = 'redis://' + str(REDIS_HOST) + ':' + str(REDIS_PORT) + '/' + str(REDIS_DB+1)

	CELERY_IMPORTS = ['aggregation_all', 'host_wise_aggr', 'historical_mysql_export', 'mysql_clean']
	CELERY_ALWAYS_EAGER = True
	CELERY_TASK_RESULT_EXPIRES = timedelta(hours=1)
	CELERY_QUEUES = (
    		Queue('celery', routing_key='celery'),
    		Queue('transient', routing_key='transient', delivery_mode=1),
    		Queue('queue1', routing_key='queue1', delivery_mode=1),
	)
	CELERY_ROUTES = {
		'host_wise_aggr.call_quantify_perf_data': {'queue': 'transient'},
		'host_wise_aggr.collector': {'queue': 'transient'},
		'host_wise_aggr.quantify_perf_data': {'queue': 'transient'},
		'host_wise_aggr.calc_values': {'queue': 'transient'},
		'host_wise_aggr.type_caste': {'queue': 'transient'},
		'host_wise_aggr.find_existing_entry': {'queue': 'transient'},
		'historical_mysql_export.mysql_export': {'queue': 'transient'},
		'historical_mysql_export.read_data': {'queue': 'transient'},
		'aggregation_all.demo_task': {'queue': 'transient'},
		'clean-main': {'queue': 'queue1', 'routing_key': 'queue1'},
	}
	
	## Celery beat configurations
	CELERY_TIMEZONE = 'Asia/Calcutta'
	#CELERYBEAT_SCHEDULE
	CELERYBEAT_SCHEDULE = {
		'demo-task': {
        		'task': 'demo-task',
        		'schedule': crontab(minute='*/32'),
    		},
		# hourly
		'aggr-hourly-network': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=10),
        		'kwargs': {
				'source_perf_table': 'performance_performancenetworkbihourly',
				'destination_perf_table': 'performance_performancenetworkhourly',
				'read_from': 'mysql',
				'time_frame': 'hourly',
				'hours': 1,
				'machine': 'historical',
				'all': True
			}
    		},
		'aggr-hourly-service': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=15),
        		'kwargs': {
				'source_perf_table': 'performance_performanceservicebihourly',
				'destination_perf_table': 'performance_performanceservicehourly',
				'read_from': 'mysql',
				'time_frame': 'hourly',
				'hours': 1,
				'machine': 'historical',
				'all': True
			}
    		},
		# daily
		'aggr-daily-network': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=25, hour=0),
        		'kwargs': {
				'source_perf_table': 'performance_performancenetworkhourly',
				'destination_perf_table': 'performance_performancenetworkdaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'historical',
				'all': True
			}
    		},
		'aggr-daily-service': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=40, hour=0),
        		'kwargs': {
				'source_perf_table': 'performance_performanceservicehourly',
				'destination_perf_table': 'performance_performanceservicedaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'historical',
				'all': True
			}
    		},
		# bihourly ospf1
		'aggr-bihourly-network-ospf1': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/30'),
        		'kwargs': {
				'source_perf_table': 'performance_performancenetwork',
				'destination_perf_table': 'performance_performancenetworkbihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'ospf1',
				'all': False
			}
    		},
		'aggr-bihourly-service-ospf1': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/30'),
        		'kwargs': {
				'source_perf_table': 'performance_performanceservice',
				'destination_perf_table': 'performance_performanceservicebihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'ospf1',
				'all': False
			}
    		},
		# bihourly, ospf2
		'aggr-bihourly-network-ospf2': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/30'),
        		'kwargs': {
				'source_perf_table': 'performance_performancenetwork',
				'destination_perf_table': 'performance_performancenetworkbihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'ospf2',
				'all': False
			}
    		},
		'aggr-bihourly-service-ospf2': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/30'),
        		'kwargs': {
				'source_perf_table': 'performance_performanceservice',
				'destination_perf_table': 'performance_performanceservicebihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'ospf2',
				'all': False
			}
    		},
		# bihourly, ospf3
		'aggr-bihourly-network-ospf3': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/30'),
        		'kwargs': {
				'source_perf_table': 'performance_performancenetwork',
				'destination_perf_table': 'performance_performancenetworkbihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'ospf3',
				'all': False
			}
    		},
		'aggr-bihourly-service-ospf3': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/30'),
        		'kwargs': {
				'source_perf_table': 'performance_performanceservice',
				'destination_perf_table': 'performance_performanceservicebihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'ospf3',
				'all': False
			}
    		},
		# bihourly, ospf4
		'aggr-bihourly-network-ospf4': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/32'),
        		'kwargs': {
				'source_perf_table': 'performance_performancenetwork',
				'destination_perf_table': 'performance_performancenetworkbihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'ospf4',
				'all': False
			}
    		},
		'aggr-bihourly-service-ospf4': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/32'),
        		'kwargs': {
				'source_perf_table': 'performance_performanceservice',
				'destination_perf_table': 'performance_performanceservicebihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'ospf4',
				'all': False
			}
    		},
		# bihourly, ospf5
		'aggr-bihourly-network-ospf5': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/32'),
        		'kwargs': {
				'source_perf_table': 'performance_performancenetwork',
				'destination_perf_table': 'performance_performancenetworkbihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'ospf5',
				'all': False
			}
    		},
		'aggr-bihourly-service-ospf5': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/32'),
        		'kwargs': {
				'source_perf_table': 'performance_performanceservice',
				'destination_perf_table': 'performance_performanceservicebihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'ospf5',
				'all': False
			}
    		},
		# bihourly, vrfprv
		'aggr-bihourly-network-vrfprv': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/32'),
        		'kwargs': {
				'source_perf_table': 'performance_performancenetwork',
				'destination_perf_table': 'performance_performancenetworkbihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'vrfprv',
				'all': False
			}
    		},
		'aggr-bihourly-service-vrfprv': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/32'),
        		'kwargs': {
				'source_perf_table': 'performance_performanceservice',
				'destination_perf_table': 'performance_performanceservicebihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'vrfprv',
				'all': False
			}
    		},
		# bihourly, pub
		'aggr-bihourly-network-pub': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/32'),
        		'kwargs': {
				'source_perf_table': 'performance_performancenetwork',
				'destination_perf_table': 'performance_performancenetworkbihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'pub',
				'all': False
			}
    		},
		'aggr-bihourly-service-pub': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/32'),
        		'kwargs': {
				'source_perf_table': 'performance_performanceservice',
				'destination_perf_table': 'performance_performanceservicebihourly',
				'read_from': 'mysql',
				'time_frame': 'half_hourly',
				'hours': 0.5,
				'machine': 'pub',
				'all': False
			}
    		},
		'hist-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(minute=45, hour=1),
        		'kwargs': {
			    'type': 'historical'
			}
    		},
		'ospf1-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(minute=30, hour=0),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf1'
			}
    		},
		'ospf2-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(minute=40, hour=0),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf2'
			}
    		},
		'ospf3-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(minute=50, hour=0),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf3'
			}
    		},
		'ospf4-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(minute=0, hour=1),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf4'
			}
    		},
		'ospf5-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(minute=20, hour=1),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf5'
			}
    		},
		'vrfprv-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(minute=40, hour=1),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'vrfprv'
			}
    		},
		'pub-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(minute=0, hour=2),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'pub'
			}
    		},
	}

	# application specific settings [not related to celery]
	DEVICE_SET = 200
	
app.config_from_object(Config)
