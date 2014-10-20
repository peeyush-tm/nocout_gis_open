select * /*bh_info.BHID as BHID*/ from (
	select backhaul.id as BHID,
			backhaul.bh_port_name as BH_PORT,
			backhaul.bh_type as BH_TYPE,
			backhaul.pe_hostname as BH_PE_HOSTNAME,
			backhaul.pe_ip as BH_PE_IP,
			backhaul.bh_connectivity as BH_CONNECTIVITY,
			backhaul.bh_circuit_id as BH_CIRCUIT_ID,
			backhaul.bh_capacity as BH_CAPACITY,
			backhaul.ttsl_circuit_id as BH_TTSL_CIRCUIT_ID,
			backhaul.dr_site as BH_DR_SITE,
			
			device.device_name as BHCONF,
			device.ip_address as BHCONF_IP
	from inventory_backhaul as backhaul
	join (
		device_device as device
	)
	on (
		device.id = backhaul.bh_configured_on_id
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
