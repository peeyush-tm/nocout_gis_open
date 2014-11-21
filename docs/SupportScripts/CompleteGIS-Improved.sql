select * from (
				select  basestation.id as BSID,
						basestation.name as BSNAME,
						basestation.alias as BSALIAS,
						basestation.bs_site_id as BSSITEID,
						basestation.bs_site_type as BSSITETYPE,

						device.ip_address as BSSWITCH,

						basestation.bs_type as BSTYPE,
						basestation.bh_bso as BSBHBSO,
						basestation.hssu_used as BSHSSUUSED,
						basestation.latitude as BSLAT,
						basestation.longitude as BSLONG,

						basestation.infra_provider as BSINFRAPROVIDER,
						basestation.gps_type as BSGPSTYPE,
						basestation.building_height as BSBUILDINGHGT,
						basestation.tower_height as BSTOWERHEIGHT,

						city.city_name as BSCITY,
						state.state_name as BSSTATE,
						country.country_name as BSCOUNTRY,

						basestation.address as BSADDRESS,

						backhaul.id as BHID,
						sector.id as SID
						
				from inventory_basestation as basestation
				left join inventory_sector as sector
				on sector.base_station_id = basestation.id
				left join inventory_backhaul as backhaul
				on backhaul.id = basestation.backhaul_id 
				left join device_country as country
				on country.id = basestation.country
				left join device_city as city
				on city.id = basestation.city
				left join device_state as state
				on state.id = basestation.state
				left join device_device as device
				on device.id = basestation.bs_switch_id
				group by BSID
			)as bs_info 
left join (
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
		device.device_name as SECTOR_CONF_ON_NAME,
		device.device_alias as SECTOR_CONF_ON_ALIAS,
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

			circuit.circuit_type as CIRCUIT_TYPE,
			circuit.qos_bandwidth as QOS,
			circuit.dl_rssi_during_acceptance as RSSI,
			circuit.dl_cinr_during_acceptance as CINR,
			circuit.jitter_value_during_acceptance as JITTER,
			circuit.throughput_during_acceptance as THROUHPUT,
			circuit.date_of_acceptance as DATE_OF_ACCEPT,

			customer.alias as CUST,
			customer.address as SS_CUST_ADDR,

			substation.id as SSID,
			substation.name as SS_NAME,
			substation.alias as SS_ALIAS,
			substation.version as SS_VERSION,
			substation.serial_no as SS_SERIAL_NO,
			substation.building_height as SS_BUILDING_HGT,
			substation.tower_height as SS_TOWER_HGT,
			substation.ethernet_extender as SS_ETH_EXT,
			substation.cable_length as SS_CABLE_LENGTH,
			substation.latitude as SS_LATITUDE,
			substation.longitude as SS_LONGITUDE,
			substation.mac_address as SS_MAC,

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
			device.id as SS_DEVICE_ID,
			device.device_alias as SSDEVICEALIAS,
			device.device_name as SSDEVICENAME,

			technology.name as SS_TECH,
			vendor.name as SS_VENDOR,
			devicetype.name as SS_TYPE,
			devicetype.name as SSDEVICETYPE,
			devicetype.device_icon as SS_ICON,
			devicetype.device_gmap_icon as SS_GMAP_ICON

		from inventory_circuit as circuit
		join (
			inventory_substation as substation,
			inventory_customer as customer,
			inventory_antenna as antenna,
			device_device as device,
			device_devicetechnology as technology,
			device_devicevendor as vendor,
			device_devicetype as devicetype
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
		and
			devicetype.id = device.device_type
		)
	) as ckt_info
	on (
		ckt_info.SID = sector_info.SECTOR_ID
	)
) as sect_ckt
on (sect_ckt.SECTOR_BS_ID = bs_info.BSID)
left join
	(
		select bh_info.BHID as BHID,
				bh_info.BH_PORT as BH_PORT,
				bh_info.BH_TYPE as BH_TYPE,
				bh_info.BH_PE_HOSTNAME as BH_PE_HOSTNAME,
				bh_info.BH_PE_IP as BH_PE_IP,
				bh_info.BH_CONNECTIVITY as BH_CONNECTIVITY,
				bh_info.BH_CIRCUIT_ID as BH_CIRCUIT_ID,
				bh_info.BH_CAPACITY as BH_CAPACITY,
				bh_info.BH_TTSL_CIRCUIT_ID as BH_TTSL_CIRCUIT_ID,


				bh_info.BH_DEVICE_ID as BH_DEVICE_ID,
				bh_info.BHCONF as BHCONF,
				bh_info.BHCONF_IP as BHCONF_IP,
				bh_info.BHTECH as BHTECH,
				bh_info.BHTYPE as BHTYPE,

				POP_IP,
				AGGR_IP,
				BSCONV_IP

		from (
		select backhaul.id as BHID,
				backhaul.bh_port_name as BH_PORT,
				backhaul.bh_type as BH_TYPE,
				backhaul.pe_hostname as BH_PE_HOSTNAME,
				backhaul.pe_ip as BH_PE_IP,
				backhaul.bh_connectivity as BH_CONNECTIVITY,
				backhaul.bh_circuit_id as BH_CIRCUIT_ID,
				backhaul.bh_capacity as BH_CAPACITY,
				backhaul.ttsl_circuit_id as BH_TTSL_CIRCUIT_ID,


				device.id as BH_DEVICE_ID,
				device.device_name as BHCONF,
				device.ip_address as BHCONF_IP,
				tech.name as BHTECH,
				devicetype.name as BHTYPE

		from inventory_backhaul as backhaul
		join (
			device_device as device,
			device_devicetype as devicetype,
			device_devicetechnology as tech
		)
		on (
			device.id = backhaul.bh_configured_on_id
			and
			tech.id = device.device_technology
			and
			devicetype.id = device.device_type
		)
		) as bh_info left join (
				select backhaul.id as BHID, device.device_name as POP, device.ip_address as POP_IP from inventory_backhaul as backhaul
				left join (
					device_device as device
				)
				on (
					device.id = backhaul.pop_id
				)
		) as pop_info
		on (bh_info.BHID = pop_info.BHID)
		left join ((
				select backhaul.id as BHID, device.device_name as BSCONV, device.ip_address as BSCONV_IP from inventory_backhaul as backhaul
				left join (
					device_device as device
				)
				on (
					device.id = backhaul.bh_switch_id
				)
		) as bscon_info
		) on (bh_info.BHID = bscon_info.BHID)
		left join ((
				select backhaul.id as BHID, device.device_name as AGGR, device.ip_address as AGGR_IP from inventory_backhaul as backhaul
				left join (
					device_device as device
				)
				on (
					device.id = backhaul.aggregator_id
				)
		) as aggr_info
		) on (bh_info.BHID = aggr_info.BHID)

	) as bh
on
	(bh.BHID = bs_info.BHID)

  group by BSID,SECTOR_ID,CID 