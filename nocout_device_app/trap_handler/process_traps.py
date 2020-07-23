""" Processes the raw traps and creates TM traps"""

from db_ops import ConnectionBase, ExportTraps


# Indexes of the trap attributes in a '|' separated formatline
# e.g. Trap PMP1 SS {} Downlink Modulation Changes HI Threshold crossed|
#1024|1|00:02:73:93:34:29    |PMC Slot
formatline_indexes = {
	# for wimax we need only these two vars
        'wimax': {
            'event_name': 0,
            'event_no': 1,
            'severity': 2,
            },
        }


class ProcessTraps(object):

	def __init__(self):
		self.conn_base = ConnectionBase()
		# read inventory info from redis [ip --> name mappings]
		self.inventory_info = self.read_cached_inventory()

		# `id` of the most latest row read from MySQL
		self.latest_id = None

	def do_work(self, traps):
		""" Starting point for processing all traps"""
		self.latest_id = traps[-1][0]
		wimax_traps, traps = self.filter_traps(traps, device_type='wimax')
		if wimax_traps:
			#self.process_wimax_traps(wimax_traps)
			pass
		if traps:
			self.process_traps(traps)

	def filter_traps(self, traps, device_type=None):
		""" Filters the traps based on device type"""
		filtered = [t for t in traps if 
				device_type in t[1].lower()]
		remaining = [t for t in traps if 
				device_type not in t[1].lower()]

		return filtered , remaining

	def process_traps(self, traps):
		alarm_mask_oids = self.get_alarm_mask_oids()
		traps, require_masking = self.normalize_traps(traps, alarm_mask_oids)
		# get traps which are not alive any more
		mark_inactive = self.get_inactive_traps(require_masking, alarm_mask_oids)
		#print 'require_masking: {0}'.format(require_masking)
		#print 'mark_inactive: {0}'.format(mark_inactive)

		if traps:
			export_traps = ExportTraps()
			export_traps.do_work(traps, mark_inactive=mark_inactive, 
					latest_id=self.latest_id)
			print 'Processed {0} pmp traps'.format(len(traps))

	def process_wimax_traps(self, traps):
		""" Processing wimax specific traps bcz they have
		completely different structure"""
		# TODO: keep formatline configs in Redis cache
		global formatline_indexes
		indexes = formatline_indexes['wimax']

		# parse the formatline for each trap
		traps = self.normalize_wimax_traps(traps, indexes)
		#alarm_mask_list = self.get_alarm_mask_oids(traps)

		if traps:
			export_traps = ExportTraps()
			export_traps.do_work(traps, latest_id=self.latest_id)
			print 'Processed {0} wimax traps'.format(len(traps))

	def normalize_wimax_traps(self, traps, indexes):
		""" Parse out the formatline and converts the traps into 
		dict format"""
		# TODO: read the traps in dict format from MySQL using DictCursor cursor
		# TODO: remove the hard-coding on indexes here
		out = []
		new_trap = {}
		# keep track to remove dupli traps in same cycle
		#unique_trap_per_host = {}

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
				new_trap.update({
					'ip_address': trap[3],
					'device_name': self.inventory_info.get(trap[3]),
					'trapoid': trap[4],
					'eventname': formatline[indexes['event_name']],
					'eventno': formatline[indexes['event_no']],
					'severity': self.severity_mapping(
						formatline[indexes['severity']]),
					'uptime': trap[7],
					'traptime': trap[8],
					'last_occurred': trap[8],
					'first_occurred': trap[8],
					'alarm_count': 1,
					'description': trap[-1],
					'is_active': 1
					})
			except IndexError as exc:
				#print 'Exc in formatline: {0}'.format(exc)
				#print 'Formatline: {0}'.format(formatline)
				continue

			out.append(new_trap)
			new_trap = {}

		return out

	def normalize_traps(self, traps, alarm_mask_oids):
		""" Convert the traps to compatible schema"""
		out = []
		# these traps have current/clear traps associated with them
		require_masking = []
		new_trap = {}

		for trap in traps:
			new_trap = {}
			try:
				new_trap.update({
					'ip_address': trap[3],
					'device_name': self.inventory_info.get(trap[3]),
					'trapoid': trap[4],
					'eventname': trap[1],
					'eventno': None,
					'severity': trap[6].lower(),
					'uptime': trap[7],
					'traptime': trap[8],
					'last_occurred': trap[8],
					'first_occurred': trap[8],
					'alarm_count': 1,
					'description': trap[-1],
					'is_active': 1,
					})
			except Exception as exc:
				print 'Exc in normalize traps: {0}'.format(exc)
				continue
			out.append(new_trap)

			mask_oid = alarm_mask_oids.get(trap[4])
			if mask_oid:
				# update alarms with `is_active` field to 0
				require_masking.append((str(trap[3]), str(mask_oid)))

		return out, require_masking

	def get_inactive_traps(self, traps, alarm_mask_oids):
		""" Get final traps which needs to be updated as `not 
		active` in db"""
		mapping = {}
		for trap in reversed(traps):
			mask_oid = alarm_mask_oids.get(trap[1])
			mask = (trap[0], mask_oid)
			if mask in mapping.keys():
				# its masking trap has appeared before
				continue
			else:
				if trap not in mapping:
					mapping.update({
						trap: 1
						})
		traps = [t for t in traps if t not in mapping]

		return traps

	def get_alarm_mask_oids(self):
		""" For every current trap, adds its corresponding clear trap 
		and vice-versa"""
		qry = """
		SELECT 
			main1.oid, main2.oid mask_oid
		FROM
			alarm_masking_table mask
		INNER JOIN
			main_alarm_table main1
		ON
			mask.alarm_id = main1.id
		INNER JOIN
			main_alarm_table main2
		ON
			mask.alarm_mask_id = main2.id
		"""
		my_cnx = self.conn_base.mysql_cnx(db_name='snmptt_db')
		cursor = my_cnx.cursor()
		cursor.execute(qry)
		data = cursor.fetchall()
		data = dict([(str(k), str(v)) for (k, v) in data])

		return data

	def read_cached_inventory(self):
		redis_cnx = self.conn_base.redis_cnx(db_name='redis_main')
		try:
			p = redis_cnx.pipeline()
			p.hgetall('ip:host')
			out = p.execute()
		except Exception as exc:
			out = [{}]
			print 'Error in reading cached inventory: {0}'.format(exc)

		return out[0]

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
