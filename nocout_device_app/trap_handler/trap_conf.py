""" Keeps traps formatline and unique keys related to traps"""

# indexes of the trap attributes in a '|' separated formatline
# Trap PMP1 SS {} Downlink Modulation Changes HI Threshold crossed|
#1024|1|00:02:73:93:34:29|PMC Slot|$6|$7|$8|$9
formatline_indexes = {
        'wimax': {
            'event_name': 0,
            'event_no': 1,
            'severity': 2,
            'component_id': 3,
            'component_name': 4
            },
	'cambium': {
            'event_name': None,
            'event_no': None,
            'severity': 0,
            'component_id': 1,
            'component_name': None
	    }
        }
