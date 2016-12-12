/**
 * This library handles the tab click event & load the data as per the selected tab.
 * @class alertOpenTab
 * @event click
 */

var last_clicked_tab = "",
    alertTabTimeoutId = "",
    tech_list = ['PMP',"P2P","WiMAX", "Backhaul"];

/*Initialize the timer in seconds.Right now its 1 year*/
/*86400 is 24 hrs miliseconds*/
// var timer = 86400 * 30 * 12; // 1 Year in seconds
var timer = 300; // 5 Minutes in seconds

$(".nav-tabs li a").click(function (e, isFirst) {
    // Update the breadcrumb as per clicked tab
    $(".breadcrumb li.active").html($.trim($(this).text()));

    var anchor_id = e.currentTarget.id,
        second_condition = "";

    if (isFirst) {
        second_condition = isFirst;
    } else {
        second_condition = false;
    }

    var destroy = false,
        div_id = e.currentTarget.href.split("#")[1],
        table_id = $("#" + div_id).find("table")[0].id,
        ajax_url = e.currentTarget.attributes.data_url.value,
        grid_headers = JSON.parse(e.currentTarget.attributes.data_header.value);

    if(table_id && ajax_url && grid_headers) {
        if(last_clicked_tab != e.currentTarget.id || second_condition) {
            if(table_id.toLowerCase().indexOf("p2p") > -1 || table_id.toLowerCase().indexOf("ptp") > -1) {
                for (var i = 0; i < grid_headers.length; i++) {
                    var column = grid_headers[i];
                    if (column.mData.indexOf("sector_id") > -1) {
                        if (column.sClass) {
                            column.sClass = "hide";
                        } else {
                            column["sClass"] = "hide";
                        }
                    }
                }
            }

            if(table_id.toLowerCase().indexOf("rad5") > -1) {
                for (var i = 0; i < grid_headers.length; i++) {
                    var column = grid_headers[i];
                    if (column.mData.indexOf("min_latency") > -1
                        ||
                        column.mData.indexOf("site_id") > -1
                        ||
                        column.mData.indexOf("dl_uas") > -1
                        ||
                        column.mData.indexOf("ul_uas") > -1 
                        ||
                        column.mData.indexOf("dl_utilization") > -1
                        ||
                        column.mData.indexOf("ul_utilization") > -1
                        ||
                        column.mData.indexOf("device_uptime") > -1){ 
                        if (!column.bVisible) {
                            column.bVisible = true;
                        } else {
                            column["bVisible"] = true;
                        }
                    }
                }
            }

            if(!tables_info[anchor_id]) {
                /*Call createDataTable function to create the data table for specified dom element with given data*/
                dataTableInstance.createDataTable(
                    table_id,
                    grid_headers,
                    ajax_url,
                    destroy
                );
            } else {
                if(tables_info[anchor_id]) {
                    var table_title = tables_info[anchor_id].table_title ? tables_info[anchor_id].table_title : false,
                        app_name = tables_info[anchor_id].app_name ? tables_info[anchor_id].app_name : false,
                        header_class_name = tables_info[anchor_id].header_class_name ? tables_info[anchor_id].header_class_name : false,
                        data_class_name = tables_info[anchor_id].data_class_name ? tables_info[anchor_id].data_class_name : false,
                        header_extra_param = tables_info[anchor_id].header_extra_param ? encodeURIComponent(tables_info[anchor_id].header_extra_param) : false,
                        data_extra_param = tables_info[anchor_id].data_extra_param ? encodeURIComponent(tables_info[anchor_id].data_extra_param) : false,
                        excluded_columns = tables_info[anchor_id].excluded ? encodeURIComponent(tables_info[anchor_id].excluded) : false;

                    // SET/RESET server side paging flag
                    if(tables_info[anchor_id].serverside_rendering != undefined) {
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
        // Hide Spinner(Loading)
        hideSpinner();
    }

    /*Save the last clicked tab id in global variable for condition checks*/
    last_clicked_tab = e.currentTarget.id;
});


/**
 * This function trigger given tab id click event after specific time
 * @method refreshAlertTab
 * @param tab_id {String}, It contains the dom id of tab
 * @param refresh_time {Number}, It contains the time to refresh tab in seconds
 */
function refreshAlertTab(tab_id, refresh_time) {

    /*Clear or Reset Time out*/
    try {
        clearTimeout(alertTabTimeoutId);
    } catch(e) {
        alertTabTimeoutId = '';
    }

    /*Refresh the tab after every given timer. Right now it is 5 minutes*/
    alertTabTimeoutId = setTimeout(function () {
        $("#" + tab_id).trigger('click', true);
    }, (+(refresh_time) + "000"));
}