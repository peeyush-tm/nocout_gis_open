select 
	original.device_name as BSNAME, 
	original.mac_address as BSMAC,
	original.ip_address as BSIP, 
	SSNAME, 
	SSMAC, 
	SSIP, 
	DEVICETYPE, 
	TAG, 
	SITE,
	SUBSTATION, 
	CIRCUIT,
	SECTOR 
	from device_device as original
	inner join (
		(select 
		device_device.device_name SSNAME,
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
		where device_device.is_deleted=0 and device_devicetechnology.name in ("PMP") ) as dupli
	)
on (original.id = dupli.matcher)