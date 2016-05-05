/**
 * This library is used to show performance data of particular device in charts & tables
 * @class nocout.perf.lib
 * @uses Highcharts
 * @uses jquery Datatables
 * Coded By :- Yogender Purohit
 */

/*Global Variables*/
var perf_that = "",
    allDevices = "",
    device_status = "",
    device_services = "",
    tabs_click_counter = -1,
    single_service_data = "",
    getServiceDataUrl = "",
    chart_instance = "",
    old_table = "",
    base_url = "",
    timeInterval = "",
    live_data_tab = [
        {"id": "live", "title": "Live"}
    ],
    poll_now_tab = [
        { "id" : "live_poll_now", "title" : "On Demand Poll", disabled_url : true }
    ],
    tabs_with_historical = [
        {"id": "bihourly", "title": "Half-Hourly"},
        {"id": "hourly", "title": "Hourly"},
        {"id": "daily", "title": "Daily"},
        {"id": "weekly", "title": "Weekly"},
        {"id": "monthly", "title": "Monthly"},
        // {"id": "yearly", "title": "Yearly" }
    ],
    inventory_status_inner_inner_tabs = [
        {"id": "daily", "title": "Daily"},
        {"id": "weekly", "title": "Weekly"},
        {"id": "monthly", "title": "Monthly"},
        // {"id": "yearly", "title": "Yearly"}
    ],
    default_live_table_headers_without_ds = [
        {'mData': 'sys_timestamp', 'sTitle': 'Time', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'current_value', 'sTitle': 'Current Value', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'severity', 'sTitle': 'Severity', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'warning_threshold', 'sTitle': 'Warning Threshold', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'critical_threshold', 'sTitle': 'Critical Threshold', 'sWidth': 'auto', 'bSortable': true}
    ],
    default_live_table_headers_with_ds = [
        {'mData': 'sys_timestamp', 'sTitle': 'Time', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'data_source', 'sTitle': 'Data Source', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'current_value', 'sTitle': 'Current Value', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'severity', 'sTitle': 'Severity', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'warning_threshold', 'sTitle': 'Warning Threshold', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'critical_threshold', 'sTitle': 'Critical Threshold', 'sWidth': 'auto', 'bSortable': true},
    ]
    default_hist_table_headers_without_ds = [
        {'mData': 'sys_timestamp', 'sTitle': 'Time', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'avg_value', 'sTitle': 'Avg. Value', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'min_value', 'sTitle': 'Min. Value', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'max_value', 'sTitle': 'Max. Value', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'current_value', 'sTitle': 'Current Value', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'severity', 'sTitle': 'Severity', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'warning_threshold', 'sTitle': 'Warning Threshold', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'critical_threshold', 'sTitle': 'Critical Threshold', 'sWidth': 'auto', 'bSortable': true},
    ],
    default_hist_table_headers_with_ds = [
        {'mData': 'sys_timestamp', 'sTitle': 'Time', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'data_source', 'sTitle': 'Data Source', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'avg_value', 'sTitle': 'Avg. Value', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'min_value', 'sTitle': 'Min. Value', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'max_value', 'sTitle': 'Max. Value', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'current_value', 'sTitle': 'Current Value', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'severity', 'sTitle': 'Severity', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'warning_threshold', 'sTitle': 'Warning Threshold', 'sWidth': 'auto', 'bSortable': true},
        {'mData': 'critical_threshold', 'sTitle': 'Critical Threshold', 'sWidth': 'auto', 'bSortable': true},
    ],
    date_range_picker_html = "",
    spinner_html = '<h3 align="left"><i class="fa fa-spinner fa-spin" title="Fetching Current Status"></i></h3>',
    is_exact_url = false,
    pollCallingTimeout = "",
    remainingPollCalls = 0,
    pollingInterval = 10,
    pollingMaxInterval = 1,
    isPollingPaused = 0,
    isPerfCallStopped = 1,
    isPerfCallStarted = 0,
    poll_now_data_dict = {},
    last_active_tab = "",
    is_polling_active = false,
    non_polled_ids = ['rf'],
    perf_datatable_ids = {
        "chart" : "other_perf_table",
        "table" : "perf_data_table"
    };


/*Set the base url of application for ajax calls*/
if (window.location.origin) {
    base_url = window.location.origin;
} else {
    base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
}

// Daterangepicker HTML String
date_range_picker_html = '<input type="text" name="reservation" id="reservationtime" \
                          class="form-control input-large search-query" value="" readonly/>';

/**
 * This class(function) contains function to handle single device performance page functionality
 * @method nocoutPerfLib
 */
function nocoutPerfLib() {

    /*Save reference of current pointer to the global variable*/
    perf_that = this;

    /**
     * This function initializes daterange picker on given domElemet
     * @method initDateRangePicker
     * @param domElemet "String", It contains the dom element id on which the the date range picker is to be initialized.
     */
    this.initDateRangePicker = function(domElemet) {

        var saved_start_date = "",
            saved_end_date = "",
            oldStartDate = saved_start_date ? new Date(saved_start_date * 1000) : new Date(),
            oldENdData = saved_end_date ? new Date(saved_end_date * 1000) : new Date();

        startDate = saved_start_date ? new Date(saved_start_date * 1000) : "";
        endDate = saved_end_date ? new Date(saved_end_date * 1000) : "";

        $('#' + domElemet).daterangepicker({
            timePicker: true,
            timePickerIncrement: 1,
            opens: "right",
            showDropdowns: true,
            ranges: {
                'Today': [moment().startOf('day'), moment()],
                'Last 24 Hours': [moment().subtract('days', 1), moment()],
                'Last 7 Days': [moment().subtract('days', 6), moment()],
                'Last 30 Days': [moment().subtract('days', 29), moment()],
                'This Month': [moment().startOf('month'), moment().endOf('month')],
                'Last Month': [moment().subtract('month', 1).startOf('month'), moment().subtract('month', 1).endOf('month')]
            },
            buttonClasses: ['btn btn-sm'],
            applyClass: 'btn-default',
            cancelClass: 'btn-default',
            format: "DD-MM-YYYY HH:mm:ss",
            separator: ' to ',
            startDate: oldStartDate,
            endDate: oldENdData
        }, function (start, end) {
            startDate = start;
            endDate = end;
        });

        if (saved_start_date && saved_end_date) {
            $('#' + domElemet).val(moment(oldStartDate).format("DD-MM-YYYY HH:mm:ss") + '  to  ' + moment(oldENdData).format("DD-MM-YYYY HH:mm:ss"));
            startDate = moment(oldStartDate);
            endDate = moment(oldENdData);
        }
    };

    /**
     * This function Show/Hide tabs as per the page type
     * @method togglePerfPageElements
     * @param page_type "String", It contains the page type i.e either the page is of network, customer or other devices
     * @param technology "String", It contains current device technology
     */
    this.togglePerfPageElements = function(page_type, technology, device_type) {

        if (!device_type) {
            device_type = '';
        }
        
        if (!technology) {
            technology = '';
        }

        var condition_1 = page_type == 'customer' || technology.toLowerCase() == 'ptp' || technology.toLowerCase() == 'p2p' || device_type.toLowerCase() == 'radwin2kss',
            condition_2 = page_type == 'other',
            condition_3 = page_type == 'customer'; //&& device_type.toLowerCase() != 'radwin2kbs';
            
        // Show power tab only if page type = Customer 
        if (condition_3) {
            if ($("#power").hasClass("hide")) {
                $("#power").removeClass("hide");
            }

            if ($("#power_tab").hasClass("hide")) {
                $("#power_tab").removeClass("hide");
            }
        } else {
            if (!$("#power").hasClass("hide")) {
                $("#power").addClass("hide");
            }

            if (!$("#power_tab").hasClass("hide")) {
                $("#power_tab").addClass("hide");
            }
        }
        
        // Show/hide parent Tabs
        if (condition_1 || condition_2) {
            if (!$("#topology").hasClass("hide")) {
                $("#topology").addClass("hide");
            }

            if (!$("#topology_tab").hasClass("hide")) {
                $("#topology_tab").addClass("hide");
            }
        } else {
            
            if ($("#topology").hasClass("hide")) {
                $("#topology").removeClass("hide");
            }

            if ($("#topology_tab").hasClass("hide")) {
                $("#topology_tab").removeClass("hide");
            }
        }


        // Show/hide live polling button & chart container
        var live_poll_condition1 = ptp_tech_list.indexOf(technology) > -1,
            live_poll_condition2 = page_type == 'customer';

        if (!live_poll_condition1 && !live_poll_condition2) {
            $(".single_perf_poll_now, #perf_live_poll_input, #perf_live_poll_chart").addClass("hide");
        }

    };

    /**
     * This function fetch the status of current device
     * @method getStatus
     * @param get_status_url "String", It contains the url to fetch the status of current device.
     * @param device_id "INT", It contains the ID of current device.
     */
    this.getStatus = function (get_status_url, device_id) {

        /*Ajax call to Get Devices API*/
        var get_url = get_status_url;
        $.ajax({
            url: get_url,
            type: "GET",
            dataType: "json",
            success: function (response) {

                var result = "";
                // Type check of response
                if (typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }

                if (result.success == 1) {

                    device_status = result.data.objects;

                    var device_inventory_status = result.data.objects,
                        complete_headers_html = "",
                        complete_rows_html = "";

                    // If it is single device page for other devices then hide utilization tab
                    if (device_inventory_status.is_others_page) {
                        if (!$("#utilization_top").hasClass("hide")) {
                            $("#utilization_top").addClass("hide");
                        }

                        if (!$("#utilization_top_tab").hasClass("hide")) {
                            $("#utilization_top_tab").addClass("hide");
                        }
                    }
                    // Loop to populated table headers & data
                    for (var i=0;i<device_inventory_status.length;i++) {
                        var header_row_string = "",
                            data_row_string = "",
                            inner_rows = device_inventory_status[i];

                        for (var j=0;j<inner_rows.length;j++) {
                            var link_html = '';

                            if (i === 0) {
                                header_row_string += "<th class='vAlign_middle'>"+inner_rows[j].title+"</th>";
                            }

                            if (inner_rows[j].url) {
                                var row_val = inner_rows[j].value,
                                    class_attr = '';
                                // Highlight the text in case of DR device
                                if (row_val.indexOf('(DR)') > -1) {
                                    class_attr = "class='"+bold_class+"'";
                                }

                                link_html = "<a href = '"+inner_rows[j].url+"' "+class_attr+" target='_blank'>"+row_val+"</a>";
                            } else {
                                link_html = inner_rows[j].value;
                            }

                            data_row_string += "<td class='vAlign_middle'>"+link_html+"</td>";
                        }

                        if(header_row_string && i == 0) {
                            complete_headers_html = "<tr>"+header_row_string+"</tr>";
                        }

                        complete_rows_html += "<tr>"+data_row_string+"</tr>";
                    }

                    /*Populate table headers*/
                    $("#status_table thead").html(complete_headers_html);
                    $("#status_table tbody").html(complete_rows_html);

                } else {
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: 'Performance',
                        // (string | mandatory) the text inside the notification
                        text: result.message,
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: false
                    });
                }
            },
            error: function (err) {

                $("#status_table tbody").html(err.statusText);

                $.gritter.add({
                    // (string | mandatory) the heading of the notification
                    title: 'Performance',
                    // (string | mandatory) the text inside the notification
                    text: err.statusText,
                    // (bool | optional) if you want it to fade out on its own or just sit there
                    sticky: false
                });

            }
        });
    };

    /**
     * This function make HTML for LI element of TAB
     * @method make_tab_li_html
     * @param tab_config "{Object}", It contains the configuration for creating tab html
     * @return li_html {String}, It contains the required HTML string
     */
    this.make_tab_li_html = function(tab_config) {
        var li_html = "";

        if (!tab_config || $.isEmptyObject(tab_config)) {
            return li_html;
        }

        var active_class = tab_config.active_class ? tab_config.active_class : "",
            unique_key = tab_config.unique_key ? tab_config.unique_key : "",
            content_href = unique_key ? unique_key + "_block" : "",
            id = unique_key ? unique_key + "_tab" : "",
            api_url = tab_config.api_url ? tab_config.api_url : "",
            title = tab_config.title ? tab_config.title : "",
            icon_class = tab_config.icon_class ? tab_config.icon_class : "";

        li_html = '<li class="' + active_class+ '"><a href="#' + content_href+ '" \
                   url="' + api_url+ '" id="' + id+ '" data-toggle="tab">\
                   <i class="' + icon_class+ '">&nbsp;</i>' + title+ '\
                   </a></li>';

        return li_html;
    };

    /**
     * This function make HTML for TAB content
     * @method make_tab_content_html
     * @param tab_content_config {Object}, It contains the configuration for creating tab content html
     * @return content_html {String}, It contains the required HTML string
     */
    this.make_tab_content_html = function(tab_content_config) {
        var content_html = "";

        if (!tab_content_config || $.isEmptyObject(tab_content_config)) {
            return content_html;
        }

        var active_class = tab_content_config.active_class ? tab_content_config.active_class : "",
            unique_key = tab_content_config.unique_key ? tab_content_config.unique_key : "",
            id = unique_key ? unique_key + "_block" : "",
            show_last_updated = tab_content_config.show_last_updated != 'undefined' ? tab_content_config.show_last_updated : true,
            last_updated_id = unique_key ? "last_updated_" + unique_key + "_block" : "",
            chart_id = unique_key ? unique_key + "_chart" : "",
            bottom_table_id = unique_key ? unique_key + "_bottom_table" : "",
            legends_block_id = unique_key ? unique_key + "_legends_block" : "";


        content_html += '<div class="tab-pane ' + active_class+ '" id="' + id+ '">';

        if (show_last_updated) {
            content_html += '<div align="center" class="last_updated_container" id="' + last_updated_id+ '">\
                            <h3 align="left"><i class="fa fa-spinner fa-spin" title="Fetching Current Status"></i></h3>\
                            </div>';
        }
        if (tab_content_config.tab_id == 'live_poll_now') {
            content_html += '<div class="col-md-1">\
                                <button class="btn btn-default btn-sm single_perf_poll_now " title="Poll Now" \
                                data-complete-text="<i class=\'fa fa-flash\'></i>" data-loading-text="<i class=\'fa fa-spinner fa fa-spin\'> </i>">\
                                <i class="fa fa-flash"></i></button>\
                            </div>\
                            <div class="col-md-2" align="center" style="padding-top:4px;">\
                            <strong>OR</strong> \
                            </div>\
                            <div class="col-md-9 row">\
                            <div class="col-md-4">\
                                <select name="poll_interval" class="form-control input-sm poll_interval">\
                                <option value="">Select Poll Interval</option>\
                                <option value="10">10 Seconds</option>\
                                <option value="20">20 Seconds</option>\
                                <option value="30">30 Seconds</option>\
                                <option value="40">40 Seconds</option>\
                                <option value="50">50 Seconds</option>\
                                <option value="60">60 Seconds</option>\
                                </select>\
                            </div>\
                            <div class="col-md-4">\
                                <select name="poll_maxInterval" class="form-control input-sm poll_maxInterval">\
                                <option value="">Select Maximum Interval</option>\
                                <option value="1">1 Minute</option>\
                                <option value="2">2 Minute</option>\
                                <option value="3">3 Minute</option>\
                                <option value="4">4 Minute</option>\
                                </select>\
                            </div>\
                            <div class="col-md-4">\
                                <button class="btn btn-default btn-sm play_pause_btns poll_play_btn" \
                                    data-complete-text="<i class=\'fa fa-play text-success\'> </i>" \
                                    data-loading-text="<i class=\'fa fa-spinner fa-spin\'> </i>" title="Play" >\
                                    <i class="fa fa-play text-success"> </i>\
                                </button>\
                                <button class="btn btn-default btn-sm play_pause_btns poll_pause_btn" \
                                    data-complete-text="<i class=\'fa fa-pause text-warning\'> </i>" \
                                    data-loading-text="<i class=\'fa fa-spinner fa-spin\'> </i>" title="Pause" >\
                                    <i class="fa fa-pause text-warning"> </i>\
                                </button>\
                                <button class="btn btn-default btn-sm play_pause_btns poll_stop_btn" \
                                    data-complete-text="<i class\'fa fa-stop text-danger\'> </i>" \
                                    data-loading-text="<i class=\'fa fa-spinner fa-spin\'> </i>" title="Stop" >\
                                    <i class="fa fa-stop text-danger"> </i>\
                                </button>\
                                <div align="right" class="pull-right"> \
                                    <button class="btn btn-default btn-sm play_pause_btns reset_live_polling" title="Clear all polled data"> \
                                        <i class="fa fa-trash-o text-danger"></i> \
                                    </button> \
                                </div> \
                            </div>\
                            <div class="clearfix"></div></div>\
                            <div class="clearfix"></div><div class="divide-20"></div>';

            content_html += '<div class="chart_container">\
                            <div id="' + chart_id+ '" style="width:100%;"></div>\
                            <div id="' + legends_block_id+ '" class="custom_legends_container hide"> \
                            <div class="custom_legends_block"></div><div class="clearfix"></div> \
                            </div> \
                            <div id="' + bottom_table_id+ '"></div></div></div>';
        } else if (tab_content_config.unique_key.indexOf('power_content') > -1) {
            content_html += '<div class="chart_container">\
                            <div id="' + chart_id+ '" style="width:100%;">\
                            <h3><i class="fa fa-spinner fa-spin"></i></h3></div>\
                            <button title="Power Status" class="btn btn-default power-actions" id="power_send_status" data-button-respone="status" \
                                data-complete-text="<i class=\'fa fa-circle\'></i> Power Status" \
                                data-loading-text="<i class=\'fa fa-spinner fa-spin\'></i> Sending..."> <i class="fa fa-circle"></i> Power Status\
                            </button>\
                            <button title="Power Reboot" class="btn btn-default power-actions" id="power_send_reset" data-button-respone="reset" \
                                data-complete-text="<i class=\'fa fa-refresh\'></i> Power Reboot" \
                                data-loading-text="<i class=\'fa fa-spinner fa-spin\'></i> Sending..."> <i class="fa fa-refresh"></i> Power Reboot\
                            </button>\
                            <button title="JOJI" class="btn btn-default power-actions" id="power_send_joji" data-button-respone="joji" \
                                data-complete-text="<i class=\'fa fa-plug\'></i> JOJI" \
                                data-loading-text="<i class=\'fa fa-spinner fa-spin\'></i> Sending..."> <i class="fa fa-plug"></i> JOJI\
                            </button>\
                            {0}\
                            <div class="clearfix"></div>\
                            <div class="divide-20"></div>\
                            <table id="power_msg_listing" class="datatable table table-striped table-bordered table-hover"> \
                                <thead></thead> \
                                <tbody></tbody> \
                            </table> \
                            <div id="' + legends_block_id+ '" class="custom_legends_container hide"> \
                            </div></div></div>';
            
            var reboot_btn_html = '';
            if (enable_reboot_btn) {
                reboot_btn_html = '<button title="Soft Reboot" class="btn btn-default power-actions" \
                                       id="power_send_reboot" data-button-respone="reboot" \
                                       data-complete-text="<i class=\'fa fa-refresh\'></i> Soft Reboot" \
                                       data-loading-text="<i class=\'fa fa-spinner fa-spin\'> \
                                       </i> Please Wait..."> <i class="fa fa-refresh"></i> Soft Reboot\
                                       </button>';
            }
            content_html = content_html.replace('{0}', reboot_btn_html);
        } else {
            content_html += '<div class="chart_container">\
                            <div id="' + chart_id+ '" style="width:100%;">\
                            <h3><i class="fa fa-spinner fa-spin"></i></h3></div>\
                            <div id="' + legends_block_id+ '" class="custom_legends_container hide"> \
                            <div class="custom_legends_block"></div><div class="clearfix"></div> \
                            </div> \
                            <div id="' + bottom_table_id+ '"></div></div></div>';
        }

        return content_html;
    };

    /**
     * This function fetch the list of services
     * @method getServices
     * @param get_service_url "String", It contains the url to fetch the services.
     * @param device_id "INT", It contains the ID of current device.
     */
    this.getServices = function (get_service_url, device_id) {

        /*Show the spinner*/
        // showSpinner();

        var active_tab_id = "",
            active_tab_url = "",
            active_tab_content_dom_id = "";

        /*Ajax call to Get Devices API*/
        var get_url = get_service_url;
        $.ajax({
            url: get_url,
            type: "GET",
            dataType: "json",
            success: function (response) {
                
                var result = "";
                // Type check of response
                if (typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }

                if (result.success == 1) {
                    all_services_list = [];
                    try {
                        all_services_list = result.data.meta.services_list;
                    } catch(e) {
                        all_services_list = [];
                    }
                    $('#all_serv_live_report_btn').attr('data-services', JSON.stringify(all_services_list));

                    var first_loop = 0;
                    // If any data exists
                    if (result.data.objects && !$.isEmptyObject(result.data.objects)) {
                        /*Loop to get services from object*/
                        for(service_key in result.data.objects) {

                            var tab_id = service_key.split("_tab")[0];
                            // If dom element exists
                            if ($("#" + service_key).length > 0 && $("#" + tab_id).length > 0) {
                                // Reset Variables
                                device_services = "";
                                tabs_with_data = "";

                                if ($("#" + service_key).hasClass("active")) {
                                    $("#" + service_key).removeClass("active");
                                }

                                if ($("#" + tab_id).parent("li").hasClass("active")) {
                                    $("#" + tab_id).parent("li").removeClass("active");
                                }

                                device_services = result.data.objects[service_key].info;
                                if (device_services && device_services.length > 0) {
                                    var tabs_hidden_class = "";
                                    
                                    if (device_services.length == 1 && tab_id.indexOf('custom_dashboard') == -1) {
                                        tabs_hidden_class = "hide";
                                    }

                                    var count = 0,
                                        tabs_with_data = "",
                                        service_tabs_data = '<div class="tab-content" style="overflow:auto;">',
                                        service_tabs = '<ul class="left_tabs_container nav nav-tabs ' + tabs_hidden_class+ '">';

                                    var is_first_tab = 0;
                                    if (result.data.objects[service_key].isActive == 1) {
                                        is_first_tab = 1;
                                        $("#" + tab_id).parent("li").addClass("active");
                                        $("#" + service_key).addClass("active");
                                    }
                                    
                                    $.each(device_services, function (key, value) {
                                        var sds_key = value.sds_key ? value.sds_key : '',
                                            unique_item_key = service_key+ '_' + String(count)+ '_' + String(i),
                                            active_class = '';

                                        if (is_first_tab == 1 && count == 0) {
                                            // Save the active tab data in global variables
                                            active_tab_id = unique_item_key;
                                            active_tab_content_dom_id = unique_item_key+ '_block';
                                            active_tab_url = "/" + value.url;

                                            // add 'active' class for active i.e first tab
                                            active_class = 'active';
                                        }

                                        var show_last_updated = true;

                                        if (unique_item_key.indexOf('custom_dashboard') > -1) {
                                            show_last_updated = false;
                                        }

                                        var tab_info_obj = {
                                                'active_class' : active_class,
                                                'unique_key' : unique_item_key,
                                                'icon_class' : 'fa ' + default_left_tab_icon,
                                                'api_url' : value.url,
                                                'title' : value.title
                                            },
                                            content_info_obj = {
                                                'active_class' : active_class,
                                                'unique_key' : unique_item_key,
                                                'show_last_updated' : show_last_updated,
                                            };

                                        // Create Tab HTML
                                        service_tabs += perf_that.make_tab_li_html(tab_info_obj);

                                        var all_tabs_condition_1 = unique_item_key.indexOf('availability') == -1,
                                            all_tabs_condition_2 = unique_item_key.indexOf('topology') == -1,
                                            all_tabs_condition_3 = unique_item_key.indexOf('utilization') == -1,
                                            all_tabs_condition_4 = unique_item_key.indexOf('power_content') == -1,
                                            inner_inner_tabs = [],
                                            inner_tab_ids = [];

                                        // Create tab content HTML
                                        if ((show_historical_on_performance && all_tabs_condition_1 && all_tabs_condition_2 && all_tabs_condition_3 && all_tabs_condition_4) || is_perf_polling_enabled) {

                                            if(all_tabs_condition_1 && all_tabs_condition_2 && all_tabs_condition_3 && all_tabs_condition_4) {
                                                
                                                service_tabs_data += '<div class="tab-pane ' + active_class+ '" id="' + unique_item_key+ '_block">';
                                                if (show_last_updated) {
                                                    service_tabs_data += '<div align="center" class="last_updated_container" id="last_updated_' + unique_item_key+ '_block">\
                                                                      <h3 align="left"><i class="fa fa-spinner fa-spin" title="Fetching Current Status"></i></h3>\
                                                                      </div>';
                                                }

                                                service_tabs_data += '<div class="tabbable"><ul class="nav nav-tabs inner_inner_tab">';

                                                if(show_historical_on_performance) {
                                                    inner_inner_tabs = inner_inner_tabs.concat(live_data_tab);
                                                    if(unique_item_key.indexOf('_status') == -1) {
                                                        inner_inner_tabs = inner_inner_tabs.concat(tabs_with_historical);
                                                    }
                                                }

                                                if (show_historical_on_performance && unique_item_key.indexOf('_status') > -1) {
                                                    // inner_inner_tabs = inventory_status_inner_inner_tabs;
                                                    inner_inner_tabs = inner_inner_tabs.concat(inventory_status_inner_inner_tabs);
                                                }

                                                // If poll now flag enabled
                                                if(is_perf_polling_enabled) {
                                                    if (non_poll_sds.indexOf(sds_key) == -1) {
                                                        // Append poll now  & live tab
                                                        if(!inner_inner_tabs.length) {
                                                            inner_inner_tabs = inner_inner_tabs.concat(live_data_tab);
                                                        }
                                                        if(non_polled_ids.indexOf(value["name"]) == -1) {
                                                            inner_inner_tabs = inner_inner_tabs.concat(poll_now_tab);
                                                        }
                                                    }
                                                }
                                                

                                                // CREATE SUB INNER TAB HTML
                                                if (inner_inner_tabs && inner_inner_tabs.length > 0) {

                                                    for(var x=0;x<inner_inner_tabs.length;x++) {
                                                        var inner_active_class = '';
                                                        if (x == 0) {
                                                            inner_active_class = 'active';
                                                        }
                                                        var current_item = inner_inner_tabs[x],
                                                            id = current_item.id,
                                                            title = current_item.title,
                                                            data_url = "";

                                                        if (!current_item["disabled_url"]) {
                                                            if (value.url.indexOf('?') == -1) {
                                                                data_url = value.url + "?data_for=" + id        
                                                            } else {
                                                                data_url = value.url + "&data_for=" + id
                                                            }
                                                        }


                                                        var inner_tab_info_obj = {
                                                                'active_class' : inner_active_class,
                                                                'unique_key' : id + "_" + unique_item_key,
                                                                'icon_class' : 'fa fa-clock-o',
                                                                'api_url' : data_url,
                                                                'title' : title
                                                            };

                                                        if(!poll_now_data_dict[inner_tab_info_obj["unique_key"]]) {
                                                            poll_now_data_dict[inner_tab_info_obj["unique_key"]] = [];
                                                        }
                                                        
                                                        service_tabs_data += perf_that.make_tab_li_html(inner_tab_info_obj);
                                                        if (inner_tab_ids.indexOf(id) == -1) {
                                                            inner_tab_ids.push(id);
                                                        }
                                                    }

                                                } else {
                                                    var inner_tab_info_obj = {
                                                        'active_class' : 'active',
                                                        'unique_key' : "live_" + unique_item_key,
                                                        'icon_class' : 'fa fa-caret-right',
                                                        'api_url' : value.url + "?data_for=live",
                                                        'title' : "Live"
                                                    };
                                                    service_tabs_data += perf_that.make_tab_li_html(inner_tab_info_obj);
                                                    inner_tab_ids.push('live');
                                                }
                                                service_tabs_data += '</ul><div class="divide-20"></div><div class="tab-content">';
                                                // CREATE SUB INNER TAB CONTENT HTML
                                                for(var y=0;y<inner_tab_ids.length;y++) {
                                                    var current_key = inner_tab_ids[y],
                                                        inner_content_info_obj = {
                                                            'tab_id' : current_key,
                                                            'active_class' : '',
                                                            'unique_key' : current_key + "_" + unique_item_key,
                                                            'show_last_updated' : false
                                                        };
                                                    if (y==0) {
                                                        inner_content_info_obj['active_class'] = 'active';
                                                    }
                                                    service_tabs_data += perf_that.make_tab_content_html(inner_content_info_obj);
                                                }
                                                service_tabs_data += '</div></div><div class="clearfix"></div></div>';
                                            } else {
                                                service_tabs_data += perf_that.make_tab_content_html(content_info_obj);
                                            }
                                        } else {
                                            service_tabs_data += perf_that.make_tab_content_html(content_info_obj);
                                        }

                                        // Increment the counter
                                        count++;
                                    });

                                    service_tabs += '</ul>';
                                    // service_tabs_data += '</div>';
                                    tabs_with_data = service_tabs + " " + service_tabs_data;
                                } else {
                                    if (!$("#" + tab_id).hasClass("hide") && tab_id.indexOf('custom_dashboard') == -1) {
                                        $("#" + tab_id).addClass("hide");
                                    }
                                }

                                $("#" + service_key + " .inner_tab_container .panel-body .tabs-left").html(tabs_with_data);
                            }
                        }

                        /*Bind click event on tabs*/
                        $('.inner_tab_container .panel-body .tabs-left').delegate('ul.nav-tabs > li > a', 'click', function (e) {
                            // show loading spinner
                            // showSpinner();
                            var current_target = e.currentTarget,
                                current_attr = current_target.attributes,
                                serviceId = current_target.id.slice(0, -4),
                                splitted_local_id = current_attr.href.value.split("#"),
                                tab_content_dom_id = splitted_local_id.length > 1 ? splitted_local_id[1] : splitted_local_id[0];
                            
                            //@TODO: all the ursl must end with a / - django style
                            var service_data_url_val = current_attr.url ? $.trim(current_attr.url.value) : "";
                                serviceDataUrl = "";

                            if(serviceId.indexOf('_status_') == -1 || serviceId.indexOf('_inventory_') == -1) {
                                if ($('.top_perf_tabs > li.active a').attr('id').indexOf('bird') == -1) {
                                    // Hide display type option from only table tabs
                                    if ($("#display_type_container").hasClass("hide")) {
                                        $("#display_type_container").removeClass("hide")
                                    }
                                }
                            }

                            if (service_data_url_val) {
                                if (service_data_url_val[0] != "/") {
                                    serviceDataUrl = "/" + service_data_url_val;
                                } else {
                                    serviceDataUrl = service_data_url_val;
                                }
                            }

                            if ($("#last_updated_" + tab_content_dom_id).length > 0) {
                                perf_that.resetLivePolling(tab_content_dom_id);
                                // add 'only_service' param to querystring if unified view
                                var view_type = $.trim($('input[name="service_view_type"]:checked').val());
                                if (view_type == 'unified') {
                                    if (serviceDataUrl.indexOf('?') > -1) {
                                        serviceDataUrl += '&only_service=1';
                                    } else {
                                        serviceDataUrl += '?only_service=1';
                                    }
                                }
                                // get the service status for that service
                                perfInstance.getServiceStatus(serviceDataUrl, is_exact_url, function(response_type,data_obj) {
                                    if (response_type == 'success') {
                                        // Call function to populate latest status for this service
                                        populateServiceStatus_nocout("last_updated_" + tab_content_dom_id,data_obj);
                                    } else {
                                        $("#last_updated_" + tab_content_dom_id).html("");
                                    }
                                });
                            }

                            if (
                                (
                                    !show_historical_on_performance
                                    &&
                                    !is_perf_polling_enabled
                                )
                                ||
                                serviceId.indexOf('availability') > -1
                                ||
                                serviceId.indexOf('utilization_top') > -1
                                ||
                                serviceId.indexOf('topology') > -1
                                ||
                                serviceId.indexOf('power_content') > -1
                            ) {
                                perfInstance.initGetServiceData(serviceDataUrl, serviceId, current_device);
                            }
                        });
                    }
                } else {
                    $(".inner_tab_container").html("<p>" + result.message + "</p>");
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: 'Performance',
                        // (string | mandatory) the text inside the notification
                        text: result.message,
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: false
                    });
                }

                /*Hide the spinner*/
                // hideSpinner();

            },
            error: function (err) {

                $(".inner_tab_container").html(err.statusText);

                /*Hide the spinner*/
                // hideSpinner();
            },
            complete: function () {
                if (active_tab_url && active_tab_id) {
                    // remove the 'active_left_tab_icon' class from all link (if exists)
                    $('.left_tabs_container li a i').removeClass(active_left_tab_icon);
                    //  Add 'default_left_tab_icon' class to active link
                    $('.left_tabs_container li a i').addClass(default_left_tab_icon);
                    //  Add 'active_left_tab_icon' class to active link
                    $('#' + active_tab_id + '_tab i').addClass(active_left_tab_icon);
                    //  Remove 'default_left_tab_icon' class to active link
                    $('#' + active_tab_id + '_tab i').removeClass(default_left_tab_icon);

                    /*Reset Variables & counters */
                    clearTimeout(timeInterval);
                    nocout_destroyDataTable('other_perf_table');
                    nocout_destroyDataTable('perf_data_table');

                    perf_that.resetLivePolling(active_tab_content_dom_id);
                    /*Get Last opened tab id from cookie*/
                    var parent_tab_id = $.cookie('parent_tab_id');
                    
                    if(is_util_tab) {
                        parent_tab_id = 'utilization_top'
                    }

                    //If parent Tab id is there & parent tab element exist in the dom.
                    if (parent_tab_id && $('#' + parent_tab_id).length && $('#' + parent_tab_id)[0].className.indexOf('hide') == -1) {
                        $('#' + parent_tab_id).trigger('click');
                    } else {
                        // show loading spinner
                        // showSpinner();
                        if ($("#last_updated_" + active_tab_content_dom_id).length > 0) {
                            // add 'only_service' param to querystring if unified view
                            var view_type = $.trim($('input[name="service_view_type"]:checked').val());
                            if (view_type == 'unified') {
                                if (active_tab_url.indexOf('?') > -1) {
                                    active_tab_url += '&only_service=1';
                                } else {
                                    active_tab_url += '?only_service=1';
                                }
                            }
                            perfInstance.getServiceStatus(active_tab_url, is_exact_url, function(response_type,data_obj) {
                                if (response_type == 'success') {
                                    // Call function to populate latest status for this service
                                    populateServiceStatus_nocout("last_updated_" + active_tab_content_dom_id,data_obj);
                                } else {
                                    $("#last_updated_" + active_tab_content_dom_id).html("");
                                }
                            });
                        }

                        if (show_historical_on_performance || is_perf_polling_enabled) {
                            $("#live_" + active_tab_id + "_tab").trigger('click');
                        } else {
                            /*Call getServiceData function to fetch the data for currently active service*/
                            perf_that.getServiceData(active_tab_url, active_tab_id, device_id);
                        }
                    }
                }
            }
        });
    };

    /**
     * This function get the service status for given url
     * @method getServiceStatus
     * @param service_status_url "String", It contains the url to fetch the status of current device.
     * @param is_exact_url "Boolean", It contains the flag that either the url is exact or we have to update it.
     * @callback Back to the called function.
     */
    this.getServiceStatus = function(service_status_url, is_exact_url, callback) {

        if(!is_exact_url) {
            
            if (service_status_url.indexOf('?') == -1) {
                var splitted_status_url = service_status_url.split("/"),
                    updated_url = splitted_status_url[splitted_status_url.length -1] != "" ? service_status_url + "/" : service_status_url,
                    device_id = splitted_status_url[splitted_status_url.length -1] != "" ? splitted_status_url[splitted_status_url.length -1] : splitted_status_url[splitted_status_url.length -2];
            } else {
                var splitted_status_url = service_status_url.split('?')[0].split("/");
                var updated_url = splitted_status_url[splitted_status_url.length -1] != "" ? service_status_url.split('?')[0] + "/" + "?" + service_status_url.split('?')[1] : service_status_url,
                    device_id = splitted_status_url[splitted_status_url.length -1] != "" ? splitted_status_url[splitted_status_url.length -1] : splitted_status_url[splitted_status_url.length -2];
            }

            if (updated_url.indexOf("/servicedetail/") > -1) {
                if (updated_url.indexOf("rssi") > -1) {
                    updated_url = "/performance/servicestatus/rssi/service_data_source/rssi/device/" + device_id + "/";
                } else if (updated_url.indexOf("util") > -1) {
                    updated_url = "/performance/servicestatus/utilization/service_data_source/utilization/device/" + device_id + "/";
                }
            } else if (updated_url.indexOf('/powerlisting/') > -1) {
                updated_url = updated_url.replace("/powerlisting/","/powerstatus/");
            } else {
                // Replace 'service' with 'servicestatus'
                updated_url = updated_url.replace("/service/","/servicestatus/");
            }
        } else {
            updated_url = service_status_url;
        }

        if (updated_url[0] != '/') {
            updated_url = '/' + updated_url;
        }

        $.ajax({
            url : base_url + "" + updated_url,
            type : "GET",
            success : function(response) {
                var result = "",
                    last_updated = "",
                    perf = "",
                    status = "";

                // Type check of response
                if (typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }
                if (result.success) {
                    if (result.data && result.data.objects) {
                        // Call function to populate latest status info
                        populateDeviceStatus_nocout("latestStatusContainer",result.data.objects);

                        last_updated = result.data.objects.last_updated ? result.data.objects.last_updated : "";
                        perf = result.data.objects.perf ? result.data.objects.perf : "";
                        status = result.data.objects.status ? result.data.objects.status : "";

                        var response_obj = {
                            "last_updated" : last_updated,
                            "perf" : perf,
                            "status" : status
                        };

                        callback("success",result.data.objects);
                    } else {
                        callback("error","");
                    }
                } else {
                    callback("error","");
                }
            },
            error : function(err) {
                $.gritter.add({
                    // (string | mandatory) the heading of the notification
                    title: 'Performance - Service Status',
                    // (string | mandatory) the text inside the notification
                    text: err.statusText,
                    // (bool | optional) if you want it to fade out on its own or just sit there
                    sticky: false
                });
                callback("error","");
            }
        });
    };

    /**
     * This function fetches data regarding particular service
     * @method getServiceData
     * @param get_service_data_url "String", It contains the url to fetch the status of current device.
     * @param service_id "String", It contains unique name for service.
     * @param device_id "INT", It contains the ID of current device.
     */
    this.getServiceData = function (get_service_data_url, service_id, device_id) {

        // If call from "Power tab then initialize datatable & return"
        if (get_service_data_url.indexOf('/powerlisting/') > -1) {
            dataTableInstance.createDataTable(power_table_id, power_listing_headers, power_ajax_url, false);
            return true;
        }

        // Hide custom legends block if exists
        if(!$('#' + service_id + '_legends_block').hasClass('hide')) {
            $('#' + service_id + '_legends_block').addClass('hide');
        }

        if (!get_service_data_url || (service_id.indexOf('live_poll_now') > -1 && get_service_data_url.indexOf('live_poll_now') > -1)) {
            if(service_id.indexOf('live_poll_now') > -1 && get_service_data_url.indexOf('live_poll_now') > -1) {
                perf_that.resetLivePolling(service_id);
            }
            return true;
        }
        
        if (get_service_data_url[0] != '/') {
            get_service_data_url = "/" + get_service_data_url;
        }

        var draw_type = $("input[name='item_type']:checked").val(),
            listing_ajax_url = "",
            listing_headers = default_live_table_headers,
            is_birdeye_view = clicked_tab_id.indexOf('bird') > -1 || $('.top_perf_tabs > li.active a').attr('id').indexOf('bird') > -1,
            is_custom_view = clicked_tab_id.indexOf('custom') > -1 || $('.top_perf_tabs > li.active a').attr('id').indexOf('custom') > -1;

        if (!draw_type || clicked_tab_id.indexOf('bird') > -1 || clicked_tab_id.indexOf('custom_dashboard') > -1) {
            draw_type = "chart";
        }

        // If birdeye view then show header with DS
        if (clicked_tab_id.indexOf('bird') > -1) {
            listing_headers = default_live_table_headers_with_ds;
        }

        // Decrement the tabs click on evert click counter
        tabs_click_counter--;

        $.cookie('activeTabId', service_id + "_tab", {path: '/'});

        var start_date = "",
            end_date = "",
            get_url = "",
            get_param_start_date = "", 
            get_param_end_date = "";

        // Show loading spinner
        showSpinner();

        // URL to fetch chart data
        get_url = base_url + "" + get_service_data_url;

        // Reset global variables
        start_date = "";
        end_date = "";

        if (startDate && endDate && clicked_tab_id.indexOf('bird') == -1) {
            
            var myStartDate = startDate.toDate(),
                myEndDate = endDate.toDate();

            start_date = myStartDate.getTime(),
            end_date = myEndDate.getTime();

            try {
                if ($("#" + service_id + "_chart").highcharts()) {
                    var chart = $("#" + service_id + "_chart").highcharts(),
                        chart_series = chart.series;

                    if (chart_series && chart_series.length > 0) {
                        // Remove series from highchart
                        while(chart_series.length > 0) {
                            chart_series[0].remove(true);
                        }
                    }
                    // Destroy highchart
                    $("#" + service_id + "_chart").highcharts().destroy();
                }

                if ($("#" + service_id + "_bottom_table").length) {
                    $("#" + service_id + "_bottom_table").html("");
                }

                get_param_start_date = getDateInEpochFormat(start_date);
                get_param_end_date = getDateInEpochFormat(end_date)

            } catch(e) {
                // console.log(e);
            }
        } else {
            start_date = '';
            end_date = '';
        }

        if (get_service_data_url.indexOf("?") > -1) {
            listing_ajax_url = get_service_data_url + "&start_date=" + get_param_start_date + "&end_date=" + get_param_end_date;
        } else {
            listing_ajax_url = get_service_data_url + "?start_date=" + get_param_start_date + "&end_date=" + get_param_end_date;
        }

        try {
            var not_live_tab = listing_ajax_url.split("data_for=")[1].indexOf('live') == -1

            // If historical tab then update table_headers variable
            if ((show_historical_on_performance && not_live_tab) || (listing_ajax_url.indexOf('/rta/') > -1)) {
                listing_headers = default_hist_table_headers;
            }
        } catch(e) {
            // console.log(e);
        }

        if(listing_ajax_url.indexOf("_invent") > -1 || listing_ajax_url.indexOf("_status") > -1) {
            if (clicked_tab_id.indexOf('bird') == -1 || clicked_tab_id.indexOf('custom') == -1) {
                // Hide display type option from only table tabs
                if (!$("#display_type_container").hasClass("hide")) {
                    $("#display_type_container").addClass("hide")
                }
                
                draw_type = 'table';
                // Update radio button selection
                $('#display_table').attr('checked', 'checked');
                $('#display_table').prop('checked', true);

                // Update dropdown button html
                updateDropdownHtml();
            }

            $('#' + service_id+ '_chart').html("");

            initChartDataTable_nocout(
                "other_perf_table",
                listing_headers,
                service_id,
                listing_ajax_url,
                true
            );
        } else {
            // Send ajax call
            sendAjax(start_date, end_date);
        }

        // This function returns date object as per given date string
        function getDate(date) {
            var dateSplittedString = date.split('-');
            return new Date(dateSplittedString[2], (parseInt(dateSplittedString[1], 10) - 1), dateSplittedString[0]);
        }

        // This function returns next date as per given date
        function getTomorrowDate(date) {
            var tomorowDate = new Date(date);
            tomorowDate.setFullYear(date.getFullYear());
            tomorowDate.setMonth(date.getMonth());
            tomorowDate.setDate(date.getDate() + 1);
            return tomorowDate;
        }

        // This function return given date in DD-mm-YYYY format
        function getDateinStringFormat(date) {
            if (date) {
                return date.getDate() + "-" + (parseInt(date.getMonth(), 10) + 1) + "-" + date.getFullYear();
            } else {
                return '';
            }
        }


        // This function convert given date, time in epoch format.
        function getDateInEpochFormat(date, time) {
            new_date = new Date(date);
            return (new_date.getTime()) / 1000;
        }

        // This function send ajax call as per given param to get device service perf info. 
        function sendAjax(ajax_start_date, ajax_end_date) {

            var urlDataStartDate = '', urlDataEndDate = '';
            if (ajax_start_date == '' && ajax_end_date == '') {
                // Pass
            } else if(clicked_tab_id.indexOf('custom') > -1) {
                urlDataStartDate = getDateInEpochFormat(ajax_start_date);
                urlDataEndDate = getDateInEpochFormat(ajax_end_date);
            } else if(clicked_tab_id.indexOf('bird') > -1) {
                // Pass
            } else {
                var end_Date = "";
                if (moment(ajax_start_date).date() == moment(ajax_end_date).date() && moment(ajax_start_date).dayOfYear() == moment(ajax_end_date).dayOfYear()) {
                    end_Date = moment(ajax_end_date).toDate();
                } else {
                    end_Date = moment(ajax_start_date).endOf('day').toDate();
                }
                urlDataStartDate = getDateInEpochFormat(ajax_start_date);
                urlDataEndDate = getDateInEpochFormat(end_Date)
            }
            is_normal_table = false;
            $.ajax({
                url: get_url,
                data: {
                    'start_date': urlDataStartDate,
                    'end_date': urlDataEndDate
                },
                type: "GET",
                dataType: "json",
                success: function (response) {
                    var result = "";
                    // Type check of response
                    if (typeof response == 'string') {
                        result = JSON.parse(response);
                    } else {
                        result = response;
                    }

                    if (result.success == 1) {

                        var grid_headers = result.data.objects.table_data_header,
                            plot_type = result['data']['objects']['plot_type'];

                        if (plot_type && plot_type.toLowerCase() == 'string') {
                            draw_type = 'table';
                            $('#item_type_btn').addClass('hide');
                        } else {
                            $('#item_type_btn').removeClass('hide');
                        }

                        if (grid_headers && grid_headers.length > 0) {

                            if (!is_birdeye_view) {
                                // update 'draw_type' variable
                                draw_type = 'table';
                                // Update radio button selection
                                $('#display_table').attr('checked', 'checked');
                                $('#display_table').prop('checked', true);

                                // Update dropdown button html
                                updateDropdownHtml();

                                // Hide display type option from only table tabs
                                if (!$("#display_type_container").hasClass("hide")) {
                                    $("#display_type_container").addClass("hide")
                                }
                            }
                            
                            // Destroy Highchart
                            nocout_destroyHighcharts(service_id);

                            if (typeof(grid_headers[0]) == 'string') {
                                is_normal_table = true;
                                var table_data = result.data.objects.table_data ? result.data.objects.table_data : [];
                                if ($('table[id*="other_perf_table"]').length == 0) {
                                    initNormalDataTable_nocout(
                                        'other_perf_table',
                                        grid_headers,
                                        service_id
                                    );
                                }

                                // Call addDataToNormalTable_nocout (utilities) function to add data to initialize datatable
                                addDataToNormalTable_nocout(
                                    table_data,
                                    grid_headers,
                                    'other_perf_table',
                                    service_id
                                );
                            } else {
                                setTimeout(function() {
                                    initChartDataTable_nocout(
                                        "other_perf_table",
                                        listing_headers,
                                        service_id,
                                        listing_ajax_url,
                                        true
                                    );
                                },300)
                            }
                        } else {
                            var chart_config = result.data.objects;

                            if (
                                listing_ajax_url.indexOf('service/rf/') > -1
                                ||
                                listing_ajax_url.indexOf('servicedetail') > -1
                                ||
                                listing_ajax_url.indexOf('availability') > -1) {
                                
                                if (!is_birdeye_view && !is_custom_view) {
                                    // Show display type option from only table tabs
                                    if (!$("#display_type_container").hasClass("hide")) {
                                        $("#display_type_container").addClass("hide")
                                    }
                                    draw_type = 'chart';
                                    // Update radio button selection
                                    $('#display_chart').attr('checked', 'checked');
                                    $('#display_chart').prop('checked', true);

                                    // Update dropdown button html
                                    updateDropdownHtml();
                                }
                            } else {
                                if (!is_birdeye_view && !is_custom_view) {
                                    // Show display type option from only table tabs
                                    if ($("#display_type_container").hasClass("hide")) {
                                        $("#display_type_container").removeClass("hide")
                                    }
                                }
                            }

                            // If any data available then plot chart & table
                            if (chart_config.chart_data.length > 0) {
                                if (draw_type == 'chart') {
                                    if (!is_birdeye_view && !is_custom_view) {
                                        // Destroy 'perf_data_table'
                                        nocout_destroyDataTable('other_perf_table');
                                    }

                                    if (!(
                                        listing_ajax_url.indexOf('service/rf/') > -1
                                        ||
                                        listing_ajax_url.indexOf('servicedetail') > -1
                                        ||
                                        listing_ajax_url.indexOf('availability') > -1
                                    )) {
                                        if (!is_birdeye_view && !is_custom_view) {
                                            nocout_destroyDataTable('perf_data_table');
                                        }
                                    }

                                    if (!$('#' + service_id+ '_chart').highcharts()) {
                                        createHighChart_nocout(chart_config,service_id, false, false, function(status) {
                                            // 
                                        });
                                    } else {
                                        addPointsToChart_nocout(chart_config.chart_data,service_id);
                                    }

                                    // To show the table in case of utilization_top tab
                                    if (
                                        listing_ajax_url.indexOf('servicedetail') > -1
                                        ||
                                        listing_ajax_url.indexOf('service/rf/') > -1
                                        ||
                                        listing_ajax_url.indexOf('availability') > -1
                                    ) {
                                        if ($("#perf_data_table").length == 0 || !$("#perf_data_table").html()) {
                                            var contentHtml = createChartDataTableHtml_nocout(
                                                "perf_data_table",
                                                chart_config.chart_data
                                            );

                                            // Update bottom table HTML
                                            $('#' + service_id+ '_bottom_table').html(contentHtml);

                                            // Margin of 20px between the chart & table
                                            $('#' + service_id+ '_bottom_table').css("margin-top","20px");

                                            $("#perf_data_table").DataTable({
                                                sDom: 'T<"clear">lfrtip',
                                                oTableTools: {
                                                    sSwfPath: base_url + "/static/js/datatables/extras/TableTools/media/swf/copy_csv_xls.swf",
                                                    aButtons: [
                                                        {
                                                            sExtends: "xls",
                                                            sButtonText: "Download Excel",
                                                            sFileName: "*.xls",
                                                            // mColumns: excel_columns
                                                        }
                                                    ]
                                                },
                                                fnInitComplete: function(oSettings) {
                                                    var row_per_pages_selectbox = '#perf_data_table_wrapper div.dataTables_length label select',
                                                        search_box = '#perf_data_table_wrapper div.dataTables_filter label input';
                                                    // Update search txt box & row per pages dropdown style
                                                    $(row_per_pages_selectbox + ' , ' + search_box).addClass("form-control");
                                                    $(row_per_pages_selectbox + ' , ' + search_box).addClass("input-sm");
                                                    $(row_per_pages_selectbox + ' , ' + search_box).css("max-width","150px");
                                                },
                                                bPaginate: true,
                                                bDestroy: true,
                                                aaSorting : [[0,'desc']],
                                                sPaginationType: "full_numbers"
                                            });
                                        }
                                        // Add data to table
                                        addDataToChartTable_nocout(chart_config.chart_data, 'perf_data_table');
                                    }

                                } else {
                                    // Destroy Highcharts
                                    if (!is_birdeye_view && !is_custom_view) {
                                        nocout_destroyHighcharts(service_id);
                                    }

                                    if (listing_ajax_url.indexOf('servicedetail') == -1) {
                                        if (!is_birdeye_view && !is_custom_view) {
                                            draw_type = 'table';
                                            // Update radio button selection
                                            $('#display_table').attr('checked', 'checked');
                                            $('#display_table').prop('checked', true);

                                            // Update dropdown button html
                                            updateDropdownHtml();
                                        }

                                        setTimeout(function() {
                                            initChartDataTable_nocout(
                                                "other_perf_table",
                                                listing_headers,
                                                service_id,
                                                listing_ajax_url,
                                                true
                                            );
                                        }, 300)
                                    }
                                }
                            } else {
                                if (draw_type == 'chart') {
                                    if (!is_birdeye_view && !is_custom_view) {
                                        if (!$('#' + service_id+ '_chart').highcharts()) {
                                            nocout_destroyDataTable('perf_data_table');
                                        }
                                    }

                                    if (!$.trim(ajax_start_date) && !$.trim(ajax_end_date)) {
                                        if (!$('#' + service_id+ '_chart').highcharts()) {
                                            $('#' + service_id+ '_chart').html("No Data.");
                                        }
                                    }
                                } else {

                                    if (listing_ajax_url.indexOf('servicedetail') == -1) {
                                        // Clear the DIV HTML
                                        $('#' + service_id+ '_chart').html("");
                                        
                                        var table_headers = default_live_table_headers,
                                            not_availability_page = listing_ajax_url.indexOf("availability")  == -1,
                                            not_live_tab = listing_ajax_url.split("data_for=")[1].indexOf('live') == -1;

                                        // If historical tab then update table_headers variable
                                        if (show_historical_on_performance && not_availability_page && not_live_tab) {
                                            table_headers = default_hist_table_headers;
                                        }
                                        if (!is_birdeye_view && !is_custom_view) {
                                            draw_type = 'table';
                                            // Update radio button selection
                                            $('#display_table').attr('checked', 'checked');
                                            $('#display_table').prop('checked', true);

                                            // Update dropdown button html
                                            updateDropdownHtml();
                                        }

                                        setTimeout(function() {
                                            initChartDataTable_nocout(
                                                "other_perf_table",
                                                listing_headers,
                                                service_id,
                                                listing_ajax_url,
                                                true
                                            );
                                        }, 300);
                                    }
                                }
                            }
                        }
                    } else {
                        if (
                            listing_ajax_url.indexOf('service/rf/') > -1
                            ||
                            listing_ajax_url.indexOf('servicedetail') > -1
                            ||
                            listing_ajax_url.indexOf('availability') > -1
                        ) {
                            if (!is_birdeye_view && !is_custom_view) {
                                // Show display type option from only table tabs
                                if (!$("#display_type_container").hasClass("hide")) {
                                    $("#display_type_container").addClass("hide")
                                }

                                draw_type = 'chart';
                                // Update radio button selection
                                $('#display_chart').attr('checked', 'checked');
                                $('#display_chart').prop('checked', true);

                                // Update dropdown button html
                                updateDropdownHtml();
                            }
                        } else {
                            if (!is_birdeye_view && !is_custom_view) {
                                // Show display type option from only table tabs
                                if ($("#display_type_container").hasClass("hide")) {
                                    $("#display_type_container").removeClass("hide")
                                }
                            }
                        }

                        if (draw_type == 'chart') {
                            if(!(
                                listing_ajax_url.indexOf('service/rf/') > -1
                                ||
                                listing_ajax_url.indexOf('servicedetail') > -1
                                ||
                                listing_ajax_url.indexOf('availability') > -1
                            )) {
                                if (!is_birdeye_view && !is_custom_view) {
                                    if (!$('#' + service_id+ '_chart').highcharts()) {
                                        nocout_destroyDataTable('perf_data_table');
                                    }
                                }
                            }
                            if (!$.trim(ajax_start_date) && !$.trim(ajax_end_date)) {
                                if (!$('#' + service_id+ '_chart').highcharts()) {
                                    $('#' + service_id+ '_chart').html(result.message);
                                }
                            }
                        } else {
                            // Clear chart DIV HTML
                            $('#' + service_id+ '_chart').html("");

                            var table_headers = default_live_table_headers;

                            if (show_historical_on_performance && listing_ajax_url.split("data_for=")[1].indexOf('live') == -1) {
                                table_headers = default_hist_table_headers;
                            }
                            
                            if (!is_birdeye_view && !is_custom_view) {
                                draw_type = 'table';
                                // Update radio button selection
                                $('#display_table').attr('checked', 'checked');
                                $('#display_table').prop('checked', true);

                                // Update dropdown button html
                                updateDropdownHtml();
                            }

                            initChartDataTable_nocout(
                                "other_perf_table",
                                listing_headers,
                                service_id,
                                listing_ajax_url,
                                true
                            );
                        }
                    }

                    if (draw_type == 'chart') {
                        //check condition if start date and end date is defined.
                        if ($.trim(ajax_start_date) && $.trim(ajax_end_date)) {
                            //if last date
                            if (moment(ajax_start_date).date() == moment(ajax_end_date).date() && moment(ajax_start_date).dayOfYear() == moment(ajax_end_date).dayOfYear()) {

                                if (!$('#' + service_id+ '_chart').highcharts()) {
                                    $('#' + service_id+ '_chart').html(result.message);
                                }

                                hideSpinner();
                            //Else sendAjax request for next Date
                            } else {

                                var nextDay = moment(ajax_start_date).add(1, 'd');
                                var ohayoo = nextDay.startOf('day');
                                timeInterval = setTimeout(function () {
                                    (function(ohayoo) {
                                        sendAjax(ohayoo.toDate(), ajax_end_date);
                                    })(ohayoo);
                                }, 400);
                            }
                        } else {
                            hideSpinner();
                        }
                    } else if(draw_type == 'table' && is_normal_table) {
                        if ($.trim(ajax_start_date) && $.trim(ajax_end_date)) {
                            //if last date
                            if (moment(ajax_start_date).date() == moment(ajax_end_date).date() && moment(ajax_start_date).dayOfYear() == moment(ajax_end_date).dayOfYear()) {
                                hideSpinner();
                            //Else sendAjax request for next Date
                            } else {

                                var nextDay = moment(ajax_start_date).add(1, 'd');
                                var ohayoo = nextDay.startOf('day');
                                timeInterval = setTimeout(function () {
                                    (function(ohayoo) {
                                        sendAjax(ohayoo.toDate(), ajax_end_date);
                                    })(ohayoo);
                                }, 400);
                            }
                        } else {
                            hideSpinner();    
                        }
                    }
                },
                error : function(err) {
                    // console.log(err.statusText);
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: 'Performance - Service Data',
                        // (string | mandatory) the text inside the notification
                        text: err.statusText,
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: false
                    });

                    hideSpinner();
                }
            });
        }
    };
    /**
     * This function reset the live polling section
     * @method resetLivePolling
     */
    this.resetLivePolling = function(container_dom_id) {

        try {
            $("#"+container_dom_id+"_block .poll_play_btn").button("complete");

            if($("#"+container_dom_id+"_block .poll_play_btn").hasClass("disabled")) {
                $("#"+container_dom_id+"_block .poll_play_btn").removeClass("disabled");
            }
            $("#"+container_dom_id+"_block .poll_interval").removeAttr("disabled");
            $("#"+container_dom_id+"_block .poll_interval").val("");
            $("#"+container_dom_id+"_block .poll_maxInterval").removeAttr("disabled");
            $("#"+container_dom_id+"_block .poll_maxInterval").val("");

            if(pollCallingTimeout) {
                clearTimeout(pollCallingTimeout);
            }

            remainingPollCalls = 0;

        } catch(e) {
            // console.log(e);
        }
    };

    /**
     * This function initializes
     * @method initGetServiceData
     * @param get_service_data_url "String", It contains the url to fetch the status of current device.
     * @param service_id "String", It contains unique name for service.
     * @param device_id "INT", It contains the ID of current device.
     */
    this.initGetServiceData = function(get_service_data_url, service_id, device_id) {
        /*Reset Variables & counters */
        if (timeInterval) {
            clearTimeout(timeInterval);
        }

        nocout_destroyHighcharts(service_id);
        nocout_destroyDataTable('other_perf_table');
        nocout_destroyDataTable('perf_data_table');

        if(get_service_data_url && service_id && device_id) {
            /*Call getServiceData function to fetch the data for clicked service tab*/
            perfInstance.getServiceData(get_service_data_url, service_id, device_id);
        } else if (is_perf_polling_enabled) {
            setTimeout(function(e) {
                nocout_togglePollNowContent();
            }, 150);
        }
    };
}


/** 
 * This function updates service/datasource dropdown HTML on change of its value
 * @method updateServiceTypeDropdownHtml
 */
function updateServiceTypeDropdownHtml() {

    var view_type = $("input[name='service_view_type']:checked").val(),
        icon_html = '<i class="text-primary fa fa-bar-chart-o"> </i>';

    if (view_type == 'normal') {
        icon_html += ' Datasource View';
    } else {
        icon_html += ' Service View';
    }

    // Create button new html
    var caret_html = ' <span class="caret"></span> ',
        btn_html = icon_html + caret_html,
        radioId = $("input[name='service_view_type']:checked").attr('id');

    // Remove active class from all li
    $('#service_view_type_ul li').removeClass('active');

    // Add active class of current parent li
    $('a[radioId="' + radioId + '"]').parent().addClass('active');

    // Update dropdown button html
    $('#service_view_type_btn').html(btn_html);
}


/** 
 * This function updates display table/chart dropdown HTML on change of its value
 * @method updateDropdownHtml
 */
function updateDropdownHtml() {
    var draw_type = $("input[name='item_type']:checked").val(),
        icon_html = '';

    if (draw_type == 'chart') {
        icon_html = '<i class="text-primary fa fa-bar-chart-o"> </i> Display Chart';
    } else {
        icon_html = '<i class="text-primary fa fa-table"> </i> Display Table';
    }

    // Create button new html
    var caret_html = ' <span class="caret"></span> ',
        btn_html = icon_html + caret_html,
        radioId = $("input[name='item_type']:checked").attr('id');

    // Remove active class from all li
    $('#item_type_ul li').removeClass('active');

    // Add active class of current parent li
    $('a[radioId="' + radioId + '"]').parent().addClass('active');

    // Update dropdown button html
    $('#item_type_btn').html(btn_html);
}


/**
 * This event trigger when innermost tabs (historical + live) clicked
 * @event click(with delegate)
 */
$('.inner_tab_container').delegate('ul.inner_inner_tab li a','click',function (e) {
    var current_target = e.currentTarget,
        current_attr = current_target.attributes,
        tab_service_id = current_target.id.slice(0, -4);

    if (last_active_tab && last_active_tab.indexOf('live_poll_now') > -1 && is_polling_active) {
        // Stop live polling
        nocout_stopPollNow();
        // notify user
        bootbox.alert("Live polling is stopped");
    } else {
        var service_data_url_val = current_attr.url ? $.trim(current_attr.url.value) : "";
            serviceDataUrl = "";

        if (service_data_url_val) {
            if (service_data_url_val[0] != "/") {
                serviceDataUrl = "/" + service_data_url_val;
            } else {
                serviceDataUrl = service_data_url_val;
            }
        }

        if (show_historical_on_performance || is_perf_polling_enabled) {
            perfInstance.initGetServiceData(serviceDataUrl, tab_service_id, current_device);
        }
    }

    last_active_tab = tab_service_id;
});


/**
 * This event trigger when display type radio buttons changed
 * @event Change
 */
$('input[name="item_type"]').change(function(e) {

    var active_tab_obj = nocout_getPerfTabDomId(),
        service_id = active_tab_obj["active_dom_id"] ? active_tab_obj["active_dom_id"] : "",
        get_service_data_url = active_tab_obj["active_tab_api_url"] ? active_tab_obj["active_tab_api_url"] : "";

    if (
        service_id.indexOf('availability') > -1
        ||
        service_id.indexOf('utilization_top') > -1
        ||
        service_id.indexOf('topology') > -1
    ) {

        var active_inner_tab = $('.top_perf_tab_content div.active .inner_tab_container .nav-tabs li.active a'),
            service_id = active_inner_tab.attr("id").slice(0, -4),
            get_service_data_url = active_inner_tab.attr("url");
    }

    // Update dropdown button html
    updateDropdownHtml();

    if (get_service_data_url && service_id && current_device) {
        perfInstance.initGetServiceData(get_service_data_url, service_id, current_device);
    } else if (is_perf_polling_enabled) {
        nocout_togglePollNowContent();
    }
});


/**
 * This event trigger when one time poll button under onDemand Polling tab clicked
 * @event click(with delegate)
 */
$(".perfContainerBlock").delegate('.single_perf_poll_now', 'click', function(e) {

    var active_tab_obj = nocout_getPerfTabDomId(),
        tab_id = active_tab_obj["active_dom_id"];

    var currentTarget = e.currentTarget;
    // Show button in loading view
    $(currentTarget).button('loading');
    if(!$("#" + tab_id + "_block .play_pause_btns").hasClass("disabled")) {
        $("#" + tab_id + "_block .play_pause_btns").addClass("disabled");
    }
    initSingleDevicePolling(function(response) {
        
        $(currentTarget).button('complete');
        
        if($("#" + tab_id + "_block .play_pause_btns").hasClass("disabled")) {
            $("#" + tab_id + "_block .play_pause_btns").removeClass("disabled");
        }
    });
});


/**
 * This event trigger when recursive poll button(Play Button) under onDemand Polling tab clicked
 * @event click(with delegate)
 */
$(".perfContainerBlock").delegate('.poll_play_btn', 'click', function(e) {
    // Update the flag
    is_polling_active = true;
    var active_tab_obj = nocout_getPerfTabDomId(),
        tab_id = active_tab_obj["active_dom_id"];

    var poll_interval = $("#" + tab_id + "_block .poll_interval").val(),
        max_interval = $("#" + tab_id + "_block .poll_maxInterval").val();
    
    if (poll_interval && max_interval) {
        // Show button in loading view
        $(e.currentTarget).button('loading');

        if($("#"+tab_id+ "_block .poll_pause_btn").hasClass("disabled")) {
            $("#"+tab_id+ "_block .poll_pause_btn").removeClass("disabled");
        }

        if(!$("#" + tab_id + "_block .single_perf_poll_now").hasClass("disabled")) {
            $("#" + tab_id + "_block .single_perf_poll_now").addClass("disabled");
        }
        /*Disable poll interval & max interval dropdown*/
        $("#" + tab_id + "_block .poll_interval").attr("disabled","disabled");
        $("#" + tab_id + "_block .poll_maxInterval").attr("disabled","disabled");

        pollCallingTimeout = "";
        pollingInterval = $("#" + tab_id + "_block .poll_interval").val() ? +($("#" + tab_id + "_block .poll_interval").val()) : 10;
        pollingMaxInterval = $("#" + tab_id + "_block .poll_maxInterval").val() ? +($("#" + tab_id + "_block .poll_maxInterval").val()) : 1;
        isPollingPaused = 0;
        if(remainingPollCalls == 0) {
            remainingPollCalls = Math.floor((60*pollingMaxInterval)/pollingInterval);
        }

        recursivePolling();

    } else {
        bootbox.alert("Please select polling interval & maximum interval.");
    }
});


/**
 * This event trigger when recursive poll pause button(Pause Button) under onDemand Polling tab clicked
 * @event click(with delegate)
 */
$(".perfContainerBlock").delegate('.poll_pause_btn', 'click', function(e) {
    nocout_pausePollNow();
});


/**
 * This event trigger when recursive poll stop button(Stop Button) under onDemand Polling tab clicked
 * @event click(with delegate)
 */
$(".perfContainerBlock").delegate('.poll_stop_btn', 'click', function(e) {
    nocout_stopPollNow();
});


/**
 * This event trigger when reset live polled data button(Reset Button) under onDemand Polling tab clicked
 * @event click(with delegate)
 */
$(".perfContainerBlock").delegate('.reset_live_polling', 'click', function(e) {
    var active_tab_obj = nocout_getPerfTabDomId(),
        tab_id = active_tab_obj["active_dom_id"];

    if (poll_now_data_dict[tab_id] && poll_now_data_dict[tab_id].length > 0) {
        try {
            if ($("#" + tab_id + "_chart").highcharts()) {
                var chart = $("#" + tab_id + "_chart").highcharts(),
                    chart_series = chart.series;

                if (chart_series && chart_series.length > 0) {
                    // Remove series from highchart
                    while(chart_series.length > 0) {
                        chart_series[0].remove(true);
                    }
                }
                // Destroy highchart
                $("#" + tab_id + "_chart").highcharts().destroy();
            }

            if ($("#" + tab_id + "_bottom_table").length) {
                $("#" + tab_id + "_bottom_table").html("");
            }

            nocout_destroyDataTable('other_perf_table');
        } catch(e) {
            // console.log(e);
        }

        // Reset the global variable
        poll_now_data_dict[tab_id] = [];
        // Reset the min, max & avg legends DOM
        if(!$('#' + tab_id + '_legends_block').hasClass('hide')) {
            $('#' + tab_id + '_legends_block').addClass('hide');
        }
    } else {
        bootbox.alert("You don't have any live polled data for this service/data source.");
    }
});


/**
 * This event trigger when service/datasource view radio buttons changed
 * @event Change
 */
$('input[name="service_view_type"]').change(function(e) {

    // selected value of 'service_view_type'
    var service_view_type = $(this).val();

    // Set the 'service_view_type'  cookie
    $.cookie("service_view_type", service_view_type, {path: '/'});
    
    // Reload the page
    initPerformancePage();
});


/**
 * This event trigger when display type value clicked from display type dropdown
 * @event Click
 */
$('#item_type_ul li a').click(function(e) {

    // Prevent default functionality
    e.preventDefault();

    var radio_id = $(this).attr('radioId')

    $('#' + radio_id)[0].checked = true;
    $('#' + radio_id).trigger('change');
});


/**
 * This event trigger when service/datasource view value clicked from service/datasource view dropdown
 * @event Click
 */
$('#service_view_type_ul li a').click(function(e) {

    // Prevent default functionality
    e.preventDefault();

    var radio_id = $(this).attr('radioId')

    // Update radio button selection
    $('#' + radio_id).attr('checked', 'checked');
    $('#' + radio_id).prop('checked', true);

    // Update dropdown button html
    updateServiceTypeDropdownHtml();

    // Set the 'service_view_type'  cookie
    $.cookie("service_view_type", $('#' + radio_id).val(), {path: '/'});

    // Reload the page
    initPerformancePage();
});


/**
 * This event trigger all service report download button clicked
 * @event Click
 */
$('#all_serv_live_report_btn').click(function(e) {
    
    // prevent default functionality
    e.preventDefault();

    var report_title = 'All Services(Live Data - 5 Min.)' + current_device_ip,
        services_list = $(this).data('services');

    if (services_list && typeof services_list == 'object') {
        services_list = JSON.stringify(services_list);
    }

    var main_url = base_url+"/downloader/datatable/?",
        url_get_param = '';
        applied_start_date = '',
        applied_end_date = '';

    // If any datetime filter applied
    if (startDate && endDate) {
        applied_start_date = startDate.toDate().getTime() / 1000;
        applied_end_date = endDate.toDate().getTime() / 1000;
    }

    var datetime_filter_param = " 'start_date' : '" + applied_start_date + "', 'end_date' : '" + applied_end_date + "' ",
        device_id_param = " 'device_id' : '" + current_device + "' ",
        service_list_param = " 'service_view_type' : '" + $('input[name="service_view_type"]:checked').val() + "', 'services_list' : "+services_list,
        sds_param = " 'service_data_source_type' : 'all', 'service_name' : 'all', 'data_for' : 'live' ",
        common_param = " 'download_excel' : 'yes', 'report_title' : '" + report_title + "' ",
        specific_params = " 'is_multi_sheet' : 1, 'data_key' : 'services_list', 'change_key' : 'service_name' "
        row_data_param = "";

    // prepare row_data params
    row_data_param += sds_param + "," + datetime_filter_param + ",";
    row_data_param += device_id_param + "," + common_param + ",";
    row_data_param += specific_params + "," + service_list_param ;

    // prepare get params
    url_get_param += "app=performance";
    url_get_param += "&rows="+data_class_name;
    url_get_param += "&rows_data={" + row_data_param + "}"
    url_get_param += "&headers="+header_class_name;
    url_get_param += "&headers_data={" + common_param + "}";

    var api_url = main_url + url_get_param;

    // Make Ajax Call
    $.ajax({
        url : api_url,
        type : 'GET',
        success : function(response) {
            var result = response;
            // parse response if stringified.
            if(typeof response == 'string') {
                result = JSON.parse(response);
            }

            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: report_title,
                // (string | mandatory) the text inside the notification
                text: result.message,
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // Time in ms after which the gritter will dissappear.
                time : 1000
            });
        },
        error : function(err) {
            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: report_title,
                // (string | mandatory) the text inside the notification
                text: err.statusText,
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // Time in ms after which the gritter will dissappear.
                time : 1000
            });
        }
    });
});


/**
 * This event trigger when live+hist report download button clicked.
 * @event Click
 */
$('#live_hist_report_btn').click(function(e) {
    
    // prevent default functionality
    e.preventDefault();

    var main_url = base_url+"/downloader/datatable/?",
        live_hist_obj = [],
        url_get_param = '';
        applied_start_date = '',
        applied_end_date = '',
        active_tab_obj = nocout_getPerfTabDomId(),
        tab_text = $.trim($('#' + active_tab_obj.active_dom_id + '_tab').text()),
        active_tab_api_url = active_tab_obj.active_tab_api_url,
        service_name = active_tab_api_url.split('/service/')[1].split('/')[0],
        ds_name = active_tab_api_url.split('/service_data_source/')[1].split('/')[0],
        report_title = 'Single Service (Live + Historical) - ' + current_device_ip;

    // If any datetime filter applied
    if (startDate && endDate) {
        applied_start_date = startDate.toDate().getTime() / 1000;
        applied_end_date = endDate.toDate().getTime() / 1000;
    }

    if (service_name.indexOf('_status') > -1 || service_name.indexOf('_invent') > -1) {
        live_hist_obj = live_data_tab.concat(inventory_status_inner_inner_tabs);
    } else {
        live_hist_obj = live_data_tab.concat(tabs_with_historical);
    }

    var datetime_filter_param = " 'start_date' : '" + applied_start_date + "', 'end_date' : '" + applied_end_date + "' ",
        device_id_param = " 'device_id' : '" + current_device + "' ",
        tabs_list_param = " 'tabs_list' : "+JSON.stringify(live_hist_obj),
        sds_param = " 'service_data_source_type' : '" + ds_name + "', 'service_name' : '" + service_name + "', 'data_for' : 'live' ",
        common_param = " 'download_excel' : 'yes', 'report_title' : '" + report_title + "' ",
        specific_params = " 'is_multi_sheet' : 1, 'data_key' : 'tabs_list', 'change_key' : 'data_for' "
        row_data_param = "";

    // prepare row_data params
    row_data_param += sds_param + "," + datetime_filter_param + ",";
    row_data_param += device_id_param + "," + common_param + ",";
    row_data_param += specific_params + "," + tabs_list_param + ",";
    row_data_param += " 'service_view_type' : '" + $('input[name="service_view_type"]:checked').val() + "' ";

    // prepare get params
    url_get_param += "app=performance";
    url_get_param += "&rows="+data_class_name;
    url_get_param += "&rows_data={" + row_data_param + "}"
    url_get_param += "&headers="+header_class_name;
    url_get_param += "&headers_data={" + common_param + "}";

    var api_url = main_url + url_get_param;

    // Make Ajax Call
    $.ajax({
        url : api_url,
        type : 'GET',
        success : function(response) {
            var result = response;
            // parse response if stringified.
            if(typeof response == 'string') {
                result = JSON.parse(response);
            }

            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: report_title,
                // (string | mandatory) the text inside the notification
                text: result.message,
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // Time in ms after which the gritter will dissappear.
                time : 1000
            });
        },
        error : function(err) {
            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: report_title,
                // (string | mandatory) the text inside the notification
                text: err.statusText,
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // Time in ms after which the gritter will dissappear.
                time : 1000
            });
        }
    });
});


$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href),
        url_param = "";
    if (results == null) {
        url_param = null;
    } else {
        url_param = results[1] || 0;
    }
    return url_param;
};


function updateQueryStringParameter(uri, key, value) {
    var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i"),
        separator = uri.indexOf('?') !== -1 ? "&" : "?",
        query_str = "";
    if (uri.match(re)) {
        query_str = uri.replace(re, '$1' + key + "=" + value + '$2');
    } else {
        query_str = uri + separator + key + "=" + value;
    }

    return query_str;
}