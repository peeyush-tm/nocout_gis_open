"""
Django settings for nocout project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
import json
from django.conf import global_settings
from collections import namedtuple
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(__file__)

DEBUG = False
TEMPLATE_DEBUG = DEBUG
PROFILE = DEBUG
PROFILE_TYPE = 'line'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'nocout_dev',  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'root',
        'PASSWORD': 'pass',
        'HOST': 'localhost',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '3306',  # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Calcutta'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/home/'
LOGIN_EXEMPT_URLS = (
    r'auth/', 'login/', 'admin/', 'sm/dialog_for_page_refresh/', 'sm/dialog_expired_logout_user/', 'reset-cache/',
    'sm/dialog_action/', 'user/change_password/','download_center/processedreportemail/', 'power/get_sms/')

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, "static/"),
)


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'dajaxice.finders.DajaxiceFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
# A secret key for a particular Django installation.
# This is used to provide cryptographic signing,
# and should be set to a unique, unpredictable value.
SECRET_KEY = 'q+(_ijqc+^&#_51_duhnl+u-$&63tzgdo2b0_gaw!*%swxkc!&'

TEMPLATE_DIRS = (os.path.join(PROJECT_DIR, "templates"),)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)
# Template context processors

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'nocout.context_processors_profile.user_profile_atts.user_dept_org',
    'django_settings_export.settings_export',  # 25th March
)

MIDDLEWARE_CLASSES = (
    # site caching
    # 'django.middleware.cache.UpdateCacheMiddleware',
    # site caching
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'nocout.middleware.UserProfileAuditMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
    'nocout.middlewares.LoginRequiredMiddleware.LoginRequiredMiddleware',
    # 'audit_log.middleware.UserLoggingMiddleware',
    # 'audit_log.middleware.AuditlogMiddleware',
    # Uncomment the next line for simple clickjacking protection
    # required for GISS SCAN
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # site caching
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    # site caching
)

# Whether to use HttpOnly flag on the CSRF cookie. If this is set to True,
# client-side JavaScript will not to be able to access the CSRF cookie.
CSRF_COOKIE_HTTPONLY = True

# Whether to use a secure cookie for the CSRF cookie. If this is set to True,
# the cookie will be marked as secure, which means browsers may ensure that
# the cookie is only sent with an HTTPS connection.
CSRF_COOKIE_SECURE = True

# Whether to use HTTPOnly flag on the session cookie. If this is set to True,
# client-side JavaScript will not to be able to access the session cookie.
SESSION_COOKIE_HTTPONLY = True

# Whether to use a secure cookie for the session cookie. If this is set to True,
# the cookie will be marked as secure, which means browsers may ensure that the
# cookie is only sent under an HTTPS connection.
SESSION_COOKIE_SECURE = True

# A string representing the full Python import path to your root URLconf.
# For example: 'mydjangoapps.urls'. Can be overridden on a per-request basis by
# setting the attribute urlconf on the incoming HttpRequest object.
ROOT_URLCONF = 'nocout.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'nocout.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'session_security',
    'nocout.signals',  # Load before nocout apps
    'nocout',  # 25th March 2015
    'user_profile',
    'device',
    'inventory',
    'organization',
    'service',
    'command',
    'site_instance',
    'machine',
    'home',
    'devicevisualization',
    'sitesearch',
    'downloader',
    'alert_center',
    'capacity_management',
    'download_center',
    'performance',
    'dashboard',
    'scheduling_management',
    'django.contrib.admin',
    'session_management',
    'corsheaders',
    'activity_stream',
    'jsonify',
    'djcelery',
    'rest_framework',
    'alarm_escalation',
    'django_bootstrap_breadcrumbs'
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'session_management.backends.TokenAuthBackend',
)

# Celery settings.
import djcelery
djcelery.setup_loader()

# Redis settings.
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_CONNECT_RETRY = True

# Celery result backend configuration.
CELERY_RESULT_BACKEND = 'redis://' + str(REDIS_HOST) + ':' + str(REDIS_PORT) + '/' + str(REDIS_DB)

# Celery broker settings.
BROKER_HOST = REDIS_HOST         # Maps to redis host.
BROKER_PORT = REDIS_PORT         # Maps to redis port.
BROKER_VHOST = (REDIS_DB + 1)    # Maps to database number.

# Celery broker configuration.
BROKER_URL = 'redis://' + str(BROKER_HOST) + ':' + str(BROKER_PORT) + '/' + str(BROKER_VHOST)

# Celery periodic tasks settings.
from celery import crontab

# Time zone for celery periodic tasks.
CELERY_TIMEZONE = 'Asia/Calcutta'
CELERY_ENABLE_UTC = False
CELERYD_TASK_TIME_LIMIT = 300
CELERY_IGNORE_RESULT = True

REDIS_CACHE_HOST = REDIS_HOST
REDIS_CACHE_PORT = REDIS_PORT
REDIS_CACHE_DB = (REDIS_DB + 2)
REDIS_CACHE_URL = 'redis://' + str(REDIS_CACHE_HOST) + ':' + str(REDIS_CACHE_PORT) + '/' + str(REDIS_CACHE_DB)

# A dictionary containing the settings for all caches to be used with Django.
# It is a nested dictionary whose contents maps cache aliases to a dictionary
# containing the options for an individual cache.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CACHE_URL,
        'TIMEOUT': 60,
        "OPTIONS": {
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'MAX_ENTRIES': 1000,
            "COMPRESS_MIN_LEN": 10,
            "IGNORE_EXCEPTIONS": True,
        }
    }
}

REDIS_QUEUE_HOST = REDIS_HOST
REDIS_QUEUE_PORT = REDIS_PORT
REDIS_QUEUE_DB = (REDIS_DB + 3)
REDIS_QUEUE_URL = 'redis://' + str(REDIS_QUEUE_HOST) + ':' + str(REDIS_QUEUE_PORT) + '/' + str(REDIS_QUEUE_DB)

QUEUES = {
    'default': {
        'LOCATION': REDIS_QUEUE_URL,
        'TIMEOUT': 60,
        'NAMESPACE': 'noc:queue:'
    }
}
# 16th March 2016 : Using Redis Server as Cache Server instead of much performant Memcached.

ALLOWED_APPS_TO_CLEAR_CACHE = [
    'inventory',
]

# Celerybeat tasks scheduler configuration.
CELERYBEAT_SCHEDULE = {
    # BEGIN Topology Updates
    # 'pmp-topology-site-wise': {
    #     'task': 'inventory.tasks.topology_site_wise',
    #     'schedule': crontab(minute='1,6,11,16,21,26,31,36,41,46,51,56'),  # timedelta(seconds=300),
    #     'args': ['PMP']
    # },
    # 'wimax-topology-site-wise': {
    #     'task': 'inventory.tasks.topology_site_wise',
    #     'schedule': crontab(minute='3,8,13,18,23,28,33,38,43,48,53,58'),  # timedelta(seconds=300),
    #     'args': ['WiMAX']
    # },
    'validate_file_for_bulk_upload_create': {
        'task': 'inventory.tasks.validate_file_for_bulk_upload',
        'schedule': crontab(minute=0, hour=12),  # Execute daily at 12:00 p.m
        'args': ['c']
    },
    'validate_file_for_bulk_upload_delete': {
        'task': 'inventory.tasks.validate_file_for_bulk_upload',
        'schedule': crontab(minute=15, hour=12),  # Execute daily at 12:15 p.m
        'args': ['d']
    },
    'process_file_for_bulk_upload': {
        'task': 'inventory.tasks.process_file_for_bulk_upload',
        'schedule': crontab(minute=30, hour=12),  # Execute daily at 12:30 p.m
    },
    'process_file_for_bulk_delete': {
        'task': 'inventory.tasks.process_file_for_bulk_delete',
        'schedule': crontab(minute=15, hour=12),  # Execute daily at 12:45 p.m
    },
    'update-inventory-topology': {
        'task': 'inventory.tasks.update_topology',
        'schedule': timedelta(seconds=300),
    },
    'validate-file-for-bulk-upload': {
        'task': 'inventory.tasks.validate_file_for_bulk_upload',
        'schedule': crontab(minute=0, hour=12),  # Execute daily at 12:00 p.m
    },
    'process-file-for-bulk-upload': {
        'task': 'inventory.tasks.process_file_for_bulk_upload',
        'schedule': crontab(minute=50, hour=12),  # Execute daily at 12:50 p.m
    },
    # END Topology Updates
    # updating the polled sector frequency
    'update-sector-frequency': {
        'task': 'inventory.tasks.update_sector_frequency_per_day',
        'schedule': crontab(minute=0, hour=0)
    },
    # BEGIN Escalation Status for the configured services
    'check-device-status': {
        'task': 'alarm_escalation.tasks.check_device_status',
        'schedule': timedelta(seconds=300),
    },
    # END Escalation Status for the configured services
    # BEGIN Calculations for Capacity
    # Calculations start at 2nd minute for Backhual
    'gather_backhaul_status': {
        'task': 'capacity_management.tasks.gather_backhaul_status',
        'schedule': crontab(minute='*/5'),  # timedelta(seconds=300),
    },
    # Sector Capacity Caclucations
    # Calculations start at 2nd minute for PMP
    'gather_sector_status-pmp': {
        'task': 'capacity_management.tasks.gather_sector_status',
        'schedule': crontab(minute='*/5'),  # timedelta(seconds=300),
        'args': ['PMP']
    },
    # Calculations start at 3rd minute for WiMAX
    'gather_sector_status-wimax': {
        'task': 'capacity_management.tasks.gather_sector_status',
        'schedule': crontab(minute='*/5'),  # timedelta(seconds=300),
        'args': ['WiMAX']
    },
    # END Calculations for Capacity
    # Dashboards Calculations start at 5th minute of the hour
    'calculate_speedometer_dashboards-NW': {
        'task': 'dashboard.tasks.network_speedometer_dashboards',
        'schedule': crontab(minute='*/5'),
    },
    'calculate_speedometer_dashboards-TEMP': {
        'task': 'dashboard.tasks.temperature_speedometer_dashboards',
        'schedule': crontab(minute='*/5'),
    },
    # BEGIN: Range Dashboards
    'calculate_range_dashboards-PMP': {
        'task': 'dashboard.tasks.calculate_range_dashboards',
        'schedule': crontab(minute='4,9,14,19,24,29,34,39,44,49,54,59'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'PMP', 'type': 'sector'}
    },
    'calculate_range_dashboards-WiMAX': {
        'task': 'dashboard.tasks.calculate_range_dashboards',
        'schedule': crontab(minute='4,9,14,19,24,29,34,39,44,49,54,59'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'WiMAX', 'type': 'sector'}
    },
    'calculate_range_dashboards-PMP-BH': {
        'task': 'dashboard.tasks.calculate_range_dashboards',
        'schedule': crontab(minute='4,9,14,19,24,29,34,39,44,49,54,59'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'PMP', 'type': 'backhaul'}
    },
    'calculate_range_dashboards-WiMAX-BH': {
        'task': 'dashboard.tasks.calculate_range_dashboards',
        'schedule': crontab(minute='4,9,14,19,24,29,34,39,44,49,54,59'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'WiMAX', 'type': 'backhaul'}
    },
    'calculate_range_dashboards-TCLPOP-BH': {
        'task': 'dashboard.tasks.calculate_range_dashboards',
        'schedule': crontab(minute='4,9,14,19,24,29,34,39,44,49,54,59'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'TCLPOP', 'type': 'backhaul'}
    },
    # END: Range Dashboards
    'calculate_status_dashboards-PMP': {
        'task': 'dashboard.tasks.calculate_status_dashboards',
        'schedule': crontab(minute='4,9,14,19,24,29,34,39,44,49,54,59'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'PMP'}
    },
    'calculate_status_dashboards-WiMAX': {
        'task': 'dashboard.tasks.calculate_status_dashboards',
        'schedule': crontab(minute='4,9,14,19,24,29,34,39,44,49,54,59'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'WiMAX'}
    },
    'calculate_rf_range_dashboards-WiMAX': {
        'task': 'dashboard.tasks.calculate_RF_Performance_dashboards',
        'schedule': crontab(minute='*/5'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'WiMAX'}
    },
    'calculate_rf_range_dashboards-PMP': {
        'task': 'dashboard.tasks.calculate_RF_Performance_dashboards',
        'schedule': crontab(minute='*/5'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'PMP'}
    },
    'calculate_rf_range_dashboards-PTP': {
        'task': 'dashboard.tasks.calculate_RF_Performance_dashboards',
        'schedule': crontab(minute='*/5'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'P2P'}
    },
    'calculate_rf_range_dashboards-PTP-BH': {
        'task': 'dashboard.tasks.calculate_RF_Performance_dashboards',
        'schedule': crontab(minute='*/5'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'P2P', 'is_bh' : True}
    },
    'hourly-main-dashboard': {
        'task': 'dashboard.tasks.calculate_hourly_main_dashboard',
        'schedule': crontab(minute='5', hour='*')
    },
    'hourly-speedometer-dashboard': {
        'task': 'dashboard.tasks.calculate_hourly_speedometer_dashboard',
        'schedule': crontab(minute='5', hour='*')
    },
    'daily-main-dashboard': {
        'task': 'dashboard.tasks.calculate_daily_main_dashboard',
        'schedule': crontab(minute='5', hour=0)  # Execute Daily at Midnight
    },
    'daily-speedometer-dashboard': {
        'task': 'dashboard.tasks.calculate_daily_speedometer_dashboard',
        'schedule': crontab(minute='5', hour=0)  # Execute Daily at Midnight
    },
    # END Backhaul Capacity Task
    # BEGIN sector spot dashboard jobs
    # will run on STATUS tables. must run within 5 minutes
    'get_all_sector_devices-PMP': {
        'task': 'performance.tasks.get_all_sector_devices',
        'schedule': crontab(minute='1,6,11,16,21,26,31,36,41,46,51,56'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'PMP'}
    },
    'get_all_sector_devices-WiMAX': {
        'task': 'performance.tasks.get_all_sector_devices',
        'schedule': crontab(minute='3,8,13,18,23,28,33,38,43,48,53,58'),  # timedelta(seconds=300),
        'kwargs': {'technology': 'WiMAX'}
    },
    'check_for_monthly_spot-WiMAX-PMP': {
        'task': 'performance.tasks.check_for_monthly_spot',
        'schedule': crontab(hour=23, minute=30)
    },
    # END sector spot dashboard jobs
    # Remove all caching per 6 hours
    'cache_clear_task': {
        'task': 'nocout.tasks.cache_clear_task',
        'schedule': crontab(minute=3, hour='*/6'),  # per 6 hours delete all cache
    },
    # RF Network Availability Job - PTP-BH
    'calculate_rf_network_availability-PTP-BH': {
        'task': 'performance.tasks.calculate_rf_network_availability',
        'kwargs': {'technology': 'P2P'},  # PTP BH is not a tachnology, P2P is
        'schedule': crontab(minute=05, hour=0)
    },
    # RF Network Availability Job - PMP
    'calculate_rf_network_availability-PMP': {
        'task': 'performance.tasks.calculate_rf_network_availability',
        'kwargs': {'technology': 'PMP'},
        'schedule': crontab(minute=15, hour=0)
    },
    # RF Network Availability Job - WiMAX
    'calculate_rf_network_availability-WiMAX': {
        'task': 'performance.tasks.calculate_rf_network_availability',
        'kwargs': {'technology': 'WiMAX'},
        'schedule': crontab(minute=25, hour=0)
    },
    'scheduled_email_report_task': {
        'task': 'download_center.tasks.scheduled_email_report',
        'schedule': crontab(minute=0, hour=12),  # Execute daily at 12:00 p.m
    }
}

CORS_ORIGIN_ALLOW_ALL = True

# Full import path of a serializer class to use for serializing session data.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('/tmp/nocout_main.log'),
            'maxBytes': 1048576,
            'backupCount': 100,
            'formatter': 'verbose',
        },

    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['sentry'],
            'propagate': False,
        },
        'raven': {
            'level': 'ERROR',
            'handlers': ['sentry'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        '': {
            'handlers': ['logfile'],
            'level': 'INFO',
        },
    },
}

# Multi processing data analysis settings.
# If True, then multiprocessing is allowed.
MULTI_PROCESSING_ENABLED = False


# Configuration for 'django-session-security' module.
# Time (in seconds) before the user should be warned that is session will expire because of inactivity.
SESSION_SECURITY_WARN_AFTER = 3540
# Time (in seconds) before the user should be logged out if inactive.
SESSION_SECURITY_EXPIRE_AFTER = 3600
# Expire session on closing web browser.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# List of urls that should be ignored by the middleware.
SESSION_SECURITY_PASSIVE_URLS = ['dialog_for_page_refresh', 'dialog_expired_logout_user']
# Maximum number of users logged in.
MAX_USER_LOGIN_LIMIT = 100

# Nocout custom settings.
DEFAULT_USERS = namedtuple('DEFAULT_USERS', 'USERNAME ID')
NOCOUT_USER = DEFAULT_USERS(USERNAME='nocout', ID=1)
GISADMIN = DEFAULT_USERS(USERNAME='gisadmin', ID=2)
GISOPERATOR_ID = DEFAULT_USERS(USERNAME='gisoperator', ID=3)
GISVIEWER_ID = DEFAULT_USERS(USERNAME='gisviewer', ID=3)


# TODO: With each deployment check for all the technologies.
# Device technologies used in nocout.
DEVICE_TECHNOLOGY = namedtuple('DEVICE_TECHNOLOGY', 'NAME ID')
P2P = DEVICE_TECHNOLOGY('P2P', '2')
WiMAX = DEVICE_TECHNOLOGY('WiMAX', '3')
PMP = DEVICE_TECHNOLOGY('PMP', '4')
Switch = DEVICE_TECHNOLOGY('Switch', '7')
TCLPTPPOP = DEVICE_TECHNOLOGY('TCLPTPPOP', '9')
TCLPOP = DEVICE_TECHNOLOGY('TCLPOP', '8')

MPTT_TREE = namedtuple('MPTT_TREE', 'lft rght level')

ISOLATED_NODE = MPTT_TREE(lft=1, rght=2, level=0)

# Default PING parameters
PING_PACKETS = 60
PING_TIMEOUT = 20
PING_NORMAL_CHECK_INTERVAL = 5
PING_RTA_WARNING = 1500
PING_RTA_CRITICAL = 3000
PING_PL_WARNING = 80
PING_PL_CRITICAL = 100

# List of private IP's.
PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )
GIS_MAP_MAX_DEVICE_LIMIT = 1000

# Exceptional services, i.e. 'ss' services which get service data from 'bs' instead from 'ss'.
EXCEPTIONAL_SERVICES = ['wimax_dl_cinr', 'wimax_ul_cinr', 'wimax_dl_rssi',
                        'wimax_ul_rssi', 'wimax_ul_intrf', 'wimax_dl_intrf',
                        'wimax_modulation_dl_fec', 'wimax_modulation_ul_fec',
                        'cambium_ul_rssi', 'cambium_ul_jitter', 'cambium_reg_count',
                        'cambium_rereg_count']

DEVICE_APPLICATION = {
    'default': {
        'NAME': 'master_UA',  # Or path to database file if using sqlite3.
    }
}

# Services & service datasources settings.
SERVICE_DATA_SOURCE = {
    "rta": {
        "display_name": "Latency",
        "type": "line",
        "valuesuffix": " ms",
        "valuetext": "ms",
        "formula": "rta_null",
        "show_min": 1,
        "show_max": 1,
        "show_gis": 1,
        "show_performance_center": 1,
        "is_inverted": 0,
        "chart_color": "#70AFC4",
        "service_name": 'ping',
        "service_alias": 'Ping',
    },
    "pl": {
        "display_name": "Packet Drop",
        "type": "column",
        "valuesuffix": " %",
        "valuetext": "Percentage (%)",
        "formula": None,
        "show_min": 0,
        "show_max": 0,
        "show_gis": 1,
        "show_performance_center": 1,
        "is_inverted": 0,
        # "chart_color": "#70AFC4",
        "chart_color": "transparent",
        "service_name": 'ping',
        "service_alias": 'Ping',
    },
    "availability": {
        "display_name": "Availability",
        "type": "column",
        "valuesuffix": " %",
        "valuetext": "Percentage (%)",
        "formula": None,
        "show_min": 0,
        "show_max": 0,
        "show_gis": 1,
        "show_performance_center": 1,
        "is_inverted": 0,
        "chart_color": "#70AFC4",
        "service_name": 'availability',
        "service_alias": 'Availability',
    },
    "rf": {
        "display_name": "RF Latency",
        "type": "spline",
        "valuesuffix": " ms",
        "valuetext": "ms",
        "formula": None,
        "show_min": 0,
        "show_max": 0,
        "show_gis": 0,
        "show_ss": 1,
        "show_bs": 1,
        "show_performance_center": 1,
        "is_inverted": 0,
        "chart_color": "#70AFC4",
        "service_name": 'rf',
        "service_alias": 'RF Latency',
    }
}

SERVICES = {

}

# Date Format to be used throughout the application.
# Before:
# DATE_TIME_FORMAT = "%m/%d/%y (%b) %H:%M:%S (%I:%M %p)"
# After: 29-April-15
DATE_TIME_FORMAT = "%d/%m/%y %H:%M"

# Reports configurations.
REPORT_PATH = '/opt/nocout/nocout_gis/nocout/media/download_center/reports'
REPORT_RELATIVE_PATH = '/opt/nocout/nocout_gis/nocout'


# Configuration for 'django-passwords' module.
# PASSWORD_MIN_LENGTH = 6  # Defaults to 6
# PASSWORD_MAX_LENGTH = 120  # Defaults to None
#
# PASSWORD_DICTIONARY = "/usr/share/dict/words"  # Defaults to None
# # PASSWORD_DICTIONARY = "/usr/share/dict/american-english" # Defaults to None
#
# PASSWORD_MATCH_THRESHOLD = 0.9  # Defaults to 0.9, should be 0.0 - 1.0 where 1.0 means exactly the same
# PASSWORD_COMMON_SEQUENCES = []  # Should be a list of strings, see passwords/validators.py for default
# PASSWORD_COMPLEXITY = {  # You can ommit any or all of these for no limit for that particular set
#                          "UPPER": 1,  # Uppercase
#                          "LOWER": 1,  # Lowercase
#                          "DIGITS": 1,  # Digits
#                          "PUNCTUATION": 0,  # Punctuation (string.punctuation)
#                          "NON ASCII": 0,  # Non Ascii (ord() >= 128)
#                          "WORDS": 0  # Words (substrings seperates by a whitespace)
# }


# Email settings.
DEFAULT_FROM_EMAIL = 'wirelessone@tcl.com'
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/nocout/tmp/app-messages'   # Change this to a proper location.
SMS_LOG_FILE_PATH = '/nocout/tmp/app-messages/sms'   # Change this to a proper location.

# Special Calculation Mechanism for capacity management.
CAPACITY_SPECIFIC_TIME = 0

# Live Polling Configuration.
LIVE_POLLING_CONFIGURATION = {
    'maps_default': True,
    'maps_themetics': True,
    'maps_single_service': True,
    'performance': True
}

# Periodic polling parallel processes count.
PERIODIC_POLL_PROCESS_COUNT = 2

# Flag to enable/disable global search.
GLOBAL_SEARCH_FLAG = True

# Flag to enable/disable datatable download option.
DATATABLES_DOWNLOAD_FLAG = True

# White map configuration.
# 1 April 2015
WHITE_MAP_CONFIGURATION = json.dumps({
    "format": "application/openlayers",
    "geoserver_url_India": "http://10.133.12.163:5008/geoserver/cite/wms",
    "layer": "cite:STATE",
    "initial_bounds": [68.14339447036186, 6.748584270488672, 97.40963745103579, 37.07349395945833],
})

# Flag to show/hide historical data on performance page.
# 4 April 2015
HISTORICAL_ON_PERFORMANCE = True

# Chart type for min, max & avg values.
# 11 April 2015
MIN_CHART_TYPE = 'spline'
MAX_CHART_TYPE = 'spline'
AVG_CHART_TYPE = 'spline'

# Chart color for min, max & avg values.
# 15 April 2015
MIN_CHART_COLOR = '#0000FF'
MAX_CHART_COLOR = '#FF00FF'
AVG_CHART_COLOR = '#00FFFF'

# Warning, critical color & type.
# 6 June 2015
WARN_COLOR = '#FFE90D' 
CRIT_COLOR = '#FF193B'
WARN_TYPE = 'line'
CRIT_TYPE = 'line'

# Display flag for severity distrubution pie chart.
# 15 April 2015
DISPLAY_SEVERITY_PIE_CHART = False

# #### Enable Disable Service Impacting Alarms from GUI.
# Version 1 : 25th March 2015
SIA_ENABLED = True
TRAPS_DATABASE = 'default'
# #### Enable Disable Service Impacting Alarms from GUI.

# #### Access Variables in Templates
# Version 1: 25th March 2015
# Now you can access those exported settings from your templates via settings.<KEY>:
# https://github.com/jakubroztocil/django-settings-export
SETTINGS_EXPORT = [
    'DEBUG',
    'SIA_ENABLED',
    'GLOBAL_SEARCH_FLAG',
    'DATATABLES_DOWNLOAD_FLAG',
    'WHITE_MAP_CONFIGURATION',
    'HISTORICAL_ON_PERFORMANCE',
    'WARN_COLOR',
    'CRIT_COLOR',
    'WARN_TYPE',
    'CRIT_TYPE',
    'ENABLE_ADVANCE_FILTERS',
    'ENABLE_UNIFIED_SERVICE_VIEW',
    'ENABLE_AGGREGATE_REPORT_DOWNLOAD',
    'ENABLE_WHITE_THEME',
    'ENABLE_TOPO_VIEW',
    'ENABLE_POWER_TAB',
    'ENABLE_DEVICE_REBOOT_BTN',
    'SHOW_POWER_LOGS',
    'ENABLE_BIRDEYE_VIEW',
    'ENABLE_CUSTOM_DASHBOARD_VIEW',
    'SHOW_RF_COLUMN',
    'NO_ONDEMAND_POLL_SDS',
    'SINGLE_REPORT_EMAIL',
    'SCHEDULED_REPORT_EMAIL',
    'REPORT_EMAIL_PERM',
    'SCHEDULED_SINGLE_REPORT_EMAIL',
    'TICKETS_LINK_ENABLED',
    'NETWORK_TICKET_URL',
    'CUSTOMER_TICKET_URL',
    'PERMISSIONS_MODULE_ENABLED',
    'FAULT_REPORT_ENABLED',
    'SHOW_RFO_DASHBOARD',
    'SHOW_ALL_TAB_IN_ALERTS',
    'GLOBAL_SEARCH_BY_BS_NAME',
    'IDU_SEC_COMMON_UTIL_TAB',
    'SHOW_MTTR_DASHBOARD',
    'SHOW_INC_TICKET_DASHBOARD',
    'SHOW_RESOLUTION_EFFCIENCY_DASHBOARD',
    'SHOW_BH_LINK_ON_SS',
    'SHOW_SECTOR_LINK_ON_SS',
    'TICKETS_LINK_ON_PERF_PAGE'
]

# Dashbaord Settings
# 25th March
SPEEDOMETER_DASHBAORDS = ['down-network', 'packetloss-network', 'latency-network', 'temperature-idu']

# Variables for charts server side rendering.
# 5 May 2015
# Variables for phantom js host location
PHANTOM_PROTOCOL = "http"
PHANTOM_HOST = "10.133.12.163"
PHANTOM_PORT = "5004"

# Exported Chart Image Type, Width & Height
CHART_WIDTH = 900
CHART_HEIGHT = 400
CHART_IMG_TYPE = "png"
# Variable for env name i.e. either it is localhost, uat or prod
ENV_NAME = 'uat'

# URL for 'highcharts-convert.js'.
HIGHCHARTS_CONVERT_JS = STATIC_ROOT + "js/highcharts-convert-" + ENV_NAME + "/highcharts-convert.js"

# For cache time properties, static data caching period and polling data caching period
# 2nd June 2016
CACHE_TIME = {
    'DASHBOARD': 300,
    'INVENTORY': 3600,
    'SERVICE_ALERT': 300,
    'NETWORK_ALERT': 300,
    'DEFAULT_ALERT': 300,
    'SERVICE_PERFORMANCE': 300,
    'NETWORK_PERFORMANCE': 300,
    'DEFAULT_PERFORMANCE': 300,
    'DEFAULT': 60
}

POWER_SMS_DICT = {
    'status' : 'Status',
    'reset' : 'Reset',
    'joji' : 'JOJI'
}

# Params for advance filters feature.
MAX_SUGGESTION_COUNT = 40
DATATABLE_SEARCHTXT_KEY = 'sSearch'

# Flag to enable/disable advance filters feature for datatables.
ENABLE_ADVANCE_FILTERS = False

# Flag to enable/disable unified service view on single performance page.
ENABLE_UNIFIED_SERVICE_VIEW = True

# Flag to enable/disable aggregate report download on single performance page.
ENABLE_AGGREGATE_REPORT_DOWNLOAD = False

####################### Flag to enable/disable new Theme #######################
ENABLE_WHITE_THEME = True

# Flag to show the number of columns on Rf_Performance Dashboard.(equals to 12/number_of_columns_to_be_shown)
SHOW_RF_COLUMN = 6

# Flag to enable/disable topology view on single performance page.
ENABLE_TOPO_VIEW = False

# Flag to enable/disable power on single performance page.
ENABLE_POWER_TAB = False

# Flag to show/hide "Soft Reboot" button from power tab
ENABLE_DEVICE_REBOOT_BTN = False

# Flag to show/hide power logs menu
SHOW_POWER_LOGS = False

# Flag to enable/disable birdeye view on single performance page.
ENABLE_BIRDEYE_VIEW = False

# Flag to enable/disable custom dashboards on single performance page.
ENABLE_CUSTOM_DASHBOARD_VIEW = False

# Flag to enable global search by Base station name
GLOBAL_SEARCH_BY_BS_NAME = False

# Flag to enable common utilization tab for IDU Ip and Sector ID global search
IDU_SEC_COMMON_UTIL_TAB = False

# Password complexity settings.
# ===============================
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 44
PASSWORD_DICTIONARY = {
    'PATH': os.path.join(BASE_DIR, 'user_profile', 'files', 'dictionary.txt'),
    'CHECK': False
}
PASSWORD_COMPLEXITY = {
    'UPPER': 1,
    'LOWER': 1,
    'PUNCTUATION': 1,
    'DIGITS': 1
}

# SDS for which on-demand poll tab should not be visible
NO_ONDEMAND_POLL_SDS = json.dumps([
    'cambium_bs_frequency_invent_frequency',
    'cambium_bs_ip_invent_bs_ip',
    'cambium_bs_mac_invent_bs_mac',
    'cambium_bs_sector_id_invent_bs_sector_id',
    'cambium_bs_ul_issue_kpi_bs_ul_issue',
    'cambium_cell_radius_invent_cell_radius',
    'cambium_color_code_invent_color_code',
    'cambium_commanded_rx_power_invent_commanded_rx_power',
    'cambium_data_rate_modulation_invent_data_rate_modulation',
    'cambium_dl_util_kpi_cam_dl_util_kpi',
    'cambium_odu_type_invent_odu_type',
    'cambium_qos_invent_bw_dl_sus_rate',
    'cambium_qos_invent_bw_ul_sus_rate',
    'cambium_qos_invent_dl_burst_allocation',
    'cambium_qos_invent_ul_burst_allocation',
    'cambium_serial_number_invent_serial_number',
    'cambium_ss_connected_bs_ip_invent_bs_ip',
    'cambium_ss_connected_bs_mac_invent_ss_connected_bs_mac',
    'cambium_ss_frequency_invent_frequency',
    'cambium_ss_ip_invent_ss_ip',
    'cambium_ss_mac_invent_ss_mac',
    'cambium_ss_provis_kpi_ss_state',
    'cambium_ss_sector_id_invent_ss_sector_id',
    'cambium_ss_ul_issue_kpi_ul_issue',
    'cambium_transmit_power_invent_transmit_power',
    'cambium_ul_util_kpi_cam_ul_util_kpi',
    'cambium_vlan_invent_vlan',
    'radwin_dl_util_kpi_rad_dl_util_kpi',
    'radwin_idu_sn_invent_idu_sn',
    'radwin_link_distance_invent_link_distance',
    'radwin_mimo_diversity_invent_mimo_diversity',
    'radwin_odu_sn_invent_odu_sn',
    'radwin_producttype_invent_producttype',
    'radwin_ss_provis_kpi_ss_state',
    'radwin_ssid_invent_ssid',
    'radwin_ul_util_kpi_rad_ul_util_kpi',
    'wimax_bs_ip_invent_bs_ip',
    'wimax_bs_temperature_acb_acb_temp',
    'wimax_bs_temperature_fan_fan_temp',
    'wimax_bs_ul_issue_kpi_pmp1_ul_issue',
    'wimax_bs_ul_issue_kpi_pmp2_ul_issue',
    'wimax_bs_uptime_uptime',
    'wimax_dl_intrf_dl_intrf',
    'wimax_idu_serial_invent_Carrier_Board',
    'wimax_idu_serial_invent_Chassis',
    'wimax_idu_type_invent_idu_type',
    'wimax_odu_serial_invent_odu1',
    'wimax_odu_serial_invent_odu2',
    'wimax_p1_cmd_rx_pwr_invent_p1_cmd_rx_pwr',
    'wimax_p1_mrc_stc_invent_pmp1_mrc',
    'wimax_p1_mrc_stc_invent_pmp1_stc',
    'wimax_p2_cmd_rx_pwr_invent_p2_cmd_rx_pwr',
    'wimax_p2_mrc_stc_invent_pmp2_mrc',
    'wimax_p2_mrc_stc_invent_pmp2_stc',
    'wimax_pmp1_dl_util_kpi_pmp1_dl_util_kpi',
    'wimax_pmp1_frequency_invent_bs_frequency_pmp1',
    'wimax_pmp1_sector_id_invent_pmp1_sector_id',
    'wimax_pmp1_ul_util_kpi_pmp1_ul_util_kpi',
    'wimax_pmp2_dl_util_kpi_pmp2_dl_util_kpi',
    'wimax_pmp2_frequency_invent_bs_frequency_pmp2',
    'wimax_pmp2_sector_id_invent_pmp2_sector_id',
    'wimax_pmp2_ul_util_kpi_pmp2_ul_util_kpi',
    'wimax_pmp_bw_invent_pmp1_bw',
    'wimax_pmp_bw_invent_pmp2_bw',
    'wimax_pmp_cyclic_prefix_invent_pmp1_prefix',
    'wimax_pmp_cyclic_prefix_invent_pmp2_prefix',
    'wimax_pmp_frame_length_invent_pmp1_fr_len',
    'wimax_pmp_frame_length_invent_pmp2_fr_len',
    'wimax_qos_invent_dl_qos',
    'wimax_qos_invent_ul_qos',
    'wimax_ss_errors_status_ifin_errors',
    'wimax_ss_errors_status_ifout_errors',
    'wimax_ss_frequency_frequency',
    'wimax_ss_ip_ss_ip',
    'wimax_ss_mac_ss_mac',
    'wimax_ss_provis_kpi_ss_state',
    'wimax_ss_sector_id_ss_sector_id',
    'wimax_ss_ul_issue_kpi_ul_issue',
    'wimax_ss_vlan_invent_ss_vlan',
    'wimax_transmit_power_pmp1_invent_transmit_power_pmp1',
    'wimax_transmit_power_pmp2_invent_transmit_power_pmp2',
    'wimax_ul_intrf_ul_intrf',
    'cisco_switch_ul_util_kpi_fa0_1_kpi',
    'cisco_switch_dl_util_kpi_fa0_1_kpi',
    'cisco_switch_ul_util_kpi_fa0_2_kpi',
    'cisco_switch_dl_util_kpi_fa0_2_kpi',
    'cisco_switch_ul_util_kpi_fa0_3_kpi',
    'cisco_switch_dl_util_kpi_fa0_3_kpi',
    'cisco_switch_ul_util_kpi_fa0_4_kpi',
    'cisco_switch_dl_util_kpi_fa0_4_kpi',
    'cisco_switch_ul_util_kpi_fa0_5_kpi',
    'cisco_switch_dl_util_kpi_fa0_5_kpi',
    'cisco_switch_ul_util_kpi_fa0_6_kpi',
    'cisco_switch_dl_util_kpi_fa0_6_kpi',
    'cisco_switch_ul_util_kpi_fa0_7_kpi',
    'cisco_switch_dl_util_kpi_fa0_7_kpi',
    'cisco_switch_ul_util_kpi_fa0_8_kpi',
    'cisco_switch_dl_util_kpi_fa0_8_kpi',
    'cisco_switch_ul_util_kpi_fa0_9_kpi',
    'cisco_switch_dl_util_kpi_fa0_9_kpi',
    'cisco_switch_ul_util_kpi_fa0_10_kpi',
    'cisco_switch_dl_util_kpi_fa0_10_kpi',
    'cisco_switch_ul_util_kpi_fa0_11_kpi',
    'cisco_switch_dl_util_kpi_fa0_11_kpi',
    'cisco_switch_ul_util_kpi_fa0_12_kpi',
    'cisco_switch_dl_util_kpi_fa0_12_kpi',
    'cisco_switch_ul_util_kpi_fa0_13_kpi',
    'cisco_switch_dl_util_kpi_fa0_13_kpi',
    'cisco_switch_ul_util_kpi_fa0_14_kpi',
    'cisco_switch_dl_util_kpi_fa0_14_kpi',
    'cisco_switch_ul_util_kpi_fa0_15_kpi',
    'cisco_switch_dl_util_kpi_fa0_15_kpi',
    'cisco_switch_ul_util_kpi_fa0_16_kpi',
    'cisco_switch_dl_util_kpi_fa0_16_kpi',
    'cisco_switch_ul_util_kpi_fa0_17_kpi',
    'cisco_switch_dl_util_kpi_fa0_17_kpi',
    'cisco_switch_ul_util_kpi_fa0_18_kpi',
    'cisco_switch_dl_util_kpi_fa0_18_kpi',
    'cisco_switch_ul_util_kpi_fa0_19_kpi',
    'cisco_switch_dl_util_kpi_fa0_19_kpi',
    'cisco_switch_ul_util_kpi_fa0_20_kpi',
    'cisco_switch_dl_util_kpi_fa0_20_kpi',
    'cisco_switch_ul_util_kpi_fa0_21_kpi',
    'cisco_switch_dl_util_kpi_fa0_21_kpi',
    'cisco_switch_ul_util_kpi_fa0_22_kpi',
    'cisco_switch_dl_util_kpi_fa0_22_kpi',
    'cisco_switch_ul_util_kpi_fa0_23_kpi',
    'cisco_switch_dl_util_kpi_fa0_23_kpi',
    'cisco_switch_ul_util_kpi_fa0_24_kpi',
    'cisco_switch_dl_util_kpi_fa0_24_kpi',
    'cisco_switch_ul_util_kpi_gi0_1_kpi',
    'cisco_switch_dl_util_kpi_gi0_1_kpi',
    'cisco_switch_ul_util_kpi_gi0_2_kpi',
    'cisco_switch_dl_util_kpi_gi0_2_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_0_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_0_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_1_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_1_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_2_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_2_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_3_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_3_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_4_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_4_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_5_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_5_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_6_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_6_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_7_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_7_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_8_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_8_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_9_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_9_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_10_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_10_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_11_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_11_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_12_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_12_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_13_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_13_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_14_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_14_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_15_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_15_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_16_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_16_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_17_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_17_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_18_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_18_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_19_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_19_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_20_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_20_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_21_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_21_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_22_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_22_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_23_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_23_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_24_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_24_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_25_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_25_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_26_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_26_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_27_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_27_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_28_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_28_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_29_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_29_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_30_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_30_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_31_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_31_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_32_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_32_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_33_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_33_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_34_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_34_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_35_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_35_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_36_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_36_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_37_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_37_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_38_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_38_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_39_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_39_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_40_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_40_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_41_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_41_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_42_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_42_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_43_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_43_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_44_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_44_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_45_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_45_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_46_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_46_kpi',
    'juniper_switch_ul_util_kpi_ge-0_0_47_kpi',
    'juniper_switch_dl_util_kpi_ge-0_0_47_kpi',
    'juniper_switch_ul_util_kpi_ge-0_1_0_kpi',
    'juniper_switch_dl_util_kpi_ge-0_1_0_kpi',
    'juniper_switch_ul_util_kpi_ge-0_1_1_kpi',
    'juniper_switch_dl_util_kpi_ge-0_1_1_kpi',
    'juniper_switch_ul_util_kpi_ge-0_1_2_kpi',
    'juniper_switch_dl_util_kpi_ge-0_1_2_kpi',
    'juniper_switch_ul_util_kpi_ge-0_1_3_kpi',
    'juniper_switch_dl_util_kpi_ge-0_1_3_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_1_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_1_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_2_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_2_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_3_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_3_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_4_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_4_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_5_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_5_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_6_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_6_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_7_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_7_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_8_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_8_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_9_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_9_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_10_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_10_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_11_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_11_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_12_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_12_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_13_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_13_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_14_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_14_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_15_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_15_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_16_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_16_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_17_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_17_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_18_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_18_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_19_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_19_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_20_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_20_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_21_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_21_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_22_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_22_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_23_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_23_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_24_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_24_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_25_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_25_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_26_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_26_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_27_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_27_kpi',
    'huawei_switch_ul_util_kpi_gigabitethernet0_0_28_kpi',
    'huawei_switch_dl_util_kpi_gigabitethernet0_0_28_kpi'
])
# Global variable to show/hide Scheduled report mail option in dowload center listing.
REPORT_EMAIL_PERM = json.dumps({
    'bs_dump': 1,
    'ss_dump': 1,
    'ptp_dump': 1,
    'latency_dump': 1,
    'customer_report': 1,
    'duplex_report': 1,
    'ul_issue': 1,
    'modulation': 1,
    'utilization_tot': 1,
    'temperature': 1,
    'rectification_segment': 1,
    'health_ptp_bh': 1    
})

# Global variable to show/hide single report mail option in download center listing
SINGLE_REPORT_EMAIL = False
SCHEDULED_REPORT_EMAIL = False
SCHEDULED_SINGLE_REPORT_EMAIL = False

# Network & customer tickets url
TICKETS_LINK_ENABLED = False
TICKET_PROTOCOL = 'http'
TICKET_IP_PORT = '10.133.12.73:8080'

NETWORK_TICKET_URL = TICKET_PROTOCOL + '://' + TICKET_IP_PORT + '/arsys/forms/remedy-ebu-dev-app1/MPE4%3ARFNOC300%3ADisplayConsole/RFNOC+310+Display+Console/?mode=New'
CUSTOMER_TICKET_URL = TICKET_PROTOCOL + '://' + TICKET_IP_PORT + '/arsys/forms/remedy-ebu-dev-app1/MPE4%3ARFNOC300%3ADisplayConsole/RFNOC+300+Display+Console/?mode=New'

# Enable/Disable permissions link from side menu
PERMISSIONS_MODULE_ENABLED = False

# Enable/Disable fault reports from download center
FAULT_REPORT_ENABLED = False
SHOW_ALL_TAB_IN_ALERTS = False

SHOW_RFO_DASHBOARD = False
SHOW_MTTR_DASHBOARD = False
SHOW_INC_TICKET_DASHBOARD = False
SHOW_RESOLUTION_EFFCIENCY_DASHBOARD = False
SHOW_BH_LINK_ON_SS = False
SHOW_SECTOR_LINK_ON_SS = False
TICKETS_LINK_ON_PERF_PAGE = False

# Import the local_settings.py file to override global settings
try:
    from local_settings import *
except ImportError:
    pass