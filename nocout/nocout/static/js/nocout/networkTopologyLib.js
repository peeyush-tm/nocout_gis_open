/**
* This function convert the API response from JSON to VIS.js lib format .
* @method convertToVis
* @param response {Object}, It contains the API response in JSON format
*/
function convertToVis(response, required_dom_id) {
	// checking size of BS_ID_LIST
	bs_list_len = typeof bs_id != 'undefined' ? (JSON.parse(bs_id)).length : 0;
	updatedSize = 80

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
	          levelSeparation: 1300,
	          direction: 'LR',   // UD, DU, LR, RL
	          sortMethod: 'directed' // hubsize, directed
	      }
	    },

	    nodes : {
	        shape : 'image',
	        size : 30
	    },
	    edges: {
	        width : 3,
	        selectionWidth : 5,
	        arrows : {
	            middle : true,
	        },
	        smooth: {
				type: 'cubicBezier',
				forceDirection: 'vertical',
				roundness : 0.3
				},
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

	var severity = response_data.pl_info.severity ? response_data.pl_info.severity.toUpperCase() : 'NA';
	var bh_color_info_object = nocout_getSeverityColorIcon(severity);

	nodes.add({
	    id: 'BACKHAUL',
	    label: response_data.bh_ip,
	    image: response_data.bh_icon,
	    shape: 'image',
	    borderWidth : 0,
	    borderWidthSelected : 0,
	    title: '<span style="color:'+bh_color_info_object.color+'"><i class="fa '+bh_color_info_object.icon+'""></i> ' +severity + ' - ' + response_data.pl_info.value + '</span>'
	});

	if(current_device_ip == response_data.bh_ip){
	    highlight_id = 'BACKHAUL'
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

		edges.add({from: 'BACKHAUL', to: 'BASESTATION_'+i, color: 'black'})

		var sectors = base_station_list[i].sectors;
		
		for(j=0; j<sectors.length; j++){
		    var severity = sectors[j].pl_info.severity ? sectors[j].pl_info.severity.toUpperCase() : 'NA';
		    var sect_color_info_object = nocout_getSeverityColorIcon(severity);
		    nodes.add({id: 'SECTOR'+"_"+(i+1)+'_'+(j+1), label: sectors[j].sect_ip_id_title,
				        title: '<span style="color:'+sect_color_info_object.color+'"><i class="fa '+sect_color_info_object.icon+'""></i> ' +
				        severity + ' - ' + sectors[j].pl_info.value + '</span>', image: sectors[j].icon})

		    if(current_device_ip == sectors[j].ip_address){
			    highlight_id = 'SECTOR'+"_"+(i+1)+'_'+(j+1)
			}
		    edges.add({from: 'BASESTATION_'+i, to: 'SECTOR'+"_"+(i+1)+'_'+(j+1), color: 'black'})


		    for(k=0; k<sectors[j].sub_station.length; k++) {
		        var severity = sectors[j].sub_station[k].pl_info.severity ? sectors[j].pl_info.severity.toUpperCase() : 'NA';
		        var ss_color_info_object = nocout_getSeverityColorIcon(severity);
		        nodes.add({id: 'SUBSTATION'+'_'+(i+1)+"_"+(j+1)+"_"+(k+1), label: sectors[j].sub_station[k].ip_address,
				            title: '<span style="color:'+ss_color_info_object.color+'"><i class="fa '+ss_color_info_object.icon+'""></i> ' +
				            severity + ' - ' + sectors[j].sub_station[k].pl_info.value + '</span>' , image: sectors[j].sub_station[k].icon})

		        if(current_device_ip == sectors[j].sub_station[k].ip_address){
		        	highlight_id = 'SUBSTATION'+'_'+(i+1)+"_"+(j+1)+"_"+(k+1)
				}

		        edges.add({from: 'SECTOR'+"_"+(i+1)+'_'+(j+1), to: 'SUBSTATION'+'_'+(i+1)+"_"+(j+1)+"_"+(k+1), color: sectors[j].sub_station[k].link_color})
		    }
		}
	}




	// provide the data in the vis format
	var data = {
	    nodes: nodes,
	    edges: edges
	};

	// Highlighting selected device
	nodes.update({
		id: highlight_id,
		color : {
			border : '#444',
			background : '#ffffff',
			highlight : {
				border : '#444'
			}
		},
		shadow : {
			size : 2
		},
		shapeProperties : {
			useBorderWithImage : true
		},
		borderWidth: 2,
		borderWidthSelected: 2
	});

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
		                
		                var actual_data = rearrangeTooltipArray(bs_toolTip_static,result.data)
		                
		            } else if(window_title.toLowerCase().indexOf('sub station') > -1) {
		                var actual_data = rearrangeTooltipArray(ss_toolTip_static,result.data)

		            } else if(window_title.toLowerCase().indexOf('backhaul') > -1) {
		                var actual_data = rearrangeTooltipArray(bh_toolTip_static,result.data)

		            } else if(window_title.toLowerCase().indexOf('sector') > -1) {
		                
		                if(device_tech.toLowerCase() == 'p2p') {
		                    actual_data = rearrangeTooltipArray(ptp_sector_toolTip_static,result.data);
		                } else if(device_tech.toLowerCase() == 'wimax') {
		                    actual_data = rearrangeTooltipArray(wimax_sector_toolTip_static,result.data);
		                } else if(device_tech.toLowerCase() == 'pmp') {
		                    actual_data = rearrangeTooltipArray(pmp_sector_toolTip_static,result.data);
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
		            infoTable += createTableDataHtml(mrotech_bh_toolTip_polled);
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
	                    } else if(point_type == 'BS') {
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