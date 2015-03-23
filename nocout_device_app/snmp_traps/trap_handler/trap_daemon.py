#!/usr/bin/python

import sys
import os
from datetime import datetime
import logging
from mysql.connector import Connect
from mysql.connector import Error as SQL_ERR
from daemon import Daemon
from collections import OrderedDict, deque
import mysql

# indexes of the trap attributes in a '|' separated formatline
# Trap PMP1 SS {} Downlink Modulation Changes HI Threshold crossed|1024|1|00:02:73:93:34:29    |PMC Slot|$6|$7|$8|$9
formatline_indexes = {
        'wimax': {
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
        'wimax': OrderedDict([('ip_address', 0), ('eventno', 8), ('component_id', 12)])
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

        processed_traps = []
        processed_traps = process_history_alarms()
        if processed_traps:
            process_current_clear_alarms(processed_traps)
        print 'Processed %s traps\n' % len(processed_traps)
        print 'Done Processing ...\n'

class MyDBConnection:
    """
    Database connection class
    """
    def __init__(self, conf=None, db_type=None):
        self.conf_dict = {}
        self.db = None
        if conf:
            execfile(conf, self.conf_dict)
            self.conf_dict = self.conf_dict[db_type]

    def get_connection(self):
        try:
            self.db = Connect(**self.conf_dict)
        except SQL_ERR as e:
            print e
        except Exception as exp:
            print exp
            
        return self.db

    def close_connection(self):
        if isinstance(self.db, mysql.connector.connection.MySQLConnection):
            self.db.close()

def process_history_alarms():
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
        devices_info, custom_traps = get_inventory_devices()
        trap_data = normalize_trap_data(trap_data, devices_info, custom_traps)
        # bulk insert processed traps into final tables
        processed_traps_db_obj = MyDBConnection(conf='/omd/trap_handler/trap_conf.py', 
                db_type='processed_traps')
        p_db = processed_traps_db_obj.get_connection()
        insert_qry = "INSERT INTO history_alarms" 
        insert_qry += """
        (ip_address, device_name, device_type, device_technology, device_vendor, device_model, 
        trapoid, eventname, eventno, severity, uptime, traptime, component_id, 
        component_name, description)
        VALUES (%s, %s, %s,%s, %s, %s,%s, %s,%s,%s, %s, %s, %s, %s, %s)
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
    current_table, clear_table = 'current_alarms', 'clear_alarms'
    db_obj = MyDBConnection(conf='/omd/trap_handler/trap_conf.py', 
        db_type='processed_traps')
    db = db_obj.get_connection()
    # dict to store an alarm's state, would store an alarms
    # latest state only, based on `traptime`
    state_dict = {}
    # dict to store alarm's severity
    severity_dict = {}
    # list-containers to store clear/current alarm's rows
    # used to insert data into mysql
    current_alarms, clear_alarms = deque(), deque()
    for data in reversed(trap_data):
        # load unique indexes
        indexes = unique_key_indexes.get(data[3].lower())
        key = tuple([data[i] for i in indexes.values()])
        # add most latest entry only
        if key not in state_dict:
            state_dict[key] = data
            severity_dict[key] = data[9]
    if db:
        cursor = db.cursor()
    # this loop also deletes old data from alarm tables
    for key_set, values in state_dict.items():
        if severity_dict[key_set] == 'clear':
            clear_alarms.append(values)
            # load unique indexes
            indexes = unique_key_indexes.get(values[3].lower())
            key_names = indexes.keys()
            # 1. First we need to delete each alarm from current alarms table
            # for each corresponding entry present in clear_alarms list
            # based on alarms unique key, and vice-versa
            # perform deletion from clear_alarms table
            # 2. Also deleting old alarms from the same table,
            # in order to remove duplicacy for the same alarm with same severity
            try:
                # deletion from alternate table
                delete_qry = "DELETE FROM %s WHERE " % current_table
                delete_qry += ' AND '.join("%s='%s'" % t for t in zip(key_names, key_set))
                cursor.execute(delete_qry)
                # deletion from the same table
                delete_qry = "DELETE FROM %s WHERE " % clear_table
                delete_qry += ' AND '.join("%s='%s'" % t for t in zip(key_names, key_set))
                cursor.execute(delete_qry)
                #db.commit()
            except:
                sys.stdout.write('Exception in single delete from %s\n' % current_table)
        else:
            # add all non-clear alarms to current list
            current_alarms.append(values)
            # load unique indexes
            indexes = unique_key_indexes.get(values[3].lower())
            key_names = indexes.keys()
            try:
                delete_qry = "DELETE FROM %s WHERE " % clear_table
                delete_qry += ' AND '.join("%s='%s'" % t for t in zip(key_names, key_set))
                cursor.execute(delete_qry)
                delete_qry = "DELETE FROM %s WHERE " % current_table
                delete_qry += ' AND '.join("%s='%s'" % t for t in zip(key_names, key_set))
                cursor.execute(delete_qry)
                #db.commit()
            except:
                sys.stdout.write('Exception in single delete from %s\n' % clear_table)
    try:
        # don't put commit operation inside loop
        db.commit()
    except:
        sys.stdout.write('Exception in commit delete\n')

    # TODO :: How to remove alarms duplicacy, if exists
    # should we attempt to remove old alarms first, before inserting new alarms

    # insert query
    insert_qry = (
            "(ip_address, device_name, device_type, device_technology, device_vendor,"
            "device_model, trapoid, eventname, eventno, "
            "severity, uptime, traptime, component_id, component_name, description)" 
            "VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s, %s, %s, %s)"
                )
    current_insert_qry = "INSERT INTO %s" % current_table + insert_qry
    clear_insert_qry = "INSERT INTO %s" % clear_table + insert_qry
    if db:
        try:
            cursor = db.cursor()
            cursor.executemany(current_insert_qry, current_alarms)
        except SQL_ERR as e:
            sys.stdout.write('DB error with current alarms insertion\n') 
            sys.stdout.write(str(e)) 
        except Exception as e:
            sys.stdout.write('Exception with current alarms insertion\n') 
            sys.stdout.write(str(e)) 
        # inserting clear n current alarms in separate statements
        try:
            cursor = db.cursor()
            cursor.executemany(clear_insert_qry, clear_alarms)
            # commit into db only once for both the operations
            db.commit()
        except SQL_ERR as e:
            sys.stdout.write('DB error with clear alarms insertion\n') 
            sys.stdout.write(str(e)) 
        except Exception as e:
            sys.stdout.write('Exception with clear alarms insertion\n') 
            sys.stdout.write(str(e)) 
    db_obj.close_connection()

        #if indexes:
        #    keys, vals = indexes.keys(), indexes.values()
        #    vals = map(lambda e: data[e], vals)
        #    delete_qry = "DELETE FROM %s WHERE " % delete_from
        #    delete_qry += ' AND '.join("%s='%s'" % t for t in zip(keys, vals))
        #    find_existing_qry = "SELECT COUNT(1) FROM %s WHERE " % insert_into
        #    find_existing_qry += ' AND '.join("%s='%s'" % t for t in zip(keys, vals))

def normalize_trap_data(data, devices_info, custom_traps):
    """
    Formats the data for processed alarm tables.
    """
    global formatline_indexes
    out = []
    for entry in data:
        current_device_attr = devices_info.get(str(entry[3]))
        if current_device_attr:
            device_type = current_device_attr[2]
            device_technology = current_device_attr[1].lower()
            formatline = entry[-1]
            indexes = formatline_indexes[str(device_technology)]
            severity = map_severity(formatline.split('|')[indexes['severity']].strip())
            processed_entry = (entry[3], current_device_attr[0], device_type, current_device_attr[1],
                current_device_attr[3], current_device_attr[4], entry[4], 
                formatline.split('|')[indexes['event_name']].strip(),
                formatline.split('|')[indexes['event_no']].strip(),
            severity, entry[7], entry[8],
            formatline.split('|')[indexes['component_id']].strip(),
            formatline.split('|')[indexes['component_name']].strip(),
            formatline
            )
            out.append(processed_entry)

    return out


def get_inventory_devices():
    devices_info, custom_traps = {}, []
    # get device names from device_device table in configuration db
    # need to keep the device names in memory
    conf_db_obj = MyDBConnection(conf='/omd/trap_handler/trap_conf.py', db_type='conf_db')
    conf_db = conf_db_obj.get_connection()
    #logger.debug('Got db connection : %s' % pformat(conf_db))
    if conf_db:
        # TODO :: select those devices only whose traps are to be processed (based on device type)
        # device_qry = """select d.ip_address, d.device_name from device_device d left join 
        #    (device_devicetechnology t) on (d.device_technology = t.id) where t.name in ('Wimax', 'PMP')"""
        device_qry = """
            SELECT D.ip_address, D.device_name, Dt.name technology, Dtype.name type, Dven.name vendor, 
            Dmod.name model FROM device_device D LEFT JOIN (device_devicetechnology Dt, 
            device_devicetype Dtype, device_devicevendor Dven, 
            device_devicemodel Dmod) ON (D.device_technology = Dt.id AND D.device_type = Dtype.id AND 
            D.device_vendor = Dven.id AND D.device_model = Dmod.id)
        """
        cursor = conf_db.cursor()
        cursor.execute(device_qry)
        #cur_desc = cursor.description
        #devices_info = [dict(zip([col[0] for col in cur_desc], row))
         #       for row in cursor.fetchall()]
        data = cursor.fetchall()
        # mapping device attributes to device ip
        map(lambda x: devices_info.update({str(x[0]): x[1:]}), data)
        # get user defined traps from application db
        device_qry = "SELECT trap_oid FROM scheduling_management_snmptrapsettings"
        cursor = conf_db.cursor()
        cursor.execute(device_qry)
        custom_traps = cursor.fetchall()
        custom_traps = map(lambda x: x[0], custom_traps)
    conf_db_obj.close_connection()

    return devices_info, custom_traps


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
