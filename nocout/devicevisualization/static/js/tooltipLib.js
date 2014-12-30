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
        'show'  : 1,
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
		'name'  : 'latitude',
        'title' : 'Latitude',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'longitude',
        'title' : 'Longitude',
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
		'name'  : 'bh_utilization',
        'title' : 'BH Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'bh_off_on_net',
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
		'name'  : 'bh_bso_circuit_id',
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
		'name'  : 'converter_type',
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
		'name'  : 'bh_configured_on_port',
        'title' : 'SW/CON Port',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	}
];

// BH Tooltip polled info object
var bh_toolTip_polled = [];

// PTP SS Tooltip static info object
var ptp_ss_toolTip_static = [
	{
		'name'  : 'customer_alias',
        'title' : 'Customer Name',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cktid',
        'title' : 'CKT ID',
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
		'name': 'latitude',
        'title': 'Latitude',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'longitude',
		'title': 'Longitude',
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
		'name': 'antenna_type',
		'title': 'Antenna Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'mount_type',
		'title': 'Antena Mount Type',
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
		'name': 'cable_length',
		'title': 'Cable Length',
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
		'name': 'customer_address',
		'title': 'Customer Address',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'throughput_during_acceptance',
		'title': 'Throughput During Acceptance',
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
		'name': 'bh_bso',
		'title': 'BH BSO',
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
	}
];

// PTP SS Tooltip polled info object
var ptp_ss_toolTip_polled = [
	{
		'name'  : 'producttype',
        'title' : 'Product Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'frequency',
        'title' : 'Frequency',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'uas',
        'title' : 'UAS',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'rssi',
        'title' : 'RSSI',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'service_throughput',
        'title' : 'Estimated Throughput',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'utilization',
        'title' : 'Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'uptime',
        'title' : 'Uptime',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'link_distance',
        'title' : 'Link Distance',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'cbw',
        'title' : 'CBW',
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
	},
	{
		'name'  : 'ul_utilization',
        'title' : 'UL Utilization',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'dl_utilization',
        'title' : 'DL Utilization',
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
		'name'  : 'duplex',
        'title' : 'Duplex',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'ss_speed',
        'title' : 'Speed',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : '',
        'title' : 'Link',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : '',
        'title' : 'HSSU',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	}
];

/*************************** PTP SECTOR TOOLTIP IS EQUIVALENT TO PTP SS TOOLTIP ***************************/
// PTP Sector Tooltip static info object
var ptp_sector_toolTip_static = [
	{
		'name'  : '',
        'title' : '',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	}
];


// PMP SS Tooltip static info object
var pmp_ss_toolTip_static = [
	{
		'name': 'alias',
		'title': 'SS Name',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'cktid',
		'title': 'CKT ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'qos_bandwidth',
		'title': 'QOS(BW)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'latitude',
		'title': 'Latitude',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'longitude',
		'title': 'Longitude',
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
		'name': 'antenna_type',
		'title': 'Antenna Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'mount_type',
		'title': 'SS MountType',
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
		'name': 'cable_length',
		'title': 'Cable Length',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'dl_rssi_during_acceptance',
		'title': 'DL RSSI During Acceptance',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'jitter_value_during_acceptance',
		'title': 'Jitter Value During Acceptance',
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
		'name': 'date_of_acceptance',
		'title': 'Date of Acceptance',
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
	}
];

// PMP Sector Tooltip static info object
var pmp_sector_toolTip_static = [
	{
		'name'  : 'site_name',
        'title' : 'Site Name',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'city',
        'title' : 'City',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'site_type',
        'title' : 'Site Type',
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
		'name'  : 'antenna_height',
        'title' : 'Antenna Height',
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
		'name'  : 'antenna_tilt',
		'title' : 'Antenna Tilt',
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
	}
];

// Wimax SS Tooltip static info object
var wimax_ss_toolTip_static = [
	{
		'name': 'alias',
		'title': 'SS Name',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'cktid',
		'title': 'CKT ID',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'qos_bandwidth',
		'title': 'QOS(BW)',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'latitude',
		'title': 'Latitude',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'longitude',
		'title': 'Longitude',
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
		'name': 'antenna_type',
		'title': 'Antenna Type',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'mount_type',
		'title': 'SS MountType',
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
		'name': 'cable_length',
		'title': 'Cable Length',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'dl_rssi_during_acceptance',
		'title': 'DL RSSI During Acceptance',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name': 'dl_cinr_during_acceptance',
		'title': 'DL CINR During Acceptance',
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
		'name': 'date_of_acceptance',
		'title': 'Date of Acceptance',
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
	}
];

// Wimax Sector Tooltip static info object
var wimax_sector_toolTip_static = [
	{
		'name'  : 'site_name',
        'title' : 'Site Name',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'city',
        'title' : 'City',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'site_type',
        'title' : 'Site Type',
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
		'name'  : 'antenna_height',
        'title' : 'Antenna Height',
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
		'name'  : 'antenna_tilt',
		'title' : 'Antenna Tilt',
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
		'name'  : 'antenna_make',
        'title' : 'Antenna Make',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'antenna_splitter_installed',
        'title' : 'Installation Of Splitter',
        'show'  : 1,
        'value' : '',
        'url'   : ''
	},
	{
		'name'  : 'dr_site',
        'title' : 'DR Site',
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
	var updated_info_list = [];
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
				current_info_obj["value"] = backend_info["value"];
				current_info_obj["show"] = backend_info["show"];

				break backend_info_loop;
			}
		}
		// Push info object to array
		updated_info_list.push(current_info_obj);
	}

	return updated_info_list;
}