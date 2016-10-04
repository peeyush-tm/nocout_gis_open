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
			'tasks', 'db_tasks', 
			'client', 'mysql_clean_by_partitions')
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
	one_30_MIN = '1-59/30'
	two_30_MIN = '2-59/30'
	CELERYBEAT_SCHEDULE = {
		# hourly
		'aggr-hourly-network': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=15),
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
        		'schedule': crontab(minute=20),
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
		'aggr-hourly-util': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=10),
        		'kwargs': {
				'source_perf_table': 'performance_utilizationbihourly',
				'destination_perf_table': 'performance_utilizationhourly',
				'read_from': 'mysql',
				'time_frame': 'hourly',
				'hours': 1,
				'machine': 'historical',
				'all': True
			}
    		},
		# daily network
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
		# daily service
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
		# daily utilization
		'aggr-daily-util': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=45, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_utilizationhourly',
				'destination_perf_table': 'performance_utilizationdaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'historical',
				'all': True
			}
    		},
		# daily interface ospf1
		'aggr-daily-interface-ospf1': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=15, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performancestatus',
				'destination_perf_table': 'performance_performancestatusdaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'ospf1',
				'all': False
			}
    		},
		# daily interface ospf2
		'aggr-daily-interface-ospf2': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=15, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performancestatus',
				'destination_perf_table': 'performance_performancestatusdaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'ospf2',
				'all': False
			}
    		},
		# daily interface ospf3
		'aggr-daily-interface-ospf3': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=15, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performancestatus',
				'destination_perf_table': 'performance_performancestatusdaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'ospf3',
				'all': False
			}
    		},
		# daily interface ospf4
		'aggr-daily-interface-ospf4': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=15, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performancestatus',
				'destination_perf_table': 'performance_performancestatusdaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'ospf4',
				'all': False
			}
    		},
		# daily interface ospf5
		'aggr-daily-interface-ospf5': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=15, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performancestatus',
				'destination_perf_table': 'performance_performancestatusdaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'ospf5',
				'all': False
			}
    		},
		# daily interface vrfprv
		'aggr-daily-interface-vrfprv': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=15, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performancestatus',
				'destination_perf_table': 'performance_performancestatusdaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'vrfprv',
				'all': False
			}
    		},
		# daily interface pub
		'aggr-daily-interface-pub': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=15, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performancestatus',
				'destination_perf_table': 'performance_performancestatusdaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'pub',
				'all': False
			}
    		},
		# daily inventory ospf1
		'aggr-daily-inventory-ospf1': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=40, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performanceinventory',
				'destination_perf_table': 'performance_performanceinventorydaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'ospf1',
				'all': False
			}
    		},
		# daily inventory ospf2
		'aggr-daily-inventory-ospf2': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=40, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performanceinventory',
				'destination_perf_table': 'performance_performanceinventorydaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'ospf2',
				'all': False
			}
    		},
		# daily inventory pub
		'aggr-daily-inventory-pub': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=40, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performanceinventory',
				'destination_perf_table': 'performance_performanceinventorydaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'pub',
				'all': False
			}
    		},
		# daily inventory ospf3
		'aggr-daily-inventory-ospf3': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=40, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performanceinventory',
				'destination_perf_table': 'performance_performanceinventorydaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'ospf3',
				'all': False
			}
    		},
		# daily inventory ospf4
		'aggr-daily-inventory-ospf4': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=40, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performanceinventory',
				'destination_perf_table': 'performance_performanceinventorydaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'ospf4',
				'all': False
			}
    		},
		# daily inventory ospf5
		'aggr-daily-inventory-ospf5': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=40, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performanceinventory',
				'destination_perf_table': 'performance_performanceinventorydaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'ospf5',
				'all': False
			}
    		},
		# daily inventory vrfprv
		'aggr-daily-inventory-vrfprv': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=40, hour=1),
        		'kwargs': {
				'source_perf_table': 'performance_performanceinventory',
				'destination_perf_table': 'performance_performanceinventorydaily',
				'read_from': 'mysql',
				'time_frame': 'daily',
				'hours': 24,
				'machine': 'vrfprv',
				'all': False
			}
    		},
		## bihourly ospf1
		'aggr-bihourly-network-ospf1': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=one_30_MIN),
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
        		'schedule': crontab(minute=one_30_MIN),
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
		'aggr-bihourly-util-ospf1': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=one_30_MIN),
        		'kwargs': {
				'source_perf_table': 'performance_utilization',
				'destination_perf_table': 'performance_utilizationbihourly',
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
        		'schedule': crontab(minute=one_30_MIN),
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
        		'schedule': crontab(minute=one_30_MIN),
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
		'aggr-bihourly-util-ospf2': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=one_30_MIN),
        		'kwargs': {
				'source_perf_table': 'performance_utilization',
				'destination_perf_table': 'performance_utilizationbihourly',
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
        		'schedule': crontab(minute=one_30_MIN),
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
        		'schedule': crontab(minute=one_30_MIN),
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
		'aggr-bihourly-util-ospf3': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=one_30_MIN),
        		'kwargs': {
				'source_perf_table': 'performance_utilization',
				'destination_perf_table': 'performance_utilizationbihourly',
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
        		'schedule': crontab(minute=two_30_MIN),
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
        		'schedule': crontab(minute=two_30_MIN),
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
		'aggr-bihourly-util-ospf4': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=one_30_MIN),
        		'kwargs': {
				'source_perf_table': 'performance_utilization',
				'destination_perf_table': 'performance_utilizationbihourly',
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
        		'schedule': crontab(minute=two_30_MIN),
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
        		'schedule': crontab(minute=two_30_MIN),
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
		'aggr-bihourly-util-ospf5': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=one_30_MIN),
        		'kwargs': {
				'source_perf_table': 'performance_utilization',
				'destination_perf_table': 'performance_utilizationbihourly',
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
        		'schedule': crontab(minute=two_30_MIN),
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
        		'schedule': crontab(minute=two_30_MIN),
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
		'aggr-bihourly-util-vrfprv': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=one_30_MIN),
        		'kwargs': {
				'source_perf_table': 'performance_utilization',
				'destination_perf_table': 'performance_utilizationbihourly',
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
        		'schedule': crontab(minute=two_30_MIN),
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
        		'schedule': crontab(minute=two_30_MIN),
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
		'aggr-bihourly-util-pub': {
        		'task': 'aggregation-main',
        		'schedule': crontab(minute=one_30_MIN),
        		'kwargs': {
				'source_perf_table': 'performance_utilization',
				'destination_perf_table': 'performance_utilizationbihourly',
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
        		'schedule': crontab(day_of_week='sat', minute=0, hour=7),
        		'kwargs': {
			    'type': 'historical',
			},
    		},
		# poller clean
		'ospf1-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='sat', minute=30, hour=7),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf1'
			}
    		},
		'ospf2-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='sat', minute=0, hour=8),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf2'
			}
    		},
		'ospf3-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='sat', minute=30, hour=8),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf3'
			}
    		},
		'ospf4-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='sat', minute=45, hour=8),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf4'
			}
    		},
		'ospf5-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='sat', minute=0, hour=9),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'ospf5'
			}
    		},
		'vrfprv-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='sat', minute=30, hour=9),
        		'kwargs': {
			    'type': 'live',
			    'machine': 'vrfprv'
			}
    		},
		'pub-clean': {
        		'task': 'clean-main',
        		'schedule': crontab(day_of_week='sat', minute=45, hour=9),
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
