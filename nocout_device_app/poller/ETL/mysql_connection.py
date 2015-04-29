import mysql.connector
import socket
import memcache
try:
    import nocout_settings
    from nocout_settings import _DATABASES, _LIVESTATUS
except Exception as exp:
    print exp

try:
    db = mysql.connector.connect(
		user=_DATABASES['user'],
		host=_DATABASES['host'],
		password=_DATABASES['password'],
		database=_DATABASES['database'],
		port=_DATABASES['port']
		)
except Exception as exp:
    db= None
    print exp

try:
    memc = memcache.Client(['115.114.79.37:11211','115.114.79.38:11211','115.114.79.39:11211','115.114.79.40:11211','115.114.79.41:11211'], debug=1)
except Exception as e:
    memc =None
    print e
