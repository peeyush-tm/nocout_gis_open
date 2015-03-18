import mysql.connector
import socket
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

