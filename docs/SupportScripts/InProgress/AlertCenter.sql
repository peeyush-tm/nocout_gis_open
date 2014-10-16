EXPLAIN (Select * from (select * from performance_eventnetwork as pne
                                where pne.device_name in (
                                        select device.device_name from device_device as device join (
                                        inventory_sector as sector,
                                        inventory_substation as substation,
                                        inventory_circuit as circuit,
                                        inventory_basestation as basestation
                                        )
                                        on
                                        (
                                                sector.sector_configured_on_id = device.id
                                                and
                                                basestation.id = sector.base_station_id
                                                and
                                                circuit.sector_id = sector.id
                                                and
                                                substation.id = circuit.sub_station_id
                                        )
                                )
                        ) as original_table left outer join (
                                Select * from (select * from performance_eventnetwork as pne
                                                                where pne.device_name in (
                                                                        select device.device_name from device_device as device join (
                                                                        inventory_sector as sector,
                                                                        inventory_substation as substation,
                                                                        inventory_circuit as circuit,
                                                                        inventory_basestation as basestation
                                                                        )
                                                                        on
                                                                        (
                                                                                sector.sector_configured_on_id = device.id
                                                                                and
                                                                                basestation.id = sector.base_station_id
                                                                                and
                                                                                circuit.sector_id = sector.id
                                                                                and
                                                                                substation.id = circuit.sub_station_id
                                                                        )
                                                                )
                                                        ) as dt
) as duplicate_table
on (original_table.device_name = duplicate_table.device_name and original_table.data_source = duplicate_table.data_source and original_table.id < duplicate_table.id)
where (duplicate_table.id is null)
order by original_table.sys_timestamp DESC)