import mysql.connector
from pprint import pformat


db = None
all_hosts = []
ipaddresses = {}
host_attributes = {}


def main():
	global all_hosts
	global ipaddresses
	global host_attributes
	mysql_conn()
	make_BS_data()
	make_SS_data()
	write_data()


def make_BS_data():
	query = """
	select 
	device_device.device_name,
	device_device.ip_address,
	device_devicetype.name,
	device_device.mac_address,
	device_device.ip_address,
	device_devicetype.agent_tag,
	inventory_sector.name,
	site_instance_siteinstance.name
	from device_device inner join (device_devicetechnology, device_devicemodel, device_devicetype, machine_machine, site_instance_siteinstance, inventory_sector)
	on (
	device_devicetype.id = device_device.device_type and
	device_devicetechnology.id = device_device.device_technology and
	device_devicemodel.id = device_device.device_model and
	machine_machine.id = device_device.machine_id and
	site_instance_siteinstance.id = device_device.site_instance_id and
	inventory_sector.sector_configured_on_id = device_device.id
	)
	where device_device.is_deleted=0 and device_devicetechnology.name in ("P2P")
	"""
	cur = db.cursor() 
	cur.execute(query) 
	data = cur.fetchall() 
	cur.close() 
	for device in data: 
		entry = str(device[0]) + '|' + str(device[2]) + '|' + str(device[3]).lower() + '|wan|prod|' + str(device[5]) + '|site:' + str(device[7]) + '|wato|//' 
		all_hosts.append(entry) 
		ipaddresses.update({str(device[0]): str(device[1])}) 
		host_attributes.update({ str(device[0]): { 
			'alias': str(device[0]), 
			'contactgroups': (True, ['all']),
			'site': str(device[7]),
			'tag_agent': str(device[5])
			}})


def write_data():
	with open('hosts.mk', 'w') as f:
		f.write("# encoding: utf-8\n\n")
		f.write("\nhost_contactgroups += []\n\n\n")
		f.write("all_hosts += %s\n" % pformat(all_hosts))
		f.write("\n\n# Explicit IP Addresses\n")
		f.write("ipaddresses.update(%s)\n\n" % pformat(ipaddresses))
		f.write("host_attributes.update(\n%s)\n" % pformat(host_attributes))


def make_SS_data():
	query = """
	select 
	device_device.device_name,
	device_device.ip_address,
	device_devicetype.name,
	device_device.mac_address,
	device_device.ip_address,
	device_devicetype.agent_tag,
	inventory_substation.name,
	site_instance_siteinstance.name
	from device_device inner join (device_devicetechnology, device_devicemodel, device_devicetype, machine_machine, site_instance_siteinstance, inventory_substation)
	on (
	device_devicetype.id = device_device.device_type and
	device_devicetechnology.id = device_device.device_technology and
	device_devicemodel.id = device_device.device_model and machine_machine.id = device_device.machine_id and
	site_instance_siteinstance.id = device_device.site_instance_id and
	inventory_substation.device_id = device_device.id
	)
	where device_device.is_deleted=0 and device_devicetechnology.name in ("P2P")
	"""
	cur = db.cursor()
	cur.execute(query)
	data = cur.fetchall()
	cur.close()
	for device in data:
		entry = str(device[0]) + '|' + str(device[2]) + '|' + str(device[3]).lower() + '|wan|prod|' + str(device[5]) + '|site:' + str(device[7]) + '|wato|//'
		all_hosts.append(entry)
		ipaddresses.update({str(device[0]): str(device[1])})
		host_attributes.update({
			str(device[0]): {
			'alias': str(device[0]),
			'contactgroups': (True, ['all']),
			'site': str(device[7]),
			'tag_agent': str(device[5])
			}})


def mysql_conn():
	global db
	db = mysql.connector.connect(
			host='121.244.255.107',
			user='root',
			password='root',
			database='nocout_dev_27_08_14'
			)


if __name__ == '__main__':
	main()
