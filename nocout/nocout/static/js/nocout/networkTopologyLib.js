/**
* This function convert the API response from JSON to VIS.js lib format .
* @method convertToVis
* @param response {Object}, It contains the API response in JSON format
*/
function convertToVis(response, required_dom_id) {
	// checking size of BS_ID_LIST
	bs_list_len = typeof bs_id != 'undefined' ? (JSON.parse(bs_id)).length : 0;
	updatedSize = 75;
	backhaul_exist = true
	pe_exist = false
	aggr_switch_exist = false
	pop_convertor_exist = false
	bs_convertor_exist = false
	severity_check = ['down']


	var pe_edge_color = '#468847',
		aggr_sw_edge_color = '#468847',
		pop_edge_color = '#468847',
		bs_conv_edge_color = '#468847',
		bs_sw_edge_color = '#468847',
		bs_edge_color = '#468847',
		sec_edge_color = '#468847'

	var sector_up_image_url = '/static/green.png',
		sector_down_image_url = '/static/red.png'
		sector_image_url = sector_up_image_url

	// In case of Multiple BaseStation updating size to avoid overlapping of images.
	if (bs_list_len > 1) {
		updatedSize  = 25
	}




	// Options for vis network object
	var options = {
	    height: '480px',

	    layout: {
	        hierarchical: {
	          enabled:true,
	          levelSeparation: 400,
	          direction: 'LR',   // UD, DU, LR, RL
	          sortMethod: 'directed' // hubsize, directed
	      }
	    },

	    nodes : {
	        shape : 'image',
	        size : 30
	    },
	    edges: {
	        width : 2,
	        selectionWidth : 3,
	        arrows : {
	            middle : true,
	        },
	  //       smooth: {
			// 	type: 'cubicBezier',
			// 	forceDirection: 'horizontal',
			// 	roundness : 0.5
			// },
	    },

	    interaction : {
	        dragNodes:false,
	        dragView: true,
	        tooltipDelay : 0,
	        navigationButtons : true
	    }

	};

	// creating two seperate datasets for Nodes and Edges
	var nodes = new vis.DataSet();
	var edges = new vis.DataSet();

	var response_data = response.data[0];

	base_station_list = response_data.base_station;

	// create a network
	var container = document.getElementById(required_dom_id);

	// severity and color info for bs_switch
	var bs_switch_severity = response_data.bs_switch_pl_info.severity ? response_data.bs_switch_pl_info.severity.toUpperCase() : 'NA';
	var bs_switch_color_info_object = nocout_getSeverityColorIcon(bs_switch_severity),
		bs_switch_polled_val = response_data.bs_switch_pl_info.value;

	// severity and color info for bh_pop_convertor
	var bh_pop_severity = response_data.bh_pop_pl_info.severity ? response_data.bh_pop_pl_info.severity.toUpperCase() : 'NA';
	var bh_pop_color_info_object = nocout_getSeverityColorIcon(bh_pop_severity),
		bh_pop_polled_val = response_data.bh_pop_pl_info.value;

	// severity and color info for bs_convertor
	var bs_convertor_severity = response_data.bs_convertor_pl_info.severity ? response_data.bs_convertor_pl_info.severity.toUpperCase() : 'NA';
	var bs_convertor_color_info_object = nocout_getSeverityColorIcon(bs_convertor_severity),
		bs_convertor_polled_val = response_data.bs_convertor_pl_info.value;

	// severity and color info for bh_aggr_switch
	var bh_aggr_switch_severity = response_data.bh_aggr_pl_info.severity ? response_data.bh_aggr_pl_info.severity.toUpperCase() : 'NA';
	var bh_aggr_switch_color_info_object = nocout_getSeverityColorIcon(bh_aggr_switch_severity),
		bh_aggr_switch_polled_val = response_data.bh_aggr_pl_info.value;	
	
	// Changing the color of connecting edges //
	/* This is a requirement from client side that if any median device goes down
	   then all the devices connected next to it will be connected with a red line otherwise green line
	   device connection anatomy is :-> 
	   PE -> Aggr_Switch -> Pop_Convertor -> Bs_Convertor -> Bs_Switch -> BS -> Sectors -> Sub-stations */

	if (severity_check.indexOf(bh_aggr_switch_severity.toLowerCase()) > -1){
		aggr_sw_edge_color = pop_edge_color = bs_conv_edge_color = bs_sw_edge_color =
		bs_edge_color = sec_edge_color = '#b94a48';
	}
	else if (severity_check.indexOf(bh_pop_severity.toLowerCase()) > -1){
		pop_edge_color = bs_conv_edge_color = bs_sw_edge_color =
		bs_edge_color = sec_edge_color = '#b94a48';
	}
	else if (severity_check.indexOf(bs_convertor_severity.toLowerCase()) > -1){
		bs_conv_edge_color = bs_sw_edge_color =
		bs_edge_color = sec_edge_color = '#b94a48';
	}
	else if (severity_check.indexOf(bs_switch_severity.toLowerCase()) > -1){
		bs_sw_edge_color = bs_edge_color = sec_edge_color = '#b94a48';
	}
	
	if (typeof polled_val == 'undefined' || polled_val == '') {
		polled_val = 'NA';
	}

	// Adding PE Host only if it exists 
	if (response_data.pe_ip != 'NA'){
		nodes.add({
		    id: 'PE',
		    label: response_data.pe_ip + 'PE',
		    image: response_data.bh_icon,
		    shape: 'image',
		    // title: '<span style="color:'+bh_color_info_object.color+'"><i class="fa '+bh_color_info_object.icon+'""></i> ' +severity + ' - ' + polled_val + '</span>'
		});
		pe_exist = true
	}

	// Adding Aggregation Switch only if it exists
	if (response_data.aggregation_switch_ip != 'NA'){
		nodes.add({
		    id: 'aggr_switch',
		    label: response_data.aggregation_switch_ip + 'aggr_switch',
		    image: response_data.bh_icon,
		    shape: 'image',
		    title: '<span style="color:'+bh_aggr_switch_color_info_object.color+'"><i class="fa '+bh_aggr_switch_color_info_object.icon+'""></i> ' + bh_aggr_switch_severity + ' - ' + bh_aggr_switch_polled_val + '</span>'
		});
		aggr_switch_exist = true
	}

	// Adding Pop Convertor only if it exists
	if (response_data.pop_convertor_ip != 'NA'){
		nodes.add({
		    id: 'pop_convertor',
		    label: response_data.pop_convertor_ip + 'pop_convertor',
		    image: response_data.bh_icon,
		    shape: 'image',
		    title: '<span style="color:'+bh_pop_color_info_object.color+'"><i class="fa '+bh_pop_color_info_object.icon+'""></i> ' + bh_pop_severity + ' - ' + bh_pop_polled_val + '</span>'
		});
		pop_convertor_exist = true
	}

	// Adding BS Convertor only if it exists
	if (response_data.bs_convertor_ip != 'NA'){
		nodes.add({
		    id: 'bs_convertor',
		    label: response_data.bs_convertor_ip + 'bs_convertor',
		    image: response_data.bh_icon,
		    shape: 'image',
		    title: '<span style="color:'+bs_convertor_color_info_object.color+'"><i class="fa '+bs_convertor_color_info_object.icon+'""></i> ' + bs_convertor_severity + ' - ' + bs_convertor_polled_val + '</span>'
		});
		bs_convertor_exist = true
	}
	// Here BACKHAUL refers to BS Switch
	if (response_data.bh_ip != 'NA'){
		nodes.add({
		    id: 'BACKHAUL',
		    label: response_data.bh_ip + 'bs_switch',
		    image: response_data.bh_icon,
		    shape: 'image',
		    title: '<span style="color:'+bs_switch_color_info_object.color+'"><i class="fa '+bs_switch_color_info_object.icon+'""></i> ' + bs_switch_severity + ' - ' + bs_switch_polled_val + '</span>'
		});
		backhaul_exist = true
	}
	if(current_device_ip == response_data.bh_ip){
	    highlight_id = 'BACKHAUL'
	}

	if(backhaul_exist){ //if backhaul exists
		if(bs_convertor_exist){ //if backhaul and bs_convertor exists
			edges.add({from: 'bs_convertor', to: 'BACKHAUL', color: bs_conv_edge_color})
			if(pop_convertor_exist){ //if backhaul and bs_convertor and pop_convertor exists
				edges.add({from: 'pop_convertor', to: 'bs_convertor', color: pop_edge_color})
				if(aggr_switch_exist){ //if backhaul, bs_convertor, pop_convertor and aggr_switch exists
					edges.add({from: 'aggr_switch', to: 'pop_convertor', color: aggr_sw_edge_color})
					if(pe_exist){ //if backhaul, bs_convertor, pop_convertor, aggr_switch and PE exists
						edges.add({from: 'PE', to: 'aggr_switch', color: pe_edge_color})
					}
				}
				else{  //if backhaul, bs_convertor, pop_convertor exists but aggr_switch doesn't exist
					if(pe_exist){
						edges.add({from: 'PE', to: 'pop_convertor', color: pe_edge_color})
					}
				}
			}
			else{ //if backhaul, bs_convertor exists but pop_convertor doesn't exist
				if(aggr_switch_exist){ //if backhaul, bs_convertor exists , pop_convertor doesn't exist but aggr_switch exists 
					edges.add({from: 'aggr_switch', to: 'bs_convertor', color: aggr_sw_edge_color})
					if(pe_exist){
						edges.add({from: 'PE', to: 'aggr_switch', color: pe_edge_color})
					}
				}
				else{
					if(pe_exist){
						edges.add({from: 'PE', to: 'bs_convertor', color: pe_edge_color})
					}
				}

			}
		} else { //if backhaul exists but bs_convertor doesn't
			if(pop_convertor_exist){ //if bs_convertor doesn't exists butbackhaul and pop_convertor exists
				edges.add({from: 'pop_convertor', to: 'BACKHAUL', color: pop_edge_color})
				if(aggr_switch_exist){ //if bs_convertor doesn't exists butbackhaul, pop_convertor, aggr_switch exists
					edges.add({from: 'aggr_switch', to: 'pop_convertor', color: aggr_sw_edge_color})
					if(pe_exist){ //if bs_convertor doesn't exists butbackhaul, pop_convertor, aggr_switch, PE exists
						edges.add({from: 'PE', to: 'aggr_switch', color: pe_edge_color})
					}
				}
				else{  //if backhaul, pop_convertor exists but bs_convertor, aggr_switch doesn't exist
					if(pe_exist){
						edges.add({from: 'PE', to: 'pop_convertor', color: pe_edge_color})
					}
				}
			} else { //if backhaul exists but pop_convertor, bs_convertor doesn't exist
				if(aggr_switch_exist){ //if backhaul, bs_convertor exists , pop_convertor doesn't exist but aggr_switch exists 
					edges.add({from: 'aggr_switch', to: 'BACKHAUL', color: aggr_sw_edge_color})
					if(pe_exist){
						edges.add({from: 'PE', to: 'aggr_switch', color: pe_edge_color})
					}
				}
				else{
					if(pe_exist){
						edges.add({from: 'PE', to: 'BACKHAUL', color: pe_edge_color})
					}
				}
			}
		}
	} else { //if backhaul doesn't exist
		if(bs_convertor_exist){ //if backhaul doesn't exist and bs_convertor exists
			if(pop_convertor_exist){ //if backhaul doesn't exist and bs_convertor and pop_convertor exists
				edges.add({from: 'pop_convertor', to: 'bs_convertor', color: pop_edge_color})
				if(aggr_switch_exist){ //if backhaul doesn't exist and bs_convertor, pop_convertor and aggr_switch exists
					edges.add({from: 'aggr_switch', to: 'pop_convertor', color: aggr_sw_edge_color})
					if(pe_exist){ //if backhaul doesn't exist and bs_convertor, pop_convertor, aggr_switch and PE exists
						edges.add({from: 'PE', to: 'aggr_switch', color: pe_edge_color})
					}
				}
				else{  //if bs_convertor, pop_convertor exists but backhaul, aggr_switch doesn't exist
					if(pe_exist){
						edges.add({from: 'PE', to: 'pop_convertor', color: pe_edge_color})
					}
				}
			}
			else{ //if bs_convertor exists but pop_convertor, backhaul doesn't exist
				if(aggr_switch_exist){ //if  bs_convertor exists, aggr_switch exists but backhaul, pop_convertor doesn't exist 
					edges.add({from: 'aggr_switch', to: 'bs_convertor', color: aggr_sw_edge_color})
					if(pe_exist){
						edges.add({from: 'PE', to: 'aggr_switch', color: pe_edge_color})
					}
				}
				else{
					if(pe_exist){
						edges.add({from: 'PE', to: 'bs_convertor', color: pe_edge_color})
					}
				}

			}
		}
		else{ //backhaul, bs_convertor doesn't exist
			if(pop_convertor_exist){ //if backhaul, bs_convertor doesn't exists but pop_convertor exists
				if(aggr_switch_exist){ //if backhaul, bs_convertor doesn't exists but pop_convertor, aggr_switch exists
					edges.add({from: 'aggr_switch', to: 'pop_convertor', color: aggr_sw_edge_color})
					if(pe_exist){ //if backhaul, bs_convertor doesn't exists but pop_convertor, aggr_switch, PE exists
						edges.add({from: 'PE', to: 'aggr_switch', color: pe_edge_color})
					}
				}
				else{  //if pop_convertor exists but bs_convertor, backhaul, aggr_switch doesn't exist
					if(pe_exist){
						edges.add({from: 'PE', to: 'pop_convertor', color: pe_edge_color})
					}
				}
			}
			else{ //if backhaul, pop_convertor, bs_convertor doesn't exist
				if(aggr_switch_exist){ //if bs_convertor exists , backhaul, pop_convertor doesn't exist but aggr_switch exists 
					if(pe_exist){
						edges.add({from: 'PE', to: 'aggr_switch', color: pe_edge_color})
					}
				}
				else{
					if(pe_exist){
						edges.add({from: 'PE', to: 'BASESTATION_'+i, color: pe_edge_color})
					}
				}

			}
		}
	}

	for (var i=0;i<base_station_list.length;i++) {

		// adding nodes and edges in the network
		nodes.add({
		    id: 'BASESTATION_'+i,
		    label: base_station_list[i].bs_alias,
		    image: base_station_list[i].bs_icon,
		    size : updatedSize,
		    title: base_station_list[i].bs_alias,
		    shape: 'image',
		    borderWidth : 0,
		    borderWidthSelected : 0
		});

		if(backhaul_exist){ //if backhaul exists
			edges.add({from: 'BACKHAUL', to: 'BASESTATION_'+i, color: bs_sw_edge_color});
		} else { //if backhaul doesn't exist
			if(bs_convertor_exist){ //if backhaul doesn't exist and bs_convertor exists
				edges.add({from: 'bs_convertor', to: 'BASESTATION_'+i, color: bs_conv_edge_color});
			} else { //backhaul, bs_convertor doesn't exist
				if(pop_convertor_exist){ //if backhaul, bs_convertor doesn't exists but pop_convertor exists
					edges.add({from: 'pop_convertor', to: 'BASESTATION_'+i, color: pop_edge_color});
				} else { //if backhaul, pop_convertor, bs_convertor doesn't exist
					if(aggr_switch_exist){ //if bs_convertor exists , backhaul, pop_convertor doesn't exist but aggr_switch exists 
						edges.add({from: 'aggr_switch', to: 'BASESTATION_'+i, color: aggr_sw_edge_color});
					} else {
						if(pe_exist){
							edges.add({from: 'PE', to: 'BASESTATION_'+i, color: pe_edge_color})
						}
					}

				}
			}
		}

		var sectors = base_station_list[i].sectors;
		
		for(j=0; j<sectors.length; j++){
		    var sector_severity = sectors[j].pl_info.severity ? sectors[j].pl_info.severity.toUpperCase() : 'NA',
		    sect_color_info_object = nocout_getSeverityColorIcon(sector_severity),
		    sector_polled_val = sectors[j].pl_info.value

		    // if sector's severity is down then change edge color to red.
		    if (severity_check.indexOf(sector_severity.toLowerCase()) > -1) {
		    	sec_edge_color = '#b94a48';
		    	sector_image_url = sector_down_image_url
		    }


			if (typeof sector_polled_val == 'undefined' || sector_polled_val == '') {
				sector_polled_val = 'NA';
			}

		    nodes.add({
		    	id: 'SECTOR'+"_"+(i+1)+'_'+(j+1),
		    	label: sectors[j].sect_ip_id_title,
		        title: '<span style="color:'+sect_color_info_object.color+'"><i class="fa '+sect_color_info_object.icon+'""></i> ' + sector_severity + ' - ' + sector_polled_val + '</span>',
		        shape: 'image',
		        image: sector_image_url
		    })

		    if(current_device_ip == sectors[j].ip_address){
			    highlight_id = 'SECTOR'+"_"+(i+1)+'_'+(j+1)
			}
		    edges.add({
		    	from: 'BASESTATION_'+i,
		    	to: 'SECTOR'+"_"+(i+1)+'_'+(j+1),
		    	color: bs_edge_color,
		    	smooth: {
					type: 'cubicBezier',
					forceDirection: 'horizontal',
					roundness : 0.5
				}
		    })


		    for(k=0; k<sectors[j].sub_station.length; k++) {
		        var ss_severity = sectors[j].sub_station[k].pl_info.severity ? sectors[j].sub_station[k].pl_info.severity.toUpperCase() : 'NA',
		        ss_color_info_object = nocout_getSeverityColorIcon(ss_severity),
		        ss_polled_val = sectors[j].sub_station[k].pl_info.value

		        if (typeof ss_polled_val == 'undefined' || ss_polled_val == '') {
					ss_polled_val = 'NA';
				}

		        nodes.add({id: 'SUBSTATION'+'_'+(i+1)+"_"+(j+1)+"_"+(k+1), label: sectors[j].sub_station[k].ip_address,
				            title: '<span style="color:'+ss_color_info_object.color+'"><i class="fa '+ss_color_info_object.icon+'""></i> ' +
				            ss_severity + ' - ' + ss_polled_val + '</span>' , image: sectors[j].sub_station[k].icon})

		        if(current_device_ip == sectors[j].sub_station[k].ip_address){
		        	highlight_id = 'SUBSTATION'+'_'+(i+1)+"_"+(j+1)+"_"+(k+1)
				}

		        edges.add({from: 'SECTOR'+"_"+(i+1)+'_'+(j+1), to: 'SUBSTATION'+'_'+(i+1)+"_"+(j+1)+"_"+(k+1), color: sec_edge_color})
		    }
		}
	}




	// provide the data in the vis format
	var data = {
	    nodes: nodes,
	    edges: edges
	};

	// Highlighting selected device
	// nodes.update({
	// 	id: highlight_id,
	// 	color : {
	// 		border : '#444',
	// 		background : '#ffffff',
	// 		highlight : {
	// 			border : '#444'
	// 		}
	// 	},
	// 	shadow : {
	// 		size : 2
	// 	},
	// 	shapeProperties : {
	// 		useBorderWithImage : true
	// 	},
	// 	borderWidth: 2,
	// 	borderWidthSelected: 2
	// });

	// initialize your network
	network = new vis.Network(container, data, options);

	// adding a event listner on Nodes
	network.on('selectNode', function (event, properties, senderId) {
	   try {
	        single_bs_id = JSON.parse(bs_id)[0];
	    } catch(e) {
	    // console.error(e);
	   }
	   var window_title = '';
	   var no_polled_tab = false;

	   if(event.nodes[0] == 'BACKHAUL'){
	        var type = "BH";
	        var passing_id = response_data.bh_id;
	        device_id = response_data.bh_device_id;
	        device_tech = response_data.bh_device_tech;
	        device_type = response_data.bh_device_type;
	        window_title = 'Backhaul';
	   }
	   else if(event.nodes[0].indexOf('BASESTATION') > -1){
	        var type = "BS";
	        var res = event.nodes[0].split("_");
	        var bs_index = parseInt(res[1]);
	        var passing_id = base_station_list[bs_index]['bs_id'];
	        window_title = 'Base Station';
	        device_id = ''
	        no_polled_tab = true;
	   }
	   else if(event.nodes[0].indexOf("SECTOR") > -1){
	        var res = event.nodes[0].split("_");
	        var bs_index = parseInt(res[1]) - 1;
	        var sect_index = parseInt(res[2]) - 1;
	        var type = "SECT";
	        var passing_id = base_station_list[bs_index].sectors[sect_index].id;
	        device_tech = base_station_list[bs_index].sectors[sect_index].device_tech;
	        device_type = base_station_list[bs_index].sectors[sect_index].device_type;
	        device_id = base_station_list[bs_index].sectors[sect_index].device_id;
	        window_title = 'Sector';
	   }
	   else if(event.nodes[0].indexOf("SUBSTATION") > -1){
	        var res = event.nodes[0].split("_");
	        var bs_index = parseInt(res[1]) - 1;
	        var sect_index = parseInt(res[2]) - 1;
	        var ss_index = parseInt(res[3]) - 1;
	        var type = "SS";
	        var passing_id = base_station_list[bs_index].sectors[sect_index].sub_station[ss_index].id;
	        device_id = base_station_list[bs_index].sectors[sect_index].sub_station[ss_index].device_id;
	        device_tech = base_station_list[bs_index].sectors[sect_index].sub_station[ss_index].device_tech;
	        device_type = base_station_list[bs_index].sectors[sect_index].sub_station[ss_index].device_type;
	        window_title = 'Sub Station';
	   }

	    // Ajax request for tooltip info
	   $.ajax({                
	        url: base_url +  "/performance/get_topology/tool_tip/?type=" + type + '&id='+passing_id,
	        type: 'GET',
	        success: function(response) {
	        	var result = response;

	        	if (typeof(response) == 'string') {
	        		result = JSON.parse(response);
	        	}

	        	if (result.success) {
	        		if(window_title.toLowerCase().indexOf('base station') > -1) {
		                
		                var actual_data = rearrangeTooltipArray(bs_toolTip_static,result.data);
		                
		            } else if(window_title.toLowerCase().indexOf('sub station') > -1) {
		                var actual_data = rearrangeTooltipArray(ss_toolTip_static,result.data)
		                if(device_tech.toLowerCase() == 'p2p') {
		                    toolTip_polled_tab = ptp_ss_toolTip_polled;
		                } else if(device_tech.toLowerCase() == 'wimax') {
		                    toolTip_polled_tab = wimax_ss_toolTip_polled;
		                } else if(device_tech.toLowerCase() == 'pmp') {
		                    if(device_type.toLowerCase() == 'radwin5kss' ) {
								toolTip_polled_tab = pmp_radwin5k_ss_toolTip_polled;
							} else {
								toolTip_polled_tab = pmp_ss_toolTip_polled;
							}
		                }
		            } else if(window_title.toLowerCase().indexOf('backhaul') > -1) {
		                var actual_data = rearrangeTooltipArray(bh_toolTip_static,result.data)
	                	if(device_type.toLowerCase() == 'pine') {
							toolTip_polled_tab = mrotech_bh_toolTip_polled;
						} else if(device_type.toLowerCase() == 'switch') {
							toolTip_polled_tab = switch_bh_toolTip_polled;
						} else if(device_type.toLowerCase() == 'rici') {
							toolTip_polled_tab = rici_bh_toolTip_polled;
						}

		            } else if(window_title.toLowerCase().indexOf('sector') > -1) {
		                
		                if(device_tech.toLowerCase() == 'p2p') {
		                    actual_data = rearrangeTooltipArray(ptp_sector_toolTip_static,result.data);
		                    toolTip_polled_tab = ptp_sector_toolTip_polled;
		                } else if(device_tech.toLowerCase() == 'wimax') {
		                    actual_data = rearrangeTooltipArray(wimax_sector_toolTip_static,result.data);
		                    toolTip_polled_tab = wimax_sector_toolTip_polled;
		                } else if(device_tech.toLowerCase() == 'pmp') {
		                    actual_data = rearrangeTooltipArray(pmp_sector_toolTip_static,result.data);
		                    toolTip_polled_tab = pmp_sector_toolTip_polled;
		                } else {
		                    actual_data = result.data;
		                }

		            }


		            infoTable = '';

		            infoTable += '<div class="tabbable">';
		            /*Tabs Creation Start*/
		            if(no_polled_tab){
		                infoTable += '<ul class="nav nav-tabs">\
		                            <li class="active"><a href="#static_block" data-toggle="tab">\
		                            <i class="fa fa-arrow-circle-o-right"></i> Static Info</a></li>\
		                            <i class="fa fa-spinner fa fa-spin hide"> </i></a>\
		                            </li>';
		            }
		            else {
		                infoTable += '<ul class="nav nav-tabs">\
		                            <li class="active"><a href="#static_block" data-toggle="tab">\
		                            <i class="fa fa-arrow-circle-o-right"></i> Static Info</a></li>\
		                            <li class=""><a href="#polled_block" data-toggle="tab" id="polled_tab"\
		                            device_id="'+device_id+'" point_type="'+type+'" \
		                            device_tech="'+device_tech+'" \
		                            device_type="'+device_type+'">\
		                            <i class="fa fa-arrow-circle-o-right"></i> Polled Info \
		                            <i class="fa fa-spinner fa fa-spin hide"> </i></a>\
		                            </li>';
		            }
		            infoTable += '</ul>';

		            infoTable += '<div class="tab-content"><div class="tab-pane fade active in" id="static_block"><div class="divide-10"></div>';
		            infoTable += "<table class='table table-bordered table-hover'><tbody>";
		            infoTable += createTableDataHtml(actual_data);
		            infoTable += "</tbody></table>";
		            infoTable += '</div>';
		            infoTable += '<div class="tab-pane fade" id="polled_block"><div class="divide-10"></div>';
		            infoTable += "<table class='table table-bordered table-hover'><tbody>";
		            infoTable += createTableDataHtml(toolTip_polled_tab);
		            infoTable += "</tbody></table>";
		            infoTable += '</div></div>';

		            /*Final infowindow content string*/
		            windowContent = "<div class='windowContainer' style='z-index: 300; position:relative;'>\
		                              <div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  \
		                              "+window_title+"</h4><div class='tools'><a class='close_info_window' title='Close'>\
		                              <i class='fa fa-times text-danger'></i></a></div></div>\
		                              <div class='box-body'><div align='center'>"+infoTable+"</div>\
		                              <div class='clearfix'></div><div class='pull-right'></div><div class='clearfix'>\
		                              </div></div></div></div>";

		            $("#infoWindowContainer").html(windowContent);
		            $("#infoWindowContainer").removeClass('hide');
	        	} else {

	        	}

	        },
	        error : function(err) {
	        // console.log('TopoToolTip Error Working');
	        },
	        complete: function() {
	        // console.log('TopoToolTip compulsary Working');

	        }

	    });
	});    
}


/**
* This event triggers when close button on infowindow clicked
* @event Click(Using Delegate)
*/
$('#infoWindowContainer').delegate('.close_info_window','click',function(e) {
	$('#infoWindowContainer').html("");
	network.unselectAll();
	if(!$('#infoWindowContainer').hasClass("hide")) {
	    $('#infoWindowContainer').addClass("hide");
	}
});

    /**
* This event triggers when Tabs on infowindow clicked(or selected) 
* @event Click(Using Delegate)
*/
$("#infoWindowContainer").delegate(".nav-tabs li a",'click',function(evt) {

	var current_device_id = evt.currentTarget.attributes.device_id ? evt.currentTarget.attributes.device_id.value : "",
	    point_type = evt.currentTarget.attributes.point_type ? evt.currentTarget.attributes.point_type.value : "",
	    dom_id = evt.currentTarget.attributes.id ? evt.currentTarget.attributes.id.value : "",
	    device_tech = evt.currentTarget.attributes.device_tech ? $.trim(evt.currentTarget.attributes.device_tech.value.toLowerCase()) : "",
	    device_type = evt.currentTarget.attributes.device_type ? $.trim(evt.currentTarget.attributes.device_type.value.toLowerCase()) : "",
	    href_attr = evt.currentTarget.attributes.href ? evt.currentTarget.attributes.href.value.split("#") : "",
	    block_id = href_attr.length > 1 ? href_attr[1] : "",
	    pl_attr = evt.currentTarget.attributes.pl_value,
	    device_pl = pl_attr && pl_attr.value != 'N/A' ? pl_attr.value : "";

	if(dom_id && point_type && current_device_id) {
	    // Show Spinner
	    if(dom_id == 'polled_tab') {
	        if($("a#"+dom_id+" .fa-spinner").hasClass("hide")) {
	            $("a#"+dom_id+" .fa-spinner").removeClass("hide");
	        }

	        // Make AJAX Call
	        periodic_tooltip_call = $.ajax({
	            url: base_url+'/network_maps/perf_info/?device_id='+current_device_id+"&device_pl="+device_pl,
	            type : "GET",
	            success : function(response) {

	                var result = "",
	                    polled_data_html = "";
	                // Type check for response
	                if(typeof response == 'string') {
	                    result = JSON.parse(response);
	                } else {
	                    result = response;
	                }

	                if(result && result.length > 0) {

	                    var fetched_polled_info = result,
	                        tooltip_info_dict = [];

	                    if(point_type == 'SECT') {
	                        
	                        if(ptp_tech_list.indexOf(device_tech) > -1) {
	                            tooltip_info_dict = rearrangeTooltipArray(ptp_sector_toolTip_polled,fetched_polled_info);
	                        } else if(device_tech == 'wimax') {
	                            tooltip_info_dict = rearrangeTooltipArray(wimax_sector_toolTip_polled,fetched_polled_info);
	                        } else if(device_tech == 'pmp') {
	                            if(device_type == 'radwin5kbs') {
	                                tooltip_info_dict = rearrangeTooltipArray(pmp_radwin5k_sector_toolTip_polled, fetched_polled_info);
	                            } else {
	                                tooltip_info_dict = rearrangeTooltipArray(pmp_sector_toolTip_polled, fetched_polled_info);
	                            }
	                        } else {
	                            // pass
	                        }
	                    } else if(point_type == 'SS') {
	                        if(ptp_tech_list.indexOf(device_tech) > -1) {
	                            tooltip_info_dict = rearrangeTooltipArray(ptp_ss_toolTip_polled,fetched_polled_info);
	                        } else if(device_tech == 'wimax') {
	                            tooltip_info_dict = rearrangeTooltipArray(wimax_ss_toolTip_polled,fetched_polled_info);
	                        } else if(device_tech == 'pmp') {                                
	                            if(device_type == 'radwin5kss') {
	                                tooltip_info_dict = rearrangeTooltipArray(pmp_radwin5k_ss_toolTip_polled, fetched_polled_info);
	                            } else {
	                                tooltip_info_dict = rearrangeTooltipArray(pmp_ss_toolTip_polled, fetched_polled_info);
	                            }                                
	                        } else {
	                            // pass
	                        }
	                    } else if(point_type == 'BH') {
	                        if(device_type == 'pine') {
	                            tooltip_info_dict = rearrangeTooltipArray(mrotech_bh_toolTip_polled,fetched_polled_info);
	                        } else if(device_type == 'switch') {
	                            tooltip_info_dict = rearrangeTooltipArray(switch_bh_toolTip_polled,fetched_polled_info);
	                        } else if(device_type == 'rici') {
	                            tooltip_info_dict = rearrangeTooltipArray(rici_bh_toolTip_polled,fetched_polled_info);
	                        }
	                    } else {
	                        // pass
	                    }

	                    polled_data_html = "";
	                    
	                    polled_data_html += "<table class='table table-bordered table-hover'><tbody>";

	                    /*Poll Parameter Info*/
	                    for(var i=0; i< tooltip_info_dict.length; i++) {
	                        var url = "",
	                            text_class = "";
	                        if(tooltip_info_dict[i]["show"]) {
	                            // GET text color as per the severity of device
	                            var severity = tooltip_info_dict[i]["severity"],
	                                severity_obj = nocout_getSeverityColorIcon(severity),
	                                text_color = severity_obj.color ? severity_obj.color : "",
	                                cursor_css = text_color ? "cursor:pointer;" : "";

	                            // Url
	                            url = tooltip_info_dict[i]["url"] ? tooltip_info_dict[i]["url"] : "";
	                            text_class = "text-primary";

	                            polled_data_html += "<tr style='color:"+text_color+";'><td url='"+url+"' style='"+cursor_css+"'>"+tooltip_info_dict[i]['title']+"</td>\
	                                                 <td>"+tooltip_info_dict[i]['value']+"</td></tr>";
	                        }
	                    }

	                    polled_data_html += "</tbody></table>";

	                    // Clear the polled block HTML
	                    $("#"+block_id).html('<div class="divide-10"></div>');

	                    // Append the polled data info
	                    $("#"+block_id).append(polled_data_html);

	                } else {
	                    $.gritter.add({
	                        title: "Polled Info",
	                        text: "Please try again later.",
	                        sticky: false,
	                        time : 1000
	                    });
	                }
	            },
	            error : function(err) {

	                if(err.statusText != 'abort') {
	                    $.gritter.add({
	                        title: "Polled Info",
	                        text: err.statusText,
	                        sticky: false,
	                        time : 1000
	                    });
	                }
	            },
	            complete : function() {
	                if(!$("a#"+dom_id+" .fa-spinner").hasClass("hide")) {
	                    $("a#"+dom_id+" .fa-spinner").addClass("hide");
	                }       
	            }
	        });

	    }
	} else {
	    if(!$(".nav-tabs li a:last-child .fa-spinner").hasClass("hide")) {
	        $(".nav-tabs li a:last-child .fa-spinner").addClass("hide");
	    }
	}
});

function createTableDataHtml(data_obj) {

    var table_html = "";

    if(data_obj && data_obj.length) {
        for(var i=0; i< data_obj.length; i++) {
            var url = '',
                text_class = '',
                text_color = '',
                highlight_class = '';

            if(data_obj[i]["show"]) {                            
                var val = data_obj[i]["value"];

                // current value
                actual_val = val;

                // This is useful only for polled data
                url = data_obj[i]["url"] ? $.trim(data_obj[i]["url"]) : '';

                table_html += "<tr style='color:"+text_color+";'><td class='"+highlight_class+"' url='"+url+"'>\
                              "+data_obj[i]['title']+"</td><td>"+actual_val+"</td></tr>";
            }
        }
    }

    return table_html;
}