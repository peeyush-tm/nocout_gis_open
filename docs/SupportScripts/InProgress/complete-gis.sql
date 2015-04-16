select * from (
	select * from inventory_basestation as basestation
	left join (
		inventory_sector as sector, 
		inventory_backhaul as backhaul, 
		inventory_antenna as antenna
	)
	on (
		sector.base_station_id = basestation.id
	and
		backhaul.id = basestation.backhaul_id
	and
		antenna.id = sector.antenna_id
	)
) as bs_info;

/*bs all info*/
select basestation.id as BSID,
		basestation.name as BSNAME,
		basestation.alias as BSALIAS,
		basestation.latitude as BSLAT,
		basestation.longitude as BSLONG,
		basestation.address as BSADDRESS,
		backhaul.id as BHID,
		sector.id as SID,
		sector.name as SNAME,
		sector.alias as SALIAS,
		antenna.height as SHGT
from inventory_basestation as basestation
left join (
	inventory_sector as sector, 
	inventory_backhaul as backhaul, 
	inventory_antenna as antenna
)
on (
	sector.base_station_id = basestation.id
and
	backhaul.id = basestation.backhaul_id
and
	antenna.id = sector.antenna_id
);

/*circuit + substation +sector information*/

select circuit.id as CID,
		circuit.alias as CALIAS,
		circuit.circuit_id as CCID,
		customer.alias as CUST,
		substation.id as SSID,
		antenna.height as SSHGT,
		sector.id as SID
from inventory_circuit as circuit 
join (
	inventory_substation as substation,
	inventory_customer as customer,
	inventory_sector as sector,
	inventory_antenna as antenna
)
on (
	sector.id = circuit.sector_id
and
	customer.id = circuit.customer_id
and
	substation.id = circuit.sub_station_id
and
	antenna.id = substation.antenna_id
);

/*circuits + substation only*/
select * from inventory_circuit as circuit 
join (
	inventory_substation as substation,
	inventory_customer as customer,
	inventory_antenna as antenna
)
on (
	customer.id = circuit.customer_id
and
	substation.id = circuit.sub_station_id
and
	antenna.id = substation.antenna_id
);
