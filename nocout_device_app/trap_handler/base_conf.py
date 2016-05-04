# connection to snmptt database
snmptt_db = {
        'host': '121.244.255.108',
        'port': 3200,
        'user': 'nocout_admin',
        'password': 'nocout_root_master_UA@123',
        'database': 'nocout_snmptt'
}

# connection to application database
application_db = {
        'host': '121.244.255.107',
        'port': 3200,
        'user': 'nocout_root',
        'password': 'nocout_root_master_UA@123',
        'database': 'nocout_m6'
}

# connection to traps database
traps_db = application_db

# connection to redis db for invent info
redis_master = {
                'host': '121.244.255.123',
                'port': 6379,
                'db': 3
                }

# connection to redis db for storing current/clear trap info
redis = {
                'host': '121.244.255.123',
                'port': 6379,
                'db': 0
                }

# connection to redis db for MAT info
redis_MAT =  {
                'host': '121.244.255.123',
                'port': 6379,
                'db': 5
                }
