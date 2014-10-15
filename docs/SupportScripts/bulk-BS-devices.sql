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
