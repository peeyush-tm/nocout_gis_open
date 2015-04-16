INSERT INTO `performance_networkstatus`
(
	`device_name`,
	`service_name`,
	`machine_name`,
	`site_name`,
	`ip_address`,
	`data_source`,
	`severity`,
	`current_value`,
	`min_value`,
	`max_value`,
	`avg_value`,
	`warning_threshold`,
	`critical_threshold`,
	`sys_timestamp`,
	`check_timestamp`,
	`age`
)

select 
	device_name, 
	'ping', 
	'ospf1',
	'ospf1_slave_1', 
	ip_address,
	'rta',
	'down', 
	FLOOR(RAND() * (100 - 0 + 1)), 
	0,
	0,
	0,
	0,
	0,
	0,
	0,
	1416309666
from device_device;
