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
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'alias',
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

// BH Tooltip polled info object
var bh_toolTip_polled = [
    {
        'name'  : 'converter_temp',
        'title' : 'Converter Temperature',
        'show'  : 0,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'bh_utilization',
        'title' : 'BH Utilization',
        'show'  : 0,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'pl',
        'title' : 'Packet Loss',
        'show'  : 0,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'rta',
        'title' : 'Latency',
        'show'  : 0,
        'value' : '',
        'url'   : ''
    }
];

// General SS Tooltip static info object
var ss_toolTip_static = [
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
		'name'  : 'radwin_producttype_invent_producttype',
        'title' : 'Product Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_frequency_invent_frequency',
        'title' : 'Frequency',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_cbw_invent_cbw',
        'title' : 'Channel Bandwidth',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_uas_uas',
        'title' : 'UAS',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_rssi_rssi',
        'title' : 'RSSI',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_service_throughput_service_throughput',
        'title' : 'Throughput',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_link_distance_invent_link_distance',
        'title' : 'Link Distance',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_ul_utilization_Management_Port_on_Odu',
        'title' : 'Uplink Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_dl_utilization_Management_Port_on_Odu',
        'title' : 'Downlink Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
    {
        'name'  : 'session_uptime',
        'title' : 'Session Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
	{
		'name'  : 'radwin_uptime_uptime',
        'title' : 'Device Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_autonegotiation_status_1',
        'title' : 'Auto Negotiation',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_port_mode_status_1',
        'title' : 'Duplex',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_port_speed_status_1',
        'title' : 'Speed',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_link_ethernet_status_Management_Port_on_Odu',
        'title' : 'Link Ethernet Status',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_mimo_diversity_invent_mimo_diversity',
        'title' : 'Mimo Diversity',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_ssid_invent_ssid',
        'title' : 'SSID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_idu_sn_invent_idu_sn',
        'title' : 'IDU S/N',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_odu_sn_invent_odu_sn',
        'title' : 'ODU S/N',
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
		'name'  : 'radwin_producttype_invent_producttype',
        'title' : 'Product Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_frequency_invent_frequency',
        'title' : 'Frequency',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_cbw_invent_cbw',
        'title' : 'Channel Bandwidth',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_uas_uas',
        'title' : 'UAS',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_rssi_rssi',
        'title' : 'RSSI',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_service_throughput_service_throughput',
        'title' : 'Estimated Throughput',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_link_distance_invent_link_distance',
        'title' : 'Link Distance',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_ul_utilization_Management_Port_on_Odu',
        'title' : 'Uplink Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_dl_utilization_Management_Port_on_Odu',
        'title' : 'Downlink Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
    {
        'name'  : 'session_uptime',
        'title' : 'Session Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
	{
		'name'  : 'radwin_uptime_uptime',
        'title' : 'Device Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_autonegotiation_status_1',
        'title' : 'Auto Negotiation',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_port_mode_status_1',
        'title' : 'Duplex',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_port_speed_status_1',
        'title' : 'Speed',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_link_ethernet_status_Management_Port_on_Odu',
        'title' : 'Link Ethernet Status',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_sync_state_status_site_sync_state',
        'title' : 'Sync State',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_mimo_diversity_invent_mimo_diversity',
        'title' : 'Mimo Diversity',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_ssid_invent_ssid',
        'title' : 'SSID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_idu_sn_invent_idu_sn',
        'title' : 'IDU S/N',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'radwin_odu_sn_invent_odu_sn',
        'title' : 'ODU S/N',
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

// PMP SS Tooltip static info object
var pmp_ss_toolTip_static = [];

// PMP SS Tooltip polled info object
var pmp_ss_toolTip_polled = [
	{
		'name'  : 'cambium_ul_utilization_ul_utilization',
        'title' : 'Uplink Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_dl_utilization_dl_utilization',
        'title' : 'Downlink Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_vlan_invent_vlan',
        'title' : 'VLAN',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_qos_invent_bw_ul_sus_rate',
        'title' : 'QOS(Polled)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
    {
        'name'  : 'session_uptime',
        'title' : 'Session Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
	{
		'name'  : 'cambium_uptime_uptime',
        'title' : 'Device Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
    {
        'name'  : '',
        'title' : 'Auto Negotiation',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : '',
        'title' : 'Duplex',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : '',
        'title' : 'Speed',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
	{
		'name'  : 'cambium_link_ethernet_status_link_state',
        'title' : 'Link Ethernet Status',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_dl_rssi_dl_rssi',
        'title' : 'RSSI DL',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_dl_jitter_dl_jitter',
        'title' : 'Jitter DL',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_ul_rssi_ul_rssi',
        'title' : 'RSSI UL',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_ul_jitter_ul_jitter',
        'title' : 'Jitter UL',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_rereg_count_rereg_count',
        'title' : 'Rereg Count',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_reg_count_reg_count',
        'title' : 'Reg Count',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_transmit_power_invent_transmit_power',
        'title' : 'SM Transmit Power',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_ss_mac_invent_ss_mac',
        'title' : 'SS MAC',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_ss_sector_id_invent_ss_sector_id',
        'title' : 'Sector ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_ss_connected_bs_ip_invent_bs_ip',
        'title' : 'Connected BS IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
    {
        'name'  : '',
        'title' : 'If Out Errors',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : '',
        'title' : 'If In Errors',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
	{
		'name'  : 'cambium_ss_frequency_invent_frequency',
        'title' : 'Frequency',
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
        'name'  : 'cambium_bs_frequency_invent_frequency',
        'title' : 'Polled Frequency',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'cambium_transmit_power_invent_transmit_power',
        'title' : 'Tx Power Polled',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'cambium_commanded_rx_power_invent_commanded_rx_power',
        'title' : 'Rx Power Polled',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
	{
		'name'  : 'cambium_ul_utilization_ul_utilization',
		'title' : 'Sector UL Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
    {
        'name'  : 'cambium_dl_utilization_dl_utilization',
        'title' : 'Sector DL Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
	{
		'name'  : 'cambium_uptime_uptime',
		'title' : 'Sector Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : '',
		'title' : 'Interface eth Error',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_sync_state_invent_sync_state',
		'title' : 'Sync State',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_data_rate_modulation_invent_data_rate_modulation',
		'title' : 'Data Rate',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : '',
		'title' : 'TDD Split',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : '',
		'title' : 'Last GPS Alert Time',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cambium_cell_radius_invent_cell_radius',
		'title' : 'Cell Radius',
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
	},
	{
		'name'  : 'pl',
		'title' : 'Packet Loss',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	}
];

// Wimax SS Tooltip static info object
var wimax_ss_toolTip_static = [];

// Wimax SS Tooltip Polled Info Object
var wimax_ss_toolTip_polled = [
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
    },
	{
		'name'  : 'wimax_ss_ul_utilization_ul_utilization',
        'title' : 'Uplink Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ss_dl_utilization_dl_utilization',
        'title' : 'Downlink Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ss_vlan_invent_ss_vlan',
        'title' : 'VLAN',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_qos_invent_ul_qos',
        'title' : 'QOS(Polled)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ss_session_uptime_session_uptime',
        'title' : 'Session Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ss_uptime_uptime',
        'title' : 'Device Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
    {
        'name'  : 'wimax_ss_autonegotiation_status_autonegotiation',
        'title' : 'Auto Negotiation',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'wimax_ss_duplex_status_duplex',
        'title' : 'Duplex',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'wimax_ss_speed_status_ss_speed',
        'title' : 'Speed',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
	{
		'name'  : 'wimax_ss_link_status_link_state',
        'title' : 'Link Ethernet Status',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_dl_rssi_dl_rssi',
        'title' : 'RSSI DL',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_dl_intrf_dl_intrf',
        'title' : 'INTRF DL',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_dl_cinr_dl_cinr',
        'title' : 'CINR DL',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ul_rssi_ul_rssi',
        'title' : 'RSSI UL',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ul_intrf_ul_intrf',
        'title' : 'INTRF UL',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ul_cinr_ul_cinr',
        'title' : 'CINR UL',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_modulation_ul_fec_modulation_ul_fec',
        'title' : 'Modulation UL FEC',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_modulation_dl_fec_modulation_dl_fec',
        'title' : 'Modulation DL FEC',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ss_ptx_invent_ss_ptx',
        'title' : 'PTX',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ss_mac_ss_mac',
        'title' : 'SS MAC',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ss_sector_id_ss_sector_id',
        'title' : 'Sector ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		// 'name'  : 'wimax_bs_ip_invent_bs_ip',
        'name'  : 'connected_bs_ip',
        'title' : 'Connected BS IP',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ss_errors_status_ifout_errors',
        'title' : 'If Out Error',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ss_errors_status_ifin_errors',
        'title' : 'If In Error',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_ss_frequency_frequency',
        'title' : 'Frequency',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_dl_modulation_change_invent_dl_modulation_change',
        'title' : 'Downlink Modulation Change',
        'show'  : 1,
        'value' : '',
        'url'   : ''
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
        'name'  : 'wimax_pmp1_frequency_invent_frequency',
        'title' : 'Polled Frequency[PMP1]',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'wimax_pmp2_frequency_invent_frequency',
        'title' : 'Polled Frequency [PMP2]',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'wimax_transmit_power_pmp1_invent_transmit_power_pmp1',
        'title' : 'Tx Power Polled [PMP1]',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'wimax_transmit_power_pmp2_invent_transmit_power_pmp2',
        'title' : 'Tx Power Polled [PMP2]',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'wimax_p1_cmd_rx_pwr_invent_p1_cmd_rx_pwr',
        'title' : 'Rx Power Polled [PMP1]',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
        'name'  : 'wimax_p2_cmd_rx_pwr_invent_p2_cmd_rx_pwr',
        'title' : 'Rx Power Polled [PMP2]',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
    {
		'name'  : 'wimax_pmp1_utilization_pmp1_utilization',
		'title' : 'Sector Utilization [PMP1]',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
    {
        'name'  : 'wimax_pmp2_utilization_pmp2_utilization',
        'title' : 'Sector Utilization [PMP2]',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
	{
		'name'  : 'wimax_bs_uptime_uptime',
		'title' : 'Sector Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_pmp_bw_invent_pmp1_bw',
		'title' : 'RF BW Polled [PMP1]',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
    {
        'name'  : 'wimax_pmp_bw_invent_pmp2_bw',
        'title' : 'RF BW Polled [PMP2]',
        'show'  : 1,
        'value' : '',
        'url'   : ''
    },
	{
		'name'  : '',
		'title' : 'Last GPS Alert Time',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_bs_temperature_acb_acb_temp',
		'title' : 'Temperature ACB',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'wimax_bs_temperature_fan_fan_temp',
		'title' : 'Temperature Fan',
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
	},
	{
		'name'  : 'pl',
		'title' : 'Packet Loss',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	}
];

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
			// if info name's are same
			if(correct_info_name == backend_info_name) {
				var url = backend_info["url"] ? backend_info["url"] : "";
				current_info_obj["value"] = backend_info["value"];
				current_info_obj["show"] = backend_info["show"];
				current_info_obj["url"] = url;

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
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "road",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#ffffff"
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#fee379"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#fee379"
                }
            ]
        },
        {
            "featureType": "landscape",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#f3f4f4"
                }
            ]
        },
        {
            "featureType": "water",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#7fc8ed"
                }
            ]
        },
        {},
        {
            "featureType": "road",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "poi.park",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#83cead"
                }
            ]
        },
        {
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "landscape.man_made",
            "elementType": "geometry",
            "stylers": [
                {
                    "weight": 0.9
                },
                {
                    "visibility": "off"
                }
            ]
        }
    ],
    [
        {
            "featureType": "water",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#a2daf2"
                }
            ]
        },
        {
            "featureType": "landscape.man_made",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#f7f1df"
                }
            ]
        },
        {
            "featureType": "landscape.natural",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#d0e3b4"
                }
            ]
        },
        {
            "featureType": "landscape.natural.terrain",
            "elementType": "geometry",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "poi.park",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#bde6ab"
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
            "featureType": "poi.medical",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#fbd3da"
                }
            ]
        },
        {
            "featureType": "poi.business",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#ffe15f"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#efd151"
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#ffffff"
                }
            ]
        },
        {
            "featureType": "road.local",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "black"
                }
            ]
        },
        {
            "featureType": "transit.station.airport",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#cfb2db"
                }
            ]
        }
    ],
    [
        {
            "featureType": "water",
            "stylers": [
                {
                    "color": "#19a0d8"
                }
            ]
        },
        {
            "featureType": "administrative",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "color": "#ffffff"
                },
                {
                    "weight": 6
                }
            ]
        },
        {
            "featureType": "administrative",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "color": "#e85113"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#efe9e4"
                },
                {
                    "lightness": -40
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#efe9e4"
                },
                {
                    "lightness": -20
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "lightness": 100
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "lightness": -100
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "labels.icon"
        },
        {
            "featureType": "landscape",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "landscape",
            "stylers": [
                {
                    "lightness": 20
                },
                {
                    "color": "#efe9e4"
                }
            ]
        },
        {
            "featureType": "landscape.man_made",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "lightness": 100
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "lightness": -100
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "hue": "#11ff00"
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "lightness": 100
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "labels.icon",
            "stylers": [
                {
                    "hue": "#4cff00"
                },
                {
                    "saturation": 58
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "geometry",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#f0e4d3"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#efe9e4"
                },
                {
                    "lightness": -25
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#efe9e4"
                },
                {
                    "lightness": -10
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        }
    ],
    [
        {
            "featureType": "administrative",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "poi",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        },
        {
            "featureType": "road",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        },
        {
            "featureType": "water",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        },
        {
            "featureType": "transit",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        },
        {
            "featureType": "landscape",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "road.local",
            "stylers": [
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry",
            "stylers": [
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "water",
            "stylers": [
                {
                    "color": "#5f94ff"
                },
                {
                    "lightness": 26
                },
                {
                    "gamma": 5.86
                }
            ]
        },
        {},
        {
            "featureType": "road.highway",
            "stylers": [
                {
                    "weight": 0.6
                },
                {
                    "saturation": -85
                },
                {
                    "lightness": 61
                }
            ]
        },
        {
            "featureType": "road"
        },
        {},
        {
            "featureType": "landscape",
            "stylers": [
                {
                    "hue": "#0066ff"
                },
                {
                    "saturation": 74
                },
                {
                    "lightness": 100
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
            "stylers": [
                {
                    "saturation": 43
                },
                {
                    "lightness": -11
                },
                {
                    "hue": "#0088ff"
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "hue": "#ff0000"
                },
                {
                    "saturation": -100
                },
                {
                    "lightness": 99
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#808080"
                },
                {
                    "lightness": 54
                }
            ]
        },
        {
            "featureType": "landscape.man_made",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#ece2d9"
                }
            ]
        },
        {
            "featureType": "poi.park",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#ccdca1"
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "color": "#767676"
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "color": "#ffffff"
                }
            ]
        },
        {
            "featureType": "poi",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "landscape.natural",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#b8cb93"
                }
            ]
        },
        {
            "featureType": "poi.park",
            "stylers": [
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "poi.sports_complex",
            "stylers": [
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "poi.medical",
            "stylers": [
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "poi.business",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        }
    ],
    [
        {
            "featureType": "water",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#b5cbe4"
                }
            ]
        },
        {
            "featureType": "landscape",
            "stylers": [
                {
                    "color": "#efefef"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#83a5b0"
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#bdcdd3"
                }
            ]
        },
        {
            "featureType": "road.local",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#ffffff"
                }
            ]
        },
        {
            "featureType": "poi.park",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#e3eed3"
                }
            ]
        },
        {
            "featureType": "administrative",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "lightness": 33
                }
            ]
        },
        {
            "featureType": "road"
        },
        {
            "featureType": "poi.park",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "lightness": 20
                }
            ]
        },
        {},
        {
            "featureType": "road",
            "stylers": [
                {
                    "lightness": 20
                }
            ]
        }
    ],
    [
        {
            "elementType": "geometry",
            "stylers": [
                {
                    "hue": "#ff4400"
                },
                {
                    "saturation": -68
                },
                {
                    "lightness": -4
                },
                {
                    "gamma": 0.72
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "labels.icon"
        },
        {
            "featureType": "landscape.man_made",
            "elementType": "geometry",
            "stylers": [
                {
                    "hue": "#0077ff"
                },
                {
                    "gamma": 3.1
                }
            ]
        },
        {
            "featureType": "water",
            "stylers": [
                {
                    "hue": "#00ccff"
                },
                {
                    "gamma": 0.44
                },
                {
                    "saturation": -33
                }
            ]
        },
        {
            "featureType": "poi.park",
            "stylers": [
                {
                    "hue": "#44ff00"
                },
                {
                    "saturation": -23
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "hue": "#007fff"
                },
                {
                    "gamma": 0.77
                },
                {
                    "saturation": 65
                },
                {
                    "lightness": 99
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "gamma": 0.11
                },
                {
                    "weight": 5.6
                },
                {
                    "saturation": 99
                },
                {
                    "hue": "#0091ff"
                },
                {
                    "lightness": -86
                }
            ]
        },
        {
            "featureType": "transit.line",
            "elementType": "geometry",
            "stylers": [
                {
                    "lightness": -48
                },
                {
                    "hue": "#ff5e00"
                },
                {
                    "gamma": 1.2
                },
                {
                    "saturation": -23
                }
            ]
        },
        {
            "featureType": "transit",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "saturation": -64
                },
                {
                    "hue": "#ff9100"
                },
                {
                    "lightness": 16
                },
                {
                    "gamma": 0.47
                },
                {
                    "weight": 2.7
                }
            ]
        }
    ]
];