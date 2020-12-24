# connection to snmptt database
snmptt_db = {
        'host': '10.133.19.165',
        'port': 3200,
        'user': 'snmptt',
        'password': 'snmptt',
        'database': 'snmptt'
}

# connection to application database
application_db = {
        'host': '10.133.12.163',
        'port': 3200,
        'user': 'root',
        'password': 'root',
        'database': 'nocout_24_09_14'
}

# connection to traps database
traps_db = application_db

# connection to redis db for invent info
redis_main = {
		'host': '10.133.19.165',
		'port': 6380,
		'db': 3
		}

# connection to redis db for storing current/clear trap info
redis = {
                'host': '10.133.19.165',
                'port': 6380,
                'db': 0
                }

# connection to redis db for MAT info
redis_MAT =  {
                'host': '10.133.19.165',
                'port': 6380,
                'db': 5
                }
