import operator
from db_conn import ConnectionBase, ExportTraps
from collections import defaultdict
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
class Eventmapper(object):
   def __init__(self):
	self.conn_base = ConnectionBase()
	# read inventory info from redis [ip --> name mappings]
	self.inventory_info = self.read_cached_inventory()

	# `id` of the most latest row read from MySQL
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

	event_dict = {}
	#sorted_traps = sorted(traps.items(),key=operator.itemgetter(0))
	global alarm_mask_oid
	global mat_entries
	mat_entries =  self.get_mapped_mat_entries()
	alarm_mask_oid = self.get_alarm_mask_oids()
        mask_oid_key = None 	
	mat_entry = None
	for event in events :
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
	        else:
		    event_dict[unique_key] = event
	    else :
		print "Not mapped in MAT : ",mat_entry
	return event_dict.values()

   def normalize_events(self, events, alarm_mask_oid,event_type=None):
	""" Convert the traps to compatible schema"""
	out = []
	# these traps have current/clear traps associated with them
	require_masking = []
	# severity for Clear table
	current_events =[]
	clear_events = []
	#print "normalize_events"
	for event in events:
		mask_oid = None
		new_event = {}
		try:
			new_event.update({
				'ip_address': str(event[3]),
				'device_name': self.inventory_info.get(event[3]),
				'trapoid': str(event[4]),
				'eventname': str(event[1]),
				'eventno': str(event[2]),
				'severity': event[6].lower(),
				'uptime': event[7],
				'traptime': event[8],
				'last_occurred': event[8],
				'first_occurred': event[8],
				'alarm_count': 1,
				'description': event[-1],
				'is_active': 1,
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
			# ip,(traipoid or eventname),severity
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
			new_trap.update({
				'ip_address': trap[3],
				'device_name': self.inventory_info.get(trap[3]),
				'trapoid': trap[4],
				'eventname': formatline[indexes['event_name']].replace(' ','_'),
				'eventno': formatline[indexes['event_no']],
				'severity': severity,
				'uptime': trap[7],
				'traptime': trap[8],
				'last_occurred': trap[8],
				'first_occurred': trap[8],
				'alarm_count': 1,
				'description': trap[-1],
				'is_active': 1
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
	#print "traps.........."
	#print traps
	self.latest_id = traps[-1][0]
        current_traps=None
        clear_traps=None
        require_masking = None
	#print '........len of traps....'
	#print traps
	traps = self.make_unique_event_dict(traps)
	#print '........len of unique event....'
	#print traps
	wimax_traps, other_traps = self.filter_wimax_traps(traps, device_type='wimax')
	#alarm_mask_oid = self.get_alarm_mask_oids()
	#print 'alarm mask oid'
	#print alarm_mask_oid
	if wimax_traps:
		#print 'inwimax trap'
		current_traps,clear_traps,require_masking = self.process_wimax_traps(wimax_traps,alarm_mask_oid)
                #print 'wimax...require masking'
                #print require_masking
		#print current_traps,clear_traps
		# update db based on Current,clear alarms
		self.update_db(current_traps=current_traps,clear_traps=clear_traps,require_masking=require_masking,flag='wimax_trap')
		#current_table_list,clear_table_list =self.segregate_events_for_tables(wimax_traps)
	if other_traps:
		current_traps,clear_traps,require_masking = self.process_events(other_traps,alarm_mask_oid,flag='trap')
                #print 'pmp...require masking'
                #print require_masking
		self.update_db(current_traps=current_traps,clear_traps=clear_traps,require_masking=require_masking,flag='trap')
		
		#print '...........................CURRENT>>>>>>>>>>>>>>>>>>'
		#print current_traps
		#print '...........................CLEAR>>>>>>>>>>>>>>>>>>'
		#print clear_traps
		#print require_masking

   def filter_events(self,events):
	""" starting point for processing all events"""
	#alarm_mask_oid = self.get_alarm_mask_oids()
	if events:
		events = self.make_unique_event_dict(events,flag='event')
		current_events,clear_events,require_masking=self.process_events(events,alarm_mask_oid,flag='event')
                #print '...require masking'
                #print require_masking
		self.update_db(current_traps=current_events,clear_traps=clear_events,require_masking=require_masking,flag='event')
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

   def update_db(self,current_traps=None,clear_traps=None,require_masking=None,flag=None):
	export_traps = ExportTraps()
	if current_traps or clear_traps:
		export_traps.do_work(current_traps=current_traps, clear_traps=clear_traps, mark_inactive=require_masking, latest_id=self.latest_id,flag=flag)
		print 'Processed {0} current traps'.format(len(current_traps),len(clear_traps))




	   



