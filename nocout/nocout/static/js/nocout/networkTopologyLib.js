/**
* This function convert the API response from JSON to VIS.js lib format .
* @method convertToVis
* @param response {Object}, It contains the API response in JSON format
*/
function convertToVis(response, required_dom_id){
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
        size : 30,
        // borderWidth : 22, 
        // borderWidthSelected : 24,
        // color : {border : '#80CCFF', background : '#ffffff', highlight: {background : '#ffffff'}}
    },
    edges: {
        width : 3,
        selectionWidth : 5,
        arrows : {
            middle : true,
        }
    },

    interaction : {
        dragNodes:false,
        dragView: true,
    }

};

// creating two seperate datasets for Nodes and Edges
var nodes = new vis.DataSet();
var edges = new vis.DataSet();

var response_data = response.data[0]
var sectors = response.data[0].sectors

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
    title: '<span style="color:'+bh_color_info_object.color+'"><i class="fa '+bh_color_info_object.icon+'""></i>' +severity + ' - ' + response_data.pl_info.value + '</span>'
});

if(current_device_ip == response_data.bh_ip){
    highlight_id = 'BACKHAUL'
}

// adding nodes and edges in the network
nodes.add({
    id: 'BASE STATION',
    label: response_data.bs_alias,
    image: response_data.bs_icon,
    size : 80,
    shape: 'image',
    borderWidth : 0,
    borderWidthSelected : 0
})
edges.add({from: 'BACKHAUL', to: 'BASE STATION', color: 'black'})

for(i=0; i<sectors.length; i++){
    var severity = sectors[i].pl_info.severity ? sectors[i].pl_info.severity.toUpperCase() : 'NA';
    var sect_color_info_object = nocout_getSeverityColorIcon(severity);
    nodes.add({id: 'SECTOR'+"_"+(i+1), label: sectors[i].sect_ip_id_title,
        title: '<span style="color:'+sect_color_info_object.color+'"><i class="fa '+sect_color_info_object.icon+'""></i>' +
        severity + ' - ' + sectors[i].pl_info.value + '</span>', image: sectors[i].icon})

    if(current_device_ip == response_data.sectors[i].ip_address){
    highlight_id = 'SECTOR'+"_"+(i+1)
}
    edges.add({from: 'BASE STATION', to: 'SECTOR'+"_"+(i+1), color: 'black'})


    for(j=0; j<sectors[i].sub_station.length; j++){
        var severity = sectors[i].sub_station[j].pl_info.severity ? sectors[i].pl_info.severity.toUpperCase() : 'NA';
        var ss_color_info_object = nocout_getSeverityColorIcon(severity);
        nodes.add({id: 'SUB STATION'+"_"+(i+1)+"_"+(j+1), label: sectors[i].sub_station[j].ip_address,
            title: '<span style="color:'+ss_color_info_object.color+'"><i class="fa '+ss_color_info_object.icon+'""></i>' +
            severity + ' - ' + sectors[i].sub_station[j].pl_info.value + '</span>' , image: sectors[i].sub_station[j].icon})

        if(current_device_ip == response_data.sectors[i].sub_station[j].ip_address){
        highlight_id = 'SUB STATION'+"_"+(i+1)+"_"+(j+1)
}
        edges.add({from: 'SECTOR'+"_"+(i+1), to: 'SUB STATION'+"_"+(i+1)+"_"+(j+1), color: sectors[i].sub_station[j].link_color})
    }
}



// provide the data in the vis format
var data = {
    nodes: nodes,
    edges: edges
};

// Highlighting selected device
nodes.update({id: highlight_id, color : {border : '#333', highlight : {border : '#333'}}, shadow : {size : 2}, shapeProperties : {useBorderWithImage : true}, borderWidth : 5, borderWidthSelected : 7});

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
   else if(event.nodes[0] == 'BASE STATION'){
        var type = "BS";
        var passing_id = single_bs_id;
        window_title = 'Base Station';
        device_id = ''
        no_polled_tab = true;
   }
   else if(event.nodes[0].indexOf("SECTOR") != -1){
        var res = event.nodes[0].split("_");
        var sect_index = parseInt(res[1]) - 1;
        var type = "SECT";
        var passing_id = sectors[sect_index].id;
        device_tech = sectors[sect_index].device_tech;
        device_type = sectors[sect_index].device_type;
        device_id = sectors[sect_index].device_id;
        window_title = 'Sector';
   }
   else if(event.nodes[0].indexOf("SUB STATION") != -1){
        var res = event.nodes[0].split("_");
        var sect_index = parseInt(res[1]) - 1;
        var ss_index = parseInt(res[2]) - 1;
        var type = "SS";
        var passing_id = sectors[sect_index].sub_station[ss_index].id;
        device_id = sectors[sect_index].sub_station[ss_index].device_id;
        device_tech = sectors[sect_index].sub_station[ss_index].device_tech;
        device_type = sectors[sect_index].sub_station[ss_index].device_type;
        window_title = 'Sub Station';
   }

    // Ajax request for tooltip info
   $.ajax({                
        url: base_url +  "/performance/get_topology/tool_tip/",
        type: 'GET',
        data: {
            'type' : type,
            'id' : passing_id,
        },
        success: function(response) {
        
            if(window_title.toLowerCase().indexOf('base station') > -1) {
                
                var actual_data = rearrangeTooltipArray(bs_toolTip_static,response)
                
            } else if(window_title.toLowerCase().indexOf('sub station') > -1) {
                var actual_data = rearrangeTooltipArray(ss_toolTip_static,response)

            } else if(window_title.toLowerCase().indexOf('backhaul') > -1) {
                var actual_data = rearrangeTooltipArray(bh_toolTip_static,response)

            } else if(window_title.toLowerCase().indexOf('sector') > -1) {
                
                if(device_tech.toLowerCase() == 'p2p') {
                    actual_data = rearrangeTooltipArray(ptp_sector_toolTip_static,response);
                } else if(device_tech.toLowerCase() == 'wimax') {
                    actual_data = rearrangeTooltipArray(wimax_sector_toolTip_static,response);
                } else if(device_tech.toLowerCase() == 'pmp') {
                    actual_data = rearrangeTooltipArray(pmp_sector_toolTip_static,response);
                } else {
                    actual_data = response;
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

            infoTable += '<div class="tab-pane fade active in" id="static_block"><div class="divide-10"></div>';
            infoTable += "<table class='table table-bordered table-hover'><tbody>";
            infoTable += createTableDataHtml(actual_data);
            infoTable += "</tbody></table>";
            infoTable += '</div>';
            infoTable += '<div class="tab-pane fade" id="polled_block"><div class="divide-10"></div>';
            infoTable += "<table class='table table-bordered table-hover'><tbody>";
            infoTable += createTableDataHtml(mrotech_bh_toolTip_polled);
            infoTable += "</tbody></table>";
            infoTable += '</div>';

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
    device_tech = evt.currentTarget.attributes.device_tech ? evt.currentTarget.attributes.device_tech.value : "",
    device_type = evt.currentTarget.attributes.device_type ? evt.currentTarget.attributes.device_type.value : "",
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

        // if(periodic_tooltip_call) {
        //     periodic_tooltip_call.abort();
        // }

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
    // if(periodic_tooltip_call) {
    //     periodic_tooltip_call.abort();
    // }
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