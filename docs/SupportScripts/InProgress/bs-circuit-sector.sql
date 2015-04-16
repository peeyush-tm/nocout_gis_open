
/*basestation + Circuit Information*/
select 
    *
from
    (select 
        basestation.id as BSID,
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
    from
        inventory_basestation as basestation
    left join (inventory_sector as sector, inventory_backhaul as backhaul, device_country as country, device_city as city, device_state as state, device_device as device) ON (sector.base_station_id = basestation.id
        and backhaul.id = basestation.backhaul_id
        and city.id = basestation.city
        and state.id = basestation.state
        and country.id = basestation.country
        and device.id = basestation.bs_switch_id)) as bs_info
        left join
    (select 
        circuit.id as CID,
            circuit.alias as CALIAS,
            circuit.circuit_id as CCID,
            customer.alias as CUST,
            substation.id as SSID,
            antenna.height as SSHGT,
            sector.id as SID,
            device.ip_address as SSIP,
            device.device_alias as SSDEVICEALIAS
    from
        inventory_circuit as circuit
    join (inventory_substation as substation, inventory_customer as customer, inventory_sector as sector, inventory_antenna as antenna, device_device as device, device_devicetechnology as technology, device_devicevendor as vendor) ON (sector.id = circuit.sector_id
        and customer.id = circuit.customer_id
        and substation.id = circuit.sub_station_id
        and antenna.id = substation.antenna_id
        and device.id = substation.device_id
        and technology.id = device.device_technology
        and vendor.id = device.device_vendor)) as ckt_info ON (ckt_info.SID = bs_info.SID)
        left join
    (select 
        bh_info.BHID as BHID
    from
        (select 
        backhaul.id as BHID, device.device_name as BHCONF
    from
        inventory_backhaul as backhaul
    join (device_device as device) ON (device.id = backhaul.bh_configured_on_id)) as bh_info
    left join (select 
        backhaul.id as BHID, device.device_name as POP
    from
        inventory_backhaul as backhaul
    left join (device_device as device) ON (device.id = backhaul.pop_id)) as pop_info ON (bh_info.BHID = pop_info.BHID)
    left join ((select 
        backhaul.id as BHID, device.device_name as BSCONV
    from
        inventory_backhaul as backhaul
    left join (device_device as device) ON (device.id = backhaul.bh_switch_id)) as bscon_info) ON (bh_info.BHID = bscon_info.BHID)
    left join ((select 
        backhaul.id as BHID, device.device_name as AGGR
    from
        inventory_backhaul as backhaul
    left join (device_device as device) ON (device.id = backhaul.aggregator_id)) as aggr_info) ON (bh_info.BHID = aggr_info.BHID)) as bh ON (bh.BHID = bs_info.BHID)
        left join
    (select 
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
    from
        inventory_sector as sector
    join (device_device as device, inventory_antenna as antenna, device_devicetechnology as technology, device_devicevendor as vendor, device_devicetype as devicetype) ON (device.id = sector.sector_configured_on_id
        and antenna.id = sector.antenna_id
        and technology.id = device.device_technology
        and devicetype.id = device.device_type
        and vendor.id = device.device_vendor)
    left join (device_devicefrequency as frequency) ON (frequency.id = sector.frequency_id)) as sector_info ON (sector_info.SECTOR_ID = bs_info.SID)