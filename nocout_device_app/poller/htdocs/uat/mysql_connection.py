import mysql.connector

def mysql_conn():
    db = mysql.connector.connect(
                        host='10.133.12.163',
                        user='root',
                        password='root',
                        database='nocout_24_09_14',
                        port=3200
                        )
    return db

def dict_rows(cursor):
   desc = cursor.description
   return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
   ] 
