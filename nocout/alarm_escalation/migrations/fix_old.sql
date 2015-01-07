DROP TABLE IF EXISTS alarm_escalation_alarmescalation_level;
DROP TABLE IF EXISTS alarm_escalation_alarmescalation;
DROP TABLE IF EXISTS alarm_escalation_escalationlevel;
DROP TABLE IF EXISTS alarm_escalation_escalationstatus;
DELETE FROM south_migrationhistory WHERE app_name='alarm_escalation';
