/**
 * This file contain the global reusable function for nocout platform
 * @for nocoutUtilsLib
 */


// Global Variables
var green_color = "#468847",
    orange_color = "#f0ad4e",
    red_color = "#b94a48",
    green_status_array = ['ok','success','up'],
    red_status_array = ['critical'],
    down_status_array = ['down'],
    orange_status_array = ['warning'],
    left_block_style = "border:1px solid #CCC;border-right:0px;padding: 3px 5px;background:#FFF;",
    right_block_style = "border:1px solid #CCC;padding: 3px 5px;background:#FFF;",
    val_icon = '<i class="fa fa-arrow-circle-o-right"></i>',
    time_icon = '<i class="fa fa-clock-o"></i>',
    perf_page_live_polling_call = "";


/**
 * This function is used to populate the latest status info for any device as per given params
 * @method populateDeviceStatus_nocout
 * @param domElement {String}, It contains the dom element ID on which the info is to be populated
 * @param info {Object}, It contains the latest status info object
 */
function populateDeviceStatus_nocout(domElement,info) {

    var fa_icon_class = "fa-circle",
        txt_color = "",
        status_html = "",
        age = info.age ? info.age : "Unknown",
        lastDownTime = info.last_down_time ? info.last_down_time : "Unknown",
        status = info.status ? info.status.toUpperCase() : "Unknown";

    if(green_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        txt_color = green_color;
        fa_icon_class = "fa-check-circle";
    } else if(red_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        txt_color = red_color;
        fa_icon_class = "fa-times-circle";
    } else if(orange_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        txt_color = orange_color;
        fa_icon_class = "fa-warning";
    } else if(down_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        txt_color = red_color;
        fa_icon_class = "fa-warning";
    } else {
        // pass
    }

    status_html = "";

    status_html += '<table id="final_status_table" class="table table-responsive table-bordered" style="background:#FFFFFF;"><tr>';
    status_html += '<td style="color:'+txt_color+';"><i title = "'+status+'" class="fa '+fa_icon_class+'" style="vertical-align: middle;"> </i> <b>Current Status</b> : '+status+'</td>';
    status_html += '<td style="color:'+txt_color+';"><b>Current Status Since</b> : '+age+'</td>';
    status_html += '<td style="color:'+txt_color+';"><b>Last Down Time</b> : '+lastDownTime+'</td>';
    status_html += '</tr></table>';

    // Update Status Block HTML as per the device status
    $("#"+domElement).html(status_html);
}

/**
 * This function is used to populate the latest status for any service as per given params
 * @method populateServiceStatus_nocout
 * @param domElement {String}, It contains the dom element ID on which the info is to be populated
 * @param info {Object}, It contains the latest status object
 */
function populateServiceStatus_nocout(domElement,info) {

    if(!is_perf_polling_enabled) {
        /********** Service Status Without Live Polling  - START     ********************/
        if($.trim(info.last_updated) != "" || $.trim(info.perf) != "") {
            
            var last_updated = info.last_updated ? info.last_updated : "N/A",
                perf = info.perf ? info.perf : "N/A",
                inner_status_html = '';

            inner_status_html += '<table id="perf_output_table" class="table table-responsive table-bordered" style="background:#F5F5F5;">';
            inner_status_html += '<tr>';
            inner_status_html += '<td><b>Latest Performance Output</b> : '+perf+'</td>';
            inner_status_html += '<td><b>Last Updated At</b> : '+last_updated+'</td>';
            inner_status_html += '</tr>';
            inner_status_html += '</table><div class="clearfix"></div><div class="divide-20"></div>';

            $("#"+domElement).html(inner_status_html);
        } else {
            $("#"+domElement).html("");
        }

        /********** Service Status Without Live Polling  - END     ********************/
    } else {
        /********** LIVE POLLING CODE  - START     ********************/

        // Clear status block when we are on utilization or availablility tabs
        if(domElement.indexOf('availability') > -1 || domElement.indexOf('utilization_top') > -1 || domElement.indexOf('topology') > -1) {

            $("#"+domElement).html("");

        } else {

            var last_updated = info.last_updated ? info.last_updated : "N/A",
                perf = info.perf ? info.perf : "N/A",
                inner_status_html = '';

            // Create Table for service polled value & live polling --- START
            inner_status_html += '<table id="perf_output_table" class="table table-responsive table-bordered" style="background:#F5F5F5;">';
            inner_status_html += '<tr>';
            
            inner_status_html += '<td style="width:47.5%;"><b>Service Output :</b> <br/>\
                                '+val_icon+' '+perf+'<br/>\
                                '+time_icon+' '+last_updated+'</td>';
            
            inner_status_html += '<td style="width:5%;vertical-align: middle;">\
                                 <button class="btn btn-primary btn-xs perf_poll_now"\
                                 title="Poll Now" data-complete-text="<i class=\'fa fa-hand-o-right\'></i>" \
                                 data-loading-text="<i class=\'fa fa-spinner fa fa-spin\'> </i>"><i \
                                 class="fa fa-hand-o-right"></i></button>\
                                 </td>';

            inner_status_html += '<td style="width:47.5%;">\
                                 <b>Poll Output :</b> \
                                 <span id="perf_live_poll_chart"></span><br/>\
                                 <ul id="perf_live_poll_vals" class="list-unstyled"></ul>\
                                 </td>';
            

            inner_status_html += '</tr>';
            inner_status_html += '</table>';
            // Create Table for service polled value & live polling --- END

            // Create hidden input field to store polling values --- START
            inner_status_html += '<input type="hidden" name="perf_live_poll_input" id="perf_live_poll_input" value="">';
            // Create hidden input field to store polling values --- END

            inner_status_html += '<div class="clearfix"></div><div class="divide-20"></div>';

            $("#"+domElement).html(inner_status_html);
        }
        /********** LIVE POLLING CODE  - END     ********************/
    }
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

    if($('#'+table_id).length > 0) {
        $("#"+table_id).dataTable().fnDestroy();
        $("#"+table_id).remove();
    }

    table_string += '<table id="' + table_id + '" class="datatable table table-striped table-bordered table-hover table-responsive"><thead>';
    /*Table header creation start*/
    for (var i = 0; i < grid_headers.length; i++) {
        table_string += '<td><b>' + grid_headers[i].toUpperCase() + '</b></td>';
        excel_columns.push(i);
    }
    table_string += '</thead></table>';
    /*Table header creation end*/


    if(service_id) {
        $('#'+service_id+'_chart').html(table_string);
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
        bPaginate: true,
        bDestroy: true,
        aaSorting : [[0,'desc']],
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
function initChartDataTable_nocout(table_id, headers, service_id) {

    var excel_columns = [];

    if($('#'+table_id).length > 0) {
        $("#"+table_id).dataTable().fnDestroy();
        $("#"+table_id).remove();
    }

    var data_in_table = "<table id='"+table_id+"' class='datatable table table-striped table-bordered table-hover table-responsive'><thead><tr>";
    /*Make table headers*/
    for (var i = 0; i < headers.length; i++) {
        data_in_table += '<td colspan="2" align="center"><b>' + headers[i].name + '</b></td>';
        excel_columns.push(i);
        if(headers.length <= i+1) {
            excel_columns.push(i+1);
        }

    }
    data_in_table += '</tr><tr>';

    for (var i = 0; i < headers.length; i++) {
        data_in_table += '<td><em>Time</em></td><td><em>Value</em></td>';
    }

    data_in_table += '</tr></thead></table>';
    /*Table header creation end*/
    if(service_id) {
        $('#'+service_id+'_bottom_table').html(data_in_table);
    }

    $("#"+table_id).DataTable({
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
        bPaginate: true,
        bDestroy: true,
        aaSorting : [[0,'desc']],
        sPaginationType: "full_numbers"
    });
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
            var inner_data = table_obj[j].data[i];

            if(inner_data) {
                if(inner_data.constructor == Array) {
                    if(inner_data[0]) {
                        row_val.push(new Date(inner_data[0]).toLocaleString());
                        var chart_val = inner_data[1];
                        row_val.push(chart_val);
                    }
                } else if(inner_data.constructor == Object) {
                    if(inner_data.x) {
                        row_val.push(new Date(inner_data.x).toLocaleString());
                        var chart_val = inner_data.y;
                        row_val.push(chart_val);
                    }
                }
            }
        }
        // If row are less than total columns then add blank fields
        if(row_val.length < total_columns) {
            var val_diff = total_columns - row_val.length;
            for(var x=0;x<val_diff;x++) {
                row_val.push(" ");
            }
            $('#'+table_id).dataTable().fnAddData(row_val);
        } else {
            $('#'+table_id).dataTable().fnAddData(row_val);
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
        legends_color = text_color ? text_color : "#FFF";

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
        tooltip: {
            headerFormat: '{point.x:%e/%m/%Y (%b)  %l:%M %p}<br>',
            pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b><br/>',
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
            minRange: 3600000,
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
        series: chartConfig.chart_data
    };

    try {
        if(need_extra_config) {
            chart_options["yAxis"]["max"] = 100;
            chart_options["plotOptions"] = {series: {stacking: 'normal'}};
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

    if($("#"+table_id).length > 0) {
        $("#"+table_id).dataTable().fnDestroy();
        $("#"+table_id).remove();
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

    if($("#"+table_id).length > 0) {
        $("#"+table_id).dataTable().fnDestroy();
        $("#"+table_id).remove();
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
            if (inner_data instanceof Array) {
                time_val = new Date(inner_data[0]).toLocaleString();
                val = inner_data[1];
            } else {
                time_val = new Date(inner_data.x).toLocaleString();
                val = inner_data.y;
            }
            data_in_table += '<td>'+time_val+'</td><td>'+val+'</td>';
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
    callback
) {
    // Make Ajax Call
    perf_page_live_polling_call = $.ajax({
        url : base_url+"/"+"device/lp_bulk_data/?service_name="+service_name+"&devices="+JSON.stringify(device_name)+"&ds_name="+ds_name,
        type : "GET",
        success : function(response) {
            
            var result = "";
            // Type check of response
            if(typeof response == 'string') {
                result = JSON.parse(response);
            } else {
                result = response;
            }

            if(result.success == 1) {

                var fetched_val = result.data.devices[device_name] ? result.data.devices[device_name]['value'] : "";
                var shown_val = "",
                    current_val_html = "",
                    dateObj = new Date(),
                    current_time = dateObj.getHours()+":"+dateObj.getMinutes()+":"+dateObj.getSeconds(),
                    fetched_data = true;
                if(fetched_val != "" && fetched_val != "NA" && fetched_val != null) {
                    
                    if(typeof fetched_val == 'object') {
                        fetched_val = fetched_val[0];
                    }

                    // If call is from single device page then proceed else return data
                    if(container_dom_id) {
                        // Create Fetched val html with time stamp
                        current_val_html += '<li style="display:none;">'+val_icon+' '+fetched_val;
                        current_val_html += '<br/>'+time_icon+' '+current_time+'</li>';
                        
                        // Prepend new fetched val & time li
                        $("#"+container_dom_id+" #perf_output_table tr td:last-child ul#perf_live_poll_vals").html(current_val_html);
                        // Animation effect to added li
                        $("#"+container_dom_id+" #perf_output_table tr td:last-child ul#perf_live_poll_vals li").slideDown('slow');


                        /******************** Create Sparkline Chart for numeric values ********************/
                        if(!isNaN(Number(fetched_val))) {
                            var existing_val = $("#"+container_dom_id+" #"+hidden_input_dom_id).val(),
                                new_values_list = "";

                            if(existing_val) {
                                new_values_list = existing_val+","+fetched_val;
                            } else {
                                new_values_list = fetched_val;
                            }
                            
                            // Update the value in input field
                            $("#"+container_dom_id+" #"+hidden_input_dom_id).val(new_values_list);

                            // Make array of values from "," comma seperated string
                            var new_chart_data = new_values_list.split(",");

                            /*Plot sparkline chart with the fetched polling value*/
                            $("#"+container_dom_id+" #"+sparkline_dom_id).sparkline(new_chart_data, {
                                type: "line",
                                lineColor: "blue",
                                spotColor : "orange",
                                defaultPixelsPerValue : 10
                            });
                        }
                    } else {
                        fetched_data = {
                            "val" : fetched_val,
                            "time" : current_time
                        };
                    }


                } else {
                    fetched_data = {
                        "val" : fetched_val,
                        "time" : current_time
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
            if($.trim(err.statusText) != 'abort') {    
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
            if(container_dom_id) {
                // Enable the "Poll Now" button
                $("#"+container_dom_id+" #perf_output_table tr td:nth-child(2) .perf_poll_now").button("complete");
            }
        }
    });
}