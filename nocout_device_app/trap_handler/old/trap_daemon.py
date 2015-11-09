#!/usr/bin/python

import sys, time
import os
from datetime import datetime
from pprint import pformat
import logging
from mysql.connector import Connect
from mysql.connector import Error as SQL_ERR
from daemon import Daemon
from collections import OrderedDict
import mysql

formatline_indexes = {
        # for wimax
        '.1.3.6.1.4.1.5812.2000.15.2.1': {
            'event_name': 0,
            'event_no': 1,
            'severity': 2,
            'component_id': 3,
            'component_name': 4
            }
        }
# determines a trap uniquely, for a device type
unique_key_indexes = {
        # (ip, eventno, component_id) for wimax
        'wimax': OrderedDict(
		[('ip_address', 0), ('eventno', 5), ('component_id', 9)])
	}

class Logger:
    """
    A generic logger class, returns a logger object.
    """
    def __init__(self, name = 'trap_handler', logfile='/omd/nocout/trap_handler.log', logger=None):
        self.name = name
        self.logfile = logfile
        self.logger = logger

    def get(self):
        """
        Returns a logger object, which logs activities to a
        log file
        """
        if os.path.exists(self.logfile):
            self.logger = logging.getLogger(self.name)
            if not len(self.logger.handlers):
                self.logger.setLevel(logging.DEBUG)
                handler=logging.FileHandler(self.logfile)
                formatter = logging.Formatter('%(asctime)s - %(levelname)s >> %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        else:
            message = "Unable to locate log file...logging to stdout"
            sys.stdout.write(message)

        return self.logger

class MyDaemon(Daemon):
    def run(self):
        #logger_instance = Logger()
        #logger = logger_instance.get()
        #logger.debug('Trap daemon started at: %s' % pformat(datetime.now()))

        devices_info = []
        processed_traps = []
        # get device names from device_device table in configuration db
        # need to keep the device names in memory
        conf_db_obj = MyDBConnection(conf='/omd/trap_handler/trap_conf.py', db_type='conf_db')
        conf_db = conf_db_obj.get_connection()
        #logger.debug('Got db connection : %s' % pformat(conf_db))
        if conf_db:
            device_qry = "SELECT device_name, ip_address FROM device_device"
            cursor = conf_db.cursor()
            cursor.execute(device_qry)
            #cur_desc = cursor.description
            #devices_info = [dict(zip([col[0] for col in cur_desc], row))
             #       for row in cursor.fetchall()]
            devices_info = cursor.fetchall()
        conf_db_obj.close_connection()
        print devices_info[0:10]

        if devices_info:
            processed_traps = process_history_alarms(devices_info)
        if processed_traps:
            process_current_clear_alarms(processed_traps)
        print 'Processed %s traps\n' % len(processed_traps)
        print 'Done Processing ...\n'

class MyDBConnection:
    """
    Database connection class
    """
    def __init__(self, conf=None, db_type=None):
        self.conf_vars = {}
        self.db = None
        if conf:
            execfile(conf, self.conf_vars)
            self.conf_vars = self.conf_vars[db_type]
            #del self.conf_vars['__builtins__']

    def get_connection(self):
        try:
            self.db = Connect(host=self.conf_vars['host'], port=self.conf_vars['port'], 
                    user=self.conf_vars['user'], password=self.conf_vars['password'], 
                    database=self.conf_vars['database'])
        except SQL_ERR as e:
            print e
        except Exception as exp:
            print exp
            
        return self.db

    def close_connection(self):
        if isinstance(self.db, mysql.connector.connection.MySQLConnection):
            self.db.close()

def process_history_alarms(devices_info):
    """
    Import all the traps into history trap table.
    """
    trap_data = []
    index = ()
    # Connection to snmptt database
    trap_db_obj = MyDBConnection(conf='/omd/trap_handler/trap_conf.py', db_type='snmptt')
    trap_db = trap_db_obj.get_connection()
    index_query = "SELECT processed_row FROM id_info"
    try:
        cursor = trap_db.cursor()
        cursor.execute(index_query)
        index = cursor.fetchall()
    except SQL_ERR as e:
        print 'DB error with id_info'
        print e
    except Exception as exp:
        print 'Exception with id_info'
        print exp
    if len(index):
        select_trap_qry = "SELECT id, eventname, eventid, agentip, trapoid, category, \
                severity, uptime, traptime, formatline FROM"
        select_trap_qry += " snmptt WHERE id > %s" % index[0]
	try:
	    cursor.execute(select_trap_qry)
	    trap_data = cursor.fetchall()
	except SQL_ERR as e:
	    print 'DB error with snmptt'
	    print e
	except Exception as exp:
	    print 'Exception with snmptt'
	    print exp
        if len(trap_data):
            update_index = trap_data[-1][0]
            update_index_qry = "UPDATE id_info SET processed_row=%s, timestamp='%s'" \
                    % (update_index, datetime.now())
            cursor.execute(update_index_qry)
            trap_db.commit()
    else:
        index_query = "INSERT INTO id_info(processed_row, timestamp) "
	index_query += "VALUES (%s, '%s')" % (0, datetime.now())
        try:
	    cursor.execute(index_query)
	    trap_db.commit()
        except SQL_ERR as e:
	    print 'DB error with insert id_info'
	    print e
        except Exception as exp:
	    print 'Exception with insert id_info'
	    print exp
    trap_db_obj.close_connection()
    if len(trap_data):
        trap_data = normalize_trap_data(trap_data, devices_info)
        # bulk insert processed traps into final tables
        processed_traps_db_obj = MyDBConnection(conf='/omd/trap_handler/trap_conf.py', 
                db_type='processed_traps')
        p_db = processed_traps_db_obj.get_connection()
        insert_qry = "INSERT INTO history_alarms" 
        insert_qry += """
        (ip_address, device_name, device_type, trapoid, eventname, eventno,
        severity, uptime, traptime, component_id, component_name, description)
         VALUES (%s, %s, %s,%s, %s, %s,%s, %s,%s,%s, %s, %s)
        """
        if p_db:
            try:
                cursor = p_db.cursor()
                cursor.executemany(insert_qry, trap_data)
            except SQL_ERR as e:
                print 'DB error in inserting processed traps...'
                print e
            except Exception as exp:
                print 'Exception in inserting processed traps...'
                print exp
            else:
                p_db.commit()
            finally:
                cursor.close()
                processed_traps_db_obj.close_connection()

    return trap_data

def process_current_clear_alarms(trap_data):
    global unique_key_indexes
    db_obj = MyDBConnection(conf='/omd/trap_handler/trap_conf.py', 
		db_type='processed_traps')
    db = db_obj.get_connection()
    for data in trap_data:
        delete_from, insert_into = None, None
        indexes = None
        # load unique indexes
        if 'wimax' in data[2].lower():
            indexes = unique_key_indexes['wimax']
        if 'clear' in data[6]:
            delete_from = 'current_alarms'
            insert_into = 'clear_alarms'
        else:
            delete_from = 'clear_alarms'
            insert_into = 'current_alarms'
        if indexes:
            keys, vals = indexes.keys(), indexes.values()
	    vals = map(lambda e: data[e], vals)
            delete_qry = "DELETE FROM %s WHERE " % delete_from
	    delete_qry += ' AND '.join("%s='%s'" % t for t in zip(keys, vals))
	    insert_qry = "INSERT INTO %s" % insert_into
            insert_qry += (
                    "(ip_address, device_name, device_type, trapoid, eventname, eventno, "
                    "severity, uptime, traptime, component_id, component_name, description)" 
                    "VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s)"
                    )
            find_existing_qry = "SELECT COUNT(1) FROM %s WHERE " % insert_into
            find_existing_qry += ' AND '.join("%s='%s'" % t for t in zip(keys, vals))
            if db:
                try:
                    # delete trap from current/clear
                    cursor = db.cursor()
                    cursor.execute(delete_qry)
                    db.commit()
                    # check whether trap is already inserted
                    cursor.execute(find_existing_qry)
                    trap_exists = cursor.fetchall()
                    if not trap_exists[0][0]:
			# insert trap into current/clear
                        cursor.execute(insert_qry, data)
			db.commit()
                except SQL_ERR as e:
                    print 'DB error in current/clear...'
                    print e
                except Exception as exp:
                    print 'Exception in current/clear...'
                    print exp
    db_obj.close_connection()

def normalize_trap_data(data, devices_info):
    """
    Formats the data for processed alarm tables.
    """
    global formatline_indexes
    out = []
    for entry in data:
        for d in devices_info:
            current_device = None
            if str(entry[3]) == str(d['ip_address']):
                current_device = d['device_name']
                break
        # ToDo:: If device is not being monitored, skip the step for that device
        formatline = entry[-1]
        indexes = formatline_indexes[str(entry[4]).strip()]
        severity = map_severity(formatline.split('|')[indexes['severity']].strip())
        processed_entry = (entry[3], current_device, entry[1].split('_')[0].lower(), entry[4], 
                formatline.split('|')[indexes['event_name']].strip(),
                formatline.split('|')[indexes['event_no']].strip(),
                severity, entry[7], entry[8],
                formatline.split('|')[indexes['component_id']].strip(),
                formatline.split('|')[indexes['component_name']].strip(),
                formatline
                )
        out.append(processed_entry)

    return out

def map_severity(severity):
    verb_severity = None
    severity = int(severity) if severity.isdigit() else None
    if severity == 1:
        verb_severity = 'clear'
    elif severity == 2:
        verb_severity = 'indeterminate'
    elif severity == 3:
        verb_severity = 'critical'
    elif severity == 4:
        verb_severity = 'major'
    elif severity == 5:
        verb_severity = 'minor'
    elif severity == 6:
        verb_severity = 'warning'

    return verb_severity
        

if __name__ == "__main__":
    daemon = MyDaemon('/tmp/trap_handler.pid', 'trapHandler')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        elif 'foreground' == sys.argv[1]:
            daemon.run()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
