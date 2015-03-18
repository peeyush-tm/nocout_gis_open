import mysql.connector

def mysql_conn():
    db = mysql.connector.connect(
                        host='121.244.255.107',
                        user='nocout_root',
                        password='nocout_root_master_UA@123',
                        database='nocout_22_10_14',
                        port=3200
                        )
    return db

def dict_rows(cursor):
   desc = cursor.description
   return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
   ] 
