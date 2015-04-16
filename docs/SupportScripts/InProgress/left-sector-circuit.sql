select * from inventory_sector as sector
left join (
select circuit.id as CID,
		circuit.alias as CALIAS,
		circuit.circuit_id as CCID,
		customer.alias as CUST,
		circuit.sector_id,

		substation.id as SSID,
		antenna.height as SSHGT,
		
		device.ip_address as SSIP,
		device.device_alias as SSDEVICEALIAS
	from inventory_circuit as circuit 
	join (
		inventory_substation as substation,
		inventory_customer as customer,
		inventory_antenna as antenna,
		device_device as device,
		device_devicetechnology as technology,
		device_devicevendor as vendor
	)
	on (
		customer.id = circuit.customer_id
	and
		substation.id = circuit.sub_station_id
	and
		antenna.id = substation.antenna_id
	and
		device.id = substation.device_id
	and
		technology.id = device.device_technology
	and
		vendor.id = device.device_vendor
	)
) as circuit
on (sector.id = circuit.sector_id)