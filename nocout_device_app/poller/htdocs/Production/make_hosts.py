from mysql_connection import mysql_conn
from pprint import pformat


db = None
all_hosts = []
ipaddresses = {}
host_attributes = {}


def main():
	global db
	global all_hosts
	global ipaddresses
	global host_attributes
	# This file contains device names, to be updated in configuration db
	open('/apps/omd/sites/main_UA/etc/check_mk/conf.d/wato/hosts.txt', 'w').close()
	db = mysql_conn()
	make_BS_data()
	make_SS_data()
	write_data()


def make_BS_data():
	global all_hosts
	global db
	query = """
	select 
        DISTINCT(device_device.ip_address),
	device_device.device_name,
	device_devicetype.name,
	device_device.mac_address,
	device_device.ip_address,
	device_devicetype.agent_tag,
	inventory_sector.name,
	site_instance_siteinstance.name,
        device_device.device_alias
	from device_device inner join (device_devicetechnology, device_devicemodel, device_devicetype, machine_machine, site_instance_siteinstance, inventory_sector)
	on (
	device_devicetype.id = device_device.device_type and
	device_devicetechnology.id = device_device.device_technology and
	device_devicemodel.id = device_device.device_model and
	machine_machine.id = device_device.machine_id and
	site_instance_siteinstance.id = device_device.site_instance_id and
	inventory_sector.sector_configured_on_id = device_device.id
	)
	where device_device.is_deleted=0 and device_devicetechnology.name in ('WiMAX', 'P2P', 'PMP') and device_devicetype.name in ('Radwin2KBS', 'CanopyPM100AP', 'CanopySM100AP', 'StarmaxIDU');
	"""
        #host name | device type | mac | parent _ name | wan | prod | agent tags | site | wato
	cur = db.cursor() 
	cur.execute(query) 
	data = cur.fetchall() 
	cur.close() 
        processed = []
	hosts_only = open('/apps/omd/sites/main_UA/etc/check_mk/conf.d/wato/hosts.txt', 'a')
	for device in data:
                if  str(device[1]) in processed:
                    continue
	        hosts_only.write(str(device[1]) + '\n')
                processed.append(str(device[1]))
		entry = str(device[1]) + '|' + str(device[2]) + '|' + str(device[3]).lower() + '|wan|prod|' + str(device[5]) + '|site:' + str(device[7]) + '|wato|//' 
		all_hosts.append(entry) 
		ipaddresses.update({str(device[1]): str(device[0])}) 
		host_attributes.update({ str(device[1]): { 
			'alias': str(device[8]), 
			'contactgroups': (True, ['all']),
			'site': str(device[7]),
			'tag_agent': str(device[5])
			}})
	#all_hosts = list(set(all_hosts))
	hosts_only.close()


def write_data():
	with open('/apps/omd/sites/main_UA/etc/check_mk/conf.d/wato/hosts.mk', 'w') as f:
		f.write("# encoding: utf-8\n\n")
		f.write("\nhost_contactgroups += []\n\n\n")
		f.write("all_hosts += %s\n" % pformat(all_hosts))
		f.write("\n\n# Explicit IP Addresses\n")
		f.write("ipaddresses.update(%s)\n\n" % pformat(ipaddresses))
		f.write("host_attributes.update(\n%s)\n" % pformat(host_attributes))


def make_SS_data():
	global db
	global all_hosts
        query = """
        select 
	distinct(SSIP),
	original.device_name as BSNAME, 
	original.mac_address as BSMAC,
	original.ip_address as BSIP, 
	SSNAME, 
	SSMAC, 
	DEVICETYPE, 
	TAG, 
	SITE,
	SUBSTATION, 
	CIRCUIT,
	SECTOR,
        original.device_alias as BSALIAS,
        SSALIAS
	from device_device as original
	inner join (
	(select 
	device_device.device_name SSNAME,
        device_device.device_alias as SSALIAS,
	device_devicetype.name as DEVICETYPE,
	device_device.mac_address as SSMAC,
	device_device.ip_address as SSIP,
	device_devicetype.agent_tag as TAG,
	inventory_substation.name as SUBSTATION,
	site_instance_siteinstance.name as SITE,
	inventory_circuit.circuit_id as CIRCUIT,
	inventory_sector.name SECTOR,
	inventory_sector.sector_configured_on_id as matcher
	from device_device 
	inner join (device_devicetechnology, device_devicemodel, device_devicetype, machine_machine, site_instance_siteinstance, inventory_substation, inventory_circuit, inventory_sector)
	on (
	device_devicetype.id = device_device.device_type and
	device_devicetechnology.id = device_device.device_technology and
	device_devicemodel.id = device_device.device_model and
	machine_machine.id = device_device.machine_id and
	site_instance_siteinstance.id = device_device.site_instance_id and
	inventory_substation.device_id = device_device.id and
	inventory_circuit.sub_station_id = inventory_substation.id and
	!isnull(inventory_circuit.sector_id) and
	inventory_sector.id = inventory_circuit.sector_id
	)
	where device_device.is_deleted=0 and device_devicetechnology.name in ('WiMAX', 'P2P', 'PMP') and device_devicetype.name in ('Radwin2KSS', 'CanopyPM100SS', 'CanopySM100SS', 'StarmaxSS')) as dupli
	)
	on (original.id = dupli.matcher)
        """
        #host name | device type | mac | parent _ name | wan | prod | agent tags | site | wato
	cur = db.cursor()
	cur.execute(query)
	data = cur.fetchall()
	cur.close()
        processed = []
	hosts_only = open('/apps/omd/sites/main_UA/etc/check_mk/conf.d/wato/hosts.txt', 'a')
	for device in data:
                if str(device[4]) in processed:
                    continue
	        hosts_only.write(str(device[4]) + '\n')
                processed.append(str(device[4]))
		entry = str(device[4]) + '|' + str(device[6]) + '|' + str(device[5]).lower() + '|' + str(device[1]) + '|wan|prod|' + str(device[7]) + '|site:' + str(device[8]) + '|wato|//'
		all_hosts.append(entry)
		ipaddresses.update({str(device[4]): str(device[0])})
		host_attributes.update({
			str(device[4]): {
			'alias': str(device[13]),
			'contactgroups': (True, ['all']),
			'site': str(device[8]),
			'tag_agent': str(device[7])
			}})
	#all_hosts = list(set(all_hosts))
	hosts_only.close()


def update_configuration_db():
	hosts = []
	with open('/apps/omd/sites/main_UA/etc/check_mk/conf.d/wato/hosts.txt', 'r') as f:
		hosts = map(lambda t: t.strip(), list(f))
	query = "UPDATE device_device set is_added_to_nms = 1, is_monitored_on_nms = 1"
	query += " WHERE device_name IN %s" % pformat(tuple(hosts))
	db = mysql_conn()
	cur = db.cursor()
	cur.execute(query)
	db.commit()
	cur.close()


if __name__ == '__main__':
	main()
