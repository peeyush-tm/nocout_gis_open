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
    header_extra_param = "{'download_excel': 'yes' }",
    na_list = ['NA', 'N/A', 'na', 'n/a'],
    legends_gradient_string = 'background: xxxx; \
                               background: -moz-linear-gradient(left, xxxx 0%, yyyy 100%); \
                               background: -webkit-gradient(linear, left top, right top, color-stop(0%,xxxx), color-stop(44%,yyyy), color-stop(100%,yyyy)); \
                               background: -webkit-linear-gradient(left, xxxx 0%,yyyy 100%); \
                               background: -o-linear-gradient(left, xxxx 0%,yyyy 100%); \
                               background: -ms-linear-gradient(left, xxxx 0%,yyyy 100%); \
                               background: linear-gradient(to right, xxxx 0%,yyyy 100%); \
                               filter: progid:DXImageTransform.Microsoft.gradient( startColorstr="xxxx", endColorstr="yyyy",GradientType=1 );',
    default_legends_bg = '#343435',
    parallel_calling_len = 3,
    birdeye_start_counter = 0,
    birdeye_end_counter = parallel_calling_len,
    is_mouse_out = true;


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
        // status = info.status ? info.status.toUpperCase() : "Unknown",
        status = info.pl_status ? info.pl_status.toUpperCase() : "Unknown",
        severity_up = info.severity && info.severity.ok ? info.severity.ok : 0,
        severity_warn = info.severity && info.severity.warn ? info.severity.warn : 0,
        severity_crit = info.severity && info.severity.crit ? info.severity.crit : 0,
        severity_unknown = info.severity && info.severity.unknown ? info.severity.unknown : 0;

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
                    <td data-severity="ok" title="Click to see all up services" class="severity_block vAlign_middle" style="background:' + ok_severity_color + ';">' + severity_up + '</td>\
                    <td data-severity="warning" title="Click to see all warning services" class="severity_block vAlign_middle" style="background:' + orange_color + ';">' + severity_warn + '</td>\
                    <td data-severity="critical" title="Click to see all critical services" class="severity_block vAlign_middle" style="background:' + red_color + ';">' + severity_crit + '</td>\
                    <td data-severity="unknown" title="Click to see all unknown services" class="severity_block vAlign_middle" \
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

    /********** Service Status Without Live Polling  - START     ********************/
    if ($.trim(info.last_updated) !== "" || $.trim(info.perf) !== "" || $.trim(info.status) !== "") {
        var last_updated = info.last_updated ? info.last_updated : "N/A",
            perf = info.perf ? info.perf : "N/A",
            status = info.status ? info.status.toUpperCase() : "",
            severity_style_obj = nocout_getSeverityColorIcon(status)
            txt_color = severity_style_obj.color ? severity_style_obj.color : "",
            fa_icon_class = severity_style_obj.icon ? severity_style_obj.icon : "fa-circle",
            inner_status_html = '';

        var view_type = $.trim($('input[name="service_view_type"]:checked').val());

        if (view_type == 'unified') {
            inner_status_html = '<table id="perf_output_table" class="table table-responsive table-bordered">\
                                  <tr style="color:'+txt_color+';"><td>\
                                  <i title = "' + status + '" class="fa ' + fa_icon_class + '" \
                                  style="vertical-align: middle;"> </i> \
                                  <strong>Current Status:</strong> ' + status + '</td>\
                                  <td><strong>Updated At:</strong> ' + last_updated + '</td>\
                                  </tr>\
                                  </table><div class="clearfix"></div>';
        } else {
            if (domElement.indexOf('power_content') > -1){
                if (perf.toLowerCase().indexOf('up') == -1){
                    $('#power_send_reset').addClass('disabled')
                    $('#power_send_joji').addClass('disabled')
                }
                inner_status_html = '<table id="perf_output_table" class="table table-responsive table-bordered">\
                                  <tr style="color:'+txt_color+';"><td>\
                                  <i title = "' + status + '" class="fa ' + fa_icon_class + '" \
                                  style="vertical-align: middle;"> </i> \
                                  <strong>Last Received Status: </strong> ' + perf + '</td>\
                                  <td><strong>Updated At: </strong> ' + last_updated + '</td>\
                                  </tr>\
                                  </table><div class="clearfix"></div>';  
            }
            else{
                inner_status_html = '<table id="perf_output_table" class="table table-responsive table-bordered">\
                                  <tr style="color:'+txt_color+';"><td>\
                                  <i title = "' + status + '" class="fa ' + fa_icon_class + '" \
                                  style="vertical-align: middle;"> </i> \
                                  <strong>Performance Output: </strong> ' + perf + '</td>\
                                  <td><strong>Updated At: </strong> ' + last_updated + '</td>\
                                  </tr>\
                                  </table><div class="clearfix"></div>';
            }
        }

        $("#" + domElement).html(inner_status_html);
    } else {
        $("#" + domElement).html("");
    }
}


/**
 * This function adds data to initialized datatable as per given params
 * @method addDataToNormalTable_nocout
 * @param table_data {Array}, It contains the data object array for table
 * @param table_headers {Array}, It contains the headers object array for table
 * @param table_id {String}, It contains the table dom element ID
 */
function addDataToNormalTable_nocout(table_data, table_headers, table_id, service_id) {

    for (var j = 0; j < table_data.length; j++) {
        var row_val = [];
        for (var i = 0; i < table_headers.length; i++) {
            var insert_val = typeof(table_data[j][table_headers[i]]) != 'undefined' ? table_data[j][table_headers[i]] : "";
            row_val.push(insert_val);
        }
        $('#'+ service_id +  '_' + table_id).dataTable().fnAddData(row_val);
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

    if(!$('#' + service_id + '_legends_block').hasClass('hide')) {
        $('#' + service_id + '_legends_block').addClass('hide');
    }

    var table_string = "",
        grid_headers = headers,
        excel_columns = [];

    // Destroy Datatable
    if ($('.top_perf_tabs > li.active a').attr('id').indexOf('bird') == -1) {
        nocout_destroyDataTable('other_perf_table');
        nocout_destroyDataTable('perf_data_table');
    }

    table_string += '<table id="' + service_id + '_'+ table_id + '" class="datatable table table-striped table-bordered table-hover table-responsive"><thead>';
    /*Table header creation start*/
    for (var i = 0; i < grid_headers.length; i++) {
        table_string += '<th><b>' + grid_headers[i].toUpperCase() + '</b></th>';
        excel_columns.push(i);
    }
    table_string += '</thead></table>';
    /*Table header creation end*/

    if (service_id) {
        $('#' + service_id + '_chart').html(table_string);
    }

    $("#" + service_id + '_'+ table_id).DataTable({
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
            var row_per_pages_selectbox = '#' + service_id + '_'+ table_id + '_wrapper div.dataTables_length label select',
                search_box = '#' + service_id + '_'+ table_id + '_wrapper div.dataTables_filter label input';
            // Update search txt box & row per pages dropdown style
            $(row_per_pages_selectbox + ' , ' + search_box).addClass("form-control");
            $(row_per_pages_selectbox + ' , ' + search_box).addClass("input-sm");
            $(row_per_pages_selectbox + ' , ' + search_box).css("max-width","150px");
        },
        bPaginate: true,
        bDestroy: true,
        aaSorting : [[2, 'desc']],
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

    var data_in_table = "<table id='" + service_id + '_' + table_id + "' \
                         class='datatable table table-striped table-bordered table-hover'><thead>";
        is_birdeye_view = false;

    if (typeof nocout_getPerfTabDomId != 'undefined' && typeof live_data_tab != 'undefined') {
        is_birdeye_view = clicked_tab_id.indexOf('bird') > -1;
    }

    if (!is_birdeye_view) {
        // Destroy Datatable
        nocout_destroyDataTable('other_perf_table');
        nocout_destroyDataTable('perf_data_table');
    }

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

    var service_name = updated_url.indexOf("/service/") && updated_url.split("/service/").length > 1 ? updated_url.split("/service/")[1].split("/")[0] : '[]';
        ds_name = updated_url.split("/service/").length > 1 ? updated_url.split("/service/")[1].split("/")[2] : '',
        get_param_string = updated_url.split("?")[1].split("&"),
        data_for = 'live',
        get_param_data = "",
        data_extra_param = "",
        applied_adv_filter = '[]';

    // append 'advance_filter' GET param to url if exists.
    if ($('#'+service_id+'_tab').attr('data_url') && !is_birdeye_view) {
        var filtering_url = $('#'+service_id+'_tab').attr('data_url');
        applied_adv_filter = filtering_url.indexOf('advance_filter=') ? filtering_url.split('advance_filter=')[1] : '[]';
        
        if (updated_url.indexOf('advance_filter=') > -1) {
            updated_url = updated_url.split('advance_filter=')[0];
        }

        if (updated_url.indexOf('?') > -1) {
            updated_url += '&advance_filter=' + applied_adv_filter
        } else {
            updated_url += '?advance_filter=' + applied_adv_filter
        }
    }

    for(var i=0;i<get_param_string.length;i++) {
        var splitted_string = get_param_string[i].split("=");
        if (splitted_string[1] != 'undefined') {
            if (i == get_param_string.length-1) {
                get_param_data += "'" + splitted_string[0] + "':'" + splitted_string[1] + "'";
            } else {
                get_param_data += "'" + splitted_string[0] + "':'" + splitted_string[1] + "',";
            }
        }
    }

    if ($(".top_perf_tabs").length > 0 && !is_birdeye_view && clicked_tab_id.indexOf('custom_dashboard') == -1) {
        var report_title = "";
        try {
            var top_tab_id = $(".top_perf_tabs > li.active a").attr('href'),
                left_tab_id = $(top_tab_id + " .left_tabs_container li.active a")[0].id,
                top_tab_text = $.trim($(".top_perf_tabs > li.active a")[0].text),
                left_tab_txt = $.trim($("#" +left_tab_id).text());
        } catch(e) {
            var top_tab_id = '#' + clicked_tab_id + '_tab',
                left_tab_id = $(top_tab_id + " .left_tabs_container li.active a")[0].id,
                top_tab_text = $.trim($(".top_perf_tabs > li.active a")[0].text),
                left_tab_txt = $.trim($("#" +left_tab_id).text());
        }

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
            service_id + '_' + table_id,
            tableheaders,
            updated_url,
            false,
            table_title,
            app_name,
            header_class_name,
            data_class_name,
            header_extra_param,
            data_extra_param,
            [],
            applied_adv_filter
        );

    } else {
        /*Call createDataTable function to create the data table for specified dom element with given data*/
        dataTableInstance.createDataTable(
            service_id + '_' + table_id,
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
                            var formatted_datetime = getFormattedDate(inner_data[0]);
                            
                            row_val.push(formatted_datetime);
                            var chart_val = inner_data[1];
                            row_val.push(chart_val);
                        }
                    } else if (inner_data.constructor === Object) {
                        if (inner_data.x) {
                            var formatted_datetime = getFormattedDate(inner_data.x);
                            row_val.push(formatted_datetime);
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
        if (typeof dataset_list != 'undefined' && dataset_list.length) {
            $('#'+dom_id+'_chart').highcharts().series[i].setData(dataset_list[i]['data'],false,false);
        } else {
            for (var j = 0; j < pointArray[i].data.length; j++) {
                $('#'+dom_id+'_chart').highcharts().series[i].addPoint(pointArray[i].data[j], false, false, false);
            }   
        }
    }

    if (pointArray && pointArray.length) {
        // Redraw the chart
        $('#'+dom_id+'_chart').highcharts().redraw();
        // Update legends
        prepareValueLegends($('#'+dom_id+'_chart').highcharts().series, dom_id);
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
        xMinRange = chartConfig["x_min_range"] ? chartConfig["x_min_range"] : 3600000,
        yAxisObj = '',
        is_display_name = typeof chartConfig['chart_display_name'] != 'undefined',
        exported_filename = '';

    try {
        exported_filename = is_display_name ? chartConfig.chart_display_name + '_' + current_device_ip : current_device_ip;
    } catch(e) {
        exported_filename = 'Performance Chart'
    }

    var reset_zoom_position = {x: -35, y: 0};

    // Create yAxis data as per the given params
    if (typeof chartConfig.valuetext == 'string' || chartConfig['is_single']) {
        var title_txt = chartConfig.valuetext;
        if (chartConfig['is_single']) {
            try {
                title_txt = chartConfig.valuetext.join(', ')
            } catch(e) {
                // console.error(e);
            }
        }
        yAxisObj = {
            title : {
                text : title_txt
            },
            reversed : is_y_inverted
        };
    } else if(chartConfig['valuetext'] && chartConfig['valuetext'].length) {
        if (chartConfig.valuetext.length > 1) {
            reset_zoom_position = {x: 15, y: 0};
        }
        yAxisObj = [];
        for(var i=0;i<chartConfig.valuetext.length;i++) {
            var opposite = false;
            if (i == chartConfig.valuetext.length -1) {
                opposite = true;
            }
            yAxisObj.push({
                title : {
                    text : chartConfig.valuetext[i]
                },
                reversed : is_y_inverted,
                opposite : opposite
            })
        }
    } else {
        yAxisObj = {
            title : {
                text : ''
            },
            reversed : is_y_inverted
        };
    }

    var chart_options = {
        chart: {
            zoomType: 'x',
            resetZoomButton: {
                position: reset_zoom_position
            },
            type: chartConfig.type,
            events : {
                load : function(evt) {
                    // set the background color of custom legends panel as per chart background color.
                    try {
                        var background_color = evt.currentTarget.options.chart.backgroundColor;

                        if (typeof background_color == 'string') {
                            $('.custom_legends_container').css('background-color', background_color);
                        } else {
                            var color_list = background_color.stops,
                                gradient_color = legends_gradient_string,
                                first_color = 'xxxx',
                                second_color = 'yyyy',
                                first_color_re = new RegExp(first_color, 'g'),
                                second_color_re = new RegExp(second_color, 'g');

                            gradient_color = gradient_color.replace(first_color_re, color_list[0][1]);
                            gradient_color = gradient_color.replace(second_color_re, color_list[1][1]);

                            $('.custom_legends_container').attr('style', gradient_color);
                        }
                    } catch(e) {
                        // console.error(e);
                        $('.custom_legends_container').css('background-color', default_legends_bg);
                    }

                    prepareValueLegends(evt.currentTarget.series, dom_id);
                },
                selection : function(evt) {
                    // Trigger after .5 second to get the exact values not the old one.
                    setTimeout(function() {
                        var is_zoom_in = evt.currentTarget.resetZoomButton;
                        prepareValueLegends(evt.currentTarget.series, dom_id, is_zoom_in);
                    }, 500);
                }
            }
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
        exporting:{
            // url:'http://localhost:8080/highcharts-export-web/',
            enabled : true,
            allowHTML: true,
            sourceWidth: 950,
            sourceHeight: 375,
            filename: exported_filename
        },
        tooltip: {
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
                        var formatted_time = getFormattedDate(this.x);
                        if (formatted_time) {                            
                            tooltip_string = '<b>' + formatted_time + '</b>';
                        } else {
                            tooltip_string = '<b>' + this_date.toLocaleString()+ '</b>';
                        }
                    } catch(e) {
                        tooltip_string = '<b>' + this_date.toLocaleString()+ '</b>';
                    }
                } else {
                    var key_name = this.point.series.name ? this.point.series.name : this.key;
                    tooltip_string = '<b>' + key_name+ '</b>';
                }

                if (this.points && this.points.length > 0) {
                    for(var i=0;i<this.points.length;i++) {
                        var color = this.points[i].series.color;
                        if (color && color == 'transparent') {
                            color = '#70AFC4';
                        }

                        tooltip_string += '<br/><span style="color:' + color + '"> \
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
        yAxis: yAxisObj,
        plotOptions : {
            column : {
                borderWidth : 0,
                borderColor : ''
            },
            bar : {
                borderWidth : 0,
                borderColor : ''
            }
        },
        series: chartConfig.chart_data
    };

    try {
        if (need_extra_config) {
            chart_options["yAxis"]["max"] = 100;
            chart_options["plotOptions"]["series"] = {stacking: 'normal'};
        }

        if ($('.top_perf_tabs > li.active a').attr('id').indexOf('bird') > -1) {
            chart_options["exporting"] = {};
            chart_options["exporting"]["enabled"] = false;
        }
    } catch(e) {
        // pass
    }

    if ($('#'+dom_id+'_chart').hasClass('charts_block')) {
        if (dom_id.indexOf('ping') > -1) {
            $('#'+dom_id+'_chart').attr('style', 'height:350px;');
        } else {
            $('#'+dom_id+'_chart').attr('style', 'height:250px;');
        }
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
        table_string += '<th><b>' + grid_headers[i].toUpperCase() + '</b></th>';
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
        data_in_table += '<th colspan="2" style="text-align: center;"><b>' + chartObj[i].name + '</b></th>';
    }
    data_in_table += '</tr><tr>';

    for (var i = 0; i < chartObj.length; i++) {
        var name = '';
        try {
            splitted_chart_name = chartObj[i].name.split(':')
            name = $.trim(splitted_chart_name[0]);

            if (splitted_chart_name.length > 1) {
                if (splitted_chart_name[1].indexOf('PMP1') > -1) {
                    name += ': PMP1'
                } else if (splitted_chart_name[1].indexOf('PMP2') > -1) {
                    name += ': PMP2'
                } else if (splitted_chart_name[1].indexOf('(') > -1) {
                    name += ' (' + splitted_chart_name[1].split('(')[1]
                }
            }

        } catch(e) {
            name = $.trim(chartObj[i].name);
        }
        data_in_table += '<th><em>Time: '+ name +'</em></th><th><em>Value: '+ name +'</em></th>';
    }

    data_in_table += '</tr></thead><tbody>';
    /*Table header creation end*/

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
 * @param extra_info_obj {Object}, It contains the extra info required in further functionality.
 */
function nocout_livePollCurrentDevice(
    service_name,
    ds_name,
    device_name,
    extra_info_obj,
    callback
) {

    var container_dom_id = extra_info_obj['container_dom_id'] ? extra_info_obj['container_dom_id'] : "",
        sparkline_dom_id = extra_info_obj['sparkline_dom_id'] ? extra_info_obj['sparkline_dom_id'] : "",
        hidden_input_dom_id = extra_info_obj['hidden_input_dom_id'] ? extra_info_obj['hidden_input_dom_id'] : "",
        polled_val_shown_dom_id = extra_info_obj['polled_val_shown_dom_id'] ? extra_info_obj['polled_val_shown_dom_id'] : "",
        show_sparkline_chart = extra_info_obj['show_sparkline_chart'] ? extra_info_obj['show_sparkline_chart'] : false,
        is_first_call = typeof extra_info_obj['is_first_call'] != 'undefined' ? extra_info_obj['is_first_call'] : 1,
        is_rad5_device = '';

    // Condition to set/reset is_radwin flag
    if (typeof is_radwin5 != 'undefined') {
        is_rad5_device = is_radwin5;
    } else if (typeof extra_info_obj['is_radwin5'] != 'undefined') {
        is_rad5_device = extra_info_obj['is_radwin5'];
    } else {
        is_rad5_device = 0;
    }

    // Make Ajax Call
    perf_page_live_polling_call = $.ajax({
        url: base_url+"/device/lp_bulk_data/?service_name=" + service_name + "&devices=" + JSON.stringify(device_name) + "&ds_name="+ds_name+"&is_first_call="+is_first_call+"&is_radwin5="+is_rad5_device,
        type: "GET",
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
                    meta_info = result.data.meta ? result.data.meta : "",
                    data_type = meta_info && meta_info["data_source_type"] ? meta_info["data_source_type"] : "numeric",
                    chart_type = meta_info && meta_info["chart_type"] ? meta_info["chart_type"] : "column",
                    chart_color = meta_info && meta_info["chart_color"] ? meta_info["chart_color"] : "#70AFC4",
                    valuesuffix = meta_info && meta_info["valuesuffix"] ? meta_info["valuesuffix"] : "",
                    valuetext = meta_info && meta_info["valuetext"] ? meta_info["valuetext"] : "",
                    is_inverted = meta_info && meta_info["is_inverted"] ? meta_info["is_inverted"] : false,
                    warning_threshold = meta_info && meta_info["warning"] ? meta_info["warning"] : "",
                    critical_threshold = meta_info && meta_info["critical"] ? meta_info["critical"] : "",
                    dateObj = new Date(),
                    epoch_time = dateObj.getTime(),
                    current_date = dateObj.getDate() > 9 ? dateObj.getDate() : '0' + String(dateObj.getDate()),
                    month = Number(dateObj.getMonth()) + 1 > 9 ? Number(dateObj.getMonth()) + 1 : '0' + String(Number(dateObj.getMonth()) + 1),
                    date_str = current_date + "-" + month + "-" + dateObj.getFullYear(),
                    current_hour = dateObj.getHours() > 9 ? dateObj.getHours() : '0' + String(dateObj.getHours()),
                    current_minutes = dateObj.getMinutes() > 9 ? dateObj.getMinutes() : '0' + String(dateObj.getMinutes()),
                    current_second = dateObj.getSeconds() > 9 ? dateObj.getSeconds() : '0' + String(dateObj.getSeconds()),
                    time_str = current_hour + ":" + current_minutes + ":" + current_second,
                    current_time = date_str + " " + time_str,
                    fetched_data = true;

                if (fetched_val != "" && fetched_val != "NA" && fetched_val != null) {
                    
                    if (typeof fetched_val == 'object') {
                        fetched_val = fetched_val[0];
                    }

                    if (isNaN(Number(fetched_val))) {
                        fetched_val = fetched_val;
                    } else {
                        fetched_val = Number(fetched_val);
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
                            "valuetext" : valuetext ? valuetext : "",
                            "valuesuffix" : valuesuffix ? valuesuffix : "",
                            "warning_threshold" : warning_threshold,
                            "critical_threshold" : critical_threshold,
                            "is_inverted" : is_inverted
                        };
                    }
                } else {
                    if (!fetched_val || fetched_val == 'NA') {
                        fetched_val = null;
                    }

                    fetched_data = {
                        "val" : fetched_val,
                        "time" : current_time,
                        "epoch_time" : epoch_time ? epoch_time : "",
                        "type" : data_type ? data_type : "numeric",
                        "chart_type" : chart_type ? chart_type : "column",
                        "chart_color" : chart_color ? chart_color : "#70AFC4",
                        "valuetext" : valuetext ? valuetext : "",
                        "valuesuffix" : valuesuffix ? valuesuffix : "",
                        "warning_threshold" : warning_threshold,
                        "critical_threshold" : critical_threshold,
                        "is_inverted" : is_inverted
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
                $("#" + container_dom_id + " #perf_output_table tr td:nth-child(2) .single_perf_poll_now").button("complete");
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
        $("#"+container_id+" #perf_output_table tr td:nth-child(2) .single_perf_poll_now").button("loading");

        var active_tab_obj = nocout_getPerfTabDomId(),
            dom_id = active_tab_obj["active_dom_id"] ? active_tab_obj["active_dom_id"] : "",
            is_first_call = 1;

        if(poll_now_data_dict[dom_id] && poll_now_data_dict[dom_id].length > 0) {
            is_first_call = 0;            
        }

        var extra_info_obj = {
            'container_dom_id' : container_id,
            'sparkline_dom_id' : sparkline_dom_id,
            'hidden_input_dom_id' : hidden_input_dom_id,
            'polled_val_shown_dom_id' : polled_val_shown_dom_id,
            'show_sparkline_chart' : false,
            'is_first_call' : is_first_call
        };

        // Call function to fetch live polling data
        nocout_livePollCurrentDevice(
            service_name,
            ds_name,
            [device_name],
            extra_info_obj,
            function(response) {
                
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
 * @method checkpollvalues
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
            "is_inverted" : false,
            "chart_data": []
        },
        chart_data_list = {
            "warning" : {
                "color": 0,
                "name": "Warning Threshold",
                "type" : warn_type,
                "data" : []
            },
            "critical" : {
                "color": 0,
                "name": "Critical Threshold",
                "type" : crit_type,
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

        if (typeof(fetched_val) == 'undefined' || na_list.indexOf(fetched_val) > -1) {
            fetched_val = null;
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
            chart_config["is_inverted"] = result[i]["is_inverted"];
            chart_config["valuesuffix"] = result[i]["valuesuffix"] ? result[i]["valuesuffix"] : '';
            chart_config["valuetext"] = result[i]["valuetext"] ? result[i]["valuetext"] : '';
            
            if (fetch_warning_threshold) {
                if(!chart_data_list["warning"]["color"]) {
                    chart_data_list["warning"]["color"] = warn_color;
                }
                chart_data_list["warning"]["data"].push({
                    "color": warn_color,
                    "y": Number(fetch_warning_threshold),
                    "name": "Warning Threshold",
                    "x": result[i]['epoch_time']
                });
            }

            if (fetch_critical_threshold) {
                if(!chart_data_list["critical"]["color"]) {
                    chart_data_list["critical"]["color"] = crit_color;
                }
                chart_data_list["critical"]["data"].push({
                    "color": crit_color,
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
                "y": fetched_val,
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

            if ($("#" + dom_id + "_other_perf_table").length == 0) {
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
                'other_perf_table',
                dom_id
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

            nocout_destroyDataTable('other_perf_table');
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
        top_tab_content_id = $(".top_perf_tabs > li.active a").attr("href");

    var is_singular_view = false;

    if (typeof nocout_getPerfTabDomId != 'undefined' && typeof live_data_tab != 'undefined') {
        var is_birdeye_view = clicked_tab_id.indexOf('bird') > -1 || $('.top_perf_tabs > li.active a').attr('id').indexOf('bird') > -1,
            is_topo_view = clicked_tab_id.indexOf('topo') > -1 || $('.top_perf_tabs > li.active a').attr('id').indexOf('topo') > -1;
        is_singular_view = is_birdeye_view || is_topo_view;
    }

    if (is_singular_view) {
        return response_dict;
    }

    if(show_historical_on_performance || is_perf_polling_enabled) {
        var left_tab_content_id = $(top_tab_content_id + " .left_tabs_container li.active a").attr("href"),
            active_inner_tab = $(left_tab_content_id + " .inner_inner_tab li.active a");
        
        response_dict["active_dom_id"] = active_inner_tab.attr("id").slice(0, -4);
        response_dict["active_tab_api_url"] = active_inner_tab.attr("url");
    } else {
        var left_active_tab_anchor = $(top_tab_content_id + " .left_tabs_container li.active a"),
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

    if($("#" + tab_id + "_block .single_perf_poll_now").hasClass("disabled")) {
        $("#" + tab_id + "_block .single_perf_poll_now").removeClass("disabled");
    }

    try {
        if (perf_page_live_polling_call) {
            perf_page_live_polling_call.abort();
        }
    } catch(e) {
        // console.error(e);
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

        try {
            if (perf_page_live_polling_call) {
                perf_page_live_polling_call.abort();
            }
        } catch(e) {
            // console.error(e);
        }

    } else {
        bootbox.alert("Please run polling first.");
    }
}


/**
 * This function destroy datatable with given dom id
 * @method nocout_destroyDataTable
 */
function nocout_destroyDataTable(domId) {

    if (!domId) {
        return true;
    }

    if ($('#' + domId).length == 0 && $('table[id*="' + domId + '"]').length == 0) {
        return true;
    }

    if ($('table[id*="' + domId + '"]').length > 0) {
        var all_tables = $('table[id*="' + domId + '"]');
        for (var i=0;i<all_tables.length;i++) {
            try {
                $(all_tables[i]).dataTable().fnDestroy();
            } catch(e) {
                // console.error(e);
            }
            $(all_tables[i]).remove();
        }
    } else if($('#' + domId).length > 0) {
        try {
            $("#" + domId).dataTable().fnDestroy();
        } catch(e) {
            // console.error(e);
        }
        $("#" + domId).remove();
    }

    // Remove advance filter button
    if($('button[id*="_advance_filter_btn"]').length) {
        $('button[id*="_advance_filter_btn"]').addClass('hide');
    }

    if($('div.remove_advance_filters_btn').length) {
        $('div.remove_advance_filters_btn').hide();
    }

    // Remove advance filter form container
    if($('div.advance_filters_container').length) {
        $('div.advance_filters_container').hide();
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


/**
 * This function find & returns the tab id as per the given help text
 * @method getRequiredTabId
 * @param help_txt {String}, It contains the help text whose matched id is to be returned
 */
function getRequiredTabId(help_txt) {
    var top_tab_content_id = $(".top_perf_tabs > li.active a").attr("href"),
        left_tab_content_id = $(top_tab_content_id + " .left_tabs_container li.active a").attr("href"),
        inner_tabs = $(left_tab_content_id + ' ul.inner_inner_tab li'),
        required_tab_id = "";

    for (var i=0;i<inner_tabs.length;i++) {
        var tab_id = $(inner_tabs[i]).children('a')[0].id;
        if (help_txt == 'hourly') {
            if (tab_id.indexOf(help_txt) > -1 && tab_id.indexOf('bihourly') == -1) {
                required_tab_id = tab_id;
                break;
            }
        } else {
            if (tab_id.indexOf(help_txt) > -1) {
                required_tab_id = tab_id;
                break;
            }
        }
    }

    return required_tab_id;
}


/**
 * This function prepares min, max & avg legends on highcharts
 * @method prepareValueLegends
 * @param dataset {Array}, It contains the series data plotted on chart
 * @param dom_id {String}, It contains the dom id of parent container
 * @param is_zoom_in {Undefined/Object}, It contains undefined if on zero zoom level else object.
 */
function prepareValueLegends(dataset, dom_id, is_zoom_in) {
    var legends_block_id = dom_id + '_legends_block',
        legends_html = '<ul class="list-unstyled list-inline">';

    for(var i=0;i<dataset.length;i++) {
        var lowered_name = $.trim(dataset[i].name.toLowerCase());
        if (
            lowered_name.indexOf('critical') == -1
            &&
            lowered_name.indexOf('warning') == -1
            &&
            lowered_name.indexOf('threshold') == -1
            &&
            lowered_name.indexOf('min value') == -1
            &&
            lowered_name.indexOf('max value') == -1
            &&
            lowered_name.indexOf('avg value') == -1
        ) {
            var avg_val = calculateAverageValue(dataset[i].data, 'y'),
                max_val = typeof dataset[i].dataMax != 'undefined' ? dataset[i].dataMax : 'NA',
                min_val = typeof dataset[i].dataMin != 'undefined' ? dataset[i].dataMin : 'NA',
                box_color = dataset[i].color,
                name = dataset[i].name;

            avg_val = typeof avg_val != 'undefined' ? avg_val : 'NA';
            /****** If need to show (min + max) / 2 in avg legend then uncomment below code ******/
            // If chart is on some zoom level then calculate avg from min & max values
            // if (typeof is_zoom_in != 'undefined') {
            //     avg_val = (max_val + min_val) / 2;
            //     avg_val = avg_val.toFixed(2);
            // } else {
            //     avg_val = calculateAverageValue(dataset[i].data, 'y');
            // }
            
            legends_html += '<li>\
                             <span style="background:'+box_color+';">&nbsp;</span>\
                             '+ name +'(Min Val) : '+min_val+' \
                             </li> \
                             <li>\
                             <span style="background:'+box_color+';">&nbsp;</span>\
                             '+ name +'(Max Val) : '+max_val+' \
                             </li>';

            if (typeof is_zoom_in == 'undefined') {
                legends_html += '<li>\
                             <span style="background:'+box_color+';">&nbsp;</span>\
                             '+ name +'(Avg Val) : '+avg_val+' \
                             </li>';
            }
        }
    }

    legends_html += '</ul>';

    $('#' + legends_block_id + ' > .custom_legends_block').html(legends_html);

    if ($('#' + legends_block_id).hasClass('hide')) {
        $('#' + legends_block_id).removeClass('hide');
    }
}


/**
 * This function calculates & return the average value as per given params
 * @method calculateAverageValue
 * @param resultset {Array}, It contains the single series data plotted on chart
 * @param key {String}, It contains the object key whose data is to be average.
 */
function calculateAverageValue(resultset, key) {
    var total_val = 0;
    for (var x=0;x<resultset.length;x++) {
        total_val += resultset[x][key];
    }

    return (total_val/resultset.length).toFixed(2);
}


/**
 * This function calls different functions to generate birdeye view HTML & draw respective table/chart
 * @method initBirdEyeView
 * @param container_id {String}, It contains the dom id of parent element on which birdeye view is to be created
 */
function initBirdEyeView(container_id) {

    if (typeof all_services_list != 'undefined' && all_services_list.length) {
        // if birdeye view HTML is not created then first create it.
        if($.trim($('#birdeye_container').html()).length == 0) {
            createBirdEyeViewHTML(container_id);
        }

        populateBirdViewCharts(birdeye_start_counter, birdeye_end_counter);
    } else {
        return true;
    }

    hideSpinner();
}


/**
 * This function call getServiceData for different services in loop to populate chart/table in birdeye view
 * @method populateBirdViewCharts
 * @param start {Number}, It contains the start index of for loop for all_services_list array
 * @param end {Number}, It contains the end index of for loop for all_services_list array
 */
function populateBirdViewCharts(start, end) {
    for (var i=start;i<end;i++) {
        if (all_services_list[i]) {
            var api_url = perf_base_url,
                srv_name = all_services_list[i].id;
            
            // Update url with actual service name
            api_url = api_url.replace('srv_name', srv_name);

            if (api_url.indexOf('?') > -1) {
                api_url = api_url + '&service_view_type=unified'
            } else {
                api_url = api_url + '?service_view_type=unified'
            }

            api_url += '&only_service=1';

            // Get Service Status (Closure function used)
            (function(index) {
                var srv = all_services_list[index].id;
                perfInstance.getServiceStatus(api_url, false, function(response_type, data_obj) {
                    var severity_status = data_obj['status'] ? data_obj['status'] : 'unknown',
                        status_since = data_obj['last_updated'] ? data_obj['last_updated'] : 'NA',
                        severity_style_obj = nocout_getSeverityColorIcon(severity_status),
                        txt_color = severity_style_obj.color ? severity_style_obj.color : "",
                        fa_icon_class = severity_style_obj.icon ? severity_style_obj.icon : "fa-circle",
                        status_html = '<td title="Status"><i class="fa '+fa_icon_class+'"></i></td>\
                                       <td title="Status Since"><strong>Since:</strong> '+status_since+'</td>';
                    // Change the color of row as per severity
                    $('#' + srv + '_status_table tbody tr:first-child').css('color', txt_color);
                    $('#' + srv + '_status_table tbody tr:first-child').html(status_html);
                });
            }(i));

            // call function to fetch perf data for this service
            perfInstance.getServiceData(api_url, srv_name, current_device);
            if (!$('#' + srv_name + '_heading .fa-spinner').hasClass('hide')) {
                $('#' + srv_name + '_heading .fa-spinner').addClass('hide');
            }
        }
    }

    if (end < all_services_list.length - 1) {
        populateBirdViewCharts(end, end * 2)
    }
}


/**
 * This function creates birdeye view content HTML skull.
 * @method createBirdEyeViewHTML
 * @param container_id {String}, It contains the dom id of parent element on which birdeye view is to be created
 */
function createBirdEyeViewHTML(container_id) {

    var birdeye_html = '';

    for(var i=0;i<all_services_list.length;i++) {
        var not_ping = true;
        if (all_services_list[i]['id'] == 'ping') {
            birdeye_html += '<div class="col-md-12 row">';
            not_ping = false;
        } else {
            not_ping = true;
            var float_class = '';
            if (i % 2 == 0) {
                float_class = 'pull-right';
            }

            birdeye_html += '<div class="col-md-6 ' + float_class + ' row">';
        }

        if (not_ping) {
            birdeye_html += '<div class="birdeye_title_block">';
            birdeye_html += '<h4 class="zero_top_margin pull-left" id="' + all_services_list[i]['id'] + '_heading"> \
                             ' + all_services_list[i]['title'] + ' <i class="fa fa-spinner fa-spin"></i></h4>';
            birdeye_html += '<table class="table-bordered pull-right" id="' + all_services_list[i]['id'] + '_status_table">';
            birdeye_html += '<tbody><tr></tr></tbody>';
            birdeye_html += '</table><div class="clearfix"></div></div>';
        } else {
            birdeye_html += '<h4 class="zero_top_margin" id="' + all_services_list[i]['id'] + '_heading"> \
                             ' + all_services_list[i]['title'] + ' <i class="fa fa-spinner fa-spin"></i></h4>';
        }
                         
        birdeye_html += '<div class="birdeye_view_charts">';
        birdeye_html += '<div id="' + all_services_list[i]['id'] + '_chart" class="charts_block"></div>';
        birdeye_html += '<div id="' + all_services_list[i]['id'] + '_bottom_table"></div>';
        birdeye_html += '<div class="clearfix"></div>';
        birdeye_html += '</div>';
        birdeye_html += '</div>';

        if (i % 2 == 0 || i == all_services_list.length - 1) {
            birdeye_html += '<div class="clearfix"></div><hr/>';
        }
    }

    $('#' + container_id).html(birdeye_html);
}


/**
 * This function formats given date object in DD/MM/YY HH:MM(24 Hrs)
 * @method getFormattedDate
 * @param input_date {Object}, It contains date object
 * @return formatted_date {String}, It contains the formatted date string
 */
function getFormattedDate(input_date) {
    var formatted_date = '';

    try {
        var fetched_datetime = new Date(input_date),
            fetched_day = fetched_datetime.getDate() > 9 ? fetched_datetime.getDate() : '0' + String(fetched_datetime.getDate()),
            fetched_month = fetched_datetime.getMonth() + 1 > 9 ? fetched_datetime.getMonth() + 1 : '0' + String(fetched_datetime.getMonth() + 1),
            fetched_year = String(fetched_datetime.getYear()).substr(-2),
            fetched_hours = fetched_datetime.getHours() > 9 ? fetched_datetime.getHours() : '0' + String(fetched_datetime.getHours()),
            fetched_minutes = fetched_datetime.getMinutes() > 9 ? fetched_datetime.getMinutes() : '0' + String(fetched_datetime.getMinutes());

        formatted_date = fetched_day + '/' + fetched_month + '/' + fetched_year + ' ' + fetched_hours + ':' + fetched_minutes;
    } catch(e) {
        // console.error(e);
    }

    return formatted_date;
}


/**
 * This event trigger when severity status block clicked
 * @event click(with delegate)
 */
$('#status_container').delegate('#final_status_table .severity_block', 'click', function(e) {

    // Show loading spinner
    showSpinner();

    var severity_list = ['ok', 'warning', 'critical', 'unknown'],
        block_severity = $(this).data('severity') ? $.trim($(this).data('severity').toLowerCase()) : '',
        count_txt = $(this).text() ? Number($.trim($(this).text())) : 0;

    if (severity_list.indexOf(block_severity) > -1) {
        if (count_txt > 0 && typeof severity_wise_data_api != 'undefined') {
            var view_type = $.trim($('input[name="service_view_type"]:checked').val()),
                get_params = '?severity=' + block_severity + '&device_id=' + current_device + '&view_type=' + view_type;
            // Make ajax call
            $.ajax({
                url: severity_wise_data_api + get_params,
                type: 'GET',
                success: function(response) {
                    var result = response;

                    if (typeof result == 'string') {
                        result = JSON.parse(result);
                    }

                    if (result['success']) {

                        var dataset = result.data,
                            table_html = '';
                        
                        table_html += '<table class="table table-bordered table-hover table-striped table-responsive">';
                        table_html += '<thead>';
                        table_html += '<tr> \
                                            <th>Time</th> \
                                            <th>Datasource</th> \
                                            <th>Service</th> \
                                            <th>Value</th> \
                                            <th>Severity</th> \
                                            <th>Warning Threshold</th> \
                                            <th>Critical Threshold</th> \
                                       </tr>';
                        table_html += '</thead><tbody>';

                        for (var i=0;i<dataset.length;i++) {
                            table_html += '<tr> \
                                                <td>' + dataset[i]['sys_timestamp'] + '</td> \
                                                <td>' + dataset[i]['data_source'] + '</td> \
                                                <td>' + dataset[i]['service_name'] + '</td> \
                                                <td>' + dataset[i]['current_value'] + '</td> \
                                                <td>' + dataset[i]['severity'] + '</td> \
                                                <td>' + dataset[i]['warning_threshold'] + '</td> \
                                                <td>' + dataset[i]['critical_threshold'] + '</td> \
                                           </tr>';
                        }

                        table_html += '</tbody></table>';

                        bootbox.dialog({
                            message: '<div id="severity_wise_data_container" style="max-height: 450px; overflow: auto;"></div>',
                            title: '<i class="fa fa-dot-circle-o">&nbsp;</i> SEVERITY WISE DATA - ' + block_severity.toUpperCase()
                        });

                        $(".modal-dialog").css("width","80%");

                        $('#severity_wise_data_container').html(table_html);

                    } else {
                        $.gritter.add({
                            // (string | mandatory) the heading of the notification
                            title: block_severity + ' severity wise status',
                            // (string | mandatory) the text inside the notification
                            text: result.message,
                            // (bool | optional) if you want it to fade out on its own or just sit there
                            sticky: false
                        });
                    }
                },
                error: function(err) {
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: block_severity + ' severity wise status',
                        // (string | mandatory) the text inside the notification
                        text: err.statusText,
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: false
                    });
                },
                complete: function() {
                    // Hide loading spinner
                    hideSpinner();
                }
            });
        } else {
            bootbox.alert("This device don't have any service in '" + block_severity + "'");
            // Hide loading spinner
            hideSpinner();
        }
    }
});

/**
 * This function binds the click event on 'STATUS, RESET, JOJI' buttons on power tab
 * on single performance page
 * @event click
 */
$("#content").delegate(".power-actions", 'click', function(){

    var button_this = this,
        button_name = $(button_this).attr('data-button-respone'),
        button_title = $(button_this).attr('title'),
        msg_box_html = '';

    
    msg_box_html = '<textarea id="power_msg_txt" placeholder="Please enter the reason for your action." \
                    class="form-control" rows="5"></textarea> \
                    <span id="power_error_msg" class="text-danger"></span>';

    // Show popup to take reason message from user & save it to user logs
    bootbox.confirm(msg_box_html, function(action) {


        if(action) {

            var reason_str = $.trim($('#power_msg_txt').val());

            if (!reason_str) {
                $('#power_error_msg').html('*Reason required.');
                return false;
            }

            // Show loading on button
            $(button_this).button('loading');

            // If send message button clicked
            if (button_name != 'reboot') {
                initSendSMS(current_device, button_name, button_this, function(succeeded) {
                    // Complete button loading
                    $(button_this).button('complete');

                    // if (succeeded) {
                        savePowerLog(current_device, reason_str, button_title);
                    // }
                });
            } else {
                if (typeof current_device == 'undefined') {
                    current_device = '';
                }

                var device_id = $(button_this).attr('device_id');

                if (device_id) {
                    current_device = device_id;
                }
                // Add the reboot code here(Shellinabox)
                initDeviceReboot(current_device, button_this, function(response) {
                    // Complete button loading
                    $(button_this).button('complete');

                    // if (succeeded) {
                        savePowerLog(current_device, reason_str, button_title);
                    // }
                });
            }
        }
    });
});

/**
 * This function makes ajax call to save power logs
 * @method savePowerLog
 * @param reason_str {}
 */
function savePowerLog(device_id, reason_str, action) {
    // Make ajax call
    $.ajax({
        url: base_url+save_power_log_url,
        type: 'POST',
        data: {
            'device_id': device_id,
            'reason_str': reason_str,
            'action': action
        },
        success: function(response) {
            
            // console.log(response);
        },
        error: function(err) {

        }
    });
}

/**
 * This function makes ajax call to send sms as per the user actions.
 * @method initSendSMS
 * @param button_name {String}, It contains name of clicked button.
 * @param clicked_button_instance {Object}, It contains the clicked button instance.
 */
function initSendSMS(device_id, button_name, clicked_button_instance, callback) {
    // Make ajax call to send message
    $.ajax({
        url : base_url + power_sms_url + "?device_id=" + device_id + "&button_name=" + button_name,
        type : 'GET',
        success : function(response) {
            if (typeof response == 'string') {
                response = JSON.parse(response);
            }
            var is_success = response['success'];
            if (response['success']) {
                dataTableInstance.createDataTable(
                    power_table_id,
                    power_listing_headers,
                    power_ajax_url,
                    false
                );
            }

            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: $.trim($(clicked_button_instance).attr('title')),
                // (string | mandatory) the text inside the notification
                text: response['message'],
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // Time in ms after which the gritter will dissappear.
                time : 2000
            });
            callback(is_success);
        },
        error : function(e) {
            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: $.trim($(clicked_button_instance).attr('title')),
                // (string | mandatory) the text inside the notification
                text: e.message,
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // Time in ms after which the gritter will dissappear.
                time : 2000
            });
            callback(false);
        },
        complete: function() {
            // Complete button loading
            $(clicked_button_instance).button('complete');
        }
    });
}

/**
 * This function makes ajax call to reboot current device
 * @method initDeviceReboot
 * @param clicked_button_instance {Object}, It contains the clicked button instance.
 */
function initDeviceReboot(device_id, clicked_button_instance, callback) {
    // Make ajax call to send message
    $.ajax({
        url : base_url + device_reboot_url + "?device_id=" + device_id,
        type : 'GET',
        success : function(response) {
            
            if (typeof response == 'string') {
                response = JSON.parse(response);
            }

            var is_success = response['success'];
            // if (response['success']) {
            //     dataTableInstance.createDataTable(
            //         power_table_id,
            //         power_listing_headers,
            //         power_ajax_url,
            //         false
            //     );
            // }

            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: $.trim($(clicked_button_instance).attr('title')),
                // (string | mandatory) the text inside the notification
                text: response['message'],
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // Time in ms after which the gritter will dissappear.
                time : 2000
            });
            callback(is_success);
        },
        error : function(e) {
            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: $.trim($(clicked_button_instance).attr('title')),
                // (string | mandatory) the text inside the notification
                text: e.message,
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // Time in ms after which the gritter will dissappear.
                time : 2000
            });
            callback(false);
        },
        complete: function() {
            // Complete button loading
            $(clicked_button_instance).button('complete');
        }
    });
}