/**
 * This library handles the tab click event & load the data as per the selected tab.
 * @class openTabContentLib
 * @event click
 */

var last_clicked_tab = "",
    timeOutId = "",
    ptp_list = ['ptp','p2p'],
    pmp_list = ['pmp'],
    wimax_list = ['wimax','wifi','temp','ulissue','sectorutil'],
    other_list = ['converter','bh','backhaul','bhutil'];

$(".nav-tabs li a").click(function (e, isFirst) {

    /*Initialize the timer in seconds.Right now its 1 year*/
    /*86400 is 24 hrs miliseconds*/
    var timer = 86400 * 30 * 12;
    /* 1 Year in seconds */

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

    /*Current Tab content id or anchor tab hyperlink*/
    new_url = e.currentTarget.href;


    if (!isFirst) {
        window.location.href = new_url;
    }

    var destroy = false,
        div_id = e.currentTarget.href.split("#").length > 1 ? e.currentTarget.href.split("#")[1] : "",
        table_id = $("#" + div_id).find("table").length > 0 ? $("#" + div_id).find("table")[0].id : "",
        ajax_url = e.currentTarget.attributes.data_url ? e.currentTarget.attributes.data_url.value : "",
        grid_headers = e.currentTarget.attributes.data_header ? JSON.parse(e.currentTarget.attributes.data_header.value) : "",
        isTab = $('.nav li.active .hidden-inline-mobile');

    if(table_id && ajax_url && grid_headers) {
        if (last_clicked_tab != e.currentTarget.id || second_condition) {
            var tab_id = table_id ? table_id.toLowerCase() : "";

            var isPtp = ptp_list.filter(function(list_val) {
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
            if(isPtp > 0) {
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
            } else if(isPmpWimax > 0) {
                if(window.location.href.search("customer_live") == -1 && window.location.href.search("customer_detail") == -1) {
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
            } else if(isOther > 0) {
                // For other case
                for (var i = 0; i < grid_headers.length; i++) {
                    var column = grid_headers[i],
                        condition1 = column.mData.indexOf("sector_id") > -1,
                        condition2 = column.mData.indexOf("circuit_id") > -1,
                        condition3 = column.mData.indexOf("customer_name") > -1;

                    if(condition1 || condition2 || condition3) {
                        if(column.bVisible) {
                            column.sClass = "hide";
                        } else {
                            column["sClass"] = "hide";
                        }
                    }
                }
            }

            var con1 = window.location.href.indexOf('alert_center/customer/device/') > -1,
                con2 = window.location.href.indexOf('alert_center/network/device/') > -1;
            // If single device alert page
            if(con1 || con2) {

                if(table_id == 'network_alert_service_table') {
                    service_name = 'service';
                } else if(table_id == 'network_alert_down_table') {
                    service_name = 'down';
                } else if(table_id == 'network_alert_packet_table') {
                    service_name = 'packet_drop';
                } else if(table_id == 'network_alert_latency_table') {
                    service_name = 'latency';
                } else {
                    service_name = 'ping';
                }

                ajax_url = ajax_url+'?service_name='+service_name;


                try {

                    if(isDateFilterApplied) {
                        ajax_url = ajax_url+'&start_date='+startDate+'&end_date='+endDate;
                    }
                    
                    var service_status_url = "";
                    if(service_name) {
                        if(current_device_id) {
                            service_status_url = "/performance/servicestatus/"+service_name+"/service_data_source/pl/device/"+current_device_id+"/";
                        }
                    }
                    // Call function to get service status
                    if (service_status_url) {
                        getPlServiceStatus(service_status_url);
                    }
                } catch(e) {
                    // console.log(e);
                }
            }

            /*Call createDataTable function to create the data table for specified dom element with given data*/
            dataTableInstance.createDataTable(table_id, grid_headers, ajax_url, destroy);
        }
    } else {
        /*Hide the spinner*/
        hideSpinner();
    }

    setTimeout(function() {
        // Update Breadcrumb
        $(".breadcrumb li:last-child").html('<a href="javascript:;"><strong>'+$('.nav li.active .hidden-inline-mobile').text()+'</strong></a>');
    },150);

    /*Save the last clicked tab id in global variable for condition checks*/
    last_clicked_tab = e.currentTarget.id;

    /*Refresh the tab after every given timer. Right now it is 5 minutes*/
    timeOutId = setTimeout(function () {
        $("#"+anchor_id).trigger('click', true);
    }, (+(timer) + "000"));
});