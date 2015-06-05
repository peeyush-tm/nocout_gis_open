/**
 * This file contain the global reusable function for nocout platform
 * @for nocoutUtilsLib
 */


// Global Variables
var green_color = "#468847",
    orange_color = "#f0ad4e",
    red_color = "#b94a48",
    ok_severity_color = "#30B91A",
    unknown_severity_color = "#555555",
    green_status_array = ['ok', 'success', 'up'],
    red_status_array = ['critical'],
    down_status_array = ['down'],
    orange_status_array = ['warning'],
    left_block_style = "border:1px solid #CCC;border-right:0px;padding: 3px 5px;background:#FFF;",
    right_block_style = "border:1px solid #CCC;padding: 3px 5px;background:#FFF;",
    val_icon = '<i class="fa fa-arrow-circle-o-right"></i>',
    time_icon = '<i class="fa fa-clock-o"></i>',
    perf_page_live_polling_call = "",
    isLatestStatusUpdated = false,
    table_title = 'Service Datasource Report',
    app_name = 'performance',
    header_class_name = 'ServiceDataSourceHeaders',
    data_class_name = 'ServiceDataSourceListing',
    header_extra_param = "{'download_excel': 'yes' }";


/**
 * This function is used to populate the latest status info for any device as per given params
 * @method populateDeviceStatus_nocout
 * @param domElement {String}, It contains the dom element ID on which the info is to be populated
 * @param info {Object}, It contains the latest status info object
 */
function populateDeviceStatus_nocout(domElement,info) {

    if (isLatestStatusUpdated) {
        return true;
    }

    var fa_icon_class = "",
        txt_color = "",
        status_html = "",
        age = info.age ? info.age : "Unknown",
        lastDownTime = info.last_down_time ? info.last_down_time : "Unknown",
        status = info.status ? info.status.toUpperCase() : "Unknown",
        severity_up = info.severity && info.severity.ok ? Number(info.severity.ok) : 0,
        severity_warn = info.severity && info.severity.warn ? Number(info.severity.warn) : 0,
        severity_crit = info.severity && info.severity.crit ? Number(info.severity.crit) : 0,
        severity_unknown = info.severity && info.severity.unknown ? Number(info.severity.unknown) : 0;

    var severity_style_obj = nocout_getSeverityColorIcon(status);

    txt_color = severity_style_obj.color ? severity_style_obj.color : "";
    fa_icon_class = severity_style_obj.icon ? severity_style_obj.icon : "fa-circle";

    status_html = "";
    status_html += '<table id="final_status_table" class="device_status_tbl table table-responsive table-bordered" \
                    style="background:#FFFFFF;"><tr style="color:' + txt_color + ';">\
                    <td class="one_fourth_column vAlign_middle">\
                    <i title = "' + status + '" class="fa ' + fa_icon_class + '" \
                    style="vertical-align: middle;"> </i> \
                    <b>Current Status</b> : ' + status + '</td>\
                    <td class="one_fourth_column vAlign_middle">\
                    <b>Since</b> : ' + age + '</td>\
                    <td class="one_fourth_column vAlign_middle">\
                    <b>Last Down Time</b> : ' + lastDownTime + '</td>\
                    <td title="OK" class="severity_block vAlign_middle" style="background:' + ok_severity_color + ';">' + severity_up + '</td>\
                    <td title="Warning" class="severity_block vAlign_middle" style="background:' + orange_color + ';">' + severity_warn + '</td>\
                    <td title="Critical" class="severity_block vAlign_middle" style="background:' + red_color + ';">' + severity_crit + '</td>\
                    <td title="Unknown" class="severity_block vAlign_middle" \
                    style="background:' + unknown_severity_color + ';">' + severity_unknown + '</td>\
                    </tr></table>';

    // Update Status Block HTML as per the device status
    $("#" + domElement).html(status_html);

    if (!isLatestStatusUpdated) {
        isLatestStatusUpdated = true;
    }
}

/**
 * This function is used to get icon & color as per the severity
 * @method nocout_getSeverityColorIcon
 * @param status {String}, It contains the severity status
 */

function nocout_getSeverityColorIcon(status) {

    var info_obj = {
        "color" : "",
        "icon" : "fa-circle"
    };

    if (!status) {
        return info_obj;
    }

    if (green_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        info_obj.color = green_color;
        info_obj.icon = "fa-check-circle";
    } else if (red_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        info_obj.color = red_color;
        info_obj.icon = "fa-times-circle";
    } else if (orange_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        info_obj.color = orange_color;
        info_obj.icon = "fa-warning";
    } else if (down_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        info_obj.color = red_color;
        info_obj.icon = "fa-warning";
    } else {
        // pass
    }

    return info_obj;
}


/**
 * This function is used to populate the latest status for any service as per given params
 * @method populateServiceStatus_nocout
 * @param domElement {String}, It contains the dom element ID on which the info is to be populated
 * @param info {Object}, It contains the latest status object
 */
function populateServiceStatus_nocout(domElement,info) {

    // if (!is_perf_polling_enabled) {
        /********** Service Status Without Live Polling  - START     ********************/
        if ($.trim(info.last_updated) !== "" || $.trim(info.perf) !== "") {
            var last_updated = info.last_updated ? info.last_updated : "N/A",
                perf = info.perf ? info.perf : "N/A",
                status = info.status ? info.status.toUpperCase() : "",
                txt_color = "",
                fa_icon_class = "",
                inner_status_html = '',
                severity_style_obj = nocout_getSeverityColorIcon(status);

            txt_color = severity_style_obj.color ? severity_style_obj.color : "";
            fa_icon_class = severity_style_obj.icon ? severity_style_obj.icon : "fa-circle";
            inner_status_html = '<table id="perf_output_table" class="table table-responsive table-bordered">\
                                  <tr style="color:'+txt_color+';"><td>\
                                  <i title = "' + status + '" class="fa ' + fa_icon_class + '" \
                                  style="vertical-align: middle;"> </i> \
                                  <b>Performance Output</b> : ' + perf + '</td>\
                                  <td><b>Updated At</b> : ' + last_updated + '</td>\
                                  </tr>\
                                  </table><div class="clearfix"></div><div class="divide-20"></div>';

            $("#" + domElement).html(inner_status_html);
        } else {
            $("#" + domElement).html("");
        }

        /********** Service Status Without Live Polling  - END     ********************/
    // } else {
    //     /********** LIVE POLLING CODE  - START     ********************/
    //     var left_tab_txt = '';

    //     try {
    //         left_tab_txt = $.trim($("#" + domElement.split("_block")[0].split("last_updated_")[1]+"_tab").text());
    //     } catch(e) {
    //         // console.log(e);
    //     }
    //     var dom_condition_1 = domElement.indexOf('availability') > -1,
    //         dom_condition_2 = domElement.indexOf('utilization_top') > -1,
    //         dom_condition_3 = domElement.indexOf('topology') > -1;
    //     // Clear status block when we are on utilization or availablility tabs
    //     if (dom_condition_1 || dom_condition_2 || dom_condition_3 || left_tab_txt == 'RF Latency') {

    //         $("#" + domElement).html("");

    //     } else {

    //         var last_updated = info.last_updated ? info.last_updated : "N/A",
    //             perf = info.perf ? info.perf : "N/A",
    //             inner_status_html = '';

    //         // Create Table for service polled value & live polling --- START
    //         inner_status_html += '<table id="perf_output_table" class="table table-responsive table-bordered" style="background:#F5F5F5;">';
    //         inner_status_html += '<tr>';
            
    //         inner_status_html += '<td style="width:47.5%;"><b>Service Output :</b> <br/>\
    //                             ' + val_icon + ' ' + perf + '<br/>\
    //                             ' + time_icon + ' ' + last_updated + '</td>';
    //         inner_status_html += '<td style="width:5%;vertical-align: middle;text-align:center;">\
    //                              <button class="btn btn-primary btn-xs perf_poll_now"\
    //                              title="Poll Now" data-complete-text="<i class=\'fa fa-flash\'></i>" \
    //                              data-loading-text="<i class=\'fa fa-spinner fa fa-spin\'> </i>">\
    //                              <i class="fa fa-flash"></i></button>\
    //                              </td>';
    //         inner_status_html += '<td style="width:47.5%;">\
    //                              <b>Poll Output :</b> \
    //                              <span id="perf_live_poll_chart"></span><br/>\
    //                              <ul id="perf_live_poll_vals" class="list-unstyled"></ul>\
    //                              </td>';
            

    //         inner_status_html += '</tr>';
    //         inner_status_html += '</table>';
    //         // Create Table for service polled value & live polling --- END

    //         // Create hidden input field to store polling values --- START
    //         inner_status_html += '<input type="hidden" name="perf_live_poll_input" id="perf_live_poll_input" value="">';
    //         // Create hidden input field to store polling values --- END

    //         inner_status_html += '<div class="clearfix"></div><div class="divide-20"></div>';

    //         $("#"+domElement).html(inner_status_html);
    //     }
    //     /********** LIVE POLLING CODE  - END     ********************/
    // }
}


/**
 * This function adds data to initialized datatable as per given params
 * @method addDataToNormalTable_nocout
 * @param table_data {Array}, It contains the data object array for table
 * @param table_headers {Array}, It contains the headers object array for table
 * @param table_id {String}, It contains the table dom element ID
 */
function addDataToNormalTable_nocout(table_data, table_headers, table_id) {

    for (var j = 0; j < table_data.length; j++) {
        var row_val = [];
        for (var i = 0; i < table_headers.length; i++) {
            var insert_val = table_data[j][table_headers[i]] ? table_data[j][table_headers[i]] : "";
            row_val.push(insert_val);
        }
        $('#' + table_id).dataTable().fnAddData(row_val);
    }
}

/**
 * This function creates blank data table as per given params
 * @method initNormalDataTable_nocout
 * @param table_id {String}, It contains the table dom element ID
 * @param headers {Array}, It contains the headers object array for table
 * @param service_id {String}, It contains the service dom id in which the table is to be populate.
 */
function initNormalDataTable_nocout(table_id, headers, service_id) {

    var table_string = "",
        grid_headers = headers,
        excel_columns = [];

    // Destroy Datatable
    nocout_destroyDataTable('other_perf_table');
    nocout_destroyDataTable('perf_data_table');

    table_string += '<table id="' + table_id + '" class="datatable table table-striped table-bordered table-hover table-responsive"><thead>';
    /*Table header creation start*/
    for (var i = 0; i < grid_headers.length; i++) {
        table_string += '<td><b>' + grid_headers[i].toUpperCase() + '</b></td>';
        excel_columns.push(i);
    }
    table_string += '</thead></table>';
    /*Table header creation end*/


    if (service_id) {
        $('#' + service_id + '_chart').html(table_string);
    }

    $("#" + table_id).DataTable({
        sDom: 'T<"clear">lfrtip',
        oTableTools: {
            sSwfPath: base_url + "/static/js/datatables/extras/TableTools/media/swf/copy_csv_xls.swf",
            aButtons: [
                {
                    sExtends: "xls",
                    sButtonText: "Download Excel",
                    sFileName: "*.xls",
                    mColumns: excel_columns
                }
            ]
        },
        fnInitComplete: function(oSettings) {
            var row_per_pages_selectbox = '#' + table_id + '_wrapper div.dataTables_length label select',
                search_box = '#' + table_id + '_wrapper div.dataTables_filter label input';
            // Update search txt box & row per pages dropdown style
            $(row_per_pages_selectbox + ' , ' + search_box).addClass("form-control");
            $(row_per_pages_selectbox + ' , ' + search_box).addClass("input-sm");
            $(row_per_pages_selectbox + ' , ' + search_box).css("max-width","150px");
        },
        bPaginate: true,
        bDestroy: true,
        aaSorting : [[0, 'desc']],
        sPaginationType: "full_numbers"
    });
}

/**
 * This function creates blank data table for chart data as per given params
 * @method initChartDataTable_nocout
 * @param table_id {String}, It contains the table dom element ID
 * @param headers {Array}, It contains the headers object array for table
 * @param service_id {String}, It contains the service dom id in which the table is to be populate.
 */
function initChartDataTable_nocout(table_id, headers_config, service_id, ajax_url, has_headers) {

    var data_in_table = "<table id='" + table_id + "' class='datatable table table-striped table-bordered table-hover'><thead>";

    // Destroy Datatable
    nocout_destroyDataTable('other_perf_table');
    nocout_destroyDataTable('perf_data_table');

    /*Table header creation end*/
    if (service_id) {
        $('#'+service_id+'_bottom_table').html(data_in_table);
    }

    var splitted_url = ajax_url.split("/performance/");

    splitted_url[1] = "listing/" + splitted_url[1];

    var updated_url = splitted_url.join("/performance/"),
        tableheaders = headers_config;

    if (!has_headers) {
        // Reset columns variable
        tableheaders = [];
        var has_severity_column = false;
        for(var i=0;i<headers_config.length;i++) {
            var header_key = headers_config[i].name.replace(/ /g, '_').toLowerCase(),
                head_condition_1 = header_key.indexOf('warning_threshold') === -1,
                head_condition_2 = header_key.indexOf('critical_threshold') === -1,
                head_condition_3 = header_key.indexOf('min_value') === -1,
                head_condition_4 = header_key.indexOf('max_value') === -1,
                head_condition_5 = header_key.indexOf('avg_value') === -1,
                head_condition_6 = header_key.indexOf('severity') === -1;

            // Condition check for current value
            if (head_condition_1 && head_condition_2 && head_condition_3 && head_condition_4 && head_condition_5 && head_condition_6) {
                header_key = 'current_value';
            }

            if (header_key.indexOf('min_value') > -1) {
                header_key = 'min_value';
            }

            if (header_key.indexOf('max_value') > -1) {
                header_key = 'max_value';
            }

            if (header_key.indexOf('avg_value') > -1) {
                header_key = 'avg_value';
            }

            if (header_key.indexOf('severity') > -1) {
                header_key = 'severity';
                has_severity_column = true;
            }

            var header_dict = {
                'mData': header_key,
                'sTitle': headers_config[i].name,
                'sWidth': 'auto',
                'bSortable': true
            };

            tableheaders.push(header_dict);
        }

        if (!has_severity_column) {
            // Add severity
            tableheaders.push({
                'mData': 'severity',
                'sTitle': 'Severity',
                'sWidth': 'auto',
                'bSortable': true
            });
        }

        // Add sys_timestamp
        tableheaders.push({
            'mData': 'sys_timestamp',
            'sTitle': 'Time',
            'sWidth': 'auto',
            'bSortable': true
        });
    }

    var service_name = updated_url.split("/service/")[1].split("/")[0],
        ds_name = updated_url.split("/service/")[1].split("/")[2],
        get_param_string = updated_url.split("?")[1].split("&"),
        data_for = 'live',
        get_param_data = "",
        data_extra_param = "";

    for(var i=0;i<get_param_string.length;i++) {
        var splitted_string = get_param_string[i].split("=");
        if (splitted_string[1] != undefined) {
            if (i == get_param_string.length-1) {
                get_param_data += "'" + splitted_string[0] + "':'" + splitted_string[1] + "'";
            } else {
                get_param_data += "'" + splitted_string[0] + "':'" + splitted_string[1] + "',";
            }
        }
    }
    
    if ($(".top_perf_tabs").length > 0) {
        var top_tab_content_href = $(".top_perf_tabs > li.active a").attr('href'),
            top_tab_id = top_tab_content_href.split("#").length > 1 ? top_tab_content_href.split("#")[1] : top_tab_content_href.split("#")[0],
            left_tab_content_href = $("#" + top_tab_id + " .left_tabs_container li.active a").attr("href"),
            left_tab_id = left_tab_content_href.split("#").length > 1 ? left_tab_content_href.split("#")[1] : left_tab_content_href.split("#")[0],
            top_tab_text = $.trim($(".top_perf_tabs > li.active a").text()),
            left_tab_txt = $.trim($("#" + top_tab_id + " .left_tabs_container > li.active a").text()),
            report_title = "";
        
        if (show_historical_on_performance) {
            try {
                var content_tab_text = $.trim($("#" + left_tab_id + " .inner_inner_tab li.active a").text());
                report_title += top_tab_text + " > " + left_tab_txt + " > " + content_tab_text + "(" + current_device_ip + ")";
            } catch(e) {
                report_title += top_tab_text + " > " + left_tab_txt + "(" + current_device_ip + ")";
            }

        } else {
            report_title += top_tab_text + " > " + left_tab_txt + "(" + current_device_ip + ")";
        }

        if (top_tab_text && left_tab_txt && current_device_ip) {
            table_title = report_title;
        }
        
        data_extra_param = "{'service_name' : '" + service_name + "', 'service_data_source_type' : '" + ds_name + "', 'report_title' : '" + table_title + "',";

        if (show_historical_on_performance) {
            data_extra_param += "'device_id' : '" + current_device + "',";
        } else {
            data_extra_param += "'device_id' : '" + current_device + "', 'data_for' : '" + data_for + "',";
        }

        if (get_param_data) {
            data_extra_param += get_param_data+",";
        }

        data_extra_param += "'download_excel': 'yes'";
        data_extra_param += " }";

        /*Call createDataTable function to create the data table for specified dom element with given data*/
        dataTableInstance.createDataTable(
            table_id,
            tableheaders,
            updated_url,
            false,
            table_title,
            app_name,
            header_class_name,
            data_class_name,
            header_extra_param,
            data_extra_param
        );

    } else {
        /*Call createDataTable function to create the data table for specified dom element with given data*/
        dataTableInstance.createDataTable(
            table_id,
            tableheaders,
            updated_url,
            false
        );
    }

}

/**
 * This function adds data to initialized datatable as per given params
 * @method addDataToChartTable_nocout
 * @param table_obj {Array}, It contains the chart data object array
 * @param table_id {String}, It contains the table dom element ID
 */
function addDataToChartTable_nocout(table_obj, table_id) {

    var data = table_obj[0].data,
        total_columns = table_obj.length * 2;

    for(var i = 0; i < data.length; i++) {
        var row_val = [];
        for (var j = 0; j < table_obj.length; j++) {
            if (table_obj[j].type !== 'pie') {
                var inner_data = table_obj[j].data[i];
                if (inner_data) {
                    if (inner_data.constructor === Array) {
                        if (inner_data[0]) {
                            row_val.push(new Date(inner_data[0]).toLocaleString());
                            var chart_val = inner_data[1];
                            row_val.push(chart_val);
                        }
                    } else if (inner_data.constructor === Object) {
                        if (inner_data.x) {
                            row_val.push(new Date(inner_data.x).toLocaleString());
                            var chart_val = inner_data.y;
                            row_val.push(chart_val);
                        }
                    }
                }
            }
        }
        // If row are less than total columns then add blank fields
        if (row_val.length < total_columns) {
            var val_diff = total_columns - row_val.length;
            for(var x=0;x<val_diff;x++) {
                row_val.push(" ");
            }
            $('#' + table_id).dataTable().fnAddData(row_val);
        } else {
            $('#' + table_id).dataTable().fnAddData(row_val);
        }
    }
}

/**
 * This function adds data to created highchart
 * @method addPointsToChart_nocout
 * @param pointArray {Array}, It contains the chart data object array
 * @param dom_id {String}, It contains the chart dom element ID
 */
function addPointsToChart_nocout(pointArray, dom_id) {

    var highChartSeries = $('#'+dom_id+'_chart').highcharts().series;

    for (var i = 0; i < highChartSeries.length; i++) {
        for (var j = 0; j < pointArray[i].data.length; j++) {
            $('#'+dom_id+'_chart').highcharts().series[i].addPoint(pointArray[i].data[j], false, false, false);
        }
    }
}

/**
 * This function creates highchart for device performance
 * @method createHighChart_nocout
 * @param chartConfig {Array}, It contains configuration & data to initialize highcharts
 * @param dom_id {String}, It contains the chart dom element ID
 * @param text_color {String}, It contains the color of text of chart
 * @param need_extra_config {Boolean}, It contains the boolean flag either to add extra config or not.
 */
function createHighChart_nocout(chartConfig, dom_id, text_color, need_extra_config, callback) {

    // Is the y axis should be reversed or not
    var is_y_inverted = chartConfig["is_inverted"] ? chartConfig["is_inverted"] : false,
        legends_color = text_color ? text_color : "#FFF",
        xMinRange = chartConfig["x_min_range"] ? chartConfig["x_min_range"] : 3600000;

    var chart_options = {
        chart: {
            zoomType: 'x',
            type: chartConfig.type
        },
        title: {
            // text: chartConfig.name
            text: ""
        },
        credits: {
            enabled: false
        },
        legend:{
            itemDistance : 15,
            itemMarginBottom : 5,
            borderColor : legends_color,
            borderWidth : "1",
            borderRadius : "8",
            itemStyle: {
                color: legends_color,
                fontSize : '12px'
            }
        },
        // exporting:{
        //     url:'http://localhost:8080/highcharts-export-web/'
        // },
        tooltip: {
            // headerFormat: '{point.x:%e/%m/%Y (%b)  %l:%M %p}<br>',
            // pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b><br/>',
            formatter: function () {
                var this_date = new Date(this.x),
                    tooltip_string = "";

                if (this.x && this_date !== 'Invalid Date') {
                    var date_str_options = {
                        timezone : "Asia/Kolkata",
                        year: 'numeric',
                        month : 'numeric',
                        day : 'numeric',
                        hour : 'numeric',
                        minute : 'numeric',
                        hour12 : true
                    };

                    try {
                        tooltip_string = '<b>' + this_date.toLocaleString(date_str_options).toUpperCase()+ '</b>';
                    } catch(e) {
                        tooltip_string = '<b>' + this_date.toLocaleString()+ '</b>';
                    }
                } else {
                    var key_name = this.point.series.name ? this.point.series.name : this.key;
                    tooltip_string = '<b>' + key_name+ '</b>';
                }
                if (this.points && this.points.length > 0) {
                    for(var i=0;i<this.points.length;i++) {
                        tooltip_string += '<br/><span style="color:' + this.points[i].series.color + '"> \
                                          '+this.points[i].series.name+'</span>: <strong>' +this.points[i].y+'</strong>';
                    }
                } else {
                    tooltip_string += '<br/><span style="color:' + this.point.color + '">\
                                      ' + this.point.name + '</span>: <strong>' + this.point.y + '</strong>';
                }

                return tooltip_string;
            },
            shared: true,
            crosshairs: true,
            useHTML: true,
            valueSuffix: chartConfig.valuesuffix
        },
        xAxis: {
            title: {
                text: "Time"
            },
            type: 'datetime',
            minRange: xMinRange,
            dateTimeLabelFormats: {
                millisecond: '%H:%M:%S.%L',
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%e. %b',
                week: '%e. %b',
                month: '%b \'%y',
                year: '%Y'
            }
        },
        yAxis: {
            title : {
                text : chartConfig.valuetext
            },
            reversed : is_y_inverted
        },
        plotOptions : {
            column : {
                borderWidth : 0
            },
            bar : {
                borderWidth : 0
            }
        },
        series: chartConfig.chart_data
    };

    try {
        if (need_extra_config) {
            chart_options["yAxis"]["max"] = 100;
            chart_options["plotOptions"]["series"] = {stacking: 'normal'};
        }
    } catch(e) {
        // pass
    }

    var chart_instance = $('#'+dom_id+'_chart').highcharts(chart_options);

    callback(true);
}

/**
 * This function creates & returns table structur(with data) html
 * @method createTableHtml_nocout
 * @param dom_id {String}, It contains the table dom element ID
 * @param table_headers {Array}, It contains the headers object array for table
 * @param table_data {Array}, It contains the data object array for table
 */
function createTableHtml_nocout(dom_id, table_headers, table_data) {

    var table_string = "",
        grid_headers = table_headers,
        table_id = dom_id ? dom_id : "table1";

    if ($("#" + table_id).length > 0) {
        $("#" + table_id).dataTable().fnDestroy();
        $("#" + table_id).remove();
    }

    table_string += '<table id="' + table_id + '" class="datatable table table-striped table-bordered table-hover table-responsive"><thead>';
    /*Table header creation start*/
    for (var i = 0; i < grid_headers.length; i++) {
        table_string += '<td><b>' + grid_headers[i].toUpperCase() + '</b></td>';
    }

    table_string += '</thead><tbody>';
    /*Table header creation end*/

    /*Table data creation start*/
    for (var j = 0; j < table_data.length; j++) {
        table_string += '<tr>';
        for (var i = 0; i < grid_headers.length; i++) {
            table_string += '<td>'+table_data[j][grid_headers[i]]+'</td>';
        }
        table_string += '</tr>';
    }
    /*Table data creation End*/

    table_string += '</tbody></table>';

    // return tbale string
    return table_string;
}

/**
 * This function creates & returns table structur(with data) html
 * @method createTableHtml_nocout
 * @param dom_id {String}, It contains the table dom element ID.
 * @param chartObj {Array}, It contains the chart data info object array.
 */
function createChartDataTableHtml_nocout(dom_id, chartObj) {

    var table_id = dom_id ? dom_id : "table1";

    if ($("#" + table_id).length > 0) {
        $("#" + table_id).dataTable().fnDestroy();
        $("#" + table_id).remove();
    }

    var data_in_table = "<table id='" + table_id + "' class='datatable table table-striped table-bordered table-hover table-responsive'><thead><tr>";

    /*Make table headers*/
    for (var i = 0; i < chartObj.length; i++) {
        data_in_table += '<td colspan="2" align="center"><b>' + chartObj[i].name + '</b></td>';
    }
    data_in_table += '</tr><tr>';

    for (var i = 0; i < chartObj.length; i++) {
        data_in_table += '<td><em>Time</em></td><td><em>Value</em></td>';
    }

    data_in_table += '</tr></thead><tbody>';
    /*Table header creation end*/

    var data = chartObj[0].data;

    for (var j = 0; j < data.length; j++) {
        data_in_table += '<tr>';

        for (var i = 0; i < chartObj.length; i++) {
            var inner_data = chartObj[i].data[j],
                time_val = "",
                val = "";
            if (inner_data) {
                if (inner_data instanceof Array) {
                    time_val = new Date(inner_data[0]).toLocaleString();
                    val = inner_data[1];
                } else {
                    time_val = new Date(inner_data.x).toLocaleString();
                    val = inner_data.y;
                }
            }
            data_in_table += '<td>' + time_val + '</td><td>' + val + '</td>';
        }
        
        data_in_table += '</tr>';
    }

    data_in_table += '</tbody>';
    data_in_table += '</table>';

    return data_in_table;
}

/**
 * This function triggers when live poll button is clicked. It fetched the live polled value & create or update sparkline chart
 * @method nocout_livePollCurrentDevice
 * @param service_name {String}, It is the name of current service
 * @param ds_name {String}, It is the name of current data source
 * @param device_name {Array}, It is the list of device names(right now we have only one device name)
 * @param container_dom_id {String}, It is the dom id in of last updated block div in which the chart is to be prepared.
 * @param sparkline_dom_id {String}, It is the dom id in which sparkline chart is to be created
 * @param hidden_input_dom_id {String}, It is the dom id(input element) in which sparkline chart data is to be saved
 * @param polled_val_shown_dom_id {String}, It is the dom id in which the latest polled value is to be shown.
 */
function nocout_livePollCurrentDevice(
    service_name,
    ds_name,
    device_name,
    container_dom_id,
    sparkline_dom_id,
    hidden_input_dom_id,
    polled_val_shown_dom_id,
    show_sparkline_chart,
    callback
) {
    // Make Ajax Call
    perf_page_live_polling_call = $.ajax({
        url : base_url+"/device/lp_bulk_data/?service_name=" + service_name + "&devices=" + JSON.stringify(device_name) + "&ds_name="+ds_name,
        type : "GET",
        success : function(response) {
            
            var result = "";
            // Type check of response
            if (typeof response == 'string') {
                result = JSON.parse(response);
            } else {
                result = response;
            }

            if (result.success == 1) {

                var fetched_val = result.data.devices[device_name] ? result.data.devices[device_name]['value'] : "",
                    shown_val = "",
                    current_val_html = "",
                    ds_key = result.data.meta ? result.data.meta : "",
                    data_type = ds_key && ds_key["data_source_type"] ? ds_key["data_source_type"] : "numeric",
                    chart_type = ds_key && ds_key["chart_type"] ? ds_key["chart_type"] : "column",
                    chart_color = ds_key && ds_key["chart_color"] ? ds_key["chart_color"] : "#70AFC4",
                    warning_threshold = ds_key && ds_key["warning"] ? ds_key["warning"] : "",
                    critical_threshold = ds_key && ds_key["critical"] ? ds_key["critical"] : "",
                    dateObj = new Date(),
                    epoch_time = dateObj.getTime(),
                    month = Number(dateObj.getMonth()) + 1,
                    date_str = dateObj.getDate() + "-" + month + "-" + dateObj.getFullYear(),
                    time_str = dateObj.getHours() + ":" + dateObj.getMinutes() + ":" + dateObj.getSeconds(),
                    current_time = date_str + " " + time_str,
                    fetched_data = true;

                if (fetched_val != "" && fetched_val != "NA" && fetched_val != null) {
                    
                    if (typeof fetched_val == 'object') {
                        fetched_val = fetched_val[0];
                    }

                    // If call is from single device page then proceed else return data
                    if (container_dom_id && show_sparkline_chart) {
                        // Create Fetched val html with time stamp
                        current_val_html += '<li style="display:none;">' + val_icon + ' ' + fetched_val;
                        current_val_html += '<br/>' + time_icon + ' ' + current_time + '</li>';
                        
                        // Prepend new fetched val & time li
                        $("#" + container_dom_id+" #perf_output_table tr td:last-child ul#perf_live_poll_vals").html(current_val_html);
                        // Animation effect to added li
                        $("#" + container_dom_id+" #perf_output_table tr td:last-child ul#perf_live_poll_vals li").slideDown('slow');


                        /******************** Create Sparkline Chart for numeric values ********************/
                        if (!isNaN(Number(fetched_val))) {
                            var existing_val = $("#" + container_dom_id + " #" + hidden_input_dom_id).val(),
                                new_values_list = "";

                            if (existing_val) {
                                new_values_list = existing_val + "," + fetched_val;
                            } else {
                                new_values_list = fetched_val;
                            }
                            
                            // Update the value in input field
                            $("#" + container_dom_id + " #" + hidden_input_dom_id).val(new_values_list);

                            // Make array of values from "," comma seperated string
                            var new_chart_data = new_values_list.split(",");

                            /*Plot sparkline chart with the fetched polling value*/
                            $("#" + container_dom_id + " #" + sparkline_dom_id).sparkline(new_chart_data, {
                                type: "line",
                                lineColor: "blue",
                                spotColor : "orange",
                                defaultPixelsPerValue : 10
                            });
                        }
                    } else {
                        fetched_data = {
                            "val" : fetched_val,
                            "time" : current_time,
                            "epoch_time" : epoch_time ? epoch_time : "",
                            "type" : data_type ? data_type : "numeric",
                            "chart_type" : chart_type ? chart_type : "column",
                            "chart_color" : chart_color ? chart_color : "#70AFC4",
                            "warning_threshold" : warning_threshold,
                            "critical_threshold" : critical_threshold
                        };
                    }
                } else {
                    if (!fetched_val) {
                        fetched_val = "N/A";
                    }

                    fetched_data = {
                        "val" : fetched_val,
                        "time" : current_time,
                        "epoch_time" : epoch_time ? epoch_time : "",
                        "type" : data_type ? data_type : "numeric",
                        "chart_type" : chart_type ? chart_type : "column",
                        "chart_color" : chart_color ? chart_color : "#70AFC4",
                        "critical_threshold" : critical_threshold,
                        "warning_threshold" : warning_threshold
                    };
                }
                callback(fetched_data);
            } else {
                $.gritter.add({
                    // (string | mandatory) the heading of the notification
                    title: 'Live Polling',
                    // (string | mandatory) the text inside the notification
                    text: result.message,
                    // (bool | optional) if you want it to fade out on its own or just sit there
                    sticky: false
                });
                
                callback(false);
            }
        },
        error : function(err) {
            if ($.trim(err.statusText) != 'abort') {    
                $.gritter.add({
                    // (string | mandatory) the heading of the notification
                    title: 'Live Polling',
                    // (string | mandatory) the text inside the notification
                    text: err.statusText,
                    // (bool | optional) if you want it to fade out on its own or just sit there
                    sticky: false
                });

                // If call is not from single device page then proceed
                callback(false);
            }
        },
        complete : function() {
            // If call is from single device page then proceed else return data
            if (container_dom_id) {
                // Enable the "Poll Now" button
                $("#" + container_dom_id + " #perf_output_table tr td:nth-child(2) .perf_poll_now").button("complete");
            }
        }
    });
}

/**
 * This function concat base url & given url as per the "/" cases
 * @method getCompleteUrl
 * @param api_url {String}, It contails any url string
 * @return complete_url {String}, It contails the concated url with base_url
 */
function getCompleteUrl(api_url) {

    var complete_url = "",
        url_connector = "";

    if (!api_url) {
         return complete_url;
    }

    if (!base_url) {
        base_url = getBaseUrl();
    }

    if (api_url[0] != "/") {
        url_connector = "/";
    }

    complete_url = base_url+url_connector+api_url;

    return complete_url;
}

/**
 * This function returns the base url of the webpage
 * @method getBaseUrl
 * @return complete_url {String}, It contails the base url of the webpage
 */
function getBaseUrl() {

    var webpage_base_url = "",
        page_origin = window.location.origin;
    /*Set the base url of application for ajax calls*/
    if (page_origin) {
        webpage_base_url = page_origin;
    } else {
        var page_protocol = window.location.protocol,
            page_hostname = window.location.hostname;
            page_port = "";

        try {
            page_port = window.location.port;
        } catch(e) {
            // console.log(e);
        }

        webpage_base_url = page_protocol + "//" + page_hostname + (page_port ? ':' + page_port: '');
    }

    return webpage_base_url;
}

/**
 * This function recursively performs poll now functionality as per the selected criteria
 * @method recursivePolling
 */
function recursivePolling() {

    var active_tab_obj = nocout_getPerfTabDomId(),
        tab_id = active_tab_obj["active_dom_id"];

    if (remainingPollCalls > 0) {
        if (isPollingPaused == 0) {
            var timeout_time = pollingInterval*1000;
            // Call function to fetch polled data for selected devices
            initSingleDevicePolling(function(result) {
                remainingPollCalls--;
                if(remainingPollCalls == 0) {
                    timeout_time = 10;
                }

                pollCallingTimeout = setTimeout(function() {
                    recursivePolling();
                },timeout_time);
            });
        } else {
            if ($("#" + tab_id + "_block .poll_play_btn").hasClass("disabled")) {
                $("#" + tab_id + "_block .poll_play_btn").removeClass("disabled");
            }
            $(".poll_play_btn").button("complete");
            clearTimeout(pollCallingTimeout);
        }
    } else {
        nocout_stopPollNow();
    }
}

/**
 * This function triggers when live poll functionality trigger from single device page
 * @method initSingleDevicePolling
 */
function initSingleDevicePolling(callback) {

    var sparkline_dom_id = 'perf_live_poll_chart',
        hidden_input_dom_id = 'perf_live_poll_input',
        polled_val_shown_dom_id = "last_polled_val",
        current_active_tab_url = $(".top_perf_tab_content div.active ul.left_tabs_container li.active a").attr("url"),
        service_name = "",
        ds_name = "",
        container_id = "",
        block_dom_id_str = $(".top_perf_tab_content div.active ul.left_tabs_container li.active a").attr("href");

    if (current_active_tab_url && current_active_tab_url.indexOf("service/") > -1 && current_active_tab_url.indexOf("service_data_source/") > -1 ) {
        service_name = current_active_tab_url ? current_active_tab_url.split("service/")[1].split("/")[0] : "";
        ds_name = current_active_tab_url ? current_active_tab_url.split("service_data_source/")[1].split("/")[0] : "";
    }

    if (block_dom_id_str && block_dom_id_str.indexOf("#") > -1) {
        container_id = "last_updated_"+block_dom_id_str.split("#")[1];
    }

    if (device_name.length > 0 && service_name.length > 0 && ds_name.length > 0) {
        // Disable the "Poll Now" button
        $("#"+container_id+" #perf_output_table tr td:nth-child(2) .perf_poll_now").button("loading");

        // Call function to fetch live polling data
        nocout_livePollCurrentDevice(
            service_name,
            ds_name,
            [device_name],
            container_id,
            sparkline_dom_id,
            hidden_input_dom_id,
            polled_val_shown_dom_id,
            false,
            function(response) {
                x = new Date()
                response = {
                            "val" : [62],
                            "time" : '14th July 1991',
                            "epoch_time" : x.getTime(),
                            "type" : "numeric",
                            "chart_type" : "column",
                            "chart_color" : "#70AFC4",
                            "warning_threshold" : "",
                            "critical_threshold" : ""
                        };

                if (!(response instanceof Array)) {
                    response = [response];
                }

                if (response) {
                    checkpollvalues(response, true, function(response) {
                        callback(response);
                    });
                } else {
                    callback(false);
                }
            }
        );
    } else {
        callback(false);
    }
}

/**
 * This function draws chart/table as per the poll now response
 * @param  {[type]}   result      [description]
 * @param  {Boolean}  is_new_data [description]
 * @param  {Function} callback    [description]
 * @return {[type]}               [description]
 */
function checkpollvalues(result, is_new_data, callback) {
    
    var active_tab_obj = nocout_getPerfTabDomId(),
        dom_id = active_tab_obj["active_dom_id"] ? active_tab_obj["active_dom_id"] : "",
        block_title = $.trim($(".top_perf_tab_content div.active ul.left_tabs_container li.active a").text()),
        draw_table = false;

    if(!poll_now_data_dict[dom_id]) {
        poll_now_data_dict[dom_id] = [];
    }

    if (is_new_data) {
        poll_now_data_dict[dom_id] = poll_now_data_dict[dom_id].concat(result);
    }

    var draw_type = $("input[name='item_type']:checked").val();

    if (!draw_type) {
        draw_type = "chart";
    }

    var chart_config = {
            "type" : "column",
            "value_text": block_title,
            "x_min_range" : 10000,
            "valuesuffix": " %",
            "chart_data": []
        },
        chart_data_list = {
            "warning" : {
                "color": 0,
                "name": "Warning Threshold",
                "type" : "line",
                "data" : []
            },
            "critical" : {
                "color": 0,
                "name": "Critical Threshold",
                "type" : "line",
                "data" : []
            },
            "normal" : {
                "color": 0,
                "name": block_title,
                "type" : "column",
                "data" : []
            }
        };

    for(var i=0;i<result.length;i++) {

        var fetched_val = result[i]['val'],
            fetch_warning_threshold =  result[i]['warning_threshold'],
            fetch_critical_threshold =  result[i]['critical_threshold'];

        if(fetched_val && fetched_val instanceof Array) {
            fetched_val = fetched_val[0];
        }

        if(fetch_warning_threshold && fetch_warning_threshold instanceof Array) {
            fetch_warning_threshold = fetch_warning_threshold[0];
        }

        if(fetch_critical_threshold && fetch_critical_threshold instanceof Array) {
            fetch_critical_threshold = fetch_critical_threshold[0];
        }

        if (result[i].type.toLowerCase() == 'numeric' && draw_type == 'chart') {

            // Hide display type option from only table tabs
            if ($("#display_type_container").hasClass("hide")) {
                $("#display_type_container").removeClass("hide")
            }

            // Update the chart type & data key as per the given params
            chart_config["type"] = result[i]["chart_type"];
            
            if (fetch_warning_threshold) {
                if(!chart_data_list["warning"]["color"]) {
                    chart_data_list["warning"]["color"] = "#FF0000";
                }
                chart_data_list["warning"]["data"].push({
                    "color": "#FF0000",
                    "y": Number(fetch_warning_threshold),
                    "name": "Warning Threshold",
                    "x": result[i]['epoch_time']
                });
            }

            if (fetch_critical_threshold) {
                if(!chart_data_list["critical"]["color"]) {
                    chart_data_list["critical"]["color"] = "#CCCCCC";
                }
                chart_data_list["critical"]["data"].push({
                    "color": "#CCCCCC",
                    "y": Number(fetch_critical_threshold),
                    "name": "Critical Threshold",
                    "x": result[i]['epoch_time']
                });
            }

            if(!chart_data_list["normal"]["color"]) {
                chart_data_list["normal"]["color"] = result[i]['chart_color'];
            }

            chart_data_list["normal"]["type"] = result[i]["chart_type"];

            chart_data_list["normal"]["data"].push({
                "color": result[i]['chart_color'],
                "y": Number(fetched_val),
                "name": block_title,
                "x": result[i]['epoch_time']
            });
        } else {
            if(result[i].type.toLowerCase() == 'numeric' && dom_id.indexOf('_status_') == -1 && dom_id.indexOf('_inventory_') == -1) {
                // Hide display type option from only table tabs
                if ($("#display_type_container").hasClass("hide")) {
                    $("#display_type_container").removeClass("hide")
                }
            }
            draw_table = true;
        }

        if (draw_table) {
            var date_time_str = result[i]['time'],
                grid_headers = [
                    "service_name",
                    "value",
                    "time",
                    "warning_threshold",
                    "critical_threshold"
                ],
                table_data = [{
                    "service_name": block_title,
                    "value": fetched_val,
                    "time": date_time_str,
                    "warning_threshold": fetch_warning_threshold,
                    "critical_threshold": fetch_critical_threshold
                }];

            if ($("#other_perf_table").length == 0) {
                initNormalDataTable_nocout(
                    'other_perf_table',
                    grid_headers,
                    dom_id
                );
            }

            // Call addDataToNormalTable_nocout (utilities) function to add data to initialize datatable
            addDataToNormalTable_nocout(
                table_data,
                grid_headers,
                'other_perf_table'
            );
        }
    }

    if (draw_type == 'chart') {
        for (key in chart_data_list) {
            if (chart_data_list[key] && chart_data_list[key]["data"].length) {
                chart_config["chart_data"].push(chart_data_list[key]);
            }
        }

        if (!$('#' + dom_id+ '_chart').highcharts()) {
            createHighChart_nocout(chart_config,dom_id, false, false, function(status) {
                // pass
            });
        } else {
            addPointsToChart_nocout(chart_config.chart_data,dom_id);
        }
    }
    
    if ($('#' + dom_id+ '_chart').highcharts()) {
        $('#' + dom_id + '_chart').highcharts().redraw();
    }
    callback(true);
}

/**
 * This function toggles the current state of poll now content(chart/table) as per the item type selection
 * @method nocout_togglePollNowContent
 */
function nocout_togglePollNowContent() {

    var active_tab_obj = nocout_getPerfTabDomId(),
        tab_id = active_tab_obj["active_dom_id"] ? active_tab_obj["active_dom_id"] : "";

    if(poll_now_data_dict[tab_id] && poll_now_data_dict[tab_id].length) {
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

            if ($("#other_perf_table").length > 0) {
                $("#other_perf_table").dataTable().fnDestroy();
                $("#other_perf_table").remove();
            }
        } catch(e) {
            // console.log(e);
        }
        checkpollvalues(poll_now_data_dict[tab_id], false, function(response) {
            
        });
    }
}

/**
 * This function returns the active tab dom id & API url
 * @method nocout_getPerfTabDomId
 * @return {Object} It contains the active tab dom ID & active tab API url
 */
function nocout_getPerfTabDomId() {

    var response_dict = {
            "active_dom_id" : "",
            "active_tab_api_url" : ""
        },
        top_tab_content_href = $(".top_perf_tabs > li.active a").attr("href"),
        top_tab_content_id = top_tab_content_href.split("#").length > 1 ? top_tab_content_href.split("#")[1] : top_tab_content_href.split("#")[0];

    if(show_historical_on_performance || is_perf_polling_enabled) {
        var left_active_tab_href = $("#"+top_tab_content_id+" .left_tabs_container li.active a").attr("href"),
            left_tab_content_id = left_active_tab_href.split("#").length > 1 ? left_active_tab_href.split("#")[1] : left_active_tab_href.split("#")[0];

        var active_inner_tab = $("#"+left_tab_content_id+" .inner_inner_tab li.active a");
        
        response_dict["active_dom_id"] = active_inner_tab.attr("id").slice(0, -4);
        response_dict["active_tab_api_url"] = active_inner_tab.attr("url");
    } else {
        var left_active_tab_anchor = $("#"+top_tab_content_id+" .left_tabs_container li.active a"),
            active_inner_tab = $('.top_perf_tab_content div.active .inner_tab_container .nav-tabs li.active a');

        response_dict["active_dom_id"] = left_active_tab_anchor.attr("id").slice(0, -4);
        response_dict["active_tab_api_url"] = left_active_tab_anchor.attr("url");
    }

    return response_dict;
}

/**
 * This function stops active recursive polling
 * @method nocout_stopPollNow
 */
function nocout_stopPollNow() {

    // Update the flag
    is_polling_active = false;

    var active_tab_obj = nocout_getPerfTabDomId(),
        tab_id = active_tab_obj["active_dom_id"];

    if($("#" + tab_id + "_block .play_pause_btns").hasClass("disabled")) {
        $("#" + tab_id + "_block .play_pause_btns").removeClass("disabled");
    }
    
    /*Disable poll interval & max interval dropdown*/
    $("#" + tab_id + "_block .poll_interval").removeAttr("disabled");
    $("#" + tab_id + "_block .poll_maxInterval").removeAttr("disabled");

    if($("#" + tab_id + "_block .play_pause_btns").hasClass("disabled")) {
        $("#" + tab_id + "_block .play_pause_btns").removeClass("disabled");
    }

    if($("#fetch_polling").hasClass("disabled")) {
        $("#fetch_polling").removeClass("disabled");
    }

    if(pollCallingTimeout) {
        clearTimeout(pollCallingTimeout);
        pollCallingTimeout = "";
    }

    pollingInterval = 10;
    pollingMaxInterval = 1;
    remainingPollCalls = 0;
    isPollingPaused = 0;
    $("#" + tab_id + "_block .poll_play_btn").button('complete');

    if($("#" + tab_id + "_block .perf_poll_now").hasClass("disabled")) {
        $("#" + tab_id + "_block .perf_poll_now").removeClass("disabled");
    }
}

/**
 * This function pause active recursive polling
 * @method nocout_pausePollNow
 */
function nocout_pausePollNow() {

    // Update the flag
    is_polling_active = false;

    var active_tab_obj = nocout_getPerfTabDomId(),
        tab_id = active_tab_obj["active_dom_id"];

    if($("#" + tab_id + "_block .play_pause_btns").hasClass("disabled")) {
        $("#" + tab_id + "_block .play_pause_btns").removeClass("disabled");
    }
    if(remainingPollCalls > 0) {
        if(!$("#" + tab_id + "_block .poll_pause_btn").hasClass("disabled")) {
            $("#" + tab_id + "_block .poll_pause_btn").addClass("disabled");
        }

        //stop perf calling
        if(pollCallingTimeout) {
            clearTimeout(pollCallingTimeout);
            pollCallingTimeout = "";
        }
        isPollingPaused = 1;
        $("#" + tab_id + "_block .poll_play_btn").button('complete');        
    } else {
        bootbox.alert("Please run polling first.");
    }
}

/**
 * This function destroy datatable with given dom id
 * @method nocout_destroyDataTable
 */
function nocout_destroyDataTable(domId) {

    if (domId && $('#' + domId).length > 0) {
        $("#" + domId).dataTable().fnDestroy();
        $("#" + domId).remove();
    }
}

/**
 * This function destroy highcharts with given dom id
 * @method nocout_destroyHighcharts
 */
function nocout_destroyHighcharts(domId) {
    try {
        if (domId && $("#" + domId + "_chart").highcharts()) {
            var chart = $("#" + domId + "_chart").highcharts(),
                chart_series = chart.series;

            if (chart_series && chart_series.length > 0) {
                // Remove series from highchart
                while(chart_series.length > 0) {
                    chart_series[0].remove(true);
                }
            }
            // Destroy highchart
            $("#" + domId + "_chart").highcharts().destroy();
        }

        // Clear HTML
        $("#" + domId + "_chart").html("");

        if (domId && $("#" + domId + "_bottom_table").length) {
            $("#" + domId + "_bottom_table").html("");
        }

    } catch(e) {
        // console.log(e);
    }
}