"""  Module to handle mysql connection for sync api"""

#import mysql.connector
from MySQLdb import connect

from django.conf import settings

def mysql_conn():
	conf = {
			'HOST': 'localhost',
			'USER': 'root',
			'PASSWORD': 'root',
			'NAME': 'nocout_m6_v2',
			'PORT': 3306
			}
	conf = settings.DATABASES['default']
	db = connect(
						host=conf.get('HOST'),
						port=conf.get('PORT'),
						user=conf.get('USER'),
						passwd=conf.get('PASSWORD'),
						db=conf.get('NAME'),
						)
	return db

def dict_rows(cursor):
   desc = cursor.description
   return [
		dict(zip([col[0] for col in desc], row))
		for row in cursor.fetchall()
   ] 
