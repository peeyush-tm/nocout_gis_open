*SNMP Traps*
=============

> 1. Calling script trap_daemon.py with option `start` will start the process as a daemon.
   If script is called with option `foreground`, process will remain in foreground mode, this
   is useful if we want to run our script with cronjob or for testing.
   This will process alarms from `snmptt` database, into `clear_alarms`, `current_alarms` and
   `history_alarms` tables.

> 2. `trap_conf.py` contains database configuration settings used by above process.
