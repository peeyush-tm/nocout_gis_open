from datetime import datetime
import operator
#from db_conn import ConnectionBase, ExportTraps
from collections import defaultdict
#import imp

# changed module for production
from trap_handler.db_conn import ConnectionBase, ExportTraps
from start.start import app
#start_app_module = imp.load_source('start_pub', '/omd/sites/ospf1_slave_1/lib/python/start_pub.py')
#app = start_app_module.app

severity_for_clear_table = ['clear','ok']
global alarm_mask_oid
global mat_entries
formatline_indexes = {
	# for wimax we need only these two vars
        'wimax': {
            'event_name': 0,
            'event_no': 1,
            'severity': 2,
            },
        }

sia_value = {
	'NA' : '',
	'0' : 'NSA',
	'1' : 'SA',
}
class Eventmapper(object):
   def __init__(self):
	self.conn_base = ConnectionBase()
	# read inventory info from redis [ip --> name mappings]
	self.inventory_info = self.read_cached_inventory()
	# `id` of the most latest row read from MySQL
	self.mat_entry_details = self.read_mat_entries()
	self.customer_count_details = self.read_customer_count_from_redis()
	self.latest_id = None

   def read_cached_inventory(self):
	redis_cnx = self.conn_base.redis_cnx(db_name='redis_master')
	try:
		p = redis_cnx.pipeline()
		p.hgetall('ip:host')
		out = p.execute()
	except Exception as exc:
		out = [{}]
		print 'Error in reading cached inventory: {0}'.format(exc)

	return out[0]

   def read_mat_entries(self):
	redis_cnx = self.conn_base.redis_cnx(db_name='redis_MAT')
	mat_entry_details = {}
	try:
		mat_alarms = redis_cnx.keys('rf_ip*')
		for alarms in mat_alarms:
			mat_entry_details[alarms] = eval(redis_cnx.get(alarms))
	except Exception as exc:
		mat_entry_details = {}
		print 'Error in reading MAT: {0}'.format(exc)
	return mat_entry_details

   def read_customer_count_from_redis(self):	
        customer_count_dict = defaultdict(list)
	try :
		redis_cnx = self.conn_base.redis_cnx(db_name='redis')
		customer_count_data = redis_cnx.keys('customer_count:*')
		for entry in customer_count_data :
        		key = entry.split(':')[-1]
        		customer_count_dict[key] = int(redis_cnx.get(entry))
	except Exception,exc :
  		print 'Error in reading customer count from redis: {0}'.format(exc)
	return customer_count_dict

   def get_alarm_mask_oids(self):
	""" For every current trap, adds its corresponding clear trap 
	and vice-versa"""
        alarm_masking_dict = defaultdict(list)
        query_1 = """
	SELECT master1.alarm_name, master1.severity, master2.alarm_name,master2.severity
	FROM
		alarm_masking_table mask
	INNER JOIN
		master_alarm_table master1
	ON
		mask.alarm_id = master1.id
	INNER JOIN
		master_alarm_table master2
	ON
		mask.alarm_mask_id = master2.id

	and     master1.device_type in ('wimax')
        """
	qry = """
	SELECT 
		master1.oid,master1.severity ,master2.oid mask_oid,master2.severity mask_severity
	FROM
		alarm_masking_table mask
	INNER JOIN
		master_alarm_table master1
	ON
		mask.alarm_id = master1.id
	INNER JOIN
		master_alarm_table master2
	ON
		mask.alarm_mask_id = master2.id

	and     master1.device_type not in ('wimax')
	"""
	my_cnx = self.conn_base.mysql_cnx(db_name='snmptt_db')
	cursor = my_cnx.cursor()
	cursor.execute(query_1)
	wimax_data = cursor.fetchall()
	cursor.execute(qry)
	other_traps_data = cursor.fetchall()
        for (name,severity,mask_name,mask_severity) in wimax_data:
		alarm_masking_dict[(name,severity)].append((mask_name,mask_severity))
	for oid,severity,mask_oid,mask_severity in other_traps_data:
        	alarm_masking_dict[(str(oid),severity)].append((mask_oid,mask_severity))
	return  alarm_masking_dict

   def get_mapped_mat_entries(self):
        """ Mapped MAT entries"""
        mat_entries = []
        query_1 = """
        SELECT
                alarm_name
        FROM
                master_alarm_table
        WHERE        
                device_type in ('wimax')
        """
        qry = """
        SELECT
                oid
        FROM
                master_alarm_table
        WHERE
                device_type not in ('wimax')
        """
        my_cnx = self.conn_base.mysql_cnx(db_name='snmptt_db')
        cursor = my_cnx.cursor()
        cursor.execute(query_1)
        wimax_mat_entries = [item[0] for item in cursor.fetchall()]
        cursor.execute(qry)
        other_traps_mat_entries = [item[0] for item in cursor.fetchall()]
        mat_entries = wimax_mat_entries
        mat_entries.extend(other_traps_mat_entries)
        mat_entries = set(mat_entries)
        return mat_entries

   def make_unique_event_dict(self,events,flag=None):
        # Sample trap entry
        # (222026, u'RAD5K_hbsEncryptionClear', u'.1.3.6.1.4.1.4458.1000.0.237', u'10.172.207.71', 
        #  u'.1.3.6.1.4.1.4458.1000.0.237', u'Status Events', u'clear', u'103:16:56:09.00',
        #datetime.datetime(2016, 1, 22, 11, 24, 53))
	redis_cnx = self.conn_base.redis_cnx(db_name='redis')
	event_dict = {}
	event_count_dict = {}
	#sorted_traps = sorted(traps.items(),key=operator.itemgetter(0))
	global alarm_mask_oid
	global mat_entries
	mat_entries =  self.get_mapped_mat_entries()
	alarm_mask_oid = self.get_alarm_mask_oids()
        mask_oid_key = None 	
	mat_entry = None
	for event in events :
	    alarm_name = str(event[1])
	    if flag == 'event' :
		unique_key = (event[1],event[3])
	    elif 'wimax_trap' in event[1].lower():
	        global formatline_indexes
        	indexes = formatline_indexes['wimax']
		formatline = event[-1].split('|')
		alarm_name = formatline[indexes['event_name']].replace(' ','_')
		unique_key = (alarm_name,event[3])
	    else:
	        unique_key = (event[2],event[3])
	    mat_entry = unique_key[0]
	    if mat_entry in mat_entries :
                # consider trapname and severity for getting maksing entry for WIMAX traps and Events
                # consider trapoid and severity for getting maksing entry for other traps
	        mask_oid_key = alarm_mask_oid.get((unique_key[0],event[6].lower()))
                #delete masking entries in event_dict if previosuly occured
	        if mask_oid_key:
		    for entry in mask_oid_key:
		        try:
			    if (entry[0],event[3]) in event_dict:
			        del event_dict[(entry[0],event[3])]
		        except KeyError:
			    pass
                stored_event = event_dict.get(unique_key)
	        if stored_event:
		    stored_event_time = stored_event[8]
		    if stored_event_time < event[8]:
		        event_dict[unique_key] = event
			event_count_dict[unique_key][1] = event
	        else:
		    event_dict[unique_key] = event
                    # Dictionary to store event count
                    if  unique_key in event_count_dict.keys() :
                        key = 'traps:%s:%s:%s' % (unique_key[1],alarm_name,event[6].lower())
                        redis_cnx.set(key,event_count_dict[unique_key][1][8])
                        event_count_dict[unique_key] = [event_count_dict[unique_key][0] + 1 , event]
                    elif unique_key not in event_count_dict.keys():
                        event_count_dict[unique_key] = [1,event]


	    else :
		print "Not mapped in MAT : ",mat_entry
	return event_dict.values(),event_count_dict

   def update_trap_count(self,event_count_dict):
   	"""Update trap count field using event_count_dict"""
	redis_cnx = self.conn_base.redis_cnx(db_name='redis')
	current_events_update = []
	clear_events_update = []
	traps_events_update = []
	history_event = []
        for count,trap in event_count_dict.values():
            new_trap =  {}
	    current_events_update = []
            if 'wimax' in trap[1].lower() :
                global formatline_indexes
                indexes = formatline_indexes['wimax']
                formatline = trap[-1].split('|')
                severity  = self.severity_mapping(formatline[indexes['severity']])
		last_occurred =  redis_cnx.get('traps:%s:%s:%s' % (trap[3],\
					 formatline[indexes['event_name']].replace(' ','_'),severity))
		if last_occurred :
		    last_occurred = datetime.strptime(last_occurred,'%Y-%m-%d %H:%M:%S')
                else :
		    last_occurred = trap[8]
		eventname = formatline[indexes['event_name']].replace(' ','_')
		sia = sia_value[str(self.mat_entry_details['rf_ip_%s_%s' % (eventname,severity)]['sia'])]
                new_trap.update({
                                'ip_address': trap[3],
                                'device_name': self.inventory_info.get(trap[3]),
                                'trapoid': trap[4],
                                'eventname': formatline[indexes['event_name']].replace(' ','_'),
                                'eventno': formatline[indexes['event_no']],
                                'severity': severity,
                                'uptime': trap[7],
                                'traptime': trap[8],
                                'last_occurred': last_occurred,
                                'first_occurred': trap[8],
                                'alarm_count': count,
                                'description': trap[-1],
                                'is_active': 0,
                                'sia': sia,
				'customer_count': self.customer_count_details[str(trap[3])] \
						if str(trap[3]) in self.customer_count_details else None
                                })
            else :
		severity  = trap[6].lower()
		last_occurred = redis_cnx.get('traps:%s:%s:%s' % (str(trap[3]), str(trap[1]),severity))
                if last_occurred :
                    last_occurred = datetime.strptime(last_occurred,'%Y-%m-%d %H:%M:%S')
                else :
                    last_occurred = trap[8]
		eventname =  str(trap[1])
		try :
                	sia = sia_value[str(self.mat_entry_details['rf_ip_%s_%s' % (eventname,severity)]['sia'])]
                except :
                        sia = ''

                new_trap.update({
                                'ip_address': str(trap[3]),
                                'device_name': self.inventory_info.get(trap[3]),
                                'trapoid': str(trap[4]),
                                'eventname': str(trap[1]),
                                'eventno': str(trap[2]),
                                'severity': trap[6].lower(),
                                'uptime': trap[7],
                                'traptime': trap[8],
                                'last_occurred': last_occurred ,
                                'first_occurred': trap[8],
                                'alarm_count': count,
                                'description': trap[-1],
                                'is_active': 0,
                                'sia': sia,
                                'customer_count': self.customer_count_details[str(trap[3])] \
						if str(trap[3]) in self.customer_count_details else None
                                })
	      
            if severity.lower() not in severity_for_clear_table:
                current_events_update.append(new_trap)
            else:
                clear_events_update.append(new_trap)

	    # Update is_active to 1 in history records
	    new_trap['is_active'] = 1

	    # Update redis key for next polling cycle last_occurred value
	    key = 'traps:%s:%s:%s' % (new_trap['ip_address'],new_trap['eventname'],new_trap['severity'])
	    redis_cnx.set(key,str(new_trap['traptime']))
	    history_event.append(new_trap)


	self.update_db(current_traps=current_events_update, clear_traps=clear_events_update,\
			require_masking=None, flag='update', history_traps=history_event)

   def normalize_events(self, events, alarm_mask_oid,event_type=None):
	""" Convert the traps to compatible schema"""
	redis_cnx = self.conn_base.redis_cnx(db_name='redis')
	out = []
	# these traps have current/clear traps associated with them
	require_masking = []
	# severity for Clear table
	current_events =[]
	clear_events = []
	for event in events:
		mask_oid = None
		new_event = {}
		try:
			last_occurred = redis_cnx.get('traps:%s:%s:%s' % \
					(str(event[3]), str(event[1]),event[6].lower()))
			if last_occurred :
				last_occurred = datetime.strptime(last_occurred,'%Y-%m-%d %H:%M:%S')
			else :
				last_occurred = event[8]

	                eventname =  str(event[1])
			try :
	                	sia = sia_value[str(self.mat_entry_details['rf_ip_%s_%s' \
						 % (eventname,event[6].lower())]['sia'])]
			except :
				print "EventName doesn't match with mapped EventName"
				sia = ''

			new_event.update({
				'ip_address': str(event[3]),
				'device_name': self.inventory_info.get(event[3]),
				'trapoid': str(event[4]),
				'eventname': str(event[1]),
				'eventno': str(event[2]),
				'severity': event[6].lower(),
				'uptime': event[7],
				'traptime': event[8],
				'last_occurred': last_occurred,
				'first_occurred': event[8],
				'alarm_count': 1,
				'description': event[-1],
				'is_active': 1,
                                'sia': sia,
                                'customer_count': self.customer_count_details[str(event[3])]
						 if str(event[3]) in self.customer_count_details else None
				})
			if event[6].lower() not in severity_for_clear_table:
				current_events.append(new_event)
			else:
				clear_events.append(new_event)
		except Exception as exc:
			print 'Exc in normalize traps: {0}'.format(exc)
			continue
		#out.append(new_trap)
		if event_type  == 'event':
			mask_oid = alarm_mask_oid.get((event[1],event[6].lower()))
		elif event_type == 'trap':
			mask_oid = alarm_mask_oid.get((event[4],event[6].lower()))
		if mask_oid:
			# update these alarms with `is_active` field to 0
			require_masking.extend(((str(event[3])),str(item[0]),str(item[1].lower())) for item in mask_oid)
	return current_events,clear_events, require_masking

   def severity_mapping(self, bit):
	""" Maps int severity bit to corresponding char severity"""
	mapping = {
			'1': 'clear',
			'2': 'indeterminate',
			'3': 'critical',
			'4': 'major',
			'5': 'minor',
			'6': 'warning',
		    }

	return mapping.get(bit)
   def normalize_wimax_traps(self, traps, indexes,alarm_mask_oid):
	""" Parse out the formatline and converts the traps into 
	dict format"""
	# TODO: read the traps in dict format from MySQL using DictCursor cursor
	# TODO: remove the hard-coding on indexes here
	out = []
	new_trap = {}
	# keep track to remove dupli traps in same cycle
	#unique_trap_per_host = {}
	require_masking = []
        current_traps=[]
	clear_traps=[]
	redis_cnx = self.conn_base.redis_cnx(db_name='redis')
	for trap in traps:

		formatline = trap[-1].split('|')
		# key: (host, event_name, severity)
		#key = (
		#		trap[3], 
		#		formatline[indexes['event_name']],
		#		formatline[indexes['severity']]
		#		)
		#if key in unique_trap_per_host:
		#	continue
		#else:
		#	unique_trap_per_host[key] = 1

		try:
			severity  = self.severity_mapping(formatline[indexes['severity']])
			last_occurred = redis_cnx.get('traps:%s:%s:%s' \
					% (trap[3], formatline[indexes['event_name']].replace(' ','_'),severity))
                        if last_occurred :
                            last_occurred = datetime.strptime(last_occurred,'%Y-%m-%d %H:%M:%S')
                        else :
                            last_occurred = trap[8]

	                eventname = formatline[indexes['event_name']].replace(' ','_')
                        sia = sia_value[str(self.mat_entry_details['rf_ip_%s_%s' % (eventname,severity)]['sia'])]

			new_trap.update({
				'ip_address': trap[3],
				'device_name': self.inventory_info.get(trap[3]),
				'trapoid': trap[4],
				'eventname': formatline[indexes['event_name']].replace(' ','_'),
				'eventno': formatline[indexes['event_no']],
				'severity': severity,
				'uptime': trap[7],
				'traptime': trap[8],
				'last_occurred': last_occurred,
				'first_occurred': trap[8],
				'alarm_count': 1,
				'description': trap[-1],
				'is_active': 1,
				'sia': sia,
                                'customer_count': self.customer_count_details[str(trap[3])] 
						if str(trap[3]) in self.customer_count_details else None
				})

			if severity not in severity_for_clear_table:
				current_traps.append(new_trap)
			else:
				clear_traps.append(new_trap) 
		except IndexError as exc:
			continue

		#out.append(new_trap)
                eventname = formatline[indexes['event_name']]
		eventname = eventname.replace(' ','_')
		severity= self.severity_mapping(formatline[indexes['severity']])
		mask_oid = alarm_mask_oid.get((eventname,severity))
		if mask_oid:
			# update these alarms with `is_active` field to 0
			require_masking.extend((str(trap[3]),str(item[0]),str(item[1])) for item in mask_oid)
		new_trap = {}
	return current_traps,clear_traps,require_masking

   def process_events(self, events,alarm_mask_oid,flag=None):
	current_events,clear_events, require_masking = self.normalize_events(events, alarm_mask_oid,event_type=flag)
	# get traps which are not alive any more
	#mark_inactive = self.get_inactive_traps(require_masking, alarm_mask_oids)
	#print 'require_masking: {0}'.format(require_masking)
	#print 'mark_inactive: {0}'.format(mark_inactive)

	#if traps:
	#	export_traps = ExportTraps()
	#	export_traps.do_work(traps, mark_inactive=mark_inactive, 
	#			latest_id=self.latest_id)
	#	print 'Processed {0} pmp traps'.format(len(traps))
        return current_events,clear_events,require_masking

   def filter_wimax_traps(self, traps, device_type=None):
	""" Filters the traps based on device type"""
	filtered = [t for t in traps if 
			device_type in t[1].lower()]
	remaining = [t for t in traps if 
			device_type not in t[1].lower()]

	return filtered , remaining

   def filter_traps(self, traps):
	""" Starting point for processing all traps"""
	self.latest_id = traps[-1][0]
        current_traps=None
        clear_traps=None
        require_masking = None
	traps,alarm_count_dict  = self.make_unique_event_dict(traps)
	wimax_traps, other_traps = self.filter_wimax_traps(traps, device_type='wimax')
	#alarm_mask_oid = self.get_alarm_mask_oids()
	if wimax_traps:
		current_traps, clear_traps, require_masking = self.process_wimax_traps(wimax_traps, alarm_mask_oid)
		self.update_db(current_traps=current_traps, clear_traps=clear_traps, \
				require_masking=require_masking, flag='wimax_trap')

		#current_table_list,clear_table_list =self.segregate_events_for_tables(wimax_traps)
	if other_traps:
		current_traps,clear_traps,require_masking = self.process_events(other_traps,alarm_mask_oid,flag='trap')
		self.update_db(current_traps=current_traps,clear_traps=clear_traps,\
				require_masking=require_masking,flag='trap')
		
	self.update_trap_count(alarm_count_dict)

   def filter_events(self,events):
	""" starting point for processing all events"""
	#alarm_mask_oid = self.get_alarm_mask_oids()
	if events:
		events,alarm_count_dict = self.make_unique_event_dict(events,flag='event')
		current_events,clear_events,require_masking=self.process_events(events,alarm_mask_oid,flag='event')
		self.update_db(current_traps=current_events,clear_traps=clear_events,\
				require_masking=require_masking,flag='event')
		self.update_trap_count(alarm_count_dict)
   """
   def segregate_events_for_tables(self,event_list):
	# severity for Clear table
	#severity_for_clear_table = ['clear','ok']
	#current_table_list = [entry for entry in event_list if entry['severity'].lower() not in
	#			severity_for_clear_table ]
	#clear_table_list =  [entry_1 for entry_1 in event_list if entry_1 not in current_table_list  ]
	return current_table_list,clear_table_list
   """

   def process_wimax_traps(self, traps,alarm_mask_oid):
	""" Processing wimax specific traps bcz they have
	completely different structure"""
	# TODO: keep formatline configs in Redis cache
	global formatline_indexes
	indexes = formatline_indexes['wimax']

	# parse the formatline for each trap
	current_traps,clear_traps,require_masking = self.normalize_wimax_traps(traps, indexes,alarm_mask_oid)
	#alarm_mask_list = self.get_alarm_mask_oids(traps)
	return current_traps,clear_traps,require_masking

   def update_db(self,**kwargs):
	export_traps = ExportTraps()
	current_traps = kwargs['current_traps']
	clear_traps = kwargs['clear_traps']
	require_masking = kwargs['require_masking']
	flag = kwargs['flag']
	history_traps = kwargs['history_traps'] if 'history_traps' in kwargs else None

	if current_traps or clear_traps :
		export_traps.do_work(current_traps=current_traps, clear_traps=clear_traps, \
				mark_inactive=require_masking, latest_id=self.latest_id,\
				flag=flag,history_traps = history_traps)

		print 'Processed {0} current traps'.format(len(current_traps),len(clear_traps))

@app.task(name='load_customer_count_in_redis')
def load_customer_count_in_redis():
    """Store ODU/IDU customer count from MySQL to Redis DB"""
    conn_base = ConnectionBase()
    my_cnx = conn_base.mysql_cnx(db_name='application_db')
    cursor = my_cnx.cursor()
    query = """
            SELECT
                `Sector Config IP`,`Count Of Customer` 
	    FROM
		download_center_customer_count_ipaddress
	    """
    cursor.execute(query)
    customer_count_data = cursor.fetchall()
    cursor.close()
    try :
	redis_cnx = conn_base.redis_cnx(db_name='redis')
	p = redis_cnx.pipeline()
	for (sector_config_ip,customer_count) in customer_count_data:
	    p.set('customer_count:%s' % sector_config_ip,customer_count)
	    p.execute()
    except Exception,exc :
        print 'Error in writing customer count to redis: {0}'.format(exc)

@app.task(name='delete_history_trap')
def delete_history_trap():
    """Delete 3 months old trap after updating the alarm_count in current and clear tables"""
    current_date = datetime.now()
    current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0) 
    conn_base = ConnectionBase()
    my_cnx = conn_base.mysql_cnx(db_name='snmptt_db')
    cursor = my_cnx.cursor()
    
    current_update_query = """
	    UPDATE
        	 alert_center_currentalarms current  
	    INNER JOIN (
		SELECT
		    device_name,eventname,severity,count(history.alarm_count) AS count
		FROM
		     alert_center_historyalarms history 
		WHERE
		     history.severity NOT IN ('clear', 'ok ')
		    AND 
		    history.traptime BETWEEN DATE_SUB('{0}', INTERVAL 3 MONTH) AND '{0}'
		GROUP BY
		     history.device_name, history.eventname, history.severity
		    ) AS current_history
	    ON 
		current.device_name = current_history.device_name              
	    SET
		current.alarm_count = (current.alarm_count - current_history.count);
	    """.format(current_date)
    
    clear_update_query = """
	    UPDATE
		 alert_center_clearalarms clear  
	    INNER JOIN (
		SELECT
		    device_name,eventname,severity,count(history.alarm_count) AS count
		FROM
		     alert_center_historyalarms history 
		WHERE
		    history.severity IN ('clear', 'ok ')
		    AND 
		    history.traptime BETWEEN DATE_SUB('{0}', INTERVAL 3 MONTH) AND '{0}'
		GROUP BY
		     history.device_name, history.eventname, history.severity
		    ) AS clear_history
	    ON 
		clear.device_name = clear_history.device_name              
	    SET
		clear.alarm_count = (clear.alarm_count - clear_history.count);
	    """.format(current_date)
    
    delete_query = """
	    DELETE FROM
		alert_center_historyalarms
	    WHERE    
		traptime BETWEEN DATE_SUB('{0}', INTERVAL 3 MONTH) AND '{0}'; 
    	    """.format(current_date)
    
    try:
        cursor.execute(current_update_query)
    except (mysql.connector.Error) as exc:
        cursor.close()
        print 'Mysql Current Update Error', exc
    else:
        my_cnx.commit()
        
    try:
        cursor.execute(clear_update_query)
    except (mysql.connector.Error) as exc:
        cursor.close()
        print 'Mysql Clear Update Error', exc
    else:
        my_cnx.commit()    
    
    try:
        cursor.execute(delete_query)
    except (mysql.connector.Error) as exc:
        cursor.close()
        print 'Mysql History Update Error', exc
    else:
        my_cnx.commit() 
         
    cursor.close()
    my_cnx.close()

