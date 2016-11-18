/**
 * This file defines the default sequence of tooltip info for all type of devices shown on map with blank or null values 
   & update the tooltip info come from backend same as this sequence
 * @for tooltipLib
 */

// BS Tooltip info object
var bs_toolTip_static = [
    {
        'name'  : 'name',
        'title' : 'BS Name',
        'show'  : 0,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'base_station_alias',
        'title' : 'BS Name',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bs_site_name',
        'title' : 'BS Site Name',
        'show'  : 0,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bs_site_id',
        'title' : 'Site ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'building_height',
        'title' : 'Building Height',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'tower_height',
        'title' : 'Tower Height',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bs_type',
        'title' : 'Site Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bs_gps_type',
        'title' : 'GPS Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bs_address',
        'title' : 'Address',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bs_city',
        'title' : 'City',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bs_state',
        'title' : 'State',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'lat_lon',
        'title' : 'Lat, Long',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bs_infra_provider',
        'title' : 'Infra Provider',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'tag1',
        'title': 'Tag1',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'tag2',
        'title': 'Tag2',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    }
];

// BH Tooltip static info object
var bh_toolTip_static = [
    {
        'name'  : 'bh_capacity',
        'title' : 'BH Capacity',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bh_connectivity',
        'title' : 'BH Offnet/Onnet',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bh_type',
        'title' : 'Backhaul Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bh_circuit_id',
        'title' : 'BH Circuit ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bh_ttsl_circuit_id',
        'title' : 'BSO Circuit ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bh_pe_hostname',
        'title' : 'PE Hostname',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'pe_ip',
        'title' : 'PE IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bs_switch_ip',
        'title' : 'BS Switch IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'aggregation_switch',
        'title' : 'Agg Switch IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'aggregation_switch_port',
        'title' : 'Agg Switch Port',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bs_converter_ip',
        'title' : 'BS Converter IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'pop',
        'title' : 'POP Converter IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bh_device_type',
        'title' : 'Converter Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bh_configured_on',
        'title' : 'BH Configured On SW/CON',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bh_device_port',
        'title' : 'SW/CON Port',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    }
];

// MROTECH BH Tooltip polled info object
var mrotech_bh_toolTip_polled = [
    {
        'name'  : 'mrotek_ul_utilization_fe_1',
        'title' : 'BH UL Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'mrotek_dl_utilization_fe_1',
        'title' : 'BH DL Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'mrotek_temperature_temperature',
        'title' : 'BH Temperature',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'pl',
        'title' : 'Packet Loss',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rta',
        'title' : 'Latency',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    }
];

// RICI BH Tooltip polled info object
var rici_bh_toolTip_polled = [
    {
        'name'  : 'rici_ul_utilization_eth_1',
        'title' : 'BH UL Utilization(eth 1)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rici_ul_utilization_eth_2',
        'title' : 'BH UL Utilization(eth 2)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rici_ul_utilization_eth_3',
        'title' : 'BH UL Utilization(eth 3)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rici_ul_utilization_eth_4',
        'title' : 'BH UL Utilization(eth 4)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rici_dl_utilization_eth_1',
        'title' : 'BH DL Utilization(eth 1)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rici_dl_utilization_eth_2',
        'title' : 'BH DL Utilization(eth 2)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rici_dl_utilization_eth_3',
        'title' : 'BH DL Utilization(eth 3)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rici_dl_utilization_eth_4',
        'title' : 'BH DL Utilization(eth 4)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'pl',
        'title' : 'Packet Loss',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rta',
        'title' : 'Latency',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    }
];

// SWITCH BH Tooltip polled info object
var switch_bh_toolTip_polled = [
    {
        'name'  : 'switch_ul_utilization_fe_1',
        'title' : 'BH UL Utilization(fe 1)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'switch_ul_utilization_fe_2',
        'title' : 'BH UL Utilization(fe 2)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'switch_ul_utilization_fe_3',
        'title' : 'BH UL Utilization(fe 3)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'switch_dl_utilization_fe_1',
        'title' : 'BH DL Utilization(fe 1)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'switch_dl_utilization_fe_2',
        'title' : 'BH DL Utilization(fe 2)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'switch_dl_utilization_fe_3',
        'title' : 'BH DL Utilization(fe 3)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'pl',
        'title' : 'Packet Loss',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rta',
        'title' : 'Latency',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    }
];

// General SS Tooltip static info object
var ss_toolTip_static = [
    {
        'name'  : 'base_station_alias',
        'title' : 'Base Station Name',
        'show'  : 0,
        'value' : ''
    },
    {
        'name'  : 'cktid',
        'title' : 'Circuit ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'customer_alias',
        'title' : 'Customer Name',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'ss_ip',
        'title': 'SS IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'pe_ip',
        'title': 'PE IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'qos_bandwidth',
        'title' : 'QOS(BW)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'antenna_height',
        'title': 'Antenna Height',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'polarisation',
        'title': 'Polarisation',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'mount_type',
        'title': 'SS Mount Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'antenna_type',
        'title': 'Antenna Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'cable_length',
        'title': 'Cable Length',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'ethernet_extender',
        'title': 'Ethernet Extender',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'building_height',
        'title': 'Building Height',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'tower_height',
        'title': 'Tower/Pole Height',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'ss_technology',
        'title': 'Technology',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'lat_lon',
        'title' : 'Lat, Long',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'customer_address',
        'title': 'Customer Address',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'alias',
        'title': 'Alias',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'dl_rssi_during_acceptance',
        'title': 'RSSI During Acceptance',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'date_of_acceptance',
        'title': 'Date of Acceptance',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'pos_link1',
        'title': 'POS Link1',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'pos_link2',
        'title': 'POS Link2',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    }
];

// PTP SS Tooltip polled info object
var ptp_ss_toolTip_polled = [
    {
        'name'         : 'radwin_producttype_invent_producttype',
        'title'        : 'Product Type',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_producttype_invent',
        'ds'           : 'producttype'
    },
    {
        'name'         : 'radwin_frequency_invent_frequency',
        'title'        : 'Frequency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_frequency_invent',
        'ds'           : 'frequency'
    },
    {
        'name'         : 'radwin_cbw_invent_cbw',
        'title'        : 'Channel Bandwidth',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_cbw_invent',
        'ds'           : 'cbw'
    },
    {
        'name'         : 'radwin_uas_uas',
        'title'        : 'UAS',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_uas',
        'ds'           : 'uas'
    },
    {
        'name'         : 'radwin_rssi_rssi',
        'title'        : 'RSSI',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_rssi',
        'ds'           : 'rssi'
    },
    {
        'name'         : 'radwin_service_throughput_service_throughput',
        'title'        : 'Throughput',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_service_throughput',
        'ds'           : 'service_throughput'
    },
    {
        'name'         : 'radwin_crc_errors_crc_errors',
        'title'        : 'CRC Error',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_crc_errors',
        'ds'           : 'crc_errors'
    },
    {
        'name'         : 'radwin_link_distance_invent_link_distance',
        'title'        : 'Link Distance (mtr)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_link_distance_invent',
        'ds'           : 'link_distance'
    },
    {
        'name'         : 'radwin_ul_utilization_Management_Port_on_Odu',
        'title'        : 'Uplink Utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_ul_utilization',
        'ds'           : 'Management_Port_on_Odu'
    },
    {
        'name'         : 'radwin_dl_utilization_Management_Port_on_Odu',
        'title'        : 'Downlink Utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_dl_utilization',
        'ds'           : 'Management_Port_on_Odu'
    },
    {
        'name'         : 'radwin_uptime_uptime',
        'title'        : 'Device Uptime',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_uptime',
        'ds'           : 'uptime'
    },
    {
        'name'         : 'radwin_autonegotiation_status_1',
        'title'        : 'Auto Negotiation',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_autonegotiation_status',
        'ds'           : '1'
    },
    {
        'name'         : 'radwin_port_mode_status_1',
        'title'        : 'Duplex',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_port_mode_status',
        'ds'           : '1'
    },
    {
        'name'         : 'radwin_port_speed_status_1',
        'title'        : 'Speed',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_port_speed_status',
        'ds'           : '1'
    },
    {
        'name'         : 'radwin_link_ethernet_status_Management_Port_on_Odu',
        'title'        : 'Link Ethernet Status',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_link_ethernet_status',
        'ds'           : 'Management_Port_on_Odu'
    },
    {
        'name'         : 'radwin_mimo_diversity_invent_mimo_diversity',
        'title'        : 'Mimo Diversity',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_mimo_diversity_invent',
        'ds'           : 'mimo_diversity'
    },
    {
        'name'         : 'radwin_ssid_invent_ssid',
        'title'        : 'SSID',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_ssid_invent',
        'ds'           : 'ssid'
    },
    {
        'name'         : 'radwin_idu_sn_invent_idu_sn',
        'title'        : 'IDU S/N',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_idu_sn_invent',
        'ds'           : 'idu_sn'
    },
    {
        'name'         : 'radwin_odu_sn_invent_odu_sn',
        'title'        : 'ODU S/N',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_odu_sn_invent',
        'ds'           : 'odu_sn'
    },
    {
        'name'         : 'pl',
        'title'        : 'Packet Loss',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'pl'
    },
    {
        'name'         : 'rta',
        'title'        : 'Latency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'rta'
    }
];

// PTP Sector Tooltip static info object
var ptp_sector_toolTip_static = [
    {
        'name'  : 'cktid',
        'title' : 'Circuit ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'customer_alias',
        'title' : 'Customer Name',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'idu_ip',
        'title': 'Near End IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'pe_ip',
        'title': 'PE IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'qos_bandwidth',
        'title' : 'QOS(BW)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'hssu_used',
        'title' : 'HSSU Used',
        'show'  : 1,
        'value' : 'NA',
        'url'   : ''
    },
    {
        'name'  : 'hssu_port',
        'title' : 'HSSU Port',
        'show'  : 1,
        'value' : 'NA',
        'url'   : ''
    },
    {
        'name'  : 'bh_bso',
        'title' : 'BH BSO',
        'show'  : 1,
        'value' : 'NA',
        'url'   : ''
    },
    {
        'name': 'antenna_height',
        'title': 'Antenna Height',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'antenna_polarization',
        'title': 'Polarisation',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'mount_type',
        'title': 'SS Mount Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'cable_length',
        'title': 'Cable Length',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'ethernet_extender',
        'title': 'Ethernet Extender',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'building_height',
        'title': 'Building Height',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'tower_height',
        'title': 'Tower/Pole Height',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'technology',
        'title': 'Technology',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'lat_lon',
        'title' : 'Lat, Long',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'customer_address',
        'title': 'Customer Address',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'sector_alias',
        'title': 'Alias',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'dl_rssi_during_acceptance',
        'title': 'RSSI During Acceptance',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'date_of_acceptance',
        'title': 'Date of Acceptance',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'pos_link1',
        'title': 'POS Link1',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name': 'pos_link2',
        'title': 'POS Link2',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    }
];

// PTP Sector Tooltip polled info object
var ptp_sector_toolTip_polled = [
    {
        'name'         : 'radwin_producttype_invent_producttype',
        'title'        : 'Product Type',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_producttype_invent',
        'ds'           : 'producttype'
    },
    {
        'name'         : 'radwin_frequency_invent_frequency',
        'title'        : 'Frequency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_frequency_invent',
        'ds'           : 'frequency'
    },
    {
        'name'         : 'radwin_cbw_invent_cbw',
        'title'        : 'Channel Bandwidth',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_cbw_invent',
        'ds'           : 'cbw'
    },
    {
        'name'         : 'radwin_uas_uas',
        'title'        : 'UAS',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_uas',
        'ds'           : 'uas'
    },
    {
        'name'         : 'radwin_rssi_rssi',
        'title'        : 'RSSI',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_rssi',
        'ds'           : 'rssi'
    },
    {
        'name'         : 'radwin_service_throughput_service_throughput',
        'title'        : 'Estimated Throughput',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_service_throughput',
        'ds'           : 'service_throughput'
    },
    {
        'name'         : 'radwin_crc_errors_crc_errors',
        'title'        : 'CRC Error',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_crc_errors',
        'ds'           : 'crc_errors'
    },
    {
        'name'         : 'radwin_link_distance_invent_link_distance',
        'title'        : 'Link Distance (mtr)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_link_distance_invent',
        'ds'           : 'link_distance'
    },
    {
        'name'         : 'radwin_ul_utilization_Management_Port_on_Odu',
        'title'        : 'Uplink Utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_ul_utilization',
        'ds'           : 'Management_Port_on_Odu'
    },
    {
        'name'         : 'radwin_dl_utilization_Management_Port_on_Odu',
        'title'        : 'Downlink Utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_dl_utilization',
        'ds'           : 'Management_Port_on_Odu'
    },
    // {
    //     'name'      : 'session_uptime',
    //     'title'     : 'Session Uptime',
    //     'show'      : 1,
    //     'value'     : '',
    //     'url'       : ''
    // },
    {
        'name'         : 'radwin_uptime_uptime',
        'title'        : 'Device Uptime',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_uptime',
        'ds'           : 'uptime'
    },
    {
        'name'         : 'radwin_autonegotiation_status_1',
        'title'        : 'Auto Negotiation',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_autonegotiation_status',
        'ds'           : '1'
    },
    {
        'name'         : 'radwin_port_mode_status_1',
        'title'        : 'Duplex',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_port_mode_status',
        'ds'           : '1'
    },
    {
        'name'         : 'radwin_port_speed_status_1',
        'title'        : 'Speed',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_port_speed_status',
        'ds'           : '1'
    },
    {
        'name'         : 'radwin_link_ethernet_status_Management_Port_on_Odu',
        'title'        : 'Link Ethernet Status',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_link_ethernet_status',
        'ds'           : 'Management_Port_on_Odu'
    },
    {
        'name'         : 'radwin_sync_state_status_site_sync_state',
        'title'        : 'Sync State',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_sync_state_status',
        'ds'           : 'site_sync_state'
    },
    {
        'name'         : 'radwin_mimo_diversity_invent_mimo_diversity',
        'title'        : 'Mimo Diversity',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_mimo_diversity_invent',
        'ds'           : 'mimo_diversity'
    },
    {
        'name'         : 'radwin_ssid_invent_ssid',
        'title'        : 'SSID',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_ssid_invent',
        'ds'           : 'ssid'
    },
    {
        'name'         : 'radwin_idu_sn_invent_idu_sn',
        'title'        : 'IDU S/N',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_idu_sn_invent',
        'ds'           : 'idu_sn'
    },
    {
        'name'         : 'radwin_odu_sn_invent_odu_sn',
        'title'        : 'ODU S/N',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin_odu_sn_invent',
        'ds'           : 'odu_sn'
    },
    {
        'name'         : 'pl',
        'title'        : 'Packet Loss',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'pl'
    },
    {
        'name'         : 'rta',
        'title'        : 'Latency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'rta'
    }
];

// PMP SS Tooltip static info object
var pmp_ss_toolTip_static = [];
// PMP SS Tooltip polled info object for radwin 5k
var pmp_radwin5k_ss_toolTip_polled = [
    {
        'name'         : 'rad5k_ss_ul_utilization_ul_utilization',
        'title'        : 'Uplink utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_ul_utilization',
        'ds'           : 'ul_utilization'
    },
    {
        'name'         : 'rad5k_ss_dl_utilization_dl_utilization',
        'title'        : 'DL utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_dl_utilization',
        'ds'           : 'dl_utilization'
    },
    {
        'name'         : 'rad5k_ul_rssi_ul_rssi',
        'title'        : 'UL RSSI 1',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ul_rssi',
        'ds'           : 'ul_rssi'
    },
    {
        'name'         : 'rad5k_dl_rssi_dl_rssi',
        'title'        : 'DL RSSI 1',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_dl_rssi',
        'ds'           : 'dl_rssi'
    },
    {
        'name'         : 'rad5k_ss2_ul_rssi_ul_2rssi',
        'title'        : 'UL RSSI 2',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss2_ul_rssi',
        'ds'           : 'ul_2rssi'
    },
    {
        'name'         : 'rad5k_ss2_dl_rssi_dl_2rssi',
        'title'        : 'DL RSSI 2',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss2_dl_rssi',
        'ds'           : 'dl_2rssi'
    },
    {
        'name'         : 'rad5k_ss_data_vlan_invent_ss_data_vlan',
        'title'        : 'Data VLAN',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_data_vlan_invent',
        'ds'           : 'ss_data_vlan'
    },
    {
        'name'         : 'rad5k_man_vlan_invent_ss_vlan',
        'title'        : 'Management VLAN',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_man_vlan_invent',
        'ds'           : 'ss_vlan'
    },
    {
        'name'         : 'rad5k_ss_device_uptime_uptime',
        'title'        : 'Device Uptime',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_device_uptime',
        'ds'           : 'uptime'
    },
    {
        'name'         : 'rad5k_ss_auto_neg_status_autonegotiation',
        'title'        : 'Auto Negotiation',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_auto_neg_status',
        'ds'           : 'autonegotiation'
    },
    {
        'name'         : 'rad5k_duplex_status_duplex',
        'title'        : 'Duplex',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_duplex_status',
        'ds'           : 'duplex'
    },
    {
        'name'         : 'rad5k_speed_status_ss_speed',
        'title'        : 'Speed',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_speed_status',
        'ds'           : 'ss_speed'
    },
    {
        'name'         : 'rad5k_eth_link_status_link_state',
        'title'        : 'Link Ethernet Status',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_eth_link_status',
        'ds'           : 'link_state'
    },
    {
        'name'         : 'rad5k_ss_transmit_power_transmit_power',
        'title'        : 'SM transmit power',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_transmit_power',
        'ds'           : 'transmit_power'
    },
    {
        'name'         : 'rad5k_ss_mac_ss_mac',
        'title'        : 'HSU MAC',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_mac',
        'ds'           : 'ss_mac'
    },
    {
        'name'         : 'rad5k_ss_sector_id_sector_id',
        'title'        : 'Sector ID',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_sector_id',
        'ds'           : 'sector_id'
    },
    {
        'name'         : 'rad5k_ss_conn_bs_ip_invent_bs_ip',
        'title'        : 'Connected HBS IP',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_conn_bs_ip_invent',
        'ds'           : 'bs_ip'
    },
    {
        'name'         : 'rad5k_ss_frequency_frequency',
        'title'        : 'Frequency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_frequency',
        'ds'           : 'frequency'
    },
    {
        'name'         : 'pl',
        'title'        : 'Packet Loss',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'pl'
    },
    {
        'name'         : 'rta',
        'title'        : 'Latency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'rta'
    },
    {
        'name'         : 'rad5k_ss_dl_uas_dl_uas',
        'title'        : 'DL UAS',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_dl_uas',
        'ds'           : 'dl_uas'
    },
    {
        'name'         : 'rad5k_ss_ul_uas_ul_uas',
        'title'        : 'UL UAS',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_ul_uas',
        'ds'           : 'ul_uas'
    },
    {
        'name'         : 'radwin5k_ss_ul_dyn_tl_kpi_rad5k_ss_ul_dyn_tl',
        'title'        : 'UL timeslots',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin5k_ss_ul_dyn_tl_kpi',
        'ds'           : 'rad5k_ss_ul_dyn_tl'
    },
    {
        'name'         : 'radwin5k_ss_dl_dyn_tl_kpi_rad5k_ss_dl_dyn_tl',
        'title'        : 'DL timeslots',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'radwin5k_ss_dl_dyn_tl_kpi',
        'ds'           : 'rad5k_ss_dl_dyn_tl'
    },
    {
        'name'         : 'rad5k_ss_crc_error_status_crc_errors',
        'title'        : 'CRC Errors',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_crc_error_status',
        'ds'           : 'crc_errors'
    },
    {
        'name'         : 'rad5k_ss_session_uptime_session_uptime',
        'title'        : 'Session Uptime',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_session_uptime',
        'ds'           : 'session_uptime'
    },
    {
        'name'         : 'rad5k_ss_ul_estmd_throughput_ul_estimated_throughput',
        'title'        : 'UL Est. throughput (bps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_ul_estmd_throughput',
        'ds'           : 'ul_estimated_throughput'
    },
    {
        'name'         : 'rad5k_ss_dl_estmd_throughput_dl_estimated_throughput',
        'title'        : 'DL Est. throughput (bps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_ss_dl_estmd_throughput',
        'ds'           : 'dl_estimated_throughput'
    },
    {
        'name'         : '',
        'title'        : 'QOS',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : '',
        'ds'           : ''
    },
];

var pmp_radwin5k_sector_toolTip_polled = [
    {
        'name'         : 'rad5k_bs_dl_utilization_dl_utilization',
        'title'        : 'Utilisation DL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_bs_dl_utilization',
        'ds'           : 'dl_utilization'
    },
    {
        'name'         : 'rad5k_bs_ul_utilization_ul_utilization',
        'title'        : 'Utilisation UL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_bs_ul_utilization',
        'ds'           : 'ul_utilization'
    },
    {
        'name'         : 'rad5k_channel_bw_invent_cbw',
        'title'        : 'Channel Bandwidth',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_channel_bw_invent',
        'ds'           : 'cbw'
    },
    //{
    //    'name'         : '',
    //    'title'        : 'Connected HSUb v                                                                                         v  - Serial No',
    //    'show'         : 1,
    //    'value'        : '',
    //    'url'          : '',
    //    'service_name' : '',
    //    'ds'           : ''
    //},
    {
        'name'         : 'rad5k_bs_crc_error_invent_crc_errors',
        'title'        : 'CRC errors',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_bs_crc_error_invent',
        'ds'           : 'crc_errors'
    },
    {
        'name'         : 'rad5k_bs_frequency_invent_frequency',
        'title'        : 'Frequency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_bs_frequency_invent',
        'ds'           : 'frequency'
    },
    {
        'name'         : 'rad5k_bs_ip_invent_bs_ip',
        'title'        : 'HBS IP',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_bs_ip_invent',
        'ds'           : 'bs_ip'
    },
    {
        'name'         : 'rad5k_bs_mac_invent_bs_mac',
        'title'        :'HBS MAC',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_bs_mac_invent',
        'ds'           : 'bs_mac'
    },
    {
        'name'         : 'rad5k_gps_sync_invent_site_sync_state',
        'title'        : 'Master-Slave (GPS sync)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_gps_sync_invent',
        'ds'           : 'site_sync_state'
    },
    {
        'name'         : 'rad5k_mimo_diversity_invent_mimo_diversity',
        'title'        : 'Mimo/Diversity',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_mimo_diversity_invent',
        'ds'           : 'mimo_diversity'
    },
    {
        'name'         : 'rad5k_odu_type_invent_odu_type',
        'title'        : 'ODU Type',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_odu_type_invent',
        'ds'           : 'odu_type'

    },
    {
        'name'         : 'rad5k_bs_sector_id_invent_bs_sector_id',
        'title'        : 'Sector ID',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_bs_sector_id_invent',
        'ds'           : 'bs_sector_id'

    },
    {
        'name'         : 'rad5k_bs_serial_no_invent_serial_number',
        'title'        : 'Serial Number',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_bs_serial_no_invent',
        'ds'           : 'serial_number'

    },
    {
        'name'         : 'rad5k_bs_system_uptime_uptime',
        'title'        : 'System Uptime',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_bs_system_uptime',
        'ds'           : 'uptime'
    },
    {
        'name'         : 'rad5k_bs_transmit_power_invent_transmit_power',
        'title'        : 'Transmit power',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'rad5k_bs_transmit_power_invent',
        'ds'           : 'transmit_power'
    }
];


// PMP SS Tooltip polled info object
var pmp_ss_toolTip_polled = [
    {
        'name'         : 'cambium_ss_ul_utilization_ul_utilization',
        'title'        : 'Uplink Utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_ss_ul_utilization',
        'ds'           : 'ul_utilization'
    },
    {
        'name'         : 'cambium_dl_utilization_dl_utilization',
        'title'        : 'Downlink Utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_ss_dl_utilization',
        'ds'           : 'dl_utilization'
    },
    {
        'name'         : 'cambium_vlan_invent_vlan',
        'title'        : 'VLAN',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_vlan_invent',
        'ds'           : 'vlan'
    },
    {
        'name'         : 'cambium_qos_invent_bw_ul_sus_rate',
        'title'        : 'QOS(Polled)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_qos_invent',
        'ds'           : 'bw_ul_sus_rate'
    },
    // {
    //     'name'      : 'session_uptime',
    //     'title'     : 'Session Uptime',
    //     'show'      : 1,
    //     'value'     : '',
    //     'url'       : '',
        // 'service_name' : '',
        // 'ds'           : ''
    // },
    {
        'name'         : 'cambium_uptime_uptime',
        'title'        : 'Device Uptime',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_uptime',
        'ds'           : 'uptime'
    },
    {
        'name'         : 'cambium_port_auto_status_autonegotiation',
        'title'        : 'Auto Negotiation',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_port_auto_status',
        'ds'           : 'autonegotiation'
    },
    {
        'name'         : 'cambium_port_duplex_status_duplex',
        'title'        : 'Duplex',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_port_duplex_status',
        'ds'           : 'duplex'
    },
    {
        'name'         : 'cambium_port_speed_status_ss_speed',
        'title'        : 'Speed',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_port_speed_status',
        'ds'           : 'ss_speed'
    },
    {
        'name'         : 'cambium_link_ethernet_status_link_state',
        'title'        : 'Link Ethernet Status',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_link_ethernet_status',
        'ds'           : 'link_state'
    },
    {
        'name'         : 'cambium_dl_rssi_dl_rssi',
        'title'        : 'RSSI DL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_dl_rssi',
        'ds'           : 'dl_rssi'
    },
    {
        'name'         : 'cambium_dl_jitter_dl_jitter',
        'title'        : 'Jitter DL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_dl_jitter',
        'ds'           : 'dl_jitter'
    },
    {
        'name'         : 'cambium_ul_rssi_ul_rssi',
        'title'        : 'RSSI UL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_ul_rssi',
        'ds'           : 'ul_rssi'
    },
    {
        'name'         : 'cambium_ul_jitter_ul_jitter',
        'title'        : 'Jitter UL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_ul_jitter',
        'ds'           : 'ul_jitter'
    },
    {
        'name'         : 'cambium_rereg_count_rereg_count',
        'title'        : 'Rereg Count',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_rereg_count',
        'ds'           : 'rereg_count'
    },
    {
        'name'         : 'cambium_reg_count_reg_count',
        'title'        : 'Reg Count',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_reg_count',
        'ds'           : 'reg_count'
    },
    {
        'name'         : 'cambium_transmit_power_invent_transmit_power',
        'title'        : 'SM Transmit Power',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_transmit_power_invent',
        'ds'           : 'transmit_power'
    },
    {
        'name'         : 'cambium_ss_mac_invent_ss_mac',
        'title'        : 'SS MAC',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_ss_mac_invent',
        'ds'           : 'ss_mac'
    },
    {
        'name'         : 'cambium_ss_sector_id_invent_ss_sector_id',
        'title'        : 'Sector ID',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_ss_sector_id_invent',
        'ds'           : 'ss_sector_id'
    },
    {
        'name'         : 'cambium_ss_connected_bs_ip_invent_bs_ip',
        'title'        : 'Connected BS IP',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_ss_connected_bs_ip_invent',
        'ds'           : 'bs_ip'

    },

    // {
    //     'name'      : '',
    //     'title'     : 'If Out Errors',
    //     'show'      : 1,
    //     'value'     : '',
    //     'url'       : '',
        // 'service_name' : '',
        // 'ds'           : ''
    // },
    // {
    //     'name'      : '',
    //     'title'     : 'If In Errors',
    //     'show'      : 1,
    //     'value'     : '',
    //     'url'       : '',
        // 'service_name' : '',
        // 'ds'           : ''
    // },
    {
        'name'         : 'cambium_ss_frequency_invent_frequency',
        'title'        : 'Frequency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_ss_frequency_invent',
        'ds'           : 'frequency'
    },
    {
        'name'         : 'pl',
        'title'        : 'Packet Loss',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'pl'
    },
    {
        'name'         : 'rta',
        'title'        : 'Latency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'rta'
    }
];

// PMP Sector Tooltip static info object
var pmp_sector_toolTip_static = [
    {
        'name'  : 'technology',
        'title' : 'Technology',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'sector_id',
        'title' : 'Sector ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'idu_ip',
        'title' : 'IDU IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'frequency',
        'title' : 'Planned Frequency',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'antenna_height',
        'title' : 'Antenna Height',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'antenna_polarization',
        'title' : 'Antenna Polarization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'ugps_installed',
        'title' : 'UGPS Installed',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'tx_power_planned',
        'title' : 'Tx Power Planned',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rx_power_planned',
        'title' : 'Rx Power Planned',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'antenna_azimuth',
        'title' : 'Antenna Azimuth',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'antenna_make',
        'title' : 'Antenna Make',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'sync_splitter',
        'title' : 'Sync Splitter Installed',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    }
];

// PMP Sector Tooltip polled info object
var pmp_sector_toolTip_polled = [
    {
        'name'         : 'cambium_bs_frequency_invent_frequency',
        'title'        : 'Polled Frequency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_bs_frequency_invent',
        'ds'           : 'frequency'
    },
    {
        'name'         : 'cambium_transmit_power_invent_transmit_power',
        'title'        : 'Tx Power Polled',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_transmit_power_invent',
        'ds'           : 'transmit_power'
    },
    {
        'name'         : 'cambium_commanded_rx_power_invent_commanded_rx_power',
        'title'        : 'Rx Power Polled',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_commanded_rx_power_invent',
        'ds'           : 'commanded_rx_power'
    },
    {
        'name'         : 'cambium_ul_utilization_ul_utilization',
        'title'        : 'Sector UL Utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_ul_utilization',
        'ds'           : 'ul_utilization'
    },
    {
        'name'         : 'cambium_dl_utilization_dl_utilization',
        'title'        : 'Sector DL Utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_dl_utilization',
        'ds'           : 'dl_utilization'
    },
    {
        'name'         : 'cambium_uptime_uptime',
        'title'        : 'Sector Uptime',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_uptime',
        'ds'           : 'uptime'
    },
    {
        'name'         : '',
        'title'        : 'Interface eth Error',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : '',
        'ds'           : ''
    },
    {
        'name'         : 'cambium_sync_state_invent_sync_state',
        'title'        : 'Sync State',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_sync_state_invent',
        'ds'           : 'sync_state'
    },
    {
        'name'         : 'cambium_data_rate_modulation_invent_data_rate_modulation',
        'title'        : 'Data Rate',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_data_rate_modulation_invent',
        'ds'           : 'data_rate_modulation'
    },
    {
        'name'         : '',
        'title'        : 'TDD Split',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : '',
        'ds'           : ''
    },
    {
        'name'         : '',
        'title'        : 'Last GPS Alert Time',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : '',
        'ds'           : ''
    },
    {
        'name'         : 'cambium_cell_radius_invent_cell_radius',
        'title'        : 'Cell Radius',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'cambium_cell_radius_invent',
        'ds'           : 'cell_radius'
    },
    {
        'name'         : 'rta',
        'title'        : 'Latency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'rta'
    },
    {
        'name'         : 'pl',
        'title'        : 'Packet Loss',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'pl'
    }
];

// Wimax SS Tooltip static info object
var wimax_ss_toolTip_static = [];

// Wimax SS Tooltip Polled Info Object
var wimax_ss_toolTip_polled = [
    {
        'name'         : 'pl',
        'title'        : 'Packet Loss',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'pl'
    },
    {
        'name'         : 'rta',
        'title'        : 'Latency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'rta'
    },
    {
        'name'         : 'wimax_ss_ul_utilization_ul_utilization',
        'title'        : 'Uplink Utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_ul_utilization',
        'ds'           : 'ul_utilization'
    },
    {
        'name'         : 'wimax_ss_dl_utilization_dl_utilization',
        'title'        : 'Downlink Utilization (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_dl_utilization',
        'ds'           : 'dl_utilization'
    },
    {
        'name'         : 'wimax_ss_vlan_invent_ss_vlan',
        'title'        : 'VLAN',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_vlan_invent',
        'ds'           : 'ss_vlan'
    },
    {
        'name'         : 'wimax_qos_invent_ul_qos',
        'title'        : 'QOS(Polled)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_qos_invent',
        'ds'           : 'ul_qos'
    },
    {
        'name'         : 'wimax_ss_session_uptime_session_uptime',
        'title'        : 'Session Uptime',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_session_uptime',
        'ds'           : 'session_uptime'
    },
    {
        'name'         : 'wimax_ss_uptime_uptime',
        'title'        : 'Device Uptime',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_uptime',
        'ds'           : 'uptime'
    },
    {
        'name'         : 'wimax_ss_autonegotiation_status_autonegotiation',
        'title'        : 'Auto Negotiation',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_autonegotiation_status',
        'ds'           : 'autonegotiation'
    },
    {
        'name'         : 'wimax_ss_duplex_status_duplex',
        'title'        : 'Duplex',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_duplex_status',
        'ds'           : 'duplex'
    },
    {
        'name'         : 'wimax_ss_speed_status_ss_speed',
        'title'        : 'Speed',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_speed_status',
        'ds'           : 'ss_speed'
    },
    {
        'name'         : 'wimax_ss_link_status_link_state',
        'title'        : 'Link Ethernet Status',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_link_status',
        'ds'           : 'link_state'
    },
    {
        'name'         : 'wimax_dl_rssi_dl_rssi',
        'title'        : 'RSSI DL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_dl_rssi',
        'ds'           : 'dl_rssi'
    },
    {
        'name'         : 'wimax_dl_intrf_dl_intrf',
        'title'        : 'INTRF DL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_dl_intrf',
        'ds'           : 'dl_intrf'
    },
    {
        'name'         : 'wimax_dl_cinr_dl_cinr',
        'title'        : 'CINR DL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_dl_cinr',
        'ds'           : 'dl_cinr'
    },
    {
        'name'         : 'wimax_ul_rssi_ul_rssi',
        'title'        : 'RSSI UL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ul_rssi',
        'ds'           : 'ul_rssi'
    },
    {
        'name'         : 'wimax_ul_intrf_ul_intrf',
        'title'        : 'INTRF UL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ul_intrf',
        'ds'           : 'ul_intrf'
    },
    {
        'name'         : 'wimax_ul_cinr_ul_cinr',
        'title'        : 'CINR UL',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ul_cinr',
        'ds'           : 'ul_cinr'
    },
    {
        'name'         : 'wimax_modulation_ul_fec_modulation_ul_fec',
        'title'        : 'Modulation UL FEC',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_modulation_ul_fec',
        'ds'           : 'modulation_ul_fec'
    },
    {
        'name'         : 'wimax_modulation_dl_fec_modulation_dl_fec',
        'title'        : 'Modulation DL FEC',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_modulation_dl_fec',
        'ds'           : 'modulation_dl_fec'
    },
    {
        'name'         : 'wimax_ss_ptx_invent_ss_ptx',
        'title'        : 'PTX',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_ptx_invent',
        'ds'           : 'ss_ptx'
    },
    {
        'name'         : 'wimax_ss_mac_ss_mac',
        'title'        : 'SS MAC',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_mac',
        'ds'           : 'ss_mac'
    },
    {
        'name'         : 'wimax_ss_sector_id_ss_sector_id',
        'title'        : 'Sector ID',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_sector_id',
        'ds'           : 'ss_sector_id'
    },
    {
        // 'name'      : 'wimax_bs_ip_invent_bs_ip',
        'name'         : 'connected_bs_ip',
        'title'        : 'Connected BS IP',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : '',
        'ds'           : ''
    },
    {
        'name'         : 'wimax_ss_errors_status_ifout_errors',
        'title'        : 'If Out Error',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_errors_status',
        'ds'           : 'ifout_errors'
    },
    {
        'name'         : 'wimax_ss_errors_status_ifin_errors',
        'title'        : 'If In Error',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_errors_status',
        'ds'           : 'ifin_errors'
    },
    {
        'name'         : 'wimax_ss_frequency_frequency',
        'title'        : 'Frequency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_ss_frequency',
        'ds'           : 'frequency'
    },
    {
        'name'         : 'wimax_dl_modulation_change_invent_dl_modulation_change',
        'title'        : 'Downlink Modulation Change',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_dl_modulation_change_invent',
        'ds'           : 'dl_modulation_change'
    }
];

// Wimax Sector Tooltip static info object
var wimax_sector_toolTip_static = [
    {
        'name'  : 'technology',
        'title' : 'Technology',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'sector_id',
        'title' : 'Sector ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'idu_ip',
        'title' : 'IDU IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'pmp_port',
        'title' : 'PMP Port',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'frequency',
        'title' : 'Planned Frequency',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'antenna_height',
        'title' : 'Antenna Height',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'antenna_polarization',
        'title' : 'Antenna Polarization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'dr_status',
        'title' : 'DR Status',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'mrc_status',
        'title' : 'MRC Status',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'tx_power_planned',
        'title' : 'Tx Power Planned',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rx_power_planned',
        'title' : 'Rx Power Planned',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'antenna_azimuth',
        'title' : 'Antenna Azimuth',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'antenna_make',
        'title' : 'Antenna Make',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'antenna_tilt',
        'title' : 'Antenna Tilt',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'antenna_splitter_installed',
        'title' : 'Splitter Installed',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'frame_length',
        'title' : 'Frame Length',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    }
];

// Wimax Sector Tooltip polled info object
var wimax_sector_toolTip_polled = [
    {
        'name'         : 'wimax_pmp1_frequency_invent_frequency',
        'title'        : 'Polled Frequency[PMP1]',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_pmp1_frequency_invent',
        'ds'           : 'frequency'
    },
    {
        'name'         : 'wimax_pmp2_frequency_invent_frequency',
        'title'        : 'Polled Frequency [PMP2]',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_pmp2_frequency_invent',
        'ds'           : 'frequency'
    },
    {
        'name'         : 'wimax_transmit_power_pmp1_invent_transmit_power_pmp1',
        'title'        : 'Tx Power Polled [PMP1]',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_transmit_power_pmp1_invent',
        'ds'           : 'transmit_power_pmp1'
    },
    {
        'name'         : 'wimax_transmit_power_pmp2_invent_transmit_power_pmp2',
        'title'        : 'Tx Power Polled [PMP2]',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_transmit_power_pmp2_invent',
        'ds'           : 'transmit_power_pmp2'
    },
    {
        'name'         : 'wimax_p1_cmd_rx_pwr_invent_p1_cmd_rx_pwr',
        'title'        : 'Rx Power Polled [PMP1]',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_p1_cmd_rx_pwr_invent',
        'ds'           : 'p1_cmd_rx_pwr'
    },
    {
        'name'         : 'wimax_p2_cmd_rx_pwr_invent_p2_cmd_rx_pwr',
        'title'        : 'Rx Power Polled [PMP2]',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_p2_cmd_rx_pwr_invent',
        'ds'           : 'p2_cmd_rx_pwr'
    },
    {
        'name'         : 'wimax_pmp1_ul_util_bgp_pmp1_ul_util',
        'title'        : 'Sector UL Utilization [PMP1] (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_pmp1_ul_util_bgp',
        'ds'           : 'pmp1_ul_util'
    },
    {
        'name'         : 'wimax_pmp1_dl_util_bgp_pmp1_dl_util',
        'title'        : 'Sector DL Utilization [PMP1] (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_pmp1_dl_util_bgp',
        'ds'           : 'pmp1_dl_util'
    },
    {
        'name'         : 'wimax_pmp2_ul_util_bgp_pmp2_ul_util',
        'title'        : 'Sector UL Utilization [PMP2] (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_pmp2_ul_util_bgp',
        'ds'           : 'pmp2_ul_util'
    },
    {
        'name'         : 'wimax_pmp2_dl_util_bgp_pmp2_dl_util',
        'title'        : 'Sector DL Utilization [PMP2] (Mbps)',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_pmp2_dl_util_bgp',
        'ds'           : 'pmp2_dl_util'
    },
    {
        'name'         : 'wimax_bs_uptime_uptime',
        'title'        : 'IDU Uptime',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_bs_uptime',
        'ds'           : 'uptime'
    },
    {
        'name'         : 'wimax_pmp_bw_invent_pmp1_bw',
        'title'        : 'RF BW Polled [PMP1]',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_pmp_bw_invent',
        'ds'           : 'pmp1_bw'
    },
    {
        'name'         : 'wimax_pmp_bw_invent_pmp2_bw',
        'title'        : 'RF BW Polled [PMP2]',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_pmp_bw_invent',
        'ds'           : 'pmp2_bw'
    },
    {
        'name'         : '',
        'title'        : 'Last GPS Alert Time',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : '',
        'ds'           : ''
    },
    {
        'name'         : 'wimax_bs_temperature_acb_acb_temp',
        'title'        : 'Temperature ACB',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_bs_temperature_acb',
        'ds'           : 'acb_temp'
    },
    {
        'name'         : 'wimax_bs_temperature_fan_fan_temp',
        'title'        : 'Temperature Fan',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'wimax_bs_temperature_fan',
        'ds'           : 'fan_temp'
    },
    {
        'name'         : 'rta',
        'title'        : 'Latency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'rta'
    },
    {
        'name'         : 'pl',
        'title'        : 'Packet Loss',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'pl'
    }
];

var common_toolTip_poll_now = [
    {
        'name'         : 'rta',
        'title'        : 'Latency',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'rta'
    },
    {
        'name'         : 'pl',
        'title'        : 'Packet Loss',
        'show'         : 1,
        'value'        : '',
        'url'          : '',
        'service_name' : 'ping',
        'ds'           : 'pl'
    }
]

/**
 * This function return array of object in desired sequence as per given param.
 * @method rearrangeTooltipArray.
 * @param correct_info_list {Array}, It contains the actual sequence of tooltip info.
 * @param backend_info_list {Array}, It contains the backend response array object of tooltip info.
 * @return updated_info_list {Array}, It contains the updated sequence of backend response as per actual sequence of tooltip.
 */
function rearrangeTooltipArray(correct_info_list,backend_info_list) {
    var updated_info_list = [],
        extra_info_list = [];
    // Loop actual info object array
    correct_info_loop:
    for(var i=0;i<correct_info_list.length;i++) {

        var correct_info = correct_info_list[i],
            correct_info_name = correct_info.name ? $.trim(correct_info.name) : "",
            current_info_obj = JSON.parse(JSON.stringify(correct_info));

        // Loop backend response info object array
        backend_info_loop:
        for(var j=0;j<backend_info_list.length;j++) {

            var backend_info = backend_info_list[j],
                backend_info_name = backend_info.name ? $.trim(backend_info.name) : "";
            // console.log(correct_info_name + ' === ' + backend_info_name);
            // if info name's are same
            if(correct_info_name == backend_info_name) {
                var url = backend_info["url"] ? backend_info["url"] : "",
                    severity = backend_info["severity"] ? backend_info["severity"] : "";

                current_info_obj["value"] = backend_info["value"];
                current_info_obj["show"] = backend_info["show"];
                current_info_obj["url"] = url;
                current_info_obj["severity"] = severity;

                break backend_info_loop;
            }
        }

        // Push info object to array
        updated_info_list.push(current_info_obj);
    }

    // Get extra info come from backend
    // var extra_info = getUncommonData(correct_info_list,backend_info_list);
    // updated_info_list = updated_info_list.concat(extra_info);

    return updated_info_list;
}


/**
 * This function returns the unmatched dict items between given two
 * @method getUncommonData.
 * @param array1 {Array}, It contains the actual sequence of tooltip info.
 * @param array2 {Array}, It contains the backend response array object of tooltip info.
 * @return uncommon_info_list {Array}, It contains the updated sequence of backend response as per actual sequence of tooltip.
 */
function getUncommonData(array1,array2) {
    var uncommon_info_list = [];

    array2_loop:
    for(var i=0;i<array2.length;i++) {
        var current_array2_val = array2[i],
            isPresent = false;
        array1_loop:
        for(var j=0;j<array1.length;j++) {
            var current_array1_val = array1[j];
            if(current_array2_val["name"] == current_array1_val["name"]) {
                isPresent = true;
                break array1_loop;
            }
        }

        if(!isPresent) {
            uncommon_info_list.push(current_array2_val);
        }
    }

    return uncommon_info_list;
}

// Gmap Styles Array
var gmap_styles_array = [
    [
        {
            "featureType": "landscape",
            "stylers": [
                {
                    "hue": "#FFA800"
                },
                {
                    "saturation": 0
                },
                {
                    "lightness": 0
                },
                {
                    "gamma": 1
                }
            ]
        },
        {
            "featureType": "road.highway",
            "stylers": [
                {
                    "hue": "#53FF00"
                },
                {
                    "saturation": -73
                },
                {
                    "lightness": 40
                },
                {
                    "gamma": 1
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "stylers": [
                {
                    "hue": "#FBFF00"
                },
                {
                    "saturation": 0
                },
                {
                    "lightness": 0
                },
                {
                    "gamma": 1
                }
            ]
        },
        {
            "featureType": "road.local",
            "stylers": [
                {
                    "hue": "#00FFFD"
                },
                {
                    "saturation": 0
                },
                {
                    "lightness": 30
                },
                {
                    "gamma": 1
                }
            ]
        },
        {
            "featureType": "water",
            "stylers": [
                {
                    "hue": "#00BFFF"
                },
                {
                    "saturation": 6
                },
                {
                    "lightness": 8
                },
                {
                    "gamma": 1
                }
            ]
        },
        {
            "featureType": "poi",
            "stylers": [
                {
                    "hue": "#679714"
                },
                {
                    "saturation": 33.4
                },
                {
                    "lightness": -25.4
                },
                {
                    "gamma": 1
                }
            ]
        }
    ],
    [
        {
            "featureType": "road",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "simplified"
                },
                {
                    "lightness": 20
                }
            ]
        },
        {
            "featureType": "administrative.land_parcel",
            "elementType": "all",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "landscape.man_made",
            "elementType": "all",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "transit",
            "elementType": "all",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "road.local",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        },
        {
            "featureType": "road.local",
            "elementType": "geometry",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "all",
            "stylers": [
                {
                    "hue": "#a1cdfc"
                },
                {
                    "saturation": 30
                },
                {
                    "lightness": 49
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry",
            "stylers": [
                {
                    "hue": "#f49935"
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "geometry",
            "stylers": [
                {
                    "hue": "#fad959"
                }
            ]
        }
    ],
    [
        {
            "featureType": "water",
            "elementType": "all",
            "stylers": [
                {
                    "hue": "#d7ebef"
                },
                {
                    "saturation": -5
                },
                {
                    "lightness": 54
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "landscape",
            "elementType": "all",
            "stylers": [
                {
                    "hue": "#eceae6"
                },
                {
                    "saturation": -49
                },
                {
                    "lightness": 22
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "poi.park",
            "elementType": "all",
            "stylers": [
                {
                    "hue": "#dddbd7"
                },
                {
                    "saturation": -81
                },
                {
                    "lightness": 34
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "poi.medical",
            "elementType": "all",
            "stylers": [
                {
                    "hue": "#dddbd7"
                },
                {
                    "saturation": -80
                },
                {
                    "lightness": -2
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "poi.school",
            "elementType": "all",
            "stylers": [
                {
                    "hue": "#c8c6c3"
                },
                {
                    "saturation": -91
                },
                {
                    "lightness": -7
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "landscape.natural",
            "elementType": "all",
            "stylers": [
                {
                    "hue": "#c8c6c3"
                },
                {
                    "saturation": -71
                },
                {
                    "lightness": -18
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "all",
            "stylers": [
                {
                    "hue": "#dddbd7"
                },
                {
                    "saturation": -92
                },
                {
                    "lightness": 60
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "all",
            "stylers": [
                {
                    "hue": "#dddbd7"
                },
                {
                    "saturation": -81
                },
                {
                    "lightness": 34
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "all",
            "stylers": [
                {
                    "hue": "#dddbd7"
                },
                {
                    "saturation": -92
                },
                {
                    "lightness": 37
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "transit",
            "elementType": "geometry",
            "stylers": [
                {
                    "hue": "#c8c6c3"
                },
                {
                    "saturation": 4
                },
                {
                    "lightness": 10
                },
                {
                    "visibility": "on"
                }
            ]
        }
    ]
];