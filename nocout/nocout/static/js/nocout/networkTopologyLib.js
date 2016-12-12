/**
* This function convert the API response from JSON to VIS.js lib format .
* @method convertToVis
* @param response {Object}, It contains the API response in JSON format
*/
function convertToVis(response, required_dom_id) {
	
    // checking size of BS_ID_LIST
    bs_list_len = typeof bs_id != 'undefined' ? (JSON.parse(bs_id)).length : 0;
    updatedSize = 50;
    backhaul_exist = false
    pe_exist = false
    aggr_switch_exist = false
    pop_convertor_exist = false
    bs_convertor_exist = false
    far_end_bs_sw_exist = false
    pl_device_list = []
    device_nodeId_mapping = {}
    ip_port_dict = {}
    unique_sec_list = []
    severity_check = ['down']
    is_ptp_bh = response['have_ptp_bh']
    limit_till_bs = response['limit_till_bs']
    show_ports = false
    // this is for updating that from which bs which device is connected backside
    bs_back_edges_dict = {}

    down_devices_list = []
    is_device_down = {
        'pe' : false,
        'aggr_sw' : false,
        'pop' : false,
        'bs_conv' : false,
        'bs_sw' : false,
        'bs' : false,
        'ne' : false,
        'fe' : false,
        'fe_bs_sw' : false,
        'fe_bs' : false,
        'idu' : false,
        'sec' : false
    }

    // creating two seperate datasets for Nodes and Edges
    nodes = new vis.DataSet();
    edges = new vis.DataSet();

    pe_edge_color = '#468847', //edge originating from PE
    aggr_sw_edge_color = '#468847', //edge originating from Aggregation Switch
    pop_edge_color = '#468847', //edge originating from POP Convertor
    bs_conv_edge_color = '#468847', //edge originating from Near End BS Convertor
    bs_sw_edge_color = '#468847', //edge originating from Near End BS Switch
    bs_edge_color = '#468847', //edge originating from Near End Base Station
    ne_edge_color = '#468847', //edge originating from Near End
    fe_edge_color = '#468847', //edge originating from Far End
    fe_bs_sw_edge_color = '#468847', //edge originating from Near End BS Switch
    fe_bs_edge_color = '#468847', //edge originating from Far End Base Station
    idu_edge_color = '#468847', //edge originating from IDU Device
    sec_edge_color = '#468847',
    ss_edge_color = '#468847'

    var sector_up_image_url = '/static/img/icons/green.png',
        sector_down_image_url = '/static/img/icons/red.png'
        sector_image_url = sector_up_image_url,
        converter_image = '/static/img/icons/converter.png',
        switch_image = '/static/img/icons/switch.png',
        router_image = '/static/img/icons/router.png',
        idu_image = '/static/img/icons/idu.png',
        far_end_image = '/static/img/icons/far_end.png',
        near_end_image = '/static/img/icons/near_end.png',
        ss_image = '/static/img/icons/ss.png'

    // In case of Multiple BaseStation updating size to avoid overlapping of images.
    if (bs_list_len > 1) {
        updatedSize  = 25
    }




    // Options for vis network object
    var options = {
        height: '100%',

        layout: {
            hierarchical: {
              enabled:true,
              levelSeparation: 400,
              nodeSpacing: 200,
              direction: 'LR',   // UD, DU, LR, RL
              sortMethod: 'directed' // hubsize, directed
          }
        },

        nodes : {
            // shape : 'image',
            size : 40,
            shapeProperties : {
                useBorderWithImage : true,
            },
            borderWidth : 4,
            borderWidthSelected : 6,
            color: {
                border: '#309408',
                background: '#ffffff',
                highlight: {
                    border: '#309408',
                    background: '#ffffff',
                }
            },
        },
        edges: {
            width : 2,
            selectionWidth : 3,
            arrows : {
                middle : true,
            },
      //       smooth: {
            //  type: 'cubicBezier',
            //  forceDirection: 'horizontal',
            //  roundness : 0.5
            // },
        },

        interaction : {
            dragNodes:false,
            dragView: true,
            tooltipDelay : 0,
            navigationButtons : true
        }

    };


    var response_data = response.data[0];

    base_station_list = response_data.base_station;
    far_end_base_station_list = response_data.far_end_base_station

    // create a network
    var container = document.getElementById(required_dom_id);

    // severity and color info for PE device
    var pe_severity = response_data.pe_pl_info.severity ? response_data.pe_pl_info.severity.toUpperCase() : 'NA',
        pe_pl = response_data.pe_pl_info.packet_loss ? response_data.pe_pl_info.packet_loss : 'NA',
        pe_latency = response_data.pe_pl_info.latency ? response_data.pe_pl_info.latency : 'NA';
    var pe_color_info_object = nocout_getSeverityColorIcon(pe_severity),
        pe_polled_val = response_data.pe_pl_info.value;

    // severity and color info for bs_switch
    var bs_switch_severity = response_data.bs_switch_pl_info.severity ? response_data.bs_switch_pl_info.severity.toUpperCase() : 'NA',
        bs_switch_pl = response_data.bs_switch_pl_info.packet_loss ? response_data.bs_switch_pl_info.packet_loss : 'NA',
        bs_switch_latency = response_data.bs_switch_pl_info.latency ? response_data.bs_switch_pl_info.latency : 'NA';
    var bs_switch_color_info_object = nocout_getSeverityColorIcon(bs_switch_severity),
        bs_switch_polled_val = response_data.bs_switch_pl_info.value;

    // severity and color info for bh_pop_convertor
    var bh_pop_severity = response_data.bh_pop_pl_info.severity ? response_data.bh_pop_pl_info.severity.toUpperCase() : 'NA',
        bh_pop_pl = response_data.bh_pop_pl_info.packet_loss ? response_data.bh_pop_pl_info.packet_loss : 'NA',
        bh_pop_latency = response_data.bh_pop_pl_info.latency ? response_data.bh_pop_pl_info.latency : 'NA';
    var bh_pop_color_info_object = nocout_getSeverityColorIcon(bh_pop_severity),
        bh_pop_polled_val = response_data.bh_pop_pl_info.value;

    // severity and color info for bs_convertor
    var bs_convertor_severity = response_data.bs_convertor_pl_info.severity ? response_data.bs_convertor_pl_info.severity.toUpperCase() : 'NA',
        bs_convertor_pl = response_data.bs_convertor_pl_info.packet_loss ? response_data.bs_convertor_pl_info.packet_loss : 'NA',
        bs_convertor_latency = response_data.bs_convertor_pl_info.latency ? response_data.bs_convertor_pl_info.latency : 'NA';
    var bs_convertor_color_info_object = nocout_getSeverityColorIcon(bs_convertor_severity),
        bs_convertor_polled_val = response_data.bs_convertor_pl_info.value;

    // severity and color info for bh_aggr_switch
    var bh_aggr_switch_severity = response_data.bh_aggr_pl_info.severity ? response_data.bh_aggr_pl_info.severity.toUpperCase() : 'NA',
        bh_aggr_pl = response_data.bh_aggr_pl_info.packet_loss ? response_data.bh_aggr_pl_info.packet_loss : 'NA',
        bh_aggr_latency = response_data.bh_aggr_pl_info.latency ? response_data.bh_aggr_pl_info.latency : 'NA';
    var bh_aggr_switch_color_info_object = nocout_getSeverityColorIcon(bh_aggr_switch_severity),
        bh_aggr_switch_polled_val = response_data.bh_aggr_pl_info.value;    
    
    if(is_ptp_bh){
        // severity and color info for far_end_bs_switch
        var far_end_bs_switch_severity = response_data.far_end_bs_switch_pl_info.severity ? response_data.far_end_bs_switch_pl_info.severity.toUpperCase() : 'NA',
            far_end_bs_switch_pl = response_data.far_end_bs_switch_pl_info.packet_loss ? response_data.far_end_bs_switch_pl_info.packet_loss : 'NA',
            far_end_bs_switch_latency = response_data.far_end_bs_switch_pl_info.latency ? response_data.far_end_bs_switch_pl_info.latency : 'NA';
        var far_end_bs_switch_color_info_object = nocout_getSeverityColorIcon(far_end_bs_switch_severity),
            far_end_bs_switch_polled_val = response_data.far_end_bs_switch_pl_info.value;

        // severity and color info for far_end_device
        var far_end_severity = response_data.far_end_pl_info.severity ? response_data.far_end_pl_info.severity.toUpperCase() : 'NA',
            far_end_pl = response_data.far_end_pl_info.packet_loss ? response_data.far_end_pl_info.packet_loss : 'NA',
            far_end_latency = response_data.far_end_pl_info.latency ? response_data.far_end_pl_info.latency : 'NA';
        var far_end_color_info_object = nocout_getSeverityColorIcon(far_end_severity),
            far_end_polled_val = response_data.far_end_pl_info.value;

        // severity and color info for near_end_device
        var near_end_severity = response_data.near_end_pl_info.severity ? response_data.near_end_pl_info.severity.toUpperCase() : 'NA',
            near_end_pl = response_data.near_end_pl_info.packet_loss ? response_data.near_end_pl_info.packet_loss : 'NA',
            near_end_latency = response_data.near_end_pl_info.latency ? response_data.near_end_pl_info.latency : 'NA';
        var near_end_color_info_object = nocout_getSeverityColorIcon(near_end_severity),
            near_end_polled_val = response_data.near_end_pl_info.value; 
    }
    


    // Changing the color of connecting edges //
    /* This is a requirement from client side that if any median device goes down
       then all the devices connected next to it will be connected with a red line otherwise green line
       device connection anatomy is :-> 
       PE -> Aggr_Switch -> Pop_Convertor -> Bs_Convertor -> Bs_Switch -> BS -> Sectors -> Sub-stations */

    if (severity_check.indexOf(pe_severity.toLowerCase()) > -1){
        pe_edge_color = '#b94a48';
        is_device_down['pe'] = true
    }
    if (severity_check.indexOf(bh_aggr_switch_severity.toLowerCase()) > -1){
        aggr_sw_edge_color = '#b94a48';
        is_device_down['aggr_sw'] = true

        // sector_image_url = sector_down_image_url;
    }
    if (severity_check.indexOf(bh_pop_severity.toLowerCase()) > -1){
        pop_edge_color = '#b94a48';
        is_device_down['pop'] = true
        // sector_image_url = sector_down_image_url;
    }
    if (severity_check.indexOf(bs_convertor_severity.toLowerCase()) > -1){
        bs_conv_edge_color = '#b94a48';
        is_device_down['bs_conv'] = true

        // sector_image_url = sector_down_image_url;
    }
    if (severity_check.indexOf(bs_switch_severity.toLowerCase()) > -1){
        bs_sw_edge_color = '#b94a48';
        is_device_down['bs_sw'] = true
    }
    
    if (is_ptp_bh){
        if (severity_check.indexOf(near_end_severity.toLowerCase()) > -1){
            ne_edge_color = '#b94a48';
            is_device_down['ne'] = true

            // sector_image_url = sector_down_image_url;
        }
        if (severity_check.indexOf(far_end_severity.toLowerCase()) > -1){
            fe_edge_color = '#b94a48';
            is_device_down['fe'] = true

            // sector_image_url = sector_down_image_url;
        }
        if (severity_check.indexOf(far_end_bs_switch_severity.toLowerCase()) > -1){
            fe_bs_sw_edge_color = '#b94a48';
            is_device_down['fe_bs_sw'] = true

            // sector_image_url = sector_down_image_url;
        }
    }
    
    if (typeof polled_val == 'undefined' || polled_val == '') {
        polled_val = 'NA';
    }

    // Adding PE Host only if it exists 
    if (response_data.pe_ip != 'NA'){
        nodes.add({
            id: 'PE',
            // label:  'PE Router\n\n' +
            //      'PE IP : ' + response_data.pe_ip + '\n' +
            //      'PE Hostname : ' + response_data.pe_hostname,
            label: createNodeLabel(response_data.pe_ip, '', pe_pl, pe_latency, 'PE Router'),
            image: router_image,
            shape: 'image',
            title: '<span style="color:'+pe_color_info_object.color+'"><i class="fa '+pe_color_info_object.icon+'""></i> ' + pe_severity + ' - ' + pe_polled_val + '</span>'
        });
        pe_exist = true
        pl_device_list.push(response_data.pe_name)
        device_nodeId_mapping[response_data.pe_name] = 'PE'
        ip_port_dict['PE'] = {
            'ip_address' : response_data.pe_ip,
            'port' : '',
            'node_name' : 'PE Router'
        }
    }

    // Adding Aggregation Switch only if it exists
    if (response_data.aggregation_switch_ip != 'NA'){
        var node_id = 'aggr_' + response_data.bh_aggregator_device_name;

        nodes.add({
            id: node_id,
            label: createNodeLabel(response_data.aggregation_switch_ip, response_data.aggregation_switch_port, bh_aggr_pl, bh_aggr_latency, 'Aggregation Switch'),
            image: switch_image,
            shape: 'image',
            title: '<span style="color:'+bh_aggr_switch_color_info_object.color+'"><i class="fa '+bh_aggr_switch_color_info_object.icon+'""></i> ' + bh_aggr_switch_severity + ' - ' + bh_aggr_switch_polled_val + '</span>'
        });
        aggr_switch_exist = true
        pl_device_list.push(response_data.bh_aggregator_device_name)
        device_nodeId_mapping[response_data.bh_aggregator_device_name] = 'aggr_' + response_data.bh_aggregator_device_name
        ip_port_dict['aggr_' + response_data.bh_aggregator_device_name] = {
                                                                            'ip_address' : response_data.aggregation_switch_ip,
                                                                            'port' : response_data.aggregation_switch_port,
                                                                            'node_name' : 'Aggregation Switch'
                                                                        }

        // Pushing node id to down_device_list if device is down else do nothing
        is_device_down['aggr_sw'] ? down_devices_list.push(node_id) : 0
    }

    // Adding Pop Convertor only if it exists
    if (response_data.pop_convertor_ip != 'NA'){
        var node_id = 'pop_' + response_data.bh_pop_device_name
        nodes.add({
            id: node_id,
            label: createNodeLabel(response_data.pop_convertor_ip, response_data.pop_convertor_port, bh_pop_pl, bh_pop_latency, 'POP Convertor'),
            image: converter_image,
            shape: 'image',
            title: '<span style="color:'+bh_pop_color_info_object.color+'"><i class="fa '+bh_pop_color_info_object.icon+'""></i> ' + bh_pop_severity + ' - ' + bh_pop_polled_val + '</span>'
        });
        pop_convertor_exist = true
        pl_device_list.push(response_data.bh_pop_device_name)
        device_nodeId_mapping[response_data.bh_pop_device_name] = 'pop_' + response_data.bh_pop_device_name
        ip_port_dict['pop_' + response_data.bh_pop_device_name] = {
                                                                            'ip_address' : response_data.pop_convertor_ip,
                                                                            'port' : response_data.pop_convertor_port,
                                                                            'node_name' : 'POP Convertor'
                                                                        }
        // Pushing node id to down_device_list if device is down else do nothing
        is_device_down['pop'] ? down_devices_list.push(node_id) : 0
    }

    // Adding BS Convertor only if it exists
    if (response_data.bs_convertor_ip != 'NA'){
        var node_id = 'conv_' + response_data.bs_convertor_device_name;
        nodes.add({
            id: node_id,
            label: createNodeLabel(response_data.bs_convertor_ip, response_data.bs_convertor_port, bs_convertor_pl, bs_convertor_latency, 'BS Convertor'),
            image: converter_image,
            shape: 'image',
            title: '<span style="color:'+bs_convertor_color_info_object.color+'"><i class="fa '+bs_convertor_color_info_object.icon+'""></i> ' + bs_convertor_severity + ' - ' + bs_convertor_polled_val + '</span>'
        });
        bs_convertor_exist = true
        pl_device_list.push(response_data.bs_convertor_device_name)
        device_nodeId_mapping[response_data.bs_convertor_device_name] = 'conv_' + response_data.bs_convertor_device_name
        ip_port_dict['conv_' + response_data.bs_convertor_device_name] = {
                                                                            'ip_address' : response_data.bs_convertor_ip,
                                                                            'port' : response_data.bs_convertor_port,
                                                                            'node_name' : 'BS Convertor'
                                                                        }
        // Pushing node id to down_device_list if device is down else do nothing
        is_device_down['bs_conv'] ? down_devices_list.push(node_id) : 0
    }
    
    // *****************************************
    // *** Here BACKHAUL refers to BS Switch ***
    // *****************************************
    if (response_data.bs_switch_ip != 'NA'){
        var node_id = 'ne_sw_' + response_data.bs_switch_name;
        nodes.add({
            id: node_id,
            label: createNodeLabel(response_data.bs_switch_ip, response_data.bs_switch_port, bs_switch_pl, bs_switch_latency, 'BS Switch'),
            image: switch_image,
            shape: 'image',
            title: '<span style="color:'+bs_switch_color_info_object.color+'"><i class="fa '+bs_switch_color_info_object.icon+'""></i> ' + bs_switch_severity + ' - ' + bs_switch_polled_val + '</span>'
        });
        backhaul_exist = true
        pl_device_list.push(response_data.bs_switch_name)
        device_nodeId_mapping[response_data.bs_switch_name] = 'ne_sw_' + response_data.bs_switch_name
        ip_port_dict['ne_sw_' + response_data.bs_switch_name] = {
                                                                    'ip_address' : response_data.bs_switch_ip,
                                                                    'port' : response_data.bs_switch_port,
                                                                    'node_name' : 'BS Switch'
                                                                }
        // Pushing node id to down_device_list if device is down else do nothing
        is_device_down['bs_sw'] ? down_devices_list.push(node_id) : 0
    }
    if(current_device_ip == response_data.bh_ip){
        highlight_id = response_data.bs_switch_name
    }

    if(backhaul_exist){ //if backhaul exists
        if(bs_convertor_exist){ //if backhaul and bs_convertor exists
            edges.add({from: 'conv_' + response_data.bs_convertor_device_name, to: 'ne_sw_' + response_data.bs_switch_name, color: bs_sw_edge_color})
            if(pop_convertor_exist){ //if backhaul and bs_convertor and pop_convertor exists
                edges.add({from: 'pop_' + response_data.bh_pop_device_name, to: 'conv_' + response_data.bs_convertor_device_name, color: bs_conv_edge_color})
                if(aggr_switch_exist){ //if backhaul, bs_convertor, pop_convertor and aggr_switch exists
                    edges.add({from: 'aggr_' + response_data.bh_aggregator_device_name, to: 'pop_' + response_data.bh_pop_device_name, color: pop_edge_color})
                    if(pe_exist){ //if backhaul, bs_convertor, pop_convertor, aggr_switch and PE exists
                        edges.add({from: 'PE', to: 'aggr_' + response_data.bh_aggregator_device_name, color: aggr_sw_edge_color})
                    }
                }
                else{  //if backhaul, bs_convertor, pop_convertor exists but aggr_switch doesn't exist
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'pop_' + response_data.bh_pop_device_name, color: pop_edge_color})
                    }
                }
            }
            else{ //if backhaul, bs_convertor exists but pop_convertor doesn't exist
                if(aggr_switch_exist){ //if backhaul, bs_convertor exists , pop_convertor doesn't exist but aggr_switch exists 
                    edges.add({from: 'aggr_' + response_data.bh_aggregator_device_name, to: 'conv_' + response_data.bs_convertor_device_name, color: bs_conv_edge_color})
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'aggr_' + response_data.bh_aggregator_device_name, color: aggr_sw_edge_color})
                    }
                }
                else{
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'conv_' + response_data.bs_convertor_device_name, color: bs_conv_edge_color})
                    }
                }

            }
        } else { //if backhaul exists but bs_convertor doesn't
            if(pop_convertor_exist){ //if bs_convertor doesn't exists butbackhaul and pop_convertor exists
                edges.add({from: 'pop_' + response_data.bh_pop_device_name, to: 'ne_sw_' + response_data.bs_switch_name, color: bs_sw_edge_color})
                if(aggr_switch_exist){ //if bs_convertor doesn't exists butbackhaul, pop_convertor, aggr_switch exists
                    edges.add({from: 'aggr_' + response_data.bh_aggregator_device_name, to: 'pop_' + response_data.bh_pop_device_name, color: pop_edge_color})
                    if(pe_exist){ //if bs_convertor doesn't exists butbackhaul, pop_convertor, aggr_switch, PE exists
                        edges.add({from: 'PE', to: 'aggr_' + response_data.bh_aggregator_device_name, color: aggr_sw_edge_color})
                    }
                }
                else{  //if backhaul, pop_convertor exists but bs_convertor, aggr_switch doesn't exist
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'pop_' + response_data.bh_pop_device_name, color: pop_edge_color})
                    }
                }
            } else { //if backhaul exists but pop_convertor, bs_convertor doesn't exist
                if(aggr_switch_exist){ //if backhaul, bs_convertor exists , pop_convertor doesn't exist but aggr_switch exists 
                    edges.add({from: 'aggr_' + response_data.bh_aggregator_device_name, to: 'ne_sw_' + response_data.bs_switch_name, color: bs_sw_edge_color})
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'aggr_' + response_data.bh_aggregator_device_name, color: aggr_sw_edge_color})
                    }
                }
                else{
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'ne_sw_' + response_data.bs_switch_name, color: bs_sw_edge_color})
                    }
                }
            }
        }
    } else { //if backhaul doesn't exist
        if(bs_convertor_exist){ //if backhaul doesn't exist and bs_convertor exists
            if(pop_convertor_exist){ //if backhaul doesn't exist and bs_convertor and pop_convertor exists
                edges.add({from: 'pop_' + response_data.bh_pop_device_name, to: 'conv_' + response_data.bs_convertor_device_name, color: bs_conv_edge_color})
                if(aggr_switch_exist){ //if backhaul doesn't exist and bs_convertor, pop_convertor and aggr_switch exists
                    edges.add({from: 'aggr_' + response_data.bh_aggregator_device_name, to: 'pop_' + response_data.bh_pop_device_name, color: pop_edge_color})
                    if(pe_exist){ //if backhaul doesn't exist and bs_convertor, pop_convertor, aggr_switch and PE exists
                        edges.add({from: 'PE', to: 'aggr_' + response_data.bh_aggregator_device_name, color: aggr_sw_edge_color})
                    }
                }
                else{  //if bs_convertor, pop_convertor exists but backhaul, aggr_switch doesn't exist
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'pop_' + response_data.bh_pop_device_name, color: pop_edge_color})
                    }
                }
            }
            else{ //if bs_convertor exists but pop_convertor, backhaul doesn't exist
                if(aggr_switch_exist){ //if  bs_convertor exists, aggr_switch exists but backhaul, pop_convertor doesn't exist 
                    edges.add({from: 'aggr_' + response_data.bh_aggregator_device_name, to: 'conv_' + response_data.bs_convertor_device_name, color: bs_conv_edge_color})
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'aggr_' + response_data.bh_aggregator_device_name, color: aggr_sw_edge_color})
                    }
                }
                else{
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'conv_' + response_data.bs_convertor_device_name, color: bs_conv_edge_color})
                    }
                }

            }
        }
        else{ //backhaul, bs_convertor doesn't exist
            if(pop_convertor_exist){ //if backhaul, bs_convertor doesn't exists but pop_convertor exists
                if(aggr_switch_exist){ //if backhaul, bs_convertor doesn't exists but pop_convertor, aggr_switch exists
                    edges.add({from: 'aggr_' + response_data.bh_aggregator_device_name, to: 'pop_' + response_data.bh_pop_device_name, color: pop_edge_color})
                    if(pe_exist){ //if backhaul, bs_convertor doesn't exists but pop_convertor, aggr_switch, PE exists
                        edges.add({from: 'PE', to: 'aggr_' + response_data.bh_aggregator_device_name, color: aggr_sw_edge_color})
                    }
                }
                else{  //if pop_convertor exists but bs_convertor, backhaul, aggr_switch doesn't exist
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'pop_' + response_data.bh_pop_device_name, color: pop_edge_color})
                    }
                }
            }
            else{ //if backhaul, pop_convertor, bs_convertor doesn't exist
                if(aggr_switch_exist){ //if bs_convertor exists , backhaul, pop_convertor doesn't exist but aggr_switch exists 
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'aggr_' + response_data.bh_aggregator_device_name, color: aggr_sw_edge_color})
                    }
                }
                else{
                    if(pe_exist){
                        edges.add({from: 'PE', to: 'BASESTATION_'+i, color: pe_edge_color})
                        bs_back_edges_dict['BASESTATION_'+i] = 'PE'
                    }
                }

            }
        }
    }

    if (is_ptp_bh){
        for (var i=0;i<base_station_list.length;i++) {
            // adding nodes and edges in the network
            nodes.add({
                id: 'BASESTATION_'+i,
                label: base_station_list[i].bs_alias,
                image: far_end_base_station_list[i].bs_icon,
                size : updatedSize,
                shapeProperties : {
                    useBorderWithImage : false
                },
                title: base_station_list[i].bs_alias,
                shape: 'image',
                borderWidth : 0,
                borderWidthSelected : 0
            });

            if(backhaul_exist){ //if backhaul exists
                edges.add({from: 'ne_sw_' + response_data.bs_switch_name, to: 'BASESTATION_'+i, color: bs_sw_edge_color});
                bs_back_edges_dict['BASESTATION_'+i] = 'ne_sw_' + response_data.bs_switch_name
            } else { //if backhaul doesn't exist
                if(bs_convertor_exist){ //if backhaul doesn't exist and bs_convertor exists
                    edges.add({from: 'conv_' + response_data.bs_convertor_device_name, to: 'BASESTATION_'+i, color: bs_conv_edge_color});
                    bs_back_edges_dict['BASESTATION_'+i] = 'conv_' + response_data.bs_convertor_device_name
                } else { //backhaul, bs_convertor doesn't exist
                    if(pop_convertor_exist){ //if backhaul, bs_convertor doesn't exists but pop_convertor exists
                        edges.add({from: 'pop_' + response_data.bh_pop_device_name, to: 'BASESTATION_'+i, color: pop_edge_color});
                        bs_back_edges_dict['BASESTATION_'+i] = 'pop_' + response_data.bh_pop_device_name
                    } else { //if backhaul, pop_convertor, bs_convertor doesn't exist
                        if(aggr_switch_exist){ //if bs_convertor exists , backhaul, pop_convertor doesn't exist but aggr_switch exists 
                            edges.add({from: 'aggr_' + response_data.bh_aggregator_device_name, to: 'BASESTATION_'+i, color: aggr_sw_edge_color});
                            bs_back_edges_dict['BASESTATION_'+i] = 'aggr_' + response_data.bh_aggregator_device_name
                        } else {
                            if(pe_exist){
                                edges.add({from: 'PE', to: 'BASESTATION_'+i, color: pe_edge_color})
                                    bs_back_edges_dict['BASESTATION_'+i] = 'PE'
                            }
                        }

                    }
                }
            }

            // Adding near end
            nodes.add({
                id: 'ne_' + response_data.near_end_device_name,
                label: createNodeLabel(response_data.near_end_ip, '', near_end_pl, near_end_latency, 'Near End'),
                image: near_end_image,
                shape: 'image',
                title: '<span style="color:'+near_end_color_info_object.color+'"><i class="fa '+near_end_color_info_object.icon+'""></i> ' + near_end_severity + ' - ' + near_end_polled_val + '</span>'
            });
            pl_device_list.push(response_data.near_end_device_name)
            device_nodeId_mapping[response_data.near_end_device_name] = 'ne_' + response_data.near_end_device_name
            ip_port_dict['ne_' + response_data.near_end_device_name] = {
                                                                        'ip_address' : response_data.near_end_ip,
                                                                        'port' : '',
                                                                        'node_name' : 'Near End'
                                                                    }

            is_device_down['ne'] ? down_devices_list.push('ne_' + response_data.near_end_device_name) : 0

            // Adding far end
            nodes.add({
                id: 'fe_' + response_data.far_end_device_name,
                label: createNodeLabel(response_data.far_end_ip, '', far_end_pl, far_end_latency, 'Far End'),
                image: far_end_image,
                shape: 'image',
                title: '<span style="color:'+far_end_color_info_object.color+'"><i class="fa '+far_end_color_info_object.icon+'""></i> ' + far_end_severity + ' - ' + far_end_polled_val + '</span>'
            });
            pl_device_list.push(response_data.far_end_device_name)
            device_nodeId_mapping[response_data.far_end_device_name] = 'fe_' + response_data.far_end_device_name
            ip_port_dict['fe_' + response_data.far_end_device_name] = {
                                                                        'ip_address' : response_data.far_end_ip,
                                                                        'port' : '',
                                                                        'node_name' : 'Far End'
                                                                    }

            is_device_down['fe'] ? down_devices_list.push('fe_' + response_data.far_end_device_name) : 0

            // Adding far end bs switch
            if (response_data.far_end_bs_switch_ip != 'NA'){
                nodes.add({
                    id: 'fe_sw_' + response_data.far_end_bs_switch_name,
                    label: createNodeLabel(response_data.far_end_bs_switch_ip, response_data.far_end_bs_switch_port, far_end_bs_switch_pl, far_end_bs_switch_latency, 'BS Switch'),
                    image: switch_image,
                    shape: 'image',
                    title: '<span style="color:'+far_end_bs_switch_color_info_object.color+'"><i class="fa '+far_end_bs_switch_color_info_object.icon+'""></i> ' + far_end_bs_switch_severity + ' - ' + far_end_bs_switch_polled_val + '</span>'
                });

                far_end_bs_sw_exist = true
                pl_device_list.push(response_data.far_end_bs_switch_name)
                device_nodeId_mapping[response_data.far_end_bs_switch_name] = 'fe_sw_' + response_data.far_end_bs_switch_name
                ip_port_dict['fe_sw_' + response_data.far_end_bs_switch_name] = {
                                                                            'ip_address' : response_data.far_end_bs_switch_ip,
                                                                            'port' : response_data.far_end_bs_switch_port,
                                                                            'node_name' : 'BS Switch'
                                                                        }

                is_device_down['fe_bs_sw'] ? down_devices_list.push('fe_sw_' + response_data.far_end_bs_switch_name) : 0
            }
            

            nodes.add({
                id: 'far_end_base_station',
                label: far_end_base_station_list[i].far_end_bs_alias,
                image: far_end_base_station_list[i].bs_icon,
                size : updatedSize, //115
                title: far_end_base_station_list[i].far_end_bs_alias,
                shape: 'image',
                shapeProperties : {
                    useBorderWithImage : false
                },
                borderWidth : 0,
                borderWidthSelected : 0
            });

            edges.add({from: 'BASESTATION_'+i, to: 'ne_' + response_data.near_end_device_name , color: ne_edge_color});
            edges.add({from: 'ne_' + response_data.near_end_device_name, to: 'fe_' + response_data.far_end_device_name , color: fe_edge_color});

            if (far_end_bs_sw_exist) {
                edges.add({from: 'fe_' + response_data.far_end_device_name, to: 'fe_sw_' + response_data.far_end_bs_switch_name , color: fe_bs_sw_edge_color});
                edges.add({from: 'fe_sw_' + response_data.far_end_bs_switch_name, to: 'far_end_base_station' , color: fe_bs_sw_edge_color});    
            } 
            else {
                edges.add({from: 'fe_' + response_data.far_end_device_name, to: 'far_end_base_station' , color: fe_edge_color});
                bs_back_edges_dict['far_end_base_station'] = 'fe_' + response_data.far_end_device_name
            }
            

            var sectors = far_end_base_station_list[i].sectors;
            
            if (!limit_till_bs) {
                var idu_id_list = [];
                for(j=0; j<sectors.length; j++){

                    var sector_severity = sectors[j].pl_info.severity ? sectors[j].pl_info.severity.toUpperCase() : 'NA',
                        sector_pl = sectors[j].pl_info.packet_loss ? sectors[j].pl_info.packet_loss : 'NA',
                        sector_latency = sectors[j].pl_info.latency ? sectors[j].pl_info.latency : 'NA',
                        sect_color_info_object = nocout_getSeverityColorIcon(sector_severity),
                        sector_polled_val = sectors[j].pl_info.value,
                        idu_id = 'idu_' + sectors[j].ip_address;
                        
                    if(sectors[j].device_tech.toLowerCase().indexOf('wimax') > -1){
                        var bs_device_type = 'IDU';
                    } else if(sectors[j].device_tech.toLowerCase().indexOf('pmp') > -1) {
                        var bs_device_type = 'ODU';
                    } else if(['ptp', 'p2p', 'P2P'].indexOf(sectors[j].device_tech.toLowerCase()) > -1){
                        var bs_device_type = 'Near End';
                    } else {
                        var bs_device_type = 'BS Device';
                    }

                    if (typeof sector_polled_val == 'undefined' || sector_polled_val == '') {
                        sector_polled_val = 'NA';
                    }

                    if (idu_id_list.indexOf(idu_id) == -1){

                        var idu_label = bs_device_type + '\n' +
                                         '\nIP Address : ' + sectors[j].ip_address + 
                                         '\nPacket Drop : ' + sector_pl +
                                         '\nLatency : ' + sector_latency;

                        nodes.add({
                            id: idu_id,
                            label: idu_label,
                            title: '<span style="color:'+sect_color_info_object.color+'"><i class="fa '+sect_color_info_object.icon+'""></i> ' + sector_severity + ' - ' + sector_polled_val + '</span>',
                            shape: 'image',
                            image: idu_image
                        });

                        idu_id_list.push(idu_id)
                    }

                    // if sector's severity is down then change edge color to red.
                    if (severity_check.indexOf(sector_severity.toLowerCase()) > -1) {
                        sec_edge_color = idu_edge_color = bs_edge_color ='#b94a48';
                        sector_image_url = sector_down_image_url

                        if (down_devices_list.indexOf(idu_id) == -1){
                            down_devices_list.push(idu_id)
                        }
                    } else {
                        sec_edge_color = idu_edge_color ='#468847',
                        sector_image_url = sector_up_image_url
                    }


                    nodes.add({
                        id: 'sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address,
                        label: 'Sector ID : '+sectors[j].sect_ip_id_title,
                        title: '<span style="color:'+sect_color_info_object.color+'"><i class="fa '+sect_color_info_object.icon+'""></i> ' + sector_severity + ' - ' + sector_polled_val + '</span>',
                        shape: 'image',
                        shapeProperties : {
                            useBorderWithImage : false
                        },
                        image: sector_image_url
                    })

                    // sectors are on configured on same IDU device so they have same device id
                    if(pl_device_list.indexOf(sectors[j].device_name) ==-1) {
                        pl_device_list.push(sectors[j].device_name)
                    }
                    
                    unique_sec_list.push('sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address)
                    device_nodeId_mapping[sectors[j].device_name] = unique_sec_list
                    ip_port_dict['sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address] = {
                                                                            'ip_address' : sectors[j].sect_ip_id_title,
                                                                            'port' : sectors[j].sect_port,
                                                                            'node_name' : ''
                                                                        }

                    // device_nodeId_mapping[sectors[j].device_name]

                    if(current_device_ip == sectors[j].ip_address){
                        highlight_id = sectors[j].sect_ip_id_title
                    }
                    edges.add({
                        // from: 'BASESTATION_'+i,
                        from: 'far_end_base_station',
                        to: idu_id,//'sec_' + sectors[j].sect_ip_id_title,
                        color: idu_edge_color,
                        smooth: {
                            type: 'cubicBezier',
                            forceDirection: 'horizontal',
                            roundness : 0.5
                        }
                    });

                    edges.add({
                        // from: 'BASESTATION_'+i,
                        from: idu_id,
                        to: 'sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address,
                        color: sec_edge_color,
                        smooth: {
                            type: 'cubicBezier',
                            forceDirection: 'horizontal',
                            roundness : 0.5
                        }
                    })


                    for(k=0; k<sectors[j].sub_station.length; k++) {
                        var ss_severity = sectors[j].sub_station[k].pl_info.severity ? sectors[j].sub_station[k].pl_info.severity.toUpperCase() : 'NA',
                            ss_pl = sectors[j].sub_station[k].pl_info.packet_loss ? sectors[j].sub_station[k].pl_info.packet_loss : 'NA',
                            ss_latency = sectors[j].sub_station[k].pl_info.latency ? sectors[j].sub_station[k].pl_info.latency : 'NA',
                            ss_color_info_object = nocout_getSeverityColorIcon(ss_severity),
                            ss_polled_val = sectors[j].sub_station[k].pl_info.value

                        if (typeof ss_polled_val == 'undefined' || ss_polled_val == '') {
                            ss_polled_val = 'NA';
                        }


                        var node_id = 'ss_' + sectors[j].sub_station[k].device_name;
                        nodes.add({
                            id: node_id, 
                            label: createNodeLabel(sectors[j].sub_station[k].ip_address, '', ss_pl, ss_latency),//sectors[j].sub_station[k].ip_address,
                            title: '<span style="color:'+ss_color_info_object.color+'"><i class="fa '+ss_color_info_object.icon+'""></i> ' +
                                    ss_severity + ' - ' + ss_polled_val + '</span>' ,
                            size: 30,
                            shape: 'image',
                            image: ss_image //sectors[j].sub_station[k].icon
                        })

                        pl_device_list.push(sectors[j].sub_station[k].device_name) 
                        device_nodeId_mapping[sectors[j].sub_station[k].device_name] = 'ss_' + sectors[j].sub_station[k].device_name
                        ip_port_dict['ss_' + sectors[j].sub_station[k].device_name] = {
                                                                            'ip_address' : sectors[j].sub_station[k].ip_address,
                                                                            'port' : '',
                                                                            'node_name' : ''
                                                                        }

                        if(current_device_ip == sectors[j].sub_station[k].ip_address){
                            highlight_id = sectors[j].sub_station[k].device_name
                        }

                        if (severity_check.indexOf(ss_severity.toLowerCase()) > -1) {
                            ss_edge_color = '#b94a48';
                            down_devices_list.push(node_id)
                        }

                        edges.add({from: 'sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address, to: 'ss_' + sectors[j].sub_station[k].device_name, color: sec_edge_color})
                    }
                }
            }
            
        }
    }
    else {
        for (var i=0;i<base_station_list.length;i++) {

            // adding nodes and edges in the network
            nodes.add({
                id: 'BASESTATION_'+i,
                label: base_station_list[i].bs_alias,
                image: base_station_list[i].bs_icon,
                size : updatedSize,
                title: base_station_list[i].bs_alias,
                shape: 'image',
                shapeProperties : {
                    useBorderWithImage : false
                },
                borderWidth : 0,
                borderWidthSelected : 0
            });

            if(backhaul_exist){ //if backhaul exists
                edges.add({from: 'ne_sw_' + response_data.bs_switch_name, to: 'BASESTATION_'+i, color: bs_sw_edge_color});
                bs_back_edges_dict['BASESTATION_'+i] = 'ne_sw_' + response_data.bs_switch_name
            } else { //if backhaul doesn't exist
                if(bs_convertor_exist){ //if backhaul doesn't exist and bs_convertor exists
                    edges.add({from: 'conv_' + response_data.bs_convertor_device_name, to: 'BASESTATION_'+i, color: bs_conv_edge_color});
                    bs_back_edges_dict['BASESTATION_'+i] = 'conv_' + response_data.bs_convertor_device_name
                } else { //backhaul, bs_convertor doesn't exist
                    if(pop_convertor_exist){ //if backhaul, bs_convertor doesn't exists but pop_convertor exists
                        edges.add({from: 'pop_' + response_data.bh_pop_device_name, to: 'BASESTATION_'+i, color: pop_edge_color});
                        bs_back_edges_dict['BASESTATION_'+i] = 'pop_' + response_data.bh_pop_device_name
                    } else { //if backhaul, pop_convertor, bs_convertor doesn't exist
                        if(aggr_switch_exist){ //if bs_convertor exists , backhaul, pop_convertor doesn't exist but aggr_switch exists 
                            edges.add({from: 'aggr_' + response_data.bh_aggregator_device_name, to: 'BASESTATION_'+i, color: aggr_sw_edge_color});
                            bs_back_edges_dict['BASESTATION_'+i] = 'aggr_' + response_data.bh_aggregator_device_name
                        } else {
                            if(pe_exist){
                                edges.add({from: 'PE', to: 'BASESTATION_'+i, color: pe_edge_color})
                                bs_back_edges_dict['BASESTATION_'+i] = 'PE'
                            }
                        }

                    }
                }
            }

            var sectors = base_station_list[i].sectors,
                idu_id_list = [];

            for(j=0; j<sectors.length; j++){
                var sector_severity = sectors[j].pl_info.severity ? sectors[j].pl_info.severity.toUpperCase() : 'NA',
                    sector_pl = sectors[j].pl_info.packet_loss ? sectors[j].pl_info.packet_loss : 'NA',
                    sector_latency = sectors[j].pl_info.latency ? sectors[j].pl_info.latency : 'NA',
                    sect_color_info_object = nocout_getSeverityColorIcon(sector_severity),
                    sector_polled_val = sectors[j].pl_info.value,
                    show_sector = true,
                    idu_id = 'idu_' + sectors[j].ip_address;
                    
                if(sectors[j].device_tech.toLowerCase().indexOf('wimax') > -1){
                    var bs_device_type = 'IDU';
                } else if(sectors[j].device_tech.toLowerCase().indexOf('pmp') > -1) {
                    var bs_device_type = 'ODU';
                } else if(['ptp', 'p2p', 'P2P'].indexOf(sectors[j].device_tech.toLowerCase()) > -1){
                    var bs_device_type = 'Near End',
                        bs_device_icon = near_end_image,
                        ss_device_icon = far_end_image;
                        show_sector = false
                } else {
                    var bs_device_type = 'BS Device';
                }

                // if sector's severity is down then change edge color to red.
                if (severity_check.indexOf(sector_severity.toLowerCase()) > -1) {
                    sec_edge_color = idu_edge_color = bs_edge_color =  '#b94a48';
                    sector_image_url = sector_down_image_url

                    if (down_devices_list.indexOf(idu_id) == -1){
                        down_devices_list.push(idu_id)
                    }
                } else {
                    sec_edge_color = idu_edge_color ='#468847',
                    sector_image_url = sector_up_image_url
                }

                if (typeof sector_polled_val == 'undefined' || sector_polled_val == '') {
                    sector_polled_val = 'NA';
                }

                if (idu_id_list.indexOf(idu_id) == -1){

                    var idu_label = bs_device_type + '\n' +
                                    '\nIP Address : ' + sectors[j].ip_address + 
                                    '\nPacket Drop : ' + sector_pl +
                                    '\nLatency : ' + sector_latency;

                    nodes.add({
                        id: idu_id,
                        label: idu_label,
                        title: '<span style="color:'+sect_color_info_object.color+'"><i class="fa '+sect_color_info_object.icon+'""></i> ' + sector_severity + ' - ' + sector_polled_val + '</span>',
                        shape: 'image',
                        image: !show_sector ? bs_device_icon : idu_image
                    });

                    idu_id_list.push(idu_id)
                }

                if (show_sector){
                    nodes.add({
                        id: 'sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address,
                        label: 'Sector ID : '+sectors[j].sect_ip_id_title,
                        title: '<span style="color:'+sect_color_info_object.color+'"><i class="fa '+sect_color_info_object.icon+'""></i> ' + sector_severity + ' - ' + sector_polled_val + '</span>',
                        shape: 'image',
                        shapeProperties : {
                            useBorderWithImage : false
                        },
                        image: sector_image_url
                    });
                }

                // sectors are on configured on same IDU device so they have same device id
                if (pl_device_list.indexOf(sectors[j].device_name) ==-1) {
                    pl_device_list.push(sectors[j].device_name)
                }
                unique_sec_list.push('sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address)
                device_nodeId_mapping[sectors[j].device_name] = unique_sec_list
                ip_port_dict['sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address] = {
                                                                        'ip_address' : sectors[j].sect_ip_id_title,
                                                                        'port' : sectors[j].sect_port,
                                                                        'node_name' : ''
                                                                    }

                if(current_device_ip == sectors[j].ip_address){
                    highlight_id = sectors[j].sect_ip_id_title
                }
                edges.add({
                    from: 'BASESTATION_'+i,
                    to: idu_id,
                    color: idu_edge_color,
                    smooth: {
                        type: 'cubicBezier',
                        forceDirection: 'horizontal',
                        roundness : 0.5
                    }
                });

                // edges.add({
                //         // from: 'BASESTATION_'+i,
                //         from: idu_id,
                //         to: 'sec_' + sectors[j].sect_ip_id_title,
                //         color: idu_edge_color,
                //         smooth: {
                //             type: 'cubicBezier',
                //             forceDirection: 'horizontal',
                //             roundness : 0.5
                //         }
                //     })


                for(k=0; k<sectors[j].sub_station.length; k++) {
                    var ss_severity = sectors[j].sub_station[k].pl_info.severity ? sectors[j].sub_station[k].pl_info.severity.toUpperCase() : 'NA',
                        ss_pl = sectors[j].sub_station[k].pl_info.packet_loss ? sectors[j].sub_station[k].pl_info.packet_loss : 'NA',
                        ss_latency = sectors[j].sub_station[k].pl_info.latency ? sectors[j].sub_station[k].pl_info.latency : 'NA',
                        ss_color_info_object = nocout_getSeverityColorIcon(ss_severity),
                        ss_polled_val = sectors[j].sub_station[k].pl_info.value

                    if (severity_check.indexOf(ss_severity.toLowerCase()) > -1) {
                        ss_edge_color = '#b94a48';
                    }

                    if (typeof ss_polled_val == 'undefined' || ss_polled_val == '') {
                        ss_polled_val = 'NA';
                    }

                    if(!show_sector){
                        fe_label = 'Far End\n\n'+createNodeLabel(sectors[j].sub_station[k].ip_address, '', ss_pl, ss_latency)
                    } else {
                        fe_label = createNodeLabel(sectors[j].sub_station[k].ip_address, '', ss_pl, ss_latency)
                    }

                    var node_id = 'ss_' + sectors[j].sub_station[k].device_name;
                    nodes.add({
                        id: node_id,
                        label: fe_label,
                        title: '<span style="color:'+ss_color_info_object.color+'"><i class="fa '+ss_color_info_object.icon+'""></i> ' +
                                ss_severity + ' - ' + ss_polled_val + '</span>' ,
                        size: 30,
                        shape: 'image',
                        image: !show_sector ? ss_device_icon : ss_image
                    })

                    if (!show_sector){
                        var unique_ss_id = 'ss_' + sectors[j].sub_station[k].device_name;
                    }

                    pl_device_list.push(sectors[j].sub_station[k].device_name)
                    device_nodeId_mapping[sectors[j].sub_station[k].device_name] = 'ss_' + sectors[j].sub_station[k].device_name
                    ip_port_dict['ss_' + sectors[j].sub_station[k].device_name] = {
                                                                                    'ip_address' : sectors[j].sub_station[k].ip_address,
                                                                                    'port' : '',
                                                                                    'node_name' : ''
                                                                                }

                    if(current_device_ip == sectors[j].sub_station[k].ip_address){
                        highlight_id = sectors[j].sub_station[k].device_name
                    }

                    edges.add({
                        from: show_sector ? 'sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address : idu_id,
                        to: 'ss_' + sectors[j].sub_station[k].device_name,
                        color: ss_edge_color
                    })

                    if (severity_check.indexOf(ss_severity.toLowerCase()) > -1){
                        down_devices_list.push(node_id)
                    }

                    edges.add({from: 'sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address, to: 'ss_' + sectors[j].sub_station[k].device_name, color: sec_edge_color})
                }
                edges.add({
                    // from: 'BASESTATION_'+i,
                    from: idu_id,
                    to: show_sector ? 'sec_' + sectors[j].sect_ip_id_title + '_||_' + sectors[j].ip_address : unique_ss_id,
                    color: show_sector ? sec_edge_color : ss_edge_color,
                    smooth: {
                        type: 'cubicBezier',
                        forceDirection: 'horizontal',
                        roundness : 0.5
                    }
                });
            }
        }       
    }


    // provide the data in the vis format
    var data = {
        nodes: nodes,
        edges: edges
    };

    for(i=0; i<down_devices_list.length; i++){
        nodes.update({
            id: down_devices_list[i],
            shape: 'circularImage',
         //    shapeProperties : {
            //  useBorderWithImage : true
            // },
            borderWidth : 6,
            borderWidthSelected : 8,
            color: {
                border: '#FF0000',
                background: '#ffffff',
                highlight: {
                    border: '#FF0000',
                    background: '#ffffff',
                }
            }
        })
    }

    // Highlighting selected device
    // nodes.update({
    //  id: highlight_id,
    //  color : {
    //      border : '#444',
    //      background : '#ffffff',
    //      highlight : {
    //          border : '#444'
    //      }
    //  },
    //  shadow : {
    //      size : 2
    //  },
    //  shapeProperties : {
    //      useBorderWithImage : true
    //  },
    //  borderWidth: 2,
    //  borderWidthSelected: 2
    // });

    /*  This is for updating the back edge of BS
        Becuase BS is not a device so it's back edge color
        should be depends on the IDU device
    */
    for(base_station_id in bs_back_edges_dict){
        edges.update({
            from: bs_back_edges_dict[base_station_id],
            to: base_station_id,
            color: bs_edge_color
        })
    }

    // initialize your network
    network = new vis.Network(container, data, options);

    /**
    * This event triggers when a node is selected/clicked
    * @event selectNode
    */
    network.on('selectNode', function(e){
        // Further will be processed if selected node id contains 'sec_' in it.
        if(e.nodes[0].toLowerCase().indexOf('sec_') > -1){
            var url_with_params = '',
                table_html = '',
                table_data_html = '',
                sector_id = e.nodes[0].split('sec_')[1].split('_||_')[0].trim(),
                device_ip = e.nodes[0].split('sec_')[1].split('_||_')[1].trim();

            url_with_params = topo_alarms_url + "?device_ip="+ device_ip +"&sector_id="+ sector_id;
            $.ajax({
                url: base_url + url_with_params,
                type: 'GET',
                success: function(response){
                    var alarms_list = response['data']['alarms_list'],
                        extra_info = response['data']['extra_info'];

                    var bs_alias = extra_info.alias && extra_info.alias != undefined  ? extra_info.alias : 'NA',
                        bs_city = extra_info.city && extra_info.city != undefined ? extra_info.city : 'NA',
                        bs_state = extra_info.state && extra_info.state != undefined ? extra_info.state : 'NA',
                        bh_connectivity = extra_info.bh_connectivity && extra_info.bh_connectivity != undefined ? extra_info.bh_connectivity : 'NA',
                        device_type = extra_info.device_type && extra_info.device_type != undefined ? extra_info.device_type : 'NA';

                    // Creating Table HTML for boot box.
                    if(alarms_list.length > 0){
                        table_data_html += '<tbody>'
                        for(var i=0; i<alarms_list.length; i++){
                            table_data_html +=  '<tr>\
                                                    <td>'+ alarms_list[i].severity +'</td>\
                                                    <td>'+ alarms_list[i].ip_address +'</td>\
                                                    <td>'+ sector_id +'</td>\
                                                    <td>'+ bs_alias +'</td>\
                                                    <td>'+ bs_city +'</td>\
                                                    <td>'+ bs_state +'</td>\
                                                    <td>'+ bh_connectivity +'</td>\
                                                    <td>'+ device_type +'</td>\
                                                    <td>'+ alarms_list[i].eventname +'</td>\
                                                    <td>'+ (alarms_list[i].uptime ? alarms_list[i].uptime :'NA') +'</td>\
                                                    <td>'+ (alarms_list[i].alarm_count ? alarms_list[i].alarm_count :'NA')+'</td>\
                                                    <td>'+ (alarms_list[i].first_occurred ? alarms_list[i].first_occurred :'NA') + '</td>\
                                                    <td>'+ (alarms_list[i].last_occurred ? alarms_list[i].last_occurred :'NA') + '</td>\
                                                </tr>'
                        }
                        table_data_html += '</tbody>'
                    }

                    table_html +=   '<div style="overflow: auto">\
                                        <table id="bootbox_alarms_table">\
                                            <thead>\
                                                <tr>\
                                                    <th>Severity</th>\
                                                    <th>IP</th>\
                                                    <th>Sector ID</th>\
                                                    <th>BS Name</th>\
                                                    <th>City</th>\
                                                    <th>State</th>\
                                                    <th>BH Connectivity</th>\
                                                    <th>Device Type</th>\
                                                    <th>Event Name</th>\
                                                    <th>Uptime</th>\
                                                    <th>Alarm Count</th>\
                                                    <th>First Occurred</th>\
                                                    <th>Last Occurred</th>\
                                                </tr>\
                                            </thead>'
                                            + table_data_html +
                                        '</table>\
                                    </div>'
                    bootbox.dialog({
                        title: 'Sector Impact',
                        message: table_html,
                        className: 'bootbox_large'
                    });
                    
                    // Initializing datatble.js on Alarms table.
                    setTimeout(function(){
                        var tableId = 'bootbox_alarms_table'
                        $('#bootbox_alarms_table').DataTable({
                            fnInitComplete: function(oSettings) {
                                $('#'+tableId+'_wrapper div.dataTables_length label select, #'+tableId+'_wrapper div.dataTables_filter label input').addClass("form-control");
                                $('#'+tableId+'_wrapper div.dataTables_length label select, #'+tableId+'_wrapper div.dataTables_filter label input').addClass("input-sm");
                                $('#'+tableId+'_wrapper div.dataTables_length label select, #'+tableId+'_wrapper div.dataTables_filter label input').css("max-width","150px");
                            }
                        });
                    }, 100)
                }
            })
        }
    });

    /**
    *  **************************************************************************************************
    *  Following commented code is for on click tool-tip functionaloty, which is not required right now.*
    *  **************************************************************************************************
    */

    // adding a event listner on Nodes
    // network.on('selectNode', function (event, properties, senderId) {
    //    try {
    //         single_bs_id = JSON.parse(bs_id)[0];
    //     } catch(e) {
    //     // console.error(e);
    //    }
    //    var window_title = '';
    //    var no_polled_tab = false;

    //    if(event.nodes[0] == 'BACKHAUL'){
    //         var type = "BH";
    //         var passing_id = response_data.bh_id;
    //         device_id = response_data.bh_device_id;
    //         device_tech = response_data.bh_device_tech;
    //         device_type = response_data.bh_device_type;
    //         window_title = 'Backhaul';
    //    }
    //    else if(event.nodes[0].indexOf('BASESTATION') > -1){
    //         var type = "BS";
    //         var res = event.nodes[0].split("_");
    //         var bs_index = parseInt(res[1]);
    //         var passing_id = base_station_list[bs_index]['bs_id'];
    //         window_title = 'Base Station';
    //         device_id = ''
    //         no_polled_tab = true;
    //    }
    //    else if(event.nodes[0].indexOf("SECTOR") > -1){
    //         var res = event.nodes[0].split("_");
    //         var bs_index = parseInt(res[1]) - 1;
    //         var sect_index = parseInt(res[2]) - 1;
    //         var type = "SECT";
    //         var passing_id = base_station_list[bs_index].sectors[sect_index].id;
    //         device_tech = base_station_list[bs_index].sectors[sect_index].device_tech;
    //         device_type = base_station_list[bs_index].sectors[sect_index].device_type;
    //         device_id = base_station_list[bs_index].sectors[sect_index].device_id;
    //         window_title = 'Sector';
    //    }
    //    else if(event.nodes[0].indexOf("SUBSTATION") > -1){
    //         var res = event.nodes[0].split("_");
    //         var bs_index = parseInt(res[1]) - 1;
    //         var sect_index = parseInt(res[2]) - 1;
    //         var ss_index = parseInt(res[3]) - 1;
    //         var type = "SS";
    //         var passing_id = base_station_list[bs_index].sectors[sect_index].sub_station[ss_index].id;
    //         device_id = base_station_list[bs_index].sectors[sect_index].sub_station[ss_index].device_id;
    //         device_tech = base_station_list[bs_index].sectors[sect_index].sub_station[ss_index].device_tech;
    //         device_type = base_station_list[bs_index].sectors[sect_index].sub_station[ss_index].device_type;
    //         window_title = 'Sub Station';
    //    }

    //     // Ajax request for tooltip info
    //    $.ajax({                
    //         url: base_url +  "/performance/get_topology/tool_tip/?type=" + type + '&id='+passing_id,
    //         type: 'GET',
    //         success: function(response) {
    //          var result = response;

    //          if (typeof(response) == 'string') {
    //              result = JSON.parse(response);
    //          }

    //          if (result.success) {
    //              if(window_title.toLowerCase().indexOf('base station') > -1) {
                        
    //                  var actual_data = rearrangeTooltipArray(bs_toolTip_static,result.data);
                        
    //              } else if(window_title.toLowerCase().indexOf('sub station') > -1) {
    //                  var actual_data = rearrangeTooltipArray(ss_toolTip_static,result.data)
    //                  if(device_tech.toLowerCase() == 'p2p') {
    //                      toolTip_polled_tab = ptp_ss_toolTip_polled;
    //                  } else if(device_tech.toLowerCase() == 'wimax') {
    //                      toolTip_polled_tab = wimax_ss_toolTip_polled;
    //                  } else if(device_tech.toLowerCase() == 'pmp') {
    //                      if(device_type.toLowerCase() == 'radwin5kss' ) {
    //                          toolTip_polled_tab = pmp_radwin5k_ss_toolTip_polled;
    //                      } else {
    //                          toolTip_polled_tab = pmp_ss_toolTip_polled;
    //                      }
    //                  }
    //              } else if(window_title.toLowerCase().indexOf('backhaul') > -1) {
    //                  var actual_data = rearrangeTooltipArray(bh_toolTip_static,result.data)
    //                  if(device_type.toLowerCase() == 'pine') {
    //                      toolTip_polled_tab = mrotech_bh_toolTip_polled;
    //                  } else if(device_type.toLowerCase() == 'switch') {
    //                      toolTip_polled_tab = switch_bh_toolTip_polled;
    //                  } else if(device_type.toLowerCase() == 'rici') {
    //                      toolTip_polled_tab = rici_bh_toolTip_polled;
    //                  }

    //              } else if(window_title.toLowerCase().indexOf('sector') > -1) {
                        
    //                  if(device_tech.toLowerCase() == 'p2p') {
    //                      actual_data = rearrangeTooltipArray(ptp_sector_toolTip_static,result.data);
    //                      toolTip_polled_tab = ptp_sector_toolTip_polled;
    //                  } else if(device_tech.toLowerCase() == 'wimax') {
    //                      actual_data = rearrangeTooltipArray(wimax_sector_toolTip_static,result.data);
    //                      toolTip_polled_tab = wimax_sector_toolTip_polled;
    //                  } else if(device_tech.toLowerCase() == 'pmp') {
    //                      actual_data = rearrangeTooltipArray(pmp_sector_toolTip_static,result.data);
    //                      toolTip_polled_tab = pmp_sector_toolTip_polled;
    //                  } else {
    //                      actual_data = result.data;
    //                  }

    //              }


    //              infoTable = '';

    //              infoTable += '<div class="tabbable">';
    //              /*Tabs Creation Start*/
    //              if(no_polled_tab){
    //                  infoTable += '<ul class="nav nav-tabs">\
    //                              <li class="active"><a href="#static_block" data-toggle="tab">\
    //                              <i class="fa fa-arrow-circle-o-right"></i> Static Info</a></li>\
    //                              <i class="fa fa-spinner fa fa-spin hide"> </i></a>\
    //                              </li>';
    //              }
    //              else {
    //                  infoTable += '<ul class="nav nav-tabs">\
    //                              <li class="active"><a href="#static_block" data-toggle="tab">\
    //                              <i class="fa fa-arrow-circle-o-right"></i> Static Info</a></li>\
    //                              <li class=""><a href="#polled_block" data-toggle="tab" id="polled_tab"\
    //                              device_id="'+device_id+'" point_type="'+type+'" \
    //                              device_tech="'+device_tech+'" \
    //                              device_type="'+device_type+'">\
    //                              <i class="fa fa-arrow-circle-o-right"></i> Polled Info \
    //                              <i class="fa fa-spinner fa fa-spin hide"> </i></a>\
    //                              </li>';
    //              }
    //              infoTable += '</ul>';

    //              infoTable += '<div class="tab-content"><div class="tab-pane fade active in" id="static_block"><div class="divide-10"></div>';
    //              infoTable += "<table class='table table-bordered table-hover'><tbody>";
    //              infoTable += createTableDataHtml(actual_data);
    //              infoTable += "</tbody></table>";
    //              infoTable += '</div>';
    //              infoTable += '<div class="tab-pane fade" id="polled_block"><div class="divide-10"></div>';
    //              infoTable += "<table class='table table-bordered table-hover'><tbody>";
    //              infoTable += createTableDataHtml(toolTip_polled_tab);
    //              infoTable += "</tbody></table>";
    //              infoTable += '</div></div>';

    //              /*Final infowindow content string*/
    //              windowContent = "<div class='windowContainer' style='z-index: 300; position:relative;'>\
    //                                <div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  \
    //                                "+window_title+"</h4><div class='tools'><a class='close_info_window' title='Close'>\
    //                                <i class='fa fa-times text-danger'></i></a></div></div>\
    //                                <div class='box-body'><div align='center'>"+infoTable+"</div>\
    //                                <div class='clearfix'></div><div class='pull-right'></div><div class='clearfix'>\
    //                                </div></div></div></div>";

    //              $("#infoWindowContainer").html(windowContent);
    //              $("#infoWindowContainer").removeClass('hide');
    //          } else {

    //          }

    //         },
    //         error : function(err) {
    //         // console.log('TopoToolTip Error Working');
    //         },
    //         complete: function() {
    //         // console.log('TopoToolTip compulsary Working');

    //         }

    //     });
    // });    
}


/**
* This event triggers when close button on infowindow clicked
* @event Click(Using Delegate)
*/
// $('#infoWindowContainer').delegate('.close_info_window','click',function(e) {
//  $('#infoWindowContainer').html("");
//  network.unselectAll();
//  if(!$('#infoWindowContainer').hasClass("hide")) {
//      $('#infoWindowContainer').addClass("hide");
//  }
// });

    /**
* This event triggers when Tabs on infowindow clicked(or selected) 
* @event Click(Using Delegate)
*/
// $("#infoWindowContainer").delegate(".nav-tabs li a",'click',function(evt) {

//  var current_device_id = evt.currentTarget.attributes.device_id ? evt.currentTarget.attributes.device_id.value : "",
//      point_type = evt.currentTarget.attributes.point_type ? evt.currentTarget.attributes.point_type.value : "",
//      dom_id = evt.currentTarget.attributes.id ? evt.currentTarget.attributes.id.value : "",
//      device_tech = evt.currentTarget.attributes.device_tech ? $.trim(evt.currentTarget.attributes.device_tech.value.toLowerCase()) : "",
//      device_type = evt.currentTarget.attributes.device_type ? $.trim(evt.currentTarget.attributes.device_type.value.toLowerCase()) : "",
//      href_attr = evt.currentTarget.attributes.href ? evt.currentTarget.attributes.href.value.split("#") : "",
//      block_id = href_attr.length > 1 ? href_attr[1] : "",
//      pl_attr = evt.currentTarget.attributes.pl_value,
//      device_pl = pl_attr && pl_attr.value != 'N/A' ? pl_attr.value : "";

//  if(dom_id && point_type && current_device_id) {
//      // Show Spinner
//      if(dom_id == 'polled_tab') {
//          if($("a#"+dom_id+" .fa-spinner").hasClass("hide")) {
//              $("a#"+dom_id+" .fa-spinner").removeClass("hide");
//          }

//          // Make AJAX Call
//          periodic_tooltip_call = $.ajax({
//              url: base_url+'/network_maps/perf_info/?device_id='+current_device_id+"&device_pl="+device_pl,
//              type : "GET",
//              success : function(response) {

//                  var result = "",
//                      polled_data_html = "";
//                  // Type check for response
//                  if(typeof response == 'string') {
//                      result = JSON.parse(response);
//                  } else {
//                      result = response;
//                  }

//                  if(result && result.length > 0) {

//                      var fetched_polled_info = result,
//                          tooltip_info_dict = [];

//                      if(point_type == 'SECT') {
                            
//                          if(ptp_tech_list.indexOf(device_tech) > -1) {
//                              tooltip_info_dict = rearrangeTooltipArray(ptp_sector_toolTip_polled,fetched_polled_info);
//                          } else if(device_tech == 'wimax') {
//                              tooltip_info_dict = rearrangeTooltipArray(wimax_sector_toolTip_polled,fetched_polled_info);
//                          } else if(device_tech == 'pmp') {
//                              if(device_type == 'radwin5kbs') {
//                                  tooltip_info_dict = rearrangeTooltipArray(pmp_radwin5k_sector_toolTip_polled, fetched_polled_info);
//                              } else {
//                                  tooltip_info_dict = rearrangeTooltipArray(pmp_sector_toolTip_polled, fetched_polled_info);
//                              }
//                          } else {
//                              // pass
//                          }
//                      } else if(point_type == 'SS') {
//                          if(ptp_tech_list.indexOf(device_tech) > -1) {
//                              tooltip_info_dict = rearrangeTooltipArray(ptp_ss_toolTip_polled,fetched_polled_info);
//                          } else if(device_tech == 'wimax') {
//                              tooltip_info_dict = rearrangeTooltipArray(wimax_ss_toolTip_polled,fetched_polled_info);
//                          } else if(device_tech == 'pmp') {                                
//                              if(device_type == 'radwin5kss') {
//                                  tooltip_info_dict = rearrangeTooltipArray(pmp_radwin5k_ss_toolTip_polled, fetched_polled_info);
//                              } else {
//                                  tooltip_info_dict = rearrangeTooltipArray(pmp_ss_toolTip_polled, fetched_polled_info);
//                              }                                
//                          } else {
//                              // pass
//                          }
//                      } else if(point_type == 'BH') {
//                          if(device_type == 'pine') {
//                              tooltip_info_dict = rearrangeTooltipArray(mrotech_bh_toolTip_polled,fetched_polled_info);
//                          } else if(device_type == 'switch') {
//                              tooltip_info_dict = rearrangeTooltipArray(switch_bh_toolTip_polled,fetched_polled_info);
//                          } else if(device_type == 'rici') {
//                              tooltip_info_dict = rearrangeTooltipArray(rici_bh_toolTip_polled,fetched_polled_info);
//                          }
//                      } else {
//                          // pass
//                      }

//                      polled_data_html = "";
                        
//                      polled_data_html += "<table class='table table-bordered table-hover'><tbody>";

//                      /*Poll Parameter Info*/
//                      for(var i=0; i< tooltip_info_dict.length; i++) {
//                          var url = "",
//                              text_class = "";
//                          if(tooltip_info_dict[i]["show"]) {
//                              // GET text color as per the severity of device
//                              var severity = tooltip_info_dict[i]["severity"],
//                                  severity_obj = nocout_getSeverityColorIcon(severity),
//                                  text_color = severity_obj.color ? severity_obj.color : "",
//                                  cursor_css = text_color ? "cursor:pointer;" : "";

//                              // Url
//                              url = tooltip_info_dict[i]["url"] ? tooltip_info_dict[i]["url"] : "";
//                              text_class = "text-primary";

//                              polled_data_html += "<tr style='color:"+text_color+";'><td url='"+url+"' style='"+cursor_css+"'>"+tooltip_info_dict[i]['title']+"</td>\
//                                                   <td>"+tooltip_info_dict[i]['value']+"</td></tr>";
//                          }
//                      }

//                      polled_data_html += "</tbody></table>";

//                      // Clear the polled block HTML
//                      $("#"+block_id).html('<div class="divide-10"></div>');

//                      // Append the polled data info
//                      $("#"+block_id).append(polled_data_html);

//                  } else {
//                      $.gritter.add({
//                          title: "Polled Info",
//                          text: "Please try again later.",
//                          sticky: false,
//                          time : 1000
//                      });
//                  }
//              },
//              error : function(err) {

//                  if(err.statusText != 'abort') {
//                      $.gritter.add({
//                          title: "Polled Info",
//                          text: err.statusText,
//                          sticky: false,
//                          time : 1000
//                      });
//                  }
//              },
//              complete : function() {
//                  if(!$("a#"+dom_id+" .fa-spinner").hasClass("hide")) {
//                      $("a#"+dom_id+" .fa-spinner").addClass("hide");
//                  }       
//              }
//          });

//      }
//  } else {
//      if(!$(".nav-tabs li a:last-child .fa-spinner").hasClass("hide")) {
//          $(".nav-tabs li a:last-child .fa-spinner").addClass("hide");
//      }
//  }
// });

// function createTableDataHtml(data_obj) {

//     var table_html = "";

//     if(data_obj && data_obj.length) {
//         for(var i=0; i< data_obj.length; i++) {
//             var url = '',
//                 text_class = '',
//                 text_color = '',
//                 highlight_class = '';

//             if(data_obj[i]["show"]) {                            
//                 var val = data_obj[i]["value"];

//                 // current value
//                 actual_val = val;

//                 // This is useful only for polled data
//                 url = data_obj[i]["url"] ? $.trim(data_obj[i]["url"]) : '';

//                 table_html += "<tr style='color:"+text_color+";'><td class='"+highlight_class+"' url='"+url+"'>\
//                               "+data_obj[i]['title']+"</td><td>"+actual_val+"</td></tr>";
//             }
//         }
//     }

//     return table_html;
// }


/**
* This function creates label for all nodes in network
* @method createNodeLabel
* @param ip_addr {string}, ip address of current node
* @param port {string}, port of current node
* @param pack_drop {string}, Packet drop value of current node
* @param latency {string}, Latency of current node
*/
function createNodeLabel(ip_addr, port, pack_drop, latency, node_name) {
    if (port == undefined || port.length == 0) {
        port_str = '\nPort : NA'
    } else {
        port_str = '\nPort : ' + port
    }

    if (node_name == undefined || node_name.length == 0) {
        node_name = ''
    } else {
        node_name = node_name + '\n\n'
    }

    // showing ports if Flag is true
    port_str = show_ports ? port_str : ''

    result_str = node_name +
                 'IP Address : ' + ip_addr + 
                 port_str +
                 '\nPacket Drop : ' + pack_drop +
                 '\nLatency : ' + latency

    return result_str
}

/**
* This function update Node pl info periodically
* @method updateNetworkPeriodically
* @param pl_info_list {array}, list containing pl info of nodes
*/
function updateNetworkPeriodically(pl_info_list) {

    pl_list_data = pl_info_list.data
    // console.log(pl_list_data);


    for (var i = 0; i < pl_list_data.length ; i++) {

        var device_severity = pl_list_data[i].severity ? pl_list_data[i].severity.toUpperCase() : 'NA',
            device_pl = pl_list_data[i].packet_loss ? pl_list_data[i].packet_loss : 'NA',
            device_latency = pl_list_data[i].latency ? pl_list_data[i].latency : 'NA',
            device_color_info_object = nocout_getSeverityColorIcon(device_severity),
            device_polled_val = pl_list_data[i].value;

        id = device_nodeId_mapping[pl_list_data[i].id]
        if (typeof id == 'object') {

            for (var j=0; j< id.length ; j++){
                unique_id = id[j]
                var current_ip = ip_port_dict[unique_id].ip_address ? ip_port_dict[unique_id].ip_address : 'NA',
                    current_port = ip_port_dict[unique_id].port ? ip_port_dict[unique_id].port : 'NA',
                    current_node_name = ip_port_dict[unique_id].node_name;

                if (severity_check.indexOf(device_severity.toLowerCase()) > -1){
                    sec_edge_color = '#b94a48';
                }
                nodes.update({
                    id : id[j],
                    label : createNodeLabel(current_ip, current_port, device_pl, device_latency, current_node_name),
                    title: '<span style="color:'+device_color_info_object.color+'"><i class="fa '+device_color_info_object.icon+'""></i> '+device_severity+' - '+device_polled_val+'</span>'
                });
            }
        }
        else {
            var current_ip = ip_port_dict[id].ip_address ? ip_port_dict[id].ip_address : 'NA' ,
                current_port = ip_port_dict[id].port ? ip_port_dict[id].port : 'NA',
                current_node_name = ip_port_dict[id].node_name;

            if (id.indexOf('PE') > -1) {
                if (severity_check.indexOf(device_severity.toLowerCase()) > -1){
                    pe_edge_color = '#b94a48';
                }
            }
            if (id.indexOf('aggr_') > -1) {
                if (severity_check.indexOf(device_severity.toLowerCase()) > -1){
                    aggr_sw_edge_color = '#b94a48';
                }
            }
            if (id.indexOf('pop_') > -1) {
                if (severity_check.indexOf(device_severity.toLowerCase()) > -1){
                    pop_edge_color = '#b94a48';
                }
            }
            if (id.indexOf('conv_') > -1) {
                if (severity_check.indexOf(device_severity.toLowerCase()) > -1){
                    bs_conv_edge_color = '#b94a48';
                }
            }
            if (id.indexOf('ne_sw_') > -1) {
                if (severity_check.indexOf(device_severity.toLowerCase()) > -1){
                    bs_sw_edge_color = '#b94a48';
                }
            }
            if(is_ptp_bh){
                if (id.indexOf('ne_') > -1) {
                    if (severity_check.indexOf(device_severity.toLowerCase()) > -1){
                        ne_edge_color = '#b94a48';
                    }
                }
                if (id.indexOf('fe_') > -1) {
                    if (severity_check.indexOf(device_severity.toLowerCase()) > -1){
                        fe_edge_color = '#b94a48';
                    }
                }
                if (id.indexOf('fe_sw_') > -1) {
                    if (severity_check.indexOf(device_severity.toLowerCase()) > -1){
                        fe_bs_sw_edge_color = '#b94a48';
                    }
                }   
            }
            
            nodes.update({
                id : id,
                label : createNodeLabel(current_ip, current_port, device_pl, device_latency, current_node_name),
                title: '<span style="color:'+device_color_info_object.color+'"><i class="fa '+device_color_info_object.icon+'""></i> '+device_severity+' - '+device_polled_val+'</span>'
            });
        }
        
    }

    if (is_topo_tab_clicked){
        network.redraw();   
    }
    
}