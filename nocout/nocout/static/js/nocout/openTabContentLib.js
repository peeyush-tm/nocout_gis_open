/**
 * This library handles the tab click event & load the data as per the selected tab.
 * @class openTabContentLib
 * @event click
 */

var tables_info = {},
    last_clicked_tab = "",
    timeOutId = "",
    ptp_list = ['ptp','p2p'],
    pmp_list = ['pmp', 'rad5'],
    rad5_list = ['rad5'],
    wimax_list = ['wimax','wifi','temp','ulissue','sectorutil'],
    other_list = ['converter','bh','backhaul','bhutil'],
    server_side_rendering = true,
    refresh_time = '';

/**
 * This event triggers when any tab clicked
 * @event click
 */
$(".nav-tabs li a").click(function (e, isFirst) {
    var tab_txt = $.trim($(this).text());
    
    // Update the breadcrumb as per clicked tab
    $(".breadcrumb li.active").html(tab_txt);

    /*Initialize the timer in seconds.Right now its 1 year*/
    /*86400 is 24 hrs miliseconds*/
    var timer = 86400 * 30 * 12; // 1 Year in seconds
    // var timer = 300; // 5 Minutes in seconds

    timer = refresh_time ? refresh_time : timer;

    /*Clear or Reset Time out*/
    clearTimeout(timeOutId);

    var anchor_id = e.currentTarget.id,
        browser_url_array = window.location.href.split("#"),
        second_condition = "";

    if (isFirst) {
        second_condition = isFirst;
    } else {
        second_condition = false;
    }

    var destroy = false,
        header_attr = e.currentTarget.attributes.data_header,
        url_attr = e.currentTarget.attributes.data_url,
        div_id = e.currentTarget.href.split("#").length > 1 ? e.currentTarget.href.split("#")[1] : "",
        table_id = $("#" + div_id).find("table").length > 0 ? $("#" + div_id).find("table")[0].id : "",
        ajax_url = url_attr && url_attr.value ? url_attr.value : "",
        grid_headers = header_attr && header_attr.value ? JSON.parse(header_attr.value) : "",
        isTab = $('.nav li.active .hidden-inline-mobile');


    if (table_id && ajax_url && grid_headers) {
        if (last_clicked_tab != e.currentTarget.id || second_condition) {
            var tab_id = table_id ? table_id.toLowerCase() : "";

            console.log(tab_id);
            var isPtp = ptp_list.filter(function(list_val) {
                    return tab_id.search(list_val) > -1
                }).length,
                is_rad5 = rad5_list.filter(function(list_val) {
                    return tab_id.search(list_val) > -1
                }).length,
                pmpLength = pmp_list.filter(function(list_val) {
                    return tab_id.search(list_val) > -1
                }).length,
                wimaxLength = wimax_list.filter(function(list_val) {
                    return tab_id.search(list_val) > -1
                }).length,
                isPmpWimax = pmpLength + wimaxLength,
                isOther = other_list.filter(function(list_val) {
                    return tab_id.search(list_val) > -1
                }).length;
            // If tab is ptp
            if (isPtp > 0) {
                for (var i = 0; i < grid_headers.length; i++) {
                    var column = grid_headers[i];
                    if (column.mData.indexOf("sector_id") > -1) {
                        if (column.bVisible) {
                            column.sClass = "hide";
                        } else {
                            column["sClass"] = "hide";
                        }
                    }
                }
            // If tab is PMP or Wimax
            } else if (isPmpWimax > 0) {
                if (window.location.href.search("customer_live") == -1 && window.location.href.search("customer_detail") == -1) {
                    for (var i = 0; i < grid_headers.length; i++) {
                        var column = grid_headers[i];
                        if (column.mData.indexOf("circuit_id") > -1 || column.mData.indexOf("customer_name") > -1) {
                            if (column.bVisible) {
                                column.sClass = "hide";
                            } else {
                                column["sClass"] = "hide";
                            }
                        }
                    }
                }
            // If tab is other devices
            } else if (isOther > 0) {
                // For other case
                for (var i = 0; i < grid_headers.length; i++) {
                    var column = grid_headers[i],
                        condition1 = column.mData.indexOf("sector_id") > -1,
                        condition2 = column.mData.indexOf("circuit_id") > -1,
                        condition3 = column.mData.indexOf("customer_name") > -1;

                    if (condition1 || condition2 || condition3) {
                        if (column.bVisible) {
                            column.sClass = "hide";
                        } else {
                            column["sClass"] = "hide";
                        }
                    }
                }
            }

            // For radwin5k specific columns.
            if (is_rad5 > 0){
                for (var i = 0; i < grid_headers.length; i++) {
                    var column = grid_headers[i];
                    if (column.mData.indexOf("region") > -1 || column.mData.indexOf("min_latency") > -1) {
                        if (!column.bVisible) {
                            column.bVisible = true;
                        } else {
                            column["bVisible"] = true;
                        }
                    }
                }
            }

            var con1 = window.location.href.indexOf('alert_center/customer_alert/') > -1,
                con2 = window.location.href.indexOf('alert_center/network_alert/') > -1;
            // If single device alert page
            if (con1 || con2) {

                // Add service_name get param to url if not exists
                if (ajax_url.indexOf('?service_name') == -1) {
                    
                    if (table_id == 'network_alert_service_table') {
                        service_name = 'service';
                    } else if (table_id == 'network_alert_down_table') {
                        service_name = 'down';
                    } else if (table_id == 'network_alert_packet_table') {
                        service_name = 'packet_drop';
                    } else if (table_id == 'network_alert_latency_table') {
                        service_name = 'latency';
                    } else {
                        service_name = 'ping';
                    }
                    // Add service_name get param to url
                    ajax_url = ajax_url+'?service_name='+service_name;
                }


                try {

                    if (isDateFilterApplied) {
                        
                        var epoch_startDate = startDate / 1000,
                            epoch_endDate = endDate / 1000;

                        ajax_url = ajax_url+'&start_date='+epoch_startDate+'&end_date='+epoch_endDate;

                        // If we have tab info params
                        if (tables_info[anchor_id]) {
                            var data_param = tables_info[anchor_id].data_extra_param,
                                splitted_params = data_param.split("}");

                            splitted_params[1] = "'start_date' : '"+epoch_startDate+"', 'end_date' : '"+epoch_endDate+"'}"

                            tables_info[anchor_id].data_extra_param = splitted_params.join(",");
                        }
                    }
                } catch(e) {
                    // console.log(e);
                }
            }
            
            if (!tables_info[anchor_id]) {
                /*Call createDataTable function to create the data table for specified dom element with given data*/
                dataTableInstance.createDataTable(
                    table_id,
                    grid_headers,
                    ajax_url,
                    destroy
                );
            } else {
                if (tables_info[anchor_id]) {
                    var table_title = tables_info[anchor_id].table_title ? tables_info[anchor_id].table_title : false,
                        app_name = tables_info[anchor_id].app_name ? tables_info[anchor_id].app_name : false,
                        header_class_name = tables_info[anchor_id].header_class_name ? tables_info[anchor_id].header_class_name : false,
                        data_class_name = tables_info[anchor_id].data_class_name ? tables_info[anchor_id].data_class_name : false,
                        header_extra_param = tables_info[anchor_id].header_extra_param ? encodeURIComponent(tables_info[anchor_id].header_extra_param) : false,
                        data_extra_param = tables_info[anchor_id].data_extra_param ? encodeURIComponent(tables_info[anchor_id].data_extra_param) : false,
                        excluded_columns = tables_info[anchor_id].excluded ? encodeURIComponent(tables_info[anchor_id].excluded) : false;

                    // SET/RESET server side paging flag
                    if (tables_info[anchor_id].serverside_rendering != undefined) {
                        server_side_rendering = tables_info[anchor_id].serverside_rendering;
                    } else {
                        server_side_rendering = true;
                    }

                    /*Call createDataTable function to create the data table for specified dom element with given data*/
                    dataTableInstance.createDataTable(
                        table_id,
                        grid_headers,
                        ajax_url,
                        destroy,
                        table_title,
                        app_name,
                        header_class_name,
                        data_class_name,
                        header_extra_param,
                        data_extra_param,
                        excluded_columns
                    );
                }
            }
        }
    } else {
        /*Hide the spinner*/
        hideSpinner();
    }

    /*Save the last clicked tab id in global variable for condition checks*/
    last_clicked_tab = e.currentTarget.id;
    /*Refresh the tab after every given timer. Right now it is 5 minutes*/
    timeOutId = setTimeout(function () {
        $("#"+anchor_id).trigger('click', true);
    }, (Number(timer) * 1000));
});