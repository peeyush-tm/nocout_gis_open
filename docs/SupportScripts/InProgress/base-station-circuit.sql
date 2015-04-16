
/*basestation + Circuit Information*/
select * from (
	select basestation.id as BSID,
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
	left join (
		inventory_sector as sector, 
		inventory_backhaul as backhaul,
		device_country as country,
		device_city as city,
		device_state as state,
		device_device as device
	)
	on (
		sector.base_station_id = basestation.id
	and
		backhaul.id = basestation.backhaul_id
	and
		city.id = basestation.city
	and
		state.id = basestation.state
	and
		country.id = basestation.country
	and 
		device.id = basestation.bs_switch_id
	) 
)as bs_info 
left join (
	select circuit.id as CID,
		circuit.alias as CALIAS,
		circuit.circuit_id as CCID,
		customer.alias as CUST,
		substation.id as SSID,
		antenna.height as SSHGT,
		sector.id as SID,
		device.ip_address as SSIP,
		device.device_alias as SSDEVICEALIAS
	from inventory_circuit as circuit 
	join (
		inventory_substation as substation,
		inventory_customer as customer,
		inventory_sector as sector,
		inventory_antenna as antenna,
		device_device as device,
		device_devicetechnology as technology,
		device_devicevendor as vendor
	)
	on (
		sector.id = circuit.sector_id
	and
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
	ckt_info.SID = bs_info.SID
)
left join (
	select bh_info.BHID as BHID from (
	select backhaul.id as BHID, device.device_name as BHCONF from inventory_backhaul as backhaul
	join (
		device_device as device
	)
	on (
		device.id = backhaul.bh_configured_on_id
	)
	) as bh_info left join (
			select backhaul.id as BHID, device.device_name as POP from inventory_backhaul as backhaul
			left join (
				device_device as device
			)
			on (
				device.id = backhaul.pop_id
			)
	) as pop_info
	on (bh_info.BHID = pop_info.BHID)
	left join ((
			select backhaul.id as BHID, device.device_name as BSCONV from inventory_backhaul as backhaul
			left join (
				device_device as device
			)
			on (
				device.id = backhaul.bh_switch_id
			)
	) as bscon_info
	) on (bh_info.BHID = bscon_info.BHID)
	left join ((
			select backhaul.id as BHID, device.device_name as AGGR from inventory_backhaul as backhaul
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
LIMIT 0,10000