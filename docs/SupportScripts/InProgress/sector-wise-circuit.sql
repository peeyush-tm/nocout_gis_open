select * from (select 
	sector.id as SECTOR_ID,
	sector.name as SECTOR_NAME,
	sector.alias as SECTOR_ALIAS,
	sector.sector_id as SECTOR_SECTOR_ID,
	sector.base_station_id as SECTOR_BS_ID,
	sector.mrc as SECTOR_MRC,
	sector.tx_power as SECTOR_TX,
	sector.rx_power as SECTOR_RX,
	sector.rf_bandwidth as SECTOR_RFBW,
	sector.frame_length as SECTOR_FRAME_LENGTH,
	sector.cell_radius as SECTOR_CELL_RADIUS,
	sector.modulation as SECTOR_MODULATION,

	technology.name as SECTOR_TECH,
	vendor.name as SECTOR_VENDOR,
	devicetype.name as SECTOR_TYPE,
	devicetype.device_icon as SECTOR_ICON,
	devicetype.device_gmap_icon as SECTOR_GMAP_ICON,

	device.id as SECTOR_CONF_ON_ID,
	device.device_name as SECTOR_CONF_ON,
	device.ip_address as SECTOR_CONF_ON_IP,
	device.mac_address as SECTOR_CONF_ON_MAC,

	antenna.antenna_type as SECTOR_ANTENNA_TYPE,
	antenna.height as SECTOR_ANTENNA_HEIGHT,
	antenna.polarization as SECTOR_ANTENNA_POLARIZATION,
	antenna.tilt as SECTOR_ANTENNA_TILT,
	antenna.gain as SECTOR_ANTENNA_GAIN,
	antenna.mount_type as SECTORANTENNAMOUNTTYPE,
	antenna.beam_width as SECTOR_BEAM_WIDTH,
	antenna.azimuth_angle as SECTOR_ANTENNA_AZMINUTH_ANGLE,
	antenna.reflector as SECTOR_ANTENNA_REFLECTOR,
	antenna.splitter_installed as SECTOR_ANTENNA_SPLITTER,
	antenna.sync_splitter_used as SECTOR_ANTENNA_SYNC_SPLITTER,
	antenna.make_of_antenna as SECTOR_ANTENNA_MAKE,

	frequency.color_hex_value as SECTOR_FREQUENCY_COLOR,
	frequency.frequency_radius as SECTOR_FREQUENCY_RADIUS,
	frequency.value as SECTOR_FREQUENCY

	from inventory_sector as sector
	join (
		device_device as device,
		inventory_antenna as antenna,
		device_devicetechnology as technology,
		device_devicevendor as vendor,
		device_devicetype as devicetype
	)
	on (
		device.id = sector.sector_configured_on_id
	and
		antenna.id = sector.antenna_id
	and
		technology.id = device.device_technology
	and
		devicetype.id = device.device_type
	and
		vendor.id = device.device_vendor
	) left join (device_devicefrequency as frequency)
	on (
		frequency.id = sector.frequency_id
	)
) as sector_info
left join (
	select circuit.id as CID,
		circuit.alias as CALIAS,
		circuit.circuit_id as CCID,
		circuit.sector_id as SID,

		customer.alias as CUST,
		substation.id as SSID,

		antenna.height as SSHGT,
		antenna.antenna_type as SS_ANTENNA_TYPE,
		antenna.height as SS_ANTENNA_HEIGHT,
		antenna.polarization as SS_ANTENNA_POLARIZATION,
		antenna.tilt as SS_ANTENNA_TILT,
		antenna.gain as SS_ANTENNA_GAIN,
		antenna.mount_type as SSANTENNAMOUNTTYPE,
		antenna.beam_width as SS_BEAM_WIDTH,
		antenna.azimuth_angle as SS_ANTENNA_AZMINUTH_ANGLE,
		antenna.reflector as SS_ANTENNA_REFLECTOR,
		antenna.splitter_installed as SS_ANTENNA_SPLITTER,
		antenna.sync_splitter_used as SS_ANTENNA_SYNC_SPLITTER,
		antenna.make_of_antenna as SS_ANTENNA_MAKE,

		device.ip_address as SSIP,
		device.device_alias as SSDEVICEALIAS,
		technology.name as SS_TECH,
		vendor.name as SS_VENDOR
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
) as ckt_info
on (
	ckt_info.SID = sector_info.SECTOR_ID
)
