from __future__ import absolute_import
import os
from celery.schedules import crontab
from datetime import timedelta
from kombu import Queue
from celery.beat import PersistentScheduler
from celery import Celery

# Replace a child worker process with a new one, every 20 minutes
os.environ["AUTOSCALE_KEEPALIVE"] = "20"

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

	CELERY_IMPORTS = (
			'tasks', 'db_tasks', 'client')
	#CELERY_ALWAYS_EAGER = True
	CELERY_TASK_RESULT_EXPIRES = timedelta(minutes=30)
	CELERYD_MAX_TASKS_PER_CHILD = 200
	CELERY_QUEUES = (
    		Queue('celery', routing_key='celery'),
    		Queue('transient', routing_key='transient', delivery_mode=1),
    		Queue('queue1', routing_key='queue1', delivery_mode=1),
	)
	CELERY_ROUTES = {
		'client.main': {'queue': 'transient'},
		'client.prepare_data': {'queue': 'transient'},
		'tasks.quantify_perf_data': {'queue': 'transient'},
		'tasks.calc_values': {'queue': 'transient'},
		'tasks.type_caste': {'queue': 'transient'},
		'tasks.find_existing_entry': {'queue': 'transient'},
		'db_tasks.mysql_export': {'queue': 'transient'},
		'db_tasks.read_data': {'queue': 'transient'},
		'clean-main': {'queue': 'queue1', 'routing_key': 'queue1'},
	}
	
	## Celery beat configurations
	CELERY_TIMEZONE = 'Asia/Calcutta'
	#CELERYBEAT_SCHEDULE
	CELERYBEAT_SCHEDULE = {
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
		## bihourly ospf1
		'aggr-bihourly-network-ospf1': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute='*/31'),
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
        		'schedule': crontab(minute='*/31'),
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
        		'schedule': crontab(minute='*/31'),
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
        		'schedule': crontab(minute='*/31'),
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
        		'schedule': crontab(minute='*/31'),
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
        		'schedule': crontab(minute='*/31'),
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
		# historical clean
		'hist-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='tue', minute=0, hour=7),
        		'kwargs': {
			    'type': 'historical',
			},
    		},
		# poller clean
		'ospf1-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='tue', minute=30, hour=7),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf1'
			}
    		},
		'ospf2-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='tue', minute=0, hour=8),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf2'
			}
    		},
		'ospf3-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='tue', minute=30, hour=8),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf3'
			}
    		},
		'ospf4-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='tue', minute=45, hour=8),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf4'
			}
    		},
		'ospf5-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='tue', minute=0, hour=9),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf5'
			}
    		},
		'vrfprv-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='tue', minute=30, hour=9),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'vrfprv'
			}
    		},
		'pub-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='tue', minute=45, hour=9),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'pub'
			}
    		},
	}

	# application specific settings [not related to celery]
	DEVICE_SET = 200
	BATCH_SIZE = 10
	
app.config_from_object(Config)
