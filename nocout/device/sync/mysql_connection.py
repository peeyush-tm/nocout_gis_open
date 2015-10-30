"""  Module to handle mysql connection for sync api"""

from django.db import connection

def mysql_conn():
	"""  Function to return mysql connection to execute raw MySQL
	queries through django"""

	return connection

def dict_rows(cursor):
   desc = cursor.description
   return [
		dict(zip([col[0] for col in desc], row))
		for row in cursor.fetchall()
   ] 
