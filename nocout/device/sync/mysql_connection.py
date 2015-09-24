import mysql.connector

from django.conf.settings import DATABASES

def mysql_conn():
	conf = DATABASES['default']
	db = mysql.connector.connect(
						host=conf.get('HOST'),
						user=conf.get('USER'),
						password=conf.get('PASSWORD'),
						database=conf.get('NAME'),
						port=conf.get('PORT')
						)
	return db

def dict_rows(cursor):
   desc = cursor.description
   return [
		dict(zip([col[0] for col in desc], row))
		for row in cursor.fetchall()
   ] 
