from datetime import datetime
import operator
#from db_conn import ConnectionBase, ExportTraps
from collections import defaultdict
#import imp
import re
# changed module for production
from trap_handler.db_conn import ConnectionBase, ExportTraps
from start.start import app
#start_app_module = imp.load_source('start_pub', '/omd/sites/ospf1_slave_1/lib/python/start_pub.py')
#app = start_app_module.app
from copy import deepcopy
from time import sleep
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
info, warning, error = logger.info, logger.warning, logger.error


severity_for_clear_table = ['clear','ok']
global alarm_mask_oid
global mat_entries
global monolith_ticket_dict
global correlated_trap_alarm_id
global alarms_to_forward_to_monolith
global alarm_mask_alarm_name

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

technology = {
        'wimax' : 'wimax',
        'pmp' : 'pmp',
        'radwin5k' : 'rad5k',
        'converter' : 'converter',
}


include_in_redis_event = [ "PD_threshold_breach_major",\
                           "Device_not_reachable",\
                         ]

exclude_in_correlation = [ "Latency_Threshold_Breach_major",\
			   "Latency_Threshold_Breach_warning",\
			   "PD_threshold_breach_warning",\
                           "Uplink_Issue_threshold_Breach",\
                        ]

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
		logger.error('Error in reading cached inventory: {0}'.format(exc))
		#print 'Error in reading cached inventory: {0}'.format(exc)

	return out[0]

   def read_mat_entries(self):
	redis_cnx = self.conn_base.redis_cnx(db_name='redis_MAT')
	mat_entry_details = {}
        try:
                mat_alarms = eval(redis_cnx.get('mat_data'))
                for alarms , data in mat_alarms.items() :
                        mat_entry_details[alarms] = data
        except Exception as exc:
                mat_entry_details = {}
		logger.error('Error in reading MAT: {0}'.format(exc))
                #print 'Error in reading MAT: {0}'.format(exc)
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
		logger.error('Error in reading customer count from redis: {0}'.format(exc))
  		#print 'Error in reading customer count from redis: {0}'.format(exc)
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
	try:
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
        except Exception ,e :
		logger.error("Error in get_alarm_mask_oids : %s ", str(e))
                #print "Error in get_alarm_mask_oids : %s "% str(e)
        finally:
                if cursor :
                        cursor.close()
                        my_cnx.close()

	return  alarm_masking_dict

   def get_alarm_mask_alarm_name(self):
        """ For every current trap, adds its corresponding clear trap
        and vice-versa"""
        alarm_mask_alarm_dict = defaultdict(list)
        query = """
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

        """
        my_cnx = self.conn_base.mysql_cnx(db_name='snmptt_db')
        cursor = my_cnx.cursor()
        cursor.execute(query)
        alarm_mask_data = cursor.fetchall()
        for (name,severity,mask_name,mask_severity) in alarm_mask_data:
                alarm_mask_alarm_dict[(name,severity)].append((mask_name,mask_severity))
        return  alarm_mask_alarm_dict

   def get_mapped_mat_entries(self):
        """ Mapped MAT entries"""
        mat_entries = []
        query_1 = """
        SELECT
                alarm_name, severity
        FROM
                master_alarm_table
        WHERE
                device_type in ('wimax')
        """
        qry = """
        SELECT
                oid, severity
        FROM
                master_alarm_table
        WHERE
                device_type not in ('wimax')
        """
        try :
                my_cnx = self.conn_base.mysql_cnx(db_name='snmptt_db')
                cursor = my_cnx.cursor()
                cursor.execute(query_1)
                wimax_mat_entries = [(item[0],item[1]) for item in cursor.fetchall()]
                cursor.execute(qry)
                other_traps_mat_entries = [(item[0],item[1]) for item in cursor.fetchall()]
                mat_entries = wimax_mat_entries
                mat_entries.extend(other_traps_mat_entries)
                mat_entries = set(mat_entries)
        except Exception ,e :
                #print "Error in get_mapped_mat_entries : %s "% str(e)
		logger.error("Error in get_mapped_mat_entries : %s ", str(e))
        finally:
                if cursor :
                        cursor.close()
                        my_cnx.close()

        return mat_entries

   def get_alarms_to_forward_to_monolith(self):
        """ Mapped MAT entries for which alarm has to be forwarded to monolith"""
        alarms_to_forward_to_monolith = []
        query = """
        SELECT
                alarm_name, severity
        FROM
                master_alarm_table
        WHERE
                alarm_forward_to_monolith = 1
        """
        my_cnx = self.conn_base.mysql_cnx(db_name='snmptt_db')
        cursor = my_cnx.cursor()
        cursor.execute(query)
        alarms_to_forward_to_monolith = [(item[0],item[1]) for item in cursor.fetchall()]
        #print "alarms_to_forward_to_monolith",alarms_to_forward_to_monolith
        return alarms_to_forward_to_monolith


   def make_unique_event_dict(self,events,flag=None):
        # Sample trap entry
        # (222026, u'RAD5K_hbsEncryptionClear', u'.1.3.6.1.4.1.4458.1000.0.237', u'10.172.207.71', 
        #  u'.1.3.6.1.4.1.4458.1000.0.237', u'Status Events', u'clear', u'103:16:56:09.00',
        #datetime.datetime(2016, 1, 22, 11, 24, 53))
        redis_cnx = self.conn_base.redis_cnx(db_name='redis')
        event_dict = {}
        event_count_dict = {}
        monolith_ticket_traps = []
        #sorted_traps = sorted(traps.items(),key=operator.itemgetter(0))
        global alarm_mask_oid
        global mat_entries
	global alarms_to_forward_to_monolith
	global alarm_mask_alarm_name
        mat_entries =  self.get_mapped_mat_entries()
	alarms_to_forward_to_monolith = self.get_alarms_to_forward_to_monolith()
	alarm_mask_alarm_name = self.get_alarm_mask_alarm_name()
        alarm_mask_oid = self.get_alarm_mask_oids()
        mask_oid_key = None
        mat_entry = None
        not_mapped = []
        for event in events :
            alarm_name = str(event[1])
            if flag == 'event' :
                unique_key = (event[1],event[3])
            elif 'wimax_trap' in event[1].lower():
                global formatline_indexes
                indexes = formatline_indexes['wimax']
                formatline = event[-1].split('|')
                #alarm_name = formatline[indexes['event_name']].replace(' ','_')
                alarm_name = re.sub('[: ]', '_', formatline[indexes['event_name']])
                unique_key = (alarm_name,event[3])
            elif 'monolithticket' in alarm_name.lower():
                monolith_ticket_traps.append(event)
		continue
            else:
                unique_key = (event[2],event[3])
            mat_entry = (unique_key[0],event[6].lower())
            event_unique_key = (unique_key[0],unique_key[1],event[6].lower())
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
                        event_count_dict[event_unique_key][1] = event
                else:
                    event_dict[unique_key] = event
                    # Dictionary to store event count
                    if  event_unique_key in event_count_dict.keys() :
                        key = 'traps:%s:%s:%s' % (event_unique_key[1],alarm_name,event[6].lower())
                        redis_cnx.set(key,event_count_dict[event_unique_key][1][8])
                        event_count_dict[event_unique_key] = [event_count_dict[event_unique_key][0] + 1 , event]
                    elif event_unique_key not in event_count_dict.keys():
                        event_count_dict[event_unique_key] = [1,event]
            else :
                not_mapped.append(mat_entry)
        if not_mapped:
                #print "Not mapped in MAT : ",not_mapped
		logger.error("Not mapped in MAT : %s",str(not_mapped))
        return (event_dict.values(),monolith_ticket_traps,event_count_dict)

   def delete_cleared_monolith_ticket(self,ip_address,eventname):
	"""Delete tickets from monolith_ticket:IP redis dict"""
	redis_cnx_mat = self.conn_base.redis_cnx(db_name='redis_MAT')
	monolith_ticket_entry = eval(redis_cnx_mat.get('monolith_ticket:%s' %ip_address))
	monolith_ticket_entry.pop(eventname, None)
	redis_cnx_mat.set('monolith_ticket:%s' %ip_address,monolith_ticket_entry)
	
   def get_monolith_ticket_dict(self):
	"""Fetch tickets from monolith_ticket:IP redis dict"""
	monolith_ticket = {}
	redis_cnx_mat = self.conn_base.redis_cnx(db_name='redis_MAT')
	monolith_ticket_number_ip = redis_cnx_mat.keys('monolith_ticket:*')
	if monolith_ticket_number_ip:
	    for ip in monolith_ticket_number_ip :
            	monolith_ticket[ip.split(':')[1]] = eval(redis_cnx_mat.get(ip))
	return monolith_ticket

   def get_correlated_trap_alarm_id(self):
	"""Fetch correlated_trap from correlated_traps redis hash"""
	correlated_trap = {}
	redis_cnx_mat = self.conn_base.redis_cnx(db_name='redis_MAT')
	correlated_trap_data = redis_cnx_mat.hgetall('correlated_traps')
	if correlated_trap_data :
	    for key,value in correlated_trap_data.iteritems():
	    	correlated_trap[key] = eval(value)['alrm_id']
	return correlated_trap

   def return_ticket_details(self,ip_address,eventname,severity):
	"""Fetch Alarm Id, Ticket Number, Manual trap bit for particular IP Address and Eventname"""
	mask_key = alarm_mask_alarm_name.get((eventname,severity.lower()))
        mask_eventname,mask_severity = mask_key[0]
        if severity in severity_for_clear_table :
            try :
                alarm_id = monolith_ticket_dict[ip_address][mask_eventname]['alarm_id']
		ticket_number = monolith_ticket_dict[ip_address][mask_eventname]['ticket_number']
		is_manual =  monolith_ticket_dict[ip_address][mask_eventname]['is_manual']
		self.delete_cleared_monolith_ticket(ip_address,mask_eventname)
            except Exception,e :
		print "Exception in fetch alarm_id in mapper: %s"%str(e) 
                ticket_number = None
		"""
		try :
		    alarm_id = correlated_trap_alarm_id[ip_address+'_'+eventname] 
		except Exception,e :
                    alarm_id = None
		"""
	else :
	    ticket_number = None
	    alarm_id = None
	    is_manual = None
        return (ticket_number,alarm_id,is_manual)

   def update_trap_count(self,event_count_dict):
        """Update trap count field using event_count_dict"""
        redis_cnx_mat = self.conn_base.redis_cnx(db_name='redis_MAT')
        redis_cnx = self.conn_base.redis_cnx(db_name='redis')
        current_events_update = []
        clear_events_update = []
        traps_events_update = []
        history_event = []
        redis_event_entry = []
        redis_trap_entry = []
	global monolith_ticket_dict
	monolith_ticket_dict = self.get_monolith_ticket_dict()
	#global correlated_trap_alarm_id
	#correlated_trap_alarm_id = self.get_correlated_trap_alarm_id()
        for count,trap in event_count_dict.values():
            new_trap =  {}
            if 'wimax' in trap[1].lower() :
                global formatline_indexes
                indexes = formatline_indexes['wimax']
                formatline = trap[-1].split('|')
                severity  = self.severity_mapping(formatline[indexes['severity']])
                try:
                    last_occurred =  redis_cnx.get('traps:%s:%s:%s' % (trap[3],\
                                         formatline[indexes['event_name']].replace(' ','_'),severity))
                    last_occurred = datetime.strptime(last_occurred,'%Y-%m-%d %H:%M:%S')
                except :
                    last_occurred = trap[8]
                eventname = re.sub('[: ]', '_', formatline[indexes['event_name']])
		ticket_number, alarm_id, is_manual = self.return_ticket_details(trap[3],eventname,severity)	
                try:
                    sia = sia_value[str(self.mat_entry_details[(eventname,severity)]['sia'])]
                    device_type = technology[str(self.mat_entry_details[(eventname,severity)]['device_type']).lower()]

                except Exception,e:
                    #print e
                    sia = ''
                    device_type = ''

                new_trap.update({
                                'ip_address': trap[3],
                                'device_name': self.inventory_info.get(trap[3]) if self.inventory_info.get(trap[3]) is not None else '',
                                'trapoid': trap[4],
                                'eventname': eventname,
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
                                                if str(trap[3]) in self.customer_count_details else None,
                                'technology': device_type,
				'ticket_number' : None,
				'alarm_id' : None,
				'is_manual' : None
                                })
            else :
                severity  = trap[6].lower()
                try:
                    last_occurred = redis_cnx.get('traps:%s:%s:%s' % (str(trap[3]), str(trap[1]),severity))
                    last_occurred = datetime.strptime(last_occurred,'%Y-%m-%d %H:%M:%S')
                except :
                    last_occurred = trap[8]
                eventname =  str(trap[1])
		ticket_number , alarm_id, is_manual = self.return_ticket_details(trap[3],eventname,severity)
                try :
                        if 'PMP_' in eventname :
                            sia = sia_value[str(self.mat_entry_details[(eventname.split('_')[1],severity)]['sia'])]
                            device_type = technology[str(self.mat_entry_details[(eventname.split('_')[1],severity)]['device_type']).lower()]
                        else :
                            sia = sia_value[str(self.mat_entry_details[(eventname,severity)]['sia'])]
                            device_type = technology[str(self.mat_entry_details[(eventname,severity)]['device_type']).lower()]

                except Exception,e:
                        #print e
                        sia = ''
                        device_type = ''
                new_trap.update({
                                'ip_address': str(trap[3]),
                                'device_name': self.inventory_info.get(trap[3]) if self.inventory_info.get(trap[3]) is not None else '',
                                'trapoid': str(trap[4]),
                                'eventname': eventname,
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
                                                if str(trap[3]) in self.customer_count_details else None,
                                'technology':device_type,
				'ticket_number' : None,
				'alarm_id' : None,
				'is_manual' : None
                                })
            trap = ()
            #if new_trap['eventname'] not in exclude_in_redis_event :
            if new_trap and (new_trap['eventname'],new_trap['severity']) in alarms_to_forward_to_monolith:
                trap = (
                '',
                new_trap['eventname'],
                new_trap['eventno'],
                new_trap['ip_address'],
                new_trap['trapoid'],
                '',
                new_trap['severity'],
                new_trap['uptime'],
                new_trap['traptime'].strftime("%Y-%m-%d %H:%M:%S") if type(new_trap['traptime']) is not str else new_trap['traptime'],
                new_trap['description']
                )
                if new_trap['eventname'] in include_in_redis_event :
                        redis_event_entry.append(trap)
                else :
                        redis_trap_entry.append(trap)


            if severity.lower() not in severity_for_clear_table:
                current_events_update.append(new_trap)
            else:
		new_trap['ticket_number'] = ticket_number
		new_trap['alarm_id'] = alarm_id
		new_trap['is_manual'] = is_manual
                clear_events_update.append(new_trap)
            history_trap = deepcopy(new_trap)
            # Update is_active to 1 in history records
            history_trap['is_active'] = 1
            history_trap['last_occurred'] = history_trap['first_occurred']

            # Update redis key for next polling cycle last_occurred value
            key = 'traps:%s:%s:%s' % (new_trap['ip_address'],new_trap['eventname'],new_trap['severity'])
            redis_cnx.set(key,str(new_trap['traptime']))
            history_event.append(history_trap)

        if redis_event_entry:
            #logger.error('redis_event_entry {0}'.format(redis_event_entry))
            redis_cnx_mat.rpush('queue:events',*redis_event_entry)
        if redis_trap_entry:
            redis_cnx_mat.rpush('queue:traps', *redis_trap_entry)

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
                        try :
                                last_occurred = redis_cnx.get('traps:%s:%s:%s' % \
                                        (str(event[3]), str(event[1]),event[6].lower()))
                                last_occurred = datetime.strptime(last_occurred,'%Y-%m-%d %H:%M:%S')
                        except :
                                last_occurred = event[8]

                        eventname =  str(event[1])
			ticket_number , alarm_id , is_manual = self.return_ticket_details(str(event[3]),eventname,event[6].lower())
                        try :
                                if 'PMP_' in eventname :
                                    sia = sia_value[str(self.mat_entry_details[(eventname.split('_')[1],event[6].lower())]['sia'])]
                                    device_type = technology[str(self.mat_entry_details[(eventname.split('_')[1],event[6].lower())]['device_type']).lower()]
                                else :
                                    sia = sia_value[str(self.mat_entry_details[(eventname,event[6].lower())]['sia'])]
                                    device_type = technology[str(self.mat_entry_details[(eventname,event[6].lower())]['device_type']).lower()]
                        except Exception,e:
                                #print "EventName doesn't match with mapped EventName",e
                                sia = ''
                                device_type = ''

                        new_event.update({
                                'ip_address': str(event[3]),
                                'device_name': self.inventory_info.get(event[3]) if self.inventory_info.get(event[3]) is not None else '',
                                'trapoid': str(event[4]),
                                'eventname': eventname,
                                'eventno': str(event[2]),
                                'severity': event[6].lower(),
                                'uptime': event[7],
                                'traptime': event[8],
                                'last_occurred': last_occurred,
                                'first_occurred': last_occurred,
                                'alarm_count': 0,
                                'description': event[-1],
                                'is_active': 1,
                                'sia': sia,
                                'customer_count': self.customer_count_details[str(event[3])]
						 if str(event[3]) in self.customer_count_details else None,
                                'technology': device_type
				})
			if event[6].lower() not in severity_for_clear_table:
				new_event['ticket_number'] = None
				new_event['alarm_id'] = None
                                new_event['is_manual'] = None
				current_events.append(new_event)
			else:
				new_event['ticket_number'] = ticket_number
				new_event['alarm_id'] = alarm_id
                                new_event['is_manual'] = None
				clear_events.append(new_event)
		except Exception as exc:
			#print 'Exc in normalize traps: {0}'.format(exc)
			logger.error('Exc in normalize traps: {0}'.format(exc))
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
			try :
			    last_occurred = redis_cnx.get('traps:%s:%s:%s' \
					% (trap[3], formatline[indexes['event_name']].replace(' ','_'),severity))
                            last_occurred = datetime.strptime(last_occurred,'%Y-%m-%d %H:%M:%S')
                        except :
                            last_occurred = trap[8]

                        eventname = re.sub('[: ]', '_', formatline[indexes['event_name']])
			ticket_number, alarm_id, is_manual = self.return_ticket_details(trap[3],eventname,severity)
                        try :
                            sia = sia_value[str(self.mat_entry_details[(eventname,severity)]['sia'])]
                            device_type = technology[str(self.mat_entry_details[(eventname,severity)]['device_type']).lower()]
                        except Exception,e:
                            print e
                            sia = 'NA'
                            device_type = ''

                        new_trap.update({
                                'ip_address': trap[3],
                                'device_name': self.inventory_info.get(trap[3]) if self.inventory_info.get(trap[3]) is not None else '',
                                'trapoid': trap[4],
                                'eventname': eventname,
                                'eventno': formatline[indexes['event_no']],
                                'severity': severity,
                                'uptime': trap[7],
                                'traptime': trap[8],
                                'last_occurred': last_occurred,
                                'first_occurred': last_occurred,
                                'alarm_count': 0,
                                'description': trap[-1],
                                'is_active': 1,
                                'sia': sia,
                                'customer_count': self.customer_count_details[str(trap[3])]
                                                if str(trap[3]) in self.customer_count_details else None,
                                'technology': device_type
                                })

			if severity not in severity_for_clear_table:
				new_trap['ticket_number'] = None
				new_trap['alarm_id'] = None
                                new_trap['is_manual'] = None
				current_traps.append(new_trap)
			else:
                                new_trap['ticket_number'] = ticket_number
                                new_trap['alarm_id'] = alarm_id
                                new_trap['is_manual'] = None
				clear_traps.append(new_trap)
		except IndexError as exc:
			continue

                #out.append(new_trap)
                eventname = re.sub('[: ]', '_', formatline[indexes['event_name']])
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

	return (filtered, remaining)

   def filter_traps(self, traps):
	""" Starting point for processing all traps"""
	self.latest_id = traps[-1][0]
        current_traps=None
        clear_traps=None
        require_masking = None
        traps,monolith_ticket_traps,alarm_count_dict  = self.make_unique_event_dict(traps)
	if not traps and monolith_ticket_traps :
		 self.update_db(current_traps=None,clear_traps=None,\
                                require_masking=None,flag='monolith_trap')
        #logger.error('Monolith filter_traps {0}'.format(monolith_ticket_traps))
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

        # Traps from monolith for RF-IP correlation module
        if monolith_ticket_traps:
		redis_cnx_mat = self.conn_base.redis_cnx(db_name='redis_MAT')
                #logger.error("Monolith_ticket_traps {0}".format(monolith_ticket_traps))
                #logger.error("chanish : monolith_ticket_traps {0}".format(monolith_ticket_traps))
                traps = self.process_deviceticket(monolith_ticket_traps)
		"""
                table = 'device_deviceticket'
                columns = ('ip_address','alarm_id')
                p0 = "UPDATE  device_deviceticket SET ticket_number= %(ticket_number)s WHERE "
                p2 = ' and '.join(map(lambda x: x+'= %('+ x + ')s', columns))
                query_for_device_deviceticket = ''.join([p0,p2])
		"""
                #logger.error('Query device_deviceticket : {0}'.format(query_for_device_deviceticket))
		query_current_alarm  =  'UPDATE alert_center_currentalarms SET ticket_number = %(ticket_number)s \
                                	where alarm_id = %(alarm_id)s'

		query_clear_alarm  =  	'UPDATE alert_center_clearalarms SET ticket_number = %(ticket_number)s \
                                	where alarm_id = %(alarm_id)s'

        	query_history_alarm  =  'UPDATE alert_center_historyalarms SET ticket_number = %(ticket_number)s \
					where alarm_id = %(alarm_id)s'

		export_traps = ExportTraps()
		monolith_tickets_ip = redis_cnx_mat.keys('monolith_ticket:*')
		monolith_ticket = {}
                if traps:
		    for each_trap in traps:
                        try:
                            # Store the Ticket and other information on application database.
			    """
                            try :
			        export_traps.exec_qry(query_for_device_deviceticket, each_trap, False, db_name='application_db')
			    except Exception,e :
			        print "Error in query for device_deviceticket %s",query_for_device_deviceticket
			    """
			    export_traps.exec_qry(query_current_alarm, each_trap, False, db_name='snmptt_db')
			    export_traps.exec_qry(query_history_alarm, each_trap, False,db_name='snmptt_db')

			    affected_row_count = export_traps.exec_qry(query_clear_alarm, each_trap, False, db_name='snmptt_db')

			    print "affected_row_count" ,affected_row_count
			    if affected_row_count == 0 :
				ip_address = each_trap.get('ip_address')
				eventname =  re.sub('[: ]', '_', each_trap.get('eventname'))
				ticket_number = each_trap.get('ticket_number')
				alarm_id = each_trap.get('alarm_id')
				print "ticket number: %s"%str(ticket_number)

				#alarm_id = each_trap.get('alarm_id')
				if 'monolith_ticket:' + ip_address in monolith_tickets_ip :
				    monolith_ticket = eval(redis_cnx_mat.get('monolith_ticket:' + ip_address))
				    monolith_ticket[eventname]['ticket_number'] = ticket_number
				redis_cnx_mat.set('monolith_ticket:' + ip_address, monolith_ticket)
			
                        except Exception as exc:
                                inserted = False
                                #logger.error('chanish : Exc in mysql trap insert: {0}'.format(exc))

   def process_deviceticket(self,monolith_traps):
        traps = []
        for t in monolith_traps:
            trap_dict = {}
            formatline = t[-1].split('|')
            if formatline:
                #TODO: Replace formatline index with actual index coming from monolith traps.
                trap_dict['ip_address'] = formatline[4]
                trap_dict['ticket_number'] = formatline[3]
                trap_dict['alarm_id'] = formatline[2]
		trap_dict['eventname'] = "PD threshold breach major" if formatline[0] == "PD threshold breach" \
					else formatline[0]
                traps.append(trap_dict)
        #logger.error('chanish : ticket information from snmptt table {0}'.format(traps))
        return traps


   def filter_events(self,events):
	""" starting point for processing all events"""
	#alarm_mask_oid = self.get_alarm_mask_oids()
	if events:
		events,mono,alarm_count_dict = self.make_unique_event_dict(events,flag='event')
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

		print 'Processed {0} current traps, {1} clear traps'.format(len(current_traps),len(clear_traps))
	elif flag is 'monolith_trap':
		export_traps.do_work(current_traps=current_traps, clear_traps=clear_traps, \
                                mark_inactive=require_masking, latest_id=self.latest_id,\
                                flag='monolith_trap',history_traps = history_traps)
	print 'Processed monolith traps; last processed id : {0}'.format(self.latest_id)

@app.task(name='load_customer_count_in_redis')
def load_customer_count_in_redis():
    """Store ODU/IDU customer count from MySQL to Redis DB"""
    conn_base = ConnectionBase()
    my_cnx = conn_base.mysql_cnx(db_name='application_db')
    cursor = my_cnx.cursor()
    query = """
            SELECT
                `sector_config_ip`,`count_of_customer`
            FROM
                download_center_customer_count_ipaddress
            """
    try:
        cursor.execute(query)
        customer_count_data = cursor.fetchall()
    except Exception ,e:
        #print "MySQL exception : %s" % e
	logger.error("MySQL exception : %s", e)
        cursor.close()
    try :
	redis_cnx = conn_base.redis_cnx(db_name='redis')
	p = redis_cnx.pipeline()
	for (sector_config_ip,customer_count) in customer_count_data:
	    p.set('customer_count:%s' % sector_config_ip,customer_count)
	    p.execute()
    except Exception,exc :
        #print 'Error in writing customer count to redis: {0}'.format(exc)
	logger.error('Error in writing customer count to redis: {0}'.format(exc))

@app.task(name='delete_history_trap')
def delete_history_trap():
    """Delete 3 months old trap after updating the alarm_count in current and clear tables"""
    current_date = datetime.now()
    current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    conn_base = ConnectionBase()
    my_cnx = conn_base.mysql_cnx(db_name='snmptt_db')
    cursor = my_cnx.cursor()
    delete_current_entry = True
    delete_clear_entry = True

    current_count_update_query = """
        UPDATE
            alert_center_currentalarms current
        INNER JOIN (
            SELECT
                ip_address, eventname,severity, SUM(history.alarm_count) AS count
            FROM
                alert_center_historyalarms history
            WHERE
                history.severity NOT IN ('clear', 'ok') and history.eventname not in ('PD_threshold_breach',
                 'Device_not_reachable','Latency_Threshold_Breach', 'Uplink_Issue_threshold_Breach')
                AND
                history.traptime < DATE_SUB('{0}', INTERVAL 3 MONTH)
            GROUP BY
                history.ip_address, history.eventname, history.severity
            ) AS current_history
        ON
            current.ip_address = current_history.ip_address and current.eventname = current_history.eventname
            and current.severity = current_history.severity
        SET
            current.alarm_count = current.alarm_count - current_history.count
        WHERE
            current.is_active = 0
            and current.traptime > DATE_SUB('{0}', INTERVAL 3 MONTH);
        """.format(current_date)

    clear_count_update_query = """
        UPDATE
            alert_center_clearalarms clear
        INNER JOIN (
            SELECT
                ip_address, eventname, severity, SUM(history.alarm_count) AS count
            FROM
                alert_center_historyalarms history
            WHERE
                history.severity IN ('clear', 'ok')
                AND
                history.traptime < DATE_SUB('{0}', INTERVAL 3 MONTH)
                AND
                history.eventname not in ('PD_threshold_breach', 'Device_not_reachable',
                'Latency_Threshold_Breach', 'Uplink_Issue_threshold_Breach')
            GROUP BY
                history.ip_address, history.eventname, history.severity
            ) AS clear_history
        ON
            clear.ip_address = clear_history.ip_address and clear.eventname = clear_history.eventname
            and clear.severity = clear_history.severity
        SET
            clear.alarm_count = (clear.alarm_count - clear_history.count)
        WHERE
            clear.traptime > DATE_SUB('{0}', INTERVAL 3 MONTH);
        """.format(current_date)

    clear_time_update_query = """
        UPDATE
            alert_center_clearalarms clear_alarm
        INNER JOIN (
            SELECT
                ip_address, eventname, severity, MIN(traptime) as history_traptime
            FROM
                alert_center_historyalarms history
            WHERE
                history.severity IN ('clear','ok')  AND history.traptime > DATE_SUB('{0}', INTERVAL 3 MONTH)
                AND history.eventname not in ('PD_threshold_breach', 'Device_not_reachable',
                'Latency_Threshold_Breach', 'Uplink_Issue_threshold_Breach')
            GROUP BY
                history.ip_address, history.eventname, history.severity
            )clear
        ON
            clear_alarm.ip_address = clear.ip_address and clear_alarm.eventname = clear.eventname
            and clear_alarm.severity = clear.severity
        SET
            clear_alarm.first_occurred = clear.history_traptime ,
            clear_alarm.last_occurred = if(clear_alarm.last_occurred < DATE_SUB('{0}', INTERVAL 3 MONTH), clear.history_traptime, clear_alarm.last_occurred)
        WHERE
            clear_alarm.first_occurred < DATE_SUB('{0}', INTERVAL 3 MONTH) ;
        """.format(current_date)

    current_time_update_query = """
        UPDATE
            alert_center_currentalarms current_alarm
        INNER JOIN (
            SELECT
                ip_address, eventname, severity, MIN(traptime) as history_traptime
            FROM
                alert_center_historyalarms history_current
            WHERE
                history_current.severity NOT IN ('clear','ok')  AND history_current.traptime > DATE_SUB('{0}', INTERVAL 3 MONTH)
                AND history_current.eventname not in ('PD_threshold_breach', 'Device_not_reachable',
                'Latency_Threshold_Breach', 'Uplink_Issue_threshold_Breach')
            GROUP BY
                history_current.ip_address, history_current.eventname, history_current.severity
            )current
        ON
            current_alarm.ip_address = current.ip_address and current_alarm.eventname = current.eventname
            and current_alarm.severity = current.severity
        SET
            current_alarm.first_occurred = current.history_traptime,
            current_alarm.last_occurred = if(current_alarm.last_occurred < DATE_SUB('{0}', INTERVAL 3 MONTH),
            current.history_traptime,
            current_alarm.last_occurred
            )
        WHERE
            current_alarm.is_active = 0 and
            current_alarm.first_occurred < DATE_SUB('{0}', INTERVAL 3 MONTH) ;
        """.format(current_date)

    delete_query_clearhistory = """
        DELETE FROM
            alert_center_historyalarms
        WHERE
            traptime < DATE_SUB('{0}', INTERVAL 3 MONTH) AND severity IN ('clear', 'ok')
            AND eventname not in ('PD_threshold_breach', 'Device_not_reachable',
            'Latency_Threshold_Breach', 'Uplink_Issue_threshold_Breach');
        """.format(current_date)

    delete_query_currenthistory = """
        DELETE FROM
             alert_center_historyalarms
        WHERE id
        IN
        (SELECT history.id FROM
            alert_center_currentalarms cur
        INNER JOIN(
            SELECT
                id, ip_address, eventname, severity, traptime
            FROM
                alert_center_historyalarms historyalarms
            WHERE
                historyalarms.traptime < DATE_SUB('{0}', INTERVAL 3 MONTH)
            ) history
        ON
            history.ip_address = cur.ip_address and history.eventname = cur.eventname
            AND history.severity = cur.severity
        WHERE
            cur.is_active=0
            AND cur.eventname NOT IN ('PD_threshold_breach', 'Device_not_reachable',
             'Latency_Threshold_Breach', 'Uplink_Issue_threshold_Breach'));
                """.format(current_date)

    current_delete_query = """
        DELETE FROM
            alert_center_currentalarms
        WHERE
            traptime < DATE_SUB('{0}', INTERVAL 3 MONTH) AND is_active = 0
            AND eventname not in ('PD_threshold_breach', 'Device_not_reachable',
            'Latency_Threshold_Breach', 'Uplink_Issue_threshold_Breach');
        """.format(current_date)

    clear_delete_query = """
        DELETE FROM
            alert_center_clearalarms
        WHERE
            traptime < DATE_SUB('{0}', INTERVAL 3 MONTH)
            AND eventname not in ('PD_threshold_breach', 'Device_not_reachable',
            'Latency_Threshold_Breach', 'Uplink_Issue_threshold_Breach');
        """.format(current_date)

    try:
        cursor.execute(current_count_update_query)
    except Exception, exc:
        cursor.close()
        delete_current_entry = False
        #print 'Mysql Current Alarm Count Update Error', exc
	logger.error('Mysql Current Alarm Count Update Error : %s', str(exc))
    else:
        my_cnx.commit()
    sleep(30)

    try:
        cursor.execute(clear_count_update_query)
    except Exception, exc:
        cursor.close()
        delete_clear_entry = False
        #print 'Mysql Clear Alarm Count Update Error', exc
	logger.error('Mysql Clear Alarm Count Update Error : %s', str(exc))
    else:
        my_cnx.commit()
    sleep(30)

    try:
        cursor.execute(clear_time_update_query)
    except Exception, exc:
        cursor.close()
        delete_clear_entry = False
        #print 'Mysql Clear Alarm Time Update Error', exc
	logger.error('Mysql Clear Alarm Time Update Error : %s', str(exc))
    else:
        my_cnx.commit()
    sleep(30)

    try:
        cursor.execute(current_time_update_query)
    except Exception, exc:
        cursor.close()
        delete_current_entry = False
        #print 'Mysql Current Alarm Time Update Error', exc
	logger.error('Mysql Current Alarm Time Update Error : %s', str(exc))
    else:
        my_cnx.commit()
    sleep(30)

    if delete_current_entry :
        try:
            cursor.execute(delete_query_currenthistory)
        except Exception, exc:
            cursor.close()
            #print 'Mysql Current Events History Delete Error', exc
	    logger.error('Mysql Current Events History Delete Error : %s', str(exc))
        else:
            my_cnx.commit()
            sleep(30)
            try:
                cursor.execute(current_delete_query)
            except Exception, exc:
                cursor.close()
                #print 'Mysql Current Delete Error', exc
		logger.error('Mysql Current Delete Error : %s', str(exc))
            else:
                my_cnx.commit()
    sleep(30)

    if delete_clear_entry :
        try:
            cursor.execute(delete_query_clearhistory)
        except Exception, exc:
            cursor.close()
            #print 'Mysql Clear Events History Delete Error', exc
	    logger.error('Mysql Clear Events History Delete Error : %s', str(exc))
        else:
            my_cnx.commit()
            sleep(30)
            try:
                cursor.execute(clear_delete_query)
            except Exception, exc:
                cursor.close()
                #print 'Mysql Clear Delete Error', exc
		logger.error('Mysql Clear Delete Error : %s', str(exc))
            else:
                my_cnx.commit()

    cursor.close()
    my_cnx.close()
